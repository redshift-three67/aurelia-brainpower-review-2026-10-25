import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest

from governor_workbench.store import Store


@unittest.skipUnless(os.name == 'nt', 'Owned Windows runtime profile')
class RuntimeProfileTests(unittest.TestCase):
    def setUp(self):
        from governor_workbench.runtime_profiles import RuntimeProfiles
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(Path(self.tmp.name) / 'journal.db')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
        self.config = {'runtime_probe_port': port, 'data_dir': self.tmp.name}
        self.manager = RuntimeProfiles(self.store, self.config)
        self.addCleanup(self.manager.close)

    def start(self):
        p = self.manager.profile()
        return self.manager.start(p['id'], p['hash'], threading.Event())

    def test_start_readiness_stop_and_history(self):
        row = self.start()
        self.assertEqual(row['status'], 'running')
        self.assertTrue(row['readiness_verified'])
        self.assertEqual(self.manager.stop(row['id'])['status'], 'stopped')
        self.assertEqual(self.manager.stop(row['id'])['status'], 'stopped')
        history = self.manager.state()['instances']
        self.assertEqual(history[0]['id'], row['id'])
        self.assertEqual(history[0]['status'], 'stopped')

    def test_explicit_check_records_current_instance_and_rejects_stopped(self):
        row = self.start()
        checked = self.manager.check(row['id'], threading.Event())
        self.assertTrue(checked['last_check']['success'])
        self.assertTrue(checked['last_check']['checked_at'])
        self.assertEqual(checked['last_check']['profile_hash'], row['profile_hash'])
        self.manager.stop(row['id'])
        with self.assertRaises(ValueError): self.manager.check(row['id'], threading.Event())

    def test_check_failure_replaces_success_without_stopping_service(self):
        from unittest.mock import patch
        row = self.start()
        self.manager.check(row['id'], threading.Event())
        with patch('governor_workbench.runtime_profiles.urllib.request.OpenerDirector.open', side_effect=OSError('private detail')):
            checked = self.manager.check(row['id'], threading.Event())
        self.assertFalse(checked['last_check']['success'])
        self.assertNotIn('private detail', str(checked))
        self.assertEqual(checked['status'], 'running')

    def test_check_rejects_wrong_identity_and_profile_drift(self):
        from unittest.mock import patch, MagicMock
        row = self.start()
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'{"service":"governor-runtime-probe","instance_id":"other"}'
        with patch('governor_workbench.runtime_profiles.urllib.request.OpenerDirector.open', return_value=response):
            self.assertFalse(self.manager.check(row['id'], threading.Event())['last_check']['success'])
        with patch.object(self.manager, 'profile', return_value={'hash':'changed'}):
            self.assertFalse(self.manager.check(row['id'], threading.Event())['last_check']['success'])

    def test_cancelled_check_leaves_no_success_receipt(self):
        from governor_workbench.jobs import JobCancelled
        row = self.start()
        event = threading.Event(); event.set()
        with self.assertRaises(JobCancelled): self.manager.check(row['id'], event)
        self.assertNotIn('last_check', self.manager.state()['instances'][0])

    def test_occupied_port_never_starts_or_kills_foreign_listener(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', self.config['runtime_probe_port'])); sock.listen()
            with self.assertRaises(ValueError): self.start()
            self.assertEqual(sock.getsockname()[1], self.config['runtime_probe_port'])
        self.assertEqual(self.manager.state()['instances'], [])

    def test_stale_hash_and_unknown_profile_are_rejected(self):
        with self.assertRaises(ValueError):
            self.manager.start('local_probe', '0' * 64, threading.Event())
        with self.assertRaises(ValueError):
            self.manager.start('aurelia', self.manager.profile()['hash'], threading.Event())
        self.assertEqual(self.manager.state()['instances'], [])

    def test_duplicate_start_rejected_and_close_stops_owned_runtime(self):
        row = self.start()
        with self.assertRaises(ValueError): self.start()
        self.manager.close()
        self.assertEqual(self.manager.state()['instances'][0]['status'], 'stopped')
        with self.assertRaises(ValueError): self.start()

    def test_restart_marks_stale_receipt_interrupted_without_launch(self):
        from governor_workbench.runtime_profiles import RuntimeProfiles
        from unittest.mock import patch
        self.manager.close()
        with self.store.db() as db:
            db.execute('INSERT INTO runtime_instances(id,body) VALUES(?,?)',
                       ('f'*32, '{"id":"'+'f'*32+'","status":"running"}'))
        with patch('governor_workbench.runtime_profiles.start_owned_windows', side_effect=AssertionError('no replay')):
            restarted = RuntimeProfiles(self.store, self.config)
            try:
                self.assertEqual(restarted.state()['instances'][0]['status'], 'interrupted')
            finally: restarted.close()

    def test_pre_cancel_creates_no_runtime(self):
        from governor_workbench.jobs import JobCancelled
        event = threading.Event(); event.set()
        p = self.manager.profile()
        with self.assertRaises(JobCancelled): self.manager.start(p['id'], p['hash'], event)
        self.assertEqual(self.manager.state()['instances'], [])

    def test_unexpected_process_exit_is_recorded_without_restart(self):
        import time
        row = self.start()
        self.manager.active[1].kill()
        for _ in range(30):
            latest = self.manager.state()['instances'][0]
            if latest['status'] == 'failed': break
            time.sleep(.1)
        self.assertEqual(latest['status'], 'failed')
        self.assertEqual(latest['id'], row['id'])
        self.assertIsNone(self.manager.active)

    def test_cancel_during_readiness_closes_owned_tree(self):
        from governor_workbench.jobs import JobCancelled
        from unittest.mock import patch
        event = threading.Event()
        p = self.manager.profile()
        timer = threading.Timer(.2, event.set)
        timer.start()
        try:
            with patch('governor_workbench.runtime_profiles.urllib.request.OpenerDirector.open', side_effect=OSError('not ready')):
                with self.assertRaises(JobCancelled):
                    self.manager.start(p['id'],p['hash'],event)
        finally: timer.cancel()
        self.assertIsNone(self.manager.active)
        self.assertEqual(self.manager.state()['instances'][0]['status'],'failed')
