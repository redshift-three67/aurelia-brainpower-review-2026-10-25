from __future__ import annotations

import sys
import json
import re
import hashlib
import os
from pathlib import Path
import time
from typing import List, Dict, Optional, Iterable
from datetime import datetime

import numpy as np
import typer

from core.levels.level_resonance import (
    calculate_level_resonance,
    convert_base_rate_to_copen_rate,
    find_highest_resonance_level,
    level_label,
)
from core.profiles.profile import (
    calculate_copen_rate,
    word_to_copen_rate,
    focus_to_copen_rates,
)
from core.morphic_field import (
    MorphicFieldConfig,
    calculate_morphic_field,
    generate_default_quantum_states,
)
from core.nls3d_points_new import NLS3D_POINTS, map_item_to_point
from apps.cli.profiles.registry import get_groups_for_profile, validate_profile_groups
from core.subgroups.procedural_groups import list_groups
from core.hardware import get_full_system_report
from core.remedy_group_registry import is_remedy_group as _central_is_remedy_group

# Import für erweiterte CLI-Befehle (Trend, Konfidenz, 3D, etc.)
try:
    from apps.cli.commands_extended import extended_app
    EXTENDED_CLI_AVAILABLE = True
except ImportError:
    EXTENDED_CLI_AVAILABLE = False
    extended_app = None

# Import für Beschreibungen und Synergien
try:
    from core.remedy_descriptions import get_description
    DESCRIPTIONS_AVAILABLE = True
except ImportError:
    DESCRIPTIONS_AVAILABLE = False
    def get_description(label: str, category: str = "auto") -> Optional[str]:
        return None

def _compute_db_client_rate_value(name: str, first_name: str, birth_date: str, birth_place: str) -> int:
    raw = f"{first_name}{name}{birth_date}{birth_place}"
    raw_norm = "".join(str(raw).split()).upper()
    filtered: List[str] = []
    for ch in raw_norm:
        if "A" <= ch <= "Z" or ch.isdigit():
            filtered.append(ch)
    if not filtered:
        return 0
    total = 0
    for idx, ch in enumerate(filtered):
        pos = idx + 1
        if "A" <= ch <= "Z":
            val = ord(ch) - 64
        else:
            val = ord(ch) - ord("0")
        total += val * pos
    base_rate = total * 1000
    mod_rate = int((base_rate / 21.0) * 34.0)
    if mod_rate < 0:
        mod_rate = 0
    return mod_rate


def _build_db_client_rate_block(client_info: Dict[str, str]) -> Dict[str, object]:
    name = str(client_info.get("name", "") or "")
    first_name = str(client_info.get("first_name", "") or "")
    birth_date = str(client_info.get("birth_date", "") or "")
    birth_place = str(client_info.get("birth_place", "") or "")
    value = _compute_db_client_rate_value(name, first_name, birth_date, birth_place)
    source = "calculated" if value else "empty"
    return {
        "value": float(value),
        "source": source,
    }


def _compute_db_resonance_score(client_rate_value: float, item_rate: float) -> float:
    if client_rate_value <= 0.0 or item_rate <= 0.0:
        return 0.0
    delta_rel = abs(item_rate - client_rate_value) / client_rate_value
    if delta_rel >= 1.0:
        return 0.0
    score = 100.0 * (1.0 - delta_rel)
    if score < 0.0:
        score = 0.0
    elif score > 100.0:
        score = 100.0
    return score


def _build_db_items_from_sub_results(
    sub_results_top: List[Dict[str, object]],
    max_items: int,
    client_rate_value: float | None,
) -> List[Dict[str, object]]:
    db_items: List[Dict[str, object]] = []
    if max_items <= 0:
        return db_items
    limit = max_items if max_items > 0 else len(sub_results_top)
    for entry in sub_results_top[:limit]:
        try:
            label = str(entry.get("label", "") or "").strip()
        except Exception:
            label = ""
        if not label:
            continue
        group_val = str(entry.get("group", "") or "").strip()
        potency_val = str(entry.get("potency", "") or "").strip()
        rate_raw = entry.get("copen_rate")
        rate_num: float | None
        try:
            if rate_raw is None:
                rate_num = None
            else:
                rate_num = float(rate_raw)
        except Exception:
            rate_num = None
        item_block: Dict[str, object] = {
            "label": label,
            "group": group_val,
        }
        if potency_val:
            item_block["potency"] = potency_val
        resonance_val: float | None = None
        if rate_num is not None:
            item_block["rate"] = float(rate_num)
            try:
                rate_int = int(rate_num)
                rate_fmt = f"{rate_int:,}".replace(",", ".")
            except Exception:
                rate_fmt = str(rate_num)
            item_block["rate_formatted"] = rate_fmt
            if client_rate_value is not None:
                try:
                    cr = float(client_rate_value)
                except Exception:
                    cr = 0.0
                if cr > 0.0 and rate_num > 0.0:
                    resonance_val = _compute_db_resonance_score(cr, float(rate_num))
        if resonance_val is not None:
            item_block["resonance_score"] = float(resonance_val)
        db_items.append(item_block)
    return db_items


def _build_db_analysis_summary(items: List[Dict[str, object]], top_n: int = 5) -> Dict[str, object]:
    total = len(items)
    resonance_values: List[float] = []
    for it in items:
        try:
            raw = it.get("resonance_score")
            if raw is None:
                continue
            val = float(raw)
        except Exception:
            continue
        resonance_values.append(val)

    res_count = len(resonance_values)
    if res_count > 0:
        res_max = max(resonance_values)
        res_min = min(resonance_values)
        res_mean = float(sum(resonance_values) / res_count)
    else:
        res_max = None
        res_min = None
        res_mean = None

    top_candidates: List[Dict[str, object]] = []
    if res_count > 0 and items:
        tmp: List[Dict[str, object]] = []
        for it in items:
            try:
                raw = it.get("resonance_score")
                if raw is None:
                    continue
                val = float(raw)
            except Exception:
                continue
            if val < 0.0:
                continue
            label = str(it.get("label", "") or "").strip()
            group_val = str(it.get("group", "") or "").strip()
            tmp.append(
                {
                    "label": label,
                    "group": group_val,
                    "resonance_score": float(val),
                }
            )
        tmp.sort(key=lambda e: e.get("resonance_score", 0.0), reverse=True)
        if top_n > 0:
            top_candidates = tmp[:top_n]
        else:
            top_candidates = tmp

    summary: Dict[str, object] = {
        "items_total": int(total),
        "resonance_count": int(res_count),
        "resonance_max": float(res_max) if res_max is not None else None,
        "resonance_min": float(res_min) if res_min is not None else None,
        "resonance_mean": float(res_mean) if res_mean is not None else None,
        "top_resonance": top_candidates,
    }
    return summary


def _summarize_axis_items(items: List[Dict[str, object]], top_n: int = 5) -> Dict[str, object]:
    """Erzeugt eine kompakte Zusammenfassung für eine Achse aus Top-Items.

    Nutzt ausschließlich vorhandene Felder (label, score, group, level, copen_rate).
    """

    total = len(items)
    scores: List[float] = []
    for it in items:
        try:
            raw = it.get("score")
            if raw is None:
                continue
            val = float(raw)
        except Exception:
            continue
        scores.append(val)

    if scores:
        score_max = max(scores)
        score_mean = float(sum(scores) / len(scores))
    else:
        score_max = None
        score_mean = None

    tops: List[Dict[str, object]] = []
    if items and top_n != 0:
        # Sortiere nach Score absteigend, falls möglich
        try:
            tmp = [it for it in items]

            def _score_key(e: Dict[str, object]) -> float:
                try:
                    raw = e.get("score")
                    if raw is None:
                        return 0.0
                    return float(raw)
                except Exception:
                    return 0.0

            tmp.sort(key=_score_key, reverse=True)
        except Exception:
            tmp = items

        if top_n > 0:
            tmp = tmp[:top_n]

        for it in tmp:
            label = str(it.get("label", "") or "").strip()
            group_val = str(it.get("group", "") or "").strip()
            entry: Dict[str, object] = {
                "label": label,
                "group": group_val,
            }
            try:
                raw_score = it.get("score")
                if raw_score is not None:
                    entry["score"] = float(raw_score)
            except Exception:
                pass
            level_val = it.get("level")
            if level_val not in (None, ""):
                entry["level"] = level_val
            try:
                cr_raw = it.get("copen_rate")
                if cr_raw is not None:
                    entry["copen_rate"] = float(cr_raw)
            except Exception:
                pass
            tops.append(entry)

    summary: Dict[str, object] = {
        "items_total": int(total),
        "score_max": float(score_max) if score_max is not None else None,
        "score_mean": float(score_mean) if score_mean is not None else None,
        "top": tops,
    }
    return summary


def _build_morphic_axes_from_sub_results(sub_results_top: List[Dict[str, object]]) -> Dict[str, object]:
    """Leitet Achsen (Wirbelsäule, Zahn-Organ-System) aus den Top-Items ab.

    Verwendet nur vorhandene Gruppen wie "wirbelsaeule*", "zahnorgane*" und "odontone".
    Ändert keine Scores, fasst nur zusammen.
    """

    def _norm_group(g: str) -> str:
        return (g or "").strip().lower()

    spine_all: List[Dict[str, object]] = []
    spine_hws: List[Dict[str, object]] = []
    spine_bws: List[Dict[str, object]] = []
    spine_lws: List[Dict[str, object]] = []

    dental_all: List[Dict[str, object]] = []
    zahnorgane_items: List[Dict[str, object]] = []
    odontone_items: List[Dict[str, object]] = []

    for it in sub_results_top:
        group_raw = str(it.get("group", "") or "")
        g = _norm_group(group_raw)
        if not g:
            continue

        # Wirbelsäule: alle Gruppen, die mit "wirbelsaeule" beginnen
        if g.startswith("wirbelsaeule"):
            spine_all.append(it)
            if g == "wirbelsaeule_hws":
                spine_hws.append(it)
            elif g == "wirbelsaeule_bws":
                spine_bws.append(it)
            elif g == "wirbelsaeule_lws":
                spine_lws.append(it)

        # Zahn-Organ-System: zahnorgane*, odontone
        if g.startswith("zahnorgane") or g == "odontone":
            dental_all.append(it)
            if g.startswith("zahnorgane"):
                zahnorgane_items.append(it)
            elif g == "odontone":
                odontone_items.append(it)

    axes: Dict[str, object] = {
        "enabled": False,
        "engine": "morphic_axes_v1",
    }

    spine_block: Dict[str, object] = {}
    if spine_all:
        spine_block["global"] = _summarize_axis_items(spine_all)
    if spine_hws:
        spine_block["hws"] = _summarize_axis_items(spine_hws)
    if spine_bws:
        spine_block["bws"] = _summarize_axis_items(spine_bws)
    if spine_lws:
        spine_block["lws"] = _summarize_axis_items(spine_lws)

    dental_block: Dict[str, object] = {}
    if dental_all:
        dental_block["global"] = _summarize_axis_items(dental_all)
    if zahnorgane_items:
        dental_block["zahnorgane"] = _summarize_axis_items(zahnorgane_items)
    if odontone_items:
        dental_block["odontone"] = _summarize_axis_items(odontone_items)

    if spine_block:
        axes["spine"] = spine_block
    if dental_block:
        axes["dental"] = dental_block

    if spine_block or dental_block:
        axes["enabled"] = True

    return axes


def analyze_remedy_synergies(items: List[Dict], max_results: int = 10) -> List[Dict]:
    """Analysiert synergetische Remedy-Kombinationen basierend auf Rate-Overlap.

    Rückgabeformat (kompatibel zum HTML-Renderer):
    [
        {
            "label": str,              # Haupt-Remedy
            "score": float,            # Score des Haupt-Remedys
            "rates": List[float],      # [min_rate, max_rate] oder erste zwei Raten
            "synergies": [             # Synergetische Partner
                {"partner_label": str, "synergy_score": float},
                ...
            ],
        },
        ...
    ]
    """
    if not items or len(items) < 2:
        return []

    # Map von Label auf Original-Item (für Score/Raten)
    label_to_item: Dict[str, Dict] = {}
    for it in items:
        try:
            lbl = str(it.get("label", "") or "").strip()
        except Exception:
            continue
        if not lbl:
            continue
        label_to_item[lbl] = it

    if len(label_to_item) < 2:
        return []

    # Sammle Synergien pro Haupt-Label
    main_synergies: Dict[str, Dict[str, float]] = {}

    labels = list(label_to_item.keys())
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            lbl1 = labels[i]
            lbl2 = labels[j]
            item1 = label_to_item[lbl1]
            item2 = label_to_item[lbl2]

            rates1 = item1.get("rates", [])
            rates2 = item2.get("rates", [])
            if not rates1 or not rates2:
                continue

            # Berechne Rate-Overlap (einfache Distanz der ersten beiden Raten)
            try:
                r1 = np.array([float(x) for x in rates1[:2]])
                r2 = np.array([float(x) for x in rates2[:2]])
                if r1.shape[0] == 0 or r2.shape[0] == 0:
                    continue

                distance = np.linalg.norm(r1 - r2)

                # Synergie-Score: Je näher die Raten, desto höher die Synergie
                synergy_score = max(0.0, 10.0 - distance / 10.0)

                # Nur signifikante Synergien berücksichtigen
                if synergy_score <= 5.0:
                    continue

                # Trage Synergie bidirektional ein
                main_synergies.setdefault(lbl1, {})[lbl2] = max(
                    synergy_score,
                    main_synergies.get(lbl1, {}).get(lbl2, 0.0),
                )
                main_synergies.setdefault(lbl2, {})[lbl1] = max(
                    synergy_score,
                    main_synergies.get(lbl2, {}).get(lbl1, 0.0),
                )
            except Exception:
                continue

    if not main_synergies:
        return []

    # Baue Ergebnisstruktur pro Haupt-Remedy
    results: List[Dict] = []
    for main_label, partners in main_synergies.items():
        item = label_to_item.get(main_label) or {}
        try:
            main_score = float(item.get("score", 0.0) or 0.0)
        except Exception:
            main_score = 0.0

        rates_raw = item.get("rates", []) or []
        rates_clean: List[float] = []
        try:
            rates_clean = [float(x) for x in rates_raw[:2]]
        except Exception:
            rates_clean = []
        
        # Copen-Rate übernehmen falls vorhanden
        copen_rate = item.get("copen_rate")

        # Falls weniger als zwei Raten vorhanden sind, aus allen Raten in partners approximieren
        if len(rates_clean) < 2:
            collected: List[float] = []
            for partner_label in partners.keys():
                p_item = label_to_item.get(partner_label) or {}
                try:
                    pr = [float(x) for x in (p_item.get("rates", []) or [])[:2]]
                    collected.extend(pr)
                except Exception:
                    continue
            if collected:
                rates_clean = [min(collected), max(collected)]

        partner_list = [
            {"partner_label": pl, "synergy_score": float(ps or 0.0)}
            for pl, ps in partners.items()
        ]
        partner_list.sort(key=lambda e: e["synergy_score"], reverse=True)

        if not partner_list:
            continue

        max_partner_synergy = partner_list[0]["synergy_score"]
        result_item = {
            "label": main_label,
            "score": main_score,
            "rates": rates_clean,
            "synergies": partner_list,
            "_max_partner_synergy": max_partner_synergy,
        }
        # Copen-Rate hinzufügen falls vorhanden
        if copen_rate is not None:
            result_item["copen_rate"] = copen_rate
        results.append(result_item)

    if not results:
        return []

    # Sortiere nach höchster Partner-Synergie und begrenze Anzahl Ergebnisse
    results.sort(key=lambda x: x.get("_max_partner_synergy", 0.0), reverse=True)
    trimmed = results[:max_results]
    for r in trimmed:
        r.pop("_max_partner_synergy", None)
    return trimmed


def _is_remedy_group(group: str) -> bool:
    """Heuristik, um Remedy-Gruppen zu erkennen.
    
    Verwendet die zentrale Registry aus core.remedy_group_registry.
    Neue Remedy-Gruppen müssen NUR DORT hinzugefügt werden!
    """
    return _central_is_remedy_group(group)

_POTENCY_PATTERN = re.compile(r"\b(D|C|LM|M|CM|MM)\s*([0-9]+)?\b", re.IGNORECASE)

_LEGACY_LEVELS = (
    "physisch",
    "energetisch",
    "mental",
    "astral",
    "kausal",
    "spiritual",
    "seelisch",
    "kosmisch",
    "monadisch",
    "logoisch",
    "göttlich",
    "quanten",
    "hyper",
)


def _rates_to_level_info(rates: List[float], label: str) -> tuple[int, float, str, float]:
    """Leitet aus vorhandenen Raten eine dominante Ebene ab.

    - Nutzt die erste Base-10-Rate zur Frequenzberechnung.
    - Berechnet anschließend die 13-Ebenen-Resonanz und ermittelt die höchste Ebene.
    """

    if not rates:
        return 0, 0.0, "-", 0.0
    try:
        # Base-10-Rate (0-100) in eine Base-Rate nach Copen-Logik überführen.
        # Hier skalieren wir so, dass die resultierende Copen-Rate typischerweise
        # im Bereich 1-20 Mio liegt und damit gut zu den Ebenenfenstern passt.
        # Näherung: base_rate ~ primarySum * 1000.
        base_rate = float(rates[0]) * 100_000.0
        copen_rate = convert_base_rate_to_copen_rate(base_rate)
        res_levels = calculate_level_resonance(copen_rate, label)

        # Level 13 (Schöpfer/Göttlichkeit) bleibt optional im System,
        # wird aber aktuell nicht als dominante Ebene ausgewählt.
        if "level_13" in res_levels:
            res_levels["level_13"] = 0.0

        lvl_id, lvl_val = find_highest_resonance_level(res_levels)
        if lvl_id <= 0 or lvl_val <= 0.0:
            return 0, 0.0, "-", float(copen_rate)
        return int(lvl_id), float(lvl_val), level_label(int(lvl_id)), float(copen_rate)
    except Exception:
        return 0, 0.0, "-", 0.0


def _extract_potency_from_label(label: str) -> str | None:
    """Extrahiert Potenz aus Label (z.B. 'An Shen Wan C200' -> 'C200')."""
    match = _POTENCY_PATTERN.search(label)
    if not match:
        return None
    pot_type, pot_val = match.groups()
    pot_type = pot_type.upper()
    
    # Spezialfälle: CM, MM ohne Zahl
    if pot_type in {"CM", "MM"}:
        return pot_type
    
    # Normale Potenzen mit Wert
    if pot_val:
        return f"{pot_type}{pot_val}"
    
    # Nur Typ ohne Wert -> nicht verwenden
    return None

# Erweiterte Potenzreihen (inkl. D0 = Ursubstanz)
_D_POTENCIES = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 15, 30, 60, 100, 200]
_C_POTENCIES = [1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 15, 30, 60, 100, 200]
_LM_POTENCIES = list(range(1, 31))  # LM1-LM30
_Q_POTENCIES = list(range(1, 31))   # Q1-Q30
_KORSAKOFF = ["M", "CM", "MM", "1M", "5M", "10M", "50M", "100M"]
_FLUXION = ["FC1M", "FC5M", "FC10M", "FC50M", "FC100M"]

_POTENCY_TYPE_WEIGHTS = [
    ("D", 30),   # Dezimal-Potenzen
    ("C", 25),   # Centesimal-Potenzen
    ("LM", 20),  # LM-Potenzen
    ("M", 15),   # Korsakoff-/M-Potenzen
    ("F1", 5),   # Fluxion 1
    ("F2", 3),   # Fluxion 2
    ("F3", 2),   # Fluxion 3
]


def _weighted_pick_potency_type() -> str:
    """Gewichtete Auswahl des Potenztyps (D, C, LM, M, F1, F2, F3)."""
    import random

    r = random.random() * 100.0
    cumulative = 0.0
    for pot_type, weight in _POTENCY_TYPE_WEIGHTS:
        cumulative += float(weight)
        if r < cumulative:
            return str(pot_type)
    return "D"


def _generate_potency_for_type(pot_type: str) -> str:
    """Erzeugt eine Potenzangabe für den gegebenen Potenztyp.

    Verwendet die diskreten Potenzreihen gemäß Dokumentation:
    - D-Potenzen: D1-7, 9, 10, 12, 15, 30, 60, 100, 200
    - C-Potenzen: C1-7, 9, 10, 12, 15, 30, 60, 100, 200
    - LM-Potenzen: LM1-30
    - Korsakoff-Potenzen: 1M, 5M, 10M, 50M, 100M (inkl. M/CM/MM als Spezialfälle)
    - Fluxionspotenzen: FC1M, FC5M, FC10M, FC50M, FC100M
    """

    import random

    pot_type = pot_type.upper()

    # D-Potenzen: 70 % niedrig (≤ D30), 30 % höher (> D30)
    if pot_type == "D":
        available = [v for v in _D_POTENCIES if v > 0]
        low = [v for v in available if v <= 30]
        high = [v for v in available if v > 30]
        r = random.random()
        if r < 0.7 and low:
            val = random.choice(low)
        elif high:
            val = random.choice(high)
        else:
            val = random.choice(available)
        return f"D{int(val)}"

    # C-Potenzen: 60 % niedrige/mittlere (bis C30), 40 % hohe (C60/C100/C200)
    if pot_type == "C":
        available = list(_C_POTENCIES)
        low = [v for v in available if v <= 30]
        high = [v for v in available if v > 30]
        r = random.random()
        if r < 0.6 and low:
            val = random.choice(low)
        elif high:
            val = random.choice(high)
        else:
            val = random.choice(available)
        return f"C{int(val)}"

    # LM-Potenzen: LM1-LM30, gleichverteilt
    if pot_type == "LM":
        if not _LM_POTENCIES:
            return "LM1"
        val = random.choice(_LM_POTENCIES)
        return f"LM{int(val)}"

    # M/Korsakoff-Potenzen: Auswahl aus 1M, 5M, 10M, 50M, 100M (+ M/CM/MM)
    if pot_type == "M":
        if not _KORSAKOFF:
            return "M1"
        # Einfache gewichtete Auswahl: niedrigere M häufiger
        candidates = ["1M", "5M", "10M", "50M", "100M"]
        weights = [40, 30, 15, 10, 5]
        r = random.random() * sum(weights)
        cumulative = 0.0
        for label, w in zip(candidates, weights):
            cumulative += float(w)
            if r < cumulative:
                return label
        return candidates[0]

    # Fluxionspotenzen: F1/F2/F3 werden auf FC-Potenzen abgebildet
    if pot_type in {"F1", "F2", "F3"}:
        if not _FLUXION:
            return f"{pot_type}-1"
        # F1 bevorzugt niedrigere FC-Potenzen, F3 höherere
        if pot_type == "F1":
            subset = _FLUXION[:2]  # FC1M, FC5M
        elif pot_type == "F2":
            subset = _FLUXION[1:4]  # FC5M, FC10M, FC50M
        else:  # F3
            subset = _FLUXION[2:]  # FC10M, FC50M, FC100M
        return random.choice(subset)

    # Fallback: eine moderate D-Potenz
    return "D6"


def _interpret_potency_from_score(score: float) -> str:
    """Potenzberechnung über gewichtete Zufallsauswahl.

    Die Score-Höhe wird derzeit nicht direkt verwendet; die Potenz ergibt sich aus
    einer gewichteten Auswahl des Potenztyps (D/C/LM/M/F1/F2/F3) und der jeweiligen
    Potenzreihe. Potenzen aus dem Label haben weiterhin Vorrang (_interpret_potency).
    """

    pot_type = _weighted_pick_potency_type()
    return _generate_potency_for_type(pot_type)

def _interpret_level(score: float, group: str, label: str = "") -> str:
    """Interpretiert die Ebene basierend auf Score und Gruppe (Referenz 16.11)."""
    if not group:
        return "physisch"
    
    group = group.lower()
    
    # Energetische Systeme
    energetics = {"chakren", "chakren_full", "chakren_erweitert", "nebenchakren", "extra_meridiane"}
    if group in energetics:
        if score > 10.0:
            return "astral"
        elif score > 5.0:
            return "mental"
        else:
            return "energetisch"
    
    # Meridiane und TCM
    meridians = {"meridiane", "tcm_punkte", "tcm_punkte_extended", "tcm_full"}
    if group in meridians:
        if score > 8.0:
            return "energetisch"
        else:
            return "physisch"
    
    # Homöopathie und Remedies
    remedies = {"homoeopathie_klassisch", "homoeopathie_klassisch_potenzen", "spagyrik", 
                "tcm_rezepturen", "tcm_rezepturen_potenzen"}
    if group in remedies:
        if score > 12.0:
            return "mental"
        elif score > 6.0:
            return "energetisch"
        else:
            return "physisch"
    
    # Pathogene und Toxine
    patho = {"bakterien", "bakterien_fein", "viren", "viren_fein", 
             "parasiten", "parasiten_fein", "pilze", "pilze_fein"}
    tox = {"schwermetalle", "schwermetalle_tox", "strahlung_tox", 
           "pestizide_tox", "chemikalien_tox", "emf_fein"}
    if group in patho or group in tox:
        return "physisch"
    
    # EMF hat spezielle Ebene
    if "emf" in group:
        return "energie"
    
    # Standard: Score-basiert
    if score > 10.0:
        return "energetisch"
    else:
        return "physisch"

def _interpret_potency(score: float, label: str | None = None) -> str:
    """Interpretiert die Potenz: Zuerst aus Label, dann aus Score (Referenz 16.11)."""
    label = label or ""
    
    # 1. Priorität: Potenz aus Label extrahieren
    extracted = _extract_potency_from_label(label)
    if extracted:
        return extracted
    
    # 2. Fallback: Score-basierte Berechnung
    return _interpret_potency_from_score(score)

def _generate_harmonization_steps(group_buckets: Dict[str, List[Dict[str, object]]], max_score: float) -> List[str]:
    """Generiert konkrete Harmonisierungsschritte basierend auf den Gruppen-Ergebnissen."""
    steps = []
    
    # Priorisierung basierend auf Scores
    high_priority_groups = []
    medium_priority_groups = []
    
    for group, items in group_buckets.items():
        if not items:
            continue
        
        # Höchster Score in der Gruppe
        max_group_score = max(float(item.get("score", 0.0)) for item in items)
        relative_score = max_group_score / max_score if max_score > 0 else 0
        
        if relative_score > 0.7:  # Hohe Priorität
            high_priority_groups.append((group, max_group_score, items))
        elif relative_score > 0.3:  # Mittlere Priorität
            medium_priority_groups.append((group, max_group_score, items))
    
    # Sortiere nach Score
    high_priority_groups.sort(key=lambda x: x[1], reverse=True)
    medium_priority_groups.sort(key=lambda x: x[1], reverse=True)
    
    # Generiere Schritte für hohe Priorität
    for group, score, items in high_priority_groups[:3]:  # Top 3
        top_item = max(items, key=lambda x: float(x.get("score", 0.0)))
        label = top_item.get("label", "")
        
        if group in ["bakterien", "bakterien_fein", "viren", "viren_fein", "parasiten", "parasiten_fein", "pilze", "pilze_fein"]:
            steps.append(f"<strong>Mikrobielles Feld regulieren:</strong> {label} ({score:.2f}) mit Feinscan bestätigen und gezielt behandeln. Immunsystem stärken.")
        elif group in ["schwermetalle", "schwermetalle_tox"]:
            steps.append(f"<strong>Entgiftung einleiten:</strong> {label} ({score:.2f}) - Separater Schwermetall-Scan empfohlen. Entgiftungsorgane unterstützen.")
        elif group in ["meridiane", "tcm_punkte", "tcm_punkte_extended"]:
            steps.append(f"<strong>Energiefluss harmonisieren:</strong> {label} ({score:.2f}) - Akupunktur oder energetische Behandlung erwägen.")
        elif group in ["chakren", "chakren_full", "chakren_erweitert", "nebenchakren"]:
            steps.append(f"<strong>Energiezentren ausgleichen:</strong> {label} ({score:.2f}) - Energetische Harmonisierung, Meditation, Chakra-Arbeit.")
        elif group in ["homoeopathie_klassisch", "homoeopathie_klassisch_potenzen"]:
            steps.append(f"<strong>Konstitutionelle Behandlung:</strong> {label} ({score:.2f}) - Homöopathische Konstitutionsbehandlung in Betracht ziehen.")
        elif group in ["zahnorgane", "odontone"]:
            steps.append(f"<strong>Zahn-Organ-System prüfen:</strong> {label} ({score:.2f}) - Zahnärztliche Kontrolle, mögliche Störfelder abklären.")
        elif group in ["endokrin", "detox", "mitochondrien"]:
            steps.append(f"<strong>Grundregulation stärken:</strong> {label} ({score:.2f}) - Systemische Regulation unterstützen, Mikronährstoffe prüfen.")
        else:
            steps.append(f"<strong>{group.title()} harmonisieren:</strong> {label} ({score:.2f}) - Spezifische Behandlung erwägen.")
    
    # Generiere allgemeine Schritte für mittlere Priorität
    if medium_priority_groups:
        medium_groups = [group for group, _, _ in medium_priority_groups[:2]]
        if medium_groups:
            steps.append(f"<strong>Ergänzende Maßnahmen:</strong> {', '.join(medium_groups)} - Unterstützende Therapien in Betracht ziehen.")
    
    # Allgemeine Empfehlungen
    if high_priority_groups or medium_priority_groups:
        steps.append("<strong>Nachkontrolle:</strong> Verlaufskontrolle nach 4-6 Wochen empfohlen, um Behandlungserfolg zu überprüfen.")
        steps.append("<strong>Ganzheitlicher Ansatz:</strong> Ernährung, Bewegung und Stressmanagement als Basis-Therapie integrieren.")
    
    return steps

from core.profiles.profile import ClientProfile, RateEncoder
from services.analysis_service import AnalysisService
from services.subgroup_service import SubgroupService
from services.nls_service import NlsService
from services.description_service import get_descriptions_batch
from providers.hardware.hardware_entropy import get_adaptive_h_level, sample_hid_level
from providers.hardware.entropy_sources import select_entropy_source
from tools.group_manager import GroupManager

# Import potency_sim from parent directory
import sys
from pathlib import Path
_parent_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

try:
    from potency_sim import simulate as simulate_potency
except ImportError:
    # Fallback: Einfache deterministische Simulation
    def simulate_potency(label: str, seed: str | None = None) -> tuple[str, int, int]:
        import hashlib
        h = hashlib.sha256(f"{label}|{seed or ''}".encode()).hexdigest()
        pot_types = ["D", "C", "LM", "M"]
        pot_idx = int(h[:2], 16) % len(pot_types)
        pot_type = pot_types[pot_idx]
        pot_val = (int(h[2:4], 16) % 100) + 1
        level = (int(h[4:6], 16) % 12) + 1
        return pot_type, pot_val, level


app = typer.Typer(help="Morphic Engine V1 – CLI für Analyse-Workflows.")

# Erweiterte CLI-Befehle registrieren (ext trend, ext recommend, etc.)
if EXTENDED_CLI_AVAILABLE and extended_app is not None:
    app.add_typer(extended_app, name="ext", help="Erweiterte Analyse-Befehle")


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _build_rate_db_from_subgroups(groups: List[str], seed: str, k_total: int = 64) -> Dict[str, List[float]]:
    svc = SubgroupService()
    candidates = svc.generate_fullbody_candidates(groups, seed, k_total=k_total)
    rate_db: Dict[str, List[float]] = {}
    for item in candidates:
        label = str(item.get("label"))
        rates = [float(r) for r in item.get("rates", [])]
        if not rates:
            continue
        rate_db[label] = rates
    return rate_db


def _client_folder_name(name: str, first_name: str, birth_date: str, birth_place: str) -> str:
    slug = f"{name}_{first_name}_{birth_date}_{birth_place}".strip()
    return slug.replace(" ", "_")


def _resolve_export_paths(export: Path, client: Dict[str, str], command: str, filename_suffix: str = "", scan_type: str = "", session_id: str = "") -> tuple[Path, Path]:
    """
    Löst Export-Pfade auf und erstellt Ordnerstruktur.
    
    Args:
        export: Basis-Export-Pfad
        client: Klienten-Daten
        command: Befehlsname (z.B. 'multiplex_scan')
        filename_suffix: Optionaler Dateiname-Suffix
        scan_type: Scan-Typ für Ordner-Label ('SINGLE' oder 'top5_session')
        session_id: Session-ID für Top-5 Gruppierung
    """
    export = export.resolve()
    suffix = export.suffix.lower()

    if suffix == ".json":
        json_path = export
        html_path = export.with_suffix(".html")
    elif suffix in {".html", ".htm"}:
        html_path = export
        json_path = export.with_suffix(".json")
    else:
        base_dir = export
        client_dir = base_dir / _client_folder_name(
            str(client.get("name", "")),
            str(client.get("first_name", "")),
            str(client.get("birth_date", "")),
            str(client.get("birth_place", "")),
        )
        # Verwende filename_suffix wenn angegeben, sonst Standard-Timestamp
        if filename_suffix:
            ts = filename_suffix
        else:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # NEUE STRUKTUR: Top-5 Sessions gruppiert, Einzelscans separat
        # Format Top-5: Klient_Ordner/YYYYMMDD_HHMMSS_TOP5_SESSION/01_profil/...
        # Format Single: Klient_Ordner/YYYYMMDD_HHMMSS_SINGLE/...
        if scan_type == "top5_session" and session_id:
            # Top-5 Session: Alle Profile in einen SESSION-Ordner
            session_folder = f"{session_id}_TOP5_SESSION"
            session_dir = client_dir / session_folder
            
            # Extrahiere Profil-Nummer und Namen aus filename_suffix
            # Format: YYYYMMDD_HHMMSS_01_profilename_top5
            parts = filename_suffix.split("_")
            if len(parts) >= 4:
                profile_num = parts[2]  # "01", "02", etc.
                profile_name = "_".join(parts[3:-1])  # profilename (ohne "top5")
                profile_folder = f"{profile_num}_{profile_name}"
            else:
                profile_folder = filename_suffix
            
            analysis_dir = session_dir / profile_folder
            json_path = analysis_dir / f"{ts}_{command}.json"
            html_path = analysis_dir / f"{ts}_{command}.html"
        elif scan_type:
            # Single-Scan oder andere Scan-Typen
            folder_name = f"{ts}_{scan_type}"
            analysis_dir = client_dir / folder_name
            json_path = analysis_dir / f"{ts}_{command}.json"
            html_path = analysis_dir / f"{ts}_{command}.html"
        else:
            # Fallback: Alte Struktur
            folder_name = ts
            analysis_dir = client_dir / folder_name
            json_path = analysis_dir / f"{ts}_{command}.json"
            html_path = analysis_dir / f"{ts}_{command}.html"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    return json_path, html_path


def _atomic_write_text(target: Path, content: str) -> None:
    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)
    tmp = parent / (target.name + f".tmp.{int(time.time()*1000)}")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)


_HTML_HEAD = (
    "<!DOCTYPE html><html lang='de'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    "<title>Resonanzanalyse – Report</title><style>"
    # Modern Light Design - Inspiriert von Neomorphism & Glassmorphismus
    "* {margin:0;padding:0;box-sizing:border-box;}"
    "body{font-family:'Inter','Segoe UI',Roboto,Arial,sans-serif;background:linear-gradient(135deg,#E8F1F8 0%,#D8E8F0 50%,#C5DAE8 100%);"
    "min-height:100vh;padding:30px 20px;font-size:11pt;line-height:1.6;color:#2C3E50;}"
    # Container mit Glasmorphism
    ".container{max-width:1100px;margin:0 auto;background:rgba(255,255,255,0.75);backdrop-filter:blur(20px);"
    "padding:35px;border-radius:24px;box-shadow:0 8px 32px rgba(107,165,208,0.15),0 2px 8px rgba(0,0,0,0.05);"
    "border:1px solid rgba(255,255,255,0.8);}"
    # Header Styling - Soft Blue Gradient
    "h1{font-size:22pt;font-weight:600;margin:0 0 20px;color:#2C3E50;padding-bottom:15px;"
    "border-bottom:2px solid rgba(107,165,208,0.3);letter-spacing:-0.5px;}"
    "h2{font-size:16pt;font-weight:600;margin:30px 0 15px;color:#3D5A73;"
    "padding:12px 20px;background:linear-gradient(135deg,rgba(107,165,208,0.08),rgba(167,199,231,0.12));"
    "border-radius:12px;border-left:4px solid #6BA5D0;}"
    "h3{font-size:13pt;font-weight:600;margin:20px 0 12px;color:#4A6278;}"
    # Tabellen - Clean & Modern
    "table{border-collapse:separate;border-spacing:0;width:100%;font-size:10pt;margin:20px 0;"
    "background:rgba(255,255,255,0.5);border-radius:12px;overflow:hidden;"
    "box-shadow:0 2px 12px rgba(107,165,208,0.08);}"
    "th,td{padding:12px 16px;text-align:left;border-bottom:1px solid rgba(107,165,208,0.1);}"
    "th{background:linear-gradient(135deg,#6BA5D0,#7FB5DB);color:#FFFFFF;font-weight:600;"
    "text-transform:uppercase;font-size:9pt;letter-spacing:0.5px;}"
    "tbody tr{transition:all 0.2s ease;}"
    "tbody tr:hover{background:rgba(107,165,208,0.08);transform:translateX(2px);}"
    "tbody tr:last-child td{border-bottom:none;}"
    # Badges - Soft Colors
    ".badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:9pt;font-weight:600;letter-spacing:0.3px;}"
    ".prio-high{background:linear-gradient(135deg,#FF6B9D,#FFA07A);color:#FFF;box-shadow:0 2px 8px rgba(255,107,157,0.3);}"
    ".prio-mid{background:linear-gradient(135deg,#FFB347,#FFCC80);color:#FFF;box-shadow:0 2px 8px rgba(255,179,71,0.3);}"
    ".prio-low{background:linear-gradient(135deg,#77DD77,#98D8C8);color:#FFF;box-shadow:0 2px 8px rgba(119,221,119,0.3);}"
    # Dots - Matching Badge Colors
    ".dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);}"
    ".dot-high{background:linear-gradient(135deg,#FF6B9D,#FFA07A);}"
    ".dot-mid{background:linear-gradient(135deg,#FFB347,#FFCC80);}"
    ".dot-low{background:linear-gradient(135deg,#77DD77,#98D8C8);}"
    # Info Boxes - Glassmorphism
    ".note{font-size:9pt;color:#5D6D7E;margin-top:12px;padding:12px 16px;"
    "background:rgba(107,165,208,0.06);border-radius:10px;border-left:3px solid #A7C7E7;}"
    ".header-info{background:linear-gradient(135deg,rgba(167,199,231,0.15),rgba(107,165,208,0.10));"
    "padding:20px;border-radius:16px;margin-bottom:25px;border:1px solid rgba(107,165,208,0.2);"
    "box-shadow:0 4px 16px rgba(107,165,208,0.1);}"
    ".header-info p{margin:8px 0;color:#34495E;font-size:10.5pt;}"
    # Spezial-Zellen
    "td.rates{font-family:'Fira Code','Consolas','Monaco',monospace;font-size:9pt;color:#6BA5D0;font-weight:500;}"
    "td.description{font-size:9.5pt;color:#5D6D7E;max-width:350px;line-height:1.5;word-wrap:break-word;white-space:normal;}"
    "p{word-wrap:break-word;white-space:normal;}"
    ".explanation,.summary,.focus-text{word-wrap:break-word;white-space:normal;line-height:1.6;}"
    # Scrollable Sections
    "div[style*='overflow-y']{border:1px solid rgba(107,165,208,0.15);border-radius:12px;"
    "background:rgba(255,255,255,0.4);box-shadow:inset 0 2px 8px rgba(107,165,208,0.05);}"
    # Print Stylesheet
    "@media print{"
    "body{background:#FFF!important;padding:10px!important;}"
    ".container{background:#FFF!important;box-shadow:none!important;backdrop-filter:none!important;border:none!important;}"
    "h1{font-size:18pt!important;}"
    "h2{font-size:14pt!important;background:#F0F8FF!important;}"
    "h3{font-size:12pt!important;}"
    "table{font-size:9pt!important;box-shadow:none!important;}"
    "th{background:#6BA5D0!important;-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important;}"
    ".badge,.dot{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important;}"
    "}"
    "</style></head><body><div class='container'>"
)

_HTML_FOOT = "</div></body></html>"


def _normalize_tcm_type(raw: str) -> Dict[str, str]:
    result = {
        "code": "",
        "label": "",
        "element": "",
        "organs": "",
    }
    if not raw:
        return result
    s = raw.strip().lower()
    s = s.replace("–", "-").replace("—", "-")
    s_norm = re.sub(r"\s+", " ", s)
    mapping = {
        "holz": ("holz_leber", "Holz – Leber Typ", "Holz", "Leber, Gallenblase"),
        "leber": ("holz_leber", "Holz – Leber Typ", "Holz", "Leber, Gallenblase"),
        "feuer": ("feuer_herz", "Feuer – Herz Typ", "Feuer", "Herz, Dünndarm"),
        "herz": ("feuer_herz", "Feuer – Herz Typ", "Feuer", "Herz, Dünndarm"),
        "erde": ("erde_milz", "Erde – Milz Typ", "Erde", "Milz, Magen"),
        "milz": ("erde_milz", "Erde – Milz Typ", "Erde", "Milz, Magen"),
        "metall": ("metall_lunge", "Metall – Lungen Typ", "Metall", "Lunge, Dickdarm, Haut"),
        "lunge": ("metall_lunge", "Metall – Lungen Typ", "Metall", "Lunge, Dickdarm, Haut"),
        "wasser": ("wasser_niere", "Wasser – Nieren Typ", "Wasser", "Niere, Blase, Knochen"),
        "niere": ("wasser_niere", "Wasser – Nieren Typ", "Wasser", "Niere, Blase, Knochen"),
    }
    for key, val in mapping.items():
        if key in s_norm:
            code, label, elem, organs = val
            return {
                "code": code,
                "label": label,
                "element": elem,
                "organs": organs,
            }
    return {
        "code": "",
        "label": raw.strip(),
        "element": "",
        "organs": "",
    }


def _normalize_planet_type(raw: str) -> Dict[str, str]:
    result = {
        "code": "",
        "label": "",
        "keywords": "",
        "description": "",
    }
    if not raw:
        return result
    s = raw.strip().lower()
    mapping = {
        "sonne": (
            "sonne",
            "Sonne",
            "Lebenskraft, Identität, Selbstvertrauen",
            "Sonne: steht für Lebenskraft, Schöpfung, Selbstvertrauen und Willenskraft.",
        ),
        "sun": (
            "sonne",
            "Sonne",
            "Lebenskraft, Identität, Selbstvertrauen",
            "Sonne: steht für Lebenskraft, Schöpfung, Selbstvertrauen und Willenskraft.",
        ),
        "mond": (
            "mond",
            "Mond",
            "Emotion, Sicherheit, Fruchtbarkeit",
            "Mond: steht für Emotion, Bedürfnis nach Sicherheit und innere Gefühlswelt.",
        ),
        "moon": (
            "mond",
            "Mond",
            "Emotion, Sicherheit, Fruchtbarkeit",
            "Mond: steht für Emotion, Bedürfnis nach Sicherheit und innere Gefühlswelt.",
        ),
        "merkur": (
            "merkur",
            "Merkur",
            "Kommunikation, Denken, Lernen",
            "Merkur: steht für Kommunikation, Denken, Lernen und geistige Beweglichkeit.",
        ),
        "venus": (
            "venus",
            "Venus",
            "Liebe, Beziehungen, Schönheit",
            "Venus: steht für Liebe, Beziehungsgestaltung, Schönheit und Harmonie.",
        ),
        "mars": (
            "mars",
            "Mars",
            "Aktion, Durchsetzung, physische Energie",
            "Mars: steht für Aktion, Durchsetzungskraft, Mut und physische Energie.",
        ),
        "jupiter": (
            "jupiter",
            "Jupiter",
            "Wachstum, Optimismus, Expansion",
            "Jupiter: steht für Wachstum, Optimismus, Sinnsuche und Expansion.",
        ),
        "saturn": (
            "saturn",
            "Saturn",
            "Struktur, Grenze, Verantwortung",
            "Saturn: steht für Struktur, Grenzen, Disziplin und Verantwortung.",
        ),
        "uranus": (
            "uranus",
            "Uranus",
            "Unabhängigkeit, Veränderung, Originalität",
            "Uranus: steht für Unabhängigkeit, plötzliche Veränderungen und Originalität.",
        ),
        "neptun": (
            "neptun",
            "Neptun",
            "Intuition, Spiritualität, Empathie",
            "Neptun: steht für Intuition, Spiritualität, Empathie und Durchlässigkeit.",
        ),
        "pluto": (
            "pluto",
            "Pluto",
            "Transformation, Unterbewusstsein, Macht",
            "Pluto: steht für tiefe Transformation, Unterbewusstsein und Wandlung.",
        ),
    }
    for key, val in mapping.items():
        if s == key or s.startswith(key):
            code, label, keywords, desc = val
            return {
                "code": code,
                "label": label,
                "keywords": keywords,
                "description": desc,
            }
    return {
        "code": "",
        "label": raw.strip(),
        "keywords": "",
        "description": "",
    }


def _build_organ_clock_block(now: Optional[datetime] = None) -> Dict[str, object]:
    if now is None:
        now = datetime.now()
    hour = now.hour
    segment = ""
    organ = ""
    if 3 <= hour < 5:
        segment = "03–05 Lunge"
        organ = "Lunge"
    elif 5 <= hour < 7:
        segment = "05–07 Dickdarm"
        organ = "Dickdarm"
    elif 7 <= hour < 9:
        segment = "07–09 Magen"
        organ = "Magen"
    elif 9 <= hour < 11:
        segment = "09–11 Milz/Pankreas"
        organ = "Milz/Pankreas"
    elif 11 <= hour < 13:
        segment = "11–13 Herz"
        organ = "Herz"
    elif 13 <= hour < 15:
        segment = "13–15 Dünndarm"
        organ = "Dünndarm"
    elif 15 <= hour < 17:
        segment = "15–17 Blase"
        organ = "Blase"
    elif 17 <= hour < 19:
        segment = "17–19 Niere"
        organ = "Niere"
    elif 19 <= hour < 21:
        segment = "19–21 Perikard/Kreislauf"
        organ = "Perikard/Kreislauf"
    elif 21 <= hour < 23:
        segment = "21–23 Dreifacher Erwärmer"
        organ = "Dreifacher Erwärmer"
    elif hour >= 23 or hour < 1:
        segment = "23–01 Gallenblase"
        organ = "Gallenblase"
    elif 1 <= hour < 3:
        segment = "01–03 Leber"
        organ = "Leber"
    return {
        "segment": segment or "neutral",
        "active_organs": [organ] if organ else [],
        "local_time": now.isoformat(),
    }


def _build_image_block(image_signature: object) -> Dict[str, object]:
    present = image_signature is not None
    if not present:
        return {
            "present": False,
            "source": "default",
            "quality": "",
        }
    return {
        "present": True,
        "source": "custom",
        "quality": "",
    }


def _build_influence_factors(
    tcm_type_raw: str,
    planet_type_raw: str,
    image_signature: object,
) -> Dict[str, object]:
    tcm_info = _normalize_tcm_type(tcm_type_raw or "")
    planet_info = _normalize_planet_type(planet_type_raw or "")
    organ_block = _build_organ_clock_block()
    image_block = _build_image_block(image_signature)
    return {
        "tcm": tcm_info,
        "planet": planet_info,
        "organ_clock": organ_block,
        "image": image_block,
    }


def _compute_influence_multiplier_for_item(
    group: str,
    label: str,
    influence_factors: Dict[str, object],
) -> float:
    """Berechnet einen sanften Multiplikator [1.0, 1.03] für ein Item.

    Aktuell werden nur TCM-Typ (Organe) und Organuhr berücksichtigt.
    Es werden ausschließlich passende Organe leicht verstärkt, nichts wird aktiv
    abgewertet.
    """

    base = 1.0
    if not influence_factors:
        return base

    max_delta = 0.03
    delta = 0.0

    tcm_block = influence_factors.get("tcm") or {}
    organ_block = influence_factors.get("organ_clock") or {}

    organ_names: List[str] = []

    tcm_organs_raw = str(tcm_block.get("organs", "") or "").strip()
    if tcm_organs_raw:
        for part in tcm_organs_raw.split(","):
            part_str = part.strip()
            if part_str:
                organ_names.append(part_str)

    active_organs = organ_block.get("active_organs") or []
    if isinstance(active_organs, (list, tuple)):
        for o in active_organs:
            if isinstance(o, str):
                o_str = o.strip()
                if o_str:
                    organ_names.append(o_str)

    if not organ_names:
        return base

    def _norm(s: str) -> str:
        s = (s or "").strip().lower()
        s = (
            s.replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ß", "ss")
        )
        return s

    label_norm = _norm(label)
    group_norm = _norm(group)

    organ_aliases: Dict[str, List[str]] = {
        "niere": ["ren", "kidney"],
        "leber": ["hepar", "hepatis", "liver"],
        "gallenblase": ["vesica biliaris", "gallbladder"],
    }

    for organ_name in organ_names:
        onorm = _norm(organ_name)
        if not onorm:
            continue

        match = False
        if onorm in label_norm or onorm in group_norm:
            match = True
        else:
            aliases = organ_aliases.get(onorm, [])
            for alias in aliases:
                anorm = _norm(alias)
                if not anorm:
                    continue
                if anorm in label_norm or anorm in group_norm:
                    match = True
                    break

        if not match:
            continue

        delta += 0.01
        if delta >= max_delta:
            break

    if delta <= 0.0:
        return base

    if delta > max_delta:
        delta = max_delta
    return base + delta


def _compute_focus_multiplier_for_item(
    focus: str, 
    group: str, 
    label: str,
    item_copen_rate: float = 0.0,
) -> float:
    """Berechnet einen sanften Multiplikator [1.0, 1.15] basierend auf dem Fokus.

    Es werden ausschließlich passende Gruppen/Labels leicht verstärkt; nichts wird
    aktiv abgewertet. Ohne gesetzten Fokus bleibt der Multiplikator 1.0.
    
    ERWEITERT am 01.12.2025: 
    - Zusätzlich zur Keyword-Map wird jetzt auch Copen-Rate-Resonanz berechnet
    - Fokus-Begriffe werden in Copen-Raten umgewandelt
    - Items mit ähnlicher Copen-Rate erhalten einen Resonanz-Bonus
    - max_delta von 0.08 auf 0.15 erhöht (+15% statt +8%)
    """

    base = 1.0
    focus_norm = (focus or "").strip().lower()
    if not focus_norm:
        return base

    def _norm(s: str) -> str:
        s = (s or "").strip().lower()
        s = (
            s.replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ß", "ss")
        )
        return s

    focus_norm = _norm(focus_norm)
    text_norm = _norm(f"{group} {label}")

    # Grobe Zuordnung von Fokus-Schlüsselwörtern zu relevanten Begriffen in
    # Gruppen/Labels. Diese Liste wurde am 30.11.2025 erweitert.
    focus_map: Dict[str, List[str]] = {
        "atmung": ["atmung", "lunge", "bronchien", "respiration"],
        "haut": ["haut", "derma", "narben", "ekzem", "psoriasis"],
        "zahn": ["zahn", "zaehn", "odont", "dental", "kiefer"],
        "schwermetall": ["schwermetall", "schwermetalle", "quecksilber", "blei", "cadmium", "amalgam"],
        "wirbelsaeule": ["wirbelsaeule", "wirbelsaule", "hws", "bws", "lws", "ruecken"],
        "herz-kreislauf": ["herz", "koronar", "kreislauf", "blutdruck", "arterie"],
        "entgiftung": ["entgiftung", "detox", "leber", "niere", "lymphe", "ausleitung"],
        # Neue Kategorien 30.11.2025
        "vergiftung": ["gift", "toxin", "vergiftung", "intoxikation", "belastung"],
        "pestizid": ["pestizid", "herbizid", "insektizid", "glyphosat", "pflanzenschutz"],
        "medikament": ["medikament", "arzneimittel", "nebenwirkung", "interaktion", "pharma"],
        "histamin": ["histamin", "intoleranz", "unvertraeglichkeit", "allergie"],
        "gluten": ["gluten", "zoeliakie", "weizen", "getreide"],
        "laktose": ["laktose", "milch", "dairy", "kasein"],
        "mitochondrien": ["mitochondrien", "atp", "energie", "erschoepfung", "fatigue"],
        "bindegewebe": ["bindegewebe", "faszien", "kollagen", "matrix"],
        "nerv": ["nerv", "neuro", "gehirn", "zns", "vegetativ"],
        "immun": ["immun", "abwehr", "entzuendung", "autoimmun"],
        "darm": ["darm", "mikrobiom", "verdauung", "leaky"],
        "stress": ["stress", "burnout", "erschoepfung", "nebenniere", "cortisol"],
        # Neue Kategorien 01.12.2025 - Sinne
        "sehen": ["auge", "augen", "sehen", "optik", "retina", "makula", "sehnerv"],
        "hoeren": ["ohr", "ohren", "hoeren", "akustik", "tinnitus", "gehoer"],
        "fuehlen": ["haut", "tastsinn", "nerv", "sensorik", "empfindung"],
        "sinne": ["auge", "ohr", "haut", "nase", "zunge", "sensorik"],
    }

    max_delta_keyword = 0.08  # Keyword-basierter Bonus
    max_delta_copen = 0.07    # Copen-Rate-Resonanz-Bonus
    max_delta_total = 0.15    # Maximaler Gesamtbonus
    
    delta_keyword = 0.0
    delta_copen = 0.0

    # === TEIL 1: Keyword-basierte Gewichtung (wie bisher) ===
    for key, synonyms in focus_map.items():
        if key not in focus_norm:
            continue
        for syn in synonyms:
            syn_n = _norm(syn)
            if syn_n and syn_n in text_norm:
                delta_keyword += 0.02
                if delta_keyword >= max_delta_keyword:
                    break
        if delta_keyword >= max_delta_keyword:
            break

    # === TEIL 2: Copen-Rate-Resonanz (NEU 01.12.2025) ===
    # Berechne Copen-Raten für alle Fokus-Begriffe
    if item_copen_rate > 0:
        try:
            avg_focus_rate, focus_rates = focus_to_copen_rates(focus)
            if avg_focus_rate > 0 and focus_rates:
                # Berechne Resonanz zwischen Fokus-Rate und Item-Rate
                # Resonanz = 1 / (1 + |fokus_rate - item_rate| / scale)
                # Je näher die Raten, desto höher die Resonanz
                scale = 1_000_000.0  # Skalierungsfaktor für Copen-Raten
                
                # Beste Resonanz unter allen Fokus-Begriffen finden
                best_resonance = 0.0
                for term, focus_rate in focus_rates.items():
                    if focus_rate > 0:
                        distance = abs(focus_rate - item_copen_rate)
                        resonance = 1.0 / (1.0 + distance / scale)
                        if resonance > best_resonance:
                            best_resonance = resonance
                
                # Resonanz in Bonus umwandeln (0.0 - 0.07)
                # Resonanz von 0.5+ gibt vollen Bonus
                if best_resonance > 0.1:
                    delta_copen = min(max_delta_copen, best_resonance * max_delta_copen * 2)
        except Exception:
            # Bei Fehlern: Kein Copen-Bonus
            pass

    # === Gesamtbonus berechnen ===
    total_delta = delta_keyword + delta_copen
    if total_delta <= 0.0:
        return base
    if total_delta > max_delta_total:
        total_delta = max_delta_total
    
    return base + total_delta


def _render_basic_html(export_data: Dict[str, object]) -> str:
    client = export_data.get("client") or {}
    first_name = str(client.get("first_name", "")).strip()
    last_name = str(client.get("name", "")).strip()
    birth_date = str(client.get("birth_date", "")).strip()
    birth_place = str(client.get("birth_place", "")).strip()

    command = str(export_data.get("command", "")).strip()
    focus = str(export_data.get("focus", "") or "").strip()

    # Unterstütze sowohl alte "metrics" als auch neue "analysis" Struktur
    metrics = export_data.get("metrics") or {}
    analysis = export_data.get("analysis") or {}
    
    m_field = float(analysis.get("morphic_field") or metrics.get("morphic_field", 0.0) or 0.0)
    entropy = float(analysis.get("holographic_entropy") or metrics.get("holographic_entropy", 0.0) or 0.0)
    entropy_cal = float(analysis.get("entropy_calibrated") or metrics.get("entropy_calibrated", entropy) or entropy)
    heim_sig = analysis.get("heim_signature") or metrics.get("heim_signature") or export_data.get("heim_signature") or []
    rates = analysis.get("rates") or metrics.get("rates") or []

    h_level = float(export_data.get("h_level", 0.0) or 0.0)
    hw_profile = str(export_data.get("hardware_profile", "")).strip()
    hw_source = str(export_data.get("hardware_source", "")).strip()

    scores = export_data.get("scores") or []
    top_scores = export_data.get("top_scores") or []
    sub_results = export_data.get("sub_results") or {}
    sub_top = sub_results.get("top") or []

    # Mapping Label -> Copen-Rate (aus den Top-Sub-Ergebnissen),
    # um sie später in der Quantum-Synergy-Sektion kompakt anzuzeigen.
    copen_by_label: Dict[str, float] = {}
    if isinstance(sub_top, list):
        for it in sub_top:
            try:
                lbl = str(it.get("label", "") or "").strip()
                if not lbl:
                    continue
                cr_raw = it.get("copen_rate")
                if cr_raw is None:
                    continue
                cr_val = float(cr_raw)
            except Exception:
                continue
            if cr_val != 0.0 and lbl not in copen_by_label:
                copen_by_label[lbl] = cr_val

    influence = export_data.get("influence_factors") or {}
    tcm_block = influence.get("tcm") or {}
    planet_block = influence.get("planet") or {}
    organ_block = influence.get("organ_clock") or {}
    image_block = influence.get("image") or {}
    influence_scoring = export_data.get("influence_scoring") or {}
    db_analysis_block = export_data.get("db_analysis") or {}
    morphic_field_block = export_data.get("morphic_field") or {}
    morphic_axes_block = export_data.get("morphic_axes") or {}
    if isinstance(db_analysis_block, dict):
        db_summary = db_analysis_block.get("summary") or {}
    else:
        db_summary = {}

    heim_str = ""
    has_heim = False
    if heim_sig:
        has_heim = True
        try:
            heim_str = ", ".join(f"{float(x):.3f}" for x in heim_sig)  # type: ignore[assignment]
        except Exception:
            heim_str = ", ".join(str(x) for x in heim_sig)

    parts: List[str] = []
    parts.append(_HTML_HEAD)
    parts.append(f"<h1>Resonanzanalyse – Report</h1>")
    parts.append(
        f"<p><b>Klient:</b> {first_name} {last_name} – {birth_date}, {birth_place}</p>"
    )
    parts.append(
        f"<p><b>Modus:</b> {command or 'analyze'} | "
        f"<b>Hardware-Profil:</b> {hw_profile or '-'} | "
        f"<b>Quelle:</b> {hw_source or '-'}"  # type: ignore[str-format]
        "</p>"
    )
    summary_line = (
        f"<p><b>Hardware-Level:</b> {h_level:.3f} | "
        f"<b>Morphisches Feld:</b> {m_field:.4f} | "
        f"<b>Entropie(kal):</b> {entropy_cal:.4f}"
    )
    if focus:
        summary_line += f" | <b>Fokus:</b> {focus}"
    summary_line += "</p>"
    parts.append(summary_line)

    # Morphische Feld-Analyse (Übersicht, nur wenn neuer Block vorhanden ist)
    if isinstance(morphic_field_block, dict) and morphic_field_block:
        try:
            mf_strength = float(morphic_field_block.get("field_strength", 0.0) or 0.0)
        except Exception:
            mf_strength = 0.0
        try:
            mf_coherence = float(morphic_field_block.get("coherence", 0.0) or 0.0)
        except Exception:
            mf_coherence = 0.0
        try:
            mf_freq = float(morphic_field_block.get("resonance_frequency", 0.0) or 0.0)
        except Exception:
            mf_freq = 0.0

        parts.append("<h2>Morphische Feld-Analyse (Übersicht, experimentell)</h2>")
        parts.append("<p><b>Feldstärke:</b> " f"{mf_strength:.4f} "
                     "| <b>Kohärenz:</b> " f"{mf_coherence:.3f} "
                     "| <b>Resonanzfrequenz:</b> " f"{mf_freq:.0f} Hz" "</p>")

        if mf_coherence >= 0.66:
            parts.append(
                "<p>Das morphische Feld zeigt eine <b>hohe Kohärenz</b>. "
                "Dies spricht für eine relativ gut abgestimmte Gesamtorganisation "
                "des Klientenfeldes zum Zeitpunkt der Messung.</p>"
            )
        elif mf_coherence >= 0.33:
            parts.append(
                "<p>Das morphische Feld zeigt eine <b>mittlere Kohärenz</b>. "
                "Regulatorische Prozesse sind aktiv; die Harmonisierung kann helfen, "
                "das Feld weiter zu stabilisieren.</p>"
            )
        else:
            parts.append(
                "<p>Das morphische Feld zeigt eine <b>verminderte Kohärenz</b>. "
                "Dies weist auf erhöhte Regulations- und Ausgleichsbedürfnisse hin; "
                "gezielte Harmonisierung und Folgesitzungen werden empfohlen.</p>"
            )

    # Experimentelle Wirbelsäulen- & Zahnachsen-Übersicht (nur wenn Block vorhanden ist)
    if isinstance(morphic_axes_block, dict) and morphic_axes_block.get("enabled"):
        spine_block = morphic_axes_block.get("spine") or {}
        dental_block = morphic_axes_block.get("dental") or {}

        if isinstance(spine_block, dict) and spine_block or isinstance(dental_block, dict) and dental_block:
            parts.append("<h2>Wirbelsäulen- & Zahnachsen (experimentell)</h2>")

        # Wirbelsäule (global + HWS-Schlüsselresonanz)
        if isinstance(spine_block, dict) and spine_block:
            global_spine = spine_block.get("global") or {}
            if isinstance(global_spine, dict) and global_spine:
                try:
                    sp_items = int(global_spine.get("items_total", 0) or 0)
                except Exception:
                    sp_items = 0
                try:
                    sp_max = float(global_spine.get("score_max", 0.0) or 0.0)
                except Exception:
                    sp_max = 0.0
                try:
                    sp_mean = float(global_spine.get("score_mean", 0.0) or 0.0)
                except Exception:
                    sp_mean = 0.0

                parts.append(
                    "<p><b>Wirbelsäule (gesamt):</b> "
                    f"Items: {sp_items} | Max-Score: {sp_max:.2f} | Mittelwert: {sp_mean:.2f}</p>"
                )

            hws_block = spine_block.get("hws") or {}
            if isinstance(hws_block, dict):
                top_hws = hws_block.get("top") or []
                if isinstance(top_hws, list) and top_hws:
                    try:
                        top0 = top_hws[0]
                        lbl = str(top0.get("label", "") or "").strip()
                        try:
                            sc = float(top0.get("score", 0.0) or 0.0)
                        except Exception:
                            sc = 0.0
                        parts.append(
                            "<p><b>HWS (Schlüsselresonanz):</b> "
                            f"{lbl or '-'} (Score {sc:.2f})</p>"
                        )
                    except Exception:
                        pass

        # Zahnachsen (global)
        if isinstance(dental_block, dict) and dental_block:
            global_dental = dental_block.get("global") or {}
            if isinstance(global_dental, dict) and global_dental:
                try:
                    de_items = int(global_dental.get("items_total", 0) or 0)
                except Exception:
                    de_items = 0
                try:
                    de_max = float(global_dental.get("score_max", 0.0) or 0.0)
                except Exception:
                    de_max = 0.0
                try:
                    de_mean = float(global_dental.get("score_mean", 0.0) or 0.0)
                except Exception:
                    de_mean = 0.0

                parts.append(
                    "<p><b>Zahnachsen (gesamt):</b> "
                    f"Items: {de_items} | Max-Score: {de_max:.2f} | Mittelwert: {de_mean:.2f}</p>"
                )

    influence_lines: List[str] = []
    tcm_label = str(tcm_block.get("label", "")).strip()
    tcm_elem = str(tcm_block.get("element", "")).strip()
    if tcm_label or tcm_elem:
        if tcm_elem and tcm_label:
            influence_lines.append(
                f"<b>TCM-Typ:</b> {tcm_label} (Element {tcm_elem})"
            )
        elif tcm_label:
            influence_lines.append(f"<b>TCM-Typ:</b> {tcm_label}")
    planet_label = str(planet_block.get("label", "")).strip()
    planet_desc = str(planet_block.get("description", "")).strip()
    if planet_label:
        if planet_desc:
            influence_lines.append(
                f"<b>Planetentyp:</b> {planet_label} – {planet_desc}"
            )
        else:
            influence_lines.append(f"<b>Planetentyp:</b> {planet_label}")
    organ_segment = str(organ_block.get("segment", "")).strip()
    if organ_segment:
        influence_lines.append(f"<b>Organuhr:</b> {organ_segment}")
    img_present = bool(image_block.get("present", False))
    img_source = str(image_block.get("source", "")).strip() or "default"
    if img_present:
        influence_lines.append(
            f"<b>Bildsignatur:</b> gesetzt (Quelle: {img_source})"
        )
    else:
        influence_lines.append("<b>Bildsignatur:</b> nicht gesetzt")

    influence_enabled = bool((influence_scoring or {}).get("enabled"))
    if influence_enabled:
        organs_summary: List[str] = []
        tcm_orgs_text = str(tcm_block.get("organs", "") or "").strip()
        if tcm_orgs_text:
            for part in tcm_orgs_text.split(","):
                part_str = part.strip()
                if part_str:
                    organs_summary.append(part_str)
        active_orgs_html = organ_block.get("active_organs") or []
        if isinstance(active_orgs_html, (list, tuple)):
            for o in active_orgs_html:
                if isinstance(o, str):
                    o_str = o.strip()
                    if o_str:
                        organs_summary.append(o_str)
        uniq_orgs_html: List[str] = []
        seen_html: set[str] = set()
        for o in organs_summary:
            if not o:
                continue
            if o not in seen_html:
                seen_html.add(o)
                uniq_orgs_html.append(o)
        if uniq_orgs_html:
            try:
                max_delta_val = float((influence_scoring or {}).get("max_delta", 0.0) or 0.0)
                max_pct_val = int(round(max_delta_val * 100.0))
                if max_pct_val <= 0:
                    max_pct_val = 3
            except Exception:
                max_pct_val = 3
            joined_orgs = ", ".join(uniq_orgs_html)
            influence_lines.append(
                f"<i>Influence-Scoring aktiv (max. +{max_pct_val}% für Items zu: {joined_orgs}).</i>"
            )

    if influence_lines:
        parts.append("<h2>Einflussfaktoren</h2>")
        for line in influence_lines:
            parts.append(f"<p>{line}</p>")
    
    # === DEUTUNG DES GEZEIGTEN LAUFS (wie in alten Berichten) ===
    parts.append("<h2>Deutung des gezeigten Laufs</h2>")
    deutung_lines: List[str] = []
    if focus:
        deutung_lines.append(f"Fokus: {focus}")
        deutung_lines.append("")

    if top_scores:
        deutung_lines.append("Höchste Resonanzen")
        try:
            top_for_text = top_scores[:5]
        except Exception:
            top_for_text = top_scores
        label_score_parts = []
        for entry in top_for_text:
            try:
                lbl = str(entry.get("label", ""))  # type: ignore[assignment]
                val = float(entry.get("score", 0.0) or 0.0)  # type: ignore[assignment]
            except Exception:
                continue
            label_score_parts.append(f"{lbl} ({val:.2f})")
        if label_score_parts:
            deutung_lines.append(", ".join(label_score_parts) + " sind aktuell führend.")

    if sub_top:
        group_buckets: Dict[str, List[Dict[str, object]]] = {}
        for it in sub_top:
            g = str(it.get("group", "") or "")
            group_buckets.setdefault(g, []).append(it)

        cat_defs: List[tuple[str, List[str] | None, str]] = [
            ("Herz/Kreislauf", ["kreislauf"], "sind wiederholt präsent."),
            (
                "Meridiane / Chakren",
                [
                    "meridiane",
                    "tcm_punkte",
                    "tcm_punkte_extended",
                    "tcm_full",
                    "extra_meridiane",
                    "chakren",
                    "chakren_erweitert",
                    "chakren_full",
                    "nebenchakren",
                ],
                "zeigen erhöhte Resonanz.",
            ),
            (
                "Mikroorganismen",
                [
                    "bakterien",
                    "bakterien_fein",
                    "viren",
                    "viren_fein",
                    "parasiten",
                    "parasiten_fein",
                    "pilze",
                    "pilze_fein",
                ],
                "sind im aktuellen Lauf hervorgehoben. Vorgehen: Zielgruppen-Replikation und Feinscan; nur konsolidierte Treffer behandeln.",
            ),
            (
                "Toxische Belastungen",
                [
                    "schwermetalle",
                    "schwermetalle_tox",
                    "strahlung_tox",
                    "pestizide_tox",
                    "chemikalien_tox",
                    "emf_fein",
                    "geopathie",
                ],
                "weisen auf relevante Belastungen hin. Vorgehen: Separater Schwermetall-Scan zur Verifikation, Entgiftung einleiten.",
            ),
            (
                "Regulation & Systeme",
                [
                    "endokrin",
                    "detox",
                    "mikrozirkulation",
                    "mitochondrien",
                    "entzuendung",
                    "allergene",
                    "mikronaehrstoffe",
                    "wirbelsaeule",
                    "schlaf",
                ],
                "zeigen Regulationsbedarf. Empfehlung: Grundregulation stärken, Mikronährstoffe prüfen.",
            ),
            (
                "Zahn-Organ-System",
                [
                    "zahnorgane",
                    "odontone",
                ],
                "können Störfelder oder Organverbindungen anzeigen. Empfehlung: Zahnärztliche Kontrolle, Herddiagnostik.",
            ),
            (
                "Homöopathie / TCM / Spagyrik",
                [
                    "homoeopathie_klassisch",
                    "homoeopathie_klassisch_potenzen",
                    "tcm_rezepturen",
                    "tcm_rezepturen_potenzen",
                    "spagyrik",
                ],
                "können als Richtungsanzeige für Mittelwahl und Regulation dienen. Empfehlung: Konstitutionelle Behandlung erwägen.",
            ),
            (
                "Komplementäre Therapien",
                [
                    "farbtherapie",
                    "edelsteine",
                    "laser_protokolle",
                    "rife_cafl_proc",
                    "baklayan_proc",
                ],
                "bieten ergänzende Therapieoptionen.",
            ),
            ("Weitere Systeme", None, "zeigen ergänzende Resonanzmuster."),
        ]

        covered_groups: set[str] = set()
        for _, groups_for_cat, _ in cat_defs:
            if groups_for_cat is None:
                continue
            for g in groups_for_cat:
                covered_groups.add(g)

        def _collect_items(groups_for_cat: List[str] | None) -> List[Dict[str, object]]:
            items: List[Dict[str, object]] = []
            if groups_for_cat is None:
                for g, bucket in group_buckets.items():
                    if g not in covered_groups:
                        items.extend(bucket)
            else:
                for g in groups_for_cat:
                    items.extend(group_buckets.get(g, []))
            items_sorted = sorted(
                items,
                key=lambda e: float(e.get("score", 0.0) or 0.0),
                reverse=True,
            )
            return items_sorted

        for heading, groups_for_cat, tail in cat_defs:
            items_sorted = _collect_items(groups_for_cat)
            if not items_sorted:
                continue
            label_score_parts_cat: List[str] = []
            seen_labels_cat: set[str] = set()
            for it in items_sorted:
                try:
                    lbl = str(it.get("label", ""))
                    if not lbl:
                        continue
                    s_val = float(it.get("score", 0.0) or 0.0)
                except Exception:
                    continue
                if lbl in seen_labels_cat:
                    continue
                seen_labels_cat.add(lbl)
                label_score_parts_cat.append(f"{lbl} ({s_val:.2f})")
                if len(label_score_parts_cat) >= 3:
                    break
            if not label_score_parts_cat:
                continue
            deutung_lines.append(heading)
            deutung_lines.append(", ".join(label_score_parts_cat) + " " + tail)
    sections_for_text = export_data.get("sections") or []
    sub_results_for_text = export_data.get("sub_results") or {}
    has_fallback_items = bool(getattr(sub_results_for_text, "get", lambda _k, _d=None: None)("top"))
    if sections_for_text or has_fallback_items:
        def _is_remedy_group_name(g: str) -> bool:
            # Verwendet zentrale Registry - keine lokale Logik mehr nötig!
            return _central_is_remedy_group(g)

        items_for_text: List[Dict[str, object]] = []
        if sections_for_text:
            for sec in sections_for_text:
                try:
                    entries = sec.get("entries") or []  # type: ignore[assignment]
                except Exception:
                    continue
                for it in entries:
                    try:
                        lbl = str(it.get("label", "") or "")
                        if not lbl:
                            continue
                        prio = str(it.get("priority", "") or "").lower()
                        if prio not in ("hoch", "mittel"):
                            continue
                        grp = str(it.get("group", "") or "")
                        float(it.get("score", 0.0) or 0.0)
                    except Exception:
                        continue
                    items_for_text.append(it)
        else:
            sub_top_ft = sub_results_for_text.get("top") or []  # type: ignore[assignment]
            if isinstance(sub_top_ft, list) and sub_top_ft:
                try:
                    max_score_ft = max(
                        float(e.get("score", 0.0) or 0.0) for e in sub_top_ft
                    )
                except Exception:
                    max_score_ft = 0.0
                for it in sub_top_ft:
                    try:
                        lbl = str(it.get("label", "") or "")
                        if not lbl:
                            continue
                        s_val = float(it.get("score", 0.0) or 0.0)
                    except Exception:
                        continue
                    rel = s_val / max_score_ft if max_score_ft > 0.0 else 0.0
                    if rel >= 0.66:
                        prio_txt = "hoch"
                    elif rel >= 0.33:
                        prio_txt = "mittel"
                    else:
                        prio_txt = "niedrig"
                    if prio_txt not in ("hoch", "mittel"):
                        continue
                    item_copy = dict(it)
                    item_copy["priority"] = prio_txt
                    items_for_text.append(item_copy)

        load_items: List[Dict[str, object]] = []
        remedy_items: List[Dict[str, object]] = []
        for it in items_for_text:
            try:
                lbl = str(it.get("label", "") or "")
                if not lbl:
                    continue
                grp = str(it.get("group", "") or "")
                float(it.get("score", 0.0) or 0.0)
            except Exception:
                continue
            if _is_remedy_group_name(grp):
                remedy_items.append(it)
            else:
                load_items.append(it)

        def _select_top_unique(items: List[Dict[str, object]], limit: int = 5) -> List[Dict[str, object]]:
            try:
                items_sorted = sorted(
                    items,
                    key=lambda e: float(e.get("score", 0.0) or 0.0),
                    reverse=True,
                )
            except Exception:
                items_sorted = items
            seen_labels: set[str] = set()
            result: List[Dict[str, object]] = []
            for it in items_sorted:
                try:
                    lbl = str(it.get("label", "") or "")
                except Exception:
                    continue
                if not lbl or lbl in seen_labels:
                    continue
                seen_labels.add(lbl)
                result.append(it)
                if len(result) >= limit:
                    break
            return result

        top_loads = _select_top_unique(load_items)
        if top_loads:
            parts_load: List[str] = []
            for it in top_loads:
                try:
                    lbl = str(it.get("label", "") or "")
                    s_val = float(it.get("score", 0.0) or 0.0)
                    prio_txt = str(it.get("priority", "") or "")
                except Exception:
                    continue
                if not lbl:
                    continue
                parts_load.append(f"{lbl} ({s_val:.2f}, {prio_txt})")
            if parts_load:
                deutung_lines.append("Top-Belastungen (hohe/mittlere Priorität)")
                deutung_lines.append(", ".join(parts_load) + " sollten im Verlauf besonders beachtet werden.")

        top_remedies = _select_top_unique(remedy_items)
        if top_remedies:
            parts_rem: List[str] = []
            for it in top_remedies:
                try:
                    lbl = str(it.get("label", "") or "")
                    s_val = float(it.get("score", 0.0) or 0.0)
                    prio_txt = str(it.get("priority", "") or "")
                except Exception:
                    continue
                if not lbl:
                    continue
                parts_rem.append(f"{lbl} ({s_val:.2f}, {prio_txt})")
            if parts_rem:
                deutung_lines.append("Top-Remedies (hohe/mittlere Priorität)")
                deutung_lines.append(", ".join(parts_rem) + " bieten vorrangige Ansatzpunkte für Harmonisierung und Therapie.")

    deutung_lines.append("Vorgehen")
    deutung_lines.append(
        "Die aufgeführten Resonanzen sollten im Kontext des Fokus und der klinischen Situation "
        "überprüft und bei Bedarf in einem Feinscan vertieft werden."
    )
    parts.append("<pre>" + "\n".join(deutung_lines) + "</pre>")

    groups_used = sub_results.get("groups") if isinstance(sub_results, dict) else None
    if groups_used:
        try:
            groups_txt = ", ".join(str(g) for g in groups_used)
        except Exception:
            groups_txt = str(groups_used)
        parts.append("<h3>Verwendete Subgruppen</h3>")
        parts.append(f"<p>{groups_txt}</p>")

    if focus:
        parts.append("<h2>Fokus / Symptom</h2>")
        parts.append(f"<p>{focus}</p>")

    # === RESONANZANALYSE SEKTION (wie in alten Berichten) ===
    parts.append("<h2>Resonanzanalyse</h2>")
    
    # === BASIS-METRIKEN (exakt wie alte Berichte) ===
    parts.append("<h3>Basis‑Metriken</h3>")
    try:
        if rates:
            rates_str = "[ " + "  ".join(f"{float(x):.2f}" for x in rates[:9]) + " ]"
        else:
            rates_str = "[]"
    except Exception:
        rates_str = str(rates)
    
    heim_str_formatted = "[ " + "  ".join(f"{float(x):.2f}" for x in heim_sig[:4]) + " ]" if heim_sig else "[]"
    
    parts.append(
        "<p>"
        f"<b>Raten:</b> {rates_str}<br>"
        f"<b>Morphisches Feld:</b> {m_field:.4f} | "
        f"<b>Entropie (roh):</b> {entropy:.4f} | "
        f"<b>Entropie (kal):</b> {entropy_cal:.4f}<br>"
        f"<b>Heim‑Signatur:</b> {heim_str_formatted}"
        "</p>"
    )

    # === RESONANZWERTE TABELLE (wie in alten Berichten) ===
    resonance_map = analysis.get("resonance_map") or {}
    if resonance_map:
        parts.append("<h3>Resonanzwerte</h3>")
        parts.append("<table><tr><th>System</th><th>Score</th><th>Priorität</th></tr>")
        max_resonance = max(resonance_map.values()) if resonance_map else 1.0
        
        for system, score_val in resonance_map.items():
            try:
                score_val = float(score_val)
                system_name = system.replace("_", " ").title()
                rel = score_val / max_resonance if max_resonance > 0.0 else 0.0
                if rel >= 0.66:
                    prio_cls = "prio-high"
                    prio_txt = "hoch"
                elif rel >= 0.33:
                    prio_cls = "prio-mid"
                    prio_txt = "mittel"
                else:
                    prio_cls = "prio-low"
                    prio_txt = "niedrig"
                parts.append(
                    f"<tr><td>{system_name}</td><td>{score_val:.4f}</td>"
                    f"<td><span class='badge {prio_cls}'>{prio_txt}</span></td></tr>"
                )
            except Exception:
                continue
        parts.append("</table>")
        parts.append(
            "<p class='note'>Priorität bezieht sich auf die relative Höhe des jeweiligen Scores "
            "innerhalb der Resonanzwerte dieses Laufs (hoch ≥ 66%, mittel 33–66%, niedrig &lt; 33%).</p>"
        )
    
    # Zeige auch Top-Scores wenn vorhanden und verschieden von resonance_map
    if top_scores and not resonance_map:
        parts.append("<h3>Resonanzwerte (Top)</h3>")
        parts.append("<table><tr><th>Label</th><th>Score</th><th>Priorität</th></tr>")
        max_score = 0.0
        for entry in top_scores:
            try:
                s_val = float(entry.get("score", 0.0) or 0.0)  # type: ignore[assignment]
            except Exception:
                continue
            if s_val > max_score:
                max_score = s_val

        for entry in top_scores:
            try:
                label = str(entry.get("label", ""))  # type: ignore[assignment]
                score_val = float(entry.get("score", 0.0) or 0.0)  # type: ignore[assignment]
            except Exception:
                continue
            rel = score_val / max_score if max_score > 0.0 else 0.0
            if rel >= 0.66:
                prio_cls = "prio-high"
                prio_txt = "hoch"
            elif rel >= 0.33:
                prio_cls = "prio-mid"
                prio_txt = "mittel"
            else:
                prio_cls = "prio-low"
                prio_txt = "niedrig"
            parts.append(
                f"<tr><td>{label}</td><td>{score_val:.4f}</td>"
                f"<td><span class='badge {prio_cls}'>{prio_txt}</span></td></tr>"
            )
        parts.append("</table>")
        parts.append(
            "<p class='note'>Priorität bezieht sich auf die relative Höhe des jeweiligen Scores "
            "innerhalb der Resonanzwerte dieses Laufs (hoch ≥ 66%, mittel 33–66%, niedrig &lt; 33%).</p>"
        )

    # Optionale Bruce-Copen-DB-Analyse im HTML, basierend auf db_analysis.summary
    if isinstance(db_summary, dict) and db_summary.get("resonance_count"):
        try:
            items_total = int(db_summary.get("items_total", 0) or 0)
        except Exception:
            items_total = 0
        try:
            res_count = int(db_summary.get("resonance_count", 0) or 0)
        except Exception:
            res_count = 0

        res_max_raw = db_summary.get("resonance_max")
        res_min_raw = db_summary.get("resonance_min")
        res_mean_raw = db_summary.get("resonance_mean")
        try:
            res_mean_val = float(res_mean_raw) if res_mean_raw is not None else None
        except Exception:
            res_mean_val = None

        parts.append("<h3>Bruce-Copen-DB-Analyse (experimentell)</h3>")
        summary_txt_parts: List[str] = []
        summary_txt_parts.append(
            f"Items mit berechneter Resonanz: {res_count} von {items_total}."
        )
        if res_mean_val is not None:
            summary_txt_parts.append(
                f"Mittlere Resonanz: {res_mean_val:.1f} / 100."
            )
        parts.append("<p>" + " ".join(summary_txt_parts) + "</p>")

        top_res = db_summary.get("top_resonance") or []
        if isinstance(top_res, list) and top_res:
            parts.append("<ul>")
            for entry in top_res:
                try:
                    label_tr = str(entry.get("label", "") or "").strip()
                    group_tr = str(entry.get("group", "") or "").strip()
                    score_tr_raw = entry.get("resonance_score")
                    score_tr = float(score_tr_raw) if score_tr_raw is not None else 0.0
                except Exception:
                    continue
                label_disp = label_tr or "-"
                if group_tr:
                    line = f"{label_disp} [{group_tr}] – Resonanz {score_tr:.1f} / 100"
                else:
                    line = f"{label_disp} – Resonanz {score_tr:.1f} / 100"
                parts.append(f"<li>{line}</li>")
            parts.append("</ul>")

        parts.append(
            "<p><i>Basierend auf Bruce-Copen-DB-Analyse; experimentell, ohne Einfluss auf NLS-Scores.</i></p>"
        )

    synergy_results: List[Dict[str, object]] = []
    synergy_flags: Dict[str, float] = {}

    if sub_top:
        # Baue Remedy-Pool (nur Remedy-Gruppen gemäß _is_remedy_group)
        # NEU: Max 5 Items pro Gruppe, um Dominanz einzelner Gruppen zu vermeiden
        remedy_pool: List[Dict[str, object]] = []
        group_counts: Dict[str, int] = {}
        MAX_ITEMS_PER_GROUP = 5
        
        # Sortiere nach Score absteigend, um die besten Items pro Gruppe zu nehmen
        sorted_items = sorted(sub_top, key=lambda x: float(x.get("score", 0.0) or 0.0), reverse=True)
        
        for it in sorted_items:
            try:
                g = str(it.get("group", "") or "")
            except Exception:
                continue
            if _is_remedy_group(g):
                # Prüfe ob Gruppe schon MAX_ITEMS_PER_GROUP erreicht hat
                current_count = group_counts.get(g, 0)
                if current_count < MAX_ITEMS_PER_GROUP:
                    remedy_pool.append(it)
                    group_counts[g] = current_count + 1

        if len(remedy_pool) >= 2:
            try:
                # Bis zu 10 relevante Remedy-Kombinationen auswerten
                synergy_results = analyze_remedy_synergies(remedy_pool, max_results=10)
            except Exception:
                synergy_results = []

        # Map für schnelle Markierung synergetischer Remedies aufbauen
        for syn in synergy_results or []:
            try:
                main_label = str(syn.get("label", "") or "")
                partners = syn.get("synergies", []) or []
            except Exception:
                continue
            max_partner = 0.0
            for p in partners:
                try:
                    pl = str(p.get("partner_label", "") or "")
                    ps = float(p.get("synergy_score", 0.0) or 0.0)
                except Exception:
                    continue
                if not pl:
                    continue
                if ps > max_partner:
                    max_partner = ps
                prev = synergy_flags.get(pl, 0.0)
                if ps > prev:
                    synergy_flags[pl] = ps
            if main_label and max_partner > 0.0:
                prev = synergy_flags.get(main_label, 0.0)
                if max_partner > prev:
                    synergy_flags[main_label] = max_partner

    if sub_top:
        parts.append("<h2>Fullbody-Subgruppen – multiplex</h2>")
        
        # Gruppiere Items nach Kategorien wie in alten Berichten
        group_buckets: Dict[str, List[Dict[str, object]]] = {}
        max_sub_score = 0.0
        
        for it in sub_top:
            try:
                s_val = float(it.get("score", 0.0) or 0.0)
                if s_val > max_sub_score:
                    max_sub_score = s_val
                    
                group = str(it.get("group", "") or "andere")
                if group not in group_buckets:
                    group_buckets[group] = []
                group_buckets[group].append(it)
            except Exception:
                continue
        
        # Definiere Gruppen-Reihenfolge und Titel
        group_order = [
            ("bakterien", "Bakterien", "Bakterielle Belastungen – Feinscan empfohlen"),
            ("bakterien_fein", "Bakterien (detailliert)", "Spezifische bakterielle Erreger"),
            ("viren", "Viren", "Virale Belastungen – Immunsystem stärken"),
            ("viren_fein", "Viren (detailliert)", "Spezifische virale Erreger"),
            ("parasiten", "Parasiten", "Parasitäre Belastungen – Darmreinigung"),
            ("parasiten_fein", "Parasiten (detailliert)", "Spezifische Parasiten"),
            ("pilze", "Pilze", "Pilzbelastungen – Darmmilieu regulieren"),
            ("pilze_fein", "Pilze (detailliert)", "Spezifische Pilzerreger"),
            ("schwermetalle", "Schwermetalle", "Toxische Metalle – Entgiftung einleiten"),
            ("schwermetalle_tox", "Schwermetalle (erweitert)", "Detaillierte Metallbelastung"),
            ("meridiane", "Meridiane", "Energieleitbahnen – Akupunktur/TCM"),
            ("tcm_punkte", "TCM-Punkte", "Spezifische Akupunkturpunkte"),
            ("tcm_punkte_extended", "TCM-Punkte (erweitert)", "Erweiterte Punktauswahl"),
            ("chakren", "Chakren", "Energiezentren – energetische Harmonisierung"),
            ("chakren_full", "Chakren (vollständig)", "Alle Hauptchakren"),
            ("chakren_erweitert", "Chakren (erweitert)", "Zusätzliche Energiezentren"),
            ("nebenchakren", "Nebenchakren", "Sekundäre Energiezentren"),
            ("homoeopathie_klassisch", "Homöopathie", "Klassische Mittel – nach Konstitution"),
            ("homoeopathie_klassisch_potenzen", "Homöopathie (Potenzen)", "Potenzierte Mittel"),
            ("tcm_rezepturen", "TCM-Rezepturen", "Traditionelle chinesische Formeln"),
            ("tcm_rezepturen_potenzen", "TCM-Rezepturen (Potenzen)", "Potenzierte TCM-Formeln"),
            ("spagyrik", "Spagyrik", "Alchemistische Essenzen"),
            ("zahnorgane", "Zahn-Organ-System", "Störfelder und Organverbindungen"),
            ("odontone", "Odontone", "Zahnbezogene Resonanzen"),
            ("endokrin", "Endokrines System", "Hormonelle Regulation"),
            ("detox", "Entgiftung", "Entgiftungsorgane und -wege"),
            ("mikrozirkulation", "Mikrozirkulation", "Durchblutung auf Zellebene"),
            ("mitochondrien", "Mitochondrien", "Zelluläre Energieproduktion"),
            ("entzuendung", "Entzündung", "Entzündungsmarker und -regulation"),
            # Hersteller-spezifische Remedy-Gruppen (NEU)
            ("heel_remedies_multiplex", "Heel Homotoxikologie", "Biologische Komplexmittel nach Dr. Reckeweg"),
            ("nutramedix_remedies_multiplex", "Nutramedix Phytotherapie", "Pflanzliche Extrakte für Borreliose & Entgiftung"),
            ("schuessler_remedies_multiplex", "Schüssler-Salze", "Biochemische Mineralsalze nach Dr. Schüßler"),
            # OOREP Klassische Homöopathie (2432 Einzelmittel)
            ("oorep_homeopathy_multiplex", "OOREP Klassische Homöopathie", "2432 Einzelmittel nach Kent, Boericke, Hahnemann"),
            ("andere", "Weitere Systeme", "Zusätzliche Resonanzmuster"),
        ]

        group_meta_lookup = {key: (title, desc) for key, title, desc in group_order}
        rendered_group_keys: set[str] = set()

        def _render_group_block(group_key: str, group_title: str, group_description: str) -> None:
            items = group_buckets.get(group_key)
            if not items:
                return

            # Sortiere Items nach Score und entferne doppelte Labels pro Gruppe
            items.sort(key=lambda x: float(x.get("score", 0.0) or 0.0), reverse=True)
            unique_items: List[Dict[str, object]] = []
            seen_labels: set[str] = set()
            for entry in items:
                label = str(entry.get("label", "")).strip()
                if not label or label in seen_labels:
                    continue
                seen_labels.add(label)
                unique_items.append(entry)

            if not unique_items:
                return
            
            # NEU: Begrenze auf max 30 Items pro Gruppe (außer wenn >30 hoch/mittelpriore)
            MAX_ITEMS_PER_SUBGROUP = 30
            if len(unique_items) > MAX_ITEMS_PER_SUBGROUP:
                # Zähle hoch/mittelpriore Items (Score >= 33% des Gruppen-Max)
                temp_max = max((float(it.get("score", 0.0) or 0.0) for it in unique_items), default=0.0)
                high_mid_count = sum(1 for it in unique_items 
                                    if float(it.get("score", 0.0) or 0.0) >= temp_max * 0.33)
                # Nur begrenzen wenn nicht mehr als 30 hoch/mittelpriore Items
                if high_mid_count <= MAX_ITEMS_PER_SUBGROUP:
                    unique_items = unique_items[:MAX_ITEMS_PER_SUBGROUP]

            group_max_score = max(
                (float(it.get("score", 0.0) or 0.0) for it in unique_items),
                default=0.0,
            )

            all_rates: List[float] = []
            for rit in unique_items:
                try:
                    rv = rit.get("rates") or []
                    for x in rv:
                        all_rates.append(float(x))
                except Exception:
                    continue

            rendered_group_keys.add(group_key)

            parts.append(f"<h3>{group_title}</h3>")
            parts.append(f"<p class='note'>{group_description}</p>")
            
            # Scrollbarer Container bei vielen Items (>15)
            if len(unique_items) > 15:
                parts.append("<div style='max-height:400px; overflow-y:auto; border:1px solid #ddd; border-radius:4px;'>")
            
            parts.append(
                "<table><tr>"
                "<th>Label</th><th>Score</th><th>Intensität (global/gruppe)</th>"
                "<th>Potenz</th><th>Ebene</th><th>Raten</th><th>Priorität</th><th>Beschreibung</th>"
                "</tr>"
            )

            for it in unique_items:
                try:
                    label = str(it.get("label", ""))
                    score_val = float(it.get("score", 0.0) or 0.0)
                except Exception:
                    continue
                if not label:
                    continue

                # Globale Intensität relativ zum stärksten Fullbody-Treffer
                intensity_global = score_val / max_sub_score if max_sub_score > 0.0 else 0.0
                potency = str(it.get("potency", "") or "-")
                level = str(it.get("level", "") or "-")

                rates_vals = it.get("rates") or []
                copen_val = it.get("copen_rate")
                try:
                    if rates_vals:
                        rates_str = f"[ {float(rates_vals[0]):.2f} - {float(rates_vals[1]):.2f} ]"
                    else:
                        rates_str = "[]"
                except Exception:
                    rates_str = str(rates_vals)

                # Copen-Rate kompakt in derselben Zeile anzeigen, um die Zeilenhöhe konstant zu halten
                try:
                    if copen_val is not None:
                        rates_str = f"{rates_str} (Copen: {float(copen_val):.0f})"
                except Exception:
                    pass

                # Gruppenbezogene Intensität relativ zum Gruppen-Maximum
                rel = score_val / group_max_score if group_max_score > 0.0 else 0.0
                intensity_group = rel
                prio_level = max(1, min(10, int(rel * 10) + 1))  # 1-10 Skala
                
                # Farbe basierend auf Level
                if prio_level >= 8:
                    prio_cls = "prio-high"
                elif prio_level >= 5:
                    prio_cls = "prio-mid"
                else:
                    prio_cls = "prio-low"
                prio_txt = str(prio_level)

                # Synergie-Markierung für Remedies (⚡)
                synergy_mark = ""
                try:
                    syn_score = float(synergy_flags.get(label, 0.0) or 0.0)
                    if syn_score > 0.0:
                        synergy_mark = " ⚡"
                except Exception:
                    synergy_mark = ""

                description = get_description(label) if DESCRIPTIONS_AVAILABLE else None
                desc_text = description[:60] + "..." if description and len(description) > 60 else (description or "-")

                parts.append(
                    f"<tr><td>{label}{synergy_mark}</td><td>{score_val:.4f}</td>"
                    f"<td>{intensity_global:.2f} / {intensity_group:.2f}</td><td>{potency}</td><td>{level}</td>"
                    f"<td class='rates'>{rates_str}</td>"
                    f"<td><span class='badge {prio_cls}'>{prio_txt}</span></td>"
                    f"<td class='note' style='font-size:11px;'>{desc_text}</td></tr>"
                )

            parts.append("</table>")

            if all_rates:
                try:
                    min_rate = min(all_rates)
                    max_rate = max(all_rates)
                    avg_rate = sum(all_rates) / len(all_rates)
                    parts.append(
                        "<p class='note' style='font-size:11px; color:#888;'>"
                        f"<strong>Kombinierte Raten:</strong> [ {min_rate:.2f} - {max_rate:.2f} ], Ø {avg_rate:.2f}"
                        "</p>"
                    )
                except Exception:
                    pass
            
            # Schließe Scroll-Container falls geöffnet
            if len(unique_items) > 15:
                parts.append("</div>")
            
            parts.append(
                "<p class='note' style='font-size:10px; color:#555; margin-top:4px; padding:4px; background:#f9f9f9; border-left:3px solid #5cb85c;'>"
                "<strong>📊 Score & Intensität:</strong> Score = Absolute Resonanzstärke (0-10). Intensität: erster Wert relativ zum stärksten Fullbody-Treffer "
                f"(global, Max: {max_sub_score:.2f}), zweiter Wert relativ zum Gruppen-Maximum (lokal, Max: {group_max_score:.2f}). "
                "<strong>Priorität:</strong> Level 1-10 relativ zum Gruppen-Maximum, wobei 10 = höchste Priorität. "
                "<strong>Interpretation:</strong> Score &gt;7 = sehr hoch, 5-7 = hoch, 3-5 = mittel, 1-3 = niedrig, &lt;1 = sehr niedrig. "
                "Intensität &gt;0.8 = sehr stark, 0.6-0.8 = stark, 0.4-0.6 = mittel, 0.2-0.4 = schwach, &lt;0.2 = sehr schwach. "
                "Priorität: 10-8 = sehr hoch (rot), 7-5 = mittel (orange), 4-1 = niedrig (grün)."
                "</p>"
            )
            parts.append("<br>")

        # Rendere alle bekannten Gruppen in definierter Reihenfolge
        for group_key, group_title, group_description in group_order:
            _render_group_block(group_key, group_title, group_description)

        # Füge alle weiteren Gruppen (aus dem Multiplex-Profil) hinzu
        remaining_keys = sorted(
            key for key in group_buckets.keys() if key not in rendered_group_keys
        )
        for group_key in remaining_keys:
            title, desc = group_meta_lookup.get(
                group_key,
                (group_key.replace("_", " ").title(), "Spezifische Resonanzgruppe"),
            )
            _render_group_block(group_key, title, desc)
        parts.append(
            "<p class='note'>Intensität ist relativ zum stärksten Fullbody-Treffer dieses Laufs skaliert "
            "(1.00 = höchster Score).</p>"
        )
        
        # === SYNERGIE-ANALYSE SEKTION ===
        if synergy_results:
            try:
                parts.append("<h2>⚡ Synergetische Remedy-Kombinationen (Rate-Overlap-Analyse)</h2>")
                parts.append(
                    "<p class='note'>Basierend auf Frequenz-Ähnlichkeit. Es werden nur Remedies aus den entsprechenden Remedy-Gruppen (Homöopathie/TCM-Rezepturen/Spagyrik/etc.) berücksichtigt.</p>"
                )
                parts.append(
                    "<table><tr>"
                    "<th>Remedy</th><th>Score</th><th>Raten</th><th>⚡ Synergien</th><th>Synergie-Score</th>"
                    "</tr>"
                )

                for syn_item in synergy_results[:10]:
                    label = syn_item.get("label", "")
                    score = float(syn_item.get("score", 0.0) or 0.0)
                    rates = syn_item.get("rates", [])
                    synergies = syn_item.get("synergies", [])
                    copen_rate = syn_item.get("copen_rate")

                    try:
                        if len(rates) >= 2:
                            rates_str = f"[ {float(rates[0]):.2f} - {float(rates[1]):.2f} ]"
                        else:
                            rates_str = "[]"
                    except Exception:
                        rates_str = "[]"
                    
                    # Copen-Rate hinzufügen wie bei den anderen Items
                    try:
                        if copen_rate is not None:
                            rates_str = f"{rates_str}<br>(Copen: {float(copen_rate):.0f})"
                    except Exception:
                        pass

                    partner_lines = []
                    for syn in synergies[:3]:
                        partner_label = syn.get("partner_label", "")
                        partner_score = float(syn.get("synergy_score", 0.0) or 0.0)
                        partner_lines.append(f"{partner_label} ({partner_score:.2f})")

                    synergy_text = "<br>".join(partner_lines) if partner_lines else "-"
                    avg_synergy = 0.0
                    if synergies:
                        avg_synergy = sum(float(s.get("synergy_score", 0.0) or 0.0) for s in synergies[:3]) / min(len(synergies[:3]), 3)
                    if avg_synergy > 0.7:
                        synergy_class = "prio-high"
                    elif avg_synergy > 0.5:
                        synergy_class = "prio-mid"
                    else:
                        synergy_class = "prio-low"

                    parts.append(
                        f"<tr><td><strong>{label}</strong></td>"
                        f"<td>{score:.3f}</td>"
                        f"<td class='rates'>{rates_str}</td>"
                        f"<td style='font-size:10px;'>{synergy_text}</td>"
                        f"<td><span class='badge {synergy_class}'>{avg_synergy:.2f}</span></td></tr>"
                    )

                parts.append("</table>")
                parts.append(
                    "<p class='note' style='font-size:11px;'>Synergie-Score: 0.0-0.3 = schwach, 0.3-0.5 = mittel, 0.5-0.7 = gut, 0.7-1.0 = sehr stark.</p>"
                )
            except Exception:
                pass
        
        # === HARMONISIERUNGSSCHRITTE SEKTION ===
        parts.append("<h2>Empfohlene Harmonisierungsschritte</h2>")
        harmonization_steps = _generate_harmonization_steps(group_buckets, max_sub_score)
        if harmonization_steps:
            parts.append("<ol>")
            for step in harmonization_steps:
                parts.append(f"<li>{step}</li>")
            parts.append("</ol>")
        else:
            parts.append("<p>Keine spezifischen Harmonisierungsschritte erforderlich.</p>")

    quantum_synergy = export_data.get("quantum_synergy")
    if isinstance(quantum_synergy, list) and quantum_synergy:
        focus = str(export_data.get("focus", "") or "").strip()

        def _axes_from_focus_text(focus_text: str) -> set[str]:
            txt = (focus_text or "").lower()
            axes: set[str] = set()
            if any(k in txt for k in ("lymph", "lymphe", "lymphsystem")):
                axes.add("drainage")
            if any(k in txt for k in ("leber", "galle", "entgift", "detox", "ausleit", "darm", "niere", "kidney", "haut", "schweißdrüsen", "talgdrüsen")):
                axes.add("drainage")
            if any(k in txt for k in ("immunsystem", "immun", "entzünd", "entzuend", "inflamm", "infekt", "virus", "bakter", "pilz", "parasit", "allerg", "autoimmun")):
                axes.add("immune")
            if any(k in txt for k in ("gehirn", "hirn", "zns", "nerv", "neuro", "schwindel", "kopfschmerz", "migraen", "migrän", "schlaf", "psyche", "angst", "depress")):
                axes.add("neuro")
            if any(k in txt for k in ("stoffwechsel", "metabol", "blutzucker", "insulin", "diabet", "lipid", "cholester", "triglycerid")):
                axes.add("metabolic")
            if any(k in txt for k in ("vitamin", "mineral", "spurenelement", "mikronähr", "mikronaehr", "mikronaehrstoff")):
                axes.add("regulation")
            return axes

        def _axes_from_label_and_groups(lbl: str, groups_raw: list[str]) -> set[str]:
            txt = (lbl or "").lower()
            for g in groups_raw:
                txt += " " + (g or "").lower()
            axes: set[str] = set()
            if any(k in txt for k in ("lymph", "lymphe", "lymphknoten", "lymphgefä", "lymphgefa", "drainage", "entgift", "detox", "ausleit", "galle", "leber", "niere", "kidney", "darm", "colon", "haut", "schweißdrüsen", "talgdrüsen")):
                axes.add("drainage")
            if any(k in txt for k in ("immunsystem", "immun", "entzünd", "entzuend", "inflamm", "infekt", "virus", "bakter", "pilz", "parasit", "mykose", "allerg", "autoimmun")):
                axes.add("immune")
            if any(k in txt for k in ("gehirn", "hirn", "zns", "nerv", "neuro", "neurolog", "schwindel", "vertigo", "kopfschmerz", "migraen", "migrän", "schlaf", "psyche", "angst", "depress")):
                axes.add("neuro")
            if any(k in txt for k in ("stoffwechsel", "metabol", "pankreas", "zucker", "glukose", "glucose", "insulin", "diabet", "lipid", "cholester", "triglycerid")):
                axes.add("metabolic")
            if any(k in txt for k in ("vitamin", "mineral", "spurenelement", "mikronähr", "mikronaehr", "mikronaehrstoff")):
                axes.add("regulation")
            return axes

        focus_axes = _axes_from_focus_text(focus)
        axis_phrases: Dict[str, str] = {
            "drainage": "Entgiftung/Drainage (Leber–Lymphe–Niere)",
            "immune": "Immunsystem/Entzündung",
            "neuro": "Nerven-/Gehirnregulation",
            "metabolic": "Stoffwechsel",
            "regulation": "Mikronährstoff- und Regulationsachse",
        }

        parts.append("<h2 style='color:#667eea;'>⚛️ Quantum-Synergy Analyse</h2>")
        parts.append(
            "<p style='background:#f8f9fa;padding:14px;border-left:4px solid #667eea;margin-top:8px;'>" \
            "Diese Analyse basiert auf dem Quantum-inspirierten Grover-Ansatz. Es werden nur die stärksten Kombinationen" \
            " aus dem aktuellen Multiplex-Lauf berücksichtigt. Fokus:" + (focus or " –") + "</p>"
        )

        for idx, combo in enumerate(quantum_synergy, 1):
            combo_score = float(combo.get("score", 0.0) or 0.0)
            combo_items = combo.get("items", []) or []
            components = combo.get("components", {}) or {}
            frequencies = combo.get("frequencies", []) or []

            if combo_score >= 8.5:
                color = "#28a745"
                priority = "Sehr hoch"
            elif combo_score >= 7.5:
                color = "#17a2b8"
                priority = "Hoch"
            else:
                color = "#ffc107"
                priority = "Mittel"

            parts.append(
                f"<div style='background:#fff;border:1px solid #e2e8f0;border-left:4px solid {color};"
                "padding:16px;margin:16px 0;border-radius:4px;'>"
            )
            parts.append(
                f"<h3 style='margin-top:0;color:{color};'>#{idx} – Synergy-Score {combo_score:.2f}/10.0 "
                f"<span style='font-size:12px;color:#555;'>({priority})</span></h3>"
            )

            # Dedupliziere gleiche Substanzen innerhalb der Kombination, fasse Gruppen zusammen
            dedup: Dict[str, Dict[str, object]] = {}
            for item in combo_items:
                try:
                    lbl = str(item.get("label", "") or "").strip()
                except Exception:
                    continue
                if not lbl:
                    continue
                grp_raw = str(item.get("group", "") or "")
                entry = dedup.get(lbl)
                if entry is None:
                    entry = {"groups": [], "groups_set": set()}
                    dedup[lbl] = entry
                gset = entry["groups_set"]  # type: ignore[assignment]
                glst = entry["groups"]      # type: ignore[assignment]
                if grp_raw and grp_raw not in gset:
                    gset.add(grp_raw)
                    glst.append(grp_raw)

            parts.append("<p><strong>Kombination (Substanzen, gruppenübergreifend):</strong></p><ul>")
            for item_label, info in dedup.items():
                groups_raw = info.get("groups", []) or []  # type: ignore[assignment]
                if groups_raw:
                    groups_fmt = ", ".join(
                        str(g).replace("_", " ").title() for g in groups_raw
                    )
                else:
                    groups_fmt = "Gruppe unbekannt"
                parts.append(
                    f"<li>{item_label} <span style='color:#777;font-size:11px;'>[{groups_fmt}]</span></li>"
                )
            parts.append("</ul>")

            ind_score = float(components.get("individual_scores", 0.0) or 0.0)
            res_score = float(components.get("resonance", 0.0) or 0.0)
            har_score = float(components.get("harmony", 0.0) or 0.0)
            rel_score = float(components.get("relevance", 0.0) or 0.0)

            parts.append(
                "<table style='width:100%;border-collapse:collapse;margin:10px 0;font-size:12px;'>"
                "<tr><th style='text-align:left;background:#f1f5f9;'>Komponente</th><th style='background:#f1f5f9;'>Score</th>"
                "<th style='text-align:left;background:#f1f5f9;'>Bedeutung</th></tr>"
            )
            parts.append(
                f"<tr><td>Einzelwirkungen</td><td>{ind_score:.2f}/10.0</td>"
                "<td style='font-size:11px;'>Durchschnitt der beteiligten Items</td></tr>"
            )
            parts.append(
                f"<tr><td>Resonanz-Verstärkung</td><td>{res_score:.2f}/10.0</td>"
                "<td style='font-size:11px;'>Bruce-Copen Resonanzüberlagerung</td></tr>"
            )
            parts.append(
                f"<tr><td>Frequenz-Harmonien</td><td>{har_score:.2f}/10.0</td>"
                "<td style='font-size:11px;'>Phi/Oktaven/Schumann-Bezug</td></tr>"
            )
            parts.append(
                f"<tr><td>Fokus-Relevanz</td><td>{rel_score:.2f}/10.0</td>"
                f"<td style='font-size:11px;'>Semantische Nähe zum Fokus '{focus or '-'}'</td></tr>"
            )
            parts.append("</table>")

            if frequencies:
                # Frequenzen pro Substanz (ggf. mehrere Einträge aus verschiedenen Gruppen zusammengefasst)
                freq_map: Dict[str, List[float]] = {}
                for item, freq in zip(combo_items, frequencies):
                    try:
                        lbl = str(item.get("label", "") or "").strip()
                        fval = float(freq)
                    except Exception:
                        continue
                    if not lbl:
                        continue
                    freq_map.setdefault(lbl, []).append(fval)

                parts.append("<p><strong>Frequenzen (pro Substanz):</strong></p>")
                parts.append(
                    "<table style='width:100%;border-collapse:collapse;font-size:11px;'>"
                    "<tr><th style='text-align:left;background:#f9fafb;'>Substanz</th>"
                    "<th style='background:#f9fafb;'>Frequenz (Hz)</th></tr>"
                )

                for lbl, vals in freq_map.items():
                    if not vals:
                        freq_str = "-"
                    elif len(vals) == 1:
                        freq_str = f"{vals[0]:.2f}"
                    else:
                        f_min = min(vals)
                        f_max = max(vals)
                        f_avg = sum(vals) / len(vals)
                        freq_str = f"{f_min:.2f}–{f_max:.2f} (Ø {f_avg:.2f})"
                    parts.append(
                        f"<tr><td>{lbl}</td><td>{freq_str}</td></tr>"
                    )

                parts.append("</table>")

            # Copen-Raten der Komponenten (falls in den Top-Sub-Ergebnissen vorhanden)
            if copen_by_label:
                copen_parts: List[str] = []
                for item_label in dedup.keys():
                    try:
                        cr_val = float(copen_by_label.get(item_label, 0.0))
                    except Exception:
                        cr_val = 0.0
                    if cr_val <= 0.0:
                        continue
                    try:
                        cr_str = f"{int(round(cr_val)):,}".replace(",", " ")
                    except Exception:
                        cr_str = f"{cr_val:.0f}"
                    copen_parts.append(f"{item_label}: {cr_str}")
                if copen_parts:
                    parts.append(
                        "<p style='font-size:11px;color:#374151;'>"
                        "<strong>Copen-Raten der Komponenten:</strong> "
                        + " | ".join(copen_parts)
                        + "</p>"
                    )

            combo_axes: Dict[str, int] = {}
            for item_label, info in dedup.items():
                try:
                    groups_raw = info.get("groups", []) or []
                except Exception:
                    groups_raw = []
                axes_here = _axes_from_label_and_groups(item_label, groups_raw)
                for ax in axes_here:
                    combo_axes[ax] = combo_axes.get(ax, 0) + 1

            # Kompakte, regelbasierte Interpretation auf Basis der Komponenten-Scores
            if res_score >= 8.5:
                base_interpret = "Sehr starke Resonanzüberlagerung – simultane Behandlung empfohlen."
            elif res_score >= 7.0:
                base_interpret = "Gute Synergien – Kombination priorisieren."
            else:
                base_interpret = "Moderate Synergien – nach klinischer Relevanz auswählen."

            def _score_qualifier(v: float) -> str:
                if v >= 8.5:
                    return "sehr hoch"
                if v >= 7.0:
                    return "hoch"
                if v >= 5.0:
                    return "mittel"
                if v >= 3.0:
                    return "niedrig"
                return "sehr niedrig"

            ind_txt = _score_qualifier(ind_score)
            res_txt = _score_qualifier(res_score)
            har_txt = _score_qualifier(har_score)
            rel_txt = _score_qualifier(rel_score)

            dominant_axis = None
            if combo_axes:
                try:
                    dominant_axis = max(combo_axes.items(), key=lambda kv: kv[1])[0]
                except Exception:
                    dominant_axis = None

            focus_sentence = ""
            if focus and dominant_axis:
                dom_phrase = axis_phrases.get(dominant_axis, dominant_axis)
                overlap = focus_axes.intersection(combo_axes.keys())
                if overlap and rel_score >= 7.0:
                    focus_sentence = (
                        f" Die Kombination passt inhaltlich gut zum Fokus \"{focus}\" "
                        f"und betont vor allem die Achse {dom_phrase}."
                    )
                elif overlap and rel_score >= 5.0:
                    focus_sentence = (
                        f" Die Kombination unterstützt den Fokus \"{focus}\" moderat "
                        f"über die Achse {dom_phrase}."
                    )
                elif overlap:
                    focus_sentence = (
                        f" Die Kombination berührt den Fokus \"{focus}\" eher indirekt; "
                        f"im Vordergrund steht die Achse {dom_phrase}."
                    )
                elif rel_score >= 7.0:
                    focus_sentence = (
                        f" Trotz anderer Schwerpunkte (Achse {dom_phrase}) zeigt die Kombination "
                        f"eine hohe Fokus-Relevanz zu \"{focus}\"."
                    )
                else:
                    focus_sentence = (
                        f" Die Kombination zielt primär auf die Achse {dom_phrase}; "
                        f"der Bezug zum Fokus \"{focus}\" ist eher ergänzend."
                    )
            elif dominant_axis:
                dom_phrase = axis_phrases.get(dominant_axis, dominant_axis)
                focus_sentence = (
                    f" Inhaltlich liegt der Schwerpunkt der Kombination auf der Achse {dom_phrase}."
                )
            elif focus:
                focus_sentence = (
                    f" Der Bezug zum Fokus \"{focus}\" ergibt sich vor allem aus der Gesamtbewertung der Komponenten."
                )

            details_text = (
                f"Einzelwirkungen: {ind_txt}, Resonanz-Verstärkung: {res_txt}, "
                f"Frequenz-Harmonien: {har_txt}, Fokus-Relevanz: {rel_txt}."
            )
            final_interpret = f"{base_interpret} {details_text}"
            if focus_sentence:
                final_interpret += focus_sentence

            parts.append(
                "<p style='font-size:12px;color:#374151;background:#f8fafc;padding:10px;border-radius:4px;'>" \
                f"<strong>Interpretation:</strong> {final_interpret}" \
                "</p>"
            )
            parts.append("</div>")

        label_counts: Dict[str, int] = {}
        for combo in quantum_synergy:
            for item in combo.get("items", []) or []:
                lbl = str(item.get("label", "")).strip()
                if lbl:
                    label_counts[lbl] = label_counts.get(lbl, 0) + 1

        if label_counts:
            combo_total = len(quantum_synergy)
            parts.append("<h3>Häufigste Quantum-Trigger</h3>")
            parts.append("<ul>")
            for label, count in sorted(label_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]:
                parts.append(
                    f"<li><strong>{label}</strong> – in {count} von {combo_total} Kombinationen</li>"
                )
            parts.append("</ul>")
        parts.append(
            "<p class='note'>Berechnung gemäß Referenzstand 16.11.2025: Nur Items aus den top-resonanten Gruppen "
            "des aktuellen Laufs werden berücksichtigt. Keine globalen Ergänzungen.</p>"
        )
    client = export_data.get("client") or {}
    first_name = str(client.get("first_name", "")).strip()
    last_name = str(client.get("name", "")).strip()
    birth_date = str(client.get("birth_date", "")).strip()
    birth_place = str(client.get("birth_place", "")).strip()

    command = str(export_data.get("command", "multiplex_scan")).strip()
    focus = str(export_data.get("focus", "") or "").strip()

    metrics = export_data.get("metrics") or {}
    analysis_block = export_data.get("analysis") or {}

    # Fallback: Wenn im aktuellen Export keine alten metrics gesetzt sind
    # (z.B. bei neuen multiplex_scan-Exports), nutze die Werte aus analysis,
    # damit am unteren Rand keine 0.0000-Werte angezeigt werden.
    m_field = float(
        metrics.get("morphic_field")
        or analysis_block.get("morphic_field", 0.0)
        or 0.0
    )
    entropy = float(
        metrics.get("holographic_entropy")
        or analysis_block.get("holographic_entropy", 0.0)
        or 0.0
    )
    heim_sig = (
        metrics.get("heim_signature")
        or analysis_block.get("heim_signature")
        or []
    )

    h_level = float(export_data.get("h_level", 0.0) or 0.0)
    hw_profile = str(export_data.get("hardware_profile", "")).strip()
    hw_source = str(export_data.get("hardware_source", "")).strip()

    sections = export_data.get("sections") or []
    aggregates = export_data.get("aggregates") or []
    therapy_top = export_data.get("therapy_top") or []

    parts.append("<h1>Resonanzanalyse – Multiplex-Scan</h1>")
    parts.append(
        f"<p><b>Klient:</b> {first_name} {last_name} – {birth_date}, {birth_place}</p>"
    )
    
    # === SCAN-PARAMETER ANZEIGEN (NEU) ===
    scan_profile = export_data.get("profile", "unknown")
    scan_intention = export_data.get("intention")
    scan_planet = export_data.get("planet_type")
    profile_groups_count = export_data.get("profile_groups_count", 0)
    focus_weighting_enabled = export_data.get("focus_weighting", False)
    personal_values = export_data.get("personal_profile_values", {})
    entropy_mode = export_data.get("entropy_mode", "legacy")
    use_hybrid = export_data.get("use_hybrid_entropy", False)
    
    parts.append(
        f"<p><b>Profil:</b> {scan_profile} "
        f"({profile_groups_count} Gruppen definiert)</p>"
    )
    
    # Zeile 1: Fokus & Fokus-Gewichtung
    scan_params_1 = []
    if focus:
        focus_weight_text = " (Gewichtung aktiv)" if focus_weighting_enabled else ""
        scan_params_1.append(f"<b>Fokus:</b> {focus}{focus_weight_text}")
    
    if scan_params_1:
        parts.append(f"<p>{' | '.join(scan_params_1)}</p>")
    
    # Zeile 2: Planet & Intention
    scan_params_2 = []
    if scan_planet:
        scan_params_2.append(f"<b>Geburtsplanet:</b> {scan_planet}")
    if scan_intention:
        scan_params_2.append(f"<b>Intention:</b> {scan_intention}")
    
    if scan_params_2:
        parts.append(f"<p>{' | '.join(scan_params_2)}</p>")
    
    # Zeile 3: Personalprofil-Werte
    if personal_values:
        pp_text = f"Emotion={personal_values.get('emotion', 0.5):.2f}, "
        pp_text += f"Physisch={personal_values.get('physisch', 0.5):.2f}, "
        pp_text += f"Mental={personal_values.get('mental', 0.5):.2f}, "
        pp_text += f"Astral={personal_values.get('astral', 0.5):.2f}"
        parts.append(f"<p><b>Personalprofil:</b> {pp_text}</p>")
    
    # Zeile 4: Entropie-Konfiguration
    entropy_config = f"<b>Entropie-Modus:</b> {entropy_mode}"
    if use_hybrid:
        entropy_config += " (Hybrid-Entropy aktiv)"
    parts.append(f"<p>{entropy_config}</p>")
    
    parts.append(
        f"<p><b>Modus:</b> {command} | "
        f"<b>Hardware-Profil:</b> {hw_profile or '-'} | "
        f"<b>Quelle:</b> {hw_source or '-'}"  # type: ignore[str-format]
        "</p>"
    )
    summary = (
        f"<p><b>Hardware-Level:</b> {h_level:.3f} | "
        f"<b>Morphisches Feld:</b> {m_field:.4f} | "
        f"<b>Entropie:</b> {entropy:.4f}</p>"
    )
    parts.append(summary)

    try:
        heim_str = ", ".join(f"{float(x):.3f}" for x in heim_sig)
        parts.append(f"<p><b>Heim‑Signatur:</b> [{heim_str}]</p>")
    except Exception:
        pass

    if aggregates:
        parts.append("<h2>Gruppenaggregate</h2>")
        parts.append(
            "<table><tr><th>Sektion</th><th>Aus Subgruppen</th><th>Aus NLS</th><th>Kombiniert</th></tr>"
        )
        for ag in aggregates:
            try:
                name = str(ag.get("name", ""))
                r_sub = ag.get("subgroups_rates") or []
                r_nls = ag.get("nls_rates") or []
                r_comb = ag.get("combined_rates") or []
                def _fmt(rv: list[float] | list) -> str:
                    try:
                        if rv:
                            return "[ " + " ".join(f"{float(x):.2f}" for x in rv[:2]) + " ]"
                    except Exception:
                        pass
                    return "[]"
                parts.append(
                    f"<tr><td>{name}</td><td class='rates'>{_fmt(r_sub)}</td>"
                    f"<td class='rates'>{_fmt(r_nls)}</td><td class='rates'>{_fmt(r_comb)}</td></tr>"
                )
            except Exception:
                continue
        parts.append("</table>")
        parts.append(
            "<p class='note'>Aggregierte Raten je Kategorie: 'Aus Subgruppen' (einfacher Mittelwert), 'Aus NLS' (score-gewichtet), 'Kombiniert' (Mittel der beiden)." 
            "</p>"
        )

    for section in sections:
        name = str(section.get("name", ""))
        entries = section.get("entries") or []
        if not entries:
            continue
        parts.append(f"<h2>{name}</h2>")
        
        # Hole Beschreibungen für alle Items in dieser Sektion
        labels_in_section = [str(it.get("label", "")) for it in entries if it.get("label")]
        descriptions_map = {}
        try:
            descriptions_map = get_descriptions_batch(labels_in_section)
        except Exception:
            pass  # Wenn keine Beschreibungen verfügbar, einfach ohne weitermachen
        
        parts.append(
            "<table><tr>"
            "<th>Label</th><th>Beschreibung</th><th>Gesamtscore</th><th>Intensität</th><th>Potenz</th><th>DV</th>"
            "<th>Ebene</th><th>Resonanz</th><th>Entropie Ausrichtung</th><th>Priorität</th><th>Raten</th>"
            "</tr>"
        )
        for it in entries:
            try:
                lbl = str(it.get("label", ""))
                score_val = float(it.get("score", 0.0) or 0.0)
                intensity = float(it.get("intensity", 0.0) or 0.0)
                potency = str(it.get("potency", "") or "-")
                dv = int(it.get("dv", 0) or 0)
                level = str(it.get("group", "") or "-")
                s_res = float(it.get("resonance", 0.0) or 0.0)
                s_ent = float(it.get("entropy_alignment", 0.0) or 0.0)
                prio = str(it.get("priority", "niedrig"))
                rates_vals = it.get("rates") or []
                copen_val = it.get("copen_rate")
            except Exception:
                continue

            if prio == "hoch":
                prio_cls = "prio-high"
            elif prio == "mittel":
                prio_cls = "prio-mid"
            else:
                prio_cls = "prio-low"

            try:
                if rates_vals:
                    rates_str = "[ " + " ".join(f"{float(x):.2f}" for x in rates_vals) + " ]"
                else:
                    rates_str = "[]"
            except Exception:
                rates_str = str(rates_vals)

            try:
                if copen_val is not None:
                    rates_str = f"{rates_str} (Copen: {float(copen_val):.0f})"
            except Exception:
                pass

            # Hole Beschreibung für dieses Item
            desc_text = ""
            if lbl in descriptions_map:
                desc_info = descriptions_map[lbl]
                desc_text = desc_info.get("description", "")
                if desc_text:
                    # Kürze Beschreibung auf 150 Zeichen für Tabelle
                    if len(desc_text) > 150:
                        desc_text = desc_text[:147] + "..."
            
            if not desc_text:
                desc_text = "-"

            parts.append(
                f"<tr><td>{lbl}</td><td class='description'>{desc_text}</td><td>{score_val:.4f}</td><td>{intensity:.2f}</td><td>{potency}</td>"
                f"<td>{dv}</td><td>{level}</td><td>{s_res:.4f}</td><td>{s_ent:.4f}</td>"
                f"<td><span class='badge {prio_cls}'>{prio}</span></td><td class='rates'>{rates_str}</td></tr>"
            )
        parts.append("</table>")

    # === B.A.T. SUBGRUPPEN-ANALYSE (wenn vorhanden) ===
    bat_subgroups = export_data.get("bat_subgroups") or []
    if bat_subgroups:
        parts.append("<h2>B.A.T. Subgruppen-Analyse (Top 5)</h2>")
        parts.append("<p class='note'>Aggregierte Ergebnisse aus dem B.A.T. Akutprogramm mit empfohlenen Remedies.</p>")
        
        for i, subgroup in enumerate(bat_subgroups, 1):
            sg_name = subgroup.get("name", "Unbekannt")
            sg_avg_score = float(subgroup.get("avg_score", 0.0) or 0.0)
            sg_item_count = int(subgroup.get("item_count", 0) or 0)
            sg_top_items = subgroup.get("top_items", [])
            sg_remedies = subgroup.get("remedies", [])
            
            parts.append(f"<h3>#{i} {sg_name}</h3>")
            parts.append(f"<p><b>Score:</b> {sg_avg_score:.4f} (Durchschnitt) | <b>Items:</b> {sg_item_count}</p>")
            
            # Top Items Tabelle
            if sg_top_items:
                parts.append("<table><tr><th>Item</th><th>Score</th></tr>")
                for item in sg_top_items[:3]:
                    item_label = item.get("label", "")
                    item_score = float(item.get("score", 0.0) or 0.0)
                    parts.append(f"<tr><td>{item_label}</td><td>{item_score:.4f}</td></tr>")
                parts.append("</table>")
            
            # Remedies
            if sg_remedies:
                parts.append("<p><b>Empfohlene Remedies:</b></p>")
                parts.append("<ul>")
                for remedy in sg_remedies:
                    r_name = remedy.get("name", "")
                    r_ind = remedy.get("indication", "")
                    parts.append(f"<li><b>{r_name}</b> – {r_ind}</li>")
                parts.append("</ul>")

    parts.append(_HTML_FOOT)
    return "\n".join(parts)


def _render_multiplex_txt(export_data: Dict[str, object]) -> str:
    client = export_data.get("client") or {}
    first_name = str(client.get("first_name", "")).strip()
    last_name = str(client.get("name", "")).strip()
    birth_date = str(client.get("birth_date", "")).strip()
    birth_place = str(client.get("birth_place", "")).strip()

    command = str(export_data.get("command", "multiplex_scan")).strip()
    focus = str(export_data.get("focus", "") or "").strip()

    metrics = export_data.get("metrics") or {}
    m_field = float(metrics.get("morphic_field", 0.0) or 0.0)
    entropy = float(metrics.get("holographic_entropy", 0.0) or 0.0)
    heim_sig = metrics.get("heim_signature") or []

    h_level = float(export_data.get("h_level", 0.0) or 0.0)
    hw_profile = str(export_data.get("hardware_profile", "")).strip()
    hw_source = str(export_data.get("hardware_source", "")).strip()

    sections = export_data.get("sections") or []
    aggregates = export_data.get("aggregates") or []
    therapy_top = export_data.get("therapy_top") or []

    def _fmt_rates(lst: List[float] | list) -> str:
        try:
            if lst:
                return "[ " + " ".join(f"{float(x):.2f}" for x in lst[:2]) + " ]"
        except Exception:
            pass
        return "[]"

    lines: List[str] = []
    lines.append("Morphic Engine V1 – Multiplex-Scan (TXT)")
    lines.append(f"Klient: {first_name} {last_name} – {birth_date}, {birth_place}")
    lines.append(f"Modus: {command} | Hardware-Profil: {hw_profile or '-'} | Quelle: {hw_source or '-'}")
    base = f"Hardware-Level: {h_level:.3f} | Morphisches Feld: {m_field:.4f} | Entropie: {entropy:.4f}"
    if focus:
        base += f" | Fokus: {focus}"
    lines.append(base)
    try:
        if heim_sig:
            heim_str = ", ".join(f"{float(x):.3f}" for x in heim_sig)
            lines.append(f"Heim-Signatur: [ {heim_str} ]")
    except Exception:
        pass
    if aggregates:
        lines.append("")
        lines.append("Gruppenaggregate")
        for ag in aggregates:
            try:
                name = str(ag.get("name", ""))
                r_sub = ag.get("subgroups_rates") or []
                r_nls = ag.get("nls_rates") or []
                r_comb = ag.get("combined_rates") or []
                lines.append(
                    f"- Sektion: {name} | Subgruppen: {_fmt_rates(r_sub)} | NLS: {_fmt_rates(r_nls)} | Kombiniert: {_fmt_rates(r_comb)}"
                )
            except Exception:
                continue
    for section in sections:
        name = str(section.get("name", ""))
        entries = section.get("entries") or []
        if not entries:
            continue
        lines.append("")
        lines.append(name)
        for it in entries:
            try:
                lbl = str(it.get("label", ""))
                score_val = float(it.get("score", 0.0) or 0.0)
                intensity = float(it.get("intensity", 0.0) or 0.0)
                potency = str(it.get("potency", "") or "-")
                dv = int(it.get("dv", 0) or 0)
                level = str(it.get("group", "") or "-")
                s_res = float(it.get("resonance", 0.0) or 0.0)
                s_ent = float(it.get("entropy_alignment", 0.0) or 0.0)
                prio = str(it.get("priority", "niedrig"))
                rates_vals = it.get("rates") or []
            except Exception:
                continue
            try:
                if rates_vals:
                    rates_str = "[ " + " ".join(f"{float(x):.2f}" for x in rates_vals[:2]) + " ]"
                else:
                    rates_str = "[]"
            except Exception:
                rates_str = "[]"
            lines.append(
                f"- {lbl} | score={score_val:.4f} | intensität={intensity:.2f} | dv={dv} | potenz={potency} | gruppe={level} | res={s_res:.4f} | ent={s_ent:.4f} | prio={prio} | rates: {rates_str}"
            )
    if therapy_top:
        lines.append("")
        lines.append("Therapie – Top-Kandidaten")
        for e in therapy_top:
            try:
                lbl = str(e.get("label", ""))
                sc = float(e.get("score", 0.0) or 0.0)
                pot = str(e.get("potency", "") or "-")
                grp = str(e.get("group", "") or "-")
                dv = int(e.get("dv", 0) or 0)
                prio = str(e.get("priority", ""))
                r_vals = e.get("rates") or []
            except Exception:
                continue
            try:
                if r_vals:
                    r_str = "[ " + " ".join(f"{float(x):.2f}" for x in r_vals[:2]) + " ]"
                else:
                    r_str = "[]"
            except Exception:
                r_str = "[]"
            lines.append(
                f"- {lbl} | score={sc:.4f} | potenz={pot} | gruppe={grp} | dv={dv} | prio={prio} | rates: {r_str}"
            )
    return "\n".join(lines)


@app.command("groups-overview")
def groups_overview(json_out: bool = typer.Option(False, "--json", help="Ausgabe als JSON")) -> None:
    """Zeigt eine Übersicht aller verfügbaren Gruppen/Multiplexe und vergleicht sie mit dem FULL-Profil.

    - System-Gruppen: prozedural verfügbare Gruppen (SubgroupService / procedural_groups)
    - Custom-Gruppen & Multiplexe: aus tools/group_manager
    - FULL-Profil: Gruppenliste aus multiplex_scan (Profil 'full'/'therapy')
    """

    subgroup_svc = SubgroupService()
    system_groups = set(subgroup_svc.list_groups())

    manager = GroupManager()
    custom_groups = set(manager.list_custom_groups())
    custom_multiplexes = manager.list_custom_multiplexes()

    # Referenz: FULL-Profil-Gruppen (wie in multiplex_scan für prof in ("full", "therapy"))
    full_profile_groups = {
        # Basis-Systeme
        "kreislauf",
        "chakren",
        "chakren_full",
        "chakren_erweitert",
        "nebenchakren",
        "meridiane",
        "tcm_punkte",
        "tcm_punkte_extended",
        "tcm_full",
        "extra_meridiane",
        # Pathogene (Basis + Fein)
        "bakterien",
        "bakterien_fein",
        "viren",
        "viren_fein",
        "parasiten",
        "parasiten_fein",
        "pilze",
        "pilze_fein",
        # Toxine & Belastungen
        "schwermetalle",
        "schwermetalle_tox",
        "pestizide_tox",
        "chemikalien_tox",
        "strahlung_tox",
        "emf_fein",
        "geopathie",
        # Regulation & Systeme
        "endokrin",
        "detox",
        "mikrozirkulation",
        "mitochondrien",
        "entzuendung",
        "allergene",
        "mikronaehrstoffe",
        "wirbelsaeule",
        "zahnorgane",
        "odontone",
        "schlaf",
        # Remedies & Therapien
        "homoeopathie_klassisch",
        "homoeopathie_klassisch_potenzen",
        "tcm_rezepturen",
        "tcm_rezepturen_potenzen",
        "spagyrik",
        "farbtherapie",
        "edelsteine",
        # Erweiterte Protokolle
        "laser_protokolle",
        "rife_cafl_proc",
        "baklayan_proc",
    }

    missing_in_system = sorted(g for g in full_profile_groups if g not in system_groups)
    extra_system = sorted(g for g in system_groups if g not in full_profile_groups)

    summary: Dict[str, object] = {
        "system_groups": sorted(system_groups),
        "full_profile_groups": sorted(full_profile_groups),
        "missing_in_system": missing_in_system,
        "extra_system_groups": extra_system,
        "custom_groups": sorted(custom_groups),
        "custom_multiplexes": sorted(custom_multiplexes),
    }

    if json_out:
        typer.echo(json.dumps(summary, indent=2, ensure_ascii=False))
        return

    typer.echo("Morphic Engine V1 – Gruppen-/Profil-Übersicht")
    typer.echo("")

    typer.echo(f"System-Gruppen (prozedural): {len(system_groups)}")
    for g in sorted(system_groups):
        typer.echo(f"  - {g}")

    typer.echo("")
    typer.echo(f"FULL-Profil-Gruppen: {len(full_profile_groups)}")
    typer.echo(f"  Davon physisch vorhanden: {len(full_profile_groups - set(missing_in_system))}")
    typer.echo(f"  Davon fehlend: {len(missing_in_system)}")
    if missing_in_system:
        typer.echo("  Fehlende FULL-Gruppen:")
        for g in missing_in_system:
            typer.echo(f"    - {g}")

    if extra_system:
        typer.echo("")
        typer.echo(f"System-Gruppen außerhalb des FULL-Profils: {len(extra_system)}")
        for g in extra_system:
            typer.echo(f"  - {g}")

    typer.echo("")
    typer.echo(f"Benutzerdefinierte Gruppen: {len(custom_groups)}")
    for g in sorted(custom_groups):
        typer.echo(f"  - {g}")

    typer.echo("")
    typer.echo(f"Benutzerdefinierte Multiplexe: {len(custom_multiplexes)}")
    for m in sorted(custom_multiplexes):
        typer.echo(f"  - {m}")

@app.command("hw-diagnostics")
def hw_diagnostics(
    duration_s: float = typer.Option(2.0, "--duration", help="Messdauer je Quelle in Sekunden"),
    export: Path | None = typer.Option(
        None,
        "--export",
        help="Exportiert Ergebnisse der Hardware-Diagnose als JSON-Datei",
    ),
) -> None:
    """Diagnose der verfügbaren Hardware-Entropiequellen.

    Zeigt an, welche Quellen (cpu_timer, hid_sensor, qrng) verfügbar sind und
    welche h-Level-Werte sie liefern. Zusätzlich wird ausgegeben, welche Quelle
    `select_entropy_source` aktuell auswählen würde.
    """

    typer.echo("Morphic Engine V1 – Hardware-Diagnose")
    typer.echo(f"Messdauer: {duration_s:.2f}s")
    typer.echo("")

    result: Dict[str, object] = {"duration_s": float(duration_s), "sources": {}}
    sources: Dict[str, Dict[str, object]] = {}
    result["sources"] = sources

    cpu_src = select_entropy_source(preferred=["cpu_timer"])
    cpu_h = _clamp(cpu_src.sample_h_level(duration_s=duration_s))
    typer.echo(f"cpu_timer: verfügbar, h_level={cpu_h:.3f}")
    sources["cpu_timer"] = {"available": True, "h_level": float(cpu_h)}

    hid_src = select_entropy_source(preferred=["hid_sensor", "cpu_timer"])
    hid_h = None
    if hid_src.name() == "hid_sensor":
        try:
            hid_stats = sample_hid_level(duration_s=duration_s)
        except Exception:
            hid_stats = {"ok": False, "h_level": 0.0}
        hid_h = _clamp(float(hid_stats.get("h_level", 0.0)))
        typer.echo(f"hid_sensor: verfügbar, h_level={hid_h:.3f}")
        sources["hid_sensor"] = {
            "available": True,
            "h_level": float(hid_h),
            "ok": bool(hid_stats.get("ok")),
            "count": hid_stats.get("count"),
            "std_norm": hid_stats.get("std_norm"),
            "var_norm": hid_stats.get("var_norm"),
            "entropy": hid_stats.get("entropy"),
            "reason": hid_stats.get("reason"),
        }

        ok = bool(hid_stats.get("ok"))
        if ok:
            count = hid_stats.get("count")
            std_norm = hid_stats.get("std_norm")
            var_norm = hid_stats.get("var_norm")
            entropy = hid_stats.get("entropy")

            detail_parts = []
            if count is not None:
                try:
                    detail_parts.append(f"count={int(count)}")
                except Exception:
                    pass
            if std_norm is not None:
                try:
                    detail_parts.append(f"std_norm={float(std_norm):.3f}")
                except Exception:
                    pass
            if var_norm is not None:
                try:
                    detail_parts.append(f"var_norm={float(var_norm):.3f}")
                except Exception:
                    pass
            if entropy is not None:
                try:
                    detail_parts.append(f"entropy={float(entropy):.3f}")
                except Exception:
                    pass
            if detail_parts:
                typer.echo("  HID-Details: " + ", ".join(detail_parts))
        else:
            reason = hid_stats.get("reason")
            count = hid_stats.get("count")
            msg = "  HID-Fehler"
            if reason:
                msg += f": {reason}"
            if count is not None:
                try:
                    msg += f" (count={int(count)})"
                except Exception:
                    pass
            typer.echo(msg)
    else:
        typer.echo("hid_sensor: nicht verfügbar oder kein Gerät gefunden")
        sources["hid_sensor"] = {"available": False}

    qrng_src = select_entropy_source(preferred=["qrng", "cpu_timer"])
    qrng_h = None
    if qrng_src.name() == "qrng":
        try:
            qrng_h_val = qrng_src.sample_h_level(duration_s=duration_s)
        except Exception:
            qrng_h_val = 0.0
        qrng_h = _clamp(float(qrng_h_val))
        typer.echo(f"qrng: verfügbar, h_level={qrng_h:.3f}")
        sources["qrng"] = {"available": True, "h_level": float(qrng_h)}
    else:
        typer.echo("qrng: nicht verfügbar")
        sources["qrng"] = {"available": False}

    gpu_src = select_entropy_source(preferred=["gpu", "cpu_timer"])
    gpu_h = None
    if gpu_src.name() == "gpu":
        try:
            gpu_h_val = gpu_src.sample_h_level(duration_s=duration_s)
        except Exception:
            gpu_h_val = 0.0
        gpu_h = _clamp(float(gpu_h_val))
        typer.echo(f"gpu: verfügbar, h_level={gpu_h:.3f}")
        sources["gpu"] = {"available": True, "h_level": float(gpu_h)}
    else:
        typer.echo("gpu: nicht verfügbar")
        sources["gpu"] = {"available": False}

    network_src = select_entropy_source(preferred=["network", "cpu_timer"])
    network_h = None
    if network_src.name() == "network":
        try:
            network_h_val = network_src.sample_h_level(duration_s=duration_s)
        except Exception:
            network_h_val = 0.0
        network_h = _clamp(float(network_h_val))
        typer.echo(f"network: verfügbar, h_level={network_h:.3f}")
        sources["network"] = {"available": True, "h_level": float(network_h)}
    else:
        typer.echo("network: nicht verfügbar")
        sources["network"] = {"available": False}

    typer.echo("")
    typer.echo("Adaptive Auswahl (Bevorzugung: qrng > gpu > network > hid_sensor > cpu_timer):")

    selected_name = "cpu_timer"
    selected_h = cpu_h

    if qrng_src.name() == "qrng" and qrng_h is not None and qrng_h > 0.0:
        selected_name = "qrng"
        selected_h = qrng_h
    elif gpu_src.name() == "gpu" and gpu_h is not None and gpu_h > 0.0:
        selected_name = "gpu"
        selected_h = gpu_h
    elif network_src.name() == "network" and network_h is not None and network_h > 0.0:
        selected_name = "network"
        selected_h = network_h
    elif hid_src.name() == "hid_sensor" and hid_h is not None and hid_h > 0.0:
        selected_name = "hid_sensor"
        selected_h = hid_h

    typer.echo(f"  ausgewählte Quelle: {selected_name}, h_level={selected_h:.3f}")
    sources["selected"] = {"name": selected_name, "h_level": float(selected_h)}

    if export is not None:
        try:
            export.parent.mkdir(parents=True, exist_ok=True)
            export.write_text(
                json.dumps(result, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            typer.echo(f"Export gespeichert: {export}")
        except Exception as exc:
            typer.echo(f"Export fehlgeschlagen: {exc}")


@app.command()
def analyze(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09031999"),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    group: List[str] = typer.Option(
        ["chakren", "meridiane"],
        "--group",
        "-g",
        help="Subgruppen, aus denen Kandidaten generiert werden",
    ),
    seed: str = typer.Option("cli-seed", "--seed", help="Seed für prozedurale Kandidaten"),
    fixed_h: float = typer.Option(
        None,
        "--fixed-h",
        min=0.0,
        max=1.0,
        help="Optional fester h-Level in [0,1]; ohne Angabe wird adaptiv gemessen",
    ),
    top_k: int = typer.Option(5, "--top-k", min=1, help="Anzahl der Top-Resonanzen"),
    hardware_profile: str = typer.Option(
        "windows",
        "--hardware-profile",
        help="Hardware-Profil: z.B. 'legacy', 'windows' oder 'debian_server'",
    ),
    focus: str = typer.Option(
        "",
        "--focus",
        help="Optionaler Fokus / Symptom, das in der Auswertung hervorgehoben werden soll",
    ),
    export: Path | None = typer.Option(
        None,
        "--export",
        help=(
            "Exportiert Ergebnisse der Analyse als JSON+HTML. "
            "Pfad kann Datei (.json/.html) oder Basisordner (z.B. 'history') sein."
        ),
    ),
) -> None:
    """Führt eine Kernanalyse basierend auf prozeduralen Subgruppen durch."""

    rate_db = _build_rate_db_from_subgroups(group, seed, k_total=64)
    if not rate_db:
        typer.echo("Keine Kandidaten im Rate-Database erzeugt.")
        raise typer.Exit(code=1)

    _profile = (hardware_profile or "windows").strip().lower()
    src_name = "cpu_timer"

    if fixed_h is None:
        if _profile == "debian_server":
            duration = 2.0
            src = select_entropy_source(preferred=["qrng", "gpu", "network", "cpu_timer"])
            h_level = _clamp(src.sample_h_level(duration_s=duration))
            if src.name() in ("qrng", "gpu", "network") and h_level <= 0.0:
                fallback_src = select_entropy_source(preferred=["cpu_timer"])
                fallback_h = _clamp(fallback_src.sample_h_level(duration_s=duration))
                if fallback_h > h_level:
                    src = fallback_src
                    h_level = fallback_h
        else:
            duration = 3.0 if _profile == "windows" else 2.0
            src = select_entropy_source(preferred=["hid_sensor", "cpu_timer"])
            h_level = _clamp(src.sample_h_level(duration_s=duration))
            if src.name() == "hid_sensor" and h_level <= 0.0:
                fallback_src = select_entropy_source(preferred=["cpu_timer"])
                fallback_h = _clamp(fallback_src.sample_h_level(duration_s=duration))
                if fallback_h > h_level:
                    src = fallback_src
                    h_level = fallback_h
        src_name = src.name()
    else:
        h_level = _clamp(float(fixed_h))
        src_name = "fixed"

    profile = ClientProfile(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        image_signature=None,
    )

    service = AnalysisService(rate_db, h_level=h_level)
    result = service.analyze(profile)

    resonance_map = result["resonance_map"]
    sorted_items = sorted(resonance_map.items(), key=lambda kv: kv[1], reverse=True)[:top_k]

    typer.echo(f"Morphic Engine V1 – Analyse für {first_name} {name}")
    typer.echo(f"h_level (Hardware): {h_level:.3f} [{src_name} / profile={_profile}]")
    typer.echo(f"Morphic field: {result['morphic_field']:.4f}")
    typer.echo(f"Holographic entropy: {result['holographic_entropy']:.4f}")
    typer.echo("Top Resonances:")
    for label, score in sorted_items:
        typer.echo(f"  - {label}: {score:.4f}")

    if export is not None:
        scores_export: List[Dict[str, object]] = []
        for label, score in resonance_map.items():
            scores_export.append({"label": str(label), "score": float(score)})

        top_scores_export: List[Dict[str, object]] = []
        for label, score in sorted_items:
            top_scores_export.append({"label": str(label), "score": float(score)})

        client_info: Dict[str, str] = {
            "name": name,
            "first_name": first_name,
            "birth_date": birth_date,
            "birth_place": birth_place,
        }

        heim_sig_raw = result.get("heim_signature")
        if heim_sig_raw is None:
            heim_sig_list: List[float] = []
        else:
            heim_sig_list = [float(x) for x in heim_sig_raw]
        rates_raw = result.get("rates")
        if rates_raw is None:
            rates_list: List[float] = []
        else:
            rates_list = [float(x) for x in rates_raw]
        entropy_val = float(result.get("holographic_entropy", 0.0))
        metrics: Dict[str, object] = {
            "morphic_field": float(result.get("morphic_field", 0.0)),
            "holographic_entropy": entropy_val,
            "entropy_calibrated": entropy_val,
            "heim_signature": heim_sig_list,
            "rates": rates_list,
        }

        sub_results: Dict[str, object] = {}
        try:
            subgroup_svc = SubgroupService()
            sub_candidates = subgroup_svc.generate_fullbody_candidates(group, seed, k_total=64)
            sub_top: List[Dict[str, object]] = []
            for it in sub_candidates:
                label_it = str(it.get("label", ""))
                if not label_it or label_it not in resonance_map:
                    continue
                try:
                    score_it = float(resonance_map.get(label_it, 0.0) or 0.0)
                except Exception:
                    continue
                rates_it = [float(r) for r in it.get("rates", [])]
                entry: Dict[str, object] = {
                    "label": label_it,
                    "score": score_it,
                    "rates": rates_it,
                    "group": str(it.get("group", "")),
                }
                potency = it.get("potency")
                if potency is not None:
                    entry["potency"] = str(potency)
                desc = it.get("description")
                if desc:
                    entry["description"] = str(desc)
                sub_top.append(entry)

            sub_top_sorted = sorted(
                sub_top,
                key=lambda e: float(e.get("score", 0.0) or 0.0),
                reverse=True,
            )
            sub_results = {
                "groups": list(group),
                "method": "fullbody",
                "candidates": len(sub_candidates),
                "top": sub_top_sorted,
            }
        except Exception:
            sub_results = {}

        export_data: Dict[str, object] = {
            "command": "analyze",
            "hardware_profile": _profile,
            "hardware_source": src_name,
            "h_level": float(h_level),
            "client": client_info,
            "focus": focus,
            "metrics": metrics,
            "scores": scores_export,
            "top_scores": top_scores_export,
            "sub_results": sub_results,
        }

        try:
            json_path, html_path = _resolve_export_paths(export, client_info, "analyze")
            typer.echo(f"Export-Basis (absolut): {json_path.parent}")
            json_path.write_text(
                json.dumps(export_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            html = _render_basic_html(export_data)
            html_path.write_text(html, encoding="utf-8")
            typer.echo(f"Export gespeichert: {json_path}")
            typer.echo(f"HTML-Report gespeichert: {html_path}")
        except Exception as exc:
            typer.echo(f"Export fehlgeschlagen: {exc}")


@app.command()
def field_test(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09031999"),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    seed: str = typer.Option("field-seed", "--seed", help="Seed für prozedurale Feldtest-Kandidaten"),
    p_emotion: float = typer.Option(0.5, "--p-emotion", min=0.0, max=1.0, help="Einstufung emotionale Ebene [0,1]"),
    p_physisch: float = typer.Option(0.5, "--p-physisch", min=0.0, max=1.0, help="Einstufung physische Ebene [0,1]"),
    p_mental: float = typer.Option(0.5, "--p-mental", min=0.0, max=1.0, help="Einstufung mentale Ebene [0,1]"),
    p_astral: float = typer.Option(0.5, "--p-astral", min=0.0, max=1.0, help="Einstufung astrale Ebene [0,1]"),
    hardware_profile: str = typer.Option(
        "legacy",
        "--hardware-profile",
        help="Hardware-Profil: z.B. 'legacy' (Standard), 'windows' oder 'debian_server'",
    ),
    top_k: int = typer.Option(8, "--top-k", min=1, help="Anzahl der Top-Resonanzen im Bericht"),
    export: Path | None = typer.Option(
        None,
        "--export",
        help="Exportiert Ergebnisse des Feldtests als JSON-Datei",
    ),
) -> None:
    """Führt einen personalisierten Feldtest (Emotion/Physisch/Mental/Astral) durch."""

    groups = ["emotion", "physisch", "mental", "astral"]
    subgroup_svc = SubgroupService()
    # Für den Feldtest mehr Kandidaten erzeugen, damit pro Ebene genügend
    # unterschiedliche Items zur Verfügung stehen.
    items = subgroup_svc.generate_fullbody_candidates(groups, seed, k_total=128)
    if not items:
        typer.echo("Keine Feldtest-Kandidaten erzeugt.")
        raise typer.Exit(code=1)

    personal_profile = {
        "emotion": _clamp(p_emotion),
        "physisch": _clamp(p_physisch),
        "mental": _clamp(p_mental),
        "astral": _clamp(p_astral),
    }

    _profile = (hardware_profile or "legacy").strip().lower()

    # Profil-spezifische Auswahl der Entropiequelle.
    # - "legacy": HID bevorzugt, 2s Messdauer
    # - "windows": HID bevorzugt, leicht verlängerte Messdauer (3s)
    # - "debian_server": QRNG/GPU bevorzugt, HID ignoriert
    # Bei Ausfällen wird konservativ auf cpu_timer zurückgefallen.
    if _profile == "debian_server":
        duration = 2.0
        src = select_entropy_source(preferred=["qrng", "gpu", "network", "cpu_timer"])
        h_level = _clamp(src.sample_h_level(duration_s=duration))
        if src.name() in ("qrng", "gpu", "network") and h_level <= 0.0:
            fallback_src = select_entropy_source(preferred=["cpu_timer"])
            fallback_h = _clamp(fallback_src.sample_h_level(duration_s=duration))
            if fallback_h > h_level:
                src = fallback_src
                h_level = fallback_h
    else:
        duration = 3.0 if _profile == "windows" else 2.0
        src = select_entropy_source(preferred=["hid_sensor", "cpu_timer"])
        h_level = _clamp(src.sample_h_level(duration_s=duration))
        if src.name() == "hid_sensor" and h_level <= 0.0:
            fallback_src = select_entropy_source(preferred=["cpu_timer"])
            fallback_h = _clamp(fallback_src.sample_h_level(duration_s=duration))
            if fallback_h > h_level:
                src = fallback_src
                h_level = fallback_h

    profile = ClientProfile(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        image_signature=None,
        personal_profile=personal_profile,
    )

    analysis = AnalysisService(rate_database={}, h_level=h_level)
    client_rates = analysis.encode_profile(profile)
    client_entropy = analysis.resonator.holographic_entropy(client_rates)
    m_field = analysis.resonator.calculate_m_field(client_rates)
    heim_sig = analysis.resonator.heim_signature(client_rates)

    encoder = RateEncoder()
    client_personal_vector = encoder.personal_profile_to_vector(personal_profile)

    def resonance_fn(a: np.ndarray, b: np.ndarray) -> float:
        return float(analysis.resonator.resonance_score(a, b))

    nls_service = NlsService(items)
    scores = nls_service.compute_scores_v2(
        client_rates,
        client_entropy,
        resonance_fn,
        client_personal_vector=client_personal_vector,
    )

    # Optional: Fokus kann die Scores sanft gewichten, wenn aktiviert und gesetzt.
    # ERWEITERT 01.12.2025: Jetzt mit Copen-Rate-Resonanz
    if focus_weighting and (focus or "").strip():
        # Lookup-Tabellen für Gruppe und Copen-Rate erstellen
        label_to_group: Dict[str, str] = {}
        label_to_copen_rate: Dict[str, float] = {}
        for it in items:
            lbl = str(it.get("label", "") or "").strip()
            if not lbl or lbl in label_to_group:
                continue
            grp = str(it.get("group", "") or "").strip()
            label_to_group[lbl] = grp
            # Copen-Rate aus Item extrahieren (falls vorhanden)
            try:
                copen_rate = float(it.get("copen_rate", 0.0) or 0.0)
            except (TypeError, ValueError):
                copen_rate = 0.0
            label_to_copen_rate[lbl] = copen_rate

        scores_with_focus: List[Dict[str, object]] = []
        for entry in scores:
            lbl = str(entry.get("label", "") or "").strip()
            grp = label_to_group.get(lbl, "")
            item_copen_rate = label_to_copen_rate.get(lbl, 0.0)
            # Erweiterte Fokus-Gewichtung mit Copen-Rate-Resonanz
            m_focus = _compute_focus_multiplier_for_item(focus, grp, lbl, item_copen_rate)
            new_entry = dict(entry)
            new_entry["focus_multiplier"] = float(m_focus)
            new_entry["score"] = float(new_entry.get("score", 0.0) or 0.0) * m_focus
            scores_with_focus.append(new_entry)

        scores = scores_with_focus

    typer.echo("Morphic Engine V1 – Feldtest (Emotion/Physisch/Mental/Astral)")
    typer.echo(f"Klient: {first_name} {name}")
    typer.echo(
        "Personalprofil: "
        f"Emotion={personal_profile['emotion']:.2f}, "
        f"Physisch={personal_profile['physisch']:.2f}, "
        f"Mental={personal_profile['mental']:.2f}, "
        f"Astral={personal_profile['astral']:.2f}"
    )
    typer.echo(f"Morphic field: {m_field:.4f}")
    typer.echo(f"h_level (Hardware): {h_level:.3f} [{src.name()} / profile={_profile}]")
    typer.echo(f"Holographic entropy: {client_entropy:.4f}")
    typer.echo("Heim signature:")
    typer.echo("  " + ", ".join(f"{x:.3f}" for x in heim_sig))

    typer.echo("")
    typer.echo("Top Items (NLS v2, personalisiert):")
    # Doppelte Labels vermeiden: über die sortierten Scores iterieren und
    # jedes Label höchstens einmal berücksichtigen.
    seen_labels = set()
    top_scores = []
    for entry in scores:
        label = entry["label"]
        if label in seen_labels:
            continue
        seen_labels.add(label)
        top_scores.append(entry)
        if len(top_scores) >= top_k:
            break
    for entry in top_scores:
        label = entry["label"]
        score = entry["score"]
        rel = entry["reliability"]
        palign = entry.get("personal_alignment", 1.0)
        typer.echo(
            f"  - {label}: score={score:.4f}, rel={rel:.2f}, personal_align={palign:.2f}"
        )

    # Build label -> meta lookup from generated items
    meta_by_label: Dict[str, Dict[str, object]] = {}
    for it in items:
        lab = str(it.get("label", ""))
        if not lab or lab in meta_by_label:
            continue
        meta_by_label[lab] = it

    # Enrich NLS scores with group/potency/rates and 13-Ebenen-Resonanz
    enriched: List[Dict[str, object]] = []
    for e in scores:
        lab = str(e.get("label", ""))
        if not lab:
            continue
        m = meta_by_label.get(lab, {})
        group = str(m.get("group", "") or "")
        potency = m.get("potency")
        rates_vals = m.get("rates", [])
        try:
            rates_list = [float(x) for x in rates_vals] if rates_vals else []
        except Exception:
            rates_list = []
        s_res = float(e.get("resonance", 0.0) or 0.0)
        s_ent = float(e.get("entropy_alignment", 0.0) or 0.0)
        dv_val = int(max(1, min(6, 1 + round(5.0 * (1.0 - s_ent)))))

        lvl_id, lvl_val, lvl_text, copen_rate = _rates_to_level_info(rates_list, lab)

        enriched.append(
            {
                "label": lab,
                "score": float(e.get("score", 0.0) or 0.0),
                "resonance": s_res,
                "entropy_alignment": s_ent,
                "z_entropy": float(e.get("z_entropy", 0.0) or 0.0),
                "reliability": float(e.get("reliability", 1.0) or 1.0),
                "personal_alignment": float(e.get("personal_alignment", 1.0) or 1.0),
                "group": group,
                "potency": str(potency) if potency is not None else "-",
                "rates": rates_list,
                "dv": int(dv_val),
                "level": lvl_text,
                "level_id": int(lvl_id),
                "level_value": float(lvl_val),
                "copen_rate": float(copen_rate),
            }
        )

    # Map groups to legacy-style auto-* section names
    def _category_for_group(g: str) -> str:
        g = (g or "").strip().lower()
        mapping = {
            "bakterien": "auto-bakterien",
            "bakterien_fein": "auto-bakterien",
            "viren": "auto-viren",
            "viren_fein": "auto-viren",
            "parasiten": "auto-parasiten",
            "parasiten_fein": "auto-parasiten",
            "pilze": "auto-pilze",
            "pilze_fein": "auto-pilze",
            "schwermetalle": "auto-schwermetalle",
            "schwermetalle_tox": "auto-schwermetalle",
            "detox": "auto-detox",
            "mikrozirkulation": "auto-mikrozirkulation",
            "mitochondrien": "auto-mitochondrien",
            "entzuendung": "auto-entzündung",
            "allergene": "auto-allergene",
            "mikronaehrstoffe": "auto-mikronährstoffe",
            "wirbelsaeule": "auto-wirbelsäule",
            "odontone": "auto-odontone",
            "kreislauf": "auto-kreislauf",
            "chakren": "auto-chakren",
            "chakren_erweitert": "auto-chakren",
            "chakren_full": "auto-chakren",
            "nebenchakren": "auto-chakren",
            "meridiane": "auto-meridiane",
            "tcm_punkte": "auto-meridiane",
            "tcm_punkte_extended": "auto-meridiane",
            "tcm_full": "auto-meridiane",
            "endokrin": "auto-endokrin",
            # Remedies / Rezepturen – zusammengefasste Rubriken
            "homoeopathie_klassisch": "auto-homöopathie",
            "homoeopathie_klassisch_potenzen": "auto-homöopathie",
            "tcm_rezepturen": "auto-tcm-rezepturen",
            "tcm_rezepturen_potenzen": "auto-tcm-rezepturen",
            "spagyrik": "auto-spagyrik",
        }
        return mapping.get(g, f"auto-{g}" if g else "auto-sonstige")

    # Bucket entries per section
    sections_dict: Dict[str, Dict[str, object]] = {}
    for rec in enriched:
        cat = _category_for_group(str(rec.get("group", "")))
        sec = sections_dict.setdefault(cat, {"name": cat, "entries": []})
        sec["entries"].append(rec)

    # Compute per-section intensity and priority; sort entries by score desc
    def _priority(rel: float) -> str:
        if rel >= 0.66:
            return "hoch"
        if rel >= 0.33:
            return "mittel"
        return "niedrig"

    for sec in sections_dict.values():
        entries = sec["entries"]  # type: ignore[index]
        try:
            max_score = max(float(e.get("score", 0.0) or 0.0) for e in entries)
        except ValueError:
            max_score = 0.0
        for e in entries:
            s_val = float(e.get("score", 0.0) or 0.0)
            rel = s_val / max_score if max_score > 0.0 else 0.0
            e["intensity"] = rel
            e["priority"] = _priority(rel)
        entries.sort(key=lambda x: float(x.get("score", 0.0) or 0.0), reverse=True)

    max_per_section = 21
    for sec in sections_dict.values():
        entries = sec["entries"]  # type: ignore[index]
        highs = [e for e in entries if str(e.get("priority", "")) == "hoch"]
        mids = [e for e in entries if str(e.get("priority", "")) == "mittel"]
        if len(mids) > max_per_section:
            new_entries = highs + mids
        else:
            total_hm = len(highs) + len(mids)
            if total_hm <= max_per_section:
                new_entries = highs + mids
            else:
                slots_for_mid = max_per_section - len(highs)
                if slots_for_mid < 0:
                    slots_for_mid = 0
                new_entries = highs + mids[:slots_for_mid]
        sec["entries"] = new_entries

    sections = list(sections_dict.values())

    # Aggregates per section (Aus Subgruppen, Aus NLS, Kombiniert)
    def _rate_pair(lst: List[float]) -> List[float]:
        try:
            if not lst:
                return [0.0, 0.0]
            if len(lst) == 1:
                v = float(lst[0])
                return [v, v]
            return [float(lst[0]), float(lst[1])]
        except Exception:
            return [0.0, 0.0]

    aggregates_list: List[Dict[str, object]] = []
    for cat_name, sec in sections_dict.items():
        entries = sec["entries"]  # type: ignore[index]
        if not entries:
            continue
        vals = [_rate_pair(e.get("rates") or []) for e in entries]  # type: ignore[arg-type]
        n = len(vals)
        if n > 0:
            avg_sub = [sum(v[0] for v in vals) / n, sum(v[1] for v in vals) / n]
        else:
            avg_sub = [0.0, 0.0]
        weights = [float(e.get("score", 0.0) or 0.0) for e in entries]
        ws = sum(weights)
        if ws > 0.0:
            sum0 = 0.0
            sum1 = 0.0
            for e in entries:
                w = float(e.get("score", 0.0) or 0.0)
                r0, r1 = _rate_pair(e.get("rates") or [])  # type: ignore[arg-type]
                sum0 += w * r0
                sum1 += w * r1
            avg_nls = [sum0 / ws, sum1 / ws]
        else:
            avg_nls = avg_sub
        combined = [(avg_sub[0] + avg_nls[0]) / 2.0, (avg_sub[1] + avg_nls[1]) / 2.0]
        aggregates_list.append(
            {
                "name": cat_name,
                "subgroups_rates": [float(avg_sub[0]), float(avg_sub[1])],
                "nls_rates": [float(avg_nls[0]), float(avg_nls[1])],
                "combined_rates": [float(combined[0]), float(combined[1])],
            }
        )

    # Condensed therapy top across remedies
    therapy_cats = {"auto-homöopathie", "auto-tcm-rezepturen", "auto-spagyrik"}
    therapy_pool: List[Dict[str, object]] = []

    # Historische Haupt-Rubriken weiter berücksichtigen
    for cat in therapy_cats:
        sec = sections_dict.get(cat)
        if not sec:
            continue
        therapy_pool.extend(sec["entries"])  # type: ignore[index]

    # Zusätzlich alle Einträge aus Sektionen aufnehmen, deren Gruppen echte Remedies sind
    for sec in sections_dict.values():
        entries = sec.get("entries") or []  # type: ignore[assignment]
        for e in entries:
            grp_val = str(e.get("group", "") or "").strip().lower()
            if grp_val and _is_remedy_group(grp_val):
                therapy_pool.append(e)
    therapy_pool_sorted = sorted(
        therapy_pool, key=lambda x: float(x.get("score", 0.0) or 0.0), reverse=True
    )
    therapy_top: List[Dict[str, object]] = []
    seen_lbl: set[str] = set()
    for e in therapy_pool_sorted:
        lbl = str(e.get("label", ""))
        if not lbl or lbl in seen_lbl:
            continue
        seen_lbl.add(lbl)
        therapy_top.append(
            {
                "label": lbl,
                "score": float(e.get("score", 0.0) or 0.0),
                "potency": str(e.get("potency", "-") or "-"),
                "group": str(e.get("group", "") or ""),
                "dv": int(e.get("dv", 0) or 0),
                "rates": e.get("rates", []),
                "priority": str(e.get("priority", "")),
            }
        )
        if len(therapy_top) >= 24:
            break

    # Build export data
    client_info: Dict[str, str] = {
        "name": name,
        "first_name": first_name,
        "birth_date": birth_date,
        "birth_place": birth_place,
    }
    export_data: Dict[str, object] = {
        "command": "multiplex_scan",
        "hardware_profile": _profile,
        "hardware_source": src.name(),
        "h_level": float(h_level),
        "client": client_info,
        "focus": focus,
        "personal_profile": personal_profile,
        "metrics": {
            "morphic_field": float(m_field),
            "holographic_entropy": float(client_entropy),
            "heim_signature": [float(x) for x in heim_sig],
        },
        "sections": sections,
        "aggregates": aggregates_list,
        "therapy_top": therapy_top,
    }

    if export is not None:
        try:
            json_path, html_path = _resolve_export_paths(export, client_info, "multiplex_scan", filename_suffix, scan_type, session_id)
            typer.echo(f"Export-Basis (absolut): {json_path.parent}")
            txt_path = html_path.with_suffix(".txt")
            typer.echo(f"Export-Pfade: JSON -> {json_path}")
            typer.echo(f"Export-Pfade: HTML -> {html_path}")
            typer.echo(f"Export-Pfade: TXT  -> {txt_path}")
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            _atomic_write_text(json_path, json_str)
            html = _render_multiplex_html(export_data)
            _atomic_write_text(html_path, html)
            txt = _render_multiplex_txt(export_data)
            _atomic_write_text(txt_path, txt)
            try:
                sections_hm = export_data.get("sections") or []
                high_mid: List[Dict[str, object]] = []
                for sec in sections_hm:
                    entries = sec.get("entries") or []  # type: ignore[assignment]
                    for e in entries:
                        prio = str(e.get("priority", ""))
                        if prio not in ("hoch", "mittel"):
                            continue
                        try:
                            sc = float(e.get("score", 0.0) or 0.0)
                        except Exception:
                            sc = 0.0
                        label_hm = str(e.get("label", ""))
                        if not label_hm:
                            continue
                        try:
                            cr = float(e.get("copen_rate", 0.0) or 0.0)
                        except Exception:
                            cr = 0.0
                        high_mid.append(
                            {
                                "label": label_hm,
                                "copen_rate": cr,
                                "score": sc,
                                "priority": prio,
                            }
                        )

                if high_mid:
                    high_mid_sorted = sorted(
                        high_mid,
                        key=lambda r: float(r.get("score", 0.0) or 0.0),
                        reverse=True,
                    )
                    labels_lines: List[str] = []
                    copen_lines: List[str] = []
                    for rec in high_mid_sorted:
                        labels_lines.append(str(rec.get("label", "")))
                        try:
                            cr_val = float(rec.get("copen_rate", 0.0) or 0.0)
                            if float(cr_val).is_integer():
                                copen_lines.append(f"{int(cr_val)}")
                            else:
                                copen_lines.append(f"{cr_val:.4f}")
                        except Exception:
                            copen_lines.append("0")

                    base_stem = txt_path.with_suffix("").name
                    labels_path = txt_path.with_name(base_stem + "_labels_hoch_mittel.txt")
                    rates_path = txt_path.with_name(base_stem + "_copen_hoch_mittel.txt")
                    if labels_lines:
                        _atomic_write_text(labels_path, "\n".join(labels_lines))
                    if copen_lines:
                        _atomic_write_text(rates_path, "\n".join(copen_lines))
            except Exception:
                pass
            ok_json = json_path.exists() and json_path.stat().st_size > 0
            ok_html = html_path.exists() and html_path.stat().st_size > 0
            ok_txt = txt_path.exists() and txt_path.stat().st_size > 0
            typer.echo(f"JSON geschrieben: {'OK' if ok_json else 'FEHLER'} -> {json_path}")
            typer.echo(f"HTML geschrieben: {'OK' if ok_html else 'FEHLER'} -> {html_path}")
            typer.echo(f"TXT geschrieben:  {'OK' if ok_txt else 'FEHLER'} -> {txt_path}")
            if ok_json:
                typer.echo(f"Export gespeichert: {json_path}")
            if ok_html:
                typer.echo(f"HTML-Report gespeichert: {html_path}")
            if ok_txt:
                typer.echo(f"TXT-Report gespeichert: {txt_path}")
        except Exception as exc:
            typer.echo(f"Export fehlgeschlagen: {exc}")
    fam_best: Dict[str, Dict[str, float | str]] = {}
    fam_top: Dict[str, List[Dict[str, float | str]]] = {}
    fam_seen: Dict[str, set[str]] = {}
    for entry in scores:
        label = entry["label"]
        score = entry["score"]
        fam = None
        if label.startswith("Emotion ") or label.startswith("Emotion –"):
            fam = "Emotion"
        elif label.startswith("Physisch ") or label.startswith("Physisch –"):
            fam = "Physisch"
        elif label.startswith("Mental ") or label.startswith("Mental –"):
            fam = "Mental"
        elif label.startswith("Astral ") or label.startswith("Astral –"):
            fam = "Astral"
        if fam is None:
            continue
        best = fam_best.get(fam)
        if best is None or float(score) > float(best["score"]):
            fam_best[fam] = {"label": label, "score": float(score)}
        seen = fam_seen.setdefault(fam, set())
        if label in seen:
            continue
        seen.add(label)
        lst = fam_top.setdefault(fam, [])
        if len(lst) < 3:
            lst.append({"label": label, "score": float(score)})

    typer.echo("")
    typer.echo("Beste Resonanzen je Ebene (Top 3):")
    for fam in ("Emotion", "Physisch", "Mental", "Astral"):
        entries = fam_top.get(fam, [])
        if not entries:
            continue
        typer.echo(f"  {fam}:")
        for e in entries:
            typer.echo(f"    - {e['label']} ({e['score']:.4f})")

    # (Kein zweiter Exportblock hier; der vorherige Block schreibt JSON+HTML bereits korrekt.)
@app.command("multiplex-scan")
def multiplex_scan(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09041966"),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    profile: str = typer.Option(
        "pathogen",
        "--profile",
        "-P",
        help="Multiplex-Profil: 'pathogen', 'toxin', 'regulation', 'full' (Alias: 'therapy')",
    ),
    seed: str = typer.Option("multiplex-seed", "--seed", help="Seed für prozedurale Multiplex-Kandidaten"),
    p_emotion: float = typer.Option(0.5, "--p-emotion", min=0.0, max=1.0, help="Einstufung emotionale Ebene [0,1]"),
    p_physisch: float = typer.Option(0.5, "--p-physisch", min=0.0, max=1.0, help="Einstufung physische Ebene [0,1]"),
    p_mental: float = typer.Option(0.5, "--p-mental", min=0.0, max=1.0, help="Einstufung mentale Ebene [0,1]"),
    p_astral: float = typer.Option(0.5, "--p-astral", min=0.0, max=1.0, help="Einstufung astrale Ebene [0,1]"),
    hardware_profile: str = typer.Option(
        "windows",
        "--hardware-profile",
        help="Hardware-Profil: z.B. 'legacy', 'windows' oder 'debian_server'",
    ),
    focus: str = typer.Option(
        "",
        "--focus",
        help="Optionaler Fokus / Symptom (z.B. 'Narbenstörung')",
    ),
    k_total: int = typer.Option(512, "--k-total", min=16, help="Anzahl der Multiplex-Kandidaten"),
    top_k: int = typer.Option(32, "--top-k", min=1, help="Anzahl der Top-Resonanzen im Bericht"),
    export: Path | None = typer.Option(
        None,
        "--export",
        help="Exportiert Ergebnisse des Multiplex-Scans als JSON+HTML",
    ),
    synergy: bool = typer.Option(
        True,
        "--synergy/--no-synergy",
        help="Aktiviert Quantum-Synergy Analyse für synergistische Kombinationen",
    ),
    synergy_combos: int = typer.Option(
        4,
        "--synergy-combos",
        min=2,
        max=5,
        help="Anzahl Items pro synergistischer Kombination (2-5)",
    ),
    synergy_threshold: float = typer.Option(
        6.0,
        "--synergy-threshold",
        min=0.0,
        max=10.0,
        help="Mindest-Score für Synergy-Kombinationen (0-10, Standard: 6.0 wie früher)",
    ),
    tcm_type: str = typer.Option(
        "",
        "--tcm-type",
        help=(
            "Optionaler TCM-Grundtyp, z.B. 'Holz-Leber', 'Feuer-Herz', "
            "'Erde-Milz', 'Metall-Lunge', 'Wasser-Niere'."
        ),
    ),
    planet_type: str = typer.Option(
        "",
        "--planet-type",
        help=(
            "Optionaler Planetentyp, z.B. 'Mars', 'Venus', 'Sonne', "
            "'Saturn', 'Neptun'."
        ),
    ),
    debug_groups: bool = typer.Option(
        False,
        "--debug-groups",
        help="Zeigt Verteilung der Multiplex-Kandidaten pro Gruppe an",
    ),
    influence_compare: bool = typer.Option(
        False,
        "--influence-compare",
        help=(
            "Berechnet zusätzliche Influence-Scores (TCM+Organuhr) im JSON-Export "
            "zur Gegenüberstellung von Basis- und beeinflusstem Scoring."
        ),
    ),
    db_analysis_mode: bool = typer.Option(
        False,
        "--db-analysis",
        help=(
            "Aktiviert experimentelle Bruce-Copen-DB-Analyse im JSON-Export "
            "(zusätzlicher Block 'db_analysis')."
        ),
    ),
    morphic_field: bool = typer.Option(
        True,  # GEÄNDERT 01.12.2025: Standardmäßig aktiviert für authentischere Ergebnisse
        "--morphic-field/--no-morphic-field",
        help=(
            "Aktiviert morphische Feld-Analyse im JSON-Export "
            "(zusätzlicher Block 'morphic_field'). Standard: aktiviert."
        ),
    ),
    mf_geometry: str = typer.Option(
        "",
        "--mf-geometry",
        help=(
            "Optionale geometrische Form fuer die morphische Feld-Analyse "
            "(z.B. 'flower_of_life', 'merkaba', 'torus')."
        ),
    ),
    mf_intention: str = typer.Option(
        "",
        "--mf-intention",
        help=(
            "Optionale Intention fuer die morphische Feld-Analyse "
            "(z.B. 'healing', 'detox', 'protection', 'harmonization')."
        ),
    ),
    mf_use_hardware: bool = typer.Option(
        True,  # GEÄNDERT 01.12.2025: Standardmäßig aktiviert für Kozyrev-Integration
        "--mf-use-hardware/--no-mf-use-hardware",
        help=(
            "Verwendet Hardware-Modulation (h_level) in der morphischen Feld-Analyse. "
            "Standard: aktiviert (Kozyrev-inspiriert)."
        ),
    ),
    focus_weighting: bool = typer.Option(
        True,
        "--focus-weighting/--no-focus-weighting",
        help=(
            "Steuert, ob der gesetzte Fokus das Scoring sanft gewichten darf "
            "(Multiplikator bis ca. +5%)."
        ),
    ),
    export_3d: bool = typer.Option(
        False,
        "--export-3d",
        help="Generiert eine 3D-JSON-Datei für den Morphic Viewer."
    ),
    show_progress: bool = typer.Option(
        True,
        "--progress/--no-progress",
        help="Zeigt Fortschritts-Updates während des Scans."
    ),
    use_hybrid_entropy: bool = typer.Option(
        False,
        "--hybrid-entropy",
        help="Verwendet Hybrid-Entropie (mehrere Quellen kombiniert)."
    ),
    show_confidence: bool = typer.Option(
        True,
        "--confidence/--no-confidence",
        help="Zeigt Konfidenz-Bewertung im Report."
    ),
    intention: str = typer.Option(
        "",
        "--intention",
        "-I",
        help=(
            "Aktive Intention für Score-Gewichtung: "
            "'healing' (Heilung), 'clearing' (Klärung), 'protection' (Schutz), "
            "'transformation', 'harmonization', 'connection', 'activation'. "
            "Leer = keine Gewichtung."
        ),
    ),
    filename_suffix: str = typer.Option(
        "",
        "--filename-suffix",
        help="Optionaler Suffix für den Dateinamen (z.B. Profilname bei Top-3 Scan)",
    ),
    scan_type: str = typer.Option(
        "SINGLE",
        "--scan-type",
        help="Scan-Typ für Ordner-Label: 'SINGLE', 'top5_session', etc.",
    ),
    session_id: str = typer.Option(
        "",
        "--session-id",
        help="Session-ID für Top-5 Gruppierung (alle Profile derselben Session)",
    ),
    # === ERWEITERTE KLIENTEN-MODIFIKATOREN (optional) ===
    client_gender: str = typer.Option(
        "",
        "--gender",
        "-G",
        help="Geschlecht des Klienten: 'm' (männlich), 'f' (weiblich), 'd' (divers). Leer = neutral.",
    ),
    client_weight: float = typer.Option(
        0.0,
        "--weight",
        "-W",
        help="Gewicht in kg (z.B. 75.5). 0 = nicht angegeben.",
    ),
    client_height: int = typer.Option(
        0,
        "--height",
        "-H",
        help="Größe in cm (z.B. 178). 0 = nicht angegeben.",
    ),
    client_stress: int = typer.Option(
        0,
        "--stress-level",
        help="Stress-Level 1-10 (1=niedrig, 10=sehr hoch). 0 = nicht angegeben.",
    ),
    client_sleep: float = typer.Option(
        0.0,
        "--sleep-hours",
        help="Durchschnittliche Schlafstunden pro Nacht. 0 = nicht angegeben.",
    ),
    client_emf: str = typer.Option(
        "",
        "--emf-exposure",
        help="EMF-Belastung: 'niedrig', 'mittel', 'hoch'. Leer = nicht angegeben.",
    ),
) -> None:
    """Führt einen erweiterten Multiplex-Scan über vordefinierte Gruppenprofile durch."""

    # Phase 2: Hardware Detection & Auto-Config
    sys_info = get_full_system_report()
    typer.echo(f"Hardware-Profil: {sys_info['profile']} | CPU: {sys_info['cpu']['physical_cores']} Kerne")
    if sys_info['gpu']['has_gpu']:
        typer.echo(f"GPU-Beschleunigung: AKTIV ({sys_info['gpu']['device_name']})")
    else:
        typer.echo("GPU-Beschleunigung: INAKTIV (CPU Mode)")

    s_info = sys_info.get('sensors', {})
    if s_info.get('count', 0) > 0:
        typer.echo(f"Externe Sensoren: {s_info['count']} erkannt")
        for d in s_info.get('devices', []):
            typer.echo(f"  - [{d['type']}] {d['name']}")

    typer.echo("-" * 60)

    prof = (profile or "pathogen").strip().lower()

    # Phase 1 Modularisierung: Registry Check
    registry_groups = get_groups_for_profile(prof)
    if registry_groups:
        groups = registry_groups
    elif prof == "pathogen":
        # Fokus-Profil: Pathogene Erreger (Bakterien, Viren, Parasiten, Pilze)
        groups = [
            # Basis-Erreger
            "bakterien",
            "viren",
            "parasiten",
            "pilze",
            # Fein-Differenzierung
            "bakterien_fein",
            "viren_fein",
            "parasiten_fein",
            "pilze_fein",
            # Detaillierte Erreger-Analyse
            "bakterien_detailliert_fein",
            "viren_detailliert_fein",
            "parasiten_detailliert_fein",
            "pilze_detailliert_fein",
            # Biofilme & Infektionssymptome
            "biofilme_fein",
            "infektions_symptome_fein",
            # Immunabwehr
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "immunstaerkung_remedies_multiplex",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "toxin":
        # Fokus-Profil: Toxine, Schwermetalle, Umweltbelastungen
        groups = [
            # Schwermetalle
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            # Chemikalien & Pestizide
            "chemikalien_tox",
            "chemikalien_detailliert_fein",
            "pestizide_tox",
            # Strahlung & EMF
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "emf_fein",
            # Geopathie & Umwelt
            "geopathie",
            "geopathie_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Toxin-Symptome & Entgiftung
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_remedies_multiplex",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "regulation":
        # Fokus-Profil: Energetische & vegetative Regulation
        groups = [
            # Chakren & Energiezentren
            "chakren",
            "chakren_full",
            "chakren_detailliert_fein",
            "chakren_erweitert",
            "nebenchakren",
            "energetische_blockaden_fein",
            # Meridiane & TCM
            "meridiane",
            "meridiane_detailliert_fein",
            "tcm_punkte",
            "tcm_punkte_extended",
            "tcm_full",
            "extra_meridiane",
            # Zahn-Organ-Beziehungen
            "zahnorgane",
            "odontone",
            # Vegetative Regulation
            "nervensystem_vegetativ",
            "nervensystem_neurotransmitter_fein",
            # Zellregulation
            "mikrozirkulation",
            "mitochondrien",
            "entzuendung",
            # Hormonelle Regulation
            "endokrin",
            "hormone_symptome_fein",
            # Entgiftung & Nährstoffe
            "detox",
            "mikronaehrstoffe",
            "orthomolekular_therapie_multiplex",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "meridiane_detailliert":
        # Fokus-Profil: TCM, Meridiane, Akupunktur
        groups = [
            # Meridiane
            "meridiane",
            "meridiane_detailliert_fein",
            "extra_meridiane",
            # TCM Punkte & Rezepturen
            "tcm_punkte",
            "tcm_punkte_extended",
            "tcm_full",
            "tcm_rezepturen",
            "tcm_rezepturen_multiplex",
            # Chakren & Energie
            "chakren",
            "chakren_full",
            "chakren_detailliert_fein",
            "chakren_erweitert",
            "energetische_blockaden_fein",
            # Psychosomatik
            "emotionale_blockaden_fein",
            "psychosomatik_fein",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("full", "therapy"):
        # Umfassendes Profil: reale/verfeinerte Gruppen für maximale Multiplex-Analyse
        groups = [
            # Basis-Systeme
            "kreislauf",
            "kreislauf_fein",
            "chakren",
            "chakren_full",
            "chakren_erweitert",
            "nebenchakren",
            "meridiane",
            "meridiane_detailliert_fein",
            "tcm_punkte",
            "tcm_punkte_extended",
            "tcm_full",
            "extra_meridiane",

            # Pathogene (Basis + Fein)
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",

            # Toxine & Belastungen
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "strahlung_schutz_multiplex",
            "geopathie_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",

            # Regulation & Systeme
            "endokrin",
            "hormone_schilddruese_fein",
            "hormone_geschlecht_fein",
            "detox",
            "entgiftung_organe_fein",
            "mikrozirkulation",
            "mitochondrien",
            "entzuendung",
            "allergene",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "mikronaehrstoffe",
            "orthomolekular_mineralien_fein",
            "orthomolekular_vitamine_fein",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "zahnorgane",
            "zahnorgane_fein",
            "odontone",
            "schlaf",
            "schlafstoerungen_fein",

            # Remedies & Therapien
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "homoeopathie_sarcoden",
            "tcm_rezepturen",
            "tcm_rezepturen_potenzen",
            "tcm_rezepturen_multiplex",
            "spagyrik",
            "spagyrik_multiplex",
            "farbtherapie",
            "edelsteine",
            "edelsteine_chakren",
            "edelsteine_schutz",
            "bachblueten_38",
            "bachblueten_multiplex",

            # Erweiterte Protokolle / Frequenzen
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("dizziness", "schwindel"):
        # Fokus-Profil: Schwindel (multifaktorielle Ursachen)
        groups = [
            # Spezifische Schwindel-Gruppen
            "schwindel_hws",
            "schwindel_kreislauf",
            "schwindel_medikament",
            "schwindel_vestibular",
            "schwindel_vestibular_fein",
            "schwindel_zentral",
            "schwindel_zentral_fein",
            # Kreislauf & Herz
            "kreislauf",
            "kreislauf_fein",
            "herz_fein",
            # Wirbelsäule & Statik
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            # Sinnesorgane & Nerven
            "auge_fein",
            "ohr_fein",
            "nervensystem_zns_fein",
            "nervensystem_hirnnerven_fein",
            "nervensystem_vegetativ",
            # Systemische Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "schwindel_detailliert":
        groups = [
            "schwindel_hws",
            "schwindel_kreislauf",
            "schwindel_medikament",
            "schwindel_vestibular",
            "schwindel_vestibular_fein",
            "schwindel_zentral",
            "schwindel_zentral_fein",
            "kreislauf",
            "kreislauf_fein",
            "herz_fein",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "auge_fein",
            "ohr_fein",
            "nervensystem_zns_fein",
            "nervensystem_hirnnerven_fein",
            "nervensystem_vegetativ",
            "nerven_symptome_fein",
            "nerven_pathologien_fein",
            "nerven_remedies_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("circulation", "durchblutung"):
        # Fokus-Profil: Durchblutung & Gefäßsystem
        groups = [
            # Herz-Kreislauf & Blut
            "kreislauf",
            "kreislauf_fein",
            "herz_fein",
            "blut_fein",

            # Mikrozirkulation & strukturelle Achsen
            "mikrozirkulation",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "zahnorgane",
            "zahnorgane_fein",
            "odontone",

            # Meridiane & TCM
            "meridiane",
            "meridiane_detailliert_fein",
            "tcm_punkte",
            "tcm_punkte_extended",
            "tcm_full",

            # Toxische Belastungen
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",

            # Regulation & Systeme
            "entzuendung",
            "endokrin",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",

            # Remedies & komplementäre Verfahren
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("respiration", "atmung"):
        # Fokus-Profil: Atmung (Lunge, Bronchien, Atemwege)
        groups = [
            # Atmungs-Systeme (erweitert + fein)
            "atmung_lunge",
            "atmung_bronchien",
            "atmung_zwerchfell",
            "atmung_nase",
            "atmung_rachen",
            "atmung_lunge_fein",
            "atmung_symptome_fein",
            "atmung_pathologien_fein",

            # Kreislauf-Achse
            "kreislauf",
            "kreislauf_fein",

            # Pathogene (Atemwegsinfekte)
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",

            # Toxische Atembelastungen
            "schwermetalle",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",

            # Immun & Regulation
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",

            # Remedies & Therapien
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "atmung_remedies_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "knochen_detailliert":
        groups = [
            "knochen_gelenke",
            "knochen_gelenke_fein",
            "knochen_symptome_fein",
            "knochen_pathologien_fein",
            "knochen_osteoporose",
            "knochen_osteoblasten",
            "knochen_osteoklasten",
            "knochen_knorpel",
            "knochen_remedies_multiplex",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_sakral",
            "wirbelsaeule_bandscheiben",
            "wirbelsaeule_bandscheiben_fein",
            "wirbelsaeule_symptome_fein",
            "wirbelsaeule_pathologien_fein",
            "wirbelsaeule_remedies_multiplex",
            "muskulatur_fein",
            "faszien_fein",
            "schmerz_ruecken",
            "schmerz_gelenk",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "orthomolekular_therapie_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "wirbelsaeule_detailliert":
        groups = [
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_sakral",
            "wirbelsaeule_bandscheiben",
            "wirbelsaeule_bandscheiben_fein",
            "wirbelsaeule_facetten",
            "wirbelsaeule_symptome_fein",
            "wirbelsaeule_pathologien_fein",
            "wirbelsaeule_remedies_multiplex",
            "knochen_gelenke",
            "knochen_gelenke_fein",
            "knochen_symptome_fein",
            "knochen_pathologien_fein",
            "knochen_remedies_multiplex",
            "nervensystem_zns_fein",
            "nervensystem_pns_fein",
            "nerven_symptome_fein",
            "nerven_pathologien_fein",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "stoerfelder_toxisch":
        groups = [
            "entgiftung_leber_phase1",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_haut",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            "entgiftung_remedies_multiplex",
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "luft_symptome_fein",
            "luft_remedies_multiplex",
            "nahrung_symptome_fein",
            "nahrung_unvertraeglichkeiten_fein",
            "nahrung_remedies_multiplex",
            "geopathie_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "strahlung_schutz_multiplex",
            "magnetfeld",
            "entzuendung",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_therapie_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("immune", "immunsystem"):
        # Fokus-Profil: Immunsystem (angeboren, erworben, Autoimmunität)
        groups = [
            # Immunsystem (erweitert + fein)
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "immunsystem_zytokine",
            "immunsystem_zytokine_fein",
            "immunsystem_autoimmun",
            "immunsystem_autoimmun_fein",

            # Immunsystem-Antikörper
            "immunsystem_antikoerper",
            # Lymphsystem & Entgiftungsachsen
            "lymphsystem_lymphknoten",
            "lymphsystem_lymphknoten_fein",
            "lymphsystem_milz",
            "lymphsystem_thymus",
            "lymphsystem_tonsillen",
            "entgiftung_lymphe",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_organe_fein",

            # Pathogene
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",

            # Belastungen, die das Immunsystem schwächen
            "schwermetalle",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",

            # Mikronährstoffe & Regulation
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "entzuendung",

            # Remedies (systemisch, nosodisch, miasmatisch)
            "homoeopathie_nosoden",
            "homoeopathie_isopathie",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "miasmatik_remedies_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("detox", "entgiftung"):
        # Fokus-Profil: Entgiftung (Leber, Niere, Lymphe, Haut, Darm)
        groups = [
            # Entgiftungssysteme
            "entgiftung_leber_phase1",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_haut",
            "entgiftung_organe_fein",
            "entgiftung_remedies_multiplex",
            "entgiftung_symptome_fein",
            # Belastungen
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("heavy_metals", "heavy-metal", "schwermetalle"):
        # Fokus-Profil: Schwermetalle & Ausleitung
        groups = [
            # Schwermetalle detailliert
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            # Toxin-Symptome
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Entgiftungsachsen
            "entgiftung_leber_phase1",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            "entgiftung_remedies_multiplex",
            # Mikronährstoffe für Ausleitung
            "mikronaehrstoffe",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "narben_entstoerung_energetisch":
        groups = [
            # Energetische Stoerfelder & Achsen
            "energetische_blockaden_fein",
            "meridiane",
            "meridiane_detailliert_fein",
            "tcm_punkte",
            "tcm_punkte_extended",
            "tcm_full",
            "extra_meridiane",
            "chakren",
            "chakren_full",
            "chakren_detailliert_fein",
            "chakren_erweitert",
            # Remedies & innere Regulation
            "energie_remedies_multiplex",
            "orthomolekular_therapie_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "narben_entstoerung_gewebe_remedies":
        groups = [
            # Haut / Narben / Zahnstorferlder
            "haut_detailliert_fein",
            "energetische_blockaden_fein",
            "zahnorgane",
            "zahnorgane_fein",
            "odontone",
            # Entgiftung & Gewebeachsen
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_haut",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            # Umwelt- und Materialbelastungen
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Remedies & Mikronaehrstoffe
            "energie_remedies_multiplex",
            "entgiftung_remedies_multiplex",
            "orthomolekular_therapie_multiplex",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Hersteller-spezifische Remedy-Gruppen (NEU für Narben)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "schwermetalle_sanft_multiplex":
        groups = [
            # Schwermetalle & Toxin-Symptome
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "toxine_symptome_fein",
            # Umweltquellen
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Entgiftungssysteme (sanft, breit)
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            # Remedies & innere Regulation
            "toxine_remedies_multiplex",
            "entgiftung_remedies_multiplex",
            "orthomolekular_therapie_multiplex",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("radiation", "strahlung"):
        # Fokus-Profil: Strahlenbelastungen (EMF, Umwelt, Schutz)
        groups = [
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "strahlung_schutz_multiplex",
            "magnetfeld",
            "geopathie_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "strahlung_detailliert":
        groups = [
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "strahlung_schutz_multiplex",
            "magnetfeld",
            "geopathie_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "luft_symptome_fein",
            "luft_remedies_multiplex",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "energie_remedies_multiplex",
            "psyche_remedies_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("teeth", "zahn", "zaehne", "zähne"):
        # Fokus-Profil: Zahn-Organ-System, Materialien, Störfelder
        groups = [
            # Zähne & Kiefer
            "zahnorgane",
            "zahnorgane_fein",
            "zahnorgane_frontzaehne",
            "zahnorgane_quadrant1",
            "zahnorgane_quadrant2",
            "zahnorgane_quadrant3",
            "zahnorgane_quadrant4",
            "zahnorgane_weisheitszaehne",
            "zahnorgane_kiefergelenk",
            "zahnorgane_kiefer_herde",
            "zahn_materialien_fein",
            "zahn_pathologien_fein",
            "zahn_symptome_fein",
            "zahn_remedies_multiplex",
            # Zugehörige Achsen (Wirbelsäule, Statik, Nervensystem)
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_remedies_multiplex",
            "nervensystem_zns_fein",
            # Systemische Remedies ergänzen
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "zahn_detailliert":
        groups = [
            "zahnorgane",
            "zahnorgane_fein",
            "zahnorgane_frontzaehne",
            "zahnorgane_quadrant1",
            "zahnorgane_quadrant2",
            "zahnorgane_quadrant3",
            "zahnorgane_quadrant4",
            "zahnorgane_weisheitszaehne",
            "zahnorgane_kiefergelenk",
            "zahnorgane_kiefer_herde",
            "zahn_materialien_fein",
            "zahn_pathologien_fein",
            "zahn_symptome_fein",
            "zahn_remedies_multiplex",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_remedies_multiplex",
            "knochen_gelenke",
            "knochen_gelenke_fein",
            "knochen_symptome_fein",
            "knochen_pathologien_fein",
            "knochen_osteoporose",
            "knochen_osteoblasten",
            "knochen_osteoklasten",
            "knochen_knorpel",
            "knochen_remedies_multiplex",
            "nervensystem_zns_fein",
            "nervensystem_vegetativ",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "haut_detailliert":
        # Fokus-Profil: Haut (Dermatologie, Allergien, Entgiftung)
        groups = [
            # Haut-spezifisch
            "haut_detailliert_fein",
            "hautprobleme",
            "hautprobleme_fein",
            # Entgiftung über Haut
            "entgiftung_haut",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_symptome_fein",
            # Durchblutung & Versorgung
            "mikrozirkulation",
            "kreislauf_fein",
            # Immunsystem (Allergien, Autoimmun)
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "immunsystem_autoimmun_fein",
            "entzuendung",
            # Pathogene (Hautinfektionen)
            "bakterien_fein",
            "pilze_fein",
            "viren_fein",
            # Psychosomatik (Haut als Spiegel)
            "psychosomatik_fein",
            "emotionale_blockaden_fein",
            # Mikronährstoffe
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "haut_detailliert_toxisch":
        groups = [
            "haut_detailliert_fein",
            "hautprobleme_fein",
            "hautprobleme",
            "entgiftung_haut",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "mikrozirkulation",
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "luft_symptome_fein",
            "luft_remedies_multiplex",
            "nahrung_symptome_fein",
            "nahrung_unvertraeglichkeiten_fein",
            "nahrung_remedies_multiplex",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "immunsystem_autoimmun_fein",
            "immunsystem_zytokine_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_therapie_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            # Zahn- und Kieferachsen
            "zahnorgane",
            "zahnorgane_fein",
            "zahnorgane_frontzaehne",
            "zahnorgane_quadrant1",
            "zahnorgane_quadrant2",
            "zahnorgane_quadrant3",
            "zahnorgane_quadrant4",
            "zahnorgane_weisheitszaehne",
            "zahnorgane_kiefergelenk",
            "zahnorgane_kiefer_herde",
            "zahn_materialien_fein",
            "zahn_pathologien_fein",
            "zahn_symptome_fein",
            "zahn_remedies_multiplex",
            # Wirbelsäule & Nervensystem als Zahn-Haut-Achse
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_remedies_multiplex",
            "nervensystem_zns_fein",
            "nervensystem_vegetativ",
            # Systemische Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "auge_detailliert":
        groups = [
            # Anatomie & Funktion Auge
            "auge_fein",
            "nervensystem_hirnnerven_fein",
            "nervensystem_zns_fein",
            "wirbelsaeule_hws",
            "mikrozirkulation",
            # Pathogene & Belastungen
            "bakterien_detailliert_fein",
            "viren_detailliert_fein",
            "pilze_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            # Entgiftung & Immun
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_organe_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            # Orthomolekular & Nährstoffe
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "orthomolekular_therapie_multiplex",
            # Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "ohr_detailliert":
        groups = [
            # Anatomie & Funktion Ohr / Gleichgewicht
            "ohr_fein",
            "schwindel_vestibular_fein",
            "schwindel_zentral_fein",
            "nervensystem_hirnnerven_fein",
            "nervensystem_zns_fein",
            "nervensystem_vegetativ",
            "wirbelsaeule_hws",
            # Pathogene & Toxine
            "bakterien_detailliert_fein",
            "viren_detailliert_fein",
            "pilze_detailliert_fein",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            # Entgiftung & Immun
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_organe_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            # Nerven-spezifische Symptomgruppen & Remedies
            "nerven_symptome_fein",
            "nerven_pathologien_fein",
            "nerven_remedies_multiplex",
            "anti_infektions_remedies_multiplex",
            "immunstaerkung_remedies_multiplex",
            # Orthomolekular & Systemische Remedies
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "leber_detailliert":
        groups = [
            # Leber-Entgiftungsphasen & Enzyme
            "entgiftung_leber_phase1",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            # Entgiftungsachsen
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_haut",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            # Verdauung / Leber-Galle-Achse
            "verdauung_leber",
            "verdauung_galle",
            "verdauung_pankreas",
            "verdauung_magen",
            "verdauung_duenndarm",
            "verdauung_dickdarm",
            "verdauung_mikrobiom",
            "verdauung_barriere",
            "verdauung_duenndarm_fein",
            "verdauung_dickdarm_fein",
            "verdauung_mikrobiom_fein",
            "verdauung_symptome_fein",
            "verdauung_pathologien_fein",
            # Toxine & Schwermetalle
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Immun & Entzündung
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "immunsystem_zytokine_fein",
            "entzuendung",
            # Orthomolekular & Mikronährstoffe
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "orthomolekular_multiplex",
            "orthomolekular_therapie_multiplex",
            # Entgiftungs- und Verdauungs-Remedies
            "entgiftung_remedies_multiplex",
            "verdauung_remedies_multiplex",
            # Systemische Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "galle_detailliert":
        groups = [
            # Galle & hepatobiliäre Achse
            "verdauung_galle",
            "verdauung_leber",
            "verdauung_pankreas",
            "verdauung_magen",
            "verdauung_duenndarm",
            "verdauung_dickdarm",
            "verdauung_mikrobiom",
            "verdauung_barriere",
            "verdauung_duenndarm_fein",
            "verdauung_dickdarm_fein",
            "verdauung_mikrobiom_fein",
            "verdauung_symptome_fein",
            "verdauung_pathologien_fein",
            # Entgiftung
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            # Toxine & Immun
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "toxine_symptome_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            # Orthomolekular & Remedies
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            "verdauung_remedies_multiplex",
            "entgiftung_remedies_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "verdauung_detailliert":
        groups = [
            # Verdauungstrakt komplett
            "verdauung_magen",
            "verdauung_duenndarm",
            "verdauung_dickdarm",
            "verdauung_leber",
            "verdauung_galle",
            "verdauung_pankreas",
            "verdauung_mikrobiom",
            "verdauung_barriere",
            "verdauung_duenndarm_fein",
            "verdauung_dickdarm_fein",
            "verdauung_mikrobiom_fein",
            "verdauung_symptome_fein",
            "verdauung_pathologien_fein",
            # Entgiftung & Immun
            "entgiftung_darm",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_organe_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            # Pathogene & Toxine
            "bakterien_detailliert_fein",
            "viren_detailliert_fein",
            "parasiten_detailliert_fein",
            "pilze_detailliert_fein",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "nahrung_symptome_fein",
            "nahrung_unvertraeglichkeiten_fein",
            "nahrung_remedies_multiplex",
            # Orthomolekular & Remedies
            "verdauung_remedies_multiplex",
            "entgiftung_remedies_multiplex",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "herz_kreislauf_fein":
        groups = [
            "herz_fein",
            "kreislauf",
            "kreislauf_fein",
            "herz_symptome_fein",
            "herz_pathologien_fein",
            "kreislauf_symptome_fein",
            "mikrozirkulation",
            "meridiane",
            "meridiane_detailliert_fein",
            "herz_remedies_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "atmung_lunge_detailliert":
        groups = [
            # Atmung/Lunge detailliert inkl. Lunge-Darm-Achse
            "atmung_lunge",
            "atmung_bronchien",
            "atmung_zwerchfell",
            "atmung_nase",
            "atmung_rachen",
            "atmung_lunge_fein",
            "atmung_symptome_fein",
            "atmung_pathologien_fein",
            # Kreislauf-Kopplung
            "kreislauf",
            "kreislauf_fein",
            # Lunge-Darm-Achse
            "verdauung_barriere",
            "verdauung_mikrobiom_fein",
            # Pathogene und Belastungen
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            # Immun & Regulation
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Remedies & Therapien
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "atmung_remedies_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "nervensystem_detailliert":
        groups = [
            "nervensystem_zns",
            "nervensystem_zns_fein",
            "nervensystem_pns",
            "nervensystem_pns_fein",
            "nervensystem_vegetativ",
            "nervensystem_hirnnerven",
            "nervensystem_hirnnerven_fein",
            "nervensystem_plexus",
            "nervensystem_neurotransmitter",
            "nervensystem_neurotransmitter_fein",
            "nerven_symptome_fein",
            "nerven_pathologien_fein",
            "nerven_remedies_multiplex",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_sakral",
            "wirbelsaeule_bandscheiben",
            "wirbelsaeule_bandscheiben_fein",
            "wirbelsaeule_symptome_fein",
            "wirbelsaeule_pathologien_fein",
            "schwindel_hws",
            "schwindel_kreislauf",
            "schwindel_medikament",
            "schwindel_vestibular",
            "schwindel_vestibular_fein",
            "schwindel_zentral",
            "schwindel_zentral_fein",
            "schmerz_kopf",
            "schmerz_kopf_fein",
            "schmerz_ruecken",
            "schmerz_gelenk",
            "schlafstoerungen",
            "schlafstoerungen_fein",
            "muedigkeit_chronisch",
            "konzentration",
            "schwermetalle",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "orthomolekular_therapie_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            "energie_remedies_multiplex",
            "psyche_remedies_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "endokrin_detailliert":
        # Fokus-Profil: Hormonsystem, Schilddrüse, Nebenniere, Geschlechtshormone
        groups = [
            # Endokrine Drüsen
            "endokrin",
            "schilddruese_fein",
            "nebenniere_fein",
            "hypophyse_fein",
            # Hormone & Symptome
            "hormone_symptome_fein",
            "hormone_schilddruese_fein",
            "hormone_geschlecht_fein",
            "hormone_remedies_multiplex",
            # Geschlechtsspezifisch
            "urogenitalsystem_fein",
            "wechseljahre_detailliert_fein",
            "schwangerschaft_geburt_fein",
            # Stress- und Regulationsachsen
            "nervensystem_vegetativ",
            "schlafstoerungen",
            "schlafstoerungen_fein",
            "muedigkeit_chronisch",
            # Entgiftung & Immunsystem
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_organe_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            # Mikronährstoffe & Orthomolekular
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "orthomolekular_therapie_multiplex",
            # Systemische Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            "energie_remedies_multiplex",
            "psyche_remedies_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "urogenital_detailliert":
        groups = [
            "urogenitalsystem_fein",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_organe_fein",
            # Pathogene
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            # Toxische Belastungen
            "schwermetalle",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Zahn- & Wirbelsäulenachsen (Niere/Blase-Bezug)
            "zahnorgane",
            "zahnorgane_fein",
            "zahnorgane_quadrant1",
            "zahnorgane_quadrant2",
            "zahnorgane_quadrant3",
            "zahnorgane_quadrant4",
            "zahnorgane_weisheitszaehne",
            "zahnorgane_kiefer_herde",
            "zahn_materialien_fein",
            "zahn_pathologien_fein",
            "zahn_symptome_fein",
            "zahn_remedies_multiplex",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_remedies_multiplex",
            "meridiane",
            "meridiane_detailliert_fein",
            # Regulation & Mikronährstoffe
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_therapie_multiplex",
            # Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "schmerz_detailliert":
        groups = [
            # Schmerz- und Schlafsymptomatik
            "schmerz_kopf",
            "schmerz_kopf_fein",
            "schmerz_ruecken",
            "schmerz_gelenk",
            "schlafstoerungen",
            "schlafstoerungen_fein",
            "muedigkeit_chronisch",
            # Strukturelle Achsen
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_sakral",
            "wirbelsaeule_bandscheiben",
            "wirbelsaeule_bandscheiben_fein",
            "wirbelsaeule_symptome_fein",
            "wirbelsaeule_pathologien_fein",
            "wirbelsaeule_remedies_multiplex",
            "knochen_gelenke",
            "knochen_gelenke_fein",
            "knochen_symptome_fein",
            "knochen_pathologien_fein",
            "muskulatur_fein",
            "faszien_fein",
            # Entzündung & Immun
            "entzuendung",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            # Belastungen
            "schwermetalle",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Psyche, Energie, Miasmen
            "psyche_remedies_multiplex",
            "energie_remedies_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            # Mikronährstoffe & Orthomolekular
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            # Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "tote_zaehne_detailliert":
        groups = [
            # Zähne & Kiefer (devitale Zähne, Herde)
            "zahnorgane",
            "zahnorgane_fein",
            "zahnorgane_frontzaehne",
            "zahnorgane_quadrant1",
            "zahnorgane_quadrant2",
            "zahnorgane_quadrant3",
            "zahnorgane_quadrant4",
            "zahnorgane_weisheitszaehne",
            "zahnorgane_kiefergelenk",
            "zahnorgane_kiefer_herde",
            "zahn_materialien_fein",
            "zahn_pathologien_fein",
            "zahn_symptome_fein",
            "zahn_remedies_multiplex",
            # Knochen-/Kieferstruktur
            "knochen_gelenke",
            "knochen_gelenke_fein",
            "knochen_symptome_fein",
            "knochen_pathologien_fein",
            "knochen_osteoporose",
            "knochen_osteoblasten",
            "knochen_osteoklasten",
            "knochen_knorpel",
            "knochen_remedies_multiplex",
            # Wirbelsäule & Nervensystem
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_sakral",
            "wirbelsaeule_bandscheiben",
            "wirbelsaeule_bandscheiben_fein",
            "wirbelsaeule_symptome_fein",
            "wirbelsaeule_pathologien_fein",
            "wirbelsaeule_remedies_multiplex",
            "nervensystem_zns_fein",
            "nervensystem_vegetativ",
            "nervensystem_hirnnerven",
            "nervensystem_hirnnerven_fein",
            # Toxine & Materialien
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Pathogene
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            # Entgiftung & Immunsystem
            "entgiftung_leber_phase1",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "immunsystem_autoimmun_fein",
            "immunsystem_zytokine_fein",
            "entzuendung",
            # Umweltachsen
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Mikronährstoffe & Regulation
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            # Systemische Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    else:
        typer.echo(
            f"Unbekanntes Multiplex-Profil: '{profile}'. Erlaubt sind 'pathogen', 'toxin', 'regulation', 'full' (Alias: 'therapy')."
        )
        raise typer.Exit(code=1)

    # Phase 1 Modularisierung: Validate Groups
    # Wir prüfen, ob die angeforderten Gruppen überhaupt existieren.
    if show_progress:
        typer.echo(f"[1/5] 🔍 Validiere {len(groups)} Gruppen...")
    
    available_groups_set = set(list_groups())
    missing_groups = validate_profile_groups(groups, available_groups_set)
    
    if missing_groups:
        typer.echo("")
        typer.echo("⚠ WARNUNG: Folgende Gruppen wurden im Profil definiert, existieren aber nicht im System:")
        for mg in missing_groups:
            typer.echo(f"  - {mg}")
        typer.echo("Die Analyse läuft weiter, aber diese Gruppen liefern KEINE Ergebnisse.")
        typer.echo("")

    if show_progress:
        typer.echo(f"[2/5] 📦 Generiere {k_total} Kandidaten aus {len(groups)} Gruppen...")
    
    subgroup_svc = SubgroupService()
    items = subgroup_svc.generate_fullbody_candidates(groups, seed, k_total=k_total)
    if not items:
        typer.echo("Keine Multiplex-Kandidaten erzeugt.")
        raise typer.Exit(code=1)
    
    if show_progress:
        typer.echo(f"[2/5] ✓ {len(items)} Kandidaten generiert")

    if debug_groups:
        typer.echo("")
        typer.echo("=" * 70)
        typer.echo(f"DEBUG: Multiplex-Kandidatenverteilung über {len(groups)} Gruppen")
        typer.echo("=" * 70)

        counts: Dict[str, int] = {}
        for it in items:
            g = str(it.get("group", "") or "").strip()
            if not g:
                g = "_ungrouped"
            counts[g] = counts.get(g, 0) + 1

        groups_with = sorted(counts.items(), key=lambda kv: kv[0])
        zero_groups = [g for g in groups if g not in counts]

        typer.echo(f"✓ Gruppen MIT Kandidaten: {len(groups_with)}")
        typer.echo(f"✗ Gruppen OHNE Kandidaten: {len(zero_groups)}")
        typer.echo("")

        typer.echo("Kandidaten pro Gruppe:")
        for g, c in groups_with:
            typer.echo(f"  - {g}: {c}")
        if zero_groups:
            typer.echo("")
            typer.echo("Gruppen mit 0 Kandidaten:")
            for g in zero_groups:
                typer.echo(f"  - {g}")
        typer.echo("=" * 70)
        typer.echo("")

    personal_profile = {
        "emotion": _clamp(p_emotion),
        "physisch": _clamp(p_physisch),
        "mental": _clamp(p_mental),
        "astral": _clamp(p_astral),
    }

    _profile = (hardware_profile or "windows").strip().lower()
    mode = (os.getenv("ME_ENTROPY_MODE") or "legacy").strip().lower()

    # Default-Exportordner setzen, wenn nicht angegeben
    if export is None:
        export = Path("Benutzer_Archive")
    typer.echo(f"Export-Ziel: {export}")

    if show_progress:
        typer.echo("[3/5] 🎲 Sampling Entropie...")
    
    # Hybrid-Entropy Option
    entropy_source_name = "standard"
    if use_hybrid_entropy:
        try:
            from core.hybrid_entropy import get_hybrid_h_level, format_hybrid_display
            h_level, hybrid_meta = get_hybrid_h_level()
            entropy_source_name = f"hybrid ({hybrid_meta.get('method', 'mix')})"
            src = type('HybridSource', (), {'name': lambda self: entropy_source_name})()
            if show_progress:
                typer.echo(format_hybrid_display(hybrid_meta))
        except ImportError:
            use_hybrid_entropy = False
    
    if not use_hybrid_entropy:
        if _profile == "debian_server":
            duration = 2.0
            if mode == "enhanced":
                pref = ["qrng", "gpu", "network", "cpu_timer"]
            else:
                pref = ["qrng", "gpu", "cpu_timer"]
            src = select_entropy_source(preferred=pref)
            h_level = _clamp(src.sample_h_level(duration_s=duration))
            if src.name() in ("qrng", "gpu", "network") and h_level <= 0.0:
                fallback_src = select_entropy_source(preferred=["cpu_timer"])
                fallback_h = _clamp(fallback_src.sample_h_level(duration_s=duration))
                if fallback_h > h_level:
                    src = fallback_src
                    h_level = fallback_h
        else:
            duration = 3.0 if _profile == "windows" else 2.0
            if mode == "enhanced":
                pref = ["truerng", "hid_sensor", "network", "cpu_timer"]
            else:
                pref = ["hid_sensor", "cpu_timer"]
            
            # Kaskadierende Fallback-Logik: Jede Quelle der Reihe nach testen
            # bis eine h_level > 0 liefert
            src = None
            h_level = 0.0
            for source_key in pref:
                candidate_src = select_entropy_source(preferred=[source_key])
                if candidate_src.name() == source_key:
                    candidate_h = _clamp(candidate_src.sample_h_level(duration_s=duration))
                    if candidate_h > 0.0:
                        src = candidate_src
                        h_level = candidate_h
                        break
            
            # Fallback auf cpu_timer wenn keine Quelle einen Wert > 0 lieferte
            if src is None or h_level <= 0.0:
                src = select_entropy_source(preferred=["cpu_timer"])
                h_level = _clamp(src.sample_h_level(duration_s=duration))
        entropy_source_name = src.name()
    
    if show_progress:
        typer.echo(f"[3/5] ✓ h_level: {h_level:.4f} ({entropy_source_name})")

    profile_obj = ClientProfile(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        image_signature=None,
        personal_profile=personal_profile,
        planet_type=planet_type,
    )

    analysis = AnalysisService(rate_database={}, h_level=h_level)
    client_rates = analysis.encode_profile(profile_obj)
    client_entropy = analysis.resonator.holographic_entropy(client_rates)
    m_field = analysis.resonator.calculate_m_field(client_rates)
    heim_sig = analysis.resonator.heim_signature(client_rates)

    encoder = RateEncoder()
    client_personal_vector = encoder.personal_profile_to_vector(personal_profile)

    def resonance_fn(a: np.ndarray, b: np.ndarray) -> float:
        return float(analysis.resonator.resonance_score(a, b))

    if show_progress:
        typer.echo(f"[4/5] 🔬 Berechne Resonanz-Scores für {len(items)} Items...")
    
    nls_service = NlsService(items)
    scores = nls_service.compute_scores_v2(
        client_rates,
        client_entropy,
        resonance_fn,
        client_personal_vector=client_personal_vector,
    )
    
    # Gruppen-Information aus Items in Scores übertragen (für BAT-Aggregation)
    item_group_map = {it.get('label', ''): it.get('group', '') for it in items}
    for score_entry in scores:
        if 'group' not in score_entry or not score_entry.get('group'):
            score_entry['group'] = item_group_map.get(score_entry.get('label', ''), '')
    
    # === CLIENT PROFILE MODIFIERS (erweitert 01.12.2025) ===
    from datetime import datetime as _dt
    
    # Initialisiere alle Modifikatoren
    modifiers = {
        'age_factor': 1.0,
        'gender_factor': 1.0,
        'bmi_factor': 1.0,
        'stress_factor': 1.0,
        'sleep_factor': 1.0,
        'emf_factor': 1.0,
    }
    client_age = 0
    client_bmi = None
    
    try:
        # 1. ALTERS-FAKTOR aus Geburtsdatum (Format: DDMMYYYY)
        bd = birth_date.strip()
        if len(bd) == 8:
            day = int(bd[:2])
            month = int(bd[2:4])
            year = int(bd[4:])
            birth = _dt(year, month, day)
            today = _dt.now()
            client_age = today.year - birth.year
            if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
                client_age -= 1
            
            if client_age < 18:
                modifiers['age_factor'] = 1.15  # Kinder: höhere Sensitivität
            elif client_age > 65:
                modifiers['age_factor'] = 1.10  # Senioren: leicht erhöhte Resonanz
            elif client_age > 50:
                modifiers['age_factor'] = 1.05  # Mittleres Alter
    except Exception:
        client_age = 0
    
    # 2. GESCHLECHTS-FAKTOR (optional)
    if client_gender:
        g = client_gender.strip().lower()
        if g == 'f':
            modifiers['gender_factor'] = 1.05  # Weiblich: andere hormonelle Signatur
        elif g == 'm':
            modifiers['gender_factor'] = 0.98  # Männlich: leicht gedämpft
        # 'd' oder andere: neutral (1.0)
    
    # 3. BMI-FAKTOR (optional, wenn Größe und Gewicht angegeben)
    if client_height > 0 and client_weight > 0:
        height_m = client_height / 100.0
        client_bmi = round(client_weight / (height_m ** 2), 1)
        if client_bmi < 18.5:
            modifiers['bmi_factor'] = 1.10  # Untergewicht: höhere Sensitivität
        elif client_bmi > 30:
            modifiers['bmi_factor'] = 0.92  # Adipositas: gedämpfte Resonanz
        elif client_bmi > 25:
            modifiers['bmi_factor'] = 0.96  # Übergewicht: leicht gedämpft
    
    # 4. STRESS-FAKTOR (optional)
    if client_stress > 0:
        if client_stress >= 8:
            modifiers['stress_factor'] = 1.25  # Sehr hoher Stress: verstärkte Reaktion
        elif client_stress >= 6:
            modifiers['stress_factor'] = 1.15  # Hoher Stress
        elif client_stress >= 4:
            modifiers['stress_factor'] = 1.05  # Mittlerer Stress
    
    # 5. SCHLAF-FAKTOR (optional)
    if client_sleep > 0:
        if client_sleep < 5:
            modifiers['sleep_factor'] = 1.20  # Starker Schlafmangel
        elif client_sleep < 6:
            modifiers['sleep_factor'] = 1.10  # Schlafmangel
        elif client_sleep > 9:
            modifiers['sleep_factor'] = 0.95  # Übermäßiger Schlaf (kann auf Probleme hindeuten)
        elif client_sleep >= 7:
            modifiers['sleep_factor'] = 0.92  # Guter Schlaf: bessere Regeneration
    
    # 6. EMF-FAKTOR (optional)
    if client_emf:
        emf = client_emf.strip().lower()
        if emf == "hoch":
            modifiers['emf_factor'] = 1.25  # Hohe EMF-Belastung
        elif emf == "mittel":
            modifiers['emf_factor'] = 1.10  # Mittlere EMF-Belastung
        # "niedrig" oder leer: neutral (1.0)
    
    # Berechne kombinierten Modifikator (multiplikativ)
    combined_modifier = 1.0
    active_modifiers = []
    for key, value in modifiers.items():
        if value != 1.0:
            combined_modifier *= value
            active_modifiers.append(f"{key}={value:.2f}")
    
    # Wende kombinierten Modifikator auf alle Scores an
    if combined_modifier != 1.0:
        for score_entry in scores:
            original_score = float(score_entry.get("score", 0.0))
            score_entry["score"] = original_score * combined_modifier
            score_entry["client_modifiers"] = modifiers.copy()
            score_entry["combined_modifier"] = combined_modifier
        
        if show_progress:
            typer.echo(f"  📊 Klienten-Modifikatoren aktiv: {', '.join(active_modifiers)}")
            typer.echo(f"     Kombinierter Faktor: {combined_modifier:.3f}")
    
    # === QUANTEN-SUPERPOSITION (zeitabhängige Modulation) ===
    import time as _time
    import math as _math
    
    # Berechne Quanten-Komponente aus morphic_field/engine
    HBAR = 1.054571817e-34
    n_states = 5  # Standard: 5 Quantenzustände
    amplitude = 1.0 / _math.sqrt(float(n_states))
    base_energy = 1.6e-19
    t_now = _time.time()
    
    real_part = 0.0
    imag_part = 0.0
    for k in range(1, n_states + 1):
        energy = base_energy * (k * k)
        phase_offset = _math.pi * float(k) / float(n_states + 1)
        phase = -(energy * t_now) / HBAR + phase_offset
        real_part += amplitude * _math.cos(phase)
        imag_part += amplitude * _math.sin(phase)
    
    quantum_magnitude = _math.hypot(real_part, imag_part) / _math.sqrt(float(n_states))
    # Normiere auf sinnvollen Bereich [0.8, 1.2] für sanfte Modulation
    quantum_factor = 0.9 + 0.2 * min(1.0, max(0.0, quantum_magnitude))
    
    # Wende Quanten-Faktor auf alle Scores an
    for score_entry in scores:
        original_score = float(score_entry.get("score", 0.0))
        score_entry["score"] = original_score * quantum_factor
        score_entry["quantum_factor"] = quantum_factor
    
    # === INTENTIONS-FAKTOR ANWENDEN ===
    intention_factors = {
        "healing": 1.272,        # √φ - Natürliche Wiederherstellung
        "manifestation": 1.618,  # φ  - Goldene Schöpfung
        "protection": 1.414,     # √2 - Stabiler Schild
        "transformation": 2.236, # √5 - Dynamische Veränderung
        "connection": 2.0,       # 2  - Perfekte Einheit
        "clearing": 1.732,       # √3 - Reinigung/Klärung
        "activation": 2.718,     # e  - Natürliches Erwachen
        "harmonization": 1.618,  # φ  - Perfekte Balance
    }
    
    intention_key = (intention or "").strip().lower()
    intention_factor = intention_factors.get(intention_key, 1.0)
    intention_active = intention_factor != 1.0
    
    # === KOHÄRENZ BERECHNEN (für jeden Score) ===
    import math as _math
    for score_entry in scores:
        # Kohärenz aus 4 Faktoren: resonance, entropy_alignment, reliability, personal_alignment
        factors = [
            float(score_entry.get("resonance", 0.5)),
            float(score_entry.get("entropy_alignment", 0.5)),
            float(score_entry.get("reliability", 1.0)),
            float(score_entry.get("personal_alignment", 1.0)),
        ]
        mean_f = sum(factors) / len(factors)
        variance_f = sum((x - mean_f) ** 2 for x in factors) / len(factors)
        std_dev_f = _math.sqrt(max(variance_f, 0.0))
        coherence = 1.0 / (1.0 + std_dev_f)
        score_entry["coherence"] = max(0.0, min(1.0, coherence))
    
    if intention_active:
        for score_entry in scores:
            original_score = float(score_entry.get("score", 0.0))
            # Sanfte Gewichtung: 80% Basis + 20% Intentions-Modulation
            weighted_score = original_score * (0.8 + 0.2 * intention_factor)
            score_entry["score"] = weighted_score
            score_entry["intention_factor"] = intention_factor
        # Neu sortieren nach gewichtetem Score
        scores.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    
    if show_progress:
        typer.echo(f"[4/5] ✓ {len(scores)} Scores berechnet")
        if modifiers['age_factor'] != 1.0:
            typer.echo(f"[4/5] ✓ Alters-Faktor: {modifiers['age_factor']:.2f} (Alter: {client_age} Jahre)")
        if active_modifiers:
            typer.echo(f"  📊 Klienten-Modifikatoren aktiv: {', '.join(active_modifiers)}")
            typer.echo(f"     Kombinierter Faktor: {combined_modifier:.3f}")
        typer.echo(f"[4/5] ✓ Quantum-Faktor: {quantum_factor:.4f}")
        if intention_active:
            typer.echo(f"[4/5] ✓ Intention '{intention_key}' angewendet (Faktor: {intention_factor:.3f})")

    influence_factors = _build_influence_factors(
        tcm_type,
        planet_type,
        profile_obj.image_signature,
    )

    if show_progress:
        typer.echo("[5/5] 📝 Erstelle Report...")
    
    typer.echo("Morphic Engine V1 – Multiplex-Scan")
    typer.echo(f"Profil: {prof}")
    typer.echo(f"Klient: {first_name} {name}" + (f" ({client_age} Jahre)" if client_age > 0 else ""))
    if (focus or "").strip():
        typer.echo(f"Fokus: {focus}")
    if intention_active:
        typer.echo(f"Intention: {intention_key} (Faktor: {intention_factor:.3f})")
    if modifiers['age_factor'] != 1.0:
        typer.echo(f"Alters-Faktor: {modifiers['age_factor']:.2f}")
    typer.echo(f"Quantum-Faktor: {quantum_factor:.4f}")
    typer.echo(
        "Personalprofil: "
        f"Emotion={personal_profile['emotion']:.2f}, "
        f"Physisch={personal_profile['physisch']:.2f}, "
        f"Mental={personal_profile['mental']:.2f}, "
        f"Astral={personal_profile['astral']:.2f}"
    )
    typer.echo(f"Morphic field: {m_field:.4f}")
    typer.echo(f"h_level (Hardware): {h_level:.3f} [{src.name()} / profile={_profile}]")
    typer.echo(f"Holographic entropy: {client_entropy:.4f}")
    typer.echo("Heim signature:")
    typer.echo("  " + ", ".join(f"{x:.3f}" for x in heim_sig))

    typer.echo("")
    typer.echo("Top Items (NLS v2, personalisiert):")
    seen_labels = set()
    top_scores = []
    for entry in scores:
        label = entry["label"]
        if label in seen_labels:
            continue
        seen_labels.add(label)
        top_scores.append(entry)
        if len(top_scores) >= top_k:
            break
    for entry in top_scores:
        label = entry["label"]
        score = entry["score"]
        coherence = entry.get("coherence", 0.0)
        # Kohärenz-Symbol: ✓ bei > 0.7, ⚠ bei 0.4-0.7, ⚡ bei < 0.4
        coh_symbol = "✓" if coherence > 0.7 else ("⚠" if coherence > 0.4 else "⚡")
        typer.echo(
            f"  - {label}: score={score:.4f}, coherence={coherence:.0%} {coh_symbol}"
        )

    # B.A.T. Subgruppen-Aggregation (nur für bat_ Profile)
    subgroup_data = None
    if prof.startswith('bat_'):
        try:
            from core.bat_report_aggregator import (
                aggregate_by_subgroup,
                format_subgroup_report,
                generate_subgroup_json
            )
            
            aggregated = aggregate_by_subgroup(scores, top_subgroups=5, top_items_per_group=3)
            if aggregated:
                subgroup_data = generate_subgroup_json(aggregated, include_remedies=True)
                report_text = format_subgroup_report(aggregated, include_remedies=True)
                try:
                    typer.echo(report_text)
                except UnicodeEncodeError:
                    # Fallback ohne Emojis für Batch-Modus
                    safe_text = report_text.replace("💊", "[R]")
                    typer.echo(safe_text)
        except ImportError as e:
            typer.echo(f"⚠ BAT-Aggregation nicht verfügbar: {e}")
        except Exception as e:
            typer.echo(f"⚠ BAT-Report Fehler: {e}")

    synergy_results = None
    if synergy:
        # Verwende Fokus oder Fallback für allgemeine Analyse
        effective_focus = focus.strip() if focus.strip() else "Allgemeine Balance"
        
        try:
            from core.quantum_synergy import QuantumSynergyEngine

            typer.echo("")
            typer.echo("=" * 70)
            typer.echo("QUANTUM-SYNERGY ANALYSE")
            typer.echo("=" * 70)
            typer.echo(f"Fokus: {effective_focus}")
            typer.echo(f"Kombinations-Größe: {synergy_combos}")
            typer.echo(f"Threshold: {synergy_threshold}/10.0")
            typer.echo("")

            # Quantum-Synergy wie FRÜHER: Nutze gesamte Datenbank mit Fokus-Filterung
            # WICHTIG: Keine scan_results Filterung mehr - Engine nutzt volle Datenbank!
            engine = QuantumSynergyEngine()
            effective_threshold = float(synergy_threshold)
            # Reduziere Threshold bei größeren Kombinationen für bessere Ergebnisse
            if synergy_combos >= 4:
                effective_threshold = max(4.5, effective_threshold - 0.5)
                typer.echo(f"   → Threshold angepasst auf {effective_threshold:.1f} (Kombos >= 4)")
            elif synergy_combos >= 3:
                effective_threshold = max(5.0, effective_threshold - 0.3)
                typer.echo(f"   → Threshold angepasst auf {effective_threshold:.1f} (Kombos >= 3)")
            
            typer.echo(f"   → Nutze gesamte Datenbank mit Fokus-Filterung (wie früher)...")
            typer.echo("")

            synergy_results = engine.find_synergistic_triggers(
                focus=effective_focus,
                scan_results=None,  # ← KEINE Filterung - volle Datenbank wie früher!
                combination_size=synergy_combos,
                top_n=10,
                threshold=effective_threshold,
            )

            if not synergy_results and effective_threshold > 4.0:
                fallback_threshold = max(4.0, effective_threshold - 1.5)
                typer.echo(
                    f"⚠ Keine Kombinationen über Threshold {effective_threshold:.1f} gefunden – "
                    f"versuche niedrigeren Threshold {fallback_threshold:.1f}..."
                )
                synergy_results = engine.find_synergistic_triggers(
                    focus=effective_focus,
                    scan_results=None,  # Volle Datenbank
                    combination_size=synergy_combos,
                    top_n=10,
                    threshold=fallback_threshold,
                )

            # Best-Effort-Fallback: Wenn weiterhin keine Kombinationen gefunden
            # wurden, führe eine Suche ohne Threshold aus und nimm die Top-5,
            # damit im Report trotzdem eine Quantum-Synergy-Sektion sichtbar ist.
            if not synergy_results:
                best_effort_threshold = 0.0
                typer.echo(
                    "ℹ Keine Kombinationen über regelbasierte Thresholds – "
                    "best-effort Suche ohne Threshold (Top-5 Kombinationen)..."
                )
                synergy_results = engine.find_synergistic_triggers(
                    focus=effective_focus,
                    scan_results=None,  # Volle Datenbank
                    combination_size=synergy_combos,
                    top_n=5,
                    threshold=best_effort_threshold,
                )

            if synergy_results:
                # HYBRID-ANSATZ: Kategorisiere nach Scan-Overlap
                scan_labels = set(entry["label"] for entry in top_scores[:32])
                
                primary_synergies = []  # Mind. 1 Item aus Scan
                secondary_synergies = []  # Rein fokus-basiert
                
                for combo_items, combo_score, details in synergy_results:
                    combo_labels = [item["label"] for item in combo_items]
                    overlap = len(set(combo_labels) & scan_labels)
                    
                    if overlap >= 1:  # Mind. 1 Item aus aktuellem Scan
                        primary_synergies.append((combo_items, combo_score, details, overlap))
                    else:
                        secondary_synergies.append((combo_items, combo_score, details, overlap))
                
                typer.echo(f"✓ {len(synergy_results)} synergistische Kombinationen gefunden")
                typer.echo(f"  → {len(primary_synergies)} basieren auf aktuellem Scan")
                typer.echo(f"  → {len(secondary_synergies)} sind erweiterte Fokus-Synergien")
                typer.echo("")
                
                # Zeige Primary Synergies
                if primary_synergies:
                    typer.echo("=" * 70)
                    typer.echo("HAUPT-SYNERGIEN (basierend auf aktuellem Scan)")
                    typer.echo("=" * 70)
                    typer.echo("")
                    
                    for i, (combo_items, combo_score, details, overlap) in enumerate(primary_synergies, 1):
                        typer.echo(f"#{i} - Synergy-Score: {combo_score:.2f}/10.0 [{overlap} Items aus Scan]")
                        typer.echo("-" * 70)
                        typer.echo("Items:")
                        for item in combo_items:
                            in_scan = "✓" if item["label"] in scan_labels else " "
                            typer.echo(f"  {in_scan} • {item['label']}")
                        typer.echo("")
                        typer.echo("Komponenten:")
                        typer.echo(f"  Einzelwirkungen:      {details['individual_scores']:.2f}/10.0")
                        typer.echo(f"  Resonanz-Verstärkung: {details['resonance']:.2f}/10.0")
                        typer.echo(f"  Frequenz-Harmonien:   {details['harmony']:.2f}/10.0")
                        typer.echo(f"  Fokus-Relevanz:       {details['relevance']:.2f}/10.0")
                        typer.echo("")
                
                # Zeige Secondary Synergies (optional, nur Top 3)
                if secondary_synergies:
                    typer.echo("=" * 70)
                    typer.echo("ERWEITERTE FOKUS-SYNERGIEN (Top 3)")
                    typer.echo("=" * 70)
                    typer.echo("")
                    
                    for i, (combo_items, combo_score, details, overlap) in enumerate(secondary_synergies[:3], 1):
                        typer.echo(f"#{i} - Synergy-Score: {combo_score:.2f}/10.0 [Fokus-basiert]")
                        typer.echo("-" * 70)
                        typer.echo("Items:")
                        for item in combo_items:
                            typer.echo(f"    • {item['label']}")
                        typer.echo("")
            else:
                typer.echo("⚠ Keine synergistischen Kombinationen gefunden")
                typer.echo("")
        except ImportError:
            typer.echo("⚠ Quantum-Synergy Modul nicht verfügbar")
            typer.echo("")
        except Exception as exc:
            typer.echo(f"⚠ Quantum-Synergy Fehler: {exc}")
            typer.echo("")

    # Export-Block für multiplex_scan
    if export is not None:
        client_info = {
            "name": name,
            "first_name": first_name,
            "birth_date": birth_date,
            "birth_place": birth_place,
        }

        # Baue Metadaten-Lookup, um Gruppen/Raten/Potenzen/Level aus den Kandidaten zu ziehen
        meta_by_label: Dict[str, Dict[str, object]] = {}
        used_groups: set[str] = set()
        for it in items:
            label_it = str(it.get("label", "")).strip()
            if not label_it or label_it in meta_by_label:
                continue
            meta_by_label[label_it] = it
            grp = str(it.get("group", "") or "").strip()
            if grp:
                used_groups.add(grp)

        def _as_rates(raw: Iterable[object] | None) -> List[float]:
            if not raw:
                return []
            try:
                return [float(x) for x in raw]
            except Exception:
                return []

        sub_results_top: List[Dict[str, object]] = []
        for entry in scores:
            label = str(entry.get("label", ""))
            if not label:
                continue
            meta = meta_by_label.get(label, {})
            group_val = str(meta.get("group", "") or "").strip()
            if group_val:
                used_groups.add(group_val)
            rates_vals = meta.get("rates") or entry.get("rates")
            potency_meta = meta.get("potency")
            level_meta = meta.get("level")
            desc_meta = meta.get("description") or entry.get("description")

            score_val = float(entry.get("score", 0.0) or 0.0)
            rates_list = _as_rates(rates_vals)

            potency_display = (
                str(potency_meta)
                if potency_meta not in (None, "")
                else _interpret_potency(score_val, label)
            )

            # 13-Ebenen-Resonanz: wenn sinnvoll vorhanden, diese als Ebene anzeigen,
            # sonst auf den bisherigen Level-Interpreter zurückfallen.
            lvl_id, lvl_val, lvl_text, copen_rate = _rates_to_level_info(rates_list, label)
            if lvl_id > 0 and lvl_val > 0.0:
                level_display = lvl_text
            else:
                level_display = (
                    str(level_meta)
                    if level_meta not in (None, "")
                    else _interpret_level(score_val, group_val, label)
                )

            sub_entry: Dict[str, object] = {
                "label": label,
                "score": score_val,
                "rates": rates_list,
                "group": group_val,
                "potency": potency_display,
                "level": level_display,
                "copen_rate": float(copen_rate),
                "reliability": float(entry.get("reliability", 1.0) or 1.0),
                "personal_alignment": float(entry.get("personal_alignment", 1.0) or 1.0),
            }
            if desc_meta:
                sub_entry["description"] = str(desc_meta)
            sub_results_top.append(sub_entry)

        # Vollständige Gruppenliste: Alle Profil-Gruppen + gefundene Gruppen
        all_groups = set(groups)  # Alle Gruppen aus dem Multiplex-Profil
        all_groups.update(used_groups)  # Plus alle gefundenen Gruppen
        
        sub_results = {
            "groups": sorted(g for g in all_groups if g),
            "method": "multiplex",
            "candidates": len(items),
            "top": sub_results_top,
        }
        
        # Erstelle Basis-Resonance-Map (vereinfacht für multiplex_scan)
        resonance_map = {}
        for i, entry in enumerate(top_scores[:7]):  # Top 7 für Basis-Systeme
            system_name = entry["label"].lower().replace(" ", "_").replace("-", "_")
            resonance_map[system_name] = entry["score"]
        
        synergy_export = None
        if synergy_results:
            synergy_export = []
            # Kategorisiere wie in Konsolen-Ausgabe
            scan_labels_export = set(entry["label"] for entry in top_scores[:32])
            
            for combo_items, combo_score, details in synergy_results:
                combo_labels_export = [item["label"] for item in combo_items]
                overlap_count = len(set(combo_labels_export) & scan_labels_export)
                category = "primary" if overlap_count >= 1 else "secondary"
                
                synergy_export.append(
                    {
                        "items": [
                            {
                                "label": item["label"], 
                                "group": item.get("group", ""),
                                "in_scan": item["label"] in scan_labels_export  # NEU: Markiere Scan-Items
                            }
                            for item in combo_items
                        ],
                        "score": float(combo_score),
                        "category": category,  # NEU: primary oder secondary
                        "scan_overlap": overlap_count,  # NEU: Anzahl Items aus Scan
                        "components": {
                            "individual_scores": float(details["individual_scores"]),
                            "resonance": float(details["resonance"]),
                            "harmony": float(details["harmony"]),
                            "relevance": float(details["relevance"]),
                        },
                        "frequencies": [float(f) for f in details.get("frequencies", [])],
                    }
                )

        # === REMEDY-SYNERGIEN BERECHNEN (für JSON-Export) ===
        remedy_synergies_export = []
        if sub_results_top:
            # Sammle alle Remedy-Items
            MAX_ITEMS_PER_GROUP = 5
            remedy_pool = []
            group_counts: Dict[str, int] = {}
            
            for entry in sub_results_top:
                g = str(entry.get("group", "") or "").strip()
                if not g:
                    continue
                if _is_remedy_group(g):
                    current_count = group_counts.get(g, 0)
                    if current_count < MAX_ITEMS_PER_GROUP:
                        remedy_pool.append(entry)
                        group_counts[g] = current_count + 1
            
            # Berechne Synergien
            if len(remedy_pool) >= 2:
                try:
                    remedy_synergy_results = analyze_remedy_synergies(remedy_pool, max_results=20)
                    
                    # Konvertiere in Export-Format
                    for syn in remedy_synergy_results:
                        label = syn.get("label", "")
                        score = syn.get("score", 0.0)
                        rates = syn.get("rates", [])
                        synergies = syn.get("synergies", [])
                        
                        # Extrahiere erste Synergy für vereinfachtes Format
                        if synergies:
                            partner = synergies[0]
                            remedy_synergies_export.append({
                                "item1": label,
                                "item2": partner.get("partner_label", ""),
                                "synergy_score": partner.get("synergy_score", 0.0),
                                "rate1": rates,
                                "rate2": partner.get("partner_rates", []),
                            })
                except Exception as e:
                    typer.echo(f"⚠ Remedy-Synergy Fehler: {e}")

        influence_scoring: Dict[str, object] | None = None
        if influence_compare:
            influence_items: List[Dict[str, object]] = []
            for entry in top_scores:
                label_it = str(entry.get("label", "")).strip()
                if not label_it:
                    continue
                score_val = float(entry.get("score", 0.0) or 0.0)
                meta_it = meta_by_label.get(label_it, {})
                group_val = str(meta_it.get("group", "") or "").strip()
                m = _compute_influence_multiplier_for_item(
                    group_val,
                    label_it,
                    influence_factors,
                )
                influence_items.append(
                    {
                        "label": label_it,
                        "group": group_val,
                        "score_base": score_val,
                        "multiplier": float(m),
                        "score_influenced": float(score_val * m),
                    }
                )

            influence_scoring = {
                "enabled": True,
                "mode": "tcm_organ_clock_v1",
                "max_delta": 0.03,
                "items": influence_items,
            }

        db_analysis_block: Dict[str, object] | None = None
        if db_analysis_mode:
            client_rate_block = _build_db_client_rate_block(client_info)
            hardware_block: Dict[str, object] = {
                "profile": _profile,
                "source": src.name(),
                "h_level": float(h_level),
            }
            config_block: Dict[str, object] = {
                "profile": prof,
                "k_total": int(k_total),
                "top_k": int(top_k),
                "intention": intention_key if intention_active else None,
                "intention_factor": intention_factor if intention_active else None,
            }
            client_rate_value = None
            try:
                client_rate_value = float(client_rate_block.get("value", 0.0))
            except Exception:
                client_rate_value = None
            db_items = _build_db_items_from_sub_results(sub_results_top, int(top_k), client_rate_value)
            summary_block = _build_db_analysis_summary(db_items)
            db_analysis_block = {
                "enabled": True,
                "engine": "bruce_copen_db_v1",
                "client_rate": client_rate_block,
                "hardware": hardware_block,
                "config": config_block,
                "items": db_items,
                "summary": summary_block,
            }

        morphic_field_block: Dict[str, object] | None = None
        morphic_axes_block: Dict[str, object] | None = None
        if morphic_field:
            try:
                numerical_sequence: List[float] = []
                for sub in sub_results_top:
                    try:
                        raw_rate = sub.get("copen_rate")
                        if raw_rate is None:
                            continue
                        rate_val = float(raw_rate)
                    except Exception:
                        continue
                    if rate_val != 0.0:
                        numerical_sequence.append(rate_val)

                states = generate_default_quantum_states()
                geo_form = (mf_geometry or "flower_of_life").strip().lower() or "flower_of_life"
                intent = (mf_intention or "harmonization").strip().lower() or "harmonization"
                use_hw_mod = bool(mf_use_hardware)

                mf_config = MorphicFieldConfig(
                    quantum_states=states,
                    numerical_sequence=numerical_sequence,
                    geometric_form=geo_form,
                    intention=intent,
                    use_hardware_modulation=use_hw_mod,
                    hardware_profile=_profile,
                    time=None,
                )
                metrics_score: float | None = None
                if use_hw_mod:
                    try:
                        metrics_score = float(h_level) * 10.0
                    except Exception:
                        metrics_score = None

                mf_result = calculate_morphic_field(mf_config, metrics_score)

                mf_strength_val = float(mf_result.field_strength)
                mf_coherence_val = float(mf_result.coherence)
                mf_freq_val = float(mf_result.resonance_frequency)

                status = "unbekannt"
                status_text = ""
                if mf_coherence_val >= 0.66:
                    status = "hoch"
                    status_text = "hohe Kohärenz des Feldes (gut abgestimmte Organisation)."
                elif mf_coherence_val >= 0.33:
                    status = "mittel"
                    status_text = "mittlere Kohärenz, Regulierung und Harmonisierung empfohlen."
                else:
                    status = "niedrig"
                    status_text = (
                        "verminderte Kohärenz, erhöhter Regulationsbedarf "
                        "und Folgesitzungen sinnvoll."
                    )

                morphic_field_block = {
                    "total_wave_function": float(mf_result.total_wave_function),
                    "quantum_component": float(mf_result.quantum_component),
                    "numerical_factor": float(mf_result.numerical_factor),
                    "geometric_factor": float(mf_result.geometric_factor),
                    "intention_factor": float(mf_result.intention_factor),
                    "hardware_factor": float(mf_result.hardware_factor)
                    if mf_result.hardware_factor is not None
                    else None,
                    "coherence": mf_coherence_val,
                    "resonance_frequency": mf_freq_val,
                    "field_strength": mf_strength_val,
                    "status": status,
                    "status_text": status_text,
                    "timestamp": float(mf_result.timestamp),
                }

                # Achsen-/Wirbelsäulenanalyse nur lesend aus den Top-Items ableiten
                axes_candidate = _build_morphic_axes_from_sub_results(sub_results_top)
                if isinstance(axes_candidate, dict) and axes_candidate.get("enabled"):
                    morphic_axes_block = axes_candidate
            except Exception:
                morphic_field_block = None
                morphic_axes_block = None

        export_data: Dict[str, object] = {
            "group": None,
            "use_hw": True,
            "use_hid": src.name() == "hid_sensor",
            "h_level": float(h_level),
            "focus": focus if focus else None,
            # === SCAN-PARAMETER (NEU) ===
            "profile": prof,  # Profil-Name (z.B. "gehirn_detailliert")
            "profile_groups_count": len(groups),  # Anzahl definierter Gruppen
            "intention": intention if intention and intention.strip() else None,
            "planet_type": planet_type if planet_type and planet_type.strip() else None,
            "focus_weighting": focus_weighting,
            # === PERSONALPROFIL-WERTE ===
            "personal_profile_values": {
                "emotion": p_emotion,
                "physisch": p_physisch,
                "mental": p_mental,
                "astral": p_astral
            },
            # === ENTROPIE-KONFIGURATION ===
            "entropy_mode": mode,  # "enhanced" oder "legacy"
            "use_hybrid_entropy": use_hybrid_entropy,
            "analysis": {
                "rates": client_rates.tolist() if hasattr(client_rates, 'tolist') else list(client_rates),
                "morphic_field": float(m_field),
                "holographic_entropy": float(client_entropy),
                "entropy_calibrated": float(client_entropy * 0.247),  # Approximation der Kalibrierung
                "heim_signature": [float(x) for x in heim_sig],
                "resonance_map": resonance_map,
            },
            "sub_results": sub_results,
            "nls_scores": [dict(entry) for entry in scores[:50]],  # Erweiterte NLS-Daten
            "quantum_synergy": synergy_export,
            "remedy_synergies": remedy_synergies_export,  # Synergetische Remedy-Kombinationen
            # Zusätzliche Metadaten für Kompatibilität
            "command": "multiplex_scan",
            "hardware_profile": _profile,
            "hardware_source": src.name(),
            "client": client_info,
            "personal_profile": personal_profile,
            "focus": focus if focus and focus.strip() else "",
            "influence_factors": influence_factors,
        }

        if influence_scoring is not None:
            export_data["influence_scoring"] = influence_scoring

        if db_analysis_block is not None:
            export_data["db_analysis"] = db_analysis_block

        if morphic_field_block is not None:
            export_data["morphic_field"] = morphic_field_block

        if morphic_axes_block is not None:
            export_data["morphic_axes"] = morphic_axes_block

        # B.A.T. Subgruppen-Daten hinzufügen
        if subgroup_data is not None:
            export_data["bat_subgroups"] = subgroup_data

        try:
            json_path, html_path = _resolve_export_paths(export, client_info, "multiplex_scan", filename_suffix, scan_type, session_id)
            typer.echo(f"Export-Basis (absolut): {json_path.parent}")
            txt_path = html_path.with_suffix(".txt")
            typer.echo(f"Export-Pfade: JSON -> {json_path}")
            typer.echo(f"Export-Pfade: HTML -> {html_path}")
            typer.echo(f"Export-Pfade: TXT  -> {txt_path}")
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            _atomic_write_text(json_path, json_str)
            # Verwende basic_html mit der neuen sub_results Struktur
            html = _render_basic_html(export_data)
            _atomic_write_text(html_path, html)
            # TXT-Export erweitert für multiplex_scan mit Gruppierungen
            txt_lines = [
                "Morphic Engine V1 – Multiplex-Scan (TXT)",
                f"Klient: {first_name} {name} – {birth_date}, {birth_place}",
                f"Profil: {prof} | Hardware: {_profile} | Quelle: {src.name()}",
                f"Hardware-Level: {h_level:.3f} | Morphisches Feld: {m_field:.4f} | Entropie: {client_entropy:.4f}",
                f"Fokus: {focus}" if focus else "",
                "",
                "Einflussfaktoren:",
            ]

            # Optionale Kurzübersicht zur morphischen Feld-Analyse (neuer Engine-Block)
            mf_block_txt = export_data.get("morphic_field") or {}
            if isinstance(mf_block_txt, dict) and mf_block_txt:
                try:
                    mf_strength_txt = float(mf_block_txt.get("field_strength", 0.0) or 0.0)
                except Exception:
                    mf_strength_txt = 0.0
                try:
                    mf_coherence_txt = float(mf_block_txt.get("coherence", 0.0) or 0.0)
                except Exception:
                    mf_coherence_txt = 0.0
                try:
                    mf_freq_txt = float(mf_block_txt.get("resonance_frequency", 0.0) or 0.0)
                except Exception:
                    mf_freq_txt = 0.0

                txt_lines.append("")
                txt_lines.append("Morphische Feld-Analyse (Übersicht, experimentell):")
                txt_lines.append(
                    f"  Feldstärke: {mf_strength_txt:.4f} | Kohärenz: {mf_coherence_txt:.3f} | "
                    f"Resonanzfrequenz: {mf_freq_txt:.0f} Hz"
                )

                if mf_coherence_txt >= 0.66:
                    txt_lines.append(
                        "  Bewertung: hohe Kohärenz des Feldes (gut abgestimmte Organisation)."
                    )
                elif mf_coherence_txt >= 0.33:
                    txt_lines.append(
                        "  Bewertung: mittlere Kohärenz, Regulierung und Harmonisierung empfohlen."
                    )
                else:
                    txt_lines.append(
                        "  Bewertung: verminderte Kohärenz, erhöhter Regulationsbedarf und Folgesitzungen sinnvoll."
                    )

            # Experimentelle Wirbelsäulen- & Zahnachsen-Übersicht (nur wenn Block vorhanden ist)
            axes_block_txt = export_data.get("morphic_axes") or {}
            if isinstance(axes_block_txt, dict) and axes_block_txt.get("enabled"):
                spine_block_txt = axes_block_txt.get("spine") or {}
                dental_block_txt = axes_block_txt.get("dental") or {}

                if (isinstance(spine_block_txt, dict) and spine_block_txt) or (
                    isinstance(dental_block_txt, dict) and dental_block_txt
                ):
                    txt_lines.append("")
                    txt_lines.append("Wirbelsäulen- & Zahnachsen (experimentell):")

                # Wirbelsäule (gesamt + HWS-Schlüsselresonanz)
                if isinstance(spine_block_txt, dict) and spine_block_txt:
                    global_spine_txt = spine_block_txt.get("global") or {}
                    if isinstance(global_spine_txt, dict) and global_spine_txt:
                        try:
                            sp_items_txt = int(global_spine_txt.get("items_total", 0) or 0)
                        except Exception:
                            sp_items_txt = 0
                        try:
                            sp_max_txt = float(global_spine_txt.get("score_max", 0.0) or 0.0)
                        except Exception:
                            sp_max_txt = 0.0
                        try:
                            sp_mean_txt = float(global_spine_txt.get("score_mean", 0.0) or 0.0)
                        except Exception:
                            sp_mean_txt = 0.0

                        txt_lines.append(
                            f"  Wirbelsäule gesamt: Items={sp_items_txt}, Max-Score={sp_max_txt:.2f}, Mittelwert={sp_mean_txt:.2f}"
                        )

                    hws_block_txt = spine_block_txt.get("hws") or {}
                    if isinstance(hws_block_txt, dict):
                        top_hws_txt = hws_block_txt.get("top") or []
                        if isinstance(top_hws_txt, list) and top_hws_txt:
                            try:
                                top0_hws = top_hws_txt[0]
                                lbl_hws = str(top0_hws.get("label", "") or "").strip()
                                try:
                                    sc_hws = float(top0_hws.get("score", 0.0) or 0.0)
                                except Exception:
                                    sc_hws = 0.0
                                txt_lines.append(
                                    f"  HWS-Schlüsselresonanz: {lbl_hws or '-'} (Score {sc_hws:.2f})"
                                )
                            except Exception:
                                pass

                # Zahnachsen (gesamt)
                if isinstance(dental_block_txt, dict) and dental_block_txt:
                    global_dental_txt = dental_block_txt.get("global") or {}
                    if isinstance(global_dental_txt, dict) and global_dental_txt:
                        try:
                            de_items_txt = int(global_dental_txt.get("items_total", 0) or 0)
                        except Exception:
                            de_items_txt = 0
                        try:
                            de_max_txt = float(global_dental_txt.get("score_max", 0.0) or 0.0)
                        except Exception:
                            de_max_txt = 0.0
                        try:
                            de_mean_txt = float(global_dental_txt.get("score_mean", 0.0) or 0.0)
                        except Exception:
                            de_mean_txt = 0.0

                        txt_lines.append(
                            f"  Zahnachsen gesamt: Items={de_items_txt}, Max-Score={de_max_txt:.2f}, Mittelwert={de_mean_txt:.2f}"
                        )

            inf = influence_factors or {}
            tcm_block_txt = inf.get("tcm") or {}
            planet_block_txt = inf.get("planet") or {}
            organ_block_txt = inf.get("organ_clock") or {}
            image_block_txt = inf.get("image") or {}

            tcm_label_txt = str(tcm_block_txt.get("label", "")).strip()
            tcm_elem_txt = str(tcm_block_txt.get("element", "")).strip()
            if tcm_label_txt or tcm_elem_txt:
                if tcm_elem_txt and tcm_label_txt:
                    txt_lines.append(
                        f"TCM-Typ: {tcm_label_txt} (Element {tcm_elem_txt})"
                    )
                elif tcm_label_txt:
                    txt_lines.append(f"TCM-Typ: {tcm_label_txt}")
            else:
                txt_lines.append("TCM-Typ: nicht gesetzt")

            planet_label_txt = str(planet_block_txt.get("label", "")).strip()
            if planet_label_txt:
                txt_lines.append(f"Planetentyp: {planet_label_txt}")
            else:
                txt_lines.append("Planetentyp: nicht gesetzt")

            organ_seg_txt = str(organ_block_txt.get("segment", "")).strip()
            if organ_seg_txt:
                txt_lines.append(f"Organuhr: {organ_seg_txt}")
            else:
                txt_lines.append("Organuhr: neutral")

            img_present_txt = bool(image_block_txt.get("present", False))
            img_source_txt = str(image_block_txt.get("source", "")).strip() or "default"
            if img_present_txt:
                txt_lines.append(
                    f"Bildsignatur: gesetzt (Quelle: {img_source_txt})"
                )
            else:
                txt_lines.append("Bildsignatur: nicht gesetzt")

            if influence_scoring is not None and bool(influence_scoring.get("enabled")):
                organs_summary_txt: List[str] = []
                tcm_orgs_txt = str(tcm_block_txt.get("organs", "") or "").strip()
                if tcm_orgs_txt:
                    for part in tcm_orgs_txt.split(","):
                        part_str = part.strip()
                        if part_str:
                            organs_summary_txt.append(part_str)
                active_orgs_txt = organ_block_txt.get("active_organs") or []
                if isinstance(active_orgs_txt, (list, tuple)):
                    for o in active_orgs_txt:
                        if isinstance(o, str):
                            o_str = o.strip()
                            if o_str:
                                organs_summary_txt.append(o_str)
                uniq_orgs_txt: List[str] = []
                seen_txt: set[str] = set()
                for o in organs_summary_txt:
                    if not o:
                        continue
                    if o not in seen_txt:
                        seen_txt.add(o)
                        uniq_orgs_txt.append(o)
                if uniq_orgs_txt:
                    try:
                        max_delta_val_txt = float(influence_scoring.get("max_delta", 0.0) or 0.0)
                        max_pct_val_txt = int(round(max_delta_val_txt * 100.0))
                        if max_pct_val_txt <= 0:
                            max_pct_val_txt = 3
                    except Exception:
                        max_pct_val_txt = 3
                    joined_orgs_txt = ", ".join(uniq_orgs_txt)
                    txt_lines.append(
                        f"Influence-Scoring aktiv (max. +{max_pct_val_txt}% für Items zu: {joined_orgs_txt})."
                    )

            txt_lines.extend(
                [
                    "",
                    "Verwendete Gruppen:",
                    ", ".join(sorted(used_groups)),
                    "",
                    "Top-Resonanzen (NLS v2) - nach Gruppen:",
                ]
            )
            
            # Gruppiere Ausgabe nach Kategorien
            for group_name in sorted(used_groups):
                group_items = [e for e in top_scores if e.get("group") == group_name]
                if group_items:
                    txt_lines.append(f"\n{group_name.upper()}:")
                    for entry in group_items[:5]:  # Top 5 pro Gruppe
                        txt_lines.append(f"- {entry['label']}: score={entry['score']:.4f}, rel={entry['reliability']:.2f}")

            if synergy_export:
                label_counts_txt: Dict[str, int] = {}
                combo_count_txt = len(synergy_export)
                for combo in synergy_export:
                    items = combo.get("items", []) or []
                    for item in items:
                        item_label = str(item.get("label", "")).strip()
                        if not item_label:
                            continue
                        label_counts_txt[item_label] = label_counts_txt.get(item_label, 0) + 1

                if label_counts_txt:
                    txt_lines.append("")
                    txt_lines.append("Quantum-Synergy – häufigste Trigger (regelbasiert):")
                    for label, count in sorted(label_counts_txt.items(), key=lambda kv: (-kv[1], kv[0]))[:5]:
                        txt_lines.append(f"- {label} (in {count} von {combo_count_txt} Kombinationen)")

            # Optionale Bruce-Copen-DB-Analyse im TXT-Report, basierend auf db_analysis.summary
            db_block_txt = export_data.get("db_analysis") or {}
            if isinstance(db_block_txt, dict):
                db_summary_txt = db_block_txt.get("summary") or {}
            else:
                db_summary_txt = {}

            if isinstance(db_summary_txt, dict) and db_summary_txt.get("resonance_count"):
                try:
                    items_total_txt = int(db_summary_txt.get("items_total", 0) or 0)
                except Exception:
                    items_total_txt = 0
                try:
                    res_count_txt = int(db_summary_txt.get("resonance_count", 0) or 0)
                except Exception:
                    res_count_txt = 0

                top_res_txt = db_summary_txt.get("top_resonance") or []
                txt_lines.append("")
                txt_lines.append("Bruce-Copen-DB-Analyse (experimentell):")
                txt_lines.append(
                    f"Items mit Resonanz: {res_count_txt} von {items_total_txt}."
                )
                if isinstance(top_res_txt, list) and top_res_txt:
                    for idx, entry in enumerate(top_res_txt[:5], 1):
                        try:
                            label_tr = str(entry.get("label", "") or "").strip()
                            group_tr = str(entry.get("group", "") or "").strip()
                            score_raw = entry.get("resonance_score")
                            score_val = float(score_raw) if score_raw is not None else 0.0
                        except Exception:
                            continue
                        if group_tr:
                            line = (
                                f"{idx}. {label_tr} [{group_tr}] – Resonanz {score_val:.1f} / 100"
                            )
                        else:
                            line = f"{idx}. {label_tr} – Resonanz {score_val:.1f} / 100"
                        txt_lines.append(line)

            txt_content = "\n".join(line for line in txt_lines if line)
            _atomic_write_text(txt_path, txt_content)

            try:
                high_mid: List[Dict[str, object]] = []
                max_score_hm = 0.0
                try:
                    if sub_results_top:
                        max_score_hm = max(
                            float(e.get("score", 0.0) or 0.0) for e in sub_results_top
                        )
                    else:
                        max_score_hm = 0.0
                except Exception:
                    max_score_hm = 0.0

                if sub_results_top and max_score_hm > 0.0:
                    for e in sub_results_top:
                        try:
                            s_val = float(e.get("score", 0.0) or 0.0)
                        except Exception:
                            s_val = 0.0
                        rel = s_val / max_score_hm if max_score_hm > 0.0 else 0.0
                        if rel >= 0.66:
                            prio = "hoch"
                        elif rel >= 0.33:
                            prio = "mittel"
                        else:
                            prio = "niedrig"
                        if prio not in ("hoch", "mittel"):
                            continue
                        label_hm = str(e.get("label", "")).strip()
                        if not label_hm:
                            continue
                        try:
                            cr_val = float(e.get("copen_rate", 0.0) or 0.0)
                        except Exception:
                            cr_val = 0.0
                        high_mid.append(
                            {
                                "label": label_hm,
                                "copen_rate": cr_val,
                                "score": s_val,
                                "priority": prio,
                            }
                        )

                if high_mid:
                    high_mid_sorted = sorted(
                        high_mid,
                        key=lambda r: float(r.get("score", 0.0) or 0.0),
                        reverse=True,
                    )
                    labels_lines: List[str] = []
                    copen_lines: List[str] = []
                    for rec in high_mid_sorted:
                        labels_lines.append(str(rec.get("label", "")))
                        try:
                            cr_line = float(rec.get("copen_rate", 0.0) or 0.0)
                            if float(cr_line).is_integer():
                                copen_lines.append(f"{int(cr_line)}")
                            else:
                                copen_lines.append(f"{cr_line:.4f}")
                        except Exception:
                            copen_lines.append("0")

                    base_stem = txt_path.with_suffix("").name
                    labels_path = txt_path.with_name(base_stem + "_labels_hoch_mittel.txt")
                    rates_path = txt_path.with_name(base_stem + "_copen_hoch_mittel.txt")
                    if labels_lines:
                        _atomic_write_text(labels_path, "\n".join(labels_lines))
                    if copen_lines:
                        _atomic_write_text(rates_path, "\n".join(copen_lines))
            except Exception:
                pass
            
            ok_json = json_path.exists() and json_path.stat().st_size > 0
            ok_html = html_path.exists() and html_path.stat().st_size > 0
            ok_txt = txt_path.exists() and txt_path.stat().st_size > 0
            typer.echo(f"JSON geschrieben: {'OK' if ok_json else 'FEHLER'} -> {json_path}")
            typer.echo(f"HTML geschrieben: {'OK' if ok_html else 'FEHLER'} -> {html_path}")
            typer.echo(f"TXT geschrieben:  {'OK' if ok_txt else 'FEHLER'} -> {txt_path}")
            if ok_json:
                typer.echo(f"Export gespeichert: {json_path}")
            if ok_html:
                typer.echo(f"HTML-Report gespeichert: {html_path}")
            if ok_txt:
                typer.echo(f"TXT-Report gespeichert: {txt_path}")

            if export_3d:
                try:
                    typer.echo("Generiere 3D-Export für Viewer...")
                    points_3d = []
                    for entry in scores: 
                        pt_def = map_item_to_point(entry)
                        if pt_def:
                            points_3d.append({
                                "id": pt_def.id,
                                "label": entry["label"], 
                                "layer": pt_def.layer,
                                "coords": pt_def.coords,
                                "value": float(entry["score"]),
                                "intensity": float(entry.get("reliability", 1.0)) / 10.0,
                                "group_hint": pt_def.group_hint
                            })
                    
                    if points_3d:
                        export_3d_file = json_path.with_name(json_path.stem + "_3d_scan.json")
                        with open(export_3d_file, "w", encoding="utf-8") as f:
                            json.dump({
                                "points": points_3d, 
                                "meta": {
                                    "client": f"{first_name} {name}", 
                                    "profile": prof,
                                    "timestamp": time.time()
                                }
                            }, f, indent=2)
                        typer.echo(f"✓ 3D-Daten gespeichert: {export_3d_file}")
                    else:
                        typer.echo("⚠ Keine 3D-Punkte gemappt (Daten vorhanden aber ohne Mapping).")
                except Exception as e3d:
                    typer.echo(f"⚠ Fehler beim 3D-Export: {e3d}")

        except Exception as exc:
            typer.echo(f"Export fehlgeschlagen: {exc}")


@app.command("nls-3d-export")
def nls_3d_export(
    input_file: Path = typer.Argument(
        ...,
        help="JSON-Exportdatei eines field_test- oder multiplex-scan-Laufs",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        help=(
            "Zieldatei fuer 3D-Scan-Export (JSON). Standard: "
            "<basename>_3d_scan.json im selben Ordner."
        ),
    ),
) -> None:
    """Erzeugt einen symbolischen 3D-Scan-Export aus einem vorhandenen JSON-Export.

    Nutzt NLS3D_POINTS und map_item_to_point, um Items auf logische 3D-Punkte
    zu mappen. Der Export ist rein additiv und veraendert keine bestehenden
    JSON/TXT-Reports.
    """

    if not input_file.exists() or not input_file.is_file():
        typer.echo(f"Eingabedatei existiert nicht oder ist keine Datei: {input_file}")
        raise typer.Exit(code=1)

    try:
        data = json.loads(input_file.read_text(encoding="utf-8"))
    except Exception as exc:
        typer.echo(f"JSON konnte nicht gelesen werden: {exc}")
        raise typer.Exit(code=1)

    cmd = str(data.get("command", "") or "").strip().lower()
    if cmd not in {"field_test", "multiplex_scan"}:
        typer.echo(
            f"Warnung: Unerwarteter command-Typ '{cmd}' im Export (erwartet 'field_test' oder 'multiplex_scan')."
        )

    sub_results = data.get("sub_results") or {}
    sub_top = None
    if isinstance(sub_results, dict):
        sub_top = sub_results.get("top")

    items_source = None
    if isinstance(sub_top, list) and sub_top:
        items_source = sub_top
    else:
        top_scores = data.get("top_scores") or []
        if isinstance(top_scores, list) and top_scores:
            items_source = top_scores

    if not items_source:
        typer.echo("Keine geeigneten Item-Listen (sub_results.top oder top_scores) im Export gefunden.")
        raise typer.Exit(code=1)

    by_point: Dict[str, Dict[str, object]] = {}
    global_max_score = 0.0

    for entry in items_source:
        try:
            label = str(entry.get("label", "") or "").strip()
        except Exception:
            label = ""
        if not label:
            continue

        group_val = str(entry.get("group", "") or "").strip()
        try:
            score = float(entry.get("score", 0.0) or 0.0)
        except Exception:
            score = 0.0
        if score <= 0.0:
            continue

        point_id = map_item_to_point(label, group_val)
        if not point_id:
            continue

        acc = by_point.setdefault(
            point_id,
            {"score_sum": 0.0, "score_max": 0.0, "count": 0},
        )

        try:
            cur_sum = float(acc.get("score_sum", 0.0) or 0.0)
        except Exception:
            cur_sum = 0.0
        try:
            cur_max = float(acc.get("score_max", 0.0) or 0.0)
        except Exception:
            cur_max = 0.0
        try:
            cur_count = int(acc.get("count", 0) or 0)
        except Exception:
            cur_count = 0

        new_sum = cur_sum + score
        new_max = max(cur_max, score)
        new_count = cur_count + 1

        acc["score_sum"] = new_sum
        acc["score_max"] = new_max
        acc["count"] = new_count

        if new_max > global_max_score:
            global_max_score = new_max

    if not by_point:
        typer.echo(
            "Keine Items konnten einem 3D-Punkt zugeordnet werden (Mapping ergab keine Treffer)."
        )
        raise typer.Exit(code=1)

    points_out: List[Dict[str, object]] = []
    for pid, stats in sorted(
        by_point.items(),
        key=lambda kv: float(kv[1].get("score_sum", 0.0) or 0.0),
        reverse=True,
    ):
        point_def = NLS3D_POINTS.get(pid)
        if point_def is not None:
            label_pt = point_def.label
            layer = point_def.layer
            coords = list(point_def.coords)
            group_hint = list(point_def.group_hint)
        else:
            label_pt = pid
            layer = "unbekannt"
            coords = [0.0, 0.0, 0.0]
            group_hint = []

        try:
            score_sum = float(stats.get("score_sum", 0.0) or 0.0)
        except Exception:
            score_sum = 0.0
        try:
            score_max = float(stats.get("score_max", 0.0) or 0.0)
        except Exception:
            score_max = 0.0
        try:
            count = int(stats.get("count", 0) or 0)
        except Exception:
            count = 0

        if global_max_score > 0.0:
            normalized = score_max / global_max_score
        else:
            normalized = 0.0

        points_out.append(
            {
                "id": pid,
                "label": label_pt,
                "layer": layer,
                "coords": coords,
                "score_sum": score_sum,
                "score_max": score_max,
                "normalized": float(normalized),
                "count": int(count),
                "group_hint": group_hint,
            }
        )

    client_block = data.get("client") or {}

    export_data = {
        "schema": "nls3d_points_v1",
        "source_file": str(input_file.name),
        "command": cmd,
        "client": client_block,
        "generated_at": float(time.time()),
        "points": points_out,
    }

    if output is None:
        out_dir = input_file.parent
        base_name = input_file.with_suffix("").name
        output = out_dir / f"{base_name}_3d_scan.json"

    try:
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        _atomic_write_text(output, json_str)
        typer.echo(f"3D-Scan-Export geschrieben: {output}")
    except Exception as exc:
        typer.echo(f"3D-Scan-Export fehlgeschlagen: {exc}")
        raise typer.Exit(code=1)


@app.command("analyze-trends")
def analyze_trends(
    input_dir: Path = typer.Argument(..., help="Ordner mit JSON-Exporten von field_test/multiplex-scan"),
    client: str = typer.Option(
        "",
        "--client",
        help="Optional: Filter nach Klient (Teilstring in 'Vorname Nachname')",
    ),
    top_n: int = typer.Option(10, "--top-n", min=1, help="Anzahl der Top-Trend-Items"),
    recent: int = typer.Option(
        5,
        "--recent",
        min=1,
        help="Anzahl der letzten Sitzungen pro Item zur Trendberechnung",
    ),
) -> None:
    """Analysiert Archiv-Exports und zeigt wiederkehrende & aufsteigende Items."""

    if not input_dir.exists() or not input_dir.is_dir():
        typer.echo(f"Eingabeordner existiert nicht oder ist kein Ordner: {input_dir}")
        raise typer.Exit(code=1)

    files = sorted(input_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        typer.echo("Keine JSON-Exportdateien gefunden.")
        raise typer.Exit(code=1)

    client_filter = (client or "").strip().lower()

    label_entries: Dict[str, List[tuple[float, float]]] = {}
    mf_coherence_series: List[tuple[float, float]] = []
    mf_strength_series: List[tuple[float, float]] = []

    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        cmd = str(data.get("command", "")).strip().lower()
        if cmd not in {"field_test", "multiplex_scan"}:
            continue

        client_data = data.get("client") or {}
        first_name = str(client_data.get("first_name", "")).strip()
        last_name = str(client_data.get("name", "")).strip()
        full_name = (first_name + " " + last_name).strip()

        if client_filter and client_filter not in full_name.lower():
            continue

        top_scores = data.get("top_scores") or []
        if not isinstance(top_scores, list):
            continue

        ts = float(path.stat().st_mtime)

        mf_block = data.get("morphic_field") or {}
        if isinstance(mf_block, dict) and mf_block:
            try:
                coh = float(mf_block.get("coherence", 0.0) or 0.0)
            except Exception:
                coh = 0.0
            try:
                strength = float(mf_block.get("field_strength", 0.0) or 0.0)
            except Exception:
                strength = 0.0

            if coh or strength:
                try:
                    ts_mf = float(mf_block.get("timestamp", 0.0) or 0.0)
                except Exception:
                    ts_mf = 0.0
                if ts_mf <= 0.0:
                    ts_mf = ts
                if coh:
                    mf_coherence_series.append((ts_mf, coh))
                if strength:
                    mf_strength_series.append((ts_mf, strength))
        for entry in top_scores:
            try:
                label = str(entry["label"])
                score = float(entry["score"])
            except Exception:
                continue
            bucket = label_entries.setdefault(label, [])
            bucket.append((ts, score))

    if not label_entries:
        typer.echo("Keine passenden Trenddaten gefunden (Filter zu streng oder keine Exporte).")
        raise typer.Exit(code=1)

    stats: List[Dict[str, float | str]] = []
    for label, entries in label_entries.items():
        if len(entries) == 0:
            continue
        entries_sorted = sorted(entries, key=lambda x: x[0])
        count_all = len(entries_sorted)
        recent_entries = entries_sorted[-recent:]
        times_scores = recent_entries
        scores_recent = [s for _, s in times_scores]
        last_t, last_score = times_scores[-1]
        prev_scores = scores_recent[:-1]
        if prev_scores:
            mean_prev = sum(prev_scores) / len(prev_scores)
        else:
            mean_prev = last_score
        delta = last_score - mean_prev
        avg_all = sum(s for _, s in entries_sorted) / count_all
        stats.append(
            {
                "label": label,
                "count": float(count_all),
                "avg": float(avg_all),
                "last": float(last_score),
                "delta": float(delta),
            }
        )

    typer.echo("Morphic Engine V1 – Trendanalyse")
    if client_filter:
        typer.echo(f"Filter Klient: {client}")
    typer.echo(f"Ausgewertete Items: {len(stats)}")

    typer.echo("")
    typer.echo("Wiederkehrende Top-Items (nach Häufigkeit & Durchschnittsscore):")
    stats_recurring = sorted(
        stats,
        key=lambda d: (d["count"], d["avg"]),
        reverse=True,
    )[:top_n]
    for d in stats_recurring:
        typer.echo(
            f"  - {d['label']}: count={int(d['count'])}, avg={d['avg']:.4f}, last={d['last']:.4f}"
        )

    typer.echo("")
    typer.echo("Stärkste Aufwärtstrends (delta zwischen letzter und vorherigen Sitzungen):")
    stats_trend = [d for d in stats if d["count"] >= 2]
    stats_trend = sorted(stats_trend, key=lambda d: d["delta"], reverse=True)[:top_n]
    for d in stats_trend:
        typer.echo(
            f"  - {d['label']}: delta={d['delta']:.4f}, last={d['last']:.4f}, avg={d['avg']:.4f}, count={int(d['count'])}"
        )

    if mf_coherence_series or mf_strength_series:
        typer.echo("")
        typer.echo("Morphische Feld-Parameter (Verlauf):")

        if mf_coherence_series:
            coh_sorted = sorted(mf_coherence_series, key=lambda x: x[0])
            coh_vals = [v for _, v in coh_sorted]
            coh_last = coh_vals[-1]
            if len(coh_vals) > 1:
                coh_mean_prev = sum(coh_vals[:-1]) / float(len(coh_vals) - 1)
            else:
                coh_mean_prev = coh_last
            coh_delta = coh_last - coh_mean_prev
            coh_mean_all = sum(coh_vals) / float(len(coh_vals))
            typer.echo(
                f"  Kohärenz: letzter Wert={coh_last:.4f}, Mittelwert={coh_mean_all:.4f}, Delta={coh_delta:.4f}"
            )

        if mf_strength_series:
            fs_sorted = sorted(mf_strength_series, key=lambda x: x[0])
            fs_vals = [v for _, v in fs_sorted]
            fs_last = fs_vals[-1]
            if len(fs_vals) > 1:
                fs_mean_prev = sum(fs_vals[:-1]) / float(len(fs_vals) - 1)
            else:
                fs_mean_prev = fs_last
            fs_delta = fs_last - fs_mean_prev
            fs_mean_all = sum(fs_vals) / float(len(fs_vals))
            typer.echo(
                f"  Feldstärke: letzter Wert={fs_last:.4f}, Mittelwert={fs_mean_all:.4f}, Delta={fs_delta:.4f}"
            )


@app.command("batch-scan")
def batch_scan(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09041966"),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    profiles: str = typer.Option(
        "pathogen,toxin,regulation",
        "--profiles",
        help="Kommaseparierte Liste von Profilen (z.B. 'pathogen,bat_akut,toxin')",
    ),
    k_total: int = typer.Option(64, "--k-total", min=16, help="Anzahl der Multiplex-Kandidaten pro Profil"),
    top_k: int = typer.Option(10, "--top-k", min=1, help="Anzahl der Top-Resonanzen im Bericht"),
    hardware_profile: str = typer.Option("windows", "--hardware-profile", help="Hardware-Profil"),
) -> None:
    """Führt mehrere Multiplex-Scans in Serie aus (Batch-Modus).
    
    Beispiel:
        python -m apps.cli.main batch-scan "Mustermann" "Max" -d 01011990 -p Berlin --profiles pathogen,bat_akut,toxin
    """
    import subprocess
    import sys
    
    profile_list = [p.strip() for p in profiles.split(",") if p.strip()]
    
    if not profile_list:
        typer.echo("❌ Keine Profile angegeben!")
        raise typer.Exit(code=1)
    
    typer.echo("=" * 70)
    typer.echo("BATCH-SCAN MODUS")
    typer.echo("=" * 70)
    typer.echo(f"Klient: {first_name} {name}")
    typer.echo(f"Profile: {', '.join(profile_list)}")
    typer.echo(f"Kandidaten pro Profil: {k_total}")
    typer.echo("=" * 70)
    typer.echo("")
    
    results = []
    
    for i, profile in enumerate(profile_list, 1):
        typer.echo(f"[{i}/{len(profile_list)}] 🔄 Starte Scan mit Profil: {profile}")
        typer.echo("-" * 50)
        
        # Führe multiplex-scan als Subprocess aus
        cmd = [
            sys.executable, "-m", "apps.cli.main", "multiplex-scan",
            name, first_name,
            "-d", birth_date,
            "-p", birth_place,
            "--profile", profile,
            "--k-total", str(k_total),
            "--top-k", str(top_k),
            "--hardware-profile", hardware_profile,
            "--no-progress",
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            
            # Zeige Output
            if result.stdout:
                # Nur die wichtigsten Zeilen anzeigen
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if any(x in line for x in ["Top Items", "score=", "Export", "B.A.T.", "Empfohlene Remedies", "💊", "#"]):
                        typer.echo(f"  {line}")
            
            if result.returncode == 0:
                results.append({"profile": profile, "status": "OK"})
                typer.echo(f"  ✅ Profil {profile} abgeschlossen")
            else:
                results.append({"profile": profile, "status": "FEHLER", "error": result.stderr})
                typer.echo(f"  ❌ Profil {profile} fehlgeschlagen")
                if result.stderr:
                    typer.echo(f"     Fehler: {result.stderr[:200]}")
        
        except Exception as exc:
            results.append({"profile": profile, "status": "EXCEPTION", "error": str(exc)})
            typer.echo(f"  ❌ Ausnahme bei Profil {profile}: {exc}")
        
        typer.echo("")
    
    # Zusammenfassung
    typer.echo("=" * 70)
    typer.echo("BATCH-SCAN ZUSAMMENFASSUNG")
    typer.echo("=" * 70)
    
    ok_count = sum(1 for r in results if r["status"] == "OK")
    typer.echo(f"Erfolgreich: {ok_count}/{len(profile_list)}")
    
    for r in results:
        status_icon = "✅" if r["status"] == "OK" else "❌"
        typer.echo(f"  {status_icon} {r['profile']}: {r['status']}")
    
    typer.echo("=" * 70)


# ============================================================================
# TOP-N PROFILE SCAN - Automatische Ermittlung der relevantesten Profile
# ============================================================================

# WICHTIG: Profile werden jetzt aus der zentralen Synchronisierung geladen!
# Änderungen an Profilen NUR in core/profile_sync/__init__.py vornehmen!
try:
    from core.profile_sync import get_top3_analysis_profiles as _get_sync_profiles
    TOP3_ANALYSIS_PROFILES = _get_sync_profiles()
    _PROFILES_SYNCED = True
except ImportError:
    _PROFILES_SYNCED = False
    # Fallback: Legacy-Definition (nur wenn profile_sync nicht verfügbar)
    TOP3_ANALYSIS_PROFILES = [
        # Basis-Diagnose
        ("pathogen", "Pathogene Erreger (Bakterien, Viren, Parasiten, Pilze)"),
        ("toxin", "Toxine & Umweltbelastungen"),
        ("immune", "Immunsystem"),
        ("detox", "Entgiftung"),
        ("regulation", "Energetische Regulation"),
        # Organ-spezifisch
        ("verdauung_detailliert", "Verdauungssystem"),
        ("leber_detailliert", "Leber & Gallensystem"),
        ("nervensystem_detailliert", "Nervensystem"),
        ("herz_kreislauf_fein", "Herz-Kreislauf"),
        ("atmung_lunge_detailliert", "Atmung & Lunge"),
        ("endokrin_detailliert", "Hormonsystem"),
        ("haut_detailliert", "Haut"),
        ("niere_detailliert", "Niere & Harnwege"),
        ("lymphsystem_detailliert", "Lymphsystem"),
        ("immunsystem_detailliert", "Immunsystem detailliert"),
        ("gehirn_detailliert", "Gehirn & ZNS"),
        # Struktur
        ("knochen_detailliert", "Knochen & Gelenke"),
        ("wirbelsaeule_detailliert", "Wirbelsäule"),
        ("zahn_detailliert", "Zähne & Kiefer"),
        ("tote_zaehne_detailliert", "Tote Zähne & Herde"),
        # Symptom-spezifisch
        ("schmerz_detailliert", "Schmerz & Schlaf"),
        ("schwindel_detailliert", "Schwindel"),
        ("allergie_detailliert", "Allergien & Unverträglichkeiten"),
        # Belastungen & Vergiftung
        ("schwermetalle", "Schwermetalle"),
        ("strahlung_detailliert", "Strahlung & EMF"),
        ("stoerfelder_toxisch", "Störfelder"),
        ("vergiftung_komplett", "Vergiftungserscheinungen (komplett)"),
        ("pestizide_herbizide", "Pestizide & Herbizide"),
        ("medikamenten_toxizitaet", "Medikamenten-Toxizität"),
        # Intoleranzen & Stoffwechsel
        ("nahrungsmittel_intoleranzen", "Nahrungsmittel-Intoleranzen"),
        ("mitochondrien_dysfunktion", "Mitochondrien-Dysfunktion"),
        ("bindegewebe_faszien", "Bindegewebe & Faszien"),
        # Psyche & Energie
        ("psyche_detailliert", "Psyche & Emotionen"),
        ("chakren_meridiane", "Chakren & Meridiane"),
        ("miasma_detailliert", "Miasmen & Erbbelastungen"),
    ]

# Fokus-zu-Profil-Mapping für intelligente Profil-Priorisierung
FOCUS_PROFILE_MAP: Dict[str, List[str]] = {
    # Organe
    "leber": ["leber_detailliert", "verdauung_detailliert", "detox", "toxin", "vergiftung_komplett"],
    "galle": ["leber_detailliert", "verdauung_detailliert"],
    "niere": ["niere_detailliert", "detox", "vergiftung_komplett"],
    "darm": ["verdauung_detailliert", "pathogen", "immune"],
    "magen": ["verdauung_detailliert", "pathogen"],
    "herz": ["herz_kreislauf_fein", "regulation"],
    "lunge": ["atmung_lunge_detailliert", "pathogen"],
    "gehirn": ["gehirn_detailliert", "nervensystem_detailliert", "schwindel_detailliert"],
    "haut": ["haut_detailliert", "allergie_detailliert", "detox"],
    "lymph": ["lymphsystem_detailliert", "immune", "detox"],
    # Systeme
    "immun": ["immune", "immunsystem_detailliert", "pathogen", "lymphsystem_detailliert"],
    "hormon": ["endokrin_detailliert", "regulation"],
    "nerv": ["nervensystem_detailliert", "gehirn_detailliert", "schmerz_detailliert"],
    "verdauung": ["verdauung_detailliert", "leber_detailliert", "pathogen"],
    # Symptome
    "schmerz": ["schmerz_detailliert", "nervensystem_detailliert", "wirbelsaeule_detailliert"],
    "kopfschmerz": ["gehirn_detailliert", "nervensystem_detailliert", "schmerz_detailliert", "zahn_detailliert"],
    "migrän": ["gehirn_detailliert", "nervensystem_detailliert", "leber_detailliert"],
    "schwindel": ["schwindel_detailliert", "nervensystem_detailliert", "herz_kreislauf_fein"],
    "müdig": ["endokrin_detailliert", "regulation", "immune", "vergiftung_komplett"],
    "schlaf": ["schmerz_detailliert", "nervensystem_detailliert", "psyche_detailliert"],
    "allergie": ["allergie_detailliert", "immune", "haut_detailliert", "verdauung_detailliert"],
    # Struktur
    "zahn": ["zahn_detailliert", "tote_zaehne_detailliert", "stoerfelder_toxisch"],
    "zähn": ["zahn_detailliert", "tote_zaehne_detailliert", "stoerfelder_toxisch"],
    "wirbel": ["wirbelsaeule_detailliert", "schmerz_detailliert", "nervensystem_detailliert"],
    "rücken": ["wirbelsaeule_detailliert", "schmerz_detailliert"],
    "gelenk": ["knochen_detailliert", "schmerz_detailliert", "immune"],
    "knochen": ["knochen_detailliert", "schmerz_detailliert"],
    # Belastungen & Vergiftung
    "entgift": ["detox", "leber_detailliert", "vergiftung_komplett", "schwermetalle"],
    "detox": ["detox", "leber_detailliert", "vergiftung_komplett", "schwermetalle"],
    "gift": ["vergiftung_komplett", "toxin", "schwermetalle", "detox"],
    "vergift": ["vergiftung_komplett", "toxin", "schwermetalle", "detox"],
    "schwermetall": ["schwermetalle", "vergiftung_komplett", "detox", "nervensystem_detailliert"],
    "quecksilber": ["schwermetalle", "vergiftung_komplett", "nervensystem_detailliert"],
    "amalgam": ["schwermetalle", "zahn_detailliert", "vergiftung_komplett"],
    "strahl": ["strahlung_detailliert", "vergiftung_komplett", "immune"],
    "emf": ["strahlung_detailliert", "nervensystem_detailliert"],
    "elektro": ["strahlung_detailliert", "nervensystem_detailliert"],
    "pestizid": ["vergiftung_komplett", "toxin", "detox"],
    "herbizid": ["vergiftung_komplett", "toxin", "detox"],
    "chemie": ["vergiftung_komplett", "toxin", "allergie_detailliert"],
    # Psyche
    "angst": ["psyche_detailliert", "nervensystem_detailliert"],
    "depression": ["psyche_detailliert", "nervensystem_detailliert", "endokrin_detailliert"],
    "stress": ["psyche_detailliert", "endokrin_detailliert", "regulation"],
    "trauma": ["psyche_detailliert", "miasma_detailliert"],
    "psyche": ["psyche_detailliert", "nervensystem_detailliert"],
    # Erreger
    "virus": ["pathogen", "immune", "immunsystem_detailliert"],
    "bakter": ["pathogen", "immune"],
    "pilz": ["pathogen", "immune", "verdauung_detailliert"],
    "candida": ["pathogen", "verdauung_detailliert", "immune"],
    "parasit": ["pathogen", "verdauung_detailliert", "immune"],
    "borrel": ["pathogen", "immune", "nervensystem_detailliert"],
    "infekt": ["pathogen", "immune", "immunsystem_detailliert"],
    # Energie
    "chakr": ["chakren_meridiane", "regulation", "psyche_detailliert"],
    "meridian": ["chakren_meridiane", "regulation"],
    "energie": ["regulation", "chakren_meridiane", "endokrin_detailliert", "mitochondrien_dysfunktion"],
    "miasm": ["miasma_detailliert", "pathogen"],
    # Neue Profile 30.11.2025
    "pestizid": ["pestizide_herbizide", "vergiftung_komplett", "toxin", "detox"],
    "herbizid": ["pestizide_herbizide", "vergiftung_komplett", "toxin"],
    "glyphosat": ["pestizide_herbizide", "vergiftung_komplett", "nervensystem_detailliert"],
    "medikament": ["medikamenten_toxizitaet", "vergiftung_komplett", "leber_detailliert"],
    "nebenwirkung": ["medikamenten_toxizitaet", "vergiftung_komplett"],
    "histamin": ["nahrungsmittel_intoleranzen", "allergie_detailliert", "verdauung_detailliert"],
    "gluten": ["nahrungsmittel_intoleranzen", "verdauung_detailliert", "immune"],
    "laktose": ["nahrungsmittel_intoleranzen", "verdauung_detailliert"],
    "intoleranz": ["nahrungsmittel_intoleranzen", "allergie_detailliert", "verdauung_detailliert"],
    "unverträglich": ["nahrungsmittel_intoleranzen", "allergie_detailliert"],
    "mitochondr": ["mitochondrien_dysfunktion", "regulation", "vergiftung_komplett"],
    "erschöpf": ["mitochondrien_dysfunktion", "endokrin_detailliert", "regulation"],
    "fatigue": ["mitochondrien_dysfunktion", "immune", "endokrin_detailliert"],
    "chronic fatigue": ["mitochondrien_dysfunktion", "immune", "pathogen"],
    "bindegewebe": ["bindegewebe_faszien", "knochen_detailliert", "immune"],
    "faszien": ["bindegewebe_faszien", "schmerz_detailliert", "wirbelsaeule_detailliert"],
    "kollagen": ["bindegewebe_faszien", "haut_detailliert"],
    "matrix": ["bindegewebe_faszien", "detox", "lymphsystem_detailliert"],
    # Ergänzungen 01.12.2025 - Fokus-Verbesserung
    "bandscheibe": ["wirbelsaeule_detailliert", "knochen_detailliert", "schmerz_detailliert", "nervensystem_detailliert"],
    "bandscheiben": ["wirbelsaeule_detailliert", "knochen_detailliert", "schmerz_detailliert", "nervensystem_detailliert"],
    "gedächtnis": ["gehirn_detailliert", "nervensystem_detailliert", "psyche_detailliert"],
    "gedaechtnis": ["gehirn_detailliert", "nervensystem_detailliert", "psyche_detailliert"],
    "konzentration": ["gehirn_detailliert", "nervensystem_detailliert", "endokrin_detailliert"],
    "fühlen": ["psyche_detailliert", "nervensystem_detailliert", "gehirn_detailliert"],
    "fuehlen": ["psyche_detailliert", "nervensystem_detailliert", "gehirn_detailliert"],
    "gefühl": ["psyche_detailliert", "nervensystem_detailliert"],
    "emotion": ["psyche_detailliert", "nervensystem_detailliert", "endokrin_detailliert"],
    "blut": ["herz_kreislauf_fein", "immune", "leber_detailliert", "lymphsystem_detailliert"],
    "blutdruck": ["herz_kreislauf_fein", "niere_detailliert", "endokrin_detailliert"],
    "kreislauf": ["herz_kreislauf_fein", "regulation"],
    "durchblutung": ["herz_kreislauf_fein", "nervensystem_detailliert"],
    "ischias": ["wirbelsaeule_detailliert", "nervensystem_detailliert", "schmerz_detailliert"],
    "hexenschuss": ["wirbelsaeule_detailliert", "schmerz_detailliert"],
    "lendenwirbel": ["wirbelsaeule_detailliert", "schmerz_detailliert", "nervensystem_detailliert"],
    "halswirbel": ["wirbelsaeule_detailliert", "schmerz_detailliert", "nervensystem_detailliert"],
    "brustwirbel": ["wirbelsaeule_detailliert", "schmerz_detailliert"],
    "skoliose": ["wirbelsaeule_detailliert", "knochen_detailliert", "schmerz_detailliert"],
    "arthrose": ["knochen_detailliert", "schmerz_detailliert", "immune"],
    "arthritis": ["knochen_detailliert", "immune", "schmerz_detailliert"],
    "rheuma": ["immune", "knochen_detailliert", "schmerz_detailliert", "verdauung_detailliert"],
    "osteoporose": ["knochen_detailliert", "endokrin_detailliert"],
    "demenz": ["gehirn_detailliert", "nervensystem_detailliert", "vergiftung_komplett"],
    "alzheimer": ["gehirn_detailliert", "nervensystem_detailliert", "vergiftung_komplett"],
    "parkinson": ["gehirn_detailliert", "nervensystem_detailliert", "vergiftung_komplett"],
    "multiple sklerose": ["nervensystem_detailliert", "immune", "gehirn_detailliert"],
    "ms": ["nervensystem_detailliert", "immune", "gehirn_detailliert"],
    "tinnitus": ["nervensystem_detailliert", "gehirn_detailliert", "zahn_detailliert", "schwindel_detailliert"],
    "hörsturz": ["nervensystem_detailliert", "herz_kreislauf_fein"],
    "auge": ["nervensystem_detailliert", "gehirn_detailliert", "leber_detailliert"],
    "sehen": ["nervensystem_detailliert", "gehirn_detailliert", "leber_detailliert"],
    "diabetes": ["endokrin_detailliert", "verdauung_detailliert", "herz_kreislauf_fein"],
    "schilddrüse": ["endokrin_detailliert", "immune", "regulation"],
    "schilddruese": ["endokrin_detailliert", "immune", "regulation"],
    "nebenniere": ["endokrin_detailliert", "regulation", "psyche_detailliert"],
    "burnout": ["endokrin_detailliert", "psyche_detailliert", "mitochondrien_dysfunktion"],
    "erschöpfung": ["mitochondrien_dysfunktion", "endokrin_detailliert", "regulation"],
    "chronisch": ["mitochondrien_dysfunktion", "immune", "pathogen"],
    "autoimmun": ["immune", "immunsystem_detailliert", "verdauung_detailliert"],
    "entzündung": ["immune", "pathogen", "verdauung_detailliert"],
    "entzuendung": ["immune", "pathogen", "verdauung_detailliert"],
}


def _compute_focus_profile_bonus(focus: str, profile_name: str) -> float:
    """
    Berechnet einen Fokus-Bonus für ein Profil basierend auf dem Fokus-Text.
    
    Returns:
        0.25 (25%) wenn Profil direkt zum Fokus passt
        0.15 (15%) wenn Profil sekundär relevant ist
        0.10 (10%) wenn Profil artverwandt ist
        0.00 wenn kein Bezug
    """
    if not focus:
        return 0.0
    
    focus_lower = focus.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    profile_lower = profile_name.lower()
    
    # Direkte Treffer im Profil-Namen
    for keyword in focus_lower.split():
        if len(keyword) >= 3 and keyword in profile_lower:
            return 0.25  # Direkter Treffer: 25% Bonus
    
    # Prüfe Fokus-Mapping
    for focus_key, profiles in FOCUS_PROFILE_MAP.items():
        focus_key_norm = focus_key.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        if focus_key_norm in focus_lower or focus_key in focus.lower():
            if profile_name in profiles:
                # Position in der Liste bestimmt Relevanz
                idx = profiles.index(profile_name)
                if idx == 0:
                    return 0.25  # Primäres Profil: 25% Bonus
                elif idx <= 2:
                    return 0.15  # Sekundäres Profil: 15% Bonus
                else:
                    return 0.10  # Artverwandtes Profil: 10% Bonus
    
    return 0.0


@app.command("top3-scan")
def top3_scan(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09041966"),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    export_path: str = typer.Option("C:\\Benutzer_Archive_Start", "--export", "-e", help="Export-Verzeichnis"),
    focus: str = typer.Option("", "--focus", "-f", help="Optionaler Fokus/Symptom des Klienten"),
    k_total: int = typer.Option(4096, "--k-total", min=16, help="Anzahl der Multiplex-Kandidaten pro Profil"),
    top_k: int = typer.Option(192, "--top-k", min=1, help="Anzahl der Top-Resonanzen im Bericht"),
    hardware_profile: str = typer.Option("windows", "--hardware-profile", help="Hardware-Profil"),
    quick_scan: bool = typer.Option(True, "--quick/--full", help="Schnell-Scan (weniger Kandidaten) oder Voll-Scan"),
    synergy: bool = typer.Option(True, "--synergy/--no-synergy", help="Quantum-Synergy Analyse aktivieren"),
    synergy_combos: int = typer.Option(4, "--synergy-combos", help="Anzahl Synergy-Kombinationen"),
    synergy_threshold: float = typer.Option(6.0, "--synergy-threshold", help="Synergy-Schwellenwert (Standard: 6.0 wie früher)"),
    top_n: int = typer.Option(5, "--top-n", "-n", min=3, max=10, help="Anzahl der Top-Profile (Standard: 5, früher 3)"),
) -> None:
    """Ermittelt automatisch die Top-N relevantesten Profile und führt vollständige Analysen durch.
    
    Dieser Befehl führt zunächst einen schnellen Screening-Scan über alle Haupt-Profile durch,
    ermittelt die N Profile mit den höchsten Resonanzen (Standard: 5) und führt dann vollständige 
    Analysen für diese Profile durch. Bei gesetztem Fokus werden fokus-relevante Profile priorisiert.
    
    Beispiel:
        python -m apps.cli.main top3-scan "Mustermann" "Max" -d 01011990 -p Berlin
        python -m apps.cli.main top3-scan "Mustermann" "Max" -d 01011990 -p Berlin --top-n 3 --focus "Bandscheiben"
    """
    import subprocess
    import sys
    import json
    from pathlib import Path
    
    typer.echo("=" * 70)
    typer.echo(f"TOP-{top_n} PROFIL-ANALYSE")
    typer.echo("=" * 70)
    typer.echo(f"Klient: {first_name} {name}")
    typer.echo(f"Geburtsdatum: {birth_date}")
    typer.echo(f"Geburtsort: {birth_place}")
    typer.echo("=" * 70)
    typer.echo("")
    
    # Phase 1: Schnelles Screening aller Profile
    typer.echo("📊 PHASE 1: Screening aller Haupt-Profile...")
    typer.echo("-" * 50)
    
    screening_k = 24 if quick_scan else 48  # Weniger Kandidaten für Screening
    profile_scores = []
    
    for i, (profile_name, profile_desc) in enumerate(TOP3_ANALYSIS_PROFILES, 1):
        typer.echo(f"  [{i}/{len(TOP3_ANALYSIS_PROFILES)}] Screening: {profile_name}...", nl=False)
        
        # Führe schnellen Scan durch
        cmd = [
            sys.executable, "-m", "apps.cli.main", "multiplex-scan",
            name, first_name,
            "-d", birth_date,
            "-p", birth_place,
            "--profile", profile_name,
            "--k-total", str(screening_k),
            "--top-k", "5",
            "--hardware-profile", hardware_profile,
            "--no-progress",
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,  # 2 Minuten Timeout
            )
            
            # Extrahiere durchschnittlichen Score aus Output
            # Erfolg wird anhand des Outputs geprüft, nicht nur Return-Code
            avg_score = 0.0
            high_count = 0
            output = result.stdout + result.stderr
            lines = output.strip().split("\n")
            
            # Prüfe ob Export erfolgreich war
            export_success = any("Export gespeichert" in line or "HTML geschrieben: OK" in line for line in lines)
            
            for line in lines:
                if "score=" in line:
                    try:
                        score_part = line.split("score=")[1].split()[0].rstrip(",")
                        score = float(score_part.replace(",", "."))
                        avg_score += score
                        high_count += 1
                    except (IndexError, ValueError):
                        pass
            
            if export_success or high_count > 0:
                if high_count > 0:
                    avg_score = avg_score / high_count
                
                profile_scores.append({
                    "profile": profile_name,
                    "description": profile_desc,
                    "avg_score": avg_score,
                    "high_count": high_count,
                })
                typer.echo(f" ✓ (avg={avg_score:.3f}, n={high_count})")
            else:
                typer.echo(f" ✗ (Fehler)")
        
        except subprocess.TimeoutExpired:
            typer.echo(f" ✗ (Timeout)")
        except Exception as exc:
            typer.echo(f" ✗ ({exc})")
    
    typer.echo("")
    
    # === FOKUS-BASIERTE PROFIL-PRIORISIERUNG ===
    # Berechne finalen Score mit Fokus-Bonus
    for p in profile_scores:
        focus_bonus = _compute_focus_profile_bonus(focus, p["profile"])
        p["focus_bonus"] = focus_bonus
        p["raw_score"] = p["avg_score"]
        p["final_score"] = p["avg_score"] * (1 + focus_bonus)
    
    # Sortiere nach finalem Score (mit Fokus-Bonus)
    profile_scores.sort(key=lambda x: x["final_score"], reverse=True)
    
    # Signifikanz-Prüfung: Wenn ein nicht-fokus-relevantes Profil >25% höher ist,
    # wird es trotzdem berücksichtigt
    if focus:
        # Finde das beste fokus-relevante Profil
        best_focus_profile = None
        for p in profile_scores:
            if p["focus_bonus"] > 0:
                best_focus_profile = p
                break
        
        # Prüfe ob ein nicht-fokus-relevantes Profil signifikant höher ist
        if best_focus_profile:
            best_focus_raw = best_focus_profile["raw_score"]
            for p in profile_scores:
                if p["focus_bonus"] == 0 and p["raw_score"] > best_focus_raw * 1.25:
                    # Dieses Profil ist signifikant höher - markieren
                    p["significant_override"] = True
                    typer.echo(f"  ⚠️  {p['profile']} hat signifikant höhere Resonanz ({p['raw_score']:.3f} vs {best_focus_raw:.3f})")
    
    # Top-N ermitteln (Standard: 5, konfigurierbar)
    top_profiles = profile_scores[:top_n]
    
    typer.echo("=" * 70)
    typer.echo(f"🏆 TOP-{top_n} RELEVANTE PROFILE:")
    if focus:
        typer.echo(f"   (Fokus: {focus} - Gewichtung: 25%/15%/10%)")
    typer.echo("=" * 70)
    for i, p in enumerate(top_profiles, 1):
        bonus_str = f" [+{p['focus_bonus']*100:.0f}% Fokus]" if p.get("focus_bonus", 0) > 0 else ""
        override_str = " ⚠️ SIGNIFIKANT" if p.get("significant_override") else ""
        typer.echo(f"  {i}. {p['profile']} ({p['description']}){bonus_str}{override_str}")
        typer.echo(f"     Resonanz: {p['raw_score']:.4f} → Final: {p['final_score']:.4f}")
    typer.echo("")
    
    # Phase 2: Vollständige Analyse der Top-N
    typer.echo("=" * 70)
    typer.echo(f"📋 PHASE 2: Vollständige Analyse der Top-{top_n} Profile...")
    typer.echo("=" * 70)
    typer.echo("")
    
    # Erstelle Session-Timestamp für alle Profile
    from datetime import datetime
    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    results = []
    
    for i, p in enumerate(top_profiles, 1):
        profile_name = p["profile"]
        typer.echo(f"[{i}/{top_n}] 🔬 Vollständige Analyse: {profile_name}")
        typer.echo("-" * 50)
        
        # Verwende Session-Timestamp und numeriere Profile durch
        profile_number = str(i).zfill(2)  # 01, 02, 03, etc.
        filename_suffix = f"{session_timestamp}_{profile_number}_{profile_name}_top{top_n}"
        
        # Verwende Benutzer-Fokus wenn angegeben, sonst Profil-Beschreibung als Fallback
        effective_focus = focus.strip() if focus.strip() else p["description"]
        
        cmd = [
            sys.executable, "-m", "apps.cli.main", "multiplex-scan",
            name, first_name,
            "-d", birth_date,
            "-p", birth_place,
            "--profile", profile_name,
            "--export", export_path,
            "--k-total", str(k_total),
            "--top-k", str(top_k),
            "--hardware-profile", hardware_profile,
            "--filename-suffix", filename_suffix,
            "--focus", effective_focus,
            "--scan-type", f"top{top_n}_session",  # Label für SESSION-Ordner
            "--session-id", session_timestamp,  # Session-ID für Gruppierung
        ]
        
        # Synergy-Parameter hinzufügen
        if synergy:
            cmd.extend([
                "--synergy",
                "--synergy-combos", str(synergy_combos),
                "--synergy-threshold", str(synergy_threshold),
            ])
        
        try:
            # Setze Encoding-Umgebungsvariablen für den Subprocess
            import os
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
            
            output = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""
            full_output = output + stderr
            lines = full_output.strip().split("\n")
            
            # Zeige wichtige Zeilen
            for line in lines:
                if any(x in line for x in ["Top Items", "Export gespeichert", "HTML-Report", "HTML geschrieben"]):
                    typer.echo(f"  {line}")
            
            # Prüfe Erfolg anhand des Outputs (mehrere Indikatoren)
            export_success = any(
                "Export gespeichert" in line or 
                "HTML geschrieben: OK" in line or
                "HTML-Report gespeichert" in line or
                "_multiplex_scan.html" in line
                for line in lines
            )
            
            if export_success:
                results.append({"profile": profile_name, "status": "OK"})
                typer.echo(f"  ✅ Profil {profile_name} abgeschlossen")
            else:
                results.append({"profile": profile_name, "status": "FEHLER"})
                typer.echo(f"  ❌ Profil {profile_name} fehlgeschlagen")
                # Debug: Zeige letzte Zeilen bei Fehler
                if len(lines) > 0:
                    typer.echo(f"  [Debug] Letzte Zeile: {lines[-1][:100]}")
        
        except Exception as exc:
            results.append({"profile": profile_name, "status": "EXCEPTION", "error": str(exc)})
            typer.echo(f"  ❌ Ausnahme bei Profil {profile_name}: {exc}")
        
        typer.echo("")
    
    # Zusammenfassung
    typer.echo("=" * 70)
    typer.echo(f"TOP-{top_n} ANALYSE ZUSAMMENFASSUNG")
    typer.echo("=" * 70)
    typer.echo(f"Klient: {first_name} {name}")
    if focus:
        typer.echo(f"Fokus: {focus}")
    typer.echo(f"Analysierte Profile ({top_n}):")
    for i, p in enumerate(top_profiles, 1):
        status = next((r["status"] for r in results if r["profile"] == p["profile"]), "?")
        status_icon = "✅" if status == "OK" else "❌"
        bonus_str = f" [+{p.get('focus_bonus', 0)*100:.0f}%]" if p.get('focus_bonus', 0) > 0 else ""
        typer.echo(f"  {i}. {status_icon} {p['profile']} (Score: {p['final_score']:.4f}){bonus_str}")
    typer.echo("")
    typer.echo("Die HTML-Berichte wurden im Benutzer_Archive_Start Ordner gespeichert.")
    
    # === KONSOLIDIERTE BERICHTE ERSTELLEN ===
    try:
        from tools.synergy_consolidator import consolidate_synergies
        from tools.remedy_reporter import consolidate_remedy_synergies
        
        typer.echo("")
        typer.echo("=" * 70)
        typer.echo("ERSTELLE KONSOLIDIERTE BERICHTE...")
        typer.echo("=" * 70)
        
        # Finde alle JSON-Dateien des Top-N Scans
        import glob
        scan_pattern = str(base_dir / f"{timestamp_str}_top{top_n}" / "*_multiplex_scan.json")
        json_files = glob.glob(scan_pattern)
        
        if json_files:
            typer.echo(f"✓ {len(json_files)} JSON-Dateien gefunden")
            
            # 1. SYNERGY-REPORT (existiert bereits)
            typer.echo("  → Erstelle Quantum-Synergy Report...")
            synergy_success = consolidate_synergies(json_files, base_dir)
            if synergy_success:
                typer.echo("  ✅ Quantum-Synergy Report erstellt")
            else:
                typer.echo("  ⚠ Quantum-Synergy Report konnte nicht erstellt werden")
            
            # 2. REMEDY-REPORT (NEU!)
            typer.echo("  → Erstelle Remedy-Kombinationen Report...")
            remedy_success = consolidate_remedy_synergies(json_files, base_dir)
            if remedy_success:
                typer.echo("  ✅ Remedy-Kombinationen Report erstellt")
            else:
                typer.echo("  ⚠ Remedy-Kombinationen Report konnte nicht erstellt werden")
        else:
            typer.echo(f"⚠ Keine JSON-Dateien gefunden unter: {scan_pattern}")
    
    except ImportError as e:
        typer.echo(f"⚠ Konsolidierungs-Module nicht verfügbar: {e}")
    except Exception as e:
        typer.echo(f"⚠ Fehler beim Erstellen der konsolidierten Berichte: {e}")
    
    typer.echo("=" * 70)


def get_remedy_description(remedy_name: str, indication: str) -> str:
    """
    Gibt erweiterte Beschreibung für ein Remedy zurück.
    
    Args:
        remedy_name: Name des Remedies (z.B. "Arnica C200")
        indication: Kurze Indikation (z.B. "Trauma")
    
    Returns:
        Erweiterte Beschreibung oder leerer String
    """
    # Remedy-Beschreibungen (energetisch/unterstützend formuliert)
    remedy_descriptions = {
        'arnica': 'Kann als energetische Unterstützung bei Verletzungen, Prellungen und Schock gesehen werden.',
        'symphytum': 'Wird im Rahmen der Bioresonanz als Hinweis auf Knochenregeneration interpretiert.',
        'calendula': 'Kann als energetische Unterstützung bei Wundheilung und Geweberegeneration gesehen werden.',
        'oscillococcinum': 'Wird im Rahmen der Bioresonanz als Hinweis auf virale Belastungen interpretiert.',
        'influenzinum': 'Kann als energetische Unterstützung bei grippalen Infekten gesehen werden.',
        'engystol': 'Wird im Rahmen der Bioresonanz als Hinweis auf Immunmodulation interpretiert.',
        'echinacea': 'Kann als energetische Unterstützung bei Immunsystem-Aktivierung gesehen werden.',
        'lymphomyosot': 'Wird im Rahmen der Bioresonanz als Hinweis auf lymphatische Entlastung interpretiert.',
        'nux vomica': 'Kann als energetische Unterstützung bei Entgiftung und Stoffwechsel gesehen werden.',
        'carbo vegetabilis': 'Wird im Rahmen der Bioresonanz als Hinweis auf Erschöpfung interpretiert.',
        'rescue': 'Kann als energetische Unterstützung in Stress-Situationen gesehen werden.',
    }
    
    # Suche nach Schlüsselwort im Remedy-Namen
    remedy_lower = remedy_name.lower()
    for key, desc in remedy_descriptions.items():
        if key in remedy_lower:
            return desc
    
    return ""


@app.command("bat-area-scan")
def bat_area_scan(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09041966"),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    top_areas: int = typer.Option(2, "--top-areas", help="Anzahl der Top-Bereiche für Detail-Scan"),
    intention: str = typer.Option("", "--intention", "-I", help="Aktive Intention (healing, clearing, etc.)"),
) -> None:
    """Zweistufiger BAT-Scan: Erst Bereiche scannen, dann Top-Bereiche mit Remedies analysieren.
    
    Schritt 1: Scannt alle 82 BAT-Bereiche (Überschriften)
    Schritt 2: Führt Detail-Scan der Top-N Bereiche mit Remedies durch
    
    Beispiel:
        python -m apps.cli.main bat-area-scan "Mustermann" "Max" -d 01011990 -p Berlin --top-areas 3
    """
    import subprocess
    import sys
    from pathlib import Path
    from core.bat_report_aggregator import beautify_bat_group_name
    
    typer.echo("=" * 70)
    typer.echo("BAT-BEREICHS-SCAN (Zweistufig)")
    typer.echo("=" * 70)
    typer.echo(f"Klient: {first_name} {name}")
    typer.echo(f"Top-Bereiche für Detail-Scan: {top_areas}")
    typer.echo("")
    
    # === SCHRITT 1: Alle BAT-Bereiche laden ===
    typer.echo("[1/3] 📊 Lade BAT-Bereiche...")
    
    bat_dir = Path("data/generated_groups/BAT_Akutprogramme")
    if not bat_dir.exists():
        typer.echo("❌ BAT-Verzeichnis nicht gefunden!")
        raise typer.Exit(1)
    
    bat_groups = []
    for json_file in sorted(bat_dir.glob("*.json")):
        group_name = f"bat_{json_file.stem.lower()}"
        bat_groups.append(group_name)
    
    typer.echo(f"[1/3] ✓ {len(bat_groups)} BAT-Bereiche gefunden")
    
    # === SCHRITT 2: Bereichs-Resonanzen berechnen ===
    typer.echo("[2/3] 🔬 Berechne Bereichs-Resonanzen...")
    
    # Nutze existierende Imports und Services (wie in multiplex_scan)
    from core.subgroups.procedural_groups import generate_candidates_for_group
    from providers.hardware.entropy_sources import select_entropy_source
    
    personal_profile = {"emotion": 0.5, "physisch": 0.5, "mental": 0.5, "astral": 0.5}
    
    # Entropie sammeln
    src = select_entropy_source(preferred=["cpu_timer"])
    h_level = max(0.0, min(1.0, src.sample_h_level(duration_s=2.0)))
    
    # Client-Profil erstellen (wie in multiplex_scan)
    profile_obj = ClientProfile(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        image_signature=None,
        personal_profile=personal_profile,
        planet_type=None,
    )
    
    # AnalysisService für Resonanz-Berechnung (wie in multiplex_scan)
    analysis = AnalysisService(rate_database={}, h_level=h_level)
    client_rates = analysis.encode_profile(profile_obj)
    client_entropy = analysis.resonator.holographic_entropy(client_rates)
    
    encoder = RateEncoder()
    client_personal_vector = encoder.personal_profile_to_vector(personal_profile)
    
    def resonance_fn(a: np.ndarray, b: np.ndarray) -> float:
        return float(analysis.resonator.resonance_score(a, b))
    
    # Für jeden BAT-Bereich: Durchschnittliche Resonanz berechnen
    seed = f"{name}{first_name}{birth_date}{birth_place}"
    area_scores = []
    for group_name in bat_groups:
        try:
            items = generate_candidates_for_group(group_name, seed, k=10)  # Nur 10 Items pro Bereich
            if not items:
                continue
            
            nls_service = NlsService(items)
            scores = nls_service.compute_scores_v2(
                client_rates,
                client_entropy,
                resonance_fn,
            )
            
            if scores:
                avg_score = sum(s.get("score", 0) for s in scores) / len(scores)
                max_score = max(s.get("score", 0) for s in scores)
                area_scores.append({
                    "group": group_name,
                    "name": beautify_bat_group_name(group_name),
                    "avg_score": avg_score,
                    "max_score": max_score,
                    "item_count": len(items),
                })
        except Exception:
            continue
    
    # Sortieren nach Durchschnitts-Score
    area_scores.sort(key=lambda x: x["avg_score"], reverse=True)
    
    typer.echo(f"[2/3] ✓ {len(area_scores)} Bereiche analysiert")
    typer.echo("")
    
    # Top-Bereiche anzeigen
    typer.echo("=" * 70)
    typer.echo("TOP BAT-BEREICHE (nach Resonanzstärke)")
    typer.echo("=" * 70)
    
    for i, area in enumerate(area_scores[:10], 1):
        marker = "→" if i <= top_areas else " "
        typer.echo(f"  {marker} #{i:2d} {area['name']}: Ø {area['avg_score']:.4f} (max: {area['max_score']:.4f})")
    
    typer.echo("")
    
    # === SCHRITT 3: Detail-Scan der Top-Bereiche ===
    typer.echo(f"[3/3] 🔍 Detail-Scan der Top-{top_areas} Bereiche mit Remedies...")
    typer.echo("")
    
    # Remedy-Empfehlungen basierend auf Bereich
    from core.bat_report_aggregator import find_remedies_for_group
    from services.description_service import get_descriptions_batch
    
    top_groups = [a["group"] for a in area_scores[:top_areas]]
    
    for i, group_name in enumerate(top_groups, 1):
        area_info = next((a for a in area_scores if a["group"] == group_name), None)
        typer.echo(f"--- Detail-Scan #{i}: {area_info['name'] if area_info else group_name} ---")
        
        # Berechne vollständigen Scan für diese Gruppe
        try:
            items = generate_candidates_for_group(group_name, seed, k=64)
            if items:
                nls_service = NlsService(items)
                detail_scores = nls_service.compute_scores_v2(
                    client_rates,
                    client_entropy,
                    resonance_fn,
                    client_personal_vector=client_personal_vector,
                )
                
                # Sortiere und zeige Top-5
                detail_scores.sort(key=lambda x: x.get("score", 0), reverse=True)
                
                # Berechne Kohärenz für jeden Score
                import math as _math
                for score_entry in detail_scores:
                    factors = []
                    for key in ["quantum_component", "numerical_factor", "geometric_factor", "intention_factor"]:
                        val = score_entry.get(key)
                        if val is not None and isinstance(val, (int, float)):
                            factors.append(float(val))
                    
                    if len(factors) >= 2:
                        mean_f = sum(factors) / len(factors)
                        variance_f = sum((x - mean_f) ** 2 for x in factors) / len(factors)
                        std_dev_f = _math.sqrt(max(variance_f, 0.0))
                        coherence = 1.0 / (1.0 + std_dev_f)
                        score_entry["coherence"] = max(0.0, min(1.0, coherence))
                    else:
                        score_entry["coherence"] = 1.0
                
                # Hole Beschreibungen für Top-Items
                top_labels = [sc.get("label", "") for sc in detail_scores[:5]]
                descriptions = get_descriptions_batch(top_labels)
                
                typer.echo(f"    Top Items ({len(detail_scores)} analysiert):")
                for j, sc in enumerate(detail_scores[:5], 1):
                    label = sc.get("label", "?")
                    score = sc.get("score", 0)
                    coherence = sc.get("coherence", 0.0)
                    
                    # Kohärenz-Symbol
                    if coherence >= 0.8:
                        coh_symbol = "⚡⚡⚡"
                    elif coherence >= 0.6:
                        coh_symbol = "⚡⚡"
                    elif coherence >= 0.4:
                        coh_symbol = "⚡"
                    else:
                        coh_symbol = "⚠️"
                    
                    typer.echo(f"      #{j} {label}: score={score:.4f} | Kohärenz: {coherence:.2f} {coh_symbol}")
                    
                    # Zeige Beschreibung falls vorhanden
                    if label in descriptions and descriptions[label]:
                        desc = descriptions[label]
                        # Kürze auf 100 Zeichen für kompakte Anzeige
                        desc_short = desc[:100] + "..." if len(desc) > 100 else desc
                        typer.echo(f"          ℹ️  {desc_short}")
                
                # Remedy-Empfehlungen mit erweiterten Beschreibungen
                try:
                    remedies = find_remedies_for_group(group_name)
                    if remedies:
                        typer.echo(f"    Empfohlene Remedies:")
                        for rem_name, rem_indication in remedies[:3]:
                            typer.echo(f"      💊 {rem_name}")
                            typer.echo(f"         Indikation: {rem_indication}")
                            
                            # Erweiterte Beschreibung basierend auf Remedy-Typ
                            extended_desc = get_remedy_description(rem_name, rem_indication)
                            if extended_desc:
                                typer.echo(f"         {extended_desc}")
                except Exception:
                    pass
                
                typer.echo(f"  ✅ Detail-Scan abgeschlossen")
            else:
                typer.echo(f"  ⚠️ Keine Items für Gruppe gefunden")
        
        except Exception as exc:
            typer.echo(f"  ❌ Fehler: {exc}")
        
        typer.echo("")
    
    # Zusammenfassung
    typer.echo("=" * 70)
    typer.echo("BAT-BEREICHS-SCAN ABGESCHLOSSEN")
    typer.echo("=" * 70)
    typer.echo(f"Analysierte Bereiche: {len(area_scores)}")
    typer.echo(f"Detail-Scans durchgeführt: {len(top_groups)}")
    typer.echo("")
    typer.echo("Top-Bereiche:")
    for i, area in enumerate(area_scores[:top_areas], 1):
        typer.echo(f"  #{i} {area['name']}")
    typer.echo("=" * 70)


@app.command("harmonize")
def harmonize(
    frequency: float = typer.Argument(..., help="Ziel-Frequenz in Hz (z.B. 432.0)"),
    duration: int = typer.Argument(..., help="Dauer in Minuten"),
    intention: str = typer.Option("harmonization", "--intention", "-i", help="Intention (healing, clearing, protection, etc.)"),
    use_cpu: bool = typer.Option(True, "--cpu/--no-cpu", help="CPU-Timing-Modulation verwenden"),
    use_gpu: bool = typer.Option(False, "--gpu/--no-gpu", help="GPU-Modulation verwenden"),
    use_ram: bool = typer.Option(False, "--ram/--no-ram", help="RAM Access Pattern Modulation verwenden"),
    use_websocket: bool = typer.Option(False, "--websocket/--no-websocket", help="WebSocket-Übertragung verwenden"),
) -> None:
    """Startet eine Harmonisierung als Background-Job.
    
    Die Harmonisierung läuft im Hintergrund weiter, auch wenn die PowerShell geschlossen wird.
    
    Beispiele:
        python -m apps.cli.main harmonize 432.0 30 -i healing
        python -m apps.cli.main harmonize 528.0 60 -i clearing --gpu --ram
        python -m apps.cli.main harmonize 963.0 120 -i protection --cpu --gpu --ram --websocket
    """
    import sys
    import io
    
    # Erzwinge UTF-8 Encoding für stdout/stderr
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    from services.harmonization_worker import start_harmonization_job
    
    typer.echo("=" * 70)
    typer.echo("HARMONISIERUNG STARTEN")
    typer.echo("=" * 70)
    typer.echo(f"Frequenz: {frequency} Hz")
    typer.echo(f"Dauer: {duration} Minuten")
    typer.echo(f"Intention: {intention}")
    typer.echo("")
    
    # Hardware-Konfiguration
    hardware_config = {
        "use_cpu": use_cpu,
        "use_gpu": use_gpu,
        "use_ram": use_ram,
        "use_websocket": use_websocket,
        "use_quartz": False
    }
    
    active_hw = [k.replace("use_", "").upper() for k, v in hardware_config.items() if v]
    typer.echo(f"Hardware: {', '.join(active_hw) if active_hw else 'Keine'}")
    typer.echo("")
    
    # Starte Job
    try:
        job_id = start_harmonization_job(
            target_frequency=frequency,
            duration_minutes=duration,
            intention=intention,
            hardware_config=hardware_config
        )
        
        typer.echo(f"✅ Harmonisierung gestartet!")
        typer.echo(f"   Job-ID: {job_id}")
        typer.echo("")
        typer.echo("Der Job läuft jetzt im Hintergrund.")
        typer.echo("Status prüfen mit:")
        typer.echo(f"  python -m apps.cli.main harmonize-status {job_id}")
        typer.echo("")
        typer.echo("Alle Jobs anzeigen:")
        typer.echo(f"  python -m apps.cli.main harmonize-status")
        typer.echo("=" * 70)
    
    except Exception as e:
        typer.echo(f"❌ Fehler beim Starten: {e}", err=True)
        raise typer.Exit(1)


@app.command("harmonize-status")
def harmonize_status(
    job_id: Optional[str] = typer.Argument(None, help="Job-ID (optional, zeigt alle Jobs wenn leer)"),
    active_only: bool = typer.Option(False, "--active", "-a", help="Nur aktive Jobs anzeigen"),
) -> None:
    """Zeigt den Status von Harmonisierungs-Jobs.
    
    Beispiele:
        python -m apps.cli.main harmonize-status
        python -m apps.cli.main harmonize-status harm_abc123
        python -m apps.cli.main harmonize-status --active
    """
    import sys
    import io
    
    # Erzwinge UTF-8 Encoding für stdout/stderr
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    from services.harmonization_worker import (
        HarmonizationJob,
        list_all_jobs,
        get_active_jobs,
        format_job_status
    )
    
    typer.echo("=" * 70)
    typer.echo("HARMONISIERUNGS-STATUS")
    typer.echo("=" * 70)
    
    # Einzelner Job
    if job_id:
        job = HarmonizationJob.load(job_id)
        
        if not job:
            typer.echo(f"❌ Job '{job_id}' nicht gefunden", err=True)
            raise typer.Exit(1)
        
        typer.echo(format_job_status(job))
        typer.echo("=" * 70)
        return
    
    # Alle Jobs oder nur aktive
    jobs = get_active_jobs() if active_only else list_all_jobs()
    
    if not jobs:
        typer.echo("\nKeine Jobs gefunden.")
        typer.echo("=" * 70)
        return
    
    typer.echo(f"\nGefundene Jobs: {len(jobs)}")
    
    for job in jobs:
        typer.echo(format_job_status(job))
    
    typer.echo("\n" + "=" * 70)


@app.command("harmonize-stop")
def harmonize_stop(
    job_id: str = typer.Argument(..., help="Job-ID des zu stoppenden Jobs"),
) -> None:
    """Stoppt einen laufenden Harmonisierungs-Job.
    
    Beispiel:
        python -m apps.cli.main harmonize-stop harm_abc123
    """
    import sys
    import io
    
    # Erzwinge UTF-8 Encoding für stdout/stderr
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    from services.harmonization_worker import stop_harmonization_job, HarmonizationJob
    
    typer.echo("=" * 70)
    typer.echo("HARMONISIERUNG STOPPEN")
    typer.echo("=" * 70)
    typer.echo(f"Job-ID: {job_id}")
    typer.echo("")
    
    # Prüfe ob Job existiert
    job = HarmonizationJob.load(job_id)
    
    if not job:
        typer.echo(f"❌ Job '{job_id}' nicht gefunden", err=True)
        raise typer.Exit(1)
    
    if job.status != "running":
        typer.echo(f"⚠️  Job ist nicht aktiv (Status: {job.status})")
        typer.echo("=" * 70)
        return
    
    # Stoppe Job
    try:
        success = stop_harmonization_job(job_id)
        
        if success:
            typer.echo(f"✅ Job gestoppt")
            typer.echo("")
            typer.echo("HINWEIS: Der Worker-Prozess läuft möglicherweise noch kurz weiter,")
            typer.echo("da er den Status erst beim nächsten Zyklus prüft.")
        else:
            typer.echo(f"❌ Job konnte nicht gestoppt werden", err=True)
    
    except Exception as e:
        typer.echo(f"❌ Fehler beim Stoppen: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo("=" * 70)


@app.command("descriptions-sync")
def descriptions_sync() -> None:
    """Synchronisiert alle Gruppen mit der Beschreibungs-Datenbank."""
    from services.description_service import get_sync_status, update_sync_timestamp
    from core.subgroups.procedural_groups import list_groups
    
    typer.echo("=" * 70)
    typer.echo("BESCHREIBUNGS-DATENBANK SYNCHRONISIEREN")
    typer.echo("=" * 70)
    typer.echo("")
    
    try:
        # Hole alle verfügbaren Gruppen
        all_groups = list_groups()
        typer.echo(f"📊 Verfügbare Gruppen: {len(all_groups)}")
        
        # Hole Sync-Status
        status = get_sync_status()
        typer.echo(f"📅 Letzte Synchronisation: {status.get('last_sync', 'Nie')}")
        typer.echo(f"📝 Beschreibungen in DB: {status.get('total_descriptions', 0)}")
        typer.echo("")
        
        # Aktualisiere Timestamp
        update_sync_timestamp()
        typer.echo("✅ Synchronisation abgeschlossen")
        
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo("=" * 70)


@app.command("descriptions-status")
def descriptions_status(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Zeigt detaillierte Statistiken pro Gruppe")
) -> None:
    """Zeigt den Status der Beschreibungs-Datenbank."""
    from services.description_service import get_sync_status, get_group_stats, get_db_path
    
    typer.echo("=" * 70)
    typer.echo("BESCHREIBUNGS-DATENBANK STATUS")
    typer.echo("=" * 70)
    typer.echo("")
    
    try:
        # Allgemeiner Status
        status = get_sync_status()
        db_path = get_db_path()
        
        typer.echo(f"📁 Datenbank: {db_path}")
        typer.echo(f"📅 Letzte Sync: {status.get('last_sync', 'Nie')}")
        typer.echo(f"📝 Gesamt Beschreibungen: {status.get('total_descriptions', 0)}")
        typer.echo(f"🏷️  Gruppen mit Beschreibungen: {status.get('groups_with_descriptions', 0)}")
        typer.echo("")
        
        # Detaillierte Statistiken
        if detailed:
            typer.echo("GRUPPEN-STATISTIKEN:")
            typer.echo("-" * 70)
            
            group_stats = get_group_stats()
            
            if not group_stats:
                typer.echo("  Keine Gruppen-Statistiken verfügbar")
            else:
                # Sortiere nach Anzahl Beschreibungen (with_desc)
                sorted_stats = sorted(
                    group_stats,
                    key=lambda x: x.get("with_desc", 0),
                    reverse=True
                )
                
                for stat in sorted_stats[:20]:  # Top 20
                    group_name = stat.get("group", "Unbekannt")
                    total = stat.get("total", 0)
                    with_desc = stat.get("with_desc", 0)
                    typer.echo(f"  {group_name:40} {with_desc:4}/{total:4} Beschreibungen")
                
                if len(sorted_stats) > 20:
                    typer.echo(f"\n  ... und {len(sorted_stats) - 20} weitere Gruppen")
        
    except Exception as e:
        typer.echo(f"❌ Fehler: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo("=" * 70)


@app.command("descriptions-generate")
def descriptions_generate(
    group: Optional[str] = typer.Option(None, "--group", "-g", help="Gruppe für die Beschreibungen generiert werden"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Kategorie (z.B. bakterien, viren, bachblueten)"),
    limit: int = typer.Option(0, "--limit", "-l", help="Maximale Anzahl Items (0 = alle)"),
    test: bool = typer.Option(False, "--test", "-t", help="Test-Modus mit 5 Items")
) -> None:
    """Generiert AI-Beschreibungen für Items mit Ollama."""
    
    typer.echo("=" * 70)
    typer.echo("BESCHREIBUNGEN GENERIEREN")
    typer.echo("=" * 70)
    typer.echo("")
    
    if test:
        typer.echo("🧪 TEST-MODUS: Generiere 5 Test-Beschreibungen")
        typer.echo("")
        typer.echo("⚠️  Bitte verwende: python tools/batch_descriptions.py --test")
        typer.echo("=" * 70)
        return
    
    if not group and not category:
        typer.echo("❌ Bitte --group oder --category angeben", err=True)
        typer.echo("")
        typer.echo("Beispiele:")
        typer.echo("  python -m apps.cli.main descriptions-generate --group bakterien")
        typer.echo("  python -m apps.cli.main descriptions-generate --category homoeopathie")
        typer.echo("")
        typer.echo("Verfügbare Kategorien:")
        typer.echo("  bat_akut, bakterien, viren, pilze, parasiten,")
        typer.echo("  homoeopathie, spagyrik, bachblueten, organe,")
        typer.echo("  chakra, meridiane, wirbelsaeule, schmerz, orthomolekular")
        typer.echo("=" * 70)
        raise typer.Exit(1)
    
    typer.echo("⚠️  Für die Generierung bitte verwenden:")
    typer.echo("")
    
    if group:
        cmd = f"python tools/batch_descriptions.py --group {group}"
        if limit > 0:
            cmd += f" --limit {limit}"
        typer.echo(f"  {cmd}")
    
    if category:
        typer.echo(f"  python tools/batch_descriptions.py --category {category}")
    
    typer.echo("")
    typer.echo("HINWEIS: Die Generierung läuft über das separate Script,")
    typer.echo("da es Ollama-Integration und längere Laufzeiten erfordert.")
    typer.echo("=" * 70)


@app.command("client-trends")
def client_trends(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    output: str = typer.Option("both", "--output", "-o", help="Ausgabeformat: text, html, both"),
    save: bool = typer.Option(True, "--save/--no-save", help="Speichere Bericht im Klienten-Ordner"),
) -> None:
    """Erstellt eine Trendanalyse über alle Scans eines Klienten im Benutzer_Archive_Start.
    
    Analysiert:
    - Wiederkehrende Resonanzen über mehrere Scans
    - Zeitliche Entwicklung (steigend/fallend/stabil)
    - Gruppen-Trends
    - Scan-Historie
    
    Beispiel:
        python -m apps.cli.main client-trends "Mustermann" "Max"
    """
    import subprocess
    import sys
    
    typer.echo("=" * 70)
    typer.echo("KLIENTEN-TRENDANALYSE")
    typer.echo("=" * 70)
    typer.echo(f"Klient: {first_name} {name}")
    typer.echo("")
    
    # Rufe das Trend-Analyzer-Script auf
    cmd = [
        sys.executable,
        "tools/trend_analyzer.py",
        name,
        first_name,
        "--output", output,
    ]
    
    if save:
        cmd.append("--save")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        
        if result.returncode != 0:
            typer.echo(f"\n❌ Trendanalyse fehlgeschlagen (Code: {result.returncode})")
            raise typer.Exit(code=1)
    
    except FileNotFoundError:
        typer.echo("❌ trend_analyzer.py nicht gefunden!")
        raise typer.Exit(code=1)
    except Exception as exc:
        typer.echo(f"❌ Fehler: {exc}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
