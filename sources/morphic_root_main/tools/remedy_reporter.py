from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Iterable

from apps.cli.commands.helpers.harmonization_helpers import (
    _render_visible_scroll_section,
)
from tools.reporting_common import (
    client_info,
    client_report_dir,
    escape,
    find_client_scan_files,
    register_report_artifact,
    render_legacy_html,
    safe_part,
    timestamp,
    write_html_pdf,
)


DEFAULT_ARCHIVE_DIR = Path(r"C:\Benutzer_Archive_Start")
DEFAULT_REMEDIES_DIR = Path(r"C:\Benutzer_Remedies_Start")
PROJECT_FALLBACK_DIR = Path("Benutzer_Archive") / "Remedy_Reports"


def _ensure_output_dir(path: Path) -> Path:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except PermissionError:
        fallback = PROJECT_FALLBACK_DIR / path.name
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _profile_label_from_source(path: Path, payload: dict) -> str:
    profile = str(payload.get("profile") or "").strip()
    if profile:
        return profile
    parent = path.parent.name
    if parent:
        return parent
    return path.stem


def _profile_remedies(path: Path, payload: dict) -> list[dict]:
    remedies = []
    for entry in payload.get("remedy_synergies") or []:
        if isinstance(entry, dict):
            remedies.append(
                {
                    "source": path.name,
                    "profile": _profile_label_from_source(path, payload),
                    **entry,
                }
            )
    return remedies


def _score_value(item: dict, key: str = "synergy_score") -> float:
    try:
        return float(item.get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


def _format_score(value: object) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return escape(value)


def _format_rates(values: list[object]) -> str:
    formatted = []
    for value in values:
        try:
            formatted.append(f"{float(value):.2f}")
        except (TypeError, ValueError):
            text = str(value or "").strip()
            if text:
                formatted.append(text)
    return ", ".join(formatted) if formatted else "-"


def _aggregate_remedies(remedies: list[dict]) -> list[dict]:
    aggregated: dict[str, dict] = {}
    for entry in remedies:
        score = _score_value(entry)
        for item_key, partner_key, rate_key in (
            ("item1", "item2", "rate1"),
            ("item2", "item1", "rate2"),
        ):
            name = str(entry.get(item_key) or "").strip()
            if not name:
                continue
            current = aggregated.setdefault(
                name.casefold(),
                {
                    "remedy": name,
                    "scores": [],
                    "rates": [],
                    "copen_rates": [],
                    "partners": {},
                    "profiles": set(),
                },
            )
            current["scores"].append(score)
            rates = entry.get(rate_key)
            if isinstance(rates, list):
                current["rates"].extend(rates[:4])
                # Copen-Rate aus erster Rate ableiten (rate * 162_000)
                if rates:
                    try:
                        base_rate = float(rates[0])
                        copen = base_rate * 162_000.0
                        copen_int = int(round(copen))
                        if copen_int not in current["copen_rates"]:
                            current["copen_rates"].append(copen_int)
                    except (TypeError, ValueError):
                        pass
            partner = str(entry.get(partner_key) or "").strip()
            if partner:
                current["partners"][partner] = max(
                    score, current["partners"].get(partner, 0.0)
                )
            profile = str(entry.get("profile") or "").strip()
            if profile:
                current["profiles"].add(profile)

    summary = []
    for current in aggregated.values():
        scores = current["scores"]
        max_score = max(scores) if scores else 0.0
        avg_score = sum(scores) / len(scores) if scores else 0.0
        partners = sorted(
            current["partners"].items(), key=lambda item: item[1], reverse=True
        )
        summary.append(
            {
                "remedy": current["remedy"],
                "score": avg_score,
                "rates": current["rates"],
                "copen_rates": current["copen_rates"],
                "synergies": [
                    {"remedy": partner, "score": partner_score}
                    for partner, partner_score in partners[:8]
                ],
                "synergy_score": max_score,
                "profiles": sorted(current["profiles"]),
            }
        )
    summary.sort(key=lambda item: item["synergy_score"], reverse=True)
    return summary


def _render_remedy_summary(
    summary: list[dict], source_count: int, combination_count: int
) -> str:
    rows = []
    for item in summary:
        synergies = "<br>".join(
            f"{escape(partner.get('remedy', ''))} ({_format_score(partner.get('score', 0))})"
            for partner in item.get("synergies") or []
        )
        if not synergies:
            synergies = "-"
        rows.append(
            "<tr>"
            f"<td><strong>{escape(item.get('remedy', ''))}</strong></td>"
            f"<td>{_format_score(item.get('score', 0))}</td>"
            f"<td class='rates'>{escape(_format_rates(item.get('rates') or []))}"
            + (
                f"<br>(Copen: {(item.get('copen_rates') or [0])[0]})"
                if item.get("copen_rates")
                else ""
            )
            + "</td>"
            f"<td style='font-size:10px;'>{synergies}</td>"
            f'<td><span class="badge badge-high">{_format_score(item.get("synergy_score", 0))}</span></td>'
            "</tr>"
        )
    if not rows:
        rows.append(
            '<tr><td colspan="5">Keine Remedy-Kombinationen im Quellmaterial enthalten.</td></tr>'
        )
    table_html = (
        "<table><tr><th>Remedy</th><th>Score</th><th>Raten</th><th>Synergien</th><th>Synergie-Score</th></tr>"
        f"{''.join(rows)}</table>"
    )

    return "".join(
        [
            '<div class="section">',
            "<h2>Synergetische Remedy-Kombinationen (Therapeutische Synergie-Analyse)</h2>",
            '<p class="note">Basierend auf therapeutischen Synergie-Regeln und Frequenz-Resonanz. ',
            "Kombinationen aus allen analysierten Profilen.</p>",
            f'<div class="summary">Quellen: {source_count} | Anzahl Remedies: {len(summary)} | Kombinationen: {combination_count}</div>',
            _render_visible_scroll_section(
                table_html,
                len(summary),
                label="Remedy-Uebersicht",
            ),
            '<p class="note">Synergie-Score: 0-5 = niedrig, 5-7 = mittel, 7-8 = gut, 8-10 = sehr stark.</p>',
            "</div>",
        ]
    )


def _render_remedy_pair_table(remedies: list[dict], file_count: int) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{idx}</td>"
        f"<td>{escape(item.get('item1', ''))}</td>"
        f"<td>{escape(item.get('item2', ''))}</td>"
        f"<td>{escape(item.get('profile', '-'))}</td>"
        f'<td><span class="badge badge-high">{_format_score(item.get("synergy_score", 0))}</span></td>'
        "</tr>"
        for idx, item in enumerate(sorted(remedies, key=_score_value, reverse=True), 1)
    )
    if not rows:
        rows = '<tr><td colspan="5">Keine Remedy-Kombinationen im Quellmaterial enthalten.</td></tr>'
    table_html = (
        "<table><tr><th>#</th><th>Remedy 1</th><th>Remedy 2</th><th>Profil</th><th>Score</th></tr>"
        f"{rows}</table>"
    )
    return "".join(
        [
            '<div class="section">',
            "<h2>Remedy-Kombinationen Detail</h2>",
            f'<div class="summary">Quellen: {file_count} | Kombinationen: {len(remedies)}</div>',
            _render_visible_scroll_section(
                table_html,
                len(remedies),
                label="Remedy-Kombinationen",
            ),
            "</div>",
        ]
    )


