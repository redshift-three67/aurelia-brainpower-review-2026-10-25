from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"


def test_hardware_truth_renders_external_payload_as_text_nodes() -> None:
    source = RENDER_JS.read_text(encoding="utf-8")
    hardware_truth = source.split("renderHardwareTruth(payload)", 1)[1].split(
        "/* ── Review Cards", 1
    )[0]

    assert ".innerHTML" not in hardware_truth
    assert "textContent" in hardware_truth
    assert "replaceChildren()" in hardware_truth
