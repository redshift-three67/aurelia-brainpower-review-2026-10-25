from __future__ import annotations

import html
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping

from core.compliance.safety import wellbeing_html_block
from core.compliance.runtime_manifest import RuntimeManifestService


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
) -> Path:
    """Verzeichnis fuer berichtsspezifische Ausgaben.

    Hierarchie: output_root / report_type / client_slug
    Z.B. C:\\Benutzer_Archive_Start / Deutung / Mustermann_Klaus_09041966_Augsburg
    """
    slug = client_slug(last_name, first_name, birth_date, birth_place)
    type_folder = safe_part(report_type) if report_type else ""
    path = Path(output_root)
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


def render_legacy_html(
    *,
    title: str,
    subtitle: str,
    body_html: str,
    focus: str = "",
    meta: Iterable[tuple[str, object]] = (),
) -> str:
    meta_html = "".join(
        f"<span><strong>{escape(label)}:</strong> {escape(value)}</span>"
        for label, value in meta
        if str(value or "").strip()
    )
    focus_html = f'<div class="focus">{escape(focus)}</div>' if focus else ""
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{ color-scheme: light; }}
        body {{
            font-family: 'Inter', 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #E8F1F8 0%, #D8E8F0 50%, #C5DAE8 100%);
            min-height: 100vh;
            color: #2C3E50;
            padding: 30px 20px;
            font-size: 11pt;
            line-height: 1.6;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .report-shell {{ display: grid; gap: 22px; }}
        .header {{
            background: rgba(255,255,255,0.75);
            backdrop-filter: blur(20px);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(107,165,208,0.15);
            border: 1px solid rgba(255,255,255,0.8);
        }}
        .header h1 {{ font-size: 22pt; margin-bottom: 12px; color: #2C3E50; font-weight: 600; letter-spacing: -0.5px; }}
        .subtitle {{ font-size: 11pt; color: #5D6D7E; margin-bottom: 15px; }}
        .meta {{ display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; margin-top: 15px; }}
        .meta span {{
            background: linear-gradient(135deg, rgba(107,165,208,0.15), rgba(167,199,231,0.20));
            padding: 8px 18px;
            border-radius: 24px;
            color: #3D5A73;
            font-weight: 500;
            border: 1px solid rgba(107,165,208,0.25);
        }}
        .focus {{
            background: linear-gradient(135deg, rgba(107,165,208,0.15), rgba(167,199,231,0.20));
            padding: 12px 24px;
            border-radius: 24px;
            display: inline-block;
            margin-top: 15px;
            font-weight: 600;
            color: #3D5A73;
            border: 1px solid rgba(107,165,208,0.3);
            box-shadow: 0 4px 12px rgba(107,165,208,0.1);
        }}
        .section, .report-block {{
            background: rgba(255,255,255,0.75);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.8);
            box-shadow: 0 4px 20px rgba(107,165,208,0.1);
        }}
        .section h2 {{
            color: #3D5A73;
            font-size: 16pt;
            font-weight: 600;
            margin-bottom: 18px;
            padding-left: 20px;
            border-left: 4px solid #6BA5D0;
            background: linear-gradient(135deg, rgba(107,165,208,0.08), rgba(167,199,231,0.12));
            padding: 12px 20px;
            border-radius: 12px;
            margin: 0 -5px 18px -5px;
        }}
        .report-shell h2, .report-shell h3, .report-shell p, .report-shell ul, .report-shell ol, .report-shell pre, .report-shell table {{ margin-top: 0; margin-bottom: 18px; }}
        h3 {{ font-size: 13pt; font-weight: 600; margin: 20px 0 12px; color: #4A6278; }}
        .summary {{
            background: linear-gradient(135deg, rgba(107,165,208,0.10), rgba(167,199,231,0.15));
            padding: 22px;
            border-radius: 14px;
            font-size: 1.05em;
            line-height: 1.7;
            border-left: 4px solid #6BA5D0;
            color: #34495E;
            box-shadow: 0 2px 12px rgba(107,165,208,0.08);
        }}
        table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin: 20px 0; font-size: 10pt; background: rgba(255,255,255,0.5); border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(107,165,208,0.08); }}
        th {{ background: linear-gradient(135deg, #6BA5D0, #7FB5DB); color: #FFFFFF; padding: 12px 16px; text-align: left; font-weight: 600; text-transform: uppercase; font-size: 9pt; letter-spacing: 0.5px; }}
        td {{ padding: 12px 16px; border-bottom: 1px solid rgba(107,165,208,0.1); vertical-align: top; }}
        tbody tr {{ transition: all 0.2s ease; }}
        tbody tr:hover {{ background: rgba(107,165,208,0.08); transform: translateX(2px); }}
        tbody tr:last-child td {{ border-bottom: none; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; color: white; font-weight: 600; letter-spacing: 0.3px; font-size: 9pt; }}
        .badge-high, .prio-high {{ background: linear-gradient(135deg, #FF6B9D, #FFA07A); box-shadow: 0 2px 8px rgba(255,107,157,0.3); }}
        .badge-mid, .prio-mid {{ background: linear-gradient(135deg, #FFB347, #FFCC80); box-shadow: 0 2px 8px rgba(255,179,71,0.3); }}
        .prio-low {{ background: linear-gradient(135deg, #77DD77, #98D8C8); box-shadow: 0 2px 8px rgba(119,221,119,0.3); }}
        .note {{ color: #5D6D7E; font-size: 9pt; margin-top: 12px; padding: 12px 16px; background: rgba(107,165,208,0.06); border-radius: 10px; border-left: 3px solid #A7C7E7; }}
        .card {{ background: rgba(255,255,255,0.6); border: 1px solid rgba(107,165,208,0.15); border-radius: 12px; padding: 18px; margin-bottom: 15px; transition: all 0.2s ease; }}
        .card:hover {{ transform: translateX(4px); box-shadow: 0 4px 16px rgba(107,165,208,0.12); }}
        .card.highlight {{ border-left: 4px solid #6BA5D0; }}
        .card.quantum {{ border-left: 4px solid #ffc107; }}
        .card-title {{ font-weight: 600; color: #2C3E50; margin-bottom: 8px; font-size: 14pt; }}
        .card-meta {{ font-size: 13px; color: #5D6D7E; }}
        .score {{ font-size: 18px; font-weight: 600; color: #6BA5D0; }}
        .badge-success {{ background: linear-gradient(135deg, #77DD77, #98D8C8); color: white; box-shadow: 0 2px 8px rgba(119,221,119,0.3); }}
        .badge-warning {{ background: linear-gradient(135deg, #FFB347, #FFCC80); color: white; box-shadow: 0 2px 8px rgba(255,179,71,0.3); }}
        .badge-info {{ background: linear-gradient(135deg, #6BA5D0, #A7C7E7); color: white; box-shadow: 0 2px 8px rgba(107,165,208,0.3); }}
        .profile-tag {{
            background: linear-gradient(135deg, rgba(107,165,208,0.15), rgba(167,199,231,0.20));
            padding: 10px 18px;
            border-radius: 24px;
            font-size: 0.9em;
            color: #3D5A73;
            font-weight: 500;
            border: 1px solid rgba(107,165,208,0.25);
            display: inline-block;
            margin: 3px;
            transition: all 0.2s ease;
        }}
        .profile-tag:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(107,165,208,0.2); }}
        .profiles {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 12px; }}
        .finding {{
            background: rgba(255,255,255,0.6);
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s ease;
            border: 1px solid rgba(107,165,208,0.15);
        }}
        .finding:hover {{ transform: translateX(4px); box-shadow: 0 4px 16px rgba(107,165,208,0.12); }}
        .finding .label {{ font-weight: 600; color: #2C3E50; }}
        .finding .score {{
            background: linear-gradient(135deg, #6BA5D0, #7FB5DB);
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 0.9em;
            color: #FFFFFF;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(107,165,208,0.3);
        }}
        .finding.high {{ border-left: 4px solid #FF6B9D; background: rgba(255,107,157,0.05); }}
        .finding.medium {{ border-left: 4px solid #FFB347; background: rgba(255,179,71,0.05); }}
        .pattern {{
            background: rgba(255,255,255,0.5);
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 12px;
            border: 1px solid rgba(107,165,208,0.15);
        }}
        .pattern .type {{ color: #6BA5D0; font-weight: 600; margin-bottom: 8px; font-size: 1.05em; }}
        .pattern .items {{ font-size: 0.95em; color: #5D6D7E; margin-top: 10px; line-height: 1.6; }}
        .recommendation {{
            background: linear-gradient(135deg, rgba(119,221,119,0.08), rgba(152,216,200,0.12));
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 12px;
            border-left: 4px solid #77DD77;
            color: #34495E;
            box-shadow: 0 2px 12px rgba(119,221,119,0.1);
        }}
        td.rates {{ font-family: 'Fira Code', 'Consolas', 'Monaco', monospace; font-size: 9pt; color: #6BA5D0; font-weight: 500; }}
        td.description {{ font-size: 9.5pt; color: #5D6D7E; max-width: 350px; line-height: 1.5; word-wrap: break-word; white-space: normal; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; background: rgba(255,255,255,0.50); padding: 18px; border-radius: 12px; border: 1px solid rgba(107,165,208,0.12); max-height: min(70vh, 960px); overflow: auto; }}
        p {{ word-wrap: break-word; white-space: normal; }}
        .scroll-section {{ overflow-y: auto; max-height: min(70vh, 960px); border: 1px solid rgba(107,165,208,0.15); border-radius: 12px; background: rgba(255,255,255,0.4); box-shadow: inset 0 2px 8px rgba(107,165,208,0.05); padding: 0; }}
        .scroll-section table {{ margin: 0; border-radius: 0; box-shadow: none; }}
        .visible-limit-note {{ margin-bottom: 8px; }}
        .footer {{ text-align: center; padding: 25px; color: #7F8C8D; font-size: 0.9em; }}
        .llm-section {{ background: linear-gradient(135deg, rgba(102, 126, 234, 0.10), rgba(118, 75, 162, 0.10)); border-left: 4px solid #764ba2; }}
        @media print {{
            body {{ background: #f8f9fa !important; color: #2c3e50 !important; padding: 10px !important; font-family: 'Segoe UI', 'Roboto', Arial, sans-serif !important; font-size: 11pt !important; }}
            .container {{ max-width: 100% !important; }}
            .header {{ background: linear-gradient(135deg, #3d5a73 0%, #2c4356 100%) !important; color: #ffffff !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
            .header h1 {{ color: #ffffff !important; font-size: 18pt !important; }}
            .subtitle {{ color: #e0e8f0 !important; }}
            .focus {{ background: rgba(255,255,255,0.25) !important; color: #ffffff !important; }}
            .section, .report-block {{ background: #ffffff !important; border: 1px solid #d1d5db !important; box-shadow: none !important; backdrop-filter: none !important; page-break-inside: avoid; }}
            .section h2 {{ color: #4a6278 !important; }}
            .summary {{ background: #e8f4f8 !important; color: #2c3e50 !important; border-left-color: #5a7a9a !important; }}
            .finding {{ background: #f8f9fa !important; }}
            .finding .label {{ color: #1a252f !important; }}
            .finding .score {{ background: #5a7a9a !important; color: white !important; }}
            .finding.high {{ border-left-color: #c0392b !important; }}
            .finding.medium {{ border-left-color: #d68910 !important; }}
            table {{ box-shadow: none !important; }}
            th {{ background: #6BA5D0 !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
            .badge, .prio-high, .prio-mid, .prio-low {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
            .profile-tag {{ background: #d5e8f0 !important; color: #2c3e50 !important; }}
            .recommendation {{ background: #e8f6ef !important; border-left-color: #27ae60 !important; }}
            .footer {{ color: #5d6d7e !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <main class="report-shell">
        <div class="header report-block">
            <h1>{escape(title)}</h1>
            <div class="subtitle">{escape(subtitle)}</div>
            {focus_html}
            <div class="meta">{meta_html}</div>
        </div>
        {wellbeing_html_block()}
        {body_html}
        <div class="footer">
            <p>Generiert am {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} | Morphic Engine V1</p>
        </div>
        </main>
    </div>
</body>
</html>
"""
