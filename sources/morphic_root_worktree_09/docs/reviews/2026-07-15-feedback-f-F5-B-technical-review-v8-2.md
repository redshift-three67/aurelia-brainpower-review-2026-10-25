# Technisches Review 2 – F5-B Technical Freeze v8

## 1. Verdict

**REQUEST CHANGES**

| Schweregrad | Anzahl |
|---|---:|
| P0 | 0 |
| P1 | 2 |
| P2 | 0 |
| P3 | 0 |

Freeze v8 ist **nicht approvable**. Es wurde kein Scope-Drift festgestellt; daher lautet das Verdict nicht `INVALIDATED BY SCOPE DRIFT`.

Die beiden P1-Befunde betreffen:

1. Umgehung der Validierungsbindung durch eine konsistente Manipulation aller Draft-Attestierungsfelder zwischen Validate und Publish.
2. Nicht handle-/verzeichnisgebundene und nicht nachweislich crash-durable Authority-Replacements bei Registry, Stage-Index, Ledger, Stage und Stage-Key.

---

## 2. Prüfgegenstand und Methode

Das Review wurde unabhängig und strikt read-only als adversariales Datenintegritäts-/Recovery-Review durchgeführt.

Statisch gelesen wurden:

- der vollständige Freeze v8;
- alle **47 Manifestdateien**;
- die historischen Freeze-v4–v7-Dokumente und v6/v7-Reviewevidenz;
- Registry-, Stage-, Key-, Index- und Ledger-Persistenzpfade;
- Draft-Import, Validate, Publish und Source-Receipt-Bindung;
- Pending/Replace/Commit/Recovery;
- Revision, Aktivierung, Rollback, Audit und Backup/Restore;
- zugehörige Tests einschließlich der v8-Regressionstests.

Gemäß Reviewauftrag wurden **keine Tests ausgeführt**, keine Server gestartet, keine Netzwerkzugriffe durchgeführt, keine Dateien erzeugt oder verändert und kein Stage-Key angelegt.

---

## 3. Freeze-, Scope- und Authority-Nachweis

### Unmittelbar vor dem Verdict verifiziert

- Freeze-SHA-256:
  `1b697e2be4c9b9e276e123b178ba1d4e1050fd641b518e6ec12c26efe48d006d`
- Erwarteter Freeze-SHA-256: identisch
- Manifest: **47 Dateien**
- Eindeutige Manifestpfade: **47**
- Hashübereinstimmung: **47/47**
- Scope-Drift: **0**
- Branch: `operator-workbench-phase1`
- HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
- Registry-Authority:
  `config/source_repositories.json`
  SHA-256 `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3`
- Remedy-DB-Authority:
  `data/remedies.db`
  SHA-256 `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`
- `config/source_repositories.json.stage-key`: **ABSENT**
- Registry-Lock-Sidecars: **ABSENT**
- `MORPHIC_ADMIN_STAGE_KEY`: **ABSENT**
- Working-Tree-Status: unverändert gegenüber Freeze-Evidenz:
  - 349 Statuszeilen
  - Fingerprint `a45db0b32c163f73b1da6b5e4278fe0df6bcb49c611d819bfba32eba3b5227df`

Damit ist der Review technisch driftfrei.

---

# 4. Findings

## P1-1 – Konsistente Draft-Zeilenmanipulation kann die Validate→Publish-Bindung umgehen

### Fundstellen

- `core/admin_catalog/store.py:132-136`
- `core/admin_catalog/store.py:1824-1841`
- `core/admin_catalog/store.py:1914-1942`
- `core/admin_catalog/store.py:1959-1966`
- unvollständiger Regressionstest:
  `tests/test_f5b_review_findings.py:1535-1569`

### Problem

Die erfolgreiche Draft-Validierung wird ausschließlich durch Felder derselben mutablen `catalog_drafts`-Zeile repräsentiert:

- `payload_json`
- `payload_hash`
- `version`
- `validated_version`
- `validated_payload_hash`

