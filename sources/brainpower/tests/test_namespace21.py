import importlib.util
from pathlib import Path
import unittest


class NamespaceProbeTests(unittest.TestCase):
    def test_only_inert_command_and_run_mount_differ(self):
        path = Path(__file__).resolve().parents[1] / 'artifacts/server-namespace21.py'
        spec = importlib.util.spec_from_file_location('namespace21', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original, candidate = (module.arguments(x) for x in ('original', 'empty_run'))
        for args in (original, candidate):
            self.assertEqual(args[-1], '/usr/bin/true')
            for protection in ('PrivateNetwork=yes', 'User=postgres', 'ProtectSystem=strict',
                               'NoNewPrivileges=yes', 'CapabilityBoundingSet='):
                self.assertIn(protection, args)
        old = next(x for x in original if x.startswith('InaccessiblePaths='))
        new = next(x for x in candidate if x.startswith('InaccessiblePaths='))
        self.assertEqual(old.replace(' /run ', ' '), new)
        self.assertIn('TemporaryFileSystem=/run:ro', candidate)
        with self.assertRaises(ValueError):
            module.arguments('other')
