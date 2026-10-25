from contextlib import contextmanager
from pathlib import Path
import hashlib
import os
import sqlite3
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from governor_workbench.registry import Registry
from governor_workbench.store import Store


class RegistryMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.store = Store(self.root/'journal.sqlite')
        self.reg = Registry(self.store, [])
        self.project_root = self.root/'project'
        self.project_root.mkdir()
        self.p = self.reg.register('Example', str(self.project_root), requirements='Keep existing code')
        self.g = self.reg.create_group('Group')

    def service(self, assigned=True):
        from governor_workbench.memory_registry import RegistryMemory
        if assigned: self.reg.assign(self.p['id'], self.g['id'], 'parent')
        return RegistryMemory(self.reg, self.root/'runtime')

    def test_service_exists(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('governor_workbench.memory_registry'))

    def test_new_project_gets_one_stable_incomplete_memory(self):
        svc = self.service()
        value = svc.provision(self.p['id'])
        self.assertEqual(value['name'], 'strategy_project_1.md')
        self.assertTrue(value['created'])
        self.assertFalse(value['complete'])
        self.assertEqual(self.reg.list_projects()[0]['memory_provisioning'], 'provisioned_incomplete')
        content = Path(value['path']).read_text(encoding='utf-8')
        for text in (self.p['id'], self.g['id'], 'parent', 'Keep existing code', 'incomplete'):
            self.assertIn(text, content)
        again = svc.provision(self.p['id'])
        self.assertFalse(again['created'])
        self.assertEqual(again['sha256'], value['sha256'])
        self.assertEqual(len(list((self.project_root/'project_memories').iterdir())), 1)

    def test_existing_strategy_memory_is_preserved_byte_for_byte(self):
        folder = self.project_root/'project_memories'
        folder.mkdir()
        existing = folder/'strategy_project_original.md'
        original = b'# Existing\r\nPrivate existing bytes\r\n'
        existing.write_bytes(original)
        value = self.service().provision(self.p['id'])
        self.assertFalse(value['created'])
        self.assertEqual(value['name'], existing.name)
        self.assertEqual(value['sha256'], hashlib.sha256(original).hexdigest())
        self.assertEqual(existing.read_bytes(), original)

    def test_ambiguity_is_rejected_without_writes(self):
        folder = self.project_root/'project_memories'
        folder.mkdir()
        for name in ('strategy_project_1.md', 'strategy_project_2.md'):
            (folder/name).write_text('original', encoding='utf-8')
        with self.assertRaises(ValueError): self.service().provision(self.p['id'])
        self.assertEqual(len(list(folder.iterdir())), 2)

    def test_unassigned_and_archived_projects_are_rejected(self):
        svc = self.service(assigned=False)
        with self.assertRaises(ValueError): svc.provision(self.p['id'])
        self.reg.archive(self.p['id'])
        with self.assertRaises(ValueError): svc.provision(self.p['id'])
        self.assertFalse((self.project_root/'project_memories').exists())

    def test_symlink_escape_rejected(self):
        external = self.root/'external'
        external.mkdir()
        try: (self.project_root/'project_memories').symlink_to(external, target_is_directory=True)
        except OSError: self.skipTest('Creating symlinks requires host permission')
        with self.assertRaises(ValueError): self.service().provision(self.p['id'])
        self.assertEqual(list(external.iterdir()), [])

    def test_oversized_existing_memory_rejected(self):
        folder = self.project_root/'project_memories'
        folder.mkdir()
        (folder/'strategy_project_1.md').write_bytes(b'x'*(512*1024+1))
        with self.assertRaises(ValueError): self.service().provision(self.p['id'])

    def test_exclusive_creation_conflict_does_not_overwrite(self):
        svc = self.service()
        real_open = open
        def raced_open(path, mode='r', *args, **kwargs):
            if mode == 'xb':
                Path(path).write_bytes(b'concurrent writer')
            return real_open(path, mode, *args, **kwargs)
        with patch('builtins.open', side_effect=raced_open), self.assertRaises(ValueError):
            svc.provision(self.p['id'])
        self.assertEqual((self.project_root/'project_memories'/'strategy_project_1.md').read_bytes(), b'concurrent writer')

    def test_database_failure_removes_only_newly_created_file(self):
        svc = self.service()
        original_db = self.store.db
        @contextmanager
        def failed_db():
            with original_db() as c:
                yield c
                raise sqlite3.OperationalError('simulated commit failure')
        with patch.object(self.store, 'db', failed_db), self.assertRaises(sqlite3.OperationalError):
            svc.provision(self.p['id'])
        self.assertFalse((self.project_root/'project_memories'/'strategy_project_1.md').exists())

    @unittest.skipUnless(os.name == 'nt', 'Windows junction test')
    def test_windows_junction_escape_rejected(self):
        external = self.root/'external'
        external.mkdir()
        link = self.project_root/'project_memories'
        subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(link), str(external)],
                       check=True, capture_output=True)
        with self.assertRaises(ValueError): self.service().provision(self.p['id'])
        self.assertEqual(list(external.iterdir()), [])

    def test_compensation_preserves_concurrent_writer(self):
        svc = self.service()
        original_db = self.store.db
        target = self.project_root/'project_memories'/'strategy_project_1.md'
        @contextmanager
        def failed_db():
            with original_db() as c:
                yield c
                target.write_bytes(b'concurrent edit')
                raise sqlite3.OperationalError('simulated commit failure')
        with patch.object(self.store, 'db', failed_db), self.assertRaises(sqlite3.OperationalError):
            svc.provision(self.p['id'])
        self.assertEqual(target.read_bytes(), b'concurrent edit')

    def test_stable_index_includes_archived_registry_rows(self):
        self.reg.archive(self.p['id'])
        root2 = self.root/'second'
        root2.mkdir()
        p2 = self.reg.register('Second', str(root2))
        self.reg.assign(p2['id'], self.g['id'])
        value = self.service(assigned=False).provision(p2['id'])
        self.assertEqual(value['name'], 'strategy_project_2.md')

    def test_root_canonical_identity_drift_rejected(self):
        svc = self.service()
        with self.store.db() as c:
            c.execute('UPDATE reg_projects SET path=? WHERE id=?',
                      (str(self.project_root/'..'/'project'), self.p['id']))
        with self.assertRaises(ValueError): svc.provision(self.p['id'])
        self.assertEqual(list(self.project_root.iterdir()), [])


if __name__ == '__main__': unittest.main()
