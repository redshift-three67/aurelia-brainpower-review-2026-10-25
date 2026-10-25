"""Append-only, source-bound plan proposals and operator selections.

Selection approval is not product-gate approval. Technical test recognition
delegates bounded file checks to its adapter; no product writes or automatic execution.
"""
import copy
import json
from pathlib import PurePosixPath
import re
import uuid

from .evidence import fingerprint, now


def _text(value, maximum=4000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError('Plantext fehlt oder überschreitet die Größenbegrenzung.')
    if any(ord(ch) < 32 and ch not in '\n\r\t' for ch in value):
        raise ValueError('Plantext enthält Steuerzeichen.')
    return value


def _id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', value):
        raise ValueError('Ungültige Plan-, Projekt- oder Schritt-ID.')
    return value


def _hash(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-f0-9]{64}', value):
        raise ValueError('Gültiger Quellenhash erforderlich.')
    return value


def _scope(kind, key):
    if kind not in ('project', 'group'):
        raise ValueError('Ungültiger Plangeltungsbereich.')
    return kind, _id(key)


def _context(context):
    if not isinstance(context, dict) or context.get('plan_ready') is not True:
        raise ValueError('Projektaufnahme ist nicht vollständig.')
    scope = context.get('review_scope')
    if not isinstance(scope, dict):
        raise ValueError('Plangeltungsbereich fehlt.')
    kind, key = _scope(scope.get('kind'), scope.get('id'))
    source_hash = _hash(context.get('scope_hash'))
    projects = context.get('registry_projects')
    if not isinstance(projects, list) or not 1 <= len(projects) <= 50:
        raise ValueError('Begrenzte Projektliste erforderlich.')
    ids = [_id(p.get('id')) if isinstance(p, dict) else _id(None) for p in projects]
    if len(set(ids)) != len(ids) or (kind == 'project' and ids != [key]):
        raise ValueError('Projektliste passt nicht zum Geltungsbereich.')
    return kind, key, source_hash, set(ids)


def _path(value):
    _text(value, 240)
    if any(ch in value for ch in '\\:*?<>|\r\n\t'):
        raise ValueError('Nur konkrete relative Dateipfade sind zulässig.')
    parts = value.split('/')
    if PurePosixPath(value).is_absolute() or any(p in ('', '.', '..') or p.endswith((' ', '.')) for p in parts):
        raise ValueError('Pfad verlässt den begrenzten Planumfang.')
    forbidden = {'.git', '.ssh', '.aws', '.azure', '.codex', 'credentials', 'credentials.json',
                 'auth.json', 'tokens.json', 'token.json', 'secrets', 'secrets.json', 'id_rsa', 'id_ed25519'}
    if any(p.casefold() in forbidden or p.casefold().startswith('.env')
           or re.search(r'(^|[._-])(credentials?|secrets?|tokens?)([._-]|$)', p.casefold())
           or p.casefold().endswith(('.pem', '.key', '.p12', '.pfx')) for p in parts):
        raise ValueError('Git-Metadaten und Zugangsdaten sind kein zulässiger Planumfang.')
    return value


def _proposal(proposal, project_ids):
    if not isinstance(proposal, dict) or set(proposal) != {'summary', 'steps'}:
        raise ValueError('Plan benötigt ausschließlich summary und steps.')
    _text(proposal['summary'])
    steps = proposal['steps']
    if not isinstance(steps, list) or not 1 <= len(steps) <= 50:
        raise ValueError('Ein Plan benötigt 1 bis 50 Schritte.')
    graph = {}
    fields = {'id', 'title', 'project_id', 'priority', 'depends_on', 'rationale', 'scope', 'tests', 'action'}
    for step in steps:
        if not isinstance(step, dict) or set(step) != fields:
            raise ValueError('Ungültige Schrittstruktur; keine zusätzlichen Befehlsfelder erlaubt.')
        key = _id(step['id'])
        if key in graph or _id(step['project_id']) not in project_ids:
            raise ValueError('Doppelte Schritt-ID oder Projekt außerhalb des Geltungsbereichs.')
        _text(step['title'], 160)
        _text(step['rationale'])
        if type(step['priority']) is not int or not 0 <= step['priority'] <= 100:
            raise ValueError('Schrittpriorität muss eine ganze Zahl zwischen 0 und 100 sein.')
        if step['action'] not in ('clarify', 'review', 'test', 'change'):
            raise ValueError('Nicht unterstützte Planaktion.')
        dependencies = step['depends_on']
        if not isinstance(dependencies, list) or len(dependencies) > 50:
            raise ValueError('Ungültige Abhängigkeiten.')
        dependencies = [_id(dep) for dep in dependencies]
        if len(set(dependencies)) != len(dependencies):
            raise ValueError('Doppelte Abhängigkeit.')
        graph[key] = dependencies
        for field in ('scope', 'tests'):
            values = step[field]
            if not isinstance(values, list) or not 1 <= len(values) <= 50:
                raise ValueError('Begrenzter Dateiumfang und Prüfauftrag sind erforderlich.')
            for value in values:
                _path(value) if field == 'scope' else _text(value, 1000)
    visited = set()
    def visit(key, chain):
        if key not in graph or key in chain:
            raise ValueError('Unbekannte oder zyklische Schrittvoraussetzung.')
        if key in visited:
            return
        for dep in graph[key]:
            visit(dep, chain | {key})
        visited.add(key)
    for key in graph:
        visit(key, set())
    if len(json.dumps(proposal, ensure_ascii=False)) > 95000:
        raise ValueError('Plan überschreitet das Kontextbudget.')
    return copy.deepcopy(proposal)


class PlanBook:
    def __init__(self, store, config=None):
        self.store = store
        self.config = config
        with store.db() as c:
            c.execute('CREATE TABLE IF NOT EXISTS plan_candidates(id TEXT PRIMARY KEY, scope_kind TEXT NOT NULL, scope_id TEXT NOT NULL, version INTEGER NOT NULL, body TEXT NOT NULL, UNIQUE(scope_kind,scope_id,version))')
            c.execute('CREATE TABLE IF NOT EXISTS plan_approvals(id TEXT PRIMARY KEY, candidate_id TEXT NOT NULL, body TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS step_completions(id TEXT PRIMARY KEY, candidate_id TEXT NOT NULL, step_id TEXT NOT NULL, body TEXT NOT NULL)')
            for table in ('plan_candidates', 'plan_approvals', 'step_completions'):
                for operation in ('UPDATE', 'DELETE'):
                    c.execute(f"CREATE TRIGGER IF NOT EXISTS {table}_no_{operation.lower()} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT,'Plan history is immutable'); END")

    @staticmethod
    def _candidate(c, candidate_id):
        _id(candidate_id)
        row = c.execute('SELECT body FROM plan_candidates WHERE id=?', (candidate_id,)).fetchone()
        if row is None:
            raise ValueError('Plankandidat nicht gefunden.')
        return json.loads(row['body'])

    @staticmethod
    def _latest(c, kind, key):
        row = c.execute('SELECT id,version FROM plan_candidates WHERE scope_kind=? AND scope_id=? ORDER BY version DESC LIMIT 1', (kind, key)).fetchone()
        return dict(row) if row else None

    def save_candidate(self, context, proposal, review, job_id):
        kind, key, source_hash, projects = _context(context)
        proposal = _proposal(proposal, projects)
        _text(job_id, 64)
        if (not isinstance(review, dict) or set(review) != {'summary', 'decision', 'findings', 'required_evidence'}
                or review['decision'] != 'REVIEW_ONLY' or review['findings'] != [] or review['required_evidence'] != []):
            raise ValueError('Unabhängiger Review muss ohne offene Befunde oder Nachweise vorliegen.')
        _text(review['summary'])
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            previous = self._latest(c, kind, key)
            record = dict(id=uuid.uuid4().hex, status='candidate', scope_kind=kind, scope_id=key,
                          version=previous['version'] + 1 if previous else 1,
                          previous_candidate_id=previous['id'] if previous else None,
                          scope_hash=source_hash, proposal_hash=fingerprint(proposal), proposal=proposal,
                          review=copy.deepcopy(review), job_id=job_id, created_at=now(), execution_enabled=False)
            c.execute('INSERT INTO plan_candidates VALUES(?,?,?,?,?)',
                      (record['id'], kind, key, record['version'], json.dumps(record, ensure_ascii=False)))
            return record

    def list(self, kind, key, limit=100):
        _scope(kind, key)
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError('Maximal 100 Planrevisionen pro Abruf.')
        with self.store.db() as c:
            return [json.loads(row['body']) for row in c.execute(
                'SELECT body FROM plan_candidates WHERE scope_kind=? AND scope_id=? ORDER BY version DESC LIMIT ?', (kind, key, limit))]

    def get(self,candidate_id):
        with self.store.db() as c: return self._candidate(c,candidate_id)

    def _fresh(self, c, candidate, current_context):
        kind, key, source_hash, projects = _context(current_context)
        from .change_chain import latest, valid
        transition=latest(c,candidate['id'])
        expected_scope=candidate['scope_hash']
        if transition:
            if not valid(self.store,self.config,current_context,transition):
                raise ValueError('Bestätigter Quellenübergang ist nicht mehr aktuell.')
            expected_scope=transition['to_scope_hash']
        if ((kind, key, source_hash) != (candidate['scope_kind'], candidate['scope_id'], expected_scope)
                or self._latest(c, kind, key)['id'] != candidate['id']):
            raise ValueError('Planrevision oder Quellenstand ist nicht mehr aktuell.')
        _proposal(candidate['proposal'], projects)

    def approve(self, candidate_id, expected_scope_hash, current_context, selected_step_ids, mode='single'):
        _hash(expected_scope_hash)
        if mode not in ('single', 'sequence') or not isinstance(selected_step_ids, list) or not 1 <= len(selected_step_ids) <= 50:
            raise ValueError('Explizite begrenzte Schrittauswahl erforderlich.')
        selection = [_id(key) for key in selected_step_ids]
        if len(set(selection)) != len(selection) or (mode == 'single' and len(selection) != 1):
            raise ValueError('Ungültige Einzelschritt- oder Sequenzauswahl.')
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            candidate = self._candidate(c, candidate_id)
            self._fresh(c, candidate, current_context)
            from .change_chain import latest
            if latest(c, candidate_id):
                raise ValueError('Nach bestätigtem Quellenübergang erfordert eine neue Auswahl einen neuen Plan.')
            if expected_scope_hash != candidate['scope_hash']:
                raise ValueError('Angezeigter Quellenstand ist veraltet.')
            steps = {step['id']: step for step in candidate['proposal']['steps']}
            seen = set()
            for key in selection:
                if key not in steps or not set(steps[key]['depends_on']) <= seen:
                    raise ValueError('Auswahl enthält unbekannte Schritte oder unerfüllte/vorgezogene Voraussetzungen.')
                seen.add(key)
            record = dict(id=uuid.uuid4().hex, candidate_id=candidate_id, proposal_hash=candidate['proposal_hash'],
                          scope_hash=expected_scope_hash, selected_step_ids=selection, mode=mode,
                          actor='operator', approval_kind='plan_selection_only', created_at=now(), execution_enabled=False)
            c.execute('INSERT INTO plan_approvals VALUES(?,?,?)', (record['id'], candidate_id, json.dumps(record, ensure_ascii=False)))
            return record

    def execution_permission(self, candidate_id, step_id, current_context):
        _id(step_id)
        result = dict(plan_selection_approved=False, execution_enabled=False,
                      reason='Planauswahl ersetzt keine Produktgates; Ausführung ist nicht implementiert.')
        with self.store.db() as c:
            candidate = self._candidate(c, candidate_id)
            from .change_chain import latest
            if latest(c,candidate_id): return result
            try:
                self._fresh(c, candidate, current_context)
            except ValueError:
                return result
            row = c.execute('SELECT body FROM plan_approvals WHERE candidate_id=? ORDER BY rowid DESC LIMIT 1', (candidate_id,)).fetchone()
            if row:
                approval = json.loads(row['body'])
                result['plan_selection_approved'] = (approval['proposal_hash'] == candidate['proposal_hash']
                  and approval['scope_hash'] == candidate['scope_hash'] and step_id in approval['selected_step_ids'])
                if result['plan_selection_approved']:
                    result['plan_selection_id'] = approval['id']
        return result

    def dependency_report(self, candidate_id, current_context):
        """General DAG diagnostics; test jobs are not semantic completion receipts."""
        with self.store.db() as c:
            c.execute('BEGIN')
            candidate=self._candidate(c,candidate_id)
            proposal=_proposal(candidate['proposal'],{s['project_id'] for s in candidate['proposal']['steps']})
            current=True; reason=''
            try: self._fresh(c,candidate,current_context)
            except ValueError as error: current=False; reason=str(error)
            from .change_chain import latest
            transition=latest(c,candidate_id)
            effective_scope=transition['to_scope_hash'] if transition else candidate['scope_hash']
            effective_candidate=dict(candidate,scope_hash=effective_scope)
            row=c.execute('SELECT body FROM plan_approvals WHERE candidate_id=? ORDER BY rowid DESC LIMIT 1',(candidate_id,)).fetchone()
            approval=json.loads(row['body']) if row else None
            selected=set(approval['selected_step_ids']) if current and approval and approval['scope_hash']==candidate['scope_hash'] and approval['proposal_hash']==candidate['proposal_hash'] else set()
            steps={s['id']:s for s in proposal['steps']}; order=[]; ancestors={}
            def visit(key):
                if key in ancestors: return
                all_ids=set()
                for dep in steps[key]['depends_on']:
                    visit(dep); all_ids.add(dep); all_ids.update(ancestors[dep])
                ancestors[key]=all_ids; order.append(key)
            for key in steps: visit(key)
            rows=[]; accepted={}
            for key in order:
                step=steps[key]
                source=c.execute("SELECT id,status FROM jobs WHERE action='scope_patch' AND json_extract(request,'$.candidate_id')=? AND json_extract(request,'$.step_id')=? ORDER BY rowid DESC LIMIT 1",(candidate_id,key)).fetchone()
                test=c.execute("SELECT id,status FROM jobs WHERE action='stage_test' AND json_extract(request,'$.stage_job_id')=? ORDER BY rowid DESC LIMIT 1",(source['id'],)).fetchone() if source else None
                if step['action']=='test':
                    test=c.execute("SELECT id,status FROM jobs WHERE action='plan_test' AND json_extract(request,'$.candidate_id')=? AND json_extract(request,'$.step_id')=? ORDER BY rowid DESC LIMIT 1",(candidate_id,key)).fetchone()
                predecessors=[dep for dep in order if dep in ancestors[key]]
                record=c.execute('SELECT body FROM step_completions WHERE candidate_id=? AND step_id=? ORDER BY rowid DESC LIMIT 1',(candidate_id,key)).fetchone()
                receipt=json.loads(record['body']) if record else None
                status='not_proven'
                if receipt:
                    status='withdrawn' if receipt['status']=='withdrawn' else 'stale'
                    supported=step['action'] in ('clarify','review')
                    if step['action']=='test' and receipt.get('kind')=='plan_test':
                        from .plan_tests import valid_receipt
                        supported=current and valid_receipt(c,receipt,self.config,current_context,effective_candidate,step)
                    if step['action']=='change' and receipt.get('kind')=='change_transition':
                        supported=bool(transition and receipt.get('transition_id')==transition['id']
                                       and key==transition['step_id'] and not step['depends_on'])
                    if (receipt['status']=='accepted' and current and key in selected
                            and supported
                            and receipt['scope_hash']==effective_scope
                            and receipt['selection_id']==approval['id']
                            and receipt['step_hash']==fingerprint(step)
                            and all(dep in accepted for dep in step['depends_on'])
                            and receipt['predecessor_receipts']=={dep:accepted[dep] for dep in step['depends_on']}):
                        status='accepted'; accepted[key]=receipt['id']
                test_available=False; attempts=None
                if step['action']=='test':
                    from .plan_tests import attempt_policy
                    attempts=attempt_policy(c,candidate_id,key)
                if step['action']=='test' and current and key in selected and all(dep in accepted for dep in step['depends_on']):
                    from .plan_tests import eligibility
                    try:
                        eligibility(self.config,current_context,effective_candidate,key); test_available=attempts['allowed']
                    except (ValueError,OSError,KeyError,TypeError): pass
                rows.append(dict(id=key,title=step['title'],project_id=step['project_id'],test_run_available=test_available,test_attempts=attempts,
                    direct_predecessors=step['depends_on'],all_predecessors=predecessors,
                    missing_completion_ids=[dep for dep in predecessors if dep not in accepted],selected=key in selected,
                    latest_patch=dict(source) if source else None,latest_test=dict(test) if test else None,
                    completion_status=status,completion_receipt=receipt,action=step['action'],execution_enabled=False))
            return dict(candidate_id=candidate_id,scope_hash=effective_scope,original_scope_hash=candidate['scope_hash'],source_transition=transition,checked_at=now(),
                        current=current,reason=reason,steps=rows,selection_id=approval['id'] if selected else None,execution_enabled=False,
                        limitation='Klärung/Review: Betreiberabnahme. Test: gebundener Pilot-Test. Isolierte Änderung: ausdrücklich bestätigter Quellenübergang. Weitere Änderungsausführung und automatische Folgen bleiben gesperrt.')

    def complete_step(self,candidate_id,step_id,context,scope_hash,selection_id,note):
        _id(step_id); _hash(scope_hash); _id(selection_id); _text(note,2000)
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            report=self.dependency_report(candidate_id,context)
            row=next((r for r in report['steps'] if r['id']==step_id),None)
            if (not report['current'] or report['scope_hash']!=scope_hash or report['selection_id']!=selection_id
                    or row is None or not row['selected'] or row['missing_completion_ids']
                    or row['action'] not in ('clarify','review') or row['completion_status']=='accepted'):
                raise ValueError('Fachliche Abnahme benötigt aktuelle Auswahl, unterstützte Schrittart und vollständig abgenommene Vorgänger.')
            candidate=self._candidate(c,candidate_id)
            step=next(s for s in candidate['proposal']['steps'] if s['id']==step_id)
            by_id={r['id']:r for r in report['steps']}
            receipt=dict(id=uuid.uuid4().hex,candidate_id=candidate_id,step_id=step_id,status='accepted',
                scope_hash=scope_hash,selection_id=selection_id,step_hash=fingerprint(step),
                predecessor_receipts={dep:by_id[dep]['completion_receipt']['id'] for dep in step['depends_on']},
                actor='operator',note=note,created_at=now(),execution_enabled=False,product_gate_approved=False)
            c.execute('INSERT INTO step_completions VALUES(?,?,?,?)',(receipt['id'],candidate_id,step_id,json.dumps(receipt,ensure_ascii=False)))
            return receipt

    def withdraw_completion(self,candidate_id,step_id,expected_receipt_id,note):
        _id(candidate_id); _id(step_id); _id(expected_receipt_id); _text(note,2000)
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT body FROM step_completions WHERE candidate_id=? AND step_id=? ORDER BY rowid DESC LIMIT 1',(candidate_id,step_id)).fetchone()
            receipt=json.loads(row['body']) if row else None
            if not receipt or receipt['id']!=expected_receipt_id or receipt['status']!='accepted':
                raise ValueError('Abnahme wurde inzwischen geändert oder zurückgenommen.')
            updated=dict(receipt,id=uuid.uuid4().hex,status='withdrawn',previous_receipt_id=receipt['id'],note=note,created_at=now())
            c.execute('INSERT INTO step_completions VALUES(?,?,?,?)',(updated['id'],candidate_id,step_id,json.dumps(updated,ensure_ascii=False)))
            return updated
