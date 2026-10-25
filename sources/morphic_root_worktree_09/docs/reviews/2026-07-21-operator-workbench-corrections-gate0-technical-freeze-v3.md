# Gate 0 Technical Freeze v3 — Operator Workbench corrections

Datum: 2026-07-21
Status: REVIEW CANDIDATE — NO-GO bis zwei unabhängige driftfreie Nullbefund-Reviews vorliegen
Branch: `operator-workbench-phase1`
HEAD/Baseline: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
Vorgänger: Freeze v2, SHA-256 `702ec049d3f0bf910fb0a322528368942f2b1e0758d769608fab365f1c19c408`, immutable abgelehnt

## 1. Scope und Schutzgrenzen

Dieser Freeze umfasst ausschließlich Gate 0 und die Remediation der zwei unabhängigen v2-Reviews. Der stark dirty Worktree ist beabsichtigt; fremde Änderungen wurden weder resettet noch gestaged, committet oder gepusht.

Geschützte Liveprozesse zum Freezezeitpunkt:

- Port 8090: PID 17136, unverändert
- Port 8765: PID 12992, unverändert; weiterhin alter Liveprozess
- Port 8766: frei; sämtliche eigenen QA-Prozesse und temporären Browserartefakte entfernt

Port 8765 darf erst nach zwei unabhängigen Reviews mit Drift 0 und P0=P1=P2=P3=0 neu gestartet werden.

## 2. Immutable Reviewevidenz des abgelehnten Freeze v2

- Freeze v2: `docs/reviews/2026-07-21-operator-workbench-corrections-gate0-technical-freeze-v2.md`
  - SHA-256: `702ec049d3f0bf910fb0a322528368942f2b1e0758d769608fab365f1c19c408`
- Review v2-1: `docs/reviews/2026-07-21-operator-workbench-corrections-gate0-review-v2-1.md`
  - SHA-256: `2950d8a5478a5d5436ecccf06e86fdd9afdfc09c1b672bd24fd850cab9fdc512`
  - Verdict: REQUEST CHANGES; Drift 0; P0=0, P1=2, P2=0, P3=0
- Review v2-2: `docs/reviews/2026-07-21-operator-workbench-corrections-gate0-review-v2-2.md`
  - SHA-256: `7fa369822402b4557a3e74744fad7a69b013bd8ead61bafcd1b0606ef6e0c83d`
  - Verdict: REQUEST CHANGES; Drift 0; P0=0, P1=2, P2=1, P3=0

Freeze v2 wurde nicht editiert. Freeze v3 ist eine neue hashgebundene Einheit.

## 3. Geschlossene v2-Befundklassen

### 3.1 Strukturell fehlerhafte Registryeinträge

`SourceManifest.from_mapping()` validiert den Laufzeittyp vor jedem `.get()`-Zugriff und normalisiert Nicht-Objekte in `sources[]` zu `SourceRegistryError`. Damit greifen die bereits redigierten 503-Verträge sowohl bei `/api/sources` als auch beim Scanprofilkatalog. Reale malformed-Dateien werden für beide Routen getestet; lokale Pfade und Parserinternas bleiben verborgen.

### 3.2 Timeout und Upstream-Abort während des Response-Body-Reads

`requestJson()` klassifiziert `AbortError` jetzt auch während `response.json()`:

- eigener GET-Timeout → stabiler Fehlercode `request_timeout`,
- vom Aufrufer geliefertes Abortsignal → unverändert als `AbortError`,
- kein stilles `null` nach einem Body-Read-Abbruch.

Nicht-idempotente Requests erhalten weiterhin keinen automatisch erzeugten Timeout/Abort.

### 3.3 Mutation-Commit-Ambiguität bei Scan- und Harmonisierungsstart

Eine neue durable Start-Operation-Autorität schreibt vor Job-Erzeugung einen fail-closed Claim unter `runtime/start-operations`:

- clientgenerierte Idempotency-ID,
- Bindung an Operationstyp, Request-SHA-256 sowie Tenant und Operator,
- atomare persistente Zustände `pending|completed|failed`,
- abgeschlossene Wiederholung liefert denselben bestehenden Job,
- `pending` nach Prozess- oder Antwortverlust erlaubt keine zweite Erstellung,
- abweichender Payload unter derselben ID wird abgewiesen,
- Browser hält die nicht aufgelöste ID ohne Klientendaten in `localStorage`, über Reload und Browserneustart hinweg,
- Transport- und Server-5xx-Fehler behalten die Autorität; ein Fallwechsel bleibt bis zum Abgleich gesperrt,
- validierte 201-Antwort ohne Job-ID behält die Operation zur sicheren Wiederholung.

Die Headerunterstützung bleibt rückwärtskompatibel: ohne explizite Operation-ID wird kein Headerwert `undefined` gesendet.

### 3.4 Solfeggio-Reset

Der New-Case-Reset ruft `wireSolfeggioChoiceCards("#solfeggio-base-choices")` mit dem expliziten DOM-Ziel auf. Der echte Browservertrag setzt zunächst 528 Hz, führt den Privacy-Reset aus und bestätigt anschließend den sichtbaren und internen Standard 432 Hz.

