# RadiWorks — Port-Plan (Python-Engine + HTML-App)

> **Aktueller RadiWorks-Stand 08.10.2026:** R6-Release, 200 manifestierte Produktdateien; kanonische Quelle synchronisiert. Frühere Nachträge unten sind historische Belege. [Aktueller Abgleich und Grenzen](../../../Brainpower/docs/verification/RADIWORKS_R6_SOURCE_TEMPLATE_SYNC_2026-10-08.md). Keine Aurelia-Integrationsfreigabe.

> Zielbild: `radiworks/engine` (FastAPI) + `radiworks/webapp` (HTML) nach `MODUL_STANDARD.md`,
> API nach `API_CONTRACT.md`, Ziel-Reifegrad Stufe 4.
> Logischer Zielort des Prototyps: `C:\Users\Hubert111\Documents\Radiworks\radiworks_port\` (bleibt im gesicherten Repo, bis das Modul seinen eigenen Endort erhält).

**Ist-Nachtrag 30.09.2026:** P0–P4 dokumentieren die Portierungsabsicht, nicht automatisch eine abgenommene Stufe. Der getrennte lokale Kandidat `a242d24758d53e86ab290454ae4772f0827acc06` umfasst Engine und Webapp; 105/105 Moduldateien stimmen mit dem RadiWorks-Arbeitsstand bytegleich überein. Isolierter Chrome-Smoke 19/19 und gezielte hörende Fallaktionsprobe sind bestätigt. Das [lokale Vertragsprofil](../../standards/RADIOWORKS_LOCAL_PROFILE_V1_1_DRAFT.md) benennt die Abweichungen zum gemeinsamen API-v1-Soll; S4, Ziel-Ubuntu-24.04.4 und Aurelia-Host bleiben offen. Beleggrenze: Brainpower `docs/verification/RADIWORKS_RELEASE_BOUNDARY_2026-09-29.md`.

## Phase P0 — Engine-Skelett (Stufe 2)

```
radiworks_port/engine/
├── pyproject.toml
├── src/radiworks/main.py        # create_app(), CORS localhost, Static-Mount webapp/
├── src/radiworks/manifest.py    # Kernel-ABI-v1: radiworks.engine / 0.2.0; REST ABI v1
├── src/radiworks/entropy.py     # EntropyProvider-Kette
├── src/radiworks/core/
│   ├── analysis.py              # analyse_rate_list, check_general_vitality, analyze_potency, search_anomaly
│   ├── rates.py                 # TXT-Parser ("NAME\tURL"), Präfix-Matching (HOMEOPATHY* etc.)
│   ├── cases.py                 # Case/Session-JSON-Contract (FUNKTIONSANALYSE §7.1)
│   ├── broadcast.py             # Queue-Thread, Resonanz-Events, Fibonacci-Schwellen
│   ├── stickpad.py              # Positions-Abbildung (Random(x)/Random(y))
│   └── materia.py               # Clarke-JSONs laden + FTS-Suche
└── tests/                       # Seed-fixierte Goldwert-Tests gegen Java-Referenzwerte
```

**Entscheidungen (verbindlich):**
1. Entropie: `EntropyProvider`-Interface `get_boolean()/get_integer(min,max)`;
   Factory-Default `seeded`, `stochastic` explizit per Settings/Request.
   Stochastic-Reihenfolge: Webcam-/Hotbits-FIFO → random.org → OS-CSPRNG;
   Seeded löst keinen Netzverkehr aus.
2. Hotbits-Dateiformat `{"integerList":[…]}` bleibt kompatibel (Bestandsdaten ladbar).
3. Nitrite-DB wird NICHT portiert (im Original toter Pfad). Spring-Properties nur als Defaults-Quelle für Entropie-Parameter.
4. Materia Medica: SQLite-FTS5 (procno external deps) oder `rank_bm25` — 1008 JSONs unverändert übernehmen aus `Radiworks/materiaMedica/Clarke/`.
5. Raten-Datenbanken: expliziter read-only Katalog über `RADIOWORKS_DATA_DIR`;
   ohne Variable `${RADIOWORKS_HOME}/data`. Ein reproduzierbarer, lizenzierter
   Bootstrap bleibt ein separater R2-Gate.

## Phase P1 — Algorithmen 1:1 (Stufe 2 Kern)

Portierreihenfolge mit Goldwert-Tests (Java-Ausgaben mit fixierten Hotbit-Seeds als Referenz):
1. `check_general_vitality` (3× max 0–999 + Bonus-Spirale >950)
2. `analyse_rate_list` (shuffle → n=max(size/10,120,≤5000) → Anreicherung +getInteger(10) bis maxHits 100/1000 → sort → shorten(105) → Potenz + Level-12-Fächer)
3. `analyze_potency` (Typen D/C/LM/Q/FLUX, Stärkefolgen, 77-Treffer-Akku)
4. Broadcast-Queue (FIFO, 8 parallel / 1 im single-Modus, 500 ms Takt) + Resonanz-Event `nextInt(6765+multiplier)`
5. Stick-Pad-Abbildung
6. Essential-Questions-Orakel (GV-Schwellen 500, Zeit-Prognose 7 Optionen)

## Phase P2 — API-Layer (Stufe 2 Abschluss)

Das lokale REST-v1-Skelett folgt `API_CONTRACT.md` mit den im Profilentwurf
benannten Abweichungen, insbesondere beim Analyse-Body und Host-Scope. Dazu
kommen Original-Namen als Aliase
(`/ping→ping`, `/databases→rates`, `/analysis→analysis`, `/gv→gv`), damit die
Original-Dokumentation (FUNKTIONSANALYSE §8) als Testlog fungiert.
WebSocket `/ws` mit boot-bewusstem Umschlag
`{v:1,id,boot,type,payload,ts}`, initialem `server.hello` und Reconnect über
`last_event_id` plus `last_boot`; bei Replay-Lücken folgt `server.replay_gap`.

## Phase P3 — HTML-App (Stufe 3)

```
radiworks_port/webapp/
├── index.html             # zehn Ansichten: Start, Analyse, Raten/Stick-Pad,
│                          # Broadcast, Bild/Area, Peggotty, Entropie, Fälle,
│                          # Einstellungen, Über/Quellen
├── css/tokens.css         # bestehende lokale Token-Basis
├── css/module-theme.css   # Modulakzent
├── css/app.css            # Komponenten und responsives Layout
├── js/boot.js             # Navigation, Verbindungs- und Live-Initialisierung
├── js/api.js              # lokaler Contract-Client
└── js/views/              # analyze, stickpad, broadcast, images, peggotty,
                           # entropy, cases, settings, info u. a.
