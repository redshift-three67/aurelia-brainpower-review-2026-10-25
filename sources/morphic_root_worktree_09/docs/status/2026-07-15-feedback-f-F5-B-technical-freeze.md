# Feedback f – F5-B technischer Freeze

Datum: 2026-07-15
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: SUPERSEDED / REQUEST CHANGES

Superseded am 2026-07-15 durch die beiden hashgebundenen Reviews aus
`deleg_b485fb9f`. Dieser Freeze bleibt als unveränderlicher Nachweis des
gescheiterten ersten Reviewstands erhalten. Nach Schließung der Findings gilt
`2026-07-15-feedback-f-F5-B-technical-freeze-v2.md`.

## Scope und Grenzen

Dieser Freeze bindet Makroblock F5-B:

- F5.2: typenspezifische, geschlossene und deterministische Source-Normalisierung;
- F5.3: kontrollierter immutable Stage→Catalog-Draft-Import;
- Catalog-Schema v4 für append-only Source-Import-Receipts;
- CLI-Befehl `sources data-import-draft` als vom Consistency-Pfad getrennter Draft-Import.

Ausdrücklich nicht freigegeben:

- kein Catalog-Activate;
- keine Runtime-, Engine-, Scan- oder Webwirkung;
- kein Netzwerkfetch;
- keine automatische Source-Aufwertung;
- keine Änderung der produktiven Registry- oder Remedy-Authority;
- Feedback f insgesamt bleibt NO-GO bis zu den eigenen F6–F8-Gates.

## Verifikationsnachweise

- F5-B/Admin-Fokus: `401 passed, 6 skipped`;
- gezielte Schema-/Normalizer-/Draft-Regression: `58 passed, 1 skipped`;
- breite Suite: `948 passed, 8 skipped` plus exakt 14 bekannte Baselinefehler;
- Baselinefehler: ein datumsabhängiger Consent-Fixture-Test und 13 HTTP-429-Rate-Limit-Fälle;
- alle 13 HTTP-429-Fälle bestanden einzeln in frischen Python-Prozessen;
- Top-5-Smoke: `1 passed in 96.70s`;
- Ruff: PASS;
- `py_compile`: PASS;
- `git diff --check`: PASS;
- F5-B-Pre-State-Manifest: vollständig PASS;
- Port 8000 frei; bestehender Listener auf 127.0.0.1:8090 unangetastet.

Während der breiten Verifikation wurde genau eine neue F5-B-Testdrift gefunden und geschlossen: Das durch die neue Receipt-Tabelle korrekt auf v4 erhöhte Catalog-Schema wurde in einem bestehenden Backup/Restore-Test noch als v3 erwartet. Nach der isolierten Korrektur blieb nur die dokumentierte 14-Fehler-Baseline.

## Produktive Authorities

- `config/source_repositories.json`: `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3`
- `data/remedies.db`: `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`

Beide Hashes entsprechen dem F5-B-Pre-State.

## Gebundener technischer Scope

| Datei | SHA-256 |
|---|---|
| `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md` | `b23b92c5414ecf3690101830ec56c11ff748163c2c795bed56376afdbc085fb0` |
| `apps/cli/commands/sources.py` | `5a3b63cac7909f5d8e9cb582314b1bc6386ab422cc8186662cc2de3cd09cf9b4` |
| `core/admin_catalog/__init__.py` | `b23ba5f29557a34f5d1727d8197a8c63a7a3e1cb9394b5e25f579a381e5be8ba` |
| `core/admin_catalog/backup.py` | `27c006998ca28aacd6cddae04357b61d2a4643d53ce3854a5c65780ae98a08fa` |
| `core/admin_catalog/contracts.py` | `49fdbb14c70f23a5d95d207a49eee0dd48313da234094c76f31cdec3a4b282e8` |
| `core/admin_catalog/service.py` | `02b7dd04cf9e28f399cf36e7c700ab5989b0535247fcccfeb8916b7dc65912d9` |
| `core/admin_catalog/source_normalization.py` | `c6327e39ee8c15c3ce4433dcdf4f3a30eed4c454f884c37bc7c4eddc30a04953` |
| `core/admin_catalog/store.py` | `903cb8da1d13aadb570ec48361a0ee7d9eb7936e88c89aadbe62bbdd8d0fc4b9` |
| `core/source_data_promotion.py` | `fb419e69add667cb91d48684020a8ae1293adeadbcc11d848b6e1de0263e0517` |
| `tests/test_admin_catalog_backup.py` | `717610fa3229868a498f12d3d5e6823a21bc5ebccce64a1057019aab395ad01a` |
| `tests/test_admin_remedy_multiplex_management.py` | `382af834693ac168ce2263a9a0ab247f8641813b90ce4dd808871ffb8fec7936` |
| `tests/test_admin_source_normalization.py` | `30c4c242e87e0ecd5c7cc28a00952f25bc5b486a8cb08d49753d6c1651016e80` |
| `tests/test_source_data_draft_import.py` | `5fdd0384e05cfa40b1c5819768b4689edf983018c9dc4dea54d38a628edb8822` |
| `tests/test_source_data_promotion.py` | `de2a73aee053bf2301fb1cb5f6ef47100345009f20a11af1ab63984cfc1901b9` |
| `tests/test_source_registry_cli.py` | `aa5fa10297212b15c3a98c1cc041cb1e54dcbe7209a36df5da3fa1bf6af40320` |

Statusfingerprint unmittelbar vor Erzeugung dieses Freeze-Dokuments:

`3278e529816531cd345a01c4ab247dc9f68d6bb46a6a671d0bfbe1ef89c39fc8`

## Reviewregel

Zwei unabhängige Reviews müssen alle 15 Scope-Hashes zu Beginn und Ende erneut berechnen. Nur `APPROVE` mit null P0–P3 und ohne Scope-Drift ist gatefähig. Jeder Repositorypatch nach Reviewdispatch supersediert diesen Freeze und alle darauf beruhenden Verdicts. Eine externe Post-State-ShadowCopy darf erst nach den erforderlichen technischen und dokumentgebundenen Doppelapprovals erzeugt werden.
