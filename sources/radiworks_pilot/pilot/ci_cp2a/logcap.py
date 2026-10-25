"""Capture only bounded own-command output; no process or product execution."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def capture(source, path, maximum=8 * 1024 * 1024):
    if maximum <= 0:
        raise ValueError('positive log limit required')
    total = 0
    h = hashlib.sha256()
    with path.open('xb') as sink:
        while True:
            block = source.read(min(65536, maximum - total + 1))
            if not block:
                return {'bytes': total, 'sha256': h.hexdigest(), 'truncated': False}
            allowed = block[:maximum-total]
            sink.write(allowed)
            h.update(allowed)
            total += len(allowed)
            if len(allowed) != len(block):
                return {'bytes': total, 'sha256': h.hexdigest(), 'truncated': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    result = capture(sys.stdin.buffer, args.path)
    print(json.dumps({'log': args.path.name, **result}))
    if result['truncated']:
        raise SystemExit(3)
