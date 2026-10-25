# Feedback f / F7.1 Adaptervertrag und Netzwerkpolicy

Stand: 2026-07-17
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Status: **F7.1 technisch geschlossen**

## 1. Kurzfazit

F7.1 ist technisch geschlossen. Der neue Layer beschreibt den Vertrag fuer
zukuenftige Onlineadapter und entscheidet fail-closed, ob ein Fetch ueberhaupt
zulaessig waere. Es gibt weiterhin keinen echten HTTP-Transport, keinen
Onlinefetch, keinen Auto-Publish und keine Runtime-Catalogwirkung.

Geschlossen sind:

- Adapter-Specs nur fuer feste Source-IDs und feste Adapterversionen;
- leere Netzwerkfreigabeliste als Default: aktive Quellen wie `ncbi_taxonomy`
  oder `nlm_mesh` reichen allein nicht fuer Fetch;
- explizite Admin-Freigabe pro Source-ID, Adapterversion und Tenant;
- Ablehnung bei disabled/quarantined Source trotz Grant;
- HTTPS-Pflicht, feste Host-Allowlist und Redirect-Host-Grenzen;
- Ablehnung privater, Loopback- und Link-local-IPs sowie DNS-Rebinding;
- Response-Groessen-, Timeout-, MIME- und Dekompressionslimits;
- Credentials nur ueber injizierten Secret-Provider;
- redigierte Logdaten ohne Secretwerte.

## 2. Geaenderter Scope

| Datei | Zweck |
|---|---|
| `core/admin_catalog/source_adapters/base.py` | transportfreier Adapter-Basisvertrag mit Source-ID, Version, Host-/MIME-/Limitvertrag und Secret-Injektion |
| `core/admin_catalog/network_policy.py` | fail-closed Netzwerkpolicy-Entscheidung ohne Netzwerk-I/O |
| `tests/test_admin_source_network_policy.py` | F7.1 RED-/GREEN-Contracts fuer Adapterdefault, Grants, DNS, Host, Limits, Secrets und Redaction |
| `docs/status/2026-07-17-feedback-f-F7-1-adapter-network-policy.md` | dieser Gate-Record |

## 3. TDD- und Verifikationsnachweis

| Schritt | Ergebnis |
|---|---|
| RED F7.1 | Importfehler: `No module named 'core.admin_catalog.network_policy'` |
| GREEN F7.1-Fokus | `17 passed in 0.16s` |
| Source-/Workbench-Regression | `157 passed, 1 skipped in 8.61s` fuer `tests/test_admin_source_network_policy.py tests/test_admin_source_policy.py tests/test_source_registry.py tests/test_source_registry_cli.py tests/test_source_registry_atomicity.py tests/test_source_data_promotion.py tests/test_workbench_sources_dom.py` |
| `py_compile` | Exitcode 0 fuer `core/admin_catalog/network_policy.py core/admin_catalog/source_adapters/base.py tests/test_admin_source_network_policy.py` |
| Konfliktmarker-Scan | keine Treffer |
| Trailing-Whitespace-Scan | keine Treffer |
| `git diff --check` | Exitcode 0 |
| Ruff | nicht verfuegbar: `No module named ruff` |

## 4. Contract-Grenzen

| Vertrag | Status |
|---|---|
| Aktive Source bedeutet nicht Adapterfreigabe | testbelegt |
| Leere Grant-Liste ist default-off | testbelegt |
| Grant muss Source-ID, Adapterversion und Tenant exakt treffen | testbelegt |
| Disabled/quarantined Source blockiert Fetch trotz Grant | testbelegt |
| HTTPS und Host-Allowlist | testbelegt |
| Redirects nur auf erlaubte Hosts | testbelegt |
| Private/loopback/link-local IPs und DNS-Rebinding fail-closed | testbelegt |
| Response-Groesse, Dekompression, Timeout und MIME fail-closed | testbelegt |
| Credentials nur aus injiziertem Provider | testbelegt |
| Secretwerte werden aus Logdaten redigiert | testbelegt |
| Kein echter Fetch, kein Adapter fuer eine konkrete Quelle, kein Publish/Activate | bewusst nicht implementiert |

## 5. Fortschritt

| Ebene | Stand nach F7.1 |
|---|---:|
| F7.1 | `100 % technisch geschlossen` |
| F7 gesamt | `1/3 = 33 %` |
| Feedback f gezaehlte Einheiten | `33/39 = 85 %` |
| Feedback f Hauptphasenmodell | `79 %` |
| Nutzerfeedback a-f gesamt | `81 %` |

## 6. Exakt hier weiter

Naechster zulaessiger Block: **F7.2 Ersten offiziellen Adapter implementieren**.

Dabei gilt:

- F7.2 nutzt ausschliesslich lokale HTTP-Fixtures oder Mocktransport;
- der erste Adapter erzeugt maximal einen quarantinisierten Snapshot;
- kein Auto-Publish, keine aktive Revision und keine Runtimewirkung;
- reale Netzwerkabnahme bleibt F7.3 und benoetigt ein eigenes Gate.
