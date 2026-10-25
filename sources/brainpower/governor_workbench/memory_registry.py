"""Explicit, non-overwriting strategy-memory provisioning for registry projects.

Existing documents are selected and hashed, never rewritten. New templates are
incomplete planning records, not approvals. Checks reject path redirection but do
not claim an OS sandbox against concurrent hostile filesystem replacement.
"""
import fnmatch
import hashlib
import os
from pathlib import Path
import stat

from .evidence import now
from .registry import _id

MAX_BYTES = 512 * 1024
MAX_ENTRIES = 1000


def _redirected(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400))


def _check_root(root):
    if _redirected(root) or not root.is_dir():
        raise ValueError('Projektpfad fehlt oder ist umgeleitet.')
    try:
        canonical = root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError('Projektpfad kann nicht sicher aufgelöst werden.') from exc
    if os.path.normcase(str(canonical)) != os.path.normcase(str(root)):
        raise ValueError('Registrierter Projektpfad hat sich geändert.')


def _check_memory_path(root, folder, target=None):
    _check_root(root)
    if folder.parent != root or _redirected(folder):
        raise ValueError('Gedächtnisordner ist umgeleitet.')
    if folder.exists() and not folder.is_dir():
        raise ValueError('Gedächtnispfad ist kein Ordner.')
    if target is not None and (target.parent != folder or _redirected(target)):
        raise ValueError('Gedächtnisdatei liegt außerhalb des erlaubten Ordners oder ist umgeleitet.')


def _read(root, folder, target):
    _check_memory_path(root, folder, target)
    if not target.is_file():
        raise ValueError('Gedächtnisdatei ist keine reguläre Datei.')
    with target.open('rb') as stream:
        content = stream.read(MAX_BYTES + 1)
    _check_memory_path(root, folder, target)
    if len(content) > MAX_BYTES:
        raise ValueError('Gedächtnisdatei überschreitet 512 KiB.')
    return content


class RegistryMemory:
    def __init__(self, registry, data_dir):
        self.registry = registry
        self.store = registry.store
        self.data_dir = Path(data_dir)  # Reserved for later vault support; no directory is created.
        with self.store.db() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS reg_memory(
                project_id TEXT PRIMARY KEY, name TEXT NOT NULL, path TEXT NOT NULL,
                sha256 TEXT NOT NULL, created INTEGER NOT NULL, complete INTEGER NOT NULL DEFAULT 0,
                provisioned_at TEXT NOT NULL)''')

    def provision(self, project_id):
        _id(project_id)
        created = False
        made_folder = False
        root = folder = target = None
        expected_hash = None
        try:
            with self.store.db() as c:
                c.execute('BEGIN IMMEDIATE')
                project = self.registry._project(c, project_id)
                if project['archived'] or not project['group_id']:
                    raise ValueError('Nur aktive, einer Gruppe zugeordnete Projekte können Gedächtnisse erhalten.')
                group = c.execute('SELECT archived FROM reg_groups WHERE id=?', (project['group_id'],)).fetchone()
                if group is None or group['archived']:
                    raise ValueError('Projektgruppe ist nicht aktiv.')
                ids = [r['id'] for r in c.execute('SELECT id FROM reg_projects ORDER BY rowid')]
                index = ids.index(project_id) + 1
                root = Path(project['path'])
                folder = root / 'project_memories'
                _check_memory_path(root, folder)
                candidates = []
                if folder.exists():
                    with os.scandir(folder) as entries:
                        for count, entry in enumerate(entries, 1):
                            if count > MAX_ENTRIES:
                                raise ValueError('Gedächtnisordner überschreitet die Prüfgrenze von 1000 Einträgen.')
                            if fnmatch.fnmatchcase(entry.name.casefold(), 'strategy_project*.md'):
                                candidates.append(folder / entry.name)
                                if len(candidates) > 1:
                                    raise ValueError('Mehrere Strategiegedächtnisse vorhanden; Auswahl ist mehrdeutig.')
                record = c.execute('SELECT name FROM reg_memory WHERE project_id=?', (project_id,)).fetchone()
                if record and (not candidates or candidates[0].name != record['name']):
                    raise ValueError('Zugeordnetes Strategiegedächtnis fehlt oder wurde ausgetauscht.')
                if candidates:
                    target = candidates[0]
                    content = _read(root, folder, target)
                else:
                    target = folder / f'strategy_project_{index}.md'
                    content = (f'# Strategy memory — {project["name"]}\n\n'
                               'Status: incomplete. This initial template is not an implementation approval.\n\n'
                               f'Project ID: {project_id}\nGroup ID: {project["group_id"]}\n'
                               f'Role: {project["role"]}\n\n## Requirements\n\n'
                               f'{project["requirements"] or "Not yet specified."}\n\n'
                               '## Evidence and next steps\n\nNot yet assessed.\n').encode('utf-8')
                    expected_hash = hashlib.sha256(content).hexdigest()
                    if not folder.exists():
                        folder.mkdir()
                        made_folder = True
                    _check_memory_path(root, folder, target)
                    try:
                        with open(target, 'xb') as stream:
                            created = True
                            stream.write(content)
                            stream.flush()
                            os.fsync(stream.fileno())
                    except FileExistsError as exc:
                        raise ValueError('Gedächtnisdatei wurde zwischenzeitlich erstellt; nichts überschrieben.') from exc
                    observed = _read(root, folder, target)
                    if observed != content:
                        raise ValueError('Gedächtnisdatei hat sich während der Erstellung geändert.')
                digest = hashlib.sha256(content).hexdigest()
                c.execute('''INSERT INTO reg_memory VALUES(?,?,?,?,?,?,?)
                    ON CONFLICT(project_id) DO UPDATE SET sha256=excluded.sha256''',
                          (project_id, target.name, str(target), digest, int(created), 0, now()))
                c.execute("UPDATE reg_projects SET memory_provisioning='provisioned_incomplete' WHERE id=?", (project_id,))
                result = dict(name=target.name, path=str(target), sha256=digest, created=created, complete=False)
            return result
        except BaseException:
            if created and target is not None:
                try:
                    current = _read(root, folder, target)
                    if hashlib.sha256(current).hexdigest() == expected_hash:
                        target.unlink()
                except (OSError, ValueError):
                    pass  # Never remove an unverified or concurrently changed file.
            if made_folder and folder is not None:
                try:
                    _check_memory_path(root, folder)
                    folder.rmdir()  # Only succeeds when the newly created directory is still empty.
                except (OSError, ValueError):
                    pass
            raise
