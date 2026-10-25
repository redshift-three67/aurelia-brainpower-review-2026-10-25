# Umsetzungsplan-Status und Tiefenanalyse

Stand: 2026-07-18
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `730da8e04d41d787a5aace6ba41f3c0b946add93`
Analyseart: Code-/Dokumentabgleich nach F5-B/v12-GO, F5-C/F5.6-Dokumentationsvertrag, F6.1-Adminauth-Gate, F6.2-Admin-Catalog-API, F6.3-Quellenanzeige-Safe-View, F6.4-getrennter Admin-UI, F7.1-Adapter-/Netzwerkpolicy, F7.2-NCBI-Taxonomy-Adapter, F7.3-realer Netzwerkabnahme, F8.1-Schattenvergleich gegen Legacy, F8.2-Runtime-Consumption aus einer Revision, F8.3-Kill-Switch, F8.4-Option-A-Runtime-Acceptance, Option-B-API/ASGI-Transport-Acceptance, Option-B-Browser-Smoke und Feedback-a-Reportdesign; Checkpoint-Commit `730da8e` vorhanden; kein Merge, kein Push, keine Produktivfreigabe.

## 1. Kurzfazit

Der aktuelle Umsetzungsstand ist funktional und als lokaler Checkpoint deutlich weiter als der alte Feedback-d-Stand. Der Git-HEAD liegt bei `730da8e` und enthaelt den bisherigen Operator-Workflow-/Feedback-f-Checkpoint. Im Working Tree liegt danach nur der separate Feedback-a-Reportdesign-Delta.

Der massgebliche aktuelle Block ist:

> Feedback f: Admin-Verwaltung Profile/Remedies/Multiplexe + Online-Repositories, F8.4 Option A, Option B API/ASGI und Option B Browser-Smoke technisch geschlossen und lokal committet (`730da8e`). Feedback a: einheitliches Workbench-Reportdesign technisch umgesetzt; naechster Schritt ist der separate Feedback-a-Commit.

Der neueste belastbare Status ist `docs/status/2026-07-18-feedback-a-workbench-report-design.md`: Die aktiven HTML-Report-Renderer und der ReportLab-PDF-Pfad sind auf ein gemeinsames Workbench-Reporttheme gebracht. F5-B/v12, F5-C/F5.6, F6.1-F6.4, F7.1-F7.3, F8.1-F8.4 Option A, Option B API/ASGI und Option B Browser-Smoke bleiben technisch geschlossen; Produktivfreigabe, Merge, Push und spaetere Workflow-Gates bleiben separat.

## 2. Aktuelle Authority-Hierarchie

| Rang | Quelle | Aktualitaet | Bewertung |
|---:|---|---|---|
| 1 | Live-Code im Worktree + Git-Status | 2026-07-18 geprueft | Hoechste technische Wahrheit fuer vorhandene Dateien und Dirty-State |
| 2 | `docs/status/2026-07-18-feedback-a-workbench-report-design.md` | 2026-07-18 | Neuester Status; Feedback a technisch umgesetzt |
| 3 | `docs/status/2026-07-18-feedback-f-option-b-browser-smoke.md` | 2026-07-18 | Option B Browser-Smoke technisch geschlossen |
| 4 | `docs/status/2026-07-18-feedback-f-option-b-live-runtime-acceptance.md` | 2026-07-18 | Option B API/ASGI technisch geschlossen |
| 5 | `docs/status/2026-07-18-feedback-f-F8-4-runtime-acceptance.md` | 2026-07-18 | F8.4 Option A technisch geschlossen |
| 6 | `docs/status/2026-07-18-feedback-f-F8-3-runtime-kill-switch.md` | 2026-07-18 | F8.3 technisch geschlossen |
| 7 | `docs/status/2026-07-18-feedback-f-F8-2-runtime-consumption.md` | 2026-07-18 | F8.2 technisch geschlossen |
| 8 | `docs/status/2026-07-18-feedback-f-F8-1-shadow-comparison.md` | 2026-07-18 | F8.1 technisch geschlossen |
| 9 | `docs/status/2026-07-17-feedback-f-F7-3-live-network-acceptance.md` | 2026-07-17 | F7.3 technisch geschlossen |
| 10 | `docs/status/2026-07-17-feedback-f-F7-2-ncbi-taxonomy-adapter.md` | 2026-07-17 | F7.2 technisch geschlossen |
| 11 | `docs/status/2026-07-17-feedback-f-F7-1-adapter-network-policy.md` | 2026-07-17 | F7.1 technisch geschlossen |
| 12 | `docs/status/2026-07-17-feedback-f-F6-4-admin-ui.md` | 2026-07-17 | F6.4 technisch geschlossen |
| 13 | `docs/status/2026-07-17-feedback-f-F6-3-source-display-safe-view.md` | 2026-07-17 | F6.3 technisch geschlossen |
| 14 | `docs/status/2026-07-17-feedback-f-F6-2-admin-catalog-api.md` | 2026-07-17 | F6.2 technisch geschlossen |
| 15 | `docs/status/2026-07-17-feedback-f-F6-1-admin-security.md` | 2026-07-17 | F6.1 technisch geschlossen |
| 16 | `docs/status/2026-07-17-feedback-f-F5-C-source-documentation-contract.md` | 2026-07-17 | F5-C/F5.6 technisch geschlossen |
| 17 | `docs/status/2026-07-17-feedback-f-F5-B-v12-GO.md` | 2026-07-17 | F5-B/v12 formal geschlossen |
| 18 | `docs/status/2026-07-17-feedback-f-F5-B-v12-post-state-shadowcopy.md` | 2026-07-17 | Externe Post-State-ShadowCopy `151/151 OK` |
| 19 | `docs/status/2026-07-17-feedback-f-F5-B-document-freeze-v3-REV-approve.md` | 2026-07-17 | Dokumentreviews v3: 2x APPROVE, null P0-P3, keine Drift |
| 20 | `docs/status/2026-07-17-feedback-f-F5-B-v12-REV-approve.md` | 2026-07-17 | zwei technische APPROVE auf Freeze v12 |
| 21 | `docs/status/2026-07-17-feedback-f-F5-B-technical-freeze-v12.md` | 2026-07-17 | FRZ v12 technisch geschlossen, Reviewanker |
| 22 | `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md` | historischer Gesamtplan | Normativer Grobplan F1-F8; durch F8.4 Option A und Option B fuer aktuellen Stand superseded |

Wichtig: Aeltere Dokumente nennen teils noch A0, M1, M2, M3, B1, P1, C1, REG, FRZ v10/v11 oder REV v10/v11 als naechsten Block. Diese Aussagen sind durch die spaeteren Gate-Records bis einschliesslich FRZ v12 ueberholt.

## 3. Repository- und Worktree-Zustand

| Merkmal | Ist-Wert | Bewertung |
|---|---:|---|
| Aktiver Arbeitsort | `C:\morphic_v1\.worktrees\operator-workbench-phase1` | Korrekt; nicht im Root `C:\morphic_v1` weiterarbeiten |
| Branch | `operator-workbench-phase1` | Korrekt |
| HEAD | `730da8e04d41d787a5aace6ba41f3c0b946add93` | Lokaler Checkpoint fuer den bisherigen Operator-Workflow-/Feedback-f-Stand |
| Tracked modified | 12 Dateien | Aktuell Feedback-a-Delta: Reporttheme, Renderer, Tests und Statusdocs |
| Nicht ignorierte untracked Einträge | 1 Datei | `docs/status/2026-07-18-feedback-a-workbench-report-design.md` |
| Ignorierte lokale Artefakte | nicht expandiert | Archive, pytest-temp und lokale Harmonization-Job-JSONs bleiben durch `.gitignore` aus dem Commit-Scope ausgeschlossen |
| Git diff stat | Feedback-a-Scope | Kein F5-/Admin-Runtime-Delta nach dem Checkpoint-Commit |
| Staged | keine beobachteten staged Änderungen | Feedback-a-Commitvorbereitung noch offen |

## 4. Übergeordneter Nutzerfeedback-Status

