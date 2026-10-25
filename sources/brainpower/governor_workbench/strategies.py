"""Immutable operator-adopted strategies, separate from step and product approval.

Only local journal records are written. Adoption never enables execution, changes
plan selections, or modifies product gates. Callers provide a freshly scanned
ScopeService context; persisted history is evidence of adoption at that time.
"""
import copy
import json
import uuid

from .evidence import fingerprint, now
from .plans import PlanBook, _context, _hash, _id, _scope, _text


class StrategyBook:
    def __init__(self, store):
        self.store = store
        self.plans = PlanBook(store)
        with store.db() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS strategy_revisions(
                id TEXT PRIMARY KEY, scope_kind TEXT NOT NULL, scope_id TEXT NOT NULL,
                version INTEGER NOT NULL, candidate_id TEXT NOT NULL UNIQUE, body TEXT NOT NULL,
                UNIQUE(scope_kind,scope_id,version))''')
            for operation in ('UPDATE', 'DELETE'):
                c.execute(f"CREATE TRIGGER IF NOT EXISTS strategy_revisions_no_{operation.lower()} "
                          f"BEFORE {operation} ON strategy_revisions "
                          "BEGIN SELECT RAISE(ABORT,'Strategy history is immutable'); END")

    def list(self, kind, key, limit=100):
        _scope(kind, key)
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError('Maximal 100 Strategierevisionen pro Abruf.')
        with self.store.db() as c:
            return [json.loads(row['body']) for row in c.execute(
                'SELECT body FROM strategy_revisions WHERE scope_kind=? AND scope_id=? '
                'ORDER BY version DESC LIMIT ?', (kind, key, limit))]

    @staticmethod
    def _completed_plan(c, candidate):
        row = c.execute('SELECT * FROM jobs WHERE id=?', (candidate['job_id'],)).fetchone()
        if row is None or row['status'] != 'completed' or row['action'] not in ('scope_plan','scope_route_b_plan'):
            raise ValueError('Abgeschlossener ursprünglicher Planauftrag erforderlich.')
        try:
            result = json.loads(row['result']) if row['result'] else None
        except (TypeError, ValueError):
            result = None
        if (not isinstance(result, dict) or result.get('stale') is not False
                or result.get('plan_ready') is not True
                or result.get('candidate') != candidate
                or result.get('proposal') != candidate['proposal']
                or result.get('review') != candidate['review']
                or result.get('scope_hash') != candidate['scope_hash']
                or result.get('review_scope') != dict(kind=candidate['scope_kind'], id=candidate['scope_id'])):
            raise ValueError('Planauftrag und gespeicherter Kandidat sind nicht vollständig konsistent.')
        from .model_memory import VERSION, stage_coverage_complete
        coverage = result.get('memory_coverage')
        if (not isinstance(coverage, dict) or coverage.get('version') != VERSION
                or not isinstance(coverage.get('files'), list)
                or not (coverage.get('status') == 'full' or stage_coverage_complete(coverage))):
            raise ValueError('Planauftrag ohne belegte vollständige Projektgedächtnisse; neuer Plan erforderlich.')
        _hash(result.get('model_context_hash'))
        if row['action'] == 'scope_route_b_plan':
            independent = result.get('critical_report')
            if (result.get('route_variant') != 'b_plus_v1'
                    or result.get('critical_reviewer') != 'gpt-6-astra'
                    or result.get('critical_review_reason') != 'mandatory_plan'
                    or result.get('critical_review_required') is not True
                    or not isinstance(independent, dict)
                    or independent.get('decision') != 'REVIEW_ONLY'
                    or independent.get('findings') != []
                    or independent.get('required_evidence') != []):
                raise ValueError('Route-B-Plan ohne unabhängige Astra-Pflichtprüfung; neuer Plan erforderlich.')
        review = candidate['review']
        if (not isinstance(review, dict)
                or set(review) != {'summary', 'decision', 'findings', 'required_evidence'}
                or review['decision'] != 'REVIEW_ONLY'
                or review['findings'] != [] or review['required_evidence'] != []):
            raise ValueError('Unabhängiger Review enthält offene Befunde oder fehlende Nachweise.')
        _text(review['summary'])
        if candidate['proposal_hash'] != fingerprint(candidate['proposal']):
            raise ValueError('Gespeicherter Vorschlag stimmt nicht mit seinem Hash überein.')

    @staticmethod
    def _provenance(c, context):
        _, _, _, ids = _context(context)
        projects = context.get('projects')
        records = context.get('intake_records')
        if (not isinstance(projects, list) or len(projects) != len(ids)
                or not isinstance(records, list) or len(records) != len(ids)):
            raise ValueError('Vollständige Projekt- und Aufnahmeherkunft erforderlich.')
        hashes = {}
        for project in projects:
            if not isinstance(project, dict):
                raise ValueError('Ungültige Projektherkunft.')
            key = _id(project.get('id'))
            if key not in ids or key in hashes:
                raise ValueError('Projektherkunft passt nicht zum Geltungsbereich.')
            hashes[key] = _hash(project.get('evidence_hash'))
        seen = set()
        if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='reg_intake'").fetchone():
            raise ValueError('Gespeicherte Aufnahmeherkunft fehlt.')
        for record in records:
            if not isinstance(record, dict):
                raise ValueError('Ungültige Aufnahmeherkunft.')
            key = _id(record.get('project_id'))
            if key not in hashes or key in seen or record.get('source_hash') != hashes[key]:
                raise ValueError('Aufnahmeherkunft ist veraltet oder außerhalb des Geltungsbereichs.')
            # The context scan precedes this transaction. A confirmation can
            # change the planning hash without changing any project bytes.
            latest = c.execute('SELECT * FROM reg_intake WHERE project_id=? ORDER BY rowid DESC LIMIT 1',
                               (key,)).fetchone()
            try:
                persisted = {**dict(latest), 'body': json.loads(latest['body'])} if latest else None
            except (TypeError, ValueError):
                persisted = None
            if persisted != record:
                raise ValueError('Aufnahmebestätigung inzwischen geändert; Kontext erneut prüfen.')
            seen.add(key)
        if len(json.dumps(records, ensure_ascii=False)) > 1000000:
            raise ValueError('Aufnahmeherkunft überschreitet das Größenlimit.')
        return hashes, copy.deepcopy(records)

    def adopt(self, candidate_id, expected_scope_hash, expected_previous_id, current_context):
        _id(candidate_id)
        _hash(expected_scope_hash)
        if expected_previous_id is not None:
            _id(expected_previous_id)
        current_context = copy.deepcopy(current_context)
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            candidate = self.plans._candidate(c, candidate_id)
            self.plans._fresh(c, candidate, current_context)
            if candidate['scope_hash'] != expected_scope_hash:
                raise ValueError('Angezeigter Quellenstand ist veraltet.')
            self._completed_plan(c, candidate)
            project_hashes, intake_records = self._provenance(c, current_context)
            kind, key = candidate['scope_kind'], candidate['scope_id']
            previous = c.execute('SELECT id,version FROM strategy_revisions '
                'WHERE scope_kind=? AND scope_id=? ORDER BY version DESC LIMIT 1', (kind, key)).fetchone()
            if expected_previous_id != (previous['id'] if previous else None):
                raise ValueError('Strategiestand inzwischen geändert; erneut prüfen.')
            if c.execute('SELECT 1 FROM strategy_revisions WHERE candidate_id=?', (candidate_id,)).fetchone():
                raise ValueError('Plankandidat wurde bereits als Strategie übernommen.')
            timestamp = now()
            record = dict(id=uuid.uuid4().hex, status='adopted', scope_kind=kind, scope_id=key,
                version=previous['version'] + 1 if previous else 1,
                previous_revision_id=previous['id'] if previous else None,
                candidate_id=candidate_id, candidate_hash=fingerprint(candidate),
                scope_hash=expected_scope_hash, proposal_hash=candidate['proposal_hash'],
                proposal=candidate['proposal'], review=candidate['review'], job_id=candidate['job_id'],
                actor='operator', execution_enabled=False, created_at=timestamp, adopted_at=timestamp,
                candidate_created_at=candidate['created_at'],
                project_hashes=project_hashes, intake_records=intake_records)
            c.execute('INSERT INTO strategy_revisions VALUES(?,?,?,?,?,?)',
                (record['id'], kind, key, record['version'], candidate_id, json.dumps(record, ensure_ascii=False)))
            return record
