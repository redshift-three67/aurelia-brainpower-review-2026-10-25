# Quellen-Registry Bewertung 2026-06-28

## Zielbild

Das spaetere Zielbild sieht registrierte externe Datenquellen und eine getrennte
Adminfreigabe vor. F5-A realisiert davon ausschliesslich Source-Registry-Sicherheit,
Manifest-Staging und ein lokales Batch-Consistency-Ledger. Es uebernimmt keine
Source-Daten in den Catalog, erzeugt keinen Aktivierungsdiff und fuehrt keine
fachliche Promotion aus. Diese Schritte bleiben F5.2/F5.3 und spaeteren Gates vorbehalten.

Die heutige Source-Registry ist keine Onlinefreigabe. Der Metadatenstatus
`active` ist keine Adapterfreigabe, kein Fetch, kein Publish und keine
Runtime-Aktivierung. Onlineadapter, echte Netzwerkfreigaben und Runtimewirkung
bleiben eigenen spaeteren Gates vorbehalten.

## Aktivieren und Deaktivieren

| Funktion | Bewertung | Empfehlung |
|---|---|---|
| Quelle aktivieren/deaktivieren | technisch einfach | `enabled: true/false` im Source-Manifest |
| Nur bestimmte Kategorien aktivieren | gut machbar | `scopes: ["profile", "group", "remedy", "terminology"]` |
| Quelle zeitweise sperren | gut machbar | `status: active/disabled/quarantined/deprecated` |
| Import rueckgaengig machen | mittel | Source-Versionen und Promotion-Batches versionieren |
| Quelle lokal/admin-eigen importieren | gut machbar | Daten-only Import, Schema-Validierung, Hash, Provenienz |

## Implementierungsstand 2026-06-29

| Baustein | Status | Datei/Command |
|---|---:|---|
| Validiertes Source-Manifest | umgesetzt | `core/source_registry.py` |
| Standard-Registry mit offiziellen Quellen | umgesetzt | `config/source_repositories.json` |
| Legacy-v1-Registry ohne Revision/History | bewusst read-only | Lesen und `import-plan` bleiben möglich; Enable/Disable, Manifest-Staging und Import verlangen zuerst eine explizit revisionsfähige Migration. Die produktive Datei wird nicht still umgeschrieben. |
| Aktivieren/Deaktivieren | umgesetzt | `python -m apps.cli.main sources enable <id>` / `disable <id>` |
| Scope-Filter und JSON-Liste | umgesetzt | `python -m apps.cli.main sources list --scope tcm --json` |
| Admin-Import einzelner Quellen | umgesetzt | `python -m apps.cli.main sources import <source-stage.json>` |
| Staging validierter Source-Manifeste | umgesetzt | `python -m apps.cli.main sources stage <manifest.json> --staging-dir <dir> --approval-id <id>` |
| Schreibfreier Diff vor Staging/Import | umgesetzt | `python -m apps.cli.main sources import-plan <manifest.json>` |
| Rollback pro Source-Manifest-Import-Batch | umgesetzt | `--rollback-dir`, `--batch-id`, `python -m apps.cli.main sources rollback <batch>` |
| Quarantined-Schutz fuer Rife/Clark | umgesetzt | Aktivierung nur mit `--allow-quarantined` |
| Online-Download/Adapter | offen | bewusst noch nicht aktiv; naechster Ausbauschritt |
| Source-Batch-Konsistenzprotokoll | umgesetzt fuer lokale JSON-Batches | `sources data-stage`, `sources data-record-consistency`, versioniertes Schema `morphic_source_data_consistency_ledger` v3, vollstaendige Hashbindung und atomar neu geschriebenes, validiertes JSON-Ledger mit Replay-Erkennung; kein Catalog-Publish. `data-promote` ist nur ein sichtbar deprecateter Alias. |
| Fachliche Mapping-Regeln pro Onlinequelle | offen | NLM/USDA/NCBI brauchen je Quelle eigene Feld-/Lizenz-/Scope-Abbildung |

Registry-Imports sind JSON-Read-Modify-Write mit atomarem Replace und
Rollback-Snapshot; sie sind nicht technisch append-only. Das lokale
Source-Batch-Konsistenzprotokoll ist Ledger-only: Es schreibt ausschliesslich
den Konsistenznachweis fuer ein gestagtes lokales Batch und ist keine fachliche Datenpromotion.

Minimaler Manifest-Entwurf:

