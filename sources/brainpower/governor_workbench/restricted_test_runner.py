"""Standalone stdlib unittest adapter with a Python audit guard, not an OS sandbox.

Trusted control code launches this script with -I -S -B. Adversarial Python/native
code can exceed Python-level defenses; this is not a general hostile-code executor.
"""
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SENTINEL = 'GOVERNOR_STAGED_TEST_RESULT:'


def install_guard(staged, scratch):
    prefix = Path(sys.base_prefix).resolve()
    allowed_reads = (staged, scratch, prefix)
    blocked_imports = {'ctypes', '_ctypes', 'socket', '_socket', 'subprocess', '_posixsubprocess',
                       'multiprocessing', 'pty', 'winreg', '_winapi'}

    def checked(value, write=False):
        if isinstance(value, int):
            raise PermissionError('Raw file-descriptor access is not allowed by this test adapter.')
        if not isinstance(value, (str, bytes, os.PathLike)):
            raise PermissionError('Unrecognized filesystem access denied.')
        path = Path(os.fsdecode(value)).absolute()
        resolved = path.resolve()
        roots = (scratch,) if write else allowed_reads
        if not any(resolved == root or resolved.is_relative_to(root) for root in roots):
            raise PermissionError('Filesystem access outside the test adapter scope denied.')
        cursor = Path(path.anchor)
        for component in path.parts[1:]:
            cursor /= component
            try:
                info = cursor.lstat()
            except FileNotFoundError:
                continue
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise PermissionError('Filesystem redirection denied.')
            if stat.S_ISREG(info.st_mode) and info.st_nlink > 1:
                raise PermissionError('Hardlinked files denied.')

    def hook(event, args):
        if event == 'import':
            name = args[0].split('.')[0]
            if name in blocked_imports:
                raise PermissionError('Network, process and native-control modules are disabled.')
            if len(args) > 1 and args[1]:
                checked(args[1])
        elif (event.startswith(('socket.', 'subprocess.', 'ctypes.')) or event in {
                'os.system', 'os.exec', 'os.spawn', 'os.posix_spawn', 'os.posix_spawnp',
                'os.fork', 'os.forkpty', 'os.startfile', 'os.startfile/2', 'os.kill', 'os.killpg',
                'os.link', 'os.symlink', 'os.chroot', 'mmap.__new__', 'sys.addaudithook'}):
            raise PermissionError('Network, child processes and native control are disabled.')
        elif event == 'open':
            path, mode, flags = args
            writes = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC))
            checked(path, writes)
        elif event in ('os.listdir', 'os.scandir'):
            checked(args[0] if args[0] is not None else os.getcwd())
        elif event == 'os.chdir':
            checked(args[0])
        elif event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.chown', 'os.utime', 'os.truncate'):
            checked(args[0], True)
        elif event in ('os.rename', 'os.replace'):
            checked(args[0], True)
            checked(args[1], True)

    sys.addaudithook(hook)


def main():
    if len(sys.argv) != 4:
        return 2
    staged = Path(sys.argv[1]).resolve(strict=True)
    scratch = Path(sys.argv[2]).resolve(strict=True)
    completion_path = Path(sys.argv[3])
    if (not staged.is_dir() or not scratch.is_dir() or scratch.is_relative_to(staged)
            or staged.is_relative_to(scratch) or completion_path.parent != scratch.parent
            or completion_path.is_relative_to(scratch)):
        return 2
    # Open outside allowed test scratch before installing the guard. Tests cannot
    # reopen this path through ordinary filesystem APIs. Capture completion APIs
    # before importing tests; premature os._exit leaves an empty, invalid record.
    # This does not isolate the descriptor from adversarial same-process Python.
    completion = completion_path.open('xb')
    completion_write, completion_flush, completion_close = completion.write, completion.flush, completion.close
    completion_fd, sync_file, serialize = completion.fileno(), os.fsync, json.dumps
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(staged))
    tempfile.tempdir = str(scratch)
    for key in ('TMP', 'TEMP', 'TMPDIR'):
        os.environ[key] = str(scratch)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    install_guard(staged, scratch)
    summary = dict(count=0, errors=0, failures=0, skipped=0, success=False)
    try:
        suite = unittest.defaultTestLoader.discover(str(staged/'tests'), pattern='test*.py')
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        summary.update(count=result.testsRun, errors=len(result.errors), failures=len(result.failures),
                       skipped=len(result.skipped), success=result.testsRun > len(result.skipped) and result.wasSuccessful())
    except BaseException:
        summary['errors'] = 1
        print('Restricted unittest discovery or execution failed.', file=sys.stderr)
    encoded = serialize(summary, sort_keys=True).encode('utf-8')
    completion_write(encoded)
    completion_flush()
    sync_file(completion_fd)
    completion_close()
    print(SENTINEL + encoded.decode('utf-8'), flush=True)  # Log only; parent trusts the separate record.
    return 0 if summary['success'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
