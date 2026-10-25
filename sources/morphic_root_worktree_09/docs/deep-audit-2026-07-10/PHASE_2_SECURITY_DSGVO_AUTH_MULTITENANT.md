# Phase 2 – Security, DSGVO, Authentifizierung und Multitenancy

## 2.1 Implementiert vs. nicht implementiert

| Bereich | Code-Echter Status | Beleg |
|---|---|---|
| API-Key | optionaler globaler Shared Secret Header `X-API-Key`; ohne `MORPHIC_API_KEY` vollständig offen | `apps/web/security.py:32-52` |
| Rate Limit | pro IP, in Memory, 60/min; keine Persistenz/Proxy-Trust-Konfiguration | `security.py:26-29,55-82` |
| CORS | `allow_origins=["*"]` plus `allow_credentials=True` | `apps/web/main.py:308-315` |
| Inputvalidation | Pydantic-Felder/Enum-ähnliche Validatoren für Webscan; nicht durchgehend `extra=forbid` | `apps/web/contracts.py:15-119` |
| Job-Ausführung | `subprocess.Popen(... shell=False)`; vorhandenes `python` wird durch `sys.executable` ersetzt | `scan_jobs.py:72-75,226-265` |
| Ownership | Scanresult prüft owner nur falls owner_id gesetzt; Legacy-/unowned Jobs sind erlaubt | `main.py:547-554`, `operator_context.py:107-122` |
| Tenant | tenant_id = env override oder lokale workspace_id; Pfad-Suffix, leseseitiger ReportCatalog pro Request | `operator_context.py:79-104`, `main.py:270-286` |
| Datenschutzregister | JSON Clients/Sessions/Artefakte/Audit, Safe Client List | `runtime_manifest.py:17-22,135-144` |
| Löschung | Manifest, Gate-Token und Kaskade über Register/registrierte Einzeldateien | `runtime_manifest.py:240-351` |
| Retention | Parameterisierter CLI-Service inkl. dry-run, kein geplanter Scheduler/policy-default | `runtime_manifest.py:390-458` |
| Verschlüsselung | nicht gefunden | JSON, Log- und Exportdaten werden als Dateien persistiert |
| echte AuthN/AuthZ/RBAC | nicht vorhanden | `operator_context.py:1-13` bezeichnet sich selbst ausdrücklich als Vorbereitungsschicht |

## 2.2 Befundmatrix