```json
{
  "id": "nlm_mesh",
  "label": "NLM MeSH",
  "enabled": false,
  "status": "disabled",
  "source_type": "online_download",
  "trust_level": "official",
  "homepage": "https://www.nlm.nih.gov/mesh/meshhome.html",
  "download_url": "https://www.nlm.nih.gov/databases/download/mesh.html",
  "scopes": ["terminology", "tcm", "acupuncture"],
  "license": "source-specific",
  "import_policy": "manual_review"
}
```

Die produktive `config/source_repositories.json` bleibt als Legacy-v1-Authority
read-only. F5-A stellt absichtlich keinen automatischen Migrationsbefehl bereit.
Für Schreibpfade muss ein Administrator zuerst eine geprüfte Arbeitskopie mit
exakt dem Wrapper `schema_version`, `revision: 0`, `rollback_history: []` und
`sources` erstellen und deren Diff freigeben. Die folgenden Schreibbeispiele
verwenden deshalb ausdrücklich `C:\Pfad\source_repositories.v1.json`; sie dürfen
nicht gegen die produktive Legacy-Datei ausgeführt werden.

Neue Source-IDs dürfen über F5-A ausschließlich deaktiviert mit der serverseitigen
Least-Privilege-Policy `trust_level: experimental_unverified` und
`import_policy: reference_only` aufgenommen werden; die Lizenz ist für `local_import`
`admin-provided`, sonst `source-specific`. Bei bestehenden Source-IDs sind diese drei
Policyfelder durch das aktuelle Registryobjekt gebunden und über Manifestreplacement
nicht änderbar. Eine Aufwertung braucht ein separates, noch nicht freigegebenes Approval-Gate.

Wichtige CLI-Beispiele:

```powershell
.\.venv\Scripts\python.exe -m apps.cli.main sources list
.\.venv\Scripts\python.exe -m apps.cli.main sources list --scope herbal_medicine --json
.\.venv\Scripts\python.exe -m apps.cli.main sources validate
.\.venv\Scripts\python.exe -m apps.cli.main sources import-plan C:\Pfad\admin_source.json
.\.venv\Scripts\python.exe -m apps.cli.main sources disable nlm_mesh --registry C:\Pfad\source_repositories.v1.json
.\.venv\Scripts\python.exe -m apps.cli.main sources enable nlm_mesh --registry C:\Pfad\source_repositories.v1.json
.\.venv\Scripts\python.exe -m apps.cli.main sources stage C:\Pfad\admin_source.json --staging-dir C:\Pfad\staging --approval-id approval-001 --registry C:\Pfad\source_repositories.v1.json
.\.venv\Scripts\python.exe -m apps.cli.main sources import C:\Pfad\staging\admin_notes.HASH.source-stage.json --registry C:\Pfad\source_repositories.v1.json
.\.venv\Scripts\python.exe -m apps.cli.main sources import C:\Pfad\staging\admin_notes.HASH.source-stage.json --rollback-dir C:/Pfad/rollbacks --batch-id batch-001 --registry C:\Pfad\source_repositories.v1.json
.\.venv\Scripts\python.exe -m apps.cli.main sources rollback batch-001 --rollback-dir C:/Pfad/rollbacks --expected-revision 1 --registry C:\Pfad\source_repositories.v1.json
.\.venv\Scripts\python.exe -m apps.cli.main sources data-stage C:\Pfad\source_batch.json --staging-dir C:\Pfad\staging --registry C:\Pfad\source_repositories.v1.json
.\.venv\Scripts\python.exe -m apps.cli.main sources data-record-consistency C:\Pfad\staging\nlm_mesh.terminology.HASH.batch.json --ledger C:\Pfad\source_data_ledger.json --registry C:\Pfad\source_repositories.v1.json --dry-run
.\.venv\Scripts\python.exe -m apps.cli.main sources data-record-consistency C:\Pfad\staging\nlm_mesh.terminology.HASH.batch.json --ledger C:\Pfad\source_data_ledger.json --registry C:\Pfad\source_repositories.v1.json
```

## Quellenkandidaten

