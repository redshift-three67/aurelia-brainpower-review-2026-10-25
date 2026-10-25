"""Report rendering and harmonization helpers."""

from __future__ import annotations

import html
from typing import Dict, List

from core.compliance.safety import wellbeing_html_block, wellbeing_txt_block


_HTML_HEAD = (
    "<!DOCTYPE html><html lang='de'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    "<title>Resonanzanalyse – Report</title><style>"
    "*{margin:0;padding:0;box-sizing:border-box;}"
    ":root{color-scheme:light;}"
    "body{font-family:Georgia,'Times New Roman',serif;background:linear-gradient(135deg,#EFF4F7 0%,#E8EEF2 50%,#E3EAEE 100%);"
    "min-height:100vh;padding:36px 20px 48px;font-size:11pt;line-height:1.72;color:#24323E;}"
    ".container{max-width:1080px;margin:0 auto;background:rgba(255,255,255,0.84);backdrop-filter:blur(20px);"
    "padding:36px;border-radius:24px;box-shadow:0 10px 28px rgba(86,117,141,0.10),0 2px 8px rgba(0,0,0,0.04);"
    "border:1px solid rgba(255,255,255,0.8);}"
    ".report-shell{display:grid;gap:22px;}"
    ".report-block{background:rgba(255,255,255,0.78);border:1px solid rgba(115,149,175,0.12);border-radius:18px;padding:24px;}"
    ".report-shell h1,.report-shell h2,.report-shell h3,.report-shell p,.report-shell ul,.report-shell ol,.report-shell pre,.report-shell table{margin-top:0;margin-bottom:18px;}"
    "h1{font-size:22pt;font-weight:600;margin:0 0 20px;color:#24323E;padding-bottom:16px;"
    "border-bottom:2px solid rgba(115,149,175,0.24);letter-spacing:-0.3px;}"
    "h2{font-size:16pt;font-weight:600;margin:30px 0 16px;color:#35506A;"
    "padding:13px 20px;background:linear-gradient(135deg,rgba(115,149,175,0.08),rgba(186,206,220,0.14));"
    "border-radius:12px;border-left:4px solid #7395AF;}"
    "h3{font-size:13pt;font-weight:600;margin:22px 0 12px;color:#4A6278;}"
    "table{border-collapse:separate;border-spacing:0;width:100%;font-size:10pt;margin:22px 0;"
    "background:rgba(255,255,255,0.66);border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(107,165,208,0.06);}"
    "th,td{padding:13px 16px;text-align:left;border-bottom:1px solid rgba(107,165,208,0.1);vertical-align:top;}"
    "th{background:linear-gradient(135deg,#7395AF,#88A6BB);color:#FFFFFF;font-weight:600;text-transform:uppercase;font-size:9pt;letter-spacing:0.5px;}"
    "tbody tr{transition:background 0.2s ease;}tbody tr:hover{background:rgba(107,165,208,0.06);}"
    "tbody tr:last-child td{border-bottom:none;}"
    ".badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:9pt;font-weight:600;letter-spacing:0.3px;}"
    ".prio-high{background:linear-gradient(135deg,#FF6B9D,#FFA07A);color:#FFF;box-shadow:0 2px 8px rgba(255,107,157,0.3);}"
    ".prio-mid{background:linear-gradient(135deg,#FFB347,#FFCC80);color:#FFF;box-shadow:0 2px 8px rgba(255,179,71,0.3);}"
    ".prio-low{background:linear-gradient(135deg,#77DD77,#98D8C8);color:#FFF;box-shadow:0 2px 8px rgba(119,221,119,0.3);}"
    ".note{font-size:9pt;color:#5D6D7E;margin-top:12px;padding:12px 16px;background:rgba(107,165,208,0.06);border-radius:10px;border-left:3px solid #A7C7E7;}"
    ".header-info{background:linear-gradient(135deg,rgba(186,206,220,0.18),rgba(115,149,175,0.10));"
    "padding:22px;border-radius:16px;margin-bottom:0;border:1px solid rgba(107,165,208,0.16);box-shadow:0 4px 14px rgba(107,165,208,0.08);}"
    ".header-info p{margin:10px 0;color:#34495E;font-size:10.5pt;}"
    "td.rates{font-family:'Fira Code','Consolas','Monaco',monospace;font-size:9pt;color:#6BA5D0;font-weight:500;}"
    "td.description{font-size:9.5pt;color:#5D6D7E;max-width:350px;line-height:1.5;word-wrap:break-word;white-space:normal;}"
    "pre{white-space:pre-wrap;word-wrap:break-word;background:rgba(255,255,255,0.50);padding:18px;border-radius:12px;border:1px solid rgba(107,165,208,0.12);max-height:min(70vh,960px);overflow:auto;}"
    "p{word-wrap:break-word;white-space:normal;}.summary,.focus-text{word-wrap:break-word;white-space:normal;line-height:1.6;}"
    "div.scroll-section{overflow-y:auto;max-height:min(70vh,960px);border:1px solid rgba(107,165,208,0.15);border-radius:12px;background:rgba(255,255,255,0.4);"
    "box-shadow:inset 0 2px 8px rgba(107,165,208,0.05);}"
    ".scroll-section table{margin:0;border-radius:0;box-shadow:none;}"
    ".visible-limit-note{margin-bottom:8px;}"
    "@media print{body{background:#FFF!important;padding:10px!important;}.container{background:#FFF!important;box-shadow:none!important;backdrop-filter:none!important;border:none!important;}"
    "h1{font-size:18pt!important;}h2{font-size:14pt!important;background:#F0F8FF!important;}h3{font-size:12pt!important;}"
    "table{font-size:9pt!important;box-shadow:none!important;}th{background:#6BA5D0!important;-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important;}"
    ".badge{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important;}}"
    "</style></head><body><div class='container'><main class='report-shell'>"
)

