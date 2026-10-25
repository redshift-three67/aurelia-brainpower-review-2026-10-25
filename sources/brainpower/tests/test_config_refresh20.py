import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


class ConfigRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('refresh', Path(__file__).resolve().parents[1] / 'artifacts/server-config-backup-20260920.py')
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def test_unmounted_primary_does_not_require_mount(self):
        with patch.object(self.m.os.path, 'ismount', return_value=False):
            self.assertEqual(self.m.primary_state({'mount_guard': lambda *a: self.fail('unexpected mount lookup')}), 'unmounted')

    def test_existing_unsafe_mount_stops(self):
        def fail(*args):
            raise ValueError('wrong source or protection')
        with patch.object(self.m.os.path, 'ismount', return_value=True):
            with self.assertRaises(ValueError):
                self.m.primary_state({'mount_guard': fail})

    def test_prior_snapshot_identity_required(self):
        self.m.verify_prior_snapshot([{'id': self.m.PRIOR_SNAPSHOT}])
        for value in ([], [{'id': 'a' * 64}], {}, [{'id': self.m.PRIOR_SNAPSHOT}, {'id': self.m.PRIOR_SNAPSHOT}]):
            with self.assertRaises(ValueError):
                self.m.verify_prior_snapshot(value)

    def test_read_only_primary_is_accepted(self):
        seen = []
        with patch.object(self.m.os.path, 'ismount', return_value=True):
            self.assertEqual(self.m.primary_state({'mount_guard': lambda *a: seen.append(a)}), 'read_only_verified')
        self.assertEqual(seen, [('/mnt/aurelia-g2', 'ro')])
