## Erster unabhängiger Gate-0-Freeze-v3-Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**

- **Branch:** `operator-workbench-phase1`
- **HEAD/Baseline:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- **Freeze-v3-SHA-256:** `833ced9d4dc60b776321350b7fef5b29689d660776706812f859f186b59a16af`
- **Drift:** 0
- **P0:** 0
- **P1:** 4
- **P2:** 1
- **P3:** 0

`APPROVE` ist wegen der fünf Befunde ausgeschlossen.

### Hashbindung Anfang → Ende

| Objekt | Manifest / Start | Ende | Drift |
|---|---|---|---:|
| Freeze v3 | `833ced9d4dc60b776321350b7fef5b29689d660776706812f859f186b59a16af` | `833ced9d4dc60b776321350b7fef5b29689d660776706812f859f186b59a16af` | 0 |
| `apps/web/main.py` | `f51d667a1cf639b88575a4f097b40b36c9890b7f711c387dec89362e51b73c58` | `f51d667a1cf639b88575a4f097b40b36c9890b7f711c387dec89362e51b73c58` | 0 |
| `apps/web/workbench.py` | `03797d657a6479dd0e147730272b08e06c8e529f56a2d31a185150f9878ecc37` | `03797d657a6479dd0e147730272b08e06c8e529f56a2d31a185150f9878ecc37` | 0 |
| `apps/web/start_operations.py` | `2d6daeace3adddf9215da6b3b5bcdd6d30a54021c41b1408b2dd536f042b90a9` | `2d6daeace3adddf9215da6b3b5bcdd6d30a54021c41b1408b2dd536f042b90a9` | 0 |
| `apps/web/static/app.js` | `4b8992ee5259214e82fadf93b72284e145f3aabc74b294a96668a0e66e665f70` | `4b8992ee5259214e82fadf93b72284e145f3aabc74b294a96668a0e66e665f70` | 0 |
| `apps/web/static/workbench-api.js` | `6f7bca07e8c15c871da98e124c051c1fa11630e785efb268ac6d49bc305faa9a` | `6f7bca07e8c15c871da98e124c051c1fa11630e785efb268ac6d49bc305faa9a` | 0 |
| `apps/web/static/workbench-render.js` | `dc5742f6bc9ab62e7603849749ff96f9b239ba04c95f6dfab58111a14cf1c2b9` | `dc5742f6bc9ab62e7603849749ff96f9b239ba04c95f6dfab58111a14cf1c2b9` | 0 |
| `apps/web/static/workbench-state.js` | `e81cf8f15a386bac78a63fa38e52baa1db900097d64195318a12dce04cad70ac` | `e81cf8f15a386bac78a63fa38e52baa1db900097d64195318a12dce04cad70ac` | 0 |
| `core/source_registry.py` | `7061fac193ef389106dd9ad7f3e53bddb6daffa44e3b51c7b209a1dce0c578cf` | `7061fac193ef389106dd9ad7f3e53bddb6daffa44e3b51c7b209a1dce0c578cf` | 0 |
| `tests/test_source_registry.py` | `1e4d79b28f1528189b92bd80c758bac681ecc3b6f57ebf4d36f4f684297c5d4d` | `1e4d79b28f1528189b92bd80c758bac681ecc3b6f57ebf4d36f4f684297c5d4d` | 0 |
| `tests/test_web_scan_profile_catalog.py` | `7e3ac77d31201d66979fbf0d6d189d115d9642fb39f239caf37c440127092bdb` | `7e3ac77d31201d66979fbf0d6d189d115d9642fb39f239caf37c440127092bdb` | 0 |
| `tests/test_start_operations.py` | `e9e224d154eb427aca9fbd5a6cf63d74b4927c63565bdf16464d0a8ead6073e5` | `e9e224d154eb427aca9fbd5a6cf63d74b4927c63565bdf16464d0a8ead6073e5` | 0 |
| `tests/test_workbench_gate0_catalog_state.py` | `688fa55e1acd7c936e37fed601672ca1b7d67ab022ceb5f533db55379d649f4b` | `688fa55e1acd7c936e37fed601672ca1b7d67ab022ceb5f533db55379d649f4b` | 0 |
| `tests/test_web_shell.py` | `98d6577eded77edd5bcb30450917776927e98f1466d12e7c28622befcc169c39` | `98d6577eded77edd5bcb30450917776927e98f1466d12e7c28622befcc169c39` | 0 |
| `tests/test_workbench_error_ui_js.py` | `9f1dde887517be639d3aba62ba7cb600b00cd144543841a87ce35850c9cddc42` | `9f1dde887517be639d3aba62ba7cb600b00cd144543841a87ce35850c9cddc42` | 0 |
| `tests/browser/workbench.spec.js` | `ca4d774f298048e1321f965bda035ed7dbde21e073f728f6fbc1f22e5c2e1530` | `ca4d774f298048e1321f965bda035ed7dbde21e073f728f6fbc1f22e5c2e1530` | 0 |

