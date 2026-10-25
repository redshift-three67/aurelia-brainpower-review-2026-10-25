"""Explicit bounded pilot writes with durable claims and conflict-aware recovery.

No shell, models, git, automatic replay or OS adversarial isolation. The caller
must enforce project policy and explicit operator approval. Backups are exclusive
files sealed in the journal, not immutable against a hostile local account.
"""
import json
import copy
import os
from pathlib import Path
import uuid

from .evidence import now
from .execution_workspace import (_components, _read, _root, _sha,
                                  MAX_MANIFEST_BYTES, MAX_TOTAL_BYTES)


def _hash(data):
    return None if data is None else _sha(data)


class PilotApply:
    def __init__(self, store, stager, allowed_roots=None):
        self.store, self.stager = store, stager
        self.allowed_roots = tuple(allowed_roots or ())
        self.base = stager.base.parent/'pilot-apply-backups'
        with store.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS pilot_apply_proposals(id TEXT PRIMARY KEY, body TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS pilot_apply_transactions(
                    id TEXT PRIMARY KEY, stage_id TEXT UNIQUE NOT NULL, status TEXT NOT NULL, body TEXT NOT NULL);
            ''')

    def _allowed(self, value, identity=None):
        root, actual = _root(value)
        allowed = [os.path.normcase(str(_root(item)[0])) for item in self.allowed_roots]
        if os.path.normcase(str(root)) not in allowed or (identity is not None and identity != actual):
            raise ValueError('Apply ist nur in ausdrücklich erlaubter isolierter Pilotwurzel zulässig.')
        if root == self.base or root.is_relative_to(self.base) or self.base.is_relative_to(root):
            raise ValueError('Backups und Pilotprojekt müssen getrennt sein.')
        return root

    def _evidence(self, stage_id, seal, test_id, scope):
        test = self.store.job(test_id); result = test.get('result') or {}
        from .staged_tests import require_current_adapter
        require_current_adapter(result)
        if (test['action'] != 'stage_test' or test['status'] != 'completed'
                or any(result.get(k) is not True for k in ('verified','success','completion_verified','sources_verified'))
                or result.get('stale') or result.get('stage_id') != stage_id
                or result.get('manifest_hash') != seal or result.get('scope_hash') != scope):
            raise ValueError('Frischer verifizierter erfolgreicher Staging-Test erforderlich.')
        parent_id = test['request'].get('stage_job_id')
        if not parent_id or result.get('stage_job_id') != parent_id:
            raise ValueError('Testreferenz stimmt nicht mit dem Journal überein.')
        self.store.require_latest_stage_test(test['id'],parent_id)
        parent = self.store.job(parent_id); source = parent.get('result') or {}
        stage = source.get('stage') or {}
        if (parent['action'] != 'scope_patch' or parent['status'] != 'completed'
                or source.get('scope_hash') != scope or stage.get('id') != stage_id
                or stage.get('manifest_hash') != seal or parent['project_id'] != test['project_id']):
            raise ValueError('Test und Änderungsvorschlag sind nicht quellengebunden.')
        self.stager.verify_source(stage_id, seal)
        manifest = json.loads(_read(self.stager.base/stage_id,'manifest.json',MAX_MANIFEST_BYTES))
        if manifest != stage.get('manifest'):
            raise ValueError('Journal und versiegeltes Manifest unterscheiden sich.')
        self._allowed(manifest['original_root'],manifest['root_identity'])
        return manifest, parent_id

    def prepare(self, stage_id, manifest_hash, verified_test_job_id, scope_hash):
        with self.store.lock:
            manifest, parent = self._evidence(stage_id,manifest_hash,verified_test_job_id,scope_hash)
            files = manifest['files']
            if not 1 <= len(files) <= 20 or sum(f['staged_bytes'] for f in files) > MAX_TOTAL_BYTES:
                raise ValueError('Pilotumfang überschreitet das Budget.')
            proposal = dict(id=uuid.uuid4().hex, created_at=now(),stage_id=stage_id,
                manifest_hash=manifest_hash,manifest=manifest,verified_test_job_id=verified_test_job_id,
                stage_job_id=parent,scope_hash=scope_hash,
                source_hashes={f['path']:f['original_sha256'] for f in files},
                diff=''.join(f['diff'] for f in files), approval_granted=False)
            proposal['proposal_hash'] = _sha(json.dumps(proposal,sort_keys=True,ensure_ascii=False).encode('utf-8'))
            with self.store.db() as db:
                db.execute('INSERT INTO pilot_apply_proposals VALUES(?,?)',(proposal['id'],json.dumps(proposal)))
            return proposal

    def get(self, proposal_id):
        with self.store.db() as db:
            row = db.execute('SELECT body FROM pilot_apply_proposals WHERE id=?',(proposal_id,)).fetchone()
        if not row: raise ValueError('Apply-Vorschlag nicht gefunden.')
        return json.loads(row['body'])

    def proposals(self):
        with self.store.db() as db:
            return [json.loads(r['body']) for r in db.execute('SELECT body FROM pilot_apply_proposals ORDER BY rowid DESC')]

    def transaction(self, transaction_id):
        with self.store.db() as db:
            row = db.execute('SELECT body FROM pilot_apply_transactions WHERE id=?',(transaction_id,)).fetchone()
        if not row: raise ValueError('Apply-Transaktion nicht gefunden.')
        return json.loads(row['body'])

    def transactions(self):
        with self.store.db() as db:
            return [json.loads(r['body']) for r in db.execute('SELECT body FROM pilot_apply_transactions ORDER BY rowid DESC')]

    def _save(self, tx, status=None):
        if status:
            tx.setdefault('history',[]).append(dict(status=status,time=now()))
            tx['status'] = status
        tx['updated_at'] = now()
        with self.store.db() as db:
            db.execute('UPDATE pilot_apply_transactions SET status=?,body=? WHERE id=?',
                       (tx['status'],json.dumps(tx),tx['id']))

    def _replace(self, root, path, data, expected):
        if _hash(_read(root,path)) != expected:
            raise ValueError('Datei wurde vor dem Schreiben extern geändert.')
        target = root/path
        # Existing parents only: rollback never has to remove preexisting directories.
        if not target.parent.is_dir():
            raise ValueError('Ziel-Elternverzeichnis muss bereits existieren.')
        temporary = target.with_name('.governor-'+uuid.uuid4().hex+'.tmp')
        try:
            _components(temporary)
            with temporary.open('xb') as stream:
                stream.write(data); stream.flush(); os.fsync(stream.fileno())
            if _hash(_read(root,path)) != expected:
                raise ValueError('Datei wurde unmittelbar vor Ersetzung verändert.')
            _components(target)
            os.replace(temporary,target)
            if _hash(_read(root,path)) != _sha(data):
                raise ValueError('Schreibkontrolle fehlgeschlagen.')
        finally:
            if temporary.exists(): temporary.unlink()

    def apply(self, proposal_id, expected_manifest_hash, current_scope_hash):
        with self.store.lock:
            p = self.get(proposal_id)
            if p['manifest_hash'] != expected_manifest_hash or p['scope_hash'] != current_scope_hash:
                raise ValueError('Apply-Freigabe hat veralteten Manifest- oder Quellenhash.')
            # Claim is committed before any write. SQLite serializes separate instances.
            with self.store.db() as db:
                db.execute('BEGIN IMMEDIATE')
                previous = db.execute('SELECT body FROM pilot_apply_transactions WHERE stage_id=?',(p['stage_id'],)).fetchone()
                if previous:
                    previous = json.loads(previous['body'])
                    if previous['status'] == 'completed': return previous
                    raise ValueError('Transaktion wird niemals erneut ausgeführt; explizite Wiederherstellung prüfen.')
                if db.execute("SELECT 1 FROM pilot_apply_transactions WHERE status IN ('running','interrupted','recovery_needed','rolling_back')").fetchone():
                    raise ValueError('Unabgeschlossene Apply-Transaktion benötigt explizite Wiederherstellung.')
                tx = dict(id=uuid.uuid4().hex,proposal_id=p['id'],stage_id=p['stage_id'],
                    manifest_hash=p['manifest_hash'],scope_hash=p['scope_hash'],
                    original_root=p['manifest']['original_root'],root_identity=p['manifest']['root_identity'],
                    status='running',created_at=now(),files=[],history=[dict(status='running',time=now())])
                db.execute('INSERT INTO pilot_apply_transactions VALUES(?,?,?,?)',
                           (tx['id'],tx['stage_id'],tx['status'],json.dumps(tx)))
            try:
                manifest, _ = self._evidence(p['stage_id'],p['manifest_hash'],p['verified_test_job_id'],current_scope_hash)
                root = self._allowed(manifest['original_root'],manifest['root_identity'])
                backup = self.base/tx['id']; _components(backup)
                backup.mkdir(parents=True); _components(backup)
                for item in manifest['files']:
                    if item['original_sha256'] == item['staged_sha256']: continue
                    old = _read(root,item['path'])
                    if _hash(old) != item['original_sha256']: raise ValueError('Originaldatei verändert.')
                    if not (root/item['path']).parent.is_dir(): raise ValueError('Fehlendes Zielverzeichnis.')
                    name = str(len(tx['files']))+'.original'
                    if old is not None:
                        with (backup/name).open('xb') as stream:
                            stream.write(old); stream.flush(); os.fsync(stream.fileno())
                    tx['files'].append(dict(path=item['path'],before=item['original_sha256'],
                        after=item['staged_sha256'],backup=name,intent=False,written=False))
                self._save(tx)
                self.stager.verify_source(p['stage_id'],p['manifest_hash'])
                for item in tx['files']:
                    self._allowed(tx['original_root'],tx['root_identity'])
                    data = _read(self.stager.base/p['stage_id']/'files',item['path'])
                    if _hash(data) != item['after']: raise ValueError('Staging-Datei verändert.')
                    item['intent'] = True; self._save(tx)
                    self._replace(root,item['path'],data,item['before'])
                    item['written'] = True; self._save(tx)
                self._allowed(tx['original_root'],tx['root_identity'])
                for item in manifest['files']:
                    if _hash(_read(root,item['path'])) != item['staged_sha256']:
                        raise ValueError('Quellen haben sich während Apply verändert.')
                self._save(tx,'completed')
                return tx
            except Exception as exc:
                try:
                    self._recover(tx,partial=True)
                    self._save(tx,'conflict')
                except Exception:
                    self._save(tx,'recovery_needed')
                raise ValueError('Apply fehlgeschlagen; Transaktionsjournal und Wiederherstellungsstatus prüfen.') from exc
            except BaseException:
                self._save(tx,'interrupted')
                raise

    def _recover(self, tx, partial):
        root = self._allowed(tx['original_root'],tx['root_identity'])
        restore = []
        for item in tx['files']:
            current = _hash(_read(root,item['path']))
            if partial and (not item['intent'] or current == item['before']): continue
            if current != item['after']:
                raise ValueError('Rollback blockiert: externe Änderung bleibt erhalten.')
            original = None if item['before'] is None else _read(self.base/tx['id'],item['backup'])
            if _hash(original) != item['before']: raise ValueError('Backup fehlt oder wurde verändert.')
            restore.append((item,original))
        # Validate the entire set before restoring any path.
        for item, original in reversed(restore):
            self._allowed(tx['original_root'],tx['root_identity'])
            if original is None:
                if _hash(_read(root,item['path'])) != item['after']: raise ValueError('Rollback-Konflikt.')
                (root/item['path']).unlink()
            else:
                self._replace(root,item['path'],original,item['after'])

    def rollback(self, transaction_id):
        from .change_rollback import prepare as prepare_chain_rollback, finish as finish_chain_rollback
        with self.store.lock:
            with self.store.db() as db:
                db.execute('BEGIN IMMEDIATE')
                row = db.execute('SELECT body FROM pilot_apply_transactions WHERE id=?',(transaction_id,)).fetchone()
                if not row: raise ValueError('Apply-Transaktion fehlt.')
                tx = json.loads(row['body'])
                guard=prepare_chain_rollback(db,tx)
                if tx['status'] == 'rolled_back':
                    finish_chain_rollback(db,guard,tx)
                    return tx
                if tx['status'] == 'rolling_back': raise ValueError('Rollback läuft oder wurde unterbrochen; manuelle Prüfung erforderlich.')
                partial = tx['status'] != 'completed'
                # Do not recover a live apply from another instance.
                if tx['status'] == 'running': raise ValueError('Laufende oder hart unterbrochene Transaktion manuell prüfen.')
                if db.execute("SELECT 1 FROM pilot_apply_transactions WHERE id<>? AND status IN ('running','rolling_back')",(tx['id'],)).fetchone():
                    raise ValueError('Andere Apply- oder Rollback-Transaktion läuft.')
                tx['status'] = 'rolling_back'
                tx.setdefault('history',[]).append(dict(status='rolling_back',time=now()))
                db.execute('UPDATE pilot_apply_transactions SET status=?,body=? WHERE id=?',
                           (tx['status'],json.dumps(tx),tx['id']))
            try:
                self._recover(tx,partial)
                if guard is None:
                    self._save(tx,'rolled_back')
                else:
                    terminal=copy.deepcopy(tx)
                    terminal.update(status='rolled_back',updated_at=now())
                    terminal.setdefault('history',[]).append(dict(status='rolled_back',time=now()))
                    with self.store.db() as db:
                        db.execute('BEGIN IMMEDIATE')
                        finish_chain_rollback(db,guard,terminal)
                        db.execute('UPDATE pilot_apply_transactions SET status=?,body=? WHERE id=?',
                            ('rolled_back',json.dumps(terminal),terminal['id']))
                    tx=terminal
            except BaseException:
                self._save(tx,'recovery_needed')
                raise
            return tx
