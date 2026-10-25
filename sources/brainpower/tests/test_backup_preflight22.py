import importlib.util
from pathlib import Path
import unittest


class PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('preflight22', Path(__file__).resolve().parents[1] / 'artifacts/server-backup-preflight22.py')
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def test_missing_file_does_not_skip_following_checks(self):
        report = {}
        def missing():
            raise FileNotFoundError('private-path')
        self.m.observe(report, 'repository', missing)
        self.m.observe(report, 'next', lambda: {'checked': True})
        self.assertEqual(report['repository'], {'status': 'missing'})
        self.assertTrue(report['next']['checked'])

    def test_local_root_mount_is_not_accepted_as_smb(self):
        data = {'filesystems': [{'target': '/', 'fstype': 'ext4', 'source': '/dev/mapper/private', 'options': 'rw,password=SECRET'}]}
        result = self.m.mount_summary(data, '/mnt/aurelia-g2')
        self.assertFalse(result['expected_smb_mount'])
        self.assertNotIn('SECRET', str(result))
        self.assertNotIn('/dev/mapper/private', str(result))

    def test_smb_identity_requires_exact_target_and_source(self):
        item = dict(target='/mnt/aurelia-g2', fstype='cifs', source=self.m.SHARE, options='rw,seal,vers=3.1.1')
        self.assertTrue(self.m.mount_summary({'filesystems': [item]}, '/mnt/aurelia-g2')['expected_smb_mount'])
        item['source'] = '//other/share'
        self.assertFalse(self.m.mount_summary({'filesystems': [item]}, '/mnt/aurelia-g2')['expected_smb_mount'])
