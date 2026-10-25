# Phase 1 – Architektur, Workflow, Steppings und Algorithmen

## 1.1 Kontrollflächen und Schichten

```text
PowerShell-Launcher / Typer CLI / FastAPI Operator Workbench
                    │
      apps.cli.commands + apps.web Router/Jobs
                    │
 services (Analyse, Harmonisierung, Descriptions)
                    │
core (Profile, Subgroups, NLS, Resonator, Compliance, Hardware)
                    │
providers (Entropy/Hardware) + data (JSON, SQLite, Exporte)
                    │
Reports: JSON / HTML / TXT / PDF / optional 3D
```

| Fläche | Autoritative Implementierung | Iststatus |
|---|---|---|
| CLI | `apps/cli/main.py:39-95` | Typer Root-App: scan, trend, harmonize, descriptions, synergy, field, sources, privacy, analyze, health, ext |
| Web | `apps/web/main.py:244-688` | FastAPI-App, Router, Jobs, Reports, Workbench |
| Browser | `apps/web/static/index.html:25-552`, `app.js:72-602` | 11 sichtbare Operatorphasen, nicht „10“ wie alte Kommentare behaupten |
| Scanjob | `apps/web/scan_jobs.py:218-324` | lokaler Subprozess, stdout/stderr-Protokolle, progress aus Textmarkern |
| Workbench-Store | `apps/web/workbench_runtime.py:26-143` | JSON-Draft/Templates/Run-Traces, atomarer Replace, nur Prozess-Lock |
| Berichte | `tools/reporting_common.py`, `tools/pdf_exporter.py` | Artefaktregister plus JSON/HTML/TXT/PDF, aktuelle PDF-Route ReportLab-basiert |

## 1.2 Web-Workflow – reale 11 Phasen

| # | Phase | Nutzeraktion / technische Wirkung |
|---:|---|---|
| 1 | Runtime & Workspace | Health, Profile, DB-/Quellenstatus laden |
| 2 | Klient / Kontext | Name, Geburtsdaten, Ort, zwei Zustimmungsschalter |
| 3 | Fokus & Zielsetzung | Fokus (Pflicht), Level, Top-N, optionales Hauptsymptom; Snapshot und lokale Fokushistorie |
| 4 | Analyseprofil | Profiltemplate, Entropiemodus, JPEG-Referenzname, adaptive Limits |
| 5 | Hardware & Realtime | Hardware-Truth/Realtime-Kalibrierung, Standard-/Expertmodus |
| 6 | Review & Freigabe | Request-Vorschau; Start erzeugt Job und springt zu Phase 7 (`app.js:184-201`) |
| 7 | Analyse-Lauf | Polling/optional WebSocket; Timeline wird aus CLI-Ausgabemarkern abgeleitet |
| 8 | Ergebnisübersicht | Top-Profile und Resonanzen aus Export-JSON |
| 9 | Technische Details | gespeicherter Run Trace |
| 10 | Berichtskatalog & Export | Tenantbezogener Katalog, Vorschau, Dateiabruf |
| 11 | Harmonisierung & Abschluss | Impuls/Pause/Dauerfaktor/Solfeggio; separater Job |

## 1.3 12-Substep-Manifest

`apps/cli/workflow/substep_manifest.py:25-106` definiert: Init/Entropy, Eingabe/Profil, Klientensignatur, Fokus/Intention, EMF/Modifier, Amplifier, Palette, Matrix-Scoring, Quantum, Post/DB, Export, Harmonisierung. Die Zuordnung zu RadiMorphic ist bewusst **nicht vollständig**: Amplifier, Palette und Harmonisierung haben `None`; candidate_generation, synergy_analysis und morphic_field sind umgekehrt ungemappt. Das ist transparent, aber die UI-Timeline ist derzeit ein semantisches Label-/Mapping, kein direkter Engine-Telemetrievertrag.

