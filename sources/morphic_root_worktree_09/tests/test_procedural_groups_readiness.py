from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from core.subgroups import procedural_groups


def _run_fresh_script(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(script)],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_import_does_not_configure_application_logging() -> None:
    completed = _run_fresh_script(
        """
        import json
        import logging

        before = len(logging.getLogger().handlers)
        from core.subgroups import procedural_groups
        after = len(logging.getLogger().handlers)
        print(json.dumps({"before": before, "after": after}))
        """
    )

    assert json.loads(completed.stdout) == {"before": 0, "after": 0}


def test_optional_import_warning_does_not_log_raw_exception_detail() -> None:
    sensitive_detail = "C:/private/groups/extended-provider.py"
    completed = _run_fresh_script(
        f"""
        import builtins
        import json

        original_import = builtins.__import__

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if fromlist and "groups_extended" in fromlist:
                raise ImportError({sensitive_detail!r})
            return original_import(name, globals, locals, fromlist, level)

        builtins.__import__ = guarded_import
        from core.subgroups import procedural_groups
        print(json.dumps({{
            "available": procedural_groups.GROUPS_EXTENDED_AVAILABLE,
        }}))
        """
    )

    assert json.loads(completed.stdout) == {"available": False}
    assert sensitive_detail not in completed.stderr


@pytest.mark.parametrize(
    "flag_name",
    [
        "GROUPS_EXTENDED_AVAILABLE",
        "GROUPS_EXTENDED_V2_AVAILABLE",
        "GROUPS_PHASE4_AVAILABLE",
        "GROUPS_PHASE5_AVAILABLE",
    ],
)
def test_strict_group_provider_rejects_missing_required_provider_flag(
    flag_name: str,
) -> None:
    completed = _run_fresh_script(
        f"""
        import json
        from core.subgroups import procedural_groups

        procedural_groups.{flag_name} = False
        try:
            procedural_groups.list_groups(strict=True)
        except Exception as exc:
            result = {{"type": type(exc).__name__, "message": str(exc)}}
        else:
            result = {{"type": None}}
        print(json.dumps(result))
        """
    )

    assert json.loads(completed.stdout) == {
        "type": "ProceduralGroupReadinessError",
        "message": "Procedural group provider is unavailable.",
    }


def test_strict_group_provider_rejects_bat_import_failure_without_raw_detail() -> None:
    sensitive_detail = "C:/private/groups/bat-provider.py"
    completed = _run_fresh_script(
        f"""
        import builtins
        import json
        from core.subgroups import procedural_groups

        original_import = builtins.__import__

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name.endswith("bat_groups") or (fromlist and "bat_groups" in fromlist):
                raise ImportError({sensitive_detail!r})
            return original_import(name, globals, locals, fromlist, level)

        builtins.__import__ = guarded_import
        try:
            procedural_groups.list_groups(strict=True)
        except Exception as exc:
            result = {{"type": type(exc).__name__, "message": str(exc)}}
        else:
            result = {{"type": None}}
        print(json.dumps(result))
        """
    )

    assert json.loads(completed.stdout) == {
        "type": "ProceduralGroupReadinessError",
        "message": "Procedural group provider is unavailable.",
    }
    assert sensitive_detail not in completed.stderr


def _assert_strict_inventory_rejected() -> None:
    with pytest.raises(Exception) as captured:
        procedural_groups.list_groups(strict=True)
    assert type(captured.value).__name__ == "ProceduralGroupReadinessError"
    assert str(captured.value) == "Procedural group provider is unavailable."


def test_strict_group_provider_rejects_empty_inventory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from core.subgroups import bat_groups

    monkeypatch.setattr(procedural_groups, "_GROUP_LABELS", {})
    monkeypatch.setattr(procedural_groups, "_DYNAMIC_GROUPS", [])
    monkeypatch.setattr(bat_groups, "list_bat_groups", lambda: [])

    _assert_strict_inventory_rejected()


def test_strict_group_provider_rejects_subset_inventory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    labels = dict(procedural_groups._GROUP_LABELS)
    labels.pop(next(iter(labels)))
    monkeypatch.setattr(procedural_groups, "_GROUP_LABELS", labels)

    _assert_strict_inventory_rejected()


def test_strict_group_provider_rejects_invalid_inventory_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        procedural_groups,
        "_DYNAMIC_GROUPS",
        [*procedural_groups._DYNAMIC_GROUPS, None],
    )

    _assert_strict_inventory_rejected()


def test_strict_group_provider_rejects_duplicate_inventory_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    duplicate = next(iter(procedural_groups._GROUP_LABELS))
    monkeypatch.setattr(
        procedural_groups,
        "_DYNAMIC_GROUPS",
        [*procedural_groups._DYNAMIC_GROUPS, duplicate],
    )

    _assert_strict_inventory_rejected()


def test_healthy_strict_group_inventory_preserves_default_order_and_count() -> None:
    default_groups = procedural_groups.list_groups()
    strict_groups = procedural_groups.list_groups(strict=True)

    assert strict_groups == default_groups
    assert len(strict_groups) == 450
