import json
import subprocess
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from apps.cli.main import app as cli_app
from apps.cli.commands import scan as scan_module
from apps.cli.commands.scan import (
    _build_interpretation_report_command,
    _build_phase1_cli_option_args,
    _effective_adaptive_top_k,
    _phase1_template_values,
)
from core import profile_sync


EXPECTED_FINGERPRINT_ENV = "MORPHIC_EXPECTED_SCAN_PROFILE_POOL_FINGERPRINT"
PROCESS_GATE_NONCE_ENV = "MORPHIC_SCAN_PROCESS_GATE_NONCE"
PROCESS_GATE_PROOF_ENV = "MORPHIC_SCAN_PROCESS_GATE_PROOF"
PRIVATE_SCAN_ENV_NAMES = (
    EXPECTED_FINGERPRINT_ENV,
    PROCESS_GATE_NONCE_ENV,
    PROCESS_GATE_PROOF_ENV,
)
PROFILE_AUTHORITY_MISMATCH = (
    "Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein."
)
SCREENING_RESULT_PREFIX = "MORPHIC_SCREENING_RESULT_V1 "
MULTIPLEX_EXPORT_PREFIX = "MORPHIC_MULTIPLEX_EXPORT_V1 "


def test_phase1_template_values_map_to_personal_profile_axes() -> None:
    assert _phase1_template_values("phase1-default") == {
        "emotion": 0.5,
        "physisch": 0.5,
        "mental": 0.5,
        "astral": 0.5,
    }
    assert _phase1_template_values("personal-balanced") == {
        "emotion": 0.6,
        "physisch": 0.6,
        "mental": 0.6,
        "astral": 0.6,
    }
    assert _phase1_template_values("personal-focused") == {
        "emotion": 0.55,
        "physisch": 0.75,
        "mental": 0.65,
        "astral": 0.45,
    }


def test_phase1_cli_options_forward_entropy_image_and_template() -> None:
    args, env = _build_phase1_cli_option_args(
        profile_template="personal-focused",
        entropy_mode="hybrid",
        image_path="C:/images/client.png",
    )

    assert env == {"ME_ENTROPY_MODE": "hybrid"}
    assert args == [
        "--p-emotion",
        "0.55",
        "--p-physisch",
        "0.75",
        "--p-mental",
        "0.65",
        "--p-astral",
        "0.45",
        "--hybrid-entropy",
        "--image",
        "C:/images/client.png",
    ]


def test_phase1_cli_options_append_opted_in_planet_type_only() -> None:
    args, _ = _build_phase1_cli_option_args(
        profile_template="phase1-default",
        entropy_mode="legacy",
        image_path="",
        planet_type="Venus",
    )

    assert args[-2:] == ["--planet-type", "Venus"]


def test_adaptive_limits_reduce_detail_top_k_without_starving_reports() -> None:
    assert _effective_adaptive_top_k(192, top_n=7, adaptive_limits=True) == 112
    assert _effective_adaptive_top_k(64, top_n=7, adaptive_limits=True) == 64
    assert _effective_adaptive_top_k(192, top_n=7, adaptive_limits=False) == 192

    detail_candidates = list(range(192))
    without_limits = detail_candidates[
        : _effective_adaptive_top_k(192, top_n=7, adaptive_limits=False)
    ]
    with_limits = detail_candidates[
        : _effective_adaptive_top_k(192, top_n=7, adaptive_limits=True)
    ]

    assert without_limits == detail_candidates
    assert with_limits == detail_candidates[:112]
    assert 191 in without_limits
    assert 191 not in with_limits


@pytest.mark.parametrize(
    ("local_ai", "expected_llm_count"),
    [(False, 0), (True, 1)],
    ids=["default-off", "explicit-local-ai"],
)
def test_interpretation_report_command_forwards_explicit_local_ai_once(
    tmp_path: Path,
    local_ai: bool,
    expected_llm_count: int,
) -> None:
    base_dir = tmp_path / "client-reports"

    command = _build_interpretation_report_command(
        name="Mustermann",
        first_name="Max",
        birth_date="01011990",
        birth_place="Berlin",
        top_n=5,
        focus="Bandscheiben",
        base_dir=base_dir,
        local_ai=local_ai,
    )

    assert command[:3] == [
        scan_module.sys.executable,
        "-m",
        "tools.interpretation_generator",
    ]
    assert command.count("--llm") == expected_llm_count
    assert [argument for argument in command if argument != "--llm"] == [
        scan_module.sys.executable,
        "-m",
        "tools.interpretation_generator",
        "Mustermann",
        "Max",
        "--birth-date",
        "01011990",
        "--birth-place",
        "Berlin",
        "--scans",
        "5",
        "--focus",
        "Bandscheiben",
        "--archive-root",
        str(base_dir),
        "--output-root",
        str(base_dir),
    ]


