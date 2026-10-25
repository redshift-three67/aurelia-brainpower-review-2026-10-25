# Feedback f – F5-B technischer Freeze v9

Datum: 2026-07-15
Freeze-Zeitanker: `2026-07-15T22:45:19+02:00`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: `SUPERSEDED / REQUEST CHANGES / NO-GO`

## Technischer Reviewausgang

Beide unabhängigen Reviews waren driftfrei und an die ursprünglichen Bytes dieses
Freeze-Dokuments mit SHA-256
`c580b92876af7e444caffefd7a7e15a99fc546fea2266e62b83e596795553c69`
gebunden.

- Review 1: `REQUEST CHANGES`, `P0=0, P1=2, P2=0, P3=0`.
- Review 2: `REQUEST CHANGES`, `P0=0, P1=4, P2=0, P3=0`.
- Vollständiger Review 1:
  `docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v9-1.md`
  - SHA-256: `4807b4057cb3dbdc4ca88806e3dc30458f05ac06eaf8cd6990786c59d8975755`
- Vollständiger Review 2:
  `docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v9-2.md`
  - SHA-256: `761bac0c6c63c9985530978169a5632ddca9d64f9bf1704dbaee946ffffde1db`

Freeze v9 ist nicht approvable. Der Dokumentfreeze bleibt blockiert. Die konsolidierten
Root-Cause-Klassen sind: Authority-Parent vor Handlebindung austauschbar;
Temp-Inode nicht selbst Publikationsquelle; Validation-Attestation ohne externe
Authentisierung forgebar; fehlende explizite Schema-v7→v8-/Backupmigration; sowie
Backup-/Restore-Publikation außerhalb der durable Commit-Boundary.

## Gate

Freeze v9 ersetzt den driftfrei reviewten, aber wegen eines `REQUEST CHANGES` mit
zwei P1 verworfenen Freeze v8. Freeze v8 und beide vollständigen v8-Reviews bleiben
unverändert als historische Evidenz im Scope erhalten.

Dieser Freeze erlaubt ausschließlich zwei neue unabhängige technische read-only
Reviews. Er ist weder Dokumentfreeze noch Backup-, ShadowCopy- oder GO-Freigabe.
F5-B bleibt `NO-GO`.

## v8-Reviewausgang

Reviewgebundener ursprünglicher Freeze-v8-SHA-256:
`1b697e2be4c9b9e276e123b178ba1d4e1050fd641b518e6ec12c26efe48d006d`

- Review 1: `APPROVE`, `P0=0, P1=0, P2=0, P3=0`.
- Review 2: `REQUEST CHANGES`, `P0=0, P1=2, P2=0, P3=0`.
- Review 1 Repository/Cache bytegleich:
  `2b4650affa063ca9d071aa2f92c2c3e13c5102c37265f4ffdc03eeb7142f07dd`.
- Review 2 Repository/Cache bytegleich:
  `47448b4d9bf7a13cf1662d7bb0970ee88607676cdb0012a3154768c9ada5e924`.

## V9-R1 – Unabhängige immutable Validation-Attestation

Betroffen:

- `core/admin_catalog/store.py`
- `core/admin_catalog/backup.py`

Closure:

1. Erfolgreiche Draftvalidierung erzeugt in derselben attestierten SQLite-Transaktion
   eine separate Zeile in `catalog_draft_validation_attestations`.
2. Die Attestation bindet den vollständigen Catalog-Kontext, Draft-ID, Draft-Version,
   kanonischen Payload-Hash, Policy-Version und Attestierungszeitpunkt.
3. `BEFORE UPDATE`- und `BEFORE DELETE`-Trigger machen Attestierungen append-only.
4. Publish liest innerhalb derselben `BEGIN IMMEDIATE`-Transaktion eine exakt passende
   Attestation für die live gelesene Draft-Version und den live gespeicherten Hash.
5. Anschließend bleiben die bereits bestehenden Prüfungen aktiv:
   `sha256(payload_json) == payload_hash`, exakte Rekanonisierung, semantische
   Snapshotvalidierung und Source-Receipt-Reattestation.
