"""Read-only, dated failure observations. Never repair instructions or authority."""
import hashlib
import json
from pathlib import Path

from .evidence import fingerprint, now
from .plans import _id
from .pilot_actions import _cancel


def source_job(app,job_id):
    _id(job_id)
    job=app.store.job(job_id)
    if (job['action']!='plan_test' or job['status'] not in ('completed','failed')
            or (job.get('result') or {}).get('success') is not False):
        raise ValueError('Abgeschlossener fehlgeschlagener eigenständiger Test erforderlich.')
    return job


def diagnose(app,job_id,cancel=None):
    from . import plan_tests
    from .execution_workspace import WorkspaceStager,_read,_root,MAX_MANIFEST_BYTES
    from .staged_tests import require_current_adapter
    _cancel(cancel)
    with app.store.lock:
        job=source_job(app,job_id);request=job['request'];evidence=job['result'].get('test_evidence') or {}
        test=evidence.get('test') or {}; output=test.get('output') or ''
        if not isinstance(output,str):output=''
        truncated=len(output)>4000
        report=dict(source_job_id=job_id,checked_at=now(),evidence_usable=False,classification='blocked',
            repair_authorized=False,models_called=False,product_files_changed=False,
            automatic_retry=False,source_evidence_hash=fingerprint(evidence),
            diagnostic_adapter_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output_excerpt=output if not truncated else output[:2000]+'\n[Auszug gekürzt; vollständige gespeicherte Ausgabe im Quellauftrag]\n'+output[-2000:],
            output_sha256=hashlib.sha256(output.encode('utf-8')).hexdigest(),output_truncated=truncated,
            output_may_already_be_truncated=True,reason='',next_steps=[])
        with app.store.db() as db:
            attempts=plan_tests.attempt_policy(db,request['candidate_id'],request['step_id'])
        report['attempts']=attempts
        try:
            if not attempts['history'] or attempts['history'][0]['id']!=job_id:
                raise ValueError('Neuerer Testversuch vorhanden; alten Fehler nicht als Reparaturgrundlage verwenden.')
            candidate,step,root,predecessors=plan_tests.preflight(app,request)
            if (evidence.get('scope_hash')!=request['scope_hash'] or evidence.get('selection_id')!=request['selection_id']
                    or evidence.get('step_hash')!=fingerprint(step) or evidence.get('predecessor_receipts')!=predecessors
                    or evidence.get('plan_test_adapter_hash')!=plan_tests.adapter_hash()):
                raise ValueError('Quellen-, Auswahl-, Vorgänger- oder Adapterbindung nicht mehr aktuell.')
            require_current_adapter(test)
            if (test.get('completion_verified') is not True or test.get('sources_verified') is not True
                    or test.get('success') is not False or type(test.get('exit_code')) is not int
                    or test['exit_code']==0
                    or any(type(test.get(k)) is not int or not 0<=test[k]<=1000000 for k in ('count','skipped','errors','failures'))
                    or test['skipped']>test['count'] or test['errors']+test['failures']==0):
                raise ValueError('Kein vollständiger Runnerbeleg für einen Testfehler; Infrastruktur oder Testabdeckung gesondert prüfen.')
            stager=WorkspaceStager(app.config['data_dir'])
            stager.verify_source(evidence['stage_id'],evidence['manifest_hash'])
            manifest=json.loads(_read(stager.base/evidence['stage_id'],'manifest.json',MAX_MANIFEST_BYTES))
            if (manifest['original_root']!=str(root) or manifest['root_identity']!=_root(root)[1]
                    or set(step['scope'])!={f['path'] for f in manifest['files']}):
                raise ValueError('Projektwurzel oder Dateiumfang stimmt nicht mehr mit dem Test überein.')
            report.update(evidence_usable=True,classification='test_failure',candidate_id=candidate['id'],step_id=step['id'],
                scope_hash=request['scope_hash'],selection_id=request['selection_id'],paths=list(step['scope']),
                counts={k:test[k] for k in ('count','skipped','errors','failures')},
                next_steps=['Fehler im Quellauftrag und betroffene Dateien fachlich prüfen; Ursache nicht automatisch bestimmt.',
                            'Für Codekorrekturen einen eigenen Änderungsplan erstellen und ausdrücklich auswählen.',
                            'Nach Korrektur neue aktuelle Testnachweise erzeugen; keine alten Folgebelege übernehmen.'])
            if not attempts['allowed']:report['next_steps'].append(attempts['reason'])
        except (ValueError,KeyError,TypeError,OSError) as error:
            report['reason']=str(error)
            report['next_steps']=['Aktuellen Quellen-/Planstand und Testnachweise klären; keine Reparatur aus diesem historischen Fehler ableiten.']
        _cancel(cancel)
        return report
