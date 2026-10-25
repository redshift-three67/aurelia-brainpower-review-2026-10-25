## Unabhängiges adversariales Review — Operator-Workbench Freeze v5

**Verdikt: REQUEST CHANGES / NO-GO**  
**Confidence: HIGH**

### Befundzahlen

| Priorität | Anzahl |
|---|---:|
| P0 | 0 |
| P1 | 4 |
| P2 | 5 |
| P3 | 1 |
| **Gesamt** | **10** |

---

## 1. Freeze- und Scope-Verifikation

Die Verifikation wurde zu Beginn und unmittelbar vor dem Urteil unabhängig wiederholt.

| Prüfung | START | END |
|---|---|---|
| Repository | `C:/morphic_v1/.worktrees/operator-workbench-phase1` | identisch |
| Branch | `operator-workbench-phase1` | identisch |
| HEAD | `3271ff9366ab3fecb2a158913a0cc19ed6a06726` | identisch |
| Freeze-Manifest | `docs/reviews/2026-07-20-workbench-remediation-technical-freeze-v5.sha256` | identisch |
| Freeze-SHA-256 | `8d4615f6718cb27e7159212fe142c4b544a7c2c05d7a4837b7186295d4dd9078` | identisch |
| Manifestzeilen | 64 | 64 |
| Hash-Einträge | 47 | 47 |
| Population inkl. Manifest | 48 | 48 |
| Aggregat, Zeilen „as listed“ | `2a7e375de48ffced0ac32183d6c7bcb879d1a41942c0a14b8c26885ac9e1d2f3` | identisch |
| Einzelhashes | 47/47 OK | 47/47 OK |
| Live-Scope | 48 geänderte/untracked Pfade | 48 |
| Scopegleichheit | exakt 47 Manifestpfade plus ausschließlich v5-Manifest | exakt |
| Drift | keine | keine |

Die 47 Manifestdateien wurden vollständig gelesen und geprüft. Zusätzlich wurden die produktiven, unveränderten Auth-/Router-Autoritäten `apps/web/security.py` und `apps/web/workbench.py` gelesen, um die im Freeze behaupteten Auth- und Privacy-Verträge bis zum realen Requestpfad zu verfolgen.

Der lexikalisch erneut sortierte Stream ergibt erwartungsgemäß ein anderes Aggregat; maßgeblich ist die dokumentierte, bereits pfadsortierte Reihenfolge „as listed“. Die v5-Rezeptur ist diesbezüglich eindeutig.

---

## 2. Findings

### P1 — Mehrfachstarts von Harmonisierungen erzeugen verwaiste Langzeitprozesse

**Dateien:**  
- `apps/web/static/app.js:562-579`  
- `apps/web/static/workbench-state.js:17`  
- `apps/web/static/app.js:721-727`  
- `services/harmonization_worker.py:739-747`

`startHarmonizationJob()` besitzt im Gegensatz zum Scanstart weder Single-Flight-State noch eine Prüfung auf einen bereits aktiven Harmonisierungsjob. Der Startbutton wird während oder nach dem Start ebenfalls nicht deaktiviert.

Adversarialer Ablauf:

1. Harmonisierung A wird gestartet.
2. Vor oder nach ihrer Antwort wird Harmonisierung B gestartet.
3. B überschreibt den einzigen `activeHarmonizationJobId`.
4. Es existiert nur ein gemeinsamer `harmonizationPollTimer`.
5. New Case stoppt ausschließlich die zuletzt gespeicherte ID.
6. A läuft als `daemon=False`-Worker weiter und kann über viele Minuten oder Stunden produktive CPU-/RAM-Arbeit ausführen.

Die Scan-Single-Flight-Remediation aus V4-06 wurde nicht auf den zweiten produktiven Prozessstarter übertragen.

