import unittest
from unittest.mock import Mock
from contract_lab.linux_memory import run_memory

RUN = 'a' * 32
IDENTITY = {'run_id': RUN, 'invocation_id': 'b' * 32, 'boot_id': 'c' * 32,
            'control_group': '/system.slice/aurelia-t3-' + RUN + '.service'}


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.controller = Mock()
        self.controller.start.return_value = IDENTITY
        self.backend = self.controller.backend
        self.backend.service_snapshot.return_value = {'ssh.service': 'active'}
        self.proof = {'identity': IDENTITY, 'state': 'ended', 'unit_result': 'oom-kill',
                      'exit_code': 2, 'exit_status': 9}
        self.backend.wait_ended.return_value = self.proof
        self.backend.memory_evidence.return_value = self.proof
        self.records = []

    def call(self):
        return run_memory(self.controller, RUN, 'package', 'd' * 64,
                          lambda report: self.records.append(dict(report)))

    def test_expected_oom_records_worker_failure_and_test_success(self):
        result = self.call()
        self.assertEqual(result['status'], 'memory_verified')
        self.controller.journal.finish.assert_called_once_with(RUN, IDENTITY, 'failed')
        self.controller.start.assert_called_once_with(RUN, 'memory', 'package', 'd' * 64)
        self.assertTrue(self.records)

    def test_wrong_end_never_finishes_or_retires(self):
        for key, value in [('identity', {}), ('state', 'running'), ('unit_result', 'timeout'),
                           ('exit_status', 0), ('exit_code', 1)]:
            with self.subTest(key=key):
                self.backend.memory_evidence.return_value = {**self.proof, key: value}
                self.assertEqual(self.call()['status'], 'blocked')
        self.controller.journal.finish.assert_not_called()
        self.backend.retire_oom.assert_not_called()

    def test_evidence_failure_preserves_test_files(self):
        self.backend.memory_evidence.side_effect = ValueError('unverified')
        self.assertEqual(self.call()['status'], 'blocked')
        self.backend.retire_oom.assert_not_called()

    def test_cleanup_failure_is_not_test_success(self):
        self.backend.retire_oom.side_effect = ValueError('unverified')
        self.assertEqual(self.call()['status'], 'blocked')

    def test_unhealthy_baseline_prevents_start(self):
        self.backend.service_snapshot.return_value = {'ssh.service': 'failed'}
        self.assertEqual(self.call()['status'], 'blocked')
        self.controller.start.assert_not_called()

    def test_checkpoint_failure_prevents_journal_completion_and_removal(self):
        def fail(report):
            raise OSError('disk full')
        result = run_memory(self.controller, RUN, 'package', 'd' * 64, fail)
        self.assertEqual(result['status'], 'blocked')
        self.controller.journal.finish.assert_not_called()
        self.backend.retire_oom.assert_not_called()

    def test_post_cleanup_service_drift_is_not_success(self):
        self.backend.service_snapshot.side_effect = [
            {'ssh.service': 'active'}, {'ssh.service': 'active'}, {'ssh.service': 'failed'}]
        result = self.call()
        self.assertEqual(result['status'], 'blocked')
        self.assertTrue(result['package_removed'])
