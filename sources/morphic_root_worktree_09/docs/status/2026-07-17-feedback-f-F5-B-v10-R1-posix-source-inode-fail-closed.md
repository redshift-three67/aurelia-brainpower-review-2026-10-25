# Feedback f / F5-B v10 / R1: POSIX source-inode-bound Fail-Closed

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **R1 technisch geschlossen; Freeze v10 superseded; naechster Block Freeze v11**

## 1. Kurzfazit

R1 schliesst das konsolidierte P1 aus den zwei v10-Reviews konservativ: POSIX-
`dir_fd` allein wird nicht mehr als sichere source-inode-gebundene Publish-
Semantik akzeptiert. `_replace_in_guard()` und `_link_in_guard()` brechen auf
POSIX jetzt nach Same-Parent-/`dir_fd`-Vorpruefung, aber vor jeder Target-Mutation,
mit `SourceRegistryError` ab.

Windows bleibt unveraendert auf dem handle-gebundenen Publish-Pfad.

## 2. Geaenderte Dateien

| Datei | Aenderung |
|---|---|
| `core/source_registry.py` | neuer Fail-Closed-Check `_require_posix_source_inode_bound_publish()`; POSIX `replace/link` mutieren nicht mehr ohne source-inode-bound Support |
| `tests/test_source_registry_atomicity.py` | neuer RED/GREEN-Test fuer POSIX mit vorhandenem `dir_fd`-Support und simulierter mutierender Publish-Funktion |

## 3. TDD-Nachweis

| Schritt | Ergebnis | Bewertung |
|---|---:|---|
| RED erster Testaufbau | `2 failed` mit Windows/`pathlib`-Simulationsproblem | Testaufbau korrigiert, kein Produktivcode geaendert |
| RED final | `2 failed` mit `DID NOT RAISE SourceRegistryError` | belegt fehlendes Fail-Closed vor Publish |
| GREEN | `2 passed in 0.72s` | neuer Vertrag erfuellt |

## 4. Verifikation

| Matrix | Ergebnis |
|---|---:|
| Neuer POSIX-Fail-Closed-Test | `2 passed in 0.72s` |
| `py_compile` fuer geaenderte/betroffene Module | Exitcode 0 |
| `ruff check core/source_registry.py tests/test_source_registry_atomicity.py` | Exitcode 0 |
| Source-Registry-Atomicity | `33 passed in 0.78s` |
| Source Registry / Atomicity / CLI / Promotion / Draft | `129 passed in 6.46s` |
| Admin Backup / v7 Backupmigration / F5B Findings | `104 passed, 1 skipped in 11.36s` |
| Stage-Key-Fokus | `3 passed in 0.24s` |
| Admin-Catalog breit | `452 passed, 6 skipped in 37.74s` |
| Source Registry / Atomicity / Promotion / Draft / CLI / Policy | `221 passed, 1 skipped in 13.25s` |
| Web / Workbench / WebUI Launcher seriell mit eindeutigem Basetemp | `153 passed in 4.36s` |
| Vollsuite ohne Top-5 mit eindeutigem Basetemp | `1078 passed, 8 skipped in 73.40s` |
| Top-5-Smoke mit eindeutigem Basetemp | `1 passed in 99.50s` |
| `git diff --check` | Exitcode 0; bekannte LF/CRLF-Warnungen im bestehenden tracked Diff |

Der erste parallele Web-Matrix-Lauf war ungueltig: Mehrere parallele Pytest-
Prozesse kollidierten auf dem Windows-Temp-/Pytest-Root und erzeugten
`PermissionError` bei `pytest-of-Hubert111`. Der serielle Wiederholungslauf mit
eindeutigem `%TEMP%`-Basetemp war gruen.

## 5. Technischer Vertrag nach R1

| Plattform / Bedingung | Verhalten |
|---|---|
| Windows | handle-gebundener Temp-Publish bleibt supported |
| POSIX ohne `dir_fd`-Support | fail-closed vor Publish |
| POSIX mit `dir_fd`, aber ohne source-inode-bound Publish | fail-closed vor `replace/link` |
| Cross-parent Source oder Target | fail-closed |

## 6. Auswirkung auf Freeze v10

Freeze v10 ist durch die Code- und Testaenderung superseded. Die v10-Reviews
bleiben als vollstaendige Evidenz erhalten, sind aber nicht mehr Abschlussbasis.

## 7. Exakt hier weiter

Naechster Block: **Freeze v11 mit aktualisiertem Scope und SHA-256-
Rueckverifikation**, danach erneut zwei technische read-only Reviews.
