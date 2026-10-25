# 01 - Executive Summary

## 1. Gesamtbewertung

Radi144 verfolgt laut Projektziel zwei Rollen: ein eigenständig nutzbares Standalone-System und ein späteres Referenz-/Informationsmodul für ein übergeordnetes Wellbeing-/Radiquant-System (`docs/RADI144_PROJECT_INTENT_2026-06-06.md:5-32`). Der aktuelle Code deckt dafür bereits ungewöhnlich viele Funktionsbereiche ab:

- FastAPI-Backend,
- Browserworkflow,
- PowerShell-Wizard,
- Python-CLI,
- 12x12-, 24x24- und teilweise 36x36-Matrixpfade,
- PDF-, XLSX-, CSV-, JSON- und Audioausgaben,
- Klienten-, Session- und Artefaktverwaltung,
- EMF-, Bio-, Amplifier- und Harmonizerfunktionen,
- optionaler SQLite-Interchange-Bus,
- Safety-Projektionen und Löschmanifest.

Diese Funktionsbreite ist jedoch nicht mit Produktionsreife gleichzusetzen. Die tragenden Sicherheits-, Datenintegritäts-, Reproduzierbarkeits-, Release- und Evidenzeigenschaften fehlen oder sind nur teilweise umgesetzt.

### Freigabeurteil nach Einsatzart

| Einsatzart | Urteil | Begründung |
|---|---|---|
| Isolierte lokale Entwicklung mit Testdaten | **Bedingt möglich** | Loopback-Start und breite Funktionalität vorhanden; Engine- und Speichergrenzen beachten |
| Lokaler Einbenutzerbetrieb mit realen Klientendaten | **Nur nach Datenschutz- und Betriebshärtung** | Klartext-PII, LocalStorage, unvollständige Löschung/Backups, keine Retention |
| LAN-/Serverbetrieb | **NO-GO** | Authentisierung, Pfadsandbox, WebSocket-Schutz, Transaktionen und Workloadgrenzen fehlen |
| Öffentlich erreichbarer Betrieb | **NO-GO / P0** | lokal vorgefundenes Profil: `0.0.0.0`, vier Worker, CORS `*`, leerer API-Key |
| Mehrbenutzer-/Mandantenbetrieb | **NO-GO** | keine Rollen, Mandantenbindung, Objektberechtigung oder sichere gemeinsame Persistenz |
| Medizinischer/therapeutischer Einsatz | **NO-GO** | keine klinische Evidenz, nicht kalibrierter Zufallsscore, gesundheitsbezogene Claims |
| Externe Distribution/Veröffentlichung | **NO-GO bis Lizenzklärung** | keine Projektlizenz/SBOM; Herkunft und Weitergaberecht der Referenzdaten ungeklärt |

## 2. Was bereits positiv ist

### 2.1 Technische Stärken

1. **Erkennbare Schichten:** API, Schemas, Algorithmen, Modelle und Services sind getrennte Pakete.
2. **Runtime-Preflight:** Core-, API- und CLI-Profile prüfen das Vorhandensein zentraler Module (`app/bootstrap.py:19-35`, `:62-80`).
3. **Typisierte API-Grenzen:** Die Hauptrequests und -responses sind mit Pydantic modelliert.
4. **Sicherer Direktstart-Default:** `python main.py` bindet standardmäßig an `127.0.0.1:8090` (`main.py:124-142`).
5. **CORS-Verbesserung im Arbeitsbaum:** Ohne Env-Konfiguration sind nur Loopback-Origins zugelassen (`main.py:42-57`).
6. **Atomarer Einzeldatei-Austausch:** `JsonStore` schreibt temporär und ersetzt die Zieldatei mit `os.replace` (`app/services/json_store.py:27-36`).
7. **Speicherschutzabsicht:** Kandidaten werden anhand physischen freien Speichers reduziert (`app/algorithms/resonance_engine.py:999-1029`).
8. **Temporärdatei-Cleanup:** Base64-Bilddateien werden im `finally` gelöscht (`app/api/resonance.py:319-391`).
9. **Safety-Bausteine:** API-Responses und API-PDFs enthalten einen zentralen Nicht-Medizin-Hinweis (`app/services/safety_service.py:21-44`; `app/api/resonance.py:847-860`).
10. **PII-reduzierte Listenansicht:** Direkte Identitätsfelder werden aus der Clientliste entfernt (`app/services/safety_service.py:49-64`).
11. **Löschmanifest:** Vor der Löschung ist eine nicht-destruktive Vorschau vorgesehen (`app/services/erasure_service.py:103-131`).
12. **SQLite-Bus mit WAL:** Der optionale Bus nutzt WAL, JSON-Constraints und parametrisierte SQL-Zugriffe (`app/interchange_bus/consumer_store.py:23-105`).
13. **Breite Testsammlung:** 92 Tests wurden aktuell gesammelt; 83 Nicht-Engine-Tests bestehen im geprüften Stand.

