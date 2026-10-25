import json
import threading
import unittest
from unittest.mock import patch

from tests import test_change_controller
from governor_workbench.change_journal import ChangeJournal
from governor_workbench.jobs import JobCancelled
from governor_workbench.store import JobBusy


class ChangeSuccessorTests(unittest.TestCase):
    setUp=test_change_controller.ChangeControllerTests.setUp
    prepare=test_change_controller.ChangeControllerTests.prepare
    execute=test_change_controller.ChangeControllerTests.execute
    verified_job=test_change_controller.ChangeControllerTests.verified_job
    complete=test_change_controller.ChangeControllerTests.complete
    pair_plan=test_change_controller.ChangeControllerTests.pair_plan
    begin=test_change_controller.ChangeControllerTests.begin
    ready=test_change_controller.ChangeControllerTests.ready
    confirm=test_change_controller.ChangeControllerTests.confirm

    def transferred(self):
        self.ready();self.edge=self.confirm()

    def preview(self):
        from governor_workbench.change_successor import preview
        return preview(self.app,self.chain['id'])

    def accept(self,shown=None,**kw):
        from governor_workbench.change_successor import acknowledge
        shown=shown or self.preview()
        return acknowledge(self.app,self.chain['id'],shown['binding_hash'],'H1 explicitly acknowledged',**kw)

    def test_preview_read_only_and_consent_preserves_original_plan(self):
        self.transferred()
        with self.store.db() as db:before='\n'.join(db.iterdump())
        shown=self.preview()
        self.assertTrue(shown['eligible'],shown)
        with self.store.db() as db:self.assertEqual(before,'\n'.join(db.iterdump()))
        self.assertEqual('a'*64,shown['binding']['original_scope_hash'])
        self.assertEqual('b'*64,shown['binding']['effective_scope_hash'])
        self.assertEqual(self.edge['id'],shown['binding']['predecessor_event_id'])
        self.assertEqual('next',shown['binding']['step_id'])
        receipt=self.accept(shown)
        self.assertEqual(receipt,self.accept(shown))
        self.assertFalse(receipt['execution_authorized'])
        self.assertEqual(self.candidate,self.book.get(self.candidate['id']))
        self.assertEqual(b'new\n',(self.root/'main.py').read_bytes())
        self.assertFalse((self.root/'future.py').exists())

    def test_unconfirmed_transfer_cannot_be_acknowledged(self):
        self.ready();self.assertFalse(self.preview()['eligible'])

    def test_foreign_byte_drift_after_preview_blocks(self):
        self.transferred();shown=self.preview()
        (self.root/'future.py').write_text('foreign')
        with self.assertRaises(ValueError):self.accept(shown)

    def test_new_verification_attempt_invalidates_preview_and_consent(self):
        self.transferred();receipt=self.accept()
        job=self.store.create_job('pilot_verify',None,dict(transaction_id=self.tx['id']))
        self.store.update_job(job['id'],status='failed')
        self.assertFalse(self.preview()['eligible'])
        from governor_workbench.change_successor import require_current
        with self.assertRaises(ValueError):require_current(self.app,receipt['id'])

    def test_rollback_permanently_invalidates_successor_consent(self):
        self.transferred();receipt=self.accept()
        from governor_workbench.pilot_actions import rollback
        rollback(self.app,self.tx['id'],None)
        self.assertFalse(self.preview()['eligible'])
        from governor_workbench.change_successor import require_current
        with self.assertRaises(ValueError):require_current(self.app,receipt['id'])

    def test_selection_changed_since_h1_blocks(self):
        self.transferred();self.context['scope_hash']='a'*64
        self.book.approve(self.candidate['id'],'a'*64,self.context,['fix','next'],'sequence')
        self.context['scope_hash']='b'*64
        self.assertFalse(self.preview()['eligible'])

    def test_cancel_and_busy_do_not_create_consent(self):
        self.transferred();shown=self.preview();event=threading.Event();event.set()
        with self.assertRaises(JobCancelled):self.accept(shown,cancel=event)
        self.store.create_job('fixture',None,{})
        with self.assertRaises(JobBusy):self.accept(shown)

    def test_saved_consent_is_immutable_and_requires_fresh_check(self):
        import sqlite3
        self.transferred();receipt=self.accept()
        from governor_workbench.change_successor import require_current
        self.assertEqual(receipt,require_current(self.app,receipt['id']))
        with self.store.db() as db:
            for sql in ('UPDATE dependent_change_successor_consents SET body=body',
                        'DELETE FROM dependent_change_successor_consents'):
                with self.assertRaises(sqlite3.IntegrityError):db.execute(sql)
        self.app.config['staging_pilot_roots']=[]
        with self.assertRaises(ValueError):require_current(self.app,receipt['id'])

    def test_drift_during_second_observation_blocks(self):
        self.transferred()
        from governor_workbench import change_successor
        original=change_successor._observe;calls=[]
        def observe(*args,**kw):
            value=original(*args,**kw);calls.append(1)
            if len(calls)==1:(self.root/'future.py').write_text('changed')
            return value
        with patch.object(change_successor,'_observe',observe):self.assertFalse(self.preview()['eligible'])

    def test_consent_cannot_enable_legacy_dependent_execution(self):
        self.transferred();self.accept()
        from governor_workbench.execution_policy import require_staging_pilot
        with self.assertRaises(ValueError):
            require_staging_pilot(self.app.config,self.context,self.candidate,'next',{'plan_selection_approved':True})

    def test_empty_preview_creates_no_schema_or_job(self):
        from governor_workbench.change_successor import preview
        with self.store.db() as db:before='\n'.join(db.iterdump())
        self.assertFalse(preview(self.app,'missing')['eligible'])
        with self.store.db() as db:self.assertEqual(before,'\n'.join(db.iterdump()))

    def test_cancel_immediately_before_commit_leaves_no_consent(self):
        self.transferred();shown=self.preview();cancel=threading.Event()
        from governor_workbench import change_successor
        original=change_successor.observe_files
        def interrupted(*args,**kw):
            original(*args,**kw);cancel.set()
        with patch.object(change_successor,'observe_files',interrupted),self.assertRaises(JobCancelled):
            self.accept(shown,cancel=cancel)
        with self.store.db() as db:
            self.assertEqual(0,db.execute('SELECT COUNT(*) FROM dependent_change_successor_consents').fetchone()[0])

    def test_failed_insert_cannot_leave_successful_claim(self):
        import sqlite3
        from governor_workbench.change_successor import _initialize
        self.transferred();shown=self.preview()
        with self.store.db() as db:
            _initialize(db)
            db.execute("CREATE TRIGGER fail_h1 BEFORE INSERT ON dependent_change_successor_consents BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(sqlite3.IntegrityError):self.accept(shown)
        with self.store.db() as db:
            self.assertEqual(0,db.execute('SELECT COUNT(*) FROM dependent_change_successor_consents').fetchone()[0])
            self.assertEqual('failed',db.execute("SELECT status FROM jobs WHERE action='change_journal_commit' ORDER BY rowid DESC LIMIT 1").fetchone()[0])

    def test_current_consent_does_not_reuse_newer_staging_test(self):
        self.transferred();receipt=self.accept()
        job=self.store.create_job('stage_test',None,dict(stage_job_id=self.source['id']))
        self.store.update_job(job['id'],status='failed')
        from governor_workbench.change_successor import require_current
        with self.assertRaises(ValueError):require_current(self.app,receipt['id'])
