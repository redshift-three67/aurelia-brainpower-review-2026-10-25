"""One bounded memory probe; expected worker failure is not application success."""
from .linux_runner import _report


def run_memory(controller, run, package, anchor, record):
    report = _report(run)
    report['manifest_sha256'] = anchor
    try:
        backend = controller.backend
        before = backend.service_snapshot()
        report['services_before'] = before
        if not before or any(state != 'active' for state in before.values()):
            raise ValueError('baseline_unverified')
        identity = controller.start(run, 'memory', package, anchor)
        report['identity'] = identity
        ended = backend.wait_ended(identity)
        if ended.get('identity') != identity or ended.get('state') != 'ended':
            raise ValueError('end_unverified')
        proof = backend.memory_evidence(identity)
        if (proof.get('identity') != identity or proof.get('state') != 'ended'
                or proof.get('unit_result') != 'oom-kill'
                or proof.get('exit_code') != 2 or proof.get('exit_status') != 9):
            raise ValueError('oom_unverified')
        report['observation'] = proof
        record(report)
        if backend.service_snapshot() != before:
            raise ValueError('service_drift')
        controller.journal.finish(run, identity, 'failed')
        report['worker_outcome'] = 'failed'
        record(report)
        backend.retire_oom(identity, anchor)
        report.update(package_removed=True, unit_retired=True)
        after = backend.service_snapshot()
        report.update(services_after=after, services_unchanged=before == after)
        if before != after:
            raise ValueError('service_drift')
        report['status'] = 'memory_verified'
    except (OSError, ValueError):
        report['error'] = 'memory_unverified'
    return report
