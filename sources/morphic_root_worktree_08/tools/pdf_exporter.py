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
            target = path.with_suffix(".pdf")
            write_text_pdf(target, path.stem, text)
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
