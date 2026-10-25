# PHASE 3 – Sicherheit, DSGVO, Authentifizierung und Multitenant

## 3.1 Sicherheitsmodell – Ist-Zustand

| Komponente | Implementierung | Beleg | Bewertung |
|---|---|---|---|
| API-Key | Header `X-API-Key`, erwartet `MORPHIC_API_KEY`; wenn Env nicht gesetzt, Auth übersprungen | `apps/web/security.py:24-52` | Lokal bequem, produktiv hochriskant. |
| Rate-Limit | In-memory pro Client-IP, 60 Requests / 60 Sekunden | `apps/web/security.py:26-30`, `55-82`; Middleware in `apps/web/main.py:174-179` | Grundschutz, aber nicht persistent/distributed. |
| Input-Validation Web Scan | Pydantic-Model `Phase1ScanRequest` mit Pflichtfeldern, Top-N, Level, Entropie, Consent | `apps/web/contracts.py:8-102` | Gut für API-Kontrakt. |
| Input-Validation Helpers | Name/Fokus/Intention/Birthdate Helper | `apps/web/security.py:85-141` | Vorhanden, aber nicht überall sichtbar genutzt. |
| CORS | `allow_origins=["*"]`, `allow_credentials=True`, alle Methoden/Header | `apps/web/main.py:181-188` | Für echte Web-Exposition falsch; nur lokal tolerierbar. |
| Security Headers | Keine zentrale CSP/HSTS/X-Frame/X-Content-Type-Middleware in `apps/web/main.py` sichtbar | `apps/web/main.py:190-203` setzt nur No-Cache für UI | Lücke. |
| HTML-Preview-Sanitizing | Allowlist-Parser; blockt `script`, `style`, `iframe`, `object`, `embed`, `svg`, `math` | `apps/web/reports.py:56-107`, `109-175`, `531-555` | Positiv; reduziert XSS in Report-Preview. |
| File Serving | Reports nur über IDs aus `ReportCatalog`, Pfad muss unter Root liegen | `_is_relative_to` `apps/web/reports.py:177-182`, `_find` `265-272` | Gute Pfadbegrenzung. |
| Prozessstart | Web-Scan startet über `subprocess.Popen(shell=False)` | `apps/web/scan_jobs.py:239-250` | Positiv gegen Shell-Injection; Input trotzdem fachlich validieren. |
| Secrets | Kein hartkodierter API-Key sichtbar; Env-basiert | `apps/web/security.py:32-34` | Gut, aber optional. |

## 3.2 Authentifizierung – Code-echter Stand

| Frage | Antwort | Beleg |
|---|---|---|
| Gibt es Login/Benutzerkonten? | Nein. Kein User-/Password-/Session-/OAuth-/JWT-System in aktiver Web-App sichtbar. | Suche nach `login/password/jwt/token/session/cookie/csrf`; nur optionale API-Key-/Session-Datenmodelle gefunden. |
| Gibt es API-Key? | Ja, optional. | `verify_api_key` in `apps/web/security.py:37-52`. |
| Sind kritische Endpunkte geschützt? | Teilweise: Scan Preview/Start und Harmonization Start/Stop hängen an `Depends(verify_api_key)`, aber wenn kein Env-Key gesetzt ist, ist Schutz aus. | `apps/web/main.py:337-392`. |
| Sind Read-Endpunkte geschützt? | Nein sichtbar: `/api/reports`, `/api/reports/{id}/preview/file`, `/api/privacy/clients`, `/api/health`, `/api/sources` ohne API-Key-Dependency. | `apps/web/main.py:235-335`. |
| Gibt es CSRF-Schutz? | Nein sichtbar. | Keine CSRF-Middleware/Token im Frontend/API. |
| Gibt es Cookie-Sessions? | Nein sichtbar. | Fetch nutzt JSON ohne Credentials-/Cookie-Flow. |

## 3.3 Multitenant – Code-echter Stand

| Baustein | Implementiert? | Beleg | Bewertung |
|---|---|---|---|
| OperatorContext | Ja, lokal abgeleitet aus OS-User/Host + Workspace-ID | `core/compliance/operator_context.py:33-88` | Erweiterungsnaht, kein Auth. |
| Ownership-Check | Ja als Funktion `assert_owner(...)` | `core/compliance/operator_context.py:91-106` | Additiv; nicht flächendeckend erzwungen. |
| Entitlement-Stub | Ja; Default erlaubt alles | `core/compliance/entitlement_stub.py:27-47` | Saubere Naht, ausdrücklich kein Gating. |
| Tenant-ID im Runtime-Manifest | Nein sichtbar | `runtime_manifest.py` Stores: clients/sessions/artifacts/audit_log ohne tenant_id | Keine echte Mandantentrennung. |
| Tenant-spezifische Report-Roots | Nein | `DEFAULT_REPORT_ROOTS` global in `apps/web/main.py:54-60` | Alle Reports liegen in gemeinsamen Wurzeln. |
| Tenant-spezifische API-Autorisierung | Nein | Read-Endpunkte ohne Auth/Ownership | Hochriskant bei Mehrbenutzerbetrieb. |

