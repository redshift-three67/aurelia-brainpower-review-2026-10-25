# Radi144 Phase 4 – PowerShell-Runtime-Metadatenstatus

Stand: 2026-06-08 00:04 CEST
Projektwurzel: `/home/klaus999/projects/Radi144`
Verifizierter Commit der Umsetzung: `4e280ac feat: add PowerShell runtime metadata adapter`

## 1. Kurzstatus

Phase 4 des Architekturplans ist jetzt adapterartig und minimal-invasiv umgesetzt.

`generate_matrix.ps1` liest die Template-Historie bevorzugt aus der gemeinsamen Runtime-Verwaltungsdomäne unter `data/runtime/`. Wenn dort noch keine Runtime-Session-Metadaten vorhanden sind oder der Export nicht möglich ist, bleibt der alte lokale Fallback über `data/session_templates.json` erhalten.

Damit ist die zuvor implizite PowerShell-/Python-Zustandsteilung nicht vollständig migriert, aber stabiler entkoppelt:

- Python/CLI/API schreiben weiterhin die gemeinsame Verwaltungsdomäne.
- PowerShell konsumiert daraus eine generierte legacy-kompatible Template-Ansicht.
- Der vorhandene Windows-Workflow bleibt erhalten.
- Die alte Template-Datei bleibt als Fallback unterstützt.

## 2. Technische Umsetzung

### 2.1 Neuer Exportadapter

Datei: `app/services/session_archive_service.py`

Neue öffentliche Funktion:

- `export_powershell_templates_from_runtime_dir(runtime_dir, output_path=None, max_templates=21) -> Path`

Aufgabe:

1. liest `data/runtime/sessions.json`
2. löst vorhandene `client_id` gegen `data/runtime/clients.json` auf
3. erzeugt daraus eine PowerShell-kompatible Template-Struktur
4. schreibt standardmäßig `data/runtime/powershell_templates.json`

Die erzeugte Datei ist Runtime-/Scratch-Zustand und bleibt über `.gitignore` geschützt.

### 2.2 PowerShell-Anbindung

Datei: `generate_matrix.ps1`

Aktueller Ablauf im Template-Bereich:

1. prüft `data/runtime/sessions.json`
2. setzt temporär `RADI144_RUNTIME_DIR`
3. ruft den Python-Adapter `export_powershell_templates_from_runtime_dir(...)` auf
4. nutzt bei erfolgreichem Export `data/runtime/powershell_templates.json`
5. fällt sonst auf `data/session_templates.json` zurück

Wichtig:

- keine PowerShell-Komplettmigration
- keine Änderung der Hauptbedienlogik
- keine Änderung der Marker-Ausgabe zu `dev_cli.py`
- keine Änderung an Analyse-, Harmonizer-, Audio-, DB- oder EMF-Parametern

### 2.3 Git-/Datenhygiene

Ergänzt und testgesichert:

- `temp_group.json` bleibt ignored
- `_temp_db_list.txt` bleibt ignored
- `data/runtime/powershell_templates.json` bleibt durch `data/runtime/` ignored

## 3. Nicht verändert

Explizit nicht verändert wurden:

- `app/algorithms/resonance_engine.py`
- Resonanzscore
- Matrixgenerierung
- Top-10-/Top-3-Selektion
- DB-Ranking
- EMF-Kompensationsalgorithmus
- Audio-Synthese
- Harmonizer-Timing
- Report-Renderer-Zusammenlegung
- API-Routenverträge
- CLI-Argumentverträge

## 4. Verifikation

Verifiziert nach Umsetzung:

- fokussierter Adaptertest: `3 passed`
- kombinierte Archiv-/API-/Hygiene-Regression: `15 passed`
- komplette Testsuite: `44 passed in 1.60s`
- Ruff für betroffene Python-Dateien: `All checks passed`
- Python-Kompilierung für betroffene Python-Einstiege: erfolgreich
- Gitstatus nach Commit: sauber

Auf diesem Linux-Host nicht verifizierbar:

- echter PowerShell-Parser-/Live-Test mit `pwsh` oder Windows PowerShell, weil kein PowerShell-Binary verfügbar war

Empfohlene spätere Zusatzverifikation auf Windows oder einem Host mit `pwsh`:

```powershell
pwsh -NoProfile -File .\generate_matrix.ps1
```

oder mindestens ein Parser-/Syntaxlauf ohne fachliche Eingabe, sofern die Umgebung dies zulässt.

## 5. Aktuelle Architekturwahrheit

Die Verwaltungsdomäne ist aktuell so zu verstehen:

- `data/runtime/clients.json`: gemeinsame Klienten-Registry
- `data/runtime/sessions.json`: gemeinsames Analyse-/Session-Archiv
- `data/runtime/artifacts.json`: Report-/Artefaktmanifest
- `data/runtime/powershell_templates.json`: generierte, legacy-kompatible Leseansicht für PowerShell

`data/session_templates.json` ist dadurch noch nicht obsolet. Es bleibt ein kompatibler Fallback für ältere lokale Workflows oder Umgebungen ohne Runtime-Metadaten.

## 6. Stabilitätsbewertung

Risiko der Änderung: niedrig

Begründung:

- additive Adapterfunktion statt Migration
- bestehende PowerShell-Dateiform bleibt erhalten
- Fallback bleibt aktiv
- Core-/Algorithmusflächen wurden nicht berührt
- Runtime-/Scratch-Dateien bleiben ignored
- automatische Tests sichern den Adaptervertrag und die Ignore-Grenzen

## 7. Nachtrag: weitere Phase-4-Haertung am 2026-06-08

Nach dem Dokumentationsabgleich wurde `generate_matrix.ps1` zusaetzlich minimal-invasiv gegen Python-Runtime-Drift gehaertet.

Neue Python-Erkennungsreihenfolge:

1. `.venv\Scripts\python.exe`
2. `.venv\bin\python`
3. `python`
4. `py`

Alle bisherigen Python-Aufrufe im PowerShell-Workflow verwenden danach denselben aufgeloesten Interpreter:

- Dependency-Check
- `torch`-/`reportlab`-Preflight
- Runtime-Metadatenadapter fuer `powershell_templates.json`
- DB-Ranking-Prescan
- DB-Scan
- GPU-/VRAM-Erkennung fuer 36x36
- finaler `dev_cli.py`-Aufruf

Auch diese Haertung veraendert keine Kernengine, keine Algorithmen, keine CLI-Argumente und keine API-Routen. Sie reduziert nur das Risiko, dass PowerShell versehentlich einen globalen Python-Interpreter statt der Projekt-`.venv` verwendet.

## 8. Empfohlene nächste technische Schritte

1. Windows-/PowerShell-Live-Verifikation nachholen, sobald ein geeigneter Host verfügbar ist.
2. Danach nur bei Bedarf weitere Phase-4-Schritte durchführen:
   - optional klarerer Template-Quellenhinweis in der interaktiven UI
   - keine Renderer- oder Core-Zusammenlegung ohne separate Freigabe
3. Dokumentation und README regelmäßig gegen den echten Teststand synchron halten.
