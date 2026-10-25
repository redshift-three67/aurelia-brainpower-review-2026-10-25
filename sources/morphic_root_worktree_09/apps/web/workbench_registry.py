from __future__ import annotations


WORKBENCH_VERSION = 1

_WORKBENCH_STEPS: tuple[dict[str, str], ...] = (
    {
        "id": "runtime",
        "label": "Runtime & Workspace",
        "cta": "Workspace pruefen",
    },
    {
        "id": "client",
        "label": "Klient / Kontext",
        "cta": "Klient erfassen",
    },
    {
        "id": "focus",
        "label": "Fokus & Zielsetzung",
        "cta": "Fokus setzen",
    },
    {
        "id": "profile",
        "label": "Analyseprofil",
        "cta": "Profil abstimmen",
    },
    {
        "id": "hardware",
        "label": "Hardware & Realtime",
        "cta": "Hardware pruefen",
    },
    {
        "id": "review",
        "label": "Review & Freigabe",
        "cta": "Freigabe erteilen",
    },
    {
        "id": "run",
        "label": "Analyse-Lauf",
        "cta": "Analyse starten",
    },
    {
        "id": "results",
        "label": "Ergebnis-Uebersicht",
        "cta": "Ergebnisse sichten",
    },
    {
        "id": "details",
        "label": "Technische Details & Nachvollziehbarkeit",
        "cta": "Details oeffnen",
    },
    {
        "id": "harmonize",
        "label": "Harmonisierung & Abschluss",
        "cta": "Harmonisierung starten",
    },
    {
        "id": "finalize",
        "label": "Berichtskatalog & Export",
        "cta": "Berichte pruefen",
    },
)

_PIPELINE_VIEW = {
    "href": "/workflow-stepping",
    "kind": "explanatory",
    "label": "Pipeline & Systemerklaerung",
}


def build_workbench_registry() -> dict[str, object]:
    return {
        "version": WORKBENCH_VERSION,
        "steps": [dict(step) for step in _WORKBENCH_STEPS],
        "pipeline_view": dict(_PIPELINE_VIEW),
    }
