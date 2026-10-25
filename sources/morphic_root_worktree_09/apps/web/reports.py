from __future__ import annotations

import hashlib
import html
import json
import os
import re
import stat
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Sequence

from apps.web.display_scores import normalize_display_payload
from apps.web.report_handles import (
    ReportHandle,
    RootIdentity,
    inspect_report_root,
    open_report_handle,
    validate_relative_components,
)


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
MAX_PREVIEW_BYTES = MAX_PREVIEW_CHARS
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
BLOCKED_HTML_TAGS = {
    "script",
    "style",
    "iframe",
    "object",
    "embed",
    "svg",
    "math",
    "head",
    "title",
}


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


def _catalog_report_id(
    canonical_root: str,
    root_device: int,
    root_inode: int | bytes,
    components: Sequence[str],
) -> str:
    encoded_inode = (
        f"file-id-128:{root_inode.hex()}"
        if isinstance(root_inode, bytes)
        else root_inode
    )
    identity = json.dumps(
        {
            "version": 1,
            "root": [canonical_root, root_device, encoded_inode],
            "components": list(components),
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(identity).hexdigest()


@dataclass(frozen=True)
class _ReportReference:
    root: Path
    root_identity: RootIdentity
    components: tuple[str, ...]
    entry: dict[str, object]


class ReportCatalog:
    def __init__(
        self,
        roots: Sequence[str | Path],
        *,
        cache_ttl_seconds: float = 0.0,
    ) -> None:
        self.roots = [Path(os.path.abspath(os.fspath(root))) for root in roots]
        self.cache_ttl_seconds = max(0.0, float(cache_ttl_seconds))
        self._cache_deadline = 0.0
        self._cache_lock = threading.RLock()
        self._cache_signature: tuple[str, ...] | None = None
        self._cache_entries: list[dict[str, object]] = []
        self._cache_references: dict[str, _ReportReference] = {}

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
        selected_internal = reports if limit is None else reports[:limit]
        selected = [self._public_entry(entry) for entry in selected_internal]
        return {
            "count": len(selected),
            "root_count": len(self.roots),
            "client_count": len({str(entry["client_id"]) for entry in selected}),
            "clients": self._group_entries(selected),
            "reports": selected,
        }

    @staticmethod
    def _public_entry(entry: dict[str, object]) -> dict[str, object]:
        return dict(entry)

    def _reference(self, report_id: str) -> _ReportReference:
        with self._cache_lock:
            now = time.monotonic()
            if self._cache_signature is None or now >= self._cache_deadline:
                self._entries_locked()
                self._cache_deadline = time.monotonic() + self.cache_ttl_seconds
            reference = self._cache_references.get(report_id)
            if reference is None:
                raise KeyError(report_id)
            return reference

    @staticmethod
    def _handle_entry(
        entry: dict[str, object],
        handle: ReportHandle,
    ) -> dict[str, object]:
        current = dict(entry)
        current["size"] = int(handle.stat.st_size)
        current["modified_at"] = datetime.fromtimestamp(
            handle.stat.st_mtime,
            timezone.utc,
        ).isoformat()
        return current

    def open_report(
        self,
        report_id: str,
    ) -> tuple[ReportHandle, dict[str, object]]:
        reference = self._reference(report_id)
        handle = open_report_handle(
            reference.root,
            reference.components,
            expected_root_identity=reference.root_identity,
        )
        try:
            entry = self._handle_entry(reference.entry, handle)
        except BaseException:
            handle.close()
            raise
        return handle, entry

    def validate(self, report_id: str) -> dict[str, object]:
        handle, entry = self.open_report(report_id)
        with handle:
            return entry

    def open_download(
        self,
        report_id: str,
    ) -> tuple[ReportHandle, dict[str, object]]:
        return self.open_report(report_id)

    def preview(self, report_id: str) -> dict[str, object]:
        handle, entry = self.open_report(report_id)
        with handle:
            file_name = str(entry["file_name"])
            suffix = Path(file_name).suffix.lower()
            base = {
                "report_id": report_id,
                "kind": entry["kind"],
                "content_type": PREVIEW_CONTENT_TYPES[suffix],
                "title": file_name,
                "size": entry["size"],
                "modified_at": entry["modified_at"],
                "file_name": file_name,
                "file_url": f"/api/reports/{report_id}/file",
            }
            if suffix == ".pdf":
                return {**base, "mode": "file", "content": None}

            content = handle.read(MAX_PREVIEW_BYTES).decode(
                "utf-8",
                errors="replace",
            )[:MAX_PREVIEW_CHARS]
            if suffix in {".html", ".htm"}:
                return {
                    **base,
                    "mode": "html",
                    "content": self._preview_shell(self._sanitize_html(content)),
                }
            if suffix == ".json":
                content = self._format_json(content)[:MAX_PREVIEW_CHARS]
            return {**base, "mode": "text", "content": content}

    def _entries(self) -> list[dict[str, object]]:
        with self._cache_lock:
            now = time.monotonic()
            if self._cache_signature is not None and now < self._cache_deadline:
                return list(self._cache_entries)
            entries = self._entries_locked()
            self._cache_deadline = time.monotonic() + self.cache_ttl_seconds
            return entries

    def _entries_locked(self) -> list[dict[str, object]]:
        reports: list[dict[str, object]] = []
        references: dict[str, _ReportReference] = {}
        for root in self.roots:
            try:
                root_identity = inspect_report_root(root)
            except OSError:
                continue
            for path in root.rglob("*"):
                try:
                    file_stat = path.lstat()
                    if (
                        not stat.S_ISREG(file_stat.st_mode)
                        or getattr(file_stat, "st_file_attributes", 0) & 0x400
                        or path.suffix.lower() not in REPORT_MEDIA_TYPES
                    ):
                        continue
                    relative = path.relative_to(root)
                    components = validate_relative_components(relative.parts)
                    if self._is_legacy_misplaced_entry(path, root):
                        continue
                    report_id = _catalog_report_id(
                        root_identity.canonical_path,
                        root_identity.device,
                        root_identity.inode,
                        components,
                    )
                    if report_id in references:
                        continue
                    entry = self._entry(path, root, file_stat, report_id)
                    references[report_id] = _ReportReference(
                        root=root,
                        root_identity=root_identity,
                        components=components,
                        entry=entry,
                    )
                    reports.append(entry)
                except (OSError, TypeError, ValueError):
                    continue
        reports.sort(key=lambda entry: str(entry["modified_at"]), reverse=True)
        self._cache_signature = tuple(str(entry["id"]) for entry in reports)
        self._cache_entries = reports
        self._cache_references = references
        return list(reports)

    def _entry(
        self,
        path: Path,
        root: Path,
        file_stat: os.stat_result,
        report_id: str,
    ) -> dict[str, object]:
        suffix = path.suffix.lower()
        relative = path.relative_to(root)
        relative_path = relative.as_posix()
        client_id = self._client_id(relative)
        session_id = self._session_id(relative, path)
        return {
            "id": report_id,
            "label": self._label(path),
            "file_name": path.name,
            "kind": REPORT_KINDS[suffix],
            "media_type": REPORT_MEDIA_TYPES[suffix],
            "size": file_stat.st_size,
            "modified_at": datetime.fromtimestamp(
                file_stat.st_mtime, timezone.utc
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
            '<link rel="stylesheet" href="/static/report-preview.css">'
            "</head><body>"
            f"{content}"
            "</body></html>"
        )
