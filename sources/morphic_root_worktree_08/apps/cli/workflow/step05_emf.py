"""Step 05: EMF-Kompensation - 4-Layer Architektur nach Radi144.

Sensing -> Profiling -> Compensation -> Monitoring
"""

from __future__ import annotations

import hashlib
import os
import time
from collections import deque

import numpy as np

from .state import WorkflowState

_SCHUMANN = [7.83, 14.3, 20.8, 27.3, 33.8]
_SOLFEGGIO_COUNTERS = [528.0, 741.0, 963.0, 174.0]


def _measure_cpu_jitter() -> float:
    timings = []
    for _ in range(50):
        t0 = time.perf_counter_ns()
        s = sum(i * i for i in range(100))
        t1 = time.perf_counter_ns()
        timings.append((t1 - t0) / 1e6)
    arr = np.array(timings)
    return float(np.std(arr))


def _measure_rng_entropy() -> float:
    data = os.urandom(2048)
    arr = np.frombuffer(data, dtype=np.uint8).astype(float)
    autocorr = float(np.corrcoef(arr[:-1], arr[1:])[0, 1]) if len(arr) > 1 else 0.0
    sample = np.frombuffer(data[:256], dtype=np.uint8)
    chi_sq = float(np.sum((np.bincount(sample, minlength=256) - 1.0) ** 2) / 1.0)
    chi_p = min(1.0, chi_sq / 400.0)
    shannon = -np.sum((arr / 256.0) * np.log2(arr / 256.0 + 1e-12))
    score = 0.4 * (shannon / 8.0) + 0.3 * (1 - abs(autocorr)) + 0.3 * (1 - chi_p)
    return float(max(0.0, min(1.0, score)))


def _measure_system_load() -> float:
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        return (cpu + ram) / 200.0
    except Exception:
        return 0.3


def step_05_emf(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    if verbose:
        print("  [5/12] EMF-Kompensation (4-Layer)...")

    # Layer 1: Sensing
    jitter = _measure_cpu_jitter()
    entropy_score = _measure_rng_entropy()
    sys_load = _measure_system_load()
    gpu_noise = 0.0
    autocorr = 0.1

    # Layer 2: Profiling
    state.composite_emf_index = (
        0.30 * (1.0 - entropy_score)
        + 0.25 * min(1.0, jitter)
        + 0.20 * sys_load
        + 0.15 * gpu_noise
        + 0.10 * abs(autocorr)
    )
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

    # Counter-Frequencies (Solfeggio)
    emf = state.composite_emf_index
    counters = []
    counters.append((528.0, 0.2 + emf * 0.6))
    if emf > 0.3:
        counters.append((741.0, emf * 0.7))
    if emf > 0.6:
        counters.append((963.0, emf * 0.5))
        counters.append((174.0, 0.4))
    state.counter_frequencies = [f for f, _ in counters]

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
