from __future__ import annotations

import math
import time as _time
from typing import Sequence

from .config_types import MorphicFieldConfig, MorphicFieldResult, QuantumState


HBAR: float = 1.054571817e-34


_GEOMETRIC_FACTORS = {
    "tetrahedron": 1.618,
    "cube": 1.732,
    "octahedron": 2.0,
    "dodecahedron": 2.618,
    "icosahedron": 2.236,
    "merkaba": 3.141,
    "torus": 1.414,
    "flower_of_life": 2.718,
    "sri_yantra": 3.0,
}


_INTENTION_FACTORS = {
    "healing": 1.272,
    "manifestation": 1.618,
    "protection": 1.414,
    "transformation": 2.236,
    "connection": 2.0,
    "clearing": 1.732,
    "activation": 2.718,
    "harmonization": 1.618,
}


def _now_seconds() -> float:
    return float(_time.time())


def generate_default_quantum_states(n: int = 5) -> list[QuantumState]:
    if n <= 0:
        return []
    amplitude = 1.0 / math.sqrt(float(n))
    base_energy = 1.6e-19
    states: list[QuantumState] = []
    for k in range(1, n + 1):
        energy = base_energy * (k * k)
        phase = math.pi * float(k) / float(n + 1)
        states.append(QuantumState(amplitude=amplitude, energy=energy, phase=phase))
    return states


def calculate_quantum_superposition(
    states: Sequence[QuantumState],
    time_seconds: float | None = None,
) -> float:
    if not states:
        return 0.0
    t = float(time_seconds) if time_seconds is not None else _now_seconds()
    real_part = 0.0
    imag_part = 0.0
    for state in states:
        phase = -(state.energy * t) / HBAR + state.phase
        cos_p = math.cos(phase)
        sin_p = math.sin(phase)
        real_part += state.amplitude * cos_p
        imag_part += state.amplitude * sin_p
    magnitude = math.hypot(real_part, imag_part)
    return magnitude / math.sqrt(float(len(states)))


def calculate_numerical_factor(sequence: Sequence[float]) -> float:
    values = [float(v) for v in sequence if v is not None]
    if not values:
        return 1.0

    harmonic_sum = 0.0
    for v in values:
        x = abs(v) if v != 0.0 else 1.0
        harmonic_sum += 1.0 / x
    harmonic_mean = len(values) / harmonic_sum if harmonic_sum > 0.0 else 1.0

    log_sum = 0.0
    for v in values:
        x = abs(v) if v != 0.0 else 1.0
        log_sum += math.log(x)
    geometric_mean = math.exp(log_sum / float(len(values)))

    factor = math.sqrt(harmonic_mean * geometric_mean) / 10000.0
    return max(0.1, min(10.0, factor))


def calculate_geometric_factor(geometric_form: str) -> float:
    key = (geometric_form or "").strip().lower()
    return _GEOMETRIC_FACTORS.get(key, 1.0)


def calculate_intention_factor(intention: str) -> float:
    key = (intention or "").strip().lower()
    return _INTENTION_FACTORS.get(key, 1.0)


def calculate_coherence(
    quantum_component: float,
    numerical_factor: float,
    geometric_factor: float,
    intention_factor: float,
) -> float:
    factors = [
        float(quantum_component),
        float(numerical_factor),
        float(geometric_factor),
        float(intention_factor),
    ]
    mean = sum(factors) / float(len(factors))
    variance = sum((x - mean) ** 2 for x in factors) / float(len(factors))
    std_dev = math.sqrt(max(variance, 0.0))
    coherence = 1.0 / (1.0 + std_dev)
    return max(0.0, min(1.0, coherence))


def calculate_resonance_frequency(
    quantum_states: Sequence[QuantumState],
    numerical_sequence: Sequence[float],
) -> float:
    base_freq = 0.0
    if quantum_states:
        avg_energy = sum(s.energy for s in quantum_states) / float(len(quantum_states))
        base_freq = avg_energy / HBAR if HBAR != 0.0 else 0.0

    seq_modulation = 1.0
    if numerical_sequence:
        avg_seq = sum(float(v) for v in numerical_sequence) / float(len(numerical_sequence))
        seq_modulation = avg_seq / 1_000_000.0

    frequency = abs(base_freq * seq_modulation)
    if frequency <= 0.0:
        return 1.0
    return max(1.0, min(1_000_000.0, frequency))


def calculate_morphic_field(
    config: MorphicFieldConfig,
    metrics_combined_score: float | None = None,
) -> MorphicFieldResult:
    states = config.quantum_states or generate_default_quantum_states()
    t = config.time if config.time is not None else _now_seconds()

    quantum_component = calculate_quantum_superposition(states, t)
    numerical_factor = calculate_numerical_factor(config.numerical_sequence)
    geometric_factor = calculate_geometric_factor(config.geometric_form)
    intention_factor = calculate_intention_factor(config.intention)

    hardware_factor: float | None = None
    if config.use_hardware_modulation and metrics_combined_score is not None:
        hardware_factor = 1.0 + float(metrics_combined_score) / 100.0
        hardware_factor = max(0.5, min(1.5, hardware_factor))

    total_wave_function = (
        quantum_component
        * numerical_factor
        * geometric_factor
        * intention_factor
        * (hardware_factor if hardware_factor is not None else 1.0)
    )

    coherence = calculate_coherence(
        quantum_component,
        numerical_factor,
        geometric_factor,
        intention_factor,
    )
    resonance_frequency = calculate_resonance_frequency(states, config.numerical_sequence)
    field_strength = total_wave_function * coherence

    timestamp = t
    return MorphicFieldResult(
        total_wave_function=total_wave_function,
        quantum_component=quantum_component,
        numerical_factor=numerical_factor,
        geometric_factor=geometric_factor,
        intention_factor=intention_factor,
        hardware_factor=hardware_factor,
        coherence=coherence,
        resonance_frequency=resonance_frequency,
        field_strength=field_strength,
        timestamp=timestamp,
    )


def test_morphic_resonance(
    config1: MorphicFieldConfig,
    config2: MorphicFieldConfig,
    metrics1_combined_score: float | None = None,
    metrics2_combined_score: float | None = None,
) -> float:
    result1 = calculate_morphic_field(config1, metrics1_combined_score)
    result2 = calculate_morphic_field(config2, metrics2_combined_score)

    if result1.resonance_frequency <= 0.0 or result2.resonance_frequency <= 0.0:
        freq_ratio = 0.0
    else:
        ratio1 = result1.resonance_frequency / result2.resonance_frequency
        ratio2 = result2.resonance_frequency / result1.resonance_frequency
        freq_ratio = min(ratio1, ratio2)

    if result1.field_strength <= 0.0 or result2.field_strength <= 0.0:
        strength_ratio = 0.0
    else:
        s1 = result1.field_strength / result2.field_strength
        s2 = result2.field_strength / result1.field_strength
        strength_ratio = min(s1, s2)

    coherence_avg = (result1.coherence + result2.coherence) / 2.0
    resonance = freq_ratio * 0.4 + strength_ratio * 0.4 + coherence_avg * 0.2
    return max(0.0, min(1.0, resonance))
