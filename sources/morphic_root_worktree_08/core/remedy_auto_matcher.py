"""
Remedy Auto-Matcher für Morphic Engine V1

Automatische Zuordnung von Remedy-Gruppen zu Profilen basierend auf:
- Profilname/Thema
- Gruppenkategorien
- Namenskonventionen (*_remedies_multiplex)
"""

from typing import List, Dict, Set, Optional
import re

# Kategorien-Mapping: Welche Remedy-Gruppen passen zu welchen Themen
CATEGORY_REMEDY_MAPPING: Dict[str, List[str]] = {
    # Neurologisch/Gehirn
    "neural": [
        "nerven_remedies_multiplex",
        "psyche_remedies_multiplex",
        "homoeopathie_klassisch",
        "bachblueten_multiplex",
        "spagyrik_multiplex",
    ],
    # Energie/Müdigkeit
    "energy": [
        "energie_remedies_multiplex",
        "orthomolekular_therapie_multiplex",
        "vitamine_detailliert_fein",
        "mineralien_spurenelemente_detailliert_fein",
    ],
    # Verdauung
    "digestive": [
        "verdauung_remedies_multiplex",
        "probiotika_multiplex",
        "enzyme_multiplex",
        "homoeopathie_komplexmittel",
    ],
    # Immunsystem
    "immune": [
        "immun_remedies_multiplex",
        "homoeopathie_nosoden",
        "homoeopathie_isopathie",
        "frequenz_clark_multiplex",
    ],
    # Bewegungsapparat
    "musculoskeletal": [
        "bewegung_remedies_multiplex",
        "mineralstoffe_multiplex",
        "homoeopathie_klassisch",
        "schmerz_remedies_multiplex",
    ],
    # Herz-Kreislauf
    "cardiovascular": [
        "herz_remedies_multiplex",
        "kreislauf_remedies_multiplex",
        "fettsaeuren_detailliert_fein",
    ],
    # Detox/Entgiftung
    "detox": [
        "detox_remedies_multiplex",
        "leber_remedies_multiplex",
        "niere_remedies_multiplex",
        "zeolith_multiplex",
        "chlorella_multiplex",
    ],
    # Haut & Narben
    "skin": [
        "haut_remedies_multiplex",
        "homoeopathie_klassisch",
        "spagyrik_multiplex",
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
    ],
    # Narben (NEU)
    "scar": [
        "heel_remedies_multiplex",
        "nutramedix_remedies_multiplex",
        "haut_remedies_multiplex",
        "homoeopathie_klassisch",
    ],
    # Hormone
    "hormonal": [
        "hormon_remedies_multiplex",
        "endokrin_remedies_multiplex",
        "adaptogene_multiplex",
    ],
    # Psyche/Emotion
    "psyche": [
        "psyche_remedies_multiplex",
        "bachblueten_multiplex",
        "homoeopathie_klassisch",
        "aromatherapie_multiplex",
    ],
}

# Profilname → Kategorien Mapping
PROFILE_CATEGORY_MAPPING: Dict[str, List[str]] = {
    "gehirn": ["neural", "psyche", "energy"],
    "nervensystem": ["neural", "energy"],
    "verdauung": ["digestive", "immune", "detox"],
    "darm": ["digestive", "immune"],
    "leber": ["digestive", "detox"],
    "herz": ["cardiovascular", "energy"],
    "kreislauf": ["cardiovascular"],
    "bewegung": ["musculoskeletal"],
    "gelenk": ["musculoskeletal"],
    "wirbel": ["musculoskeletal", "neural"],
    "immun": ["immune", "detox"],
    "allergie": ["immune", "digestive"],
    "haut": ["skin", "immune", "detox"],
    "narben": ["scar", "skin", "detox"],
    "narbe": ["scar", "skin", "detox"],
    "keloid": ["scar", "skin"],
    "entstoerung": ["scar", "detox"],
    "hormon": ["hormonal", "energy"],
    "endokrin": ["hormonal"],
    "schilddrüse": ["hormonal", "energy"],
    "nebenniere": ["hormonal", "energy"],
    "stress": ["psyche", "hormonal", "neural"],
    "schlaf": ["neural", "psyche", "hormonal"],
    "angst": ["psyche", "neural"],
    "depression": ["psyche", "neural", "energy"],
    "schmerz": ["neural", "musculoskeletal"],
    "entzündung": ["immune", "detox"],
    "toxin": ["detox"],
    "pathogen": ["immune"],
    "bakterien": ["immune"],
    "viren": ["immune"],
    "parasiten": ["immune", "detox"],
    "pilze": ["immune"],
}


