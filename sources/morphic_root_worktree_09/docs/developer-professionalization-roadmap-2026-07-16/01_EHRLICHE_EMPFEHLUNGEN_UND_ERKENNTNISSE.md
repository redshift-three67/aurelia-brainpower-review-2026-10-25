# Ehrliche Empfehlungen und Erkenntnisse

## 1. Gesamturteil

Das Projekt ist fachlich weiter als seine Repository-, Release- und Betriebsstruktur. Die Stärke liegt in umfangreicher Funktionalität, adversarialer Testtiefe und konservativer Governance. Die größten professionellen Risiken liegen aktuell nicht in fehlenden Features, sondern in fünf Querschnittsthemen:

1. mehrere Authority- und Persistenzimplementierungen;
2. ein extrem schmutziger Worktree mit Runtime-/Archivdaten;
3. nicht vollständig reproduzierbare Toolchain/Dependencies;
4. fehlende automatisierte CI-/Release-Gates;
5. Status- und Dokumentdrift durch sehr viele parallele Gate-Artefakte.

Ein Big-Bang-Neubau wäre kontraproduktiv. Die beste Route ist eine **Strangler-/Boundary-Strategie**: bestehendes Verhalten durch Contract- und Equivalence-Tests einfrieren, neue professionelle Boundaries daneben etablieren, Aufrufer gateweise migrieren und Legacy erst nach beweisbarer Ablösung entfernen.

## 2. Priorisierte Empfehlungsmatrix

| Prio | Empfehlung | Wirkung | Aufwand | Risiko bei falscher Reihenfolge |
|---:|---|---|---|---|
| 1 | F5-B/v10 exakt abschließen | schließt aktuelle P1-Integrity-Risiken | hoch | jede Parallelmodernisierung invalidiert Scope/Reviews |
| 2 | Test-/Runtime-Ausgaben aus Worktree entfernen | beherrschbarer Status, sichere Reviews/Builds | mittel | unklare Datenlöschung oder PII-Kopie |
| 3 | Vollsuite deterministisch grün machen | verlässliche Releasebasis | mittel | Baselinefehler maskieren echte Regressionen |
| 4 | eine Dependency-Authority + Lockfile | reproduzierbare Installationen | niedrig–mittel | Host-Drift, falscher Interpreter |
| 5 | Windows-CI plus statische Gates | automatisierte Mindestqualität | mittel | manuelle Evidenz bleibt alleinige Kontrolle |
| 6 | zentrale Persistence-/Authority-Bibliothek | weniger duplizierte Securitylogik | hoch | Refactor kann Authorities destabilisieren |
| 7 | klare Package-/Entrypoint-Grenzen | Wartbarkeit und Onboarding | hoch | Big-Bang-Importbruch |
| 8 | Admin-Key-/Secret-Composition Root | sicherer produktiver Adminbetrieb | mittel | unsichere Defaults/Key-Vermischung |
| 9 | Web/API-Contract- und Browser-Tests | robuste Operator-UI | mittel | UI/API-Drift bleibt unbemerkt |
| 10 | Release-/Observability-/Runbook-System | professioneller Betrieb | mittel | Fehleranalyse und Rollback bleiben ad hoc |

## 3. Repository und Datenhygiene

### Erkenntnis

`git status --short` umfasst 351 Einträge; vollständig expandiert existieren 63.994 untracked Dateien, davon 63.750 in 195 `Benutzer_Archive__ws-*`-Roots. Zusätzlich befinden sich zahlreiche historische Tools, Launcher, Analyseoutputs und Daten direkt im Root.

### Empfehlung

Nicht einfach `.gitignore` erweitern und keinesfalls pauschal löschen. Zuerst ein eigenes Hygiene-Gate:

1. jeden Top-Level-Root als `source`, `fixture`, `runtime`, `operator export`, `archive`, `generated` oder `unknown` klassifizieren;
2. mögliche PII-/Klientendaten nur metadatenarm inventarisieren, nicht in allgemeine Auditkopien aufnehmen;
3. externe User-Data-Roots für Runtime, Exporte, Archive, Logs und Testartefakte erzwingen;
4. Tests mit explizitem `tmp_path`/`--basetemp` und fail-closed Ausgabepfaden versehen;
5. erst nach hashgebundener Freigabe bekannte synthetische Artefakte bereinigen;
6. `.gitignore` danach als Defense-in-Depth, nicht als Datenarchitektur verwenden.

Professionelles Ziel: `git status --short` muss für einen definierten Entwicklungsstand klein und interpretierbar sein; Runtimebetrieb darf keine neuen Top-Level-Verzeichnisse im Repository erzeugen.

## 4. Dependencies und Toolchain

### Erkenntnis

`pyproject.toml:13-28` und `requirements.txt:1-35` sind zwei teilweise abweichende Dependency-Authorities. `requirements.txt` enthält beispielsweise `pyserial`, `scipy` und `matplotlib`, die im Projektmanifest fehlen. Es gibt keine sichtbar getrackte Lockdatei. Die Projektanweisung muss bereits ausdrücklich den venv-Interpreter nennen, weil bare `python`/`pip` auf unterschiedliche Installationen zeigen können.

