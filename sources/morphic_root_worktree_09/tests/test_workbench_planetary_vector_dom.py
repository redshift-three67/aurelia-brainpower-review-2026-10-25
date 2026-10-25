from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


def test_planetary_vector_requires_explicit_disabled_by_default_opt_in() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    js = APP_JS.read_text(encoding="utf-8")

    assert 'name="planetary_vector_enabled"' in html
    assert 'name="planet_type"' in html
    assert 'name="planetary_vector_enabled" type="checkbox"' in html
    assert 'name="planetary_vector_enabled" type="checkbox" checked' not in html
    assert 'value="Venus"' in html
    assert 'planetary_vector_enabled: data.get("planetary_vector_enabled") === "on"' in js
    assert 'planet_type: String(data.get("planet_type") || "").trim()' in js
