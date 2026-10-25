"""Internal, explicit S3 journal consent; no routes, models or dependent dispatch.

Inputs are references and observed hashes, never caller-supplied evidence. The
authenticated UI integration is C4. Any concurrent DB commit during observation
conservatively invalidates consent; callers must preview/recheck, never auto-retry.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import uuid

from .evidence import fingerprint, now
from .execution_workspace import _sha
from .plans import PlanBook, _context, _hash, _id, _text
from .change_journal import ChangeJournal
from .change_rollback import require_no_physical_claim
from .pilot_actions import _cancel
from .sequence_store import require_idle


def identity():
    names=('change_controller.py','change_successor.py','change_execution.py','change_chain_preview.py','change_journal.py',
           'change_journal_evidence.py','change_rollback.py','pilot_apply.py',
           'pilot_actions.py','pilot_verification.py','technical_completion.py',
           'plans.py','execution_policy.py','execution_workspace.py','staged_tests.py','job_routing.py','routing_policy.py','evidence.py','git_status.py')
    return fingerprint({n:_sha(Path(__file__).with_name(n).read_bytes()) for n in names})


def _environment(app):
    settings = app.store.settings()
    return fingerprint(dict(roots=app.config.get('staging_pilot_roots'),
                            reasoning_mode=settings.get('reasoning_mode',app.config.get('reasoning_mode','medium')),
                            supervisor=settings.get('supervisor',app.config.get('supervisor','gpt-5.6-sol')),
                            projects=app.config.get('projects'),
                            data_dir=str(app.config['data_dir']),
                            registry=app.registry.list_projects()))


@contextmanager
def _claim(app,operation,cancel):
    _cancel(cancel)
    with app.store.lock:
        key=uuid.uuid4().hex
        with app.store.db() as db:
            db.execute('BEGIN IMMEDIATE');require_idle(db);require_no_physical_claim(db)
            db.execute('INSERT INTO jobs(id,action,status,created_at,started_at,request) VALUES(?,?,?,?,?,?)',
                       (key,'change_journal_commit','running',now(),now(),json.dumps({'operation':operation})))
        try:
            # Schema initialization precedes the read window. No automatic startup activation.
            journal=ChangeJournal(app.store)
            with app.store.db() as watch:
                version=watch.execute('PRAGMA data_version').fetchone()[0]
                adapter=identity()
                environment=_environment(app)
                def commit(db):
                    _cancel(cancel)
                    if (watch.execute('PRAGMA data_version').fetchone()[0]!=version
                            or identity()!=adapter or _environment(app)!=environment):
                        raise ValueError('Journal oder Adapter während Belegprüfung verändert; erneut prüfen.')
                    row=db.execute('SELECT status FROM jobs WHERE id=?',(key,)).fetchone()
                    if not row or row['status']!='running':raise ValueError('Reservierung unterbrochen.')
                    require_no_physical_claim(db)
                    db.execute("UPDATE jobs SET status='completed',ended_at=?,result=? WHERE id=?",
                               (now(),json.dumps({'success':True,'execution_authorized':False}),key))
                yield journal,commit
        finally:
            # On exception only: successful terminal status committed with journal event.
            with app.store.db() as db:
                db.execute("UPDATE jobs SET status=?,ended_at=?,error=? WHERE id=? AND status='running'",
                           ('cancelled' if cancel is not None and cancel.is_set() else 'failed',now(),
                            'Journalbestätigung nicht abgeschlossen; ausdrücklich erneut prüfen.',key))


def begin(app,candidate_id,step_ids,binding_hash,note,cancel=None):
    from .change_chain_preview import preview
    _id(candidate_id);_hash(binding_hash);_text(note,2000)
    with _claim(app,'baseline',cancel) as (journal,commit):
        shown=preview(app,candidate_id,step_ids)
        if not shown['eligible'] or shown['binding_hash']!=binding_hash:
            raise ValueError('Aktuelle unveränderte Zweischrittvorschau erforderlich.')
        p=shown['binding']
        book=PlanBook.__new__(PlanBook);book.store=app.store;book.config=app.config
        candidate=book.get(candidate_id)
        steps={s['id']:s for s in candidate['proposal']['steps']}
        binding={k:p[k] for k in ('candidate_id','selection_id','step_ids','step_hashes','root','root_identity','scope_hash','sources')}
        binding.update(step_scopes={k:steps[k]['scope'] for k in p['step_ids']},adapter_hash=identity())
        return journal.create(binding,note,controller_binding=p,before_commit=commit)


def _collect(app,journal,chain_id,technical_id,observed,selection,cancel,*,historical_tip=False):
    from .pilot_verification import verify
    from . import pilot_actions
    from .technical_completion import binding as completion_binding
    from .change_journal_evidence import transition
    from .change_journal import _observe
    state=journal.read(chain_id);chain=state['chain'];base=chain['binding']
    consent=chain.get('controller_binding')
    if not consent or base['adapter_hash']!=identity() or state['requires_new_plan']:
        raise ValueError('Aktuelle Controllerbindung ohne Rücknahme erforderlich.')
    if selection!=base['selection_id']:raise ValueError('Auswahl weicht von ursprünglicher Zustimmung ab.')
    with app.store.db() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='technical_completions'").fetchone():
            raise ValueError('Technischer Abschluss fehlt.')
        row=db.execute('SELECT body FROM technical_completions WHERE id=?',(technical_id,)).fetchone()
    if not row:raise ValueError('Technischer Abschluss fehlt.')
    receipt=json.loads(row['body'])
    if receipt['id']!=technical_id:raise ValueError('Abschlussreferenz stimmt nicht überein.')
    report=verify(app,receipt['transaction_id'],cancel)
    if (report['evidence_usable'] is not True or report['technical_completion']['status']!='current'
            or report['technical_completion']['receipt']!=receipt or report['observed_scope_hash']!=observed
            or report['selection_id']!=selection or report['candidate_id']!=base['candidate_id']):
        raise ValueError('Aktueller technischer Abschluss und unveränderte Auswahl erforderlich.')
    job=app.store.job(receipt['verified_job_id']);result=job.get('result') or {}
    with app.store.db() as db:
        latest=db.execute("SELECT id FROM jobs WHERE action='pilot_verify' AND json_extract(request,'$.transaction_id')=? ORDER BY rowid DESC LIMIT 1",
                          (receipt['transaction_id'],)).fetchone()
    if (not latest or latest['id']!=job['id'] or job['action']!='pilot_verify' or job['status']!='completed'
            or job['request'].get('transaction_id')!=receipt['transaction_id'] or result.get('success') is not True
            or result.get('post_apply_verification',{}).get('evidence_usable') is not True
            or completion_binding(result['post_apply_verification'])!=receipt['binding']):
        raise ValueError('Neuester erfolgreicher Nachprüfungsauftrag erforderlich.')
    tx=pilot_actions._pilot(app).transaction(receipt['transaction_id'])
    proposal=pilot_actions._proposal(app,tx['proposal_id'])
    book=PlanBook.__new__(PlanBook);book.store=app.store;book.config=app.config
    candidate=book.get(base['candidate_id'])
    context=app.scope_context(candidate['scope_kind'],candidate['scope_id'],require_egress=False,force=True)
    kind,key,scope,projects=_context(context)
    if (kind,key,scope)!=(candidate['scope_kind'],candidate['scope_id'],observed):
        raise ValueError('Aktueller Aufnahme-/Quellenkontext stimmt nicht überein.')
    steps={s['id']:s for s in candidate['proposal']['steps']}
    if (candidate['proposal_hash']!=consent['proposal_hash']
            or any(fingerprint(steps[k])!=base['step_hashes'][k] for k in base['step_ids'])):
        raise ValueError('Schrittdefinition verändert.')
    with app.store.db() as db:
        approval=db.execute('SELECT body FROM plan_approvals WHERE candidate_id=? ORDER BY rowid DESC LIMIT 1',(candidate['id'],)).fetchone()
        selection_body=json.loads(approval['body']) if approval else {}
        if (selection_body.get('id')!=selection or not set(base['step_ids'])<=set(selection_body.get('selected_step_ids',[]))):
            raise ValueError('Ursprüngliche vollständige Auswahl fehlt.')
        # An unadopted newer transfer must not be silently crossed.
        newer=db.execute("SELECT 1 FROM pilot_apply_transactions WHERE rowid>(SELECT rowid FROM pilot_apply_transactions WHERE id=?) AND json_extract(body,'$.original_root')=? AND status NOT IN ('rolled_back','conflict')",
                         (tx['id'],tx['original_root'])).fetchone()
        if newer:raise ValueError('Neuere Übernahme muss separat geklärt werden.')
    if consent['external_receipts']:
        # Legacy current verification cannot certify historical external prerequisites
        # at H1. Keep these profiles closed until the dependent-proof adapter exists.
        raise ValueError('Externe Vorgänger nach Quellenwechsel benötigen den C3-Belegadapter.')
    evidence=dict(transaction=tx,manifest=proposal['manifest'],technical_receipt=receipt)
    if historical_tip:
        # Certify the already recorded first edge against current H1; never invent
        # a different current context or reinterpret A's tests as B's tests.
        if (len(state['events'])!=1 or state['transition_count']!=1
                or state['active_transition_ids']!=[state['head_id']]
                or state['events'][0]['evidence']!=evidence):
            raise ValueError('Genau ein unveränderter bestätigter A-Übergang erforderlich.')
        after,_=transition(base,base['sources'],base['scope_hash'],0,evidence)
        if after!=state['files']:raise ValueError('Historischer Übergang passt nicht zur aktuellen Spitze.')
    else:
        after,_=transition(base,state['files'],state['scope_hash'],state['transition_count'],evidence)
    _observe(base,after)
    _cancel(cancel)
    return state,evidence


def confirm(app,chain_id,expected_head,technical_receipt_id,observed_scope_hash,selection_id,note,cancel=None):
    for key in (chain_id,technical_receipt_id,selection_id):_id(key)
    if expected_head is not None:_id(expected_head)
    _hash(observed_scope_hash);_text(note,2000);_cancel(cancel)
    with _claim(app,'transition',cancel) as (journal,commit):
        saved=journal.read(chain_id)
        for event in saved['events']:
            if event['kind']!='transition' or event['evidence']['technical_receipt']['id']!=technical_receipt_id:continue
            proof=event['evidence']['technical_receipt']['binding']
            if (event['previous_id'],proof['observed_scope_hash'],proof['selection_id'],event['note'])!=(expected_head,observed_scope_hash,selection_id,note):
                raise ValueError('Abschluss bereits mit anderer Zustimmung gebunden.')
            # Exact retry is history, not renewed execution permission.
            return journal.transition(chain_id,expected_head,event['evidence'],note,before_commit=commit)
        state,evidence=_collect(app,journal,chain_id,technical_receipt_id,observed_scope_hash,selection_id,cancel)
        again,proof=_collect(app,journal,chain_id,technical_receipt_id,observed_scope_hash,selection_id,cancel)
        if state!=again or evidence!=proof or state['head_id']!=expected_head:
            raise ValueError('Belege oder Journalspitze seit Anzeige verändert.')
        return journal.transition(chain_id,expected_head,evidence,note,before_commit=commit)
