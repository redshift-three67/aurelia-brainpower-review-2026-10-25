from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
API_JS = ROOT / "apps" / "web" / "static" / "workbench-api.js"
STATE_JS = ROOT / "apps" / "web" / "static" / "workbench-state.js"


def test_group_draft_card_is_local_only_and_outside_the_scan_form() -> None:
    html = INDEX.read_text(encoding="utf-8")
    start = html.index('id="group-vector-draft"')
    end = html.index('id="scan-form"')
    card = html[start:end]

    assert 'data-vector="group" data-vector-state="local-draft"' in html
    assert 'id="group-draft-label"' in card
    assert 'id="group-draft-members"' in card
    assert 'id="group-members-consent"' in card
    assert 'id="group-persistence-consent"' in card
    assert 'id="group-analysis-consent"' in card
    assert 'id="save-group-draft-button"' in card
    assert 'id="delete-group-draft-button"' in card
    assert 'id="group-draft-state"' in card
    assert "Nicht Teil der Scan-Anfrage" in card
    assert "keine Auswirkung auf den aktuellen Scan" in card
    assert "Browser-Geolocation" in card
    assert 'form="scan-form"' not in card


def test_group_draft_browser_logic_uses_only_dedicated_api_and_no_local_storage() -> None:
    app_js = APP_JS.read_text(encoding="utf-8")
    api_js = API_JS.read_text(encoding="utf-8")
    state_js = STATE_JS.read_text(encoding="utf-8")

    for method in (
        "loadGroupDrafts",
        "saveGroupDraft",
        "loadGroupDraft",
        "deleteGroupDraft",
        "dryRunGroupDraftErasure",
    ):
        assert f"async {method}" in api_js
    assert "/api/workbench/group-draft" in api_js
    assert "function groupDraftPayload" in app_js
    assert "saveGroupDraft" in app_js
    assert "deleteGroupDraft" in app_js
    assert "group_label:" not in app_js[app_js.index("function formScanPayload"):app_js.index("function clientContextDraftPayload")]
    assert "group" not in state_js.lower() or "localStorage" not in state_js.lower()


def test_group_draft_ui_wires_consent_load_erasure_and_reset() -> None:
    app_js = APP_JS.read_text(encoding="utf-8")

    assert 'persistence.addEventListener("change"' in app_js
    assert "async function loadInitialGroupDraft" in app_js
    assert "MorphicWorkbenchApi.loadGroupDrafts()" in app_js
    assert "MorphicWorkbenchApi.loadGroupDraft(draftId)" in app_js
    assert 'dryRun.addEventListener("click"' in app_js
    assert "MorphicWorkbenchApi.dryRunGroupDraftErasure()" in app_js
    assert "function resetGroupDraftForm" in app_js
    assert "resetGroupDraftForm();" in app_js
