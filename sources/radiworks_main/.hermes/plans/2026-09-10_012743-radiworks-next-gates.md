# RadiWorks: nächste Umsetzungs-Gates

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Den bereits weit fortgeschrittenen lokalen RadiWorks-Prototypen zuerst zu einem nachweisbar konsistenten R0/R1-Zwischenstand führen, bevor R2-Funktionen oder neue Produktmerkmale begonnen werden.

**Architecture:** Der aktuelle Arbeitsstand enthält gleichzeitig Reliability-, Persistenz-, Paritäts- und UI-Änderungen (39 versionierte Dateien, ca. +4.600/-920 Zeilen, zusätzlich neue untracked Kernmodule). Deshalb darf der Roadmap-Abschnitt nicht als linear abgeschlossen betrachtet werden. Die nächste Arbeit erfolgt als kleine, hashgebundene TDD-Gates; jedes Gate hat einen schmalen Invariantensatz und eine volle Regression, aber keine implizite Historien- oder Produktentscheidung.

**Tech Stack:** Python 3.12+, FastAPI, pytest, Vanilla JavaScript, Browser-Contract-Tests, Java/JDK-Gold-Orakel.

---

## Ausgangslage

- `R0` der `radiworks_port/ROADMAP.md` ist teilweise im uncommitted Stand umgesetzt: Auto-Modus, Broadcast-/WebSocket-/Recovery- und Frontend-Arbeiten liegen nicht isoliert vor.
- Die Roadmap ist sinnvoll geschichtet (R0 Reliability → R1 Verträge → R2 Persistenz → R3 Produktentscheidungen), deckt aber die aktuelle statische Tiefenanalyse nicht vollständig ab.
- Kein neuer Produktumfang, keine R2-Erweiterung, kein Commit/Push und keine History-Bereinigung, bevor der gegenwärtige Änderungsstand fachlich und technisch geschlossen bewertet wurde.
- Die Auditbefunde sind statisch. Ihre Umsetzung startet mit reproduzierbaren RED-Verträgen, nicht mit einer großflächigen Umstrukturierung.

## Reihenfolge und Entscheidungslogik

1. Bestehenden R0/R1-Mischstand zuerst einfrieren und testbar machen.
2. Danach Datenintegrität an der Schnittstelle Fall → Session → GV → Draft → Broadcast korrigieren.
3. Danach UI-Sicherheits- und Ressourcenlebenszyklus schließen.
4. Erst dann die Produktentscheidung „nur vertrauenswürdiger Loopback-Betreiber“ versus „authentisierte Netzwerk-/Mandantenanwendung“ treffen.
5. R2 erst beginnen, wenn der gewählte Sicherheits- und Autoritätsvertrag aktiv durchgesetzt wird.

## Gate 0: Change-Scope-Freeze und belastbare Basis

**Objective:** Den vorhandenen, großen uncommitted Stand ohne Quellmutation eindeutig als Arbeitsbasis erfassen und R0-Fertigstellung von R1-/R2-Anteilen trennen.

**Files:**
- Read: `radiworks_port/ROADMAP.md`
- Read: `radiworks_port/engine/PARITY_MATRIX.md`
- Read: alle derzeit geänderten/untracked Dateien unter `radiworks_port/engine/` und `radiworks_port/webapp/`
- Create: eine ausschließlich technische Gate-Evidenz außerhalb der produktiven Quellen oder nach ausdrücklicher Freigabe im Dokumentationspfad

**Steps:**
1. Erzeuge eine kanonische In-Scope-Dateiliste mit SHA-256 pro geänderter und untracked RadiWorks-Datei.
2. Trenne Dateien in R0 Reliability, R1 Vertrags-/Paritätsarbeit, R2-Persistenzvorgriff und Hygiene/Artefakte.
3. Führe ausschließlich in isoliertem Runtime-Home die bestehende Engine-Test-Suite, JavaScript-Syntaxprüfungen und eine kurze Loopback-Smoke-Prüfung aus.
4. Prüfe vor/nach jedem Testlauf den Projektscope; Runtime- oder Cache-Nebenartefakte nur klassifizieren, nicht löschen.
5. Stoppe mit NO-GO, falls die Basis nicht grün ist oder Source-/Statusdrift auftritt.

