import copy
import json
import unittest

from tests import test_change_successor
from governor_workbench import pilot_actions
from governor_workbench.execution_workspace import WorkspaceStager
from governor_workbench.pilot_verification import verify


class ChangeExecutionTests(unittest.TestCase):
    for _name in ('setUp','prepare','execute','verified_job','complete','pair_plan','begin','ready','confirm','transferred','preview','accept'):
        locals()[_name]=getattr(test_change_successor.ChangeSuccessorTests,_name)
    def successor(self):
        self.transferred();self.consent=self.accept()
        return dict(scope_kind='project',scope_id='pilot',scope_hash='b'*64,
                    candidate_id=self.candidate['id'],step_id='next',successor_consent_id=self.consent['id'])

    def stage_b(self):
        from governor_workbench.change_execution import resolve
        request=self.successor();candidate,step,permission=resolve(self.app,request,self.context)
        stage=WorkspaceStager(self.app.config['data_dir']).stage(str(self.root),['future.py'],
                    [dict(path='future.py',content='second\n')],{'future.py':None})
        source=self.store.create_job('scope_patch',None,request)
        self.store.update_job(source['id'],status='completed',result=dict(stage=stage,scope_hash='b'*64))
        test=self.store.create_job('stage_test',None,dict(stage_job_id=source['id']))
        result=copy.deepcopy(self.result)
        result.update(stage_job_id=source['id'],stage_id=stage['id'],manifest_hash=stage['manifest_hash'],scope_hash='b'*64,
                      successor_binding=permission['successor_binding'])
        self.store.update_job(test['id'],status='completed',result=result)
        self.bsource,self.btest=source,test
        return pilot_actions.prepare(self.app,test['id'])

    def applied_b(self):
        p=self.stage_b();self.btx=pilot_actions.execute(self.app,p['id'],p['proposal_hash'],None)
        self.context['scope_hash']='c'*64
        return self.btx

    def test_actual_b_apply_verify_complete_confirm_and_reverse_rollback(self):
        self.applied_b();report=verify(self.app,self.btx['id'])
        self.assertTrue(report['evidence_usable'],report)
        self.assertEqual('b'*64,report['plan_scope_hash'])
        self.assertEqual('a'*64,report['original_scope_hash'])
        job=self.store.create_job('pilot_verify',None,dict(transaction_id=self.btx['id']))
        self.store.update_job(job['id'],status='completed',result=dict(success=True,post_apply_verification=report))
        from governor_workbench.technical_completion import complete
        receipt=complete(self.app,job['id'],'c'*64,'B independently checked')
        from governor_workbench.change_controller import confirm
        event=confirm(self.app,self.chain['id'],self.edge['id'],receipt['id'],'c'*64,self.selection['id'],'Explicit H2')
        self.assertEqual(self.btx['id'],event['evidence']['transaction']['id'])
        with self.assertRaises(ValueError):pilot_actions.rollback(self.app,self.tx['id'],None)
        pilot_actions.rollback(self.app,self.btx['id'],None)
        self.context['scope_hash']='b'*64
        pilot_actions.rollback(self.app,self.tx['id'],None)
        self.assertEqual(b'old WIP\r\n',(self.root/'main.py').read_bytes())
        self.assertFalse((self.root/'future.py').exists())

    def test_b_test_without_successor_binding_cannot_prepare(self):
        self.stage_b();job=self.store.job(self.btest['id']);job['result'].pop('successor_binding')
        self.store.update_job(job['id'],result=job['result'])
        with self.assertRaises(ValueError):pilot_actions.prepare(self.app,job['id'])

    def test_changed_a_after_b_blocks_verification(self):
        self.applied_b();(self.root/'main.py').write_text('foreign')
        self.assertFalse(verify(self.app,self.btx['id'])['evidence_usable'])

    def test_newer_a_test_invalidates_b_verification(self):
        self.applied_b()
        job=self.store.create_job('stage_test',None,dict(stage_job_id=self.source['id']))
        self.store.update_job(job['id'],status='failed')
        self.assertFalse(verify(self.app,self.btx['id'])['evidence_usable'])

    def test_wrong_step_cannot_borrow_successor_consent(self):
        from governor_workbench.change_execution import resolve
        request=self.successor();request['step_id']='fix'
        with self.assertRaises(ValueError):resolve(self.app,request,self.context)

    def test_unconfirmed_b_rollback_cannot_reactivate_h1_consent(self):
        self.applied_b();pilot_actions.rollback(self.app,self.btx['id'],None)
        self.context['scope_hash']='b'*64
        from governor_workbench.change_successor import require_current
        with self.assertRaises(ValueError):require_current(self.app,self.consent['id'])

    def runner(self):
        import queue
        import threading
        from types import SimpleNamespace
        from governor_workbench.jobs import JobRunner
        self.app.config.update(router_url='http://127.0.0.1:3000/v1',model_timeout=120,
                               router_api_key_env='UNUSED_TEST_KEY',orchestrator_transport='router')
        self.app.settings=lambda:{'supervisor':'gpt-6-astra'}
        self.app.event=lambda *args:None
        self.app.questions=SimpleNamespace(answers=lambda key:[])
        self.context.update(intake={},decision_hash='d'*64)
        runner=object.__new__(JobRunner);runner.app=self.app;runner.lock=threading.Lock()
        runner.pending=queue.Queue();runner.cancellations={}
        return runner

    def test_b_proposal_worker_keeps_original_and_effective_binding(self):
        import threading
        from unittest.mock import patch
        request=self.successor();runner=self.runner()
        job=runner.submit('scope_patch',scope_kind='project',scope_id='pilot',candidate_id=self.candidate['id'],
                          step_id='next',successor_consent_id=self.consent['id'])
        with patch('governor_workbench.jobs.RouterClient'),patch('governor_workbench.patch_llm.propose_patch',
                return_value=dict(patch=dict(files=[dict(path='future.py',content='second\n')]),review=self.review)):
            result=runner.execute(job,'gpt-6-astra',threading.Event())
        self.assertIn('stage',result);self.assertFalse(result['stale'])
        self.assertEqual('b'*64,result['scope_hash'])
        self.assertEqual(self.consent['id'],job['request']['successor_consent_id'])
        self.assertEqual('a'*64,self.book.get(self.candidate['id'])['scope_hash'])

    def test_b_stage_test_worker_binds_own_fresh_test(self):
        import threading
        from unittest.mock import patch
        self.stage_b();runner=self.runner()
        job=self.store.create_job('stage_test',None,dict(stage_job_id=self.bsource['id']))
        with patch('governor_workbench.jobs.RouterClient'),patch('governor_workbench.staged_tests.run_staged_tests',return_value=copy.deepcopy(self.result)),patch('governor_workbench.post_test_review.review_staged',return_value=dict(verified=True,review=self.review)):
            result=runner.execute(job,'gpt-6-astra',threading.Event())
        self.assertTrue(result['verified']);self.assertTrue(result['success'])
        self.assertEqual(self.consent['id'],result['successor_binding']['successor_consent_id'])
        self.assertEqual('b'*64,result['scope_hash'])

    def test_model_transport_rechecks_h1_before_every_call(self):
        from unittest.mock import Mock
        from governor_workbench.change_execution import GuardedClient
        request=self.successor();transport=Mock()
        source=self.store.create_job('scope_patch',None,request)
        self.store.update_job(source['id'],status='completed')
        guard=GuardedClient(transport,self.app,request,source['id'])
        (self.root/'future.py').write_text('foreign')
        with self.assertRaises(ValueError):guard.call('gpt-6-astra','fixture')
        transport.call.assert_not_called()

    def test_b_proposal_missing_consent_remains_blocked(self):
        self.successor();runner=self.runner()
        with self.assertRaises(ValueError):
            runner.submit('scope_patch',scope_kind='project',scope_id='pilot',candidate_id=self.candidate['id'],step_id='next')

    def test_a_selection_change_after_b_apply_invalidates_closure(self):
        self.applied_b();self.context['scope_hash']='a'*64
        self.book.approve(self.candidate['id'],'a'*64,self.context,['fix','next'],'sequence')
        self.context['scope_hash']='c'*64
        self.assertFalse(verify(self.app,self.btx['id'])['evidence_usable'])

    def test_newer_failed_b_proposal_blocks_old_apply_before_writes(self):
        p=self.stage_b()
        request=self.store.job(self.bsource['id'])['request']
        newer=self.store.create_job('scope_patch',None,request)
        self.store.update_job(newer['id'],status='failed')
        with self.assertRaises(ValueError):pilot_actions.execute(self.app,p['id'],p['proposal_hash'],None)
        self.assertFalse((self.root/'future.py').exists())

    def test_newer_b_proposal_blocks_old_test_before_runner(self):
        import threading
        from unittest.mock import patch
        self.stage_b();runner=self.runner()
        newer=self.store.create_job('scope_patch',None,self.store.job(self.bsource['id'])['request'])
        self.store.update_job(newer['id'],status='cancelled')
        job=self.store.create_job('stage_test',None,dict(stage_job_id=self.bsource['id']))
        with patch('governor_workbench.staged_tests.run_staged_tests') as run,self.assertRaises(ValueError):
            runner.execute(job,'gpt-6-astra',threading.Event())
        run.assert_not_called()

    def test_newer_b_proposal_blocks_old_model_transport(self):
        from unittest.mock import Mock
        from governor_workbench.change_execution import GuardedClient
        self.stage_b();request=self.store.job(self.bsource['id'])['request'];transport=Mock()
        newer=self.store.create_job('scope_patch',None,request);self.store.update_job(newer['id'],status='failed')
        with self.assertRaises(ValueError):GuardedClient(transport,self.app,request,self.bsource['id']).call('gpt-6-astra','fixture')
        transport.call.assert_not_called()
