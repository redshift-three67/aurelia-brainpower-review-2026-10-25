import unittest
from tests import test_plan_tests
from governor_workbench import plan_tests


class TestAttemptTests(unittest.TestCase):
    setUp=test_plan_tests.PlanTestCompletionTests.setUp

    def job(self,status='failed',candidate=None):
        job=self.store.create_job('plan_test',None,dict(candidate_id=candidate or self.candidate['id'],step_id='test',scope_hash='a'*64,selection_id=self.selection['id']))
        self.store.update_job(job['id'],status=status)
        return job

    def policy(self,job_id=None):
        with self.store.db() as db:
            return plan_tests.attempt_policy(db,self.candidate['id'],'test',job_id)

    def test_three_attempts_count_even_cancelled_or_interrupted(self):
        for status in ('failed','cancelled','interrupted'): self.job(status)
        value=self.policy()
        self.assertFalse(value['allowed']);self.assertEqual(value['used'],3)
        self.assertEqual(value['remaining'],0);self.assertEqual(len(value['history']),3)

    def test_active_attempt_blocks_duplicate_but_can_execute(self):
        job=self.job('queued')
        self.assertFalse(self.policy()['allowed'])
        self.assertTrue(self.policy(job['id'])['allowed'])

    def test_third_admitted_attempt_can_execute_fourth_cannot(self):
        self.job();self.job();third=self.job('running')
        self.assertTrue(self.policy(third['id'])['allowed'])
        self.store.update_job(third['id'],status='failed')
        fourth=self.job('queued')
        self.assertFalse(self.policy(fourth['id'])['allowed'])
        self.assertFalse(self.policy(third['id'])['allowed'])

    def test_other_candidate_does_not_consume_budget(self):
        self.job(candidate='f'*32)
        self.assertEqual(self.policy()['used'],0)

    def test_reselection_does_not_reset_budget(self):
        for _ in range(3):self.job()
        self.book.approve(self.candidate['id'],'a'*64,self.context,['before','test','after'],'sequence')
        self.assertFalse(self.policy()['allowed'])

    def test_chain_exposes_limit_and_disables_start(self):
        for _ in range(3):self.job()
        row=self.book.dependency_report(self.candidate['id'],self.context)['steps'][1]
        self.assertFalse(row['test_run_available'])
        self.assertEqual(row['test_attempts']['remaining'],0)

    def test_worker_blocks_excess_before_staging(self):
        for _ in range(3):self.job()
        fourth=self.job('running')
        with self.assertRaisesRegex(ValueError,'Versuch'):
            plan_tests.run(self.app,fourth,None,lambda line:None)

    def test_submission_rejects_without_inserting_another_job(self):
        import threading,queue
        from governor_workbench.jobs import JobRunner
        runner=JobRunner.__new__(JobRunner)
        runner.app=self.app;runner.lock=threading.RLock();runner.pending=queue.Queue();runner.cancellations={}
        self.app.settings=lambda:dict(supervisor='gpt-6-astra')
        request=dict(candidate_id=self.candidate['id'],step_id='test',scope_hash='a'*64,selection_id=self.selection['id'])
        first=runner.submit_plan_test(request)
        with self.assertRaises(ValueError):runner.submit_plan_test(request)
        self.assertEqual(self.policy()['used'],1)
        self.store.update_job(first['id'],status='cancelled')
        self.job();self.job()
        with self.assertRaises(ValueError):runner.submit_plan_test(request)
        self.assertEqual(self.policy()['used'],3)

    def test_third_success_remains_valid_when_budget_exhausted(self):
        self.job();self.job()
        test_plan_tests.PlanTestCompletionTests.run_test(self)
        row=self.book.dependency_report(self.candidate['id'],self.context)['steps'][1]
        self.assertEqual(row['completion_status'],'accepted')
        self.assertFalse(row['test_run_available'])
