# Feedback f / F8.3 - Expliziter Runtime-Kill-Switch

Stand: 2026-07-18
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`

## 1. Status

**F8.3 ist technisch geschlossen.**

Der Runtime-Adapter besitzt jetzt einen expliziten Kill-Switch fuer die Catalog-Runtime-Umschaltung. `MORPHIC_ADMIN_CATALOG_ENABLED` wird strikt geparst. Deaktivierte Werte behalten den Legacy-Default ohne Catalog-Read. Aktivierte Werte laden den F8.2-Catalog-Runtime-Snapshot aus genau einer aktiven Revision. Ungueltige Werte brechen vor jedem Legacy- oder Catalog-Zugriff als Konfigurationsfehler ab.

F8.3 ist noch keine reale Admin-/Runtime-Gesamtabnahme. Diese bleibt F8.4 vorbehalten.

## 2. Umgesetzter Scope

| Artefakt | Status | Befund |
|---|---|---|
| `core/admin_catalog/runtime_adapter.py` | erweitert | `parse_admin_catalog_enabled()`, `load_configured_runtime()`, `ConfiguredRuntime`, `CatalogRuntimeConfigError` und Konstante `ADMIN_CATALOG_ENABLED_ENV` |
| `tests/test_admin_catalog_runtime_consumption.py` | erweitert | F8.3-Contract-Tests fuer deaktivierte, aktivierte und ungueltige Env-Werte sowie revisionsstabile Auswahl |
| `docs/status/2026-07-18-feedback-f-F8-3-runtime-kill-switch.md` | neu | Gate-Record fuer F8.3 |
| `docs/2026-07-17-aktueller-umsetzungsplan-fortschritt.md` | aktualisiert | Rollup auf F8.3 geschlossen, F8.4 als naechster Block |
| `docs/status/2026-07-17-umsetzungsplan-status-tiefenanalyse.md` | aktualisiert | Tiefenanalyse auf F8.3/F8.4-Fortsetzung gehoben |

## 3. Geschlossene F8.3-Vertraege

| Vertrag | Status | Nachweis |
|---|---|---|
| Env nicht gesetzt, leer, `0`, `false`, `off` bedeutet deaktiviert | geschlossen | parametrisierter Kill-Switch-Test |
| Nur `1`, `true`, `on` aktiviert Catalog | geschlossen | parametrisierter Kill-Switch-Test |
| Parsing trimmt Whitespace und ist case-insensitive | geschlossen | Werte ` FALSE ` und ` TRUE ` |
| Ungueltige Werte waehlen weder Legacy noch Catalog | geschlossen | `CatalogRuntimeConfigError` vor Store-/Legacy-Zugriff |
| Deaktivierter Zustand liest keinen Catalog | geschlossen | Store-Fake explodiert bei `current_revision_snapshot()` |
| Aktivierter Zustand verlangt gueltige aktive Catalog-Revision | geschlossen | `load_configured_runtime()` nutzt `load_catalog_runtime_snapshot()` |
| Aktivierter Zustand hat keinen Legacy-Fallback | geschlossen | `get_all_profiles()`-Fake explodiert im Fehlerszenario |
| Auswahl nutzt einen Snapshot fuer Profile und Subgroup-Provider | geschlossen | `catalog_snapshot is subgroup_provider` und Revisionsstabilitaetstest |

## 4. Implementierungsentscheidung

F8.3 schaltet den globalen Produktivpfad noch nicht dauerhaft um. Stattdessen stellt es die explizite Runtime-Auswahl bereit:

- `load_configured_runtime(..., environ=...)` entscheidet Legacy oder Catalog.
- Legacy deaktiviert: `selected_source="legacy"`, `catalog_enabled=False`, kein Catalog-Read.
- Catalog aktiviert: `selected_source="catalog"`, `catalog_enabled=True`, F8.2-Snapshot als Subgroup-Provider.
- Fehler bei aktiviertem Catalog bleiben fail-closed; es gibt keinen stillen Legacy-Fallback.

## 5. Verifikation

| Pruefung | Ergebnis |
|---|---:|
| RED | `16 failed, 7 passed`; fehlend waren `load_configured_runtime` und `CatalogRuntimeConfigError` |
| F8.3-Fokustest nach Implementierung | `23 passed in 1.03s` |
| Relevante Admin-/Legacy-/Runtime-/Subgroup-Matrix | `202 passed, 3 skipped in 23.25s` |
| `py_compile` fuer Runtime-Adapter, Subgroup-Service und F8.3-Test | Exitcode 0 |
| Konfliktmarker-Scan fuer F8.3-Dateien | keine Treffer |
| Trailing-Whitespace-Scan `[ \t]+$` fuer F8.3-Dateien | keine Treffer |
| `git diff --check` | Exitcode 0; nur bestehende LF/CRLF-Warnungen in bereits dirty tracked Dateien |
| Ruff | nicht verfuegbar: `No module named ruff` |

Hinweis zur Testumgebung: Die F8.3-Pytest-Laeufe wurden mit `OPENBLAS_NUM_THREADS=1` ausgefuehrt, weil der Importpfad NumPy/OpenBLAS laedt und ohne Threadlimit in dieser Umgebung bereits waehrend der Collection an Speicherinitialisierung scheitern kann. Der finale Matrixlauf nutzte zusaetzlich `TMP`/`TEMP` im Worktree, `--basetemp codex_tmp\pytest-f83-final-rerun-20260718` und `-p no:cacheprovider`, weil die Sandbox keine Schreibrechte unter `C:\Users\Hubert111\AppData\Local\Temp` und `.pytest_cache` bereitstellt.

## 6. Fortschritt nach F8.3

| Modell | Stand |
|---|---:|
| F8 intern | `3/4` = **75 %** |
| Feedback f nach Arbeitseinheiten | `38/39` = **97 %** |
| Feedback f nach Hauptphasen | F1-F7 100 %, F8 75 % = **97 %** |
| Nutzerfeedback gesamt `a-f` | b/c/d/e fertig, f 97 %, a offen = **83 %** |

## 7. Offenes Rest-Gate

| Reihenfolge | Gate | Status | Exakter naechster Inhalt |
|---:|---|---|---|
| 1 | F8.4 | offen | Reale Admin-/Runtime-Abnahme inklusive Draft, Publish, Activate, Neustart und Rollback |

## 8. Harte Schranken

- F8.4 ist noch offen; keine Gesamtfreigabe fuer Feedback f.
- Deaktivierter Kill-Switch bleibt Legacy.
- Aktivierter Kill-Switch verlangt eine gueltige aktive Catalog-Revision.
- Bei aktiviertem Catalog gibt es keinen Legacy-Fallback.
- Kein Commit, Staging, Push, Reset oder Cleanup ohne explizite Nutzerfreigabe.

## 9. Naechster verbindlicher Block

**F8.4: Reale Admin-/Runtime-Abnahme.**

Exakt weiter geht es mit der durchgehenden Abnahme Draft -> Validate -> Diff -> Publish -> Activate, Prozessneustart, Rollback, Kontextisolation, Source-disabled/quarantined ohne Wirkung, Audit-/Log-Schutz und finaler Regression.
