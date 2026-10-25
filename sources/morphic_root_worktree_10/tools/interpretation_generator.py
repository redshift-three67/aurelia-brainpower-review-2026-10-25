from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from tools.reporting_common import (
    client_info,
    client_report_dir,
    escape,
    find_client_scan_files,
    register_report_artifact,
    render_legacy_html,
    timestamp,
)
from tools.simple_pdf import write_text_pdf


DEFAULT_ARCHIVE_DIR = Path(r"C:\Benutzer_Archive_Start")
DEFAULT_DEUTUNG_DIR = Path(r"C:\Benutzer_Deutung_Start")
PROJECT_FALLBACK_DIR = Path("Benutzer_Archive") / "Deutung_Reports"


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
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _top_findings(payload: dict) -> list[dict]:
    sub_results = payload.get("sub_results") or {}
    if isinstance(sub_results, dict) and isinstance(sub_results.get("top"), list):
        return [item for item in sub_results["top"] if isinstance(item, dict)]
    top_scores = payload.get("top_scores")
    if isinstance(top_scores, list):
        return [item for item in top_scores if isinstance(item, dict)]
    return []


def _quantum_labels(entry: dict) -> str:
    items = entry.get("items")
    if isinstance(items, list):
        labels = [
            str(item.get("label", "")).strip()
            for item in items
            if isinstance(item, dict)
        ]
        labels = [label for label in labels if label]
        if labels:
            return " + ".join(labels)
    return str(entry.get("category") or entry.get("label") or "Quantum-Synergy").strip()


def _scan_sections(files: list[Path]) -> tuple[str, str, list[dict], list[str]]:
    """Erzeugt die Scan-Body-Sektionen und sammelt Befunde/Muster fuer Deutung.

    Returns: (body_html, text_summary, findings, profile_names)
    """
    findings: list[dict] = []
    patterns: list[str] = []
    remedies: list[str] = []
    profile_names: list[str] = []

    for path in files:
        payload = _load_json(path)
        profile = str(payload.get("profile") or "").strip()
        if profile and profile not in profile_names:
            profile_names.append(profile)
        for item in _top_findings(payload)[:5]:
            label = str(item.get("label") or "").strip()
            group = str(item.get("group") or "").strip()
            score_str = str(item.get("score") or "").strip()
            try:
                score_val = float(score_str) if score_str else 0.0
            except (TypeError, ValueError):
                score_val = 0.0
            if label:
                findings.append({"label": label, "group": group, "score": score_val})

        for entry in payload.get("quantum_synergy") or []:
            if isinstance(entry, dict):
                label = _quantum_labels(entry)
                score = str(entry.get("score") or "").strip()
                patterns.append(f"{escape(label)} ({escape(score or 'n/a')})")

        for entry in payload.get("remedy_synergies") or []:
            if isinstance(entry, dict):
                item1 = str(entry.get("item1") or "").strip()
                item2 = str(entry.get("item2") or "").strip()
                score = str(
                    entry.get("synergy_score") or entry.get("score") or ""
                ).strip()
                if item1 or item2:
                    remedies.append(
                        f"{escape(item1)} + {escape(item2)} ({escape(score or 'n/a')})"
                    )

    # Gruppiere Befunde nach Label (Cross-Profil) wie in Mustermann
    findings_aggregated: dict[str, dict] = {}
    for f in findings:
        lbl = f["label"]
        cur = findings_aggregated.setdefault(
            lbl.casefold(), {"label": lbl, "scores": [], "groups": set()}
        )
        cur["scores"].append(f["score"])
        if f["group"]:
            cur["groups"].add(f["group"])
    findings_summary = []
    for cur in findings_aggregated.values():
        scores = cur["scores"]
        avg = sum(scores) / len(scores) if scores else 0.0
        findings_summary.append(
            {
                "label": cur["label"],
                "avg_score": avg,
                "count": len(scores),
                "groups": sorted(cur["groups"]),
            }
        )
    findings_summary.sort(key=lambda x: (x["count"], x["avg_score"]), reverse=True)

    findings_rows = ""
    if findings_summary:
        row_parts = []
        for f in findings_summary[:12]:
            cls = (
                "finding high"
                if f["avg_score"] >= 7.0
                else "finding medium"
                if f["avg_score"] >= 5.0
                else "finding"
            )
            score_str = f"\u00d8 {f['avg_score']:.2f} | {f['count']}x"
            row_parts.append(
                f'<div class="{cls}"><span class="label">{escape(f["label"])}</span>'
                f'<span class="score">{score_str}</span></div>'
            )
        findings_rows = "".join(row_parts)
    if not findings_rows:
        findings_rows = '<p class="note">Keine priorisierten Resonanzwerte im Quellmaterial gefunden.</p>'

    pattern_items = "".join(
        f"<li>{item}</li>" for item in (patterns[:8] + remedies[:8])
    )
    if not pattern_items:
        pattern_items = (
            "<li>Keine Synergie- oder Remedy-Muster im Quellmaterial gefunden.</li>"
        )

    text_lines = [
        "Schluesselbefunde",
        *[
            f"{f['label']} (\u00d8 {f['avg_score']:.2f}, {f['count']}x)"
            for f in findings_summary[:12]
        ],
        "",
        "Erkannte Muster",
        *[line for line in (patterns[:8] + remedies[:8])],
    ]

    body = (
        '<div class="section">'
        "<h2>\U0001f3af Schluesselbefunde</h2>"
        f"{findings_rows}"
        "</div>"
        '<div class="section">'
        "<h2>\U0001f50d Erkannte Muster</h2>"
        f"<ul>{pattern_items}</ul>"
        "</div>"
    )
    return body, "\n".join(text_lines), findings_summary, profile_names


