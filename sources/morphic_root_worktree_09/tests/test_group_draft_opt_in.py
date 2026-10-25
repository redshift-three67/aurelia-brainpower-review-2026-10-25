from __future__ import annotations

import numpy as np
import pytest

from apps.web.client_context_contracts import GroupContextDraft
from apps.web.group_analysis_activation import build_group_draft_opt_in
from core.compliance.operator_context import OperatorContext
from core.profiles.profile import ClientProfile
from services.analysis_service import AnalysisService


CONTEXT = OperatorContext(operator_id="operator-a", workspace_id="ws-a", tenant_id="tenant-a")


def _draft() -> GroupContextDraft:
    return GroupContextDraft(
        group_label="Morgenkreis",
        members=[
            {"client_id": "cli-alpha", "consent_recorded": True},
            {"client_id": "cli-beta", "consent_recorded": True},
        ],
        persistence_consent=True,
        analysis_consent=True,
        retention_days=30,
    )


def _service() -> AnalysisService:
    return AnalysisService(
        {"system_a": [10.0, 20.0, 30.0], "system_b": [40.0, 50.0, 60.0]},
        h_level=0.3,
    )


def _profile() -> ClientProfile:
    return ClientProfile(
        name="Synthetic",
        first_name="Group",
        birth_date="01011990",
        birth_place="Bern",
    )


def test_consented_local_group_draft_can_create_an_in_memory_opt_in_that_changes_analysis() -> None:
    service = _service()
    profile = _profile()
    default_result = service.analyze(profile)
    baseline = default_result["rates"]

    group_opt_in = build_group_draft_opt_in(
        _draft(),
        subject_id="cli-alpha",
        context=CONTEXT,
        member_rates={
            "cli-alpha": baseline,
            "cli-beta": baseline + 8.0,
        },
        strength=0.25,
    )
    opted_in_result = service.analyze(profile, group_opt_in=group_opt_in)

    assert group_opt_in.enabled is True
    assert group_opt_in.consent_verified is True
    assert not np.array_equal(opted_in_result["rates"], default_result["rates"])
    assert opted_in_result["morphic_field"] != default_result["morphic_field"]


def test_group_draft_opt_in_rejects_missing_or_unenrolled_member_rates() -> None:
    baseline = _service().encode_profile(_profile())

    with pytest.raises(ValueError, match="member rates"):
        build_group_draft_opt_in(
            _draft(),
            subject_id="cli-alpha",
            context=CONTEXT,
            member_rates={"cli-alpha": baseline},
            strength=0.25,
        )
    with pytest.raises(ValueError, match="member rates"):
        build_group_draft_opt_in(
            _draft(),
            subject_id="cli-alpha",
            context=CONTEXT,
            member_rates={
                "cli-alpha": baseline,
                "cli-beta": baseline,
                "cli-outsider": baseline,
            },
            strength=0.25,
        )
