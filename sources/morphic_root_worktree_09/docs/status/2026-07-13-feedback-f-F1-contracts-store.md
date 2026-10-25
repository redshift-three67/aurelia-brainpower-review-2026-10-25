# Feedback f – F1 Contracts und isolierter Catalog Store

- **Stand:** 2026-07-13 12:00 CEST
- **Branch:** `operator-workbench-phase1`
- **HEAD:** `619a1f5`
- **Gate:** F1 des Plans `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md`

## 1. Entscheidung

**F1: GO.** Der aktuelle 66-Test-Snapshot erhielt im abschließenden unabhängigen Re-Review `APPROVE` mit hoher Konfidenz und ohne offene P0–P2-Befunde. Feedback f als Gesamtfeature bleibt bis F2–F8 **NO-GO**; der nächste zulässige Block ist F2 als weiterhin offline und unverdrahtete Service-Fassade.

F1 umfasst ausschließlich:

- geschlossene Admin-Catalog-Contracts;
- einen nur über expliziten Pfad erzeugbaren SQLite-Store;
- deterministische Cross-Reference-Validierung;
- synthetische Tests und einen temporären Store-Smoke.

Nicht Bestandteil von F1 und weiterhin **NO-GO**:

- Default-/Produktivpfad;
- Runtime- oder Engine-Consumption;
- Web-/Admin-API und UI;
- Legacy-Import oder produktive Catalog-Migration;
- Onlineadapter, Fetch, Sync, Promotion oder Netzwerk;
- F2 Draft-/Diff-/Publish-Service.

## 2. Implementierter Vertrag

### F1.1 Contracts

- geschlossene Entry-Typen: `profile`, `group`, `remedy`, `pathogen`, `multiplex`, `terminology`, `relation`;
- geschlossener Relationstyp `remedy_pathogen` mit Remedy-ID, Pathogen-ID und verlustfreier nichtnegativer Priorität;
- stabile ASCII-IDs mit maximal 128 Zeichen;
- `CatalogContext` bindet Operator, Workspace, Tenant und Scope;
- Profile und Multiplexe besitzen typisierte ID-Listen;
- Terminologie bindet Ziel-ID **und** Zieltyp, ohne automatische Scanwirkung;
- PII-Schlüssel, unbekannte Felder sowie nicht-JSON-/ausführbare Payloadtypen werden fail-closed abgewiesen;
- Datensätze sind frozen; Listen werden immutable Tupel;
- kanonisches JSON und SHA-256 sind von Mapping-Reihenfolge unabhängig.

### F1.2 SQLite Store

Tabellen:

- `catalog_drafts`
- `catalog_revisions`
- `catalog_revision_entries`
- `catalog_activations`
- `catalog_audit_events`

Eigenschaften:

- kein Defaultpfad; der Aufrufer muss einen existierenden Zielordner explizit übergeben;
- `PRAGMA foreign_keys=ON` auf jeder Verbindung;
- Drafts, Revisionen und Aktivierungen sind vollständig kontextgebunden;
- Revisionen und Revisionseinträge sind über SQL-Trigger immutable;
- Revisionseinträge dürfen nur innerhalb derselben Erstellungstransaktion angelegt werden; der atomare `finalized`-Übergang sperrt danach auch zusätzliche `INSERT`s;
- der Revisionshash umfasst Kontext, Typ, Entry-ID, Source, Provenienz und Daten aller deterministisch sortierten Einträge;
- `source_draft_id` ist im Revisionshash gebunden und über einen zusammengesetzten Kontext-FK abgesichert;
- Aktivierung und Auditereignis werden unter `BEGIN IMMEDIATE` atomar geschrieben;
- erwartete Vorgänger-ID **und** Aktivierungsversion verhindern Lost Updates, Same-Pointer-Races und ABA-Wechsel;
- Rollback reaktiviert eine vorhandene Revision und löscht keine Historie;
- die Hashkette wird ehrlich nur als interne Konsistenzprüfung behandelt, nicht als manipulationssicherer externer Nachweis;
- fehlgeschlagener Auditinsert rollt die Aktivierung ohne Fragment zurück;
- alle Read-/Write-Verbindungen werden auf Erfolgs- und Fehlerpfaden explizit geschlossen.

### F1.3 Validierung

- unbekannte oder typfalsche Profil-, Multiplex-, Remedy-/Pathogen- und Terminologiereferenzen werden abgewiesen;
- Cross-Context-Verweise und gemischte Snapshots werden abgewiesen;
- normalisierte ID-Kollisionen, doppelte Aliase und Aliaszyklen werden erkannt;
- Aliase dürfen auch case-insensitiv keine fremde kanonische Entry-ID überschatten;
- deaktivierte oder leere Referenzziele sind default fail-closed;
- explizite Ausnahmen erzeugen deterministische Warnungen;
- Fehler und Warnungen sind unabhängig von der Eingabereihenfolge sortiert.

## 3. Strikter TDD-Nachweis

