"""Optional visible Chrome views with isolated profiles and bounded stdlib CDP."""
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import threading
import time
import urllib.parse
import urllib.request
import uuid

MAX_MESSAGE = 8 * 1024 * 1024
MAX_EVENTS = 100


class LiveViewError(RuntimeError):
    pass


def _validate_url(url):
    if not isinstance(url, str) or any(ord(char) < 33 for char in url) or '\\' in url:
        raise ValueError('Live view requires an explicit local HTTP URL.')
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost', '::1')
            or parsed.port is None or not 1 <= parsed.port <= 65535 or parsed.port == 3000
            or parsed.username or parsed.password or parsed.fragment):
        raise ValueError('Live view URL must use loopback HTTP with an explicit port other than 3000, without credentials or fragment.')
    return parsed


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise LiveViewError('Live view endpoint redirected; navigation was refused.')


def _http(url, limit=1_000_000, timeout=2):
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())
        deadline = time.monotonic() + timeout
        with opener.open(urllib.request.Request(url, headers={'Accept': 'application/json'}), timeout=timeout) as response:
            chunks, total = [], 0
            while True:
                if time.monotonic() >= deadline:
                    raise LiveViewError('Local endpoint read deadline exceeded.')
                chunk = response.read1(min(65536, limit + 1 - total))
                if not chunk: return b''.join(chunks)
                total += len(chunk)
                if total > limit: raise LiveViewError('Local endpoint response exceeded its size limit.')
                chunks.append(chunk)
    except LiveViewError:
        raise
    except Exception:
        raise LiveViewError('Local endpoint is unavailable; transport details withheld.') from None


