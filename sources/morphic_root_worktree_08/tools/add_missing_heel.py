"""
Fügt wichtige fehlende Heel-Mittel zur Datenbank hinzu.
Diese Mittel wurden beim PDF-Import nicht erfasst.
"""

import sqlite3
from pathlib import Path

# Wichtige Heel-Mittel die fehlen
MISSING_HEEL_REMEDIES = [
    # (Name, Indikation, Keywords)
    ("Gripp-Heel", "Grippale Infekte, Erkältungskrankheiten", 
     ["grippe", "infekt", "erkältung", "fieber", "viren", "immunsystem", "atemwege"]),
    
    ("Nervoheel N", "Nervöse Störungen, Schlafstörungen, Unruhe",
     ["nerven", "schlaf", "unruhe", "angst", "stress", "psyche", "beruhigung"]),
    
    ("Neurexan", "Nervöse Unruhe, Schlafstörungen",
     ["nerven", "schlaf", "unruhe", "stress", "angst", "beruhigung"]),
    
    ("Valerianaheel", "Schlafstörungen, nervöse Unruhe",
     ["schlaf", "nerven", "unruhe", "beruhigung", "stress"]),
    
    ("Hepeel N", "Leberfunktionsstörungen, Hepatopathien",
     ["leber", "entgiftung", "hepatopathie", "stoffwechsel", "galle"]),
    
    ("Duodenoheel", "Duodenitis, Verdauungsstörungen",
     ["verdauung", "darm", "duodenum", "magen", "gastritis"]),
    
    ("Diarrheel SN", "Durchfallerkrankungen",
     ["darm", "durchfall", "verdauung", "diarrhoe", "magen"]),
    
    ("Aurumheel N", "Herz-Kreislauf-Störungen, depressive Verstimmungen",
     ["herz", "kreislauf", "depression", "psyche", "blutdruck"]),
    
    ("Bronchalis-Heel", "Bronchitis, Atemwegserkrankungen",
     ["atemwege", "bronchien", "husten", "lunge", "erkältung"]),
    
    ("Tartephedreel N", "Bronchitis mit Verschleimung",
     ["atemwege", "bronchien", "husten", "schleim", "lunge"]),
    
    ("Schwef-Heel", "Hauterkrankungen, Ekzeme",
     ["haut", "ekzem", "allergie", "juckreiz", "dermatose"]),
    
    ("Hormeel SN", "Hormonelle Störungen, Zyklusstörungen",
     ["hormone", "zyklus", "wechseljahre", "menstruation", "frauenleiden"]),
    
    ("Gynäcoheel N", "Frauenleiden, Zyklusstörungen",
     ["hormone", "zyklus", "frauenleiden", "menstruation", "wechseljahre"]),
    
    ("Galium-Heel N", "Entgiftung, Drainage, zelluläre Ausleitung",
     ["entgiftung", "drainage", "ausleitung", "zellular", "lymphe"]),
    
    ("Rhus toxicodendron-Injeel", "Gelenkschmerzen, Rheuma",
     ["gelenke", "rheuma", "schmerz", "bewegung", "arthrose"]),
    
    # Weitere wichtige Mittel
    ("Apis-Homaccord", "Ödeme, Entzündungen, allergische Reaktionen",
     ["ödem", "entzündung", "allergie", "schwellung", "insektenstich"]),
    
    ("Belladonna-Homaccord", "Fieber, Entzündungen, Schmerzen",
     ["fieber", "entzündung", "schmerz", "infekt", "kopfschmerz"]),
    
    ("Spascupreel", "Krämpfe, Koliken, Spasmen",
     ["krampf", "kolik", "spasmus", "magen", "darm", "schmerz"]),
    
    ("Vertigoheel", "Schwindel, Übelkeit",
     ["schwindel", "übelkeit", "gleichgewicht", "kreislauf"]),
    
    ("Viburcol N", "Unruhe bei Kindern, Zahnungsbeschwerden",
     ["kinder", "unruhe", "zahnung", "fieber", "beruhigung"]),
]

def add_missing_heel():
    db_path = Path(__file__).parent.parent / "data" / "remedies.db"
    
    print(f"📂 Datenbank: {db_path}")
    print("=" * 70)
    print("🔧 FEHLENDE HEEL-MITTEL HINZUFÜGEN")
    print("=" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    added_remedies = 0
    added_keywords = 0
    
    for name, indication, keywords in MISSING_HEEL_REMEDIES:
        # Prüfe ob schon vorhanden
        cursor.execute("""
            SELECT id FROM remedies 
            WHERE name = ? AND category = 'homotoxikologie_heel'
        """, (name,))
        
        if cursor.fetchone():
            print(f"   ⏭️  Bereits vorhanden: {name}")
            continue
        
        # Füge Remedy hinzu
        cursor.execute("""
            INSERT INTO remedies (name, potency, category, indication)
            VALUES (?, '', 'homotoxikologie_heel', ?)
        """, (name, indication))
        
        remedy_id = cursor.lastrowid
        added_remedies += 1
        print(f"   ✅ Hinzugefügt: {name}")
        
        # Füge Keywords hinzu
        for kw in keywords:
            cursor.execute("""
                INSERT OR IGNORE INTO remedy_keywords (remedy_id, keyword, priority)
                VALUES (?, ?, 8)
            """, (remedy_id, kw.lower()))
            if cursor.rowcount > 0:
                added_keywords += 1
        
        # Auch Name als Keyword
        cursor.execute("""
            INSERT OR IGNORE INTO remedy_keywords (remedy_id, keyword, priority)
            VALUES (?, ?, 8)
        """, (remedy_id, name.lower()))
    
    conn.commit()
    
    print("\n" + "=" * 70)
    print("📊 ERGEBNIS")
    print("=" * 70)
    print(f"   • Remedies hinzugefügt: {added_remedies}")
    print(f"   • Keywords hinzugefügt: {added_keywords}")
    
    # Statistik
    cursor.execute("""
        SELECT COUNT(*) FROM remedies WHERE category = 'homotoxikologie_heel'
    """)
    total = cursor.fetchone()[0]
    print(f"\n   📊 Heel-Mittel gesamt: {total}")
    
    conn.close()
    print("=" * 70)

if __name__ == "__main__":
    add_missing_heel()
