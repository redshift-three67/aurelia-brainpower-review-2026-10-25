"""CopyGuard — Lexikon-Stufe, fail-closed (Aurelia docs/16-wellbeing.md).

Prototyp-Umfang: nur die Lexikon-Stufe (DE/EN), fail-closed. Die zweite Stufe
(locales schmales LLM im RAM) ist bewusst NICHT Teil dieses Kernels — sie
liegt in der Aurelia-Plattform (CopyGuard-Runtime auf der CPU), nicht im
Fachmodul. Der Kernel markiert lediglich Verdachtsfälle und liefert den
Digest fuer den Computation Passport.

Verboten sind Heil-/Diagnose-/Erfolgsversprechen (Hard Rule 1).
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

# Fail-closed-Lexikon (Auszug der Aurelia-Kategorien, regex, case-insensitive)
BLOCK_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bheilt?\b",
        r"\bheilung\b",
        r"\bheilt\b",
        r"\bdiagnostizier\w*",
        r"\bdiagnose\b",
        r"\bkrebs\s+(behandeln|heilen)\b",
        r"\bbeseitigt?\s+erreger\b",
        r"\bheilversprechen\b",
        r"\bcure\b",
        r"\bcures?\b",
        r"\bheals?\b",
        r"\bmiracle\b",
        r"\bwunderheil\w*",
        r"\bfrequenzheil\w*",
        r"\btherapie(?: erfolg)? garantiert\b",
        r"\bklinisch\s+wirksam\b",
    )
)

Verdict = str  # "allow" | "rewrite" | "block"
PUBLIC_REDACTION = "[CopyGuard: Text zurückgehalten]"


def check_text(text: str) -> tuple[Verdict, list[str]]:
    """Prueft einen sichtbaren Text. Fail-closed: Treffer => block."""
    hits: list[str] = []
    for pattern in BLOCK_PATTERNS:
        match = pattern.search(text or "")
        if match:
            hits.append(match.group(0))
    return ("block" if hits else "allow"), hits


def check_strings(values: list[str]) -> tuple[Verdict, dict[str, list[str]]]:
    """Prueft alle sichtbaren Strings eines Artefakts (UI, Draft, Report)."""
    findings: dict[str, list[str]] = {}
    for value in values:
        verdict, hits = check_text(value)
        if hits:
            findings[value] = hits
    return ("block" if findings else "allow"), findings


def visible_rate_texts(analysis_dict: dict) -> list[str]:
    """Kanonische CopyGuard-Eingabe fuer Ergebnis, Draft und Passport."""
    return [
        rate.get("nameOrRate", "") or ""
        for rate in analysis_dict.get("rateObjects", [])
    ]


def digest(values: list[str]) -> str:
    """Stabiler copyguard_digest ueber alle geprueften Strings (Passport-Pflicht)."""
    joined = "\x1e".join(sorted(values or []))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def public_view(value: Any) -> Any:
    """Reine Projektion für HTTP/Live; persistierte Originale bleiben unverändert."""
    if isinstance(value, str):
        return PUBLIC_REDACTION if check_text(value)[0] == "block" else value
    if isinstance(value, (list, tuple)):
        return [public_view(item) for item in value]
    if isinstance(value, dict):
        projected: dict[Any, Any] = {}
        # Keep already-safe names stable, even if a blocked key appears first.
        reserved = {
            key for key in value
            if isinstance(key, str) and check_text(key)[0] == "allow"
        }
        for key, item in value.items():
            safe_key = public_view(key) if isinstance(key, str) else key
            if safe_key != key:
                base = safe_key
                index = 2
                while safe_key in reserved or safe_key in projected:
                    safe_key = f"{base} [{index}]"
                    index += 1
            projected[safe_key] = public_view(item)
        return projected
    return value


def contains_public_redaction(value: Any) -> bool:
    """Projektionen dürfen nie als vollständige Falldokumente zurückfließen."""
    if isinstance(value, str):
        return PUBLIC_REDACTION in value
    if isinstance(value, (list, tuple)):
        return any(contains_public_redaction(item) for item in value)
    if isinstance(value, dict):
        return any(
            contains_public_redaction(key) or contains_public_redaction(item)
            for key, item in value.items()
        )
    return False