def _run_top3_scan(
    tmp_path: Path,
    *,
    profile_level: int = 3,
    adaptive_limits: bool = False,
    local_ai: bool = False,
    top_n: int = 7,
    entropy_mode: str = "legacy",
    export_path: Path | None = None,
    focus: str = "",
    quick_scan: bool = True,
) -> None:
    scan_module.top3_scan.__wrapped__(
        name="Test",
        first_name="Gate3",
        birth_date="01011990",
        birth_place="Berlin",
        export_path=str(export_path or tmp_path / "exports"),
        focus=focus,
        k_total=4096,
        top_k=192,
        hardware_profile="windows",
        quick_scan=quick_scan,
        synergy=False,
        synergy_combos=4,
        synergy_threshold=6.0,
        top_n=top_n,
        profile_level=profile_level,
        profile_template="phase1-default",
        entropy_mode=entropy_mode,
        image_path="",
        planet_type="",
        adaptive_limits=adaptive_limits,
        local_ai=local_ai,
    )


def _successful_scan_run(
    commands: list[list[str]],
    environments: list[dict[str, str]] | None = None,
    artifacts: list[tuple[Path, Path]] | None = None,
):
    def fake_run(command, **kwargs):
        captured = list(command)
        commands.append(captured)
        if environments is not None:
            environments.append(dict(kwargs["env"]))
        if "--export" not in captured:
            profile = captured[captured.index("--profile") + 1]
            score_count = int(captured[captured.index("--top-k") + 1])
            return subprocess.CompletedProcess(
                captured,
                0,
                stdout=(
                    "Human-readable candidate score=12345\n"
                    + SCREENING_RESULT_PREFIX
                    + json.dumps(
                        {
                            "version": 1,
                            "profile": profile,
                            "scores": [float(score_count - index) for index in range(score_count)],
                        },
                        separators=(",", ":"),
                    )
                    + "\n"
                ),
                stderr="",
            )
        profile = captured[captured.index("--profile") + 1]
        session_id = captured[captured.index("--session-id") + 1]
        export_root = Path(captured[captured.index("--export") + 1]).resolve()
        artifact_dir = export_root / "synthetic" / profile
        artifact_dir.mkdir(parents=True, exist_ok=True)
        json_path = artifact_dir / f"{session_id}_{profile}.json"
        html_path = artifact_dir / f"{session_id}_{profile}.html"
        json_path.write_text("{}", encoding="utf-8")
        html_path.write_text("<html></html>", encoding="utf-8")
        if artifacts is not None:
            artifacts.append((json_path, html_path))
        return subprocess.CompletedProcess(
            captured,
            0,
            stdout=(
                MULTIPLEX_EXPORT_PREFIX
                + json.dumps(
                    {
                        "version": 1,
                        "profile": profile,
                        "session_id": session_id,
                        "json_path": str(json_path),
                        "html_path": str(html_path),
                    },
                    separators=(",", ":"),
                )
                + "\n"
            ),
            stderr="",
        )

    return fake_run


def _patch_post_processing(monkeypatch: pytest.MonkeyPatch) -> None:
    from tools import remedy_reporter, synergy_consolidator

    monkeypatch.setattr(
        synergy_consolidator,
        "consolidate_synergies",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(
        remedy_reporter,
        "consolidate_remedy_synergies",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(scan_module, "_run_topn_report_tool", lambda *_args: False)


def test_top3_scan_source_has_one_profile_authority_and_no_fallback_pool() -> None:
    source = Path(scan_module.__file__).read_text(encoding="utf-8")

    assert "TOP3_ANALYSIS_PROFILES" not in source
    assert "_PROFILES_SYNCED" not in source
    assert "Pathogene Erreger (Bakterien, Viren, Parasiten, Pilze)" not in source
    assert "from core.profile_sync import (" in source
    assert (
        source.count(
            "screening_profiles = get_top_n_analysis_profiles_by_level(profile_level)"
        )
        == 1
    )


def test_top3_scan_uses_imported_provider_for_requested_level_and_pool(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requested_levels: list[int] = []

    def authoritative_profiles(level: int) -> list[tuple[str, str]]:
        requested_levels.append(level)
        return [("authority-only", "Authoritative screening profile")]

    monkeypatch.setattr(
        scan_module,
        "get_top_n_analysis_profiles_by_level",
        authoritative_profiles,
    )
    monkeypatch.setattr(scan_module, "_collect_current_session_scan_files", lambda *_: [])
    _patch_post_processing(monkeypatch)
    commands: list[list[str]] = []
    monkeypatch.setattr(scan_module.subprocess, "run", _successful_scan_run(commands))

    _run_top3_scan(tmp_path, profile_level=4, top_n=1)

    assert requested_levels == [4]
    assert len(commands) == 2
    assert [command[command.index("--profile") + 1] for command in commands] == [
        "authority-only",
        "authority-only",
    ]


@pytest.mark.parametrize(
    "authority_error",
    [
        profile_sync.ProfileAuthorityError(r"C:\private\profiles\authority.json"),
        OSError(r"C:\private\profiles\provider.json"),
    ],
    ids=["profile-authority-error", "unexpected-authority-error"],
)
def test_top3_scan_redacts_profile_provider_error_before_subscan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
    authority_error: Exception,
) -> None:
    subscan_commands: list[list[str]] = []
    monkeypatch.setenv(EXPECTED_FINGERPRINT_ENV, "a" * 64)
    activation_calls: list[str] = []

    def unavailable_profiles(_level: int) -> list[tuple[str, str]]:
        raise authority_error

    monkeypatch.setattr(
        scan_module,
        "get_top_n_analysis_profiles_by_level",
        unavailable_profiles,
    )
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        lambda command, **_kwargs: subscan_commands.append(list(command)),
    )
    monkeypatch.setattr(
        scan_module,
        "resolve_operator_context",
        lambda: activation_calls.append("context"),
    )
    monkeypatch.setattr(
        scan_module,
        "resolve_topn_group_opt_in",
        lambda **_kwargs: activation_calls.append("activation"),
    )

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path)

    output = capsys.readouterr()
    combined_output = output.out + output.err
    assert captured.value.exit_code == 1
    assert subscan_commands == []
    assert activation_calls == []
    assert EXPECTED_FINGERPRINT_ENV not in scan_module.os.environ
    assert "Scanprofil-Pool nicht verfügbar." in output.err
    assert "C:\\private" not in combined_output
    assert all("C:\\private" not in record.getMessage() for record in caplog.records)


