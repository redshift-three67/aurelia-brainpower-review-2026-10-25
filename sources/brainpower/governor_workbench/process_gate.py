"""Trusted bootstrap: wait for kernel job assignment before launching payload.

Executed as an isolated stdlib script. EOF or malformed control input starts
nothing. The child inherits this helper's Windows job, not its control pipe.
"""
import json
import subprocess
import sys


def main():
    raw = sys.stdin.buffer.readline(65537)
    if len(raw) > 65536 or not raw.endswith(b'\n'):
        return 125
    try:
        argv = json.loads(raw)
        if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or '\0' in x for x in argv):
            return 125
        child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, close_fds=True,
                                 creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        return child.wait()
    except (ValueError, OSError):
        print('Auftragsprozess konnte nicht gestartet werden.', flush=True)
        return 125


if __name__ == '__main__':
    raise SystemExit(main())
