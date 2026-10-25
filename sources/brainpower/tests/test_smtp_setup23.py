import importlib.util
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import MagicMock, patch


class SMTPSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('smtp_setup23', Path(__file__).resolve().parents[1]/'artifacts/server-smtp-setup23.py')
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def client(self):
        c = MagicMock()
        c.__enter__.return_value = c
        c.sock.getpeername.return_value = ('185.248.141.144', 587)
        c.ehlo.return_value = (250, b'ok')
        c.has_extn.return_value = True
        return c

    def test_tls_failure_never_authenticates(self):
        c = self.client()
        c.starttls.side_effect = ssl.SSLError('test failure')
        with patch.object(self.m.smtplib, 'SMTP', return_value=c):
            with self.assertRaises(ssl.SSLError): self.m.authenticate('synthetic')
        c.login.assert_not_called()

    def test_wrong_server_never_authenticates(self):
        c = self.client()
        c.sock.getpeername.return_value = ('192.0.2.1', 587)
        with patch.object(self.m.smtplib, 'SMTP', return_value=c):
            with self.assertRaises(ValueError): self.m.authenticate('synthetic')
        c.login.assert_not_called()

    def test_verified_tls_precedes_one_login_no_message(self):
        c = self.client()
        with patch.object(self.m.smtplib, 'SMTP', return_value=c): self.m.authenticate('synthetic')
        names = [v[0] for v in c.mock_calls]
        self.assertLess(names.index('starttls'), names.index('login'))
        ctx = c.starttls.call_args.kwargs['context']
        self.assertTrue(ctx.check_hostname)
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        c.login.assert_called_once_with(self.m.USER, 'synthetic')
        c.sendmail.assert_not_called()
        c.send_message.assert_not_called()

    def test_exclusive_secret_write_preserves_existing(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root)/'secret'
            self.m.write_exclusive(path, b'first')
            with self.assertRaises(FileExistsError): self.m.write_exclusive(path, b'second')
            self.assertEqual(path.read_bytes(), b'first')

    def test_mismatch_or_empty_password_rejected(self):
        for a, b in [('', ''), ('a', 'b'), ('x\ny', 'x\ny')]:
            with self.assertRaises(ValueError): self.m.validate_password(a, b)
