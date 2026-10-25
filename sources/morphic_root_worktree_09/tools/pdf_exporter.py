from __future__ import annotations

import argparse
import logging
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

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


# ===== ReportLab-based layout PDF =====

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER

    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False


# Color palette matching the Workbench HTML report theme.
_CLR_PRIMARY = colors.HexColor("#263029")
_CLR_ACCENT = colors.HexColor("#5F7F68")
_CLR_ACCENT_LIGHT = colors.HexColor("#3F7F7A")
_CLR_HEADER_BG = colors.HexColor("#F4F1E7")
_CLR_HEADER_TEXT = colors.HexColor("#345C41")
_CLR_SECTION_BG = colors.HexColor("#EEF5F2")
_CLR_TABLE_HEADER = colors.HexColor("#E6EDE4")
_CLR_TABLE_ALT = colors.HexColor("#FAF7EF")
_CLR_TEXT = colors.HexColor("#263029")
_CLR_MUTED = colors.HexColor("#687168")
_CLR_HIGH = colors.HexColor("#A33D35")
_CLR_MID = colors.HexColor("#9B6B23")
_CLR_LOW = colors.HexColor("#2F7B57")
_CLR_GREEN = colors.HexColor("#2F7B57")
_CLR_FOOTER = colors.HexColor("#687168")

_BADGE_MAP = {
    "prio-high": _CLR_HIGH,
    "badge-high": _CLR_HIGH,
    "prio-mid": _CLR_MID,
    "badge-mid": _CLR_MID,
    "prio-low": _CLR_LOW,
    "badge-low": _CLR_LOW,
    "badge-success": _CLR_GREEN,
    "badge-info": _CLR_ACCENT,
}

_HANDLED_DIV_CLASSES = frozenset(
    ["metric", "focus", "summary", "note", "recommendation", "llm-section", "subtitle"]
)


