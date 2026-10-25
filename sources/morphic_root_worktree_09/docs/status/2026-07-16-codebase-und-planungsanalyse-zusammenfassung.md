# Morphic Engine V1: Codebase-, Planungs- und Wiederaufnahmezusammenfassung

Stand: 2026-07-16
Arbeitsort: `C:\morphic_v1\.worktrees\operator-workbench-phase1`
Branch: `operator-workbench-phase1`
HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
Aktueller Arbeitsblock: `F5-B/v10`
Freigabestatus: **NO-GO**

> Fortschreibung 2026-07-16: Gate A0, Gate M1, Gate M2 und Gate M3 sind technisch geschlossen und reviewt. Der naechste verbindliche Implementierungsblock ist Gate B1, die gemeinsame durable Backup-Publikation. Details: `docs/status/2026-07-16-feedback-f-F5-B-v10-A0-parent-identity.md`, `docs/status/2026-07-16-feedback-f-F5-B-v10-M1-v7-known-answer.md`, `docs/status/2026-07-16-feedback-f-F5-B-v10-M2-v7-to-v8-migration.md` und `docs/status/2026-07-16-feedback-f-F5-B-v10-M3-v7-backup-migration.md`. F5-B bleibt insgesamt `NO-GO`.

## 1. Zweck dieses Dokuments

Dieses Dokument fasst den aktuellen Projektstand in einer gut verstaendlichen, aber technisch praezisen Form zusammen. Es verbindet:

- den live verifizierten Repositoryzustand;
- die aktuelle Architektur und die produktiven Ausfuehrungspfade;
- den bisherigen Umsetzungsfortschritt;
- die aktiven Hermes-Gates;
- die bereits geschlossenen und noch offenen F5-B/v10-Sicherheitsbloecke;
- die relevanten Risiken des uncommitteten Working Trees;
- die verbindliche Reihenfolge fuer die Wiederaufnahme.

Dieses Dokument ist eine erklaerende Zusammenfassung. Der normative Wiederaufnahmepunkt bleibt das hashgebundene Entwicklerpaket unter `docs/developer-current-state-2026-07-16/` zusammen mit dem aktiven Hermes-Plan `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md`.

## 2. Executive Summary

Morphic Engine V1 ist ein grosser lokaler Python-/FastAPI-/CLI-Operator-Prototyp fuer Analyse-, Resonanz-, Reporting- und Harmonisierungsablaeufe. Die Codebase ist modularisiert, besitzt eine umfangreiche Testlandschaft und folgt bei sicherheitskritischen Dateiauthorities einer aussergewoehnlich konservativen Gate-, Freeze- und Reviewstrategie.

Der aktuelle Implementierungsstand ist deutlich weiter als der letzte Commit. Der Commit `619a1f5` markiert lediglich Feedbackpunkt d) als abgeschlossen und nennt e) als naechsten Schritt. Im Working Tree sind Feedback e), grosse Teile von Feedback f), der Admin Catalog, Source-Pipeline-Hardening, Gruppenanalyse, Compliancebausteine und zahlreiche Tests bereits umgesetzt, aber noch nicht committet.

Der massgebliche aktuelle Stand lautet:

- F1 bis F4 sind gateweise `GO`.
- F5-A ist formal abgeschlossen.
- F5-B bleibt `NO-GO`.
- Freeze v9 ist `SUPERSEDED / REQUEST CHANGES / NO-GO`.
- v10 befindet sich mitten in der Implementierung.
- Zwei v10-Mikrobloecke sind substanziell geschlossen: externe HMAC-Authentisierung der Draft-Validation-Attestation und Windows-handlebasierte Registry-Publikation.
- Parentbindung fuer Stage, Index, Ledger, Rollback-Snapshot und Stage-Key ist mit Gate A0 technisch geschlossen.
- Die atomare Schema-v7->v8-Migration und die v7-Backupmigration sind mit Gate M2 und M3 technisch geschlossen; durable Backup-/Restore-Publikation, POSIX-Entscheidung und produktive Validation-Key-Komposition fehlen weiter.
- Es gibt noch keinen Freeze v10, keine v10-Abschlussreviews und keine aktuelle v10-Vollregression.

Der exakte Wiederaufnahmepunkt ist daher:

> Gate A0, M1, M2 und M3 sind geschlossen. Als Naechstes Gate B1 ausfuehren: eine gemeinsame durable FS-Authority-Boundary fuer Backup-Erzeugung und Restore-Publikation mit Handle-gebundenen SQLite-Temps, Completion-Record, Parent-/Temp-Swap- und Flush-Fault-Vertraegen schaffen.

## 3. Verbindliche Dokumenthierarchie

Die vorhandenen Dokumente haben unterschiedliche Aktualitaet und Autoritaet.

### 3.1 Primaerer Wiederaufnahmepunkt

Massgeblich ist:

- `docs/developer-current-state-2026-07-16/README.md`
- `docs/developer-current-state-2026-07-16/01_TIEFENANALYSE_AKTUELLER_STAND.md`
- `docs/developer-current-state-2026-07-16/02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md`
- `docs/developer-current-state-2026-07-16/03_VERIFIKATION.md`
- `docs/developer-current-state-2026-07-16/SOURCE_MANIFEST.sha256`

Das Paket bezeichnet sich ausdruecklich als verbindlichen Diskussions- und Wiederaufnahmepunkt vor der Fortsetzung von F5-B/v10.