| Punkt | Inhalt | Status | Beleg / Bemerkung | Offener Rest |
|---|---|---|---|---|
| b | Scoreanzeige auf maximal 5 Nachkommastellen | erledigt | Commit `abe8739`; `apps/web/display_scores.py`/Reportausgaben laut Projektmemory | Keine bekannte Lücke im aktuellen Scope |
| c | PDF-Berichte nicht mehr Rohtext, sondern Layout-PDF | erledigt | Commit `d4701e7`; zentrale Richtung: `tools/pdf_exporter.py::html_to_pdf()` | Punkt a) kann später Layout vereinheitlichen |
| d | tenantbasierte Export-Pfad-Isolation | erledigt | Commit `713b66a`; 5 Phasen in `PROJECT_MEMORY/00_CURRENT_STATE.md` dokumentiert | Bekannter Folgebruch: Weblauncher explizit `--export`, Reportkatalog tenant-suffigiert |
| e | Klienten-/Gruppenkontext nach Radi144-Vektoren | umgesetzt / gateweise GO | Viele uncommitted Gruppen-/Consent-/Handle-Module und Tests vorhanden | Geo bleibt separater NO-GO-Zweig; einige Handle-/Policy-Invalidierungen später härten |
| f | Adminverwaltung Profile/Remedies/Multiplexe + Repositories | technisch geschlossen fuer Option A und Option B | F1-F4 GO, F5-A abgeschlossen, F5-B formal GO, F5-C technisch geschlossen, F6.1-F6.4 technisch geschlossen, F7.1-F7.3 technisch geschlossen, F8.1-F8.4 Option A, Option B API/ASGI und Option B Browser-Smoke technisch geschlossen; lokaler Checkpoint-Commit `730da8e` | Keine technische Option-B-Luecke; Produktivfreigabe, Merge und Push bleiben separat |
| a | Einheitliches Design aller Berichte im Workflow-Look | technisch umgesetzt | Gemeinsames Workbench-Report-Theme fuer `render_legacy_html()`, `_render_basic_html()` und `tools/pdf_exporter.py`; Status `docs/status/2026-07-18-feedback-a-workbench-report-design.md` | Separater Commit und spaetere Workflow-Gates bleiben nachgelagert |

## 5. Abgeschlossene Hauptpläne

| Plan / Block | Status | Abschlussnachweis | Bewertung |
|---|---|---|---|
| Radiquant4-Alignment-Layer | vollständig | Alle 9 Tasks im UI/UX-Konsolidierungsplan als erledigt referenziert | Keine echte radiquant4-Netzwerkintegration; bewusst außerhalb des damaligen Plans |
| Operator Workbench Phase 1 | funktional abgeschlossen | Commits bis `495430d` plus spätere UI-Commits | Basis der heutigen 11-Phasen-Workbench |
| Radi144-UI/UX-Konsolidierungsplan 2026-07-07 | vollständig 9/9 | Commits `3a957a3`, `38fc4d3`, `53c405e`, `bbda9ae`, `18b2c4f`, `ea3a457`, `fbfd75c`, `d8c75d4` | Nur bei neuem Nutzerfeedback wieder öffnen |
| Feedback b | vollständig | Commit `abe8739` | Anzeige-/Reportbegrenzung, keine interne Berechnung pauschal geändert |
| Feedback c | vollständig | Commit `d4701e7` | Regel: im regulären Workflow `html_to_pdf()`, nicht `write_text_pdf()` |
| Feedback d | vollständig | Commit `713b66a`; docs markieren Phase 5 complete | Niedrigprioritäre Konfigreste und Web/Reportroot-Integration bleiben Folgearbeit |
| Feedback e | umgesetzt | uncommitted Module/Tests und Statusanalyse | Funktional vorhanden, aber nicht sauber committet; Geo ausgeschlossen |
| Feedback f F1-F4 | GO | Statusdateien vom 2026-07-13/14 | Keine Runtimewirkung, kein Online, keine automatische Catalogwirkung |
| Feedback f F5-A | formal abgeschlossen | `2026-07-15-feedback-f-F5-A-source-pipeline-hardening-gate.md` und Freeze-/Document-Freeze-Dateien | F5-B ist inzwischen separat formal GO |
| Feedback f F5-B/v10 Gate A0 | technisch geschlossen | `2026-07-16-feedback-f-F5-B-v10-A0-parent-identity.md` | Parent-Identity für Stage/Index/Ledger/Snapshot/Key geschlossen |
| Feedback f F5-B/v10 Gate M1 | technisch geschlossen | `2026-07-16-feedback-f-F5-B-v10-M1-v7-known-answer.md` | v7 Known-Answer-Fixture und Fail-Closed-Grenzen vorhanden |
| Feedback f F5-B/v10 Gate M2 | technisch geschlossen | `2026-07-16-feedback-f-F5-B-v10-M2-v7-to-v8-migration.md` | Dedizierte atomare Migration `migrate_catalog_v7_to_v8()` |
| Feedback f F5-B/v10 Gate M3 | technisch geschlossen | `2026-07-16-feedback-f-F5-B-v10-M3-v7-backup-migration.md` | API `migrate_catalog_backup_v7_to_v8()` vorhanden und testbelegt |
| Feedback f F5-B/v10 Gate B1 | technisch geschlossen | `2026-07-17-feedback-f-F5-B-v10-B1-durable-backup-restore.md` | Completion-Record und gemeinsame durable Backup-/Restore-Publikation testbelegt |
| Feedback f F5-B/v10 Gate P1 | technisch geschlossen | `2026-07-17-feedback-f-F5-B-v10-P1-posix-platform-contract.md` | POSIX-`dir_fd`-Vertrag und Same-Parent-Authority fail-closed testbelegt |
| Feedback f F5-B/v10 Gate C1 | technisch geschlossen | `2026-07-17-feedback-f-F5-B-v10-C1-validation-key-composition.md` | Produktive Validation-Key-Composition mit Keyring, Rotation, Cross-Key-Fail-Closed und CLI-Injektion testbelegt |
| Feedback f F5-B/v10 Gate REG | technisch geschlossen | `2026-07-17-feedback-f-F5-B-v10-REG-regression.md` | Admin, Source, Web/Workbench, Vollsuite, Top-5 und statische Checks frisch gruen |
| Feedback f F5-B/v10 Gate REV | REQUEST CHANGES | `2026-07-17-feedback-f-F5-B-v10-REV-request-changes.md` | zwei driftfreie Reviews, beide P1 POSIX source-inode-bound |
| Feedback f F5-B/v10 R1 | technisch geschlossen | `2026-07-17-feedback-f-F5-B-v10-R1-posix-source-inode-fail-closed.md` | POSIX mit `dir_fd`, aber ohne source-inode-bound Publish, endet fail-closed vor Mutation |
| Feedback f F5-B/v11 Gate REV | REQUEST CHANGES | `2026-07-17-feedback-f-F5-B-v11-REV-request-changes.md` | ein APPROVE, ein REQUEST CHANGES; konsolidiertes P1 Backup-Publish nicht bytegebunden |
| Feedback f F5-B/v11 R2 | technisch geschlossen | `2026-07-17-feedback-f-F5-B-v11-R2-backup-byte-bound-publish.md` | Backup-DB, Manifest und Completion werden an validierte Groesse/SHA-256 gebunden |
| Feedback f F5-B/v12 Gate FRZ | technisch geschlossen | `2026-07-17-feedback-f-F5-B-technical-freeze-v12.md`, `.scope.txt`, `.sha256` | 125 Scope-Dateien SHA-256-gebunden und 125/125 rueckverifiziert |
| Feedback f F5-B/v12 Gate REV | technisch geschlossen | `2026-07-17-feedback-f-F5-B-v12-REV-approve.md` | zwei driftfreie technische APPROVE ohne P0-P3 |
| Feedback f F5-B/v12 Dokumentfreeze v1 | REQUEST CHANGES | `2026-07-17-feedback-f-F5-B-document-freeze-v1-REV-request-changes.md` | driftfrei, aber P2/P3 Rollup-Inkonsistenz; durch v2 superseded |
| Feedback f F5-B/v12 Dokumentfreeze v2 | REQUEST CHANGES | `2026-07-17-feedback-f-F5-B-document-freeze-v2-REV-request-changes.md` | driftfrei, aber P2/P3 Prozent-/Next-Step-Inkonsistenz; durch v3 zu superseden |
| Feedback f F5-B/v12 Dokumentfreeze v3 | technisch geschlossen | `2026-07-17-feedback-f-F5-B-document-freeze-v3.md`, `.scope.txt`, `.sha256` | korrigierte Dokumentreviewbasis hashgebunden und rueckverifiziert |
| Feedback f F5-B/v12 Dokumentreviews v3 | APPROVE | `2026-07-17-feedback-f-F5-B-document-freeze-v3-REV-approve.md` | zwei driftfreie APPROVE ohne P0-P3 |
| Feedback f F5-B/v12 Post-State | rueckverifiziert | `2026-07-17-feedback-f-F5-B-v12-post-state-shadowcopy.md` | externe ShadowCopy `151/151 OK` |
| Feedback f F5-B/v12 GO | GO | `2026-07-17-feedback-f-F5-B-v12-GO.md` | F5-B formal geschlossen |
| Feedback f F5-C/F5.6 | technisch geschlossen | `2026-07-17-feedback-f-F5-C-source-documentation-contract.md` | Dokumentsemantik korrigiert und testbelegt |
| Feedback f F6.1 | technisch geschlossen | `2026-07-17-feedback-f-F6-1-admin-security.md` | Fail-closed Adminauthentisierung, Bootstrap-Nonce und separater Admin-Token testbelegt |
| Feedback f F6.2 | technisch geschlossen | `2026-07-17-feedback-f-F6-2-admin-catalog-api.md` | Geschuetzte Admin-Catalog-API mit Status, Entries, Draft, Publish, Activate und Rollback testbelegt |
| Feedback f F6.3 | technisch geschlossen | `2026-07-17-feedback-f-F6-3-source-display-safe-view.md` | Normale Quellenanzeige nutzt `label` und reduzierte Workbench-Safe-View |
| Feedback f F6.4 | technisch geschlossen | `2026-07-17-feedback-f-F6-4-admin-ui.md` | Getrennte Admin-UI mit Fragment-Bootstrap, fluechtigem Token, geschuetzter API und No-Store-Auslieferung testbelegt |
| Feedback f F7.1 | technisch geschlossen | `2026-07-17-feedback-f-F7-1-adapter-network-policy.md` | Transportfreie Adapter-Specs und fail-closed Netzwerkpolicy ohne Onlinefetch testbelegt |
| Feedback f F7.2 | technisch geschlossen | `2026-07-17-feedback-f-F7-2-ncbi-taxonomy-adapter.md` | Erster offizieller NCBI-Taxonomy-Adapter mit injiziertem Mocktransport und quarantinisiertem Snapshot testbelegt |
| Feedback f F7.3 | technisch geschlossen | `2026-07-17-feedback-f-F7-3-live-network-acceptance.md` | Reale NCBI-Taxonomy-Netzwerkabnahme mit immutable Evidence ohne Publish/Activate/Runtimewirkung testbelegt |
| Feedback f F8.1 | technisch geschlossen | `2026-07-18-feedback-f-F8-1-shadow-comparison.md` | Read-only Schattenvergleich gegen Legacy mit deterministischer Diffklassifikation ohne Publish/Activate/Runtimewirkung testbelegt |
| Feedback f F8.2 | technisch geschlossen | `2026-07-18-feedback-f-F8-2-runtime-consumption.md` | Explizite fail-closed Runtime-Consumption aus einer aktiven Revision mit optionaler Subgroup-Provider-Injektion testbelegt |
| Feedback f F8.3 | technisch geschlossen | `2026-07-18-feedback-f-F8-3-runtime-kill-switch.md` | Expliziter Kill-Switch fuer `MORPHIC_ADMIN_CATALOG_ENABLED`; deaktiviert kein Catalog-Read, aktiviert fail-closed Catalog-Snapshot, ungueltige Werte Konfigurationsfehler |
| Feedback f F8.4 Option A | technisch geschlossen | `2026-07-18-feedback-f-F8-4-runtime-acceptance.md` | Isolierter synthetischer Lifecycle ueber Draft/Validate/Diff/Publish/Activate, Runtime-Reload, zweite Aktivierung, Rollback, Kontextisolation, Kill-Switch und Audit-Evidence |
| Feedback f Option B API/ASGI | technisch geschlossen | `2026-07-18-feedback-f-option-b-live-runtime-acceptance.md` | Geschuetzter Webtransport bis Runtime-Read-Model mit Bootstrap, Draft, Validate, Diff, Publish, Activate, Reload, zweiter Aktivierung, Rollback, Kontextisolation, Kill-Switch und Redaction |
| Feedback f Option B Browser-Smoke | technisch geschlossen | `2026-07-18-feedback-f-option-b-browser-smoke.md` | Headless-Playwright-Abnahme ueber `admin.html` mit Runtime-Section, geschuetztem Tokenpfad, zwei Aktivierungen, Rollback und redigierter Evidence |