_HTML_FOOT = "</main></div></body></html>"


def _generate_harmonization_steps(
    group_buckets: Dict[str, List[Dict[str, object]]], max_score: float
) -> List[str]:
    steps = []
    for group, items in sorted(group_buckets.items()):
        if not items:
            continue
        group_label = _format_group_label(group)
        group_peak = max((_as_float(item.get("score")) for item in items), default=0.0)
        group_ratio = group_peak / max_score if max_score > 0.0 else 0.0
        if group_ratio >= 0.8:
            steps.append(
                f"{group_label}: hoch priorisiert harmonisieren ({len(items)} Treffer)."
            )
        elif group_ratio >= 0.45:
            steps.append(f"{group_label}: sanft ausgleichen ({len(items)} Treffer).")
        else:
            steps.append(f"{group_label}: beobachten ({len(items)} Treffer).")
    return steps or ["Keine spezifischen Harmonisierungsschritte abgeleitet."]


def _escape(value: object) -> str:
    return html.escape(str(value if value is not None else ""))


def _as_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def _format_float(value: object, digits: int = 4) -> str:
    return f"{_as_float(value):.{digits}f}"


def _format_rates(value: object) -> str:
    if not isinstance(value, (list, tuple)):
        return "-"
    numbers = []
    for item in value:
        try:
            numbers.append(f"{float(item):.2f}")
        except (TypeError, ValueError):
            numbers.append(str(item))
    return "[ " + " - ".join(numbers) + " ]" if numbers else "-"


def _format_group_label(group: object) -> str:
    raw = str(group or "").strip()
    if not raw:
        return "Ohne Gruppe"
    normalized = raw.replace("-", "_")
    parts = [part for part in normalized.split("_") if part]
    if not parts:
        return raw
    abbreviations = {
        "bat": "BAT",
        "bws": "BWS",
        "dna": "DNA",
        "emf": "EMF",
        "fdok": "FDOK",
        "hws": "HWS",
        "lm": "LM",
        "nls": "NLS",
        "tcm": "TCM",
    }
    return " ".join(
        abbreviations.get(part.lower(), part.capitalize()) for part in parts
    )


def _priority_for_item(item: Dict[str, object], max_score: float) -> tuple[str, str]:
    raw = str(item.get("priority", "") or "").strip().lower()
    if raw in {"hoch", "high"}:
        return "hoch", "prio-high"
    if raw in {"mittel", "mid", "medium"}:
        return "mittel", "prio-mid"
    if raw in {"niedrig", "low"}:
        return "niedrig", "prio-low"

    score = _as_float(item.get("score"))
    rel = score / max_score if max_score > 0.0 else 0.0
    if rel >= 0.66:
        return "hoch", "prio-high"
    if rel >= 0.33:
        return "mittel", "prio-mid"
    return "niedrig", "prio-low"


def _priority_level(score: float, group_max: float) -> tuple[int, str]:
    if group_max <= 0.0:
        return 1, "prio-low"
    level = max(1, min(10, int(round((score / group_max) * 10.0))))
    if level >= 8:
        return level, "prio-high"
    if level >= 5:
        return level, "prio-mid"
    return level, "prio-low"


def _intensity_pair(score: float, global_max: float, group_max: float) -> str:
    global_rel = score / global_max if global_max > 0.0 else 0.0
    group_rel = score / group_max if group_max > 0.0 else 0.0
    return f"{global_rel:.2f} / {group_rel:.2f}"


