# Feedback f – Admin Catalog und sichere Repositories – Implementierungsplan

> **Für Hermes:** Diesen Plan strikt gateweise, RED→GREEN und mit separatem Review je Gate ausführen. Kein Gate darf implizit Netzwerkzugriff oder produktive Katalogwirkung aktivieren.

**Ziel:** Eine lokale, revisionssichere Adminverwaltung für Profile, Gruppen, Remedies und Multiplexe mit explizitem Staging, Diff, Freigabe, Aktivierung und Rollback schaffen; Online-Repositories erst danach über feste, deaktivierte Adapter anbinden.

**Architektur:** Ein neuer SQLite-basierter Admin-Catalog speichert tenantgebundene Drafts, immutable Revisionen, Aktivierungspointer und hashverkettete Auditereignisse. Die heutige Engine bleibt zunächst unverändert und liest erst nach einem eigenen Gate über einen read-only Runtime-Adapter aus einer explizit aktivierten Revision. Source-Adapter liefern ausschließlich Daten in Quarantäne/Drafts und dürfen nie selbst publishen oder aktivieren.

**Technik:** Python 3.11, stdlib `sqlite3`, FastAPI, Vanilla JavaScript, pytest, vorhandener `OperatorContext`, bestehende Source-Registry als Metadatenbasis.

**Ist-Analyse:** `docs/status/2026-07-13-feedback-f-admin-repositories-ist-analyse.md`

---

## Globale Invarianten

1. Keine Änderung an `core/profile_sync`, `procedural_groups` oder `data/remedies.db`, bevor der Runtime-Adapter in einem separaten Gate abgenommen ist.
2. Kein Onlinezugriff in F1–F6.
3. Source aktivieren, Snapshot abrufen, Draft validieren, Revision freigeben und Revision aktivieren sind getrennte Aktionen.
4. Kein generischer URL-Fetch aus Manifestdaten.
5. Keine Klienten- oder Gruppenteilnehmerdaten im Admin-Catalog.
6. Jeder Schreibpfad bindet `operator_id`, `workspace_id`, `tenant_id` und Catalog-Scope.
7. Systemweite Änderungen bleiben gesperrt, solange kein echtes Admin-Auth-Gate existiert.
8. Drafts dürfen nie scanwirksam sein.
9. Aktivierung und Rollback erfolgen in einer SQLite-Transaktion.
10. Bestehende Repository-/Archiv-WIP-Dateien werden nicht verändert oder bereinigt.
11. Vor jedem Gate: externe hashverifizierte ShadowCopy der berührten vorhandenen Dateien.
12. Commit/Push/Staging nur nach ausdrücklicher Benutzerfreigabe.

---

## F1 – Contracts und isolierter Catalog Store

### Task F1.1: Typisierte Catalog-Verträge definieren

**Dateien:**
- Create: `core/admin_catalog/__init__.py`
- Create: `core/admin_catalog/contracts.py`
- Test: `tests/test_admin_catalog_contracts.py`

**RED-Verträge:**

- erlaubte Entry-Typen: `profile`, `group`, `remedy`, `pathogen`, `multiplex`, `terminology`, `relation`;
- stabile IDs mit konservativem Zeichensatz;
- `CatalogContext` bindet Operator/Workspace/Tenant/Scope;
- Profile referenzieren Gruppen-IDs;
- Multiplexe referenzieren Gruppen- und/oder Remedy-IDs;
- `relation` besitzt einen typisierten Relationstyp; mindestens `remedy_pathogen` bindet stabile Remedy- und Pathogen-IDs sowie Priorität verlustfrei;
- Terminologieeinträge sind referenzierbar, aber ohne explizites Mapping nicht automatisch scanwirksam;
- fachliche Datensätze enthalten keine PII-Felder;
- unbekannte Felder oder ausführbare Payloadtypen werden abgelehnt.

