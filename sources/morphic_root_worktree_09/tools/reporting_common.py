from __future__ import annotations

import html
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping

from core.compliance.safety import wellbeing_html_block
from core.compliance.runtime_manifest import RuntimeManifestService


def round_scores_for_export(value, key=""):
    """Rekursiv Werte fuer Report-Exporte auf max. 3 Nachkommastellen runden,
    wenn der Schluessel 'score' (case-insensitiv) enthaelt. Alle anderen Werte
    werden unveraendert zurueckgegeben.
    """
    if isinstance(value, list):
        return [round_scores_for_export(item, key) for item in value]
    if isinstance(value, dict):
        return {
            k: round_scores_for_export(v, k)
            for k, v in value.items()
        }
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if isinstance(key, str) and re.search(r"score", key, re.IGNORECASE):
            return round((value + 1e-12) * 1000) / 1000
        return value
    return value


def report_json_dumps(data, **kwargs):
    """json.dumps-Wrapper, der vor dem Serialisieren Score-Werte rundet."""
    return json.dumps(round_scores_for_export(data), **kwargs)


_MOJIBAKE_MARKERS = ("Ã", "Â", "â", "ð", "\ufffd")
_MOJIBAKE_FALLBACKS = {
    "\ufffd": "",
    "â€“": "–",
    "â€”": "—",
    "â€ž": "„",
    "â€œ": "“",
    "â€": "”",
    "â€¢": "•",
    "â†’": "→",
}
REPORT_THEME_ID = "morphic-workbench-report-v1"
_REPORT_THEME_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
    color-scheme: light;
    --report-paper: #f6f3ea;
    --report-surface: #fffdf7;
    --report-surface-muted: #eef2ea;
    --report-surface-strong: #e6ede4;
    --report-ink: #263029;
    --report-muted: #687168;
    --report-sage: #5f7f68;
    --report-sage-dark: #345c41;
    --report-teal: #3f7f7a;
    --report-terracotta: #b5654b;
    --report-line: #d9d6ca;
    --report-ok: #2f7b57;
    --report-warn: #9b6b23;
    --report-bad: #a33d35;
    --report-indigo: #536b92;

    /* Workbench design tokens */
    --rq-font-display: "Fraunces", ui-serif, Georgia, serif;
    --rq-font-sans: "Inter", "Source Sans 3", ui-sans-serif, system-ui, sans-serif;
    --rq-radius: 1rem;
    --rq-radius-sm: calc(var(--rq-radius) - 4px);
    --rq-radius-md: calc(var(--rq-radius) - 2px);
    --rq-shadow-soft: 0 4px 20px rgba(38, 48, 41, 0.08), 0 1px 4px rgba(38, 48, 41, 0.04);
}
html { scroll-behavior: smooth; }
body {
    min-width: 320px;
    min-height: 100vh;
    padding: 30px 20px;
    background:
        linear-gradient(135deg, rgba(95, 127, 104, 0.10), transparent 34%),
        linear-gradient(315deg, rgba(181, 101, 75, 0.08), transparent 38%),
        var(--report-paper);
    color: var(--report-ink);
    font-family: var(--rq-font-sans);
    font-size: 11pt;
    line-height: 1.6;
}
.container {
    width: min(1100px, 100%);
    margin: 0 auto;
}
.report-shell {
    display: grid;
    gap: 18px;
}
.header,
.section,
.report-block,
.card,
.finding,
.pattern,
.recommendation {
    background: var(--report-surface);
    border: 1px solid var(--report-line);
    border-radius: var(--rq-radius-sm);
    box-shadow: var(--rq-shadow-soft);
}
.header,
.report-block {
    padding: 24px;
}
.header {
    text-align: left;
    border-left: 4px solid var(--report-sage);
}
.report-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}
.eyebrow {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 6px;
    background: var(--report-surface-muted);
    color: var(--report-sage-dark);
    font-size: 9pt;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-top: 18px;
}
.metric {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 12px;
    border: 1px solid var(--report-line);
    border-radius: var(--rq-radius-sm);
    background: var(--report-surface-muted);
}
.metric span {
    color: var(--report-muted);
    font-size: 9pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.metric strong {
    color: var(--report-ink);
    font-size: 11pt;
    font-weight: 700;
}
.section {
    padding: 24px;
}
.report-shell h1,
.report-shell h2,
.report-shell h3,
.report-shell p,
.report-shell ul,
.report-shell ol,
.report-shell pre,
.report-shell table {
    margin-top: 0;
    margin-bottom: 18px;
}
.report-shell ul,
.report-shell ol {
    padding-left: 22px;
}
.header h1,
.report-shell h1 {
    color: var(--report-ink);
    font-family: var(--rq-font-display);
    font-size: 24pt;
    font-weight: 700;
    line-height: 1.12;
    letter-spacing: 0;
}
.subtitle {
    max-width: 760px;
    color: var(--report-muted);
    font-size: 11pt;
}
.meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 15px;
}
.meta span,
.profile-tag,
.badge {
    display: inline-flex;
    align-items: center;
    min-height: 30px;
    border-radius: var(--rq-radius-sm);
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 0;
}
.meta span,
.profile-tag {
    padding: 5px 10px;
    border: 1px solid var(--report-line);
    background: var(--report-surface-muted);
    color: var(--report-sage-dark);
}
.focus,
.header-info,
.summary,
.note,
.llm-section {
    border-radius: var(--rq-radius-sm);
}
.focus {
    display: inline-block;
    margin-top: 15px;
    padding: 10px 14px;
    border-left: 4px solid var(--report-terracotta);
    background: #fbf0e8;
    color: #54382e;
    font-weight: 700;
}
.header-info {
    padding: 16px;
    border: 1px solid rgba(95, 127, 104, 0.22);
    background: #f4faf6;
}
.header-info p {
    margin: 8px 0;
    color: var(--report-ink);
    font-size: 10.5pt;
}
.section h2,
.report-block h2 {
    padding: 10px 14px;
    border-left: 4px solid var(--report-sage);
    border-radius: var(--rq-radius-sm);
    background: var(--report-surface-muted);
    color: var(--report-sage-dark);
    font-family: var(--rq-font-display);
    font-size: 15pt;
    font-weight: 700;
    line-height: 1.25;
    letter-spacing: 0;
}
h3 {
    color: var(--report-teal);
    font-family: var(--rq-font-display);
    font-size: 12.5pt;
    font-weight: 700;
    line-height: 1.25;
    letter-spacing: 0;
}
.summary {
    padding: 16px;
    border-left: 4px solid var(--report-teal);
    background: #eef5f2;
    color: var(--report-ink);
}
table {
    width: 100%;
    margin: 20px 0;
    overflow: hidden;
    border: 1px solid var(--report-line);
    border-collapse: separate;
    border-spacing: 0;
    border-radius: var(--rq-radius-sm);
    background: var(--report-surface);
    font-size: 10pt;
}
th,
td {
    padding: 11px 12px;
    border-bottom: 1px solid var(--report-line);
    text-align: left;
    vertical-align: top;
}
th {
    background: var(--report-surface-strong);
    color: var(--report-sage-dark);
    font-size: 9pt;
    font-weight: 800;
    letter-spacing: 0;
    text-transform: uppercase;
}
tbody tr:nth-child(even) {
    background: #faf7ef;
}
tbody tr:last-child td {
    border-bottom: none;
}
.badge {
    padding: 4px 9px;
    border: 1px solid transparent;
    color: var(--report-surface);
}
.badge-high,
.prio-high {
    background: var(--report-bad);
}
.badge-mid,
.prio-mid,
.badge-warning {
    background: var(--report-warn);
}
.badge-low,
.prio-low,
.badge-success {
    background: var(--report-ok);
}
.badge-info {
    background: var(--report-teal);
}
.card {
    padding: 16px;
    margin-bottom: 15px;
}
.card.highlight {
    border-left: 4px solid var(--report-sage);
}
.card.quantum,
.llm-section {
    border-left: 4px solid var(--report-indigo);
}
.card-title {
    margin-bottom: 8px;
    color: var(--report-ink);
    font-size: 13pt;
    font-weight: 700;
}
.card-meta,
.note,
td.description {
    color: var(--report-muted);
}
.score,
td.rates,
.pattern .type {
    color: var(--report-sage-dark);
    font-weight: 700;
}
.finding {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 14px;
}
.finding .label {
    color: var(--report-ink);
    font-weight: 700;
}
.finding .score {
    padding: 5px 10px;
    border-radius: var(--rq-radius-sm);
    background: var(--report-sage-dark);
    color: var(--report-surface);
}
.finding.high {
    border-left: 4px solid var(--report-bad);
}
.finding.medium {
    border-left: 4px solid var(--report-warn);
}
.pattern,
.recommendation {
    padding: 14px;
    margin-bottom: 12px;
}
.recommendation {
    border-left: 4px solid var(--report-ok);
    background: #f4faf6;
}
.note {
    margin-top: 12px;
    padding: 12px 14px;
    border-left: 3px solid var(--report-terracotta);
    background: #fbf0e8;
    color: #54382e;
    font-size: 9pt;
}
td.rates {
    font-family: "Fira Code", "Consolas", "Monaco", monospace;
    font-size: 9pt;
}
td.description {
    max-width: 350px;
    font-size: 9.5pt;
    line-height: 1.5;
    overflow-wrap: anywhere;
    white-space: normal;
}
pre {
    max-height: min(70vh, 960px);
    overflow: auto;
    padding: 16px;
    border: 1px solid var(--report-line);
    border-radius: var(--rq-radius-sm);
    background: #282d2a;
    color: #f8f4eb;
    font-family: Consolas, "Cascadia Mono", monospace;
    font-size: 10pt;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}
