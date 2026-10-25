"""Bounded, file-free CPU subprocess protocol; never returns private exceptions."""
import json
import sys
from .experimental_matrix import rank_experimental_rates, MatrixError

MAX_INPUT_BYTES = 6 * 1024 * 1024


def execute(envelope, expected_implementation_hash):
    if type(envelope) is not dict or set(envelope) != {'input', 'implementationHash'}:
        return {'error': 'worker_protocol'}
    if envelope['implementationHash'] != expected_implementation_hash:
        return {'error': 'implementation_changed'}
    payload = envelope['input']
    required = {'caseId','sourceSessionId','contextSnapshot','catalog','rates','originalSubset',
        'originalProvenance','formulaVersion','implementationHash','weight','pageStart','sourceDigest'}
    if type(payload) is not dict or set(payload) != required or payload['implementationHash'] != expected_implementation_hash:
        return {'error': 'worker_protocol'}
    try:
        result = rank_experimental_rates(payload['contextSnapshot'], payload['catalog'], payload['rates'], weight=payload['weight'])
        return {'result': result}
    except MatrixError:
        return {'error': 'cpu_unavailable'}
    except Exception:
        return {'error': 'worker_failed'}


def main():
    from .comparison_controller import implementation_hash
    try:
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        result = {'error': 'worker_protocol'} if len(raw) > MAX_INPUT_BYTES else execute(json.loads(raw), implementation_hash())
    except Exception:
        result = {'error': 'worker_protocol'}
    sys.stdout.write(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
