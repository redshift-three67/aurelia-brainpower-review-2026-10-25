"""Step 07: Farbpalette - unified_coherent 4-Schicht-Fusion."""

from __future__ import annotations

import hashlib
import math
import numpy as np

from .state import WorkflowState


def _hsv_to_hex(h: float, s: float, v: float) -> str:
    h = h % 1.0
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i = i % 6
    r, g, b = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]
    return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"


def step_07_palette(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    if verbose:
        print("  [7/12] Farbpalette (unified_coherent)...")

    cf = state.client_frequency
    client_hue = (cf * 0.618033988749895) % 1.0
    comp_shift = (
        sum(abs(v) for v in list(state.signature_components.values())[:5])
        % 100
        / 3000.0
    )

    focus_hue = client_hue
    if state.focus:
        h = int(hashlib.md5(state.focus.encode()).hexdigest()[:6], 16)
        focus_hue = (h % 360) / 360.0
        diff = focus_hue - client_hue
        if diff > 0.5:
            diff -= 1.0
        elif diff < -0.5:
            diff += 1.0
        focus_hue = client_hue + (1.0 / 3.0) * diff + comp_shift
    else:
        focus_hue = client_hue + comp_shift

    emf_micro = 0.0
    if state.counter_frequencies:
        emf_micro = (state.counter_frequencies[0] % 1000) / 100000.0

    unified_hue = (focus_hue + emf_micro) % 1.0
    palette = []
    for i in range(10):
        t = i / 9.0
        sat = 0.04 + 0.14 * t
        val = 0.97 - 0.62 * t
        palette.append(_hsv_to_hex(unified_hue, sat, val))

    state.palette = palette
    if verbose:
        print(f"        Basis-Hue: {unified_hue:.3f}")
        print(f"        Palette: {palette[0]} ... {palette[-1]}")

    state.mark_step(7)
    return state
