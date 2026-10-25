from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML = (PROJECT_ROOT / "user_workflow.html").read_text(encoding="utf-8")
JS = (PROJECT_ROOT / "user_workflow.js").read_text(encoding="utf-8")
CSS = (PROJECT_ROOT / "user_workflow.css").read_text(encoding="utf-8")


def test_harmonizer_offers_three_pause_image_layers():
    assert 'id="pauseImageLayer1"' in HTML
    assert 'id="pauseImageLayer2"' in HTML
    assert 'id="pauseImageLayer3"' in HTML
    assert 'accept="image/*"' in HTML
    assert "collectPauseImageLayers" in JS
    assert "pauseImageLayers.slice(0, 3)" in JS
    assert "renderPauseLayerStack" in JS
    assert "harm-pause-layer-stack" in CSS


def test_pause_phase_renders_defined_layer_stack_instead_of_only_blank_text():
    assert "harmPauseImageLayers = collectPauseImageLayers()" in JS
    assert "renderPauseLayerStack(harmPauseImageLayers" in JS
    assert "PAUSE — Stille & Integration" in JS
    assert "harm-pause-layer" in CSS


def test_solfeggio_basis_modulation_includes_optional_498_9_hz_kammerton_h():
    assert 'name="harmSolf" value="498.9"' in HTML
    assert "498.90 Hz" in HTML
    assert "Kammerton H" in HTML
    assert "498.9" in JS
