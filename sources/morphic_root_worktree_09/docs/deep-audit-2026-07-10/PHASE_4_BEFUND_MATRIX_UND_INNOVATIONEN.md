# Phase 4 – Befundmatrix, Priorisierung und stabile Innovationen

## 4.1 Priorisierte Befundmatrix

| Prio | Befunde | Gate | Aufwand | Ziel |
|---|---|---|---|---|
| P0 | S-01–S-07, S-13–S-14 | Identity & Tenant Boundary | groß | fail-closed Auth, Rollen, tenant-abgeleitete Datenzugriffe, sichere DOM-Ausgabe, Encryption/ACLs |
| P0 | S-07/S-08/S-12 | Privacy Data Lifecycle | groß | Dateninventar, Consent-Evidence, Retention-Policy, vollständige Lösch-/Backupkaskade |
| P1 | U-05 | Report Trust Boundary | klein | `innerHTML` entfernen, report labels/HTML als untrusted testen |
| P1 | U-01–U-03/U-08 | Operator E2E Quality | mittel | UI-Gates, klare Fehlerführung, automatische Ergebnisnavigation, Playwright/a11y |
| P1 | A-01 | Algorithm Traceability | mittel | maschinenlesbares Run-Manifest mit Versionen, Seeds, Inputhashes, Parametersätzen |
| P1 | A-02 | Modifier-Wiring | klein–mittel | call-site/E2E-Nachweis für `calculate_resonance_modifiers`; erst danach Radi144-Vektorformular |
| P1 | O-01 | Reliable Job Runtime | mittel | persistente Jobmetadaten, restart recovery, strukturierte Events statt stdout-Parsing |
| P2 | D-01 | Documentation Truth | klein | README, config.yaml und aktuelle Pfade konsolidieren |
| P2 | D-02 | Deployment Baseline | mittel | CI, lockfile, SBOM/dependency scanning, signed release/backup policy |

## 4.2 Weitere codebasierte Befunde

| Nr. | Befund | Schwere | Beleg |
|---:|---|---|---|
| A-01 | Algorithmuskonstanten (z. B. Resonator alpha/beta/gamma, NLS 0.6/0.4, Reliability- und personal-alignment-Faktoren) sind im Code fest. Es gibt Tests für Verhalten, aber kein versioniertes Parameter-/Kalibrierungsprotokoll pro Report. | mittel | `core/resonance/resonator.py:18-33`; `core/nls/nls_db.py:49-51,106-121` |
| A-02 | Das umfangreiche `ClientProfile` enthält hochsensible medizinische Daten und berechnet sieben Modifier. Vor UI-Erweiterung muss der aktive Pipeline-Callgraph nachweisen, welche Modifier tatsächlich Scores beeinflussen. | hoch | `core/client_profile.py:14-58,116-183` |
| O-01 | Scanjobs sind pro App-Prozess im RAM; serverrestart verliert Lookup/Ownership/Status trotz noch vorhandener Logs. | mittel | `apps/web/scan_jobs.py:218-270` |
| O-02 | Fortschritt nutzt Textmarker in stdout statt strukturierter Events; Änderungen an CLI-Texten können UI-Fortschritt brechen. | mittel | `scan_jobs.py:29-151` |
| O-03 | Runtime- und Workbench-Stores besitzen nur Thread-Locks. Multiworker/Mehrinstanzenbetrieb wird nicht abgesichert. | mittel | `runtime_manifest.py:74-79`; `workbench_runtime.py:26-57` |
| O-04 | Harmonization-UI-Parameter Pulse/Pause/Solfeggio haben im Worker keine nachgewiesene Takt-/Frequenzwirkung; die heutige Schleife arbeitet sekundenbasiert. | hoch | `services/harmonization_worker.py:376-381,401-448,495-545` |
| U-01 | Hardware-Review kann wegen Dictionary/Array-Vertragsbruch abbrechen; API-Fehler können wegen fehlendem `response.ok` fälschlich als Start interpretiert werden. | hoch | `workbench-render.js:145-146`; `workbench-api.js:60-75`; `app.js:184-201` |
| D-01 | `config.yaml` referenziert gelöschte alte Exportroots; `PROJECT_MEMORY` markiert dies selbst als offen. | niedrig | `config.yaml:1-4`; `PROJECT_MEMORY/00_CURRENT_STATE.md:99-107` |
| D-02 | README beschreibt einen früheren Scaffold-Zustand und Python 3.13, während reale App Python 3.12 nutzt. | niedrig | `README.md:23-28`; Health-Smoke |

## 4.3 Stabile Innovationen (additiv, keine Kernengine-Änderung)

| Innovation | Nutzen | Sicherer Einstieg |
|---|---|---|
| Authenticated Operator Context Adapter | ersetzt env/getpass durch Claim-basierte IDs ohne Engineänderung | Interface neben `resolve_operator_context`, Test-double beibehalten |
| Tenant-scoped Artifact Repository | isolierte Metadaten, Reportrechte und Erasure-Abdeckung | zuerst read-only catalog adapter, danach write path |
| Signed Run Manifest | Reproduzierbarkeit: code commit, profile/data hashes, seed-mode, parameter-version, artifact hashes | JSON Schema + append-only manifest, zunächst parallel zum aktuellen Export |
| Strukturierte Progress Events | UI stabil gegen CLI-Textänderung, bessere Auditierbarkeit | JSONL Event-Emitter parallel zu stdout, UI fallback beibehalten |
| Privacy Policy Engine | consent/retention/erasure nach Policy-Version und Tenant | dry-run only, kein automatisches Löschen bis Freigabe |
| Data Classification | PII/health-data Markierung pro Feld/Artefakt, Export-Minimierung | Datenschema-/Report-Adapter, keine Scoreänderung |
| UI Quality Harness | Browser-E2E, axe, Lighthouse CI, Screenshot-basierte Regression | read-only Tests gegen temporäre Runtime |

## 4.4 Vorgeschlagene Ausführungsreihenfolge (noch kein Umsetzungsauftrag)

1. **Gate P0-Workbench-Vertrag:** Hardware-Review, HTTP-Fehlervertrag, XSS-Sinks und Scanstart-Validierung mit Browser-Regressionstests schließen.
2. **Gate P0-Identity:** Threat model und Entscheidung lokaler Einoperator vs. Netzwerk-Multitenant; keine kosmetische API-Key-Erweiterung als Ersatz.
3. **Gate P0-Data lifecycle:** Datenkarte einschließlich Exporte, Tempdateien, Browser LocalStorage, Logs und Backups; Löschtest mit temporärer Testumgebung.
4. **Gate P1-Traceability:** additive Run-Manifeste und vollständige Algorithmus-/Datenversionsbelege; bestehende Scores unverändert.
5. **Gate P1-Modifier:** erst Callgraph, dann gezielte Datenfelder mit Datenschutzfolgeabschätzung und TDD.
6. **Gate P1-Worker-Semantik:** Impuls/Pause/Solfeggio mit Mock-Clock als echte State-Machine oder UI-/API-Parameter ehrlich zurückbauen.
7. **Gate P1-Workbench quality:** U-01 bis U-14, Playwright/axe/Lighthouse.
8. **Gate P2-Betrieb:** CI, Release-/Backup-/Restore-Probe, Monitoring und README-/Config-Hygiene.

Jedes Gate folgt dem vorhandenen Sicherheitsmuster: ShadowCopy außerhalb des Projektbaums, RED-Test, additive/default-erhaltende Implementierung, Volltest, Browser-/Smoke-Nachweis, Commit und dokumentierter Restorepunkt.