## 6. Aktueller Plan: Feedback f - Gatefortschritt

| Gate | Inhalt | Status | Technischer Befund | Was noch fehlt |
|---|---|---|---|---|
| F1 | Contracts, isolierter Catalog Store, Cross-Reference-Validierung | GO | Neuer Admin-Catalog-Scope vorhanden | Kein Runtimeeffekt |
| F2 | Offline Draft/Diff/Publish/Activate/Rollback, Pfadpolicy, Backup, Auditintegrität | GO | Statusdateien F2.1-F2.4 vorhanden | Produktive Adminwirkung weiterhin gesperrt |
| F3 | Profilverwaltung und Runtime-Schattenadapter | GO | Legacyprofil-Normalisierung, Profil-Draft-CRUD, Shadowadapter | Kein produktiver Catalog-Default |
| F4 | Remedies/Pathogene/Multiplexe und Legacy-Launcher | GO | Read-only Import, Multiplexmodelle, Draft-CRUD, Launcher-Fix | Keine Runtime-/Netzwerkfreigabe |
| F5-A | Source Policy, Registry-/Audit-/Rollback-Hardening, Batchhash, Replay-Schutz | abgeschlossen | F5-A-Gate dokumentiert | Nicht ausreichend für F5-B-GO |
| F5-B A0 | Parentbindung aller F5-B-Dateiauthorities | technisch geschlossen | Generische Commitprimitive transportieren erwartete Parent-Identity | Kein formaler Gesamtfreeze |
| F5-B M1 | Historische v7 Known-Answer-Fixtures | technisch geschlossen | Fixture `tests/admin_catalog_v7_fixture.py` vorhanden | Nur Test-/Migrationsbasis, keine Migration |
| F5-B M2 | Atomare v7->v8-Migration | technisch geschlossen | `core/admin_catalog/migration.py` importiert v7-Fingerprint aus Backup-Authority | In Regression/Freeze erneut belegen |
| F5-B M3 | v7 Backup -> neues v8 Backup | technisch geschlossen | `core/admin_catalog/backup.py` enthält `migrate_catalog_backup_v7_to_v8()` | In Regression/Freeze erneut belegen |
| F5-B B1 | Gemeinsame durable Backup-/Restore-Publikation | technisch geschlossen | Backup/Restore nutzt `completion.json` und gemeinsame guard-basierte Publish-Boundary | In Regression/Freeze erneut belegen |
| F5-B P1/R1 | POSIX-Entscheidung | technisch geschlossen | Windows bleibt handle-bound; POSIX ohne echte source-inode-bound Publish-Semantik endet fail-closed vor Mutation | In v12-Reviews erneut belegen |
| F5-B C1 | Produktive Validation-Key-Composition | technisch geschlossen | Keyring-Composition, Unknown-Key-Fail-Closed, Stage-/Audit-Key-Abgrenzung und CLI-Injektion vorhanden | In Regression/Freeze erneut belegen |
| F5-B R2 | Bytebindung Backup-Publish | technisch geschlossen | Backup-DB, Manifest und Completion nutzen validierte Groesse/SHA-256; same-size Mutation fail-closed | In v12-Reviews erneut belegen |
| F5-B REG/R2 | v12 Regression nach R2 | technisch geschlossen | Admin 453/6 skipped, Source 164/1 skipped, Vollsuite 1079/8 skipped, Top-5 1 passed | in Freeze v12 aufgenommen |
| F5-B FRZ | Freeze v12 mit SHA-256 und Rueckverifikation | technisch geschlossen | 125 Scope-Dateien, Scope-SHA `807c9893364b24e857e184990904b948dcacdbbe3f923f93b56ccdf617471fd0`, Manifest-SHA `21df34a8e95c9f5ea4d09fc8733de02b98efa282ac8e7b5e343a4fc04a068559`, Rueckverifikation 125/125 OK | geschlossen; bleibt Reviewanker |
| F5-B REV | zwei technische Reviews auf Freeze v12 | technisch geschlossen | zwei driftfreie APPROVE, keine P0-P3 | geschlossen; Dokumentfreeze-Reviews folgten |
| F5-B Dokumentfreeze/Reviews/Post-State | Dokumentreview-Snapshot und externe Sicherung | GO | v3 erzeugt, 2x APPROVE, ShadowCopy `151/151 OK` | geschlossen |
| F5-C | F5.6 Quellen-Dokumentation und F5-Gesamtgate | technisch geschlossen | 14. gezaehlte F5-Arbeitseinheit; `87 passed` | geschlossen |
| F6 | Geschützte Admin-API/UI | technisch geschlossen | F6.1 Adminauth-Gate, F6.2 Admin-Catalog-API, F6.3 Quellenanzeige und F6.4 Admin-UI technisch geschlossen | geschlossen |
| F7 | Onlineadapter | technisch geschlossen | F7.1 Adaptervertrag/Netzwerkpolicy, F7.2 NCBI-Taxonomy-Adapter und F7.3 Live-Abnahme geschlossen | Keine Runtimewirkung; F8 separat |
| F8 | Runtime-Umschaltung/Release | technisch geschlossen fuer Option A und Option B | Schattenvergleich, explizite Catalog-Runtime-Consumption, Kill-Switch, isolierte Runtime-Acceptance, geschuetzter Webtransport und Browserabnahme vorhanden | Technisch geschlossen; Review/Commit-Entscheidung |

