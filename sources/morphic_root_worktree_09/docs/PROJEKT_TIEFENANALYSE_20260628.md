# Morphic Engine V1 - Codebasierte Tiefenanalyse

**Stand:** 2026-06-28  
**Projektpfad:** `C:\Morphic_v1`  
**Analyseziel:** Struktur, Workflow, Steppings/Substeppings, Reporting/Archivierung, Datenbankverwaltung, Profile/Multiplexe/Remedies, UI/UX, Benutzerführung, Lücken, Problematiken und Empfehlungen.  
**Wichtiger Scope-Hinweis:** Diese Analyse bewertet Code, Architektur, Bedienbarkeit und technische Risiken. Sie bewertet keine medizinische, therapeutische oder diagnostische Wirksamkeit.

**Status-Update 2026-06-29:** Die P0-Startprobleme aus dieser Analyse sind weitgehend stabilisiert: `.venv` ist der aktive Test-/CLI-Interpreter, `apps.cli.main --help` lädt, `scan top3-scan` und `field multiplex-scan` sind die kanonischen Pfade, `top3-scan` ist nur einmal registriert, der `scan multiplex-scan`-Wrapper delegiert an `field multiplex-scan`, und die Report-/Manifest-Pfade fuer PDF, Trend, Synergy, Remedy, Field-Test und 3D-Export sind testgedeckt. `resonance.db` ist health-seitig als optionale leere DB erlaubt. Der kanonische Description-Service liest `items`, `descriptions` und `item_descriptions` als Fallbacks. Der PowerShell-Launcher nutzt strikten Preflight und laedt Profile aus `core.profile_sync`; Source-Manifest-Importe haben Staging, Dry-Run/Diff und Rollback-Snapshots. Lokale Source-Datenpromotion ist ueber Staging, Dry-Run und append-only Ledger abgesichert. Der 3D-Viewer ist offlinefaehig, und Feldtest-/Multiplex-Reports werden auf sichtbare Encoding-Artefakte geprueft. Offene technische Punkte bleiben u.a. fachliche DB-/Description-Migrationen, konkrete Onlineadapter/Mapping-Regeln und der stark verschmutzte Git-Working-Tree.

---

## 1. Historisches Kurzfazit vom 2026-06-28

| Bereich | Befund | Schwere | Begründung / Codebezug |
|---|---:|---:|---|
| Laufzeitumgebung | Der gemeldete Fehler `ModuleNotFoundError: No module named 'typer'` ist reproduziert. `python` zeigt auf `C:\Users\Hubert111\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`, nicht auf eine Projektumgebung. | P0 | `Run-MultiplexScan.ps1:335` setzt `$pythonExe = 'python'`; reproduzierter Lauf mit `python -m apps.cli.main ...` endet bei `apps/cli/main.py:3 import typer`. |
| Projekt-venv | `venv/pyvenv.cfg` ist ein Linux-Artefakt (`home=/usr/bin`, `executable=/usr/bin/python3.11`) und auf Windows nicht ausführbar; `venv/Scripts` und `venv/bin` fehlen lokal. | P0 | Lokaler Befund: `venv\pyvenv.cfg`; `venv\Scripts` und `venv\bin` existieren nicht. |
| Importkette nach Typer | Mit explizitem Python 3.12 sind `typer`, `numpy`, `pytest` vorhanden; dann scheitert `python -m apps.cli.main --help` an `ModuleNotFoundError: No module named 'cli'`. | P0 | `apps/cli/main.py:6` importiert `from cli.utils.backup import log_command`; lokales `cli/` ist gelöscht. |
| Gelöschte Kernpakete | `cli/`, `tools/`, `providers/`, `infra/` sind im Git als gelöscht markiert, werden aber noch importiert. | P0 | `git status --short cli tools providers infra`: alle als `D`; Imports u.a. in `apps/cli/commands/field.py:14`, `apps/cli/commands/scan.py:13`, `Run-MultiplexScan.ps1:456`, `:521`, `:549`, `:586`. |
| CLI-Pfaddrift | PowerShell ruft Root-Commands `top3-scan` und `multiplex-scan` auf; die modulare CLI registriert aber Sub-Apps `scan`, `field`, `trend`, `harmonize`, `descriptions`, `synergy`. | P0 | `apps/cli/main.py:21-26`; `Run-MultiplexScan.ps1:338` und `:385`; tatsächliche `multiplex-scan`-Implementierung liegt unter `field` (`apps/cli/commands/field.py:582`). |
| Migration beschädigt | `apps/cli/main.py` enthält zwei App-Definitionen und zwei `if __name__ == "__main__"`-Blöcke. Beim direkten `-m`-Start wird `app()` bereits früh ausgeführt, bevor Legacy-Definitionen unterhalb geladen werden. | P0 | `apps/cli/main.py:10`, `:58`, `:802`, `:3216`. |
| Helper-Stubs | Mehrere Helper-Dateien sind nur leere Stubs, werden aber aus `apps/cli/commands/helpers/__init__.py` mit konkreten Funktionsnamen importiert. | P0 | `helpers/__init__.py` re-exportiert `_build_db_*`, `_interpret_*`, `_resolve_export_paths`, `_render_basic_html` usw.; `database_helpers.py`, `utility_helpers.py`, `potency_helpers.py`, `interpretation_helpers.py`, `influence_helpers.py`, `harmonization_helpers.py` enthalten diese Funktionen nicht. |
| Tests | Tests sind nicht lauffähig; explizites Python 3.12 bricht bereits in der Collection mit 8 Importfehlern ab. | P0 | `pytest -q`: Fehler u.a. `No module named 'cli'`, `resonance_pipeline`, `entropy_sources`, `nls_db`, `procedural_groups`. |
| Datenbanken | `remedies.db` ist substanziell befüllt; Beschreibungsdaten werden im kanonischen Service aus `items`, `descriptions` und `item_descriptions` gelesen; `resonance.db` ist 0 Byte und health-seitig optional. | P1 | DB-Befund: `remedies.db` 4.079 Remedies, `descriptions.db` 8.228 Items/264 Beschreibungen, `item_descriptions.db` 1 Eintrag, `resonance.db` 0 Byte. Fachliche Migration/Befuellung bleibt offen. |
| UI/UX | Bedienung ist primär PowerShell-interaktiv, lang und pfadabhaengig; der Launcher hat jetzt aber strikten Preflight, Source-Registry-Check und dynamische Profile. | P1 | `Run-MultiplexScan.ps1` enthält weiterhin viele `Read-Host`-Schritte, nutzt aber `.venv`, `health --strict`, `sources validate` und `core.profile_sync`. |

