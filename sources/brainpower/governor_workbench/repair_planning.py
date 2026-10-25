"""Explicit bounded model planning from fresh test failures, never execution."""
from .plans import _id,_text,_proposal
from .test_failure import diagnose

BINDING_FIELDS=('source_job_id','source_evidence_hash','diagnostic_adapter_hash','candidate_id','step_id','scope_hash','selection_id','paths')

def _diagnosis(app,diagnosis_job_id,note):
    _id(diagnosis_job_id);_text(note,2000)
    job=app.store.job(diagnosis_job_id)
    old=(job.get('result') or {}).get('test_failure') or {}
    if job['action']!='plan_failure' or job['status']!='completed' or old.get('evidence_usable') is not True:
        raise ValueError('Aktuelle erfolgreiche Fehlerdiagnose erforderlich.')
    return old


def submission(app,diagnosis_job_id,note):
    """Bind saved consent only; the single worker must prepare fresh evidence before dispatch."""
    from .plans import PlanBook
    old=_diagnosis(app,diagnosis_job_id,note)
    binding={key:old[key] for key in BINDING_FIELDS}
    candidate=PlanBook(app.store,app.config).get(binding['candidate_id'])
    return dict(review_scope=dict(kind=candidate['scope_kind'],id=candidate['scope_id']),scope_hash=binding['scope_hash']),binding


def prepare(app,diagnosis_job_id,note,cancel=None):
    old=_diagnosis(app,diagnosis_job_id,note)
    fresh=diagnose(app,old['source_job_id'],cancel)
    keys=BINDING_FIELDS
    if not fresh['evidence_usable'] or any(old.get(k)!=fresh.get(k) for k in keys):
        raise ValueError('Fehlerdiagnose veraltet; vor Reparaturplanung erneut prüfen.')
    from .plans import PlanBook
    candidate=PlanBook(app.store,app.config).get(fresh['candidate_id'])
    context=app.scope_context(candidate['scope_kind'],candidate['scope_id'],require_egress=True,force=True)
    if context['scope_hash']!=fresh['scope_hash'] or context.get('plan_ready') is not True:
        raise ValueError('Aktuelle Aufnahme und Quellen erforderlich.')
    context=dict(context)
    binding={k:fresh[k] for k in keys}
    from .execution_workspace import WorkspaceStager,_read,_sha
    test_job=app.store.job(fresh['source_job_id']);evidence=test_job['result']['test_evidence']
    stager=WorkspaceStager(app.config['data_dir'])
    sources=[]
    for path in fresh['paths']:
        data=_read(stager.base/evidence['stage_id']/'files',path)
        if data is None:raise ValueError('Gebundene Reparaturquelle fehlt.')
        sources.append(dict(path=path,content=data.decode('utf-8'),sha256=_sha(data)))
    stager.verify_source(evidence['stage_id'],evidence['manifest_hash'])
    context['repair_evidence']=dict(binding=binding,counts=fresh['counts'],output_excerpt=fresh['output_excerpt'],
        output_sha256=fresh['output_sha256'],output_truncated=fresh['output_truncated'],
        output_may_already_be_truncated=True,operator_note=note,root_cause_determined=False,sources=sources)
    context['current_request']=dict(authorized=True,scope='isolated_repair_planning',
        allowed_paths=fresh['paths'],source_scope_hash=fresh['scope_hash'],
        planning_only=True,required_steps='bounded change followed by dependent test',
        file_changes_authorized=False,automatic_sequence_authorized=False)
    return context,binding


def attempts(db,candidate_id,step_id,job_id=None):
    rows=db.execute("SELECT id FROM jobs WHERE action='scope_plan' AND json_extract(request,'$.repair_candidate_id')=? AND json_extract(request,'$.repair_step_id')=? ORDER BY rowid DESC",(candidate_id,step_id)).fetchall()
    if len(rows)>(2 if job_id else 1) or (job_id and (not rows or rows[0]['id']!=job_id)):
        raise ValueError('Reparaturplan-Versuchslimit erreicht oder neuerer Auftrag vorhanden.')
    return len(rows)


def validate(proposal,binding,project_id):
    proposal=_proposal(proposal,{project_id})
    steps={s['id']:s for s in proposal['steps']}
    allowed=set(binding['paths'])
    if any(not set(s['scope'])<=allowed for s in steps.values()):
        raise ValueError('Reparaturplan erweitert den bestätigten Dateiumfang.')
    changes={s['id'] for s in steps.values() if s['action']=='change'}
    if len(changes)!=1 or steps[next(iter(changes))]['depends_on']:
        raise ValueError('Reparaturpilot benötigt genau eine unabhängige Änderung; komplexere Folgen benötigen separate Planung.')
    from functools import lru_cache
    @lru_cache(maxsize=50)
    def parents(key):
        return set(steps[key]['depends_on']) | set().union(*(parents(p) for p in steps[key]['depends_on']))
    if not changes or not any(s['action']=='test' and changes<=parents(s['id']) for s in steps.values()):
        raise ValueError('Reparaturplan benötigt Änderung und nachgeordneten Test aller Änderungen.')
    return proposal
