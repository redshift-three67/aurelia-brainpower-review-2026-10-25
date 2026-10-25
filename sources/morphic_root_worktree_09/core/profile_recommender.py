"""
Auto-Profil-Empfehlung für Morphic Engine V1

Schlägt basierend auf Fokus-Eingabe automatisch passende Profile vor.
Nutzt Fokus-Synonyme und Profil-Gruppen für intelligentes Matching.
"""

from typing import List, Dict, Tuple, Optional
from .focus_synonyms import get_canonical_focus, expand_focus_keywords, FOCUS_SYNONYMS


# Profil-Fokus-Mapping: Welche Fokus-Begriffe passen zu welchen Profilen
PROFILE_FOCUS_MAP: Dict[str, List[str]] = {
    # Basis-Profile
    "gehirn_detailliert": [
        "kopfschmerz", "schwindel", "nerven", "konzentration", "gedächtnis",
        "migräne", "gehirn", "neurologie", "tinnitus"
    ],
    "lymphsystem_detailliert": [
        "immunsystem", "lymphe", "ödem", "schwellung", "entgiftung",
        "infekt", "erkältung"
    ],
    "immunsystem_detailliert": [
        "immunsystem", "allergie", "entzündung", "infekt", "autoimmun",
        "grippe", "erkältung", "abwehr"
    ],
    
    # Neue Phase-4 Profile
    "zaehne_kiefer_detailliert": [
        "zahn", "kiefergelenk", "cmd", "zahnschmerz", "kiefer",
        "amalgam", "wurzelbehandlung", "parodontose"
    ],
    "meridiane_tcm_detailliert": [
        "meridian", "tcm", "akupunktur", "chi", "qi", "energie",
        "chakra", "energetisch"
    ],
    "emf_stoerfelder_detailliert": [
        "strahlung", "emf", "elektrosmog", "5g", "wlan", "geopathie",
        "erdstrahlen", "wasserader"
    ],
    "hormone_stoffwechsel_detailliert": [
        "hormone", "schilddrüse", "stoffwechsel", "nebenniere",
        "diabetes", "gewicht", "thyroid", "endokrin"
    ],
    "psyche_emotion_detailliert": [
        "stress", "depression", "angst", "emotion", "trauma", "psyche",
        "burnout", "panik", "schlaf", "müdigkeit"
    ],
}

# Profil-Beschreibungen für Anzeige
PROFILE_DESCRIPTIONS: Dict[str, str] = {
    "gehirn_detailliert": "Neurologische Analyse (Gehirn, Nerven, Kopf)",
    "lymphsystem_detailliert": "Lymphatisches System und Entgiftung",
    "immunsystem_detailliert": "Immunologische Analyse und Abwehr",
    "zaehne_kiefer_detailliert": "Zahnmedizinische und Kieferanalyse",
    "meridiane_tcm_detailliert": "TCM Meridiane und Energetik",
    "emf_stoerfelder_detailliert": "EMF und Störfeld-Analyse",
    "hormone_stoffwechsel_detailliert": "Hormonelle und metabolische Analyse",
    "psyche_emotion_detailliert": "Psychosomatik und Emotionen",
}


def recommend_profiles(focus: str, top_k: int = 3) -> List[Dict]:
    """
    Empfiehlt Profile basierend auf Fokus-Eingabe.
    
    Args:
        focus: Eingabe-Fokus (kann Multi-Fokus sein)
        top_k: Maximale Anzahl Empfehlungen
    
    Returns:
        Liste von Empfehlungen mit Score und Beschreibung
    """
    if not focus:
        return []
    
    # Erweitere Fokus um Synonyme
    focus_keywords = set(kw.lower() for kw in expand_focus_keywords(focus))
    canonical = get_canonical_focus(focus).lower()
    focus_keywords.add(canonical)
    
    # Auch Wörter aus Original-Fokus
    for word in focus.lower().split():
        if len(word) > 2:
            focus_keywords.add(word)
    
    # Score für jedes Profil berechnen
    scores: List[Tuple[str, float, int]] = []
    
    for profile, profile_terms in PROFILE_FOCUS_MAP.items():
        profile_terms_lower = set(t.lower() for t in profile_terms)
        
        # Zähle Übereinstimmungen
        matches = focus_keywords & profile_terms_lower
        
        # Bonus für kanonische Übereinstimmung
        canonical_match = canonical in profile_terms_lower
        
        if matches or canonical_match:
            score = len(matches) * 2.0
            if canonical_match:
                score += 5.0
            
            # Normalisiere (0-1)
            normalized_score = min(1.0, score / 10.0)
            scores.append((profile, normalized_score, len(matches)))
    
    # Sortiere nach Score
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # Top-K zurückgeben
    result = []
    for profile, score, match_count in scores[:top_k]:
        if score > 0:
            result.append({
                "profile": profile,
                "score": round(score, 5),
                "match_count": match_count,
                "description": PROFILE_DESCRIPTIONS.get(profile, ""),
                "relevance": "hoch" if score > 0.7 else "mittel" if score > 0.3 else "niedrig"
            })
    
    return result


def get_best_profile(focus: str) -> Optional[str]:
    """
    Gibt das am besten passende Profil zurück.
    
    Args:
        focus: Eingabe-Fokus
    
    Returns:
        Profil-Name oder None
    """
    recommendations = recommend_profiles(focus, top_k=1)
    if recommendations:
        return recommendations[0]["profile"]
    return None


def explain_recommendation(focus: str, profile: str) -> str:
    """
    Erklärt warum ein Profil empfohlen wurde.
    
    Args:
        focus: Eingabe-Fokus
        profile: Empfohlenes Profil
    
    Returns:
        Erklärung
    """
    focus_keywords = set(kw.lower() for kw in expand_focus_keywords(focus))
    profile_terms = set(t.lower() for t in PROFILE_FOCUS_MAP.get(profile, []))
    
    matches = focus_keywords & profile_terms
    
    if matches:
        return f"Übereinstimmung bei: {', '.join(sorted(matches))}"
    
    return "Allgemeine Relevanz basierend auf Fokus-Kategorie"


def format_recommendations_display(recommendations: List[Dict]) -> str:
    """
    Formatiert Empfehlungen für Konsolen-Ausgabe.
    
    Args:
        recommendations: Liste von Empfehlungen
    
    Returns:
        Formatierte Zeichenkette
    """
    if not recommendations:
        return "Keine passenden Profile gefunden."
    
    lines = ["Empfohlene Profile:"]
    for i, rec in enumerate(recommendations, 1):
        lines.append(
            f"  {i}. {rec['profile']} "
            f"(Relevanz: {rec['relevance']}, Score: {rec['score']:.2f})"
        )
        if rec['description']:
            lines.append(f"     → {rec['description']}")
    
    return "\n".join(lines)