---

## 2. Historisch reproduzierter Fehler und Root-Cause-Kette

### 2.1 Fehlerbild

Korrigierter Top-N-Aufruf fuer denselben Fall:

```powershell
python -m apps.cli.main scan top3-scan Deisenhofer Klaus --birth-date 09041966 --birth-place Augsburg --export C:\Benutzer_Archive_Start --hardware-profile windows --k-total 4096 --top-k 384 --synergy --synergy-combos 4 --synergy-threshold 6.0 --top-n 5 --focus Bronchien
```

Historisch reproduzierter erster Fehler:

```text
File "C:\morphic_v1\apps\cli\main.py", line 3, in <module>
  import typer
ModuleNotFoundError: No module named 'typer'
```

### 2.2 Root-Cause-Analyse

| Schritt | Beobachtung | Technische Ursache | Auswirkung |
|---|---|---|---|
| 1 | `where python` findet zuerst `C:\Users\Hubert111\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`. | PowerShell startet nicht die Projektumgebung und nicht den installierten Python 3.12 zuerst. | `typer`, `numpy`, `pytest` fehlen in diesem Interpreter. |
| 2 | `pyproject.toml` und `requirements.txt` deklarieren `typer[all]`, `numpy`, `pytest`. | Dependencies sind im Projekt definiert, aber nicht in der tatsächlich verwendeten Umgebung aktiv. | Der Fehler ist kein fehlender Eintrag in `requirements.txt`, sondern eine falsche Interpreter-/Venv-Auswahl. |
| 3 | Explizites Python 3.12 findet `typer`, `numpy`, `pytest`. | System-Python 3.12 ist besser ausgestattet. | Der erste Fehler verschiebt sich weiter in die Projektimports. |
| 4 | Mit Python 3.12 scheitert `apps.cli.main` an `No module named 'cli'`. | Lokales Paket `cli/utils/backup.py` ist gelöscht, wird aber noch importiert. | Nach Installation/Aktivierung von Typer ist der nächste Blocker sofort aktiv. |
| 5 | Lokale `tools/` und `providers/` fehlen ebenfalls. | Git-Status markiert diese Pakete als gelöscht; der Code referenziert sie weiter. | Postprocessing, Entropiequellen, GroupManager, Trend/Remedy/PDF/Synergy-Tools sind nicht stabil erreichbar. |
| 6 | `python` aus Hermes resolved `cli`, `tools`, `providers` teilweise aus `C:\Users\Hubert111\AppData\Local\hermes\hermes-agent`. | Namenskonflikt mit externen Agent-Paketen. | Gefährlich: falsche Module können importiert werden, wodurch Fehler verdeckt oder verfälscht werden. |

### 2.3 Minimal korrekte Reihenfolge zur Stabilisierung

| Priorität | Maßnahme | Warum |
|---:|---|---|
| 1 | Projekt-eigene Windows-venv neu erstellen, z.B. `.venv`, und alle Launcher auf deren `python.exe` pinnen. | Behebt `typer`/`numpy`/`pytest` und verhindert Hermes-Namespace-Kollisionen. |
| 2 | Lokale Pakete `cli`, `tools`, `providers` entweder wiederherstellen oder alle Imports/Launcher konsequent auf neue Module migrieren. | Sonst folgen direkt Importfehler nach dem Typer-Fix. |
| 3 | CLI-Command-Struktur vereinheitlichen: entweder Root-Commands wieder registrieren oder PowerShell/Subprozesse auf `scan top3-scan` und `field multiplex-scan` umstellen. | Der aktuelle PowerShell-Aufruf trifft nicht die registrierte CLI-Struktur. |
| 4 | Helper-Stubs füllen oder Reexports entfernen und Imports auf `apps.cli.main`/echte Helper konsolidieren. | Die aktuelle Helper-Schicht ist nicht funktionsfähig. |
| 5 | Tests aktualisieren und als Gate nutzen. | Aktuelle Tests prüfen teils nicht mehr existierende Legacy-Module. |