@pytest.mark.parametrize(
    ("adaptive_limits", "expected_top_k"),
    [(False, "192"), (True, "112")],
)
def test_top3_scan_passes_effective_top_k_to_real_phase2_command(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    adaptive_limits: bool,
    expected_top_k: str,
) -> None:
    monkeypatch.setattr(
        scan_module,
        "get_top_n_analysis_profiles_by_level",
        lambda _level: [
            (f"synthetic-profile-{index}", f"Synthetic screening profile {index}")
            for index in range(7)
        ],
    )
    monkeypatch.setattr(scan_module, "_collect_current_session_scan_files", lambda *_: [])
    _patch_post_processing(monkeypatch)
    commands: list[list[str]] = []
    monkeypatch.setattr(scan_module.subprocess, "run", _successful_scan_run(commands))

    _run_top3_scan(tmp_path, adaptive_limits=adaptive_limits)
    output = capsys.readouterr().out

    assert len(commands) == 14
    screening_command, phase2_command = commands[0], commands[7]
    assert "--export" not in screening_command
    assert screening_command[screening_command.index("--k-total") + 1] == "24"
    assert screening_command[screening_command.index("--top-k") + 1] == "4"
    assert "--export" in phase2_command
    assert (
        phase2_command[phase2_command.index("--profile") + 1]
        == "synthetic-profile-0"
    )
    assert phase2_command[phase2_command.index("--top-k") + 1] == expected_top_k
    phase2_profile = phase2_command[phase2_command.index("--profile") + 1]
    phase2_session = phase2_command[phase2_command.index("--session-id") + 1]
    canonical_session = f"{phase2_session}_TOP7_SESSION"
    multiplex_records = [
        json.loads(line.removeprefix(MULTIPLEX_EXPORT_PREFIX))
        for line in output.splitlines()
        if line.startswith(MULTIPLEX_EXPORT_PREFIX)
    ]
    assert len(multiplex_records) == 7
    assert {record.get("session_id") for record in multiplex_records} == {
        canonical_session
    }
    assert any(
        record.get("profile") == phase2_profile
        and record.get("session_id") == canonical_session
        for record in multiplex_records
    )
    assert (tmp_path / "exports").is_dir()


@pytest.mark.parametrize(
    ("quick_scan", "expected_k_total", "expected_top_k"),
    [(True, "24", "4"), (False, "48", "5")],
    ids=["quick", "full"],
)
def test_top3_scan_screening_budget_matches_quick_full_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    quick_scan: bool,
    expected_k_total: str,
    expected_top_k: str,
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    commands: list[list[str]] = []
    monkeypatch.setattr(scan_module.subprocess, "run", _successful_scan_run(commands))

    _run_top3_scan(tmp_path, top_n=5, quick_scan=quick_scan)

    assert len(commands) == 10
    for command in commands[:5]:
        assert command[command.index("--k-total") + 1] == expected_k_total
        assert command[command.index("--top-k") + 1] == expected_top_k


def _authoritative_profiles(count: int = 5) -> list[tuple[str, str]]:
    return [
        (f"authority-profile-{index}", f"Authority profile {index}")
        for index in range(count)
    ]


def _patch_scan_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    profiles: list[tuple[str, str]],
) -> None:
    monkeypatch.setattr(
        scan_module,
        "get_top_n_analysis_profiles_by_level",
        lambda _level: profiles,
    )
    monkeypatch.setattr(scan_module, "_collect_current_session_scan_files", lambda *_: [])
    _patch_post_processing(monkeypatch)


def _invoke_top3_scan_cli(tmp_path: Path):
    return CliRunner().invoke(
        cli_app,
        [
            "scan",
            "top3-scan",
            "Test",
            "Gate3",
            "--birth-date",
            "01011990",
            "--birth-place",
            "Berlin",
            "--export",
            str(tmp_path / "exports"),
            "--top-n",
            "5",
        ],
    )


def _set_private_scan_environment(
    monkeypatch: pytest.MonkeyPatch,
    *,
    nonce: str | None,
    proof: str | None,
    fingerprint: str | None,
) -> None:
    for key, value in (
        (PROCESS_GATE_NONCE_ENV, nonce),
        (PROCESS_GATE_PROOF_ENV, proof),
        (EXPECTED_FINGERPRINT_ENV, fingerprint),
    ):
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)


def _record_private_environment_pops(
    monkeypatch: pytest.MonkeyPatch,
) -> list[str]:
    pop_calls: list[str] = []
    environment_type = type(scan_module.os.environ)
    original_pop = environment_type.pop

    def recording_pop(environment, key, *args):
        if key in PRIVATE_SCAN_ENV_NAMES:
            pop_calls.append(key)
        return original_pop(environment, key, *args)

    monkeypatch.setattr(environment_type, "pop", recording_pop)
    return pop_calls


