from __future__ import annotations

from typing import Dict, Iterable

import numpy as np


SCHUMANN_F0 = 7.83
G_NEWTON_SIM = 1.0


class MorphicFieldResonator:
    def __init__(self, rate_db: Dict[str, Iterable[float]], h_level: float = 0.0) -> None:
        self.rate_db = rate_db
        self.h_level = float(max(0.0, min(1.0, h_level)))

    def calculate_m_field(self, rates: np.ndarray) -> float:
        alpha = 0.08 * (1 + 0.2 * self.h_level)
        beta = 0.04 * (1 - 0.1 * self.h_level)
        positions = np.arange(len(rates))
        psi = np.sin(rates * 2 * np.pi / 100)
        return float(np.sum(alpha * psi * np.exp(-beta * positions)))

    def resonance_score(self, client_rates: np.ndarray, target_rates: np.ndarray) -> float:
        omega_c = np.mean(client_rates) * 2 * np.pi / 100
        omega_t = np.mean(target_rates) * 2 * np.pi / 100
        base_gamma, mass = 0.12, 1.0
        gamma = max(1e-4, base_gamma * (1 - 0.3 * self.h_level))
        if omega_t == 0:
            return 0.0
        q_factor = omega_t * mass / gamma
        detuning = (omega_c - omega_t) / omega_t
        return float(q_factor / (1 + q_factor**2 * detuning**2))

    def resonance_score_batch(self, client_rates: np.ndarray, target_rates: np.ndarray) -> np.ndarray:
        """Vectorisierte Variante für viele target-Sets zugleich.

        target_rates: shape (K, M) – M gleich client_rates.size
        """
        if target_rates.ndim == 1:
            target_rates = target_rates.reshape(1, -1)
        omega_c = np.mean(client_rates) * 2 * np.pi / 100
        omega_t = np.mean(target_rates, axis=1) * 2 * np.pi / 100
        gamma = max(1e-4, 0.12 * (1 - 0.3 * self.h_level))
        q_factor = omega_t / gamma
        detuning = (omega_c - omega_t) / omega_t
        scores = q_factor / (1 + (q_factor**2) * (detuning**2))
        return scores.astype(float)

    def holographic_entropy(self, rates: np.ndarray) -> float:
        variance = np.var(rates)
        return float(np.log1p(variance) / (4 * G_NEWTON_SIM))

    def heim_signature(self, rates: np.ndarray) -> np.ndarray:
        segments = np.array_split(rates, 4)
        return np.array([np.mean(seg) if len(seg) > 0 else 0.0 for seg in segments], dtype=float)
