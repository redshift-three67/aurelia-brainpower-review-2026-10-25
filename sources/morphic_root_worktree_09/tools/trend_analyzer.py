from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from apps.cli.commands.helpers.harmonization_helpers import (
    _render_visible_scroll_section,
)
from tools.reporting_common import (
    client_info,
    client_report_dir,
    ensure_output_dir,
    escape,
    find_client_scan_files,
    register_report_artifact,
    render_legacy_html,
    timestamp,
    write_html_pdf,
)
from core.compliance.operator_context import resolve_operator_context


DEFAULT_ARCHIVE_DIR = Path(r"C:\Benutzer_Archive_Start")
DEFAULT_TRENDS_DIR = Path(r"C:\Benutzer_Trends_Start")
PROJECT_FALLBACK_DIR = Path("Benutzer_Archive") / "Trend_Reports"
SESSION_FOLDER_RE = re.compile(r"^\d{8}_\d{6}_.+SESSION$")
SCAN_STEM_RE = re.compile(r"^(\d{8}_\d{6})_")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _top_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    sub_results = payload.get("sub_results") or {}
    if isinstance(sub_results, dict) and isinstance(sub_results.get("top"), list):
        return [item for item in sub_results["top"] if isinstance(item, dict)]
    top_scores = payload.get("top_scores")
    if isinstance(top_scores, list):
        return [item for item in top_scores if isinstance(item, dict)]
    return []


def _build_trends(files: list[Path]) -> list[dict[str, Any]]:
    chronological = sorted(files, key=lambda path: path.stat().st_mtime)
    series: dict[str, list[dict[str, Any]]] = {}
    for index, path in enumerate(chronological):
        payload = _load_json(path)
        for item in _top_items(payload):
            label = str(item.get("label", "") or "").strip()
            if not label:
                continue
            try:
                score = float(item.get("score", 0.0) or 0.0)
            except (TypeError, ValueError):
                score = 0.0
            series.setdefault(label, []).append(
                {
                    "scan_index": index,
                    "source": str(path),
                    "score": score,
                    "group": str(item.get("group", "") or ""),
                }
            )

    trends: list[dict[str, Any]] = []
    for label, points in series.items():
        if not points:
            continue
        first = points[0]
        latest = points[-1]
        first_score = round(float(first["score"]), 4)
        latest_score = round(float(latest["score"]), 4)
        delta = round(latest_score - first_score, 4)
        if delta > 0.0001:
            direction = "steigend"
        elif delta < -0.0001:
            direction = "fallend"
        else:
            direction = "stabil"
        trends.append(
            {
                "label": label,
                "group": latest.get("group") or first.get("group") or "",
                "occurrences": len(points),
                "first_score": first_score,
                "latest_score": latest_score,
                "delta": delta,
                "direction": direction,
                "sources": [point["source"] for point in points],
            }
        )
    trends.sort(
        key=lambda item: (abs(float(item["delta"])), float(item["latest_score"])),
        reverse=True,
    )
    return trends


def _session_key(path: Path) -> str:
    for parent in path.parents:
        if SESSION_FOLDER_RE.match(parent.name):
            return parent.name
    match = SCAN_STEM_RE.match(path.stem)
    if match:
        return match.group(1)
    return str(path)


def _distinct_session_count(files: list[Path]) -> int:
    return len({_session_key(path) for path in files})