---

## 3. Projektstruktur

| Pfad | Rolle im Ist-Zustand | Bewertung |
|---|---|---|
| `apps/cli/` | CLI-Einstieg, Subcommands, Profil-Registry, laufende Refactoring-Zone. | Zentral, aber derzeit inkonsistent migriert. |
| `apps/cli/main.py` | Hauptentrypoint plus verbliebene Legacy-Renderer/Helper. | Kritisch: doppelte App-Definition, frühes `app()`, Encoding-Artefakte, Root-Commands entfernt. |
| `apps/cli/commands/` | Neue modulare Command-Dateien (`scan`, `field`, `trend`, `harmonize`, `descriptions`, `synergy`). | Zielstruktur sinnvoll, Umsetzung bricht an Imports, Duplikaten und falschen Delegationen. |
| `apps/cli/commands/helpers/` | Soll ausgelagerte Helper aus `main.py` aufnehmen. | Aktuell überwiegend leere Stubs; Importlayer beschädigt. |
| `core/` | Domänenlogik: Profile, Raten, Resonanz, NLS, Subgruppen, Remedies, Synergy, Reports, 3D, Trend, Sessions. | Inhaltlich breit, aber teils mehrfach parallele Konzepte. |
| `services/` | Orchestrierungsservices: Analyse, NLS, Subgroups, Remedies, Beschreibungen, Harmonisierung. | Sinnvolle Service-Schicht, aber noch mit alten Pfad-/Importannahmen. |
| `data/` | SQLite-DBs, BAT-Gruppen, OOREP SQL, Harmonization Jobs, Cache. | Produktiv relevante Daten vorhanden; DB-Schemata konsolidierungsbedürftig. |
| `docs/` | Architektur-/Planungs-/Statusdokumente. | Umfangreich, aber teilweise historisch und nicht deckungsgleich mit aktuellem Code. |
| `PROJECT_MEMORY/` | Projektzustand, Migrationslog, Shadow-Backups, Snapshots. | Wertvoller Golden Record; beschreibt laufende Phase-3-Migration. |
| `Run-MultiplexScan.ps1` | Praktische Benutzerführung für Single- und Top-5-Scan. | Wichtigste UX-Fläche, aber technisch veraltet gegenüber aktueller CLI-Struktur. |
| `apps/viewer/` | 3D-HTML-Viewer und Z-Anatomy-Bridge. | Eigenständige Zusatz-UI, aber CDN-abhängig und nicht in Hauptworkflow integriert. |
| `apps/server/` | WebSocket-Streaming-Server. | Potenzial für Live-UI, aber derzeit Nebenpfad. |

---

## 4. CLI-Architektur und aktueller Stand

| Ebene | Aktueller Code | Bewertung |
|---|---|---|
| Root-App | `apps/cli/main.py` erstellt eine Typer-App und registriert `scan`, `field`, `trend`, `harmonize`, `descriptions`, `synergy`, `sources`, `privacy`, `analyze`, `health` und `log-check`. | Modulare Zielstruktur ist aktiv. |
| Main-Aufruf | `main()` führt `check_paths()` aus und startet danach `app()`; `__main__` ruft `main()`. | Einstiegspunkt ist eindeutig. |
| Legacy-Exports | `apps/cli/main.py` reexportiert Helper aus `apps.cli.commands.helpers`. | Kompatibilitätsschicht für alte Imports bleibt vorhanden, ohne zweite App-Definition. |
| Top-Scan | `apps/cli/commands/scan.py` registriert `top3-scan` einmal unter `scan`. | Doppelregistrierung/Duplikation wurde bereinigt; `tests/test_cli_contract.py` sichert die einmalige Registrierung. |
| Multiplex-Scan | `apps/cli/commands/field.py` enthält die große Implementierung unter `field multiplex-scan`. | Kanonischer Pfad für den vollständigen Multiplex-Workflow. |
| Scan-Wrapper | `apps/cli/commands/scan.py` definiert `scan multiplex-scan` als Kompatibilitätswrapper. | Delegiert an `field multiplex-scan` und ist per Manifest-Test abgesichert. |
| Top3-Subprozesse | `apps/cli/commands/scan.py` ruft `sys.executable -m apps.cli.main field multiplex-scan`. | Pfad folgt der modularen CLI-Struktur. |
| PowerShell | `Run-MultiplexScan.ps1` ruft `field multiplex-scan` und `scan top3-scan`. | Pfade folgen der modularen CLI-Struktur. |

