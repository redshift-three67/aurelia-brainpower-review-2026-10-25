import unittest
import tempfile
import subprocess
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch
from contract_lab.linux_loss import launch_loss, recover_loss

RUN = 'a' * 32
IDENTITY = {'run_id': RUN, 'invocation_id': 'b' * 32, 'boot_id': 'c' * 32,
            'control_group': '/system.slice/aurelia-t3-' + RUN + '.service'}
ANCHOR = 'd' * 64


class LossTests(unittest.TestCase):
    def setUp(self):
        self.controller = Mock()
        self.backend = self.controller.backend
        self.backend.service_snapshot.return_value = {'ssh.service': 'active'}
        self.controller.start.return_value = IDENTITY
        self.active = {'request_id': RUN, 'identity': IDENTITY, 'state': 'unknown',
                       'binding': {'release_id': ANCHOR}}
        self.controller.journal.snapshot.return_value = {'active': self.active}
        self.running = {'identity': IDENTITY, 'state': 'running', 'process_count': 2}
        self.backend.wait_pair.return_value = self.running
        self.backend.observe.return_value = self.running
        self.records = []
        self.launch = {'identity': IDENTITY, 'manifest_sha256': ANCHOR, 'run_id': RUN,
                       'status': 'controller_exit_prepared', 'services_before': {'ssh.service': 'active'}}

    def test_exit_only_after_durable_record(self):
        def exit_now(code):
            self.assertEqual(code, 73)
            self.assertEqual(self.records[-1]['status'], 'controller_exit_prepared')
            raise SystemExit(code)
        with self.assertRaises(SystemExit):
            launch_loss(self.controller, RUN, 'package', ANCHOR, self.records.append, exit_now)
        self.controller.journal.finish.assert_not_called()
        self.backend.stop.assert_not_called()

    def test_failed_record_never_intentionally_crashes(self):
        exit_now = Mock()
        def fail(report):
            raise OSError('disk full')
        with self.assertRaises(OSError):
            launch_loss(self.controller, RUN, 'package', ANCHOR, fail, exit_now)
        exit_now.assert_not_called()

    def test_running_state_stays_blocked_at_deadline(self):
        ticks = [0.0]
        def pause(delay):
            ticks[0] += delay
        result = recover_loss(self.controller, RUN, ANCHOR, self.launch, self.records.append,
                              clock=lambda: ticks[0], pause=pause)
        self.assertEqual(result['status'], 'blocked')
        self.controller.journal.release_unknown.assert_not_called()
        self.controller.start.assert_not_called()

    def test_wrong_binding_prevents_observation(self):
        self.active['binding']['release_id'] = 'e' * 64
        result = recover_loss(self.controller, RUN, ANCHOR, self.launch, self.records.append)
        self.assertEqual(result['status'], 'blocked')
        self.backend.observe.assert_not_called()

    def test_early_end_does_not_prove_running_after_loss(self):
        self.backend.observe.return_value = {'identity': IDENTITY, 'state': 'ended'}
        result = recover_loss(self.controller, RUN, ANCHOR, self.launch, self.records.append)
        self.assertEqual(result['status'], 'blocked')
        self.controller.journal.release_unknown.assert_not_called()

    def test_end_hands_off_to_checked_cleanup_without_start_or_stop(self):
        self.backend.observe.side_effect = [self.running, {'identity': IDENTITY, 'state': 'ended'}]
        with patch('contract_lab.linux_loss.cleanup', return_value={'status': 'cleanup_verified'}) as clean:
            result = recover_loss(self.controller, RUN, ANCHOR, self.launch, self.records.append)
        self.assertEqual(result['status'], 'controller_loss_verified')
        clean.assert_called_once()
        self.controller.start.assert_not_called()
        self.backend.stop.assert_not_called()

    def test_real_process_exit_releases_lock_and_preserves_unknown_journal(self):
        from contract_lab.linux_controller import Controller
        code = '''
import sys
from pathlib import Path
sys.path.insert(0, str(Path('tests').resolve()))
from test_contract_linux_controller import Backend, RUN
from contract_lab.linux_controller import Controller
from contract_lab.linux_probe import build_package
from contract_lab.linux_loss import launch_loss
from contract_lab.linux_runner import write_report
root = Path(sys.argv[1])
backend = Backend()
backend.service_snapshot = lambda: {'ssh.service': 'active'}
backend.wait_pair = lambda identity: {'identity': identity, 'state': 'running', 'process_count': 2}
anchor = build_package(root / 'package')
controller = Controller(root / 'journal.db', root / 'lock', backend, create=True)
launch_loss(controller, RUN, root / 'package', anchor, lambda value: write_report(root / 'launch.json', value))
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run([sys.executable, '-B', '-c', code, str(root)],
                                    capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 73, result.stderr.decode())
            self.assertEqual(json.loads((root / 'launch.json').read_text())['status'], 'controller_exit_prepared')
            controller = Controller(root / 'journal.db', root / 'lock', Mock())
            try:
                snapshot = controller.journal.snapshot()
                self.assertEqual(snapshot['active']['state'], 'unknown')
                self.assertEqual(snapshot['active']['identity'], IDENTITY)
                self.assertFalse(any(e['state'] in ('failed', 'succeeded', 'aborted') for e in snapshot['events']))
            finally:
                controller.close()

    def test_changed_identity_during_wait_never_cleans(self):
        self.backend.observe.side_effect = [self.running, {'identity': {}, 'state': 'ended'}]
        with patch('contract_lab.linux_loss.cleanup') as clean:
            result = recover_loss(self.controller, RUN, ANCHOR, self.launch, self.records.append)
        self.assertEqual(result['status'], 'blocked')
        clean.assert_not_called()

    def test_verified_stopping_transition_waits_for_end(self):
        self.backend.observe.side_effect = [self.running, {**self.running, 'state': 'stopping'},
                                            {'identity': IDENTITY, 'state': 'ended'}]
        with patch('contract_lab.linux_loss.cleanup', return_value={'status': 'cleanup_verified'}):
            result = recover_loss(self.controller, RUN, ANCHOR, self.launch, self.records.append, pause=lambda _: None)
        self.assertEqual(result['status'], 'controller_loss_verified')

    def test_unknown_transition_still_blocks(self):
        self.backend.observe.side_effect = [self.running, {**self.running, 'state': 'unknown'}]
        result = recover_loss(self.controller, RUN, ANCHOR, self.launch, self.records.append)
        self.assertEqual(result['status'], 'blocked')

    def test_proven_stop_transition_reobserved_without_restarting(self):
        from contract_lab.linux_observer import StopTransition
        self.backend.observe.side_effect = [self.running, StopTransition('stop_transition'),
                                            {'identity': IDENTITY, 'state': 'ended'}]
        with patch('contract_lab.linux_loss.cleanup', return_value={'status': 'cleanup_verified'}):
            result = recover_loss(self.controller, RUN, ANCHOR, self.launch, self.records.append, pause=lambda _: None)
        self.assertEqual(result['status'], 'controller_loss_verified')
        self.controller.start.assert_not_called()

    def test_blocked_report_identifies_phase_without_raw_exception(self):
        self.backend.observe.side_effect = ValueError('SECRET_SENTINEL')
        result = recover_loss(self.controller, RUN, ANCHOR, self.launch, self.records.append)
        self.assertEqual(result['failed_phase'], 'early_observation')
        self.assertNotIn('SECRET_SENTINEL', str(result))
