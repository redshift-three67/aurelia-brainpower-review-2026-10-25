# Radi144 Session-/Klienten-/Report-Vereinheitlichung – Architekturplan

> For Hermes: Kritische Architekturänderungen erst nach expliziter Freigabe des Nutzers umsetzen. Diese Datei ist zunächst Plan und Entscheidungsgrundlage.

Stand: 2026-06-03
Projektwurzel: `C:\Users\Hubert111\Documents\Radi144`

Nachtrag 2026-06-04 (verifiziert):

- Phase 1-3 dieses Plans sind inzwischen in der Codebasis umgesetzt.
- Die dateibasierten Services fuer `Client Registry`, `Session Archive` und `Report Manifest` sind produktiv angeschlossen.
- `dev_cli.py` spiegelt bereits in die gemeinsame Verwaltungsdomäne.
- `app/api/resonance.py` nutzt jetzt echte Runtime-`client_id`-Aufloesung, archiviert API-Analysen als Sessions und bindet den PDF-Export an das Report-Manifest an.
- Die API gibt fuer Verkettung/Weiterverarbeitung jetzt `X-Client-ID`, `X-Session-ID` und `X-Artifact-ID` zurueck.
- Ein separater, bewusst minimaler CPU-RAM-Guard in `app/algorithms/resonance_engine.py` wurde spaeter als Runtime-Stabilisierung ergaenzt; er gehoert nicht zur Verwaltungsdomäne selbst, schuetzt aber die Ausfuehrbarkeit der verifizierten Pfade.

Nachtrag 2026-06-08 (verifiziert):

- Phase 4 ist adapterartig umgesetzt, ohne PowerShell-Komplettmigration und ohne Core-/Algorithmusaenderung.
- `generate_matrix.ps1` bevorzugt jetzt eine generierte Template-Leseansicht aus `data/runtime/sessions.json` und `data/runtime/clients.json`.
- Der Adapter `export_powershell_templates_from_runtime_dir(...)` erzeugt `data/runtime/powershell_templates.json` im legacy-kompatiblen Template-Format.
- `data/session_templates.json` bleibt als Fallback erhalten.
- Die Umsetzung ist in `docs/PHASE4_POWERSHELL_METADATA_STATUS_2026-06-08.md` detailliert dokumentiert.
- Verifizierter lokaler Teststand nach Phase 4: `44 passed`.
- Offene Zusatzverifikation: echter PowerShell-/Windows-Live-Test auf einem Host mit `pwsh` oder Windows PowerShell.

**Goal:** Die aktuell fragmentierte Session-, Klienten- und Report-Verwaltung in ein konsistentes Kernmodell überführen, ohne Kernengine, Kernalgorithmen oder den verifizierten Workflow zu destabilisieren.

**Architecture:** Wir führen zuerst eine dünne Verwaltungsdomäne ein, die bestehende Dateiformate und Aufrufpfade adaptiert statt sie sofort zu ersetzen. `generate_matrix.ps1`, `dev_cli.py` und `app/api/resonance.py` bleiben zunächst funktional bestehen, delegieren aber schrittweise an gemeinsame Services für Archiv, Klient, Session und Report-Metadaten.

**Tech Stack:** Python 3.11, Pydantic v2, JSON-Dateien als bestehendes Persistenzformat, FastAPI, bestehende CLI-/PowerShell-Entrypoints, ReportLab/OpenPyXL.

---

## 1. Verifizierter Ist-Zustand

### 1.1 Session-Verwaltung heute

Session-Daten sind derzeit auf mehrere Orte verteilt:

- `last_session.json`
  - enthält letzte Personen-/Startwerte für PowerShell-Wiederverwendung
- `data/session_templates.json`
  - enthält bis zu 21 gespeicherte Template-Konfigurationen
  - wird in `dev_cli.py:141-185` geschrieben
  - wird in `generate_matrix.ps1:100-160` gelesen
- `focus_history.txt`
  - enthält Fokus-Historie für UI-Wiederverwendung
- `Analysen/<timestamp>_<client>/`
  - enthält Ergebnisartefakte pro Lauf
  - wird durch `dev_cli.py:113-122` angelegt
- `analysis_log.txt`
  - liegt innerhalb des Session-Ausgabeordners
  - wird in `dev_cli.py:1153-1162` fortgeschrieben

### 1.2 Klienten-Verwaltung heute

Es gibt aktuell kein zentrales, dauerhaftes Klientenregister.

Vorhandene Teile:

- `app/schemas/klienten.py`
  - definiert `ClientBase`, `ClientCreate`, `ClientUpdate`, `ClientInDB`
- `dev_cli.py`
  - konstruiert `client_data` ad hoc aus CLI-Argumenten
