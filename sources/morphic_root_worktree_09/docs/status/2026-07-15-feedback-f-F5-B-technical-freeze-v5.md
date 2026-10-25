# Feedback f – F5-B technischer Freeze v5

Datum: 2026-07-15
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: SUPERSEDED / REQUEST CHANGES / NO-GO

## Reviewausgang

Beide hashgebundenen v5-Reviews endeten driftfrei mit `REQUEST CHANGES`.

- Reviewer 1: `P0=0, P1=1, P2=1, P3=1`.
- Reviewer 2: `P0=1, P1=1, P2=1, P3=0`.

Der Freeze ist seit den anschließenden Scope-Patches technisch überholt und darf nicht als Approval- oder GO-Grundlage verwendet werden. Die Root-Causes werden in einem vollständig neuen Freeze v6 gebunden.

## Supersession

Dieser Freeze ersetzt Freeze v4 (`caf5873eee0c089e11a8a88af9be24c459e98f88492ec113e45df84b47a09655`) nach zwei driftfreien `REQUEST CHANGES`-Reviews aus `deleg_6e67dca5`.

Freeze v4 bleibt als eindeutig superseded markierte Belegdatei erhalten. Es wurde vor den v5-Fixes keine neue Backup-/GO-Kopie erzeugt. Die externe Post-State-ShadowCopy ist erst nach zwei driftfreien `APPROVE` auf einem späteren vollständigen Freeze und dokumentgebundener Schlussfreigabe zulässig.

## Closure der v4-Befunde

1. **Casefold-Provenance-Stripping:** geschützte und kandidierende Source-Entry-IDs werden mit `normalize_catalog_id()` verglichen.
2. **Delete-Schema-Drift:** `delete_draft()` startet mit `_begin_attested_write()`; Drift bleibt nullmutierend.
3. **Stage-Key-Race:** Key-Publikation erfolgt per exklusivem `os.link` Create-if-absent; ein Verlierer verwirft seinen Temp-Key und lädt den zuerst veröffentlichten, erneut kanonisch geprüften Key.
4. **Registry-Revocation-Replay:** Receipt/DB-Schema v7 binden den kanonischen `source_registry_path`; byteidentische Kopien sind keine Authority.
5. **Caller Base-Entries:** Store und öffentlicher Wrapper akzeptieren keine `base_entries`; der Store lädt immutable Base-Entries ausschließlich über `base_revision_id`.
6. **Stage-/Index-Dateiidentität:** Komponenten werden per `lstat` auf Symlink/Reparse geprüft; finale Dateien müssen regulär und single-link sein; `(dev, inode, size, mtime_ns, ctime_ns)` bleibt über den Read stabil.
7. **Toter Publish-Callback:** `source_receipt_validator` und sein `Callable`-/Receipt-Import sind entfernt.
8. **Wirksamer Swap-Test:** Mutation erfolgt nach dem zweiten unter Lock begonnenen Read; Dateiidentitätswechsel bricht nullmutierend ab.
9. **Cross-DB-Replay:** Stage-Index v2 trägt einen HMAC-gebundenen `consumed_receipt_sha256`; Store markiert unter Stage-/Registry-Lock nach Draft+Receipt-Inserts und vor DB-Commit. Ein zweiter Catalog-Store wird fail-closed abgewiesen.
10. **Store-Low-Level-Route:** `CatalogStore._connect()` und `CatalogStore._write_connection()` existieren nicht mehr. Unterstützte Store-APIs exponieren keine schreibbare Connection. Module-interne Connection-/SQL-Primitives gehören zur vertrauenswürdigen Implementierungsboundary; beliebiger feindlicher Code im selben Python-Prozess kann grundsätzlich direkt `sqlite3` und den DB-Pfad verwenden und erfordert für stärkere Isolation einen separaten OS-Prozess/Service.
11. **Scope-Lücke:** v5 bindet alle 14 `core/admin_catalog/*.py`-Module, `core/source_registry.py`, `core/source_data_promotion.py`, CLI und sämtliche zugehörigen Admin-/Source-Vertragstests (38 Dateien).
12. **Plan-/Status-Drift:** aktiver Plan weist F5-A als abgeschlossen, v4 als superseded und F5-B bis Doppel-APPROVE/Post-State-Nachweis als `NO-GO` aus.

## Gebundene Sicherheitsverträge

