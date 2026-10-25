import queue
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock,MagicMock,patch
from governor_workbench.jobs import JobRunner


class RepairSubmissionTests(unittest.TestCase):
    def setUp(self):
        self.binding=dict(source_job_id='b'*32,source_evidence_hash='c'*64,diagnostic_adapter_hash='d'*64,
            candidate_id='e'*32,step_id='test',scope_hash='f'*64,selection_id='1'*32,paths=['test.py'])
        self.diagnosis=dict(action='plan_failure',status='completed',result={'test_failure':dict(self.binding,evidence_usable=True)})
        store=MagicMock();store.job.return_value=self.diagnosis
        store.create_job.side_effect=lambda action,project,request:dict(id='2'*32,action=action,request=request,status='queued')
        self.app=SimpleNamespace(store=store,config=dict(orchestrator_transport='router',router_url='http://127.0.0.1:3000/v1',model_timeout=120,router_api_key_env='TEST_KEY'),
            settings=lambda:dict(supervisor='gpt-6-astra',reasoning_mode='medium'),scope_context=Mock(return_value=dict(scope_hash='f'*64)))
        self.runner=JobRunner.__new__(JobRunner);self.runner.app=self.app
        self.runner.lock=threading.RLock();self.runner.pending=queue.Queue();self.runner.cancellations={}
        self.candidate=dict(id='e'*32,scope_kind='project',scope_id='pilot')
        self.values=dict(diagnosis_job_id='a'*32,note='Explicit repair planning')

    def submit(self):
        with patch('governor_workbench.plans.PlanBook') as book,patch('governor_workbench.repair_planning.attempts'):
            book.return_value.get.return_value=self.candidate
            return self.runner.submit_repair_plan(self.values)

    def test_enqueue_binds_saved_diagnosis_without_git_or_model_work(self):
        with patch('governor_workbench.repair_planning.prepare',side_effect=AssertionError('Fresh validation belongs to worker')) as prepare:
            job=self.submit()
        prepare.assert_not_called();self.app.scope_context.assert_not_called()
        self.assertEqual(self.binding,job['request']['repair_binding'])
        self.assertEqual('pilot',job['request']['scope_id'])
        self.assertEqual((job,'gpt-6-astra'),self.runner.pending.get_nowait())

    def test_invalid_diagnosis_is_not_enqueued(self):
        self.diagnosis['status']='failed'
        with self.assertRaises(ValueError):self.submit()
        self.app.store.create_job.assert_not_called()

    def test_worker_fresh_validation_failure_prevents_model_call(self):
        job=self.submit()
        with patch('governor_workbench.repair_planning.prepare',side_effect=ValueError('source drift')) as prepare,patch('governor_workbench.jobs.RouterClient') as client:
            with self.assertRaisesRegex(ValueError,'source drift'):
                self.runner.execute(job,'gpt-6-astra',threading.Event())
            prepare.assert_called_once();client.return_value.call.assert_not_called()

    def test_worker_rejects_changed_binding_before_model_call(self):
        job=self.submit()
        with patch('governor_workbench.repair_planning.prepare',return_value=({},dict(self.binding,source_evidence_hash='0'*64))),patch('governor_workbench.jobs.RouterClient') as client:
            with self.assertRaisesRegex(ValueError,'Reparaturgrundlage geändert'):
                self.runner.execute(job,'gpt-6-astra',threading.Event())
            client.return_value.call.assert_not_called()

    def test_worker_permission_denial_prevents_validation_and_model_call(self):
        job=self.submit();self.app.scope_context.side_effect=ValueError('egress denied')
        with patch('governor_workbench.repair_planning.prepare') as prepare,patch('governor_workbench.jobs.RouterClient') as client:
            with self.assertRaisesRegex(ValueError,'egress denied'):
                self.runner.execute(job,'gpt-6-astra',threading.Event())
            prepare.assert_not_called();client.return_value.call.assert_not_called()
