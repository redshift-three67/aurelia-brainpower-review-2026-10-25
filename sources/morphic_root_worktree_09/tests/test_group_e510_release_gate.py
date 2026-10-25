from __future__ import annotations

from pathlib import Path

import numpy as np

from apps.web.contracts import Phase1ScanRequest
from core.profiles.profile import ClientProfile
from services.analysis_service import AnalysisService


ROOT = Path(__file__).resolve().parents[1]


def test_e510f_released_browser_path_remains_handle_only_and_bounded() -> None:
    main = (ROOT / "apps" / "web" / "main.py").read_text(encoding="utf-8")
    router = (ROOT / "apps" / "web" / "group_drafts.py").read_text(encoding="utf-8")
    index = (ROOT / "apps" / "web" / "static" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "apps" / "web" / "static" / "app.js").read_text(encoding="utf-8")
    runtime = (ROOT / "core" / "compliance" / "runtime_manifest.py").read_text(encoding="utf-8")

    request_fields = set(Phase1ScanRequest.model_fields)
    assert not {
        "group_opt_in",
        "group_member_rates",
        "group_strength",
        "activation_handle",
    } & request_fields
    assert "group_draft_id" in request_fields
    assert "build_resolved_group_draft_opt_in" not in main
    assert "build_resolved_group_draft_opt_in" not in router
    assert "record_group_analysis_consent" not in main
    assert "group-strength" not in index
    assert "MORPHIC_GROUP_ANALYSIS_ENABLED" not in main
    assert "prepare_group_scan_activation" in main
    assert "env_overrides=activation_environment" in main
    assert '"activation_handle"' not in main
    assert 'id="group-scan-activation-enabled"' in index
    assert 'id="group-scan-draft-id"' in index
    assert "formScanPayload({includeGroupActivation: true})" in app_js
    assert "payload.group_draft_id = draftId" in app_js
    assert "client_entry = self.get_or_create_client(client)" in runtime


def test_e510a_identity_source_has_no_runtime_manifest_fallback() -> None:
    source = (
        ROOT / "core" / "compliance" / "group_member_identity_source.py"
    ).read_text(encoding="utf-8")

    assert "LocalClientIdentityStore" in source
    assert "RuntimeManifestService" not in source
    assert "RuntimeManifestGroupMemberIdentitySource" not in source
    assert ".get_client(" not in source


def test_e510_default_path_remains_exactly_baseline_equivalent() -> None:
    service = AnalysisService(rate_database={}, h_level=0.2)
    profile = ClientProfile(
        name="ReleaseGate",
        first_name="Baseline",
        birth_date="01011980",
        birth_place="Berlin",
    )

    default = service.analyze(profile)
    explicit_none = service.analyze(profile, group_opt_in=None)

    np.testing.assert_array_equal(default["rates"], explicit_none["rates"])
    assert default["morphic_field"] == explicit_none["morphic_field"]
    assert default["holographic_entropy"] == explicit_none["holographic_entropy"]
    np.testing.assert_array_equal(default["heim_signature"], explicit_none["heim_signature"])
