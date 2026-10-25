# Technisches Review 2 – F5-B Technical Freeze v7

## Verdict

**REQUEST CHANGES**

**Konfidenz:** hoch
**Finding-Zählung:** `P0=0, P1=3, P2=0, P3=0`

Nach der für dieses Gate vorgeschriebenen Regel ist `APPROVE` nur bei `P0=P1=P2=P3=0` zulässig. Der Scope blieb driftfrei; das Verdict ist daher nicht `INVALIDATED BY SCOPE DRIFT`, sondern wegen drei substantieller Datenintegritäts-/Recovery-Findings `REQUEST CHANGES`.

---

## 1. Review-Bindung und Scope

| Merkmal | Verifiziert |
|---|---|
| Arbeitsverzeichnis | `C:\morphic_v1\.worktrees\operator-workbench-phase1` |
| Branch Start/Ende | `operator-workbench-phase1` |
| HEAD Start/Ende | `619a1f5485a151816e32732929a6a823839ccb57` |
| Freeze | `docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v7.md` |
| Freeze SHA-256 Start | `d2bb3ffd7811e0991b076599952a14ce8ca37d5d1053fb9d8f342cf3bec2da38` |
| Freeze SHA-256 Ende | `d2bb3ffd7811e0991b076599952a14ce8ca37d5d1053fb9d8f342cf3bec2da38` |
| Erwarteter Freeze-Hash | identisch |
| Manifest | exakt `44` Einträge, exakt `44` eindeutige Pfade |
| Scope-Hashprüfung Start | `44/44` entsprechen dem Manifest |
| Scope-Hashprüfung Ende | `44/44` entsprechen dem Manifest |
| Scope-Mismatches | Start `0`, Ende `0` |
| Produktiver Stage-Key Start | `ABSENT` |
| Produktiver Stage-Key Ende | `ABSENT` |
| Scope-Drift | keine |

Die vollständigen 44 Endhashes entsprachen bytegenau den vollständigen Manifesthashes in Freeze v7. Es gab keine fehlende oder zusätzliche Manifestdatei.

### Produktive Authorities

