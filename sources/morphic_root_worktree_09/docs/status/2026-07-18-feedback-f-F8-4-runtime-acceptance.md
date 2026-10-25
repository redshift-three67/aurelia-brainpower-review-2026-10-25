# Feedback f / F8.4 - Runtime Acceptance Option A

Stand: 2026-07-18
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`

## 1. Status

**F8.4 Option A ist technisch geschlossen.**

Der Admin-Catalog-Lifecycle wurde in einem isolierten synthetischen
Acceptance-Gate bis in die explizite Catalog-Runtime-Auswahl belegt:
Draft, Validate, Diff, Publish, Activate, Reload/Neustartsimulation,
zweite Aktivierung, Rollback, Kontextisolation, Kill-Switch-Grenze,
Auditkettenpruefung und redigierte Evidence.

Dies ist bewusst noch kein Browser-/Produktiv-GO. Das Ziel bleibt Option B:
derselbe fachliche Nachweis spaeter ueber laufenden FastAPI-Server,
geschuetzte Admin-UI und Browser-/Transportpfad.

## 2. Umgesetzter Scope

| Artefakt | Status | Befund |
|---|---|---|
| `core/admin_catalog/runtime_acceptance.py` | neu | Kleine Acceptance-Harness ueber bestehende `AdminCatalogService`-, `CatalogStore`- und `runtime_adapter`-Grenzen |
| `tests/test_admin_catalog_runtime_acceptance.py` | neu | Contract-Test fuer kompletten synthetischen F8.4-Option-A-Lifecycle |
| `docs/superpowers/specs/2026-07-18-feedback-f-f8-4-runtime-acceptance-design.md` | neu | Designentscheidung Option A jetzt, Option B als Ziel |
| `docs/superpowers/plans/2026-07-18-feedback-f-f8-4-runtime-acceptance.md` | neu/aktualisiert | TDD-/Status-/Verifikationsplan mit erledigten Task-1-Schritten |
| `docs/status/2026-07-18-feedback-f-F8-4-runtime-acceptance.md` | neu | Gate-Record fuer F8.4 Option A |
| `docs/2026-07-17-aktueller-umsetzungsplan-fortschritt.md` | aktualisiert | Rollup auf F8.4 Option A technisch geschlossen, Option B offen |
| `docs/status/2026-07-17-umsetzungsplan-status-tiefenanalyse.md` | aktualisiert | Tiefenanalyse auf F8.4 Option A und Option-B-Fortsetzung gehoben |

## 3. Geschlossene F8.4-Option-A-Vertraege

| Vertrag | Status | Nachweis |
|---|---|---|
| Draft -> Validate -> Diff -> Publish -> Activate laeuft ueber Public-Service-Grenzen | geschlossen | `run_synthetic_runtime_acceptance()` nutzt `AdminCatalogService` |
| Aktivierung 1 wird nach Store-Reload als aktive Catalog-Runtime gelesen | geschlossen | `revision_after_reload == "revision-a"` |
| Aktivierung 2 aendert die ausgewertete Runtime sichtbar | geschlossen | Gruppenwechsel `("group-a",)` -> `("group-b",)` |
| Rollback stellt Revision 1 wieder her | geschlossen | `revision_after_rollback == "revision-a"` und Gruppen `("group-a",)` |
| Aktivierungszaehler bleibt monoton | geschlossen | `activation_versions == (1, 2, 3)` |
| Fremder Kontext scheitert fail-closed | geschlossen | `foreign_context_error_code == "active_revision_missing"` |
| Deaktivierter Kill-Switch bleibt Legacy | geschlossen | `kill_switch_disabled_selected_source == "legacy"` |
| Auditkette bleibt gueltig | geschlossen | `audit_chain_valid is True` |
| Evidence ist redigiert | geschlossen | `redacted is True` |

## 4. Implementierungsentscheidung

Option A mutiert ausschliesslich einen testlokalen `tmp_path`-Catalog-Store.
Es gibt keine produktive Registry-Mutation, keine Remedy-DB-Mutation, keine
Source-Aktivierung, keinen Online-Fetch und keine Aenderung am produktiven
Runtime-Default.

Revision B aktualisiert bewusst stabile veroeffentlichte Managed-IDs fuer
Profile, Remedies, Pathogene, Relationen und Multiplexe, statt veroeffentlichte
Eintraege implizit verschwinden zu lassen. Damit respektiert der Test den
bestehenden Store-Vertrag, nach dem veroeffentlichte Profile als deaktivierte
Tombstones erhalten bleiben muessen, wenn sie geloescht werden sollen.

## 5. Verifikation

| Pruefung | Ergebnis |
|---|---:|
| RED | `ModuleNotFoundError: No module named 'core.admin_catalog.runtime_acceptance'` |
| F8.4-Option-A-Fokustest nach Implementierung | `1 passed in 0.36s` |
| F8.4-fokussierte Runtime-/Web-Regression | `28 passed in 2.31s` |
| `py_compile` fuer Acceptance-Harness und Test | Exitcode 0 |
| `git diff --check` | Exitcode 0; nur bekannte LF/CRLF-Warnungen in bereits dirty tracked Dateien |
| Konfliktmarker-Scan fuer F8.4-Dateien | keine Treffer |
| Trailing-Whitespace-Scan `[ \t]+$` fuer F8.4-Dateien | keine Treffer |
| Finale fokussierte Acceptance-/Runtime-/Web-/Shadow-Matrix | `35 passed in 8.17s` |

Hinweis zur Testumgebung: Die erfolgreichen Pytest-Laeufe wurden mit
`PYTHONUTF8=1`, `OPENBLAS_NUM_THREADS=1`, `TMP`/`TEMP` im Worktree,
`-p no:cacheprovider` und explizitem `--basetemp` unter `codex_tmp` ausgefuehrt,
weil die Sandbox keine Schreibrechte unter
`C:\Users\Hubert111\AppData\Local\Temp` und `.pytest_cache` bereitstellt.

## 6. Fortschritt nach F8.4 Option A

| Modell | Stand |
|---|---:|
| F8 intern | `4/4` = **100 % fuer Option A** |
| Feedback f nach Arbeitseinheiten | `39/39` = **100 % fuer Option A** |
| Feedback f nach Hauptphasen | F1-F8 100 % = **100 % fuer Option A** |
| Nutzerfeedback gesamt `a-f` | b/c/d/e fertig, f Option A technisch geschlossen, a offen = **83 %** |

## 7. Offenes Ziel-Gate

| Reihenfolge | Gate | Status | Exakter naechster Inhalt |
|---:|---|---|---|
| 1 | Option B | offen | Live-/Browser-Abnahme ueber laufenden FastAPI-Server und geschuetzte Admin-UI mit demselben fachlichen Runtime-Evidence-Ziel |

## 8. Harte Schranken

- Kein produktiver Catalog-Default.
- Deaktivierter Kill-Switch bleibt Legacy.
- Aktivierter Kill-Switch verlangt eine gueltige aktive Catalog-Revision.
- Bei aktiviertem Catalog gibt es keinen stillen Legacy-Fallback.
- Keine produktive Registry-, Remedy-DB- oder Source-Mutation durch Option A.
- Kein Commit, Staging, Push, Reset oder Cleanup ohne explizite Nutzerfreigabe.

## 9. Naechster verbindlicher Block

**Option B: Live-/Browser-Abnahme.**

Exakt weiter geht es mit der Uebertragung des gleichen fachlichen
Acceptance-Ziels auf FastAPI/Admin-UI/Browser: geschuetzter Admin-Zugang,
Draft/Validate/Diff/Publish/Activate ueber Transport, Runtime-Reload-Nachweis,
Rollback-Nachweis, Kontextisolation und redigierte Evidence.
