# TIEFENANALYSE: 13:49 Uhr Backup - Vollständige Systemprüfung
**Datum:** 19.11.2025, 11:43 Uhr  
**Status:** Projekt gesichert, KEINE Änderungen ohne Rücksprache

---

## 1. STRUKTURANALYSE: Gruppen-Definitionen

### 1.1 Import-Hierarchie
```
procedural_groups.py
├── groups_extended.py (gext)                    → VORHANDEN
├── groups_extended_v2.py (gext2)                → VORHANDEN
├── groups_phase4_corrected.py (gp4_1)          → VORHANDEN
├── groups_phase4_priority2.py (gp4_2)          → VORHANDEN
├── groups_phase4_priority3.py (gp4_3)          → VORHANDEN
├── groups_phase5_priority1.py (gp5_1)          → VORHANDEN
├── groups_phase5_priority2.py (gp5_2)          → VORHANDEN
├── groups_phase5_priority3_4.py (gp5_3)        → VORHANDEN
└── groups_phase5_priority5.py (gp5_5)          → VORHANDEN
```

**Status:** ✓ Alle Module existieren und werden importiert

### 1.2 _GROUP_LABELS Aufbau

#### Basis-Definitionen (Zeilen 213-611)
- **43 statisch definierte Gruppen** direkt in `_GROUP_LABELS`
- Beispiele: `kreislauf`, `chakren`, `bakterien`, `endokrin`, `detox`, etc.
- **Status:** ✓ Korrekt

#### Erweiterte Gruppen aus gext2 (Zeilen 614-691)
- **47 Gruppen** aus `groups_extended_v2.py`
- Kategorien: Strukturelle Systeme (FEIN), Nervensystem, Immunsystem, Verdauung, Remedies-Multiplex, etc.
- **Status:** ✓ Wird korrekt geladen (wenn gext2 verfügbar)

#### Phase 4 Gruppen (Zeilen 694-765)
- **44 Gruppen** aus `groups_phase4_*.py`
- Kategorien: Zähne, Wirbelsäule, Strahlung, Entgiftung, Verdauung, Nerven, Herz, Knochen, Toxine, Atmung, Hormone, Luftbelastungen, Nahrung
- **Status:** ✓ Wird korrekt geladen (wenn gp4_1/2/3 verfügbar)

#### Phase 5 Gruppen (Zeilen 768-809)
- **30 Gruppen** aus `groups_phase5_*.py`
- Kategorien: Infektionen, Nährstoffmängel, Energetische Systeme, Psyche, Miasmatik, etc.
- **Status:** ✓ Wird korrekt geladen (wenn gp5_1/2/3/5 verfügbar)

#### Erweiterte Gruppen aus gext (Zeilen 812-918+)
- **~90 Gruppen** aus `groups_extended.py`
- Kategorien: Wirbelsäule (detailliert), Zahnorgane, Nervensystem, Lymphsystem, Immunsystem, Knochen, Verdauung, Atmung, Entgiftung, Schwindel, Remedies (Bachblüten, Homöopathie, Schüssler)
- **Status:** ✓ Wird korrekt geladen (wenn gext verfügbar)

**Gesamtzahl Gruppen in _GROUP_LABELS:** ~254 Gruppen (bei vollständigen Imports)

---

## 2. LÜCKEN-ANALYSE

### 2.1 Fehlende Gruppen-Definitionen

**KEINE LÜCKEN in der Gruppen-Definition selbst**, ABER:

#### Problem: Fehlende Labels für einige Gruppen
Einige Gruppen werden in `_GROUP_LABELS` referenziert, aber die entsprechenden Listen in den Modulen könnten leer oder unvollständig sein.

**Beispiel:**
- `homoeopathie_klassisch` ist NICHT in `_GROUP_LABELS` enthalten
- Es gibt nur eine spezielle Fallback-Logik in `generate_candidates_for_group` (Zeile 1184), die `_load_remedy_labels_from_medica()` aufruft
- **RISIKO:** Wenn `Medica.json` fehlt oder nicht lesbar ist, gibt es keinen Fallback

### 2.2 FULL-Profil Diskrepanz

