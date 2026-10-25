import importlib.util
from pathlib import Path
import tempfile
import unittest


class ConfigScopeTests(unittest.TestCase):
    def load(self):
        path = Path(__file__).resolve().parents[1]/'artifacts/server-config-backup-20260918.py'
        self.assertTrue(path.exists(), 'Configuration backup implementation missing')
        spec = importlib.util.spec_from_file_location('config_backup', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_required_missing_blocks(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                module.select_paths(Path(tmp), ['etc/ssh'], [])

    def test_optional_absence_explicit(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'etc').mkdir()
            (root/'etc/fstab').write_text('fixture')
            self.assertEqual(module.select_paths(root, ['etc/fstab'], ['etc/wireguard']),
                             (['etc/fstab'], ['etc/wireguard']))

    def test_absolute_and_parent_paths_rejected(self):
        module = self.load()
        for path in ['/etc/shadow', '../secret', 'etc/../../secret']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                module.select_paths(Path('.'), [path], [])
