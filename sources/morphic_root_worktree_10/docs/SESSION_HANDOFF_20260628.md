# Session-Handoff 2026-06-28

## Direkt verwendbarer Wortlaut fuer die neue Session

Bitte arbeite im Projekt `C:\Morphic_v1` exakt an dem zuletzt erreichten Stand weiter.

Kontext: Das Projekt Morphic Engine V1 wurde stabilisiert. Die Python-Umgebung laeuft ueber `.venv\Scripts\python.exe`. Der urspruengliche Fehler `ModuleNotFoundError: No module named 'typer'` ist behoben. Der PowerShell-Launcher nutzt die virtuelle Umgebung und fuehrt einen Health-Preflight aus.

Der aktuelle verifizierte Stand ist:

- Komplette Testsuite: `.\.venv\Scripts\python.exe -m pytest -q` ergibt `117 passed`.
- Health: `.\.venv\Scripts\python.exe -m apps.cli.main health --strict` ergibt `Status: OK`.
- `data\resonance.db` ist als optionale leere Datenbank health-seitig erlaubt und erzeugt keine Warnung mehr.
- Source Registry: `.\.venv\Scripts\python.exe -m apps.cli.main sources validate` ergibt `Registry gueltig ... (18 Quellen)`.
- Shadow Copy existiert unter `C:\Morphic_v1\_backups\Shadow_Copy_20260628_091517`.

Bereits umgesetzt:

- `Run-MultiplexScan.ps1` bietet wieder Top-3, Top-5, Top-7 und Top-9 im Auto-Scan an.
- Der Launcher uebergibt nicht mehr hart `--top-n 5`, sondern den gewaehlten Wert.
- Der Launcher fuehrt vor dem Menue `health --strict` und `sources validate` aus und laedt die Einzelprofil-Liste dynamisch aus `core.profile_sync.get_all_profiles()`.
- Top-N-Archivstruktur ist repariert: `TOP3_SESSION`, `TOP7_SESSION`, `TOP9_SESSION` mit Profil-Unterordnern.
- `field multiplex-scan` reicht `filename_suffix`, `scan_type` und `session_id` korrekt an die Exportpfadlogik weiter.
- Source Registry MVP ist vorhanden:
  - `core/source_registry.py`
  - `config/source_repositories.json`
  - `apps/cli/commands/sources.py`
  - Registrierung in `apps/cli/main.py`
- Quellen koennen per CLI gelistet, validiert, aktiviert/deaktiviert und per Admin-Manifest importiert werden.
- Source-Manifest-Imports haben jetzt `sources stage`, `sources import --dry-run`, Diff-Ausgabe und Rollback-Snapshots pro Batch (`--rollback-dir`, `--batch-id`, `sources rollback`).
- Source-Datenbatches koennen jetzt separat validiert und staged werden: `sources data-stage <batch.json> --staging-dir <dir>`, danach `sources data-promote <staged.json> --ledger <ledger.json> [--dry-run]`.
- Die Source-Datenpromotion prueft bekannte Quellen, Datentyp, Records, Hash und Record-Count und schreibt echte Promotions in ein append-only Ledger.
- Harmonization-Commands sind verdrahtet: `harmonize harmonize`, `harmonize-status` und `harmonize-stop` delegieren auf `services.harmonization_worker`; der Worker respektiert `status: stopped` aus der Jobdatei und ueberschreibt ihn nicht mehr mit `completed`.
- Rife/Clark sind absichtlich `quarantined` und `disabled`; Aktivierung nur mit `--allow-quarantined`.
- Der Haupt-Multiplex-HTML-Report wurde vom Minimal-HTML wieder in Richtung altes Muster gebracht: Header, Metriken, Fokus, Resonanzwerte, gruppierte Subgruppen, Quantum-Synergy, Remedy-Synergien, Badges und Print-CSS.
- Feldtest-/Multiplex-Ausgaben und HTML/TXT-Exports werden auf typische mojibake-Artefakte bereinigt; neuer Smoke-Test deckt stdout und Reporttexte ab.
- Der statische 3D-Viewer und der generierte 3D-HTML-Viewer sind offlinefaehig und enthalten keine externen CDN-Script-Abhaengigkeiten mehr.
- Description-Service ist als kanonischer Lesepfad konsolidiert: `items`, `descriptions` und `item_descriptions` werden als Fallbacks gelesen; Status meldet `available_descriptions`.
- Der stark dirty Worktree ist in `docs/WORKTREE_INVENTORY_20260629.md` nicht-destruktiv dokumentiert.
- Referenz fuer alte Berichte: `D:\Testpatienten Berichte\Mustermann\*.*`.

