"""Explicit cleanup of an already ended, bound timeout test; never starts work."""
from .linux_runner import _report


def cleanup(controller, run, anchor, identity, record):
    report = _report(run)
    report.update(identity=dict(identity), manifest_sha256=anchor, journal_released=False)
    try:
        active = controller.journal.snapshot()['active']
        if (active is None or active['request_id'] != run or active['state'] != 'unknown'
                or active['identity'] != identity or identity['run_id'] != run
                or active['binding']['release_id'] != anchor):
            raise ValueError('recovery_binding_unverified')
        backend = controller.backend
        backend._package(run, anchor)
        before = backend.service_snapshot()
        report['services_before'] = before
        if not before or any(state != 'active' for state in before.values()):
            raise ValueError('service_baseline_unverified')
        proof = backend._prove_stopped(identity)
        if (not isinstance(proof, dict) or proof.get('identity') != identity
                or proof.get('state') != 'ended' or proof.get('unit_result') != 'timeout'
                or proof.get('exit_code') != 2 or proof.get('exit_status') != 9
                or proof.get('end_basis') != 'unit_and_removed_cgroup'):
            raise ValueError('timeout_end_unverified')
        report['observation'] = proof
        record(report)
        controller.journal.release_unknown(run, identity, ended=True)
        report.update(status='released_unknown', journal_released=True)
        record(report)
        # Reuse strict end checks for this recovery; this does not assert a new stop occurred.
        backend.stopped_identity = dict(identity)
        backend.retire(identity, anchor)
        report.update(package_removed=True, unit_retired=True)
        after = backend.service_snapshot()
        report.update(services_after=after, services_unchanged=before == after)
        if before != after:
            raise ValueError('service_drift')
        report['status'] = 'cleanup_verified'
    except (OSError, ValueError):
        report.update(status='blocked', error='cleanup_unverified')
    record(report)
    return report
