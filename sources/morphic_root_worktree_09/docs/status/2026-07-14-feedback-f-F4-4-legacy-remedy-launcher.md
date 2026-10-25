# Feedback f – F4.4 Legacy-Remedy-Launcher

- **Stand:** 2026-07-14
- **Teilgate:** F4.4
- **Teilgate-Status:** GO
- **Gesamtgate F4:** GO; F4.1–F4.4 vollständig geschlossen
- **Feedback f als Gesamtfeature:** weiterhin NO-GO bis F8
- **Nächster zulässiger Block:** F5.1 – vollständigen Batch-Hashvertrag einführen
- **Branch:** `operator-workbench-phase1`
- **HEAD:** `619a1f5485a151816e32732929a6a823839ccb57`

## 1. Entscheidung und Umfang

Der reproduzierte Legacy-Defekt war ein Import von `services.remedy_service.find_remedies_by_keyword`, obwohl diese Funktion nicht existiert. F4.4 entscheidet sich ausdrücklich für **Migration**, nicht für Deprecation:

- Keyword und Group verwenden die bereits bestehende Authority `find_remedies_for_group()`;
- es entsteht keine lokale Ersatzsuche, kein neues SQL und keine zweite Remedy-Authority;
- Pathogen- und Statistikpfade bleiben auf ihren bestehenden Servicefunktionen;
- der Launcher behält seinen interaktiven Default und ergänzt ausschließlich testbare `-Action`, `-Query` und `-NoPause`-Parameter.

F4.4 verändert keine Admin-Catalog-Contracts, keine Drafts, keine Publish-/Activate-Logik und keine produktive Scan-/Engine-/Web-/Netzwerkverdrahtung.

## 2. Sicherheits- und Portabilitätsvertrag

- Fester Python-Code wird über stdin ausgeführt; Eingaben werden ausschließlich als `sys.argv`-Daten übergeben.
- Python startet mit `-I -X utf8 -`; fremdes CWD, `PYTHONPATH` und `sitecustomize.py` werden nicht als Importquelle wirksam.
- `$PSScriptRoot` bindet Projektroot und explizite Projekt-Venv; der Launcher verwendet kein beliebiges PATH-`python`.
- UTF-8-BOM sowie ausführbare Smokes binden PowerShell 7 und Windows PowerShell 5.1.
- Native, von null verschiedene `Int32`-Exitcodes bleiben unverändert; die Werte 7 und 300 sind unter beiden PowerShell-Runtimes testgebunden.
- Fehlende Queries liefern fail-closed einen Fehlercode.

## 3. Ergebnisgrenzen

Die bestehende Authority kann bei bekannten Kategorie-/Multiplex-Aliassen intern mehr als `max_results` zurückgeben. F4.4 verändert diese Authority nicht, sondern erzwingt die Launchergrenze nach dem Aufruf:

- Keyword: höchstens 10 Remedies;
- Group: höchstens 10 Remedies;
- Pathogen: höchstens 5 Pathogene;
- je Pathogen: höchstens 3 Remedies.

Der RED-Vertrag reproduzierte für `heel_remedies_multiplex` jeweils 100 Ausgaben in Keyword und Group. Nach der Launcher-Kappung liefern beide Pfade exakt 10.

## 4. Test- und Datengrenze

Alle datenbanknutzenden Launcher-Vertragstests arbeiten in einer temporären, Worktree-förmigen Sandbox mit Kopien von:

- `Run-RemedyLookup.ps1`;
- `services/remedy_service.py`;
- `data/remedies.db`.

Damit öffnet der getestete Launcher nicht die produktive Repository-DB. Sandbox-DB-Hash, Sidecarfreiheit und vollständiges Cleanup werden geprüft. Die produktive Authority blieb bytegleich:

- `services/remedy_service.py`: `25da32d7c0906010676e1aae57ac6467077e12ea79d1bdd88ef9e7c94207536d`;
- `data/remedies.db`: `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`.

## 5. Finale technische Evidenz

Finaler technischer Snapshot:

- `Run-RemedyLookup.ps1`: `3768590a83cd3df02d0f039c67c7d82c8217c16f24495fed52eda4a2d1e66dd5`;
- `tests/test_legacy_remedy_lookup_contract.py`: `39a89d04053c5e305b1794eca1d586cb935c1aa5f2e1720e3dd503d9458f2c06`;
- Statusfingerprint: `5fd8c3cc2fb8677ff519845c678d1a0e10222e214815245e96a9753a2c37327b`.

Verifikation:

- F4.4-Fokus: `21 passed`;
- gesamte Adminmatrix: `323 passed, 5 skipped` mit `-W error`;
- breite Regression: `824 passed, 7 skipped` plus exakt 14 bekannte Baselinefehler;
- Top-5-Smoke: `1 passed`;
- Ruff, `py_compile`, UTF-8-BOM und `git diff --check`: PASS;
- keine produktiven `remedies.db-*`-Sidecars und keine verbliebenen `f44-remedy-lookup-*`-Sandboxes;
- Port 8000 frei; bestehender Listener auf `127.0.0.1:8090`, PID 20404, blieb unangetastet.

## 6. Reviews und Gatezustand

Ausschließlich der finale technische Batch `deleg_6f615637` ist für den Implementierungssnapshot gatewirksam:

- Security-/PowerShell-Review: **APPROVE**, hohe Konfidenz, keine P0–P3;
- Daten-/Contract-/Scope-Review: **APPROVE**, hohe Konfidenz, keine P0–P3;
- Anfangs- und Endhashes identisch, kein Drift;
- keine Reviewer-Mutation, Test-, Server- oder Netzwerkaktivität.

Frühere Reviewbatches sind wegen nachfolgender Härtung ausschließlich historische Evidenz und nicht freigabewirksam.

## 7. ShadowCopy

Externe Pre-State-ShadowCopy:

```text
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260714_210943_feedback_f_F4_4_pre
```

Pre-State-Manifest-SHA-256:

```text
e18636136c81866532f7f5761a865751903d42e0cdc09ac07b4458a774a38557
```

Vorbereitetes Post-State-Ziel, das erst nach dem dokumentationsgebundenen Doppelreview erzeugt wird:

```text
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260714_221457_feedback_f_F4_4_GO_post
```

## 8. Entscheidung

**F4.4 = GO. F4 = GO.**

F4.1–F4.4 sind vollständig geschlossen. Der konservative Feedback-f-Fortschritt steigt damit von 52,8 % auf 55,6 % beziehungsweise fünf von neun vollständig geschlossenen Gates. Feedback f, produktiver Admin-Catalog, Online-Repositories und Runtimeumschaltung bleiben bis zu den getrennten F5–F8-Gates NO-GO. Nächster zulässiger Block ist F5.1.
