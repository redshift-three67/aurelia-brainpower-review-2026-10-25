"""Essenzielle Fragen — Port des GV-Orakels (AetherOneEventHandler,
askEssentialQuestions / askQuestionWhen / AetherOneUI.checkPercentage,
FUNKTIONSANALYSE §10).

Deutsche, wellbeing-konforme Formulierung (CopyGuard-geprüft); die
Entscheidungslogik ist identisch zum Original: Schwellen GV > 500 = JA,
Zeitprognose aus 7 Optionen per GV-Maximum.
"""

from __future__ import annotations

from .. import copyguard
from ..entropy import EntropyProvider
from .analysis import check_general_vitality, check_percentage

WHEN_OPTIONS = (
    "in einer Woche",
    "in einem Monat",
    "in zwei Monaten",
    "in drei Monaten",
    "in sechs Monaten",
    "in einem Jahr",
    "in zwei Jahren",
)


def ask_essential_questions(entropy: EntropyProvider) -> str:
    lines: list[str] = ["== ESSENZIELLE FRAGEN =="]

    lines.append("Angemessenheit? (0 bis 100)")
    lines.append(f"{check_percentage(entropy)} %")
    lines.append("")

    lines.append("Darf ich mit dieser Person arbeiten?")
    gv = check_general_vitality(entropy)
    if gv > 500:
        lines.append(f"- JA ({gv})")
        lines.append("")
        lines.append("Ist es zum Besten und höchsten Wohl der Person?")
        gv = check_general_vitality(entropy)
        if gv > 500:
            lines.append(f"- JA ({gv})")
        else:
            lines.append(f"- NEIN … Wann wird es möglich sein? ({gv})")
            _append_when(lines, entropy)
        lines.append("Ist es zu meinem Besten und höchsten Wohl?")
        gv = check_general_vitality(entropy)
        if gv > 500:
            lines.append(f"- JA ({gv})")
        else:
            lines.append(f"- NEIN … Wann wird es möglich sein? ({gv})")
            _append_when(lines, entropy)
    else:
        lines.append(f"- NEIN … Wann wird es möglich sein? ({gv})")
        _append_when(lines, entropy)

    report = "\n".join(lines)
    verdict, _ = copyguard.check_text(report)
    if verdict == "block":  # pragma: no cover - Texte sind fix und konform
        raise RuntimeError("CopyGuard blockt den Fragenreport (sollte nicht passieren)")
    return report


def _append_when(lines: list[str], entropy: EntropyProvider) -> None:
    gv = check_general_vitality(entropy)
    if gv <= 500:
        lines.append(f"-- NEIN ({gv})")
        lines.append("")
        return
    lines.append(f"-- JA … In welchem Zeitraum? ({gv})")
    scores = {option: check_general_vitality(entropy) for option in WHEN_OPTIONS}
    best = max(scores.items(), key=lambda pair: pair[1])
    lines.append(f"--- {best[0]} ({best[1]})")
    lines.append("")
