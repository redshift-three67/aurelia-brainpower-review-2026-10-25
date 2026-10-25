"""
Nutramedix Extraktor
Extrahiert Produkte, Beschreibungen und Indikationen aus dem Nutramedix-PDF.
Nutzt die klare Struktur (Name -> Anwendungsbereiche -> Eigenschaften).
"""

import sys
from pathlib import Path
import re
import json

try:
    import PyPDF2
except ImportError:
    print("❌ PyPDF2 fehlt. Bitte 'pip install PyPDF2' ausführen.")
    sys.exit(1)

def extract_nutramedix(pdf_path):
    print(f"\n🌿 NUTRAMEDIX EXTRAKTION (WHITELIST): {pdf_path}")
    print("=" * 70)
    
    # Offizielle Produktliste (aus Inhaltsverzeichnis)
    whitelist = [
        "ADRENAL", "ALGAS", "AMANTILLA", "ARTEMISIA ANNUA", "AVEA", "BABUNA", 
        "BAIKAL SKULLCAP", "BANDEROL", "BARBERRY", "BINDER PLUS", "BROMELAIN", 
        "BURBUR", "BURBUR-PINELLA", "BURBUR -PINELLA",  # BEIDE Schreibweisen!
        "CHANCA PIEDRA", "CONDURA", "CUMANDA", 
        "DANDELION", "DEEP OCEAN TRACE MINERALS", "ELDERBERRY", "ENULA", "EZOV", 
        "GLUCOMEDIX", "HOUTTUYNIA", "MACA", "MAGNESIUM MALATE", "MAPALO", 
        "MOODMEDIX", "MORA", "NATTOKINASE", "NUTRA-BBS", "NUTRA-BRL", "NUTRA-BRT", 
        "PARSLEY", "PINELLA", "QUERCETIN", "QUINA", "RELAXMEDIX", "RESVERATROL", 
        "SAMENTO", "SEALANTRO", "SERRA PEPTASE", "SPARGA", "STEVIA", "TAKUNA", 
        "TANGARANA", "TEASEL", "VITALMEDIX", "ZINC"
    ]
    
    # Alias-Mapping für schwierige Fälle (basierend auf PDF-Debug)
    aliases = {
        "BURBUR-PINELLA": ["BURBUR -PINELLA", "BURBUR PINELLA"],  # Leerzeichen vor Bindestrich!
        "NUTRA-BBS": ["NUTRA -BBS", "NUTRA BBS"],  # Leerzeichen vor Bindestrich!
        "NUTRA-BRL": ["NUTRA -BRL", "NUTRA BRL"],  # Leerzeichen vor Bindestrich!
        "NUTRA-BRT": ["NUTRA -BRT", "NUTRA BRT"],  # Leerzeichen vor Bindestrich!
        "SERRA PEPTASE": ["SERRAPEPTASE", "SERRA  PEPTASE", "SERRA - PEPTASE"]  # Zusammen oder mit 2 Leerzeichen!
    }
    
    products = []
    current_product = None
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Check auf Whitelist (Case Insensitive)
                # Wir suchen nach Zeilen, die fast exakt einem Namen entsprechen
                upper_line = line.upper()
                
                matched_name = None
                
                # 1. Standard Whitelist Check
                for name in whitelist:
                    if len(upper_line) < 60:
                        # Exakter Match
                        if name == upper_line:
                            matched_name = name
                            break
                        
                        # Starts with (z.B. "SAMENTO TROPFEN")
                        if upper_line.startswith(name + " ") or upper_line.startswith(name + "-") or upper_line.endswith(" " + name):
                             matched_name = name
                             break
                             
                        # Enthalten, aber als Wort (Regex)
                        if re.search(r'\b' + re.escape(name) + r'\b', upper_line):
                            if len(upper_line) < len(name) + 20:
                                matched_name = name
                                break
                
                # 2. Alias Check (falls noch kein Match)
                if not matched_name:
                    for official_name, alias_list in aliases.items():
                        for alias in alias_list:
                            # Case-insensitive Alias-Check (längere Zeilen erlaubt wegen Copyright-Text)
                            if alias.upper() in upper_line and len(upper_line) < 80:
                                matched_name = official_name
                                break
                        if matched_name: break
                    
                if matched_name:
                    # Debug
                    # print(f"  🎯 Treffer: {matched_name} in '{line}'")
                    
                    # Wenn wir einen neuen Namen finden, schließen wir den alten ab
                    if current_product:
                        # Nur speichern, wenn wir auch Indikationen gefunden haben (sonst war es nur ein Inhaltsverzeichnis-Eintrag)
                        if len(current_product['indications']) > 0 or len(current_product['raw_text']) > 100:
                            products.append(current_product)
                    
                    # Neuen starten
                    current_product = {
                        "label": matched_name.title(), # "Adrenal"
                        "raw_text": "",
                        "indications": [],
                        "category": "phytotherapie_nutramedix"
                    }
                    # print(f"  Gefunden: {matched_name}")
                    continue
                    
                if current_product:
                    current_product["raw_text"] += line + " "
                    
                    # Indikationen sammeln (Listenpunkte)
                    if line.startswith("•") or line.startswith("-"):
                        content = line[1:].strip()
                        if len(content) > 3:
                            current_product["indications"].append(content)

    # Letztes Produkt
    if current_product:
        products.append(current_product)

    # Deduplizierung (falls Namen im Inhaltsverzeichnis und auf Seite auftauchten)
    # Wir behalten den Eintrag mit dem meisten Text/Indikationen
    final_map = {}
    
    # Normalisierungs-Mapping (PDF-Schreibweise -> Offizieller Name)
    name_normalization = {
        "BURBUR -PINELLA": "BURBUR-PINELLA",  # Leerzeichen entfernen
        "NUTRA -BBS": "NUTRA-BBS",
        "NUTRA -BRL": "NUTRA-BRL",
        "NUTRA -BRT": "NUTRA-BRT",
        "SERRAPEPTASE": "SERRA PEPTASE",
        "SERRA  PEPTASE": "SERRA PEPTASE"
    }
    
    for p in products:
        name = p['label'].upper()
        
        # Normalisiere den Namen
        if name in name_normalization:
            normalized_name = name_normalization[name].title()
        else:
            normalized_name = p['label']
            
        if normalized_name not in final_map:
            p['label'] = normalized_name  # Update label
            final_map[normalized_name] = p
        else:
            # Wenn der neue Eintrag mehr Indikationen hat, nimm ihn
            if len(p['indications']) > len(final_map[normalized_name]['indications']):
                p['label'] = normalized_name
                final_map[normalized_name] = p
                
    final_products_list = []
    for p in final_map.values():
        # Generiere Beschreibung
        desc_match = re.search(r'(?:ist|enthält).*?(?:\.|Extrakt)', p['raw_text'], re.IGNORECASE)
        base_desc = desc_match.group(0) if desc_match else "Pflanzliches Präparat von Nutramedix"
        
        # Bereinige Beschreibung (falls zu lang)
        if len(base_desc) > 200: base_desc = base_desc[:200] + "..."
        
        entry = {
            "label": p['label'],
            "category": "phytotherapie_nutramedix",
            "manufacturer": "Nutramedix",
            "source_ref": "NUTRAMEDIX-Kompakt.pdf",
            "internal_logic": {
                "index_indications": p['indications'],
                "base_description": base_desc
            }
        }
        final_products_list.append(entry)
        
    # Sortieren nach Name
    final_products_list.sort(key=lambda x: x['label'])

    print(f"✅ {len(final_products_list)} Produkte (Whitelist) extrahiert.")
    
    out_file = Path("nutramedix_import_ready.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(final_products_list, f, indent=2, ensure_ascii=False)
        
    print(f"💾 Gespeichert in: {out_file}")
    
    # Missing Check
    found_names = [p['label'].upper() for p in final_products_list]
    missing = [w for w in whitelist if w not in found_names]
    if missing:
        print(f"⚠️  Nicht gefunden ({len(missing)}): {', '.join(missing)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_nutramedix.py <pdf_path>")
        sys.exit(1)
        
    extract_nutramedix(sys.argv[1])
