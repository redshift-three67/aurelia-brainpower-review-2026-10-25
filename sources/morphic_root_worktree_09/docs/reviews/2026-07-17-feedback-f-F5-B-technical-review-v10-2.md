# Technisches Review 2 - F5-B Technical Freeze v10

Datum: 2026-07-17
Reviewart: unabhaengig, adversarial, statisch, read-only
Freeze-Dokument: `docs/status/2026-07-17-feedback-f-F5-B-technical-freeze-v10.md`
Verdict: **REQUEST CHANGES**
Konfidenz: **HIGH**
Finding-Zaehlung: `P0=0, P1=1, P2=0, P3=0`
Scope-Drift: **keine**

## 1. Scope-Verifikation

| Nachweis | Start | Ende | Ergebnis |
|---|---|---|---|
| FreezeDoc SHA-256 | `0d3f15ceded24d8b62547f9ffcffabdd784f211afebf19dc6d40860d8b583090` | identisch | PASS |
| Scope-Datei SHA-256 | `dd9449cd364e10920280b5d7f022f1c8f453d32b1cf7b29f03473dc95eaf15fd` | identisch | PASS |
| Manifest SHA-256 | `19b851aead78c27885eb5a36b75430b231e9dcb9ea887ffe486b52ab35cd6cb1` | identisch | PASS |
| Scope-Hashes | `113/113 OK` | `113/113 OK` | PASS |
| Branch | `operator-workbench-phase1` | identisch | PASS |
| HEAD | `619a1f5485a151816e32732929a6a823839ccb57` | identisch | PASS |

Das Review ist driftfrei. Das Verdict ist daher nicht `INVALIDATED BY SCOPE DRIFT`.

## 2. Finding-Matrix

| Prioritaet | Finding | Fundstellen |
|---|---|---|
| P1 | POSIX `dir_fd` Publish ist nicht source-inode-bound: Tempbytes werden nach Parent-Bindung per Pathname erzeugt, `replace/link` nutzt spaeter aber nur `source.name` relativ zum gebundenen Directory. | `core/source_registry.py:965`, `core/source_registry.py:1247`, `core/source_registry.py:1298`, `core/source_registry.py:1315` |

## 3. Finding im Detail

### P1 - POSIX Temp-Quelle ist vor Mutation nicht an den gehaltenen Inode gebunden

`_directory_commit_guard()` bindet den Parent-Directory-FD. Danach rufen
`_atomic_replace_json()` und `_atomic_publish_bytes()` jedoch
`_write_temporary_bytes(target, ...)` auf, das `target.parent / tmp-name` per
Pathname oeffnet. Auf POSIX verhindert ein gehaltener Directory-FD nicht, dass der
sichtbare Parent-Pfad umbenannt oder neu erstellt wird.

Wenn der Authority-Parent-Pfad nach Guard-Open und vor Temp-Erzeugung getauscht
wird, kann die gehaltene Temp-Identitaet zur neu erstellten Pfadansicht gehoeren,
waehrend `_replace_in_guard()` beziehungsweise `_link_in_guard()` `source.name`
im urspruenglich gebundenen Directory-FD veroeffentlicht. Ein Angreifer mit
Kontrolle ueber dieses alte Directory kann dort denselben Basename erzeugen.

Die finale Identity-/Byte-Attestation kann dann erst nach `os.replace()` oder
`os.link()` fehlschlagen. Das betrifft Registry Save, Stage-Artefakte,
Stage-Index, Ledger, Rollback-Snapshots und Stage-Key-Publikation. Beim Stage-Key
ist das besonders kritisch, weil ein fehlgeschlagener ambiger Publish eine
angreifergesteuerte 32-Byte-Keydatei hinterlassen koennte.

Konkrete Abhilfe:

1. Temp-Datei, Write, fsync, Link/Replace und Cleanup muessen vollstaendig relativ
   zum gebundenen Directory-FD erfolgen und exakt denselben Inode publizieren.
2. Alternativ muss POSIX fuer diese Authority-Mutationen fail-closed vor jeder
   Target-Mutation enden.
3. Regressionen muessen Replace, Immutable Publish, Stage-Key, Ledger und
   Rollback-Snapshot abdecken.

## 4. Recommendation

`REQUEST CHANGES`. Nicht zum Dokumentfreeze fortschreiten, bis POSIX source-inode
gebunden ist oder die betroffenen POSIX-Pfade fail-closed vor Mutation enden.