**Aktuelles FULL-Profil in main.py (Zeilen 2783-2868):**
- **58 Gruppen** definiert

**Verfügbare Gruppen in _GROUP_LABELS:**
- **~254 Gruppen** verfügbar

**LÜCKE:** Das FULL-Profil nutzt nur **23%** der verfügbaren Gruppen!

**Fehlende Kategorien im FULL-Profil:**
- Detaillierte Wirbelsäulen-Segmente (HWS/BWS/LWS einzeln)
- Knochen-Details (Osteoblasten, Osteoklasten, Knorpel)
- Verdauungs-Segmente (Magen, Dünndarm, Dickdarm einzeln)
- Zahnorgane-Quadranten
- Nervensystem-Details
- Lymphsystem
- Viele Remedy-Multiplex-Gruppen

---

## 3. STRUKTURFEHLER

### 3.1 KRITISCH: tcm_full überschreibt k-Parameter

**Ort:** `procedural_groups.py`, Zeile 1136

```python
if group == "tcm_full":
    counts = {
        "LU": 11, "LI": 20, "ST": 45, "SP": 21, "HT": 9, "SI": 19,
        "BL": 67, "KI": 27, "PC": 9, "TE": 23, "GB": 44, "LV": 14,
        "Ren": 24, "Du": 28,
    }
    labels = []
    for prefix, nmax in counts.items():
        for n in range(1, nmax + 1):
            labels.append(f"{prefix}{n}")
    k = len(labels)  # ← KRITISCHER FEHLER: überschreibt k mit 361!
```

**Problem:**
- `tcm_full` erzeugt 361 Labels
- Setzt `k = 361`, ignoriert das übergebene `k` (z.B. 4-5)
- Bei `k_total=512` auf 58 Gruppen: ~9 Kandidaten pro Gruppe
- `tcm_full` nimmt 361, bleiben 151 für 57 Gruppen (~2.6 pro Gruppe)
- **Bei 117 Gruppen:** nur ~4 pro Gruppe → `tcm_full` nimmt 361, bleiben 151 für 116 (~1.3 pro Gruppe)
- **Gruppen am Ende der Liste bekommen 0 Kandidaten!**

**Schweregrad:** KRITISCH - Verhindert faire Kandidatenverteilung

### 3.2 KRITISCH: chakren_full überschreibt k-Parameter

**Ort:** `procedural_groups.py`, Zeilen 1137-1150

```python
elif group == "chakren_full":
    main = [...]  # 7 Haupt-Chakren
    ext = [...]   # 8 Neben-Chakren
    labels = [lbl for lbl, _ in main] + ext
    k = len(labels)  # ← FEHLER: überschreibt k mit 15!
```

**Problem:**
- Ähnlich wie `tcm_full`, aber weniger drastisch
- Setzt `k = 15` statt das übergebene `k` zu respektieren

**Schweregrad:** MITTEL - Verschärft das tcm_full-Problem

### 3.3 MITTEL: Schwacher Fallback

**Ort:** `procedural_groups.py`, Zeile 1196

```python
if not labels:
    labels = [f"{group}-item{i+1}" for i in range(12)]
```

**Problem:**
- Erzeugt immer 12 generische Items, unabhängig vom übergebenen `k`
- Wenn `k=4`, sollten 4 Items erzeugt werden, nicht 12
- Verschwendet Ressourcen und erzeugt unnötige Kandidaten

**Schweregrad:** MITTEL - Funktioniert, aber suboptimal

### 3.4 MITTEL: Frühe Returns verhindern Fallback

**Ort:** `procedural_groups.py`
- Zeile 1080: `return []` wenn TCM-Formeln fehlen
- Zeile 1086: `return []` wenn total <= 0
- Zeile 1109: `return []` wenn keine Combos

**Problem:**
- Wenn externe Daten (tcm.txt, Medica.json) fehlen, werden **keine Kandidaten** erzeugt
- Der Fallback (Zeile 1196) wird nie erreicht
- **Remedy-Gruppen wie `tcm_rezepturen`, `homoeopathie_klassisch_potenzen` verschwinden komplett**

**Schweregrad:** MITTEL - Datei-abhängig, aber kritisch wenn Dateien fehlen

