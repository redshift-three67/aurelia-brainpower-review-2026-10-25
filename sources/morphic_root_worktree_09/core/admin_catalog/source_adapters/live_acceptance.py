"""F7.3 live acceptance harness for the NCBI Taxonomy adapter.

This module is the only F7.3 place that owns a real HTTP transport.  The harness
requires a time-bounded grant, performs DNS evidence checks before and after the
fetch, and writes an immutable quarantined evidence record.
"""

from __future__ import annotations

import hashlib
import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol

from core.admin_catalog.network_policy import (
    AdapterNetworkGrant,
    AdminSourceNetworkPolicy,
)
from core.admin_catalog.source_adapters.ncbi_taxonomy import (
    NCBI_TAXONOMY_ADAPTER_VERSION,
    NCBI_TAXONOMY_SOURCE_ID,
    NCBI_TAXONOMY_SPEC,
    NCBITaxonomyAdapter,
    NCBITaxonomyAdapterError,
    NCBITaxonomyHttpResponse,
    NCBITaxonomyQuarantineSnapshot,
)
from core.source_registry import SourceManifest


_EVIDENCE_SCHEMA = "morphic_ncbi_taxonomy_live_acceptance"
_EVIDENCE_SCHEMA_VERSION = 1
_USER_AGENT = "Morphic-F7.3-Live-Acceptance"


class LiveAcceptanceError(RuntimeError):
    """Raised when the F7.3 live acceptance gate fails closed."""


class DnsResolver(Protocol):
    def resolve(self, host: str) -> tuple[str, ...]:
        """Return resolved IP addresses for a host."""


@dataclass(frozen=True, slots=True)
class NCBITaxonomyLiveAcceptanceGrant:
    tenant_id: str
    granted_by: str
    reason: str
    granted_at_utc: datetime
    expires_at_utc: datetime

    def __post_init__(self) -> None:
        for label, value in (
            ("tenant_id", self.tenant_id),
            ("granted_by", self.granted_by),
            ("reason", self.reason),
        ):
            if not value.strip():
                raise LiveAcceptanceError(f"{label} must not be blank")
        if _as_utc(self.expires_at_utc) <= _as_utc(self.granted_at_utc):
            raise LiveAcceptanceError("live acceptance grant expiry must be after grant time")

    def assert_valid_at(self, now_utc: datetime) -> None:
        now = _as_utc(now_utc)
        if now < _as_utc(self.granted_at_utc):
            raise LiveAcceptanceError("live acceptance grant is not active yet")
        if now >= _as_utc(self.expires_at_utc):
            raise LiveAcceptanceError("live acceptance grant is expired")

    def to_adapter_grant(self) -> AdapterNetworkGrant:
        return AdapterNetworkGrant(
            source_id=NCBI_TAXONOMY_SOURCE_ID,
            adapter_version=NCBI_TAXONOMY_ADAPTER_VERSION,
            tenant_id=self.tenant_id,
            granted_by=self.granted_by,
            reason=self.reason,
        )


@dataclass(frozen=True, slots=True)
class NCBITaxonomyLiveAcceptanceResult:
    snapshot: NCBITaxonomyQuarantineSnapshot
    evidence_path: Path
    evidence_sha256: str
    evidence: Mapping[str, Any]


class StaticDnsResolver:
    def resolve(self, host: str) -> tuple[str, ...]:
        try:
            infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        except socket.gaierror as exc:
            raise LiveAcceptanceError(f"DNS resolution failed for host: {host}") from exc
        addresses = sorted({info[4][0] for info in infos})
        if not addresses:
            raise LiveAcceptanceError(f"DNS resolution returned no addresses: {host}")
        return tuple(addresses)


class UrllibNCBITaxonomyTransport:
    def __init__(
        self,
        *,
        opener: Any | None = None,
        max_response_bytes: int = NCBI_TAXONOMY_SPEC.max_response_bytes,
    ) -> None:
        self._opener = opener or urllib.request.build_opener()
        self._max_response_bytes = max_response_bytes

    def get(self, url: str, *, timeout_seconds: float) -> NCBITaxonomyHttpResponse:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-agent": _USER_AGENT,
            },
        )
        try:
            with self._opener.open(request, timeout=timeout_seconds) as response:
                body = response.read(self._max_response_bytes + 1)
                if len(body) > self._max_response_bytes:
                    raise LiveAcceptanceError("live response size limit exceeded")
                final_url = response.geturl()
                raw_status = getattr(response, "status", None)
                if raw_status is None:
                    raw_status = response.getcode()
                status_code = int(raw_status)
                headers = _headers_to_mapping(response.headers)
        except urllib.error.URLError as exc:
            raise LiveAcceptanceError("live fetch failed") from exc

        redirects = (final_url,) if final_url != url else ()
        return NCBITaxonomyHttpResponse(
            url=final_url,
            status_code=status_code,
            headers=headers,
            body=body,
            redirect_urls=redirects,
        )


