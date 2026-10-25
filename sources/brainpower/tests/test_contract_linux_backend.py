"""Linux backend contract tests with explicit local seams; no privileged execution."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from contract_lab.linux_backend import LinuxBackend, BackendError
from contract_lab.linux_probe import build_package, start_command

RUN = 'a' * 32
IDENTITY = {'run_id': RUN, 'invocation_id': 'b' * 32, 'boot_id': 'c' * 32,
            'control_group': '/system.slice/aurelia-t3-' + RUN + '.service'}


class BackendTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / 'source'
        self.anchor = build_package(self.source)
        self.backend = LinuxBackend()
        self.backend.base = self.root / 'staged'
        self.backend.base.mkdir()
        self.commands = []
        self.present = False
        self.backend._platform = lambda: None
        self.backend._protected = lambda path, directory=False: None
        self.backend._run = self.run_command
        self.backend._remove_unit = lambda identity: None

    def run_command(self, command, timeout=3):
        self.commands.append(command)
        if command == ['/usr/bin/python3', '--version']:
            return 'Python 3.12.3\n'
        if command == ['/usr/bin/systemctl', '--version']:
            return 'systemd 255 (255.4)\n'
        if '--property=LoadState' in command:
            return 'LoadState=' + ('loaded' if self.present else 'not-found') + '\n'
        return ''

    def prepare(self):
        self.backend.preflight(RUN, self.source, self.anchor)

    def test_platform_gate_precedes_commands(self):
        self.backend = LinuxBackend()
        with patch('contract_lab.linux_backend.sys.platform', 'win32'):
            with self.assertRaises(BackendError):
                self.backend.preflight(RUN, self.source, self.anchor)

    def test_preflight_stages_only_verified_files_without_start(self):
        self.prepare()
        self.assertEqual({p.name for p in (self.backend.base / RUN).iterdir()},
                         {'linux_worker.py', 'manifest.json'})
        self.assertFalse(any(c[0].endswith('systemd-run') for c in self.commands))

    def test_staged_files_are_explicitly_readable_despite_root_umask(self):
        with patch('contract_lab.linux_backend.os.chmod') as chmod:
            self.prepare()
        self.assertEqual(chmod.call_count, 2)
        self.assertTrue(all(call.args[1] == 0o644 for call in chmod.call_args_list))

    def test_runtime_mismatch_prevents_staging(self):
        original = self.backend._run
        self.backend._run = lambda c, timeout=3: 'Python 3.11.0' if c[0].endswith('python3') else original(c)
        with self.assertRaises(BackendError):
            self.prepare()
        self.assertFalse((self.backend.base / RUN).exists())

    def test_existing_unit_or_directory_never_overwritten(self):
        self.present = True
        with self.assertRaises(BackendError):
            self.prepare()
        self.present = False
        target = self.backend.base / RUN
        target.mkdir()
        (target / 'sentinel').write_text('keep')
        with self.assertRaises(BackendError):
            self.prepare()
        self.assertEqual((target / 'sentinel').read_text(), 'keep')

    def test_arbitrary_command_rejected(self):
        self.prepare()
        with self.assertRaises(BackendError):
            self.backend.start(['/bin/sh', '-c', 'anything'])
        self.assertFalse(any(c[0].endswith('systemd-run') for c in self.commands))

    def test_staged_drift_prevents_start(self):
        self.prepare()
        (self.backend.base / RUN / 'linux_worker.py').write_text('drift')
        with self.assertRaises(ValueError):
            self.backend.start(start_command(RUN, 'normal'))
        self.assertFalse(any(c[0].endswith('systemd-run') for c in self.commands))

    def test_cleanup_rejects_extra_files_without_deleting(self):
        self.prepare()
        target = self.backend.base / RUN
        (target / 'unexpected').write_text('keep')
        self.backend.observe = lambda identity: {'identity': identity, 'state': 'ended'}
        with self.assertRaises(ValueError):
            self.backend.retire(IDENTITY, self.anchor)
        self.assertEqual(len(list(target.iterdir())), 3)

    def test_cleanup_requires_end_and_deletes_only_package(self):
        self.prepare()
        self.backend.observe = lambda identity: {'identity': identity, 'state': 'running'}
        with self.assertRaises(BackendError):
            self.backend.retire(IDENTITY, self.anchor)
        self.backend.observe = lambda identity: {'identity': identity, 'state': 'ended'}
        self.backend.retire(IDENTITY, self.anchor)
        self.assertFalse((self.backend.base / RUN).exists())
        self.assertTrue(self.source.exists())

    def test_symlink_and_world_writable_metadata_rejected(self):
        from types import SimpleNamespace
        import stat
        for mode, uid in ((stat.S_IFREG | 0o666, 0), (stat.S_IFLNK | 0o777, 0),
                          (stat.S_IFREG | 0o644, 1000)):
            with patch.object(Path, 'lstat', return_value=SimpleNamespace(st_mode=mode, st_uid=uid, st_nlink=1)):
                with self.assertRaises(BackendError):
                    LinuxBackend._protected(Path('/synthetic'))

    def test_empty_runtime_output_rejected(self):
        self.backend._run = lambda command, timeout=3: 'Python 3.12.3' if command[0].endswith('python3') else ''
        with self.assertRaises(BackendError):
            self.prepare()

    def test_observation_binds_recovered_identity_for_stop(self):
        self.assertIsNone(self.backend.identity)
        with patch('contract_lab.linux_backend.observe', return_value={'identity': IDENTITY, 'state': 'running'}):
            self.backend.observe(IDENTITY)
        self.assertEqual(self.backend.identity, IDENTITY)

    def test_uncertain_launch_cannot_be_repeated(self):
        self.prepare()
        def fail(command, timeout=3):
            if command[0].endswith('systemd-run'):
                self.commands.append(command)
                raise BackendError('timeout')
            return self.run_command(command, timeout)
        self.backend._run = fail
        for _ in range(2):
            with self.assertRaises(BackendError):
                self.backend.start(start_command(RUN, 'normal'))
        self.assertEqual(sum(c[0].endswith('systemd-run') for c in self.commands), 1)

    def test_wait_polls_until_end_with_shared_budget(self):
        from contract_lab.linux_backend import wait_for_end
        ticks = [0.0]
        calls = []
        def observation(remaining):
            calls.append(remaining)
            return {'state': 'running' if len(calls) == 1 else 'ended', 'identity': IDENTITY}
        result = wait_for_end(observation, IDENTITY, clock=lambda: ticks[0],
                              pause=lambda seconds: ticks.__setitem__(0, ticks[0] + seconds))
        self.assertEqual(result['state'], 'ended')
        self.assertGreater(calls[0], calls[1])

    def test_wait_rejects_late_success_and_identity_change(self):
        from contract_lab.linux_backend import wait_for_end
        ticks = [0.0]
        def late(remaining):
            ticks[0] = 6.0
            return {'state': 'ended', 'identity': IDENTITY}
        with self.assertRaises(BackendError):
            wait_for_end(late, IDENTITY, clock=lambda: ticks[0])
        with self.assertRaises(BackendError):
            wait_for_end(lambda remaining: {'state': 'ended', 'identity': {}}, IDENTITY)

    def test_unit_removal_failure_preserves_package(self):
        self.prepare()
        self.backend.observe = lambda identity: {'identity': identity, 'state': 'ended'}
        def fail(identity):
            raise BackendError('unit_not_removed')
        self.backend._remove_unit = fail
        with self.assertRaises(BackendError):
            self.backend.retire(IDENTITY, self.anchor)
        self.assertEqual(len(list((self.backend.base / RUN).iterdir())), 2)

    def test_retired_unit_requires_absence_boot_and_terminal_state(self):
        from contract_lab.linux_backend import verify_retired
        text = ('Id=aurelia-t3-' + RUN + '.service\nLoadState=not-found\n'
                'InvocationID=\nActiveState=inactive\nMainPID=0')
        verify_retired(IDENTITY, text, IDENTITY['boot_id'], True)
        for output, boot, absent in ((text, IDENTITY['boot_id'], False),
                                     (text, 'd' * 32, True),
                                     (text.replace('inactive', 'active'), IDENTITY['boot_id'], True),
                                     (text.replace('not-found', 'loaded'), IDENTITY['boot_id'], True)):
            with self.assertRaises(BackendError):
                verify_retired(IDENTITY, output, boot, absent)

    def test_pair_wait_does_not_accept_single_process(self):
        from contract_lab.linux_backend import wait_for_pair
        ticks = [0.0]
        calls = []
        def sample(remaining):
            calls.append(remaining)
            return {'identity': IDENTITY, 'state': 'running', 'process_count': len(calls)}
        result = wait_for_pair(sample, IDENTITY, clock=lambda: ticks[0],
                               pause=lambda delay: ticks.__setitem__(0, ticks[0] + delay))
        self.assertEqual(result['process_count'], 2)
        with self.assertRaises(BackendError):
            wait_for_pair(lambda remaining: {'identity': IDENTITY, 'state': 'ended'}, IDENTITY)

    def test_stop_proof_rechecked_after_unit_disappears(self):
        self.backend.identity = dict(IDENTITY)
        with patch('contract_lab.linux_backend.observe', return_value={'identity': IDENTITY, 'state': 'running'}):
            self.backend._prove_stopped = lambda identity: None
            self.backend.stop(['/usr/bin/systemctl', 'stop', 'aurelia-t3-' + RUN + '.service'])
        self.assertEqual(self.backend.observe(IDENTITY)['end_basis'], 'scoped_stop_and_removed_cgroup')
        def fail(identity):
            raise BackendError('unit_reappeared')
        self.backend._prove_stopped = fail
        with self.assertRaises(BackendError):
            self.backend.observe(IDENTITY)

    def test_failed_timeout_is_end_proof_but_not_retirement(self):
        terminal = {'identity': IDENTITY, 'state': 'ended', 'unit_result': 'timeout',
                    'exit_code': 2, 'exit_status': 9, 'limits': None,
                    'end_basis': 'unit_and_removed_cgroup'}
        with patch.object(self.backend, '_prove_retired', side_effect=BackendError('not_retired')):
            with patch('contract_lab.linux_backend.observe', return_value=terminal):
                self.assertEqual(self.backend._prove_stopped(IDENTITY), terminal)

    def test_stop_fallback_rejects_unverified_or_different_end(self):
        terminal = {'identity': IDENTITY, 'state': 'ended', 'unit_result': 'timeout',
                    'exit_code': 2, 'exit_status': 9, 'limits': None,
                    'end_basis': 'unit_and_removed_cgroup'}
        for key, value in (('identity', {}), ('state', 'running'), ('unit_result', 'oom-kill'),
                           ('exit_code', 1), ('exit_status', 0), ('end_basis', 'unknown')):
            with self.subTest(key=key), patch.object(self.backend, '_prove_retired',
                                                   side_effect=BackendError('not_retired')):
                with patch('contract_lab.linux_backend.observe', return_value={**terminal, key: value}):
                    with self.assertRaises(BackendError):
                        self.backend._prove_stopped(IDENTITY)

    def test_failed_unit_reset_is_scoped_and_retirement_rechecked(self):
        self.backend.stopped_identity = dict(IDENTITY)
        with patch.object(self.backend, '_prove_stopped', return_value={'unit_result': 'timeout'}):
            with patch.object(self.backend, '_prove_retired') as proof:
                LinuxBackend._remove_unit(self.backend, IDENTITY)
        self.assertEqual(self.commands, [['/usr/bin/systemctl', 'reset-failed',
                                         'aurelia-t3-' + RUN + '.service']])
        proof.assert_called_once_with(IDENTITY)

    def test_memory_evidence_requires_stable_oom_and_memory_configuration(self):
        proof = {'identity': IDENTITY, 'state': 'ended', 'unit_result': 'oom-kill',
                 'exit_code': 2, 'exit_status': 9}
        text = 'InvocationID=' + IDENTITY['invocation_id'] + '\nMemoryMax=134217728\nMemorySwapMax=0'
        self.backend.observe = lambda identity: dict(proof)
        self.backend._run = lambda command: text
        self.assertEqual(self.backend.memory_evidence(IDENTITY)['memory_max'], 134217728)
        for bad in (text.replace('134217728', 'infinity'), text.replace('MemorySwapMax=0', 'MemorySwapMax=1'),
                    text.replace(IDENTITY['invocation_id'], 'e' * 32)):
            self.backend._run = lambda command: bad
            with self.assertRaises(BackendError):
                self.backend.memory_evidence(IDENTITY)

    def test_oom_retirement_requires_proof_before_reset(self):
        self.prepare()
        self.backend.memory_evidence = Mock(side_effect=BackendError('unverified'))
        with self.assertRaises(BackendError):
            self.backend.retire_oom(IDENTITY, self.anchor)
        self.assertTrue((self.backend.base / RUN).exists())
        self.assertFalse(any('reset-failed' in c for c in self.commands))

    def test_fast_exit_binds_expected_group_only_with_terminal_observation(self):
        self.prepare()
        original = self.backend._run
        def query(command, timeout=3):
            if any(c.startswith('--property=Id,') for c in command):
                return 'InvocationID=' + IDENTITY['invocation_id'] + '\nControlGroup=' 
            return original(command, timeout)
        self.backend._run = query
        proof = {'identity': IDENTITY, 'state': 'ended', 'end_basis': 'unit_and_removed_cgroup'}
        with patch('contract_lab.linux_backend._read', return_value=IDENTITY['boot_id']):
            with patch('contract_lab.linux_backend.observe', return_value=proof):
                self.assertEqual(self.backend.start(start_command(RUN, 'memory')), IDENTITY)


if __name__ == '__main__':
    unittest.main()
