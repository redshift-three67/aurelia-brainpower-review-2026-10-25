from __future__ import annotations

import sys

import pytest

from core.compliance.windows_protection import (
    current_windows_username,
    protect_for_current_user,
    restrict_directory_to_current_user,
    unprotect_for_current_user,
)


pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-only DPAPI/ACL gate")


def test_dpapi_roundtrip_protects_only_synthetic_payload() -> None:
    payload = b"synthetic-phase3-payload"

    protected = protect_for_current_user(payload, description="morphic-phase3-test")

    assert protected != payload
    assert unprotect_for_current_user(protected) == payload


def test_current_user_acl_is_applied_only_to_temporary_directory(tmp_path) -> None:
    protected_root = tmp_path / "synthetic-sensitive-runtime"
    protected_root.mkdir()
    (protected_root / "synthetic.txt").write_text("synthetic-only", encoding="utf-8")

    acl_listing = restrict_directory_to_current_user(protected_root)

    assert protected_root.exists()
    assert current_windows_username().casefold() in acl_listing.casefold()
    assert "synthetic-only" == (protected_root / "synthetic.txt").read_text(encoding="utf-8")
