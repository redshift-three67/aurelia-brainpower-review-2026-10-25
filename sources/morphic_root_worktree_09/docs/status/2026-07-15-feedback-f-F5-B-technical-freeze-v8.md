# Feedback f – F5-B technischer Freeze v8

Datum: 2026-07-15
Freeze-Zeitanker: `2026-07-15T22:09:11+02:00`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: `SUPERSEDED / REQUEST CHANGES / NO-GO`

## Technischer Reviewausgang

Beide unabhängigen Reviews waren driftfrei und an die ursprünglichen Bytes dieses
Freeze-Dokuments mit SHA-256
`1b697e2be4c9b9e276e123b178ba1d4e1050fd641b518e6ec12c26efe48d006d`
gebunden.

- Review 1: `APPROVE`, `P0=0, P1=0, P2=0, P3=0`.
- Review 2: `REQUEST CHANGES`, `P0=0, P1=2, P2=0, P3=0`.
- Vollständiger Review 1:
  `docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v8-1.md`
  - SHA-256: `2b4650affa063ca9d071aa2f92c2c3e13c5102c37265f4ffdc03eeb7142f07dd`
- Vollständiger Review 2:
  `docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v8-2.md`
  - SHA-256: `47448b4d9bf7a13cf1662d7bb0970ee88607676cdb0012a3154768c9ada5e924`

Schon ein `REQUEST CHANGES` blockiert den Dokumentfreeze. Freeze v8 ist nicht
approvable und darf nicht als Gate-, Backup- oder GO-Grundlage verwendet werden.
Die zwei v8-P1-Root-Causes benötigen getrennte RED→GREEN-Mikrogates und anschließend
einen vollständig neuen Technical Freeze v9 mit zwei neuen unabhängigen Reviews.

## Gate

Freeze v8 ersetzt den driftfrei reviewten, aber mit zwei `REQUEST CHANGES`
verworfenen Freeze v7. Freeze v7 und beide vollständigen v7-Reviewberichte bleiben
unverändert als historische Evidenz im Scope erhalten.

Dieser Freeze erlaubt ausschließlich zwei neue unabhängige technische read-only
Reviews. Er ist weder `APPROVE` noch Dokumentfreeze, Backup-Freigabe,
Post-State-ShadowCopy oder `GO`. F5-B bleibt `NO-GO`.

## v7-Reviewausgang und bewahrte Evidenz

Reviewgebundener Freeze-v7-SHA-256:
`d2bb3ffd7811e0991b076599952a14ce8ca37d5d1053fb9d8f342cf3bec2da38`

- Review 1: `REQUEST CHANGES`, `P0=0, P1=1, P2=0, P3=0`.
- Review 2: `REQUEST CHANGES`, `P0=0, P1=3, P2=0, P3=0`.
- Review 1 Repository/Cache bytegleich:
  `519f8ff4d41b91e0a29a277cda697cace61436f448adf7f559c3fac35dfdf8de`.
- Review 2 Repository/Cache bytegleich:
  `a192f7ad044c9bea612b7763799912050d7fad131f43ec774556cfc166bbee91`.

## Vier deduplizierte Root-Causes und v8-Closure

### V8-R1 – Authority-Pfad darf nicht vor dem Handle aufgelöst und umgebogen werden

Betroffen: `core/source_registry.py`, Registry und Stage-Key.

Closure:

- Der erwartete absolute Authority-Name bleibt die maßgebliche Identität.
- `_canonical_registry_path()` verwirft jede Auflösung auf einen anderen Pfad und
  vergleicht Initial-/Finalidentität sowie Regular-File-/Single-Link-Eigenschaften.
- Reads öffnen den erwarteten Namen mit `os.open`; `O_NOFOLLOW` wird verwendet,
  sofern die Plattform es anbietet.
- Vor- und Nachzustand des Pfads werden gegen `fstat()` des tatsächlich geöffneten
  Handles gebunden.
- Striktes JSON wird aus den vom gebundenen Handle gelesenen Bytes geparst; ein
  Post-Parse-Reread muss bytegleich sein. Swap oder Revocation im Parsefenster führt
  fail-closed zum Fehler.

### V8-R2 – Stage-Authority-JSON muss über denselben gebundenen Handle gelesen werden

Betroffen: `core/source_data_promotion.py`.

Closure:

- Stage-Dateipfade dürfen nicht auf einen anderen Pfad auflösen.
- `_load_stage_authority_json()` erfasst die erwartete Pfadidentität, öffnet den
  erwarteten Namen direkt und vergleicht ihn mit dem geöffneten Handle.
- Read und JSON-Parse erfolgen aus demselben Handle-Bytepuffer; `fstat()` vor/nach
  Parse und finaler `lstat()` müssen stabil bleiben.
- Windows verweigert einen Rename des offenen Stage-Handles; auch dieser Fehler wird
  fail-closed behandelt.

### V8-R3 – Live-Draft-Payload muss erneut kryptografisch und semantisch attestiert werden

