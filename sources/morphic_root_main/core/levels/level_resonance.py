from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import math


@dataclass(frozen=True)
class Level:
    id: int
    name: str
    german_name: str
    description: str
    freq_min: float
    freq_max: float | None  # None = unendlich
    keywords: List[str]


# 13-Ebenen-Modell nach Entwicklerdokumentation
LEVELS: List[Level] = [
    Level(
        id=1,
        name="Physical Realm - Particles",
        german_name="Physische Ebene - Partikel",
        description="Materielle Ebene: Atome, Partikel, Elemente",
        freq_min=1.0,
        freq_max=100_000.0,
        keywords=["atom", "partikel", "molekül", "element", "materie", "dna", "particles", "atoms", "matter", "struktur"],
    ),
    Level(
        id=2,
        name="Physical Realm - Structure",
        german_name="Physische Ebene - Struktur",
        description="Physische Struktur: Gewebe, Organe, Körper",
        freq_min=100_000.0,
        freq_max=500_000.0,
        keywords=["körper", "organ", "gewebe", "struktur", "fascia"],
    ),
    Level(
        id=3,
        name="Etheric Realm - Prana",
        german_name="Ätherische Ebene - Prana",
        description="Lebenskraft-Ebene: Qi, Prana, Atmung",
        freq_min=500_000.0,
        freq_max=1_000_000.0,
        keywords=["prana", "qi", "lebenskraft", "atmung", "breathing"],
    ),
    Level(
        id=4,
        name="Etheric Realm - Meridians",
        german_name="Ätherische Ebene - Meridiane",
        description="Energiekanäle: Meridiane, Chakren (physisch)",
        freq_min=1_000_000.0,
        freq_max=2_000_000.0,
        keywords=["meridian", "meridiane", "chakra", "energiekanal", "nadis", "akupunktur"],
    ),
    Level(
        id=5,
        name="Astral Realm - Emotions",
        german_name="Astrale Ebene - Emotionen",
        description="Emotionale Ebene: Gefühle, emotionale Komplexe",
        freq_min=2_000_000.0,
        freq_max=3_500_000.0,
        keywords=["emotion", "gefühl", "empfindung", "emotions", "feelings"],
    ),
    Level(
        id=6,
        name="Astral Realm - Thought-Forms",
        german_name="Astrale Ebene - Gedankenformen",
        description="Gedankenformen: magnetische Felder, Schwingungsmuster",
        freq_min=3_500_000.0,
        freq_max=5_000_000.0,
        keywords=["gedanke", "thought", "magnetisch", "schwingung", "pattern"],
    ),
    Level(
        id=7,
        name="Mental Realm - Time",
        german_name="Mentale Ebene - Zeit",
        description="Zeitliche Konstrukte: Raum, Form, Farbe",
        freq_min=5_000_000.0,
        freq_max=7_000_000.0,
        keywords=["zeit", "time", "raum", "space", "form", "farbe", "psychons"],
    ),
    Level(
        id=8,
        name="Mental Realm - Mental Constructs",
        german_name="Mentale Ebene - Mentale Konstrukte",
        description="Mentale Konstrukte: poetische Felder, Konzepte",
        freq_min=7_000_000.0,
        freq_max=9_000_000.0,
        keywords=["konzept", "idee", "mental", "konstrukt", "poetic fields"],
    ),
    Level(
        id=9,
        name="Causal Plane - Blueprints",
        german_name="Kausale Ebene - Blaupausen",
        description="Akasha-Chronik: Destiny Scripts, Blaupausen",
        freq_min=9_000_000.0,
        freq_max=11_000_000.0,
        keywords=["akasha", "blueprint", "blaupause", "destiny", "script"],
    ),
    Level(
        id=10,
        name="Causal Plane - Alchemy",
        german_name="Kausale Ebene - Alchemie",
        description="Intention: alchemische Transformation",
        freq_min=11_000_000.0,
        freq_max=13_000_000.0,
        keywords=["intention", "alchemie", "alchemy", "transformation"],
    ),
    Level(
        id=11,
        name="Atmic Plane - Identity",
        german_name="Atmische Ebene - Identität",
        description="Reine Essenz: unfragmentierte Identität",
        freq_min=13_000_000.0,
        freq_max=16_000_000.0,
        keywords=["identität", "essenz", "identity", "pure essence", "incarnation"],
    ),
    Level(
        id=12,
        name="Atmic Plane - Love & Unity",
        german_name="Atmische Ebene - Liebe & Einheit",
        description="Einheit: Liebe, archetypisches Denken",
        freq_min=16_000_000.0,
        freq_max=20_000_000.0,
        keywords=["liebe", "einheit", "love", "unity", "archetypal thinking", "transcending ego"],
    ),
    Level(
        id=13,
        name="Creator - Divinity",
        german_name="Schöpfer - Göttlichkeit",
        description="Göttliche Ebene: Ewigkeit, Wille zum Leben",
        freq_min=20_000_000.0,
        freq_max=None,
        keywords=["creator", "schöpfer", "göttlich", "divinity", "eternity", "prayers"],
    ),
]


