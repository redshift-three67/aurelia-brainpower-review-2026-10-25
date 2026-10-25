# FUNKTIONSANALYSE — AetherOnePi 2.2.0 (Portierungsbasis für Python/HTML)

> **Quelle:** Vollständige CFR-Dekompilierung von `de/isuret/polos/AetherOnePi/` (128 Klassen → 105 Java-Dateien in `decompiled/`).
> **Status:** Referenzdokument für die 1:1-Portierung der Kernengine nach Python und den Umbau als HTML-Modul in die Aurelia-Plattform.
> **Alle Angaben sind aus dem Bytecode verifiziert, nicht rekonstruiert.** Dateipfade relativ zu `Radiworks/`.

---

## 1. Systemidentität

| Attribut | Wert |
|---|---|
| Anwendung | AetherOnePi — Digitale Radionik (Open Source, Autor Isuret Polos) |
| Koordinaten | `de.isuret.polos:AetherOnePi:2.2.0`, Main-Class `de.isuret.polos.AetherOnePi.Main` |
| Original-Stack | Java 24 · Processing (PApplet+JOGL GUI) · Javalin 6.6 (Jetty 11) · Jackson 2.12 · Nitrite-DB · Lucene · Pi4J 1.2 |
| Zwei Frontends | `ui/` = Angular-Build (2 MB, mit OpenLayers-Karte) · `html/` = Vue 3 + Axios (Materia-Medica-Suche + Settings) |
| Zielelement | Raspberry Pi mit LED-Hardware (9 GPIO-Pins), Webcam-Hotbits, `/dev/hwrng` |

**Architekturprinzip:** Desktop-GUI (Processing) ist Host *und* Client zugleich; sie startet embedded einen Javalin-Server, der dieselben In-Memory-Zustände (aktueller Case, aktuelle Analyse) per REST/WebSocket nach außen spiegelt.

---

## 2. Startablauf (`AetherOneUI.setup()`, decompiled/…/processing2/AetherOneUI.java:171)

1. `Gui`- und `Settings`-Konfiguration laden (`config/Gui.json`, `config/Settings.json`); Fenstergröße Default 1285×721.
2. `HotbitsHandler` erzeugen (legt `hotbits/`-Ordner an) → dient als `IHotbitsClient`.
3. `AnalysisService` erzeugen, Hotbits-Client injizieren; lädt `data/radionics/HOMEOPATHY/clarkeMateriaMedica.json`.
4. `AetherOneEventHandler` (alle UI-Events), `GuiElements` (Tabs/Buttons/Slider).
5. 10 Tabs: `SESSION, SETTINGS, ANALYZE, IMAGE, CARD, RATES, PEGGOTTY, AREA, HOTBITS, BROADCAST` + `default`-Dashboard.
6. `HotbitsHandler.loadHotbits()` startet Cache-Thread (Abschnitt 4).
7. `AetherOneServer(Location.CLASSPATH, this)` — embedded Webserver startet.
8. Optional: `watchlist.csv` einlesen (Zeilen = Rate[,SubRate,…]), Analyse + GV je Rate, Warnung falls GV < 500.

---

## 3. Entropie-Subsystem „Hotbits" (Kern der gesamten Engine)

**Jede „Messung" im System ist ein Zufallszugriff.** Die Qualität der Entropiequelle bestimmt das gesamte Systemverhalten. Vier Quellen mit klarer Priorität:

### 3.1 `HotbitsHandler` (Runtime-Pfad der Desktop-App) — `processing2/hotbits/HotbitsHandler.java`
- Cache: `List<Integer> hotbits` aus Dateien `hotbits/hotbits_*.json` (`{"integerList":[…]}`), max. 4.000.000 Ints; Dateien werden nach dem Laden **gelöscht**.
- Hintergrund-Thread: alle 7 s Nachladen aus Ordner, wenn Cache < 1000.
- **Ziehung:** `new Random(hotbits.remove(0)).nextInt(range)` — der Hotbit-Integer wird als **Seed für Java-Random** verwendet (nicht direkt als Zufallszahl!). Fallback: `SecureRandom`.

