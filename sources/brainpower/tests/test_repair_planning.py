import unittest
from tests import test_test_failure
from governor_workbench import repair_planning


class RepairPlanningTests(unittest.TestCase):
    setUp=test_test_failure.TestFailureTests.setUp

    def diagnosis(self):
        from governor_workbench.test_failure import diagnose
        job=self.store.create_job('plan_failure',None,dict(job_id=self.job['id']))
        self.store.update_job(job['id'],status='completed',result=dict(test_failure=diagnose(self.app,self.job['id'])))
        return job

    def test_context_is_bound_and_does_not_authorize_code(self):
        context,binding=repair_planning.prepare(self.app,self.diagnosis()['id'],'Fehler beheben planen')
        self.assertEqual(binding['paths'],['tests/test_ok.py'])
        self.assertFalse(context['current_request']['file_changes_authorized'])
        self.assertIn('expected failure',context['repair_evidence']['sources'][0]['content'])

    def test_drift_and_missing_note_rejected(self):
        job=self.diagnosis()
        with self.assertRaises(ValueError):repair_planning.prepare(self.app,job['id'],' ')
        (self.root/'tests/test_ok.py').write_text('changed')
        with self.assertRaises(ValueError):repair_planning.prepare(self.app,job['id'],'Planung')

    def test_budget_all_statuses_and_self_admission(self):
        for state in ('failed','cancelled'):
            job=self.store.create_job('scope_plan',None,dict(repair_candidate_id=self.candidate['id'],repair_step_id='test'))
            self.store.update_job(job['id'],status=state)
        with self.store.db() as db:
            with self.assertRaises(ValueError):repair_planning.attempts(db,self.candidate['id'],'test')
            self.assertEqual(2,repair_planning.attempts(db,self.candidate['id'],'test',job['id']))

    def test_scope_expansion_and_missing_test_blocked(self):
        import copy
        _,binding=repair_planning.prepare(self.app,self.diagnosis()['id'],'Planung')
        change=copy.deepcopy(self.candidate['proposal']['steps'][1]);change.update(id='fix',action='change',depends_on=[])
        test=dict(change,id='check',action='test',depends_on=['fix'])
        plan=dict(summary='Repair',steps=[change,test])
        self.assertEqual(plan,repair_planning.validate(plan,binding,'pilot'))
        with self.assertRaises(ValueError):repair_planning.validate(dict(summary='Repair',steps=[change]),binding,'pilot')
        test['scope']=['outside.py']
        with self.assertRaises(ValueError):repair_planning.validate(plan,binding,'pilot')

    def test_egress_denial_prevents_preparation(self):
        from unittest.mock import patch
        job=self.diagnosis(); original=self.app.scope_context
        def guarded(*args,**kwargs):
            if kwargs.get('require_egress'):raise ValueError('egress denied')
            return original(*args,**kwargs)
        with patch.object(self.app,'scope_context',side_effect=guarded):
            with self.assertRaisesRegex(ValueError,'egress denied'):
                repair_planning.prepare(self.app,job['id'],'Planung')

    def test_pending_or_blocked_diagnosis_rejected(self):
        job=self.diagnosis();self.store.update_job(job['id'],status='failed')
        with self.assertRaises(ValueError):repair_planning.prepare(self.app,job['id'],'Planung')
