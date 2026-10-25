# Unabhängiges technisches Review — Operator-Workbench Freeze v5

**Urteil: REQUEST CHANGES / NO-GO**  
**Konfidenz: HOCH**  
**Reviewbindung:** Freeze v5, Branch `operator-workbench-phase1`, HEAD `3271ff9366ab3fecb2a158913a0cc19ed6a06726`

## 1. Start- und Endverifikation

| Prüfung | START | ENDE | Ergebnis |
|---|---|---|---|
| Git-Toplevel | `C:/morphic_v1/.worktrees/operator-workbench-phase1` | identisch | OK |
| Branch | `operator-workbench-phase1` | identisch | OK |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch | OK |
| Freeze-Manifest | `docs/reviews/2026-07-20-workbench-remediation-technical-freeze-v5.sha256` | identisch | OK |
| Freeze-SHA-256 | `8d4615f6718cb27e7159212fe142c4b544a7c2c05d7a4837b7186295d4dd9078` | identisch | OK |
| Manifest-Hashzeilen | 47 | 47 | OK |
| Einzeldateihashes | 47/47 `OK` | 47/47 `OK` | OK |
| Manifest-Aggregat, Zeilen „as listed“ | `2a7e375de48ffced0ac32183d6c7bcb879d1a41942c0a14b8c26885ac9e1d2f3` | identisch | OK |
| Pfadreihenfolge | lexikalisch nach relativem Pfad | identisch | OK |
| Git-Scopepopulation | 48 Pfade | 48 Pfade | OK |
| Scopegleichheit | 47 Manifestpfade + ausschließlich das selbstreferenzielle v5-Manifest | identisch | OK |
| Set-Differenz Manifest ↔ Status ohne v5-Manifest | leer | leer | OK |
| Drift | — | keine Hash-, HEAD-, Branch- oder Scope-Drift | OK |

Die Aggregatrezeptur ist in v5 korrekt: Die Manifestzeilen sind bereits nach dem relativen Pfad sortiert; das Aggregat entsteht aus den 47 vollständigen Hashzeilen in dieser Reihenfolge mit LF-Abschluss. Eine Sortierung der vollständigen Zeilen nach dem führenden Hash wäre eine andere, nicht deklarierte Rezeptur.

## 2. Vollständigkeit der Inspektion

Alle **47/47 Manifestdateien** wurden vollständig gelesen und technisch geprüft:

| Kategorie | Dateien |
|---|---:|
| Web-Backend und Runtime | 7 |
| Frontend HTML/CSS/JavaScript | 10 |
| Freeze-, Review- und Plandokumente | 9 |
| Hardware-/Harmonisierungsservices | 2 |
| Playwright-Konfiguration und Browserfälle | 3 |
| Python-Testmodule | 16 |
| **Gesamt** | **47** |

Die beiden v4-Reviews sowie der aktive v5-Remediationplan wurden als verbindliche Reviewanforderungen abgeglichen. Die darin dokumentierten Testresultate wurden als Freeze-Claim gelesen, aufgrund des ausdrücklichen Testverbots aber nicht erneut ausgeführt.

## 3. Befundübersicht

