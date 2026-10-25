# RadiWorks – strategischer Optimierungsplan

## Prüfgrenze

Statische, rein lesende Architekturprüfung des Repository-Snapshots `main` / `067b1142ec02f4db3b590b1d9e4c8cbc7c578284`.

Es wurden weder Anwendung, Test-Suite, Server, Browser, Importprobe oder Formatter ausgeführt noch Pakete installiert, Commits erstellt oder Quellcode verändert. Dieses Dokument ist die einzige angeforderte Dateiänderung. Aussagen zu Laufzeit, Nebenläufigkeit und Browserverhalten sind daher statische Schlussfolgerungen, keine Ausführungsbelege.

Der Arbeitsbaum war bereits vor der Prüfung wesentlich verändert: 59 Einträge im vollständigen Status, darunter 39 veränderte getrackte Dateien in `radiworks_port`, gelöschte generierte Gold-/egg-info-Artefakte sowie neue, noch nicht getrackte Engine-Module und Tests. Die Architekturbeobachtungen sind an folgende vor dem Schreiben dieses Dokuments erfasste Quellhashes gebunden:

| Pfad | SHA-256 |
|---|---|
| `radiworks_port/engine/pyproject.toml` | `1c8c164dac31aede7b189cfc35eb6d16107edd3ebf7c6cd39ff1de4f37bf9c62` |
| `radiworks_port/engine/run.py` | `d35627ec212b0dfe42263a261c6d658bfc48fa4e7566ddcc3ff75106edc0720d` |
| `radiworks_port/engine/src/radiworks/main.py` | `19290ae667bcc8d26bffd31025fa9576a1b8ca95127df8bd84b17631390d7f84` |
| `radiworks_port/engine/src/radiworks/api/routes.py` | `64da4796672d1b113b49a1f74d448c75030c5efeaaea0885b4fe1ff66186949a` |
| `radiworks_port/webapp/index.html` | `ef4e091b331aa60674c8d941306b9626cc8aed9087d91b5cee7e10579507f9ec` |
| `radiworks_port/webapp/js/api.js` | `658903338c0d718f1593b31c53bcf1f5a48f3008e11330499c11ea793356b8af` |

## 1. Repository-Topologie und Grenzen

| Grenze | Verifizierte Rolle | Autorität / Abhängigkeit | Konsequenz für die Optimierung |
|---|---|---|---|
| Repository-Wurzel | Dekompilierte Java-Anwendung bzw. Referenzkorpus mit umfangreichen Drittanbieter-Paketbäumen | 7.184 getrackte `org/`-Dateien, 3.124 `com/`-Dateien, 1.008 Clarke-Datensätze sowie native/binäre Artefakte und Dokumentation | Als Referenzevidenz behandeln, nicht als veränderbare Produktgrenze. Git-Befehle immer auf das Teilprojekt beschränken. |
| `radiworks_port/` | Aktiver Python-/FastAPI-Port mit Browser-Werkbank | 83 getrackte Dateien, rund 76 MiB | Primäre Produktgrenze; muss unabhängig baubar, testbar und auslieferbar werden. |
| `radiworks_port/engine/` | Kernel, HTTP-/WebSocket-API, Persistenz, Algorithmusport, Tests und Java-Gold-Harness | Python >=3.12, FastAPI, Uvicorn, websockets, httpx, cryptography; pytest als optionale Dev-Abhängigkeit (`pyproject.toml:5-15`) | Laufzeit- und Fachgrenze. Algorithmusäquivalenz strikt von API-, Speicher- und Produktfunktionsarbeiten trennen. |
| `radiworks_port/webapp/` | Statische ES-Modul-Oberfläche, durch die Engine ausgeliefert | Unter `/` eingehängt (`main.py:219-230`); API-Basis per Injektion/Query konfigurierbar (`webapp/js/api.js:12-30`) | Heute lokale Same-Origin-Bedienoberfläche; kein eigenständig gehärteter Multi-Tenant-Client. |
| Runtime-Home | Betreiberdateien: Fälle, Drafts, Settings, Recovery-Marker, verschlüsselte Entropiejournale und optionaler Ratenkatalog | `RADIOWORKS_HOME`, Standard `~/.radiworks` (`main.py:48-57`) | Richtigerweise außerhalb des Checkouts; Eigentümerschaft und Zugriffsschutz der dauerhaften Daten müssen vor breiterem Einsatz geschlossen werden. |
| Externer Ratenkatalog | Optionaler read-only Katalog über `RADIOWORKS_DATA_DIR` | Repository liest rekursiv `.txt`- und `.rscript`-Dateien (`core/rates.py:37-102`) | Import- und Vertrauensgrenze. Herkunft/Validierung der Betreiberinhalte von Algorithmusparität getrennt behandeln. |

