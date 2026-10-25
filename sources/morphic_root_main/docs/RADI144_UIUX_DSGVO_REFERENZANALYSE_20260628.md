# Radi144 UI/UX-, DSGVO- und Berichtswesen-Referenzanalyse

**Datum:** 2026-06-28  
**Projekt:** Morphic Engine V1 (`C:\Morphic_v1`)  
**Referenzprojekt:** Radi144 (`C:\Users\Hubert111\Documents\Radi144`)  
**Berichtsreferenz:** `D:\Testpatienten Berichte\Mustermann\*.*`  
**Ziel:** Praezise Einordnung des aktuellen Berichtswesens, DSGVO-/Wellbeing-Compliance-Anforderungen und codebasierte Analyse des Radi144-Workflows inklusive Steppings, Substeppings und heilsamem Design als Grundlage fuer die spaetere Morphic-V1-UI/UX-Anpassung.

> Hinweis: Diese Analyse ist eine technische Produkt- und Codeanalyse. Sie ersetzt keine Rechtsberatung. Fuer die DSGVO wurden offizielle Quellen herangezogen: Verordnung (EU) 2016/679 auf EUR-Lex und EDPB Guidelines 4/2019 zu Data Protection by Design and by Default.

---

## 1. Kurzstatus

| Bereich | Status | Praezise Einordnung |
|---|---:|---|
| Mustermann-Berichtsstruktur | Teilweise umgesetzt | Struktur, Namensschema und ein gemeinsamer Legacy-HTML-Rahmen wurden in Morphic V1 nachgezogen. Eine vollstaendige 1:1-Paritaet zu allen alten HTML-/PDF-/Per-Profil-Berichten ist noch offen. |
| Top-N-Auswahl | Umgesetzt | Der Launcher bietet wieder Top-3, Top-5, Top-7 und Top-9 an; `--top-n` wird nicht mehr fest auf 5 gesetzt. |
| Archivpfade | Groesstenteils umgesetzt | Deutung, Synergy, Remedies und Trends nutzen wieder klientenbezogene Zielordner inklusive Geburtsdatum und Geburtsort. |
| PDF-Export | Offen | `tools/pdf_exporter.py` schreibt aktuell nur `.pdf.txt`-Platzhalter; echter PDF-Export fehlt noch. |
| Trendwesen | Teilweise umgesetzt | Bei zu wenigen Scans wird ein `Hinweis.txt` erzeugt. Eine echte Historik-/`trends.db`-gestuetzte Trendanalyse ist noch nicht wiederhergestellt. |
| DSGVO/Wellbeing-Compliance | Konzeptionell offen | Morphic V1 braucht noch Safety-Posture, PII-Safe-Views, Einwilligung, Audit, Export und Loeschkaskade. Radi144 liefert dafuer ein gutes internes Muster. |
| Radi144-Analyse | Durchgefuehrt | Nutzerworkflow, technischer Workflow, Designsystem, JS-Workflowlogik und Compliance-Services wurden codebasiert ausgewertet. |
| UI/UX-Umsetzung in Morphic V1 | Noch nicht umgesetzt | Empfehlung: erst Compliance-/Archiv-Fundament stabilisieren, dann UI-Shell und API-/CLI-Adapter bauen. |

**Nachtrag 2026-06-28:** Der erste P0-Schnitt wurde umgesetzt: Wellbeing-/Nicht-Medizin-Hinweis in den zentralen HTML-/TXT-Report-Renderern plus einfacher echter PDF-Export statt `.pdf.txt`-Platzhalter. Abdeckung: `tests/test_wellbeing_compliance_reports.py` und `tests/test_pdf_exporter_real_pdf.py`. Manifest, Audit und Loeschkaskade bleiben der naechste P0-Block.

**Nachtrag 2026-06-28:** Der zweite P0-Schnitt wurde umgesetzt: lokales Runtime-Manifest unter `data/runtime`, pseudonyme Client-Safe-Views, Session-/Artifact-Manifest, append-only Audit, nicht-destruktives Erasure-Manifest und gated Loeschkaskade. Standalone-Reporttools und zentrale Scan-Exports registrieren Artefakte best-effort. Abdeckung: `tests/test_runtime_privacy_manifest.py`, `tests/test_privacy_cli.py`, `tests/test_report_manifest_registration.py`.

