# Feedback f – F5-B technischer Freeze v7

Datum: 2026-07-15
Freeze-Zeitanker: `2026-07-15T21:29:39+02:00`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: `SUPERSEDED / REQUEST CHANGES / NO-GO`

## Reviewausgang

Beide unabhängigen, hashgebundenen v7-Reviews endeten vollständig driftfrei mit
`REQUEST CHANGES`. Freeze, 44/44 Scope-Dateien, produktive Authorities, Branch, HEAD und
der fehlende produktive Stage-Key blieben jeweils am Start und Ende identisch.

- Review 1: `P0=0, P1=1, P2=0, P3=0`.
- Review 2: `P0=0, P1=3, P2=0, P3=0`.
- Vollständiger Review 1:
  `docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v7-1.md`
  - SHA-256: `519f8ff4d41b91e0a29a277cda697cace61436f448adf7f559c3fac35dfdf8de`
- Vollständiger Review 2:
  `docs/reviews/2026-07-15-feedback-f-F5-B-technical-review-v7-2.md`
  - SHA-256: `a192f7ad044c9bea612b7763799912050d7fad131f43ec774556cfc166bbee91`

Freeze v7 ist nicht approvable und darf nicht als Gate-, Backup- oder GO-Grundlage
verwendet werden. Die vier deduplizierten Root-Causes werden in getrennte
RED→GREEN-Mikrogates überführt; danach ist ausschließlich ein neuer Freeze v8 reviewfähig.

## Formale Einordnung

Freeze v1 bis v6 sind `SUPERSEDED / REQUEST CHANGES` und dürfen weder als Approval- noch
als GO-Grundlage wiederverwendet werden. Freeze v7 bindet den nach den zwei driftfreien
v6-Reviews korrigierten vollständigen 44-Dateien-Scope.

F5-B bleibt bis zu zwei neuen unabhängigen, driftfreien technischen `APPROVE`, einem
anschließenden Dokumentfreeze, zwei dokumentgebundenen `APPROVE` und einer danach
erzeugten und vollständig rückverifizierten externen Post-State-ShadowCopy ausdrücklich
`NO-GO`. Vor diesen Gates wird weder eine Backup-/GO-Kopie noch eine Post-State-ShadowCopy
erzeugt.

## Live-Präflight vor Erzeugung

Unmittelbar vor dem Schreiben dieses Freeze wurden live rückverifiziert:

- Branch: `operator-workbench-phase1`.
- HEAD: `619a1f5485a151816e32732929a6a823839ccb57`.
- Working Tree: absichtlich nicht clean; `347` von `git status --short` gemeldete Zeilen.
  Maßgeblich für dieses Review ist ausschließlich der unten bytegebundene 44-Dateien-Scope.
- Alle 44 erwarteten Scope-Dateien existieren.
- `git diff --check` für den gesamten Scope: PASS.
- Port 8000: kein Listener.
- Port 8090: Listener `127.0.0.1:8090`, PID `3304` (Radi144); unverändert.
- Produktiver Stage-Key `config/source_repositories.json.stage-key`: nicht vorhanden.

## Produktive Authorities

Diese Authorities sind read-only und wurden nicht verändert:

- `config/source_repositories.json`:
  `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3`
- `data/remedies.db`:
  `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`
- `config/source_repositories.json.stage-key`: **nicht vorhanden**.

Kein produktives Authority-Objekt wurde beschrieben, kein produktiver Stage-Key erzeugt,
kein Server gestartet und Radi144 nicht verändert.

## Closure der v6-Reviewfindings

1. **Registry-TOCTOU:** `_strict_json_load(...)` liest und parst die Registry über denselben
   offenen Handle. Pfad-, Handle-, Link-, Größen- und relevante Zeitmetadaten werden vor,
   während und nach dem Read abgeglichen. Ein Registry-Austausch während des Parsefensters
   schlägt fail-closed fehl.
2. **Stage-Key-TOCTOU:** `_read_registry_authority_bytes(...)` bindet den Key-Read an denselben
   Handle und gleicht Pfad-/Handleidentität nach dem Schließen erneut ab. Ein Austausch nach
   dem Read liefert keinen still akzeptierten fremden HMAC-Key.
3. **Pending-Consumer-Kontext:** Stage-Index-Schema v4 bindet `pending` zusätzlich an den
   SHA-256 des vollständigen `CatalogContext` aus Operator, Workspace, Tenant und Scope.
   Gleicher DB-Pfad und gleiche Draft-ID in einem anderen Kontext können eine Reservation
   weder übernehmen noch ersetzen.