### Empfehlung

- `pyproject.toml` wird einzige deklarative Authority.
- Runtime-, optional-hardware-, quantum/gpu- und dev-Abhängigkeiten werden sauber als Extras getrennt.
- `uv.lock` oder äquivalentes hashgebundenes Lockfile einführen.
- Python 3.11 als aktuell verifizierte Baseline explizit pinnen; 3.10/3.12 erst als eigene CI-Matrix freigeben.
- Launcher verwenden ausschließlich die projektlokale venv oder `uv run`.
- Ein `tools/preflight.py` prüft Interpreter, Lockzustand, Pflichtpakete und sichere Runtime-Roots ohne produktive Mutation.

Keine Dependency-Aktualisierung zusammen mit F5-B oder einem Algorithmusgate durchführen.

## 5. CI, Tests und Quality Gates

### Erkenntnis

Es wurden keine getrackten `.github`-Workflowdateien gefunden. Die Testbasis ist umfangreich, aber der letzte vollständige v9-Lauf hatte 14 bekannte Baselinefehler. Testzahlen und Reviewevidenz werden derzeit weitgehend manuell dokumentiert.

### Empfehlung

CI schrittweise:

1. Windows-primary: Ruff, `py_compile`, `git diff --check`, fokussierte Contract-Suites.
2. Vollsuite mit kontrollierter Zeitzone/Uhr, isolierten Rate-Limitern und externem `--basetemp`.
3. Linux zunächst advisory, bis POSIX-Authority-Semantik entschieden ist.
4. separate Marker: `unit`, `contract`, `security`, `integration`, `slow`, `windows`, `hardware`, `exploratory`.
5. Coverage als Trend-/Hotspotindikator, nicht als blindes Prozentgate.
6. Mutation-/Fault-injection nur für Persistence-, Auth- und Critical-Algorithm-Boundaries.
7. Tests dürfen keine Worktree-Runtimearchive erzeugen; vor/nach kritischen Suiten Status-/Authority-Nullmutation prüfen.

Die 14 Baselinefehler sollten nach F5-B in einem eigenen Stabilitätsgate auf null reduziert werden. „Baseline-identisch“ ist für einen Zwischenfreeze akzeptabel, aber kein optimales professionelles Endziel.

Weitere verifizierte Querschnittsbefunde für spätere Gates:

- Der Rate-Limiter hält prozessglobalen mutablen Zustand ohne klar app-lokal injizierte Lifecycle-Grenze (`apps/web/security.py:26-29,55-81`). Das erklärt die historischen In-Process-Fehlerklasse und sollte über eine app-/testlokale Instanz statt nur über Testreihenfolge geschlossen werden.
- `apps/web/launcher.py:12-37` setzt weiterhin einen festen Exportroot, während tenantabhängige Pfadauflösung an anderer Stelle existiert. Vor Mehrbenutzerbetrieb muss auch der tatsächliche Scan-Schreibpfad serverseitig aus dem Operator-/Tenant-Kontext abgeleitet werden.
- `apps/web/workbench_runtime.py:36-57` und `core/compliance/runtime_manifest.py:67-84` interpretieren beschädigtes JSON teilweise als leeren Zustand und publizieren ohne Directory-Durability. Nach F5-B ist ein eigenes fail-closed Runtime-Persistence-Gate sinnvoll; nicht still mit dem Admin-Catalog-Umbau vermischen.
- `app = create_app()` und Store-/Job-Konstruktoren können beim Import Verzeichnisse anlegen (`apps/web/main.py:258-289,783`, `apps/web/scan_jobs.py:223-230`). Read-only Werkzeuge und Tests benötigen langfristig einen expliziten, seiteneffektfreien Composition Root/Lifespan.

## 6. Architektur und Modulgrenzen

### Erkenntnis

Es existieren etablierte Bereiche (`core`, `apps`, `services`, `providers`), zugleich aber viele Rootmodule, Rootlauncher, ältere Weboberflächen (`web_ui`, `web_app.py`, `web_server.py`) und moderne `apps/web`-/`apps/cli`-Pfade. Das erhöht die Gefahr paralleler Authorities und unklarer aktiver Einstiegspunkte.

### Empfehlung

Zielarchitektur ohne Big Bang:

```text
morphic/
  domain/          reine Contracts und fachliche Algorithmen
  application/     Use Cases, Orchestrierung, Ports
  infrastructure/  SQLite, Filesystem, Hardware, externe Provider
  interfaces/
    cli/
    web/
  runtime/         Jobs/Worker/Activation
```

Praktischer Weg:

- zunächst nur Import-/Ownership-Matrix dokumentieren;
- pro Gate genau einen aktiven Entrypoint bestimmen;
- alte Entry Points als explizite Adapter/Deprecated Wrapper markieren;
- Rootmodule nicht verschieben, bevor Equivalence-/Importtests vorhanden sind;
- neue Querschnittslogik nur in Zielpackages anlegen;
- zirkuläre Imports und modulinterne Lazy-Imports (`store.py` importiert Service/Promotion innerhalb von Methoden) als Architekturindikator erfassen und später durch Ports/Dependency Injection entkoppeln.

