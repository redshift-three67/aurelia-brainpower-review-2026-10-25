# Technisches Review 1 - F5-B Technical Freeze v10

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
| P1 | POSIX Publish bindet den finalen Publish weiter an den Temp-Dateinamen, nicht an das zuvor gehaltene Temp-Inode/Handle. Dadurch ist das v9 Temp-Inode-Finding fuer POSIX nicht geschlossen. | `core/source_registry.py:1087`, `core/source_registry.py:1254`, `core/source_registry.py:1269`, `core/admin_catalog/backup.py:154` |

## 3. Finding im Detail

### P1 - POSIX Publish ist nicht source-inode-gebunden

`_held_file_identity()` haelt auf POSIX zwar einen FD auf die Temp-Datei, aber
`_replace_in_guard()` und `_link_in_guard()` veroeffentlichen danach per
`os.replace(source.name, ...)` beziehungsweise `os.link(source.name, ...)` erneut
ueber den Namen. Ein Writer im Authority-Parent kann zwischen Identity-Capture
und Publish den Temp-Namen austauschen.

Die nachgelagerte Attestation erkennt das erst nach Mutation. Bei Replace ist die
Registry-/Stage-/Ledger-Datei dann bereits ersetzt, bei Link/Backup kann ein
fremdes Immutable-Ziel stehen bleiben. `backup._publish_without_overwrite()` erbt
dieses Risiko ueber `_link_in_guard()`.

Konkrete Abhilfe:

1. POSIX-Publish muss aus dem gehaltenen FD/Inode erfolgen, nicht aus `source.name`.
2. Alternativ muessen die betroffenen POSIX-Authority-Operationen fail-closed vor
   jeder Target-Mutation enden, bis echte FD-/Inode-gebundene Semantik vorhanden ist.
3. Ergaenzender Regressionstest: POSIX mit vorhandenem `dir_fd`-Support darf vor
   `replace/link` nicht mutieren, wenn kein source-inode-bound Publish garantiert ist.

## 4. Recommendation

`REQUEST CHANGES`. Freeze v10 ist nicht approvable. Der Scope ist stabil, aber
wegen des P1-Findings darf nicht zum Dokumentfreeze fortgeschritten werden.
