# PHASE 5 – Lücken, Problematiken, Innovationen und stabile Gate-Roadmap

## 5.1 Gesamt-Befundmatrix

| Nr | Bereich | Schwere | Befund | Code-/Runtime-Beleg | Empfehlung |
|---:|---|---|---|---|---|
| 1 | Auth | hoch | Web-App kann ohne Auth laufen, wenn `MORPHIC_API_KEY` fehlt. | `apps/web/security.py:40-45` | Non-loopback ohne Auth verbieten; Security Mode anzeigen. |
| 2 | Read-Zugriffe | hoch | Reports und Privacy-Clientliste sind ohne API-Key erreichbar. | `apps/web/main.py:305-335`; Web-Smoke 200 | API-Key/AuthZ auch für Read-Endpunkte. |
| 3 | CORS | hoch | Wildcard-CORS mit Credentials. | `apps/web/main.py:181-188` | Loopback-/Allowlist-CORS; Credentials nur mit expliziter Origin. |
| 4 | Security Headers | hoch | Keine CSP/HSTS/X-Content-Type/Frame-Guard-Middleware sichtbar. | `apps/web/main.py` | Header-Middleware einführen, Tests ergänzen. |
| 5 | Multitenant | hoch | Kein echtes Tenant-/User-/Role-Modell; Stubs erlauben alles. | `core/compliance/operator_context.py`, `entitlement_stub.py:27-47` | Tenant/Role additiv in Manifest und API-Autorisierung. |
| 6 | DSGVO Vollständigkeit | hoch | Löschung deckt nur Manifest-bekannte Artifacts ab, nicht zwingend alle ReportRoot-Dateien. | `runtime_manifest.py:310-318`, `reports.py:317-341` | Retrospektive Indexierung + Manifest-first Reports. |
| 7 | Encryption | hoch | Keine Verschlüsselung at rest/KMS-Schicht sichtbar. | Code-Suche | Für produktive personenbezogene Daten Pflichtgate. |
| 8 | Legacy Web | mittel | `web_app.py` ist 907-Zeilen-Parallel-App mit `/api/v1/*`. | AST-Routenanalyse | Deprecation/Archivierung/Importprüfung. |
| 9 | Legacy CLI Backup | mittel | `apps/cli/main_backup_20251203.py` 9.436 Zeilen liegt im Source-Baum. | LOC-Analyse | Archivieren oder explizit vom Package ausschließen. |
| 10 | Große aktive Module | mittel | `field.py` 4.454 Zeilen, `scan.py` 2.593 Zeilen. | LOC-Analyse | Gateweise Extraktion nach stabilen Tests. |
| 11 | Workflow Progress | mittel | Progress aus stdout-Textmarkern rekonstruiert. | `apps/web/scan_jobs.py:94-151` | Maschinenlesbare Progress-Events. |
| 12 | Ergebnisauflösung | mittel | Web-Ergebnisse werden aus Pfaden/Slug/Session-Ordnern rekonstruiert. | `apps/web/main.py:435-553` | Manifest-first Result Resolver. |
| 13 | Consent Audit | mittel | Consent wird validiert, aber nicht als Audit-/Session-Objekt sichtbar persistiert. | `contracts.py:97-102`, `runtime_manifest.py` | Consent Snapshot in Runtime Manifest. |
| 14 | Audit Integrity | mittel | JSON-Auditlog ohne Hash Chain/Signatur. | `runtime_manifest.py:81-106` | Append-only Hash Chain. |
| 15 | Job Log Privacy | mittel | stdout/stderr Logs können sensitive Pfade/Inputs enthalten; Retention unklar. | `scan_jobs.py:230-238`, `318-319` | Redaction + Retention. |
| 16 | Frontend A11y | mittel | Kein Skip-Link, Fokus beim Stepwechsel nicht gesetzt, Touch Targets 42px. | `index.html`, `app.js:304-310`, `app.css:584-590` | A11y Gate. |
| 17 | CWV / Performance | mittel | Keine RUM-/CWV-/Lighthouse-Messung. | Code-Suche | Optionales Web-Quality Gate. |
| 18 | Reportlisten-Skalierung | mittel | 449 Reports im Smoke; UI rendert Liste direkt. | Web-Smoke `/api/reports`; `app.js:528-577` | Pagination/Filter/Virtualisierung. |
| 19 | TestClient Dependency | niedrig-mittel | Manueller `fastapi.testclient` Smoke blockiert wegen fehlendem `httpx2`. | Terminal-Smoke-Fehler | Entweder `httpx2` Dev-Dependency oder Server-Smoke dokumentieren. |
| 20 | Documentation Drift | mittel | PROJECT_MEMORY nennt 153 Tests; live 230 passed/2 skipped. | Phase 0 | Golden Record aktualisieren. |

