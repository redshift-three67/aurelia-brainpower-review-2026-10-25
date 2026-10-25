# Aktuelle Planung und exakter Pausepunkt

## 1. Pauseentscheidung

Auf ausdrücklichen Benutzerwunsch wird die Implementierung vor dem Schema-/Backup-Block pausiert. Es werden in diesem Dokumentationsschritt keine produktiven Authorities, Runtimepfade, Keys, Backups oder ShadowCopies verändert.

**Exakter Wiederaufnahmepunkt:**

> F5-B/v10, Arbeitsblock `v10-3` und `v10-4`: als Nächstes zuerst die noch partielle Parentbindung mit adversarialen Stage-/Index-/Ledger-/Snapshot-/Key-Parent-Swap-REDs schließen. Danach RED-Verträge für bestehende Schema-v7-Datenbanken, v7-Backups, unterbrochene Migration und Backup-/Restore-Publikation schreiben. Erst dann minimale fail-closed Fixes implementieren. Die bereits gezielt grüne HMAC- oder Registry-spezifische Windows-Handle-Arbeit nicht wiederholen.

## 2. Aktive Aufgaben

| ID | Status | Inhalt |
|---|---|---|
| v10-1 | abgeschlossen | v9-Reviews bytegleich bewahrt; Freeze v9 superseded |
| v10-2 | abgeschlossen | fünf v9-Root-Cause-Klassen dedupliziert |
| v10-3 | in Arbeit | RED-Verträge: Attestation und Parent/Temp erledigt; Migration/Backup offen |
| v10-4 | in Arbeit | HMAC und Windows Authority-Publish umgesetzt; Schema/Backup/POSIX offen |
| v10-5 | ausstehend | aktuelle Regression und operative Nachweise |
| v10-6 | ausstehend | Freeze v10, Rückverifikation, zwei unabhängige Reviews |

## 3. Bereits geschlossene v10-Mikroblöcke

### A. Extern authentisierte Validation-Attestation

- Eigener `ValidationKeyProvider`/HMAC-Vertrag.
- Kein Default-Key und keine Ableitung aus dem Stage-Key.
- Kanonische Bindung von Kontext, Draft, Version, Payload, Policy, Zeitpunkt, Authority und Key.
- Direkter forgebarer SQLite-Insert autorisiert keinen Publish ohne gültige externe HMAC.
- Fehlender Provider ist fail-closed.
- Aktueller gezielter Nachweis ist grün.

### B. Windows-handlebasierte Authority-Publikation

- Temp-Inode wird direkt über gehaltenen Handle publiziert.
- Tempname-Swap: tatsächliches RED vor Fix, danach fail-closed/nullmutierend.
- Parent-Substitution nach Trusted Read: tatsächliches RED vor Fix, danach fail-closed.
- Parent-Handle bleibt über Registry-Lock, Re-read und Commit gehalten.
- Stage-Key-Concurrency-Tests greifen an der neuen produktiven Boundary an.

## 4. Nächster Block: Migration und Backup/Restore

### Gate A0 – Parentidentität für alle Authority-Commits

1. Für Stage, Stage-Index, Ledger, Rollback-Snapshot und Stage-Key jeweils einen echten Parent-Substitution-RED-Vertrag ergänzen.
2. Der Test muss belegen, dass der Austausch nach vertrauenswürdigem Authority-Read/Lock tatsächlich ausgelöst wurde und vor Zielmutation fail-closed endet.
3. Die vom jeweiligen Read-/Lock-Kontext gebundene Parent-Identität verpflichtend bis in `_atomic_replace_json()`/`_atomic_publish_bytes()` transportieren; der Helper darf keine neue aktuelle Parent-Authority still selbst auswählen.
4. Registry-, Stage- und Key-Lockreihenfolge unverändert und deadlockfrei halten.
5. Danach vollständige Source-/Registry-/Promotion-/CLI-Nachbarmatrix ausführen.

Dieser Block ist vor Migration erforderlich, weil sonst Backup/Restore zwar eine neue Boundary erhalten könnte, die übrigen F5-B-Authorities aber weiterhin eine schwächere Parentbindung hätten.

### Gate M1 – v7-Known-Answer-Fixtures

1. Historisches ausführbares v7-Schema aus dem letzten validen v7-Scope rekonstruieren, nicht frei nachbauen.
2. Synthetische v7-DB mit Draft, Revision, Aktivierung, Audit und Source-Receipt erzeugen.
3. Exakten v7-Schemafingerprint als bekannte Eingangsidentität binden.
4. RED: heutiger `CatalogStore` muss den Bestand kontrolliert ablehnen; keine Teilmigration.
5. RED: unbekannter Fingerprint und Preview-v8 bleiben fail-closed.

### Gate M2 – Atomare v7→v8-Migration

1. Neue dedizierte Migration-API; kein stilles `CREATE TABLE IF NOT EXISTS` beim normalen Open.
2. `BEGIN IMMEDIATE`, v7-Vorbedingung und Schema-Attestation auf derselben Connection.
3. Attestation-Tabelle/-Trigger erstellen.
4. Alle bestehenden Draft-Validierungsmarker invalidieren; explizite Neuvalidierung mit externer Authority verlangen.
5. Foreign-Key- und Integrity-Check sowie exakter v8-Fingerprint vor Commit.
6. Fault injection vor/nach DDL und vor Commit: v7 bleibt vollständig nutzbar oder Migration ist vollständig v8; nie Mischschema.
7. Idempotenter zweiter Start auf vollständig migriertem v8; unbekannter Zustand bleibt gesperrt.

### Gate M3 – v7-Backup-Entscheidung

