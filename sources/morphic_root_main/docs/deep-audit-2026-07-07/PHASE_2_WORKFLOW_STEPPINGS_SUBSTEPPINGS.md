# PHASE 2 – Projektworkflow, Steppings und Substeppings

## 2.1 Drei reale Workflow-Oberflächen

| Oberfläche | Einstieg | Zweck | Realstatus |
|---|---|---|---|
| CLI Standard | `python -m apps.cli.main ...` | Produktive Analyse-/Scan-/Trend-/Privacy-/Source-/Harmonize-Kommandos | Aktiv; Tests grün. |
| 12-Step Workflow | `apps.cli.workflow.orchestrator.run_workflow(...)` / CLI `field workflow-scan` | Radi144-inspirierter sequenzieller Workflow | Aktiv als eigener Orchestrator; Smoke-Test vorhanden. |
| Web Operator Shell | `uvicorn apps.web.main:app`; UI `/` | Geführter 8-Step-Operator-Wizard mit API-Brücke zum CLI-Pfad | Aktiv; HTTP-Smoke erfolgreich. |

## 2.2 CLI-Workflow – Entry-Point und Delegation

| Step | Codepfad | Beleg | Beschreibung |
|---:|---|---|---|
| 1 | Start | `apps/cli/main.py:86-88` | `main()` ruft `check_paths()` und dann Typer-App. |
| 2 | Command-Router | `apps/cli/main.py:41-50` | Registriert `scan`, `trend`, `harmonize`, `descriptions`, `synergy`, `field`, `sources`, `privacy`, `analyze`, `health`. |
| 3 | Command-Module | `apps/cli/commands/*.py` | Fachliche Ausführung nach Bereich. |
| 4 | Core-/Service-Delegation | z. B. `core/*`, `services/*`, `tools/*` | Scoring, NLS, Quantum, Reports, Harmonisierung, Privacy. |
| 5 | Export/Manifest | `tools/*`, `core/compliance/runtime_manifest.py` | Dateien/Reports/Runtime-Manifest/Auditlog. |

## 2.3 12-Step-Orchestrator – realer Ablauf

`apps/cli/workflow/orchestrator.py:73-89` führt exakt folgende Sequenz aus:

| # | Step-Datei | Funktion | Zeilen | Aufgabe laut Code/Docstring | Substep-Mapping laut `substep_manifest.py` |
|---:|---|---|---:|---|---|
| 1 | `step01_init.py` | `step_01_init` | 40 | Hardware-Erkennung und Entropie-Quelle | `entropy_sampling` |
| 2 | `step02_input.py` | `step_02_input` | 33 | Klientendaten und Parameter sammeln | `profile_resolution` näherungsweise |
| 3 | `step03_signature.py` | `step_03_signature` | 231 | 6-Schicht-Klienten-Signatur | `client_signature` |
| 4 | `step04_focus.py` | `step_04_focus` | 33 | Fokus-Vektor, MD5-Seed, Bio-Matching | `intention_weighting` |
| 5 | `step05_emf.py` | `step_05_emf` | 63 | EMF-Kompensation, 4-Layer | `client_modifiers` |
| 6 | `step06_amplifier.py` | `step_06_amplifier` | 200 | 12D-Vektor, Cosinus-Match, Top-3 | Kein ehrliches RadiMorphic-Äquivalent |
| 7 | `step07_palette.py` | `step_07_palette` | 67 | Farbpalette, unified coherent Fusion | Kein ehrliches Substep-Äquivalent |
| 8 | `step08_matrix.py` | `step_08_matrix` | 59 | Matrix-Suche via `NlsService` | `multiplex_scoring` |
| 9 | `step09_quantum.py` | `step_09_quantum` | 66 | Quantum-Synergy via `QuantumSynergyEngine` | `quantum_modulation` |
| 10 | `step10_post.py` | `step_10_post` | 53 | Level-Info, De-Dup, Normalisierung | `db_analysis` |
| 11 | `step11_export.py` | `step_11_export` | 154 | Export in 5 Formaten + workflow_stepping.html | `export` |
| 12 | `step12_harmonize.py` | `step_12_harmonize` | 77 | Harmonisierung, Puls/Pause-Zyklus | Kein Substep-Äquivalent; eigener Job-Flow |

## 2.4 Substep-Manifest – Ehrlichkeitsprinzip