| ID | Priorität | Befund | Fundstelle |
|---|---:|---|---|
| F-01 | P1 | Berichtskatalog und Berichtsdateien umgehen die konfigurierte API-Key-Grenze und geben zusätzlich absolute Hostpfade aus | `apps/web/main.py:480-504`; `apps/web/reports.py:349-371` |
| F-02 | P1 | Harmonisierungsstarts sind nicht Single-Flight; Doppelstarts verwaisen mindestens einen produktiven Job | `apps/web/static/app.js:562-579`; `apps/web/static/workbench-state.js:17`; `apps/web/static/index.html:592-595` |
| F-03 | P1 | Der New-Case-Teardown sperrt neue Mutationen nicht; ein während des Resets gestarteter Job kann unbemerkt verwaisen | `apps/web/static/app.js:705-739`; `apps/web/static/workbench-api.js:7-46` |
| F-04 | P1 | `duration_factor` ist nach oben unbeschränkt und erlaubt extrem lange Jobs bzw. numerischen Ressourcen-DoS | `apps/web/contracts.py:153-155`; `services/harmonization_worker.py:494-499,731` |
| F-05 | P1 | Aktivierte Hardwarepfade laufen sequenziell unter einer gemeinsamen Impulsdeadline; nach CPU bleiben GPU/RAM regelmäßig wirkungslos | `services/hardware_modulation.py:275-325`; `services/harmonization_worker.py:532-543` |
| F-06 | P1 | Stop und terminaler Abschluss können einen persistent gestoppten Job mit einem falschen `completed`-Event kombinieren | `services/harmonization_worker.py:628-657`; `services/harmonization_worker.py:147-155` |
| F-07 | P1 | Scanprozesse überleben potentiell den Webprozess, ihre einzige Kontrollautorität ist jedoch ein In-Memory-Dictionary | `apps/web/scan_jobs.py:286-345`; `apps/web/scan_jobs.py:347-390` |
| F-08 | P2 | Fehlgeschlagene Preview-/Harmonisierungsaktionen bleiben still und können eine alte Berichtbindung aktionsfähig lassen | `apps/web/static/app.js:520-579,615-621` |
| F-09 | P2 | Draft- und Template-Schreibvorgänge sind im Gegensatz zu Run-Traces nicht prozessübergreifend serialisiert | `apps/web/workbench_runtime.py:92-131`; Vergleich `:134-205` |
| F-10 | P2 | Scanstatus-Snapshots mutieren nebenläufigen Zustand außerhalb des Service-Locks | `apps/web/scan_jobs.py:347-355,392-480` |
| F-11 | P2 | Sämtliche GET-Routen sind vollständig vom Rate-Limit ausgenommen, einschließlich rekursiver Reportscans | `apps/web/main.py:353-365`; `apps/web/reports.py:280-347` |
| F-12 | P2 | Der Browser unterstützt den konfigurierten API-Key-Modus nicht | `apps/web/static/workbench-api.js:7-47,159-218`; `apps/web/main.py:506-509,676-678` |
| F-13 | P2 | Die Produktionsseite startet mit einem personenähnlichen Datensatz statt mit datensparsamen Leerwerten | `apps/web/static/index.html:220-223,262` |
| F-14 | P2 | Das Geburtsdatum wird nur auf acht Ziffern, nicht auf ein reales Kalenderdatum geprüft | `apps/web/contracts.py:81-87`; `tests/test_web_contracts.py:127-133` |
| F-15 | P2 | Die behauptete adversarielle Abschlussaussage wird von den Tests für mehrere produktive Race-/Security-Domänen nicht getragen | `tests/browser/workbench.spec.js:153-299`; `tests/test_harmonization_worker_pulse_pause_execution.py:146-174`; `tests/test_web_workbench_runtime.py:129-176` |
| F-16 | P3 | Frontend-Grenzen für Harmonisierungsparameter widersprechen dem Backendvertrag | `apps/web/static/index.html:574-577`; `apps/web/contracts.py:145,153-155` |
| F-17 | P3 | Die 12-Schritt-Erklärseite besitzt nur einseitige ARIA-Beziehungen | `apps/web/static/workflow-stepping.js:37-49`; `apps/web/static/workflow-stepping.html:26-37` |

## 4. Befunde im Detail

### F-01 — P1: Unauthentifizierte Berichts- und Hostpfadoffenlegung

**Dateien:**  
`apps/web/main.py:480-504`  
`apps/web/reports.py:349-371`

Die Scan- und Harmonisierungsrouten verwenden `Depends(verify_api_key)`. Die Routen für Berichtsliste, Preview und Datei tun dies nicht. Gleichzeitig gibt `_entry()` neben Klienten-/Sessioninformationen die internen Felder `_root_path` und `_full_path` aus; `ReportCatalog.list()` serialisiert diese Dictionaries unverändert.

**Reproduzierbare Begründung:**

1. `MORPHIC_API_KEY` konfigurieren.
2. Ein Scanstatus ohne Header wird gemäß vorhandenem Testvertrag mit 401 abgewiesen.
3. `GET /api/reports`, `GET /api/reports/{id}/preview` und `GET /api/reports/{id}/file` haben keine entsprechende Dependency.
4. Die Listenantwort enthält Klienten-Slugs, Dateinamen und absolute Hostpfade.