### 3.2 Webcam-Erfassung (`AetherOneUI.startWebCamHotbitAcquire()`, Zeile 364)
- Kamera-Frames byteweise vergleichen: heller→`1`, dunkler→`0`; 24 Bits → Integer; Veredelung `int + new Random(int).nextInt(100000)`; Deduplizierung; Pakete à 10.000 → `hotbits_*.json`; Ziel: 20.000 Pakete.

### 3.3 `HotbitsClient` (Server-Pfad, alternative Implementierung) — `hotbits/HotbitsClient.java`
- Primärquelle: `/dev/hwrng` (Hardware-RNG des Pi) über `HotbitsAccessor.getBytes()` → Pakete à 1000 Bytes als `hotbits_YYYYMMDD_HHmmssSSS.dat`.
- Seed-Quelle: `https://www.random.org/integers/?num=1000&min=1&max=1000000&col=1&base=10&format=plain&rnd=new` (Cache-Liste).
- `getSeed(n)` = Summe von n Bytes; Ziehung `new Random(System.currentTimeMillis() + seed)`.
- Pseudo-Mode bei Quellenausfall → `SecureRandom`.
- Konfiguration (`application.properties`): `packageSize=1000, storageSize=100, hotbitsServerMode=true, hotbitsServerURLs=http://192.168.178.60:8080/`.

### 3.4 `hrng/HrngGenerator` — Windows/AMD: native `hrngAmd.dll` (Ryzen-RNG), erzeugt dieselben JSON-Pakete.

> **Portierungsentscheidung (Python):** Interface `IHotbitsClient` → `getBoolean() : bool`, `getInteger(bound) : int`, `getInteger(min,max) : int`. Python-Seitige Umsetzung: Provider-Kette `HardwareRNG → Qrng (random.org/lokal) → Webcam → secrets.SystemRandom`. **Seed-Semantik erhalten:** Zufallsquelle liefert Seeds; daraus wird deterministisch (`random.Random(seed)`) gezogen — dieses zweistufige Verfahren ist funktionaler Bestandteil (verdichtet/quält die Rohentropie) und muss 1:1 nachgebildet werden.

---

## 4. Analyse-Algorithmus (`AnalysisService.analyseRateList`, service/AnalysisService.java:49)

```
INPUT:  Iterable<Rate>  (aus Raten-DB), Settings
maxValue = 1000 wenn settings["analysis.very.high.max.hit"] sonst 100

1. Liste klonen, MIT HOTBITS mischen (shuffleRateList: remove(getInteger(0, size-1)))
2. Selektionsphase: n = size/10, geklemmt auf [120, 5000]
   n-mal: idx = getInteger(0, rest-1); Rate entfernen; ratesValues[name] = 0
3. Anreicherungsphase (bis Abbruch):
   für jede Rate in Map (Einfügereihenfolge):
       energeticValue += getInteger(10)          # 0..9
       biggestLevel = max(biggestLevel, energeticValue)
       wenn biggestLevel >= maxValue → Abbruch
   (pro Durchlauf: GPIO CONTROL togglen + 30 ms Delay, falls Pi)
   trials zählt jede Einzelziehung
4. Mapping → RateObject(energeticValue, name, url)   # Name-Format "NAME\tURL" (TAB!)
5. sort() absteichend nach energeticValue (Gleichstand: Name asc), shorten(105)
6. je Rate:
   a) potency = analyzePotency()
   b) level: 12 Fächer auf 0; 100×: level = getInteger(1,12); wenn getBoolean(): Fächer+1;
      Rate.level = Fächer mit höchstem Zähler (argmax)
OUTPUT: AnalysisResult { rateObjects[105], numberOfTrials }
```