---

## 4. FUNKTIONSFEHLER

### 4.1 generate_fullbody_candidates: Unfaire Verteilung

**Ort:** `procedural_groups.py`, Zeilen 1276-1290

```python
def generate_fullbody_candidates(groups: List[str], seed: str, k_total: int = 64) -> List[Dict]:
    if not groups:
        groups = list(_GROUP_LABELS.keys())
    g_count = max(1, len(groups))
    per = max(1, k_total // g_count)  # Gleichmäßige Verteilung
    remainder = max(0, k_total - per * g_count)
    all_items: List[Dict] = []
    for idx, g in enumerate(groups):
        extra = 1 if idx < remainder else 0
        items = generate_candidates_for_group(g, seed, k=per + extra)
        # ...
```

**Problem:**
- Gleichmäßige Verteilung: `per = k_total // g_count`
- Bei 512 / 117 = 4.4 → `per = 4`
- ABER: `tcm_full` ignoriert dies und nimmt 361!
- **Resultat:** Massive Ungleichverteilung, Gruppen am Ende bekommen 0

**Schweregrad:** HOCH - Direkte Folge von 3.1 und 3.2

### 4.2 Fehlende Validierung der Kandidatenanzahl

**Problem:**
- `generate_candidates_for_group` kann 0, 4, 12, oder 361 Kandidaten zurückgeben
- Es gibt **keine Validierung**, dass mindestens 1 Kandidat pro Gruppe erzeugt wird
- Es gibt **keine Warnung**, wenn Gruppen ignoriert werden

**Schweregrad:** MITTEL - Debugging wird erschwert

### 4.3 Medica.json Abhängigkeit

**Ort:** `procedural_groups.py`, Zeilen 142-170

```python
def _load_remedy_labels_from_medica() -> List[str] | None:
    try:
        if not _MEDICA_JSON_PATH.exists():
            return None
        # ...
```

**Problem:**
- `homoeopathie_klassisch` ist komplett abhängig von `Medica.json`
- Wenn die Datei fehlt, gibt es **keinen Fallback**
- Gruppe verschwindet komplett aus den Kandidaten

**Schweregrad:** HOCH - Kritische Remedy-Gruppe kann verschwinden

---

## 5. ABHÄNGIGKEITSFEHLER

### 5.1 Stille Import-Failures

**Ort:** `procedural_groups.py`, Zeilen 13-51

```python
try:
    from . import groups_extended as gext
    GROUPS_EXTENDED_AVAILABLE = True
except ImportError:
    GROUPS_EXTENDED_AVAILABLE = False
    gext = None
```

**Problem:**
- Import-Fehler werden **stillschweigend ignoriert**
- Wenn ein Modul Syntaxfehler hat, wird es einfach übersprungen
- **Keine Warnung**, dass Gruppen fehlen
- **RISIKO:** Nach einem Update könnte ein Syntaxfehler in `groups_extended.py` dazu führen, dass 90 Gruppen verschwinden, OHNE dass es bemerkt wird!

**Schweregrad:** KRITISCH - Silent Failures sind gefährlich

### 5.2 Keine Versionskontrolle für Gruppen-Module

**Problem:**
- Es gibt **keine Versionsnummern** für die Gruppen-Module
- Es gibt **kein Schema**, um zu prüfen ob Module kompatibel sind
- **RISIKO:** Ein Update von `groups_extended_v2.py` könnte Gruppen umbenennen/löschen, und der Rest des Systems würde es nicht merken

**Schweregrad:** MITTEL - Langfristiges Wartbarkeitsproblem

### 5.3 Datei-Abhängigkeiten ohne Fallback

**Dateien:**
- `listen/Medica.json` (für `homoeopathie_klassisch`)
- `listen/tcm.txt` (für `tcm_rezepturen`)

**Problem:**
- Wenn diese Dateien fehlen/beschädigt sind, verschwinden die Gruppen
- **Kein Fallback** auf generische Kandidaten
- **Keine Warnung** im Log

**Schweregrad:** HOCH - Remedy-Funktionalität kann komplett ausfallen

---

