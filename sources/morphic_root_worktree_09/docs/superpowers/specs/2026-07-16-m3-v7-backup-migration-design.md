# M3 v7 Backup Migration Design

## Purpose

Provide one explicit offline API that converts a fully verified v7 Admin Catalog
backup bundle into a new complete v8 backup bundle. The original v7 bundle is
an immutable input and is never restored or migrated at the requested output
path.

## Public API

`migrate_catalog_backup_v7_to_v8(source_backup_root, target_backup_root) -> Path`

- Both paths must be absolute, traversal-free paths.
- The source must be an exact v7 backup bundle.
- The target must not exist and its existing parent must not contain a reparse
  point.
- On success the returned resolved path is the new v8 bundle root.
- The migration API rejects current v8 and every other source state. Existing
  v8 bundles remain the responsibility of the ordinary v8 restore path.

## Source Acceptance Boundary

Only this M3 API accepts a v7 backup manifest. The ordinary
`restore_catalog_backup()` remains v8-only and continues to reject v7 bundles
without creating a target.

The M3 source check performs, before creating any target bundle:

1. bundle-root, manifest, database, parent and requested target safety checks;
2. an exact two-file bundle check for `catalog.sqlite3` and `manifest.json`;
3. v7 manifest-schema version, `catalog_schema_version == 7`, activation
   boundary, database filename, byte count and SHA-256 validation;
4. no SQLite WAL, SHM or journal sidecar validation;
5. SQLite integrity validation and the exact historical v7 schema fingerprint.

The existing manifest parser will be minimally generalized to validate an
explicit expected catalog schema version. Its default remains the current v8
version, preserving existing backup and restore behavior.

## Migration And Publication Flow

1. Validate the source bundle and target preconditions.
2. Exclusively reserve an owned, uniquely named temporary SQLite snapshot beside
   the target bundle root with `open("xb")`, never inside the source bundle.
3. Copy the verified source database with the existing SQLite backup API.
4. Revalidate that the actual snapshot has the source manifest byte count and
   SHA-256 before migration. This catches source races after initial validation.
5. Run `migrate_catalog_v7_to_v8()` against that temporary snapshot.
6. Revalidate no sidecars, SQLite integrity and the exact current v8 schema.
7. Pass the migrated snapshot to the existing v8 backup creator, which writes
   a new two-file bundle with a v8 manifest at the otherwise nonexistent target
   root.
8. Remove only the owned temporary snapshot on failure or after publication.

The output manifest is newly calculated from the newly created v8 snapshot. It
does not reuse the v7 database byte count or SHA-256.

## Failure Semantics

- Invalid manifest, hash, sidecar, v7 schema, SQLite integrity, unknown schema
  or migration failure raises without creating `target_backup_root`.
- A pre-existing target root raises `FileExistsError` and is not overwritten.
- A pre-existing generated temporary snapshot name raises `FileExistsError`
  before SQLite opens or cleanup can remove the foreign artifact.
- A concurrent target owner is handled by the existing non-overwriting v8
  backup creation boundary; its data is not removed.
- M2 transaction failure leaves only a temporary v7 snapshot, which M3 removes
  as owned work. It does not publish any partial v7 or v8 bundle.
- The source bundle is opened read-only for validation and is never written,
  renamed, deleted or supplemented with sidecars by M3.

## Scope Boundary

M3 builds a complete consumable v8 bundle using the existing v8 bundle format.
The stronger shared durable filesystem publication protocol, completion record,
handle-bound SQLite output and parent/temp-swap contracts belong to later Gate
B1 and are not reimplemented here.

## Tests

Add a dedicated M3 contract suite with a v7 bundle fixture and these cases:

- valid exact v7 bundle produces a v8 bundle that the normal v8 restore API
  accepts;
- source database and manifest hashes are byte-identical before and after;
- manifest, database or sidecar tampering leaves no target bundle;
- unknown, partial-v8 and current-v8 source schemas are rejected;
- injected M2 failures before DDL, after DDL and before commit leave no target
  bundle and preserve the source bundle;
- pre-existing and concurrently created targets are never overwritten;
- a pre-existing generated temporary snapshot is never opened or deleted;
- every failure removes M3-owned temporary snapshots.

## Verification

Run the new M3 contract suite first, then the Admin Catalog backup, store and
migration suites. Follow with `py_compile`, Ruff and `git diff --check`.
