"""Explicit source transition for one completed isolated change; no execution grant."""
import copy
import hashlib
import json
import uuid
from pathlib import Path
from types import SimpleNamespace

from .evidence import fingerprint, now
from .plans import _context, _id, _hash, _text


def identity():
    return fingerprint({n:hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
                        for n in ('change_chain.py','plans.py','plan_tests.py')})


def latest(db,candidate_id):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='plan_scope_transitions'").fetchone(): return None
    row=db.execute('SELECT body FROM plan_scope_transitions WHERE candidate_id=? ORDER BY rowid DESC LIMIT 1',(candidate_id,)).fetchone()
    return json.loads(row['body']) if row else None


def valid(store,config,context,transition):
    if not config or transition.get('adapter_hash')!=identity(): return False
    try:
        _context(context)
        if context['scope_hash']!=transition['to_scope_hash']: return False
        from .pilot_verification import verify
        from .registry import Registry
        registry=Registry.__new__(Registry); registry.store=store
        with store.db() as db:
            registered=db.execute("SELECT 1 FROM sqlite_master WHERE name='reg_projects'").fetchone()
        # Read-only facade: technical verifier observes the caller's fresh scope.
        app=SimpleNamespace(store=store,config=config,
            registry=registry if registered else SimpleNamespace(list_projects=lambda:context['registry_projects']),
            scope_context=lambda kind,key,**kw:copy.deepcopy(context)
                if (kind,key)==(context['review_scope']['kind'],context['review_scope']['id']) else {})
        report=verify(app,transition['transaction_id'])
        closure=report['technical_completion']
        return (report['evidence_usable'] is True and closure['status']=='current'
                and closure['receipt']['id']==transition['technical_receipt_id']
                and report['candidate_id']==transition['candidate_id']
                and report['selection_id']==transition['selection_id']
                and report['step_id']==transition['step_id']
                and report['plan_scope_hash']==transition['from_scope_hash'])
    except (ValueError,KeyError,TypeError,OSError): return False


def confirm(app,technical_receipt_id,observed_scope_hash,selection_id,note,cancel=None):
    from .pilot_actions import _cancel
    from .pilot_verification import verify
    from .plans import PlanBook
    _id(technical_receipt_id);_hash(observed_scope_hash);_id(selection_id);_text(note,2000)
    _cancel(cancel)
    with app.store.lock:
        book=PlanBook(app.store,app.config)
        with app.store.db() as db:
            if not db.execute("SELECT 1 FROM sqlite_master WHERE name='technical_completions'").fetchone():
                raise ValueError('Technischer Abschluss fehlt.')
            row=db.execute('SELECT body FROM technical_completions WHERE id=?',(technical_receipt_id,)).fetchone()
        if not row: raise ValueError('Technischer Abschluss fehlt.')
        technical=json.loads(row['body']); binding=technical['binding']
        candidate=book.get(binding['candidate_id'])
        context=app.scope_context(candidate['scope_kind'],candidate['scope_id'],require_egress=False,force=True)
        _context(context)
        report=verify(app,technical['transaction_id'],cancel)
        if (report['evidence_usable'] is not True or report['technical_completion']['status']!='current'
                or report['technical_completion']['receipt']['id']!=technical_receipt_id
                or report['observed_scope_hash']!=observed_scope_hash or context['scope_hash']!=observed_scope_hash
                or report['selection_id']!=selection_id or observed_scope_hash==candidate['scope_hash']):
            raise ValueError('Aktuelle Aufnahme, technische Nachweise, Auswahl und geänderter Nachher-Stand erforderlich.')
        step=next(s for s in candidate['proposal']['steps'] if s['id']==binding['step_id'])
        if step['depends_on']: raise ValueError('Abhängige Änderungen sind weiterhin gesperrt.')
        transition=dict(id=uuid.uuid4().hex,candidate_id=candidate['id'],step_id=step['id'],
            technical_receipt_id=technical_receipt_id,transaction_id=technical['transaction_id'],
            selection_id=selection_id,from_scope_hash=candidate['scope_hash'],to_scope_hash=observed_scope_hash,
            adapter_hash=identity(),note=note,created_at=now(),actor='operator',execution_enabled=False)
        completion=dict(id=uuid.uuid4().hex,candidate_id=candidate['id'],step_id=step['id'],kind='change_transition',
            transition_id=transition['id'],scope_hash=observed_scope_hash,selection_id=selection_id,
            step_hash=fingerprint(step),predecessor_receipts={},status='accepted',actor='operator',note=note,
            created_at=now(),execution_enabled=False,product_gate_approved=False)
        _cancel(cancel)
        with app.store.db() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS plan_scope_transitions(id TEXT PRIMARY KEY,candidate_id TEXT NOT NULL,body TEXT NOT NULL);
            CREATE TRIGGER IF NOT EXISTS transitions_no_update BEFORE UPDATE ON plan_scope_transitions BEGIN SELECT RAISE(ABORT,'immutable transition'); END;
            CREATE TRIGGER IF NOT EXISTS transitions_no_delete BEFORE DELETE ON plan_scope_transitions BEGIN SELECT RAISE(ABORT,'immutable transition'); END;''')
            db.execute('BEGIN IMMEDIATE')
            if latest(db,candidate['id']): raise ValueError('Für diese Planrevision ist bereits ein Quellenübergang dokumentiert; neuer Plan erforderlich.')
            db.execute('INSERT INTO plan_scope_transitions VALUES(?,?,?)',(transition['id'],candidate['id'],json.dumps(transition)))
            db.execute('INSERT INTO step_completions VALUES(?,?,?,?)',(completion['id'],candidate['id'],step['id'],json.dumps(completion)))
        return dict(transition=transition,completion=completion)
