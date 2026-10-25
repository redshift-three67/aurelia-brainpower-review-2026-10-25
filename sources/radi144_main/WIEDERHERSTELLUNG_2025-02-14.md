# WIEDERHERSTELLUNGS-UPDATE — Resonanzmatrix Analyse-Workflow
## Zeitstempel: 14. Februar 2026, 17:27 Uhr MEZ (UTC+01:00)

---

## 1. PROJEKT-ÜBERSICHT

**Projekt:** 12×12 Resonance Matrix Engine — Web-Frontend Workflow
**Verzeichnis:** `c:\Users\Administrator\Documents\12x12\`
**Server:** FastAPI Backend auf `http://localhost:8000`
**Frontend:** Statischer Fileserver auf `http://localhost:8090`
**Einstiegspunkt:** `http://localhost:8090/user_workflow.html`

### Betroffene Dateien (3 Dateien, alle im Root-Verzeichnis):

| Datei | Zeilen | Beschreibung |
|---|---|---|
| `user_workflow.html` | 390 | Vollständige 10-Schritt Workflow-Seite |
| `user_workflow.css` | 433 | Heilsames Naturheilpraxis-Design (komplett neu) |
| `user_workflow.js` | 1283 | Gesamte Workflow-Logik inkl. aller Features |

---

## 2. DESIGN-SYSTEM: "Heilsames Design"

### Farbpalette (Light Mode)
```
--bg:            hsl(40 30% 97%)     → Warmes Elfenbein (Hintergrund)
--bg2:           hsl(40 25% 95%)     → Karten-Hintergrund
--primary:       hsl(145 25% 36%)    → Salbeigrün (Primärfarbe)
--primary-light: hsl(145 22% 50%)    → Helles Salbeigrün
--primary-bg:    hsl(145 30% 95%)    → Grüner Hintergrund-Ton
--sand:          hsl(35 35% 85%)     → Warmer Sand (Sekundär)
--accent:        hsl(18 45% 55%)     → Terracotta (Akzent)
--green:         hsl(145 50% 40%)    → Semantisch: Erfolg
--amber:         hsl(35 85% 55%)     → Semantisch: Warnung
--red:           hsl(0 65% 50%)      → Semantisch: Fehler
--purple:        hsl(270 40% 60%)    → Semantisch: Info
--pink:          hsl(340 60% 65%)    → Semantisch: Amplifier
```

### Typografie
```
Überschriften: Playfair Display (400–700), Georgia, serif
Fließtext:     Source Sans 3 (300–700), system-ui, sans-serif
Code/Mono:     JetBrains Mono, Fira Code, Consolas, monospace
```

