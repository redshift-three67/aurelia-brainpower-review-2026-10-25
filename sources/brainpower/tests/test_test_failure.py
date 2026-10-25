import unittest
from tests import test_plan_tests


class TestFailureTests(unittest.TestCase):
    def setUp(self):
        test_plan_tests.PlanTestCompletionTests.setUp(self)
        (self.root/'tests/test_ok.py').write_text('import unittest\nclass Test(unittest.TestCase):\n def test_bad(self): self.fail("expected failure")\n')
        self.job,self.result=test_plan_tests.PlanTestCompletionTests.run_test(self)
        self.store.update_job(self.job['id'],status='failed')

    def report(self):
        from governor_workbench.test_failure import diagnose
        return diagnose(self.app,self.job['id'])

    def test_current_failure_has_bound_report_without_authorizing_repair(self):
        r=self.report();self.assertTrue(r['evidence_usable'])
        self.assertEqual(r['classification'],'test_failure')
        self.assertEqual(r['attempts']['remaining'],2)
        self.assertFalse(r['repair_authorized']);self.assertFalse(r['models_called'])

    def test_file_drift_blocks_report(self):
        (self.root/'tests/test_ok.py').write_text('changed')
        self.assertFalse(self.report()['evidence_usable'])

    def test_new_attempt_blocks_old_failure(self):
        self.store.create_job('plan_test',None,self.job['request'])
        self.assertFalse(self.report()['evidence_usable'])

    def test_predecessor_withdrawal_blocks_report(self):
        self.book.withdraw_completion(self.candidate['id'],'before',self.before['id'],'withdraw')
        self.assertFalse(self.report()['evidence_usable'])

    def test_reselection_blocks_report(self):
        self.book.approve(self.candidate['id'],'a'*64,self.context,['before','test','after'],'sequence')
        self.assertFalse(self.report()['evidence_usable'])

    def test_missing_completion_proof_is_not_a_repairable_failure(self):
        self.result['test_evidence']['test']['completion_verified']=False
        self.store.update_job(self.job['id'],result=self.result)
        self.assertFalse(self.report()['evidence_usable'])

    def test_adapter_change_blocks_report(self):
        from unittest.mock import patch
        with patch('governor_workbench.plan_tests.adapter_hash',return_value='f'*64):
            self.assertFalse(self.report()['evidence_usable'])

    def test_log_excerpt_marks_truncation_and_preserves_full_hash(self):
        import hashlib
        output='begin'+('x'*9000)+'end'
        self.result['test_evidence']['test']['output']=output
        self.store.update_job(self.job['id'],result=self.result)
        r=self.report();self.assertTrue(r['output_truncated'])
        self.assertTrue(r['output_excerpt'].startswith('begin'));self.assertTrue(r['output_excerpt'].endswith('end'))
        self.assertEqual(r['output_sha256'],hashlib.sha256(output.encode()).hexdigest())

    def test_cancel_does_not_produce_report(self):
        import threading
        from governor_workbench.jobs import JobCancelled
        from governor_workbench.test_failure import diagnose
        event=threading.Event();event.set()
        with self.assertRaises(JobCancelled):diagnose(self.app,self.job['id'],event)

    def test_success_is_not_a_failure_source(self):
        self.result['success']=True
        self.store.update_job(self.job['id'],result=self.result)
        with self.assertRaises(ValueError):self.report()

    def test_scope_drift_blocks_report(self):
        self.context['scope_hash']='f'*64
        self.assertFalse(self.report()['evidence_usable'])

    def test_exhausted_budget_does_not_erase_current_failure(self):
        for _ in range(2):
            self.job,self.result=test_plan_tests.PlanTestCompletionTests.run_test(self)
        report=self.report()
        self.assertTrue(report['evidence_usable'])
        self.assertFalse(report['attempts']['allowed'])