6. Eine kohärente Manipulation von `payload_json`, `payload_hash` und
   `validated_payload_hash` kann keine passende immutable Attestation erzeugen und
   scheitert nullmutierend vor Revision und Audit.
7. Catalog-Schema und Backupvertrag wurden gemeinsam von Version 7 auf Version 8
   angehoben und an den neuen vollständigen Schema-Fingerprint gebunden.

Adversarialer Vertrag:

- Der neue RED-Test manipulierte alle co-lokalen Draft-/Validierungsmarker konsistent
  auf einen anderen fachlich gültigen Snapshot; vor dem Fix wurde dieser veröffentlicht.
- Nach dem Fix scheitert Publish wegen fehlender immutable Attestation.
- Ein zusätzlicher Test beweist, dass Attestierungszeilen weder aktualisiert noch
  gelöscht werden können.

## V9-R2 – Parent-/Handle-gebundene und crash-durable Authority-Commits

Betroffen:

- `core/source_registry.py`
- `core/source_data_promotion.py`

Closure:

1. Alle Registry-, Stage-, Stage-Index-, Ledger-, Rollback-Snapshot- und
   Stage-Key-Publikationen verwenden die gemeinsamen Primitive
   `_atomic_replace_json`, `_atomic_publish_json` beziehungsweise
   `_atomic_publish_bytes`.
2. Vor Temp-Erzeugung wird jeder Parentpfad auf Symlink-/Reparse-Komponenten geprüft
   und sein Verzeichnis identitätsgebunden geöffnet.
3. Windows hält den Parent mit `CreateFileW`, `FILE_FLAG_BACKUP_SEMANTICS` und
   `FILE_FLAG_OPEN_REPARSE_POINT`; fehlendes `FILE_SHARE_DELETE` verhindert einen
   Parent-Namespace-Rename während des Commits.
4. POSIX hält einen `O_DIRECTORY|O_NOFOLLOW`-FD und führt Replace/Link relativ zu
   genau diesem Directory-FD aus.
5. Temp-Inhalt wird vollständig geschrieben und per `fsync` geflusht. Der Temp-Inode
   bleibt über einen offenen Handle mit erfasster Dateiidentität gebunden.
6. Windows-Replace verwendet `MoveFileExW` mit `REPLACE_EXISTING|WRITE_THROUGH`;
   POSIX verwendet `os.replace` relativ zum gebundenen Directory-FD.
7. Immutable Publish verwendet einen atomaren No-Overwrite-Hardlink unter demselben
   Parent-Guard; der Tempname wird danach entfernt.
8. Nach Replace/Link wird der Parent-Handle durable geflusht (`FlushFileBuffers` auf
   Windows, `fsync(dirfd)` auf POSIX).
9. Der finale Authority-Name wird gehärtet neu geöffnet. Finale Dateiidentität muss
   dem gehaltenen Temp-Inode entsprechen und finale Bytes müssen exakt den erwarteten
   Bytes entsprechen; jede Abweichung wird als ambiger Commit fail-closed gemeldet.
10. Stage-Key-Erzeugung nutzt nun dasselbe durable immutable Publish-Primitive und
    akzeptiert nur den expliziten Concurrent-Exists-Fall, keine andere Ambiguität.

Adversariale Nachweise:

- Der Windows-Test versucht den Authority-Parent exakt im Replacefenster umzubenennen;
  der gehaltene Parent-Handle blockiert den Austausch, danach ist die neue Registry
  byte- und identitätsverifiziert lesbar.
- Bestehende Temp-Write-, Hardlink-, Replace-Failure-, Replay-, Stage-, Ledger- und
  Key-Faulttests wurden an die gemeinsame Boundary angepasst und bleiben grün.

## TDD- und Regressionsevidenz

### Mikrogates

- Kohärente Draft-/Marker-Manipulation vor Fix: `1 failed` an der intendierten
  Validate→Publish-Boundary.
- Derselbe Test nach Fix: `1 passed`.
- Parent-Namespace-Swap unter Windows: `1 passed`.
- Validation-Attestation-Update/Delete: PASS.

### Gezielte Matrizen

