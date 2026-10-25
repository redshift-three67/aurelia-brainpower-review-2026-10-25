# Feedback f – Read-only Ist-Analyse Adminverwaltung und Repositories

**Stand:** 2026-07-13 10:32 CEST

**Arbeitsbereich:** Feedback f – Admin-Verwaltung Profile/Remedies/Multiplexe + Online-Repositories

**Branch:** `operator-workbench-phase1`

**Scope:** Quelltext-, Datenmodell-, CLI-, Web- und Testkartierung; keine Produktionsdatenmutation, kein Netzwerkzugriff

---

## 1. Entscheidung in Kurzform

Feedback f ist **noch nicht implementiert und bleibt NO-GO**. Der aktuelle Stand enthält wertvolle Vorarbeiten, aber keine durchgängige Adminverwaltung und keine produktive Online-Repository-Anbindung.

Wichtig ist die Trennung:

- Die bestehende Engine bleibt durch diesen Befund **nicht blockiert**.
- Die 18 Einträge in `config/source_repositories.json` sind derzeit eine **Metadaten-Registry**, keine aktiven Netzwerkadapter.
- `sources data-record-consistency` schreibt ausschließlich einen Consistency-Ledger-Eintrag; es aktiviert keine Profile, Gruppen, Remedies oder Multiplexe im Runtime-Katalog. `data-promote` ist nur ein sichtbar deprecateter Alias.
- Eine sichere Umsetzung muss deshalb zuerst offline und revisionsbasiert erfolgen. Netzwerkadapter kommen erst nach einem belastbaren Staging-/Freigabe-/Rollback-Gate.
- Geo bleibt außerhalb dieses Arbeitsbereichs separat NO-GO.

---

## 2. Real gemessener Ist-Stand

| Bereich | Beobachteter Stand |
|---|---:|
| Aktive Profile | 502 |
| Profile Level 1/2/3/4/5 | 5 / 30 / 20 / 153 / 294 |
| Runtime-Gruppen | 450 |
| Gruppen mit `multiplex` im Namen | 55 |
| Explizite Remedy-Gruppen | 40 |
| Dynamische Gruppen | 8 |
| Remedies in `data/remedies.db` | 4.079 |
| Pathogene | 1.273 |
| Remedy-Pathogen-Links | 4.373 |
| Remedy-Keywords | 21.349 |
| Source-Manifeste | 18 |
| Als `active` markierte Sources | 16 |
| Deaktiviert/quarantänisiert | 2 |
| Source-Typen | 8 Webreferenzen, 5 APIs, 3 Downloads, 2 lokale Imports |

Die Remedy-Datenbank wurde per SQLite-URI `mode=ro` gelesen. Ihr SHA-256 blieb vor/nach der Prüfung identisch:

```text
c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0
```

---

## 3. End-to-End-Kartierung

### 3.1 Profile

```text
core/profile_sync/__init__.py
  ├─ MASTER_PROFILES (codebasiert, Importzeit)
  ├─ _auto_register_fein_profiles()
  ├─ _auto_register_all_groups_as_profiles()
  ├─ create_dynamic_profile() (nur In-Memory)
  ├─ CLI Registry/Scan
  └─ GET /api/profiles (nur Lesen)
```

Befund:

- Die primäre Authority ist Python-Code in `core/profile_sync/__init__.py:42-83`.
- Automatische Registrierungen werden beim Modulimport ausgeführt (`core/profile_sync/__init__.py:1684-1688`).
- `create_dynamic_profile()` verändert ausschließlich das prozesslokale Dictionary und besitzt keine Persistenz, Revision oder Adminoberfläche (`core/profile_sync/__init__.py:1609-1650`).
- Die Web-API ist read-only (`apps/web/profiles.py:11-44`).
- Es existieren keine produktiven Create/Update/Delete-/Enable-/Disable-Adminendpunkte.
- Der aktive CLI-Wrapper besitzt bei einem Importfehler einen großen, duplizierten Legacy-Fallback (`apps/cli/profiles/registry.py:3-29,675-712`). Ein späterer Catalog-Adapter muss daher nicht nur `MASTER_PROFILES`, sondern auch dieses abweichende Fehlerverhalten ausdrücklich ablösen oder fail-closed machen.

