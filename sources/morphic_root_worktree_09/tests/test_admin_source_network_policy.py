from __future__ import annotations

import pytest

from core.source_registry import SourceManifest
from core.admin_catalog.network_policy import (
    AdapterNetworkGrant,
    AdminSourceNetworkPolicy,
    DnsResolutionSet,
    NetworkFetchRequest,
    NetworkPolicyError,
    redact_network_log_data,
)
from core.admin_catalog.source_adapters.base import (
    AdapterSecretError,
    SourceAdapterSecretProvider,
    SourceAdapterSpec,
)


def source(source_id: str, *, enabled: bool = True, status: str = "active") -> SourceManifest:
    return SourceManifest.from_mapping(
        {
            "id": source_id,
            "label": f"Source {source_id}",
            "description": "Network-policy fixture",
            "source_type": "online_api",
            "homepage": "https://example.org",
            "endpoint": "https://example.org/api",
            "license": "source-specific",
            "trust_level": "official",
            "import_policy": "api_manual",
            "scopes": ["terminology"],
            "enabled": enabled,
            "status": status,
        }
    )


def adapter(
    source_id: str = "ncbi_taxonomy",
    *,
    version: str = "2026.07",
    hosts: tuple[str, ...] = ("www.ncbi.nlm.nih.gov",),
    mime_types: tuple[str, ...] = ("application/json",),
    credential_names: tuple[str, ...] = (),
) -> SourceAdapterSpec:
    return SourceAdapterSpec(
        source_id=source_id,
        adapter_version=version,
        allowed_hosts=hosts,
        allowed_mime_types=mime_types,
        credential_names=credential_names,
    )


def request(
    url: str = "https://www.ncbi.nlm.nih.gov/taxonomy",
    *,
    redirects: tuple[str, ...] = (),
    response_size: int = 1024,
    decompressed_size: int = 2048,
    mime_type: str = "application/json",
    timeout_seconds: float = 10.0,
) -> NetworkFetchRequest:
    return NetworkFetchRequest(
        url=url,
        redirect_urls=redirects,
        response_size_bytes=response_size,
        decompressed_size_bytes=decompressed_size,
        response_mime_type=mime_type,
        timeout_seconds=timeout_seconds,
    )


def resolver(*ips: str) -> DnsResolutionSet:
    return DnsResolutionSet(pre_connect=tuple(ips), post_connect=tuple(ips))


def policy_with_grant(
    *,
    source_id: str = "ncbi_taxonomy",
    version: str = "2026.07",
    tenant_id: str = "tenant-a",
) -> AdminSourceNetworkPolicy:
    return AdminSourceNetworkPolicy(
        grants=(
            AdapterNetworkGrant(
                source_id=source_id,
                adapter_version=version,
                tenant_id=tenant_id,
                granted_by="operator-admin",
                reason="explicit adapter test grant",
            ),
        )
    )


def test_active_source_and_registered_adapter_are_default_off_without_exact_grant() -> None:
    policy = AdminSourceNetworkPolicy()
    active_source = source("ncbi_taxonomy")

    decision = policy.evaluate_fetch(
        active_source,
        adapter(),
        tenant_id="tenant-a",
        request=request(),
        admin_authenticated=True,
        dns_resolution=resolver("93.184.216.34"),
    )

    assert decision.allowed is False
    assert decision.reason == "missing adapter network grant"
    assert decision.source_id == "ncbi_taxonomy"


def test_fetch_requires_exact_admin_grant_for_source_adapter_version_and_tenant() -> None:
    active_source = source("ncbi_taxonomy")
    exact_policy = policy_with_grant()

    assert exact_policy.evaluate_fetch(
        active_source,
        adapter(),
        tenant_id="tenant-a",
        request=request(),
        admin_authenticated=True,
        dns_resolution=resolver("93.184.216.34"),
    ).allowed is True

    for tenant_id, spec in (
        ("tenant-b", adapter()),
        ("tenant-a", adapter(version="2026.08")),
        ("tenant-a", adapter(source_id="nlm_mesh")),
    ):
        decision = exact_policy.evaluate_fetch(
            active_source,
            spec,
            tenant_id=tenant_id,
            request=request(),
            admin_authenticated=True,
            dns_resolution=resolver("93.184.216.34"),
        )
        assert decision.allowed is False
        assert decision.reason in {
            "missing adapter network grant",
            "adapter source mismatch",
        }


