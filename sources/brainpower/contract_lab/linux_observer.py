"""Read-only Linux observation; samples are evidence, not an atomic execution lease."""
from pathlib import Path
import re
import subprocess
import sys

from .linux_probe import stop_command
from .linux_worker import validate_limits


class ObservationError(ValueError):
    pass


class StopTransition(ObservationError):
    """Same bound identity/PID/config; only known systemd stop state changed."""


FIELDS = ('Id', 'LoadState', 'InvocationID', 'ControlGroup', 'ActiveState', 'SubState',
          'MainPID', 'Result', 'ExecMainCode', 'ExecMainStatus', 'ExecMainExitTimestampMonotonic')


def _text(value):
    if type(value) is not str or len(value) > 32768 or '\x00' in value:
        raise ObservationError('invalid_observation')
    return value


def _read(path):
    if sys.platform != 'linux':
        raise ObservationError('linux_required')
    with Path(path).open('r', encoding='ascii') as stream:
        return _text(stream.read(32769))


def _query(command):
    if sys.platform != 'linux':
        raise ObservationError('linux_required')
    # Fixed systemctl properties for one validated unit, not a user command.
    completed = subprocess.run(command, capture_output=True, text=True,
                               encoding='ascii', timeout=3, check=False)
    if completed.returncode:
        raise ObservationError('unit_unavailable')
    return _text(completed.stdout)


def _number(value):
    if not re.fullmatch('[0-9]{1,10}', value):
        raise ObservationError('invalid_number')
    return int(value)


def _unit(text, receipt):
    values = {}
    for line in _text(text).splitlines():
        key, separator, value = line.partition('=')
        if not separator or key not in FIELDS or key in values:
            raise ObservationError('invalid_unit_properties')
        values[key] = value
    if (set(values) != set(FIELDS) or values['LoadState'] != 'loaded'
            or values['Id'] != 'aurelia-t3-' + receipt['run_id'] + '.service'
            or values['InvocationID'] != receipt['invocation_id']
            or values['ControlGroup'] not in ('', receipt['control_group'])):
        raise ObservationError('identity_unverified')
    for key in ('MainPID', 'ExecMainCode', 'ExecMainStatus'):
        _number(values[key])
    return values


def _absent_group(path):
    if sys.platform != 'linux':
        raise ObservationError('linux_required')
    mounted = False
    for line in _read('/proc/self/mountinfo').splitlines():
        left, separator, right = line.partition(' - ')
        fields = left.split()
        if separator and len(fields) > 4 and fields[4] == '/sys/fs/cgroup' and right.split()[0] == 'cgroup2':
            mounted = True
    target = Path(path)
    if not mounted or not target.parent.is_dir():
        raise ObservationError('cgroup_mount_unverified')
    try:
        target.lstat()
    except FileNotFoundError:
        return True
    return False


def _removed(receipt, before, command, boot_before, query, read, absent):
    path = '/sys/fs/cgroup' + receipt['control_group']
    if absent(path) is not True:
        raise ObservationError('group_not_removed')
    after = _unit(query(command), receipt)
    boot_after = _boot(read('/proc/sys/kernel/random/boot_id'))
    stamp = after['ExecMainExitTimestampMonotonic']
    if (before == after and boot_before == boot_after == receipt['boot_id']
            and after['ActiveState'] == 'deactivating'
            and after['SubState'] in ('stop-sigterm', 'stop-sigkill', 'stop-post')
            and after['Result'] == 'timeout' and absent(path) is True):
        raise StopTransition('removed_group_still_stopping')
    if (before != after or boot_before != boot_after or boot_before != receipt['boot_id']
            or after['MainPID'] != '0' or after['ExecMainCode'] not in ('1', '2', '3')
            or not re.fullmatch('[0-9]{1,20}', stamp) or int(stamp) == 0
            or (after['ActiveState'], after['SubState']) not in
               (('active', 'exited'), ('inactive', 'dead'), ('failed', 'failed'))
            or absent(path) is not True):
        raise ObservationError('removed_end_unverified')
    return {'identity': receipt, 'state': 'ended', 'unit_result': after['Result'],
            'exit_code': _number(after['ExecMainCode']), 'exit_status': _number(after['ExecMainStatus']),
            'limits': None, 'end_basis': 'unit_and_removed_cgroup'}


def _boot(text):
    value = _text(text).strip()
    if re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', value):
        value = value.replace('-', '')
    if not re.fullmatch('[0-9a-f]{32}', value):
        raise ObservationError('invalid_boot')
    return value