- Admin/F5-B/Backup/Remedy-Matrix: `152 passed, 1 skipped in 15.37s`.
- Source/Registry/Atomicity/Promotion/CLI-Matrix:
  `107 passed in 5.14s`.
- Ruff: PASS.
- `py_compile`: PASS.
- `git diff --check`: PASS; nur bekannte CRLF-Hinweise.

### Vollständige Regression

Befehl:

`C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q`

Ergebnis:

`1002 passed, 8 skipped, 14 failed in 179.25s`

Persistiertes Log:

`C:\Users\Hubert111\AppData\Local\Temp\f5b_full_v9_20260715_223933.log`

Log-SHA-256:

`33e13069fdf619e2c7198ff9241403af5d87ef7fadf6f6944d246c836ee3193b`

Die 14 Fehler sind baseline-identisch zu Freeze v8:

- ein datumsabhängiges Consent-Fixture,
- 13 kumulative In-Process-Rate-Limiter-/HTTP-429-Fälle.

Alle 13 HTTP-Fälle liefen anschließend einzeln in frischen Prozessen:
`13/13 passed`.

Top-5-Workflow-Smoke:

`1 passed in 105.70s`.

## Authority-, Betriebs- und Drift-Nachweise

- Branch: `operator-workbench-phase1`.
- HEAD: `619a1f5485a151816e32732929a6a823839ccb57`.
- Working-Tree-Statuszeilen: `351`.
- Status-Fingerprint:
  `cc90fb0fc1655236083370c1fd846833a3490ae888140400f40b325ff7fe3e50`.
- Registry-Authority:
  `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3`.
- Remedy-DB-Authority:
  `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`.
- Produktiver Stage-Key: fehlt.
- `MORPHIC_ADMIN_STAGE_KEY`: nicht gesetzt.
- Port `8000`: frei.
- Radi144: `127.0.0.1:8090`, PID `3304`, unverändert.
- Keine produktive Authority wurde geschrieben.
- Kein Backup, Dokumentfreeze oder Post-State-ShadowCopy wurde erstellt.

## Scope-Hashes (SHA-256, exakt 50 Dateien)

