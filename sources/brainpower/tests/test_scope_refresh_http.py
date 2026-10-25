import unittest
from unittest.mock import patch

from tests import test_server


class ScopeRefreshHttpTests(unittest.TestCase):
    setUp = test_server.ServerTests.setUp
    cleanup = test_server.ServerTests.cleanup
    request = test_server.ServerTests.request
    auth = test_server.ServerTests.auth

    def test_manual_refresh_forces_read_only_scan(self):
        with patch.object(self.server.app, 'scope_context', return_value={'scope_hash': 'fixture'}) as scoped:
            status, body, _ = self.request('GET', '/api/scope?kind=project&id=test&fresh=1', headers=self.auth())
            self.assertEqual(200, status)
            self.assertEqual('fixture', body['scope_hash'])
            scoped.assert_called_once_with('project', 'test', False, True)

    def test_invalid_fresh_mode_is_rejected_without_scan(self):
        with patch.object(self.server.app, 'scope_context') as scoped:
            status, _, _ = self.request('GET', '/api/scope?kind=project&id=test&fresh=yes', headers=self.auth())
            self.assertEqual(400, status)
            scoped.assert_not_called()


if __name__ == '__main__':
    unittest.main()
