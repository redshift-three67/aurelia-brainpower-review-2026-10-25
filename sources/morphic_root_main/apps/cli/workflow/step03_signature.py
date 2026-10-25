"""Step 03: Klienten-Signatur - 6-Schicht-Pipeline nach Radi144-Blueprint.

Schichten: Name(15%), Geburtsdaten(20%), Bild(25%), Organuhr(10%), Planetarisch(15%), EMF(5%)
Delegiert an AnalysisService.encode_profile() (Kernengine, unveraendert) und
fuegt aeussere Gewichtung/Radi144-Schichten als Modifikatoren hinzu.
"""

from __future__ import annotations

import hashlib
import math
from datetime import datetime

import numpy as np

from .state import WorkflowState

# TCM-Organuhr-Frequenzen (Stunde -> Hz)
_ORGAN_CLOCK = {
    1: 194.18,
    2: 194.18,  # Leber 1-3
    3: 220.0,
    4: 220.0,  # Lunge 3-5
    5: 246.94,
    6: 246.94,  # Dickdarm 5-7
    7: 261.63,
    8: 261.63,  # Magen 7-9
    9: 293.66,
    10: 293.66,  # Milz 9-11
    11: 329.63,
    12: 329.63,  # Herz 11-13
    13: 349.23,
    14: 349.23,  # Duenn darm 13-15
    15: 392.0,
    16: 392.0,  # Blase 15-17
    17: 440.0,
    18: 440.0,  # Niere 17-19
    19: 493.88,
    20: 493.88,  # Perikard 19-21
    21: 523.25,
    22: 523.25,  # 3E 21-23
    23: 587.33,
    0: 587.33,  # Gallenblase 23-1
}

# Schumann-Harmonische fuer EMF-Korrektur
_SCHUMANN_HARMONICS = [7.83, 14.3, 20.8, 27.3, 33.8]


def _text_to_frequency(text: str) -> float:
    """Numerologische + phonetische Frequenz aus Text (Radi144-Methode)."""
    if not text:
        return 0.0
    numerology = sum(ord(c) for c in text if c.isalpha())
    vowels = {"a": 440.0, "e": 330.0, "i": 550.0, "o": 220.0, "u": 165.0}
    consonant_freqs = [
        ord(c) * 2.0 for c in text.lower() if c.isalpha() and c not in vowels
    ]
    vowel_freqs = [vowels[c] for c in text.lower() if c in vowels]
    all_freqs = consonant_freqs + vowel_freqs
    phonetic = sum(all_freqs) / len(all_freqs) if all_freqs else 0.0
    combined = (numerology + phonetic) / 2.0
    return combined % 1000.0