### 3.2 Aktiver Hermes-Gesamtplan

Der normative Scope-, Gate- und Invariantenplan ist:

`.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md`

Der Plan bleibt fuer F1 bis F8 und die globalen Sicherheitsgrenzen massgeblich. Seine Statuspassagen am Ende von F5 sind jedoch veraltet: Sie beschreiben noch die Vorbereitung von Freeze v9, obwohl Freeze v9 inzwischen superseded ist und v10 laeuft.

### 3.3 Historische Evidenz

Freeze-v9- und Reviewdokumente bleiben verbindliche historische Befunde fuer die damaligen Root Causes. Sie sind keine aktuelle Freigabe und duerfen nicht als v10-Abschlussnachweis verwendet werden.

Der juengste projektlokale Hermes-Handoff vom 15.07.2026 endet noch bei Freeze v6. Er wurde durch Freeze v7 bis v9 und die anschliessende v10-Arbeit ueberholt.

### 3.4 Veraltete Statusquellen

`PROJECT_MEMORY/00_CURRENT_STATE.md`, `CLAUDE.md`, `PROJECT_STATE.md` und mehrere aeltere Kurzstatusdokumente sind fuer historischen Kontext nuetzlich, enthalten aber teilweise veraltete F5-A-/F5-B- oder UI-Aussagen. Bei Widerspruechen haben Livecode, neue Verifikation, das Entwicklerpaket vom 16.07.2026 und der aktive Hermes-Plan Vorrang.

## 4. Live verifizierter Repositoryzustand

| Merkmal | Aktueller Wert |
|---|---|
| Worktree | `C:\morphic_v1\.worktrees\operator-workbench-phase1` |
| Branch | `operator-workbench-phase1` |
| HEAD | `619a1f5485a151816e32732929a6a823839ccb57` |
| Letzter Commit | `docs: mark feedback point d) Phase 5 complete, next up is point e)` |
| Modified tracked | 37 Dateien |
| Kompakte Statuszeilen | 353 |
| Kompakte untracked Eintraege | 316 |
| Vollstaendig expandierter Status | 64.041 Zeilen |
| Git-getrackte Dateien | 585 |
| Getrackte Python-Dateien | 290 |
| Differenz zu lokalem `master` | 21 Commits voraus, 4 Commits zurueck |
| Staged | keine Dateien |
| Registry SHA-256 | `6c93c5a1aab9b022bf22e3a8c8097b07bde2738efec3678645ffadf849e4a0b3` |
| Remedy-DB SHA-256 | `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0` |
| Produktiver Stage-Key | nicht vorhanden |
| `MORPHIC_ADMIN_STAGE_KEY` | nicht gesetzt |
| Port 8000 | frei |
| Port 8090 | Radi144 auf `127.0.0.1`, PID 3304 |
| `git diff --check` | Exit 0; nur bekannte LF->CRLF-Warnungen |

Die Authority-, Branch-, HEAD-, Port- und kompakten Statuswerte stimmen mit `docs/developer-current-state-2026-07-16/03_VERIFIKATION.md` beziehungsweise der unmittelbar davor ausgefuehrten Tiefenanalyse ueberein. Die vollstaendige Statuspopulation liegt um exakt eine Zeile hoeher, weil das vorliegende Markdown als neue untracked Datei hinzugekommen ist. Der dokumentierte Pausepunkt bleibt dadurch unveraendert belastbar.

## 5. Betriebs- und Sicherheitsmodell

Morphic Engine V1 ist aktuell fuer einen einzelnen lokalen Operator vorgesehen. Es ist nicht fuer Mehrbenutzerbetrieb, LAN, Internet oder SaaS freigegeben.

Aktive Schutzgrenzen:

- kontrollierte Startwege binden nur an Loopback;
- `web_server.py` weist Nicht-Loopback-Hosts fail-closed ab;
- `Run-WebUI.ps1` bindet fest an `127.0.0.1`;
- ein belegter Port wird nicht automatisch freigemacht;
- der optionale API-Key ist keine echte Mehrbenutzer- oder Tenant-Authentisierung;
- Operator, Workspace und Tenant sind lokale Namespace-/Kontextgrenzen, keine zentral authentisierten Claims;
- Adminmutationen bleiben bis zum separaten F6-Auth-Gate gesperrt;
- Catalog-Drafts besitzen keine automatische Scan- oder Runtimewirkung;
- Onlinezugriffe sind bis F7 verboten.

## 6. Architekturuebersicht

```text
PowerShell-/CMD-Launcher
        |
FastAPI-Weboberflaeche und Typer-CLI
        |
Anwendungsservices und Job-Orchestrierung
        |
Profile, Resonanz, NLS, Gruppen und Harmonisierung
        |
Admin Catalog, Source Registry und Compliance
        |
SQLite-, JSON-, Stage-, Ledger- und Export-Authorities
```

### 6.1 Hauptbereiche

