# Feedback f: F5-B/v10 Gate M3 v7 Backup Migration Closure

Stand: 2026-07-16
Worktree: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Gate M3: **TECHNISCH GESCHLOSSEN**
F5-B gesamt: **NO-GO**

## Entscheidung

Gate M3 aus
`docs/developer-current-state-2026-07-16/02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md:71-82`

`migrate_catalog_backup_v7_to_v8(source_backup_root, target_backup_root)`
publiziert ausschliesslich ein neues vollstaendiges v8-Bundle. Das v7-Quellbundle
bleibt bytegleich. Der normale `restore_catalog_backup()`-Pfad bleibt v8-only.

## Migrationsvertrag

- Das Quellbundle muss exakt `catalog.sqlite3` und `manifest.json` enthalten.
- Das Manifest ist an Version 1, `catalog_schema_version == 7`, Dateiname,
  Dateigroesse, SHA-256 und die no-activation-Boundary gebunden.
- Reparse-Points, SQLite-Sidecars, fehlerhafte SQLite-Integritaet und jeder
  andere als der historische v7-Schemafingerprint
  `e8bcf21ff2317c82e8fd142abf46b6ca9ac1169c7738767c2553ede06e6e0d21`
  werden vor Snapshot-Erzeugung abgewiesen.
- Der Snapshotname wird mit `open("xb")` exklusiv reserviert. Eine vorhandene
  fremde Datei unter dem generierten Namen wird weder geoeffnet noch geloescht.
- Der tatsaechliche Snapshot muss vor Migration bytegleich zum v7-Manifest
  sein. Danach ruft M3 die atomare M2-Migration auf und prueft Sidecars,
  SQLite-Integritaet und die exakte aktuelle v8-Schema-Authority.
- Erst dann wird ueber `create_catalog_backup()` ein neues Bundle mit frischem
  v8-Manifest am bisher nicht vorhandenen Ziel erstellt.
- Der M3-Cleanup betrifft nur den exklusiv reservierten Snapshot. Er loescht
  weder Quellbundle noch Zielbundle oder fremde Artefakte.

## Testvertraege

`tests/test_admin_catalog_v7_backup_migration_contract.py` deckt ab:

- valides v7-Bundle zu konsumierbarem v8-Bundle;
- byteidentische v7-Quelle und fortbestehende v8-only-Restore-Grenze;
- manipuliertes Manifest, DB oder Sidecar ohne Zielbundle;
- unbekannte, partielle-v8- und aktuelle-v8-Quellschemata fail-closed;
- M2-Fault-Injection vor DDL, nach DDL und vor Commit ohne Zielbundle;
- vorhandene und waehrend Publikation entstandene Zielroots ohne Overwrite;
- vorhandenen generierten Snapshotnamen ohne Oeffnen oder Loeschen des
  Fremdartefakts.

Aktuelle Laufnachweise:

```text
M3-Vertragssuite
14 passed in 1.91s

M3 + M2 + v8-Backup-Fokusmatrix
59 passed, 1 skipped in 7.54s

Admin-Catalog-Matrix
288 passed, 5 skipped in 28.07s
```

Die Skips sind bestehende hostabhaengige Testmarkierungen; die aufgefuehrten
M3-Matrizen sind gruen.

Zusaetzlich:

- `py_compile`: PASS;
- `ruff check`: PASS;
- `git diff --check`: Exit 0; nur bekannte LF-to-CRLF-Warnungen in
  fachfremden WIP-Dateien.

## Vollsuite-Baseline

Die frische Projektvollsuite ist kein M3-Regressionstest, aber als
Abschlussnachweis ausgefuehrt worden:

```text
14 failed, 1047 passed, 8 skipped in 197.83s
```

Die 14 historischen Fehler lagen ausserhalb des M3-Scopes:

- `tests/test_group_member_consent_revocation.py` verwendet den festen
  Zeitwert 2026-07-12; dessen angeblich zukuenftige Consent-Expiry liegt am
  Ausfuehrungstag in der Vergangenheit und wird korrekt fail-closed abgewiesen.
- 13 Web-/Workbench-Tests erhalten HTTP 429, weil
  `apps/web/security.py` einen globalen, zwischen App-Instanzen geteilten
  `_rate_limit_store` pro Loopback-IP beibehalt. Ein isoliert ausgefuehrter
  betroffener Web-Test ist gruen.

Die Baselineursachen wurden anschliessend minimal testseitig repariert:

- Der Consent-Test verankert seine kuenstliche Ablaufzeit jetzt an
  `datetime.now(UTC)` statt an einem ablaufenden Kalenderdatum.
- `tests/conftest.py` leert den absichtlich prozesslokalen Web-Rate-Limit-Speicher
  vor und nach jedem Test. Das produktive Rate-Limit bleibt unveraendert.

Gezielte Nachweise: Consent-Modul `7 passed`; betroffene Web-/Workbench-Module
`32 passed`. Die anschliessende frische Projektvollsuite ist gruen:

```text
1061 passed, 8 skipped in 207.23s
```

## Review

Das erste M3-Review fand P1: Ein nur UUID-basierter Tempname konnte vor dem
SQLite-Open von einem fremden Namespace-Inhaber belegt werden. Der neue
Preclaim-RED belegt den Fehler. M3 reserviert den Namen jetzt exklusiv und
bereinigt ihn nur nach erfolgreicher Reservierung.

Das anschliessende Read-only-Re-Review ergab `APPROVED` ohne P0-P3-Befunde.

Die verbleibende strengere Boundary bleibt explizit Gate B1: Eine vollstaendig
handlegebundene SQLite-Temp- und Bundle-Publikation muss nach der bestehenden
Source-Registry-Authority-Architektur folgen. Insbesondere ersetzt M3 B1 nicht
bei Pfadersetzung nach erfolgreicher Temp-Reservierung.

## Beruehrte Dateien

- `core/admin_catalog/backup.py`
- `core/admin_catalog/migration.py`
- `tests/admin_catalog_v7_fixture.py`
- `tests/test_admin_catalog_v7_backup_migration_contract.py`
- `tests/conftest.py`
- `tests/test_group_member_consent_revocation.py`

Es wurden keine produktiven Datenbanken, Backups, Keys, Runtimepfade oder
Authorities mutiert. Der naechste verbindliche Block ist Gate B1.
