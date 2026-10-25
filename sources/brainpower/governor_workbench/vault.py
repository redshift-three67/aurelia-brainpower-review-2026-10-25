"""Explicit scoped Markdown references; vault documents never become instructions."""
import hashlib
import os
from pathlib import Path
import stat
import uuid

from .evidence import now
from .registry import _id

MAX_BYTES = 512 * 1024
MAX_SOURCES = 10
MAX_EXCERPT_BYTES = 64 * 1024


def _reparse(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400))


class Vault:
    def __init__(self, registry, data_dir, vault_root=None):
        self.registry = registry
        self.store = registry.store
        self.data_dir = Path(data_dir)
        self.root = None
        if vault_root is not None:
            raw = Path(vault_root)
            if not raw.is_absolute():
                raise ValueError('Vault-Wurzel muss ein expliziter absoluter Ordner sein.')
            try:
                if _reparse(raw) or not raw.is_dir():
                    raise ValueError('Vault-Wurzel fehlt oder ist umgeleitet.')
                self.root = raw.resolve(strict=True)
            except (OSError, RuntimeError) as exc:
                raise ValueError('Vault-Wurzel kann nicht aufgelöst werden.') from exc
        with self.store.db() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS reg_vault_sources(
                id TEXT PRIMARY KEY, kind TEXT NOT NULL, scope_key TEXT NOT NULL,
                path TEXT NOT NULL, path_key TEXT NOT NULL, name TEXT NOT NULL,
                model_egress INTEGER NOT NULL CHECK(model_egress IN (0,1)),
                created_at TEXT NOT NULL, UNIQUE(kind,scope_key,path_key))''')

    def _scope(self, c, kind, key):
        if kind not in ('project', 'group'):
            raise ValueError('Vault-Quellen benötigen einen Projekt- oder Gruppenscope.')
        _id(key)
        if kind == 'project':
            row = self.registry._project(c, key)
        else:
            row = c.execute('SELECT * FROM reg_groups WHERE id=?', (key,)).fetchone()
        if row is None or row['archived']:
            raise ValueError('Aktiver Vault-Scope nicht gefunden.')

    def _path(self, value):
        if self.root is None:
            raise ValueError('Keine explizite Vault-Wurzel konfiguriert.')
        if not isinstance(value, (str, os.PathLike)):
            raise ValueError('Vault-Quelle benötigt einen absoluten Markdown-Pfad.')
        raw = Path(value)
        if not raw.is_absolute() or raw.suffix.casefold() != '.md':
            raise ValueError('Vault-Quelle benötigt einen absoluten Markdown-Pfad.')
        try:
            if _reparse(self.root) or self.root.resolve(strict=True) != self.root:
                raise ValueError('Vault-Wurzel wurde umgeleitet.')
            # Inspect every lexical component before resolving: symlinks and
            # junctions cannot be used as aliases, even when they point inward.
            cursor = Path(raw.anchor)
            for component in raw.parts[1:]:
                if component == '..':
                    raise ValueError('Vault-Pfad darf keine übergeordneten Verzeichnisse verwenden.')
                cursor = cursor / component
                if _reparse(cursor):
                    raise ValueError('Vault-Quelle enthält eine Pfadumleitung.')
            resolved = raw.resolve(strict=True)
            if resolved == self.root or not resolved.is_relative_to(self.root) or not resolved.is_file():
                raise ValueError('Vault-Quelle liegt nicht innerhalb der konfigurierten Wurzel.')
            return resolved
        except (OSError, RuntimeError) as exc:
            raise ValueError('Vault-Quelle fehlt oder kann nicht sicher aufgelöst werden.') from exc

    def _read(self, value):
        path = self._path(value)
        with path.open('rb') as stream:
            data = stream.read(MAX_BYTES + 1)
        self._path(path)
        if len(data) > MAX_BYTES:
            raise ValueError('Vault-Quelle überschreitet 512 KiB.')
        try:
            data.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise ValueError('Vault-Quelle muss UTF-8-Text enthalten.') from exc
        return path, data

    @staticmethod
    def _mapping(row):
        return dict(id=row['id'], kind=row['kind'], key=row['scope_key'],
                    path=row['path'], name=row['name'], model_egress=bool(row['model_egress']))

    def map_source(self, kind, key, path, model_egress=False):
        if type(model_egress) is not bool:
            raise ValueError('Vault-Modellfreigabe muss explizit boolesch sein.')
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            self._scope(c, kind, key)
            resolved, _ = self._read(path)
            path_key = os.path.normcase(str(resolved))
            if c.execute('SELECT 1 FROM reg_vault_sources WHERE kind=? AND scope_key=? AND path_key=?',
                         (kind, key, path_key)).fetchone():
                raise ValueError('Diese Vault-Quelle ist dem Scope bereits zugeordnet.')
            if c.execute('SELECT COUNT(*) FROM reg_vault_sources WHERE kind=? AND scope_key=?',
                         (kind, key)).fetchone()[0] >= MAX_SOURCES:
                raise ValueError('Maximal zehn Vault-Quellen je Scope.')
            source_id = uuid.uuid4().hex
            c.execute('INSERT INTO reg_vault_sources VALUES(?,?,?,?,?,?,?,?)',
                      (source_id, kind, key, str(resolved), path_key, resolved.name, int(model_egress), now()))
            return self._mapping(c.execute('SELECT * FROM reg_vault_sources WHERE id=?', (source_id,)).fetchone())

    def list_sources(self, kind, key):
        with self.store.db() as c:
            self._scope(c, kind, key)
            return [self._mapping(row) for row in c.execute(
                'SELECT * FROM reg_vault_sources WHERE kind=? AND scope_key=? ORDER BY rowid', (kind, key))]

    def context(self, kind, key, require_egress=True):
        if type(require_egress) is not bool:
            raise ValueError('Modellkontext-Schalter muss boolesch sein.')
        with self.store.db() as c:
            self._scope(c, kind, key)
            if self.root is None:
                raise ValueError('Keine explizite Vault-Wurzel konfiguriert.')
            rows = c.execute('SELECT * FROM reg_vault_sources WHERE kind=? AND scope_key=? ORDER BY rowid LIMIT ?',
                             (kind, key, MAX_SOURCES + 1)).fetchall()
            if len(rows) > MAX_SOURCES:
                raise ValueError('Maximal zehn Vault-Quellen je Scope.')
            if require_egress and any(not row['model_egress'] for row in rows):
                raise ValueError('Modellversand ist nicht für alle zugeordneten Vault-Quellen freigegeben.')
            sources = []
            remaining = MAX_EXCERPT_BYTES
            for index, row in enumerate(rows):
                path, data = self._read(row['path'])
                allowance = remaining // (len(rows) - index)
                excerpt = data[:allowance].decode('utf-8', errors='ignore')
                used = len(excerpt.encode('utf-8'))
                remaining -= used
                sources.append(dict(id=row['id'], name=row['name'], path=str(path),
                                    sha256=hashlib.sha256(data).hexdigest(), content=excerpt,
                                    truncated=used < len(data), original_bytes=len(data), excerpt_bytes=used,
                                    authority='reference_data_only'))
            return dict(kind=kind, key=key, sources=sources,
                        truncated=any(s['truncated'] for s in sources),
                        total_excerpt_bytes=MAX_EXCERPT_BYTES - remaining)