def _write_profile_remedy_report(
    path: Path,
    payload: dict,
    output_dir: Path,
    *,
    session_id: str = "",
    client: dict | None = None,
) -> tuple[Path, Path, Path]:
    profile_label = _profile_label_from_source(path, payload)
    remedies = _profile_remedies(path, payload)
    safe_profile = safe_part(profile_label)
    prefix = f"{safe_part(session_id)}_" if session_id else ""
    json_path = output_dir / f"{prefix}{safe_profile}_remedy.json"
    html_path = output_dir / f"{prefix}{safe_profile}_remedy.html"

    client_name = ""
    if isinstance(client, dict):
        first = str(client.get("first_name") or "").strip()
        last = str(client.get("name") or "").strip()
        client_name = f"{first} {last}".strip()

    report = {
        "schema": "morphic_remedy_profile_report",
        "schema_version": 1,
        "created_at": timestamp(),
        "session_id": session_id,
        "client": client or {},
        "source_file": path.name,
        "profile": profile_label,
        "remedy_count": len(remedies),
        "remedies": remedies,
    }
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    rows = "\n".join(
        "<tr>"
        f"<td>{idx}</td>"
        f"<td>{escape(item.get('item1', ''))}</td>"
        f"<td>{escape(item.get('item2', ''))}</td>"
        f'<td><span class="badge badge-high">{escape(item.get("synergy_score", ""))}</span></td>'
        "</tr>"
        for idx, item in enumerate(remedies, 1)
    )
    if not rows:
        rows = '<tr><td colspan="4">Keine Remedy-Kombinationen im Quellscan enthalten.</td></tr>'
    meta_pairs: list[tuple[str, object]] = [
        ("Profil", profile_label),
        ("Kombinationen", len(remedies)),
    ]
    if client_name:
        meta_pairs.insert(0, ("Klient", client_name))
    body = "".join(
        [
            '<div class="section">',
            "<h2>Remedy Detailbericht</h2>",
            f'<div class="summary">Profil: {escape(profile_label)} | Kombinationen: {len(remedies)}</div>',
            _render_visible_scroll_section(
                "<table><tr><th>#</th><th>Remedy 1</th><th>Remedy 2</th><th>Score</th></tr>"
                f"{rows}</table>",
                len(remedies),
                label="Profil-Remedies",
            ),
            "</div>",
        ]
    )
    title = f"Remedy Detailbericht - {client_name or profile_label}"
    html_path.write_text(
        render_legacy_html(
            title=title,
            subtitle="Morphic Engine Remedy-Profilbericht",
            body_html=body,
            meta=tuple(meta_pairs),
        ),
        encoding="utf-8",
    )
    pdf_path = write_html_pdf(html_path, title)
    return json_path, html_path, pdf_path


