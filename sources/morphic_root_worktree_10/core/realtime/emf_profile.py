from __future__ import annotations

import math
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Callable


RngBytes = Callable[[int], bytes]
TimingProbe = Callable[[int], list[float]]
SystemLoadProbe = Callable[[], float]
SensorEntropyProbe = Callable[[], tuple[float, str]]


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, float(value)))


def histogram_entropy_score(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    total = float(len(data))
    entropy = 0.0
    for count in counts:
        if count:
            p = count / total
            entropy -= p * math.log2(p)
    return clamp(entropy / 8.0)


def lag1_autocorrelation_score(data: bytes, sample_size: int = 512) -> float:
    values = [float(b) for b in data[:sample_size]]
    if len(values) < 2:
        return 0.5
    mean = sum(values) / len(values)
    den = sum((v - mean) ** 2 for v in values)
    if den <= 0:
        return 0.0
    num = sum(
        (values[i] - mean) * (values[i + 1] - mean)
        for i in range(len(values) - 1)
    )
    return clamp(1.0 - abs(num / den))


def default_timing_probe(iterations: int) -> list[float]:
    timings: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        _ = sum(i * i for i in range(50))
        t1 = time.perf_counter_ns()
        timings.append((t1 - t0) / 1e6)
    return timings


def default_system_load_probe() -> float:
    try:
        import psutil

        return clamp(
            (psutil.cpu_percent(interval=0.05) + psutil.virtual_memory().percent)
            / 200.0
        )
    except Exception:
        return 0.3


def default_sensor_entropy_probe() -> tuple[float, str]:
    return 0.5, "fallback"


def sensor_manager_entropy_probe() -> tuple[float, str]:
    try:
        from core.hardware.sensors import SensorManager

        return clamp(SensorManager().get_combined_entropy()), "ok"
    except Exception:
        return 0.5, "fallback"


def hardware_sampler_entropy_probe(
    sampler: object,
    provider_ids: list[str] | None = None,
) -> tuple[float, str]:
    try:
        samples = sampler.sample(provider_ids)
    except Exception:
        return 0.5, "fallback"
    ok_values = [
        float(getattr(sample, "value", 0.5))
        for sample in samples
        if getattr(sample, "status", "") == "ok"
    ]
    ok_values = [value for value in ok_values if math.isfinite(value)]
    if not ok_values:
        return 0.5, "fallback"
    value = round(sum(ok_values) / len(ok_values), 4)
    status = "ok" if len(ok_values) == len(samples) else "partial"
    return clamp(value), status


@dataclass
class EMFProfile:
    timestamp: str
    emf_index: float
    entropy_score: float
    timing_jitter_ms: float
    system_load: float
    sensor_entropy: float
    recommendation: str
    counter_frequencies: list[float]
    source_health: dict[str, str] = field(default_factory=dict)
    replay: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class EMFProfileService:
    def __init__(
        self,
        *,
        sample_size: int = 2048,
        timing_iterations: int = 20,
        rng_bytes: RngBytes = os.urandom,
        timing_probe: TimingProbe = default_timing_probe,
        system_load_probe: SystemLoadProbe = default_system_load_probe,
        sensor_entropy_probe: SensorEntropyProbe = default_sensor_entropy_probe,
        sensor_source: str = "fallback",
    ) -> None:
        self.sample_size = sample_size
        self.timing_iterations = timing_iterations
        self._rng_bytes = rng_bytes
        self._timing_probe = timing_probe
        self._system_load_probe = system_load_probe
        self._sensor_entropy_probe = sensor_entropy_probe
        self._sensor_source = str(sensor_source or "fallback")

    def measure(self) -> EMFProfile:
        source_health = {
            "rng": "ok",
            "cpu_timing": "ok",
            "system_load": "ok",
            "sensor_entropy": "ok",
        }
        try:
            data = self._rng_bytes(self.sample_size)
        except Exception:
            data = bytes([128]) * self.sample_size
            source_health["rng"] = "fallback"

        entropy_score = histogram_entropy_score(data)
        autocorr_score = lag1_autocorrelation_score(data)

        try:
            timings = self._timing_probe(self.timing_iterations)
            mean_t = sum(timings) / len(timings) if timings else 0.0
            jitter = (
                math.sqrt(
                    sum((t - mean_t) ** 2 for t in timings) / len(timings)
                )
                if timings
                else 0.0
            )
        except Exception:
            jitter = 0.0
            source_health["cpu_timing"] = "fallback"

        try:
            system_load = clamp(self._system_load_probe())
        except Exception:
            system_load = 0.3
            source_health["system_load"] = "fallback"

        try:
            sensor_entropy, sensor_status = self._sensor_entropy_probe()
            sensor_entropy = clamp(sensor_entropy)
            source_health["sensor_entropy"] = sensor_status or "ok"
        except Exception:
            sensor_entropy = 0.5
            source_health["sensor_entropy"] = "fallback"

        emf_index = clamp(
            0.30 * (1.0 - entropy_score)
            + 0.25 * clamp(jitter)
            + 0.20 * system_load
            + 0.10 * (1.0 - autocorr_score)
            + 0.15 * abs(sensor_entropy - 0.5) * 2.0
        )
        recommendation = (
            "hoch" if emf_index > 0.6 else "mittel" if emf_index > 0.3 else "niedrig"
        )
        counters = [528.0]
        if emf_index > 0.3:
            counters.append(741.0)
        if emf_index > 0.6:
            counters.extend([963.0, 174.0])

        return EMFProfile(
            timestamp=datetime.now().isoformat(),
            emf_index=round(emf_index, 4),
            entropy_score=round(entropy_score, 4),
            timing_jitter_ms=round(jitter, 4),
            system_load=round(system_load, 4),
            sensor_entropy=round(sensor_entropy, 4),
            recommendation=recommendation,
            counter_frequencies=counters,
            source_health=source_health,
            replay={
                "algorithm": "emf-profile-v2",
                "sample_size": self.sample_size,
                "timing_iterations": self.timing_iterations,
                "sensor_source": self._sensor_source,
            },
        )
