# Feedback f / F8.1 - Schattenvergleich gegen Legacy

Stand: 2026-07-18
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`

## 1. Status

**F8.1 ist technisch geschlossen.**

Der neue Schattenvergleich vergleicht eine explizite Legacy-Snapshot-Projektion read-only gegen genau eine aktive Admin-Catalog-Revision. Er klassifiziert jede Differenz deterministisch als `expected`, `warning` oder `blocker`. Der produktive Default bleibt weiterhin **Legacy**.

F8.1 aktiviert keinen Catalog, publiziert keine Revision, erzeugt keinen Source-Fetch und verdrahtet keinen produktiven Runtime-Consumer.

## 2. Umgesetzter Scope

| Artefakt | Status | Befund |
|---|---|---|
| `core/admin_catalog/shadow_comparison.py` | neu | Read-only F8.1-Reportmodul mit festen Domains, atomarem Snapshot-Read und deterministischer Diffklassifikation |
| `tests/test_admin_catalog_shadow_comparison.py` | neu | Contract-Tests fuer Read-only-Verhalten, Legacy-Default, Fehlerfaelle, atomaren Snapshot-Read, Legacy-Exportprojektion und fehlende produktive Consumer-Verdrahtung |
| `docs/status/2026-07-18-feedback-f-F8-1-shadow-comparison.md` | neu | Gate-Record fuer F8.1 |
| `docs/2026-07-17-aktueller-umsetzungsplan-fortschritt.md` | aktualisiert | Rollup auf F8.1 geschlossen, F8.2 als naechster Block |
| `docs/status/2026-07-17-umsetzungsplan-status-tiefenanalyse.md` | aktualisiert | Tiefenanalyse auf F8.1/F8.2-Fortsetzung gehoben |

## 3. Geschlossene F8.1-Vertraege

| Vertrag | Status | Nachweis |
|---|---|---|
| Profile, Gruppen, Remedies, Pathogene, Remedy-Relationen und Multiplexe werden in festen Domains verglichen | geschlossen | `_DOMAINS` und F8.1-Fixtures in `tests/test_admin_catalog_shadow_comparison.py` |
| Vergleich liest Catalogdaten aus einer expliziten aktiven Revision | geschlossen | `store.current_revision_snapshot(context)` ist der einzige produktive Store-Read |
| Split-Reads aus Aktivierungspointer und Revisionseintraegen sind verboten | geschlossen | Test `test_shadow_comparison_uses_one_atomic_active_snapshot_read` |
| Fehlende aktive Revision faellt sichtbar fail-closed aus | geschlossen | Errorcode `active_revision_missing`, Legacy bleibt selected |
| Fremder oder invalider Snapshot wird nicht gedifft | geschlossen | Errorcode `active_revision_invalid`, redigierte Meldung |
| Jede Differenz wird deterministisch klassifiziert | geschlossen | `ShadowDiffExpectation`, Default `blocker`, stabile Sortierung und Hashes |
| Default bleibt Legacy | geschlossen | `selected_source="legacy"` in Erfolg und Fehlerpfaden |
| Keine produktive Runtimewirkung | geschlossen | `productive_runtime_effect=False`, `no_publish=True`, `no_activate=True` |
| Keine produktive Consumer-Verdrahtung | geschlossen | Statischer Test gegen `shadow_comparison`-Consumer ausser Modul und Test |

## 4. Implementierungsentscheidung

F8.1 wurde bewusst als eigenes Reportmodul umgesetzt:

- Keine Re-Exports in `core/admin_catalog/__init__.py`.
- Keine Aenderung an `runtime_adapter.py`.
- Keine Aenderung an `services/subgroup_service.py`.
- Keine Aenderung an zentralen Scan-/Runtime-Zusammenstellungen.
- Kein Publish, Activate, Fetch oder Store-Write im Vergleichspfad.

Damit ist F8.1 eine belastbare Abnahmebruecke vor F8.2, aber noch keine produktive Catalog-Consumption.

## 5. Verifikation

| Pruefung | Ergebnis |
|---|---:|
| RED | `ModuleNotFoundError: No module named 'core.admin_catalog.shadow_comparison'` |
| F8.1-Fokustest nach Implementierung | `7 passed in 2.39s` |
| Relevante Admin-/Legacy-/Runtime-Matrix | `174 passed, 3 skipped in 20.53s` |
| `py_compile` fuer F8.1-Modul und Test | Exitcode 0 |
| Konfliktmarker-Scan fuer F8.1-Modul und Test | keine Treffer |
| Trailing-Whitespace-Scan fuer F8.1-Modul und Test | keine Treffer |
| `git diff --check` | Exitcode 0; bekannte LF/CRLF-Warnungen in bestehenden tracked Dateien |
| Ruff | nicht verfuegbar: `No module named ruff` |

Die Abschlussmatrix umfasst:

- `tests/test_admin_catalog_shadow_comparison.py`
- `tests/test_admin_catalog_runtime_adapter.py`
- `tests/test_admin_catalog_legacy_profiles.py`
- `tests/test_admin_catalog_legacy_remedies.py`
- `tests/test_admin_catalog_legacy_multiplexes.py`
- `tests/test_admin_catalog_validation.py`
- `tests/test_admin_catalog_store.py`
- `tests/test_admin_profile_management.py`
- `tests/test_admin_remedy_multiplex_management.py`

## 6. Fortschritt nach F8.1

| Modell | Stand |
|---|---:|
| F8 intern | `1/4` = **25 %** |
| Feedback f nach Arbeitseinheiten | `36/39` = **92 %** |
| Feedback f nach Hauptphasen | F1-F7 100 %, F8 25 % = **91 %** |
| Nutzerfeedback gesamt `a-f` | b/c/d/e fertig, f 92 %, a offen = **82 %** |

## 7. Offene Rest-Gates

| Reihenfolge | Gate | Status | Exakter naechster Inhalt |
|---:|---|---|---|
| 1 | F8.2 | offen | Vollstaendige Runtime-Consumption aus einer aktiven Revision |
| 2 | F8.3 | offen | Expliziter Kill-Switch ohne stillen Legacy-Fallback bei aktivem Catalog |
| 3 | F8.4 | offen | Reale Admin-/Runtime-Abnahme inklusive Draft, Publish, Activate, Neustart und Rollback |

## 8. Harte Schranken

- Legacy bleibt Default.
- Kein produktiver Catalog-Consumer vor F8.2.
- Kein Kill-Switch vor F8.3.
- Keine reale Admin-/Runtime-Freigabe vor F8.4.
- Kein Commit, Staging, Push, Reset oder Cleanup ohne explizite Nutzerfreigabe.

## 9. Naechster verbindlicher Block

**F8.2: Vollstaendige Runtime-Consumption aus einer Revision.**

Exakt weiter geht es mit einem Runtime-Snapshot, der Profile, Gruppen, Remedies, Pathogene, Relationen und Multiplexe atomar an dieselbe aktive Revision bindet. Erst danach darf ein expliziter Kill-Switch und danach die reale Admin-/Runtime-Abnahme folgen.
