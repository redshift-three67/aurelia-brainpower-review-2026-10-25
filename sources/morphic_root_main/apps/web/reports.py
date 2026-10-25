from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Sequence

from apps.web.display_scores import normalize_display_payload


REPORT_MEDIA_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".json": "application/json",
    ".txt": "text/plain; charset=utf-8",
    ".pdf": "application/pdf",
}

REPORT_KINDS = {
    ".html": "HTML",
    ".htm": "HTML",
    ".json": "JSON",
    ".txt": "TXT",
    ".pdf": "PDF",
}

PREVIEW_CONTENT_TYPES = {
    ".html": "text/html",
    ".htm": "text/html",
    ".json": "application/json",
    ".txt": "text/plain",
    ".pdf": "application/pdf",
}

SESSION_STAMP_RE = re.compile(r"(?P<stamp>\d{8}_\d{6})")
MAX_PREVIEW_CHARS = 200_000
LEGACY_CLIENT_SUFFIXES = ("_Synergy", "_Remedies", "_Deutung", "_Trends")
# Neue Hierarchie: ReportType / ClientSlug / Session / File
_REPORT_TYPE_ROOTS = frozenset({"Resonanz", "Synergy", "Remedies", "Deutung", "Trends"})
DISPLAY_TOKEN_MAP = {
    "api": "API",
    "html": "HTML",
    "json": "JSON",
    "nls": "NLS",
    "pdf": "PDF",
    "top3": "TOP3",
    "txt": "TXT",
    "ui": "UI",
    "ux": "UX",
}

SAFE_HTML_TAGS = {
    "html",
    "head",
    "body",
    "title",
    "meta",
    "div",
    "span",
    "p",
    "br",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "small",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "pre",
    "code",
    "section",
    "article",
    "header",
    "footer",
    "main",
    "aside",
    "hr",
}
SAFE_HTML_ATTRS = {
    "class",
    "id",
    "colspan",
    "rowspan",
    "scope",
    "lang",
    "charset",
}
BLOCKED_HTML_TAGS = {"script", "style", "iframe", "object", "embed", "svg", "math"}


