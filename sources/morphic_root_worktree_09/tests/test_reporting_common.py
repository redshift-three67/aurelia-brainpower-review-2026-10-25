import json
from pathlib import Path

from tools.reporting_common import (
    REPORT_THEME_ID,
    client_report_dir,
    render_legacy_html,
    report_json_dumps,
    round_scores_for_export,
)


def test_client_report_dir_matches_legacy_shape_without_tenant_id(tmp_path: Path) -> None:
    result = client_report_dir(
        tmp_path, "Mustermann", "Klaus", "Deutung", "09041966", "Augsburg"
    )

    assert result == tmp_path / "Deutung" / "Mustermann_Klaus_09041966_Augsburg"


def test_client_report_dir_isolates_by_tenant_id(tmp_path: Path) -> None:
    result_a = client_report_dir(
        tmp_path,
        "Mustermann",
        "Klaus",
        "Deutung",
        "09041966",
        "Augsburg",
        tenant_id="ws-tenant-a",
    )
    result_b = client_report_dir(
        tmp_path,
        "Mustermann",
        "Klaus",
        "Deutung",
        "09041966",
        "Augsburg",
        tenant_id="ws-tenant-b",
    )

    assert result_a != result_b
    assert "ws-tenant-a" in str(result_a)
    assert "ws-tenant-b" in str(result_b)


def test_legacy_report_html_uses_workbench_report_theme() -> None:
    html = render_legacy_html(
        title="Deutung - Klaus Mustermann",
        subtitle="Morphic Engine Deutungsbericht",
        body_html='<section class="report-block"><h2>Abschnitt</h2><p>Inhalt</p></section>',
        focus="Bronchien",
        meta=(("Profil", "Phase 1"),),
    )

    assert f'data-report-theme="{REPORT_THEME_ID}"' in html
    assert "--report-paper: #f6f3ea;" in html
    assert "--report-surface: #fffdf7;" in html
    assert "--report-sage: #5f7f68;" in html
    assert "--report-terracotta: #b5654b;" in html
    assert "--rq-font-display:" in html
    assert "--rq-font-sans:" in html
    assert "--rq-radius-sm:" in html
    assert "border-radius: var(--rq-radius-sm)" in html
    assert "#E8F1F8" not in html
    assert "#6BA5D0" not in html
    assert "letter-spacing: -0.5px" not in html


def test_round_scores_for_export_limits_score_fractions_to_three_digits() -> None:
    payload = {
        "profile": "pathogen",
        "score": 1.23456,
        "top_scores": [
            {"label": "A", "score": 2.34567, "entropy_score": 0.98765},
            {"label": "B", "score": 3.0, "raw": 3.14159},
        ],
    }
    rounded = round_scores_for_export(payload)
    assert rounded["score"] == 1.235
    assert rounded["top_scores"][0]["score"] == 2.346
    assert rounded["top_scores"][0]["entropy_score"] == 0.988
    assert rounded["top_scores"][1]["score"] == 3
    assert rounded["top_scores"][1]["raw"] == 3.14159
    dumped = report_json_dumps(payload, indent=2)
    decoded = json.loads(dumped)
    assert decoded["top_scores"][0]["score"] == 2.346
