"""Fall-Statistik — 1:1-Port (utils/StatisticsGenerator.java).

Aggregiert RateObjectWrapper je Raten-Namen über alle Sessions eines Falls:
occurrence = Anzahl, overallGV = GV-Summe, overallEnergeticValue = EV-Summe.
Sortierung: occurrence → overallGV → overallEnergeticValue (je absteigend),
Gleichstand Name aufsteigend; Top 10 landen in case["topTenList"].
"""

from __future__ import annotations

from typing import Any


def case_statistics(case: dict[str, Any], limit: int = 11) -> list[dict[str, Any]]:
    """Original: start() — Sortier- und Grenzverhalten exakt (count <= 10)."""
    rates: dict[str, dict[str, int]] = {}
    for session in case.get("sessionList", []):
        result = session.get("analysisResult")
        if not result:
            continue
        for rate in result.get("rateObjects", []):
            name = rate.get("nameOrRate") or ""
            wrapper = rates.get(name)
            if wrapper is None:
                wrapper = rates[name] = {
                    "name": name,
                    "occurrence": 0,
                    "overallGV": 0,
                    "overallEnergeticValue": 0,
                }
            wrapper["occurrence"] += 1
            wrapper["overallGV"] += rate.get("gv") or 0
            wrapper["overallEnergeticValue"] += rate.get("energeticValue") or 0

    ordered = sorted(
        rates.values(),
        key=lambda w: (
            -w["occurrence"],
            -w["overallGV"],
            -w["overallEnergeticValue"],
            w["name"],
        ),
    )

    top_list: list[dict[str, Any]] = []
    count = 0
    for wrapper in ordered:
        top_list.append(wrapper)
        count += 1
        if count > 10:  # Original: if (++count <= 10) continue; break;
            break
    if limit is not None:
        top_list = top_list[:limit]
    case["topTenList"] = top_list
    return top_list