**Verification:**
- vollständige Hashliste und Statusfingerprint vor/nach
- `pytest` vollständig grün
- alle Webapp-JS-Dateien bestehen `node --check`
- kurzer Server-/HTTP-/WebSocket-Smoke nur auf freiem Loopback-Port

## Gate 1: Fall-, Session-, GV- und Draft-Autorität

**Objective:** Sicherstellen, dass eine angezeigte oder freigegebene Analyse immer genau dem aktiven Fall, der gewählten Session und der aktuellen GV-Revision gehört.

**Files:**
- Modify: `radiworks_port/engine/src/radiworks/core/gvround.py`
- Modify: `radiworks_port/engine/src/radiworks/core/cases.py`
- Modify: `radiworks_port/engine/src/radiworks/core/draft.py`
- Modify: `radiworks_port/engine/src/radiworks/api/routes.py`
- Modify: `radiworks_port/webapp/js/views/analyze.js`
- Modify: `radiworks_port/webapp/js/views/cases.js`
- Test: `radiworks_port/engine/tests/test_session_persistence.py`
- Test: `radiworks_port/engine/tests/test_api.py`
- Create/Test: gezielte Browser-unabhängige JS-Contract-Probe für Case-/Sessionwechsel

**Steps:**
1. Schreibe RED-Tests: GV-Schritt aktualisiert sowohl Snapshot als auch persisted Draft-Projektion konsistent.
2. Schreibe RED-Tests: historisches Session-Viewing darf keine Draft-ID, Freigabeaktion oder Analysewerte aus einem anderen Fall weiterverwenden.
3. Definiere einen expliziten Bindungswert (`case_id`/Sessionrevision/Draft-ID) statt impliziter „letzter Draft“-Semantik.
4. Ändere API und UI minimal, sodass Wechsel die Analyseansicht vollständig in einen neutralen oder exakt gebundenen Zustand versetzt.
5. Schreibe RED-Tests für Case-Overwrite: eine allgemeine Case-Änderung darf Sessionhistorie nicht unbemerkt ersetzen.
6. Führe für Sitzungshistorie eine revisionsgesicherte Mutation oder eine explizite Konfliktantwort ein; keine globale Neuarchitektur der JSON-Persistenz in diesem Gate.

**Verification:**
- gezielte RED→GREEN-Tests
- `test_session_persistence.py`, `test_api.py`, `test_draft.py`, `test_stufe3.py`
- vollständige Suite

## Gate 2: Promotion-/Broadcast-Transaktion und Workflow-Serialisierung

**Objective:** Promotion und Aussendung dürfen weder doppelt noch teilweise als erfolgreich erscheinen; Fallwechsel und Analyse dürfen keine Zustände vermischen.

**Files:**
- Modify: `radiworks_port/engine/src/radiworks/core/draft.py`
- Modify: `radiworks_port/engine/src/radiworks/core/broadcast.py`
- Modify: `radiworks_port/engine/src/radiworks/api/routes.py`
- Modify: `radiworks_port/engine/src/radiworks/persistence.py`
- Test: `radiworks_port/engine/tests/test_broadcast.py`
- Test: `radiworks_port/engine/tests/test_recovery_persistence.py`
- Test: `radiworks_port/engine/tests/test_api.py`