## 6. MÖGLICHE LÖSUNGEN

### Lösung A: MINIMAL-FIX (Sofort umsetzbar, geringes Risiko)

**Änderung 1:** Fix `tcm_full` k-Override
```python
# Zeile 1136: ALT
k = len(labels)

# Zeile 1136: NEU
if k <= 0:
    k = len(labels)
```

**Änderung 2:** Fix `chakren_full` k-Override
```python
# Zeile 1150: ALT
k = len(labels)

# Zeile 1150: NEU
if k <= 0:
    k = len(labels)
```

**Effekt:**
- ✓ Respektiert übergebenes `k`
- ✓ Faire Kandidatenverteilung
- ✓ Alle Gruppen bekommen Kandidaten
- ✓ Minimale Code-Änderung (2 Zeilen)
- ✓ Keine Seiteneffekte

**Risiko:** MINIMAL

---

### Lösung B: ROBUSTER FALLBACK (Mittlere Komplexität)

**Änderung 1-2:** Wie Lösung A

**Änderung 3:** Verbesserter generischer Fallback
```python
# Zeile 1196: ALT
labels = [f"{group}-item{i+1}" for i in range(12)]

# Zeile 1196: NEU
labels = [f"{group}-item{i+1}" for i in range(max(k, 12))]
```

**Änderung 4:** Entferne frühe Returns, lasse zum Fallback durchfallen
```python
# Zeile 1080: ALT
return []

# Zeile 1080: NEU
# Falls zum Fallback durchfallen lassen
```

**Effekt:**
- ✓ Wie Lösung A
- ✓ Guarantee: Jede Gruppe erzeugt mindestens 1 Kandidat
- ✓ Keine Abhängigkeit von externen Dateien

**Risiko:** GERING

---

### Lösung C: INTELLIGENTE VERTEILUNG (Hohe Komplexität)

**Konzept:**
- Gruppen bekommen Prioritäten (wichtig, normal, niedrig)
- `tcm_full` bekommt mehr Kandidaten als andere
- Dynamische Verteilung basierend auf Gruppen-Wichtigkeit

**Beispiel:**
```python
PRIORITY_WEIGHTS = {
    "tcm_full": 10,      # Bekommt 10x mehr Kandidaten
    "chakren_full": 3,   # Bekommt 3x mehr Kandidaten
    # Alle anderen: 1
}
```

**Effekt:**
- ✓ Faire UND intelligente Verteilung
- ✓ Wichtige Gruppen bekommen mehr Kandidaten
- ✗ Hohe Komplexität
- ✗ Schwer wartbar

**Risiko:** HOCH (Komplexität)

---

### Lösung D: VALIDIERUNG & WARNINGS (Ergänzend zu A/B)

**Änderung 1:** Füge Logging hinzu
```python
import logging
logger = logging.getLogger(__name__)

# Bei Import-Failure:
logger.warning(f"Gruppen-Modul {name} konnte nicht geladen werden")

# Bei 0 Kandidaten:
logger.warning(f"Gruppe {group} hat 0 Kandidaten erzeugt")
```

**Änderung 2:** Füge Unit-Tests hinzu
```python
def test_all_groups_generate_candidates():
    for group in _GROUP_LABELS.keys():
        candidates = generate_candidates_for_group(group, "test", k=5)
        assert len(candidates) >= 1, f"{group} erzeugt 0 Kandidaten!"
```

**Effekt:**
- ✓ Frühzeitige Fehlerkennung
- ✓ Besseres Debugging
- ✓ Verhindert zukünftige Probleme

**Risiko:** MINIMAL

---

## 7. EMPFEHLUNG: STUFENPLAN

### STUFE 1: SOFORT (Option 2)
1. Backup erstellen
2. Lösung A implementieren (2 Zeilen ändern)
3. Test-Scan durchführen
4. Validieren: Alle Gruppen haben Kandidaten

**Zeitaufwand:** 10 Minuten  
**Risiko:** MINIMAL  
**Effekt:** 90% des Problems gelöst

---

### STUFE 2: KURZ nach Stufe 1 (wenn Stufe 1 erfolgreich)
1. Lösung B implementieren (Robuster Fallback)
2. Test-Scan durchführen
3. Validieren: Auch ohne externe Dateien funktioniert es

