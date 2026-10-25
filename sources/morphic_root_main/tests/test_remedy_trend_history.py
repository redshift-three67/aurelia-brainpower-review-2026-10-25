import json
import os
import subprocess
import sys
from pathlib import Path

from core.compliance.runtime_manifest import RuntimeManifestService
from tools.remedy_reporter import consolidate_remedy_synergies


ROOT = Path(__file__).resolve().parents[1]


def _run_tool(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )


def _run_cli(args: list[str], runtime: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["MORPHIC_RUNTIME_DIR"] = str(runtime)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
    )


def _write_scan(path: Path, *, profile: str, bronchien_score: float, remedy_score: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "profile": profile,
                "client": {
                    "name": "Mustermann",
                    "first_name": "Klaus",
                    "birth_date": "09041966",
                    "birth_place": "Augsburg",
                },
                "sub_results": {
                    "top": [
                        {
                            "label": "Bronchien",
                            "group": "atmung",
                            "score": bronchien_score,
                        },
                        {
                            "label": "Mucosa compositum",
                            "group": "remedies",
                            "score": remedy_score,
                        },
                    ]
                },
                "remedy_synergies": [
                    {
                        "item1": "Mucosa compositum",
                        "item2": "Bronchien",
                        "synergy_score": remedy_score,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _seed_two_scans(archive: Path) -> None:
    _write_scan(
        archive
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP3_SESSION"
        / "01_atmung_lunge_detailliert"
        / "20251222_210515_01_atmung_lunge_detailliert_top3_multiplex_scan.json",
        profile="atmung_lunge_detailliert",
        bronchien_score=4.0,
        remedy_score=6.5,
    )
    _write_scan(
        archive
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251223_210515_TOP3_SESSION"
        / "02_atmung_lunge_detailliert"
        / "20251223_210515_02_atmung_lunge_detailliert_top3_multiplex_scan.json",
        profile="atmung_lunge_detailliert",
        bronchien_score=7.0,
        remedy_score=8.2,
    )


def test_remedy_reporter_writes_per_profile_reports(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    report_root = tmp_path / "reports"
    _seed_two_scans(archive)

    result = _run_tool(
        [
            "tools.remedy_reporter",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--archive-root",
            str(archive),
            "--output-root",
            str(report_root),
            "--top-n",
            "3",
        ]
    )

    assert result.returncode == 0, result.stdout + result.stderr
    remedies_dir = report_root / "Remedies" / "Mustermann_Klaus_09041966_Augsburg"
    assert list(remedies_dir.glob("*_top3_remedies.html"))
    profile_reports = list(remedies_dir.glob("*_remedy.html"))
    assert len(profile_reports) >= 1
    profile_html = profile_reports[0].read_text(encoding="utf-8")
    assert "Remedy Detailbericht" in profile_html
    assert "atmung_lunge_detailliert" in profile_html
    assert "Mucosa compositum" in profile_html
    assert "Bronchien" in profile_html


def test_remedy_consolidation_can_write_session_scoped_profile_reports(tmp_path: Path) -> None:
    scan_path = (
        tmp_path
        / "archive"
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260628_224628_TOP3_SESSION"
        / "01_pathogen"
        / "20260628_224628_01_pathogen_top3_multiplex_scan.json"
    )
    _write_scan(scan_path, profile="pathogen", bronchien_score=4.0, remedy_score=6.5)

    output_dir = tmp_path / "reports"
    ok = consolidate_remedy_synergies(
        [scan_path],
        output_dir,
        top_n=3,
        title="Remedy Report - Klaus Mustermann",
        session_id="20260628_224628",
    )

    assert ok is True
    assert (output_dir / "20260628_224628_pathogen_remedy.json").exists()
    assert (output_dir / "20260628_224628_pathogen_remedy.html").exists()
    assert (output_dir / "20260628_224628_top3_remedies.json").exists()
    assert (output_dir / "20260628_224628_top3_remedies.html").exists()
    assert not (output_dir / "pathogen_remedy.html").exists()


def test_trend_analyzer_writes_score_history(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    report_root = tmp_path / "reports"
    _seed_two_scans(archive)

    result = _run_tool(
        [
            "tools.trend_analyzer",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--archive-root",
            str(archive),
            "--output-root",
            str(report_root),
        ]
    )

    assert result.returncode == 0, result.stdout + result.stderr
    trends_dir = report_root / "Trends" / "Mustermann_Klaus_09041966_Augsburg"
    trend_json = list(trends_dir.glob("trendanalyse_*.json"))
    trend_html = list(trends_dir.glob("trendanalyse_*.html"))
    assert len(trend_json) == 1
    assert len(trend_html) == 1

    payload = json.loads(trend_json[0].read_text(encoding="utf-8"))
    assert payload["schema"] == "morphic_trend_report"
    assert payload["schema_version"] == 1
    bronchien = next(item for item in payload["trends"] if item["label"] == "Bronchien")
    assert bronchien["first_score"] == 4.0
    assert bronchien["latest_score"] == 7.0
    assert bronchien["delta"] == 3.0
    assert bronchien["direction"] == "steigend"

    html = trend_html[0].read_text(encoding="utf-8")
    assert "Trend-Historik" in html
    assert "Bronchien" in html
    assert "steigend" in html


def test_client_trends_wrapper_uses_archive_and_output_roots(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    report_root = tmp_path / "reports"
    runtime = tmp_path / "runtime"
    _seed_two_scans(archive)

    result = _run_cli(
        [
            "apps.cli.main",
            "trend",
            "client-trends",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--archive-root",
            str(archive),
            "--output-root",
            str(report_root),
        ],
        runtime,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    trends_dir = report_root / "Trends" / "Mustermann_Klaus_09041966_Augsburg"
    assert list(trends_dir.glob("trendanalyse_*.json"))
    assert list(trends_dir.glob("trendanalyse_*.html"))
    assert list(trends_dir.glob("trendanalyse_*.pdf"))

    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert {"trend_json", "trend_html", "trend_pdf"} <= artifact_types


def test_trend_analyzer_writes_notice_for_single_topn_session(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    report_root = tmp_path / "reports"
    session = archive / "Mustermann_Klaus_09041966_Augsburg" / "20260628_224628_TOP3_SESSION"
    for index, profile in enumerate(["pathogen", "toxin", "immune"], 1):
        _write_scan(
            session
            / f"{index:02d}_{profile}"
            / f"20260628_224628_{index:02d}_{profile}_top3_multiplex_scan.json",
            profile=profile,
            bronchien_score=float(index),
            remedy_score=6.5 + index,
        )

    result = _run_tool(
        [
            "tools.trend_analyzer",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--archive-root",
            str(archive),
            "--output-root",
            str(report_root),
        ]
    )

    assert result.returncode == 0, result.stdout + result.stderr
    trends_dir = report_root / "Trends" / "Mustermann_Klaus_09041966_Augsburg"
    notice = trends_dir / "Hinweis.txt"
    assert notice.exists()
    assert "Noch keine Trends" in notice.read_text(encoding="utf-8")
    assert not list(trends_dir.glob("trendanalyse_*.html"))