**Steps:**
1. Schreibe RED-Tests für Enqueue-Fehler und mehrere Einträge: Draft darf erst als promoted gelten, wenn der definierte atomare Erfolg erreicht wurde; Teilerfolg muss sichtbar/retrybar sein.
2. Schreibe RED-Test für zwei konkurrierende Promote-Aufrufe desselben Drafts.
3. Definiere eine idempotente Promotion anhand einer stabilen Promotion-ID oder eines Zustandsvergleichs; keine bloße Prozesslokal-Sperre als alleinige Lösung.
4. Schreibe RED-Test für Analyse parallel zu Fallwechsel/GV-Schritt.
5. Führe eine schmale Workflow-/Case-Revision-Grenze am API-Pfad ein, die Konflikte explizit meldet statt falsche Zuordnung zu persistieren.
6. Prüfe, ob `ScopeResolver`/`WorkflowRegistry` dabei integriert oder bewusst entfernt/deprecated werden; keine tote Sicherheitsarchitektur behalten.

**Verification:**
- Fehler- und Paralleltests deterministisch
- Recovery-Fault-Test ohne Datenverlust bzw. ohne als erfolgreich markierte Teiloperation
- vollständige Engine-Suite

## Gate 3: Frontend-Sicherheits- und Datenschutzschluss

**Objective:** HTML-Sinks, Kameraressourcen und Backendzielwahl erhalten einen expliziten sicheren Vertrag.

**Files:**
- Modify: `radiworks_port/webapp/js/views/analyze.js`
- Modify: `radiworks_port/webapp/js/views/entropy.js`
- Modify: `radiworks_port/webapp/js/api.js`
- Modify: `radiworks_port/webapp/js/views/peggotty.js`
- Modify: `radiworks_port/webapp/js/views/statusbar.js`
- Test/Create: JS-Contract-Proben unter `radiworks_port/engine/tests/` oder ein klar abgegrenzter Webapp-Testpfad

**Steps:**
1. Schreibe RED-Test, der bösartige Clarke-/Materia-Felder liefert und beweist, dass sie nicht als HTML interpretiert werden.
2. Ersetze dynamisches `innerHTML` für untrusted Werte durch DOM-Knoten und `textContent`; statisches Markup bleibt getrennt.
3. Schreibe RED-Test für Start→Start→Stop und Start→Stop→verzögertes Medienversprechen.
4. Führe generation-/abort-basierte Kameraautorität ein; Stop muss sämtliche bekannten und verspätet erzeugten Tracks sicher schließen.
5. Definiere API-/WS-Origin-Policy: im Local-only-Modus keine beliebigen Queryparameter-Ziele; falls konfigurierbar erforderlich, nur sichere Allowlist/Build-Konfiguration.
6. Vereinheitliche alle Fetches auf den API-Client inklusive `response.ok`, Timeout und sichtbarer Fehlerdarstellung.

**Verification:**
- Node-basierte Contract-Proben grün
- `node --check` für alle Dateien unter `webapp/js/`
- manueller Browser-Smoketest für Kamera (explizite Einwilligung), Fallwechsel, Analyse und Broadcast

## Gate 4: Expositions- und Scope-Produktentscheidung

**Objective:** Das Sicherheitsmodell verbindlich festlegen, bevor eine Netzfreigabe oder Mehrbenutzerfähigkeit behauptet wird.

**Decision required:**
- A: ausschließlich lokaler Einzelbetreiber auf Loopback, keine Netzwerkunterstützung
- B: authentisierte, autorisierte und mandantenisolierte Betreiber-/Netzwerkanwendung

**Files (Option A):**
- Modify: `radiworks_port/engine/run.py`
- Modify: `radiworks_port/engine/src/radiworks/main.py`
- Modify: `radiworks_port/engine/README.md`

**Files (Option B, separates Großgate):**
- Modify: `main.py`, `api/routes.py`, `scope.py`, `workflow.py`, WebSocket-Handshake, alle Case-/Draft-/Journal-Pfade
- Create: zentrale Auth-/Identity-/Authorization-Schicht und vollständige Tenant-Persistenzmigration

