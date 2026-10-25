# Quantum-Synergy Module

Quantum-Enhanced Synergy Detection für optimale Item-Kombinationen bei gegebenem Fokus.

## Features

✅ **Automatische Erkennung** aller Items aus 111+ Gruppen  
✅ **Hybrid-Ansatz** (Klassisch + Quantum-inspiriert)  
✅ **Skalierbar** bis 10.000+ Items  
✅ **Bruce Copen Integration** (Resonanz-Verstärkung)  
✅ **Frequenz-Harmonien** (Phi, Schumann)  
✅ **Fokus-Relevanz** Analyse  

## Installation

Keine zusätzlichen Dependencies erforderlich!
Verwendet nur Standard-Python-Bibliotheken.

## Verwendung

### Basis-Verwendung

```python
from core.quantum_synergy import QuantumSynergyEngine

# Engine initialisieren
engine = QuantumSynergyEngine()

# Synergistische Kombinationen finden
results = engine.find_synergistic_triggers(
    focus="Migräne",
    scan_results={
        "Kopfschmerzen (Stirn)": 8.5,
        "Magnesium-Mangel": 8.0,
        "Vitamin B2-Mangel": 7.5,
    },
    combination_size=3,
    top_n=5,
    threshold=7.0
)

# Ergebnisse anzeigen
for items, score, details in results:
    print(f"Score: {score:.2f}")
    for item in items:
        print(f"  • {item['label']}")
```

### Parameter

- **focus** (str): Fokus-Thema (z.B. "Migräne", "Erschöpfung", "Verdauung")
- **scan_results** (dict): Optional - Scan-Ergebnisse {label: score}
- **combination_size** (int): Anzahl Items pro Kombination (2-5, default: 3)
- **top_n** (int): Anzahl Top-Ergebnisse (default: 5)
- **prefilter_size** (int): Items nach Pre-Filtering (default: 200)
- **threshold** (float): Mindest-Score für Synergy (0-10, default: 7.0)

### Datenbank aktualisieren

```python
# Nach Hinzufügen neuer Gruppen
engine.update_database(force=True)
```

### Statistiken

```python
stats = engine.get_statistics()
print(f"Items: {stats['total_items']}")
print(f"Gruppen: {stats['total_groups']}")
```

## Tests

```bash
# Alle Tests ausführen
python test_quantum_synergy.py

# Oder via CMD
test_quantum_synergy.cmd
```

## Architektur

### Module

1. **database_manager.py** - Dynamisches Laden aller Items
2. **synergy_core.py** - Synergy-Score Berechnung
3. **hybrid_engine.py** - Haupt-Engine (Hybrid-Ansatz)

### Workflow

```
INPUT: Fokus + Scan-Ergebnisse
    ↓
[1] Pre-Filtering (Klassisch)
    → Reduziert auf Top 200 relevante Items
    ↓
[2] Quantum-inspirierte Suche
    → Findet optimale Kombinationen
    ↓
[3] Ranking & Details
    → Top-5 synergistische Kombinationen
    ↓
OUTPUT: Ergebnisse mit Scores & Details
```

### Synergy-Score Formel

```python
synergy_score = (
    0.3 * sum(individual_scores) +      # Einzelwirkungen
    0.3 * resonance_amplification +      # Bruce Copen Resonanz
    0.2 * frequency_harmony +            # Phi/Schumann Harmonien
    0.2 * focus_relevance                # Fokus-Bezug
)
```

## Performance

| Items | Kombinationen | Pre-Filter | Suche | Gesamt |
|-------|--------------|------------|-------|--------|
| 2500  | ~2.6M        | ~0.5s      | ~2s   | ~2.5s  |
| 5000  | ~20M         | ~1s        | ~4s   | ~5s    |
| 10000 | ~166M        | ~2s        | ~8s   | ~10s   |

## Skalierbarkeit

✅ **Automatisch skalierbar** bei neuen Gruppen  
✅ **Kein Code-Update** erforderlich  
✅ **Intelligentes Sampling** bei großen Suchräumen  
✅ **Caching** für Performance  

## Beispiele

### Migräne

```python
results = engine.find_synergistic_triggers(
    focus="Migräne",
    combination_size=3,
    threshold=7.0
)
```

### Erschöpfung / Burnout

```python
results = engine.find_synergistic_triggers(
    focus="Erschöpfung Burnout",
    combination_size=3,
    threshold=6.5
)
```

### Verdauungsprobleme

```python
results = engine.find_synergistic_triggers(
    focus="Verdauung Reizdarm",
    combination_size=3,
    threshold=7.0
)
```

## Version

**1.0.0** - Initial Release

## Autor

Morphic Engine Team
