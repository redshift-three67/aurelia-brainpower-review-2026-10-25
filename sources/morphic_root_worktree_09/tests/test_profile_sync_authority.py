from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from core import profile_sync
from core.profile_sync import (
    SCAN_PROCESS_GATE_NONCE_ENV,
    SCAN_PROCESS_GATE_PROOF_ENV,
    build_scan_process_gate_proof,
)


class _StrSubclass(str):
    pass


def test_scan_process_gate_proof_is_stable_and_domain_bound() -> None:
    nonce = "a" * 64
    fingerprint = "b" * 64

    proof = build_scan_process_gate_proof(nonce, fingerprint)
    expected = hashlib.sha256(
        b"morphic-scan-process-gate-v1\0"
        + nonce.encode("ascii")
        + b"\0"
        + fingerprint.encode("utf-8")
    ).hexdigest()
    wrong_domain = hashlib.sha256(
        b"morphic-scan-process-gate-v2\0"
        + nonce.encode("ascii")
        + b"\0"
        + fingerprint.encode("utf-8")
    ).hexdigest()

    assert re.fullmatch(r"[0-9a-f]{64}", proof)
    assert proof == expected
    assert proof == build_scan_process_gate_proof(nonce, fingerprint)
    assert proof != wrong_domain
    assert proof != build_scan_process_gate_proof("c" * 64, fingerprint)
    assert proof != build_scan_process_gate_proof(nonce, "d" * 64)
    assert SCAN_PROCESS_GATE_NONCE_ENV == "MORPHIC_SCAN_PROCESS_GATE_NONCE"
    assert SCAN_PROCESS_GATE_PROOF_ENV == "MORPHIC_SCAN_PROCESS_GATE_PROOF"


@pytest.mark.parametrize(
    "nonce",
    [
        "",
        "a" * 63,
        "a" * 65,
        "A" * 64,
        "g" * 64,
        None,
        True,
        [],
        _StrSubclass("a" * 64),
    ],
)
def test_scan_process_gate_proof_rejects_invalid_nonce(nonce: object) -> None:
    with pytest.raises(profile_sync.ProfileAuthorityError) as captured:
        build_scan_process_gate_proof(nonce, "b" * 64)

    assert str(captured.value) == "Scan process proof is invalid."


@pytest.mark.parametrize(
    "fingerprint",
    [None, True, [], b"fingerprint", _StrSubclass("fingerprint"), "x" * 129],
)
def test_scan_process_gate_proof_rejects_invalid_fingerprint(
    fingerprint: object,
) -> None:
    with pytest.raises(profile_sync.ProfileAuthorityError) as captured:
        build_scan_process_gate_proof("a" * 64, fingerprint)

    assert str(captured.value) == "Scan process proof is invalid."


@pytest.mark.parametrize("fingerprint", ["", "not-authority-syntax", "ä" * 128])
def test_scan_process_gate_proof_accepts_builder_opaque_fingerprint(
    fingerprint: str,
) -> None:
    assert re.fullmatch(
        r"[0-9a-f]{64}",
        build_scan_process_gate_proof("a" * 64, fingerprint),
    )


def test_scan_process_gate_proof_normalizes_utf8_encoding_failure() -> None:
    fingerprint = "private\ud800value"

    with pytest.raises(profile_sync.ProfileAuthorityError) as captured:
        build_scan_process_gate_proof("a" * 64, fingerprint)

    assert str(captured.value) == "Scan process proof is invalid."
    assert "private" not in str(captured.value)


@pytest.mark.parametrize(
    "max_level",
    [True, False, 3.0, "3", None, 0, 6],
)
def test_top_n_profile_authority_rejects_invalid_max_level(max_level: object) -> None:
    error_type = getattr(profile_sync, "ProfileAuthorityError", None)
    assert error_type is not None

    with pytest.raises(error_type):
        profile_sync.get_top_n_analysis_profiles_by_level(max_level)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("name", "display_name"),
    [
        (None, "Label"),
        ("id", None),
        (" ", "Label"),
        ("id", "\t"),
        (7, "Label"),
        ("id", False),
    ],
)
def test_top_n_profile_authority_validates_generated_pool(
    monkeypatch: pytest.MonkeyPatch,
    name: object,
    display_name: object,
) -> None:
    error_type = getattr(profile_sync, "ProfileAuthorityError", None)
    assert error_type is not None
    monkeypatch.setattr(
        profile_sync,
        "get_profiles_up_to_level",
        lambda _max_level: [SimpleNamespace(name=name, display_name=display_name)],
    )

    with pytest.raises(error_type):
        profile_sync.get_top_n_analysis_profiles_by_level(3)


