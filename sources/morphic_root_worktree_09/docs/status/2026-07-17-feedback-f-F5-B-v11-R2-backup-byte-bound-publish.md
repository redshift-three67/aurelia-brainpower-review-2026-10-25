# Feedback f / F5-B v11 / R2: Bytegebundener Backup-Publish

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **R2 technisch geschlossen; Freeze v11 superseded; naechster Block Freeze v12**

## 1. Kurzfazit

R2 schliesst das P1 aus REV v11: Backup-Erzeugung bindet die nach
Schema-/Integritaetsvalidierung gemessenen Artefaktbytes jetzt an den
Publish. `_publish_without_overwrite()` kann erwartete Groesse und SHA-256
pruefen, und `create_catalog_backup()` verwendet diese validierten Werte fuer
Datenbank, Manifest und Completion Record.

Damit kann eine same-size Mutation zwischen Validierung und Publish nicht mehr
als autoritativer Backup-Hash manifestiert werden.

## 2. Geaenderte Dateien

| Datei | Aenderung |
|---|---|
| `core/admin_catalog/backup.py` | neue Snapshot-/Erwartungspruefung; Backup-DB, Manifest und Completion werden mit erwarteter Groesse/SHA-256 publiziert; Manifest-/Completion-Hashes stammen aus validierten Temp-Artefakten |
| `tests/test_admin_catalog_backup.py` | neuer RED/GREEN-Test fuer same-size SQLite-Snapshot-Mutation unmittelbar vor Backup-DB-Publish |

## 3. TDD-Nachweis

| Schritt | Ergebnis | Bewertung |
|---|---:|---|
| RED erster Testaufbau | Fehler durch offen gehaltene SQLite-Verbindung | Test korrigiert, Verbindung explizit geschlossen |
| RED final | `1 failed` mit `DID NOT RAISE ValueError` | P1 reproduziert |
| GREEN | `1 passed in 0.21s` | neuer Vertrag erfuellt |

## 4. Verifikation

| Matrix | Ergebnis | Bewertung |
|---|---:|---|
| Neuer R2-Test | `1 passed in 0.21s` | bestanden |
| Backup/Restore-Smoke | `1 passed in 0.23s` | bestanden |
| `py_compile core/admin_catalog/backup.py tests/test_admin_catalog_backup.py` | Exitcode 0 | bestanden |
| `ruff check core/admin_catalog/backup.py tests/test_admin_catalog_backup.py` | Exitcode 0 | bestanden |
| Backup-Testdatei komplett | `34 passed, 1 skipped in 2.83s` | bestanden |
| Admin Backup / v7 Backupmigration / F5B Findings | `105 passed, 1 skipped in 9.73s` | bestanden |
| Admin-Catalog breit | `453 passed, 6 skipped in 30.24s` | bestanden |
| Source Registry / Atomicity / Promotion / Draft / CLI | `164 passed, 1 skipped in 4.86s` | bestanden |
| Vollsuite ohne Top-5 | `1079 passed, 8 skipped in 68.72s` | bestanden |
| Top-5-Smoke | `1 passed in 94.91s` | bestanden |

Ein erster Vollsuite-Lauf mit `--basetemp` unter `codex_tmp`, aber ohne
angepasstes `TEMP/TMP`, war ungueltig: 11 Temp-Sicherheitsvertrags-Tests
erwarteten `tmp_path` unter `tempfile.gettempdir()`. Der Wiederholungslauf mit
`TEMP/TMP=C:\morphic_v1\codex_tmp\os-temp-r2-full` und passendem Basetemp war
gruen.

## 5. Technischer Vertrag nach R2

| Artefakt | Vor R2 | Nach R2 |
|---|---|---|
| temporaere Backup-DB | nach Schema-Pruefung nur Inode/Groesse im Publish verglichen | Groesse und SHA-256 aus validiertem Snapshot vor und nach Publish geprueft |
| `manifest.json` | Hash/Bytes der publizierten DB erneut aus Ziel gelesen | DB-Eintrag aus validiertem Temp-DB-Snapshot abgeleitet |
| `completion.json` | Datenbank-/Manifest-Hash erneut aus Zielartefakten gelesen | Hashes aus validierter Temp-DB und validiertem Temp-Manifest abgeleitet |

## 6. Auswirkung auf Freeze v11

Freeze v11 ist durch R2 superseded. Die v11-Reviews bleiben als Evidenz
erhalten, sind aber keine Abschlussbasis mehr.

## 7. Exakt hier weiter

Naechster Block: **Freeze v12 mit aktualisiertem Scope, SHA-256-Manifest und
Rueckverifikation**, danach erneut zwei technische read-only Reviews.