@pytest.mark.parametrize(
    "blocked_source",
    [
        source("ncbi_taxonomy", enabled=False, status="disabled"),
        source("ncbi_taxonomy", enabled=False, status="quarantined"),
    ],
)
def test_disabled_or_quarantined_source_cannot_fetch_even_with_adapter_grant(
    blocked_source: SourceManifest,
) -> None:
    decision = policy_with_grant().evaluate_fetch(
        blocked_source,
        adapter(),
        tenant_id="tenant-a",
        request=request(),
        admin_authenticated=True,
        dns_resolution=resolver("93.184.216.34"),
    )

    assert decision.allowed is False
    assert decision.reason == "source is not active"


@pytest.mark.parametrize(
    ("bad_request", "reason"),
    [
        (request(url="http://www.ncbi.nlm.nih.gov/taxonomy"), "https required"),
        (request(url="https://evil.example/api"), "host not allowed"),
        (
            request(redirects=("https://evil.example/redirect",)),
            "redirect host not allowed",
        ),
        (request(response_size=20_000_001), "response size limit exceeded"),
        (request(decompressed_size=80_000_001), "decompression limit exceeded"),
        (request(mime_type="text/html"), "mime type not allowed"),
        (request(timeout_seconds=90), "timeout limit exceeded"),
    ],
)
def test_network_request_metadata_must_stay_inside_adapter_safety_limits(
    bad_request: NetworkFetchRequest,
    reason: str,
) -> None:
    decision = policy_with_grant().evaluate_fetch(
        source("ncbi_taxonomy"),
        adapter(),
        tenant_id="tenant-a",
        request=bad_request,
        admin_authenticated=True,
        dns_resolution=resolver("93.184.216.34"),
    )

    assert decision.allowed is False
    assert decision.reason == reason


@pytest.mark.parametrize(
    ("dns_resolution", "reason"),
    [
        (resolver("127.0.0.1"), "unsafe resolved ip"),
        (resolver("10.0.0.5"), "unsafe resolved ip"),
        (resolver("169.254.1.3"), "unsafe resolved ip"),
        (
            DnsResolutionSet(
                pre_connect=("93.184.216.34",),
                post_connect=("10.0.0.5",),
            ),
            "dns rebinding detected",
        ),
    ],
)
def test_dns_resolution_rejects_private_loopback_link_local_and_rebinding(
    dns_resolution: DnsResolutionSet,
    reason: str,
) -> None:
    decision = policy_with_grant().evaluate_fetch(
        source("ncbi_taxonomy"),
        adapter(),
        tenant_id="tenant-a",
        request=request(),
        admin_authenticated=True,
        dns_resolution=dns_resolution,
    )

    assert decision.allowed is False
    assert decision.reason == reason


def test_adapter_secret_values_require_injected_provider_and_are_redacted() -> None:
    spec = adapter(credential_names=("api_token",))

    with pytest.raises(AdapterSecretError, match="secret provider"):
        spec.resolve_credentials(None)

    class Provider(SourceAdapterSecretProvider):
        def get_secret(
            self,
            *,
            source_id: str,
            adapter_version: str,
            secret_name: str,
        ) -> str:
            assert (source_id, adapter_version, secret_name) == (
                "ncbi_taxonomy",
                "2026.07",
                "api_token",
            )
            return "super-secret-token"

    credentials = spec.resolve_credentials(Provider())
    assert credentials == {"api_token": "super-secret-token"}

    redacted = redact_network_log_data(
        {
            "url": "https://www.ncbi.nlm.nih.gov/taxonomy?api_token=super-secret-token",
            "headers": {"Authorization": "Bearer super-secret-token"},
            "message": "fetch failed for super-secret-token",
        },
        secrets=credentials.values(),
    )

    assert "super-secret-token" not in repr(redacted)
    assert "REDACTED" in repr(redacted)


def test_adapter_spec_rejects_dynamic_or_unsafe_registration_values() -> None:
    for kwargs in (
        {"source_id": ""},
        {"source_id": "unknown/source"},
        {"adapter_version": ""},
        {"allowed_hosts": ()},
        {"allowed_hosts": ("https://www.ncbi.nlm.nih.gov",)},
    ):
        with pytest.raises(NetworkPolicyError):
            SourceAdapterSpec(
                source_id=str(kwargs.get("source_id", "ncbi_taxonomy")),
                adapter_version=str(kwargs.get("adapter_version", "2026.07")),
                allowed_hosts=kwargs.get(
                    "allowed_hosts",
                    ("www.ncbi.nlm.nih.gov",),
                ),
            )
