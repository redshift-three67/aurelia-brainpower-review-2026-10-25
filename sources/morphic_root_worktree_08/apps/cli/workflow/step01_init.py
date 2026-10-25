"""Step 01: System-Init - Hardware-Erkennung und Entropie-Quelle.

Delegiert an existierende morphic_v1 Hardware-Module ohne sie zu aendern.
"""

from __future__ import annotations

from .state import WorkflowState


def step_01_init(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    """Step 1: Hardware-Erkennung, Entropie-Quelle, h_level."""
    if verbose:
        print("  [1/12] System-Init...")

    try:
        from providers.hardware.entropy_sources import select_entropy_source

        preferred = ["qrng", "truerng", "hid_sensor", "network", "cpu_timer"]
        src = select_entropy_source(preferred)
        state.entropy_source_name = src.name()
        state.h_level = float(src.sample_h_level(duration_s=1.5))
        state.hardware_report = {
            "selected_source": state.entropy_source_name,
            "preferred_order": preferred,
            "sampled_h_level": state.h_level,
        }
        if verbose:
            print(
                f"        Hardware: {state.entropy_source_name} (h_level={state.h_level:.4f})"
            )
    except Exception as exc:
        state.add_error(1, str(exc))
        state.h_level = 0.05
        state.entropy_source_name = "cpu_timer_fallback"
        if verbose:
            print(f"        [WARN] Hardware-Init fallback: {exc}")

    state.mark_step(1)
    return state
