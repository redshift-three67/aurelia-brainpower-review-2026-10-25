#!/usr/bin/env python3
"""
Beschreibungs-Datenbank für Meridiane, Chakras, Remedies und andere Elemente.
Bietet kurze, prägnante Beschreibungen für bessere Klienten-Kommunikation.
"""

from typing import Dict, Optional

# === MERIDIANE BESCHREIBUNGEN ===
MERIDIAN_DESCRIPTIONS = {
    "Lunge": "Atmung, Immunabwehr, Hautfunktion, emotionale Verarbeitung von Trauer",
    "Dickdarm": "Ausscheidung, Entgiftung, Loslassen auf körperlicher und emotionaler Ebene",
    "Magen": "Verdauung, Nährstoffaufnahme, Sorgen und Grübeln, Erdung",
    "Milz-Pankreas": "Blutzucker, Immunsystem, Transformation, Konzentration und Denken",
    "Herz": "Kreislauf, Bewusstsein, Freude, emotionale Klarheit und Liebe",
    "DuennDarm": "Nährstoffaufnahme, Entscheidungsfindung, Trennung von Wichtigem und Unwichtigem",
    "Blase": "Wasserhaushalt, Ausscheidung, Willenskraft, Ängste und Phobien",
    "Niere": "Entgiftung, Lebensenergie (Jing), Fortpflanzung, Grundkonstitution",
    "Perikard": "Herzschutz, emotionale Abgrenzung, Beziehungen, Kreislaufregulation",
    "Drei-Erwaermer": "Wärmeregulation, Stoffwechsel, Energieverteilung, hormonelle Balance",
    "Gallenblase": "Fettverdauung, Entscheidungskraft, Mut, Flexibilität",
    "Leber": "Entgiftung, Blutbildung, Planung, Wut und Frustration, Flexibilität",
}

# === CHAKRAS BESCHREIBUNGEN ===
CHAKRA_DESCRIPTIONS = {
    "Wurzelchakra": "Erdung, Sicherheit, Überleben, Urvertrauen, materielle Stabilität",
    "Sakralchakra": "Kreativität, Sexualität, Emotionen, Lebensfreude, Beziehungen",
    "Solarplexus": "Persönliche Macht, Selbstwert, Willenskraft, Verdauung, Kontrolle",
    "Herzchakra": "Liebe, Mitgefühl, Verbindung, Heilung, emotionale Balance",
    "Kehlchakra": "Kommunikation, Ausdruck, Wahrheit, Kreativität, Authentizität",
    "Stirnchakra": "Intuition, Klarheit, Weisheit, geistige Wahrnehmung, Erkenntnis",
    "Kronenchakra": "Spiritualität, Bewusstsein, Verbindung zum Höheren, Erleuchtung",
    "Thymuschakra": "Immunsystem, Selbstliebe, Heilung, emotionale Transformation",
    "Milzchakra": "Energieaufnahme, Vitalität, Abgrenzung, emotionale Reinigung",
    "Handchakra": "Heilkraft, Manifestation, Berührung, energetische Übertragung",
    "Fußchakra": "Erdverbindung, Stabilität, Energieaufnahme aus der Erde",
}

# === HOMÖOPATHISCHE MITTEL BESCHREIBUNGEN ===
HOMEOPATHY_DESCRIPTIONS = {
    "Bryonia": "Trockenheit, langsame Entwicklung, Verschlimmerung durch Bewegung, Reizbarkeit",
    "Rhus toxicodendron": "Steifheit, Besserung durch Bewegung, Unruhe, Hautprobleme",
    "Belladonna": "Akute Entzündungen, Hitze, Röte, plötzlicher Beginn, Fieber",
    "Arnica": "Verletzungen, Trauma, Blutergüsse, Schock, Erschöpfung",
    "Nux vomica": "Stress, Überarbeitung, Verdauungsprobleme, Reizbarkeit, Entgiftung",
    "Pulsatilla": "Wechselhafte Symptome, sanfte Natur, Besserung an frischer Luft",
    "Sulphur": "Hautprobleme, Entgiftung, Hitze, Brennen, chronische Zustände",
    "Phosphorus": "Nervensystem, Blutungen, Ängste, Sensibilität, Erschöpfung",
    "Calcarea carbonica": "Konstitutionsmittel, Knochen, Stoffwechsel, Ängste, Kälte",
    "Lycopodium": "Verdauung, Leber, Selbstvertrauen, Blähungen, Rechtsseitigkeit",
}

# === TCM REZEPTUREN BESCHREIBUNGEN ===
TCM_FORMULAS_DESCRIPTIONS = {
    "Liu Wei Di Huang Wan": "Nieren-Yin stärken, Grundkonstitution, Anti-Aging, Erschöpfung",
    "Bu Zhong Yi Qi Tang": "Mitte stärken, Qi-Mangel, Verdauung, Immunsystem, Energie",
    "Gan Mai Da Zao Tang": "Emotionale Stabilität, Nervosität, Herz-Geist beruhigen",
    "Xiao Yao San": "Leber-Qi bewegen, Stress, emotionale Blockaden, Menstruationsprobleme",
    "An Shen Ding Zhi Wan": "Geist beruhigen, Schlafstörungen, Angst, emotionale Unruhe",
    "Ding Zhi Wan": "Phlegm-Hitze klären, geistige Klarheit, Konzentration, Verwirrung",
}

