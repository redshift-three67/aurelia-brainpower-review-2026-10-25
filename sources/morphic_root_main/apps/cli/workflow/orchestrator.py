"""Workflow Orchestrator - 12-Step Sequenzieller Ablauf nach Radi144-Blueprint.

Dies ist der Haupt-Einstiegspunkt fuer den Workflow-Scan. Es orchestriert
alle 12 Steps sequentiell und reicht den WorkflowState durch.

WICHTIG: Die Kernengine (core/*, services/*) wird NICHT modifiziert.
Alle Steps delegieren an existierende Module oder fuehren aeussere
Modifikationen durch.
"""

from __future__ import annotations

from .state import WorkflowState
from .step01_init import step_01_init
from .step02_input import step_02_input
from .step03_signature import step_03_signature
from .step04_focus import step_04_focus
from .step05_emf import step_05_emf
from .step06_amplifier import step_06_amplifier
from .step07_palette import step_07_palette
from .step08_matrix import step_08_matrix
from .step09_quantum import step_09_quantum
from .step10_post import step_10_post
from .step11_export import step_11_export
from .step12_harmonize import step_12_harmonize


def run_workflow(
    name: str,
    first_name: str,
    birth_date: str = "",
    birth_place: str = "",
    focus: str = "",
    intention: str = "harmonization",
    profile_level: int = 3,
    top_n: int = 5,
    image_path: str = "",
    planet_type: str = "",
    p_emotion: float = 0.5,
    p_physisch: float = 0.5,
    p_mental: float = 0.5,
    p_astral: float = 0.5,
    export_dir: str = "C:\\Benutzer_Archive_Start",
    harmonize: bool = False,
    harmonize_duration: int = 1,
    verbose: bool = True,
) -> WorkflowState:
    """Fuehrt den kompletten 12-Step Workflow aus.

    Returns den finalen WorkflowState mit allen Ergebnissen.
    """
    print("=" * 70)
    print("MORPHIC ENGINE V1 - 12-STEP WORKFLOW (Radi144-Blueprint)")
    print("=" * 70)

    state = WorkflowState(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        focus=focus,
        intention=intention,
        profile_level=profile_level,
        top_n=top_n,
        image_path=image_path,
        planet_type=planet_type,
        p_emotion=p_emotion,
        p_physisch=p_physisch,
        p_mental=p_mental,
        p_astral=p_astral,
    )

    # 12 Steps sequentiell ausfuehren
    step_01_init(state, verbose=verbose)
    step_02_input(state, verbose=verbose)
    step_03_signature(state, verbose=verbose)
    step_04_focus(state, verbose=verbose)
    step_05_emf(state, verbose=verbose)
    step_06_amplifier(state, verbose=verbose)
    step_07_palette(state, verbose=verbose)
    step_08_matrix(state, verbose=verbose)
    step_09_quantum(state, verbose=verbose)
    step_10_post(state, verbose=verbose)
    step_11_export(state, export_dir=export_dir, verbose=verbose)

    if harmonize:
        step_12_harmonize(state, duration_minutes=harmonize_duration, verbose=verbose)
    else:
        state.mark_step(12)
        if verbose:
            print("  [12/12] Harmonisierung uebersprungen.")

    # Zusammenfassung
    print()
    print("=" * 70)
    print("WORKFLOW ABGESCHLOSSEN")
    print("=" * 70)
    print(f"  Steps: {len(state.step_completed)}/12")
    print(f"  Fehler: {len(state.errors)}")
    if state.errors:
        for e in state.errors:
            print(f"    - {e}")
    if state.export_paths:
        print(f"  Export: {state.export_paths.get('html', '-')}")
    print()

    return state
