"""Database helper functions for CLI command exports."""

from __future__ import annotations

from typing import Dict, List


def _compute_db_client_rate_value(name: str, first_name: str, birth_date: str, birth_place: str) -> int:
    raw = f"{first_name}{name}{birth_date}{birth_place}"
    raw_norm = "".join(str(raw).split()).upper()
    filtered = [ch for ch in raw_norm if "A" <= ch <= "Z" or ch.isdigit()]
    if not filtered:
        return 0

    total = 0
    for idx, ch in enumerate(filtered):
        value = ord(ch) - 64 if "A" <= ch <= "Z" else ord(ch) - ord("0")
        total += value * (idx + 1)
    return max(0, int(((total * 1000) / 21.0) * 34.0))


def _build_db_client_rate_block(client_info: Dict[str, str]) -> Dict[str, object]:
    value = _compute_db_client_rate_value(
        str(client_info.get("name", "") or ""),
        str(client_info.get("first_name", "") or ""),
        str(client_info.get("birth_date", "") or ""),
        str(client_info.get("birth_place", "") or ""),
    )
    return {"value": float(value), "source": "calculated" if value else "empty"}


def _compute_db_resonance_score(client_rate_value: float, item_rate: float) -> float:
    if client_rate_value <= 0.0 or item_rate <= 0.0:
        return 0.0
    delta_rel = abs(item_rate - client_rate_value) / client_rate_value
    if delta_rel >= 1.0:
        return 0.0
    return max(0.0, min(100.0, 100.0 * (1.0 - delta_rel)))


def _build_db_items_from_sub_results(
    sub_results_top: List[Dict[str, object]],
    max_items: int,
    client_rate_value: float | None,
) -> List[Dict[str, object]]:
    items: List[Dict[str, object]] = []
    if max_items <= 0:
        return items

    for entry in sub_results_top[:max_items]:
        label = str(entry.get("label", "") or "").strip()
        if not label:
            continue

        item: Dict[str, object] = {
            "label": label,
            "group": str(entry.get("group", "") or "").strip(),
        }
        potency = str(entry.get("potency", "") or "").strip()
        if potency:
            item["potency"] = potency

        rate_raw = entry.get("copen_rate")
        try:
            rate = float(rate_raw) if rate_raw is not None else None
        except Exception:
            rate = None
        if rate is not None:
            item["rate"] = rate
            item["rate_formatted"] = f"{int(rate):,}".replace(",", ".")
            if client_rate_value is not None:
                score = _compute_db_resonance_score(float(client_rate_value), rate)
                if score > 0.0:
                    item["resonance_score"] = score
        items.append(item)
    return items


def _build_db_analysis_summary(items: List[Dict[str, object]], top_n: int = 5) -> Dict[str, object]:
    values: List[float] = []
    for item in items:
        try:
            raw = item.get("resonance_score")
            if raw is not None:
                values.append(float(raw))
        except Exception:
            continue

    ranked = []
    for item in items:
        try:
            score = item.get("resonance_score")
            if score is None:
                continue
            ranked.append(
                {
                    "label": str(item.get("label", "") or ""),
                    "group": str(item.get("group", "") or ""),
                    "resonance_score": float(score),
                }
            )
        except Exception:
            continue
    ranked.sort(key=lambda entry: entry["resonance_score"], reverse=True)

    return {
        "items_total": len(items),
        "resonance_count": len(values),
        "resonance_max": max(values) if values else None,
        "resonance_min": min(values) if values else None,
        "resonance_mean": (sum(values) / len(values)) if values else None,
        "top_resonance": ranked[:top_n] if top_n > 0 else ranked,
    }


def _summarize_axis_items(items: List[Dict[str, object]], top_n: int = 5) -> Dict[str, object]:
    scores: List[float] = []
    for item in items:
        try:
            raw = item.get("score")
            if raw is not None:
                scores.append(float(raw))
        except Exception:
            continue

    ranked = list(items)
    ranked.sort(key=lambda item: float(item.get("score", 0.0) or 0.0), reverse=True)
    top = []
    for item in ranked[:top_n] if top_n > 0 else ranked:
        entry: Dict[str, object] = {
            "label": str(item.get("label", "") or ""),
            "group": str(item.get("group", "") or ""),
        }
        if item.get("score") is not None:
            entry["score"] = float(item.get("score", 0.0) or 0.0)
        if item.get("level") not in (None, ""):
            entry["level"] = item.get("level")
        if item.get("copen_rate") is not None:
            entry["copen_rate"] = float(item.get("copen_rate", 0.0) or 0.0)
        top.append(entry)

    return {
        "items_total": len(items),
        "score_max": max(scores) if scores else None,
        "score_mean": (sum(scores) / len(scores)) if scores else None,
        "top": top,
    }


def _build_morphic_axes_from_sub_results(sub_results_top: List[Dict[str, object]]) -> Dict[str, object]:
    spine = []
    dental = []
    for item in sub_results_top:
        group = str(item.get("group", "") or "").strip().lower()
        if group.startswith("wirbelsaeule"):
            spine.append(item)
        if group.startswith("zahnorgane") or group == "odontone":
            dental.append(item)

    axes: Dict[str, object] = {"enabled": False, "engine": "morphic_axes_v1"}
    if spine:
        axes["spine"] = {"global": _summarize_axis_items(spine)}
    if dental:
        axes["dental"] = {"global": _summarize_axis_items(dental)}
    if spine or dental:
        axes["enabled"] = True
    return axes