**Nachtrag 2026-06-28:** Der erste P1-Berichtsschnitt wurde umgesetzt: `tools/remedy_reporter.py` erzeugt neben dem Gesamtbericht wieder Per-Profil-Remedy-Berichte (`*_remedy.html/json`), und `tools/trend_analyzer.py` schreibt bei mindestens zwei Scans eine echte Label-/Score-Trend-Historik mit Delta und Richtung. Abdeckung: `tests/test_remedy_trend_history.py`.

**Nachtrag 2026-06-28:** Der erste Radi144-inspirierte UI-Schnitt wurde als FastAPI Web Shell unter `apps/web` umgesetzt. Die Oberfläche zeigt direkt den Morphic-Workflow mit Systemstatus, Wellbeing-Compliance, Klient, Fokus & Top-N, Quellen/Preflight, Analyse-Vorschau sowie Berichte & Datenschutz. Die API nutzt bestehende Services fuer Health, Source Registry und DSGVO-Safe-Client-Views; der Top-N-Scan wird in diesem Schnitt bewusst nur als nicht-ausfuehrende CLI-Vorschau erzeugt. Abdeckung: `tests/test_web_shell.py`.

---

## 2. Mustermann-Berichte: Analyse- und Umsetzungsstand

### 2.1 Referenzstruktur aus `D:\Testpatienten Berichte\Mustermann`

| Referenzbereich | Beobachtete Struktur | Funktionale Bedeutung |
|---|---|---|
| Resonanz | `Mustermann_Klaus_09041966_Augsburg_Resonanz\YYYYMMDD_HHMMSS_TOP9_SESSION\01_<profil>\*_multiplex_scan.{json,html,txt}` | Je Profil ein eigener Multiplex-Scan mit JSON, HTML und TXT. |
| Deutung | `Mustermann_Klaus_09041966_Augsburg_Deutung\YYYYMMDD_HHMMSS_top5\deutung_*.html/pdf` | Separate, klientenbezogene Deutungsmappe pro Sitzung. |
| Synergy | `Mustermann_Klaus_09041966_Augsburg_Synergy\YYYYMMDD_HHMMSS_synergy_report\synergy_gesamt.html/json` | Konsolidierter Synergy-Gesamtbericht ueber Session-Ergebnisse. |
| Remedies | `Mustermann_Klaus_09041966_Augsburg_Remedies\YYYYMMDD_HHMMSS_top9_remedies.html` plus einzelne `*_remedy.html` | Gesamt-Remedy-Bericht plus profilbezogene Einzelberichte. |
| Trends | `Mustermann_Klaus_09041966_Augsburg_Trends\Hinweis.txt` | Hinweis bei zu wenig Historie; urspruenglich an `trends.db` angebunden. |

### 2.2 Layout-Merkmale der alten Mustermann-Berichte

| Bericht | Alte Layout-/Funktionsmerkmale | Aktuelle Morphic-V1-Annaeherung |
|---|---|---|
| Multiplex-Hauptbericht | Light-Blue-Verlauf, glasartige Container, Header `Resonanzanalyse - Report`, Metriken, Einflussfaktoren, Fokus, Resonanzwerte, Fullbody-Subgruppen, Synergy/Remedy-Sektionen. | Der Haupt-Multiplex-Renderer wurde wieder in diese Richtung gebracht: Header, Metriken, Fokus, gruppierte Subgruppen, Quantum-Synergy, Remedy-Synergien, Badges und Print-CSS. |
| Deutung | Titel `Deutung - <Vorname> <Nachname>`, hellblauer Verlauf, Container, Header, Sections, Summary/Finding-Bloecke. | `tools/interpretation_generator.py` erzeugt wieder klientenbezogene Deutungsordner und nutzt den gemeinsamen Legacy-HTML-Rahmen. Inhaltlich noch einfach. |
| Synergy | Header/Meta/Section/Card-Struktur mit `synergy_gesamt.html/json`. | `tools/synergy_consolidator.py` erzeugt wieder `synergy_gesamt.html/json` in `..._Synergy\...\_synergy_report`. Layout ist angenaehert, Inhalt noch verdichtet. |
| Remedies | Blue-Gradient, `Remedy Report - Klaus Mustermann`, Remedy-Items, Score-Badges, Tabellen. | `tools/remedy_reporter.py` erzeugt wieder Gesamtberichte mit Top-N-Suffix. Per-Profil-Remedy-Reports fehlen noch. |
| Trends | `Hinweis.txt` bei zu wenig Historie; alte `trends.db` wurde im Hinweis erwaehnt. | `tools/trend_analyzer.py` erzeugt wieder `Hinweis.txt`, wenn weniger als zwei verwertbare Scans vorhanden sind. Echte Trends noch offen. |
| PDF | Alte Referenz enthaelt echte PDF-Dateien. | Aktuell nur Platzhalter via `tools/pdf_exporter.py`; kein echter PDF-Renderer. |