**Erforderliche Korrektur:** Single-Flight für Startrequest und aktive Laufzeit, Startbutton entsprechend deaktivieren und serverseitig einen Owner-/Report-gebundenen Concurrent-Job- oder Idempotency-Vertrag erzwingen. Alternativ müssen alle aktiven Job-IDs und Pollpfade vollständig verwaltet und beim Fallwechsel gestoppt werden.

---

### P1 — `duration_factor` ist unbegrenzt und ermöglicht praktisch unendliche persistente Worker

**Dateien:**  
- `apps/web/contracts.py:153-155`  
- `apps/web/main.py:524-539`  
- `services/harmonization_worker.py:494-502`  
- `services/harmonization_worker.py:731-745`

`duration_factor` hat nur `ge=1`, aber keine Obergrenze. Der Worker berechnet daraus direkt:

```text
total_seconds = duration_factor × 21 × 60
```

Ein direkter API-Aufrufer kann daher einen extrem großen Integer übergeben und einen praktisch unbegrenzt laufenden, nicht daemonisierten Prozess erzeugen. Das POST-Limit erlaubt zudem bis zu 60 solcher Starts pro IP und Minute. Zusammen mit dem fehlenden Concurrent-Job-Limit ist dies ein konkretes lokales Availability-/Resource-Exhaustion-Risiko.

Die Frequenz- und Puls-/Pausengrenzen schließen V4-04 daher nur teilweise: Ein einzelner Impuls ist kooperativ begrenzt, die Anzahl und Gesamtdauer der Impulse nicht.

**Erforderliche Korrektur:** fachlich begründete Obergrenze für `duration_factor`, serverseitige Concurrent-Job-Quota je Operator/Tenant und atomare Reservierung vor dem Prozessstart.

---

### P1 — Report-Preview-Antworten können sich überholen und den falschen Bericht binden

**Dateien:**  
- `apps/web/static/app.js:489-505`  
- `apps/web/static/app.js:520-557`

`renderReportPreview()` schützt nur gegen einen Fallwechsel über `caseGeneration`. Es gibt keinen Preview-Request-/Selection-Token.

Adversarialer Ablauf:

1. Operator wählt Bericht A; dessen Antwort ist langsam.
2. Operator wählt Bericht B; B wird zuerst gerendert.
3. Die verspätete Antwort von A wird anschließend ebenfalls akzeptiert.
4. A überschreibt Titel, Inhalt, Link und `activeReportId`.
5. Eine anschließend gestartete Harmonisierung wird an A gebunden, obwohl B die jüngste bewusste Auswahl war.

Damit besteht sowohl ein stale-async Preview-Leak als auch eine falsche Selection-to-Action-Bindung. Der vorhandene HTML→Text→HTML-Test prüft nur sequenzielle Antworten und kann diese Race Condition nicht erkennen.

**Erforderliche Korrektur:** monotonen Preview-Request-Token oder AbortController verwenden; nach jedem `await` sowohl Fallgeneration als auch aktuelle Reportauswahl prüfen. Inaktive Preview-Requests abbrechen beziehungsweise ihre Antworten verwerfen.

---

### P1 — Authentifizierungsgrenze ist gespalten: sensible Reads bleiben offen, während der Browser den geschützten Modus nicht bedienen kann

**Dateien:**  
- `apps/web/main.py:480-504`  
- `apps/web/main.py:506-577`  
- `apps/web/main.py:676-747`  
- `apps/web/main.py:426`  
- `apps/web/static/workbench-api.js:7-48`  
- produktive Routerautorität: `apps/web/workbench.py:61-110`  
- Authautorität: `apps/web/security.py:32-52`

Bei gesetztem `MORPHIC_API_KEY` schützen Scan- und Harmonisierungsendpunkte ihre Status-/Mutationspfade. Dagegen haben unter anderem folgende sensible Endpunkte keine `verify_api_key`-Dependency:

- vollständiger Reportkatalog;
- Reportpreview und Reportdatei;
- persistierter Workbench-Draft;
- persistierte Templates;
- Run-Trace.

