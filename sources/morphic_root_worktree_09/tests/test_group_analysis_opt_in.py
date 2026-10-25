from __future__ import annotations

import numpy as np
import pytest

from core.profiles.group_vector import GroupAnalysisOptIn
from core.profiles.profile import ClientProfile
from services.analysis_service import AnalysisService


def _profile() -> ClientProfile:
    return ClientProfile(
        name="Synthetic",
        first_name="Group",
        birth_date="01011990",
        birth_place="Bern",
        image_signature=None,
        planet_type="",
    )


def _service() -> AnalysisService:
    return AnalysisService(
        {"system_a": [10.0, 20.0, 30.0], "system_b": [40.0, 50.0, 60.0]},
        h_level=0.3,
    )


def test_disabled_group_opt_in_is_exactly_equivalent_to_the_default_analysis() -> None:
    service = _service()
    profile = _profile()

    default_result = service.analyze(profile)
    disabled_result = service.analyze(
        profile,
        group_opt_in=GroupAnalysisOptIn(enabled=False),
    )

    np.testing.assert_array_equal(disabled_result["rates"], default_result["rates"])
    assert disabled_result["morphic_field"] == default_result["morphic_field"]
    assert disabled_result["holographic_entropy"] == default_result["holographic_entropy"]
    np.testing.assert_array_equal(disabled_result["heim_signature"], default_result["heim_signature"])
    assert disabled_result["resonance_map"] == default_result["resonance_map"]


def test_consented_enabled_group_opt_in_changes_only_the_synthetic_analysis_result() -> None:
    service = _service()
    profile = _profile()
    default_result = service.analyze(profile)
    centroid = default_result["rates"] + 8.0

    opted_in_result = service.analyze(
        profile,
        group_opt_in=GroupAnalysisOptIn(
            enabled=True,
            centroid_rates=centroid,
            strength=0.25,
            consent_verified=True,
        ),
    )

    assert not np.array_equal(opted_in_result["rates"], default_result["rates"])
    assert opted_in_result["morphic_field"] != default_result["morphic_field"]


def test_enabled_group_opt_in_fails_closed_without_consent_or_a_centroid() -> None:
    service = _service()
    profile = _profile()
    centroid = service.encode_profile(profile) + 8.0

    with pytest.raises(ValueError, match="consent"):
        service.analyze(
            profile,
            group_opt_in=GroupAnalysisOptIn(
                enabled=True,
                centroid_rates=centroid,
                strength=0.25,
                consent_verified=False,
            ),
        )
    with pytest.raises(ValueError, match="centroid"):
        service.analyze(
            profile,
            group_opt_in=GroupAnalysisOptIn(
                enabled=True,
                centroid_rates=None,
                strength=0.25,
                consent_verified=True,
            ),
        )