| Bereich | Verantwortung |
|---|---|
| `apps/web` | FastAPI-App, Operator Workbench, Scan-, Report-, Gruppen- und Harmonization-API |
| `apps/cli` | produktive Analyse-, Scan-, Source-, Export- und Privacy-Befehle |
| `services` | Analyse-, NLS-, Gruppen-, Remedy- und Harmonization-Fassaden |
| `core/profiles` | Profilkodierung, Gruppenvektoren und Member-Rate-Aufloesung |
| `core/resonance` | Resonanzberechnung |
| `core/nls` | NLS-Scoring und Datenbankzugriff |
| `core/harmonization` | Harmonisierungslogik und Sequenzplanung |
| `core/compliance` | OperatorContext, Privacy, Manifeste, DPAPI und Artifactplanung |
| `core/admin_catalog` | revisionssicherer lokaler Admin Catalog |
| `core/source_registry.py` | Source-Metadatenauthority und FS-Commitprimitive |
| `core/source_data_promotion.py` | Stage-, Index-, Ledger- und Draft-Import-Protokoll |
| `providers/hardware` | CPU-, HID-, TrueRNG-, GPU- und Netzwerk-Entropy |
| `tools` | Reporting, PDF, Interpretation, Remedy-, Synergy- und Trend-Ausgaben |

### 6.2 Packaging-Grenze

`pyproject.toml` inkludiert derzeit nur `apps*`, `core*`, `providers*`, `services*`, `infra*` und `data*`. Mehrere produktiv importierte Bereiche wie `tools`, `cli`, `monitoring`, Rootentrypoints und Konfigurationsmodule sind nicht vollstaendig als installierbares Package abgebildet.

Die Anwendung setzt deshalb praktisch weiterhin einen vollstaendigen Source-Checkout voraus. `pyproject.toml` und `requirements.txt` sind zudem nicht deckungsgleich. Diese Punkte sind reale Reproduzierbarkeitsrisiken, gehoeren aber nicht in den aktuellen P0/F5-B-v10-Scope.

## 7. Produktiver Scan- und Reportpfad

Der offizielle produktive Pfad lautet:

```text
Operator Workbench
-> POST /api/scan/jobs
-> build_phase1_scan_launcher()
-> LocalScanJobService
-> python -m apps.cli.main scan top3-scan
-> Screening- und Full-Analysis-Subprozesse
-> Profil-/Gruppen-/Resonanz-/NLS-Berechnung
-> JSON-/HTML-/PDF-/TXT-Exports
-> Reportkatalog
-> optionale Harmonisierung
```

Wichtige Implementierungsorte:

- Requestvertrag: `apps/web/contracts.py`
- Launcher: `apps/web/launcher.py`
- Webstart: `apps/web/main.py`
- Prozessmanagement: `apps/web/scan_jobs.py`
- Top-N-Orchestrierung: `apps/cli/commands/scan.py`
- Feldanalyse und Exporte: `apps/cli/commands/field.py`
- Artifactregistrierung: `tools/reporting_common.py`

Aktive Scanprozesse sind nur in-memory registriert. Logs liegen auf Disk, aber ein produktiver, nach Neustart rekonstruierbarer Web-Job-Index fehlt. `core/compliance/web_job_manifest.py` und `core/compliance/progress_events.py` sind vorhanden, aber ausdruecklich noch nicht in den produktiven Webruntimepfad integriert.

## 8. Operator Workbench

Die offizielle Workbench besteht aus elf Phasen:

| Phase | Funktion | Reifegrad |
|---:|---|---|
| 1 | Runtime und Workspace | operativ |
| 2 | Klient und Kontext | operativ; Gruppenpfad umfangreich |
| 3 | Fokus und Ziel | operativ |
| 4 | Analyseprofil | weitgehend operativ |
| 5 | Hardware und Realtime | operativ als Truth-/Readiness-Ansicht |
| 6 | Review und Freigabe | operativ |
| 7 | Analyselauf | realer Subprozesspfad |
| 8 | Ergebnisuebersicht | nur teilweise ausgebaut |
| 9 | technische Details | Run-Trace noch unvollstaendig |
| 10 | Berichtskatalog | funktional, aber Lifecycle-Luecken |
| 11 | Harmonisierung und Abschluss | Worker real, Bindung unvollstaendig |

Wesentliche offene Integrationspunkte:

- Phasen koennen frei angesprungen werden; es gibt kein vollstaendiges Unlockmodell.
- Pflichtfeld- und Consentvalidierung erfolgt erst bei Preview und Start.
- Die Ergebnisansicht rendert noch nicht die vollstaendige Ergebnismatrix.
- Der Run-Trace wird beim Start erzeugt, nach Abschluss aber nicht mit finalen Ergebnissen, Artefakten und Hashes angereichert.
- Die 12-Schritt-Timeline beruht auf heuristischen Logmarkern.
- Reportauswahl und Harmonization-Job sind nicht dauerhaft aneinander gebunden.
- `solfeggio_base` wird gespeichert, besitzt aber derzeit keine nachgewiesene Modulationswirkung.
- Angezeigte `duration_minutes` und reale Worker-Laufzeit koennen voneinander abweichen.

### 8.1 Bekannter Export-/Report-Integrationsbruch

Der Weblauncher uebergibt explizit:

```text
--export C:\Benutzer_Archive_Start
```

Der Reportkatalog liest dagegen tenant-suffigierte Roots wie:

```text
C:\Benutzer_Archive_Start__<tenant_id>
```

Die CLI fuegt den Tenant-Suffix nur beim internen Defaultpfad hinzu, nicht bei explizitem `--export`. Dadurch koennen ein Webscan und der anschliessende Reportkatalog unterschiedliche Verzeichnisse verwenden.