def _disable_command_logging_side_effects(monkeypatch: pytest.MonkeyPatch) -> None:
    from cli.utils import backup as backup_module

    monkeypatch.setattr(backup_module, "_create_backup", lambda *_args: None)
    monkeypatch.setattr(backup_module.log, "info", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        backup_module.log,
        "exception",
        lambda *_args, **_kwargs: None,
    )


def test_scan_profile_pool_fingerprint_environment_constant_is_shared() -> None:
    assert (
        getattr(profile_sync, "SCAN_PROFILE_POOL_FINGERPRINT_ENV", None)
        == EXPECTED_FINGERPRINT_ENV
    )
    assert (
        getattr(scan_module, "SCAN_PROFILE_POOL_FINGERPRINT_ENV", None)
        == EXPECTED_FINGERPRINT_ENV
    )


def test_top3_scan_valid_process_proof_is_popped_before_pool_and_reaches_scan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profiles = _authoritative_profiles()
    fingerprint = profile_sync.build_scan_profile_pool_fingerprint(3, profiles)
    nonce = "a" * 64
    proof = profile_sync.build_scan_process_gate_proof(nonce, fingerprint)
    _set_private_scan_environment(
        monkeypatch,
        nonce=nonce,
        proof=proof,
        fingerprint=fingerprint,
    )
    pop_calls = _record_private_environment_pops(monkeypatch)
    pool_calls: list[int] = []

    def authoritative_profiles(level: int) -> list[tuple[str, str]]:
        assert pop_calls == list(PRIVATE_SCAN_ENV_NAMES)
        assert all(key not in scan_module.os.environ for key in PRIVATE_SCAN_ENV_NAMES)
        pool_calls.append(level)
        return profiles

    monkeypatch.setattr(
        scan_module,
        "get_top_n_analysis_profiles_by_level",
        authoritative_profiles,
    )
    monkeypatch.setattr(scan_module, "resolve_operator_context", lambda: object())
    monkeypatch.setattr(scan_module, "resolve_topn_group_opt_in", lambda **_kwargs: None)
    monkeypatch.setattr(scan_module, "_collect_current_session_scan_files", lambda *_: [])
    _patch_post_processing(monkeypatch)
    _disable_command_logging_side_effects(monkeypatch)
    commands: list[list[str]] = []
    environments: list[dict[str, str]] = []
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        _successful_scan_run(commands, environments),
    )

    result = _invoke_top3_scan_cli(tmp_path)

    assert result.exit_code == 0, result.output
    assert pool_calls == [3]
    assert len(commands) == 10
    assert all(
        key not in environment
        for environment in environments
        for key in PRIVATE_SCAN_ENV_NAMES
    )
    assert all(key not in scan_module.os.environ for key in PRIVATE_SCAN_ENV_NAMES)
    for private_value in (fingerprint, nonce, proof):
        assert private_value not in result.output
    for private_name in PRIVATE_SCAN_ENV_NAMES:
        assert private_name not in result.output


@pytest.mark.parametrize(
    ("nonce", "proof", "fingerprint"),
    [
        ("a" * 64, None, "b" * 64),
        ("a" * 64, None, None),
        (None, "c" * 64, "b" * 64),
        (None, "c" * 64, None),
        ("A" * 64, "c" * 64, "b" * 64),
        ("short-nonce", "c" * 64, "b" * 64),
        ("g" * 64, "c" * 64, "b" * 64),
        ("a" * 64, "C" * 64, "b" * 64),
        ("a" * 64, "short-proof", "b" * 64),
        ("a" * 64, "g" * 64, "b" * 64),
        ("a" * 64, "c" * 64, "B" * 64),
        ("a" * 64, "c" * 64, "short-fingerprint"),
        ("a" * 64, "c" * 64, "g" * 64),
        (
            "a" * 64,
            profile_sync.build_scan_process_gate_proof("a" * 64, ""),
            None,
        ),
        ("a" * 64, "0" * 64, "b" * 64),
    ],
    ids=[
        "missing-proof",
        "nonce-only-without-fingerprint",
        "missing-nonce",
        "proof-only-without-fingerprint",
        "uppercase-nonce",
        "short-nonce",
        "nonhex-nonce",
        "uppercase-proof",
        "short-proof",
        "nonhex-proof",
        "uppercase-fingerprint",
        "short-fingerprint",
        "nonhex-fingerprint",
        "missing-fingerprint",
        "tampered-proof",
    ],
)
def test_top3_scan_invalid_process_proof_fails_before_all_side_effects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    nonce: str | None,
    proof: str | None,
    fingerprint: str | None,
) -> None:
    _set_private_scan_environment(
        monkeypatch,
        nonce=nonce,
        proof=proof,
        fingerprint=fingerprint,
    )
    pop_calls = _record_private_environment_pops(monkeypatch)
    failure_messages: list[str] = []
    original_fail = scan_module._fail_top3_scan

    def failure_probe(message: str) -> None:
        assert pop_calls == list(PRIVATE_SCAN_ENV_NAMES)
        assert all(key not in scan_module.os.environ for key in PRIVATE_SCAN_ENV_NAMES)
        failure_messages.append(message)
        original_fail(message)

    pool_calls: list[int] = []
    context_calls: list[str] = []
    activation_calls: list[str] = []
    export_calls: list[Path] = []
    subprocess_calls: list[list[str]] = []

    def forbidden_mkdir(path: Path, *_args, **_kwargs) -> None:
        export_calls.append(path)
        raise AssertionError("export root reached")

    monkeypatch.setattr(scan_module, "_fail_top3_scan", failure_probe)
    monkeypatch.setattr(
        scan_module,
        "get_top_n_analysis_profiles_by_level",
        lambda level: pool_calls.append(level) or _authoritative_profiles(),
    )
    monkeypatch.setattr(
        scan_module,
        "resolve_operator_context",
        lambda: context_calls.append("context"),
    )
    monkeypatch.setattr(
        scan_module,
        "resolve_topn_group_opt_in",
        lambda **_kwargs: activation_calls.append("activation"),
    )
    monkeypatch.setattr(Path, "mkdir", forbidden_mkdir)
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        lambda command, **_kwargs: subprocess_calls.append(list(command)),
    )
    _disable_command_logging_side_effects(monkeypatch)

    result = _invoke_top3_scan_cli(tmp_path)

    assert result.exit_code == 1
    assert result.stdout == ""
    assert result.stderr == PROFILE_AUTHORITY_MISMATCH + "\n"
    assert failure_messages == [PROFILE_AUTHORITY_MISMATCH]
    assert pool_calls == []
    assert context_calls == []
    assert activation_calls == []
    assert export_calls == []
    assert subprocess_calls == []
    assert all(key not in scan_module.os.environ for key in PRIVATE_SCAN_ENV_NAMES)
    combined_output = result.stdout + result.stderr
    assert "Traceback" not in combined_output
    for private_value in (nonce, proof, fingerprint):
        if private_value is not None:
            assert private_value not in combined_output
    for private_name in PRIVATE_SCAN_ENV_NAMES:
        assert private_name not in combined_output


