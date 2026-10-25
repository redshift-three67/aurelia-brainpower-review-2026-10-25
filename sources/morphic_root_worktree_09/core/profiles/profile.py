from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

import numpy as np

SCHUMANN_F0 = 7.83


# =============================================================================
# BRUCE COPEN V4 RATEN-BERECHNUNG (Original-Algorithmus)
# =============================================================================

def calculate_copen_rate(
    word: str,
    potency: int = 0,
    potency_type: str = 'D',
    use_adaptive_fibonacci: bool = False,
    image_signature: str = "",
    use_image_signature: bool = False,
) -> Dict[str, Any]:
    """
    Bruce Copen V4 Ratenberechnung - EXAKT wie Original-TypeScript.
    
    Formel:
    1. Normalisierung: word → CLEANWORD (nur A-Z, 0-9)
    2. Primärsumme: S = Σ(W(ch) × position) wobei A-Z=1-26, 0-9=0-9
    3. Baserate: B = S × 1000
    4. Fibonacci-Rate: F = ⌊(B/21)×34⌋ oder adaptiv
    5. Potenz-Bonus: P = ⌊F×(k/Faktor)⌋
    6. Finale Rate: R = F + P
    
    Args:
        word: Das zu berechnende Wort/Begriff
        potency: Potenzwert (z.B. 30 für D30)
        potency_type: 'D', 'C', 'LM', 'M', 'F1', 'F2', 'F3'
        use_adaptive_fibonacci: Wortlängen-abhängige Fibonacci-Paare
        image_signature: Optionale Bildsignatur als Text
        use_image_signature: Ob Bildsignatur verwendet werden soll
    
    Returns:
        Dictionary mit allen Berechnungsdetails
    """
    
    # SCHRITT 1: Normalisierung (exakt wie Original)
    def normalize(w: str) -> str:
        result = w.upper()
        result = result.replace('Ä', 'AE').replace('Ö', 'OE').replace('Ü', 'UE').replace('ß', 'SS')
        # Potenzangaben entfernen (D30, C200, LM6, etc.)
        import re
        result = re.sub(r'\s*[DCLMF]+\d+', '', result)
        # Nur Buchstaben und Zahlen behalten
        result = ''.join(c for c in result if c.isalpha() or c.isdigit())
        return result.strip()
    
    # SCHRITT 2: Zeichenwert-Berechnung (A-Z=1-26, 0-9=0-9)
    def get_char_value(ch: str) -> int:
        if 'A' <= ch <= 'Z':
            return ord(ch) - 64  # A=1, B=2, ..., Z=26
        if '0' <= ch <= '9':
            return int(ch)  # 0=0, 1=1, ..., 9=9
        return 0
    
    # SCHRITT 3: Positionsgewichtete Primärsumme
    def compute_primary_sum(text: str) -> int:
        total = 0
        pos = 1
        for ch in text:
            value = get_char_value(ch)
            total += value * pos  # S = Σ(W(ch) × position)
            pos += 1
        return total
    
    clean_word = normalize(word)
    primary_sum = compute_primary_sum(clean_word)
    
    # SCHRITT 4: Bildsignatur (Optional)
    if use_image_signature and image_signature and image_signature.strip():
        clean_sig = normalize(image_signature)
        img_primary = compute_primary_sum(clean_sig)
        primary_sum = math.floor((primary_sum + img_primary) / 2)  # Arithmetisches Mittel
    
    # SCHRITT 5: Baserate
    base_rate = primary_sum * 1000
    
    # SCHRITT 6: Fibonacci-Modulation
    fibonacci_pair = None
    if use_adaptive_fibonacci:
        # ADAPTIV: Wortlängen-abhängig
        word_len = len(clean_word)
        if 1 <= word_len <= 4:
            div, mult = 13, 21  # ≈ 1.615
        elif 5 <= word_len <= 10:
            div, mult = 21, 34  # ≈ 1.619 (Standard)
        elif 11 <= word_len <= 20:
            div, mult = 34, 55  # ≈ 1.618
        else:
            div, mult = 55, 89  # >20 Zeichen
        fibonacci_pair = {'div': div, 'mult': mult}
    else:
        # ORIGINAL COPEN: Feste Ratio 21/34
        div, mult = 21, 34
    
    fibonacci_rate = math.floor((base_rate / div) * mult)
    
    # SCHRITT 7: Potenz-Bonus
    potency_bonus = 0
    p = max(0, potency)
    if p > 0:
        potency_factors = {
            'D': 10,   # D-Potenzen: /10
            'C': 5,    # C-Potenzen: /5
            'LM': 2,   # LM-Potenzen: /2
            'M': 1,    # M-Potenzen: /1
            'F1': 6,   # Fluxion 1: /6
            'F2': 4,   # Fluxion 2: /4
            'F3': 3,   # Fluxion 3: /3
        }
        factor = potency_factors.get(potency_type.upper(), 10)
        potency_bonus = math.floor(fibonacci_rate * (p / factor))
    
    # SCHRITT 8: Finale Rate
    final_rate = fibonacci_rate + potency_bonus
    
    return {
        'word': word,
        'clean_word': clean_word,
        'potency': potency,
        'potency_type': potency_type,
        'primary_sum': primary_sum,
        'base_rate': base_rate,
        'fibonacci_rate': fibonacci_rate,
        'fibonacci_pair': fibonacci_pair,
        'potency_bonus': potency_bonus,
        'final_rate': final_rate,
        'is_adaptive': use_adaptive_fibonacci,
    }


