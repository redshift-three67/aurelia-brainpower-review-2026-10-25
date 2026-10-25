"""
Logic Injector
Injiziert die Hidden Logic (Indikationen aus dem PDF-Index) als Keywords in die Datenbank.
Damit werden Mittel wie 'Traumeel' auch bei Suche nach 'Entzündung' gefunden.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.remedy_service import get_remedy_connection

def inject_logic(json_file):
    print(f"\n💉 INJIZIERE LOGIK AUS {json_file}...")
    print("=" * 70)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    conn = get_remedy_connection()
    # Context manager liefert connection, wir müssen manuell schließen oder with nutzen
    # Aber get_remedy_connection ist ein contextmanager, also:
    
    updated_count = 0
    keyword_count = 0
    
    with get_remedy_connection() as conn:
        cursor = conn.cursor()
        
        for item in data:
            label = item.get('label')
            logic = item.get('internal_logic', {})
            indications = logic.get('index_indications', [])
            
            if not label or not indications:
                continue
                
            # 1. Finde Remedy ID
            cursor.execute("SELECT id FROM remedies WHERE name = ?", (label,))
            row = cursor.fetchone()
            
            if not row:
                # Versuche Fuzzy Match (z.B. ohne "N" am Ende)
                cursor.execute("SELECT id FROM remedies WHERE name LIKE ?", (f"{label}%",))
                row = cursor.fetchone()
            
            if row:
                remedy_id = row[0]
                # print(f"  Verarbeite {label} (ID: {remedy_id})...")
                
                # 2. Injiziere Keywords
                local_keywords = 0
                for ind in indications:
                    # Reinige Indikation (z.B. "Entzündungen (akut)" -> "entzündungen")
                    # Wir speichern sowohl den vollen Begriff als auch Einzelwörter
                    
                    keywords_to_add = [ind.lower()]
                    
                    # Splitte komplexe Indikationen
                    # "Angina tonsillaris" -> "angina", "tonsillaris"
                    parts = ind.split()
                    if len(parts) > 1:
                        keywords_to_add.extend([p.lower().strip('(),.') for p in parts if len(p) > 3])
                    
                    for kw in keywords_to_add:
                        if len(kw) < 3: continue
                        
                        try:
                            cursor.execute("""
                                INSERT OR IGNORE INTO remedy_keywords (remedy_id, keyword, priority)
                                VALUES (?, ?, ?)
                            """, (remedy_id, kw, 5)) # Priorität 5 für Index-Begriffe
                            if cursor.rowcount > 0:
                                keyword_count += 1
                                local_keywords += 1
                        except Exception:
                            pass
                            
                if local_keywords > 0:
                    updated_count += 1
            else:
                # print(f"⚠️  Mittel nicht in DB gefunden: {label}")
                pass
                
        conn.commit()
        
    print("-" * 70)
    print(f"✅ Fertig! {updated_count} Mittel aktualisiert.")
    print(f"💉 {keyword_count} neue Keywords injiziert.")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inject_hidden_logic.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    inject_logic(json_file)
