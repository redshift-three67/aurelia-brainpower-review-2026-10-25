from __future__ import annotations

import json
from pathlib import Path

from core.trend_analysis import compare_two_scans, load_client_scans


def test_load_client_scans_reads_nested_topn_exports_with_current_schema(tmp_path: Path) -> None:
    scan_dir = (
        tmp_path
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260629_080000_TOP5_SESSION"
        / "01_atmung"
    )
    scan_dir.mkdir(parents=True)
    scan_path = scan_dir / "20260629_080001_atmung_multiplex_scan.json"
    scan_path.write_text(
        json.dumps(
            {
                "profile": "atmung",
                "focus": "Bronchien",
                "sub_results": {
                    "top": [
                        {"label": "Bronchien", "score": 8.2},
                        {"label": "Lunge", "score": 7.7},
                    ]
                },
            }
        ),
        encoding="utf-8",
    )

    snapshots = load_client_scans(str(tmp_path), "Mustermann*")

    assert len(snapshots) == 1
    assert snapshots[0].profile == "atmung"
    assert [item["label"] for item in snapshots[0].top_items] == ["Bronchien", "Lunge"]


def test_compare_two_scans_uses_current_scan_schema(tmp_path: Path) -> None:
    older = tmp_path / "20260628_080000_atmung_multiplex_scan.json"
    newer = tmp_path / "20260629_080000_atmung_multiplex_scan.json"
    older.write_text(
        json.dumps(
            {
                "sub_results": {
                    "top": [
                        {"label": "Bronchien", "score": 8.0},
                        {"label": "Lunge", "score": 7.0},
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    newer.write_text(
        json.dumps(
            {
                "top_scores": [
                    {"label": "Bronchien", "score": 6.0},
                    {"label": "Zwerchfell", "score": 7.5},
                ]
            }
        ),
        encoding="utf-8",
    )

    comparison = compare_two_scans(str(older), str(newer))

    assert comparison["new_items"] == ["Zwerchfell"]
    assert comparison["resolved_items"] == ["Lunge"]
    assert comparison["changed_items"][0]["label"] == "Bronchien"
