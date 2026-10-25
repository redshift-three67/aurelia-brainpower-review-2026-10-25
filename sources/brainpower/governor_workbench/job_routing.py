"""Server-owned routing snapshots and fresh per-call decisions."""
import hashlib
from pathlib import Path
from .routing_policy import VERSION, ROUTE_B_EFFORTS, choose, validate_mode, routine_step
from .llm import ModelError


def snapshot(app, supervisor):
    settings = app.settings()
    return dict(version=VERSION, mode=validate_mode(settings.get('reasoning_mode', 'medium')),
                supervisor=supervisor, selected_supervisor=settings.get('supervisor'),
                transport=app.config.get('orchestrator_transport', 'hermes'),
                router=app.config.get('router_url'), timeout=app.config.get('model_timeout'),
                policy_sha256=hashlib.sha256(Path(__file__).with_name('routing_policy.py').read_bytes()).hexdigest())


def routine_origin(app, candidate):
    try:
        origin = app.store.job(candidate['job_id'])
        return (origin['action'] == 'scope_plan' and origin['status'] == 'completed'
                and not any(key.startswith('repair_') for key in origin.get('request', {}))
                and not (origin.get('result') or {}).get('repair_binding')
                and not app.questions.answers(candidate['job_id']))
    except (KeyError, TypeError, ValueError):
        return False


class JobRouting:
    def __init__(self, app, job, supervisor, binding=None):
        self.app, self.job, self.supervisor = app, job, supervisor
        self.binding = binding or job.get('request', {}).get('_model_routing')
        self.legacy = self.binding is None
        if self.legacy: self.binding = snapshot(app, supervisor)
        self.routine = False

    def enable_routine(self, step):
        req = self.job['request']
        if (self.job['action'] == 'scope_patch' and req.get('scope_kind') == 'project'
                and not req.get('successor_consent_id') and not req.get('repair_binding')
                and not self.app.questions.answers(self.job['id'])
                and routine_step(step, req.get('routine_note'))):
            self.routine = True

    def __call__(self, model):
        if self.binding != snapshot(self.app, self.supervisor):
            raise ModelError('Modellrouting seit Auftrag/Vorschau geändert; neuer ausdrücklicher Auftrag erforderlich.')
        routine = self.routine
        if routine:
            from .change_execution import resolve
            req = self.job['request']
            context = self.app.scope_context(req['scope_kind'], req['scope_id'], require_egress=True, force=True)
            if context['scope_hash'] != req['scope_hash']:
                raise ModelError('Routinegrundlage seit Auftrag geändert.')
            candidate, step, _ = resolve(self.app, req, context)
            routine = (not self.app.questions.answers(self.job['id'])
                       and routine_origin(self.app, candidate)
                       and routine_step(step, req.get('routine_note')))
        decision = choose('medium' if self.legacy else self.binding['mode'], model, routine=routine)
        if self.legacy: decision['reason'] = 'Altauftrag ohne gespeicherte Auswahl bleibt Medium'
        return decision


ROUTE_B_VERSION = 'route-b-v2'


def route_b_snapshot(app, supervisor):
    return dict(snapshot(app, supervisor), variant=ROUTE_B_VERSION,
                route_sha256=hashlib.sha256(Path(__file__).with_name('route_b.py').read_bytes()).hexdigest())


class RouteBRouting:
    """Bound exactly three role/effort pairs without changing legacy RH-1 jobs."""
    def __init__(self, app, job, supervisor):
        self.app, self.supervisor = app, supervisor
        self.binding = job.get('request', {}).get('_model_routing')
        if not isinstance(self.binding, dict) or self.binding.get('variant') != ROUTE_B_VERSION:
            raise ModelError('Gebundene Route B fehlt; neuer ausdrücklicher Auftrag erforderlich.')

    def __call__(self, model):
        if self.binding != route_b_snapshot(self.app, self.supervisor):
            raise ModelError('Route B seit Auftrag geändert; neuer ausdrücklicher Auftrag erforderlich.')
        if model not in ROUTE_B_EFFORTS:
            raise ModelError('Modell gehört nicht zur gebundenen Route B.')
        roles = {'gpt-6-sol': 'orchestrator', 'gpt-6-luna': 'worker_review',
                 'gpt-6-astra': 'critical_independent_review'}
        return dict(requested=ROUTE_B_VERSION, effective=ROUTE_B_EFFORTS[model],
                    role=roles[model], reason='Ausdrücklich gewählte Route B; feste Rollenbindung',
                    version=ROUTE_B_VERSION)
