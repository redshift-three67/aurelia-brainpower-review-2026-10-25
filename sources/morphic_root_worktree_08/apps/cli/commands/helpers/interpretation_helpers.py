"""Interpretation helper functions."""

from __future__ import annotations

from typing import List


# 13-Ebenen-Modell (aus core/levels/level_resonance.py abgeleitet).
# -Level-4 bis Level-11-Abbreviations gemaess Mustermann-Referenzberichten.
_LEVEL_MAP = {
    4: "Aetherische Ebene - Meridiane (Level 4)",
    5: "Astrale Ebene - Emotionen (Level 5)",
    6: "Astrale Ebene - Gedankenformen (Level 6)",
    7: "Mentale Ebene - Zeit (Level 7)",
    8: "Mentale Ebene - Mentale Konstrukte (Level 8)",
    9: "Kausale Ebene - Blaupausen (Level 9)",
    10: "Kausale Ebene - Alchemie (Level 10)",
    11: "Atmische Ebene - Identitaet (Level 11)",
}


def _interpret_level(score: float, group: str, label: str = "") -> str:
    group_norm = (group or "").strip().lower()
    if not group_norm:
        return "physisch"

    if group_norm in {
        "chakren",
        "chakren_full",
        "chakren_erweitert",
        "nebenchakren",
        "extra_meridiane",
    }:
        if score > 10.0:
            return "astral"
        if score > 5.0:
            return "mental"
        return "energetisch"

    if group_norm in {"meridiane", "tcm_punkte", "tcm_punkte_extended", "tcm_full"}:
        return "energetisch" if score > 8.0 else "physisch"

    if group_norm in {
        "homoeopathie_klassisch",
        "homoeopathie_klassisch_potenzen",
        "spagyrik",
        "tcm_rezepturen",
        "tcm_rezepturen_potenzen",
    }:
        if score > 12.0:
            return "mental"
        if score > 6.0:
            return "energetisch"
        return "physisch"

    if group_norm in {
        "bakterien",
        "bakterien_fein",
        "viren",
        "viren_fein",
        "parasiten",
        "parasiten_fein",
        "pilze",
        "pilze_fein",
    }:
        return "physisch"
    if "emf" in group_norm:
        return "energie"
    return "energetisch" if score > 10.0 else "physisch"


def _rates_to_level_info(
    rates: List[float], label: str
) -> tuple[int, float, str, float]:
    """Berechnet Bewusstseins-Ebene (Level 4-11), Level-Wert und Copen-Rate.

    Die Ebene wird aus der ersten Rate (base_rate) abgeleitet:
      - Rate < 10   -> physische Ebene (Level 0, kein Text)
      - Rate 10-20  -> Level 4 (aetherisch/Meridiane)
      - Rate 20-30  -> Level 5 (astral/Emotionen)
      - Rate 30-40  -> Level 6 (astral/Gedankenformen)
      - Rate 40-50  -> Level 7 (mental/Zeit)
      - Rate 50-60  -> Level 8 (mental/Konstrukte)
      - Rate 60-70  -> Level 9 (kausal/Blaupausen)
      - Rate 70-80  -> Level 10 (kausal/Alchemie)
      - Rate >= 80  -> Level 11 (atmisch/Identitaet)

    Copen-Rate = base_rate * 162_000 (Referenz: Mustermann-Berichte).
    """
    if not rates:
        return 0, 0.0, "-", 0.0
    try:
        base_rate = float(rates[0])
    except (TypeError, ValueError):
        return 0, 0.0, "-", 0.0

    copen_rate = base_rate * 162_000.0

    if base_rate < 10.0:
        return 0, base_rate, "physisch", copen_rate

    # Level 4-11 Mapping
    level_id = 4 + int(min(max(base_rate - 10.0, 0.0), 70.0) // 10.0)
    level_id = max(4, min(11, level_id))
    level_text = _LEVEL_MAP.get(level_id, "-")
    return level_id, base_rate, level_text, copen_rate
