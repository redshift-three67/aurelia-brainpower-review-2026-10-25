# Morphic Operator Workbench Design

**Stand:** `2026-07-05`
**Workspace:** `C:/morphic_V1`
**Status:** abgestimmtes Zieldesign vor Implementierungsplanung

## Ziel

`Morphic V1` soll von einer teilweise fragmentierten Web-Shell mit konkurrierenden Workflow-Modellen zu einer professionellen, intuitiven und nachvollziehbaren `Operator Workbench` konsolidiert werden.

Das neue Zielbild verbindet:

- einen einzigen offiziellen Operator-Workflow,
- eine separate Erklaer-/Pipelineansicht,
- einen klaren Hardware-/Realtime-Kontext,
- einen Review-Gate vor Ausfuehrung,
- Ergebnis-, Harmonisierung- und Exportphasen als echte Workflow-Abschnitte,
- sowie einen transparenten `Dual mode` fuer Hardware- und Realtime-Kommunikation.

## Ausgangslage

Die vorangehende Tiefenanalyse hat diese Kernprobleme bestaetigt:

1. Es existieren drei konkurrierende Workflow-Realitaeten:
   - produktiver Top-N-CLI-Pfad,
   - 12-Step-Orchestrator,
   - 8-Step-Web-Wizard.
2. Die aktuelle Web-Oberflaeche ist nutzbar, aber noch zu nah an einem linearen Start-Dialog statt an einem echten Operator-Arbeitsplatz.
3. Hardware-/Realtime-Kommunikation ist teilweise real, teilweise simuliert, aber nicht konsistent sichtbar oder ehrlich klassifiziert.
4. `Radi144` enthaelt mehrere starke UX-/Workflow-Muster, die sinnvoll transferiert werden koennen, ohne dessen spekulativere Fach- oder Hardwarebehauptungen zu uebernehmen.

## Designprinzipien

1. **Eine Arbeitsoberflaeche**
   - `apps/web/static/*` bleibt die einzige offizielle Produktionsoberflaeche fuer Operatoren.
2. **Eine Erklaeroberflaeche**
   - die Pipeline-/Workflow-Erklaerung bleibt separat und wird nicht mehr als konkurrierender Produktfluss behandelt.
3. **Eine Statussprache**
   - UI, API, Laufstatus, Hardware und Ergebnisse benutzen dieselben Begriffe.
4. **Review vor Ausfuehrung**
   - kein Scan- oder Harmonisierungsstart ohne bewussten Freigabeschritt.
5. **Hardware-Wahrheit statt Hardware-Mythos**
   - jede Komponente wird als `real`, `fallback`, `simuliert`, `nicht verfuegbar` oder `nicht implementiert` klassifiziert.
6. **Ergebnis als Arbeitsphase**
   - Resultate, technische Details, Harmonisierung und Export sind integrale Bestandteile des Flows.
7. **Resume statt Wegwerf-Wizard**
   - Sitzungswiederaufnahme und Templates gehoeren in den offiziellen Workflow.

## Offizieller Ziel-Workflow

Der neue kanonische `Morphic Operator Workbench` besteht aus 10 Phasen:

### Phase 1: Runtime & Workspace

Zweck:

- Health, Quellen, Runtime, Report-Roots und grundsaetzliche Betriebsbereitschaft sichtbar machen.

Inhalte:

- Python-/Runtime-Status
- Datenbanken
- Quellen-Registry
- Report-Roots / Archive-Roots
- Hardware-Readiness-Kurzstatus
- letzter wiederaufnehmbarer Workbench-Zustand

### Phase 2: Klient / Kontext

Zweck:

- offizieller Einstieg ueber den professionellen Klientenpfad.

Inhalte:

- Nachname
- Vorname
- Geburtsdatum
- Geburtsort
- optionale Zusatzfelder, sofern sie im produktiven Pfad verwendet werden

Nicht Ziel der ersten Konsolidierung:

- sofortige Uebernahme aller Radi144-Eingangsarten wie Gruppe, Geo oder Bild als gleichrangige Startmodi

### Phase 3: Fokus & Zielsetzung

Zweck:

- den fachlichen Operator-Kontext sauber setzen.

