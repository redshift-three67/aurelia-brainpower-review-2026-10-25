# Feedback f / F7.3 Reale Netzwerkabnahme

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **F7.3 technisch geschlossen**

## 1. Kurzfazit

F7.3 ist technisch geschlossen. Die reale Netzwerkabnahme wurde für den ersten
offiziellen Adapter `ncbi_taxonomy` ausgeführt und als immutable Evidence-Datei
persistiert. Die Abnahme blieb auf Taxonomy-ID `9606` begrenzt und erzeugte nur
einen quarantänisierten Snapshot.

Weiterhin nicht freigegeben:

- kein Auto-Publish;
- keine aktive Revision;
- keine Draft-/Staging-Übernahme;
- keine Runtime-Catalogwirkung;
- keine allgemeine URL-Fetch-Funktion.

## 2. Geänderter Scope

| Datei | Zweck |
|---|---|
| `core/admin_catalog/source_adapters/live_acceptance.py` | F7.3 Live-Abnahmeharness mit zeitlich begrenztem Grant, DNS-Vor-/Nachprüfung, isoliertem `urllib`-Transport und immutable Evidence-Write |
| `core/admin_catalog/source_adapters/ncbi_taxonomy.py` | F7.3-Erweiterung für digitbasierte NCBI-ESummary-Abfrage und DNS-Resolver-basierte Pre-/Postflight-Prüfung |
| `tests/test_admin_source_adapter_live_acceptance.py` | F7.3 RED-/GREEN-Contracts für Grant-Expiry, DNS-Rebinding, immutable Evidence und isolierten Transport |
| `docs/status/f7-3-live-acceptance/ncbi_taxonomy.2026.07.7a73b0fa4d633d2c6514eec1ab00f07ef0e5aa2c75513cbff15dda7b37850e9d.live-acceptance.json` | Live-Abnahme-Evidence ohne Raw-Body |
| `docs/status/2026-07-17-feedback-f-F7-3-live-network-acceptance.md` | dieser Gate-Record |

## 3. Live-Abnahme-Evidence

| Feld | Wert |
|---|---|
| Quelle | `ncbi_taxonomy` |
| Adapterversion | `2026.07` |
| Endpoint | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=taxonomy&retmode=json&id=9606` |
| Query | `9606` |
| Accepted at UTC | `2026-07-17T21:17:17.549037Z` |
| Grant-Fenster | `2026-07-17T21:17:17.549037Z` bis `2026-07-17T21:32:17.549037Z` |
| HTTP-Status | `200` |
| MIME | `application/json` |
| Redirects | keine |
| DNS pre-connect | `34.107.134.59` |
| DNS post-connect | `34.107.134.59` |
| Response-Größe | `335` Bytes |
| Response-SHA-256 | `4d3caec1029c7e41c1f03ca6cc7b1c9ebdb8549b7203d49b0eaa9374957f26cf` |
| Snapshot-SHA-256 | `f27212765cb5ffc177ccf7f2dca7187746e1d1cc4e0145fd760fdd3da0ed96b9` |
| Evidence-SHA-256 | `7a73b0fa4d633d2c6514eec1ab00f07ef0e5aa2c75513cbff15dda7b37850e9d` |
| Record Count | `1` |
| Record | `ncbi_taxonomy_9606`, `Homo sapiens`, Rank `species` |
| Rechte | `draft=false`, `publish=false`, `activate=false` |
| Runtimewirkung | `no_runtime_effect=true` |

## 4. TDD- und Verifikationsnachweis

| Schritt | Ergebnis |
|---|---|
| RED F7.3 | Importfehler: `No module named 'core.admin_catalog.source_adapters.live_acceptance'` |
| GREEN F7.3-Fokus | `4 passed in 0.15s` |
| F7/Source-/Workbench-Regression | `165 passed, 1 skipped in 4.06s` für `tests/test_admin_source_adapter_live_acceptance.py tests/test_admin_source_adapter_ncbi.py tests/test_admin_source_network_policy.py tests/test_admin_source_policy.py tests/test_source_registry.py tests/test_source_registry_cli.py tests/test_source_registry_atomicity.py tests/test_source_data_promotion.py tests/test_workbench_sources_dom.py` |
| Reale Netzwerkabnahme | Exitcode 0; Evidence-Datei erzeugt; DNS pre/post identisch; HTTP 200; MIME `application/json`; keine Redirects |
| `py_compile` | Exitcode 0 für F7.1-F7.3 Adapter-/Testdateien |
| Konfliktmarker-Scan | keine Treffer |
| Trailing-Whitespace-Scan | keine Treffer |
| `git diff --check` | Exitcode 0; nur bestehende LF/CRLF-Warnungen in anderen tracked Dateien |
| Ruff | nicht verfügbar: `No module named ruff` |

## 5. Geschlossener Vertrag

| Vertrag | Status |
|---|---|
| Live-Fetch nur über zeitlich begrenzten Grant | testbelegt |
| Expired Grant blockiert vor DNS und Transport | testbelegt |
| DNS wird vor und nach Fetch geprüft | testbelegt und live belegt |
| DNS-Rebinding verhindert Evidence-Write | testbelegt |
| Echter HTTP-Transport ist isoliert im F7.3-Modul | testbelegt |
| Evidence-Datei ist hashbenannt und immutable geschrieben | testbelegt |
| Evidence enthält keine Raw-Body-Persistenz | belegt |
| Snapshot bleibt quarantänisiert | testbelegt und live belegt |
| Keine Draft-/Publish-/Activate-/Runtime-Verdrahtung | statisch testbelegt |

## 6. Fortschritt

| Ebene | Stand nach F7.3 |
|---|---:|
| F7.1 | `100 % technisch geschlossen` |
| F7.2 | `100 % technisch geschlossen` |
| F7.3 | `100 % technisch geschlossen` |
| F7 gesamt | `3/3 = 100 %` |
| Feedback f gezählte Einheiten | `35/39 = 90 %` |
| Feedback f Hauptphasenmodell | `88 %` |
| Nutzerfeedback a-f gesamt | `82 %` |

## 7. Exakt hier weiter

Nächster zulässiger Block: **F8.1 Schattenvergleich gegen Legacy**.

Dabei gilt:

- F7-Onlineabnahme impliziert keine Runtime-Freigabe;
- F8 startet mit read-only Schattenvergleich;
- produktive Catalog-Consumption, Kill-Switch und Release bleiben eigene Gates;
- Legacy-Default bleibt unverändert, bis F8.2-F8.4 separat geschlossen sind.
