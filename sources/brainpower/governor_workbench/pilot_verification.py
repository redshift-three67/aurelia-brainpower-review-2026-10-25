"""Explicit post-apply observations, never plan acceptance or target test execution."""
import json

from .evidence import now, fingerprint
from .execution_workspace import WorkspaceStager, _read, MAX_MANIFEST_BYTES
from . import pilot_actions


def verify(app, transaction_id, cancel=None):
    checks=[dict(id=key,label=label,status='not_checked',reason='') for key,label in (
        ('transaction','Abgeschlossene Übernahme und gebundener Vorschlag'),
        ('test','Bisheriger Staging-Test, Adapter und neuester Versuch'),
        ('selection','Pilotfreigabe, Planauswahl und aktueller Kontext'),
        ('files','Übernommene Dateien und versiegeltes Staging'))]
    report=dict(transaction_id=transaction_id,checks=checks,evidence_usable=False,
                applied_files_verified=False,context_matches_plan=False,
                step_completion_granted=False,approval_granted=False,
                target_tests_executed=False,product_files_changed=False,
                automatic_sequence=False,observed_scope_hash=None)
    pilot_actions._cancel(cancel)
    with app.store.lock:
        index=0
        try:
            pilot=pilot_actions._pilot(app)
            tx=pilot.transaction(transaction_id)
            proposal=pilot_actions._proposal(app,tx['proposal_id'])
            manifest=proposal['manifest']
            if (tx['status']!='completed'
                    or any(tx[key]!=proposal[key] for key in ('stage_id','manifest_hash','scope_hash'))
                    or any(tx[key]!=manifest[key] for key in ('original_root','root_identity'))):
                raise ValueError('Keine abgeschlossene, passend gebundene Übernahme.')
            expected={f['path']:(f['original_sha256'],f['staged_sha256']) for f in manifest['files']
                      if f['original_sha256']!=f['staged_sha256']}
            if (len(tx['files'])!=len(expected) or
                    {f['path']:(f['before'],f['after']) for f in tx['files']}!=expected or
                    any(f['written'] is not True or f['intent'] is not True for f in tx['files'])):
                raise ValueError('Transaktionsdateien passen nicht zum Übernahmemanifest.')
            checks[index]['status']='passed'; index=1
            source,test=pilot_actions._source(app,proposal['verified_test_job_id'])
            stage=source['result']['stage']
            if (source['id']!=proposal['stage_job_id'] or stage['id']!=tx['stage_id']
                    or stage['manifest_hash']!=tx['manifest_hash'] or stage['manifest']!=manifest
                    or source['request']['scope_hash']!=proposal['scope_hash']
                    or source['result']['scope_hash']!=proposal['scope_hash']
                    or test['result']['scope_hash']!=proposal['scope_hash']):
                raise ValueError('Übernahme und Test verweisen nicht auf denselben Vorschlag.')
            report.update(verified_test_job_id=test['id'],stage_job_id=source['id'],
                          stage_id=stage['id'],manifest_hash=stage['manifest_hash'],
                          plan_scope_hash=proposal['scope_hash'],
                          test_adapter_hash=fingerprint(test['result']['adapter_after']))
            checks[index]['status']='passed'; index=2
            pilot_actions._registry_identity(app,source,manifest)
            request=source['request']
            # Do not synthesize a current context using the old source hash.
            with app.store.db() as db:
                candidate=db.execute('SELECT body FROM plan_candidates WHERE id=?',(request['candidate_id'],)).fetchone()
                if candidate is None: raise ValueError('Plan fehlt.')
                candidate=json.loads(candidate['body'])
                latest=db.execute('SELECT id FROM plan_candidates WHERE scope_kind=? AND scope_id=? ORDER BY version DESC LIMIT 1',
                                  (request['scope_kind'],request['scope_id'])).fetchone()
                row=db.execute('SELECT body FROM plan_approvals WHERE candidate_id=? ORDER BY rowid DESC LIMIT 1',
                               (candidate['id'],)).fetchone()
                selection=json.loads(row['body']) if row else {}
                step=next((s for s in candidate['proposal']['steps'] if s['id']==request['step_id']),None)
                dependent='successor_consent_id' in request
                if (not latest or latest['id']!=candidate['id']
                        or selection.get('id')!=test['result'].get('plan_selection_id')
                        or not selection.get('id') or request['step_id'] not in selection.get('selected_step_ids',[])
                        or selection.get('proposal_hash')!=candidate['proposal_hash']
                        or selection.get('scope_hash')!=candidate['scope_hash']
                        or (not dependent and candidate['scope_hash']!=proposal['scope_hash'])
                        or not step or step['action']!='change' or (step['depends_on'] and not dependent)
                        or step['project_id']!=request['scope_id']
                        or set(step['scope'])!={f['path'] for f in manifest['files']}):
                    raise ValueError('Planauswahl oder begrenzter Änderungsschritt nicht mehr passend.')
                newer=db.execute("SELECT id FROM jobs WHERE action='scope_patch' AND json_extract(request,'$.candidate_id')=? AND json_extract(request,'$.step_id')=? ORDER BY rowid DESC LIMIT 1",
                                 (candidate['id'],step['id'])).fetchone()
                if not newer or newer['id']!=source['id']:
                    raise ValueError('Neuerer Änderungsvorschlag benötigt eigene Nachweise.')
            context=app.scope_context(request['scope_kind'],request['scope_id'],require_egress=False,force=True)
            if dependent:
                from .change_execution import applied
                report.update(applied(app,request,context,tx,manifest,test))
            scope=context.get('scope_hash')
            import re
            if not isinstance(scope,str) or re.fullmatch('[a-f0-9]{64}',scope) is None:
                raise ValueError('Aktueller Quellenhash fehlt.')
            report.update(candidate_id=candidate['id'],step_id=step['id'],step_hash=fingerprint(step),selection_id=selection['id'],
                          observed_scope_hash=scope,context_matches_plan=scope==proposal['scope_hash'])
            checks[index]['status']='passed'; index=3
            pilot_actions._cancel(cancel)
            stager=WorkspaceStager(app.config['data_dir'])
            stager.verify_applied(stage['id'],stage['manifest_hash'])
            sealed=json.loads(_read(stager.base/stage['id'],'manifest.json',MAX_MANIFEST_BYTES))
            if sealed!=manifest: raise ValueError('Journal und versiegeltes Manifest unterscheiden sich.')
            report['applied_files_verified']=True
            checks[index]['status']='passed'
        except (ValueError,KeyError,TypeError,OSError) as error:
            checks[index].update(status='blocked',reason=str(error) if isinstance(error,ValueError)
                                 else 'Nachweis unvollständig oder Datei nicht lesbar; Prüfung gesperrt.')
    pilot_actions._cancel(cancel)
    report.update(checked_at=now(),evidence_usable=all(c['status']=='passed' for c in checks))
    from .technical_completion import snapshot, adapter_hash
    report['completion_adapter_hash']=adapter_hash()
    report['technical_completion']=snapshot(app.store,transaction_id,report)
    return report
