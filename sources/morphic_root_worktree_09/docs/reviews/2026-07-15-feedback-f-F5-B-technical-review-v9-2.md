# Technisches Review 2 – F5-B Technical Freeze v9

## 1. Verdict

# **REQUEST CHANGES**

**Konfidenz:** HOCH
**Reviewart:** unabhängig, adversarial, vollständig statisch und read-only
**Finding-Zählung:** `P0=0, P1=4, P2=0, P3=0`
**Scope-Drift:** keine
**F5-B:** weiterhin `NO-GO`

Freeze v9 ist formal driftfrei und vollständig bytegebunden, aber wegen vier substantieller Datenintegritäts-/Recovery-Befunde nicht approvable. Insbesondere sind die behauptete unabhängige Validation-Attestation, die Temp-Inode-Bindung und der Schema-v8-/Recovery-Vertrag nicht vollständig erfüllt.

---

## 2. Freeze-, Scope- und Authority-Nachweis

### Start und unmittelbar vor Verdict verifiziert

| Nachweis | Ergebnis |
|---|---|
| Freeze-Datei | `docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v9.md` |
| Erwarteter Freeze-SHA-256 | `c580b92876af7e444caffefd7a7e15a99fc546fea2266e62b83e596795553c69` |
| Freeze-SHA-256 Start | identisch |
| Freeze-SHA-256 Ende | identisch |
| Manifesteinträge | exakt `50` |
| Eindeutige Manifestpfade | exakt `50` |
| Scope-Hashprüfung Start | `50/50` korrekt |
| Scope-Hashprüfung Ende | `50/50` korrekt |
| Branch | `operator-workbench-phase1` |
| HEAD | `619a1f5485a151816e32732929a6a823839ccb57` |
| Working-Tree-Statuszeilen | `351` |
| Status-Fingerprint | `cc90fb0fc1655236083370c1fd846833a3490ae888140400f40b325ff7fe3e50` |
| Registry-Authority | `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3` |
| Remedy-DB-Authority | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` |
| `config/source_repositories.json.stage-key` | **ABSENT** |
| `MORPHIC_ADMIN_STAGE_KEY` | **ABSENT** |
| Port 8000 | frei |
| Scope-Drift | **0** |

Alle 50 Manifestdateien wurden statisch geprüft. Es wurden keine Tests, Test-Collector, Server oder Netzwerkzugriffe ausgeführt und kein Stage-Key erzeugt.

---

## 3. Finding-Matrix

| ID | Priorität | Finding | Primärbeleg |
|---|---:|---|---|
| F5B-V9-R2-01 | P1 | Die Validation-Attestation ist bei direkter kohärenter DB-Manipulation frei nacherzeugbar und deshalb nicht unabhängig | `core/admin_catalog/store.py:141-167`, `1871-1887`, `1979-1997`; `tests/test_f5b_review_findings.py:1605-1684` |
| F5B-V9-R2-02 | P1 | Der gehaltene Temp-Inode ist nicht atomar an den publizierten Tempnamen gebunden; ein Child-Name-Swap kann die Authority vor der finalen Attestation überschreiben | `core/source_registry.py:1035-1082`, `1085-1117`, `1132-1170`; `tests/test_source_registry_atomicity.py:125-153` |
| F5B-V9-R2-03 | P1 | Für bestehende Schema-v7-Cataloge und v7-Backups existiert kein Schema-v8-Migrationspfad | `core/admin_catalog/store.py:1133-1149`; `core/admin_catalog/backup.py:14-23`, `246-249`, `266-318` |
| F5B-V9-R2-04 | P1 | Backup- und Restore-Publikation bleibt pathname-basiert und ohne durable Parent-Directory-Publikation | `core/admin_catalog/backup.py:112-143`, `181-233`, `266-322`; `tests/test_admin_catalog_backup.py:392-412`, `620-640` |

---

# 4. Findings im Detail

## F5B-V9-R2-01 – Validation-Attestation ist bei direkter DB-Manipulation forgebar

**Priorität:** P1
**Dateien:**

- `core/admin_catalog/store.py:141-167`
- `core/admin_catalog/store.py:1871-1887`
- `core/admin_catalog/store.py:1979-1997`
- `tests/test_f5b_review_findings.py:1605-1684`

### Problem

Die neue Attestation liegt zwar in einer separaten Tabelle und ist durch `BEFORE UPDATE`-/`BEFORE DELETE`-Trigger gegen nachträgliche Änderung geschützt. Es gibt jedoch keine Barriere gegen einen direkten zusätzlichen `INSERT`.

`mark_draft_validated()` erzeugt eine Zeile mit Kontext, Draft-ID, Version, Payload-Hash und Policy-Version. Publish verlangt lediglich, dass eine passende Zeile existiert. Weder die Attestation noch ihr Erzeuger werden durch einen externen Schlüssel, eine Signatur oder eine außerhalb derselben SQLite-Datei liegende Authority authentisiert.

Die beiden Trigger verhindern nur Update und Delete. Ein kohärenter DB-Manipulator kann jederzeit eine neue, passende Attestierungszeile einfügen. Der vorhandene Test beweist nur:

- kohärente Draftmanipulation **ohne** passende neue Attestation scheitert;
- vorhandene Attestierungszeilen können nicht aktualisiert oder gelöscht werden.

Er beweist nicht, dass eine passende Attestation nicht direkt eingefügt werden kann.

### Failure-Pfad

1. Payload A wird regulär validiert.
2. Direkt in SQLite werden `payload_json`, `payload_hash` und `validated_payload_hash` kohärent auf einen fachlich gültigen Payload B geändert.
3. Zusätzlich wird in `catalog_draft_validation_attestations` eine neue Zeile für:
   - denselben Kontext,
   - dieselbe Draft-ID,
   - dieselbe Version,
   - `payload_hash(B)`,
   - `catalog-validation-v1`
   eingefügt.
4. Die Update-/Delete-Trigger greifen nicht, da es sich um einen Insert handelt.
5. Publish findet die passende Attestation.
6. Live-Hash, Rekanonisierung und semantische Validierung von B bestehen.
7. Payload B wird veröffentlicht, obwohl kein vertrauenswürdiger Validate-Vorgang B attestiert hat.

### Auswirkung

- Die Attestation ist gegenüber dem ausdrücklich angeforderten direkten kohärenten DB-Manipulationsmodell nicht unabhängig.
- Eine vollständig intern konsistente, aber gefälschte Validate→Publish-Kette ist möglich.
- Revision, Aktivierung, Audit und Rollback können anschließend den gefälscht attestierten Payload als regulär behandeln.

### Abhilfe

1. Validation-Attestations extern authentisieren, mindestens mit HMAC/Signatur über:
   - vollständigen Catalog-Kontext,
   - Draft-ID und Version,
   - kanonischen Payload-Hash,
   - Policy-/Schema-Version,
   - Validierungszeitpunkt beziehungsweise monotone Approval-ID.
2. Schlüssel außerhalb der Catalog-DB und außerhalb des Backuppayloads halten.
3. Publish muss die Signatur innerhalb der finalen Transaktion gegen einen injizierten, vertrauenswürdigen Key-Provider verifizieren.
4. Alternativ die gesamte Validate-/Publish-Boundary in einen getrennten OS-Prozess mit exklusiver DB-Authority verlagern und direkte externe DB-Schreibbarkeit aus der Bedrohungsannahme entfernen.
5. RED-Test ergänzen: kohärente Draftmanipulation plus direkter Insert einer passend aussehenden, aber unsignierten Attestation muss nullmutierend scheitern.

---

## F5B-V9-R2-02 – Temp-Inode-Bindung verhindert keinen Tempnamen-Swap

**Priorität:** P1
**Dateien:**

- `core/source_registry.py:1035-1082`
- `core/source_registry.py:1085-1117`
- `core/source_registry.py:1132-1170`
- `tests/test_source_registry_atomicity.py:125-153`

### Problem

`_held_file_identity()` hält zwar einen Handle beziehungsweise FD auf dem geprüften Temp-Inode. `_replace_in_guard()` und `_link_in_guard()` publizieren danach jedoch weiterhin den **Tempnamen**:

- POSIX: `os.replace(source.name, ..., src_dir_fd=dirfd)` beziehungsweise `os.link(source.name, ...)`;
- Windows: `MoveFileExW(str(source), ...)` beziehungsweise `os.link(source, target)`.

Der offene Temp-Handle bindet den Inode, aber nicht atomar den später erneut ausgewerteten Verzeichnisnamen an diesen Inode.

Auf POSIX kann ein anderer lokaler Writer den Tempnamen trotz offenem FD umbenennen oder unlinken und unter demselben Namen eine andere Datei erzeugen. Auf Windows wird der Temp-Handle ausdrücklich mit `FILE_SHARE_DELETE` geöffnet (`0x00000004`), wodurch Rename/Delete des Tempnamens ebenfalls nicht ausgeschlossen wird.

Die finale Byte-/Identitätsattestation erkennt die Abweichung erst **nach** Replace oder Link. Zu diesem Zeitpunkt kann die fremde Datei bereits unter dem produktiven Authority-Namen liegen.

### Failure-Pfad

1. Erwartete Bytes werden in Temp-Inode T geschrieben und geflusht.
2. `_held_file_identity()` erfasst T.
3. Ein nicht kooperierender Writer entfernt oder verschiebt den Tempnamen.
4. Unter demselben Tempnamen wird Inode X mit fremden Bytes angelegt.
5. `_replace_in_guard()` oder `_link_in_guard()` publiziert X, weil die Operation den Namen erneut auflöst.
6. Die produktive Registry, der Stage-Index, das Ledger oder ein immutable Artefakt zeigt jetzt auf X.
7. `_attest_published_bytes()` erkennt den Identitäts-/Bytefehler und wirft eine Exception.
8. Die Operation meldet zwar einen ambigen Fehler, die Authority wurde aber bereits mit fremden Bytes überschrieben beziehungsweise veröffentlicht.

### Auswirkung

- Fail-closed Rückmeldung ohne Erhalt der vorherigen Authority.
- Potenzielle Registry-/Ledger-/Stage-Index-Korruption.
- Bei Stage-Index-Verlust oder -Substitution mögliche Replay- und Recovery-Divergenz.
- Die Freeze-Behauptung, der finale Name müsse dem gehaltenen Temp-Inode entsprechen, wird nur nachträglich geprüft, nicht commit-seitig erzwungen.

### Abhilfe

- **Windows:** Temp-Handle ohne `FILE_SHARE_DELETE` halten und Rename/Link über eine handle-basierte API ausführen; der Tempname darf während des Commitfensters nicht austauschbar sein.
- **POSIX:** fd-/inode-basierte Publikation verwenden, beispielsweise `O_TMPFILE` plus `linkat(..., AT_EMPTY_PATH)` für immutable Publikation; für Replace eine Plattformprimitive einsetzen, die den gehaltenen Inode statt eines erneut aufgelösten Tempnamens publiziert, oder den Authority-Parent so besitzen/berechtigen, dass kein fremder Child-Name-Writer möglich ist.
- Finalattestation beibehalten, aber nicht als Ersatz für die atomare Inode→Finalname-Bindung behandeln.
- RED-Tests für Registry, Stage-Index und immutable Publish ergänzen:
  - Tempname nach `_held_file_identity()` austauschen;
  - Injektion explizit bestätigen;
  - vorherige Authority muss bytegleich erhalten bleiben;
  - kein fremder Finalname darf verbleiben.

---

## F5B-V9-R2-03 – Schema v7 kann nicht auf Schema v8 migriert werden

**Priorität:** P1
**Dateien:**

- `core/admin_catalog/store.py:1133-1149`
- `core/admin_catalog/backup.py:14-23`
- `core/admin_catalog/backup.py:246-249`
- `core/admin_catalog/backup.py:266-318`

### Problem

`CatalogStore.__init__()` führt `_SCHEMA` ausschließlich bei einer neuen oder leeren Datenbank aus. Jede bestehende nichtleere Datenbank wird unmittelbar gegen den exakten Schema-v8-Fingerprint geprüft.

Eine gültige Schema-v7-Datenbank scheitert daher an `_assert_catalog_schema()` und wird weder:

- erkannt und versioniert migriert,
- transaktional um die neue Attestationstabelle und Trigger ergänzt,
- noch über einen expliziten Offline-Migrationsbefehl aktualisiert.

Dasselbe gilt für bestehende v7-Backups: `_load_manifest()` akzeptiert ausschließlich `catalog_schema_version == 8`. Ein korrektes v7-Backup kann nicht in einen neuen Store restauriert und anschließend migriert werden.

### Failure-Pfad

1. Ein bestehender gültiger Catalog beziehungsweise ein gültiges Backup wurde unter Schema v7 erzeugt.
2. Die Anwendung wird auf Freeze-v9-Code aktualisiert.
3. `CatalogStore(existing_v7_db)` prüft sofort den v8-Fingerprint.
4. Die Prüfung schlägt fehl; `_SCHEMA` und damit die neue Attestationstabelle werden nicht angewendet.
5. Ein Restore des v7-Backups scheitert bereits an der Manifest-Schema-Version.
6. Bestehende Drafts, Revisionen, Aktivierungen und Auditdaten sind mit dem neuen Code nicht mehr zugänglich.

### Auswirkung

- Upgrade-/Recovery-Ausfall für bestehende Schema-v7-Cataloge.
- Vorher gültige v7-Backups besitzen keinen unterstützten Wiederherstellungspfad.
- Der Schema-v8-Vertrag ist nur ein Fresh-DB-Vertrag, kein vollständiger Migrations-/Recovery-Vertrag.

### Abhilfe

1. Explizite, versionierte Offline-Migration `v7 -> v8` implementieren.
2. Migration in einer exklusiven `BEGIN IMMEDIATE`-Transaktion:
   - exakten v7-Fingerprint attestieren;
   - neue Tabelle und Trigger mit festem SQL erzeugen;
   - keine historischen Attestierungen erfinden;
   - resultierenden v8-Fingerprint prüfen;
   - vollständig committen oder rollbacken.
3. Vor Migration ein verifiziertes v7-Backup erzeugen oder einen expliziten caller-owned Backup-Pfad verlangen.
4. Restore muss entweder:
   - v7-Bundles akzeptieren, als v7 verifizieren und anschließend migrieren, oder
   - einen separaten dokumentierten `restore-v7-and-migrate-v8`-Pfad bereitstellen.
5. RED-Tests mit echten v7-Schemafixtures für Datenbankmigration, v7-Backup-Restore und Rollback bei jeder Migrationsgrenze ergänzen.

---

## F5B-V9-R2-04 – Backup/Restore ist nicht parent-/handle-gebunden oder crash-durable

**Priorität:** P1
**Dateien:**

- `core/admin_catalog/backup.py:112-143`
- `core/admin_catalog/backup.py:181-233`
- `core/admin_catalog/backup.py:266-322`
- `tests/test_admin_catalog_backup.py:392-412`
- `tests/test_admin_catalog_backup.py:620-640`

### Problem

Backup und Restore verwenden nicht die neuen gemeinsamen Authority-Commitprimitive.

Insbesondere:

- Backup veröffentlicht Datenbank und Manifest mit pathname-basiertem `os.replace()`.
- Restore verwendet unter Windows `os.rename(source, target)`.
- POSIX-Restore verwendet pathname-basiertes `os.link(source, target)`.
- Der Target-Parent wird nicht über einen identitätsgebundenen Directory-Handle gehalten.
- Nach Rename/Link erfolgt kein `fsync(dirfd)` beziehungsweise gleichwertiger durable Namespace-Commit.
- Die finale Identitäts-/Byteprüfung erkennt Abweichungen erst nach der Publikation.

Damit ist ein erfolgreich zurückgegebener Restore nicht nachweislich crash-durable. Außerdem bleiben Parent-/Child-Namespace-Swaps zwischen Vorprüfung und Veröffentlichung möglich.

### Failure-Pfad

1. Restore erzeugt und verifiziert `temporary_target`.
2. `_publish_without_overwrite()` veröffentlicht pathname-basiert.
3. Rename/Link kehrt erfolgreich zurück.
4. Es erfolgt kein durable Flush der Parent-Verzeichnismetadaten.
5. Die finalen Bytes werden geprüft und `restore_catalog_backup()` gibt Erfolg zurück.
6. Host- oder Stromausfall vor dauerhaftem Directory-Commit.
7. Nach Recovery kann der Zielname fehlen, auf einem älteren Namespacezustand beruhen oder als ambiger Restore vorliegen.

Analog kann während der pathname-basierten Publikation ein lokaler Writer Parent- oder Tempnamen austauschen. Die vorhandene Post-Publish-Prüfung bewahrt bewusst ein bereits publiziertes verdächtiges Ziel, stellt aber die vorherige Authority nicht wieder her.

### Auswirkung

- Ein als erfolgreich gemeldeter Recovery-Vorgang kann nach einem Crash verschwinden.
- Backupbundle kann Datenbank und Manifest in unterschiedlichen durable Zuständen hinterlassen.
- Restore besitzt schwächere Commitgarantien als Registry, Stage, Index und Ledger.
- Recovery ist nicht durchgehend an dieselbe Authority-owning Commitprimitive gebunden.

### Abhilfe

1. Backupdatenbank, Manifest und Restoreziel über dieselben gehärteten Commitprimitive veröffentlichen.
2. Parent-Directory vor Temp-Erzeugung identitätsgebunden öffnen und bis nach finaler Attestation halten.
3. Temp-Inode bis zur Publikation binden.
4. POSIX: dirfd-relative Link/Rename plus `fsync(dirfd)`.
5. Windows: no-delete-share Parent-/Temp-Handles, write-through Publish und dokumentierte durable Flush-Semantik.
6. Finale Datei über denselben Parent neu öffnen und exakte Bytes/Identität prüfen.
7. Backupbundle erst als vollständig gültig behandeln, wenn Datenbank und Manifest jeweils durable sind; optional ein zuletzt veröffentlichtes immutable Completion-Record verwenden.
8. Fault-Injection-Tests für Crash nach DB-Publish, nach Manifest-Publish, nach Restore-Link/Rename und vor/nach Parent-Flush ergänzen.

---

## 5. Bewertung der v6–v8-Closure

| Frühere Root-Cause | Bewertung in v9 |
|---|---|
| Registry-/Key-Read-TOCTOU | statisch geschlossen |
| Stage-/Index-Read nicht handlegebunden | statisch geschlossen |
| Pending ohne vollständigen Catalog-Kontext | geschlossen |
| Pending-Approval-/Receipt-Austausch | geschlossen |
| Source-Base-Provenance-Poisoning | geschlossen |
| Komponierbarer Raw-Revisionswriter | geschlossen |
| Live-Payload-Hash/Kanonizität/Receipt-Reattestation | geschlossen |
| Kohärente Validate→Publish-Manipulation | **nur gegen Draftzeilenmanipulation ohne Attestation-Insert geschlossen; im angeforderten direkten DB-Manipulationsmodell offen** |
| Parent-/Handle-gebundene Authority-Publikation | **Parentbindung verbessert, Temp-Inode→Tempname-Bindung offen** |
| Crash-Durability aller Recovery-Authorities | **für Registry-/Stage-Primitiven verbessert; Backup/Restore weiterhin offen** |
| Schema-v8-Backup-/Restore-Migration | **offen** |

---

## 6. Schlussentscheidung

```text
VERDICT: REQUEST CHANGES
P0=0
P1=4
P2=0
P3=0
SCOPE DRIFT: NO
FREEZE V9: DRIFTFREI, ABER NICHT APPROVABLE
F5-B: NO-GO
```

Erforderlich sind getrennte RED→GREEN-Mikrogates für:

1. extern authentisierte beziehungsweise tatsächlich unabhängige Validation-Attestation;
2. atomare Temp-Inode→Finalname-Bindung ohne austauschbaren Tempnamen;
3. vollständige Schema-v7→v8-Migration einschließlich alter Backups;
4. parent-/handle-gebundene und crash-durable Backup-/Restore-Publikation.

Anschließend sind ein neuer vollständiger Technical Freeze und zwei neue unabhängige driftfreie Reviews erforderlich.

## 7. Änderungs- und Ausführungsnachweis

- Repositorydateien erstellt: **keine**
- Repositorydateien verändert: **keine**
- Tests/Test-Collector: **nicht ausgeführt**
- Server: **nicht gestartet**
- Netzwerk: **nicht verwendet**
- Produktive Authorities: **nur read-only gehasht**
- Stage-Key: **nicht erzeugt**
- Backup/ShadowCopy: **nicht erstellt**