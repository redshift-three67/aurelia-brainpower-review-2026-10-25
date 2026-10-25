# Feedback f – F5-B technischer Freeze v4

Datum: 2026-07-15
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: SUPERSEDED / REQUEST CHANGES / NO-GO

Beide Ersatzreviews aus `deleg_6e67dca5` endeten driftfrei mit `REQUEST CHANGES`.
Nach den anschließenden Scope-Patches ist dieser Freeze technisch überholt und darf nicht als Approval- oder GO-Grundlage verwendet werden.

## Supersession und Sicherung

Dieser Freeze ersetzt v3 nach zwei driftfreien `REQUEST CHANGES`-Reviews aus
`deleg_c3fcdfff`.

Verifizierter v3-Pre-Fix-Snapshot:
`E:/mprphic_v1_Backups/morphic_v1_shadowcopy_20260715_124144_feedback_f_F5B_v3_review_fixes_pre`

Manifest-SHA-256:
`4b006b1d99ede491db268dca0677120e91bbe55177075f4784c66fe7a523d0e8`

## Closure der v3-Befunde

1. Caller-supplied Publish-Proof entfernt:
   - `_publish_validated_draft` und `_revalidated_source_receipt_hashes` existieren
     im Produktionscode nicht mehr;
   - `publish_validated_draft` ist die einzige finale Store-Boundary;
   - Source-Receipts erzwingen einen Registry-Authority-Pfad, den die Boundary selbst
     sperrt, lädt und live revalidiert; der Lock bleibt bis nach Commit gehalten.
2. Forged Receipt/Raw Insert entfernt:
   - `_create_source_import_draft` existiert weder auf Store noch Service;
   - `import_staged_source_draft` akzeptiert ausschließlich Stage-, Registry-, Kontext-
     und Auditinputs, keine Entries, Receipts, Proofs oder Callbacks;
   - die Store-Boundary ruft den autoritativen Preparation-Context selbst auf und
     persistiert Draft+Receipt noch innerhalb dessen Stage-/Registry-Locks.
3. Stage-Datei-TOCTOU geschlossen:
   - der Lock-Context liefert exakt den unter HMAC/Index geprüften In-Memory-Payload;
   - nach der letzten Prüfung erfolgt kein erneuter Stage-Dateiread.
4. Schema-vor-jedem-Write:
   - einziges rohes `BEGIN IMMEDIATE` liegt in `_begin_attested_write`;
   - alle acht Store-Write-Routen attestieren auf derselben Connection nach
     `BEGIN IMMEDIATE` und vor dem ersten Datenwrite;
   - Drift rollt nullmutierend zurück.
5. Stage-Key-Authority:
   - kanonischer Keypfad muss außerhalb des Staging-Roots liegen;
   - Symlink/Reparse-/Hardlink-Prüfung verwendet dieselbe kanonische Authority-Prüfung
     wie die Registry;
   - Key wird exklusiv temporär vollständig geschrieben und fsync't, dann atomar
     veröffentlicht; Fehler hinterlassen keine finale partielle Keydatei.
6. Receipt-Kontext:
   - Operator, Workspace, Tenant und Scope werden vor Insert gegen den Aufrufkontext
     geprüft.
7. Provenance-Stripping:
   - generische Direktrevisionen dürfen keine stabile Entry-ID enthalten, die im selben
     Kontext aus einem Source-Receipt-Draft stammt, unabhängig von Payloadmutation,
     Source-ID oder Label;
   - Finalisierung bleibt dem dedizierten Source-Publishpfad vorbehalten.

## Gebundene Sicherheitsverträge

- Stage-Artefakt-ID, expliziter Root und HMAC-signierter Stage-Index;
- Registry-/Stage-Locks bis nach atomarem Draft+Receipt- bzw. Publish-Commit;
- DB-weite Batch-Identity gegen Cross-Context-Replay;
- Receipt bindet Artefakt, Draft, Base-Revision, vollständigen Kontext und Registry;
- Schema v6 mit globalem Replay-Index;
- Attestierung bestehender DB vor Initialisierung und unmittelbar vor jedem Write;
- CLI Base-/Semantik-Preflight vor Ziel-DB-Erzeugung;
- quarantänisierte Source-Records verhindern Import vollständig;
- kein Activate, Runtime-, Engine-, Scan-, Web- oder Netzwerk-Wiring.

## Verifikationsmatrix

- v3-Review-Regressionsmodul: `27 passed`;
- konsolidierte F5.2/F5.3/CLI/Store/Backup-Matrix: `120 passed, 1 skipped`;
- vollständige Admin-/Source-Matrix: `491 passed, 6 skipped`;
- breite Suite: `975 passed, 8 skipped, 14 failed` in 153.19 s;
- Fehlerliste exakt baseline-identisch:
  - 1 datumsabhängiger Consent-Fixturefehler;
  - 13 HTTP-429-Fälle durch kumulierten In-Process-Rate-Limiter;
- dieselben 13 HTTP-Fälle in separaten Prozessen: `13/13 passed`;
- Top-5-Smoke: `1 passed in 98.38s`;
- Ruff: PASS;
- `py_compile`: PASS;
- `git diff --check`: PASS;
- Port 8000 frei; Radi144 auf 8090/PID 3304 unangetastet.

Breitlog:
`C:/Users/Hubert111/AppData/Local/Temp/f5b_full_v4_20260715_130900.log`

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
f86479860264f7a346f5692d3458399c51973984fddcbe7d3093ae2701c97a14  core/admin_catalog/backup.py
49fdbb14c70f23a5d95d207a49eee0dd48313da234094c76f31cdec3a4b282e8  core/admin_catalog/contracts.py
1afae78f4032978596d6c0e3fdf906db7bafbb4c31e5aeb65b2b694d243cb3ea  core/admin_catalog/service.py
a9353695838fb1abfb13100b69708958551cd4574c6bf8300a409ba75ee2e35e  core/admin_catalog/source_normalization.py
1a2ae81d0c988dd278d9f1852c8ba885203fcc2f5e3db279494f8dd3b22d94f1  core/admin_catalog/store.py
6cd2e2fe11b857f2838782732617d1c7ff825f1a0691bc53f44c94650de7a505  core/source_data_promotion.py
717610fa3229868a498f12d3d5e6823a21bc5ebccce64a1057019aab395ad01a  tests/test_admin_catalog_backup.py
563816ff2c638e69db9a6a9ab8d7c8bf73e7c74ba874ea8697745cc992f9f7d1  tests/test_admin_remedy_multiplex_management.py
30c4c242e87e0ecd5c7cc28a00952f25bc5b486a8cb08d49753d6c1651016e80  tests/test_admin_source_normalization.py
8b6ca76f1c65d8dcf6ae6f3d8f9fc46e49d5188ad7673c396d48a30e83957d75  tests/test_f5b_review_findings.py
2ffabc29e99a04aa7007fed9e1b2ab7a923de36ede08dffce117074cc3375c8b  tests/test_source_data_draft_import.py
72a53d49e9f16b69c1b2d074eac45b69e77f4fb7c258e88f209165eaf16fac15  tests/test_source_registry_cli.py
edc6b70172b8bb5ad9bc37d2252e2faeaf6579cff9cd0e16cac08a73b61836bc  tests/test_admin_catalog_store.py
```

## Reviewregel

`APPROVE` nur bei Start=Ende für Freeze und alle 16 Scope-Dateien, unveränderten
Authorities sowie P0=P1=P2=P3=0. Reviews bleiben strikt statisch/read-only.
Bis zu zwei unabhängigen `APPROVE`-Verdicts bleibt F5-B `NO-GO`.
