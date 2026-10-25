# Feedback f – F5-B technischer Freeze v6

Datum: 2026-07-15
Freeze-Zeitanker: `2026-07-15T20:49:41+02:00`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: `SUPERSEDED / REQUEST CHANGES / NO-GO`

## Reviewausgang

Beide unabhängigen, hashgebundenen v6-Reviews endeten vollständig driftfrei mit
`REQUEST CHANGES`. Freeze, 41/41 Scope-Dateien, beide produktiven Authorities,
Branch, HEAD und der fehlende produktive Stage-Key waren jeweils am Start und Ende
identisch.

- Review 1: `P0=0, P1=3, P2=0, P3=0`.
- Review 2: `P0=0, P1=3, P2=0, P3=1`.

Vollständige eigenständige Reports, aus den Hermes-Delegationsartefakten inhaltlich
unverändert mit LF-Zeilenenden bewahrt:

- `docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v6-1.md`
  (`b1f02111189b91d16154e8285f5eea2ead8bb1ba1fbab0949126df3d415affe8`).
- `docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v6-2.md`
  (`9a59f5c4169b2db60c359b7c4fae106242a146eedbc35f6771763e6ba9324fe1`).

Damit ist Freeze v6 nicht approvable und darf nicht als Gate-, Backup- oder GO-Grundlage
verwendet werden. Die Befunde werden in getrennte RED→GREEN-Mikrogates überführt; nach
vollständiger Regression ist ausschließlich ein neuer Freeze v7 reviewfähig.

## Formale Einordnung

Freeze v1 bis v5 bleiben `SUPERSEDED / REQUEST CHANGES`; insbesondere sind Freeze v4 und v5 eindeutig `SUPERSEDED / REQUEST CHANGES / NO-GO` und dürfen weder als Approval- noch als GO-Grundlage wiederverwendet werden. Freeze v6 bindet den nach den v5-Reviews korrigierten vollständigen 41-Dateien-Scope.

F5-B bleibt bis zu zwei neuen unabhängigen, driftfreien technischen `APPROVE`, einem anschließenden Dokumentfreeze, zwei dokumentgebundenen `APPROVE` und einer danach erzeugten und vollständig rückverifizierten externen Post-State-ShadowCopy ausdrücklich `NO-GO`. Vor diesen Gates wird weder eine Backup-/GO-Kopie noch eine Post-State-ShadowCopy erzeugt.

## Live-Präflight vor Erzeugung

Unmittelbar vor dem Schreiben dieses Freeze wurden live rückverifiziert:

- Branch: `operator-workbench-phase1`.
- HEAD: `619a1f5485a151816e32732929a6a823839ccb57`.
- Working Tree: absichtlich nicht clean; `37` modified und `62001` untracked Einträge. Die große untracked Menge besteht überwiegend aus bereits vorhandenen, nicht zum F5-B-Scope gehörenden Worktree-/Archivartefakten. Maßgeblich für dieses Review ist ausschließlich der unten bytegebundene 41-Dateien-Scope; alle übrigen Working-Tree-Dateien sind ausgeschlossen.
- Alle 41 erwarteten Scope-Dateien existieren und stimmen `41/41` mit dem Manifest überein.
- `git diff --check`: PASS; lediglich bekannte CRLF-Hinweise in älteren/fremden Worktree-Dateien.
- Port 8000: kein Listener.
- Port 8090: Listener `127.0.0.1:8090`, PID `3304` (Radi144); unverändert und nicht anzufassen.
- Produktiver Stage-Key `config/source_repositories.json.stage-key`: nicht vorhanden.

## Produktive Authorities

Diese Authorities sind read-only zu behandeln und wurden nicht verändert:

- `config/source_repositories.json`:
  `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3`
- `data/remedies.db`:
  `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`
- `config/source_repositories.json.stage-key`: **nicht vorhanden**.

Kein produktives Authority-Objekt wurde für die Verifikation geöffnet oder beschrieben, soweit dies über den rein lesenden Hashzugriff hinausging. Es wurde kein Server gestartet und kein produktiver Stage-Key erzeugt.

## Gebundene Versionen und Sicherheitsverträge

- Catalog-Schema-Version: `7`.
- Catalog-Schema-Fingerprint:
  `e8bcf21ff2317c82e8fd142abf46b6ca9ac1169c7738767c2553ede06e6e0d21`.
