"""Controller sequencing with an explicit backend. No default privileged executor."""
import os
from pathlib import Path

from .linux_probe import verify_package, start_command, stop_command
from .recovery import Journal


class ControllerError(ValueError):
    pass


class Lease:
    """OS lock on a persistent inode; never unlink a lock file during release."""
    def __init__(self, path):
        self.fd = None
        path = Path(path)
        try:
            if path.is_symlink():
                raise ControllerError('unsafe_lock_path')
            self.fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
            if os.fstat(self.fd).st_size == 0:
                os.write(self.fd, b'0')
            os.lseek(self.fd, 0, os.SEEK_SET)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.close()
            raise ControllerError('controller_locked_or_unavailable') from None

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None


class Controller:
    def __init__(self, journal_path, lock_path, backend, *, create=False):
        self.lease = Lease(lock_path)
        self.journal = None
        self.backend = backend
        try:
            self.journal = Journal(journal_path, create=create)
        except BaseException:
            self.close()
            raise

    def _open(self):
        if self.lease.fd is None or self.journal is None:
            raise ControllerError('controller_closed')

    @staticmethod
    def _identity(identity, run):
        try:
            stop_command(identity, identity)
            if identity['run_id'] != run:
                raise ValueError()
        except (TypeError, ValueError, KeyError):
            raise ControllerError('identity_unverified') from None
        return dict(identity)

    def start(self, run, mode, package, anchor):
        self._open()
        command = start_command(run, mode)
        verify_package(package, anchor)
        if self.journal.snapshot()['active'] is not None:
            raise ControllerError('recovery_required')
        # Backend must validate protected staging, runtime and unit absence, without starting.
        self.backend.preflight(run, package, anchor)
        verify_package(package, anchor)
        self.journal.reserve(run, {'tenant_id': 'synthetic', 'actor_id': 'controller',
                                  'release_id': anchor, 'profile_revision': 'aurelia-rest/1.0-draft.1'})
        try:
            identity = self._identity(self.backend.start(command), run)
            self.journal.started(run, identity)
            return identity
        except (OSError, ValueError):
            # A launch may have happened: preserve the reservation, never retry or delete.
            raise ControllerError('start_unconfirmed') from None

    def stop(self, run):
        self._open()
        active = self.journal.snapshot()['active']
        if (active is None or active['request_id'] != run or active['identity'] is None
                or active['state'] not in ('running', 'abort_requested', 'unknown')):
            raise ControllerError('owned_process_unverified')
        identity = self._identity(active['identity'], run)
        before = self.backend.observe(identity)
        if (type(before) is not dict or before.get('identity') != identity
                or before.get('state') != 'running'):
            raise ControllerError('stop_observation_unverified')
        if active['state'] == 'running':
            self.journal.abort(run)
        command = stop_command(identity, before['identity'])
        self.backend.stop(command)
        after = self.backend.observe(identity)
        if (type(after) is not dict or after.get('identity') != identity
                or after.get('state') != 'ended'):
            raise ControllerError('end_unverified')
        if active['state'] == 'unknown':
            self.journal.release_unknown(run, identity, ended=True)
        else:
            self.journal.finish(run, identity, 'aborted')
        return after

    def close(self):
        if self.journal is not None:
            self.journal.close()
            self.journal = None
        self.lease.close()
