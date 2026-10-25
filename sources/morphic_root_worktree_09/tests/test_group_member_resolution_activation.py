from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from apps.web.client_context_contracts import GroupContextDraft
from apps.web.group_analysis_activation import build_resolved_group_draft_opt_in
from core.compliance.group_member_identity_source import LocalClientIdentitySource
from core.compliance.local_client_identity_store import LocalClientIdentityStore
from core.compliance.operator_context import OperatorContext
from core.profiles.group_member_rate_resolver import GROUP_MEMBER_CONSENT_VERSION
from core.profiles.profile import ClientProfile
from services.analysis_service import AnalysisService


CONTEXT = OperatorContext(
    operator_id="operator-local",
    workspace_id="ws-local",
    tenant_id="tenant-local",
)


def _register_member(
    service: LocalClientIdentityStore,
    *,
    first_name: str,
    last_name: str,
    birth_date: str,
    birth_place: str,
) -> tuple[str, ClientProfile]:
    client = {
        "first_name": first_name,
        "last_name": last_name,
        "birth_date": birth_date,
        "birth_place": birth_place,
    }
    client_id = service.register(client, context=CONTEXT)["client_id"]
    service.record_group_analysis_consent(
        client_id,
        context=CONTEXT,
        enabled=True,
        consent_version=GROUP_MEMBER_CONSENT_VERSION,
        valid_until=datetime.now(UTC) + timedelta(days=30),
    )
    return client_id, ClientProfile(name=last_name, first_name=first_name, birth_date=birth_date, birth_place=birth_place)


def _draft(member_ids: list[str], *, analysis_consent: bool = True) -> GroupContextDraft:
    return GroupContextDraft(
        group_label="Synthetische Resolver-Gruppe",
        members=[
            {"client_id": client_id, "consent_recorded": True}
            for client_id in member_ids
        ],
        persistence_consent=True,
        analysis_consent=analysis_consent,
        retention_days=30,
    )


def test_runtime_source_resolves_draft_members_into_a_real_in_memory_opt_in(
    tmp_path: Path,
) -> None:
    identity_store = LocalClientIdentityStore(tmp_path / "client-identities")
    alpha_id, alpha_profile = _register_member(
        identity_store,
        first_name="Anna",
        last_name="Alpha",
        birth_date="01011980",
        birth_place="Berlin",
    )
    beta_id, _ = _register_member(
        identity_store,
        first_name="Berta",
        last_name="Beta",
        birth_date="02021982",
        birth_place="Bern",
    )
    source = LocalClientIdentitySource(identity_store, context=CONTEXT)
    analysis = AnalysisService(rate_database={}, h_level=0.2)
    baseline = analysis.analyze(alpha_profile)

    opt_in = build_resolved_group_draft_opt_in(
        _draft([alpha_id, beta_id]),
        subject_id=alpha_id,
        context=CONTEXT,
        source=source,
        strength=0.25,
    )
    result = analysis.analyze(alpha_profile, group_opt_in=opt_in)

    assert opt_in.enabled is True
    assert opt_in.consent_verified is True
    assert opt_in.centroid_rates is not None
    assert not np.array_equal(result["rates"], baseline["rates"])
    assert result["morphic_field"] != baseline["morphic_field"]


def test_draft_analysis_consent_is_checked_before_identity_source_access() -> None:
    class CountingSource:
        calls = 0

        def resolve(self, client_id: str):
            self.calls += 1
            raise AssertionError("identity source must not be read without draft consent")

    source = CountingSource()
    with pytest.raises(ValueError, match="analysis consent"):
        build_resolved_group_draft_opt_in(
            _draft(["cli-alpha", "cli-beta"], analysis_consent=False),
            subject_id="cli-alpha",
            context=CONTEXT,
            source=source,
            strength=0.25,
        )

    assert source.calls == 0


def test_resolved_draft_flow_fails_closed_when_any_member_is_unresolvable(
    tmp_path: Path,
) -> None:
    identity_store = LocalClientIdentityStore(tmp_path / "client-identities")
    alpha_id, _ = _register_member(
        identity_store,
        first_name="Anna",
        last_name="Alpha",
        birth_date="01011980",
        birth_place="Berlin",
    )
    source = LocalClientIdentitySource(identity_store, context=CONTEXT)

    with pytest.raises(LookupError):
        build_resolved_group_draft_opt_in(
            _draft([alpha_id, "cli-00000000000000000000"]),
            subject_id=alpha_id,
            context=CONTEXT,
            source=source,
            strength=0.25,
        )


def test_resolved_draft_bridge_is_not_mounted_as_a_route_or_scan_input() -> None:
    root = Path(__file__).resolve().parents[1]
    main = (root / "apps" / "web" / "main.py").read_text(encoding="utf-8")
    router = (root / "apps" / "web" / "group_drafts.py").read_text(encoding="utf-8")
    contracts = (root / "apps" / "web" / "contracts.py").read_text(encoding="utf-8")

    assert "build_resolved_group_draft_opt_in" not in main
    assert "build_resolved_group_draft_opt_in" not in router
    assert "group_member_rates" not in contracts
    assert "group_opt_in" not in contracts
