"""Worker and application-state regressions; temporary fixtures, no models."""
import json
import sqlite3
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from governor_workbench import pilot_actions
from governor_workbench.jobs import JobRunner
from governor_workbench.pilot_apply import PilotApply
from governor_workbench.server import Application
from governor_workbench.store import Store
from tests import test_pilot_actions as fixtures


class PilotJobReceiptTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.PilotActionsTests()
        self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.app=self.fixture.app
        self.app.stop_event=threading.Event()
        self.app.bump=lambda:None
        self.app.settings=lambda:dict(supervisor='gpt-5.6-sol',reasoning_mode='medium',monitor_enabled=False,auto_review=False)
        self.finished=threading.Event()
        def event(level,source,message,job_id=None):
            self.app.store.event(level,source,message,job_id)
            if source=='governor' and job_id: self.finished.set()
        self.app.event=event
        self.runner=JobRunner(self.app)
        self.addCleanup(self.stop_worker)

    def stop_worker(self):
        self.app.stop_event.set(); self.runner.thread.join(3)
        self.assertFalse(self.runner.thread.is_alive())

    def run_job(self,action,request):
        self.finished.clear()
        job=self.runner.submit_pilot(action,request)
        self.assertTrue(self.finished.wait(6),'Worker did not publish its final status')
        self.assertTrue(self.runner.thread.is_alive(),'Worker must survive the operation')
        return self.app.store.job(job['id'])

    def test_write_failure_keeps_original_error_and_unknown_receipt(self):
        proposal=self.fixture.prepare(); original=PilotApply._replace
        def fail(pilot,root,path,data,expected):
            original(pilot,root,path,data,expected)
            (root/path).write_bytes(b'external after replace')
            raise OSError('injected failure')
        with patch.object(PilotApply,'_replace',fail):
            job=self.run_job('pilot_apply',dict(proposal_id=proposal['id'],proposal_hash=proposal['proposal_hash']))
        self.assertEqual('failed',job['status'])
        self.assertIn('Apply fehlgeschlagen',job['error'])
        self.assertFalse(job['result']['success'])
        self.assertIsNone(job['result']['product_files_changed'])
        self.assertEqual('unknown_requires_inspection',job['result']['file_state'])
        self.assertEqual('recovery_needed',job['result']['pilot_transaction']['status'])
        self.assertEqual(b'external after replace',(self.fixture.root/'main.py').read_bytes())

    def test_completed_apply_with_late_cancellation_stays_completed(self):
        proposal=self.fixture.prepare(); original=PilotApply._replace
        def cancel_after_write(pilot,root,path,data,expected):
            original(pilot,root,path,data,expected)
            for event in self.runner.cancellations.values(): event.set()
        with patch.object(PilotApply,'_replace',cancel_after_write):
            job=self.run_job('pilot_apply',dict(proposal_id=proposal['id'],proposal_hash=proposal['proposal_hash']))
        self.assertEqual('completed',job['status'])
        self.assertIsNone(job['error'])
        self.assertEqual('completed',job['result']['pilot_transaction']['status'])
        self.assertEqual(b'new\n',(self.fixture.root/'main.py').read_bytes())

    def test_completed_rollback_with_late_cancellation_stays_completed(self):
        tx=self.fixture.execute(self.fixture.prepare()); original=PilotApply._replace
        def cancel_after_write(pilot,root,path,data,expected):
            original(pilot,root,path,data,expected)
            for event in self.runner.cancellations.values(): event.set()
        with patch.object(PilotApply,'_replace',cancel_after_write):
            job=self.run_job('pilot_rollback',dict(transaction_id=tx['id']))
        self.assertEqual('completed',job['status'])
        self.assertEqual('rolled_back',job['result']['pilot_transaction']['status'])
        self.assertEqual(b'old WIP\r\n',(self.fixture.root/'main.py').read_bytes())

    def test_receipt_lookup_database_failure_preserves_original_worker_error(self):
        proposal=self.fixture.prepare()
        with patch.object(pilot_actions,'execute',side_effect=ValueError('original apply failure')):
            with patch.object(pilot_actions,'recovery_receipt',side_effect=sqlite3.OperationalError('receipt query unavailable')):
                job=self.run_job('pilot_apply',dict(proposal_id=proposal['id'],proposal_hash=proposal['proposal_hash']))
        self.assertEqual('failed',job['status'])
        self.assertEqual('original apply failure',job['error'])

    def test_application_state_exposes_unresolved_transaction_after_restart_and_job_truncation(self):
        tx=self.fixture.execute(self.fixture.prepare())
        self.stop_worker()
        with self.app.store.db() as db:
            tx['status']='running'  # Simulate durable intent left by an uncatchable process exit.
            db.execute('UPDATE pilot_apply_transactions SET status=?,body=? WHERE id=?',('running',json.dumps(tx),tx['id']))
        for _ in range(45):
            item=self.app.store.create_job('refresh',None)
            self.app.store.update_job(item['id'],status='completed',result={'success':True})
        self.app.store=Store(self.app.store.path)
        self.app.lock=threading.RLock(); self.app.observation=dict(observed_at=None,projects=[],evidence_hash='')
        self.app.health={}; self.app.last_error=None; self.app.scope_cache={}; self.app.csrf='fixture'
        self.app.config.update(monitor_interval=15,git_interval=60,hermes_path='missing-fixture-hermes',
            orchestrator='gpt-5.6-terra',orchestrator_transport='router')
        self.app.governance=lambda *args:dict(projects=[])
        self.app.live_state=lambda:[]
        self.app.questions=SimpleNamespace(list=lambda **kwargs:[])
        self.app.scope_monitor=SimpleNamespace(state=lambda:{})
        self.app.runtime_profiles=SimpleNamespace(state=lambda:{'profiles':[],'instances':[]})
        self.app.registry.list_groups=lambda:[]
        state=Application.state(self.app)
        self.assertEqual(40,len(state['jobs']))
        self.assertNotIn(self.fixture.source['id'],[job['id'] for job in state['jobs']])
        self.assertEqual(tx['id'],state['pilot_transactions'][0]['id'])
        self.assertEqual('running',state['pilot_transactions'][0]['status'])
        self.assertEqual('running',pilot_actions.transaction_snapshot(self.app)[0]['status'])