**Präzisierung der Ausführung:** Die Workbench startet produktiv `scan top3-scan` (`apps/web/launcher.py:9-17`, `apps/web/main.py:487-520`). Der tatsächlich ausführende, separate 12-Step-Orchestrator ist über `field workflow-scan` erreichbar (`apps/cli/commands/field.py:4395-4454`, `apps/cli/workflow/orchestrator.py:73-107`). Die 12er-Timeline der Workbench darf deshalb nicht als 1:1-Laufzeittelemetrie des Web-Scans verstanden werden; ihr Fortschritt wird aus stdout-Mustern heuristisch abgeleitet.

## 1.4 Algorithmische Kernpfade

| Komponente | Implementierte Formel/Regel | Klassifikation |
|---|---|---|
| Resonator | `q_factor / (1 + q_factor² * detuning²)` mit `gamma=0.12*(1-0.3*h_level)` (`core/resonance/resonator.py:24-48`) | implementiert; Konfiguration/Kalibrierung der Konstanten fehlt |
| NLS v1 | `weight*(0.6*resonance + 0.4*entropy_alignment)` (`core/nls/nls_db.py:36-60`) | implementiert und equivalence-getestet |
| Entropy match | `exp(-0.5*z²)`, `z=(client_entropy-mean)/std` | implementiert, Schutz `std>=1e-6` vorhanden |
| NLS v2 | v1 × Reliability-Faktor `(0.5+0.5*rel)` × optional personal alignment (`:81-136`) | implementiert; v1-Äquivalenz bei Defaults getestet |
| personal alignment | normierte Kosinusähnlichkeit von [-1,1] nach [0,1] | implementiert, Fehlerfallback 1.0 kann Datenprobleme maskieren |
| Seed | SHA-256 über workspace+Klientenbasis, optional zusätzlicher `os.urandom`-Seed (`core/realtime/seed_generator.py:26-88`) | ehrlich: Hardwarequelle ist Kontextlabel, nicht kryptographische Seed-Quelle |
| Client Modifier | Alter/Geschlecht/BMI/Stress/Schlaf/EMF in `core/client_profile.py:116-183` | **berechnet, aktive E2E-Einbindung vor weiterer Datenerfassung zwingend nachweisen** |

## 1.5 Pipeline und Nebenwirkungen

`apps.web.main` baut aus dem Pydantic-Request eine CLI-Commandline, `LocalScanJobService` startet sie mit `shell=False` und festem `sys.executable`. Nach Exports lesen `/results` und der ReportCatalog Artefakte wieder ein. Positiv: keine Shell-Interpolation bei Scanstarts. Risiko: Jobs leben nur im RAM (`_jobs`), sind nach Serverrestart nicht rekonstruierbar; Fortschritt hängt an deutschsprachigen/fragilen stdout-Markern (`scan_jobs.py:29-151`).

**Harmonisierung – implementiert versus UI-Semantik:** Der Worker persistiert Pulse/Pause/Solfeggio-Parameter, aber der Audit-Callgraph zeigt keine echte Puls-/Pausen-State-Machine: `total_cycles` wird laufzeitlich sekundenbasiert überschrieben und die Schleife taktet in Ein-Sekunden-Schritten (`services/harmonization_worker.py:376-381,401-448,495-545`). Der UI-Eindruck eines konfigurierbaren Impuls/Pause-Zyklus ist daher gegenwärtig nicht als tatsächliche Parameterwirkung nachgewiesen.

## 1.6 Daten-/Persistenzstatus

Runtime-Manifeste nutzen vier JSON-Dateien (clients, sessions, artifacts, audit). Workbench nutzt weitere JSON-Dateien. Die Persistenz schreibt atomar via temporärer Datei+replace (`runtime_manifest.py:74-79`), bietet aber keine DB-Transaktion, keine Verschlüsselung und keine Prozess-/Mehrinstanzen-Synchronisation. Exportpfade tragen seit `713b66a` einen `__tenant_id`-Suffix nur bei impliziten Roots; explizite Nutzerpfade bleiben absichtlich unisoliert.
