import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


def sha(data): return hashlib.sha256(data).hexdigest()


class WorkspaceStagerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.project = self.root/'project'
        self.project.mkdir()
        self.original = self.project/'app.py'
        self.original.write_bytes(b'# user WIP\n')

    def stager(self):
        from governor_workbench.execution_workspace import WorkspaceStager
        return WorkspaceStager(self.root/'runtime')

    def stage(self, **kwargs):
        args = dict(project_root=self.project, allowed_paths=['app.py'],
                    patches=[dict(path='app.py',content='# proposed\n')],
                    expected_hashes={'app.py':sha(self.original.read_bytes())})
        args.update(kwargs)
        return self.stager().stage(**args)

    def test_module_exists(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('governor_workbench.execution_workspace'))

    def test_wip_preserved_and_staged_proposal_is_inspectable(self):
        value = self.stage()
        self.assertEqual(self.original.read_bytes(), b'# user WIP\n')
        self.assertEqual((Path(value['path'])/'files'/'app.py').read_bytes(), b'# proposed\n')
        self.assertIn('-# user WIP', value['manifest']['files'][0]['diff'])
        self.assertFalse(value['manifest']['execution_enabled'])
        checked = self.stager().verify_source(value['id'], value['manifest_hash'])
        self.assertTrue(checked['verified'])

    def test_new_file_requires_explicit_absence(self):
        value = self.stage(allowed_paths=['new.md'], patches=[dict(path='new.md',content='new')], expected_hashes={'new.md':None})
        self.assertFalse((self.project/'new.md').exists())
        (self.project/'new.md').write_text('concurrent creation',encoding='utf-8')
        with self.assertRaises(ValueError): self.stager().verify_source(value['id'],value['manifest_hash'])

    def test_applied_observation_checks_unchanged_files_and_keeps_source_check_strict(self):
        (self.project/'keep.md').write_bytes(b'unchanged')
        value=self.stage(allowed_paths=['app.py','keep.md'],expected_hashes={
            'app.py':sha(self.original.read_bytes()),'keep.md':sha(b'unchanged')})
        with self.assertRaises(ValueError): self.stager().verify_applied(value['id'],value['manifest_hash'])
        self.original.write_bytes(b'# proposed\n')
        self.assertTrue(self.stager().verify_applied(value['id'],value['manifest_hash'])['verified'])
        with self.assertRaises(ValueError): self.stager().verify_source(value['id'],value['manifest_hash'])
        (self.project/'keep.md').write_bytes(b'external edit')
        with self.assertRaises(ValueError): self.stager().verify_applied(value['id'],value['manifest_hash'])

    def test_only_explicit_allowed_files_are_copied(self):
        (self.project/'keep.md').write_bytes(b'allowed')
        (self.project/'private.md').write_bytes(b'not in scope')
        value=self.stage(allowed_paths=['app.py','keep.md'],expected_hashes={
            'app.py':sha(self.original.read_bytes()),'keep.md':sha(b'allowed')})
        files=Path(value['path'])/'files'
        self.assertEqual((files/'keep.md').read_bytes(),b'allowed')
        self.assertFalse((files/'private.md').exists())

    def test_missing_and_wrong_hashes_are_rejected(self):
        for hashes in ({}, {'app.py':None}, {'app.py':'a'*64}):
            with self.assertRaises(ValueError): self.stage(expected_hashes=hashes)

    def test_unauthorized_duplicate_and_traversing_paths_rejected(self):
        for patches in ([dict(path='../outside',content='bad')],
                        [dict(path='other.py',content='bad')],
                        [dict(path='app.py',content='one'),dict(path='app.py',content='two')]):
            with self.assertRaises(ValueError): self.stage(patches=patches)
        with self.assertRaises(ValueError): self.stage(allowed_paths=['.env'])

    def test_source_change_and_deletion_are_drift(self):
        value = self.stage()
        self.original.write_bytes(b'# changed again\n')
        with self.assertRaises(ValueError): self.stager().verify_source(value['id'],value['manifest_hash'])
        self.original.unlink()
        with self.assertRaises(ValueError): self.stager().verify_source(value['id'],value['manifest_hash'])

    def test_staged_and_manifest_tampering_rejected(self):
        value = self.stage()
        (Path(value['path'])/'files'/'app.py').write_text('tampered',encoding='utf-8')
        with self.assertRaises(ValueError): self.stager().verify_source(value['id'],value['manifest_hash'])
        second = self.stage()
        Path(second['manifest_path']).write_text('{}',encoding='utf-8')
        with self.assertRaises(ValueError): self.stager().verify_source(second['id'],second['manifest_hash'])

    def test_unexpected_staging_directory_rejected(self):
        value=self.stage()
        (Path(value['path'])/'unexpected').mkdir()
        with self.assertRaises(ValueError): self.stager().verify_source(value['id'],value['manifest_hash'])

    def test_diff_marks_missing_final_newlines(self):
        self.original.write_bytes(b'old')
        value=self.stage(patches=[dict(path='app.py',content='new')])
        diff=value['manifest']['files'][0]['diff']
        self.assertIn('-old\n\\ No newline at end of file\n',diff)
        self.assertIn('+new\n\\ No newline at end of file\n',diff)

    def test_file_byte_and_total_patch_limits(self):
        with self.assertRaises(ValueError): self.stage(patches=[dict(path='app.py',content='ü'*(128*1024+1))])
        paths=[f'file{i}.md' for i in range(5)]
        with self.assertRaises(ValueError): self.stage(allowed_paths=paths,
            patches=[dict(path=p,content='x'*(256*1024)) for p in paths],expected_hashes={p:None for p in paths})

    def test_unknown_ids_missing_seal_and_root_alias_rejected(self):
        for key in ('../other', {}, 'a'*32):
            with self.assertRaises(ValueError): self.stager().verify_source(key,'a'*64)
        with self.assertRaises(ValueError): self.stage(project_root=self.project/'..'/'project')

    def test_hardlinked_source_rejected(self):
        os.link(self.original,self.project/'alias.py')
        with self.assertRaises(ValueError): self.stage()

    @unittest.skipUnless(os.name=='nt','Windows junction check')
    def test_junction_source_escape_rejected(self):
        external=self.root/'external'
        external.mkdir()
        (external/'note.md').write_text('private',encoding='utf-8')
        subprocess.run(['cmd.exe','/d','/c','mklink','/J',str(self.project/'linked'),str(external)],check=True,capture_output=True)
        with self.assertRaises(ValueError): self.stage(allowed_paths=['linked/note.md'],
            patches=[dict(path='linked/note.md',content='bad')],expected_hashes={'linked/note.md':sha(b'private')})

    @unittest.skipUnless(os.name=='nt','Windows junction check')
    def test_replaced_original_root_is_rejected_during_verification(self):
        value=self.stage()
        moved=self.root/'moved'
        self.project.rename(moved)
        subprocess.run(['cmd.exe','/d','/c','mklink','/J',str(self.project),str(moved)],check=True,capture_output=True)
        with self.assertRaises(ValueError): self.stager().verify_source(value['id'],value['manifest_hash'])


if __name__=='__main__': unittest.main()