Wichtig: Der Code ist ehrlich. `operator_context.py:8-13` sagt explizit, dass dies kein echtes Auth-/Multitenant-System ist, sondern eine Vorbereitungsschicht.

## 3.4 DSGVO / Privacy – Ist-Zustand

| DSGVO-Anforderung | Vorhandene Umsetzung | Beleg | Lücke |
|---|---|---|---|
| Datenminimierte Client-Liste | `/api/privacy/clients` gibt nur `client_id`, `created_at`, `updated_at` zurück | `RuntimeManifestService.list_clients_safe` in `runtime_manifest.py:135-144`; Endpoint `main.py:305-309` | Rohdaten bleiben im Store/Reports. |
| Auskunft/Manifest | `erasure_manifest(client_id)` sammelt Sessions/Artifacts | `runtime_manifest.py:240-269` | Kein vollständiges DSAR-Exportformat für Betroffene. |
| Löschung | `execute_erasure` mit Gate-Token; löscht Clients/Sessions/Artifacts und Artifact-Dateien | `runtime_manifest.py:271-351` | Nur Manifest-Artifacts; eventuell nicht indexierte Reportdateien bleiben. |
| Retention | `find_expired_clients`, `purge_expired`, Dry-run | `runtime_manifest.py:390-458` | Policy/Standardtage/Automatisierung nicht zentral sichtbar. |
| Audit | `append_audit` schreibt Event-ID, Actor, Action, Client, Entity, Outcome, Detail | `runtime_manifest.py:81-106` | Nicht manipulationssicher; keine Signatur/Hash Chain. |
| Consent | UI verlangt lokale Verarbeitung + Wellbeing-Hinweis; API validiert beide `True` | `index.html:95-102`, `contracts.py:97-102` | Consent wird nicht sichtbar als eigene Audit-Entität persistiert. |
| Wellbeing Disclaimer | Berichtssicherheitsmarker und HTML/TXT-Blöcke | `core/compliance/safety.py:6-35` | Kein umfassender medizinischer Claim-Scanner in dieser Datei sichtbar. |
| Datenschutz by Design | Lokale Verarbeitung, Safe List, Gate Token, No-Cache UI | diverse | Keine Verschlüsselung at rest, keine Rollen, keine Mandanten. |

## 3.5 Sensible Datenflüsse

| Daten | Erfassung | Verarbeitung | Speicherung/Anzeige | Risiko |
|---|---|---|---|---|
| Name/Vorname/Geburtsdatum/Geburtsort | Web-Form `index.html:115-132`, API `Phase1ScanRequest` | CLI Preview/Scan Command; Client-Slug/Runtime ID | Reports unter `C:/Benutzer_*_Start`, Runtime Manifest | Personenbezug hoch; Dateinamen/Pfade können Identität tragen. |
| Fokus/Symptom | UI Step 4, API Payload | Scoring/Report/Preview | Reports/Logs | Gesundheitsnah; klare Disclaimer nötig. |
| Bildpfad | optional `image_path` | an CLI übergeben, kein Upload im UI sichtbar | Pfad in Preview/Logs | Lokale Pfade können sensitive Namen enthalten. |
| Reports | CLI Export | Web ReportCatalog | HTML/JSON/TXT/PDF Preview/File | Zugriff aktuell ohne echte Auth möglich. |
| Job Logs | CLI stdout/stderr | Polling/Progress | `codex_tmp/web-jobs` oder Runtime `web_jobs` | Können Eingaben/Fehler/Pfade enthalten; Retention/Maskierung unklar. |

## 3.6 Konkrete Security-/DSGVO-Befunde

