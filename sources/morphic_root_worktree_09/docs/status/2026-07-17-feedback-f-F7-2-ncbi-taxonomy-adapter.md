# Feedback f / F7.2 NCBI-Taxonomy-Adapter

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **F7.2 technisch geschlossen**

## 1. Kurzfazit

F7.2 ist technisch geschlossen. Als erster offizieller Adapter wurde
`ncbi_taxonomy` implementiert. Der Adapter besitzt weiterhin **keinen echten
HTTP-Client**, verwendet ausschließlich einen injizierten lokalen Transport und
erzeugt nur einen quarantänisierten Snapshot.

Nicht umgesetzt und weiterhin gesperrt:

- kein echter Netzwerkzugriff;
- kein Auto-Publish;
- keine aktive Revision;
- keine Runtime-Catalogwirkung;
- keine automatische Staging-/Draft-Übernahme.

## 2. Geänderter Scope

| Datei | Zweck |
|---|---|
| `core/admin_catalog/source_adapters/ncbi_taxonomy.py` | erster offizieller Adapter mit fixer Source-ID, fixer Version, F7.1-Policy-Preflight/Postflight, Mocktransport-Grenze und quarantänisiertem Snapshot |
| `tests/test_admin_source_adapter_ncbi.py` | F7.2 RED-/GREEN-Contracts für Snapshot, Grant-vor-Transport, MIME-Postflight, malformed Fixture und fehlende Runtime-/Store-Verdrahtung |
| `docs/status/2026-07-17-feedback-f-F7-2-ncbi-taxonomy-adapter.md` | dieser Gate-Record |
| `docs/2026-07-17-aktueller-umsetzungsplan-fortschritt.md` | Rollup nach F7.2 |
| `docs/status/2026-07-17-umsetzungsplan-status-tiefenanalyse.md` | Tiefenanalyse-Rollup nach F7.2 |

## 3. Geschlossener Vertrag

| Vertrag | Status |
|---|---|
| Source-ID fix `ncbi_taxonomy` | testbelegt |
| Adapterversion fix `2026.07` | testbelegt |
| Host-Allowlist `eutils.ncbi.nlm.nih.gov` | testbelegt über F7.1-Policy |
| Transport ausschließlich injiziert | testbelegt; kein eingebauter Client |
| F7.1-Preflight vor Transport | testbelegt; ohne Grant kein Transportaufruf |
| F7.1-Postflight nach Response | testbelegt; falscher MIME-Typ verhindert Snapshot |
| Lokales Fixture-JSON wird deterministisch geparst | testbelegt |
| Snapshot bleibt quarantänisiert | testbelegt |
| Snapshotrechte `draft=false`, `publish=false`, `activate=false` | testbelegt |
| Keine Raw-Body-Persistenz im Snapshot | testbelegt |
| Keine Catalog-Store-, Admin-Service-, Staging- oder Runtime-Verdrahtung | statisch testbelegt |

## 4. TDD- und Verifikationsnachweis

| Schritt | Ergebnis |
|---|---|
| RED F7.2 | Importfehler: `No module named 'core.admin_catalog.source_adapters.ncbi_taxonomy'` |
| GREEN F7.2-Fokus | `4 passed in 0.15s` |
| Source-/Workbench-Regression | `161 passed, 1 skipped in 5.16s` für `tests/test_admin_source_adapter_ncbi.py tests/test_admin_source_network_policy.py tests/test_admin_source_policy.py tests/test_source_registry.py tests/test_source_registry_cli.py tests/test_source_registry_atomicity.py tests/test_source_data_promotion.py tests/test_workbench_sources_dom.py` |
| `py_compile` | Exitcode 0 für `core/admin_catalog/source_adapters/ncbi_taxonomy.py tests/test_admin_source_adapter_ncbi.py` |
| Konfliktmarker-Scan | keine Treffer |
| Trailing-Whitespace-Scan | keine Treffer |
| `git diff --check` | Exitcode 0; nur bestehende LF/CRLF-Warnungen in anderen tracked Dateien |
| Ruff | nicht verfügbar: `No module named ruff` |

## 5. Fortschritt

| Ebene | Stand nach F7.2 |
|---|---:|
| F7.1 | `100 % technisch geschlossen` |
| F7.2 | `100 % technisch geschlossen` |
| F7 gesamt | `2/3 = 67 %` |
| Feedback f gezählte Einheiten | `34/39 = 87 %` |
| Feedback f Hauptphasenmodell | `83 %` |
| Nutzerfeedback a-f gesamt | `81 %` |

## 6. Exakt hier weiter

Nächster zulässiger Block: **F7.3 Reale Netzwerkabnahme als eigenes Gate**.

Dabei gilt:

- F7.3 darf nicht aus F7.2 implizit entstehen;
- vorher muss eine isolierte Netzwerkabnahme mit expliziter, zeitlich begrenzter Freigabe definiert werden;
- Response-Hash, Lizenz/Version, Größe, Redirectkette und Retention müssen dokumentiert werden;
- Netzwerkfehler dürfen aktive Revisionen nicht verändern;
- weiterhin kein Auto-Publish und keine Runtimewirkung.