Aktuelles Prozentmodell nach Option B Browser-Smoke:

| Modell | Berechnung | Stand |
|---|---|---:|
| F8 intern | F8.1-F8.4 Option A plus Option B API/ASGI und Browser-Smoke geschlossen | **100 % technisch** |
| Feedback f nach Arbeitseinheiten | F1-F4 `14/14`, F5 `14/14`, F6 `4/4`, F7 `3/3`, F8 inklusive Option B geschlossen | **100 % technisch** |
| Feedback f nach Hauptphasen | F1-F8 je 100 % technisch, inklusive Option B | **100 % technisch** |
| Nutzerfeedback gesamt `a-f` | b/c/d/e fertig, f technisch geschlossen, a offen: `(4 + 1 + 0) / 6` | **83 %** |

## 7. M3/B1/P1/C1/REG-Codeabgleich

Der M3-, B1-, P1-, C1- und REG-Status ist nicht nur dokumentiert, sondern im Code sichtbar:

| Artefakt | Befund |
|---|---|
| `core/admin_catalog/backup.py` | `_V7_CATALOG_SCHEMA_FINGERPRINT`, `_assert_v7_catalog_schema()`, versionierte `_load_manifest()`, `restore_catalog_backup()`, `migrate_catalog_backup_v7_to_v8()` vorhanden |
| `core/admin_catalog/backup.py` | B1-Completion-Authority mit `BACKUP_COMPLETION_FILENAME`, `_completion_payload()`, `_load_completion()` und guard-basierter `_publish_without_overwrite()` vorhanden |
| `core/source_registry.py` | P1-Authority-Contract mit `_require_guarded_publish_paths()` und `_require_posix_dir_fd_support()` vorhanden |
| `core/admin_catalog/validation_key_composition.py` | C1-Composition Root fuer externe Validation-Keyrings, Env-Konfiguration und Service-Build vorhanden |
| `apps/cli/commands/sources.py` | `sources data-import-draft --validation-keyring` injiziert den Provider explizit in `CatalogStore` |
| `core/admin_catalog/migration.py` | verwendet den historischen v7-Fingerprint aus `backup.py` |
| `tests/test_admin_catalog_v7_backup_migration_contract.py` | testet erfolgreiche Migration, v8-Restore, normale v7-Restore-Ablehnung, Tampering, Unknown/Preview/v8-Quellen, Fault Injection, Target-Konflikte und Snapshot-Konflikt |
| `tests/test_admin_catalog_backup.py` | testet finalen Completion-Record, fehlende Completion vor Restore, Bundle-Hashbindung, Race-/Windows-Publish-Verhalten und post-publish Rechecks |
| `tests/test_source_registry_atomicity.py` | testet P1 Same-Parent-Authority und POSIX-`dir_fd`-Fail-Closed-Verhalten |
| `tests/test_admin_catalog_validation_key_composition.py` | testet C1 fehlende Keys, Cross-Key, Unknown Active Key-ID, Rotation und Service-Komposition |
| `tests/test_source_registry_cli.py` | testet C1 CLI-Provider-Injektion ohne Secret-Ausgabe |
| `docs/status/2026-07-17-feedback-f-F5-B-v10-REG-regression.md` | dokumentiert frische breite REG-Matrix und operative Nachweise |
| `docs/reviews/2026-07-17-feedback-f-F5-B-technical-review-v10-1.md` | dokumentiert v10 Review 1 mit REQUEST CHANGES |
| `docs/reviews/2026-07-17-feedback-f-F5-B-technical-review-v10-2.md` | dokumentiert v10 Review 2 mit REQUEST CHANGES |
| `docs/status/2026-07-17-feedback-f-F5-B-v10-REV-request-changes.md` | konsolidiert v10 Reviewausgang |
| `docs/status/2026-07-17-feedback-f-F5-B-v10-R1-posix-source-inode-fail-closed.md` | dokumentiert R1-Fix und Regression |
| `docs/reviews/2026-07-17-feedback-f-F5-B-technical-review-v11-1.md` | dokumentiert v11 Review 1 mit APPROVE |
| `docs/reviews/2026-07-17-feedback-f-F5-B-technical-review-v11-2.md` | dokumentiert v11 Review 2 mit REQUEST CHANGES |
| `docs/status/2026-07-17-feedback-f-F5-B-v11-REV-request-changes.md` | konsolidiert v11 Reviewausgang |
| `docs/status/2026-07-17-feedback-f-F5-B-v11-R2-backup-byte-bound-publish.md` | dokumentiert R2-Fix und Regression |
| `docs/status/2026-07-17-feedback-f-F5-B-technical-freeze-v12.md` | dokumentiert FRZ v12, Prozentstand, Freeze-Scope, Reviewauftrag und Schranken |
| `docs/status/2026-07-17-feedback-f-F5-B-technical-freeze-v12.scope.txt` | bindet exakt 125 Reviewdateien |
| `docs/status/2026-07-17-feedback-f-F5-B-technical-freeze-v12.sha256` | bindet SHA-256 je Scope-Datei; direkt rueckverifiziert |
| `docs/reviews/2026-07-17-feedback-f-F5-B-technical-review-v12-1.md` | dokumentiert technisches Review 1 mit APPROVE |
| `docs/reviews/2026-07-17-feedback-f-F5-B-technical-review-v12-2.md` | dokumentiert technisches Review 2 mit APPROVE |
| `docs/status/2026-07-17-feedback-f-F5-B-v12-REV-approve.md` | konsolidiert technisches Doppel-APPROVE |
| `docs/reviews/2026-07-17-feedback-f-F5-B-document-review-v1-1.md` | dokumentiert Dokumentreview 1 mit REQUEST CHANGES |
| `docs/reviews/2026-07-17-feedback-f-F5-B-document-review-v1-2.md` | dokumentiert Dokumentreview 2 mit REQUEST CHANGES |
| `docs/status/2026-07-17-feedback-f-F5-B-document-freeze-v1-REV-request-changes.md` | konsolidiert Dokumentfreeze-v1-Reviewausgang |
| `docs/status/2026-07-17-feedback-f-F5-B-document-freeze-v2.md` | dokumentiert korrigierten Dokumentfreeze v2, Reviewauftrag und Schranken |
| `docs/status/2026-07-17-feedback-f-F5-B-document-freeze-v2.scope.txt` | bindet korrigierten Dokumentreview-Scope |
| `docs/status/2026-07-17-feedback-f-F5-B-document-freeze-v2.sha256` | bindet SHA-256 je Dokumentfreeze-v2-Datei |
| `docs/reviews/2026-07-17-feedback-f-F5-B-document-review-v2-1.md` | dokumentiert Dokumentreview v2-1 mit REQUEST CHANGES |
| `docs/reviews/2026-07-17-feedback-f-F5-B-document-review-v2-2.md` | dokumentiert Dokumentreview v2-2 mit APPROVE |
| `docs/status/2026-07-17-feedback-f-F5-B-document-freeze-v2-REV-request-changes.md` | konsolidiert Dokumentfreeze-v2-Reviewausgang |
| `docs/status/2026-07-17-feedback-f-F5-B-document-freeze-v3.md` | dokumentiert korrigierten Dokumentfreeze v3, Reviewauftrag und Schranken |
| `docs/status/2026-07-17-feedback-f-F5-B-document-freeze-v3.scope.txt` | bindet korrigierten Dokumentreview-v3-Scope |
| `docs/status/2026-07-17-feedback-f-F5-B-document-freeze-v3.sha256` | bindet SHA-256 je Dokumentfreeze-v3-Datei |
| `docs/reviews/2026-07-17-feedback-f-F5-B-document-review-v3-1.md` | dokumentiert Dokumentreview v3-1 mit APPROVE |
| `docs/reviews/2026-07-17-feedback-f-F5-B-document-review-v3-2.md` | dokumentiert Dokumentreview v3-2 mit APPROVE |
| `docs/status/2026-07-17-feedback-f-F5-B-document-freeze-v3-REV-approve.md` | konsolidiert Dokumentreview-v3-Doppel-APPROVE |
| `docs/status/2026-07-17-feedback-f-F5-B-v12-post-state-shadowcopy.md` | dokumentiert externe ShadowCopy und Rueckverifikation |
| `docs/status/2026-07-17-feedback-f-F5-B-v12-GO.md` | setzt F5-B/v12 formal GO |
| `docs/QUELLEN_REGISTRY_BEWERTUNG_20260628.md` | F5-C: reale Source-Registry-/Ledger-Semantik korrigiert |
| `docs/STABILIZATION_TEST_MATRIX.md` | F5-C: Stabilisierungsmatrix an reale Source-Semantik angepasst |
| `tests/test_source_documentation_contract.py` | F5-C: Contract-Test fuer Dokumentsemantik |
| `docs/status/2026-07-17-feedback-f-F5-C-source-documentation-contract.md` | dokumentiert F5-C-Abschluss und Verifikation |
| `apps/web/admin_security.py` | F6.1: separater Admin-Security-State mit Bootstrap-Nonce, `X-Morphic-Admin-Token`, Origin-/Host-Gate und constant-time Digestvergleich |
| `tests/test_web_admin_security.py` | F6.1: Contract-Tests fuer Fail-Closed, Headertrennung, Nonce-/Tokenvertrag und Launchergrenzen |
| `Run-WebUI.ps1` | F6.1: optionaler Adminstart mit Fragment-Nonce ohne Tokenausgabe |
| `docs/status/2026-07-17-feedback-f-F6-1-admin-security.md` | dokumentiert F6.1-Abschluss und Verifikation |
| `apps/web/admin_catalog.py` | F6.2: geschuetzter Admin-Catalog-Router hinter `require_admin_request` |
| `tests/test_web_admin_catalog.py` | F6.2: Contract-Tests fuer Adminauth, CAS/Auditgrund, Draft/Validate/Publish/Activate/Rollback |
| `docs/status/2026-07-17-feedback-f-F6-2-admin-catalog-api.md` | dokumentiert F6.2-Abschluss und Verifikation |
| `apps/web/main.py` | F6.3: `/api/sources` gibt nur Workbench-Safe-View zurueck |
| `apps/web/static/app.js` | F6.3: Quellenliste rendert `label` statt `name` |
| `tests/test_workbench_sources_dom.py` | F6.3: Contract-Tests fuer Safe-View und DOM-Feldvertrag |
| `docs/status/2026-07-17-feedback-f-F6-3-source-display-safe-view.md` | dokumentiert F6.3-Abschluss und Verifikation |
| `apps/web/static/admin.html` | F6.4: getrennte Admin-Catalog-Oberflaeche ohne normale Workbench-Integration |
| `apps/web/static/admin-catalog.js` | F6.4: Fragment-Bootstrap, fluechtiger Admin-Token und geschuetzter Admin-Catalog-API-Client |
| `apps/web/static/app.css` | F6.4: responsive Admin-Oberflaechen-Styles |
| `apps/web/main.py` | F6.4: No-Store fuer `/static/admin.html` und `/static/admin-catalog.js` |
| `tests/test_admin_catalog_dom.py` | F6.4: DOM-/Security-Contract fuer getrennte Admin-UI |
| `docs/status/2026-07-17-feedback-f-F6-4-admin-ui.md` | dokumentiert F6.4-Abschluss und Verifikation |
| `core/admin_catalog/source_adapters/base.py` | F7.1: transportfreier Adapter-Basisvertrag mit festen Source-/Version-/Hostgrenzen |
| `core/admin_catalog/network_policy.py` | F7.1: fail-closed Netzwerkpolicy-Entscheidung ohne Netzwerk-I/O |
| `tests/test_admin_source_network_policy.py` | F7.1: Contract-Tests fuer Grants, DNS, Host, Limits, Secret-Injektion und Redaction |
| `docs/status/2026-07-17-feedback-f-F7-1-adapter-network-policy.md` | dokumentiert F7.1-Abschluss und Verifikation |
| `core/admin_catalog/source_adapters/ncbi_taxonomy.py` | F7.2: erster offizieller Adapter mit fixer Source-ID, fixer Version, F7.1-Policy, injiziertem Transport und quarantinisiertem Snapshot |
| `tests/test_admin_source_adapter_ncbi.py` | F7.2: Contract-Tests fuer Grant-vor-Transport, MIME-Postflight, Snapshotrechte und fehlende Runtime-/Store-Verdrahtung |
| `docs/status/2026-07-17-feedback-f-F7-2-ncbi-taxonomy-adapter.md` | dokumentiert F7.2-Abschluss und Verifikation |
| `core/admin_catalog/source_adapters/live_acceptance.py` | F7.3: Live-Abnahmeharness mit zeitlich begrenztem Grant, echtem isoliertem `urllib`-Transport, DNS-Pre-/Postflight und immutable Evidence-Write |
| `tests/test_admin_source_adapter_live_acceptance.py` | F7.3: Contract-Tests fuer Grant-Expiry, DNS-Rebinding, Evidence-Write und fehlende Runtime-/Store-Verdrahtung |
| `docs/status/f7-3-live-acceptance/ncbi_taxonomy.2026.07.7a73b0fa4d633d2c6514eec1ab00f07ef0e5aa2c75513cbff15dda7b37850e9d.live-acceptance.json` | F7.3: echte Netzwerkabnahme-Evidence fuer Taxonomy-ID `9606`, ohne Raw-Body |
| `docs/status/2026-07-17-feedback-f-F7-3-live-network-acceptance.md` | dokumentiert F7.3-Abschluss und Verifikation |
| `core/admin_catalog/shadow_comparison.py` | F8.1: read-only Schattenvergleich gegen Legacy mit festen Domains, atomarem aktiven Snapshot-Read und Diffklassifikation |
| `tests/test_admin_catalog_shadow_comparison.py` | F8.1: Contract-Tests fuer Read-only-Verhalten, Legacy-Default, Fehlerfaelle, atomaren Snapshot-Read, Legacy-Exportprojektion und fehlende produktive Consumer-Verdrahtung |
| `docs/status/2026-07-18-feedback-f-F8-1-shadow-comparison.md` | dokumentiert F8.1-Abschluss, Verifikation und F8.2-Fortsetzung |
| `core/admin_catalog/runtime_adapter.py` | F8.2/F8.3: `load_catalog_runtime_snapshot()` projiziert Profile, Gruppen, Remedies, Pathogene, Relationen und Multiplexe aus genau einer aktiven Revision; `MORPHIC_ADMIN_CATALOG_ENABLED`, `parse_admin_catalog_enabled()` und `load_configured_runtime()` bilden den expliziten Kill-Switch |
| `services/subgroup_service.py` | F8.2: optionale Catalog-Provider-Injektion fuer Gruppenliste, Gruppenkandidaten und Fullbody-Kandidaten; Default bleibt prozedural |
| `tests/test_admin_catalog_runtime_consumption.py` | F8.2/F8.3: Contract-Tests fuer alle Runtime-Domains, Remedy-/Multiplexaufloesung, fail-closed Fehler, atomaren Snapshot-Read, Revisionsstabilitaet und Kill-Switch-Verhalten |
| `docs/status/2026-07-18-feedback-f-F8-2-runtime-consumption.md` | dokumentiert F8.2-Abschluss, Verifikation und F8.3-Fortsetzung |
| `docs/status/2026-07-18-feedback-f-F8-3-runtime-kill-switch.md` | dokumentiert F8.3-Abschluss, Verifikation und F8.4-Fortsetzung |
| `core/admin_catalog/runtime_acceptance.py` | F8.4 Option A: isolierte Acceptance-Harness fuer Draft/Validate/Diff/Publish/Activate, Runtime-Reload, zweite Aktivierung, Rollback, Kontextisolation, Kill-Switch und Audit-Evidence |
| `tests/test_admin_catalog_runtime_acceptance.py` | F8.4 Option A: Contract-Test mit synthetischen Revisionspayloads und redigierter Evidence |
| `docs/status/2026-07-18-feedback-f-F8-4-runtime-acceptance.md` | dokumentiert F8.4-Option-A-Abschluss, Verifikation und Vorbereitung auf Option B |
| `apps/web/admin_catalog.py` | Option B API/ASGI: geschuetzter `GET /api/admin/catalog/runtime`-Endpunkt mit Runtime-Adapter, Kill-Switch, strukturierten Fehlern und redigierter Response |
| `tests/test_web_admin_catalog_runtime_acceptance.py` | Option B API/ASGI: Bootstrap-Exchange, Admin-Catalog-Lifecycle, Reload, Rollback, Kontextisolation, Kill-Switch und Redaction ueber ASGI-Transport |
| `docs/status/2026-07-18-feedback-f-option-b-live-runtime-acceptance.md` | dokumentiert Option-B-API/ASGI-Abschluss, Verifikation und Browser-Smoke-Nachtrag |
| `apps/web/static/admin.html` | Option B Browser-Smoke: Runtime-Section, Runtime-Metriken und geschuetzter Load-Button fuer Browserabnahme |
| `apps/web/static/admin-catalog.js` | Option B Browser-Smoke: `loadRuntime()` gegen `/api/admin/catalog/runtime`, stabile UI-Ausgabe ohne persistierte Secrets |
| `apps/web/admin_security.py` | Option B Browser-Smoke: Same-Origin-Browserrequests ohne expliziten `Origin`-Header werden aus `Host`/URL abgeleitet und bleiben tokengebunden |
| `tests/test_admin_catalog_dom.py` | Option B Browser-Smoke: DOM-/JS-Vertrag fuer Runtime-Section, Endpoint, Load-Action und Security-Grenzen |
| `tests/test_admin_catalog_runtime_adapter.py` | Option B Browser-Smoke: Runtime-Adapter-Consumer-Guard erlaubt nur die Option-A-Harness, den geschuetzten Admin-Runtime-Endpunkt und den Option-B-Web-Acceptance-Test |
| `docs/status/2026-07-18-feedback-f-option-b-browser-smoke.md` | dokumentiert Browser-Smoke-Abschluss, Headless-Playwright-Evidence und verbleibende Nicht-Produktivfreigabe |
| `tests/conftest.py` | Baselinefix für prozesslokalen Web-Rate-Limiter dokumentiert |
| `tests/test_group_member_consent_revocation.py` | datumsabhängiger Consent-Test wurde auf aktuelle UTC-Zeitbasis repariert |

