from __future__ import annotations

import hashlib
import math
from typing import List, Dict

import numpy as np

SCHUMANN_F0 = 7.83
PHI = (1.0 + 5.0 ** 0.5) / 2.0


def _u01(seed: str) -> float:
    h = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / (2 ** 64)


def _rate_from_freq(f: float) -> float:
    f = max(f, 1e-9)
    return float((math.log10(f / SCHUMANN_F0) * 100.0) % 100.0)


def _musical_rate(n: int) -> float:
    # f = f0 * 2^(n/12)
    f = SCHUMANN_F0 * (2.0 ** (n / 12.0))
    return _rate_from_freq(f)


def _phi_rate(m: int) -> float:
    # f = f0 * phi^m
    f = SCHUMANN_F0 * (PHI ** m)
    return _rate_from_freq(f)


_LABELS: List[str] = [
    "Aorta",
    "Vena cava",
    "Koronararterien",
    "Arteriolen",
    "Kapillaren",
    "Mitralklappe",
    "Aortenklappe",
    "Trikuspidalklappe",
    "Pulmonalklappe",
    "SA-Knoten",
    "AV-Knoten",
    "His-Buendel",
]


def generate_circulation_candidates(seed: str, k: int = 32) -> List[Dict]:
    """
    Erzeugt deterministische Kandidaten (Label + Raten) aus Seed ohne DB.
    - nutzt Halbtonleiter (2^(n/12)) und goldenen Schnitt (phi^m) zur Rate-Erzeugung
    - liefert Paare von Raten (2 Werte) pro Kandidat
    """
    out: List[Dict] = []
    for i in range(k):
        label = _LABELS[i % len(_LABELS)]
        u0 = _u01(f"{seed}|{label}|n")
        u1 = _u01(f"{seed}|{label}|m")
        # n in [-36, +36], m in [-6, +6]
        n = int(round(u0 * 72)) - 36
        m = int(round(u1 * 12)) - 6
        r1 = _musical_rate(n)
        r2 = _phi_rate(m)
        base = (r1 + r2) / 2.0
        # zweite Komponente per deterministischem Offset
        off = int(round(_u01(f"{seed}|{label}|off") * 20))  # 0..20
        r_pair = [float(base % 100.0), float((base + off) % 100.0)]
        out.append({"label": label, "rates": r_pair})
    return out