### 2.2 Organisatorische Stärken

- Die bestehende Dokumentation benennt bereits mehrere Daten-, Restore- und Lizenzrisiken.
- Runtime-, Analyse-, Secret- und Sessionpfade werden überwiegend aus Git ausgeschlossen (`.gitignore:15-30`).
- Historische Restore- und Diagnosewerkzeuge werden nicht mehr als aktuelle Baseline behandelt.
- Das Projektziel fordert phase-gated, testbare und rückwärtsverträgliche Änderungen (`docs/RADI144_PROJECT_INTENT_2026-06-06.md:23-32`).

## 3. Wichtigste Produktionsblocker

### 3.1 Sicherheit

1. **Effektive lokale Serverkonfiguration ist offen:** `APP_HOST=0.0.0.0`, `APP_WORKERS=4`, `CORS_ORIGINS=*`, `API_KEY=` im ignorierten lokalen `deploy/server.env`.
2. **Authentisierung ist fail-open:** Leerer oder Placeholder-Key deaktiviert das Gate (`main.py:87-98`).
3. **API-Key und Browser-UI sind inkompatibel:** Bei aktivem Key blockiert die Middleware auch HTML/CSS/JS; die UI sendet keinen `x-api-key` (`main.py:94-107`; `user_workflow.js:1042-1046`).
4. **WebSockets sind ungeschützt:** Beide EMF-WebSockets akzeptieren sofort, ohne Token, Origin- oder Mandantenprüfung (`app/api/resonance.py:1072-1138`).
5. **Dateipfade sind nicht sandboxed:** `db_path`/`image_path` können beliebige vorhandene Dateien referenzieren; `output_path` kann beliebige beschreibbare Ziele überschreiben (`app/api/resonance.py:128-135`, `:212-228`, `:642-693`, `:864-874`).
6. **Löschgate hat bekannten Default:** Ohne Env-Secret gilt der Quelltextwert `R144_ERASURE_ACKNOWLEDGED`; das Token wird als Queryparameter übertragen (`app/services/erasure_service.py:30-35`; `app/api/clients.py:94-108`).
7. **Browser-DOM-XSS:** Mehrere Nutzer-, LocalStorage- und API-Werte fließen ungeescaped in `innerHTML` (`user_workflow.js:820-862`, `:1207-1238`, `:2323-2340`).
8. **PowerShell-Command-Injection:** Nutzereingaben werden zu Befehlsstrings kombiniert und mit `Invoke-Expression` ausgeführt (`generate_matrix.ps1:999-1034`).

### 3.2 Datenintegrität und Datenschutz

1. **Vier Worker plus JSON-Read-Modify-Replace:** Parallele Writes können sich gegenseitig verlieren; `os.replace` schützt nur vor Teilwrites, nicht vor Lost Updates.
2. **Mehrdateioperationen sind nicht transaktional:** Client, Session, Artefakt, Datei und Audit können auseinanderlaufen.
3. **Löschung ist nicht wiederanlaufsicher:** Der Client wird vor Sessions und Dateien entfernt; ein Teilausfall erschwert den Retry (`app/services/erasure_service.py:178-233`).
4. **Klartext-PII:** Namen, Geburtsdaten, Orte, Fokus und Metadaten liegen in JSON, Reports, Logs und Browser-LocalStorage.
5. **Unvollständige Löschung:** Browserdaten, Downloads, Legacy-Dateien, Logs, Backups, Busdaten und Git-Historie werden nicht vollständig erreicht.
6. **Keine Retention:** Clients, Sessions, Artefakte, Audit und Analyseausgaben wachsen ohne zeitbasierte Löschregel.
7. **Personenbezogene Dateien sind getrackt:** `Ha und De v1.json` und `HA und DE v2.json` enthalten identitätsbezogene Daten und sind Teil des Git-Objektbestands.