- `generate_matrix.ps1`
  - sammelt Klientendaten interaktiv und schreibt sie indirekt in CLI-Argumente
- `app/api/resonance.py`
  - akzeptiert `client_data` oder `client_id`
  - bei `client_id` gibt es aktuell nur `_default_client_data()` statt echter Auflösung

Kernaussage:
`client_id` suggeriert Persistenz, aber im jetzigen Zustand existiert keine echte Client-Repository-Schicht.

### 1.3 Report-Verwaltung heute

Reports werden heute fachlich erzeugt, aber organisatorisch nicht zentral verwaltet.

CLI-Pfade:

- `dev_cli.py:213-309`
  - Excel-Export
- `dev_cli.py:311-463`
  - Einzel-PDF-Export
- `dev_cli.py:464-...`
  - kombiniertes PDF
- `dev_cli.py:1167-1185`
  - Export-Orchestrierung pro Lauf

API-Pfad:

- `app/api/resonance.py:585-745`
  - separater PDF-Export-Endpunkt
  - anderer Kontext-/Payload-Stil als in der CLI

Kernaussage:
Die Report-Erzeugung existiert doppelt: einmal als CLI-/Dateisystem-Workflow und einmal als API-Byte-Response. Ein gemeinsames Report-Metadatenmodell fehlt.

---

## 2. Hauptprobleme der aktuellen Struktur

### P1 – Kein einheitlicher Session-Begriff

Aktuell gibt es mindestens vier konkurrierende Session-Bedeutungen:

1. letzte Eingabesession (`last_session.json`)
2. Template-Session (`session_templates.json`)
3. Analyse-Session im Ordner `Analysen/...`
4. Harmonize-/Audio-Lauf innerhalb einer Analyse

Folge:
Ein späteres Archiv, eine parallele Sitzungssteuerung oder eine echte Session-Wiederaufnahme sind schwer konsistent abbildbar.

### P2 – Klientendaten sind transportiert, aber nicht verwaltet

`client_data` wird zwar durch das System getragen, aber nicht zentral gespeichert, versioniert oder referenziert.

Folge:
- `client_id` in der API ist semantisch zu stark für die aktuelle Implementierung
- Dopplungen und Inkonsistenzen sind wahrscheinlich
- Session-Historie kann keinen stabilen Klientenanker nutzen

### P3 – Report-Artefakte haben kein zentrales Manifest

PDF, XLSX, kombiniertes PDF und Logdatei werden erzeugt, aber nicht in einer gemeinsamen Metadatenstruktur beschrieben.

Folge:
- keine stabile Archivsicht
- keine einfache API-/UI-Liste aller Berichte
- kein sicherer Bezug zwischen Analyse, Report und Harmonisierung

### P4 – PowerShell und Python teilen denselben Fachzustand nur implizit

`generate_matrix.ps1` und `dev_cli.py` teilen Informationen derzeit über:

- Dateien
- CLI-Argumente
- Standardwerte
- Seiteneffekte

Folge:
Die Struktur ist benutzbar, aber nicht sauber modelliert.

---

## 3. Zielbild ohne Destabilisierung

Wir ändern nicht sofort den gesamten Workflow. Stattdessen schaffen wir ein kompatibles Kernmodell unterhalb der bestehenden Entrypoints.

### 3.1 Zieldomänen

Es sollen vier dünne Domänen eingeführt werden:

1. Client Registry
2. Session Archive
3. Report Manifest
4. Workflow Context

### 3.2 Minimaler Zielzuschnitt je Domäne

#### A. Client Registry

Zweck:
- stabiler Schlüssel für Klienten
- Normalisierung persönlicher Stammdaten
- Wiederverwendung über CLI, API und Archiv

Minimalmodell:
- `client_id`
- Name/Vorname
- Geburtsdatum
- Geburtsort
- optional Planet
- optionale Metadaten
- `created_at`
- `updated_at`

#### B. Session Archive

Zweck:
- genau eine eindeutige Analyse-Session pro Lauf
- Verbindung von Eingabe, Resultaten, Exporten und Harmonisierung

Minimalmodell:
- `session_id`
- `client_id` oder eingebettete Client-Referenz
- Timestamp
- Fokus/Fokusliste
- Berechnungsmodus
- Matrixgröße
- aktivierte Flags
- Ergebniszusammenfassung
- Artefaktliste
- Harmonisierungsstatus

#### C. Report Manifest

Zweck:
- alle erzeugten Dateien als referenzierte Artefakte beschreiben

Minimalmodell:
- `artifact_id`
- `session_id`
- Typ (`pdf`, `xlsx`, `combined_pdf`, `audio`, `log`)
- absoluter oder projekt-relativer Pfad
- Erzeugungszeit
- optional Hash/Größe

#### D. Workflow Context