### 2.3 Bereits integrierte Morphic-V1-Bausteine

| Datei/Baustein | Aktueller Nutzen |
|---|---|
| `tools/reporting_common.py` | Gemeinsame Helfer fuer `client_report_dir`, sichere Pfadbestandteile, Scan-Dateisuche und Legacy-HTML-Rahmen. |
| `tools/interpretation_generator.py` | Deutungsbericht mit `--birth-date`, `--birth-place`, `--output-root`. |
| `tools/synergy_consolidator.py` | Konsolidiert `quantum_synergy` aus Scan-JSONs und schreibt `synergy_gesamt.html/json`. |
| `tools/remedy_reporter.py` | Konsolidiert `remedy_synergies` und schreibt `topN_remedies.html/json`. |
| `tools/trend_analyzer.py` | Findet klientenbezogene Scans und erzeugt bei fehlender Historie einen Hinweis. |
| `Run-MultiplexScan.ps1` | Uebergibt `--birth-date`, `--birth-place`, `--top-n` an die relevanten Tools. |
| `apps/cli/commands/scan.py` | Direkte `top3-scan`-Konsolidierung fuer Synergy/Remedies nutzt nun strukturierte Zielordner. |
| `tests/test_report_tool_archives.py` | Regressionstest fuer strukturierte Report-Tool-Archive. |
| `tests/test_top5_workflow_smoke.py` | Prueft Top-N-Workflow inklusive strukturierter Synergy-/Remedy-Ausgaben. |

### 2.4 Offene Berichtsluecken

| Prioritaet | Luecke | Risiko | Empfehlung |
|---:|---|---|---|
| P0 | Globaler Wellbeing-/Nicht-Medizin-Hinweis fehlt in allen V1-Berichten. | Berichte koennen als Diagnose-/Therapieaussage missverstanden werden. | Kanonischen Safety-Block in HTML, TXT und spaeter PDF erzwingen. |
| P0 | Echte PDF-Erzeugung fehlt. | Alte Funktionalitaet wirkt fuer Anwender unvollstaendig. | Lokalen PDF-Renderer definieren, z.B. Playwright/Chromium oder ReportLab; keine stillen Platzhalter. |
| P1 | Per-Profil-Remedy-Berichte fehlen. | Mustermann-Paritaet nicht vollstaendig; Detailnavigation schwach. | Aus jedem Profil-JSON einen `*_remedy.html` erzeugen und Gesamtbericht verlinken. |
| P1 | Trendanalyse ist nur Minimalhinweis. | Verlauf/Archivwesen fachlich unvollstaendig. | `trends.db`-Ersatz oder JSONL/Event-Store definieren; mindestens zwei Sessions vergleichen. |
| P1 | Keine visuelle Regression gegen Mustermann-Screenshots. | Layout kann formal aehnlich, visuell aber abweichend sein. | Referenzreport und neuen Report per Playwright screenshotten und visuell pruefen. |
| P2 | Report-Artefakte sind noch nicht in einem Manifest registriert. | DSGVO-Auskunft, Export und Loeschung bleiben schwer nachvollziehbar. | Report-Manifest analog Radi144 einfuehren. |

---

## 3. DSGVO und Wellbeing Compliance

