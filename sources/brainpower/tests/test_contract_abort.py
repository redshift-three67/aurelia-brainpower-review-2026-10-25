"""Bounded abort orchestration with synthetic OS observations."""
from pathlib import Path
import tempfile
import unittest

from contract_lab.linux_controller import Controller
from contract_lab.linux_probe import build_package
from contract_lab.linux_runner import run_abort
from test_contract_linux_runner import RunnerBackend
from test_contract_linux_controller import RUN, IDENTITY


class AbortTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.package = root / 'package'
        self.anchor = build_package(self.package)
        self.backend = RunnerBackend()
        self.backend.state = 'running'
        self.live = {'identity': IDENTITY, 'state': 'running', 'process_count': 2,
                     'limits': {'memory.max': '134217728', 'memory.swap.max': '0',
                                'pids.max': '16', 'cpu.max': '25000 100000'}}
        self.backend.wait_pair = lambda identity: self.live
        self.controller = Controller(root / 'journal.db', root / 'lease', self.backend, create=True)
        self.addCleanup(self.controller.close)

    def call(self):
        return run_abort(self.controller, RUN, self.package, self.anchor)

    def test_live_limits_and_processes_then_confirmed_stop(self):
        report = self.call()
        self.assertEqual(report['status'], 'abort_verified')
        self.assertEqual(report['running_observation'], self.live)
        self.assertTrue(report['package_removed'])
        self.assertEqual(self.controller.journal.snapshot()['events'][-1]['state'], 'aborted')

    def test_one_process_or_no_limits_does_not_pass(self):
        self.live['process_count'] = 1
        self.assertEqual(self.call()['status'], 'blocked')
        self.assertFalse(self.backend.retired)

    def test_unbounded_limit_blocks(self):
        self.live['limits']['memory.max'] = 'max'
        self.assertEqual(self.call()['status'], 'blocked')
        self.assertFalse(self.backend.retired)

    def test_failed_stop_keeps_evidence(self):
        self.backend.stop = lambda command: None
        self.assertEqual(self.call()['status'], 'blocked')
        self.assertFalse(self.backend.retired)
        self.assertEqual(self.controller.journal.snapshot()['active']['state'], 'abort_requested')

    def test_foreign_identity_is_not_stopped(self):
        self.live['identity'] = dict(IDENTITY, invocation_id='e' * 32)
        self.assertEqual(self.call()['status'], 'blocked')
        self.assertNotIn('stop', self.backend.calls)
