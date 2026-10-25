## Unabhängiger Gate-0-Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**

- **Drift:** 0
- **P0:** 0
- **P1:** 2
- **P2:** 2
- **P3:** 0
- **HEAD:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- **Branch:** `operator-workbench-phase1`

### Hashbindung

| Objekt | SHA-256 Anfang | SHA-256 Ende | Drift |
|---|---|---|---:|
| Freeze | `82e12284b4572b4110a53ae6149e7073c26dac68211a37dc962bba7e17ad0fc3` | identisch | 0 |
| `apps/web/workbench.py` | `9772375518fc75fa3548fc94dff6deb8320d5579d12d05674cb2c70a69d0c5a0` | identisch | 0 |
| `apps/web/static/app.js` | `40fb5b013258a2f8b19fbfba471e28456b074f12fe8e20c8b78dc8fc14839747` | identisch | 0 |
| `apps/web/static/workbench-api.js` | `ab391471b0c58162db2be6c49b3223e6a02f7d087d315fce852d901279f1e85c` | identisch | 0 |
| `apps/web/static/workbench-render.js` | `dc5742f6bc9ab62e7603849749ff96f9b239ba04c95f6dfab58111a14cf1c2b9` | identisch | 0 |
| `apps/web/static/workbench-state.js` | `4b51f26e625a3a74d98065792774334b657e4f9db4b41da66a2dc9787c0b84be` | identisch | 0 |
| `tests/test_web_scan_profile_catalog.py` | `13b958f4ee0271349282e2c0d6e667543fd9b957e18f3116066d91e51665748a` | identisch | 0 |
| `tests/test_workbench_gate0_catalog_state.py` | `34079d75207da48e35555d81c4fbf24a7a5895b3b09b66824c03d9c14374a31b` | identisch | 0 |
| `tests/browser/workbench.spec.js` | `ae75c934d7107b1a492bbbf89af6378db063aa1166f910484d8dff1139314f44` | identisch | 0 |

Die externe Pre-Plan-Sicherung war erreichbar. Ihr Manifest besitzt den angegebenen SHA-256 `738dabe6dd0e63f2e193c6b8729714aa77e88ba7c24efc441d4cf3b16a253bb0`; die sieben vorhandenen Baseline-Dateien stimmen mit ihren Manifest-Einträgen überein. `tests/test_workbench_gate0_catalog_state.py` ist wie deklariert neu.

## Befunde

| Priorität | Befund | Fundstelle |
|---|---|---|
| **P1** | Der neu eingeführte Timeout gilt nicht nur für Browser-Reads, sondern unterschiedslos auch für alle POST/PUT/DELETE-Aufrufe. Wird etwa ein Job serverseitig erzeugt und die Antwort nach 30 Sekunden abgebrochen, verwirft der Client die autoritative Job-ID, setzt `scanStartPending` zurück und aktiviert einen erneuten Start. Dadurch sind verwaiste oder doppelte Jobs möglich. Dasselbe Ambiguitätsfenster betrifft Speichern, Löschen und Stoppen. | `apps/web/static/workbench-api.js:8-21`, `apps/web/static/workbench-api.js:32-55`, `apps/web/static/app.js:457-484`, `apps/web/static/app.js:816-843` |
| **P1** | Die Fehlerredaktion ist nicht vollständig. `SourceRegistryError` und `OSError` werden zwar redigiert, andere lokale Registry-Parsefehler fallen jedoch in den generischen `ValueError`-Zweig und werden als HTTP 422 mit `str(exc)` veröffentlicht. Insbesondere ein direkt aus `json.loads` kommender `JSONDecodeError` ist ein `ValueError`, aber kein `SourceRegistryError`. Ein beschädigter lokaler Katalog erhält daher weder den vorgesehenen redigierten 503 noch die zugesicherte terminale Fehlerklasse. | `apps/web/workbench.py:89-103` |
| **P2** | Der Timeout-Test deckt ausschließlich einen hängenden `loadRegistry()`-Read ab. Nicht abgesichert sind Upstream-Abort versus Timeout, der `setTimeout`-Fallback, Listener-Cleanup sowie insbesondere die ausdrücklich geforderte Unverändertheit der Scan-/Harmonisierungs-Polling-Timer und Retry-Zustände. | `tests/test_workbench_gate0_catalog_state.py:23-54` |
| **P2** | Für das explizite Ziel „verspätetes Registry-Rendering setzt den aktuell gewählten Schritt nicht visuell auf Phase 1 zurück“ fehlt ein verhaltensbasierter Regressionstest. Die produktive Änderung berechnet zwar den aktiven Index neu, aber kein Gate-0-Test verzögert die Registry-Antwort, navigiert vorher weiter und prüft danach aktiven Step, `aria-current` und `tabindex`. | `apps/web/static/workbench-render.js:26-45`, `tests/test_workbench_gate0_catalog_state.py:121-133` |

## Empfehlung

1. Timeouts standardmäßig auf idempotente Reads begrenzen. Mutationen benötigen entweder keinen clientseitigen Abbruch nach Versand oder eine Idempotency-/Reconciliation-Autorität, mit der ein abgebrochener Start/Stop sicher wiedergefunden wird.
2. Eingabevalidierung für `profile_level` vor den lokalen Reads durchführen und anschließend alle Registry-Lade-/Parsefehler geschlossen auf den redigierten 503 abbilden.
3. Adversarielle Tests für:
   - Server-Commit unmittelbar vor clientseitigem Mutationstimeout,
   - malformed JSON/`JSONDecodeError`,
   - Polling-Timeout mit genau einem Retry-Timer,
   - verspätete Registry-Antwort nach Navigation.

**Dateien erstellt oder geändert:** keine.  
**Tests, Server oder Netzwerk gestartet:** nein.