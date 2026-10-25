from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"


def test_choice_cards_and_results_render_dynamic_values_as_text_nodes() -> None:
    source = RENDER_JS.read_text(encoding="utf-8")
    choice_cards = source.split("renderChoiceCards(containerId", 1)[1].split(
        "/* ── 12-Substep-Timeline", 1
    )[0]
    results = source.split("renderResults(resultPayload)", 1)[1].split(
        "/* ── Run Trace", 1
    )[0]

    assert ".innerHTML" not in choice_cards
    assert ".innerHTML" not in results
    assert "textContent" in choice_cards
    assert "textContent" in results