| Nr | Kategorie | Schwere | Befund | Beleg | Empfehlung |
|---:|---|---|---|---|---|
| S1 | Auth | hoch | API-Key ist optional; ohne `MORPHIC_API_KEY` läuft Web-App ohne Auth. | `apps/web/security.py:40-45` | Für alles außer localhost-dev Auth zwingend aktivieren; Start verweigern, wenn Host != loopback und kein Key. |
| S2 | Read Protection | hoch | Report- und Privacy-Read-Endpunkte sind ungeschützt sichtbar. | `apps/web/main.py:305-335` | `Depends(verify_api_key)` oder echte Session/AuthZ auch für Reads. |
| S3 | CORS | hoch | `allow_origins=["*"]` + `allow_credentials=True`. | `apps/web/main.py:181-188` | Loopback/konfigurierbare Origin-Allowlist; Credentials nicht mit Wildcard. |
| S4 | Security Headers | hoch | Keine CSP/HSTS/X-Content-Type/Frame-Policy-Middleware sichtbar. | `apps/web/main.py:190-203` | Zentrale Header-Middleware mit lokalem Default. |
| S5 | Multitenant | hoch | Kein echtes Tenant-Feld in Clients/Sessions/Artifacts; Entitlements erlauben alles. | `runtime_manifest.py:17-22`, `entitlement_stub.py:27-47` | Tenant-ID, Role, Ownership, ReportRoot-Scope additiv einführen. |
| S6 | DSGVO Löschung | mittel-hoch | Löschung entfernt nur Manifest-bekannte Artifacts; ReportCatalog scannt unabhängige Dateiwurzeln. | `runtime_manifest.py:310-318`, `reports.py:317-341` | Retrospektive Report-Indexierung + Löschung gegen tatsächliche Report-Roots. |
| S7 | Audit Integrity | mittel | Auditlog ist JSON ohne Hash Chain/Signatur. | `runtime_manifest.py:81-106` | Append-only Hash Chain pro Event und Exportprüfsumme. |
| S8 | Consent Persistenz | mittel | Consent wird zur API-Validierung genutzt, aber nicht sichtbar auditierbar persistiert. | `contracts.py:97-102` | Consent Snapshot im Session-/Audit-Manifest speichern. |
| S9 | Logs | mittel | Job-Logs werden erstellt, aber Retention/Maskierung nicht zentral sichtbar. | `scan_jobs.py:230-238`, `318-319` | Log-Retention, Redaction, Zugriffsschutz. |
| S10 | Encryption | mittel-hoch | Keine at-rest Encryption/KMS-Schicht sichtbar. | Code-Suche | Für produktive Personen-/Gesundheitsdaten Verschlüsselung ergänzen. |

## 3.7 Empfohlene Sicherheits-Gates

| Gate | Ziel | Minimaler Scope | TDD/Verifikation |
|---|---|---|---|
| SEC-1 Loopback/Auth Guard | Keine versehentliche öffentliche App ohne Auth | Host/Origin/Auth-Policy in `apps/web/security.py`/`main.py` | Tests: kein API-Key bei non-loopback = Start/Request verweigert; loopback dev bleibt möglich. |
| SEC-2 Security Headers | Browser-Baseline | Middleware für CSP, X-Content-Type-Options, Referrer-Policy, Frame-Guard, COOP/CORP; HSTS nur HTTPS | Web-Shell Tests prüfen Header. |
| SEC-3 Protected Reads | Reports/Privacy nicht offen | API-Key/AuthZ auf `/api/reports*`, `/api/privacy*` | Tests für 401 bei fehlendem Key und 200 bei gültigem Key. |
| SEC-4 Tenant Manifest | Additive Tenant-ID | `tenant_id`, `operator_id`, `workspace_id` in clients/sessions/artifacts; Default `local` | Rückwärtskompatible Migrationstests. |
| SEC-5 DSAR/Retention Hardening | DSGVO-Prozess schließen | Retrospektive Report-Indexierung, Lösch-Dryrun, Lösch-Audit mit Hash | Tests mit Temp-ReportRoot. |
| SEC-6 Audit Hash Chain | Manipulationshinweis | `prev_hash`, `event_hash` im Auditlog | Tests: Chain validiert, Manipulation erkannt. |

## 3.8 Reifegrad Phase 3

| Dimension | Score | Begründung |
|---|---:|---|
| Lokaler Dev-Schutz | 3.2/5 | Rate Limit, optionaler API-Key, Pydantic, Sanitizer. |
| Produktive Auth | 1.8/5 | Kein echtes Login/Rollen/Tenants. |
| DSGVO-Grundlagen | 3.4/5 | Safe-List, Löschung, Retention, Audit vorhanden. |
| Multitenant-Reife | 2.0/5 | OperatorContext/Entitlement nur Stub/Naht. |
| Web-Hardening | 2.4/5 | CORS/Headers/Protected Reads offen. |

Phase-3-Urteil: Für lokale Einzelplatznutzung akzeptabel, für echte Plattform-/Mandanten-/personenbezogene Web-Nutzung nicht bereit. Security muss vor jeder externen Bereitstellung priorisiert werden.
