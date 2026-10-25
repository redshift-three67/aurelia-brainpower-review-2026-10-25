# Operator Workbench Korrekturen a–p — Gate 0 Technical Freeze v2

- Freeze-Zeit: 2026-07-21T18:34:03+02:00
- Branch: `operator-workbench-phase1`
- HEAD: `3271ff9366ab3fecb2a158913a0cc19ed6a06726`
- Status: `REVIEW PENDING / NO-GO für produktiven Neustart`
- Supersedes: Gate-0 Technical Freeze v1 nach zwei driftfreien `REQUEST CHANGES`

## Historische, unveränderte Ablehnungsevidenz

```text
82e12284b4572b4110a53ae6149e7073c26dac68211a37dc962bba7e17ad0fc3  docs/reviews/2026-07-21-operator-workbench-corrections-gate0-technical-freeze-v1.md
1986e636f53b87af35390ee51ccb255a6af6bbd8fed7eb613f7bd8bd1c9bbbbb  docs/reviews/2026-07-21-operator-workbench-corrections-gate0-review-v1-1.md
6cf4e06eab32b18b274779b350feb16ba3375feb29742414b50c691085cbf029  docs/reviews/2026-07-21-operator-workbench-corrections-gate0-review-v1-2.md
```

Die beiden Reviewdateien wurden bytegleich aus dem Hermes-Delegationscache kopiert; Quell- und Zielhash waren jeweils identisch. Freeze v1 wurde nicht umgeschrieben.

## Autoritativer Ausgangszustand

Pre-Plan-Sicherung:

`C:\Users\Hubert111\Documents\Morphic_Safeguards\2026-07-21_151323_operator-workbench-preplan\files`

Manifest-SHA-256:

`738dabe6dd0e63f2e193c6b8729714aa77e88ba7c24efc441d4cf3b16a253bb0`

Plan-Autorität:

```text
4cef63af95b275eba240007b7d6a34bae43103731b17767bc2a99958423c1459  .hermes/plans/2026-07-21_152301-operator-workbench-korrekturen-a-bis-p.md
```

Der Worktree war vor Gate 0 bereits stark dirty. Nur der nachfolgende Scope wird durch v2 neu beurteilt; alle anderen Änderungen bleiben ausgeschlossen.

## Abschlussmapping der v1-Befunde

1. **P1 – Mutations-Timeout/Ambiguität:** automatischer Clienttimeout gilt jetzt ausschließlich für idempotente GET-Reads. POST/PUT/DELETE erhalten ohne explizites Upstream-Signal keine Abort-Autorität. Test: `test_workbench_api_does_not_abort_dispatched_mutations_without_reconciliation`.
2. **P1 – JSON-/ValueError-Offenlegung:** `profile_level` wird vor lokalen Reads validiert. Danach werden `SourceRegistryError`, `OSError` und lokale `ValueError`/`JSONDecodeError` geschlossen als redigiertes HTTP 503 behandelt. Tests decken alle Klassen und Nullzugriff bei ungültigem Level ab.
3. **P1 – Same-Generation Hardware-/Report-Races:** beide Loader besitzen eigene monotone Requesttokens; Hardware bindet zusätzlich den angeforderten Modus an den aktuellen Modus. Browserinterleaving beweist „latest wins“.
4. **P2 – Health/Sources seriell:** getrennte Loader werden innerhalb eines `Promise.allSettled` gleichzeitig gestartet. Browserabnahme hält Health offen und beweist vorherige Source-Hydration.
5. **P2 – `/api/sources` Sibling:** dieselbe redigierte 503-Fehlerklasse gilt nun auch für diesen parallelen Registry-Lesepfad.
6. **P2 – Mutation-/Polling-Testlücke:** Mutation ohne automatische Abort-Autorität ist verhaltensbasiert geprüft; bestehende Browserverträge für Polling-Timer und Retry bleiben grün.
7. **P2 – verspätete Registry:** expliziter Browservertrag verzögert Registry, navigiert vorher und prüft danach aktiven Step, `aria-current` und `tabindex`.
8. **P2 – Bootstrap-/Race-Testlücken:** neue echte Browserinterleavings decken verzögertes Health, Registry, Hardware und Reportkatalog ab.

## Gate-0-v2-Scope und SHA-256

