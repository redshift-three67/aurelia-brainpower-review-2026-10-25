"""
Multi-Fokus Support für Morphic Engine V1

Ermöglicht kombinierte Fokus-Angaben wie:
- "Migräne + Stress"
- "Verdauung, Müdigkeit"
- "Rücken und Schlaf"

Kombiniert Synonyme und Gewichtungen aus mehreren Fokus-Bereichen.
"""

import re
from typing import List, Dict, Set, Tuple
from .focus_synonyms import expand_focus_keywords, get_canonical_focus
from .adaptive_weights import get_focus_category, CATEGORY_WEIGHTS


# Trennzeichen für Multi-Fokus
FOCUS_SEPARATORS = re.compile(r'[,;+&]|\s+und\s+|\s+and\s+|\s+mit\s+|\s+with\s+')


def parse_multi_focus(focus_input: str) -> List[str]:
    """
    Parst einen Multi-Fokus-String in einzelne Fokus-Begriffe.
    
    Args:
        focus_input: Eingabe wie "Migräne + Stress" oder "Verdauung, Müdigkeit"
    
    Returns:
        Liste der einzelnen Fokus-Begriffe
    """
    if not focus_input:
        return []
    
    # Aufteilen an Trennzeichen
    parts = FOCUS_SEPARATORS.split(focus_input)
    
    # Bereinigen und filtern
    focuses = []
    for part in parts:
        cleaned = part.strip()
        if cleaned and len(cleaned) > 2:  # Mindestens 3 Zeichen
            focuses.append(cleaned)
    
    return focuses


def expand_multi_focus_keywords(focus_input: str) -> List[str]:
    """
    Erweitert Multi-Fokus um alle zugehörigen Synonyme.
    
    Args:
        focus_input: Multi-Fokus-String
    
    Returns:
        Kombinierte Liste aller relevanten Keywords
    """
    focuses = parse_multi_focus(focus_input)
    
    all_keywords: Set[str] = set()
    for focus in focuses:
        keywords = expand_focus_keywords(focus)
        all_keywords.update(keywords)
    
    return list(all_keywords)


def get_multi_focus_weights(focus_input: str) -> Dict[str, float]:
    """
    Kombiniert Gewichtungen aus mehreren Fokus-Kategorien.
    
    Args:
        focus_input: Multi-Fokus-String
    
    Returns:
        Gemittelte Gewichtungen
    """
    focuses = parse_multi_focus(focus_input)
    
    if not focuses:
        return {
            "individual": 0.25,
            "resonance": 0.25,
            "harmony": 0.25,
            "relevance": 0.25,
            "categories": ["default"]
        }
    
    # Sammle alle Kategorien
    categories = []
    for focus in focuses:
        category = get_focus_category(focus)
        if category not in categories:
            categories.append(category)
    
    # Mittele die Gewichtungen
    total_weights = [0.0, 0.0, 0.0, 0.0]
    for category in categories:
        weights = CATEGORY_WEIGHTS.get(category, CATEGORY_WEIGHTS["default"])
        for i in range(4):
            total_weights[i] += weights[i]
    
    n = len(categories)
    return {
        "individual": total_weights[0] / n,
        "resonance": total_weights[1] / n,
        "harmony": total_weights[2] / n,
        "relevance": total_weights[3] / n,
        "categories": categories
    }


def get_multi_focus_canonical(focus_input: str) -> List[str]:
    """
    Gibt die kanonischen Begriffe für alle Fokus-Teile zurück.
    
    Args:
        focus_input: Multi-Fokus-String
    
    Returns:
        Liste der kanonischen Begriffe
    """
    focuses = parse_multi_focus(focus_input)
    return [get_canonical_focus(f) for f in focuses]


def format_multi_focus_display(focus_input: str) -> str:
    """
    Formatiert Multi-Fokus für Anzeige.
    
    Args:
        focus_input: Multi-Fokus-String
    
    Returns:
        Formatierte Anzeige mit Kategorien
    """
    focuses = parse_multi_focus(focus_input)
    
    if not focuses:
        return "Kein Fokus"
    
    parts = []
    for focus in focuses:
        canonical = get_canonical_focus(focus)
        category = get_focus_category(focus)
        parts.append(f"{focus} [{category}]")
    
    return " + ".join(parts)
