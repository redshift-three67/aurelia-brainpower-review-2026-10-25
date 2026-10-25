"""Strict authenticated-handler dispatch for explicit dependent pilot decisions."""
from .plans import _id
from .change_journal import ChangeJournal


FIELDS={
    'state':{'candidate_id'},
    'begin':{'candidate_id','step_ids','binding_hash','note'},
    'successor-preview':{'chain_id'},
    'acknowledge':{'chain_id','binding_hash','note'},
    'confirm':{'chain_id','expected_head','technical_receipt_id','observed_scope_hash','selection_id','note'},
    'propose':{'consent_id'},
}


def state(app,candidate_id):
    _id(candidate_id)
    journal=ChangeJournal.__new__(ChangeJournal);journal.store=app.store
    with app.store.db() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='dependent_change_chains'").fetchone():
            return dict(chains=[],consents=[])
        row=db.execute('SELECT id FROM dependent_change_chains WHERE candidate_id=?',(candidate_id,)).fetchone()
        if not row:return dict(chains=[],consents=[])
        value=journal.read(row['id']);consents=[]
        if db.execute("SELECT 1 FROM sqlite_master WHERE name='dependent_change_successor_consents'").fetchone():
            from .change_successor import _decode
            consents=[_decode(r) for r in db.execute('SELECT * FROM dependent_change_successor_consents WHERE chain_id=? LIMIT 2',(row['id'],))]
    return dict(chains=[value],consents=consents)


def dispatch(app,operation,data):
    if operation not in FIELDS or set(data)!=FIELDS[operation]:raise ValueError('Ungültige Felder für die ausdrückliche Änderungsentscheidung.')
    if operation=='state':return state(app,**data),200
    if operation=='begin':
        from .change_controller import begin
        return dict(chain=begin(app,**data)),200
    if operation=='successor-preview':
        from .change_successor import preview
        return preview(app,**data),200
    if operation=='acknowledge':
        from .change_successor import acknowledge
        return dict(consent=acknowledge(app,**data)),200
    if operation=='confirm':
        from .change_controller import confirm
        return dict(event=confirm(app,**data)),200
    from .change_successor import require_current
    receipt=require_current(app,data['consent_id']);b=receipt['binding']
    from .plans import PlanBook
    book=PlanBook.__new__(PlanBook);book.store=app.store;book.config=app.config
    candidate=book.get(b['candidate_id'])
    job=app.runner.submit('scope_patch',scope_kind=candidate['scope_kind'],scope_id=candidate['scope_id'],
                          candidate_id=candidate['id'],step_id=b['step_id'],successor_consent_id=receipt['id'])
    return dict(job=job),202
