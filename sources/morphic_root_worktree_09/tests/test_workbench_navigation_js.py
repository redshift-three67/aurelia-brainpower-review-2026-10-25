from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


def test_fallback_navigation_uses_all_11_static_steps() -> None:
    source = APP_JS.read_text(encoding="utf-8")

    assert "const FALLBACK_STEPS = [" in source
    assert "state.registry ? state.registry.steps.length : FALLBACK_STEPS.length" in source
    assert source.count('id:"') >= 11


def test_arrow_navigation_is_scoped_to_the_workbench_stepper() -> None:
    source = APP_JS.read_text(encoding="utf-8")

    assert 'const stepper = $("#wizard-stepper");' in source
    assert 'stepper.addEventListener("keydown", (e) => {' in source
    assert 'document.addEventListener("keydown", (e) =>' not in source
    assert 'if (e.key === "ArrowRight") {' in source
    assert 'if (e.key === "ArrowLeft") {' in source
    assert source.count("e.preventDefault();") >= 2
