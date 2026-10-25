"""Synthetic validity/policy/log boundaries over actual local TLS."""
import contextlib
import http.client
import io
import json
import ssl
import unittest

from contract_tls_fixture import Certificates
from test_contract_lab import approved, context
from contract_lab.authority import TestAuthority
from contract_lab.validation import ContractError
from contract_lab.transport import LabServer, TransportError, analyse, client_context


class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certs = Certificates()
        try:
            for role in ('client', 'server'):
                cls.certs.issue_window('expired-' + role, role, '20000101000000Z', '20010101000000Z')
                cls.certs.issue_window('future-' + role, role, '20990101000000Z', '21000101000000Z')
        except BaseException:
            cls.certs.close()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.certs.close()
        if cls.certs.root.exists():
            raise AssertionError('Certificate fixture not removed')

    def setUp(self):
        self.now = 100
        self.allowed = {self.certs.fingerprint('client')}
        self.authority = TestAuthority([('A', 'alice', 'synthetic', 'analysis', 'rev-1')])
        self.server = self.new_server()

    def new_server(self, name='server'):
        server = LabServer(self.certs.path(name + '.pem'), self.certs.path('server.key'),
                           self.certs.path('ca.pem'), self.allowed, approved(), self.authority,
                           now=lambda: self.now)
        server.start()
        self.addCleanup(server.close)
        return server

    def load(self, expires=130, revision=1):
        self.server.replace_policy(self.allowed, valid_until=expires, revision=revision)

    def call(self, server=None, cert='client'):
        return analyse((server or self.server).port, self.certs.path('ca.pem'),
                       self.certs.path(cert + '.pem'), self.certs.path('client.key'),
                       {'context': context(issued_at=self.now, expires_at=self.now + 30),
                        'payload': {'value': 7}})

    def test_missing_policy_fails_closed(self):
        with self.assertRaises(TransportError) as caught:
            self.call()
        self.assertEqual(caught.exception.code, 'http_503')
        self.assertEqual(self.server.calls, 0)

    def test_invalid_policy_types_and_bounds(self):
        for expiry, revision in ((True, 1), (100, 1), (161, 1), (130, True),
                                 (130, 0), (130.0, 1), (130, '1')):
            with self.subTest(expiry=expiry, revision=revision):
                with self.assertRaises(ContractError):
                    self.load(expiry, revision)
                with self.assertRaises(TransportError) as caught:
                    self.call()
                self.assertEqual(caught.exception.code, 'http_503')
        self.assertEqual(self.server.calls, 0)

    def test_policy_copies_caller_collection(self):
        self.load()
        self.allowed.clear()
        self.assertEqual(self.call()['result'], 14)

    def test_exact_policy_expiry_and_refresh(self):
        self.load()
        self.now = 129
        self.assertEqual(self.call()['result'], 14)
        self.now = 130
        with self.assertRaises(TransportError) as caught:
            self.call()
        self.assertEqual(caught.exception.code, 'http_503')
        self.assertEqual(self.server.calls, 1)
        self.load(expires=160, revision=2)
        self.call()
        self.assertEqual(self.server.calls, 2)

    def test_invalid_reload_removes_authority(self):
        self.load()
        with self.assertRaises(ContractError):
            self.server.replace_policy({'not-a-fingerprint'}, valid_until=130, revision=2)
        with self.assertRaises(TransportError):
            self.call()
        self.assertEqual(self.server.calls, 0)

    def test_old_revision_cannot_revive_policy(self):
        self.load(revision=2)
        with self.assertRaises(ContractError):
            self.load(revision=1)
        with self.assertRaises(TransportError):
            self.call()
        self.assertEqual(self.server.calls, 0)

    def test_clock_rollback_fails_closed(self):
        self.load()
        self.now = 99
        with self.assertRaises(TransportError):
            self.call()
        self.assertEqual(self.server.calls, 0)

    def test_policy_expires_during_work(self):
        self.load()
        def compute(value):
            self.now = 130
            return value * 2
        self.server.compute = compute
        with self.assertRaises(TransportError) as caught:
            self.call()
        self.assertEqual(caught.exception.code, 'http_503')
        self.assertEqual(self.server.calls, 1)

    def test_stale_policy_cannot_be_revived_by_allow(self):
        self.load()
        self.now = 130
        with self.assertRaises(ContractError):
            self.server.allow(self.certs.fingerprint('rotated'))
        with self.assertRaises(TransportError):
            self.call()

    def test_expired_client_certificate(self):
        self.allowed.add(self.certs.fingerprint('expired-client'))
        self.load()
        with self.assertRaises(TransportError):
            self.call(cert='expired-client')
        self.assertEqual(self.server.calls, 0)

    def test_future_client_certificate(self):
        self.allowed.add(self.certs.fingerprint('future-client'))
        self.load()
        with self.assertRaises(TransportError):
            self.call(cert='future-client')
        self.assertEqual(self.server.calls, 0)

    def test_expired_server_certificate(self):
        server = self.new_server('expired-server')
        with self.assertRaises(TransportError):
            self.call(server)
        self.assertEqual(server.calls, 0)

    def test_future_server_certificate(self):
        server = self.new_server('future-server')
        with self.assertRaises(TransportError):
            self.call(server)
        self.assertEqual(server.calls, 0)

    def test_sensitive_markers_not_in_responses_or_console(self):
        self.load()
        marker = 'SYNTHETIC_SECRET_MARKER'
        output, errors = io.StringIO(), io.StringIO()
        cases = [('POST', '/analysis', b'{"' + marker.encode() + b'":true}', 400),
                 ('POST', '/' + marker, b'{}', 404),
                 (marker, '/analysis', b'{}', 501)]
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            for method, path, body, expected in cases:
                connection = http.client.HTTPSConnection('localhost', self.server.port,
                    context=client_context(self.certs.path('ca.pem'), self.certs.path('client.pem'),
                                           self.certs.path('client.key')), timeout=3)
                try:
                    connection.request(method, path, body, {'Content-Type': 'application/json',
                                                           'X-Test-Secret': marker})
                    response = connection.getresponse()
                    self.assertEqual(response.status, expected)
                    self.assertNotIn(marker.encode(), response.read())
                finally:
                    connection.close()
        self.assertNotIn(marker, output.getvalue() + errors.getvalue())
        self.assertEqual(self.server.calls, 0)


if __name__ == '__main__':
    unittest.main()