Das ist ein realer End-to-End-Befund, aber kein Bestandteil des aktuellen F5-B/v10-P0-Sicherheitsblocks. Er muss spaeter in einem separaten, testgebundenen Integrationsgate geschlossen werden.

## 9. Gruppenanalyse und Feedback e)

Feedback e) ist nicht nur als UI umgesetzt, sondern besitzt einen echten, default-off und consentgebundenen produktiven Pfad:

```text
geschuetzte Client-Identitaet
-> versionierter und zeitlich begrenzter Consent
-> DPAPI-geschuetzter Gruppendraft
-> serverseitige Memberaufloesung
-> deterministischer Gruppenvektor
-> Authorization-Objekt
-> kurzlebiger One-Time-DPAPI-Handle
-> Child-Prozess
-> explizites GroupAnalysisOptIn
-> kontrollierter Blend in AnalysisService
```

Produktive Wirkung erfordert gleichzeitig:

- `MORPHIC_GROUP_ANALYSIS_ENABLED=true`;
- explizite, positive Strength;
- einen ausgewaehlten Gruppendraft;
- mindestens zwei eindeutige Teilnehmer;
- gueltige Teilnehmer-Consents;
- passende Operator-/Workspace-/Tenant-Bindung;
- Mitgliedschaft des Scan-Subjekts in der Gruppe.

Zentrale Module:

- `apps/web/group_analysis_runtime.py`
- `apps/web/group_analysis_activation.py`
- `apps/web/group_consents.py`
- `apps/web/group_drafts.py`
- `core/compliance/group_activation_handle_store.py`
- `core/compliance/local_client_identity_store.py`
- `core/profiles/group_vector.py`
- `services/analysis_service.py`

Offene Sekundaerthemen:

- Draftaenderungen invalidieren bereits ausgestellte Handles nicht;
- Policyaenderungen invalidieren bestehende Handles nicht;
- Handle-Consumption ist nur prozesslokal gelockt;
- einzelne Docstrings und Safe-Summaries beschreiben noch den aelteren, nicht produktiven Stand;
- Geo bleibt ein eigener, ausdruecklich nicht freigegebener Zweig.

## 10. Fortschritt der bisherigen Nutzeranforderungen

| Punkt | Inhalt | Status |
|---|---|---|
| b | Scoreanzeige auf maximal fuenf Nachkommastellen | abgeschlossen, Commit `abe8739` |
| c | formatierte PDF-Berichte statt Rohtext | abgeschlossen, Commit `d4701e7` |
| d | tenantbasierte Exportpfadisolation | abgeschlossen, Commit `713b66a` |
| e | Klienten-/Gruppenkontext nach Radi144-Vektoren | umgesetzt und gateweise GO; Geo ausgeschlossen |
| f | Adminverwaltung und Repositories | F1-F4 GO, F5-A abgeschlossen, F5-B/v10 NO-GO |
| a | einheitliches Design aller Berichte | offen und noch nicht terminiert |

Radiquant4-Alignment und der Radi144-UI/UX-Konsolidierungsplan mit neun Tasks sind abgeschlossen.

## 11. Admin Catalog

Der neue Admin Catalog unter `core/admin_catalog/` modelliert:

- Profile;
- Gruppen;
- Remedies;
- Pathogene;
- Multiplexe;
- Terminologie;
- typisierte Relationen.

Die Architektur bietet:

- `CatalogContext` mit Operator, Workspace, Tenant und Scope;
- versionierte mutable Drafts;
- immutable Revisionen;
- Validation-Attestations;
- Source-Import-Receipts;
- terminale Tombstones;
- einen aktiven Revisionspointer pro Kontext;
- atomare Aktivierung und Rollback;
- hashverkettete Auditereignisse;
- Cross-Reference-Validierung;
- read-only Legacy-Inventarisierung;
- einen read-only Runtime-Schattenadapter.

Der Admin Catalog ist noch nicht scanwirksam. Der Runtime-Adapter kann Catalog und Legacy vergleichen, produktiv bleiben aber die Legacyauthorities aktiv. Eine produktive Runtimeumschaltung ist erst fuer F8 vorgesehen.

## 12. Gatefortschritt F1 bis F5

### 12.1 F1 bis F4

| Gate | Inhalt | Status |
|---|---|---|
| F1 | Contracts, SQLite Store und Cross-Reference-Validierung | GO |
| F2 | Service, Pfadpolicy, Backup und Auditintegritaetsstufen | GO |
| F3 | Profilverwaltung und Runtime-Schattenadapter | GO |
| F4 | Remedies, Pathogene, Multiplexe und Legacy-Launcher | GO |

Diese Gates erlauben weiterhin keine automatische Catalog-, Publish-, Activate-, Netzwerk- oder Enginewirkung.

### 12.2 F5-Makrobloecke

| Makroblock | Inhalt | Status |
|---|---|---|
| F5-A | Source Policy, Registry-/Audit-/Rollback-Hardening, Batchhash und Replay-Schutz | formal abgeschlossen |
| F5-B | Source-Normalisierung und kontrollierte Catalog-Draft-Uebernahme | v10 in Arbeit, NO-GO |
| F5-C | verbleibende Pipelinehaertung und F5-Gesamtgate | ausstehend |

## 13. Bereits geschlossene F5-B/v10-Mikrobloecke

### 13.1 Extern authentisierte Validation-Attestation

Umgesetzt sind:

- ein eigener `ValidationKeyProvider`;
- HMAC-Bindung von Kontext, Draft, Version, Payload, Policy, Schema, Zeitpunkt, Authority und Key-ID;
- kein unsicherer Default-Key;
- keine Ableitung aus dem Stage-Key;
- fail-closed Validate und Publish ohne Provider;
- Schutz gegen direkte gefaelschte SQLite-Attestation-Inserts.

Relevante Dateien:

- `core/admin_catalog/validation_attestation.py`
- `core/admin_catalog/store.py`
- `tests/test_f5b_review_findings.py`

Die produktive Composition ist noch offen: `apps/cli/commands/sources.py` konstruiert den `CatalogStore` weiterhin ohne Validation-Key-Provider.

### 13.2 Windows-handlebasierte Authority-Publikation

Umgesetzt sind:

- Bindung der Parent-Identitaet beim vertrauenswuerdigen Read;
- ein gehaltener Windows-Parent-Handle waehrend des Commits;
- Bindung der Tempdatei an einen Descriptor;
- Publication ueber `SetFileInformationByHandle`;
- Abwehr von Tempname-Swap;
- Abwehr von Parent-Substitution fuer `SourceRegistry.save()`;
- abschliessende Identitaets- und Byteattestierung.

Relevante Bereiche:

- `core/source_registry.py:660-705`
- `core/source_registry.py:983-1074`
- `core/source_registry.py:1077-1276`
- `tests/test_source_registry_atomicity.py`

Diese Arbeit ist gezielt gruen, aber noch nicht in einem positiven Freeze v10 unabhaengig abgenommen.

## 14. Offene F5-B/v10-Blocker

### 14.1 Gate A0: Parentbindung aller Authorities - geschlossen

Die generischen Helper:

- `_atomic_replace_json()`;
- `_atomic_publish_bytes()`

oeffnen den aktuell sichtbaren Parent selbst und akzeptieren noch keine vom vorgelagerten Authority-Read gebundene `expected_identity`.

Betroffen sind insbesondere:

- Stage-Artefakte;
- Stage-Index;
- Consistency Ledger;
- Rollback-Snapshot;
- Stage-Key.

Die Parent-Identitaet wird jetzt verpflichtend bis in die gemeinsame Commitprimitive transportiert. Source Data Stage, Source Manifest Stage, beide Stage-Index-Schreibfamilien, Ledger, Rollback Snapshot und Stage-Key besitzen reale Parent-Substitution-Vertraege. Der technische Abschluss ist in `docs/status/2026-07-16-feedback-f-F5-B-v10-A0-parent-identity.md` dokumentiert.

### 14.2 Gate M1: v7-Known-Answer-Fixtures - geschlossen

Geschlossen sind:

- eine historisch korrekte v7-Schemarekonstruktion;
- eine synthetische v7-Datenbank mit Draft, Revision, Activation, Audit und Source-Receipt;
- ein gebundener exakter v7-Fingerprint;
- RED-Vertraege fuer kontrollierte Ablehnung, unbekannte Fingerprints und synthetische Preview-v8-Formen.

Der technische Abschluss ist in `docs/status/2026-07-16-feedback-f-F5-B-v10-M1-v7-known-answer.md` dokumentiert.

### 14.3 Gate M2: atomare v7->v8-Migration

Es fehlen:

- eine dedizierte Migration-API;
- `BEGIN IMMEDIATE` und v7-Attestation auf derselben Connection;
- Anlage der Attestationtabellen und Trigger;
- Invalidierung alter Validierungsmarker;
- explizite Neuvalidierung mit externer Authority;
- Foreign-Key-, Integrity- und exakte v8-Fingerprint-Pruefung;
- Fault-Injection vor und nach DDL sowie vor Commit;
- Nachweis, dass nie ein Mischschema entsteht.

### 14.4 Gate M3: v7-Backupmigration

Die aktuelle Backupimplementierung akzeptiert ausschliesslich Schema 8. Ein valides v7-Backup muss spaeter in einen temporaeren Snapshot restored, dort migriert und nur als neues v8-Ziel publiziert werden. Das Originalbackup muss bytegleich und immutable bleiben.

### 14.5 Gate B1: durable Backup-/Restore-Publikation

Aktuell:

- Backup publiziert Datenbank und Manifest getrennt mit `os.replace`;
- es gibt keinen finalen Completion-Record;
- Restore verwendet eine eigene `os.rename`-/`os.link`-Primitive;
- Backup und Restore benutzen nicht dieselbe handlegebundene Authority-Boundary wie Registry und Stage.

Erforderlich ist ein Bundleprotokoll, bei dem ausschliesslich der final durable Completion-Record ein Backup als konsumierbar autorisiert.

### 14.6 Gate P1: POSIX-Entscheidung

Auf Windows wird der gehaltene Temp-Descriptor publiziert. Auf POSIX wird weiterhin der Tempname ueber `os.replace` oder `os.link` verwendet.

Vor Freeze v10 ist eine klare Entscheidung erforderlich:

- sichere inodegebundene POSIX-Publikation; oder
- expliziter fail-closed Plattformvertrag fuer die betroffenen mutierenden Pfade.

### 14.7 Gate C1: produktive Composition Root

Es fehlen:

- eigene Validation-Key-Konfiguration;
- Trennung von Validation-, Stage- und Audit-Key;
- Authority-ID, Key-ID und Rotation;
- explizite Providerinjektion in CLI/API;
- fail-closed Verhalten bei fehlendem oder unbekanntem Key;
- betriebliche Regeln, die Secrets aus DB, Backup, Manifest, Logs und Dokumentation fernhalten.

### 14.8 Formale Freigabe

Es fehlen:

- aktuelle v10-Nachbarmatrizen;
- v10-Vollsuite;
- Freeze v10 mit Einzeldateihashes;
- unmittelbare Freeze-Rueckverifikation;
- zwei unabhaengige technische Reviews;
- separater Dokumentfreeze;
- zwei dokumentgebundene Reviews;
- externe Post-State-ShadowCopy;
- finale GO-Entscheidung.

## 15. Source-Pipeline: aktueller Charakter

Der beabsichtigte sichere Pfad lautet:

```text
Source-Daten
-> Source-/License-/Scope-Pruefung
-> immutables Batchartefakt
-> HMAC-signierter Stage-Index
-> Stage-/Registry-Locks
-> typisierte Catalog-Normalisierung
-> vollstaendige Snapshotvalidierung
-> Stage-Reservierung
-> atomarer SQLite-Draft plus Receipt
-> Stage-Commit
-> authentisierte Draftvalidierung
-> Source-Revalidierung bei Publish
-> separate explizite Aktivierung
```

Wichtige Grenzen:

- `data-import-draft` darf nur in einen Catalog-Draft schreiben;
- es erfolgt kein automatisches Publish oder Activate;
- `data-record-consistency` ist ein reiner Ledgerpfad;
- `data-promote` ist nur ein sichtbar deprecateter Alias und keine fachliche Promotion;
- Source-Adapter duerfen spaeter nur in Quarantaene oder Drafts liefern;
- Source-Aktivierung, Fetch, Validate, Publish und Runtime-Aktivierung bleiben getrennte Aktionen.

Aktuelle operative Einschraenkungen:

- die bestehende produktive Registry besitzt die Legacyform und ist fuer Mutationen read-only;
- ein Registry-Migrationsbefehl fehlt;
- neue Sources starten zwingend `experimental_unverified/reference_only`;
- `reference_only` ist nicht importberechtigt;
- eine separate sichere Aufwertungsstrecke fehlt noch;
- mehrere konfigurierte Source-Scopes sind plural, waehrend Promotion-Datentypen singular sind.

Diese Grenzen duerfen nicht durch permissive Sonderfaelle umgangen werden.

## 16. Persistenz- und Authority-Inventar

| Authority | Aktueller Zustand |
|---|---|
| Source Registry | revisioniert, hashgebunden, Windows-handlegehaertet |
| Source Manifest Stage | immutable JSON-Artefakte |
| Source Data Stage | immutable Batchdateien plus HMAC-Index |
| Stage-Key | lokale Datei, produktiv derzeit nicht vorhanden |
| Consistency Ledger | lokale kanonische Hashkette |
| Admin Catalog | kontextgebundenes SQLite mit immutable Revisionen |
| Catalog Backup | Hashmanifest, aber noch kein Completion-Protokoll |
| Runtime Manifest | JSON, Cleartext, kein Interprozesslock |
| Workbench State | lokale JSON-Dateien, nur In-Process-Lock |
| Scan Jobs | Prozessobjekte in-memory, Logs auf Disk |
| Client identities | DPAPI-geschuetzt |
| Group drafts | DPAPI-geschuetzt unter OS-Temp |
| Group handles | DPAPI, kurzlebig, single-use |
| Harmonization Jobs | globale JSON-/JSONL-Dateien |
| Reports | Filesystemarchive, teilweise klare PII-Verzeichnisnamen |
| Run Manifest | implementiert, noch nicht produktiv verdrahtet |
| Web Job Manifest | implementiert, noch nicht produktiv verdrahtet |
| Parallel Artifact Repository | derzeit Plan-/Pfadadapter, keine vollstaendige Schreibintegration |

## 17. Test- und Verifikationsstand

### 17.1 Aktuelle gezielte v10-Nachweise

| Matrix | Ergebnis |
|---|---:|
| F5-B plus Admin Service/Remedy/Profile | 134 passed |
| Source Registry/Atomicity/Promotion/Draft/CLI | 109 passed |
| Atomicity plus Promotion | 68 passed |
| Stage-Key-Concurrency | 2 passed |
| Ruff im aktuellen Scope | PASS |

### 17.2 Historische Freeze-v9-Nachweise

| Matrix | Ergebnis |
|---|---:|
| Vollsuite | 1002 passed, 8 skipped, 14 failed |
| Fresh-Process HTTP | 13/13 passed |
| Top-5 | 1 passed |

Die 14 Vollsuitefehler waren historisch baseline-identisch und betrafen ein datumsabhaengiges Consent-Fixture sowie In-Process-Rate-Limiter-Faelle. Diese Ergebnisse sind keine v10-Abschlussevidenz, weil nach Freeze v9 produktive Scopedateien veraendert wurden.

Im Rahmen der aktuellen Bestandsanalyse wurden keine Tests oder Builds gestartet. Read-only erneut verifiziert wurden Branch, HEAD, Statuspopulation, Authority-Hashes, Stage-Key-Zustand, Ports und `git diff --check`.

## 18. Working-Tree- und Integrationsrisiko

