from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, List

import numpy as np

from core.profiles.profile import ClientProfile
from core.resonance.resonator import MorphicFieldResonator
from core.harmonization.engine import HarmonizationEngine


class HarmonizationService:
    """Spiegelt das Verhalten von ResonancePipeline.harmonize.

    Erzeugt Harmonisierung aus Baseline-Analyse oder expliziten Zielraten.
    """

    def __init__(self, rate_database: Dict[str, Iterable[float]], h_level: float = 0.0) -> None:
        self.rate_db = rate_database
        self.resonator = MorphicFieldResonator(rate_database, h_level=h_level)
        self.harmonizer = HarmonizationEngine(self.resonator)

    def harmonize(
        self,
        profile: ClientProfile,
        analysis: Dict[str, Any],
        targets: Optional[List[np.ndarray]] = None,
    ) -> Dict[str, Any]:
        """Erzeuge Harmonisierung aus Baseline oder expliziten Zielraten.

        Die Logik entspricht der ursprünglichen ResonancePipeline.harmonize.
        """
        imbalanced: List[np.ndarray]
        if targets is None:
            resonance_map: Dict[str, float] = analysis["resonance_map"]
            imbalanced = [
                np.array(self.resonator.rate_db[system], dtype=float)
                for system, score in resonance_map.items()
                if score < 0.6
            ]
        else:
            imbalanced = [np.array(r, dtype=float) for r in targets if r is not None and len(r) > 0]

        if not imbalanced:
            return {"status": "balanced", "treatment_rates": []}

        inv_list = [self.harmonizer.inverse_rates(r) for r in imbalanced]
        max_len = max(len(v) for v in inv_list)
        padded = [np.resize(v, max_len) if len(v) < max_len else v for v in inv_list]
        base_matrix = np.vstack(padded)
        adaptive = self.harmonizer.adaptive_loop(profile, base_matrix.mean(axis=0))
        optimized = self.harmonizer.holographic_optimize(base_matrix)

        return {
            "status": "harmonizing",
            "base_inverse": base_matrix,
            "adaptive_rates": adaptive,
            "optimized_rates": optimized,
        }
