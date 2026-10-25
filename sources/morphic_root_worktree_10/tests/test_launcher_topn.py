from pathlib import Path


def test_launcher_offers_top_n_selection() -> None:
    launcher = Path("Run-MultiplexScan.ps1").read_text(encoding="utf-8")

    assert "Top-N Auto-Scan" in launcher
    assert "Top-3/5/7/9" in launcher
    assert "Read-TopNSelection" in launcher
    assert "'--top-n', $TopN.ToString()" in launcher
    assert "'--top-n', '5'" not in launcher


def test_launcher_runs_strict_health_preflight() -> None:
    launcher = Path("Run-MultiplexScan.ps1").read_text(encoding="utf-8")

    assert "$PythonExe -m apps.cli.main health --strict" in launcher


def test_launcher_validates_source_registry_before_menu() -> None:
    launcher = Path("Run-MultiplexScan.ps1").read_text(encoding="utf-8")

    assert "$PythonExe -m apps.cli.main sources validate" in launcher
    assert launcher.index("sources validate") < launcher.index("SCAN-MODUS AUSWAHL")


def test_launcher_loads_profiles_from_profile_sync() -> None:
    launcher = Path("Run-MultiplexScan.ps1").read_text(encoding="utf-8")

    assert "Get-MorphicProfiles" in launcher
    assert "from core.profile_sync import get_all_profiles" in launcher
    assert "$profiles = @(Get-MorphicProfiles -PythonExe $pythonExe)" in launcher
    assert "Name = 'heel_remedies'" not in launcher
