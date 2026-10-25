from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.admin_catalog.network_policy import (
    AdapterNetworkGrant,
    AdminSourceNetworkPolicy,
    DnsResolutionSet,
)
from core.admin_catalog.source_adapters.ncbi_taxonomy import (
    NCBI_TAXONOMY_ADAPTER_VERSION,
    NCBI_TAXONOMY_SOURCE_ID,
    NCBITaxonomyAdapter,
    NCBITaxonomyAdapterError,
    NCBITaxonomyHttpResponse,
)
from core.source_registry import SourceManifest


def active_ncbi_source() -> SourceManifest:
    return SourceManifest.from_mapping(
        {
            "id": NCBI_TAXONOMY_SOURCE_ID,
            "label": "NCBI Taxonomy",
            "description": "Official taxonomy fixture source",
            "source_type": "online_api",
            "homepage": "https://www.ncbi.nlm.nih.gov/taxonomy",
            "endpoint": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            "license": "source-specific",
            "trust_level": "official",
            "import_policy": "manual_review",
            "scopes": ["terminology"],
            "enabled": True,
            "status": "active",
        }
    )


def public_dns() -> DnsResolutionSet:
    return DnsResolutionSet(
        pre_connect=("93.184.216.34",),
        post_connect=("93.184.216.34",),
    )


def policy_with_grant(tenant_id: str = "tenant-a") -> AdminSourceNetworkPolicy:
    return AdminSourceNetworkPolicy(
        grants=(
            AdapterNetworkGrant(
                source_id=NCBI_TAXONOMY_SOURCE_ID,
                adapter_version=NCBI_TAXONOMY_ADAPTER_VERSION,
                tenant_id=tenant_id,
                granted_by="operator-admin",
                reason="local fixture adapter test",
            ),
        )
    )


def taxonomy_fixture_response(
    *,
    headers: dict[str, str] | None = None,
    body: dict[str, object] | None = None,
) -> NCBITaxonomyHttpResponse:
    payload = body or {
        "source_version": "ncbi-taxonomy-fixture-2026-07",
        "records": [
            {
                "tax_id": "9606",
                "scientific_name": "Homo sapiens",
                "rank": "species",
                "lineage": ["cellular organisms", "Eukaryota", "Metazoa"],
            },
            {
                "tax_id": "2697049",
                "scientific_name": "Severe acute respiratory syndrome coronavirus 2",
                "rank": "species",
                "lineage": ["Viruses", "Riboviria", "Coronaviridae"],
            },
        ],
    }
    return NCBITaxonomyHttpResponse(
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        status_code=200,
        headers=headers or {"content-type": "application/json; charset=utf-8"},
        body=json.dumps(payload, sort_keys=True).encode("utf-8"),
    )


class RecordingTransport:
    def __init__(self, response: NCBITaxonomyHttpResponse) -> None:
        self.response = response
        self.calls: list[tuple[str, float]] = []

    def get(self, url: str, *, timeout_seconds: float) -> NCBITaxonomyHttpResponse:
        self.calls.append((url, timeout_seconds))
        return self.response