Ermittelter Umfang: Engine-Quellen 5.974 LOC, Engine-Tests 3.614 LOC, UI-JavaScript 2.518 LOC und UI-CSS 660 LOC. Das Test-zu-Quell-Verhältnis ist positiv, beweist aber keine Lauffähigkeit, da die Suite absichtlich nicht gestartet wurde.

## 2. Systemmodell und Kerninvarianten

```text
Browser-Oberfläche
  -> REST-Client + reconnectender WebSocket-Client
  -> FastAPI-Router / AppState im Speicher
  -> Algorithmusdienste + Draft-/Fall-/Broadcast-Zustand
  -> JSON-Dokumente im Runtime-Home / verschlüsseltes Journal

Externer Ratenkatalog -> RateRepository -> Analyse/Auto/Skript/Training
Clarke-Korpus --------> MateriaMedica -> Suche/Vergleich
Java-Referenz --------> Gold-Fixtures/Harness -> seeded-Paritätstests
```

| Invariante | Beleg | Erforderliche Bewahrung |
|---|---|---|
| Seeded-Entropie ist reproduzierbarer Standard; stochastic ist explizit und nicht replaybar | `entropy.py:20-21,123-250`; `README.md:47-75` | Stochastic-Verhalten nicht in Paritätsbehauptungen mischen. Modus und wirksamen Seed in jeder Analyseprovenienz bewahren. |
| Die Analyse ist eine begrenzte, im Seed-Modus deterministische Pipeline | `core/analysis.py:154-221`; Ergebnislimit 105 in `:20,215` | Java-PRNG- und Java-HashMap-Reihenfolge getrennt von sonstigem Verhalten absichern. |
| Eine Analyse erzeugt vor dem regulären Broadcast einen prüfbaren Draft | `core/draft.py:1-12,29-35,290-328`; Routen `:1250-1298` | Zustandsautomat und CopyGuard-Prüfung auf allen Standard-Promote-Pfaden erhalten. |
| Fall-Sessions sind append-orientiert und versioniert | `core/cases.py:162-209,230-263`; `core/gvround.py:45-100` | Baseline/Ergebnis-Trennung, Session-IDs, Revisionsprüfungen und Nachfolge-Drafts bei Änderungen bewahren. |
| Mehrdatei-Änderungen an Fall und Draft sind wiederherstellbar oder fail-closed | `persistence.py:84-193`; Analysefluss `api/routes.py:597-646` | Jeder neue gekoppelte Zustand muss dasselbe Recovery-Protokoll oder eine gleichwertige atomare Autorität nutzen. |
| Broadcast ist servergetaktet, simuliert und ereignisbasiert | `core/broadcast.py:8-14,130-428`; Manifest `:146-172` | Keine physische Ausgabe behaupten. Hardwareaktivierung benötigt eine getrennte Lease-/Arming-/ACK-Autorität. |
| WebSocket-Event-IDs sind bootbewusst und begrenzt | `api/routes.py:67-75,190-315,1445-1572`; UI-Client `api.js:190-275` | Monotone IDs pro Boot, explizite Replay-Lücke, begrenzte Sender-Queues und REST-Abgleich erhalten. |
| Betreiberdateien dürfen nicht in den Checkout geschrieben werden | `main.py:48-57`; Engine-README `:23-41` | Runtime-Home extern halten und neue Helfer am stillen Auflösen in Projektpfade hindern. |
| Wellbeing-/klinische Aussagen bleiben eingeschränkt | `copyguard.py:1-74`; UI-Hinweise `index.html:112-115,526-529` | CopyGuard ist ein lexikalisches Gate, keine klinische Validierung und keine Autorisierung. |

