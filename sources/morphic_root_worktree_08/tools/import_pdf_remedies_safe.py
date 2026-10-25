"""
PDF-Remedy-Import Tool (Rechtssicher)

Importiert Remedy-Namen aus PDFs mit AI-generierten neutralen Beschreibungen.
Keine Urheberrechtsverletzung, keine Heilversprechen.

Verwendung:
    python import_pdf_remedies_safe.py --extract imports/Antihomotoxikologie.pdf
    python import_pdf_remedies_safe.py --import product_list.txt --category homotoxikologie_heel --manufacturer Heel
"""

import sys
from pathlib import Path
import re
import json
import time

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.remedy_service import add_remedy, get_remedy_stats, init_remedy_database, get_remedy_connection


# Prompt-Template für neutrale Beschreibungen
NEUTRAL_DESCRIPTION_PROMPT = """
Erstelle eine sehr kurze, neutrale Beschreibung für das Präparat "{label}" 
aus der Kategorie "{category}".

KONTEXT: Bioresonanz und energetische Betrachtung

STRIKTE REGELN:
1. KEINE medizinischen Aussagen
2. KEINE Heilversprechen  
3. KEINE Indikationen
4. KEINE Dosierungen
5. Nur energetische/symbolische Aspekte

VERWENDE NUR DIESE FORMULIERUNGEN:
- "Wird im Rahmen der Bioresonanz als..."
- "Kann als energetische Unterstützung bei..."
- "Die Resonanzanalyse zeigt Hinweise auf..."
- "Im bioenergetischen Kontext..."
- "Resonanzpunkt für..."

LÄNGE: Maximal 2-3 Sätze

BEISPIEL:
"Wird im Rahmen der Bioresonanz als energetische Unterstützung bei 
lymphatischen Themen betrachtet. Die Resonanzanalyse kann Hinweise 
auf energetische Zusammenhänge im Lymphsystem geben."

Beschreibung für {label}:
"""


