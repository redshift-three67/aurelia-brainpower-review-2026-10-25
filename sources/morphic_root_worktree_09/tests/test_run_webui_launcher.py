from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "Run-WebUI.ps1"


def test_launcher_is_loopback_only_and_never_kills_an_existing_listener() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")

    assert '$HostName = "127.0.0.1"' in source
    assert "--host $HostName" in source
    assert "Stop-Process -Name" not in source
    assert 'throw "Port $Port ist bereits belegt' in source


def test_launcher_opens_browser_only_after_health_endpoint_is_ready() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")

    port_check = source.index("Get-NetTCPConnection -LocalPort $Port")
    browser_job = source.index('Start-Job -Name "MorphicWebUILaunchBrowser"')
    server_start = source.index("& $PythonExe -m uvicorn")

    assert '$HealthUrl = "$AdminExpectedOrigin/api/health"' in source
    assert "Invoke-WebRequest -UseBasicParsing -Uri $HealthUrl" in source
    assert port_check < browser_job < server_start


def test_launcher_uses_windows_powershell_compatible_nonce_generation() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")

    assert "RandomNumberGenerator]::Fill" not in source
    assert "RandomNumberGenerator]::Create()" in source
    assert ".GetBytes($Bytes)" in source


def test_launcher_preserves_default_port_and_adds_isolated_acceptance_mode() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")

    assert "[int]$Port = 8000" in source
    assert "[switch]$IsolatedAcceptance" in source
    assert "[switch]$NoBrowser" in source
    assert "[switch]$ExitAfterHealth" in source
    assert '$LaunchUrl = "$AdminExpectedOrigin/"' in source
    assert "$env:MORPHIC_RUNTIME_DIR" in source
    assert "$env:MORPHIC_HARMONIZATION_JOBS_DIR" in source
    assert "$env:MORPHIC_PARALLEL_EXPORT_ROOT" in source
    assert "morphic-webui-acceptance-" in source


def test_isolated_acceptance_mode_reports_health_and_exact_port_owner() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")

    managed_start = source.index("if ($IsolatedAcceptance)")
    process_start = source.index("Start-Process -FilePath $PythonExe", managed_start)
    health_wait = source.index("Invoke-WebRequest -UseBasicParsing -Uri $HealthUrl", process_start)
    owner_lookup = source.index("$PortOwnerPid", health_wait)
    browser_open = source.index("Start-Process $LaunchUrl", owner_lookup)
    exact_stop = source.index("Stop-Process -Id $PortOwnerPid", browser_open)

    assert managed_start < process_start < health_wait < owner_lookup < browser_open < exact_stop
    assert "Launcher-PID" in source
    assert "Port-Owner-PID" in source
    assert "QA Health" in source
    assert "if ($ExitAfterHealth)" in source
    assert "$CurrentListener" in source
    assert "[int]$CurrentListener.OwningProcess -eq $PortOwnerPid" in source
    assert "Stop-Process -Id $ServerProcess.Id" in source
