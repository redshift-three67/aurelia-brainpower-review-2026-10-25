"""Trusted B binding; historical A proof is never a test approval for B."""
import json

from .evidence import fingerprint
from .plans import PlanBook, _context
from .change_controller import identity, _environment
from .change_journal import _observe as observe_files
from .change_successor import _journal, _decode, require_current


def _original(app,receipt,request,context):
    b=receipt['binding'];_context(context)
    book=PlanBook.__new__(PlanBook);book.store=app.store;book.config=app.config
    candidate=book.get(b['candidate_id'])
    step=next(s for s in candidate['proposal']['steps'] if s['id']==b['step_id'])
    with app.store.db() as db:
        latest=db.execute('SELECT id FROM plan_candidates WHERE scope_kind=? AND scope_id=? ORDER BY version DESC LIMIT 1',
                          (candidate['scope_kind'],candidate['scope_id'])).fetchone()
        row=db.execute('SELECT body FROM plan_approvals WHERE candidate_id=? ORDER BY rowid DESC LIMIT 1',(candidate['id'],)).fetchone()
    selection=json.loads(row['body']) if row else {}
    if (not latest or latest['id']!=candidate['id']
            or (request.get('candidate_id'),request.get('step_id'),request.get('scope_kind'),request.get('scope_id'),request.get('scope_hash'))
                !=(b['candidate_id'],b['step_id'],candidate['scope_kind'],candidate['scope_id'],b['effective_scope_hash'])
            or context['review_scope']!={'kind':candidate['scope_kind'],'id':candidate['scope_id']}
            or candidate['scope_hash']!=b['original_scope_hash'] or fingerprint(step)!=b['step_hash']
            or selection.get('id')!=b['selection_id'] or b['step_id'] not in selection.get('selected_step_ids',[])
            or selection.get('proposal_hash')!=candidate['proposal_hash'] or selection.get('scope_hash')!=candidate['scope_hash']
            or b['adapter_hash']!=identity() or b['environment_hash']!=_environment(app)):
        raise ValueError('Originalplan, Auswahl oder Nachfolgerbindung verändert.')
    return candidate,step


def resolve(app,request,context):
    from .execution_policy import require_staging_pilot
    if 'successor_consent_id' not in request:
        book=PlanBook(app.store);candidate=book.get(request['candidate_id'])
        permission=book.execution_permission(candidate['id'],request['step_id'],context)
        step=require_staging_pilot(app.config,context,candidate,request['step_id'],permission)
        return candidate,step,permission
    receipt=require_current(app,request['successor_consent_id'])
    candidate,step=_original(app,receipt,request,context)
    b=receipt['binding']
    if context['scope_hash']!=b['effective_scope_hash']:raise ValueError('Aktueller H1-Stand erforderlich.')
    return candidate,step,dict(plan_selection_approved=True,plan_selection_id=b['selection_id'],
        execution_enabled=False,successor_binding=proof(receipt))


def proof(receipt):
    b=receipt['binding']
    return dict(successor_consent_id=receipt['id'],successor_binding_hash=receipt['binding_hash'],
                original_scope_hash=b['original_scope_hash'],predecessor_event_id=b['predecessor_event_id'],
                predecessor_event_hash=b['predecessor_event_hash'])


def require_latest_source(app,request,source_id):
    if 'successor_consent_id' not in request:return
    with app.store.db() as db:
        row=db.execute("SELECT id FROM jobs WHERE action='scope_patch' AND json_extract(request,'$.candidate_id')=? AND json_extract(request,'$.step_id')=? ORDER BY rowid DESC LIMIT 1",
                       (request['candidate_id'],request['step_id'])).fetchone()
    if not row or row['id']!=source_id:raise ValueError('Neuerer B-Vorschlag vorhanden; ältere Nachweise dürfen nicht ausgeführt werden.')


