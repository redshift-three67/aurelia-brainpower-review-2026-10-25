from __future__ import annotations

from math import floor
from typing import Any, Iterable


_PRIORITY_ORDER = {"hoch": 2, "mittel": 1}


def _priority_for(item: dict[str, Any]) -> str:
    priority = str(item.get("priority") or "").strip().lower()
    if priority in _PRIORITY_ORDER:
        return priority
    score = float(item.get("score") or 0.0)
    if score > 0.5:
        return "hoch"
    if score > 0.2:
        return "mittel"
    return "niedrig"


def plan_harmonization_sequence(
    raw_items: Iterable[dict[str, Any]],
    *,
    pulse_seconds: float,
    pause_seconds: float,
    duration_factor: int,
) -> dict[str, Any]:
    """Return the historic PowerShell impulse/pause plan without side effects."""
    if pulse_seconds <= 0 or pause_seconds <= 0 or duration_factor < 1:
        raise ValueError("pulse_seconds, pause_seconds and duration_factor must be positive")

    retained: dict[str, dict[str, Any]] = {}
    rejected_count = 0
    for raw in raw_items:
        label = str(raw.get("label") or "").strip()
        score = float(raw.get("score") or 0.0)
        priority = _priority_for(raw)
        if not label or priority not in _PRIORITY_ORDER:
            rejected_count += 1
            continue
        item = {"label": label, "score": score, "priority": priority, "rates": raw.get("rates")}
        current = retained.get(label)
        if current is None or score > float(current["score"]):
            retained[label] = item

    items = sorted(retained.values(), key=lambda item: float(item["score"]), reverse=True)[:20]
    seconds_per_item = pulse_seconds + pause_seconds
    one_round_seconds = len(items) * seconds_per_item
    max_seconds = duration_factor * 21 * 60
    rounds = max(1, floor(max_seconds / one_round_seconds)) if one_round_seconds else 0
    total_items = len(items) * rounds
    return {
        "items": items,
        "rounds": rounds,
        "total_items": total_items,
        "planned_seconds": total_items * seconds_per_item,
        "rejected_count": rejected_count,
    }


def plan_harmonization_from_scan_export(
    export_data: dict[str, Any],
    *,
    pulse_seconds: float,
    pause_seconds: float,
    duration_factor: int,
) -> dict[str, Any]:
    """Extract the historic export item shapes, then build a side-effect-free plan."""
    sub_results = export_data.get("sub_results") or {}
    items: list[dict[str, Any]] = []
    if isinstance(sub_results, dict) and isinstance(sub_results.get("sections"), list):
        for section in sub_results["sections"]:
            if isinstance(section, dict) and isinstance(section.get("items"), list):
                items.extend(item for item in section["items"] if isinstance(item, dict))
    elif isinstance(sub_results, dict) and isinstance(sub_results.get("top"), list):
        items = [item for item in sub_results["top"] if isinstance(item, dict)]
    elif isinstance(export_data.get("nls_scores"), list):
        items = [item for item in export_data["nls_scores"] if isinstance(item, dict)]
    elif isinstance(export_data.get("bat_subgroups"), list):
        for section in export_data["bat_subgroups"]:
            if isinstance(section, dict) and isinstance(section.get("items"), list):
                items.extend(item for item in section["items"] if isinstance(item, dict))
    return plan_harmonization_sequence(
        items,
        pulse_seconds=pulse_seconds,
        pause_seconds=pause_seconds,
        duration_factor=duration_factor,
    )
