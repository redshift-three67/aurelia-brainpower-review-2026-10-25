from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Any

import numpy as np

from core.nls import nls_db


class NlsService:
    """Service-Schicht für NLS-Datenbanken und Scoring.

    Aktuell bildet diese Klasse 1:1 das Verhalten von nls_db.compute_nls_scores ab
    und dient als Einstiegspunkt für zukünftige "v2"-Modelle.
    """

    def __init__(self, items: List[Dict[str, Any]]) -> None:
        self._items = items

    @staticmethod
    def load_db(path: str | Path) -> List[Dict[str, Any]]:
        return nls_db.load_nls_db(str(path))

    def compute_scores(
        self,
        client_rates: np.ndarray,
        client_entropy: float,
        resonance_fn: Callable[[np.ndarray, np.ndarray], float],
    ) -> List[Dict[str, Any]]:
        return nls_db.compute_nls_scores(self._items, client_rates, client_entropy, resonance_fn)

    def compute_scores_v2(
        self,
        client_rates: np.ndarray,
        client_entropy: float,
        resonance_fn: Callable[[np.ndarray, np.ndarray], float],
        client_personal_vector: np.ndarray | None = None,
    ) -> List[Dict[str, Any]]:
        """NLS-Scoring mit Reliability- und optionalem Personal-Faktor (v2-Modell)."""
        return nls_db.compute_nls_scores_v2(
            self._items,
            client_rates,
            client_entropy,
            resonance_fn,
            client_personal_vector=client_personal_vector,
        )
