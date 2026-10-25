from __future__ import annotations

import math
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from numbers import Real
from typing import Callable

from core.hardware.drivers import VALID_STATUSES as DRIVER_VALID_STATUSES


DEFAULT_SAMPLE_SIZE = 2048
DEFAULT_TIMING_ITERATIONS = 20
MAX_SAMPLE_SIZE = 1024 * 1024
MAX_TIMING_ITERATIONS = 100_000
RngBytes = Callable[[int], bytes]
TimingProbe = Callable[[int], list[float]]
SystemLoadProbe = Callable[[], float]
SensorEntropyProbe = Callable[[], tuple[float, str]]
SENSOR_HEALTH_STATUSES = frozenset({"ok", "partial", "fallback"})
HARDWARE_SAMPLE_STATUSES = frozenset(DRIVER_VALID_STATUSES)


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, float(value)))


def _is_finite_real(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, Real):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def _bounded_effective_length(
    requested: object,
    default: int,
    maximum: int,
) -> tuple[int, bool]:
    if type(requested) is int and 0 < requested <= maximum:
        return requested, True
    return default, False


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
    import psutil

    return (
        psutil.cpu_percent(interval=0.05) + psutil.virtual_memory().percent
    ) / 200.0


def default_sensor_entropy_probe() -> tuple[float, str]:
    return 0.5, "fallback"


def sensor_manager_entropy_probe() -> tuple[float, str]:
    try:
        from core.hardware.sensors import SensorManager

        value = SensorManager().get_combined_entropy()
        if not _is_finite_real(value):
            return 0.5, "fallback"
        return clamp(value), "ok"
    except Exception:
        return 0.5, "fallback"


def hardware_sampler_entropy_probe(
    sampler: object,
    provider_ids: list[str] | None = None,
) -> tuple[float, str]:
    try:
        samples = sampler.sample(provider_ids)
        if type(samples) is not list or not samples:
            raise ValueError("invalid hardware samples")

        ok_values: list[Real] = []
        for sample in samples:
            sample_status = getattr(sample, "status")
            if (
                type(sample_status) is not str
                or sample_status not in HARDWARE_SAMPLE_STATUSES
            ):
                raise ValueError("invalid hardware sample status")
            if sample_status != "ok":
                continue
            sample_value = getattr(sample, "value")
            if not _is_finite_real(sample_value):
                raise ValueError("invalid hardware sample value")
            ok_values.append(sample_value)

        if not ok_values:
            raise ValueError("no healthy hardware samples")
        value = math.fsum(ok_values) / len(ok_values)
        if not _is_finite_real(value):
            raise ValueError("invalid hardware sample average")
        value = round(value, 4)
        status = "ok" if len(ok_values) == len(samples) else "partial"
        return clamp(value), status
    except Exception:
        return 0.5, "fallback"


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
        sample_size: int = DEFAULT_SAMPLE_SIZE,
        timing_iterations: int = DEFAULT_TIMING_ITERATIONS,
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
        sample_size, sample_size_valid = _bounded_effective_length(
            self.sample_size,
            DEFAULT_SAMPLE_SIZE,
            MAX_SAMPLE_SIZE,
        )
        timing_iterations, timing_iterations_valid = _bounded_effective_length(
            self.timing_iterations,
            DEFAULT_TIMING_ITERATIONS,
            MAX_TIMING_ITERATIONS,
        )
        source_health = {
            "rng": "ok",
            "cpu_timing": "ok",
            "system_load": "ok",
            "sensor_entropy": "ok",
        }
        try:
            if not sample_size_valid:
                raise ValueError("invalid sample size")
            probe_data = self._rng_bytes(sample_size)
            if type(probe_data) is not bytes or len(probe_data) != sample_size:
                raise ValueError("invalid RNG probe result")
            data = probe_data
        except Exception:
            data = bytes([128]) * sample_size
            source_health["rng"] = "fallback"

        entropy_score = histogram_entropy_score(data)
        autocorr_score = lag1_autocorrelation_score(data)

        try:
            if not timing_iterations_valid:
                raise ValueError("invalid timing iteration count")
            timings = self._timing_probe(timing_iterations)
            if (
                type(timings) is not list
                or len(timings) != timing_iterations
                or not all(_is_finite_real(timing) and timing >= 0 for timing in timings)
            ):
                raise ValueError("invalid timing probe result")
            mean_t = sum(timings) / len(timings)
            if not _is_finite_real(mean_t):
                raise ValueError("invalid timing mean")
            jitter = math.sqrt(
                sum((timing - mean_t) ** 2 for timing in timings) / len(timings)
            )
            if not _is_finite_real(jitter):
                raise ValueError("invalid timing jitter")
        except Exception:
            jitter = 0.0
            source_health["cpu_timing"] = "fallback"

        try:
            probed_system_load = self._system_load_probe()
            if not _is_finite_real(probed_system_load):
                raise ValueError("invalid system load probe result")
            system_load = clamp(probed_system_load)
        except Exception:
            system_load = 0.3
            source_health["system_load"] = "fallback"

        try:
            sensor_result = self._sensor_entropy_probe()
            if type(sensor_result) is not tuple or len(sensor_result) != 2:
                raise ValueError("invalid sensor probe shape")
            probed_sensor_entropy, sensor_status = sensor_result
            if (
                not _is_finite_real(probed_sensor_entropy)
                or sensor_status not in SENSOR_HEALTH_STATUSES
            ):
                raise ValueError("invalid sensor probe result")
            sensor_entropy = clamp(probed_sensor_entropy)
            source_health["sensor_entropy"] = sensor_status
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
                "sample_size": sample_size,
                "timing_iterations": timing_iterations,
                "sensor_source": self._sensor_source,
            },
        )
