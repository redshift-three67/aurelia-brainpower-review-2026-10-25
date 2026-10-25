"""Fixed synthetic Linux worker. Refuses execution outside its bounded cgroup."""
import json
import os
from pathlib import Path
import re
import signal
import sys
import time


def result():
    return {'data_class': 'synthetic', 'result': 14}


def validate_limits(values):
    try:
        memory = int(values['memory.max'])
        swap = int(values['memory.swap.max'])
        pids = int(values['pids.max'])
        quota, period = map(int, values['cpu.max'].split())
        if not (0 < memory <= 134217728 and swap == 0 and 0 < pids <= 16
                and 0 < quota and 0 < period and quota * 4 <= period):
            raise ValueError()
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ValueError('unsafe_limits') from None


def guard(run):
    if (sys.platform != 'linux' or not re.fullmatch('[0-9a-f]{32}', run)
            or os.geteuid() == 0):
        raise ValueError('unsafe_execution_context')
    expected = '/system.slice/aurelia-t3-' + run + '.service'
    groups = Path('/proc/self/cgroup').read_text().splitlines()
    if groups != ['0::' + expected]:
        raise ValueError('wrong_cgroup')
    base = Path('/sys/fs/cgroup' + expected)
    validate_limits({name: (base / name).read_text().strip()
                     for name in ('memory.max', 'memory.swap.max', 'pids.max', 'cpu.max')})
    if not re.fullmatch('[0-9a-f]{32}', os.environ.get('INVOCATION_ID', '')):
        raise ValueError('missing_invocation')


def cpu_sample(run):
    guard(run)
    group = '/system.slice/aurelia-t3-' + run + '.service'
    base = Path('/sys/fs/cgroup' + group)
    def counters():
        values = dict(line.split() for line in (base / 'cpu.stat').read_text().splitlines())
        return {key: int(values[key]) for key in
                ('usage_usec', 'nr_periods', 'nr_throttled', 'throttled_usec')}
    before = counters()
    started = time.monotonic_ns()
    # Single thread, four seconds wall time; systemd independently bounds lifetime to 20s.
    value = 0
    while time.monotonic_ns() - started < 4000000000:
        value = (value + 1) % 1048576
    elapsed = time.monotonic_ns() - started
    after = counters()
    guard(run)
    return {'status': 'cpu_sample', 'identity': {
                'run_id': run, 'invocation_id': os.environ['INVOCATION_ID'],
                'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip().replace('-', ''),
                'control_group': group},
            'elapsed_ns': elapsed, 'before': before, 'after': after,
            'limits': {key: (base / key).read_text().strip() for key in
                       ('cpu.max', 'memory.max', 'memory.swap.max', 'pids.max')}}


def main():
    if (len(sys.argv) != 4 or sys.argv[2] not in ('normal', 'ignore_term', 'memory', 'cpu')
            or sys.argv[3] != '--guarded'):
        raise ValueError('invalid_mode')
    guard(sys.argv[1])
    mode = sys.argv[2]
    print(json.dumps({'status': 'guard_verified', 'mode': mode}), flush=True)
    if mode == 'normal':
        print(json.dumps(result()), flush=True)
    elif mode == 'cpu':
        print(json.dumps(cpu_sample(sys.argv[1])), flush=True)
    elif mode == 'ignore_term':
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        child = os.fork()
        if child == 0:
            while True:
                time.sleep(0.1)
        print(json.dumps({'status': 'child_started'}), flush=True)
        while True:
            time.sleep(0.1)
    else:
        # Bounded demand above MemoryMax; never grows without a fixed upper bound.
        blocks = []
        for _ in range(160):
            blocks.append(bytearray(1024 * 1024))
        raise ValueError('memory_limit_not_observed')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, MemoryError):
        print('{"status":"probe_failed"}', flush=True)
        sys.exit(2)