class _WebSocket:
    def __init__(self, url, port, timeout=8):
        parsed = urllib.parse.urlsplit(url)
        if (parsed.scheme != 'ws' or parsed.hostname not in ('127.0.0.1', 'localhost', '::1') or parsed.port != port
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or not parsed.path.startswith('/devtools/') or any(ord(c) < 33 for c in url)):
            raise LiveViewError('Unexpected browser debugger endpoint.')
        self.deadline, self.serial, self.events, self.buffer = time.monotonic() + timeout, 0, [], bytearray()
        self.sock = None
        try:
            self.sock = socket.create_connection(('127.0.0.1', port), timeout=min(timeout, 3))
            key = base64.b64encode(os.urandom(16)).decode()
            request = ('GET ' + parsed.path + ' HTTP/1.1\r\nHost: 127.0.0.1:' + str(port)
                       + '\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: ' + key
                       + '\r\nSec-WebSocket-Version: 13\r\n\r\n')
            self.sock.sendall(request.encode('ascii'))
            while b'\r\n\r\n' not in self.buffer:
                self._timeout()
                chunk = self.sock.recv(1024)
                if not chunk or len(self.buffer) + len(chunk) > 16_384:
                    raise LiveViewError('Browser WebSocket handshake failed or exceeded its bound.')
                self.buffer.extend(chunk)
            head, rest = bytes(self.buffer).split(b'\r\n\r\n', 1)
            self.buffer = bytearray(rest)
            lines = head.decode('ascii').split('\r\n')
            headers = {line.split(':', 1)[0].lower(): line.split(':', 1)[1].strip() for line in lines[1:] if ':' in line}
            expected = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            if (len(lines[0].split()) < 2 or lines[0].split()[1] != '101'
                    or headers.get('sec-websocket-accept') != expected or headers.get('upgrade', '').lower() != 'websocket'
                    or 'upgrade' not in [token.strip() for token in headers.get('connection', '').lower().split(',')]):
                raise LiveViewError('Browser WebSocket handshake was rejected.')
        except Exception:
            self.close()
            raise LiveViewError('Browser WebSocket connection failed.') from None

    def _timeout(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise LiveViewError('Browser capture deadline exceeded.')
        self.sock.settimeout(remaining)

    def _read(self, size):
        while len(self.buffer) < size:
            self._timeout()
            data = self.sock.recv(min(65536, size - len(self.buffer)))
            if not data:
                raise LiveViewError('Browser debugger disconnected.')
            self.buffer.extend(data)
        result = bytes(self.buffer[:size])
        del self.buffer[:size]
        return result

    def _send(self, payload, opcode=1):
        if len(payload) > MAX_MESSAGE:
            raise LiveViewError('Browser command exceeded its size bound.')
        mask = os.urandom(4)
        length = len(payload)
        header = bytes([0x80 | opcode])
        header += bytes([0x80 | length]) if length < 126 else bytes([0x80 | 126]) + struct.pack('!H', length) if length < 65536 else bytes([0x80 | 127]) + struct.pack('!Q', length)
        self._timeout()
        self.sock.sendall(header + mask + bytes(value ^ mask[index % 4] for index, value in enumerate(payload)))

    def _receive(self):
        fragments, started, size = [], False, 0
        while True:
            first, second = self._read(2)
            final, opcode = bool(first & 128), first & 15
            if first & 0x70 or second & 128:
                raise LiveViewError('Unsupported browser WebSocket frame.')
            length = second & 127
            if length == 126: length = struct.unpack('!H', self._read(2))[0]
            elif length == 127: length = struct.unpack('!Q', self._read(8))[0]
            if length > MAX_MESSAGE or (opcode >= 8 and (not final or length > 125)):
                raise LiveViewError('Browser WebSocket frame exceeded its bounds.')
            payload = self._read(length)
            if opcode == 8: raise LiveViewError('Browser debugger closed the connection.')
            if opcode == 9:
                self._send(payload, 10)
                continue
            if opcode == 10: continue
            if (opcode == 1 and started) or (opcode == 0 and not started) or opcode not in (0, 1):
                raise LiveViewError('Invalid browser WebSocket message sequence.')
            started = True
            size += len(payload)
            if size > MAX_MESSAGE: raise LiveViewError('Browser message exceeded its bound.')
            fragments.append(payload)
            if final:
                return b''.join(fragments).decode('utf-8')

    def _record(self, event):
        method = event.get('method')
        params = event.get('params') or {}
        if method == 'Runtime.exceptionThrown':
            detail = params.get('exceptionDetails') or {}
            text = (detail.get('exception') or {}).get('description') or detail.get('text') or 'JavaScript exception'
            entry = {'type': 'exception', 'level': 'error', 'text': str(text)[:2000]}
        elif method == 'Log.entryAdded':
            detail = params.get('entry') or {}
            entry = {'type': 'log', 'level': str(detail.get('level', 'info'))[:30], 'text': str(detail.get('text', ''))[:2000]}
        else:
            return
        self.events.append(entry)
        self.events[:] = self.events[-MAX_EVENTS:]

    def call(self, method, params=None):
        self.serial += 1
        try:
            self._send(json.dumps({'id': self.serial, 'method': method, 'params': params or {}}).encode())
            while True:
                message = json.loads(self._receive())
                if not isinstance(message, dict): raise LiveViewError('Invalid debugger response.')
                if message.get('id') == self.serial:
                    if 'error' in message: raise LiveViewError('Browser rejected the capture operation.')
                    return message.get('result') or {}
                self._record(message)
        except LiveViewError:
            raise
        except Exception as exc:
            raise LiveViewError('Browser protocol failed during ' + method + ' (' + type(exc).__name__ + '); raw response withheld.') from None

    def close(self):
        if self.sock is not None:
            self.sock.close()


class LiveViews:
    def __init__(self, config):
        self.config = config
        self.root = Path(config.get('data_dir', 'runtime')).resolve() / 'live'
        self.allowed = config.get('live_views', {})
        if not isinstance(self.allowed, dict): raise ValueError('live_views must be a project mapping.')
        for target in self.allowed.values(): _validate_url(target['url'])
        self._views = {}
        self._lock = threading.RLock()

    def _chrome(self):
        explicit = self.config.get('chrome_path')
        if explicit:
            if Path(explicit).is_file(): return str(Path(explicit).resolve())
            raise LiveViewError('Configured Chrome executable was not found.')
        candidates = [Path(os.environ.get(name, '')) / 'Google/Chrome/Application/chrome.exe'
                      for name in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA') if os.environ.get(name)]
        for candidate in candidates:
            if candidate.is_file(): return str(candidate)
        for name in ('google-chrome', 'chromium', 'chromium-browser'):
            found = shutil.which(name)
            if found: return found
        raise LiveViewError('Chrome is not installed or discoverable. Set chrome_path to its executable.')

    def _preflight(self, url, expected_openapi_title=None):
        _http(url, limit=2_000_000)
        if expected_openapi_title is not None:
            parsed = _validate_url(url)
            identity_url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, '/openapi.json', '', ''))
            try:
                document = json.loads(_http(identity_url, limit=200_000))
                title = document['info']['title']
            except (ValueError, TypeError, KeyError):
                raise LiveViewError('Local service identity could not be verified.') from None
            if title != expected_openapi_title:
                raise LiveViewError('Local service identity does not match the configured module.')

    def _public(self, view):
        result = {key: view[key] for key in ('id', 'project_id', 'url', 'pid', 'debug_port', 'status')}
        if view['process'].poll() is not None:
            result['status'] = view['status'] = 'stopped'
            view['proxy'].close()
        return result

    def start(self, project_id, url):
        with self._lock:
            if project_id not in self.allowed or self.allowed[project_id].get('url') != url:
                raise ValueError('Live view URL is not configured for this project.')
            parsed = _validate_url(url)
            if sum(v['process'].poll() is None for v in self._views.values()) >= 3:
                raise LiveViewError('At most three owned Chrome views may run at once.')
            expected_title = self.allowed[project_id].get('expected_openapi_title')
            if expected_title is None:
                self._preflight(url)
            else:
                self._preflight(url, expected_title)
            chrome = self._chrome()
            view_id = uuid.uuid4().hex
            profile = self.root / view_id
            profile.mkdir(parents=True)
            proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy.bind(('127.0.0.1', 0))  # Reserved but not listening: fail closed for proxied requests.
            bypass = '<-loopback>;127.0.0.1:' + str(parsed.port) + ';localhost:' + str(parsed.port) + ';[::1]:' + str(parsed.port)
            args = [chrome, '--user-data-dir=' + str(profile), '--remote-debugging-port=0', '--remote-debugging-address=127.0.0.1',
                    '--app=' + url, '--no-first-run', '--no-default-browser-check', '--disable-extensions',
                    '--disable-background-networking', '--disable-component-update', '--disable-sync', '--disable-quic',
                    '--disable-default-apps', '--disable-domain-reliability', '--disable-breakpad',
                    '--disable-features=MediaRouter,OptimizationHints', '--force-webrtc-ip-handling-policy=disable_non_proxied_udp',
                    '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1, EXCLUDE [::1]',
                    '--proxy-server=http://127.0.0.1:' + str(proxy.getsockname()[1]), '--proxy-bypass-list=' + bypass]
            process = None
            try:
                process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                view = {'id': view_id, 'project_id': project_id, 'url': url, 'pid': process.pid, 'debug_port': None,
                        'status': 'starting', 'process': process, 'profile': profile, 'proxy': proxy, 'browser_path': None}
                self._views[view_id] = view
                deadline = time.monotonic() + 10
                active = profile / 'DevToolsActivePort'
                while time.monotonic() < deadline:
                    if process.poll() is not None: raise LiveViewError('Owned Chrome exited during startup.')
                    if active.is_file():
                        with active.open(encoding='utf-8') as port_file:
                            raw = port_file.read(2049)
                        if len(raw) > 2048: raise LiveViewError('Browser discovery record exceeded its bound.')
                        lines = raw.splitlines()
                        if len(lines) >= 2 and lines[0].isdigit() and 1 <= int(lines[0]) <= 65535 and lines[1].startswith('/devtools/browser/'):
                            view.update(debug_port=int(lines[0]), browser_path=lines[1], status='running')
                            return self._public(view)
                    time.sleep(.05)
                raise LiveViewError('Owned Chrome debugger did not become ready within 10 seconds.')
            except Exception as exc:
                if process is not None: self._terminate(process)
                proxy.close()
                if view_id in self._views: self._views[view_id]['status'] = 'stopped'
                if isinstance(exc, LiveViewError): raise
                raise LiveViewError('Owned Chrome could not start; process details withheld.') from None

    @staticmethod
    def _terminate(process):
        if process.poll() is None:
            process.terminate()
            try: process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)

    def _owned(self, view_id):
        if view_id not in self._views: raise ValueError('Unknown owned live view.')
        return self._views[view_id]

    @staticmethod
    def _wait_page(ws, expected):
        deadline = min(ws.deadline, time.monotonic() + 4)
        expression = '({href:location.href,ready:document.readyState,width:innerWidth,height:innerHeight})'
        while time.monotonic() < deadline:
            result = ws.call('Runtime.evaluate', {'expression': expression, 'returnByValue': True})
            value = (result.get('result') or {}).get('value') or {}
            href = value.get('href', '')
            if href and href != 'about:blank':
                current = urllib.parse.urlsplit(href)
                if (current.scheme, current.hostname, current.port) != (expected.scheme, expected.hostname, expected.port):
                    raise LiveViewError('Chrome navigation failed or left the configured local origin.')
                if value.get('ready') in ('interactive', 'complete') and value.get('width', 0) > 0 and value.get('height', 0) > 0:
                    return
            time.sleep(.1)
        raise LiveViewError('Configured page has no ready, visible viewport yet; capture can be retried.')

    def stop(self, view_id):
        with self._lock:
            view = self._owned(view_id)
            if view['process'].poll() is None and view['debug_port'] and view['browser_path']:
                ws = None
                try:
                    ws = _WebSocket('ws://127.0.0.1:' + str(view['debug_port']) + view['browser_path'], view['debug_port'], timeout=2)
                    ws.call('Browser.close')
                    view['process'].wait(timeout=2)
                except Exception:
                    pass
                finally:
                    if ws: ws.close()
            self._terminate(view['process'])
            view['proxy'].close()
            view['status'] = 'stopped'
            return self._public(view)

    def snapshot(self, view_id):
        with self._lock:
            view = self._owned(view_id)
            if view['process'].poll() is not None or view['status'] != 'running': raise LiveViewError('Owned Chrome is not running.')
            port = view['debug_port']
            try: targets = json.loads(_http('http://127.0.0.1:' + str(port) + '/json/list'))
            except (ValueError, TypeError): raise LiveViewError('Browser target listing is invalid.') from None
            if not isinstance(targets, list) or len(targets) > 100 or any(not isinstance(item, dict) for item in targets):
                raise LiveViewError('Browser target listing is invalid or oversized.')
            expected = _validate_url(view['url'])
            target = None
            for candidate in targets:
                if candidate.get('type') != 'page': continue
                current = urllib.parse.urlsplit(candidate.get('url', ''))
                if (current.scheme, current.hostname, current.port) == (expected.scheme, expected.hostname, expected.port):
                    target = candidate
                    break
            if not target: raise LiveViewError('No browser page remains on the configured local origin.')
            ws = _WebSocket(target.get('webSocketDebuggerUrl', ''), port, timeout=12)
            try:
                ws.call('Runtime.enable')
                ws.call('Log.enable')
                ws.call('Page.enable')
                self._wait_page(ws, expected)
                data = ws.call('Page.captureScreenshot', {'format': 'png', 'fromSurface': True, 'captureBeyondViewport': False})
                image = base64.b64decode(data.get('data', ''), validate=True)
                if not image.startswith(b'\x89PNG\r\n\x1a\n') or len(image) > MAX_MESSAGE:
                    raise LiveViewError('Browser returned an invalid or oversized PNG.')
                screenshot = view['profile'] / 'screenshot.png'
                temporary = screenshot.with_suffix('.tmp')
                temporary.write_bytes(image)
                os.replace(temporary, screenshot)
                return {**self._public(view), 'screenshot': str(screenshot), 'captured_at': time.time(),
                        'exceptions': [event for event in ws.events if event['type'] == 'exception'],
                        'logs': [event for event in ws.events if event['type'] == 'log'],
                        'log_scope': 'Events observed while capture domains are enabled; not complete browser history.'}
            except LiveViewError:
                raise
            except Exception:
                raise LiveViewError('Browser capture failed; raw protocol details withheld.') from None
            finally:
                ws.close()

    def state(self):
        with self._lock:
            return [self._public(view) for view in self._views.values()]

    def close(self):
        failed = False
        for view in self.state():
            try:
                self.stop(view['id'])
            except Exception:
                failed = True
        if failed:
            raise LiveViewError('At least one owned Chrome could not be closed; other owned views were also checked.')
