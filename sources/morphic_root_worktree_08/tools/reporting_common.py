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
    return Path(output_root) / client_slug(
        last_name, first_name, birth_date, birth_place
    )


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
    from tools.pdf_exporter import html_to_text
    from tools.simple_pdf import write_text_pdf

    pdf_path = target.with_suffix(".pdf")
    write_text_pdf(pdf_path, title or target.stem, html_to_text(target))
    return pdf_path


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

    files: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for folder in root.glob(pattern):
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
            font-family: Georgia, 'Times New Roman', serif;
            background: linear-gradient(135deg, #EFF4F7 0%, #E8EEF2 50%, #E3EAEE 100%);
            min-height: 100vh;
            color: #24323E;
            padding: 36px 20px 48px;
            font-size: 11pt;
            line-height: 1.72;
        }}
        .container {{ max-width: 1080px; margin: 0 auto; }}
        .report-shell {{ display: grid; gap: 22px; }}
        .header {{
            background: rgba(255,255,255,0.84);
            backdrop-filter: blur(20px);
            padding: 34px;
            border-radius: 22px;
            text-align: center;
            box-shadow: 0 10px 28px rgba(86, 117, 141, 0.10);
            border: 1px solid rgba(255,255,255,0.88);
        }}
        .header h1 {{ font-size: 22pt; margin-bottom: 14px; color: #24323E; font-weight: 600; }}
        .subtitle {{ font-size: 11pt; color: #516170; margin-bottom: 18px; }}
        .meta {{ display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; margin-top: 18px; }}
        .meta span {{
            background: linear-gradient(135deg, rgba(115,149,175,0.12), rgba(186,206,220,0.22));
            padding: 9px 18px;
            border-radius: 24px;
            color: #35506A;
            border: 1px solid rgba(115,149,175,0.18);
        }}
        .focus {{
            background: linear-gradient(135deg, rgba(115,149,175,0.13), rgba(186,206,220,0.22));
            padding: 13px 24px;
            border-radius: 24px;
            display: inline-block;
            margin-top: 16px;
            font-weight: 600;
            color: #35506A;
            border: 1px solid rgba(115,149,175,0.2);
        }}
        .section, .report-block {{
            background: rgba(255,255,255,0.82);
            backdrop-filter: blur(20px);
            border-radius: 18px;
            padding: 28px;
            border: 1px solid rgba(255,255,255,0.88);
            box-shadow: 0 4px 18px rgba(86, 117, 141, 0.08);
        }}
        .section h2 {{
            color: #35506A;
            font-size: 16pt;
            font-weight: 600;
            margin-bottom: 20px;
            border-left: 4px solid #7395AF;
            background: linear-gradient(135deg, rgba(115,149,175,0.08), rgba(186,206,220,0.14));
            padding: 13px 20px;
            border-radius: 12px;
        }}
        .report-shell h2, .report-shell h3, .report-shell p, .report-shell ul, .report-shell ol, .report-shell pre, .report-shell table {{ margin-top: 0; margin-bottom: 18px; }}
        .summary {{
            background: linear-gradient(135deg, rgba(115,149,175,0.10), rgba(186,206,220,0.16));
            padding: 24px;
            border-radius: 14px;
            line-height: 1.75;
            border-left: 4px solid #7395AF;
            color: #34495E;
        }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: rgba(255,255,255,0.72); }}
        th {{ background: linear-gradient(135deg, #7395AF, #88A6BB); color: white; padding: 13px 14px; text-align: left; }}
        td {{ padding: 13px 14px; border-bottom: 1px solid rgba(115,149,175,0.12); vertical-align: top; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; color: white; font-weight: 600; }}
        .badge-high {{ background: linear-gradient(135deg,#FF6B9D,#FFA07A); }}
        .badge-mid {{ background: linear-gradient(135deg,#FFB347,#FFCC80); }}
        .note {{ color: #5D6D7E; font-size: 10pt; margin-top: 10px; }}
        .card {{ background: rgba(255,255,255,0.68); border: 1px solid rgba(115,149,175,0.13); border-radius: 14px; padding: 20px; margin-bottom: 16px; transition: box-shadow 0.2s ease, border-color 0.2s ease; }}
        .card:hover {{ box-shadow: 0 4px 16px rgba(107,165,208,0.10); }}
        .card.highlight {{ border-left: 4px solid #7395AF; }}
        .card.quantum {{ border-left: 4px solid #ffc107; }}
        .card-title {{ font-weight: 600; color: #2d3748; margin-bottom: 8px; font-size: 14pt; }}
        .card-meta {{ font-size: 13px; color: #718096; }}
        .score {{ font-size: 18px; font-weight: 600; color: #6BA5D0; }}
        .badge-success {{ background: linear-gradient(135deg, #77DD77, #98D8C8); color: white; box-shadow: 0 2px 8px rgba(119,221,119,0.3); }}
        .badge-warning {{ background: linear-gradient(135deg, #FFB347, #FFCC80); color: white; box-shadow: 0 2px 8px rgba(255,179,71,0.3); }}
        .badge-info {{ background: linear-gradient(135deg, #6BA5D0, #A7C7E7); color: white; box-shadow: 0 2px 8px rgba(107,165,208,0.3); }}
        .profile-tag {{ background: linear-gradient(135deg, rgba(107,165,208,0.15), rgba(167,199,231,0.20)); padding: 6px 12px; border-radius: 16px; font-size: 11px; color: #3D5A73; font-weight: 500; border: 1px solid rgba(107,165,208,0.2); display: inline-block; margin: 3px; }}
        .profiles {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 12px; }}
        .finding {{ background: rgba(255,255,255,0.68); padding: 18px; border-radius: 14px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; gap: 16px; transition: box-shadow 0.2s ease, border-color 0.2s ease; border: 1px solid rgba(115,149,175,0.13); }}
        .finding:hover {{ box-shadow: 0 4px 16px rgba(107,165,208,0.10); }}
        .finding .label {{ font-weight: 600; color: #2C3E50; }}
        .finding .score {{ background: linear-gradient(135deg, #7395AF, #88A6BB); padding: 6px 18px; border-radius: 20px; font-size: 0.9em; color: #FFFFFF; font-weight: 600; box-shadow: 0 2px 8px rgba(115,149,175,0.24); }}
        .finding.high {{ border-left: 4px solid #FF6B9D; background: rgba(255,107,157,0.05); }}
        .finding.medium {{ border-left: 4px solid #FFB347; background: rgba(255,179,71,0.05); }}
        .recommendation {{ background: linear-gradient(135deg, rgba(119,221,119,0.08), rgba(152,216,200,0.12)); padding: 18px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid #77DD77; color: #34495E; box-shadow: 0 2px 12px rgba(119,221,119,0.1); }}
        pre, .scroll-section {{ max-height: min(70vh, 960px); overflow: auto; }}
        .scroll-section {{ padding: 0; border-radius: 14px; }}
        .footer {{ text-align: center; padding: 25px; color: #7F8C8D; font-size: 0.9em; }}
        @media print {{
            body {{ background: white !important; padding: 10px !important; }}
            .header, .section {{ box-shadow: none !important; backdrop-filter: none !important; }}
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
        <div style="text-align:center;padding:25px;color:#7F8C8D;font-size:0.9em;">
            <p>Generiert am {datetime.now().strftime("%d.%m.%Y %H:%M:%S")} | Morphic Engine V1</p>
        </div>
        </main>
    </div>
</body>
</html>
"""
