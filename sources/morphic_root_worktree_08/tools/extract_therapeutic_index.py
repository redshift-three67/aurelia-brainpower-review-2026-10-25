"""
Heel Therapeutischer Index Extraktor
Extrahiert die Zuordnung von Indikationen (Symptomen) zu Mitteln aus dem PDF (ab S. 49).

Zielstruktur:
{
  "Angstzustände": [
    {"name": "Gelsemium-Homaccord", "context": "Kopfschmerzen, Neuralgien"},
    {"name": "Ignatia-Homaccord", "context": "Weinerlichkeit"}
  ],
  "Aphthen": [...]
}
"""

import sys
from pathlib import Path
import re
import json

# Versuch, PyPDF2 zu importieren
try:
    import PyPDF2
except ImportError:
    print("❌ PyPDF2 fehlt. Bitte 'pip install PyPDF2' ausführen.")
    sys.exit(1)

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_index(pdf_path, start_page, end_page):
    print(f"\n🧠 Analysiere Therapeutischen Index S. {start_page}-{end_page}...")
    print("=" * 70)
    
    index_data = {}
    current_indication = "Unbekannt"
    
    # Keywords, die Struktur anzeigen (keine Indikationen oder Mittel)
    structure_keywords = [
        "BASISTHERAPIE", "ORALE THERAPIE", "PARENTERALE THERAPIE",
        "BEGLEITTHERAPIE", "WEITERE VERFAHREN", "NEURALTHERAPIE",
        "AUSLEITENDE THERAPIE", "PHYSIKALISCHE THERAPIE", "DIFFERENTIALDIAGNOSE",
        "INTERMEDIÄRE KATALYSATOREN", "NOSODEN", "SUIS-ORGANPRÄPARATE",
        "PÄDIATRIE", "DOSIERUNG", "HINWEIS", "BESONDERE HINWEISE"
    ]
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        
        for i in range(start_page, min(end_page + 1, len(reader.pages))):
            page = reader.pages[i]
            text = page.extract_text()
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 1. PRÜFUNG: Ist es eine Struktur-Überschrift?
                is_structure = False
                for kw in structure_keywords:
                    if kw in line.upper():
                        is_structure = True
                        break
                if is_structure:
                    continue

                # 2. PRÜFUNG: Ist es eine NEUE Indikation (Symptom)?
                # Heuristik: Kurze Zeile, beginnt mit Großbuchstaben, keine Klammern am Anfang
                # Und: Das ist der schwierigste Teil. Wir nehmen an, Indikationen stehen allein.
                if (len(line) < 40 and 
                    not line.endswith('.') and 
                    not re.search(r'\d', line) and # Keine Zahlen
                    not re.search(r'\(|\[', line) and # Keine Klammern (Mittel haben oft Klammern)
                    not line.startswith('•') and
                    len(line) > 3):
                    
                    current_indication = line
                    if current_indication not in index_data:
                        index_data[current_indication] = []
                    # print(f"  👉 Neue Indikation: {current_indication}")
                    continue

                # 3. PRÜFUNG: Ist es ein Mittel?
                # Mittel haben oft Format: "Name (Darreichung) [Indikation]"
                # Oder einfach "Name"
                
                if current_indication != "Unbekannt":
                    # Suche nach Mittelnamen am Zeilenanfang
                    # Regex: Alles bis zur ersten Klammer ( oder [
                    match = re.match(r'^([A-Za-zÄÖÜäöü][A-Za-zÄÖÜäöü0-9\s-]+?)(\s*\(|\s*\[|$)', line)
                    
                    if match:
                        raw_name = match.group(1).strip()
                        
                        # Filter: Name muss valide aussehen
                        if len(raw_name) > 3 and raw_name.upper() not in structure_keywords:
                            
                            # Kontext extrahieren (alles in eckigen Klammern)
                            context_match = re.search(r'\[(.*?)\]', line)
                            context = context_match.group(1) if context_match else ""
                            
                            # Speichern
                            # Wir speichern nur, wenn es noch nicht existiert für diese Indikation
                            entry = {"name": raw_name, "context": context}
                            
                            # Check auf Dubletten in der Liste
                            exists = False
                            for e in index_data[current_indication]:
                                if e["name"] == raw_name:
                                    exists = True
                                    break
                            
                            if not exists:
                                index_data[current_indication].append(entry)

    return index_data

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_therapeutic_index.py <pdf_path> [start_page] [end_page]")
        sys.exit(1)
        
    pdf_path = Path(sys.argv[1])
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 49
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 55
    
    data = extract_index(pdf_path, start, end)
    
    print(f"\n✅ Analyse abgeschlossen. {len(data)} Indikationen gefunden.")
    print("-" * 70)
    
    # Zeige Beispiele
    count = 0
    for ind, remedies in data.items():
        if count > 10: break
        if len(remedies) > 0:
            print(f"🏥 {ind}:")
            for r in remedies[:3]: # Zeige max 3 Mittel pro Indikation
                print(f"   💊 {r['name']} ({r['context']})")
            if len(remedies) > 3:
                print(f"   ... ({len(remedies)-3} weitere)")
            print("-" * 30)
            count += 1
            
    # JSON speichern
    out_file = Path("heel_index_debug.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Daten gespeichert in {out_file}")

if __name__ == "__main__":
    main()