Die Analyse-/Scoring-/Profilkerne bleiben unangetastet, bis eigene Equivalence-Gates eine Migration erlauben.

## 7. Persistence und Security

### Erkenntnis

Das Projekt besitzt mehrere hochwertige, aber teilweise duplizierte Boundaries: Catalog-Store, Source Registry, Stage/Index/Ledger, Backup/Restore, Audit-HMAC und Validation-HMAC. Die aktuelle v10-Arbeit zeigt, dass kleine Unterschiede zwischen diesen Implementierungen P1-Risiken erzeugen.

### Empfehlung

Nach F5-B eine kleine interne `infrastructure/authority_io`-Schicht mit eindeutigem Contract:

- held-handle read;
- atomic replace;
- immutable create-if-absent;
- directory durability;
- identity-/byte-attestation;
- platform capability detection;
- explicit fail-closed unsupported operation;
- fault-injection hooks nur für Tests.

Diese Schicht darf erst nach Characterization-Tests extrahiert werden. Registry, Stage und Backup werden nacheinander migriert; nie alle gleichzeitig.

Secrets:

- Stage-HMAC, Audit-HMAC, Validation-HMAC und Admin-Session-Key bleiben getrennte Zwecke/Authorities.
- ein zentraler Composition Root wählt Provider, aber kein „Universal Key Provider“ liefert denselben Schlüssel für mehrere Zwecke.
- Key-ID, Rotation, Revocation, ACL/DPAPI/HSM-Option und Backup-Ausschluss erhalten eigene Runbooks.
- kein Key wird still erzeugt, wenn eine produktive Authority fehlt.

## 8. Web, API und Operator Experience

### Erkenntnis

FastAPI und Vanilla JS sind funktional und bewusst leichtgewichtig. F6 sieht eine getrennte Adminoberfläche und fail-closed Adminauth vor (`.hermes/plans/...:434-497`), ist aber noch Zukunftsarbeit. Ohne Browser-/Accessibility-CI bleibt visuelles und DOM-seitiges Verhalten vorwiegend manuell.

### Empfehlung

- OpenAPI/Pydantic-Verträge als API-Authority; clientseitige Payloads dagegen testen.
- Playwright-Smokes für die fünf wichtigsten Operatorpfade.
- axe-core für Accessibility; Keyboard/Fokus/Error Summary verpflichtend.
- CSP, sichere Header, Origin/Host und keine Secret-Persistenz als Contracttests.
- Long-running Jobs über stabile Job-State-Machine mit Cancellation/Recovery, nicht über UI-Timing.
- Vanilla JS darf bleiben; ein Frameworkwechsel ist aktuell nicht gerechtfertigt.
- Frontend-Buildsystem nur einführen, wenn Module, Typechecking oder CSP-Nonce-Handling es konkret erfordern.

## 9. Dokumentation und Governance

### Erkenntnis

Die Dokumentation ist außergewöhnlich umfangreich, aber der aktive Plan ist gegenüber dem v10-Livezustand bereits veraltet. Viele Freeze-/Review-/Statusdateien sind wichtig als Evidenz, erschweren aber die Sicht auf genau einen Golden Record.

### Empfehlung

- genau ein aktuelles `docs/status/CURRENT.md` oder `PROJECT_MEMORY/00_CURRENT_STATE.md` als navigierender Golden Record;
- historische Gate-/Freeze-Dokumente immutable unter `docs/history` oder klarer Indexstruktur;
- maschinenlesbarer Gate-Index (`gate_id`, `status`, `freeze_hash`, `reviews`, `superseded_by`);
- CI-Link-/Stale-Status-Prüfung;
- Architekturentscheidungen als kurze ADRs;
- Runbooks getrennt von Designplänen;
- Dokumentfreeze weiterhin hashgebunden, aber repetitive Evidenz automatisiert generieren.

Automatisierung darf die Reviewregel nicht schwächen; sie soll nur manuelle Hash-/Tabellenfehler reduzieren.

## 10. Was ausdrücklich nicht empfohlen wird

| Nicht empfohlen | Grund |
|---|---|
| kompletter Rewrite | vernichtet testgebundene Fachlogik und erhöht Regressionrisiko |
| sofortige Microservices | lokale Single-Operator-Architektur gewinnt dadurch wenig, Betriebskomplexität steigt |
| Frameworkwechsel im Frontend | kein belegter Engpass |
| gleichzeitige Dependency- und Securitymigration | Reviewscope wird unbeherrschbar |
| pauschale Löschung untracked Archive | potenzieller Daten-/Evidenzverlust |
| „Universal-HMAC-Key“ | Zwecktrennung und Rotation werden kompromittiert |
| sofortige Runtime-Aktivierung des Admin-Catalogs | F5-B/F6/F7/F8 und Fallbackpolicy sind nicht geschlossen |
| Optimierung von Algorithmen ohne Equivalence-Gate | gefährdet fachliche Stabilität |