- Catalog-Schema v7; Fingerprint `e8bcf21ff2317c82e8fd142abf46b6ca9ac1169c7738767c2553ede06e6e0d21`.
- Einziges rohes `BEGIN IMMEDIATE` liegt in `_begin_attested_write`; alle unterstützten Store-Write-Routen attestieren auf derselben Connection vor dem ersten Datenwrite.
- Stage-Index v2 mit HMAC, single-consumption und globalem Cross-DB-Replay-Schutz pro Stage-Authority.
- Stage-Artefakt, Index, Registry und Key sind kanonisch, symlink-/reparse-/hardlink-geschützt.
- Stage-Key liegt außerhalb des Staging-Roots und wird temp-write + fsync + exklusives Create-if-absent veröffentlicht.
- Store-owned Import akzeptiert Stage-/Registry-/Kontext-/Auditinputs und `base_revision_id`, aber keine Entries, Receipts, Proofs oder Callbacks.
- Draft+Receipt werden in einer SQLite-Transaktion geschrieben; Stage-Consumption erfolgt unter denselben Authority-Locks vor Commit.
- Receipt bindet Stage-Artefakt, Batch, Draft, Base-Revision, vollständigen Catalog-Kontext, Registry-Inhalt und kanonischen Registry-Pfad.
- Source-Publish lädt/revalidiert die gebundene Live-Registry selbst und hält den Authority-Lock bis nach Commit.
- Generische Publish-/Direct-Revision-Routen können Source-Provenance weder exakt, mutiert noch case-variant strippen.
- Kein automatisches Activate; kein Runtime-, Web-, Engine-, Scan- oder Netzwerk-Wiring.

## Verifikationsmatrix

- v4-Finding-/Source-/Store-Mikrogates: `56 passed`.
- konsolidierte F5.2/F5.3/CLI/Store/Backup-Matrix: `128 passed, 1 skipped`.
- vollständige Admin-/Source-Matrix: `499 passed, 6 skipped`.
- breite Suite: `983 passed, 8 skipped, 14 failed` in 157.36 s.
- breite Fehlerliste exakt baseline-identisch:
  - 1 datumsabhängiger Consent-Fixturefehler;
  - 13 HTTP-429-Fälle durch kumulierten In-Process-Rate-Limiter.
- dieselben 13 HTTP-Fälle in separaten Prozessen: `13/13 passed`.
- Top-5-Smoke: `1 passed in 98.86s`.
- Ruff: PASS.
- `py_compile`: PASS.
- `git diff --check`: PASS.
- Produktionssymbolscan auf alte Raw-/Proof-/Callback-Routen: 0 Treffer.
- Port 8000 frei; Radi144 auf 8090/PID 3304 unangetastet.

Breitlog:
`C:/Users/Hubert111/AppData/Local/Temp/f5b_full_v5_20260715_140515.log`

## Produktive Authorities

- `config/source_repositories.json`:
  `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3`
- `data/remedies.db`:
  `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`
- `config/source_repositories.json.stage-key`: nicht vorhanden.

## Scope-Hashes (SHA-256, 38 Dateien)