## 3. Abhängigkeits- und Ausführungspfad

### Steuerungsebene der Engine

1. `engine/run.py:34-74` löst Runtime-, Daten-, Clarke- und Webapp-Pfade auf, kann einen synthetischen Katalog bootstrappen, erzeugt die App und startet Uvicorn.
2. `main.create_app()` erzeugt Repositories, Stores, Recovery-Koordinator, MateriaMedica, Settings, Broadcast-Manager und Auto-Modus-Regler (`main.py:88-150`).
3. Der FastAPI-Lebenszyklus repariert offene Mehrdatei-Änderungen, aktiviert den globalen Kompatibilitätszustand, aktualisiert Raten-/Materia-Indizes und beendet Auto-, Broadcast- und WebSocket-Zustand (`main.py:152-173`).
4. `api/routes.py` ist die einzige produktive HTTP-/WebSocket-Kompositionswurzel: 1.572 LOC für API-Modelle, App-Zustand, lebenszyklussensitiven WebSocket-Transport, Orchestrierung, Persistenzkoordination und alle Route-Handler.

### Analyse- und Dokumentationsfluss

```text
POST /analysis
  -> RateRepository-Präfix-/Exaktsuche
  -> Entropieprovider (seeded/stochastic)
  -> Passport-Eingabe-/Provenienz-Hash
  -> analyse_rate_list()
  -> CopyGuard-Digest
  -> transienter Draft-Plan
  -> optionaler Fall-Session-Plan
  -> RecoveryCoordinator schreibt Draft- und Fall-Endzustand
  -> GvRoundState im Speicher + analysis.update-WebSocket-Event
```

Der Draft durchläuft `draft -> client_review -> ready -> promoted | discarded`. Das reguläre Promote ist die Grenze zur Erzeugung von Broadcast-Einträgen. Ein Legacy-Einklickpfad existiert, ist aber standardmäßig über `broadcast.legacyMixMode` deaktiviert (`api/routes.py:1318-1356`).

### UI-Fluss

`webapp/js/boot.js:87-120` erzeugt einen API-Client und Event-Bus, verbindet den WebSocket und installiert die View-Module. Die Analyse-View bündelt unverhältnismäßig viel Verhalten: Request-Zustand, Tabellenrendering, direkte Einzelraten-Broadcasts, Draft-Zustand, GV-Fortschritt, Auto-Modus-Kommandos und -Abgleich, Clipboard-Export, Sessions und Fallbearbeitung (`webapp/js/views/analyze.js`, 850 LOC). Dies ist die zentrale Frontend-Kohäsionsgrenze.

## 4. Befunde und Architektur-Risiken

Die Schwere beschreibt die Umsetzungspriorität, nicht eine Behauptung über eine beobachtete Ausnutzung oder Laufzeitstörung.

