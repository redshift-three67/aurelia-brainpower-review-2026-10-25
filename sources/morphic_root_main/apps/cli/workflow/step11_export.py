"""Step 11: Ausgabe - Export in 5 Formaten + workflow_stepping.html."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .state import WorkflowState


def step_11_export(
    state: WorkflowState,
    export_dir: str = "C:\\Benutzer_Archive_Start",
    verbose: bool = True,
) -> WorkflowState:
    if verbose:
        print("  [11/12] Ausgabe (Export)...")

    try:
        from apps.cli.commands.helpers.utility_helpers import _atomic_write_text
        from apps.cli.commands.helpers.harmonization_helpers import _render_basic_html

        client_dir = (
            Path(export_dir)
            / f"{state.name}_{state.first_name}_{state.birth_date}_{state.birth_place}".strip(
                "_"
            )
        )
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = client_dir / f"{ts}_WORKFLOW_SESSION"
        session_dir.mkdir(parents=True, exist_ok=True)

        export_data = {
            "command": "workflow-scan",
            "client": {
                "name": state.name,
                "first_name": state.first_name,
                "birth_date": state.birth_date,
                "birth_place": state.birth_place,
            },
            "focus": state.focus,
            "hardware_profile": state.entropy_source_name,
            "hardware_source": state.entropy_source_name,
            "h_level": state.h_level,
            "profile": "workflow",
            "analysis": {
                "rates": state.client_rates.tolist()
                if state.client_rates is not None
                else [],
                "morphic_field": 0.0,
                "holographic_entropy": 0.3,
                "entropy_calibrated": 0.3 * 0.247,
                "heim_signature": [],
            },
            "sub_results": {
                "groups": [],
                "method": "workflow",
                "candidates": state.candidate_count,
                "top": state.matrix_results[:384],
            },
            "quantum_synergy": state.quantum_synergies,
            "personal_profile_values": {
                "emotion": state.p_emotion,
                "physisch": state.p_physisch,
                "mental": state.p_mental,
                "astral": state.p_astral,
            },
            "entropy_mode": "enhanced",
            "workflow": {
                "client_frequency": state.client_frequency,
                "signature_components": state.signature_components,
                "emf_index": state.composite_emf_index,
                "counter_frequencies": state.counter_frequencies,
                "amplifier_recommendations": state.amplifier_recommendations,
                "palette": state.palette,
                "palette_strategy": state.palette_strategy,
                "steps_completed": state.step_completed,
                "errors": state.errors,
            },
        }

        json_path = session_dir / f"{ts}_workflow_scan.json"
        html_path = session_dir / f"{ts}_workflow_scan.html"
        txt_path = session_dir / f"{ts}_workflow_scan.txt"

        json_str = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        _atomic_write_text(json_path, json_str)
        state.export_paths["json"] = str(json_path)

        html = _render_basic_html(export_data)
        _atomic_write_text(html_path, html)
        state.export_paths["html"] = str(html_path)

        txt_lines = [
            "Morphic Engine V1 - Workflow-Scan (TXT)",
            f"Klient: {state.first_name} {state.name} - {state.birth_date}, {state.birth_place}",
            f"Fokus: {state.focus or '-'}",
            f"Hardware: {state.entropy_source_name} (h_level={state.h_level:.4f})",
            f"Klienten-Frequenz: {state.client_frequency:.2f} Hz",
            f"EMF-Index: {state.composite_emf_index:.3f}",
            f"Counter-Frequenzen: {state.counter_frequencies}",
            "",
            "Amplifier-Empfehlungen:",
        ]
        for a in state.amplifier_recommendations:
            txt_lines.append(f"  - {a['name']} (score={a['score']:.3f})")
        txt_lines.extend(
            ["", "Palette:", *[f"  {i}: {c}" for i, c in enumerate(state.palette)]]
        )
        txt_lines.extend(["", f"Top-Resonanzen ({len(state.matrix_results)}):"])
        for i, e in enumerate(state.matrix_results[:20], 1):
            txt_lines.append(
                f"  {i}. {e.get('label', '?')} (score={e.get('score', 0):.4f}, level={e.get('level', '-')})"
            )
        txt_lines.extend(["", f"Quantum-Synergien: {len(state.quantum_synergies)}"])
        txt_lines.append(f"Steps abgeschlossen: {state.step_completed}")
        _atomic_write_text(txt_path, "\n".join(txt_lines))
        state.export_paths["txt"] = str(txt_path)

        # Platform-Export-Adapter (additiv, StandardAnalysisBlock-kompatibel,
        # siehe docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md).
        # Ein Fehler hier darf den bereits erfolgreichen Export oben nicht als
        # fehlgeschlagen markieren.
        try:
            from core.compliance.platform_export import (
                build_standard_output_block_from_workflow_state,
            )

            standard_block = build_standard_output_block_from_workflow_state(state)
            standard_path = session_dir / f"{ts}_standard_block.json"
            _atomic_write_text(
                standard_path,
                json.dumps(standard_block, indent=2, ensure_ascii=False, default=str),
            )
            state.export_paths["standard_block"] = str(standard_path)
            if verbose:
                print(f"        Standard-Block: {standard_path.name}")
        except Exception as adapter_exc:
            if verbose:
                print(f"        [WARN] Standard-Block-Export uebersprungen: {adapter_exc}")

        if verbose:
            print(f"        Export: {session_dir}")
            print(f"        JSON: {json_path.name}")
            print(f"        HTML: {html_path.name}")
            print(f"        TXT: {txt_path.name}")
    except Exception as exc:
        state.add_error(11, str(exc))
        if verbose:
            print(f"        [WARN] Export: {exc}")

    state.mark_step(11)
    return state