Der öffentliche Reportkatalog liefert zudem die IDs, mit denen Preview und Datei ohne Auth abgerufen werden können. Die Draft-/Template-Endpunkte können Klientendaten enthalten.

Gleichzeitig fügt `requestJson()` nie `X-API-Key` hinzu und es existiert kein browserseitiger Key-/Session-Mechanismus. Sobald der optionale Authmodus aktiviert wird, bleiben sensible Reads teilweise offen, während legitime Scan-/Harmonisierungsaktionen der Workbench mit 401 fehlschlagen.

**Erforderliche Korrektur:** eine einheitliche Auth-Composition-Root für sämtliche Workbench-, Report-, Draft-, Template-, Trace-, Scan- und Harmonisierungsrouten; der Browser benötigt einen sicheren lokalen Session-/Key-Bootstrap. Keine Secrets in JavaScript-Quelltext oder Local Storage einbetten.

---

### P2 — New Case scrubbt weiterhin nicht alle personenbezogenen DOM-Träger

**Dateien:**  
- `apps/web/static/workbench-render.js:203-224`  
- `apps/web/static/index.html:290-294`  
- `apps/web/static/app.js:771-870`

Der Reset leert viele Lifecycle- und Preview-Felder, aber nicht:

- `#review-client`, `#review-focus`, `#review-profile`, `#review-hardware`;
- die Fokus-Mini-Snapshot-Ausgaben;
- mehrere Statusausgaben für Gruppenentwurf, Identität/Einwilligung, Client-Kontext und Analysepolicy.

Insbesondere die Review-Karten enthalten Name, Geburtsdatum, Geburtsort, Fokus und Hauptsymptom. Diese Daten bleiben nach New Case im versteckten DOM erhalten. Ein späterer Navigations- oder Renderingfehler kann sie erneut sichtbar machen.

Der Browsertest `tests/browser/workbench.spec.js:77-150` injiziert und prüft zahlreiche Lifecycle-Felder, aber keine dieser realen Review-/Mini-Snapshot-/Gruppenstatus-Träger.

**Erforderliche Korrektur:** sämtliche fallbezogenen Text- und Statuscontainer explizit leeren beziehungsweise auf neutrale Defaults setzen; dies mit echten gerenderten Klientendaten behavioristisch prüfen.

---

### P2 — Fehlgeschlagener Zwei-Job-Fallwechsel ist nicht failure-atomic

**Dateien:**  
- `apps/web/static/app.js:705-734`  
- `tests/browser/workbench.spec.js:223-257`

Der Reset stoppt zuerst den Scan und danach die Harmonisierung. Wenn der Scan erfolgreich beendet wurde, aber der Harmonisierungsstop fehlschlägt, liefert der Reset zwar `false` und behält lokale IDs/Generation, der Scan wurde serverseitig jedoch bereits irreversibel gestoppt.

Der Test deckt nur den Fehler beim ersten Scan-Stop ab. Er prüft nicht:

- Scan-Stop erfolgreich;
- Harmonisierungsstop fehlschlägt;
- lokaler Fall bleibt bestehen, aber ein Teil seiner produktiven Arbeit wurde bereits beendet.

Damit ist die dokumentierte „failure-atomic New Case“-Behauptung zu stark.

**Erforderliche Korrektur:** entweder Teardown als explizit partiell-terminalen Ablauf modellieren und UI/Status entsprechend aktualisieren, oder einen serverseitigen gebundenen Teardownvertrag schaffen. Der zweite-Stop-Fehler muss behavioristisch getestet werden.

---

### P2 — Scanstatus mutiert gemeinsamen Jobzustand außerhalb des Service-Locks

**Datei:** `apps/web/scan_jobs.py:347-350,392-461`

`get()` hält `_lock` nur beim Lookup des `_LocalScanJob`. `_snapshot()` verändert anschließend ohne Lock unter anderem:

- stdout-/stderr-Positionen und Puffer;
- aktuelle Phase und Stage;
- Completed-/Seen-Listen und Sets;
- Artefaktpfade;
- Fortschritt und Zeitstempel.

Zwei parallele GETs können daher denselben Offset lesen, unterschiedlich große Chunks sehen und anschließend ältere Progress-/Stage-Daten über einen bereits weiter fortgeschrittenen Snapshot schreiben. Artefakte können ebenfalls doppelt oder in inkonsistenter Reihenfolge aufgenommen werden.

Die GETs sind vollständig vom Rate-Limit ausgenommen, wodurch parallele direkte Polls nicht verhindert werden. Sämtliche Snapshot-Tests sind sequenziell.

**Erforderliche Korrektur:** Lookup und gesamte Snapshot-Mutation unter demselben per-Job- beziehungsweise Service-Lock serialisieren; einen deterministischen Parallel-Poll-Test mit zwischenzeitlich wachsendem Log ergänzen.

---

### P2 — Draft-/Template-Store verliert Updates zwischen mehreren App-Prozessen

**Dateien:**  
- `apps/web/workbench_runtime.py:92-132`  
- `tests/test_web_workbench_runtime.py:129-176`

Nur Run-Traces verwenden `_process_lock`. `save_template()` und `delete_template()` führen dagegen Load→Modify→Replace ausschließlich unter einem instanzlokalen `threading.RLock` aus.

Zwei Uvicorn-Worker oder zwei App-Instanzen mit demselben Runtime-Root können dieselbe Ausgangsliste laden und sich anschließend gegenseitig überschreiben. Der angebliche Serialisierungstest verwendet zwei Threads auf demselben Storeobjekt und beweist keine Prozesssicherheit.

**Erforderliche Korrektur:** denselben Cross-Process-Lock-/CAS-Vertrag für jeden mehrstufigen Draft-/Template-Write anwenden; mit zwei unabhängigen Prozessen oder Storeinstanzen prüfen.

---

### P2 — Mehrere behauptete adversariale Abschlussverträge werden weiterhin nicht in der behaupteten Concurrency-Domain getestet

**Dateien:**  
- `tests/test_harmonization_worker_pulse_pause_execution.py:146-174`  
- `tests/test_workbench_review_regressions.py:232-271`  
- `tests/browser/workbench.spec.js:259-283`  
- `docs/superpowers/plans/2026-07-19-workbench-freeze-v4-review-remediation-v5.md:31-40`

Konkret:

- Der Stop-vs-Cycle-Commit-Test ruft Stop sequenziell aus `capture_realtime_context()` auf; er erzeugt keine konkurrierende Stop-/Commit-Interleaving-Grenze.
- Der stale-save-Test verwendet Threads, obwohl der Claim eine Cross-Process-Grenze betrifft.
- Der stale-bootstrap-Browsertest verzögert ausschließlich den ersten Registry-Request. Der vorausgehende Plan verlangte ausdrücklich eine Verzögerung über die gesamte Bootstrap-Sequenz; spätere Health-, Hardware-, Reports-, Draft-, Gruppen- und Consent-Lader werden nicht adversarial überholt.
- Es gibt keinen Test für doppelte Harmonisierungstarts oder überholende Reportpreview-Antworten.

**Erforderliche Korrektur:** Tests in der tatsächlichen Domain ergänzen: unabhängige Prozesse für File-Lock-Verträge, deterministisch geblockte Commit-Grenze, verspätete spätere Bootstrap-Lader sowie A/B-Completion in beiden Reihenfolgen.

---

### P3 — Freeze-/Plan-Evidenz übertreibt die erreichte Schließung

**Dateien:**  
- `docs/superpowers/plans/2026-07-19-workbench-dogfood-remediation.md:183-185`  
- `docs/superpowers/plans/2026-07-19-workbench-freeze-v4-review-remediation-v5.md:31-43`  
- `docs/reviews/2026-07-20-workbench-remediation-technical-freeze-v5.sha256:7-14`

