import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MOJIBAKE_MARKERS = ("Ã", "â", "ð", "\ufffd")


def _run_cli(args: list[str], runtime: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["MORPHIC_RUNTIME_DIR"] = str(runtime)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "apps.cli.main", *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
    )


def _assert_mojibake_free(label: str, text: str) -> None:
    found = [marker for marker in MOJIBAKE_MARKERS if marker in text]
    assert not found, f"{label} contains mojibake markers {found!r}: {text[:500]!r}"


def test_field_test_stdout_and_exports_are_mojibake_free(tmp_path: Path) -> None:
    output = tmp_path / "archive"
    result = _run_cli(
        [
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
        tmp_path / "runtime",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    _assert_mojibake_free("field-test stdout", result.stdout)
    for path in list(output.rglob("*_field_test.txt")) + list(output.rglob("*_field_test.html")):
        _assert_mojibake_free(str(path), path.read_text(encoding="utf-8"))


def test_multiplex_stdout_and_text_export_are_mojibake_free(tmp_path: Path) -> None:
    output = tmp_path / "archive"
    result = _run_cli(
        [
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
            "--export",
            str(output),
        ],
        tmp_path / "runtime",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    _assert_mojibake_free("multiplex stdout", result.stdout)
    txt_files = list(output.rglob("*_multiplex_scan.txt"))
    assert txt_files
    for path in txt_files:
        _assert_mojibake_free(str(path), path.read_text(encoding="utf-8"))