def word_to_copen_rate(word: str) -> float:
    """
    Schnelle Berechnung der Copen-Rate für ein Wort (ohne Potenz).
    
    Args:
        word: Das zu berechnende Wort
    
    Returns:
        Die finale Copen-Rate als Float
    """
    result = calculate_copen_rate(word, potency=0, potency_type='D')
    return float(result['final_rate'])


def focus_to_copen_rates(focus_string: str) -> Tuple[float, Dict[str, float]]:
    """
    Berechnet Copen-Raten für einen Fokus-String (komma-separiert).
    
    Args:
        focus_string: z.B. "Sehen, Hören, Fühlen"
    
    Returns:
        Tuple aus (Durchschnitts-Rate, Dict mit einzelnen Raten)
    """
    if not focus_string or not focus_string.strip():
        return 0.0, {}
    
    # Fokus-Begriffe trennen
    terms = [t.strip() for t in focus_string.replace(';', ',').split(',') if t.strip()]
    
    if not terms:
        return 0.0, {}
    
    rates = {}
    for term in terms:
        rate = word_to_copen_rate(term)
        rates[term] = rate
    
    avg_rate = sum(rates.values()) / len(rates) if rates else 0.0
    return avg_rate, rates

@dataclass
class ClientProfile:
    name: str
    first_name: str
    birth_date: str
    birth_place: str
    image_signature: Optional[np.ndarray] = None
    personal_profile: Optional[dict[str, float]] = None
    planet_type: str = ""


class RateEncoder:
    """Konvertiert Klientendaten in Radionik-Raten."""

    def name_to_rate(self, text: str) -> np.ndarray:
        """
        Konvertiert einen Namen in eine Rate-Array.
        KORRIGIERT: Verwendet jetzt Bruce Copen V4 Algorithmus.
        """
        result = calculate_copen_rate(text, potency=0, potency_type='D')
        primary_sum = result['primary_sum']
        
        # Für Kompatibilität: 3-stelliges Array aus Primärsumme
        total = primary_sum % 1000
        return np.array([total // 100, (total % 100) // 10, total % 10], dtype=float)
    
    def name_to_copen_rate(self, text: str) -> float:
        """
        Berechnet die vollständige Bruce Copen Rate für einen Namen.
        
        Returns:
            Die finale Copen-Rate
        """
        return word_to_copen_rate(text)
    
    def text_to_copen_rate_full(self, text: str, potency: int = 0, potency_type: str = 'D') -> Dict[str, Any]:
        """
        Vollständige Copen-Rate-Berechnung mit allen Details.
        
        Returns:
            Dictionary mit allen Berechnungsschritten
        """
        return calculate_copen_rate(text, potency, potency_type)

    def date_to_rate(self, date_str: str) -> float:
        digits = [int(c) for c in date_str if c.isdigit()]
        if not digits:
            return 0.0
        weighted = sum(val * (idx + 1) for idx, val in enumerate(digits))
        return float(weighted % 100)

    def place_to_rate(self, place: str) -> float:
        hashed = sum(ord(c) * (i + 1) for i, c in enumerate(place.lower()))
        return float(hashed % 100)

    def planet_to_rate(self, planet: str) -> float:
        text = (planet or "").strip()
        if not text:
            return 0.0
        hashed = sum(ord(c) * (i + 1) for i, c in enumerate(text.lower()))
        return float(hashed % 100)

    def image_to_rates(self, image: np.ndarray, top_k: int = 4) -> np.ndarray:
        spectrum = np.fft.fft(image.flatten())
        idx = np.argsort(np.abs(spectrum))[-top_k:]
        freq = np.maximum(idx, 1) * SCHUMANN_F0
        rates = (np.log10(freq / SCHUMANN_F0) * 100) % 100
        return rates.real.astype(float)

    @staticmethod
    def _clamp01(x: float) -> float:
        return float(max(0.0, min(1.0, x)))

    def personal_profile_to_vector(self, personal_profile: dict[str, float]) -> np.ndarray:
        keys = ("emotion", "physisch", "mental", "astral")
        values = []
        for key in keys:
            raw = float(personal_profile.get(key, 0.5))
            values.append(self._clamp01(raw))
        return np.asarray(values, dtype=float)
