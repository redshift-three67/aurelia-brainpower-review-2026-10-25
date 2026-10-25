# V1 Wellbeing Report Compliance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a canonical Wellbeing/Non-Medical safety block to Morphic V1 reports and replace the PDF placeholder with a real dependency-free PDF writer.

**Architecture:** Keep core scan engines unchanged. Add a tiny compliance module that report renderers can call, inject the disclaimer into shared HTML/TXT renderers, and make `tools.pdf_exporter` produce valid PDF files from HTML text using only the Python standard library.

**Tech Stack:** Python 3.10+, Typer/CLI subprocess tests, pytest, stdlib `html.parser`, stdlib file I/O.

---

## File Structure

| File | Responsibility |
|---|---|
| `core/compliance/__init__.py` | Export the canonical safety helpers. |
| `core/compliance/safety.py` | Single source for Wellbeing/Non-Medical disclaimer and HTML/TXT blocks. |
| `tools/reporting_common.py` | Inject the safety block into Deutung/Synergy/Remedy/Trend HTML reports. |
| `apps/cli/commands/helpers/harmonization_helpers.py` | Inject the safety block into Multiplex HTML/TXT reports. |
| `tools/simple_pdf.py` | Minimal valid PDF writer for text pages, dependency-free. |
| `tools/pdf_exporter.py` | Convert HTML inputs to real `.pdf` files; no `.pdf.txt` placeholder. |
| `tests/test_wellbeing_compliance_reports.py` | Regression tests for disclaimer placement in report renderers. |
| `tests/test_pdf_exporter_real_pdf.py` | Regression tests for real PDF generation. |

---

### Task 1: Failing Tests For Report Safety Blocks

**Files:**
- Create: `tests/test_wellbeing_compliance_reports.py`
- Modify later: `core/compliance/safety.py`
- Modify later: `tools/reporting_common.py`
- Modify later: `apps/cli/commands/helpers/harmonization_helpers.py`

- [ ] **Step 1: Write the failing test**

```python
from apps.cli.commands.helpers import _render_basic_html, _render_multiplex_txt
from tools.reporting_common import render_legacy_html


def test_shared_legacy_html_contains_wellbeing_disclaimer() -> None:
    html = render_legacy_html(
        title="Deutung - Klaus Mustermann",
        subtitle="Morphic Engine Deutungsbericht",
        body_html='<div class="section"><h2>Zusammenfassung</h2><p>Test</p></div>',
        focus="Bronchien",
    )

    assert "Wellbeing Compliance" in html
    assert "keine medizinische Diagnose" in html
    assert "keine Behandlung oder Heilung" in html


def test_multiplex_html_contains_wellbeing_disclaimer() -> None:
    html = _render_basic_html(
        {
            "command": "multiplex_scan",
            "focus": "Bronchien",
            "client": {
                "first_name": "Klaus",
                "name": "Mustermann",
                "birth_date": "09041966",
                "birth_place": "Augsburg",
            },
            "analysis": {"rates": [1, 2, 3], "morphic_field": 0.5},
            "sub_results": {"top": [{"label": "Bronchien", "score": 8.0, "group": "Atmung"}]},
        }
    )

    assert "Wellbeing Compliance" in html
    assert "keine medizinische Diagnose" in html
    assert "keine Behandlung oder Heilung" in html


def test_multiplex_txt_contains_wellbeing_disclaimer() -> None:
    text = _render_multiplex_txt(
        {
            "profile": "atmung_lunge_detailliert",
            "focus": "Bronchien",
            "client": {"first_name": "Klaus", "name": "Mustermann"},
            "sub_results": {"top": [{"label": "Bronchien", "score": 8.0, "group": "Atmung"}]},
        }
    )

    assert "Wellbeing Compliance" in text
    assert "keine medizinische Diagnose" in text
    assert "keine Behandlung oder Heilung" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_wellbeing_compliance_reports.py -q
```

Expected: FAIL because report renderers do not yet include `Wellbeing Compliance`.

---

### Task 2: Implement Canonical Safety Block

**Files:**
- Create: `core/compliance/__init__.py`
- Create: `core/compliance/safety.py`
- Modify: `tools/reporting_common.py`
- Modify: `apps/cli/commands/helpers/harmonization_helpers.py`

- [ ] **Step 1: Add `core/compliance/safety.py`**

```python
from __future__ import annotations

import html


WELLBEING_DISCLAIMER_DE = (
    "Wellbeing Compliance: Diese Auswertung ist eine energetische Resonanz- "
    "und Wellbeing-Analyse. Sie ersetzt keine medizinische Diagnose, keine "
    "Behandlung oder Heilung und kein therapeutisches Fachurteil. Bei Krankheit, "
    "akuten Beschwerden oder Therapiebedarf bitte Arzt, Heilpraktiker oder eine "
    "andere geeignete Fachperson aufsuchen."
)


def safety_marker() -> dict[str, object]:
    return {
        "medical_claims": 0,
        "inference_only": True,
        "non_medical": True,
        "disclaimer": WELLBEING_DISCLAIMER_DE,
    }


def wellbeing_html_block() -> str:
    text = html.escape(WELLBEING_DISCLAIMER_DE)
    return (
        '<div class="section safety-notice">'
        "<h2>Wellbeing Compliance</h2>"
        f'<div class="summary">{text}</div>'
        "</div>"
    )


def wellbeing_txt_block() -> str:
    return "\nWellbeing Compliance\n" + WELLBEING_DISCLAIMER_DE + "\n"
```