Damit schützt der konfigurierte Schlüssel Jobmetadaten, aber nicht die wesentlich sensibleren Berichte. CORS ist kein Zugriffsschutz für direkte HTTP-Clients oder Navigationen.

**Erforderliche Korrektur:** API-Key-/Operatorgrenze auf Liste, Preview und Datei anwenden; interne `_root_path`-/`_full_path`-Felder vor der Response entfernen und einen expliziten öffentlichen Responsevertrag verwenden.

---

### F-02 — P1: Mehrere Harmonisierungsjobs können gleichzeitig gestartet werden

**Dateien:**  
`apps/web/static/app.js:562-579`  
`apps/web/static/workbench-state.js:17`  
`apps/web/static/index.html:592-595`

Für Scans existieren `scanStartPending`, `scanRunActive` und ein deaktivierter Startbutton. Der Harmonisierungsstart besitzt keinen entsprechenden Single-Flight-Zustand. Der Startbutton wird nach dem ersten Klick nicht deaktiviert.

**Reproduzierbarer Ablauf:**

1. Zwei schnelle Klicks starten Request A und B.
2. Beide serverseitigen Requests erzeugen je einen Workerprozess.
3. A setzt `activeHarmonizationJobId=A`, B überschreibt ihn mit B.
4. Beide Aufrufe starten Polling; es existiert aber nur ein globaler Timerhandle.
5. New Case und Stop kennen anschließend nur B.
6. Job A läuft bis zu 21 Minuten oder länger weiter und ist aus dem Browser nicht mehr kontrollierbar.

**Erforderliche Korrektur:** Harmonisierungsstart mit eigenem `startPending`/`runActive`-Vertrag, deaktiviertem Startbutton und genau einer aktiven Job-/Pollautorität absichern.

---

### F-03 — P1: Neue Mutationen können während New Case gestartet werden

**Dateien:**  
`apps/web/static/app.js:705-739`  
`apps/web/static/workbench-api.js:7-46`

`pendingMutations` verhindert nur, dass Reset während einer bereits laufenden Mutation beginnt. Beim Reset wird ausschließlich der New-Case-Button deaktiviert. Andere mutierende Controls bleiben aktiv; `requestJson()` prüft nicht, ob ein Reset läuft.

**Reproduzierbarer Ablauf:**

1. New Case startet ohne aktiven Scan, aber mit einem Harmonisierungsjob.
2. Während der erwarteten Stopantwort klickt der Operator „Analyse starten“.
3. Der neue Scan wird serverseitig angelegt und kann seine Job-ID noch vor der lokalen Resetphase liefern.
4. Der Reset erhöht danach `caseGeneration`, löscht `activeJobId` und leert die UI.
5. Dieser neue Scan war nicht Teil der zu Beginn ermittelten Stopmenge und läuft ohne erreichbare Browserreferenz weiter.

Derselbe Race ist für andere mutierende Draft-/Consent-/Policy-Aktionen möglich.

**Erforderliche Korrektur:** Einen expliziten `resetInProgress`-Zustand einführen, alle mutierenden Initiatoren am Einstieg fail-closed sperren und die aktive Jobmenge unmittelbar vor dem Commit erneut atomar prüfen.

---

### F-04 — P1: Unbeschränkter Dauerfaktor

**Dateien:**  
`apps/web/contracts.py:153-155`  
`services/harmonization_worker.py:494-499,731`

`duration_factor` besitzt nur `ge=1`. Laufzeit und Zyklenzahl werden direkt als `duration_factor × 21 × 60` berechnet.

**Reproduzierbare Begründung:**

- Ein direkter API-Aufruf kann `duration_factor=1000000000` senden.
- Der Worker wird damit für Milliarden mal 21 Minuten geplant und erzeugt eine entsprechend enorme Zyklenzahl.
- Noch größere Ganzzahlen können bei der Fließkommadivision oder bei `time.time() + total_seconds` einen Overflow/500 verursachen.
- Das Request-Rate-Limit begrenzt nur die Requestanzahl, nicht die durch einen Request dauerhaft gebundenen Prozesse.

**Erforderliche Korrektur:** Fachlich zulässige Faktoren als endliche Menge oder mit defensiver Obergrenze validieren; abgeleitete Gesamtdauer und Gesamtzyklen ebenfalls vor Prozessstart begrenzen.

---

