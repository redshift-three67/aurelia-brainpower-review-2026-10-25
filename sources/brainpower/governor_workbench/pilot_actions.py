"""Local policy checks for explicit bounded pilot apply/rollback job calls.

The HTTP/job caller owns operator authentication and explicit approval. These
functions never call models or turn plan selection into general product approval.
Cancellation is checked before the write operation, never between its files.
"""
import json
import os
from pathlib import Path

from .execution_policy import require_staging_pilot
from .execution_workspace import WorkspaceStager, _root, _sha
from .jobs import JobCancelled
from .pilot_apply import PilotApply
from .plans import PlanBook
from .registry import INITIAL_ROLES


def _pilot(app):
    return PilotApply(app.store,WorkspaceStager(app.config['data_dir']),
                      allowed_roots=app.config.get('staging_pilot_roots',[]))


def _cancel(event):
    if event is not None and event.is_set():
        raise JobCancelled('Pilotaktion vor Dateischreibvorgang abgebrochen.')


def _source(app, test_id):
    test=app.store.job(test_id)
    result=test.get('result') or {}
    parent_id=test['request'].get('stage_job_id')
    if test['action']!='stage_test' or test['status']!='completed' or not parent_id:
        raise ValueError('Abgeschlossener Staging-Test erforderlich.')
    app.store.require_latest_stage_test(test['id'],parent_id)
    if any(result.get(k) is not True for k in ('success','verified','completion_verified','sources_verified')) or result.get('stale'):
        raise ValueError('Test und Quellen sind nicht frisch verifiziert.')
    from .staged_tests import require_current_adapter
    require_current_adapter(result)
    if (type(result.get('exit_code')) is not int or result['exit_code']!=0
            or type(result.get('count')) is not int or not 0<result['count']<=1000000
            or type(result.get('skipped')) is not int or not 0<=result['skipped']<result['count']
            or any(type(result.get(k)) is not int or result[k]!=0 for k in ('errors','failures'))):
        raise ValueError('Tatsächlicher Testbericht ist nicht erfolgreich.')
    post=result.get('post_test_review') or {}; review=post.get('review') or {}
    if (post.get('verified') is not True or review.get('decision')!='REVIEW_ONLY'
            or review.get('findings')!=[] or review.get('required_evidence')!=[]):
        raise ValueError('Unabhängige Nachprüfung hat offene Befunde.')
    source=app.store.job(parent_id)
    from .change_execution import require_latest_source
    require_latest_source(app,source['request'],source['id'])
    stage=(source.get('result') or {}).get('stage') or {}
    if (source['action']!='scope_patch' or source['status']!='completed'
            or result.get('stage_job_id')!=source['id'] or result.get('stage_id')!=stage.get('id')
            or result.get('manifest_hash')!=stage.get('manifest_hash')):
        raise ValueError('Testreferenzen passen nicht zum Änderungsvorschlag.')
    return source,test


def _registry_identity(app, source, manifest):
    request=source['request']
    project_id=request.get('scope_id')
    projects=app.registry.list_projects()
    project=next((p for p in projects if p['id']==project_id),None)
    if (request.get('scope_kind')!='project' or project is None or project_id in INITIAL_ROLES
            or project.get('archived') is not False or 'group_id' not in project or project['group_id'] is not None):
        raise ValueError('Nur ein aktiver isolierter Pilot darf verändert oder zurückgenommen werden.')
    root,identity=_root(project.get('path'))
    original,original_identity=_root(manifest['original_root'])
    if os.path.normcase(str(root))!=os.path.normcase(str(original)) or identity!=manifest['root_identity'] or identity!=original_identity:
        raise ValueError('Registriertes Projekt entspricht nicht der versiegelten Originalwurzel.')
    roots=app.config.get('staging_pilot_roots')
    if not isinstance(roots,list) or not 1<=len(roots)<=5 or any(not isinstance(p,str) for p in roots):
        raise ValueError('Explizite begrenzte Pilotwurzelliste erforderlich.')
    if os.path.normcase(str(root)) not in {os.path.normcase(str(_root(p)[0])) for p in roots}:
        raise ValueError('Pilotwurzelfreigabe fehlt oder wurde zurückgenommen.')
    # Defense against configuring a new ID at/inside/above a historical root.
    for historical in projects+list(app.config.get('projects',[])):
        if historical.get('id') not in INITIAL_ROLES: continue
        value=historical.get('path')
        if not isinstance(value,str) or not Path(value).is_absolute():
            raise ValueError('Historische Projektwurzel kann nicht sicher ausgeschlossen werden.')
        excluded=Path(value).resolve()
        if root==excluded or root.is_relative_to(excluded) or excluded.is_relative_to(root):
            raise ValueError('Historische Produktwurzel ist vom Pilot ausgeschlossen.')
    return project