Zweck:
- gemeinsame Eingabe-/Kontextrepräsentation für CLI, API und PS1

Minimalmodell:
- vector mode (`client`, `group`, `geo`, `image`, `db`)
- Fokusdaten
- Klient-/Gruppen-/Geo-/Bild-Kontext
- Runtime-Flags
- Report-Flags
- Harmonizer-Flags

---

## 4. Sicherheitsprinzipien für den Umbau

Um die Kernengine und den verifizierten Workflow nicht zu destabilisieren, gelten diese Regeln:

1. Keine Änderungen an mathematischer Kernlogik in `app/algorithms/resonance_engine.py`
2. Keine Änderung am Top-3-/Harmonize-Verhalten ohne separate Freigabe
3. Bestehende Dateinamen und Ausgabeordner zunächst beibehalten
4. Bestehende JSON-Dateien zunächst lesen und weiter schreiben können
5. Neue Verwaltungsdomäne zuerst als Adapter, nicht als Zwangsmigration
6. PowerShell-Workflow zuerst nur konsumierend anbinden, nicht neu erfinden

---

## 5. Empfohlene Implementierungsreihenfolge

## Phase 1 – Nur Domänen einführen, noch keine Verhaltensänderung

Ziel:
Neue gemeinsame Modelle und Services hinzufügen, aber bestehende Pfade unverändert lassen.

Neue Zielpfade:
- `app/models/client_registry.py`
- `app/models/session_archive.py`
- `app/models/report_manifest.py`
- `app/services/client_registry_service.py`
- `app/services/session_archive_service.py`
- `app/services/report_manifest_service.py`

Erwartetes Verhalten:
- bestehende CLI/API laufen weiter
- neue Services können parallel Metadaten erzeugen
- noch keine harte Migration alter Daten

## Phase 2 – CLI zuerst an die Services anbinden

Warum zuerst CLI?
- `dev_cli.py` ist derzeit der vollständigste echte Fachworkflow
- dort entstehen Sessionordner, Templates und Reports real
- Risiko ist geringer als direkt API + PS1 + Engine gleichzeitig anzufassen

In Phase 2 soll `dev_cli.py` zusätzlich:
- eine echte `session_id` erzeugen
- ein Session-Manifest schreiben
- exportierte Artefakte registrieren
- optional Klienten in einer Registry nachführen

Wichtig:
- bestehende Dateien (`session_templates.json`, `analysis_log.txt`, `Analysen/...`) bleiben erhalten
- Services spiegeln nur mit

## Phase 3 – API auf dieselben Domänen heben

Ziel:
- `client_id` sinnvoll machen
- API-Analysen ebenfalls als echte Session archivieren
- `/export/pdf` an gemeinsames Report-Metadatenmodell anbinden

Wichtig:
- API darf zunächst Dateisystem-basiert bleiben
- keine Datenbankpflicht in dieser Phase

Status 2026-06-04:
- umgesetzt und getestet
- `client_id` ist jetzt ein echter String-Schluessel der Runtime-Registry
- API-Analysen spiegeln Sessions in `data/runtime/sessions.json`
- PDF-Exporte koennen bei vorhandenem `session_id` im Report-Manifest registriert werden
- Response-Header fuer Verwaltungs-IDs sind verifiziert

## Phase 4 – PowerShell nur noch gegen gemeinsame Metadaten lesen

Ziel:
- `generate_matrix.ps1` liest Template-/Session-Infos aus einem stabileren Metadatenformat
- Altdateien können weiter unterstützt werden

Wichtig:
- keine vollständige PowerShell-Neuschreibung
- nur strukturierte Entkopplung

Status 2026-06-08:
- adapterartig umgesetzt und testgesichert
- PowerShell nutzt bevorzugt `data/runtime/powershell_templates.json`, das aus `data/runtime/sessions.json` und `data/runtime/clients.json` generiert wird
- Legacy-Fallback `data/session_templates.json` bleibt aktiv
- Core-Engine, Algorithmen, Report-Renderer, CLI-Vertrag und API-Routen wurden nicht veraendert
- Details: `docs/PHASE4_POWERSHELL_METADATA_STATUS_2026-06-08.md`

---

## 6. Konkrete kritische Entscheidungen vor Umsetzung

Diese Punkte sollten wir vor dem ersten Architekturpatch bewusst festlegen:

### K1 – Soll Klientenpersistenz zuerst nur dateibasiert bleiben?

Empfehlung:
Ja. Erst JSON-basiertes Registry-Modell, keine DB-Einführung in der ersten Runde.

Begründung:
- minimal-invasiv
- kompatibel mit aktuellem Projektzustand
- keine zusätzliche Betriebsabhängigkeit

### K2 – Soll `client_id` in der API sofort echt werden?