def observe(receipt, *, query=None, read=None, absent=None):
    """Injected readers are test seams, never data supplied by HTTP/model output."""
    query = query or _query
    read = read or _read
    absent = absent or _absent_group
    try:
        stop_command(receipt, receipt)  # Validate all identity fields before any OS access.
        receipt = dict(receipt)
        command = ['/usr/bin/systemctl', 'show', '--no-pager',
                   '--property=' + ','.join(FIELDS),
                   'aurelia-t3-' + receipt['run_id'] + '.service']
        boot_before = _boot(read('/proc/sys/kernel/random/boot_id'))
        before = _unit(query(command), receipt)
        base = '/sys/fs/cgroup' + receipt['control_group'] + '/'
        try:
            limits = {key: _text(read(base + key)).strip()
                      for key in ('memory.max', 'memory.swap.max', 'pids.max', 'cpu.max')}
        except FileNotFoundError:
            return _removed(receipt, _unit(query(command), receipt), command, boot_before, query, read, absent)
        if before['ControlGroup'] != receipt['control_group']:
            raise ObservationError('group_identity_unverified')
        validate_limits(limits)
        try:
            event_text = _text(read(base + 'cgroup.events'))
            process_text = _text(read(base + 'cgroup.procs'))
        except FileNotFoundError:
            return _removed(receipt, _unit(query(command), receipt), command, boot_before, query, read, absent)
        events = {}
        for line in event_text.splitlines():
            fields = line.split()
            if len(fields) != 2 or fields[0] in events:
                raise ObservationError('invalid_cgroup_events')
            events[fields[0]] = _number(fields[1])
        if events.get('populated') not in (0, 1) or events.get('frozen') != 0:
            raise ObservationError('cgroup_unverified')
        pids = [_number(line) for line in process_text.splitlines()]
        if len(pids) != len(set(pids)) or any(pid == 0 for pid in pids):
            raise ObservationError('invalid_pids')
        after = _unit(query(command), receipt)
        boot_after = _boot(read('/proc/sys/kernel/random/boot_id'))
        if boot_before != boot_after or boot_before != receipt['boot_id']:
            raise ObservationError('observation_changed')
        if before != after:
            if ((before['ActiveState'], before['SubState']) in
                    (('deactivating', 'stop-sigterm'), ('deactivating', 'stop-sigkill'))
                    and (after['ActiveState'], after['SubState']) == ('failed', 'failed')
                    and before['Result'] == after['Result'] == 'timeout'
                    and after['MainPID'] == '0' and after['ExecMainCode'] == '2'
                    and after['ExecMainStatus'] == '9'):
                raise StopTransition('stop_terminal_transition')
            mutable = {'ActiveState', 'SubState', 'Result'}
            if (all(before[key] == after[key] for key in FIELDS if key not in mutable)
                    and (before['ActiveState'], before['SubState']) == ('active', 'running')
                    and (after['ActiveState'], after['SubState']) == ('deactivating', 'stop-sigterm')
                    and before['Result'] == 'success' and after['Result'] == 'timeout'
                    and after['MainPID'] != '0' and int(after['MainPID']) in pids
                    and events['populated'] == 1):
                raise StopTransition('stop_transition')
            raise ObservationError('observation_changed')
        pid = _number(after['MainPID'])
        if events['populated'] == 0 and (pids or pid):
            raise ObservationError('inconsistent_processes')
        if pid and pid not in pids:
            raise ObservationError('main_pid_unverified')
        state = 'unknown'
        if after['ActiveState'] == 'active' and after['SubState'] == 'running' and pid:
            state = 'running'
        if (after['ActiveState'] == 'deactivating'
                and after['SubState'] in ('stop-sigterm', 'stop-sigkill')
                and events['populated'] == 1):
            state = 'stopping'
        if (pid == 0 and not pids and events['populated'] == 0
                and (after['ActiveState'], after['SubState']) in
                (('active', 'exited'), ('inactive', 'dead'), ('failed', 'failed'))):
            state = 'ended'
        return {'identity': receipt, 'state': state, 'unit_result': after['Result'],
                'exit_code': _number(after['ExecMainCode']),
                'exit_status': _number(after['ExecMainStatus']), 'limits': limits,
                'process_count': len(pids)}
    except StopTransition:
        raise
    except ObservationError:
        raise
    except (OSError, KeyError, TypeError, ValueError, subprocess.SubprocessError):
        raise ObservationError('observation_unverified') from None


def release_observed(journal, request_id, receipt, *, query=None, read=None):
    """Explicit controller action. Does not retry work or turn unknown into success."""
    observation = observe(receipt, query=query, read=read)
    if observation['state'] != 'ended':
        raise ObservationError('end_unverified')
    journal.release_unknown(request_id, observation['identity'], ended=True)
    return observation
