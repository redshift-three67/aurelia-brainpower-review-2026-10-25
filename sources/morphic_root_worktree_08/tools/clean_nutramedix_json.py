"""
Nutramedix Cleaner
Bereinigt die JSON-Datei von Artefakten und Fehlinterpretationen,
bevor sie importiert wird.
"""

import json
from pathlib import Path

def clean_json(input_file):
    print(f"\n🧹 BEREINIGE {input_file}...")
    print("=" * 70)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    clean_data = []
    deleted = []
    
    # Blacklist für Labels (exakte Matches oder Teilstrings)
    blacklist_labels = [
        "Supports Healthy",
        "Fibrinolytic Activity",
        "Curculation",
        "Glucose / Metabolic",
        "10.1142", # DOI
        "10.5897", # DOI
        "Doi:",    # DOI
        "Dietary Supplement",
        "Antioxidan T",
        "Hiv",
        "Gsh",
        "Unterstützung Für",
        "Gelenke Und Protein",
        "Aufs Paltung",
        "Gesunde Entzündungs",
        "Stressmanagement, Unter",
        "Mood / Emotional",
        "Energy/Vitality",
        "Gastrointestinal",
        "Detox / Antioxidant",
        "Minerals",
        "Immunsystem Und", # Neu
        "Entzündungsreaktionen", # Neu
        "Antioxidans", # Neu
        "Sund Heit", # Neu
        "Kardiovaskulärer Ge-", # Neu
        "Anzeige", # Neu
        "Absorption", # Vitamin C Absorption
        "Immunsupport", # Immunsupport Und Zink
        "Darmgesundheit",
        "Gelen Ke",
        "Proteinstoffwechsel",
        "Vitamin C -",
        "Entspannung /",
        "Ung Von", # Unterstützung Von
        "Stützung Der",
        "Mikrobielle Abwehr", # Das klingt fast legitim, aber ist meist Überschrift
        "Unterstützung Der Gelenke",
        "Antioxidative Unterstützung",
        "Reaktion",
        "Schlafunterstützung"
    ]
    
    # Mapping für Korrekturen (Label -> Neues Label oder Merge)
    corrections = {
        "Nattokinase": {
            "merge_indications_from": ["Fibrinolytic Activity &", "Curculation"]
        }
    }
    
    for item in data:
        label = item['label']
        
        # 1. Check Blacklist
        is_bad = False
        for bad in blacklist_labels:
            if bad.lower() in label.lower():
                is_bad = True
                deleted.append(label)
                break
        
        if is_bad:
            continue
            
        # 2. Spezielle Korrekturen
        if label == "Nattokinase":
            # Hier ist alles ok, Indikationen sind im JSON schon gut
            pass
            
        # 3. Generelle Filter
        if len(label) < 3:
            deleted.append(label)
            continue
            
        # Wenn wir hier sind, ist das Item gut
        clean_data.append(item)
        
    # Speichern
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)
        
    print(f"✅ {len(clean_data)} Produkte behalten.")
    print(f"🗑️  {len(deleted)} Produkte gelöscht:")
    for d in deleted:
        print(f"   - {d}")

if __name__ == "__main__":
    clean_json("nutramedix_import_ready.json")
