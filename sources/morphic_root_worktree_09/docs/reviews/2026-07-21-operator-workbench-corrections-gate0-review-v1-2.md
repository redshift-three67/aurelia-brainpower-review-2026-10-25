## Review-Ergebnis

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**

**Befunde:** P0=0 · P1=2 · P2=3 · P3=0  
**Drift:** 0  
`APPROVE` ist wegen der fünf Befunde ausgeschlossen.

### Hashbindung

Branch und HEAD blieben unverändert:

- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`

| Objekt | SHA-256 Beginn | SHA-256 Ende | Drift |
|---|---|---|---:|
| Technical Freeze v1 | `82e12284b4572b4110a53ae6149e7073c26dac68211a37dc962bba7e17ad0fc3` | identisch | 0 |
| `apps/web/workbench.py` | `9772375518fc75fa3548fc94dff6deb8320d5579d12d05674cb2c70a69d0c5a0` | identisch | 0 |
| `apps/web/static/app.js` | `40fb5b013258a2f8b19fbfba471e28456b074f12fe8e20c8b78dc8fc14839747` | identisch | 0 |
| `apps/web/static/workbench-api.js` | `ab391471b0c58162db2be6c49b3223e6a02f7d087d315fce852d901279f1e85c` | identisch | 0 |
| `apps/web/static/workbench-render.js` | `dc5742f6bc9ab62e7603849749ff96f9b239ba04c95f6dfab58111a14cf1c2b9` | identisch | 0 |
| `apps/web/static/workbench-state.js` | `4b51f26e625a3a74d98065792774334b657e4f9db4b41da66a2dc9787c0b84be` | identisch | 0 |
| `tests/test_web_scan_profile_catalog.py` | `13b958f4ee0271349282e2c0d6e667543fd9b957e18f3116066d91e51665748a` | identisch | 0 |
| `tests/test_workbench_gate0_catalog_state.py` | `34079d75207da48e35555d81c4fbf24a7a5895b3b09b66824c03d9c14374a31b` | identisch | 0 |
| `tests/browser/workbench.spec.js` | `ae75c934d7107b1a492bbbf89af6378db063aa1166f910484d8dff1139314f44` | identisch | 0 |

### Befunde

| Priorität | Befund | Evidenz |
|---|---|---|
| **P1** | Der neue Timeout gilt auch für mutierende Requests. Ein clientseitiger Abort kann nicht beweisen, dass die serverseitige Mutation abgebrochen wurde. Nach 30 Sekunden wird `pendingMutations` dennoch reduziert und die UI entsperrt; bei Scan-/Harmonisierungsstarts wird der Start als fehlgeschlagen behandelt und erneut ermöglicht. Ein bereits serverseitig erzeugter Job kann dadurch ohne bekannte Job-ID weiterlaufen und ein Retry einen konkurrierenden Job starten. | `apps/web/static/workbench-api.js:8-21`, `apps/web/static/workbench-api.js:42-55`, `apps/web/static/workbench-api.js:91-95`, `apps/web/static/app.js:440-484`, `apps/web/static/app.js:804-844` |
| **P1** | Die Parallelisierung eröffnet Same-Generation-Races bei den Bootstrap-Siblings. Hardware- und Report-Loader besitzen nur eine Fallgeneration, aber keinen Requesttoken. Eine verspätete initiale Standard-Hardwareantwort kann daher eine neuere Antwort nach einem Moduswechsel überschreiben; entsprechend kann ein verspäteter initialer Reportkatalog einen neueren manuellen oder terminalen Refresh ersetzen. | `apps/web/static/app.js:386-392`, `apps/web/static/app.js:641-704`, `apps/web/static/app.js:1320-1336`, `apps/web/static/app.js:1417-1418`, `apps/web/static/app.js:1430-1435` |
| **P2** | Das Ziel „unabhängige Reads isoliert/parallel“ ist nicht vollständig umgesetzt: Health und Sources bleiben innerhalb `loadHealthAndSources()` seriell. Ein hängender Health-Read verzögert den unabhängigen Source-Read bis zum Timeout. Der statische Test prüft lediglich, dass der kombinierte Loader in `Promise.allSettled()` vorkommt. | `apps/web/static/app.js:266-294`, `apps/web/static/app.js:1332`, `tests/test_workbench_gate0_catalog_state.py:121-133` |
| **P2** | Sibling-Path-Gap bei derselben Registry-Autorität: `/api/workbench/scan-profile-catalog` redigiert `SourceRegistryError`/`OSError` als 503, `/api/sources` lässt dieselben Fehler dagegen unkontrolliert als 500 auslaufen. Damit ist die Fehlerklassifizierung der parallel gestarteten Registry-Lesewege nicht geschlossen. | `apps/web/workbench.py:84-103`, `apps/web/main.py:611-619` |
| **P2** | Die Browserverträge decken die risikoreichen neuen Grenzen nicht ab. Der Timeout-Test prüft nur einen hängenden GET-Registry-Read in einem Node-Stub; es fehlen Verträge für mutation-timeout/unklare Commitlage, Polling nach echtem Timeout, hängenden Bootstrap bei weiter bedienbarer UI sowie Same-Generation-Reordering von Hardware und Reports. Der Bootstrap-Test ist überwiegend Source-String-Prüfung. | `tests/test_workbench_gate0_catalog_state.py:23-54`, `tests/test_workbench_gate0_catalog_state.py:106-133`, `tests/browser/workbench.spec.js:265-340`, `tests/browser/workbench.spec.js:694-760` |

### Erforderliche Korrekturen

1. Read-Timeouts von Mutationen trennen; mutierende Starts entweder nicht clientseitig abbrechen oder mit serverseitigem Idempotenz-/Requesttoken und anschließender Status-Reconciliation binden.
2. Hardware- und Report-Loader an `(caseGeneration, requestToken, angeforderter Modus/Reportkontext)` binden.
3. Health und Sources als zwei unabhängig begrenzte Bootstrap-Promises starten.
4. Alle produktiven `SourceRegistry.load_default()`-Read-Siblings konsistent in sichere, redigierte Fehlerantworten überführen.
5. Echte Browserverträge für diese Interleavings ergänzen; reine String-Prüfungen reichen für Race-/Lifecycle-Aussagen nicht.

### Read-only-Nachweis

- Keine Tests, Server oder Netzwerkzugriffe gestartet.
- Keine Dateien erstellt, geändert, gestaged oder gelöscht.
- Baseline-Vergleich gegen die angegebene Pre-Plan-Sicherung durchgeführt.
- Ein MSYS-internes `git diff --no-index` konnte den absoluten Baseline-Pfad nicht auflösen; der Vergleich wurde anschließend rein lesend mit `diff -u` durchgeführt.