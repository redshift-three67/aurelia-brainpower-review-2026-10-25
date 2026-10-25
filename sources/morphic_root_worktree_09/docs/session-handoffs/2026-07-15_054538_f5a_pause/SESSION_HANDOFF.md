# Pause-Handoff – Feedback f / F5-A Source-Integritätsfundament

**Erstellt:** 2026-07-15 05:45 lokaler Hostzeit
**Arbeitsverzeichnis:** `C:\morphic_v1\.worktrees\operator-workbench-phase1`
**Branch:** `operator-workbench-phase1`
**HEAD:** `619a1f5485a151816e32732929a6a823839ccb57`
**Hermes-Session:** `20260715_054525_14f636`
**Status dieses Dokuments:** verbindlicher Pause-/Wiederanlaufpunkt; kein formales F5-A-GO

---

## 1. Kurzentscheidung

F5-A ist funktional weitgehend umgesetzt und umfangreich verifiziert, aber **noch nicht formal freigegeben**.

Der letzte technisch ausgeführte Stand lautet:

- F5-A-Fokus: `103 passed, 1 skipped`;
- Adminmatrix: `426 passed, 6 skipped`;
- breite Suite: `910 passed, 8 skipped` sowie exakt die 14 bekannten Baselinefehler;
- statische Checks: Ruff, `py_compile` und `git diff --check` bestanden;
- letzter Top-5-Nachweis vor dem abschließenden bool-sicheren `record_count`-Patch: `1 passed in 94.87s`;
- nach diesem letzten kleinen Patch wurde Top-5 wegen des damaligen Toollimits noch nicht erneut ausgeführt.

Das neueste driftfreie Data-/CLI-/Dokumentationsreview `deleg_11f0ea26` meldete zwei noch offene P2-Punkte:

1. persistierter und öffentlicher Vertrag verwendet weiterhin missverständliche `promotion`-Terminologie;
2. der verlinkte Vollplan weist noch fälschlich F5.1 als neu zu beginnenden Arbeitsblock aus.

Deshalb gilt:

- **F5-A technisch weitgehend GREEN, formal NO-GO**;
- **F5-B gesperrt**;
- **Feedback f insgesamt NO-GO bis F8**;
- kein Catalog-Publish, keine Aktivierung, keine Runtimewirkung, kein Netzwerk und kein lokales Source-Daten-I/O freigegeben.

---

## 2. Verbindliches F5-Makroblockmodell

Makroblöcke dienen nur der ergonomischen Orchestrierung. Teilnummern, RED-/GREEN-Verträge, Hashbindungen, Reviews, Stop-Gates und ShadowCopies bleiben getrennt rückverfolgbar.

- **F5-A:**
  - F5.5 Source-Policy und lokale Importgrenzen;
  - F5.4 atomare Registry-, Audit-, Snapshot- und Rollbackpfade;
  - F5.1 vollständiger Batchhash, Replay-Schutz und quarantänisiertes `analysis_only`-Staging.
- **F5-B:**
  - F5.2 typenspezifische Normalizer;
  - F5.3 kontrollierte Draft-Übernahme.
- **F5-C:**
  - F5.6 verbleibende Pipeline-Härtung;
  - F5-Gesamtgate.

Verbindliche Reihenfolge je Makroblock:

1. read-only Discovery;
2. explizite Authority-/Scope-Entscheidung;
3. externe hashverifizierte Pre-State-ShadowCopy;
4. getrennte RED-Verträge;
5. kleinste GREEN-Implementierung;
6. adversariale Härtung;
7. Fokus-, Admin-, breite und Top-5-Verifikation;
8. finaler Scope-/Status-/Dateihashfreeze;
9. zwei unabhängige driftfreie technische Reviews;
10. Gate- und Golden-Record-Dokumentation;
11. dokumentationsgebundener Doppelreview;
12. externe Post-State-ShadowCopy mit vollständiger Manifest-Rückverifikation.

Jeder Patch nach einem Reviewdispatch invalidiert den betreffenden Snapshot. Auch reine Gate-Dokumentationspatches verlangen einen neuen dokumentgebundenen Hashreview vor Post-State und formalem GO.