p,
.summary,
.focus-text {
    overflow-wrap: anywhere;
    white-space: normal;
}
.profiles {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
}
.scroll-section {
    max-height: min(70vh, 960px);
    overflow-y: auto;
    padding: 0;
    border: 1px solid var(--report-line);
    border-radius: var(--rq-radius-sm);
    background: rgba(250, 247, 239, 0.75);
}
.scroll-section table {
    margin: 0;
    border: 0;
    border-radius: 0;
    box-shadow: none;
}
.visible-limit-note {
    margin-bottom: 8px;
}
hr {
    margin: 0 0 24px;
    border: 0;
    border-top: 1px solid var(--report-line);
}
.footer {
    padding: 24px 0 0;
    color: var(--report-muted);
    font-size: 0.9em;
    text-align: center;
}
@media print {
    body {
        padding: 10px !important;
        background: #ffffff !important;
        color: var(--report-ink) !important;
    }
    .container {
        width: 100% !important;
    }
    .header,
    .section,
    .report-block,
    .card,
    .finding,
    .pattern,
    .recommendation {
        background: #ffffff !important;
        box-shadow: none !important;
        page-break-inside: avoid;
    }
    .section h2,
    .report-block h2,
    th {
        background: var(--report-surface-strong) !important;
        color: var(--report-sage-dark) !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }
    .badge,
    .prio-high,
    .prio-mid,
    .prio-low {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }
}
"""


def normalize_visible_text(value: object) -> str:
    text = str(value if value is not None else "")
    if not any(marker in text for marker in _MOJIBAKE_MARKERS):
        return text

    repaired = text
    try:
        candidate = text.encode("latin-1").decode("utf-8")
        if sum(candidate.count(marker) for marker in _MOJIBAKE_MARKERS) < sum(
            text.count(marker) for marker in _MOJIBAKE_MARKERS
        ):
            repaired = candidate
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    for bad, replacement in _MOJIBAKE_FALLBACKS.items():
        repaired = repaired.replace(bad, replacement)
    return repaired


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_part(value: object) -> str:
    text = str(value or "").strip()
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text)
    return text.strip("_") or "unbekannt"


def client_slug(
    last_name: str, first_name: str, birth_date: str = "", birth_place: str = ""
) -> str:
    parts = [safe_part(last_name), safe_part(first_name)]
    if birth_date:
        parts.append(safe_part(birth_date))
    if birth_place:
        parts.append(safe_part(birth_place))
    return "_".join(parts)


def client_report_dir(
    output_root: str | Path,
    last_name: str,
    first_name: str,
    report_type: str,
    birth_date: str = "",
    birth_place: str = "",
    tenant_id: str = "",
) -> Path:
    """Verzeichnis fuer berichtsspezifische Ausgaben.

    Hierarchie: output_root / report_type / client_slug
    Z.B. C:\\Benutzer_Archive_Start / Deutung / Mustermann_Klaus_09041966_Augsburg

    `tenant_id` isoliert `output_root` selbst (Suffix `__<tenant_id>`), wenn
    gesetzt. Bleibt leer (Default), aendert sich nichts am bestehenden
    Pfadverhalten (additiv, rueckwaertskompatibel).
    """
    slug = client_slug(last_name, first_name, birth_date, birth_place)
    type_folder = safe_part(report_type) if report_type else ""
    path = Path(output_root)
    if tenant_id:
        path = path.with_name(f"{path.name}__{tenant_id}")
    if type_folder:
        path = path / type_folder
    return path / slug


def client_info(
    last_name: str,
    first_name: str,
    birth_date: str = "",
    birth_place: str = "",
) -> dict[str, str]:
    return {
        "last_name": str(last_name or "").strip(),
        "name": str(last_name or "").strip(),
        "first_name": str(first_name or "").strip(),
        "birth_date": str(birth_date or "").strip(),
        "birth_place": str(birth_place or "").strip(),
    }


def register_report_artifact(
    path: str | Path,
    client: Mapping[str, object],
    artifact_type: str,
    *,
    label: str = "",
    session_id: str = "",
    focus: str = "",
    config: Mapping[str, object] | None = None,
) -> dict[str, object] | None:
    try:
        target = Path(path)
        if not target.exists():
            return None
        resolved_session_id = session_id or (
            "sess-"
            + hashlib.sha256(str(target.parent.resolve()).encode("utf-8")).hexdigest()[
                :12
            ]
        )
        return RuntimeManifestService().register_artifact(
            dict(client),
            artifact_type=artifact_type,
            path=target,
            label=label,
            session_id=resolved_session_id,
            focus=focus,
            config=dict(config or {}),
        )
    except Exception:
        return None


def register_report_artifacts(
    paths: Iterable[str | Path],
    client: Mapping[str, object],
    artifact_type: str,
    *,
    label: str = "",
    session_id: str = "",
    focus: str = "",
    config: Mapping[str, object] | None = None,
) -> list[dict[str, object]]:
    registered: list[dict[str, object]] = []
    for path in paths:
        artifact = register_report_artifact(
            path,
            client,
            artifact_type,
            label=label,
            session_id=session_id,
            focus=focus,
            config=config,
        )
        if artifact is not None:
            registered.append(artifact)
    return registered


def write_html_pdf(html_path: str | Path, title: str = "") -> Path:
    target = Path(html_path)
    from tools.pdf_exporter import html_to_pdf

    return html_to_pdf(target, title or target.stem)


def ensure_output_dir(
    path: str | Path, fallback_root: str | Path | None = None
) -> Path:
    target = Path(path)
    try:
        target.mkdir(parents=True, exist_ok=True)
        return target
    except PermissionError:
        if fallback_root is None:
            raise
        fallback = Path(fallback_root) / target.name
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def find_client_scan_files(
    archive_root: str | Path,
    last_name: str,
    first_name: str,
    birth_date: str = "",
    birth_place: str = "",
    *,
    single: bool = False,
) -> list[Path]:
    root = Path(archive_root)
    patterns = [f"{safe_part(last_name)}_{safe_part(first_name)}_*"]
    if birth_date or birth_place:
        patterns.insert(
            0, f"{client_slug(last_name, first_name, birth_date, birth_place)}*"
        )

    # Such-Roots: neue Hierarchie (Resonanz/) zuerst, dann Fallback (flach)
    search_roots: list[Path] = []
    resonance_root = root / "Resonanz"
    if resonance_root.is_dir():
        search_roots.append(resonance_root)
    if root.is_dir():
        search_roots.append(root)

    files: list[Path] = []
    seen: set[Path] = set()
    for search_root in search_roots:
        for pattern in patterns:
            for folder in search_root.glob(pattern):
                if not folder.is_dir():
                    continue
                for path in folder.rglob("*_field_test.json"):
                    resolved = path.resolve()
                    if resolved not in seen:
                        files.append(path)
                        seen.add(resolved)
                for path in folder.rglob("*_multiplex_scan.json"):
                    resolved = path.resolve()
                    if resolved not in seen:
                        files.append(path)
                        seen.add(resolved)
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return files[:1] if single and files else files


def escape(value: object) -> str:
    return html.escape(normalize_visible_text(value))


def report_theme_css() -> str:
    return _REPORT_THEME_CSS.strip()


def report_document_start(title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
    <style>
{report_theme_css()}
    </style>
</head>
<body data-report-theme="{REPORT_THEME_ID}">
    <div class="container">
        <main class="report-shell" data-report-theme="{REPORT_THEME_ID}">
"""


