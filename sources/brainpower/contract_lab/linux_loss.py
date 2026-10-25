"""Synthetic abrupt controller exit and bounded, non-replaying recovery."""
import os
import time
from .linux_runner import _report
from .linux_cleanup import cleanup
from .linux_observer import StopTransition, ObservationError


def launch_loss(controller, run, package, anchor, record, exit_now=os._exit):
    before = controller.backend.service_snapshot()
    if not before or any(state != 'active' for state in before.values()):
        raise ValueError('baseline_unverified')
    identity = controller.start(run, 'ignore_term', package, anchor)
    live = controller.backend.wait_pair(identity)
    if (live.get('identity') != identity or live.get('state') != 'running'
            or type(live.get('process_count')) is not int or live['process_count'] < 2):
        raise ValueError('pair_unverified')
    report = _report(run)
    report.update(status='controller_exit_prepared', identity=identity,
                  manifest_sha256=anchor, services_before=before, running_observation=live)
    record(report)
    exit_now(73)  # This process only; deliberately bypass Python cleanup, not systemd.
    raise ValueError('exit_returned')


def recover_loss(controller, run, anchor, launch, record, *, clock=time.monotonic, pause=time.sleep):
    report = _report(run)
    phase = 'binding'
    try:
        active = controller.journal.snapshot()['active']
        identity = launch.get('identity')
        if (launch.get('status') != 'controller_exit_prepared' or launch.get('run_id') != run
                or launch.get('manifest_sha256') != anchor or active is None
                or active['request_id'] != run or active['state'] != 'unknown'
                or active['binding']['release_id'] != anchor or active['identity'] != identity):
            raise ValueError('loss_binding_unverified')
        backend = controller.backend
        phase = 'service_baseline'
        if backend.service_snapshot() != launch['services_before']:
            raise ValueError('service_drift')
        phase = 'early_observation'
        early = backend.observe(identity)
        if early.get('identity') != identity or early.get('state') != 'running':
            raise ValueError('running_after_loss_unverified')
        report.update(identity=identity, unknown_while_running=True, early_observation=early)
        record(report)
        # This 30s watchdog observation is separate from the existing 5s stop proof.
        deadline = clock() + 30.0
        phase = 'watchdog_observation'
        while True:
            if clock() >= deadline:
                raise ValueError('watchdog_deadline')
            try:
                observation = backend.observe(identity)
            except StopTransition:
                report['stop_transition_observed'] = True
                pause(min(0.25, max(0.0, deadline - clock())))
                continue
            report['last_observation'] = observation
            if observation.get('identity') != identity or clock() >= deadline:
                raise ValueError('watchdog_end_unverified')
            if observation.get('state') == 'ended':
                break
            if observation.get('state') not in ('running', 'stopping'):
                raise ValueError('watchdog_state_unverified')
            pause(min(0.25, max(0.0, deadline - clock())))
        phase = 'service_comparison'
        if backend.service_snapshot() != launch['services_before']:
            raise ValueError('service_drift')
        phase = 'cleanup'
        result = cleanup(controller, run, anchor, identity, record)
        report.update(result, unknown_while_running=True, early_observation=early)
        if result['status'] == 'cleanup_verified':
            report['status'] = 'controller_loss_verified'
    except (OSError, ValueError, KeyError, TypeError) as exc:
        report.update(status='blocked', error='controller_loss_unverified', failed_phase=phase)
        if isinstance(exc, ObservationError) and str(exc) in {
                'observation_changed', 'observation_unverified', 'removed_end_unverified',
                'group_not_removed', 'identity_unverified', 'main_pid_unverified',
                'inconsistent_processes', 'group_identity_unverified', 'cgroup_unverified'}:
            report['observation_error'] = str(exc)
    record(report)
    return report