### 3.2 Remedies

```text
data/remedies.db
  ├─ remedies / remedy_keywords / remedy_descriptions
  ├─ pathogens / pathogen_keywords
  ├─ remedy_pathogen_map
  ├─ services/remedy_service.py
  └─ core/subgroups/procedural_groups.py (vier DB-Kategorien als Runtime-Labels)
```

Befund:

- `services/remedy_service.py` enthält Add- und Read-Funktionen, aber keine vollständige Update-/Delete-/Deactivate-/Revision-API.
- Ein bestehendes Remedy wird durch `INSERT OR IGNORE` nicht fachlich aktualisiert; zusätzliche Keywords werden nur angehängt (`services/remedy_service.py:139-180`).
- Das Schema enthält keine Source-ID, Import-Batch-ID, Revision, Aktivierungsstatus, Operator-/Workspace-/Tenantbindung oder fachliche Freigabe.
- SQLite-Fremdschlüssel werden deklariert, aber der Service aktiviert `PRAGMA foreign_keys=ON` nicht.
- Der Modulimport ruft `init_remedy_database()` auf (`services/remedy_service.py:624-629`) und ist daher nicht rein lesend.
- Nur vier dynamische Runtime-Gruppen laden Remedy-Namen nach fest codierter Kategorie aus der DB (`core/subgroups/procedural_groups.py:1494-1507`).
- BAT-Berichte besitzen zusätzlich einen eigenen Remedy-Suchpfad mit Hardcode-Fallback (`core/bat_report_aggregator.py:225-292`). Auch dieser aktive Fallback ist Teil der späteren Authority-Migration.

### 3.3 Multiplexe

Der Begriff „Multiplex“ bezeichnet aktuell drei nicht vereinheitlichte Modelle:

1. **Statische/prozedurale Runtime-Gruppen**

   55 Gruppennamen enthalten `multiplex`; Labels stammen aus Python-Listen, Dateien oder vier fest verdrahteten Remedy-DB-Kategorien.
2. **Remedy-Pathogen-Mapping**

   `remedy_pathogen_map` enthält 4.373 Links. Schreib-/Lesefunktionen existieren in `services/remedy_service.py:472-515`, aber außerhalb dieses Services wurde kein produktiver Konsument gefunden.
3. **Custom-Multiplex-Konfiguration**

   `tools/group_manager.py` kann `config/groups_config.json` schreiben. Die Datei existiert aktuell nicht. Die aktive CLI verwendet den Manager nur für `scan groups-overview`; Custom-Gruppen/-Multiplexe werden nicht in `procedural_groups.list_groups()` oder die Scan-Kandidatenerzeugung eingebunden (`apps/cli/commands/scan.py:543-620`).

Damit existiert keine kanonische Multiplex-Authority. Eine über `GroupManager` angelegte Struktur wäre zwar auflistbar, aber nicht nachweislich produktiv scanwirksam.

### 3.4 Source Registry und Datenkonsistenz

**Zeitbezug:** Die nachfolgende Befundmatrix dokumentiert die Vor-F5-A-Baseline vom 13. Juli 2026.
Die Punkte F-06 bis F-09, F-16 und die planseitige lokale Pfadgrenze aus F-17 wurden durch F5-A
technisch geschlossen; die aktualisierten Nachweise stehen jeweils direkt in der Tabelle. Nicht
freigegeben bleiben ein echter lokaler Handle-Consumer, Catalog-Publish/-Activate und Netzwerkadapter.

