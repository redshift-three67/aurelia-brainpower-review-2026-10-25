import unittest
from unittest.mock import patch

from tests import test_pilot_actions


class PilotVerificationTests(unittest.TestCase):
    setUp = test_pilot_actions.PilotActionsTests.setUp
    prepare = test_pilot_actions.PilotActionsTests.prepare
    execute = test_pilot_actions.PilotActionsTests.execute
    def verify(self, tx, cancel=None):
        from governor_workbench.pilot_verification import verify
        return verify(self.app, tx['id'], cancel)

    def test_post_apply_matches_even_when_current_scope_changes(self):
        tx=self.execute(self.prepare())
        self.context['scope_hash']='b'*64
        report=self.verify(tx)
        self.assertTrue(report['applied_files_verified'])
        self.assertTrue(report['evidence_usable'])
        self.assertFalse(report['context_matches_plan'])
        self.assertFalse(report['step_completion_granted'])
        self.assertFalse(report['target_tests_executed'])
        self.assertEqual(tx['id'],report['transaction_id'])
        self.assertEqual('b'*64,report['observed_scope_hash'])

    def test_post_apply_detects_drift_without_writing(self):
        tx=self.execute(self.prepare())
        (self.root/'main.py').write_bytes(b'external edit')
        report=self.verify(tx)
        self.assertFalse(report['evidence_usable'])
        self.assertEqual('blocked',report['checks'][-1]['status'])
        self.assertEqual(b'external edit',(self.root/'main.py').read_bytes())

    def test_post_apply_rejects_rollback(self):
        from governor_workbench import pilot_actions
        tx=self.execute(self.prepare())
        pilot_actions.rollback(self.app,tx['id'],None)
        self.assertFalse(self.verify(tx)['evidence_usable'])

    def test_post_apply_rejects_new_test_and_new_selection(self):
        tx=self.execute(self.prepare())
        newer=self.store.create_job('stage_test',None,{'stage_job_id':self.source['id']})
        self.store.update_job(newer['id'],status='failed')
        self.assertFalse(self.verify(tx)['evidence_usable'])
        with self.store.db() as db:
            db.execute('DELETE FROM jobs WHERE id=?',(newer['id'],))
        self.book.approve(self.candidate['id'],'a'*64,self.context,['fix'])
        self.assertFalse(self.verify(tx)['evidence_usable'])

    def test_post_apply_rejects_manifest_drift(self):
        tx=self.execute(self.prepare())
        from governor_workbench.execution_workspace import WorkspaceStager
        manifest=WorkspaceStager(self.app.config['data_dir']).base/tx['stage_id']/'manifest.json'
        manifest.write_text('{}')
        self.assertFalse(self.verify(tx)['evidence_usable'])

    def test_post_apply_cancellation_propagates(self):
        import threading
        from governor_workbench.jobs import JobCancelled
        tx=self.execute(self.prepare()); event=threading.Event(); event.set()
        with self.assertRaises(JobCancelled): self.verify(tx,event)

    def test_post_apply_missing_transaction_is_blocked(self):
        self.assertFalse(self.verify({'id':'a'*32})['evidence_usable'])

    def test_post_apply_context_failure_never_claims_success(self):
        tx=self.execute(self.prepare())
        with patch.object(self.app,'scope_context',side_effect=ValueError('Kontext fehlt')):
            self.assertFalse(self.verify(tx)['evidence_usable'])

    def test_post_apply_blocks_new_revision_and_new_patch(self):
        tx=self.execute(self.prepare())
        newer=self.store.create_job('scope_patch',None,self.source['request'])
        self.assertFalse(self.verify(tx)['evidence_usable'])
        with self.store.db() as db:
            db.execute('DELETE FROM jobs WHERE id=?',(newer['id'],))
        self.book.save_candidate(self.context,dict(summary='New',steps=[self.step]),self.review,'e'*32)
        self.assertFalse(self.verify(tx)['evidence_usable'])

    def test_post_apply_blocks_revoked_allowlist_and_adapter(self):
        tx=self.execute(self.prepare())
        with patch('governor_workbench.staged_tests.adapter_identity',return_value={'changed':True}):
            self.assertFalse(self.verify(tx)['evidence_usable'])
        self.app.config['staging_pilot_roots']=[]
        self.assertFalse(self.verify(tx)['evidence_usable'])

    def test_post_apply_inspects_stage_and_missing_target(self):
        tx=self.execute(self.prepare())
        (self.root/'main.py').unlink()
        self.assertFalse(self.verify(tx)['evidence_usable'])
        (self.root/'main.py').write_bytes(b'new\n')
        from governor_workbench.execution_workspace import WorkspaceStager
        stage=WorkspaceStager(self.app.config['data_dir']).base/tx['stage_id']/'files'/'main.py'
        stage.write_bytes(b'changed')
        self.assertFalse(self.verify(tx)['evidence_usable'])

    def test_post_apply_journal_file_tampering_is_rejected(self):
        import json
        tx=self.execute(self.prepare())
        tx['files'][0]['written']=False
        with self.store.db() as db:
            db.execute('UPDATE pilot_apply_transactions SET body=? WHERE id=?',(json.dumps(tx),tx['id']))
        self.assertFalse(self.verify(tx)['evidence_usable'])