### 3.1 Offizielle Bezugspunkte

| Quelle | Relevanz fuer Morphic V1 |
|---|---|
| EUR-Lex, Verordnung (EU) 2016/679, Art. 24 | Verantwortliche muessen geeignete technische und organisatorische Massnahmen implementieren und nachweisen koennen. |
| EUR-Lex, Verordnung (EU) 2016/679, Art. 25 | Datenschutz durch Technikgestaltung und datenschutzfreundliche Voreinstellungen, insbesondere Pseudonymisierung und Datenminimierung. |
| EUR-Lex, Art. 17 | Recht auf Loeschung muss technisch abbildbar sein. |
| EUR-Lex, Art. 20 | Datenuebertragbarkeit: Export personenbezogener Daten in geeigneter Form. |
| EDPB Guidelines 4/2019 | Konkretisierung von Data Protection by Design and by Default. |

Quellen:

- https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
- https://www.edpb.europa.eu/documents/guideline/guidelines-42019-on-article-25-data-protection-by-design-and-by-default_en

### 3.2 Konkrete technische Anforderungen fuer Morphic V1

| Anforderung | Morphic-V1-Konsequenz | Prioritaet |
|---|---|---:|
| Wellbeing-Klarstellung | Produkttexte, UI, CLI und Berichte duerfen keine Diagnose, Behandlung oder Heilversprechen formulieren. | P0 |
| Einwilligung/Zweck | Vor Analyse Start: Zweck, lokale Verarbeitung, Exportziel und Berichtserzeugung bestaetigen lassen. | P0 |
| Datenminimierung | Pflichtfelder nur dort, wo Engine/Archiv sie wirklich braucht; optionale Felder deutlich optional. | P0 |
| Pseudonymisierung | Stabiler `client_id`-Hash aus Identitaetsdaten; interne PII bleibt getrennt von Safe-Views. | P0 |
| Safe-Views | UI-/Admin-Listen duerfen nicht automatisch Roh-PII anzeigen. | P0 |
| Audit | Erzeugung, Export, Import, Quellenaktivierung, Loeschmanifest und Loeschung append-only protokollieren. | P1 |
| Loeschung | Erst nicht-destruktives Manifest, dann gated Execute mit Audit und Kaskade ueber Berichte/Archive. | P1 |
| Datenexport | Klienten-/Session-/Report-Export fuer Auskunft und Portabilitaet. | P1 |
| Quellenverwaltung | Online- und Admin-Repositories standardmaessig deaktivierbar, aktivierbar, quarantainierbar und auditierbar. | P1 |
| Aufbewahrung | Retention-Konzept fuer lokale Archive und alte Exporte. | P2 |

### 3.3 Radi144 als Compliance-Vorbild

| Radi144-Datei | Beobachtetes Muster | Uebernahmeempfehlung fuer Morphic V1 |
|---|---|---|
| `app/services/safety_service.py` | Kanonischer Disclaimer, Safety-Marker, PII-Stripping fuer Client/Session-Projektionen. | Direktes Muster fuer `services/safety_service.py` oder `core/compliance/safety.py`. |
| `app/api/clients.py` | Endpunkte fuer Safety-Posture, Pseudonym-Safe-View, Erasure-Manifest, gated Delete und Audit. | Als API-Vertrag fuer spaetere Morphic-UI uebernehmen. |
| `app/services/client_registry_service.py` | Stabiler pseudonymer `client_id` via SHA1-Stable-Key. | Fuer Morphic adaptieren; ggf. spaeter staerkerer Hash/HMAC mit lokalem Secret. |
| `app/services/session_archive_service.py` | Session-Metadaten mit `client_ref`, Fokus, Konfiguration, Result-Summary und Artefakten. | Morphic-Scans als Sessions erfassen, ohne Engine-JSONs zu veraendern. |
| `app/services/report_manifest_service.py` | Registriert Artefakte je Session. | Grundlage fuer Berichtsauskunft und Loeschkaskade. |
| `app/services/erasure_service.py` | Nicht-destruktives Manifest, Gate-Token, Kaskade ueber JSON-Stores und Dateisystem, Audit. | Sehr geeignet fuer Morphic-V1-Archive. |
| `tests/test_safety_posture.py` | Pinnt Disclaimer in Responses und PDF. | Entsprechende Regressionstests vor Implementierung schreiben. |
| `tests/test_client_safe_projection.py` | Verhindert Roh-PII in Safe-Views. | Muss fuer Morphic-V1-Adminlisten uebernommen werden. |
| `tests/test_erasure_cascade.py` | Manifest, Gate, Kaskade und Idempotenz werden getestet. | Vor Loeschlogik als V1-Kontrakt nutzen. |

