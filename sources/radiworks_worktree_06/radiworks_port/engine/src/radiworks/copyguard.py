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


def digest(values: list[str]) -> str:
    """Stabiler copyguard_digest ueber alle geprueften Strings (Passport-Pflicht)."""
    joined = "\x1e".join(sorted(values or []))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