def test_top3_scan_group_token_only_stays_healthy_direct_mode_without_proof(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    group_token = "recovery-authority-only"
    monkeypatch.setenv("MORPHIC_SCAN_GROUP_TOKEN", group_token)
    _set_private_scan_environment(
        monkeypatch,
        nonce=None,
        proof=None,
        fingerprint=None,
    )
    profiles = _authoritative_profiles()
    pool_calls: list[int] = []
    monkeypatch.setattr(
        scan_module,
        "get_top_n_analysis_profiles_by_level",
        lambda level: pool_calls.append(level) or profiles,
    )
    monkeypatch.setattr(scan_module, "resolve_operator_context", lambda: object())
    monkeypatch.setattr(scan_module, "resolve_topn_group_opt_in", lambda **_kwargs: None)
    monkeypatch.setattr(scan_module, "_collect_current_session_scan_files", lambda *_: [])
    _patch_post_processing(monkeypatch)
    _disable_command_logging_side_effects(monkeypatch)
    commands: list[list[str]] = []
    environments: list[dict[str, str]] = []
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        _successful_scan_run(commands, environments),
    )

    result = _invoke_top3_scan_cli(tmp_path)

    assert result.exit_code == 0, result.output
    assert pool_calls == [3]
    assert len(commands) == 10
    assert all(
        environment["MORPHIC_SCAN_GROUP_TOKEN"] == group_token
        for environment in environments
    )
    assert all(
        key not in environment
        for environment in environments
        for key in PRIVATE_SCAN_ENV_NAMES
    )
    assert all(key not in scan_module.os.environ for key in PRIVATE_SCAN_ENV_NAMES)


@pytest.mark.parametrize(
    "invalid_fingerprint",
    ["a" * 63, "A" * 64, "g" * 64],
    ids=["too-short", "uppercase", "non-hex"],
)
def test_top3_scan_rejects_invalid_expected_fingerprint_and_pops_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    invalid_fingerprint: str,
) -> None:
    profiles = _authoritative_profiles()
    _patch_scan_dependencies(monkeypatch, profiles)
    monkeypatch.setenv(EXPECTED_FINGERPRINT_ENV, invalid_fingerprint)
    commands: list[list[str]] = []
    activation_calls: list[str] = []
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        lambda command, **_kwargs: commands.append(list(command)),
    )
    monkeypatch.setattr(
        scan_module,
        "resolve_operator_context",
        lambda: activation_calls.append("context"),
    )

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=5)

    output = capsys.readouterr()
    assert captured.value.exit_code == 1
    assert commands == []
    assert activation_calls == []
    assert EXPECTED_FINGERPRINT_ENV not in scan_module.os.environ
    assert (
        "Scanprofil-Pool stimmt nicht mit der bestätigten Autorität überein."
        in output.err
    )
    assert invalid_fingerprint not in output.out + output.err


def test_top3_scan_rejects_mismatched_expected_fingerprint_before_subprocess(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profiles = _authoritative_profiles()
    actual = profile_sync.build_scan_profile_pool_fingerprint(3, profiles)
    mismatch = "0" * 64 if actual != "0" * 64 else "1" * 64
    _patch_scan_dependencies(monkeypatch, profiles)
    monkeypatch.setenv(EXPECTED_FINGERPRINT_ENV, mismatch)
    commands: list[list[str]] = []
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        lambda command, **_kwargs: commands.append(list(command)),
    )

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=5)

    assert captured.value.exit_code == 1
    assert commands == []
    assert EXPECTED_FINGERPRINT_ENV not in scan_module.os.environ