### F-05 — P1: Mehrfach aktivierte Hardwarepfade erhalten nicht jeweils den Impulszeitraum

**Dateien:**  
`services/hardware_modulation.py:275-325`  
`services/harmonization_worker.py:532-543`

`modulate_all_hardware()` behauptet parallele Ausführung, ruft CPU, GPU, RAM und WebSocket aber nacheinander auf. Alle erhalten dieselbe `should_continue`-Funktion mit einer einzigen absoluten Impulsdeadline.

**Reproduzierbare Begründung:**

1. `use_cpu=True` und `use_gpu=True` aktivieren.
2. CPU wird zuerst aufgerufen und nutzt den Impulszeitraum bis zur gemeinsamen Deadline.
3. Beim folgenden GPU-Aufruf liefert `should_continue()` bereits false oder fast unmittelbar false.
4. GPU meldet null oder nur einen vernachlässigbaren Anteil der erwarteten Arbeit.
5. RAM und WebSocket liegen noch weiter hinten.

Die UI erlaubt diese Kombination ausdrücklich; die Tests beweisen lediglich, dass das Konfigurationsdictionary weitergereicht wird, nicht dass alle gewählten Pfade produktiv ausgeführt werden.

**Erforderliche Korrektur:** Entweder echte parallele, kooperativ abbrechbare Ausführung implementieren oder den Vertrag/UI auf genau einen produktiven Modulationspfad begrenzen.

---

### F-06 — P1: Stop/Completed-Widerspruch am terminalen Workerabschluss

**Dateien:**  
`services/harmonization_worker.py:628-657`  
`services/harmonization_worker.py:147-155`

Vor dem terminalen Abschluss wird der aktuelle Job einmal geladen. Danach wird ein möglicherweise veraltetes `job`-Objekt auf `completed` gesetzt und gespeichert. `_save_locked()` korrigiert es bei vorhandenem Stopmarker zwar zu `stopped`; der Code emittiert anschließend aber unabhängig vom tatsächlichen gespeicherten Status das Event `completed`.

**Deterministischer Race-Ablauf:**

1. Worker führt die Stopprüfung an Zeile 628 aus und sieht noch `running`.
2. Stop veröffentlicht danach Marker und gestoppten Snapshot.
3. Worker setzt sein altes Objekt auf `completed`.
4. `job.save()` erkennt den Marker und persistiert tatsächlich `stopped`.
5. Zeilen 649–657 schreiben trotzdem ein `completed`-Event mit 100 % und geben „abgeschlossen“ aus.

Damit widersprechen Jobauthority und Audit-/Realtime-Telemetrie einander.

**Erforderliche Korrektur:** Terminalstatus unter derselben `_job_lock`-Grenze laden, entscheiden, persistieren und erst nach bestätigtem `completed` das Abschlussereignis emittieren.

---

### F-07 — P1: Scan-Lifecycle ist nicht restartfest

**Datei:** `apps/web/scan_jobs.py:286-390`

Die gesamte Scan-Autorität befindet sich in `self._jobs`. Prozesse werden als eigene Windows-Prozessgruppe bzw. POSIX-Session gestartet, aber Job-ID, PID, Logpositionen, Owner und Artefaktbindung werden nicht dauerhaft registriert.

**Reproduzierbarer Ablauf:**

1. Scan starten; Kindprozess läuft.
2. Webprozess beenden oder neu starten.
3. Scanprozess kann unabhängig weiterlaufen.
4. Die neue `LocalScanJobService`-Instanz besitzt ein leeres `_jobs`.
5. Status und Stop liefern 404; New Case kann die Serverarbeit nicht mehr sicher beenden.

Die langlebige Prozesssemantik und die rein flüchtige Kontrollautorität sind damit vertragswidrig kombiniert.

**Erforderliche Korrektur:** Scanbindung einschließlich PID/Prozessgruppen-ID, Owner, Logpfaden und Status dauerhaft speichern und konservativ rekonstruieren; alternativ Kindprozess zwingend an den Webprozess-Lifecycle binden.

---

### F-08 — P2: Stille Fehler behalten alte Aktionsbindung

**Datei:** `apps/web/static/app.js:520-579,615-621`

