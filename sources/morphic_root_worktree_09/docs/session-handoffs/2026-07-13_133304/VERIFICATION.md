# Verifikationsprotokoll – Pause nach F2.1-GO

> Nur real beobachtete Ergebnisse. Keine synthetisch ergänzten Erfolgswerte.

## 1. Repository und Umgebung

Erhoben am 2026-07-13 um 13:33:04 lokal:

```text
Worktree: C:\morphic_v1\.worktrees\operator-workbench-phase1
Branch: operator-workbench-phase1
HEAD: 619a1f5485a151816e32732929a6a823839ccb57
```

Portmomentaufnahme:

```text
127.0.0.1:8000 LISTEN PID 23944
127.0.0.1:8090 LISTEN PID 18240
```

Beide Ports waren belegt und wurden nicht verändert. Neue Session muss den Zustand erneut erheben; PIDs sind nicht dauerhaft.

## 2. F2.1 fokussierte Tests

### Service-Fokus

```text
................                                                         [100%]
16 passed in 1.03s
```

### Gesamte Admin-Catalog-Matrix

Aufruf:

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 \
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_admin_catalog_contracts.py \
  tests/test_admin_catalog_store.py \
  tests/test_admin_catalog_validation.py \
  tests/test_admin_catalog_service.py \
  -q -W error
```

Beobachtetes Ergebnis:

```text
........................................................................ [ 87%]
..........                                                               [100%]
82 passed in 8.94s
```

### Compile

Folgender Compile-Schritt war Teil desselben erfolgreichen Befehls:

```bash
/c/morphic_v1/.venv/Scripts/python.exe -m py_compile \
  core/admin_catalog/__init__.py \
  core/admin_catalog/contracts.py \
  core/admin_catalog/store.py \
  core/admin_catalog/validation.py \
  core/admin_catalog/service.py
```

Ergebnis: PASS, Exitcode 0.

## 3. Breite Regression

Aufruf ohne Top-5:

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 \
/c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q \
  --ignore=tests/test_top5_workflow_smoke.py
```

Final beobachtetes Ergebnis:

```text
13 failed, 563 passed, 2 skipped in 31.52s
```

Die 13 Fehler waren ausschließlich dieselben bekannten HTTP-429-/Rate-Limiter-Ausreißer in:

- `tests/test_web_shell.py`
- `tests/test_web_workbench_runtime.py`
- `tests/test_workbench_client_context_persistence.py`

Belegte Baseline ohne Admin-Catalog-Testdateien:

```text
13 failed, 481 passed, 2 skipped
```

Differenz:

```text
563 - 481 = 82
```

Diese Differenz entspricht exakt den 82 neuen grünen Admin-Catalog-Tests. Die Fehlerzahl und Fehlerklasse blieb gleich.

## 4. Top-5-Smoke

Finaler Aufruf:

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 \
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
  tests/test_top5_workflow_smoke.py -q
```

Ergebnis:

```text
.                                                                        [100%]
1 passed in 107.39s (0:01:47)
```

## 5. Reale synthetische Smokes

Während F2.1 beobachtet:

```text
F2_1_REVIEWFIX_TEMP_SERVICE_SMOKE_OK
F2_1_REVIEWFIX_PUBLIC_IMPORT_OK
F2_1_PROVENANCE_TEMP_SMOKE_OK
F2_1_REVISION_CONFLICT_IMPORT_OK
```

Damit belegt:

- explizit injizierter Tempstore funktioniert;
- Draft → Validate → Publish → Aktivierungs-Lifecycle funktioniert;
- exakte Draft-Version/-Hash-Provenienz bleibt erhalten;
- öffentlicher Paketimport erzeugt keine Dateien oder Defaultdatenbank;
- neue Domainfehler sind öffentlich importierbar;
- temporäre Handles werden geschlossen und Tempverzeichnisse können entfernt werden.

## 6. Gezielte Reviewfix-Regressionen

Real grün bestätigt wurden unter anderem:

- `mark_draft_validated(expected_version=True)` wird abgewiesen;
- boolesche/nonpositive CAS-Werte werden abgewiesen;
- publizierte Draft-ID kann wegen Revisionsprovenienz nicht gelöscht werden;
- nur echter FK-Constraint wird als `PublishedDraftError` klassifiziert;
- doppelte Revisions-ID wird als `RevisionConflictError` klassifiziert;
- andere IntegrityErrors werden weder bei Delete noch Publish falsch umetikettiert;
- partielle Revisionsanlage wird bei injiziertem Publishfehler zurückgerollt;
- Provenienz-ID, -Version und -Payload-Hash sind persistiert und revisionsgehasht;
- Finalisierungstrigger blockiert Änderung von Provenienzversion/-hash beim Übergang `0 → 1`;
- Rollback auf aktuelle und nie aktive Revision scheitert;
- tatsächlicher R2→R1-Rollback mit früherer Aktivierung funktioniert;
- Audittypen und erfolglose Mutationen sind korrekt;
- alle sieben `EntryType`-Varianten bestehen den strukturierten Roundtrip.

## 7. Unabhängiger Review

Maßgeblicher Current-Snapshot-Review:

```text
Delegation: deleg_fa94b8c3
Snapshot: 82 fokussierte Tests
Verdikt: APPROVE
Konfidenz: HOCH
Offene historische oder neue P0–P2: keine
```

Der Reviewer bestätigte insbesondere:

- präzise SQLite-Fehlercodes;
- vollständigen Immutability-Trigger;
- atomare Provenienz/Hashbindung;
- striktes CAS;
- echten historischen Rollback;
- aussagekräftige Negativtests ohne erkennbare False Positives;
- explizite öffentliche API ohne Importseiteneffekte;
- keine Runtime-/Web-/CLI-/Netzwerkverdrahtung.

## 8. Nichtmutation und Git-Hygiene

Finaler SHA-256:

```text
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0 *data/remedies.db
```

`git diff --check`: Exitcode 0. Git meldete ausschließlich bestehende LF→CRLF-Warnungen für fremde/benachbarte Dateien; keine Whitespace-Fehler.

Eigene Admin-Catalog-Test-`.pyc`-Artefakte wurden exakt entfernt:

```text
ADMIN_PYC_REMAINING=0
```

Nicht durchgeführt:

- kein Commit;
- kein Push;
- kein Staging;
- kein Reset;
- kein Clean;
- keine produktive Datenmutation;
- keine Server-/Portänderung;
- kein Netzwerkzugriff für F2.1.

## 9. Post-State-ShadowCopy

```text
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_132404_feedback_f_F2_1_GO_post
FILES=13 VERIFIED=13
MANIFEST_SHA256=d1ab265153fce472aa72b6e395d6989003012439803be97d603a0a5a76dd124e
```

Die Sicherung umfasst die F1/F2.1-Implementierung, fokussierten Tests, Plan- und Gate-/Fortschrittsdokumente.

## 10. Handoff-Verifikation

Nach Erzeugung der Handoff-Dateien wird `SOURCE_MANIFEST.sha256` im Handoff-Ordner erstellt und unmittelbar mit `sha256sum -c` geprüft. Das Ergebnis ist im finalen Benutzerhinweis anzugeben.
