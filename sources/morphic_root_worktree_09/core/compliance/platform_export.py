"""Platform Export Adapter.

Erzeugt aus vorhandenen Scan-/Workflow-Ergebnissen zusaetzlich einen
`StandardAnalysisBlock`-kompatiblen Ausgabeblock, wie ihn radiquant4s
RadiMorphic-Reporting-Adapter erwartet (siehe
`docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`,
Abschnitt 6: `inputs`/`outputs`/`meta` mit `remedy_matches` als
`(name, score)`-Liste).

Diese Schicht ist rein additiv: Sie ersetzt keinen bestehenden Export und
aendert kein bestehendes Datenformat. Felder ohne echte Datenquelle werden
als `None`/leer belassen statt erfunden (siehe Designprinzip "Keine
Vortaeuschung" in
`docs/superpowers/specs/2026-07-05-morphic-v1-radiquant4-alignment-design.md`).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Sequence

SOURCE_SYSTEM = "MORPHIC_V1"


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_standard_output_block(
    *,
    profiles: Sequence[str] | None = None,
    focus: str | None = None,
    intention: str | None = None,
    quality_score: float | None = None,
    morphic_field: float | None = None,
    holographic_entropy: float | None = None,
    remedy_matches: Sequence[tuple[str, float]] | None = None,
    timestamp: str | None = None,
    source_system: str = SOURCE_SYSTEM,
) -> dict[str, Any]:
    """Baut einen `StandardAnalysisBlock`-kompatiblen Ausgabeblock.

    Struktur und Feldnamen entsprechen exakt dem, was
    `RadiMorphicReportingAdapter` in radiquant4 aus
    `analysis_sessions.results["radimorphic"]` liest.
    """

    return {
        "inputs": {
            "profiles": list(profiles) if profiles else [],
            "focus": focus,
            "intention": intention,
        },
        "outputs": {
            "quality_score": quality_score,
            "morphic_field": morphic_field,
            "holographic_entropy": holographic_entropy,
            "remedy_matches": [[name, score] for name, score in (remedy_matches or [])],
        },
        "meta": {
            "timestamp": timestamp or _now(),
            "source_system": source_system,
        },
    }


def build_standard_output_block_from_workflow_state(state: Any) -> dict[str, Any]:
    """Convenience-Wrapper fuer `apps.cli.workflow.state.WorkflowState`.

    Der Typ wird absichtlich nicht importiert (nur `getattr`-Zugriff), damit
    `core/` nicht auf `apps/` angewiesen ist (Schichtregel, siehe
    `docs/deep-audit-2026-07-04/PHASE_1_CODEBASE_ARCHITEKTUR_UND_STRUKTUR.md`).
    """

    remedy_matches: list[tuple[str, float]] = []
    for entry in getattr(state, "matrix_results", None) or []:
        label = entry.get("label") if isinstance(entry, dict) else None
        score = entry.get("score") if isinstance(entry, dict) else None
        if label is not None and score is not None:
            remedy_matches.append((str(label), float(score)))

    quantum_synergies = getattr(state, "quantum_synergies", None) or []
    scores = [
        s.get("score")
        for s in quantum_synergies
        if isinstance(s, dict) and s.get("score") is not None
    ]
    quality_score = (sum(scores) / len(scores)) if scores else None

    focus = getattr(state, "focus", None) or None

    return build_standard_output_block(
        profiles=[focus] if focus else [],
        focus=focus,
        intention=getattr(state, "intention", None) or None,
        quality_score=quality_score,
        # morphic_field/holographic_entropy haben in WorkflowState heute
        # keine echte Datenquelle (der 12-Step-Export nutzt dafuer bislang
        # hartkodierte Platzhalter, siehe apps/cli/workflow/step11_export.py) -
        # bewusst None statt Uebernahme eines Platzhalters.
        morphic_field=None,
        holographic_entropy=None,
        remedy_matches=remedy_matches[:20],
    )