```text
79d05110caebc9aff2661910bba17a95ca96fa0c935883fe7204827deba3bc4b  .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
0c7cc76b5794a4fb39d28977c68ca408e47a6292eaf771994a22a65c263deae6  apps/cli/commands/sources.py
461de2b6187f191f7d23a97566a8e25c85ae81af663c99ae18b154abf5c02b3a  core/source_data_promotion.py
eb9e8fba918dbde6ea07722e80af498ae831f876fd87765aedd0409b9185550a  core/source_registry.py
b23ba5f29557a34f5d1727d8197a8c63a7a3e1cb9394b5e25f579a381e5be8ba  core/admin_catalog/__init__.py
db2dc01e9375264075f0e614e944ed886cf73fb9b995c9f5ae15cdee2a23334c  core/admin_catalog/audit_integrity.py
a552b3ccf57d95837e9278326bee372a56da9c02d45f867fa2ac4124a133adc1  core/admin_catalog/backup.py
49fdbb14c70f23a5d95d207a49eee0dd48313da234094c76f31cdec3a4b282e8  core/admin_catalog/contracts.py
314b41c04e2ae3544c834ca9ea5a6faca48fe99cb9c84cc11f434d2aae8b08ba  core/admin_catalog/legacy_multiplex_adapter.py
2e6e90d04d53e9fcb6e7231a38099b2d581c2030c63d00f49c24ba30c9e61e31  core/admin_catalog/legacy_profile_adapter.py
0828434114e5870efcea36f144b6c93542863525ead1e40f362777215334057f  core/admin_catalog/legacy_remedy_adapter.py
e5eaf86c7df2c41d8c6e8e4dfd3354d74eb2c51360ce97062d8a9f159932d6b1  core/admin_catalog/paths.py
e0b6f24f68d2572e4736d2b8096cbee7fde3e8f49103de924b9d02ffbe9fd499  core/admin_catalog/runtime_adapter.py
5799f69c698c219ab9314bb8764ef13179f982ae619f6777c7e8b8d50a025aab  core/admin_catalog/service.py
a9353695838fb1abfb13100b69708958551cd4574c6bf8300a409ba75ee2e35e  core/admin_catalog/source_normalization.py
153bfd23cb0bd57b61b0ddc5f4d5bd666c9643538c54ddaf4ee666241e5c0277  core/admin_catalog/source_policy.py
e8322ba4c0e488378b07083184945034bc92b65fac895e21bb1b10888661a6bf  core/admin_catalog/store.py
6b2e8156b4297cd9f6c3f566afbde25babdc137e6903ca5067a8c4edec87a5d5  core/admin_catalog/validation.py
cfd88963eab154debe4e7fe141f344ac9dc6c6c221f0d79bb9b9ce875a2f9a59  tests/test_admin_catalog_audit_integrity.py
717610fa3229868a498f12d3d5e6823a21bc5ebccce64a1057019aab395ad01a  tests/test_admin_catalog_backup.py
e927d28e82fa74fc6ea012dd5e84b015bc62868abb62b2892ebe879dadfa3260  tests/test_admin_catalog_contracts.py
87f09b41fe34662eb4b11a0dbf4e3e14e7152b911479bcb078f593a9a54db7af  tests/test_admin_catalog_legacy_multiplexes.py
6f5c2630b4db1d3ac0eed6db503630b5a759e957a72985e3b84808c57bff8726  tests/test_admin_catalog_legacy_profiles.py
8fa092bc74a077f170294b23b35fcefb69136447b6f39a6f949c145e6c3845e9  tests/test_admin_catalog_legacy_remedies.py
388096c672ff5677674fef67530881e6c98c29455ba31afff89b0c054be542ac  tests/test_admin_catalog_paths.py
853c5e4d5aab7edd6671b491d3c67ddb2fecb4aa3f1c285eb5a0a5f9c3fbd79a  tests/test_admin_catalog_runtime_adapter.py
a7a958290b17076bef50367f0f2b2928505cb97ea2a532e31c3e433ea0db2081  tests/test_admin_catalog_service.py
be99f705d4fc84c51576ef1e286bcbeea2f2a55e5f6cb5dd6de625aff1f13460  tests/test_admin_catalog_store.py
22f2e5e167afce8d2544c76e476a184f8a5d8ccd751e702f2c4674c0fe6d1d2e  tests/test_admin_catalog_validation.py
08c64e45ff6e4b626ef834ce5a9d2b28f287afc31ff18b6e21251e78ba7b2b08  tests/test_admin_remedy_multiplex_management.py
30c4c242e87e0ecd5c7cc28a00952f25bc5b486a8cb08d49753d6c1651016e80  tests/test_admin_source_normalization.py
885e0280b21ec040da089060e638a9b7de4c6f3f24b32052e8a95a158f2e0736  tests/test_admin_source_policy.py
051b654bbae7cfdad02064119cf49956bc797bc5277d8837d2af9799851aa6da  tests/test_f5b_review_findings.py
fbe120b68ee4026bbc7308057a98eba02e9e5d73d9c0c3c31c11545679a4b08f  tests/test_source_data_draft_import.py
461d828d99704315801a3c28a9d0fcd85359aac2ecd2ddc94a6c9acf854680df  tests/test_source_data_promotion.py
7cc243b7e9e528b7b970b384c24820303726b481f2b4864c309d9b4ede17b062  tests/test_source_registry.py
56651262eb88d103a1c680e890e418b19dd2f26e54fe260ef1830c28dd94486b  tests/test_source_registry_atomicity.py
4c4218013291907cc988478958a47bad6337a97d3501210f59bcaf7bae8f000a  tests/test_source_registry_cli.py
0000d132ef5662840f47ea4f2506c7d8ef89379a06a4ee2cb2698430fe83e782  tests/test_admin_profile_management.py
b028ba68a0b5a50d63262f3c943322e4c6a9cdb6c2ab266191cd864fb46d9e2b  docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v4.md
eea69b674503f0eb305c36700fbbabb50575899c8c85a1ae0d1d5c39012fe4fc  docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v5.md
575b76e9e929065e3c9b37ebcd51d34ae43297c99f8976fadca0dd8c49c57028  docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v6.md
b1f02111189b91d16154e8285f5eea2ead8bb1ba1fbab0949126df3d415affe8  docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v6-1.md
9a59f5c4169b2db60c359b7c4fae106242a146eedbc35f6771763e6ba9324fe1  docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v6-2.md
49becf99afe6531ea1d8001155ac31a4897d998cfea50eb8e0ce0085bfb0b5b5  docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v7.md
519f8ff4d41b91e0a29a277cda697cace61436f448adf7f559c3fac35dfdf8de  docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v7-1.md
a192f7ad044c9bea612b7763799912050d7fad131f43ec774556cfc166bbee91  docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v7-2.md
176e5b07bf57572defda0a0909ad9ba3a6e1a36a5a3e378f5d1eda7c102f11ee  docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v8.md
2b4650affa063ca9d071aa2f92c2c3e13c5102c37265f4ffdc03eeb7142f07dd  docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v8-1.md
47448b4d9bf7a13cf1662d7bb0970ee88607676cdb0012a3154768c9ada5e924  docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v8-2.md
```

