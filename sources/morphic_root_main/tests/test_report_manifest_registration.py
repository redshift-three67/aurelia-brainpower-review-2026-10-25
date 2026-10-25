import json
import os
import subprocess
import sys
from pathlib import Path

from core.compliance.runtime_manifest import RuntimeManifestService


ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str], runtime: Path) -> subprocess.CompletedProcess[str]:
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


def _sample_scan(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
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
                            "group": "atmung_lunge_detailliert",
                            "score": 6.2,
                        }
                    ]
                },
                "quantum_synergy": [{"score": 8.4, "category": "primary"}],
                "remedy_synergies": [
                    {"item1": "Mucosa compositum", "item2": "Bronchien", "synergy_score": 7.1}
                ],
            }
        ),
        encoding="utf-8",
    )


def test_interpretation_tool_registers_report_artifact(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    output = tmp_path / "reports"

    result = _run(
        [
            "tools.interpretation_generator",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--scans",
            "3",
            "--archive-root",
            str(tmp_path / "empty_archive"),
            "--output-root",
            str(output),
        ],
        runtime,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert {"interpretation_html", "interpretation_pdf"} <= artifact_types
    assert any(entry["path"].endswith(".html") for entry in artifacts)
    assert any(entry["path"].endswith(".pdf") for entry in artifacts)


def test_synergy_tool_registers_html_and_json_artifacts(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    archive = tmp_path / "archive"
    output = tmp_path / "reports"
    _sample_scan(
        archive
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP3_SESSION"
        / "01_atmung"
        / "20251222_210515_01_atmung_top3_multiplex_scan.json"
    )

    result = _run(
        [
            "tools.synergy_consolidator",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--archive-root",
            str(archive),
            "--output-root",
            str(output),
        ],
        runtime,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert {"synergy_json", "synergy_html", "synergy_pdf"} <= artifact_types


def test_remedy_tool_registers_pdf_artifacts(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    archive = tmp_path / "archive"
    output = tmp_path / "reports"
    _sample_scan(
        archive
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP3_SESSION"
        / "01_atmung"
        / "20251222_210515_01_atmung_top3_multiplex_scan.json"
    )

    result = _run(
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
            str(output),
            "--top-n",
            "3",
        ],
        runtime,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert {"remedy_pdf", "remedy_profile_pdf"} <= artifact_types
    assert all(Path(entry["path"]).exists() for entry in artifacts if entry["artifact_type"].endswith("_pdf"))


def test_trend_tool_registers_pdf_artifact_for_real_history(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    archive = tmp_path / "archive"
    output = tmp_path / "reports"
    _sample_scan(
        archive
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP3_SESSION"
        / "01_atmung"
        / "20251222_210515_01_atmung_top3_multiplex_scan.json"
    )
    _sample_scan(
        archive
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251223_210515_TOP3_SESSION"
        / "01_atmung"
        / "20251223_210515_01_atmung_top3_multiplex_scan.json"
    )

    result = _run(
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
            str(output),
        ],
        runtime,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert {"trend_json", "trend_html", "trend_pdf"} <= artifact_types


def test_field_test_export_registers_json_html_and_txt_artifacts(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    output = tmp_path / "archive"

    result = _run(
        [
            "apps.cli.main",
            "field",
            "field-test",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--hardware-profile",
            "windows",
            "--top-k",
            "2",
            "--focus",
            "Bronchien",
            "--export",
            str(output),
        ],
        runtime,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert {"field_test_json", "field_test_html", "field_test_pdf", "field_test_txt"} <= artifact_types
    assert any(entry["path"].endswith(".pdf") for entry in artifacts)
    pdf_files = list(output.rglob("*_field_test.pdf"))
    assert pdf_files
    assert pdf_files[0].read_bytes().startswith(b"%PDF-")
    json_files = list(output.rglob("*_field_test.json"))
    assert json_files
    payload = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert payload["schema"] == "morphic_field_test"
    assert payload["schema_version"] == 1


def test_scan_analyze_export_registers_json_html_and_pdf_artifacts(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    output = tmp_path / "archive"

    result = _run(
        [
            "apps.cli.main",
            "scan",
            "analyze",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--group",
            "chakren",
            "--seed",
            "manifest-test",
            "--fixed-h",
            "0.5",
            "--top-k",
            "2",
            "--focus",
            "Bronchien",
            "--export",
            str(output),
        ],
        runtime,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert {"analyze_json", "analyze_html", "analyze_pdf"} <= artifact_types
    pdf_files = list(output.rglob("*_analyze.pdf"))
    assert pdf_files
    assert pdf_files[0].read_bytes().startswith(b"%PDF-")
    json_files = list(output.rglob("*_analyze.json"))
    assert json_files
    payload = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert payload["schema"] == "morphic_analyze_export"
    assert payload["schema_version"] == 1


def test_multiplex_export_3d_registers_viewer_artifact(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    output = tmp_path / "archive"

    result = _run(
        [
            "apps.cli.main",
            "field",
            "multiplex-scan",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--profile",
            "chakren_meridiane",
            "--hardware-profile",
            "windows",
            "--k-total",
            "16",
            "--top-k",
            "2",
            "--focus",
            "Chakren",
            "--no-synergy",
            "--export-3d",
            "--export",
            str(output),
        ],
        runtime,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert "multiplex_scan_3d_json" in artifact_types
    viewer_files = list(output.rglob("*_3d_scan.json"))
    assert viewer_files
    payload = json.loads(viewer_files[0].read_text(encoding="utf-8"))
    assert payload["points"]


def test_scan_multiplex_wrapper_exports_reports_like_field_command(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    output = tmp_path / "archive"

    result = _run(
        [
            "apps.cli.main",
            "scan",
            "multiplex-scan",
            "Mustermann",
            "Klaus",
            "--birth-date",
            "09041966",
            "--birth-place",
            "Augsburg",
            "--profile",
            "chakren_meridiane",
            "--hardware-profile",
            "windows",
            "--k-total",
            "16",
            "--top-k",
            "2",
            "--focus",
            "Chakren",
            "--no-synergy",
            "--export",
            str(output),
        ],
        runtime,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    exports = list(output.rglob("*_multiplex_scan.json"))
    assert exports
    assert all(path.with_suffix(".html").exists() for path in exports)
    assert all(path.with_suffix(".pdf").read_bytes().startswith(b"%PDF-") for path in exports)

    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert {"multiplex_scan_json", "multiplex_scan_html", "multiplex_scan_pdf", "multiplex_scan_txt"} <= artifact_types


def test_nls_3d_export_command_writes_viewer_json_and_manifest_artifact(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    archive = tmp_path / "archive"
    scan_path = (
        archive
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP3_SESSION"
        / "01_atmung"
        / "20251222_210515_01_atmung_top3_multiplex_scan.json"
    )
    _sample_scan(scan_path)

    result = _run(
        [
            "apps.cli.main",
            "scan",
            "nls-3d-export",
            str(scan_path),
        ],
        runtime,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    output_path = scan_path.with_name(f"{scan_path.stem}_3d_scan.json")
    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["points"]
    assert {"id", "label", "coords", "value", "intensity"} <= set(payload["points"][0])

    artifacts = RuntimeManifestService(runtime).load_store("artifacts")["artifacts"]
    artifact_types = {entry["artifact_type"] for entry in artifacts}
    assert "nls_3d_json" in artifact_types
    assert any(entry["path"] == str(output_path) for entry in artifacts)