def _write_remedy_index(
    output_dir: Path,
    profile_reports: list[tuple[str, Path]],
    *,
    session_id: str = "",
    client: dict | None = None,
) -> Path:
    """Erstellt eine Index-HTML mit Links zu allen Profil-Remedy-Berichten."""
    client_name = ""
    if isinstance(client, dict):
        first = str(client.get("first_name") or "").strip()
        last = str(client.get("name") or "").strip()
        client_name = f"{first} {last}".strip()

    from datetime import datetime

    stamp_display = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    prefix = f"{safe_part(session_id)}_" if session_id else ""
    index_name = f"{prefix}remedy_kombinationen_index.html"
    index_path = output_dir / index_name

    links = "\n".join(
        f"<li><a href='{html.escape(html_path.name)}' target='_blank'>{html.escape(profile_label)}</a></li>"
        for profile_label, html_path in profile_reports
        if html_path.exists()
    )
    if not links:
        links = "<li>Keine Profil-Remedy-Berichte vorhanden.</li>"

    title = (
        f"Remedy-Kombination - {client_name}" if client_name else "Remedy-Kombination"
    )
    html_content = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title>"
        "<style>body{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}"
        "h1{color:#2c3e50}ul{list-style:none;padding:0}li{margin:8px 0}"
        "a{color:#2980b9;text-decoration:none}a:hover{text-decoration:underline}"
        "p{color:#555}</style></head><body>"
        f"<h1>\U0001f9ea Remedy-Kombination - {html.escape(client_name)}</h1>"
        f"<p>Uebersicht ueber die einzelnen Remedy-Berichte ({len(profile_reports)} Profile).</p>"
        f"<ul>{links}</ul>"
        f"<p>Generiert am {stamp_display}</p>"
        "</body></html>"
    )
    index_path.write_text(html_content, encoding="utf-8")
    return index_path


