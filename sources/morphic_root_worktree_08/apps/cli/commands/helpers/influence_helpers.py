"""Influence and focus weighting helpers."""

from __future__ import annotations

from typing import Dict, List

from .utility_helpers import _build_image_block, _build_organ_clock_block, _normalize_planet_type, _normalize_tcm_type


def _build_influence_factors(tcm_type_raw: str, planet_type_raw: str, image_signature: object) -> Dict[str, object]:
    return {
        "tcm": _normalize_tcm_type(tcm_type_raw or ""),
        "planet": _normalize_planet_type(planet_type_raw or ""),
        "organ_clock": _build_organ_clock_block(),
        "image": _build_image_block(image_signature),
    }


def _norm(text: str) -> str:
    return (
        (text or "")
        .strip()
        .lower()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )


def _compute_influence_multiplier_for_item(group: str, label: str, influence_factors: Dict[str, object]) -> float:
    if not influence_factors:
        return 1.0

    organ_names: List[str] = []
    tcm = influence_factors.get("tcm") or {}
    organ_clock = influence_factors.get("organ_clock") or {}
    if isinstance(tcm, dict):
        organs = str(tcm.get("organs", "") or "")
        organ_names.extend(part.strip() for part in organs.split(",") if part.strip())
    active = organ_clock.get("active_organs") if isinstance(organ_clock, dict) else []
    if isinstance(active, (list, tuple)):
        organ_names.extend(str(item).strip() for item in active if str(item).strip())

    text = _norm(f"{group} {label}")
    delta = 0.0
    aliases = {
        "niere": ["kidney", "ren"],
        "leber": ["liver", "hepar"],
        "lunge": ["lung", "pulmo", "bronchien"],
        "herz": ["heart", "cardio"],
    }
    for organ in organ_names:
        organ_norm = _norm(organ)
        candidates = [organ_norm] + aliases.get(organ_norm, [])
        if any(candidate and candidate in text for candidate in candidates):
            delta += 0.01
        if delta >= 0.03:
            break
    return 1.0 + min(delta, 0.03)


def _compute_focus_multiplier_for_item(
    focus: str,
    group: str,
    label: str,
    item_copen_rate: float = 0.0,
) -> float:
    focus_norm = _norm(focus)
    if not focus_norm:
        return 1.0

    text = _norm(f"{group} {label}")
    focus_map: Dict[str, List[str]] = {
        "atmung": ["atmung", "lunge", "bronchien", "respiration"],
        "bronchien": ["bronchien", "lunge", "atmung", "respiration"],
        "lunge": ["lunge", "bronchien", "atmung", "pulmo"],
        "haut": ["haut", "derma", "narben"],
        "zahn": ["zahn", "zaehn", "odont", "dental", "kiefer"],
        "schwermetall": ["schwermetall", "quecksilber", "blei", "cadmium", "amalgam"],
        "entgiftung": ["entgiftung", "detox", "leber", "niere", "lymphe"],
        "nerv": ["nerv", "neuro", "gehirn", "zns"],
        "immun": ["immun", "abwehr", "entzuendung"],
        "darm": ["darm", "mikrobiom", "verdauung"],
    }

    delta = 0.0
    for key, synonyms in focus_map.items():
        if key in focus_norm:
            for synonym in synonyms:
                if _norm(synonym) in text:
                    delta += 0.025
                    break
    if focus_norm in text:
        delta += 0.05
    return 1.0 + min(delta, 0.15)

