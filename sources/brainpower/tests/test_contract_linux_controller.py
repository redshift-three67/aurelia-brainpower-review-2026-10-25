"""Controller failure sequencing with a synthetic backend, no Linux execution."""
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from contract_lab.linux_controller import Controller, ControllerError, Lease
from contract_lab.linux_probe import build_package
from contract_lab.recovery import Journal

RUN = 'a' * 32
IDENTITY = {'run_id': RUN, 'invocation_id': 'b' * 32, 'boot_id': 'c' * 32,
            'control_group': '/system.slice/aurelia-t3-' + RUN + '.service'}


class Backend:
    def __init__(self):
        self.calls = []
        self.state = 'running'
        self.identity = dict(IDENTITY)
        self.fail_start = False

    def preflight(self, run, package, anchor):
        self.calls.append('preflight')

    def start(self, command):
        self.calls.append('start')
        if self.fail_start:
            raise OSError('uncertain start')
        return dict(self.identity)

    def observe(self, identity):
        self.calls.append('observe')
        return {'identity': dict(self.identity), 'state': self.state}

    def stop(self, command):
        self.calls.append('stop')
        self.state = 'ended'


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / 'package'
        self.anchor = build_package(self.package)
        self.backend = Backend()
        self.controller = Controller(self.root / 'journal.db', self.root / 'lease', self.backend, create=True)
        self.addCleanup(self.controller.close)

    def start(self):
        return self.controller.start(RUN, 'normal', self.package, self.anchor)

    def test_reservation_precedes_external_start(self):
        original = self.backend.start
        def start(command):
            self.assertEqual(self.controller.journal.snapshot()['active']['state'], 'reserved')
            return original(command)
        self.backend.start = start
        self.start()
        self.assertEqual(self.controller.journal.snapshot()['active']['state'], 'running')

    def test_duplicate_start_never_reaches_backend(self):
        self.start()
        with self.assertRaises(ValueError):
            self.start()
        self.assertEqual(self.backend.calls.count('start'), 1)

    def test_package_drift_never_reserves_or_starts(self):
        (self.package / 'linux_worker.py').write_text('drift')
        with self.assertRaises(ValueError):
            self.start()
        self.assertEqual(self.backend.calls, [])
        self.assertIsNone(self.controller.journal.snapshot()['active'])

    def test_uncertain_start_stays_reserved_no_retry(self):
        self.backend.fail_start = True
        with self.assertRaises(ControllerError):
            self.start()
        self.assertEqual(self.controller.journal.snapshot()['active']['state'], 'reserved')
        with self.assertRaises(ValueError):
            self.start()
        self.assertEqual(self.backend.calls.count('start'), 1)

    def test_wrong_start_identity_never_recorded(self):
        self.backend.identity['run_id'] = 'd' * 32
        with self.assertRaises(ControllerError):
            self.start()
        self.assertIsNone(self.controller.journal.snapshot()['active']['identity'])

    def test_stop_requires_fresh_identity_and_end(self):
        self.start()
        self.controller.stop(RUN)
        self.assertEqual(self.backend.calls[-3:], ['observe', 'stop', 'observe'])
        self.assertIsNone(self.controller.journal.snapshot()['active'])
        self.assertEqual(self.controller.journal.snapshot()['events'][-1]['state'], 'aborted')

    def test_identity_drift_prevents_stop(self):
        self.start()
        self.backend.identity['invocation_id'] = 'e' * 32
        with self.assertRaises(ControllerError):
            self.controller.stop(RUN)
        self.assertNotIn('stop', self.backend.calls)

    def test_stop_without_end_holds_slot(self):
        self.start()
        self.backend.stop = lambda command: self.backend.calls.append('stop')
        with self.assertRaises(ControllerError):
            self.controller.stop(RUN)
        self.assertEqual(self.controller.journal.snapshot()['active']['state'], 'abort_requested')

    def test_reopen_never_restarts_and_unknown_is_preserved(self):
        self.start()
        self.controller.close()
        self.controller = Controller(self.root / 'journal.db', self.root / 'lease', self.backend)
        self.addCleanup(self.controller.close)
        self.assertEqual(self.controller.journal.snapshot()['active']['state'], 'unknown')
        self.controller.stop(RUN)
        self.assertEqual(self.backend.calls.count('start'), 1)
        self.assertEqual(self.controller.journal.snapshot()['events'][-1]['state'], 'released_unknown')

    def test_second_controller_cannot_take_over_journal(self):
        self.start()
        with self.assertRaises(ControllerError):
            Controller(self.root / 'journal.db', self.root / 'lease', self.backend)
        self.assertEqual(self.controller.journal.snapshot()['active']['state'], 'running')

    def test_close_prevents_external_actions(self):
        self.controller.close()
        with self.assertRaises(ControllerError):
            self.start()
        self.assertEqual(self.backend.calls, [])

    def test_separate_process_cannot_acquire_held_lease(self):
        code = '''import sys
from contract_lab.linux_controller import Lease, ControllerError
try:
    lease = Lease(sys.argv[1])
except ControllerError:
    sys.exit(0)
lease.close()
sys.exit(3)
'''
        completed = subprocess.run([sys.executable, '-B', '-c', code, str(self.root / 'lease')],
                                   capture_output=True, timeout=10)
        self.assertEqual(completed.returncode, 0)

    def test_failed_start_receipt_write_does_not_retry_or_cleanup(self):
        def fail(*args):
            raise ValueError('synthetic journal failure')
        self.controller.journal.started = fail
        with self.assertRaises(ControllerError):
            self.start()
        self.assertEqual(self.backend.calls, ['preflight', 'start'])
        self.assertEqual(self.controller.journal.snapshot()['active']['state'], 'reserved')
        self.assertTrue((self.package / 'linux_worker.py').exists())

    def test_preflight_failure_cannot_reserve(self):
        def fail(*args):
            raise ValueError('invalid runtime')
        self.backend.preflight = fail
        with self.assertRaises(ValueError):
            self.start()
        self.assertIsNone(self.controller.journal.snapshot()['active'])

    def test_drift_during_preflight_never_starts(self):
        def change(*args):
            (self.package / 'linux_worker.py').write_text('drift')
        self.backend.preflight = change
        with self.assertRaises(ValueError):
            self.start()
        self.assertNotIn('start', self.backend.calls)


if __name__ == '__main__':
    unittest.main()