Aktuelle P1/B1-Verifikation und historische M3-Kontextwerte:

| Lauf | Ergebnis |
|---|---:|
| B1 RED: Completion-Record und fehlende Completion | 2 erwartete Fehler vor Implementierung |
| B1 GREEN zielgerichtet | 2 passed |
| B1 Admin-Backup-Suite | 33 passed, 1 skipped |
| B1 M3-Backup-Migrationskontrakt | 14 passed |
| B1 kombinierte Fokusmatrix | 61 passed, 1 skipped |
| B1 `py_compile` | Exitcode 0 |
| B1 globaler Ruff-Check | Exitcode 0 |
| B1 `git diff --check` | Exitcode 0 fuer tracked diff; nur bestehende LF/CRLF-Warnungen in anderen Dateien; untracked B1-Dateien dadurch nicht abgedeckt |
| B1 direkter trailing-whitespace-Scan | keine Treffer |
| B1 direkter Konfliktmarker-Scan | keine Treffer |
| P1 RED Same-Parent-Guard | 4 erwartete Fehler vor Implementierung |
| P1 GREEN Same-Parent-Guard | 4 passed |
| P1 RED POSIX-`dir_fd`-Fail-Closed | 2 erwartete Fehler vor Implementierung |
| P1 GREEN POSIX-`dir_fd`-Fail-Closed | 2 passed |
| P1 Source-Registry-Atomicity-Suite | 31 passed |
| P1 Source-Registry-Suite | 18 passed |
| P1 Admin-Backup + Migrationsmatrix | 61 passed, 1 skipped |
| P1 kombinierte Fokusmatrix | 110 passed, 1 skipped |
| P1 `py_compile` | Exitcode 0 |
| P1 globaler Ruff-Check | Exitcode 0 |
| P1 `git diff --check` | Exitcode 0 fuer tracked diff; bekannte LF/CRLF-Warnungen; untracked Dateien dadurch nicht abgedeckt |
| P1 direkter trailing-whitespace-Scan | keine Treffer |
| P1 direkter Konfliktmarker-Scan | keine Treffer |
| C1 RED Composition + CLI | 8 erwartete Fehler vor Implementierung |
| C1 GREEN Composition + CLI | 8 passed |
| C1/F5-B Fokusmatrix | 181 passed |
| C1 P1/B1/Migrationsmatrix | 117 passed, 1 skipped |
| C1 `py_compile` | Exitcode 0 |
| C1 globaler Ruff-Check | Exitcode 0 |
| C1 `git diff --check` | Exitcode 0 fuer tracked diff; bekannte LF/CRLF-Warnungen; untracked Dateien dadurch nicht abgedeckt |
| C1 direkter trailing-whitespace-Scan | keine Treffer |
| C1 direkter Konfliktmarker-Scan | keine Treffer |
| REG Admin-Catalog breit | 452 passed, 6 skipped |
| REG Source Registry/Atomicity/Promotion/Draft/CLI | 219 passed, 1 skipped |
| REG Web/Workbench/WebUI Launcher | 153 passed |
| REG Vollsuite ohne Top-5 nach Lintfix | 1076 passed, 8 skipped |
| REG Top-5 nach Lintfix | 1 passed |
| REG Legacy-Multiplex nach Lintfix | 30 passed, 2 skipped |
| REG `py_compile` | Exitcode 0 |
| REG globaler Ruff-Check | Exitcode 0 nach Entfernung eines unbenutzten Imports |
| REG `git diff --check` | Exitcode 0 fuer tracked diff; bekannte LF/CRLF-Warnungen; untracked Dateien dadurch nicht abgedeckt |
| REG direkter trailing-whitespace-Scan | keine Treffer |
| REG direkter Konfliktmarker-Scan | keine Treffer |
| R1 neuer POSIX-Fail-Closed-Test | 2 passed |
| R1 Source-Registry-Atomicity | 33 passed |
| R1 Source Registry/Atomicity/CLI/Promotion/Draft | 129 passed |
| R1 Admin Backup/v7 Backupmigration/F5B Findings | 104 passed, 1 skipped |
| R1 Admin-Catalog breit | 452 passed, 6 skipped |
| R1 Source Registry/Atomicity/Promotion/Draft/CLI/Policy | 221 passed, 1 skipped |
| R1 Web/Workbench/WebUI Launcher | 153 passed |
| R1 Vollsuite ohne Top-5 | 1078 passed, 8 skipped |
| R1 Top-5-Smoke | 1 passed |
| v11 Review 1 | APPROVE, keine P0-P3, keine Drift |
| v11 Review 2 | REQUEST CHANGES, P1 Backup-Publish byte/schema binding, keine Drift |
| R2 neuer Backup-Bytebinding-Test | 1 passed |
| R2 Backup-Testdatei komplett | 34 passed, 1 skipped |
| R2 Admin Backup/v7 Backupmigration/F5B Findings | 105 passed, 1 skipped |
| R2 Admin-Catalog breit | 453 passed, 6 skipped |
| R2 Source Registry/Atomicity/Promotion/Draft/CLI | 164 passed, 1 skipped |
| R2 Vollsuite ohne Top-5 | 1079 passed, 8 skipped |
| R2 Top-5-Smoke | 1 passed |
| FRZ v12 Freeze-Dokument SHA-256 | `64bc565b5e69b9703bef1a425a7d621f21ced6564e457457068b71538e238840` |
| FRZ v12 Scope-Datei | 125 Dateien |
| FRZ v12 Scope-Datei SHA-256 | `807c9893364b24e857e184990904b948dcacdbbe3f923f93b56ccdf617471fd0` |
| FRZ v12 Hash-Manifest SHA-256 | `21df34a8e95c9f5ea4d09fc8733de02b98efa282ac8e7b5e343a4fc04a068559` |
| FRZ v12 Manifest-Rueckverifikation | 125/125 OK |
| REV v12 Review 1 | APPROVE, keine P0-P3, keine Drift |
| REV v12 Review 2 | APPROVE, keine P0-P3, keine Drift |
| Dokumentfreeze v1 Reviews | REQUEST CHANGES, keine Drift, P2/P3 Dokumentrollup |
| Dokumentfreeze v2 | REQUEST CHANGES, keine Drift, P2/P3 Prozent-/Next-Step-Modell |
| Dokumentfreeze v3 | korrigierter Scope/Manifest erzeugt und rueckverifiziert |
| Dokumentreviews v3 | 2x APPROVE, keine P0-P3, keine Drift |
| Post-State-ShadowCopy | 151 Dateien, 151/151 OK, Manifest-SHA `e47cb8accf4e8f5dadb41d56ef29415514e5f5aa1b42568f811ac192f77ed765` |
| F5-C RED | 1 failed, 1 passed wegen fehlender Dokumentgrenzen |
| F5-C GREEN | 2 passed |
| F5-C Source-Matrix | 87 passed |
| F6.1 RED | erwarteter Importfehler fuer fehlendes `apps.web.admin_security` |
| F6.1 GREEN | 8 passed |
| F6.1 Security-/Launcher-Smoke | 11 passed |
| F6.1 Web-App-Regression | 48 passed |
| F6.1 `py_compile` | Exitcode 0 |
| F6.2 RED Service-Injektion | 4 failed wegen fehlender `admin_catalog_service_factory` |
| F6.2 GREEN | 4 passed |
| F6.2 RED PATCH-Route | 1 failed mit `404` fuer `PATCH /api/admin/catalog/drafts/draft-1` |
| F6.2 Web-/Admin-Regression | 52 passed |
| F6.2 Abschlussmatrix Web/Admin/Core | 68 passed |
| F6.2 `py_compile` | Exitcode 0 |
| F6.3 RED | 2 failed wegen zu breiter Source-API und `s.name` im DOM |
| F6.3 GREEN | 2 passed |
| F6.3 Web/Admin-Regression | 34 passed |
| F6.3 `py_compile` | Exitcode 0 |
| F6.4 RED | 4 failed wegen fehlender Admin-UI-Dateien und 404 fuer `/static/admin.html` |
| F6.4 GREEN | 4 passed |
| F6.4 Web/Admin-Regression | 40 passed |
| F6.4 `py_compile` | Exitcode 0 |
| F6.4 JS-Syntax | `node --check` Exitcode 0 |
| F6.4 Konflikt-/Whitespace-/Diff-Check | keine Konfliktmarker, kein trailing whitespace, `git diff --check` Exitcode 0 |
| F7.1 RED | Importfehler fuer fehlendes `core.admin_catalog.network_policy` |
| F7.1 GREEN | 17 passed |
| F7.1 Source-/Workbench-Regression | 157 passed, 1 skipped |
| F7.1 `py_compile` | Exitcode 0 |
| F7.1 Konflikt-/Whitespace-/Diff-Check | keine Konfliktmarker, kein trailing whitespace, `git diff --check` Exitcode 0 |
| F7.1 Ruff | nicht verfuegbar: `No module named ruff` |
| F7.2 RED | Importfehler fuer fehlendes `core.admin_catalog.source_adapters.ncbi_taxonomy` |
| F7.2 GREEN | 4 passed |
| F7.2 Source-/Workbench-Regression | 161 passed, 1 skipped |
| F7.2 `py_compile` | Exitcode 0 |
| F7.2 Konflikt-/Whitespace-/Diff-Check | keine Konfliktmarker, kein trailing whitespace, `git diff --check` Exitcode 0 mit bestehenden LF/CRLF-Warnungen in anderen tracked Dateien |
| F7.2 Ruff | nicht verfuegbar: `No module named ruff` |
| F7.3 RED | Importfehler fuer fehlendes `core.admin_catalog.source_adapters.live_acceptance` |
| F7.3 GREEN | 4 passed |
| F7.3 F7/Source-/Workbench-Regression | 165 passed, 1 skipped |
| F7.3 reale Netzwerkabnahme | Exitcode 0; Evidence-SHA `7a73b0fa4d633d2c6514eec1ab00f07ef0e5aa2c75513cbff15dda7b37850e9d`; Response-SHA `4d3caec1029c7e41c1f03ca6cc7b1c9ebdb8549b7203d49b0eaa9374957f26cf`; DNS pre/post `34.107.134.59`; HTTP 200 |
| F7.3 `py_compile` | Exitcode 0 |
| F7.3 Konflikt-/Whitespace-/Diff-Check | keine Konfliktmarker, kein trailing whitespace, `git diff --check` Exitcode 0 mit bestehenden LF/CRLF-Warnungen in anderen tracked Dateien |
| F7.3 Ruff | nicht verfuegbar: `No module named ruff` |
| F8.1 RED | Importfehler fuer fehlendes `core.admin_catalog.shadow_comparison` |
| F8.1 GREEN | 7 passed |
| F8.1 Admin-/Legacy-/Runtime-Regression | 174 passed, 3 skipped |
| F8.1 `py_compile` | Exitcode 0 |
| F8.1 Konflikt-/Whitespace-/Diff-Check | keine Konfliktmarker, kein trailing whitespace, `git diff --check` Exitcode 0 mit bestehenden LF/CRLF-Warnungen in anderen tracked Dateien |
| F8.1 Ruff | nicht verfuegbar: `No module named ruff` |
| F8.2 RED | 7 failed wegen fehlendem `load_catalog_runtime_snapshot`, fehlendem `CatalogRuntimeError` und fehlender `SubgroupService(catalog_provider=...)`-Injektion |
| F8.2 GREEN | 7 passed |
| F8.2 Runtime-/Shadow-/Store-Fokusmatrix | 128 passed |
| F8.2 Admin-/Legacy-/Runtime-/Subgroup-Regression | 186 passed, 3 skipped |
| F8.2 `py_compile` | Exitcode 0 |
| F8.2 Konflikt-/Whitespace-/Diff-Check | keine Konfliktmarker, kein trailing whitespace mit `[ \t]+$`, `git diff --check` Exitcode 0 mit bekannten LF/CRLF-Warnungen, neu auch fuer `services/subgroup_service.py` |
| F8.2 Ruff | nicht verfuegbar: `No module named ruff` |
| F8.3 RED | 16 failed, 7 passed wegen fehlendem `load_configured_runtime()` und fehlendem `CatalogRuntimeConfigError` |
| F8.3 GREEN | 23 passed |
| F8.3 Admin-/Legacy-/Runtime-/Subgroup-Regression | 202 passed, 3 skipped in 23.25s |
| F8.3 `py_compile` | Exitcode 0 |
| F8.3 Konflikt-/Whitespace-/Diff-Check | keine Konfliktmarker, kein trailing whitespace mit `[ \t]+$`, `git diff --check` Exitcode 0 mit bekannten LF/CRLF-Warnungen |
| F8.3 Ruff | nicht verfuegbar: `No module named ruff` |
| F8.4 Option A RED | `ModuleNotFoundError: No module named 'core.admin_catalog.runtime_acceptance'` |
| F8.4 Option A GREEN | 1 passed in 0.36s |
| F8.4 Option A Runtime-/Web-Fokusmatrix | 28 passed in 2.31s |
| F8.4 Option A finale Matrix | 35 passed in 8.17s |
| Option B API/ASGI RED Endpoint | 1 failed, fehlender Runtime-Endpunkt lieferte HTTP 404 |
| Option B API/ASGI GREEN Endpoint | 1 passed in 0.80s |
| Option B API/ASGI RED Redaction | 2 failed, 2 passed; fehlendes `redacted`-Feld |
| Option B API/ASGI Boundary-GREEN | 4 passed in 1.06s |
| Option B API/ASGI Fokusmatrix | 39 passed in 4.76s |
| Option B UI RED Runtime-Surface | 2 failed, 2 passed; Runtime-Endpoint, Load-Button und UI-Felder fehlten |
| Option B UI GREEN Runtime-Surface | 4 passed in 0.57s |
| Option B Same-Origin-Origin-RED | 1 failed; gleicher Host ohne `Origin` wurde HTTP 403 |
| Option B Admin-Security-GREEN | 9 passed in 0.61s |
| Option B Browser-Prereq-Matrix | 52 passed in 5.29s |
| Option B Browser-Smoke | passed; Quelle `catalog`, finale Revision `browser-revision-a`, Evidence `redigiert`, keine Console-Meldungen |
| Option B finale Adapter-/Pfad-Nachpruefung | 37 passed, 1 skipped in 2.04s; externer Basetemp unter `C:\tmp` |
| Option B finale Vollsuite | 1161 passed, 8 skipped in 160.96s; externer Basetemp unter `C:\tmp` |
| Historische M3 Admin-Catalog-Matrix | 288 passed, 5 skipped |
| Historische Vollsuite nach Baselinefix | 1061 passed, 8 skipped |

