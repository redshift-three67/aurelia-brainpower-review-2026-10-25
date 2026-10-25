from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from core.admin_catalog.source_adapters.live_acceptance import (
    LiveAcceptanceError,
    NCBITaxonomyLiveAcceptanceGrant,
    UrllibNCBITaxonomyTransport,
    run_ncbi_taxonomy_live_acceptance,
)
from core.admin_catalog.source_adapters.ncbi_taxonomy import (
    NCBI_TAXONOMY_ADAPTER_VERSION,
    NCBI_TAXONOMY_SOURCE_ID,
    NCBITaxonomyHttpResponse,
)
from core.source_registry import SourceManifest


def active_ncbi_source() -> SourceManifest:
    return SourceManifest.from_mapping(
        {
            "id": NCBI_TAXONOMY_SOURCE_ID,
            "label": "NCBI Taxonomy",
            "description": "Official taxonomy live acceptance source",
            "source_type": "online_api",
            "homepage": "https://www.ncbi.nlm.nih.gov/taxonomy",
            "endpoint": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            "license": "source-specific",
            "trust_level": "official",
            "import_policy": "manual_review",
            "scopes": ["terminology"],
            "enabled": True,
            "status": "active",
        }
    )


def acceptance_grant(*, expires_at_utc: datetime | None = None) -> NCBITaxonomyLiveAcceptanceGrant:
    return NCBITaxonomyLiveAcceptanceGrant(
        tenant_id="tenant-a",
        granted_by="operator-admin",
        reason="F7.3 isolated NCBI taxonomy live acceptance",
        granted_at_utc=datetime(2026, 7, 17, 20, 0, tzinfo=timezone.utc),
        expires_at_utc=expires_at_utc
        or datetime(2026, 7, 17, 20, 15, tzinfo=timezone.utc),
    )


def ncbi_esummary_response() -> NCBITaxonomyHttpResponse:
    payload = {
        "header": {"type": "esummary", "version": "0.3"},
        "result": {
            "uids": ["9606"],
            "9606": {
                "uid": "9606",
                "taxid": 9606,
                "scientificname": "Homo sapiens",
                "rank": "species",
                "lineage": "cellular organisms; Eukaryota; Metazoa",
            },
        },
    }
    return NCBITaxonomyHttpResponse(
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        status_code=200,
        headers={"content-type": "application/json; charset=utf-8"},
        body=json.dumps(payload, sort_keys=True).encode("utf-8"),
    )


class RecordingTransport:
    def __init__(self, response: NCBITaxonomyHttpResponse) -> None:
        self.response = response
        self.calls: list[tuple[str, float]] = []

    def get(self, url: str, *, timeout_seconds: float) -> NCBITaxonomyHttpResponse:
        self.calls.append((url, timeout_seconds))
        return self.response


class SequencedResolver:
    def __init__(self, *answers: tuple[str, ...]) -> None:
        self.answers = list(answers)
        self.calls: list[str] = []

    def resolve(self, host: str) -> tuple[str, ...]:
        self.calls.append(host)
        if not self.answers:
            raise AssertionError("resolver exhausted")
        return self.answers.pop(0)


def test_live_acceptance_writes_immutable_quarantined_evidence(tmp_path: Path) -> None:
    transport = RecordingTransport(ncbi_esummary_response())
    resolver = SequencedResolver(("93.184.216.34",), ("93.184.216.34",))

    result = run_ncbi_taxonomy_live_acceptance(
        source=active_ncbi_source(),
        grant=acceptance_grant(),
        query="9606",
        evidence_dir=tmp_path,
        transport=transport,
        dns_resolver=resolver,
        now_utc=datetime(2026, 7, 17, 20, 5, tzinfo=timezone.utc),
    )

    assert len(transport.calls) == 1
    requested_url, timeout = transport.calls[0]
    assert requested_url.startswith(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
    )
    assert "db=taxonomy" in requested_url
    assert "id=9606" in requested_url
    assert timeout == 10.0
    assert resolver.calls == ["eutils.ncbi.nlm.nih.gov", "eutils.ncbi.nlm.nih.gov"]

    assert result.snapshot.quarantine_state == "quarantined"
    assert result.snapshot.rights == {"draft": False, "publish": False, "activate": False}
    assert result.snapshot.records[0]["tax_id"] == "9606"
    assert result.snapshot.records[0]["scientific_name"] == "Homo sapiens"
    assert len(result.evidence_sha256) == 64
    assert result.evidence_path.exists()
    assert result.evidence_path.parent == tmp_path
    assert result.evidence_path.name.endswith(".live-acceptance.json")

    evidence = json.loads(result.evidence_path.read_text(encoding="utf-8"))
    assert evidence["schema"] == "morphic_ncbi_taxonomy_live_acceptance"
    assert evidence["source_id"] == NCBI_TAXONOMY_SOURCE_ID
    assert evidence["adapter_version"] == NCBI_TAXONOMY_ADAPTER_VERSION
    assert evidence["network_acceptance"]["dns_pre_connect"] == ["93.184.216.34"]
    assert evidence["network_acceptance"]["dns_post_connect"] == ["93.184.216.34"]
    assert evidence["snapshot"]["publication_state"] == "not_published"
    assert evidence["snapshot"]["rights"] == {
        "draft": False,
        "publish": False,
        "activate": False,
    }
    assert "body" not in json.dumps(evidence).lower()


