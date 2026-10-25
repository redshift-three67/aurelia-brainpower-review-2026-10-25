"""Tests fuer apps.cli.workflow.substep_manifest."""

from __future__ import annotations

import pytest

from apps.cli.workflow.substep_manifest import (
    SUBSTEP_MANIFEST,
    UNMAPPED_RADIMORPHIC_SUBSTEPS,
    get_radimorphic_equivalent,
)


def test_manifest_covers_all_12_morphic_steps_in_order() -> None:
    steps = [entry["morphic_step"] for entry in SUBSTEP_MANIFEST]

    assert steps == [f"step{n:02d}_{suffix}" for n, suffix in enumerate(
        [
            "init", "input", "signature", "focus", "emf", "amplifier",
            "palette", "matrix", "quantum", "post", "export", "harmonize",
        ],
        start=1,
    )]
    assert [entry["morphic_step_index"] for entry in SUBSTEP_MANIFEST] == list(range(1, 13))


def test_get_radimorphic_equivalent_returns_mapped_value() -> None:
    assert get_radimorphic_equivalent("step09_quantum") == "quantum_modulation"
    assert get_radimorphic_equivalent("step11_export") == "export"


def test_get_radimorphic_equivalent_returns_none_when_no_honest_mapping_exists() -> None:
    assert get_radimorphic_equivalent("step06_amplifier") is None
    assert get_radimorphic_equivalent("step07_palette") is None
    assert get_radimorphic_equivalent("step12_harmonize") is None


def test_get_radimorphic_equivalent_raises_for_unknown_step() -> None:
    with pytest.raises(KeyError):
        get_radimorphic_equivalent("step99_does_not_exist")


def test_unmapped_radimorphic_substeps_are_not_claimed_elsewhere() -> None:
    mapped_targets = {
        entry["radimorphic_substep"]
        for entry in SUBSTEP_MANIFEST
        if entry["radimorphic_substep"] is not None
    }

    assert mapped_targets.isdisjoint(UNMAPPED_RADIMORPHIC_SUBSTEPS)