def consolidate_remedy_synergies(
    json_files: Iterable[str | Path],
    output_dir: str | Path,
    *,
    top_n: int = 0,
    title: str = "Remedy Report",
    session_id: str = "",
    client: dict | None = None,
) -> bool:
    files = [Path(path) for path in json_files]
    out_dir = Path(output_dir)
    out_dir = _ensure_output_dir(out_dir)

    remedies = []
    profile_reports: list[tuple[str, Path]] = []
    for path in files:
        payload = _load_json(path)
        profile_label = _profile_label_from_source(path, payload)
        json_path, html_path, _pdf_path = _write_profile_remedy_report(
            path, payload, out_dir, session_id=session_id, client=client
        )
        profile_reports.append((profile_label, html_path))
        for entry in payload.get("remedy_synergies") or []:
            if isinstance(entry, dict):
                remedies.append(
                    {"source": path.name, "profile": profile_label, **entry}
                )

    report = {
        "schema": "morphic_remedy_report",
        "schema_version": 1,
        "created_at": timestamp(),
        "session_id": session_id,
        "client": client or {},
        "source_files": [path.name for path in files],
        "remedy_count": len(remedies),
        "remedy_summary": _aggregate_remedies(remedies),
        "remedies": remedies,
    }
    stamp = safe_part(session_id) if session_id else timestamp()
    suffix = f"top{top_n}_remedies" if top_n else "remedy_report"
    json_path = out_dir / f"{stamp}_{suffix}.json"
    html_path = out_dir / f"{stamp}_{suffix}.html"
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    body = _render_remedy_summary(
        report["remedy_summary"], len(files), len(remedies)
    ) + _render_remedy_pair_table(remedies, len(files))
    meta_pairs: list[tuple[str, object]] = [
        ("Quellen", len(files)),
        ("Kombinationen", len(remedies)),
    ]
    if isinstance(client, dict):
        first = str(client.get("first_name") or "").strip()
        last = str(client.get("name") or "").strip()
        cn = f"{first} {last}".strip()
        if cn:
            meta_pairs.insert(0, ("Klient", cn))
    html_path.write_text(
        render_legacy_html(
            title=title,
            subtitle="Konsolidierter Morphic Remedy-Bericht",
            body_html=body,
            meta=tuple(meta_pairs),
        ),
        encoding="utf-8",
    )
    write_html_pdf(html_path, title)

    # Index-Datei mit Links zu allen Profil-Remedy-Berichten
    if profile_reports:
        _write_remedy_index(
            out_dir, profile_reports, session_id=session_id, client=client
        )

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create Morphic remedy summary reports."
    )
    parser.add_argument("last_name")
    parser.add_argument("first_name")
    parser.add_argument("--single", action="store_true")
    parser.add_argument("--session", action="store_true")
    parser.add_argument("--top-n", type=int, default=0)
    parser.add_argument("--birth-date", default="")
    parser.add_argument("--birth-place", default="")
    parser.add_argument("--archive-root", default=str(DEFAULT_ARCHIVE_DIR))
    parser.add_argument("--output-root", default=str(DEFAULT_REMEDIES_DIR))
    args = parser.parse_args()

    files = find_client_scan_files(
        args.archive_root,
        args.last_name,
        args.first_name,
        args.birth_date,
        args.birth_place,
        single=args.single,
    )
    base_dir = client_report_dir(
        args.output_root,
        args.last_name,
        args.first_name,
        "Remedies",
        args.birth_date,
        args.birth_place,
    )
    output_dir = _ensure_output_dir(base_dir)
    consolidate_remedy_synergies(
        files,
        output_dir,
        top_n=args.top_n,
        title=f"Remedy Report - {args.first_name} {args.last_name}",
        client=client_info(
            args.last_name, args.first_name, args.birth_date, args.birth_place
        ),
    )
    client = client_info(
        args.last_name, args.first_name, args.birth_date, args.birth_place
    )
    for json_path in output_dir.glob("*_remedies.json"):
        register_report_artifact(
            json_path,
            client,
            "remedy_json",
            label="Remedy JSON",
            config={
                "command": "remedy_reporter",
                "source_files": len(files),
                "top_n": args.top_n,
            },
        )
    for html_path in output_dir.glob("*_remedies.html"):
        register_report_artifact(
            html_path,
            client,
            "remedy_html",
            label="Remedy HTML",
            config={
                "command": "remedy_reporter",
                "source_files": len(files),
                "top_n": args.top_n,
            },
        )
    for pdf_path in output_dir.glob("*_remedies.pdf"):
        register_report_artifact(
            pdf_path,
            client,
            "remedy_pdf",
            label="Remedy PDF",
            config={
                "command": "remedy_reporter",
                "source_files": len(files),
                "top_n": args.top_n,
            },
        )
    for json_path in output_dir.glob("*_remedy.json"):
        register_report_artifact(
            json_path,
            client,
            "remedy_profile_json",
            label="Remedy Profil JSON",
            config={
                "command": "remedy_reporter",
                "source_files": len(files),
                "top_n": args.top_n,
            },
        )
    for pdf_path in output_dir.glob("*_remedy.pdf"):
        register_report_artifact(
            pdf_path,
            client,
            "remedy_profile_pdf",
            label="Remedy Profil PDF",
            config={
                "command": "remedy_reporter",
                "source_files": len(files),
                "top_n": args.top_n,
            },
        )
    for html_path in output_dir.glob("*_remedy.html"):
        register_report_artifact(
            html_path,
            client,
            "remedy_profile_html",
            label="Remedy Profil HTML",
            config={
                "command": "remedy_reporter",
                "source_files": len(files),
                "top_n": args.top_n,
            },
        )
    print(f"Remedy report written: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
