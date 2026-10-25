"""Step 05: EMF-Kompensation - 4-Layer Architektur nach Radi144.

Sensing -> Profiling -> Compensation -> Monitoring
"""

from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path

import numpy as np

from core.realtime.emf_profile import EMFProfileService
from apps.web.emf_authority import EmfTelemetryAuthority

from .state import WorkflowState


def step_05_emf(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    if verbose:
        print("  [5/12] EMF-Kompensation (4-Layer)...")

    # Layer 1/2: Shared V2 sensing and profiling.
    authority_path = os.getenv("MORPHIC_EMF_AUTHORITY_PATH", "").strip()
    authority = EmfTelemetryAuthority(Path(authority_path)) if authority_path else None
    measurement_generation = authority.begin_measurement() if authority is not None else None
    profile = EMFProfileService().measure() if measurement_generation is not None else None
    if (
        profile is not None
        and authority is not None
        and authority.measurement_is_current(measurement_generation)
    ):
        jitter = profile.timing_jitter_ms
        entropy_score = profile.entropy_score
        emf_index = profile.emf_index
        counter_frequencies = list(profile.counter_frequencies)
    else:
        jitter = 0.0
        entropy_score = 0.0
        emf_index = 0.0
        counter_frequencies = []
    gpu_noise = 0.0

    state.composite_emf_index = float(emf_index)
    state.composite_emf_index = float(max(0.0, min(1.0, state.composite_emf_index)))

    # Layer 3: Compensation
    comp_strength = state.composite_emf_index * 0.3
    seed_str = (
        f"{entropy_score:.4f}_{jitter:.4f}_{gpu_noise:.4f}_{time.strftime('%Y%m%d%H')}"
    )
    seed = int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16)
    rng = np.random.RandomState(seed)
    base = np.ones(256, dtype=float)
    noise = rng.randn(256)
    comp = base + noise * comp_strength
    norm = np.linalg.norm(comp)
    if norm > 0:
        comp = comp / norm * np.sqrt(256)
    state.compensation_vector = comp

    # Counter-Frequencies (Solfeggio) come from the shared profile.
    emf = state.composite_emf_index
    state.counter_frequencies = counter_frequencies

    # EMF-Korrektur auf Signatur anwenden (aeussere Modifikation)
    if state.client_rates is not None:
        comp_subset = comp[: len(state.client_rates)]
        state.client_rates = state.client_rates * comp_subset
        state.emf_corrected_frequency = state.client_frequency * (1.0 - emf * 0.05)

    if verbose:
        print(f"        EMF-Index: {emf:.3f}")
        print(f"        Kompensation: {comp_strength:.3f}")
        print(f"        Counter-Freq: {state.counter_frequencies}")

    # Layer 4: Monitoring wird durch wiederholte Ausfuehrung erreicht
    state.mark_step(5)
    return state
