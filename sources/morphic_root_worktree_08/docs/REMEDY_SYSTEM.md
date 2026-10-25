# 🌿 Remedy-System - Morphic Engine V1

## Übersicht

Das Remedy-System verwaltet **6979 Datensätze** für kohärente Harmonisierung:
- **1333 Remedies** (Kohärente Harmonisierung mit...)
- **1273 Pathogene** (Kohärente Harmonisierung von...)
- **4373 Multiplex-Links** (Pathogen → Remedy Zuordnungen)

---

## 🚀 Quick Start

### Statistiken anzeigen
```bash
python services/remedy_service.py
```

### Beispiel-Verknüpfungen anzeigen
```bash
python tools/link_pathogens_remedies.py --examples
```

---

## 📊 Datenbank-Struktur

### Tabelle: `remedies`
**Format:** "Kohärente Harmonisierung mit [Name]"

**Beispiele:**
- Kohärente Harmonisierung mit Arnica C200
- Kohärente Harmonisierung mit Echinacea D6
- Kohärente Harmonisierung mit California Flower Essence: Aloe Vera

**Kategorien:**
- Homöopathische Mittel (172)
- Nosoden (311)
- Schüssler-Salze (137)
- Bachblüten (38)
- Essenzen (Alaska, California, Himalaya, etc.)
- Aromatherapie, Kräuter, Tinkturen, etc.

### Tabelle: `pathogens`
**Format:** "Kohärente Harmonisierung von [Name]"

**Beispiele:**
- Kohärente Harmonisierung von Staphylococcus aureus
- Kohärente Harmonisierung von Candida albicans
- Kohärente Harmonisierung von Herpes-simplex-Viren

**Typen:**
- Pilze: 382
- Bakterien: 306
- Infektionen: 218
- Parasiten: 192
- Viren: 175

### Tabelle: `remedy_pathogen_map` (Multiplex B)
**Automatische Verknüpfungen** basierend auf Keyword-Matching.

**Beispiel:**
```
Pathogen: Kohärente Harmonisierung von Staphylococcus aureus
  → Remedy: Kohärente Harmonisierung mit Echinacea D6 (Score: 4)
  → Remedy: Kohärente Harmonisierung mit Propolis C30 (Score: 3)
  → Remedy: Kohärente Harmonisierung mit Belladonna C30 (Score: 2)
```

---

## 🔧 Import-Tools

### Remedies importieren
```bash
# Dry-Run (nur analysieren)
python tools/import_txt_remedies.py --dry-run

# Echter Import
python tools/import_txt_remedies.py
```

**Quelle:** `imports/Datenbanken/#M *.txt` (32 Dateien)

### Pathogene importieren
```bash
# Dry-Run
python tools/import_txt_pathogens.py --dry-run

# Echter Import
python tools/import_txt_pathogens.py
```

**Quelle:** `imports/Datenbanken/#K *.txt` (5 Dateien)

### Multiplex-Links erstellen
```bash
# Dry-Run
python tools/link_pathogens_remedies.py --dry-run

# Echter Linking-Prozess
python tools/link_pathogens_remedies.py
```

---

## 🎯 Verwendung im Code

### Remedies finden
```python
from services.remedy_service import find_remedies_for_group

# Finde Remedies für eine Gruppe
remedies = find_remedies_for_group("bakterien_fein", max_results=5)

for name, indication in remedies:
    print(f"{name}: {indication}")
```

### Pathogene suchen
```python
from services.remedy_service import find_pathogens_by_keyword

# Suche Pathogene
pathogens = find_pathogens_by_keyword("staphylo", max_results=10)

for pathogen in pathogens:
    print(f"{pathogen['name']} ({pathogen['pathogen_type']})")
```

### Remedies für Pathogen finden (Multiplex B)
```python
from services.remedy_service import get_remedies_for_pathogen

# Hole Remedies für ein Pathogen
remedies = get_remedies_for_pathogen(pathogen_id=123, max_results=5)

for name, indication in remedies:
    print(f"→ {name}")
```

---

## 📋 Namenskonventionen

### Remedies
**Präfix:** "Kohärente Harmonisierung mit"

**Kategorien:**
- `Kohärente Harmonisierung mit Homöopathischen Mitteln`
- `Kohärente Harmonisierung mit Nosoden`
- `Kohärente Harmonisierung mit Bachblüten`
- `Kohärente Harmonisierung mit California Flower Essenzen`
- etc.

### Pathogene
**Präfix:** "Kohärente Harmonisierung von"

**Kategorien:**
- `Kohärente Harmonisierung von Bakterien`
- `Kohärente Harmonisierung von Viren`
- `Kohärente Harmonisierung von Pilzen`
- `Kohärente Harmonisierung von Parasiten`

---

## 🔍 Keyword-System

**Automatische Zuordnung** via Keywords:

### Remedy-Keywords
Extrahiert aus:
- Remedy-Name (z.B. "Arnica" → Keywords: arnica, trauma, verletzung)
- Indikation (z.B. "Immunstärkung" → Keywords: immun, stärkung, abwehr)
- Kategorie (z.B. "Homöopathie" → Keywords: homöopathie, mittel)

### Pathogen-Keywords
Extrahiert aus:
- Pathogen-Name (z.B. "Staphylococcus aureus" → Keywords: staphylococcus, aureus, bakterien)
- Typ (bakterien, viren, pilze, parasiten)
- Details (z.B. "Hautinfektionen" → Keywords: haut, infektion)

### Matching-Algorithmus
1. Vergleiche Keywords zwischen Pathogen und allen Remedies
2. Score = Anzahl übereinstimmender Keywords
3. Top 5 Remedies mit höchstem Score werden verknüpft
4. Priority-Score wird in `remedy_pathogen_map` gespeichert

---

## 📊 Statistiken

### Gesamt
- **6979 Datensätze** in Datenbank
- **0 Fehler** beim Import
- **3168 Duplikate** gefiltert

### Abdeckung
- **84% der Pathogene** haben passende Remedies (1076/1273)
- **16% ohne Matches** (197/1273) - meist sehr spezifische Pathogene

### Performance
- Import: ~30 Sekunden für alle Dateien
- Linking: ~15 Sekunden für 4373 Verknüpfungen
- Suche: <1ms pro Keyword-Match

---

## 🔮 Zukünftige Erweiterungen

### Phase 1 (Kurzfristig)
- ✅ Remedies importiert
- ✅ Pathogene importiert
- ✅ Multiplex B implementiert
- ⏳ AI-Beschreibungen generieren (Ollama)

### Phase 2 (Mittelfristig)
- ⏳ Integration in alle Scans (BAT, Multiplex)
- ⏳ Remedy-Empfehlungen in Reports
- ⏳ Weitere TXT-Files importieren (#P Psyche, #E Energie)

### Phase 3 (Langfristig)
- ⏳ Multiplex A (Remedy-Kombinationen)
- ⏳ Multiplex C (Multi-Ebenen mit Frequenzen)
- ⏳ Biofeedback-Integration

---

## 📚 Weitere Ressourcen

- **Harmonisierungs-System:** `docs/HARMONIZATION_SYSTEM.md`
- **BAT-System:** `docs/BAT_SYSTEM.md`
- **Tiefenanalyse:** `TIEFENANALYSE_271125.md`

---

**Erstellt:** 27.11.2025  
**Version:** 1.0  
**Status:** ✅ Produktionsbereit  
**Datensätze:** 6979
