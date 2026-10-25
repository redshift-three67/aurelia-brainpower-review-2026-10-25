from __future__ import annotations

import hashlib

import pytest

from core.compliance.run_manifest import build_run_manifest


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def test_run_manifest_is_deterministic_pseudonymous_and_hash_complete() -> None:
    kwargs = {
        "run_id": "run-001",
        "created_at": "2026-07-10T20:00:00Z",
        "commit": "619a1f5485a1",
        "tenant_id": "ws-synthetic",
        "client_id": "cli-synthetic",
        "profile_hashes": {"profile-default": _digest("profile")},
        "data_hashes": {"groups": _digest("groups")},
        "seed_mode": "deterministic",
        "parameter_version": "v1",
        "artifact_hashes": {"result.json": _digest("result")},
    }

    manifest = build_run_manifest(**kwargs)

    assert manifest == build_run_manifest(**kwargs)
    assert manifest["schema_version"] == 1
    assert manifest["run_id"] == "run-001"
    assert manifest["software"] == {"commit": "619a1f5485a1"}
    assert manifest["identity"] == {
        "tenant_id": "ws-synthetic",
        "client_id": "cli-synthetic",
    }
    assert manifest["inputs"]["seed_mode"] == "deterministic"
    assert manifest["inputs"]["parameter_version"] == "v1"
    assert manifest["artifacts"] == {"result.json": _digest("result")}
    assert len(manifest["manifest_sha256"]) == 64
    assert "first_name" not in str(manifest)
    assert "last_name" not in str(manifest)
    assert "birth_date" not in str(manifest)


def test_run_manifest_rejects_noncanonical_identity_and_invalid_hashes() -> None:
    kwargs = {
        "run_id": "run-001",
        "created_at": "2026-07-10T20:00:00Z",
        "commit": "619a1f5485a1",
        "tenant_id": "ws-synthetic",
        "client_id": "cli-synthetic",
        "profile_hashes": {"profile-default": _digest("profile")},
        "data_hashes": {"groups": _digest("groups")},
        "seed_mode": "deterministic",
        "parameter_version": "v1",
    }

    with pytest.raises(ValueError, match="canonical"):
        build_run_manifest(**{**kwargs, "client_id": "Synthetic Person"})
    with pytest.raises(ValueError, match="sha256"):
        build_run_manifest(**{**kwargs, "artifact_hashes": {"result.json": "not-a-hash"}})