| Manifest-Element | Beleg | Bewertung |
|---|---|---|
| Es wird nicht alles erzwungen gemappt | `apps/cli/workflow/substep_manifest.py:8-10` | Positiv: keine Vortäuschung von 1:1-Äquivalenz. |
| Unmapped RadiMorphic-Substeps | `candidate_generation`, `synergy_analysis`, `morphic_field` in `apps/cli/workflow/substep_manifest.py:100-106` | Wichtige Lücke/Abgrenzung für spätere Roadmap. |
| Mapping abrufbar | `get_radimorphic_equivalent(...)` in `apps/cli/workflow/substep_manifest.py:109-118` | Testbar und explizit. |

## 2.5 WorkflowState – zentrale Datenstruktur

| Bereich | Felder | Beleg | Status |
|---|---|---|---|
| Init | `hardware_report`, `h_level`, `entropy_source_name` | `apps/cli/workflow/state.py:18-22` | Hardware-/Entropy-Ausgang. |
| Eingabe | Name, Vorname, Geburtsdaten, Fokus, Intention, Profile Level, Top-N, Image, Planet | `state.py:23-40` | Vollständige Klienten-/Workflowparameter. |
| Signatur | `client_rates`, `client_frequency`, `signature_components`, `emf_corrected_frequency` | `state.py:42-46` | Algorithmenübergabe. |
| Fokus/EMF | `focus_vector`, `focus_multiplier`, `composite_emf_index`, `compensation_vector`, `counter_frequencies` | `state.py:48-55` | Radi144-artige Korrektur-/Fokusdaten. |
| Amplifier/Palette/Matrix/Quantum | Empfehlungen, Palette, Matrix Results, Quantum Synergies | `state.py:57-70` | Schrittweise Ergebnisakkumulation. |
| Export/Harmonisierung | `export_paths`, `harmonization_active`, `harmonization_job_id` | `state.py:77-82` | Artefakte und Abschluss. |
| Metadaten | `session_id`, `errors`, `step_completed` | `state.py:84-98` | Minimaler Fortschritts-/Fehlerzustand. |

## 2.6 Web-Operator-Wizard – UI-Steps

Die Web-Shell bildet im Frontend 8 Bedien-Steps ab (`apps/web/static/index.html:22-31`, `apps/web/static/app.js:4-13`):

| UI-Step | Code-Beleg | Substeps im HTML | Backend-Verbindung |
|---:|---|---|---|
| 1 Preflight | `index.html:45-79` | Laufzeit/DB prüfen, Phase-1-Bereitschaft, Datenquellenstatus | GET `/api/health`, GET `/api/sources` in `app.js:316-369` |
| 2 Hinweise | `index.html:81-103` | Wellbeing-Hinweis, lokale Verarbeitung, Erwartung setzen | Consent-Flags `consent_local`, `consent_safety` in `contracts.py:22-23`, Validator `97-102` |
| 3 Klientenaufnahme | `index.html:105-132` | Personendaten, Geburtskontext, optional Bild | POST Payload in `app.js:794-811` |
| 4 Fokus | `index.html:135-169` | Fokus/Symptom, Top-N, Fokuspriorisierung | `focus`, `profile_level`, `top_n` an API |
| 5 Scan-Profil | `index.html:171-211` | Profilvorlage, Entropie-Modus, Adaptive Limits | Pydantic-Validatoren `contracts.py:30-87` |
| 6 Analysefreigabe | `index.html:213-262` | Preview, finale Prüfung, Start/Status | `/api/scan/preview`, `/api/scan/jobs`, Polling in `app.js:814-925` |
| 7 Berichte | `index.html:264-294` | Berichtskatalog, Vorschau, Datei öffnen | `/api/reports`, `/api/reports/{id}/preview/file` |
| 8 Harmonisierung | `index.html:296-397` | Bericht bestätigen, Parameter/Hardware, Start/Refresh/Stop | `/api/harmonization/jobs` in `app.js:718-792` |

## 2.7 Web-Scan-Job-Ablauf