def run_ncbi_taxonomy_live_acceptance(
    *,
    source: SourceManifest,
    grant: NCBITaxonomyLiveAcceptanceGrant,
    query: str,
    evidence_dir: Path | str,
    transport: Any | None = None,
    dns_resolver: DnsResolver | None = None,
    now_utc: datetime | None = None,
) -> NCBITaxonomyLiveAcceptanceResult:
    now = _as_utc(now_utc or datetime.now(timezone.utc))
    grant.assert_valid_at(now)

    policy = AdminSourceNetworkPolicy(grants=(grant.to_adapter_grant(),))
    adapter = NCBITaxonomyAdapter(
        network_policy=policy,
        transport=transport or UrllibNCBITaxonomyTransport(),
    )
    resolver = dns_resolver or StaticDnsResolver()
    try:
        snapshot = adapter.fetch_quarantined_snapshot_with_dns_resolver(
            source=source,
            tenant_id=grant.tenant_id,
            admin_authenticated=True,
            dns_resolver=resolver,
            query=query,
        )
    except NCBITaxonomyAdapterError as exc:
        raise LiveAcceptanceError(str(exc)) from exc

    evidence = _evidence_mapping(
        snapshot=snapshot,
        grant=grant,
        query=query,
        accepted_at_utc=now,
    )
    evidence_sha256 = _canonical_sha256(evidence)
    evidence_with_hash = {**evidence, "sha256": evidence_sha256}
    target_dir = Path(evidence_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = (
        target_dir
        / f"{NCBI_TAXONOMY_SOURCE_ID}.{NCBI_TAXONOMY_ADAPTER_VERSION}."
        f"{evidence_sha256}.live-acceptance.json"
    )
    _write_immutable_json(evidence_path, evidence_with_hash)
    return NCBITaxonomyLiveAcceptanceResult(
        snapshot=snapshot,
        evidence_path=evidence_path,
        evidence_sha256=evidence_sha256,
        evidence=evidence_with_hash,
    )


def _evidence_mapping(
    *,
    snapshot: NCBITaxonomyQuarantineSnapshot,
    grant: NCBITaxonomyLiveAcceptanceGrant,
    query: str,
    accepted_at_utc: datetime,
) -> dict[str, Any]:
    retrieval = snapshot.retrieval_metadata
    return {
        "schema": _EVIDENCE_SCHEMA,
        "schema_version": _EVIDENCE_SCHEMA_VERSION,
        "source_id": snapshot.source_id,
        "adapter_version": snapshot.adapter_version,
        "tenant_id": grant.tenant_id,
        "query": query,
        "accepted_at_utc": _iso_utc(accepted_at_utc),
        "grant": {
            "granted_by": grant.granted_by,
            "reason": grant.reason,
            "granted_at_utc": _iso_utc(grant.granted_at_utc),
            "expires_at_utc": _iso_utc(grant.expires_at_utc),
        },
        "network_acceptance": {
            "url": retrieval["url"],
            "mime_type": retrieval["mime_type"],
            "status_code": retrieval["status_code"],
            "redirect_urls": retrieval["redirect_urls"],
            "response_size_bytes": retrieval["response_size_bytes"],
            "response_sha256": retrieval["response_sha256"],
            "dns_pre_connect": retrieval["dns_pre_connect"],
            "dns_post_connect": retrieval["dns_post_connect"],
        },
        "snapshot": snapshot.to_mapping(),
        "no_publish": True,
        "no_activate": True,
        "no_runtime_effect": True,
    }


def _headers_to_mapping(headers: Any) -> dict[str, str]:
    if isinstance(headers, Mapping):
        return {str(key).lower(): str(value) for key, value in headers.items()}
    return {str(key).lower(): str(value) for key, value in headers.items()}


def _write_immutable_json(path: Path, payload: Mapping[str, Any]) -> None:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
            handle.write("\n")
    except FileExistsError:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing != dict(payload):
            raise LiveAcceptanceError("live acceptance evidence hash collision")


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise LiveAcceptanceError("live acceptance timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def _iso_utc(value: datetime) -> str:
    return _as_utc(value).isoformat().replace("+00:00", "Z")


__all__ = [
    "DnsResolver",
    "LiveAcceptanceError",
    "NCBITaxonomyLiveAcceptanceGrant",
    "NCBITaxonomyLiveAcceptanceResult",
    "StaticDnsResolver",
    "UrllibNCBITaxonomyTransport",
    "run_ncbi_taxonomy_live_acceptance",
]