Beim Publish wird geprüft:

```text
validated_version == version
validated_payload_hash == payload_hash
sha256(payload_json) == payload_hash
payload_json ist kanonisch
Snapshot ist aktuell semantisch valide
```

Diese Prüfungen erkennen eine isolierte Änderung von `payload_json`, wie sie der v8-Test abdeckt. Sie erkennen jedoch **keine kohärente Manipulation aller korrelierten Felder**.

Die Validierungsattestierung ist weder in einer unveränderlichen separaten Zeile gebunden noch kryptografisch von der mutablen Draft-Zeile unabhängig.

### Reproduzierbarer Failure-Pfad

1. Ein manueller Draft mit Payload **A** wird erstellt.
2. `mark_draft_validated()` validiert **A** und setzt:
   - `validated_version = version`
   - `validated_payload_hash = payload_hash(A)`
3. Zwischen Validate und Publish werden außerhalb der Store-API in derselben Draft-Zeile atomar gesetzt:
   - `payload_json = canonical_json(B)`
   - `payload_hash = sha256(canonical_json(B))`
   - `validated_payload_hash = sha256(canonical_json(B))`
   - `validated_version` und `version` bleiben gleich.
4. Payload **B** ist kanonisch und als Snapshot fachlich valide, wurde aber nie durch den ursprünglichen Validate-Vorgang attestiert.
5. Die Prüfungen in `publish_validated_draft()` bestehen:
   - Marker stimmen miteinander überein;
   - Live-Hash stimmt;
   - kanonisches JSON stimmt;
   - semantische Revalidierung ist grün.
6. Für einen receiptlosen generischen Draft greift anschließend nur `_require_no_source_identity_bypass()`. Eine neue beziehungsweise zulässige manuelle Identität wird dadurch nicht blockiert.
7. Revision **B** wird veröffentlicht und trägt Provenienzfelder, die den Eindruck einer gültigen Validate→Publish-Kette erzeugen.

Der vorhandene v8-Test verändert dagegen nur `payload_json`, lässt `payload_hash` und `validated_payload_hash` unverändert und beweist deshalb nur die triviale inkonsistente Manipulationsvariante.

### Auswirkung

- Veröffentlichung eines Payloads, der nicht der ursprünglich attestierte Validate-Snapshot ist.
- Falsche beziehungsweise irreführende Revisionsprovenienz.
- Ein späteres Activate kann den manipulierten Inhalt produktiv auswählen.
- Rollback und Audit können die manipulierte Revision anschließend als scheinbar ordnungsgemäß veröffentlichte Revision behandeln.
- Die Freeze-Behauptung, DB-Manipulation zwischen Validate und Publish werde fail-closed erkannt, ist damit zu weitgehend.

Source-importierte Drafts sind durch den zusätzlichen immutable Receipt-Payload-Hash besser geschützt. Das Defizit bleibt jedoch auf dem generischen Publish-Pfad vollständig bestehen.

### Präzise Abhilfe

1. Erfolgreiche Validierungen in einer **separaten append-only Validation-Attestation-Tabelle** persistieren, mindestens gebunden an:
   - vollständigen Catalog-Kontext,
   - Draft-ID,
   - Draft-Version,
   - kanonischen Payload-Hash,
   - Validierungs-Policy-/Schema-Version,
   - Attestierungszeitpunkt,
   - optional Actor/Approval-ID.
2. Attestierungszeilen nach Erstellung per attestierten Schema-Triggern unveränderlich machen.
3. Publish muss innerhalb derselben `BEGIN IMMEDIATE`-Transaktion die passende immutable Attestierungszeile lesen und gegen die live rekonstruierten Payloadbytes vergleichen.
4. Die mutablen `validated_*`-Spalten dürfen nicht alleinige Authority sein.
5. Falls Schutz gegen absichtliche Direktmanipulation der gesamten SQLite-Datei behauptet wird, benötigt die Attestierung zusätzlich einen extern verankerten HMAC-/Signaturnachweis. SQLite-Trigger allein sind keine Sicherheitsgrenze gegen einen vollständig privilegierten DB-Manipulator.
6. Neuer RED-Test:
   - nach erfolgreicher Validierung `payload_json`, `payload_hash` und `validated_payload_hash` kohärent auf einen anderen validen Snapshot setzen;
   - Publish muss nullmutierend scheitern;
   - keine Revision, kein Auditfragment und keine Aktivierungsänderung.

