# Feedback f: F5-B/v10 Gate M2 v7-to-v8 Migration Closure

Stand: 2026-07-16
Worktree: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Gate M2: **TECHNISCH GESCHLOSSEN**
F5-B gesamt: **NO-GO**

## Entscheidung

Gate M2 aus
`docs/developer-current-state-2026-07-16/02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md:61-69`
fokussiert verifiziert.

`migrate_catalog_v7_to_v8(db_path)` akzeptiert ausschliesslich die exakte,
`e8bcf21ff2317c82e8fd142abf46b6ca9ac1169c7738767c2553ede06e6e0d21`.
Eine vollstaendige aktuelle v8-Datenbank wird byteunveraendert als
idempotenter No-op erkannt. Jeder andere Zustand bleibt gesperrt.

Die Migration ist nicht an das normale `CatalogStore`-Oeffnen gekoppelt. Der
normale Store lehnt v7 weiterhin kontrolliert und ohne Teilmigration ab.

## Sicherheitsvertrag

- Die Migration oeffnet die bereits existierende, nicht leere DB und beginnt
  auf derselben Connection mit `BEGIN IMMEDIATE`.
- Vor jeder Mutation prueft sie den exakten v7-Schemafingerprint.
- Sie erzeugt ausschliesslich die aktuellen Validation-Attestation-DDL-Objekte
  aus der zentralen Store-DDL-Konstante.
- Sie invalidiert alle historischen Draft-Marker
  `validated_version` und `validated_payload_hash`.
- Vor Commit prueft sie `PRAGMA foreign_key_check`, `PRAGMA integrity_check`
  und die exakte aktuelle v8-Schema-Authority
  `3dde32b404989c89c392a272c086d09b8b9ac2cb7e2f61372b6d5f41fa5385c5`.
- Jede Ausnahme rollt die laufende Transaktion vollstaendig zurueck.

Ein migrierter Draft kann nicht mit einem impliziten oder lokal abgeleiteten
Key revalidiert werden. `CatalogStore.mark_draft_validated()` verlangt weiter

## Vertraege und Nachweise

`tests/test_admin_catalog_v7_migration_contract.py` deckt ab:

- Migration des historischen Known-Answer-v7 mit Erhalt aller Domainzeilen,
  v8-Attestationobjekten und invalidierten Legacy-Markern;
- idempotenten v8-Zweitstart ohne Checkpoint oder Dateirewrite;
- fail-closed Ablehnung unbekannter sowie synthetischer Preview-v8-Formen;
- Fault Injection vor DDL, nach DDL und unmittelbar vor Commit, jeweils mit
  vollstaendig nutzbarem v7 nach Rollback;
- Rollback eines fehlgeschlagenen Integrity-Checks;
- erforderliche externe Revalidierung nach Migration.

Aktuelle Laufnachweise:

```text
tests/test_admin_catalog_v7_migration_contract.py
14 passed in 1.28s

Admin-Catalog-Nachbarmatrix
274 passed, 5 skipped in 23.50s
```

Die fuenf Skips stammen aus bestehenden Testmarkierungen; die Matrix enthielt
keine Fehlschlaege.

Zusaetzlich:

- `py_compile`: PASS;
- `ruff check`: PASS mit dem vorhandenen systemweiten Ruff unter Python 3.12;
- `git diff --check`: Exit 0; nur bekannte LF-to-CRLF-Warnungen in
  fachfremden WIP-Dateien.

## Review

Ein fokussiertes Read-only-Review der M2-Produktions- und Vertragsscope-Dateien
ergab `APPROVED` ohne P0-P3-Befunde.

Als nicht gate-blockierende zusaetzliche Testabdeckung bleiben moeglich:

- eine absichtlich korrumpierte, weiterhin exakt-v7-fingerprintgebundene
  Datenbank fuer einen direkten `foreign_key_check`-Fehlerpfad;
- ein Publish-Versuch vor und nach externer Revalidierung.

Die historische v7-Trigger- und FK-Logik weist den naheliegenden Orphan-Insert
bereits selbst ab. Die M2-Integritaetsfehler-Transaktionsgrenze wird deshalb
ueber einen kontrollierten Fehler an der Integritaetspruefung belegt.

## Beruehrte Dateien

- `core/admin_catalog/migration.py`
- `core/admin_catalog/store.py`
- `tests/admin_catalog_v7_fixture.py`
- `tests/test_admin_catalog_v7_migration_contract.py`

Es wurden keine produktiven Datenbanken, Backups, Keys, Runtimepfade oder
Authorities mutiert. M3, die v7-Backupentscheidung und -publikation, bleibt
