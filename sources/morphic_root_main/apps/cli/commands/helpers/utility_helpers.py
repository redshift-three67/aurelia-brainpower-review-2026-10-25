"""Utility helper functions for CLI commands."""

from __future__ import annotations

import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:
    from core.remedy_group_registry import is_remedy_group as _central_is_remedy_group
except Exception:
    def _central_is_remedy_group(group: str) -> bool:
        return any(token in (group or "").lower() for token in ("remedy", "homoeopathie", "tcm_rezepturen", "schuessler"))


def _is_remedy_group(group: str) -> bool:
    return bool(_central_is_remedy_group(group))


def _client_folder_name(name: str, first_name: str, birth_date: str, birth_place: str) -> str:
    slug = f"{name}_{first_name}_{birth_date}_{birth_place}".strip()
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", slug).strip("_") or "client"


def _topn_session_parts(scan_type: str, filename_suffix: str) -> tuple[str, str] | None:
    match = re.fullmatch(r"top(\d+)_session", (scan_type or "").strip().lower())
    if not match:
        return None

    suffix_parts = [part for part in (filename_suffix or "").split("_") if part]
    profile_folder = filename_suffix or "profile"
    if len(suffix_parts) >= 5:
        profile_number = suffix_parts[2]
        profile_name = "_".join(suffix_parts[3:-1])
        profile_folder = f"{profile_number}_{profile_name}"

    return match.group(1), profile_folder


def _resolve_export_paths(
    export: Path,
    client: Dict[str, str],
    command: str,
    filename_suffix: str = "",
    scan_type: str = "",
    session_id: str = "",
) -> tuple[Path, Path]:
    export = export.resolve()
    suffix = export.suffix.lower()
    if suffix == ".json":
        json_path = export
        html_path = export.with_suffix(".html")
    elif suffix in {".html", ".htm"}:
        html_path = export
        json_path = export.with_suffix(".json")
    else:
        client_dir = export / "Resonanz" / _client_folder_name(
            str(client.get("name", "") or ""),
            str(client.get("first_name", "") or ""),
            str(client.get("birth_date", "") or ""),
            str(client.get("birth_place", "") or ""),
        )
        timestamp = filename_suffix or datetime.now().strftime("%Y%m%d_%H%M%S")
        topn_session = _topn_session_parts(scan_type, filename_suffix)
        if topn_session and session_id:
            top_n, profile_folder = topn_session
            analysis_dir = client_dir / f"{session_id}_TOP{top_n}_SESSION" / profile_folder
        elif scan_type:
            analysis_dir = client_dir / f"{timestamp}_{scan_type}"
        else:
            analysis_dir = client_dir / timestamp
        json_path = analysis_dir / f"{timestamp}_{command}.json"
        html_path = analysis_dir / f"{timestamp}_{command}.html"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    return json_path, html_path


def _atomic_write_text(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.parent / f"{target.name}.tmp.{int(time.time() * 1000)}"
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)


def _normalize_tcm_type(raw: str) -> Dict[str, str]:
    result = {"code": "", "label": "", "element": "", "organs": ""}
    text = (raw or "").strip().lower()
    if not text:
        return result
    mapping = {
        "holz": ("holz_leber", "Holz - Leber Typ", "Holz", "Leber, Gallenblase"),
        "leber": ("holz_leber", "Holz - Leber Typ", "Holz", "Leber, Gallenblase"),
        "feuer": ("feuer_herz", "Feuer - Herz Typ", "Feuer", "Herz, Duenndarm"),
        "herz": ("feuer_herz", "Feuer - Herz Typ", "Feuer", "Herz, Duenndarm"),
        "erde": ("erde_milz", "Erde - Milz Typ", "Erde", "Milz, Magen"),
        "metall": ("metall_lunge", "Metall - Lungen Typ", "Metall", "Lunge, Dickdarm, Haut"),
        "lunge": ("metall_lunge", "Metall - Lungen Typ", "Metall", "Lunge, Dickdarm, Haut"),
        "wasser": ("wasser_niere", "Wasser - Nieren Typ", "Wasser", "Niere, Blase, Knochen"),
        "niere": ("wasser_niere", "Wasser - Nieren Typ", "Wasser", "Niere, Blase, Knochen"),
    }
    for key, value in mapping.items():
        if key in text:
            code, label, element, organs = value
            return {"code": code, "label": label, "element": element, "organs": organs}
    return {"code": "", "label": raw.strip(), "element": "", "organs": ""}


def _normalize_planet_type(raw: str) -> Dict[str, str]:
    text = (raw or "").strip().lower()
    if not text:
        return {"code": "", "label": "", "keywords": "", "description": ""}
    labels = {
        "sonne": "Lebenskraft, Identitaet, Selbstvertrauen",
        "mond": "Emotion, Sicherheit, Fruchtbarkeit",
        "merkur": "Kommunikation, Denken, Lernen",
        "venus": "Liebe, Beziehungen, Schoenheit",
        "mars": "Aktion, Durchsetzung, physische Energie",
        "jupiter": "Wachstum, Optimismus, Expansion",
        "saturn": "Struktur, Grenze, Verantwortung",
        "uranus": "Unabhaengigkeit, Veraenderung, Originalitaet",
        "neptun": "Intuition, Spiritualitaet, Empathie",
        "pluto": "Transformation, Unterbewusstsein, Macht",
    }
    for key, keywords in labels.items():
        if text == key or text.startswith(key):
            return {"code": key, "label": key.title(), "keywords": keywords, "description": keywords}
    return {"code": "", "label": raw.strip(), "keywords": "", "description": ""}


def _build_organ_clock_block(now: Optional[datetime] = None) -> Dict[str, object]:
    now = now or datetime.now()
    ranges = [
        (3, 5, "03-05 Lunge", "Lunge"),
        (5, 7, "05-07 Dickdarm", "Dickdarm"),
        (7, 9, "07-09 Magen", "Magen"),
        (9, 11, "09-11 Milz/Pankreas", "Milz/Pankreas"),
        (11, 13, "11-13 Herz", "Herz"),
        (13, 15, "13-15 Duenndarm", "Duenndarm"),
        (15, 17, "15-17 Blase", "Blase"),
        (17, 19, "17-19 Niere", "Niere"),
        (19, 21, "19-21 Perikard/Kreislauf", "Perikard/Kreislauf"),
        (21, 23, "21-23 Dreifacher Erwaermer", "Dreifacher Erwaermer"),
        (1, 3, "01-03 Leber", "Leber"),
    ]
    hour = now.hour
    if hour >= 23 or hour < 1:
        segment, organ = "23-01 Gallenblase", "Gallenblase"
    else:
        segment, organ = "neutral", ""
        for start, end, label, active in ranges:
            if start <= hour < end:
                segment, organ = label, active
                break
    return {"segment": segment, "active_organs": [organ] if organ else [], "local_time": now.isoformat()}


def _build_image_block(image_signature: object) -> Dict[str, object]:
    return {"present": image_signature is not None, "source": "custom" if image_signature is not None else "default", "quality": ""}
