"""Fixed Linux test backend. Requires root and a separately approved controller call."""
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

from .linux_probe import RUNTIME, _run as valid_run, verify_package, start_command, stop_command
from .linux_observer import observe, _boot, _read, _absent_group, FIELDS


class BackendError(ValueError):
    pass


def wait_for_end(sample, identity, *, clock=time.monotonic, pause=time.sleep):
    deadline = clock() + 5.0
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            raise BackendError('observation_deadline')
        result = sample(remaining)
        if result.get('identity') != identity or clock() >= deadline:
            raise BackendError('observation_unverified')
        if result.get('state') == 'ended':
            return result
        if result.get('state') != 'running':
            raise BackendError('observation_unverified')
        pause(min(0.1, max(0.0, deadline - clock())))


def wait_for_pair(sample, identity, *, clock=time.monotonic, pause=time.sleep):
    deadline = clock() + 5.0
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            raise BackendError('pair_deadline')
        result = sample(remaining)
        if (result.get('identity') != identity or result.get('state') != 'running'
                or clock() >= deadline):
            raise BackendError('pair_unverified')
        if type(result.get('process_count')) is int and result['process_count'] >= 2:
            return result
        pause(min(0.1, max(0.0, deadline - clock())))


def verify_retired(identity, text, boot, absent):
    values = {}
    for line in text.splitlines():
        key, separator, value = line.partition('=')
        if not separator or key in values:
            raise BackendError('unit_retirement_unverified')
        values[key] = value
    if (set(values) != {'Id', 'LoadState', 'InvocationID', 'ActiveState', 'MainPID'}
            or values['Id'] != 'aurelia-t3-' + identity['run_id'] + '.service'
            or values['ActiveState'] != 'inactive' or values['MainPID'] != '0'
            or boot != identity['boot_id'] or absent is not True
            or values['LoadState'] not in ('loaded', 'not-found')
            or values['LoadState'] == 'loaded' and values['InvocationID'] != identity['invocation_id']):
        raise BackendError('unit_retirement_unverified')


