"""
Heel Deep Scan Extraktor
Sucht gezielt nach Einzelmitteln, Injeelen und Suis-Präparaten, die im ersten Pass übersehen wurden.
"""

import sys
from pathlib import Path
import re

try:
    import PyPDF2
except ImportError:
    print("❌ PyPDF2 fehlt. Bitte 'pip install PyPDF2' ausführen.")
    sys.exit(1)

def extract_deep(pdf_path, start_page, end_page, existing_file):
    print(f"\n🕵️ TIEFEN-SCAN S. {start_page}-{end_page}...")
    print("=" * 70)
    
    # Lade bereits bekannte Produkte
    existing_products = set()
    if Path(existing_file).exists():
        with open(existing_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    existing_products.add(line.lower()) # Case insensitive Vergleich
    print(f"📚 Ignoriere {len(existing_products)} bereits bekannte Produkte.")
    
    found_products = set()
    
    # Muster für Deep Scan
    patterns = [
        r'.*Injeel.*',       # Alles mit Injeel
        r'.*\ssuis.*',       # Alles mit suis (Organpräparate)
        r'^Acidum\s.*',      # Säuren
        r'^Calcium\s.*',     # Mineralien
        r'^Ferrum\s.*',
        r'^Kalium\s.*',
        r'^Natrium\s.*',
        r'^Magnesium\s.*',
        r'^Argentum\s.*',
        r'^Aurum\s.*',
        r'.*comp\..*',       # Abkürzungen für compositum
        r'.*forte.*',         # Stärken
        r'.*Homaccord.*'      # Falls welche fehlen
    ]
    
    # Ignore Liste (Störwörter)
    blacklist = [
        "DOSIERUNG", "ANWENDUNG", "NEBENWIRKUNGEN", "KONTRAINDIKATIONEN",
        "ZUSAMMENSETZUNG", "INDIKATION", "PACKUNGSGRÖSSE", "TROPFEN", "AMPULLEN",
        "TABLETTEN", "SIEHE", "BEACHTEN", "VERDÜNNUNG", "FLÜSSIGE", "INJEKTION",
        "REG.-NR", "HEEL", "BADEN-BADEN", "MISCHUNG", "AUFTRAGEN"
    ]

    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        
        for i in range(start_page, min(end_page + 1, len(reader.pages))):
            page = reader.pages[i]
            text = page.extract_text()
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Filter 1: Zu kurz/lang
                if len(line) < 5 or len(line) > 50:
                    continue
                    
                # Filter 2: Blacklist
                is_bad = False
                for bad in blacklist:
                    if bad in line.upper():
                        is_bad = True
                        break
                if is_bad:
                    continue
                
                # Filter 3: Muss Buchstaben enthalten
                if not re.search(r'[a-zA-Z]', line):
                    continue
                    
                # Filter 4: Prüfe auf Muster
                is_match = False
                for pattern in patterns:
                    if re.match(pattern, line, re.IGNORECASE):
                        is_match = True
                        break
                
                # Spezialfall: Mittelnamen starten meist Groß
                if not line[0].isupper():
                    is_match = False

                if is_match:
                    # Bereinigung: Entferne Klammern am Ende (oft Indikationen oder deutsche Namen)
                    # "Arnica (Bergwohlverleih)" -> "Arnica"
                    # Aber Vorsicht: "Graphites-Homaccord"
                    
                    # Wir nehmen die ganze Zeile als Kandidat, aber entfernen harte Artefakte
                    clean_name = line
                    
                    # Entferne führende "• " oder "- "
                    clean_name = re.sub(r'^[\•\-\*]\s*', '', clean_name)
                    
                    # Check Duplicate
                    if clean_name.lower() not in existing_products:
                        if clean_name not in found_products:
                            # print(f"  ✨ Gefunden: {clean_name}")
                            found_products.add(clean_name)

    # Sortieren und Speichern
    sorted_products = sorted(list(found_products))
    
    out_file = Path("heel_deep_scan.txt")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write("# Heel Deep Scan Ergebnisse\n")
        f.write(f"# Anzahl: {len(sorted_products)}\n\n")
        for p in sorted_products:
            f.write(f"{p}\n")
            
    print("\n" + "=" * 70)
    print(f"✅ Deep Scan fertig. {len(sorted_products)} NEUE Produkte gefunden.")
    print(f"💾 Gespeichert in: {out_file}")
    
    # Preview
    print("\nBeispiele:")
    for p in sorted_products[:10]:
        print(f"  🔹 {p}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_heel_deep.py <pdf_path> [start] [end]")
        sys.exit(1)
        
    pdf = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 360
    
    extract_deep(pdf, start, end, "heel_products_clean.txt")
