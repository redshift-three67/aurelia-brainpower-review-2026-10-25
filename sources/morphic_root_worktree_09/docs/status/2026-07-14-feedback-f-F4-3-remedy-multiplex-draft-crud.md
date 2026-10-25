# Feedback f – F4.3 Remedy-/Multiplex-Draft-CRUD und Cross-References

- **Stand:** 2026-07-14
- **Teilgate:** F4.3
- **Teilgate-Status:** GO
- **Gesamtgate F4:** offen; F4.4 ausstehend
- **Feedback f als Gesamtfeature:** NO-GO bis F8
- **Branch:** `operator-workbench-phase1`
- **HEAD:** `619a1f5485a151816e32732929a6a823839ccb57`

## 1. Vorgesehener Freigabeumfang

F4.3 ergänzt ausschließlich versionierte, kontextisolierte Draft-Verwaltung für Remedies und Multiplexe:

- typisiertes Add, Update, Enable, Disable und Tombstone;
- strikt positive Integer-CAS-Werte;
- atomare Lifecycle- und Referenzprüfung unter `BEGIN IMMEDIATE`;
- terminale Tombstones mit draft- und revisionsübergreifender Retention;
- deterministische Referenzblocker für Multiplex-, Relation- und Terminology-Referenzen;
- hashgebundene Relation-Priorität und Record-Provenienz;
- vollständige Snapshotvalidierung an Attestierungs-, Publish- und Direct-Revision-Grenzen;
- keine automatische Kaskade und keine stille Datenentfernung.

Dieser Record dokumentiert den freigegebenen F4.3-Snapshot. Zwei unabhängige, exakt hashgebundene Reviews unter `deleg_8e9bbfb0` lieferten `APPROVE` mit hoher Konfidenz und ohne offene P0–P3.

## 2. Wirkungsgrenze

F4.3 erzeugt weder Publish noch Activate automatisch. Es gibt keine neue Runtime-, Engine-, Scan-, CLI-, Web- oder Netzwerkverdrahtung. Die bestehenden Legacy-Authorities werden weder migriert noch verändert:

- `data/remedies.db`;
- `core/bat_report_aggregator.py`;
- `core/subgroups/procedural_groups.py`;
- `core/remedy_group_registry.py`.

Drafts dürfen als Zwischenzustand invalid sein. Ein invalider Draft darf jedoch weder erfolgreich attestiert noch publiziert werden. Direct Revisions werden ebenfalls vor der Finalisierung vollständig validiert.

## 3. Cross-Reference-Vertrag

Für live Entries werden sämtliche typisierten Referenzen geprüft:

- `profile.group_ids -> group`;
- `multiplex.group_ids -> group`;
- `multiplex.remedy_ids -> remedy`;
- `relation.remedy_id -> remedy`;
- `relation.pathogen_id -> pathogen`;
- `terminology.target_entry_id -> target_entry_type`;
- jedes zugelassene `terminology_ids -> terminology`.

Unbekannte, typfalsche, kontextfremde oder deaktivierte Ziele schlagen fail-closed fehl. Historische ausgehende Referenzen eines terminalen Remedy-/Multiplex-/Profil-Tombstones werden nicht neu interpretiert; der Tombstone selbst bleibt hashidentisch.

Ein Remedy kann weder deaktiviert noch tombstoniert werden, solange Multiplex-, Relation- oder Terminology-Referenzen im Kandidaten bzw. atomar gelesenen Draft verbleiben. Referenzen müssen in expliziten, versionierten CAS-Updates entfernt werden. F4.3 führt keine automatische Kaskade aus.

## 4. Store- und Bypassgrenzen

- `create_draft()` und `create_revision()` materialisieren caller-gelieferte Iterables exakt einmal.
- Low-Level-`update_draft()` blockiert Hard-Delete, unautorisierte Tombstones und Disable eines weiterhin referenzierten Remedies.
- `mark_draft_validated()` lädt und validiert den persistierten Snapshot atomar.
- `publish_validated_draft()` revalidiert den vollständigen persistierten Snapshot innerhalb derselben `BEGIN IMMEDIATE`-Transaktion, auch bei manipuliertem Validation Marker.
- `create_revision()` validiert ausnahmslos den vollständigen Snapshot, auch relation-, terminology- oder profile-only.
- Publizierte Tombstones reservieren ID und Aliase in allen vier Kollisionsrichtungen.

## 5. SQLite-Schema v3 und Backup-Kompatibilität

F4.3 erweitert das Admin-Catalog-Schema additiv um `catalog_draft_managed_tombstones`. Diese Tabelle bindet die ausschließlich über den privaten atomaren Storepfad erzeugte Remedy-/Multiplex-Tombstone-Autorisierung an Draft, Typ, ID und Payload-Hash.

- **Catalog-Schema-Version:** `3`
- **Schema-v3-Fingerprint:** `8561479448208e9b66a97ccef39ef5767734c93a2f520860267b45aa13c7bda6`
- Backup und Restore erhalten die Autorisierungstabelle vollständig und fingerprintgebunden.

### Bewusste v2-Inkompatibilität

Der Restore-Vertrag akzeptiert nur exakt die aktuelle Manifest-Schema-Version und den aktuellen Schemafingerprint. Daher werden Schema-v2-Backups nach dem F4.3-Schemabump bewusst fail-closed abgewiesen. F4.3 enthält **keine** stille v2→v3-Backupmigration und behauptet keine Rückwärtskompatibilität.

Ein v2-Backup muss entweder mit der dazugehörigen v2-Laufzeit restauriert oder in einem separaten, test- und reviewgebundenen Migrationsgate konvertiert werden. Die technische Ablehnung eines v2-Bundles ist beabsichtigt und kein stiller Datenverlustpfad.

## 6. Review- und Gatezustand

Frühere Review-Snapshots sind wegen nachfolgender Härtung ungültig. Ausschließlich der finale Batch `deleg_8e9bbfb0` ist gatewirksam:

- Security-/Atomicity-Review: **APPROVE**, hohe Konfidenz, keine P0–P3;
- Daten-/Contract-/Schema-Review: **APPROVE**, hohe Konfidenz, keine P0–P3;
- Hashprüfung jeweils am Anfang und Ende ohne Drift;
- keine Reviewer-Mutation, Test-, Server- oder Netzwerkaktivität.

Finale Verifikation:

- F4.3-Fokus: `29 passed`;
- Validation plus F4.3: `44 passed`;
- gesamte Adminmatrix: `323 passed, 5 skipped` mit `-W error`;
- breite Regression: `803 passed, 7 skipped` plus exakt 14 bekannte Baselinefehler;
- Top-5-Smoke: `1 passed`;
- Ruff, `py_compile`, Schemafingerprint und `git diff --check`: PASS;
- `data/remedies.db` blieb bei SHA-256 `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`.

Externe Post-State-ShadowCopy:

```text
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260714_204833_feedback_f_F4_3_GO_post
```

Sie wird nach dem dokumentationsgebundenen Snapshotreview erzeugt und über ihr Manifest vollständig zurückverifiziert.

**Aktuelle Entscheidung: F4.3 = GO.**

Nächster zulässiger Block ist F4.4. Produktive Aktivierung, Runtimeumschaltung und Netzwerk bleiben NO-GO.
