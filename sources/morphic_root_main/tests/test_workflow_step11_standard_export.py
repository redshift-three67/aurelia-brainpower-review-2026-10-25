"""Integrationstest: Step 11 des 12-Step-Workflows schreibt zusaetzlich
einen StandardAnalysisBlock-kompatiblen Ausgabeblock (additiv)."""

from __future__ import annotations

import json
from pathlib import Path

from apps.cli.workflow.state import WorkflowState
from apps.cli.workflow.step11_export import step_11_export


def test_step_11_export_writes_standard_block_alongside_existing_exports(
    tmp_path: Path,
) -> None:
    state = WorkflowState(
        name="Mustermann",
        first_name="Klaus",
        birth_date="09041966",
        birth_place="Augsburg",
        focus="Bronchien",
        intention="harmonization",
        matrix_results=[
            {"label": "Arnica", "score": 8.1, "level": "primary"},
            {"label": "Belladonna", "score": 6.4, "level": "secondary"},
        ],
        quantum_synergies=[{"score": 7.0}, {"score": 9.0}],
    )

    result = step_11_export(state, export_dir=str(tmp_path), verbose=False)

    assert result.errors == []
    assert "json" in result.export_paths
    assert "standard_block" in result.export_paths

    standard_path = Path(result.export_paths["standard_block"])
    assert standard_path.exists()
    assert standard_path.parent == Path(result.export_paths["json"]).parent

    block = json.loads(standard_path.read_text(encoding="utf-8"))
    assert set(block.keys()) == {"inputs", "outputs", "meta"}
    assert block["inputs"]["focus"] == "Bronchien"
    assert block["outputs"]["remedy_matches"] == [
        ["Arnica", 8.1],
        ["Belladonna", 6.4],
    ]
    assert block["meta"]["source_system"] == "MORPHIC_V1"