---

## P1-2 – Authority-Replacements sind pfadbasiert, nicht verzeichnis-handle-gebunden und nicht nachweislich crash-durable

### Fundstellen

Zentrale Schreibprimitive:

- `core/source_registry.py:925-955`
- `core/source_registry.py:958-966`

Registry-Commit:

- `core/source_registry.py:647-684`

Stage-Index-Transitions:

- `core/source_data_promotion.py:1027-1074`
- `core/source_data_promotion.py:1280-1351`

Stage-Key-Publikation:

- `core/source_data_promotion.py:1436-1475`

Consistency-Ledger:

- `core/source_data_promotion.py:636-642`

Zusätzliche immutable Stage-/Rollback-Publikation:

- `core/source_registry.py:958-966`
- `core/source_registry.py:694-724`

### Problem

`_atomic_replace_json()` schreibt und fsync’t eine temporäre Datei, schließt deren Handle und führt danach ein pfadbasiertes:

```python
os.replace(temporary, target)
```

aus.

Bei Registry und Ledger wird unmittelbar davor noch ein `authority_validator(target)` aufgerufen. Dieser Validator bindet jedoch weder:

- das Parent-Verzeichnis über einen offenen Handle,
- die temporäre Datei bis zum Replace,
- noch den Namespace zwischen Validator-Rückkehr und `os.replace()`.

Für den Stage-Index wird `_atomic_replace_json(index_path, index)` sogar ohne Authority-Validator verwendet.

`_atomic_publish_json()` verwendet entsprechend ein pfadbasiertes `os.link(temporary, target)` und löscht danach den temporären Namen.

Zusätzlich fehlt nach `os.replace()` beziehungsweise `os.link()` eine nachweislich dauerhafte Synchronisierung der Verzeichnis-Metadaten. Ein `fsync()` des Inhalts der temporären Datei beweist nicht, dass der neue Name beziehungsweise der Rename nach einem Stromausfall dauerhaft ist.

### Reproduzierbarer Failure-Pfad A – Parent-/Namespace-Swap

Auf einem Dateisystem, das konkurrierenden Austausch oder Umbenennung des Authority-Parents erlaubt:

1. Stage-Index oder Registry wird über gehärtete Read-Handles gelesen.
2. Der neue HMAC-/Registry-Payload wird berechnet.
3. `_write_temporary_json()` erzeugt und schließt die temporäre Datei.
4. Ein lokaler konkurrierender Akteur tauscht den Parent-Namespace oder verschiebt den ursprünglichen Parent und stellt am gleichen Pfad einen anderen Namespace bereit.
5. Bei Registry/Ledger kann der Tausch auch in dem Fenster nach `authority_validator(target)` erfolgen.
6. `os.replace(temporary, target)` löst beide Namen erneut pfadbasiert auf.
7. Mögliche Resultate:
   - Write landet in einer anderen Authority-Instanz;
   - Operation scheitert nach bereits erfolgten Vortransitionen;
   - bei kontrolliert bereitgestelltem temporärem Namen wird nicht mehr zwingend der zuvor fsync’te Temp-Inode publiziert;
   - der Prozess meldet Erfolg, ohne die final publizierte Datei über deren Identität und Bytes erneut zu attestieren.

Der Prozesslock schützt nur den gelockten Datei-Inode. Er bindet den umgebenden Verzeichnisnamespace nicht gegen einen lokalen Dateisystemakteur.

### Reproduzierbarer Failure-Pfad B – Crash nach erfolgreichem Rename, vor durable directory commit

