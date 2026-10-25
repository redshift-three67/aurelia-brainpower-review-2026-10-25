"""Tests fuer core.compliance.platform_export (StandardAnalysisBlock-Adapter)."""

from __future__ import annotations

from core.compliance.platform_export import (
    build_standard_output_block,
    build_standard_output_block_from_workflow_state,
)


def test_build_standard_output_block_has_contracted_shape() -> None:
    block = build_standard_output_block(
        profiles=["Bronchien"],
        focus="Bronchien",
        intention="harmonization",
        quality_score=7.5,
        morphic_field=0.42,
        holographic_entropy=0.31,
        remedy_matches=[("Arnica", 8.1), ("Belladonna", 6.4)],
        timestamp="2026-07-06T10:00:00Z",
    )

    assert set(block.keys()) == {"inputs", "outputs", "meta"}
    assert block["inputs"] == {
        "profiles": ["Bronchien"],
        "focus": "Bronchien",
        "intention": "harmonization",
    }
    assert block["outputs"]["quality_score"] == 7.5
    assert block["outputs"]["morphic_field"] == 0.42
    assert block["outputs"]["holographic_entropy"] == 0.31
    assert block["outputs"]["remedy_matches"] == [["Arnica", 8.1], ["Belladonna", 6.4]]
    assert block["meta"] == {
        "timestamp": "2026-07-06T10:00:00Z",
        "source_system": "MORPHIC_V1",
    }


def test_build_standard_output_block_defaults_are_empty_not_fabricated() -> None:
    block = build_standard_output_block()

    assert block["inputs"] == {"profiles": [], "focus": None, "intention": None}
    assert block["outputs"]["quality_score"] is None
    assert block["outputs"]["morphic_field"] is None
    assert block["outputs"]["holographic_entropy"] is None
    assert block["outputs"]["remedy_matches"] == []
    assert block["meta"]["source_system"] == "MORPHIC_V1"
    assert block["meta"]["timestamp"]


def test_build_standard_output_block_from_workflow_state_extracts_remedy_matches() -> None:
    class FakeState:
        focus = "Bronchien"
        intention = "harmonization"
        matrix_results = [
            {"label": "Arnica", "score": 8.1},
            {"label": "Belladonna", "score": 6.4},
            {"label": "no-score-here"},
        ]
        quantum_synergies = [{"score": 7.0}, {"score": 9.0}]

    block = build_standard_output_block_from_workflow_state(FakeState())

    assert block["inputs"]["focus"] == "Bronchien"
    assert block["inputs"]["intention"] == "harmonization"
    assert block["outputs"]["remedy_matches"] == [["Arnica", 8.1], ["Belladonna", 6.4]]
    assert block["outputs"]["quality_score"] == 8.0
    assert block["outputs"]["morphic_field"] is None
    assert block["outputs"]["holographic_entropy"] is None


def test_build_standard_output_block_from_workflow_state_handles_empty_state() -> None:
    class EmptyState:
        pass

    block = build_standard_output_block_from_workflow_state(EmptyState())

    assert block["outputs"]["remedy_matches"] == []
    assert block["outputs"]["quality_score"] is None
    assert block["inputs"]["focus"] is None