`renderReportPreview()` und `startHarmonizationJob()` besitzen leere Catch-Blöcke. Bei einem fehlgeschlagenen neuen Preview bleibt der vorherige `activeReportId` erhalten und der Harmonisierungsbutton aktiviert. Pollfehler werden ohne sichtbaren Fehlerzustand unbegrenzt wiederholt.

**Folge:** Nach Klick auf einen nicht mehr verfügbaren Bericht kann die UI weiterhin den alten Bericht als Aktionsbindung verwenden, ohne den Operator über den fehlgeschlagenen Wechsel zu informieren.

**Erforderliche Korrektur:** Vor Previewwechsel einen Loading-/Selectionzustand setzen, bei Fehler die neue Auswahl verwerfen oder die alte explizit kennzeichnen, den Aktionsbutton sicher deaktivieren und Fehler in einer sichtbaren `aria-live`-Region ausgeben. Polling braucht einen sichtbaren Offline-/Abbruchzustand.

---

### F-09 — P2: Prozessübergreifender Datenverlust bei Drafts und Templates

**Datei:** `apps/web/workbench_runtime.py:92-131`

Drafts und Templates verwenden nur `self._lock`, der ausschließlich Threads derselben Instanz schützt. Nur Run-Traces verwenden zusätzlich `_process_lock()`.

**Reproduzierbarer Ablauf:**

1. Zwei App-Prozesse erstellen getrennte `WorkbenchRuntimeStore`-Instanzen auf demselben Root.
2. Beide lesen zeitgleich dieselbe Templateliste.
3. Beide fügen einen unterschiedlichen Eintrag hinzu.
4. Beide ersetzen atomar dieselbe Datei.
5. Der letzte Replace gewinnt; ein Template geht verloren.

Der vorhandene Test `test_workbench_runtime_store_serializes_template_writes` verwendet nur zwei Threads auf demselben Objekt und beweist diese Domäne daher nicht.

**Erforderliche Korrektur:** Auch Draft-/Template-Load-Modify-Replace-Vorgänge unter den jeweiligen Prozesslocks ausführen und mit zwei unabhängigen Prozessen testen.

---

### F-10 — P2: Nebenläufige Scan-Snapshots sind nicht serialisiert

**Datei:** `apps/web/scan_jobs.py:347-355,392-480`

`get()` und `stop()` halten `_lock` nur beim Dictionaryzugriff. `_snapshot()` läuft danach ohne Lock und mutiert unter anderem Dateipositionen, Restpuffer, Stage-Listen, Artefaktpfade und Fortschritt.

**Reproduzierbarer Interleaving:**

1. GET A liest ab Position 0 bis Position X und pausiert vor dem Commit.
2. Neue Ausgabe erscheint.
3. GET B liest ab Position 0 bis Y, setzt Phase/Fortschritt und Position Y.
4. GET A schreibt danach die ältere Position X und einen älteren Stagezustand zurück.
5. Der nächste Poll verarbeitet einen Bereich erneut und sichtbare Telemetrie kann temporär regressieren oder duplizieren.

**Erforderliche Korrektur:** Lookup und kompletten Snapshotzustandsübergang unter einem jobbezogenen Lock ausführen; Prozesssteuerung und Statussnapshot ebenfalls an derselben Grenze ordnen.

---

### F-11 — P2: Unbegrenzte GET-Amplifikation

**Dateien:**  
`apps/web/main.py:353-365`  
`apps/web/reports.py:280-347`

Alle GET-Requests umgehen das Rate-Limit vollständig. Dazu gehören `/api/reports`, dessen Signaturberechnung alle Reportroots rekursiv traversiert, sowie weitere Hardware-/Health-Endpunkte.

**Reproduzierbare Begründung:** Beliebig viele parallele GETs auf `/api/reports` erzwingen Dateisystemtraversierungen, ohne irgendein Lese-, Parallelitäts- oder Kostenbudget zu verbrauchen. Der v5-Vertrag schließt zwar korrekterweise aus, dass GETs das Mutationsbudget verbrauchen; daraus folgt aber nicht, dass teure Reads unbegrenzt bleiben müssen.

**Erforderliche Korrektur:** Mutations- und Lesebudgets trennen; Pollrouten gezielt und kostengerecht behandeln, teure Katalog-/Hardware-Reads begrenzen bzw. cachen.

---

### F-12 — P2: Der produktive Browser kann keinen konfigurierten API-Key senden