## 5.2 Reifegradbewertung

| Dimension | Score | Statussatz |
|---|---:|---|
| Funktionalität lokal | 4.4/5 | CLI/Web/Workflow/Reports/Harmonisierung funktionieren im Smoke/Test. |
| Codequalität | 3.8/5 | Gute Modularisierung, aber große/legacy Dateien. |
| Testcoverage / Regression | 4.3/5 | 230 Tests grün, viele Contract-/Equivalence-/Web-Tests. |
| Sicherheit lokal | 3.0/5 | API-Key optional, Rate Limit, Sanitizer; lokal ok. |
| Sicherheit produktiv | 2.0/5 | Kein echtes Auth/Tenant/Headers/Encryption. |
| DSGVO-Grundlagen | 3.4/5 | Manifest, Löschung, Retention, Audit; nicht vollständig. |
| Frontend UX | 3.8/5 | Gute Operatorführung; A11y/Performance-Gates fehlen. |
| Google/web.dev Qualität | 3.3/5 | Gute statische Grundlagen; keine Messung/Headers. |
| Architektur-Zukunftsfähigkeit | 4.0/5 | Additive Compliance-/Platform-/Radiquant4-Naht vorhanden. |
| Gesamt | 3.6/5 | Lokal sehr gut nutzbar; produktive Plattformreife erfordert Security-/Tenant-/Privacy-Gates. |

## 5.3 Priorisierte Gate-Roadmap

### Gate A – Security Baseline vor jeder externen Nutzung

| Subgate | Ziel | Dateien | Tests |
|---|---|---|---|
| A1 Security Mode | App weiß, ob sie `local-open`, `local-api-key`, `network-blocked`, `network-authenticated` ist | `apps/web/security.py`, `apps/web/main.py` | Web status tests |
| A2 Protected Reads | `/api/reports*`, `/api/privacy*` schützen | `apps/web/main.py` | 401/200 Tests mit/ohne Key |
| A3 CORS Allowlist | Wildcard entfernen | `apps/web/main.py` | Middleware config tests |
| A4 Headers | CSP, X-Content-Type-Options, Referrer-Policy, Frame-Guard, COOP/CORP | `apps/web/main.py` oder neues `headers.py` | Header assertions |
| A5 UI Security Pill | Operator sieht Auth-/Local-Modus | `apps/web/static/*` | Web shell test |

### Gate B – DSGVO/Manifest-first Runtime

| Subgate | Ziel | Dateien | Tests |
|---|---|---|---|
| B1 Consent Snapshot | Consent in Session/Audit speichern | `runtime_manifest.py`, Scan API/CLI | Runtime manifest tests |
| B2 Report Indexing | Alle bestehenden ReportRoot-Dateien manifestieren | neues Tool/CLI unter `apps/cli/commands/privacy.py` oder `reports.py` | Temp report root tests |
| B3 Manifest-first Reports | ReportCatalog mit Artifact IDs verbinden | `apps/web/reports.py`, `runtime_manifest.py` | Report catalog tests |
| B4 DSAR Export | Klientendaten/Sessions/Artifacts/Audit als Paket | Privacy CLI | JSON shape tests |
| B5 Erasure Coverage | Löschung deckt manifestierte Reportdateien ab | `runtime_manifest.py` | Filesystem deletion tests |
| B6 Audit Hash Chain | Manipulation erkennbar | `runtime_manifest.py` | Chain validation tests |

