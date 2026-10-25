# Technisches Review 1 – F5-B Technical Freeze v9

## 1. Verdict

# **REQUEST CHANGES**

**Konfidenz:** hoch
**Reviewart:** unabhängig, adversarial, statisch und strikt read-only
**Finding-Zählung:** `P0=0, P1=2, P2=0, P3=0`
**Scope-Drift:** keine
**F5-B-Status:** weiterhin `NO-GO`

Die Validation-Attestation schließt die kohärente Manipulation der Draft-Zeile innerhalb des dokumentierten, zeilenbezogenen Bedrohungsmodells. Die neue Authority-Commit-Boundary bindet jedoch weder die ursprünglich erwartete Parent-Identität noch den tatsächlich geschriebenen Temp-Inode vollständig gegen nicht kooperierende Namespace-Manipulation. Beide Lücken betreffen alle darauf aufbauenden Registry-, Stage-, Index-, Ledger-, Snapshot- und Stage-Key-Schreibpfade.

---

## 2. Freeze-, Scope- und Authority-Bindung

| Nachweis | Start | Unmittelbar vor Verdict | Ergebnis |
|---|---|---|---|
| Freeze SHA-256 | `c580b92876af7e444caffefd7a7e15a99fc546fea2266e62b83e596795553c69` | identisch | PASS |
| Manifesteinträge | 50 | 50 | PASS |
| Eindeutige Pfade | 50 | 50 | PASS |
| Existierende Scope-Dateien | 50/50 | 50/50 | PASS |
| Scope-Hashes | 50/50 korrekt | 50/50 korrekt | PASS |
| Scope-Mismatches | 0 | 0 | PASS |
| Branch | `operator-workbench-phase1` | identisch | PASS |
| HEAD | `619a1f5485a151816e32732929a6a823839ccb57` | identisch | PASS |
| Registry-Authority | `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3` | identisch | PASS |
| Remedy-DB-Authority | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` | identisch | PASS |
| `config/source_repositories.json.stage-key` | `ABSENT` | `ABSENT` | PASS |
| `MORPHIC_ADMIN_STAGE_KEY` | `ABSENT` | `ABSENT` | PASS |

Es trat kein Freeze-, Scope-, Branch-, HEAD- oder Authority-Drift auf. Das Verdict lautet daher nicht `INVALIDATED BY SCOPE DRIFT`.

Alle 50 Manifestdateien wurden bytegenau gelesen und hashverifiziert. Die produktiven Implementierungs-, Schema-, Backup-, Test-, Plan-, Freeze- und Reviewdateien wurden statisch in ihrem Vertragszusammenhang geprüft.

---

## 3. Finding-Matrix

| Priorität | Finding | Primäre Fundstellen |
|---|---|---|
| **P1** | Der Parent-Guard bindet den Parent erst nach einer pfadbasierten, austauschbaren Authority-Auswahl. Ein vor dem Handle-Open substituierter Parent kann als vermeintlich richtige Authority akzeptiert und dauerhaft beschrieben werden. | `core/source_registry.py:942-963`, `979-1002`, `1006-1025`, `1139-1146`, `1155-1161`; unvollständiger Test `tests/test_source_registry_atomicity.py:125-152` |
| **P1** | Der offene Temp-Handle bindet nicht den bei Replace/Link erneut per Namen aufgelösten Temp-Inode. Ein Temp-Namensswap kann fremde Bytes publizieren; die finale Attestation erkennt dies erst nach der Mutation und stellt die Authority nicht wieder her. | `core/source_registry.py:925-939`, `1035-1082`, `1085-1117`, `1120-1170` |

---

# 4. Findings im Detail

## P1-1 – Parent-Handle kann an einen substituierten Namespace gebunden werden

### Fundstellen

- `core/source_registry.py:942-953`
- `core/source_registry.py:956-963`
- Windows: `core/source_registry.py:979-1002`
- POSIX: `core/source_registry.py:1006-1025`
- Replace/Publish-Aufrufer:
  - `core/source_registry.py:1139-1148`
  - `core/source_registry.py:1155-1168`
- Unvollständiger Windows-Test:
  - `tests/test_source_registry_atomicity.py:125-152`

### Problem

`_directory_commit_guard()` prüft zunächst die Parent-Komponenten pfadbasiert:

```text
_require_no_reparse_components(parent)
initial = os.lstat(parent)
```

Erst danach wird der Parent erneut über seinen vollständigen Pfad geöffnet:

- Windows: `CreateFileW(str(parent), ...)`
- POSIX: `os.open(parent, O_DIRECTORY | O_NOFOLLOW, ...)`

Der Vergleich `initial.st_dev/st_ino` gegen den geöffneten Handle schützt nur gegen einen Austausch **nach** dem `initial`-`lstat`. Er schützt nicht gegen eine Parent- oder Ancestor-Substitution:

1. nach einer erfolgreichen Komponentenprüfung und vor `initial = os.lstat(parent)`, oder
2. bereits vor Eintritt in `_directory_commit_guard()`, nachdem Registry/Index/Stage-Zustand und Lock im ursprünglichen Namespace gelesen wurden.

Der Guard bindet dann konsistent den ausgetauschten Parent. Die abschließende `lstat(parent)`-Prüfung sieht denselben Ersatzparent und meldet keinen Identitätswechsel.

Der vorhandene Windows-Test greift erst in `_replace_in_guard()` an, also nachdem der Parent-Handle bereits geöffnet wurde. Er beweist korrekt, dass dieser bereits gehaltene Windows-Handle einen späteren Parent-Rename blockiert. Er deckt jedoch die Authority-Auswahl vor dem Handle-Open nicht ab.

### Failure-Pfad

1. `SourceRegistry.save()` öffnet die Lockdatei und liest die Registry im ursprünglichen Parent `D`.
2. Nach der Baselineprüfung, aber vor `_directory_commit_guard()`, verschiebt ein nicht kooperierender lokaler Akteur `D` nach `D-old`.
3. Am ursprünglichen Pfad wird ein regulärer, nicht als Reparse/Symlink markierter Ersatzparent `D` angelegt.
4. `_require_no_reparse_components()`, `lstat()` und `CreateFileW` beziehungsweise `os.open()` attestieren konsistent den Ersatzparent.
5. Die Temp-Datei wird im Ersatzparent erzeugt.
6. `authority_validator(target)` akzeptiert dort bei fehlendem Target den erwarteten absoluten Namen.
7. Replace, Directory-Flush und finale Byteprüfung erfolgen vollständig im falschen Parent.
8. Der Aufruf meldet Erfolg, während die ursprünglich gelesene und durch den Lock repräsentierte Registry unter `D-old` unverändert blieb.

Dasselbe Grundproblem betrifft neue oder bestehende:

- Registry-Dateien,
- Stage-Artefakte,
- Stage-Indizes,
- Consistency-Ledger,
- Rollback-Snapshots und Consumed-Marker,
- Stage-Keys.

### Auswirkung

- Erfolgreich gemeldeter Commit in eine andere Authority-Instanz.
- Divergenz zwischen Lock-/Read-Authority und Write-Authority.
- Stage- und Registry-State-Machines können intern gültige Daten im falschen Namespace fortschreiben.
- Ein Registry- oder Stage-Key-Commit kann am erwarteten textuellen Pfad erscheinen, ohne an den zuvor geprüften Parent gebunden zu sein.
- Die Freeze-Behauptung einer Parent-/Handle-gebundenen Write-Boundary ist damit nicht vollständig erfüllt.

### Konkrete Abhilfe

1. Authority-Pfade komponentenweise von einem vertrauenswürdig gebundenen Root-/Ancestor-Handle aus öffnen.
2. POSIX:
   - `openat()`-Kette mit `O_DIRECTORY|O_NOFOLLOW`;
   - jede Komponente über den vorherigen Directory-FD öffnen;
   - Temp, Target, Rename und Link ausschließlich relativ zum finalen gebundenen FD durchführen.
3. Windows:
   - Parent/Komponenten über handle-relative beziehungsweise NT-native Handle-Semantik öffnen;
   - nicht nach einer separaten Pfadprüfung erneut den vollständigen Win32-Pfad als Authority auswählen.
4. Registry-/Stage-Operationen müssen nachweisen, dass Lock-, Read- und Commit-Parent dieselbe gebundene Authority-Identität besitzen.
5. RED-Tests ergänzen:
   - Parent-Swap vor `initial lstat`;
   - Parent-Swap zwischen Komponentenprüfung und Parent-Open;
   - Registry-Lock im ursprünglichen Parent, Commitversuch im ersetzten Parent;
   - getrennt für Windows und POSIX beziehungsweise durch eine deterministische Boundary-Injektion.

---

## P1-2 – Temp-Inode wird bei Replace/Link nicht als Publikationsquelle verwendet

### Fundstellen

- Temp-Erzeugung und Schließen des Write-Handles:
  - `core/source_registry.py:925-939`
- Erneutes pfadbasiertes Öffnen:
  - `core/source_registry.py:1035-1082`
- Replace:
  - `core/source_registry.py:1085-1103`
- Immutable Link:
  - `core/source_registry.py:1106-1117`
- Finale Attestation:
  - `core/source_registry.py:1120-1129`
- Aufrufer:
  - `core/source_registry.py:1132-1170`

### Problem

`_write_temporary_bytes()` schreibt und `fsync()`t die Temp-Datei, schließt danach aber den Schreibhandle und gibt nur den Pfad zurück.

`_held_file_identity()` öffnet anschließend diesen Pfad erneut und hält einen Handle, verwendet diesen Handle aber nicht als Quelle der Publikation. Replace und Link lösen den Temp-Namen erneut auf:

- Windows Replace: `MoveFileExW(str(source), str(target), ...)`
- Windows Link: `os.link(source, target)`
- POSIX Replace: `os.replace(source.name, target.name, src_dir_fd=..., dst_dir_fd=...)`
- POSIX Link: `os.link(source.name, target.name, src_dir_fd=..., dst_dir_fd=...)`

Der Directory-FD bindet auf POSIX zwar das Verzeichnis, nicht aber den Inode hinter `source.name`. Ein offener Inode-Handle verhindert auf POSIX keinen Rename/Unlink des Namens. Auf Windows wird der Temp-Handle ausdrücklich mit `FILE_SHARE_DELETE` geöffnet, sodass auch dort ein Namenswechsel möglich bleibt.

Damit besteht mindestens ein Swapfenster:

1. nach dem Schließen des Write-Handles und vor `_held_file_identity()`, sowie
2. nach dem Erfassen von `temporary_identity` und vor dem namensbasierten Replace/Link.

Die finale Identitäts-/Byteattestation erkennt eine abweichende Publikation zwar anschließend, aber erst nachdem:

- beim Replace die vorherige Authority überschrieben wurde, oder
- beim immutable Publish ein fremder finaler Name erzeugt wurde.

Die Fehlerbehandlung entfernt nur den Temp-Namen. Sie stellt die vorherige Replace-Authority nicht wieder her und entfernt den fremden immutable Target-Namen nicht sicher.

### Failure-Pfad A – Replace

1. Temp-Inode `T` enthält die erwarteten, geflushten Bytes.
2. `_held_file_identity(T)` erfasst die Identität von `T`.
3. Ein lokaler Akteur benennt `T` um und stellt unter demselben Temp-Namen Datei `X` bereit.
4. `_replace_in_guard()` veröffentlicht `X` über den erneut aufgelösten Temp-Namen.
5. Die bisherige Registry beziehungsweise der bisherige Stage-Index ist bereits überschrieben.
6. `_attest_published_bytes()` erkennt die falsche Identität oder falsche Bytes und wirft einen Fehler.
7. Der Aufrufer erhält zwar einen Fehler, die Authority enthält aber weiterhin `X`; ein Rollback auf die vorherigen Bytes erfolgt nicht.

### Failure-Pfad B – Immutable Publish/Stage-Key

1. Der Temp-Name wird nach der Identitätserfassung durch eine fremde 32-Byte-Datei ersetzt.
2. `_link_in_guard()` erzeugt den finalen Stage-Key als Hardlink auf die fremde Datei.
3. Die finale Attestation wirft wegen Identitäts-/Byteabweichung.
4. Der fremde finale Stage-Key bleibt bestehen.
5. Beim nächsten Initialisierungsversuch wird nur „Immutable artifact already exists“ gesehen; anschließend kann der vorhandene 32-Byte-Key über die gehärtete Read-Boundary geladen werden.
6. Der Angreifer-Key kann danach einen vom Angreifer signierten Stage-Index autorisieren.

### Auswirkung

- Authority-Korruption trotz gemeldetem Fehler.
- Verlust der vorherigen Registry-/Index-/Ledgerbytes beim Replace.
- Persistenz eines fremden immutable Stage-Artefakts oder Stage-Keys.
- Die finale Attestation ist eine nachträgliche Detektion, aber keine nullmutierende Fail-Closed-Grenze.
- Stage-Key, Stage-Index und Pending/Committed-Recovery können nach einem fehlgeschlagenen Commit an Angreiferbytes gebunden sein.
- Die Freeze-Behauptung, der gehaltene Temp-Inode werde publiziert und jede Abweichung fail-closed behandelt, ist nicht erfüllt.

### Konkrete Abhilfe

1. Den ursprünglich geschriebenen Temp-Handle vom Write bis zur Publikation offen halten; kein Close-und-Reopen über den Namen.
2. Die Publikationsoperation muss den gehaltenen Temp-Handle selbst als Quelle verwenden:
   - POSIX beispielsweise `O_TMPFILE` plus `linkat(..., AT_EMPTY_PATH)` für immutable Publish;
   - für Replace eine geeignete handlegebundene Rename-/Exchange-Strategie oder ein nachweislich unmanipulierbarer Temp-Namespace;
   - Windows über File-Rename-/Link-Informationen am geöffneten Dateihandle statt `MoveFileExW`/`os.link` mit erneut aufgelöstem Source-Pfad.
3. Wenn eine Plattform keine echte handlegebundene Quelle unterstützt, darf der Code nicht behaupten, den Temp-Inode sicher zu publizieren. Der Commit muss dann als nicht unterstützte sichere Operation fail-closed vor Target-Mutation enden.
4. Post-Publish-Mismatch darf keinen fremden Target-Namen als künftig vertrauenswürdige Authority zurücklassen. Eine Bereinigung ist nur mit gebundener Target-Identität sicher.
5. RED-Tests ergänzen:
   - Temp-Swap nach Write-Handle-Close;
   - Temp-Swap nach `_held_file_identity`, vor Replace;
   - entsprechender Link-Swap für immutable Stage und Stage-Key;
   - Nachweis, dass bei Fehler weder vorherige Replace-Authority verändert noch ein finales immutable Target hinterlassen wird.

---

## 5. Bewertung der Validation-Attestation und Schema-v8-Closure

| Prüfpunkt | Ergebnis |
|---|---|
| Separate Validation-Attestation-Tabelle | vorhanden: `catalog_draft_validation_attestations` |
| Kontextbindung | Operator, Workspace, Tenant und Scope gebunden |
| Draftbindung | Draft-ID, Version und Payload-Hash gebunden |
| Policybindung | `_VALIDATION_POLICY_VERSION` gebunden |
| Zeitbindung | `validated_at` gespeichert |
| Atomare Erstellung | innerhalb der attestierten SQLite-Write-Transaktion |
| UPDATE-Schutz | `BEFORE UPDATE`-Trigger vorhanden |
| DELETE-Schutz | `BEFORE DELETE`-Trigger vorhanden |
| Publish-Lookup | innerhalb derselben `BEGIN IMMEDIATE`-Transaktion |
| Live-Hash | `sha256(payload_json) == payload_hash` geprüft |
| Rekanonisierung | exakte kanonische JSON-Gleichheit geprüft |
| Semantik | vollständige Snapshotvalidierung erneut ausgeführt |
| Kohärente Draft-Zeilenmanipulation | scheitert ohne passende separate Attestation |
| Schema-Version | Catalog-Schema Version 8 |
| Schema-Fingerprint | Store und Backup an `a855ef…670f` gebunden |
| Backup/Restore | Schema-v8-Fingerprint wird vor Backup, am Snapshot und beim Restore geprüft |
| Ältere/abweichende Schemata | fail-closed; keine implizite Migration |

Die v8-Validation-Manipulationslücke ist für das explizit dokumentierte Modell „kohärente Manipulation der Draft-Zeile ohne Erzeugung einer neuen Attestation“ geschlossen. Die Trigger sind jedoch keine externe Sicherheitsgrenze gegen einen vollständig privilegierten Manipulator der gesamten SQLite-Authority; dafür wäre weiterhin eine externe HMAC-/Signaturverankerung erforderlich.

---

## 6. Regression der v6–v8-Findings

| Frühere Root-Cause | v9-Bewertung |
|---|---|
| v6 Registry-Read nicht handlegebunden | geschlossen |
| v6 Stage-Key-Read nicht handlegebunden | geschlossen |
| v6 Pending ohne vollständigen Kontext | geschlossen |
| v6 komponierbarer Low-Level-Revisionswriter | geschlossen |
| v6 Base-Revision-Provenancevergiftung | geschlossen |
| v6 Planstatusdrift | geschlossen |
| v7 Canonicalization bindet Read an fremdes Resolve-Ziel | für Datei-Reads geschlossen |
| v7 Stage-/Indexbytes nicht über denselben Handle | geschlossen |
| v7 Live-Draft-Payload nicht gegen Hash/Receipt attestiert | geschlossen |
| v7 Pending-Receipt austauschbar | geschlossen |
| v8 kohärente Draftmarker-Manipulation | geschlossen |
| v8 nicht parent-/handlegebundene Authority-Commits | **nicht vollständig geschlossen: P1-1 und P1-2** |

---

## 7. Ausführungs- und Änderungsnachweis

- Keine Tests oder Test-Collector ausgeführt.
- Kein Server gestartet oder beendet.
- Keine Netzwerkzugriffe durchgeführt.
- Kein Anwendungscode produktiv importiert oder ausgeführt.
- Keine SQLite-Probe- oder Testdatenbank erzeugt.
- Keine produktive Authority geschrieben.
- Kein Stage-Key erzeugt.
- Keine Repositorydatei erstellt, verändert oder gelöscht.
- Ausschließlich statische Reads, Inhaltssuchen, Git-Metadatenabfragen und SHA-256-Berechnungen durchgeführt.

**Erstellte oder veränderte Repositorydateien:** keine.
**Aufgetretene Probleme bei der Prüfung:** keine blockierenden; ein anfänglicher rein lesender Shell-Parser-Aufruf scheiterte an Shell-Quoting und wurde ohne Dateieffekt wiederholt.

---

# 8. Schlussentscheidung

```text
VERDICT: REQUEST CHANGES
P0=0
P1=2
P2=0
P3=0
SCOPE DRIFT: NO
FREEZE V9: DRIFTFREI, ABER NICHT APPROVABLE
F5-B: NO-GO
```

Freeze v9 ist formal korrekt bytegebunden und driftfrei. Die Validation-Attestation und Schema-v8-Closure sind statisch plausibel. Die zentrale Authority-Commit-Closure bleibt jedoch unvollständig: Der Parent kann vor seiner Handlebindung substituiert werden, und der gehaltene Temp-Inode ist nicht die tatsächlich handlegebundene Quelle des namensbasierten Replace/Link. Daher ist nach der vorgeschriebenen Null-Finding-Schwelle ausschließlich **`REQUEST CHANGES`** zulässig.