Die Dokumentation bezeichnet den v5-Kandidaten unter anderem als:

- failure-atomic bei New Case;
- vollständig lifecycle-/preview-gescrubbt;
- mit Stop-vs-Cycle-Commit-Serialisierung behavioristisch geschlossen;
- mit vollständig behavioral geschlossenen Testverträgen.

Die oben belegten Restlücken und Fake-/falsche Concurrency-Domains tragen diese Aussagen nicht. Die aufgeführten Testzahlen können echte beobachtete Läufe sein, beweisen aber nicht die behaupteten adversarialen Eigenschaften.

**Erforderliche Korrektur:** Aussagen bis zur echten behavioristischen Schließung auf „vorläufige Evidenz“ begrenzen und die konkreten Testdomänen exakt benennen.

---

## 3. Trace der Freeze-v4-Befunde

| V4-ID | v5-Bewertung |
|---|---|
| V4-01 Pending-Harmonisierungspolling | produktiv geschlossen |
| V4-02 fehlgeschlagener New-Case-Stop | Generation/Monitoring verbessert; Zwei-Stop-Fehler bleibt nicht failure-atomic |
| V4-03 Scan-Prozessbaumstop | Windows-Pfad substanziell verbessert und real getestet; POSIX weiterhin überwiegend Fake-Domain |
| V4-04 Impulsabbruch | produktive Modulatoren kooperativ begrenzt; unbegrenzter Gesamtfaktor und fehlende Jobquota bleiben |
| V4-05 Stop vs. Cycle-Commit | Implementierung besitzt gemeinsame Lockgrenze; behaupteter deterministischer Race-Test ist nicht konkurrierend |
| V4-06 konkurrierende Scanstarts | für Scans geschlossen; gleiches Problem bleibt bei Harmonisierungen offen |
| V4-07 Preview-Metadatenvertrag | geschlossen |
| V4-08 Lifecycle-DOM-Scrub | bekannte Labels geschlossen; weitere PII-Träger bleiben erhalten |
| V4-09 Previewmodus-Scrub | sequenzieller Moduswechsel geschlossen; A/B-Response-Race offen |
| V4-10 Fake-/Token-Verträge | nur teilweise geschlossen |
| V4-11 Aggregatrezeptur | geschlossen und eindeutig |
| V4-12 Dokumentübertreibung | weiterhin offen |
| V4-13 GET verbraucht Mutationsbudget | umgesetzt; GET besitzt nun überhaupt kein separates Limit, auch nicht für teure/sensible Reads |

---

## 4. Schlussfolgerung

Freeze v5 ist **hash- und scopekonsistent sowie driftfrei**, aber technisch nicht freigabefähig. Besonders blockierend sind:

1. mehrfach startbare und unbegrenzt lange Harmonisierungsprozesse;
2. stale Reportpreview-Antworten mit falscher produktiver Reportbindung;
3. die gespaltene Authentifizierungsgrenze;
4. verbleibende Race-, Privacy- und Evidenzlücken.

**Kein APPROVE. Freeze v5 muss superseded werden; nach Korrektur sind vollständige neue Tests, ein neuer Freeze und zwei neue unabhängige Nullbefund-Reviews erforderlich.**

### Review-Hygiene

- Keine Tests, Imports, Server, Netzwerkaufrufe, Installationen oder Applikationsprozesse ausgeführt.
- Keine Repositorydateien erstellt, geändert oder gelöscht.
- Keine projektbezogenen temporären Dateien oder Cacheartefakte erzeugt.
- Ausschließlich lesende Datei-, Git-, Such- und SHA-256-Operationen verwendet.
- Einzige beobachtete Besonderheit: harmlose Git-LF/CRLF-Warnungen; keine Byte- oder Scope-Drift.