"""Real loopback TLS with synthetic data; no Governor or product imports."""
import http.client
import json
import ssl
import threading
import unittest

from contract_tls_fixture import Certificates
from test_contract_lab import approved, context
from contract_lab.authority import TestAuthority
from contract_lab.transport import LabServer, TransportError, analyse, client_context


class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certs = Certificates()

    @classmethod
    def tearDownClass(cls):
        root = cls.certs.root
        cls.certs.close()
        if root.exists():
            raise AssertionError('Temporary certificate directory remained')

    def setUp(self):
        self.authority = TestAuthority([('A', 'alice', 'synthetic', 'analysis', 'rev-1')])
        self.server = LabServer(self.certs.path('server.pem'), self.certs.path('server.key'),
                                self.certs.path('ca.pem'), {self.certs.fingerprint('client')},
                                approved(), self.authority, now=lambda: 100)
        self.server.replace_policy({self.certs.fingerprint('client')}, valid_until=160, revision=1)
        self.server.start()
        self.addCleanup(self.server.close)

    def tearDown(self):
        self.assertEqual(self.server.handler_failures, 0)

    def call(self, name='client', data=None):
        return analyse(self.server.port, self.certs.path('ca.pem'),
                       self.certs.path(name + '.pem') if name else None,
                       self.certs.path(name + '.key') if name else None,
                       data if data is not None else {'context': context(), 'payload': {'value': 7}})

    def test_positive_tls13_and_unsigned_result(self):
        result = self.call()
        self.assertEqual(result, {'result': 14, 'passport': {'data_class': 'synthetic',
                         'signatur_status': 'unsigned', 'release_id': 'release-1'}})
        self.assertEqual(self.server.calls, 1)
        self.assertEqual(self.server.last_tls_version, 'TLSv1.3')

    def test_missing_certificate(self):
        with self.assertRaises(TransportError):
            self.call(None)
        self.assertEqual(self.server.calls, 0)

    def test_foreign_certificate(self):
        with self.assertRaises(TransportError):
            self.call('foreign')
        self.assertEqual(self.server.calls, 0)

    def test_same_ca_is_not_authorization(self):
        with self.assertRaises(TransportError) as caught:
            self.call('denied')
        self.assertEqual(caught.exception.code, 'http_403')
        self.assertEqual(self.server.calls, 0)

    def test_rotation_and_revocation(self):
        self.call()
        self.server.allow(self.certs.fingerprint('rotated'))
        self.call('rotated')
        self.server.revoke(self.certs.fingerprint('client'))
        with self.assertRaises(TransportError):
            self.call('client')
        self.call('rotated')
        self.assertEqual(self.server.calls, 3)

    def test_revoked_existing_connection(self):
        connection = self.connection()
        self.addCleanup(connection.close)
        body = json.dumps({'context': context(), 'payload': {'value': 7}})
        connection.request('POST', '/analysis', body, {'Content-Type': 'application/json'})
        first = connection.getresponse()
        self.assertEqual(first.status, 200)
        first.read()
        original_socket = connection.sock
        self.server.revoke(self.certs.fingerprint('client'))
        connection.request('POST', '/analysis', body, {'Content-Type': 'application/json'})
        second = connection.getresponse()
        self.assertEqual(second.status, 403)
        self.assertIs(connection.sock, original_socket)
        second.read()
        self.assertEqual(self.server.calls, 1)

    def connection(self):
        tls = client_context(self.certs.path('ca.pem'), self.certs.path('client.pem'), self.certs.path('client.key'))
        return http.client.HTTPSConnection('localhost', self.server.port, context=tls, timeout=3)

    def test_bad_server_name(self):
        # 127.0.0.1 is deliberately absent from the server certificate SAN.
        tls = client_context(self.certs.path('ca.pem'), self.certs.path('client.pem'), self.certs.path('client.key'))
        connection = http.client.HTTPSConnection('127.0.0.1', self.server.port, context=tls, timeout=3)
        self.addCleanup(connection.close)
        with self.assertRaises(ssl.SSLCertVerificationError):
            connection.request('POST', '/analysis', b'{}')
        self.assertEqual(self.server.calls, 0)

    def test_tls12_rejected(self):
        tls = client_context(self.certs.path('ca.pem'), self.certs.path('client.pem'), self.certs.path('client.key'))
        tls.minimum_version = tls.maximum_version = ssl.TLSVersion.TLSv1_2
        connection = http.client.HTTPSConnection('localhost', self.server.port, context=tls, timeout=3)
        self.addCleanup(connection.close)
        with self.assertRaises((ssl.SSLError, OSError)):
            connection.request('POST', '/analysis', b'{}')
        self.assertEqual(self.server.calls, 0)

    def test_context_expired(self):
        with self.assertRaises(TransportError):
            self.call(data={'context': context(issued_at=60, expires_at=90), 'payload': {'value': 7}})
        self.assertEqual(self.server.calls, 0)

    def test_foreign_tenant(self):
        with self.assertRaises(TransportError):
            self.call(data={'context': context(tenant_id='B'), 'payload': {'value': 7}})
        self.assertEqual(self.server.calls, 0)

    def test_grant_revoked(self):
        self.authority.revoke('A', 'alice', 'synthetic', 'analysis', 'rev-1')
        with self.assertRaises(TransportError):
            self.call()
        self.assertEqual(self.server.calls, 0)

    def test_payload_contract_and_no_retry(self):
        for payload in ({'value': True}, {'value': 101}, {'value': -1}, {'value': 7, 'tenant_id': 'B'}):
            with self.subTest(payload=payload), self.assertRaises(TransportError):
                self.call(data={'context': context(), 'payload': payload})
        self.assertEqual(self.server.calls, 0)
        self.call()
        self.assertEqual(self.server.calls, 1)

    def test_unknown_path_and_compression(self):
        for path, headers, expected in [('/other', {}, 404),
                                        ('/analysis', {'Content-Encoding': 'gzip'}, 415)]:
            connection = self.connection()
            try:
                connection.request('POST', path, b'{}', headers)
                response = connection.getresponse()
                self.assertEqual(response.status, expected)
                response.read()
            finally:
                connection.close()
        self.assertEqual(self.server.calls, 0)

    def test_large_request_blocked(self):
        with self.assertRaises(TransportError):
            self.call(data={'padding': 'x' * (1024 * 1024)})
        self.assertEqual(self.server.calls, 0)

    def test_server_rejects_oversized_declared_length(self):
        connection = self.connection()
        try:
            connection.putrequest('POST', '/analysis')
            connection.putheader('Content-Length', str(1024 * 1024 + 1))
            connection.endheaders()
            response = connection.getresponse()
            self.assertEqual(response.status, 413)
            response.read()
        finally:
            connection.close()
        self.assertEqual(self.server.calls, 0)

    def test_server_rejects_ambiguous_framing(self):
        for headers in [[('Content-Length', '2'), ('Content-Length', '3')],
                        [('Transfer-Encoding', 'chunked')], []]:
            connection = self.connection()
            try:
                connection.putrequest('POST', '/analysis')
                for key, value in headers:
                    connection.putheader(key, value)
                connection.endheaders()
                response = connection.getresponse()
                self.assertIn(response.status, (400, 415))
                response.read()
            finally:
                connection.close()
        self.assertEqual(self.server.calls, 0)

    def test_timeout_keeps_server_slot_until_work_finishes(self):
        entered, release = threading.Event(), threading.Event()
        errors = []
        def work(value):
            entered.set()
            if not release.wait(3):
                raise AssertionError('Fixture work was not released')
            return value * 2
        self.server.compute = work
        def first_call():
            try:
                analyse(self.server.port, self.certs.path('ca.pem'), self.certs.path('client.pem'),
                        self.certs.path('client.key'), {'context': context(), 'payload': {'value': 7}},
                        total_timeout=0.25)
            except TransportError as exc:
                errors.append(exc.code)
        thread = threading.Thread(target=first_call)
        thread.start()
        try:
            self.assertTrue(entered.wait(2))
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
            self.assertEqual(errors, ['deadline_exceeded'])
            with self.assertRaises(TransportError) as caught:
                self.call()
            self.assertEqual(caught.exception.code, 'http_503')
            self.assertEqual(self.server.calls, 1)
        finally:
            release.set()
            thread.join(timeout=3)
        self.assertTrue(self.server.idle.wait(2))
        self.assertEqual(self.call()['result'], 14)
        self.assertEqual(self.server.calls, 2)

    def test_revocation_during_work_prevents_result_delivery(self):
        def revoke_during_work(value):
            self.authority.revoke('A', 'alice', 'synthetic', 'analysis', 'rev-1')
            return value * 2
        self.server.compute = revoke_during_work
        with self.assertRaises(TransportError) as caught:
            self.call()
        self.assertEqual(caught.exception.code, 'http_403')
        self.assertEqual(self.server.calls, 1)

    def test_request_byte_boundaries(self):
        base = json.dumps({'context': context(), 'payload': {'value': 7}}).encode()
        for size in (1024 * 1024 - 1, 1024 * 1024):
            connection = self.connection()
            try:
                connection.request('POST', '/analysis', base + b' ' * (size - len(base)),
                                   {'Content-Type': 'application/json'})
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(json.loads(response.read())['result'], 14)
            finally:
                connection.close()
        self.assertEqual(self.server.calls, 2)

    def test_untrusted_server_ca(self):
        with self.assertRaises(TransportError):
            analyse(self.server.port, self.certs.path('foreign.pem'), self.certs.path('client.pem'),
                    self.certs.path('client.key'), {'context': context(), 'payload': {'value': 7}})
        self.assertEqual(self.server.calls, 0)


if __name__ == '__main__':
    unittest.main()