Empfohlen: v7-Backups werden nach vollständiger Manifest-/Hash-/Sidecarprüfung in einen temporären Snapshot restored, dort atomar migriert und erst als neues v8-Ziel publiziert. Das Originalbackup bleibt immutable. Direkte In-place-Manipulation eines Backup-Bundles ist verboten.

Tests:

- valides v7-Backup → neues v8-Ziel;
- manipuliertes Manifest/DB/Sidecar → nullmutierend;
- unbekannte Schemaidentität → fail-closed;
- Migration unterbrochen → kein Ziel;
- vorhandenes Ziel → kein Overwrite;
- altes Backup bleibt bytegleich.

### Gate B1 – gemeinsame durable Backup-Publikation

1. Gemeinsame FS-Authority-Abstraktion aus `source_registry.py` herauslösen oder bewusst intern wiederverwenden; keine zweite Sicherheitsimplementierung.
2. SQLite-Temp-Snapshot über gehaltenen Handle schreiben/prüfen.
3. DB, Manifest und finalen Completion-Record als Bundle-Protokoll publizieren.
4. Nur Completion-Record autorisiert ein konsumierbares Backup.
5. Restore publiziert das exakt geprüfte Temp-Inode über dieselbe Boundary.
6. Nach post-publish Fehlern keine unsichere pfadbasierte Löschung eines möglicherweise fremden Ziels.
7. Parent-/Temp-Swap, Concurrent Exists und Directory-Flush-Faults testen.

### Gate P1 – POSIX-Entscheidung

Vor v10-Freeze muss eine eindeutige Entscheidung fallen:

- sichere Implementierung mit Directory-FD plus handlegebundener Temp-Inode-Publikation (`O_TMPFILE`/`linkat(AT_EMPTY_PATH)` soweit nachweisbar), oder
- expliziter fail-closed Plattformvertrag für die betroffenen mutierenden Operationspfade.

Ein namenbasiertes `renameat/linkat` nach Temp-Swap-Prüfung reicht unter dem festgelegten nichtkooperierenden Namespace-Angreifermodell nicht.

### Gate C1 – Composition Root

- Eigene Validation-Key-Konfiguration, getrennt von Stage- und Audit-Key.
- Klare Authority-ID/Key-ID/Rotation.
- CLI/API-Konstruktion injiziert Provider explizit.
- Missing/unknown key verhindert Validate/Publish ohne DB-/Filesystem-Nebenwirkung.
- Secrets nie in DB, Backup, Manifest, Logs oder Dokumentation.

## 5. Regression nach Implementierung

Reihenfolge:

1. neue Migration-/Backup-/POSIX-RED-Suite;
2. `tests/test_f5b_review_findings.py`;
3. Admin Store/Service/Backup/Profile/Remedy;
4. Source Registry/Atomicity/Promotion/Draft/CLI;
5. Ruff, `py_compile`, `git diff --check`;
6. Vollsuite in neues unverändertes Log;
7. bekannte 14 Baselinefälle exakt vergleichen und frisch isoliert rerunnen;
8. Fresh-Process HTTP 13/13;
9. Top-5-Smoke;
10. Authority-, Key-, Port-, Branch-, HEAD- und Statusnachweise.

Historische v9-Werte dürfen nicht als v10-Nachweis verwendet werden.

## 6. Freeze- und Reviewfolge

1. Aktiven Plan auf realen v10-Abschlussstand aktualisieren.
2. Scope einschließlich aller transitiven Sicherheitsdateien, Tests, superseded Freezes und vollständigen Reviews festlegen.
3. Freeze v10 mit SHA-256 je Scope-Datei erzeugen.
4. Freeze und Manifest unmittelbar rückverifizieren.
5. Zwei unabhängige statische read-only Reviews an exakt denselben Freeze-Hash binden.
6. Bei irgendeinem P0–P3: Freeze superseden, Reports bytegleich bewahren, neue RED→GREEN-Runde.
7. Nur bei zwei `APPROVE`, Null Findings und Null Drift: technisches Gate schließen.
8. Danach separater Dokumentfreeze und zwei dokumentgebundene Reviews.
9. Erst danach externe Post-State-ShadowCopy mit verifiziertem Manifest.
10. Erst nach allen Schranken ist eine GO-Entscheidung zulässig.

## 7. Copy-paste-Wiederaufnahme

```text
Arbeite in C:\morphic_v1\.worktrees\operator-workbench-phase1 auf Branch operator-workbench-phase1. Lies zuerst CLAUDE.md, docs/developer-current-state-2026-07-16/README.md, 01_TIEFENANALYSE_AKTUELLER_STAND.md, 02_AKTUELLE_PLANUNG_UND_PAUSEPUNKT.md und den aktiven Plan .hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md. Verifiziere Branch, HEAD, kompakten Status-Fingerprint, produktive Authority-Hashes, fehlenden Stage-Key sowie Ports 8000/8090 neu. F5-B bleibt NO-GO. Setze exakt bei v10-3/v10-4 fort: zuerst Stage-/Index-/Ledger-/Snapshot-/Key-Parent-Swap-REDs und verpflichtenden Transport der vorher gebundenen Parent-Identität schließen; danach echte RED-Verträge für v7-DB, v7-Backup, unterbrochene Migration und Backup-/Restore-Publikation. Implementiere jeweils minimal fail-closed. Wiederhole nicht die bereits gezielt grüne HMAC- oder Registry-spezifische Windows-Handle-Arbeit. Keine produktiven Authorities, kein Backup und keine ShadowCopy vor den vorgeschriebenen APPROVE-Gates.
```