- [ ] **Step 2: Add `core/compliance/__init__.py`**

```python
from .safety import (
    WELLBEING_DISCLAIMER_DE,
    safety_marker,
    wellbeing_html_block,
    wellbeing_txt_block,
)

__all__ = [
    "WELLBEING_DISCLAIMER_DE",
    "safety_marker",
    "wellbeing_html_block",
    "wellbeing_txt_block",
]
```

- [ ] **Step 3: Inject safety block in `tools/reporting_common.py`**

Add the import near the existing imports:

```python
from core.compliance.safety import wellbeing_html_block
```

Then insert the block inside `render_legacy_html()` immediately after the header block and before `{body_html}`:

```python
        {wellbeing_html_block()}
        {body_html}
```

- [ ] **Step 4: Inject safety block in `apps/cli/commands/helpers/harmonization_helpers.py`**

Add the import near the existing imports:

```python
from core.compliance.safety import wellbeing_html_block, wellbeing_txt_block
```

Inside `_render_basic_html()`, append the HTML block after the header-info block:

```python
    parts.append(wellbeing_html_block())
```

Inside `_render_multiplex_txt()`, add the text block after the initial blank line:

```python
        wellbeing_txt_block().strip(),
        "",
```

- [ ] **Step 5: Run test to verify it passes**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_wellbeing_compliance_reports.py -q
```

Expected: `3 passed`.

---

### Task 3: Failing Test For Real PDF Export

**Files:**
- Create: `tests/test_pdf_exporter_real_pdf.py`
- Modify later: `tools/simple_pdf.py`
- Modify later: `tools/pdf_exporter.py`

- [ ] **Step 1: Write the failing test**

```python
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
    assert b"Deutung - Klaus Mustermann" in data
    assert b"keine medizinische Diagnose" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_pdf_exporter_real_pdf.py -q
```

Expected: FAIL because the current exporter writes `.pdf.txt`, not `.pdf`.

---

### Task 4: Implement Dependency-Free PDF Writer

**Files:**
- Create: `tools/simple_pdf.py`
- Modify: `tools/pdf_exporter.py`

- [ ] **Step 1: Add `tools/simple_pdf.py`**

```python
from __future__ import annotations

from pathlib import Path


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_lines(text: str, width: int = 92) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines() or [""]:
        words = raw.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            if len(current) + 1 + len(word) > width:
                lines.append(current)
                current = word
            else:
                current += " " + word
        lines.append(current)
    return lines


def write_text_pdf(path: str | Path, title: str, text: str) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = _wrap_lines(title + "\n\n" + text)
    content_parts = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
    first = True
    for line in lines:
        if not first:
            content_parts.append("T*")
        content_parts.append(f"({_escape_pdf_text(line)}) Tj")
        first = False
    content_parts.append("ET")
    stream = "\n".join(content_parts).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    destination.write_bytes(bytes(output))
    return destination
```

- [ ] **Step 2: Replace `tools/pdf_exporter.py`**

```python
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path

from tools.simple_pdf import write_text_pdf


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"p", "div", "h1", "h2", "h3", "tr", "li", "br"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if text:
            self.parts.append(text)

    def text(self) -> str:
        return "\n".join(part.strip() for part in self.parts if part.strip())


def html_to_text(path: Path) -> str:
    parser = _TextExtractor()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return parser.text()


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Morphic HTML reports as simple PDF files.")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--latest", action="store_true")
    args = parser.parse_args()

    written = 0
    for raw in args.paths:
        path = Path(raw)
        if path.suffix.lower() in {".html", ".htm"} and path.exists():
            text = html_to_text(path)
            title = path.stem
            target = path.with_suffix(".pdf")
            write_text_pdf(target, title, text)
            old_placeholder = path.with_suffix(".pdf.txt")
            if old_placeholder.exists():
                old_placeholder.unlink()
            print(f"PDF written: {target}")
            written += 1
    if written == 0:
        print("PDF export skipped: no existing HTML path supplied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run PDF test to verify it passes**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_pdf_exporter_real_pdf.py -q
```

Expected: `1 passed`.

---

### Task 5: Regression Verification

**Files:**
- Existing tests only.

- [ ] **Step 1: Run focused report tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_wellbeing_compliance_reports.py tests\test_pdf_exporter_real_pdf.py tests\test_report_tool_archives.py tests\test_report_renderer_legacy_layout.py -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run full suite**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Expected: full suite passes.

- [ ] **Step 3: Update status docs if needed**

If tests pass and implementation is complete, add a short note to `docs/RADI144_UIUX_DSGVO_REFERENZANALYSE_20260628.md` under the report status section:

```markdown
Nachtrag: Der P0-Schnitt "Wellbeing-Hinweis in Reports + echter einfacher PDF-Export" wurde umgesetzt und ist durch `tests/test_wellbeing_compliance_reports.py` sowie `tests/test_pdf_exporter_real_pdf.py` abgedeckt.
```

---

## Self-Review

| Check | Ergebnis |
|---|---|
| Spec coverage | Deckt den ersten P0-Schnitt aus der Radi144/DSGVO-Analyse ab: Safety-Hinweis und PDF-Platzhalter entfernen. |
| Placeholder scan | Keine `TBD`-/`TODO`-Marker im Plan. |
| Type consistency | Alle geplanten Funktionen sind eindeutig benannt und werden in Tests/Implementierung konsistent verwendet. |
| Scope | Manifest, Audit und Loeschkaskade sind bewusst nicht in diesem Schnitt enthalten und bleiben der naechste P0-Block. |
