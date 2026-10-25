import threading
import unittest
from unittest.mock import patch

from tests import test_technical_completion
from governor_workbench.change_chain_preview import preview
from governor_workbench.change_journal import ChangeJournal
from governor_workbench.jobs import JobCancelled
from governor_workbench.store import JobBusy


class ChangeControllerTests(unittest.TestCase):
    setUp = test_technical_completion.TechnicalCompletionTests.setUp
    prepare = test_technical_completion.TechnicalCompletionTests.prepare
    execute = test_technical_completion.TechnicalCompletionTests.execute
    verified_job = test_technical_completion.TechnicalCompletionTests.verified_job
    complete = test_technical_completion.TechnicalCompletionTests.complete

    def pair_plan(self):
        future=dict(self.step,id='next',scope=['future.py'],depends_on=['fix'])
        self.candidate=self.book.save_candidate(self.context,dict(summary='Pair',steps=[self.step,future]),self.review,'f'*32)
        self.selection=self.book.approve(self.candidate['id'],'a'*64,self.context,['fix','next'],'sequence')
        # Rebind fixture upstream stage/test to this real selected two-step plan.
        import json
        with self.store.db() as db:
            req=dict(self.source['request'],candidate_id=self.candidate['id'])
            db.execute('UPDATE jobs SET request=? WHERE id=?',(json.dumps(req),self.source['id']))
        self.result['plan_selection_id']=self.selection['id']
        self.store.update_job(self.test['id'],result=self.result)
        return preview(self.app,self.candidate['id'],['fix','next'])

    def begin(self,shown=None,cancel=None):
        from governor_workbench.change_controller import begin
        shown=shown or self.pair_plan()
        return begin(self.app,self.candidate['id'],['fix','next'],shown['binding_hash'],'Explicit baseline',cancel)

    def ready(self):
        self.chain=self.begin();self.receipt=self.complete(self.verified_job())

    def confirm(self,**kw):
        from governor_workbench.change_controller import confirm
        args=dict(app=self.app,chain_id=self.chain['id'],expected_head=None,
                  technical_receipt_id=self.receipt['id'],observed_scope_hash='b'*64,
                  selection_id=self.selection['id'],note='Explicit H1')
        args.update(kw)
        return confirm(**args)

    def test_durable_baseline_real_completion_and_idempotent_adoption(self):
        self.ready();event=self.confirm()
        self.assertEqual(self.tx['id'],event['evidence']['transaction']['id'])
        self.assertEqual(self.receipt,event['evidence']['technical_receipt'])
        self.assertFalse(event['execution_authorized'])
        self.assertEqual(event,self.confirm())
        with self.assertRaises(ValueError):self.confirm(note='Different consent')
        self.assertEqual(1,len(ChangeJournal(self.store).read(self.chain['id'])['events']))

    def test_old_preview_and_changed_selection_block_baseline(self):
        shown=self.pair_plan()
        self.book.approve(self.candidate['id'],'a'*64,self.context,['fix','next'],'sequence')
        with self.assertRaises(ValueError):self.begin(shown)

    def test_busy_and_cancelled_admission(self):
        shown=self.pair_plan();job=self.store.create_job('fixture',None,{})
        with self.assertRaises(JobBusy):self.begin(shown)
        self.store.update_job(job['id'],status='cancelled')
        cancel=threading.Event();cancel.set()
        with self.assertRaises(JobCancelled):self.begin(shown,cancel)

    def test_newer_failed_verification_blocks_old_receipt(self):
        self.ready();new=self.store.create_job('pilot_verify',None,dict(transaction_id=self.tx['id']))
        self.store.update_job(new['id'],status='failed')
        with self.assertRaises(ValueError):self.confirm()
        self.assertEqual([],ChangeJournal(self.store).read(self.chain['id'])['events'])

    def test_newer_failed_test_blocks_old_receipt(self):
        self.ready();new=self.store.create_job('stage_test',None,dict(stage_job_id=self.source['id']))
        self.store.update_job(new['id'],status='failed')
        with self.assertRaises(ValueError):self.confirm()

    def test_other_chain_file_drift_blocks_adoption(self):
        self.ready();(self.root/'future.py').write_text('foreign')
        with self.assertRaises(ValueError):self.confirm()

    def test_new_selection_blocks_even_when_original_bytes_return(self):
        self.ready();self.context['scope_hash']='a'*64
        self.book.approve(self.candidate['id'],'a'*64,self.context,['fix','next'],'sequence')
        self.context['scope_hash']='b'*64
        with self.assertRaises(ValueError):self.confirm()

    def test_cancellation_at_commit_does_not_append(self):
        self.ready();cancel=threading.Event()
        original=ChangeJournal.transition
        def cancelled(journal,*args,**kwargs):
            cancel.set();return original(journal,*args,**kwargs)
        with patch.object(ChangeJournal,'transition',cancelled),self.assertRaises(JobCancelled):
            self.confirm(cancel=cancel)
        self.assertEqual([],ChangeJournal(self.store).read(self.chain['id'])['events'])

    def test_worker_claim_blocks_competing_manual_job_during_verification(self):
        self.ready();original=self.app.scope_context;seen=[]
        def context(*args,**kwargs):
            with self.assertRaises(JobBusy):self.store.create_job('competing',None,{})
            seen.append(True);return original(*args,**kwargs)
        self.app.scope_context=context;self.confirm();self.assertTrue(seen)

    def test_commit_rechecks_changed_durable_proof(self):
        self.ready();original=ChangeJournal.transition
        def changed(journal,*args,**kwargs):
            self.store.update_job(self.test['id'],status='failed')
            return original(journal,*args,**kwargs)
        with patch.object(ChangeJournal,'transition',changed),self.assertRaises(ValueError):self.confirm()
        self.assertEqual([],ChangeJournal(self.store).read(self.chain['id'])['events'])

    def test_restart_interrupts_claim_without_adoption_or_replay(self):
        from governor_workbench.store import Store
        self.ready();original=ChangeJournal.transition
        def restart(journal,*args,**kwargs):
            Store(self.store.path)
            return original(journal,*args,**kwargs)
        with patch.object(ChangeJournal,'transition',restart),self.assertRaises(ValueError):self.confirm()
        self.assertEqual([],ChangeJournal(self.store).read(self.chain['id'])['events'])
        with self.store.db() as db:
            self.assertEqual('interrupted',db.execute("SELECT status FROM jobs WHERE action='change_journal_commit' ORDER BY rowid DESC LIMIT 1").fetchone()[0])

    def test_failure_rolls_back_terminal_claim_and_releases_slot(self):
        import sqlite3
        self.ready()
        with self.store.db() as db:
            db.execute("CREATE TRIGGER fail_event BEFORE INSERT ON dependent_change_events BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(sqlite3.IntegrityError):self.confirm()
        with self.store.db() as db:
            self.assertEqual('failed',db.execute("SELECT status FROM jobs WHERE action='change_journal_commit' ORDER BY rowid DESC LIMIT 1").fetchone()[0])
        self.assertEqual([],ChangeJournal(self.store).read(self.chain['id'])['events'])
        self.assertEqual(b'new\n',(self.root/'main.py').read_bytes())
        self.store.create_job('slot_available',None,{})

    def test_adapter_or_allowlist_or_observed_scope_change_blocks(self):
        self.ready()
        with patch('governor_workbench.change_controller.identity',return_value='f'*64),self.assertRaises(ValueError):self.confirm()
        with self.assertRaises(ValueError):self.confirm(observed_scope_hash='c'*64)
        self.app.config['staging_pilot_roots']=[]
        with self.assertRaises(ValueError):self.confirm()

    def test_changed_verification_report_is_not_trusted(self):
        self.ready();job=self.store.job(self.receipt['verified_job_id'])
        job['result']['post_apply_verification']['step_hash']='f'*64
        self.store.update_job(job['id'],result=job['result'])
        with self.assertRaises(ValueError):self.confirm()

    def test_tampered_manifest_blocks_even_with_saved_success(self):
        self.ready()
        from governor_workbench.execution_workspace import WorkspaceStager
        path=WorkspaceStager(self.app.config['data_dir']).base/self.tx['stage_id']/'manifest.json'
        path.write_text('{}')
        with self.assertRaises(ValueError):self.confirm()

    def test_unconfirmed_newer_transfer_blocks_adoption(self):
        import json
        self.ready()
        with self.store.db() as db:
            tx=dict(self.tx,id='unconfirmed',stage_id='other')
            db.execute('INSERT INTO pilot_apply_transactions VALUES(?,?,?,?)',(tx['id'],tx['stage_id'],'completed',json.dumps(tx)))
        with self.assertRaises(ValueError):self.confirm()

    def test_baseline_repeat_does_not_duplicate_or_change_original_selection(self):
        shown=self.pair_plan();chain=self.begin(shown)
        self.assertEqual(chain,self.begin(shown))
        self.assertEqual(shown['binding'],chain['controller_binding'])
        self.assertEqual(self.selection['id'],chain['binding']['selection_id'])
        self.assertEqual(b'old WIP\r\n',(self.root/'main.py').read_bytes())

    def test_allowlist_revoked_immediately_before_commit_blocks(self):
        self.ready();original=ChangeJournal.transition
        def revoke(journal,*args,**kwargs):
            self.app.config['staging_pilot_roots']=[]
            return original(journal,*args,**kwargs)
        with patch.object(ChangeJournal,'transition',revoke),self.assertRaises(ValueError):self.confirm()
        self.assertEqual([],ChangeJournal(self.store).read(self.chain['id'])['events'])
