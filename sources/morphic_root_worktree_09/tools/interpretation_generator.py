from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from core.llm import get_ollama_client
from tools.reporting_common import (
    client_info,
    client_report_dir,
    escape,
    find_client_scan_files,
    register_report_artifact,
    render_legacy_html,
    timestamp,
)
from tools.pdf_exporter import html_to_pdf
from core.compliance.operator_context import resolve_operator_context


DEFAULT_ARCHIVE_DIR = Path(r"C:\Benutzer_Archive_Start")
DEFAULT_DEUTUNG_DIR = Path(r"C:\Benutzer_Deutung_Start")
PROJECT_FALLBACK_DIR = Path("Benutzer_Archive") / "Deutung_Reports"


@dataclass(frozen=True)
class InterpretationOutcome:
    text: str
    mode: Literal["disabled", "ollama", "rule_fallback"]
    model: str = ""
    reason: str = ""


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


def _build_interpretation_outcome(
    files: list[Path],
    focus: str,
    client_name: str,
    *,
    local_ai_enabled: bool,
) -> InterpretationOutcome:
    top_items = _collect_top_findings(files)
    fallback_text = (
        _rule_based_analysis(top_items, focus, client_name)
        if top_items
        else "Keine Resonanzwerte fuer eine Deutung verfuegbar."
    )
    if not local_ai_enabled:
        return InterpretationOutcome(text=fallback_text, mode="disabled")
    if not top_items:
        return InterpretationOutcome(
            text=fallback_text,
            mode="rule_fallback",
            reason="no_findings",
        )

    try:
        client = get_ollama_client()
        if client is None:
            return InterpretationOutcome(
                text=fallback_text,
                mode="rule_fallback",
                reason="unavailable_or_model_missing",
            )
        if not client.available:
            return InterpretationOutcome(
                text=fallback_text,
                mode="rule_fallback",
                reason=getattr(client, "unavailability_reason", "")
                or "unavailable_or_model_missing",
            )
        result = client.analyze_report_summary(top_items, focus=focus)
        if isinstance(result, str) and result.strip():
            return InterpretationOutcome(
                text=result.strip(),
                mode="ollama",
                model=client.model,
            )
        return InterpretationOutcome(
            text=fallback_text,
            mode="rule_fallback",
            reason="empty_response",
        )
    except Exception:
        return InterpretationOutcome(
            text=fallback_text,
            mode="rule_fallback",
            reason="client_error",
        )


def _rule_based_analysis(top_items: list[dict], focus: str, client_name: str) -> str:
    """Regelbasierte Fallback-Deutung, wenn Ollama nicht verfuegbar ist."""
    top = top_items[:8]
    labels = [item["label"] for item in top if item.get("label")]
    groups = sorted({item.get("group", "") for item in top if item.get("group")})
    focus_text = f"Thematischer Fokus: {focus}. " if focus else ""
    labels_text = ", ".join(labels) if labels else "keine dominante Resonanz"
    groups_text = ", ".join(groups) if groups else "verschiedene Gruppen"
    top3 = top[:3]
    top3_text = "; ".join(
        f"{item.get('label', '')} (Score {item.get('score', 0):.2f})"
        for item in top3
        if item.get("label")
    )

    return (
        f"1. Die Hauptbelastungen scheinen sich um eine Kombination aus {groups_text} zu drehen. "
        f"Die Top-Resonanzen sind: {top3_text}. {focus_text}"
        "Diese Hauptthemen stehen im Zusammenhang mit den energetisch staerksten Signalen.\n\n"
        f"2. Die Score-Analyse der Top-Resonanzen deutet auf einen Schwerpunkt im Bereich {groups_text} hin. "
        f"Insgesamt wurden {len(top_items)} priorisierte Items ermittelt. "
        "Die hauefigsten Befunde sind: "
        f"{labels_text}.\n\n"
        "3. Fuer die Therapie empfehle ich zunaechst, den Fokus auf die dominanten Befunde zu legen "
        "und deren Gruppen-Zusammenhaenge in der Verlaufskontrolle zu beobachten. "
        "Falls Symptome vorliegen, sollte eine geeignete Fachperson konsultiert werden.\n\n"
        "4. Diese regelbasierte Deutung ist keine KI-gestuetzte Tiefenanalyse. "
        "Die tieferliegenden Ursachen koennten historisch bedingt sein: "
        "chronische Belastungen, Naehrstoff-Bilanzen oder Umweltfaktoren, die sich in den "
        "Resonanzen widerspiegeln. Eine Befundtiefe und Verlaufskontrolle hilft, diese zu klaeren.\n\n"
        "Bitte beachten Sie, dass dies keine medizinische Diagnose darstellt und professionelle "
        "medizinische Hilfe empfohlen wird, insbesondere wenn Symptome vorliegen oder sich im Laufe der Zeit verschlechtern."
    )


