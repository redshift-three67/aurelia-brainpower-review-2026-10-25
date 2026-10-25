from pydantic import ValidationError

from apps.web.contracts import Phase1ScanRequest
from apps.web.launcher import build_phase1_scan_launcher
from apps.web.workbench import current_scan_profile_pool_fingerprint
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
    payload.setdefault(
        "scan_profile_pool_fingerprint",
        current_scan_profile_pool_fingerprint(payload["profile_level"]),
    )
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
    assert command[command.index("--k-total") + 1] == "2048"
    assert command[command.index("--top-k") + 1] == "192"
    assert "--synergy" in command
    assert command[command.index("--synergy-combos") + 1] == "4"
    assert command[command.index("--synergy-threshold") + 1] == "6.0"
    assert command[command.index("--top-n") + 1] == "7"
    assert command[command.index("--focus") + 1] == "Bronchien"
    assert "--p-emotion" not in command
    assert command[command.index("--profile-template") + 1] == "phase1-default"
    assert command[command.index("--entropy-mode") + 1] == "legacy"
    assert "--image" not in command
    assert launcher["script_path"] == "Run-MultiplexScan.ps1"
    assert launcher["mode"] == "top_n_auto_scan"
    assert launcher["cli_entrypoint"].endswith(" -m apps.cli.main scan top3-scan")
    assert launcher["unsupported_request_fields"] == []


def test_phase1_launcher_preview_and_execution_share_same_command() -> None:
    request = make_request(top_n=5, focus="Atmungsorgane")

    preview = build_phase1_scan_launcher(request, executes=False)
    execution = build_phase1_scan_launcher(request, executes=True)

    assert preview["executes"] is False
    assert execution["executes"] is True
    assert preview["command"] == execution["command"]
    assert preview["launcher"] == execution["launcher"]
    assert preview["notes"] == execution["notes"]


def test_phase1_launcher_default_command_omits_local_ai_flags() -> None:
    command = build_phase1_scan_launcher(make_request(), executes=False)["command"]

    assert "--local-ai" not in command
    assert "--no-local-ai" not in command


def test_phase1_launcher_forwards_local_ai_once_with_preview_execution_parity() -> None:
    request = make_request(local_ai_enabled=True)

    preview = build_phase1_scan_launcher(request, executes=False)
    execution = build_phase1_scan_launcher(request, executes=True)

    assert preview["command"].count("--local-ai") == 1
    assert execution["command"] == preview["command"]


def test_phase1_launcher_combines_focus_and_main_symptom() -> None:
    launch = build_phase1_scan_launcher(
        make_request(focus="Bronchien", main_symptom="Husten", notes="nachts"),
        executes=False,
    )
    command = launch["command"]

    assert command[command.index("--focus") + 1] == "Bronchien | Husten"
    assert launch["focus"] == "Bronchien | Husten"
    assert "Hauptsymptom: Husten" in launch["notes"]
    assert "Notizen: nachts" in launch["notes"]


def test_phase1_launcher_omits_focus_extension_when_main_symptom_blank() -> None:
    launch = build_phase1_scan_launcher(
        make_request(focus="Bronchien", main_symptom="   "),
        executes=False,
    )
    command = launch["command"]

    assert command[command.index("--focus") + 1] == "Bronchien"
    assert launch["focus"] == "Bronchien"


def test_phase1_launcher_focus_blank_fallback_is_unreachable_via_contract() -> None:
    # launcher.py:63-66 has an `elif not effective_focus: effective_focus =
    # main_symptom` fallback branch, but Phase1ScanRequest.validate_required_text
    # rejects a blank `focus` before build_phase1_scan_launcher ever runs, so
    # this branch cannot be reached through the web contract. Documented here
    # instead of asserted as reachable launcher behavior.
    try:
        make_request(focus="   ", main_symptom="Husten")
    except ValidationError as exc:
        assert "focus must not be blank" in str(exc)
    else:
        raise AssertionError("expected ValidationError")


def test_phase1_launcher_does_not_duplicate_main_symptom_already_in_focus() -> None:
    launch = build_phase1_scan_launcher(
        make_request(focus="Bronchien und Husten", main_symptom="husten"),
        executes=False,
    )
    command = launch["command"]

    assert command[command.index("--focus") + 1] == "Bronchien und Husten"
    assert launch["focus"] == "Bronchien und Husten"


def test_phase1_launcher_forwards_opted_in_planet_type() -> None:
    launch = build_phase1_scan_launcher(
        make_request(planetary_vector_enabled=True, planet_type="Venus"), executes=False
    )

    command = launch["command"]
    assert command[command.index("--planet-type") + 1] == "Venus"


def test_phase1_launcher_forwards_phase1_cli_options() -> None:
    launch = build_phase1_scan_launcher(
        make_request(
            profile_template="personal-focused",
            entropy_mode="hybrid",
            image_path="C:/images/client.jpg",
            adaptive_limits=True,
        ),
        executes=False,
    )
    command = launch["command"]

    assert command[command.index("--profile-template") + 1] == "personal-focused"
    assert command[command.index("--entropy-mode") + 1] == "hybrid"
    assert command[command.index("--image") + 1] == "C:/images/client.jpg"
    assert "--adaptive-limits" in command
    assert launch["launcher"]["unsupported_request_fields"] == []
