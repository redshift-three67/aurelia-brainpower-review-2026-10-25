from __future__ import annotations

from core.harmonization.sequence_planner import (
    plan_harmonization_from_scan_export,
    plan_harmonization_sequence,
)


def test_plan_harmonization_sequence_reproduces_historic_priority_deduplication_and_rounds() -> None:
    plan = plan_harmonization_sequence(
        [
            {"label": "Alpha", "score": 0.40, "priority": "mittel", "rates": [100.0]},
            {"label": "Alpha", "score": 0.90, "priority": "hoch", "rates": [200.0]},
            {"label": "Beta", "score": 0.60},
            {"label": "Gamma", "score": 0.10},
        ],
        pulse_seconds=21,
        pause_seconds=42,
        duration_factor=1,
    )

    assert [item["label"] for item in plan["items"]] == ["Alpha", "Beta"]
    assert [item["score"] for item in plan["items"]] == [0.90, 0.60]
    assert plan["rounds"] == 10
    assert plan["total_items"] == 20
    assert plan["planned_seconds"] == 1260
    assert plan["rejected_count"] == 1


def test_plan_harmonization_sequence_limits_to_twenty_items_and_keeps_at_least_one_round() -> None:
    items = [{"label": f"item-{index}", "score": 1 - index / 100, "priority": "hoch"} for index in range(25)]

    plan = plan_harmonization_sequence(items, pulse_seconds=700, pause_seconds=700, duration_factor=1)

    assert len(plan["items"]) == 20
    assert plan["rounds"] == 1
    assert plan["total_items"] == 20


def test_plan_harmonization_from_scan_export_collects_historic_sections_shape() -> None:
    plan = plan_harmonization_from_scan_export(
        {"sub_results": {"sections": [{"items": [{"label": "Section item", "score": 0.8}]}]}},
        pulse_seconds=3,
        pause_seconds=2,
        duration_factor=1,
    )

    assert [item["label"] for item in plan["items"]] == ["Section item"]
