import copy
import sqlite3
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor

from tests import test_sequences
from governor_workbench.evidence import fingerprint
from governor_workbench.store import Store, JobBusy
from governor_workbench.sequence_store import SequenceJournal


class SequenceJournalTests(unittest.TestCase):
    def setUp(self):
        test_sequences.SequencePreviewTests.setUp(self)
        from governor_workbench.sequences import preview
        self.binding=preview(self.app,self.source['id'])['binding']
        self.journal=SequenceJournal(self.store)

    def start(self,journal=None):
        return (journal or self.journal).start(self.binding,fingerprint(self.binding),'Explicit fixture sequence')

    def finish(self,sequence,result=None,current=True):
        self.journal.begin_child(sequence['id'],sequence['current_job_id'])
        return self.journal.finish_child(sequence['id'],sequence['current_job_id'],'completed',
            result or {'success':True,'verified':True},evidence_current=current)

    def test_atomic_start_and_identical_retry(self):
        value=self.start();again=self.start()
        self.assertEqual(value,again)
        self.assertEqual('testing',value['status'])
        job=self.store.job(value['current_job_id'])
        self.assertEqual('stage_test',job['action'])
        self.assertEqual({'stage_job_id':self.source['id']},job['request'])
        with self.assertRaises(JobBusy):self.store.create_job('refresh',None)
        with self.assertRaises(ValueError):
            self.journal.start(self.binding,fingerprint(self.binding),'different consent')

    def test_exact_two_children_and_terminal_halt(self):
        first=self.start();second=self.finish(first)
        self.assertEqual('assessing',second['status'])
        job=self.store.job(second['current_job_id'])
        self.assertEqual('pilot_assess',job['action'])
        self.assertEqual({'verified_test_job_id':first['current_job_id']},job['request'])
        self.store.require_latest_stage_test(first['current_job_id'],self.source['id'])
        end=self.finish(second,{'success':True,'pilot_assessment':{'evidence_usable':True}})
        self.assertEqual('awaiting_transfer_decision',end['status'])
        self.assertEqual(2,len(end['children']))
        self.assertEqual(end,self.start())
        self.store.create_job('refresh',None)
        with self.assertRaises(ValueError):self.finish(second)

    def test_failed_evidence_never_creates_followup(self):
        value=self.start();end=self.finish(value,current=False)
        self.assertEqual('blocked',end['status']);self.assertEqual(1,len(end['children']))

    def test_cancel_queued_child_is_terminal_and_not_replayed(self):
        value=self.start();end=self.journal.cancel(value['id'])
        self.assertEqual('cancelled',end['status'])
        self.assertEqual('cancelled',self.store.job(value['current_job_id'])['status'])
        self.assertEqual(end,self.start())
        with self.assertRaises(ValueError):self.journal.begin_child(value['id'],value['current_job_id'])
        self.store.create_job('refresh',None)

    def test_cancel_running_child_retains_reservation_until_finish(self):
        value=self.start();self.journal.begin_child(value['id'],value['current_job_id'])
        pending=self.journal.cancel(value['id'])
        self.assertTrue(pending['cancel_requested']);self.assertEqual('testing',pending['status'])
        with self.assertRaises(JobBusy):self.store.create_job('refresh',None)
        end=self.journal.finish_child(value['id'],value['current_job_id'],'completed',
            {'success':True,'verified':True},evidence_current=True)
        self.assertEqual('cancelled',end['status']);self.assertEqual(1,len(end['children']))

    def test_restart_interrupts_reservation_and_owned_queued_child(self):
        value=self.start()
        restarted=Store(self.store.path)
        end=SequenceJournal(restarted).get(value['id'])
        self.assertEqual('interrupted',end['status'])
        self.assertEqual('interrupted',restarted.job(value['current_job_id'])['status'])
        self.assertEqual(1,len(end['children']))
        self.assertEqual(end,self.start(SequenceJournal(restarted)))
        restarted.create_job('refresh',None)

    def test_concurrent_start_on_independent_connections_creates_one_child(self):
        other=copy.copy(self.store);other.lock=threading.RLock()
        barrier=threading.Barrier(2)
        def create(store):
            barrier.wait();return self.start(SequenceJournal(store))
        with ThreadPoolExecutor(2) as pool:
            values=list(pool.map(create,[self.store,other]))
        self.assertEqual(values[0]['id'],values[1]['id'])
        self.assertEqual(1,len(values[0]['children']))

    def test_cancel_racing_finish_does_not_leave_runnable_followup(self):
        value=self.start();self.journal.begin_child(value['id'],value['current_job_id'])
        other=copy.copy(self.store);other.lock=threading.RLock();barrier=threading.Barrier(2)
        def cancel():barrier.wait();return SequenceJournal(other).cancel(value['id'])
        def finish():
            barrier.wait()
            return self.journal.finish_child(value['id'],value['current_job_id'],'completed',
                {'success':True,'verified':True},evidence_current=True)
        with ThreadPoolExecutor(2) as pool:
            pending=[pool.submit(cancel),pool.submit(finish)]
            for task in pending:task.result()
        end=self.journal.get(value['id'])
        self.assertEqual('cancelled',end['status'])
        for child in end['children']:
            self.assertNotIn(self.store.job(child['job_id'])['status'],('queued','running'))

    def test_immutable_consent_events_and_children(self):
        value=self.start()
        for statement in ("UPDATE sequence_runs SET note='tamper'",'DELETE FROM sequence_events',
                          'DELETE FROM sequence_children',"UPDATE sequence_children SET ordinal=9"):
            with self.subTest(statement=statement), self.assertRaises(sqlite3.IntegrityError):
                with self.store.db() as db:db.execute(statement)
        self.assertEqual(value,self.journal.get(value['id']))

    def test_reservation_still_blocks_between_terminal_child_and_controller(self):
        value=self.start();self.store.update_job(value['current_job_id'],status='failed')
        with self.assertRaises(JobBusy):self.store.create_job('hybrid_review',None)
        self.journal.cancel(value['id'])
        self.store.create_job('refresh',None)

    def test_child_creation_failure_rolls_back_start(self):
        with self.store.db() as db:
            db.execute("CREATE TRIGGER fail_fixture BEFORE INSERT ON sequence_children BEGIN SELECT RAISE(ABORT,'fixture'); END")
        before=self.store.jobs()
        with self.assertRaises(sqlite3.IntegrityError):self.start()
        self.assertEqual(before,self.store.jobs())
        with self.store.db() as db:self.assertEqual(0,db.execute('SELECT count(*) FROM sequence_runs').fetchone()[0])

    def test_bad_binding_and_active_foreign_job_rejected(self):
        with self.assertRaises(ValueError):self.journal.start(self.binding,'0'*64,'note')
        self.store.create_job('refresh',None)
        with self.assertRaises(JobBusy):self.start()

    def test_waiting_question_cannot_resume_through_reservation(self):
        from governor_workbench.operator_questions import OperatorQuestions
        questions=OperatorQuestions(self.store)
        job=self.store.create_job('scope_plan',None,{'scope_kind':'project','scope_id':'pilot'})
        self.store.update_job(job['id'],status='running')
        q=questions.ask(job['id'],{'text':'Which?','reason':'Fixture'},'a'*64,'project','pilot','gpt-6-astra')
        value=self.start()
        self.store.update_job(value['current_job_id'],status='completed')
        with self.assertRaises(JobBusy):questions.answer(q['id'],'Fixture','a'*64,'a'*64)
        self.assertEqual('pending',questions.get(q['id'])['status'])
        self.assertEqual('waiting_for_operator',self.store.job(job['id'])['status'])

    def test_failed_child_and_negative_assessment_stop(self):
        value=self.start();self.journal.begin_child(value['id'],value['current_job_id'])
        end=self.journal.finish_child(value['id'],value['current_job_id'],'failed',{'success':False})
        self.assertEqual('failed',end['status']);self.assertEqual(1,len(end['children']))

    def test_assessment_requires_boolean_positive_evidence(self):
        second=self.finish(self.start())
        end=self.finish(second,{'success':True,'pilot_assessment':{'evidence_usable':1}})
        self.assertEqual('blocked',end['status']);self.assertEqual(2,len(end['children']))

    def test_restart_after_transition_does_not_repeat_test_or_assessment(self):
        second=self.finish(self.start())
        self.journal.begin_child(second['id'],second['current_job_id'])
        restarted=Store(self.store.path)
        end=SequenceJournal(restarted).get(second['id'])
        self.assertEqual('interrupted',end['status'])
        self.assertEqual('completed',restarted.job(end['children'][0]['job_id'])['status'])
        self.assertEqual('interrupted',restarted.job(end['children'][1]['job_id'])['status'])
        self.assertEqual(2,len(end['children']))

    def test_second_child_failure_rolls_back_parent_and_predecessor(self):
        value=self.start();self.journal.begin_child(value['id'],value['current_job_id'])
        with self.store.db() as db:
            db.execute("CREATE TRIGGER fail_followup BEFORE INSERT ON sequence_children WHEN NEW.ordinal=1 BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.journal.finish_child(value['id'],value['current_job_id'],'completed',
                {'success':True,'verified':True},evidence_current=True)
        self.assertEqual('running',self.store.job(value['current_job_id'])['status'])
        self.assertEqual('testing',self.journal.get(value['id'])['status'])
        self.assertEqual(1,len(self.journal.get(value['id'])['children']))

    def test_plain_job_racing_sequence_has_only_one_winner(self):
        other=copy.copy(self.store);other.lock=threading.RLock();barrier=threading.Barrier(2)
        def create(sequence):
            barrier.wait()
            try:return self.start() if sequence else other.create_job('refresh',None)
            except JobBusy:return None
        with ThreadPoolExecutor(2) as pool:values=list(pool.map(create,[True,False]))
        self.assertEqual(1,sum(value is not None for value in values))
        self.assertEqual(1,len([j for j in self.store.jobs() if j['status']=='queued']))

    def test_newer_test_since_preview_blocks_admission(self):
        newer=self.store.create_job('stage_test',None,{'stage_job_id':self.source['id']})
        self.store.update_job(newer['id'],status='failed')
        with self.assertRaises(ValueError):self.start()

    def test_jobrunner_and_automatic_review_respect_reserved_gap(self):
        import queue
        from governor_workbench.jobs import JobRunner
        from governor_workbench.server import Application
        value=self.start();self.store.update_job(value['current_job_id'],status='failed')
        runner=object.__new__(JobRunner);runner.app=self.app;runner.lock=threading.Lock()
        runner.pending=queue.Queue();runner.cancellations={};self.app.runner=runner
        for action in ('refresh','hybrid_review','model_check','hermes_check'):
            with self.subTest(action=action),self.assertRaises(JobBusy):runner.submit(action)
        with self.assertRaises(JobBusy):runner.submit_runtime('runtime_check',{'instance_id':'f'*32})
        with self.assertRaises(JobBusy):runner.submit_pilot('pilot_assess',{'verified_test_job_id':'f'*32})
        self.settings['auto_review']=True
        self.app.config.update(auto_review_cooldown=900,auto_review_daily_limit=4)
        self.store.set_setting('_last_auto_evidence','older')
        before=self.store.settings()
        Application.auto_review(self.app,{'evidence_complete':True,'evidence_hash':'b'*64})
        self.assertEqual(before,self.store.settings())
        self.assertTrue(runner.pending.empty());self.assertFalse(runner.cancellations)
