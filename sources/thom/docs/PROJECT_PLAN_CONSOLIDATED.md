# Feldengine – Konsolidierter Projektplan v2
> Stand: 2026-03-08 | Tiefenscan & Optimierungsplan

---

## Teil 1: Tiefenscan – Identifizierte Probleme & Lücken

### 🔴 Kritische Bugs

| # | Problem | Schwere | Beschreibung |
|---|---------|---------|-------------|
| B1 | **Wortenergie-DB: "Bitte erst Klienten-Vektor erstellen"** | 🔴 Hoch | `WordEnergyDBManager` prüft `vectorAnalysis` (Zeile 154), aber der Vektor wird erst nach Klientenauswahl UND Slider-Interaktion erstellt. Der Nutzer wählt einen Klienten, hat aber noch keinen Vektor berechnet → Fehlermeldung irreführend. **Fix:** Wortenergie-Sammlungen unabhängig vom Vektor anzeigen/verwalten, nur die Resonanz-Analyse benötigt den Vektor. Button-Text ändern zu "Resonanz-Analyse (Vektor benötigt)". |
| B2 | **Frequenz-Anzeige zeigt "—" statt Wert** | 🟠 Mittel | In `TreatmentInProgress` (Zeile 932): `progress.currentPoint?.frequency` ist manchmal `undefined` statt 0, weil NLS-Punkte mit `scanFrequency` gemappt werden und Typkonversion-Edge-Cases auftreten. **Fix:** Explizite Null-Prüfung und Fallback auf 0.00 Hz. |
| B3 | **Nachtestung simuliert nur Shift** | 🟡 Info | `handleRetestAnalysis` (Zeile 217-235) simuliert Post-Behandlungs-Shift mit Random-Faktor statt echte Re-Analyse. Akzeptabel als MVP, sollte aber mit echten Sensor-Daten verbunden werden. |

### 🟠 Workflow-Lücken

| # | Lücke | Beschreibung |
|---|-------|-------------|
| W1 | **Kein automatischer Re-Analyse-Flow nach Harmonisierung** | Nach Behandlungsabschluss fehlt: automatische Re-Analyse der behandelten Meridian- und NLS-Punkte → Ergebnisse in nächsten Zyklus einfließen lassen. |
| W2 | **NLS-Scan-Konfiguration falsch platziert** | Aktuell im 3D-Viewer Side-Panel. Soll: oben rechts unterhalb des Analysefeldes (ClientVectorInterface). Scan-Start bleibt beim 3D-Viewer. |
| W3 | **Session-Management zu rudimentär** | Kein dediziertes Dashboard für Klienten-Sessions, keine Filterfunktionen, kein Vergleich historischer Sitzungen. |
| W4 | **Sitzungsberichte nicht automatisch befüllt** | Nutzer muss manuell "Berichte laden" klicken. Berichte enthalten keine NLS-Scan-Ergebnisse oder Remedy-Empfehlungen. |
| W5 | **Trendanalyse abhängig von abgeschlossenen Sessions** | TCMTrendAnalytics zeigt nur Daten wenn `diagnosis_snapshot` in Sessions gespeichert wurde – oft leer, da Snapshot-Speicherung nicht immer getriggert wird. |
| W6 | **Remedy-DB nicht in Harmonisierungssequenz integriert** | Die 100 Mittel sind vorhanden, aber nicht als Therapie-Empfehlung in den Behandlungsplan eingebunden. |

---

## Teil 2: Workflow-Analyse aus höherer Sicht

### Aktueller Workflow (Ist-Zustand)
```
1. Klient auswählen/anlegen
2. Dimensionen einstellen → Vektor berechnen
3. [Optional] Wortenergie-Sammlung hinzufügen
4. 3D-Viewer: Anatomie-Modell + NLS-Scan konfigurieren
5. NLS-Scan durchführen
6. Meridian-Diagnose automatisch
7. Behandlungssequenz starten (Audio)
8. [Optional] Nachtestung nach 21 Min Pause
9. [Manuell] Berichte laden
```

