# Feedback f – F2.1 Offline Admin-Catalog-Service

- **Stand:** 2026-07-13
- **Gate:** F2.1
- **Status:** technische Verifikation abgeschlossen; unabhängiger Review ausstehend
- **Gesamtfeature Feedback f:** NO-GO

## 1. Scope

F2.1 ergänzt eine ausschließlich offline nutzbare Service-Fassade auf dem explizit injizierten `CatalogStore`:

- öffentliche, seiteneffektfreie Paketgrenze `core.admin_catalog`;
- Draft anlegen, lesen, versioniert aktualisieren und löschen;
- Draft gegen den kanonischen Catalog-Vertrag validieren;
- deterministischen Diff gegen die aktive Revision bilden;
- ausschließlich einen aktuell und erfolgreich validierten Draft atomar publizieren;
- Revision explizit aktivieren und deaktivieren;
- auf eine frühere Revision mit Pflichtgrund zurückrollen.

Ausdrücklich nicht enthalten:

- kein Default- oder Produktivpfad;
- keine Runtime-, Engine-, Web-, API- oder CLI-Verdrahtung;
- kein Netzwerkadapter;
- keine Migration bestehender Catalog-Datenbanken;
- keine produktive Catalog-Aktivierung.

## 2. Sicherheits- und Integritätsverträge

| Vertrag | Umsetzung |
|---|---|
| Kontextisolation | Alle Storezugriffe sind an Operator, Workspace, Tenant und Scope gebunden. |
| Draft-CAS | Update, Delete und Publish verlangen eine exakte positive Integer-Version; boolesche Werte werden abgewiesen. |
| Validierungsbindung | Erfolgreiche Validierung bindet Draft-Version und Payload-Hash; Update löscht diese Bindung. |
| Atomarer Publish | Prüfung der Validierungsbindung und Erstellung der finalisierten Revision erfolgen in einer `BEGIN IMMEDIATE`-Transaktion. |
| Publish ohne Aktivierung | Publish erstellt nur eine immutable Revision; der Aktivierungspointer bleibt unverändert. |
| Exakte Revisionsprovenienz | Source-Draft-ID, -Version und -Payload-Hash werden atomar persistiert und in den Revisionshash aufgenommen. |
| Provenienz-Immutabilität | Der SQL-Finalisierungstrigger fixiert ID, Version und Payload-Hash bereits beim Übergang `0 → 1`. |
| Revisions-ID-Konflikt | Doppelte IDs werden als öffentlicher `RevisionConflictError` abgewiesen; SQLite-Ausnahmen verlassen die Fassade nicht. |
| Präzise Delete-Fehlergrenze | Nur `SQLITE_CONSTRAINT_FOREIGNKEY` wird als `PublishedDraftError` klassifiziert. |
| Deterministischer Diff | Added, Removed und Changed werden über typisierte normalisierte Entry-Schlüssel stabil sortiert. |
| Deactivate ohne Datenverlust | Deactivate setzt einen Pointer-Tombstone; Revision und Revisionseinträge bleiben erhalten. |
| ABA-Schutz | Die monotone Aktivierungsversion bleibt über Deactivate hinweg erhalten. |
| Audit | Activate, Deactivate und Rollback sind getrennte atomare Hashkettenereignisse. |
| Rollback | Der Service-Test wechselt nachweislich von Revision 2 auf Revision 1 zurück. |

## 3. TDD-Evidenz

### Initialer RED-Lauf

```text
ModuleNotFoundError: No module named 'core.admin_catalog.service'
```

### Zusätzlicher Boundary-RED-Lauf

```text
3 failed
```

Die drei Fehler reproduzierten boolesche CAS-Werte bei Draft-Delete, Publish und Deactivate.

Die Umstellung des Tests auf die öffentliche Paketgrenze reproduzierte vor dem Export
erwartungsgemäß:

```text
ImportError: cannot import name 'AdminCatalogService' from 'core.admin_catalog'
```

### GREEN

```text
16 passed in 1.03s
82 passed in 8.94s
```

Die 82 Tests umfassen Contracts, Store, Validation und Offline-Service mit `-W error`.

### Compile und Smoke

```text
py_compile: PASS
F2_1_TEMP_SERVICE_SMOKE_OK
F2_1_PROVENANCE_TEMP_SMOKE_OK
F2_1_PUBLIC_IMPORT_NO_SIDE_EFFECTS_OK
Top-5-Smoke: 1 passed in 107.39s
```

Der Temp-Smoke führte Create → Validate → Publish → Activate → Deactivate aus, verifizierte den Aktivierungstombstone `(None, 2)`, prüfte die Auditkette und entfernte den temporären Store wieder.

## 4. Breite Regression

```text
563 passed, 2 skipped, 13 failed
```

Baseline ohne Admin-Catalog:

```text
481 passed, 2 skipped, 13 failed
```

Die Differenz beträgt exakt 82 neue grüne Catalog-Tests. Die 13 Fehler sind dieselben bekannten prozessweiten HTTP-429-/Rate-Limiter-Ausreißer der Baseline und keine F2.1-Regression.

## 5. Nichtmutationsnachweis

`data/remedies.db` blieb unverändert:

```text
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0
```

Repositoryweit importiert ausschließlich `tests/test_admin_catalog_service.py` die neue Service-Fassade. Damit besteht keine produktive Verdrahtung.

## 6. Sicherung

Pre-State-ShadowCopy:

```text
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_121915_feedback_f_F2_1_pre
```

Manifest: `SHA256_MANIFEST.json`, 5/5 Dateien hashverifiziert.

Pre-State vor dem unabhängigen Reviewfix-Block:

```text
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_124344_feedback_f_F2_1_reviewfix_pre
```

Manifest: `SHA256_MANIFEST.json`, 6/6 Dateien hashverifiziert.

Post-State nach F2.1-GO:

```text
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_132404_feedback_f_F2_1_GO_post
```

Manifest: `SHA256_MANIFEST.json`, 13/13 Dateien hashverifiziert.

## 7. Gateentscheidung

**GO.** Der unabhängige Current-Snapshot-Review `deleg_fa94b8c3` ergab am 2026-07-13 `APPROVE` mit hoher Konfidenz und ohne offene historische oder neue P0–P2-Befunde.

Die finale Evidenz lautet: 82 fokussierte Catalog-Tests mit `-W error`, `py_compile`, 563 grüne Restsuite-Tests plus 2 Skips bei denselben 13 bekannten Baseline-429-Ausreißern, grüner Top-5-Smoke, unveränderter Remedy-DB-Hash und keine produktive Verdrahtung. F2.1 ist damit formal geschlossen. Als nächster zulässiger Block folgt F2.2; F2 insgesamt und Feedback f bleiben NO-GO.
