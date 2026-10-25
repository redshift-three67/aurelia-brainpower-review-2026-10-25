from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.admin_catalog import CatalogContext, CatalogEntry, EntryType


VALIDATION_PURPOSE = "morphic_admin_catalog_validation_hmac_v1"


def _write_keyring(
    path: Path,
    *,
    purpose: str = VALIDATION_PURPOSE,
    authority_id: str = "admin-catalog-validation-tests",
    active_key_id: str = "validation-v2",
    keys: dict[str, str] | None = None,
) -> Path:
    path.write_text(
        json.dumps(
            {
                "purpose": purpose,
                "authority_id": authority_id,
                "active_key_id": active_key_id,
                "keys": keys
                or {
                    "validation-v1": "11" * 32,
                    "validation-v2": "22" * 32,
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def _context() -> CatalogContext:
    return CatalogContext(
        operator_id="operator-c1",
        workspace_id="workspace-c1",
        tenant_id="tenant-c1",
        scope="workspace",
    )


def test_required_environment_composition_fails_closed_without_validation_key() -> None:
    from core.admin_catalog.validation_key_composition import (
        ValidationKeyCompositionError,
        validation_key_provider_from_environment,
    )

    with pytest.raises(ValidationKeyCompositionError, match="validation key"):
        validation_key_provider_from_environment({}, required=True)


def test_optional_environment_composition_returns_none_without_configuration() -> None:
    from core.admin_catalog.validation_key_composition import (
        validation_key_provider_from_environment,
    )

    assert validation_key_provider_from_environment({}, required=False) is None


def test_validation_keyring_rejects_stage_or_audit_key_material(tmp_path: Path) -> None:
    from core.admin_catalog.validation_key_composition import (
        ValidationKeyCompositionError,
        validation_key_provider_from_keyring,
    )

    stage_key = tmp_path / "sources.json.stage-key"
    stage_key.write_bytes(b"S" * 32)
    with pytest.raises(ValidationKeyCompositionError, match="validation|keyring|JSON"):
        validation_key_provider_from_keyring(stage_key)

    audit_keyring = _write_keyring(
        tmp_path / "audit-keyring.json",
        purpose="morphic_admin_catalog_audit_hmac_v1",
    )
    with pytest.raises(ValidationKeyCompositionError, match="purpose|validation"):
        validation_key_provider_from_keyring(audit_keyring)


def test_validation_keyring_rejects_unknown_active_key_without_leaking_secret(
    tmp_path: Path,
) -> None:
    from core.admin_catalog.validation_key_composition import (
        ValidationKeyCompositionError,
        validation_key_provider_from_keyring,
    )

    secret_hex = "ab" * 32
    keyring = _write_keyring(
        tmp_path / "validation-keyring.json",
        active_key_id="missing-validation-key",
        keys={"validation-v1": secret_hex},
    )

    with pytest.raises(ValidationKeyCompositionError) as exc_info:
        validation_key_provider_from_keyring(keyring)

    message = str(exc_info.value)
    assert "active validation key_id" in message
    assert secret_hex not in message


def test_validation_keyring_supports_rotation_and_rejects_cross_key_verification(
    tmp_path: Path,
) -> None:
    from core.admin_catalog.validation_key_composition import (
        validation_key_provider_from_keyring,
    )

    provider = validation_key_provider_from_keyring(
        _write_keyring(tmp_path / "validation-keyring.json")
    )
    message = b"catalog validation attestation message"

    signature = provider.sign_hmac_sha256("validation-v2", message)

    assert provider.authority_id == "admin-catalog-validation-tests"
    assert provider.active_key_id() == "validation-v2"
    assert provider.verify_hmac_sha256("validation-v2", message, signature) is True
    assert provider.verify_hmac_sha256("validation-v1", message, signature) is False
    assert provider.verify_hmac_sha256("unknown-validation-key", message, signature) is False


def test_admin_catalog_service_requires_external_validation_key_when_requested(
    tmp_path: Path,
) -> None:
    from core.admin_catalog.validation_key_composition import (
        ValidationKeyCompositionError,
        build_admin_catalog_service,
    )

    db_path = tmp_path / "catalog.db"

    with pytest.raises(ValidationKeyCompositionError, match="validation key"):
        build_admin_catalog_service(
            db_path,
            environment={},
            require_validation_key=True,
        )

    assert not db_path.exists()


def test_admin_catalog_service_composition_injects_validation_provider(
    tmp_path: Path,
) -> None:
    from core.admin_catalog.validation_key_composition import (
        build_admin_catalog_service,
    )

    context = _context()
    service = build_admin_catalog_service(
        tmp_path / "catalog.db",
        validation_keyring_path=_write_keyring(tmp_path / "validation-keyring.json"),
        environment={},
        require_validation_key=True,
    )
    entry = CatalogEntry(
        entry_id="c1-validation-group",
        entry_type=EntryType.GROUP,
        context=context,
        source_id="manual",
        provenance="manual",
        data={"label": "C1 Validation"},
    )

    service.create_draft(context, "c1-validation-draft", [entry])
    result = service.validate_draft(context, "c1-validation-draft")

    assert result.is_valid is True
    assert service.store.validation_key_provider is not None
    assert service.store.get_draft(context, "c1-validation-draft")["validated_version"] == 1
