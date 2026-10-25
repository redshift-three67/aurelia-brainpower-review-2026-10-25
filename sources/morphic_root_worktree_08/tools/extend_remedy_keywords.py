"""
Erweitert Heel & Nutramedix Keywords für vollständige Profil-Integration.

Ziel: Heel & Nutramedix sollen in ALLEN relevanten Standard-Profilen erscheinen,
genau wie bestehende Remedies (Homöopathie, Bachblüten, etc.)

Dieses Script fügt medizinische Basis-Keywords hinzu basierend auf:
1. Bekannten Indikationen der Mittel
2. Therapeutischen Kategorien
3. Körpersystemen
"""

import sqlite3
from pathlib import Path

# ============================================================================
# HEEL KEYWORD-MAPPING (basierend auf bekannten Indikationen)
# ============================================================================
HEEL_KEYWORD_MAP = {
    # Infektionen & Immunsystem
    "Aconitum-Homaccord": ["infekt", "grippe", "erkältung", "fieber", "viren", "immunsystem"],
    "Engystol N": ["viren", "grippe", "infekt", "immunsystem", "erkältung", "herpes"],
    "Gripp-Heel": ["grippe", "infekt", "viren", "erkältung", "fieber", "immunsystem"],
    "Echinacea compositum SN": ["immunsystem", "infekt", "bakterien", "abwehr", "entzündung"],
    "Traumeel S": ["entzündung", "verletzung", "schmerz", "schwellung", "trauma"],
    
    # Entgiftung & Leber
    "Hepar compositum N": ["leber", "entgiftung", "hepatitis", "stoffwechsel", "galle"],
    "Hepeel N": ["leber", "entgiftung", "hepatopathie", "stoffwechsel"],
    "Nux vomica-Homaccord": ["leber", "entgiftung", "magen", "verdauung", "übelkeit"],
    "Chelidonium-Homaccord N": ["leber", "galle", "entgiftung", "stoffwechsel"],
    "Solidago compositum SN": ["niere", "entgiftung", "ausleitung", "harnwege"],
    
    # Verdauung
    "Gastricumeel": ["magen", "verdauung", "gastritis", "sodbrennen", "übelkeit"],
    "Duodenoheel": ["verdauung", "darm", "duodenum", "magen"],
    "Diarrheel SN": ["darm", "durchfall", "verdauung", "diarrhoe"],
    "Mucosa compositum": ["schleimhaut", "darm", "verdauung", "magen"],
    
    # Herz-Kreislauf
    "Cor compositum N": ["herz", "kreislauf", "kardio", "herzinsuffizienz"],
    "Cralonin": ["herz", "kreislauf", "angina", "herzrhythmus"],
    "Aurumheel N": ["herz", "kreislauf", "blutdruck", "depression"],
    
    # Nervensystem & Psyche
    "Nervoheel N": ["nerven", "stress", "angst", "schlaf", "psyche", "unruhe"],
    "Neurexan": ["schlaf", "stress", "nerven", "unruhe", "angst"],
    "Ignatia-Homaccord": ["psyche", "trauer", "stress", "depression", "nerven"],
    "Valerianaheel": ["schlaf", "nerven", "unruhe", "stress", "beruhigung"],
    
    # Bewegungsapparat
    "Zeel comp. N": ["gelenke", "arthrose", "rheuma", "bewegung", "schmerz"],
    "Rhus toxicodendron-Homaccord": ["gelenke", "rheuma", "schmerz", "bewegung"],
    "Colocynthis-Homaccord": ["nerven", "neuralgie", "schmerz", "ischias"],
    
    # Atemwege
    "Bronchalis-Heel": ["atemwege", "bronchien", "husten", "lunge"],
    "Tartephedreel N": ["atemwege", "bronchien", "husten", "schleim"],
    "Husteel": ["husten", "atemwege", "bronchien", "erkältung"],
    
    # Haut
    "Cutis compositum N": ["haut", "ekzem", "dermatose", "allergie"],
    "Graphites-Homaccord": ["haut", "ekzem", "narben", "wundheilung"],
    "Schwef-Heel": ["haut", "ekzem", "allergie", "juckreiz"],
    
    # Hormone
    "Hormeel SN": ["hormone", "zyklus", "wechseljahre", "menstruation"],
    "Gynäcoheel N": ["hormone", "zyklus", "frauenleiden", "menstruation"],
    "Thyreoidea compositum": ["schilddrüse", "hormone", "stoffwechsel"],
    
    # Lymphe & Drainage
    "Lymphomyosot": ["lymphe", "drainage", "ödem", "entgiftung", "immunsystem"],
    "Galium-Heel N": ["entgiftung", "drainage", "zellular", "ausleitung"],
}

