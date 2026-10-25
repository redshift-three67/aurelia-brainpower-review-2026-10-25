"""Fail-closed network policy for future admin source adapters.

This module performs no network I/O.  Callers must provide already collected
request, redirect, response and DNS metadata so the policy can decide whether a
future adapter would be allowed to fetch.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


DEFAULT_MAX_RESPONSE_BYTES = 20_000_000
DEFAULT_MAX_DECOMPRESSED_BYTES = 80_000_000
DEFAULT_TIMEOUT_SECONDS = 30.0
_REDACTED = "REDACTED"
_SECRET_QUERY_KEYS = frozenset(
    {"api_key", "api_token", "access_token", "token", "key", "secret", "password"}
)
_SECRET_HEADER_KEYS = frozenset({"authorization", "cookie", "x-api-key"})


class NetworkPolicyError(ValueError):
    """Raised when adapter or network policy configuration is unsafe."""


@dataclass(frozen=True)
class DnsResolutionSet:
    pre_connect: tuple[str, ...]
    post_connect: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.pre_connect or not self.post_connect:
            raise NetworkPolicyError("dns resolution must include pre and post connect IPs")
        for raw_ip in (*self.pre_connect, *self.post_connect):
            try:
                ipaddress.ip_address(raw_ip)
            except ValueError as exc:
                raise NetworkPolicyError("dns resolution contains invalid IP") from exc


@dataclass(frozen=True)
class NetworkFetchRequest:
    url: str
    redirect_urls: tuple[str, ...] = ()
    response_size_bytes: int = 0
    decompressed_size_bytes: int = 0
    response_mime_type: str = ""
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if not self.url.strip():
            raise NetworkPolicyError("fetch url must not be blank")
        if self.response_size_bytes < 0:
            raise NetworkPolicyError("response size must be non-negative")
        if self.decompressed_size_bytes < 0:
            raise NetworkPolicyError("decompressed size must be non-negative")
        if self.timeout_seconds <= 0:
            raise NetworkPolicyError("timeout must be positive")


@dataclass(frozen=True)
class AdapterNetworkGrant:
    source_id: str
    adapter_version: str
    tenant_id: str
    granted_by: str
    reason: str

    def __post_init__(self) -> None:
        for label, value in (
            ("source_id", self.source_id),
            ("adapter_version", self.adapter_version),
            ("tenant_id", self.tenant_id),
            ("granted_by", self.granted_by),
            ("reason", self.reason),
        ):
            if not value.strip():
                raise NetworkPolicyError(f"{label} must not be blank")

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.source_id, self.adapter_version, self.tenant_id)


@dataclass(frozen=True)
class NetworkPolicyDecision:
    allowed: bool
    reason: str
    source_id: str
    adapter_version: str
    tenant_id: str
    host: str = ""


@dataclass(frozen=True)
class AdminSourceNetworkPolicy:
    grants: tuple[AdapterNetworkGrant, ...] = ()
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES
    max_decompressed_bytes: int = DEFAULT_MAX_DECOMPRESSED_BYTES
    max_timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    _grant_keys: frozenset[tuple[str, str, str]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.max_response_bytes <= 0:
            raise NetworkPolicyError("max response bytes must be positive")
        if self.max_decompressed_bytes <= 0:
            raise NetworkPolicyError("max decompressed bytes must be positive")
        if self.max_timeout_seconds <= 0:
            raise NetworkPolicyError("max timeout seconds must be positive")
        object.__setattr__(self, "_grant_keys", frozenset(grant.key for grant in self.grants))

    def evaluate_fetch(
        self,
        source: Any,
        adapter: Any,
        *,
        tenant_id: str,
        request: NetworkFetchRequest,
        admin_authenticated: bool,
        dns_resolution: DnsResolutionSet,
    ) -> NetworkPolicyDecision:
        source_id = getattr(source, "id", "")
        adapter_source_id = getattr(adapter, "source_id", "")
        adapter_version = getattr(adapter, "adapter_version", "")

        if source_id != adapter_source_id:
            return self._deny(
                "adapter source mismatch",
                source_id=source_id,
                adapter_version=adapter_version,
                tenant_id=tenant_id,
            )
        if not bool(getattr(source, "active", False)):
            return self._deny(
                "source is not active",
                source_id=source_id,
                adapter_version=adapter_version,
                tenant_id=tenant_id,
            )
        if not admin_authenticated:
            return self._deny(
                "admin authentication required",
                source_id=source_id,
                adapter_version=adapter_version,
                tenant_id=tenant_id,
            )
        if (source_id, adapter_version, tenant_id) not in self._grant_keys:
            return self._deny(
                "missing adapter network grant",
                source_id=source_id,
                adapter_version=adapter_version,
                tenant_id=tenant_id,
            )

        host_result = self._check_url_and_redirects(adapter, request)
        if host_result.reason:
            return self._deny(
                host_result.reason,
                source_id=source_id,
                adapter_version=adapter_version,
                tenant_id=tenant_id,
                host=host_result.host,
            )

        dns_reason = self._check_dns_resolution(dns_resolution)
        if dns_reason:
            return self._deny(
                dns_reason,
                source_id=source_id,
                adapter_version=adapter_version,
                tenant_id=tenant_id,
                host=host_result.host,
            )

        response_reason = self._check_response_limits(adapter, request)
        if response_reason:
            return self._deny(
                response_reason,
                source_id=source_id,
                adapter_version=adapter_version,
                tenant_id=tenant_id,
                host=host_result.host,
            )

        return NetworkPolicyDecision(
            allowed=True,
            reason="allowed",
            source_id=source_id,
            adapter_version=adapter_version,
            tenant_id=tenant_id,
            host=host_result.host,
        )

    def _check_url_and_redirects(
        self,
        adapter: Any,
        request: NetworkFetchRequest,
    ) -> "_HostCheckResult":
        allowed_hosts = frozenset(getattr(adapter, "allowed_hosts", ()))
        parsed = urlsplit(request.url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme.lower() != "https":
            return _HostCheckResult(host=host, reason="https required")
        if host not in allowed_hosts:
            return _HostCheckResult(host=host, reason="host not allowed")
        for redirect_url in request.redirect_urls:
            redirect = urlsplit(redirect_url)
            redirect_host = (redirect.hostname or "").lower()
            if redirect.scheme.lower() != "https":
                return _HostCheckResult(host=redirect_host, reason="https required")
            if redirect_host not in allowed_hosts:
                return _HostCheckResult(
                    host=redirect_host,
                    reason="redirect host not allowed",
                )
        return _HostCheckResult(host=host)

    def _check_dns_resolution(self, dns_resolution: DnsResolutionSet) -> str:
        pre = frozenset(dns_resolution.pre_connect)
        post = frozenset(dns_resolution.post_connect)
        if pre != post:
            return "dns rebinding detected"
        for raw_ip in (*dns_resolution.pre_connect, *dns_resolution.post_connect):
            if _is_unsafe_network_ip(raw_ip):
                return "unsafe resolved ip"
        return ""

    def _check_response_limits(self, adapter: Any, request: NetworkFetchRequest) -> str:
        max_response = min(
            self.max_response_bytes,
            int(getattr(adapter, "max_response_bytes", self.max_response_bytes)),
        )
        max_decompressed = min(
            self.max_decompressed_bytes,
            int(
                getattr(
                    adapter,
                    "max_decompressed_bytes",
                    self.max_decompressed_bytes,
                )
            ),
        )
        max_timeout = min(
            self.max_timeout_seconds,
            float(getattr(adapter, "timeout_seconds", self.max_timeout_seconds)),
        )
        allowed_mime_types = frozenset(getattr(adapter, "allowed_mime_types", ()))

        if request.response_size_bytes > max_response:
            return "response size limit exceeded"
        if request.decompressed_size_bytes > max_decompressed:
            return "decompression limit exceeded"
        if request.timeout_seconds > max_timeout:
            return "timeout limit exceeded"
        if request.response_mime_type not in allowed_mime_types:
            return "mime type not allowed"
        return ""

    def _deny(
        self,
        reason: str,
        *,
        source_id: str,
        adapter_version: str,
        tenant_id: str,
        host: str = "",
    ) -> NetworkPolicyDecision:
        return NetworkPolicyDecision(
            allowed=False,
            reason=reason,
            source_id=source_id,
            adapter_version=adapter_version,
            tenant_id=tenant_id,
            host=host,
        )


@dataclass(frozen=True)
class _HostCheckResult:
    host: str
    reason: str = ""


def _is_unsafe_network_ip(raw_ip: str) -> bool:
    ip = ipaddress.ip_address(raw_ip)
    return ip.is_loopback or ip.is_private or ip.is_link_local


def redact_network_log_data(
    payload: Mapping[str, Any],
    *,
    secrets: Iterable[str] = (),
) -> dict[str, Any]:
    replacements = tuple(secret for secret in secrets if secret)
    return {
        key: _redact_value(key, value, replacements)
        for key, value in payload.items()
    }


def _redact_value(key: str, value: Any, secrets: tuple[str, ...]) -> Any:
    if isinstance(value, Mapping):
        return {
            child_key: _redact_value(child_key, child_value, secrets)
            for child_key, child_value in value.items()
        }
    if isinstance(value, list):
        return [_redact_value(key, item, secrets) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_value(key, item, secrets) for item in value)
    if not isinstance(value, str):
        return value

    if key.lower() in _SECRET_HEADER_KEYS:
        return _REDACTED
    redacted = _redact_url(value)
    for secret in secrets:
        redacted = redacted.replace(secret, _REDACTED)
    return redacted


def _redact_url(value: str) -> str:
    parsed = urlsplit(value)
    if not parsed.scheme or not parsed.netloc:
        return value
    query = urlencode(
        [
            (key, _REDACTED if key.lower() in _SECRET_QUERY_KEYS else item_value)
            for key, item_value in parse_qsl(parsed.query, keep_blank_values=True)
        ]
    )
    netloc = parsed.hostname or ""
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, query, parsed.fragment))


__all__ = [
    "AdapterNetworkGrant",
    "AdminSourceNetworkPolicy",
    "DnsResolutionSet",
    "NetworkFetchRequest",
    "NetworkPolicyDecision",
    "NetworkPolicyError",
    "redact_network_log_data",
]
