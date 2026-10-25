"""Step 04: Fokus-Vektor - MD5-Seed basiert, mit Bio-Matching."""

from __future__ import annotations

import hashlib
import numpy as np

from .state import WorkflowState


def step_04_focus(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    if verbose:
        print("  [4/12] Fokus-Vektor...")

    if not state.focus:
        state.focus_vector = np.ones(256, dtype=float) / np.sqrt(256)
        state.focus_multiplier = 1.0
        if verbose:
            print("        Kein Fokus - neutraler Vektor")
    else:
        seed = int(hashlib.md5(state.focus.encode()).hexdigest()[:8], 16)
        rng = np.random.RandomState(seed)
        state.focus_vector = rng.randn(256).astype(float)
        norm = np.linalg.norm(state.focus_vector)
        if norm > 0:
            state.focus_vector /= norm
        state.focus_multiplier = 1.0
        if verbose:
            print(f"        Fokus: {state.focus}")
            print(f"        Vektor-Dimension: {len(state.focus_vector)}")

    state.mark_step(4)
    return state
