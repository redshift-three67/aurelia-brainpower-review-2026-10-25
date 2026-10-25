# Feedback f – F5-B technischer Freeze v3

Datum: 2026-07-15
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: SUPERSEDED / REQUEST CHANGES

Superseded am 2026-07-15 durch die beiden hashgebundenen Reviews aus
`deleg_c3fcdfff`. Nach Schließung der Befunde ist ein neuer Freeze erforderlich.

## Supersession und Sicherung

Dieser Freeze ersetzt v2 nach zwei driftfreien `REQUEST CHANGES`-Reviews aus
`deleg_b2c79c2b`.

Verifizierter v2-Pre-Fix-Snapshot:
`E:/mprphic_v1_Backups/morphic_v1_shadowcopy_20260715_120206_feedback_f_F5B_v2_review_fixes_pre`

Manifest-SHA-256:
`1b7b1536f305ba4b87c5a838d9aaf279c0e9f516e1b28f8853df2b86ec2380bd`

## Gebundene Sicherheitsverträge

- Source-Scope bei Stage und jeder Revalidierung fail-closed;
- Stage-Artefakt-ID, expliziter Root und HMAC-signierter Stage-Index;
- 256-Bit Stage-Key außerhalb des Staging-Roots und an den Registry-Pfad gebunden;
- Stage-Index- und Registry-Lock werden verschachtelt bis nach Draft+Receipt-Commit gehalten;
- Stage wird innerhalb der Lockkette erneut geladen und vollständig revalidiert;
- Receipt bindet Artefakt, Draft, Base-Revision, vollständigen Catalog-Kontext und Registry;
- Batch-Identity ist DB-weit eindeutig, nicht nur kontextlokal;
- öffentliche generische Publish-API akzeptiert keine Receipt-Hash-Capability;
- öffentliche Service-Bypassmethode entfernt;
- Source-Publish erfolgt nur intern während gehaltenem Registry-Lock;
- direkte Revision weist Source-Import-Draft und bekannte Source-Snapshots atomar ab;
- rohe Source-Receipt-Erzeugung ist auf Store und Service nicht öffentlich;
- bestehende DB wird vor jedem Schemawrite attestiert; Drift bleibt nullmutierend;
- Schema v6 bindet globalen Replay-Index;
- CLI prüft Base-Existenz und semantische Normalisierung vor Ziel-DB-Erzeugung;
- quarantänisierte Source-Records verhindern den Draft-Import vollständig;
- transitive Referenzschließung und opaque ungültige Record-IDs;
- keine Activation-, Runtime-, Engine-, Scan-, Web- oder Netzwerkwirkung.

## Verifikationsmatrix

- konsolidierte Review-/F5.2-/F5.3-/CLI-/Store-/Backup-Matrix: `113 passed, 1 skipped`;
- vollständige Admin-/Source-Matrix: `484 passed, 6 skipped`;
- breite Suite: `968 passed, 8 skipped, 14 failed` in 151.78 s;
- Fehlerliste exakt baseline-identisch:
  - 1 datumsabhängiger Consent-Fixturefehler;
  - 13 HTTP-429-Fälle durch kumulierten In-Process-Rate-Limiter;
- dieselben 13 HTTP-Fälle in separaten Prozessen: `13/13 passed`;
- Top-5-Smoke: `1 passed in 96.48s`;
- Ruff: PASS;
- `py_compile`: PASS;
- `git diff --check`: PASS;
- Port 8000 frei; Radi144 auf 8090/PID 3304 unangetastet.

Breitlog:
`C:/Users/Hubert111/AppData/Local/Temp/f5b_full_v3_20260715_122648.log`

## Produktive Authorities

- `config/source_repositories.json`:
  `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3`
- `data/remedies.db`:
  `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`
- kein `config/source_repositories.json.stage-key` erzeugt.

## Scope-Hashes (SHA-256)

```text
b23b92c5414ecf3690101830ec56c11ff748163c2c795bed56376afdbc085fb0  .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
b2dc2fe677b0b4cf5d2e78d6eb6ece45eca4edb7c1cfec284ead1a0dba166e5f  apps/cli/commands/sources.py
b23ba5f29557a34f5d1727d8197a8c63a7a3e1cb9394b5e25f579a381e5be8ba  core/admin_catalog/__init__.py
e5fc1eb1f808528147102001d5aec837482d76bf603d6c9666dbee04c599b59b  core/admin_catalog/backup.py
49fdbb14c70f23a5d95d207a49eee0dd48313da234094c76f31cdec3a4b282e8  core/admin_catalog/contracts.py
bcc8bdc54b0f7e6af20ce728b7175d3b3652224a0f6c505981c0e43392f432e6  core/admin_catalog/service.py
a9353695838fb1abfb13100b69708958551cd4574c6bf8300a409ba75ee2e35e  core/admin_catalog/source_normalization.py
c78f538409fbb95d1cbaac0a96f9be0050f5dc0109c53cd45fe7e562f28c2722  core/admin_catalog/store.py
0179c530e1f5d6ee91c6f453d84ddc9fc6414d14031c70dcabe013b2666b25fe  core/source_data_promotion.py
717610fa3229868a498f12d3d5e6823a21bc5ebccce64a1057019aab395ad01a  tests/test_admin_catalog_backup.py
563816ff2c638e69db9a6a9ab8d7c8bf73e7c74ba874ea8697745cc992f9f7d1  tests/test_admin_remedy_multiplex_management.py
30c4c242e87e0ecd5c7cc28a00952f25bc5b486a8cb08d49753d6c1651016e80  tests/test_admin_source_normalization.py
d7df45a62ed31a5cb2e19e3da34712a2ca5bab2add00982a934a0fd009231391  tests/test_f5b_review_findings.py
2ffabc29e99a04aa7007fed9e1b2ab7a923de36ede08dffce117074cc3375c8b  tests/test_source_data_draft_import.py
72a53d49e9f16b69c1b2d074eac45b69e77f4fb7c258e88f209165eaf16fac15  tests/test_source_registry_cli.py
d3af8e783a9d4d4ebc6cc1366a08f0b4492d7fe9014e56ac9d6f2ec9867371df  tests/test_admin_catalog_store.py
```

## Reviewregel

`APPROVE` nur bei Start=Ende für Freeze und alle 16 Scope-Dateien, unveränderten
Authorities sowie P0=P1=P2=P3=0. Reviews bleiben strikt statisch/read-only.
Bis zu zwei unabhängigen `APPROVE`-Verdicts bleibt F5-B `NO-GO`.
