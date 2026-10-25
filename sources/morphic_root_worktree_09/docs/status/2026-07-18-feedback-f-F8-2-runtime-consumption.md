# Feedback f / F8.2 - Runtime-Consumption aus einer Revision

Stand: 2026-07-18
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`

## 1. Status

**F8.2 ist technisch geschlossen.**

Der Runtime-Adapter kann jetzt einen expliziten Catalog-Runtime-Snapshot aus genau einer aktiven Admin-Catalog-Revision laden. Der Snapshot umfasst Profile, Gruppen, Remedies, Pathogene, Remedy-Relationen und Multiplexe und ist fail-closed: fehlt die aktive Revision oder ist sie invalide, gibt es keinen stillen Legacy-Fallback.

Der bestehende Defaultpfad bleibt unverändert. `SubgroupService` nutzt weiterhin prozedurale Legacy-Gruppen, solange kein Catalog-Provider explizit injiziert wird.

## 2. Umgesetzter Scope

| Artefakt | Status | Befund |
|---|---|---|
| `core/admin_catalog/runtime_adapter.py` | erweitert | `load_catalog_runtime_snapshot()` und immutable F8.2-Runtime-Datentraeger fuer Gruppen, Remedies, Pathogene, Relationen und Multiplexe |
| `services/subgroup_service.py` | erweitert | optionale `catalog_provider`-Injektion fuer Gruppenliste, Gruppenkandidaten und Fullbody-Kandidaten; ohne Provider unveraenderter prozeduraler Pfad |
| `tests/test_admin_catalog_runtime_consumption.py` | neu | Contract-Tests fuer atomaren Snapshot, alle Runtime-Domains, Remedy-/Multiplexauflösung, fail-closed Fehler, Revisionsstabilitaet und Provider-Injektion |
| `docs/status/2026-07-18-feedback-f-F8-2-runtime-consumption.md` | neu | Gate-Record fuer F8.2 |
| `docs/2026-07-17-aktueller-umsetzungsplan-fortschritt.md` | aktualisiert | Rollup auf F8.2 geschlossen, F8.3 als naechster Block |
| `docs/status/2026-07-17-umsetzungsplan-status-tiefenanalyse.md` | aktualisiert | Tiefenanalyse auf F8.2/F8.3-Fortsetzung gehoben |

## 3. Geschlossene F8.2-Vertraege

| Vertrag | Status | Nachweis |
|---|---|---|
| Runtime-Snapshot bindet alle Domains an dieselbe aktive Revision-ID | geschlossen | `load_catalog_runtime_snapshot()` liest ausschliesslich `store.current_revision_snapshot(context)` |
| Kein Split-Read aus Aktivierungspointer und Revisionseintraegen | geschlossen | Test `test_catalog_runtime_snapshot_uses_one_atomic_active_snapshot_read` |
| Profile lesen Gruppen aus derselben Revision | geschlossen | Snapshot-Projektion validiert Cross-References vor Mapping |
| Gruppenlisten und Kandidaten koennen ueber injizierten Catalog-Provider laufen | geschlossen | `SubgroupService(catalog_provider=...)` |
| Remedy-Auflösung nutzt Catalog-Remedies und `remedy_pathogen`-Relationen derselben Revision | geschlossen | `find_remedies_for_pathogen()` |
| Multiplexe lösen ihre Gruppen-/Remedy-Referenzen produktiv aus dem Snapshot | geschlossen | `resolve_multiplex()` und `find_remedies_for_group()` |
| Fehlende oder invalide aktive Revision scheitert fail-closed | geschlossen | `CatalogRuntimeError`, Codes `active_revision_missing` und `active_revision_invalid` |
| Kein stiller Legacy-Fallback im Catalog-Runtime-Pfad | geschlossen | Fehlerpfad wirft Exception statt Legacy-Auswahl |
| Prozess-Snapshot bleibt revisionsstabil | geschlossen | bestehender Snapshot bleibt auf Revision A, neuer Snapshot sieht Revision B |
| Legacy-Default bleibt unveraendert | geschlossen | `SubgroupService()` ohne Provider nutzt weiterhin `procedural_groups` |

## 4. Implementierungsentscheidung

F8.2 fuehrt die explizite Catalog-Consumption-Schnittstelle ein, schaltet den produktiven Default aber noch nicht um:

- `load_runtime_profiles(..., shadow_mode=False)` bleibt Legacy-default.
- `load_catalog_runtime_snapshot(...)` ist eine explizite fail-closed Catalog-Boundary.
- `SubgroupService` konsumiert Catalogdaten nur, wenn ein Provider injiziert wird.
- Es gibt weiterhin keinen globalen Kill-Switch; dieser folgt in F8.3.
- Es gibt weiterhin keine reale Admin-/Runtime-Gesamtabnahme; diese folgt in F8.4.

## 5. Verifikation

| Pruefung | Ergebnis |
|---|---:|
| RED | `7 failed`; fehlend waren `load_catalog_runtime_snapshot`, `CatalogRuntimeError` und `SubgroupService(catalog_provider=...)` |
| F8.2-Fokustest nach Implementierung | `7 passed in 0.49s` |
| Runtime-/Shadow-/Store-Fokusmatrix | `128 passed in 11.87s` |
| Relevante Admin-/Legacy-/Runtime-/Subgroup-Matrix | `186 passed, 3 skipped in 22.44s` |
| `py_compile` fuer F8.2-Modul, Service und Test | Exitcode 0 |
| Konfliktmarker-Scan fuer F8.2-Dateien | keine Treffer |
| Trailing-Whitespace-Scan `[ \t]+$` fuer F8.2-Dateien | keine Treffer |
| `git diff --check` | Exitcode 0; bekannte LF/CRLF-Warnungen in bestehenden tracked Dateien, neu auch fuer `services/subgroup_service.py` |
| Ruff | nicht verfuegbar: `No module named ruff` |

## 6. Fortschritt nach F8.2

| Modell | Stand |
|---|---:|
| F8 intern | `2/4` = **50 %** |
| Feedback f nach Arbeitseinheiten | `37/39` = **95 %** |
| Feedback f nach Hauptphasen | F1-F7 100 %, F8 50 % = **94 %** |
| Nutzerfeedback gesamt `a-f` | b/c/d/e fertig, f 95 %, a offen = **83 %** |

## 7. Offene Rest-Gates

| Reihenfolge | Gate | Status | Exakter naechster Inhalt |
|---:|---|---|---|
| 1 | F8.3 | offen | Expliziter Kill-Switch ohne stillen Legacy-Fallback bei aktivem Catalog |
| 2 | F8.4 | offen | Reale Admin-/Runtime-Abnahme inklusive Draft, Publish, Activate, Neustart und Rollback |

## 8. Harte Schranken

- Legacy bleibt Default, bis F8.3/F8.4 die Umschaltung explizit abnehmen.
- Bei expliziter Catalog-Consumption gibt es keinen Legacy-Fallback.
- Kein Kill-Switch vor F8.3.
- Keine reale Admin-/Runtime-Freigabe vor F8.4.
- Kein Commit, Staging, Push, Reset oder Cleanup ohne explizite Nutzerfreigabe.

## 9. Naechster verbindlicher Block

**F8.3: Expliziter Kill-Switch.**

Exakt weiter geht es mit einer strikt geparsten Aktivierungsentscheidung fuer `MORPHIC_ADMIN_CATALOG_ENABLED`: deaktiviert muss byte-/verhaltensaehnlich Legacy bleiben; aktiviert muss eine gueltige aktive Catalog-Revision verlangen und bei Fehlern fail-closed abbrechen.
