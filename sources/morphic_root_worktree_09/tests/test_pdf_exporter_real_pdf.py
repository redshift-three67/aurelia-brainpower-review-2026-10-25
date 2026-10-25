import subprocess
import sys
from pathlib import Path

from tools import pdf_exporter


ROOT = Path(__file__).resolve().parents[1]


def _hex(color: object) -> str:
    return color.hexval().replace("0x", "#").lower()


def test_pdf_exporter_writes_real_pdf_not_placeholder(tmp_path: Path) -> None:
    html_path = tmp_path / "bericht.html"
    html_path.write_text(
        "<html><body><h1>Deutung - Klaus Mustermann</h1>"
        "<p>Wellbeing Compliance: keine medizinische Diagnose.</p>"
        "<p>Bronchien Resonanzbericht</p></body></html>",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "tools.pdf_exporter", str(html_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )

    pdf_path = html_path.with_suffix(".pdf")
    placeholder_path = html_path.with_suffix(".pdf.txt")

    assert result.returncode == 0, result.stdout + result.stderr
    assert pdf_path.exists()
    assert not placeholder_path.exists()
    data = pdf_path.read_bytes()
    assert data.startswith(b"%PDF-1.4")
    assert b"PDF export placeholder" not in data
    # Real layout renderers (ReportLab or wkhtmltopdf) generate compressed content
    # streams. Verify it is a genuine PDF from one of them, not the raw-text fallback.
    text = data.decode("utf-16-be", errors="ignore").lower()
    assert "reportlab" in text or "wkhtmltopdf" in text
    # The title should appear in PDF metadata
    assert b"bericht" in data.lower() or b"Deutung" in data or b"/Title" in data


def test_pdf_exporter_palette_matches_workbench_report_theme() -> None:
    assert _hex(pdf_exporter._CLR_PRIMARY) == "#263029"
    assert _hex(pdf_exporter._CLR_ACCENT) == "#5f7f68"
    assert _hex(pdf_exporter._CLR_ACCENT_LIGHT) == "#3f7f7a"
    assert _hex(pdf_exporter._CLR_HEADER_BG) == "#f4f1e7"
    assert _hex(pdf_exporter._CLR_SECTION_BG) == "#eef5f2"
    assert _hex(pdf_exporter._CLR_TABLE_HEADER) == "#e6ede4"
