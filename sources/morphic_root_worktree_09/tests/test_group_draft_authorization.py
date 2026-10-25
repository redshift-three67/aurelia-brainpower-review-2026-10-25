from __future__ import annotations

import pytest

from apps.web.client_context_contracts import GroupContextDraft
from apps.web.group_analysis_activation import build_group_draft_authorization
from core.compliance.operator_context import OperatorContext


CONTEXT = OperatorContext(operator_id="operator-a", workspace_id="ws-a", tenant_id="tenant-a")


def _draft(*, analysis_consent: bool = False) -> GroupContextDraft:
    return GroupContextDraft(
        group_label="Morgenkreis",
        members=[
            {"client_id": "cli-alpha", "consent_recorded": True},
            {"client_id": "cli-beta", "consent_recorded": True},
        ],
        persistence_consent=True,
        analysis_consent=analysis_consent,
        retention_days=30,
    )


def test_group_draft_requires_separate_analysis_consent_and_exposes_only_safe_state() -> None:
    draft = _draft()

    assert draft.analysis_consent is False
    with pytest.raises(ValueError, match="analysis consent"):
        build_group_draft_authorization(draft, subject_id="cli-alpha", context=CONTEXT)


def test_consented_group_draft_binds_only_an_enrolled_subject_to_current_operator() -> None:
    authorization = build_group_draft_authorization(
        _draft(analysis_consent=True),
        subject_id="cli-alpha",
        context=CONTEXT,
    )

    assert authorization.subject_id == "cli-alpha"
    assert authorization.owner_id == "operator-a"
    assert authorization.member_count == 2
    assert authorization.member_consent_verified is True
    assert authorization.safe_summary() == {
        "vector": "group",
        "purpose": "group-analysis-v1",
        "member_count": 2,
        "activation_requested": True,
    }


def test_group_draft_authorization_rejects_a_subject_outside_the_consented_group() -> None:
    with pytest.raises(ValueError, match="enrolled"):
        build_group_draft_authorization(
            _draft(analysis_consent=True),
            subject_id="cli-outsider",
            context=CONTEXT,
        )