| Authority | Start | Ende | Erwartung |
|---|---|---|---|
| `config/source_repositories.json` | `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3` | identisch | identisch |
| `data/remedies.db` | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` | identisch | identisch |
| `config/source_repositories.json.stage-key` | fehlt | fehlt | muss fehlen |

Der begrenzte tracked Working-Tree-Status umfasste am Start und Ende dieselben `37` Zeilen. Der End-Fingerprint dieses Status war:

```text
77cf319c0c498a58148b79bccf68343e9b5f7dc0deb859069274a6754d55321c
```

---

## 2. Finding-Matrix

| Priorität | Finding | Primärbeleg |
|---|---|---|
| **P1** | Stage-Artefakt und Stage-Index werden nicht über denselben identitätsgeprüften Handle gelesen; transienter Path-Swap bleibt möglich | `core/source_data_promotion.py:961-984`, `1432-1451` |
| **P1** | Publish revalidiert den live gelesenen Draft-Payload nicht gegen Payload-Hash und Source-Receipt; semantisch gültig manipulierte Draftbytes können publiziert werden | `core/admin_catalog/store.py:1914-1941`, `2032-2068` |
| **P1** | Eine bestehende `pending`-Reservation bindet nicht die vollständige Receipt-/Approval-Identität und kann vor DB-Commit mit geänderten Attestierungsfeldern ersetzt werden | `core/source_data_promotion.py:308-355`, `1283-1307`; `core/admin_catalog/store.py:1239-1275` |

---

# 3. Findings im Detail

## P1-1: Stage- und Indexbytes sind nicht handlegebunden

**Datei:** `core/source_data_promotion.py:961-984`
**Weitere Belege:** `core/source_data_promotion.py:1057-1061`, `1117-1122`, `1261-1263`, `1432-1451`

### Befund

`_load_stage_authority_json()` prüft zunächst die Dateimetadaten über den Pfad:

```python
canonical = _canonical_stage_file(path)
before = os.stat(canonical, follow_symlinks=False)
payload = _load_json(canonical)
after = os.stat(canonical, follow_symlinks=False)
```

Der tatsächliche Read findet jedoch in `_load_json()` erneut pfadbasiert statt:

```python
payload = json.loads(path.read_text(encoding="utf-8"), ...)
```

Damit gibt es keinen offenen Handle, dessen `fstat`-Identität an genau die gelesenen Bytes gebunden wird. Ein Angreifer oder konkurrierender nicht kooperierender Writer kann zwischen `before` und dem impliziten Open in `read_text()` die Pathname-Datei austauschen und sie vor `after` wiederherstellen. Die beiden Pfad-Stats sehen dann dieselbe ursprüngliche Datei, obwohl andere Bytes geparst wurden.

Der Prozesslock ändert daran nichts: Er koordiniert nur kooperierende Writer und bindet die gelesenen Bytes nicht kryptographisch oder über einen File-Handle.

Diese Funktion liest sowohl:

- das immutable Stage-Artefakt,
- den HMAC-signierten Stage-Index,
- alle Precheck-/Reserve-/Commit-/Recovery-Zugriffe auf den Index.

Die vorhandene Swap-Abdeckung ersetzt den Pfad dauerhaft während beziehungsweise nach `_load_json`; sie deckt keinen transienten `swap → read → restore` zwischen den beiden Path-Stats ab.

### Auswirkung

Eine transient eingeschleuste, früher gültige und mit demselben Stage-Key signierte Stage-/Index-Kombination kann im Readfenster als Authority dienen, ohne dass die anschließenden Pfadmetadaten den Austausch zwingend erkennen. Damit sind die Freeze-Claims zur echten Stage-Index-Integrität und Swap-/TOCTOU-Abdeckung nicht vollständig erfüllt.

### Erforderliche Korrektur

- Stage-Artefakt und Stage-Index jeweils einmal über einen no-follow beziehungsweise entsprechend gehärteten Handle öffnen.
- `fstat` vor und nach dem Read auf demselben Handle ausführen.
- Die vollständigen Bytes über genau diesen Handle lesen.
- Erst die eingefrorenen Bytes parsen.
- Nach dem Read die Handleidentität mit der aktuellen Pathname-Identität vergleichen.
- Einen deterministischen RED-Test für `swap → fremde Bytes lesen → ursprünglichen Pfad wiederherstellen` ergänzen, getrennt für Stage und Index.

---

## P1-2: Publish attestiert nicht den live gelesenen Draft-Payload

**Datei:** `core/admin_catalog/store.py:1914-1941`
**Weitere Belege:** `core/admin_catalog/store.py:2032-2068`, `65-118`

### Befund

`publish_validated_draft()` liest innerhalb der finalen `BEGIN IMMEDIATE`-Transaktion:

```sql
payload_json,
payload_hash,
version,
validated_version,
validated_payload_hash
```

Danach prüft der Code nur:

```python
row["validated_version"] == row["version"]
row["validated_payload_hash"] == row["payload_hash"]
```

Anschließend wird `payload_json` geparst und semantisch validiert:

```python
candidate_entries = _entries_from_payload_json(str(row["payload_json"]))
_require_valid_snapshot(candidate_entries)
```

Es fehlt jedoch die entscheidende Integritätsprüfung:

```python
_sha256(str(row["payload_json"])) == row["payload_hash"]
```

Für den dedizierten Source-Publish fehlt zusätzlich der Vergleich der live gelesenen Draftbytes mit:

- `receipt.draft_payload_hash`,
- `receipt.draft_version`,
- der zum Receipt gehörenden vollständigen Draftidentität.

`authorized_receipts` werden vor der SQLite-Transaktion gegen die Registry geprüft; innerhalb der Transaktion werden anschließend lediglich ihre Hash-IDs mit den DB-Zeilen verglichen. Existiert ein Receipt, wird `_require_no_source_identity_bypass()` ausdrücklich übersprungen.

### Adversariales Szenario

1. Ein Source-Draft wird korrekt importiert und validiert.
2. `payload_hash`, `validated_payload_hash` und Receipt bleiben unverändert.
3. `payload_json` wird durch andere, weiterhin semantisch gültige Catalogdaten ersetzt.
4. Beim Publish:
   - stimmen die zwei gespeicherten Hashspalten weiterhin miteinander überein;
   - der veränderte Payload besteht `validate_entries`;
   - das vorhandene Source-Receipt verhindert den generischen Bypasscheck;
   - `_revision_insert_plan()` erzeugt eine neue Revision aus den veränderten Einträgen.
5. Die publizierte Revision enthält damit nicht mehr die vom Source-Receipt freigegebenen Draftbytes.

Der Ausschluss beliebigen feindlichen `sqlite3`-Zugriffs aus der API-Capability-Grenze beseitigt dieses Datenintegritätsproblem nicht: Der Store attestiert und verifiziert bereits persistierte Revisionen gegen Korruption. Die finale Publish-Boundary muss ebenso fail-closed mit den live gelesenen Draftbytes umgehen.

### Auswirkung

Ein Source-Receipt kann eine andere Payload autorisieren als die tatsächlich publizierte Revision. Dadurch brechen:

- Draft-/Receipt-Atomicity über den späteren Publish hinweg,
- Source-Provenance,
- Attestation der finalen Write-Boundary,
- die Behauptung, dass nur der exakt freigegebene Source-Draft publiziert wird.

### Erforderliche Korrektur

Innerhalb derselben attestierten `BEGIN IMMEDIATE`-Transaktion und vor dem ersten Revisionswrite:

1. kanonische Integrität von `payload_json` prüfen;
2. den Hash der live gelesenen Bytes gegen `catalog_drafts.payload_hash` vergleichen;
3. `version`, live Payload-Hash und Kontext gegen jedes Source-Receipt vergleichen;
4. bei Abweichung ohne Revisionsfragment rollbacken;
5. RED-Tests für semantisch gültige Payloadmanipulation bei unveränderten Hash-/Validierungsmarkern hinzufügen, sowohl für generischen als auch dedizierten Source-Publish.

---

## P1-3: `pending` kann mit geänderter Approval-Semantik übernommen werden

**Dateien:**

- `core/source_data_promotion.py:308-355`
- `core/source_data_promotion.py:1283-1307`
- `core/admin_catalog/store.py:1239-1275`

### Befund

Eine `pending`-Reservation bindet:

- Catalog-Pfad,
- Catalog-Kontext-Hash,
- Draft-ID,
- Receipt-Hash.

Bei einem erneuten Reserve-Aufruf mit gleichem Pfad, Kontext und Draft prüft `_transition_registered_stage()` jedoch nicht, ob der neue Receipt-Hash mit der bestehenden Reservation übereinstimmt:

```python
if target_state == "pending" and previous_state == "pending":
    return previous_receipt_hash