def report_document_end() -> str:
    return """        </main>
    </div>
</body>
</html>
"""


def render_report_header(
    *,
    title: str,
    subtitle: str,
    focus: str = "",
    meta: Iterable[tuple[str, object]] = (),
) -> str:
    meta_html = "".join(
        f'<div class="metric"><span>{escape(label)}</span><strong>{escape(value)}</strong></div>'
        for label, value in meta
        if str(value or "").strip()
    )
    focus_html = f'<div class="focus">{escape(focus)}</div>' if focus else ""
    return f"""<section class="header report-block report-hero">
            <div class="report-topbar">
                <div class="eyebrow">Morphic Engine V1</div>
            </div>
            <h1>{escape(title)}</h1>
            <div class="subtitle">{escape(subtitle)}</div>
            {focus_html}
            <div class="metric-grid">{meta_html}</div>
        </section>
"""


def render_legacy_html(
    *,
    title: str,
    subtitle: str,
    body_html: str,
    focus: str = "",
    meta: Iterable[tuple[str, object]] = (),
) -> str:
    return (
        report_document_start(title)
        + render_report_header(
            title=title,
            subtitle=subtitle,
            focus=focus,
            meta=meta,
        )
        + wellbeing_html_block()
        + body_html
        + f"""<div class="footer">
            <p>Generiert am {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} | Morphic Engine V1</p>
        </div>
"""
        + report_document_end()
    )