# ============================================================================
# NUTRAMEDIX KEYWORD-MAPPING
# ============================================================================
NUTRAMEDIX_KEYWORD_MAP = {
    # Borreliose & Infektionen
    "Banderol": ["borreliose", "bakterien", "infekt", "lyme", "biofilm"],
    "Samento": ["borreliose", "immunsystem", "infekt", "lyme", "entzündung"],
    "Cumanda": ["borreliose", "bakterien", "parasiten", "infekt", "biofilm"],
    "Quina": ["parasiten", "malaria", "infekt", "fieber"],
    "Houttuynia": ["viren", "bakterien", "infekt", "immunsystem"],
    "Mora": ["borreliose", "infekt", "bakterien", "lyme"],
    "Takuna": ["borreliose", "viren", "infekt", "immunsystem"],
    "Enula": ["borreliose", "parasiten", "bakterien", "infekt"],
    
    # Entgiftung
    "Burbur": ["entgiftung", "leber", "niere", "ausleitung", "drainage"],
    "Burbur-Pinella": ["entgiftung", "leber", "gehirn", "nerven", "ausleitung"],
    "Pinella": ["entgiftung", "gehirn", "nerven", "neurotoxine"],
    "Parsley": ["entgiftung", "niere", "blase", "harnwege", "ausleitung"],
    "Sparga": ["entgiftung", "lymphe", "drainage", "ausleitung"],
    "Sealantro": ["entgiftung", "schwermetalle", "ausleitung", "drainage"],
    "Binder Plus": ["entgiftung", "toxine", "darm", "ausleitung", "immunsystem"],
    
    # Verdauung
    "Chanca Piedra": ["verdauung", "leber", "galle", "niere", "steine"],
    "Dandelion": ["verdauung", "leber", "galle", "entgiftung"],
    "Stevia": ["verdauung", "darm", "candida", "pilze", "zucker"],
    "Algas": ["verdauung", "darm", "mineralien", "entgiftung"],
    
    # Immunsystem
    "Elderberry": ["immunsystem", "viren", "erkältung", "grippe"],
    "Zinc": ["immunsystem", "haut", "hormone", "stoffwechsel"],
    "Quercetin": ["immunsystem", "allergie", "entzündung", "antioxidans"],
    
    # Nerven & Psyche
    "Amantilla": ["nerven", "schlaf", "stress", "angst", "beruhigung"],
    "Babuna": ["nerven", "verdauung", "entzündung", "beruhigung"],
    "Relaxmedix": ["stress", "nerven", "entspannung", "schlaf"],
    "Moodmedix": ["psyche", "stimmung", "depression", "stress"],
    
    # Herz-Kreislauf
    "Magnesium Malate": ["herz", "muskeln", "energie", "nerven", "kreislauf"],
    "Resveratrol": ["herz", "kreislauf", "antioxidans", "gefäße"],
    "Nattokinase": ["herz", "kreislauf", "blut", "gefäße", "fibrin"],
    
    # Energie & Hormone
    "Adrenal": ["nebennieren", "stress", "energie", "hormone", "erschöpfung"],
    "Maca": ["hormone", "energie", "libido", "nebennieren"],
    "Vitalmedix": ["energie", "stoffwechsel", "vitalität"],
    
    # Entzündung
    "Bromelain": ["entzündung", "verdauung", "schwellung", "enzyme"],
    "Serra Peptase": ["entzündung", "fibrin", "schleim", "enzyme"],
    "Baikal Skullcap": ["entzündung", "allergie", "nerven", "beruhigung"],
    
    # Parasiten
    "Artemisia Annua": ["parasiten", "malaria", "würmer", "infekt"],
}