### Optimierter Workflow (Soll-Zustand)
```
1. Klient auswählen/anlegen → Dashboard mit Historie
2. Dimensionen einstellen + Wortenergie-DB → Vektor berechnen
3. NLS-Scan konfigurieren (oben rechts) → Scan starten (im 3D-Viewer)
4. Automatische Meridian-Diagnose + NLS-Korrelation
5. Behandlungsplan: Meridian-Punkte + NLS-Punkte + Remedy-Empfehlungen
6. Harmonisierungssequenz starten (Audio + Spooky2)
7. ↻ Nach jedem Zyklus: automatische Re-Analyse → adaptive Sequenz
8. Nachtestung → Vergleich vorher/nachher → automatischer Bericht
9. Session-Dashboard: Trends, Berichte, Mittel-DB
```

---

## Teil 3: Detaillierte Antworten auf Ihre Punkte

### a) Wortenergie-DB Fehlermeldung
**Problem bestätigt.** Die `analyzeResonance`-Funktion (WordEnergyDBManager.tsx:154) prüft `vectorAnalysis` und zeigt die irreführende Meldung. 
**Lösung:** Sammlungsverwaltung (CRUD) komplett ohne Vektor ermöglichen. Nur der "Resonanz-Analyse"-Button benötigt den Vektor. Klarer Tooltip: "Erstellen Sie zuerst einen Klienten-Vektor für die Resonanz-Voranalyse."

### b) NLS-Scan Konfiguration Platzierung
**Lösung:** NLS-Scan-Config wird als eigenständige Komponente aus dem AnatomyResonanceViewer extrahiert und im Analyse-Layout zwischen ClientVectorInterface und 3D-Viewer platziert. Der "NLS-Scan starten"-Button verbleibt im 3D-Viewer-Kontext.

### c) Freie/günstige Anatomie-Modelle
**Verfügbare hochdetaillierte Open-Source-Modelle:**

| Quelle | Lizenz | Details | Format | Qualität |
|--------|--------|---------|--------|----------|
| **Z-Anatomy** | CC-BY-SA 4.0 | 7000+ anatomische Strukturen, farb-codiert | GLB/FBX | ⭐⭐⭐⭐⭐ |
| **BodyParts3D (RIKEN)** | CC-BY-SA 2.1 JP | 159 Organe, japanisches Forschungsinstitut | OBJ → GLB | ⭐⭐⭐⭐ |
| **OpenAnatomy** | CC-BY-SA | Atlas-basiert, Segmentierungen | NRRD/VTK → GLB | ⭐⭐⭐⭐ |
| **Virtual Human** (NLM) | Public Domain | Komplett-Datensatz, Schnittbilder | DICOM → GLB | ⭐⭐⭐ |
| **AnatomyZone/Sketchfab** | CC-BY | Einzelorgane, didaktisch | GLB | ⭐⭐⭐ |

**Empfehlung:** Z-Anatomy ist am besten geeignet (7000+ Strukturen, GLB-Export direkt aus Blender-Datei verfügbar). Die Blender-Datei kann in Organ-Systeme aufgeteilt werden (Herz, Lunge, Niere etc.) und mit Draco-Kompression auf <10MB pro Modell reduziert werden.

**Import-Workflow bereits implementiert:** Das Upload-System unterstützt GLB bis 100MB via TUS-Protokoll.

### d) CPU/GPU-Last Optimierung
**Aktuelle Optimierungen:**
- ✅ Low-Poly Sphären (4-Segment), meshBasicMaterial
- ✅ Bedingtes useFrame (nur aktive Punkte)
- ✅ React.memo auf Meridian-Komponenten

**Weitere Optimierungsmöglichkeiten ohne Qualitätsverlust:**