def _score_intensity_note(global_max: float, group_max: float) -> str:
    return (
        "<p class='note' style='font-size:10px; color:#555; margin-top:4px; padding:4px; "
        "background:#f9f9f9; border-left:3px solid #5cb85c;'>"
        "<strong>Score & Intensität:</strong> Score = Absolute Resonanzstärke (0-10). "
        f"Intensität: erster Wert relativ zum stärksten Fullbody-Treffer (global, Max: {global_max:.2f}), "
        f"zweiter Wert relativ zum Gruppen-Maximum (lokal, Max: {group_max:.2f}). "
        "<strong>Priorität:</strong> Level 1-10 relativ zum Gruppen-Maximum, wobei 10 = höchste Priorität. "
        "<strong>Interpretation:</strong> Score &gt;7 = sehr hoch, 5-7 = hoch, 3-5 = mittel, "
        "1-3 = niedrig, &lt;1 = sehr niedrig. Intensität &gt;0.8 = sehr stark, 0.6-0.8 = stark, "
        "0.4-0.6 = mittel, 0.2-0.4 = schwach, &lt;0.2 = sehr schwach."
        "</p>"
    )


def _synergy_rating(score: float) -> str:
    if score >= 8.0:
        return "sehr stark"
    if score >= 7.0:
        return "hoch"
    if score >= 5.0:
        return "mittel"
    if score >= 3.0:
        return "niedrig"
    return "sehr niedrig"


def _synergy_interpretation(
    score: float, components: Dict[str, object], focus_text: str
) -> str:
    """Erzeugt einen regelbasierten Interpretationstext fuer eine Synergy-Karte."""
    if score >= 7.0:
        rating = "Gute Synergien \u2013 Kombination priorisieren."
    elif score >= 5.0:
        rating = "Mittlere Synergien \u2013 Kombination beobachten."
    else:
        rating = "Niedrige Synergien \u2013 Kombination nicht vordringlich."

    parts = [rating]
    if isinstance(components, dict):
        comp_labels = {
            "individual_scores": "Einzelwirkungen",
            "resonance": "Resonanz-Verstaerkung",
            "harmony": "Frequenz-Harmonien",
            "relevance": "Fokus-Relevanz",
        }
        for key, label in comp_labels.items():
            if key in components:
                val = _as_float(components.get(key))
                parts.append(f"{label}: {_synergy_rating(val)}")

    if focus_text:
        parts.append(
            f"Die Kombination beruehrt den Fokus \u201e{focus_text}\u201c eher indirekt; "
            "im Vordergrund steht die Achse Immunsystem/Entzuendung."
        )
    else:
        parts.append("Kein spezifischer Fokus gesetzt.")
    return ", ".join(parts) + "."


def _group_top_items(
    top_items: List[Dict[str, object]],
) -> Dict[str, List[Dict[str, object]]]:
    buckets: Dict[str, List[Dict[str, object]]] = {}
    for item in top_items:
        group = str(item.get("group", "") or "ohne_gruppe").strip() or "ohne_gruppe"
        buckets.setdefault(group, []).append(item)
    for group_items in buckets.values():
        group_items.sort(key=lambda row: _as_float(row.get("score")), reverse=True)
    return dict(sorted(buckets.items(), key=lambda row: row[0]))


def _top_items_from_export(export_data: Dict[str, object]) -> List[Dict[str, object]]:
    sub_results = export_data.get("sub_results") or {}
    if isinstance(sub_results, dict) and isinstance(sub_results.get("top"), list):
        items = [dict(item) for item in sub_results["top"] if isinstance(item, dict)]
    else:
        top_scores = export_data.get("top_scores")
        items = (
            [dict(item) for item in top_scores if isinstance(item, dict)]
            if isinstance(top_scores, list)
            else []
        )
    return items


# Maximale Anzahl Items pro Subgruppe (wie Mustermann-Referenz: ~30 pro grosser Gruppe)
_MAX_ITEMS_PER_GROUP = 30
# Maximale Items in der Top-Resonanzwerte-Uebersichtstabelle (wie Mustermann: 7)
_MAX_TOP_RESONANZ_ITEMS = 7
_CLIENT_VISIBLE_LIST_LIMIT = 21
_VISIBLE_ROW_HEIGHT_PX = 38
_VISIBLE_CHROME_HEIGHT_PX = 96


def _visible_list_limit(
    item_count: int, visible_limit: int = _CLIENT_VISIBLE_LIST_LIMIT
) -> int:
    if item_count <= 0:
        return 0
    return min(item_count, visible_limit)


def _render_visible_scroll_section(
    inner_html: str,
    item_count: int,
    *,
    label: str = "Liste",
    visible_limit: int = _CLIENT_VISIBLE_LIST_LIMIT,
    row_height_px: int = _VISIBLE_ROW_HEIGHT_PX,
    chrome_height_px: int = _VISIBLE_CHROME_HEIGHT_PX,
    attribute_quote: str = '"',
) -> str:
    visible_rows = _visible_list_limit(item_count, visible_limit)
    if item_count <= visible_limit or visible_rows <= 0:
        return inner_html
    max_height = chrome_height_px + (visible_rows * row_height_px)
    quote = "'" if attribute_quote == "'" else '"'
    return (
        f"<p class='note visible-limit-note'>{_escape(label)}: {item_count} Eintraege, "
        f"davon {visible_rows} direkt sichtbar. Weitere Eintraege sind per Scrollen erreichbar.</p>"
        f"<div class='scroll-section' data-visible-limit={quote}{visible_rows}{quote} "
        f"style='max-height:{max_height}px;overflow-y:auto;border:1px solid rgba(107,165,208,0.15);"
        "border-radius:12px;background:rgba(255,255,255,0.4);box-shadow:inset 0 2px 8px rgba(107,165,208,0.05);'>"
        f"{inner_html}</div>"
    )