def _birth_to_frequency(birth_date: str, birth_place: str) -> float:
    """Geburtsdaten -> Frequenz (Julian Day + Orts-Hash)."""
    try:
        if len(birth_date) >= 8:
            day = int(birth_date[:2])
            month = int(birth_date[2:4])
            year = int(birth_date[4:8])
        else:
            return 0.0
    except (ValueError, IndexError):
        return 0.0

    julian = (
        367 * year
        - 7 * (year + (month + 9) // 12) // 4
        + 275 * month // 9
        + day
        + 1721013
    )
    jd_freq = julian % 1000.0

    place_hash = int(hashlib.md5(birth_place.encode()).hexdigest()[:4], 16) / 65.535

    combined = 0.60 * jd_freq + 0.30 * place_hash + 0.10 * 50.0
    return combined % 1000.0


def _image_to_frequency(image_path: str) -> float:
    """Bild -> Frequenz via SHA-256."""
    if not image_path:
        return 0.0
    try:
        from pathlib import Path

        p = Path(image_path)
        if not p.exists():
            return 0.0
        raw = p.read_bytes()[:1024]
        return int(hashlib.sha256(raw).hexdigest()[:8], 16) % 1000.0
    except Exception:
        return 0.0


def _planet_frequency(birth_date: str) -> float:
    """Planetarische Frequenz aus Geburtsdatum."""
    try:
        if len(birth_date) >= 8:
            day = int(birth_date[:2])
            month = int(birth_date[2:4])
            year = int(birth_date[4:8])
        else:
            return 0.0
    except (ValueError, IndexError):
        return 0.0
    day_of_year = (datetime(year, month, day) - datetime(year, 1, 1)).days + 1
    return 100.0 * (1.0 + math.sin(day_of_year * 2.0 * math.pi / 365.25))


def step_03_signature(state: WorkflowState, verbose: bool = True) -> WorkflowState:
    """Step 3: 6-Schicht-Signatur-Pipeline."""
    if verbose:
        print("  [3/12] Klienten-Signatur (6-Schicht)...")

    components: dict[str, float] = {}
    weights: dict[str, float] = {}

    full_name = f"{state.first_name} {state.name}"

    # Schicht 1: Name (15%)
    name_freq = _text_to_frequency(full_name)
    components["name"] = name_freq
    weights["name"] = 0.15

    # Schicht 2: Geburtsdaten (20%)
    birth_freq = _birth_to_frequency(state.birth_date, state.birth_place)
    components["birth"] = birth_freq
    weights["birth"] = 0.20

    # Schicht 3: Bild (25%, optional)
    if state.image_path:
        img_freq = _image_to_frequency(state.image_path)
        components["image"] = img_freq
        weights["image"] = 0.25

    # Schicht 4: Organuhr (10%)
    now = datetime.now()
    organ_freq = _ORGAN_CLOCK.get(now.hour, 432.0)
    components["organ"] = organ_freq
    weights["organ"] = 0.10

    # Schicht 5: Planetarisch (15%, optional)
    if state.planet_type or state.birth_date:
        planet_freq = _planet_frequency(state.birth_date)
        components["planet"] = planet_freq
        weights["planet"] = 0.15

    # Schicht 6: EMF-Korrektur (5%, wird in Step 5 verfeinert)
    emf_index = 0.1  # Placeholder, wird in Step 5 aktualisiert
    schumann_idx = min(4, int(emf_index * 5))
    emf_freq = _SCHUMANN_HARMONICS[schumann_idx] * emf_index * 10.0
    components["emf"] = emf_freq
    weights["emf"] = 0.05

    # Gewichtete Kombination
    total_weight = sum(weights.values())
    if total_weight > 0:
        state.client_frequency = (
            sum(components[k] * weights[k] for k in components) / total_weight
        )
    else:
        state.client_frequency = 432.0

    state.signature_components = components

    # Kernengine: encode_profile (unveraendert)
    try:
        from core.profiles.profile import ClientProfile
        from services.analysis_service import AnalysisService

        image_sig = None
        if state.image_path:
            try:
                from PIL import Image as _PILImage

                img = _PILImage.open(state.image_path).convert("L").resize((32, 32))
                image_sig = np.array(img, dtype=float)
            except Exception:
                import hashlib as _h
                from pathlib import Path as _P

                raw = _P(state.image_path).read_bytes()[:1024]
                image_sig = np.frombuffer(
                    _h.sha256(raw).digest()[:32], dtype=np.uint8
                ).astype(float)

        personal_profile = {
            "emotion": state.p_emotion,
            "physisch": state.p_physisch,
            "mental": state.p_mental,
            "astral": state.p_astral,
        }

        profile_obj = ClientProfile(
            name=state.name,
            first_name=state.first_name,
            birth_date=state.birth_date,
            birth_place=state.birth_place,
            image_signature=image_sig,
            personal_profile=personal_profile,
            planet_type=state.planet_type or None,
        )

        analysis = AnalysisService(rate_database={}, h_level=state.h_level)
        state.client_rates = analysis.encode_profile(profile_obj)
        state.emf_corrected_frequency = state.client_frequency
        if verbose:
            print(f"        Frequenz: {state.client_frequency:.2f} Hz")
            print(f"        Raten: {len(state.client_rates)} Werte")
            print(f"        Schichten: {', '.join(components.keys())}")
    except Exception as exc:
        state.add_error(3, f"encode_profile: {exc}")
        if verbose:
            print(f"        [WARN] Signatur-Engine: {exc}")

    state.mark_step(3)
    return state