```text
config/source_repositories.json
  └─ core/source_registry.py
      ├─ CLI: list/enable/disable/validate/stage/import/rollback
      └─ GET /api/sources

JSON-Datenbatch
  └─ stage_source_data_batch()
      └─ immutable staged JSON + Vollvertragshash + stabile Batchidentitaet
          └─ promote_staged_source_data()
              └─ data-record-consistency + v3-Consistency-Ledger-Eintrag
                  └─ KEINE aktive Katalogmutation
```

Vorhanden und testabgesichert:

- Manifestvalidierung, eindeutige Source-IDs und HTTPS-Schema.
- Aktivieren/Deaktivieren sowie Quarantäne-Override.
- Staging, Dry-Run/Diff und Registry-Rollback-Snapshot.
- Vollstaendiger Datenbatchvertrag, stabile Duplicate-Identitaet, Record-Count und Replay-Sperre.
- Atomare Registry-/Ledgerpfade mit Prozesslock sowie Hardlink-/Alias-Ablehnung.
- Server-owned Policytransition: bestehende Policyfelder sind immutable; neue Sources starten
  ausschließlich `experimental_unverified`/`reference_only` und deaktiviert.
- CLI-Discovery und lokale JSON-Testbatches.

Nicht vorhanden:

- Online-Fetcher oder quellspezifische Adapter.
- Produktive Aktivierung der gestagten Datensätze.
- Typenspezifische Profil-/Gruppen-/Remedy-/Multiplex-Schemas.
- Aktivierungspointer auf eine freigegebene, immutable Revision.
- Atomare Laufzeitumschaltung und Runtime-Reload.
- Operator-/Workspace-/Tenant-Ownership und Adminberechtigung.
- Netzwerk-Allowlist/Redirect-/DNS-/IP-/Größen-/Timeout-Gates.

---

## 4. Befundmatrix

