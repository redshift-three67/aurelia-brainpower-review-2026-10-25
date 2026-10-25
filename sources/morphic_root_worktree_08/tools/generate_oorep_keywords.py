#!/usr/bin/env python3
"""
Generiert Keywords für OOREP homöopathische Mittel.

Extrahiert relevante Keywords aus den Mittelnamen für die Suche und Zuordnung.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# Pfade
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
REMEDIES_DB = DATA_DIR / "remedies.db"

# Kategorie
CATEGORY = "oorep_homeopathy_multiplex"

# Keyword-Mapping für häufige homöopathische Begriffe
KEYWORD_MAPPINGS = {
    # Pflanzen
    "arnica": ["verletzung", "trauma", "bluterguss", "muskel", "schmerz"],
    "belladonna": ["fieber", "entzuendung", "kopfschmerz", "roetung", "akut"],
    "bryonia": ["schmerz", "bewegung", "trockenheit", "husten", "gelenk"],
    "chamomilla": ["schmerz", "reizbarkeit", "zahnung", "kolik", "kind"],
    "nux vomica": ["verdauung", "uebelkeit", "leber", "stress", "ueberarbeitung"],
    "pulsatilla": ["erkaeltung", "schleim", "weinerlich", "hormon", "frauen"],
    "rhus": ["gelenk", "rheuma", "steifheit", "bewegung", "haut"],
    "sulphur": ["haut", "juckreiz", "entgiftung", "chronisch", "waerme"],
    "phosphorus": ["blutung", "lunge", "angst", "erschoepfung", "nerven"],
    "lycopodium": ["verdauung", "leber", "blaehung", "selbstvertrauen"],
    "sepia": ["hormon", "frauen", "erschoepfung", "depression", "uterus"],
    "natrum": ["kopfschmerz", "trauer", "salz", "trockenheit"],
    "calcarea": ["knochen", "entwicklung", "schwaeche", "kalk", "kind"],
    "silicea": ["eiterung", "knochen", "schwaeche", "bindegewebe", "narben"],
    "arsenicum": ["angst", "erschoepfung", "durchfall", "vergiftung", "brennen"],
    "aconitum": ["schock", "angst", "fieber", "akut", "kaelte"],
    "apis": ["schwellung", "oedem", "stich", "allergie", "hitze"],
    "argentum": ["angst", "nerven", "schleimhaut", "verdauung"],
    "aurum": ["depression", "herz", "knochen", "schwermut"],
    "baryta": ["entwicklung", "druesen", "alter", "kind"],
    "carbo": ["schwaeche", "kollaps", "verdauung", "blaehung"],
    "causticum": ["lahmung", "heiserkeit", "warzen", "brennen"],
    "china": ["schwaeche", "fieber", "blaehung", "blutung"],
    "conium": ["druesen", "lahmung", "schwindel", "alter"],
    "gelsemium": ["grippe", "schwaeche", "zittern", "angst", "lahmung"],
    "hepar": ["eiterung", "empfindlichkeit", "kaelte", "haut"],
    "ignatia": ["trauer", "krampf", "hysterie", "emotion"],
    "kali": ["schleim", "erkaeltung", "verdauung", "schwaeche"],
    "lachesis": ["blut", "herz", "eifersucht", "links", "klimakterium"],
    "mercurius": ["speichel", "druesen", "entzuendung", "nacht"],
    "thuja": ["warzen", "impfung", "haut", "wucherung"],
    "tuberculinum": ["lunge", "erkaeltung", "unruhe", "abmagerung"],
    "medorrhinum": ["schleim", "rheuma", "harnwege", "miasma"],
    "carcinosinum": ["krebs", "erschoepfung", "perfektion", "miasma"],
    "staphysagria": ["aerger", "unterdrueckung", "harnwege", "wunden"],
    "stramonium": ["angst", "gewalt", "dunkelheit", "krampf"],
    "veratrum": ["kollaps", "kaelte", "durchfall", "schweiss"],
    "zincum": ["nerven", "unruhe", "beine", "erschoepfung"],
    # Nosoden
    "nosode": ["nosode", "miasma", "chronisch"],
    "bacillinum": ["lunge", "tuberkulose", "nosode"],
    "medorrhinum": ["gonorrhoe", "nosode", "schleim"],
    "syphilinum": ["syphilis", "nosode", "knochen"],
    "psorinum": ["haut", "nosode", "juckreiz"],
    # Säuren
    "acidum": ["saeure", "schwaeche", "verdauung"],
    "phosphoricum": ["erschoepfung", "nerven", "durchfall"],
    "muriaticum": ["salzsaeure", "verdauung", "emotion"],
    "nitricum": ["schleimhaut", "warzen", "splitter"],
    "sulphuricum": ["schwaeche", "zittern", "verdauung"],
    # Metalle
    "metallicum": ["metall", "konstitution"],
    "ferrum": ["eisen", "blut", "anaemie", "schwaeche"],
    "cuprum": ["krampf", "kolik", "muskel"],
    "plumbum": ["lahmung", "kolik", "verstopfung"],
    "stannum": ["schwaeche", "lunge", "erschoepfung"],
    # Salze
    "carbonicum": ["karbonat", "schwaeche", "verdauung"],
    "sulphuratum": ["schwefel", "haut", "entgiftung"],
    "iodatum": ["jod", "druesen", "schilddruese"],
    "bromatum": ["brom", "nerven", "druesen"],
    # Tierische
    "apis": ["biene", "schwellung", "stich"],
    "lachesis": ["schlange", "blut", "links"],
    "tarentula": ["spinne", "unruhe", "zucken"],
    "cantharis": ["blase", "brennen", "harnwege"],
    "sepia": ["tintenfisch", "hormon", "frauen"],
}


def extract_keywords_from_name(name: str, abbrev: str) -> list[str]:
    """Extrahiert Keywords aus dem Mittelnamen."""
    keywords = set()
    name_lower = name.lower()
    abbrev_lower = abbrev.lower() if abbrev else ""
    
    # Basis-Keywords aus dem Namen
    keywords.add("homoeopathie")
    keywords.add("klassisch")
    keywords.add("einzelmittel")
    
    # Prüfe Mapping
    for key, kw_list in KEYWORD_MAPPINGS.items():
        if key in name_lower or key in abbrev_lower:
            keywords.update(kw_list)
    
    # Spezielle Kategorien erkennen
    if "nosode" in name_lower or name_lower.endswith("inum"):
        keywords.add("nosode")
    
    if "acidum" in name_lower or "acid" in name_lower:
        keywords.add("saeure")
    
    if "metallicum" in name_lower or "met." in abbrev_lower:
        keywords.add("metall")
    
    if "carbonicum" in name_lower or "-c." in abbrev_lower:
        keywords.add("karbonat")
    
    if "sulph" in name_lower:
        keywords.add("schwefel")
    
    if "calc" in name_lower:
        keywords.add("kalk")
        keywords.add("knochen")
    
    if "nat" in name_lower[:4]:
        keywords.add("natrium")
    
    if "kali" in name_lower[:4]:
        keywords.add("kalium")
    
    if "ferr" in name_lower[:4]:
        keywords.add("eisen")
    
    if "arg" in name_lower[:4]:
        keywords.add("silber")
    
    if "aur" in name_lower[:4]:
        keywords.add("gold")
    
    if "cupr" in name_lower[:4]:
        keywords.add("kupfer")
    
    if "plumb" in name_lower[:5]:
        keywords.add("blei")
    
    if "merc" in name_lower[:4]:
        keywords.add("quecksilber")
    
    # Pflanzliche Mittel (häufige Endungen)
    plant_indicators = ["vulgaris", "officinalis", "alba", "nigra", "rubra", 
                        "montana", "sylvestris", "arvensis", "pratensis"]
    for indicator in plant_indicators:
        if indicator in name_lower:
            keywords.add("pflanze")
            keywords.add("phytotherapie")
            break
    
    return sorted(keywords)


def generate_keywords():
    """Generiert Keywords für alle OOREP-Mittel."""
    
    print("=" * 60)
    print("OOREP Keywords Generator")
    print("=" * 60)
    
    conn = sqlite3.connect(REMEDIES_DB)
    cursor = conn.cursor()
    
    # Hole alle OOREP-Mittel
    cursor.execute("""
        SELECT id, name, abbrev 
        FROM remedies 
        WHERE category = ?
    """, (CATEGORY,))
    
    remedies = cursor.fetchall()
    print(f"Gefunden: {len(remedies)} Mittel")
    
    # Prüfe ob Keywords-Tabelle existiert
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='remedy_keywords'
    """)
    if not cursor.fetchone():
        print("Erstelle remedy_keywords Tabelle...")
        cursor.execute("""
            CREATE TABLE remedy_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remedy_id INTEGER NOT NULL,
                keyword TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                FOREIGN KEY (remedy_id) REFERENCES remedies(id)
            )
        """)
    
    # Zähle existierende Keywords für OOREP
    cursor.execute("""
        SELECT COUNT(*) FROM remedy_keywords rk
        JOIN remedies r ON rk.remedy_id = r.id
        WHERE r.category = ?
    """, (CATEGORY,))
    existing = cursor.fetchone()[0]
    
    if existing > 0:
        print(f"⚠️  {existing} Keywords existieren bereits für OOREP")
        print("   Überspringe Generierung (keine Duplikate)")
        conn.close()
        return
    
    # Generiere Keywords
    total_keywords = 0
    for remedy_id, name, abbrev in remedies:
        keywords = extract_keywords_from_name(name, abbrev)
        
        for i, kw in enumerate(keywords):
            cursor.execute("""
                INSERT INTO remedy_keywords (remedy_id, keyword, priority)
                VALUES (?, ?, ?)
            """, (remedy_id, kw, i))
            total_keywords += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ {total_keywords} Keywords generiert für {len(remedies)} Mittel")
    print(f"   Durchschnitt: {total_keywords / len(remedies):.1f} Keywords pro Mittel")


if __name__ == "__main__":
    generate_keywords()
