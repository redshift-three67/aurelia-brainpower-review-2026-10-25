"""Potency helper functions."""

from __future__ import annotations

import random
import re


_POTENCY_PATTERN = re.compile(r"\b(D|C|LM|M|CM|MM)\s*([0-9]+)?\b", re.IGNORECASE)
_D_POTENCIES = [1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 15, 30, 60, 100, 200]
_C_POTENCIES = [1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 15, 30, 60, 100, 200]
_LM_POTENCIES = list(range(1, 31))
_Q_POTENCIES = list(range(1, 31))
_KORSAKOFF = ["1M", "5M", "10M", "50M", "100M"]
_FLUXION = ["FC1M", "FC5M", "FC10M", "FC50M", "FC100M"]
_POTENCY_TYPE_WEIGHTS = [("D", 30), ("C", 25), ("LM", 20), ("M", 15), ("F1", 5), ("F2", 3), ("F3", 2)]


def _extract_potency_from_label(label: str) -> str | None:
    match = _POTENCY_PATTERN.search(label or "")
    if not match:
        return None
    pot_type, pot_val = match.groups()
    pot_type = pot_type.upper()
    if pot_type in {"CM", "MM"}:
        return pot_type
    if pot_val:
        return f"{pot_type}{pot_val}"
    return None


def _weighted_pick_potency_type() -> str:
    threshold = random.random() * sum(weight for _, weight in _POTENCY_TYPE_WEIGHTS)
    cumulative = 0.0
    for pot_type, weight in _POTENCY_TYPE_WEIGHTS:
        cumulative += float(weight)
        if threshold < cumulative:
            return pot_type
    return "D"


def _generate_potency_for_type(pot_type: str) -> str:
    pot_type = (pot_type or "D").upper()
    if pot_type == "D":
        return f"D{random.choice(_D_POTENCIES)}"
    if pot_type == "C":
        return f"C{random.choice(_C_POTENCIES)}"
    if pot_type == "LM":
        return f"LM{random.choice(_LM_POTENCIES)}"
    if pot_type == "Q":
        return f"Q{random.choice(_Q_POTENCIES)}"
    if pot_type == "M":
        return random.choice(_KORSAKOFF)
    if pot_type in {"F1", "F2", "F3"}:
        return random.choice(_FLUXION)
    return "D6"


def _interpret_potency_from_score(score: float) -> str:
    return _generate_potency_for_type(_weighted_pick_potency_type())


def _interpret_potency(score: float, label: str | None = None) -> str:
    extracted = _extract_potency_from_label(label or "")
    if extracted:
        return extracted
    return _interpret_potency_from_score(score)

