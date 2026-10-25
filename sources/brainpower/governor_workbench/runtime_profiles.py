"""One explicit built-in runtime profile with durable receipts, no replay.

This fixture is deliberately not a generic project command execution API.
Windows job handles own processes; journal IDs never authorize PID attachment.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import threading
import time
import urllib.request
import uuid

from .evidence import now, fingerprint
from .process_tree import start_owned_windows

STARTUP_SECONDS = 12  # Windows cold start can exceed five seconds; readiness remains mandatory.

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class RuntimeProfiles:
    def __init__(self, store, config):
        self.store, self.config = store, config
        self.lock = threading.RLock()
        self.closing = threading.Event()
        self.active = None
        with store.db() as db:
            db.executescript('CREATE TABLE IF NOT EXISTS runtime_instances(id TEXT PRIMARY KEY, body TEXT);'
                             'CREATE TABLE IF NOT EXISTS runtime_events(id INTEGER PRIMARY KEY AUTOINCREMENT, instance_id TEXT, body TEXT);')
            for record in db.execute('SELECT body FROM runtime_instances').fetchall():
                row = json.loads(record['body'])
                if row['status'] in ('starting', 'running'):
                    row.update(status='interrupted', ended_at=now(), reason='Dienstneustart: kein automatischer Wiederanlauf, keine PID-Übernahme.')
                    self._save(row, db)
        self.thread = threading.Thread(target=self._watch, daemon=True, name='runtime-owner')
        self.thread.start()

    def _save(self, row, db=None):
        if db is None:
            with self.store.db() as connection: self._save(row, connection)
            return
        body = json.dumps(row, ensure_ascii=False)
        db.execute('INSERT OR REPLACE INTO runtime_instances VALUES(?,?)', (row['id'], body))
        db.execute('INSERT INTO runtime_events(instance_id,body) VALUES(?,?)', (row['id'], body))

    def profile(self):
        sources = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                   for name in ('runtime_profiles.py', 'runtime_probe.py', 'process_tree.py', 'process_gate.py')}
        value = dict(id='local_probe', name='Lokaler Laufzeittest', port=self.config.get('runtime_probe_port', 8794),
                     host='127.0.0.1', max_seconds=3600, sources=sources)
        return dict(value, hash=fingerprint(value), supported=os.name == 'nt', product_execution=False)

    def state(self):
        with self.lock, self.store.db() as db:
            rows = db.execute('SELECT body FROM runtime_instances ORDER BY rowid DESC LIMIT 30').fetchall()
            return {'profiles': [self.profile()], 'instances': [json.loads(r['body']) for r in rows],
                    'automatic_restart': False, 'product_execution': False}

    def start(self, profile_id, expected_hash, cancel):
        from .jobs import JobCancelled
        with self.lock:
            if cancel.is_set(): raise JobCancelled('Laufzeitstart abgebrochen.')
            if self.closing.is_set(): raise ValueError('Laufzeitverwaltung wird beendet.')
            profile = self.profile()
            if not profile['supported']: raise ValueError('Laufzeitprofil benötigt Windows-Prozessbesitz.')
            if profile_id != profile['id'] or expected_hash != profile['hash']:
                raise ValueError('Laufzeitprofil geändert oder unbekannt. Ansicht neu laden.')
            if self.active is not None: raise ValueError('Ein eigener Laufzeitdienst ist bereits aktiv.')
            port = profile['port']
            if type(port) is not int or not 1024 <= port <= 65535 or port in (3000, self.config.get('port', 8787)):
                raise ValueError('Ungültiger Testport.')
            with socket.socket() as check:
                if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
                    check.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
                try: check.bind(('127.0.0.1', port))
                except OSError: raise ValueError('Testport belegt. Fremder Dienst bleibt unverändert.') from None
            row = dict(id=uuid.uuid4().hex, profile_id=profile_id, profile_hash=expected_hash,
                       port=port, status='starting', started_at=now(), ended_at=None,
                       readiness_verified=False, reason='', exit_code=None,
                       url=f'http://127.0.0.1:{port}/health')
            self._save(row)
            process = owner = None
            try:
                env = {k: os.environ[k] for k in ('SystemRoot', 'SYSTEMROOT', 'WINDIR', 'SystemDrive') if k in os.environ}
                process, owner = start_owned_windows(
                    [sys.executable, '-I', '-S', '-B', str(Path(__file__).with_name('runtime_probe.py')),
                     str(port), row['id']], self.config['data_dir'], env)
                self.active = (row, process, owner, time.monotonic())
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
                deadline = time.monotonic() + STARTUP_SECONDS
                while time.monotonic() < deadline:
                    if cancel.is_set() or self.closing.is_set(): raise JobCancelled('Laufzeitstart abgebrochen.')
                    if process.poll() is not None: raise ValueError('Prüfdienst vor Bereitschaft beendet.')
                    try:
                        with opener.open(row['url'], timeout=0.2) as response:
                            ready = json.loads(response.read(513))
                        if ready == {'service': 'governor-runtime-probe', 'instance_id': row['id']}:
                            if self.profile()['hash'] != expected_hash: raise ValueError('Profil während Start geändert.')
                            row.update(status='running', readiness_verified=True)
                            self._save(row)
                            return dict(row)
                    except (OSError, ValueError):
                        pass
                    cancel.wait(0.05)
                raise ValueError('Keine verifizierte Bereitschaft innerhalb des Startlimits.')
            except BaseException:
                if self.active is not None:
                    self._finish('failed', 'Start ohne Bereitschaft oder abgebrochen.')
                else:
                    row.update(status='failed', ended_at=now(), reason='Prozessstart fehlgeschlagen.')
                    self._save(row)
                raise

    def check(self, instance_id, cancel):
        """Explicit point-in-time observation, never a restart or approval."""
        from .jobs import JobCancelled
        with self.lock:
            if cancel.is_set(): raise JobCancelled('Laufzeitprüfung abgebrochen.')
            if self.closing.is_set() or self.active is None or self.active[0]['id'] != instance_id:
                raise ValueError('Keine passende eigene aktive Laufzeitinstanz.')
            row, process, _, _ = self.active
            success = False
            if row['status'] == 'running' and process.poll() is None and self.profile()['hash'] == row['profile_hash']:
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
                try:
                    with opener.open(row['url'], timeout=0.2) as response:
                        ready = json.loads(response.read(513))
                    success = (ready == {'service':'governor-runtime-probe', 'instance_id':instance_id}
                               and process.poll() is None and self.profile()['hash'] == row['profile_hash'])
                except (OSError, ValueError):
                    pass
            if cancel.is_set() or self.closing.is_set(): raise JobCancelled('Laufzeitprüfung abgebrochen.')
            row['last_check'] = dict(success=success, checked_at=now(), profile_hash=row['profile_hash'],
                                     summary='Bereitschaft zum Prüfzeitpunkt bestätigt.' if success else
                                     'Bereitschaft nicht bestätigt: Antwort, Prozess oder Profil stimmt nicht.')
            self._save(row)
            return dict(row)

    def _finish(self, status, reason):
        row, process, owner, _ = self.active
        owner.close()
        process.wait(timeout=5)
        process.stdout.close()
        row.update(status=status, ended_at=now(), reason=reason, exit_code=process.returncode)
        self._save(row)
        self.active = None
        return dict(row)

    def stop(self, instance_id):
        with self.lock:
            if self.active is not None and self.active[0]['id'] == instance_id:
                return self._finish('stopped', 'Ausdrücklicher Stop.')
            with self.store.db() as db:
                row = db.execute('SELECT body FROM runtime_instances WHERE id=?', (instance_id,)).fetchone()
            if row is None: raise ValueError('Unbekannte eigene Laufzeitinstanz.')
            return json.loads(row['body'])

    def _watch(self):
        while not self.closing.wait(0.5):
            with self.lock:
                if self.active is not None:
                    _, process, _, started = self.active
                    if process.poll() is not None:
                        self._finish('failed', 'Prozess unerwartet beendet; kein automatischer Wiederanlauf.')
                    elif time.monotonic() - started >= 3600:
                        self._finish('stopped', 'Maximale Laufzeit von einer Stunde erreicht.')

    def close(self):
        self.closing.set()
        with self.lock:
            if self.active is not None:
                self._finish('stopped', 'Governor wird beendet.')
        self.thread.join(timeout=2)