### 3.3 Fachliche und algorithmische Verlässlichkeit

1. **Kein trainiertes KI-Modell:** Client- und Fokus-„Embeddings“ sind MD5-seedete `torch.randn(256)`-Vektoren (`resonance_engine.py:1157-1187`).
2. **Score ohne validierte Bedeutung:** Er ist Kosinusähnlichkeit in einer zufälligen, nicht trainierten Projektion und keine Wahrscheinlichkeit, Diagnose oder Wirksamkeit.
3. **Nur Zufallsstichprobe:** Der Code bewertet 80.000 bis 1.000.000 Kandidaten, nicht den Raum von `10^144` vollständig (`resonance_engine.py:57-92`, `:1045-1092`).
4. **Score passt nach Symmetrie nicht zur Ausgabe:** Matrix wird nach dem Scoring verändert, Score und Intensität bleiben unverändert (`resonance_engine.py:415-433`).
5. **Precision ist nicht vollständig reproduzierbar:** Organuhr, HRV, EMF, Hardware, freier Speicher, CUDA/TF32 und Bildtempnamen können Ergebnisse verändern.
6. **DB-Rankings sind nicht sauber vergleichbar:** Für jeden Fokus/Eintrag werden Seed, Kandidaten und Zufallsprojektion verändert.
7. **Quantum/D-Wave ist ein Mock:** Refinement ist `pass`, D-Wave gibt die Eingangsmatrix zurück (`resonance_engine.py:1113-1155`).
8. **Wirkungslose API-Felder:** `iterations`, `use_quantum` und `use_cuda` werden archiviert, aber nicht an die Berechnung übergeben (`app/schemas/resonance.py:12-17`; `app/api/resonance.py:441-452`).
9. **EMF ist überwiegend Systemrauschprofil:** Gemessen werden CPU-Timing, Betriebssystemzufall, Systemlast und GPU-Laufzeiten, nicht standardmäßig ein elektromagnetisches Feld (`emf_compensator.py:132-355`, `:388-456`).

### 3.4 Betrieb und Release

1. Keine CI/CD-Pipeline, keine Coverage-Gates, kein Lint-/Type-Gate.
2. Kein `pyproject.toml`, kein Package, kein Lockfile, keine Hashes.
3. Keine Projektlizenz, keine Third-Party-Notices, keine SBOM.
4. Deployment kopiert einen beliebigen Entwicklerarbeitsbaum statt eines freigegebenen Artefakts.
5. `deploy/server.env` ist in Clean-Checkout nicht vorhanden, wird aber von systemd zwingend verlangt.
6. Kein belastbarer Health-/Readiness-Endpunkt, Monitoring, Alerting oder Logrotation.
7. Kein aktueller, getesteter Backup-/Restore-, Upgrade- oder Rollbackprozess.
8. Dokumentation driftet bei Port, Version, D-Wave, Testzahlen und Produktstatus.

## 4. Aktueller Verifikationsstand

Prüfumgebung:

- Windows
- Python 3.11.12
- pytest 9.0.3
- NumPy 2.4.6
- Torch 2.12.0

Ergebnisse:

