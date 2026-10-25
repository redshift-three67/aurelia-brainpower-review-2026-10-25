## Zweiter unabhängiger adversarieller Gate-0-v3-Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**

- **Drift:** 0
- **P0:** 0
- **P1:** 3
- **P2:** 1
- **P3:** 0
- **Branch:** `operator-workbench-phase1`
- **HEAD Start = Ende:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`

### Start-/Endhashbindung

Alle Werte waren am Anfang und Ende identisch und entsprachen exakt Freeze v3:

| Objekt | SHA-256 Start = Ende | Drift |
|---|---|---:|
| Freeze v3 | `833ced9d4dc60b776321350b7fef5b29689d660776706812f859f186b59a16af` | 0 |
| `apps/web/main.py` | `f51d667a1cf639b88575a4f097b40b36c9890b7f711c387dec89362e51b73c58` | 0 |
| `apps/web/workbench.py` | `03797d657a6479dd0e147730272b08e06c8e529f56a2d31a185150f9878ecc37` | 0 |
| `apps/web/start_operations.py` | `2d6daeace3adddf9215da6b3b5bcdd6d30a54021c41b1408b2dd536f042b90a9` | 0 |
| `apps/web/static/app.js` | `4b8992ee5259214e82fadf93b72284e145f3aabc74b294a96668a0e66e665f70` | 0 |
| `apps/web/static/workbench-api.js` | `6f7bca07e8c15c871da98e124c051c1fa11630e785efb268ac6d49bc305faa9a` | 0 |
| `apps/web/static/workbench-render.js` | `dc5742f6bc9ab62e7603849749ff96f9b239ba04c95f6dfab58111a14cf1c2b9` | 0 |
| `apps/web/static/workbench-state.js` | `e81cf8f15a386bac78a63fa38e52baa1db900097d64195318a12dce04cad70ac` | 0 |
| `core/source_registry.py` | `7061fac193ef389106dd9ad7f3e53bddb6daffa44e3b51c7b209a1dce0c578cf` | 0 |
| `tests/test_source_registry.py` | `1e4d79b28f1528189b92bd80c758bac681ecc3b6f57ebf4d36f4f684297c5d4d` | 0 |
| `tests/test_web_scan_profile_catalog.py` | `7e3ac77d31201d66979fbf0d6d189d115d9642fb39f239caf37c440127092bdb` | 0 |
| `tests/test_start_operations.py` | `e9e224d154eb427aca9fbd5a6cf63d74b4927c63565bdf16464d0a8ead6073e5` | 0 |
| `tests/test_workbench_gate0_catalog_state.py` | `688fa55e1acd7c936e37fed601672ca1b7d67ab022ceb5f533db55379d649f4b` | 0 |
| `tests/test_web_shell.py` | `98d6577eded77edd5bcb30450917776927e98f1466d12e7c28622befcc169c39` | 0 |
| `tests/test_workbench_error_ui_js.py` | `9f1dde887517be639d3aba62ba7cb600b00cd144543841a87ce35850c9cddc42` | 0 |
| `tests/browser/workbench.spec.js` | `ca4d774f298048e1321f965bda035ed7dbde21e073f728f6fbc1f22e5c2e1530` | 0 |

Die drei immutable v2-Artefakte stimmen ebenfalls:

- Freeze v2: `702ec049d3f0bf910fb0a322528368942f2b1e0758d769608fab365f1c19c408`
- Review v2-1: `2950d8a5478a5d5436ecccf06e86fdd9afdfc09c1b672bd24fd850cab9fdc512`
- Review v2-2: `7fa369822402b4557a3e74744fad7a69b013bd8ead61bafcd1b0606ef6e0c83d`

## Befunde

| Priorität | Befund | Fundstelle |
|---|---|---|
| **P1** | Die Start-Operation-Autorität ist nicht prozessübergreifend atomar. `threading.RLock` schützt nur eine Store-Instanz im aktuellen Prozess. Zwei Worker/Prozesse können beide `path.exists() == false` beobachten, jeweils einen ersetzenden `pending`-Record veröffentlichen und anschließend jeweils einen Job erzeugen. `complete()` ist ebenfalls kein CAS und kann danach die konkurrierenden Job-IDs gegenseitig überschreiben. Das lässt doppelte Jobs bei parallelem Retry, Reload/altem Request oder mehreren Server-Workern zu. | `apps/web/start_operations.py:43-46`, `apps/web/start_operations.py:123-147`, `apps/web/start_operations.py:149-165` |
| **P1** | Die öffentliche Start-API erzwingt keine Idempotency-ID. Fehlt der Header, liefert `_begin_start_operation()` unmittelbar „nicht beansprucht“ zurück; beide Endpunkte erzeugen den Job danach ungeschützt. Ein direkter API-Client, ältere UI oder verlorener Header kann nach Antwortverlust erneut senden und einen zweiten Scan-/Harmonisierungsjob erzeugen. Die Autorität ist daher nicht klassenweit vor jeder Job-Erzeugung aktiv. | `apps/web/main.py:678-684`, `apps/web/main.py:756-770`, `apps/web/main.py:882-909`; bedingte Headerweitergabe `apps/web/static/workbench-api.js:252-260`, `apps/web/static/workbench-api.js:294-302` |
| **P1** | Payload-Mismatch oder beschädigter persistenter Record wird serverseitig als HTTP 422 ausgegeben; der Browser löscht bei jedem 422 die gespeicherte Operation-ID. Konkreter Ablauf: erster Request erzeugt/komplettiert einen Job, Antwort geht verloren, Reload oder Formänderung verändert den Payload, Wiederholung mit alter ID erhält „identity mismatch“ 422, der Client löscht die ID, und der folgende Klick erzeugt mit einer neuen ID einen zweiten Job. Dasselbe fail-open-Verhalten gilt bei einem unlesbaren/korrupten Record. Damit sind Client-Key-Verlust, persistente Korruption und sichere 4xx-Clear-Semantik nicht geschlossen. | Serverklassifikation `apps/web/main.py:685-696`; Recordfehler `apps/web/start_operations.py:80-109`, `apps/web/start_operations.py:124-133`; Clear-Entscheidung `apps/web/static/app.js:82-102`, `apps/web/static/app.js:573-579`, `apps/web/static/app.js:944-954` |
| **P2** | Die neuen Tests beweisen die produktiven Risikogrenzen nicht. Der Browser-„lost response“-Test fängt den ersten Request per Playwright-Route ab und bricht ihn ab, ohne einen echten serverseitigen Commit zu erzeugen; die zweite Antwort wird ebenfalls synthetisch erfüllt. Die Backendtests prüfen nur sequenzielle Wiederholung bzw. sequenzielle Store-Neuerzeugung. Es fehlt ein echter Commit-vor-Antwortverlust-Vertrag, ein Payloadwechsel nach Reload, beschädigter Record sowie eine konkurrierende Prüfung mit zwei unabhängigen Store-/Serverprozessen. | `tests/browser/workbench.spec.js:487-541`, `tests/test_start_operations.py:14-72`, `tests/test_web_shell.py:771-798`, `tests/test_web_shell.py:994-1024` |

## Klassenschluss der v2-Befunde

| Befundklasse | Ergebnis |
|---|---|
| Strukturell fehlerhafte Registryeinträge und redigierte Sibling-Routen | **Geschlossen**: Nicht-Mappings werden vor Mappingzugriffen in `SourceRegistryError` normalisiert; beide realen Routen besitzen malformed-Registry-Verträge. |
| Timeout während `response.json()` | **Geschlossen**: eigener Timeout bleibt `request_timeout`. |
| Upstream-Abort während Body-Read | **Geschlossen**: `AbortError` wird nicht mehr zu `null` oder HTTP-Fehler umklassifiziert. |
| Solfeggio-DOM-/Backing-/Form-Reset | **Geschlossen**: explizites DOM-Ziel und echter Browserabgleich für 528 → 432 vorhanden. |
| Mutation-Commit-Ambiguität / langlebige Idempotenz | **Nicht geschlossen**: optionale Autorität, prozesslokale Synchronisation und unsicheres Löschen bei 422. |
| Cross-Tenant-/Owner-Bindung | Kein separater Replay-Befund im geprüften Pfad; Owner und Requesthash werden geprüft und Job-Replays anschließend erneut eigentumsgeprüft. |
| Reset-/LocalStorage-Privacy | Keine Klientendaten im neuen Operation-Key-Record gefunden; der Privacy-Reset sperrt bei ungelösten IDs fail-closed. Die oben beschriebene 422-Löschung bleibt jedoch ein Integritätsproblem. |

## Read-only-Nachweis

- Keine Tests oder Server gestartet.
- Keine Netzwerkzugriffe durchgeführt.
- Keine Repositorydateien erstellt, geändert oder gelöscht.
- Ausschließlich statische Reads, SHA-256 und read-only Git-Abfragen verwendet.
- Eine versehentlich zu große `git ls-files --others`-Ausgabe wurde durch die Hermes-Laufzeit gekürzt; eine mögliche Infrastruktur-Cachepersistenz außerhalb des Repositories kann deshalb nicht ausgeschlossen werden. Alle Repository- und Scopehashes blieben unverändert.

**Freigabe bleibt NO-GO.**