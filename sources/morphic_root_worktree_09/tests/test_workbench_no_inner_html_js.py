from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"


def test_remaining_static_renderers_avoid_inner_html_and_preview_is_sandboxed() -> None:
    renderer = RENDER_JS.read_text(encoding="utf-8")
    app = APP_JS.read_text(encoding="utf-8")
    index_html = INDEX_HTML.read_text(encoding="utf-8")

    assert ".innerHTML" not in renderer
    assert ".innerHTML" not in app
    assert '<iframe id="report-preview-frame" class="report-preview-frame" sandbox' in index_html