Betroffen: `core/admin_catalog/store.py`.

Closure:

- Unmittelbar in der Authority-owning Publish-Transaktion wird
  `sha256(payload_json) == payload_hash` erneut geprüft.
- Die dekodierten Entries müssen wieder exakt zum kanonischen `payload_json` führen.
- Jeder Source-Receipt muss denselben Draft, dieselbe Version, denselben live
  verifizierten Payload-Hash und denselben vollständigen Catalog-Kontext attestieren.
- Sowohl generischer Publish als auch Source-Publish brechen vor Revision und Audit
  fail-closed ab, wenn die live DB-Zeile außerhalb der Store-API manipuliert wurde.

### V8-R4 – Pending-Recovery darf Approval-Semantik nicht austauschen

Betroffen: `core/source_data_promotion.py`.

Closure:

- `imported_at` ist für denselben Stage-Artefakt deterministisch an dessen
  `staged_at` gebunden.
- Ein bereits `pending` reserviertes Artefakt akzeptiert ausschließlich exakt
  denselben vollständigen `receipt_sha256`.
- Geänderte `actor_id`, `reason`, Catalog-/Draft-Kontext oder andere
  receipt-signifikante Felder führen fail-closed zum Fehler.
- Ein Retry mit identischer Approval-Semantik bleibt recovery-fähig; eine fremde
  zweite Approval-Identität kann die Reservation nicht übernehmen.

## TDD- und Regressionsevidenz

### Neue adversariale RED-Mikrogates

Vor der v8-Implementierung wurden fünf konkrete Tests ergänzt und gezielt ausgeführt:

1. Registry-/Key-Authority-Substitution während Path-Resolution: RED.
2. Stage-Authority-Namensswap beim direkten Open: RED.
3. Generischer Publish mit live manipuliertem Draft-Payload: RED.
4. Source-Publish mit Payload außerhalb des Receipt-Vertrags: RED.
5. Pending-Recovery mit geändertem Actor/Reason: RED.

Erster kombinierter Lauf: `5 failed` – jeweils an der intendierten Boundary.
Nach den minimalen Fixes: `5 passed`.

### Gezielte und benachbarte GREEN-Nachweise

- `tests/test_f5b_review_findings.py`: `51 passed in 4.84s`.
- Source-/Registry-/Draft-Matrix: `94 passed in 3.48s`.
- Admin-/Store-/CLI-Matrix: `51 passed in 4.75s`.
- Ruff auf allen geänderten Python-Dateien: PASS.
- `py_compile` auf allen geänderten Python-Dateien: PASS.
- `git diff --check` auf dem v8-Reparaturscope: PASS.

### Vollständige Regression

Befehl:

`C:\morphic_v1\.venv\Scripts\python.exe -m pytest tests -q`

Ergebnis:

`999 passed, 8 skipped, 14 failed in 181.80s`

Persistiertes Log:

`C:\Users\Hubert111\AppData\Local\Temp\f5b_full_v8_20260715_215658.log`

Log-SHA-256:

`5d1027c574295c8fc194f488b909676d7d38f72db8e6f94fda64ee12113976eb`

Die 14 Fehler sind baseline-identisch zu Freeze v7:

- ein datumsabhängiges Consent-Fixture (`NOW` liegt inzwischen in der Vergangenheit),
- 13 kumulative In-Process-Rate-Limiter-/HTTP-429-Fälle.

Alle 13 HTTP-Fälle liefen anschließend einzeln in frischen Prozessen:
`13/13 passed`.

Top-5-Workflow-Smoke:

`1 passed in 105.68s`.

Keiner der 14 baseline-identischen Fehler berührt die vier v8-Boundaries.

## Authority-, Betriebs- und Drift-Nachweise

- Branch: `operator-workbench-phase1`.
- HEAD: `619a1f5485a151816e32732929a6a823839ccb57`.
- Tracked-/untracked Statuszeilen: `349`.
- Status-Fingerprint:
  `a45db0b32c163f73b1da6b5e4278fe0df6bcb49c611d819bfba32eba3b5227df`.
- Registry-Authority:
  `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3`.
- Remedy-DB-Authority:
  `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`.
- Produktiver Stage-Key `config/source_repositories.json.stage-key`: fehlt.
- `MORPHIC_ADMIN_STAGE_KEY`: für die Nachweise nicht gesetzt.
- Port `8000`: frei.
- Radi144: `127.0.0.1:8090`, PID `3304`, unverändert.
- Kein Server wurde gestartet oder beendet.
- Keine produktive Authority wurde geschrieben.
- Kein Backup, Dokumentfreeze oder Post-State-ShadowCopy wurde erstellt.

## Scope-Hashes (SHA-256, exakt 47 Dateien)