class _StructuredExtractor(HTMLParser):
    """Extract structured content from HTML for reportlab rendering."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[dict[str, Any]] = []
        self._current: dict[str, Any] | None = None
        self._tag_stack: list[str] = []
        self._in_table = False
        self._table_rows: list[list[str]] = []
        self._current_row: list[str] = []
        self._current_cell: str = ""
        self._in_th = False
        self._in_badge = False
        self._badge_class = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self._tag_stack.append(tag)
        attrs_dict = dict(attrs)

        if tag in ("h1", "h2", "h3"):
            self._current = {"type": tag, "text": "", "class": attrs_dict.get("class", "")}
        elif tag == "p":
            cls = attrs_dict.get("class", "")
            self._current = {"type": "p", "text": "", "class": cls}
        elif tag == "pre":
            self._current = {"type": "pre", "text": ""}
        elif tag == "table":
            self._in_table = True
            self._table_rows = []
        elif tag == "tr":
            self._current_row = []
        elif tag in ("td", "th"):
            self._in_th = tag == "th"
            self._current_cell = ""
            self._badge_class = ""
        elif tag == "span":
            cls = attrs_dict.get("class", "")
            if any(b in cls for b in _BADGE_MAP):
                self._in_badge = True
                self._badge_class = cls
        elif tag == "br":
            if self._current:
                self._current["text"] += "\n"
            if self._in_table:
                self._current_cell += "\n"
        elif tag == "li":
            self._current = {"type": "li", "text": ""}
        elif tag == "div":
            cls = attrs_dict.get("class", "")
            div_classes = set(cls.split()) & _HANDLED_DIV_CLASSES
            if div_classes:
                # Store the original classes so the render loop can map them via substring checks.
                self._current = {"type": "p", "text": "", "class": cls}

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if tag in ("h1", "h2", "h3", "p", "pre", "li", "div") and self._current:
            self.elements.append(self._current)
            self._current = None
        elif tag == "table":
            self._in_table = False
            if self._table_rows:
                self.elements.append({"type": "table", "rows": self._table_rows})
            self._table_rows = []
        elif tag == "tr":
            if self._current_row:
                self._table_rows.append(self._current_row)
            self._current_row = []
        elif tag in ("td", "th"):
            if self._in_th:
                self._current_row.insert(0, "")  # placeholder; we'll detect headers by position
            self._current_row.append(self._current_cell.strip())
            self._in_th = False
        elif tag == "span":
            self._in_badge = False
            self._badge_class = ""

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        if self._in_badge:
            # Render badge text inline
            if self._in_table:
                self._current_cell += text
            elif self._current:
                self._current["text"] += text
        elif self._in_table and (self._in_th or self._current_cell is not None):
            self._current_cell += " " + text if self._current_cell else text
        elif self._current:
            self._current["text"] += " " + text if self._current["text"] else text

    @property
    def in_table(self) -> bool:
        return self._in_table


def _strip_tags(text: str) -> str:
    """Remove HTML tags and decode entities."""
    return re.sub(r"<[^>]+>", "", text).strip()


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()["Normal"]
    return {
        "title": ParagraphStyle(
            "CustomTitle", parent=base, fontSize=20, textColor=_CLR_PRIMARY,
            spaceAfter=6, alignment=TA_LEFT, fontName="Times-Bold",
        ),
        "h2": ParagraphStyle(
            "CustomH2", parent=base, fontSize=14, textColor=_CLR_HEADER_TEXT,
            spaceBefore=16, spaceAfter=8, fontName="Times-Bold",
            leftIndent=8, borderColor=_CLR_ACCENT, borderWidth=0,
        ),
        "h3": ParagraphStyle(
            "CustomH3", parent=base, fontSize=12, textColor=_CLR_ACCENT_LIGHT,
            spaceBefore=12, spaceAfter=6, fontName="Times-Bold",
        ),
        "body": ParagraphStyle(
            "CustomBody", parent=base, fontSize=10, textColor=_CLR_TEXT,
            leading=14, spaceAfter=8, alignment=TA_LEFT,
        ),
        "summary": ParagraphStyle(
            "CustomSummary", parent=base, fontSize=10.5, textColor=_CLR_TEXT,
            leading=15, spaceAfter=8, leftIndent=10, backColor=_CLR_SECTION_BG,
            borderPadding=8, borderColor=_CLR_ACCENT, borderWidth=0,
        ),
        "subtitle": ParagraphStyle(
            "CustomSubtitle", parent=base, fontSize=11, textColor=_CLR_MUTED,
            leading=15, spaceAfter=12,
        ),
        "metric": ParagraphStyle(
            "CustomMetric", parent=base, fontSize=10.5, textColor=_CLR_TEXT,
            leading=14, spaceAfter=8, backColor=_CLR_TABLE_HEADER,
            borderPadding=8, borderColor=_CLR_ACCENT, borderWidth=1,
            fontName="Helvetica-Bold",
        ),
        "pre": ParagraphStyle(
            "CustomPre", parent=base, fontSize=8.5, textColor=_CLR_TEXT,
            leading=12, fontName="Courier", spaceAfter=8,
            backColor=colors.HexColor("#F8F9FA"), borderPadding=8,
        ),
        "footer": ParagraphStyle(
            "CustomFooter", parent=base, fontSize=8, textColor=_CLR_FOOTER,
            alignment=TA_CENTER, spaceBefore=20,
        ),
        "table_header": ParagraphStyle(
            "TableHeader", parent=base, fontSize=8.5, textColor=_CLR_HEADER_TEXT,
            fontName="Helvetica-Bold",
        ),
        "table_cell": ParagraphStyle(
            "TableCell", parent=base, fontSize=8.5, textColor=_CLR_TEXT,
            leading=11,
        ),
    }


def _render_table(rows: list[list[str]], styles: dict[str, ParagraphStyle]) -> Table:
    """Render a table with styled headers and alternating rows."""
    if not rows:
        return Spacer(1, 1 * mm)

    # First row is header (from <th> or first <tr>)
    header = rows[0]
    data_rows = rows[1:] if len(rows) > 1 else []

    # Wrap cells in Paragraphs
    header_cells = [
        Paragraph(_strip_tags(str(cell)), styles["table_header"]) for cell in header
    ]
    body_cells = []
    for row in data_rows:
        body_cells.append([
            Paragraph(_strip_tags(str(cell)), styles["table_cell"]) for cell in row
        ])

    col_count = len(header)
    available_width = A4[0] - 40 * mm
    col_width = available_width / col_count if col_count > 0 else available_width

    table_data = [header_cells] + body_cells
    col_widths = [col_width] * col_count

    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), _CLR_TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), _CLR_HEADER_TEXT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9D6CA")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _CLR_TABLE_ALT]),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]
    tbl.setStyle(TableStyle(style_cmds))
    return tbl


def _header_footer(canvas, doc):
    """Draw header bar and footer on each page."""
    canvas.saveState()
    width, height = A4
    # Header bar
    canvas.setFillColor(_CLR_HEADER_BG)
    canvas.rect(0, height - 15 * mm, width, 15 * mm, fill=1, stroke=0)
    canvas.setFillColor(_CLR_PRIMARY)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(20 * mm, height - 10 * mm, "Morphic Engine V1")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 20 * mm, height - 10 * mm, "Resonanzanalyse")
    # Footer
    canvas.setFillColor(_CLR_FOOTER)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(width / 2, 10 * mm, f"Seite {doc.page}")
    canvas.restoreState()


def write_layout_pdf(path: Path, title: str, html_content: str) -> Path:
    """Write a layout-rich PDF using reportlab.

    Falls back to simple text PDF if reportlab is not available.
    """
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if not _REPORTLAB_AVAILABLE:
        # Fallback to simple text PDF
        return write_text_pdf(destination, title, html_content)

    # Parse HTML
    extractor = _StructuredExtractor()
    extractor.feed(html_content)

    styles = _build_styles()
    story: list[Any] = []

    # The report HTML already provides an <h1> via render_report_header, so we
    # render the extracted elements directly without an extra title paragraph.
    for elem in extractor.elements:
        etype = elem.get("type", "")
        text = elem.get("text", "").strip()

        if etype == "h1":
            story.append(Paragraph(text, styles["title"]))
            story.append(Spacer(1, 4 * mm))
        elif etype == "h2":
            clean = _strip_tags(text)
            if clean:
                story.append(Paragraph(clean, styles["h2"]))
        elif etype == "h3":
            clean = _strip_tags(text)
            if clean:
                story.append(Paragraph(clean, styles["h3"]))
        elif etype == "p":
            cls = elem.get("class", "")
            clean = _strip_tags(text)
            if not clean:
                continue
            if "metric" in cls:
                story.append(Paragraph(clean, styles["metric"]))
            elif "summary" in cls or "focus" in cls:
                story.append(Paragraph(clean, styles["summary"]))
            elif "note" in cls:
                story.append(Paragraph(f"<i>{clean}</i>", styles["body"]))
            elif "recommendation" in cls:
                story.append(Paragraph(clean, styles["summary"]))
            elif "subtitle" in cls:
                story.append(Paragraph(clean, styles["subtitle"]))
            else:
                story.append(Paragraph(clean, styles["body"]))
        elif etype == "pre":
            clean = text.strip()
            if clean:
                # Escape for reportlab
                clean = clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(clean, styles["pre"]))
        elif etype == "li":
            clean = _strip_tags(text)
            if clean:
                story.append(Paragraph(f"• {clean}", styles["body"]))
        elif etype == "table":
            rows = elem.get("rows", [])
            if rows:
                story.append(Spacer(1, 4 * mm))
                story.append(_render_table(rows, styles))
                story.append(Spacer(1, 4 * mm))

    # Footer
    from datetime import datetime
    story.append(Spacer(1, 15 * mm))
    story.append(Paragraph(
        f"Generiert am {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | Morphic Engine V1",
        styles["footer"],
    ))

    doc = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="Morphic Engine V1",
    )
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return destination


def _wkhtmltopdf_path() -> str | None:
    binary = shutil.which("wkhtmltopdf")
    if binary:
        return binary
    candidates = [
        Path(r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"),
        Path(r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe"),
        Path("/usr/local/bin/wkhtmltopdf"),
        Path("/usr/bin/wkhtmltopdf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def _try_wkhtmltopdf(html_path: Path, pdf_path: Path) -> bool:
    """Render HTML to PDF with wkhtmltopdf if available."""
    binary = _wkhtmltopdf_path()
    if not binary:
        return False
    try:
        cmd = [
            binary,
            "--page-size",
            "A4",
            "--encoding",
            "utf-8",
            "--enable-local-file-access",
            "--margin-top",
            "15mm",
            "--margin-bottom",
            "15mm",
            "--margin-left",
            "15mm",
            "--margin-right",
            "15mm",
            str(html_path),
            str(pdf_path),
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        if result.returncode == 0 and pdf_path.exists() and pdf_path.stat().st_size > 0:
            return True
        logger.warning("wkhtmltopdf failed: %s", result.stderr[:500])
        return False
    except Exception as exc:
        logger.warning("wkhtmltopdf error: %s", exc)
        return False


def html_to_pdf(path: Path, title: str = "") -> Path:
    """Convert an HTML file to a layout-rich PDF.

    Prefer wkhtmltopdf if installed (matches legacy reference layout);
    fall back to the ReportLab renderer otherwise.
    """
    target = Path(path)
    pdf_path = target.with_suffix(".pdf")
    if _try_wkhtmltopdf(target, pdf_path):
        return pdf_path
    html_content = target.read_text(encoding="utf-8", errors="replace")
    return write_layout_pdf(pdf_path, title or target.stem, html_content)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Morphic HTML reports as PDF files.")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--latest", action="store_true")
    args = parser.parse_args()

    written = 0
    for raw in args.paths:
        path = Path(raw)
        if path.suffix.lower() in {".html", ".htm"} and path.exists():
            html_to_pdf(path, path.stem)
            print(f"PDF written: {path.with_suffix('.pdf')}")
            written += 1
    if written == 0:
        print("PDF export skipped: no existing HTML path supplied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