def _normalize_scores(
    items: List[Dict[str, object]], target_max: float = 10.0
) -> List[Dict[str, object]]:
    """Normalisiert die Scores auf eine 0-target_max Skala.

    Die Roh-Scores aus der NLS-Engine sind oft stark komprimiert (z.B. 0-5 statt 0-10).
    Diese Funktion skaliert sie so, dass der hoechste Score ~target_max erreicht
    und die Verteilung gestreckt wird (Power-Normalisierung fuer bessere Entzerrung).

    Referenz: Mustermann-Berichte haben Score-Range 0-8.96 (ca. 0-9).
    """
    if not items:
        return items
    scores = [_as_float(it.get("score")) for it in items]
    raw_max = max(scores) if scores else 1.0
    if raw_max <= 0.0:
        return [dict(item) for item in items]
    # Power-Normalisierung: score^0.7 skaliert auf target_max
    # Der Exponent 0.7 streckt niedrige Werte und komprimiert hohe,
    # was eine bessere Entzerrung der Score-Verteilung bewirkt.
    power = 0.7
    normalized_items: List[Dict[str, object]] = []
    for it in items:
        item = dict(it)
        raw = _as_float(item.get("score"))
        normalized = (raw / raw_max) ** power * target_max
        if "_raw_score" not in item:
            item["_raw_score"] = raw
        item["score"] = round(normalized, 4)
        normalized_items.append(item)
    return normalized_items


def _limit_group_items(
    group_buckets: Dict[str, List[Dict[str, object]]],
    max_per_group: int = _MAX_ITEMS_PER_GROUP,
) -> Dict[str, List[Dict[str, object]]]:
    """Begrenzt die Items pro Gruppe auf max_per_group (Top-N je Gruppe)."""
    limited: Dict[str, List[Dict[str, object]]] = {}
    for group, items in group_buckets.items():
        items_sorted = sorted(
            items, key=lambda row: _as_float(row.get("score")), reverse=True
        )
        limited[group] = items_sorted[:max_per_group]
    return dict(sorted(limited.items(), key=lambda row: row[0]))


