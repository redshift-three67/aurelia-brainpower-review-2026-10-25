"""Field Test Command"""

from pathlib import Path
from typing import Dict, List, Optional, Iterable
import os
import numpy as np
import typer
import time
import json
import re
from datetime import datetime

from services.subgroup_service import SubgroupService
from core.profiles.profile import ClientProfile, RateEncoder
from services.analysis_service import AnalysisService
from services.nls_service import NlsService
from providers.hardware.entropy_sources import select_entropy_source
from core.hardware import get_full_system_report
from apps.cli.profiles.registry import get_groups_for_profile, validate_profile_groups
from core.subgroups.procedural_groups import list_groups
from core.nls3d_points_new import NLS3D_POINTS, map_item_to_point
from core.morphic_field import (
    MorphicFieldConfig,
    calculate_morphic_field,
    generate_default_quantum_states,
)

field_app = typer.Typer()


_VISIBLE_TEXT_REPLACEMENTS = (
    ("–", "-"),
    ("—", "-"),
    ("â†’", "->"),
    ("âœ“", "OK"),
    ("âœ—", "WARN"),
    ("âš ", "WARN"),
    ("âš¡", "LOW"),
    ("â„¹", "INFO"),
    ("•", "-"),
    ("âˆš", "sqrt"),
    ("Ä", "Ae"),
    ("Ö", "Oe"),
    ("Ü", "Ue"),
    ("ä", "ae"),
    ("ö", "oe"),
    ("ü", "ue"),
    ("ß", "ss"),
    ("Ã©", "e"),
    ("Ã¨", "e"),
    ("Ã¡", "a"),
    ("Ã ", "a"),
    ("Ã³", "o"),
    ("Ã²", "o"),
    ("Ã­", "i"),
    ("Ã¬", "i"),
    ("Ï†", "phi"),
)


def _sanitize_visible_text(value: str) -> str:
    cleaned = value
    for bad, replacement in _VISIBLE_TEXT_REPLACEMENTS:
        cleaned = cleaned.replace(bad, replacement)
    cleaned = re.sub(r"ðŸ\S*", "", cleaned)
    return cleaned.replace("\ufffd", "")


def _echo(message: object = None, *args: object, **kwargs: object) -> None:
    if isinstance(message, str):
        message = _sanitize_visible_text(message)
    typer.echo(message, *args, **kwargs)


@field_app.command()
def field_test(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(
        ..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09031999"
    ),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    seed: str = typer.Option(
        "field-seed", "--seed", help="Seed für prozedurale Feldtest-Kandidaten"
    ),
    p_emotion: float = typer.Option(
        0.5, "--p-emotion", min=0.0, max=1.0, help="Einstufung emotionale Ebene [0,1]"
    ),
    p_physisch: float = typer.Option(
        0.5, "--p-physisch", min=0.0, max=1.0, help="Einstufung physische Ebene [0,1]"
    ),
    p_mental: float = typer.Option(
        0.5, "--p-mental", min=0.0, max=1.0, help="Einstufung mentale Ebene [0,1]"
    ),
    p_astral: float = typer.Option(
        0.5, "--p-astral", min=0.0, max=1.0, help="Einstufung astrale Ebene [0,1]"
    ),
    hardware_profile: str = typer.Option(
        "legacy",
        "--hardware-profile",
        help="Hardware-Profil: z.B. 'legacy' (Standard), 'windows' oder 'debian_server'",
    ),
    top_k: int = typer.Option(
        8, "--top-k", min=1, help="Anzahl der Top-Resonanzen im Bericht"
    ),
    focus: str = typer.Option(
        "",
        "--focus",
        help="Optionaler Fokus / Symptom zur Gewichtung der Ergebnisse",
    ),
    export: Path | None = typer.Option(
        None,
        "--export",
        help="Exportiert Ergebnisse des Feldtests als JSON-Datei",
    ),
) -> None:
    """Führt einen personalisierten Feldtest (Emotion/Physisch/Mental/Astral) durch."""

    from apps.cli.commands.scan import _clamp
    from apps.cli.commands.helpers import (
        _atomic_write_text,
        _compute_focus_multiplier_for_item,
        _is_remedy_group,
        _rates_to_level_info,
        _render_basic_html,
        _render_multiplex_txt,
        _resolve_export_paths,
    )
    from tools.reporting_common import register_report_artifact
    from tools.pdf_exporter import html_to_text
    from tools.simple_pdf import write_text_pdf

    groups = ["emotion", "physisch", "mental", "astral"]
    subgroup_svc = SubgroupService()
    # Für den Feldtest mehr Kandidaten erzeugen, damit pro Ebene genügend
    # unterschiedliche Items zur Verfügung stehen.
    items = subgroup_svc.generate_fullbody_candidates(groups, seed, k_total=128)
    if not items:
        _echo("Keine Feldtest-Kandidaten erzeugt.")
        raise typer.Exit(code=1)

    personal_profile = {
        "emotion": _clamp(p_emotion),
        "physisch": _clamp(p_physisch),
        "mental": _clamp(p_mental),
        "astral": _clamp(p_astral),
    }

    _profile = (hardware_profile or "legacy").strip().lower()

    # Profil-spezifische Auswahl der Entropiequelle.
    # - "legacy": HID bevorzugt, 2s Messdauer
    # - "windows": HID bevorzugt, leicht verlängerte Messdauer (3s)
    # - "debian_server": QRNG/GPU bevorzugt, HID ignoriert
    # Bei Ausfällen wird konservativ auf cpu_timer zurückgefallen.
    if _profile == "debian_server":
        duration = 2.0
        src = select_entropy_source(preferred=["qrng", "gpu", "network", "cpu_timer"])
        h_level = _clamp(src.sample_h_level(duration_s=duration))
        if src.name() in ("qrng", "gpu", "network") and h_level <= 0.0:
            fallback_src = select_entropy_source(preferred=["cpu_timer"])
            fallback_h = _clamp(fallback_src.sample_h_level(duration_s=duration))
            if fallback_h > h_level:
                src = fallback_src
                h_level = fallback_h
    else:
        duration = 3.0 if _profile == "windows" else 2.0
        src = select_entropy_source(preferred=["hid_sensor", "cpu_timer"])
        h_level = _clamp(src.sample_h_level(duration_s=duration))
        if src.name() == "hid_sensor" and h_level <= 0.0:
            fallback_src = select_entropy_source(preferred=["cpu_timer"])
            fallback_h = _clamp(fallback_src.sample_h_level(duration_s=duration))
            if fallback_h > h_level:
                src = fallback_src
                h_level = fallback_h

    profile = ClientProfile(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        image_signature=None,
        personal_profile=personal_profile,
    )

    analysis = AnalysisService(rate_database={}, h_level=h_level)
    client_rates = analysis.encode_profile(profile)
    client_entropy = analysis.resonator.holographic_entropy(client_rates)
    m_field = analysis.resonator.calculate_m_field(client_rates)
    heim_sig = analysis.resonator.heim_signature(client_rates)

    encoder = RateEncoder()
    client_personal_vector = encoder.personal_profile_to_vector(personal_profile)

    def resonance_fn(a: np.ndarray, b: np.ndarray) -> float:
        return float(analysis.resonator.resonance_score(a, b))

    nls_service = NlsService(items)
    scores = nls_service.compute_scores_v2(
        client_rates,
        client_entropy,
        resonance_fn,
        client_personal_vector=client_personal_vector,
    )

    # Optional: Fokus kann die Scores sanft gewichten, wenn aktiviert und gesetzt.
    # ERWEITERT 01.12.2025: Jetzt mit Copen-Rate-Resonanz
    if (focus or "").strip():
        # Lookup-Tabellen für Gruppe und Copen-Rate erstellen
        label_to_group: Dict[str, str] = {}
        label_to_copen_rate: Dict[str, float] = {}
        for it in items:
            lbl = str(it.get("label", "") or "").strip()
            if not lbl or lbl in label_to_group:
                continue
            grp = str(it.get("group", "") or "").strip()
            label_to_group[lbl] = grp
            # Copen-Rate aus Item extrahieren (falls vorhanden)
            try:
                copen_rate = float(it.get("copen_rate", 0.0) or 0.0)
            except (TypeError, ValueError):
                copen_rate = 0.0
            label_to_copen_rate[lbl] = copen_rate

        scores_with_focus: List[Dict[str, object]] = []
        for entry in scores:
            lbl = str(entry.get("label", "") or "").strip()
            grp = label_to_group.get(lbl, "")
            item_copen_rate = label_to_copen_rate.get(lbl, 0.0)
            # Erweiterte Fokus-Gewichtung mit Copen-Rate-Resonanz
            m_focus = _compute_focus_multiplier_for_item(
                focus, grp, lbl, item_copen_rate
            )
            new_entry = dict(entry)
            new_entry["focus_multiplier"] = float(m_focus)
            new_entry["score"] = float(new_entry.get("score", 0.0) or 0.0) * m_focus
            scores_with_focus.append(new_entry)

        scores = scores_with_focus

    _echo("Morphic Engine V1 – Feldtest (Emotion/Physisch/Mental/Astral)")
    _echo(f"Klient: {first_name} {name}")
    _echo(
        "Personalprofil: "
        f"Emotion={personal_profile['emotion']:.2f}, "
        f"Physisch={personal_profile['physisch']:.2f}, "
        f"Mental={personal_profile['mental']:.2f}, "
        f"Astral={personal_profile['astral']:.2f}"
    )
    _echo(f"Morphic field: {m_field:.4f}")
    _echo(f"h_level (Hardware): {h_level:.3f} [{src.name()} / profile={_profile}]")
    _echo(f"Holographic entropy: {client_entropy:.4f}")
    _echo("Heim signature:")
    _echo("  " + ", ".join(f"{x:.3f}" for x in heim_sig))

    _echo("")
    _echo("Top Items (NLS v2, personalisiert):")
    # Doppelte Labels vermeiden: über die sortierten Scores iterieren und
    # jedes Label höchstens einmal berücksichtigen.
    seen_labels = set()
    top_scores = []
    for entry in scores:
        label = entry["label"]
        if label in seen_labels:
            continue
        seen_labels.add(label)
        top_scores.append(entry)
        if len(top_scores) >= top_k:
            break
    for entry in top_scores:
        label = entry["label"]
        score = entry["score"]
        rel = entry["reliability"]
        palign = entry.get("personal_alignment", 1.0)
        _echo(
            f"  - {label}: score={score:.4f}, rel={rel:.2f}, personal_align={palign:.2f}"
        )

    # Build label -> meta lookup from generated items
    meta_by_label: Dict[str, Dict[str, object]] = {}
    for it in items:
        lab = str(it.get("label", ""))
        if not lab or lab in meta_by_label:
            continue
        meta_by_label[lab] = it

    # Enrich NLS scores with group/potency/rates and 13-Ebenen-Resonanz
    enriched: List[Dict[str, object]] = []
    for e in scores:
        lab = str(e.get("label", ""))
        if not lab:
            continue
        m = meta_by_label.get(lab, {})
        group = str(m.get("group", "") or "")
        potency = m.get("potency")
        rates_vals = m.get("rates", [])
        try:
            rates_list = [float(x) for x in rates_vals] if rates_vals else []
        except Exception:
            rates_list = []
        s_res = float(e.get("resonance", 0.0) or 0.0)
        s_ent = float(e.get("entropy_alignment", 0.0) or 0.0)
        dv_val = int(max(1, min(6, 1 + round(5.0 * (1.0 - s_ent)))))

        lvl_id, lvl_val, lvl_text, copen_rate = _rates_to_level_info(rates_list, lab)

        enriched.append(
            {
                "label": lab,
                "score": float(e.get("score", 0.0) or 0.0),
                "resonance": s_res,
                "entropy_alignment": s_ent,
                "z_entropy": float(e.get("z_entropy", 0.0) or 0.0),
                "reliability": float(e.get("reliability", 1.0) or 1.0),
                "personal_alignment": float(e.get("personal_alignment", 1.0) or 1.0),
                "group": group,
                "potency": str(potency) if potency is not None else "-",
                "rates": rates_list,
                "dv": int(dv_val),
                "level": lvl_text,
                "level_id": int(lvl_id),
                "level_value": float(lvl_val),
                "copen_rate": float(copen_rate),
            }
        )

    # Map groups to legacy-style auto-* section names
    def _category_for_group(g: str) -> str:
        g = (g or "").strip().lower()
        mapping = {
            "bakterien": "auto-bakterien",
            "bakterien_fein": "auto-bakterien",
            "viren": "auto-viren",
            "viren_fein": "auto-viren",
            "parasiten": "auto-parasiten",
            "parasiten_fein": "auto-parasiten",
            "pilze": "auto-pilze",
            "pilze_fein": "auto-pilze",
            "schwermetalle": "auto-schwermetalle",
            "schwermetalle_tox": "auto-schwermetalle",
            "detox": "auto-detox",
            "mikrozirkulation": "auto-mikrozirkulation",
            "mitochondrien": "auto-mitochondrien",
            "entzuendung": "auto-entzündung",
            "allergene": "auto-allergene",
            "mikronaehrstoffe": "auto-mikronährstoffe",
            "wirbelsaeule": "auto-wirbelsäule",
            "odontone": "auto-odontone",
            "kreislauf": "auto-kreislauf",
            "chakren": "auto-chakren",
            "chakren_erweitert": "auto-chakren",
            "chakren_full": "auto-chakren",
            "nebenchakren": "auto-chakren",
            "meridiane": "auto-meridiane",
            "tcm_punkte": "auto-meridiane",
            "tcm_punkte_extended": "auto-meridiane",
            "tcm_full": "auto-meridiane",
            "endokrin": "auto-endokrin",
            # Remedies / Rezepturen – zusammengefasste Rubriken
            "homoeopathie_klassisch": "auto-homöopathie",
            "homoeopathie_klassisch_potenzen": "auto-homöopathie",
            "tcm_rezepturen": "auto-tcm-rezepturen",
            "tcm_rezepturen_potenzen": "auto-tcm-rezepturen",
            "spagyrik": "auto-spagyrik",
        }
        return mapping.get(g, f"auto-{g}" if g else "auto-sonstige")

    # Bucket entries per section
    sections_dict: Dict[str, Dict[str, object]] = {}
    for rec in enriched:
        cat = _category_for_group(str(rec.get("group", "")))
        sec = sections_dict.setdefault(cat, {"name": cat, "entries": []})
        sec["entries"].append(rec)

    # Compute per-section intensity and priority; sort entries by score desc
    def _priority(rel: float) -> str:
        if rel >= 0.66:
            return "hoch"
        if rel >= 0.33:
            return "mittel"
        return "niedrig"

    for sec in sections_dict.values():
        entries = sec["entries"]  # type: ignore[index]
        try:
            max_score = max(float(e.get("score", 0.0) or 0.0) for e in entries)
        except ValueError:
            max_score = 0.0
        for e in entries:
            s_val = float(e.get("score", 0.0) or 0.0)
            rel = s_val / max_score if max_score > 0.0 else 0.0
            e["intensity"] = rel
            e["priority"] = _priority(rel)
        entries.sort(key=lambda x: float(x.get("score", 0.0) or 0.0), reverse=True)

    max_per_section = 21
    for sec in sections_dict.values():
        entries = sec["entries"]  # type: ignore[index]
        highs = [e for e in entries if str(e.get("priority", "")) == "hoch"]
        mids = [e for e in entries if str(e.get("priority", "")) == "mittel"]
        if len(mids) > max_per_section:
            new_entries = highs + mids
        else:
            total_hm = len(highs) + len(mids)
            if total_hm <= max_per_section:
                new_entries = highs + mids
            else:
                slots_for_mid = max_per_section - len(highs)
                if slots_for_mid < 0:
                    slots_for_mid = 0
                new_entries = highs + mids[:slots_for_mid]
        sec["entries"] = new_entries

    sections = list(sections_dict.values())

    # Aggregates per section (Aus Subgruppen, Aus NLS, Kombiniert)
    def _rate_pair(lst: List[float]) -> List[float]:
        try:
            if not lst:
                return [0.0, 0.0]
            if len(lst) == 1:
                v = float(lst[0])
                return [v, v]
            return [float(lst[0]), float(lst[1])]
        except Exception:
            return [0.0, 0.0]

    aggregates_list: List[Dict[str, object]] = []
    for cat_name, sec in sections_dict.items():
        entries = sec["entries"]  # type: ignore[index]
        if not entries:
            continue
        vals = [_rate_pair(e.get("rates") or []) for e in entries]  # type: ignore[arg-type]
        n = len(vals)
        if n > 0:
            avg_sub = [sum(v[0] for v in vals) / n, sum(v[1] for v in vals) / n]
        else:
            avg_sub = [0.0, 0.0]
        weights = [float(e.get("score", 0.0) or 0.0) for e in entries]
        ws = sum(weights)
        if ws > 0.0:
            sum0 = 0.0
            sum1 = 0.0
            for e in entries:
                w = float(e.get("score", 0.0) or 0.0)
                r0, r1 = _rate_pair(e.get("rates") or [])  # type: ignore[arg-type]
                sum0 += w * r0
                sum1 += w * r1
            avg_nls = [sum0 / ws, sum1 / ws]
        else:
            avg_nls = avg_sub
        combined = [(avg_sub[0] + avg_nls[0]) / 2.0, (avg_sub[1] + avg_nls[1]) / 2.0]
        aggregates_list.append(
            {
                "name": cat_name,
                "subgroups_rates": [float(avg_sub[0]), float(avg_sub[1])],
                "nls_rates": [float(avg_nls[0]), float(avg_nls[1])],
                "combined_rates": [float(combined[0]), float(combined[1])],
            }
        )

    # Condensed therapy top across remedies
    therapy_cats = {"auto-homöopathie", "auto-tcm-rezepturen", "auto-spagyrik"}
    therapy_pool: List[Dict[str, object]] = []

    # Historische Haupt-Rubriken weiter berücksichtigen
    for cat in therapy_cats:
        sec = sections_dict.get(cat)
        if not sec:
            continue
        therapy_pool.extend(sec["entries"])  # type: ignore[index]

    # Zusätzlich alle Einträge aus Sektionen aufnehmen, deren Gruppen echte Remedies sind
    for sec in sections_dict.values():
        entries = sec.get("entries") or []  # type: ignore[assignment]
        for e in entries:
            grp_val = str(e.get("group", "") or "").strip().lower()
            if grp_val and _is_remedy_group(grp_val):
                therapy_pool.append(e)
    therapy_pool_sorted = sorted(
        therapy_pool, key=lambda x: float(x.get("score", 0.0) or 0.0), reverse=True
    )
    therapy_top: List[Dict[str, object]] = []
    seen_lbl: set[str] = set()
    for e in therapy_pool_sorted:
        lbl = str(e.get("label", ""))
        if not lbl or lbl in seen_lbl:
            continue
        seen_lbl.add(lbl)
        therapy_top.append(
            {
                "label": lbl,
                "score": float(e.get("score", 0.0) or 0.0),
                "potency": str(e.get("potency", "-") or "-"),
                "group": str(e.get("group", "") or ""),
                "dv": int(e.get("dv", 0) or 0),
                "rates": e.get("rates", []),
                "priority": str(e.get("priority", "")),
            }
        )
        if len(therapy_top) >= 24:
            break

    # Build export data
    client_info: Dict[str, str] = {
        "name": name,
        "first_name": first_name,
        "birth_date": birth_date,
        "birth_place": birth_place,
    }
    export_data: Dict[str, object] = {
        "schema": "morphic_field_test",
        "schema_version": 1,
        "command": "field_test",
        "hardware_profile": _profile,
        "hardware_source": src.name(),
        "h_level": float(h_level),
        "client": client_info,
        "focus": focus,
        "personal_profile": personal_profile,
        "metrics": {
            "morphic_field": float(m_field),
            "holographic_entropy": float(client_entropy),
            "heim_signature": [float(x) for x in heim_sig],
        },
        "sections": sections,
        "aggregates": aggregates_list,
        "therapy_top": therapy_top,
    }

    if export is not None:
        try:
            json_path, html_path = _resolve_export_paths(
                export, client_info, "field_test"
            )
            _echo(f"Export-Basis (absolut): {json_path.parent}")
            txt_path = html_path.with_suffix(".txt")
            _echo(f"Export-Pfade: JSON -> {json_path}")
            _echo(f"Export-Pfade: HTML -> {html_path}")
            _echo(f"Export-Pfade: TXT  -> {txt_path}")
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            _atomic_write_text(json_path, json_str)
            html = _sanitize_visible_text(_render_basic_html(export_data))
            _atomic_write_text(html_path, html)
            pdf_path = html_path.with_suffix(".pdf")
            write_text_pdf(pdf_path, html_path.stem, html_to_text(html_path))
            txt = _sanitize_visible_text(_render_multiplex_txt(export_data))
            _atomic_write_text(txt_path, txt)
            try:
                sections_hm = export_data.get("sections") or []
                high_mid: List[Dict[str, object]] = []
                for sec in sections_hm:
                    entries = sec.get("entries") or []  # type: ignore[assignment]
                    for e in entries:
                        prio = str(e.get("priority", ""))
                        if prio not in ("hoch", "mittel"):
                            continue
                        try:
                            sc = float(e.get("score", 0.0) or 0.0)
                        except Exception:
                            sc = 0.0
                        label_hm = str(e.get("label", ""))
                        if not label_hm:
                            continue
                        try:
                            cr = float(e.get("copen_rate", 0.0) or 0.0)
                        except Exception:
                            cr = 0.0
                        high_mid.append(
                            {
                                "label": label_hm,
                                "copen_rate": cr,
                                "score": sc,
                                "priority": prio,
                            }
                        )

                if high_mid:
                    high_mid_sorted = sorted(
                        high_mid,
                        key=lambda r: float(r.get("score", 0.0) or 0.0),
                        reverse=True,
                    )
                    labels_lines: List[str] = []
                    copen_lines: List[str] = []
                    for rec in high_mid_sorted:
                        labels_lines.append(str(rec.get("label", "")))
                        try:
                            cr_val = float(rec.get("copen_rate", 0.0) or 0.0)
                            if float(cr_val).is_integer():
                                copen_lines.append(f"{int(cr_val)}")
                            else:
                                copen_lines.append(f"{cr_val:.4f}")
                        except Exception:
                            copen_lines.append("0")

                    base_stem = txt_path.with_suffix("").name
                    labels_path = txt_path.with_name(
                        base_stem + "_labels_hoch_mittel.txt"
                    )
                    rates_path = txt_path.with_name(
                        base_stem + "_copen_hoch_mittel.txt"
                    )
                    if labels_lines:
                        _atomic_write_text(labels_path, "\n".join(labels_lines))
                    if copen_lines:
                        _atomic_write_text(rates_path, "\n".join(copen_lines))
            except Exception:
                pass
            ok_json = json_path.exists() and json_path.stat().st_size > 0
            ok_html = html_path.exists() and html_path.stat().st_size > 0
            ok_pdf = pdf_path.exists() and pdf_path.stat().st_size > 0
            ok_txt = txt_path.exists() and txt_path.stat().st_size > 0
            _echo(f"JSON geschrieben: {'OK' if ok_json else 'FEHLER'} -> {json_path}")
            _echo(f"HTML geschrieben: {'OK' if ok_html else 'FEHLER'} -> {html_path}")
            _echo(f"PDF geschrieben:  {'OK' if ok_pdf else 'FEHLER'} -> {pdf_path}")
            _echo(f"TXT geschrieben:  {'OK' if ok_txt else 'FEHLER'} -> {txt_path}")
            if ok_json:
                _echo(f"Export gespeichert: {json_path}")
            if ok_html:
                _echo(f"HTML-Report gespeichert: {html_path}")
            if ok_pdf:
                _echo(f"PDF-Report gespeichert: {pdf_path}")
            if ok_txt:
                _echo(f"TXT-Report gespeichert: {txt_path}")
            if ok_json:
                register_report_artifact(
                    json_path,
                    client_info,
                    "field_test_json",
                    label="Feldtest JSON",
                    focus=focus,
                    config={"command": "field_test"},
                )
            if ok_html:
                register_report_artifact(
                    html_path,
                    client_info,
                    "field_test_html",
                    label="Feldtest HTML",
                    focus=focus,
                    config={"command": "field_test"},
                )
            if ok_pdf:
                register_report_artifact(
                    pdf_path,
                    client_info,
                    "field_test_pdf",
                    label="Feldtest PDF",
                    focus=focus,
                    config={"command": "field_test"},
                )
            if ok_txt:
                register_report_artifact(
                    txt_path,
                    client_info,
                    "field_test_txt",
                    label="Feldtest TXT",
                    focus=focus,
                    config={"command": "field_test"},
                )
        except Exception as exc:
            _echo(f"Export fehlgeschlagen: {exc}")
    fam_best: Dict[str, Dict[str, float | str]] = {}
    fam_top: Dict[str, List[Dict[str, float | str]]] = {}
    fam_seen: Dict[str, set[str]] = {}
    for entry in scores:
        label = entry["label"]
        score = entry["score"]
        fam = None
        if label.startswith("Emotion ") or label.startswith("Emotion –"):
            fam = "Emotion"
        elif label.startswith("Physisch ") or label.startswith("Physisch –"):
            fam = "Physisch"
        elif label.startswith("Mental ") or label.startswith("Mental –"):
            fam = "Mental"
        elif label.startswith("Astral ") or label.startswith("Astral –"):
            fam = "Astral"
        if fam is None:
            continue
        best = fam_best.get(fam)
        if best is None or float(score) > float(best["score"]):
            fam_best[fam] = {"label": label, "score": float(score)}
        seen = fam_seen.setdefault(fam, set())
        if label in seen:
            continue
        seen.add(label)
        lst = fam_top.setdefault(fam, [])
        if len(lst) < 3:
            lst.append({"label": label, "score": float(score)})

    _echo("")
    _echo("Beste Resonanzen je Ebene (Top 3):")
    for fam in ("Emotion", "Physisch", "Mental", "Astral"):
        entries = fam_top.get(fam, [])
        if not entries:
            continue
        _echo(f"  {fam}:")
        for e in entries:
            _echo(f"    - {e['label']} ({e['score']:.4f})")

    # (Kein zweiter Exportblock hier; der vorherige Block schreibt JSON+HTML bereits korrekt.)