```

Existiert noch kein Receipt in der Catalog-DB, ruft der Store anschließend auf:

```python
_replace_pending_registered_stage(...)
```

Dieser Pfad ersetzt `consumed_receipt_sha256` durch den neu erzeugten Receipt-Hash.

Der neue Receipt kann sich in attestierungsrelevanten Feldern unterscheiden, insbesondere:

- `actor_id`,
- `reason`,
- `imported_at`,
- daraus folgend `receipt_sha256`.

`imported_at` wird bei jeder Vorbereitung neu erzeugt. Die Reservation bindet daher nicht die vollständige ursprüngliche Approval-/Operation-Identität, sondern erlaubt vor dem DB-Commit eine nachträgliche Umschreibung.

### Auswirkung

Nach einem Fehler zwischen Reservation und Catalog-Commit kann derselbe Stage-Consumer die bestehende Reservation mit einer anderen Auditbegründung oder einem anderen Actor fortsetzen. Der Stage-Index belegt dann nicht mehr unveränderlich, welche Approval-Semantik ursprünglich reserviert wurde.

Die v4-Kontextbindung verhindert korrekt die Übernahme durch einen anderen Catalog-Kontext. Sie verhindert aber nicht die Änderung der Attestierung innerhalb desselben Kontextes und derselben Draft-ID.

### Erforderliche Korrektur

- Eine stabile Operation-/Approval-ID in Stage-Index und Receipt aufnehmen.
- `pending` an den vollständigen Receipt-Hash oder einen kanonischen Hash aller approval-signifikanten Felder binden.
- Bei Recovery nur den exakt gleichen reservierten Receipt akzeptieren.
- Falls eine Reservation vor DB-Commit bewusst aufgegeben werden soll, dafür einen separaten, explizit autorisierten Abandon-/Reset-Übergang mit eigener Auditidentität definieren.
- RED-Tests für geänderte `actor_id`, `reason`, Zeitstempel und sonstige Receiptfelder bei bestehendem `pending` ergänzen.

---

## 4. Positiv statisch verifizierte Grenzen

Unabhängig von den Findings waren folgende wesentliche Eigenschaften im eingefrorenen Code statisch nachweisbar:

- Registry- und Stage-Key-Reads verwenden ihre gelesenen Bytes über denselben geöffneten Handle und vergleichen Handle-/Path-Identitäten.
- Stage-Index-Schema ist Version `4`; Kontext-Hash umfasst Operator, Workspace, Tenant und Scope.
- `committed`-Stages werden gegen Replay in andere DBs, Kontexte und Drafts abgewiesen.
- Draft und Source-Receipt werden in derselben SQLite-Transaktion geschrieben.
- Alle geprüften Store-Mutationspfade beginnen mit `BEGIN IMMEDIATE` und Schema-Attestierung.
- `_revision_insert_plan()` ist ein reiner Plan ohne Connection oder SQL-Ausführung; ein eigenständiger roher `_insert_revision()`-Writer existiert nicht.
- Revisionen und Revisionseinträge besitzen DB-Trigger gegen Update/Delete sowie einen Finalisierungsübergang.
- Der generische Service-Publish weist Source-Drafts ab; der dedizierte Source-Publish hält den Registry-Lock bis nach dem Catalog-Commit.
- Es wurde kein Runtime-, Web-, Engine-, Scan- oder Netzwerk-Consumer der F5-B-Pipeline gefunden.
- Die CLI führt `data-import-draft` getrennt von Publish und Activation; `data-promote` bleibt ein sichtbar deprecateter Consistency-Alias.

Diese Punkte kompensieren die drei Findings nicht.

---

## 5. Read-only-Nachweis

Während dieses Reviews wurden ausschließlich ausgeführt:

- Datei-Reads,
- statische Quelltextsuche,
- SHA-256-Berechnung in einem einmaligen Python-Prozess mit `PYTHONDONTWRITEBYTECODE=1`,
- `git branch --show-current`,
- `git rev-parse HEAD`,
- begrenztes `git status --short --untracked-files=no`.

Es wurden ausdrücklich **nicht** ausgeführt:

- keine Tests,
- kein Test-Collector,
- kein Server,
- kein Port-/Runtime-Smoke,
- kein Netzwerkzugriff,
- kein SQLite-Open durch Anwendungscode,
- keine Tempdatei,
- keine Datenbankerzeugung,
- kein Stage-Key,
- keine Repositoryänderung.

**Erzeugte oder veränderte Dateien:** keine.
**Aufgetretene Scope-Drift:** keine.

---

# 6. Schlussentscheidung

```text
VERDICT: REQUEST CHANGES
P0=0
P1=3
P2=0
P3=0
SCOPE DRIFT: NO
FREEZE V7: DRIFTFREI, ABER NICHT APPROVABLE
F5-B: NO-GO
```

Freeze v7 muss gemäß seiner eigenen Gate-Regel bewahrt und als `SUPERSEDED / REQUEST CHANGES` behandelt werden. Die drei Findings benötigen getrennte RED→GREEN-Mikrogates und anschließend einen neuen vollständigen Technical Freeze mit zwei neuen unabhängigen Reviews.