```
- Canvas-Broadcast übernimmt exakt die Schwellenfolge 13/21/33/54/89/144/233/377/610/987/6765 (FUNKTIONSANALYSE §5.1).
- CopyGuard-Wortliste anwenden (Wellbeing-Formulierungen, keine Heilversprechen).
- Deutsche UI, Tastaturbedienung, 44-px-Ziele.

## Phase P4 — Integrationsreife (Stufe 4)

- Lokal vorhanden und geprüft: `/manifest` mit dynamischem Hash, WebSocket-
  Livekanal und versionierter isolierter Browser-Smoke unter
  `radiworks_port/engine/tools/browser_smoke/smoke.mjs` (19/19).
- Offen: vollständige CopyGuard-/WCAG-Abdeckung, Ziel-Ubuntu-24.04.4-Lauf,
  serverseitig autorisierte Mandanten-/Auftragsbindung und gemeinsamer
  Template-/Aurelia-Hostvertrag. Nullable Body-Felder allein wären kein
  Scope-Nachweis; `tenant_id`/`client_id` werden lokal im Analyse-Body abgewiesen.

## Risiken & Notizen

1. **Reihenfolge:** Die ältere Aurelia-Quelle sagt „Migration: Morphic zuerst" (`module.tsx:19-22`). Der aktuelle Betreiberplan prüft **lokal** erst RadiWorks, danach Radi144, `morphic_v1` und ein neues Modul; der Matrixplan und erst dann die Aurelia-Integration folgen separat. Die historische Migrationsaussage ist keine Freigabe, den jetzigen Ablauf umzustellen.
2. **TABU:** keine Anlehnung/Kopie aus `/opt/radiquant4` (Alt-FastAPI-Baum, „Never" lt. `AGENTS.project.md:40`).
3. **Entropie unter Windows:** `/dev/hwrng` entfällt → QRNG-API/OS-Entropie; für reproduzierbare Tests Seed-Modus nutzen.
4. **Kein Cross-Origin in Aurelia:** spätere Einbettung same-origin/iframe (deren `assertSameSiteRequest` blockt Cross-Site, `isolation.server.ts:34`).
5. JGit-Auto-Klon des Originals bei jedem Start ist für Aurelia-Booten untauglich → Raten-Repo als gepinnte Daten-Beilage.

## RadiWorks-Nachtrag 01.10.2026

Der lokale Kandidat und der RadiWorks-Quellordner stimmen für 101 geprüfte Kandidatendateien bytegleich überein; 19 vorher abweichende/fehlende Dateien wurden mit Hash- und Sicherungsmanifest unter `Brainpower/runtime/radiworks-source-sync-20261001/manifest.json` synchronisiert. Neue Funktion im lokalen Prototyp: `POST /analysis/stickpad-followup` nutzt ausschließlich die gespeicherten Treffer einer aktiven Stick-Pad-Quellsitzung, berechnet neue Werte und erzeugt eine eigene, über `parentSessionId` verknüpfte Sitzung. Die ursprüngliche Sitzung bleibt erhalten; ihre ersten EW werden nicht als Gewichte übernommen. Die normale Datenbankanalyse bleibt separat. Dieser Zusatz ist noch kein Teil der gemeinsamen ABI oder des Aurelia-Hostvertrags.

Die vollständige Python-Engine-Suite bestand lokal mit zwei umgebungsabhängigen Skips, der bestehende isolierte Chrome-Smoke 19/19 und ein getrennter synthetischer Browserlauf für den Folgeanalyseweg. Entropie-Kamerastatus und Feedzahl wurden klarer getrennt; diese Anzeige beweist keine physikalische Zufallsqualität. Die laufende Betreiberinstanz auf 8103 hatte beim Abgleich noch die ältere API im Prozess und wurde für den Test weder neu gestartet noch beschrieben. Stochastic mit aktivem Fall benötigt weiterhin einen dauerhaften Recovery-Schlüssel. P4/S4 und parallele Fallaufträge bleiben offen.


## Betriebs- und Nachweisnachtrag 03.10.2026

Sieben getrennte lokale Runtime-/Fall-Scopes auf 8103–8109 sind über Windows-Aufgaben eingerichtet; Entwicklung ab 8110. Der Wiederanlauf nach Anmeldung ist konfiguriert, die Windows-Warmstartprobe noch offen. Mehrere Aufträge pro Fall innerhalb derselben Engine sind dadurch nicht freigegeben. Peggotty-Duplikatlabels werden live mit HTTP 422 abgewiesen; fünf gezielte Regressionstests bestanden. GV-RE zählt identische nicht-null Raten-GV im vollständigen Ergebnis und ist kein zeitlicher Trend. Periodische GV-Verläufe benötigen vor Aktivierung eine geprüfte Fall-/Sitzungs-/Broadcast-Zuordnung und getrennte Entropie. Kamera/Stochastic-Langlauf und S4.8 bleiben offen. Maßgeblicher Bericht: `C:\Users\Hubert111\Documents\Brainpower\docs\verification\RADIWORKS_SIEBEN_INSTANZEN_CHAT_NETZWERK_2026-10-03.md`. Gemeinsame ABI, Host-/Mandantenautorität und Reifegradregeln werden durch diesen Nachtrag nicht geändert.

## RadiWorks-Nachtrag 05.10.2026 — gepinnter C23-Quellstand

Der für die lokale C23-Abnahme verwendete Engine-/Webapp-Quellstand ist ../Brainpower/runtime/rw-c23-fixed-release-20261005. Sein Produktmanifest enthält 131 Dateien und hat SHA-256 9ba23c5dbfe856fc6887abf87fe13aba302ec362c1cdd432654d8fa30fe50694. Der äußere Servicewrapper ist eine getrennte Datei. Engine-Version 0.2.0 und REST-ABI v1 bleiben unverändert; Portable5 0.3.0-rc1 ist nur die private Paketbezeichnung.

Vor dem gesonderten Hash-Overlay ergab der Vergleich mit Documents/Radiworks/radiworks_port: 77/131 bytegleich, 15 abweichend, 39 fehlend. Zehn der 15 kanonischen Varianten stimmen exakt mit früheren rw-journal/rw-gv2/rw-vf-Snapshots überein. In den acht geprüften Pythonmodulen wurden keine ausschließlich kanonischen Funktions-/Klassendefinitionen gefunden; die abweichenden kanonischen Zeilen stammen überwiegend aus älteren Implementierungen, etwa Fall-/Journal-/UI-Pfaden. Der Quellordner hat kein Git-Metadatenverzeichnis; die Hashdifferenzen belegen daher Bytes, nicht ihre Commit- oder Urheberschaft.

Pfadtrennung: Die aktive virtuelle Umgebung liegt unter Documents/Radiworks/radiworks_port/engine/.venv und ist ein VenvProxy mit C:/Python313 als Base-Python. Ein Prozesspfad zu C:/Python313/python.exe allein beweist nicht, dass die venv ungenutzt ist. Die Live-Evidenz bindet den Produktquellstand separat an den festen C23-Release-Pin. Der eingebettete CPython im Portable5-Paket ist wiederum eine eigene Laufzeitkopie.

Ein Quellabgleich darf keine abweichenden Ausgangsbytes überschreiben, bevor sie separat gesichert und rückgelesen wurden. Die 39 fehlenden manifestierten Dateien sind additiv einzubringen; 77 gleiche Dateien können unverändert bleiben; nicht manifestierte Dateien, engine/.venv, Homes, Fälle und Schlüssel sind außerhalb dieses Datei-Overlays. Abschluss erst nach erneutem Manifest-Readback behaupten.

Die lokale Abnahme umfasst fünf isolierte synthetische Instanzen, Originalanalysen, den getrennten 21×80.000-CPU-Vergleich, Browserleseprüfungen und Stop/Neustart. Sie ist keine Zweit-PC-Abnahme und keine S4-/Aurelia-Freigabe. Windows 10/11 x64 benötigt die Microsoft VC++ v14 x64-Laufzeit; nach erfüllter Voraussetzung ist das Paket offline über Loopback betrieben. Die Datenlizenzzuordnung der Clarke-Beilage bleibt ungeklärt; private synthetische Prüfung ersetzt keine Freigabe öffentlicher Weitergabe.

Nachweise: Template-Delta unter ../../../Brainpower/docs/verification/RADIWORKS_EXP1_C23_TEMPLATE_DELTA_2026-10-05.md; Portable5-Abschluss unter ../../../Brainpower/docs/verification/RADIWORKS_C23_PORTABLE5_ABSCHLUSS_2026-10-05.md; Produktmanifest unter ../../../Brainpower/runtime/rw-c23-fixed-release-20261005/PRODUCT_MANIFEST.json. Links sind relativ zum vorgesehenen modules/radiworks-Zielordner.


### Abschließender Quellabgleich 05.10.2026

131/131 kanonische Produktdateien SHA-gleich mit dem C23-Pin; 15 ersetzt/39 ergänzt/77 unverändert. Drei Nachträge nach Vorherkopie übernommen. Details und Grenzen: [Synchronisationsbericht](../../../Brainpower/docs/verification/RADIWORKS_SOURCE_TEMPLATE_SYNC_2026-10-05.md). Keine normative API-/S4.8-Freigabe.


## R6-Nachtrag 08.10.2026 – bestätigter lokaler Modulprototyp

Quellpin `Brainpower/runtime/rw-r6-release-20261008`, Produktmanifest SHA256 `445ece8f8c826e1391fead34c9a4c9b271e3b13b6d59a7654f66f11ab77b6275`, 200 Dateien; Kernel `radiworks.engine 0.2.0`, lokale REST-ABI weiterhin v1. Der kanonische Quellordner `Documents/Radiworks/radiworks_port` ist dateiweise SHA-gleich. Der Produktmanifesthash und die sieben verschiedenen lokalen Prozess-Scopes sind keine autoritative Aurelia-Identität.

- Zwei getrennte Achsen: Original AetherOne / Persönliche Heuristik sowie reproduzierbar / stochastisch. Original-EW/GV und persönliche Matrixscores bleiben getrennt; keine zusätzlichen Originalformeln. Persönliche vollständige Einzeldatenbankaufträge sind auf höchstens 4096 Raten begrenzt; Altvergleichsbelege bleiben lesbar, überholte Vergleichs-UI ist entfernt. Verfahren, Quelle, Katalog und Fallkontext werden pro Auftrag festgehalten; Umschalten ändert keine laufenden Aufträge.
- Getrennte persönliche Kontextfelder, aktiver Ortstyp, neutraler Fall-Identifier, Fokusvorschläge nach bestehender Wortheuristik und optionales Fokusbild. Keine semantische KI-Suche. Speicherung und Kontextübernahme ersetzen keine klinische Messung.
- Original-GV/21er-Runden, separate Beobachtungshistorie und ausdrücklich gestartete Watchlist; Auto AUS beendet nicht automatisch alle virtuellen Broadcasts. Broadcast-Queue und sichtbare Resonanzliste sind bewusst getrennt leerbar, erhaltene Historien bleiben erhalten.
- Fallbezogenes Medienprofil: bis zu fünf geordnete Animationsbilder; feste Einzeltöne, Solfeggiofolge, Rosa Rauschen, gleichmäßige/Phi-/Fibonacci-Pulsprofile. Phi/Fibonacci koppeln Pulsrate und Abschnittsdauer. Bestehende Broadcasts behalten ihren eingefrorenen Profilstand. Audio nur nach bewusster Browseraktivierung, keine serverseitige Schallausgabe oder unbelegte Gesundheitswirkung. Normative Host-/Mandantenrechte werden dadurch nicht erweitert.
- Sieben lokale Dauerinstanzen 8103–8109 mit getrennten Homes/Scopes und unveränderten Windows-Taskdefinitionen geprüft; externe Stochastic-Recovery weiter nur auf 8103 vorhanden. Start5 0.4.0-rc1 wird separat als Fünferpaket geprüft, keine fertige Paket- oder Zweit-PC-Abnahme aus diesem Nachtrag ableiten.

Offen bleiben autoritative Host-/Tenant-/Client-/Job-Zuordnung, Rechte/Widerruf/Quotas, Plattform-RLS, gemeinsame Datenbank-/Kataloggovernance und Importvertrag, Ubuntu-Abnahme und S4.8. Der gemeinsame API_CONTRACT und MODUL_STANDARD sind unverändert. Kamera- und weitere externe Prüfungen bleiben gesonderte Belege. Details: [R6-Quell-/Referenzabgleich](../../../Brainpower/docs/verification/RADIWORKS_R6_SOURCE_TEMPLATE_SYNC_2026-10-08.md).
