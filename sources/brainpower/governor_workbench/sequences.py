"""Fresh consent binding for the fixed pilot sequence; no target writes."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from .config import SUPERVISORS
from .evidence import fingerprint
from .execution_policy import require_staging_pilot
from .execution_workspace import WorkspaceStager, _read, MAX_MANIFEST_BYTES
from .pilot_actions import _registry_identity
from .plans import PlanBook


PROFILE_ID = 'pilot_test_assess_v1'


def preview(app, stage_job_id):
    report = dict(eligible=False, profile_id=PROFILE_ID, binding=None, binding_hash=None,
                  actions=['stage_test', 'pilot_assess'],
                  stop_before=['pilot_prepare', 'pilot_apply'],
                  model_transmission_required=True, execution_authorized=False)
    phase = 'source'
    reasons = {
        'source': 'Abgeschlossener Änderungsvorschlag mit gültigen Staging-Referenzen erforderlich.',
        'context': 'Aktuelle Aufnahme, Quellen und Versandfreigaben konnten nicht bestätigt werden.',
        'selection': 'Aktuelle Auswahl eines unabhängigen erlaubten Pilot-Änderungsschritts erforderlich.',
        'files': 'Versiegelter Dateiumfang oder registrierte Originalwurzel ist nicht mehr gültig.',
        'routing': 'Das konfigurierte Modellrouting muss unverändert unterstützt sein.',
        'adapter': 'Profil- oder Testadapteridentität konnte nicht vollständig gelesen werden.',
    }
    try:
        if not isinstance(stage_job_id, str) or not re.fullmatch('[a-f0-9]{32}', stage_job_id):
            raise ValueError('Invalid job reference')
        source = app.store.job(stage_job_id)
        if source['action'] != 'scope_patch' or source['status'] != 'completed':
            raise ValueError('Not a completed patch')
        result = source.get('result') or {}
        stage = result['stage']; req = source['request']
        if not isinstance(stage, dict) or result.get('stale') or result.get('success') is False:
            raise ValueError('Invalid stage result')
        phase = 'context'
        context = app.scope_context(req['scope_kind'], req['scope_id'], require_egress=True, force=True)
        if (context.get('plan_ready') is not True or context['scope_hash'] != req['scope_hash']
                or context['scope_hash'] != result['scope_hash']):
            raise ValueError('Scope changed')
        phase = 'selection'
        book = PlanBook(app.store)
        candidate = book.get(req['candidate_id'])
        permission = book.execution_permission(candidate['id'], req['step_id'], context)
        step = require_staging_pilot(app.config, context, candidate, req['step_id'], permission)
        selection_id = permission['plan_selection_id']
        if not selection_id:
            raise ValueError('No current selection')
        phase = 'files'
        stager = WorkspaceStager(app.config['data_dir'])
        stager.verify_source(stage['id'], stage['manifest_hash'])
        manifest = json.loads(_read(stager.base / stage['id'], 'manifest.json', MAX_MANIFEST_BYTES))
        if (fingerprint(manifest) != fingerprint(stage['manifest'])
                or sorted(row['path'] for row in manifest['files']) != sorted(step['scope'])):
            raise ValueError('Manifest binding differs')
        _registry_identity(app, source, manifest)
        phase = 'routing'
        supervisor = app.settings()['supervisor']
        transport = app.config['orchestrator_transport']
        if supervisor not in SUPERVISORS or transport not in ('hermes', 'router') or app.config['reasoning'] != 'medium':
            raise ValueError('Unsupported routing')
        url = urlsplit(app.config['router_url'])
        if (url.scheme != 'http' or url.hostname not in ('localhost', '127.0.0.1')
                or url.username or url.password or url.query or url.fragment):
            raise ValueError('Unsupported router')
        from .job_routing import snapshot
        model_policy = snapshot(app, supervisor)
        from .routing_policy import choose
        routing = dict(supervisor=supervisor, reasoning=choose(model_policy['mode'],supervisor)['effective'], model_policy=model_policy, orchestrator_transport=transport,
                       post_review_transport='router', router_host=url.hostname,
                       router_port=url.port or 80, router_path=url.path,
                       model_timeout=app.config['model_timeout'])
        phase = 'adapter'
        from .staged_tests import adapter_identity
        adapter = adapter_identity()
        names = ('sequences.py', 'execution_policy.py', 'plans.py', 'pilot_actions.py',
                 'post_test_review.py', 'config.py', 'scopes.py', 'registry.py', 'vault.py',
                 'sequence_store.py', 'store.py', 'operator_questions.py', 'server.py', 'llm.py', 'model_usage.py', 'job_routing.py', 'routing_policy.py','evidence.py','git_status.py')
        profile_files = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                         for name in names}
        with app.store.db() as db:
            latest = db.execute("SELECT id FROM jobs WHERE action='stage_test' "
                                "AND json_extract(request,'$.stage_job_id')=? ORDER BY rowid DESC LIMIT 1",
                                (stage_job_id,)).fetchone()
        binding = dict(profile_id=PROFILE_ID, profile_files=profile_files, stage_job_id=stage_job_id,
                       stage_id=stage['id'], manifest_hash=stage['manifest_hash'],
                       candidate_id=candidate['id'], step_id=step['id'], step_hash=fingerprint(step),
                       selection_id=selection_id, scope_hash=context['scope_hash'],
                       original_root=manifest['original_root'], root_identity=manifest['root_identity'],
                       pilot_roots=sorted(app.config['staging_pilot_roots']), egress_verified=True,
                       adapter=adapter, routing=routing, latest_stage_test_id=latest['id'] if latest else None)
        phase = 'files'
        stager.verify_source(stage['id'], stage['manifest_hash'])
        report.update(eligible=True, binding=binding, binding_hash=fingerprint(binding),
                      reason='Prüffolge vorschlagbar; ausdrücklicher gebundener Start erforderlich.')
    except (ValueError, TypeError, KeyError, OSError):
        report.update(reason=reasons[phase], blocked_at=phase)
    return report


def start(app,values):
    from .sequence_store import SequenceJournal
    if not isinstance(values,dict) or set(values)!={'stage_job_id','binding_hash','note'}:
        raise ValueError('Prüffolge benötigt Vorschlag, Vorschauhash und Begründung.')
    journal=SequenceJournal(app.store)
    existing=journal.find(stage_job_id=values['stage_job_id'])
    if existing:
        # Historical retry is read-only, never a new authorization or dispatch.
        return journal.start(existing['binding'],values['binding_hash'],values['note']),False
    report=preview(app,values['stage_job_id'])
    if not report['eligible'] or report['binding_hash']!=values['binding_hash']:
        raise ValueError('Vorschau nicht mehr aktuell oder gesperrt; erneut prüfen.')
    return journal.start(report['binding'],values['binding_hash'],values['note']),True


def validate_child(app,job):
    from .sequence_store import SequenceJournal,ACTIVE
    row=SequenceJournal(app.store).find(job_id=job['id'])
    if row is None:return None
    if row['status'] not in ACTIVE or row['cancel_requested'] or row['current_job_id']!=job['id']:
        raise ValueError('Prüffolge ist beendet oder Abbruch angefordert.')
    expected=dict(row['binding']);expected['latest_stage_test_id']=row['children'][0]['job_id']
    first=row['status']=='testing'
    request={'stage_job_id':row['stage_job_id']} if first else {'verified_test_job_id':expected['latest_stage_test_id']}
    if job['action']!=('stage_test' if first else 'pilot_assess') or job['request']!=request:
        raise ValueError('Kindauftrag passt nicht zur gebundenen Prüffolge.')
    current=preview(app,row['stage_job_id'])
    if not current['eligible'] or fingerprint(current['binding'])!=fingerprint(expected):
        raise ValueError('Prüffolgenbindung geändert; kein weiterer Versand oder Folgeschritt.')
    return row


class GuardedClient:
    """Revalidate immediately before each actual external call, including retries."""
    def __init__(self,client,app,job):self.client=client;self.app=app;self.job=job
    def prompt_limit(self,model):return self.client.prompt_limit(model)
    def call(self,model,prompt,**kwargs):
        row=validate_child(self.app,self.job)
        if row and model!=row['binding']['routing']['supervisor']:
            raise ValueError('Modell weicht von der bestätigten Prüffolge ab.')
        return self.client.call(model,prompt,**kwargs)