def detect_categories(profile_name: str, groups: List[str]) -> Set[str]:
    """
    Erkennt Kategorien basierend auf Profilname und enthaltenen Gruppen.
    
    Args:
        profile_name: Name des Profils
        groups: Liste der Gruppen im Profil
    
    Returns:
        Set von erkannten Kategorien
    """
    categories = set()
    profile_lower = profile_name.lower()
    
    # Aus Profilname
    for keyword, cats in PROFILE_CATEGORY_MAPPING.items():
        if keyword in profile_lower:
            categories.update(cats)
    
    # Aus Gruppennamen
    all_groups_str = " ".join(groups).lower()
    for keyword, cats in PROFILE_CATEGORY_MAPPING.items():
        if keyword in all_groups_str:
            categories.update(cats)
    
    # Default wenn nichts erkannt
    if not categories:
        categories.add("neural")  # Fallback
    
    return categories


def get_matching_remedies(
    profile_name: str,
    existing_groups: List[str],
    available_remedy_groups: Optional[List[str]] = None
) -> List[str]:
    """
    Gibt passende Remedy-Gruppen für ein Profil zurück.
    
    Args:
        profile_name: Name des Profils
        existing_groups: Bereits im Profil enthaltene Gruppen
        available_remedy_groups: Optional: Liste verfügbarer Remedy-Gruppen
    
    Returns:
        Liste empfohlener Remedy-Gruppen (ohne Duplikate)
    """
    categories = detect_categories(profile_name, existing_groups)
    
    # Sammle Remedies aus allen erkannten Kategorien
    remedies = set()
    for cat in categories:
        cat_remedies = CATEGORY_REMEDY_MAPPING.get(cat, [])
        remedies.update(cat_remedies)
    
    # Entferne bereits vorhandene
    existing_set = set(g.lower() for g in existing_groups)
    remedies = {r for r in remedies if r.lower() not in existing_set}
    
    # Filter auf verfügbare Gruppen wenn angegeben
    if available_remedy_groups:
        available_set = set(g.lower() for g in available_remedy_groups)
        remedies = {r for r in remedies if r.lower() in available_set}
    
    return sorted(remedies)


def suggest_remedies_for_new_profile(
    profile_name: str,
    base_groups: List[str]
) -> Dict:
    """
    Schlägt Remedies für ein neues Profil vor.
    
    Args:
        profile_name: Name des neuen Profils
        base_groups: Basis-Gruppen des Profils
    
    Returns:
        Dict mit Empfehlungen und Begründungen
    """
    categories = detect_categories(profile_name, base_groups)
    remedies = get_matching_remedies(profile_name, base_groups)
    
    return {
        "profile": profile_name,
        "detected_categories": sorted(categories),
        "suggested_remedies": remedies,
        "reasoning": f"Basierend auf {len(categories)} erkannten Kategorien: {', '.join(sorted(categories))}",
        "complete_groups": base_groups + remedies,
        "total_groups": len(base_groups) + len(remedies)
    }


def auto_extend_profile_with_remedies(groups: List[str], profile_name: str = "") -> List[str]:
    """
    Erweitert eine Gruppenliste automatisch um passende Remedies.
    
    Args:
        groups: Ursprüngliche Gruppenliste
        profile_name: Optionaler Profilname für bessere Erkennung
    
    Returns:
        Erweiterte Gruppenliste mit Remedies
    """
    remedies = get_matching_remedies(profile_name, groups)
    return groups + remedies


def list_all_remedy_categories() -> Dict[str, List[str]]:
    """Gibt alle definierten Remedy-Kategorien zurück."""
    return CATEGORY_REMEDY_MAPPING.copy()


def format_suggestion_display(suggestion: Dict) -> str:
    """Formatiert Remedy-Vorschlag für Konsolenausgabe."""
    lines = [
        f"🔬 Remedy-Vorschlag für: {suggestion['profile']}",
        "-" * 50,
        f"Erkannte Kategorien: {', '.join(suggestion['detected_categories'])}",
        "",
        "Empfohlene Remedy-Gruppen:",
    ]
    
    for r in suggestion['suggested_remedies']:
        lines.append(f"  + {r}")
    
    if not suggestion['suggested_remedies']:
        lines.append("  (keine neuen Empfehlungen)")
    
    lines.extend([
        "",
        f"Gesamt: {suggestion['total_groups']} Gruppen",
        f"Begründung: {suggestion['reasoning']}"
    ])
    
    return "\n".join(lines)
