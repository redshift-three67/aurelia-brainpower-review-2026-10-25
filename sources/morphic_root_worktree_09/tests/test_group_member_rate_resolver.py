from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from core.compliance.operator_context import OperatorContext, OwnershipError
from core.profiles.group_member_rate_resolver import (
    GROUP_MEMBER_CONSENT_VERSION,
    GROUP_MEMBER_RESOLVER_VERSION,
    GroupMemberIdentity,
    resolve_group_member_rates,
)
from core.profiles.profile import ClientProfile
from services.analysis_service import AnalysisService


class FakeIdentitySource:
    def __init__(self, identities: list[GroupMemberIdentity]) -> None:
        self._identities = {identity.client_id: identity for identity in identities}

    def resolve(self, client_id: str) -> GroupMemberIdentity:
        if client_id not in self._identities:
            raise LookupError("unknown member")
        return self._identities[client_id]


def _context() -> OperatorContext:
    return OperatorContext(
        operator_id="operator-local",
        workspace_id="ws-local",
        tenant_id="tenant-local",
    )


def _identity(client_id: str, *, first_name: str, last_name: str) -> GroupMemberIdentity:
    return GroupMemberIdentity(
        client_id=client_id,
        owner_id="operator-local",
        tenant_id="tenant-local",
        first_name=first_name,
        last_name=last_name,
        birth_date="01011980",
        birth_place="Berlin",
        analysis_consent=True,
        consent_version=GROUP_MEMBER_CONSENT_VERSION,
    )


def test_resolver_builds_deterministic_existing_engine_baselines() -> None:
    alpha = _identity("cli-alpha", first_name="Anna", last_name="Alpha")
    beta = _identity("cli-beta", first_name="Berta", last_name="Beta")
    source = FakeIdentitySource([alpha, beta])

    first = resolve_group_member_rates(
        ["cli-beta", "cli-alpha"],
        source=source,
        context=_context(),
    )
    second = resolve_group_member_rates(
        ["cli-alpha", "cli-beta"],
        source=source,
        context=_context(),
    )

    expected_alpha = AnalysisService(rate_database={}, h_level=0.0).encode_profile(
        ClientProfile(
            name="Alpha",
            first_name="Anna",
            birth_date="01011980",
            birth_place="Berlin",
            image_signature=None,
            personal_profile=None,
            planet_type="",
        )
    )

    assert list(first.member_rates) == ["cli-alpha", "cli-beta"]
    assert list(second.member_rates) == ["cli-alpha", "cli-beta"]
    np.testing.assert_array_equal(first.member_rates["cli-alpha"], expected_alpha)
    np.testing.assert_array_equal(
        first.member_rates["cli-alpha"], second.member_rates["cli-alpha"]
    )
    assert first.resolver_version == GROUP_MEMBER_RESOLVER_VERSION


def test_resolver_safe_summary_contains_no_identity_or_rates() -> None:
    source = FakeIdentitySource(
        [
            _identity("cli-alpha", first_name="Anna", last_name="Alpha"),
            _identity("cli-beta", first_name="Berta", last_name="Beta"),
        ]
    )

    resolution = resolve_group_member_rates(
        ["cli-alpha", "cli-beta"],
        source=source,
        context=_context(),
    )
    summary = resolution.safe_summary()
    text = str(summary)

    assert summary == {
        "resolver_version": GROUP_MEMBER_RESOLVER_VERSION,
        "member_count": 2,
        "purpose": "group-analysis-v1",
    }
    assert "cli-alpha" not in text
    assert "Anna" not in text
    assert str(resolution.member_rates["cli-alpha"][0]) not in text


@pytest.mark.parametrize(
    ("member_ids", "identity_change", "context", "error_type"),
    [
        (["cli-alpha"], {}, _context(), ValueError),
        (["cli-alpha", "cli-alpha"], {}, _context(), ValueError),
        (["cleartext-alpha", "cli-beta"], {}, _context(), ValueError),
        (
            ["cli-alpha", "cli-beta"],
            {"owner_id": "foreign-owner"},
            _context(),
            OwnershipError,
        ),
        (
            ["cli-alpha", "cli-beta"],
            {"tenant_id": "foreign-tenant"},
            _context(),
            OwnershipError,
        ),
        (
            ["cli-alpha", "cli-beta"],
            {"analysis_consent": False},
            _context(),
            ValueError,
        ),
        (
            ["cli-alpha", "cli-beta"],
            {"consent_version": "legacy-consent"},
            _context(),
            ValueError,
        ),
    ],
)
def test_resolver_fails_closed_for_invalid_membership_and_authorization(
    member_ids: list[str],
    identity_change: dict[str, object],
    context: OperatorContext,
    error_type: type[Exception],
) -> None:
    alpha = replace(
        _identity("cli-alpha", first_name="Anna", last_name="Alpha"),
        **identity_change,
    )
    source = FakeIdentitySource(
        [alpha, _identity("cli-beta", first_name="Berta", last_name="Beta")]
    )

    with pytest.raises(error_type):
        resolve_group_member_rates(member_ids, source=source, context=context)


def test_resolver_fails_closed_for_unknown_member_and_incomplete_identity() -> None:
    valid = _identity("cli-alpha", first_name="Anna", last_name="Alpha")

    with pytest.raises(LookupError):
        resolve_group_member_rates(
            ["cli-alpha", "cli-missing"],
            source=FakeIdentitySource([valid]),
            context=_context(),
        )

    incomplete = replace(
        _identity("cli-beta", first_name="Berta", last_name="Beta"),
        birth_place="",
    )
    with pytest.raises(ValueError, match="identity fields"):
        resolve_group_member_rates(
            ["cli-alpha", "cli-beta"],
            source=FakeIdentitySource([valid, incomplete]),
            context=_context(),
        )


def test_resolver_rejects_identity_returned_for_another_client() -> None:
    class MismatchedSource:
        def resolve(self, client_id: str) -> GroupMemberIdentity:
            return _identity("cli-other", first_name="Other", last_name="Member")

    with pytest.raises(ValueError, match="requested client_id"):
        resolve_group_member_rates(
            ["cli-alpha", "cli-beta"],
            source=MismatchedSource(),
            context=_context(),
        )


def test_resolver_module_stays_out_of_external_and_artifact_paths() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "core"
        / "profiles"
        / "group_member_rate_resolver.py"
    ).read_text(encoding="utf-8")

    assert "apps.web" not in source
    assert "apps.cli" not in source
    assert "runtime_manifest" not in source
    assert "report" not in source
    assert "artifact" not in source
