from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from core.admin_catalog.audit_integrity import (
    CONSISTENCY_ONLY,
    HMAC_SHA256,
    AuditHeadReceipt,
    IntegrityConfigurationError,
    assess_consistency_chain,
    issue_audit_head_receipt,
    select_admin_integrity_level,
    verify_audit_head_receipt,
)


SYNTHETIC_KEY_V1 = b"synthetic-audit-key-v1-32-bytes!!"
SYNTHETIC_KEY_V2 = b"synthetic-audit-key-v2-32-bytes!!"
HEAD_HASH = "a" * 64
ISSUED_AT = datetime(2026, 7, 13, 12, 30, tzinfo=UTC)


def _receipt() -> AuditHeadReceipt:
    return issue_audit_head_receipt(
        tenant_id="tenant-a",
        last_sequence=7,
        last_hash=HEAD_HASH,
        policy_version="audit-head-v1",
        issued_at=ISSUED_AT,
        key_version="key-v1",
        key=SYNTHETIC_KEY_V1,
    )


def test_plain_database_hash_chain_is_named_consistency_only() -> None:
    assessment = assess_consistency_chain(valid=True)

    assert assessment.level == CONSISTENCY_ONLY
    assert assessment.chain_valid is True
    assert assessment.tamper_resistant is False
    assert "consistency" in assessment.explanation.casefold()
    assert "tamper-proof" not in assessment.explanation.casefold()


def test_hmac_receipt_binds_tenant_head_policy_time_and_key_version() -> None:
    receipt = _receipt()

    assert receipt.algorithm == "HMAC-SHA256"
    assert receipt.tenant_id == "tenant-a"
    assert receipt.last_sequence == 7
    assert receipt.last_hash == HEAD_HASH
    assert receipt.policy_version == "audit-head-v1"
    assert receipt.issued_at == "2026-07-13T12:30:00+00:00"
    assert receipt.key_version == "key-v1"
    assert len(receipt.signature) == 64
    assert verify_audit_head_receipt(receipt, {"key-v1": SYNTHETIC_KEY_V1}) is True


def test_hmac_receipt_matches_independent_known_answer_vector() -> None:
    assert _receipt().signature == (
        "7300ef66659bbdc7bd404d61943fb3e71bad9cc4a53b6de105b90728810d602c"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("tenant_id", "tenant-b"),
        ("last_sequence", 8),
        ("last_hash", "b" * 64),
        ("policy_version", "audit-head-v2"),
        ("issued_at", "2026-07-13T12:31:00+00:00"),
        ("key_version", "key-v2"),
        ("algorithm", "SHA-256"),
        ("signature", "0" * 64),
    ],
)
def test_receipt_verification_rejects_bound_field_changes(field: str, value: object) -> None:
    receipt = replace(_receipt(), **{field: value})

    assert verify_audit_head_receipt(
        receipt,
        {"key-v1": SYNTHETIC_KEY_V1, "key-v2": SYNTHETIC_KEY_V2},
    ) is False


def test_key_rotation_verifies_old_receipts_only_with_the_declared_version() -> None:
    old_receipt = _receipt()
    new_receipt = issue_audit_head_receipt(
        tenant_id="tenant-a",
        last_sequence=8,
        last_hash="b" * 64,
        policy_version="audit-head-v1",
        issued_at=ISSUED_AT,
        key_version="key-v2",
        key=SYNTHETIC_KEY_V2,
    )
    keyring = {"key-v1": SYNTHETIC_KEY_V1, "key-v2": SYNTHETIC_KEY_V2}

    assert verify_audit_head_receipt(old_receipt, keyring) is True
    assert verify_audit_head_receipt(new_receipt, keyring) is True
    assert verify_audit_head_receipt(old_receipt, {"key-v2": SYNTHETIC_KEY_V2}) is False
    assert verify_audit_head_receipt(new_receipt, {"key-v1": SYNTHETIC_KEY_V1}) is False


def test_receipt_verification_rejects_wrong_key_for_declared_version() -> None:
    assert (
        verify_audit_head_receipt(_receipt(), {"key-v1": SYNTHETIC_KEY_V2})
        is False
    )


@pytest.mark.parametrize("key", [None, b"", b"too-short", "not-bytes"])
def test_receipt_verification_rejects_invalid_keyring_key(key: object) -> None:
    assert (
        verify_audit_head_receipt(
            _receipt(),
            {"key-v1": key},  # type: ignore[dict-item]
        )
        is False
    )


@pytest.mark.parametrize("key", [None, b"", b"too-short", "not-bytes"])
def test_receipt_issuance_rejects_missing_or_invalid_keys(key: object) -> None:
    with pytest.raises(IntegrityConfigurationError, match="key"):
        issue_audit_head_receipt(
            tenant_id="tenant-a",
            last_sequence=7,
            last_hash=HEAD_HASH,
            policy_version="audit-head-v1",
            issued_at=ISSUED_AT,
            key_version="key-v1",
            key=key,  # type: ignore[arg-type]
        )


def test_production_admin_integrity_fails_closed_without_hmac_key() -> None:
    assert select_admin_integrity_level(production_mode=False, key=None) == CONSISTENCY_ONLY

    with pytest.raises(IntegrityConfigurationError, match="key"):
        select_admin_integrity_level(production_mode=True, key=None)

    assert (
        select_admin_integrity_level(production_mode=True, key=SYNTHETIC_KEY_V1)
        == HMAC_SHA256
    )


@pytest.mark.parametrize("key", [b"", b"too-short", "not-bytes"])
def test_production_admin_integrity_rejects_every_invalid_key(key: object) -> None:
    with pytest.raises(IntegrityConfigurationError, match="key"):
        select_admin_integrity_level(
            production_mode=True,
            key=key,  # type: ignore[arg-type]
        )


def test_receipt_never_contains_or_exposes_the_secret_key() -> None:
    receipt = _receipt()
    serialized = receipt.to_mapping()
    secret_text = SYNTHETIC_KEY_V1.decode("ascii")

    assert "key" not in serialized
    assert secret_text not in repr(receipt)
    assert secret_text not in str(serialized)


@pytest.mark.parametrize(
    "overrides",
    [
        {"tenant_id": ""},
        {"last_sequence": -1},
        {"last_sequence": True},
        {"last_hash": "not-a-sha256"},
        {"policy_version": ""},
        {"issued_at": datetime(2026, 7, 13, 12, 30)},
        {"key_version": ""},
    ],
)
def test_receipt_issuance_rejects_invalid_head_metadata(overrides: dict[str, object]) -> None:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "last_sequence": 7,
        "last_hash": HEAD_HASH,
        "policy_version": "audit-head-v1",
        "issued_at": ISSUED_AT,
        "key_version": "key-v1",
        "key": SYNTHETIC_KEY_V1,
    }
    values.update(overrides)

    with pytest.raises(ValueError):
        issue_audit_head_receipt(**values)  # type: ignore[arg-type]
