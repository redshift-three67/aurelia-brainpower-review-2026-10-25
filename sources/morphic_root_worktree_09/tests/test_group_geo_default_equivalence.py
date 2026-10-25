from __future__ import annotations

import numpy as np

from core.profiles.profile import ClientProfile
from services.analysis_service import AnalysisService


def test_group_geo_future_work_preserves_frozen_default_analysis_baseline() -> None:
    profile = ClientProfile(
        name="Baseline",
        first_name="Vector",
        birth_date="01011990",
        birth_place="Bern",
        image_signature=None,
        planet_type="",
    )
    service = AnalysisService(
        {"system_a": [10.0, 20.0, 30.0], "system_b": [40.0, 50.0, 60.0]},
        h_level=0.3,
    )

    result = service.analyze(profile)

    np.testing.assert_allclose(
        result["rates"],
        [3.0, 0.0, 1.0, 28.0, 82.0, 11.394335230683666, 14.61280356782379, 17.609125905568135, 0.0, 0.0],
        rtol=0.0,
        atol=1e-12,
    )
    assert result["morphic_field"] == pytest_approx(0.18627041161627866)
    assert result["holographic_entropy"] == pytest_approx(1.5862843893175127)
    np.testing.assert_allclose(
        result["heim_signature"],
        [1.3333333333333333, 40.464778410227886, 16.110964736695962, 0.0],
        rtol=0.0,
        atol=1e-12,
    )
    assert result["resonance_map"] == {
        "system_a": pytest_approx(1.6564453199398308),
        "system_b": pytest_approx(0.07393820917032262),
    }


def pytest_approx(value: float):
    import pytest

    return pytest.approx(value, rel=0.0, abs=1e-12)
