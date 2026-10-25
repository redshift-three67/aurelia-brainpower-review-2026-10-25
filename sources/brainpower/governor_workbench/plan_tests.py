"""Explicit standalone plan tests; no models, original writes or automatic follow-ups."""
import hashlib
import json
import uuid
from pathlib import Path

from .evidence import fingerprint, now
from .execution_policy import require_staging_pilot
from .execution_workspace import WorkspaceStager, _read, _sha, _root, MAX_MANIFEST_BYTES
from .plans import PlanBook
from .staged_tests import run_staged_tests, require_current_adapter
from .pilot_actions import _cancel
from .registry import INITIAL_ROLES

MAX_ATTEMPTS = 3


def attempt_policy(db,candidate_id,step_id,job_id=None):
    """Journal order is authoritative; a new selection never resets this budget."""
    where="action='plan_test' AND json_extract(request,'$.candidate_id')=? AND json_extract(request,'$.step_id')=?"
    args=(candidate_id,step_id)
    used=db.execute('SELECT COUNT(*) FROM jobs WHERE '+where,args).fetchone()[0]
    history=[dict(r) for r in db.execute('SELECT id,status,created_at FROM jobs WHERE '+where+' ORDER BY rowid DESC LIMIT 3',args)]
    reason=''
    if job_id:
        if not history or history[0]['id']!=job_id or history[0]['status'] not in ('queued','running'):
            reason='Testversuch ist nicht der neueste aktive Auftrag.'
        elif used>MAX_ATTEMPTS: reason='Versuchslimit überschritten; neuer Plan erforderlich.'
    elif used>=MAX_ATTEMPTS:
        reason='Drei Testversuche verbraucht; neuer Plan erforderlich.'
    if not reason and any(r['status'] in ('queued','running') and r['id']!=job_id for r in history):
        reason='Ein Testversuch ist bereits eingeplant oder läuft.'
    return dict(limit=MAX_ATTEMPTS,used=used,remaining=max(0,MAX_ATTEMPTS-used),
                allowed=not reason,reason=reason,history=history,automatic_retry=False)


def adapter_hash():
    return fingerprint({name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                        for name in ('plan_tests.py','plans.py','execution_policy.py')})


def eligibility(config,context,candidate,step_id):
    if not config: raise ValueError('Testkonfiguration fehlt.')
    step=require_staging_pilot(config,context,candidate,step_id,{'plan_selection_approved':True},test_step=True)
    root,_=_root(context['registry_projects'][0]['path'])
    for project in config.get('projects',[]):
        if project['id'] in INITIAL_ROLES:
            historical=Path(project['path']).resolve()
            if root==historical or root.is_relative_to(historical) or historical.is_relative_to(root):
                raise ValueError('Historische Produktwurzel ist kein Testpilot.')
    return step,root


def successful(result):
    return (result.get('success') is True and result.get('sources_verified') is True
            and result.get('completion_verified') is True and type(result.get('exit_code')) is int and result['exit_code']==0
            and all(type(result.get(k)) is int for k in ('count','skipped','errors','failures'))
            and 0<=result['skipped']<result['count']<=1000000 and result['errors']==result['failures']==0)


def valid_receipt(db,receipt,config,context,candidate,step):
    try:
        _,root=eligibility(config,context,candidate,step['id'])
        row=db.execute("SELECT id,status,result FROM jobs WHERE action='plan_test' AND json_extract(request,'$.candidate_id')=? AND json_extract(request,'$.step_id')=? ORDER BY rowid DESC LIMIT 1",
                       (candidate['id'],step['id'])).fetchone()
        if not row or row['id']!=receipt['job_id'] or row['status']!='completed': return False
        result=json.loads(row['result']) or {}
        if result.get('success') is not True or (result.get('completion_receipt') or {}).get('id')!=receipt['id']:
            return False
        evidence=result.get('test_evidence') or {}
        if (fingerprint(evidence)!=receipt['evidence_hash'] or not successful(evidence['test'])
                or evidence['plan_test_adapter_hash']!=adapter_hash()): return False
        require_current_adapter(evidence['test'])
        stager=WorkspaceStager(config['data_dir'])
        stager.verify_source(evidence['stage_id'],evidence['manifest_hash'])
        manifest=json.loads(_read(stager.base/evidence['stage_id'],'manifest.json',MAX_MANIFEST_BYTES))
        if manifest['original_root']!=str(root) or manifest['root_identity']!=_root(root)[1]: return False
        return True
    except (ValueError,TypeError,KeyError,OSError): return False


