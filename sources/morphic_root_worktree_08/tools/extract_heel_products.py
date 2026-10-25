"""
Heel-Produkt-Extraktor (Präzisions-Tool)

Analysiert das Antihomotoxikologie-PDF nach spezifischen Mustern für Kombinationspräparate.
Extrahiert Label, Zusammensetzung und Anwendungsgebiete (für interne Logik).
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
    """Bereinigt Text von Zeilenumbrüchen und überflüssigen Leerzeichen."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def extract_products(pdf_path, start_page, end_page):
    """
    Extrahiert Produkte basierend auf Layout-Mustern.
    
    Muster-Hypothese:
    - Produktname steht oft allein oder vor "• DARREICHUNGSFORM"
    - Gefolgt von "Zusammensetzung:"
    """
    print(f"\n🔍 Analysiere Seiten {start_page}-{end_page} in {pdf_path.name}")
    print("=" * 70)
    
    products = []
    current_product = None
    buffer_text = []
    
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
                
                # 1. ERKENNUNG NEUES PRODUKT
                # Starke Indikatoren: Zeile endet mit ® oder ist gefolgt von Darreichungsform
                # Im Fließtext oft schwer, daher suchen wir nach "Zusammensetzung:" als Anker
                # und schauen "nach oben".
                
                # Da PDF-Extraktion zeilenbasiert ist, puffern wir.
                buffer_text.append(line)
                
                # Wenn wir "Zusammensetzung:" finden, war das davor wahrscheinlich der Name
                if line.startswith("Zusammensetzung:") or "Zusammensetzung:" in line:
                    # Suche rückwärts nach möglichem Namen
                    # Meist 1-2 Zeilen über "Zusammensetzung" oder über "• TABLETTEN" etc.
                    
                    # Wir schließen das vorherige Produkt ab
                    if current_product:
                        products.append(current_product)
                    
                    # Versuche Namen zu finden
                    # Kandidat ist die Zeile(n) vor dem Block-Start
                    # Wir müssen schauen, wo der letzte "Block" (Zusammensetzung/Anwendung) aufgehört hat.
                    
                    # Simpler Ansatz für Prototyp:
                    # Suche in den letzten 5 Puffer-Zeilen nach Zeile mit ® oder Fettdruck-Indikator (schwer in plain text)
                    # Oder Zeile, die NICHTS mit dem vorherigen Text zu tun hat.
                    
                    # Hier nehmen wir an: Name steht 1-3 Zeilen über "Zusammensetzung"
                    # oder über der Darreichungsform (• TROPFEN)
                    
                    # Wir suchen im Puffer nach dem Start des neuen Produkts
                    # Das ist sehr heuristisch.
                    pass

    # ALTERNATIVER ANSATZ: Regex über den ganzen Seitentext
    # Das ist oft robuster bei PDFs.
    
    all_text = ""
    for i in range(start_page, min(end_page + 1, len(reader.pages))):
        page = reader.pages[i]
        all_text += page.extract_text() + "\n"
        
    # Wir suchen nach Blöcken.
    # Ein Block beginnt meist mit dem Namen, dann Darreichungsform, dann Zusammensetzung.
    
    # Muster:
    # Name (evtl. mit ®)
    # • DARREICHUNGSFORM (optional)
    # Zusammensetzung: ...
    
    # Wir splitten den Text anhand von "Zusammensetzung:" und schauen uns den Teil DAVOR an.
    parts = re.split(r'(Zusammensetzung:)', all_text)
    
    # part[0] ist Text vor dem ersten "Zusammensetzung:" -> Müll oder erstes Produkt-Start
    # part[1] ist "Zusammensetzung:"
    # part[2] ist Inhalt bis zum nächsten
    
    found_products = []
    
    # Wir iterieren in 2er Schritten (Separator + Content)
    # Aber parts[0] ist speziell.
    
    # Wir müssen den Namen aus dem ENDE des vorangehenden Teils extrahieren.
    
    for k in range(0, len(parts)-1, 2):
        pre_text = parts[k] # Text VOR "Zusammensetzung:"
        content = parts[k+2] if k+2 < len(parts) else "" # Text DANACH (bis zum nächsten Zusammensetzung)
        
        # Name extrahieren: Die letzten Zeilen von pre_text
        pre_lines = [l.strip() for l in pre_text.split('\n') if l.strip()]
        
        if not pre_lines:
            continue
            
        # Kandidat für Name: Letzte Zeile, die KEIN "•" ist und nicht "Tabletten" etc. heißt
        # Wir schauen uns die letzten 6 Zeilen an (erweitert)
        name_candidate = ""
        
        # Gehe rückwärts durch Zeilen
        for j in range(len(pre_lines)-1, max(-1, len(pre_lines)-7), -1):
            line = pre_lines[j]
            
            # Ignoriere Darreichungsformen und technische Infos
            skip_keywords = [
                "•", "TABLETTEN", "TROPFEN", "SALBE", "INJEKTIONSLÖSUNG", "AMPULLEN",
                "FLÜSSIGE", "VERDÜNNUNG", "ZUR", "INJEKTION", "ZUL.-NR", "MISCHUNG",
                "EINNAHME", "AUFTRAGEN", "BESTANDTEILE", "DARREICHUNGSFORM",
                "PACKUNGSGRÖSSEN", "HEEL", "BADEN-BADEN", "TROPFFLASCHEN", "PACKUNGEN",
                "DOSIERUNGSANLEITUNG", "ANWENDUNG", "GEGENANZEIGEN", "WARNHINWEISE",
                "NEBENWIRKUNGEN", "WECHSELWIRKUNGEN", "ART UND DAUER"
            ]
            
            is_skip = False
            for keyword in skip_keywords:
                if keyword in line.upper():
                    is_skip = True
                    break
            
            if is_skip:
                continue
                
            # Ignoriere zu lange Zeilen (wahrscheinlich Fließtext)
            if len(line) > 40:  # Strenger: Max 40 Zeichen für Produktnamen
                continue

            # Ignoriere Zeilen, die mit Punkt enden (Sätze, Symptome)
            if line.endswith('.'):
                continue

            # Ignoriere Zeilen mit Klammern am Ende (meist Einzelmittel mit deutschem Namen)
            # z.B. "Crataegus (Weißdorn)"
            if re.search(r'\([^\)]+\)$', line):
                continue

            # Ignoriere Zeilen, die nur aus Sonderzeichen/Zahlen bestehen
            if re.match(r'^[\d\.\s-]+$', line):
                continue
                
            # Das hier könnte der Name sein
            name_candidate = line
            break
            
        if name_candidate:
            # Bereinigung
            clean_name = name_candidate
            # Entferne ®
            clean_name = clean_name.replace('®', '').strip()
            
            # Entferne typische Suffixe am Ende, die Darreichungsform sind
            clean_name = re.sub(r'\s+(Ampullen|Tabletten|Tropfen|Salbe)$', '', clean_name, flags=re.IGNORECASE)
            
            # Korrigiere OCR-Fehler: Trenne S/N/N am Ende ab (z.B. CruroheelS -> Cruroheel S)
            # Aber nur wenn davor Kleinbuchstaben sind
            clean_name = re.sub(r'([a-z])([SN])$', r'\1 \2', clean_name)
            clean_name = re.sub(r'([a-z])(Injeel)$', r'\1 \2', clean_name)
            
            # Extrahiere Anwendungsgebiete aus content
            usage = ""
            usage_match = re.search(r'Anwendungsgebiete:(.*?)(?:Gegenanzeigen|Warnhinweise|Dosierung|Nebenwirkungen|Wechselwirkungen|$)', content, re.DOTALL)
            if usage_match:
                usage = clean_text(usage_match.group(1))
            
            # Extrahiere Zusammensetzung (direkt am Anfang von content)
            composition = ""
            comp_match = re.search(r'(.*?)(?:Sonstiger|Anwendungsgebiete|Gegenanzeigen)', content, re.DOTALL)
            if comp_match:
                composition = clean_text(comp_match.group(1))
            
            product = {
                "label": clean_name,
                "internal_logic": {
                    "usage": usage,
                    "composition": composition
                },
                "source_page": "unknown" # TODO: Mapping auf echte Seite
            }
            
            # Filter: Name muss kurz sein (kein ganzer Satz)
            # Filter: Name darf keine Darreichungsform sein (falls durchgerutscht)
            if len(clean_name) < 50 and len(clean_name) > 2:
                skip_final = False
                for keyword in skip_keywords:
                    if clean_name.upper() == keyword:
                        skip_final = True
                        break
                if not skip_final:
                    found_products.append(product)

    return found_products

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_heel_products.py <pdf_path> [start_page] [end_page]")
        sys.exit(1)
        
    pdf_path = Path(sys.argv[1])
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 170
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 180
    
    products = extract_products(pdf_path, start, end)
    
    print(f"\n✅ {len(products)} Produkte gefunden (Bereich {start}-{end})")
    print("-" * 70)
    
    for p in products:
        print(f"📦 LABEL: {p['label']}")
        # print(f"   LOGIK-IND: {p['internal_logic']['usage'][:100]}...")
        print("-" * 30)
        
    # Speichere als JSON für Inspektion
    out_file = Path("heel_products_debug.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Debug-Daten gespeichert in {out_file}")

    # Speichere als TXT für Import
    txt_file = Path("heel_products.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("# Automatisch extrahierte Heel-Produkte\n")
        f.write("# Bitte überprüfen!\n\n")
        # Deduplizierung durch Set
        seen_labels = set()
        for p in products:
            label = p['label']
            if label not in seen_labels:
                f.write(f"{label}\n")
                seen_labels.add(label)
    print(f"💾 Import-Liste gespeichert in {txt_file}")

if __name__ == "__main__":
    main()