| ID | Schwere | Befund | Beleg | Folge | Empfohlenes Gate |
|---|---|---|---|---|---|
| F-01 | hoch | Scope-Enforcement existiert als abgekoppeltes Primitive, nicht als produktive HTTP-Workflow-Autorität. | `scope.py:47-78` löst lokale/erzwungene Scopes, `workflow.py:24-59` partitioniert Stores. Ihre einzigen Quellnutzungen liegen in eigenen Modulen und Store-Konstruktoren; `main.py:105-112` erzeugt ungescopte Stores, während `api/routes.py` Tenant-/Client-Werte direkt annimmt (`:351-358,537-571`). | Ein `enforced`-Environment-Setting schützt produktive REST-/WebSocket-Lese- und Schreibzugriffe nicht. Request-gelieferte Tenant-/Client-Metadaten können ohne erzwungene Speicherisolation aufgezeichnet werden. | G1: Produktive Fall-/Draft-/Recovery-Autorität auf request-gescopten Workspace-Resolver umstellen; in enforced fail-closed; REST- und WebSocket-Querscope-Verträge ergänzen. |
| F-02 | hoch | Die API ist nicht authentifiziert; Standard-CORS deckt mehrere localhost-Ursprünge ab, während Fälle, Drafts, Settings, Entropiefeed, Broadcasts und WebSockets veränderbar sind. | `main.py:38-45,210-217`; Routendefinitionen in `api/routes.py`. Keine Authentifizierungs-/Autorisierungsabhängigkeit in `pyproject.toml:6-12` oder Handlern. | Nur innerhalb einer vertrauenswürdigen lokalen Einzelbetreiber-Prozessgrenze vertretbar. Jede Erweiterung des Host-Binds, Browser-Embeddings oder nichtlokalen Einsatzes braucht ein explizites Sicherheitsmodell. | G0: unterstützte Deploymentgrenze dokumentieren und testen. Bei nichtlokalem Einsatz Session-Transport, Origin-/Host-Politik, CSRF, WebSocket-Autorisierung, Redaction und Owner-Prüfungen vor neuen Funktionen definieren. |
| F-03 | hoch | `GET /settings` verändert das Runtime-Dateisystem, weil selbst-defaultende Getter Defaults persistieren. | `api/routes.py:876-906`; `config.py:39-90`. | Ein nomineller Leseendpunkt hat Schreibnebenwirkungen und erschwert Backup, Berechtigungen, Audit, Recovery und sichere Prüfung. | G2: Default-Materialisierung zu explizitem Schreib-/Migrationsvorgang machen; Werte ohne GET-Schreiben zurückgeben; No-Mutation-Tests ergänzen. |
| F-04 | hoch | `AppStateHolder` bleibt globaler Kompatibilitätszeiger; der App-Zustand enthält genau einen aktuellen Fall, GV-Runde, Trainingssignatur und Auto-Regler. | `api/routes.py:325-345`; `main.py:120-150`; Lebenszyklus `main.py:152-173`. | Gleichzeitige Betreiber oder Tenants erhalten über die aktive API keinen isolierten veränderbaren Workflow-Zustand. Das vorhandene Scope-Workspace-Design schließt diese Lücke nicht. | G1: ein Ownership-Modell pro Request/Workflow festlegen. Globale Zustandsabhängigkeit erst nach Verträgen für parallele App-/Betreiberfälle entfernen. |
| F-05 | mittel | Die statische UI akzeptiert API-/WebSocket-Ziele per Query-Parametern und verwendet Wildcard-`postMessage` für Theme-Kommunikation. | `webapp/js/api.js:12-30`; `webapp/js/boot.js:27-33`. | Flexibel für Embedding, aber ohne Origin-Allowlist. Bei künftiger Authentifizierung oder nichtlokalem Einsatz entsteht ein Confused-Deputy-/Exfiltrationsrisiko. | G0/G3: explizite unterstützte Embedding-Ursprünge und Protokolle wählen; beliebige Endpoint-Overrides in Produktionsbuilds verbieten. |
| F-06 | mittel | Vom Server gelieferte Katalog-/Materia-Werte werden im Clarke-Dialog mittels `innerHTML` interpoliert. | `webapp/js/views/analyze.js:340-360`; Werte kommen über externe Datenpfade aus `core/materia.py:101-134`. | Ein böswilliger oder defekter externer Katalog kann einen Server-zu-Browser-HTML-Sink erreichen. Die Suchmethode escaped ihr Highlighting (`materia.py:164-171`), der Vergleichsdialog belegt dies nicht gleichwertig. | G3: HTML-String-Rendering durch DOM-APIs und `textContent` ersetzen; feindliche Remedy-/Symptom-Fixtures testen. |
| F-07 | mittel | `routes.py` ist ein 1.572-LOC-Kompositions-, Transport- und Workflow-Modul; `analyze.js` ein 850-LOC-UI-Controller mehrerer Domänen. | Dateigrößen und Quellenprüfung. | Hohe Regressionskopplung: Änderungen an Lifecycle, Sicherheit, Persistenz oder Analyse können fachfremde Bereiche und Tests treffen. | G4: zunächst verhaltensbewahrende Route-/Service-Seams und Frontend-Controller hinter Vertragstests erzeugen; kein breiter Rewrite. |
| F-08 | mittel | Runtime-Persistenz verwendet unterschiedliche Haltbarkeitsprimitive. Fall/Draft/Recovery nutzen fsync plus replace; Settings nutzt direktes `write_text`. | `persistence.py:52-73`; `config.py:39-54`. | Unterschiedliches Power-Loss-/Korruptionsmodell; fehlerhafte Settings werden still zurückgesetzt (`config.py:30-37`). | G2: Settings über dieselbe atomare Dokumenthilfe schreiben und fail-closed- versus Quarantäne-Politik festlegen. |
| F-09 | mittel | Stochastic-Entropie kann während eines Requests einen synchronen random.org-Netzaufruf ausführen. | `entropy.py:52-91,167-179`; `RANDOM_ORG_TIMEOUT_S = 2.0`. | Unter Last kann ein externer I/O-Aufruf den Request-Handling-Thread blockieren; Budget/Circuit-Breaker ist nicht ausgedrückt. | G5: Entropiebeschaffung mit begrenzten Timeouts, Cache und Beobachtbarkeit isolieren; Offline-Garantie für seeded bewahren. |
| F-10 | mittel | `RateRepository` liest alle Katalogdateien rekursiv und stellt benannte Skripte zur Ausführung bereit; Herkunft, Größenbudgets und Skriptpolitik des externen Katalogs sind nicht explizit. | `core/rates.py:37-102`; Skriptrouten `api/routes.py:952-986`. | Betreiberkatalog ist zugleich Eingabedaten- und ausführungsnahe Autorität. Leseprobleme werden derzeit als leere Ergebnisse behandelt. | G5: Katalogmanifest/Herkunft, Größen-/Encodinglimits, zugelassene Skriptquellen, read-only Behandlung und sichtbare Fehler-/Quarantänezustände definieren. |
| F-11 | mittel | Dokumentierte Testabdeckung konzentriert sich auf Unit-/Contract-Fixtures; vollständige Deploymentkompatibilität ist statisch nicht bewiesen. Die Engine fordert Python >=3.12, der aktuelle Host meldet Python 3.11.16. | `pyproject.toml:5,14-15`; isolierte TestClient-Fixture `tests/conftest.py:12-64`. | Aus dieser Prüfung ist keine Laufzeitaussage zulässig. Ein falscher Interpreter ist auf diesem Host ein absehbarer Gate-Fehler. | G6: saubere Python-3.12-Umgebung, fixierter Dependency-Lock, isoliertes Runtime-Home, Port-Preflight sowie getrennte Unit-/Integration-/Browser-/Paritätsevidenz. |
| F-12 | niedrig | README-/API-Kommentare verweisen auf fehlende `Modul_Templates`-/Aurelia-Pfade; die Repository-Wurzel wird von dekompiliertem Referenzmaterial dominiert. | `engine/README.md:20-22,43-53`; `api/routes.py:1-9`; `ROADMAP.md:67-71`. | Normative Vertragsbelege, Zielbild und historische Referenz sind für neue Bearbeiter nicht zuverlässig unterscheidbar. | G7: lokalen, autoritativen Dokumentationsindex erstellen; reine Referenzpfade markieren und defekte Verweise erst nach Link-Inventar korrigieren. |
| F-13 | niedrig | Hygiene generierter Artefakte ist im schmutzigen Arbeitsbaum noch offen. | Gelöschte `*.egg-info`- und Gold-Ausgaben im Status; `ROADMAP.md:16-21,67-71`. | Build-Ausgaben und Beweise können mit Quellautorität verwechselt werden. | G7: jedes generierte/Fixture-/Referenzartefakt klassifizieren, Ignore-Regeln für verschachtelte Engine-Pfade korrigieren und Gold-Evidenz reproduzierbar machen. |

