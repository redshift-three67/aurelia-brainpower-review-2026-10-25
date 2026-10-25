"""Bounded read-only md state observation; pending writes are never accepted as healthy."""
import time


def sample_raid(read, *, pause=time.sleep, clock=time.monotonic):
    deadline = clock() + 1.0
    samples = []
    for _ in range(12):
        if samples and clock() >= deadline:
            break
        degraded, state = read()
        samples.append({'degraded': degraded, 'state': state})
        if type(degraded) is not int or degraded != 0:
            raise ValueError('RAID degraded_or_unverified')
        if clock() >= deadline:
            break
        if state in ('clean', 'active', 'active-idle'):
            return {'degraded': degraded, 'state': state, 'samples': samples}
        if state != 'write-pending':
            raise ValueError('RAID unhealthy_state: ' + str(state))
        pause(min(0.1, max(0.0, deadline - clock())))
    raise ValueError('RAID transition_not_resolved')
