from __future__ import annotations

import math
import time
from typing import Dict

import numpy as np


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def sample_timer_jitter(duration_s: float = 2.0, target_samples: int = 5000) -> Dict[str, float]:
    start = time.perf_counter_ns()
    stamps = []
    while len(stamps) < max(3, target_samples):
        stamps.append(time.perf_counter_ns())
        if (stamps[-1] - start) / 1e9 >= max(0.01, duration_s):
            break

    if len(stamps) < 3:
        return {"rel_jitter": 0.0, "entropy": 0.0}

    diffs = np.diff(np.asarray(stamps, dtype=np.int64)).astype(np.float64)
    median = float(np.median(diffs)) or 1.0
    std = float(np.std(diffs))
    rel = std / abs(median)

    if std <= 0.0:
        entropy = 0.0
    else:
        bins = max(2, min(64, int(len(diffs) ** 0.5)))
        counts, _ = np.histogram(diffs, bins=bins)
        probs = counts[counts > 0].astype(np.float64)
        probs = probs / float(np.sum(probs))
        entropy = -float(np.sum(probs * np.log2(probs))) / math.log2(bins)

    return {"rel_jitter": _clamp(rel / (rel + 1.0)), "entropy": _clamp(entropy)}


def sample_cpu_mem(duration_s: float = 1.5, interval_s: float = 0.2) -> Dict[str, float]:
    samples = max(3, int(max(duration_s, 0.1) / max(interval_s, 0.01)))
    values = []
    for _ in range(samples):
        start = time.perf_counter()
        time.sleep(min(0.01, max(interval_s, 0.001)))
        values.append(time.perf_counter() - start)
    arr = np.asarray(values, dtype=np.float64)
    mean = float(np.mean(arr)) or 1.0
    rel = float(np.std(arr)) / abs(mean)
    return {"cpu_var": _clamp(rel / (rel + 1.0)), "mem_var": 0.02}


def sample_time_coherence(duration_s: float = 1.0, interval_s: float = 0.01) -> Dict[str, float]:
    perf_start = time.perf_counter()
    wall_start = time.time()
    drifts = []
    deadline = perf_start + max(0.01, duration_s)
    while time.perf_counter() < deadline:
        perf_rel = time.perf_counter() - perf_start
        wall_rel = time.time() - wall_start
        drifts.append(abs(perf_rel - wall_rel))
        time.sleep(min(0.01, max(interval_s, 0.001)))
    avg_drift = float(np.mean(drifts)) if drifts else 0.0
    return {"avg_drift": avg_drift, "coherence": _clamp(1.0 - (avg_drift / 0.05))}


def sample_h_level(max_duration_s: float = 3.5) -> float:
    timer = sample_timer_jitter(duration_s=min(0.5, max_duration_s), target_samples=512)
    cpu = sample_cpu_mem(duration_s=min(0.2, max_duration_s))
    coherence = sample_time_coherence(duration_s=min(0.2, max_duration_s))
    h = (
        0.35 * timer.get("rel_jitter", 0.0)
        + 0.25 * timer.get("entropy", 0.0)
        + 0.25 * cpu.get("cpu_var", 0.0)
        + 0.10 * cpu.get("mem_var", 0.0)
        + 0.05 * coherence.get("coherence", 0.5)
    )
    return _clamp(float(h) if math.isfinite(h) else 0.0)


def sample_hid_raw(
    vid: int = 0x0E50,
    pid: int = 0x0002,
    duration_s: float = 2.0,
    report_size: int = 64,
) -> dict:
    return {"ok": False, "reason": "hid module not available", "count": 0}


def sample_hid_level(vid: int = 0x0E50, pid: int = 0x0002, duration_s: float = 2.0) -> dict:
    return {"ok": False, "h_level": 0.0, "reason": "hid module not available", "count": 0}


def get_adaptive_h_level(
    *,
    duration_s: float = 2.0,
    prefer_qrng: bool = False,
    allow_hid: bool = True,
    vid: int = 0x0E50,
    pid: int = 0x0002,
) -> float:
    from providers.hardware.entropy_sources import select_entropy_source

    preferred = []
    if prefer_qrng:
        preferred.append("qrng")
    if allow_hid:
        preferred.append("hid_sensor")
    preferred.append("cpu_timer")
    source = select_entropy_source(preferred=preferred)
    try:
        return _clamp(source.sample_h_level(duration_s=duration_s))
    except Exception:
        return _clamp(sample_h_level(max_duration_s=duration_s))
