import base64
import hashlib
import json
from pathlib import Path
import socket
import struct
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

from governor_workbench.live_view import LiveViews, LiveViewError, _WebSocket, _validate_url, _http, MAX_MESSAGE, MAX_EVENTS
from governor_workbench.config import load_config


class FakeSocket:
    def __init__(self, data=b''):
        self.data = bytearray(data)
        self.sent = []
    def recv(self, size):
        value = bytes(self.data[:size])
        del self.data[:size]
        return value
    def sendall(self, data): self.sent.append(data)
    def settimeout(self, value): pass
    def close(self): pass


def frame(opcode, payload, final=True):
    return bytes([(128 if final else 0) | opcode, len(payload)]) + payload


class WebSocketTests(unittest.TestCase):
    def socket(self, data):
        ws = _WebSocket.__new__(_WebSocket)
        ws.sock, ws.buffer, ws.deadline, ws.serial = FakeSocket(data), bytearray(), time.monotonic() + 3, 0
        ws.events = []
        return ws

    def test_fragmentation_ping_and_client_mask(self):
        payload = b'{"id":1,"result":{"ok":true}}'
        ws = self.socket(frame(1, payload[:10], False) + frame(9, b'hi') + frame(0, payload[10:]))
        self.assertTrue(ws.call('Page.enable')['ok'])
        self.assertTrue(all(data[1] & 128 for data in ws.sock.sent))
        self.assertEqual(ws.sock.sent[1][0], 0x8A)

    def test_oversized_frame_rejected_before_reading_payload(self):
        ws = self.socket(bytes([0x81, 127]) + struct.pack('!Q', MAX_MESSAGE + 1))
        with self.assertRaises(LiveViewError): ws.call('Page.enable')

    def test_deadline_and_bad_frames(self):
        ws = self.socket(b'')
        ws.deadline = time.monotonic() - 1
        with self.assertRaises(LiveViewError): ws.call('Page.enable')

    def test_socket_send_timeout_is_sanitized(self):
        ws = self.socket(b'')
        ws.sock.sendall = Mock(side_effect=socket.timeout())
        with self.assertRaises(LiveViewError): ws.call('Page.enable')
        ws = self.socket(bytes([0x81, 0x80]))
        with self.assertRaises(LiveViewError): ws.call('Page.enable')

    def test_handshake_validates_accept(self):
        key = base64.b64encode(b'0' * 16).decode()
        accept = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
        headers = ('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ' + accept + '\r\n\r\n').encode()
        sock = FakeSocket(headers)
        with patch('socket.create_connection', return_value=sock), patch('os.urandom', return_value=b'0' * 16):
            ws = _WebSocket('ws://127.0.0.1:4444/devtools/page/abc', 4444)
        self.assertIn(b'GET /devtools/page/abc HTTP/1.1', sock.sent[0])
        ws.close()

    def test_event_history_is_bounded(self):
        ws = self.socket(b'')
        for _ in range(MAX_EVENTS + 20):
            ws._record({'method': 'Log.entryAdded', 'params': {'entry': {'text': 'x' * 3000, 'level': 'error'}}})
        self.assertEqual(len(ws.events), MAX_EVENTS)
        self.assertEqual(len(ws.events[0]['text']), 2000)


