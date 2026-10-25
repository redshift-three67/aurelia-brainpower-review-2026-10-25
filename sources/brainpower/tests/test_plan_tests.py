import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from governor_workbench.store import Store
from governor_workbench.plans import PlanBook


class PlanTestCompletionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        base=Path(self.tmp.name).resolve(); self.root=base/'pilot'; (self.root/'tests').mkdir(parents=True)
        (self.root/'tests/test_ok.py').write_text('import unittest\nclass Test(unittest.TestCase):\n def test_ok(self): self.assertEqual(1,1)\n')
        self.store=Store(base/'data/journal.db')
        self.config=dict(data_dir=str(base/'data'),staging_pilot_roots=[str(self.root)],projects=[])
        self.context=dict(plan_ready=True,scope_hash='a'*64,review_scope=dict(kind='project',id='pilot'),
                          registry_projects=[dict(id='pilot',path=str(self.root),group_id=None,archived=False)])
        self.app=SimpleNamespace(store=self.store,config=self.config,scope_context=lambda *a,**kw:copy.deepcopy(self.context))
        self.book=PlanBook(self.store,self.config)
        def step(key,action,deps): return dict(id=key,title=key,project_id='pilot',priority=1,depends_on=deps,
            rationale='Fixture',scope=['tests/test_ok.py'],tests=['stdlib unittest'],action=action)
        self.candidate=self.book.save_candidate(self.context,dict(summary='Fixture',steps=[step('before','review',[]),step('test','test',['before']),step('after','review',['test'])]),
            dict(summary='Clean',decision='REVIEW_ONLY',findings=[],required_evidence=[]),'fixture')
        self.selection=self.book.approve(self.candidate['id'],'a'*64,self.context,['before','test','after'],'sequence')
        self.before=self.book.complete_step(self.candidate['id'],'before',self.context,'a'*64,self.selection['id'],'Reviewed')

    def run_test(self):
        from governor_workbench.plan_tests import run
        request=dict(candidate_id=self.candidate['id'],step_id='test',scope_hash='a'*64,selection_id=self.selection['id'])
        job=self.store.create_job('plan_test',None,request)
        self.store.update_job(job['id'],status='running')
        result=run(self.app,job,None,lambda line:None)
        self.store.update_job(job['id'],status='completed',result=result)
        return job,result

    def rows(self): return {row['id']:row for row in self.book.dependency_report(self.candidate['id'],self.context)['steps']}

    def test_success_satisfies_chain_and_withdrawal_invalidates_descendants(self):
        job,result=self.run_test()
        self.assertTrue(result['success']); self.assertEqual('accepted',self.rows()['test']['completion_status'])
        self.book.complete_step(self.candidate['id'],'after',self.context,'a'*64,self.selection['id'],'Reviewed')
        self.book.withdraw_completion(self.candidate['id'],'before',self.before['id'],'Withdrawn')
        self.assertEqual('stale',self.rows()['test']['completion_status'])
        self.assertEqual('stale',self.rows()['after']['completion_status'])

    def test_file_drift_invalidates_test_and_followup(self):
        self.run_test()
        self.book.complete_step(self.candidate['id'],'after',self.context,'a'*64,self.selection['id'],'Reviewed')
        (self.root/'tests/test_ok.py').write_text('changed')
        self.assertEqual('stale',self.rows()['test']['completion_status'])
        self.assertEqual('stale',self.rows()['after']['completion_status'])

    def test_new_attempt_invalidates_old_success_even_when_queued(self):
        job,result=self.run_test()
        self.store.create_job('plan_test',None,job['request'])
        self.assertEqual('stale',self.rows()['test']['completion_status'])

    def test_failure_never_creates_completion(self):
        (self.root/'tests/test_ok.py').write_text('import unittest\nclass Test(unittest.TestCase):\n def test_fail(self): self.fail("expected")\n')
        job,result=self.run_test()
        self.assertFalse(result['success']); self.assertEqual('not_proven',self.rows()['test']['completion_status'])

    def test_revoked_predecessor_prevents_run(self):
        self.book.withdraw_completion(self.candidate['id'],'before',self.before['id'],'Withdrawn')
        with self.assertRaises(ValueError): self.run_test()

    def test_adapter_and_allowlist_changes_invalidate_receipt(self):
        from unittest.mock import patch
        self.run_test()
        with patch('governor_workbench.plan_tests.adapter_hash',return_value='b'*64):
            self.assertEqual('stale',self.rows()['test']['completion_status'])
        self.config['staging_pilot_roots']=[]
        self.assertEqual('stale',self.rows()['test']['completion_status'])

    def test_reselection_invalidates_test(self):
        self.run_test()
        self.book.approve(self.candidate['id'],'a'*64,self.context,['before','test','after'],'sequence')
        self.assertEqual('stale',self.rows()['test']['completion_status'])

    def test_test_withdrawal_and_retest_dont_revive_old_followup(self):
        job,result=self.run_test()
        self.book.complete_step(self.candidate['id'],'after',self.context,'a'*64,self.selection['id'],'Reviewed')
        self.book.withdraw_completion(self.candidate['id'],'test',result['completion_receipt']['id'],'Retest needed')
        self.assertEqual('withdrawn',self.rows()['test']['completion_status'])
        self.assertEqual('stale',self.rows()['after']['completion_status'])
        self.run_test()
        self.assertEqual('accepted',self.rows()['test']['completion_status'])
        self.assertEqual('stale',self.rows()['after']['completion_status'])

    def test_missing_config_never_acknowledges_test_receipt(self):
        self.run_test()
        report=PlanBook(self.store).dependency_report(self.candidate['id'],self.context)
        self.assertEqual('stale',next(r for r in report['steps'] if r['id']=='test')['completion_status'])

    def test_scope_or_predecessor_change_during_run_blocks_completion(self):
        from unittest.mock import patch
        from governor_workbench.staged_tests import run_staged_tests
        def changed(*args):
            result=run_staged_tests(*args)
            self.context['scope_hash']='b'*64
            return result
        with patch('governor_workbench.plan_tests.run_staged_tests',side_effect=changed):
            with self.assertRaises(ValueError): self.run_test()
        self.assertIsNone(self.rows()['test']['completion_receipt'])

    def test_all_skipped_cannot_complete(self):
        (self.root/'tests/test_ok.py').write_text('import unittest\n@unittest.skip("fixture")\nclass Test(unittest.TestCase):\n def test_skip(self): pass\n')
        job,result=self.run_test()
        self.assertFalse(result['success']); self.assertIsNone(self.rows()['test']['completion_receipt'])

    def test_relocated_registry_root_cannot_reuse_old_files_receipt(self):
        self.run_test()
        other=self.root.parent/'other'; other.mkdir()
        self.config['staging_pilot_roots'].append(str(other))
        self.context['registry_projects'][0]['path']=str(other)
        self.assertEqual('stale',self.rows()['test']['completion_status'])