---

## 3. Aktueller Produktiv-, Test- und Dokumentationsscope

### Produktionscode

- `core/admin_catalog/source_policy.py`
- `core/source_registry.py`
- `core/source_data_promotion.py`
- `apps/cli/commands/sources.py`

### Fokustests

- `tests/test_admin_source_policy.py`
- `tests/test_source_registry_atomicity.py`
- `tests/test_source_registry.py`
- `tests/test_source_data_promotion.py`
- `tests/test_source_registry_cli.py`

### Relevante Dokumentation und Authorities

- `PROJECT_MEMORY/00_CURRENT_STATE.md`
- `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md`
- `docs/status/2026-07-13-feedback-f-umsetzungsplan-kurz.md`
- `docs/status/2026-07-12-gesamtstruktur-fortschritt.md`
- `docs/QUELLEN_REGISTRY_BEWERTUNG_20260628.md`
- `docs/STABILIZATION_TEST_MATRIX.md`
- `docs/SESSION_HANDOFF_20260628.md`
- `docs/WORKTREE_INVENTORY_20260629.md`
- `config/source_repositories.json`
- `data/remedies.db`

Produktive Authorities sollen unverändert bleiben:

- `config/source_repositories.json` – zuletzt verifizierter SHA-256: `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3`;
- `data/remedies.db` – zuletzt verifizierter SHA-256: `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`.

---

## 4. Umgesetzte technische Verträge

### F5.5 – Source-Policy und Importgrenzen

- zentrale fail-closed Authority in `core/admin_catalog/source_policy.py`;
- strikte JSON-Verträge, Duplicate-Key-Ablehnung, `NaN`-/`Infinity`-Ablehnung;
- unbekannte Felder und typfalsche Werte werden abgewiesen;
- `enabled` muss echtes JSON-Boolean sein;
- lokale Pfade müssen explizit, absolut, existent, kanonisch und an einen Importroot gebunden sein;
- Registry-/Ledgerpfade werden vor Lock-/I/O-Verwendung kanonisiert;
- vorhandene Reparsekomponenten werden fail-closed behandelt.

Bewusste Grenze: Die lokale Pfadprüfung ist nur Point-in-time-Planvalidierung. Ein späterer echter Windows-Dateiconsumer muss über denselben Handle öffnen, Reparse-/Final-Path-Eigenschaften prüfen und in einen privaten immutable Snapshot kopieren. Diese Grenze gehört nicht still in F5-A implementiert.

### F5.4 – Registry-, Import- und Rollbackatomizität

- atomare Temp/Flush/Replace-Schreibpfade und Locks;
- Revision-CAS plus vollständiger Registry-Payload-Baseline-Hash;
- same-revision Swaps und Revision-0-Löschung werden erkannt;
- Legacy-v1 ist read-only und wird am finalen on-disk Boundary abgewiesen;
- Manifest-Stage-Artefakte binden Revision, vollständigen Registryhash, Manifesthash und Artefakthash;
- `deprecated` ist terminal;
- Quarantäne kann nicht über generisches Replacement umgangen werden;
- Rollback ist hash-, pfad-, revisions-, snapshot- und current-state-gebunden;
- `rollback_history` ist authoritative Single-use-Quelle;
- Consumed-Sidecars sind nur ergänzende Evidenz und können keinen autorisierten Rollback vetoieren;
- post-commit Fehler werden als committed, nicht committed oder uneindeutig klassifiziert;
- bei nachgewiesenem Commit wird Evidenz weiter publiziert, bei nachgewiesenem Nicht-Commit In-Memory-State restauriert, bei Ambiguität fail-closed gemeldet.

### F5.1 – Datenbatch-/Ledgervertrag