Die P1/B1/C1/REG/R1/R2/FRZ-v12/REV-v12-Werte wurden am 2026-07-17 in diesem Worktree ausgefuehrt. Die historischen M3-Werte bleiben Kontextwerte und sind nicht als neuer v12-Freeze zu werten.

## 8. Offene Lücken und Risiken

| Priorität | Lücke | Warum relevant | Nächste Maßnahme |
|---|---|---|---|
| P0 | Abschlussentscheidung offen | Geschlossen: lokaler Checkpoint-Commit `730da8e`; Feedback a wurde danach als separater Layoutblock umgesetzt | Nach Feedback-a-Commit keine weitere Abschlussentscheidung vorziehen |
| P0 | Freeze-Drift waere invalidierend | Jede Aenderung an den 125 Scope-Dateien oder Freeze-Artefakten macht Reviews ungueltig | Vor Reviews Freeze-Dokument-SHA und 125/125 Scope-Hashes erneut pruefen |
| P1 | Working Tree extrem groß und dirty | Tracked-only Commit wäre unvollständig; untracked Archive können Daten enthalten | Hygiene später als eigener Block, nichts pauschal löschen/stagen |
| P1 | Webscan-Exportroot und Reportkatalog können auseinanderlaufen | Weblauncher nutzt explizites `--export`; Reportkatalog liest tenant-suffigierte Roots | Separates Integrationsgate mit E2E-Test |
| P1 | Run-/Webjob-Manifeste noch nicht produktiv verdrahtet | Jobs nach Neustart nicht rekonstruierbar | Späteres Persistence-Gate |
| P1 | Harmonization-Job-Bindung unvollständig | Reportauswahl und Harmonisierung nicht dauerhaft gebunden | Späteres Harmonization-/Artifact-Gate |
| P1 | Feedback a offen | Geschlossen: einheitliches Workbench-Reportdesign technisch umgesetzt | Nachgelagert nur Review/Commit/Workflow-Gates |
| P2 | Packaging/CI unvollständig | Source-Checkout weiter praktisch erforderlich | Professionalisierungsphase nach Sicherheitsabschluss |

