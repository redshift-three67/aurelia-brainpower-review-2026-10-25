"""
Adaptive Gewichtung für Morphic Engine V1

Passt Scoring-Gewichte basierend auf Fokus-Kategorie an.
Verschiedene Fokus-Typen benötigen unterschiedliche Gewichtungen:
- Physische Fokus → höhere Frequenz-Harmonie-Gewichtung
- Emotionale Fokus → höhere Resonanz-Gewichtung
- Mentale Fokus → höhere Individual-Score-Gewichtung
"""

from typing import Dict, Tuple
from .focus_synonyms import get_canonical_focus


# Fokus-Kategorien und ihre zugehörigen kanonischen Begriffe
FOCUS_CATEGORIES: Dict[str, list] = {
    "physical": [
        "kopfschmerz", "rücken", "gelenk", "muskel", "knochen",
        "verdauung", "blähung", "verstopfung", "durchfall",
        "herz", "kreislauf", "blutdruck", "atmung", "husten", "asthma",
        "haut", "neurodermitis", "zahn", "kiefergelenk"
    ],
    "emotional": [
        "stress", "depression", "angst", "emotion", "trauma",
        "schlaf", "müdigkeit"
    ],
    "mental": [
        "nerven", "schwindel", "konzentration", "gedächtnis"
    ],
    "energetic": [
        "meridian", "chakra", "energie"
    ],
    "toxicological": [
        "entgiftung", "schwermetall", "strahlung", "allergie"
    ],
    "immune": [
        "immunsystem", "entzündung", "allergie"
    ],
    "hormonal": [
        "hormone", "schilddrüse", "stoffwechsel"
    ]
}

# Gewichtungs-Profile pro Kategorie
# Format: (individual_weight, resonance_weight, harmony_weight, relevance_weight)
CATEGORY_WEIGHTS: Dict[str, Tuple[float, float, float, float]] = {
    "physical":      (0.20, 0.25, 0.35, 0.20),  # Höhere Frequenz-Harmonie
    "emotional":     (0.15, 0.40, 0.20, 0.25),  # Höhere Resonanz
    "mental":        (0.35, 0.20, 0.20, 0.25),  # Höhere Individual-Scores
    "energetic":     (0.20, 0.35, 0.25, 0.20),  # Resonanz + Harmonie
    "toxicological": (0.30, 0.20, 0.20, 0.30),  # Individual + Relevanz
    "immune":        (0.25, 0.25, 0.25, 0.25),  # Ausgewogen
    "hormonal":      (0.25, 0.30, 0.20, 0.25),  # Leicht erhöhte Resonanz
    "default":       (0.25, 0.25, 0.25, 0.25),  # Standard ausgewogen
}


def get_focus_category(focus: str) -> str:
    """
    Bestimmt die Kategorie eines Fokus.
    
    Args:
        focus: Eingabe-Fokus
    
    Returns:
        Kategorie-Name oder "default"
    """
    if not focus:
        return "default"
    
    canonical = get_canonical_focus(focus).lower()
    
    for category, terms in FOCUS_CATEGORIES.items():
        if canonical in terms:
            return category
    
    # Teilstring-Suche
    focus_lower = focus.lower()
    for category, terms in FOCUS_CATEGORIES.items():
        for term in terms:
            if term in focus_lower or focus_lower in term:
                return category
    
    return "default"


def get_adaptive_weights(focus: str) -> Dict[str, float]:
    """
    Gibt adaptive Gewichtungen basierend auf Fokus zurück.
    
    Args:
        focus: Eingabe-Fokus
    
    Returns:
        Dict mit Gewichtungen für Synergy-Berechnung
    """
    category = get_focus_category(focus)
    weights = CATEGORY_WEIGHTS.get(category, CATEGORY_WEIGHTS["default"])
    
    return {
        "individual": weights[0],
        "resonance": weights[1],
        "harmony": weights[2],
        "relevance": weights[3],
        "category": category
    }


def explain_weights(focus: str) -> str:
    """
    Gibt eine Erklärung der gewählten Gewichtung zurück.
    
    Args:
        focus: Eingabe-Fokus
    
    Returns:
        Menschenlesbare Erklärung
    """
    weights = get_adaptive_weights(focus)
    category = weights["category"]
    
    explanations = {
        "physical": "Physischer Fokus: Frequenz-Harmonie priorisiert für körperliche Resonanz",
        "emotional": "Emotionaler Fokus: Resonanz-Amplifikation für energetische Wirkung",
        "mental": "Mentaler Fokus: Individual-Scores für kognitive Präzision",
        "energetic": "Energetischer Fokus: Resonanz + Harmonie für Meridian/Chakra-Arbeit",
        "toxicological": "Toxikologischer Fokus: Individual + Relevanz für Entgiftung",
        "immune": "Immunologischer Fokus: Ausgewogene Gewichtung",
        "hormonal": "Hormoneller Fokus: Resonanz erhöht für endokrines System",
        "default": "Standard: Ausgewogene Gewichtung aller Faktoren"
    }
    
    return explanations.get(category, explanations["default"])
