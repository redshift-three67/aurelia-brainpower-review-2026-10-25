import unittest
from unittest.mock import patch
from pathlib import Path
from contract_tls_fixture import openssl_path


class FixturePlatformTests(unittest.TestCase):
    def test_fixed_platform_paths(self):
        for platform, expected in [('linux', '/usr/bin/openssl'),
                                   ('win32', 'C:/Program Files/Git/usr/bin/openssl.exe')]:
            with self.subTest(platform=platform), patch('contract_tls_fixture.sys.platform', platform):
                with patch.object(Path, 'is_file', return_value=True):
                    self.assertEqual(openssl_path(), Path(expected))

    def test_missing_binary_fails_without_skip_or_path_fallback(self):
        with patch.object(Path, 'is_file', return_value=False):
            with self.assertRaises(RuntimeError):
                openssl_path()

    def test_unsupported_platform_fails(self):
        with patch('contract_tls_fixture.sys.platform', 'unknown'):
            with self.assertRaises(RuntimeError):
                openssl_path()
