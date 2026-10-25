"""Base contracts for future admin source adapters.

The base contract is intentionally transport-free.  It describes fixed adapter
identity, host and response limits plus explicit secret injection boundaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlsplit

from core.admin_catalog.network_policy import (
    DEFAULT_MAX_DECOMPRESSED_BYTES,
    DEFAULT_MAX_RESPONSE_BYTES,
    DEFAULT_TIMEOUT_SECONDS,
    NetworkPolicyError,
)


_IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")


class AdapterSecretError(RuntimeError):
    """Raised when an adapter cannot resolve required injected credentials."""


class SourceAdapterSecretProvider(Protocol):
    def get_secret(
        self,
        *,
        source_id: str,
        adapter_version: str,
        secret_name: str,
    ) -> str:
        """Return a credential value from an injected provider."""


@dataclass(frozen=True)
class SourceAdapterSpec:
    source_id: str
    adapter_version: str
    allowed_hosts: tuple[str, ...]
    allowed_mime_types: tuple[str, ...] = ("application/json",)
    credential_names: tuple[str, ...] = ()
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES
    max_decompressed_bytes: int = DEFAULT_MAX_DECOMPRESSED_BYTES
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if not _IDENTIFIER_RE.fullmatch(self.source_id):
            raise NetworkPolicyError("source_id must be a fixed registered identifier")
        if not self.adapter_version.strip():
            raise NetworkPolicyError("adapter_version must not be blank")
        if not self.allowed_hosts:
            raise NetworkPolicyError("allowed_hosts must not be empty")
        normalized_hosts = tuple(_normalize_host(host) for host in self.allowed_hosts)
        if any(not host for host in normalized_hosts):
            raise NetworkPolicyError("allowed_hosts must contain host names")
        if not self.allowed_mime_types:
            raise NetworkPolicyError("allowed_mime_types must not be empty")
        if self.max_response_bytes <= 0:
            raise NetworkPolicyError("max_response_bytes must be positive")
        if self.max_decompressed_bytes <= 0:
            raise NetworkPolicyError("max_decompressed_bytes must be positive")
        if self.timeout_seconds <= 0:
            raise NetworkPolicyError("timeout_seconds must be positive")
        object.__setattr__(self, "allowed_hosts", normalized_hosts)

    def resolve_credentials(
        self,
        provider: SourceAdapterSecretProvider | None,
    ) -> dict[str, str]:
        if not self.credential_names:
            return {}
        if provider is None:
            raise AdapterSecretError("adapter credentials require injected secret provider")
        credentials: dict[str, str] = {}
        for secret_name in self.credential_names:
            if not secret_name.strip():
                raise AdapterSecretError("secret name must not be blank")
            value = provider.get_secret(
                source_id=self.source_id,
                adapter_version=self.adapter_version,
                secret_name=secret_name,
            )
            if not value:
                raise AdapterSecretError("secret provider returned blank credential")
            credentials[secret_name] = value
        return credentials


def _normalize_host(value: str) -> str:
    candidate = value.strip().lower()
    parsed = urlsplit(candidate)
    if parsed.scheme or parsed.netloc or "/" in candidate:
        raise NetworkPolicyError("allowed_hosts must be fixed host names, not URLs")
    return candidate


__all__ = [
    "AdapterSecretError",
    "SourceAdapterSecretProvider",
    "SourceAdapterSpec",
]
