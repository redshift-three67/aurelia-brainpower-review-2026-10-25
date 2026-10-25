## Unabhängiger Gate-0-Review v2

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**

- **Drift:** 0
- **P0:** 0
- **P1:** 2
- **P2:** 0
- **P3:** 0
- **Branch:** `operator-workbench-phase1`
- **HEAD:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`

### Hashbindung Anfang → Ende

Alle Werte entsprachen am Anfang und Ende exakt dem Freeze-v2-Manifest:

| Objekt | SHA-256 | Drift |
|---|---|---:|
| Freeze v2 | `702ec049d3f0bf910fb0a322528368942f2b1e0758d769608fab365f1c19c408` | 0 |
| `apps/web/main.py` | `cb75c39894c49a7a41d361d81d04ac9cf1af69cd62d3aa3640ea2401a43e6ac7` | 0 |
| `apps/web/workbench.py` | `03797d657a6479dd0e147730272b08e06c8e529f56a2d31a185150f9878ecc37` | 0 |
| `apps/web/static/app.js` | `af5ba3d56f57e0d40669b755e2b367ca61edc253ef997f830bd8a71ef7026c00` | 0 |
| `apps/web/static/workbench-api.js` | `55c42f0142c7a55b533a454dd92d0e13663770bb61d1b4f58cf9f19806aa0421` | 0 |
| `apps/web/static/workbench-render.js` | `dc5742f6bc9ab62e7603849749ff96f9b239ba04c95f6dfab58111a14cf1c2b9` | 0 |
| `apps/web/static/workbench-state.js` | `4b51f26e625a3a74d98065792774334b657e4f9db4b41da66a2dc9787c0b84be` | 0 |
| `tests/test_web_scan_profile_catalog.py` | `fd0d74141f814eba25a3021003abf67a904e670f0fb0734a12f44610cf9a3d14` | 0 |
| `tests/test_workbench_gate0_catalog_state.py` | `a536621097c732c35f61e3812b4f3ac493f9a7a04075ad82787d0b5d273953a1` | 0 |
| `tests/test_web_shell.py` | `d1c31a3e8b431eeaedadb51438b5c135ef3ab91282b253aa394fc802128d5936` | 0 |
| `tests/browser/workbench.spec.js` | `9082dddbd6d351dce02b13c6eec467effa8ae65d10871d28c98156c22cccd7a0` | 0 |

Freeze v1 und beide v1-Reviews wurden vollständig einbezogen; ihre Hashes stimmen ebenfalls:

- Freeze v1: `82e12284…0fc3`
- Review v1-1: `1986e636…bbbb`
- Review v1-2: `6cf4e06e…f029`

Das Baseline-Manifest wurde mit `738dabe6…3bb0` bestätigt. Sämtliche Baseline-Dateien entsprachen ihren Manifest-Einträgen; `tests/test_workbench_gate0_catalog_state.py` ist neu. Die vollständigen Änderungen aller zehn Scope-Dateien gegen die Baseline wurden geprüft.

## Befunde

| Priorität | Befund | Fundstelle |
|---|---|---|
| **P1** | Die Registry-Fehlerklasse ist weiterhin nicht geschlossen. Beide Endpunkte fangen nur `SourceRegistryError`, `OSError` und `ValueError`. Ein syntaktisch gültiger, aber strukturell beschädigter Katalog wie `{"sources":[1]}` erreicht `SourceManifest.from_mapping(1)` und löst bei der Feldprüfung einen ungefangenen `TypeError` aus. Damit entsteht bei beiden Endpunkten kein zugesicherter redigierter HTTP 503. Die neuen Tests injizieren nur bereits klassifizierte Ausnahmen und prüfen diesen realen Parserpfad nicht. | `apps/web/workbench.py:94-106`, `apps/web/main.py:613-620`, ursächlicher Pfad `core/source_registry.py:241`, `core/source_registry.py:1701-1705`; Testlücke `tests/test_web_scan_profile_catalog.py:55-88`, `tests/test_web_shell.py:466-482` |
| **P1** | Timeout- und Upstream-Abort-Semantik gilt nicht für die vollständige GET-Übertragung. Sobald `fetch()` nach Empfang der Header aufgelöst wurde, wird ein späterer Abort während `response.json()` pauschal verschluckt und in `payload = null` umgewandelt. Ein erfolgreicher 2xx-Read kann dadurch trotz Timeout oder explizitem Upstream-Abort erfolgreich mit `null` zurückkehren; bei Fehlerantworten wird der Abort als HTTP-Status fehlklassifiziert. Der Timeout-Test simuliert ausschließlich einen vor den Headern hängenden `fetch()` und erkennt das nicht. | `apps/web/static/workbench-api.js:52-68`, `tests/test_workbench_gate0_catalog_state.py:23-54` |

### Klassenschluss

Statisch nachvollziehbar geschlossen sind:

- automatische Timeouts nur für GET; Mutationen erhalten ohne explizites Signal keine Abort-Autorität;
- Vorvalidierung des Profillevels vor lokalen Reads;
- getrennte parallele Health-/Sources-Hydration;
- Hardware- und Reportkatalog-Requesttokens;
- Wizard-Registry-Race bezüglich aktivem Step, `aria-current` und `tabindex`;
- Reset-/Generation-Guards und die zugehörigen Browserinterleavings.

**Nicht geschlossen** bleiben die vollständige Registry-Parsefehlerklasse beider Endpunkte sowie Timeout/Upstream-Abort während des Response-Body-Reads.

### Read-only-Nachweis

- Keine Dateien erstellt, geändert oder gelöscht.
- Keine Tests oder Server gestartet.
- Keine Netzwerkzugriffe durchgeführt.
- Ausschließlich statische Reads, Hashing und read-only Git-/Baseline-Vergleiche verwendet.