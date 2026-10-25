"""Composition helpers for external Admin-Catalog validation HMAC keys."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Mapping

from .service import AdminCatalogService
from .store import CatalogStore
from .validation_attestation import HmacValidationKeyProvider, ValidationKeyProvider


VALIDATION_KEYRING_PURPOSE = "morphic_admin_catalog_validation_hmac_v1"
VALIDATION_KEYRING_FILE_ENV = "MORPHIC_ADMIN_VALIDATION_KEYRING_FILE"
VALIDATION_KEYRING_ENV = "MORPHIC_ADMIN_VALIDATION_KEYRING"
VALIDATION_AUTHORITY_ID_ENV = "MORPHIC_ADMIN_VALIDATION_AUTHORITY_ID"
VALIDATION_ACTIVE_KEY_ID_ENV = "MORPHIC_ADMIN_VALIDATION_KEY_ID"
VALIDATION_KEY_HEX_ENV = "MORPHIC_ADMIN_VALIDATION_KEY_HEX"
_MINIMUM_VALIDATION_HMAC_KEY_BYTES = 32


class ValidationKeyCompositionError(ValueError):
    """Validation-key composition is missing, unsafe, or malformed."""


def _clean_environment_value(
    environment: Mapping[str, str],
    key: str,
) -> str:
    return str(environment.get(key, "")).strip()


def _validation_keyring_path_from_environment(
    environment: Mapping[str, str],
) -> Path | None:
    for key in (VALIDATION_KEYRING_FILE_ENV, VALIDATION_KEYRING_ENV):
        configured = _clean_environment_value(environment, key)
        if configured:
            return Path(configured).expanduser()
    return None


def _hex_key_bytes(raw_value: object) -> bytes:
    if not isinstance(raw_value, str) or not raw_value.strip():
        raise ValidationKeyCompositionError(
            "validation HMAC key material must be hex text"
        )
    try:
        key = bytes.fromhex(raw_value.strip())
    except ValueError as exc:
        raise ValidationKeyCompositionError(
            "validation HMAC key material must be hex text"
        ) from exc
    if len(key) < _MINIMUM_VALIDATION_HMAC_KEY_BYTES:
        raise ValidationKeyCompositionError(
            "validation HMAC key material must contain at least 32 bytes"
        )
    return key


def _required_text(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationKeyCompositionError(f"validation keyring {key} is required")
    return value.strip()


def validation_key_provider_from_keyring(
    keyring_path: str | Path,
) -> HmacValidationKeyProvider:
    """Load a validation provider from an explicit external JSON keyring."""

    path = Path(keyring_path).expanduser()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationKeyCompositionError(
            "validation keyring file does not exist"
        ) from exc
    except (OSError, UnicodeError) as exc:
        raise ValidationKeyCompositionError(
            "validation keyring file cannot be read safely"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValidationKeyCompositionError("validation keyring must be JSON") from exc
    if not isinstance(payload, dict):
        raise ValidationKeyCompositionError("validation keyring must be a JSON object")
    if payload.get("purpose") != VALIDATION_KEYRING_PURPOSE:
        raise ValidationKeyCompositionError(
            "validation keyring purpose must be morphic_admin_catalog_validation_hmac_v1"
        )
    keys_payload = payload.get("keys")
    if not isinstance(keys_payload, dict) or not keys_payload:
        raise ValidationKeyCompositionError("validation keyring keys are required")

    keys: dict[str, bytes] = {}
    for raw_key_id, raw_key_material in keys_payload.items():
        if not isinstance(raw_key_id, str) or not raw_key_id.strip():
            raise ValidationKeyCompositionError("validation key_id is required")
        keys[raw_key_id.strip()] = _hex_key_bytes(raw_key_material)

    try:
        return HmacValidationKeyProvider(
            authority_id=_required_text(payload, "authority_id"),
            active_key_id=_required_text(payload, "active_key_id"),
            keys=keys,
        )
    except (TypeError, ValueError) as exc:
        raise ValidationKeyCompositionError(str(exc)) from exc


def validation_key_provider_from_environment(
    environment: Mapping[str, str] | None = None,
    *,
    required: bool,
) -> ValidationKeyProvider | None:
    """Compose the validation provider from explicit environment configuration."""

    current_environment = os.environ if environment is None else environment
    keyring_path = _validation_keyring_path_from_environment(current_environment)
    if keyring_path is not None:
        return validation_key_provider_from_keyring(keyring_path)

    authority_id = _clean_environment_value(
        current_environment, VALIDATION_AUTHORITY_ID_ENV
    )
    active_key_id = _clean_environment_value(
        current_environment, VALIDATION_ACTIVE_KEY_ID_ENV
    )
    key_hex = _clean_environment_value(current_environment, VALIDATION_KEY_HEX_ENV)
    direct_values = (authority_id, active_key_id, key_hex)
    if any(direct_values):
        if not all(direct_values):
            raise ValidationKeyCompositionError(
                "complete validation key configuration is required"
            )
        return HmacValidationKeyProvider(
            authority_id=authority_id,
            active_key_id=active_key_id,
            keys={active_key_id: _hex_key_bytes(key_hex)},
        )

    if required:
        raise ValidationKeyCompositionError("validation key configuration is required")
    return None


def build_admin_catalog_service(
    db_path: str | Path,
    *,
    validation_keyring_path: str | Path | None = None,
    environment: Mapping[str, str] | None = None,
    require_validation_key: bool,
) -> AdminCatalogService:
    """Build a service with explicit validation-key composition before DB open."""

    provider = (
        validation_key_provider_from_keyring(validation_keyring_path)
        if validation_keyring_path is not None
        else validation_key_provider_from_environment(
            environment,
            required=require_validation_key,
        )
    )
    return AdminCatalogService(
        CatalogStore(db_path, validation_key_provider=provider)
    )


__all__ = [
    "VALIDATION_ACTIVE_KEY_ID_ENV",
    "VALIDATION_AUTHORITY_ID_ENV",
    "VALIDATION_KEYRING_ENV",
    "VALIDATION_KEYRING_FILE_ENV",
    "VALIDATION_KEYRING_PURPOSE",
    "VALIDATION_KEY_HEX_ENV",
    "ValidationKeyCompositionError",
    "build_admin_catalog_service",
    "validation_key_provider_from_environment",
    "validation_key_provider_from_keyring",
]