def preflight(app,request):
    book=PlanBook(app.store,app.config); candidate=book.get(request['candidate_id'])
    context=app.scope_context(candidate['scope_kind'],candidate['scope_id'],require_egress=False,force=True)
    report=book.dependency_report(candidate['id'],context)
    row=next((s for s in report['steps'] if s['id']==request['step_id']),None)
    if (not report['current'] or report['scope_hash']!=request['scope_hash']
            or report['selection_id']!=request['selection_id'] or not row or not row['selected']
            or row['action']!='test' or row['missing_completion_ids']):
        raise ValueError('Test benötigt aktuelle Auswahl und sämtliche aktuellen Vorgängerbelege.')
    candidate=dict(candidate,scope_hash=report['scope_hash'])
    step,root=eligibility(app.config,context,candidate,row['id'])
    predecessors={s['id']:s['completion_receipt']['id'] for s in report['steps'] if s['id'] in step['depends_on']}
    return candidate,step,root,predecessors


def run(app,job,cancel,on_line):
    _cancel(cancel); request=job['request']
    with app.store.lock:
        with app.store.db() as db:
            attempts=attempt_policy(db,request['candidate_id'],request['step_id'],job['id'])
        if not attempts['allowed']: raise ValueError(attempts['reason'])
        candidate,step,root,predecessors=preflight(app,request)
        identity=adapter_hash()
        hashes={}; copies=[]
        for path in step['scope']:
            data=_read(root,path)
            if data is None: raise ValueError('Alle ausgewählten Testdateien müssen vorhanden sein.')
            hashes[path]=_sha(data)
            copies.append(dict(path=path,content=data.decode('utf-8')))
        stager=WorkspaceStager(app.config['data_dir'])
        stage=stager.stage(str(root),step['scope'],copies,hashes)
    test=run_staged_tests(stager,stage['id'],stage['manifest_hash'],cancel,on_line)
    evidence=dict(test=test,stage_id=stage['id'],manifest_hash=stage['manifest_hash'],
                  plan_test_adapter_hash=identity,scope_hash=request['scope_hash'],selection_id=request['selection_id'],
                  step_hash=fingerprint(step),predecessor_receipts=predecessors)
    if not successful(test):
        return dict(success=False,test_evidence=evidence,summary='Test nicht bestanden; kein Abschlussbeleg.',execution_enabled=False)
    with app.store.lock:
        _,current_step,_,current_predecessors=preflight(app,request)
        if fingerprint(current_step)!=fingerprint(step) or predecessors!=current_predecessors or adapter_hash()!=identity:
            raise ValueError('Schritt, Vorgänger oder Testadapter während des Tests verändert.')
        require_current_adapter(test); stager.verify_source(stage['id'],stage['manifest_hash'])
        _cancel(cancel)
        receipt=dict(id=uuid.uuid4().hex,candidate_id=candidate['id'],step_id=step['id'],status='accepted',kind='plan_test',
                     scope_hash=request['scope_hash'],selection_id=request['selection_id'],step_hash=fingerprint(step),
                     predecessor_receipts=predecessors,actor='test_adapter',note='Gebundener stdlib-Unittest erfolgreich.',
                     created_at=now(),job_id=job['id'],evidence_hash=fingerprint(evidence),
                     execution_enabled=False,product_gate_approved=False)
        with app.store.db() as db:
            latest=db.execute("SELECT id FROM jobs WHERE action='plan_test' AND json_extract(request,'$.candidate_id')=? AND json_extract(request,'$.step_id')=? ORDER BY rowid DESC LIMIT 1",
                              (candidate['id'],step['id'])).fetchone()
            if not latest or latest['id']!=job['id']: raise ValueError('Neuerer Testversuch vorhanden.')
            db.execute('INSERT INTO step_completions VALUES(?,?,?,?)',(receipt['id'],candidate['id'],step['id'],json.dumps(receipt)))
    return dict(success=True,test_evidence=evidence,completion_receipt=receipt,execution_enabled=False,
                summary='Ausgewählter Testschritt belegt; keine automatische Fortsetzung oder Produktfreigabe.')