def applied(app,request,context,tx,manifest,test):
    """Validate B's post-apply state with historical A, without synthesizing H1 context."""
    from .pilot_verification import verify
    from .technical_completion import binding as technical_binding
    with app.store.db() as db:
        receipt=_decode(db.execute('SELECT * FROM dependent_change_successor_consents WHERE id=?',
                                   (request['successor_consent_id'],)).fetchone())
    candidate,step=_original(app,receipt,request,context);b=receipt['binding']
    if test['result'].get('successor_binding')!=proof(receipt):raise ValueError('Eigener gebundener B-Test fehlt.')
    state=_journal(app.store).read(b['chain_id']);base=state['chain']['binding']
    if state['requires_new_plan'] or len(state['events']) not in (1,2):raise ValueError('Unveränderte lineare Historie erforderlich.')
    edge=state['events'][0]
    if (edge['id']!=b['predecessor_event_id'] or fingerprint(edge)!=b['predecessor_event_hash']
            or state['active_transition_ids']!=[e['id'] for e in state['events']]
            or (len(state['events'])==2 and state['events'][1]['evidence']['transaction']['id']!=tx['id'])):
        raise ValueError('Historischer A-Vorgänger verändert oder B nicht passend.')
    historical=edge['evidence'];a=historical['technical_receipt']
    report=verify(app,historical['transaction']['id'])
    # H2 is observed truthfully. Only scope equality is historical; all other
    # A transaction/test/selection/root/adapter evidence must still match.
    fresh=technical_binding(report);old=dict(a['binding'])
    fresh.pop('observed_scope_hash');old.pop('observed_scope_hash')
    if (report['evidence_usable'] is not True or fresh!=old
            or report['technical_completion']['receipt']!=a
            or fingerprint(a)!=b['predecessor_receipt_hash']):
        raise ValueError('Historischer A-Nachweis nicht mehr belastbar.')
    with app.store.db() as db:
        latest=db.execute("SELECT * FROM jobs WHERE action='pilot_verify' AND json_extract(request,'$.transaction_id')=? ORDER BY rowid DESC LIMIT 1",
                          (a['transaction_id'],)).fetchone()
        newer=db.execute("SELECT 1 FROM pilot_apply_transactions WHERE rowid>(SELECT rowid FROM pilot_apply_transactions WHERE id=?) AND id<>? AND json_extract(body,'$.original_root')=? AND status NOT IN ('rolled_back','conflict')",
                         (a['transaction_id'],tx['id'],tx['original_root'])).fetchone()
    job=app.store.decode(latest) if latest else {}
    if (job.get('id')!=a['verified_job_id'] or job.get('status')!='completed'
            or job.get('result',{}).get('success') is not True
            or technical_binding(job['result']['post_apply_verification'])!=a['binding'] or newer):
        raise ValueError('Neuerer A-Versuch oder ungeklärte weitere Übernahme vorhanden.')
    if (tx['scope_hash']!=b['effective_scope_hash'] or manifest['original_root']!=b['root']
            or manifest['root_identity']!=b['root_identity']
            or {f['path'] for f in manifest['files']}!=set(step['scope'])):
        raise ValueError('B-Übernahme weicht vom bestätigten H1 ab.')
    files=dict(b['files'])
    for f in manifest['files']:
        if f['original_sha256']!=files[f['path']]:raise ValueError('B-Dateivorgänger stimmt nicht mit H1 überein.')
        files[f['path']]=f['staged_sha256']
    observe_files(b,files)
    return proof(receipt)


class GuardedClient:
    def __init__(self,client,app,request,source_id=None):
        self.client=client;self.app=app;self.request=request;self.source_id=source_id
    def prompt_limit(self,model):return self.client.prompt_limit(model)
    def call(self,model,prompt,**kwargs):
        if 'successor_consent_id' in self.request:
            require_latest_source(self.app,self.request,self.source_id)
            context=self.app.scope_context(self.request['scope_kind'],self.request['scope_id'],require_egress=True,force=True)
            resolve(self.app,self.request,context)
        return self.client.call(model,prompt,**kwargs)
