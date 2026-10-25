from __future__ import annotations

from typing import Iterable

import numpy as np
from ..profiles.profile import ClientProfile
from ..resonance.resonator import MorphicFieldResonator


class HarmonizationEngine:
    def __init__(self, resonator: MorphicFieldResonator) -> None:
        self.resonator = resonator

    def inverse_rates(self, rates: np.ndarray) -> np.ndarray:
        return (100 - rates) % 100

    def adaptive_loop(
        self,
        profile: ClientProfile,
        base_rates: np.ndarray,
        max_iter: int = 60,
        threshold: float = 0.78,
    ) -> np.ndarray:
        tuned = base_rates.copy()
        for _ in range(max_iter):
            state = self._simulate_biofeedback(profile, tuned)
            if state >= threshold:
                break
            gradient = (threshold - state) * 0.015
            tuned = (tuned + gradient) % 100
        return tuned

    def holographic_optimize(self, rate_matrix: np.ndarray) -> np.ndarray:
        reference = np.mean(rate_matrix, axis=0)
        interference = rate_matrix * np.conj(reference)
        optimized = np.real(interference) + 1j * np.imag(rate_matrix)
        return np.real(np.mean(optimized, axis=0))

    def _simulate_biofeedback(self, profile: ClientProfile, rates: np.ndarray) -> float:
        variance_term = np.exp(-np.var(rates) / 800)
        name_factor = (len(profile.name) + len(profile.first_name)) % 7 / 7
        return float(0.5 + 0.4 * variance_term + 0.1 * name_factor)
