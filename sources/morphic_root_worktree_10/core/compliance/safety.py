from __future__ import annotations

import html


WELLBEING_DISCLAIMER_DE = (
    "Wellbeing Compliance: Diese Auswertung ist eine energetische Resonanz- "
    "und Wellbeing-Analyse. Sie ersetzt keine medizinische Diagnose, keine "
    "Behandlung oder Heilung und kein therapeutisches Fachurteil. Bei Krankheit, "
    "akuten Beschwerden oder Therapiebedarf bitte Arzt, Heilpraktiker oder eine "
    "andere geeignete Fachperson aufsuchen."
)


def safety_marker() -> dict[str, object]:
    return {
        "medical_claims": 0,
        "inference_only": True,
        "non_medical": True,
        "disclaimer": WELLBEING_DISCLAIMER_DE,
    }


def wellbeing_html_block() -> str:
    text = html.escape(WELLBEING_DISCLAIMER_DE)
    return (
        '<div class="section safety-notice">'
        "<h2>Wellbeing Compliance</h2>"
        f'<div class="summary">{text}</div>'
        "</div>"
    )


def wellbeing_txt_block() -> str:
    return "\nWellbeing Compliance\n" + WELLBEING_DISCLAIMER_DE + "\n"
