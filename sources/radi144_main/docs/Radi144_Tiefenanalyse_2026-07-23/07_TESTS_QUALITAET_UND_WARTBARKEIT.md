# 07 - Tests, Qualität und Wartbarkeit

## 1. Testinventar

Der aktuelle Arbeitsbaum enthält:

- 22 `test_*.py`-Module,
- 92 von pytest gesammelte Tests inklusive Parametrisierungen,
- Unit-/Komponenten-, API-, Dateisystem-, SQLite- und Charakterisierungstests,
- keine explizite Trennung über Marker in Unit, Integration, E2E, Performance oder Security.

`pytest.ini` enthält nur Testpfad, Ausschlussverzeichnisse und `-ra` (`pytest.ini:1-4`).

### 1.1 Vorhandene Testbereiche

| Bereich | Beispiele |
|---|---|
| Engine | Smoke, Precision-Seed, RNG-Restore, Memory Guard, Paletten, Bio-Erkennung |
| API | TestClient-Kompatibilität, API-Key, Vektormodi, Archiv/PDF |
| Persistenz | Client Registry, Sessions, Artefaktmanifest, Löschung |
| Datenschutz/Safety | PII-Projektionen, Safety-Block, PDF-Disclaimer |
| Bus | Schema, Poll, Cursor, ACK, Tamper, Safety, Topicwerte |
| CLI | Archivspiegelung |
| Frontend | Quelltext-/String-/CSS-Charakterisierung |
| PowerShell | Metadatenadapter und Quelltextmerkmale |
| Repository | Ignore-/Datenhygiene und Referenzdatenanzahl |

## 2. Aktuelle Verifikation

### 2.1 Prüfumgebung

| Komponente | Version/Stand |
|---|---|
| Plattform | Windows |
| Python | 3.11.12 |
| pytest | 9.0.3 |
| NumPy | 2.4.6 |
| Torch | 2.12.0 |
| Branch | `fix/r144-frontend-synergy` |
| HEAD | `9649e9b` |

### 2.2 Ausgeführte Prüfungen

#### Vollständige Collection ohne BLAS-Threadlimit

Ergebnis:

```text
OpenBLAS error: Memory allocation still failed after 10 retries, giving up.
```

Der Prozess konnte NumPy/Torch wegen nahezu ausgeschöpftem Windows-Commit-/Auslagerungsspeicher nicht zuverlässig importieren. Zum Messzeitpunkt waren ungefähr 5,3 GB physischer RAM, aber nur etwa 258 MB virtueller Commit-Spielraum frei. Ein PowerShell-Prozess scheiterte parallel explizit mit `0x800705AF` („Auslagerungsdatei ist zu klein“).

#### Collection mit Threadlimits

Mit temporären Prozessvariablen:

```text
OPENBLAS_NUM_THREADS=1
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
```

wurden 92 Tests gesammelt.

#### Nicht-Engine-Suite

```text
83 passed, 30 warnings in 9.83s
```

Die Warnungen stammen aus `httpx`: der alte `app`-Shortcut ist deprecated.

#### Leichte Engine-Tests

Vier Tests ohne vollständige Großallokation bestanden:

- CPU-Guard reduziert Kandidaten bei niedrigem RAM,
- Major-Tensor-Schätzung bleibt unter Testbudget,
- Chakra-Spektrumpalette vollständig,
- Twilight-Palette vollständig.

```text
4 passed in 1.81s
```

#### Reale Engine-Tests

Der erste echte Berechnungstest scheiterte:

```text
RuntimeError: DefaultCPUAllocator: not enough memory:
you tried to allocate 85684224 bytes.
```

Ort: `app/algorithms/resonance_engine.py:1089`, `cosine_similarity`.

Der folgende Precision-Test endete nativ:

```text
Windows fatal exception: access violation
```

ebenfalls an `resonance_engine.py:1089`.

#### Kontrollierter manueller Smoke

Mit zur Laufzeit auf 1.000 reduzierter Kandidatenzahl lieferte die CPU-Engine erfolgreich:

- eine 12x12-Matrix,
- einen Score innerhalb 0 bis 1.

Das zeigt: Der Algorithmuspfad funktioniert grundsätzlich, die Standardressourcensteuerung ist im aktuellen Systemzustand aber nicht robust.

#### Weitere Checks

| Check | Ergebnis |
|---|---|
| `node --check user_workflow.js` | erfolgreich |
| PowerShell-Parser für `generate_matrix.ps1` | erfolgreich |
| `.venv\Scripts\python.exe -m pip check` | keine gebrochenen Requirements |

## 3. Root-Cause-Einordnung des Testabbruchs

Der unmittelbare Umgebungsfaktor war erschöpfter Windows-Commit-/Pagefile-Spielraum. Der Code besitzt aber zugleich eine Designlücke:

1. Der Guard nutzt `psutil.virtual_memory().available`, also primär physischen verfügbaren RAM.
2. Er budgetiert maximal 128 MiB für grob geschätzte Haupttensors.
3. `torch.randint(...).float()` kann Integer- und Floatkopie überlappen.
4. Projektion, Similarity-Normen und weitere temporäre Allokationen erhöhen den Peak.
5. Windows-Commit-/Pagefile-Verfügbarkeit wird nicht berücksichtigt.
6. Tests verwenden die hardwareadaptive Produktionskandidatenzahl statt eines kleinen deterministischen Testprofils.

Die korrekte Bewertung ist daher nicht „nur zu wenig RAM“, sondern:

- **Umgebung:** zu kleiner verbleibender Commit-Spielraum.
- **Engine:** unvollständige Peak-/Commit-Budgetierung und kein sicherer OOM-Fallback.
- **Tests:** keine isolierte, ressourcenbegrenzte Engine-Testkonfiguration.

## 4. Aussagekraft vorhandener Tests

### 4.1 Stärken

1. Persistenztests verwenden überwiegend `tmp_path` und berühren keine realen Runtime-Daten.
2. Löschtests prüfen Manifest, Gate, Idempotenz, Stores, Dateien und Audit.
3. Bus-Tests decken deutlich mehr als einen Happy Path ab.
4. API-Key-Verhalten ist gut charakterisiert.
5. PII-Projektionen sind explizit geprüft.
6. Repositoryhygiene hält Runtime-Pfade aus Git heraus.
7. Engine-Regressionsfälle adressieren konkrete frühere Speicher- und Determinismusthemen.

### 4.2 Grenzen

#### API-Tests mocken den Kern

`tests/test_api_vector_modes.py` ersetzt Engine und Vorabsignatur weitgehend durch Dummies. Nicht geprüft werden:

- echte Gruppen-, Geo-, Bild- und DB-Mathematik,
- echte Ressourcenlimits,
- tatsächliche Parameterübergabe an Torch,
- reales Cleanup unter Fehlern.

#### Frontendtests sind überwiegend statisch

Sie prüfen Strings und CSS-/HTML-Merkmale, nicht:

- DOM-Verhalten,
- Browserkompatibilität,
- XSS,
- Accessibility,
- Audio-/Timerlebenszyklus,
- API-Key-Modus,
- Netzwerkfehler oder Reloadzustand.

#### Audio-Test prüft eine Kopie

`tests/test_audio_checksum.py` implementiert einen Test-WAV-Generator, statt die verschachtelte Produktionsfunktion in `dev_cli.py` aufzurufen. Produktionsregressionen können dadurch unentdeckt bleiben.

#### Engine-Tests sind hardwareabhängig

Mehrere Tests nutzen die reale adaptive Kandidatenzahl. Es fehlen Slow-Marker, Timeout, kleine Testfixture und getrennte Hardware-Suite.

## 5. Kritische Testlücken

### 5.1 Engine und Fachlogik

- vollständige Ausgabe bei identischem Input über Neustarts,
- `focus_weight=Deaktiviert` wirklich fokusunabhängig,
- Score und Intensität nach Symmetrie,
- Nullverteilung und Scorekalibration,
- Vergleichbarkeit zwischen Fokussen/DB-Einträgen,
- Synonyme, Tippfehler und Unicode-Normalisierung,
- Gruppenreihenfolge,
- identischer Base64-Bildinhalt,
- Geburtszeitwirkung,
- Mitternacht der Organuhr,
- CPU/CUDA-Parität und CUDA-Determinismus,
- OOM-/Commit-/Low-Memory-Fallback,
- `top_k > candidates`,
- parallele Precision-Aufrufe und RNG-Restore bei Exceptions.

### 5.2 API und Security

- Path Traversal/absolute Pfade/Symlinks,
- Exportüberschreibung,
- WebSocket-Auth/Origin/Payloadlimits,
- gemischte `client_id`/`client_data`,
- disjunkte Vektormodi,
- ungültige/negative/riesige Matrixgrößen,
- Body-, Fokus-, Gruppen- und Sequenzlimits,
- Rate Limiting und Timeout,
- XSS-/CSV-Formula-Injection,
- Admin-/Ownership-Autorisierung,
- Fehlerdetail-Leaks.

### 5.3 Persistenz und Recovery

- parallele Writer und mehrere Prozesse,
- beschädigtes/leeres JSON,
- Disk-full und PermissionError,
- Teilausfälle mehrerer Stores,
- Lösch-Retry nach Teilfehler,
- Backup/Restore-Konsistenz,
- Schema-Migration und unbekannte Felder,
- Artefakt-Reconciliation,
- Retention/Purge.

### 5.4 Betrieb

- Clean-Clone-Installation Windows/Linux,
- echte Batch-/PowerShell-Ausführung,
- systemd-Start mit Env und Berechtigungen,
- CUDA-Zielhardware,
- Deployment-Allowlist,
- Upgrade/Rollback,
- Health/Readiness,
- Last- und Langzeittest,
- Backup-/Restore-Drill.