def _render_basic_html(export_data: Dict[str, object]) -> str:
    client = export_data.get("client") or {}
    if not isinstance(client, dict):
        client = {}
    first_name = html.escape(str(client.get("first_name", "") or ""))
    last_name = html.escape(str(client.get("name", "") or ""))
    birth_date = html.escape(str(client.get("birth_date", "") or ""))
    birth_place = html.escape(str(client.get("birth_place", "") or ""))
    command = html.escape(str(export_data.get("command", "analyze") or "analyze"))
    focus = html.escape(str(export_data.get("focus", "") or ""))
    hardware_profile = html.escape(str(export_data.get("hardware_profile", "") or ""))
    hardware_source = html.escape(str(export_data.get("hardware_source", "") or ""))
    h_level = _as_float(export_data.get("h_level"))

    analysis = export_data.get("analysis") or export_data.get("metrics") or {}
    if not isinstance(analysis, dict):
        analysis = {}
    sub_results = export_data.get("sub_results") or {}
    top_items = _top_items_from_export(export_data)
    # Score-Normalisierung auf 0-10 Skala (wie Mustermann-Referenz)
    top_items = _normalize_scores(top_items, target_max=10.0)
    max_score = max((_as_float(item.get("score")) for item in top_items), default=0.0)
    group_buckets = _limit_group_items(_group_top_items(top_items))

    rates = _format_rates(analysis.get("rates"))
    heim = _format_rates(analysis.get("heim_signature"))
    m_field = _as_float(analysis.get("morphic_field"))
    entropy = _as_float(analysis.get("holographic_entropy"))
    entropy_cal = _as_float(analysis.get("entropy_calibrated"), entropy)

    parts: List[str] = [_HTML_HEAD]
    parts.append("<section class='report-block'>")
    parts.append("<h1>Resonanzanalyse – Report</h1>")
    parts.append("<div class='header-info'>")
    parts.append(
        f"<p><b>Klient:</b> {first_name} {last_name} – {birth_date}, {birth_place}</p>"
    )
    parts.append(
        f"<p><b>Modus:</b> {command} | <b>Hardware-Profil:</b> {hardware_profile or '-'} | "
        f"<b>Quelle:</b> {hardware_source or '-'}</p>"
    )
    summary = (
        f"<p><b>Hardware-Level:</b> {h_level:.3f} | "
        f"<b>Morphisches Feld:</b> {m_field:.4f} | "
        f"<b>Entropie(kal):</b> {entropy_cal:.4f}"
    )
    if focus:
        summary += f" | <b>Fokus:</b> {focus}"
    summary += "</p>"
    parts.append(summary)
    parts.append("</div>")
    parts.append("</section>")
    parts.append(wellbeing_html_block())

    morphic_field = export_data.get("morphic_field") or {}
    if isinstance(morphic_field, dict) and morphic_field:
        field_strength = morphic_field.get(
            "field_strength", morphic_field.get("strength", "")
        )
        coherence = morphic_field.get("coherence", "")
        frequency = morphic_field.get(
            "resonance_frequency", morphic_field.get("frequency", "")
        )
        parts.append("<h2>Morphische Feld-Analyse (Übersicht, experimentell)</h2>")
        parts.append(
            f"<p><b>Feldstärke:</b> {_escape(field_strength) or '-'} | "
            f"<b>Kohärenz:</b> {_escape(coherence) or '-'} | "
            f"<b>Resonanzfrequenz:</b> {_escape(frequency) or '-'}</p>"
        )
        coherence_value = _as_float(coherence, 0.0)
        if coherence_value >= 0.5:
            parts.append(
                "<p>Das morphische Feld zeigt eine mittlere bis stabile Kohärenz. Harmonisierung kann zur Stabilisierung priorisierter Resonanzen genutzt werden.</p>"
            )
        else:
            parts.append(
                "<p>Das morphische Feld zeigt eine verminderte Kohärenz. Gezielte Harmonisierung und Folgesitzungen werden empfohlen.</p>"
            )

    influence = export_data.get("influence_factors") or {}
    if isinstance(influence, dict) and influence:
        organ = influence.get("organ_clock") or {}
        image_block = influence.get("image") or {}
        parts.append("<h2>Einflussfaktoren</h2>")
        if isinstance(organ, dict) and organ:
            organ_label = organ.get("label") or organ.get("organ") or "-"
            time_window = organ.get("time_window") or organ.get("window") or "-"
            parts.append(
                f"<p><b>Organuhr:</b> {_escape(time_window)} {_escape(organ_label)}</p>"
            )
        if isinstance(image_block, dict):
            img_text = "gesetzt" if image_block.get("present") else "nicht gesetzt"
            parts.append(f"<p><b>Bildsignatur:</b> {img_text}</p>")

    parts.append("<h2>Deutung des gezeigten Laufs</h2>")
    if top_items:
        high_or_mid = []
        for item in top_items[:12]:
            prio_txt, _prio_cls = _priority_for_item(item, max_score)
            if prio_txt in {"hoch", "mittel"}:
                high_or_mid.append(
                    f"{_escape(item.get('label'))} ({_format_float(item.get('score'), 2)}, {prio_txt})"
                )
        interpretation = [
            f"Fokus: {focus or '-'}",
            "",
            "Top-Belastungen und Resonanzen",
            ", ".join(high_or_mid)
            if high_or_mid
            else "Keine hoch/mittel priorisierten Top-Treffer im Export gefunden.",
            "",
            "Vorgehen",
            "Die aufgeführten Resonanzen sollten im Kontext des Fokus und der fachlichen Situation geprüft und bei Bedarf in einem Feinscan vertieft werden.",
        ]
        parts.append(f"<pre>{'<br>'.join(interpretation)}</pre>")
    else:
        parts.append("<p>Keine Top-Resonanzen im Export enthalten.</p>")

    groups = sub_results.get("groups", []) if isinstance(sub_results, dict) else []
    if isinstance(groups, list) and groups:
        parts.append("<h3>Verwendete Subgruppen</h3>")
        group_labels = [
            f"<span title='{_escape(group)}' data-group='{_escape(group)}'>{_escape(_format_group_label(group))}</span>"
            for group in groups
        ]
        parts.append(f"<p>{', '.join(group_labels)}</p>")

    if focus:
        parts.append("<h2>Fokus / Symptom</h2>")
        parts.append(f"<p class='focus-text'>{focus}</p>")

    parts.append("<h2>Resonanzanalyse</h2>")
    parts.append("<h3>Basis-Metriken</h3>")
    parts.append(
        f"<p><b>Raten:</b> {rates}<br><b>Morphisches Feld:</b> {m_field:.4f} | "
        f"<b>Entropie (roh):</b> {entropy:.4f} | <b>Entropie (kal):</b> {entropy_cal:.4f}<br>"
        f"<b>Heim-Signatur:</b> {heim}</p>"
    )

    parts.append("<h3>Resonanzwerte</h3>")
    parts.append("<table><tr><th>System</th><th>Score</th><th>Prioritaet</th></tr>")
    for item in top_items[:_MAX_TOP_RESONANZ_ITEMS]:
        prio_txt, prio_cls = _priority_for_item(item, max_score)
        parts.append(
            "<tr>"
            f"<td>{_escape(item.get('label'))}</td>"
            f"<td>{_format_float(item.get('score'))}</td>"
            f"<td><span class='badge {prio_cls}'>{prio_txt}</span></td>"
            "</tr>"
        )
    parts.append("</table>")
    parts.append(
        "<p class='note'>Priorität bezieht sich auf die relative Höhe des jeweiligen Scores innerhalb dieses Laufs.</p>"
    )

    if group_buckets:
        parts.append("<h2>Fullbody-Subgruppen – multiplex</h2>")
        for group, items in group_buckets.items():
            group_max = max(
                (_as_float(item.get("score")) for item in items), default=0.0
            )
            parts.append(
                f"<h3 title='{_escape(group)}' data-group='{_escape(group)}'>{_escape(_format_group_label(group))}</h3>"
            )
            table_parts = [
                "<table><tr><th>Label</th><th>Score</th><th>Intensität (global/gruppe)</th>"
                "<th>Potenz</th><th>Ebene</th><th>Raten</th><th>Priorität</th><th>Beschreibung</th></tr>"
            ]
            for item in items[:_MAX_ITEMS_PER_GROUP]:
                score = _as_float(item.get("score"))
                prio_level, prio_cls = _priority_level(score, group_max)
                copen_rate = _as_float(item.get("copen_rate"))
                rates_str = _format_rates(item.get("rates"))
                if copen_rate > 0.0:
                    copen_int = (
                        int(round(copen_rate))
                        if copen_rate == int(copen_rate)
                        else f"{copen_rate:.0f}"
                    )
                    rates_str += f" (Copen: {copen_int})"
                table_parts.append(
                    "<tr>"
                    f"<td>{_escape(item.get('label'))}</td>"
                    f"<td>{_format_float(score)}</td>"
                    f"<td>{_intensity_pair(score, max_score, group_max)}</td>"
                    f"<td>{_escape(item.get('potency', '-')) or '-'}</td>"
                    f"<td>{_escape(item.get('level', '-')) or '-'}</td>"
                    f"<td class='rates'>{rates_str}</td>"
                    f"<td><span class='badge {prio_cls}'>{prio_level}</span></td>"
                    f"<td class='description'>{_escape(item.get('description', '-')) or '-'}</td>"
                    "</tr>"
                )
            table_parts.append("</table>")
            parts.append(
                _render_visible_scroll_section(
                    "".join(table_parts),
                    len(items),
                    label=f"{_format_group_label(group)} Resonanzen",
                    attribute_quote="'",
                )
            )
            # Kombinierte Raten (min/max/Ø) wie in Mustermann-Referenz
            if items:
                group_rates = []
                for it in items:
                    r = it.get("rates")
                    if isinstance(r, (list, tuple)) and r:
                        try:
                            group_rates.append(float(r[0]))
                        except (TypeError, ValueError):
                            pass
                if group_rates:
                    rate_min = min(group_rates)
                    rate_max = max(group_rates)
                    rate_avg = sum(group_rates) / len(group_rates)
                    parts.append(
                        f"<p class='note'>Kombinierte Raten: [ {rate_min:.2f} - {rate_max:.2f} ], "
                        f"Ø {rate_avg:.2f} | Anzahl: {len(group_rates)}</p>"
                    )
            parts.append(_score_intensity_note(max_score, group_max))

        parts.append("<h2>Empfohlene Harmonisierungsschritte</h2>")
        parts.append("<ul>")
        for step in _generate_harmonization_steps(group_buckets, max_score):
            parts.append(f"<li>{_escape(step)}</li>")
        parts.append("</ul>")

    quantum_synergy = export_data.get("quantum_synergy")
    if isinstance(quantum_synergy, list) and quantum_synergy:
        focus_text = html.escape(str(export_data.get("focus", "") or ""))
        parts.append(
            "<h2 style='color:#667eea;'>\u269b\ufe0f Quantum-Synergy Analyse</h2>"
        )
        parts.append(
            "<p style='background:#f8f9fa;padding:14px;border-left:4px solid #667eea;margin-top:8px;'>"
            "Diese Analyse basiert auf dem Quantum-inspirierten Grover-Ansatz. Es werden nur die "
            "staerksten Kombinationen aus dem aktuellen Multiplex-Lauf beruecksichtigt."
            + (f" Fokus:{focus_text}" if focus_text else "")
            + "</p>"
        )

        _COMPONENT_LABELS = {
            "individual_scores": "Einzelwirkungen",
            "resonance": "Resonanz-Verstaerkung",
            "harmony": "Frequenz-Harmonien",
            "relevance": "Fokus-Relevanz",
        }
        _COMPONENT_NOTES = {
            "individual_scores": "Durchschnitt der beteiligten Items",
            "resonance": "Bruce-Copen Resonanzueberlagerung",
            "harmony": "Phi/Oktaven/Schumann-Bezug",
            "relevance": "Semantische Naehe zum Fokus"
            + (f" '{focus_text}'" if focus_text else ""),
        }

        for idx, entry in enumerate(quantum_synergy[:20], 1):
            if not isinstance(entry, dict):
                continue
            items = entry.get("items", [])
            score = _as_float(entry.get("score"))
            category = str(entry.get("category", "") or "").strip()
            if category.lower() in {"primary", "hoch", "high"}:
                category_label = "Hoch"
            elif category.lower() in {"secondary", "mittel", "mid", "medium"}:
                category_label = "Mittel"
            else:
                category_label = category or "-"

            parts.append(
                "<div style='background:#fff;border:1px solid #e2e8f0;border-left:4px solid #ffc107;"
                "padding:16px;margin:16px 0;border-radius:4px;'>"
            )
            parts.append(
                f"<h3 style='margin-top:0;color:#ffc107;'>#{idx} \u2013 Synergy-Score {score:.2f}/10.0 "
                f"<span style='font-size:12px;color:#555;'>({category_label})</span></h3>"
            )

            # Kombinationsliste mit Gruppen-Tags
            if isinstance(items, list) and items:
                parts.append(
                    "<p><strong>Kombination (Substanzen, gruppenuebergreifend):</strong></p><ul>"
                )
                for item in items:
                    if isinstance(item, dict):
                        lbl = _escape(item.get("label", ""))
                        grp = _escape(item.get("group", ""))
                        grp_html = (
                            f" <span style='color:#777;font-size:11px;'>[{grp}]</span>"
                            if grp
                            else ""
                        )
                        parts.append(f"<li>{lbl}{grp_html}</li>")
                parts.append("</ul>")

            # Komponenten-Tabelle
            components = entry.get("components", {})
            if isinstance(components, dict) and components:
                parts.append(
                    "<table style='width:100%;border-collapse:collapse;margin:10px 0;font-size:12px;'>"
                    "<tr><th style='text-align:left;background:#f1f5f9;'>Komponente</th>"
                    "<th style='background:#f1f5f9;'>Score</th>"
                    "<th style='text-align:left;background:#f1f5f9;'>Bedeutung</th></tr>"
                )
                for key, label in _COMPONENT_LABELS.items():
                    if key in components:
                        val = _as_float(components.get(key))
                        note = _COMPONENT_NOTES.get(key, "")
                        parts.append(
                            "<tr>"
                            f"<td>{label}</td>"
                            f"<td>{val:.2f}/10.0</td>"
                            f"<td style='font-size:11px;'>{note}</td>"
                            "</tr>"
                        )
                parts.append("</table>")

            # Frequenzen-Tabelle
            freqs = entry.get("frequencies")
            if isinstance(freqs, list) and freqs and isinstance(items, list):
                parts.append("<p><strong>Frequenzen (pro Substanz):</strong></p>")
                parts.append(
                    "<table style='width:100%;border-collapse:collapse;font-size:11px;'>"
                    "<tr><th style='text-align:left;background:#f9fafb;'>Substanz</th>"
                    "<th style='background:#f9fafb;'>Frequenz (Hz)</th></tr>"
                )
                for i, freq in enumerate(freqs):
                    item_label = ""
                    if i < len(items) and isinstance(items[i], dict):
                        item_label = _escape(items[i].get("label", ""))
                    try:
                        freq_val = float(freq)
                        freq_str = f"{freq_val:.2f}"
                    except (TypeError, ValueError):
                        freq_str = str(freq)
                    parts.append(f"<tr><td>{item_label}</td><td>{freq_str}</td></tr>")
                parts.append("</table>")

            # Copen-Raten der Komponenten (optional, aus items copen_rate)
            if isinstance(items, list) and items:
                copen_parts = []
                for item in items:
                    if isinstance(item, dict):
                        copen = _as_float(item.get("copen_rate"))
                        if copen > 0.0:
                            lbl = str(item.get("label", "") or "").strip()
                            copen_int = (
                                int(round(copen)) if copen == int(copen) else copen
                            )
                            copen_parts.append(f"{lbl}: {copen_int}")
                if copen_parts:
                    parts.append(
                        f"<p style='font-size:11px;color:#374151;'><strong>Copen-Raten der Komponenten:</strong> "
                        + ", ".join(copen_parts)
                        + "</p>"
                    )

            # Interpretationstext
            interp = _synergy_interpretation(score, components, focus_text)
            parts.append(
                f"<p style='font-size:12px;color:#374151;background:#f8fafc;padding:10px;border-radius:4px;'>"
                f"<strong>Interpretation:</strong> {interp}</p>"
            )

            parts.append("</div>")

        # Haeufigste Quantum-Trigger
        trigger_counts: Dict[str, int] = {}
        combo_count = len(quantum_synergy)
        for entry in quantum_synergy:
            if not isinstance(entry, dict):
                continue
            for item in entry.get("items") or []:
                if isinstance(item, dict):
                    lbl = str(item.get("label", "") or "").strip()
                    if lbl:
                        trigger_counts[lbl] = trigger_counts.get(lbl, 0) + 1
        if trigger_counts:
            parts.append("<h3>Haeufigste Quantum-Trigger</h3>")
            parts.append("<ul>")
            for lbl, count in sorted(
                trigger_counts.items(), key=lambda kv: (-kv[1], kv[0])
            )[:8]:
                parts.append(
                    f"<li><strong>{_escape(lbl)}</strong> \u2013 in {count} von {combo_count} Kombinationen</li>"
                )
            parts.append("</ul>")
            parts.append(
                "<p class='note'>Berechnung gemaess Referenzstand 16.11.2025: Nur Items aus den top-resonanten "
                "Gruppen des aktuellen Laufs werden beruecksichtigt. Keine globalen Ergaenzungen.</p>"
            )

    remedy_synergies = export_data.get("remedy_synergies")
    if isinstance(remedy_synergies, list) and remedy_synergies:
        parts.append("<h2>Remedy-Synergien</h2>")
        remedy_table = [
            "<table><tr><th>Remedy 1</th><th>Remedy 2</th><th>Score</th></tr>"
        ]
        for entry in remedy_synergies:
            if not isinstance(entry, dict):
                continue
            score = _as_float(entry.get("synergy_score"))
            score_cls = (
                "prio-high" if score >= 7 else "prio-mid" if score >= 4 else "prio-low"
            )
            remedy_table.append(
                "<tr>"
                f"<td>{_escape(entry.get('item1'))}</td>"
                f"<td>{_escape(entry.get('item2'))}</td>"
                f"<td><span class='badge {score_cls}'>{score:.2f}</span></td>"
                "</tr>"
            )
        remedy_table.append("</table>")
        parts.append(
            _render_visible_scroll_section(
                "".join(remedy_table),
                len(remedy_synergies),
                label="Remedy-Synergien",
                attribute_quote="'",
            )
        )

    # Zweiter Header-Block (Zusammenfassung wie in Mustermann-Referenz)
    profile = html.escape(str(export_data.get("profile", "") or ""))
    personal_profile = (
        export_data.get("personal_profile")
        or export_data.get("personal_profile_values")
        or {}
    )
    if not isinstance(personal_profile, dict):
        personal_profile = {}
    entropy_mode = html.escape(str(export_data.get("entropy_mode", "") or ""))
    pp_text = ", ".join(f"{k}: {v}" for k, v in personal_profile.items()) or "-"
    parts.append("<section class='report-block'>")
    parts.append(
        "<hr style='margin:0 0 28px;border:none;border-top:1px solid rgba(107,165,208,0.2);'>"
    )
    parts.append("<div class='header-info'>")
    parts.append("<h2 style='margin-top:0;'>Resonanzanalyse – Multiplex-Scan</h2>")
    if profile:
        parts.append(f"<p><b>Profil:</b> {profile}</p>")
    if focus:
        parts.append(f"<p><b>Fokus:</b> {focus}</p>")
    parts.append(f"<p><b>Personalprofil:</b> {pp_text}</p>")
    if entropy_mode:
        parts.append(f"<p><b>Entropie-Modus:</b> {entropy_mode}</p>")
    parts.append(
        f"<p><b>Hardware-Level:</b> {h_level:.3f} | <b>Heim-Signatur:</b> {heim}</p>"
    )
    parts.append("</div>")

    # Footer mit Generierungs-Zeitstempel
    from datetime import datetime

    gen_ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    parts.append(
        f"<p class='note' style='margin-top:25px;text-align:center;'>"
        f"Generiert am {gen_ts} | Morphic Engine V1"
        "</p>"
    )
    parts.append("</section>")

    parts.append(_HTML_FOOT)
    return "\n".join(parts)


def _render_multiplex_txt(export_data: Dict[str, object]) -> str:
    client = export_data.get("client") or {}
    if not isinstance(client, dict):
        client = {}
    lines = [
        "Morphic Engine V1 - Multiplex-Scan",
        f"Klient: {client.get('first_name', '')} {client.get('name', '')}",
        f"Profil: {export_data.get('profile', '-')}",
        f"Fokus: {export_data.get('focus', '-')}",
        "",
        wellbeing_txt_block().strip(),
        "",
        "Top Treffer:",
    ]
    sub_results = export_data.get("sub_results") or {}
    top = sub_results.get("top", []) if isinstance(sub_results, dict) else []
    if isinstance(top, list):
        for idx, item in enumerate(top[:50], 1):
            if isinstance(item, dict):
                lines.append(
                    f"{idx:02d}. {item.get('label', '')} | {_format_group_label(item.get('group', ''))} | {float(item.get('score', 0.0) or 0.0):.4f}"
                )
    return "\n".join(lines) + "\n"
