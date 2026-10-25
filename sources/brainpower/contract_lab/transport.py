"""Loopback-only synthetic lab. Not a hardened or persistent product service."""
import hashlib
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import socket
import ssl
import threading
import time

from .errors import adapter_error
from .lifecycle import authorize_analysis
from .validation import ContractError, parse_object

REQUEST_LIMIT = 1024 * 1024
RESPONSE_LIMIT = 4 * 1024 * 1024


class TransportError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def client_context(ca, certificate=None, key=None):
    tls = ssl.create_default_context(cafile=ca)
    tls.minimum_version = tls.maximum_version = ssl.TLSVersion.TLSv1_3
    if certificate is not None:
        tls.load_cert_chain(certificate, key)
    return tls


class _Connection(http.client.HTTPSConnection):
    def __init__(self, *args, deadline, **kwargs):
        super().__init__(*args, **kwargs)
        self.deadline = deadline
        self.expired = threading.Event()
        self._wire = None
        self._wire_lock = threading.Lock()

    def _track(self, wire):
        with self._wire_lock:
            if self.expired.is_set():
                wire.close()
                raise TransportError('deadline_exceeded')
            self._wire = wire

    def expire(self):
        self.expired.set()
        with self._wire_lock:
            wire = self._wire
            if wire is not None:
                try:
                    wire.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

    def connect(self):
        connect_end = min(self.deadline, time.monotonic() + self.timeout)
        raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._track(raw)
            raw.settimeout(max(0.001, connect_end - time.monotonic()))
            raw.connect(('127.0.0.1', self.port))
            wire = self._context.wrap_socket(raw, server_hostname='localhost', do_handshake_on_connect=False)
            self.sock = wire
            self._track(wire)
            remaining = connect_end - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Connection budget exhausted')
            wire.settimeout(remaining)
            wire.do_handshake()
            if self.expired.is_set() or time.monotonic() >= self.deadline:
                raise TransportError('deadline_exceeded')
            wire.settimeout(max(0.001, self.deadline - time.monotonic()))
        except BaseException:
            raw.close()
            self.close()
            raise


def analyse(port, ca, certificate, key, envelope, *, total_timeout=15, connect_timeout=3):
    started = time.monotonic()
    for limit, maximum in ((total_timeout, 15), (connect_timeout, 3)):
        if type(limit) not in (int, float) or not math.isfinite(limit) or not 0 < limit <= maximum:
            raise TransportError('invalid_timeout')
    deadline = started + total_timeout
    if type(port) is not int or not 1024 <= port <= 65535:
        raise TransportError('invalid_target')
    try:
        raw = json.dumps(envelope, allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, RecursionError):
        raise TransportError('invalid_request') from None
    if len(raw) > REQUEST_LIMIT:
        raise TransportError('payload_limit')
    connection = _Connection('localhost', port, context=client_context(ca, certificate, key),
                             timeout=connect_timeout, deadline=deadline)
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TransportError('deadline_exceeded')
    timer = threading.Timer(remaining, connection.expire)
    timer.name = 'aurelia-t2-deadline'
    timer.start()
    try:
        connection.request('POST', '/analysis', raw, {'Content-Type': 'application/json'})
        response = connection.getresponse()
        if response.status != 200:
            raise TransportError('http_' + str(response.status))
        lengths = response.headers.get_all('Content-Length', [])
        encodings = response.headers.get_all('Transfer-Encoding', [])
        if (len(lengths) > 1 or lengths and encodings or len(encodings) > 1
                or encodings and encodings[0].lower() != 'chunked'
                or response.headers.get('Content-Encoding')
                or response.headers.get_content_type() != 'application/json'):
            raise TransportError('invalid_response')
        declared = None
        if lengths:
            if (not lengths[0].isascii() or not lengths[0].isdigit()
                    or len(lengths[0]) > 10):
                raise TransportError('invalid_response')
            declared = int(lengths[0])
            if declared > RESPONSE_LIMIT:
                raise TransportError('response_limit')
        body = response.read(RESPONSE_LIMIT + 1)
        if connection.expired.is_set() or time.monotonic() >= deadline:
            raise TransportError('deadline_exceeded')
        if declared is not None and len(body) != declared:
            raise TransportError('invalid_response')
        data = parse_object(body, RESPONSE_LIMIT)
        passport = data.get('passport')
        if (data.keys() != {'result', 'passport'} or type(data['result']) is not int
                or not 0 <= data['result'] <= 200 or type(passport) is not dict
                or passport != {'data_class': 'synthetic', 'signatur_status': 'unsigned',
                                'release_id': envelope['context']['release_id']}
                or type(envelope['payload']['value']) is not int
                or data['result'] != envelope['payload']['value'] * 2):
            raise TransportError('invalid_response')
        return data
    except (OSError, http.client.HTTPException, ContractError, KeyError, TypeError):
        if connection.expired.is_set() or time.monotonic() >= deadline:
            raise TransportError('deadline_exceeded') from None
        raise TransportError('transport_or_response_failure') from None
    finally:
        timer.cancel()
        timer.join()
        connection.close()


