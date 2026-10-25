import queue
import threading
import unittest
from unittest.mock import patch

from tests import test_sequences
from governor_workbench import sequences
from governor_workbench.jobs import JobRunner
from governor_workbench.sequence_store import SequenceJournal


class SequenceControllerTests(unittest.TestCase):
    def setUp(self):
        test_sequences.SequencePreviewTests.setUp(self)
        self.app.bump=lambda:None
        self.app.event=lambda *args:None
        self.runner=object.__new__(JobRunner)
        self.runner.app=self.app;self.runner.lock=threading.Lock()
        self.runner.pending=queue.Queue();self.runner.cancellations={}
        self.app.runner=self.runner
        self.journal=SequenceJournal(self.store)
        self.values=dict(stage_job_id=self.source['id'],binding_hash=sequences.preview(self.app,self.source['id'])['binding_hash'],note='Explicit test consent')

    def start(self):return self.runner.submit_sequence(self.values)

    def test_bound_start_retry_and_forged_fields(self):
        value=self.start();again=self.start()
        self.assertEqual(value['id'],again['id']);self.assertEqual(1,self.runner.pending.qsize())
        for values in (dict(self.values,note='changed'),dict(self.values,command='no'),dict(self.values,binding_hash='0'*64)):
            with self.assertRaises(ValueError):self.runner.submit_sequence(values)
        self.runner.cancel_sequence(value['id'])
        self.assertEqual('cancelled',self.journal.get(value['id'])['status'])
        self.assertEqual(value['id'],self.start()['id']);self.assertEqual(1,self.runner.pending.qsize())

    def test_drift_between_preview_and_start_rejected(self):
        self.settings['supervisor']='gpt-5.6-sol'
        with self.assertRaises(ValueError):self.start()
        self.assertTrue(self.runner.pending.empty())

    def test_owned_test_identity_and_fresh_binding(self):
        value=self.start();job=self.store.job(value['current_job_id'])
        sequences.validate_child(self.app,job)
        self.settings['supervisor']='gpt-5.6-sol'
        with self.assertRaises(ValueError):sequences.validate_child(self.app,job)

    def test_worker_drift_blocks_before_adapter(self):
        value=self.start();job,supervisor=self.runner.pending.get_nowait()
        self.settings['supervisor']='gpt-5.6-sol'
        with patch.object(self.runner,'execute') as execute:
            self.runner.sequence_child(job,supervisor,self.runner.cancellations[job['id']])
            execute.assert_not_called()
        self.assertEqual('blocked',self.journal.get(value['id'])['status'])

    def test_running_cancellation_stops_followup_and_preserves_result(self):
        value=self.start();job,supervisor=self.runner.pending.get_nowait()
        def execute(*args):
            self.runner.cancel(job['id'])
            return dict(success=True,verified=True,output='retained')
        with patch.object(self.runner,'execute',side_effect=execute):
            self.runner.sequence_child(job,supervisor,self.runner.cancellations[job['id']])
        self.assertEqual('cancelled',self.journal.get(value['id'])['status'])
        self.assertEqual('retained',self.store.job(job['id'])['result']['output'])
        self.assertTrue(self.runner.pending.empty())

    def test_guard_rechecks_at_actual_model_call(self):
        value=self.start();job=self.store.job(value['current_job_id'])
        self.journal.begin_child(value['id'],job['id'])
        from unittest.mock import Mock
        client=Mock();guard=sequences.GuardedClient(client,self.app,job)
        self.settings['supervisor']='gpt-5.6-sol'
        with self.assertRaises(ValueError):guard.call('gpt-6-astra','fixture')
        client.call.assert_not_called()

    def test_post_execution_drift_keeps_result_without_followup(self):
        value=self.start();job,supervisor=self.runner.pending.get_nowait()
        def execute(*args):
            self.context['scope_hash']='b'*64
            return dict(success=True,verified=True,output='actual tests')
        with patch.object(self.runner,'execute',side_effect=execute):
            self.runner.sequence_child(job,supervisor,self.runner.cancellations[job['id']])
        self.assertEqual('blocked',self.journal.get(value['id'])['status'])
        self.assertEqual('actual tests',self.store.job(job['id'])['result']['output'])
        self.assertFalse(self.store.job(job['id'])['result']['verified'])
        self.assertTrue(self.store.job(job['id'])['result']['stale'])
        self.assertTrue(self.runner.pending.empty())

    def test_queued_cancel_never_calls_adapter(self):
        value=self.start();job,supervisor=self.runner.pending.get_nowait()
        self.runner.cancel_sequence(value['id'])
        with patch.object(self.runner,'execute') as execute:
            self.runner.sequence_child(job,supervisor,self.runner.cancellations[job['id']])
            execute.assert_not_called()
        self.assertEqual('cancelled',self.journal.get(value['id'])['status'])

    def test_failed_tests_keep_evidence_and_do_not_assess(self):
        value=self.start();job,supervisor=self.runner.pending.get_nowait()
        with patch.object(self.runner,'execute',return_value=dict(success=False,verified=False,count=1,failures=1)):
            self.runner.sequence_child(job,supervisor,self.runner.cancellations[job['id']])
        self.assertEqual('failed',self.journal.get(value['id'])['status'])
        self.assertEqual(1,self.store.job(job['id'])['result']['failures'])
        self.assertTrue(self.runner.pending.empty())

    def assessment(self):
        value=self.start();job,supervisor=self.runner.pending.get_nowait()
        with patch.object(self.runner,'execute',return_value=dict(self.result)):
            self.runner.sequence_child(job,supervisor,self.runner.cancellations[job['id']])
        second,supervisor=self.runner.pending.get_nowait()
        return value,second,supervisor

    def test_negative_assessment_is_not_successful_sequence(self):
        value,job,supervisor=self.assessment()
        with patch.object(self.runner,'execute',return_value=dict(success=True,pilot_assessment={'evidence_usable':False})):
            self.runner.sequence_child(job,supervisor,self.runner.cancellations[job['id']])
        self.assertEqual('blocked',self.journal.get(value['id'])['status'])
        self.assertEqual('completed',self.store.job(job['id'])['status'])
        self.assertTrue(self.runner.pending.empty())

    def test_cancel_during_assessment_is_terminal(self):
        value,job,supervisor=self.assessment()
        def execute(*args):
            self.runner.cancel_sequence(value['id'])
            return dict(success=True,pilot_assessment={'evidence_usable':True})
        with patch.object(self.runner,'execute',side_effect=execute):
            self.runner.sequence_child(job,supervisor,self.runner.cancellations[job['id']])
        self.assertEqual('cancelled',self.journal.get(value['id'])['status'])
        self.assertTrue(self.runner.pending.empty())

    def test_reselection_before_model_egress_is_blocked(self):
        value=self.start();job=self.store.job(value['current_job_id'])
        self.journal.begin_child(value['id'],job['id'])
        self.book.approve(self.candidate['id'],'a'*64,self.context,['fix'])
        from unittest.mock import Mock
        client=Mock()
        with self.assertRaises(ValueError):sequences.GuardedClient(client,self.app,job).call('gpt-6-astra','fixture')
        client.call.assert_not_called()

    def test_model_egress_denial_preserves_reservation_until_blocked(self):
        value=self.start();job,supervisor=self.runner.pending.get_nowait()
        with patch.object(self.app,'scope_context',side_effect=ValueError('private path')),patch.object(self.runner,'execute') as execute:
            self.runner.sequence_child(job,supervisor,self.runner.cancellations[job['id']])
            execute.assert_not_called()
        self.assertEqual('blocked',self.journal.get(value['id'])['status'])
        self.assertNotIn('private path',str(self.store.job(job['id'])))

    def test_source_file_drift_before_send_blocks_model(self):
        value=self.start();job=self.store.job(value['current_job_id'])
        self.journal.begin_child(value['id'],job['id'])
        (self.root/'main.py').write_text('drift')
        from unittest.mock import Mock
        client=Mock()
        with self.assertRaises(ValueError):sequences.GuardedClient(client,self.app,job).call('gpt-6-astra','fixture')
        client.call.assert_not_called()