Inhalte:

- Fokus
- Hauptsymptom
- Analyse-Level
- Top-N
- optional Fokus-Historie
- wiederverwendbare Fokus-Sets sind eine geplante Folgestufe und nicht Teil der ersten Ausbaustufe

### Phase 4: Analyseprofil

Zweck:

- reproduzierbare Konfiguration des Laufpfads.

Inhalte:

- Profiltemplate
- Entropiemodus
- Bildreferenz
- adaptive Limits
- weitere produktiv relevante Analyseoptionen

### Phase 5: Hardware & Realtime

Zweck:

- eine professionelle, ehrliche und nachvollziehbare Systemschicht zwischen Konfiguration und Freigabe.

Diese Phase enthaelt vier Teilbereiche:

1. `Capability Snapshot`
2. `Realtime Calibration`
3. `Mode Decision`
4. `Traceability Manifest`

Details dazu stehen im Abschnitt `Hardware Truth Model`.

### Phase 6: Review & Freigabe

Zweck:

- bewusster Uebergabepunkt vor der Ausfuehrung.

Inhalte:

- zusammengefasster Klientenkontext
- Fokus und Zielsetzung
- Analyseprofil
- Hardware-/Realtime-Status
- aktueller Modus: `Standard` oder `Experte`
- geplanter produktiver Pfad
- Hinweis auf erkannte Fallbacks, Simulationen oder Experten-Gates

### Phase 7: Analyse-Lauf

Zweck:

- aktiver Lauf, Fortschritt und Ereignisse.

Inhalte:

- Phase
- Substeps
- Fortschritt
- Logs
- aktueller Status
- die erste Ausbaustufe darf noch auf dem bestehenden Polling-/Parsing-Modell aufsetzen; eine eventbasierte Rueckfuehrung ist eine geplante Folgestufe

### Phase 8: Ergebnis-Uebersicht

Zweck:

- operatorgerechte Sicht auf das zentrale Ergebnis.

Inhalte:

- Top-Profile
- Top-Resonanzen
- zusammenfassende Resultatkarten
- relevante Exportpfade
- empfohlene naechste Aktionen

### Phase 9: Technische Details & Nachvollziehbarkeit

Zweck:

- technische Transparenz ohne Debug-Chaos.

Inhalte:

- Hardwarekontext
- EMF-Kontext
- Entropiequelle
- Driver-Layer-/Snapshot-Bezug
- Run Trace Manifest
- Session-/Artifact-Verknuepfung

### Phase 10: Harmonisierung & Export

Zweck:

- professioneller Abschluss des Operator-Zyklus.

Inhalte:

- Harmonisierung
- Report- und Exportuebersicht
- Session-Abschluss
- optional Template aus Session erzeugen
- neuer Fall / Ruecksprung / Abschlussaktion

## Zu uebernehmende Radi144-Patterns

Die folgenden Radi144-Muster werden bewusst uebernommen:

1. **Review Gate vor dem Start**
2. **Resume + Templates**
3. **Result Workspace statt Endscreen**
4. **Abschluss als eigener Schritt**
5. **Getrennte Oberflaechen fuer Arbeit und Verstaendnis**
6. **Preflight als echter Einstieg**
7. **Naechste Aktion immer klar sichtbar**

## Nicht zu uebernehmende Radi144-Muster

1. `localStorage` als primaerer Persistenzkern
2. rohe JSON-/Debug-Ansichten als Standardansicht
3. spekulative Hardware-/EMF-Erklaerrahmen
4. monolithische Mixed-Responsibility-Dateien
5. ueberladene Multi-Input-Verzweigung bereits in der ersten Morphic-Konsolidierung

## Integrationsarchitektur im Projekt

### 1. Offizieller Web-Entry-Point

`apps/web/main.py` bleibt der einzige offizielle Web-Entry-Point.

Er ist verantwortlich fuer:

- die kanonische Workbench
- die zugehoerigen API-Endpunkte
- die Pipeline-/Erklaeroberflaeche

### 2. Offizielle Produktionsoberflaeche

`apps/web/static/*` wird weiterentwickelt und bleibt die einzige offizielle Produktionsoberflaeche.

Ziel:

