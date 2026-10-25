import copy
import json
import unittest
from tests import test_technical_completion
from governor_workbench.plans import PlanBook


class ChangeChainTests(unittest.TestCase):
    setUp = test_technical_completion.TechnicalCompletionTests.setUp
    prepare = test_technical_completion.TechnicalCompletionTests.prepare
    execute = test_technical_completion.TechnicalCompletionTests.execute
    verified_job = test_technical_completion.TechnicalCompletionTests.verified_job
    complete = test_technical_completion.TechnicalCompletionTests.complete

    def transition(self):
        from governor_workbench.change_chain import confirm
        job=self.verified_job(); technical=self.complete(job)
        return confirm(self.app,technical['id'],'b'*64,self.result['plan_selection_id'],'Neuen Stand und Plan geprüft.')

    def test_change_is_accepted_only_after_explicit_transition(self):
        receipt=self.transition()
        report=PlanBook(self.store,self.app.config).dependency_report(self.candidate['id'],self.context)
        self.assertTrue(report['current'])
        self.assertEqual(report['scope_hash'],'b'*64)
        self.assertEqual(report['steps'][0]['completion_status'],'accepted')
        self.assertEqual(report['steps'][0]['completion_receipt']['id'],receipt['completion']['id'])
        self.assertFalse(self.book.execution_permission(self.candidate['id'],'fix',self.context)['plan_selection_approved'])

    def test_drift_invalidates_transition(self):
        self.transition(); (self.root/'main.py').write_text('drift')
        report=PlanBook(self.store,self.app.config).dependency_report(self.candidate['id'],self.context)
        self.assertFalse(report['current']); self.assertEqual(report['steps'][0]['completion_status'],'stale')

    def test_missing_current_intake_prevents_transition(self):
        from governor_workbench.change_chain import confirm
        job=self.verified_job(); technical=self.complete(job); self.context['plan_ready']=False
        with self.assertRaises(ValueError): confirm(self.app,technical['id'],'b'*64,self.result['plan_selection_id'],'Prüfen')

    def test_withdrawal_invalidates_change_without_reactivation(self):
        r=self.transition(); self.book.withdraw_completion(self.candidate['id'],'fix',r['completion']['id'],'Zurückgezogen')
        report=PlanBook(self.store,self.app.config).dependency_report(self.candidate['id'],self.context)
        self.assertEqual(report['steps'][0]['completion_status'],'withdrawn')

    def test_no_config_fails_closed(self):
        self.transition()
        self.assertFalse(self.book.dependency_report(self.candidate['id'],self.context)['current'])

    def test_rollback_blocks_chain(self):
        self.transition()
        from governor_workbench.pilot_actions import rollback
        rollback(self.app,self.tx['id'],None)
        self.assertFalse(PlanBook(self.store,self.app.config).dependency_report(self.candidate['id'],self.context)['current'])

    def test_duplicate_wrong_selection_and_wrong_scope_rejected(self):
        from governor_workbench.change_chain import confirm
        job=self.verified_job(); technical=self.complete(job)
        for scope,selection in [('c'*64,self.result['plan_selection_id']),('b'*64,'f'*32)]:
            with self.assertRaises(ValueError): confirm(self.app,technical['id'],scope,selection,'Prüfung')
        confirm(self.app,technical['id'],'b'*64,self.result['plan_selection_id'],'Prüfung')
        with self.assertRaises(ValueError): confirm(self.app,technical['id'],'b'*64,self.result['plan_selection_id'],'Nochmals')

    def test_new_test_attempt_invalidates_chain(self):
        self.transition()
        self.store.create_job('stage_test',None,dict(stage_job_id=self.source['id']))
        self.assertFalse(PlanBook(self.store,self.app.config).dependency_report(self.candidate['id'],self.context)['current'])

    def test_new_revision_invalidates_chain(self):
        self.transition()
        self.book.save_candidate(self.context,dict(summary='New',steps=[self.step]),self.review,'f'*32)
        self.assertFalse(PlanBook(self.store,self.app.config).dependency_report(self.candidate['id'],self.context)['current'])

    def test_reselection_after_transition_requires_new_plan(self):
        self.transition()
        with self.assertRaisesRegex(ValueError,'neuen Plan'):
            PlanBook(self.store,self.app.config).approve(self.candidate['id'],'a'*64,self.context,['fix'])

    def test_missing_technical_receipt_is_descriptive(self):
        from governor_workbench.change_chain import confirm
        with self.assertRaisesRegex(ValueError,'Abschluss fehlt'):
            confirm(self.app,'f'*32,'b'*64,'e'*32,'Prüfung')

    def test_cancel_creates_no_transition(self):
        import threading
        from governor_workbench.change_chain import confirm,latest
        from governor_workbench.jobs import JobCancelled
        job=self.verified_job(); technical=self.complete(job)
        cancel=threading.Event();cancel.set()
        with self.assertRaises(JobCancelled):
            confirm(self.app,technical['id'],'b'*64,self.result['plan_selection_id'],'Prüfung',cancel)
        with self.store.db() as db: self.assertIsNone(latest(db,self.candidate['id']))

    def test_transition_journal_is_immutable(self):
        import sqlite3
        self.transition()
        with self.store.db() as db:
            with self.assertRaises(sqlite3.IntegrityError): db.execute('DELETE FROM plan_scope_transitions')

    def test_adapter_or_registry_change_invalidates_chain(self):
        from unittest.mock import patch
        self.transition(); book=PlanBook(self.store,self.app.config)
        with patch('governor_workbench.change_chain.identity',return_value='c'*64):
            self.assertFalse(book.dependency_report(self.candidate['id'],self.context)['current'])
        self.project['archived']=True
        self.assertFalse(book.dependency_report(self.candidate['id'],self.context)['current'])

    def test_following_review_uses_new_scope(self):
        follow=dict(self.step,id='review',action='review',depends_on=['fix'])
        self.candidate=self.book.save_candidate(self.context,dict(summary='Chain',steps=[self.step,follow]),self.review,'e'*32)
        approval=self.book.approve(self.candidate['id'],'a'*64,self.context,['fix','review'],'sequence')
        with self.store.db() as db:
            db.execute('UPDATE jobs SET request=? WHERE id=?',(json.dumps({**self.source['request'],'candidate_id':self.candidate['id']}),self.source['id']))
        self.result['plan_selection_id']=approval['id']; self.store.update_job(self.test['id'],result=self.result)
        self.transition()
        book=PlanBook(self.store,self.app.config)
        book.complete_step(self.candidate['id'],'review',self.context,'b'*64,approval['id'],'Review geprüft')
        report=book.dependency_report(self.candidate['id'],self.context)
        self.assertEqual([r['completion_status'] for r in report['steps']],['accepted','accepted'])