| ID | Priorität für Feedback f | Befund | Evidenz / Wirkung |
|---|---:|---|---|
| F-01 | P0 | Keine durchgängige Adminoberfläche oder Admin-API | Profile nur GET; Remedies nur interne Servicefunktionen; Multiplexmodelle getrennt |
| F-02 | P0 | Source-Datenkonsistenz ist keine fachliche Promotion | `data-record-consistency` schreibt nur das lokale Consistency-Ledger v3; `data-promote` ist deprecatet |
| F-03 | P0 | Keine produktiven Onlineadapter | Registry enthält URLs, aber kein Runtime-Fetch-/Mappingpfad |
| F-04 | P0 | Keine kanonische, versionierte Catalog-Authority | Profile, statische Gruppen, Remedy-SQLite und Custom-Config sind getrennte Wahrheiten |
| F-05 | P1 | Generisches Batchschema ist fachlich zu schwach | Nur `id`/`label`; beliebiges `payload`; keine typenspezifischen Referenzprüfungen |
| F-06 | P1 → geschlossen in F5-A | Integritätshash band nur `records` | Vollvertrag bindet Source, Typ, Lizenz, Retrieval-Metadaten, Records, Registry-/Manifestbaseline, Rechte, Quarantänestatus und Stagingzeit; stabile Batchidentität bindet den fachlichen Batch ohne Zeitfeld. |
| F-07 | P1 → geschlossen in F5-A | Disabled/quarantined Source konnte gestaged/geloggert werden | Disabled wird abgewiesen; Quarantäne benötigt einen disjunkten Analysis-only-Root und besitzt keine Consistency-/Draft-/Publish-/Activate-Rechte. |
| F-08 | P1 → geschlossen innerhalb der dokumentierten F5-A-Grenze | Ledger war nicht replay-sicher | v3-Ledger wird vollständig validiert, unter Lock atomar ersetzt, weist Duplicate-Identitäten und Hardlink-Aliase ab; kein externer Tamper-Anker wird behauptet. |
| F-09 | P1 → geschlossen in F5-A | Registry-/Ledger-Schreibvorgänge waren nicht atomar/konkurrenzsicher | Temp+fsync+Replace/Publish, CAS-/Revisionprüfung, Prozesslocks und Aliasprüfung sind testgebunden. |
| F-10 | P1 | Remedy-Datensätze besitzen keine Provenienz/Revision/Aktivierung/Ownership | aktuelles SQLite-Schema in `services/remedy_service.py:42-111` |
| F-11 | P1 | Custom-Multiplexe sind nicht scanwirksam verdrahtet | `GroupManager` wird produktiv nur in `groups-overview` gelesen |
| F-12 | P1 | Aktuelle Operator-/Entitlement-Schichten sind kein echtes Admin-Authsystem | `operator_context.py:8-13`; Entitlement-Stub erlaubt standardmäßig alles |
| F-13 | P2 | Web-Quellenliste verwendet falsches Feld | API liefert `label`; `apps/web/static/app.js:216` rendert `s.name` |
| F-14 | P2 | Dokumentation überschätzt einzelne Sicherheitsmerkmale | „HTTPS-Allowlist“, „append-only“ und „Promotion“ sind im aktuellen Code enger/anders umgesetzt |
| F-15 | P2 | `GroupManager` mutiert bei Konstruktion potenziell das Dateisystem | `config_path.parent.mkdir(...)` in `tools/group_manager.py:20-23` |
| F-16 | P1 → geschlossen in F5-A | Policy war manifestseitig selbstzuweisbar | Enumvalidierung plus server-owned Transition: bestehende `license`/`trust_level`/`import_policy` sind bei Manifestreplacement immutable; neue Sources sind ausschließlich deaktiviertes Least-Privilege-Onboarding. |
| F-17 | P1 → planseitige Grenze geschlossen in F5-A | Lokale Importpfade waren nicht eingegrenzt | Existenz, expliziter absoluter Admin-Root, Containment sowie Symlink-/Reparse-Ablehnung sind Point-in-time geprüft. Ein künftiger Consumer muss am Read-Boundary erneut per Handle prüfen und privat snapshotten. |
| F-18 | P1 → geschlossen in F5-A | Registry-Rollback war global und nicht konfliktgesichert | Revision-/Hash-CAS verhindert das Überschreiben späterer Änderungen; Rollback-Snapshots sind integritätsgebunden und besitzen einen autoritativen One-shot-Verbrauchsstatus. |
| F-19 | P2 | Aktive Legacy-/Fallbackpfade erhöhen Authority-Drift | duplizierte CLI-Profilliste, BAT-Remedy-Hardcodes und gebrochener `Run-RemedyLookup.ps1`-Import (`apps/cli/profiles/registry.py:3-29`; `core/bat_report_aggregator.py:225-292`; `Run-RemedyLookup.ps1:39-54`) |
| F-20 | P2 | Web-Source-Safe-View ist nicht reduziert | unauthentifiziertes GET gibt das vollständige Mapping einschließlich lokaler Pfade/Warnungen aus (`apps/web/main.py:435-443`; `core/source_registry.py:94-116`) |

Keiner dieser Befunde ist ein neuer E5.10-Regressionstatbestand. Sie sind jedoch Release-Blocker für eine Behauptung, Feedback f sei umgesetzt.

---

## 5. Sicherheitsgrenzen für das Zielbild

