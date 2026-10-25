"""Offline audit-integrity contracts for Admin Catalog F2.4.

This module classifies the existing database hash chain honestly and provides
pure HMAC-SHA-256 audit-head receipts with explicitly injected keys. It performs
no database, environment, network, runtime, or key-provider I/O.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Mapping


CONSISTENCY_ONLY = "consistency_only"
HMAC_SHA256 = "hmac_sha256"
_HMAC_ALGORITHM = "HMAC-SHA256"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_MINIMUM_HMAC_KEY_BYTES = 32


class IntegrityConfigurationError(ValueError):
    """Audit-integrity configuration is missing or unsafe."""


@dataclass(frozen=True, slots=True)
class IntegrityAssessment:
    level: str
    chain_valid: bool
    tamper_resistant: bool
    explanation: str


@dataclass(frozen=True, slots=True)
class AuditHeadReceipt:
    tenant_id: str
    last_sequence: int
    last_hash: str
    policy_version: str
    issued_at: str
    key_version: str
    algorithm: str
    signature: str

    def to_mapping(self) -> dict[str, object]:
        """Return public receipt fields; the injected key is never retained."""

        return asdict(self)


def _clean_required(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _validate_sequence(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("last_sequence must be a non-negative integer")
    return value


def _validate_hash(value: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise ValueError("last_hash must be a lowercase SHA-256 hex digest")
    return value


def _validate_key(key: bytes | None) -> bytes:
    if not isinstance(key, bytes) or len(key) < _MINIMUM_HMAC_KEY_BYTES:
        raise IntegrityConfigurationError(
            f"HMAC key must be bytes with at least {_MINIMUM_HMAC_KEY_BYTES} bytes"
        )
    return key


def _canonical_payload(receipt: AuditHeadReceipt) -> bytes:
    payload = receipt.to_mapping()
    payload.pop("signature")
    return json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _signature(receipt: AuditHeadReceipt, key: bytes) -> str:
    return hmac.new(key, _canonical_payload(receipt), hashlib.sha256).hexdigest()


def assess_consistency_chain(*, valid: bool) -> IntegrityAssessment:
    """Classify the existing unhashed-key database chain without overclaiming."""

    if not isinstance(valid, bool):
        raise ValueError("valid must be boolean")
    return IntegrityAssessment(
        level=CONSISTENCY_ONLY,
        chain_valid=valid,
        tamper_resistant=False,
        explanation=(
            "Database hash-chain consistency check only; without an external key "
            "this does not prove tamper resistance."
        ),
    )


def issue_audit_head_receipt(
    *,
    tenant_id: str,
    last_sequence: int,
    last_hash: str,
    policy_version: str,
    issued_at: datetime,
    key_version: str,
    key: bytes | None,
) -> AuditHeadReceipt:
    """Create a deterministic public receipt signed by an injected secret key."""

    tenant = _clean_required(tenant_id, "tenant_id")
    sequence = _validate_sequence(last_sequence)
    head_hash = _validate_hash(last_hash)
    policy = _clean_required(policy_version, "policy_version")
    version = _clean_required(key_version, "key_version")
    if not isinstance(issued_at, datetime) or issued_at.tzinfo is None:
        raise ValueError("issued_at must be a timezone-aware datetime")
    signing_key = _validate_key(key)
    unsigned = AuditHeadReceipt(
        tenant_id=tenant,
        last_sequence=sequence,
        last_hash=head_hash,
        policy_version=policy,
        issued_at=issued_at.astimezone(UTC).isoformat(),
        key_version=version,
        algorithm=_HMAC_ALGORITHM,
        signature="",
    )
    return AuditHeadReceipt(**{**unsigned.to_mapping(), "signature": _signature(unsigned, signing_key)})


def verify_audit_head_receipt(
    receipt: AuditHeadReceipt,
    keys_by_version: Mapping[str, bytes],
) -> bool:
    """Verify against exactly the non-secret key version declared by the receipt."""

    if not isinstance(receipt, AuditHeadReceipt) or receipt.algorithm != _HMAC_ALGORITHM:
        return False
    try:
        _clean_required(receipt.tenant_id, "tenant_id")
        _validate_sequence(receipt.last_sequence)
        _validate_hash(receipt.last_hash)
        _clean_required(receipt.policy_version, "policy_version")
        _clean_required(receipt.key_version, "key_version")
        parsed_time = datetime.fromisoformat(receipt.issued_at)
        if parsed_time.tzinfo is None:
            return False
        if _SHA256_RE.fullmatch(receipt.signature) is None:
            return False
        key = _validate_key(keys_by_version.get(receipt.key_version))
    except (AttributeError, TypeError, ValueError):
        return False
    expected = _signature(
        AuditHeadReceipt(**{**receipt.to_mapping(), "signature": ""}),
        key,
    )
    return hmac.compare_digest(receipt.signature, expected)


def select_admin_integrity_level(*, production_mode: bool, key: bytes | None) -> str:
    """Fail closed for a future production admin mode instead of downgrading."""

    if not isinstance(production_mode, bool):
        raise ValueError("production_mode must be boolean")
    if key is None:
        if production_mode:
            raise IntegrityConfigurationError(
                "HMAC key is required for production admin integrity"
            )
        return CONSISTENCY_ONLY
    _validate_key(key)
    return HMAC_SHA256


__all__ = [
    "CONSISTENCY_ONLY",
    "HMAC_SHA256",
    "AuditHeadReceipt",
    "IntegrityAssessment",
    "IntegrityConfigurationError",
    "assess_consistency_chain",
    "issue_audit_head_receipt",
    "select_admin_integrity_level",
    "verify_audit_head_receipt",
]