Wichtige zuletzt geaenderte oder neue Dateien:

- `Run-MultiplexScan.ps1`
- `apps/cli/main.py`
- `apps/cli/commands/field.py`
- `apps/cli/commands/harmonize.py`
- `apps/cli/commands/sources.py`
- `apps/cli/commands/helpers/utility_helpers.py`
- `apps/cli/commands/helpers/harmonization_helpers.py`
- `apps/viewer/index.html`
- `core/source_data_promotion.py`
- `core/source_registry.py`
- `core/viewer_3d.py`
- `services/harmonization_worker.py`
- `config/source_repositories.json`
- `docs/QUELLEN_REGISTRY_BEWERTUNG_20260628.md`
- `docs/STABILIZATION_TEST_MATRIX.md`
- `docs/WORKTREE_INVENTORY_20260629.md`
- `tests/test_launcher_topn.py`
- `tests/test_harmonization_worker_stop.py`
- `tests/test_topn_export_paths.py`
- `tests/test_source_registry.py`
- `tests/test_source_registry_cli.py`
- `tests/test_source_data_promotion.py`
- `tests/test_viewer_offline.py`
- `tests/test_report_text_cleanliness.py`
- `tests/test_report_renderer_legacy_layout.py`
- `tests/test_top5_workflow_smoke.py`

Bitte beachte:

- Die Worktree ist stark dirty; viele geloeschte oder geaenderte Dateien sind vorbestehend. Nicht revertieren, nicht aufraeumen, sofern es fuer die Aufgabe nicht zwingend noetig ist.
- Nutze `rg` fuer Suchen.
- Nutze `apply_patch` fuer manuelle Datei-Edits.
- Vor Codeaenderungen testgetrieben arbeiten: erst fokussierten Test schreiben, roten Lauf sehen, dann implementieren.
- Vor Abschluss verifizieren; keine Erfolgsbehauptung ohne konkrete Befehle.

Naechste empfohlene Prioritaeten:

1. Berichtswesen weiter angleichen:
   - Alten Referenzordner `D:\Testpatienten Berichte\Mustermann\*.*` weiter auswerten.
   - Nicht nur Haupt-Multiplex-Report, sondern auch Deutung, Trend, Synergy und Remedy funktional/layoutseitig angleichen.
   - Besonders `tools/interpretation_generator.py`, `tools/trend_analyzer.py`, `tools/synergy_consolidator.py`, `tools/remedy_reporter.py`, `tools/pdf_exporter.py` pruefen.

2. Source Registry ausbauen:
   - Source-Manifest-Staging, Dry-Run/Diff und Rollback pro Import-Batch sind umgesetzt.
   - Lokale fachliche Datenpromotion fuer konkrete JSON-Batches ist umgesetzt.
   - Offen bleiben konkrete fachliche Mapping-Regeln pro Quelle und danach einzelne Onlineadapter, priorisiert: NLM MeSH, USDA FoodData Central, NCBI Taxonomy.

3. Report-/Archivstruktur konsolidieren:
   - Alte Zielstruktur aus Referenz:
     - `..._Resonanz\YYYYMMDD_HHMMSS_TOP9_SESSION\01_profil\...`
     - `..._Deutung\...`
     - `..._Remedies\...`
     - `..._Synergy\...`
     - `..._Trends\...`
   - Aktuelle Tools schreiben teils noch in vereinfachte Startordner. Bitte pruefen und schrittweise harmonisieren.

4. Optional danach:
   - `resonance.db`: fachlich entscheiden, ob sie spaeter befuellt wird; health-seitig ist sie als optionale leere DB akzeptiert.
   - Visuelle HTML-Regression ueber erzeugten Top-9-Beispielreport gegen Referenz pruefen.

Start bitte mit einer kurzen Bestandspruefung:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m apps.cli.main health --strict
.\.venv\Scripts\python.exe -m apps.cli.main sources validate
```

Danach bitte nach Prioritaet 1 mit dem Berichtswesen weiterarbeiten.