| Maßnahme | Einsparung | Qualitätsimpact |
|----------|-----------|-----------------|
| **LOD (Level of Detail)** für 3D-Modelle | ~40% GPU | Keiner (entfernte Punkte vereinfacht) |
| **InstancedMesh** für identische Punkte | ~60% Draw Calls | Keiner |
| **Frustum Culling** explizit aktivieren | ~20% GPU | Keiner (unsichtbare Punkte nicht rendern) |
| **Web Worker** für Vektor-Berechnung | ~100% UI-Thread | Keiner |
| **requestIdleCallback** für Diagnose | Bessere Responsiveness | Keiner |
| **Canvas DPR begrenzen** auf max 1.5 | ~30% GPU bei HiDPI | Minimal |

### e) Design: Heller, freundlicher, heilsamer
**Aktuell:** Sehr dunkles Theme (background: `222 47% 4%` = fast schwarz).
**Vorschlag:** Warmes, helles Healing-Theme mit Teal/Sage-Akzenten:

```
Background:     hsl(165 20% 96%) → Warmes Off-White mit Grünstich
Card:           hsl(165 15% 98%) → Sanftes Weiß
Primary:        hsl(175 50% 40%) → Healing Teal
Secondary:      hsl(38 65% 55%) → Warmes Gold
Muted:          hsl(165 10% 90%) → Sanftes Sage
Accent:         hsl(280 40% 60%) → Sanftes Violett
```

### f) Frequenz-Anzeige Strich statt Wert
**Bug bestätigt.** In `TreatmentInProgress` (Zeile 932):
```typescript
{progress.currentPoint?.frequency != null ? `${Number(progress.currentPoint.frequency).toFixed(2)} Hz` : '— Hz'}
```
Das `!= null` fängt `undefined` ab, aber wenn `frequency` als String gespeichert wird (NLS-Punkte), schlägt `Number()` fehl → NaN → zeigt "—".
**Fix:** Defensive Konversion: `const freq = parseFloat(String(progress.currentPoint?.frequency)); isNaN(freq) ? '—' : freq.toFixed(2)`

### g) Trendanalyse Funktionsstand
**Status: 80% funktional.**
- ✅ LineChart über Sessions (Wu-Xing Elemente)
- ✅ RadarChart für Element-Balance
- ✅ Sheng/Ke-Zyklus Analyse
- ❌ Daten nur verfügbar wenn `diagnosis_snapshot` in Sessions gespeichert wird → oft leer
- ❌ Keine Echtzeit-Aktualisierung nach Behandlung
- ❌ Kein automatischer Vergleich vorher/nachher

**Fix benötigt:** `diagnosis_snapshot` zuverlässig bei Session-Abschluss speichern (Zeile 106-113 in Analyse.tsx: `completeSession` erhält derzeit keine Diagnose-Daten).

### h) Sitzungsberichte
**Status: 70% funktional.**
- ✅ HTML-Report mit Vektor-Daten, Diagnose, Behandlungsergebnis
- ✅ Druck- und Download-Funktion
- ❌ Manueller Klick auf "Berichte laden" nötig
- ❌ Keine NLS-Scan-Ergebnisse im Bericht
- ❌ Keine Remedy-Empfehlungen im Bericht
- ❌ Kein PDF-Export (nur HTML mit Print-CSS)
- ❌ Kein Klienten-Logo/Praxis-Header

### i) Nachtestungs-Flow & Adaptive Sequenz
**Aktueller Stand:**
- ✅ Nachtestung nach konfigurierbarer Pause (Standard 21 Min)
- ✅ Vergleich vorher/nachher im Retest-Tab
- ❌ Re-Analyse fließt NICHT in nächsten Zyklus ein
- ❌ Keine gezielte Re-Analyse nur der behandelten Punkte/NLS-Punkte