### Immutable v2-Evidenz

Auch am Anfang und Ende identisch:

| Objekt | SHA-256 | Drift |
|---|---|---:|
| Freeze v2 | `702ec049d3f0bf910fb0a322528368942f2b1e0758d769608fab365f1c19c408` | 0 |
| Review v2-1 | `2950d8a5478a5d5436ecccf06e86fdd9afdfc09c1b672bd24fd850cab9fdc512` | 0 |
| Review v2-2 | `7fa369822402b4557a3e74744fad7a69b013bd8ead61bafcd1b0606ef6e0c83d` | 0 |

## Befunde

| Priorität | Befund | Fundstelle |
|---|---|---|
| **P1** | **Die Idempotency-Autorität ist an beiden Startendpunkten optional und daher umgehbar.** Fehlt der Header, liefert `_begin_start_operation()` unmittelbar `(False, None)` und der Job wird ohne Claim erzeugt. Jeder direkte API-Client, ältere Client oder fehlerhafte Browserpfad kann damit Scan oder Harmonisierung weiterhin ohne durable Request-/Owner-Bindung starten. Das ist kein authority-owning Idempotency-Vertrag für die Endpunkte. | `apps/web/main.py:678-684`, `apps/web/main.py:732-739`, `apps/web/main.py:850-858` |
| **P1** | **Die Claim-Erzeugung ist nur innerhalb einer einzelnen Python-Instanz exklusiv.** `StartOperationStore` besitzt lediglich ein instanzlokales `threading.RLock`; unter zwei Prozessen bzw. zwei Store-Instanzen können beide nach `path.exists() == False` einen Pending-Record per Replace publizieren und anschließend je einen Job starten. Die Tests beweisen nur einen sequenziellen Neustart, keine konkurrierende Erstbeanspruchung. | `apps/web/start_operations.py:43-46`, `apps/web/start_operations.py:111-147`; Testlücke `tests/test_start_operations.py:14-35` |
| **P1** | **Replay wird bei beiden Endpunkten erst nach veränderlichen Vorbedingungen beziehungsweise beim Scan sogar nach einer Mutation erkannt.** Harmonisierung prüft zuerst, ob der Bericht noch existiert; ein nach erfolgreichem Start entfernter Bericht verhindert deshalb den Replay des bereits gebundenen Jobs. Der Scan führt vor `_begin_start_operation()` `prepare_group_scan_activation()` aus, dessen produktiver Pfad einen neuen Aktivierungshandle ausstellt. Ein Replay bzw. selbst ein Pending-Retry kann daher erneut mutieren oder wegen inzwischen geänderter Draft-/Consent-Autorität scheitern, statt zuerst denselben Job zurückzugeben. | `apps/web/main.py:741-759`, `apps/web/main.py:859-884`; mutierender Aufrufpfad `apps/web/group_analysis_runtime.py:45-70` |
| **P1** | **Der Crash-/Fehlerkorridor zwischen Job-Erzeugung und Claim-Completion ist dauerhaft unreconciliierbar und blockiert den Fallwechsel unbegrenzt.** Nach erfolgreichem `jobs.start()` enthält der Claim bis zum nachfolgenden `complete()` keine Job-ID. Prozessabbruch oder ein Fehler beim Completion-Write lässt einen restartfesten `pending`-Claim zurück; jeder Retry endet ausschließlich mit 409. Es gibt weder Operation-Status-Lookup noch Job-Key-Reconciliation noch eine sichere administrative Auflösung. Der Browser behält die ID und `resetWorkbenchForNewCase()` sperrt dadurch dauerhaft. Das erfüllt Fail-closed-Duplikatvermeidung, aber nicht die zugesicherte sichere Replay-/Abgleichsemantik. | `apps/web/main.py:697-704`, `apps/web/main.py:769-799`, `apps/web/main.py:907-925`, `apps/web/static/app.js:96-101`, `apps/web/static/app.js:1142-1156` |
| **P2** | **Der Freeze bindet die neue transitive Durability-Grenze nicht ein.** `start_operations.py` delegiert alle sicherheitsrelevanten Pending-/Completed-/Failed-Publikationen an `apps/web/durable_io.py`; diese untracked, gegenüber HEAD neue Datei fehlt aber in den 15 Scopehashes. Ihr aktueller Hash ist zwar byteidentisch zur früheren v10-Evidenz (`abbac903…de9c2`), Änderungen daran würden Freeze v3 selbst jedoch nicht invalidieren. | `apps/web/start_operations.py:13`, `apps/web/start_operations.py:146-165`, `apps/web/start_operations.py:167-180`; Manifestlücke `docs/reviews/2026-07-21-operator-workbench-corrections-gate0-technical-freeze-v3.md:70-88` |

