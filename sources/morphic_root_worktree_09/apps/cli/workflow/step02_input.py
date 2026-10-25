"""Step 02: Eingabe - Klientendaten und Parameter sammeln."""

from __future__ import annotations

from .state import WorkflowState


def step_02_input(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    """Step 2: Eingabe-Parameter validieren und Personalprofil aufbauen."""
    if verbose:
        print("  [2/12] Eingabe-Validierung...")

    if not state.name or not state.first_name:
        state.add_error(2, "Name/Vorname fehlt")
        return state

    if not state.birth_date:
        state.add_error(2, "Geburtsdatum fehlt")

    if verbose:
        print(
            f"        Klient: {state.first_name} {state.name} ({state.birth_date}, {state.birth_place})"
        )
        if state.focus:
            print(f"        Fokus: {state.focus}")
        print(f"        Intention: {state.intention}")
        print(f"        Level: {state.profile_level}, Top-N: {state.top_n}")
        print(
            f"        Personalprofil: E={state.p_emotion:.1f} P={state.p_physisch:.1f} M={state.p_mental:.1f} A={state.p_astral:.1f}"
        )

    state.mark_step(2)
    return state
