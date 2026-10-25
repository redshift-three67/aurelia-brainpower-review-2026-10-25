## Zweiter unabhängiger adversarieller Gate-0-v2-Review

**Verdikt: REQUEST CHANGES**  
**Konfidenz: HOCH**

- **Drift:** 0
- **P0:** 0
- **P1:** 2
- **P2:** 1
- **P3:** 0
- **Branch:** `operator-workbench-phase1`
- **HEAD:** `3271ff9366ab3fecb2a158913a0cc19ed6a06726`

### Hashbindung

Alle Start- und Endhashes waren identisch und entsprachen Freeze v2:

| Objekt | SHA-256 Start = Ende | Drift |
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

Pflichtkontext v1 und beide v1-Reviews waren hashidentisch zur v2-Deklaration. Das externe Baseline-Manifest hatte den erwarteten SHA-256 `738dabe6…53bb0`; neun Scope-Dateien existierten dort und unterschieden sich vom v2-Stand, `tests/test_workbench_gate0_catalog_state.py` ist neu.

## Befunde

| Priorität | Befund | Fundstelle |
|---|---|---|
| **P1** | **Mutation-Commit-Ambiguität bleibt trotz Entfernung des automatischen Mutationstimeouts bestehen.** Ein mutierender `fetch()` kann nach serverseitigem Commit durch Verbindungsabbruch oder verlorene Antwort ablehnen. `requestJson()` reduziert dann im `finally` die Mutationssperre; Scan- und Harmonisierungsstarter löschen anschließend ihren Pending-Zustand und erlauben den Retry, obwohl der erste Job bereits existieren kann. Der neue Test beweist lediglich, dass `saveDraft()` kein Signal erhält, nicht dass ein „Commit vor Transportfehler“ reconciled wird. Damit ist der v1-P1 nur für den speziellen Timeout-Auslöser, nicht für die eigentliche Commit-Ambiguitätsklasse geschlossen. | `apps/web/static/workbench-api.js:46-54`, `apps/web/static/workbench-api.js:87-99`, `apps/web/static/app.js:462-507`, `apps/web/static/app.js:833-873`, `tests/test_workbench_gate0_catalog_state.py:57-79` |
| **P1** | **Der neue Fallwechsel erzeugt eine sichtbare Solfeggio-/Zielwert-ABA.** `resetChoiceCardControls()` setzt Backing-State und Formularwert auf 432, ruft `wireSolfeggioChoiceCards()` aber ohne den erforderlichen Container-Selektor auf. Die bereits gerenderte Choice-Card kann deshalb weiterhin beispielsweise 528 Hz als ausgewählt anzeigen, während eine anschließende Harmonisierung tatsächlich 432 Hz sendet. Die Reset-Browserverträge prüfen zwar Fortschritt und andere Felder, aber nicht den visuellen Solfeggio-Zustand gegen `selectedSolfeggioBase` und `target_frequency`. | `apps/web/static/app.js:1274-1285`, `apps/web/static/app.js:1314-1330`, `tests/browser/workbench.spec.js:42-194`, `tests/browser/workbench.spec.js:1112-1126` |
| **P2** | **Der Timeout-Harness liefert ein Falschpositiv für die vollständige Read-Timeout-Semantik.** Der Test simuliert nur einen `fetch`, der vor den Response-Headern hängt. Treffen die Header rechtzeitig ein, hängt aber `response.json()`, kann der Timeout den Body-Read mit `AbortError` abbrechen. Dieser Fehler wird vom allgemeinen JSON-Catch verschluckt und ein erfolgreicher HTTP-Read als `null` aufgelöst, statt `request_timeout` zu melden. Downstream entstehen dadurch je nach Loader TypeErrors, generische Fehler oder Retries statt der zugesicherten Timeout-Fehlerklasse. | `apps/web/static/workbench-api.js:51-68`, `apps/web/static/workbench-api.js:69-86`, `tests/test_workbench_gate0_catalog_state.py:23-54` |

### Erforderliche Korrekturen

1. Mutationen mit einer clientgenerierten Idempotency-/Request-ID und serverseitiger Status-Reconciliation binden; insbesondere Startoperationen dürfen nach Transportfehler nicht blind erneut freigegeben werden.
2. Beim Reset `wireSolfeggioChoiceCards("#solfeggio-base-choices")` verwenden und den Gleichlauf von sichtbarer Auswahl, Backing-State und Formularwert verhaltensbasiert prüfen.
3. Timeout-/Abortfehler über `fetch` **und** Body-Decoding hinweg klassifizieren; einen Harness ergänzen, bei dem die Response-Header eintreffen, aber `response.json()` bis zum Abort hängt.

### Read-only-Nachweis

- Keine Tests, Server oder Netzwerkzugriffe gestartet.
- Keine Repositorydateien erstellt oder verändert.
- Durch die automatische Größenbegrenzung des Hermes-Readers wurden zwei Ausgabe-Cachedateien außerhalb des Repositories unter `C:\Users\Hubert111\AppData\Local\hermes\cache\terminal\hermes-results\` angelegt; keine Projekt- oder Scope-Datei war betroffen.