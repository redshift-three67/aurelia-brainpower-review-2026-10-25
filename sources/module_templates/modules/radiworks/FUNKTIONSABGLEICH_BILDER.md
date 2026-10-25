# RadiWorks — Funktionsabgleich anhand der Original-Screenshots

> Grundlage: `Radiworks/screenshots/` — 3 Design-Vorlagen („Radiquant5") und
> 9 AetherOnePi-Betriebsaufnahmen (Aether_1–9). Bewertung: Umsetzbarkeit im
> Modul (Engine+Webapp) und in der Aurelia-Plattform. Stand 2026-08-29.
> **Datenschutz:** Die Aufnahmen enthalten reale Fallkennungen (Namen,
> Geburtsdaten, Orte). Diese werden hier bewusst NICHT reproduziert; der
> Befund ist selbst ein Compliance-Thema (siehe §3).

## 1. Design-Vorlagen (Radiquant5) — designseitige Befunde

| Befund | Bewertung für das Modul | Bewertung für Aurelia |
|---|---|---|
| Sanfter Mint→Lavendel-Verlauf, Serifen-Display („Resonanz finden. Balance erleben."), viel Weißraum | Stimmung ist mit den Layer-1-Tokens nachbaubar (Verlauf als `color-mix`-Gradient statt Hartfarben) | ✅ regelkonform, solange Akzente aus Basis abgeleitet — **umgesetzt als „Start"-Ansicht** (Hero, Pipeline-Karten, Drei Prinzipien; 2026-08-29) |
| Vier Phasenfarben: Erfassung (Petrol), Resonanz-Analyse (**Lila**), Harmonisierung (Grün), Reflexion (Salbei) | Als Modul-Akzente je Phase umsetzbar | ⚠️ Lila ist in Aurelia verboten („kein Lila", 08-ui-a11y) → Phase „Analyse" erhält eine regelkonforme Ableitung (z. B. Wellenreiter-Blau); Gold-Töne ebenfalls nur als entsättigte `color-mix`-Variante |
| **Workflow-Pipeline der 6 Module mit Rollen** (Design_Template_Neu_2): Radi144 „Erfassung: 144-Felder-Resonanz-Baseline" → **RadiWorks „Analyse: Korrelations-Engine — Mustererkennung und Korrelations-Matrix der Felder"** → RadiMorphic „NLS-Pattern-Analyse über 220 Profile" → RadiBlohm „Frequenz-Spektrum" → RadiThoms „Harmonisierung: Meridian-Profil, TCM + HRV" → RadiCopen „Reflexion: Copen-Rate auf Fibonacci-Basis, Synergy-Score" | Bestätigt die Rollenzuordnung; die AetherOnePi-Kernmaschine (Analyse/GV/Broadcast) ist das Substrat der „Korrelations-Engine" | ✅ Kernbefund für die Integration: Module tauschen Artefakte (AnalysisDraft, D18) — die 144-Felder-Baseline von Radi144 kann als Draft-Payload an RadiWorks übergeben werden |
| Hinweiskasten: „6 Module laufen mit deterministischen Mock-Engines (Phase 1), echte Compute-Pipelines später (FastAPI + GPU + Ollama)" | Deckungsgleich mit unserem Weg (seeded Default, echte Entropie opt-in) | ✅ „Debian"-Verweis ist historisch (Aurelia: Ubuntu 24.04.4) |
| Onboarding-Assistent, Schritt „Erscheinungsbild": **Circadian** (Tageszeit-adaptiv, empfohlen), Hell, Dunkel | Klein umsetzbar: JS-Scheduler setzt `data-mode` nach Tageszeit (oder CSS `light-dark()`) | ✅ **umgesetzt** — Modus-Knopf zirkelt Hell → Dunkel → Auto (Circadian, 18–8 Uhr dunkel) |
| Disclaimer-Box „kein Medizinprodukt …" + „© … DSGVO-konform · Made in the EU" | Bereits im Footer unseres Moduls | ✅ Pflichttext vorhanden |

## 2. Betriebsaufnahmen Aether_1–9 — Funktionsinventar & Machbarkeit

Legende Port-Status: ✅ vorhanden · 🟡 teilweise/vorbereitet · ❌ fehlt (Port-Erweiterung nötig)

| # | Funktion (Bild) | Port | Modul machbar? | Aurelia machbar? | Anmerkung |
|---|---|---|---|---|---|
| 1 | Dashboard „LAST CASES" (zuletzt geladene Fälle) | ❌ klein | ✅ | ✅ | Original `dashboardInformations.json` portieren; **in Aurelia pseudonymisiert** (case names enthalten heute reale Namen/Geburtsdaten → Art.-9-Thema) |
| 1 | Status-LEDs (PI, BROADCASTING, CLEARING, GROUNDING, COPYING) | 🟡 (WS-Status) | ✅ als WS-Events | ✅ | PI/COPYING sind Hardware-/Cache-Vorgänge → Ereignis-Äquivalente |
| 1 | Slider PACKAGES/CACHE/PROGRESS/QUEUE (Hotbits-Cache) | 🟡 | ✅ Zähler in EntropyProvider + `/entropy/status` | ✅ | |
| 1 | Broadcast-Queue mit Fortschrittsbalken | ✅ | ✅ | ✅ | Webapp zeigt Cards; Balken-Ansicht wie Original ergänzbar |
| 1 | RESONATED RATES (Zähler je Rate, sortiert) | ✅ (`resonanceTotals`) | ✅ UI-Tabelle ergänzen | ✅ | |
| 1 | GV-Graph + „AUTO MODE ON — GV = n" (Auto-Modus) | ❌ | ✅ (GV-Serie + Chart) | ✅ | Auto-Modus = wiederholte GV-Züge; Uhr bleibt Server (Hard Rule 4) |
| 2 | Session NEW/LOAD/SAVE + NAME/DESCRIPTION | ✅ `/cases` | ✅ UI erweitern | ✅ + Pflichtfelder `tenant_id`/`client_id` | |
| 2 | EDIT CASE (Session-Dialog) | ❌ | ✅ | ✅ | |
| 2 | ESSENTIAL QUESTIONS (GV-Orakel) | ❌ (P1-Punkt 6) | ✅ | ✅ | Ausgabe durch CopyGuard (Wellbeing-Formulierungen) |
| 3 | Settings-Toggles (10 Booleans; neu entdeckt: `notification.after.broadcast`, `use.overlay`) | 🟡 (Store ja, API fehlt) | ✅ → `GET/PUT /settings` ergänzen | ✅ (plattformseitig admin, Flags fail-closed) | Settings-Schema identisch portiert |
| 4 | Analyse-Tabelle: NO/EV/RATE/POTENCY/LVL/HIT/GV/GV_RE/REC | 🟡 (EV/Level/Potenz ✅; GV-Runde fehlt) | ✅ | ✅ | GV-Runde (Enter-Logik) als API + Webapp; recurring/GV_RE vorhanden |
| 4 | **Eigene Raten-Datenbanken** („Raphael_WS_Physis.txt", deutsche Körperraten) | ✅ (Parser + Präfix-Matching) | ✅ | ✅ | Kategorien = Präfixe, genau wie Original |
| 4 | Zeilenaktion „BROADCAST" je Rate | ✅ (`POST /broadcast`) | ✅ | ✅ | direkter Operator-Befehl, D18-konform |
| 4 | „GOOGLE"-Link je Rate | ❌ absichtlich | ⚠️ technisch trivial | **❌ ablehnen** | sendet Raten-Text an Google → Datenaustritt; Ersatz: Materia-Medica-URL aus der Rate (Spalte URL) — wie im Original vorgesehen |
| 4 | Pagination (1–5) | ❌ trivial | ✅ | ✅ | |
| 4 | „GENERAL VITALITY: 888 (runs = 1708)" | ❌ klein | ✅ | ✅ | |
| 4 | TRAINING MODE [START/UNCOVER] | ❌ klein | ✅ (`selectTrainingRate` portieren) | ✅ | |
| 4 | STATISTICS | ❌ | ✅ (Fallstatistik-Generator portieren) | ✅ | |
| 4 | CLIPBOARD (Analyse + KI-Interpretationsprompt) | ❌ | ✅ (Zwischenablage solo) | ✅ **als Draft-Notiz via lokales LLM** (Aurelia CopyGuard-LLM im RAM, D13/C02) — **kein Cloud-LLM** | passt exakt in Aurelias Architektur |
| 4 | CLEAR / GROUNDING / BROADCAST MIX / AUTO ON/OFF | 🟡 | ✅ | ✅ | Grounding-Signatur portiert; MIX = Festlegung 2 |
| 5 | IMAGE-Tab (paste/load/layers/analyze/broadcast/MD5) | ❌ | ✅ (Upload, Schicht-GV-Analyse, MD5) | ⚠️ mit Auflagen | Zeugen-Bilder = sensible Artefakte: `no-store`, kein CDN, keine KI-Verarbeitung ohne Freigabe; **MD5 ≙ `input_hash` im Passport** — natürliche Passung |
| 6 | RATES/Stick-Pad („PRESS AND HOLD SPACE …") | ❌ | ✅ (Pointer/Key-Hold → `(x,y)` → `/stickpad`) | ✅ | StickPad-Algorithmus ist in FUNKTIONSANALYSE §6 vollständig dokumentiert |
| 7 | AREA (paste/load/clear/SCAN FOR TARGET/AGRICULTURE) | 🟡 (`/search-anomaly` ✅) | ✅ Heatmap-UI über Bild | ✅ | AGRICULTURE = eigene Raten-Präfix-Datenbanken |
| 8 | HOTBITS-Webcam (SHOW/SET WEBCAM, GET/STOP, WEBCAM[n]) | 🟡 (Provider-Kette steht, Webcam-Quelle fehlt) | ✅ `getUserMedia` → Framedifferenz → Original-`hotbits_*.json` → `/entropy/acquire` | ⚠️ Hocheingriff: Kamera = biometrienahe Quelle → explizite Einwilligung, **keine Bildspeicherung**, nur Zufallswerte; bis Klärung nur Labor-Mandant | Original-Dateiformat bleibt kompatibel |
| 9 | Broadcast NOW/LIST/STOP CURRENT/STOP ALL/Resonanzliste + SIGNATURE/SECONDS/MULTIPLIER | ✅ vollständig | ✅ | ✅ | |
| 9 | Radionic-Card-Kreise (konzentrische Ellipsen in Panels) | ✅ (Canvas-Shapes) | ✅ + CardMaker-PNG später | ✅ | |
| — | PEGGOTTY-Tab (RadionicScript-Interpreter) | ❌ | ✅ portierbar | ✅ später | Mini-Skriptsprache, FUNKTIONSANALYSE §10 |

## 3. Compliance-Befunde aus den Aufnahmen (wichtig)

1. **Fallnamen mit Geburtsdaten/Orten als Dateinamen** (`cases/*.json`) — reale
   Personenbezug in Klartext-Pfaden. Im Modul-Solo-Betrieb okay ( lokale
   Datei), in Aurelia zwingend: Pseudonym-Dateinamen + `(tenant_id,
   client_id)`-Scoping (Hard Rule 8) — die JSON-Verträge tragen die Felder
   bereits. Konvention für den Port ab Stufe 4: Dateiname = Case-ID (UUID),
   Anzeige-Name im Dokument.
2. **GOOGLE-Links** — Datenaustritt; in der Aurelia-Variante ersetzen
   (Materia-Medica-URL), im Solo-Betrieb optional deaktivierbar.
3. **Webcam-Entropie** — nur mit Einwilligungsoberfläche; keine Frame-Speicherung.
4. Die aufgezeichneten Screenshots selbst enthalten Art.-9-nahe Daten →
   Ordner `screenshots/` nicht in geteilte Repos/Clouds übernehmen (gilt auch
   für `Radiworks`-Repo: Ordner liegt im Git-Bestand → prüfen, ob gitignored
   werden soll).

## 4. Fazit

**Alle sichtbaren Original-Funktionen sind im Modul umgesetzt** (Stand
2026-08-29, Stufe 3 abgeschlossen): ① GV-Runde + runs-Zähler ✅,
② Essenzielle Fragen ✅, ③ Settings-API + Toggles ✅, ④ Stick-Pad ✅,
⑤ Analyse-View (Pager 21, HIT, GV-Graph, Auto-Modus, Zeilen-Broadcast) ✅,
⑥ Fall-Statistik ✅, ⑦ Bildschichten + Area-Scan ✅, ⑧ Webcam-Entropie
(Einwilligung, keine Bildspeicherung) ✅, ⑨ PEGGOTTY-Interpreter ✅ — dazu
die Fälle-Verwaltung (Aether_2) und die Start-Pipeline-Ansicht. Die drei
bewussten Anpassungen bleiben: GOOGLE-Links ersetzt (Datenaustritt),
Zeugen-Hash SHA-256 statt MD5 (Passport-Familie), Webcam nur mit
Einwilligungsoberfläche. Der größte Erkenntnisgewinn bleibt die
**Pipeline-Rolle** aus Design 2: RadiWorks ist als Korrelations-Engine das
Empfängerartefakt der Radi144-Baseline — der Übergabeweg ist durch den
AnalysisDraft (D18) vorgezeichnet.
