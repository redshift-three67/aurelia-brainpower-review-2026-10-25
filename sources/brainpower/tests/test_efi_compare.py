import importlib.util
from pathlib import Path
import tempfile
import unittest


class EfiCompareTests(unittest.TestCase):
    def load(self):
        path = Path(__file__).resolve().parents[1]/'artifacts/server-efi-compare-20260919.py'
        self.assertTrue(path.exists(), 'EFI comparison not implemented')
        spec = importlib.util.spec_from_file_location('efi_probe', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_missing_changed_and_extra_distinguished(self):
        m = self.load()
        self.assertEqual(m.compare({'same': 'a', 'changed': 'b', 'left': 'c'},
                                   {'same': 'a', 'changed': 'd', 'right': 'e'}),
                         {'only_primary': ['left'], 'only_secondary': ['right'], 'different': ['changed'], 'identical': False})

    def test_empty_not_success(self):
        m = self.load()
        self.assertFalse(m.compare({}, {})['identical'])

    def test_manifest_detects_byte_change(self):
        m = self.load()
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); (p/'boot.efi').write_bytes(b'abc')
            before = m.manifest(p)
            (p/'boot.efi').write_bytes(b'abd')
            self.assertEqual(m.compare(before, m.manifest(p))['different'], ['boot.efi'])