**Konsequenz:** Die Command-Pfade fuer Single- und Top-N-Workflows sind stabilisiert; verbleibende Risiken liegen eher in Daten-/DB-Konsolidierung, optionalen Tool-Pfaden und fachlicher Gewichtung.

---

## 5. Workflow: Single-Scan und Top-5-Auto-Scan

### 5.1 Benutzer-Workflow im PowerShell-Launcher

| Schritt | Codebereich | Benutzeraktion | Output / Seiteneffekt | Risiko |
|---:|---|---|---|---|
| 1 | `Run-MultiplexScan.ps1` | Strikter Preflight, dann Auswahl Single oder Top-N. | `health --strict`, `sources validate`, `$useTop5Scan`. | Startfehler werden frueh sichtbar; Launcher bleibt interaktiv lang. |
| 2 | `Run-MultiplexScan.ps1` | Profilmenü bei Single-Scan. | Dynamische Liste aus `core.profile_sync.get_all_profiles()`. | Profilanzeige folgt der zentralen Wahrheit. |
| 3 | `:119-162` | Name, Vorname, Geburtsdatum, Ort. | `last_client.json` wird aktualisiert. | Keine Validierung des Datumsformats außer Nichtleer. |
| 4 | `:192-203` | Fokus und Fokusgewichtung. | `--focus`, optional `--no-focus-weighting`. | Top-5 übergibt nur Fokus; kein `--no-focus-weighting` im Top-5-Pfad. |
| 5 | `:205-227` | Planetentyp und Intention. | CLI-Optionen für Single-Scan. | Top-5-Pfad übergibt Planet/Intention nicht an `top3-scan`. |
| 6 | `:230-306` | Personalprofil-Template. | `--p-emotion`, `--p-physisch`, `--p-mental`, `--p-astral` nur Single-Scan. | Top-5-Pfad verliert Personalprofil. |
| 7 | `:309-330` | Entropie-Modus/env vars. | `ME_ENTROPY_MODE`, `ME_NETWORK_ENTROPY_URL`, optional `ME_TRUERNG_PORT`. | Keine Prüfung, ob Provider-Module vorhanden sind. |
| 8 | `:337-370` | Single-Scan-Argumente. | Kanonischer Aufruf `python -m apps.cli.main field multiplex-scan`. | Pfad konsistent zur modularen CLI. |
| 9 | `:384-401` | Top-N-Argumente. | Kanonischer Aufruf `python -m apps.cli.main scan top3-scan`. | Pfad konsistent zur modularen CLI. |
| 10 | `:438-759` | Top-5 Postprocessing. | Deutung, Trend, Synergy, Remedy, PDF, Harmonisierung. | Lokale `tools.*`-Pfade sind wieder vorhanden und fuer Synergy/Remedy/Trend/PDF testgedeckt. |
| 11 | `:772-894` | Single Postprocessing. | Synergy, Remedy, Trend, optionale Deutung. | Weiterhin ein langer PowerShell-Pfad, aber nicht mehr durch fehlende `tools.*`-Module blockiert. |

### 5.2 Multiplex-Scan Engine-Steps

| Engine-Step | Codebereich | Beschreibung | Befund |
|---:|---|---|---|
| 1 | `apps/cli/commands/field.py:826`, `:2626-2640` | Profilgruppen ermitteln und gegen verfügbare Gruppen validieren. | Registry-first ist gut; fehlende Gruppen werden nur gewarnt, nicht hart blockiert. |
| 2 | `:2643-2652` | Kandidaten aus Subgroups generieren. | Benötigt `SubgroupService` und `procedural_groups`; in der Projekt-`.venv` testgedeckt. |
| 3 | `:2701-2758` | Entropie/h-Level bestimmen, optional Hybrid-Entropie. | Lokale Provider-Pfade sind wieder importierbar; externe Entropiequellen bleiben optional/environment-abhängig. |
| 4 | `:2772-2790` | Client-Raten, Entropie und NLS-v2-Scores berechnen. | Domänenlogik ist klar getrennt über `AnalysisService` und `NlsService`. |
| 5 | `:2848-2995` | Klientenmodifikatoren, Quantum-Faktor, Intention und Kohärenz anwenden. | Viele Gewichtungen sind in CLI-Funktion eingebettet, nicht separat testbar. |
| 6 | `:2997-3040` | Konsolenreport mit Top Items. | Ausgabe enthält Encoding-Artefakte in Datei; Windows-Konsole kann weitere Darstellungsprobleme haben. |
| 7 | `:3067-3203` | Quantum-Synergy Analyse. | Nutzt globale Synergy-Datenbank; bei `scan_results=None` bewusst nicht auf Scanraum begrenzt. |
| 8 | `:3207-3583` | Exportdaten bauen: `sub_results`, `quantum_synergy`, Remedy-Synergien, DB-Analyse, morphic field/axes. | Fachlich reichhaltig, aber sehr große Funktion; viele interne Zustände sind schwer isoliert testbar. |
| 9 | `:3586-3952` | JSON, HTML, TXT und Harmonization-Dateien schreiben. | Export nutzt `_resolve_export_paths` und `_atomic_write_text`, aktuell aber aus `apps.cli.main`/Helpern abhängig. |
| 10 | `:3956-3986` | Optionaler 3D-Export. | Nützlich, aber optional und Mapping kann leer sein. |

