"""
Bereinigt die Nutramedix-Einträge in der Datenbank.
Behält nur die 48 offiziellen Mittel laut PDF.
"""

import sqlite3
from pathlib import Path

# Die 48 offiziellen Nutramedix-Mittel (exakt wie im PDF)
OFFICIAL_NUTRAMEDIX = [
    "Adrenal",
    "Algas",
    "Amantilla",
    "Artemisia Annua",
    "Avea",
    "Babuna",
    "Baikal Skullcap",
    "Banderol",
    "Barberry",
    "Binder Plus",
    "Bromelain",
    "Burbur",
    "Burbur-Pinella",
    "Chanca Piedra",
    "Condura",
    "Cumanda",
    "Dandelion",
    "Deep Ocean Trace Minerals",
    "Elderberry",
    "Enula",
    "Ezov",
    "Glucomedix",  # Auch GlucoMedix
    "Houttuynia",
    "Maca",
    "Magnesium Malate",
    "Mapalo",
    "Moodmedix",  # Auch MoodMedix
    "Mora",
    "Nattokinase",
    "Nutra-Bbs",  # Auch Nutra-BBS
    "Nutra-Brl",  # Auch Nutra-BRL
    "Nutra-Brt",  # Auch Nutra-BRT
    "Parsley",
    "Pinella",
    "Quercetin",
    "Quina",
    "Relaxmedix",
    "Resveratrol",
    "Samento",
    "Sealantro",
    "Serra Peptase",
    "Sparga",
    "Stevia",
    "Takuna",
    "Tangarana",
    "Teasel",
    "Vitalmedix",
    "Zinc"
]

def cleanup_nutramedix():
    db_path = Path(__file__).parent.parent / "data" / "remedies.db"
    
    print(f"📂 Datenbank: {db_path}")
    print("=" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Hole alle aktuellen Nutramedix-Einträge
    cursor.execute("""
        SELECT id, name FROM remedies 
        WHERE category = 'phytotherapie_nutramedix'
        ORDER BY name
    """)
    current_entries = cursor.fetchall()
    
    print(f"📊 Aktuelle Nutramedix-Einträge: {len(current_entries)}")
    print(f"📊 Offizielle Nutramedix-Mittel: {len(OFFICIAL_NUTRAMEDIX)}")
    print()
    
    # Erstelle normalisierte Liste für Vergleich
    official_lower = [name.lower() for name in OFFICIAL_NUTRAMEDIX]
    
    # Finde zu löschende Einträge
    to_delete = []
    to_keep = []
    
    for remedy_id, name in current_entries:
        name_lower = name.lower()
        
        # Prüfe ob der Name in der offiziellen Liste ist
        is_official = False
        for official in official_lower:
            # Exakter Match oder ähnlich genug
            if name_lower == official or name_lower.replace("-", "").replace(" ", "") == official.replace("-", "").replace(" ", ""):
                is_official = True
                break
        
        if is_official:
            to_keep.append((remedy_id, name))
        else:
            to_delete.append((remedy_id, name))
    
    print(f"✅ Behalten: {len(to_keep)}")
    print(f"❌ Löschen: {len(to_delete)}")
    print()
    
    if to_delete:
        print("🗑️  ZU LÖSCHENDE EINTRÄGE:")
        for remedy_id, name in to_delete:
            print(f"   • [{remedy_id}] {name}")
        print()
        
        # Lösche die Einträge
        for remedy_id, name in to_delete:
            # Lösche Keywords zuerst
            cursor.execute("DELETE FROM remedy_keywords WHERE remedy_id = ?", (remedy_id,))
            # Lösche Beschreibungen
            cursor.execute("DELETE FROM remedy_descriptions WHERE remedy_id = ?", (remedy_id,))
            # Lösche Remedy
            cursor.execute("DELETE FROM remedies WHERE id = ?", (remedy_id,))
            print(f"   ✅ Gelöscht: {name}")
        
        conn.commit()
        print()
        print(f"✅ {len(to_delete)} Einträge gelöscht!")
    else:
        print("✅ Keine Einträge zu löschen.")
    
    # Finale Statistik
    cursor.execute("SELECT COUNT(*) FROM remedies WHERE category = 'phytotherapie_nutramedix'")
    final_count = cursor.fetchone()[0]
    print()
    print("=" * 70)
    print(f"📊 FINALE NUTRAMEDIX-ANZAHL: {final_count}")
    print("=" * 70)
    
    conn.close()

if __name__ == "__main__":
    cleanup_nutramedix()
