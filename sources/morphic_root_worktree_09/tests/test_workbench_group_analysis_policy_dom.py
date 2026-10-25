from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
API_JS = ROOT / "apps" / "web" / "static" / "workbench-api.js"


def test_group_analysis_policy_panel_is_outside_scan_form_and_explicit() -> None:
    html = INDEX.read_text(encoding="utf-8")
    start = html.index('id="group-analysis-policy-panel"')
    end = html.index('id="scan-form"')
    panel = html[start:end]

    assert 'id="group-analysis-feature-state"' in panel
    assert 'id="group-analysis-strength"' in panel
    assert 'min="0"' in panel
    assert 'max="1"' in panel
    assert 'step="0.01"' in panel
    assert 'id="save-group-analysis-policy-button"' in panel
    assert 'id="group-analysis-policy-state"' in panel
    assert "Keine Scanaktivierung" in panel
    assert "serverseitige Kill-Switch" in panel
    assert 'form="scan-form"' not in panel


def test_group_analysis_policy_browser_uses_dedicated_api_only() -> None:
    app_js = APP_JS.read_text(encoding="utf-8")
    api_js = API_JS.read_text(encoding="utf-8")

    assert "async loadGroupAnalysisPolicy" in api_js
    assert "async saveGroupAnalysisPolicy" in api_js
    assert "/api/workbench/group-analysis-policy" in api_js
    assert "function wireGroupAnalysisPolicy" in app_js
    assert "MorphicWorkbenchApi.loadGroupAnalysisPolicy()" in app_js
    assert "MorphicWorkbenchApi.saveGroupAnalysisPolicy({strength})" in app_js
    assert "strength: null" not in app_js


def test_group_analysis_strength_is_not_added_to_scan_payload() -> None:
    app_js = APP_JS.read_text(encoding="utf-8")
    scan_payload = app_js[
        app_js.index("function formScanPayload"):
        app_js.index("function clientContextDraftPayload")
    ]

    assert "group_strength" not in scan_payload
    assert "group-analysis-strength" not in scan_payload
    assert "MORPHIC_GROUP_ANALYSIS_ENABLED" not in app_js
