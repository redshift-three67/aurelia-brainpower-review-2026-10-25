import queue
import threading
import unittest
from unittest.mock import patch
from tests import test_test_chains
from governor_workbench.jobs import JobRunner
from governor_workbench.test_chain_store import TestChainJournal


class TestChainControllerTests(unittest.TestCase):
    preview=test_test_chains.TestChainPreviewTests.preview

    def setUp(self):
        test_test_chains.TestChainPreviewTests.setUp(self)
        self.app.bump=lambda:None;self.app.event=lambda *a:None
        self.app.settings=lambda:dict(supervisor='gpt-6-astra')
        self.runner=object.__new__(JobRunner);self.runner.app=self.app
        self.runner.lock=threading.Lock();self.runner.pending=queue.Queue();self.runner.cancellations={}
        self.journal=TestChainJournal(self.store)

    def start(self):
        p=self.preview()
        return self.runner.submit_test_chain(dict(candidate_id=self.candidate['id'],step_ids=['second','test'],binding_hash=p['binding_hash'],note='Explicit chain'))

    def run_next(self):
        job,supervisor=self.runner.pending.get_nowait()
        self.runner.test_chain_child(job,supervisor,self.runner.cancellations[job['id']])
        self.runner.pending.task_done()
        return job

    def test_real_dependent_tests_complete_without_models_or_source_writes(self):
        original=(self.root/'tests/test_ok.py').read_bytes()
        with patch('governor_workbench.jobs.RouterClient') as models:
            row=self.start();first=self.run_next()
            interim=self.journal.get(row['id']);self.assertEqual(2,len(interim['children']))
            self.assertEqual('completed',self.store.job(first['id'])['status'])
            self.run_next();models.assert_not_called()
        self.assertEqual('completed',self.journal.get(row['id'])['status'])
        self.assertTrue(self.runner.pending.empty())
        self.assertEqual(original,(self.root/'tests/test_ok.py').read_bytes())
        rows=self.book.dependency_report(self.candidate['id'],self.context)['steps']
        self.assertTrue(all(r['completion_status']=='accepted' for r in rows))

    def test_file_drift_blocks_before_execution(self):
        row=self.start();(self.root/'tests/test_ok.py').write_text('drift')
        with patch.object(self.runner,'execute') as execute:self.run_next();execute.assert_not_called()
        self.assertEqual('blocked',self.journal.get(row['id'])['status']);self.assertTrue(self.runner.pending.empty())

    def test_failed_test_never_dispatches_next(self):
        (self.root/'tests/test_ok.py').write_text('import unittest\nclass Test(unittest.TestCase):\n def test_fail(self): self.fail()\n')
        row=self.start();self.run_next()
        self.assertEqual('failed',self.journal.get(row['id'])['status']);self.assertTrue(self.runner.pending.empty())

    def test_cancel_before_worker_starts(self):
        row=self.start();self.runner.cancel_test_chain(row['id']);self.run_next()
        self.assertEqual('cancelled',self.journal.get(row['id'])['status'])

    def test_withdrawal_after_first_blocks_second(self):
        row=self.start();self.run_next()
        self.book.withdraw_completion(self.candidate['id'],'before',self.before['id'],'Withdraw')
        self.run_next();self.assertEqual('blocked',self.journal.get(row['id'])['status'])

    def test_zero_and_only_skipped_tests_never_continue(self):
        for source in ('import unittest\n', 'import unittest\nclass Test(unittest.TestCase):\n @unittest.skip("skip")\n def test_skip(self): pass\n'):
            with self.subTest(source=source):
                (self.root/'tests/test_ok.py').write_text(source)
                self.selection=self.book.approve(self.candidate['id'],'a'*64,self.context,['before','test','second'],'sequence')
                self.before=self.book.complete_step(self.candidate['id'],'before',self.context,'a'*64,self.selection['id'],'Reviewed')
                row=self.start();self.run_next()
                self.assertEqual('failed',self.journal.get(row['id'])['status']);self.assertTrue(self.runner.pending.empty())

    def test_drift_after_adapter_preserves_output_but_blocks_receipt(self):
        row=self.start();execute=self.runner.execute
        def changed(*args):
            result=execute(*args);(self.root/'tests/test_ok.py').write_text('drift');return result
        with patch.object(self.runner,'execute',side_effect=changed):job=self.run_next()
        result=self.store.job(job['id'])['result']
        self.assertFalse(result['success']);self.assertTrue(result['stale']);self.assertIn('test_evidence',result)
        self.assertEqual('blocked',self.journal.get(row['id'])['status']);self.assertTrue(self.runner.pending.empty())

    def test_cancel_during_adapter(self):
        row=self.start();execute=self.runner.execute
        def cancelled(*args):
            result=execute(*args);self.runner.cancel_test_chain(row['id']);return result
        with patch.object(self.runner,'execute',side_effect=cancelled):self.run_next()
        self.assertEqual('cancelled',self.journal.get(row['id'])['status']);self.assertTrue(self.runner.pending.empty())

    def test_reselection_and_adapter_drift_block(self):
        row=self.start()
        self.book.approve(self.candidate['id'],'a'*64,self.context,['before','test','second'],'sequence')
        with patch.object(self.runner,'execute') as execute:self.run_next();execute.assert_not_called()
        self.assertEqual('blocked',self.journal.get(row['id'])['status'])

    def test_cancel_in_reserved_receipt_phase_does_not_allocate_next(self):
        row=self.start()
        from governor_workbench import test_chains
        validate=test_chains.validate
        def cancel_at_check(app,value):
            validate(app,value)
            if value['status']=='checking':self.journal.cancel(value['id'])
        with patch('governor_workbench.test_chains.validate',side_effect=cancel_at_check):self.run_next()
        self.assertEqual('cancelled',self.journal.get(row['id'])['status']);self.assertTrue(self.runner.pending.empty())

    def test_branched_three_test_chain(self):
        import copy
        steps=copy.deepcopy(self.candidate['proposal']['steps'])
        steps.insert(2,dict(steps[1],id='parallel'))
        steps[-1]['depends_on']=['test','parallel']
        self.candidate=self.book.save_candidate(self.context,dict(summary='Branch',steps=steps),self.candidate['review'],'fixture')
        self.selection=self.book.approve(self.candidate['id'],'a'*64,self.context,['before','test','parallel','second'],'sequence')
        self.book.complete_step(self.candidate['id'],'before',self.context,'a'*64,self.selection['id'],'Reviewed')
        p=self.preview(['second','parallel','test'])
        row=self.runner.submit_test_chain(dict(candidate_id=self.candidate['id'],step_ids=['second','parallel','test'],binding_hash=p['binding_hash'],note='Branch'))
        for _ in range(3):self.run_next()
        result=self.journal.get(row['id']);self.assertEqual('completed',result['status'])
        self.assertEqual(['test','parallel','second'],[c['step_id'] for c in result['children']])

    def test_missing_receipt_stops_successful_looking_result(self):
        row=self.start()
        with patch.object(self.runner,'execute',return_value={'success':True}):self.run_next()
        self.assertEqual('blocked',self.journal.get(row['id'])['status']);self.assertTrue(self.runner.pending.empty())

    def test_adapter_drift_blocks_before_execute(self):
        row=self.start()
        with patch('governor_workbench.test_chains.adapter_hash',return_value='b'*64),patch.object(self.runner,'execute') as execute:
            self.run_next();execute.assert_not_called()
        self.assertEqual('blocked',self.journal.get(row['id'])['status'])

    def test_retry_outside_visible_history_does_not_replay(self):
        p=self.preview();values=dict(candidate_id=self.candidate['id'],step_ids=['test','second'],binding_hash=p['binding_hash'],note='Old consent')
        row=self.runner.submit_test_chain(values);self.runner.cancel_test_chain(row['id']);self.run_next()
        with self.store.db() as db:
            for i in range(41):
                db.execute("INSERT INTO test_chain_runs(id,activation,binding_hash,binding,note,created_at,status) VALUES(?,?,?,?,?,?,?)",
                           (str(i),str(i),'other','{}','fixture','fixture','cancelled'))
        again=self.runner.submit_test_chain(values)
        self.assertEqual(row['id'],again['id']);self.assertTrue(self.runner.pending.empty())