## 5. Strategische Optimierungsreihenfolge

Dieser Plan autorisiert keine Implementierung. Jedes Gate ist bewusst eng. Jede Quell- oder Dokumentänderung nach einer Prüfung benötigt vor dem nächsten Freigabegate einen neuen Freeze und unabhängige Prüfung.

### G0 – Unterstützte Deployment- und Vertrauensgrenze einfrieren

**Ziel:** Den heute sicheren Betriebsrahmen benennen und eine unbeabsichtigte Ausweitung der Angriffsfläche verhindern.

- Das Produkt bis zu einem authentifizierten Deploymentvertrag als lokal und einzelbetreibergebunden festlegen.
- Zulässige Bind-Adressen, Browser-Ursprünge, Reverse-Proxy-Annahmen, Eigentümerschaft des Ratenkatalogs und Embedding-Unterstützung festhalten.
- Eine kurze Sicherheitsgrenzendokumentation in der Produktgrenze, nicht im Referenzkorpus, anlegen.
- Abnahmeevidenz: kein öffentlicher Host-Startpfad, kein beliebiger Cross-Origin-Browsersteuerpfad und dokumentiertes No-Go-Kriterium für Mehrbenutzerbetrieb.

**Nicht kombinieren mit:** Authentifizierungsimplementierung, Scope-Migration, UI-Redesign oder Algorithmusänderungen.

