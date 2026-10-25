from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from core.compliance.group_analysis_authorization import (
    GroupAnalysisAuthorization,
    authorize_group_opt_in,
)
from core.compliance.operator_context import OperatorContext, OwnershipError
from core.profiles.group_vector import GroupAnalysisOptIn


CONTEXT = OperatorContext(operator_id="operator-a", workspace_id="ws-a", tenant_id="tenant-a")


def _enabled_opt_in() -> GroupAnalysisOptIn:
    return GroupAnalysisOptIn(
        enabled=True,
        centroid_rates=np.asarray([10.0, 20.0, 30.0]),
        strength=0.25,
        consent_verified=True,
    )


def _authorization(**overrides: object) -> GroupAnalysisAuthorization:
    payload: dict[str, object] = {
        "subject_id": "cli-subject",
        "owner_id": "operator-a",
        "member_count": 2,
        "member_consent_verified": True,
        "purpose": "group-analysis-v1",
    }
    payload.update(overrides)
    return GroupAnalysisAuthorization(**payload)


def test_group_analysis_authorization_binds_an_enabled_candidate_to_current_owner() -> None:
    opt_in = _enabled_opt_in()

    authorized = authorize_group_opt_in(opt_in, _authorization(), context=CONTEXT)

    assert authorized is opt_in


def test_group_analysis_authorization_fails_closed_for_wrong_owner_or_incomplete_consent() -> None:
    opt_in = _enabled_opt_in()

    with pytest.raises(OwnershipError):
        authorize_group_opt_in(opt_in, _authorization(owner_id="operator-b"), context=CONTEXT)
    with pytest.raises(ValueError, match="member consent"):
        authorize_group_opt_in(
            opt_in,
            _authorization(member_consent_verified=False),
            context=CONTEXT,
        )
    with pytest.raises(ValueError, match="member_count"):
        authorize_group_opt_in(opt_in, _authorization(member_count=1), context=CONTEXT)


def test_group_analysis_authorization_safe_summary_redacts_subject_owner_and_centroid() -> None:
    authorization = _authorization()

    summary = authorization.safe_summary()

    assert summary == {
        "vector": "group",
        "purpose": "group-analysis-v1",
        "member_count": 2,
        "activation_requested": True,
    }
    assert "cli-subject" not in str(summary)
    assert "operator-a" not in str(summary)
    assert "10.0" not in str(summary)


def test_disabled_group_opt_in_remains_default_without_authorization() -> None:
    disabled = GroupAnalysisOptIn(enabled=False)

    assert authorize_group_opt_in(disabled, None, context=CONTEXT) is disabled


def test_group_authorization_remains_outside_web_cli_and_artifact_paths() -> None:
    root = Path(__file__).resolve().parents[1]
    protected_paths = (
        root / "apps" / "cli" / "commands" / "field.py",
        root / "apps" / "web" / "contracts.py",
        root / "apps" / "web" / "launcher.py",
        root / "apps" / "web" / "main.py",
        root / "core" / "compliance" / "run_manifest.py",
    )

    for path in protected_paths:
        source = path.read_text(encoding="utf-8")
        assert "group_analysis_authorization" not in source
        assert "GroupAnalysisAuthorization" not in source
        assert "authorize_group_opt_in" not in source