- vollständiger Batchhash bindet fachliche und technische Batchfelder;
- revisionsunabhängige Replay-Identität über `batch_identity_sha256`;
- Daten-Staging bindet Source-Manifesthash, Registryrevision und vollständigen Registryhash;
- Registry wird unter Lock aktuell geladen; Promotion revalidiert den aktuellen Zustand;
- Records verlangen echte nichtleere Strings für `id` und `label`;
- `record_count` verlangt echten `int`, lehnt `bool` ab und muss exakt zur Recordanzahl passen;
- normale und Quarantäne-Stagingroots müssen disjunkt sein;
- F5-A-Artefakte bleiben `analysis_only` und quarantänisiert;
- Ledger-v2-Wrapper und Entries werden feldgenau validiert;
- `entry_sha256` bindet jeden vollständigen Ledger-Eintrag;
- Legacy-v1-Ledger werden nicht still als v2 fortgeführt;
- Dry-run validiert Ledger und Replay, erzeugt aber weder Verzeichnis noch Registry-/Ledger-Lock-Sidecar;
- Dry-run und Realpfad besitzen dieselbe Legacy-Zulässigkeit.

Bewusste Grenze: Das Ledger besitzt keinen extern gebundenen Head und keinen externen Tamper-Evidence-Anker. Replay-Erkennung gilt nur innerhalb des intakten aktuellen Ledgers.

---

## 5. Offene P2-Punkte aus `deleg_11f0ea26`

### P2-A – `promotion`-Terminologie im Maschinenvertrag und öffentlichen CLI

Aktuell werden weiterhin Begriffe wie die folgenden verwendet:

- Ledger-Schema `morphic_source_data_promotion_ledger`;
- Entry-Feld `promoted_at`;
- CLI-Command `sources data-promote`;
- zugehörige Meldungen/Tests.

Das ist missverständlich, weil F5-A keine Catalog-Promotion durchführt. Die Operation schreibt ausschließlich einen lokal validierten Konsistenzeintrag.

Konservativer Zielvertrag:

1. Vor Mutation alle aktuellen Schema-, Feld-, CLI- und Testverwendungen suchen.
2. RED-Verträge für eindeutige Consistency-Terminologie schreiben.
3. Einen **neuen versionierten Consistency-Vertrag** einführen, zum Beispiel:
   - Schema `morphic_source_data_consistency_ledger`;
   - Feld `recorded_at`;
   - primärer CLI-Command `data-record-consistency` oder ein gleich eindeutig benannter Command.
4. Alte Promotion-Namen nicht still umdeuten:
   - entweder explizit ablehnen;
   - oder nur als klar deprecateten Alias mit eindeutiger Warnung und identischer No-Publish-Semantik erhalten.
5. Vor einer Entscheidung prüfen, ob außerhalb von Tests bereits Ledgerdateien existieren. Keine produktiven Daten still migrieren.
6. Dokumentation, Hilfetexte, Tests und Maschinenvertrag gemeinsam aktualisieren.

Der genaue neue Commandname ist noch keine Nutzerentscheidung. In der nächsten Session darf eine konservative, konsistente Standardentscheidung getroffen werden, aber erst nach read-only Usage-Inventar und RED-Verträgen.

### P2-B – veralteter Vollplan

`.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md:592-604` sagt noch, F5.1 sei der nächste neu zu beginnende Block.

Erforderliche Korrektur:

- F5-A = F5.5/F5.4/F5.1 technisch umgesetzt;
- formal weiterhin NO-GO;
- aktueller Schritt = P2 schließen, vollständige Matrix, Freeze, Doppelreview, Gate-Dokumentation, dokumentgebundener Doppelreview, Post-State;
- F5-B bleibt gesperrt;
- F4.4 bleibt geschlossen und wird nicht wieder geöffnet.

---

## 6. Verifikation und bekannte Baseline

Verbindliche Umgebung:

```bash
PYTHONDONTWRITEBYTECODE=1
PYTHONUTF8=1
OPENBLAS_NUM_THREADS=1
/c/morphic_v1/.venv/Scripts/python.exe
```

### Letzter ausgeführter Stand

```text
Fokus: 103 passed, 1 skipped
Admin: 426 passed, 6 skipped
Breit: 910 passed, 8 skipped, 14 failed
Statisch: Ruff PASS, py_compile PASS, git diff --check PASS
Top-5 unmittelbar vor letztem record_count-Patch: 1 passed in 94.87s
```