def _ensure_output_dir(path: Path) -> Path:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except PermissionError:
        fallback = PROJECT_FALLBACK_DIR / path.name
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def _render_trend_table(trends: list[dict[str, Any]], file_count: int) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(item.get('label', ''))}</td>"
        f"<td>{escape(item.get('group') or '-')}</td>"
        f"<td>{float(item.get('first_score', 0.0) or 0.0):.4f}</td>"
        f"<td>{float(item.get('latest_score', 0.0) or 0.0):.4f}</td>"
        f"<td>{float(item.get('delta', 0.0) or 0.0):.4f}</td>"
        f"<td>{escape(item.get('direction', ''))}</td>"
        "</tr>"
        for item in trends
    )
    table_html = (
        "<table><tr><th>Label</th><th>Gruppe</th><th>Erster Score</th><th>Letzter Score</th><th>Delta</th><th>Richtung</th></tr>"
        f"{rows}</table>"
    )
    return (
        '<div class="section">'
        "<h2>Trend-Historik</h2>"
        f'<div class="summary">Gefundene Scans: {file_count} | Trends: {len(trends)}</div>'
        + _render_visible_scroll_section(
            table_html, len(trends), label="Trend-Historik"
        )
        + "</div>"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a lightweight Morphic trend report."
    )
    parser.add_argument("last_name")
    parser.add_argument("first_name")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--db", action="store_true")
    parser.add_argument("--output", default="html")
    parser.add_argument("--birth-date", default="")
    parser.add_argument("--birth-place", default="")
    parser.add_argument("--archive-root", default=str(DEFAULT_ARCHIVE_DIR))
    parser.add_argument("--output-root", default=str(DEFAULT_TRENDS_DIR))
    args = parser.parse_args()

    files = find_client_scan_files(
        args.archive_root,
        args.last_name,
        args.first_name,
        args.birth_date,
        args.birth_place,
    )
    out_dir = client_report_dir(
        args.output_root,
        args.last_name,
        args.first_name,
        "Trends",
        args.birth_date,
        args.birth_place,
        tenant_id=(
            resolve_operator_context().tenant_id
            if args.output_root == str(DEFAULT_TRENDS_DIR)
            else ""
        ),
    )
    client = client_info(
        args.last_name, args.first_name, args.birth_date, args.birth_place
    )

    if len(files) < 2 or _distinct_session_count(files) < 2:
        out_dir = _ensure_output_dir(out_dir)
        notice_path = out_dir / "Hinweis.txt"
        notice_path.write_text(
            "Noch keine Trends verfuegbar, da zu wenige bisherige Testungen vorliegen.\n\n"
            "Die Trendanalyse benoetigt mindestens zwei verwertbare Scan-Exporte.\n",
            encoding="utf-8",
        )
        register_report_artifact(
            notice_path,
            client,
            "trend_notice",
            label="Trend Hinweis",
            config={"command": "trend_analyzer", "source_files": len(files)},
        )
        print(f"Trendanalyse notice written: {out_dir}")
        return 0

    stamp = timestamp()
    out_dir = _ensure_output_dir(out_dir)
    trends = _build_trends(files)
    payload = {
        "schema": "morphic_trend_report",
        "schema_version": 1,
        "created_at": timestamp(),
        "source_files": [str(path) for path in files],
        "trend_count": len(trends),
        "trends": trends,
    }
    json_path = out_dir / f"trendanalyse_{stamp}.json"
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    body = _render_trend_table(trends, len(files))
    html_path = out_dir / f"trendanalyse_{stamp}.html"
    html_path.write_text(
        render_legacy_html(
            title=f"Trendanalyse - {args.first_name} {args.last_name}",
            subtitle="Morphic Engine Verlaufsbericht",
            body_html=body,
            meta=(
                ("Scans", len(files)),
                ("Datenbank", "aktiv" if args.db else "inaktiv"),
            ),
        ),
        encoding="utf-8",
    )
    pdf_path = write_html_pdf(
        html_path, f"Trendanalyse - {args.first_name} {args.last_name}"
    )
    register_report_artifact(
        json_path,
        client,
        "trend_json",
        label="Trend JSON",
        config={"command": "trend_analyzer", "source_files": len(files)},
    )
    register_report_artifact(
        html_path,
        client,
        "trend_html",
        label="Trend HTML",
        config={"command": "trend_analyzer", "source_files": len(files)},
    )
    register_report_artifact(
        pdf_path,
        client,
        "trend_pdf",
        label="Trend PDF",
        config={"command": "trend_analyzer", "source_files": len(files)},
    )
    print(f"Trendanalyse written: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