def test_live_acceptance_rejects_expired_grant_before_transport(tmp_path: Path) -> None:
    transport = RecordingTransport(ncbi_esummary_response())
    resolver = SequencedResolver(("93.184.216.34",), ("93.184.216.34",))

    with pytest.raises(LiveAcceptanceError, match="expired"):
        run_ncbi_taxonomy_live_acceptance(
            source=active_ncbi_source(),
            grant=acceptance_grant(
                expires_at_utc=datetime(2026, 7, 17, 20, 4, tzinfo=timezone.utc)
            ),
            query="9606",
            evidence_dir=tmp_path,
            transport=transport,
            dns_resolver=resolver,
            now_utc=datetime(2026, 7, 17, 20, 5, tzinfo=timezone.utc),
        )

    assert transport.calls == []
    assert resolver.calls == []
    assert list(tmp_path.iterdir()) == []


def test_live_acceptance_rejects_dns_rebinding_without_evidence(tmp_path: Path) -> None:
    transport = RecordingTransport(ncbi_esummary_response())
    resolver = SequencedResolver(("93.184.216.34",), ("10.0.0.5",))

    with pytest.raises(LiveAcceptanceError, match="dns rebinding detected"):
        run_ncbi_taxonomy_live_acceptance(
            source=active_ncbi_source(),
            grant=acceptance_grant(),
            query="9606",
            evidence_dir=tmp_path,
            transport=transport,
            dns_resolver=resolver,
            now_utc=datetime(2026, 7, 17, 20, 5, tzinfo=timezone.utc),
        )

    assert len(transport.calls) == 1
    assert list(tmp_path.iterdir()) == []


class FakeHttpResponse:
    status = 200

    def __init__(self, body: bytes) -> None:
        self._body = body
        self.headers = {"content-type": "application/json; charset=utf-8"}

    def __enter__(self) -> "FakeHttpResponse":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    def geturl(self) -> str:
        return "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    def read(self, limit: int = -1) -> bytes:
        assert limit > 0
        return self._body


class FakeOpener:
    def __init__(self, body: bytes) -> None:
        self.body = body
        self.calls: list[tuple[Any, float]] = []

    def open(self, request: Any, *, timeout: float) -> FakeHttpResponse:
        self.calls.append((request, timeout))
        return FakeHttpResponse(self.body)


def test_urllib_transport_is_explicit_and_has_no_runtime_wiring() -> None:
    body = ncbi_esummary_response().body
    opener = FakeOpener(body)
    transport = UrllibNCBITaxonomyTransport(opener=opener)

    response = transport.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?id=9606",
        timeout_seconds=10.0,
    )

    assert response.status_code == 200
    assert response.body == body
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    request, timeout = opener.calls[0]
    assert timeout == 10.0
    assert request.headers["User-agent"] == "Morphic-F7.3-Live-Acceptance"

    module_source = Path(
        "core/admin_catalog/source_adapters/live_acceptance.py"
    ).read_text(encoding="utf-8")
    forbidden_tokens = (
        "AdminCatalogService",
        "CatalogStore",
        "stage_source_data_batch",
        "activate_revision",
        "publish_revision",
        "localStorage",
    )
    assert all(token not in module_source for token in forbidden_tokens)
