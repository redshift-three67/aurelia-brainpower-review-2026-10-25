"""Realer Qiskit-Grover-Pfad-Test.

Wird nur ausgefuehrt, wenn Qiskit verfuegbar ist (optionales Extra
`pip install .[quantum]`). Im Default-dev-Environment ohne Qiskit bleibt
der Test inaktiv (skip), damit die Standardsuite nicht von der optionalen
Abhaengigkeit abhaengt.

Dokumentiert in:
- `docs/deep-audit-2026-07-05/PHASE_8_QUANTUM_FRAMEWORK_TIEFENANALYSE.md`
- `docs/deep-audit-2026-07-05/QISKIT_VERIFICATION_LOG.md`
"""

from __future__ import annotations

import pytest

from core.quantum_synergy.grover_search import (
    QISKIT_AVAILABLE,
    GroverRemedySearch,
)


pytestmark = pytest.mark.skipif(
    not QISKIT_AVAILABLE,
    reason="qiskit nicht installiert - Real-Pfad-Test inaktiv (optionales Extra).",
)


def test_real_grover_circuit_runs_and_amplifies_single_marked_item() -> None:
    """Ein markiertes Item von 8 muss durch Amplitudenverstaerkung das
    Top-Ergebnis werden. Das ist der schärfste Test fuer korrektes
    Grover-Verhalten und wurde manuell am 2026-07-06 mit qiskit 2.5.0
    verifiziert (siehe QISKIT_VERIFICATION_LOG.md)."""

    items = [{"label": f"item{i}", "group": "x", "score": 1.0} for i in range(8)]

    def oracle(item: dict) -> bool:
        return item["label"] == "item5"

    searcher = GroverRemedySearch(verbose=False)
    results = searcher.search(items, oracle, max_results=8, shots=4000)

    assert results, "Real-Pfad lieferte keine Ergebnisse"
    top_item, top_prob = results[0]
    assert top_item["label"] == "item5"
    assert top_prob > 0.5, f"markiertes Item nicht deutlich verstaerkt: {top_prob}"


def test_real_grover_circuit_handles_empty_items() -> None:
    searcher = GroverRemedySearch(verbose=False)
    results = searcher.search([], lambda item: True, max_results=5, shots=64)
    assert results == []