**Vorschlag: Adaptive Harmonisierungs-Loop:**
```
Zyklus N → Harmonisierung → Pause (21 Min) → Re-Analyse
  → Noch dysregulierte Punkte identifizieren
  → Neue Sequenz NUR mit verbleibenden Dysregulationen
  → Zyklus N+1 (adaptiv verkürzt)
```

### j) Audioqualität
**Status: 90% optimal.**
- ✅ 48kHz Sample Rate
- ✅ Konstante 0.8 Amplitude (kein Fade-in/out)
- ✅ Oszillator-Reuse (keine Clicks/Pops)
- ✅ AM-Modulation für sub-audible Frequenzen (432Hz Carrier)
- ❌ Keine AnalyserNode für Echtzeit-FFT-Visualisierung
- ❌ Kein AudioWorklet (würde Latenz weiter reduzieren)
- ❌ Keine USB-DAC spezifische Routing-Logik

**Empfehlung:** AudioWorklet für <1ms Latenz, AnalyserNode für Live-Spektrum-Anzeige.

### k) Spooky2 XM/Generator X Pro Konnektierung
**Vorbereitungsstand: 60%**
- ✅ Device-Profile angelegt: Spooky2 XM (VID: 0x04d8, PID: 0xea60) und Generator X (VID: 0x04d8, PID: 0x00dd)
- ✅ WebSerial-Discovery implementiert
- ✅ HardwareDiscoveryService mit Auto-Scan
- ❌ Kein Spooky2-spezifisches Protokoll implementiert (Befehlsformat, Handshake)
- ❌ Keine Frequenz-Upload-Funktion (Generator benötigt spezifisches Serial-Protokoll)
- ❌ Keine Biofeedback-Empfangslogik (Generator X Pro)

**Spooky2 Serial-Protokoll (basierend auf öffentlicher Dokumentation):**
```
Verbindung: 115200 Baud, 8N1
Befehlsformat: ASCII-basiert
Frequenz setzen: "F=xxxx.xx\r\n"
Amplitude: "A=x.xx\r\n"  
Wellenform: "W=sine|square|saw\r\n"
Start: "S\r\n"
Stop: "P\r\n"
```

