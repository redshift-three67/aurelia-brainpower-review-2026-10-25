"""Synergy Helpers - Helper Functions for Remedy Synergy Analysis"""

from typing import List, Dict
import numpy as np


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

            try:
                r1 = np.array([float(x) for x in rates1[:2]])
                r2 = np.array([float(x) for x in rates2[:2]])
                if r1.shape[0] == 0 or r2.shape[0] == 0:
                    continue

                distance = np.linalg.norm(r1 - r2)

                synergy_score = max(0.0, 10.0 - distance / 10.0)

                if synergy_score <= 5.0:
                    continue

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

        copen_rate = item.get("copen_rate")

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
        if copen_rate is not None:
            result_item["copen_rate"] = copen_rate
        results.append(result_item)

    if not results:
        return []

    results.sort(key=lambda x: x.get("_max_partner_synergy", 0.0), reverse=True)
    trimmed = results[:max_results]
    for r in trimmed:
        r.pop("_max_partner_synergy", None)
    return trimmed
