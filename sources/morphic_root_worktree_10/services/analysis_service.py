from __future__ import annotations

from typing import Any, Dict, Iterable

import numpy as np

from core.profiles.profile import ClientProfile, RateEncoder
from core.resonance.resonator import MorphicFieldResonator
from core.harmonization.engine import HarmonizationEngine


class AnalysisService:
    """Kapselt die Basis-Analysepipeline (Profil → Raten → Kernmetriken).

    Diese Klasse entspricht funktional dem Kern von ResonancePipeline.analyze,
    ist aber vom CLI und sonstiger I/O entkoppelt.
    """

    def __init__(self, rate_database: Dict[str, Iterable[float]], h_level: float = 0.0) -> None:
        self.rate_db = rate_database
        self.encoder = RateEncoder()
        self.resonator = MorphicFieldResonator(rate_database, h_level=h_level)
        self.harmonizer = HarmonizationEngine(self.resonator)

    # --- Profil → Raten -------------------------------------------------

    def encode_profile(self, profile: ClientProfile) -> np.ndarray:
        """Erzeugt den kombinierten Ratenvektor aus Name, Datum, Ort, Bild."""
        image = profile.image_signature
        if image is None:
            image = np.ones((32, 32), dtype=float)

        name_rate = self.encoder.name_to_rate(profile.name + profile.first_name)
        date_rate = np.array([self.encoder.date_to_rate(profile.birth_date)])
        place_rate = np.array([self.encoder.place_to_rate(profile.birth_place)])
        image_rates = self.encoder.image_to_rates(image)

        planet_text = getattr(profile, "planet_type", "")
        planet_rate = np.array([self.encoder.planet_to_rate(planet_text)])

        all_rates = np.concatenate([name_rate, date_rate, place_rate, image_rates, planet_rate])
        return all_rates

    # --- Analyse --------------------------------------------------------

    def analyze(self, profile: ClientProfile) -> Dict[str, Any]:
        """Führt die Kernanalyse aus und liefert Basiskennzahlen.

        Rückgabe:
          - rates: kombinierter Ratenvektor
          - morphic_field
          - holographic_entropy
          - heim_signature
          - resonance_map: Scores pro System im rate_database
        """
        rates = self.encode_profile(profile)
        m_field = self.resonator.calculate_m_field(rates)
        entropy = self.resonator.holographic_entropy(rates)
        heim_sig = self.resonator.heim_signature(rates)

        resonance_map = {
            system: self.resonator.resonance_score(rates, np.array(sys_rates, dtype=float))
            for system, sys_rates in self.rate_db.items()
        }

        return {
            "rates": rates,
            "morphic_field": m_field,
            "holographic_entropy": entropy,
            "heim_signature": heim_sig,
            "resonance_map": resonance_map,
        }
