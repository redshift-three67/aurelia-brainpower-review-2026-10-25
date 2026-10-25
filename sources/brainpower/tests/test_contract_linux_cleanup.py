import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock

from contract_lab.linux_controller import Controller
from contract_lab.linux_cleanup import cleanup

RUN = 'a' * 32
ANCHOR = 'd' * 64
IDENTITY = {'run_id': RUN, 'invocation_id': 'b' * 32, 'boot_id': 'c' * 32,
            'control_group': '/system.slice/aurelia-t3-' + RUN + '.service'}


class CleanupTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.backend = Mock()
        self.backend.service_snapshot.return_value = {'ssh.service': 'active'}
        self.backend._prove_stopped.return_value = {
            'identity': IDENTITY, 'state': 'ended', 'unit_result': 'timeout',
            'exit_code': 2, 'exit_status': 9, 'end_basis': 'unit_and_removed_cgroup'}
        controller = Controller(root / 'db', root / 'lock', self.backend, create=True)
        controller.journal.reserve(RUN, {'tenant_id': 'synthetic', 'actor_id': 'controller',
                                       'release_id': ANCHOR, 'profile_revision': 'aurelia-rest/1.0-draft.1'})
        controller.journal.started(RUN, IDENTITY)
        controller.journal.abort(RUN)
        controller.close()
        self.controller = Controller(root / 'db', root / 'lock', self.backend)
        self.addCleanup(self.controller.close)
        self.saved = []

    def call(self, anchor=ANCHOR, record=None):
        return cleanup(self.controller, RUN, anchor, IDENTITY,
                       record or (lambda report: self.saved.append(dict(report))))

    def test_releases_unknown_without_replay_and_records_before_removal(self):
        def retire(*args):
            self.assertTrue(self.saved)
            self.assertEqual(self.saved[-1]['status'], 'released_unknown')
        self.backend.retire.side_effect = retire
        result = self.call()
        self.assertEqual(result['status'], 'cleanup_verified')
        self.assertIsNone(self.controller.journal.snapshot()['active'])
        self.assertEqual(self.controller.journal.snapshot()['events'][-1]['state'], 'released_unknown')
        self.backend.start.assert_not_called()
        self.backend.stop.assert_not_called()

    def test_wrong_binding_blocks_before_removal(self):
        self.assertEqual(self.call('e' * 64)['status'], 'blocked')
        self.backend.retire.assert_not_called()
        self.assertIsNotNone(self.controller.journal.snapshot()['active'])

    def test_missing_end_proof_preserves_active_journal(self):
        self.backend._prove_stopped.return_value = None
        self.assertEqual(self.call()['status'], 'blocked')
        self.backend.retire.assert_not_called()
        self.assertIsNotNone(self.controller.journal.snapshot()['active'])

    def test_failed_evidence_write_prevents_removal(self):
        def fail(report):
            raise OSError('disk full')
        with self.assertRaises(OSError):
            self.call(record=fail)
        self.backend.retire.assert_not_called()

    def test_failed_removal_is_not_success_and_does_not_replay(self):
        self.backend.retire.side_effect = ValueError('retirement_unverified')
        result = self.call()
        self.assertEqual(result['status'], 'blocked')
        self.assertTrue(result['journal_released'])
        self.assertFalse(result['package_removed'])
        self.backend.start.assert_not_called()