- Stage-Index-Schema-Version: `3`.
- Stage-Consumption verwendet einen HMAC-gebundenen Zustandsautomaten `"" -> pending -> committed`.
- Pending bindet den kanonischen Catalog-Pfad und die Draft-ID. Derselbe Consumer kann Commit-/Finalisierungsfenster deterministisch reconciliieren; fremde Catalog-DB oder Draft-ID bleibt fail-closed.
- Store-owned Source-Import akzeptiert nur die unabhängig konfigurierte `core.source_registry.DEFAULT_SOURCE_REGISTRY_PATH`; eine caller-selected eigene oder stale Registry darf keine Ersatzauthority etablieren.
- Dedizierter Source-Publish revalidiert die gebundene Live-Registry unter Lock und hält die Authority-Boundary bis nach dem Catalog-Commit.
- Direkte Revision und generischer Draft-Publish erzwingen innerhalb ihrer finalen attestierten `BEGIN IMMEDIATE`-Transaktion dieselbe contextweite Source-Identity-Policy. Receiptlose Generic-Publish-Routen dürfen receipt-gebundene Source-Identitäten weder exakt noch mutiert noch case-variant übernehmen.
- Alle unterstützten Catalog-Write-Routen attestieren das Schema auf derselben Write-Connection vor dem ersten Datenwrite.
- Stage-Artefakt, Stage-Index, Registry und Stage-Key werden gegen Symlink-/Reparse-/Hardlink-Aliase sowie Dateiidentitätswechsel an den Authority-Read-Grenzen geprüft.
- Es gibt kein automatisches Publish, Activate, Runtime-, Web-, Engine-, Scan- oder Netzwerk-Wiring.

### Explizite Trust-Grenze

Der Sicherheitsvertrag gilt für die unterstützten Store-, Service- und CLI-APIs. Führende Unterstriche sind keine Capability; die unterstützten Persistenzboundaries müssen selbst fail-closed sein und exponieren keine schreibbare Low-Level-Connection. F5-B behauptet jedoch ausdrücklich **keinen** Schutz gegen beliebigen direkten `sqlite3`- oder Dateizugriff durch vollständig feindlichen Code im selben Python-Prozess. Für diese stärkere Bedrohungsannahme wäre eine getrennte OS-Prozess-/Service-Isolation erforderlich und Gegenstand eines eigenen Gates.

## Closure der v5-Reviewfindings

1. **Generic-Draft-Laundering:** `_require_no_source_identity_bypass(...)` ist als gemeinsame Connection-Policy in der finalen attestierten Transaktion von `create_revision()` und receiptlosem `publish_validated_draft()` wirksam. Der case-variante Übernahme-/Mutationsangriff scheitert nullmutierend.
2. **Caller-selected Registry / Revocation-Bypass:** Der Store vergleicht den bereitgestellten Registry-Pfad kanonisch mit `DEFAULT_SOURCE_REGISTRY_PATH` und revalidiert nur die unabhängig konfigurierte Authority. Eine eigene oder stale Registry kann eine produktive Revocation nicht umgehen.
3. **Irreversibles pre-commit Consumption:** Stage-Index v3 reserviert zunächst `pending`, schreibt Draft und Receipt, committet SQLite explizit und finalisiert danach `committed`. Beide Commit-/Finalisierungsfehlerfenster sind deterministisch recoverbar.
4. **Unvollständige Race-/Swap-Ausführung:** Der Parallel-Key-Test nutzt zwei reale Threads und eine Barrier am exklusiven `os.link`; exakt zwei Linkversuche werden bestätigt. Der Index-Swap-Test ersetzt den Index im attestierten Readfenster, bestätigt die Injektion exakt einmal und bleibt nullmutierend.
5. **Scope-Lücke:** `tests/test_admin_profile_management.py` ist explizit Bestandteil des v6-Manifests. Damit ist der generische Profil-Draft-/Publish-Siblingpfad im Reviewscope enthalten.
6. **Plan-/Freeze-Drift:** Der aktive Plan weist Freeze v4/v5 als superseded, Freeze v6 als nächsten Block, Schema v7, Stage-Index v3, konfigurierte Registry-Authority sowie Pending-/Committed-Reconciliation aus. Die superseded Freeze-v4/v5-Dateien sind im Scope als Evidenz gebunden.

