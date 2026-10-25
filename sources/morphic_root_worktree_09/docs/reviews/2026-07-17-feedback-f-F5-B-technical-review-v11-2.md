# Technisches Review 2 - F5-B Technical Freeze v11

Datum: 2026-07-17
Reviewart: unabhaengig, adversarial, statisch, read-only
Freeze-Dokument: `docs/status/2026-07-17-feedback-f-F5-B-technical-freeze-v11.md`
Verdict: **REQUEST CHANGES**
Konfidenz: **HIGH**
Finding-Zaehlung: `P0=0, P1=1, P2=0, P3=0`
Scope-Drift: **keine**
Review-Run: `019f701f-23f3-7ab2-918e-604fc8616f0a`

## 1. Scope-Verifikation

| Nachweis | Erwartung | Ergebnis |
|---|---:|---|
| Scope-Dateien | `118` | `118/118 OK` |
| FreezeDoc SHA-256 | `081efaf4484acc662036b56419f1679d991d533309735eb867adfe98498ff967` | PASS |
| Scope-Datei SHA-256 | `fb58c10e90c6cc272aa2456c2df535a6aca7e055fddd184ec3d966d6f2c23d2d` | PASS |
| Manifest SHA-256 | `eb9455e063b13c7f00f7e095769d91b906cd6a2c4ffeb1b133c70bcf14eb25f5` | PASS |
| Branch | `operator-workbench-phase1` | PASS |
| HEAD | `619a1f5485a151816e32732929a6a823839ccb57` | PASS |

Das Review ist driftfrei. Das Verdict ist daher nicht durch Scope-Drift
invalidiert.

## 2. Finding-Matrix

| Prioritaet | Finding | Fundstellen |
|---|---|---|
| P1 | Backup-Erzeugung kann eine nach Schema-Validierung manipulierte temporaere DB als autoritativen Backup-Hash manifestieren, wenn die Mutation gleiche Groesse und gleiche Inode-Identitaet behaelt. | `core/admin_catalog/backup.py:154`, `core/admin_catalog/backup.py:335`, `core/admin_catalog/backup.py:337`, `core/admin_catalog/backup.py:342` |

## 3. Finding im Detail

`create_catalog_backup()` validiert die temporaere SQLite-Kopie zunaechst mit
`_assert_catalog_schema(temporary_db)`. Danach publiziert
`_publish_without_overwrite()` das Artefakt und vergleicht am Ende nur
`st_dev`, `st_ino` und `st_size` gegen die gehaltene Temp-Identitaet.

Eine same-size Mutation der temporaeren DB nach der Schema-Validierung, aber vor
oder waehrend Publish, kann dadurch in `backup_db` landen. Anschliessend baut der
alte Code das Manifest aus `backup_db.stat().st_size` und `_sha256(backup_db)`
und wuerde somit die manipulierten Bytes als autoritativen Backup-Hash
festschreiben.

## 4. Recommendation

`REQUEST CHANGES`. Die nach Schema-/Integritaetspruefung gemessenen Bytes muessen
an den Publish gebunden werden. Manifest und Completion duerfen nicht aus einem
spaeter erneut gelesenen, potentiell schon veraenderten Zielartefakt abgeleitet
werden, sondern aus den validierten Snapshot-Werten.
