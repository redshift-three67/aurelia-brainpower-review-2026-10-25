from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from core.profiles.group_vector import (
    GroupMemberRates,
    blend_group_centroid,
    build_group_centroid,
)


ROOT = Path(__file__).resolve().parents[1]


def _member(client_id: str, rates: list[float], *, consent_recorded: bool = True) -> GroupMemberRates:
    return GroupMemberRates(
        client_id=client_id,
        rates=np.asarray(rates, dtype=float),
        consent_recorded=consent_recorded,
    )


def test_group_centroid_is_deterministic_pseudonymous_and_order_invariant() -> None:
    members = [
        _member("cli-alpha", [10.0, 20.0, 30.0]),
        _member("cli-beta", [20.0, 40.0, 60.0]),
    ]

    first = build_group_centroid(members)
    second = build_group_centroid(list(reversed(members)))

    np.testing.assert_array_equal(first, [15.0, 30.0, 45.0])
    np.testing.assert_array_equal(first, second)


def test_group_centroid_rejects_missing_consent_duplicate_members_bad_lengths_and_nonfinite_rates() -> None:
    invalid_memberships = (
        [_member("cli-alpha", [10.0, 20.0, 30.0])],
        [
            _member("cli-alpha", [10.0, 20.0, 30.0], consent_recorded=False),
            _member("cli-beta", [20.0, 40.0, 60.0]),
        ],
        [
            _member("cli-alpha", [10.0, 20.0, 30.0]),
            _member("cli-alpha", [20.0, 40.0, 60.0]),
        ],
        [
            _member("cli-alpha", [10.0, 20.0]),
            _member("cli-beta", [20.0, 40.0, 60.0]),
        ],
        [
            _member("cli-alpha", [10.0, np.nan, 30.0]),
            _member("cli-beta", [20.0, 40.0, 60.0]),
        ],
    )

    for members in invalid_memberships:
        with pytest.raises(ValueError):
            build_group_centroid(members)


def test_group_blend_preserves_an_exact_baseline_at_zero_strength() -> None:
    baseline = np.asarray([10.0, 20.0, 30.0])
    centroid = np.asarray([30.0, 40.0, 50.0])

    blended = blend_group_centroid(baseline, centroid, strength=0.0)

    np.testing.assert_array_equal(blended, baseline)
    assert blended is not baseline


def test_group_blend_interpolates_only_when_explicitly_given_a_strength() -> None:
    baseline = np.asarray([10.0, 20.0, 30.0])
    centroid = np.asarray([30.0, 40.0, 50.0])

    blended = blend_group_centroid(baseline, centroid, strength=0.25)

    np.testing.assert_array_equal(blended, [15.0, 25.0, 35.0])


def test_group_blend_rejects_invalid_strength_shapes_and_nonfinite_values() -> None:
    baseline = np.asarray([10.0, 20.0, 30.0])
    centroid = np.asarray([30.0, 40.0, 50.0])

    for strength in (-0.01, 1.01, np.nan, np.inf):
        with pytest.raises(ValueError):
            blend_group_centroid(baseline, centroid, strength=strength)
    with pytest.raises(ValueError):
        blend_group_centroid(baseline, centroid[:2], strength=0.25)
    with pytest.raises(ValueError):
        blend_group_centroid(baseline, np.asarray([30.0, np.nan, 50.0]), strength=0.25)


def test_group_vector_productive_integration_remains_handle_only_at_external_boundaries() -> None:
    external_paths = (
        ROOT / "apps" / "web" / "launcher.py",
        ROOT / "core" / "compliance" / "run_manifest.py",
    )

    for path in external_paths:
        source = path.read_text(encoding="utf-8")
        assert "group_vector" not in source
        assert "GroupAnalysisOptIn" not in source
        assert "blend_group_centroid" not in source

    for path in (
        ROOT / "apps" / "cli" / "commands" / "field.py",
        ROOT / "apps" / "web" / "main.py",
    ):
        source = path.read_text(encoding="utf-8")
        assert "blend_group_centroid" not in source
        assert "group_member_rates" not in source
        assert "centroid_rates" not in source