class LinuxBackend:
    def __init__(self):
        self.base = Path('/var/tmp/aurelia-t3')
        self.prepared = None
        self.identity = None
        self.attempted = False
        self.stopped_identity = None

    @staticmethod
    def _platform():
        if sys.platform != 'linux' or os.geteuid() != 0:
            raise BackendError('linux_root_required')

    @staticmethod
    def _protected(path, directory=False):
        info = path.lstat()
        kind = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
        if (not kind or info.st_uid != 0 or info.st_mode & 0o022
                or not directory and info.st_nlink != 1):
            raise BackendError('unsafe_path')

    @staticmethod
    def _run(command, timeout=3):
        try:
            completed = subprocess.run(command, capture_output=True, text=True,
                                       encoding='utf-8', timeout=timeout, check=False)
            if completed.returncode or len(completed.stdout) > 32768:
                raise BackendError('command_unverified')
            return completed.stdout
        except (OSError, UnicodeError, subprocess.SubprocessError):
            raise BackendError('command_unverified') from None

    def _absent(self, run):
        text = self._run(['/usr/bin/systemctl', 'show', '--no-pager', '--property=LoadState',
                         'aurelia-t3-' + run + '.service'])
        if text.strip() != 'LoadState=not-found':
            raise BackendError('unit_exists_or_unverified')

    def _package(self, run, anchor):
        self._protected(self.base, directory=True)
        target = self.base / run
        self._protected(target, directory=True)
        for name in ('linux_worker.py', 'manifest.json'):
            self._protected(target / name)
        verify_package(target, anchor)
        return target

    def preflight(self, run, package, anchor):
        self._platform()
        valid_run(run)
        verify_package(package, anchor)
        if self.prepared is not None:
            raise BackendError('already_prepared')
        if self._run(['/usr/bin/python3', '--version']).strip() != 'Python ' + RUNTIME['python']:
            raise BackendError('runtime_drift')
        lines = self._run(['/usr/bin/systemctl', '--version']).splitlines()
        version = lines[0].split() if lines else []
        if len(version) < 2 or version[:2] != ['systemd', str(RUNTIME['systemd_major'])]:
            raise BackendError('runtime_drift')
        self._absent(run)
        # /var/tmp is deliberately shared; protect the newly created private child.
        if not self.base.exists():
            self.base.mkdir(mode=0o700, parents=False, exist_ok=False)
        self._protected(self.base, directory=True)
        target = self.base / run
        try:
            target.mkdir(mode=0o700, exist_ok=False)
        except OSError:
            raise BackendError('staging_exists_or_unavailable') from None
        for name in ('linux_worker.py', 'manifest.json'):
            raw = (Path(package) / name).read_bytes()
            if len(raw) > 65536:
                raise BackendError('oversized_package')
            fd = os.open(target / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(target / name, 0o644)
        self._package(run, anchor)
        self.prepared = (run, anchor)

    def start(self, command):
        self._platform()
        if self.prepared is None or self.attempted:
            raise BackendError('not_prepared')
        run, anchor = self.prepared
        if command not in [start_command(run, mode) for mode in ('normal', 'ignore_term', 'memory', 'cpu')]:
            raise BackendError('invalid_command')
        self._package(run, anchor)
        self._absent(run)
        self.attempted = True
        self._run(command, timeout=5)
        text = self._run(['/usr/bin/systemctl', 'show', '--no-pager',
                          '--property=' + ','.join(FIELDS), 'aurelia-t3-' + run + '.service'])
        values = {}
        for line in text.splitlines():
            key, separator, value = line.partition('=')
            if not separator or key in values:
                raise BackendError('identity_unverified')
            values[key] = value
        group = values.get('ControlGroup')
        identity = {'run_id': run, 'invocation_id': values.get('InvocationID'),
                    'control_group': '/system.slice/aurelia-t3-' + run + '.service' if group == '' else group,
                    'boot_id': _boot(_read('/proc/sys/kernel/random/boot_id'))}
        stop_command(identity, identity)
        observation = self.observe(identity)
        if group == '' and (observation.get('state') != 'ended'
                            or observation.get('end_basis') != 'unit_and_removed_cgroup'):
            raise BackendError('fast_exit_unverified')
        if observation['state'] not in ('running', 'ended'):
            raise BackendError('start_unverified')
        self.identity = identity
        return dict(identity)

    def observe(self, identity):
        self._platform()
        if self.stopped_identity == identity:
            proof = self._prove_stopped(identity)
            if proof is not None:
                return proof
            return {'identity': dict(identity), 'state': 'ended', 'limits': None,
                    'end_basis': 'scoped_stop_and_removed_cgroup'}
        result = observe(identity, query=self._run)
        self.identity = dict(result['identity'])
        return result

    def wait_ended(self, identity):
        return self._wait(identity, wait_for_end)

    def wait_pair(self, identity):
        return self._wait(identity, wait_for_pair)

    def _wait(self, identity, waiter):
        self._platform()
        def sample(remaining):
            deadline = time.monotonic() + remaining
            def query(command):
                left = deadline - time.monotonic()
                if left <= 0:
                    raise BackendError('observation_deadline')
                return self._run(command, timeout=min(3.0, left))
            return observe(identity, query=query)
        return waiter(sample, identity)

    def _remove_unit(self, identity):
        if self.stopped_identity == identity:
            proof = self._prove_stopped(identity)
            if proof is not None:
                self._run(['/usr/bin/systemctl', 'reset-failed',
                           'aurelia-t3-' + identity['run_id'] + '.service'])
                self._prove_retired(identity)
            return
        fresh = self.observe(identity)
        if fresh['state'] != 'ended' or fresh['identity'] != identity:
            raise BackendError('end_unverified')
        self._run(stop_command(identity, fresh['identity']), timeout=5)
        self._prove_retired(identity)

    def _prove_stopped(self, identity):
        try:
            self._prove_retired(identity)
            return None
        except BackendError:
            # A stop timeout can end both processes yet retain a failed unit.
            proof = observe(identity, query=self._run)
            if (proof.get('identity') != identity or proof.get('state') != 'ended'
                    or proof.get('end_basis') != 'unit_and_removed_cgroup'
                    or proof.get('unit_result') != 'timeout'
                    or proof.get('exit_code') != 2 or proof.get('exit_status') != 9):
                raise BackendError('stop_end_unverified')
            return proof

    def _prove_retired(self, identity):
        text = self._run(['/usr/bin/systemctl', 'show', '--no-pager',
                          '--property=Id,LoadState,InvocationID,ActiveState,MainPID',
                          'aurelia-t3-' + identity['run_id'] + '.service'])
        verify_retired(identity, text, _boot(_read('/proc/sys/kernel/random/boot_id')),
                       _absent_group('/sys/fs/cgroup' + identity['control_group']))

    def stop(self, command):
        self._platform()
        if self.identity is None:
            raise BackendError('identity_unbound')
        fresh = self.observe(self.identity)
        if fresh['state'] != 'running' or command != stop_command(self.identity, fresh['identity']):
            raise BackendError('stop_unverified')
        self._run(command, timeout=5)
        self._prove_stopped(self.identity)
        self.stopped_identity = dict(self.identity)

    def retire(self, identity, anchor):
        self._platform()
        stop_command(identity, identity)
        target = self._package(identity['run_id'], anchor)
        fresh = self.observe(identity)
        if fresh.get('identity') != identity or fresh.get('state') != 'ended':
            raise BackendError('end_unverified')
        self._remove_unit(identity)
        # No recursion, no wildcard, no journal deletion. Unknown files block verification above.
        for name in ('linux_worker.py', 'manifest.json'):
            (target / name).unlink()
        target.rmdir()

    def memory_evidence(self, identity):
        self._platform()
        stop_command(identity, identity)
        before = self.observe(identity)
        text = self._run(['/usr/bin/systemctl', 'show', '--no-pager',
                          '--property=InvocationID,MemoryMax,MemorySwapMax',
                          'aurelia-t3-' + identity['run_id'] + '.service'])
        values = {}
        for line in text.splitlines():
            key, separator, value = line.partition('=')
            if not separator or key in values:
                raise BackendError('memory_evidence_unverified')
            values[key] = value
        after = self.observe(identity)
        if (before != after or after.get('identity') != identity or after.get('state') != 'ended'
                or after.get('unit_result') != 'oom-kill'
                or after.get('exit_code') != 2 or after.get('exit_status') != 9
                or values != {'InvocationID': identity['invocation_id'],
                              'MemoryMax': '134217728', 'MemorySwapMax': '0'}):
            raise BackendError('memory_evidence_unverified')
        return {**after, 'memory_max': 134217728, 'memory_swap_max': 0}

    def retire_oom(self, identity, anchor):
        self._platform()
        stop_command(identity, identity)
        target = self._package(identity['run_id'], anchor)
        self.memory_evidence(identity)
        self._run(['/usr/bin/systemctl', 'reset-failed',
                   'aurelia-t3-' + identity['run_id'] + '.service'])
        self._prove_retired(identity)
        for name in ('linux_worker.py', 'manifest.json'):
            (target / name).unlink()
        target.rmdir()

    def service_snapshot(self):
        self._platform()
        values = {}
        for unit in ('ssh.service', 'wg-quick@wg-admin.service', 'gdm.service'):
            state = self._run(['/usr/bin/systemctl', 'show', '--no-pager',
                               '--property=ActiveState', '--value', unit]).strip()
            if state not in ('active', 'inactive', 'failed', 'activating', 'deactivating', 'reloading'):
                raise BackendError('service_state_unverified')
            values[unit] = state
        return values
