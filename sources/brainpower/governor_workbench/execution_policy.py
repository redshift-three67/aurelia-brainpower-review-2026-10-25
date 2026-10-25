"""Fail-closed eligibility for an explicitly configured isolated staging pilot.

This check grants neither product execution nor apply-back permission. Dependent
change steps, grouped projects and historical products remain unavailable.
The standalone test caller must additionally validate predecessor receipts.
"""
import copy
import os

from .execution_workspace import _root
from .plans import _context, _id, _proposal
from .registry import INITIAL_ROLES


def require_staging_pilot(config, context, candidate, step_id, permission, *, test_step=False):
    if not isinstance(permission, dict) or permission.get('plan_selection_approved') is not True:
        raise ValueError('Aktuelle ausdrückliche Planauswahl ist erforderlich.')
    kind, key, source_hash, projects = _context(context)
    if kind != 'project':
        raise ValueError('Staging ist zunächst nur für ein isoliertes Single-Pilotprojekt verfügbar.')
    if (not isinstance(candidate, dict)
            or (candidate.get('scope_kind'), candidate.get('scope_id'), candidate.get('scope_hash')) != (kind, key, source_hash)):
        raise ValueError('Plankandidat und aktueller Quellenkontext stimmen nicht überein.')
    proposal = _proposal(candidate.get('proposal'), projects)
    _id(step_id)
    step = next((row for row in proposal['steps'] if row['id'] == step_id), None)
    if step is None or step['action'] != ('test' if test_step else 'change'):
        raise ValueError('Ein ausdrücklich ausgewählter passender Test-/Änderungsschritt ist erforderlich.')
    if step['depends_on'] and not test_step:
        raise ValueError('Schritte mit Abhängigkeiten benötigen einen noch nicht verfügbaren Fortschrittsnachweis.')
    project = context['registry_projects'][0]
    if test_step and project.get('archived') is not False:
        raise ValueError('Test benötigt ein aktives registriertes Pilotprojekt.')
    if (project['id'] in INITIAL_ROLES or 'group_id' not in project or project['group_id'] is not None):
        raise ValueError('Gruppen und die fünf bestehenden Produkte sind keine isolierten Staging-Piloten.')
    roots = config.get('staging_pilot_roots') if isinstance(config, dict) else None
    if not isinstance(roots, list) or not 1 <= len(roots) <= 5:
        raise ValueError('Staging ist ohne explizite begrenzte staging_pilot_roots-Liste gesperrt.')
    project_root, _ = _root(project.get('path'))
    allowed = set()
    for value in roots:
        if not isinstance(value, str):
            raise ValueError('Pilotwurzeln müssen explizite absolute Pfade sein.')
        root, _ = _root(value)
        allowed.add(os.path.normcase(str(root)))
    if os.path.normcase(str(project_root)) not in allowed:
        raise ValueError('Projektwurzel ist nicht ausdrücklich als isolierter Staging-Pilot freigegeben.')
    return copy.deepcopy(step)


def pilot_model_context(context,candidate,step,phase):
    """Controller request after require_staging_pilot; never sourced from memories."""
    if phase not in ('patch_preflight','post_test_review'):
        raise ValueError('Unbekannte Pilotphase.')
    result=copy.deepcopy(context)
    result['current_request']=dict(authorized=True,scope='isolated_staging_pilot',phase=phase,
        project_id=step['project_id'],candidate_id=candidate['id'],step_id=step['id'],
        source_scope_hash=context['scope_hash'],allowed_paths=list(step['scope']),
        plan_selection_verified=True,pilot_allowlist_verified=True,
        staging_copy_authorized=True,restricted_staged_unittest_authorized=True,
        original_file_changes_authorized=False,product_implementation_authorized=False,
        apply_back_authorized=False,automatic_sequence_authorized=False,
        historical_pause_superseded_for_this_review=True)
    return result
