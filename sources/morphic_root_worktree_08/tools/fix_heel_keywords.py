"""
Bereinigt und re-injiziert Heel-Keywords.
1. Löscht alle alten Heel-Keywords (PDF-Artefakte)
2. Injiziert saubere Keywords aus heel_import_ready.json
"""

import sqlite3
import json
import re
from pathlib import Path

def clean_keyword(kw: str) -> str:
    """Bereinigt ein Keyword von PDF-Artefakten."""
    if not kw:
        return ""
    
    # Entferne eckige Klammern und deren Inhalt am Ende
    kw = re.sub(r'\]$', '', kw)
    kw = re.sub(r'^\[', '', kw)
    
    # Entferne runde Klammern am Anfang/Ende
    kw = re.sub(r'^\(', '', kw)
    kw = re.sub(r'\)$', '', kw)
    
    # Entferne Sonderzeichen
    kw = kw.replace(':', '').replace(';', '').replace(',', ' ')
    
    # Normalisiere Whitespace
    kw = ' '.join(kw.split())
    
    # Kleinschreibung
    kw = kw.lower().strip()
    
    return kw

def extract_keywords_from_text(text: str) -> list:
    """Extrahiert NUR medizinisch relevante Keywords aus einem Text."""
    if not text:
        return []
    
    # Bereinige den Text
    text = clean_keyword(text)
    
    # Splitte in Wörter
    words = text.split()
    
    # ERWEITERTE Stoppwörter - inkl. Pharma-Floskeln
    stopwords = {
        # Deutsche Stoppwörter
        'und', 'oder', 'der', 'die', 'das', 'bei', 'mit', 'von', 'zu', 'im', 'in', 'auf', 
        'für', 'als', 'auch', 'nach', 'durch', 'über', 'unter', 'vor', 'den', 'des', 'dem',
        'ein', 'eine', 'einer', 'einem', 'einen', 'eines', 'sich', 'sie', 'ihr', 'ihre',
        'ihren', 'ihrer', 'ihrem', 'sein', 'seine', 'seinen', 'seiner', 'seinem', 'sind',
        'wird', 'werden', 'wurde', 'wurden', 'hat', 'haben', 'hatte', 'hatten', 'kann',
        'können', 'konnte', 'konnten', 'soll', 'sollen', 'sollte', 'sollten', 'muss',
        'müssen', 'musste', 'mussten', 'darf', 'dürfen', 'durfte', 'durften', 'mag',
        'mögen', 'mochte', 'mochten', 'will', 'wollen', 'wollte', 'wollten', 'lassen',
        'nicht', 'nur', 'noch', 'schon', 'bereits', 'immer', 'wieder', 'sehr', 'mehr',
        'weniger', 'etwa', 'circa', 'ungefähr', 'fast', 'ganz', 'gar', 'völlig', 'total',
        'besonders', 'sowie', 'dazu', 'dabei', 'damit', 'dafür', 'dagegen', 'daher',
        'darum', 'darauf', 'darin', 'daraus', 'davon', 'davor', 'dazwischen',
        # Pharma-Floskeln
        'anwendungsgebiete', 'leiten', 'homöopathischen', 'arzneimittelbildern', 'gehören',
        'hinweis', 'anhaltenden', 'unklaren', 'auftretenden', 'beschwerden', 'sollten',
        'ihren', 'arzt', 'aufsuchen', 'tablette', 'enthält', 'arzneilich', 'wirksame',
        'bestandteile', 'sonstige', 'magnesiumstearat', 'gemeinsame', 'potenzierung',
        'stufen', 'verreibung', 'flüssige', 'verdünnung', 'ampulle', 'ampullen',
        'tropfen', 'injektionszwecke', 'natriumchlorid', 'ethanol', 'wasser', 'gereinigtes',
        'jeweils', 'über', 'letzten', 'letzte', 'stufe', 'bestandteil', 'bestandteilen',
        'compositum', 'homaccord', 'injeel', 'heel', 'coenzyme', 'cralonin',
        'auto-sanguis-stufentherapie', 'sekundärer', 'art', 'neu', 'neue', 'neuen',
        # Weitere Füllwörter
        'ursache', 'form', 'formen', 'typ', 'typen', 'fall', 'fälle', 'fällen',
        'beispiel', 'beispiele', 'teil', 'teile', 'teilen', 'art', 'arten',
        # Pharma-Hinweise und Müll
        'abklären', 'abklärung', 'index', 'u.a.', 'u.a', 'etc', 'bzw', 'ggf',
        'cave', 'hinweis', 'vorsicht', 'kontraindikation', 'kontraindikationen',
        'nebenwirkung', 'nebenwirkungen', 'wechselwirkung', 'wechselwirkungen',
        'dosierung', 'anwendung', 'einnahme', 'packungsbeilage', 'beipackzettel',
        'erschöpfungs-', 'schwächezuständen', 'neuro-injeel', 'glonoin-homaccord',
        'lymphomyosot', 'mehrere', 'kleine', 'mahlzeiten', 'pectanginöse',
    }
    
    keywords = []
    for word in words:
        # Mindestens 4 Zeichen, nicht in Stoppwörtern
        if len(word) >= 4 and word not in stopwords:
            # Keine reinen Zahlen oder Dosierungen
            if not re.match(r'^[\d.,]+$', word):
                if not re.match(r'^d\d+$', word):  # D4, D6, D12 etc.
                    # Keine Wörter mit Ausrufezeichen (Pharma-Warnungen)
                    if '!' not in word:
                        # Keine Wörter die mit Bindestrich enden (abgebrochene Wörter)
                        if not word.endswith('-'):
                            keywords.append(word)
    
    return list(set(keywords))