## Scope und Ausschlüsse

Reviewscope sind exakt die 50 Manifestdateien: produktive F5-B-Boundaries,
transitive `core/admin_catalog/*.py`-Sicherheitsabhängigkeiten, CLI, alle relevanten
Admin-/Source-/Profile-/Atomicity-Vertragstests, aktiver Plan, superseded Freeze
v4–v8 und die vollständigen v6-/v7-/v8-Reviewreports.

Produktive Registry und Remedy-DB sind nur als read-only Authority-Hashes gebunden.
Ausgeschlossen bleiben andere Working-Tree-/Archivartefakte,
Runtime-/Web-/Engine-/Scan-Wiring, Onlinezugriff und F6-Authentisierung.

## Adversarialer Reviewauftrag

Beide Reviewer müssen unabhängig, adversarial, statisch und read-only prüfen:

1. Validate→Publish gegen kohärente Manipulation aller Draftmarker; echte
   Unabhängigkeit und Immutabilität der Validation-Attestation.
2. Catalog-Schema-v8-/Backup-/Restore-Vertrag und Migrationsverhalten.
3. Parent-/Handlebindung aller Authority-Schreibpfade auf Windows und POSIX.
4. Temp-Inode-Bindung, No-Overwrite-Publish, Namespace-Durability und finale
   Identitäts-/Byteattestation bei Registry, Stage, Index, Ledger, Snapshot und Key.
5. Fehler-/Crashfenster vor und nach Replace, Link, Directory-Flush, SQLite-Commit
   und Stage-Commit; keine stille Ambiguität oder Cross-DB-Replayöffnung.
6. Alle v6–v8-Findings auf tatsächliche Closure ohne Regression.
7. Freeze-, Scope-, Branch-, HEAD-, Authority-, Stage-Key- und Port-Nachweise.

Reviewvorgaben:

- Freeze-v9-Datei und alle 50 Manifestdateien bleiben unverändert.
- Keine Tests, Server, Netzwerkzugriffe oder Dateischreiboperationen.
- Freeze-SHA und 50/50 Scope-Hashes am Anfang und unmittelbar vor Verdict prüfen.
- Findings mit P0–P3, Datei:Zeile, Failure-Pfad und konkreter Abhilfe.
- `APPROVE` ausschließlich bei `P0=P1=P2=P3=0` und ohne Scope-Drift.
- Andernfalls `REQUEST CHANGES`; bei Drift `INVALIDATED BY SCOPE DRIFT`.

## Explizite Schranken

- F5-B bleibt bis zu zwei technischen und allen nachfolgenden dokumentgebundenen
  `APPROVE`-Gates `NO-GO`.
- Kein Backup und keine Post-State-ShadowCopy vor sämtlichen APPROVE-Gates.
- Radi144 auf Port 8090/PID 3304 darf nicht verändert werden.
- Der produktive Stage-Key darf nicht erzeugt werden.
- Reviewausgaben sind vor jeder späteren Reparatur vollständig und getrennt zu bewahren.
