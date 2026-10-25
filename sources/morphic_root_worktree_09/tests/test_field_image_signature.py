from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from core.profiles.profile import ClientProfile
from services.analysis_service import AnalysisService


Image = pytest.importorskip("PIL.Image")


def _profile(image_signature: np.ndarray | None) -> ClientProfile:
    return ClientProfile(
        name="Muster",
        first_name="Alex",
        birth_date="01011990",
        birth_place="Bern",
        image_signature=image_signature,
    )


def test_field_image_signature_is_deterministic_and_score_effective(tmp_path: Path) -> None:
    from apps.cli.commands.field import _load_image_signature

    image_path = tmp_path / "synthetic-client.jpg"
    pixels = np.arange(64, dtype=np.uint8).reshape(8, 8) * 4
    Image.fromarray(pixels, mode="L").save(image_path, format="JPEG")

    first = _load_image_signature(str(image_path))
    second = _load_image_signature(str(image_path))

    assert first is not None
    assert first.shape == (32, 32)
    np.testing.assert_array_equal(first, second)

    service = AnalysisService(rate_database={})
    image_rates = service.encode_profile(_profile(first))
    default_rates = service.encode_profile(_profile(None))

    assert not np.array_equal(image_rates, default_rates)


def test_field_image_signature_returns_none_for_missing_path(tmp_path: Path) -> None:
    from apps.cli.commands.field import _load_image_signature

    assert _load_image_signature(str(tmp_path / "missing-client.jpg")) is None