**Dateien:**  
`apps/web/static/workbench-api.js:7-47,159-218`  
`apps/web/main.py:506-509,676-678`

Die Browserhelper setzen ausschließlich `Content-Type`; kein geschützter Aufruf sendet `X-API-Key`. Sobald `MORPHIC_API_KEY` aktiviert ist, funktionieren Scanpreview, Scanstart/-polling sowie Harmonisierung aus der offiziellen UI nicht mehr.

**Erforderliche Korrektur:** Einen sicheren lokalen Auth-Transport bzw. eine serverseitige Session etablieren. Den statischen Browser nicht mit einem fest eingebetteten Secret ausliefern.

---

### F-13 — P2: Nicht datensparsamer Initialzustand

**Datei:** `apps/web/static/index.html:220-223,262`

Ein frischer Seitenaufruf enthält bereits Nachname, Vorname, Geburtsdatum, Geburtsort und Fokus. Das sind personenähnliche Werte, obwohl noch keine Einwilligung vorliegt.

**Folgen:**

- unnötige personenbezogene Darstellung im initialen DOM;
- Gefahr, versehentlich den vorbelegten statt des tatsächlichen Falls zu analysieren;
- inkonsistente Datenschutzsemantik: New Case leert dieselben Felder, der erste Seitenaufruf aber nicht.

**Erforderliche Korrektur:** Produktionsformular leer ausliefern; Beispieldaten ausschließlich in ausdrücklich aktivierbaren Demo-/Testfixtures verwenden.

---

### F-14 — P2: Semantisch ungültige Geburtsdaten werden akzeptiert

**Dateien:**  
`apps/web/contracts.py:81-87`  
`tests/test_web_contracts.py:127-133`

Der Validator akzeptiert jedes achtstellige Token, etwa `31022024` oder `00000000`. Diese Werte fließen in stabile Client-IDs, Ownership-/Manifestpfade und den produktiven CLI-Aufruf ein.

**Erforderliche Korrektur:** Mit `datetime.strptime(value, "%d%m%Y")` oder äquivalent validieren und gegebenenfalls fachlich plausible Jahresgrenzen definieren. Tests für unmögliche Tage und Schaltjahre ergänzen.

---

### F-15 — P2: Testevidenz deckt die maßgeblichen Domänen nicht ab

**Dateien:**  
`tests/browser/workbench.spec.js:153-299`  
`tests/test_harmonization_worker_pulse_pause_execution.py:146-174`  
`tests/test_web_workbench_runtime.py:129-176`

Die Freeze-Claims nennen Browser-, Lifecycle-, Prozess- und Race-Abschlüsse, aber es fehlen insbesondere:

- doppelter Harmonisierungsstart und konkurrierende Pollschleifen;
- Mutation, die **nach Beginn** eines New-Case-Teardowns startet;
- Stop genau zwischen terminaler Vorprüfung und `completed`-Publikation;
- produktive gleichzeitige CPU/GPU/RAM-Ausführung;
- App-Neustart während eines laufenden Scans;
- zwei unabhängige Prozesse für Template-/Draft-Schreibkonflikte;
- Authentifizierung der Reportliste, Preview und Datei;
- konkurrierende Scanstatus-Snapshots;
- Obergrenze für `duration_factor`.

Die vorhandenen Browserfälle testen dagegen Mutation-vor-Reset, Scan-Single-Flight und Pending-Polling; der Worker-Test setzt Stop vor dem Cycle-Commit, nicht am späteren terminalen Abschluss; der Template-Test nutzt Threads eines einzigen Storeobjekts.

**Erforderliche Korrektur:** Für jede oben genannte Domäne einen verhaltensbasierten adversariellen Test hinzufügen. Quelltexttoken oder gleiche Objektinstanzen reichen nicht als Race-/Prozessnachweis.

---

### F-16 — P3: Browser- und Backendparametergrenzen divergieren

**Dateien:**  
`apps/web/static/index.html:574-577`  
`apps/web/contracts.py:145,153-155`

Backendgrenzen:

- Frequenz maximal 2000;
- Impuls maximal 5;
- Pause maximal 5.

Die HTML-Inputs besitzen keine entsprechenden `max`-Attribute. Der Browser lässt daher Werte zu, die erst nach dem Request mit HTTP 422 scheitern; dieser Fehler wird wegen F-08 anschließend nicht sichtbar dargestellt.