```text
efffdedd42c84807383192e59a03443baecb8ed60cc32ab235c1c64f3f684234  .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
0c7cc76b5794a4fb39d28977c68ca408e47a6292eaf771994a22a65c263deae6  apps/cli/commands/sources.py
d6acb6282e743051338352f638f2dd090a4fa4936fb459b14542dd658911f88b  core/source_data_promotion.py
839faf4775ed429bc6e5b544b5ff51dc7d7679ea59e4ed0fd5e2d22617a7eb0b  core/source_registry.py
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
33784021ed8a3fe7d1dd9295d326040579fa19b1856d48b52bc1a12629af4e66  core/admin_catalog/store.py
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
c1f6b86206e35ff49f2f930fc6dc5e1bc8de06ac134a374033961c2a0a95f113  tests/test_admin_catalog_store.py
22f2e5e167afce8d2544c76e476a184f8a5d8ccd751e702f2c4674c0fe6d1d2e  tests/test_admin_catalog_validation.py
eec32694a99d1b0001eb79ecb962f17eb9250e7a124fd478ef88a6cae8ad675a  tests/test_admin_remedy_multiplex_management.py
30c4c242e87e0ecd5c7cc28a00952f25bc5b486a8cb08d49753d6c1651016e80  tests/test_admin_source_normalization.py
885e0280b21ec040da089060e638a9b7de4c6f3f24b32052e8a95a158f2e0736  tests/test_admin_source_policy.py
9368cc02cb1674acc52e5f43ae6a950aa57dc8cf72fd71e98eb7d370de305d25  tests/test_f5b_review_findings.py
fbe120b68ee4026bbc7308057a98eba02e9e5d73d9c0c3c31c11545679a4b08f  tests/test_source_data_draft_import.py
de2a73aee053bf2301fb1cb5f6ef47100345009f20a11af1ab63984cfc1901b9  tests/test_source_data_promotion.py
7cc243b7e9e528b7b970b384c24820303726b481f2b4864c309d9b4ede17b062  tests/test_source_registry.py
a4e4be6b05768bd2bd6c6143cf303f4b25f8baa8fd8e60a3b21868eabf4c507e  tests/test_source_registry_atomicity.py
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
```

## Scope und Ausschlüsse

Reviewscope sind exakt die 47 Manifestdateien: produktive F5-B-Boundaries,
transitive `core/admin_catalog/*.py`-Sicherheitsabhängigkeiten, CLI, alle relevanten
Admin-/Source-/Profile-Vertragstests, aktiver Plan, superseded Freeze v4–v7 und die
vollständigen v6-/v7-Reviewreports.

Produktive Registry und Remedy-DB sind nur als read-only Authority-Hashes gebunden und
keine Änderungsobjekte. Ausgeschlossen bleiben sonstige Working-Tree-/Archivartefakte,
Runtime-/Web-/Engine-/Scan-Wiring, Onlinezugriff und F6-Authentisierung.

## Adversarialer Reviewauftrag

Beide Reviewer müssen vollständig unabhängig, adversarial, statisch und read-only prüfen:

1. Authority-Pfadbindung bei Registry und Stage-Key, einschließlich Resolution-,
   Open-, Handle-, Parse- und Post-Parse-Swapfenstern.
2. Stage-Authority-Reads über den gebundenen Handle und alle Stage-Index-v4-
   Reserve-/Replace-/Commit-/Recovery-Übergänge.
3. Live-Draft-Payload-Hash, Kanonizität, Source-Receipt-Attestation und
   Authority-owning Publish-Transaktion.
4. Vollständige Pending-Approval-Identität; insbesondere Actor-/Reason-Wechsel und
   Recovery mit identischer Approval-Semantik.
5. Alle v6-/v7-Findings auf tatsächliche Closure ohne Regression.
6. Authority-, Scope-, Manifest-, Branch-, HEAD-, Stage-Key- und Port-Nachweise.

Reviewvorgaben:

- Freeze-v8-Datei und alle 47 Manifestdateien bleiben unverändert.
- Keine Tests, Server, Netzwerkzugriffe oder Dateischreiboperationen.
- Freeze-SHA und alle 47 Scope-Hashes am Anfang und unmittelbar vor dem Verdict prüfen.
- Findings mit Datei:Zeile, Exploit-/Failure-Pfad und konkreter Abhilfe dokumentieren.
- Prioritäten `P0`, `P1`, `P2`, `P3`.
- `APPROVE` ausschließlich bei `P0=P1=P2=P3=0` und ohne Scope-Drift.
- Andernfalls `REQUEST CHANGES`; bei Drift `INVALIDATED BY SCOPE DRIFT`.

## Explizite Schranken

- F5-B bleibt bis zu zwei gültigen technischen und anschließend allen weiterhin
  vorgeschriebenen dokumentgebundenen `APPROVE`-Gates `NO-GO`.
- Kein Backup und keine Post-State-ShadowCopy vor sämtlichen APPROVE-Gates.
- Radi144 auf Port 8090/PID 3304 darf nicht verändert werden.
- Der produktive Stage-Key darf nicht stillschweigend erzeugt werden.
- Reviewausgaben müssen vor jeder späteren Reparatur vollständig und getrennt im
  Repository bewahrt werden.
