from pathlib import Path
import tempfile
import unittest
from governor_workbench.store import Store, JobBusy


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'journal.db'
        self.store=Store(self.path)

    def test_duplicate_pending_job_rejected(self):
        self.store.create_job('hybrid_review','demo')
        with self.assertRaises(JobBusy): self.store.create_job('hybrid_review','demo')

    def test_restart_marks_unfinished_job_interrupted(self):
        job=self.store.create_job('refresh',None)
        self.store.update_job(job['id'],status='running')
        other=Store(self.path)
        self.assertEqual('interrupted',other.jobs()[0]['status'])

    def test_events_and_settings_persist(self):
        self.store.event('info','test','saved')
        self.store.set_setting('supervisor','gpt-6-astra')
        other=Store(self.path)
        self.assertEqual('gpt-6-astra',other.settings()['supervisor'])
        self.assertTrue(any(e['message']=='saved' for e in other.events()))

    def test_legacy_journal_upgrade_preserves_history(self):
        import sqlite3
        from contextlib import closing
        legacy=Path(self.tmp.name)/'legacy.db'
        with closing(sqlite3.connect(legacy)) as db, db:
            db.execute('CREATE TABLE jobs(id TEXT PRIMARY KEY,action TEXT,project_id TEXT,status TEXT,created_at TEXT,started_at TEXT,ended_at TEXT,error TEXT,result TEXT)')
            db.execute("INSERT INTO jobs(id,action,status,result) VALUES(?,?,?,?)",('a'*32,'refresh','completed','{"proof":"retained"}'))
            db.execute("INSERT INTO jobs(id,action,status) VALUES(?,?,?)",('b'*32,'refresh','running'))
        upgraded=Store(legacy)
        self.assertEqual({'proof':'retained'},upgraded.job('a'*32)['result'])
        self.assertEqual('completed',upgraded.job('a'*32)['status'])
        self.assertEqual('interrupted',upgraded.job('b'*32)['status'])
        with upgraded.db() as db:
            self.assertEqual(0,db.execute('SELECT count(*) FROM sequence_runs').fetchone()[0])

    def test_planned_module_dependency_validation(self):
        p=self.store.add_project('Future','description',['base'],['base'])
        self.assertEqual('planned',p['kind'])
        with self.assertRaises(ValueError): self.store.add_project('Another','',['unknown'],['base'])

if __name__=='__main__': unittest.main()
