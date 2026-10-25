from pathlib import Path
import os
import subprocess
import tempfile
import unittest

from governor_workbench.registry import Registry
from governor_workbench.store import Store


class VaultTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.vault_root = self.root/'vault'
        self.vault_root.mkdir()
        self.store = Store(self.root/'journal.sqlite')
        self.reg = Registry(self.store, [])
        self.g = self.reg.create_group('First')
        self.other = self.reg.create_group('Other')

    def service(self, configured=True):
        from governor_workbench.vault import Vault
        return Vault(self.reg, self.root/'runtime', vault_root=self.vault_root if configured else None)

    def note(self, name, content='Source text'):
        path = self.vault_root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return str(path)

    def test_service_exists(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('governor_workbench.vault'))

    def test_scope_and_permission_are_explicit_persistent_and_separate(self):
        svc = self.service()
        path = self.note('system_prompts.md')
        mapping = svc.map_source('group', self.g['id'], path)
        self.assertEqual(svc.list_sources('group', self.other['id']), [])
        with self.assertRaises(ValueError): svc.context('group', self.g['id'])
        local = svc.context('group', self.g['id'], require_egress=False)
        self.assertEqual(local['sources'][0]['content'], 'Source text')
        self.assertEqual(local['sources'][0]['authority'], 'reference_data_only')
        self.assertEqual(self.service().list_sources('group', self.g['id']), [mapping])
        self.assertEqual(svc.context('group', self.other['id'])['sources'], [])

    def test_file_changes_change_hash(self):
        svc = self.service()
        path = self.note('one.md')
        svc.map_source('group', self.g['id'], path, model_egress=True)
        before = svc.context('group', self.g['id'])
        Path(path).write_text('Changed', encoding='utf-8')
        after = svc.context('group', self.g['id'])
        self.assertNotEqual(before['sources'][0]['sha256'], after['sources'][0]['sha256'])

    def test_path_escape_wrong_extension_missing_and_alias_rejected(self):
        svc = self.service()
        outside = self.root/'outside.md'
        outside.write_text('private', encoding='utf-8')
        note = self.note('one.md')
        svc.map_source('group', self.g['id'], note)
        for path in (str(outside), str(self.vault_root/'..'/'outside.md'), 'one.md', self.note('bad.txt'), str(self.vault_root/'missing.md'), str(self.vault_root/'sub'/'..'/'one.md')):
            with self.subTest(path=path), self.assertRaises(ValueError):
                svc.map_source('group', self.g['id'], path)

    def test_same_filename_in_distinct_folders_is_not_confused(self):
        svc = self.service()
        svc.map_source('group', self.g['id'], self.note('one/state.md', 'First'), True)
        svc.map_source('group', self.g['id'], self.note('two/state.md', 'Second'), True)
        sources = svc.context('group', self.g['id'])['sources']
        self.assertEqual({s['content'] for s in sources}, {'First','Second'})
        self.assertEqual(len({s['id'] for s in sources}), 2)

    def test_limits_and_truncation(self):
        svc = self.service()
        for i in range(10):
            svc.map_source('group', self.g['id'], self.note(f'{i}.md', 'ü'*40000), True)
        context = svc.context('group', self.g['id'])
        self.assertTrue(context['truncated'])
        self.assertLessEqual(sum(len(s['content'].encode('utf-8')) for s in context['sources']), 65536)
        with self.assertRaises(ValueError): svc.map_source('group', self.g['id'], self.note('extra.md'))
        with self.assertRaises(ValueError):
            svc.map_source('group', self.other['id'], self.note('huge.md', 'x'*(512*1024+1)))

    def test_root_and_scope_and_permission_validation(self):
        path = self.note('one.md')
        with self.assertRaises(ValueError): self.service(False).map_source('group', self.g['id'], path)
        svc = self.service()
        for kind, key, egress in (('global',self.g['id'],False),('group',{},False),('group','missing',False),('group',self.g['id'],'yes')):
            with self.assertRaises(ValueError): svc.map_source(kind,key,path,egress)
        project_root = self.root/'project'
        project_root.mkdir()
        p = self.reg.register('Project', str(project_root))
        svc.map_source('project',p['id'],path,True)
        self.reg.archive(p['id'])
        with self.assertRaises(ValueError): svc.context('project',p['id'])

    @unittest.skipUnless(os.name == 'nt', 'Windows junction check')
    def test_mapped_directory_replaced_by_junction_is_rejected(self):
        svc = self.service()
        path = self.note('mapped/state.md')
        svc.map_source('group', self.g['id'], path, True)
        source_folder = self.vault_root/'mapped'
        source_folder.rename(self.vault_root/'old')
        outside = self.root/'outside'
        outside.mkdir()
        (outside/'state.md').write_text('must not be read', encoding='utf-8')
        subprocess.run(['cmd.exe','/d','/c','mklink','/J',str(source_folder),str(outside)],
                       check=True,capture_output=True)
        with self.assertRaises(ValueError): svc.context('group', self.g['id'])


if __name__ == '__main__': unittest.main()
