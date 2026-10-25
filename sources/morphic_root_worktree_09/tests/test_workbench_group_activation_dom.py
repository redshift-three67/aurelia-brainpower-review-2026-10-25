from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
STATE_JS = ROOT / "apps" / "web" / "static" / "workbench-state.js"


def _function(source: str, name: str, next_name: str) -> str:
    return source[source.index(f"function {name}"):source.index(f"function {next_name}")]


def test_group_scan_activation_controls_are_explicit_and_outside_scan_form() -> None:
    html = INDEX.read_text(encoding="utf-8")
    start = html.index('id="group-scan-activation-panel"')
    end = html.index('id="scan-form"')
    panel = html[start:end]

    assert 'id="group-scan-activation-enabled"' in panel
    assert 'id="group-scan-draft-id"' in panel
    assert '<option value="" selected>Keine Gruppe aktivieren</option>' in panel
    assert 'id="group-scan-activation-state"' in panel
    assert "bewusst" in panel.lower()
    assert "keine produktive wirkung" in panel.lower()
    assert 'form="scan-form"' not in panel


def test_scan_payload_adds_only_explicit_group_draft_id_for_real_start() -> None:
    app_js = APP_JS.read_text(encoding="utf-8")
    payload = _function(app_js, "formScanPayload", "clientContextDraftPayload")
    preview = app_js[app_js.index("async function generatePreview"):app_js.index("async function startScanJob")]
    start = app_js[app_js.index("async function startScanJob"):app_js.index("async function pollScanJob")]

    assert "includeGroupActivation" in payload
    assert '$("#group-scan-activation-enabled")' in payload
    assert '$("#group-scan-draft-id")' in payload
    assert "payload.group_draft_id" in payload
    for forbidden in (
        "group_member_rates",
        "group_opt_in",
        "group_centroid",
        "group_subject_id",
        "activation_handle",
    ):
        assert forbidden not in payload
    assert "includeGroupActivation" not in preview
    assert "formScanPayload({includeGroupActivation: true})" in start
    assert "validateScanPayload(body, {includeGroupActivation: true})" in start


def test_group_activation_selection_is_not_implicitly_loaded_or_persisted() -> None:
    app_js = APP_JS.read_text(encoding="utf-8")
    state_js = STATE_JS.read_text(encoding="utf-8")
    initial_load = _function(app_js, "loadInitialGroupDraft", "wireGroupDraft")
    template_handler = app_js[app_js.index('const saveTemplate = $("#save-template-button")'):app_js.index('const newCase = $("#new-case-button")')]

    assert "renderGroupActivationDraftOptions" in initial_load
    assert "selectedIndex = 0" in initial_load
    assert "group_draft_id" not in template_handler
    assert "includeGroupActivation" not in template_handler
    assert "group_draft" not in state_js.lower()
    assert "activation_handle" not in state_js.lower()
    assert "sessionStorage" not in state_js


def test_group_activation_status_reflects_server_policy_without_exposing_handle() -> None:
    app_js = APP_JS.read_text(encoding="utf-8")

    assert "function updateGroupScanActivationState" in app_js
    assert "feature_enabled" in app_js
    assert "strength_explicit" in app_js
    assert "Keine produktive Wirkung" in app_js
    assert "activation_handle" not in app_js