## Klassenschluss der besonders verlangten Verträge

| Klasse | Ergebnis |
|---|---|
| Strukturell fehlerhafte Registryeinträge `/api/sources` | **Geschlossen:** Nicht-Mappings werden vor `.get()`/Feldzugriff zu `SourceRegistryError`; realer `sources:[1]`-Pfad vorhanden. |
| Strukturell fehlerhafte Registryeinträge Scanprofilkatalog | **Geschlossen:** gleicher reale Parserpfad wird als redigierter 503 behandelt. |
| GET-Timeout vor Response-Headern | **Geschlossen.** |
| Timeout während `response.json()` | **Geschlossen:** Timeout bleibt `request_timeout`, kein `null`-Erfolg. |
| Upstream-Abort während `response.json()` | **Geschlossen:** `AbortError` wird weitergereicht. |
| Keine automatisch erzeugte Mutation-Abort-Autorität | **Geschlossen.** Explizite Aufrufersignale bleiben möglich. |
| Request-Payload-/Tenant-/Operatorbindung eines vorhandenen Claims | **Geschlossen:** kanonischer Requesthash und zusammengesetzter Owner werden verglichen. |
| Fail-closed `pending` über sequenziellen Serverrestart | **Geschlossen, aber ohne sichere Auflösung:** keine zweite Erstellung unter demselben Claim; siehe P1. |
| Client-Operation-ID über Reload/Browserrestart | **Geschlossen für verfügbares `localStorage`;** ID enthält keine Klientendaten. |
| Sichere Replay-Semantik beider Startendpunkte | **Nicht geschlossen:** optionale Autorität, Vor-Replay-Mutation/Vorbedingungen und unreconciliierbarer Crashkorridor. |
| Resetblockade während laufender Mutation/unaufgelöstem Start | **Teilweise geschlossen:** blockiert korrekt, kann wegen unreconciliierbarem Pending aber dauerhaft verriegeln. |
| Solfeggio-Reset | **Geschlossen:** sichtbare Karte, Backing-State und `target_frequency` werden auf 432 gesetzt; expliziter Container-Selektor vorhanden. |
| Cross-Process-Durable-Idempotency | **Nicht geschlossen:** instanzlokaler Lock und nicht-exklusive Erstpublikation. |

## HEAD-/Baseline-Differenz

- Alle 15 manifestierten Dateien wurden gegen HEAD/Baseline und im aktuellen Volltext geprüft.
- Scope-Zustand: **10 tracked-modified + 5 neue/untracked Dateien**.
- Die neuen/untracked Scopeobjekte sind:
  - `apps/web/start_operations.py`
  - `tests/test_start_operations.py`
  - `tests/test_web_scan_profile_catalog.py`
  - `tests/test_workbench_gate0_catalog_state.py`
  - `tests/browser/workbench.spec.js`
- Die v2-Remediation schließt Registry-Shape, Body-Read-Aborts und Solfeggio-Reset, führt aber die oben genannten neuen Idempotency-/Replay-Lücken ein bzw. lässt sie offen.

## Read-only-Nachweis

- Keine Repositorydateien erstellt, geändert oder gelöscht.
- Keine Tests ausgeführt.
- Keine Server oder Prozesse gestartet.
- Keine Netzwerkzugriffe durchgeführt.
- Ports 8090, 8765 und 8766 wurden nicht berührt.
- Anfangs- und Endstatus blieben identisch: `53 M`, `3302 ??`.