Die 14 breiten Baselinefehler sind exakt:

- ein datumsabhängiger Consent-Test;
- dreizehn bestehende Web-Rate-Limit-/HTTP-429-Tests.

Kein anderer breiter Fehler ist akzeptabel. Für die breite Suite keinen externen inkompatiblen `--basetemp` erzwingen.

### Nach den P2-Patches erneut ausführen

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 \
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
tests/test_admin_source_policy.py \
tests/test_source_registry_atomicity.py \
tests/test_source_registry.py \
tests/test_source_data_promotion.py \
tests/test_source_registry_cli.py -q -W error

PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 \
/c/morphic_v1/.venv/Scripts/python.exe -m pytest \
tests/test_admin_*.py \
tests/test_source_registry.py \
tests/test_source_registry_atomicity.py \
tests/test_source_data_promotion.py \
tests/test_source_registry_cli.py -q -W error

PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 \
/c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q

PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 \
/c/morphic_v1/.venv/Scripts/python.exe -m pytest tests/test_top5_workflow_smoke.py -q -W error
```

Anschließend Ruff über den vollständigen Produktiv-/Testscope, `py_compile` über die Produktionsdateien und `git diff --check` ausführen.

---

## 7. Backup- und Portgrenzen

F5-A-Pre-State:

`E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260714_224422_feedback_f_F5_A_pre`

Bestätigte Rückverifikation:

```text
verified=12/12 bad=[]
```

Der konkrete Pre-State-Manifesthash ist im erhaltenen Verlauf nicht verfügbar und darf nicht erfunden werden.

Portgrenzen:

- keinen Server starten;
- Port 8000 freihalten;
- bestehenden Dienst auf `127.0.0.1:8090` nicht stören;
- der Pause-Handoff-Probeoutput war unter Git-Bash für 8090 binär verkürzt; deshalb in der nächsten Session vor jeder Serveraktion mit einer geeigneten read-only Portabfrage erneut prüfen.

---

## 8. Reviewhistorie richtig einordnen

Alle älteren PREreview-Batches wurden durch nachfolgende Patches oder Drift invalidiert. Sie dürfen nicht als finale Approvals verwendet werden:

- `deleg_bdc59646`
- `deleg_e42f3880`
- `deleg_310c16e4`
- `deleg_90d4b60a`
- `deleg_0d54c8af`
- `deleg_c56c08e7`
- `deleg_1039c2a4`
- `deleg_42dcb2d1`

`deleg_11f0ea26` ist der jüngste relevante Stand:

- Securityteil: wegen Drift in `tests/test_source_data_promotion.py` invalidiert;
- Data-/CLI-/Docs-Teil: driftfrei, `REQUEST CHANGES`, zwei P2 wie in Abschnitt 5.

Vollständige Summary:

`C:\Users\Hubert111\AppData\Local\hermes\cache\delegation\subagent-summary-1-20260715_015628_277528.txt`

Nach jedem neuen Patch müssen beide technischen Reviews auf einem neuen Freeze erneut ausgeführt werden.

---

## 9. Exakte Fortsetzungsreihenfolge

### Phase A – Wiederanlauf, nur read-only

1. `CLAUDE.md` lesen.
2. Dieses Handoff und `NEXT_SESSION_PROMPT.md` lesen.
3. `PROJECT_MEMORY/00_CURRENT_STATE.md` lesen.
4. Vollplan, Kurzplan und Gesamtstatus lesen.
5. Branch, HEAD, vollständigen gezielten Status und relevante SHA-256 neu prüfen.
6. Ports 8000 und 8090 read-only prüfen.
7. Keine alten Reviewverdikte übertragen.

### Phase B – P2 testgetrieben schließen

1. Alle Promotion-/Consistency-Namen und Konsumenten suchen.
2. Prüfen, ob reale Ledgerartefakte außerhalb von Tests existieren; keine Secrets oder produktiven Inhalte ausgeben.
3. RED-Verträge für versioniertes Consistency-Schema, Zeitfeld, CLI-Hilfe und Legacyverhalten ergänzen.
4. RED bestätigen.
5. Kleinsten konsistenten GREEN-Patch implementieren.
6. Vollplan auf den tatsächlichen F5-A-Abschlussstand korrigieren.
7. Golden Record, Kurzplan und Gesamtstatus erst nach den Tests mit den neuen Zahlen aktualisieren.

### Phase C – vollständige technische Matrix

1. Fokus.
2. Adminmatrix.
3. breite Suite mit exakter Baselineklassifikation.
4. Top-5.
5. Ruff.
6. `py_compile`.
7. `git diff --check`.
8. Temp-/Sidecar-/Scope-/Portprüfung.
9. produktive Authorities erneut hashen.

### Phase D – technischer Freeze und Doppelreview

1. finalen Scope deklarieren;
2. Git-Statusfingerprint und SHA-256 aller Scope-Dateien persistent speichern;
3. zwei unabhängige read-only Reviewer parallel dispatchen;
4. beide müssen F5.5, F5.4 und F5.1 separat bewerten;
5. Start-/Endhashes müssen identisch sein;
6. P0–P3, Drift oder Scope-Creep => automatischer Stopp;
7. nur zwei ausdrückliche `APPROVE` gelten.

### Phase E – Dokumentation und formales Gate

1. F5-A-Gate-Record erstellen;
2. Vollplan, Kurzplan, Golden Record und Gesamtfortschritt aktualisieren;
3. formale Grenzen dokumentieren: kein Publish, Activate, Runtime, Netzwerk oder Source-Datenrollback;
4. zwei dokumentationsgebundene Reviews auf dem vollständigen Code-/Dokumentsnapshot einholen;
5. jeder Patch danach invalidiert beide Reviews.

### Phase F – externe Post-State-ShadowCopy

1. außerhalb des Repositories unter `E:\mprphic_v1_Backups` sichern;
2. vollständiges Manifest mit SHA-256 erzeugen;
3. jedes Manifestobjekt aus dem Ziel zurücklesen und verifizieren;
4. externe Pfade und Hashnachweis im Gate-Record dokumentieren;
5. erst danach F5-A formal GO setzen;
6. Feedback f bleibt dennoch insgesamt NO-GO und F5-B darf erst danach beginnen.

---

## 10. Stop-Gates

Sofort stoppen bei:

- P0–P3 in einem Abschlussreview;
- Hash- oder Scope-Drift;
- neuen breiten Fehlern außerhalb der exakt 14 bekannten Baselinefälle;
- Mutation von `config/source_repositories.json` oder `data/remedies.db`;
- unerwarteten Server-/Netzwerkaktionen;
- F3-/F4-Evidenzdrift;
- unvollständiger ShadowCopy-Rückverifikation;
- Versuch, F5-B vor formalem F5-A-GO zu beginnen.

---

## 11. Repositorydisziplin

- Worktree ist umfangreich dirty/untracked; letzter Gesamtsnapshot: 321 Einträge.
- Kein pauschales Clean, Reset, Checkout, Staging oder Commit.
- Keine fremden Dateien umformatieren oder reparieren.
- Kein Commit/Push ohne ausdrückliche Nutzeranweisung.
- Projekt-Python immer explizit über `C:\morphic_v1\.venv\Scripts\python.exe` beziehungsweise `/c/morphic_v1/.venv/Scripts/python.exe` aufrufen.
- Keine Credentials oder `.env`-Inhalte lesen oder exportieren.

---

## 12. Session-Sicherung

Hermes-Export, automatisch secret-redigiert und mit logischer Kompressions-Lineage:

`docs/session-handoffs/2026-07-15_054538_f5a_pause/session-export/20260715_054525_14f636-handoff-wiederhergestellt-und-tests-abgeschlossen-16.md`

Der Export wurde während der noch aktiven Sitzung erzeugt und endet daher am Exportzeitpunkt. Dieses Handoff ergänzt den danach geschriebenen finalen Pausezustand.
