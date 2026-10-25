#!/usr/bin/env python3
"""
Zentrale Registry für Remedy-Gruppen.

WICHTIG: Neue Remedy-Gruppen müssen NUR HIER hinzugefügt werden!
Alle anderen Module importieren diese Konfiguration.

Checkliste für neue Remedy-Gruppen:
1. Gruppe zu EXPLICIT_REMEDY_GROUPS hinzufügen
2. Optional: Token zu REMEDY_TOKENS hinzufügen (für Namens-Heuristik)
3. Optional: Präfix zu REMEDY_PREFIXES hinzufügen
4. Optional: Suffix zu REMEDY_SUFFIXES hinzufügen
5. Gruppe zu GROUP_DISPLAY_INFO hinzufügen (für HTML-Berichte)

Das war's! Keine weiteren Änderungen in main.py oder anderen Dateien nötig.
"""

from typing import Dict, Tuple, Set

# =============================================================================
# EXPLIZITE REMEDY-GRUPPEN
# =============================================================================
# Alle bekannten Remedy-Gruppen (exakte Namen)
EXPLICIT_REMEDY_GROUPS: Set[str] = {
    # Klassische Homöopathie
    "homoeopathie_klassisch",
    "homoeopathie_klassisch_potenzen",
    "homoeopathie_komplexmittel",
    "homoeopathie_isopathie",
    "homoeopathie_nosoden",
    # TCM
    "tcm_rezepturen",
    "tcm_rezepturen_potenzen",
    # Spagyrik
    "spagyrik",
    "spagyrik_multiplex",
    # Bachblüten
    "bachblueten_multiplex",
    # Frequenz-Therapien
    "frequenz_clark_multiplex",
    "frequenz_rife_multiplex",
    "frequenz_solfeggio_multiplex",
    # Zentrale Multiplex-Remedy-Container
    "energie_remedies_multiplex",
    "entgiftung_remedies_multiplex",
    "toxine_remedies_multiplex",
    "atmung_remedies_multiplex",
    "nahrung_remedies_multiplex",
    "luft_remedies_multiplex",
    "nerven_remedies_multiplex",
    "knochen_remedies_multiplex",
    "wirbelsaeule_remedies_multiplex",
    "orthomolekular_therapie_multiplex",
    "anti_infektions_remedies_multiplex",
    "immunstaerkung_remedies_multiplex",
    "verdauung_remedies_multiplex",
    "bewegung_remedies_multiplex",
    "schmerz_remedies_multiplex",
    "allergie_remedies_multiplex",
    "endokrin_remedies_multiplex",
    "haut_remedies_multiplex",
    "schwindel_remedies_multiplex",
    "strahlung_remedies_multiplex",
    "stoerfeld_remedies_multiplex",
    "psyche_remedies_multiplex",
    "miasmatik_remedies_multiplex",
    # Hersteller-spezifische Remedy-Gruppen
    "heel_remedies_multiplex",
    "nutramedix_remedies_multiplex",
    "schuessler_remedies_multiplex",
    # OOREP Klassische Homöopathie (2432 Einzelmittel)
    "oorep_homeopathy_multiplex",
}

# =============================================================================
# REMEDY-TOKENS (für Namens-Heuristik)
# =============================================================================
# Wenn ein Gruppenname eines dieser Tokens enthält, wird er als Remedy erkannt
REMEDY_TOKENS: Tuple[str, ...] = (
    # Homöopathie
    "homoeopathie",
    "homöopathie",
    "homeopathy",
    # Spagyrik
    "spagyrik",
    # Rezepturen
    "rezeptur",
    "rezepturen",
    # Blüten
    "blten",  # robust gegen Kodierungsvarianten
    "bluten",
    "blueten",
    "flower",
    # Nosoden
    "nosoden",
    "nosode",
    # Bioresonanz
    "bioresonanz",
    # Farben
    "farb",
    "color",
    "farbe",
    # Edelsteine
    "edelstein",
    "edelsteine",
    "gemstone",
    # Generische Remedy-/Therapie-Container
    "remedy",
    "remedies",
    "therapie_multiplex",
    "therapy_multiplex",
    "orthomolekular_therapie",
    # Hersteller-spezifische Tokens
    "heel",
    "nutramedix",
    "homotoxikologie",
    "phytotherapie",
    "schuessler",
    "schüssler",
    # OOREP
    "oorep",
)

# =============================================================================
# REMEDY-PRÄFIXE (für Namens-Heuristik)
# =============================================================================
# Wenn ein Gruppenname mit einem dieser Präfixe beginnt, wird er als Remedy erkannt
REMEDY_PREFIXES: Tuple[str, ...] = (
    "homoeopathie_",
    "spagyrik",
    "bachblueten",
    "tcm_rezepturen",
    "frequenz_",
    "oorep_",
)

# =============================================================================
# REMEDY-SUFFIXE (für Namens-Heuristik)
# =============================================================================
# Wenn ein Gruppenname mit einem dieser Suffixe endet, wird er als Remedy erkannt
REMEDY_SUFFIXES: Tuple[str, ...] = (
    "_remedies_multiplex",
    "_multiplex",  # Vorsicht: Kann auch Nicht-Remedies matchen
)