@field_app.command("multiplex-scan")
def multiplex_scan(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(
        ..., "--birth-date", "-d", help="Geburtsdatum, z.B. 09041966"
    ),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    profile: str = typer.Option(
        "pathogen",
        "--profile",
        "-P",
        help="Multiplex-Profil: 'pathogen', 'toxin', 'regulation', 'full' (Alias: 'therapy')",
    ),
    seed: str = typer.Option(
        "multiplex-seed", "--seed", help="Seed für prozedurale Multiplex-Kandidaten"
    ),
    p_emotion: float = typer.Option(
        0.5, "--p-emotion", min=0.0, max=1.0, help="Einstufung emotionale Ebene [0,1]"
    ),
    p_physisch: float = typer.Option(
        0.5, "--p-physisch", min=0.0, max=1.0, help="Einstufung physische Ebene [0,1]"
    ),
    p_mental: float = typer.Option(
        0.5, "--p-mental", min=0.0, max=1.0, help="Einstufung mentale Ebene [0,1]"
    ),
    p_astral: float = typer.Option(
        0.5, "--p-astral", min=0.0, max=1.0, help="Einstufung astrale Ebene [0,1]"
    ),
    hardware_profile: str = typer.Option(
        "windows",
        "--hardware-profile",
        help="Hardware-Profil: z.B. 'legacy', 'windows' oder 'debian_server'",
    ),
    focus: str = typer.Option(
        "",
        "--focus",
        help="Optionaler Fokus / Symptom (z.B. 'Narbenstörung')",
    ),
    k_total: int = typer.Option(
        512, "--k-total", min=16, help="Anzahl der Multiplex-Kandidaten"
    ),
    top_k: int = typer.Option(
        32, "--top-k", min=1, help="Anzahl der Top-Resonanzen im Bericht"
    ),
    export: Path | None = typer.Option(
        None,
        "--export",
        help="Exportiert Ergebnisse des Multiplex-Scans als JSON+HTML",
    ),
    synergy: bool = typer.Option(
        True,
        "--synergy/--no-synergy",
        help="Aktiviert Quantum-Synergy Analyse für synergistische Kombinationen",
    ),
    synergy_combos: int = typer.Option(
        4,
        "--synergy-combos",
        min=2,
        max=5,
        help="Anzahl Items pro synergistischer Kombination (2-5)",
    ),
    synergy_threshold: float = typer.Option(
        6.0,
        "--synergy-threshold",
        min=0.0,
        max=10.0,
        help="Mindest-Score für Synergy-Kombinationen (0-10, Standard: 6.0 wie früher)",
    ),
    tcm_type: str = typer.Option(
        "",
        "--tcm-type",
        help=(
            "Optionaler TCM-Grundtyp, z.B. 'Holz-Leber', 'Feuer-Herz', "
            "'Erde-Milz', 'Metall-Lunge', 'Wasser-Niere'."
        ),
    ),
    planet_type: str = typer.Option(
        "",
        "--planet-type",
        help=(
            "Optionaler Planetentyp, z.B. 'Mars', 'Venus', 'Sonne', 'Saturn', 'Neptun'."
        ),
    ),
    debug_groups: bool = typer.Option(
        False,
        "--debug-groups",
        help="Zeigt Verteilung der Multiplex-Kandidaten pro Gruppe an",
    ),
    influence_compare: bool = typer.Option(
        False,
        "--influence-compare",
        help=(
            "Berechnet zusätzliche Influence-Scores (TCM+Organuhr) im JSON-Export "
            "zur Gegenüberstellung von Basis- und beeinflusstem Scoring."
        ),
    ),
    db_analysis_mode: bool = typer.Option(
        False,
        "--db-analysis",
        help=(
            "Aktiviert experimentelle Bruce-Copen-DB-Analyse im JSON-Export "
            "(zusätzlicher Block 'db_analysis')."
        ),
    ),
    morphic_field: bool = typer.Option(
        True,  # GEÄNDERT 01.12.2025: Standardmäßig aktiviert für authentischere Ergebnisse
        "--morphic-field/--no-morphic-field",
        help=(
            "Aktiviert morphische Feld-Analyse im JSON-Export "
            "(zusätzlicher Block 'morphic_field'). Standard: aktiviert."
        ),
    ),
    mf_geometry: str = typer.Option(
        "",
        "--mf-geometry",
        help=(
            "Optionale geometrische Form fuer die morphische Feld-Analyse "
            "(z.B. 'flower_of_life', 'merkaba', 'torus')."
        ),
    ),
    mf_intention: str = typer.Option(
        "",
        "--mf-intention",
        help=(
            "Optionale Intention fuer die morphische Feld-Analyse "
            "(z.B. 'healing', 'detox', 'protection', 'harmonization')."
        ),
    ),
    mf_use_hardware: bool = typer.Option(
        True,  # GEÄNDERT 01.12.2025: Standardmäßig aktiviert für Kozyrev-Integration
        "--mf-use-hardware/--no-mf-use-hardware",
        help=(
            "Verwendet Hardware-Modulation (h_level) in der morphischen Feld-Analyse. "
            "Standard: aktiviert (Kozyrev-inspiriert)."
        ),
    ),
    focus_weighting: bool = typer.Option(
        True,
        "--focus-weighting/--no-focus-weighting",
        help=(
            "Steuert, ob der gesetzte Fokus das Scoring sanft gewichten darf "
            "(Multiplikator bis ca. +5%)."
        ),
    ),
    export_3d: bool = typer.Option(
        False,
        "--export-3d",
        help="Generiert eine 3D-JSON-Datei für den Morphic Viewer.",
    ),
    show_progress: bool = typer.Option(
        True,
        "--progress/--no-progress",
        help="Zeigt Fortschritts-Updates während des Scans.",
    ),
    use_hybrid_entropy: bool = typer.Option(
        False,
        "--hybrid-entropy",
        help="Verwendet Hybrid-Entropie (mehrere Quellen kombiniert).",
    ),
    show_confidence: bool = typer.Option(
        True,
        "--confidence/--no-confidence",
        help="Zeigt Konfidenz-Bewertung im Report.",
    ),
    intention: str = typer.Option(
        "",
        "--intention",
        "-I",
        help=(
            "Aktive Intention für Score-Gewichtung: "
            "'healing' (Heilung), 'clearing' (Klärung), 'protection' (Schutz), "
            "'transformation', 'harmonization', 'connection', 'activation'. "
            "Leer = keine Gewichtung."
        ),
    ),
    filename_suffix: str = typer.Option(
        "",
        "--filename-suffix",
        help="Optionaler Suffix für den Dateinamen (z.B. Profilname bei Top-3 Scan)",
    ),
    scan_type: str = typer.Option(
        "SINGLE",
        "--scan-type",
        help="Scan-Typ für Ordner-Label: 'SINGLE', 'top5_session', etc.",
    ),
    session_id: str = typer.Option(
        "",
        "--session-id",
        help="Session-ID für Top-5 Gruppierung (alle Profile derselben Session)",
    ),
    # === ERWEITERTE KLIENTEN-MODIFIKATOREN (optional) ===
    client_gender: str = typer.Option(
        "",
        "--gender",
        "-G",
        help="Geschlecht des Klienten: 'm' (männlich), 'f' (weiblich), 'd' (divers). Leer = neutral.",
    ),
    client_weight: float = typer.Option(
        0.0,
        "--weight",
        "-W",
        help="Gewicht in kg (z.B. 75.5). 0 = nicht angegeben.",
    ),
    client_height: int = typer.Option(
        0,
        "--height",
        "-H",
        help="Größe in cm (z.B. 178). 0 = nicht angegeben.",
    ),
    client_stress: int = typer.Option(
        0,
        "--stress-level",
        help="Stress-Level 1-10 (1=niedrig, 10=sehr hoch). 0 = nicht angegeben.",
    ),
    client_sleep: float = typer.Option(
        0.0,
        "--sleep-hours",
        help="Durchschnittliche Schlafstunden pro Nacht. 0 = nicht angegeben.",
    ),
    client_emf: str = typer.Option(
        "",
        "--emf-exposure",
        help="EMF-Belastung: 'niedrig', 'mittel', 'hoch'. Leer = nicht angegeben.",
    ),
    image_path: str = typer.Option(
        "",
        "--image",
        help="Optionaler Pfad zu einem Klienten-Bild (JPG/PNG) fuer Bild-Vektor-Signatur.",
    ),
) -> None:
    """Führt einen erweiterten Multiplex-Scan über vordefinierte Gruppenprofile durch."""

    from apps.cli.commands.scan import _clamp
    from apps.cli.commands.helpers import (
        _atomic_write_text,
        _build_db_analysis_summary,
        _build_db_client_rate_block,
        _build_db_items_from_sub_results,
        _build_influence_factors,
        _build_morphic_axes_from_sub_results,
        _compute_influence_multiplier_for_item,
        _format_group_label,
        _interpret_level,
        _interpret_potency,
        _is_remedy_group,
        _rates_to_level_info,
        _render_basic_html,
        _render_multiplex_txt,
        _resolve_export_paths,
        analyze_remedy_synergies,
    )
    from tools.reporting_common import register_report_artifact
    from tools.pdf_exporter import html_to_text
    from tools.simple_pdf import write_text_pdf

    # Phase 2: Hardware Detection & Auto-Config
    sys_info = get_full_system_report()
    _echo(
        f"Hardware-Profil: {sys_info['profile']} | CPU: {sys_info['cpu']['physical_cores']} Kerne"
    )
    if sys_info["gpu"]["has_gpu"]:
        _echo(f"GPU-Beschleunigung: AKTIV ({sys_info['gpu']['device_name']})")
    else:
        _echo("GPU-Beschleunigung: INAKTIV (CPU Mode)")

    s_info = sys_info.get("sensors", {})
    if s_info.get("count", 0) > 0:
        _echo(f"Externe Sensoren: {s_info['count']} erkannt")
        for d in s_info.get("devices", []):
            _echo(f"  - [{d['type']}] {d['name']}")

    _echo("-" * 60)

    prof = (profile or "pathogen").strip().lower()

    # Phase 1 Modularisierung: Registry Check
    registry_groups = get_groups_for_profile(prof)
    if registry_groups:
        groups = registry_groups
    elif prof == "pathogen":
        # Fokus-Profil: Pathogene Erreger (Bakterien, Viren, Parasiten, Pilze)
        groups = [
            # Basis-Erreger
            "bakterien",
            "viren",
            "parasiten",
            "pilze",
            # Fein-Differenzierung
            "bakterien_fein",
            "viren_fein",
            "parasiten_fein",
            "pilze_fein",
            # Detaillierte Erreger-Analyse
            "bakterien_detailliert_fein",
            "viren_detailliert_fein",
            "parasiten_detailliert_fein",
            "pilze_detailliert_fein",
            # Biofilme & Infektionssymptome
            "biofilme_fein",
            "infektions_symptome_fein",
            # Immunabwehr
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "immunstaerkung_remedies_multiplex",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "toxin":
        # Fokus-Profil: Toxine, Schwermetalle, Umweltbelastungen
        groups = [
            # Schwermetalle
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            # Chemikalien & Pestizide
            "chemikalien_tox",
            "chemikalien_detailliert_fein",
            "pestizide_tox",
            # Strahlung & EMF
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "emf_fein",
            # Geopathie & Umwelt
            "geopathie",
            "geopathie_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Toxin-Symptome & Entgiftung
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_remedies_multiplex",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "regulation":
        # Fokus-Profil: Energetische & vegetative Regulation
        groups = [
            # Chakren & Energiezentren
            "chakren",
            "chakren_full",
            "chakren_detailliert_fein",
            "chakren_erweitert",
            "nebenchakren",
            "energetische_blockaden_fein",
            # Meridiane & TCM
            "meridiane",
            "meridiane_detailliert_fein",
            "tcm_punkte",
            "tcm_punkte_extended",
            "tcm_full",
            "extra_meridiane",
            # Zahn-Organ-Beziehungen
            "zahnorgane",
            "odontone",
            # Vegetative Regulation
            "nervensystem_vegetativ",
            "nervensystem_neurotransmitter_fein",
            # Zellregulation
            "mikrozirkulation",
            "mitochondrien",
            "entzuendung",
            # Hormonelle Regulation
            "endokrin",
            "hormone_symptome_fein",
            # Entgiftung & Nährstoffe
            "detox",
            "mikronaehrstoffe",
            "orthomolekular_therapie_multiplex",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "meridiane_detailliert":
        # Fokus-Profil: TCM, Meridiane, Akupunktur
        groups = [
            # Meridiane
            "meridiane",
            "meridiane_detailliert_fein",
            "extra_meridiane",
            # TCM Punkte & Rezepturen
            "tcm_punkte",
            "tcm_punkte_extended",
            "tcm_full",
            "tcm_rezepturen",
            "tcm_rezepturen_multiplex",
            # Chakren & Energie
            "chakren",
            "chakren_full",
            "chakren_detailliert_fein",
            "chakren_erweitert",
            "energetische_blockaden_fein",
            # Psychosomatik
            "emotionale_blockaden_fein",
            "psychosomatik_fein",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("full", "therapy"):
        # Umfassendes Profil: reale/verfeinerte Gruppen für maximale Multiplex-Analyse
        groups = [
            # Basis-Systeme
            "kreislauf",
            "kreislauf_fein",
            "chakren",
            "chakren_full",
            "chakren_erweitert",
            "nebenchakren",
            "meridiane",
            "meridiane_detailliert_fein",
            "tcm_punkte",
            "tcm_punkte_extended",
            "tcm_full",
            "extra_meridiane",
            # Pathogene (Basis + Fein)
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            # Toxine & Belastungen
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "strahlung_schutz_multiplex",
            "geopathie_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Regulation & Systeme
            "endokrin",
            "hormone_schilddruese_fein",
            "hormone_geschlecht_fein",
            "detox",
            "entgiftung_organe_fein",
            "mikrozirkulation",
            "mitochondrien",
            "entzuendung",
            "allergene",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "mikronaehrstoffe",
            "orthomolekular_mineralien_fein",
            "orthomolekular_vitamine_fein",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "zahnorgane",
            "zahnorgane_fein",
            "odontone",
            "schlaf",
            "schlafstoerungen_fein",
            # Remedies & Therapien
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "homoeopathie_sarcoden",
            "tcm_rezepturen",
            "tcm_rezepturen_potenzen",
            "tcm_rezepturen_multiplex",
            "spagyrik",
            "spagyrik_multiplex",
            "farbtherapie",
            "edelsteine",
            "edelsteine_chakren",
            "edelsteine_schutz",
            "bachblueten_38",
            "bachblueten_multiplex",
            # Erweiterte Protokolle / Frequenzen
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("dizziness", "schwindel"):
        # Fokus-Profil: Schwindel (multifaktorielle Ursachen)
        groups = [
            # Spezifische Schwindel-Gruppen
            "schwindel_hws",
            "schwindel_kreislauf",
            "schwindel_medikament",
            "schwindel_vestibular",
            "schwindel_vestibular_fein",
            "schwindel_zentral",
            "schwindel_zentral_fein",
            # Kreislauf & Herz
            "kreislauf",
            "kreislauf_fein",
            "herz_fein",
            # Wirbelsäule & Statik
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            # Sinnesorgane & Nerven
            "auge_fein",
            "ohr_fein",
            "nervensystem_zns_fein",
            "nervensystem_hirnnerven_fein",
            "nervensystem_vegetativ",
            # Systemische Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "schwindel_detailliert":
        groups = [
            "schwindel_hws",
            "schwindel_kreislauf",
            "schwindel_medikament",
            "schwindel_vestibular",
            "schwindel_vestibular_fein",
            "schwindel_zentral",
            "schwindel_zentral_fein",
            "kreislauf",
            "kreislauf_fein",
            "herz_fein",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "auge_fein",
            "ohr_fein",
            "nervensystem_zns_fein",
            "nervensystem_hirnnerven_fein",
            "nervensystem_vegetativ",
            "nerven_symptome_fein",
            "nerven_pathologien_fein",
            "nerven_remedies_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("circulation", "durchblutung"):
        # Fokus-Profil: Durchblutung & Gefäßsystem
        groups = [
            # Herz-Kreislauf & Blut
            "kreislauf",
            "kreislauf_fein",
            "herz_fein",
            "blut_fein",
            # Mikrozirkulation & strukturelle Achsen
            "mikrozirkulation",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "zahnorgane",
            "zahnorgane_fein",
            "odontone",
            # Meridiane & TCM
            "meridiane",
            "meridiane_detailliert_fein",
            "tcm_punkte",
            "tcm_punkte_extended",
            "tcm_full",
            # Toxische Belastungen
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            # Regulation & Systeme
            "entzuendung",
            "endokrin",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Remedies & komplementäre Verfahren
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("respiration", "atmung"):
        # Fokus-Profil: Atmung (Lunge, Bronchien, Atemwege)
        groups = [
            # Atmungs-Systeme (erweitert + fein)
            "atmung_lunge",
            "atmung_bronchien",
            "atmung_zwerchfell",
            "atmung_nase",
            "atmung_rachen",
            "atmung_lunge_fein",
            "atmung_symptome_fein",
            "atmung_pathologien_fein",
            # Kreislauf-Achse
            "kreislauf",
            "kreislauf_fein",
            # Pathogene (Atemwegsinfekte)
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            # Toxische Atembelastungen
            "schwermetalle",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            # Immun & Regulation
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Remedies & Therapien
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "atmung_remedies_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "knochen_detailliert":
        groups = [
            "knochen_gelenke",
            "knochen_gelenke_fein",
            "knochen_symptome_fein",
            "knochen_pathologien_fein",
            "knochen_osteoporose",
            "knochen_osteoblasten",
            "knochen_osteoklasten",
            "knochen_knorpel",
            "knochen_remedies_multiplex",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_sakral",
            "wirbelsaeule_bandscheiben",
            "wirbelsaeule_bandscheiben_fein",
            "wirbelsaeule_symptome_fein",
            "wirbelsaeule_pathologien_fein",
            "wirbelsaeule_remedies_multiplex",
            "muskulatur_fein",
            "faszien_fein",
            "schmerz_ruecken",
            "schmerz_gelenk",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "orthomolekular_therapie_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "wirbelsaeule_detailliert":
        groups = [
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_sakral",
            "wirbelsaeule_bandscheiben",
            "wirbelsaeule_bandscheiben_fein",
            "wirbelsaeule_facetten",
            "wirbelsaeule_symptome_fein",
            "wirbelsaeule_pathologien_fein",
            "wirbelsaeule_remedies_multiplex",
            "knochen_gelenke",
            "knochen_gelenke_fein",
            "knochen_symptome_fein",
            "knochen_pathologien_fein",
            "knochen_remedies_multiplex",
            "nervensystem_zns_fein",
            "nervensystem_pns_fein",
            "nerven_symptome_fein",
            "nerven_pathologien_fein",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "stoerfelder_toxisch":
        groups = [
            "entgiftung_leber_phase1",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_haut",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            "entgiftung_remedies_multiplex",
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "luft_symptome_fein",
            "luft_remedies_multiplex",
            "nahrung_symptome_fein",
            "nahrung_unvertraeglichkeiten_fein",
            "nahrung_remedies_multiplex",
            "geopathie_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "strahlung_schutz_multiplex",
            "magnetfeld",
            "entzuendung",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_therapie_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("immune", "immunsystem"):
        # Fokus-Profil: Immunsystem (angeboren, erworben, Autoimmunität)
        groups = [
            # Immunsystem (erweitert + fein)
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "immunsystem_zytokine",
            "immunsystem_zytokine_fein",
            "immunsystem_autoimmun",
            "immunsystem_autoimmun_fein",
            # Immunsystem-Antikörper
            "immunsystem_antikoerper",
            # Lymphsystem & Entgiftungsachsen
            "lymphsystem_lymphknoten",
            "lymphsystem_lymphknoten_fein",
            "lymphsystem_milz",
            "lymphsystem_thymus",
            "lymphsystem_tonsillen",
            "entgiftung_lymphe",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_organe_fein",
            # Pathogene
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            # Belastungen, die das Immunsystem schwächen
            "schwermetalle",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            # Mikronährstoffe & Regulation
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "entzuendung",
            # Remedies (systemisch, nosodisch, miasmatisch)
            "homoeopathie_nosoden",
            "homoeopathie_isopathie",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "miasmatik_remedies_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("detox", "entgiftung"):
        # Fokus-Profil: Entgiftung (Leber, Niere, Lymphe, Haut, Darm)
        groups = [
            # Entgiftungssysteme
            "entgiftung_leber_phase1",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_haut",
            "entgiftung_organe_fein",
            "entgiftung_remedies_multiplex",
            "entgiftung_symptome_fein",
            # Belastungen
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("heavy_metals", "heavy-metal", "schwermetalle"):
        # Fokus-Profil: Schwermetalle & Ausleitung
        groups = [
            # Schwermetalle detailliert
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            # Toxin-Symptome
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Entgiftungsachsen
            "entgiftung_leber_phase1",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            "entgiftung_remedies_multiplex",
            # Mikronährstoffe für Ausleitung
            "mikronaehrstoffe",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "narben_entstoerung_energetisch":
        groups = [
            # Energetische Stoerfelder & Achsen
            "energetische_blockaden_fein",
            "meridiane",
            "meridiane_detailliert_fein",
            "tcm_punkte",
            "tcm_punkte_extended",
            "tcm_full",
            "extra_meridiane",
            "chakren",
            "chakren_full",
            "chakren_detailliert_fein",
            "chakren_erweitert",
            # Remedies & innere Regulation
            "energie_remedies_multiplex",
            "orthomolekular_therapie_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "narben_entstoerung_gewebe_remedies":
        groups = [
            # Haut / Narben / Zahnstorferlder
            "haut_detailliert_fein",
            "energetische_blockaden_fein",
            "zahnorgane",
            "zahnorgane_fein",
            "odontone",
            # Entgiftung & Gewebeachsen
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_haut",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            # Umwelt- und Materialbelastungen
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Remedies & Mikronaehrstoffe
            "energie_remedies_multiplex",
            "entgiftung_remedies_multiplex",
            "orthomolekular_therapie_multiplex",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Hersteller-spezifische Remedy-Gruppen (NEU für Narben)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "schwermetalle_sanft_multiplex":
        groups = [
            # Schwermetalle & Toxin-Symptome
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "toxine_symptome_fein",
            # Umweltquellen
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Entgiftungssysteme (sanft, breit)
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            # Remedies & innere Regulation
            "toxine_remedies_multiplex",
            "entgiftung_remedies_multiplex",
            "orthomolekular_therapie_multiplex",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("radiation", "strahlung"):
        # Fokus-Profil: Strahlenbelastungen (EMF, Umwelt, Schutz)
        groups = [
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "strahlung_schutz_multiplex",
            "magnetfeld",
            "geopathie_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "strahlung_detailliert":
        groups = [
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "strahlung_schutz_multiplex",
            "magnetfeld",
            "geopathie_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "luft_symptome_fein",
            "luft_remedies_multiplex",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "energie_remedies_multiplex",
            "psyche_remedies_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof in ("teeth", "zahn", "zaehne", "zähne"):
        # Fokus-Profil: Zahn-Organ-System, Materialien, Störfelder
        groups = [
            # Zähne & Kiefer
            "zahnorgane",
            "zahnorgane_fein",
            "zahnorgane_frontzaehne",
            "zahnorgane_quadrant1",
            "zahnorgane_quadrant2",
            "zahnorgane_quadrant3",
            "zahnorgane_quadrant4",
            "zahnorgane_weisheitszaehne",
            "zahnorgane_kiefergelenk",
            "zahnorgane_kiefer_herde",
            "zahn_materialien_fein",
            "zahn_pathologien_fein",
            "zahn_symptome_fein",
            "zahn_remedies_multiplex",
            # Zugehörige Achsen (Wirbelsäule, Statik, Nervensystem)
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_remedies_multiplex",
            "nervensystem_zns_fein",
            # Systemische Remedies ergänzen
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "zahn_detailliert":
        groups = [
            "zahnorgane",
            "zahnorgane_fein",
            "zahnorgane_frontzaehne",
            "zahnorgane_quadrant1",
            "zahnorgane_quadrant2",
            "zahnorgane_quadrant3",
            "zahnorgane_quadrant4",
            "zahnorgane_weisheitszaehne",
            "zahnorgane_kiefergelenk",
            "zahnorgane_kiefer_herde",
            "zahn_materialien_fein",
            "zahn_pathologien_fein",
            "zahn_symptome_fein",
            "zahn_remedies_multiplex",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_remedies_multiplex",
            "knochen_gelenke",
            "knochen_gelenke_fein",
            "knochen_symptome_fein",
            "knochen_pathologien_fein",
            "knochen_osteoporose",
            "knochen_osteoblasten",
            "knochen_osteoklasten",
            "knochen_knorpel",
            "knochen_remedies_multiplex",
            "nervensystem_zns_fein",
            "nervensystem_vegetativ",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "haut_detailliert":
        # Fokus-Profil: Haut (Dermatologie, Allergien, Entgiftung)
        groups = [
            # Haut-spezifisch
            "haut_detailliert_fein",
            "hautprobleme",
            "hautprobleme_fein",
            # Entgiftung über Haut
            "entgiftung_haut",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_symptome_fein",
            # Durchblutung & Versorgung
            "mikrozirkulation",
            "kreislauf_fein",
            # Immunsystem (Allergien, Autoimmun)
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "immunsystem_autoimmun_fein",
            "entzuendung",
            # Pathogene (Hautinfektionen)
            "bakterien_fein",
            "pilze_fein",
            "viren_fein",
            # Psychosomatik (Haut als Spiegel)
            "psychosomatik_fein",
            "emotionale_blockaden_fein",
            # Mikronährstoffe
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "haut_detailliert_toxisch":
        groups = [
            "haut_detailliert_fein",
            "hautprobleme_fein",
            "hautprobleme",
            "entgiftung_haut",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "mikrozirkulation",
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "luft_symptome_fein",
            "luft_remedies_multiplex",
            "nahrung_symptome_fein",
            "nahrung_unvertraeglichkeiten_fein",
            "nahrung_remedies_multiplex",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "immunsystem_autoimmun_fein",
            "immunsystem_zytokine_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_therapie_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            # Zahn- und Kieferachsen
            "zahnorgane",
            "zahnorgane_fein",
            "zahnorgane_frontzaehne",
            "zahnorgane_quadrant1",
            "zahnorgane_quadrant2",
            "zahnorgane_quadrant3",
            "zahnorgane_quadrant4",
            "zahnorgane_weisheitszaehne",
            "zahnorgane_kiefergelenk",
            "zahnorgane_kiefer_herde",
            "zahn_materialien_fein",
            "zahn_pathologien_fein",
            "zahn_symptome_fein",
            "zahn_remedies_multiplex",
            # Wirbelsäule & Nervensystem als Zahn-Haut-Achse
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_remedies_multiplex",
            "nervensystem_zns_fein",
            "nervensystem_vegetativ",
            # Systemische Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "auge_detailliert":
        groups = [
            # Anatomie & Funktion Auge
            "auge_fein",
            "nervensystem_hirnnerven_fein",
            "nervensystem_zns_fein",
            "wirbelsaeule_hws",
            "mikrozirkulation",
            # Pathogene & Belastungen
            "bakterien_detailliert_fein",
            "viren_detailliert_fein",
            "pilze_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            # Entgiftung & Immun
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_organe_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            # Orthomolekular & Nährstoffe
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "orthomolekular_therapie_multiplex",
            # Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "ohr_detailliert":
        groups = [
            # Anatomie & Funktion Ohr / Gleichgewicht
            "ohr_fein",
            "schwindel_vestibular_fein",
            "schwindel_zentral_fein",
            "nervensystem_hirnnerven_fein",
            "nervensystem_zns_fein",
            "nervensystem_vegetativ",
            "wirbelsaeule_hws",
            # Pathogene & Toxine
            "bakterien_detailliert_fein",
            "viren_detailliert_fein",
            "pilze_detailliert_fein",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            # Entgiftung & Immun
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_organe_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            # Nerven-spezifische Symptomgruppen & Remedies
            "nerven_symptome_fein",
            "nerven_pathologien_fein",
            "nerven_remedies_multiplex",
            "anti_infektions_remedies_multiplex",
            "immunstaerkung_remedies_multiplex",
            # Orthomolekular & Systemische Remedies
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "leber_detailliert":
        groups = [
            # Leber-Entgiftungsphasen & Enzyme
            "entgiftung_leber_phase1",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            # Entgiftungsachsen
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_haut",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            # Verdauung / Leber-Galle-Achse
            "verdauung_leber",
            "verdauung_galle",
            "verdauung_pankreas",
            "verdauung_magen",
            "verdauung_duenndarm",
            "verdauung_dickdarm",
            "verdauung_mikrobiom",
            "verdauung_barriere",
            "verdauung_duenndarm_fein",
            "verdauung_dickdarm_fein",
            "verdauung_mikrobiom_fein",
            "verdauung_symptome_fein",
            "verdauung_pathologien_fein",
            # Toxine & Schwermetalle
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Immun & Entzündung
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "immunsystem_zytokine_fein",
            "entzuendung",
            # Orthomolekular & Mikronährstoffe
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "orthomolekular_multiplex",
            "orthomolekular_therapie_multiplex",
            # Entgiftungs- und Verdauungs-Remedies
            "entgiftung_remedies_multiplex",
            "verdauung_remedies_multiplex",
            # Systemische Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "galle_detailliert":
        groups = [
            # Galle & hepatobiliäre Achse
            "verdauung_galle",
            "verdauung_leber",
            "verdauung_pankreas",
            "verdauung_magen",
            "verdauung_duenndarm",
            "verdauung_dickdarm",
            "verdauung_mikrobiom",
            "verdauung_barriere",
            "verdauung_duenndarm_fein",
            "verdauung_dickdarm_fein",
            "verdauung_mikrobiom_fein",
            "verdauung_symptome_fein",
            "verdauung_pathologien_fein",
            # Entgiftung
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            # Toxine & Immun
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "toxine_symptome_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            # Orthomolekular & Remedies
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            "verdauung_remedies_multiplex",
            "entgiftung_remedies_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "verdauung_detailliert":
        groups = [
            # Verdauungstrakt komplett
            "verdauung_magen",
            "verdauung_duenndarm",
            "verdauung_dickdarm",
            "verdauung_leber",
            "verdauung_galle",
            "verdauung_pankreas",
            "verdauung_mikrobiom",
            "verdauung_barriere",
            "verdauung_duenndarm_fein",
            "verdauung_dickdarm_fein",
            "verdauung_mikrobiom_fein",
            "verdauung_symptome_fein",
            "verdauung_pathologien_fein",
            # Entgiftung & Immun
            "entgiftung_darm",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_organe_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            # Pathogene & Toxine
            "bakterien_detailliert_fein",
            "viren_detailliert_fein",
            "parasiten_detailliert_fein",
            "pilze_detailliert_fein",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "nahrung_symptome_fein",
            "nahrung_unvertraeglichkeiten_fein",
            "nahrung_remedies_multiplex",
            # Orthomolekular & Remedies
            "verdauung_remedies_multiplex",
            "entgiftung_remedies_multiplex",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "herz_kreislauf_fein":
        groups = [
            "herz_fein",
            "kreislauf",
            "kreislauf_fein",
            "herz_symptome_fein",
            "herz_pathologien_fein",
            "kreislauf_symptome_fein",
            "mikrozirkulation",
            "meridiane",
            "meridiane_detailliert_fein",
            "herz_remedies_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "atmung_lunge_detailliert":
        groups = [
            # Atmung/Lunge detailliert inkl. Lunge-Darm-Achse
            "atmung_lunge",
            "atmung_bronchien",
            "atmung_zwerchfell",
            "atmung_nase",
            "atmung_rachen",
            "atmung_lunge_fein",
            "atmung_symptome_fein",
            "atmung_pathologien_fein",
            # Kreislauf-Kopplung
            "kreislauf",
            "kreislauf_fein",
            # Lunge-Darm-Achse
            "verdauung_barriere",
            "verdauung_mikrobiom_fein",
            # Pathogene und Belastungen
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            # Immun & Regulation
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            # Remedies & Therapien
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "atmung_remedies_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "nervensystem_detailliert":
        groups = [
            "nervensystem_zns",
            "nervensystem_zns_fein",
            "nervensystem_pns",
            "nervensystem_pns_fein",
            "nervensystem_vegetativ",
            "nervensystem_hirnnerven",
            "nervensystem_hirnnerven_fein",
            "nervensystem_plexus",
            "nervensystem_neurotransmitter",
            "nervensystem_neurotransmitter_fein",
            "nerven_symptome_fein",
            "nerven_pathologien_fein",
            "nerven_remedies_multiplex",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_sakral",
            "wirbelsaeule_bandscheiben",
            "wirbelsaeule_bandscheiben_fein",
            "wirbelsaeule_symptome_fein",
            "wirbelsaeule_pathologien_fein",
            "schwindel_hws",
            "schwindel_kreislauf",
            "schwindel_medikament",
            "schwindel_vestibular",
            "schwindel_vestibular_fein",
            "schwindel_zentral",
            "schwindel_zentral_fein",
            "schmerz_kopf",
            "schmerz_kopf_fein",
            "schmerz_ruecken",
            "schmerz_gelenk",
            "schlafstoerungen",
            "schlafstoerungen_fein",
            "muedigkeit_chronisch",
            "konzentration",
            "schwermetalle",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            "strahlung_tox",
            "strahlung_quellen_fein",
            "strahlung_symptome_fein",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "orthomolekular_therapie_multiplex",
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            "energie_remedies_multiplex",
            "psyche_remedies_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "endokrin_detailliert":
        # Fokus-Profil: Hormonsystem, Schilddrüse, Nebenniere, Geschlechtshormone
        groups = [
            # Endokrine Drüsen
            "endokrin",
            "schilddruese_fein",
            "nebenniere_fein",
            "hypophyse_fein",
            # Hormone & Symptome
            "hormone_symptome_fein",
            "hormone_schilddruese_fein",
            "hormone_geschlecht_fein",
            "hormone_remedies_multiplex",
            # Geschlechtsspezifisch
            "urogenitalsystem_fein",
            "wechseljahre_detailliert_fein",
            "schwangerschaft_geburt_fein",
            # Stress- und Regulationsachsen
            "nervensystem_vegetativ",
            "schlafstoerungen",
            "schlafstoerungen_fein",
            "muedigkeit_chronisch",
            # Entgiftung & Immunsystem
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3_fein",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_organe_fein",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            # Mikronährstoffe & Orthomolekular
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "vitamine_detailliert_fein",
            "mineralien_spurenelemente_detailliert_fein",
            "aminosaeuren_detailliert_fein",
            "fettsaeuren_detailliert_fein",
            "orthomolekular_therapie_multiplex",
            # Systemische Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            "energie_remedies_multiplex",
            "psyche_remedies_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "urogenital_detailliert":
        groups = [
            "urogenitalsystem_fein",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_organe_fein",
            # Pathogene
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            # Toxische Belastungen
            "schwermetalle",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Zahn- & Wirbelsäulenachsen (Niere/Blase-Bezug)
            "zahnorgane",
            "zahnorgane_fein",
            "zahnorgane_quadrant1",
            "zahnorgane_quadrant2",
            "zahnorgane_quadrant3",
            "zahnorgane_quadrant4",
            "zahnorgane_weisheitszaehne",
            "zahnorgane_kiefer_herde",
            "zahn_materialien_fein",
            "zahn_pathologien_fein",
            "zahn_symptome_fein",
            "zahn_remedies_multiplex",
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_remedies_multiplex",
            "meridiane",
            "meridiane_detailliert_fein",
            # Regulation & Mikronährstoffe
            "immunsystem_angeboren_fein",
            "immunsystem_erworben_fein",
            "entzuendung",
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_therapie_multiplex",
            # Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "schmerz_detailliert":
        groups = [
            # Schmerz- und Schlafsymptomatik
            "schmerz_kopf",
            "schmerz_kopf_fein",
            "schmerz_ruecken",
            "schmerz_gelenk",
            "schlafstoerungen",
            "schlafstoerungen_fein",
            "muedigkeit_chronisch",
            # Strukturelle Achsen
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_sakral",
            "wirbelsaeule_bandscheiben",
            "wirbelsaeule_bandscheiben_fein",
            "wirbelsaeule_symptome_fein",
            "wirbelsaeule_pathologien_fein",
            "wirbelsaeule_remedies_multiplex",
            "knochen_gelenke",
            "knochen_gelenke_fein",
            "knochen_symptome_fein",
            "knochen_pathologien_fein",
            "muskulatur_fein",
            "faszien_fein",
            # Entzündung & Immun
            "entzuendung",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            # Belastungen
            "schwermetalle",
            "schwermetalle_detailliert_fein",
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Psyche, Energie, Miasmen
            "psyche_remedies_multiplex",
            "energie_remedies_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            # Mikronährstoffe & Orthomolekular
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            # Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    elif prof == "tote_zaehne_detailliert":
        groups = [
            # Zähne & Kiefer (devitale Zähne, Herde)
            "zahnorgane",
            "zahnorgane_fein",
            "zahnorgane_frontzaehne",
            "zahnorgane_quadrant1",
            "zahnorgane_quadrant2",
            "zahnorgane_quadrant3",
            "zahnorgane_quadrant4",
            "zahnorgane_weisheitszaehne",
            "zahnorgane_kiefergelenk",
            "zahnorgane_kiefer_herde",
            "zahn_materialien_fein",
            "zahn_pathologien_fein",
            "zahn_symptome_fein",
            "zahn_remedies_multiplex",
            # Knochen-/Kieferstruktur
            "knochen_gelenke",
            "knochen_gelenke_fein",
            "knochen_symptome_fein",
            "knochen_pathologien_fein",
            "knochen_osteoporose",
            "knochen_osteoblasten",
            "knochen_osteoklasten",
            "knochen_knorpel",
            "knochen_remedies_multiplex",
            # Wirbelsäule & Nervensystem
            "wirbelsaeule",
            "wirbelsaeule_fein",
            "wirbelsaeule_hws",
            "wirbelsaeule_bws",
            "wirbelsaeule_lws",
            "wirbelsaeule_sakral",
            "wirbelsaeule_bandscheiben",
            "wirbelsaeule_bandscheiben_fein",
            "wirbelsaeule_symptome_fein",
            "wirbelsaeule_pathologien_fein",
            "wirbelsaeule_remedies_multiplex",
            "nervensystem_zns_fein",
            "nervensystem_vegetativ",
            "nervensystem_hirnnerven",
            "nervensystem_hirnnerven_fein",
            # Toxine & Materialien
            "schwermetalle",
            "schwermetalle_tox",
            "schwermetalle_detailliert_fein",
            "chemikalien_detailliert_fein",
            "toxine_symptome_fein",
            "toxine_remedies_multiplex",
            # Pathogene
            "bakterien",
            "bakterien_detailliert_fein",
            "viren",
            "viren_detailliert_fein",
            "parasiten",
            "parasiten_detailliert_fein",
            "pilze",
            "pilze_detailliert_fein",
            # Entgiftung & Immunsystem
            "entgiftung_leber_phase1",
            "entgiftung_leber_phase1_fein",
            "entgiftung_leber_phase2",
            "entgiftung_leber_phase2_fein",
            "entgiftung_leber_phase3",
            "entgiftung_leber_phase3_fein",
            "entgiftung_leber",
            "entgiftung_niere",
            "entgiftung_lymphe",
            "entgiftung_darm",
            "entgiftung_organe_fein",
            "entgiftung_symptome_fein",
            "immunsystem_angeboren",
            "immunsystem_angeboren_fein",
            "immunsystem_erworben",
            "immunsystem_erworben_fein",
            "immunsystem_autoimmun_fein",
            "immunsystem_zytokine_fein",
            "entzuendung",
            # Umweltachsen
            "umweltbelastungen_erweitert_fein",
            "wohnraumgifte_fein",
            # Mikronährstoffe & Regulation
            "mikronaehrstoffe",
            "orthomolekular_vitamine_fein",
            "orthomolekular_mineralien_fein",
            "orthomolekular_aminosauren_fein",
            "orthomolekular_therapie_multiplex",
            "miasmatik_fein",
            "miasmatik_remedies_multiplex",
            # Systemische Remedies
            "homoeopathie_klassisch",
            "homoeopathie_klassisch_potenzen",
            "homoeopathie_komplexmittel",
            "homoeopathie_isopathie",
            "homoeopathie_nosoden",
            "spagyrik",
            "spagyrik_multiplex",
            "bachblueten_multiplex",
            "frequenz_clark_multiplex",
            "frequenz_rife_multiplex",
            "frequenz_solfeggio_multiplex",
            # Hersteller-Remedies (NEU)
            "heel_remedies_multiplex",
            "nutramedix_remedies_multiplex",
            "oorep_homeopathy_multiplex",
        ]
    else:
        _echo(
            f"Unbekanntes Multiplex-Profil: '{profile}'. Erlaubt sind 'pathogen', 'toxin', 'regulation', 'full' (Alias: 'therapy')."
        )
        raise typer.Exit(code=1)

    # Phase 1 Modularisierung: Validate Groups
    # Wir prüfen, ob die angeforderten Gruppen überhaupt existieren.
    if show_progress:
        _echo(f"[1/5] ðŸ” Validiere {len(groups)} Gruppen...")

    available_groups_set = set(list_groups())
    missing_groups = validate_profile_groups(groups, available_groups_set)

    if missing_groups:
        _echo("")
        _echo(
            "âš  WARNUNG: Folgende Gruppen wurden im Profil definiert, existieren aber nicht im System:"
        )
        for mg in missing_groups:
            _echo(f"  - {mg}")
        _echo("Die Analyse läuft weiter, aber diese Gruppen liefern KEINE Ergebnisse.")
        _echo("")

    if show_progress:
        _echo(f"[2/5] ðŸ“¦ Generiere {k_total} Kandidaten aus {len(groups)} Gruppen...")

    subgroup_svc = SubgroupService()
    items = subgroup_svc.generate_fullbody_candidates(groups, seed, k_total=k_total)
    if not items:
        _echo("Keine Multiplex-Kandidaten erzeugt.")
        raise typer.Exit(code=1)

    if show_progress:
        _echo(f"[2/5] âœ“ {len(items)} Kandidaten generiert")

    if debug_groups:
        _echo("")
        _echo("=" * 70)
        _echo(f"DEBUG: Multiplex-Kandidatenverteilung über {len(groups)} Gruppen")
        _echo("=" * 70)

        counts: Dict[str, int] = {}
        for it in items:
            g = str(it.get("group", "") or "").strip()
            if not g:
                g = "_ungrouped"
            counts[g] = counts.get(g, 0) + 1

        groups_with = sorted(counts.items(), key=lambda kv: kv[0])
        zero_groups = [g for g in groups if g not in counts]

        _echo(f"âœ“ Gruppen MIT Kandidaten: {len(groups_with)}")
        _echo(f"âœ— Gruppen OHNE Kandidaten: {len(zero_groups)}")
        _echo("")

        _echo("Kandidaten pro Gruppe:")
        for g, c in groups_with:
            _echo(f"  - {g}: {c}")
        if zero_groups:
            _echo("")
            _echo("Gruppen mit 0 Kandidaten:")
            for g in zero_groups:
                _echo(f"  - {g}")
        _echo("=" * 70)
        _echo("")

    personal_profile = {
        "emotion": _clamp(p_emotion),
        "physisch": _clamp(p_physisch),
        "mental": _clamp(p_mental),
        "astral": _clamp(p_astral),
    }

    _profile = (hardware_profile or "windows").strip().lower()
    mode = (os.getenv("ME_ENTROPY_MODE") or "legacy").strip().lower()

    # Default-Exportordner setzen, wenn nicht angegeben
    if export is None:
        export = Path("Benutzer_Archive")
    _echo(f"Export-Ziel: {export}")

    if show_progress:
        _echo("[3/5] ðŸŽ² Sampling Entropie...")

    # Hybrid-Entropy Option
    entropy_source_name = "standard"
    if use_hybrid_entropy:
        try:
            from core.hybrid_entropy import get_hybrid_h_level, format_hybrid_display

            h_level, hybrid_meta = get_hybrid_h_level()
            entropy_source_name = f"hybrid ({hybrid_meta.get('method', 'mix')})"
            src = type("HybridSource", (), {"name": lambda self: entropy_source_name})()
            if show_progress:
                _echo(format_hybrid_display(hybrid_meta))
        except ImportError:
            use_hybrid_entropy = False

    if not use_hybrid_entropy:
        if _profile == "debian_server":
            duration = 2.0
            if mode == "enhanced":
                pref = ["qrng", "gpu", "network", "cpu_timer"]
            else:
                pref = ["qrng", "gpu", "cpu_timer"]
            src = select_entropy_source(preferred=pref)
            h_level = _clamp(src.sample_h_level(duration_s=duration))
            if src.name() in ("qrng", "gpu", "network") and h_level <= 0.0:
                fallback_src = select_entropy_source(preferred=["cpu_timer"])
                fallback_h = _clamp(fallback_src.sample_h_level(duration_s=duration))
                if fallback_h > h_level:
                    src = fallback_src
                    h_level = fallback_h
        else:
            duration = 3.0 if _profile == "windows" else 2.0
            if mode == "enhanced":
                pref = ["truerng", "hid_sensor", "network", "cpu_timer"]
            else:
                pref = ["hid_sensor", "cpu_timer"]

            # Kaskadierende Fallback-Logik: Jede Quelle der Reihe nach testen
            # bis eine h_level > 0 liefert
            src = None
            h_level = 0.0
            for source_key in pref:
                candidate_src = select_entropy_source(preferred=[source_key])
                if candidate_src.name() == source_key:
                    candidate_h = _clamp(
                        candidate_src.sample_h_level(duration_s=duration)
                    )
                    if candidate_h > 0.0:
                        src = candidate_src
                        h_level = candidate_h
                        break

            # Fallback auf cpu_timer wenn keine Quelle einen Wert > 0 lieferte
            if src is None or h_level <= 0.0:
                src = select_entropy_source(preferred=["cpu_timer"])
                h_level = _clamp(src.sample_h_level(duration_s=duration))
        entropy_source_name = src.name()

    if show_progress:
        _echo(f"[3/5] âœ“ h_level: {h_level:.4f} ({entropy_source_name})")

    # Bild-Signatur laden (optional)
    image_signature = None
    if image_path and image_path.strip():
        try:
            from pathlib import Path as _P

            img_file = _P(image_path.strip())
            if img_file.exists():
                try:
                    from PIL import Image as _PILImage

                    img = _PILImage.open(img_file).convert("L").resize((32, 32))
                    image_signature = np.array(img, dtype=float)
                    if show_progress:
                        _echo(f"[2.5/5] Bild-Signatur geladen: {img_file.name}")
                except ImportError:
                    # Fallback ohne PIL: Dateigroesse + Hash als Pseudo-Vektor
                    import hashlib

                    raw = img_file.read_bytes()[:1024]
                    h = hashlib.sha256(raw).digest()
                    image_signature = np.frombuffer(h[:32], dtype=np.uint8).astype(
                        float
                    )
                    if show_progress:
                        _echo(f"[2.5/5] Bild-Signatur (fallback): {img_file.name}")
            else:
                if show_progress:
                    _echo(f"[WARN] Bild nicht gefunden: {image_path}")
        except Exception as exc:
            if show_progress:
                _echo(f"[WARN] Bild-Signatur konnte nicht geladen werden: {exc}")

    profile_obj = ClientProfile(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        image_signature=image_signature,
        personal_profile=personal_profile,
        planet_type=planet_type,
    )

    analysis = AnalysisService(rate_database={}, h_level=h_level)
    client_rates = analysis.encode_profile(profile_obj)
    client_entropy = analysis.resonator.holographic_entropy(client_rates)
    m_field = analysis.resonator.calculate_m_field(client_rates)
    heim_sig = analysis.resonator.heim_signature(client_rates)

    encoder = RateEncoder()
    client_personal_vector = encoder.personal_profile_to_vector(personal_profile)

    def resonance_fn(a: np.ndarray, b: np.ndarray) -> float:
        return float(analysis.resonator.resonance_score(a, b))

    if show_progress:
        _echo(f"[4/5] 🔬 Berechne Resonanz-Scores für {len(items)} Items...")

    nls_service = NlsService(items)
    scores = nls_service.compute_scores_v2(
        client_rates,
        client_entropy,
        resonance_fn,
        client_personal_vector=client_personal_vector,
    )

    # Gruppen-Information aus Items in Scores übertragen (für BAT-Aggregation)
    item_group_map = {it.get("label", ""): it.get("group", "") for it in items}
    for score_entry in scores:
        if "group" not in score_entry or not score_entry.get("group"):
            score_entry["group"] = item_group_map.get(score_entry.get("label", ""), "")

    # === CLIENT PROFILE MODIFIERS (erweitert 01.12.2025) ===
    from datetime import datetime as _dt

    # Initialisiere alle Modifikatoren
    modifiers = {
        "age_factor": 1.0,
        "gender_factor": 1.0,
        "bmi_factor": 1.0,
        "stress_factor": 1.0,
        "sleep_factor": 1.0,
        "emf_factor": 1.0,
    }
    client_age = 0
    client_bmi = None

    try:
        # 1. ALTERS-FAKTOR aus Geburtsdatum (Format: DDMMYYYY)
        bd = birth_date.strip()
        if len(bd) == 8:
            day = int(bd[:2])
            month = int(bd[2:4])
            year = int(bd[4:])
            birth = _dt(year, month, day)
            today = _dt.now()
            client_age = today.year - birth.year
            if today.month < birth.month or (
                today.month == birth.month and today.day < birth.day
            ):
                client_age -= 1

            if client_age < 18:
                modifiers["age_factor"] = 1.15  # Kinder: höhere Sensitivität
            elif client_age > 65:
                modifiers["age_factor"] = 1.10  # Senioren: leicht erhöhte Resonanz
            elif client_age > 50:
                modifiers["age_factor"] = 1.05  # Mittleres Alter
    except Exception:
        client_age = 0

    # 2. GESCHLECHTS-FAKTOR (optional)
    if client_gender:
        g = client_gender.strip().lower()
        if g == "f":
            modifiers["gender_factor"] = 1.05  # Weiblich: andere hormonelle Signatur
        elif g == "m":
            modifiers["gender_factor"] = 0.98  # Männlich: leicht gedämpft
        # 'd' oder andere: neutral (1.0)

    # 3. BMI-FAKTOR (optional, wenn Größe und Gewicht angegeben)
    if client_height > 0 and client_weight > 0:
        height_m = client_height / 100.0
        client_bmi = round(client_weight / (height_m**2), 1)
        if client_bmi < 18.5:
            modifiers["bmi_factor"] = 1.10  # Untergewicht: höhere Sensitivität
        elif client_bmi > 30:
            modifiers["bmi_factor"] = 0.92  # Adipositas: gedämpfte Resonanz
        elif client_bmi > 25:
            modifiers["bmi_factor"] = 0.96  # Übergewicht: leicht gedämpft

    # 4. STRESS-FAKTOR (optional)
    if client_stress > 0:
        if client_stress >= 8:
            modifiers["stress_factor"] = 1.25  # Sehr hoher Stress: verstärkte Reaktion
        elif client_stress >= 6:
            modifiers["stress_factor"] = 1.15  # Hoher Stress
        elif client_stress >= 4:
            modifiers["stress_factor"] = 1.05  # Mittlerer Stress

    # 5. SCHLAF-FAKTOR (optional)
    if client_sleep > 0:
        if client_sleep < 5:
            modifiers["sleep_factor"] = 1.20  # Starker Schlafmangel
        elif client_sleep < 6:
            modifiers["sleep_factor"] = 1.10  # Schlafmangel
        elif client_sleep > 9:
            modifiers["sleep_factor"] = (
                0.95  # Übermäßiger Schlaf (kann auf Probleme hindeuten)
            )
        elif client_sleep >= 7:
            modifiers["sleep_factor"] = 0.92  # Guter Schlaf: bessere Regeneration

    # 6. EMF-FAKTOR (optional)
    if client_emf:
        emf = client_emf.strip().lower()
        if emf == "hoch":
            modifiers["emf_factor"] = 1.25  # Hohe EMF-Belastung
        elif emf == "mittel":
            modifiers["emf_factor"] = 1.10  # Mittlere EMF-Belastung
        # "niedrig" oder leer: neutral (1.0)

    # Berechne kombinierten Modifikator (multiplikativ)
    combined_modifier = 1.0
    active_modifiers = []
    for key, value in modifiers.items():
        if value != 1.0:
            combined_modifier *= value
            active_modifiers.append(f"{key}={value:.2f}")

    # Wende kombinierten Modifikator auf alle Scores an
    if combined_modifier != 1.0:
        for score_entry in scores:
            original_score = float(score_entry.get("score", 0.0))
            score_entry["score"] = original_score * combined_modifier
            score_entry["client_modifiers"] = modifiers.copy()
            score_entry["combined_modifier"] = combined_modifier

        if show_progress:
            _echo(f"  ðŸ“Š Klienten-Modifikatoren aktiv: {', '.join(active_modifiers)}")
            _echo(f"     Kombinierter Faktor: {combined_modifier:.3f}")

    # === QUANTEN-SUPERPOSITION (zeitabhängige Modulation) ===
    import time as _time
    import math as _math

    # Berechne Quanten-Komponente aus morphic_field/engine
    HBAR = 1.054571817e-34
    n_states = 5  # Standard: 5 Quantenzustände
    amplitude = 1.0 / _math.sqrt(float(n_states))
    base_energy = 1.6e-19
    t_now = _time.time()

    real_part = 0.0
    imag_part = 0.0
    for k in range(1, n_states + 1):
        energy = base_energy * (k * k)
        phase_offset = _math.pi * float(k) / float(n_states + 1)
        phase = -(energy * t_now) / HBAR + phase_offset
        real_part += amplitude * _math.cos(phase)
        imag_part += amplitude * _math.sin(phase)

    quantum_magnitude = _math.hypot(real_part, imag_part) / _math.sqrt(float(n_states))
    # Normiere auf sinnvollen Bereich [0.8, 1.2] für sanfte Modulation
    quantum_factor = 0.9 + 0.2 * min(1.0, max(0.0, quantum_magnitude))

    # Wende Quanten-Faktor auf alle Scores an
    for score_entry in scores:
        original_score = float(score_entry.get("score", 0.0))
        score_entry["score"] = original_score * quantum_factor
        score_entry["quantum_factor"] = quantum_factor

    # === INTENTIONS-FAKTOR ANWENDEN ===
    intention_factors = {
        "healing": 1.272,  # √φ - Natürliche Wiederherstellung
        "manifestation": 1.618,  # φ  - Goldene Schöpfung
        "protection": 1.414,  # âˆš2 - Stabiler Schild
        "transformation": 2.236,  # √5 - Dynamische Veränderung
        "connection": 2.0,  # 2  - Perfekte Einheit
        "clearing": 1.732,  # √3 - Reinigung/Klärung
        "activation": 2.718,  # e  - Natürliches Erwachen
        "harmonization": 1.618,  # Ï†  - Perfekte Balance
    }

    intention_key = (intention or "").strip().lower()
    intention_factor = intention_factors.get(intention_key, 1.0)
    intention_active = intention_factor != 1.0

    # === KOHÄRENZ BERECHNEN (für jeden Score) ===
    import math as _math

    for score_entry in scores:
        # Kohärenz aus 4 Faktoren: resonance, entropy_alignment, reliability, personal_alignment
        factors = [
            float(score_entry.get("resonance", 0.5)),
            float(score_entry.get("entropy_alignment", 0.5)),
            float(score_entry.get("reliability", 1.0)),
            float(score_entry.get("personal_alignment", 1.0)),
        ]
        mean_f = sum(factors) / len(factors)
        variance_f = sum((x - mean_f) ** 2 for x in factors) / len(factors)
        std_dev_f = _math.sqrt(max(variance_f, 0.0))
        coherence = 1.0 / (1.0 + std_dev_f)
        score_entry["coherence"] = max(0.0, min(1.0, coherence))

    if intention_active:
        for score_entry in scores:
            original_score = float(score_entry.get("score", 0.0))
            # Sanfte Gewichtung: 80% Basis + 20% Intentions-Modulation
            weighted_score = original_score * (0.8 + 0.2 * intention_factor)
            score_entry["score"] = weighted_score
            score_entry["intention_factor"] = intention_factor
        # Neu sortieren nach gewichtetem Score
        scores.sort(key=lambda x: x.get("score", 0.0), reverse=True)

    if show_progress:
        _echo(f"[4/5] âœ“ {len(scores)} Scores berechnet")
        if modifiers["age_factor"] != 1.0:
            _echo(
                f"[4/5] âœ“ Alters-Faktor: {modifiers['age_factor']:.2f} (Alter: {client_age} Jahre)"
            )
        if active_modifiers:
            _echo(f"  ðŸ“Š Klienten-Modifikatoren aktiv: {', '.join(active_modifiers)}")
            _echo(f"     Kombinierter Faktor: {combined_modifier:.3f}")
        _echo(f"[4/5] âœ“ Quantum-Faktor: {quantum_factor:.4f}")
        if intention_active:
            _echo(
                f"[4/5] âœ“ Intention '{intention_key}' angewendet (Faktor: {intention_factor:.3f})"
            )

    influence_factors = _build_influence_factors(
        tcm_type,
        planet_type,
        profile_obj.image_signature,
    )

    if show_progress:
        _echo("[5/5] ðŸ“ Erstelle Report...")

    _echo("Morphic Engine V1 – Multiplex-Scan")
    _echo(f"Profil: {prof}")
    _echo(
        f"Klient: {first_name} {name}"
        + (f" ({client_age} Jahre)" if client_age > 0 else "")
    )
    if (focus or "").strip():
        _echo(f"Fokus: {focus}")
    if intention_active:
        _echo(f"Intention: {intention_key} (Faktor: {intention_factor:.3f})")
    if modifiers["age_factor"] != 1.0:
        _echo(f"Alters-Faktor: {modifiers['age_factor']:.2f}")
    _echo(f"Quantum-Faktor: {quantum_factor:.4f}")
    _echo(
        "Personalprofil: "
        f"Emotion={personal_profile['emotion']:.2f}, "
        f"Physisch={personal_profile['physisch']:.2f}, "
        f"Mental={personal_profile['mental']:.2f}, "
        f"Astral={personal_profile['astral']:.2f}"
    )
    _echo(f"Morphic field: {m_field:.4f}")
    _echo(f"h_level (Hardware): {h_level:.3f} [{src.name()} / profile={_profile}]")
    _echo(f"Holographic entropy: {client_entropy:.4f}")
    _echo("Heim signature:")
    _echo("  " + ", ".join(f"{x:.3f}" for x in heim_sig))

    _echo("")
    _echo("Top Items (NLS v2, personalisiert):")
    seen_labels = set()
    top_scores = []
    for entry in scores:
        label = entry["label"]
        if label in seen_labels:
            continue
        seen_labels.add(label)
        top_scores.append(entry)
        if len(top_scores) >= top_k:
            break
    for entry in top_scores:
        label = entry["label"]
        score = entry["score"]
        coherence = entry.get("coherence", 0.0)
        # Kohärenz-Symbol: ✓ bei > 0.7, ⚠ bei 0.4-0.7, ⚡ bei < 0.4
        coh_symbol = "âœ“" if coherence > 0.7 else ("âš " if coherence > 0.4 else "âš¡")
        _echo(f"  - {label}: score={score:.4f}, coherence={coherence:.0%} {coh_symbol}")

    # B.A.T. Subgruppen-Aggregation (nur für bat_ Profile)
    subgroup_data = None
    if prof.startswith("bat_"):
        try:
            from core.bat_report_aggregator import (
                aggregate_by_subgroup,
                format_subgroup_report,
                generate_subgroup_json,
            )

            aggregated = aggregate_by_subgroup(
                scores, top_subgroups=5, top_items_per_group=3
            )
            if aggregated:
                subgroup_data = generate_subgroup_json(
                    aggregated, include_remedies=True
                )
                report_text = format_subgroup_report(aggregated, include_remedies=True)
                try:
                    _echo(report_text)
                except UnicodeEncodeError:
                    # Fallback ohne Emojis für Batch-Modus
                    safe_text = report_text.replace("ðŸ’Š", "[R]")
                    _echo(safe_text)
        except ImportError as e:
            _echo(f"⚠ BAT-Aggregation nicht verfügbar: {e}")
        except Exception as e:
            _echo(f"âš  BAT-Report Fehler: {e}")

    synergy_results = None
    if synergy:
        # Verwende Fokus oder Fallback für allgemeine Analyse
        effective_focus = focus.strip() if focus.strip() else "Allgemeine Balance"

        try:
            from core.quantum_synergy import QuantumSynergyEngine

            _echo("")
            _echo("=" * 70)
            _echo("QUANTUM-SYNERGY ANALYSE")
            _echo("=" * 70)
            _echo(f"Fokus: {effective_focus}")
            _echo(f"Kombinations-Größe: {synergy_combos}")
            _echo(f"Threshold: {synergy_threshold}/10.0")
            _echo("")

            # Quantum-Synergy wie FRÜHER: Nutze gesamte Datenbank mit Fokus-Filterung
            # WICHTIG: Keine scan_results Filterung mehr - Engine nutzt volle Datenbank!
            engine = QuantumSynergyEngine()
            effective_threshold = float(synergy_threshold)
            # Reduziere Threshold bei größeren Kombinationen für bessere Ergebnisse
            if synergy_combos >= 4:
                effective_threshold = max(4.5, effective_threshold - 0.5)
                _echo(
                    f"   â†’ Threshold angepasst auf {effective_threshold:.1f} (Kombos >= 4)"
                )
            elif synergy_combos >= 3:
                effective_threshold = max(5.0, effective_threshold - 0.3)
                _echo(
                    f"   â†’ Threshold angepasst auf {effective_threshold:.1f} (Kombos >= 3)"
                )

            _echo(f"   → Nutze gesamte Datenbank mit Fokus-Filterung (wie früher)...")
            _echo("")

            synergy_results = engine.find_synergistic_triggers(
                focus=effective_focus,
                scan_results=None,  # <- KEINE Filterung - volle Datenbank wie frueher!
                combination_size=synergy_combos,
                top_n=10,
                threshold=effective_threshold,
            )

            if not synergy_results and effective_threshold > 4.0:
                fallback_threshold = max(4.0, effective_threshold - 1.5)
                _echo(
                    f"⚠ Keine Kombinationen über Threshold {effective_threshold:.1f} gefunden – "
                    f"versuche niedrigeren Threshold {fallback_threshold:.1f}..."
                )
                synergy_results = engine.find_synergistic_triggers(
                    focus=effective_focus,
                    scan_results=None,  # Volle Datenbank
                    combination_size=synergy_combos,
                    top_n=10,
                    threshold=fallback_threshold,
                )

            # Best-Effort-Fallback: Wenn weiterhin keine Kombinationen gefunden
            # wurden, führe eine Suche ohne Threshold aus und nimm die Top-5,
            # damit im Report trotzdem eine Quantum-Synergy-Sektion sichtbar ist.
            if not synergy_results:
                best_effort_threshold = 0.0
                _echo(
                    "ℹ Keine Kombinationen über regelbasierte Thresholds – "
                    "best-effort Suche ohne Threshold (Top-5 Kombinationen)..."
                )
                synergy_results = engine.find_synergistic_triggers(
                    focus=effective_focus,
                    scan_results=None,  # Volle Datenbank
                    combination_size=synergy_combos,
                    top_n=5,
                    threshold=best_effort_threshold,
                )

            if synergy_results:
                # HYBRID-ANSATZ: Kategorisiere nach Scan-Overlap
                scan_labels = set(entry["label"] for entry in top_scores[:32])

                primary_synergies = []  # Mind. 1 Item aus Scan
                secondary_synergies = []  # Rein fokus-basiert

                for combo_items, combo_score, details in synergy_results:
                    combo_labels = [item["label"] for item in combo_items]
                    overlap = len(set(combo_labels) & scan_labels)

                    if overlap >= 1:  # Mind. 1 Item aus aktuellem Scan
                        primary_synergies.append(
                            (combo_items, combo_score, details, overlap)
                        )
                    else:
                        secondary_synergies.append(
                            (combo_items, combo_score, details, overlap)
                        )

                _echo(
                    f"âœ“ {len(synergy_results)} synergistische Kombinationen gefunden"
                )
                _echo(f"  â†’ {len(primary_synergies)} basieren auf aktuellem Scan")
                _echo(
                    f"  â†’ {len(secondary_synergies)} sind erweiterte Fokus-Synergien"
                )
                _echo("")

                # Zeige Primary Synergies
                if primary_synergies:
                    _echo("=" * 70)
                    _echo("HAUPT-SYNERGIEN (basierend auf aktuellem Scan)")
                    _echo("=" * 70)
                    _echo("")

                    for i, (combo_items, combo_score, details, overlap) in enumerate(
                        primary_synergies, 1
                    ):
                        _echo(
                            f"#{i} - Synergy-Score: {combo_score:.2f}/10.0 [{overlap} Items aus Scan]"
                        )
                        _echo("-" * 70)
                        _echo("Items:")
                        for item in combo_items:
                            in_scan = "âœ“" if item["label"] in scan_labels else " "
                            _echo(f"  {in_scan} • {item['label']}")
                        _echo("")
                        _echo("Komponenten:")
                        _echo(
                            f"  Einzelwirkungen:      {details['individual_scores']:.2f}/10.0"
                        )
                        _echo(
                            f"  Resonanz-Verstärkung: {details['resonance']:.2f}/10.0"
                        )
                        _echo(f"  Frequenz-Harmonien:   {details['harmony']:.2f}/10.0")
                        _echo(
                            f"  Fokus-Relevanz:       {details['relevance']:.2f}/10.0"
                        )
                        _echo("")

                # Zeige Secondary Synergies (optional, nur Top 3)
                if secondary_synergies:
                    _echo("=" * 70)
                    _echo("ERWEITERTE FOKUS-SYNERGIEN (Top 3)")
                    _echo("=" * 70)
                    _echo("")

                    for i, (combo_items, combo_score, details, overlap) in enumerate(
                        secondary_synergies[:3], 1
                    ):
                        _echo(
                            f"#{i} - Synergy-Score: {combo_score:.2f}/10.0 [Fokus-basiert]"
                        )
                        _echo("-" * 70)
                        _echo("Items:")
                        for item in combo_items:
                            _echo(f"    • {item['label']}")
                        _echo("")
            else:
                _echo("âš  Keine synergistischen Kombinationen gefunden")
                _echo("")
        except ImportError:
            _echo("⚠ Quantum-Synergy Modul nicht verfügbar")
            _echo("")
        except Exception as exc:
            _echo(f"âš  Quantum-Synergy Fehler: {exc}")
            _echo("")

    # Export-Block für multiplex_scan
    if export is not None:
        client_info = {
            "name": name,
            "first_name": first_name,
            "birth_date": birth_date,
            "birth_place": birth_place,
        }

        # Baue Metadaten-Lookup, um Gruppen/Raten/Potenzen/Level aus den Kandidaten zu ziehen
        meta_by_label: Dict[str, Dict[str, object]] = {}
        used_groups: set[str] = set()
        for it in items:
            label_it = str(it.get("label", "")).strip()
            if not label_it or label_it in meta_by_label:
                continue
            meta_by_label[label_it] = it
            grp = str(it.get("group", "") or "").strip()
            if grp:
                used_groups.add(grp)

        def _as_rates(raw: Iterable[object] | None) -> List[float]:
            if not raw:
                return []
            try:
                return [float(x) for x in raw]
            except Exception:
                return []

        # De-Duplizierung: pro (label, group) nur den Top-Score behalten,
        # aber alle Potenzen als Liste sammeln (Referenz: Mustermann-Berichte
        # zeigen ein Item mit seiner Top-Potenz, nicht 40 Duplikate).
        sub_results_top: List[Dict[str, object]] = []
        _dedup_index: Dict[tuple[str, str], Dict[str, object]] = {}
        for entry in scores:
            label = str(entry.get("label", ""))
            if not label:
                continue
            meta = meta_by_label.get(label, {})
            group_val = str(meta.get("group", "") or "").strip()
            if group_val:
                used_groups.add(group_val)
            rates_vals = meta.get("rates") or entry.get("rates")
            potency_meta = meta.get("potency")
            level_meta = meta.get("level")
            desc_meta = meta.get("description") or entry.get("description")

            score_val = float(entry.get("score", 0.0) or 0.0)
            rates_list = _as_rates(rates_vals)

            potency_display = (
                str(potency_meta)
                if potency_meta not in (None, "")
                else _interpret_potency(score_val, label)
            )

            # 13-Ebenen-Resonanz: wenn sinnvoll vorhanden, diese als Ebene anzeigen,
            # sonst auf den bisherigen Level-Interpreter zurueckfallen.
            lvl_id, lvl_val, lvl_text, copen_rate = _rates_to_level_info(
                rates_list, label
            )
            if lvl_id > 0 and lvl_val > 0.0:
                level_display = lvl_text
            else:
                level_display = (
                    str(level_meta)
                    if level_meta not in (None, "")
                    else _interpret_level(score_val, group_val, label)
                )

            dedup_key = (label.casefold(), group_val.casefold())
            existing = _dedup_index.get(dedup_key)
            if existing is not None:
                # Hoeheren Score behalten; Potenz ergaenzen
                if score_val > float(existing.get("score", 0.0) or 0.0):
                    existing["score"] = score_val
                    existing["rates"] = rates_list
                    existing["potency"] = potency_display
                    existing["level"] = level_display
                    existing["copen_rate"] = float(copen_rate)
                    existing["reliability"] = float(
                        entry.get("reliability", 1.0) or 1.0
                    )
                    existing["personal_alignment"] = float(
                        entry.get("personal_alignment", 1.0) or 1.0
                    )
                pot_list = existing.setdefault("potencies", [])
                if potency_display and potency_display not in pot_list:
                    pot_list.append(potency_display)
                continue

            sub_entry: Dict[str, object] = {
                "label": label,
                "score": score_val,
                "rates": rates_list,
                "group": group_val,
                "potency": potency_display,
                "level": level_display,
                "copen_rate": float(copen_rate),
                "reliability": float(entry.get("reliability", 1.0) or 1.0),
                "personal_alignment": float(
                    entry.get("personal_alignment", 1.0) or 1.0
                ),
            }
            if desc_meta:
                sub_entry["description"] = str(desc_meta)
            sub_results_top.append(sub_entry)
            _dedup_index[dedup_key] = sub_entry

        # Sortiere deduplizierte Top-Liste nach Score absteigend
        sub_results_top.sort(
            key=lambda e: float(e.get("score", 0.0) or 0.0), reverse=True
        )

        # Vollständige Gruppenliste: Alle Profil-Gruppen + gefundene Gruppen
        all_groups = set(groups)  # Alle Gruppen aus dem Multiplex-Profil
        all_groups.update(used_groups)  # Plus alle gefundenen Gruppen

        sub_results = {
            "groups": sorted(g for g in all_groups if g),
            "method": "multiplex",
            "candidates": len(items),
            "top": sub_results_top,
        }

        # Erstelle Basis-Resonance-Map (vereinfacht für multiplex_scan)
        resonance_map = {}
        for i, entry in enumerate(top_scores[:7]):  # Top 7 für Basis-Systeme
            system_name = entry["label"].lower().replace(" ", "_").replace("-", "_")
            resonance_map[system_name] = entry["score"]

        synergy_export = None
        if synergy_results:
            synergy_export = []
            # Kategorisiere wie in Konsolen-Ausgabe
            scan_labels_export = set(entry["label"] for entry in top_scores[:32])

            for combo_items, combo_score, details in synergy_results:
                combo_labels_export = [item["label"] for item in combo_items]
                overlap_count = len(set(combo_labels_export) & scan_labels_export)
                category = "primary" if overlap_count >= 1 else "secondary"

                synergy_export.append(
                    {
                        "items": [
                            {
                                "label": item["label"],
                                "group": item.get("group", ""),
                                "in_scan": item["label"]
                                in scan_labels_export,  # NEU: Markiere Scan-Items
                            }
                            for item in combo_items
                        ],
                        "score": float(combo_score),
                        "category": category,  # NEU: primary oder secondary
                        "scan_overlap": overlap_count,  # NEU: Anzahl Items aus Scan
                        "components": {
                            "individual_scores": float(details["individual_scores"]),
                            "resonance": float(details["resonance"]),
                            "harmony": float(details["harmony"]),
                            "relevance": float(details["relevance"]),
                        },
                        "frequencies": [
                            float(f) for f in details.get("frequencies", [])
                        ],
                    }
                )

        # === REMEDY-SYNERGIEN BERECHNEN (für JSON-Export) ===
        remedy_synergies_export = []
        if sub_results_top:
            # Sammle alle Remedy-Items
            MAX_ITEMS_PER_GROUP = 5
            remedy_pool = []
            group_counts: Dict[str, int] = {}

            for entry in sub_results_top:
                g = str(entry.get("group", "") or "").strip()
                if not g:
                    continue
                if _is_remedy_group(g):
                    current_count = group_counts.get(g, 0)
                    if current_count < MAX_ITEMS_PER_GROUP:
                        remedy_pool.append(entry)
                        group_counts[g] = current_count + 1

            # Berechne Synergien
            if len(remedy_pool) >= 2:
                try:
                    remedy_synergy_results = analyze_remedy_synergies(
                        remedy_pool, max_results=20
                    )

                    # Konvertiere in Export-Format
                    for syn in remedy_synergy_results:
                        label = syn.get("label", "")
                        score = syn.get("score", 0.0)
                        rates = syn.get("rates", [])
                        synergies = syn.get("synergies", [])

                        # Extrahiere erste Synergy für vereinfachtes Format
                        if synergies:
                            partner = synergies[0]
                            remedy_synergies_export.append(
                                {
                                    "item1": label,
                                    "item2": partner.get("partner_label", ""),
                                    "synergy_score": partner.get("synergy_score", 0.0),
                                    "rate1": rates,
                                    "rate2": partner.get("partner_rates", []),
                                }
                            )
                except Exception as e:
                    _echo(f"âš  Remedy-Synergy Fehler: {e}")

        influence_scoring: Dict[str, object] | None = None
        if influence_compare:
            influence_items: List[Dict[str, object]] = []
            for entry in top_scores:
                label_it = str(entry.get("label", "")).strip()
                if not label_it:
                    continue
                score_val = float(entry.get("score", 0.0) or 0.0)
                meta_it = meta_by_label.get(label_it, {})
                group_val = str(meta_it.get("group", "") or "").strip()
                m = _compute_influence_multiplier_for_item(
                    group_val,
                    label_it,
                    influence_factors,
                )
                influence_items.append(
                    {
                        "label": label_it,
                        "group": group_val,
                        "score_base": score_val,
                        "multiplier": float(m),
                        "score_influenced": float(score_val * m),
                    }
                )

            influence_scoring = {
                "enabled": True,
                "mode": "tcm_organ_clock_v1",
                "max_delta": 0.03,
                "items": influence_items,
            }

        db_analysis_block: Dict[str, object] | None = None
        if db_analysis_mode:
            client_rate_block = _build_db_client_rate_block(client_info)
            hardware_block: Dict[str, object] = {
                "profile": _profile,
                "source": src.name(),
                "h_level": float(h_level),
            }
            config_block: Dict[str, object] = {
                "profile": prof,
                "k_total": int(k_total),
                "top_k": int(top_k),
                "intention": intention_key if intention_active else None,
                "intention_factor": intention_factor if intention_active else None,
            }
            client_rate_value = None
            try:
                client_rate_value = float(client_rate_block.get("value", 0.0))
            except Exception:
                client_rate_value = None
            db_items = _build_db_items_from_sub_results(
                sub_results_top, int(top_k), client_rate_value
            )
            summary_block = _build_db_analysis_summary(db_items)
            db_analysis_block = {
                "enabled": True,
                "engine": "bruce_copen_db_v1",
                "client_rate": client_rate_block,
                "hardware": hardware_block,
                "config": config_block,
                "items": db_items,
                "summary": summary_block,
            }

        morphic_field_block: Dict[str, object] | None = None
        morphic_axes_block: Dict[str, object] | None = None
        if morphic_field:
            try:
                numerical_sequence: List[float] = []
                for sub in sub_results_top:
                    try:
                        raw_rate = sub.get("copen_rate")
                        if raw_rate is None:
                            continue
                        rate_val = float(raw_rate)
                    except Exception:
                        continue
                    if rate_val != 0.0:
                        numerical_sequence.append(rate_val)

                states = generate_default_quantum_states()
                geo_form = (
                    mf_geometry or "flower_of_life"
                ).strip().lower() or "flower_of_life"
                intent = (
                    mf_intention or "harmonization"
                ).strip().lower() or "harmonization"
                use_hw_mod = bool(mf_use_hardware)

                mf_config = MorphicFieldConfig(
                    quantum_states=states,
                    numerical_sequence=numerical_sequence,
                    geometric_form=geo_form,
                    intention=intent,
                    use_hardware_modulation=use_hw_mod,
                    hardware_profile=_profile,
                    time=None,
                )
                metrics_score: float | None = None
                if use_hw_mod:
                    try:
                        metrics_score = float(h_level) * 10.0
                    except Exception:
                        metrics_score = None

                mf_result = calculate_morphic_field(mf_config, metrics_score)

                mf_strength_val = float(mf_result.field_strength)
                mf_coherence_val = float(mf_result.coherence)
                mf_freq_val = float(mf_result.resonance_frequency)

                status = "unbekannt"
                status_text = ""
                if mf_coherence_val >= 0.66:
                    status = "hoch"
                    status_text = (
                        "hohe Kohärenz des Feldes (gut abgestimmte Organisation)."
                    )
                elif mf_coherence_val >= 0.33:
                    status = "mittel"
                    status_text = (
                        "mittlere Kohärenz, Regulierung und Harmonisierung empfohlen."
                    )
                else:
                    status = "niedrig"
                    status_text = (
                        "verminderte Kohärenz, erhöhter Regulationsbedarf "
                        "und Folgesitzungen sinnvoll."
                    )

                morphic_field_block = {
                    "total_wave_function": float(mf_result.total_wave_function),
                    "quantum_component": float(mf_result.quantum_component),
                    "numerical_factor": float(mf_result.numerical_factor),
                    "geometric_factor": float(mf_result.geometric_factor),
                    "intention_factor": float(mf_result.intention_factor),
                    "hardware_factor": float(mf_result.hardware_factor)
                    if mf_result.hardware_factor is not None
                    else None,
                    "coherence": mf_coherence_val,
                    "resonance_frequency": mf_freq_val,
                    "field_strength": mf_strength_val,
                    "status": status,
                    "status_text": status_text,
                    "timestamp": float(mf_result.timestamp),
                }

                # Achsen-/Wirbelsäulenanalyse nur lesend aus den Top-Items ableiten
                axes_candidate = _build_morphic_axes_from_sub_results(sub_results_top)
                if isinstance(axes_candidate, dict) and axes_candidate.get("enabled"):
                    morphic_axes_block = axes_candidate
            except Exception:
                morphic_field_block = None
                morphic_axes_block = None

        export_data: Dict[str, object] = {
            "schema": "morphic_multiplex_scan",
            "schema_version": 1,
            "group": None,
            "use_hw": True,
            "use_hid": src.name() == "hid_sensor",
            "h_level": float(h_level),
            "focus": focus if focus else None,
            # === SCAN-PARAMETER (NEU) ===
            "profile": prof,  # Profil-Name (z.B. "gehirn_detailliert")
            "profile_groups_count": len(groups),  # Anzahl definierter Gruppen
            "intention": intention if intention and intention.strip() else None,
            "planet_type": planet_type if planet_type and planet_type.strip() else None,
            "focus_weighting": focus_weighting,
            # === PERSONALPROFIL-WERTE ===
            "personal_profile_values": {
                "emotion": p_emotion,
                "physisch": p_physisch,
                "mental": p_mental,
                "astral": p_astral,
            },
            # === ENTROPIE-KONFIGURATION ===
            "entropy_mode": mode,  # "enhanced" oder "legacy"
            "use_hybrid_entropy": use_hybrid_entropy,
            "analysis": {
                "rates": client_rates.tolist()
                if hasattr(client_rates, "tolist")
                else list(client_rates),
                "morphic_field": float(m_field),
                "holographic_entropy": float(client_entropy),
                "entropy_calibrated": float(
                    client_entropy * 0.247
                ),  # Approximation der Kalibrierung
                "heim_signature": [float(x) for x in heim_sig],
                "resonance_map": resonance_map,
            },
            "sub_results": sub_results,
            "nls_scores": [
                dict(entry) for entry in scores[:50]
            ],  # Erweiterte NLS-Daten
            "quantum_synergy": synergy_export,
            "remedy_synergies": remedy_synergies_export,  # Synergetische Remedy-Kombinationen
            # Zusätzliche Metadaten für Kompatibilität
            "command": "multiplex_scan",
            "hardware_profile": _profile,
            "hardware_source": src.name(),
            "client": client_info,
            "personal_profile": personal_profile,
            "focus": focus if focus and focus.strip() else "",
            "influence_factors": influence_factors,
        }

        if influence_scoring is not None:
            export_data["influence_scoring"] = influence_scoring

        if db_analysis_block is not None:
            export_data["db_analysis"] = db_analysis_block

        if morphic_field_block is not None:
            export_data["morphic_field"] = morphic_field_block

        if morphic_axes_block is not None:
            export_data["morphic_axes"] = morphic_axes_block

        # B.A.T. Subgruppen-Daten hinzufügen
        if subgroup_data is not None:
            export_data["bat_subgroups"] = subgroup_data

        try:
            json_path, html_path = _resolve_export_paths(
                export,
                client_info,
                "multiplex_scan",
                filename_suffix,
                scan_type,
                session_id,
            )
            _echo(f"Export-Basis (absolut): {json_path.parent}")
            txt_path = html_path.with_suffix(".txt")
            _echo(f"Export-Pfade: JSON -> {json_path}")
            _echo(f"Export-Pfade: HTML -> {html_path}")
            _echo(f"Export-Pfade: TXT  -> {txt_path}")
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            _atomic_write_text(json_path, json_str)
            # Verwende basic_html mit der neuen sub_results Struktur
            html = _sanitize_visible_text(_render_basic_html(export_data))
            _atomic_write_text(html_path, html)
            pdf_path = html_path.with_suffix(".pdf")
            write_text_pdf(pdf_path, html_path.stem, html_to_text(html_path))
            # TXT-Export erweitert für multiplex_scan mit Gruppierungen
            txt_lines = [
                "Morphic Engine V1 – Multiplex-Scan (TXT)",
                f"Klient: {first_name} {name} – {birth_date}, {birth_place}",
                f"Profil: {prof} | Hardware: {_profile} | Quelle: {src.name()}",
                f"Hardware-Level: {h_level:.3f} | Morphisches Feld: {m_field:.4f} | Entropie: {client_entropy:.4f}",
                f"Fokus: {focus}" if focus else "",
                "",
                "Einflussfaktoren:",
            ]

            # Optionale Kurzübersicht zur morphischen Feld-Analyse (neuer Engine-Block)
            mf_block_txt = export_data.get("morphic_field") or {}
            if isinstance(mf_block_txt, dict) and mf_block_txt:
                try:
                    mf_strength_txt = float(
                        mf_block_txt.get("field_strength", 0.0) or 0.0
                    )
                except Exception:
                    mf_strength_txt = 0.0
                try:
                    mf_coherence_txt = float(mf_block_txt.get("coherence", 0.0) or 0.0)
                except Exception:
                    mf_coherence_txt = 0.0
                try:
                    mf_freq_txt = float(
                        mf_block_txt.get("resonance_frequency", 0.0) or 0.0
                    )
                except Exception:
                    mf_freq_txt = 0.0

                txt_lines.append("")
                txt_lines.append("Morphische Feld-Analyse (Übersicht, experimentell):")
                txt_lines.append(
                    f"  Feldstärke: {mf_strength_txt:.4f} | Kohärenz: {mf_coherence_txt:.3f} | "
                    f"Resonanzfrequenz: {mf_freq_txt:.0f} Hz"
                )

                if mf_coherence_txt >= 0.66:
                    txt_lines.append(
                        "  Bewertung: hohe Kohärenz des Feldes (gut abgestimmte Organisation)."
                    )
                elif mf_coherence_txt >= 0.33:
                    txt_lines.append(
                        "  Bewertung: mittlere Kohärenz, Regulierung und Harmonisierung empfohlen."
                    )
                else:
                    txt_lines.append(
                        "  Bewertung: verminderte Kohärenz, erhöhter Regulationsbedarf und Folgesitzungen sinnvoll."
                    )

            # Experimentelle Wirbelsäulen- & Zahnachsen-Übersicht (nur wenn Block vorhanden ist)
            axes_block_txt = export_data.get("morphic_axes") or {}
            if isinstance(axes_block_txt, dict) and axes_block_txt.get("enabled"):
                spine_block_txt = axes_block_txt.get("spine") or {}
                dental_block_txt = axes_block_txt.get("dental") or {}

                if (isinstance(spine_block_txt, dict) and spine_block_txt) or (
                    isinstance(dental_block_txt, dict) and dental_block_txt
                ):
                    txt_lines.append("")
                    txt_lines.append("Wirbelsäulen- & Zahnachsen (experimentell):")

                # Wirbelsäule (gesamt + HWS-Schlüsselresonanz)
                if isinstance(spine_block_txt, dict) and spine_block_txt:
                    global_spine_txt = spine_block_txt.get("global") or {}
                    if isinstance(global_spine_txt, dict) and global_spine_txt:
                        try:
                            sp_items_txt = int(
                                global_spine_txt.get("items_total", 0) or 0
                            )
                        except Exception:
                            sp_items_txt = 0
                        try:
                            sp_max_txt = float(
                                global_spine_txt.get("score_max", 0.0) or 0.0
                            )
                        except Exception:
                            sp_max_txt = 0.0
                        try:
                            sp_mean_txt = float(
                                global_spine_txt.get("score_mean", 0.0) or 0.0
                            )
                        except Exception:
                            sp_mean_txt = 0.0

                        txt_lines.append(
                            f"  Wirbelsäule gesamt: Items={sp_items_txt}, Max-Score={sp_max_txt:.2f}, Mittelwert={sp_mean_txt:.2f}"
                        )

                    hws_block_txt = spine_block_txt.get("hws") or {}
                    if isinstance(hws_block_txt, dict):
                        top_hws_txt = hws_block_txt.get("top") or []
                        if isinstance(top_hws_txt, list) and top_hws_txt:
                            try:
                                top0_hws = top_hws_txt[0]
                                lbl_hws = str(top0_hws.get("label", "") or "").strip()
                                try:
                                    sc_hws = float(top0_hws.get("score", 0.0) or 0.0)
                                except Exception:
                                    sc_hws = 0.0
                                txt_lines.append(
                                    f"  HWS-Schlüsselresonanz: {lbl_hws or '-'} (Score {sc_hws:.2f})"
                                )
                            except Exception:
                                pass

                # Zahnachsen (gesamt)
                if isinstance(dental_block_txt, dict) and dental_block_txt:
                    global_dental_txt = dental_block_txt.get("global") or {}
                    if isinstance(global_dental_txt, dict) and global_dental_txt:
                        try:
                            de_items_txt = int(
                                global_dental_txt.get("items_total", 0) or 0
                            )
                        except Exception:
                            de_items_txt = 0
                        try:
                            de_max_txt = float(
                                global_dental_txt.get("score_max", 0.0) or 0.0
                            )
                        except Exception:
                            de_max_txt = 0.0
                        try:
                            de_mean_txt = float(
                                global_dental_txt.get("score_mean", 0.0) or 0.0
                            )
                        except Exception:
                            de_mean_txt = 0.0

                        txt_lines.append(
                            f"  Zahnachsen gesamt: Items={de_items_txt}, Max-Score={de_max_txt:.2f}, Mittelwert={de_mean_txt:.2f}"
                        )

            inf = influence_factors or {}
            tcm_block_txt = inf.get("tcm") or {}
            planet_block_txt = inf.get("planet") or {}
            organ_block_txt = inf.get("organ_clock") or {}
            image_block_txt = inf.get("image") or {}

            tcm_label_txt = str(tcm_block_txt.get("label", "")).strip()
            tcm_elem_txt = str(tcm_block_txt.get("element", "")).strip()
            if tcm_label_txt or tcm_elem_txt:
                if tcm_elem_txt and tcm_label_txt:
                    txt_lines.append(
                        f"TCM-Typ: {tcm_label_txt} (Element {tcm_elem_txt})"
                    )
                elif tcm_label_txt:
                    txt_lines.append(f"TCM-Typ: {tcm_label_txt}")
            else:
                txt_lines.append("TCM-Typ: nicht gesetzt")

            planet_label_txt = str(planet_block_txt.get("label", "")).strip()
            if planet_label_txt:
                txt_lines.append(f"Planetentyp: {planet_label_txt}")
            else:
                txt_lines.append("Planetentyp: nicht gesetzt")

            organ_seg_txt = str(organ_block_txt.get("segment", "")).strip()
            if organ_seg_txt:
                txt_lines.append(f"Organuhr: {organ_seg_txt}")
            else:
                txt_lines.append("Organuhr: neutral")

            img_present_txt = bool(image_block_txt.get("present", False))
            img_source_txt = str(image_block_txt.get("source", "")).strip() or "default"
            if img_present_txt:
                txt_lines.append(f"Bildsignatur: gesetzt (Quelle: {img_source_txt})")
            else:
                txt_lines.append("Bildsignatur: nicht gesetzt")

            if influence_scoring is not None and bool(influence_scoring.get("enabled")):
                organs_summary_txt: List[str] = []
                tcm_orgs_txt = str(tcm_block_txt.get("organs", "") or "").strip()
                if tcm_orgs_txt:
                    for part in tcm_orgs_txt.split(","):
                        part_str = part.strip()
                        if part_str:
                            organs_summary_txt.append(part_str)
                active_orgs_txt = organ_block_txt.get("active_organs") or []
                if isinstance(active_orgs_txt, (list, tuple)):
                    for o in active_orgs_txt:
                        if isinstance(o, str):
                            o_str = o.strip()
                            if o_str:
                                organs_summary_txt.append(o_str)
                uniq_orgs_txt: List[str] = []
                seen_txt: set[str] = set()
                for o in organs_summary_txt:
                    if not o:
                        continue
                    if o not in seen_txt:
                        seen_txt.add(o)
                        uniq_orgs_txt.append(o)
                if uniq_orgs_txt:
                    try:
                        max_delta_val_txt = float(
                            influence_scoring.get("max_delta", 0.0) or 0.0
                        )
                        max_pct_val_txt = int(round(max_delta_val_txt * 100.0))
                        if max_pct_val_txt <= 0:
                            max_pct_val_txt = 3
                    except Exception:
                        max_pct_val_txt = 3
                    joined_orgs_txt = ", ".join(uniq_orgs_txt)
                    txt_lines.append(
                        f"Influence-Scoring aktiv (max. +{max_pct_val_txt}% für Items zu: {joined_orgs_txt})."
                    )

            txt_lines.extend(
                [
                    "",
                    "Verwendete Gruppen:",
                    ", ".join(
                        _format_group_label(group_name)
                        for group_name in sorted(used_groups)
                    ),
                    "",
                    "Top-Resonanzen (NLS v2) - nach Gruppen:",
                ]
            )

            # Gruppiere Ausgabe nach Kategorien
            for group_name in sorted(used_groups):
                group_items = [e for e in top_scores if e.get("group") == group_name]
                if group_items:
                    txt_lines.append(f"\n{_format_group_label(group_name)}:")
                    for entry in group_items[:5]:  # Top 5 pro Gruppe
                        txt_lines.append(
                            f"- {entry['label']}: score={entry['score']:.4f}, rel={entry['reliability']:.2f}"
                        )

            if synergy_export:
                label_counts_txt: Dict[str, int] = {}
                combo_count_txt = len(synergy_export)
                for combo in synergy_export:
                    items = combo.get("items", []) or []
                    for item in items:
                        item_label = str(item.get("label", "")).strip()
                        if not item_label:
                            continue
                        label_counts_txt[item_label] = (
                            label_counts_txt.get(item_label, 0) + 1
                        )

                if label_counts_txt:
                    txt_lines.append("")
                    txt_lines.append(
                        "Quantum-Synergy – häufigste Trigger (regelbasiert):"
                    )
                    for label, count in sorted(
                        label_counts_txt.items(), key=lambda kv: (-kv[1], kv[0])
                    )[:5]:
                        txt_lines.append(
                            f"- {label} (in {count} von {combo_count_txt} Kombinationen)"
                        )

            # Optionale Bruce-Copen-DB-Analyse im TXT-Report, basierend auf db_analysis.summary
            db_block_txt = export_data.get("db_analysis") or {}
            if isinstance(db_block_txt, dict):
                db_summary_txt = db_block_txt.get("summary") or {}
            else:
                db_summary_txt = {}

            if isinstance(db_summary_txt, dict) and db_summary_txt.get(
                "resonance_count"
            ):
                try:
                    items_total_txt = int(db_summary_txt.get("items_total", 0) or 0)
                except Exception:
                    items_total_txt = 0
                try:
                    res_count_txt = int(db_summary_txt.get("resonance_count", 0) or 0)
                except Exception:
                    res_count_txt = 0

                top_res_txt = db_summary_txt.get("top_resonance") or []
                txt_lines.append("")
                txt_lines.append("Bruce-Copen-DB-Analyse (experimentell):")
                txt_lines.append(
                    f"Items mit Resonanz: {res_count_txt} von {items_total_txt}."
                )
                if isinstance(top_res_txt, list) and top_res_txt:
                    for idx, entry in enumerate(top_res_txt[:5], 1):
                        try:
                            label_tr = str(entry.get("label", "") or "").strip()
                            group_tr = str(entry.get("group", "") or "").strip()
                            score_raw = entry.get("resonance_score")
                            score_val = (
                                float(score_raw) if score_raw is not None else 0.0
                            )
                        except Exception:
                            continue
                        if group_tr:
                            line = f"{idx}. {label_tr} [{_format_group_label(group_tr)}] – Resonanz {score_val:.1f} / 100"
                        else:
                            line = f"{idx}. {label_tr} – Resonanz {score_val:.1f} / 100"
                        txt_lines.append(line)

            txt_content = _sanitize_visible_text(
                "\n".join(line for line in txt_lines if line)
            )
            _atomic_write_text(txt_path, txt_content)

            try:
                high_mid: List[Dict[str, object]] = []
                max_score_hm = 0.0
                try:
                    if sub_results_top:
                        max_score_hm = max(
                            float(e.get("score", 0.0) or 0.0) for e in sub_results_top
                        )
                    else:
                        max_score_hm = 0.0
                except Exception:
                    max_score_hm = 0.0

                if sub_results_top and max_score_hm > 0.0:
                    for e in sub_results_top:
                        try:
                            s_val = float(e.get("score", 0.0) or 0.0)
                        except Exception:
                            s_val = 0.0
                        rel = s_val / max_score_hm if max_score_hm > 0.0 else 0.0
                        if rel >= 0.66:
                            prio = "hoch"
                        elif rel >= 0.33:
                            prio = "mittel"
                        else:
                            prio = "niedrig"
                        if prio not in ("hoch", "mittel"):
                            continue
                        label_hm = str(e.get("label", "")).strip()
                        if not label_hm:
                            continue
                        try:
                            cr_val = float(e.get("copen_rate", 0.0) or 0.0)
                        except Exception:
                            cr_val = 0.0
                        high_mid.append(
                            {
                                "label": label_hm,
                                "copen_rate": cr_val,
                                "score": s_val,
                                "priority": prio,
                            }
                        )

                if high_mid:
                    high_mid_sorted = sorted(
                        high_mid,
                        key=lambda r: float(r.get("score", 0.0) or 0.0),
                        reverse=True,
                    )
                    labels_lines: List[str] = []
                    copen_lines: List[str] = []
                    for rec in high_mid_sorted:
                        labels_lines.append(str(rec.get("label", "")))
                        try:
                            cr_line = float(rec.get("copen_rate", 0.0) or 0.0)
                            if float(cr_line).is_integer():
                                copen_lines.append(f"{int(cr_line)}")
                            else:
                                copen_lines.append(f"{cr_line:.4f}")
                        except Exception:
                            copen_lines.append("0")

                    base_stem = txt_path.with_suffix("").name
                    labels_path = txt_path.with_name(
                        base_stem + "_labels_hoch_mittel.txt"
                    )
                    rates_path = txt_path.with_name(
                        base_stem + "_copen_hoch_mittel.txt"
                    )
                    if labels_lines:
                        _atomic_write_text(labels_path, "\n".join(labels_lines))
                    if copen_lines:
                        _atomic_write_text(rates_path, "\n".join(copen_lines))
            except Exception:
                pass

            ok_json = json_path.exists() and json_path.stat().st_size > 0
            ok_html = html_path.exists() and html_path.stat().st_size > 0
            ok_pdf = pdf_path.exists() and pdf_path.stat().st_size > 0
            ok_txt = txt_path.exists() and txt_path.stat().st_size > 0
            _echo(f"JSON geschrieben: {'OK' if ok_json else 'FEHLER'} -> {json_path}")
            _echo(f"HTML geschrieben: {'OK' if ok_html else 'FEHLER'} -> {html_path}")
            _echo(f"PDF geschrieben:  {'OK' if ok_pdf else 'FEHLER'} -> {pdf_path}")
            _echo(f"TXT geschrieben:  {'OK' if ok_txt else 'FEHLER'} -> {txt_path}")
            if ok_json:
                _echo(f"Export gespeichert: {json_path}")
            if ok_html:
                _echo(f"HTML-Report gespeichert: {html_path}")
            if ok_pdf:
                _echo(f"PDF-Report gespeichert: {pdf_path}")
            if ok_txt:
                _echo(f"TXT-Report gespeichert: {txt_path}")
            if ok_json:
                register_report_artifact(
                    json_path,
                    client_info,
                    "multiplex_scan_json",
                    label=f"Multiplex JSON {prof}",
                    session_id=session_id,
                    focus=focus,
                    config={
                        "command": "multiplex_scan",
                        "profile": prof,
                        "scan_type": scan_type,
                    },
                )
            if ok_html:
                register_report_artifact(
                    html_path,
                    client_info,
                    "multiplex_scan_html",
                    label=f"Multiplex HTML {prof}",
                    session_id=session_id,
                    focus=focus,
                    config={
                        "command": "multiplex_scan",
                        "profile": prof,
                        "scan_type": scan_type,
                    },
                )
            if ok_pdf:
                register_report_artifact(
                    pdf_path,
                    client_info,
                    "multiplex_scan_pdf",
                    label=f"Multiplex PDF {prof}",
                    session_id=session_id,
                    focus=focus,
                    config={
                        "command": "multiplex_scan",
                        "profile": prof,
                        "scan_type": scan_type,
                    },
                )
            if ok_txt:
                register_report_artifact(
                    txt_path,
                    client_info,
                    "multiplex_scan_txt",
                    label=f"Multiplex TXT {prof}",
                    session_id=session_id,
                    focus=focus,
                    config={
                        "command": "multiplex_scan",
                        "profile": prof,
                        "scan_type": scan_type,
                    },
                )

            if export_3d:
                try:
                    _echo("Generiere 3D-Export für Viewer...")
                    points_3d = []
                    for entry in scores:
                        pt_def = map_item_to_point(entry)
                        if pt_def:
                            points_3d.append(
                                {
                                    "id": pt_def.id,
                                    "label": entry["label"],
                                    "layer": pt_def.layer,
                                    "coords": pt_def.coords,
                                    "value": float(entry["score"]),
                                    "intensity": float(entry.get("reliability", 1.0))
                                    / 10.0,
                                    "group_hint": pt_def.group_hint,
                                }
                            )

                    if points_3d:
                        export_3d_file = json_path.with_name(
                            json_path.stem + "_3d_scan.json"
                        )
                        with open(export_3d_file, "w", encoding="utf-8") as f:
                            json.dump(
                                {
                                    "points": points_3d,
                                    "meta": {
                                        "client": f"{first_name} {name}",
                                        "profile": prof,
                                        "timestamp": time.time(),
                                    },
                                },
                                f,
                                indent=2,
                            )
                        register_report_artifact(
                            export_3d_file,
                            client_info,
                            "multiplex_scan_3d_json",
                            label=f"Multiplex 3D JSON {prof}",
                            session_id=session_id,
                            focus=focus,
                            config={
                                "command": "multiplex_scan",
                                "profile": prof,
                                "scan_type": scan_type,
                            },
                        )
                        _echo(f"âœ“ 3D-Daten gespeichert: {export_3d_file}")
                    else:
                        _echo(
                            "âš  Keine 3D-Punkte gemappt (Daten vorhanden aber ohne Mapping)."
                        )
                except Exception as e3d:
                    _echo(f"âš  Fehler beim 3D-Export: {e3d}")

        except Exception as exc:
            _echo(f"Export fehlgeschlagen: {exc}")


@field_app.command("workflow-scan")
def workflow_scan(
    name: str = typer.Argument(..., help="Nachname des Klienten"),
    first_name: str = typer.Argument(..., help="Vorname des Klienten"),
    birth_date: str = typer.Option(..., "--birth-date", "-d", help="Geburtsdatum"),
    birth_place: str = typer.Option(..., "--birth-place", "-p", help="Geburtsort"),
    focus: str = typer.Option("", "--focus", "-f", help="Fokus/Symptom"),
    intention: str = typer.Option("harmonization", "--intention", help="Intention"),
    profile_level: int = typer.Option(
        3, "--level", "-l", min=1, max=5, help="Profil-Level 1-5"
    ),
    top_n: int = typer.Option(5, "--top-n", "-n", min=3, max=10, help="Top-N Profile"),
    image_path: str = typer.Option("", "--image", help="Klienten-Bild (JPG/PNG)"),
    planet_type: str = typer.Option("", "--planet-type", help="Geburtsplanet"),
    p_emotion: float = typer.Option(0.5, "--p-emotion", min=0.0, max=1.0),
    p_physisch: float = typer.Option(0.5, "--p-physisch", min=0.0, max=1.0),
    p_mental: float = typer.Option(0.5, "--p-mental", min=0.0, max=1.0),
    p_astral: float = typer.Option(0.5, "--p-astral", min=0.0, max=1.0),
    export: str = typer.Option(
        "C:\\Benutzer_Archive_Start", "--export", "-e", help="Export-Verzeichnis"
    ),
    harmonize: bool = typer.Option(
        False, "--harmonize/--no-harmonize", help="Harmonisierung starten"
    ),
    harmonize_duration: int = typer.Option(
        1, "--harm-duration", min=1, max=60, help="Harmonisierungs-Dauer (Min)"
    ),
) -> None:
    """Fuehrt den 12-Step Workflow-Scan nach Radi144-Blueprint aus.

    Sequenzieller Ablauf: Init -> Eingabe -> Signatur -> Fokus -> EMF ->
    Amplifier -> Palette -> Matrix -> Quantum -> Post-Processing ->
    Export -> Harmonisierung

    Beispiel:
        python -m apps.cli.main field workflow-scan "Test" "Klaus" -d 01011970 -p Berlin --focus Lunge
        python -m apps.cli.main field workflow-scan "Test" "Klaus" -d 01011970 -p Berlin --harmonize --harm-duration 5
    """
    from apps.cli.workflow.orchestrator import run_workflow

    run_workflow(
        name=name,
        first_name=first_name,
        birth_date=birth_date,
        birth_place=birth_place,
        focus=focus,
        intention=intention,
        profile_level=profile_level,
        top_n=top_n,
        image_path=image_path,
        planet_type=planet_type,
        p_emotion=p_emotion,
        p_physisch=p_physisch,
        p_mental=p_mental,
        p_astral=p_astral,
        export_dir=export,
        harmonize=harmonize,
        harmonize_duration=harmonize_duration,
        verbose=True,
    )
