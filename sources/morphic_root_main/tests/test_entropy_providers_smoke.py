from __future__ import annotations

from pathlib import Path

import numpy as np

_THIS_FILE = Path(__file__).resolve()
RADIALGO_ROOT = _THIS_FILE.parents[2]
ME_ROOT = _THIS_FILE.parents[1]

import sys
for p in (RADIALGO_ROOT, ME_ROOT):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

import entropy_sources as old_es  # type: ignore
import hardware_entropy as old_he  # type: ignore
from providers.hardware import entropy_sources as new_es
from providers.hardware import hardware_entropy as new_he


def test_mock_source_deterministic() -> None:
    src_old = old_es.MockSource(fixed_h=0.42)
    src_new = new_es.MockSource(fixed_h=0.42)
    h_old = src_old.sample_h_level()
    h_new = src_new.sample_h_level()
    assert np.isclose(h_old, 0.42)
    assert np.isclose(h_new, 0.42)


def test_cpu_timer_source_range() -> None:
    src_old = old_es.CpuTimerSource()
    src_new = new_es.CpuTimerSource()
    h_old = src_old.sample_h_level(duration_s=0.2)
    h_new = src_new.sample_h_level(duration_s=0.2)
    assert 0.0 <= h_old <= 1.0
    assert 0.0 <= h_new <= 1.0


def test_select_entropy_source_cpu_preference() -> None:
    src_old = old_es.select_entropy_source(preferred=["cpu_timer"])
    src_new = new_es.select_entropy_source(preferred=["cpu_timer"])
    assert src_old.name() == "cpu_timer"
    assert src_new.name() == "cpu_timer"


def test_get_adaptive_h_level_range_cpu_only() -> None:
    h_old = old_he.get_adaptive_h_level(duration_s=0.3, prefer_qrng=False, allow_hid=False)
    h_new = new_he.get_adaptive_h_level(duration_s=0.3, prefer_qrng=False, allow_hid=False)
    assert 0.0 <= h_old <= 1.0
    assert 0.0 <= h_new <= 1.0


def test_gpu_source_safe_and_bounded() -> None:
    gpu_src = new_es.GpuSource()
    cupy_mod = getattr(new_es, "cupy", None)
    if cupy_mod is None:
        # Ohne CuPy/CUDA darf die Quelle nicht als gesund melden und liefert 0.0.
        assert gpu_src.healthy() is False
        h = gpu_src.sample_h_level(duration_s=0.1)
        assert h == 0.0
    else:
        # Mit CuPy/CUDA stellen wir nur sicher, dass der Wert im gültigen Bereich liegt.
        h = gpu_src.sample_h_level(duration_s=0.1)
        assert 0.0 <= h <= 1.0


def test_select_entropy_source_gpu_then_cpu_timer() -> None:
    src = new_es.select_entropy_source(preferred=["gpu", "cpu_timer"])
    assert src.name() in ("gpu", "cpu_timer")
    if src.name() == "gpu":
        assert new_es.GpuSource().healthy()


def test_debian_server_like_selection_range() -> None:
    """Simuliert die Auswahl- und Fallback-Logik des debian_server-Profils.

    qrng/gpu werden bevorzugt, bei h<=0 wird auf cpu_timer zurückgefallen. Der
    resultierende h-Level muss immer im gültigen Bereich [0,1] liegen.
    """

    duration = 0.1
    src = new_es.select_entropy_source(preferred=["qrng", "gpu", "cpu_timer"])
    h = src.sample_h_level(duration_s=duration)
    if src.name() in ("qrng", "gpu") and h <= 0.0:
        fallback_src = new_es.select_entropy_source(preferred=["cpu_timer"])
        fallback_h = fallback_src.sample_h_level(duration_s=duration)
        if fallback_h > h:
            src = fallback_src
            h = fallback_h
    assert 0.0 <= h <= 1.0
