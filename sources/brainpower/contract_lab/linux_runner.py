"""Narrow normal-run/recovery orchestration. Reports are evidence, not product gates."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import uuid

from .linux_probe import _run as valid_run
from .linux_worker import validate_limits


def _report(run):
    valid_run(run)
    return {'schema': 1, 'run_id': run, 'utc': datetime.now(timezone.utc).isoformat(),
            'status': 'blocked', 'package_removed': False, 'services_unchanged': False}


def _ended(backend, identity):
    observation = backend.wait_ended(identity)
    if observation.get('identity') != identity or observation.get('state') != 'ended':
        raise ValueError('end_unverified')
    return observation


def run_normal(controller, run, package, anchor, *, mode='normal'):
    report = _report(run)
    report['manifest_sha256'] = anchor
    try:
        if mode not in ('normal', 'cpu'):
            raise ValueError('invalid_normal_mode')
        before = controller.backend.service_snapshot()
        report['services_before'] = before
        if not before or any(value != 'active' for value in before.values()):
            raise ValueError('baseline_unverified')
        identity = controller.start(run, mode, package, anchor)
        report['identity'] = identity
        observation = _ended(controller.backend, identity)
        report['observation'] = observation
        if (observation.get('unit_result') != 'success'
                or type(observation.get('exit_code')) is not int or observation['exit_code'] != 1
                or type(observation.get('exit_status')) is not int or observation['exit_status'] != 0):
            raise ValueError('normal_exit_unverified')
        if mode == 'cpu':
            from .linux_cpu import verify_cpu_evidence
            text = controller.backend._run(['/usr/bin/journalctl', '--no-pager', '-o', 'cat',
                '_SYSTEMD_INVOCATION_ID=' + identity['invocation_id']])
            report['cpu_evidence'] = verify_cpu_evidence(text, identity)
        after = controller.backend.service_snapshot()
        report['services_after'] = after
        report['services_unchanged'] = before == after
        if not report['services_unchanged']:
            raise ValueError('service_drift')
        controller.journal.finish(run, identity, 'succeeded')
        controller.backend.retire(identity, anchor)
        report['package_removed'] = True
        report['unit_retired'] = True
        report['services_after_retirement'] = controller.backend.service_snapshot()
        report['services_unchanged'] = before == report['services_after_retirement']
        if not report['services_unchanged']:
            raise ValueError('service_drift_after_retirement')
        report['status'] = 'cpu_verified' if mode == 'cpu' else 'process_completed'
    except (OSError, ValueError):
        report['error'] = 'run_unverified'
    return report


def recover(controller, run):
    report = _report(run)
    try:
        active = controller.journal.snapshot()['active']
        if (active is None or active['request_id'] != run or active['state'] != 'unknown'
                or active['identity'] is None):
            raise ValueError('recovery_unverified')
        observation = _ended(controller.backend, active['identity'])
        controller.journal.release_unknown(run, observation['identity'], ended=True)
        report.update(status='released_unknown', identity=observation['identity'], observation=observation)
        # Recovery never deletes evidence or claims that the original computation succeeded.
    except (OSError, ValueError):
        report['error'] = 'recovery_unverified'
    return report


def run_abort(controller, run, package, anchor):
    report = _report(run)
    report['manifest_sha256'] = anchor
    try:
        before = controller.backend.service_snapshot()
        report['services_before'] = before
        if not before or any(value != 'active' for value in before.values()):
            raise ValueError('baseline_unverified')
        identity = controller.start(run, 'ignore_term', package, anchor)
        report['identity'] = identity
        live = controller.backend.wait_pair(identity)
        if (live.get('identity') != identity or live.get('state') != 'running'
                or type(live.get('process_count')) is not int or live['process_count'] < 2):
            raise ValueError('process_pair_unverified')
        validate_limits(live.get('limits'))
        report['running_observation'] = live
        report['observation'] = controller.stop(run)
        report['services_after'] = controller.backend.service_snapshot()
        if report['services_after'] != before:
            raise ValueError('service_drift')
        controller.backend.retire(identity, anchor)
        report['package_removed'] = True
        report['unit_retired'] = True
        report['services_after_retirement'] = controller.backend.service_snapshot()
        report['services_unchanged'] = report['services_after_retirement'] == before
        if not report['services_unchanged']:
            raise ValueError('service_drift')
        report['status'] = 'abort_verified'
    except (OSError, ValueError):
        report['error'] = 'abort_unverified'
    return report


def write_report(path, report):
    data = json.dumps(report, sort_keys=True, indent=2, allow_nan=False).encode('utf-8') + b'\n'
    if len(data) > 65536:
        raise ValueError('report_limit')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def main(argv=None):
    from .linux_backend import LinuxBackend
    from .linux_controller import Controller
    args = sys.argv[1:] if argv is None else argv
    try:
        if len(args) != 3 or args[0] not in ('normal', 'recover', 'abort', 'memory', 'loss-launch', 'loss-recover', 'cpu'):
            raise ValueError('invalid_arguments')
        action, run, anchor = args
        valid_run(run)
        if not re.fullmatch('[0-9a-f]{64}', anchor):
            raise ValueError('invalid_anchor')
        backend = LinuxBackend()
        backend._platform()
        root = Path('/var/tmp/aurelia-t3-control')
        if not root.exists():
            root.mkdir(mode=0o700, parents=False, exist_ok=False)
        backend._protected(root, directory=True)
        journal = root / 'journal.db'
        lock = root / 'controller.lock'
        for path in (journal, lock):
            if path.exists() or path.is_symlink():
                backend._protected(path)
        if action in ('recover', 'loss-recover') and not journal.exists():
            raise ValueError('missing_journal')
        controller = Controller(journal, lock, backend, create=not journal.exists())
        try:
            if action == 'normal':
                report = run_normal(controller, run, Path('/opt/aurelia-t3/package'), anchor)
            elif action == 'cpu':
                report = run_normal(controller, run, Path('/opt/aurelia-t3/package-cpu20'), anchor, mode='cpu')
            elif action == 'abort':
                report = run_abort(controller, run, Path('/opt/aurelia-t3/package'), anchor)
            elif action == 'memory':
                from .linux_memory import run_memory
                def record(partial):
                    write_report(root / (run + '-checkpoint-' + uuid.uuid4().hex + '.json'), partial)
                report = run_memory(controller, run, Path('/opt/aurelia-t3/package'), anchor, record)
            elif action in ('loss-launch', 'loss-recover'):
                from .linux_loss import launch_loss, recover_loss
                launch_path = root / (run + '-loss-launch.json')
                if action == 'loss-launch':
                    launch_loss(controller, run, Path('/opt/aurelia-t3/package'), anchor,
                                lambda value: write_report(launch_path, value))
                    raise ValueError('loss_exit_returned')
                backend._protected(launch_path)
                raw = launch_path.read_bytes()
                if len(raw) > 65536:
                    raise ValueError('launch_report_limit')
                def record_loss(value):
                    write_report(root / (run + '-loss-proof-' + uuid.uuid4().hex + '.json'), value)
                report = recover_loss(controller, run, anchor, json.loads(raw), record_loss)
            else:
                active = controller.journal.snapshot()['active']
                if active is None or active['binding']['release_id'] != anchor:
                    raise ValueError('recovery_anchor_mismatch')
                report = recover(controller, run)
            report_path = root / (run + '-' + uuid.uuid4().hex + '.json')
            write_report(report_path, report)
        finally:
            controller.close()
        print(json.dumps({'status': report['status'], 'report': str(report_path)}))
        return 0 if report['status'] in ('process_completed', 'released_unknown', 'abort_verified', 'memory_verified', 'controller_loss_verified', 'cpu_verified') else 2
    except (OSError, ValueError):
        print('{"status":"blocked","error":"entry_unverified"}')
        return 2


if __name__ == '__main__':
    sys.exit(main())