def fix_heel_keywords():
    db_path = Path(__file__).parent.parent / "data" / "remedies.db"
    json_path = Path(__file__).parent.parent / "heel_import_ready.json"
    
    print(f"📂 Datenbank: {db_path}")
    print(f"📂 JSON: {json_path}")
    print("=" * 70)
    
    # Lade JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        heel_data = json.load(f)
    
    print(f"📊 Heel-Mittel im JSON: {len(heel_data)}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Zähle alte Keywords
    cursor.execute("""
        SELECT COUNT(*) FROM remedy_keywords 
        WHERE remedy_id IN (SELECT id FROM remedies WHERE category = 'homotoxikologie_heel')
    """)
    old_count = cursor.fetchone()[0]
    print(f"📊 Alte Heel-Keywords: {old_count}")
    
    # 2. Lösche alte Keywords
    print("\n🗑️  Lösche alte Heel-Keywords...")
    cursor.execute("""
        DELETE FROM remedy_keywords 
        WHERE remedy_id IN (SELECT id FROM remedies WHERE category = 'homotoxikologie_heel')
    """)
    conn.commit()
    print(f"   ✅ {old_count} alte Keywords gelöscht")
    
    # 3. Injiziere neue Keywords
    print("\n💉 Injiziere neue Keywords...")
    
    total_keywords = 0
    updated_remedies = 0
    
    for item in heel_data:
        label = item.get('label', '')
        internal_logic = item.get('internal_logic', {})
        
        # Finde Remedy in DB
        cursor.execute("SELECT id FROM remedies WHERE name = ? AND category = 'homotoxikologie_heel'", (label,))
        row = cursor.fetchone()
        
        if not row:
            print(f"   ⚠️  Nicht gefunden: {label}")
            continue
        
        remedy_id = row[0]
        keywords = set()
        
        # 1. Keywords NUR aus index_indications (saubere medizinische Begriffe)
        for indication in internal_logic.get('index_indications', []):
            for kw in extract_keywords_from_text(indication):
                keywords.add(kw)
        
        # 2. Remedy-Name als Keyword (ohne Zusätze wie "N", "S", etc.)
        base_name = label.lower().replace(' n', '').replace(' s', '').strip()
        keywords.add(base_name)
        keywords.add(label.lower())
        
        # Injiziere Keywords
        for kw in keywords:
            if len(kw) >= 3:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO remedy_keywords (remedy_id, keyword, priority)
                        VALUES (?, ?, 5)
                    """, (remedy_id, kw, ))
                    total_keywords += 1
                except Exception as e:
                    pass
        
        updated_remedies += 1
    
    conn.commit()
    
    # 4. Finale Statistik
    cursor.execute("""
        SELECT COUNT(*) FROM remedy_keywords 
        WHERE remedy_id IN (SELECT id FROM remedies WHERE category = 'homotoxikologie_heel')
    """)
    new_count = cursor.fetchone()[0]
    
    print(f"\n" + "=" * 70)
    print(f"📊 ERGEBNIS:")
    print(f"   • Remedies aktualisiert: {updated_remedies}")
    print(f"   • Neue Keywords: {new_count}")
    print(f"   • Alte Keywords: {old_count} (gelöscht)")
    print("=" * 70)
    
    # 5. Test: Suche nach relevanten Keywords
    print("\n🔍 TEST: Suche nach relevanten Keywords...")
    
    test_terms = ["entzündung", "infektion", "schmerz", "ekzem", "grippe", "herz", "leber", "niere"]
    
    for term in test_terms:
        cursor.execute("""
            SELECT COUNT(DISTINCT r.id)
            FROM remedies r
            JOIN remedy_keywords rk ON r.id = rk.remedy_id
            WHERE r.category = 'homotoxikologie_heel'
            AND rk.keyword LIKE ?
        """, (f"%{term}%",))
        count = cursor.fetchone()[0]
        status = "✅" if count > 0 else "❌"
        print(f"   {status} '{term}': {count} Heel-Mittel")
    
    conn.close()

if __name__ == "__main__":
    fix_heel_keywords()
