"""Substep-Vokabular-Mapping: morphic_v1 12-Step-Workflow <-> radiquant4 RadiMorphic-Substeps.

Rein dokumentarisch/labelgebend - aendert kein Verhalten des Orchestrators
und keine bestehenden Step-Namen. Quelle radiquant4-seitig:
`docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`,
Abschnitt 3.2 (`_RADI_MORPHIC_GOLD_SUBSTEPS`).

Wo keine ehrliche 1:1-Entsprechung existiert, wird das explizit als
`None` gefuehrt statt erzwungen zugeordnet (Designprinzip "Keine
Vortaeuschung").
"""

from __future__ import annotations

from typing import TypedDict


class SubstepMappingEntry(TypedDict):
    morphic_step: str
    morphic_step_index: int
    radimorphic_substep: str | None
    note: str


SUBSTEP_MANIFEST: list[SubstepMappingEntry] = [
    {
        "morphic_step": "step01_init",
        "morphic_step_index": 1,
        "radimorphic_substep": "entropy_sampling",
        "note": "Hardware-/Entropy-Init entspricht der Entropy-Sampling-Substep.",
    },
    {
        "morphic_step": "step02_input",
        "morphic_step_index": 2,
        "radimorphic_substep": "profile_resolution",
        "note": "Naeherungsweise: Eingabepruefung/Klientenaufnahme vs. Aufloesung von Profil/Scan-Modus/Level.",
    },
    {
        "morphic_step": "step03_signature",
        "morphic_step_index": 3,
        "radimorphic_substep": "client_signature",
        "note": "Direkte begriffliche Entsprechung (Klienten-Raten/-Signatur).",
    },
    {
        "morphic_step": "step04_focus",
        "morphic_step_index": 4,
        "radimorphic_substep": "intention_weighting",
        "note": "Fokus-Vektor/-Multiplikator entspricht Fokus-/Intentions-Gewichtung.",
    },
    {
        "morphic_step": "step05_emf",
        "morphic_step_index": 5,
        "radimorphic_substep": "client_modifiers",
        "note": "EMF-Kompensation ist explizit Teil der Client-Modifier-Gruppe (Stress/Schlaf/EMF/Konstitution).",
    },
    {
        "morphic_step": "step06_amplifier",
        "morphic_step_index": 6,
        "radimorphic_substep": None,
        "note": "Kein ehrliches Aequivalent - Amplifier-Matching ist morphic_v1-spezifisch.",
    },
    {
        "morphic_step": "step07_palette",
        "morphic_step_index": 7,
        "radimorphic_substep": None,
        "note": "Kein ehrliches Aequivalent auf Substep-Ebene. radiquant4 fuehrt Chromotherapie-Farben nur auf Phasen-Ebene (diagnose/analyse/harmonize).",
    },
    {
        "morphic_step": "step08_matrix",
        "morphic_step_index": 8,
        "radimorphic_substep": "multiplex_scoring",
        "note": "morphic_v1 fuehrt Kandidatenraum-Aufbau und Hadamard-Scoring in einem Step zusammen; die eigentliche Scoring-Operation entspricht multiplex_scoring, nicht candidate_generation.",
    },
    {
        "morphic_step": "step09_quantum",
        "morphic_step_index": 9,
        "radimorphic_substep": "quantum_modulation",
        "note": "Direkte begriffliche Entsprechung.",
    },
    {
        "morphic_step": "step10_post",
        "morphic_step_index": 10,
        "radimorphic_substep": "db_analysis",
        "note": "Post-Processing/Level-Info entspricht der Analyse-Summary-Verdichtung.",
    },
    {
        "morphic_step": "step11_export",
        "morphic_step_index": 11,
        "radimorphic_substep": "export",
        "note": "Direkte begriffliche Entsprechung.",
    },
    {
        "morphic_step": "step12_harmonize",
        "morphic_step_index": 12,
        "radimorphic_substep": None,
        "note": "radiquant4 fuehrt Harmonisierung als eigenen Job-Flow (start_harmonization) ausserhalb der 12 Gold-Substeps - kein Substep-Aequivalent.",
    },
]

# radiquant4-Substeps ohne eigenen morphic_v1-Quellschritt (informativ, kein
# Zwang zur Schliessung dieser Luecke im Rahmen dieses Mappings).
UNMAPPED_RADIMORPHIC_SUBSTEPS: list[str] = [
    "candidate_generation",
    "synergy_analysis",
    "morphic_field",
]


def get_radimorphic_equivalent(morphic_step: str) -> str | None:
    """Liefert das radiquant4-Substep-Vokabular fuer einen morphic_v1-Step.

    Wirft `KeyError`, wenn `morphic_step` nicht im Manifest gefuehrt wird.
    """

    for entry in SUBSTEP_MANIFEST:
        if entry["morphic_step"] == morphic_step:
            return entry["radimorphic_substep"]
    raise KeyError(f"Unbekannter morphic_v1-Step: {morphic_step!r}")