def test_top3_scan_matching_fingerprint_stays_private_and_preserves_phase1_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profiles = _authoritative_profiles()
    fingerprint = profile_sync.build_scan_profile_pool_fingerprint(3, profiles)
    _patch_scan_dependencies(monkeypatch, profiles)
    monkeypatch.setenv(EXPECTED_FINGERPRINT_ENV, fingerprint)
    commands: list[list[str]] = []
    environments: list[dict[str, str]] = []
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        _successful_scan_run(commands, environments),
    )

    _run_top3_scan(tmp_path, top_n=5, entropy_mode="hybrid")

    assert len(commands) == 10
    assert sum("--export" not in command for command in commands) == 5
    assert sum("--export" in command for command in commands) == 5
    assert len(environments) == 10
    assert all(EXPECTED_FINGERPRINT_ENV not in env for env in environments)
    assert all(env["ME_ENTROPY_MODE"] == "hybrid" for env in environments)
    assert EXPECTED_FINGERPRINT_ENV not in scan_module.os.environ


def test_top3_scan_rejects_top_n_larger_than_authoritative_pool(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    commands: list[list[str]] = []
    activation_calls: list[str] = []
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        lambda command, **_kwargs: commands.append(list(command)),
    )
    monkeypatch.setattr(
        scan_module,
        "resolve_operator_context",
        lambda: activation_calls.append("context"),
    )

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=9)

    output = capsys.readouterr()
    assert captured.value.exit_code == 1
    assert commands == []
    assert activation_calls == []
    assert "Top-N überschreitet den bestätigten Scanprofil-Pool." in output.err


def test_top3_scan_allows_top_n_equal_to_authoritative_pool_without_expected_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    monkeypatch.delenv(EXPECTED_FINGERPRINT_ENV, raising=False)
    commands: list[list[str]] = []
    monkeypatch.setattr(scan_module.subprocess, "run", _successful_scan_run(commands))

    _run_top3_scan(tmp_path, top_n=5)

    assert len(commands) == 10


def test_top3_scan_rejects_file_export_root_before_activation_or_subprocess(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    export_root = tmp_path / "existing-file"
    export_root.write_text("not a directory", encoding="utf-8")
    activation_calls: list[str] = []
    commands: list[list[str]] = []
    monkeypatch.setattr(
        scan_module,
        "resolve_operator_context",
        lambda: activation_calls.append("context"),
    )
    monkeypatch.setattr(scan_module.subprocess, "run", _successful_scan_run(commands))

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=5, export_path=export_root)

    output = capsys.readouterr()
    assert captured.value.exit_code == 1
    assert activation_calls == []
    assert commands == []
    assert "Export-Verzeichnis nicht verfügbar." in output.err
    assert str(export_root) not in output.out + output.err


def test_top3_scan_rejects_export_root_permission_error_before_activation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    export_root = tmp_path / "permission-denied"
    sensitive_path = r"C:\private\exports\denied"
    original_mkdir = Path.mkdir
    activation_calls: list[str] = []
    commands: list[list[str]] = []

    def guarded_mkdir(path: Path, *args, **kwargs):
        if path == export_root:
            raise PermissionError(sensitive_path)
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", guarded_mkdir)
    monkeypatch.setattr(
        scan_module,
        "resolve_operator_context",
        lambda: activation_calls.append("context"),
    )
    monkeypatch.setattr(scan_module.subprocess, "run", _successful_scan_run(commands))

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=5, export_path=export_root)

    output = capsys.readouterr()
    assert captured.value.exit_code == 1
    assert activation_calls == []
    assert commands == []
    assert "Export-Verzeichnis nicht verfügbar." in output.err
    assert sensitive_path not in output.out + output.err


def test_top3_scan_rejects_oversized_record_before_json_decode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    sensitive_detail = r"C:\private\records\oversized.json"
    commands: list[list[str]] = []

    def forbidden_json_decode(_payload: str):
        raise RuntimeError(sensitive_detail)

    def fake_run(command, **_kwargs):
        commands.append(list(command))
        monkeypatch.setattr(scan_module.json, "loads", forbidden_json_decode)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=SCREENING_RESULT_PREFIX + ("x" * (64 * 1024 + 1)) + "\n",
            stderr="",
        )

    monkeypatch.setattr(scan_module.subprocess, "run", fake_run)

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=5)

    output = capsys.readouterr()
    assert captured.value.exit_code == 1
    assert len(commands) == 1
    assert "Screening fehlgeschlagen." in output.err
    assert sensitive_detail not in output.out + output.err
    assert "Traceback" not in output.out + output.err


def test_top3_scan_normalizes_deeply_nested_record_recursion_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    commands: list[list[str]] = []
    nested_json = ("[" * 5000) + "0" + ("]" * 5000)

    def fake_run(command, **_kwargs):
        commands.append(list(command))
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=SCREENING_RESULT_PREFIX + nested_json + "\n",
            stderr="",
        )

    monkeypatch.setattr(scan_module.subprocess, "run", fake_run)

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=5)

    output = capsys.readouterr()
    assert captured.value.exit_code == 1
    assert len(commands) == 1
    assert "Screening fehlgeschlagen." in output.err
    assert "RecursionError" not in output.out + output.err
    assert "Traceback" not in output.out + output.err