### Gate C – Multitenant-Vorbereitung ohne Big Bang

| Subgate | Ziel | Dateien | Tests |
|---|---|---|---|
| C1 Tenant Field | `tenant_id` additiv mit Default `local` | Runtime stores/contracts | Backward compatibility tests |
| C2 Operator Ownership Web | Jobs/Reports an `OperatorContext` binden | `scan_jobs.py`, `reports.py`, `main.py` | Fremder Owner = 403 |
| C3 Entitlement Integration | Stub an Endpunkte anbinden, ohne Default-Verhalten zu brechen | `entitlement_stub.py`, `main.py` | Default true, custom false |
| C4 Role Skeleton | `admin/operator/viewer` Rollenmodell vorbereiten | neue compliance/auth module | Policy tests |
| C5 Real Auth Decision | API-Key vs. local password vs. OAuth/OIDC entscheiden | Planung vor Code | Architekturentscheidung |

### Gate D – Workflow Eventing und Result-Stabilität

| Subgate | Ziel | Dateien | Tests |
|---|---|---|---|
| D1 JSON Progress Events | CLI schreibt optionale maschinenlesbare Progress Lines | `apps/cli/commands/*`, `scan_jobs.py` | Parser tests |
| D2 Result Manifest | Scan schreibt finales Result-Manifest | CLI export layer | Web result tests |
| D3 Report-ID in Harmonization | Harmonisierung bekommt Artifact/Report-Kontext | `app.js`, `main.py`, `harmonization.py` | Job payload tests |
| D4 Log Redaction | PII in Logs maskieren | `scan_jobs.py` | Redaction tests |

### Gate E – Frontend Quality / Google-web.dev Engineering

| Subgate | Ziel | Dateien | Tests |
|---|---|---|---|
| E1 Skip/Fokus/Touch | A11y-Basis schließen | `index.html`, `app.js`, `app.css` | Static DOM tests |
| E2 Report Filter/Pagination | 449+ Reports performant | `app.js`, `reports.py` | API/UI tests |
| E3 CWV Mini Metrics | INP/LCP/CLS lokal messbar | `app.js` optional | Disabled-by-default tests |
| E4 Visual/Accessibility Smoke | Playwright/Lighthouse optional | Tests/Dev deps | Nicht blockierend einführen |

### Gate F – Legacy-/Repo-Hygiene

| Subgate | Ziel | Dateien | Tests |
|---|---|---|---|
| F1 Legacy Inventory | `web_app.py`, `main_backup` und alte Backups offiziell klassifizieren | docs + packaging | Import boundary tests |
| F2 Package Exclusions | Backup/Legacy nicht paketieren | `pyproject.toml` | Build/package test |
| F3 Golden Record Update | `PROJECT_MEMORY`/`CLAUDE.md` an Live-Stand anpassen | Docs | Keine Codewirkung |
| F4 Large Module Decomposition Plan | `field.py`/`scan.py` nur geplant, nicht sofort refactoren | docs/superpowers plan | Gate approval |

## 5.4 Stabile Innovationen

