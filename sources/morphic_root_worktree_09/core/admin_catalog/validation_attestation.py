"""External authentication contract for Admin-Catalog validation attestations."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Protocol, runtime_checkable


@runtime_checkable
class ValidationKeyProvider(Protocol):
    """Trusted key authority kept outside the Catalog SQLite database and backups."""

    @property
    def authority_id(self) -> str:
        """Return the stable, non-secret identity of this key authority."""

    def active_key_id(self) -> str:
        """Return the key identifier used for newly created attestations."""

    def sign_hmac_sha256(self, key_id: str, message: bytes) -> bytes:
        """Authenticate *message* with the requested key."""

    def verify_hmac_sha256(
        self,
        key_id: str,
        message: bytes,
        signature: bytes,
    ) -> bool:
        """Verify an attestation without exposing key material."""


@dataclass(frozen=True, slots=True, init=False)
class HmacValidationKeyProvider:
    """In-memory provider for explicit composition and isolated tests.

    Applications remain responsible for loading the keys from an authority that is
    outside the Catalog database and its backup bundle.
    """

    authority_id: str
    _active_key_id: str
    _keys: Mapping[str, bytes]

    def __init__(
        self,
        *,
        authority_id: str,
        active_key_id: str,
        keys: Mapping[str, bytes],
    ) -> None:
        clean_authority_id = authority_id.strip()
        clean_active_key_id = active_key_id.strip()
        copied_keys = {key_id.strip(): bytes(key) for key_id, key in keys.items()}
        if not clean_authority_id:
            raise ValueError("validation authority_id is required")
        if not clean_active_key_id or clean_active_key_id not in copied_keys:
            raise ValueError("active validation key_id is missing")
        if any(not key_id for key_id in copied_keys):
            raise ValueError("validation key_id is required")
        if any(len(key) < 32 for key in copied_keys.values()):
            raise ValueError("validation HMAC keys must contain at least 32 bytes")
        object.__setattr__(self, "authority_id", clean_authority_id)
        object.__setattr__(self, "_active_key_id", clean_active_key_id)
        object.__setattr__(self, "_keys", MappingProxyType(copied_keys))

    def active_key_id(self) -> str:
        return self._active_key_id

    def sign_hmac_sha256(self, key_id: str, message: bytes) -> bytes:
        try:
            key = self._keys[key_id]
        except KeyError as exc:
            raise ValueError("unknown validation key_id") from exc
        return hmac.new(key, message, hashlib.sha256).digest()

    def verify_hmac_sha256(
        self,
        key_id: str,
        message: bytes,
        signature: bytes,
    ) -> bool:
        try:
            expected = self.sign_hmac_sha256(key_id, message)
        except ValueError:
            return False
        return hmac.compare_digest(expected, signature)