### Google Fonts Import (in HTML Zeile 7)
```html
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Source+Sans+3:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

### Schatten-System
```
--shadow-soft:     0 4px 20px -4px hsl(145 20% 30% / 0.08)
--shadow-card:     0 8px 30px -8px hsl(145 20% 30% / 0.1)
--shadow-elevated: 0 20px 50px -15px hsl(145 20% 20% / 0.15)
```

### Animationen
- `fadeIn` — Opacity + translateY(16px) → 0
- `slideUp` — Opacity + translateY(20px) → 0
- `scaleIn` — Opacity + scale(0.96) → 1
- `btnPulse` — Box-shadow pulsierend auf Primary-Buttons
- `pulse` — API-Status-Punkt pulsierend
- `spin` — Analyse-Spinner 360°

---

## 3. WORKFLOW: 10 Schritte (1:1 mit generate_matrix.ps1)

| Step | data-step | Name | Icon-Klasse | Beschreibung |
|---|---|---|---|---|
| 1 | 0 | Willkommen | si-cyan | Übersicht, API-Check, Template-Verwaltung |
| 2 | 1 | Klient | si-purple | Pflicht: Vorname*, Nachname*, Geburtsdatum*, Geburtsort*; Optional: Zeit, E-Mail, Symptom, Geburtsplanet, Notizen |
| 3 | 2 | Fokus | si-amber | Fokus-Textarea (Multi-Fokus ;-getrennt), Preset-Buttons, Fokus-History-Chips |
| 4 | 3 | Config | si-green | Matrix (12/24/36), Modus (Quantum/Precision), Gewichtung, Symmetrie, Palette, EMF-Toggle, HRV-Toggle, Amplifier |
| 5 | 4 | EMF | si-red | EMF-Umfeld-Messung (wenn aktiviert): Index, Entropy, Jitter, Counter-Frequencies |
| 6 | 5 | Analyse | si-cyan | Zusammenfassung aller Eingaben, "Analyse starten"-Button, Fortschrittsbalken |
| 7 | 6 | Matrix | si-green | Farbige Matrix-Visualisierung, Score, Rechenzeit, Hardware, Legende |
| 8 | 7 | Details | si-purple | Kerndaten, Technische Details, EMF-Ergebnis, Roh-JSON |
| 9 | 8 | Harmonie | si-pink | Impuls/Pausen-Konfiguration, Solfeggio, Audio, Timer, Zyklen, Matrix-Animation |
| 10 | 9 | Export | si-amber | JSON, CSV, Zwischenablage, PDF-Bericht, Excel/CSV, Neue Analyse, Zurück-Buttons |

---

## 4. FEATURE-LISTE (vollständig implementiert)

### 4.1 Session-Persistenz (localStorage)
- **Key:** `resonance_session`
- **Auto-Save:** Debounced bei `input` (500ms) und `change` (300ms) Events
- **Restore:** Automatisch beim Seitenaufruf (`restoreSession()` in INIT)
- **Reset:** `localStorage.removeItem("resonance_session")` bei `resetWorkflow()`
- **Felder:** firstName, lastName, birthDate, birthPlace, birthTime, birthPlanet, email, mainSymptom, notes, focusText, matrixSize, calcMode, focusWeight, symmetry, palette, amplifier, emfToggle, hrvToggle, savedAt

### 4.2 Fokus-History
- **Key:** `resonance_focus_history`
- **Max:** 42 Einträge (FIFO)
- **Speicherung:** Bei jeder erfolgreichen Analyse (`saveFocusToHistory()`)
- **Anzeige:** Gestrichelte Chips unter den Presets (max. 15 angezeigt, ohne Standard-Presets)
- **Klick:** Fügt Fokus per Semikolon an bestehenden Text an

### 4.3 Multi-Fokus
- **Trenner:** Semikolon (;)
- **Max:** 42 Einträge pro Analyse
- **FIFO:** Bei >42 werden die ältesten automatisch entfernt
- **Counter:** Live-Anzeige der Fokus-Anzahl unter dem Textarea
- **Platzhalter:** Erklärt Semikolon-Syntax im Textarea-Placeholder

### 4.4 Template-Historie
- **Key:** `resonance_templates`
- **Max:** 21 benannte Templates
- **Modal:** Overlay mit Liste, Laden/Löschen-Buttons, Name-Input + Speichern
- **Zugang:** "Templates verwalten"-Button auf Willkommensseite (Step 1)
- **Zähler:** Zeigt Anzahl gespeicherter Templates auf Startseite
- **ESC:** Schließt das Modal

### 4.5 Harmonisierung (Web Audio API)
- **Impuls/Pause:** Konfigurierbar (Standard 14s/14s)
- **Dauer:** Faktor × 21 Minuten (1–21)
- **Solfeggio:** 528 Hz, 429.62 Hz, 432 Hz (Standard)
- **Audio-Layers:** Base-Frequenz, Quinte, Solfeggio, Oktave darunter, Amplifier-Frequenz
- **Visual:** Matrix wird im IMPULS angezeigt, "PAUSE — Stille & Integration" im Pause-Modus
- **Timer:** Countdown mit Restzeit und Zyklen-Anzeige
- **Recording:** MediaRecorder API, WebM-Format, automatischer Export-Prompt bei Stop

### 4.6 Amplifier (9 Stück, 1:1 mit PS1)
```javascript
rosenquarz: 350 Hz, amethyst: 480 Hz, bergkristall: 528 Hz,
schwarzer_turmalin: 174 Hz, schungit: 196 Hz (Standard-Vorauswahl),
orgonit_pyramide_schungit: 7.83 Hz, orgonit_pyramide_bergkristall: 7.83 Hz,
lapislazuli: 448 Hz, selenit: 560 Hz
```

### 4.7 Export-Optionen
| Format | Funktion | Beschreibung |
|---|---|---|
| JSON | `exportJSON()` | Komplettes `analysisResult` als `.json` |
| CSV | `exportCSV()` | Matrix-Daten Komma-getrennt als `.csv` |
| Zwischenablage | `copyToClipboard()` | JSON in Clipboard (mit Fallback) |
| PDF-Bericht | `exportPDF()` | Text-Report mit Klient, Config, Score, Matrix, Rates-String als `.txt` |
| Excel/CSV | `exportExcel()` | UTF-8 BOM, Semikolon-getrennt für deutsche Excel-Versionen als `.csv` |
| Audio | `exportSessionAudio()` | Harmonisierungs-Audio als `.webm` (nach Stop, per Confirm-Dialog) |

### 4.8 EMF-Kompensation
- **API-Ablauf:** POST `/emf/enable` → 1.5s Pause → GET `/emf/profile`
- **Daten-Extraktion:** `data.profile.composite_emf_index` (nested!)
- **Status-Check:** GET `/emf/status` → `data.current_profile.composite_emf_index`
- **Anzeige:** EMF-Index, Entropy Score, Timing Jitter, Low-Noise Fenster, Qualität, Empfehlung, Counter-Frequencies

---

## 5. HTML-STRUKTUR (user_workflow.html — 390 Zeilen)

```
<!DOCTYPE html>
├── <head>
│   ├── Google Fonts (Playfair Display + Source Sans 3)
│   └── user_workflow.css
├── <body>
│   ├── .header (Badge, H1, Subtitle, API-Status)
│   ├── nav.snav (Stepper-Navigation, 10 Schritte)
│   ├── main.main
│   │   ├── .op (Fortschrittsbalken)
│   │   ├── #tplModal (Template-Modal Overlay)
│   │   ├── section[data-step=0] – Willkommen
│   │   │   ├── Info-Grid (4 Schritte)
│   │   │   ├── System-Anforderung + sysInfo
│   │   │   └── Templates & Konfigurationen
│   │   ├── section[data-step=1] – Klienten-Daten
│   │   │   ├── Pflichtfelder (Vorname, Nachname, Geburtsdatum, Geburtsort)
│   │   │   └── Optionale Felder (Geburtszeit, E-Mail, Symptom, Geburtsplanet, Notizen)
│   │   ├── section[data-step=2] – Fokus & Intention
│   │   │   ├── Fokus-Textarea (Multi-Fokus, Placeholder)
│   │   │   ├── focusCount (Live-Counter)
│   │   │   ├── Preset-Grid (12 Standard-Presets)
│   │   │   └── focusHistorySection (Letzte Fokusse Chips)
│   │   ├── section[data-step=3] – Analyse-Konfiguration
│   │   │   ├── Matrix & Modus (12/24/36, Quantum/Precision, Gewichtung)
│   │   │   ├── Darstellung (Symmetrie, Palette)
│   │   │   ├── EMF-Toggle, HRV-Toggle
│   │   │   └── Amplifier-Dropdown (9 Optionen)
│   │   ├── section[data-step=4] – EMF-Umfeld-Analyse
│   │   ├── section[data-step=5] – Zusammenfassung & Start
│   │   ├── section[data-step=6] – Ergebnis: Matrix
│   │   ├── section[data-step=7] – Ergebnis: Details
│   │   ├── section[data-step=8] – Harmonisierung
│   │   │   ├── harmConfigCard (Impuls, Pause, Dauer, Solfeggio, Audio)
│   │   │   └── harmRunCard (Timer, Phase, Matrix, Info, Stop-Button)
│   │   └── section[data-step=9] – Export & Abschluss
│   │       ├── JSON, CSV, Zwischenablage (3er Grid)
│   │       ├── PDF-Bericht, Excel-Export (2er Grid)
│   │       └── Neue Analyse, Matrix ansehen, Harmonisierung
│   └── .btn-group (Zurück/Weiter)
└── <script src="user_workflow.js">
```

---

## 6. CSS-MODULE (user_workflow.css — 433 Zeilen)

| Zeilen | Modul | Beschreibung |
|---|---|---|
| 1–55 | Root-Variablen | Farben, Fonts, Schatten, Spacing |
| 57–76 | Body & Typography | Hintergrund-Gradienten, Font-Smoothing, H-Tags |
| 77–102 | Header | Badge, H1, API-Status, Pulse-Animation |
| 104–129 | Navigation | Sticky Nav, Steps, Nummern, Connector |
| 131–136 | Main & Animations | Container, fadeIn, slideUp, scaleIn |
| 138–154 | Step Header | Icons (6 Farb-Varianten), H2, Subtitle |
| 156–167 | Cards | Basis, Hover, Card-Title, Grid 2/3 |
| 169–174 | Progress Bar | Fortschrittsbalken mit Gradient |
| 176–195 | Forms | Input, Textarea, Select, Focus-States |
| 197–211 | Radio Buttons | Vertikale/horizontale Gruppen, Checked-State |
| 213–225 | Toggle Switches | Custom-Checkbox mit Slide-Animation |
| 227–235 | Preset Buttons | Pill-Buttons, Hover mit Primary-Farbe |
| 237–238 | Validation | Rot gefärbte Fehlermeldungen |
| 240–250 | Info Grid | Willkommens-Info-Karten mit Hover-Lift |
| 252–256 | Metric Rows | Zusammenfassung/Details Key-Value-Paare |
| 258–282 | Buttons | Standard, Primary, Disabled, Large, Glow |
| 284–294 | Analysis Progress | Spinner, Status-Text, Fortschrittsbalken |
| 296–312 | Matrix | CSS-Grid, Zell-Hover, Legende |
| 314–322 | Score Row | Score-Karten mit Mono-Font |
| 324–330 | Code Output | Pre-Block für JSON |
| 332–339 | Card Action | Klickbare Export-Karten |
| 341–358 | EMF Status | EMF-Grid, Solfeggio-Mini-Items |
| 360–372 | Harmonizer | Timer, Phase-Labels, Blank-Matrix |
| 374–411 | Template Modal + Focus History | Modal-Overlay, Items, Buttons, Chips |
| 413–423 | Responsive | ≤768px Anpassungen |
| 425–433 | Print | A4-Druck, versteckte UI-Elemente |

---

## 7. JAVASCRIPT-ARCHITEKTUR (user_workflow.js — 1283 Zeilen)

| Zeilen | Modul | Funktionen |
|---|---|---|
| 1–52 | Config & Constants | API_BASE, TOTAL_STEPS, STEPS[], AMP_FREQS{}, FOCUS_PRESETS[] |
| 54–111 | Navigation | buildNav(), updateProgress(), goToStep(), navigate() |
| 113–139 | Validation | validateCurrentStep() — Pflichtfelder + Fokus |
| 141–154 | Focus Presets | buildPresets() — 12 Standard-Presets |
| 156–179 | API Check | checkAPI() — EMF-Status-Endpoint |
| 181–245 | EMF Status | loadEMFStatus() — Enable, Profile, Counter-Frequencies |
| 247–288 | Summary | buildSummary(), formatDate() — inkl. Geburtsplanet |
| 290–380 | Analysis | startAnalysis() — API-Request, Progress, Fokus-History-Save |
| 382–443 | Matrix Render | renderMatrix() — Grid, Farben, Legende, Score-Row |
| 445–491 | Details Render | renderDetails() — Kern, Tech, EMF, Raw-JSON |
| 493–533 | Exports | exportJSON(), exportCSV(), downloadBlob(), copyToClipboard() |
| 535–556 | Reset | resetWorkflow() — Felder leeren, localStorage löschen |
| 558–631 | Session Persist | saveSession(), restoreSession(), Auto-Save Debounce |
| 633–726 | PDF/Excel Export | exportPDF(), exportExcel() — Text/CSV-basiert |
| 728–989 | Harmonizer | startHarmonizer(), harmScheduleNext(), harmDrawMatrix(), harmClearMatrix(), harmUpdateInfo(), harmPlayAudio(), harmStopAudio(), stopHarmonizer() |
| 991–1046 | Fokus-History | loadFocusHistory(), saveFocusToHistory(), renderFocusHistory() |
| 1048–1073 | Multi-Fokus | updateFocusCount() + DOMContentLoaded Listener |
| 1075–1216 | Template-Historie | loadTemplates(), saveTemplates(), openTplModal(), closeTplModal(), saveTemplate(), loadTemplate(), deleteTemplate(), renderTplList(), updateTplCount() |
| 1218–1264 | Audio Recording | startAudioRecording(), stopAudioRecording(), exportSessionAudio() |
| 1266–1273 | Keyboard Nav | ArrowLeft/Right, ESC (Harmonizer + Modal) |
| 1275–1282 | Init | buildNav, buildPresets, updateProgress, checkAPI, restoreSession, renderFocusHistory, updateTplCount |

---

## 8. localStorage KEYS

| Key | Typ | Max | Beschreibung |
|---|---|---|---|
| `resonance_session` | Object | 1 | Aktuelle Session (Auto-Save) |
| `resonance_focus_history` | Array<string> | 42 | Letzte verwendete Fokusse (FIFO) |
| `resonance_templates` | Array<Object> | 21 | Benannte Konfigurationen |

---

## 9. API-ENDPUNKTE (verwendet vom Frontend)

| Methode | Endpoint | Verwendung |
|---|---|---|
| GET | `/api/v1/emf/status` | API-Check (Step 1), EMF-Modul-Status |
| POST | `/api/v1/emf/enable` | EMF aktivieren (Step 5) |
| GET | `/api/v1/emf/profile` | EMF-Profil abrufen (Step 5) |
| POST | `/api/v1/analyze-matrix` | Matrix-Analyse starten (Step 6) |

### Request-Payload (`/analyze-matrix`):
```json
{
  "client_data": {
    "first_name": "...", "last_names": ["..."],
    "birth_date": "YYYY-MM-DD", "birth_place": "...",
    "birth_time": "HH:MM" | null,
    "email": "..." | null, "main_symptom": "..." | null, "notes": "..." | null
  },
  "focus": "...",
  "matrix_size": 12 | 24 | 36,
  "calculation_mode": "quantum" | "precision",
  "focus_weight": "Deaktiviert" | "Sanft" | "Normal" | "Stark",
  "symmetry": "none" | "horizontal" | "quadrant",
  "palette": "..." | null,
  "emf_compensate": true | false,
  "hrv_sim": true | false,
  "use_quantum": true,
  "use_cuda": true
}
```

---

## 10. BEKANNTE EINSCHRÄNKUNGEN / NOCH OFFEN

| Feature | Status | Grund |
|---|---|---|
| Gruppen-/Geo-/Bild-Analyse | ❌ Nicht implementiert | Braucht Backend-API-Endpoints |
| Datenbank-Vorwahl & Ranking | ❌ Nicht implementiert | Server-seitige DB nötig |
| `dev_results.txt` Archivierung | ❌ Nicht implementiert | Server-Dateisystem nötig |
| Echtes PDF (mit Grafik) | ⚠️ Nur Textdatei | jsPDF-CDN wäre nötig für echtes PDF |
| Echtes XLSX (Binary) | ⚠️ Nur CSV | SheetJS wäre nötig für echtes XLSX |
| Session-Audio als WAV | ⚠️ Nur WebM | WAV-Encoding im Browser aufwändig |

---

## 11. SERVER-STARTANWEISUNGEN

```powershell
# 1. Backend starten (FastAPI)
cd c:\Users\Administrator\Documents\12x12
python main.py
# → Läuft auf http://localhost:8000

# 2. Frontend starten (Statischer Fileserver)
cd c:\Users\Administrator\Documents\12x12
python -m http.server 8090
# → Läuft auf http://localhost:8090

# 3. Browser öffnen
# → http://localhost:8090/user_workflow.html
```

---

## 12. WIEDERHERSTELLUNGS-CHECKLISTE

Falls die Dateien wiederhergestellt werden müssen, sind folgende 3 Dateien der komplette Stand:

- [ ] `user_workflow.html` — 390 Zeilen, UTF-8
- [ ] `user_workflow.css` — 433 Zeilen, UTF-8
- [ ] `user_workflow.js` — 1283 Zeilen, UTF-8 (1 leere Zeile am Ende = 1283 total)

**Abhängigkeiten:**
- Google Fonts CDN (Playfair Display + Source Sans 3) — geladen in HTML Zeile 7
- FastAPI Backend auf localhost:8000 — muss laufen für API-Calls
- Kein NPM, kein Build-Prozess — reines Vanilla HTML/CSS/JS

---

*Erstellt am 14.02.2026 um 17:27 MEZ — Cascade AI Pair Programming Session*