### 4.1 General Vitality (`checkGeneralVitality`, Zeile 141)
```
gv = max von 3× getInteger(1000)          # 0..999
wenn gv > 950:
    roll = getInteger(100)
    solange roll >= 50:  gv += roll;  roll = getInteger(100)   # Bonus-Spirale
```
`checkPercentage()` (UI): max von 3× `getInteger(100)` → 0–100 %.
`searchAnomaly(w,h)`: w×h-Matrix von GV-Werten (Flächen-Scan).

### 4.2 Potenz-Analyse (`analyzePotency`, Zeile 172)
- 100 Kandidaten: Typ aus `[D, C, LM, Q, FLUX]`
  - D: Stärke aus `[0,1,3,4,6,12,30,200]`
  - C/FLUX: aus `[0,1,3,6,12,30,200,1000,10000,50000,100000,1000000]`
  - LM/Q: `getInteger(1,30)`
- Akkumulator über Positionen 0–99: solange kein Kandidat > 77 Treffer hat: `pos=getInteger(0,99)`, Zähler++, bei >77 → Rückgabe `"TYPE STRENGTH"`.

### 4.3 GV-Runde über Analyseergebnis (Event-Handler, `checkGeneralVitality` Zeile 878)
- Enter-Taste im Tab ANALYZE: erste GV → Case-GV; jede weitere GV → nächste Rate (Index = gvCounter-1) erhält `gv`; dabei `recurringGeneralVitality` = Häufigkeit des GV-Werts über alle Raten.
- Nach 21 Raten (oder > Anzahl Raten): Analyse zurücksetzen (alle gv=0), **neue Session** anlegen (Kopie der letzten), gvCounter=0.
- Pfeiltasten ←/→: Navigation durch historische Sessions (`analysisPointer`).

---

## 5. Broadcast-Subsystem

