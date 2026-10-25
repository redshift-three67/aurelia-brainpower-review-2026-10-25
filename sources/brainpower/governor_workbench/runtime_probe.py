"""Fixed loopback readiness fixture. Never serves files or executes requests."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket
import sys


class Server(HTTPServer):
    allow_reuse_address = False

    def server_bind(self):
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def get_request(self):
        sock, address = super().get_request()
        sock.settimeout(1)
        return sock, address


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass

    def do_GET(self):
        if self.path != '/health' or self.headers.get('Host') != '127.0.0.1:' + str(self.server.server_port):
            self.send_error(404); return
        body = json.dumps({'service': 'governor-runtime-probe', 'instance_id': self.server.instance_id}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    server = Server(('127.0.0.1', int(sys.argv[1])), Handler)
    server.instance_id = sys.argv[2]
    server.serve_forever(poll_interval=0.2)
