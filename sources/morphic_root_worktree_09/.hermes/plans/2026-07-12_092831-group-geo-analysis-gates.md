# Gruppen- und Geo-Analysewirkung – Freigabeplan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Gruppen- und Geo-Vektoren später als echte, ausdrücklich opt-in-basierte Analysewirkung ergänzen, ohne die Standardanalyse oder bestehende Datenschutzgrenzen zu regressieren.

**Architecture:** Der bestehende Klientvektor bleibt die unveränderte Baseline. Gruppe und Geo werden zuerst als reine, deterministische Kandidatenvektoren außerhalb der produktiven Scanpfade erzeugt. Erst nach je einem getrennten Default-Äquivalenz-, synthetischen Opt-in-, Privacy-/Redaktions- und Browser-Gate darf ein einziger Vektor über einen expliziten Schalter in `AnalysisService.encode_profile()` wirken.

**Tech Stack:** Python 3.12, NumPy, Pydantic v2, FastAPI, bestehender `ClientProfile`/`RateEncoder`/`AnalysisService`-Kern, Windows-DPAPI nur für lokale Entwürfe.

---

## Codebasierter Ausgangsbefund

- Der aktuelle Kern erzeugt einen zehnwertigen Baseline-Ratenvektor aus Name (3), Geburtsdatum (1), Geburtsort (1), Bild (4; ohne Bild deterministischer 32×32-Einsen-Default) und Planet (1): `services/analysis_service.py:27-42`.
- `ClientProfile` besitzt heute nur `image_signature`, `personal_profile` und `planet_type`: `core/profiles/profile.py:183-192`.
- Die produktive Feldroute baut genau dieses Profil in `apps/cli/commands/field.py:2936-2947`; Web-Preview und Web-Job starten ausschließlich über `Phase1ScanRequest`/Launcher (`apps/web/main.py:497-554`).
- Der historische V1-Code kennt Gruppen als Trend-/Reporting-Relation mit Klartext-Mitgliedsnamen und gemeinsamen historischen Scan-Items, nicht als Encoder oder Scoringvektor (`C:\Users\Hubert111\Documents\Radimorphic\Morphic_Engine_V1\tools\trend_analyzer.py:137-156`, `372-408`). Diese Struktur darf nicht übernommen werden.
- Im V1-Referenzcode wurde keine geografische Koordinaten-/Radius-Encoderformel gefunden. `mf_geometry` ist eine symbolische morphische Feldform, keine Geolokation (`...\apps\cli\main_backup_20251219_remedy_fix.py:5140-5146`).
- Daher existiert keine historische Formel, die unkritisch migriert werden könnte. Eine Wirkung muss als neue, versionierte und explizit freigegebene Semantik behandelt werden.

## Nicht verhandelbare Invarianten

1. Ohne Gruppen- oder Geo-Opt-in bleibt der resultierende Ratenvektor bitgleich zur heutigen Baseline.
2. Ein Gruppenvektor darf keine Klartextnamen, E-Mails, Geburtsdaten oder historischen Reports persistieren oder in Trace/Manifest/Report ausgeben.
3. Ein Geovektor darf nie Browser-Geolocation, Geocoding, Netzwerkzugriff oder automatische Standortermittlung auslösen.
4. Rohkoordinaten, Radius, Gruppenbezeichnung und Mitgliedsreferenzen bleiben aus Scan-Request, CLI-Argumenten, Joblogs, Run-Traces, Reports und Manifests ausgeschlossen.
5. Ein späterer Vektor darf nicht beide Wirkungen zugleich aktivieren: Gruppe und Geo erhalten separate Releases und separate Rollback-Schalter.
6. Keine medizinische Aussage oder Therapieempfehlung entsteht aus einem Vektor.

---

### Task 1: Baseline-Fingerprint vor jeder Wirkungsarbeit festschreiben

**Objective:** Den heutigen Klientvektor und alle Kernmetriken als unveränderliche Referenz sichern.

**Files:**
- Modify: `tests/test_analysis_equivalence.py`
- Create: `tests/test_group_geo_default_equivalence.py`
- Read only: `services/analysis_service.py:27-42`, `core/resonance/resonator.py:17-56`

**Step 1: Write failing tests**

- Erzeuge ein festes synthetisches `ClientProfile` ohne Bild und ohne künftige Vektoren.
- Sichere exakt: `rates`, `morphic_field`, `holographic_entropy`, `heim_signature` und eine kleine synthetische `resonance_map`.
- Erzeuge künftige Group-/Geo-Opt-in-Objekte mit `enabled=False` und erwarte exakt dieselben Werte.

**Step 2: Run the tests to verify failure**

Run:
```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests/test_group_geo_default_equivalence.py -q
```

Expected: FAIL because the explicit disabled-vector contract does not exist yet.

**Step 3: Implement minimal default behavior**

- Ergänze noch keine Formel und keine Analysewirkung.
- Die neue Vektor-Konfiguration muss `enabled=False` als Default haben und in diesem Zustand keinen bestehenden Array-Wert verändern.

