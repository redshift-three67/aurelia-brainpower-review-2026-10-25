"""Step 09: Quantum-Synergy - Delegiert an QuantumSynergyEngine (Kernengine)."""

from __future__ import annotations

import contextlib
import io

from .state import WorkflowState


def step_09_quantum(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    if verbose:
        print("  [9/12] Quantum-Synergy...")

    try:
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            from core.quantum_synergy.hybrid_engine import QuantumSynergyEngine

            engine = QuantumSynergyEngine(use_quantum=True)
        # Ehrliche Klassifikation: "real" nur, wenn der Engine tatsaechlich
        # Qiskit nutzt (QISKIT_AVAILABLE). Sonst "classical" - kein
        # Vortaeuschen von Quanten-Ausfuehrung, die nicht stattfindet.
        # Siehe docs/deep-audit-2026-07-05/PHASE_8_QUANTUM_FRAMEWORK_TIEFENANALYSE.md.
        state.quantum_mode = "real" if engine.use_quantum else "classical"
        top_items = state.matrix_results[:32] if state.matrix_results else []
        if top_items:
            scan_results = {
                str(item.get("label", "")): float(item.get("score", 0.0) or 0.0)
                for item in top_items
                if item.get("label")
            }
            with (
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                synergies = engine.find_synergistic_triggers(
                    focus=state.focus or "workflow",
                    scan_results=scan_results,
                    combination_size=4,
                    top_n=10,
                    threshold=6.0,
                )
            for combo_items, combo_score, details in synergies[:10]:
                state.quantum_synergies.append(
                    {
                        "items": [
                            {"label": i.get("label", ""), "group": i.get("group", "")}
                            for i in combo_items
                        ],
                        "score": combo_score,
                        "category": "primary" if combo_score >= 7.0 else "secondary",
                        "components": details if isinstance(details, dict) else {},
                    }
                )
        if verbose:
            print(f"        Synergien: {len(state.quantum_synergies)}")
    except Exception as exc:
        state.add_error(9, str(exc))
        if verbose:
            print(f"        [WARN] Quantum-Synergy: {exc}")

    state.mark_step(9)
    return state