### 5.3 Top-5/Top3 Scan-Steps

| Phase | Codebereich | Verhalten | Problem |
|---|---|---|---|
| Screening | `apps/cli/commands/scan.py:842-929` | Schleife über `TOP3_ANALYSIS_PROFILES`, ruft pro Profil Multiplex-Scan mit kleinem `k`. | Subprozess nutzt `field multiplex-scan`. |
| Fokusbonus | `scan.py:185-209`, `:931-951` | Profilbonus 25%/15%/10% über Fokus-Mapping. | Nutzertext sagt 25/15/10; Code passt. Signifikanzprüfung markiert nur, sortiert aber nicht neu nach Override. |
| Auswahl | `scan.py:953-965` | `profile_scores` nach `final_score` sortieren, Top-N wählen. | Wenn alle Subprozesse fehlschlagen, bleibt `profile_scores` leer; kein harter Abbruch vor Phase 2 sichtbar. |
| Vollanalyse | `scan.py:975-1000` | Top-Profile werden mit vollem `k_total/top_k` gescannt. | Nutzt ebenfalls `field multiplex-scan`. |
| Konsolidierung | `scan.py:1058-1093` | Importiert `tools.synergy_consolidator` und `tools.remedy_reporter`. | Synergy-/Remedy-Artefakte inklusive PDF/Manifest sind testgedeckt. |

---

## 6. Profile, Multiplexe und Gruppen

| Element | Ist-Zustand | Bewertung |
|---|---|---|
| Zentrale Profilquelle | `core/profile_sync/__init__.py` registriert 35 aktive Profile und 5 Aliase über `_register`. | Gute Richtung: eine Masterquelle. |
| Top-Scan-Profile | `get_top3_analysis_profiles()` gibt alle aktiven Profile zurück (`core/profile_sync/__init__.py:702`). | Der UI-Text "35 Haupt-Profile" ist für Top-5 aktuell korrekt. |
| Profil-Wrapper | `apps/cli/profiles/registry.py` verweist auf `core.profile_sync` und hält Legacy-Fallbacks. | Sinnvoll, aber Fallback erhöht Drift-Risiko. |
| PowerShell-Menü | `Run-MultiplexScan.ps1` laedt Profile aus `core.profile_sync.get_all_profiles()`. | Keine harte Profil-Liste mehr im Launcher; zentrale Profilquelle bestimmt die Anzeige. |
| Dynamic Groups | `core/subgroups/procedural_groups.py:1011-1022` enthält dynamische Remedy-Gruppen. | Starke Erweiterbarkeit, aber abhängig von `remedies.db` und `numpy`. |
| BAT-Gruppen | `core/subgroups/bat_groups.py` lädt JSON aus `data/generated_groups/BAT_Akutprogramme`. | Funktional gut als Datenadapter; Dateinamen enthalten Kodierungsartefakte. |
| Remedy-Erkennung | `core/remedy_group_registry.py:157` klassifiziert explizite Gruppen und Namensheuristik. | Gute Zentralisierung; Kommentar nennt generischen `_multiplex`-Suffix als Vorsicht, Code nutzt am Ende korrekt nur `_remedies_multiplex`. |
| Validierung | `validate_profile_groups()` meldet fehlende Gruppen nur als Liste. | Für produktive Scans sollte Preflight optional hart blockieren, wenn Kern-Gruppen fehlen. |

**Profilstatistik aus Codeimport:**  
`total_profiles=35`, `total_aliases=5`, Kategorien: `basis=5`, `organ=11`, `struktur=5`, `symptom=3`, `toxin=6`, `stoffwechsel=2`, `psyche=1`, `energie=2`, `total_groups=228`.

---

## 7. Datenbankverwaltung

### 7.1 SQLite-Bestand

| Datenbank | Tabellen / Counts | Bewertung |
|---|---:|---|
| `data/remedies.db` | `remedies=4079`, `remedy_keywords=21349`, `remedy_descriptions=298`, `pathogens=1273`, `pathogen_keywords=5359`, `remedy_pathogen_map=4373` | Produktiv relevante DB; größte fachliche Substanz. |
| `data/descriptions.db` | `items=8228`, `descriptions=264`, `sync_status=1`, `groups=0`, `metadata=0`; kanonischer Service meldet `available_descriptions=378`. | Gemischtes Modell bleibt physisch parallel, wird im Lesepfad aber konsolidiert. |
| `data/item_descriptions.db` | `item_descriptions=1` | Kleiner Generator-Cache; wird read-only als Fallback im kanonischen Description-Service genutzt. |
| `data/resonance.db` | 0 Byte, keine Tabellen | Platzhalter/Altartefakt; sollte dokumentiert oder entfernt werden. |

### 7.2 DB-Zugriffsschichten

