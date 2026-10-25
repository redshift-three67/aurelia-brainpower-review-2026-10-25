"""Synthetic OS observations; no claim that Windows tests exercise systemd."""
import unittest
from pathlib import Path
import tempfile

from contract_lab.linux_observer import observe, release_observed, ObservationError
from contract_lab.recovery import Journal

RUN = 'a' * 32
BOOT = 'c' * 32
GROUP = '/system.slice/aurelia-t3-' + RUN + '.service'
RECEIPT = {'run_id': RUN, 'boot_id': BOOT, 'invocation_id': 'b' * 32, 'control_group': GROUP}


class ObserverTests(unittest.TestCase):
    def test_removed_group_while_unit_still_stopping_is_not_end(self):
        from contract_lab.linux_observer import StopTransition
        self.unit.update(ActiveState='deactivating', SubState='stop-sigkill', Result='timeout',
                         MainPID='0', ControlGroup='')
        def read(path):
            if path.startswith('/sys/fs/cgroup'):
                raise FileNotFoundError(path)
            return self.files[path]
        with self.assertRaises(StopTransition):
            observe(RECEIPT, query=self.query, read=read, absent=lambda _: True)
        with self.assertRaises(ObservationError) as caught:
            observe(RECEIPT, query=self.query, read=read, absent=lambda _: False)
        self.assertNotIsInstance(caught.exception, StopTransition)

    def test_group_disappears_during_each_read_requires_fresh_end_pair(self):
        for missing in ('memory.max', 'memory.swap.max', 'pids.max', 'cpu.max', 'cgroup.events', 'cgroup.procs'):
            with self.subTest(missing=missing):
                self.setUp()
                def read(path):
                    if path.endswith('/' + missing):
                        self.unit.update(ActiveState='failed', SubState='failed', MainPID='0',
                                         Result='timeout', ExecMainCode='2', ExecMainStatus='9',
                                         ExecMainExitTimestampMonotonic='123456', ControlGroup='')
                        raise FileNotFoundError(path)
                    return self.files[path]
                result = observe(RECEIPT, query=self.query, read=read, absent=lambda _: True)
                self.assertEqual(result['state'], 'ended')
                self.assertGreaterEqual(len(self.commands), 3)

    def test_stop_to_terminal_change_is_not_immediate_end_evidence(self):
        from contract_lab.linux_observer import StopTransition
        self.unit.update(ActiveState='deactivating', SubState='stop-sigterm', Result='timeout')
        count = []
        def query(command):
            count.append(command)
            if len(count) == 2:
                self.unit.update(ActiveState='failed', SubState='failed', MainPID='0',
                                 ExecMainCode='2', ExecMainStatus='9', ExecMainExitTimestampMonotonic='123456',
                                 ControlGroup='')
            return self.query(command)
        with self.assertRaises(StopTransition):
            self.call(query=query)

    def test_same_identity_stop_transition_is_distinguished(self):
        from contract_lab.linux_observer import StopTransition
        calls = []
        def query(command):
            calls.append(command)
            if len(calls) == 2:
                self.unit.update(ActiveState='deactivating', SubState='stop-sigterm', Result='timeout')
            return self.query(command)
        with self.assertRaises(StopTransition):
            self.call(query=query)

    def test_verified_deactivating_group_is_stopping_not_ended(self):
        self.unit.update(ActiveState='deactivating', SubState='stop-sigterm', Result='timeout')
        result = self.call()
        self.assertEqual(result['state'], 'stopping')
        self.assertEqual(result['process_count'], 2)
        self.unit['SubState'] = 'unrecognized'
        self.assertEqual(self.call()['state'], 'unknown')

    def setUp(self):
        self.unit = {'Id': 'aurelia-t3-' + RUN + '.service', 'LoadState': 'loaded',
                     'InvocationID': 'b' * 32, 'ControlGroup': GROUP, 'ActiveState': 'active',
                     'SubState': 'running', 'MainPID': '42', 'Result': 'success',
                     'ExecMainCode': '0', 'ExecMainStatus': '0'}
        self.unit['ExecMainExitTimestampMonotonic'] = '0'
        self.files = {'/proc/sys/kernel/random/boot_id': BOOT,
                      '/sys/fs/cgroup' + GROUP + '/cgroup.events': 'populated 1\nfrozen 0\n',
                      '/sys/fs/cgroup' + GROUP + '/cgroup.procs': '42\n43\n'}
        for key, value in {'memory.max': '134217728', 'memory.swap.max': '0',
                           'pids.max': '16', 'cpu.max': '25000 100000'}.items():
            self.files['/sys/fs/cgroup' + GROUP + '/' + key] = value
        self.commands = []

    def query(self, command):
        self.commands.append(command)
        return '\n'.join(key + '=' + value for key, value in self.unit.items())

    def call(self, query=None, read=None):
        return observe(RECEIPT, query=query or self.query, read=read or self.files.__getitem__)

    def ended(self):
        self.unit.update(SubState='exited', MainPID='0', ExecMainCode='1')
        self.unit['ExecMainExitTimestampMonotonic'] = '123456'
        self.files['/sys/fs/cgroup' + GROUP + '/cgroup.events'] = 'populated 0\nfrozen 0\n'
        self.files['/sys/fs/cgroup' + GROUP + '/cgroup.procs'] = ''

    def test_running_requires_main_pid_and_group(self):
        observed = self.call()
        self.assertEqual(observed['state'], 'running')
        self.assertEqual(observed['process_count'], 2)
        self.assertEqual(len(self.commands), 2)
        self.assertTrue(all(command[:2] == ['/usr/bin/systemctl', 'show'] for command in self.commands))

    def test_empty_group_and_terminal_unit_prove_observed_end(self):
        self.ended()
        result = self.call()
        self.assertEqual(result['state'], 'ended')
        self.assertEqual(result['identity'], RECEIPT)

    def test_remaining_child_prevents_end(self):
        self.ended()
        self.files['/sys/fs/cgroup' + GROUP + '/cgroup.procs'] = '43\n'
        with self.assertRaises(ObservationError):
            self.call()

    def test_populated_subgroup_prevents_end(self):
        self.ended()
        self.files['/sys/fs/cgroup' + GROUP + '/cgroup.events'] = 'populated 1\nfrozen 0\n'
        self.assertEqual(self.call()['state'], 'unknown')

    def test_missing_cgroup_is_not_end_proof(self):
        self.ended()
        del self.files['/sys/fs/cgroup' + GROUP + '/cgroup.events']
        with self.assertRaises(ObservationError):
            self.call()

    def test_changed_invocation_or_boot_rejected(self):
        for key in ('InvocationID', 'ControlGroup', 'Id'):
            with self.subTest(key=key):
                original = self.unit[key]
                self.unit[key] = 'other'
                with self.assertRaises(ObservationError):
                    self.call()
                self.unit[key] = original
        self.files['/proc/sys/kernel/random/boot_id'] = 'd' * 32
        with self.assertRaises(ObservationError):
            self.call()

    def test_change_between_samples_rejected(self):
        calls = 0
        def query(command):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.unit['MainPID'] = '44'
            return self.query(command)
        with self.assertRaises(ObservationError):
            self.call(query=query)

    def test_duplicate_and_missing_properties_rejected(self):
        with self.assertRaises(ObservationError):
            self.call(query=lambda command: self.query(command) + '\nMainPID=42')
        del self.unit['InvocationID']
        with self.assertRaises(ObservationError):
            self.call()

    def test_unlimited_resources_rejected(self):
        self.files['/sys/fs/cgroup' + GROUP + '/memory.max'] = 'max'
        with self.assertRaises(ObservationError):
            self.call()

    def test_bad_receipt_never_queries_os(self):
        for receipt in ({}, dict(RECEIPT, run_id='../other'), dict(RECEIPT, boot_id=True)):
            with self.assertRaises(ObservationError):
                observe(receipt, query=self.query, read=self.files.__getitem__)
        self.assertEqual(self.commands, [])

    def test_pid_alone_is_insufficient(self):
        self.files['/sys/fs/cgroup' + GROUP + '/cgroup.procs'] = '43\n'
        with self.assertRaises(ObservationError):
            self.call()

    def test_absent_unit_and_oversized_output_rejected(self):
        self.unit['LoadState'] = 'not-found'
        with self.assertRaises(ObservationError):
            self.call()
        with self.assertRaises(ObservationError):
            self.call(query=lambda command: 'x' * 32769)

    def test_terminated_by_signal_is_not_success(self):
        self.ended()
        self.unit.update(ActiveState='failed', SubState='failed', Result='signal',
                         ExecMainCode='2', ExecMainStatus='9')
        result = self.call()
        self.assertEqual(result['state'], 'ended')
        self.assertEqual(result['unit_result'], 'signal')
        self.assertEqual(result['exit_status'], 9)

    def journal(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / 'journal.db'
        first = Journal(path, create=True)
        self.addCleanup(first.close)
        first.reserve('request-1', {'tenant_id': 'A', 'actor_id': 'alice',
            'release_id': 'release-1', 'profile_revision': 'aurelia-rest/1.0-draft.1'})
        first.started('request-1', RECEIPT)
        successor = Journal(path)
        self.addCleanup(successor.close)
        return successor

    def test_observed_end_releases_only_technical_slot(self):
        journal = self.journal()
        self.ended()
        release_observed(journal, 'request-1', RECEIPT,
                         query=self.query, read=self.files.__getitem__)
        state = journal.snapshot()
        self.assertIsNone(state['active'])
        self.assertEqual(state['events'][-1]['state'], 'released_unknown')

    def test_running_observation_cannot_release_journal(self):
        journal = self.journal()
        before = journal.snapshot()
        with self.assertRaises(ObservationError):
            release_observed(journal, 'request-1', RECEIPT,
                             query=self.query, read=self.files.__getitem__)
        self.assertEqual(journal.snapshot(), before)

    def test_missing_observation_cannot_release_journal(self):
        journal = self.journal()
        before = journal.snapshot()
        del self.files['/sys/fs/cgroup' + GROUP + '/cgroup.procs']
        with self.assertRaises(ObservationError):
            release_observed(journal, 'request-1', RECEIPT,
                             query=self.query, read=self.files.__getitem__)
        self.assertEqual(journal.snapshot(), before)

    def test_real_boot_id_format_normalized(self):
        self.files['/proc/sys/kernel/random/boot_id'] = 'cccccccc-cccc-cccc-cccc-cccccccccccc\n'
        self.assertEqual(self.call()['identity']['boot_id'], BOOT)

    def test_removed_group_requires_independent_absence_and_exit_record(self):
        self.ended()
        self.unit['ControlGroup'] = ''
        def read(path):
            if path.startswith('/sys/fs/cgroup'):
                raise FileNotFoundError(path)
            return self.files[path]
        calls = []
        def absent(path):
            calls.append(path)
            return True
        result = observe(RECEIPT, query=self.query, read=read, absent=absent)
        self.assertEqual(result['state'], 'ended')
        self.assertEqual(result['end_basis'], 'unit_and_removed_cgroup')
        self.assertIsNone(result['limits'])
        self.assertEqual(len(calls), 2)
        self.unit['ExecMainExitTimestampMonotonic'] = '0'
        with self.assertRaises(ObservationError):
            observe(RECEIPT, query=self.query, read=read, absent=absent)

    def test_missing_file_or_reappearing_group_never_proves_end(self):
        self.ended()
        def read(path):
            if path.startswith('/sys/fs/cgroup'):
                raise FileNotFoundError(path)
            return self.files[path]
        for answers in ((False, False), (True, False)):
            iterator = iter(answers)
            with self.assertRaises(ObservationError):
                observe(RECEIPT, query=self.query, read=read, absent=lambda path: next(iterator))

    def test_recorded_stop_timeout_with_sigkill_and_removed_group(self):
        self.ended()
        self.unit.update(ActiveState='failed', SubState='failed', Result='timeout',
                         ExecMainCode='2', ExecMainStatus='9', ControlGroup='')
        def read(path):
            if path.startswith('/sys/fs/cgroup'):
                raise FileNotFoundError(path)
            return self.files[path]
        result = observe(RECEIPT, query=self.query, read=read, absent=lambda path: True)
        self.assertEqual((result['state'], result['unit_result'], result['exit_status']),
                         ('ended', 'timeout', 9))
        for key, value in (('InvocationID', 'd' * 32), ('MainPID', '42')):
            original = self.unit[key]
            self.unit[key] = value
            with self.assertRaises(ObservationError):
                observe(RECEIPT, query=self.query, read=read, absent=lambda path: True)
            self.unit[key] = original


if __name__ == '__main__':
    unittest.main()