@pytest.mark.parametrize(
    ("returncode", "stdout", "stderr", "failure"),
    [
        (
            7,
            SCREENING_RESULT_PREFIX
            + '{"version":1,"profile":"authority-profile-0","scores":[1,2,3,4,5]}\n',
            "",
            None,
        ),
        (7, "Export gespeichert\nHTML geschrieben: OK\n", "", None),
        (0, "Client score=9 und Fokus score=8\n", "", None),
        (
            0,
            SCREENING_RESULT_PREFIX
            + '{"version":1,"profile":"authority-profile-0","scores":[1,2,3,4,NaN]}\n',
            "",
            None,
        ),
        (
            0,
            SCREENING_RESULT_PREFIX
            + '{"version":1,"profile":"authority-profile-0","scores":[1,2,3,4,Infinity]}\n',
            "",
            None,
        ),
        (0, SCREENING_RESULT_PREFIX + "not-json\n", "", None),
        (
            0,
            SCREENING_RESULT_PREFIX
            + '{"version":1,"profile":"authority-profile-0","scores":[1,2,3,4,5]}\n'
            + SCREENING_RESULT_PREFIX
            + '{"version":1,"profile":"authority-profile-0","scores":[5,4,3,2,1]}\n',
            "",
            None,
        ),
        (
            0,
            "",
            SCREENING_RESULT_PREFIX
            + '{"version":1,"profile":"authority-profile-0","scores":[1,2,3,4,5]}\n',
            None,
        ),
        (
            0,
            SCREENING_RESULT_PREFIX
            + '{"version":1,"profile":"wrong-profile","scores":[1,2,3,4,5]}\n',
            "",
            None,
        ),
        (0, "", "", subprocess.TimeoutExpired(cmd=["scan"], timeout=120)),
        (0, "", "", RuntimeError(r"C:\private\screening\failure.json")),
    ],
    ids=[
        "nonzero-with-score",
        "nonzero-with-markers",
        "name-focus-score-forgery",
        "nan-score",
        "positive-infinity-score",
        "malformed-score",
        "duplicate-record",
        "stderr-record",
        "wrong-profile",
        "timeout",
        "exception",
    ],
)
def test_top3_scan_phase1_failure_is_immediate_and_prevents_phase2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    returncode: int,
    stdout: str,
    stderr: str,
    failure: Exception | None,
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    commands: list[list[str]] = []

    def fake_run(command, **_kwargs):
        commands.append(list(command))
        if failure is not None:
            raise failure
        return subprocess.CompletedProcess(
            command,
            returncode,
            stdout=stdout,
            stderr=stderr,
        )

    monkeypatch.setattr(scan_module.subprocess, "run", fake_run)

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=5)

    output = capsys.readouterr()
    assert captured.value.exit_code == 1
    assert len(commands) == 1
    assert all("--export" not in command for command in commands)
    assert "Screening fehlgeschlagen." in output.err
    assert "C:\\private" not in output.out + output.err


def test_top3_scan_one_partial_screening_failure_prevents_ranking_and_phase2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    commands: list[list[str]] = []

    def fake_run(command, **_kwargs):
        commands.append(list(command))
        profile = command[command.index("--profile") + 1]
        score_count = int(command[command.index("--top-k") + 1])
        stdout = (
            SCREENING_RESULT_PREFIX
            + json.dumps(
                {
                    "version": 1,
                    "profile": profile,
                    "scores": [float(score_count - index) for index in range(score_count)],
                },
                separators=(",", ":"),
            )
            + "\n"
            if len(commands) == 1
            else "no structured result\n"
        )
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

    monkeypatch.setattr(scan_module.subprocess, "run", fake_run)

    with pytest.raises(typer.Exit):
        _run_top3_scan(tmp_path, top_n=5)

    output = capsys.readouterr()
    assert len(commands) == 2
    assert all("--export" not in command for command in commands)
    assert "[OK] TOP-5 RELEVANTE PROFILE" not in output.out
    assert "ANALYSE ZUSAMMENFASSUNG" not in output.out


def test_top3_scan_all_screening_failure_has_no_ok_header_or_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(
            command,
            0,
            stdout="Export gespeichert\n",
            stderr="",
        ),
    )

    with pytest.raises(typer.Exit):
        _run_top3_scan(tmp_path, top_n=5)

    output = capsys.readouterr()
    assert "[OK] TOP-5 RELEVANTE PROFILE" not in output.out
    assert "ANALYSE ZUSAMMENFASSUNG" not in output.out