class _SafeHtmlPreviewParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._blocked_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in BLOCKED_HTML_TAGS:
            self._blocked_depth += 1
            return
        if tag not in SAFE_HTML_TAGS:
            return
        if self._blocked_depth:
            return
        safe_attrs: list[str] = []
        for key, value in attrs:
            key = key.lower()
            if key not in SAFE_HTML_ATTRS:
                continue
            if value is None:
                continue
            safe_attrs.append(f'{key}="{html.escape(value, quote=True)}"')
        attr_text = (" " + " ".join(safe_attrs)) if safe_attrs else ""
        self.parts.append(f"<{tag}{attr_text}>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in BLOCKED_HTML_TAGS and self._blocked_depth:
            self._blocked_depth -= 1
            return
        if self._blocked_depth:
            return
        if tag in SAFE_HTML_TAGS:
            self.parts.append(f"</{tag}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in BLOCKED_HTML_TAGS or tag not in SAFE_HTML_TAGS or self._blocked_depth:
            return
        safe_attrs: list[str] = []
        for key, value in attrs:
            key = key.lower()
            if key not in SAFE_HTML_ATTRS or value is None:
                continue
            safe_attrs.append(f'{key}="{html.escape(value, quote=True)}"')
        attr_text = (" " + " ".join(safe_attrs)) if safe_attrs else ""
        self.parts.append(f"<{tag}{attr_text}/>")

    def handle_data(self, data: str) -> None:
        if self._blocked_depth:
            return
        self.parts.append(html.escape(data))

    def handle_entityref(self, name: str) -> None:
        if self._blocked_depth:
            return
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._blocked_depth:
            return
        self.parts.append(f"&#{name};")

    def output(self) -> str:
        return "".join(self.parts)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _report_id(path: Path) -> str:
    return hashlib.sha256(str(path).casefold().encode("utf-8")).hexdigest()[:20]


class ReportCatalog:
    def __init__(self, roots: Sequence[str | Path]) -> None:
        self.roots = [Path(root).resolve() for root in roots]
        self._cache_signature: (
            tuple[tuple[str, int | None, int, int | None, int, int | None], ...] | None
        ) = None
        self._cache_entries: list[dict[str, object]] = []

    def list(
        self,
        *,
        limit: int | None = None,
        include_all_formats: bool = True,
        client_view: bool | None = None,
    ) -> dict[str, object]:
        if client_view is not None:
            include_all_formats = not client_view

        reports = self._entries()
        if not include_all_formats:
            reports = [entry for entry in reports if str(entry["kind"]) == "HTML"]
        selected = reports if limit is None else reports[:limit]
        return {
            "count": len(selected),
            "root_count": len(self.roots),
            "client_count": len({str(entry["client_id"]) for entry in selected}),
            "clients": self._group_entries(selected),
            "reports": selected,
        }

    def file_path(self, report_id: str) -> tuple[Path, dict[str, object]]:
        path, root = self._find(report_id)
        return path, self._entry(path, root)

    def preview(self, report_id: str) -> dict[str, object]:
        path, root = self._find(report_id)
        entry = self._entry(path, root)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return {
                "report_id": report_id,
                "mode": "file",
                "kind": entry["kind"],
                "content_type": PREVIEW_CONTENT_TYPES[suffix],
                "content": None,
                "file_name": path.name,
                "file_url": f"/api/reports/{report_id}/file",
            }

        if suffix in {".html", ".htm"}:
            return {
                "report_id": report_id,
                "mode": "html",
                "kind": entry["kind"],
                "content_type": PREVIEW_CONTENT_TYPES[suffix],
                "content": self._preview_shell(
                    self._sanitize_html(self._read_text(path))
                ),
                "file_name": path.name,
                "file_url": f"/api/reports/{report_id}/file",
            }

        content = self._read_text(path)
        if suffix == ".json":
            content = self._format_json(content)

        return {
            "report_id": report_id,
            "mode": "text",
            "kind": entry["kind"],
            "content_type": PREVIEW_CONTENT_TYPES[suffix],
            "content": content,
            "file_name": path.name,
            "file_url": f"/api/reports/{report_id}/file",
        }

    def _find(self, report_id: str) -> tuple[Path, Path]:
        for entry in self._entries():
            if str(entry["id"]) != report_id:
                continue
            root = Path(str(entry["_root_path"]))
            path = Path(str(entry["_full_path"]))
            return path, root
        raise KeyError(report_id)

    def _root_signature(
        self, root: Path
    ) -> tuple[str, int | None, int, int | None, int, int | None]:
        if not root.exists():
            return (str(root), None, 0, None, 0, None)
        dir_count = 0
        file_count = 0
        newest_dir_mtime = int(root.stat().st_mtime_ns)
        newest_file_mtime: int | None = None
        for path in root.rglob("*"):
            try:
                stat_mtime = int(path.stat().st_mtime_ns)
            except OSError:
                continue

            if path.is_dir():
                dir_count += 1
                newest_dir_mtime = max(newest_dir_mtime, stat_mtime)
            elif path.is_file():
                file_count += 1
                newest_file_mtime = (
                    stat_mtime
                    if newest_file_mtime is None
                    else max(newest_file_mtime, stat_mtime)
                )

        return (
            str(root),
            newest_dir_mtime,
            dir_count,
            int(root.stat().st_mtime_ns),
            file_count,
            newest_file_mtime,
        )

    def _signature(
        self,
    ) -> tuple[tuple[str, int | None, int, int | None, int, int | None], ...]:
        values: list[tuple[str, int | None, int, int | None, int, int | None]] = []
        for root in self.roots:
            values.append(self._root_signature(root))
        return tuple(values)

    def _entries(self) -> list[dict[str, object]]:
        signature = self._signature()
        if self._cache_signature == signature:
            return list(self._cache_entries)

        reports: list[dict[str, object]] = []
        for root in self.roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in REPORT_MEDIA_TYPES:
                    continue
                try:
                    resolved = path.resolve()
                    if not _is_relative_to(resolved, root):
                        continue
                    if self._is_legacy_misplaced_entry(resolved, root):
                        continue
                    reports.append(self._entry(resolved, root))
                except OSError:
                    continue
        reports.sort(key=lambda entry: str(entry["modified_at"]), reverse=True)
        self._cache_signature = signature
        self._cache_entries = reports
        return list(reports)

    def _entry(self, path: Path, root: Path) -> dict[str, object]:
        stat = path.stat()
        suffix = path.suffix.lower()
        relative = path.relative_to(root)
        relative_path = relative.as_posix()
        client_id = self._client_id(relative)
        session_id = self._session_id(relative, path)
        return {
            "id": _report_id(path),
            "_root_path": str(root),
            "_full_path": str(path),
            "label": self._label(path),
            "file_name": path.name,
            "kind": REPORT_KINDS[suffix],
            "media_type": REPORT_MEDIA_TYPES[suffix],
            "size": stat.st_size,
            "modified_at": datetime.fromtimestamp(
                stat.st_mtime, timezone.utc
            ).isoformat(),
            "root_name": root.name,
            "client_id": client_id,
            "session_id": session_id,
            "relative_path": relative_path,
        }

    def _group_entries(
        self, entries: list[dict[str, object]]
    ) -> list[dict[str, object]]:
        grouped: dict[str, dict[str, Any]] = {}

        for entry in entries:
            client_id = str(entry["client_id"])
            session_id = str(entry["session_id"])
            client = grouped.setdefault(
                client_id,
                {
                    "client_id": client_id,
                    "label": self._client_label(client_id),
                    "latest_modified_at": str(entry["modified_at"]),
                    "sessions": {},
                },
            )
            client["latest_modified_at"] = max(
                str(client["latest_modified_at"]), str(entry["modified_at"])
            )

            sessions_by_id: dict[str, dict[str, Any]] = client["sessions"]
            session = sessions_by_id.setdefault(
                session_id,
                {
                    "session_id": session_id,
                    "label": self._session_label(session_id),
                    "latest_modified_at": str(entry["modified_at"]),
                    "files": [],
                },
            )
            session["latest_modified_at"] = max(
                str(session["latest_modified_at"]), str(entry["modified_at"])
            )
            session["files"].append(entry)

        clients = []
        for client in grouped.values():
            sessions = []
            sessions_by_id = client["sessions"]
            for session in sessions_by_id.values():
                session["files"].sort(
                    key=lambda item: (str(item["modified_at"]), str(item["file_name"])),
                    reverse=True,
                )
                sessions.append(session)
            sessions.sort(
                key=lambda item: str(item["latest_modified_at"]), reverse=True
            )
            clients.append(
                {
                    "client_id": client["client_id"],
                    "label": client["label"],
                    "latest_modified_at": client["latest_modified_at"],
                    "session_count": len(sessions),
                    "file_count": sum(len(session["files"]) for session in sessions),
                    "sessions": sessions,
                }
            )
        clients.sort(key=lambda item: str(item["latest_modified_at"]), reverse=True)
        return clients

    def _client_id(self, relative: Path) -> str:
        parts = relative.parts
        if len(parts) >= 3 and parts[0] in _REPORT_TYPE_ROOTS:
            # Neue Hierarchie: ReportType / ClientSlug / Session / File
            return parts[1]
        if len(parts) >= 2:
            # Alte Hierarchie: ClientSlug / Session / File
            return parts[0]
        return relative.stem

    def _is_legacy_misplaced_entry(self, path: Path, root: Path) -> bool:
        try:
            relative = path.relative_to(root)
        except ValueError:
            return True
        if len(relative.parts) < 2:
            return False
        # Neue Hierarchie: parts[0] ist ReportType (Resonanz/Synergy/...) - nicht "misplaced"
        if relative.parts[0] in _REPORT_TYPE_ROOTS:
            return False
        client_dir = relative.parts[0]
        root_name = root.name
        if root_name == "Benutzer_Archive_Start":
            return client_dir.endswith(("_Synergy", "_Remedies", "_Deutung", "_Trends"))
        if root_name == "Benutzer_Synergy_Start":
            return client_dir.endswith("_Synergy")
        if root_name == "Benutzer_Remedies_Start":
            return client_dir.endswith("_Remedies")
        if root_name == "Benutzer_Deutung_Start":
            return client_dir.endswith("_Deutung")
        if root_name == "Benutzer_Trends_Start":
            return client_dir.endswith("_Trends")
        return False

    def _session_id(self, relative: Path, path: Path) -> str:
        parts = relative.parts
        if len(parts) >= 4 and parts[0] in _REPORT_TYPE_ROOTS:
            # Neue Hierarchie: ReportType / ClientSlug / Session / File
            return parts[2]
        if len(parts) >= 3:
            return parts[1]
        match = SESSION_STAMP_RE.search(path.stem)
        if match:
            return match.group("stamp")
        return path.stem

    def _label(self, path: Path) -> str:
        base_name = path.stem
        leading_match = SESSION_STAMP_RE.match(base_name)
        if leading_match:
            remainder = base_name[leading_match.end() :].lstrip("_-")
            if remainder:
                base_name = remainder

        trailing_match = SESSION_STAMP_RE.search(base_name)
        if trailing_match and trailing_match.end() == len(base_name):
            remainder = base_name[: trailing_match.start()].rstrip("_-")
            if remainder:
                base_name = remainder
        return self._humanize_label(base_name)

    def _client_label(self, client_id: str) -> str:
        return self._humanize_label(client_id)

    def _session_label(self, session_id: str) -> str:
        match = SESSION_STAMP_RE.search(session_id)
        if match:
            stamp = datetime.strptime(match.group("stamp"), "%Y%m%d_%H%M%S")
            return stamp.strftime("%Y-%m-%d %H:%M:%S")
        return self._humanize_label(session_id)

    def _humanize_label(self, value: str) -> str:
        tokens = [token for token in re.split(r"[_\-\s]+", value) if token]
        if not tokens:
            return value

        humanized: list[str] = []
        for token in tokens:
            normalized = DISPLAY_TOKEN_MAP.get(token.casefold())
            if normalized is not None:
                humanized.append(normalized)
            elif token.isupper() or any(char.isdigit() for char in token):
                humanized.append(token.upper())
            else:
                humanized.append(token.capitalize())
        return " ".join(humanized)

    def _read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")[:MAX_PREVIEW_CHARS]

    def _format_json(self, content: str) -> str:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return content
        return json.dumps(
            normalize_display_payload(payload),
            indent=2,
            ensure_ascii=False,
        )

    def _sanitize_html(self, content: str) -> str:
        parser = _SafeHtmlPreviewParser()
        parser.feed(content)
        parser.close()
        return parser.output()

    def _preview_shell(self, content: str) -> str:
        return (
            "<!DOCTYPE html><html lang='de'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            "<style>body{font-family:Inter,Segoe UI,Arial,sans-serif;background:#f7f4ef;color:#23323a;padding:24px;line-height:1.65;}"
            "h1,h2,h3,h4{line-height:1.25;margin:1.2rem 0 .75rem;color:#1d2d35;}"
            "p,li{margin:.55rem 0;}"
            "table{width:100%;border-collapse:collapse;margin:1rem 0 1.25rem;background:#fff;}"
            "th,td{padding:.7rem .85rem;border:1px solid #d9e0e4;vertical-align:top;text-align:left;}"
            "th{background:#e8eef2;font-weight:600;}"
            "section,article,div{max-width:100%;}"
            ".scroll-section{max-height:28rem;overflow:auto;border:1px solid #d9e0e4;border-radius:10px;background:#fff;}"
            ".visible-limit-note{font-size:.95rem;color:#4b5d68;margin:.5rem 0;}"
            "pre,code{font-family:Consolas,Monaco,monospace;}"
            "pre{white-space:pre-wrap;word-break:break-word;background:#fff;padding:12px;border:1px solid #d9e0e4;border-radius:10px;}"
            "</style></head><body>"
            f"{content}"
            "</body></html>"
        )