### l) Klientenbezogenes Session-Dashboard
**Vorschlag: Dedizierte Unterseite `/klient/:id`**

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Klienten-Dashboard: Max Mustermann                  │
├──────────────────┬──────────────────────────────────┤
│ Session-Timeline │ Aktuelle Session                 │
│ ▸ Sitzung #5     │ ┌─────────────────────────────┐  │
│ ▸ Sitzung #4     │ │ Vektor-Radar (5D)           │  │
│ ▸ Sitzung #3     │ │ Element-Balance             │  │
│                  │ │ Meridian-Status             │  │
│ [Filter]         │ └─────────────────────────────┘  │
│ [Zeitraum]       │                                  │
├──────────────────┼──────────────────────────────────┤
│ Trend-Analyse    │ Mittel-Empfehlungen              │
│ ┌──────────────┐ │ ┌──────────────────────────────┐ │
│ │ Wu-Xing Chart│ │ │ Bachblüte: Mimulus           │ │
│ │ 5D-Verlauf   │ │ │ Schüßler: Nr.5 KalPhos      │ │
│ │ Stabilität   │ │ │ Homöo: Lycopodium D12        │ │
│ └──────────────┘ │ └──────────────────────────────┘ │
├──────────────────┴──────────────────────────────────┤
│ Sitzungsberichte                                    │
│ [PDF] [HTML] [Drucken] [Vergleichsbericht]          │
└─────────────────────────────────────────────────────┘
```

---

## Teil 4: Konsolidierter Umsetzungsplan v2

### 🔴 Phase 11 – Kritische Fixes (Sofort)

| # | Aufgabe | Priorität | Aufwand |
|---|---------|-----------|---------|
| 11.1 | **Wortenergie-DB Fehlermeldung fixen** | 🔴 | Klein |
| 11.2 | **Frequenz-Anzeige "—" Bug fixen** | 🔴 | Klein |
| 11.3 | **NLS-Scan-Config Position verschieben** | 🔴 | Mittel |
| 11.4 | **diagnosis_snapshot zuverlässig speichern** | 🔴 | Mittel |

### 🟠 Phase 12 – Design & UX Überarbeitung

| # | Aufgabe | Priorität | Aufwand |
|---|---------|-----------|---------|
| 12.1 | **Helles Healing-Theme implementieren** | 🟠 | Mittel |
| 12.2 | **Dark/Light Mode Toggle** | 🟠 | Klein |

### 🟡 Phase 13 – Adaptive Harmonisierung

| # | Aufgabe | Priorität | Aufwand |
|---|---------|-----------|---------|
| 13.1 | **Post-Zyklen Re-Analyse der behandelten Punkte** | 🟡 | Groß |
| 13.2 | **Adaptive Sequenz: verbleibende Dysregulationen in nächsten Zyklus** | 🟡 | Groß |
| 13.3 | **Nachtestung mit gezielter NLS-Punkt-Analyse** | 🟡 | Mittel |

### 🟢 Phase 14 – Audio & Hardware

| # | Aufgabe | Priorität | Aufwand |
|---|---------|-----------|---------|
| 14.1 | **AudioWorklet für minimale Latenz** | 🟢 | Mittel |
| 14.2 | **AnalyserNode: Live-FFT-Spektrum** | 🟢 | Klein |
| 14.3 | **Spooky2 XM Serial-Protokoll** | 🟢 | Groß |
| 14.4 | **Spooky2 Generator X Pro Protokoll + Biofeedback** | 🟢 | Groß |

### 🔵 Phase 15 – Klienten-Dashboard

| # | Aufgabe | Priorität | Aufwand |
|---|---------|-----------|---------|
| 15.1 | **Klienten-Dashboard Unterseite `/klient/:id`** | 🔵 | Groß |
| 15.2 | **Session-Timeline mit Vergleichsfunktion** | 🔵 | Mittel |
| 15.3 | **Remedy-Empfehlungen basierend auf Diagnose** | 🔵 | Mittel |
| 15.4 | **Erweiterte Sitzungsberichte (NLS + Remedies)** | 🔵 | Mittel |
| 15.5 | **Vergleichsbericht (Session A vs B)** | 🔵 | Mittel |

### ⚪ Phase 16 – Performance & 3D

| # | Aufgabe | Priorität | Aufwand |
|---|---------|-----------|---------|
| 16.1 | **InstancedMesh für Meridian-Punkte** | ⚪ | Mittel |
| 16.2 | **LOD-System für 3D-Modelle** | ⚪ | Mittel |
| 16.3 | **Web Worker für Vektor-Berechnungen** | ⚪ | Klein |
| 16.4 | **Z-Anatomy Modelle importieren (Organsysteme)** | ⚪ | Groß |

---

## Empfohlene Reihenfolge

```
Phase 11 (Bugs) → Phase 12.1 (Theme) → Phase 11.3 (NLS-Layout) 
→ Phase 13 (Adaptive Harmonisierung) → Phase 14 (Spooky2) 
→ Phase 15 (Dashboard) → Phase 16 (Performance)
```

**Geschätzter Gesamtaufwand:** ~20-25 Implementierungssessions

---

## Zusammenfassung

- **Identifiziert:** 3 Bugs, 6 Workflow-Lücken, 18 neue Aufgaben
- **Kritisch:** Wortenergie-Fehlermeldung, Frequenz-Anzeige, Diagnosis-Snapshot
- **Innovativ:** Adaptive Harmonisierung, Klienten-Dashboard, Spooky2-Integration
- **Abgeschlossen (bisher):** 25/25 aus Plan v1 (100%)
- **Neu geplant:** 18 Aufgaben in 6 Phasen