## Verifikationsmatrix

Alle Python-Gates wurden mit `PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1` ausgeführt.

### Mikrogates

- Generic Publish + Profile-Retention: `2 passed`.
- Registry-Revocation, Generic Publish, beide Recoverypfade und dedizierter Source-Publish: `5 passed`.
- Reale Parallel-First-Key- und Index-Swap-Angriffe: `2 passed in 0.57s`; unabhängige Wiederholung `2 passed in 0.63s`.

### Konsolidierte Gates

- Review/Source/CLI/Store/Service/Profile: `137 passed`.
- Vollständige Admin-/Source-Matrix: `505 passed, 6 skipped`.
- v6-Fokusmatrix einschließlich Profile/Backup/Remedy-Multiplex: `184 passed, 1 skipped`.

### Breite Suite und Baseline-Erklärung

Breite Suite:

- `989 passed, 8 skipped, 14 failed in 158.15s`.
- Vollständiges persistiertes Log:
  `C:\Users\Hubert111\AppData\Local\Temp\f5b_full_v6_20260715_202151.log`
- Log-SHA-256:
  `bbdfe8413ba3e378625b519353a93bc20689e0151acd324e0782d45674779dbf`

Die 14 Fehler sind exakt baseline-identisch: ein datumsabhängiger Consent-Fixturefehler und 13 HTTP-429-Ausreißer durch den kumulierten In-Process-Rate-Limiter. Exakte Nodes:

1. `tests/test_group_member_consent_revocation.py::test_expired_group_consent_fails_closed_without_mutating_client`
2. `tests/test_web_shell.py::test_web_shell_lists_opens_and_previews_reports`
3. `tests/test_web_shell.py::test_web_shell_can_start_poll_and_stop_harmonization_job`
4. `tests/test_web_shell.py::test_web_shell_passes_pulse_pause_duration_solfeggio_to_worker`
5. `tests/test_web_shell.py::test_web_shell_preserves_ui_harmonization_modes`
6. `tests/test_web_shell.py::test_web_shell_rejects_truly_unknown_harmonization_fields`
7. `tests/test_web_shell.py::test_web_shell_accepts_report_binding_and_workbench_mode_in_harmonization`
8. `tests/test_web_shell.py::test_workflow_stepping_is_explanatory_not_primary_operator_flow`
9. `tests/test_web_shell.py::test_index_links_to_pipeline_view_as_secondary_surface`
10. `tests/test_web_workbench_runtime.py::test_workbench_api_persists_draft_and_templates`
11. `tests/test_web_workbench_runtime.py::test_scan_job_start_seeds_run_trace_and_workbench_endpoint_reads_it`
12. `tests/test_web_workbench_runtime.py::test_scan_job_start_keeps_running_when_run_trace_persistence_fails`
13. `tests/test_web_workbench_runtime.py::test_scan_job_start_adds_opt_in_parallel_export_plan_without_writing`
14. `tests/test_workbench_client_context_persistence.py::test_workbench_draft_rejects_optional_client_context_without_explicit_consent`

Die 13 HTTP-Fälle liefen anschließend jeweils in einem frischen Prozess: `13/13 passed`.

### Slow/Static

- Top-5: `1 passed in 103.63s`.
- Ruff: PASS.
- `py_compile`: PASS.
- `git diff --check`: PASS.

## Scope-Hashes (SHA-256, exakt 41 Dateien)