4. **Komponierbare Persistenzumgehung:** Der rohe modulweite `_insert_revision(...)`-Writer
   wurde entfernt. `_revision_insert_plan(...)` ist rein und besitzt weder Connection noch
   SQL-Ausführung; die finalen Store-Boundaries attestieren Policy und führen die
   Revisionswrites in ihrer eigenen `BEGIN IMMEDIATE`-Transaktion aus. Der Test bestätigt,
   dass `_write_connection` und ein roher Revisionsinsert nicht mehr komponierbar sind.
5. **Base-Provenance-Poisoning:** Source-Schutzidentitäten werden als `(EntryType,
   normalized ID)` aus dem Source-Draft abzüglich der unveränderten Identitäten der explizit
   receipt-gebundenen Base-Revision berechnet. Übernommene Base-Einträge bleiben generisch
   publizierbar; tatsächlich source-eingeführte Identitäten bleiben der dedizierten
   Receipt-Publication vorbehalten.
6. **Plan-/Freeze-Drift:** Der aktive Plan weist Freeze v6 als superseded aus, nennt exakt die
   fünf v6-Root-Causes und verlangt vor jedem GO einen neuen Freeze v7 sowie sämtliche
   technischen und dokumentgebundenen Doppelreviews.

## Gebundene Sicherheitsverträge

- Catalog-Schema-Version: `7`.
- Catalog-Schema-Fingerprint:
  `e8bcf21ff2317c82e8fd142abf46b6ca9ac1169c7738767c2553ede06e6e0d21`.
- Stage-Index-Schema-Version: `4`.
- Stage-Consumption: HMAC-gebundener Zustandsautomat `"" -> pending -> committed`.
- Pending bindet kanonischen Catalog-Pfad, vollständigen Catalog-Kontext und Draft-ID.
- Store-owned Source-Import akzeptiert ausschließlich die unabhängig konfigurierte
  produktive Registry-Authority.
- Dedizierter Source-Publish revalidiert die gebundene Live-Registry unter Lock bis nach dem
  Catalog-Commit.
- Direkte Revision und generischer Draft-Publish erzwingen innerhalb ihrer finalen
  attestierten Transaktion dieselbe contextweite Source-Identity-Policy.
- Alle unterstützten Catalog-Write-Routen attestieren das Schema auf derselben
  Write-Connection vor dem ersten Datenwrite.
- Es gibt kein automatisches Publish, Activate, Runtime-, Web-, Engine-, Scan- oder
  Netzwerk-Wiring.

### Explizite Trust-Grenze

Der Sicherheitsvertrag gilt für die unterstützten Store-, Service- und CLI-APIs. Führende
Unterstriche sind keine Capability; deshalb gibt es keine separat komponierbare Kombination
aus einem unterstützten Low-Level-Connection-Provider und rohem Revisionsinsert. F5-B
behauptet ausdrücklich keinen Schutz gegen beliebigen direkten `sqlite3`- oder Dateizugriff
durch vollständig feindlichen Code im selben Python-Prozess. Dafür wäre OS-Prozess- oder
Service-Isolation erforderlich und ein eigenes Gate nötig.

## TDD- und Verifikationsmatrix

Alle Python-Gates liefen mit
`PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1`.

### Getrennte RED-Mikrogates

Vor den Produktivpatches schlugen die fünf neuen Verträge jeweils aus dem beabsichtigten
Grund fehl:

1. Registry-Swap im Parsefenster wurde akzeptiert.
2. Stage-Key-Swap nach dem Read wurde akzeptiert.
3. Pending konnte bei gleicher DB/Draft-ID in einen anderen Catalog-Kontext übernommen
   werden.
4. `_write_connection` und `_insert_revision` waren zu einem rohen Revisionswrite
   komponierbar.
5. Eine unveränderte Base-Identität wurde durch einen späteren Source-Import dauerhaft als
   Source-Identität vergiftet.

### GREEN und fokussierte Regression

- Fünf v6-Finding-Mikrogates: `5 passed`.
- Mikrogates plus Rollback-Vertrag: `6 passed in 1.13s`.
- `tests/test_f5b_review_findings.py`: `46 passed`.
- Source-Promotion plus Registry: `63 passed`.
- Admin-Catalog-Service: `16 passed`.
- Konsolidierte F5-B-/Source-/CLI-/Store-/Service-/Profile-Matrix: `142 passed in 12.10s`.

### Breite Suite und Baseline-Erklärung

- Breite Suite: `994 passed, 8 skipped, 14 failed in 181.45s`.
- Persistiertes Log:
  `C:\Users\Hubert111\AppData\Local\Temp\f5b_full_v7_20260715_212157.log`
- Log-SHA-256:
  `33f34f0755beb263d465f69b95485c399b63dbe8626c5275228d41da5881abb2`

Die 14 Fehler sind exakt baseline-identisch zu Freeze v6: ein datumsabhängiger
Consent-Fixturefehler und 13 HTTP-429-Ausreißer durch den kumulierten In-Process-Rate-Limiter.
Die 13 HTTP-Fälle liefen anschließend jeweils in einem frischen Prozess: `13/13 passed`.
Keiner der 14 Fehler berührt die fünf v7-Änderungsboundaries.

