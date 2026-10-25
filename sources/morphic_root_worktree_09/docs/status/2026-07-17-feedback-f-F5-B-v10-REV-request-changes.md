# Feedback f / F5-B v10 / Gate REV: Request Changes

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **REV v10 driftfrei, aber REQUEST CHANGES; F5-B bleibt NO-GO**

## 1. Kurzfazit

Die zwei technischen read-only Reviews auf Freeze v10 wurden driftfrei
ausgefuehrt. Beide Reviews kamen unabhaengig zum gleichen Blocker: Die POSIX-
Publish-Primitive sind trotz `dir_fd` nicht source-inode-gebunden. Damit ist
Freeze v10 nicht approvable und darf nicht in Dokumentfreeze, Dokumentreviews
oder Post-State-ShadowCopy uebergehen.

## 2. Review-Ergebnisse

| Review | Verdict | Findings | Scope-Drift | Bericht |
|---|---|---:|---|---|
| Review 1 | REQUEST CHANGES | `P0=0, P1=1, P2=0, P3=0` | keine | `docs/reviews/2026-07-17-feedback-f-F5-B-technical-review-v10-1.md` |
| Review 2 | REQUEST CHANGES | `P0=0, P1=1, P2=0, P3=0` | keine | `docs/reviews/2026-07-17-feedback-f-F5-B-technical-review-v10-2.md` |

## 3. Driftnachweise

| Nachweis | Wert |
|---|---|
| FreezeDoc SHA-256 | `0d3f15ceded24d8b62547f9ffcffabdd784f211afebf19dc6d40860d8b583090` |
| Scope-Datei SHA-256 | `dd9449cd364e10920280b5d7f022f1c8f453d32b1cf7b29f03473dc95eaf15fd` |
| Manifest SHA-256 | `19b851aead78c27885eb5a36b75430b231e9dcb9ea887ffe486b52ab35cd6cb1` |
| Scope-Hashes | `113/113 OK` in beiden Reviews |
| Branch | `operator-workbench-phase1` |
| HEAD | `619a1f5485a151816e32732929a6a823839ccb57` |

## 4. Konsolidiertes Finding

| Prioritaet | Finding | Bewertung |
|---|---|---|
| P1 | POSIX `dir_fd` Publish nutzt fuer `replace/link` weiter `source.name` und garantiert nicht, dass der gehaltene Temp-Inode publiziert wird | valide, blockierend |

Root Cause:

1. `_directory_commit_guard()` haelt den POSIX-Parent-FD.
2. `_write_temporary_bytes()` erzeugt die Temp-Datei weiterhin pfadbasiert.
3. `_held_file_identity()` haelt einen FD auf die sichtbare Temp-Datei.
4. `_replace_in_guard()` / `_link_in_guard()` publizieren danach erneut ueber
   `source.name` relativ zum Parent-FD.
5. Ohne echte FD-/Inode-gebundene POSIX-Publikation bleibt ein Name-Swap-Fenster.

## 5. Entscheidung

Die Reviewfindings sind technisch korrekt. Der sichere kurzfristige Fix ist ein
expliziter POSIX-Fail-Closed-Vertrag fuer diese mutierenden Authority-Publish-
Primitive, bis eine echte source-inode-gebundene POSIX-Publikation implementiert
und getestet ist.

## 6. Exakt hier weiter

Naechster Block: **R1 POSIX source-inode-bound fail-closed**.

| Reihenfolge | Schritt | Exit-Kriterium |
|---:|---|---|
| 1 | RED-Test fuer POSIX mit vorhandenem `dir_fd`-Support schreiben | Test zeigt Mutation oder fehlendes Fail-Closed |
| 2 | Minimaler Fail-Closed-Fix in `core/source_registry.py` | POSIX bricht vor `replace/link` mit `SourceRegistryError` ab |
| 3 | Fokus- und breite Regression | Source/Admin/Web/Vollsuite/Top-5 gruen |
| 4 | neuen Freeze erzeugen | Freeze v11 ersetzt v10 |
| 5 | neue Reviews auf v11 | erst danach wieder Dokumentfreeze moeglich |
