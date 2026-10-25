import copy
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from governor_workbench.server import Application, Handler
from governor_workbench.evidence import fingerprint


class PlannedObservationTests(unittest.TestCase):
    def fixture(self):
        app=Application.__new__(Application)
        app.lock=threading.RLock();app.revision=0;app.last_error=None
        app.source_evidence_hash=''
        app.observation={'observed_at':None,'projects':[],'evidence_hash':''}
        app.store=SimpleNamespace(lock=threading.RLock(),planned=Mock(return_value=[]))
        raw=dict(observed_at='original time',projects=[],evidence_hash='a'*64,evidence_complete=False)
        app.observer=SimpleNamespace(scan=Mock(side_effect=lambda force:copy.deepcopy(raw)))
        app.event=Mock()
        return app

    def test_planning_rebinds_evidence_without_rescanning_or_promoting_sources(self):
        app=self.fixture();old=app.refresh()
        app.last_error='previous observation failure'
        app.store.planned.return_value=[dict(id='future',kind='planned')]
        app.observer.scan.side_effect=AssertionError('No Git scan for planned metadata')
        result=app.refresh_planned()
        self.assertNotEqual(old['evidence_hash'],result['evidence_hash'])
        self.assertEqual(fingerprint({'sources':'a'*64,'planned_projects':app.store.planned()}),result['source_hash'])
        self.assertEqual('original time',result['observed_at'])
        self.assertFalse(result['evidence_complete'])
        self.assertEqual('previous observation failure',app.last_error)
        self.assertEqual(1,app.observer.scan.call_count)
        result['projects'].append('external')
        self.assertEqual([],app.observation['projects'])

    def test_planning_before_first_scan_does_not_claim_complete_evidence(self):
        app=self.fixture();app.store.planned.return_value=[dict(id='future')]
        result=app.refresh_planned()
        self.assertFalse(result.get('evidence_complete',False))
        self.assertIsNone(result['observed_at'])
        app.observer.scan.assert_not_called()

    def test_fresh_scan_uses_latest_planning_and_matches_metadata_update(self):
        app=self.fixture();app.refresh()
        app.store.planned.return_value=[dict(id='future')]
        fast=app.refresh_planned()
        fresh=app.refresh(True)
        self.assertEqual(fast['evidence_hash'],fresh['evidence_hash'])
        self.assertEqual('a'*64,app.source_evidence_hash)

    def test_publish_uses_store_before_application_lock_like_decision_writes(self):
        app=self.fixture();held=[]
        class Lock:
            def __init__(self,name):self.name=name
            def __enter__(self):
                if self.name=='app':self_test.assertIn('store',held,'Inverted locks can deadlock decision writes')
                held.append(self.name)
            def __exit__(self,*args):held.pop()
        self_test=self
        app.store.lock=Lock('store');app.lock=Lock('app')
        app.refresh();app.refresh_planned()
        with app.store.lock:app.refresh();app.refresh_planned()
        self.assertEqual([],held)


class DisconnectedReplyTests(unittest.TestCase):
    def test_disconnected_peer_does_not_become_a_local_write_failure(self):
        for stage in ('end_headers','body'):
            with self.subTest(stage=stage):
                handler=Handler.__new__(Handler)
                handler.send_response=Mock();handler.headers_base=Mock();handler.send_header=Mock()
                handler.end_headers=Mock();handler.wfile=Mock()
                target=handler.end_headers if stage=='end_headers' else handler.wfile.write
                target.side_effect=ConnectionAbortedError('client disconnected')
                handler.reply({'ok':True})
                handler.send_response.assert_called_once_with(200)
