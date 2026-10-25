"""Validate scoped synthetic worker evidence, never infer throttling from quota alone."""
import json
from .linux_worker import validate_limits


def verify_cpu_evidence(text, identity):
    try:
        if not isinstance(text, str) or len(text) > 32768:
            raise ValueError('cpu_output_limit')
        samples = []
        for line in text.splitlines():
            if not line.startswith('{'):
                continue
            data = json.loads(line)
            if isinstance(data, dict) and data.get('status') == 'cpu_sample':
                samples.append(data)
        if len(samples) != 1:
            raise ValueError('cpu_sample_count')
        data = samples[0]
        if data['identity'] != identity:
            raise ValueError('cpu_identity')
        validate_limits(data['limits'])
        duration = data['elapsed_ns']
        if type(duration) is not int or not 4000000000 <= duration <= 8000000000:
            raise ValueError('cpu_duration')
        delta = {}
        for key in ('usage_usec', 'nr_periods', 'nr_throttled', 'throttled_usec'):
            before, after = data['before'][key], data['after'][key]
            if type(before) is not int or type(after) is not int or not 0 <= before < after:
                raise ValueError('cpu_counter')
            delta[key] = after - before
        if delta['nr_throttled'] > delta['nr_periods']:
            raise ValueError('cpu_periods')
        return {**data, 'delta': delta}
    except (KeyError, TypeError, AttributeError, ValueError):
        raise ValueError('cpu_evidence_unverified') from None