1. `_transition_registered_stage()` berechnet ein gültiges HMAC-Indexobjekt.
2. Der Index wird von leer nach `pending` oder von `pending` nach `committed` ersetzt.
3. `os.replace()` kehrt erfolgreich zurück.
4. Der Verzeichniseintrag wurde nicht explizit dauerhaft synchronisiert.
5. Stromausfall beziehungsweise Host-Crash.
6. Nach Recovery kann der Dateiname auf einen älteren Indexzustand zurückfallen oder fehlen.

Besonders kritisch ist ein verlorenes `pending`:

- Die Reservierung war gegenüber der API erfolgreich.
- Nach Crash erscheint das Artefakt wieder unconsumed.
- Ein anderer Catalog-Pfad kann das Stage-Artefakt erneut reservieren.
- Der SQLite-weite Replay-Schutz ist pro Catalog-DB; er ersetzt die verlorene globale Stage-Index-Reservierung bei Cross-DB-Replay nicht.

Ein verlorenes `committed` kann zwar teilweise über eine vorhandene Draft-/Receipt-Zeile reconciled werden, ist aber ebenfalls kein Beweis für den behaupteten dauerhaft atomaren Zustandsautomaten.

Das gleiche Durability-Problem betrifft:

- Registry-Revisionen und Rollback-History;
- Stage-Key-Publikation;
- immutable Stage-Artefakte;
- Rollback-Snapshots und Consistency-Ledger.

### Auswirkung

- Cross-DB-Replay nach einem Crashfenster.
- Divergenz zwischen SQLite-Draft/Receipt und Stage-Index.
- Ambige Registry- oder Rollbackzustände trotz zuvor gemeldetem Erfolg.
- Möglichkeit eines Writes in einen ausgetauschten Namespace.
- Der behauptete `pending -> committed`-Recoveryvertrag ist nicht vollständig crash-durable.
- HMAC schützt den Inhalt eines gelesenen Index, aber nicht die Dauerhaftigkeit beziehungsweise Namespace-Identität des publizierten Dateinamens.

### Präzise Abhilfe

1. Authority-Parent einmalig identitätsgebunden öffnen und bis nach Commit halten.
2. Auf POSIX:
   - Temp-Datei relativ zu einem geöffneten Directory-FD erzeugen;
   - Temp-Inode per FD verifizieren und fsync’en;
   - `renameat`/`renameat2` beziehungsweise `linkat` relativ zu demselben Directory-FD verwenden;
   - anschließend Directory-FD `fsync()` ausführen;
   - finalen Namen relativ zu demselben Directory-FD erneut öffnen und Identität sowie Bytes prüfen.
3. Auf Windows:
   - Parent-/Dateihandles mit Reparse-sicherer Semantik verwenden;
   - Rename/Link mit Write-through- beziehungsweise Flush-Garantie;
   - final publizierten Handle und dessen File-ID gegen den Temp-Handle verifizieren.
4. Stage-Index, Registry, Ledger, Stage-Key und immutable Stage-Publikation dürfen nicht unterschiedliche, schwächere Schreibprimitive verwenden.
5. Nach jedem Write:
   - finalen Authority-Namen gehärtet neu öffnen;
   - erwartete Dateiidentität und exakte erwartete Bytes/HMAC verifizieren;
   - bei Abweichung Commit als ambig klassifizieren.
6. Fault-Injection-Tests ergänzen:
   - Parent-Swap nach Temp-fsync und vor Replace;
   - Target-/Temp-Namensswap nach Authority-Validator;
   - Crashsimulation nach `pending`-Replace;
   - Crashsimulation nach SQLite-Commit und vor `committed`;
   - dauerhafter Cross-DB-Replay-Test nach simuliert verlorenem Directory-Commit.

---

# 5. Bewertung der v6-/v7-Closure

## Geschlossen beziehungsweise statisch plausibel

