"""Integrated journal/controller/runner sequencing with explicit OS fixtures."""
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from contract_lab.linux_controller import Controller
from contract_lab.linux_probe import build_package
from contract_lab.linux_runner import run_normal, recover, write_report
from test_contract_linux_controller import Backend, RUN, IDENTITY


class RunnerBackend(Backend):
    def __init__(self):
        super().__init__()
        self.state = 'ended'
        self.exit_status = 0
        self.drift = False
        self.retired = False

    def observe(self, identity):
        self.calls.append('observe')
        return {'identity': dict(self.identity), 'state': self.state, 'unit_result': 'success',
                'exit_code': 1, 'exit_status': self.exit_status}

    def wait_ended(self, identity):
        return self.observe(identity)

    def service_snapshot(self):
        return {'ssh.service': 'failed' if self.drift and 'start' in self.calls else 'active',
                'wg-quick@wg-admin.service': 'active'}

    def retire(self, identity, anchor):
        self.retired = True


class RunnerTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.package = self.root / 'package'
        self.anchor = build_package(self.package)
        self.backend = RunnerBackend()
        self.controller = Controller(self.root / 'journal.db', self.root / 'lease', self.backend, create=True)
        self.addCleanup(self.controller.close)

    def run_normal(self):
        return run_normal(self.controller, RUN, self.package, self.anchor)

    def test_normal_report_and_terminal_journal(self):
        report = self.run_normal()
        self.assertEqual(report['status'], 'process_completed')
        self.assertTrue(report['package_removed'])
        self.assertTrue(report['services_unchanged'])
        self.assertIsNone(self.controller.journal.snapshot()['active'])
        self.assertEqual(report['manifest_sha256'], self.anchor)

    def test_running_does_not_finish_or_delete(self):
        self.backend.state = 'running'
        report = self.run_normal()
        self.assertEqual(report['status'], 'blocked')
        self.assertFalse(self.backend.retired)
        self.assertIsNotNone(self.controller.journal.snapshot()['active'])

    def test_nonzero_exit_is_not_success(self):
        self.backend.exit_status = 2
        report = self.run_normal()
        self.assertEqual(report['status'], 'blocked')
        self.assertFalse(self.backend.retired)

    def test_service_drift_blocks_cleanup(self):
        self.backend.drift = True
        report = self.run_normal()
        self.assertEqual(report['status'], 'blocked')
        self.assertFalse(report['services_unchanged'])
        self.assertFalse(self.backend.retired)

    def test_uncertain_start_report_has_no_raw_error(self):
        self.backend.fail_start = True
        report = self.run_normal()
        self.assertEqual(report['status'], 'blocked')
        self.assertNotIn('uncertain start', json.dumps(report))
        self.assertFalse(self.backend.retired)

    def test_recovery_observes_without_replay(self):
        self.controller.start(RUN, 'normal', self.package, self.anchor)
        self.controller.close()
        self.controller = Controller(self.root / 'journal.db', self.root / 'lease', self.backend)
        self.addCleanup(self.controller.close)
        report = recover(self.controller, RUN)
        self.assertEqual(report['status'], 'released_unknown')
        self.assertEqual(self.backend.calls.count('start'), 1)
        self.assertEqual(self.controller.journal.snapshot()['events'][-1]['state'], 'released_unknown')

    def test_missing_identity_recovery_stays_blocked(self):
        self.backend.fail_start = True
        self.run_normal()
        self.controller.close()
        self.controller = Controller(self.root / 'journal.db', self.root / 'lease', self.backend)
        self.addCleanup(self.controller.close)
        self.assertEqual(recover(self.controller, RUN)['status'], 'blocked')
        self.assertFalse(self.backend.retired)

    def test_report_written_once_and_not_overwritten(self):
        report = self.run_normal()
        path = self.root / 'result.json'
        write_report(path, report)
        self.assertEqual(json.loads(path.read_text()), report)
        with self.assertRaises(FileExistsError):
            write_report(path, {'status': 'replacement'})

    @unittest.skipIf(sys.platform == 'linux', 'Windows-only entry gate; Linux execution tested separately')
    def test_entrypoint_rejects_windows_before_privileged_actions(self):
        result = subprocess.run([sys.executable, '-B', '-m', 'contract_lab.linux_runner',
                                 'normal', RUN, self.anchor], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b'entry_unverified', result.stdout)

    def test_failed_cleanup_not_reported_as_success(self):
        def fail(*args):
            raise OSError('private path must not leak')
        self.backend.retire = fail
        report = self.run_normal()
        self.assertEqual(report['status'], 'blocked')
        self.assertFalse(report['package_removed'])
        self.assertNotIn('private path', json.dumps(report))

    def test_service_drift_during_retirement_is_reported(self):
        def retire(*args):
            self.backend.retired = True
            self.backend.drift = True
        self.backend.retire = retire
        report = self.run_normal()
        self.assertEqual(report['status'], 'blocked')
        self.assertTrue(report['package_removed'])
        self.assertFalse(report['services_unchanged'])