1. **Offline first:** lokale Adminimporte vollständig beherrschen, bevor der erste Netzwerkadapter aktiv wird.
2. **Keine generischen URL-Fetches:** Adapter werden per festem Source-ID-Code registriert; ein Manifest darf keine beliebige Fetch-URL ausführbar machen.
3. **Daten, niemals Code:** keine Plugins, Python-Imports, Skripte, Templates mit Ausführung oder Deserialisierung ausführbarer Objekte.
4. **Immutable Revisionen:** Staging erzeugt eine inhaltsadressierte Revision; Freigabe ändert nur einen atomaren Aktivierungspointer.
5. **Typisierte Schemas:** Profile, Gruppen, Remedies, Pathogene, Multiplexe, Terminologie und typisierte Relationen besitzen getrennte Verträge und Referenzintegrität.
6. **Fail closed:** fehlende Provenienz, Lizenz, Source-Version, Referenz oder Adminberechtigung verhindert Publish.
7. **Explizite Aktivierung:** Source aktivieren, Daten abrufen, Revision freigeben und Runtime aktivieren sind getrennte Handlungen.
8. **Rollback ohne Datenverlust:** Rollback schaltet auf eine frühere immutable Revision; keine destruktive Rückkopie.
9. **Mandantenkontext:** Drafts, Freigaben und Audit binden Operator, Workspace und Tenant; systemweite Basiskataloge benötigen einen expliziten globalen Scope.
10. **Keine PII:** Repository-Daten enthalten ausschließlich Fachkatalogdaten, keine Klienten-/Gruppenteilnehmerdaten.
11. **Netzwerk-Gates:** feste Host-Allowlist, HTTPS, Redirectgrenzen, DNS/IP-Prüfung, Größen-/Zeitlimits, MIME-Prüfung und Credentials außerhalb von Manifesten/Logs.
12. **Audit:** hashverkettete Ereignisse liefern zunächst interne Konsistenz. Manipulationssicherheit darf erst mit einem vertrauenswürdigen HMAC-/Signaturanker außerhalb der SQLite-Datei behauptet werden.
13. **Externer Store:** Der Admin-Catalog liegt standardmäßig unter einem dedizierten User-Data-Root außerhalb des Projekts; der heutige `runtime_root()`-Default im Worktree ist dafür unzulässig.
14. **Eindeutiger Fallback:** Legacy-Fallback ist nur im Schattenmodus zulässig. Nach expliziter Catalog-Aktivierung führt eine fehlende oder defekte Revision ausnahmslos fail-closed zum Abbruch.
15. **Adapter default-off:** Source-Metadatenstatus und Netzwerkadapterfreigabe sind getrennt. Auch eine heute als `active` markierte Source löst ohne separate, tenantgebundene Adapterfreigabe keinen Fetch aus.
16. **Keine Misch-Authority:** Eine aktive Catalog-Revision liefert Profile, Gruppen, Remedies, Pathogene, Relationen und Multiplexe als atomaren Snapshot; Custom-Multiplexe oder Legacy-Hardcodes dürfen nicht still beigemischt werden.

---

## 6. Empfohlene Zielarchitektur

```text
Admin UI / CLI
   │
   ▼
Admin Catalog API (explizit geschützt)
   │
   ├─ Draft Store (operator/workspace/tenant)
   ├─ Type Validators
   ├─ Diff + Cross-Reference Validation
   ├─ Approval/Audit Service
   └─ Activation Service
          │
          ▼
Immutable Catalog Revisions
          │
          ├─ profiles
          ├─ groups
          ├─ remedies
          ├─ pathogens
          ├─ multiplexes
          ├─ terminology
          └─ typed relations
          │
          ▼ atomarer active_revision-Zeiger
Runtime Catalog Snapshot / Adapter
          │
          └─ bestehende Engine-Schnittstellen

Source Adapter Registry (eigener Status, ausnahmslos default-disabled)
   └─ Fetch Snapshot → Quarantine → Normalize → Draft Store
```

Empfehlung: zunächst ein neuer, isolierter `admin_catalog`-Store unter `%LOCALAPPDATA%` oder einem expliziten `MORPHIC_ADMIN_CATALOG_DIR` außerhalb des Worktrees statt einer direkten Migration von `data/remedies.db`. Die bestehende Engine erhält einen read-only Adapter auf den aktivierten Snapshot. Dadurch bleibt der heutige Katalog bis zum expliziten Gate unverändert.

---

## 7. Gatefolge