class LabServer:
    def __init__(self, certificate, key, ca, allowed, approved, authority, now=None):
        self._allowed = set(allowed)
        self._policy_window = None
        self._policy_revision = 0
        self.approved = dict(approved)
        self.authority = authority
        self.now = now or (lambda: int(time.time()))
        self._lock = threading.Lock()
        self.idle = threading.Event()
        self.idle.set()
        self.compute = lambda value: value * 2
        self.calls = 0
        self.last_tls_version = None
        self._clients = set()
        self.thread = None
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.minimum_version = tls.maximum_version = ssl.TLSVersion.TLSv1_3
        tls.load_cert_chain(certificate, key)
        tls.load_verify_locations(cafile=ca)
        tls.verify_mode = ssl.CERT_REQUIRED
        lab = self

        class Server(ThreadingHTTPServer):
            daemon_threads = False

            def get_request(self):
                raw, addr = super().get_request()
                raw.settimeout(2)
                try:
                    client = tls.wrap_socket(raw, server_side=True)
                except BaseException:
                    raw.close()
                    raise
                with lab._lock:
                    lab._clients.add(client)
                return client, addr

            def close_request(self, request):
                with lab._lock:
                    lab._clients.discard(request)
                super().close_request(request)

            def handle_error(self, request, client_address):
                # Unexpected handler failure is visible without raw payload/traceback.
                with lab._lock:
                    lab.handler_failures += 1

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            def log_message(self, *args):
                pass

            def send_error(self, code, message=None, explain=None):
                self.reply(code, {'code': 'request_rejected'}, True)

            def reply(self, status, body, close=False):
                raw = json.dumps(body).encode('utf-8')
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(raw)))
                if close:
                    self.send_header('Connection', 'close')
                    self.close_connection = True
                self.end_headers()
                if self.command != 'HEAD':
                    self.wfile.write(raw)

            def do_POST(self):
                if self.path != '/analysis':
                    return self.reply(404, {'code': 'not_found'}, True)
                if self.headers.get('Content-Encoding') or self.headers.get('Transfer-Encoding'):
                    return self.reply(415, {'code': 'unsupported_encoding'}, True)
                lengths = self.headers.get_all('Content-Length', [])
                if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit():
                    return self.reply(400, {'code': 'invalid_length'}, True)
                if len(lengths[0]) > 10 or int(lengths[0]) > REQUEST_LIMIT:
                    return self.reply(413, {'code': 'payload_limit'}, True)
                length = int(lengths[0])
                reserved = False
                try:
                    raw = self.rfile.read(length)
                    if len(raw) != length:
                        return self.reply(400, {'code': 'invalid_length'}, True)
                    peer = hashlib.sha256(self.connection.getpeercert(binary_form=True)).hexdigest()
                    with lab._lock:
                        lab._require_policy()
                        permitted = peer in lab._allowed
                        lab.last_tls_version = self.connection.version()
                    if not permitted:
                        return self.reply(403, {'code': 'forbidden'})
                    envelope = parse_object(raw, REQUEST_LIMIT)
                    if envelope.keys() != {'context', 'payload'}:
                        raise ContractError('invalid_request')
                    authorize_analysis(envelope['context'], lab.approved, lab.authority, lab.now())
                    payload = envelope['payload']
                    if (type(payload) is not dict or payload.keys() != {'value'}
                            or type(payload['value']) is not int or not 0 <= payload['value'] <= 100):
                        raise ContractError('invalid_request')
                    with lab._lock:
                        lab._require_policy()
                        if peer not in lab._allowed:
                            raise ContractError('forbidden')
                        authorize_analysis(envelope['context'], lab.approved, lab.authority, lab.now())
                        if not lab.idle.is_set():
                            raise ContractError('busy')
                        lab.idle.clear()
                        reserved = True
                        lab.calls += 1
                    # Fixture callback is local code, never supplied by HTTP input.
                    value = lab.compute(payload['value'])
                    with lab._lock:
                        lab._require_policy()
                        if peer not in lab._allowed:
                            raise ContractError('forbidden')
                        authorize_analysis(envelope['context'], lab.approved, lab.authority, lab.now())
                    self.reply(200, {'result': value, 'passport': {'data_class': 'synthetic',
                               'signatur_status': 'unsigned', 'release_id': lab.approved['release_id']}})
                except ContractError as exc:
                    error = adapter_error(exc.code)
                    self.reply(error['status'], {'code': error['code']}, True)
                except (OSError, http.client.HTTPException):
                    self.close_connection = True
                finally:
                    if reserved:
                        lab.idle.set()

        self.handler_failures = 0
        self.server = Server(('127.0.0.1', 0), Handler)
        self.port = self.server.server_address[1]

    @staticmethod
    def _valid_fingerprint(value):
        return (type(value) is str and len(value) == 64
                and all(character in '0123456789abcdef' for character in value))

    def replace_policy(self, allowed, *, valid_until, revision):
        with self._lock:
            self._policy_window = None
            now = self.now()
            # Sixty seconds is a synthetic lab bound, not a production policy.
            if (type(now) is not int or type(valid_until) is not int
                    or not now < valid_until <= now + 60
                    or type(revision) is not int or revision <= self._policy_revision
                    or type(allowed) not in (set, frozenset, list, tuple)
                    or not all(self._valid_fingerprint(value) for value in allowed)):
                raise ContractError('invalid_request')
            self._allowed = set(allowed)
            self._policy_revision = revision
            self._policy_window = (now, valid_until)

    def _require_policy(self):
        now = self.now()
        if (self._policy_window is None or type(now) is not int
                or not self._policy_window[0] <= now < self._policy_window[1]):
            raise ContractError('authorization_unavailable')

    def allow(self, fingerprint):
        with self._lock:
            self._require_policy()
            if not self._valid_fingerprint(fingerprint):
                raise ContractError('invalid_request')
            self._allowed.add(fingerprint)

    def revoke(self, fingerprint):
        with self._lock:
            self._allowed.discard(fingerprint)

    def start(self):
        if self.thread is not None:
            raise RuntimeError('Test server already started')
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={'poll_interval': 0.05}, name='aurelia-t2-lab')
        self.thread.start()

    def close(self):
        if self.thread is not None:
            self.server.shutdown()
        with self._lock:
            clients = list(self._clients)
        for client in clients:
            try:
                client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        self.server.server_close()
        if self.thread is not None:
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                raise RuntimeError('Test server did not stop')