**Verifikation:**

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests/test_admin_catalog_contracts.py -q
```

### Task F1.2: SQLite-Schema und Transaktionsgrenzen implementieren

**Dateien:**
- Create: `core/admin_catalog/store.py`
- Test: `tests/test_admin_catalog_store.py`

**Tabellen:**

- `catalog_drafts`
- `catalog_revisions`
- `catalog_revision_entries`
- `catalog_activations`
- `catalog_audit_events`

**RED-Verträge:**

- `PRAGMA foreign_keys=ON`;
- Drafts sind kontextisoliert;
- Revisionen sind nach Erstellung immutable;
- kanonischer Payload-Hash umfasst Typ, IDs, Kontext, Source/Provenienz und Daten;
- Aktivierungspointer und Auditereignis werden atomar geschrieben;
- konkurrierende Aktivierung nutzt erwartete Vorgängerversion und scheitert bei Lost Update;
- Rollback aktiviert eine frühere Revision, ohne Revisionen zu löschen;
- Audit-Hashkette prüft interne Konsistenz und erkennt unbeabsichtigte Einzeländerungen; sie wird nicht als manipulationssicher bezeichnet, solange kein vertrauenswürdiger externer HMAC-/Signaturanker existiert;
- fehlgeschlagene Transaktion hinterlässt weder Aktivierung noch Auditfragment.

**Verifikation:**

```bash
PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests/test_admin_catalog_store.py -q
```

### Task F1.3: Typenspezifische Cross-Reference-Validierung

**Dateien:**
- Create: `core/admin_catalog/validation.py`
- Test: `tests/test_admin_catalog_validation.py`

**RED-Verträge:**

- Profil mit unbekannter Gruppe wird abgelehnt;
- Multiplex mit unbekannter Gruppe/Remedy wird abgelehnt;
- `remedy_pathogen`-Relationen mit unbekanntem Remedy oder Pathogen werden abgelehnt;
- Terminologie-Referenzen werden typ- und scopegebunden validiert;
- Alias-Zyklen und doppelte Aliase werden abgelehnt;
- leere oder deaktivierte Referenzziele sind konfigurierbar, default fail-closed;
- normalisierte IDs kollidieren nicht;
- Ergebnis enthält deterministische, sortierte Fehler und Warnungen.

### F1-Gate

**Status 2026-07-13: GO.** Contracts, isolierter SQLite-Store und Cross-Reference-Validierung sind mit `66 passed`, temporärem Live-Smoke, Compile-/Top-5-Nachweis und abschließendem unabhängigem `APPROVE` geschlossen. Gate-Record: `docs/status/2026-07-13-feedback-f-F1-contracts-store.md`. Feedback f gesamt bleibt NO-GO; als Nächstes ist ausschließlich F2 zulässig.

- Nur `tmp_path`-Daten.
- Kein Default-Runtime-Store, keine API, kein Engine-Import.
- Fokus-Suite grün, Python-Compile grün, Vollsuite ohne Top-5 grün, Top-5 separat grün.
- Read-only Review: Contracts, Transaktionen, Isolation, Hashvertrag.

---

## F2 – Offline Draft, Diff, Publish, Activate, Rollback

### Task F2.1: Admin-Service-Fassade

**Status 2026-07-13: GO.** Die vollständig offline und explizit injizierte Service-Fassade ist mit 82 fokussierten Tests, `py_compile`, baseline-identischer breiter Regression, Top-5-Smoke, unverändertem Remedy-DB-Hash und unabhängigem Current-Snapshot-`APPROVE` ohne offene P0–P2 geschlossen. Gate-Record: `docs/status/2026-07-13-feedback-f-F2-1-offline-service.md`. Als Nächstes ist ausschließlich F2.2 zulässig; F2 insgesamt und Feedback f bleiben NO-GO.

**Dateien:**
- Create: `core/admin_catalog/service.py`
- Test: `tests/test_admin_catalog_service.py`

**RED-Verträge:**

- Create/update/delete verändert nur Draft;
- deterministischer Diff Draft↔aktive Revision;
- Publish verlangt explizite erwartete Draft-Version;
- Publish ohne vorherige erfolgreiche Validierung scheitert;
- Activate ist eigener Aufruf;
- Deactivate entfernt keine Revision;
- Rollback benötigt Zielrevision und Grund;
- fremder Operator/Workspace/Tenant erhält keinen Zugriff.

### Task F2.2: Sicherer Runtime-Pfad

**Status 2026-07-13: GO.** Die vollständig offline und seiteneffektfreie Pfadpolicy ist mit 36 Pfadtests, 118 fokussierten Admin-Catalog-Tests, `py_compile`, baseline-identischer breiter Regression, Top-5-Smoke, unverändertem Remedy-DB-Hash und hashgebundenem Current-Snapshot-`APPROVE` ohne offene P0–P3 geschlossen. Gate-Record: `docs/status/2026-07-13-feedback-f-F2-2-pfadpolicy.md`. Als Nächstes ist ausschließlich F2.3 zulässig; F2 insgesamt und Feedback f bleiben NO-GO.

**Dateien:**
- Create: `core/admin_catalog/paths.py`
- Test: `tests/test_admin_catalog_paths.py`

**RED-Verträge:**

- Root kommt aus `MORPHIC_ADMIN_CATALOG_DIR` oder einem dedizierten User-Data-Default unter `%LOCALAPPDATA%/MorphicEngine/admin_catalog`; `runtime_root()` ist wegen seines Worktree-Defaults ausdrücklich nicht der Admin-Catalog-Default;
- kanonischer, kollisionsfreier Kontextnamespace;
- keine Pfadtraversierung;
- systemweiter Scope standardmäßig nicht schreibbar;
- kanonisch aufgelöste Pfade innerhalb des Projektroots, von Export-/Archivroots oder über Reparse-/Symlink-Ausbruch werden fail-closed abgewiesen.

### Task F2.3: Backup-/Recovery-Vertrag

**Status 2026-07-13: GO.** Der vollständig offline isolierte Backup-/Recovery-Baustein ist mit 31 fokussierten Backup-Tests, 149 Admin-Catalog-Tests, `py_compile`, erfolgreichem CatalogStore-Roundtrip, baseline-identischer breiter Regression, Top-5-Smoke, unverändertem Remedy-DB-Hash und hashgebundenem Current-Snapshot-`APPROVE` ohne offene P0–P3 geschlossen. Gate-Record: `docs/status/2026-07-13-feedback-f-F2-3-backup-recovery.md`. Als Nächstes ist ausschließlich F2.4 zulässig; F2 insgesamt und Feedback f bleiben NO-GO.

**Dateien:**
- Create: `core/admin_catalog/backup.py`
- Test: `tests/test_admin_catalog_backup.py`

**RED-Verträge:**

- konsistentes SQLite-Backup über Backup-API, nicht Dateikopie während Schreibzugriff;
- Manifest mit SHA-256 und Schema-Version;
- Restore nur in leeren, synthetischen Zielstore;
- Restore überschreibt keinen aktiven Store ohne gesondertes späteres Gate.

### Task F2.4: Audit-Integritätsstufen explizit machen

**Status 2026-07-13: GO.** Der reine Offline-Baustein klassifiziert die bestehende DB-Hashkette ehrlich als `consistency_only` und ergänzt HMAC-SHA-256-Audit-Head-Receipts mit expliziter Schlüsselinjektion, vollständiger Feldbindung, Rotation ohne Fallback und fail-closed Produktionsgrenze. Verifiziert mit 33 F2.4-Tests, 182 Admin-Catalog-Tests, `py_compile`, baseline-identischer breiter Regression, Top-5-Smoke, unverändertem Remedy-DB-Hash und hashgebundenem Current-Snapshot-`APPROVE` ohne offene P0–P3. Gate-Record: `docs/status/2026-07-13-feedback-f-F2-4-audit-integrity.md`. F2 ist damit vollständig GO; als Nächstes ist ausschließlich F3.1 zulässig. Feedback f bleibt NO-GO.

**Dateien:**
- Create: `core/admin_catalog/audit_integrity.py`
- Test: `tests/test_admin_catalog_audit_integrity.py`

**RED-Verträge:**

- eine reine DB-Hashkette heißt `consistency_only` und wird nicht als manipulationssicher ausgegeben;
- sicherheitsrelevante Adminfreigabe verlangt HMAC-SHA-256 mit einem injizierten Schlüssel außerhalb der SQLite-Datei;
- Tests verwenden ausschließlich synthetische Schlüssel; Produktion benötigt später einen geschützten Key-Provider außerhalb von Worktree, Export und Backuppayload;
- Audit-Head-Receipts binden Tenant, letzte Sequenz, letzten Hash, Policy-Version und Zeitpunkt;
- fehlender/ungültiger Schlüssel verhindert im späteren F6-Produktionsmodus Adminmutationen, statt still auf `consistency_only` zurückzufallen;
- Schlüsselrotation und Verifikation alter Receipts sind versioniert; Secrets erscheinen nie in DB, Logs oder Reports.

---

## F3 – Profilverwaltung ohne stille Runtimewirkung

### Task F3.1: Bestehende Profile read-only normalisieren

**Status 2026-07-14: GO.** `legacy_profile_adapter.py` exportiert 502 aktive Profile mit vollständiger Feldtreue, erhält 5 Aliasbeziehungen und löst alle 449 referenzierten Gruppen auf. Der 15-Profile-CLI-Fallback wird per AST/literal ohne Modulausführung separat als nicht autoritative Driftquelle inventarisiert (2 fehlend, 1 passend, 12 driftend). Wiederholte Exporte sind byte-/hashstabil; `MASTER_PROFILES`, CLI-Registry und Gruppenquellen bleiben unverändert. Fokus 9 Tests; breite Regression 671 passed/4 skipped bei 14 baseline-identischen Fehlern; finaler hashgebundener Review APPROVE ohne P0–P3. Gate-Record: `docs/status/2026-07-14-feedback-f-F3-1-legacy-profile-normalisierung.md`. Nächster Block: F3.2; keine Runtimewirkung.

**Dateien:**
- Create: `core/admin_catalog/legacy_profile_adapter.py`
- Test: `tests/test_admin_catalog_legacy_profiles.py`

**RED-Verträge:**

- 502 aktive Profile werden deterministisch exportiert;
- Aliasbeziehungen bleiben erhalten;
- alle 449 referenzierten Gruppen sind auflösbar;
- der duplizierte CLI-Legacy-Fallback wird separat inventarisiert und im Schattenvergleich als abweichende Authority sichtbar gemacht;
- Export verändert `MASTER_PROFILES` nicht;
- wiederholter Export ist byte-/hashstabil.

### Task F3.2: Profil-Draft-CRUD

**Status 2026-07-14: GO.** Vollständig offlinees, kontext- und CAS-gebundenes Profil-Draft-CRUD mit Create/Update/Enable/Disable/Delete-as-Tombstone. Publizierte Profile werden revisionsübergreifend erhalten; terminale Tombstones sind gegen Resurrection sowie symmetrischen ID-/Aliasdiebstahl geschützt. Tombstone-Erzeugung erfolgt ausschließlich über den spezialisierten atomaren Storepfad; mutable Revisionseingaben werden einmalig eingefroren. Verifiziert mit 34 F3.2-Tests, 225 Admin-/F3.1-Tests, baseline-identischer breiter Regression, Top-5-Smoke, unverändertem Remedy-DB-Hash und finalem hashgebundenem `APPROVE` ohne offene P0–P3. Gate-Record: `docs/status/2026-07-14-feedback-f-F3-2-profil-draft-crud.md`. Nächster Block: F3.3; keine Runtimewirkung.

**Dateien:**
- Modify: `core/admin_catalog/service.py`
- Test: `tests/test_admin_profile_management.py`

**RED-Verträge:**

- create/update/enable/disable/delete-as-tombstone;
- keine Hard-Deletes publizierter Einträge;
- Gruppenreferenzen validiert;
- Alias-Konflikte fail-closed;
- Aktivierung hat weiterhin keine Enginewirkung.

### Task F3.3: Read-only Runtime-Adapter im Schattenmodus

**Status 2026-07-14: GO; F3 vollständig GO.** Der neue Adapter liest den Catalog ausschließlich bei explizitem booleschem `shadow_mode=True`, verwendet einen atomaren, context- und hashverifizierten aktiven SQLite-Snapshot und validiert Cross-References vor dem Mapping. Die produktiv ausgewählten Profile bleiben immer entkoppelte Legacy-Kopien; Diffs sind normalisiert, deterministisch und feldspezifisch. Fehlende, defekte oder nicht sicher vergleichbare Snapshots erzeugen ausschließlich im Schattenmodus einen sichtbaren redigierten Legacy-Fallback. Es gibt keinen Package-Reexport und keinen produktiven Engine-, Web-, CLI- oder Scan-Consumer. Verifiziert mit 17 finalen Fokustests, 242 Admin-Tests, baseline-identischer breiter Regression, Top-5-Smoke und zwei finalen hashgebundenen APPROVE ohne offene P0–P3 (`deleg_aa5de206`). Gate-Record: `docs/status/2026-07-14-feedback-f-F3-3-runtime-shadow-adapter.md`. Nächster Block: F4.1 read-only.

**Dateien:**
- Create: `core/admin_catalog/runtime_adapter.py`
- Test: `tests/test_admin_catalog_runtime_adapter.py`

**RED-Verträge:**

- Adapter kann aktive Revision lesen und in bestehende `ProfileDefinition`-Form abbilden;
- ausschließlich im Schattenmodus darf eine fehlende/defekte Revision auf Legacy zurückfallen und muss den Fehler sichtbar melden;
- Schattenvergleich meldet Diff, ändert aber keinen Scan;
- Default bleibt Legacy; diese Schattenregel ist ausdrücklich keine Produktions-Fallback-Policy nach Catalog-Aktivierung.

---

## F4 – Remedies und Multiplexe vereinheitlichen

**Gate-Status 2026-07-14: GO, 100 %.** F4.1–F4.4 sind vollständig geschlossen. Weiterhin keine Runtime-, automatische Publish-/Activate- oder Netzwerkfreigabe. Feedback f bleibt bis F8 insgesamt NO-GO; nächster zulässiger Block ist F5.1.

### Task F4.1: Legacy-Remedy-Import read-only

**Status 2026-07-14: GO.** 4.079 Remedies, 1.273 Pathogene und 4.373 Links werden als 9.725 valide Catalogprojektionen deterministisch inventarisiert. Die Legacyquelle wird einmal über einen identitäts- und hashgebundenen Dateihandle gelesen; exakt diese Bytes werden ohne temporären Pfad direkt in eine gehärtete private `:memory:`-SQLite-Verbindung deserialisiert. Sidecars und Schemaabweichungen schlagen fail-closed fehl. Alle Rawfelder, IDs, Ziele, Prioritäten, Provenienzstatus und vollständigen Projektionsmappings sind testgebunden. Verifiziert mit 14 F4.1-Passes/1 hostbedingtem Symlink-Skip, 256 Admin-Passes/3 Skips, baseline-identischer breiter Regression, Top-5-Smoke und zwei finalen hashgebundenen APPROVE ohne offene P0–P3 (`deleg_82f9e495`). Gate-Record: `docs/status/2026-07-14-feedback-f-F4-1-legacy-remedy-import.md`. Nächster Block: F4.2 read-only.

**Dateien:**
- Create: `core/admin_catalog/legacy_remedy_adapter.py`
- Test: `tests/test_admin_catalog_legacy_remedies.py`

**RED-Verträge:**

- die Legacyquelle wird ohne pfadbasierten SQLite-Reopen einmalig über einen identitäts-/hashgebundenen Dateihandle gelesen; exakt diese Bytes werden direkt in eine private `query_only`-In-Memory-Verbindung deserialisiert;
- 4.079 Remedies, 1.273 Pathogene und 4.373 Links werden deterministisch erfasst;
- alte Integer-IDs werden auf stabile Catalog-IDs abgebildet;
- jeder Legacy-Link wird verlustfrei als `relation(kind="remedy_pathogen")` mit stabilen Ziel-IDs und Priorität abgebildet;
- Quellenstatus wird als `legacy_unprovenanced` gekennzeichnet, nicht erfunden;
- `data/remedies.db` bleibt hashidentisch.

### Task F4.2: Drei Multiplexmodelle explizit migrieren

**Status 2026-07-14: GO.** Die getrennten Legacy-Authorities werden vollständig read-only inventarisiert: 55 Runtime-Multiplexe, 40 explizite Remedy-Gruppen, 4.373 F4.1-gebundene Remedy-Pathogen-Relationen sowie optionale Custommodelle und 16 BAT-Fallbackschlüssel mit 48 Remedy-Paaren. Custommodelle bleiben `no_runtime_effect`, BAT bleibt `fallback_only` und sämtliche Daten `legacy_unprovenanced`. No-Follow-Descriptorbinding, Konfliktberichte, exakte BAT-Source-/Matcherhashes und der Known-Answer-Export sind fail-closed gebunden. Verifiziert mit 30 Fokustests/2 hostbedingten Skips, 286 Admin-Passes/5 Skips, baseline-identischer breiter Regression, Top-5-Smoke und zwei finalen hashgebundenen APPROVE ohne offene P0–P3 (`deleg_0c21a5c3`). Gate-Record: `docs/status/2026-07-14-feedback-f-F4-2-legacy-multiplexmodelle.md`. Nächster Block: F4.3; keine Runtimewirkung.

**Dateien:**
- Create: `core/admin_catalog/legacy_multiplex_adapter.py`
- Test: `tests/test_admin_catalog_legacy_multiplexes.py`

**RED-Verträge:**

- 55 Runtime-Multiplexgruppen werden klassifiziert;
- 40 explizite Remedy-Gruppen bleiben erkennbar;
- Remedy-Pathogen-Links und Custom-Multiplexe sind getrennte Subtypen;
- `config/groups_config.json` wird direkt und read-only gelesen; der Adapter konstruiert keinen `GroupManager`, legt keine Verzeichnisse/Dateien an und weist per Status-/Hashvergleich Nullmutation nach;
- aktive BAT-Remedy-Hardcode-Fallbacks werden als eigene Legacy-Quelle inventarisiert und nicht still als kuratierte Catalog-Daten ausgegeben;
- nicht scanwirksame Custom-Multiplexe werden nicht als aktiv dargestellt;
- Konflikte erzeugen einen Report statt stiller Überschreibung.

### Task F4.3: Remedy-/Multiplex-Draft-CRUD und Cross-Refs

**Status 2026-07-14: GO.** Versionierte Remedy-/Multiplex-Add-, Update-, Enable-, Disable- und terminale Tombstone-Semantik ist kontextisoliert und durch positive Integer-CAS-Werte gebunden. Der Store erzwingt atomar unter `BEGIN IMMEDIATE` Cross-Draft-Retention, alle vier ID-/Aliaskollisionsrichtungen sowie Remedy-Blocker für Multiplex-, Relation- und Terminology-Referenzen. Sämtliche typisierten Referenzen einschließlich `terminology_ids` werden fail-closed geprüft; Attestierung, Publish und Direct Revision revalidieren vollständige persistierte Snapshots. Schema v3 persistiert Managed-Tombstone-Autorisierung; v2-Restore ist bewusst inkompatibel und dokumentiert. Verifiziert mit 29 F4.3-Tests, 323 Admin-Passes/5 Skips, baseline-identischer breiter Regression, Top-5-Smoke und zwei finalen hashgebundenen APPROVE ohne offene P0–P3 (`deleg_8e9bbfb0`). Gate-Record: `docs/status/2026-07-14-feedback-f-F4-3-remedy-multiplex-draft-crud.md`. Der Folgeblock F4.4 ist ebenfalls GO; keine Runtimewirkung.

**Dateien:**
- Modify: `core/admin_catalog/service.py`
- Test: `tests/test_admin_remedy_multiplex_management.py`

**RED-Verträge:**

- versionierte Add/Update/Disable/Tombstone-Semantik;
- Links besitzen Priorität und Provenienz;
- Entfernen eines referenzierten Remedies wird blockiert oder als expliziter Kaskadenplan angezeigt;
- keine Runtimewirkung vor Aktivierungsgate.

### Task F4.4: Gebrochenen Legacy-Remedy-Launcher entscheiden

**Status 2026-07-14: GO; F4 vollständig GO.** Der fehlende Import `find_remedies_by_keyword` wurde reproduziert und explizit auf die bestehende `find_remedies_for_group`-Authority migriert. Fester stdin-Code, `sys.argv`, `-I -X utf8`, UTF-8-BOM, explizite Projekt-Venv, PS5-/PS7-Smokes und exakte native Exitcodes härten den Launcher. Keyword/Group sind auf 10, Pathogene auf 5 und Remedies je Pathogen auf 3 begrenzt. Datenbank-Smokes verwenden ausschließlich Sandboxkopien; Service und `data/remedies.db` bleiben bytegleich. Verifiziert mit 21 F4.4-Tests, 323 Admin-Passes/5 Skips, baseline-identischer breiter Regression, Top-5-Smoke und zwei finalen hashgebundenen APPROVE ohne P0–P3 (`deleg_6f615637`). Gate-Record: `docs/status/2026-07-14-feedback-f-F4-4-legacy-remedy-launcher.md`. Nächster Block: F5.1; keine Runtime- oder Netzwerkfreigabe.

**Dateien:**
- Modify: `Run-RemedyLookup.ps1` erst nach expliziter Migrationsentscheidung
- Test: `tests/test_legacy_remedy_lookup_contract.py`

**RED-Verträge:**

- der heutige Import der nicht vorhandenen Funktion `find_remedies_by_keyword` wird als reproduzierter Legacy-Defekt erfasst;
- vor einer Änderung wird entschieden: auf eine bestehende, getestete Servicefunktion migrieren oder den Launcher sichtbar deprecaten;
- kein stiller Alias und keine neue zweite Remedy-Such-Authority;
- der gewählte Pfad besitzt einen ausführbaren Import-/Smoke-Vertrag und verändert keine Remedy-Daten.

---

## F5 – Source-Pipeline hardening

**Zwischenstand 2026-07-15:** Makroblock F5-A (F5.5/F5.4/F5.1) ist formal abgeschlossen. F5-B (F5.2/F5.3) bleibt `NO-GO`: Freeze v4 bis v8 sind superseded; Freeze v8 erhielt ein driftfreies `APPROVE` und ein driftfreies `REQUEST CHANGES` mit zwei P1. Für Freeze v9 werden eine von der mutablen Draft-Zeile unabhängige immutable Validation-Attestation und parent-/handle-gebundene, post-attestierte, crash-durable Authority-Commitprimitive umgesetzt. Das lokale Source-Datenprotokoll verwendet den eindeutigen v3-Consistency-Vertrag und den primaeren CLI-Befehl `data-record-consistency`; `data-promote` ist nur ein sichtbar deprecateter Alias und wird niemals still als Draft-Import umgedeutet. F5-B wird erst nach zwei driftfreien `APPROVE`-Reviews auf dem vollständigen neuen Scope, anschließendem Dokumentfreeze mit zwei dokumentgebundenen `APPROVE` und einer danach vollständig rückverifizierten externen Post-State-ShadowCopy formal GO.

### Task F5.1: Vollständigen Batch-Hashvertrag einführen

**Dateien:**
- Modify: `core/source_data_promotion.py`
- Test: `tests/test_source_data_promotion.py`

**RED-Verträge:**

- Hash bindet Schema-Version, Source-ID, Datentyp, Source-Version, Lizenz, Retrieval-Metadaten und Records;
- Änderung eines gebundenen Feldes wird erkannt;
- Duplicate-/Replay-Batch wird abgewiesen;
- disabled Sources dürfen nicht gestaged werden;
- Stage bleibt für quarantined Analyse ausschließlich in einem getrennten Quarantäne-Root optional möglich, wird `analysis_only` markiert und besitzt weder Draft-, Publish- noch Aktivierungsrecht.

### Task F5.2: Typenspezifische Source-Normalizer

**Dateien:**
- Create: `core/admin_catalog/source_normalization.py`
- Test: `tests/test_admin_source_normalization.py`

**RED-Verträge:**

- separate Schemas für Profile, Gruppen, Remedies, Pathogene, Multiplexe, Terminologie und typisierte Relationen;
- jeder Record trägt Source-ID und Source-Record-ID;
- unbekannte Referenzen/Claims werden quarantänisiert;
- keine HTML-/Script-/Executable-Payloads;
- Normalisierung ist deterministisch.

### Task F5.3: Kontrollierte Uebernahme in einen Catalog-Draft

**Dateien:**
- Modify: `core/source_data_promotion.py`
- Modify: `core/source_registry.py`
- Modify: `core/admin_catalog/store.py`
- Modify: `core/admin_catalog/service.py`
- Modify: `core/admin_catalog/backup.py`
- Review dependency: `core/admin_catalog/validation.py`
- Modify: `apps/cli/commands/sources.py`
- Test: `tests/test_source_data_draft_import.py`
- Test: `tests/test_f5b_review_findings.py`
- Test: `tests/test_source_registry_cli.py`
- Test: `tests/test_admin_catalog_store.py`
- Test: `tests/test_admin_catalog_backup.py`
- Test: `tests/test_admin_profile_management.py`

**RED-Verträge:**

- der neue, getrennte Befehl `data-import-draft` schreibt ausschließlich in einen Catalog-Draft;
- expliziter Kontext, Zielstore und `--registry` sind erforderlich; es gibt keinen versteckten Default-Registry-Zugriff;
- Staging bindet den kanonischen Hash des exakten Source-Manifests, und Promotion erhält denselben expliziten Registry-Snapshot samt Identität;
- unmittelbar vor Draft-Import werden `active`, Trust-/Import-Policy und Manifest-Hash gegen den gebundenen Snapshot geprüft; disabled/quarantined/mismatched schlägt fail-closed fehl;
- ausschließlich eine immutable, zuvor gestagte und freigegebene Artefakt-ID darf übernommen werden; beliebige Ersatzdateien sind unzulässig;
- kein Publish/Activate;
- Audit und Draftmutation atomar;
- ein späteres Publish prüft das gespeicherte Source-Approval-Receipt erneut, damit eine nach Draft-Import widerrufene Source nicht aktiviert wird;
- Import akzeptiert nur die unabhängig konfigurierte `DEFAULT_SOURCE_REGISTRY_PATH`; ein caller-gelieferter Registry-Pfad kann keine eigene Authority etablieren;
- das Receipt bindet den kanonischen Registry-Authority-Pfad; byteidentische oder stale Registry-Kopien sind keine Ersatzauthority;
- der HMAC-signierte Stage-Index v3 verwendet `pending -> committed`, bindet Catalog-Pfad und Draft-ID und reconciled Commit-/Index-Fenster deterministisch; Replay in eine zweite Catalog-DB ist fail-closed;
- Stage, Index, Registry und Key weisen Symlink-/Reparse-/Hardlink-Aliase ab und binden die Dateiidentitaet ueber Authority-Reads;
- Store-owned Import laedt Base-Entries ausschliesslich ueber `base_revision_id`; Caller koennen weder Entries noch Receipts/Proofs/Callbacks einspeisen;
- alle Store-Writes beginnen mit `BEGIN IMMEDIATE` und attestieren den Schemafingerprint auf derselben Connection vor dem ersten Datenwrite;
- unterstuetzte Store-APIs exponieren keine schreibbare Low-Level-Connection. Beliebiger feindlicher Code im selben Python-Prozess bleibt ausserhalb dieser API-Trust-Grenze und erfordert fuer staerkere Isolation einen separaten OS-Prozess/Service;
- Dry-Run verändert weder Ledger noch Catalog;
- `data-record-consistency` und sein deprecateter Alias `data-promote` bleiben reine Consistency-Pfade und werden nicht still umgedeutet.

### Task F5.4: Atomare Registry-/Audit-Schreibpfade

**Dateien:**
- Modify: `core/source_registry.py`
- Test: `tests/test_source_registry_atomicity.py`

**RED-Verträge:**

- temporäre Datei + Flush + `os.replace`;
- Prozesslock oder SQLite-Registry-Migration;
- fehlgeschlagener Schreibvorgang erhält vorherigen Stand;
- Registry- und Ledgerauthorities weisen Hardlink-Aliase vor sowie am finalen Write-Boundary ab;
- Rollback-Batch-ID und Revision eindeutig;
- kein stilles Überschreiben vorhandener Stagingdateien.

### Task F5.5: Source-Policy, lokale Importgrenzen und konfliktgeprüfter Rollback

**Dateien:**
- Create: `core/admin_catalog/source_policy.py`
- Modify: `core/source_registry.py`
- Test: `tests/test_admin_source_policy.py`
- Test: `tests/test_source_registry.py`

**RED-Verträge:**

- `trust_level`, Lizenz und `import_policy` folgen serverseitigen Enums/Policyregeln; Manifest-Freitext verleiht niemals Vertrauen oder Autorisierung;
- bestehende `license`/`trust_level`/`import_policy` sind bei Manifestreplacement immutable;
- neue Source-IDs werden ausschließlich deaktiviert als `experimental_unverified`/`reference_only`
  mit typgebundener Lizenz aufgenommen; Aufwertung erfordert ein separates Folgegate;
- unbekannte `schema_version` wird abgewiesen oder über eine explizite Migration verarbeitet;
- `local_path` muss existieren, unter einem konfigurierten Admin-Importroot liegen und Reparse-/Symlink-Ausbrüche abweisen;
- Source-Manifest-Import ist nur aus einem immutable staged Artefakt mit Approval-Receipt zulässig;
- Registry-Rollback prüft erwartete aktuelle Revision und überschreibt keine legitimen späteren Änderungen;
- Rollback-Snapshots besitzen Integritätshash und eindeutigen Verbrauchs-/Revertstatus.

### Task F5.6: Bestehende Quellen-Dokumentation auf reale Semantik korrigieren

**Dateien:**
- Modify: `docs/QUELLEN_REGISTRY_BEWERTUNG_20260628.md`
- Modify: `docs/STABILIZATION_TEST_MATRIX.md`
- Test: `tests/test_source_documentation_contract.py`

**RED-Verträge:**

- „HTTPS-Allowlist“ wird nicht behauptet, solange nur ein HTTPS-Präfix geprüft wird;
- JSON-Read-Modify-Write heißt nicht „technisch append-only“;
- Ledger-only wird nicht als fachliche Datenpromotion bezeichnet;
- Metadaten-`active` wird klar von Adapterfreigabe, Fetch, Publish und Runtime-Aktivierung getrennt;
- alle Beispiele zeigen verpflichtendes Staging, Approval, explizite Registry und Rollbackgrenzen.

---

## F6 – Geschützte Admin-API und UI

### Task F6.1: Fail-closed Adminauthentisierung

**Dateien:**
- Create: `apps/web/admin_security.py`
- Modify: `Run-WebUI.ps1`
- Test: `tests/test_web_admin_security.py`

**RED-Verträge:**

- Adminmutationen sind gesperrt, wenn kein expliziter Adminschutz konfiguriert ist;
- normaler API-Key, OperatorContext und Entitlement-Stub allein gelten nicht als Adminnachweis;
- F6 authentisiert Adminrequests ausschließlich mit einem kryptographisch zufälligen, separaten `X-Morphic-Admin-Token`; der eigentliche Admin-Token erscheint nie in Cookie, Query oder URL-Fragment;
- der Launcher erzeugt serverseitig einen einmaligen Bootstrap-Nonce (maximal 30 Sekunden, single-use, an Loopback-Origin/Host und gestartete Serverinstanz gebunden) und öffnet die Adminseite über das OS ohne Ausgabe in Terminal, Log oder Clipboard;
- nur der Bootstrap-Nonce wird im URL-Fragment übergeben; Fragmente erreichen HTTP/Serverlogs nicht. Die Adminseite entfernt das Fragment vor jedem weiteren Schritt sofort mit `history.replaceState` und tauscht den Nonce einmalig per origin-/hostgeprüftem POST gegen den Admin-Token;
- Bootstrap-Nonce wird bei Erfolg, erstem Fehlversuch, Timeout oder Serverneustart unwiderruflich gelöscht; der Bootstrap-Endpunkt existiert nur während eines ausstehenden Launches, ist separat rate-limitiert und protokolliert niemals Nonce oder Token;
- der ausgegebene Admin-Token bleibt nur im Serverprozess und im flüchtigen JavaScript-Speicher, besitzt kurze TTL, Rotation bei Neustart sowie expliziten Widerruf und wird nie in `localStorage`/`sessionStorage` geschrieben; Reload schließt die Adminsession;
- Adminendpunkte prüfen zusätzlich erwarteten `Origin` und `Host`; CORS-Freigaben für Adminmutationen sind standardmäßig leer;
- da keine Cookieauthentisierung verwendet wird, entsteht kein impliziter CSRF-Credentialpfad; Requests ohne Custom Header scheitern;
- Vergleich constant-time;
- Token nie in URL, Logs, Reports oder Browserpersistenz;
- Rate-Limit separat von Scanpolling.

### Task F6.2: Admin-Catalog-API

**Dateien:**
- Create: `apps/web/admin_catalog.py`
- Modify: `apps/web/main.py`
- Test: `tests/test_web_admin_catalog.py`

**Endpunkte:**

- `GET /api/admin/catalog/status`
- `GET /api/admin/catalog/entries`
- `POST /api/admin/catalog/drafts`
- `PATCH /api/admin/catalog/drafts/{id}`
- `POST /api/admin/catalog/drafts/{id}/validate`
- `GET /api/admin/catalog/drafts/{id}/diff`
- `POST /api/admin/catalog/drafts/{id}/publish`
- `POST /api/admin/catalog/revisions/{id}/activate`
- `POST /api/admin/catalog/revisions/{id}/rollback`

Alle Mutationen benötigen Adminauth, Kontext, erwartete Version und Auditgrund.

### Task F6.3: Quellenanzeigefehler separat korrigieren

**Dateien:**
- Modify: `apps/web/static/app.js:216`
- Test: `tests/test_workbench_sources_dom.py`

**RED-Verträge:**

- `label` wird angezeigt; `name` wird nicht als Source-Contract erfunden;
- die normale Workbench erhält eine reduzierte Safe-View ohne `local_path`, interne Approvaldaten oder nicht erforderliche Repository-Metadaten;
- vollständige Source-Details sind ausschließlich in der geschützten Adminansicht verfügbar.

### Task F6.4: Admin-UI als getrennte Oberfläche

**Dateien:**
- Create: `apps/web/static/admin.html`
- Create: `apps/web/static/admin-catalog.js`
- Modify: `apps/web/static/app.css`
- Test: `tests/test_admin_catalog_dom.py`

**RED-Verträge:**

- read-only Liste ohne Auth möglich nur nach expliziter Entscheidung; Mutationen immer geschützt;
- Draft/Validierung/Diff/Publish/Aktivierung visuell getrennt;
- gefährliche Aktionen zeigen Scope, Revision, Diff und Grund;
- keine Roh-Tokens/PII/localStorage-Persistenz;
- Tastatur, Mobile 320 px, sichere Rollbackanzeige.

---

## F7 – Erster Onlineadapter, weiterhin ohne Auto-Publish

### Task F7.1: Adaptervertrag und Netzwerkpolicy

**Dateien:**
- Create: `core/admin_catalog/source_adapters/base.py`
- Create: `core/admin_catalog/network_policy.py`
- Test: `tests/test_admin_source_network_policy.py`

**RED-Verträge:**

- Adapter nur per fest registrierter Source-ID;
- Adapter-Verfügbarkeit und Adapter-Netzwerkfreigabe sind ein eigener Zustand, vollständig unabhängig von `SourceManifest.enabled/status`;
- jeder Adapter ist standardmäßig `adapter_enabled=false`; eine heute metadatenseitig aktive Source wie `ncbi_taxonomy` oder `nlm_mesh` darf dadurch keinen Fetch auslösen;
- Fetch verlangt zusätzlich zur aktiven Source eine explizite, adminauthentisierte Adapterfreigabe für genau Source-ID, Adapterversion und Tenant; eine leere Freigabeliste ist der Default;
- feste Host-Allowlist;
- HTTPS; Redirect nur auf erlaubte Hosts;
- private/loopback/link-local IPs abweisen;
- DNS-Rebinding-Schutz;
- Response-Größe, Timeout, MIME und Dekompressionslimit;
- Credentials nur aus injiziertem Secret-Provider;
- Logs redigiert;
- kein Fetch bei disabled/quarantined Source.

### Task F7.2: Ersten offiziellen Adapter implementieren

**Empfehlung:** NCBI Taxonomy oder NLM MeSH nach separater Quellenentscheidung.

**Dateien:**
- Create: `core/admin_catalog/source_adapters/ncbi_taxonomy.py` oder `nlm_mesh.py`
- Test: `tests/test_admin_source_adapter_ncbi.py` oder `test_admin_source_adapter_mesh.py`

Tests verwenden ausschließlich lokale HTTP-Fixtures/Mocktransport. Der Adapter erzeugt einen quarantänisierten Snapshot und niemals eine aktive Revision.

### Task F7.3: Reale Netzwerkabnahme als eigenes Gate

- Vorher Port-/Prozessprüfung.
- Nur eine bekannte öffentliche Quelle, deren Adapter für den isolierten Abnahmeprozess explizit und zeitlich begrenzt freigegeben wurde.
- Response-Hash, Lizenz/Version, Größe und Redirectkette dokumentieren.
- Kein Auto-Publish.
- Netzwerkfehler lassen aktive Revision unverändert.
- Der echte quarantänisierte Fetch-Snapshot bleibt gemäß definierter Retention als immutable Evidenz erhalten; bereinigt werden ausschließlich eindeutig synthetische lokale HTTP-Fixtures und davon getrennte, exakt identifizierte Testcache-Kopien.

---

## F8 – Runtime-Umschaltung und Release

### Task F8.1: Schattenvergleich gegen Legacy

- Profile, Gruppen, Remedy-Kandidaten und Multiplexauflösung für festgelegte Fixtures vergleichen.
- Jede Differenz klassifizieren: erwartet, Warnung oder Blocker.
- Default bleibt Legacy.

### Task F8.2: Vollständige Runtime-Consumption aus einer Revision

**Dateien:**
- Modify: `core/admin_catalog/runtime_adapter.py`
- Modify: `services/subgroup_service.py`
- Modify: zentrale Scan-/Runtime-Zusammenstellung erst in diesem Gate
- Test: `tests/test_admin_catalog_runtime_consumption.py`

**RED-Verträge:**

- ein Runtime-Snapshot bindet Profile, Gruppen, Remedies, Pathogene, Relationen und Multiplexe atomar an dieselbe aktive Revision-ID;
- Profilauflösung liest nur Gruppen derselben Revision;
- `SubgroupService` kann Gruppenlisten und Kandidaten über den injizierten Catalog-Provider auflösen;
- Remedy-Auflösung verwendet Catalog-Remedies und `remedy_pathogen`-Relationen derselben Revision statt paralleler Legacy-Hardcodes;
- Custom-Multiplexe lösen ihre Gruppen-/Remedy-Referenzen produktiv auf; Zyklen, dangling refs und deaktivierte Ziele schlagen fail-closed fehl;
- bei aktiviertem Catalog konsumiert kein Pfad `GroupManager`-Schattenzustand oder eine Legacy-Authority als stillen Ersatz;
- ein Prozess verwendet niemals gemischte Revisionen; Revisionwechsel wird erst im nächsten atomaren Snapshot sichtbar.

### Task F8.3: Expliziter Kill-Switch

**Dateien:**
- Modify: zentrale Runtime-Zusammenstellung erst nach bestandener F8.1- und F8.2-Abnahme.
- Test: neue Contract-/Regressionstests.

**Verträge:**

- `MORPHIC_ADMIN_CATALOG_ENABLED` wird einmalig strikt geparst: nicht gesetzt, leer, `0`, `false` oder `off` bedeutet deaktiviert; ausschließlich `1`, `true` oder `on` aktiviert;
- ein unbekannter Wert beendet den Start mit Konfigurationsfehler und wählt weder Catalog noch Legacy implizit;
- deaktiviert ergibt einen byte-/verhaltensäquivalenten Legacy-Pfad;
- aktivierter Catalog benötigt gültige aktive Revision;
- bei explizit aktiviertem Catalog führt eine fehlende, defekte, stale oder nicht autorisierte Revision ausnahmslos fail-closed zum Abbruch; es gibt keinen Produktions-Legacy-Fallback und damit keine Wiederbelebung tombstonierter/deaktivierter Catalog-Einträge;
- keine prozesslokale Mischrevision.

### Task F8.4: Reale Admin-/Runtime-Abnahme

- Desktop, Mobile und 320 px.
- Draft → Validate → Diff → Publish → Activate.
- Prozessneustart erhält aktive Revision.
- Rollback stellt vorherige Ergebnisse wieder her.
- Fremder Operator/Workspace/Tenant isoliert.
- Source disabled/quarantined bleibt ohne Wirkung.
- Auditkette und Logs ohne Token/PII.
- Vollsuite und Top-5-Smoke.
- Nur synthetische, exakt identifizierte Testdaten bereinigen.

### Finale Entscheidung

Feedback f erhält nur GO, wenn F1–F8 grün sind. Ein Offline-Admin-Catalog-GO impliziert kein Onlineadapter-GO; jede Onlinequelle erhält eine eigene Quellenfreigabe.

---

## Nächster konkrete Arbeitsblock

**F5-B Freeze v8 ist superseded / REQUEST CHANGES; bis zum Doppel-APPROVE eines neuen Freeze v9, dokumentgebundener Schlussfreigabe und Post-State-Nachweis bleibt F5-B `NO-GO`.**

Verbindliche Restfolge:

1. Die zwei v8-P1-Root-Causes schließen: erfolgreiche Draftvalidierung in einer separaten immutable Attestation-Tabelle binden und Publish gegen die live Bytes plus Attestation prüfen; Registry-, Stage-, Index-, Ledger-, Snapshot- und Key-Publikationen unter identitätsgebundenem Parent-Handle mit Temp-Inode-Bindung, durablem Namespace-Flush und finaler Byte-/Identitätsattestation ausführen.
2. Vollständige Admin-/Source-, breite und Top-5-Matrix sowie statische Checks erneut ausführen.
3. Den vollständigen Scope einschließlich Reviewregressionen, Plan und superseded Freeze-Evidenz als Freeze v9 einfrieren.
4. Zwei unabhängige driftfreie adversariale `APPROVE`-Reviews für F5.2/F5.3 einholen; jedes P0-P3 supersediert den Freeze.
5. Erst bei zwei `APPROVE`: Gate-Record, Golden Record, Kurzplan und Gesamtfortschritt aktualisieren und neu einfrieren/reviewen.
6. Externe Post-State-ShadowCopy erzeugen und jedes Manifestobjekt vollständig rückverifizieren.
7. Erst danach F5-B formal GO setzen.

F4.4 bleibt geschlossen. Keine Runtime-, Activate- oder Netzwerkfreigabe ohne eigenes Folgegate. Source-Publish ist ausschliesslich die dedizierte Receipt-Revalidierungsboundary und aktiviert nie automatisch.