### G1 – Scope und Ownership zur produktiven Autorität machen

**Ziel:** Das bestehende `ScopeResolver`-/`WorkflowRegistry`-Design mit allen HTTP- und WebSocket-Ausführungspfaden verbinden.

- Jeden Lese-/Schreibendpunkt verfolgen: Fälle, Drafts, Sessions, Analyse, GV, Entropiejournale, Settings, Broadcast, Training und WebSockets.
- Pro Modus eine vertrauenswürdige Scope-Quelle wählen. Im enforced-Modus vor jedem Lookup oder Seiteneffekt fail-closed, wenn Gateway-Kontext fehlt oder fehlerhaft ist.
- Genau einen Workspace pro Request/Workflow auflösen und Fall-, Draft-, Recovery- und Journal-Operationen daran binden.
- Festlegen, welcher In-Memory-Zustand pro Workflow ist und welcher global bleiben darf. Gemeinsamer Broadcast-/Auto-Zustand darf nie Tenant-Isolation vortäuschen.
- Adversariale Verträge für gleiche Namen/IDs in mehreren Scopes, gefälschte Header, fehlenden Scope, WebSocket-Reconnect und Recovery nach Neustart ergänzen.

**Abnahmeevidenz:** Request/Header-zu-Workspace-Pfad ist für Lese- und Schreibrouten bewiesen, und kein produktiver Handler umgeht ihn.

### G2 – Persistenzsemantik vereinheitlichen und Leseschreiben entfernen

**Ziel:** Zustandsübergänge vorhersagbar, wiederherstellbar und prüfbar machen.

- Settings-Defaults so umbauen, dass Lesezugriffe Defaults berechnen, aber nicht persistieren; nötige Initialisierung/Migration explizit machen.
- Settings über dieselbe atomare JSON-Schreibhilfe oder einen gleichwertig dokumentierten Ersatz schreiben.
- Politik für fehlerhafte Settings/Fälle/Drafts/Journale festlegen: Quarantäne mit expliziter Betreiberaktion oder fail-closed; keine stille Rücksetzung von Betreiberentscheidungen.
- Recovery-Autorität nur dort erweitern, wo Übergänge tatsächlich mehrere Dateien umfassen; einfache Writes nicht unnötig zu Marker-Workflows machen.
- Nebenwirkungsfreie Status-/Leseendpunkte mit Vorher-/Nachher-Verzeichnismanifesten testen.