### Slow/Static

- Top-5: `1 passed in 107.13s`.
- Ruff 0.1.11 auf allen fünf geänderten Python-Dateien: PASS.
- `py_compile` auf allen fünf geänderten Python-Dateien: PASS.
- `git diff --check` auf dem vollständigen 44-Dateien-Scope: PASS.

## Scope-Hashes (SHA-256, exakt 44 Dateien)

```text
9390eb51661b12aeaa6d5f47a2818fcf6fd0286e332b146a55ac0cf07e4f1715  .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md
0c7cc76b5794a4fb39d28977c68ca408e47a6292eaf771994a22a65c263deae6  apps/cli/commands/sources.py
e779a1026c9806218db4eba6c769023aaef0c6ce52b4c50e3c941d81fe147d31  core/source_data_promotion.py
aa995ae65a1561c3975e8d5262a6d37367e70ac300e40184e80bb8cbe0063023  core/source_registry.py
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
94653f9b28de83166477944532d9e34d9c3f39923b82f8ce63623488a6bc74f5  core/admin_catalog/store.py
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
a775f453878423a3fdebc1b2eb9a7d20f4d7a205f4c28cb67ed5b8b509356b3f  tests/test_f5b_review_findings.py
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
```

## Scope und Ausschlüsse

Der Reviewscope umfasst exakt die 44 Manifestdateien: produktive F5-B-Boundaries, alle
`core/admin_catalog/*.py`-Module als transitive Sicherheitsabhängigkeiten, CLI, Registry,
Promotion, relevante Admin-/Source-/Profile-Vertragstests, aktiven Plan, superseded
Freeze-v4/v5/v6-Evidenz und beide vollständigen v6-Reviewreports.

Ausgeschlossen sind alle anderen Working-Tree-/Archivartefakte, produktive Authorities als
Änderungsobjekte, Runtime-/Web-/Engine-/Scan-Wiring, Onlinezugriff und F6-Authentisierung.
Die Authority-Dateien sind nur durch die oben genannten SHA-256 gebunden.

## Adversarialer Reviewauftrag

Beide Reviewer müssen vollständig unabhängig, strikt statisch und read-only prüfen:

1. Registry- und Stage-Key-Reads: gleicher Handle, Pfad-/Handleidentität und echte
   Swap-/TOCTOU-Abdeckung.
2. Stage-Index-v4-Integrität, HMAC-Vertrag und vollständige Pending-Kontextbindung in allen
   Precheck-, Reserve-, Replace-, Commit- und Recoverypfaden.
3. Unterstützte Persistenz-API: keine komponierbare Low-Level-Connection-/Raw-Insert-Route;
   finaler Policycheck und Write auf derselben attestierten Transaktion.
4. Source-Provenance: Schutz nur tatsächlich source-eingeführter `(EntryType, normalized ID)`;
   unveränderte Base-Identitäten bleiben frei, mutierte/source-eingeführte Identitäten nicht.
5. Siblingpfade, Rollback, Context-Isolation, immutable Revisionen, Receipt-Revalidation,
   Stage-Replay und Nullmutation bei jedem Fail-closed-Pfad.
6. Exakte Plan-/Freeze-Claims, Verifikationsbaseline, Trust-Grenze und Scope-Vollständigkeit.

Reviews dürfen keine Tests, Server, Netzwerkzugriffe oder Repositorywrites ausführen. Ein
Modell-/Provider-/API-Fehler ist weder Review noch Approval und muss durch eine neue
unabhängige Delegation ersetzt werden.

## Strikte Reviewregel

`APPROVE` ist ausschließlich zulässig, wenn jeder Reviewer unabhängig nachweist:

- Freeze-v7-SHA-256 Start = Ende;
- exakt `44/44` Scope-Hashes Start = Manifest = Ende;
- beide produktiven Authority-Hashes Start = Ende und entsprechen diesem Freeze;
- produktiver Stage-Key fehlt am Start und Ende;
- Branch und HEAD stimmen;
- `P0=P1=P2=P3=0`.

Bei Scope- oder Freeze-Drift ist einzig `INVALIDATED BY SCOPE DRIFT` zulässig. Bei jedem
substantiellen P0–P3-Finding ist das Verdict `REQUEST CHANGES`; Freeze v7 wird dann bewahrt
und superseded. Es gibt keinen Gate-Record und keine Post-State-ShadowCopy. Findings werden
in getrennte RED→GREEN-Mikrogates überführt und erst ein neuer Freeze ist reviewfähig.

Während beide Reviews laufen, darf keine Scope-Datei und kein Freeze-v7-Byte verändert
werden.