| Teil | RED | GREEN |
|---|---|---|
| F1.1 | `ModuleNotFoundError: core.admin_catalog` | Contracts-Suite grün |
| Terminologie-Typbindung | `target_entry_type` als unbekannt abgewiesen | Zieltyp wird geschlossen validiert |
| F1.2 | `ModuleNotFoundError: core.admin_catalog.store` | Store-Suite grün |
| F1.3 | `ModuleNotFoundError: core.admin_catalog.validation` | Validierungssuite grün |
| Windows-Verbindungsfreigabe | `PermissionError [WinError 32]` beim Löschen des Tempstores | explizites Closing; Löschtest und Smoke grün |
| Review: Aktivierungs-CAS | ABA-/Same-Pointer-Aufruf wurde nur über Revisions-ID geprüft | Pointer + monotone Aktivierungsversion erforderlich |
| Review: Revisionsabschluss | nachträglicher SQL-`INSERT` in Revisionseinträge möglich | atomarer `finalized`-Übergang + INSERT-Trigger |
| Review: Draft-Provenienz | erfundene/fremde Draft-ID und hashgleiche Herkunft möglich | Kontext-FK + `source_draft_id` im Hash |
| Review: Alias-Namespace | einseitige case-insensitive Alias↔Canonical-Kollision blieb gültig | deterministischer `alias_canonical_collision`-Fehler |
| Review: SQLite-URI | `%23` im gültigen Windows-Dateinamen wurde als URI-Encoding fehlinterpretiert | `Path.as_uri()` + Reserved-Character-Test |
| Review: Setupfehler | PRAGMA-Fehler konnten frisch geöffnete Handles offen lassen | Setup liegt unmittelbar in `try`/`except` bzw. `try`/`finally`; Lese- und Schreibtest grün |
| Review: exakte Duplikate | gleicher Typ und gleiche ID ohne vollständigen Tie-Breaker konnten reihenfolgeabhängige Folgefehler erzeugen | kanonischer JSON-Tie-Breaker für Eingang, Index und Aliasowner |
| Review: Store-Hashordnung | normalisierte ID-Kollisionen hatten im Draft-/Revisionshash keinen totalen Tie-Breaker | Sortierung nach Typ, normalisierter ID und kanonischem Entry-JSON; echter Kollisions-Reversaltest |
| Review: nicht-endliche Zahlen | internes JSON-Freezing akzeptierte `NaN` und `±Infinity` | `math.isfinite()` fail-closed und `allow_nan=False` in beiden Serialisierern |

## 4. Verifikation

### Fokus und Compile

```text
66 passed in 1.24s
py_compile: PASS
Warnings-as-errors: PASS
```

### Synthetischer Live-Smoke

```text
F1_TEMP_STORE_SMOKE_OK
```

Der Smoke erzeugte in `TemporaryDirectory` einen Store, eine Revision und eine Aktivierung, prüfte Hashkette und aktiven Pointer und löschte den temporären Store anschließend erfolgreich.

### Top-5 separat

```text
1 passed in 96.31s
```

### Vollsuite und Baselinevergleich

Aktueller F1-Stand ohne Top-5:

```text
547 passed, 2 skipped, 13 failed
```

Baseline ohne alle drei neuen F1-Testdateien:

```text
481 passed, 2 skipped, 13 failed
```

Die 66 aktuellen F1-Tests erklären exakt die Pass-Differenz gegenüber der Baseline. Alle 13 Fehler sind in beiden Läufen identische bestehende HTTP-429-Fehler. Ursache ist der modulglobale `_rate_limit_store` in `apps/web/security.py`, der über viele `create_app()`-Tests dieselbe Test-IP akkumuliert. Drei repräsentative Fehler bestehen isoliert. Dieser fremde Web-WIP wurde in F1 bewusst nicht verändert.

## 5. Nichtmutationsnachweis

- Außerhalb der neuen Tests importiert kein bestehender Python-Pfad `core.admin_catalog`.
- Keine DB-Datei liegt im neuen Paket oder Repository.
- `data/remedies.db` blieb unverändert:

```text
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0
```

- Keine Runtime-, Web-, CLI-, Engine-, Source-Registry- oder Netzwerkverdrahtung.
- Keine Server gestartet; Ports 8000/8090 nicht verändert.
- Kein Commit, Push, Staging, Reset oder Clean.
- Statischer Scan: kein `eval`, `exec`, Pickle, Shellaufruf, dynamisch interpoliertes SQL, TODO/FIXME oder Debug-`print`.

## 6. ShadowCopy

Vor F1 wurde folgende externe Sicherung erzeugt und vollständig per SHA-256 verifiziert:

`E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_103857_feedback_f_F1_pre`

Vor dem formalen Gateabschluss wurden Plan, Gesamtstatus und dieser Gatebericht erneut extern gesichert und vollständig per SHA-256 verifiziert:

`E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_115854_feedback_f_F1_gate_close_pre`

## 7. Unabhängiger Review

**Status: APPROVE / hohe Konfidenz.** Drei Reviews älterer Snapshots ergaben zunächst `REQUEST CHANGES`; alle fünf P1-Blocker und alle fünf relevanten P2-Test-, URI-, Handle-, Determinismus- und JSON-Lücken wurden strikt RED→GREEN korrigiert. Der abschließende Review des aktuellen 66-Test-Snapshots (`deleg_439b7fe0`) bestätigte sämtliche Schließungen, fand keine neuen P0–P2-Befunde und keine erkennbaren False-Positive-Tests.