def extend_keywords():
    db_path = Path(__file__).parent.parent / "data" / "remedies.db"
    
    print(f"📂 Datenbank: {db_path}")
    print("=" * 70)
    print("🔧 KEYWORD-ERWEITERUNG FÜR PROFIL-INTEGRATION")
    print("=" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    total_added = 0
    
    # ========================================================================
    # HEEL KEYWORDS ERWEITERN
    # ========================================================================
    print("\n📋 HEEL Keywords erweitern...")
    heel_added = 0
    
    for remedy_name, keywords in HEEL_KEYWORD_MAP.items():
        # Finde Remedy in DB
        cursor.execute("""
            SELECT id FROM remedies 
            WHERE name LIKE ? AND category = 'homotoxikologie_heel'
        """, (f"%{remedy_name}%",))
        row = cursor.fetchone()
        
        if not row:
            # Versuche exakten Match
            cursor.execute("""
                SELECT id FROM remedies 
                WHERE name = ? AND category = 'homotoxikologie_heel'
            """, (remedy_name,))
            row = cursor.fetchone()
        
        if row:
            remedy_id = row[0]
            for kw in keywords:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO remedy_keywords (remedy_id, keyword, priority)
                        VALUES (?, ?, 8)
                    """, (remedy_id, kw.lower()))
                    if cursor.rowcount > 0:
                        heel_added += 1
                except:
                    pass
        else:
            print(f"   ⚠️  Nicht gefunden: {remedy_name}")
    
    print(f"   ✅ {heel_added} Heel-Keywords hinzugefügt")
    total_added += heel_added
    
    # ========================================================================
    # NUTRAMEDIX KEYWORDS ERWEITERN
    # ========================================================================
    print("\n📋 NUTRAMEDIX Keywords erweitern...")
    nutra_added = 0
    
    for remedy_name, keywords in NUTRAMEDIX_KEYWORD_MAP.items():
        # Finde Remedy in DB
        cursor.execute("""
            SELECT id FROM remedies 
            WHERE name LIKE ? AND category = 'phytotherapie_nutramedix'
        """, (f"%{remedy_name}%",))
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("""
                SELECT id FROM remedies 
                WHERE name = ? AND category = 'phytotherapie_nutramedix'
            """, (remedy_name,))
            row = cursor.fetchone()
        
        if row:
            remedy_id = row[0]
            for kw in keywords:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO remedy_keywords (remedy_id, keyword, priority)
                        VALUES (?, ?, 8)
                    """, (remedy_id, kw.lower()))
                    if cursor.rowcount > 0:
                        nutra_added += 1
                except:
                    pass
        else:
            print(f"   ⚠️  Nicht gefunden: {remedy_name}")
    
    print(f"   ✅ {nutra_added} Nutramedix-Keywords hinzugefügt")
    total_added += nutra_added
    
    conn.commit()
    
    # ========================================================================
    # STATISTIK
    # ========================================================================
    print("\n" + "=" * 70)
    print("📊 ERGEBNIS")
    print("=" * 70)
    print(f"   • Heel-Keywords hinzugefügt: {heel_added}")
    print(f"   • Nutramedix-Keywords hinzugefügt: {nutra_added}")
    print(f"   • GESAMT: {total_added}")
    
    # Test
    print("\n🔍 VERIFIKATION: Suche nach Profil-Keywords...")
    
    test_terms = ["bakterien", "viren", "parasiten", "entgiftung", "immunsystem", 
                  "herz", "nerven", "verdauung", "borreliose", "stress"]
    
    for term in test_terms:
        cursor.execute("""
            SELECT 
                (SELECT COUNT(DISTINCT r.id) FROM remedies r 
                 JOIN remedy_keywords rk ON r.id = rk.remedy_id 
                 WHERE r.category = 'homotoxikologie_heel' AND rk.keyword LIKE ?) as heel,
                (SELECT COUNT(DISTINCT r.id) FROM remedies r 
                 JOIN remedy_keywords rk ON r.id = rk.remedy_id 
                 WHERE r.category = 'phytotherapie_nutramedix' AND rk.keyword LIKE ?) as nutra
        """, (f"%{term}%", f"%{term}%"))
        heel, nutra = cursor.fetchone()
        
        heel_status = "✅" if heel > 0 else "❌"
        nutra_status = "✅" if nutra > 0 else "❌"
        print(f"   '{term:12s}': Heel {heel_status} ({heel:2d}) | Nutra {nutra_status} ({nutra:2d})")
    
    conn.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    extend_keywords()
