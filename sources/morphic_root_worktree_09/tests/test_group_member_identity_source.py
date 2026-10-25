from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from core.compliance.group_member_identity_source import LocalClientIdentitySource
from core.compliance.local_client_identity_store import LocalClientIdentityStore
from core.compliance.operator_context import OperatorContext, OwnershipError
from core.compliance.runtime_manifest import RuntimeManifestService
from core.profiles.group_member_rate_resolver import GROUP_MEMBER_CONSENT_VERSION


def _context(
    *,
    operator_id: str = "operator-local",
    workspace_id: str = "ws-local",
    tenant_id: str = "tenant-local",
) -> OperatorContext:
    return OperatorContext(
        operator_id=operator_id,
        workspace_id=workspace_id,
        tenant_id=tenant_id,
    )


def _client() -> dict[str, str]:
    return {
        "first_name": "Anna",
        "last_name": "Alpha",
        "birth_date": "01011980",
        "birth_place": "Berlin",
    }


def _trusted_client(service: LocalClientIdentityStore) -> str:
    context = _context()
    client_id = service.register(_client(), context=context)["client_id"]
    service.record_group_analysis_consent(
        client_id,
        context=context,
        enabled=True,
        consent_version=GROUP_MEMBER_CONSENT_VERSION,
        valid_until=datetime.now(UTC) + timedelta(days=30),
    )
    return client_id


def test_new_runtime_client_can_be_resolved_only_after_bound_consent(tmp_path: Path) -> None:
    service = LocalClientIdentityStore(tmp_path / "client-identities")
    context = _context()
    client_id = service.register(_client(), context=context)["client_id"]
    source = LocalClientIdentitySource(service, context=context)

    with pytest.raises(ValueError, match="consent"):
        source.resolve(client_id)

    service.record_group_analysis_consent(
        client_id,
        context=context,
        enabled=True,
        consent_version=GROUP_MEMBER_CONSENT_VERSION,
        valid_until=datetime.now(UTC) + timedelta(days=30),
    )
    identity = source.resolve(client_id)

    assert identity.client_id == client_id
    assert identity.owner_id == "ws-local"
    assert identity.tenant_id == "tenant-local"
    assert identity.first_name == "Anna"
    assert identity.last_name == "Alpha"
    assert identity.analysis_consent is True
    assert identity.consent_version == GROUP_MEMBER_CONSENT_VERSION

    safe_text = str(service.list_safe(context=context))
    assert client_id in safe_text
    assert "Anna" not in safe_text
    assert "Berlin" not in safe_text
    assert "tenant-local" not in safe_text
    assert "ws-local" not in safe_text
    assert GROUP_MEMBER_CONSENT_VERSION in safe_text


def test_legacy_runtime_client_is_not_silently_trusted_or_migrated(tmp_path: Path) -> None:
    runtime = RuntimeManifestService(tmp_path / "runtime")
    legacy = runtime.get_or_create_client(_client())
    identity_store = LocalClientIdentityStore(tmp_path / "runtime" / "client-identities")
    source = LocalClientIdentitySource(identity_store, context=_context())

    with pytest.raises(LookupError, match="identity"):
        source.resolve(legacy["client_id"])

    unchanged = runtime.load_store("clients")["clients"][0]
    assert "owner_id" not in unchanged
    assert "tenant_id" not in unchanged
    assert "group_analysis" not in unchanged

    with pytest.raises(ValueError, match="legacy|bound"):
        runtime.record_group_analysis_consent(
            legacy["client_id"],
            context=_context(),
            enabled=True,
            consent_version=GROUP_MEMBER_CONSENT_VERSION,
            valid_until=datetime.now(UTC) + timedelta(days=30),
        )


def test_identity_source_fails_closed_for_foreign_owner_tenant_and_revocation(
    tmp_path: Path,
) -> None:
    service = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = _trusted_client(service)

    with pytest.raises(OwnershipError):
        LocalClientIdentitySource(
            service,
            context=_context(workspace_id="ws-foreign"),
        ).resolve(client_id)

    with pytest.raises(OwnershipError):
        LocalClientIdentitySource(
            service,
            context=_context(tenant_id="tenant-foreign"),
        ).resolve(client_id)

    service.record_group_analysis_consent(
        client_id,
        context=_context(),
        enabled=False,
        consent_version=GROUP_MEMBER_CONSENT_VERSION,
        valid_until=datetime.now(UTC) + timedelta(days=30),
    )
    with pytest.raises(ValueError, match="consent"):
        LocalClientIdentitySource(
            service,
            context=_context(),
        ).resolve(client_id)


def test_identity_source_rejects_unknown_tampered_and_stale_consent(tmp_path: Path) -> None:
    service = LocalClientIdentityStore(tmp_path / "client-identities")
    client_id = _trusted_client(service)
    source = LocalClientIdentitySource(service, context=_context())

    with pytest.raises(LookupError):
        source.resolve("cli-00000000000000000000")

    record = service._read(client_id)
    record["birth_place"] = "Hamburg"
    service._write(client_id, record)
    with pytest.raises(ValueError, match="identity|client_id"):
        source.resolve(client_id)

    record["birth_place"] = "Berlin"
    record["group_analysis"]["consent_version"] = "legacy-consent"
    service._write(client_id, record)
    with pytest.raises(ValueError, match="version"):
        source.resolve(client_id)


def test_consent_safe_summary_is_redacted(tmp_path: Path) -> None:
    service = LocalClientIdentityStore(tmp_path / "client-identities")
    _trusted_client(service)

    entries = service.list_safe(context=_context())

    assert len(entries) == 1
    text = str(entries[0])
    assert "Anna" not in text
    assert "Berlin" not in text
    assert "rates" not in text
    assert entries[0]["consent_enabled"] is True
    assert entries[0]["consent_version"] == GROUP_MEMBER_CONSENT_VERSION