- Registry- und Key-Reads verwenden denselben geöffneten Handle und vergleichen Pfad-/Handleidentität.
- Stage-JSON wird aus den Bytes desselben Handle gelesen und geparst.
- Source-Receipt bindet Registry-Pfad, Registry-Inhalt, Kontext, Draft und Payload.
- Source-Publish hält den Registry-Lock bis nach SQLite-Commit.
- Pending bindet Catalog-Pfad, vollständigen Kontext und Draft-ID.
- Ein vorhandenes Pending akzeptiert nur denselben vollständigen Receipt-Hash.
- `imported_at` wird deterministisch aus `staged_at` abgeleitet.
- Geänderte Actor-/Reason-Semantik kann Pending nicht übernehmen.
- Direkter Raw-Revisionswriter ist nicht als unterstützte kombinierbare Store-API exponiert.
- Base-Revision-Identitäten werden nicht pauschal als Source-Identitäten vergiftet.
- Revisionswrites, Aktivierung und Audit werden in attestierten SQLite-Transaktionen ausgeführt.
- Rollback löscht keine Revisionen; Auditereignis und Aktivierungspointer sind transaktional gekoppelt.

## Nicht vollständig geschlossen

- **V8-R3 / Draft-Tampering:** Nur inkonsistente Einzeländerungen werden sicher erkannt; eine kohärente Änderung von Payload und allen co-lokalen Validierungsmarkern bleibt publizierbar.
- **Authority-owning Write-Boundaries:** Die Read-Seite ist deutlich gehärtet, aber Replace/Publish/Commit bleiben pfad- statt Parent-Handle-gebunden und ohne vollständigen Durability-Nachweis.

Damit ist die Closure aller v6/v7-Findings nicht vollständig.

---

# 6. Rollback-, Audit- und Backup/Restore-Einordnung

## Positiv

- Aktivierung und Audit-Insert sind transaktional gekoppelt.
- Aktivierung verwendet CAS/Activation-Version und verhindert ABA-/Lost-Update-Pfade.
- Rollback reaktiviert nur frühere Revisionen und löscht keine Revision.
- Die interne Audit-Hashkette wird korrekt nur als Konsistenznachweis behandelt.
- Backup verwendet die SQLite-Backup-API statt einer Live-Dateikopie.
- Restore überschreibt kein bestehendes Ziel und verifiziert Hash, Größe, Schema und publizierte Identität.

## Verbleibendes Risiko

Eine durch P1-1 unrechtmäßig veröffentlichte Revision ist danach aus Sicht von Aktivierung, Audit und Rollback eine reguläre immutable Revision. Diese nachgelagerten Mechanismen sind intern konsistent, können aber die fehlende Validate→Publish-Authentizität nicht nachträglich reparieren.

Die Registry-/Stage-Recovery bleibt wegen P1-2 zudem nicht vollständig an eine durable Authority-Transition gebunden.

---

# 7. Schlussentscheidung

Freeze v8 ist driftfrei, der Scope ist vollständig und die produktiven Authorities sind unverändert. Dennoch bestehen zwei substanzielle P1-Befunde an zentralen Persistenz- und Recovery-Boundaries.

**Finales Verdict: `REQUEST CHANGES`**

Voraussetzungen für einen neuen approvablen Freeze:

1. unabhängige immutable Validate-Attestierung gegen kohärente Draft-Zeilenmanipulation;
2. Parent-/Handle-gebundene und crash-durable Replace/Publish-Primitive für Registry, Stage-Index, Ledger, Stage und Key;
3. adversariale Regressionstests für beide Failure-Klassen;
4. vollständige erneute Freeze- und 47+-Dateien-Hashbindung;
5. zwei neue unabhängige driftfreie Reviews mit `P0=P1=P2=P3=0`.

## Änderungen während des Reviews

- Erstellte Dateien: **keine**
- Veränderte Dateien: **keine**
- Tests/Server/Netzwerk: **nicht ausgeführt**
- Produktive Authority-Writes: **keine**
- Stage-Key-Erzeugung: **keine**