```text
f9771f643cfe1adb7574edf91b656567e26fb974ae9c063a6e221ff8eff6cac4  .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
0c7cc76b5794a4fb39d28977c68ca408e47a6292eaf771994a22a65c263deae6  apps/cli/commands/sources.py
9cafd5de9d63529d713f232944592c0cb3bc28a11e7931c68d9c1bdf0e0b0192  core/source_data_promotion.py
5ab7116f64c16662e6b2c4eb1497dff690497fe11c66d84be5c653711e8f6793  core/source_registry.py
b23ba5f29557a34f5d1727d8197a8c63a7a3e1cb9394b5e25f579a381e5be8ba  core/admin_catalog/__init__.py
db2dc01e9375264075f0e614e944ed886cf73fb9b995c9f5ae15cdee2a23334c  core/admin_catalog/audit_integrity.py
5ead0d7bd319d2b050403e75f71336b575b34c9b1fb2b6b982996a1742e752c5  core/admin_catalog/backup.py
49fdbb14c70f23a5d95d207a49eee0dd48313da234094c76f31cdec3a4b282e8  core/admin_catalog/contracts.py
314b41c04e2ae3544c834ca9ea5a6faca48fe99cb9c84cc11f434d2aae8b08ba  core/admin_catalog/legacy_multiplex_adapter.py
2e6e90d04d53e9fcb6e7231a38099b2d581c2030c63d00f49c24ba30c9e61e31  core/admin_catalog/legacy_profile_adapter.py
0828434114e5870efcea36f144b6c93542863525ead1e40f362777215334057f  core/admin_catalog/legacy_remedy_adapter.py
e5eaf86c7df2c41d8c6e8e4dfd3354d74eb2c51360ce97062d8a9f159932d6b1  core/admin_catalog/paths.py
e0b6f24f68d2572e4736d2b8096cbee7fde3e8f49103de924b9d02ffbe9fd499  core/admin_catalog/runtime_adapter.py
5799f69c698c219ab9314bb8764ef13179f982ae619f6777c7e8b8d50a025aab  core/admin_catalog/service.py
a9353695838fb1abfb13100b69708958551cd4574c6bf8300a409ba75ee2e35e  core/admin_catalog/source_normalization.py
153bfd23cb0bd57b61b0ddc5f4d5bd666c9643538c54ddaf4ee666241e5c0277  core/admin_catalog/source_policy.py
0df5d17294ea4fc5966876a8c920d1bf4fe6d4f66e2e7378c6cd00f8fb27b3ec  core/admin_catalog/store.py
6b2e8156b4297cd9f6c3f566afbde25babdc137e6903ca5067a8c4edec87a5d5  core/admin_catalog/validation.py
cfd88963eab154debe4e7fe141f344ac9dc6c6c221f0d79bb9b9ce875a2f9a59  tests/test_admin_catalog_audit_integrity.py
717610fa3229868a498f12d3d5e6823a21bc5ebccce64a1057019aab395ad01a  tests/test_admin_catalog_backup.py
e927d28e82fa74fc6ea012dd5e84b015bc62868abb62b2892ebe879dadfa3260  tests/test_admin_catalog_contracts.py
87f09b41fe34662eb4b11a0dbf4e3e14e7152b911479bcb078f593a9a54db7af  tests/test_admin_catalog_legacy_multiplexes.py
6f5c2630b4db1d3ac0eed6db503630b5a759e957a72985e3b84808c57bff8726  tests/test_admin_catalog_legacy_profiles.py
8fa092bc74a077f170294b23b35fcefb69136447b6f39a6f949c145e6c3845e9  tests/test_admin_catalog_legacy_remedies.py
388096c672ff5677674fef67530881e6c98c29455ba31afff89b0c054be542ac  tests/test_admin_catalog_paths.py
853c5e4d5aab7edd6671b491d3c67ddb2fecb4aa3f1c285eb5a0a5f9c3fbd79a  tests/test_admin_catalog_runtime_adapter.py
1b31db8a26fcb5d52aded770a41bfbde3839400d7522e8e0fa4721f9057ef6b1  tests/test_admin_catalog_service.py
c1f6b86206e35ff49f2f930fc6dc5e1bc8de06ac134a374033961c2a0a95f113  tests/test_admin_catalog_store.py
22f2e5e167afce8d2544c76e476a184f8a5d8ccd751e702f2c4674c0fe6d1d2e  tests/test_admin_catalog_validation.py
eec32694a99d1b0001eb79ecb962f17eb9250e7a124fd478ef88a6cae8ad675a  tests/test_admin_remedy_multiplex_management.py
30c4c242e87e0ecd5c7cc28a00952f25bc5b486a8cb08d49753d6c1651016e80  tests/test_admin_source_normalization.py
885e0280b21ec040da089060e638a9b7de4c6f3f24b32052e8a95a158f2e0736  tests/test_admin_source_policy.py
df7ca75b540300d8168a760af0eee48770dee25b9116b2c8237a7f3b1adc1feb  tests/test_f5b_review_findings.py
f34f36d4b1be3da882ec4b838f6fec4486b6fd3db25eb6c939f89929d5d2818c  tests/test_source_data_draft_import.py
de2a73aee053bf2301fb1cb5f6ef47100345009f20a11af1ab63984cfc1901b9  tests/test_source_data_promotion.py
7cc243b7e9e528b7b970b384c24820303726b481f2b4864c309d9b4ede17b062  tests/test_source_registry.py
a4e4be6b05768bd2bd6c6143cf303f4b25f8baa8fd8e60a3b21868eabf4c507e  tests/test_source_registry_atomicity.py
72a53d49e9f16b69c1b2d074eac45b69e77f4fb7c258e88f209165eaf16fac15  tests/test_source_registry_cli.py
```

## Reviewregel

`APPROVE` nur bei Start=Ende für Freeze, alle 38 Scope-Dateien und beide Authorities sowie P0=P1=P2=P3=0. Bei Scope-Drift einziges gültiges Verdict: `INVALIDATED BY SCOPE DRIFT`. Reviews sind strikt statisch/read-only; keine Tests, Writes, Server oder Netzwerkzugriffe.

Bis zu zwei unabhängigen driftfreien `APPROVE` bleibt F5-B `NO-GO`.
