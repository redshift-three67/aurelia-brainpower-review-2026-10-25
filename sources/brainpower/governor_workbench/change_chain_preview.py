"""Read-only S3a observation. Structural eligibility never grants execution."""
import os
from pathlib import Path

from .evidence import fingerprint
from .execution_workspace import _read, _root, _sha, MAX_TOTAL_BYTES
from .plans import PlanBook, _context, _id, _proposal
from .registry import INITIAL_ROLES
from .staged_tests import adapter_identity


REASONS = {
    'request': 'Genau zwei unterschiedliche gültige Änderungsschritte erforderlich.',
    'missing_plan': 'Plan oder gespeicherte Auswahl-/Abschlussstruktur fehlt.',
    'stale_plan': 'Aufnahme, Planrevision oder Quellenstand ist nicht aktuell.',
    'selection': 'Beide Änderungen müssen aktuell ausdrücklich ausgewählt sein.',
    'chain_shape': 'Erforderlich ist eine direkte Zweierfolge A → B ohne weitere abhängige Zwischenschritte.',
    'transition_pending': 'Ein Quellenübergang besteht bereits; historische Fortschrittsprüfung benötigt S3b.',
    'missing_predecessor': 'Ein externer Vorgänger besitzt keinen aktuellen Abschlussbeleg.',
    'pilot_scope': 'Aktiver unabhängiger Pilot mit ausdrücklich erlaubter kanonischer Wurzel erforderlich.',
    'overlapping_scope': 'Schreibbereiche überschneiden sich oder enthalten aliasierte Pfade.',
    'source_unreadable': 'Dateien oder Wurzel sind nicht sicher lesbar oder überschreiten die Vorschaugrenzen.',
    'observation_drift': 'Quellen, Auswahl, Belege oder Adapter änderten sich während der Vorschau.',
    'unavailable': 'Vorschau nicht vollständig prüfbar; keine Freigabe.',
}


class Blocked(ValueError):
    pass


