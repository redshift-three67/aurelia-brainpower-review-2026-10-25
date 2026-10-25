# Stabilization Test Matrix

Stand: 2026-06-29

Diese Matrix beschreibt die aktuellen Gates, mit denen die lauffaehige
Stabilisierungsbasis des Projekts geprueft wird.

| Gate | Zweck | Kommando | Erwartung |
|---|---|---|---|
| Umgebung | Projekt-venv und Kernmodule pruefen | `.\.venv\Scripts\python.exe -c "import typer, numpy, pytest; print('env ok')"` | Exit 0 |
| CLI Entry | Root-CLI ohne Encoding-Fehler laden | `.\.venv\Scripts\python.exe -m apps.cli.main --help` | Exit 0, Commands `health`, `scan`, `field` sichtbar |
| CLI Struktur | Genau eine Typer-Root-App und ein Entry-Point | `.\.venv\Scripts\python.exe -m pytest tests\test_cli_main_structure.py -q` | Exit 0 |
| Importgrenzen | Command-Module importieren keine Helper mehr aus `cli.main` oder `apps.cli.main` | `.\.venv\Scripts\python.exe -m pytest tests\test_cli_import_boundaries.py -q` | Exit 0 |
| Main-Helper-Delegation | `apps.cli.main` exportiert Legacy-Helper nur noch als Delegation auf `apps.cli.commands.helpers` | `.\.venv\Scripts\python.exe -m pytest tests\test_cli_main_helper_delegation.py -q` | Exit 0 |
| Legacy-Adapter | `cli.main` bleibt als unterstuetzter Kompatibilitaetsadapter erhalten | `.\.venv\Scripts\python.exe -m pytest tests\test_cli_legacy_adapter.py -q` | Exit 0 |
| Health | Runtime, Profile, DBs und Exportpfade pruefen | `.\.venv\Scripts\python.exe -m apps.cli.main health --strict` | Exit 0, 35 Profile, `remedies.db` und `descriptions.db` OK |
| Health JSON | Maschinenlesbare Diagnose | `.\.venv\Scripts\python.exe -m apps.cli.main health --json` | Exit 0, `ok: true` |
| CLI-Vertrag | Subcommands discoverable | `.\.venv\Scripts\python.exe -m pytest tests\test_cli_contract.py -q` | Exit 0 |
| DB-Vertrag | SQLite-Mindestdaten und Tabellen pruefen | `.\.venv\Scripts\python.exe -m pytest tests\test_database_health.py tests\test_cli_health.py -q` | Exit 0 |
| Profil-/Gruppenintegritaet | Alle Profilgruppen und Remedy-Auto-Matcher-Ziele sind im Gruppenkatalog registriert | `.\.venv\Scripts\python.exe -m pytest tests\test_profile_group_integrity.py -q` | Exit 0 |
| Source Registry | Quellenliste, Admin-Import, Dry-Run, Staging und Rollback pruefen | `.\.venv\Scripts\python.exe -m pytest tests\test_source_registry.py tests\test_source_registry_cli.py -q` | `13 passed` |
| Source-Datenpromotion | Lokale Source-Datenbatches validiert stagen, Dry-Run pruefen und append-only Ledger schreiben | `.\.venv\Scripts\python.exe -m pytest tests\test_source_data_promotion.py tests\test_source_registry_cli.py -q` | `10 passed` |
| Offline-3D-Viewer | Statischer und generierter 3D-Viewer enthalten keine CDN-/HTTPS-Script-Abhaengigkeiten | `.\.venv\Scripts\python.exe -m pytest tests\test_viewer_offline.py -q` | `2 passed` |
| Report-Textsauberkeit | Feldtest-/Multiplex-stdout und HTML/TXT-Exports enthalten keine typischen mojibake-Marker | `.\.venv\Scripts\python.exe -m pytest tests\test_report_text_cleanliness.py -q` | `2 passed` |
| PowerShell Launcher | Top-N, strikter Preflight und dynamische Profilanzeige pruefen | `.\.venv\Scripts\python.exe -m pytest tests\test_launcher_topn.py -q` | `4 passed`; PowerShell-Syntax OK |
| Harmonization Worker | Stop-Anforderung ueber Jobdatei und CLI-Delegation pruefen | `.\.venv\Scripts\python.exe -m pytest tests\test_harmonization_worker_stop.py -q` | `2 passed` |
| Top-5 Smoke | Reduzierter Nutzerworkflow mit Fokus | `.\.venv\Scripts\python.exe -m pytest tests\test_top5_workflow_smoke.py -q` | Exit 0, mindestens 3 `*_multiplex_scan.json` |
| Volltest | Aktueller stabiler Testbestand | `.\.venv\Scripts\python.exe -m pytest -q` | `117 passed` |