def _fresh(app, source, test):
    request=source['request']; stage=source['result']['stage']
    project=_registry_identity(app,source,stage['manifest'])
    context=app.scope_context(request['scope_kind'],request['scope_id'],require_egress=False,force=True)
    if (context['scope_hash']!=source['result'].get('scope_hash')
            or context['scope_hash']!=request.get('scope_hash') or context['scope_hash']!=test['result'].get('scope_hash')):
        raise ValueError('Quellenstand seit dem getesteten Vorschlag verändert.')
    from .change_execution import resolve
    candidate,step,permission=resolve(app,request,context)
    if (not permission.get('plan_selection_id')
            or test['result'].get('plan_selection_id') != permission['plan_selection_id']):
        raise ValueError('Planauswahl seit Test geändert oder unbelegt. Staging-Test erneut ausführen.')
    if 'successor_binding' in permission and test['result'].get('successor_binding')!=permission['successor_binding']:
        raise ValueError('Eigener Test ist nicht an die aktuelle Nachfolgerzustimmung gebunden.')
    if step['project_id']!=project['id'] or set(step['scope'])!={f['path'] for f in stage['manifest']['files']}:
        raise ValueError('Getesteter Dateiumfang stimmt nicht mit der Planauswahl überein.')
    return context


def _proposal(app, proposal_id, expected_hash=None):
    value=_pilot(app).get(proposal_id)
    fields={k:v for k,v in value.items() if k!='proposal_hash'}
    actual=_sha(json.dumps(fields,sort_keys=True,ensure_ascii=False).encode('utf-8'))
    if actual!=value.get('proposal_hash') or (expected_hash is not None and actual!=expected_hash):
        raise ValueError('Angezeigter Apply-Vorschlag stimmt nicht mit dem Journal überein.')
    return value


def assess(app, verified_test_job_id):
    """Point-in-time diagnostic only; does not create an apply proposal."""
    from .evidence import now
    checks=[dict(id=key,label=label,status='not_checked',reason='') for key,label in (
        ('test','Test, Adapterstand und neuester Versuch'),
        ('selection','Quellenkontext, Planauswahl und Pilotfreigabe'),
        ('files','Versiegelte Dateien und unveränderter Originalstand'))]
    with app.store.lock:
        index=0
        try:
            source,test=_source(app,verified_test_job_id)
            checks[index]['status']='passed'; index=1
            _fresh(app,source,test)
            checks[index]['status']='passed'; index=2
            stage=source['result']['stage']
            stager=WorkspaceStager(app.config['data_dir'])
            stager.verify_source(stage['id'],stage['manifest_hash'])
            from .execution_workspace import _read, MAX_MANIFEST_BYTES
            manifest=json.loads(_read(stager.base/stage['id'],'manifest.json',MAX_MANIFEST_BYTES))
            if manifest != stage['manifest']:
                raise ValueError('Journal und versiegeltes Manifest unterscheiden sich.')
            checks[index]['status']='passed'
        except ValueError as error:
            checks[index].update(status='blocked',reason=str(error))
        except OSError:
            checks[index].update(status='blocked',reason='Dateiprüfung nicht möglich; Nachweis bleibt gesperrt.')
    return dict(verified_test_job_id=verified_test_job_id,checked_at=now(),checks=checks,
                evidence_usable=all(c['status']=='passed' for c in checks),approval_granted=False,
                product_files_changed=False,automatic_sequence=False)