**Steps:**
1. Entscheide A oder B schriftlich und prüfbar.
2. Bei A: nicht-loopback Bindung ablehnen oder nur mit explizitem, dokumentiertem unsicherem Development-Schalter zulassen; Query-Backend-Override entfernen; lokale Trust-Grenze dokumentieren.
3. Bei B: nicht mit Header-`tenant_id` starten. Erst Auth- und vertrauenswürdige Identitätsquelle, danach serverseitige Scope-Ableitung und Datenmigration.
4. Ergänze Negativtests für nicht autorisierte HTTP- und WebSocket-Zugriffe bzw. für verbotene Netzbindung.

**Verification:**
- Sicherheitsvertrag als Test, nicht nur README-Aussage
- jede HTTP- und WebSocket-Route in der gewählten Grenze geprüft

## Gate 5: Entropie- und Paritätsabschluss R1

**Objective:** Reproduzierbarkeit präzise halten und stochastic-Betrieb robust machen, ohne Java-Parität pauschal auszuweiten.

**Files:**
- Modify: `radiworks_port/engine/src/radiworks/entropy.py`
- Modify: `radiworks_port/engine/src/radiworks/core/javahashmap.py`
- Modify: `radiworks_port/engine/PARITY_MATRIX.md`
- Test: `radiworks_port/engine/tests/test_entropy.py`
- Test/Create: Gold-Orakel-Fixtures und Paritätstests

**Steps:**
1. Schreibe RED-Test: random.org-Ausfall erzeugt höchstens einen begrenzten Versuch pro Backoff-Fenster; OS-Fallback bleibt verfügbar.
2. Ersetze ungebremste Refill-Versuche durch klaren Backoff/Circuit-Breaker und begrenze Cacheoperationen.
3. Entscheide, ob shared Entropy-Provider synchronisiert oder je Workflow isoliert werden; dokumentiere die Replay-Grenze.
4. Erzeuge vor jeder HashMap-/Treeify-Behauptung ein unabhängiges JDK-Orakel; implementiere keinen Scheinnachbau ohne Fixture.
5. Aktualisiere `PARITY_MATRIX.md` nur mit tatsächlich grün ausgeführten Evidenzen.

**Verification:**
- Ausfall-/Backoff-Test
- vorhandene drei seeded REST-Gold-Fixtures grün
- neue Orakelfixtures nur mit überprüfbar versioniertem JDK-Harness

## Danach: R2 und R3

Erst nach Gates 0–5 fortsetzen:

1. R2: Datenbereitstellung, Settingsvertrag, Draft-TTL/Archiv und weitergehende Sessionrevisionen.
2. R3: Card Generator, Resonanzprotokoll, Duplicate-Start-Guard, MapDesign, Watchlist, SQLite FTS5 – jeweils erst nach ausdrücklicher Produktumfangsentscheidung.
3. Repository-/Datenschutzhygiene: Screenshots nur nach einer separaten datenschutzrechtlichen Sichtung und einer expliziten Entscheidung über Historienbereinigung behandeln.

## Risiken und Nicht-Ziele

- Keine Behauptung medizinischer Wirksamkeit; die technische Arbeit betrifft Konsistenz, Sicherheit und transparente Simulation.
- Kein Big-Bang-Wechsel von JSON zu Datenbank im laufenden Reliability-Sprint.
- Keine Auth-/Mandanten-Simulation über frei lieferbare Header.
- Keine pauschale Java-1:1-Aussage über den Umfang der versionierten JDK-Oracle-Fixtures hinaus.
- Keine Commit-/Push-/History-Änderung als impliziter Schritt.

## Empfohlener Start

Start mit Gate 0. Wenn die aktuelle Basis grün und driftfrei ist, Gate 1 als nächstes produktives TDD-Gate: zuerst die GV-/Draft-Bindung im Backend, dann der Fall-/Sessionwechsel in der UI. Das reduziert das aktuell größte Risiko falscher Ergebnis- oder Freigabezuordnung, ohne bereits eine noch nicht entschiedene Netzwerk-/Tenant-Architektur vorwegzunehmen.
