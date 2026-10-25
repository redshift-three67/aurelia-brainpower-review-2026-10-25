"""
Analysiert die Heel-Keywords in der Datenbank.
Prüft, warum Heel-Mittel nicht in Suchen gefunden werden.
"""

import sqlite3
from pathlib import Path

def analyze_heel():
    db_path = Path(__file__).parent.parent / "data" / "remedies.db"
    
    print(f"📂 Datenbank: {db_path}")
    print("=" * 70)
    print("🔍 HEEL KEYWORD-ANALYSE")
    print("=" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Anzahl Heel-Mittel
    cursor.execute("SELECT COUNT(*) FROM remedies WHERE category = 'homotoxikologie_heel'")
    heel_count = cursor.fetchone()[0]
    print(f"\n📊 Heel-Mittel in DB: {heel_count}")
    
    # 2. Anzahl Keywords für Heel
    cursor.execute("""
        SELECT COUNT(*) FROM remedy_keywords 
        WHERE remedy_id IN (SELECT id FROM remedies WHERE category = 'homotoxikologie_heel')
    """)
    heel_keywords = cursor.fetchone()[0]
    print(f"📊 Heel-Keywords: {heel_keywords}")
    print(f"📊 Keywords pro Mittel: {heel_keywords / heel_count:.1f}")
    
    # 3. Beispiel-Keywords für ein bekanntes Heel-Mittel
    print("\n" + "-" * 70)
    print("📋 BEISPIEL: Apis-Homaccord Keywords")
    print("-" * 70)
    
    cursor.execute("""
        SELECT rk.keyword, rk.priority
        FROM remedy_keywords rk
        JOIN remedies r ON rk.remedy_id = r.id
        WHERE r.name = 'Apis-Homaccord'
        ORDER BY rk.priority DESC
        LIMIT 20
    """)
    apis_keywords = cursor.fetchall()
    
    if apis_keywords:
        for kw, prio in apis_keywords:
            print(f"   [{prio}] {kw}")
    else:
        print("   ❌ KEINE KEYWORDS GEFUNDEN!")
    
    # 4. Prüfe, ob "bakterien" oder "viren" in Heel-Keywords vorkommt
    print("\n" + "-" * 70)
    print("📋 SUCHE NACH RELEVANTEN KEYWORDS")
    print("-" * 70)
    
    search_terms = ["bakterien", "viren", "entzündung", "infektion", "immunsystem", "schmerz"]
    
    for term in search_terms:
        cursor.execute("""
            SELECT COUNT(DISTINCT r.id)
            FROM remedies r
            JOIN remedy_keywords rk ON r.id = rk.remedy_id
            WHERE r.category = 'homotoxikologie_heel'
            AND rk.keyword LIKE ?
        """, (f"%{term}%",))
        count = cursor.fetchone()[0]
        
        # Zeige Beispiele
        cursor.execute("""
            SELECT DISTINCT r.name
            FROM remedies r
            JOIN remedy_keywords rk ON r.id = rk.remedy_id
            WHERE r.category = 'homotoxikologie_heel'
            AND rk.keyword LIKE ?
            LIMIT 3
        """, (f"%{term}%",))
        examples = [row[0] for row in cursor.fetchall()]
        
        status = "✅" if count > 0 else "❌"
        print(f"   {status} '{term}': {count} Heel-Mittel")
        if examples:
            print(f"      Beispiele: {', '.join(examples)}")
    
    # 5. Vergleich mit Nutramedix
    print("\n" + "-" * 70)
    print("📋 VERGLEICH: NUTRAMEDIX KEYWORDS")
    print("-" * 70)
    
    for term in search_terms:
        cursor.execute("""
            SELECT COUNT(DISTINCT r.id)
            FROM remedies r
            JOIN remedy_keywords rk ON r.id = rk.remedy_id
            WHERE r.category = 'phytotherapie_nutramedix'
            AND rk.keyword LIKE ?
        """, (f"%{term}%",))
        count = cursor.fetchone()[0]
        status = "✅" if count > 0 else "❌"
        print(f"   {status} '{term}': {count} Nutramedix-Mittel")
    
    print("\n" + "=" * 70)
    conn.close()

if __name__ == "__main__":
    analyze_heel()