def _collect_top_findings(files: list[Path]) -> list[dict]:
    """Sammelt die Top-Resonanzen aus allen Scan-JSONs fuer die LLM-Analyse."""
    all_items: list[dict] = []
    for path in files:
        payload = _load_json(path)
        for item in _top_findings(payload)[:8]:
            label = str(item.get("label") or "").strip()
            score = item.get("score")
            group = str(item.get("group") or "").strip()
            if label:
                try:
                    score_f = float(score) if score is not None else 0.0
                except (TypeError, ValueError):
                    score_f = 0.0
                all_items.append(
                    {"label": label, "score": round(score_f, 2), "group": group}
                )
    return all_items


def _run_llm_analysis(files: list[Path], focus: str, client_name: str) -> str:
    """Fuehrt eine KI-gestuetzte Tiefenanalyse via Ollama durch.

    Returns den generierten Text oder einen Fallback-Text, wenn Ollama
    nicht verfuegbar ist.
    """
    top_items = _collect_top_findings(files)
    if not top_items:
        return "Keine Resonanzwerte fuer eine Tiefenanalyse verfuegbar."

    try:
        from core.llm.ollama_client import get_ollama_client

        client = get_ollama_client()
        if client is None or not getattr(client, "available", False):
            return _rule_based_analysis(top_items, focus, client_name)

        result = client.analyze_report_summary(top_items, focus=focus)
        if result and isinstance(result, str) and result.strip():
            return result.strip()
        return _rule_based_analysis(top_items, focus, client_name)
    except Exception as exc:
        return f"{_rule_based_analysis(top_items, focus, client_name)}\n\n(Hinweis: KI-Analyse nicht verfuegbar - {exc})"