_LEVEL_BY_ID: Dict[int, Level] = {lvl.id: lvl for lvl in LEVELS}


def convert_base_rate_to_copen_rate(base_rate: float, potency_factor: float = 0.0) -> float:
    """Konvertiert eine Base-Rate in eine Bruce-Copen-Rate.

    Umsetzung gemäß Dokumentation:

    fibonacciRate = floor((baseRate / 21) * 34)
    potencyBonus = floor(fibonacciRate * potencyFactor)
    copenRate = fibonacciRate + potencyBonus

    Hinweis: Die eigentliche Primärsumme (primarySum) wird vorher bereits in
    eine Base-Rate überführt (z.B. primarySum * 1000). Diese Funktion
    arbeitet nur auf der Base-Rate.
    """

    if base_rate <= 0.0:
        return 0.0

    fibonacci_rate = math.floor((base_rate / 21.0) * 34.0)
    potency_bonus = math.floor(fibonacci_rate * potency_factor) if potency_factor > 0.0 else 0
    return float(fibonacci_rate + potency_bonus)


def calculate_level_resonance(copen_rate: float, word: str) -> Dict[str, float]:
    """Berechnet Resonanzwerte (0–100%) für alle 13 Ebenen.

    Kombination aus frequenzbasierter Resonanz und Keyword-Matches
    gemäß Entwicklerdokumentation.
    """

    resonance: Dict[str, float] = {}
    if copen_rate <= 0.0:
        # Keine sinnvolle Zuordnung möglich
        for lvl in LEVELS:
            resonance[f"level_{lvl.id}"] = 0.0
        return resonance

    normalized_word = (word or "").strip().lower()

    for lvl in LEVELS:
        base_res = 0.0
        min_f = lvl.freq_min
        max_f = lvl.freq_max

        # Sonderfall Level 13 (max = unendlich)
        if max_f is None:
            if copen_rate >= min_f:
                base_res = 100.0
            else:
                ratio = copen_rate / min_f
                base_res = max(0.0, ratio * 50.0)
        else:
            # Innerhalb des Bereichs
            if min_f <= copen_rate <= max_f:
                midpoint = (min_f + max_f) / 2.0
                distance = abs(copen_rate - midpoint)
                rng = (max_f - min_f) / 2.0
                if rng > 0.0:
                    base_res = max(0.0, 100.0 - (distance / rng) * 50.0)
                else:
                    base_res = 0.0
            # Unterhalb des Bereichs
            elif copen_rate < min_f:
                ratio = copen_rate / min_f
                base_res = max(0.0, ratio * 40.0)
            # Oberhalb des Bereichs
            else:  # copen_rate > max_f
                overshoot = (copen_rate - max_f) / max_f
                base_res = max(0.0, 30.0 - overshoot * 30.0)

        # Keyword-basierte Resonanz
        keyword_bonus = 0.0
        if normalized_word:
            for kw in lvl.keywords:
                if kw and kw.lower() in normalized_word:
                    keyword_bonus += 25.0

        total_res = min(100.0, base_res + keyword_bonus)
        resonance[f"level_{lvl.id}"] = float(f"{total_res:.2f}")

    return resonance


def find_highest_resonance_level(resonance_values: Dict[str, float]) -> Tuple[int, float]:
    """Bestimmt die Ebene mit der höchsten Resonanz.

    Erwartet ein Dict wie {"level_1": 12.34, ..., "level_13": 100.0}.
    """

    highest_level = 1
    highest_value = 0.0

    for key, val in resonance_values.items():
        try:
            value = float(val or 0.0)
        except Exception:
            continue
        if value > highest_value:
            if key.startswith("level_"):
                try:
                    lvl_id = int(key.split("_", 1)[1])
                except Exception:
                    continue
                highest_level = lvl_id
                highest_value = value

    return highest_level, highest_value


def level_label(lvl_id: int) -> str:
    """Gibt eine kompakte deutschsprachige Bezeichnung für eine Ebene zurück."""

    lvl = _LEVEL_BY_ID.get(lvl_id)
    if not lvl:
        return "-"
    return f"{lvl.german_name} (Level {lvl.id})"