## 6. Coverage und Qualitätswerkzeuge

Nicht vorhanden oder nicht konfiguriert:

- Coverage-/Branch-Coverage-Konfiguration,
- `pyproject.toml`, `setup.cfg`, Tox oder Nox,
- Ruff/Flake8/Pylint,
- Black/Isort,
- Mypy/Pyright,
- ESLint/Prettier,
- PSScriptAnalyzer,
- ShellCheck,
- Pre-commit,
- CI-Workflow,
- Security-/Secret-/Dependency-/Lizenzscan.

Eine numerische Coverageaussage ist deshalb nicht belastbar.

## 7. Codequalitätsbefunde

### 7.1 Große Module

Die sieben größten Module bündeln jeweils mehrere Verantwortungen. Das erhöht:

- Kopplung,
- Reviewaufwand,
- Regressionsrisiko,
- Testschwierigkeit,
- Mergekonflikte,
- Divergenz zwischen Schnittstellen.

### 7.2 Breite Exceptionbehandlung

Im aktiven `app/`-Code wurden mehr als 50 relevante Treffer für breite `except Exception`, bare `except` oder `pass` gefunden. Typische Folgen:

- Fehler werden zu Defaultwerten degradiert,
- partielle Ergebnisse erscheinen erfolgreich,
- Ursachen gehen verloren,
- API gibt an anderer Stelle zu viele Details preis.

### 7.3 No-op-/Mock-/toter Code

Beispiele:

- `_validate_elements` ohne Wirkung,
- `run_quantum_inspired_refinement` als `pass`,
- D-Wave-Mock,
- `resonant_patterns` immer leer,
- Remote-Sensordaten gespeichert, aber nicht profiliert,
- `EMFStatusResponse` nicht konsequent als Responsemodell,
- `mock_resonance_calculation` ohne sichtbaren Hauptflow.

### 7.4 Duplikation

- PDF in API und CLI,
- Farb-/Kontrastlogik in API, CLI und Browser,
- Harmonizer in Python und JavaScript,
- Audioerzeugung im Produktionscode und separat im Test,
- mehrfach ähnliche Dummy-Engines in Tests.

### 7.5 Typing und Verträge

- viele `Dict[str, Any]` und freie Dictionaries,
- Pydantic-Modelle decken nicht alle realen Felder ab,
- API-, CLI- und PowerShell-Feldnamen driften,
- Zeitstempeltypen und Zeitzonen sind uneinheitlich,
- `request.copy(deep=True)` ist ein Pydantic-v1-Muster (`app/api/resonance.py:479-484`).

## 8. Abhängigkeitsqualität

`requirements.txt` enthält:

- exakte Pins nur für FastAPI/Uvicorn,
- offene Mindestversionen für Torch, NumPy, Pydantic, psutil, ReportLab, openpyxl, WebSockets,
- kein Lockfile oder Hashing,
- Testabhängigkeit `httpx` im Runtimefile,
- kein deklariertes pytest,
- fehlendes Pillow trotz optionaler Bildnutzung,
- keine Python-Obergrenze oder Plattformmatrix.

Die installierte Umgebung mit NumPy 2.4.6 und Torch 2.12.0 zeigt, wie weit offene Bereiche vom ursprünglich dokumentierten Mindeststand abweichen können.

README nennt Python 3.10+, der Bus nutzt `enum.StrEnum`, das Python 3.11 voraussetzt (`app/interchange_bus/envelope.py:16-17`).

## 9. Dokumentationsqualität

Positiv:

- sehr umfangreiche historische und aktuelle Dokumentation,
- vorhandene Daten-/Git-/Restore-Audits,
- Zielbild und Änderungsgrenzen sind beschrieben.

Problematisch:

- Versionen 1.2.0, 1.4.9, 1.4.9.1, 1.5.0 und „1.5.1+“ parallel,
- Port 8000 versus 8090,
- Split-Frontend versus Same-Origin,
- 44 historische Tests versus 92 aktuell gesammelt,
- Produktionsbereit-/Akkuranz-/D-Wave-Claims ohne Codebeleg,
- aktive und historische Dokumente sind nicht klar genug als SSOT getrennt.

## 10. Qualitätsgates für später

Vor einem Release sollten als Mindestgates definiert werden:

1. reproduzierbare Clean-Installation,
2. schnelle Unit-Suite und getrennte Hardware-/E2E-Suite,
3. grüne Vollsuite ohne native Abbrüche,
4. Branch-Coverage-Baseline,
5. Lint/Format/Typing für Python,
6. JS-Lint plus Browser-E2E,
7. PowerShell- und Shellanalyse,
8. Securityregressionen,
9. Dependency-, Secret- und Lizenzscan,
10. Backup-/Restore- und Upgrade-/Rollbacktest,
11. Last-/Speicher-/Parallelitätstest,
12. Dokumentations- und Claim-Traceability.
