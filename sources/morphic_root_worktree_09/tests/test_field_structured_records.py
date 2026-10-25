from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCREENING_PREFIX = "MORPHIC_SCREENING_RESULT_V1 "
EXPORT_PREFIX = "MORPHIC_MULTIPLEX_EXPORT_V1 "


def _run_field_scan(
    tmp_path: Path,
    export_root: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["MORPHIC_RUNTIME_DIR"] = str(tmp_path / "runtime")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "apps.cli.main",
            "field",
            "multiplex-scan",
            "SensitiveLastName",
            "SensitiveFirstName",
            "--birth-date",
            "01011990",
            "--birth-place",
            "PrivatePlace",
            "--profile",
            "chakren_meridiane",
            "--hardware-profile",
            "windows",
            "--k-total",
            "16",
            "--top-k",
            "5",
            "--focus",
            "Sensitive focus score=999",
            "--no-synergy",
            "--session-id",
            "structured-test-session",
            "--export",
            str(export_root or tmp_path / "exports"),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
    )


def test_field_multiplex_scan_emits_exact_structured_records_after_export(
    tmp_path: Path,
) -> None:
    result = _run_field_scan(tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    screening_lines = [
        line for line in result.stdout.splitlines() if line.startswith(SCREENING_PREFIX)
    ]
    export_lines = [
        line for line in result.stdout.splitlines() if line.startswith(EXPORT_PREFIX)
    ]
    assert len(screening_lines) == 1
    assert len(export_lines) == 1

    screening = json.loads(screening_lines[0][len(SCREENING_PREFIX) :])
    assert set(screening) == {"version", "profile", "scores"}
    assert screening["version"] == 1
    assert screening["profile"] == "chakren_meridiane"
    assert len(screening["scores"]) == 5
    assert all(isinstance(score, (int, float)) for score in screening["scores"])
    assert "Sensitive" not in screening_lines[0]
    assert str(tmp_path) not in screening_lines[0]

    exported = json.loads(export_lines[0][len(EXPORT_PREFIX) :])
    assert set(exported) == {
        "version",
        "profile",
        "session_id",
        "json_path",
        "html_path",
    }
    assert exported["version"] == 1
    assert exported["profile"] == "chakren_meridiane"
    assert exported["session_id"] == "structured-test-session"
    for key in ("json_path", "html_path"):
        artifact = Path(exported[key])
        assert artifact.is_file()
        assert artifact.stat().st_size > 0
        artifact.resolve().relative_to((tmp_path / "exports").resolve())


def test_field_export_failure_copy_is_redacted_and_record_is_after_registration() -> None:
    source = (ROOT / "apps" / "cli" / "commands" / "field.py").read_text(
        encoding="utf-8"
    )

    assert 'Export fehlgeschlagen: {exc}' not in source
    assert '_echo("Export fehlgeschlagen.")' in source
    emitter = source.index("_emit_multiplex_export_record(", source.index("def multiplex_scan("))
    json_registration = source.index('"multiplex_scan_json"', source.index("def multiplex_scan("))
    html_registration = source.index('"multiplex_scan_html"', json_registration)
    assert json_registration < html_registration < emitter


def test_field_treats_existing_json_suffixed_export_root_as_directory(
    tmp_path: Path,
) -> None:
    export_root = tmp_path / "result.json"
    export_root.mkdir()

    result = _run_field_scan(tmp_path, export_root)

    assert result.returncode == 0, result.stdout + result.stderr
    records = [
        line for line in result.stdout.splitlines() if line.startswith(EXPORT_PREFIX)
    ]
    assert len(records) == 1
    payload = json.loads(records[0][len(EXPORT_PREFIX) :])
    for key in ("json_path", "html_path"):
        artifact = Path(payload[key]).resolve()
        artifact.relative_to(export_root.resolve())
        assert artifact.is_file()
        assert artifact.stat().st_size > 0


def test_field_export_failure_emits_no_success_record_and_no_exception_detail(
    tmp_path: Path,
) -> None:
    blocked_root = tmp_path / "blocked-export-root"
    blocked_root.write_text("not a directory", encoding="utf-8")

    result = _run_field_scan(tmp_path, blocked_root)

    assert result.returncode == 0
    assert not any(
        line.startswith(EXPORT_PREFIX) for line in result.stdout.splitlines()
    )
    failure_lines = [
        line for line in result.stdout.splitlines() if "Export fehlgeschlagen" in line
    ]
    assert failure_lines == ["Export fehlgeschlagen."]