**Abnahmeevidenz:** Unterbrochene Writes und Read-only-Routenproben hinterlassen einen erklärbaren, getesteten Endzustand.

### G3 – Browser-/Serververtrag ohne Workflowänderung härten

**Ziel:** Unsichere Darstellungs- und Konfigurationspfade entfernen und lokale Benutzbarkeit bewahren.

- Serverseitige `innerHTML`-Konstruktion im Clarke-Vergleich durch DOM-APIs und Textknoten ersetzen.
- Produktionskonfiguration für `api`, `ws` und Embedding-/Theme-Nachrichten festlegen; Entwicklungs-Overrides ausdrücklich markieren und im gehärteten Modus deaktivieren.
- Gemeinsame API-Fehler-, Timeout- und Reconciliation-Politik für verändernde Kommandos ergänzen; bootbewusste WebSocket-Semantik bewahren.
- `analyze.js` erst dann in zustandsorientierte Module trennen, wenn Browser-/DOM-Verträge die heutigen Interaktionen abbilden.

**Abnahmeevidenz:** Bösartige Katalogstrings werden inert dargestellt; Retry-/Reconnect-Verhalten bleibt vertragstestsicher; Produktionskonfiguration akzeptiert keine beliebigen Steuerendpunkte.

### G4 – Orchestrierungsseams konservativ zerlegen

**Ziel:** Regressionsradius verringern, ohne Bytecode-Parität zu verändern.

- In `api/routes.py` Endpoint-Modelle, Analyse-/Session-Workflowkoordination, Draft-Promote, Broadcast-Befehle und WebSocket-Transport in interne Module mit unveränderten Routenverträgen trennen.
- In der UI Analyseergebnis-Rendering, Draft-Steuerung, GV-/Session-Zustand und Auto-Modus-Synchronisierung trennen.
- `main.create_app()` als einzige Assembly-Wurzel bewahren und Abhängigkeiten injizieren statt Globals hinzuzufügen.
- `core/analysis.py`, Java-PRNG und HashMap-Reihenfolge in diesem Gate nicht verändern.

**Abnahmeevidenz:** Bestehende REST-/WS-Vertragsfixtures laufen unverändert; Modulauszug erzeugt keine Algorithmus-Fixture-Drift.

### G5 – Externe Eingaben beobachtbar und begrenzt machen

**Ziel:** Eine explizite Betriebsgrenze für Katalog- und Entropieprovider schaffen.

- Katalogmanifest definieren: Ursprung, Version, Inhaltshash, erlaubte Dateitypen, maximale Größe/Anzahl, Encoding, Skriptpolitik und sichtbarer ungültiger/quarantänisierter Zustand.
- Seeded-Entropie vollständig offline halten. Für stochastic Requestbudget, Provider-Timeout, Circuit-Breaker-/Cache-Semantik und Health-Telemetrie definieren, ohne Rohseedmaterial außerhalb verschlüsselter Journale zu halten.
- Status rein beobachtend halten; er darf weder Settings noch anderen Runtime-Zustand materialisieren.
- Synthetische Fehlerfixtures für defekte Katalogdateien, übergroße Eingaben, random.org-Ausfall und fehlenden Journalschlüssel ergänzen.

**Abnahmeevidenz:** Jede externe Abhängigkeit fällt sichtbar und sicher aus; seeded-Paritätsfixtures bleiben unverändert.

### G6 – Reproduzierbare Verifikationsbahnen etablieren

**Ziel:** Statisches Vertrauen durch versionierte Ausführungsevidenz ersetzen.

