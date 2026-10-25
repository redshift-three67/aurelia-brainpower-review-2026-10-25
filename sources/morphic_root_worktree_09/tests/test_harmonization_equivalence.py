from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Any

import numpy as np

_THIS_FILE = Path(__file__).resolve()
RADIALGO_ROOT = _THIS_FILE.parents[2]
ME_ROOT = _THIS_FILE.parents[1]

import sys
for p in (RADIALGO_ROOT, ME_ROOT):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

import resonance_pipeline as old_rp  # type: ignore
from core.profiles.profile import ClientProfile as NewClientProfile
from services.analysis_service import AnalysisService
from services.harmonization_service import HarmonizationService


def _sample_rate_db() -> Dict[str, Iterable[float]]:
    return {
        "system_a": [10.0, 20.0, 30.0],
        "system_b": [40.0, 50.0, 60.0],
        "system_c": [70.0, 80.0, 90.0],
    }


def test_harmonization_matches_old_for_sample_profile() -> None:
    rate_db = _sample_rate_db()
    h_level = 0.3

    old_profile = old_rp.ClientProfile(
        name="Mustermann",
        first_name="Max",
        birth_date="09031999",
        birth_place="Muenchen",
        image_signature=None,
    )

    new_profile = NewClientProfile(
        name="Mustermann",
        first_name="Max",
        birth_date="09031999",
        birth_place="Muenchen",
        image_signature=None,
    )

    old_pipeline = old_rp.ResonancePipeline(rate_db, h_level=h_level)
    old_analysis: dict[str, Any] = old_pipeline.analyze(old_profile)
    old_harm = old_pipeline.harmonize(old_profile, old_analysis, targets=None)

    analysis_service = AnalysisService(rate_db, h_level=h_level)
    new_analysis = analysis_service.analyze(new_profile)

    harm_service = HarmonizationService(rate_db, h_level=h_level)
    new_harm = harm_service.harmonize(new_profile, new_analysis, targets=None)

    assert old_harm["status"] == new_harm["status"]

    # base_inverse ist eine Matrix; wir erwarten gleiche Form und Werte
    np.testing.assert_allclose(
        new_harm["base_inverse"],
        old_harm["base_inverse"],
        rtol=1e-10,
        atol=1e-10,
    )

    np.testing.assert_allclose(
        new_harm["adaptive_rates"],
        old_harm["adaptive_rates"],
        rtol=1e-10,
        atol=1e-10,
    )

    np.testing.assert_allclose(
        new_harm["optimized_rates"],
        old_harm["optimized_rates"],
        rtol=1e-10,
        atol=1e-10,
    )