## 9. Exakte Fortsetzung

### Jetzt weiter mit Abschlussentscheidung

Ziel: Nach geschlossenem Option-B-Gate eine ausdrueckliche Entscheidung fuer Review/Commit, lokales Behalten oder den naechsten Nutzerfeedbackpunkt treffen.

Konkrete Arbeitsfolge:

1. Feedback-a-Aenderungen final verifizieren.
2. Dirty-State und betroffene Dateien gezielt erfassen.
3. Feedback-a-Commit lokal erstellen.
4. Spaetere Produktiv-, Merge-, Push- und Gesamtabnahme-Gates erst entscheiden, wenn der gesamte Workflow laeuft.

### Danach

| Reihenfolge | Block | Inhalt | Status |
|---:|---|---|---|
| 1 | F8.1 | Schattenvergleich gegen Legacy | technisch geschlossen |
| 2 | F8.2 | Vollstaendige Runtime-Consumption aus einer Revision | technisch geschlossen |
| 3 | F8.3 | Expliziter Kill-Switch | technisch geschlossen |
| 4 | F8.4 Option A | Isolierte synthetische Admin-/Runtime-Abnahme | technisch geschlossen |
| 5 | Option B API/ASGI | Geschuetzter Webtransport bis Runtime-Read-Model | technisch geschlossen |
| 6 | Option B Browser-Smoke | UI-Abnahme ueber `admin.html` | technisch geschlossen |
| 7 | Abschlussentscheidung | Review/Commit, lokales Behalten oder naechster Nutzerfeedbackpunkt | offen |