def test_ncbi_adapter_uses_f7_policy_and_returns_quarantined_snapshot() -> None:
    transport = RecordingTransport(taxonomy_fixture_response())
    adapter = NCBITaxonomyAdapter(
        network_policy=policy_with_grant(),
        transport=transport,
    )

    snapshot = adapter.fetch_quarantined_snapshot(
        source=active_ncbi_source(),
        tenant_id="tenant-a",
        admin_authenticated=True,
        dns_resolution=public_dns(),
        query="Homo sapiens",
    )

    assert len(transport.calls) == 1
    requested_url, timeout_seconds = transport.calls[0]
    assert requested_url.startswith(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
    )
    assert "db=taxonomy" in requested_url
    assert "term=Homo+sapiens" in requested_url
    assert timeout_seconds == adapter.timeout_seconds

    assert snapshot.schema == "morphic_ncbi_taxonomy_quarantine_snapshot"
    assert snapshot.schema_version == 1
    assert snapshot.source_id == NCBI_TAXONOMY_SOURCE_ID
    assert snapshot.adapter_version == NCBI_TAXONOMY_ADAPTER_VERSION
    assert snapshot.data_type == "terminology"
    assert snapshot.license == "source-specific"
    assert snapshot.quarantine_state == "quarantined"
    assert snapshot.publication_state == "not_published"
    assert snapshot.rights == {"draft": False, "publish": False, "activate": False}
    assert snapshot.record_count == 2
    assert snapshot.records[0] == {
        "id": "ncbi_taxonomy_9606",
        "tax_id": "9606",
        "scientific_name": "Homo sapiens",
        "rank": "species",
        "lineage": ("cellular organisms", "Eukaryota", "Metazoa"),
    }
    assert snapshot.retrieval_metadata["record_count"] == 2
    assert snapshot.retrieval_metadata["mime_type"] == "application/json"
    assert len(snapshot.retrieval_metadata["response_sha256"]) == 64
    assert len(snapshot.sha256) == 64
    assert not hasattr(snapshot, "body")
    assert not hasattr(snapshot, "revision_id")
    assert snapshot.to_mapping()["sha256"] == snapshot.sha256


def test_ncbi_adapter_denies_before_transport_without_exact_grant() -> None:
    transport = RecordingTransport(taxonomy_fixture_response())
    adapter = NCBITaxonomyAdapter(
        network_policy=AdminSourceNetworkPolicy(),
        transport=transport,
    )

    with pytest.raises(NCBITaxonomyAdapterError, match="missing adapter network grant"):
        adapter.fetch_quarantined_snapshot(
            source=active_ncbi_source(),
            tenant_id="tenant-a",
            admin_authenticated=True,
            dns_resolution=public_dns(),
            query="Homo sapiens",
        )

    assert transport.calls == []


def test_ncbi_adapter_postflight_rejects_bad_mime_without_snapshot() -> None:
    transport = RecordingTransport(
        taxonomy_fixture_response(headers={"content-type": "text/html"})
    )
    adapter = NCBITaxonomyAdapter(
        network_policy=policy_with_grant(),
        transport=transport,
    )

    with pytest.raises(NCBITaxonomyAdapterError, match="mime type not allowed"):
        adapter.fetch_quarantined_snapshot(
            source=active_ncbi_source(),
            tenant_id="tenant-a",
            admin_authenticated=True,
            dns_resolution=public_dns(),
            query="Homo sapiens",
        )

    assert len(transport.calls) == 1


def test_ncbi_adapter_rejects_malformed_fixture_and_has_no_runtime_wiring() -> None:
    transport = RecordingTransport(
        taxonomy_fixture_response(
            body={
                "source_version": "ncbi-taxonomy-fixture-2026-07",
                "records": [
                    {
                        "tax_id": "",
                        "scientific_name": "Invalid",
                        "rank": "species",
                        "lineage": [],
                    }
                ],
            }
        )
    )
    adapter = NCBITaxonomyAdapter(
        network_policy=policy_with_grant(),
        transport=transport,
    )

    with pytest.raises(NCBITaxonomyAdapterError, match="invalid taxonomy record"):
        adapter.fetch_quarantined_snapshot(
            source=active_ncbi_source(),
            tenant_id="tenant-a",
            admin_authenticated=True,
            dns_resolution=public_dns(),
            query="Invalid",
        )

    module_source = Path(
        "core/admin_catalog/source_adapters/ncbi_taxonomy.py"
    ).read_text(encoding="utf-8")
    forbidden_tokens = (
        "import requests",
        "import httpx",
        "urllib.request",
        "import socket",
        "AdminCatalogService",
        "CatalogStore",
        "stage_source_data_batch",
        "activate_revision",
    )
    assert all(token not in module_source for token in forbidden_tokens)
    assert not hasattr(adapter, "publish")
    assert not hasattr(adapter, "activate")
