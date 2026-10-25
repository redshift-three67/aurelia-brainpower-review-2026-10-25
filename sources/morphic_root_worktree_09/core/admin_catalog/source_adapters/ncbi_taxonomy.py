"""NCBI Taxonomy adapter with injected transport and quarantined snapshots.

The adapter intentionally has no built-in HTTP client.  F7.2 only defines the
official-source mapping against local fixtures or a caller-provided mock
transport.  Real network acceptance remains a separate F7.3 gate.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol
from urllib.parse import urlencode, urlsplit

from core.admin_catalog.network_policy import (
    AdminSourceNetworkPolicy,
    DnsResolutionSet,
    NetworkFetchRequest,
)
from core.admin_catalog.source_adapters.base import SourceAdapterSpec
from core.source_registry import SourceManifest


NCBI_TAXONOMY_SOURCE_ID = "ncbi_taxonomy"
NCBI_TAXONOMY_ADAPTER_VERSION = "2026.07"
NCBI_TAXONOMY_ESEARCH_ENDPOINT = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
)
NCBI_TAXONOMY_ESUMMARY_ENDPOINT = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
)
NCBI_TAXONOMY_ENDPOINT = NCBI_TAXONOMY_ESEARCH_ENDPOINT
NCBI_TAXONOMY_SPEC = SourceAdapterSpec(
    source_id=NCBI_TAXONOMY_SOURCE_ID,
    adapter_version=NCBI_TAXONOMY_ADAPTER_VERSION,
    allowed_hosts=("eutils.ncbi.nlm.nih.gov",),
    allowed_mime_types=("application/json",),
    max_response_bytes=2_000_000,
    max_decompressed_bytes=8_000_000,
    timeout_seconds=10.0,
)


class NCBITaxonomyAdapterError(RuntimeError):
    """Raised when the local NCBI adapter contract fails closed."""


@dataclass(frozen=True, slots=True)
class NCBITaxonomyHttpResponse:
    url: str
    status_code: int
    headers: Mapping[str, str]
    body: bytes
    redirect_urls: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.url.strip():
            raise NCBITaxonomyAdapterError("response url must not be blank")
        if self.status_code < 100 or self.status_code > 599:
            raise NCBITaxonomyAdapterError("response status code is invalid")
        if not isinstance(self.body, bytes):
            raise NCBITaxonomyAdapterError("response body must be bytes")


class NCBITaxonomyTransport(Protocol):
    def get(self, url: str, *, timeout_seconds: float) -> NCBITaxonomyHttpResponse:
        """Return an already bounded fixture response for the requested URL."""


class NCBITaxonomyDnsResolver(Protocol):
    def resolve(self, host: str) -> tuple[str, ...]:
        """Return the resolved IP set for the fixed adapter host."""


@dataclass(frozen=True, slots=True)
class NCBITaxonomyQuarantineSnapshot:
    source_id: str
    adapter_version: str
    source_version: str
    license: str
    data_type: str
    retrieval_metadata: Mapping[str, Any]
    records: tuple[dict[str, Any], ...]
    quarantine_state: str = "quarantined"
    publication_state: str = "not_published"
    schema: str = field(
        default="morphic_ncbi_taxonomy_quarantine_snapshot",
        init=False,
    )
    schema_version: int = field(default=1, init=False)
    sha256: str = field(init=False)

    def __post_init__(self) -> None:
        if self.quarantine_state != "quarantined":
            raise NCBITaxonomyAdapterError("snapshot must stay quarantined")
        if self.publication_state != "not_published":
            raise NCBITaxonomyAdapterError("snapshot must not be published")
        if not self.records:
            raise NCBITaxonomyAdapterError("snapshot records must not be empty")
        object.__setattr__(self, "records", tuple(dict(record) for record in self.records))
        object.__setattr__(self, "retrieval_metadata", dict(self.retrieval_metadata))
        object.__setattr__(self, "sha256", _canonical_sha256(self._mapping()))

    @property
    def rights(self) -> dict[str, bool]:
        return {"draft": False, "publish": False, "activate": False}

    @property
    def record_count(self) -> int:
        return len(self.records)

    def to_mapping(self) -> dict[str, Any]:
        return {**self._mapping(), "sha256": self.sha256}

    def _mapping(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "source_id": self.source_id,
            "adapter_version": self.adapter_version,
            "source_version": self.source_version,
            "license": self.license,
            "data_type": self.data_type,
            "retrieval_metadata": self.retrieval_metadata,
            "quarantine_state": self.quarantine_state,
            "publication_state": self.publication_state,
            "rights": self.rights,
            "records": self.records,
            "record_count": self.record_count,
        }


class NCBITaxonomyAdapter:
    def __init__(
        self,
        *,
        network_policy: AdminSourceNetworkPolicy,
        transport: NCBITaxonomyTransport,
        spec: SourceAdapterSpec = NCBI_TAXONOMY_SPEC,
    ) -> None:
        if spec.source_id != NCBI_TAXONOMY_SOURCE_ID:
            raise NCBITaxonomyAdapterError("NCBI taxonomy adapter source id is fixed")
        self._network_policy = network_policy
        self._transport = transport
        self.spec = spec

    @property
    def source_id(self) -> str:
        return self.spec.source_id

    @property
    def adapter_version(self) -> str:
        return self.spec.adapter_version

    @property
    def allowed_hosts(self) -> tuple[str, ...]:
        return self.spec.allowed_hosts

    @property
    def allowed_mime_types(self) -> tuple[str, ...]:
        return self.spec.allowed_mime_types

    @property
    def max_response_bytes(self) -> int:
        return self.spec.max_response_bytes

    @property
    def max_decompressed_bytes(self) -> int:
        return self.spec.max_decompressed_bytes

    @property
    def timeout_seconds(self) -> float:
        return self.spec.timeout_seconds

    def fetch_quarantined_snapshot(
        self,
        *,
        source: SourceManifest,
        tenant_id: str,
        admin_authenticated: bool,
        dns_resolution: DnsResolutionSet,
        query: str,
    ) -> NCBITaxonomyQuarantineSnapshot:
        normalized_query = _required_text(query, "query")
        url = _query_url(normalized_query)
        self._require_policy_allowed(
            source=source,
            tenant_id=tenant_id,
            admin_authenticated=admin_authenticated,
            dns_resolution=dns_resolution,
            request=NetworkFetchRequest(
                url=url,
                response_mime_type="application/json",
                timeout_seconds=self.timeout_seconds,
            ),
        )

        response = self._transport.get(url, timeout_seconds=self.timeout_seconds)
        mime_type = _content_type(response.headers)
        self._require_policy_allowed(
            source=source,
            tenant_id=tenant_id,
            admin_authenticated=admin_authenticated,
            dns_resolution=dns_resolution,
            request=NetworkFetchRequest(
                url=response.url,
                redirect_urls=tuple(response.redirect_urls),
                response_size_bytes=len(response.body),
                decompressed_size_bytes=len(response.body),
                response_mime_type=mime_type,
                timeout_seconds=self.timeout_seconds,
            ),
        )
        if response.status_code != 200:
            raise NCBITaxonomyAdapterError(
                f"NCBI taxonomy fixture returned status {response.status_code}"
            )

        source_version, records = _parse_taxonomy_payload(response.body)
        return NCBITaxonomyQuarantineSnapshot(
            source_id=self.source_id,
            adapter_version=self.adapter_version,
            source_version=source_version,
            license=source.license,
            data_type="terminology",
            retrieval_metadata={
                "url": response.url,
                "query": normalized_query,
                "mime_type": mime_type,
                "status_code": response.status_code,
                "redirect_urls": tuple(response.redirect_urls),
                "response_size_bytes": len(response.body),
                "response_sha256": hashlib.sha256(response.body).hexdigest(),
                "record_count": len(records),
                "quarantine_state": "quarantined",
            },
            records=records,
        )

    def fetch_quarantined_snapshot_with_dns_resolver(
        self,
        *,
        source: SourceManifest,
        tenant_id: str,
        admin_authenticated: bool,
        dns_resolver: NCBITaxonomyDnsResolver,
        query: str,
    ) -> NCBITaxonomyQuarantineSnapshot:
        normalized_query = _required_text(query, "query")
        url = _query_url(normalized_query)
        host = _host_from_url(url)
        pre_connect = dns_resolver.resolve(host)
        self._require_policy_allowed(
            source=source,
            tenant_id=tenant_id,
            admin_authenticated=admin_authenticated,
            dns_resolution=DnsResolutionSet(
                pre_connect=pre_connect,
                post_connect=pre_connect,
            ),
            request=NetworkFetchRequest(
                url=url,
                response_mime_type="application/json",
                timeout_seconds=self.timeout_seconds,
            ),
        )

        response = self._transport.get(url, timeout_seconds=self.timeout_seconds)
        response_host = _host_from_url(response.url)
        post_connect = dns_resolver.resolve(response_host)
        mime_type = _content_type(response.headers)
        self._require_policy_allowed(
            source=source,
            tenant_id=tenant_id,
            admin_authenticated=admin_authenticated,
            dns_resolution=DnsResolutionSet(
                pre_connect=pre_connect,
                post_connect=post_connect,
            ),
            request=NetworkFetchRequest(
                url=response.url,
                redirect_urls=tuple(response.redirect_urls),
                response_size_bytes=len(response.body),
                decompressed_size_bytes=len(response.body),
                response_mime_type=mime_type,
                timeout_seconds=self.timeout_seconds,
            ),
        )
        if response.status_code != 200:
            raise NCBITaxonomyAdapterError(
                f"NCBI taxonomy fixture returned status {response.status_code}"
            )

        source_version, records = _parse_taxonomy_payload(response.body)
        return NCBITaxonomyQuarantineSnapshot(
            source_id=self.source_id,
            adapter_version=self.adapter_version,
            source_version=source_version,
            license=source.license,
            data_type="terminology",
            retrieval_metadata={
                "url": response.url,
                "query": normalized_query,
                "mime_type": mime_type,
                "status_code": response.status_code,
                "redirect_urls": tuple(response.redirect_urls),
                "response_size_bytes": len(response.body),
                "response_sha256": hashlib.sha256(response.body).hexdigest(),
                "record_count": len(records),
                "quarantine_state": "quarantined",
                "dns_pre_connect": tuple(pre_connect),
                "dns_post_connect": tuple(post_connect),
            },
            records=records,
        )

    def _require_policy_allowed(
        self,
        *,
        source: SourceManifest,
        tenant_id: str,
        admin_authenticated: bool,
        dns_resolution: DnsResolutionSet,
        request: NetworkFetchRequest,
    ) -> None:
        decision = self._network_policy.evaluate_fetch(
            source,
            self,
            tenant_id=tenant_id,
            request=request,
            admin_authenticated=admin_authenticated,
            dns_resolution=dns_resolution,
        )
        if not decision.allowed:
            raise NCBITaxonomyAdapterError(decision.reason)


def _query_url(query: str) -> str:
    if query.isdigit():
        params = urlencode({"db": "taxonomy", "retmode": "json", "id": query})
        return f"{NCBI_TAXONOMY_ESUMMARY_ENDPOINT}?{params}"
    params = urlencode({"db": "taxonomy", "retmode": "json", "term": query})
    return f"{NCBI_TAXONOMY_ESEARCH_ENDPOINT}?{params}"


def _host_from_url(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower()
    if not host:
        raise NCBITaxonomyAdapterError("response url host must not be blank")
    return host


def _content_type(headers: Mapping[str, str]) -> str:
    for key, value in headers.items():
        if key.lower() == "content-type":
            return value.split(";", 1)[0].strip().lower()
    return ""


def _parse_taxonomy_payload(body: bytes) -> tuple[str, tuple[dict[str, Any], ...]]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NCBITaxonomyAdapterError("invalid taxonomy fixture json") from exc
    if not isinstance(payload, Mapping):
        raise NCBITaxonomyAdapterError("taxonomy fixture must be a JSON object")
    if "source_version" in payload or "records" in payload:
        source_version = _required_text(payload.get("source_version"), "source_version")
        raw_records = payload.get("records")
        if not isinstance(raw_records, list) or not raw_records:
            raise NCBITaxonomyAdapterError(
                "taxonomy fixture records must be a non-empty list"
            )
        return source_version, tuple(
            _normalize_taxonomy_record(record) for record in raw_records
        )

    result = payload.get("result")
    if isinstance(result, Mapping):
        raw_uids = result.get("uids")
        if isinstance(raw_uids, list) and raw_uids:
            header = payload.get("header")
            version = ""
            if isinstance(header, Mapping):
                version_value = header.get("version")
                if isinstance(version_value, str):
                    version = version_value
            records = []
            for raw_uid in raw_uids:
                uid = str(raw_uid)
                record = result.get(uid)
                if not isinstance(record, Mapping):
                    raise NCBITaxonomyAdapterError("invalid taxonomy record")
                records.append(_normalize_taxonomy_record(_esummary_record(record)))
            source_version = f"ncbi-esummary-{version or 'unknown'}"
            return source_version, tuple(records)

    raise NCBITaxonomyAdapterError("unsupported taxonomy response shape")


def _esummary_record(record: Mapping[str, Any]) -> dict[str, Any]:
    raw_tax_id = record.get("taxid", record.get("uid"))
    tax_id = str(raw_tax_id).strip()
    scientific_name = record.get("scientificname", record.get("scientific_name"))
    return {
        "tax_id": tax_id,
        "scientific_name": scientific_name,
        "rank": record.get("rank"),
        "lineage": _normalize_lineage_value(record.get("lineage")),
    }


def _normalize_taxonomy_record(record: object) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise NCBITaxonomyAdapterError("invalid taxonomy record")
    try:
        tax_id = _required_text(record.get("tax_id"), "tax_id")
        scientific_name = _required_text(record.get("scientific_name"), "scientific_name")
        rank = _required_text(record.get("rank"), "rank")
    except NCBITaxonomyAdapterError as exc:
        raise NCBITaxonomyAdapterError("invalid taxonomy record") from exc
    if not tax_id.isdigit():
        raise NCBITaxonomyAdapterError("invalid taxonomy record")
    lineage = record.get("lineage", ())
    if not isinstance(lineage, (list, tuple)):
        raise NCBITaxonomyAdapterError("invalid taxonomy record")
    try:
        normalized_lineage = tuple(_required_text(item, "lineage") for item in lineage)
    except NCBITaxonomyAdapterError as exc:
        raise NCBITaxonomyAdapterError("invalid taxonomy record") from exc
    return {
        "id": f"ncbi_taxonomy_{tax_id}",
        "tax_id": tax_id,
        "scientific_name": scientific_name,
        "rank": rank,
        "lineage": normalized_lineage,
    }


def _normalize_lineage_value(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(";") if item.strip())
    if isinstance(value, list):
        names: list[str] = []
        for item in value:
            if isinstance(item, Mapping):
                name = item.get("scientificname", item.get("scientific_name"))
                if isinstance(name, str) and name.strip():
                    names.append(name.strip())
            elif isinstance(item, str) and item.strip():
                names.append(item.strip())
        return tuple(names)
    return ()


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise NCBITaxonomyAdapterError(f"{field_name} must be non-empty text")
    return value.strip()


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


__all__ = [
    "NCBI_TAXONOMY_ADAPTER_VERSION",
    "NCBI_TAXONOMY_ENDPOINT",
    "NCBI_TAXONOMY_ESEARCH_ENDPOINT",
    "NCBI_TAXONOMY_ESUMMARY_ENDPOINT",
    "NCBI_TAXONOMY_SOURCE_ID",
    "NCBI_TAXONOMY_SPEC",
    "NCBITaxonomyAdapter",
    "NCBITaxonomyDnsResolver",
    "NCBITaxonomyAdapterError",
    "NCBITaxonomyHttpResponse",
    "NCBITaxonomyQuarantineSnapshot",
    "NCBITaxonomyTransport",
]
