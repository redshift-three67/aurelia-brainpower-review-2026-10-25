"""Local package/command preparation only. Does not execute privileged commands."""
import hashlib
import json
from pathlib import Path
import re


class ProbeError(ValueError):
    pass


PROPERTIES = {
    'DynamicUser': 'yes', 'NoNewPrivileges': 'yes', 'ProtectSystem': 'strict',
    'ProtectHome': 'yes', 'PrivateTmp': 'yes', 'PrivateNetwork': 'yes',
    'MemoryMax': '128M', 'MemorySwapMax': '0', 'TasksMax': '16', 'CPUQuota': '25%',
    'RuntimeMaxSec': '20s', 'TimeoutStopSec': '2s', 'KillMode': 'control-group',
    'SendSIGKILL': 'yes', 'Restart': 'no', 'Type': 'exec',
    'RemainAfterExit': 'yes', 'OOMPolicy': 'kill',
}
RUNTIME = {'python': '3.12.3', 'systemd_major': 255}


def _run(value):
    if type(value) is not str or not re.fullmatch('[0-9a-f]{32}', value):
        raise ProbeError('invalid_run')
    return value


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ProbeError('duplicate_key')
        value[key] = item
    return value


def build_package(root):
    root = Path(root)
    try:
        root.mkdir(parents=False, exist_ok=False)
        worker = Path(__file__).with_name('linux_worker.py').read_bytes()
        (root / 'linux_worker.py').write_bytes(worker)
        manifest = {'schema': 1, 'runtime': RUNTIME, 'properties': PROPERTIES,
                    'files': {'linux_worker.py': _digest(worker)}}
        data = json.dumps(manifest, sort_keys=True, indent=2).encode('utf-8') + b'\n'
        (root / 'manifest.json').write_bytes(data)
        return _digest(data)
    except OSError:
        raise ProbeError('package_creation_failed') from None


def verify_package(root, expected_manifest_hash):
    root = Path(root)
    try:
        if (type(expected_manifest_hash) is not str
                or not re.fullmatch('[0-9a-f]{64}', expected_manifest_hash)
                or root.is_symlink()
                or {item.name for item in root.iterdir()} != {'manifest.json', 'linux_worker.py'}):
            raise ProbeError('invalid_package')
        for name in ('manifest.json', 'linux_worker.py'):
            item = root / name
            if item.is_symlink() or not item.is_file() or item.stat().st_size > 65536:
                raise ProbeError('invalid_package')
        data = (root / 'manifest.json').read_bytes()
        if _digest(data) != expected_manifest_hash:
            raise ProbeError('manifest_drift')
        manifest = json.loads(data, object_pairs_hook=_object)
        if (type(manifest) is not dict
                or manifest.keys() != {'schema', 'runtime', 'properties', 'files'}
                or type(manifest['schema']) is not int or manifest['schema'] != 1
                or json.dumps(manifest['runtime'], sort_keys=True) != json.dumps(RUNTIME, sort_keys=True)
                or manifest['properties'] != PROPERTIES
                or manifest['files'] != {'linux_worker.py': _digest((root / 'linux_worker.py').read_bytes())}):
            raise ProbeError('contract_drift')
        return manifest
    except (OSError, ValueError, TypeError) as error:
        if isinstance(error, ProbeError):
            raise
        raise ProbeError('invalid_package') from None


def start_command(run, mode):
    run = _run(run)
    if type(mode) is not str or mode not in ('normal', 'ignore_term', 'memory', 'cpu'):
        raise ProbeError('invalid_mode')
    return ['/usr/bin/systemd-run', '--unit=aurelia-t3-' + run + '.service',
            '--service-type=exec',
            *['--property=' + key + '=' + value for key, value in sorted(PROPERTIES.items())],
            '--property=BindReadOnlyPaths=/var/tmp/aurelia-t3/' + run
            + '/linux_worker.py:/run/aurelia-t3-worker.py',
            '--', '/usr/bin/python3', '-I', '-B',
            '/run/aurelia-t3-worker.py', run, mode, '--guarded']


def stop_command(receipt, observation):
    keys = {'run_id', 'invocation_id', 'boot_id', 'control_group'}
    if type(receipt) is not dict or type(observation) is not dict or receipt.keys() != keys:
        raise ProbeError('invalid_receipt')
    run = _run(receipt['run_id'])
    for key in ('invocation_id', 'boot_id'):
        _run(receipt[key])
    if (receipt['control_group'] != '/system.slice/aurelia-t3-' + run + '.service'
            or receipt != observation):
        raise ProbeError('identity_conflict')
    return ['/usr/bin/systemctl', 'stop', 'aurelia-t3-' + run + '.service']
