"""
Fokus-Synonym-Mapping für Morphic Engine V1

Ermöglicht flexiblere Fokus-Eingaben durch Zusammenführung
semantisch ähnlicher Begriffe.

Beispiel: "Migräne", "Kopfschmerz", "Headache" → gleiche Relevanz-Berechnung
"""

from typing import Dict, List, Set, Optional


# Synonym-Gruppen: Hauptbegriff → Liste von Synonymen
FOCUS_SYNONYMS: Dict[str, List[str]] = {
    # Kopf & Schmerz
    "kopfschmerz": ["migräne", "headache", "cephalgie", "kopfweh", "spannungskopfschmerz"],
    "schwindel": ["vertigo", "benommenheit", "dizziness", "gleichgewicht", "taumel"],
    
    # Energie & Müdigkeit
    "müdigkeit": ["erschöpfung", "fatigue", "energie", "kraftlos", "burnout", "chronische müdigkeit"],
    "schlaf": ["insomnie", "schlafstörung", "schlaflos", "einschlafen", "durchschlafen"],
    
    # Verdauung
    "verdauung": ["magen", "darm", "digestion", "bauch", "gastro", "intestinal"],
    "blähung": ["flatulenz", "meteorismus", "völlegefühl", "aufgebläht"],
    "verstopfung": ["obstipation", "constipation", "stuhlgang"],
    "durchfall": ["diarrhoe", "diarrhea", "dünnpfiff"],
    
    # Herz-Kreislauf
    "herz": ["kardio", "cardiac", "herzrhythmus", "palpitation", "herzrasen"],
    "kreislauf": ["blutdruck", "durchblutung", "circulation", "gefäße"],
    "blutdruck": ["hypertonie", "hypotonie", "blood pressure"],
    
    # Atmung
    "atmung": ["lunge", "respiration", "breathing", "atemweg", "bronchien"],
    "husten": ["bronchitis", "cough", "tussis"],
    "asthma": ["atemnot", "dyspnoe", "kurzatmigkeit"],
    
    # Immunsystem
    "immunsystem": ["abwehr", "immune", "infekt", "erkältung", "grippe"],
    "allergie": ["heuschnupfen", "rhinitis", "histamin", "unverträglichkeit"],
    "entzündung": ["inflammation", "schwellung", "rötung"],
    
    # Bewegungsapparat
    "rücken": ["wirbelsäule", "bandscheibe", "lumbal", "back", "spine"],
    "gelenk": ["arthrose", "arthritis", "rheuma", "joint"],
    "muskel": ["verspannung", "myalgie", "muskelschmerz", "muscle"],
    "knochen": ["skelett", "osteo", "bone"],
    
    # Nervensystem
    "nerven": ["neuralgie", "neuropathie", "nervenschmerz", "neural"],
    "stress": ["anspannung", "anxiety", "angst", "nervosität"],
    "depression": ["traurigkeit", "melancholie", "antriebslos", "niedergeschlagen"],
    
    # Haut
    "haut": ["derma", "skin", "ekzem", "dermatitis", "ausschlag"],
    "neurodermitis": ["atopisch", "juckreiz", "pruritus"],
    
    # Hormone
    "hormone": ["endokrin", "drüsen", "schilddrüse", "nebenniere"],
    "schilddrüse": ["thyroid", "hashimoto", "t3", "t4"],
    "stoffwechsel": ["metabolismus", "metabolism"],
    
    # Zähne
    "zahn": ["dental", "zähne", "kiefer", "zahnfleisch", "gingiva"],
    "kiefergelenk": ["tmj", "cmd", "kieferschmerz"],
    
    # Toxine
    "entgiftung": ["detox", "ausleitung", "reinigung"],
    "schwermetall": ["amalgam", "quecksilber", "blei", "cadmium", "heavy metal"],
    "strahlung": ["emf", "elektrosmog", "5g", "wlan", "radiation"],
    
    # TCM/Energetisch
    "meridian": ["akupunktur", "tcm", "energiebahn", "chi", "qi"],
    "chakra": ["energiezentrum", "kundalini"],
    
    # Psyche
    "emotion": ["gefühl", "psyche", "seele", "mental"],
    "angst": ["panik", "phobie", "furcht", "anxiety"],
    "trauma": ["ptsd", "schock", "belastung"],
}

# Invertierter Index für schnelle Suche
_SYNONYM_INDEX: Dict[str, str] = {}


def _build_index():
    """Baut den invertierten Index auf."""
    global _SYNONYM_INDEX
    _SYNONYM_INDEX.clear()
    for main_term, synonyms in FOCUS_SYNONYMS.items():
        _SYNONYM_INDEX[main_term.lower()] = main_term
        for syn in synonyms:
            _SYNONYM_INDEX[syn.lower()] = main_term


def get_canonical_focus(focus: str) -> str:
    """
    Gibt den kanonischen Hauptbegriff für einen Fokus zurück.
    
    Args:
        focus: Eingabe-Fokus (z.B. "Migräne")
    
    Returns:
        Kanonischer Begriff (z.B. "kopfschmerz") oder Original wenn nicht gefunden
    """
    if not _SYNONYM_INDEX:
        _build_index()
    
    focus_lower = focus.lower().strip()
    
    # Direkte Übereinstimmung
    if focus_lower in _SYNONYM_INDEX:
        return _SYNONYM_INDEX[focus_lower]
    
    # Teilstring-Suche
    for term, canonical in _SYNONYM_INDEX.items():
        if term in focus_lower or focus_lower in term:
            return canonical
    
    return focus  # Original zurückgeben


def get_all_synonyms(focus: str) -> Set[str]:
    """
    Gibt alle Synonyme für einen Fokus zurück (inkl. Hauptbegriff).
    
    Args:
        focus: Eingabe-Fokus
    
    Returns:
        Set aller verwandten Begriffe
    """
    canonical = get_canonical_focus(focus)
    
    if canonical in FOCUS_SYNONYMS:
        result = {canonical}
        result.update(FOCUS_SYNONYMS[canonical])
        return result
    
    return {focus}


def expand_focus_keywords(focus: str) -> List[str]:
    """
    Erweitert einen Fokus um alle Synonyme für bessere Suche.
    
    Args:
        focus: Eingabe-Fokus
    
    Returns:
        Liste aller relevanten Suchbegriffe
    """
    synonyms = get_all_synonyms(focus)
    
    # Auch Teilwörter aus dem Original-Fokus hinzufügen
    words = focus.lower().split()
    for word in words:
        if len(word) > 3:  # Nur Wörter > 3 Zeichen
            synonyms.add(word)
    
    return list(synonyms)


# Index beim Import aufbauen
_build_index()