## Aktueller Health-Befund

| Bereich | Aktueller Wert |
|---|---|
| Python | `C:\morphic_v1\.venv\Scripts\python.exe` |
| Python-Version | `3.12.10` |
| Typer | `0.26.8` |
| NumPy | `2.5.0` |
| Profile | `35` Hauptprofile, keine fehlenden Profilgruppen im aktuellen Gruppenkatalog |
| `descriptions.db` | `items=8228`, `descriptions=264`, `available_descriptions=378` ueber den kanonischen `services.description_service`-Lesepfad |
| `remedies.db` | `remedies=4079`, `remedy_keywords=21349` |
| `item_descriptions.db` | `item_descriptions=1`, read-only Fallback im kanonischen Description-Service |
| `resonance.db` | 0 Byte, als optionale leere DB erlaubt; keine Health-Warnung |

## Hinweise

| Thema | Status |
|---|---|
| PowerShell Launcher | Nutzt jetzt `.\.venv\Scripts\python.exe`, wenn vorhanden, ruft vor dem Menue `python -m apps.cli.main health --strict` sowie `python -m apps.cli.main sources validate` auf und laedt die Einzelprofil-Liste dynamisch aus `core.profile_sync.get_all_profiles()`. |
| Source Registry | Unterstuetzt validiertes Staging (`sources stage`), Dry-Run/Diff (`sources import --dry-run`) und Rollback-Snapshots pro Import-Batch (`--rollback-dir`, `sources rollback`). |
| Source-Datenpromotion | Unterstuetzt lokale Datenbatches ueber `sources data-stage` und `sources data-promote`; Promotions werden ueber Hash, Record-Count und append-only Ledger abgesichert. |
| Offline-3D-Viewer | `apps/viewer/index.html` und `core.viewer_3d.generate_html_viewer` sind selbstenthaltene Canvas-Viewer ohne externe Script-CDNs. |
| Harmonization Jobs | `python -m apps.cli.main harmonize harmonize/status/stop` delegiert auf `services.harmonization_worker`; der Worker prueft die Jobdatei zyklisch auf `stopped` und schreibt danach nicht mehr `completed`. |
| Top-5 Launcher-Ausgabe | Zeigt Profilbasis `core.profile_sync`, Fokus und Gewichtung `+25%/+15%/+10%` vor dem Start an. |
| CLI Entry-Point | `apps/cli/main.py` enthaelt nur noch eine `app = typer.Typer(...)`-Definition und nur noch einen `if __name__ == "__main__"`-Block am Dateiende. |
| Command-Importgrenzen | `apps/cli/commands/field.py` und `apps/cli/commands/scan.py` importieren Report-/Export-Helper direkt aus `apps.cli.commands.helpers`; der Legacy-Adapter `cli.main` wird von Command-Modulen nicht mehr genutzt. |
| Main-Helper-Kopien | `apps/cli/main.py` wurde auf ein duennes Root-Modul reduziert. Private Helper-Namen werden nur noch aus `apps.cli.commands.helpers` delegiert; lokale Kopien wurden entfernt. |
| Encoding | `apps.cli.main` setzt stdout/stderr frueh auf UTF-8; `field` bereinigt sichtbare Feldtest-/Multiplex-Ausgaben und HTML/TXT-Exports von typischen mojibake-Artefakten. |
| Legacy-Adapter | `cli/main.py` bleibt bewusst als unterstuetzter Kompatibilitaetsadapter bestehen. Er exportiert `COMPATIBILITY_STATUS = "supported"` und delegiert auf `apps.cli.commands.helpers`. |
| Worktree-Inventar | `docs/WORKTREE_INVENTORY_20260629.md` dokumentiert den stark dirty Worktree nicht-destruktiv und trennt aktuelle Stabilisierungsaenderungen von vorbestehenden Loesch-/Untracked-Serien. |
