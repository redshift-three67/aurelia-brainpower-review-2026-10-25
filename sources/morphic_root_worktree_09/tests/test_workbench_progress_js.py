from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"


def test_initial_progress_matches_11_step_workbench_contract() -> None:
    index_html = INDEX_HTML.read_text(encoding="utf-8")
    renderer = RENDER_JS.read_text(encoding="utf-8")

    assert 'id="wizard-progress-label">1 / 11' in index_html
    assert "const total = steps.length || panels.length;" in renderer
    assert "this.updateProgress(index, total);" in renderer
