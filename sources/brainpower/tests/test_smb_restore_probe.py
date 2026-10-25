import importlib.util
from pathlib import Path
import tempfile
import unittest


class SmbRestoreProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('smb_probe', Path(__file__).resolve().parents[1] / 'artifacts/server-smb-restore-20260918.py')
        cls.probe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.probe)

    def test_mount_requires_exact_remote_source_and_safety_flags(self):
        good = dict(source=self.probe.SOURCE, fstype='cifs', options='rw,nosuid,nodev,noexec,seal,vers=3.1.1')
        self.probe.validate_mount(good, 'rw')
        for changed in (dict(source='/dev/sda'), dict(fstype='ext4'), dict(options='rw,nosuid,nodev,noexec,vers=3.1.1'), dict(options='ro,nosuid,nodev,noexec,seal,vers=3.1.1')):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                self.probe.validate_mount(dict(good, **changed), 'rw')

    def test_restore_rejects_changed_missing_extra_and_empty_tree(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'a').write_bytes(b'expected')
            expected = self.probe.manifest(root)
            self.probe.verify_tree(root, expected)
            (root/'a').write_bytes(b'wrong')
            with self.assertRaises(ValueError): self.probe.verify_tree(root, expected)
            (root/'a').write_bytes(b'expected')
            (root/'extra').write_bytes(b'extra')
            with self.assertRaises(ValueError): self.probe.verify_tree(root, expected)
            (root/'extra').unlink(); (root/'a').unlink()
            with self.assertRaises(ValueError): self.probe.verify_tree(root, expected)

    def test_restore_rejects_missing_root(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises((ValueError, FileNotFoundError)):
                self.probe.verify_tree(Path(d)/'missing', {})
