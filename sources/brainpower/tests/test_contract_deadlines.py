"""Adversarial actual loopback responses, no product endpoints."""
import json
import time
import threading
import unittest

from contract_tls_fixture import Certificates
from contract_wire_fixture import WirePeer
from test_contract_lab import context
from contract_lab.transport import analyse, TransportError, RESPONSE_LIMIT


BODY = json.dumps({'result': 14, 'passport': {'data_class': 'synthetic',
                  'signatur_status': 'unsigned', 'release_id': 'release-1'}}).encode()


def response(body=BODY, headers=None, status=200):
    fields = headers if headers is not None else [('Content-Length', str(len(body)))]
    text = 'HTTP/1.1 ' + str(status) + ' Synthetic\r\nContent-Type: application/json\r\n'
    text += ''.join(key + ': ' + value + '\r\n' for key, value in fields)
    return text.encode('ascii') + b'\r\n' + body


class DeadlineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certs = Certificates()

    @classmethod
    def tearDownClass(cls):
        cls.certs.close()
        if cls.certs.root.exists():
            raise AssertionError('Test key directory remained')

    def peer(self, script, handshake=True):
        peer = WirePeer(self.certs, script, handshake)
        self.addCleanup(peer.close)
        return peer

    def call(self, peer, **options):
        return analyse(peer.port, self.certs.path('ca.pem'), self.certs.path('client.pem'),
                       self.certs.path('client.key'), {'context': context(), 'payload': {'value': 7}},
                       **options)

    def test_total_deadline_with_trickling_body(self):
        def drip(connection, stop):
            connection.sendall(response(b'', [('Content-Length', str(len(BODY)))]))
            for byte in BODY:
                if stop.wait(0.04):
                    return
                connection.sendall(bytes([byte]))
        peer = self.peer(drip)
        started = time.monotonic()
        with self.assertRaises(TransportError) as caught:
            self.call(peer, total_timeout=0.35)
        self.assertEqual(caught.exception.code, 'deadline_exceeded')
        self.assertLess(time.monotonic() - started, 1.5)
        self.assertEqual(peer.requests, 1)
        self.assertEqual(peer.accepted, 1)

    def test_total_deadline_with_trickling_headers(self):
        def drip(connection, stop):
            for byte in response():
                if stop.wait(0.04):
                    return
                connection.sendall(bytes([byte]))
        peer = self.peer(drip)
        started = time.monotonic()
        with self.assertRaises(TransportError) as caught:
            self.call(peer, total_timeout=0.35)
        self.assertEqual(caught.exception.code, 'deadline_exceeded')
        self.assertLess(time.monotonic() - started, 1.5)

    def test_handshake_deadline(self):
        peer = self.peer(lambda *_: None, handshake=False)
        started = time.monotonic()
        with self.assertRaises(TransportError):
            self.call(peer, total_timeout=1, connect_timeout=0.2)
        self.assertLess(time.monotonic() - started, 1)
        self.assertEqual(peer.accepted, 1)
        self.assertEqual(peer.requests, 0)

    def test_invalid_time_limits(self):
        peer = self.peer(lambda connection, _: connection.sendall(response()))
        for bad in (0, -1, True, float('inf'), float('nan'), '1', 1e100):
            for field in ('total_timeout', 'connect_timeout'):
                with self.subTest(field=field, value=bad), self.assertRaises(TransportError):
                    self.call(peer, **{field: bad})
        self.assertEqual(peer.accepted, 0)

    def test_response_byte_boundaries(self):
        for size in (RESPONSE_LIMIT - 1, RESPONSE_LIMIT, RESPONSE_LIMIT + 1):
            body = BODY + b' ' * (size - len(BODY))
            peer = self.peer(lambda connection, _, body=body: connection.sendall(response(body)))
            with self.subTest(size=size):
                if size > RESPONSE_LIMIT:
                    with self.assertRaises(TransportError):
                        self.call(peer)
                else:
                    self.assertEqual(self.call(peer)['result'], 14)

    def test_no_length_response_is_bounded(self):
        body = BODY + b' ' * (RESPONSE_LIMIT + 1 - len(BODY))
        peer = self.peer(lambda connection, _: connection.sendall(response(body, [('Connection', 'close')])))
        with self.assertRaises(TransportError):
            self.call(peer)

    def test_response_framing_and_encoding_rejected(self):
        variants = [[('Content-Length', str(len(BODY))), ('Content-Length', '1')],
                    [('Content-Length', str(len(BODY))), ('Transfer-Encoding', 'chunked')],
                    [('Content-Length', str(len(BODY))), ('Content-Encoding', 'gzip')],
                    [('Content-Length', '-1')]]
        for fields in variants:
            peer = self.peer(lambda connection, _, fields=fields: connection.sendall(response(BODY, fields)))
            with self.subTest(fields=fields), self.assertRaises(TransportError):
                self.call(peer)

    def test_truncated_response_no_retry(self):
        peer = self.peer(lambda connection, _: connection.sendall(response(BODY[:15], [('Content-Length', str(len(BODY)))])))
        with self.assertRaises(TransportError):
            self.call(peer)
        self.assertEqual(peer.requests, 1)
        self.assertEqual(peer.accepted, 1)

    def test_disconnect_after_acceptance_no_retry(self):
        peer = self.peer(lambda *_: None)
        with self.assertRaises(TransportError):
            self.call(peer)
        self.assertEqual(peer.requests, 1)
        self.assertEqual(peer.accepted, 1)

    def test_redirect_does_not_contact_sentinel(self):
        sentinel = self.peer(lambda connection, _: connection.sendall(response()))
        redirect = response(b'', [('Location', 'https://localhost:' + str(sentinel.port) + '/analysis'),
                                  ('Content-Length', '0')], status=302)
        peer = self.peer(lambda connection, _: connection.sendall(redirect))
        with self.assertRaises(TransportError) as caught:
            self.call(peer)
        self.assertEqual(caught.exception.code, 'http_302')
        self.assertEqual(sentinel.accepted, 0)
        self.assertEqual(peer.requests, 1)

    def test_wrong_value_rejected(self):
        body = BODY.replace(b'14', b'15', 1)
        peer = self.peer(lambda connection, _: connection.sendall(response(body)))
        with self.assertRaises(TransportError):
            self.call(peer)

    def test_chunked_response_size_limit(self):
        for size in (len(BODY), RESPONSE_LIMIT + 1):
            body = BODY + b' ' * (size - len(BODY))
            chunked = hex(len(body))[2:].encode() + b'\r\n' + body + b'\r\n0\r\n\r\n'
            peer = self.peer(lambda connection, _, chunked=chunked:
                             connection.sendall(response(chunked, [('Transfer-Encoding', 'chunked')])))
            with self.subTest(size=size):
                if size > RESPONSE_LIMIT:
                    with self.assertRaises(TransportError):
                        self.call(peer)
                else:
                    self.assertEqual(self.call(peer)['result'], 14)

    def test_deadline_watchdog_removed_after_success(self):
        peer = self.peer(lambda connection, _: connection.sendall(response()))
        self.call(peer)
        self.assertFalse(any(t.name == 'aurelia-t2-deadline' for t in threading.enumerate()))


if __name__ == '__main__':
    unittest.main()