def _observe(app, candidate_id, requested):
    with app.store.db() as db:
        tables={r['name'] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not {'plan_candidates','plan_approvals','step_completions'} <= tables:
        raise Blocked('missing_plan')
    # Avoid PlanBook.__init__: a preview must never create journal schemas.
    book=PlanBook.__new__(PlanBook); book.store=app.store; book.config=app.config
    try:
        candidate=book.get(candidate_id)
    except ValueError as exc:
        raise Blocked('missing_plan') from exc
    context=app.scope_context(candidate['scope_kind'],candidate['scope_id'],require_egress=False,force=True)
    try:
        kind,key,scope_hash,projects=_context(context)
        report=book.dependency_report(candidate_id,context)
    except ValueError as exc:
        raise Blocked('stale_plan') from exc
    if not report['current']:
        raise Blocked('stale_plan')
    if report['source_transition']:
        raise Blocked('transition_pending')
    steps={s['id']:s for s in _proposal(candidate['proposal'],projects)['steps']}
    rows={r['id']:r for r in report['steps']}
    if (not report['selection_id'] or not requested <= steps.keys()
            or any(not rows[k]['selected'] or steps[k]['action']!='change' for k in requested)):
        raise Blocked('selection')
    ordered=[k for k in steps if k in requested and not (set(rows[k]['all_predecessors']) & requested)]
    if len(ordered)!=1:
        raise Blocked('chain_shape')
    a=ordered[0]; b=next(k for k in requested if k!=a); ordered.append(b)
    if a not in steps[b]['depends_on']:
        raise Blocked('chain_shape')
    external={}
    for k in ordered:
        for dep in rows[k]['all_predecessors']:
            if dep in requested:
                continue
            # A → review/test → B is not the approved direct two-change profile.
            if set(rows[dep]['all_predecessors']) & requested:
                raise Blocked('chain_shape')
            if rows[dep]['completion_status']!='accepted':
                raise Blocked('missing_predecessor')
            receipt=rows[dep]['completion_receipt']
            external[dep]=dict(id=receipt['id'],hash=fingerprint(receipt))
    project=context['registry_projects'][0]
    roots=app.config.get('staging_pilot_roots')
    if (kind!='project' or project['id'] in INITIAL_ROLES or project.get('archived') is not False
            or 'group_id' not in project or project['group_id'] is not None
            or not isinstance(roots,list) or not 1<=len(roots)<=5):
        raise Blocked('pilot_scope')
    try:
        root,identity=_root(project.get('path'))
        allowed=[os.path.normcase(str(_root(p)[0])) for p in roots if isinstance(p,str)]
        if len(allowed)!=len(roots) or os.path.normcase(str(root)) not in allowed:
            raise ValueError('Not allowlisted')
    except (ValueError,OSError) as exc:
        raise Blocked('pilot_scope') from exc
    paths=[]
    for k in ordered:
        if not 1<=len(steps[k]['scope'])<=20:
            raise Blocked('source_unreadable')
        for path in steps[k]['scope']:
            normalized=path.casefold()
            if any(normalized==old or normalized.startswith(old+'/') or old.startswith(normalized+'/') for old in paths):
                raise Blocked('overlapping_scope')
            paths.append(normalized)
    sources={};total=0
    try:
        for k in ordered:
            for path in steps[k]['scope']:
                raw=_read(root,path)
                total+=len(raw) if raw is not None else 0
                if total>MAX_TOTAL_BYTES:
                    raise ValueError('Byte budget')
                sources[path]=_sha(raw) if raw is not None else None
    except (ValueError,OSError) as exc:
        raise Blocked('source_unreadable') from exc
    files=('change_chain_preview.py','plans.py','execution_policy.py','execution_workspace.py','change_chain.py')
    binding=dict(profile_id='dependent_change_preview_v1',candidate_id=candidate_id,
        proposal_hash=candidate['proposal_hash'],selection_id=report['selection_id'],scope_hash=scope_hash,
        step_ids=ordered,step_hashes={k:fingerprint(steps[k]) for k in ordered},
        root=str(root),root_identity=identity,sources=sources,external_receipts=external,
        pilot_roots=sorted(allowed),test_adapter=adapter_identity(),
        profile_files={name:_sha(Path(__file__).with_name(name).read_bytes()) for name in files})
    views=[dict(id=k,title=steps[k]['title'],readiness='conditional' if k==b else 'prerequisites_observed',
        waiting_for=[a] if k==b else [],execution_authorized=False) for k in ordered]
    return binding,views


def preview(app,candidate_id,step_ids):
    result=dict(eligible=False,profile_id='dependent_change_preview_v1',binding=None,binding_hash=None,steps=[],
        execution_authorized=False,model_transmission_required=False,creates_jobs_or_receipts=False)
    try:
        try:
            _id(candidate_id)
            if not isinstance(step_ids,list) or len(step_ids)!=2:
                raise ValueError('Two steps')
            for key in step_ids:_id(key)
            if len(set(step_ids))!=2:
                raise ValueError('Duplicate')
        except ValueError as exc:
            raise Blocked('request') from exc
        first,views=_observe(app,candidate_id,set(step_ids))
        second,_=_observe(app,candidate_id,set(step_ids))
        if fingerprint(first)!=fingerprint(second):
            raise Blocked('observation_drift')
        result.update(eligible=True,binding=first,binding_hash=fingerprint(first),steps=views,
            reason_code='preview_only',reason='Strukturell passende Zweierfolge. B benötigt den bestätigten Abschluss von A und eigene neue Prüfungen. Ausführung bleibt gesperrt.')
    except Blocked as exc:
        result.update(reason_code=str(exc),reason=REASONS[str(exc)])
    except (ValueError,KeyError,TypeError,OSError):
        result.update(reason_code='unavailable',reason=REASONS['unavailable'])
    return result