**Step 4: Verify**

Run the focused test. Expected: PASS with bitgleicher Baseline.

---

### Task 2: Gruppen-Centroid als reine, pseudonyme Kandidatensignatur erzeugen

**Objective:** Einen determinierten Gruppen-Centroid aus bereits im Speicher vorliegenden Mitgliedsraten erzeugen, ohne ihn zu scoren oder zu persistieren.

**Files:**
- Create: `core/profiles/group_vector.py`
- Create: `tests/test_group_vector.py`
- Do not modify yet: `services/analysis_service.py`, `apps/web/*`, `apps/cli/*`

**Contract:**

- Input: mindestens zwei gleichlange, bereits erzeugte Mitglieds-Ratenarrays plus ausschließlich pseudonyme `cli-...`-Referenzen für Audit-/Einwilligungsprüfung.
- Output: arithmetischer NumPy-Centroid gleicher Länge wie die Mitgliedsraten.
- Determinismus: gleiche Eingaben ergeben bytegleiche Float-Ausgabe; Eingabereihenfolge ändert das Ergebnis nicht.
- Fail closed: leere Liste, nur ein Mitglied, ungleiche Arraylänge, NaN/Inf oder fehlende Mitgliedseinwilligung führen zu `ValueError`.
- Kein Schreiben auf Disk, keine Reports, keine Scan-/Score-Anbindung.

**Step 1: Write failing tests**

- Prüfe Centroid-Werte mit zwei kurzen synthetischen Arrays.
- Prüfe Permutationsinvarianz.
- Prüfe die fünf Fail-closed-Fälle.
- Prüfe, dass das Produktivmodul `AnalysisService` den Kandidaten nicht importiert.

**Step 2: Run the focused test and confirm RED.**

**Step 3: Implement only the pure helper.**

**Step 4: Run focused tests and the full suite.**

**Decision gate:** Der Centroid ist ein technisch definierter Kandidat, aber noch keine Wirkung. Seine spätere Kombination mit dem Klientvektor benötigt eine eigene Freigabe.

---

### Task 3: Geo-Kanonisierung als reine, manuelle Kandidatensignatur untersuchen

**Objective:** Eine lokale, netzwerkfreie und manuell eingegebene Geo-Signatur definieren, ohne sie an die Analyse anzuschließen.

**Files:**
- Create: `core/profiles/geo_vector.py`
- Create: `tests/test_geo_vector.py`
- Reuse: `apps/web/client_context_contracts.py:57-82`

**Required policy decision before implementation:**

Es gibt keine historische Geo-Encoderformel. Vor einer späteren Wirkung muss die fachliche Semantik explizit festgelegt werden. Empfohlener technische Kandidat zur Diskussion:

- Keine Rohkoordinaten in einen Report oder ein Manifest.
- Nur manuelle Eingabe, `source="manual"`.
- Eine kanonische, versionierte lokale Geo-Zelle aus Koordinatenpräzision und Radiusklasse; keine externe Karte und kein Geocoding.
- Der Kandidat muss eine feste Versionskennung tragen, z. B. `geo-v1`; ein Wechsel der Formel erzeugt `geo-v2`, niemals stilles Umschreiben alter Entwürfe.

**Step 1: Write failing tests**

- Gleiche Eingaben → gleicher Kandidat.
- Gleiche Koordinaten mit anderer Präzision/Radiusschicht → definierter anderer Kandidat.
- Browserquelle, NaN/Inf, ungültige Grenzen und unbekannte Version → Fehler.
- Kandidat enthält keine Klartext-Ortsbezeichnung.

**Step 2: Run RED.**

**Step 3: Implement only die kanonische Kandidaterzeugung; keine `AnalysisService`-Änderung.**

**Step 4: Run focused tests and full suite.**

**Decision gate:** Vor einer Score-Wirkung muss der Nutzer die Geo-Semantik sowie die zulässige räumliche Auflösung ausdrücklich bestätigen. Ohne diese Freigabe bleibt der Kandidat wirkungslos.

---

### Task 4: Je Vektor eine explizite, rückwärtskompatible Analysekombination einführen

**Objective:** Nach den separaten Kandidaten-Gates genau einen opt-in Vektor in die Analyse einführen, ohne den Default zu verändern.

**Files:**
- Modify: `core/profiles/profile.py:183-192`
- Modify: `services/analysis_service.py:27-42`
- Create: `tests/test_group_analysis_opt_in.py` oder `tests/test_geo_analysis_opt_in.py`
- Modify later, never together initially: `apps/cli/commands/field.py:2936-2947`, `apps/web/contracts.py`, `apps/web/launcher.py`, `apps/web/static/app.js`

**Implementation rule:**

- Zuerst Gruppe **oder** Geo, niemals beide im selben Release.
- Die Kombinationsmethode und Gewichtung werden erst nach Task 2 bzw. 3 festgelegt. Keine implizite Formel, keine versteckte Default-Gewichtung.
- Der entsprechende Opt-in-Schalter muss standardmäßig `False` sein.
- `enabled=False` muss die Task-1-Fingerprinttests exakt erfüllen.
- `enabled=True` muss mit ausschließlich synthetischen Daten einen nachweisbar anderen Ratenvektor und eine andere Analyse liefern.