## 10. Harte Schranken

- Nicht im Root `C:\morphic_v1` arbeiten.
- Kein Commit, Staging, Push, Reset, Cleanup oder Archivverschieben ohne explizite Nutzerfreigabe.
- `Benutzer_Archive__ws-*` nicht pauschal löschen oder stagen.
- Keine produktive Registry-/Remedy-DB-Mutation.
- Keinen produktiven Stage-Key erzeugen.
- Kein produktives Backup und keine Post-State-ShadowCopy vor den vorgeschriebenen APPROVE-Gates.
- Radi144 auf `127.0.0.1:8090` nicht verändern.
- Keine weitere produktive Runtime-Catalogwirkung oder Produktivfreigabe ohne explizite Nutzerentscheidung.
- Freeze-v9/v10/v11-Werte nicht als v12-Abschlussevidenz verwenden.

## 11. Ein-Satz-Standortbestimmung

Wir stehen nach Feedback f / F8.4 Option A, Option B API/ASGI und Option B Browser-Smoke: Der isolierte Admin-/Runtime-Acceptance-Lifecycle, der geschuetzte Webtransport bis Runtime-Read-Model und die Admin-UI-Browserabnahme sind technisch geschlossen; exakt weiter geht es mit der Abschlussentscheidung, ohne Produktivfreigabe, Staging oder Commit.
