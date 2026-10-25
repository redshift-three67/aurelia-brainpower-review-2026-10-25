"""Pure RH-1 contract, also importable by the isolated Hermes script."""
from pathlib import PurePosixPath

VERSION = 'rh1-v1'
MODELS = ('gpt-5.6-terra', 'gpt-5.6-sol', 'gpt-6-astra')
ROUTE_B_EFFORTS = {'gpt-6-sol': 'high', 'gpt-6-luna': 'max', 'gpt-6-astra': 'medium'}
MODES = ('medium', 'auto', 'high', 'xhigh')
EFFORTS = ('low', 'medium', 'high', 'xhigh')


def validate_mode(mode):
    if not isinstance(mode, str) or mode not in MODES:
        raise ValueError('Nicht unterstützte Reasoning-Auswahl.')
    return mode


def validate_effort(model, effort):
    # Local adapter contract; an upstream rejection never permits fallback.
    if model in MODELS and isinstance(effort, str) and effort in EFFORTS:
        return effort
    if model in ROUTE_B_EFFORTS:
        if effort != ROUTE_B_EFFORTS[model]:
            raise ValueError('Nicht unterstützte Modell-/Reasoning-Kombination.')
        return effort
    raise ValueError('Nicht unterstützte Modell-/Reasoning-Kombination.')


def routine_step(step, note):
    if not isinstance(note, str) or not note.strip() or len(note) > 1000:
        return False
    if not isinstance(step, dict) or step.get('action') != 'change' or step.get('depends_on') != []:
        return False
    paths = step.get('scope')
    if not isinstance(paths, list) or not 1 <= len(paths) <= 20:
        return False
    for value in paths:
        if not isinstance(value, str) or not value or '\\' in value or ':' in value:
            return False
        path = PurePosixPath(value)
        if path.is_absolute() or '..' in path.parts or path.suffix.lower() not in ('.md', '.txt'):
            return False
    return True


def choose(mode, model, *, routine=False):
    validate_mode(mode)
    if model not in MODELS:
        raise ValueError('Nicht unterstütztes Modell.')
    role = 'orchestrator' if model == MODELS[0] else 'supervisor'
    effort = 'medium' if mode == 'auto' else mode
    reason = 'Manuelle Auswahl' if mode != 'auto' else 'Keine bestätigte Routinegrundlage; Medium'
    if mode == 'auto' and role == 'supervisor':
        reason = 'Unabhängiger Review bleibt Medium'
    elif mode == 'auto' and routine is True:
        effort, reason = 'low', 'Bestätigte unabhängige Dokumentationsroutine mit aktuellem Plan'
    return dict(requested=mode, effective=effort, role=role, reason=reason, version=VERSION)
