# Quellen-Registry Bewertung 2026-06-28

## Zielbild

Externe Quellen sollen als Datenquellen registriert werden, aber nur aktiv werden,
wenn ein Administrator sie explizit freischaltet. Die Aktivierung darf keine
direkten Katalogueberschreibungen ausloesen. Jeder Import laeuft zuerst in eine
Staging-/Quarantaene-Schicht, wird validiert, als Diff angezeigt und erst danach
promoted.

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
| Aktivieren/Deaktivieren | umgesetzt | `python -m apps.cli.main sources enable <id>` / `disable <id>` |
| Scope-Filter und JSON-Liste | umgesetzt | `python -m apps.cli.main sources list --scope tcm --json` |
| Admin-Import einzelner Quellen | umgesetzt | `python -m apps.cli.main sources import <manifest.json>` |
| Staging validierter Source-Manifeste | umgesetzt | `python -m apps.cli.main sources stage <manifest.json> --staging-dir <dir>` |
| Dry-Run/Diff vor Registry-Schreibzugriff | umgesetzt | `python -m apps.cli.main sources import <manifest.json> --dry-run` |
| Rollback pro Source-Manifest-Import-Batch | umgesetzt | `--rollback-dir`, `--batch-id`, `python -m apps.cli.main sources rollback <batch>` |
| Quarantined-Schutz fuer Rife/Clark | umgesetzt | Aktivierung nur mit `--allow-quarantined` |
| Online-Download/Adapter | offen | bewusst noch nicht aktiv; naechster Ausbauschritt |
| Fachliche Datenpromotion importierter Quellen | umgesetzt fuer lokale JSON-Batches | `sources data-stage`, `sources data-promote`, Hash-/Record-Count-Pruefung und append-only Ledger |
| Fachliche Mapping-Regeln pro Onlinequelle | offen | NLM/USDA/NCBI brauchen je Quelle eigene Feld-/Lizenz-/Scope-Abbildung |

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

Wichtige CLI-Beispiele:

```powershell
.\.venv\Scripts\python.exe -m apps.cli.main sources list
.\.venv\Scripts\python.exe -m apps.cli.main sources list --scope herbal_medicine --json
.\.venv\Scripts\python.exe -m apps.cli.main sources validate
.\.venv\Scripts\python.exe -m apps.cli.main sources disable nlm_mesh
.\.venv\Scripts\python.exe -m apps.cli.main sources enable nlm_mesh
.\.venv\Scripts\python.exe -m apps.cli.main sources stage C:\Pfad\admin_source.json --staging-dir C:\Pfad\staging
.\.venv\Scripts\python.exe -m apps.cli.main sources import C:\Pfad\admin_source.json --dry-run
.\.venv\Scripts\python.exe -m apps.cli.main sources import C:\Pfad\admin_source.json
.\.venv\Scripts\python.exe -m apps.cli.main sources import C:\Pfad\admin_source.json --rollback-dir C:\Pfad\rollbacks --batch-id batch-001
.\.venv\Scripts\python.exe -m apps.cli.main sources rollback batch-001 --rollback-dir C:\Pfad\rollbacks
.\.venv\Scripts\python.exe -m apps.cli.main sources data-stage C:\Pfad\source_batch.json --staging-dir C:\Pfad\staging
.\.venv\Scripts\python.exe -m apps.cli.main sources data-promote C:\Pfad\staging\nlm_mesh.terminology.batch.json --ledger C:\Pfad\source_data_ledger.json --dry-run
.\.venv\Scripts\python.exe -m apps.cli.main sources data-promote C:\Pfad\staging\nlm_mesh.terminology.batch.json --ledger C:\Pfad\source_data_ledger.json
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
| HTTPS-Allowlist pro Quelle | verhindert beliebige Downloads |
| Kein Codeimport | Repositories liefern nur Daten, nie ausfuehrbaren Code |
| Schema pro Datentyp | Profil-, Gruppen-, Remedy- und Terminologiedaten werden getrennt validiert |
| SHA-256 fuer Dateien | Reproduzierbarkeit und Manipulationsschutz |
| Provenienzpflicht | jeder Datensatz braucht Quelle, Version, Lizenz und Importzeitpunkt |
| Staging vor Promotion | keine automatische Aenderung aktiver Kataloge |
| Admin-Dry-Run | Diff und Fehlerbericht vor Aktivierung |
| Rollback pro Batch | fehlerhafte Imports koennen deaktiviert werden |

## Priorisierte Umsetzung

1. Lokale Profil-/Gruppenintegritaet abschliessen.
2. Source-Manifest-Schema und `enabled/status/scopes` einbauen.
3. Source-Manifest-Staging, Dry-Run/Diff und Rollback als Admin-Sicherheitsblock nutzen.
4. Lokale Source-Datenpromotion jetzt als Sicherheitsblock nutzen und pro Quelle fachliche Mapping-Regeln ergaenzen.
5. Erste offizielle Onlineadapter: NLM MeSH, USDA FoodData Central, NCBI Taxonomy.
6. Danach fachliche Adapter: EMA/NCCIH Kraeuter, WHO ICD-11/Acupuncture, DailyMed/RxNorm.
7. Rife/Clark nicht automatisch online aktivieren; nur als klar markierte lokale,
   experimentelle Datenbank mit Warnhinweis und ohne medizinische Claims.
