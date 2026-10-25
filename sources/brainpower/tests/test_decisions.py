import tempfile
import unittest
from pathlib import Path
from governor_workbench.store import Store


class DecisionJournalTests(unittest.TestCase):
    def test_append_only_decisions_survive_restart(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'journal.db'; store=Store(path)
            a=store.add_decision({'step_id':'reconcile_sources','kind':'authorize','reason':'Operator request','actor':'operator','evidence_hash':'abc'})
            b=store.add_decision({'step_id':'reconcile_sources','kind':'revoke','reason':'Changed scope','actor':'operator','evidence_hash':'abc'})
            self.assertNotEqual(a['id'],b['id'])
            rows=Store(path).decisions()
            self.assertEqual(['authorize','revoke'],[x['kind'] for x in rows])
            self.assertEqual('Operator request',rows[0]['reason'])

    def test_job_step_payload_persisted_without_schema_break(self):
        with tempfile.TemporaryDirectory() as d:
            store=Store(Path(d)/'journal.db')
            job=store.create_job('governance_report',None,{'step_id':'reconcile_sources'})
            self.assertEqual('reconcile_sources',store.job(job['id'])['request']['step_id'])

    def test_test_evidence_survives_more_than_ten_other_jobs(self):
        with tempfile.TemporaryDirectory() as d:
            store=Store(Path(d)/'journal.db')
            test=store.create_job('radiworks_tests','radiworks')
            store.update_job(test['id'],status='completed',result={'summary':{'tests':205}})
            for _ in range(12):
                j=store.create_job('refresh',None); store.update_job(j['id'],status='completed')
            self.assertEqual(test['id'],store.jobs_for_action('radiworks_tests')[0]['id'])
