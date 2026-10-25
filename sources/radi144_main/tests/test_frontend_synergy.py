"""R-15/R-16/R-17/R-19: Frontend-Synergie-Regression-Guard.

Pins die Ausrichtung der editierbaren Frontend-Oberflaechen (workflow_stepping +
EMF-Monitor) auf das kanonische LIGHT "Heilsames Design" (Salbeigrün/Sand/Terracotta,
gleiche Token-Quelle wie user_workflow.css). Verhindert Rueckfall auf das DARK
neon-cyan-Theme bzw. den Google-Fonts-CDN (DSGVO-IP-Leak).

user_workflow.* (aktive Nutzer-Vorarbeit) wird hier NICHT beruehrt.
"""
from pathlib import Path

from fastapi.testclient import TestClient

from main import app

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------------ workflow_stepping
def test_workflow_stepping_css_uses_heilsames_light_tokens():
    css = (PROJECT_ROOT / "workflow_stepping.css").read_text(encoding="utf-8")
    # Kanonischer Salbeigrün-Primary (Heilsames Design)
    assert "hsl(145 25% 36%)" in css
    assert "--primary" in css and "--sand" in css and "--accent" in css
    # Kein Rueckfall auf das DARK neon-cyan-Theme
    assert "--bg: #06080f" not in css
    assert "#00d4ff33" not in css  # alter cyan-alpha-Border


def test_workflow_stepping_css_no_dark_neon_root():
    css = (PROJECT_ROOT / "workflow_stepping.css").read_text(encoding="utf-8")
    # Der alte DARK :root-Block darf nicht mehr existieren
    assert "--bg:#06080f" not in css
    assert "--cyan:#00d4ff;" not in css
    assert "--sans:'Inter'" not in css  # alter Font-Stack


def test_workflow_stepping_html_has_no_google_fonts_cdn():
    html = (PROJECT_ROOT / "workflow_stepping.html").read_text(encoding="utf-8")
    assert "fonts.googleapis.com" not in html
    assert "fonts.gstatic.com" not in html


# ------------------------------------------------------------------ EMF-Monitor (inline)
def test_emf_monitor_page_returns_heilsames_light_theme():
    client = TestClient(app)
    res = client.get("/api/v1/emf/monitor")
    assert res.status_code == 200
    body = res.text
    # Kanonische Heilsames-Token im inline :root
    assert "hsl(145 25% 36%)" in body  # --primary Salbeigrün
    assert "hsl(40 30% 97%)" in body  # --bg warmes Elfenbein
    assert "var(--primary)" in body
    # Kein Rueckfall auf DARK hardcoded
    assert "#0a0e17" not in body
    assert "#141b2d" not in body
    assert "#00d4ff" not in body  # alter Cyan (kanonisch jetzt Salbeigrün via var)


def test_emf_monitor_page_has_no_google_fonts_cdn():
    body = TestClient(app).get("/api/v1/emf/monitor").text
    assert "fonts.googleapis.com" not in body
    assert "fonts.gstatic.com" not in body


def test_emf_monitor_keeps_version_and_endpoint_semantics():
    body = TestClient(app).get("/api/v1/emf/monitor").text
    # Bewahrte funktionale Semantik (nicht nur Re-Theme)
    assert "v1.5.0" in body
    assert "WebSocket" in body
    assert "EMF Live-Monitor" in body