def prepare(app, verified_test_job_id):
    with app.store.lock:
        source,test=_source(app,verified_test_job_id)
        context=_fresh(app,source,test); stage=source['result']['stage']
        return _pilot(app).prepare(stage['id'],stage['manifest_hash'],test['id'],context['scope_hash'])


def execute(app, proposal_id, proposal_hash, cancel_event):
    _cancel(cancel_event)
    with app.store.lock:
        proposal=_proposal(app,proposal_id,proposal_hash)
        source,test=_source(app,proposal['verified_test_job_id'])
        stage=source['result']['stage']
        if (source['id']!=proposal['stage_job_id'] or stage['id']!=proposal['stage_id']
                or stage['manifest_hash']!=proposal['manifest_hash'] or stage['manifest']!=proposal['manifest']):
            raise ValueError('Apply-Vorschlag ist nicht an diesen Test gebunden.')
        context=_fresh(app,source,test)
        _cancel(cancel_event)
        return _pilot(app).apply(proposal_id,proposal['manifest_hash'],context['scope_hash'])


def rollback(app, transaction_id, cancel_event):
    _cancel(cancel_event)
    with app.store.lock:
        pilot=_pilot(app); tx=pilot.transaction(transaction_id)
        proposal=_proposal(app,tx['proposal_id'])
        source=app.store.job(proposal['stage_job_id'])
        if (tx['stage_id']!=proposal['stage_id'] or tx['manifest_hash']!=proposal['manifest_hash']
                or tx['original_root']!=proposal['manifest']['original_root']
                or tx['root_identity']!=proposal['manifest']['root_identity']):
            raise ValueError('Rollback-Journal passt nicht zum ursprünglichen Vorschlag.')
        _registry_identity(app,source,proposal['manifest'])
        _cancel(cancel_event)
        return pilot.rollback(transaction_id)


def transaction_snapshot(app, limit=40):
    """Read at most limit receipts, unresolved first, then newest journal rows.

This read does not initialize tables or change interrupted/running state. Before
the first pilot action the table may not exist. Independent of jobs pagination.
"""
    if type(limit) is not int or not 1<=limit<=100:
        raise ValueError('Transaktionsansicht benötigt ein Limit von 1 bis 100.')
    with app.store.db() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='pilot_apply_transactions'").fetchone():
            return []
        rows=db.execute('''SELECT body FROM pilot_apply_transactions
            ORDER BY CASE WHEN status IN ('running','interrupted','recovery_needed','rolling_back')
                THEN 0 ELSE 1 END, rowid DESC LIMIT ?''',(limit,)).fetchall()
        return [json.loads(row['body']) for row in rows]


def recovery_receipt(app, job):
    """Attach journal evidence to a failed attempt; never claim byte freshness.

Returns None if the request cannot identify an existing transaction. The caller
must retain its original failure/error, and should guard receipt lookup failure
so a journal I/O failure does not replace the original exception.
"""
    action=job.get('action'); request=job.get('request') or {}
    if action not in ('pilot_apply','pilot_rollback'):
        return None
    with app.store.db() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='pilot_apply_transactions'").fetchone():
            return None
        if action=='pilot_rollback':
            key=request.get('transaction_id')
            if not isinstance(key,str): return None
            row=db.execute('SELECT body FROM pilot_apply_transactions WHERE id=?',(key,)).fetchone()
        else:
            key=request.get('proposal_id')
            if not isinstance(key,str): return None
            proposal=db.execute('SELECT body FROM pilot_apply_proposals WHERE id=?',(key,)).fetchone()
            if proposal is None: return None
            stage_id=json.loads(proposal['body']).get('stage_id')
            if not isinstance(stage_id,str): return None
            row=db.execute('SELECT body FROM pilot_apply_transactions WHERE stage_id=?',(stage_id,)).fetchone()
        if row is None: return None
        tx=json.loads(row['body'])
    return dict(success=False,pilot_transaction=tx,product_files_changed=None,
                file_state='unknown_requires_inspection',approval_granted=False,
                summary='Pilotaktion fehlgeschlagen; dauerhaftes Transaktionsjournal und aktuellen Dateizustand prüfen.')