## 4. Hashgebundener Scope

| Datei | SHA-256 |
|---|---|
| `apps/web/main.py` | `f51d667a1cf639b88575a4f097b40b36c9890b7f711c387dec89362e51b73c58` |
| `apps/web/workbench.py` | `03797d657a6479dd0e147730272b08e06c8e529f56a2d31a185150f9878ecc37` |
| `apps/web/start_operations.py` | `2d6daeace3adddf9215da6b3b5bcdd6d30a54021c41b1408b2dd536f042b90a9` |
| `apps/web/static/app.js` | `4b8992ee5259214e82fadf93b72284e145f3aabc74b294a96668a0e66e665f70` |
| `apps/web/static/workbench-api.js` | `6f7bca07e8c15c871da98e124c051c1fa11630e785efb268ac6d49bc305faa9a` |
| `apps/web/static/workbench-render.js` | `dc5742f6bc9ab62e7603849749ff96f9b239ba04c95f6dfab58111a14cf1c2b9` |
| `apps/web/static/workbench-state.js` | `e81cf8f15a386bac78a63fa38e52baa1db900097d64195318a12dce04cad70ac` |
| `core/source_registry.py` | `7061fac193ef389106dd9ad7f3e53bddb6daffa44e3b51c7b209a1dce0c578cf` |
| `tests/test_source_registry.py` | `1e4d79b28f1528189b92bd80c758bac681ecc3b6f57ebf4d36f4f684297c5d4d` |
| `tests/test_web_scan_profile_catalog.py` | `7e3ac77d31201d66979fbf0d6d189d115d9642fb39f239caf37c440127092bdb` |
| `tests/test_start_operations.py` | `e9e224d154eb427aca9fbd5a6cf63d74b4927c63565bdf16464d0a8ead6073e5` |
| `tests/test_workbench_gate0_catalog_state.py` | `688fa55e1acd7c936e37fed601672ca1b7d67ab022ceb5f533db55379d649f4b` |
| `tests/test_web_shell.py` | `98d6577eded77edd5bcb30450917776927e98f1466d12e7c28622befcc169c39` |
| `tests/test_workbench_error_ui_js.py` | `9f1dde887517be639d3aba62ba7cb600b00cd144543841a87ce35850c9cddc42` |
| `tests/browser/workbench.spec.js` | `ca4d774f298048e1321f965bda035ed7dbde21e073f728f6fbc1f22e5c2e1530` |

## 5. Verifikation

Finale, nach dem letzten Produkt- und Testpatch ausgeführte Nachweise:

- vollständige Python-Suite: `1418 passed, 9 skipped in 210.40s`
- vollständige Browsermatrix: `28 passed in 17.4s`
- gezielter Reload-/Response-Loss-Browservertrag: `1 passed in 1.4s`
- fokussierte Gate-/Webmatrix: `131 passed`
- finale fokussierte Nachprüfung: `96 passed`
- JavaScript-Syntaxchecks: bestanden
- Python-Compilechecks: bestanden
- `git diff --check`: bestanden; nur bekannte LF/CRLF-Warnungen
- finales Pytest-Log: `C:\Users\Hubert111\AppData\Local\Temp\morphic_gate0_v3_final2_pytest_20260721_191953.log`
- Log-SHA-256: `9f629063b40a1ebeac05ce5eb5ce935a029cb7beef04d2ab56a8e8912f6aaabc`

Die Browsermatrix lief ausschließlich auf dem isolierten QA-Port 8766 mit dem Projektinterpreter `C:\morphic_v1\.venv\Scripts\python.exe`. QA-Skript, Runtime, `node_modules`, Lockfile und Browserreports wurden anschließend entfernt.

## 6. Reviewprotokoll

Jeder Reviewer muss:

1. Freeze-v3-SHA und alle 15 Scopehashes am Anfang prüfen.
2. Die vollständige Gate-0-Differenz gegen HEAD/Baseline und die v2-Reviewevidenz lesen.
3. Besonders Registry-Shape-Normalisierung, Body-Read-Aborts, langlebige Idempotency-Autorität, Payload-/Owner-Bindung, Fail-closed-Pending, Replay beider Startendpunkte, Local-Storage-Privacy, Resetblockade und Solfeggio-DOM-Reset prüfen.
4. Keine Dateien, Tests, Server oder Netzwerkzugriffe verändern/starten.
5. Am Ende Freeze und alle Scopehashes erneut prüfen.
6. `APPROVE` nur bei Drift 0 und P0=P1=P2=P3=0 erteilen.

## 7. Freigabestatus

`NO-GO / FREEZE V3 REVIEW CANDIDATE / PORT 8765 UNVERÄNDERT`

Ein kontrollierter Live-Restart ist erst nach zwei unabhängigen Nullbefund-Freigaben und einer unmittelbar davor wiederholten Hash-/Port-/Rollbackprüfung zulässig.