| Modul | DB | Aufgabe | Befund |
|---|---|---|---|
| `services/remedy_service.py` | `data/remedies.db` | Initialisierung, Remedy-/Pathogen-Stammdaten, Keywords, Mapping, Stats. | Solide, aber initialisiert DB beim Import; in Tests/Tools kann das Seiteneffekte haben. |
| `services/description_service.py` | `data/descriptions.db` plus read-only `data/item_descriptions.db` | Items, Gruppen, Sync-Status, Batch-Beschreibungen; liest `items`, `descriptions` und Generator-Cache als Fallbacks. | Kanonischer Report-Lesepfad. |
| `core/db/descriptions_db.py` | `data/descriptions.db` | Alternative DB-Klasse mit `descriptions` und `metadata`. | Bleibt Schreib-/Importadapter fuer die angereicherte Tabelle. |
| `core/item_description_generator.py` | `data/item_descriptions.db` | LLM-generierte Item-Descriptions mit Cache. | Wird nicht im Reportpfad generierend aufgerufen, sondern nur read-only ueber den Service genutzt. |
| `core/quantum_synergy/database_manager.py` | JSON Cache | Lädt Items aus `_GROUP_LABELS`, speichert Cache in `core/quantum_synergy/cache/items_cache.json`. | Keine DB im SQL-Sinn, aber relevante Persistenz. |
| `services/harmonization_worker.py` | JSON Jobs | Jobstatus in `data/harmonization_jobs/*.json`. | Einfach und nachvollziehbar; Worker prueft die Jobdatei zyklisch auf `stopped` und beendet dann ohne `completed` zurueckzuschreiben. |

### 7.3 DB-Lücken

| Lücke | Wirkung | Empfehlung |
|---|---|---|
| Drei Beschreibungsmodelle (`services.description_service`, `core.db.descriptions_db`, `core.item_description_generator`). | Physisch noch getrennt, aber Report-Lesepfad ist konsolidiert. | Fachliche Migration/Normalisierung spaeter entscheiden; `services.description_service` bleibt der kanonische Lesepfad. |
| `resonance.db` ist leer. | Health-seitig als optionale leere DB akzeptiert; fachliche Befüllung ist noch nicht entschieden. | Bei fachlichem Bedarf Schema/Seeder ergänzen, sonst als optionalen Platzhalter dokumentiert lassen. |
| Remedy-Service initialisiert DB bei Import. | Imports haben Seiteneffekte; schwerer testbar. | Initialisierung explizit über CLI/Setup oder idempotent mit klarer Logging-Kontrolle. |
| Keine Migrationen. | Schemaänderungen sind schwer versionierbar. | Leichtgewichtiges Schema-Versioning in `metadata` oder `PRAGMA user_version`. |

---

## 8. Reporting, Archivwesen und Dateiorganisation

| Bereich | Ist-Zustand | Problem / Risiko |
|---|---|---|
| Exportpfade | `config.yaml` enthält `archive_root`, `synergy_root`, `export_root`, `log_dir`. | Deutung, Trend, PDF und Harmonisierung sind nicht vollständig zentral konfiguriert. |
| Ordnerstruktur | `_resolve_export_paths` baut Klientenordner und bei Top-Sessions Session-/Profilunterordner. | Gute Struktur, aber Funktion liegt in `apps.cli.main` und ist während Migration kritisch abhängig. |
| Exportformate | Multiplex schreibt JSON, HTML, TXT, Harmonization-Labels/Rates, optional 3D JSON. | Breite Abdeckung; keine zentrale Export-Schema-Version außer punktuell. |
| Trendanalyse | `core/trend_analysis.py` sucht rekursiv nach `*_multiplex_scan.json`; `tools.trend_analyzer` nutzt den zentralen Archivfinder. | Top-N-Session-Unterordner werden erfasst. |
| Trenddatenmodell | `core/trend_analysis.py` und `tools.trend_analyzer` lesen `top_items`, `sub_results.top` und `top_scores`. | Legacy- und aktuelle Export-Schemata sind kompatibel. |
| Session-History | `core/session_manager.py` kann `session_history.json` verwalten. | Nicht sichtbar in Hauptworkflow integriert. |
| Harmonization Jobs | `data/harmonization_jobs/*.json`; `stop_harmonization_job()` setzt Status `stopped`, und der Worker respektiert diesen Status im Zyklus. | Kein PID-Kill noetig fuer den Standardpfad; Stop wirkt kooperativ ueber die Jobdatei. |
| PDF/Deutung/Synergy/Remedy Postprocessing | PowerShell ruft `tools.*` auf. | Synergy, Remedy, Trend und PDF sind wieder lauffähig und manifestiert; Deutungs-/UX-Pfade bleiben separat zu prüfen. |

---

## 9. UI/UX und Benutzerführung