def _outcome_status(outcome: InterpretationOutcome) -> str:
    if outcome.mode == "ollama":
        return f"Lokales Ollama verwendet ({outcome.model})"
    if outcome.mode == "rule_fallback":
        reason_map = {
            "unavailable_or_model_missing": "Ollama nicht verfuegbar oder Modell fehlt",
            "server_unreachable": "Ollama-Server nicht erreichbar",
            "model_missing": "Ollama-Modell nicht installiert",
            "no_models": "Keine Ollama-Modelle installiert",
            "server_error": "Ollama-Server antwortet nicht korrekt",
            "unavailable": "Ollama nicht verfuegbar",
            "empty_response": "Ollama-Antwort war leer",
            "client_error": "Ollama-Client-Fehler",
            "no_findings": "Keine Resonanzen fuer Deutung",
        }
        reason_text = reason_map.get(
            outcome.reason, outcome.reason or "unbekannter Grund"
        )
        return f"Opt-in erteilt; regelbasierter Fallback ({reason_text})"
    return "Lokale KI deaktiviert; regelbasierte Deutung"


def _render_interpretation_section(outcome: InterpretationOutcome) -> str:
    note = ""
    if outcome.mode == "ollama":
        note = (
            '<p class="note">Generiert mit lokaler KI (Ollama), '
            f'Modell {escape(outcome.model)}.</p>'
        )
    return (
        '<div class="section">'
        "<h2>Deutung</h2>"
        f"<p>{escape(outcome.text)}</p>"
        f'<p class="note">Quelle: {escape(_outcome_status(outcome))}.</p>'
        f"{note}"
        "</div>"
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

    output_tenant_id = (
        resolve_operator_context().tenant_id
        if args.output_root == str(DEFAULT_DEUTUNG_DIR)
        else ""
    )
    base_dir = client_report_dir(
        args.output_root,
        args.last_name,
        args.first_name,
        "Deutung",
        args.birth_date,
        args.birth_place,
        tenant_id=output_tenant_id,
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
    outcome = _build_interpretation_outcome(
        files,
        args.focus,
        client_name,
        local_ai_enabled=args.llm,
    )

    body = (
        '<div class="section">'
        "<h2>Zusammenfassung</h2>"
        f'<div class="summary">Die Deutung wurde fuer {escape(args.first_name)} {escape(args.last_name)} '
        f"auf Basis von {escape(len(files) or args.scans)} Scan(s) erstellt. "
        f"Deutungsquelle: {escape(_outcome_status(outcome))}.</div>"
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
        f"{_render_interpretation_section(outcome)}"
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
            ("Lokale KI", _outcome_status(outcome)),
        ),
    )
    html_path = out_dir / f"deutung_{stamp}.html"
    html_path.write_text(
        html,
        encoding="utf-8",
    )
    pdf_path = out_dir / f"deutung_{stamp}.pdf"
    html_to_pdf(html_path, title)
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
            "local_ai_mode": outcome.mode,
            "local_ai_model": outcome.model,
            "local_ai_reason": outcome.reason,
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
            "local_ai_mode": outcome.mode,
            "local_ai_model": outcome.model,
            "local_ai_reason": outcome.reason,
        },
    )
    print(f"Deutungsbericht written: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
