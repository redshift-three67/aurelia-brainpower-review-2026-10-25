from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = PROJECT_ROOT / "Run-RemedyLookup.ps1"
REMEDY_DB = PROJECT_ROOT / "data" / "remedies.db"
REMEDY_SERVICE = PROJECT_ROOT / "services" / "remedy_service.py"
POWERSHELLS = tuple(
    executable
    for executable in (shutil.which("pwsh"), shutil.which("powershell.exe"))
    if executable is not None
)
POWERSHELL = POWERSHELLS[0] if POWERSHELLS else None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@contextmanager
def _isolated_launcher() -> Iterator[tuple[Path, Path]]:
    with tempfile.TemporaryDirectory(prefix="f44-remedy-lookup-", dir=PROJECT_ROOT.parent) as raw:
        sandbox = Path(raw)
        launcher = sandbox / LAUNCHER.name
        database = sandbox / "data" / REMEDY_DB.name
        service = sandbox / "services" / REMEDY_SERVICE.name
        database.parent.mkdir(parents=True)
        service.parent.mkdir(parents=True)
        shutil.copy2(LAUNCHER, launcher)
        shutil.copy2(REMEDY_DB, database)
        shutil.copy2(REMEDY_SERVICE, service)
        init_file = REMEDY_SERVICE.parent / "__init__.py"
        if init_file.exists():
            shutil.copy2(init_file, service.parent / init_file.name)
        yield launcher, database