| Thema | Quelle | Eignung | Standardstatus |
|---|---|---|---|
| Medizinische Terminologie, Profile, Gruppen | NLM MeSH | sehr gut fuer kontrollierte Begriffe und Hierarchien | optional aktivierbar |
| Arzneimittel/Drug Labels | DailyMed, RxNorm, openFDA | sehr gut fuer Arzneinamen, Label, NDC/RxCUI; keine Therapievalidierung | optional aktivierbar |
| TCM / traditionelle Medizin | WHO ICD-11 Traditional Medicine, WHO Standardterminologien | gut fuer Taxonomie/Begriffe; keine Wirksamkeitsbehauptung | optional aktivierbar |
| Akupunktur | WHO Standard Acupuncture Point Locations, NCCIH | gut fuer Punkte/Nomenklatur und Evidenz-/Sicherheitshinweise | optional aktivierbar |
| Laserakupunktur | NCCIH, PubMed/MeSH | nur Evidenz-/Literaturbezug; kein stabiler Punktdaten-Import noetig | disabled, spaeter pruefen |
| Nahrung / Naehrstoffe | USDA FoodData Central | sehr gut, API und CC0, aber API-Key erforderlich | optional aktivierbar |
| Allergene / Unvertraeglichkeiten | FDA Food Allergies, MeSH | gut fuer Allergenlisten und Begriffssystematik | optional aktivierbar |
| Strahlung / EMF | WHO EMF, ICNIRP, CDC/FDA Radiation | gut fuer Schutz-/Belastungsbegriffe; keine morphische Bewertung | optional aktivierbar |
| Parasiten, Viren, Bakterien | NCBI Taxonomy, CDC Parasites, MeSH | sehr gut fuer Taxonomie und Pathogen-Namen | optional aktivierbar |
| Kraeuterheilkunde | EMA/HMPC, NCCIH Herbs at a Glance, WHO Monographs | gut fuer Monographien, Sicherheit, Interaktionen | optional aktivierbar |
| Rife-Frequenzen | keine belastbare offizielle medizinische Quelle gefunden | nur als historische/experimentelle Admin-Datenquelle | disabled by default |
| Clark-Frequenzen/Zapper | FTC/FDA warnen vor unbelegten Gesundheitsclaims | nicht als vertrauenswuerdige Onlinequelle; nur lokale Altlast mit Warnlabel | disabled/quarantined |

## Sicherheitsregeln

| Regel | Zweck |
|---|---|
| HTTPS-Praefixpruefung pro deklarierter URL | lehnt nicht verschluesselte URL-Schemata ab; keine Host-Allowlist |
| Lokaler Pfad nur Point-in-time-Plan | F5-A liest keine Quelldaten. Ein spaeterer Consumer muss den Pfad am echten I/O-Boundary ueber einen nicht loesch-/umhaengbaren Handle revalidieren und in einen privaten Snapshot kopieren. |
| Kein Codeimport | Repositories liefern nur Daten, nie ausfuehrbaren Code |
| Schema pro Datentyp | geplant fuer F5.2; F5-A besitzt nur den generischen, exakt gehashten Batch-Envelope mit `id`/`label`-Records |
| SHA-256 fuer Dateien | Reproduzierbare Konsistenzpruefung; ohne externen Vertrauensanker kein Schutz gegen absichtliches lokales Neuschreiben |
| Provenienzpflicht je Record | geplant fuer F5.2; F5-A bindet Source, Version, Lizenz und Retrieval-Metadaten auf Batch-Ebene |
| Staging vor Consistency-Ledger | keine automatische Aenderung aktiver Kataloge und kein Catalog-Publish |
| Replay-Grenze | Replay-Erkennung gilt innerhalb des intakten aktuellen Ledgers; ohne externen Signatur-/HMAC-Anker ist absichtliche lokale Ledger-Loeschung oder -Kuerzung nicht beweissicher |
| `active`-Grenze | Metadatenstatus `active` ist keine Adapterfreigabe, kein Fetch, kein Publish und keine Runtime-Aktivierung |
| Admin-Dry-Run | Manifest-Diff beziehungsweise Ledger-Plan ohne Schreibzugriff; keine Aktivierung |
| Rollback-Grenze | Rollback gilt nur fuer Source-Manifest-Registry-Imports; das F5-A-Consistency-Ledger besitzt keinen Source-Daten-Rollback |

## Priorisierte Umsetzung

1. Lokale Profil-/Gruppenintegritaet abschliessen.
2. Source-Manifest-Schema und `enabled/status/scopes` einbauen.
3. Source-Manifest-Staging, Dry-Run/Diff und Rollback als Admin-Sicherheitsblock nutzen.
4. Lokales Source-Batch-Konsistenzprotokoll als Sicherheitsblock nutzen und vor echter Datenuebernahme pro Quelle fachliche Mapping-Regeln sowie handle-basiertes lokales Snapshotting ergaenzen.
5. Erste offizielle Onlineadapter: NLM MeSH, USDA FoodData Central, NCBI Taxonomy.
6. Danach fachliche Adapter: EMA/NCCIH Kraeuter, WHO ICD-11/Acupuncture, DailyMed/RxNorm.
7. Rife/Clark nicht automatisch online aktivieren; nur als klar markierte lokale,
   experimentelle Datenbank mit Warnhinweis und ohne medizinische Claims.
