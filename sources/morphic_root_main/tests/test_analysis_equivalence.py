from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Iterable

import numpy as np

# Pfade so setzen, dass sowohl der alte Pipeline-Code als auch der neue Core gefunden werden.
_THIS_FILE = Path(__file__).resolve()
RADIALGO_ROOT = _THIS_FILE.parents[2]
ME_ROOT = _THIS_FILE.parents[1]

for p in (RADIALGO_ROOT, ME_ROOT):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

import resonance_pipeline as old_rp  # type: ignore
from core.profiles.profile import ClientProfile as NewClientProfile
from services.analysis_service import AnalysisService


def _sample_rate_db() -> Dict[str, Iterable[float]]:
    return {
        "system_a": [10.0, 20.0, 30.0],
        "system_b": [40.0, 50.0, 60.0],
    }


def test_core_matches_old_for_sample_profile() -> None:
    rate_db = _sample_rate_db()
    h_level = 0.3

    # Profil für alte Pipeline
    old_profile = old_rp.ClientProfile(
        name="Mustermann",
        first_name="Max",
        birth_date="09031999",
        birth_place="Muenchen",
        image_signature=None,
    )

    # Profil für neue Engine
    new_profile = NewClientProfile(
        name="Mustermann",
        first_name="Max",
        birth_date="09031999",
        birth_place="Muenchen",
        image_signature=None,
    )

    old_pipeline = old_rp.ResonancePipeline(rate_db, h_level=h_level)
    old_res = old_pipeline.analyze(old_profile)

    service = AnalysisService(rate_db, h_level=h_level)
    new_res = service.analyze(new_profile)

    # Raten
    np.testing.assert_allclose(new_res["rates"], old_res["rates"], rtol=1e-10, atol=1e-10)

    # Skalar-Metriken
    assert np.isclose(new_res["morphic_field"], old_res["morphic_field"], rtol=1e-10, atol=1e-10)
    assert np.isclose(
        new_res["holographic_entropy"],
        old_res["holographic_entropy"],
        rtol=1e-10,
        atol=1e-10,
    )

    # Heim-Signatur
    np.testing.assert_allclose(
        new_res["heim_signature"],
        old_res["heim_signature"],
        rtol=1e-10,
        atol=1e-10,
    )

    # Resonanzkarte
    old_map = old_res["resonance_map"]
    new_map = new_res["resonance_map"]
    assert set(old_map.keys()) == set(new_map.keys())
    for key in old_map.keys():
        assert np.isclose(new_map[key], old_map[key], rtol=1e-10, atol=1e-10)