Der Working Tree ist umfangreich und darf nicht pauschal bereinigt, gestaged oder committet werden.

Wichtige Fakten:

- 37 getrackte Dateien sind modified;
- 64.004 Dateien sind vollstaendig expandiert untracked, einschliesslich dieses Dokuments;
- rund 63.750 Dateien davon liegen in 195 `Benutzer_Archive__ws-*`-Roots;
- das gesamte neue `core/admin_catalog/` ist untracked;
- neue Gruppen-, Compliance- und Harmonization-Module sind untracked;
- 86 Testmodule sind untracked;
- 122 Dokumentdateien sind untracked;
- modified tracked Dateien importieren untracked Module.

Ein Commit nur der getrackten Aenderungen waere unvollstaendig und koennte Importfehler erzeugen. Die Archivroots koennen produktive oder operatorbezogene Daten enthalten und duerfen nicht per Wildcard geloescht, verschoben oder gestaged werden.

Repositoryhygiene ist als eigener Professionalisierungsblock P1 vorgesehen und darf nicht in den aktuellen F5-B/v10-Sicherheitsscope gezogen werden.

## 19. Weitere bekannte Risiken ausserhalb des aktuellen P0-Scopes

- Web-Export- und Reportroot stimmen nicht zuverlaessig ueberein.
- Run-/Webjob-Manifeste und strukturierte Progress Events sind noch nicht verdrahtet.
- Scan-Jobs sind nach einem Serverneustart nicht rekonstruierbar.
- Harmonization-Jobs besitzen keine vollstaendige Tenant-/Ownerisolation.
- mehrere JSON-Stores sind nicht multiprocess-sicher.
- Privacy-Erasure deckt Workbench, Joblogs, Harmonization, Browserdaten, Backups und unregistrierte Exporte nicht vollstaendig ab.
- registrierte Artifact-Pfade sind nicht ueberall auf sichere Exportroots beschraenkt.
- API-Key-Pruefung ist optional und zwischen Endpunkten uneinheitlich.
- `web_app.py` und `/ui/` bilden parallele veraltete Weboberflaechen.
- die Packagingkonfiguration bildet nicht alle Runtimeimports ab.
- `pyproject.toml` und `requirements.txt` sind nicht deckungsgleich.
- eine getrackte CI-Workflowdatei fehlt.
- dokumentierte Python-Versionen sind nicht einheitlich.

Diese Punkte sind wichtig, sollen aber den P0-Sicherheitsabschluss nicht verwischen.

## 20. Exakte Wiederaufnahmefolge

### 20.1 Preflight

1. Das Entwicklerpaket und den aktiven Hermes-Plan erneut lesen.
2. Branch und HEAD pruefen.
3. Kompakten und vollstaendigen Status erfassen.
4. Registry- und Remedy-DB-Hash erneut pruefen.
5. Fehlenden produktiven Stage-Key und fehlende Stage-Key-Umgebungsvariable bestaetigen.
6. Ports 8000 und 8090 pruefen.
7. Radi144 auf Port 8090 nicht veraendern.

### 20.2 Gate A0: Parentbindung - abgeschlossen

1. RED fuer Stage-Parent-Substitution schreiben.
2. RED fuer Stage-Index-Parent-Substitution schreiben.
3. RED fuer Ledger-Parent-Substitution schreiben.
4. RED fuer Rollback-Snapshot-Parent-Substitution schreiben.
5. RED fuer Stage-Key-Parent-Substitution schreiben.
6. In jedem Test belegen, dass der Swap nach Trusted Read oder Lock tatsaechlich ausgeloest wurde.
7. Fail-closed und Nullmutation vor Zielmutation nachweisen.
8. Die vorher gebundene Parent-Identitaet verpflichtend in `_atomic_replace_json()` und `_atomic_publish_bytes()` transportieren.
9. Registry-, Stage- und Key-Lockreihenfolge unveraendert und deadlockfrei halten.
10. Vollstaendige Source-/Registry-/Promotion-/CLI-Nachbarmatrix ausfuehren.

### 20.3 Migration und Backup

1. Historisch korrektes v7-Schema rekonstruieren.
2. v7-Known-Answer-Datenbank und Backupfixture erzeugen.
3. Kontrollierte heutige Ablehnung als RED nachweisen.
4. Atomare v7->v8-Migration mit `BEGIN IMMEDIATE` implementieren.
5. Alte Draftvalidierungen invalidieren und Neuvalidierung erzwingen.
6. Fault-Injection fuer DDL- und Commitgrenzen ausfuehren.
7. v7-Backup nur ueber einen temporaeren Snapshot migrieren.
8. Originalbackup bytegleich erhalten.
9. Backup/Restore auf die gemeinsame Authority-Boundary umstellen.
10. DB, Manifest und Completion-Record als durables Bundle publizieren.

### 20.4 Plattform und Composition

1. POSIX sicher inodegebunden implementieren oder explizit fail-closed schalten.
2. separaten Validation-Key-Provider konfigurieren.
3. Validation-, Audit- und Stage-Key strikt trennen.
4. Provider explizit in CLI/API injizieren.
5. Missing oder unknown Key ohne DB-/Filesystemmutation ablehnen.

### 20.5 Verifikation und Freeze