class LiveViewTests(unittest.TestCase):
    def test_config_rejects_duplicate_module_port_across_loopback_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'config.json'
            path.write_text(json.dumps({'version': 1, 'projects': [
                {'id': 'radiworks', 'name': 'RadiWorks', 'path': tmp},
                {'id': 'radi144', 'name': 'Radi144', 'path': tmp}],
                'live_views': {
                    'radiworks': {'url': 'http://localhost:8090/'},
                    'radi144': {'url': 'http://127.0.0.1:8090/user_workflow.html'}}}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Port.*8090'):
                load_config(path)

    def test_preflight_rejects_wrong_service_before_browser_launch(self):
        with tempfile.TemporaryDirectory() as tmp, patch('subprocess.Popen') as popen:
            url = 'http://127.0.0.1:8091/'
            views = LiveViews({'data_dir': tmp, 'live_views': {
                'radiworks': {'url': url, 'expected_openapi_title': 'RadiWorks Engine'}}})
            with patch('governor_workbench.live_view._http', side_effect=[
                    b'{"message":"12x12 Resonance Matrix Engine is running"}',
                    b'{"info":{"title":"12x12 Resonance Matrix Standalone"}}']) as request:
                with self.assertRaisesRegex(LiveViewError, 'identity'):
                    views.start('radiworks', url)
            self.assertEqual(request.call_args_list[1].args[0], 'http://127.0.0.1:8091/openapi.json')
            popen.assert_not_called()

    def test_preflight_accepts_matching_openapi_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            views = LiveViews({'data_dir': tmp})
            with patch('governor_workbench.live_view._http', side_effect=[
                    b'<html>Module</html>', b'{"info":{"title":"Morphic Engine V1 Web Shell"}}']) as request:
                views._preflight('http://127.0.0.1:8000/static/index.html', 'Morphic Engine V1 Web Shell')
            self.assertEqual(request.call_args_list[1].args[0], 'http://127.0.0.1:8000/openapi.json')

    def test_preflight_rejects_missing_openapi_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            views = LiveViews({'data_dir': tmp})
            with patch('governor_workbench.live_view._http', side_effect=[b'<html>Module</html>', b'{}']):
                with self.assertRaisesRegex(LiveViewError, 'identity'):
                    views._preflight('http://127.0.0.1:8000/', 'Morphic Engine V1 Web Shell')

    def test_close_attempts_every_owned_view_even_if_one_fails(self):
        views = LiveViews({'data_dir': '.'})
        with patch.object(views, 'state', return_value=[{'id': 'one'}, {'id': 'two'}]), patch.object(views, 'stop', side_effect=[LiveViewError('failed'), {}]) as stop:
            with self.assertRaises(LiveViewError): views.close()
        self.assertEqual(stop.call_count, 2)

    def test_startup_timeout_terminates_only_started_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            views = LiveViews({'data_dir': tmp, 'live_views': {'p': {'url': 'http://localhost:8000'}}})
            process = Mock(pid=100)
            process.poll.return_value = None
            with patch.object(views, '_chrome', return_value='chrome.exe'), patch.object(views, '_preflight'), patch('subprocess.Popen', return_value=process), patch('time.monotonic', side_effect=[0, 11]):
                with self.assertRaises(LiveViewError): views.start('p', 'http://localhost:8000')
            process.terminate.assert_called_once()
    def test_http_total_read_deadline(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read1.return_value = b'x'
        with patch('urllib.request.OpenerDirector.open', return_value=response), patch('time.monotonic', side_effect=[0, 0, 3]):
            with self.assertRaisesRegex(LiveViewError, 'deadline'): _http('http://127.0.0.1:8787/', timeout=2)
        self.assertEqual(response.read1.call_count, 1)

    def test_snapshot_refuses_navigation_outside_selected_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            views = LiveViews({'data_dir': tmp})
            process = Mock()
            process.poll.return_value = None
            views._views['owned'] = {'process': process, 'status': 'running', 'debug_port': 4444, 'url': 'http://localhost:8000'}
            with patch('governor_workbench.live_view._http', return_value=b'[{"type":"page","url":"https://example.com/"}]'), patch('governor_workbench.live_view._WebSocket') as ws:
                with self.assertRaises(LiveViewError): views.snapshot('owned')
                ws.assert_not_called()

    def test_snapshot_writes_png_and_returns_bounded_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            views = LiveViews({'data_dir': tmp})
            profile = Path(tmp) / 'live' / ('a' * 32)
            profile.mkdir(parents=True)
            process = Mock()
            process.poll.return_value = None
            views._views['a' * 32] = dict(id='a' * 32, project_id='p', url='http://localhost:8000', pid=42, debug_port=4444,
                                         process=process, status='running', profile=profile, proxy=Mock())
            png = b'\x89PNG\r\n\x1a\n' + b'test-data'
            ws = Mock(events=[{'type': 'exception', 'level': 'error', 'text': 'Synthetic exception'}])
            ws.deadline = time.monotonic() + 10
            ws.call.side_effect = lambda method, params=None: {'result': {'value': {'href': 'http://localhost:8000/', 'ready': 'complete', 'width': 800, 'height': 600}}} if method == 'Runtime.evaluate' else {'data': base64.b64encode(png).decode()}
            targets = b'[{"type":"page","url":"http://localhost:8000/","webSocketDebuggerUrl":"ws://127.0.0.1:4444/devtools/page/p"}]'
            with patch('governor_workbench.live_view._http', return_value=targets), patch('governor_workbench.live_view._WebSocket', return_value=ws):
                result = views.snapshot('a' * 32)
            self.assertEqual(Path(result['screenshot']).name, 'screenshot.png')
            self.assertEqual(Path(result['screenshot']).read_bytes(), png)
            self.assertEqual(len(result['exceptions']), 1)
            ws.close.assert_called_once()
    def test_url_restrictions(self):
        self.assertEqual(_validate_url('http://127.0.0.1:8787/').port, 8787)
        for url in ('https://127.0.0.1:8787', 'http://example.com:8787', 'http://localhost',
                    'http://localhost:3000', 'http://user@localhost:8787', 'http://localhost:8787/#x'):
            with self.assertRaises(ValueError): _validate_url(url)

    def test_unconfigured_or_different_url_never_launches(self):
        with tempfile.TemporaryDirectory() as tmp, patch('subprocess.Popen') as popen:
            views = LiveViews({'data_dir': tmp, 'live_views': {'governor': {'url': 'http://127.0.0.1:8787/'}}})
            with self.assertRaises(ValueError): views.start('missing', 'http://127.0.0.1:8787/')
            with self.assertRaises(ValueError): views.start('governor', 'http://127.0.0.1:8788/')
            popen.assert_not_called()

    def test_start_uses_unique_profile_stop_only_owned_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            views = LiveViews({'data_dir': tmp, 'live_views': {'governor': {'url': 'http://127.0.0.1:8787/'}}})
            process = Mock(pid=4242)
            process.poll.return_value = None
            def spawn(args, **kwargs):
                profile = Path(next(arg.split('=', 1)[1] for arg in args if arg.startswith('--user-data-dir=')))
                (profile / 'DevToolsActivePort').write_text('4444\n/devtools/browser/owned\n')
                self.assertIn('--remote-debugging-port=0', args)
                self.assertIn('--app=http://127.0.0.1:8787/', args)
                resolver = next(arg for arg in args if arg.startswith('--host-resolver-rules='))
                self.assertIn('EXCLUDE 127.0.0.1', resolver)
                self.assertTrue(profile.is_relative_to(Path(tmp).resolve()))
                return process
            with patch.object(views, '_chrome', return_value='chrome.exe'), patch.object(views, '_preflight'), patch('subprocess.Popen', side_effect=spawn):
                result = views.start('governor', 'http://127.0.0.1:8787/')
            self.assertEqual(result['pid'], 4242)
            self.assertEqual(result['debug_port'], 4444)
            with self.assertRaises(ValueError): views.stop('unknown')
            with patch('governor_workbench.live_view._WebSocket', side_effect=LiveViewError('offline')):
                views.stop(result['id'])
            process.terminate.assert_called_once()
            process.wait.assert_called()

    def test_preflight_failure_does_not_launch(self):
        with tempfile.TemporaryDirectory() as tmp, patch('subprocess.Popen') as popen:
            views = LiveViews({'data_dir': tmp, 'live_views': {'p': {'url': 'http://localhost:8000'}}})
            with patch.object(views, '_preflight', side_effect=LiveViewError('offline')):
                with self.assertRaises(LiveViewError): views.start('p', 'http://localhost:8000')
            popen.assert_not_called()

    def test_waits_for_real_viewport_and_refuses_error_document(self):
        ws = Mock()
        ws.deadline = time.monotonic() + 10
        ws.call.side_effect = [
            {'result': {'value': {'href': 'about:blank', 'ready': 'complete', 'width': 0, 'height': 0}}},
            {'result': {'value': {'href': 'http://localhost:8000/', 'ready': 'complete', 'width': 800, 'height': 600}}},
        ]
        with patch('time.sleep'):
            LiveViews._wait_page(ws, _validate_url('http://localhost:8000/'))
        self.assertEqual(ws.call.call_count, 2)
        ws.call.side_effect = None
        ws.call.return_value = {'result': {'value': {'href': 'chrome-error://chromewebdata/', 'ready': 'complete', 'width': 800, 'height': 600}}}
        with self.assertRaises(LiveViewError): LiveViews._wait_page(ws, _validate_url('http://localhost:8000/'))