def test_top_n_profile_authority_rejects_duplicate_generated_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error_type = getattr(profile_sync, "ProfileAuthorityError", None)
    assert error_type is not None
    monkeypatch.setattr(
        profile_sync,
        "get_profiles_up_to_level",
        lambda _max_level: [
            SimpleNamespace(name="duplicate", display_name="First"),
            SimpleNamespace(name="duplicate", display_name="Second"),
        ],
    )

    with pytest.raises(error_type):
        profile_sync.get_top_n_analysis_profiles_by_level(3)


@pytest.mark.parametrize(
    "profiles",
    [
        [("A", "Uppercase")],
        [("A", "Uppercase"), ("a", "Lowercase")],
        [(" leading", "Leading whitespace")],
        [("trailing ", "Trailing whitespace")],
        [("path/profile", "Slash")],
        [("nul\x00profile", "NUL")],
        [("dot.profile", "Dot")],
    ],
    ids=[
        "uppercase",
        "case-equivalent",
        "leading-space",
        "trailing-space",
        "slash",
        "nul",
        "dot",
    ],
)
def test_profile_pool_rejects_noncanonical_cli_unsafe_ids(
    profiles: list[tuple[str, str]],
) -> None:
    with pytest.raises(profile_sync.ProfileAuthorityError):
        profile_sync.validate_scan_profile_pool(3, profiles)


def test_profile_pool_rejects_label_that_is_not_utf8_encodable() -> None:
    with pytest.raises(profile_sync.ProfileAuthorityError) as captured:
        profile_sync.validate_scan_profile_pool(3, [("valid", "\ud800")])

    assert str(captured.value) == "Profile authority returned an invalid pool."


def test_profile_pool_fingerprint_wraps_canonicalization_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sensitive_detail = r"C:\private\profiles\canonical.json"

    def fail_canonicalization(*_args: object, **_kwargs: object):
        raise RuntimeError(sensitive_detail)

    monkeypatch.setattr(profile_sync.json, "dumps", fail_canonicalization)

    with pytest.raises(profile_sync.ProfileAuthorityError) as captured:
        profile_sync.build_scan_profile_pool_fingerprint(
            3,
            [("valid", "Valid")],
        )

    assert str(captured.value) == "Profile authority returned an invalid pool."
    assert sensitive_detail not in str(captured.value)


def test_top_n_profile_authority_redacts_internal_provider_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sensitive_detail = r"C:\private\profiles\provider.json"

    def fail_provider(_max_level: int):
        raise OSError(sensitive_detail)

    monkeypatch.setattr(profile_sync, "get_profiles_up_to_level", fail_provider)

    with pytest.raises(profile_sync.ProfileAuthorityError) as captured:
        profile_sync.get_top_n_analysis_profiles_by_level(3)

    assert str(captured.value) == "Profile authority is unavailable."
    assert sensitive_detail not in str(captured.value)


