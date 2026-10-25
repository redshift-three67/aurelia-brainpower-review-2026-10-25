import tempfile
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from governor_workbench.store import Store
from governor_workbench.execution_workspace import WorkspaceStager, _sha
from governor_workbench.pilot_apply import PilotApply


class PilotApplyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name).resolve()
        self.root = base/'project'; self.root.mkdir()
        (self.root/'a.py').write_bytes(b'old WIP\r\n')
        (self.root/'other.txt').write_bytes(b'unrelated')
        self.store = Store(base/'data'/'journal.db')
        self.stager = WorkspaceStager(base/'data')
        self.stage = self.stager.stage(str(self.root), ['a.py', 'new.py'],
            [{'path':'a.py','content':'new\n'}, {'path':'new.py','content':'created\n'}],
            {'a.py':_sha(b'old WIP\r\n'), 'new.py':None})
        parent = self.store.create_job('scope_patch', 'pilot', {})
        self.store.update_job(parent['id'], status='completed', result={'stage':self.stage,'scope_hash':'scope'})
        self.test = self.store.create_job('stage_test','pilot',{'stage_job_id':parent['id']})
        self.result = dict(stage_job_id=parent['id'],stage_id=self.stage['id'],manifest_hash=self.stage['manifest_hash'],
            scope_hash='scope',verified=True,success=True,completion_verified=True,sources_verified=True)
        from governor_workbench.staged_tests import adapter_identity
        identity=adapter_identity()
        self.result.update(adapter_verified=True,adapter_before=identity,adapter_after=identity)
        self.store.update_job(self.test['id'],status='completed',result=self.result)
        self.pilot = PilotApply(self.store,self.stager,allowed_roots=[str(self.root)])

    def prepare(self):
        return self.pilot.prepare(self.stage['id'],self.stage['manifest_hash'],self.test['id'],'scope')

    def apply(self, proposal):
        return self.pilot.apply(proposal['id'],self.stage['manifest_hash'],'scope')

    def test_apply_and_exact_rollback_and_no_replay(self):
        p = self.prepare(); tx = self.apply(p)
        self.assertEqual((self.root/'a.py').read_bytes(),b'new\n')
        self.assertEqual(self.apply(p)['id'],tx['id'])
        self.pilot.rollback(tx['id'])
        self.assertEqual((self.root/'a.py').read_bytes(),b'old WIP\r\n')
        self.assertFalse((self.root/'new.py').exists())
        self.assertEqual((self.root/'other.txt').read_bytes(),b'unrelated')
        with self.assertRaises(ValueError): self.apply(p)

    def test_unverified_or_wrong_scope_or_default_root(self):
        with self.assertRaises(ValueError): self.pilot.prepare(self.stage['id'],self.stage['manifest_hash'],self.test['id'],'wrong')
        with self.assertRaises(ValueError): PilotApply(self.store,self.stager).prepare(self.stage['id'],self.stage['manifest_hash'],self.test['id'],'scope')
        self.store.update_job(self.test['id'],result={**self.result,'verified':False})
        with self.assertRaises(ValueError): self.prepare()

    def test_source_drift_and_changed_evidence_rejected(self):
        p = self.prepare()
        self.store.update_job(self.test['id'],result={**self.result,'success':False})
        with self.assertRaises(ValueError): self.apply(p)
        self.store.update_job(self.test['id'],result=self.result)
        (self.root/'a.py').write_bytes(b'changed externally')
        with self.assertRaises(ValueError): self.apply(p)

    def test_rollback_prevalidates_all_paths(self):
        tx = self.apply(self.prepare())
        (self.root/'new.py').write_bytes(b'external')
        with self.assertRaises(ValueError): self.pilot.rollback(tx['id'])
        self.assertEqual((self.root/'a.py').read_bytes(),b'new\n')

    def test_failure_restores_written_files(self):
        p = self.prepare(); original = self.pilot._replace; count = 0
        def fail(root, path, data, expected):
            nonlocal count
            count += 1
            if count == 2: raise OSError('injected')
            return original(root,path,data,expected)
        with patch.object(self.pilot,'_replace',side_effect=fail):
            with self.assertRaises(ValueError): self.apply(p)
        self.assertEqual((self.root/'a.py').read_bytes(),b'old WIP\r\n')
        self.assertFalse((self.root/'new.py').exists())

    def test_crash_is_never_replayed_and_explicit_recovery(self):
        p = self.prepare(); original = self.pilot._replace
        def crash(root,path,data,expected):
            original(root,path,data,expected)
            raise KeyboardInterrupt()
        with patch.object(self.pilot,'_replace',side_effect=crash):
            with self.assertRaises(KeyboardInterrupt): self.apply(p)
        other = PilotApply(self.store,self.stager,allowed_roots=[str(self.root)])
        with self.assertRaises(ValueError): other.apply(p['id'],self.stage['manifest_hash'],'scope')
        other.rollback(other.transactions()[0]['id'])
        self.assertEqual((self.root/'a.py').read_bytes(),b'old WIP\r\n')

    def test_second_proposal_cannot_replay_same_stage(self):
        first = self.prepare(); second = self.prepare()
        tx = self.apply(first)
        other = PilotApply(self.store,self.stager,allowed_roots=[str(self.root)])
        self.assertEqual(other.apply(second['id'],self.stage['manifest_hash'],'scope')['id'],tx['id'])
        self.assertEqual(len(other.transactions()),1)

    def test_failure_with_external_drift_preserves_external_bytes(self):
        p = self.prepare(); original = self.pilot._replace; count = 0
        def fail(root,path,data,expected):
            nonlocal count
            count += 1
            if count == 2:
                (root/'a.py').write_bytes(b'external during apply')
                raise OSError('injected')
            return original(root,path,data,expected)
        with patch.object(self.pilot,'_replace',side_effect=fail):
            with self.assertRaises(ValueError): self.apply(p)
        self.assertEqual((self.root/'a.py').read_bytes(),b'external during apply')
        self.assertEqual(self.pilot.transactions()[0]['status'],'recovery_needed')

    def test_hardlink_after_prepare_is_rejected(self):
        p = self.prepare()
        try: os.link(self.root/'a.py',self.root/'alias.py')
        except OSError: self.skipTest('Hardlinks unavailable')
        with self.assertRaises(ValueError): self.apply(p)
        self.assertEqual((self.root/'a.py').read_bytes(),b'old WIP\r\n')

    def test_corrupt_backup_blocks_all_rollback_writes(self):
        tx = self.apply(self.prepare())
        (self.pilot.base/tx['id']/tx['files'][0]['backup']).write_bytes(b'tamper')
        with self.assertRaises(ValueError): self.pilot.rollback(tx['id'])
        self.assertEqual((self.root/'a.py').read_bytes(),b'new\n')
        self.assertEqual((self.root/'new.py').read_bytes(),b'created\n')
