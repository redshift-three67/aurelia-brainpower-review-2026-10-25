from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_JS = ROOT / "apps" / "web" / "static" / "workbench-state.js"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
HTML = ROOT / "apps" / "web" / "static" / "index.html"


def test_focus_history_requires_explicit_opt_in_and_has_a_clear_action() -> None:
    state = STATE_JS.read_text(encoding="utf-8")
    app = APP_JS.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")

    assert "FOCUS_HISTORY_CONSENT_KEY" in state
    assert "hasFocusHistoryConsent()" in state
    assert "clearFocusHistory()" in state
    assert "if (!this.hasFocusHistoryConsent()) return [];" in state
    assert "if (!this.hasFocusHistoryConsent()) return;" in state
    assert 'id="focus-history-consent"' in html
    assert 'id="clear-focus-history"' in html
    assert "setFocusHistoryConsent" in app
    assert "clearFocusHistory" in app