| Innovation | Nutzen | Warum stabil/additiv | Risiko |
|---|---|---|---|
| Security Mode Pill | Operator erkennt sofort, ob App offen/geschützt ist | Addiert Statusfeld, ändert keine Scoringlogik | gering |
| Manifest-first Report Lifecycle | DSGVO, Suche, Löschung und UI werden konsistent | Ergänzt Manifest; ReportCatalog kann fallback behalten | mittel |
| Audit Hash Chain | Rechtliche/technische Nachvollziehbarkeit steigt | Addiert Felder, alte Logs migrierbar/validierbar | mittel |
| JSON Progress Events | UI wird robust gegen Textänderungen | stdout-Text bleibt erhalten, JSON optional | gering-mittel |
| 12-Step Live Timeline | Brücke zwischen Radi144-Workflow und Operator-UI | Nutzt vorhandenes `SUBSTEP_MANIFEST` | mittel |
| Report-ID-gebundene Harmonisierung | Abschluss wird nachvollziehbar und auditierbar | Payload-Erweiterung, bestehende Parameter bleiben | gering-mittel |
| Local CWV/A11y Gate | Web-Qualität messbar | Dev-only, keine Runtime-Last | gering |
| Tenant-ready Runtime Schema | Spätere Plattformfähigkeit ohne Big Bang | Default `local`, additive Migration | mittel |
| DSAR Export Packet | DSGVO-Auskunft praktisch ausführbar | Nutzt vorhandene Stores/Artifacts | mittel |
| Log Redaction Layer | Weniger PII in Debug-/Joblogs | Additive Filterfunktion | gering |

## 5.5 Diskussionsentscheidungen vor Umsetzung

| Entscheidung | Optionen | Auswirkung |
|---|---|---|
| Betriebsmodell | Lokal-only / LAN / Internet / SaaS-Multitenant | Bestimmt Auth-, Header-, TLS-, Tenant- und Verschlüsselungspflichten. |
| Auth-Modell | API-Key streng / lokaler Login / OIDC / Windows-User | Bestimmt Implementierungsaufwand und Nutzerführung. |
| Datenhaltung | JSON Stores weiter / SQLite / externe DB | Bestimmt Transaktionen, Migration, DSGVO-Erfüllbarkeit. |
| Report-Daten | Dateisystem bleibt führend / Manifest wird führend | Bestimmt Lösch-/DSAR-Konsistenz. |
| UI-Zielgruppe | Nur Operator / auch Klienten/Kunden | Bestimmt Accessibility/BFSG/UX/DSGVO-Texttiefe. |
| Google-Ziel | Nur web.dev Qualität / echte SEO | Für lokale App ist SEO unnötig; öffentliche Produktseite wäre separates Projekt. |

## 5.6 Empfohlene Reihenfolge

| Priorität | Gate | Warum zuerst? |
|---:|---|---|
| 1 | Gate A Security Baseline | Verhindert, dass eine bereits funktionale Web-Shell versehentlich offen mit sensiblen Daten läuft. |
| 2 | Gate B DSGVO/Manifest-first Runtime | Schließt Daten-/Report-/Lösch-Konsistenz. |
| 3 | Gate E1 A11y Quick Wins | Kleine, risikoarme UI-Verbesserungen. |
| 4 | Gate D Progress/Result Manifest | Macht Workflow/UI robuster und auditierbarer. |
| 5 | Gate C Tenant Skeleton | Nur wenn produktive Mehrbenutzerfähigkeit wirklich Ziel ist. |
| 6 | Gate F Repo-Hygiene | Wichtig, aber nach Security/DSGVO nicht akut gefährlich. |

## 5.7 Schlussurteil

Morphic Engine V1 ist in der lokalen Projektform funktionsstark, teststabil und strukturell deutlich besser als ein früherer Monolith. Die größten offenen Punkte sind nicht Algorithmen- oder Workflow-Abwesenheit, sondern Plattformhärtung: echte Authentifizierung, Mandantentrennung, Zugriffsschutz auf Reports, DSGVO-vollständige Artefaktverwaltung, Security-Headers und belastbare Web-Qualitätsmessung.

Die nächsten Umsetzungen sollten deshalb nicht mit neuen fachlichen Features beginnen, sondern mit einem stabilen Security-/DSGVO-Baseline-Gate. Danach können UI/UX- und Workflow-Innovationen sicher und additiv weitergeführt werden.