---

## 4. Radi144 Projektanalyse

### 4.1 Struktur und Rollen

| Bereich | Dateien | Rolle im System |
|---|---|---|
| Haupt-Workflow-UI | `user_workflow.html`, `user_workflow.css`, `user_workflow.js` | 10-Schritt-Anwenderworkflow von Einstieg bis Export/Harmonisierung. |
| Technische Workflow-Dokumentation | `workflow_stepping.html`, `workflow_stepping.css`, `workflow_stepping.js` | 12-Schritt-Technikuebersicht fuer Engine, EMF, Matrix, Quantum, Export und API. |
| API | `app/api/resonance.py`, `app/api/clients.py` | Analyse, PDF-Export, Safety, Clients, Loeschung, Audit. |
| Runtime-Services | `app/services/*.py` | Registry, Sessions, Artefakte, Audit, Erasure, Safety. |
| Tests | `tests/test_*` | Regressionen fuer API, Safety, Erasure, Client-Projektionen und Workflow-nahe Funktionen. |
| Wiederherstellungsdoku | `WIEDERHERSTELLUNG_2025-02-14.md` | Dokumentiert Designsystem, 10 Schritte, localStorage, Export, Harmonisierung. |

### 4.2 Radi144 Nutzerworkflow: 10 Schritte

| Step | Name | Substeppings/Funktion | Uebertragbarkeit auf Morphic V1 |
|---:|---|---|---|
| 1 | Willkommen | Systemuebersicht, API-Status, Templates. | Ja: Startseite mit Health, Quellenstatus, Compliance-Hinweis. |
| 2 | Klienten-Daten | Vector Mode: Client, Gruppe, Geo, Bild; Pflichtdaten; optionale DB-/Bild-/Geo-Inputs. | Teilweise: Morphic braucht zunaechst Client und Gruppe; Geo/Bild spaeter optional. |
| 3 | Fokus & Intention | Fokus-Textarea, Multi-Fokus per Semikolon, Presets, Fokus-History. | Ja: passt gut zu Fokus-Keywords und Top-N-Analyse. |
| 4 | Analyse-Konfiguration | Matrixgroesse, Modus, Fokusgewichtung, Symmetrie, Palette, EMF, HRV, Amplifier. | Ja, aber Morphic-spezifisch: Top-N, Hardware-Profil, Synergy, Sources. |
| 5 | EMF-Umfeld-Analyse | Status, Index, Entropy, Jitter, Counter-Frequencies. | Spaeter optional; aktuell nicht vor P0/P1. |
| 6 | Zusammenfassung & Start | Eingaben pruefen, Analyse starten, Fortschritt. | Ja: wichtiger UX-Gate inklusive Einwilligung. |
| 7 | Ergebnis: Matrix | Matrix-Visualisierung, Score, Sequenznavigation. | Teilweise: Morphic zeigt eher Profil-/Multiplex- und Subgruppenresultate. |
| 8 | Ergebnis: Details | Technische Details, EMF, Raw JSON. | Ja: Expert-/Admin-Ansicht. |
| 9 | Harmonisierung | Impuls/Pause, Solfeggio, Audio, Timer, Matrixanimation. | Optional: erst nach stabilen Reports/Compliance integrieren. |
| 10 | Export & Abschluss | JSON, CSV, PDF, Excel, Template speichern, neue Analyse. | Ja: Muss mit Archiv/Manifest/DSGVO verknuepft werden. |

### 4.3 Radi144 technischer Workflow: 12 Schritte

