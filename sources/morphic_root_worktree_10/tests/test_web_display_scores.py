import json
from pathlib import Path

from apps.web.reports import ReportCatalog


def test_display_score_helpers_round_visible_scores_and_preserve_raw_values() -> None:
    from apps.web.display_scores import (
        adaptive_result_limit,
        format_display_score,
        limit_display_items,
        normalize_display_payload,
    )

    raw_payload = {
        "score": 7.12349,
        "avg_score": 8.98765,
        "nested": {
            "max_score": 6.0004,
            "scores": [1.23456, 2, 3.9999],
        },
    }

    normalized = normalize_display_payload(raw_payload)

    assert format_display_score(7.12349) == "7.123"
    assert adaptive_result_limit(3, adaptive_limits=True) == 3
    assert adaptive_result_limit(5, adaptive_limits=True) == 5
    assert adaptive_result_limit(7, adaptive_limits=True) == 5
    assert adaptive_result_limit(9, adaptive_limits=True) == 5
    assert adaptive_result_limit(9, adaptive_limits=False) == 9
    assert limit_display_items(list(range(9)), top_n=9, adaptive_limits=True) == [
        0,
        1,
        2,
        3,
        4,
    ]
    assert normalized == {
        "score": "7.123",
        "avg_score": "8.988",
        "nested": {
            "max_score": "6.000",
            "scores": ["1.235", "2.000", "4.000"],
        },
    }
    assert raw_payload == {
        "score": 7.12349,
        "avg_score": 8.98765,
        "nested": {
            "max_score": 6.0004,
            "scores": [1.23456, 2, 3.9999],
        },
    }


def test_report_catalog_preview_rounds_json_score_fields_for_display(
    tmp_path: Path,
) -> None:
    report_root = tmp_path / "reports"
    client_dir = report_root / "Mustermann_Klaus_09041966_Augsburg"
    client_dir.mkdir(parents=True)
    json_file = client_dir / "20260115_101530_multiplex_scan.json"
    raw_payload = {
        "score": 7.12349,
        "avg_score": 8.98765,
        "items": [{"label": "Bronchien", "score": 4.44444}],
    }
    json_file.write_text(json.dumps(raw_payload), encoding="utf-8")

    catalog = ReportCatalog([report_root])
    report_id = catalog.list()["reports"][0]["id"]

    preview = catalog.preview(report_id)

    assert preview["mode"] == "text"
    assert '  "score": "7.123"' in preview["content"]
    assert '  "avg_score": "8.988"' in preview["content"]
    assert '      "score": "4.444"' in preview["content"]
    assert json.loads(json_file.read_text(encoding="utf-8")) == raw_payload
