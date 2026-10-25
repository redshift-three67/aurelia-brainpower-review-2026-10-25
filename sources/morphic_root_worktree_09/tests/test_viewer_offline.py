from __future__ import annotations

from pathlib import Path

from core.viewer_3d import generate_html_viewer


ROOT = Path(__file__).resolve().parents[1]


def test_static_3d_viewer_has_no_external_script_dependencies() -> None:
    viewer = (ROOT / "apps" / "viewer" / "index.html").read_text(encoding="utf-8").lower()

    assert "https://" not in viewer
    assert "unpkg.com" not in viewer
    assert "cdn.jsdelivr.net" not in viewer
    assert "cdnjs.cloudflare.com" not in viewer
    assert "offline-viewer" in viewer


def test_generated_3d_viewer_is_self_contained(tmp_path: Path) -> None:
    output = tmp_path / "viewer.html"

    generate_html_viewer(
        [{"label": "Bronchien", "group": "atmung_lunge_detailliert", "score": 0.8}],
        str(output),
    )

    html = output.read_text(encoding="utf-8").lower()
    assert "https://" not in html
    assert "three" not in html
    assert "<canvas" in html
    assert "bronchien" in html
