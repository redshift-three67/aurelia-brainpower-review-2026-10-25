# Feedback f – F5-B technischer Freeze v2

Datum: 2026-07-15
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: SUPERSEDED / REQUEST CHANGES

Superseded am 2026-07-15 durch die beiden hashgebundenen Reviews aus
`deleg_b2c79c2b`. Nach Schließung der Befunde gilt
`2026-07-15-feedback-f-F5-B-technical-freeze-v3.md`.

## Supersession

Dieser Freeze ersetzt den ersten technischen Freeze
`2026-07-15-feedback-f-F5-B-technical-freeze.md` nach zwei driftfreien
`REQUEST CHANGES`-Reviews aus Batch `deleg_b485fb9f`.

Der externe, verifizierte Pre-Fix-Snapshot liegt unter:

`E:/mprphic_v1_Backups/morphic_v1_shadowcopy_20260715_104139_feedback_f_F5B_review_fixes_pre`

Manifest-SHA-256:
`dcb51746cd283d06d4677d4a6e1f22722e3de7fd3483361646d71cc0dda158be`

## Gebundener Scope

- F5.2: typenspezifische, geschlossene, deterministische Source-Normalisierung;
- F5.3: kontrollierter immutable Stage→Catalog-Draft-Import;
- autoritativer Stage-Root und atomarer Stage-Index;
- Source-Scope-Erzwingung bei Stage und Revalidierung;
- Catalog-Schema v5 mit append-only Source-Import-Receipts;
- Artefakt-, Registry-, Draft- und Base-Revision-Bindung;
- fail-closed generische Publish-/Revision-Boundaries;
- dedizierter registrygebundener Source-Publishpfad;
- explizite CLI-Authorities `--registry`, `--staging-root`, `--catalog-db`;
- Nullmutation bei ungültigem Preflight;
- keine Aktivierung, Runtime-, Engine-, Scan-, Web- oder Netzwerkwirkung.

## Geschlossene Reviewbefunde

1. Source-Scope wird beim Staging und bei jeder Import-Revalidierung geprüft.
2. Frei konstruierte Ersatz-Stage-Dateien werden ohne exakten Stage-Index-Eintrag abgewiesen.
3. Generischer Store-/Service-Publish weist Source-Drafts ab; der dedizierte Pfad bindet die revalidierten Receipt-Hashes.
4. `source_draft_id` kann keine vom Draft abweichenden Revisionseinträge legitimieren.
5. Referenzquarantäne wird bis zum Fixpunkt transitiv geschlossen.
6. `--registry` und `--staging-root` sind CLI-Pflichtoptionen.
7. Store-Open attestiert den vollständigen SQLite-Schemafingerprint.
8. Ungültiger CLI-Preflight erzeugt keine Catalog-DB.
9. Ungültige rohe Record-IDs erscheinen nur als deterministische opaque Quarantäne-IDs.
10. Receipt bindet Stage-Artefakt-ID, Base-Revision-ID und autoritativen Base-Revisionshash.

## Verifikationsmatrix

- Review-Regressionen: `11 passed`.
- F5.2/F5.3/CLI/Store/Backup-Fokus: `104 passed, 1 skipped`.
- vollständige Admin-/Source-Matrix: `475 passed, 6 skipped`.
- breite Suite: `959 passed, 8 skipped, 14 failed` in 156.83 s.
- breite Fehlerliste exakt baseline-identisch:
  - 1 datumsabhängiger Consent-Fixturefehler;
  - 13 HTTP-429-Fälle durch kumulierten In-Process-Rate-Limiter.
- dieselben 13 HTTP-Fälle in separaten frischen Prozessen: `13/13 passed`.
- Top-5-Smoke: `1 passed in 97.47s`.
- Ruff auf allen geänderten Produktions- und Testdateien: PASS.
- `py_compile` auf allen geänderten Python-Kernpfaden: PASS.
- `git diff --check`: PASS.
- Port 8000 frei; Radi144 auf Port 8090/PID 3304 unangetastet.

Breitlog:
`C:/Users/HUBERT~1/AppData/Local/Temp/f5b_full_after_review_20260715_115003.log`

## Produktive Authorities

- `config/source_repositories.json`:
  `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3`
- `data/remedies.db`:
  `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`

Beide Authorities sind gegenüber dem Pre-State unverändert.

## Scope-Hashes (SHA-256)

```text
b23b92c5414ecf3690101830ec56c11ff748163c2c795bed56376afdbc085fb0  .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
0260aa378b003ea4158836b21f7aa05a74d2476e4c4f025201ad2b3a757caf33  apps/cli/commands/sources.py
b23ba5f29557a34f5d1727d8197a8c63a7a3e1cb9394b5e25f579a381e5be8ba  core/admin_catalog/__init__.py
7980d4938fb3797bc2a9b49e3b7ba206e49388bba8c00e220cf6c5c827932625  core/admin_catalog/backup.py
49fdbb14c70f23a5d95d207a49eee0dd48313da234094c76f31cdec3a4b282e8  core/admin_catalog/contracts.py
a336f5acf9f24a8bebaede922c877b5c18bbd20ba558953da21f2829ce63d33d  core/admin_catalog/service.py
a9353695838fb1abfb13100b69708958551cd4574c6bf8300a409ba75ee2e35e  core/admin_catalog/source_normalization.py
23b22aa2cbb61d0ae6ea21a1a5bddc57865b64409a394780172630664eabb4c7  core/admin_catalog/store.py
ddd1443e71e68809874e94391d0494d45e4cc6a67c1bda0ffc7197b7fde496c4  core/source_data_promotion.py
717610fa3229868a498f12d3d5e6823a21bc5ebccce64a1057019aab395ad01a  tests/test_admin_catalog_backup.py
8411a4906596904ba140c27d8234defca4758990754a6b0cd3a2ed8d5157e07a  tests/test_admin_remedy_multiplex_management.py
30c4c242e87e0ecd5c7cc28a00952f25bc5b486a8cb08d49753d6c1651016e80  tests/test_admin_source_normalization.py
eb71c0b1f5ed354c53cf724f37d51f190771bd2709351f9971817dae9a9d9bc6  tests/test_f5b_review_findings.py
2ffabc29e99a04aa7007fed9e1b2ab7a923de36ede08dffce117074cc3375c8b  tests/test_source_data_draft_import.py
72a53d49e9f16b69c1b2d074eac45b69e77f4fb7c258e88f209165eaf16fac15  tests/test_source_registry_cli.py
d3af8e783a9d4d4ebc6cc1366a08f0b4492d7fe9014e56ac9d6f2ec9867371df  tests/test_admin_catalog_store.py
```

## Reviewregel

`APPROVE` ist nur zulässig, wenn:

- Freeze-Dokument und alle 16 Scope-Dateien am Anfang und Ende identische Hashes besitzen;
- P0 = P1 = P2 = P3 = 0;
- beide produktiven Authorities unverändert bleiben;
- kein Test, Server, Netzwerkzugriff oder Repositorywrite während des Reviews erfolgt.

Bis zu zwei unabhängigen `APPROVE`-Verdicts bleibt F5-B `NO-GO`.
