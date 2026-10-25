import sqlite3
import unittest

from tests import test_pilot_actions
from governor_workbench.pilot_verification import verify


class TechnicalCompletionTests(unittest.TestCase):
    setUp = test_pilot_actions.PilotActionsTests.setUp
    prepare = test_pilot_actions.PilotActionsTests.prepare
    execute = test_pilot_actions.PilotActionsTests.execute

    def verified_job(self):
        self.tx=self.execute(self.prepare())
        self.context['scope_hash']='b'*64
        report=verify(self.app,self.tx['id'])
        self.assertTrue(report['evidence_usable'])
        job=self.store.create_job('pilot_verify',None,dict(transaction_id=self.tx['id']))
        self.store.update_job(job['id'],status='completed',result=dict(success=True,post_apply_verification=report))
        return job

    def complete(self,job,scope='b'*64):
        from governor_workbench.technical_completion import complete
        return complete(self.app,job['id'],scope,'Nachher-Stand ausdrücklich geprüft.')

    def test_receipt_binds_scope_and_is_append_only(self):
        job=self.verified_job(); receipt=self.complete(job)
        self.assertEqual(receipt['binding']['observed_scope_hash'],'b'*64)
        self.assertEqual(receipt['verified_job_id'],job['id'])
        self.assertFalse(receipt['execution_enabled'])
        self.assertFalse(receipt['target_tests_executed'])
        with self.store.db() as db:
            for sql in ('DELETE FROM technical_completions','UPDATE technical_completions SET body=body'):
                with self.assertRaises(sqlite3.IntegrityError): db.execute(sql)
        report=verify(self.app,self.tx['id'])
        self.assertEqual('current',report['technical_completion']['status'])
        self.assertEqual(receipt['id'],report['technical_completion']['receipt']['id'])

    def test_wrong_scope_and_file_drift_block_receipt(self):
        job=self.verified_job()
        with self.assertRaises(ValueError): self.complete(job,'c'*64)
        (self.root/'main.py').write_bytes(b'changed')
        with self.assertRaises(ValueError): self.complete(job)

    def test_newer_verification_attempt_blocks_old_report(self):
        job=self.verified_job()
        newer=self.store.create_job('pilot_verify',None,dict(transaction_id=self.tx['id']))
        for status in ('queued','running','failed','cancelled','completed'):
            self.store.update_job(newer['id'],status=status)
            with self.subTest(status=status),self.assertRaises(ValueError): self.complete(job)

    def test_receipt_becomes_stale_after_scope_change_or_rollback(self):
        job=self.verified_job(); self.complete(job)
        self.context['scope_hash']='c'*64
        self.assertEqual('stale',verify(self.app,self.tx['id'])['technical_completion']['status'])
        from governor_workbench import pilot_actions
        pilot_actions.rollback(self.app,self.tx['id'],None)
        self.assertEqual('stale',verify(self.app,self.tx['id'])['technical_completion']['status'])

    def test_confirmation_requires_note_and_rejects_duplicate(self):
        from governor_workbench.technical_completion import complete
        job=self.verified_job()
        with self.assertRaises(ValueError): complete(self.app,job['id'],'b'*64,' ')
        self.complete(job)
        with self.assertRaises(ValueError): self.complete(job)

    def test_cancel_and_legacy_report_cannot_create_receipt(self):
        import threading
        from governor_workbench.technical_completion import complete
        from governor_workbench.jobs import JobCancelled
        job=self.verified_job(); event=threading.Event(); event.set()
        with self.assertRaises(JobCancelled): complete(self.app,job['id'],'b'*64,'Test',event)
        saved=self.store.job(job['id'])['result']
        saved['post_apply_verification'].pop('step_hash')
        self.store.update_job(job['id'],result=saved)
        with self.assertRaisesRegex(ValueError,'erneut'): self.complete(job)

    def test_selection_and_test_changes_block_confirmation(self):
        job=self.verified_job()
        self.context['scope_hash']='a'*64
        self.book.approve(self.candidate['id'],'a'*64,self.context,['fix'])
        self.context['scope_hash']='b'*64
        with self.assertRaises(ValueError): self.complete(job)

    def test_completion_adapter_change_requires_new_report(self):
        from unittest.mock import patch
        job=self.verified_job()
        with patch('governor_workbench.technical_completion.adapter_hash',return_value='c'*64):
            with self.assertRaises(ValueError): self.complete(job)
