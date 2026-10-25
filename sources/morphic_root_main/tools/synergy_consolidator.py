from __future__ import annotations

import argparse
import json
from collections import defaultdict
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
    timestamp,
    write_html_pdf,
)


DEFAULT_ARCHIVE_DIR = Path(r"C:\Benutzer_Archive_Start")
DEFAULT_SYNERGY_DIR = Path(r"C:\Benutzer_Synergy_Start")
PROJECT_FALLBACK_DIR = Path("Benutzer_Archive") / "Synergy_Reports"


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


def _score_value(item: dict, key: str = "score") -> float:
    try:
        return float(item.get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


def _format_score(value: object) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return escape(value)


def _item_label(item: object) -> str:
    if isinstance(item, dict):
        return str(
            item.get("label") or item.get("name") or item.get("item") or ""
        ).strip()
    return str(item or "").strip()


def _item_group(item: object) -> str:
    if isinstance(item, dict):
        return str(item.get("group") or item.get("category") or "").strip()
    return ""


def _synergy_item_labels(entry: dict) -> list[str]:
    return [
        label
        for label in (_item_label(item) for item in entry.get("items") or [])
        if label
    ]


def _components_note(entry: dict) -> str:
    components = entry.get("components")
    if not isinstance(components, dict):
        return ""
    labels = (
        ("individual_scores", "Einzel-Scores"),
        ("resonance", "Resonanz-Verstärkung"),
        ("harmony", "Harmonie"),
        ("relevance", "Relevanz"),
    )
    parts = []
    for key, label in labels:
        if key in components:
            parts.append(f"{escape(label)}: {_format_score(components.get(key))}/10.0")
    return " | ".join(parts)


def _cross_profile_synergies(items: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for entry in items:
        profile = str(entry.get("profile") or "").strip()
        score = _score_value(entry)
        for item in entry.get("items") or []:
            label = _item_label(item)
            if not label:
                continue
            key = label.casefold()
            current = grouped.setdefault(
                key,
                {
                    "item": label,
                    "groups": set(),
                    "profiles": set(),
                    "scores": [],
                },
            )
            group = _item_group(item)
            if group:
                current["groups"].add(group)
            if profile:
                current["profiles"].add(profile)
            current["scores"].append(score)

    cross_profile = []
    for current in grouped.values():
        profiles = sorted(current["profiles"])
        if len(profiles) < 2:
            continue
        scores = current["scores"]
        cross_profile.append(
            {
                "item": current["item"],
                "groups": sorted(current["groups"]),
                "profiles": profiles,
                "profile_count": len(profiles),
                "average_score": sum(scores) / len(scores) if scores else 0.0,
                "max_score": max(scores) if scores else 0.0,
            }
        )
    cross_profile.sort(
        key=lambda item: (item["profile_count"], item["max_score"]), reverse=True
    )
    return cross_profile


def _render_profile_overview(profiles: list[dict]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{idx}</td>"
        f"<td>{escape(profile.get('profile', ''))}</td>"
        f"<td>{escape(profile.get('synergy_count', 0))}</td>"
        f'<td><span class="badge badge-high">{_format_score(profile.get("top_score", 0))}</span></td>'
        f"<td>{escape(Path(str(profile.get('source', ''))).name)}</td>"
        "</tr>"
        for idx, profile in enumerate(profiles, 1)
    )
    if not rows:
        rows = '<tr><td colspan="5">Keine Profile im Quellmaterial gefunden.</td></tr>'
    table_html = (
        "<table><tr><th>#</th><th>Profil</th><th>Synergien</th><th>Top-Score</th><th>Quelle</th></tr>"
        f"{rows}</table>"
    )
    return "".join(
        [
            '<div class="section">',
            "<h2>Analysierte Profile</h2>",
            _render_visible_scroll_section(table_html, len(profiles), label="Profile"),
            "</div>",
        ]
    )


def _render_cross_profile(cross_profile: list[dict]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{idx}</td>"
        f"<td><strong>{escape(item.get('item', ''))}</strong></td>"
        f"<td>{escape(', '.join(item.get('groups') or []))}</td>"
        f"<td>{escape(', '.join(item.get('profiles') or []))}</td>"
        f"<td>{_format_score(item.get('average_score', 0))}</td>"
        f'<td><span class="badge badge-high">{_format_score(item.get("max_score", 0))}</span></td>'
        "</tr>"
        for idx, item in enumerate(cross_profile, 1)
    )
    if not rows:
        rows = '<tr><td colspan="6">Keine profileübergreifenden Wiederholungen im Quellmaterial gefunden.</td></tr>'
    table_html = (
        "<table><tr><th>#</th><th>Item</th><th>Gruppe</th><th>Profile</th><th>Ø Score</th><th>Max Score</th></tr>"
        f"{rows}</table>"
    )
    return "".join(
        [
            '<div class="section">',
            "<h2>Cross-Profile Synergien</h2>",
            '<p class="note">Items, die in mehreren Profilen hohe Quantum-Synergy-Resonanz zeigen.</p>',
            _render_visible_scroll_section(
                table_html,
                len(cross_profile),
                label="Cross-Profile Synergien",
            ),
            "</div>",
        ]
    )


def _render_synergy_card(entry: dict, idx: int) -> str:
    items = "\n".join(
        f'<li>{escape(_item_label(item))} <span style="color:#a0aec0;">({escape(_item_group(item))})</span></li>'
        for item in entry.get("items") or []
        if _item_label(item)
    )
    if not items:
        items = "<li>Keine Einzelitems ausgewiesen.</li>"
    components = _components_note(entry)
    components_html = f"<br>{components}" if components else ""
    score = _score_value(entry)
    if score >= 7.0:
        badge_cls = "badge-success"
        cat_label = "Hoch"
    elif score >= 5.0:
        badge_cls = "badge-warning"
        cat_label = "Mittel"
    else:
        badge_cls = "badge-info"
        cat_label = "Niedrig"
    return (
        '<div class="card quantum" style="margin-bottom:15px;">'
        f'<div class="card-title">#{idx} \u2013 Synergy-Score: <span class="score">{_format_score(entry.get("score", 0))}/10.0</span> '
        f'<span class="badge {badge_cls}">{cat_label}</span></div>'
        f'<div style="margin-top:12px;"><strong>Kombination ({len([i for i in (entry.get("items") or []) if _item_label(i)])} Items):</strong>'
        f'<ul style="margin:8px 0;padding-left:20px;">{items}</ul></div>'
        f'<div style="margin-top:10px;padding:10px;background:#f8fafc;border-radius:6px;font-size:12px;">'
        f"<strong>Komponenten:</strong>{components_html}</div>"
        "</div>"
    )


def _render_profile_details(profiles: list[dict]) -> str:
    blocks = []
    for profile in profiles:
        synergies = sorted(
            profile.get("synergies") or [], key=_score_value, reverse=True
        )
        cards = "\n".join(
            _render_synergy_card(entry, idx)
            for idx, entry in enumerate(synergies[:5], 1)
        )
        if not cards:
            cards = (
                '<p class="note">Keine Quantum-Synergien in diesem Profil gefunden.</p>'
            )
        profile_name = escape(profile.get("profile", ""))
        synergy_count = escape(profile.get("synergy_count", 0))
        blocks.append(
            '<div style="background:#f8f9fa;padding:20px;border-radius:12px;margin-bottom:20px;border-left:4px solid #667eea;">'
            f'<h3 style="color:#667eea;margin-bottom:15px;">\U0001f4ca Profil: {profile_name}</h3>'
            f'<p style="color:#718096;font-size:13px;margin-bottom:15px;">Quantum-Synergien aus diesem Profil ({synergy_count} gefunden):</p>'
            f"{cards}"
            "</div>"
        )
    fallback_note = (
        '<p class="note">Keine Quantum-Synergien im Quellmaterial gefunden.</p>'
    )
    blocks_html = "".join(blocks) if blocks else fallback_note
    return (
        '<div class="section">'
        "<h2>\u269b\ufe0f Quantum-Synergy Analyse</h2>"
        '<p style="color:#718096;font-size:14px;margin-bottom:20px;">Grover-basierte Multi-Item Kombinationen pro Profil:</p>'
        f"{blocks_html}"
        "</div>"
    )


def _render_top_synergies(items: list[dict]) -> str:
    top_items = sorted(items, key=_score_value, reverse=True)[:5]
    cards = []
    for idx, entry in enumerate(top_items, 1):
        items_html = "\n".join(
            f'<li><strong>{escape(_item_label(item))}</strong> <span style="color:#a0aec0;">({escape(_item_group(item))})</span></li>'
            for item in entry.get("items") or []
            if _item_label(item)
        )
        if not items_html:
            items_html = "<li>Keine Einzelitems ausgewiesen.</li>"
        components = entry.get("components", {})
        comp_lines = ""
        if isinstance(components, dict):
            comp_labels = {
                "individual_scores": "Einzelwirkungen",
                "resonance": "Resonanz-Verstaerkung",
                "harmony": "Frequenz-Harmonien",
                "relevance": "Fokus-Relevanz",
            }
            comp_lines = "".join(
                f"\u2022 {label}: <strong>{_format_score(components.get(key))}/10.0</strong><br>"
                for key, label in comp_labels.items()
                if key in components
            )
        score = _score_value(entry)
        if score >= 7.0:
            badge_cls = "badge-success"
            cat_label = "Hoch"
        elif score >= 5.0:
            badge_cls = "badge-warning"
            cat_label = "Mittel"
        else:
            badge_cls = "badge-info"
            cat_label = "Niedrig"
        source_profile = escape(entry.get("profile", ""))
        cards.append(
            '<div style="background:linear-gradient(135deg, rgba(102,126,234,0.08), rgba(167,199,231,0.12));'
            'padding:20px;border-radius:12px;margin-bottom:15px;border-left:4px solid #48bb78;">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">'
            f'<div style="font-size:16px;font-weight:600;color:#2d3748;">#{idx} \u2013 Score: {_format_score(entry.get("score", 0))}/10.0</div>'
            f'<div><span class="badge {badge_cls}">{cat_label}</span> '
            f'<span style="font-size:13px;color:#718096;">Quelle: {source_profile}</span></div>'
            "</div>"
            f'<div style="margin-top:12px;"><strong>Kombination (4 Items):</strong>'
            f'<ul style="margin:8px 0;padding-left:20px;">{items_html}</ul></div>'
            f'<div style="margin-top:12px;padding:12px;background:rgba(255,255,255,0.6);border-radius:6px;font-size:13px;">'
            f"<strong>\U0001f52c Komponenten-Analyse:</strong><br>{comp_lines}</div>"
            "</div>"
        )
    cards_html = "".join(cards)
    if not cards_html:
        cards_html = '<p class="note">Keine profileuebergreifenden Top-Synergien im Quellmaterial gefunden.</p>'
    return (
        '<div class="section">'
        "<h2>\U0001f31f Top Quantum-Synergien (Profile-uebergreifend)</h2>"
        '<p style="color:#718096;font-size:14px;margin-bottom:20px;">Die besten 5 Quantum-Kombinationen aus allen analysierten Profilen:</p>'
        f"{cards_html}"
        "</div>"
    )
    if not items:
        items = "<li>Keine Einzelitems ausgewiesen.</li>"
    components = _components_note(entry)
    components_html = f"<br>{components}" if components else ""
    return (
        '<div style="background:rgba(255,255,255,0.65);border:1px solid rgba(107,165,208,0.18);'
        'border-radius:12px;padding:16px;margin:12px 0;">'
        f'<div style="font-size:13pt;font-weight:600;color:#2C3E50;">#{idx} - Synergy-Score: '
        f'<span class="badge badge-high">{_format_score(entry.get("score", 0))}/10.0</span></div>'
        f'<ul style="margin:12px 0 8px 22px;">{items}</ul>'
        '<div class="note">'
        f"Kategorie: {escape(entry.get('category', '-'))} | "
        f"Scan-Overlap: {escape(entry.get('scan_overlap', 0))}"
        f"{components_html}"
        "</div>"
        "</div>"
    )


def _render_flat_synergy_table(items: list[dict], file_count: int) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{idx}</td>"
        f'<td><span class="badge badge-high">{_format_score(item.get("score", 0))}</span></td>'
        f"<td>{escape(item.get('profile', '-'))}</td>"
        f"<td>{escape(item.get('category', '-'))}</td>"
        f"<td>{escape(', '.join(_synergy_item_labels(item)))}</td>"
        "</tr>"
        for idx, item in enumerate(sorted(items, key=_score_value, reverse=True), 1)
    )
    if not rows:
        rows = '<tr><td colspan="5">Keine synergistischen Kombinationen im Quellmaterial gefunden.</td></tr>'
    table_html = (
        "<table><tr><th>#</th><th>Score</th><th>Profil</th><th>Kategorie</th><th>Items</th></tr>"
        f"{rows}</table>"
    )
    return "".join(
        [
            '<div class="section">',
            "<h2>Synergistische Kombinationen</h2>",
            f'<div class="summary">Quellen: {file_count} | Kombinationen: {len(items)}</div>',
            _render_visible_scroll_section(
                table_html,
                len(items),
                label="Synergistische Kombinationen",
            ),
            "</div>",
        ]
    )


def consolidate_synergies(
    json_files: Iterable[str | Path],
    output_dir: str | Path,
    *,
    client: dict | None = None,
    focus: str = "",
    session_id: str = "",
) -> bool:
    files = [Path(path) for path in json_files]
    out_dir = Path(output_dir)
    out_dir = _ensure_output_dir(out_dir)

    items = []
    profiles = []
    for path in files:
        payload = _load_json(path)
        profile_label = _profile_label_from_source(path, payload)
        profile_items = []
        for entry in payload.get("quantum_synergy") or []:
            if isinstance(entry, dict):
                synergy = {"source": path.name, "profile": profile_label, **entry}
                items.append(synergy)
                profile_items.append(synergy)
        top_score = max((_score_value(item) for item in profile_items), default=0.0)
        profiles.append(
            {
                "profile": profile_label,
                "source": path.name,
                "synergy_count": len(profile_items),
                "top_score": top_score,
                "synergies": profile_items,
            }
        )

    profiles.sort(
        key=lambda profile: (
            _score_value(profile, "top_score"),
            str(profile.get("profile", "")),
        ),
        reverse=True,
    )
    cross_profile = _cross_profile_synergies(items)
    top_synergies = sorted(items, key=_score_value, reverse=True)[:10]

    client_name = ""
    if isinstance(client, dict):
        first = str(client.get("first_name") or "").strip()
        last = str(client.get("name") or "").strip()
        client_name = f"{first} {last}".strip()

    report = {
        "schema": "morphic_synergy_report",
        "schema_version": 1,
        "created_at": timestamp(),
        "session_id": session_id,
        "client": client or {},
        "focus": focus,
        "source_files": [path.name for path in files],
        "synergy_count": len(items),
        "profile_count": len(profiles),
        "profiles": profiles,
        "cross_profile_synergies": cross_profile,
        "top_synergies": top_synergies,
        "synergies": items,
    }
    json_path = out_dir / "synergy_gesamt.json"
    html_path = out_dir / "synergy_gesamt.html"
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    body = (
        _render_profile_overview(profiles)
        + _render_cross_profile(cross_profile)
        + _render_profile_details(profiles)
        + _render_top_synergies(items)
        + _render_flat_synergy_table(items, len(files))
    )
    title = (
        f"Synergy-Gesamtanalyse - {client_name}"
        if client_name
        else "Synergy-Gesamtanalyse"
    )
    meta_pairs: list[tuple[str, object]] = [
        ("Quellen", len(files)),
        ("Kombinationen", len(items)),
    ]
    if client_name:
        meta_pairs.insert(0, ("Klient", client_name))
    if focus:
        meta_pairs.append(("Fokus", focus))
    html_path.write_text(
        render_legacy_html(
            title=title,
            subtitle="Konsolidierter Morphic Synergy-Bericht",
            body_html=body,
            meta=tuple(meta_pairs),
        ),
        encoding="utf-8",
    )
    write_html_pdf(html_path, title)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consolidate Morphic synergy scan reports."
    )
    parser.add_argument("last_name")
    parser.add_argument("first_name")
    parser.add_argument("--single", action="store_true")
    parser.add_argument("--hours", default="24")
    parser.add_argument("--birth-date", default="")
    parser.add_argument("--birth-place", default="")
    parser.add_argument("--archive-root", default=str(DEFAULT_ARCHIVE_DIR))
    parser.add_argument("--output-root", default=str(DEFAULT_SYNERGY_DIR))
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
        "Synergy",
        args.birth_date,
        args.birth_place,
    )
    output_dir = base_dir / f"{timestamp()}_synergy_report"
    client = client_info(
        args.last_name, args.first_name, args.birth_date, args.birth_place
    )
    consolidate_synergies(files, output_dir, client=client)
    register_report_artifact(
        output_dir / "synergy_gesamt.json",
        client,
        "synergy_json",
        label="Synergy Gesamt JSON",
        config={"command": "synergy_consolidator", "source_files": len(files)},
    )
    register_report_artifact(
        output_dir / "synergy_gesamt.html",
        client,
        "synergy_html",
        label="Synergy Gesamt HTML",
        config={"command": "synergy_consolidator", "source_files": len(files)},
    )
    register_report_artifact(
        output_dir / "synergy_gesamt.pdf",
        client,
        "synergy_pdf",
        label="Synergy Gesamt PDF",
        config={"command": "synergy_consolidator", "source_files": len(files)},
    )
    print(f"Synergy report written: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