def _rule_based_analysis(top_items: list[dict], focus: str, client_name: str) -> str:
    """Regelbasierte Fallback-Deutung, wenn Ollama nicht verfuegbar ist."""
    top3 = top_items[:3]
    labels = ", ".join(item["label"] for item in top3 if item.get("label"))
    focus_text = f" Thematischer Fokus: {focus}." if focus else ""
    return (
        f"fuer {client_name} wurden {len(top_items)} priorisierte Resonanzen ermittelt. "
        f"Die dominantesten Befunde sind: {labels}.{focus_text} "
        "Die Befunde sollten im therapeutischen Kontext und mit Verlaufskontrolle interpretiert werden. "
        "Bitte beachten Sie, dass dies keine medizinische Diagnose ersetzt."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a lightweight Morphic interpretation report."
    )
    parser.add_argument("last_name")
    parser.add_argument("first_name")
    parser.add_argument("--scans", default="1")
    parser.add_argument("--age", default="2")
    parser.add_argument("--focus", default="")
    parser.add_argument("--llm", action="store_true")
    parser.add_argument("--birth-date", default="")
    parser.add_argument("--birth-place", default="")
    parser.add_argument("--archive-root", default=str(DEFAULT_ARCHIVE_DIR))
    parser.add_argument("--output-root", default=str(DEFAULT_DEUTUNG_DIR))
    args = parser.parse_args()

    files = find_client_scan_files(
        args.archive_root,
        args.last_name,
        args.first_name,
        args.birth_date,
        args.birth_place,
    )
    requested_scans = int(args.scans) if str(args.scans).isdigit() else 1
    files = files[: max(requested_scans, 1)]

    base_dir = client_report_dir(
        args.output_root,
        args.last_name,
        args.first_name,
        "Deutung",
        args.birth_date,
        args.birth_place,
    )
    stamp = timestamp()
    scan_label = (
        f"top{args.scans}"
        if str(args.scans).isdigit() and int(args.scans) > 1
        else "single"
    )
    out_dir = _ensure_output_dir(base_dir / f"{stamp}_{scan_label}")
    scan_body, scan_text, findings_summary, profile_names = _scan_sections(files)
    client_name = f"{args.first_name} {args.last_name}".strip()
    llm_text = ""
    llm_label = "aktiviert" if args.llm else "nicht aktiviert"
    if args.llm:
        llm_text = _run_llm_analysis(files, args.focus, client_name)
        llm_label = (
            "aktiviert (KI-Text generiert)" if llm_text else "aktiviert (keine Antwort)"
        )
    if not llm_text:
        llm_text = (
            "Nicht aktiviert; regelbasierte Deutung aus den vorliegenden Scan-Daten."
        )

    # Profil-Tags wie in Mustermann-Referenz
    profile_tags_html = "".join(
        f'<span class="profile-tag">{escape(p)}</span>' for p in profile_names
    )

    # Empfehlungen ableiten (aus Top-Befunden)
    top_labels = [f["label"] for f in findings_summary[:3] if f.get("label")]
    recommendations_html = ""
    if top_labels:
        recommendations_html = (
            '<div class="recommendation">Organ-Unterstützung fokussieren: '
            + ", ".join(escape(l) for l in top_labels)
            + "</div>"
        )
    recommendations_html += '<div class="recommendation">Die angezeigten Remedies als Therapie-Optionen in Betracht ziehen</div>'

    # Zusammenfassung mit Hauptbefund
    main_finding = ""
    if findings_summary:
        f0 = findings_summary[0]
        main_finding = f" Hauptbefund: {f0['label']} (\u00d8 Score: {f0['avg_score']:.2f}, in {f0['count']} Profilen)."

    body = (
        '<div class="section">'
        "<h2>\U0001f4cb Zusammenfassung</h2>"
        f'<div class="summary">Analyse fuer {escape(args.first_name)} {escape(args.last_name)} basierend auf '
        f"{escape(len(files) or args.scans)} Profil-Scans."
        + (f" Fokus: {escape(args.focus)}." if args.focus else "")
        + escape(main_finding)
        + "</div>"
        + (
            f'<div class="profiles"><strong>Analysierte Profile:</strong>{profile_tags_html}</div>'
            if profile_tags_html
            else ""
        )
        + "</div>"
        '<div class="section">'
        "<h2>Fokus und Einordnung</h2>"
        f"<p>{escape(args.focus or 'Kein Fokus gesetzt.')}</p>"
        "</div>"
        f"{scan_body}"
        '<div class="section">'
        "<h2>\U0001f4a1 Empfehlungen</h2>"
        f"{recommendations_html}"
        "</div>"
        '<div class="section">'
        "<h2>\U0001f916 KI-gestuetzte Tiefenanalyse</h2>"
        f'<div class="summary" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%); border-left: 4px solid #764ba2;">'
        f"{escape(llm_text)}</div>"
        '<p style="font-size: 0.85em; opacity: 0.7; margin-top: 10px;">'
        "Generiert mit lokaler KI (Ollama) - basierend auf den Scan-Ergebnissen"
        "</p>"
        "</div>"
        '<div class="footer">'
        f"<p>Generiert am {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} | Morphic Engine Deutungs-System</p>"
        '<p style="margin-top: 10px; font-size: 0.85em;">'
        "\u26a0\ufe0f Diese Deutung dient als Orientierungshilfe und ersetzt keine medizinische Diagnose."
        "</p>"
        "</div>"
    )
    if not llm_text:
        llm_text = (
            "Nicht aktiviert; regelbasierte Deutung aus den vorliegenden Scan-Daten."
        )

    body = (
        '<div class="section">'
        "<h2>Zusammenfassung</h2>"
        f'<div class="summary">Die Deutung wurde fuer {escape(args.first_name)} {escape(args.last_name)} '
        f"auf Basis von {escape(len(files) or args.scans)} Scan(s) erstellt. "
        f"KI-Tiefenanalyse: {escape(llm_label)}.</div>"
        "</div>"
        '<div class="section">'
        "<h2>Fokus und Einordnung</h2>"
        f"<p>{escape(args.focus or 'Kein Fokus gesetzt.')}</p>"
        "</div>"
        f"{scan_body}"
        '<div class="section">'
        "<h2>Empfehlungen</h2>"
        "<p>Die Befunde sollten im therapeutischen Kontext, mit Verlaufskontrolle und ohne medizinische Diagnoseableitung interpretiert werden.</p>"
        "</div>"
        '<div class="section">'
        "<h2>KI-gestuetzte Tiefenanalyse</h2>"
        f"<p>{escape(llm_text)}</p>"
        '<p class="note">Generiert mit lokaler KI (Ollama) - basierend auf den Scan-Ergebnissen.</p>'
        "</div>"
    )
    title = f"Deutung - {args.first_name} {args.last_name}"
    html = render_legacy_html(
        title=title,
        subtitle="Morphic Engine Deutungsbericht",
        body_html=body,
        focus=args.focus,
        meta=(
            ("Scans", args.scans),
            ("Alter", args.age),
            ("LLM", "aktiv" if args.llm else "inaktiv"),
        ),
    )
    html_path = out_dir / f"deutung_{stamp}.html"
    html_path.write_text(
        html,
        encoding="utf-8",
    )
    pdf_path = out_dir / f"deutung_{stamp}.pdf"
    write_text_pdf(
        pdf_path,
        title,
        "\n\n".join(
            [
                f"Fokus: {args.focus or 'Kein Fokus gesetzt.'}",
                f"Quellscans: {len(files)}",
                scan_text,
                "Empfehlungen",
                "Die Befunde sollten im therapeutischen Kontext und mit Verlaufskontrolle interpretiert werden.",
                "KI-gestuetzte Tiefenanalyse",
                llm_text,
            ]
        ),
    )
    client = client_info(
        args.last_name, args.first_name, args.birth_date, args.birth_place
    )
    register_report_artifact(
        html_path,
        client,
        "interpretation_html",
        label="Deutung",
        focus=args.focus,
        config={
            "command": "interpretation_generator",
            "scans": args.scans,
            "source_files": len(files),
        },
    )
    register_report_artifact(
        pdf_path,
        client,
        "interpretation_pdf",
        label="Deutung PDF",
        focus=args.focus,
        config={
            "command": "interpretation_generator",
            "scans": args.scans,
            "source_files": len(files),
        },
    )
    print(f"Deutungsbericht written: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
