"""Bounded loopback fault peer for actual TLS tests, independent of LabServer."""
import socket
import socketserver
import ssl
import threading


class WirePeer:
    def __init__(self, certificates, script, handshake=True):
        self.script = script
        self.stop = threading.Event()
        self.accepted = 0
        self.requests = 0
        self.errors = []
        self.lock = threading.Lock()
        peer = self
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.minimum_version = tls.maximum_version = ssl.TLSVersion.TLSv1_3
        tls.load_cert_chain(certificates.path('server.pem'), certificates.path('server.key'))
        tls.load_verify_locations(cafile=certificates.path('ca.pem'))
        tls.verify_mode = ssl.CERT_REQUIRED

        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                with peer.lock:
                    peer.accepted += 1
                self.request.settimeout(3)
                if not handshake:
                    peer.stop.wait(2)
                    return
                try:
                    with tls.wrap_socket(self.request, server_side=True) as connection:
                        data = b''
                        while b'\r\n\r\n' not in data:
                            part = connection.recv(4096)
                            if not part:
                                return
                            data += part
                            if len(data) > 65536:
                                raise AssertionError('Fixture header overflow')
                        headers, body = data.split(b'\r\n\r\n', 1)
                        lengths = [line.split(b':', 1)[1].strip() for line in headers.split(b'\r\n')
                                   if line.lower().startswith(b'content-length:')]
                        length = int(lengths[0])
                        if length > 1024 * 1024:
                            raise AssertionError('Fixture body overflow')
                        while len(body) < length:
                            part = connection.recv(min(4096, length - len(body)))
                            if not part:
                                return
                            body += part
                        with peer.lock:
                            peer.requests += 1
                        peer.script(connection, peer.stop)
                except OSError:
                    # Client deadline/disconnect is expected in these fault scenarios.
                    pass
                except Exception as exc:
                    peer.errors.append(type(exc).__name__)

        class Server(socketserver.ThreadingTCPServer):
            daemon_threads = False

        self.server = Server(('127.0.0.1', 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={'poll_interval': 0.02}, name='t2-wire-fixture')
        self.thread.start()

    def close(self):
        self.stop.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        if self.thread.is_alive() or self.errors:
            raise AssertionError('Wire fixture cleanup/error: ' + repr(self.errors))