- kein drittes Frontend
- keine konkurrierenden Bedienwege
- kein Nebeneinander mehr von halb-offiziellen Wizard-Linien

### 3. Separate Pipeline-Oberflaeche

Die bisherige `/workflow-stepping`-Idee bleibt erhalten, wird aber neu positioniert als:

- Schulungsoberflaeche
- Systemerklaerung
- Debug-/Onboarding-Kontext

Nicht als zweite Produktionsoberflaeche.

## Kanonische Wahrheitsquellen

Um UI, API und Laufrealitaet zu synchronisieren, werden drei kanonische Modelle eingefuehrt.

### A. Workflow Registry

Zweck:

- eine einzige Quelle fuer:
  - Phasenreihenfolge
  - Labels
  - erlaubte Uebergaenge
  - Validierungsanforderungen
  - CTA-Definitionen

Die Registry beschreibt den offiziellen 10-Phasen-Operator-Flow.

### B. Hardware Truth Model

Zweck:

- eine einzige Sprache fuer Hardware-/Realtime-Kommunikation.

Jede Komponente erhaelt mindestens:

- `id`
- `label`
- `role`
- `status`
- `truth_class`
- `used_in_analysis`
- `used_in_harmonization`
- `notes`

Beispielhafte `status`-Werte:

- `real_active`
- `real_available_not_used`
- `software_fallback`
- `simulation`
- `not_available`
- `not_implemented`

Beispielhafte `truth_class`-Werte:

- `deterministic`
- `environment_dependent`
- `stochastic`
- `simulated`

### C. Run Trace Manifest

Zweck:

- eine kuratierte technische Mitschrift je Lauf.

Der Manifest enthaelt:

- Workbench-Kontext
- Freigabestatus
- Operator-Modus
- Analyseprofil
- aktive oder erkannte Hardwarepfade
- genutzte Entropie-/Realtime-Quellen
- Fallbacks
- Snapshot-/EMF-Kontext
- Session-/Artifact-Referenzen

Der Manifest wird nicht als rohe Debug-Ablage verstanden, sondern als offizielle Nachvollziehbarkeitsansicht.

## Hardware-/Realtime-Einbindung im Workbench

Die Hardware-/Realtime-Kommunikation wird aehnlich strukturiert wie in Radi144, aber fachlich strenger und ehrlicher.

### Teilbereich 1: Capability Snapshot

Zeigt pro Komponente:

- ob sie physisch oder technisch vorhanden ist
- ob sie im aktuellen Pfad verwendet wird
- ob sie nur simuliert wird
- ob sie derzeit nicht implementiert ist

Komponenten:

- CPU
- GPU
- RAM
- Driver Layer
- HID / serial / TrueRNG
- WebSocket
- Quartz

### Teilbereich 2: Realtime Calibration

Zeigt frische Vorlaufdaten:

- EMF-Profil
- Entropiequelle
- Snapshot-/Driver-Layer-Kontext
- Systemlast

Zweck:

- den Analysekontext vor dem Lauf sichtbar machen
- nicht mystifizieren, sondern kalibrieren und dokumentieren

### Teilbereich 3: Mode Decision

Es gibt zwei Betriebsmodi:

#### `Standard`

- advisory only
- keine harten Blocker
- Hinweise statt Verbote

#### `Experte`

- zusaetzliche Freigabe- oder Blockregeln
- zum Beispiel:
  - geforderte echte Sensorik nicht vorhanden
  - angeforderte Realtime-Komponente nur simuliert
  - Harmonisierung verlangt einen Pfad, der aktuell nicht echt aktiv ist

### Teilbereich 4: Traceability Manifest

Der Preflight- und Hardwarekontext wird in den Run Trace Manifest uebernommen und in der ersten Ausbaustufe bereits in:

- Review
- Ergebnisdetails
- Export
- Auditkontext

sichtbar gemacht.

## Analyse vs. Harmonisierung

### Analyse

Die Hardware-/Realtime-Schicht soll Analyse zuerst in diesen Rollen unterstuetzen:

- Entropie-/Umgebungskontext
- EMF-/Systemzustandskontext
- Reproduzierbarkeitskennzeichnung
- Expertenmodus-Gates

