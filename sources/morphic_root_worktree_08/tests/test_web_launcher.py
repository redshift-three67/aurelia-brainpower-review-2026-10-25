from apps.web.contracts import Phase1ScanRequest
from apps.web.launcher import build_phase1_scan_launcher
import sys


def make_request(**overrides: object) -> Phase1ScanRequest:
    payload = {
        "last_name": "Deisenhofer",
        "first_name": "Klaus",
        "birth_date": "09041966",
        "birth_place": "Augsburg",
        "focus": "Bronchien",
        "profile_level": 3,
        "top_n": 7,
        "profile_template": "phase1-default",
        "entropy_mode": "legacy",
        "image_path": None,
        "adaptive_limits": False,
        "consent_local": True,
        "consent_safety": True,
    }
    payload.update(overrides)
    return Phase1ScanRequest.model_validate(payload)


def test_phase1_launcher_builds_ps1_aligned_topn_command() -> None:
    launch = build_phase1_scan_launcher(make_request(), executes=False)
    command = launch["command"]
    launcher = launch["launcher"]

    assert launch["executes"] is False
    assert command[:6] == [
        sys.executable,
        "-m",
        "apps.cli.main",
        "scan",
        "top3-scan",
        "Deisenhofer",
    ]
    assert command[6] == "Klaus"
    assert command[command.index("--birth-date") + 1] == "09041966"
    assert command[command.index("--birth-place") + 1] == "Augsburg"
    assert command[command.index("--level") + 1] == "3"
    assert command[command.index("--export") + 1] == "C:\\Benutzer_Archive_Start"
    assert command[command.index("--hardware-profile") + 1] == "windows"
    assert command[command.index("--k-total") + 1] == "4096"
    assert command[command.index("--top-k") + 1] == "384"
    assert "--synergy" in command
    assert command[command.index("--synergy-combos") + 1] == "4"
    assert command[command.index("--synergy-threshold") + 1] == "6.0"
    assert command[command.index("--top-n") + 1] == "7"
    assert command[command.index("--focus") + 1] == "Bronchien"
    assert "--p-emotion" not in command
    assert "--entropy-mode" not in command
    assert "--image" not in command
    assert launcher["script_path"] == "Run-MultiplexScan.ps1"
    assert launcher["mode"] == "top_n_auto_scan"
    assert launcher["cli_entrypoint"].endswith(" -m apps.cli.main scan top3-scan")
    assert "profile_template" in launcher["unsupported_request_fields"]
    assert "entropy_mode" in launcher["unsupported_request_fields"]


def test_phase1_launcher_preview_and_execution_share_same_command() -> None:
    request = make_request(top_n=5, focus="Atmungsorgane")

    preview = build_phase1_scan_launcher(request, executes=False)
    execution = build_phase1_scan_launcher(request, executes=True)

    assert preview["executes"] is False
    assert execution["executes"] is True
    assert preview["command"] == execution["command"]
    assert preview["launcher"] == execution["launcher"]
    assert preview["notes"] == execution["notes"]