| UI-Fläche | Ist-Zustand | UX-Bewertung |
|---|---|---|
| PowerShell Launcher | Wichtigste Oberfläche; führt Schritt für Schritt durch Scanmodus, Klient, Fokus, Intention, Personalprofil, Entropie, Postprocessing, Harmonisierung. | Fuehrt vor Dateneingabe `health --strict` und `sources validate` aus und laedt Profile dynamisch aus `core.profile_sync`; bleibt wegen Laenge und interaktiver Pfade weiter wartungsintensiv. |
| CLI direkt | Typer-CLI mit Sub-Apps. | Gute Zielarchitektur, aber aktuelle Commands und Dokumentation/Launcher stimmen nicht überein. |
| HTML-Report | Renderer in `apps/cli/main.py` erzeugt Tabellen, Sektionen, Synergy, BAT, Remedy, DB-Analyse, morphic axes. | Reichhaltig, aber riesige Renderer-Funktion, Encoding-Artefakte, schwer wartbar. |
| 3D Viewer | `apps/viewer/index.html` Drag-and-drop fuer `*_3d_scan.json`; statischer und generierter Viewer sind selbstenthaltene Canvas-Viewer. | Offline/restricted nutzbar; Integration in Launcher bleibt separater UX-Schritt. |
| WebSocket | `apps/server/websocket_server.py` liefert Live-Events und Abort-Action. | Architekturpotenzial, aber nicht sichtbar in Hauptbedienung; `abort` hängt an StreamManager, nicht am PowerShell-Prozess. |

### Wichtigste UX-Probleme

| Problem | Wirkung | Empfehlung |
|---|---|---|
| Preflight war urspruenglich nicht am Anfang des Launchers. | Dieser Startfehler ist behoben; verbleibend sind UX-Laenge und Pfadkonfiguration. | `health --strict` und `sources validate` bleiben Pflicht-Gates vor Eingaben. |
| Harte Pfade und hartes `python`. | Interpreter-Drift ist behoben; Archiv-/Postprocessing-Zielpfade sind weiter konfigurationswuerdig. | `$pythonExe` wird aus `.venv\Scripts\python.exe` abgeleitet; naechster Schritt waere zentrale Pfadkonfiguration fuer alle Berichtstools. |
| Single und Top-5 haben unterschiedliche Optionsweitergabe. | Top-5 verliert u.a. Personalprofil, Planet, Intention. | Gemeinsames Argumentmodell für Single und Top-5. |
| Profilmenü muss zentraler Masterquelle folgen. | Behoben: der Launcher nutzt die zentrale Profilquelle. | Dynamische Profilanzeige aus `core.profile_sync` beibehalten. |
| Postprocessing hatte mehrere ungesicherte Toolpfade. | Synergy, Remedy, Trend, PDF und Harmonization sind jetzt testgedeckt; Deutungs-/UX-Pfade bleiben separat zu pruefen. | Postprocessing weiter als robuste Pipeline mit Step-Status und Skip-Gruenden ausbauen. |

---

## 10. Test- und Qualitätsstatus

| Test / Prüfung | Ergebnis | Bedeutung |
|---|---|---|
| `.\.venv\Scripts\python.exe -m apps.cli.main --help` | Laedt die Root-CLI. | Kanonischer Interpreter und modulare CLI sind aktiv. |
| `.\.venv\Scripts\python.exe -m pytest -q` | Stabiler Testbestand, zuletzt dreistellig gruen. | Tests sind wieder als Sicherheitsnetz nutzbar. |
| Importgrenzen | Command-Module importieren keine Helper mehr aus `cli.main` oder `apps.cli.main`. | Helper-Migration ist abgesichert. |
| Health/Source-Gates | `health --strict` und `sources validate` laufen vor dem Launcher-Menue. | Startfehler werden frueh sichtbar. |
| Git-Working-Tree | Sehr viele vorbestehende geloeschte/geaenderte/untracked Dateien. | Working-Tree-Konsolidierung bleibt separater, nicht-destruktiver Abschlussblock. |

---

## 11. Empfehlungen nach Priorität