### 5.1 GUI-Broadcast (`processing2/elements/BroadcastElement.java`) — der tatsächliche „Sendebetrieb"
- Element = 320×180-Panel, Lebensdauer = `seconds`; Fortschrittsbalken.
- **Zufalls-Ästhetik mit Fibonacci-Schwellen:** Malevents bei `nextInt(13)>=12`, `nextInt(21)>=20`, `nextInt(33)>=32`, `nextInt(54)>=53`, `nextInt(89)>=89`; Formen bei 144, 233, 377, 610, 987 (Rechteck/Ellipse/Triangle/Polygon/Bezier/Arc/Line).
- **Resonanz-Event** bei `nextInt(6765 + multiplier) >= 6764 + multiplier` (Fibonacci 6765!): `ResonanceObject` (Zeitstempel+Rate) in `resonanceList`; `resonateCounter` der Signatur in `resonatedList` ++ (wird sortiert angezeigt, später als „Resonanz-Protokoll" gespeichert).
- Signaturen-Overlay: bei Hotbit-Wurf ≥98 → zufälliger Text aus `ADDITIONAL_RATES = [ENERGY, FIRE, POWER, WOOD, GROUNDING, EARTH, RHYTHM, METAL, WATER, DEEPNESS, DO NO HARM!, UNITY, LOVE, BALANCE]`; Hotbits-Cache >10k/20k Pakete verstärkt die Zufallsdynamik.
- **Binaural-Sound** (bei Resonanz, Setting `play.binaural.sound`): leftFreq = 50+getInteger(500), rightFreq = left+getInteger(50), Volume 0.1+getInteger(10)×0.1, Dauer 3 s (`sound/Binaural`).
- Anti-Doppelstart: Broadcasts < 500 ms Abstand werden verworfen.
- `multiplier` (UI-Feld) erhöht Resonanzwahrscheinlichkeit linear.

### 5.2 Broadcast-Queue (`GuiElements`)
- FIFO `broadcastQueueList`; Parallelität: max. **8** aktive Elemente (Setting `broadcast.single.rates.only=true` → nur 1); Slider `QUEUE/PACKAGES/CACHE/PROGRESS` im Dashboard.
- `broadcast.delta.time` (Settings): Sekunden werden um aktuelle GV reduziert, wenn GV < Sekunden.
- `broadcast.embedded` (Default true): Queue der GUI; sonst separates `BroadcastUnit`-Fenster.
- `broadcastMix()`: nur Raten mit `gv > caseGV`, Sortierung GV desc dann energetischer Wert; Sekunden = `rate.gv - caseGV`.

### 5.3 Hardware-Broadcast am Pi (`service/BroadCastService.broadcastNow`)
```
signature ← ohne "(", ")", "-", " "
pro Repeat × pro Zeichen c:
    i = abs(c - 48)                     # ASCII-Digit-Distanz
    alle Pins low; dann je Ziffer n:
        clear-Modus:  ULTRAVIOLET wenn n ∈ [1,2,3,5,8]
        sonst:        WHITE n∈[0,9] · INFRARED n∈[1,6] · RED n∈[2,5] · GREEN n∈[3,7] · BLUE n∈[4,8]
        Blink: high → delay(data.delay, Default 25 ms) → low
danach CONTROL high, alle low
```
Pin-Mapping (WiringPi): CONTROL=GPIO_07, ULTRAVIOLET=00, WHITE=02, INFRARED=03, RED=21, GREEN=22, BLUE=23, COIL1=24, COIL2=25. `PiService` deaktiviert sich außerhalb Linux (`piAvailable=false` → No-Op).
`BroadcastQueue`: eigener Thread, 500 ms Takt, arbeitet FIFO ab, solange nicht sendend.
`GroundingProcess.getGroundingSignature()` = `"GROUNDING TO THE EARTH CORE"` → Broadcast 10 s + GV-Check des Operators.

---

## 6. Stick-Pad (`domain/StickPad.java`)
- Der Konstruktor von `StickPadPosition` addiert **einmal pro Position** die aktuelle Millisekundenzeit zu beiden Koordinaten: `seedX = x + capturedAtMs`, `seedY = y + capturedAtMs`. Dies ist im Original-Bytecode von 2.2 und im lokalen 2.9.0-JAR belegt.
- Analyse: Rate = `rates[Random(seedX).nextInt(size)]`, Wert = `Random(seedY).nextInt(10)+1`, Summierung je Rate; GV: `Random(seedX).nextInt(1000)+1`, Maximum, bei >950 Bonusfolge aus `seedY`. Nach einer GV-Prüfung werden im Original alle Positionen gelöscht.
- Im RadiWorks-Port bleibt die bisherige Abbildung aus rohem X/Y als **reproduzierbarer Standardmodus** erhalten. Der separat wählbare **Original-Zeitmodus** erfasst beim **Servereingang** den Millisekundenwert einmal je Position, speichert beide Seeds und hält die letzten 20 Laufbelege lokal vor. Netzwerkverzögerung trennt ihn vom lokalen Original-Ereigniszeitpunkt; eine reale Live-Äquivalenz über viele Positionsfolgen ist nicht nachgewiesen. Bei einer Stick-Pad-Analyse wird die Datenbankliste wie im untersuchten 2.9.0-Pfad frisch gelesen; der Laufbeleg bindet Selektor, Anzahl und SHA-256 der **geordneten, tatsächlich verwendeten Ratenwerte**. Das ist kein Rohdatei-Hash und keine manipulationssichere Signatur. Ältere Belege ohne Bindung bleiben unverifiziert.

---

## 7. Datenmodell & Persistenz

### 7.1 Case → `cases/{name ohne Leerzeichen}.json` (DataService.saveCase)
```
Case {
  name, description, created, lastChange,
  mapDesign: MapDesign { uuid, … (OSM-Karte, OpenLayers) },
  sessionList: [ Session {
      intention, description, created,
      analysisResult: AnalysisResult {
        id: UUID, generalVitality, numberOfTrials,
        rateObjects: [ RateObject {
            energeticValue, nameOrRate, url,
            gv, recurring, recurringGeneralVitality,
            level (1-12), potency ("C 30"), resonateCounter } ] },
      broadCasted: BroadCastData {
        clear, intention, signature, delay(25), repeat(1),
        enteringWithGeneralVitality, leavingWithGeneralVitality } } ],
  topTenList: [ RateObjectWrapper ]
}
```
- `dashboardInformations.json` (in cases/): zuletzt geladene Cases (max. 11).
- Konkurrierender Persistenzpfad: `DatabaseService` (Nitrite-DB, `cases/aetherone.db`, Benutzer `aetherus`/`secreto`) ist im JAR vorhanden, wird von der GUI **nicht** verwendet (nur JSON-Dateien). Für den Port: JSON-Dateipfad ist der verbindliche Contract.

### 7.2 Raten-Datenbanken (DataService)
- Baum `data/`; **`.txt`-Dateien = Datenbanken**, `.rscript` = Skripte, `FUNCTION_*` wird ignoriert.
- Zeilenformat: `RATE NAME` oder `RATE NAME\tURL` (TAB trennt Materia-Medica-Link).
- `init()` klont/pullt `https://github.com/isuretpolos/radionics-rates.git` nach `data/radionics` (JGit).
- **Präfix-Matching:** `findAllBySourceName("HOMEOPATHY")` lädt ALLE Datenbanken, deren Dateiname mit `HOMEOPATHY` beginnt — Kategorie-Buttons (HOMEOPATHY/BIOLOGICAL/SYMBOLISM/ESSENCES/CHEMICAL/ENERGY) sind Präfix-Selektoren.
- Standard-DB: `HOMEOPATHY_Clarke_With_MateriaMedicaUrls.txt`.

### 7.3 Settings (`utils/AetherOnePiProcessingConfiguration`)
- `config/{Settings,Gui,Environment}.json`; Schema `Settings { name, booleans{}, integers{}, strings{} }` mit Self-Defaulting-Gettern (Default wird beim ersten Zugriff persistiert).
- Bekannte Keys: `analysis.very.high.max.hit`, `broadcast.delta.time`, `broadcast.embedded`, `broadcast.single.rates.only`, `broadcast.specific.times`, `play.binaural.sound`, `dynamic.adjustments`, `watchlist.activate`, `power.switch`, `window.size.width/height`.

---

## 8. Server-API (Contract für HTML-Frontend & Python-Port)

Base: Javalin, `findAvailablePort(80…65535)` (Konfliktfrei), CORS anyHost, Static `ui/` (CLASSPATH).

| Methode | Route | Request | Response / Verhalten |
|---|---|---|---|
| GET | `ping` | – | `{"result":"pong"}` |
| GET | `settings` | – | Settings-JSON (booleans/integers/strings) |
| GET | `case/current` | – | aktueller Case im RAM |
| GET | `case` | – | Liste aller Case-Namen |
| GET | `case?name=X` | – | Case `cases/X.json` |
| POST | `case` | Case-JSON | speichern + als aktuellen Case setzen |
| GET | `rates` | – | Datenbank-Namen (ohne `.txt`) |
| GET | `analysis` | – | aktuelle AnalysisResult |
| POST | `analysis` | – | Neu-Analyse der selektierten DB |
| POST | `gv` | – | `{"gv":"<int>"}` (checkGeneralVitality) |
| POST | `searchAnomaly?width&height` | – | width×height-GV-Matrix |
| GET | `materiaMedicaSearch?field&query` | – | Top-20 Lucene-Treffer; Treffer werden per `content.replaceAll(queryPart, "<b>…</b>")` hervorgehoben ⚠ queryPart = Regex → Injektionsquelle |
| POST | `broadcast` | `{"signature": str, "seconds": int}` | Broadcast starten, UI-Tab BROADCAST aktivieren |
| WS | `/analysisUpdate/{id}` | – | bei jeder Analyse: Push des aktuellen AnalysisResult (JSON) an alle Sessions |

Das Vue-Frontend (`html/index.html`) hardcodet `http://localhost:7070`; das Angular-Bundle ruft same-origin relativ auf. **Für Aurelia: Port aus der Plattform-Config, nie hardcoden.**

---

## 9. Materia-Medica-Suche
- 1008 JSON-Dateien `materiaMedica/Clarke/*.json`: `{ remedyName, remedyAlternativeNames, categories: { "Clinical": [Symptome], … } }`.
- Lucene im RAM: Felder `remedyName`, `remedyAlternativeNames`, `body` (toString), je Kategorie ein Feld; StandardAnalyzer; Top 20.
- `AnalysisService.analyzeClarke(nameOrRate, result)`: Symptom-Schnittmenge der analysierten Raten → HTML-Report (j2html, Bootstrap 5 CDN) nach `logs/{Remedy}.html`; Tabelle Top-20 gemeinsamer Symptome.

---

## 10. Weitere Funktionsbereiche (für Vollständigkeit des Ports)

| Bereich | Verhalten |
|---|---|
| **Essential Questions** | GV-Orakel: „Appropriateness" (3× getMax→%), „Permission"-Kette (GV>500 = JA), Zeit-Prognose aus 7 Optionen (Woche…2 Jahre) per GV-Maximum. Ausgabe als Textblock. |
| **CLIPBOARD-Button** | Aktuelle Analyse (max. 21 Raten, ohne URLs) + GV als JSON in Zwischenablage, mit vorformuliertem KI-Interpretationsprompt („Give me an interpretation of this radionics result…"). |
| **Training** | `TRAINING[START]`: zufällige Rate aus DB als verdeckte Signatur; `TRAINING[UNCOVER]` lüftet sie. |
| **Auto-Modus** | GV-Messreihe als Balkengraph, Durchschnittsanzeige, Farbcode (≥1000 grün, <500 gelb, <250 rot). |
| **Card-Generator** | Top-10-Raten (GV·energeticValue als Winkel) → `RadionicLine` mit Hotbit-Farben → PNG nach `cards/card_<ts>.png`. |
| **Image-Layers** | Verzeichnis `IMAGE*.png` → Schichten; `analyze()`: je Schicht GV aus 256×(getInteger(0,1000)<500, +1 bei Würfel 6) bis max≥162; Minimum und Maximum bleiben über **alle** Runden erhalten, Normalisierung 256/(max-min). Der Port gibt das Verhältnis derzeit auf vier Dezimalstellen gerundet aus; vollständige Float-/Rendering-Parität ist offen. |
| **Area-Scan** | Bildfläche einfügen/laden; `SCAN FOR TARGET` → searchAnomaly-GV-Raster. |
| **Statistics** | `StatisticsGenerator.start(case)` → Auswertung über Sessions. |
| **RadionicScript** | Mini-Interpreter (`.rscript`): `PRINT`, `##` Kommentar, `GOTO label`, `var = ANALYZE db`, Zeilen mit `:` sind Labels. |
| **Rate-Kurznamen** | `cleanRateName`: æ→ae, Æ→Ae, Œ→Oe; Namen >100 Zeichen gekappt. |
| **Rekurrenz** | `recurringRateList` je Case: gleicher Rate-Name über Analysen → `recurring++`. |
| **Clear** | UV-Overlay-Blinken 70 Frames (visuelles „Reinigen"). |

---

## 11. Frontends

1. **`ui/` Angular-Build** (prod, gehashte Bundles): Voll-Client für die Server-API inkl. OpenLayers-Karte (MapDesign/OSM-Domäne: `domain/osm/{Feature,MapDesign,OsmDownload,OsmElement}`). Same-origin-Aufrufe.
2. **`html/` Vue 3** (nicht gebaut, CDN-artig lokal): Materia-Medica-Suche (Live-Suche ab 3 Zeichen) + Settings-Anzeige. Port 7070 hardcodet.

---

## 12. Portierungsbewertung (Java → Python)

| Domäne | Portierungsaufwand | Anmerkung |
|---|---|---|
| AnalysisService/GV/Potenz | **niedrig** | reine Algorithmen, direkt übertragbar; Random-Semantik (Seed→Random-Objekt) exakt nachbilden |
| Hotbits-Provider | **mittel** | `/dev/hwrng`/Webcam/DLL sind plattformabhängig → Provider-Abstraktion mit Fallback-Kette (unter Windows: QRNG-API + `secrets`) |
| REST/WebSocket | **niedrig** | FastAPI + WebSocket, 1:1 Routenübernahme (Abschnitt 8) |
| Case-Persistenz | **niedrig** | JSON-Dateien identisch möglich (Contract Abschnitt 7.1) |
| Raten-DB | **niedrig** | TXT-Format + Git-Repo unverändert nutzbar |
| Materia Medica | **mittel** | Lucene → Whoosh/Tantivy oder SQLite-FTS5; 1008 JSONs direkt übernehmbar |
| Broadcast (GUI-Ästhetik) | **mittel** | Canvas-Animation mit identischen Fibonacci-Schwellen; Resonanz-/Binaural-Logik portierbar (WebAudio) |
| Hardware (GPIO/LED) | **ersatzentfällt** | GPIO-LED-Mapping → optional an Aurelia-Hardware-Layer koppeln; Default: simuliert |
| Stick-Pad | **mittel** | Zwei getrennte Modi; Zeitaddition des Originals erfordert Erfassung und Wiederanlaufbeleg je Position. Drei feste Positionen und die erste GV-Messung wurden gegen das lokale 2.9.0-JAR verglichen. Der Port erzeugt für eine eigenständige Stick-Pad-Analyse einen positions-/kataloggebundenen Passport und Draft, bei aktivem Fall eine eigene Session; Case, Draft und Beleg werden gemeinsam wiederherstellbar gespeichert. Die nachfolgende GV gehört dieser Session. Historische Gesamtkataloge werden nicht archiviert (`replayable=false`); normale GV-Fortsetzung nutzt einen abgeleiteten Seed. Keine pauschale Live-Parität oder Hardware-Abnahme. |

**Nicht portieren:** Nitrite-DB-Pfad (tot), Spring-`application.properties` (nur Hotbits-Defaults relevant), doppelte HotbitsClient/Handler-Implementierung → **eine** Provider-Architektur in Python.

---

## 13. Offene Punkte / Quirks (dokumentiert, bewusst so im Original)

1. `materiaMedicaSearch`-Highlighting nutzt `replaceAll` mit Roh-Query → Regex-Injection/Exceptions möglich.
2. `BroadcastElement.draw()` nutzt `for (x=0; x>max; …)` — Schleifen laufen wegen `x>max` bei max>0 **nie** (Original-Bug, wirkt als Zufalls-No-Op; für Verhaltensidentität: weglassen, Wirkung = null).
3. `saveResonanceProtocol`: Dateiname wird durch Dekompiler-Artefakt (`void var5_9`) unklar → effektiv `"nocase"`-Fallback: `resonateProtocols/{ts}_resonance_nocase.txt` (Case-Name nur wenn gesetzt; Original: bedingte Zuweisung).
4. `HotbitsClient.getInteger(0, bound)`-Pfad über `getSeed(30)`+Zeitstempel — zwei verschiedene Ziehungssemantiken zwischen Handler (Seed-Cache) und Client (hwrng+Zeit). Port: Provider entscheidet, Interface identisch.
5. Doppelte Session-Neuanlage möglich (GV-Runde + Analyse) — Originalverhalten, im Port als explizite Session-Versionierung abbilden.