def _run_launcher(
    tmp_path: Path,
    *,
    launcher: Path = LAUNCHER,
    powershell: str | None = None,
    action: str,
    query: str | None = None,
    environment_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    executable = powershell or POWERSHELL
    if executable is None:
        pytest.skip("PowerShell is unavailable")
    command = [
        executable,
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(launcher),
        "-Action",
        action,
        "-NoPause",
    ]
    if query is not None:
        command.extend(["-Query", query])
    environment = os.environ.copy()
    environment.pop("PYTHONUTF8", None)
    environment.pop("PYTHONIOENCODING", None)
    if environment_overrides:
        environment.update(environment_overrides)
    return subprocess.run(
        command,
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )


def test_launcher_migrates_missing_keyword_import_to_existing_authority() -> None:
    source = LAUNCHER.read_text(encoding="utf-8-sig")

    assert "find_remedies_by_keyword" not in source
    assert "from services.remedy_service import find_remedies_for_group" in source
    assert "def find_remedies" not in source
    assert "SELECT " not in source


def test_launcher_uses_fixed_code_and_argument_data_not_python_interpolation() -> None:
    source = LAUNCHER.read_text(encoding="utf-8-sig")

    assert "sys.argv" in source
    assert "@('-I', '-X', 'utf8', '-', $projectRoot)" in source
    assert "find_remedies_for_group('$keyword'" not in source
    assert "find_remedies_for_group('$group'" not in source
    assert "find_pathogens_by_keyword('$keyword'" not in source
    assert "sys.path.insert(0, '.')" not in source
    assert "$PSScriptRoot" in source
    assert ".venv" in source
    assert "$env:PYTHONUTF8 = '1'" in source
    assert "$env:PYTHONIOENCODING = 'utf-8'" in source
    assert "$OutputEncoding = [System.Text.UTF8Encoding]::new($false)" in source


def test_launcher_has_utf8_bom_for_windows_powershell_51() -> None:
    assert LAUNCHER.read_bytes().startswith(b"\xef\xbb\xbf")


def test_launcher_parses_as_powershell(tmp_path: Path) -> None:
    if POWERSHELL is None:
        pytest.skip("PowerShell is unavailable")
    escaped_launcher = str(LAUNCHER).replace("'", "''")
    result = subprocess.run(
        [
            POWERSHELL,
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            (
                "$errors=$null; "
                "[System.Management.Automation.Language.Parser]::ParseFile("
                f"'{escaped_launcher}', [ref]$null, [ref]$errors) "
                "> $null; if ($errors.Count) { $errors | ForEach-Object { "
                "[Console]::Error.WriteLine($_.Message) }; exit 1 }"
            ),
        ],
        cwd=tmp_path,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )

    assert result.returncode == 0, result.stderr


def test_launcher_keeps_interactive_default_and_can_exit_cleanly(tmp_path: Path) -> None:
    if POWERSHELL is None:
        pytest.skip("PowerShell is unavailable")
    result = subprocess.run(
        [
            POWERSHELL,
            "-NoProfile",
            "-File",
            str(LAUNCHER),
            "-NoPause",
        ],
        cwd=tmp_path,
        input="0\n",
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Suchoptionen:" in result.stdout
    assert "Beendet." in result.stdout


@pytest.mark.parametrize("powershell", POWERSHELLS)
def test_launcher_is_executable_on_available_powershell_runtimes(
    tmp_path: Path,
    powershell: str,
) -> None:
    environment = os.environ.copy()
    environment.pop("PYTHONUTF8", None)
    environment.pop("PYTHONIOENCODING", None)
    with _isolated_launcher() as (launcher, database):
        before = _sha256(database)
        result = subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-NonInteractive",
                "-File",
                str(launcher),
                "-Action",
                "Pathogen",
                "-Query",
                "candida",
                "-NoPause",
            ],
            cwd=tmp_path,
            env=environment,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

        assert result.returncode == 0, result.stdout + result.stderr
        assert "Remedies für Gruppe anzeigen" in result.stdout
        assert "Candida" in result.stdout
        assert "->" in result.stdout
        assert _sha256(database) == before


@pytest.mark.parametrize(
    ("action", "query", "expected"),
    [
        ("Keyword", "arnica", "Arnica"),
        ("Group", "bakterien_fein", "Gefunden:"),
        ("Pathogen", "candida", "Candida"),
        ("Stats", None, "Remedies:"),
    ],
)
def test_launcher_actions_execute_from_foreign_working_directory_without_mutation(
    tmp_path: Path,
    action: str,
    query: str | None,
    expected: str,
) -> None:
    with _isolated_launcher() as (launcher, database):
        before = _sha256(database)
        sidecars_before = tuple(
            sorted(path.name for path in database.parent.glob("remedies.db-*"))
        )
        result = _run_launcher(
            tmp_path,
            launcher=launcher,
            action=action,
            query=query,
        )

        assert result.returncode == 0, result.stdout + result.stderr
        assert expected in result.stdout
        assert _sha256(database) == before
        assert tuple(
            sorted(path.name for path in database.parent.glob("remedies.db-*"))
        ) == sidecars_before


@pytest.mark.parametrize("action", ["Keyword", "Group"])
def test_launcher_caps_remedy_results_at_ten_for_category_aliases(
    tmp_path: Path,
    action: str,
) -> None:
    with _isolated_launcher() as (launcher, database):
        before = _sha256(database)
        result = _run_launcher(
            tmp_path,
            launcher=launcher,
            action=action,
            query="heel_remedies_multiplex",
        )

        numbered_results = [
            line
            for line in result.stdout.splitlines()
            if line[:1].isdigit() and ". " in line
        ]
        assert result.returncode == 0, result.stdout + result.stderr
        assert len(numbered_results) == 10
        assert "Gefunden: 10 Remedies" in result.stdout
        assert _sha256(database) == before


def test_launcher_caps_pathogens_at_five_and_remedies_at_three_each(
    tmp_path: Path,
) -> None:
    with _isolated_launcher() as (launcher, database):
        before = _sha256(database)
        result = _run_launcher(
            tmp_path,
            launcher=launcher,
            action="Pathogen",
            query="candida",
        )

        remedy_counts: list[int] = []
        for line in result.stdout.splitlines():
            if line[:1].isdigit() and ". " in line:
                remedy_counts.append(0)
            elif line.startswith("     -> "):
                assert remedy_counts
                remedy_counts[-1] += 1

        assert result.returncode == 0, result.stdout + result.stderr
        assert 1 <= len(remedy_counts) <= 5
        assert all(count <= 3 for count in remedy_counts)
        assert _sha256(database) == before


def test_launcher_treats_query_as_data_and_does_not_execute_python(tmp_path: Path) -> None:
    marker = "F44_INJECTION_MARKER"
    with _isolated_launcher() as (launcher, _database):
        result = _run_launcher(
            tmp_path,
            launcher=launcher,
            action="Keyword",
            query=f"arnica'); print('{marker}') #",
        )

    assert result.returncode == 0, result.stdout + result.stderr
    assert marker not in result.stdout
    assert "Keine Remedies gefunden." in result.stdout


def test_launcher_ignores_foreign_cwd_and_pythonpath_sitecustomize(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "sitecustomize-loaded"
    (tmp_path / "sitecustomize.py").write_text(
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('loaded', encoding='utf-8')\n",
        encoding="utf-8",
    )
    with _isolated_launcher() as (launcher, database):
        before = _sha256(database)
        result = _run_launcher(
            tmp_path,
            launcher=launcher,
            action="Stats",
            environment_overrides={"PYTHONPATH": str(tmp_path)},
        )

        assert result.returncode == 0, result.stdout + result.stderr
        assert not marker.exists()
        assert _sha256(database) == before


@pytest.mark.parametrize("powershell", POWERSHELLS)
@pytest.mark.parametrize("native_exit_code", [7, 300])
def test_launcher_propagates_native_python_failure_without_touching_database(
    tmp_path: Path,
    powershell: str,
    native_exit_code: int,
) -> None:
    with _isolated_launcher() as (launcher, database):
        before = _sha256(database)
        service = launcher.parent / "services" / REMEDY_SERVICE.name
        service.write_text(f"raise SystemExit({native_exit_code})\n", encoding="utf-8")

        result = _run_launcher(
            tmp_path,
            launcher=launcher,
            powershell=powershell,
            action="Stats",
        )

        assert result.returncode == native_exit_code
        assert (
            f"Projekt-Python wurde mit Exitcode {native_exit_code}"
            in result.stdout + result.stderr
        )
        assert _sha256(database) == before


def test_launcher_rejects_missing_query_without_touching_database(tmp_path: Path) -> None:
    with _isolated_launcher() as (launcher, database):
        before = _sha256(database)
        result = _run_launcher(tmp_path, launcher=launcher, action="Keyword")

        assert result.returncode != 0
        assert "Suchbegriff ist erforderlich" in result.stdout + result.stderr
        assert _sha256(database) == before