Nicht Ziel des ersten Umbaus:

- jeder Hardwarekanal muss sofort aktiv das Analyseergebnis steuern

### Harmonisierung

Hier ist die Hardwareebene operativer.

Die Workbench soll deutlich sichtbar machen:

- welche Kanaele aktiv modulieren
- welche nur simuliert sind
- welche nicht verfuegbar sind

## UX-Sprache fuer Hardwarewahrheit

Beispielhafte Darstellung je Karte:

### CPU Timing

- Rolle: `Analysekontext + Harmonisierungsmodulation`
- Zustand: `Real aktiv`
- Charakter: `umgebungsabhaengig`

### GPU

- Rolle: `Status / optionale Entropie`
- Zustand: `teilweise real`
- Harmonisierung: `derzeit simuliert`

### Quartz

- Rolle: `keine aktive Integration`
- Zustand: `nicht implementiert`

Diese Sprachform ist professioneller als unscharfe Marketing- oder Mystifizierungslabels.

## Datenfluss

### Operatorfluss

1. Operator setzt Klient, Fokus, Profil.
2. Workbench ermittelt Runtime-, Quellen- und Hardwarekontext.
3. Workbench baut Review-Sicht.
4. Nach Freigabe startet der offizielle Produktionspfad.
5. Laufstatus wird in die Workbench rueckgespielt.
6. Resultate werden in Ergebnis-, Detail-, Harmonisierungs- und Exportphasen nutzbar gemacht.

### Nachvollziehbarkeit

Der Run Trace Manifest verbindet:

- Vorlaufkontext
- Laufkontext
- Ergebnisdarstellung
- Export
- Audit

## Fehler- und Randfallverhalten

1. Wenn Hardwarekomponenten nur simuliert sind:
   - im Standardmodus sichtbar markieren
   - im Expertenmodus optional blockieren
2. Wenn EMF nur Fallback ist:
   - klar als Software-/Fallback-Kontext anzeigen
3. Wenn Report-/Resultatdaten nicht zur Harmonisierung gekoppelt sind:
   - UI darf keine staerkere Kopplung behaupten als backend-seitig real existiert
4. Wenn Laufpfade divergieren:
   - Workbench zeigt den aktiven kanonischen Produktionspfad an

## Nicht-Ziele der ersten Ausbaustufe

1. sofortige Volluebernahme aller Radi144-Eingangsarten
2. sofortige Umstellung jeder Statusquelle auf eventbasierte Backend-Ereignisse
3. sofortige Aktivintegration nicht implementierter Hardware wie Quartz
4. sofortige fachliche Neuinterpretation der Analysealgorithmen

## Teststrategie

Die nachfolgende Umsetzung soll mindestens diese Ebenen abdecken:

1. `Workflow Registry`-Tests
2. `Hardware Truth Model`-Tests
3. `Run Trace Manifest`-Tests
4. Web-UI-Struktur- und Routingtests
5. Review-/Freigabe-Flow-Tests
6. Standard-vs-Expertenmodus-Tests
7. Ergebnis-/Export-Nachvollziehbarkeitstests

## Risiken

1. Zu viel Radi144 auf einmal zu kopieren wuerde Morphic ueberladen.
2. Wenn die Hardwarewahrheit nicht zentral modelliert wird, reproduziert die neue UI nur die alten Inkonsistenzen in schoenerer Form.
3. Wenn Review, Ergebnis und Abschluss nicht als eigene Phasen gedacht werden, bleibt der Umbau ein kosmetisches Wizard-Redesign.

## Empfehlung

Die Umsetzung soll mit einem `Operator Workbench` beginnen, nicht mit Einzelpatches an der bestehenden 8-Step-Shell.

Die erste Umbaustufe sollte sich auf diese Punkte konzentrieren:

1. kanonischer 10-Phasen-Flow
2. Review & Freigabe
3. Resume + Templates
4. Result Workspace
5. Hardware Truth Model
6. Standard-/Expertenmodus
7. Run Trace Manifest

Damit wird `Morphic V1` nicht nur visuell verbessert, sondern strukturell auf einen professionellen, intuitiven und nachvollziehbaren Operatorbetrieb ausgerichtet.
