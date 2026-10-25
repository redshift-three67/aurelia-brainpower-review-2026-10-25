# Operator Workbench Korrekturen a–p — Gate 0 Technical Freeze v1

- Freeze-Zeit: 2026-07-21T18:10:22+02:00
- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Status: `REVIEW PENDING / NO-GO für produktiven Neustart`
- Gate: Live-/Deployment-Wahrheit und terminaler Scanprofil-Pool-Zustand

## Autoritativer Ausgangszustand

Die Gate-0-Differenz ist gegen die externe, vor Implementierungsbeginn verifizierte Sicherung zu prüfen:

`C:\Users\Hubert111\Documents\Morphic_Safeguards\2026-07-21_151323_operator-workbench-preplan\files`

Manifest:

`C:\Users\Hubert111\Documents\Morphic_Safeguards\2026-07-21_151323_operator-workbench-preplan\SOURCE_MANIFEST.sha256`

Manifest-SHA-256:

`738dabe6dd0e63f2e193c6b8729714aa77e88ba7c24efc441d4cf3b16a253bb0`

Der Worktree war vor Gate 0 bereits stark dirty. Änderungen außerhalb des unten aufgeführten Gate-0-Scopes sind weder Teil dieses Gates noch durch diesen Freeze neu freigegeben. Es wurde nichts zurückgesetzt, gestaged, committed oder gepusht.

## Gate-0-Ziele

1. `SourceRegistryError` und lokale Lesefehler des Scanprofilkatalogs werden als redigiertes HTTP 503 ausgegeben; lokale Pfade werden nicht offengelegt.
2. Browserreads besitzen ein begrenztes Timeout mit `AbortController`, ohne Polling-Timerverträge zu verfälschen.
3. Der Scanprofilkatalog besitzt autoritative Zustände `loading | ready | error`.
4. Ein Fehler wird in der Reviewkarte terminal angezeigt und kann über einen Retry behoben werden; gleichzeitig darf nicht weiter „wird geladen“ erscheinen.
5. Initiale unabhängige Reads laufen isoliert/parallel; der Profillevel-Listener ist vor ihnen gebunden.
6. Ein verspätetes Registry-Rendering darf den aktuell gewählten Wizard-Schritt nicht visuell auf Phase 1 zurücksetzen.
7. Der produktive Port 8765 bleibt bis zu zwei unabhängigen Nullbefund-Freigaben unverändert.

## Gate-0-Scope und SHA-256

```text
9772375518fc75fa3548fc94dff6deb8320d5579d12d05674cb2c70a69d0c5a0  apps/web/workbench.py
40fb5b013258a2f8b19fbfba471e28456b074f12fe8e20c8b78dc8fc14839747  apps/web/static/app.js
ab391471b0c58162db2be6c49b3223e6a02f7d087d315fce852d901279f1e85c  apps/web/static/workbench-api.js
dc5742f6bc9ab62e7603849749ff96f9b239ba04c95f6dfab58111a14cf1c2b9  apps/web/static/workbench-render.js
4b51f26e625a3a74d98065792774334b657e4f9db4b41da66a2dc9787c0b84be  apps/web/static/workbench-state.js
13b958f4ee0271349282e2c0d6e667543fd9b957e18f3116066d91e51665748a  tests/test_web_scan_profile_catalog.py
34079d75207da48e35555d81c4fbf24a7a5895b3b09b66824c03d9c14374a31b  tests/test_workbench_gate0_catalog_state.py
ae75c934d7107b1a492bbbf89af6378db063aa1166f910484d8dff1139314f44  tests/browser/workbench.spec.js
```

Plan-Autorität, unverändert seit dem letzten Planreview:

```text
4cef63af95b275eba240007b7d6a34bae43103731b17767bc2a99958423c1459  .hermes/plans/2026-07-21_152301-operator-workbench-korrekturen-a-bis-p.md
```

## RED → GREEN

Initiale Gate-0-Ausführung:

- 2 bestehende Basistests grün
- 6 neue Verträge rot aus den erwarteten Gründen:
  - Registryfehler als 422/ungefilterte Ausnahme statt redigiertem 503
  - hängender Read ohne Timeout
  - Reviewkarte bleibt im Ladezustand
  - fehlende explizite Zustände
  - serieller Bootstrap

Nach minimaler Implementierung:

- Gate-0-Verträge: `8 passed`
- fokussierte Nachbarmatrix: `100 passed`
- Browser-Einzelabnahme Fehler → Retry: `1 passed`
- vollständige Browsermatrix: `24 passed`
- vollständige Python-Suite: `1405 passed, 9 skipped in 252.48s`
- JavaScript-Syntax: bestanden
- Python-Compile: bestanden
- `git diff --check`: bestanden

Ungekürztes Full-Suite-Log außerhalb des Repositories:

`C:\Users\Hubert111\AppData\Local\Temp\morphic_gate0_full_pytest_20260721_175719.log`

Log-SHA-256:

`2193ba786b30273fe6a89eb14b20c0169d5b3bfad9af39505cae26f372e3df6e`

## Isolierte Web-Abnahme und Cleanup

- QA-Port: 8766
- synthetisches, separates Runtimeverzeichnis unter `%LOCALAPPDATA%\Temp`
- Browser: lokales Chrome, headless, ein Worker
- QA-Server beendet
- Port 8766 danach frei
- `node_modules`, `package-lock.json`, `test-results`, `playwright-report`, QA-Skript und QA-Runtime entfernt
- Port 8090/PID 17136 unverändert aktiv
- Port 8765/PID 12992 unverändert aktiv

## Explizite Nichtziele / Ausschlüsse

- kein produktiver Neustart vor Reviewfreigabe
- keine Änderung von Scan-, Score-, Profil- oder Berichtsinhalten
- keine Aktivierung von EMF, Hardwaremodulation, Harmonisierung oder Quantum
- keine Migration von Archiven oder Profilen
- keine Änderung an Authentifizierung, Rate-Limits oder produktiven Runtime-Daten
- kein Commit, Push, Staging oder Reset
- keine finale Post-State-ShadowCopy vor vollständiger Freigabe

## Reviewvertrag

Jeder Reviewer muss:

1. den Freeze-SHA sowie alle acht Scope-Hashes am Anfang und Ende selbst berechnen;
2. die aktuellen Dateien gegen die gleichnamigen Pre-Plan-Dateien unter `...\files` vergleichen; `tests/test_workbench_gate0_catalog_state.py` ist neu;
3. ausschließlich read-only arbeiten und weder Tests noch Server starten;
4. Korrektheit, Race-/Lifecycle-Verhalten, Fehlerredaktion, Timeout-/Abort-Semantik, Resetverhalten, Browserzustände und Testabdeckung prüfen;
5. P0–P3 mit `Datei:Zeile` melden;
6. nur bei Drift 0 und P0=P1=P2=P3=0 `APPROVE` ausgeben.

Jede nach diesem Freeze vorgenommene Änderung an Scope, Tests oder diesem Freeze supersediert v1 und erfordert neue Tests, einen neuen Freeze und zwei neue Reviews.