def extract_product_names_from_pdf(pdf_path: Path, output_file: Path = None):
    """
    Extrahiert potenzielle Produktnamen aus PDF.
    
    WICHTIG: Dies ist nur eine Hilfe zur manuellen Überprüfung!
    Die extrahierten Namen müssen manuell validiert werden.
    """
    try:
        import PyPDF2
    except ImportError:
        print("❌ PyPDF2 nicht installiert. Bitte installieren: pip install PyPDF2")
        return []
    
    print(f"\n🔍 Extrahiere Produktnamen aus: {pdf_path.name}")
    print("=" * 70)
    
    products = set()
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Durchsuche erste 50 Seiten (oder weniger)
            max_pages = min(50, len(reader.pages))
            
            for page_num in range(max_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                # Einfache Heuristik: Wörter mit Großbuchstaben am Anfang
                # die nicht zu häufig vorkommen (wahrscheinlich Produktnamen)
                words = re.findall(r'\b[A-Z][a-z]+(?:-[A-Z][a-z]+)*\b', text)
                
                for word in words:
                    # Filter: Mindestens 4 Zeichen, nicht zu häufige Wörter
                    if len(word) >= 4 and word not in ['Seite', 'Kapitel', 'Abbildung', 'Tabelle']:
                        products.add(word)
            
            print(f"✅ {len(products)} potenzielle Produktnamen gefunden")
            print("\nBitte manuell überprüfen und in Datei speichern!")
            print("=" * 70)
            
            # Sortiere alphabetisch
            sorted_products = sorted(products)
            
            # Zeige erste 20
            print("\nErste 20 gefundene Namen:")
            for i, product in enumerate(sorted_products[:20], 1):
                print(f"  {i:2d}. {product}")
            
            if len(sorted_products) > 20:
                print(f"  ... und {len(sorted_products) - 20} weitere")
            
            # Speichere in Datei wenn gewünscht
            if output_file:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("# Extrahierte Produktnamen\n")
                    f.write("# Bitte manuell überprüfen und nicht-relevante entfernen!\n\n")
                    for product in sorted_products:
                        f.write(f"{product}\n")
                
                print(f"\n💾 Vollständige Liste gespeichert: {output_file}")
            
            return sorted_products
    
    except Exception as e:
        print(f"❌ Fehler beim Extrahieren: {e}")
        return []


def generate_neutral_description_ollama(label: str, category: str) -> str:
    """
    Generiert neutrale Beschreibung mit Ollama.
    
    Falls Ollama nicht verfügbar, gibt Fallback-Text zurück.
    """
    try:
        import requests
        
        prompt = NEUTRAL_DESCRIPTION_PROMPT.format(label=label, category=category)
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2:3b',
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            description = result.get('response', '').strip()
            
            # Bereinige Beschreibung
            description = description.replace('\n', ' ')
            description = re.sub(r'\s+', ' ', description)
            
            return description
        else:
            print(f"⚠️  Ollama-Fehler für '{label}', verwende Fallback")
            return get_fallback_description(label, category)
    
    except Exception as e:
        print(f"⚠️  Ollama nicht erreichbar für '{label}', verwende Fallback")
        return get_fallback_description(label, category)


def get_fallback_description(label: str, category: str) -> str:
    """Fallback-Beschreibung wenn Ollama nicht verfügbar."""
    return (
        f"Wird im Rahmen der Bioresonanz als energetischer Resonanzpunkt "
        f"im Kontext von {category} betrachtet. Die Resonanzanalyse kann "
        f"Hinweise auf energetische Zusammenhänge geben."
    )


def import_remedies_from_file(
    product_file: Path,
    category: str,
    manufacturer: str,
    source_pdf: str,
    use_ai: bool = True,
    dry_run: bool = False
):
    """
    Importiert Remedies aus Produktliste (TXT oder JSON).
    
    Args:
        product_file: Datei mit Produkten (TXT: Name pro Zeile, JSON: Liste von Objekten)
        category: Kategorie (z.B. 'homotoxikologie_heel')
        manufacturer: Hersteller (z.B. 'Heel')
        source_pdf: Quellen-PDF (z.B. 'Antihomotoxikologie.pdf')
        use_ai: AI-Beschreibungen generieren (True) oder Fallback (False)
        dry_run: Nur anzeigen, nicht importieren
    """
    print("\n" + "=" * 70)
    print("REMEDY-IMPORT (Rechtssicher & Intelligent)")
    print("=" * 70)
    print(f"Produktdatei: {product_file}")
    print(f"Kategorie:    {category}")
    print(f"Hersteller:   {manufacturer}")
    print(f"Quelle:       {source_pdf}")
    print(f"AI-Beschr.:   {'Ja' if use_ai else 'Nein (Fallback)'}")
    print(f"Modus:        {'DRY RUN (kein Import)' if dry_run else 'IMPORT'}")
    print("=" * 70)
    
    # Lade Produkte (TXT oder JSON)
    products = []
    is_json = str(product_file).lower().endswith('.json')
    
    try:
        if is_json:
            print("📂 Lade JSON-Format mit Logik-Daten...")
            with open(product_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if isinstance(item, dict):
                        products.append(item) # Erwarte {"label": "...", "internal_logic": {...}}
                    else:
                        products.append({"label": str(item)})
        else:
            print("📂 Lade TXT-Format (einfache Liste)...")
            with open(product_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        products.append({"label": line})
    except Exception as e:
        print(f"❌ Fehler beim Laden der Datei: {e}")
        return
    
    print(f"\n📋 {len(products)} Produkte gefunden")
    
    if not products:
        print("❌ Keine Produkte zum Importieren!")
        return
    
    # Initialisiere DB
    init_remedy_database()
    
    # Importiere jedes Produkt
    imported = 0
    skipped = 0
    
    for i, item in enumerate(products, 1):
        label = item['label']
        internal_logic = item.get('internal_logic', {})
        
        # Kontext für Anzeige
        has_logic = bool(internal_logic.get('index_indications'))
        logic_indicator = "🧠" if has_logic else "  "
        
        print(f"\n[{i}/{len(products)}] {label} {logic_indicator}")
        
        # Kontext für AI (aber NICHT für Output)
        ai_context_prompt = ""
        if internal_logic:
            comp = internal_logic.get('composition', '')
            indications = ", ".join(internal_logic.get('index_indications', []))
            # Wir hängen das temporär an, damit die AI es weiß
            # Aber der Prompt muss instruiert sein, es nicht auszuplaudern.
            # Da wir generate_neutral_description_ollama nicht ändern wollen, tricksen wir nicht am Prompt,
            # sondern lassen die AI auf Basis des Namens arbeiten (das ist sicherer).
            # ODER wir nutzen composition als Input für den Prompt?
            
            if has_logic:
                print(f"  💡 Logik-Kontext: {len(internal_logic.get('index_indications', []))} Indikationen bekannt")

        # Generiere Beschreibung
        description = ""
        if use_ai:
            print("  🤖 Generiere AI-Beschreibung...")
            # Wir könnten hier den Kontext nutzen, aber aus Sicherheitsgründen (keine Medical Claims)
            # lassen wir die AI lieber rein auf Basis des Namens und "Bioresonanz" halluzinieren.
            # Das ist sicherer, als ihr echte Indikationen zu geben, die sie dann versehentlich nennt.
            description = generate_neutral_description_ollama(label, category)
        else:
            description = get_fallback_description(label, category)
        
        # Zeige Beschreibung
        desc_preview = description[:80].replace('\n', ' ')
        print(f"  📝 {desc_preview}...")
        
        if not dry_run:
            try:
                # 1. Remedy anlegen (Basis-Daten)
                # Wir nutzen 'label' als Name und extrahieren Potenz, falls möglich
                # Keywords generieren wir aus dem Namen
                
                keywords = [label.lower()]
                # Zerlege Namen für mehr Keywords (z.B. "Traumeel S" -> "traumeel", "s")
                keywords.extend([w.lower() for w in re.split(r'[\s-]+', label) if len(w) > 2])
                
                remedy_id = add_remedy(
                    name=label,
                    potency="", # Keine Potenz bekannt (Kombipräparat)
                    category=category,
                    indication="", # Indikation bleibt leer (rechtssicher)
                    keywords=list(set(keywords)) # Deduplizieren
                )
                
                # 2. Beschreibung speichern (Direkt in DB, da Service keine Funktion dafür hat)
                # Das ist ein Workaround, da add_remedy() keine description akzeptiert.
                if description:
                    with get_remedy_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT OR REPLACE INTO remedy_descriptions (remedy_id, description)
                            VALUES (?, ?)
                        """, (remedy_id, description))
                        conn.commit()

                print("  ✅ Importiert")
                imported += 1
                
                # Kleine Pause bei AI-Generierung
                if use_ai:
                    time.sleep(0.5)
            
            except Exception as e:
                print(f"  ❌ Fehler: {e}")
                skipped += 1

        else:
            print("  ⏭️  Übersprungen (Dry Run)")
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("IMPORT ABGESCHLOSSEN")
    print("=" * 70)
    
    if not dry_run:
        print(f"✅ Importiert: {imported}")
        print(f"❌ Fehler:     {skipped}")
        
        # Zeige Statistik
        stats = get_remedy_stats()
        print(f"\n📊 Remedy-DB Gesamt: {stats.get('total', 0)} Einträge")
    else:
        print("ℹ️  DRY RUN - Keine Änderungen vorgenommen")
    
    print("=" * 70)


def main():
    """Hauptfunktion."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='PDF-Remedy-Import Tool (Rechtssicher)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:

  # 1. Produktnamen aus PDF extrahieren (zur manuellen Überprüfung)
  python import_pdf_remedies_safe.py --extract imports/Antihomotoxikologie.pdf --output heel_products.txt
  
  # 2. Produktliste importieren (mit AI-Beschreibungen)
  python import_pdf_remedies_safe.py --import heel_products.txt --category homotoxikologie_heel --manufacturer Heel --source Antihomotoxikologie.pdf
  
  # 3. Dry Run (nur anzeigen, nicht importieren)
  python import_pdf_remedies_safe.py --import heel_products.txt --category homotoxikologie_heel --manufacturer Heel --source Antihomotoxikologie.pdf --dry-run
  
  # 4. Import ohne AI (Fallback-Beschreibungen)
  python import_pdf_remedies_safe.py --import heel_products.txt --category homotoxikologie_heel --manufacturer Heel --source Antihomotoxikologie.pdf --no-ai
        """
    )
    
    parser.add_argument('--extract', type=Path, help='PDF-Datei zum Extrahieren von Produktnamen')
    parser.add_argument('--output', type=Path, help='Output-Datei für extrahierte Namen')
    parser.add_argument('--import', dest='import_file', type=Path, help='Produktliste zum Importieren')
    parser.add_argument('--category', help='Kategorie (z.B. homotoxikologie_heel)')
    parser.add_argument('--manufacturer', help='Hersteller (z.B. Heel)')
    parser.add_argument('--source', help='Quellen-PDF (z.B. Antihomotoxikologie.pdf)')
    parser.add_argument('--no-ai', action='store_true', help='Keine AI-Beschreibungen (Fallback)')
    parser.add_argument('--dry-run', action='store_true', help='Nur anzeigen, nicht importieren')
    
    args = parser.parse_args()
    
    # Modus 1: Extrahieren
    if args.extract:
        if not args.extract.exists():
            print(f"❌ PDF nicht gefunden: {args.extract}")
            sys.exit(1)
        
        output = args.output or Path(f"extracted_{args.extract.stem}.txt")
        extract_product_names_from_pdf(args.extract, output)
    
    # Modus 2: Importieren
    elif args.import_file:
        if not args.import_file.exists():
            print(f"❌ Produktliste nicht gefunden: {args.import_file}")
            sys.exit(1)
        
        if not args.category:
            print("❌ --category erforderlich!")
            sys.exit(1)
        
        if not args.manufacturer:
            print("❌ --manufacturer erforderlich!")
            sys.exit(1)
        
        if not args.source:
            print("❌ --source erforderlich!")
            sys.exit(1)
        
        import_remedies_from_file(
            product_file=args.import_file,
            category=args.category,
            manufacturer=args.manufacturer,
            source_pdf=args.source,
            use_ai=not args.no_ai,
            dry_run=args.dry_run
        )
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