# =============================================================================
# DISPLAY-INFO FÜR HTML-BERICHTE
# =============================================================================
# (group_key, display_title, description)
GROUP_DISPLAY_INFO: Dict[str, Tuple[str, str]] = {
    # Hersteller-spezifische Remedy-Gruppen
    "heel_remedies_multiplex": ("Heel Homotoxikologie", "Biologische Komplexmittel nach Dr. Reckeweg"),
    "nutramedix_remedies_multiplex": ("Nutramedix Phytotherapie", "Pflanzliche Extrakte für Borreliose & Entgiftung"),
    "schuessler_remedies_multiplex": ("Schüssler-Salze", "Biochemische Mineralsalze nach Dr. Schüßler"),
    # OOREP Klassische Homöopathie
    "oorep_homeopathy_multiplex": ("OOREP Klassische Homöopathie", "2432 Einzelmittel nach Kent, Boericke, Hahnemann"),
    "allergie_remedies_multiplex": ("Allergie-Multiplex", "Allergiebezogene Mittelgruppen und Regulationshilfen"),
    "bewegung_remedies_multiplex": ("Bewegungsapparat-Multiplex", "Mittelgruppen für Muskeln, Gelenke, Sehnen und Bänder"),
    "endokrin_remedies_multiplex": ("Endokrin-Multiplex", "Mittelgruppen für Hormonachsen und endokrine Regulation"),
    "haut_remedies_multiplex": ("Haut-Multiplex", "Mittelgruppen für Haut, Narben und Barrierefunktionen"),
    "schmerz_remedies_multiplex": ("Schmerz-Multiplex", "Mittelgruppen für akute und chronische Schmerzresonanzen"),
    "schwindel_remedies_multiplex": ("Schwindel-Multiplex", "Mittelgruppen für vestibuläre, zentrale und Kreislauf-Bezüge"),
    "stoerfeld_remedies_multiplex": ("Störfeld-Multiplex", "Mittelgruppen für Narben, Zahnherde und fokale Belastungen"),
    "strahlung_remedies_multiplex": ("Strahlungs-Multiplex", "Mittelgruppen für Strahlungs- und EMF-Belastungskontexte"),
}


# =============================================================================
# HAUPTFUNKTION: Remedy-Gruppen-Erkennung
# =============================================================================
def is_remedy_group(group: str) -> bool:
    """
    Zentrale Funktion zur Erkennung von Remedy-Gruppen.
    
    Verwendet:
    1. Explizite Liste bekannter Remedy-Gruppen
    2. Namens-Heuristik (Tokens, Präfixe, Suffixe)
    
    Args:
        group: Name der Gruppe
        
    Returns:
        True wenn es eine Remedy-Gruppe ist, sonst False
    """
    g = (group or "").strip().lower()
    if not g:
        return False
    
    # 1. Explizite Gruppen
    if g in EXPLICIT_REMEDY_GROUPS:
        return True
    
    # 2. Token-basierte Heuristik
    for tok in REMEDY_TOKENS:
        if tok in g:
            return True
    
    # 3. Präfix-basierte Heuristik
    for prefix in REMEDY_PREFIXES:
        if g.startswith(prefix):
            return True
    
    # 4. Suffix-basierte Heuristik (nur _remedies_multiplex, nicht generisch _multiplex)
    if g.endswith("_remedies_multiplex"):
        return True
    
    return False


def get_display_info(group: str) -> Tuple[str, str] | None:
    """
    Gibt Display-Informationen für eine Remedy-Gruppe zurück.
    
    Args:
        group: Name der Gruppe
        
    Returns:
        Tuple (title, description) oder None wenn nicht gefunden
    """
    g = (group or "").strip().lower()
    return GROUP_DISPLAY_INFO.get(g)


def list_all_remedy_groups() -> list[str]:
    """Gibt alle explizit bekannten Remedy-Gruppen zurück."""
    return sorted(EXPLICIT_REMEDY_GROUPS)


# =============================================================================
# ANLEITUNG FÜR NEUE REMEDY-GRUPPEN
# =============================================================================
"""
ANLEITUNG: Neue Remedy-Gruppe hinzufügen

1. Gruppe zur Datenbank hinzufügen:
   - remedies.db: Einträge mit category = "neue_gruppe_multiplex"
   
2. Gruppe in procedural_groups.py registrieren:
   - _DYNAMIC_GROUPS.append("neue_gruppe_multiplex")
   - db_category_map["neue_gruppe_multiplex"] = "neue_gruppe_multiplex"

3. Gruppe HIER in remedy_group_registry.py hinzufügen:
   - EXPLICIT_REMEDY_GROUPS: "neue_gruppe_multiplex" hinzufügen
   - GROUP_DISPLAY_INFO: Display-Titel und Beschreibung hinzufügen
   - Optional: Token/Präfix hinzufügen wenn Namenskonvention

4. Optional: Profil in profiles/registry.py erstellen

5. Optional: PowerShell-Auswahl in Run-MultiplexScan.ps1 hinzufügen

Das war's! Die Gruppe wird automatisch:
- Als Remedy erkannt
- In Synergien berücksichtigt
- Im HTML-Bericht korrekt angezeigt
"""