# === SPAGYRIK BESCHREIBUNGEN ===
SPAGYRIK_DESCRIPTIONS = {
    "Sulfur": "Transformationsprozesse, Entgiftung, Stoffwechsel, inneres Feuer",
    "Mercurius": "Kommunikation, Nervensystem, Flexibilität, Anpassungsfähigkeit",
    "Sal": "Kristallisation, Struktur, Stabilität, Erdung, Manifestation",
    "Ars Metallorum": "Reinigung, Transformation, Auflösung alter Muster",
    "Antimonium": "Grenzziehung, Abgrenzung, Struktur, Ordnung",
    "Cuprum": "Liebe, Schönheit, Harmonie, Kreislauf, Venussignatur",
    "Ferrum": "Willenskraft, Durchsetzung, Blutbildung, Marssignatur",
}

# === EDELSTEINE BESCHREIBUNGEN ===
GEMSTONE_DESCRIPTIONS = {
    "Amethyst": "Spiritualität, Klarheit, Schutz, Transformation, Suchtbefreiung",
    "Bergkristall": "Verstärkung, Klarheit, Reinigung, universelle Heilung",
    "Rosenquarz": "Liebe, Herzöffnung, Selbstliebe, emotionale Heilung",
    "Citrin": "Lebensfreude, Manifestation, Selbstvertrauen, Fülle",
    "Achat": "Stabilität, Erdung, Schutz, emotionale Balance",
    "Jaspis": "Erdung, Ausdauer, Schutz, körperliche Stärkung",
    "Sodalith": "Kommunikation, Wahrheit, geistige Klarheit, Intuition",
    "Labradorit": "Transformation, Intuition, Schutz, magische Kräfte",
    "Turmalin": "Schutz, Erdung, Energiereinigung, elektromagnetischer Schutz",
    "Malachit": "Transformation, Herzöffnung, emotionale Heilung, Entgiftung",
}

# === FARBTHERAPIE BESCHREIBUNGEN ===
COLOR_THERAPY_DESCRIPTIONS = {
    "Rot–Grün": "Aktivierung und Beruhigung, Herz-Kreislauf, emotionale Balance",
    "Blau–Orange": "Kommunikation und Kreativität, Kehlchakra und Sakralchakra",
    "Gelb–Violett": "Intellekt und Spiritualität, Solarplexus und Kronenchakra",
    "Cyan–Rot": "Kühlung und Aktivierung, Entzündungshemmung und Durchblutung",
    "Magenta–Grün": "Transformation und Wachstum, Herzöffnung und Erneuerung",
    "Gelb–Indigo": "Klarheit und Intuition, mentale Aktivität und innere Weisheit",
}

def get_description(item_label: str, category: str = "auto") -> Optional[str]:
    """
    Gibt eine Beschreibung für ein Element zurück.
    
    Args:
        item_label: Name des Elements
        category: Kategorie ("meridian", "chakra", "homeopathy", "tcm", "spagyrik", "gemstone", "color", "auto")
    
    Returns:
        Beschreibung oder None falls nicht gefunden
    """
    if category == "auto":
        # Automatische Erkennung basierend auf dem Label
        for desc_dict in [MERIDIAN_DESCRIPTIONS, CHAKRA_DESCRIPTIONS, HOMEOPATHY_DESCRIPTIONS, 
                         TCM_FORMULAS_DESCRIPTIONS, SPAGYRIK_DESCRIPTIONS, GEMSTONE_DESCRIPTIONS, 
                         COLOR_THERAPY_DESCRIPTIONS]:
            if item_label in desc_dict:
                return desc_dict[item_label]
        return None
    
    category_map = {
        "meridian": MERIDIAN_DESCRIPTIONS,
        "chakra": CHAKRA_DESCRIPTIONS, 
        "homeopathy": HOMEOPATHY_DESCRIPTIONS,
        "tcm": TCM_FORMULAS_DESCRIPTIONS,
        "spagyrik": SPAGYRIK_DESCRIPTIONS,
        "gemstone": GEMSTONE_DESCRIPTIONS,
        "color": COLOR_THERAPY_DESCRIPTIONS,
    }
    
    desc_dict = category_map.get(category)
    if desc_dict:
        return desc_dict.get(item_label)
    
    return None

def get_all_descriptions() -> Dict[str, str]:
    """Gibt alle verfügbaren Beschreibungen zurück."""
    all_descriptions = {}
    for desc_dict in [MERIDIAN_DESCRIPTIONS, CHAKRA_DESCRIPTIONS, HOMEOPATHY_DESCRIPTIONS,
                     TCM_FORMULAS_DESCRIPTIONS, SPAGYRIK_DESCRIPTIONS, GEMSTONE_DESCRIPTIONS,
                     COLOR_THERAPY_DESCRIPTIONS]:
        all_descriptions.update(desc_dict)
    return all_descriptions