@pytest.mark.parametrize(
    (
        "failed_import_call",
        "available_level",
        "available_count",
        "blocked_level",
        "expected_provider_calls",
    ),
    [
        (1, 3, 55, 4, 1),
        (2, 4, 208, 5, 2),
    ],
    ids=["level-4-registration", "level-5-registration"],
)
def test_auto_registration_import_failure_is_level_scoped_and_fail_closed(
    failed_import_call: int,
    available_level: int,
    available_count: int,
    blocked_level: int,
    expected_provider_calls: int,
) -> None:
    script = textwrap.dedent(
        f"""
        import builtins
        import json

        original_import = builtins.__import__
        provider_import_calls = 0

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            global provider_import_calls
            if name == "core.subgroups.procedural_groups":
                provider_import_calls += 1
                if provider_import_calls == {failed_import_call}:
                    raise ImportError("C:/private/profiles/sensitive-provider.py")
            return original_import(name, globals, locals, fromlist, level)

        builtins.__import__ = guarded_import
        import core.profile_sync as profile_sync

        available = profile_sync.get_top_n_analysis_profiles_by_level({available_level})
        try:
            profile_sync.get_top_n_analysis_profiles_by_level({blocked_level})
        except profile_sync.ProfileAuthorityError as exc:
            result = {{
                "available_count": len(available),
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "provider_import_calls": provider_import_calls,
                "level_4_registered": len(profile_sync.get_profiles_by_level(4)),
                "level_5_registered": len(profile_sync.get_profiles_by_level(5)),
            }}
        else:
            result = {{"error_type": None}}
        print(json.dumps(result))
        """
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    result = json.loads(completed.stdout)

    assert result["available_count"] == available_count
    assert result["error_type"] == "ProfileAuthorityError"
    assert result["error_message"] == "Profile authority is unavailable."
    assert "private" not in result["error_message"].lower()
    assert result["provider_import_calls"] == expected_provider_calls
    assert result["level_5_registered"] == 0
    if blocked_level == 4:
        assert result["level_4_registered"] == 0


@pytest.mark.parametrize(
    "inventory",
    [
        [],
        [f"group_{index}" for index in range(450)],
    ],
    ids=["empty", "no-fein-groups"],
)
def test_invalid_or_zero_fein_inventory_blocks_level_4_and_skips_level_5(
    inventory: list[str],
) -> None:
    script = textwrap.dedent(
        f"""
        import json
        from core.subgroups import procedural_groups

        procedural_groups.list_groups = lambda strict=False: {inventory!r}
        import core.profile_sync as profile_sync

        level_3 = profile_sync.get_top_n_analysis_profiles_by_level(3)
        try:
            profile_sync.get_top_n_analysis_profiles_by_level(4)
        except profile_sync.ProfileAuthorityError as exc:
            result = {{
                "level_3_count": len(level_3),
                "error": str(exc),
                "level_4_registered": len(profile_sync.get_profiles_by_level(4)),
                "level_5_registered": len(profile_sync.get_profiles_by_level(5)),
            }}
        else:
            result = {{"error": None}}
        print(json.dumps(result))
        """
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    result = json.loads(completed.stdout)

    assert result == {
        "level_3_count": 55,
        "error": "Profile authority is unavailable.",
        "level_4_registered": 0,
        "level_5_registered": 0,
    }


def test_level_4_stages_registrations_before_publication() -> None:
    inventory = [f"staged_{index}_fein" for index in range(450)]
    script = textwrap.dedent(
        f"""
        import json
        from core.subgroups import procedural_groups
        import core.profile_sync as profile_sync

        before = set(profile_sync.MASTER_PROFILES)
        procedural_groups.list_groups = lambda strict=False: {inventory!r}
        calls = 0

        def fail_during_staging(_group_name):
            global calls
            calls += 1
            if calls == 2:
                raise RuntimeError("C:/private/groups/staging.json")
            return []

        profile_sync._get_related_remedy_groups = fail_during_staging
        profile_sync._LEVEL_4_AUTO_REGISTRATION_READY = True
        try:
            count = profile_sync._auto_register_fein_profiles()
            error_type = None
        except Exception as exc:
            count = None
            error_type = type(exc).__name__
        after = set(profile_sync.MASTER_PROFILES)
        print(json.dumps({{
            "count": count,
            "error_type": error_type,
            "ready": profile_sync._LEVEL_4_AUTO_REGISTRATION_READY,
            "leaked": sorted(after - before),
        }}))
        """
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert json.loads(completed.stdout) == {
        "count": 0,
        "error_type": None,
        "ready": False,
        "leaked": [],
    }


def test_zero_remaining_level_5_registrations_marks_readiness_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(profile_sync, "_LEVEL_5_AUTO_REGISTRATION_READY", True)

    assert profile_sync._auto_register_all_groups_as_profiles() == 0
    assert profile_sync._LEVEL_5_AUTO_REGISTRATION_READY is False


def test_healthy_level_4_pool_count_order_and_fingerprint_remain_stable() -> None:
    profiles = profile_sync.get_top_n_analysis_profiles_by_level(4)
    level_5_profiles = profile_sync.get_top_n_analysis_profiles_by_level(5)

    assert len(profiles) == 208
    assert len(level_5_profiles) == 502
    assert profile_sync.build_scan_profile_pool_fingerprint(4, profiles) == (
        "aaa6c20978c13bfc2fce19716eba0ebb0c837431bee6c875984394992b090f7f"
    )
