"""R-7/R-8: Safety-Posture + PII-Stripping fuer Radi144.

Kanonische Nicht-Medizin-Disclaimer- und Safety-Marker-Quelle. Additiv,
non-breaking: kein Term-Block, keine Wort-Zensur (Nutzer-Entscheidung
2026-06-27 — das heilungs-adjazente Wellness-Vokabular des Produkts
bleibt unangetastet; die Safety-Posture ist die Erklaerung, nicht die Zensur).

PII-Stripping (R-8): `project_client_safe`/`project_session_safe` liefern
Pseudonym-Projektionen OHNE Roh-PII — die autarkische Safe-View fuer
Audit/Bus-Andock (R-10). Die Working-Stores behalten ihre PII, denn
`engine.calculate_resonance(client_data=...)` braucht sie.
"""
from __future__ import annotations

from typing import Any

from ..models.client_registry import ClientRegistryEntry
from ..models.session_archive import SessionArchiveEntry


# Kanonischer Disclaimer (Deutsch, staerker als USER_GUIDE_DE.md:35). Wird auf
# jede Analyse-Response, jedes PDF und /safety/posture gelegt. KEINE Wort-
# Ersetzung im Produkt-Output (siehe Modul-Docstring).
DISCLAIMER_DE = (
    "Energetische Resonanz-Balancierung — ersetzt keine medizinische Diagnose, "
    "Behandlung oder Heilung. Bei Krankheit, akuten Beschwerden oder "
    "Therapiebedarf bitte Arzt oder Heilpraktiker aufsuchen. Keine "
    "medizinischen Aussagen oder Heversprechen."
)


def safety_block() -> dict[str, Any]:
    """Frische Kopie der kanonischen Safety-Marker (pro Response).

    Ehrlich zu Radi144: das Produkt hat kein ``real_output``/``adapter``-Konzept
    (im Gegensatz zu ME2). Die ME2-Bus-Paritaets-Marker ``real_output_enabled``
    und ``adapter`` liefert die R-10-Projektion beim Bus-Andock, nicht hier.
    """
    return {
        "medical_claims": 0,
        "inference_only": True,
        "non_medical": True,
        "disclaimer": DISCLAIMER_DE,
    }


# ------------------------------------------------------------------ PII-Stripping (R-8)

# PII-Felder, die aus einer Client-Projektion entfernt werden (Klartext-PII,
# die in clients.json neben dem Pseudonym steht — siehe models/client_registry.py:9-18).
_CLIENT_PII_FIELDS = ("first_name", "last_names", "birth_date", "birth_place")


def project_client_safe(entry: ClientRegistryEntry) -> dict[str, Any]:
    """Pseudonym-Projektion eines Klienten OHNE Roh-PII.

    Behaelt: ``client_id`` (Pseudonym cli-<sha1[:16]>), ``planet``, ``metadata``,
    ``created_at``/``updated_at``. Wirft: ``first_name``/``last_names``/
    ``birth_date``/``birth_place`` (Klartext-PII).
    """
    data = entry.model_dump(mode="json")
    for field in _CLIENT_PII_FIELDS:
        data.pop(field, None)
    return data


def project_session_safe(entry: SessionArchiveEntry) -> dict[str, Any]:
    """Session-Projektion mit redigiertem Klienten-Namen (PII).

    ``client_ref.client_name`` (Klartext-Vollname, redundant zum Pseudonym —
    siehe models/session_archive.py:8-10) wird zu ``[redacted]``; ``client_id``
    (Pseudonym) bleibt als Referenz erhalten.
    """
    data = entry.model_dump(mode="json")
    client_ref = data.get("client_ref")
    if isinstance(client_ref, dict):
        client_ref["client_name"] = "[redacted]"
    return data