| Prio | Empfehlung | Konkrete Umsetzung |
|---:|---|---|
| P0 | Saubere Projektumgebung herstellen. | `.venv` mit Python 3.12 erstellen, `python -m pip install -e .` oder `pip install -r requirements.txt`; Launcher nur noch `.venv\Scripts\python.exe` nutzen. |
| P0 | Lokale Pakete `cli`, `tools`, `providers` klären. | Entweder aus Git wiederherstellen oder alle Referenzen entfernen/migrieren. Keine Imports dürfen auf Hermes-Agent-Pakete fallen. |
| P0 | CLI-Struktur stabilisieren. | Einen kanonischen Aufruf festlegen, z.B. `python -m apps.cli.main scan top3-scan` und `python -m apps.cli.main field multiplex-scan`; PowerShell und Subprozesse anpassen. |
| P0 | Helper-Migration reparieren. | Funktionen aus `apps/cli/main.py` wirklich in Helperdateien verschieben oder Reexports entfernen; danach Importtests. |
| P0 | Tests aktualisieren. | Legacy-Imports ersetzen; Smoke-Tests für `--help`, Single-Scan `--no-synergy --no-progress`, Top-5 mit kleinem `k_total`. |
| P1 | Reporting-Schema versioniert halten. | Multiplex-, Field-Test-, Analyze-, Trend-, Synergy- und Remedy-JSONs tragen `schema` und `schema_version`; Trend-/Interpretationsadapter lesen Legacy- und aktuelle Top-Item-Felder. |
| P1 | Trendanalyse rekursiv und schema-kompatibel halten. | Tests sichern rekursive Top-N-Session-Suche und Parser für `top_items`, `sub_results.top`, `top_scores`. |
| P1 | DB-Konsolidierung. | Ein Description-System auswählen; `item_descriptions.db` und `descriptions.db` zusammenführen oder klar trennen. |
| P1 | Source-Registry Import-Sicherheit. | Source-Manifeste koennen gestaged, per Dry-Run/Diff geprueft und per Batch-Snapshot zurueckgerollt werden; lokale Source-Datenbatches koennen separat promoted werden; Onlineadapter bleiben separater Ausbauschritt. |
| P1 | PowerShell-Preflight. | Vor Eingaben laufen `health --strict` und `sources validate`; Python-Pfad und lokale Pakete werden dadurch frueh geprueft. |
| P1 | Dynamische Profilanzeige. | Der Launcher generiert die Profil-Liste aus `core.profile_sync.get_all_profiles()` statt aus einer harten PowerShell-Liste. |
| P2 | 3D Viewer offlinefaehig machen. | Erledigt: statischer und generierter Viewer nutzen keine externen Script-CDNs mehr. |
| P2 | Harmonization-Stop korrigieren. | Erledigt: Worker prueft die Jobdatei regelmaessig auf `stopped`; CLI `harmonize-stop` setzt diesen Status ueber den Worker-Service. |
| P2 | Encoding bereinigen. | Dateien auf UTF-8 normalisieren; kaputte Zeichen in CLI/Reports beheben. |

---

## 12. Empfohlener Reparaturplan für den konkreten Top-5-Workflow

| Schritt | Ziel | Akzeptanzkriterium |
|---:|---|---|
| 1 | `.venv`/Interpreter fixen. | `.\.venv\Scripts\python.exe -c "import typer,numpy,pytest"` erfolgreich. |
| 2 | `cli.utils.backup` wieder verfügbar machen oder Imports entfernen. | `.\.venv\Scripts\python.exe -m apps.cli.main --help` kommt bis zur Typer-Hilfe. |
| 3 | `providers.hardware.*` und `tools.*` Entscheidung treffen. | `python -c "import providers.hardware.entropy_sources"` und benötigte `tools.*` funktionieren oder Code nutzt neue Ersatzmodule. |
| 4 | `apps/cli/main.py` entdoppeln. | Genau eine Typer-App, genau ein `if __name__ == "__main__"` am Ende. |
| 5 | `scan.py` entdoppeln. | Genau eine `top3_scan`-Definition, keine Stub-Variante. |
| 6 | Multiplex-Pfad fixen. | Top-5-Subprozess ruft die echte Implementierung auf, z.B. `field multiplex-scan` oder direkte Servicefunktion. |
| 7 | PowerShell aktualisieren. | Angezeigte Argumente stimmen mit CLI-Hilfe überein. |
| 8 | Minimaltest. | `top3-scan` mit `--k-total 32 --top-k 5 --top-n 3 --no-synergy` läuft durch und schreibt JSON/HTML. |
| 9 | Volltest. | Nutzerbeispiel mit `Deisenhofer Klaus ... --focus Bronchien` läuft durch. |
| 10 | Postprocessing testen. | Trend, Deutung, Synergy, Remedy, PDF werden entweder erstellt oder mit klaren Skip-Gründen gemeldet. |

---

## 13. Schlussbewertung

Das Projekt enthält bereits viel fachliche Substanz: zentrale Profildefinitionen, prozedurale Gruppen, BAT-Importe, Remedy-Datenbank, NLS-v2-Scoring, Quantum-Synergy, HTML-/TXT-/PDF-/3D-Exports und ein umfangreiches PowerShell-Bedienkonzept. Die technische Startkette ist stabilisiert und testgedeckt; verbleibende Risiken liegen vor allem in fachlicher Datenmigration, noch nicht angeschlossenen Onlineadaptern, optionalen UI-/3D-Themen und dem stark verschmutzten Working Tree.

Der konkrete Nutzerfehler ist der erste sichtbare Bruch einer längeren Kette:

1. falscher `python` auf Hermes-Agent-venv,
2. kaputtes/ungeeignetes Projekt-`venv`,
3. fehlendes lokales `cli`,
4. fehlendes lokales `tools` und `providers`,
5. CLI-Root/Subcommand-Drift,
6. leere Helper-Stubs,
7. Tests nicht an Migration angepasst.

Die urspruengliche Startkette ist inzwischen von oben nach unten repariert. Weitere Arbeit sollte nicht mehr bei `typer`/Interpreter-Symptomen ansetzen, sondern bei fachlicher Datenpromotion, Onlineadaptern, Report-Feinschliff und kontrollierter Working-Tree-Bereinigung.