1. Saubere Python-3.12-Umgebung passend zu `pyproject.toml` erstellen.
2. Gewählten localhost-Port vorprüfen und isoliertes `RADIOWORKS_HOME` wählen; nie Produktions-/Betreiberdaten verwenden.
3. Unit-/Contract-Tests mit externem Basetemp ausführen und fehlende Checkout-Mutation belegen.
4. Java-Gold-Parität nur mit dokumentierter JDK-/Harness-/Fixture-Herkunft ausführen und Grenzen der Behauptung exakt berichten.
5. Kurzlebigen Loopback-API-/WebSocket-Smoke gegen synthetischen Katalog ausführen und anschließend stoppen.
6. JavaScript-Syntax und Browserabnahme für Draft-Promote, Recovery-Fehlerdarstellung, WebSocket-Neustart/Replay-Gap-Abgleich und gehärteten HTML-Sink ausführen.
7. Maschinenlesbares Evidenzmanifest mit Quellhashes, Interpreter-/JDK-Versionen, Dependency-Auflösung und Testergebnissen erzeugen.

**Abnahmeevidenz:** Ein sauberer Checkout reproduziert alle Bahnen ohne Betreiberdaten und ohne Netzabhängigkeit für seeded-Tests.

### G7 – Repository-/Produkthygiene und Dokumentationsautorität

**Ziel:** Das aktive Produkt im referenzlastigen Repository eindeutig lesbar machen.

- Wurzelverzeichnisse als Quelle, Referenz, dekompilierte Ausgabe, Drittanbieter-Binärdatei, Fixture, generiert oder Betreiberdatei klassifizieren.
- Einen RadiWorks-lokalen Dokumentationsindex erzeugen, der normative Verträge, Referenzdokumente, bewusst fehlende Aurelia-Integrationspunkte und generierte Artefakte benennt.
- README-/Roadmap-Aussagen mit tatsächlichen Pfaden und aktuellem Produktumfang abgleichen.
- Generierte Build-Ausgaben erst entfernen oder ignorieren, wenn Evidenz-/Reproduzierbarkeitsfluss ihre Neugenerierung beweist; weder Historie umschreiben noch Betreiberdateien ohne explizite Freigabe berühren.

**Abnahmeevidenz:** Neue Bearbeiter erkennen Produktgrenze, autoritative Verträge und Build-generierte Dateien ohne Studium des dekompilierten Korpus.

## 6. Nicht verhandelbare Bewahrungsregeln für jede freigegebene Implementierung

1. Keine Änderung von seeded-Analyseordnung, PRNG-Verhalten, Ergebnislimit, Potenz-/Level-Routinen oder Java-Paritätsfixtures ohne separates Äquivalenzgate.
2. Keine Behauptung, dass stochastic-Ausgabe, Broadcast-Events, klinischer Vergleich, CopyGuard oder Passport-Prüfsumme medizinische Validität, Hardwareaktivierung, kryptografische Signatur oder Autorisierung liefern.
3. Keine Betreiber-/Fall-/Journal-Daten in Repository, Testfixtures, Logs, Screenshots oder Source-Shadow-Copies.
4. Keine Scope-/Multitenancy-Behauptung, bevor Request-zu-Workspace-Isolation für REST und WebSocket produktiv aktiv ist.
5. Kein Leseendpunkt darf Dateien erzeugen oder persistierte Datensätze still reparieren.
6. Kein breiter Rewrite des API-Routers oder der Analyse-UI; jeweils nur einen Seam hinter unveränderten Vertragstests extrahieren.
7. Kein Commit, Push, History-Rewrite, Löschen generierter Artefakte oder externes Deployment ist durch ein Gate impliziert.

## Freigabeentscheidung

Empfohlene nächste Aktion: ausschließlich G0 freigeben oder ablehnen. G0 ist eine Dokumentations-/Vertragsklärung und darf kein Runtime-Verhalten verändern. G1 bis G7 bleiben bis zu einem freigegebenen, hashgebundenen Implementierungsfreeze sowie eigenen Test-/Evidenzplänen blockiert.
