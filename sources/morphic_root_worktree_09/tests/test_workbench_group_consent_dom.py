from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
API_JS = ROOT / "apps" / "web" / "static" / "workbench-api.js"
STATE_JS = ROOT / "apps" / "web" / "static" / "workbench-state.js"


def test_group_consent_panel_is_dedicated_and_outside_scan_form() -> None:
    html = INDEX.read_text(encoding="utf-8")
    start = html.index('id="group-consent-panel"')
    end = html.index('id="scan-form"')
    panel = html[start:end]

    for element_id in (
        "group-identity-first-name",
        "group-identity-last-name",
        "group-identity-birth-date",
        "group-identity-birth-place",
        "group-identity-retention-days",
        "group-identity-persistence-consent",
        "register-group-identity-button",
        "group-consent-client-id",
        "group-consent-valid-until",
        "group-consent-confirmation",
        "enable-group-consent-button",
        "revoke-group-consent-button",
        "group-consent-state",
    ):
        assert f'id="{element_id}"' in panel
    assert "Keine Scanaktivierung" in panel
    assert "keine Gruppenwirkung" in panel
    assert 'form="scan-form"' not in panel


def test_group_consent_browser_uses_only_dedicated_api_and_no_local_storage() -> None:
    app_js = APP_JS.read_text(encoding="utf-8")
    api_js = API_JS.read_text(encoding="utf-8")
    state_js = STATE_JS.read_text(encoding="utf-8")

    for method in ("loadGroupConsents", "registerGroupIdentity", "setGroupConsent"):
        assert f"async {method}" in api_js
    assert "/api/workbench/group-consent" in api_js
    assert "function groupIdentityRegistrationPayload" in app_js
    assert "function wireGroupConsent" in app_js
    assert "registerGroupIdentity" in app_js
    assert "setGroupConsent" in app_js
    assert "group-consent" not in state_js.lower()


def test_group_consent_controls_require_explicit_persistence_and_confirmation() -> None:
    app_js = APP_JS.read_text(encoding="utf-8")

    assert 'identityPersistence.addEventListener("change"' in app_js
    assert "register.disabled = !identityPersistence.checked" in app_js
    assert "confirmation.value.trim() === activeGroupConsentClientId" in app_js
    assert "valid_until: enabled ?" in app_js
    assert "confirmation_id: confirmation.value.trim()" in app_js
    assert "enabled: false" in app_js
    assert "loadInitialGroupConsent" in app_js
