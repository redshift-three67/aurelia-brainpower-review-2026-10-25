# RadiWorks Datenbanksuche und Fallfokus — Implementation Plan

> **For agentic workers:** Execute with source isolation, failing targeted tests before implementation, and review at the integration boundary.

**Goal:** Eine lokale Datenbanksuche und einen getrennten Fallfokus als ausdrückliche Auswahlhilfe bereitstellen, ohne Analyselogik oder den laufenden 8103-Dienst zu ändern.

**Architecture:** Änderungen zuerst in einer Kopie des aktuellen RadiWorks-Kandidaten. Die Suchansicht filtert nur die vorhandene Katalogantwort im Browser. Fallfokus wird über die bestehenden Fall- und Metadatenpfade gespeichert und in neue Drafts kopiert; Fallverweise verhindern veraltetes Speichern.

**Tech Stack:** FastAPI/Pydantic, Python-Fallstore, Vanilla JS/HTML/CSS, pytest, bestehender synthetischer Chrome-Smoke.

---

### Task 1: Isolierter Stand und rote Tests

**Files:** `engine/tests/test_public_copyguard.py`, `engine/tests/test_p3_api.py`, `engine/tools/browser_smoke/smoke.mjs` in der isolierten Kopie.

- [x] Laufenden 8103-Zustand lesend prüfen und die Kandidatenquellen in einen neuen Workspace-Ordner kopieren.
- [x] Synthetischen API-Test für Fallfokus, Draft-Snapshot und veralteten Fallverweis schreiben; gezielt rot laufen lassen.
- [x] Browserprobe für Suchfilter und ausdrückliche Fokusübernahme ergänzen; rot laufen lassen.

### Task 2: Fokus ohne Recheneinfluss

**Files:** `engine/src/radiworks/api/routes.py`, `webapp/index.html`, `webapp/js/views/cases.js`, `webapp/js/views/analyze.js`.

- [x] Optionales Fokusfeld mit begrenzter Länge im gezielten Metadatenpfad und im Fallformular ergänzen. Bestehende Falldokumente bleiben gültig.
- [x] Opaken erwarteten Fallverweis bei der Formularspeicherung vergleichen; bei Fallwechsel 409 melden.
- [x] Fokus nur in den neuen Draft-Snapshot aufnehmen; Analyserequest und Ergebnisfunktion unverändert lassen.
- [x] Gezielt rote Tests grün laufen lassen.

### Task 3: Katalogsuche und Regression

**Files:** `webapp/index.html`, `webapp/js/views/analyze.js`, gegebenenfalls `webapp/css/app.css`.

- [x] Lokales Suchfeld mit sichtbarer Trefferzahl, Rücksetzen und bewusster Fokusübernahme ergänzen. Auswahlwechsel erfolgt nur nach expliziter Auswahl.
- [x] Suchfilter mit Gruppen, leerem Ergebnis, Keyboard und 320/390-px-Ansicht prüfen.
- [x] Vollständige Engine-Suite, JS-Syntax und synthetischen Browser-Smoke laufen lassen; Fehler vor Abschluss beheben.

### Task 4: Kontrollierte Übernahme

- [x] Änderungen und Nachweise dokumentieren; Hash-Abgleich zum RadiWorks-Quellordner und Modul-Templates vorbereiten.
- [x] Port 8103 und virtuelle Queue erneut lesen. Bei aktiven Aufträgen keine Übernahme oder Neustart.
- [x] Nach leerer Queue Programmdateien hashgeprüft in Quelle und 8103-Kandidaten übernehmen; Vorschauzustand sichern, mit bestehendem lokalem Scope neu starten und Fall-/Draftbestand sowie Suche/Fokus lesend prüfen.
- [ ] Betreiberprobe mit erneut geladenem gespeichertem Fall für Fallfokus und Datenbanksuche durchführen; S4-Status nur mit belegten Ergebnissen ändern.