**Erforderliche Korrektur:** Native Grenzen mit dem Backend synchronisieren, ohne die serverseitige Validierung zu ersetzen.

---

### F-17 — P3: ARIA-Vertrag der Erklärseite ist nur einseitig

**Dateien:**  
`apps/web/static/workflow-stepping.js:37-49`  
`apps/web/static/workflow-stepping.html:26-37`

Die dynamischen Buttons besitzen `aria-controls`, aber keine stabilen IDs. Die kontrollierten Panels besitzen entsprechend kein `aria-labelledby`. Die Haupt-Workbench implementiert diese reziproke Beziehung bereits korrekt.

**Erforderliche Korrektur:** Jedem Workflowbutton eine stabile ID geben und das jeweilige Panel mit `aria-labelledby` darauf zurückbinden.

## 5. Prioritätszählung

| Priorität | Anzahl |
|---|---:|
| P0 | 0 |
| P1 | 7 |
| P2 | 8 |
| P3 | 2 |
| **Gesamt** | **17** |

## 6. Abgleich mit Freeze-v4 und v5-Remediationplan

| v5-Claim | Reviewstatus |
|---|---|
| Pending-Harmonisierung wird weiter gepollt | statisch nachvollziehbar geschlossen |
| Fehlgeschlagener New-Case-Stop behält Generation und Polling | für den getesteten Stopfehler nachvollziehbar; Reset-vs-neue-Mutation bleibt offen, siehe F-03 |
| Scan-Single-Flight | für Scans nachvollziehbar geschlossen; Harmonisierung bleibt offen, siehe F-02 |
| Prozessbaumstop | Implementierung gegenüber v4 deutlich gehärtet |
| Impulsdeadline und Frequenzobergrenze | vorhanden; Dauerfaktor und Mehrfachhardware bleiben offen, siehe F-04/F-05 |
| Stop-vs-Cycle-Commit | Cycle-Commit ist serialisiert; terminaler Completed-Pfad bleibt racy, siehe F-06 |
| Preview-Metadaten | Produktionsshape und Browserzugriff sind angeglichen |
| vollständiger DOM-Scrub | wesentliche Lifecycle-/Previewfelder werden geleert |
| allseitige Security-/Ownership-Grenze | wegen unauthentifizierter Reports nicht erfüllt, siehe F-01 |
| adversarielle Testschließung | nicht erfüllt, siehe F-15 |
| v5-Aggregatrezeptur | korrekt und unabhängig bestätigt |

## 7. Schlussurteil

**REQUEST CHANGES / NO-GO.**

Die Freeze-Bytes waren während des gesamten Reviews stabil: identischer Branch, HEAD, Manifesthash, Aggregat, 47/47 Einzelhashes und exakte Scopepopulation am Anfang und Ende. Das Urteil ist daher vollständig an den angegebenen Freeze v5 gebunden und nicht durch Drift invalidiert.

Eine Freigabe ist wegen **P1=7, P2=8 und P3=2** nach dem ausdrücklich verlangten Nullbefundvertrag ausgeschlossen. Nach Behebung sind eine vollständige neue Regressionsleiter, ein neues Freeze-Manifest und zwei neue unabhängige driftfreie Reviews erforderlich.

## 8. Read-only-Hygiene

- Keine Tests, Imports, Server, Browser, Installationen oder Netzwerkzugriffe wurden ausgeführt.
- Keine Repositorydatei wurde erstellt, verändert oder gelöscht.
- Es wurden ausschließlich Git-Identitäts-/Statusabfragen, SHA-256-Prüfungen, Datei-Lesezugriffe und Quelltextsuchen verwendet.
- Der Workspace blieb bei exakt 48 Dirty-Pfaden und ohne Scope- oder Hashdrift.
- Beim gebündelten Lesen erzeugte die Hermes-Werkzeuginfrastruktur automatisch außerhalb des Repositories eine übergroße Toolausgabe unter `C:/Users/Hubert111/AppData/Local/hermes/cache/terminal/hermes-results/`; sie wurde wegen des absoluten Read-only-/Keine-Löschung-Vertrags nicht entfernt. Im Repository bzw. Worktree entstand kein Cacheartefakt.