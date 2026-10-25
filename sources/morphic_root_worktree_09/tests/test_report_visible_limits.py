from __future__ import annotations

from pathlib import Path

from apps.cli.commands.helpers.harmonization_helpers import (
    _normalize_scores,
    _render_basic_html,
)
from tools.remedy_reporter import _render_remedy_pair_table, _render_remedy_summary
from tools.synergy_consolidator import (
    _render_cross_profile,
    _render_profile_details,
    _render_top_synergies,
)
from tools.trend_analyzer import _render_trend_table


def _make_top_item(index: int, group: str = "immune") -> dict[str, object]:
    return {
        "label": f"Item {index:02d}",
        "group": group,
        "score": 10.0 - (index * 0.1),
        "rates": [index + 100.0],
        "description": f"Beschreibung {index:02d}",
    }


def test_harmonization_html_keeps_large_group_scrollable() -> None:
    top_items = [_make_top_item(index) for index in range(1, 26)]

    html = _render_basic_html(
        {
            "client": {"first_name": "Max", "name": "Mustermann"},
            "analysis": {"rates": [1.0], "heim_signature": [2.0]},
            "sub_results": {"top": top_items, "groups": ["immune"]},
            "remedy_synergies": [
                {
                    "item1": f"Remedy {index:02d}",
                    "item2": "Partner",
                    "synergy_score": 6.0,
                }
                for index in range(1, 35)
            ],
        }
    )

    assert "data-visible-limit='21'" in html
    assert "Item 25" in html
    assert "Remedy 34" in html


def test_normalize_scores_does_not_mutate_input_items() -> None:
    items = [{"label": "A", "score": 2.0}, {"label": "B", "score": 1.0}]
    original = [dict(item) for item in items]

    normalized = _normalize_scores(items)

    assert items == original
    assert normalized[0]["score"] != original[0]["score"]
    assert "_raw_score" not in items[0]


def test_remedy_table_uses_visible_limit_wrapper() -> None:
    remedies = [
        {
            "item1": f"Remedy {index:02d}",
            "item2": f"Partner {index:02d}",
            "profile": "Basis",
            "synergy_score": 6.5,
        }
        for index in range(1, 26)
    ]

    html = _render_remedy_pair_table(remedies, 3)

    assert 'data-visible-limit="21"' in html
    assert "Remedy 25" in html


def test_synergy_cross_profile_keeps_all_rows_scrollable() -> None:
    cross_profile = [
        {
            "item": f"Shared Item {index:02d}",
            "groups": ["immune"],
            "profiles": ["A", "B"],
            "average_score": 5.0,
            "max_score": 7.0,
        }
        for index in range(1, 31)
    ]

    html = _render_cross_profile(cross_profile)

    assert 'data-visible-limit="21"' in html
    assert "Shared Item 30" in html


def test_trend_table_uses_visible_limit_wrapper() -> None:
    trends = [
        {
            "label": f"Trend {index:02d}",
            "group": "immune",
            "first_score": 1.0,
            "latest_score": 2.0,
            "delta": 1.0,
            "direction": "steigend",
        }
        for index in range(1, 26)
    ]

    html = _render_trend_table(trends, file_count=4)

    assert 'data-visible-limit="21"' in html
    assert "Trend 25" in html


def test_synergy_and_remedy_sections_use_workbench_report_classes() -> None:
    synergy_entry = {
        "profile": "Basis",
        "items": [
            {"label": "Bronchien", "group": "atmung"},
            {"label": "Mucosa compositum", "group": "remedy"},
        ],
        "score": 8.2,
        "components": {"resonance": 7.2},
    }
    remedy_summary = [
        {
            "remedy": "Mucosa compositum",
            "score": 7.0,
            "rates": [12.0],
            "synergies": [{"remedy": "Bronchien", "score": 6.5}],
            "synergy_score": 8.0,
        }
    ]

    html = (
        _render_profile_details(
            [{"profile": "Basis", "synergy_count": 1, "synergies": [synergy_entry]}]
        )
        + _render_top_synergies([synergy_entry])
        + _render_remedy_summary(remedy_summary, source_count=1, combination_count=1)
    )

    assert "card quantum" in html
    assert "class='description'" in html
    assert "class=\"card-meta\"" in html
    assert "#667eea" not in html
    assert "#764ba2" not in html
    assert "#6BA5D0" not in html
    assert "linear-gradient(135deg, rgba(102" not in html
