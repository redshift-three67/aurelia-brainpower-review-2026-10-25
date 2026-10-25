"""Pure, additive builder for versioned pseudonymous run manifests.

The builder deliberately has no connection to scan execution, report writers, or
runtime stores. Wiring it into a productive run is a later Phase-4 gate.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Mapping


_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_ARTIFACT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,255}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{7,64}$")


def _canonical(value: str, label: str) -> str:
    cleaned = str(value or "").strip()
    if not _SEGMENT.fullmatch(cleaned):
        raise ValueError(f"{label} must be canonical")
    return cleaned


def _timestamp(value: str) -> str:
    cleaned = str(value or "").strip()
    try:
        datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("created_at must be an ISO-8601 timestamp") from exc
    return cleaned


def _hashes(values: Mapping[str, str] | None, *, artifact_names: bool = False) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_name, raw_digest in sorted((values or {}).items()):
        name = str(raw_name or "").strip()
        name_pattern = _ARTIFACT_NAME if artifact_names else _SEGMENT
        if not name_pattern.fullmatch(name):
            raise ValueError("hash entry name must be canonical")
        digest = str(raw_digest or "").strip().lower()
        if not _SHA256.fullmatch(digest):
            raise ValueError("hash entry must be a sha256 digest")
        result[name] = digest
    return result


def _manifest_sha256(manifest: dict[str, object]) -> str:
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_run_manifest(
    *,
    run_id: str,
    created_at: str,
    commit: str,
    tenant_id: str,
    client_id: str,
    profile_hashes: Mapping[str, str],
    data_hashes: Mapping[str, str],
    seed_mode: str,
    parameter_version: str,
    artifact_hashes: Mapping[str, str] | None = None,
) -> dict[str, object]:
    """Build a deterministic manifest without accepting client cleartext fields."""
    resolved_commit = str(commit or "").strip().lower()
    if not _COMMIT.fullmatch(resolved_commit):
        raise ValueError("commit must be a lowercase git hash")
    manifest: dict[str, object] = {
        "schema_version": 1,
        "run_id": _canonical(run_id, "run_id"),
        "created_at": _timestamp(created_at),
        "software": {"commit": resolved_commit},
        "identity": {
            "tenant_id": _canonical(tenant_id, "tenant_id"),
            "client_id": _canonical(client_id, "client_id"),
        },
        "inputs": {
            "profile_hashes": _hashes(profile_hashes),
            "data_hashes": _hashes(data_hashes),
            "seed_mode": _canonical(seed_mode, "seed_mode"),
            "parameter_version": _canonical(parameter_version, "parameter_version"),
        },
        "artifacts": _hashes(artifact_hashes, artifact_names=True),
    }
    manifest["manifest_sha256"] = _manifest_sha256(manifest)
    return manifest
