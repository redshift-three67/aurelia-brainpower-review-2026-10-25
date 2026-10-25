from __future__ import annotations

from pathlib import Path

import pytest

from apps.web.main import create_app
from tests.test_web_shell import request


@pytest.fixture
def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("MORPHIC_GROUP_ANALYSIS_ENABLED", raising=False)
    return create_app(runtime_dir=tmp_path / "runtime")


def test_group_analysis_policy_is_default_false_without_hidden_strength(app) -> None:
    response = request(app, "GET", "/api/workbench/group-analysis-policy")

    assert response.status_code == 200
    assert response.json() == {
        "policy_version": "group-analysis-policy-v1",
        "feature_enabled": False,
        "strength": None,
        "strength_explicit": False,
        "analysis_ready": False,
        "productive_effect": False,
    }


def test_group_analysis_policy_accepts_only_explicit_bounded_strength(app) -> None:
    zero = request(
        app,
        "PUT",
        "/api/workbench/group-analysis-policy",
        json_body={"strength": 0.0},
    )
    middle = request(
        app,
        "PUT",
        "/api/workbench/group-analysis-policy",
        json_body={"strength": 0.25},
    )
    too_low = request(
        app,
        "PUT",
        "/api/workbench/group-analysis-policy",
        json_body={"strength": -0.01},
    )
    too_high = request(
        app,
        "PUT",
        "/api/workbench/group-analysis-policy",
        json_body={"strength": 1.01},
    )
    missing = request(
        app,
        "PUT",
        "/api/workbench/group-analysis-policy",
        json_body={},
    )

    assert zero.status_code == 200
    assert zero.json()["strength"] == 0.0
    assert zero.json()["feature_enabled"] is False
    assert zero.json()["productive_effect"] is False
    assert middle.status_code == 200
    assert middle.json()["strength"] == 0.25
    assert middle.json()["analysis_ready"] is False
    assert too_low.status_code == 422
    assert too_high.status_code == 422
    assert missing.status_code == 422


def test_group_analysis_feature_flag_is_server_owned_but_still_not_productive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MORPHIC_GROUP_ANALYSIS_ENABLED", "1")
    app = create_app(runtime_dir=tmp_path / "runtime")

    response = request(
        app,
        "PUT",
        "/api/workbench/group-analysis-policy",
        json_body={"strength": 0.5},
    )

    assert response.status_code == 200
    assert response.json()["feature_enabled"] is True
    assert response.json()["strength_explicit"] is True
    assert response.json()["analysis_ready"] is False
    assert response.json()["productive_effect"] is False


def test_group_analysis_policy_router_has_no_scan_or_resolver_activation_imports() -> None:
    source = Path(__file__).resolve().parents[1] / "apps" / "web" / "group_analysis_policy.py"
    text = source.read_text(encoding="utf-8")

    assert "AnalysisService" not in text
    assert "Phase1ScanRequest" not in text
    assert "group_analysis_activation" not in text
    assert "build_resolved_group_draft_opt_in" not in text
    assert "LocalClientIdentitySource" not in text