| Step | Name | Code-/Dokubereich | Bedeutung fuer Morphic V1 |
|---:|---|---|---|
| 1 | System-Initialisierung | `workflow_stepping.html` Step 0 | Morphic: venv, Health, DBs, Sources, Hardware-Profil. |
| 2 | Benutzer-Eingabe | Step 1 | Morphic: Clientdaten, Top-N, Fokus, Quellenstatus. |
| 3 | Klienten-Signatur | Step 2 | Morphic: aktuelle Signatur-/Profil-Engine erhalten, nur UI-Fassade bauen. |
| 4 | Fokus-Vektorisierung & Bio-Knowledge | Step 3 | Morphic: Fokus-Bonus/Keyword-Gewichtung transparent anzeigen. |
| 5 | EMF-Kompensation | Step 4 | Morphic: optionaler spaeterer Baustein, nicht P0. |
| 6 | Amplifier-System | Step 5 | Morphic: Remedies/Multiplexe getrennt von Aussagen zur Wirkung halten. |
| 7 | Farbpaletten-Generierung | Step 6 | Morphic: heilsames Designsystem uebernehmen, aber Reports nicht ueberfrachten. |
| 8 | Matrix-Suche | Step 7 | Morphic: Kernengine unveraendert, nur Fortschritt/Status sichtbar machen. |
| 9 | Quantum Refinement | Step 8 | Morphic: Synergy optional und klar als Inferenz kennzeichnen. |
| 10 | Post-Processing | Step 9 | Morphic: Deutung, Synergy, Remedies, Trends, PDF. |
| 11 | Ausgabe & Export | Step 10 | Morphic: Archivmanifest, PDF/HTML/JSON/TXT, Portabilitaet. |
| 12 | REST API & Live-Monitoring | Step 11 | Morphic: spaeter FastAPI-/UI-Adapter statt direkter PowerShell-Bedienung. |

### 4.4 Radi144 Designsystem

| Element | Radi144-Umsetzung | Empfehlung fuer Morphic V1 |
|---|---|---|
| Grundstimmung | Warmes Elfenbein, Salbeigruen, Sand, Terracotta. | Uebernehmen; wirkt ruhiger und weniger technisch als alte blaue Reports. |
| Typografie | `Playfair Display` fuer Ueberschriften, `Source Sans 3` fuer Fliesstext, Mono fuer technische Werte. | Uebernehmen, aber mit lokaler Fallback-Strategie fuer Offline/DSGVO. |
| Layout | Sticky Stepper, Fortschrittsbalken, Karten, Formularraster, kompakte Metrikzeilen. | Als Morphic-App-Shell uebernehmen. |
| Interaktion | Stepper-Navigation, Validierung pro Schritt, API-Status, Presets, Templates, Autosave. | Sehr geeignet fuer Benutzerfuehrung. |
| Feedback | Spinner, Progress-Bar, Statuszeilen, Ergebnis-Karten, Export-Karten. | Fuer lange CLI-/Scan-Laeufe zentral wichtig. |
| Responsiveness | Mobile Grid-Fallbacks, horizontale Stepper-Navigation. | Pflicht fuer spaetere UI. |
| Print | UI-Elemente werden im Print ausgeblendet. | Auch fuer Reports und PDF-Vorstufe nutzen. |

### 4.5 Radi144 JS-Workflowlogik

| Modul/Funktion | Beobachtung | Morphic-V1-Relevanz |
|---|---|---|
| `STEPS` / `buildNav()` | Steps werden dynamisch in Navigation abgebildet. | Morphic kann denselben Stepper-Ansatz nutzen. |
| `goToStep()` / `navigate()` | Schrittwechsel, Validierung und step-spezifische Aktionen. | Gut fuer Preflight, Scanstart, Reportanzeige. |
| `validateCurrentStep()` | Pflichtfeld- und Fokusvalidierung. | Muss um Einwilligung, Exportpfad und Quellenstatus erweitert werden. |
| `checkAPI()` | API-Verbindung wird sichtbar geprueft. | Morphic: Health, DB, Sources und venv-Status anzeigen. |
| `startAnalysis()` | API-Call, Progress, Sequenzen, Fokus-History. | Morphic: CLI/API-Adapter fuer Top-N-Scan. |
| `renderMatrix()` / `renderDetails()` | Ergebnisse visuell und technisch getrennt. | Morphic: Anwenderansicht vs. Expertendetails. |
| `saveSession()` / `restoreSession()` | localStorage Session-Persistenz. | Nur fuer nicht-sensitive UI-Settings verwenden; keine Roh-PII dauerhaft im Browser speichern. |
| `exportPDF()` / `exportCSV()` / `exportJSON()` | Mehrere Exportpfade. | Mit Report-Manifest und Audit verknuepfen. |
| Template-Management | Lokale Templates bis 21 Eintraege. | Morphic kann Top-N/Profil-/Quellen-Konfigurationen als Templates speichern. |

