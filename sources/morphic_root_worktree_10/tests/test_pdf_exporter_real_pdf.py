import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
    # ReportLab generates real PDFs with compressed content streams.
    # Verify it's a genuine ReportLab PDF (not a placeholder) and has proper metadata.
    assert b"ReportLab" in data
    # The title should appear in PDF metadata
    assert b"bericht" in data.lower() or b"Deutung" in data or b"/Title" in data
