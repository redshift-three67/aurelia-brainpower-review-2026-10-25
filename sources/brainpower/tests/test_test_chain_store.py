import unittest
from tests import test_test_chains
from governor_workbench.store import Store, JobBusy


class TestChainStoreTests(unittest.TestCase):
    setUp=test_test_chains.TestChainPreviewTests.setUp
    preview=test_test_chains.TestChainPreviewTests.preview

    def journal(self):
        from governor_workbench.test_chain_store import TestChainJournal
        return TestChainJournal(self.store)

    def start(self):
        report=self.preview()
        self.assertTrue(report['eligible'],report)
        return self.journal().start(report['binding'],report['binding_hash'],'Explicit test')

    def test_reservation_idempotency_and_cancel(self):
        row=self.start();journal=self.journal()
        again=journal.start(row['binding'],row['binding_hash'],row['note'])
        self.assertEqual(row,again)
        self.assertEqual(1,len(row['children']))
        with self.assertRaises(JobBusy):self.store.create_job('model_check',None)
        with self.assertRaises(ValueError):journal.start(row['binding'],row['binding_hash'],'Other')
        cancelled=journal.cancel(row['id'])
        self.assertEqual('cancelled',cancelled['status'])
        self.assertEqual('cancelled',self.store.job(row['current_job_id'])['status'])
        self.assertEqual(cancelled,journal.start(row['binding'],row['binding_hash'],row['note']))
        self.store.create_job('model_check',None)

    def test_running_cancel_retains_reservation_until_finish(self):
        row=self.start();journal=self.journal();key=row['current_job_id']
        journal.begin_child(row['id'],key);journal.cancel(row['id'])
        with self.assertRaises(JobBusy):self.store.create_job('model_check',None)
        end=journal.finish_child(row['id'],key,'completed',{'success':True})
        self.assertEqual('cancelled',end['status']);self.assertEqual(1,len(end['children']))

    def test_restart_interrupts_without_replay(self):
        row=self.start();Store(self.store.path)
        self.assertEqual('interrupted',self.journal().get(row['id'])['status'])
        self.assertEqual('interrupted',self.store.job(row['current_job_id'])['status'])

    def test_atomic_budget_rejects_stale_binding(self):
        report=self.preview()
        for _ in range(3):
            j=self.store.create_job('plan_test',None,dict(candidate_id=self.candidate['id'],step_id='test'))
            self.store.update_job(j['id'],status='failed')
        with self.assertRaises(ValueError):self.journal().start(report['binding'],report['binding_hash'],'Explicit')
        self.assertEqual([],self.journal().list())

    def test_terminal_and_consent_are_immutable(self):
        import sqlite3
        row=self.start();self.journal().cancel(row['id'])
        for sql in ('UPDATE test_chain_runs SET note=\'bad\'','DELETE FROM test_chain_runs',
                    'DELETE FROM test_chain_children','DELETE FROM test_chain_events'):
            with self.assertRaises(sqlite3.IntegrityError):
                with self.store.db() as db:db.execute(sql)

    def test_checking_keeps_reservation_and_restart_interrupts(self):
        row=self.start();journal=self.journal();key=row['current_job_id'];journal.begin_child(row['id'],key)
        evidence=dict(success=True,sources_verified=True,completion_verified=True,exit_code=0,count=1,skipped=0,errors=0,failures=0)
        result=dict(success=True,test_evidence=dict(test=evidence),completion_receipt=dict(id='fixture'))
        checked=journal.finish_child(row['id'],key,'completed',result,evidence_current=True)
        self.assertEqual('checking',checked['status'])
        with self.assertRaises(JobBusy):self.store.create_job('model_check',None)
        Store(self.store.path)
        self.assertEqual('interrupted',journal.get(row['id'])['status'])
        self.assertEqual(1,len(journal.get(row['id'])['children']))

    def test_concurrent_identical_starts_create_one_child(self):
        from concurrent.futures import ThreadPoolExecutor
        p=self.preview()
        with ThreadPoolExecutor(max_workers=2) as pool:
            rows=list(pool.map(lambda _:self.journal().start(p['binding'],p['binding_hash'],'Concurrent'),range(2)))
        self.assertEqual(rows[0]['id'],rows[1]['id'])
        self.assertEqual(1,len(self.store.jobs()))

    def test_s1_reservation_blocks_s2_without_any_active_job(self):
        p=self.preview()
        with self.store.db() as db:
            db.execute("INSERT INTO sequence_runs(id,stage_job_id,binding_hash,binding,note,created_at,status) VALUES(?,?,?,?,?,?,?)",
                       ('b'*32,'c'*32,'d'*64,'{}','fixture','fixture','testing'))
        with self.assertRaises(JobBusy):self.journal().start(p['binding'],p['binding_hash'],'Explicit')
        self.assertEqual([],self.journal().list())