---

## 5. Zielbild fuer Morphic Engine V1 UI/UX

### 5.1 Grundsatz

Die Morphic-Kernengines sollen erhalten bleiben. Die neue UI soll als Fassade/Adapter arbeiten:

1. UI sammelt Eingaben und Einwilligung.
2. UI startet validierte CLI/API-Kommandos.
3. Engine erzeugt unveraenderte JSON-/HTML-/TXT-Artefakte.
4. Archivservice registriert Session und Artefakte.
5. Reports und Exporte werden ueber Manifest, Audit und Safe-Views verwaltbar.

### 5.2 Empfohlener Morphic-V1-Anwenderworkflow

| Step | Morphic-V1-Zielschritt | Substeppings |
|---:|---|---|
| 1 | Willkommen & Systemstatus | Health, Python/venv, Datenbanken, Quellenstatus, Wellbeing-Hinweis. |
| 2 | Compliance & Einwilligung | Zweck, lokale Verarbeitung, Exportziel, Nicht-Medizin-Hinweis bestaetigen. |
| 3 | Klienten-Daten | Name, Geburtsdatum, Geburtsort; optional Pseudonym/Notiz; Safe-View-Hinweis. |
| 4 | Fokus & Intention | Fokus, Fokus-Presets, Fokus-History, Bonusanzeige fuer Fokus-Keywords. |
| 5 | Profil-/Gruppenauswahl | Auto-Scan 35 Hauptprofile, Top-3/5/7/9, optionale Profilgruppen. |
| 6 | Quellen & Repositories | Aktive/deaktivierte/quarantainierte Quellen, Admin-Import, Dry-Run. |
| 7 | Scan-Konfiguration | Hardware-Profil, `k-total`, `top-k`, Synergy, Threshold, Combos. |
| 8 | Vorpruefung | Schreibrechte, Archivpfade, DB-Health, Source-Registry-Validierung. |
| 9 | Analyse starten | Fortschritt, laufende Profile, Logs, Abbruchhinweis. |
| 10 | Ergebnisse | Resonanzwerte, Top-Profile, Subgruppen, Synergy, Remedies, technische Details. |
| 11 | Berichte | Deutung, Synergy, Remedies, Trends, PDF/HTML/TXT/JSON, Manifest. |
| 12 | Abschluss & Datenschutz | Export, Portabilitaet, Loeschmanifest, neue Analyse, Template speichern. |

### 5.3 Noetige Frontend-Funktionsgruppen

| Funktionsgruppe | Muss-Funktion | Spaeter erweiterbar |
|---|---|---|
| Systemstatus | Health, Sources Validate, DB-Status. | Live-Log, Performance-Metriken. |
| Client/Compliance | Einwilligung, Pseudonym-ID, Nicht-Medizin-Hinweis. | Rollen/Rechte, Retention-Regeln. |
| Scan | Top-N, Hardware, Fokus, Synergy, Exportpfad. | Batch-Queue, Wiederaufnahme. |
| Quellen | Liste, Aktivieren/Deaktivieren, Quarantaene sichtbar. | Online Sync, Admin-Staging, Rollback. |
| Reports | HTML-Vorschau, Oeffnen, PDF erzeugen, Manifest. | Visuelle Diff gegen alte Vorlage. |
| Datenschutz | Export, Audit, Loeschmanifest, Gate-Delete. | Verschluesselung, Datenschutz-Dashboard. |

---

## 6. Priorisierter Umsetzungsplan ab diesem Stand