**Mandatory tests:**

1. Default-Äquivalenz: alt = neu bei deaktiviertem Vektor.
2. Determinismus: gleicher synthetischer Opt-in → gleiche Raten und Ergebnisse.
3. Wirkung: aktivierter synthetischer Vektor verändert Raten und mindestens eine Analysemetrik.
4. Isolation: ein Gruppen-Opt-in ändert nicht Geo und umgekehrt.
5. Fail closed: ungültiger Kandidat führt zum unveränderten Default oder zu explizitem Fehler vor dem Jobstart, nie zu einer stillen Teilwirkung.

---

### Task 5: Privacy- und Redaktions-Gate vor jeder Web-/CLI-Anbindung

**Objective:** Sicherstellen, dass nur ein boolescher Aktivierungszustand und eine versionsierte, nicht rückrechenbare Kennung sichtbar werden dürfen.

**Files:**
- Modify: `apps/web/contracts.py`
- Modify: `apps/web/main.py:149-187`
- Modify: `apps/web/workbench.py:15-38`
- Modify: `core/compliance/run_manifest.py`
- Create: `tests/test_group_geo_privacy_redaction.py`
- Extend: `tests/test_web_workbench_runtime.py`, `tests/test_web_launcher.py`, `tests/test_local_vector_draft_integration_boundary.py`

**Tests:**

- Request/Launcher enthalten keine Rohkoordinaten, Radius, Gruppenbezeichnung oder Mitgliederliste.
- Run-Trace enthält maximal `group_enabled`/`geo_enabled` und eine zugelassene Versionskennung; niemals den Kandidatenrohwert.
- Report/Manifest/Joblog enthalten keine verbotenen Rohfelder.
- Fehlende Einwilligung verhindert die Persistenz und die Aktivierung.
- Erasure-Dry-Run erkennt den lokalen Entwurf; Produktivdaten werden erst nach einer separaten, expliziten Speicherklassenerweiterung berücksichtigt.

---

### Task 6: Browser-Gate und schrittweise Freigabe

**Objective:** Erst nach Backend-/Privacy-Gates eine minimalistische UI bereitstellen.

**Files:**
- Modify: `apps/web/static/index.html`
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/static/app.css`
- Extend: `tests/test_workbench_client_context_dom.py`
- Extend: `tests/test_local_vector_draft_integration_boundary.py`

**Requirements:**

- Gruppe und Geo bleiben getrennte Karten/Flows.
- Je Vektor eigener Einwilligungstext, eigener Aktivierungsschalter und klarer Hinweis auf lokale Verarbeitung.
- Keine automatische Standortabfrage; bestehende `Permissions-Policy: geolocation=()` bleibt unverändert.
- Deaktiviert bedeutet sichtbar „nicht in Analyse einbezogen“ und muss technisch den Default-Äquivalenztest erfüllen.
- Browser-Abnahme nur auf freiem Port; Port 8000 und 8090 bleiben unangetastet; Desktop und 320px ohne horizontalen Overflow prüfen.

---

## Abnahme-Reihenfolge

1. Gruppen-Kandidat rein und deterministisch.
2. Gruppen-Default-Äquivalenz und synthetische Opt-in-Wirkung.
3. Gruppen-Privacy/Redaction und Browser-Gate.
4. Erst danach Geo-Kandidat mit explizit bestätigter Formel-/Präzisionssemantik.
5. Geo-Default-Äquivalenz und synthetische Opt-in-Wirkung.
6. Geo-Privacy/Redaction und Browser-Gate.
7. Erst nach beiden Einzelabnahmen eine mögliche kombinierte Gruppen+Geo-Analyse planen.

## Risks and required decisions

- **Keine vorhandene V1-Geo-Formel:** Eine neue Geo-Wirkung wäre neue Fachlogik. Sie darf nicht als historische Parität bezeichnet werden.
- **Keine vorhandene V1-Gruppen-Encoderlogik:** V1-Gruppen sind Klartext-Trend-/Reportingdaten und deshalb keine übernehmbare Vorlage.
- **Kombinationsgewichtung:** Die Wirkung eines Kandidaten auf den Baseline-Ratenvektor ist eine explizite fachliche Entscheidung. Sie darf nicht still über Array-Konkatenation oder Mittelwertverschiebung entstehen.
- **Aufbewahrung:** Die aktuelle E4.2–E4.5-Temp-DPAPI-Ablage ist ein isolierter Feasibility-Gate. Eine produktive Ablage benötigt einen separat freigegebenen Speicherort, Tenant-/Owner-Bindung, Retention, Erasure-Abdeckung und einen unabhängigen Review.
- **Commit:** Kein Commit oder Push ohne aktuelle, ausdrückliche Nutzerfreigabe.