```text
cb75c39894c49a7a41d361d81d04ac9cf1af69cd62d3aa3640ea2401a43e6ac7  apps/web/main.py
03797d657a6479dd0e147730272b08e06c8e529f56a2d31a185150f9878ecc37  apps/web/workbench.py
af5ba3d56f57e0d40669b755e2b367ca61edc253ef997f830bd8a71ef7026c00  apps/web/static/app.js
55c42f0142c7a55b533a454dd92d0e13663770bb61d1b4f58cf9f19806aa0421  apps/web/static/workbench-api.js
dc5742f6bc9ab62e7603849749ff96f9b239ba04c95f6dfab58111a14cf1c2b9  apps/web/static/workbench-render.js
4b51f26e625a3a74d98065792774334b657e4f9db4b41da66a2dc9787c0b84be  apps/web/static/workbench-state.js
fd0d74141f814eba25a3021003abf67a904e670f0fb0734a12f44610cf9a3d14  tests/test_web_scan_profile_catalog.py
a536621097c732c35f61e3812b4f3ac493f9a7a04075ad82787d0b5d273953a1  tests/test_workbench_gate0_catalog_state.py
d1c31a3e8b431eeaedadb51438b5c135ef3ab91282b253aa394fc802128d5936  tests/test_web_shell.py
9082dddbd6d351dce02b13c6eec467effa8ae65d10871d28c98156c22cccd7a0  tests/browser/workbench.spec.js
```

## RED → GREEN v2

Neue RED-Nachweise:

- `JSONDecodeError` wurde als 422 offengelegt.
- ungültiges Level berührte die Registry.
- Mutationen erhielten eine automatische Abort-Autorität.
- `/api/sources` ließ lokale Parsefehler unkontrolliert auslaufen.
- blockierter Health-Read blockierte Sources.
- verspätete Hardwareantwort überschieb den neueren Modus.

GREEN:

- v2-Reviewregressionen: `12 passed`
- fokussierte Nachbarmatrix: `104 passed`
- neue Browserinterleavings: `3 passed`
- vollständige Browsermatrix: `27 passed`
- vollständige Python-Suite: `1409 passed, 9 skipped in 247.03s`
- JavaScript-Syntax: bestanden
- Python-Compile: bestanden
- `git diff --check`: bestanden

Ungekürztes Full-Suite-Log:

`C:\Users\Hubert111\AppData\Local\Temp\morphic_gate0_v2_full_pytest_20260721_182206.log`

```text
512fcaa531b0ef32c28b3d2af0eb5b67222f86def74331c8f5bb9416b5378173  morphic_gate0_v2_full_pytest_20260721_182206.log
```

## Isolierte QA und Cleanup

- ausschließlich Port 8766 mit synthetischer separater Runtime
- QA-Server beendet; Port 8766 frei
- QA-Skript, QA-Runtime, `node_modules`, Lockfile und Browserreports entfernt
- Port 8090/PID 17136 unverändert aktiv
- Port 8765/PID 12992 unverändert aktiv und weiterhin nicht neu gestartet

## Ausschlüsse

- kein produktiver Neustart vor zwei neuen Nullbefund-Freigaben
- keine Änderungen an Scores, Profilinhalten, Berichten, EMF, Harmonisierung oder Quantum
- keine Migrationen oder Aktivierungen
- kein Commit, Push, Staging oder Reset
- keine finale Post-State-ShadowCopy vor vollständiger Gatefreigabe

## Reviewvertrag

Jeder Reviewer muss:

1. Freeze-v2-SHA und alle zehn Scope-Hashes am Anfang und Ende selbst berechnen;
2. v1-Freeze und beide vollständigen v1-Reviews einbeziehen;
3. aktuelle Scope-Dateien gegen die Pre-Plan-Sicherung vergleichen; neue Dateien sind explizit zu identifizieren;
4. ausschließlich read-only arbeiten, keine Tests/Server/Netzwerkzugriffe starten;
5. alle v1-Befunde sowie Sibling-Pfade erneut auf Klassenschluss prüfen;
6. P0–P3 mit `Datei:Zeile` berichten;
7. nur bei Drift 0 und P0=P1=P2=P3=0 `APPROVE` ausgeben.

Jede Scope-, Test- oder Freezeänderung nach diesem Freeze supersediert v2 und erfordert erneut vollständige Gates und zwei neue Reviews.
