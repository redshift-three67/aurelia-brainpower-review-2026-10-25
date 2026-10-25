"""Synthetic durable slot. Callers supply observations; this proves no OS ownership."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import sqlite3
import time
import uuid


class RecoveryError(ValueError):
    pass


_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,95}')
_HEX = re.compile(r'[0-9a-f]{32}')
_TERMINAL = ('succeeded', 'failed', 'aborted', 'released_unknown')


def _binding(value):
    if (type(value) is not dict
            or value.keys() != {'tenant_id', 'actor_id', 'release_id', 'profile_revision'}
            or any(type(item) is not str or not _ID.fullmatch(item) for item in value.values())):
        raise RecoveryError('invalid_binding')
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def _identity(value):
    if (type(value) is not dict
            or value.keys() != {'run_id', 'invocation_id', 'boot_id', 'control_group'}
            or any(type(value[key]) is not str or not _HEX.fullmatch(value[key])
                   for key in ('run_id', 'invocation_id', 'boot_id'))
            or value['control_group'] != '/system.slice/aurelia-t3-' + value['run_id'] + '.service'):
        raise RecoveryError('invalid_identity')
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


class Journal:
    def __init__(self, path, *, create=False):
        self.connection = None
        self.owner = uuid.uuid4().hex
        path = Path(path).absolute()
        if type(create) is not bool or path.is_symlink():
            raise RecoveryError('invalid_path')
        try:
            if create:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                os.close(fd)
            self.connection = sqlite3.connect(path.as_uri() + '?mode=rw', uri=True,
                                              timeout=0.5, isolation_level=None)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute('PRAGMA synchronous=FULL')
            self.connection.execute('PRAGMA journal_mode=DELETE')
            self.connection.execute('PRAGMA max_page_count=256')
            if create:
                self.connection.executescript('''
                    BEGIN IMMEDIATE;
                    CREATE TABLE control(id INTEGER PRIMARY KEY CHECK(id=1), owner TEXT NOT NULL);
                    INSERT INTO control VALUES(1, 'initial');
                    CREATE TABLE requests(request_id TEXT PRIMARY KEY, binding TEXT NOT NULL,
                        identity TEXT, state TEXT NOT NULL, active INTEGER NOT NULL CHECK(active IN (0,1)));
                    CREATE UNIQUE INDEX one_active ON requests(active) WHERE active=1;
                    CREATE TABLE events(seq INTEGER PRIMARY KEY, request_id TEXT NOT NULL,
                        state TEXT NOT NULL, observed_ns INTEGER NOT NULL);
                    PRAGMA user_version=1;
                    COMMIT;
                ''')
            if (self.connection.execute('PRAGMA user_version').fetchone()[0] != 1
                    or self.connection.execute('PRAGMA quick_check').fetchone()[0] != 'ok'):
                raise RecoveryError('journal_unavailable')
            with self._transaction(fence=False):
                if self.connection.execute('SELECT count(*) FROM control WHERE id=1').fetchone()[0] != 1:
                    raise RecoveryError('journal_unavailable')
                self.connection.execute('UPDATE control SET owner=? WHERE id=1', (self.owner,))
                active = self.connection.execute('SELECT * FROM requests WHERE active=1').fetchone()
                if active is not None and active['state'] != 'unknown':
                    self._event(active['request_id'], 'unknown')
                    self.connection.execute("UPDATE requests SET state='unknown' WHERE active=1")
        except (OSError, sqlite3.Error):
            self.close()
            raise RecoveryError('journal_unavailable') from None
        except BaseException:
            self.close()
            raise

    @contextmanager
    def _transaction(self, fence=True):
        try:
            self.connection.execute('BEGIN IMMEDIATE')
            if fence:
                row = self.connection.execute('SELECT owner FROM control WHERE id=1').fetchone()
                if row is None or row[0] != self.owner:
                    raise RecoveryError('controller_superseded')
            yield
            self.connection.execute('COMMIT')
        except BaseException as error:
            if self.connection.in_transaction:
                self.connection.execute('ROLLBACK')
            if isinstance(error, sqlite3.Error):
                raise RecoveryError('journal_unavailable') from None
            raise

    def _event(self, request, state):
        if self.connection.execute('SELECT count(*) FROM events').fetchone()[0] >= 100:
            raise RecoveryError('journal_limit')
        self.connection.execute('INSERT INTO events(request_id,state,observed_ns) VALUES(?,?,?)',
                                (request, state, time.time_ns()))

    def reserve(self, request_id, binding):
        if type(request_id) is not str or not _ID.fullmatch(request_id):
            raise RecoveryError('invalid_request')
        binding = _binding(binding)
        with self._transaction():
            if self.connection.execute('SELECT 1 FROM requests WHERE active=1 OR request_id=?',
                                       (request_id,)).fetchone():
                raise RecoveryError('recovery_required_or_duplicate')
            self._event(request_id, 'reserved')
            self.connection.execute('INSERT INTO requests VALUES(?,?,NULL,?,1)',
                                    (request_id, binding, 'reserved'))

    def _transition(self, request_id, sources, target, identity=None):
        with self._transaction():
            row = self.connection.execute('SELECT * FROM requests WHERE request_id=? AND active=1',
                                          (request_id,)).fetchone()
            if row is None or row['state'] not in sources:
                raise RecoveryError('state_conflict')
            if target != 'running' and identity is not None and identity != row['identity']:
                raise RecoveryError('identity_conflict')
            self._event(request_id, target)
            self.connection.execute('UPDATE requests SET state=?,active=?,identity=? WHERE request_id=?',
                (target, int(target not in _TERMINAL), identity or row['identity'], request_id))

    def started(self, request_id, identity):
        self._transition(request_id, ('reserved',), 'running', _identity(identity))

    def abort(self, request_id):
        self._transition(request_id, ('running',), 'abort_requested')

    def finish(self, request_id, identity, outcome):
        if type(outcome) is not str or outcome not in ('succeeded', 'failed', 'aborted'):
            raise RecoveryError('invalid_outcome')
        sources = ('running',) if outcome == 'succeeded' else ('running', 'abort_requested')
        self._transition(request_id, sources, outcome, _identity(identity))

    def release_unknown(self, request_id, identity, *, ended):
        # Only a trusted future OS observer may supply this assertion; never HTTP input.
        if ended is not True:
            raise RecoveryError('end_unverified')
        self._transition(request_id, ('unknown',), 'released_unknown', _identity(identity))

    def snapshot(self):
        try:
            self.connection.execute('BEGIN')
            row = self.connection.execute('SELECT * FROM requests WHERE active=1').fetchone()
            active = dict(row) if row is not None else None
            if active is not None:
                active['binding'] = json.loads(active['binding'])
                active['identity'] = json.loads(active['identity']) if active['identity'] else None
            events = [dict(row) for row in self.connection.execute('SELECT * FROM events ORDER BY seq')]
            self.connection.execute('COMMIT')
            return {'active': active, 'events': events}
        except (sqlite3.Error, ValueError):
            if self.connection.in_transaction:
                self.connection.execute('ROLLBACK')
            raise RecoveryError('journal_unavailable') from None

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