| Nr. | Befund | Schwere | Codebezug | Konkrete Auswirkung / Abhilfe |
|---:|---|---|---|---|
| S-01 | Auth fällt ohne Environment-Secret komplett weg. | hoch | `security.py:40-45` | Internetbetrieb darf ohne fail-closed Deployment-Guard nicht erfolgen. |
| S-02 | Shared API-Key ist kein Benutzer, keine Session, kein Tenant und keine Rolle. | hoch | `security.py:37-52` | OIDC/SSO oder signierte Session + serverseitige Benutzer-/Tenant-/Rollenauflösung vor Multiuserbetrieb. |
| S-03 | Wildcard-CORS mit Credentials ist fehlkonfigurationsanfällig. | hoch | `main.py:308-315` | explizite Origins, credentials nur wenn benötigt, CSRF-Modell für Cookie-Auth. |
| S-04 | Mehrere sensible GET-Endpunkte haben keine `verify_api_key`-Dependency: Reports, Privacy-Safe-List, Jobstatus/-resultate, Workbench Draft/Templates. | hoch | `main.py:399-429,522-683`; `workbench.py:17-77` | zentrale Auth-Middleware bzw. Router-Dependency; Ownership auf **allen** Ressourcenzugriffen. |
| S-05 | Tenant-Isolation ist nur Pfadkonvention. `MORPHIC_TENANT_ID` ist nicht aus authentisiertem Principal abgeleitet; explizite Output-Pfade werden nicht isoliert. | hoch | `operator_context.py:79-103`; `utility_helpers.py:49-61` | Tenant aus serverseitiger Auth-Claim ableiten, DB row-level/tenant predicates, Pfad-Allowlist. |
| S-06 | Unowned Legacy-Jobs sind zugänglich; nur `results`, nicht Status/WebSocket, prüft Owner. | hoch | `operator_context.py:110-119`; `main.py:522-554`; `scan_live.py:22+` | Migration: owner_id verpflichtend; get/status/results/ws durch einheitlichen resource guard. |
| S-07 | personenbezogene und potenziell Gesundheitsdaten liegen in Klartext-JSON/Exporten, Dateinamen enthalten Identifikatoren. | hoch | `runtime_manifest.py:116-124`, `client_profile.py:79-101`, Exporthierarchie | Verschlüsselung at rest, pseudonymisierte IDs/Dateinamen, ACLs, key rotation, Export-Minimierung. |
| S-08 | Löschroutine löscht nur registrierte Artefakte als einzelne Dateien; nicht nachweislich alle abgeleiteten Exporte, Backups, Logs, Browserdaten. | mittel | `runtime_manifest.py:309-320` | Dateninventar/Verarbeitungsverzeichnis, rekursive kontrollierte purge policy, Backup-Tombstone/Restore-Sperre. |
| S-09 | Standard-Löschtoken ist im Quellcode bekannt. | mittel | `runtime_manifest.py:12,271-284` | nur Secret Manager/Deployment Secret, keine Source-defaults für produktive Löschung. |
| S-10 | Rate limit ist pro Prozess/IP; kein Redis, keine Auth-Identität, keine Audit-/Alert-Kopplung. | mittel | `security.py:26-82` | Gateway/WAF + verteiltes Limit + Login-/abuse monitoring. |
| S-11 | Pydantic-Scanrequest ignoriert unbekannte Felder, da kein `extra="forbid"`. | niedrig | `contracts.py:15-119` | bei externem API-Vertrag strict input schemas verwenden. |
| S-12 | Consent ist Boolean im Request, keine versionierte Einwilligung, kein Zweck/Policy-Text, kein zeitstempelbasierter Nachweis. | mittel | `contracts.py:30-31,114-119`; `index.html:93-99` | Consent-Record mit policy_version, timestamp, actor, tenant, purpose und Widerruf. |
| S-13 | Der Web-Scan-Launcher übergibt einen harten, expliziten Exportroot `C:\\Benutzer_Archive_Start`; dadurch greift die tenant-suffixierte Defaultpfadlogik nicht. | hoch | `apps/web/launcher.py:9-13,24-55`; `tools/reporting_common.py:68-93` | Exportroot ausschließlich serverseitig aus authentisiertem Tenant ableiten; E2E-Test Scan → Export → Report-Katalog. |
| S-14 | Dynamische Workbench-Werte werden mehrfach unescaped via `innerHTML` eingebettet; Pydantic trimmt, escaped aber nicht. | hoch | `apps/web/static/workbench-render.js:86-110,123-146,211-214`; `apps/web/static/app.js:284-307` | `textContent`/DOM-Nodes verwenden, CSP ergänzen und XSS-Regressionstests für Klient/Fokus/Report/Hardware. |

## 2.3 DSGVO-Abgleich (technisch, keine Rechtsberatung)

**Positiv:** Datenminimierte API-Safe-View (`client_id`, Zeitstempel), Audit-Entries, Erasure-Manifest vor Löschung, atomare Storewrites und retention dry-run sind solide Vorarbeiten. **Nicht ausreichend als alleinige DSGVO-Compliance:** Rechtsgrundlage/Zweckbindung, Verzeichnis von Verarbeitungstätigkeiten, TOMs, Auftragsverarbeitung, Betroffenenprozesse, Schlüsselmanagement, Backups, Breach-Prozess, Zugriffsmatrix und reale Aufbewahrungsparameter sind nicht im Code abgebildet.

## 2.4 Freigabegate

Für ausschließlich lokalen Einoperatorbetrieb: API-Key setzen, bind auf `127.0.0.1`, NTFS-ACL auf Runtime-/Exportroot, Secrets außerhalb Git, täglicher retention dry-run. Für Netzwerk-/SaaS-Betrieb: erst S-01 bis S-07 als eigenes Security-Gate mit Threat Model, automatisierten AuthZ-Tests und unabhängiger Security-Prüfung schließen.