**Zeitaufwand:** 30 Minuten  
**Risiko:** GERING  
**Effekt:** 100% des aktuellen Problems gelöst

---

### STUFE 3: LANGFRISTIG (separate Session)
1. Lösung D implementieren (Logging & Tests)
2. FULL-Profil Review: Welche Gruppen sollen rein?
3. Intelligente Verteilung evaluieren (optional)

**Zeitaufwand:** 2-3 Stunden  
**Risiko:** GERING  
**Effekt:** Zukünftige Probleme verhindern

---

## 8. FEHLER-PRÄVENTION: Zukünftige Strategien

### 8.1 Code-Review-Checkliste
```
☐ Wurden neue Gruppen zu _GROUP_LABELS hinzugefügt?
☐ Wurden diese Gruppen im FULL-Profil berücksichtigt?
☐ Wurde ein Test-Scan mit --export durchgeführt?
☐ Wurden candidates_by_group geprüft? (0-Kandidaten?)
☐ Sind Remedy-Gruppen sichtbar im HTML?
```

### 8.2 Automatische Tests (CI/CD)
```python
# test_group_coverage.py
def test_no_zero_candidate_groups():
    """Stelle sicher, dass keine Gruppe 0 Kandidaten erzeugt"""
    from core.subgroups import procedural_groups
    
    all_groups = list(procedural_groups._GROUP_LABELS.keys())
    
    for group in all_groups:
        candidates = procedural_groups.generate_candidates_for_group(
            group, seed="test", k=5
        )
        assert len(candidates) >= 1, f"Gruppe '{group}' erzeugt 0 Kandidaten!"
```

### 8.3 Gruppen-Manifest
```yaml
# groups_manifest.yaml
version: "2.0"
modules:
  groups_extended:
    version: "1.5"
    groups: 90
    critical: true
  groups_extended_v2:
    version: "1.2"
    groups: 47
    critical: true
```

### 8.4 Import-Validierung
```python
# Bei Startup
def validate_group_imports():
    errors = []
    
    if not GROUPS_EXTENDED_AVAILABLE:
        errors.append("CRITICAL: groups_extended konnte nicht geladen werden")
    
    if len(_GROUP_LABELS) < 200:
        errors.append(f"WARNING: Nur {len(_GROUP_LABELS)} Gruppen geladen (erwartet: ~254)")
    
    if errors:
        logger.error("\n".join(errors))
        raise ImportError("Gruppen-Module unvollständig geladen!")
```

---

## 9. ZUSAMMENFASSUNG

### Kritische Probleme (BLOCKING)
1. ✗ `tcm_full` überschreibt k → Unfaire Verteilung → 0 Kandidaten für viele Gruppen
2. ✗ Frühe Returns ohne Fallback → Remedy-Gruppen verschwinden bei fehlenden Dateien
3. ✗ Stille Import-Failures → Gruppen können unbemerkt verschwinden

### Mittlere Probleme (WICHTIG)
4. ⚠ `chakren_full` überschreibt k (weniger kritisch als tcm_full)
5. ⚠ Schwacher Fallback (erzeugt 12 statt k Items)
6. ⚠ Keine Validierung der Kandidatenanzahl

### Kleine Probleme (OPTIONAL)
7. ℹ FULL-Profil nutzt nur 23% der verfügbaren Gruppen
8. ℹ Keine Gruppen-Versionskontrolle

### Empfohlener Weg
**OPTION 2 + STUFE 1** ist die richtige Wahl:
- ✓ Minimal-invasiv (2 Zeilen)
- ✓ Löst 90% des Problems
- ✓ Geringes Risiko
- ✓ Schnell testbar
- ✓ Kann bei Problemen sofort zurückgerollt werden

**NACH erfolgreicher Stufe 1:**
- Stufe 2 implementieren (Robuster Fallback)
- Stufe 3 planen (Logging, Tests, Profil-Review)

---

**NÄCHSTER SCHRITT:**  
Rücksprache mit User: Ist Option 2 + Stufe 1 jetzt sinnvoll?