@pytest.mark.parametrize(
    ("returncode", "stdout", "failure"),
    [
        (
            9,
            "Export gespeichert: result.json\nHTML-Report gespeichert: result.html\n",
            None,
        ),
        (0, "HTML geschrieben: FEHLER -> x_multiplex_scan.html\n", None),
        (0, "HTML-Report gespeichert: result.html\n", None),
        (0, "Export gespeichert: result.json\n", None),
        (0, "", subprocess.TimeoutExpired(cmd=["scan"], timeout=600)),
        (0, "", RuntimeError(r"C:\private\phase2\failure.json")),
    ],
    ids=[
        "nonzero-with-markers",
        "html-error-path",
        "missing-json-marker",
        "missing-html-marker",
        "timeout",
        "exception",
    ],
)
def test_top3_scan_phase2_failure_is_immediate_and_fails_outer_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    returncode: int,
    stdout: str,
    failure: Exception | None,
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    commands: list[list[str]] = []

    def fake_run(command, **_kwargs):
        commands.append(list(command))
        if "--export" not in command:
            profile = command[command.index("--profile") + 1]
            score_count = int(command[command.index("--top-k") + 1])
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=(
                    SCREENING_RESULT_PREFIX
                    + json.dumps(
                        {
                            "version": 1,
                            "profile": profile,
                            "scores": [float(score_count - index) for index in range(score_count)],
                        },
                        separators=(",", ":"),
                    )
                    + "\n"
                ),
                stderr="",
            )
        if failure is not None:
            raise failure
        return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="")

    monkeypatch.setattr(scan_module.subprocess, "run", fake_run)

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=5)

    output = capsys.readouterr()
    assert captured.value.exit_code == 1
    assert len(commands) == 6
    assert sum("--export" in command for command in commands) == 1
    assert "Vollständige Profilanalyse fehlgeschlagen." in output.err
    assert "[Debug]" not in output.out + output.err
    assert "C:\\private" not in output.out + output.err
    assert "ANALYSE ZUSAMMENFASSUNG" not in output.out


def test_top3_scan_partial_phase2_failure_has_no_outer_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    commands: list[list[str]] = []
    phase2_calls = 0
    residual_artifacts: list[tuple[Path, Path]] = []
    successful = _successful_scan_run([], artifacts=residual_artifacts)

    def fake_run(command, **_kwargs):
        nonlocal phase2_calls
        commands.append(list(command))
        if "--export" not in command:
            return successful(command)
        phase2_calls += 1
        if phase2_calls == 1:
            return successful(command)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="Export gespeichert: result.json\n",
            stderr="",
        )

    monkeypatch.setattr(scan_module.subprocess, "run", fake_run)

    with pytest.raises(typer.Exit):
        _run_top3_scan(tmp_path, top_n=5)

    output = capsys.readouterr()
    assert len(commands) == 7
    assert phase2_calls == 2
    assert "ANALYSE ZUSAMMENFASSUNG" not in output.out
    assert len(residual_artifacts) == 1
    assert all(path.is_file() for path in residual_artifacts[0])


def test_top3_scan_activation_resolution_failure_is_redacted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    sensitive_path = r"C:\private\activation\root.handle"
    monkeypatch.setattr(
        scan_module,
        "resolve_operator_context",
        lambda: (_ for _ in ()).throw(RuntimeError(sensitive_path)),
    )
    commands: list[list[str]] = []
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        lambda command, **_kwargs: commands.append(list(command)),
    )

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=5)

    output = capsys.readouterr()
    assert captured.value.exit_code == 1
    assert commands == []
    assert "Scan-Aktivierung nicht verfügbar." in output.err
    assert sensitive_path not in output.out + output.err


def test_top3_scan_child_environment_failure_is_redacted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    sensitive_path = r"C:\private\activation\child.handle"
    monkeypatch.setattr(
        scan_module,
        "build_topn_child_process_environment",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError(sensitive_path)),
    )
    commands: list[list[str]] = []
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        lambda command, **_kwargs: commands.append(list(command)),
    )

    with pytest.raises(typer.Exit) as captured:
        _run_top3_scan(tmp_path, top_n=5)

    output = capsys.readouterr()
    assert captured.value.exit_code == 1
    assert commands == []
    assert "Scan-Aktivierung nicht verfügbar." in output.err
    assert sensitive_path not in output.out + output.err


def test_top3_scan_creates_export_root_directory_even_with_json_suffix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_scan_dependencies(monkeypatch, _authoritative_profiles(5))
    export_root = tmp_path / "result.json"
    commands: list[list[str]] = []

    def fake_run(command, **kwargs):
        if "--export" in command:
            assert export_root.is_dir()
        return _successful_scan_run(commands)(command, **kwargs)

    monkeypatch.setattr(scan_module.subprocess, "run", fake_run)

    _run_top3_scan(tmp_path, top_n=5, export_path=export_root)

    assert export_root.is_dir()
    assert len(commands) == 10


def test_top3_scan_cli_runner_returns_nonzero_for_authority_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.cli.main import app

    sensitive_path = r"C:\private\profiles\cli-authority.json"
    monkeypatch.setattr(
        scan_module,
        "get_top_n_analysis_profiles_by_level",
        lambda _level: (_ for _ in ()).throw(
            profile_sync.ProfileAuthorityError(sensitive_path)
        ),
    )
    commands: list[list[str]] = []
    monkeypatch.setattr(
        scan_module.subprocess,
        "run",
        lambda command, **_kwargs: commands.append(list(command)),
    )

    result = CliRunner().invoke(
        app,
        [
            "scan",
            "top3-scan",
            "Test",
            "Gate3",
            "--birth-date",
            "01011990",
            "--birth-place",
            "Berlin",
            "--top-n",
            "5",
        ],
    )

    assert result.exit_code == 1
    assert commands == []
    assert "Scanprofil-Pool nicht verfügbar." in result.output
    assert sensitive_path not in result.output
