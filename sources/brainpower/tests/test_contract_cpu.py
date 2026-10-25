import json
import unittest
from unittest.mock import Mock, patch

from contract_lab.linux_cpu import verify_cpu_evidence
from contract_lab.linux_runner import run_normal
from contract_lab.linux_probe import start_command

RUN = 'a' * 32
IDENTITY = {'run_id': RUN, 'invocation_id': 'b' * 32, 'boot_id': 'c' * 32,
            'control_group': '/system.slice/aurelia-t3-' + RUN + '.service'}


def proof():
    return {'status': 'cpu_sample', 'identity': dict(IDENTITY),
            'limits': {'memory.max': '134217728', 'memory.swap.max': '0',
                       'pids.max': '16', 'cpu.max': '25000 100000'},
            'elapsed_ns': 4000000000,
            'before': {'usage_usec': 100, 'nr_periods': 1, 'nr_throttled': 0, 'throttled_usec': 0},
            'after': {'usage_usec': 1000100, 'nr_periods': 41, 'nr_throttled': 39, 'throttled_usec': 2900000}}


class CpuTests(unittest.TestCase):
    def verify(self, data):
        return verify_cpu_evidence(json.dumps(data), IDENTITY)

    def test_measured_throttling_and_usage_are_required(self):
        result = self.verify(proof())
        self.assertEqual(result['delta']['nr_throttled'], 39)
        self.assertEqual(result['delta']['usage_usec'], 1000000)

    def test_missing_throttling_or_reset_counters_fail(self):
        for key in proof()['before']:
            for value in (0, -1, True, '1'):
                data = proof()
                data['after'][key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    self.verify(data)

    def test_identity_limits_and_duration_are_bound(self):
        variants = []
        data = proof(); data['identity']['invocation_id'] = 'd' * 32; variants.append(data)
        data = proof(); data['limits']['cpu.max'] = '50000 100000'; variants.append(data)
        for duration in (True, 1, 9000000000):
            data = proof(); data['elapsed_ns'] = duration; variants.append(data)
        data = proof(); data['after']['nr_throttled'] = 100; variants.append(data)
        for data in variants:
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.verify(data)

    def test_ambiguous_missing_or_malformed_output_fails(self):
        for text in ('', '{}', json.dumps(proof()) + '\n' + json.dumps(proof()),
                     '{"status":"cpu_sample", broken}', 'x' * 32769):
            with self.subTest(text=text[:50]), self.assertRaises(ValueError):
                verify_cpu_evidence(text, IDENTITY)

    def test_cpu_mode_retains_fixed_limits(self):
        command = start_command(RUN, 'cpu')
        self.assertIn('--property=CPUQuota=25%', command)
        self.assertIn('--property=RuntimeMaxSec=20s', command)
        self.assertEqual(command[-2:], ['cpu', '--guarded'])

    def test_backend_accepts_only_exact_cpu_command(self):
        from contract_lab.linux_backend import LinuxBackend
        backend = LinuxBackend()
        backend.prepared = (RUN, 'd' * 64)
        backend._platform = Mock()
        backend._package = Mock()
        backend._absent = Mock()
        backend.observe = Mock(return_value={'state': 'running', 'identity': IDENTITY})
        backend._run = Mock(side_effect=['', 'InvocationID=' + IDENTITY['invocation_id']
            + '\nControlGroup=' + IDENTITY['control_group']])
        with patch('contract_lab.linux_backend._read', return_value='c' * 32):
            self.assertEqual(backend.start(start_command(RUN, 'cpu')), IDENTITY)
        self.assertTrue(backend.attempted)

    def test_cpu_worker_measures_same_cgroup_before_and_after_guard(self):
        from contract_lab.linux_worker import cpu_sample
        def read(path):
            name = path.name
            if name == 'cpu.stat':
                return 'usage_usec 1\nnr_periods 1\nnr_throttled 1\nthrottled_usec 1'
            if name == 'boot_id':
                return 'c' * 32
            return proof()['limits'][name]
        with patch('contract_lab.linux_worker.guard') as guard, \
             patch('contract_lab.linux_worker.Path.read_text', autospec=True, side_effect=read), \
             patch('contract_lab.linux_worker.time.monotonic_ns', side_effect=[0, 1, 4000000000, 4000000001]), \
             patch.dict('contract_lab.linux_worker.os.environ', {'INVOCATION_ID': 'b' * 32}):
            data = cpu_sample(RUN)
        self.assertEqual(data['identity'], IDENTITY)
        self.assertEqual(data['elapsed_ns'], 4000000001)
        self.assertEqual(guard.call_count, 2)

    def controller(self):
        controller = Mock()
        controller.start.return_value = IDENTITY
        controller.backend.service_snapshot.return_value = {'ssh.service': 'active'}
        controller.backend.wait_ended.return_value = {
            'identity': IDENTITY, 'state': 'ended', 'unit_result': 'success',
            'exit_code': 1, 'exit_status': 0}
        controller.backend._run.return_value = json.dumps(proof())
        return controller

    def test_cpu_success_requires_evidence_before_journal_and_cleanup(self):
        controller = self.controller()
        result = run_normal(controller, RUN, 'package', 'd' * 64, mode='cpu')
        self.assertEqual(result['status'], 'cpu_verified')
        controller.journal.finish.assert_called_once_with(RUN, IDENTITY, 'succeeded')
        self.assertIn('_SYSTEMD_INVOCATION_ID=' + IDENTITY['invocation_id'],
                      controller.backend._run.call_args.args[0])

    def test_invalid_cpu_evidence_cannot_finish_or_delete(self):
        controller = self.controller()
        controller.backend._run.return_value = '{}'
        self.assertEqual(run_normal(controller, RUN, 'package', 'd' * 64, mode='cpu')['status'], 'blocked')
        controller.journal.finish.assert_not_called()
        controller.backend.retire.assert_not_called()

    def test_cleanup_failure_is_not_cpu_success(self):
        controller = self.controller()
        controller.backend.retire.side_effect = ValueError('unverified')
        self.assertEqual(run_normal(controller, RUN, 'package', 'd' * 64, mode='cpu')['status'], 'blocked')
