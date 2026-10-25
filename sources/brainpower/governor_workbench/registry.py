"""Durable local project catalog; never provisions or writes governed directories.

Configured IDs and original source metadata are retained. Only the complete known
five-project set receives the historical integration group. Egress requires an
explicit migration authorization and never follows from those IDs alone;
other configurations start as singles. Missing configured paths remain recorded.
New registrations require an existing directory. Membership is permanent, even
when archived. Memory provisioning remains explicitly pending in this phase.
"""
import json
import os
from pathlib import Path
import uuid

from .evidence import now


ROLES = ('parent', 'module', 'contracts', 'member')
_UNSET = object()
INITIAL_ROLES = {'aurelia': 'parent', 'radiworks': 'module',
                 'modul_templates': 'contracts', 'radi144': 'module', 'morphic_v1': 'module'}


def _id(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 64:
        raise ValueError('Projekt- und Gruppen-IDs müssen Text mit 1 bis 64 Zeichen sein.')
    return value


def _name(value):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 80:
        raise ValueError('Name muss 1 bis 80 Zeichen enthalten.')
    if any(ord(ch) < 32 for ch in value):
        raise ValueError('Name enthält Steuerzeichen.')
    return value.strip()


def _path(value, require_exists=True):
    if not isinstance(value, (str, os.PathLike)) or not str(value):
        raise ValueError('Absoluter Projektpfad fehlt.')
    path = Path(value)
    if not path.is_absolute():
        raise ValueError('Projektpfad muss absolut sein.')
    try:
        path = path.resolve(strict=require_exists)
        if require_exists and not path.is_dir():
            raise ValueError('Projektpfad muss ein vorhandener Ordner sein.')
    except (OSError, RuntimeError) as exc:
        raise ValueError('Projektpfad kann nicht aufgelöst werden.') from exc
    text = str(path)
    return text, text.casefold() if os.name == 'nt' else text


class Registry:
    def __init__(self, store, configured_projects, legacy_egress_authorized=False):
        self.store = store
        configured = list(configured_projects)
        if type(legacy_egress_authorized) is not bool:
            raise ValueError('Bestehende Modellfreigabe muss explizit boolesch sein.')
        if len(configured) > 50:
            raise ValueError('Maximal 50 registrierte Projekte.')
        ids = [p['id'] for p in configured]
        if len(set(ids)) != len(ids):
            raise ValueError('Konfigurierte Projekt-IDs sind nicht eindeutig.')
        known = set(INITIAL_ROLES).issubset(ids)
        with store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            c.execute('''CREATE TABLE IF NOT EXISTS reg_projects(
                id TEXT PRIMARY KEY, name TEXT NOT NULL, path TEXT NOT NULL,
                path_key TEXT NOT NULL UNIQUE, requirements TEXT NOT NULL,
                configured INTEGER NOT NULL CHECK(configured IN (0,1)),
                model_egress INTEGER NOT NULL CHECK(model_egress IN (0,1)),
                memory_provisioning TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0,
                source_config TEXT NOT NULL, created_at TEXT NOT NULL)''')
            c.execute('''CREATE TABLE IF NOT EXISTS reg_groups(
                id TEXT PRIMARY KEY, name TEXT NOT NULL, name_key TEXT NOT NULL UNIQUE,
                archived INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)''')
            c.execute('''CREATE TABLE IF NOT EXISTS reg_memberships(
                project_id TEXT PRIMARY KEY REFERENCES reg_projects(id),
                group_id TEXT NOT NULL REFERENCES reg_groups(id),
                role TEXT NOT NULL CHECK(role IN ('parent','module','contracts','member')),
                created_at TEXT NOT NULL)''')
            c.execute("CREATE UNIQUE INDEX IF NOT EXISTS reg_one_parent ON reg_memberships(group_id) WHERE role='parent'")
            c.execute('''CREATE TRIGGER IF NOT EXISTS reg_membership_no_update
                BEFORE UPDATE ON reg_memberships BEGIN SELECT RAISE(ABORT,'Membership is permanent'); END''')
            c.execute('''CREATE TRIGGER IF NOT EXISTS reg_membership_no_delete
                BEFORE DELETE ON reg_memberships BEGIN SELECT RAISE(ABORT,'Membership is permanent'); END''')
            c.execute('''CREATE TRIGGER IF NOT EXISTS reg_membership_valid_insert
                BEFORE INSERT ON reg_memberships WHEN
                NOT EXISTS(SELECT 1 FROM reg_projects WHERE id=NEW.project_id) OR
                NOT EXISTS(SELECT 1 FROM reg_groups WHERE id=NEW.group_id)
                BEGIN SELECT RAISE(ABORT,'Unknown membership reference'); END''')
            # A durable marker prevents a later configuration edit from reassigning
            # singles, reviving archives or silently changing historical metadata.
            migrated = c.execute("SELECT 1 FROM settings WHERE key='registry_migration_v1'").fetchone()
            if not migrated:
                if known:
                    c.execute('INSERT INTO reg_groups VALUES(?,?,?,?,?)',
                              ('aurelia-integration', 'Aurelia Integration', 'aurelia integration', 0, now()))
                for p in configured:
                    path, key = _path(p['path'], require_exists=False)
                    self._check_path(c, key)
                    c.execute('INSERT INTO reg_projects VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                              (p['id'], _name(p['name']), path, key, '', 1,
                               int(legacy_egress_authorized and known and p['id'] in INITIAL_ROLES), 'pending', 0,
                               json.dumps(p, ensure_ascii=False), now()))
                    if known and p['id'] in INITIAL_ROLES:
                        c.execute('INSERT INTO reg_memberships VALUES(?,?,?,?)',
                                  (p['id'], 'aurelia-integration', INITIAL_ROLES[p['id']], now()))
                c.execute('INSERT INTO settings VALUES(?,?)', ('registry_migration_v1', 'true'))

    @staticmethod
    def _check_path(c, key):
        candidate = Path(key)
        for row in c.execute('SELECT path_key FROM reg_projects'):
            existing = Path(row['path_key'])
            if candidate == existing or candidate in existing.parents or existing in candidate.parents:
                raise ValueError('Projektpfad überschneidet sich mit einem registrierten Projekt.')

    @staticmethod
    def _project(c, project_id):
        _id(project_id)
        row = c.execute('''SELECT p.*, m.group_id, m.role FROM reg_projects p
            LEFT JOIN reg_memberships m ON m.project_id=p.id WHERE p.id=?''', (project_id,)).fetchone()
        if row is None:
            raise ValueError('Projekt nicht gefunden.')
        result = dict(row)
        result.pop('path_key')
        result['source_config'] = json.loads(result['source_config'])
        for key in ('configured', 'model_egress', 'archived'):
            result[key] = bool(result[key])
        return result

    def register(self, name, path, model_egress=False, requirements=''):
        name = _name(name)
        path, key = _path(path)
        if type(model_egress) is not bool:
            raise ValueError('Modellfreigabe muss explizit boolesch sein.')
        if not isinstance(requirements, str) or len(requirements) > 4000:
            raise ValueError('Anforderungen müssen Text mit maximal 4000 Zeichen sein.')
        project_id = uuid.uuid4().hex
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT COUNT(*) FROM reg_projects').fetchone()[0] >= 50:
                raise ValueError('Maximal 50 registrierte Projekte einschließlich Archiv.')
            self._check_path(c, key)
            c.execute('INSERT INTO reg_projects VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                      (project_id, name, path, key, requirements, 0, int(model_egress),
                       'pending', 0, '{}', now()))
            return self._project(c, project_id)

    def create_group(self, name):
        name = _name(name)
        group_id = uuid.uuid4().hex
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT COUNT(*) FROM reg_groups').fetchone()[0] >= 50:
                raise ValueError('Maximal 50 registrierte Gruppen einschließlich Archiv.')
            if c.execute('SELECT 1 FROM reg_groups WHERE name_key=?', (name.casefold(),)).fetchone():
                raise ValueError('Gruppenname ist bereits registriert.')
            c.execute('INSERT INTO reg_groups VALUES(?,?,?,?,?)', (group_id, name, name.casefold(), 0, now()))
            return dict(id=group_id, name=name, archived=False, members=[])

    def assign(self, project_id, group_id, role='member'):
        _id(project_id)
        _id(group_id)
        if role not in ROLES:
            raise ValueError('Ungültige Gruppenrolle.')
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            p = self._project(c, project_id)
            if p['archived']:
                raise ValueError('Archivierte Projekte können nicht zugeordnet werden.')
            group = c.execute('SELECT * FROM reg_groups WHERE id=?', (group_id,)).fetchone()
            if group is None or group['archived']:
                raise ValueError('Aktive Gruppe nicht gefunden.')
            if p['group_id'] is not None:
                if p['group_id'] == group_id and p['role'] == role:
                    return p
                raise ValueError('Gruppenzugehörigkeit und Rolle sind dauerhaft unveränderlich.')
            if role == 'parent' and c.execute("SELECT 1 FROM reg_memberships WHERE group_id=? AND role='parent'", (group_id,)).fetchone():
                raise ValueError('Die Gruppe hat bereits ein Elternprojekt, gegebenenfalls archiviert.')
            c.execute('INSERT INTO reg_memberships VALUES(?,?,?,?)', (project_id, group_id, role, now()))
            return self._project(c, project_id)

    def archive(self, project_id):
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            self._project(c, project_id)
            c.execute('UPDATE reg_projects SET archived=1 WHERE id=?', (project_id,))
            return self._project(c, project_id)

    def set_project_policy(self, project_id, requirements=_UNSET, model_egress=_UNSET):
        """Persist explicit policy fields; omitted fields retain their old value."""
        _id(project_id)
        if requirements is _UNSET and model_egress is _UNSET:
            raise ValueError('Keine Richtlinienänderung angegeben.')
        if requirements is not _UNSET and (not isinstance(requirements, str) or len(requirements) > 4000):
            raise ValueError('Anforderungen müssen Text mit maximal 4000 Zeichen sein.')
        if model_egress is not _UNSET and type(model_egress) is not bool:
            raise ValueError('Modellfreigabe muss explizit boolesch sein.')
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            current = self._project(c, project_id)
            c.execute('UPDATE reg_projects SET requirements=?, model_egress=? WHERE id=?',
                      (current['requirements'] if requirements is _UNSET else requirements,
                       int(current['model_egress'] if model_egress is _UNSET else model_egress), project_id))
            return self._project(c, project_id)

    def list_projects(self, include_archived=True):
        with self.store.db() as c:
            return [self._project(c, r['id']) for r in c.execute(
                'SELECT id FROM reg_projects WHERE archived=0 OR ? ORDER BY rowid', (int(include_archived),)).fetchall()]

    def list_groups(self, include_archived=True):
        with self.store.db() as c:
            result = []
            for row in c.execute('SELECT * FROM reg_groups WHERE archived=0 OR ? ORDER BY rowid', (int(include_archived),)).fetchall():
                members = [dict(r) for r in c.execute(
                    'SELECT project_id, role FROM reg_memberships WHERE group_id=? ORDER BY project_id', (row['id'],))]
                result.append(dict(id=row['id'], name=row['name'], archived=bool(row['archived']), members=members))
            return result
