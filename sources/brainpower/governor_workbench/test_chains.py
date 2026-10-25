"""Read-only, conditional preview of selected test chains. Never dispatches jobs."""
import hashlib
from pathlib import Path

from .evidence import fingerprint
from .execution_workspace import _read, _root, _sha
from .plans import PlanBook, _id
from .plan_tests import eligibility, adapter_hash
from .staged_tests import adapter_identity


def _observe(app,candidate_id,requested,owned=None):
    owned=owned or {}
    with app.store.db() as db:
        tables={r['name'] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not {'plan_candidates','plan_approvals','step_completions'}<=tables:
        raise ValueError('Planbelege fehlen.')
    # Read-only facade: preview must not initialize schemas in an empty journal.
    book=PlanBook.__new__(PlanBook);book.store=app.store;book.config=app.config
    candidate=book.get(candidate_id)
    context=app.scope_context(candidate['scope_kind'],candidate['scope_id'],require_egress=False,force=True)
    report=book.dependency_report(candidate_id,context)
    if not report['current'] or not report['selection_id'] or context.get('plan_ready') is not True:
        raise ValueError('Aktuelle Aufnahme, Planrevision und Auswahl erforderlich.')
    rows={r['id']:r for r in report['steps']}
    steps={s['id']:s for s in candidate['proposal']['steps']}
    if not requested<=rows.keys():raise ValueError('Unbekannter Testschritt.')
    ordered=[];remaining=set(requested)
    while remaining:
        ready=next((key for key in steps if key in remaining and not (set(steps[key]['depends_on']) & remaining)),None)
        if ready is None:raise ValueError('Testkette enthält einen Zyklus.')
        ordered.append(ready);remaining.remove(ready)
    effective=dict(candidate,scope_hash=report['scope_hash'])
    sources={};external={};attempts={};views=[];root_identity=None;root_path=None
    for key in ordered:
        row=rows[key]
        if row['action']!='test' or not row['selected'] or (row['completion_status']=='accepted' and key not in owned):
            raise ValueError('Nur ausgewählte, noch nicht aktuell abgeschlossene Tests zulässig.')
        if not row['test_attempts']['allowed'] and key not in owned:
            raise ValueError('Testversuch nicht verfügbar; aktive Aufträge oder Versuchslimit prüfen.')
        if key in owned and owned[key]['status']=='completed':
            if row['completion_status']!='accepted' or row['completion_receipt']['job_id']!=owned[key]['id']:
                raise ValueError('Eigener Testabschluss nicht aktuell belegt.')
        for dep in row['all_predecessors']:
            if dep not in requested:
                predecessor=rows[dep]
                if predecessor['completion_status']!='accepted':
                    raise ValueError('Externer Vorgänger besitzt keinen aktuellen Abschlussbeleg.')
                receipt=predecessor['completion_receipt']
                external[dep]=dict(id=receipt['id'],hash=fingerprint(receipt))
        step,root=eligibility(app.config,context,effective,key)
        _,identity=_root(root)
        if root_identity is not None and (identity!=root_identity or str(root)!=root_path):
            raise ValueError('Uneinheitliche Pilotwurzel.')
        root_identity=identity;root_path=str(root)
        for path in step['scope']:
            if path not in sources:
                raw=_read(root,path)
                if raw is None:raise ValueError('Explizite Testquelle fehlt.')
                sources[path]=_sha(raw)
        policy=row['test_attempts'];history=policy['history']
        attempts[key]=dict(used=policy['used'],remaining=policy['remaining'],limit=policy['limit'],
            latest=dict(id=history[0]['id'],status=history[0]['status']) if history else None)
        conditional=[dep for dep in ordered if dep in row['all_predecessors'] and dep in requested]
        views.append(dict(id=key,title=step['title'],readiness='conditional' if conditional else 'ready',
            waiting_for=conditional,execution_authorized=False))
    files=('test_chains.py','test_chain_store.py','plans.py','plan_tests.py','execution_policy.py','change_chain.py')
    binding=dict(profile_id='plan_test_chain_v1',candidate_id=candidate_id,proposal_hash=candidate['proposal_hash'],
        selection_id=report['selection_id'],scope_hash=report['scope_hash'],
        transition_id=(report['source_transition'] or {}).get('id'),step_ids=ordered,
        step_hashes={key:fingerprint(steps[key]) for key in ordered},
        root=root_path,root_identity=root_identity,sources=sources,external_receipts=external,attempts=attempts,
        pilot_roots=sorted(app.config['staging_pilot_roots']),test_adapter=adapter_identity(),plan_test_adapter=adapter_hash(),
        profile_files={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in files})
    return binding,views


def preview(app,candidate_id,step_ids):
    report=dict(eligible=False,profile_id='plan_test_chain_v1',binding=None,binding_hash=None,steps=[],
        execution_authorized=False,model_transmission_required=False,creates_jobs_or_receipts=False)
    try:
        _id(candidate_id)
        if not isinstance(step_ids,list) or not 2<=len(step_ids)<=5:
            raise ValueError('Zwei bis fünf Testschritte erforderlich.')
        for key in step_ids:_id(key)
        if len(set(step_ids))!=len(step_ids):raise ValueError('Doppelte Testschritte.')
        first,views=_observe(app,candidate_id,set(step_ids))
        second,_=_observe(app,candidate_id,set(step_ids))
        if fingerprint(first)!=fingerprint(second):raise ValueError('Stand während der Vorschau geändert.')
        report.update(eligible=True,binding=first,binding_hash=fingerprint(first),steps=views,
            reason='Testkette vorschlagbar; spätere Schritte benötigen noch erfolgreiche Vorgänger. Start nicht implementiert.')
    except (ValueError,KeyError,TypeError,OSError):
        report['reason']='Testkette gesperrt: Auswahl, Vorgängerbelege, Pilotquellen oder Versuchslage fehlen oder haben sich geändert.'
    return report


def start(app,values):
    from .test_chain_store import TestChainJournal
    if not isinstance(values,dict) or set(values)!={'candidate_id','step_ids','binding_hash','note'}:
        raise ValueError('Kandidat, Testschritte, Vorschauhash und Begründung erforderlich.')
    if not isinstance(values['step_ids'],list):raise ValueError('Testliste erforderlich.')
    journal=TestChainJournal(app.store)
    # An exact historical consent retry is read-only, including after completion.
    with app.store.db() as db:
        historical=db.execute("SELECT id FROM test_chain_runs WHERE binding_hash=? AND json_extract(binding,'$.candidate_id')=? LIMIT 1",
                              (values['binding_hash'],values['candidate_id'])).fetchone()
    if historical:
        row=journal.get(historical['id'])
        if sorted(values['step_ids'])!=sorted(row['binding']['step_ids']):raise ValueError('Testliste verändert.')
        return journal.start(row['binding'],values['binding_hash'],values['note']),False
    report=preview(app,values['candidate_id'],values['step_ids'])
    if not report['eligible'] or report['binding_hash']!=values['binding_hash']:raise ValueError('Vorschau veraltet oder gesperrt.')
    return journal.start(report['binding'],values['binding_hash'],values['note']),True


def validate(app,row):
    import copy
    if row['status'] not in ('testing','checking') or row['cancel_requested']:raise ValueError('Kette nicht aktiv.')
    expected=copy.deepcopy(row['binding']);owned={}
    for child in row['children']:
        job=app.store.job(child['job_id']);step=child['step_id']
        request=dict(candidate_id=expected['candidate_id'],step_id=step,scope_hash=expected['scope_hash'],selection_id=expected['selection_id'])
        if (job['action']!='plan_test' or job['request']!=request or job['status'] not in ('queued','running','completed')
                or child['ordinal']>=len(expected['step_ids']) or expected['step_ids'][child['ordinal']]!=step):
            raise ValueError('Kindbindung verändert.')
        owned[step]=job
        prior=expected['attempts'][step]
        prior.update(used=prior['used']+1,remaining=prior['remaining']-1,latest=dict(id=job['id'],status=job['status']))
        if prior['remaining']<0:raise ValueError('Versuchslimit überschritten.')
    for _ in range(2):
        observed,_=_observe(app,expected['candidate_id'],set(expected['step_ids']),owned)
        if fingerprint(observed)!=fingerprint(expected):raise ValueError('Kettenbindung verändert.')