| Step | Code | Verhalten | Bewertung |
|---:|---|---|---|
| 1 | `apps/web/main.py:380-387` | Preview baut CLI-Launch-Payload ohne Ausführung. | Sehr gut für Freigabe/Transparenz. |
| 2 | `apps/web/main.py:389-404` | Jobstart nimmt Preview-Payload, startet CLI-Prozess. | Funktional; API-Key optional. |
| 3 | `apps/web/scan_jobs.py:226-265` | Prozess über `subprocess.Popen`, stdout/stderr in Logdateien. | Robust, Browser blockiert nicht. |
| 4 | `apps/web/scan_jobs.py:94-151` | Fortschritt aus CLI-Output-Markern extrahiert. | Praktisch; abhängig von stabilen Konsolenmarkern. |
| 5 | `apps/web/scan_jobs.py:272-325` | Snapshot liefert Status, Returncode, Tail, Progress, Substeps. | Gute UI-Integration. |
| 6 | `apps/web/main.py:413-553` | Ergebnisse werden aus Export-JSON-Dateien rekonstruiert. | Funktional, aber stark pfad-/namenabhängig. |

## 2.8 Artefakt-/Exportfluss

| Artefakt | Entstehung | Anzeige/Indexierung | Risiko |
|---|---|---|---|
| Scan-Reports HTML/TXT/PDF/JSON | CLI-Exportpfade unter `C:/Benutzer_*_Start` | `ReportCatalog` scannt Roots rekursiv (`apps/web/reports.py:317-341`) | Große lokale Datenmengen; keine Zugriffskontrolle pro Tenant. |
| Runtime Manifest | `RuntimeManifestService.register_artifact` | `/api/privacy/clients`, Privacy CLI | Manifest und tatsächlicher Report-FS-Bestand können auseinanderlaufen, wenn Dateien außerhalb des Manifests entstehen. |
| Scan Job Logs | `codex_tmp/web-jobs` oder Runtime `web_jobs` | Job-Status API | Logs können sensitive CLI-Ausgaben enthalten; Retention unklar. |
| HTML Preview | Sanitized Shell | `ReportCatalog._sanitize_html`, iframe `sandbox` | Positiv; CSS/Script werden entfernt. |

## 2.9 Workflow-Befunde

| Nr | Kategorie | Schwere | Befund | Beleg | Empfehlung |
|---:|---|---|---|---|---|
| W1 | Transparenz | niedrig | Preview zeigt Befehl, Profilwahl, Entropie, Bildoption, Adaptive Limits. | `apps/web/static/app.js:97-137` | Beibehalten; ideal für Freigabe-Gate. |
| W2 | Substep-Ehrlichkeit | niedrig | Nicht abbildbare Substeps sind explizit `None`. | `substep_manifest.py:57-67`, `93-97` | Beibehalten. |
| W3 | Marker-Abhängigkeit | mittel | UI-Fortschritt basiert auf Textmarkern in CLI-Ausgabe. | `apps/web/scan_jobs.py:29-56`, `94-151` | Mittelfristig maschinenlesbare JSON-Progress-Events statt nur stdout-Heuristik. |
| W4 | Pfadabhängigkeit | mittel | Ergebnisrekonstruktion hängt an Exportpfad, Client-Slug und Session-Namen. | `apps/web/main.py:435-553` | Manifest-first Result-Resolver einführen. |
| W5 | Harmonisierung als Abschluss | mittel | Start ist an aktiven Bericht gebunden, aber Report-ID wird nicht sichtbar in Backend-Harmonisierungspayload übergeben. | `app.js:718-747`, `main.py:337-357` | Abschlusskontext explizit mit Artifact/Report-ID persistieren. |
| W6 | RadiMorphic-Lücken | mittel | `candidate_generation`, `synergy_analysis`, `morphic_field` sind unmapped. | `substep_manifest.py:100-106` | Als eigene Gate-Entscheidung behandeln, nicht still „auffüllen“. |

## 2.10 Reifegrad Phase 2

| Dimension | Score | Begründung |
|---|---:|---|
| Ablauftransparenz | 4.4/5 | Preview, Stepper, Substep-Mapping, Logs. |
| Operator-Führung | 4.0/5 | 8-Step UI mit Consent/Preflight/Reports/Harmonisierung. |
| Maschinenlesbarkeit | 3.2/5 | Fortschritt und Ergebnisse noch teilweise stdout-/Dateipfad-getrieben. |
| Stabilität | 4.1/5 | Tests und Smoke grün. |
| Erweiterbarkeit | 3.8/5 | Gute Struktur; Substep-Lücken bewusst offen. |

Phase-2-Urteil: Workflow ist real, testbar und für lokale Operatorarbeit stark. Für Plattformreife sollten Fortschritt, Resultate und Abschlusskontext manifest-/eventbasiert statt heuristisch/dateipfadabhängig werden.