1. Neue RED-/GREEN-Suite ausfuehren.
2. `tests/test_f5b_review_findings.py` ausfuehren.
3. Admin Store/Service/Backup/Profile/Remedy ausfuehren.
4. Source Registry/Atomicity/Promotion/Draft/CLI ausfuehren.
5. Ruff, Compile und `git diff --check` ausfuehren.
6. Vollsuite in ein neues unveraendertes Log schreiben.
7. Die 14 historischen Baselinefaelle frisch und isoliert vergleichen.
8. Fresh-Process HTTP 13/13 ausfuehren.
9. Top-5-Smoke ausfuehren.
10. Authority-, Key-, Port-, Branch-, HEAD- und Statusnachweise erfassen.
11. Freeze v10 mit SHA-256 je Scopedatei erzeugen.
12. Freeze und Manifest unmittelbar rueckverifizieren.
13. Zwei unabhaengige technische Reviews auf exakt denselben Freeze-Hash binden.
14. Bei jedem P0-P3 Freeze superseden und neue RED->GREEN-Runde beginnen.
15. Erst bei zwei technischen APPROVE den Dokumentfreeze erstellen.
16. Zwei dokumentgebundene Reviews durchfuehren.
17. Erst danach externe Post-State-ShadowCopy erzeugen und vollstaendig rueckverifizieren.
18. Nur danach F5-B auf GO setzen.

## 21. Unveraenderliche Schranken

- Radi144 auf `127.0.0.1:8090` nicht veraendern.
- `config/source_repositories.json` nur read-only pruefen.
- `data/remedies.db` nur read-only pruefen.
- keinen produktiven Stage-Key erzeugen.
- kein produktives Backup vor den vorgeschriebenen APPROVE-Gates erzeugen.
- keine Post-State-ShadowCopy vor den vorgeschriebenen APPROVE-Gates erzeugen.
- die HMAC-Attestation nicht neu implementieren.
- den Registry-spezifischen Windows-Handle-Fix nicht wiederholen.
- keine Archive pauschal loeschen, verschieben oder stagen.
- keine CI-, Packaging-, Web-UX- oder Architekturmodernisierung in P0 ziehen.
- F6 Admin-API/UI nicht vorziehen.
- F8 Runtimewirkung nicht vorziehen.
- Freeze-v9-Werte nicht als v10-Abschlussevidenz verwenden.
- kein Commit, Staging oder Push ohne ausdrueckliche Benutzerfreigabe.

## 22. Roadmap nach F5-B/v10

| Phase | Ziel | Exit-Kriterium |
|---|---|---|
| P0 | F5-B/v10 sicher schliessen | zwei technische und zwei Dokument-APPROVE, danach verifizierte ShadowCopy |
| P1 | Test- und Worktree-Hygiene | keine Repositoryartefakte aus Tests, Vollsuite ohne Fehler |
| P2 | reproduzierbare Toolchain und CI | Lockfile, Windows-CI und saubere Neuinstallation |
| P3 | Authority-/Persistence-Kern vereinheitlichen | Registry, Stage und Backup nutzen einen geprueften Contract |
| P4 | Architektur und Entry Points konsolidieren | aktive Entry Points und Modulownership eindeutig |
| P5 | Admin Composition, Auth, API und UI | fail-closed Adminbetrieb und Browser-/API-Akzeptanz |
| P6 | Runtime-Aktivierung | atomare Catalogwirkung ohne stillen Legacyfallback |
| P7 | Release und Betrieb | reproduzierbares Release, Runbooks und Recovery Drill |
| P8 | Innovation und Performance | messbarer Nutzen ohne Default-Drift |

## 23. Offene spaetere Entscheidungen

1. Soll POSIX in v10 vollstaendig sicher unterstuetzt oder fuer kritische Mutationen zunaechst fail-closed werden?
2. Soll v7-Backupmigration automatisch oder nur ueber einen expliziten Operatorbefehl erfolgen? Die bestehende Empfehlung lautet: expliziter Befehl.
3. Welche `Benutzer_Archive__ws-*`-Roots sind produktiv/operatorbezogen und welche rein synthetisch?
4. Soll CI lokal/selbstgehostet oder GitHub-basiert betrieben werden?
5. Welcher gemeinsame Composition Root soll langfristig CLI und Web konfigurieren?

Diese Entscheidungen blockieren den unmittelbaren Start von Gate A0 nicht, muessen aber vor ihren jeweiligen Folgegates verbindlich getroffen werden.

## 24. Abschliessende Einordnung

Morphic Engine V1 besitzt eine breite funktionale Basis, eine tiefe Testlandschaft und eine fuer lokale Dateiauthorities sehr anspruchsvolle Security-Governance. Der aktuelle Stand ist kein frueher Prototyp mehr, aber auch noch kein freigegebener professioneller Releasezustand.

Die zentrale Trennlinie lautet:

- funktional weit fortgeschritten;
- sicherheits- und governanceorientiert gut vorbereitet;
- im Working Tree umfangreich umgesetzt;
- formal und technisch fuer F5-B weiterhin `NO-GO`;
- noch kein positiver Freeze v10;
- noch keine produktive Admin-Catalog-Wirkung;
- noch keine Freigabe fuer Onlineadapter oder Mehrbenutzerbetrieb.

Der naechste konkrete Codeblock ist eindeutig:

> **F5-B/v10, Gate M2: atomare v7->v8-Migration mit vollstaendigen Fault-Injection-Vertraegen, ohne Mischschema und mit erzwungener Neuvalidierung.**
