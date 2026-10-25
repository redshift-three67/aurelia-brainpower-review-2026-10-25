"""Durable synthetic controller tests; no OS ownership claims."""
from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from contract_lab.recovery import Journal, RecoveryError


IDENTITY = {'run_id': 'a' * 32, 'invocation_id': 'b' * 32,
            'boot_id': 'c' * 32, 'control_group': '/system.slice/aurelia-t3-' + 'a' * 32 + '.service'}
BINDING = {'tenant_id': 'A', 'actor_id': 'alice', 'release_id': 'release-1',
           'profile_revision': 'aurelia-rest/1.0-draft.1'}


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'recovery.db'
        self.journal = self.open(create=True)

    def open(self, **kwargs):
        journal = Journal(self.path, **kwargs)
        self.addCleanup(journal.close)
        return journal

    def reserve(self, request='request-1'):
        self.journal.reserve(request, BINDING)

    def test_reservation_is_committed_before_return(self):
        self.reserve()
        with closing(sqlite3.connect(self.path)) as reader:
            self.assertEqual(reader.execute('SELECT state FROM requests').fetchone()[0], 'reserved')
        self.assertEqual(self.journal.snapshot()['active']['binding'], BINDING)

    def test_duplicate_and_busy_do_not_add_events(self):
        self.reserve()
        before = self.journal.snapshot()
        for request in ('request-1', 'request-2'):
            with self.assertRaises(RecoveryError):
                self.reserve(request)
        self.assertEqual(before, self.journal.snapshot())

    def test_finish_requires_identity_and_abort_cannot_succeed(self):
        self.reserve()
        self.journal.started('request-1', IDENTITY)
        self.journal.abort('request-1')
        with self.assertRaises(RecoveryError):
            self.journal.finish('request-1', IDENTITY, 'succeeded')
        wrong = dict(IDENTITY, invocation_id='d' * 32)
        with self.assertRaises(RecoveryError):
            self.journal.finish('request-1', wrong, 'aborted')
        self.journal.finish('request-1', IDENTITY, 'aborted')
        self.assertIsNone(self.journal.snapshot()['active'])
        with self.assertRaises(RecoveryError):
            self.reserve()
        self.reserve('request-2')

    def test_takeover_fences_old_controller(self):
        self.reserve()
        successor = self.open()
        self.assertEqual(successor.snapshot()['active']['state'], 'unknown')
        with self.assertRaises(RecoveryError):
            self.journal.started('request-1', IDENTITY)
        with self.assertRaises(RecoveryError):
            successor.reserve('request-2', BINDING)

    def test_separate_process_restart_has_no_replay(self):
        self.journal.close()
        code = '''import sys
from contract_lab.recovery import Journal
j = Journal(sys.argv[1])
j.reserve('child-request', {'tenant_id':'A','actor_id':'alice','release_id':'release-1','profile_revision':'aurelia-rest/1.0-draft.1'})
import os
os._exit(0)
'''
        subprocess.run([sys.executable, '-B', '-c', code, str(self.path)], check=True,
                       timeout=15, capture_output=True)
        successor = self.open()
        state = successor.snapshot()
        self.assertEqual(state['active']['request_id'], 'child-request')
        self.assertEqual(state['active']['state'], 'unknown')
        self.assertIsNone(state['active']['identity'])
        self.assertNotIn('running', [event['state'] for event in state['events']])
        with self.assertRaises(RecoveryError):
            successor.release_unknown('child-request', IDENTITY, ended=True)

    def test_unknown_release_preserves_unknown_outcome(self):
        self.reserve()
        self.journal.started('request-1', IDENTITY)
        successor = self.open()
        for ended in (False, 1, 'yes'):
            with self.assertRaises(RecoveryError):
                successor.release_unknown('request-1', IDENTITY, ended=ended)
        successor.release_unknown('request-1', IDENTITY, ended=True)
        self.assertIsNone(successor.snapshot()['active'])
        self.assertEqual(successor.snapshot()['events'][-1]['state'], 'released_unknown')
        successor.reserve('request-2', BINDING)

    def test_bad_binding_and_identity_leave_state_unchanged(self):
        for binding in ({}, dict(BINDING, secret='never-store'), dict(BINDING, tenant_id=True)):
            with self.assertRaises(RecoveryError):
                self.journal.reserve('request-1', binding)
        self.reserve()
        before = self.journal.snapshot()
        for identity in ({}, dict(IDENTITY, run_id=True), dict(IDENTITY, control_group='/other')):
            with self.assertRaises(RecoveryError):
                self.journal.started('request-1', identity)
        self.assertEqual(before, self.journal.snapshot())

    def test_query_only_write_failure_blocks_reservation(self):
        self.journal.connection.execute('PRAGMA query_only=ON')
        with self.assertRaises(RecoveryError) as caught:
            self.reserve()
        self.assertEqual(str(caught.exception), 'journal_unavailable')
        self.assertIsNone(self.journal.snapshot()['active'])

    def test_full_database_rolls_back(self):
        self.journal.connection.execute('CREATE TABLE filler(data BLOB)')
        pages = self.journal.connection.execute('PRAGMA page_count').fetchone()[0]
        self.journal.connection.execute('PRAGMA max_page_count=' + str(pages))
        self.journal.connection.execute('''CREATE TRIGGER fill_on_reserve BEFORE INSERT ON requests
            BEGIN INSERT INTO filler VALUES(zeroblob(1048576)); END''')
        with self.assertRaises(RecoveryError) as caught:
            self.reserve()
        self.assertEqual(str(caught.exception), 'journal_unavailable')
        self.assertEqual(self.journal.snapshot(), {'active': None, 'events': []})
        self.journal.connection.execute('DROP TRIGGER fill_on_reserve')
        self.journal.connection.execute('DROP TABLE filler')
        self.reserve()
        self.assertEqual(self.journal.snapshot()['active']['state'], 'reserved')

    def test_competing_write_lock_cannot_reserve(self):
        with closing(sqlite3.connect(self.path, isolation_level=None)) as competing:
            competing.execute('BEGIN IMMEDIATE')
            with self.assertRaises(RecoveryError):
                self.reserve()
            competing.execute('ROLLBACK')
        self.assertEqual(self.journal.snapshot(), {'active': None, 'events': []})

    def test_full_journal_cannot_claim_recovery_success(self):
        self.test_event_limit_fails_closed()
        with self.assertRaises(RecoveryError):
            self.open()
        self.assertEqual(self.journal.snapshot()['active']['state'], 'reserved')

    def test_unknown_schema_version_rejected(self):
        self.journal.connection.execute('PRAGMA user_version=99')
        with self.assertRaises(RecoveryError):
            self.open()

    def test_completed_request_survives_reopen_without_replay(self):
        self.reserve()
        self.journal.started('request-1', IDENTITY)
        self.journal.finish('request-1', IDENTITY, 'succeeded')
        successor = self.open()
        self.assertIsNone(successor.snapshot()['active'])
        with self.assertRaises(RecoveryError):
            successor.reserve('request-1', BINDING)
        successor.reserve('request-2', BINDING)

    def test_no_completion_before_start_or_after_takeover(self):
        self.reserve()
        with self.assertRaises(RecoveryError):
            self.journal.finish('request-1', IDENTITY, 'succeeded')
        self.journal.started('request-1', IDENTITY)
        successor = self.open()
        with self.assertRaises(RecoveryError):
            self.journal.finish('request-1', IDENTITY, 'succeeded')
        with self.assertRaises(RecoveryError):
            successor.finish('request-1', IDENTITY, 'succeeded')
        self.assertEqual(successor.snapshot()['active']['state'], 'unknown')

    def test_event_limit_fails_closed(self):
        for number in range(33):
            request = 'request-' + str(number)
            self.journal.reserve(request, BINDING)
            self.journal.started(request, IDENTITY)
            self.journal.finish(request, IDENTITY, 'succeeded')
        self.journal.reserve('last', BINDING)
        with self.assertRaises(RecoveryError):
            self.journal.started('last', IDENTITY)
        self.assertEqual(self.journal.snapshot()['active']['state'], 'reserved')

    def test_missing_corrupt_and_existing_creation_rejected(self):
        with self.assertRaises(RecoveryError):
            self.open(create=True)
        missing = Path(self.temp.name) / 'missing.db'
        with self.assertRaises(RecoveryError):
            Journal(missing)
        self.assertFalse(missing.exists())
        corrupt = Path(self.temp.name) / 'corrupt.db'
        corrupt.write_bytes(b'not a database')
        with self.assertRaises(RecoveryError):
            Journal(corrupt)


if __name__ == '__main__':
    unittest.main()