Empfehlung:
Ja, aber nur gegen ein kleines dateibasiertes Registry-Service.

Begründung:
- hebt die API semantisch auf echten Boden
- geringe Eingriffstiefe

### K3 – Soll `last_session.json` sofort ersetzt werden?

Empfehlung:
Nein.

Begründung:
- `generate_matrix.ps1` hängt daran
- zuerst Adapter bauen, später konsolidieren

### K4 – Soll `session_templates.json` sofort migriert werden?

Empfehlung:
Nein, nur lesen/schreiben über einen Service abstrahieren.

### K5 – Soll der Report-Export sofort vereinheitlicht werden?

Empfehlung:
Nur Metadaten vereinheitlichen, noch nicht alle Renderpfade zusammenlegen.

Begründung:
Die Renderlogik in CLI und API ist ähnlich, aber noch nicht gleich genug für einen risikofreien Vollmerge.

---

## 7. Präziser Task-Plan für die erste sichere Umsetzungsrunde

### Task 1: Architektur-Regressionstests für neue Verwaltungsdomäne definieren

**Objective:** Tests schreiben, die das gewünschte Metadatenverhalten beschreiben, ohne den bestehenden Workflow zu ändern.

**Files:**
- Create: `tests/test_session_archive_service.py`
- Create: `tests/test_client_registry_service.py`
- Create: `tests/test_report_manifest_service.py`

**Zu testen:**
- Session-Manifest kann aus vorhandenem Ergebnis geschrieben werden
- Report-Artefakte werden konsistent registriert
- Client-Registry vergibt stabile IDs
- bestehende Pflichtfelder bleiben vollständig

### Task 2: Reine Pydantic-Modelle für Client, Session und Report einführen

**Objective:** Stabile Schema-Grundlage schaffen.

**Files:**
- Create: `app/models/client_registry.py`
- Create: `app/models/session_archive.py`
- Create: `app/models/report_manifest.py`

### Task 3: Dateibasierte Services mit atomarem JSON-Schreiben ergänzen

**Objective:** Die Modelle über sichere Services persistierbar machen.

**Files:**
- Create: `app/services/json_store.py`
- Create: `app/services/client_registry_service.py`
- Create: `app/services/session_archive_service.py`
- Create: `app/services/report_manifest_service.py`

### Task 4: `dev_cli.py` nur spiegelnd anbinden

**Objective:** Echte Session-Metadaten erzeugen, ohne den Kernablauf zu ändern.

**Files:**
- Modify: `dev_cli.py`
- Test: `tests/test_dev_cli_archive_integration.py`

**Spiegelnde Daten:**
- erzeugte `session_id`
- Client-Metadaten
- Fokus/Fokusliste
- Exportpfade
- Harmonize-Status

### Task 5: API schrittweise anbinden

**Objective:** `client_id` und PDF-Export an die gemeinsame Metadatenstruktur anschließen.

**Files:**
- Modify: `app/api/resonance.py`
- Test: `tests/test_api_archive_integration.py`

### Task 6: Dokumentation aktualisieren

**Objective:** Neue Architekturwahrheit sauber dokumentieren.

**Files:**
- Modify: `README.md`
- Modify: `docs/RADI144_TIEFENANALYSE_2026-06-03.md`
- Modify: `docs/SYSTEM_ARCHITECTURE_FLOW.md`

Status 2026-06-04:
- in Arbeit bzw. teilweise nachgezogen; die Codebasis ist hier die primaere Wahrheit, diese Datei dokumentiert nun den verifizierten Umsetzungsstand mit

---

## 8. Was in der ersten Runde ausdrücklich NICHT angefasst werden soll

- keine Änderung am Resonanz-Scoring
- keine Änderung am EMF-Kompensationsalgorithmus
- keine Änderung an Top-10-/Top-3-Selektion
- keine Änderung an Audio-Synthese oder Harmonizer-Timing
- keine erzwungene Datenbankeinführung
- keine PowerShell-Komplettmigration

---

## 9. Meine Empfehlung für die nächste tatsächliche Umsetzung

Die erste echte Implementierungsrunde sollte nur Folgendes tun:

1. neue Modelle
2. neue dateibasierte Services
3. spiegelnde CLI-Anbindung
4. Tests

Das ist der kleinste sinnvolle Schnitt mit hoher Stabilitätswahrscheinlichkeit.

---

## 10. Freigabeempfehlung

Empfohlener nächster aktiver Umsetzungsschritt:

- Phase 1 + Task 1-3
- optional direkt Task 4 (`dev_cli.py` spiegelnd anbinden)

Nicht empfohlen ohne gesonderte Besprechung:

- sofortige API-Umbauten mit echter `client_id`-Auflösung
- sofortige PowerShell-Migration
- Zusammenlegung aller Report-Renderer in einem Schritt