```text
382e55a3ded61a88547275398e853c86737d7b8a164ce23c89c399380c0c29c4  .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
0c7cc76b5794a4fb39d28977c68ca408e47a6292eaf771994a22a65c263deae6  apps/cli/commands/sources.py
5cfd6962c09153380303bb6a124da91f709ad47e59a4b6c22c83a2258734472a  core/source_data_promotion.py
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
44efc97f85be62e4fbec408e276669eff93ba00c3bb10d433f101fa976b3c5fa  core/admin_catalog/store.py
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
e749aabb07481fb44b6044afeeb2abfec1d67de9bce0163697f7d863cfa6c3ed  tests/test_f5b_review_findings.py
fbe120b68ee4026bbc7308057a98eba02e9e5d73d9c0c3c31c11545679a4b08f  tests/test_source_data_draft_import.py
de2a73aee053bf2301fb1cb5f6ef47100345009f20a11af1ab63984cfc1901b9  tests/test_source_data_promotion.py
7cc243b7e9e528b7b970b384c24820303726b481f2b4864c309d9b4ede17b062  tests/test_source_registry.py
a4e4be6b05768bd2bd6c6143cf303f4b25f8baa8fd8e60a3b21868eabf4c507e  tests/test_source_registry_atomicity.py
4c4218013291907cc988478958a47bad6337a97d3501210f59bcaf7bae8f000a  tests/test_source_registry_cli.py
0000d132ef5662840f47ea4f2506c7d8ef89379a06a4ee2cb2698430fe83e782  tests/test_admin_profile_management.py
b028ba68a0b5a50d63262f3c943322e4c6a9cdb6c2ab266191cd864fb46d9e2b  docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v4.md
eea69b674503f0eb305c36700fbbabb50575899c8c85a1ae0d1d5c39012fe4fc  docs/status/2026-07-15-feedback-f-F5-B-technical-freeze-v5.md
```

## Scope und Ausschlüsse

Der Reviewscope umfasst exakt die 41 Manifestdateien. Er umfasst dadurch die produktiven F5-B-Implementierungsboundaries, alle `core/admin_catalog/*.py`-Module als transitive Sicherheitsabhängigkeiten, CLI, Source-Registry/-Promotion, die relevanten Admin-/Source-/Profile-Vertragstests, den aktiven Plan sowie die superseded Freeze-v4/v5-Evidenz.

Ausgeschlossen sind alle anderen Working-Tree-Dateien und Archivartefakte, produktive Authorities als Änderungsobjekte, Runtime-/Web-/Engine-/Scan-Wiring, Onlinezugriff, Adminauthentisierung F6 sowie jede direkte Bedrohungsannahme außerhalb der unterstützten APIs. Die Authority-Dateien sind ausschließlich durch ihre oben genannten SHA-256 als unveränderte externe Vertrauensobjekte gebunden.

## Adversarialer Reviewauftrag

Beide Reviewer müssen strikt statisch und read-only prüfen:

1. caller-selected Registry und stale-copy nach produktiver Revocation;
2. Generic-Draft-Laundering exakt, mutiert und case-variant;
3. Pending-/Committed-Recovery bei Commitfehler sowie post-commit/pre-index-finalize;
4. Cross-DB- und Cross-Draft-Pending-Replay;
5. tatsächliche Parallel-Key-Injektion;
6. tatsächlichen Index-Swap;
7. Stage-/Index-/Registry-/Key-Link- und TOCTOU-Grenzen;
8. Source-Publish-Live-Revalidation und Lockdauer;
9. Schemaattestierung aller unterstützten Writes;
10. Direct Revision und Generic Publish als gemeinsame Persistenzboundary;
11. Scope-Vollständigkeit einschließlich `tests/test_admin_profile_management.py` und superseded Freeze-Evidenz;
12. genaue Plan-/Freeze-Claims, Baseline-Erklärung und Trust-Grenze.

Reviews dürfen keine Tests, Server, Netzwerkzugriffe oder Repositorywrites ausführen. Ein technischer Modell-/Provider-/API-Fehler ist weder Review noch Approval und muss durch eine neue unabhängige Delegation ersetzt werden.

## Strikte Reviewregel

`APPROVE` ist ausschließlich zulässig, wenn jeder Reviewer unabhängig nachweist:

- Freeze-SHA-256 Start = Ende;
- exakt `41/41` Scope-Hashes Start = Manifest = Ende;
- beide produktiven Authority-Hashes Start = Ende und entsprechen diesem Freeze;
- produktiver Stage-Key fehlt weiterhin am Start und Ende;
- Branch und HEAD stimmen;
- `P0=P1=P2=P3=0`.

Bei Scope- oder Freeze-Drift ist einzig `INVALIDATED BY SCOPE DRIFT` zulässig. Bei jedem substantiellen P0–P3-Finding ist das Verdict `REQUEST CHANGES`; Freeze v6 wird dann bewahrt und superseded, es gibt keinen Gate-Record und keine Post-State-ShadowCopy, die Findings werden in getrennte RED→GREEN-Mikrogates überführt, die vollständige Matrix wird wiederholt und ein neuer Freeze v7 erzeugt.

Während beide Reviews laufen, darf keine Scope-Datei und kein Freeze-v6-Byte verändert werden.