| Prüfung | Ergebnis |
|---|---|
| Test-Collection ohne Threadlimit | fehlgeschlagen: OpenBLAS kann wegen erschöpftem Commit-/Auslagerungsspeicher nicht allokieren |
| Test-Collection mit `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1` | 92 Tests gesammelt |
| Nicht-Engine-Suite | **83 bestanden**, 30 `httpx`-DeprecationWarnings |
| Vier leichte Engine-Tests | **4 bestanden** |
| Vollständige Suite | **nicht bestanden** |
| Erster realer Engine-Test | `RuntimeError`: 85.684.224 Byte konnten nicht allokiert werden (`resonance_engine.py:1089`) |
| Folgender realer Engine-Test | nativer Windows-Abbruch: Access Violation in `resonance_engine.py:1089` |
| Manuelles Engine-Smoke mit 1.000 Kandidaten | 12x12-Matrix und Scorebereich erfolgreich |
| JavaScript-Syntax | `node --check user_workflow.js` erfolgreich |
| PowerShell-Syntax | Parser erfolgreich |
| Python-Abhängigkeiten | `pip check`: keine gebrochenen Anforderungen |

Das beweist zweierlei:

1. Ein großer Teil der Service-, API-, Daten- und Strukturtests ist aktuell stabil.
2. Die reale Engine ist unter dem aktuellen Systemzustand nicht robust gegen begrenzten virtuellen Speicher; die Testsuite ist daher kein aktueller grüner Releasebeleg.

## 5. Reifegrad

Skala: 0 = nicht vorhanden, 1 = ad hoc, 2 = Entwicklungsbetrieb, 3 = Vorproduktion, 4 = belastbare Produktion.

| Bereich | Reifegrad | Kurzbegründung |
|---|---:|---|
| Lokale Funktionsbreite | 2,5 | Viele funktionale Pfade und Exporte |
| Architekturtrennung | 2,0 | Pakete getrennt, zentrale Module dennoch monolithisch |
| Algorithmische Reproduzierbarkeit | 1,0 | Teilweiser Precision-Seed, viele externe Zustände |
| Wissenschaftliche/Fachvalidierung | 0,2 | Keine Ground Truth, Kalibration oder Outcome-Evidenz |
| API-Vertragsqualität | 1,4 | Pydantic vorhanden, wichtige Grenzen und Semantik fehlen |
| Testarchitektur | 1,8 | 92 Tests, aber keine grüne Vollsuite/Coverage/E2E/Lasttests |
| Security | 0,5 | Teilkontrollen vorhanden, mehrere kritische Angriffspfade |
| Datenschutz | 0,6 | Safe-View und Löschung angelegt, Gesamtlebenszyklus unvollständig |
| Persistenz | 0,8 | Atomare Einzelwrites, keine Transaktionen/Locks/Migrationen |
| Deployment | 0,8 | systemd-Skript vorhanden, aber nicht reproduzierbar/sicher |
| Observability | 0,5 | Basislogging, keine Health-, Metrik- oder Alarmkette |
| Backup/Restore | 0,5 | Historische Ansätze, kein aktueller geprüfter Prozess |
| Release/Supply Chain | 0,2 | kein Artefakt, Lock, CI, Lizenz oder SBOM |
| Dokumentationsqualität | 1,6 | Umfangreich, aber widersprüchlich und teilweise claim-getrieben |

**Gesamteinschätzung:** etwa **1,1 von 4**, also Entwicklungsprototyp mit substanzieller Vorarbeit.

## 6. Entscheidungsempfehlung

Vor einer weiteren Featureausweitung sollten fünf Grundlagenblöcke priorisiert werden:

1. **Exposition schließen:** Zugriffsschutz, Pfadsandbox, WebSocket-Auth, Limits.
2. **Datenbasis sichern:** Transaktionen, Migrationen, Retention, vollständige Löschung, Backup/Restore.
3. **Engine-Vertrag ehrlich machen:** deterministische Rechenbasis, Scoredefinition, Mock-/No-op-Funktionen und Claims bereinigen.
4. **Betriebsfähigkeit herstellen:** reproduzierbares Artefakt, CI, Lockfiles, Health, Logs, Monitoring, Rollback.
5. **Zweck und Regulierung klären:** Wellness-/Kunstgenerator versus medizinische Zweckbestimmung; Claims und Datenverarbeitung daran ausrichten.

Diese Reihenfolge ist noch kein Implementierungsplan. Sie ist die fachliche Voraussetzung, auf deren Basis anschließend ein realistischer, risikoabhängiger Plan erstellt werden kann.