| Gate | Inhalt | Abschlusskriterium |
|---|---|---|
| F1 | Kanonische Contracts und read-only Catalog-Snapshot | Typisierte Modelle, Referenzintegrität, keine Runtimewirkung |
| F2 | Offline Draft/Revision/Activation/Rollback | Immutable Revisionen, atomarer Pointer, Audit, Tenant-Isolation |
| F3 | Profilverwaltung | CRUD als Draft; Enable/Disable; Aliase; Gruppenreferenzen; Runtime-Adapter |
| F4 | Remedy-/Multiplex-Konsolidierung | eine Authority; Migration/Diff der drei heutigen Modelle; keine stille Wirkung |
| F5 | Source-Pipeline hardening | typisierte Batches, vollständiger Hashvertrag, Replay-/Lock-/Rollback-Gates |
| F6 | Geschützte Admin-API und UI | explizite Adminauthentisierung, sichere Vorschau/Diff/Freigabe |
| F7 | Erster offizieller Onlineadapter | separate default-off Adapterfreigabe, eine feste Quelle, Netzwerk-Gates, immutable Snapshot, kein Auto-Publish |
| F8 | Runtime-Consumption und Release | ein atomarer Catalog-Snapshot für alle Authorities; Desktop/Mobile, Prozessneustart, Rollback, Artefakt-/Log-Audit, Vollregression |

Online-Repositories bleiben bis einschließlich F6 technisch NO-GO.

---

## 8. Read-only Verifikation

```text
18 Source-/CLI-/Promotion-Tests: 18 passed in 0.71s
3 Profil-/Gruppenintegritätstests: 3 passed in 0.13s
```

Zwei zusätzlich delegierte, voneinander unabhängige statische Read-only-Audits bestätigten die fragmentierte Datenhoheit und den rein metadaten-/ledgerbasierten Source-Stand. Ihre Zusatzbefunde zu CLI-/BAT-Fallbacks, frei deklarierbarer Trust-Policy, umgehbarem Staging, lokalem Pfad-Sandboxing, globalem Registry-Rollback und Web-Safe-View wurden in F-16 bis F-20 sowie in den Gateplan übernommen.

Anschließende Cross-Reviews meldeten zunächst `REQUEST CHANGES`. Korrigiert wurden das vollständige Pathogen-/Terminologie-/Relationsmodell, der externe Admin-Catalog-Pfad, die explizit gebundene Registry-Identität im Promotion-Gate, Disabled-/Quarantäne-Staging, separate default-off Adapterfreigabe, vollständige Runtime-Consumption, die eindeutige Shadow-/Produktions-Fallback-Policy, strikte Kill-Switch-Werte, ehrliche Audit-Integritätsstufen, Legacy-/Dokumentations-/Cleanup-Gates und der konkrete kurzlebige Header-Token-Vertrag samt einmaligem Bootstrap-Nonce. Der letzte Review der tatsächlich aktuellen Fassung endete mit `APPROVE`; es bestehen keine offenen P0–P2-Widersprüche im Dokumentations- und Planstand.

Zusätzlich:

- `sources --help` zeigt neben Registrybefehlen `data-stage` und den primaeren Befehl `data-record-consistency`; `data-promote` bleibt als deprecateter Kompatibilitaetsalias sichtbar.
- Repository-Statushash blieb während beider Testblöcke identisch.
- `data/remedies.db` blieb hashidentisch.
- Es wurden keine Server gestartet und keine Netzwerkzugriffe durchgeführt.
- Port 8000 und Port 8090 wurden nicht verändert.
- Keine Commits, Pushes, Stagings, Resets oder Cleans.

---

## 9. Gateentscheidung

| Bereich | Entscheidung |
|---|---:|
| Read-only Ist-Analyse | **GO / abgeschlossen** |
| Bestehende Engine | **unverändert** |
| Feedback f als Gesamtfeature | **NO-GO / nicht implementiert** |
| Offline Admin-Catalog F1 | **als nächster TDD-Block empfohlen** |
| Online-Fetch/Sync | **NO-GO bis F1–F6** |
| Geo | **separat NO-GO** |
