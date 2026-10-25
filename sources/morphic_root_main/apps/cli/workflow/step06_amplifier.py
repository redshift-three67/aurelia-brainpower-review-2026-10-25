"""Step 06: Amplifier - 12D-Vektor, Cosinus-Match, Top-3."""

from __future__ import annotations

import hashlib
import numpy as np

from .state import WorkflowState

_AMPLIFIERS = [
    {
        "id": "rosenquarz",
        "name": "Rosenquarz",
        "freq": 350,
        "element": "Wasser",
        "chakra": 4,
        "factor": 0.75,
        "solfeggio": 639,
    },
    {
        "id": "amethyst",
        "name": "Amethyst",
        "freq": 480,
        "element": "Feuer",
        "chakra": 6,
        "factor": 0.85,
        "solfeggio": 852,
    },
    {
        "id": "bergkristall",
        "name": "Bergkristall",
        "freq": 528,
        "element": "Metall",
        "chakra": 7,
        "factor": 1.0,
        "solfeggio": 528,
    },
    {
        "id": "turmalin",
        "name": "Schwarzer Turmalin",
        "freq": 174,
        "element": "Erde",
        "chakra": 1,
        "factor": 0.90,
        "solfeggio": 174,
    },
    {
        "id": "schungit",
        "name": "Schungit",
        "freq": 196,
        "element": "Erde",
        "chakra": 1,
        "factor": 0.95,
        "solfeggio": 396,
    },
    {
        "id": "citrin",
        "name": "Citrin",
        "freq": 320,
        "element": "Feuer",
        "chakra": 3,
        "factor": 0.70,
        "solfeggio": 417,
    },
    {
        "id": "lapislazuli",
        "name": "Lapislazuli",
        "freq": 448,
        "element": "Wasser",
        "chakra": 5,
        "factor": 0.80,
        "solfeggio": 741,
    },
    {
        "id": "orgonit_schungit",
        "name": "Orgonit (Schungit)",
        "freq": 8,
        "element": "Erde",
        "chakra": 0,
        "factor": 1.0,
        "solfeggio": 528,
    },
    {
        "id": "orgonit_kristall",
        "name": "Orgonit (Bergkristall)",
        "freq": 8,
        "element": "Metall",
        "chakra": 0,
        "factor": 0.95,
        "solfeggio": 528,
    },
    {
        "id": "kupferspirale",
        "name": "Kupferspirale",
        "freq": 144,
        "element": "Metall",
        "chakra": 2,
        "factor": 0.65,
        "solfeggio": 285,
    },
    {
        "id": "blume_lebens",
        "name": "Blume des Lebens",
        "freq": 432,
        "element": "Holz",
        "chakra": 0,
        "factor": 0.80,
        "solfeggio": 963,
    },
    {
        "id": "selenit",
        "name": "Selenit",
        "freq": 560,
        "element": "Wasser",
        "chakra": 7,
        "factor": 0.85,
        "solfeggio": 963,
    },
]

_CHAKRA_FREQS = {0: 432, 1: 256, 2: 288, 3: 320, 4: 341.3, 5: 384, 6: 426.7, 7: 480}
_ELEMENT_FREQS = {
    "Holz": 294.0,
    "Feuer": 440.0,
    "Erde": 264.0,
    "Metall": 352.0,
    "Wasser": 308.0,
}


def _amp_vector(amp: dict) -> np.ndarray:
    vec = np.zeros(12)
    vec[0] = (amp["freq"] - 20) / 1980.0
    vec[1] = (amp["freq"] * 1.5 - 20) / 1980.0
    vec[2] = (amp["freq"] * 2.0 - 20) / 1980.0
    vec[3] = (amp["freq"] / 2.0 - 20) / 1980.0
    vec[4] = _ELEMENT_FREQS.get(amp["element"], 308.0) / 0.20
    vec[5] = max(
        0.0, 1.0 - abs(amp["freq"] - _CHAKRA_FREQS.get(amp["chakra"], 432)) / 500.0
    )
    vec[6] = amp["factor"]
    vec[7] = (amp["solfeggio"] - 174) / (963 - 174)
    vec[8] = 0.5
    vec[9] = 0.6
    vec[10] = 0.5
    vec[11] = 0.5
    return vec


def _client_vector(state: WorkflowState) -> np.ndarray:
    cf = state.client_frequency
    vec = np.zeros(12)
    vec[0] = (cf - 20) / 1980
    vec[1] = (cf * 1.5 - 20) / 1980
    vec[2] = (cf * 2.0 - 20) / 1980
    vec[3] = (cf / 2.0 - 20) / 1980
    vec[4] = (cf % 100) / 100
    vec[5] = 0.5
    vec[6] = cf / 1000
    vec[7] = 0.5
    focus_hash = (
        int(hashlib.md5(state.focus.encode()).hexdigest()[:6], 16) if state.focus else 0
    )
    vec[8] = (focus_hash % 360) / 360
    vec[9] = 0.5 + (0.1 if state.focus else 0.0)
    vec[10] = 0.5
    vec[11] = state.composite_emf_index
    return vec


def step_06_amplifier(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    if verbose:
        print("  [6/12] Amplifier (12D Cosinus-Match)...")

    cvec = _client_vector(state)
    cnorm = np.linalg.norm(cvec)
    if cnorm == 0:
        cnorm = 1.0

    scored = []
    for amp in _AMPLIFIERS:
        avec = _amp_vector(amp)
        anorm = np.linalg.norm(avec)
        if anorm == 0:
            anorm = 1.0
        cos_sim = float(np.dot(cvec, avec) / (cnorm * anorm))
        total = 0.55 * cos_sim + 0.20 * 0.5 + 0.25 * 0.3
        scored.append({**amp, "score": total, "cosine": cos_sim})

    scored.sort(key=lambda x: x["score"], reverse=True)
    state.amplifier_recommendations = scored[:3]

    if verbose:
        for i, a in enumerate(state.amplifier_recommendations, 1):
            print(
                f"        #{i} {a['name']} (score={a['score']:.3f}, cos={a['cosine']:.3f})"
            )

    state.mark_step(6)
    return state