| Prioritaet | Schritt | Ziel | Begründung |
|---:|---|---|---|
| P0 | Kanonischen Safety-/Wellbeing-Block einfuehren | Einheitlicher Hinweis in CLI, UI-Vorstufe, HTML/TXT/PDF. | Reduziert Missverstaendnisrisiko vor weiterer UI-Verbreiterung. |
| P0 | Client-/Session-/Report-Manifest minimal einfuehren | Jede Analyse und jedes Artefakt wird nachvollziehbar registriert. | Voraussetzung fuer DSGVO-Auskunft, Export und Loeschung. |
| P0 | Echten PDF-Export entscheiden und implementieren | Mustermann-Funktionalitaet wiederherstellen. | Aktueller Platzhalter ist funktional unzureichend. |
| P1 | Per-Profil-Remedy-Reports wiederherstellen | Vollstaendigere Mustermann-Paritaet. | Anwender erwarten Detailberichte je Profil. |
| P1 | Trend-Historik technisch definieren | `Hinweis.txt` bleibt nur Fallback, echte Verlaufsauswertung kommt zurueck. | Archivwesen wird fachlich wieder sinnvoll. |
| P1 | Source Registry um Admin-Staging erweitern | Importierte Repositories pruefen, aktivieren/deaktivieren, auditieren. | Erfuellt Nutzerwunsch nach eigenen Repositories und sicherer Quellenkontrolle. |
| P1 | Radi144-UI-Shell als Morphic-Adapter entwerfen | 12-Schritt-Morphic-Workflow als Weboberflaeche. | UI erst nach stabilem Compliance-/Archivkern. |
| P2 | Backend-API-Fassade fuer UI bauen | UI startet nicht direkt PowerShell, sondern stabile API/Service-Funktionen. | Bessere Testbarkeit und Benutzerfuehrung. |
| P2 | Visuelle Regression der Reports | Alte Mustermann-Vorlage gegen neue Reports pruefen. | Verhindert Layout-Regressionen. |
| P3 | Harmonisierung/Audio/EMF optional integrieren | Spaetere Erweiterung, nicht Kernstabilitaet. | Vermeidet Ueberladung der ersten UI-Phase. |

---

## 7. Offene Fragen vor UI-Implementierung

| Frage | Empfehlung |
|---|---|
| Soll die neue UI statisch starten oder sofort FastAPI-basiert sein? | Empfehlung: FastAPI-/Service-Fassade, weil DSGVO, Audit, Loeschung und lange Scans sonst schwer sauber steuerbar sind. |
| Soll Radi144 visuell 1:1 kopiert werden? | Empfehlung: Designsystem und Workflowlogik uebernehmen, Inhalte Morphic-spezifisch umbauen. |
| Soll localStorage Roh-PII speichern? | Nein. Hoechstens nicht-sensitive UI-Konfigurationen speichern; PII nur lokal serverseitig/archiviert und pseudonymisiert sichtbar machen. |
| Soll Online-Repository-Sync automatisch laufen? | Nein. Standard: deaktiviert, Admin aktiviert bewusst, Dry-Run/Diff vor Import, Quarantaene fuer unsichere Quellen. |
| Soll die Kernengine veraendert werden? | Nein. Neue UI und Compliance-Schicht als Adapter/Fassade vor die bestehenden CLI-/Engine-Funktionen setzen. |

---

## 8. Naechste konkrete Empfehlung

Als naechstes sollte **nicht** direkt die komplette UI gebaut werden. Die sauberste Reihenfolge ist:

1. Safety-/Wellbeing-Block in Reports und CLI-Ausgaben einfuehren.
2. Minimalen Client-/Session-/Report-Manifest-Store nach Radi144-Muster bauen.
3. Echten PDF-Export ersetzen statt Platzhalter beibehalten.
4. Per-Profil-Remedy-Berichte und Trend-Historik vervollstaendigen.
5. Danach Radi144-inspirierte Morphic-V1-UI als 12-Schritt-Workflow implementieren.

Damit bleiben die Kernengines stabil, und die neue Benutzeroberflaeche bekommt ein belastbares Archiv-, Datenschutz- und Berichtsfundament.
