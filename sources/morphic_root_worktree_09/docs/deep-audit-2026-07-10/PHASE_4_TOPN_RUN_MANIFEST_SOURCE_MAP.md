# Phase 4 – Gate 3 Vorbereitung: Quellenkarte für Top-N-Läufe

**Status:** Read-only Callgraph- und Quellenentscheidung dokumentiert; keine
Produktivverdrahtung und kein neuer Manifest-Writer.
**Geltung:** Aktueller CLI-Pfad `scan top3-scan` mit seinen aufgerufenen
`field multiplex-scan`-Unterläufen.

## 1. Nachgewiesene Quellen

| Manifestschlüssel | Explizite Quelle | Beleg | Entscheidung |
|---|---|---|---|
| `software.commit` | Git-Root des gestarteten Projekts | `core/compliance/run_manifest_sources.py:resolve_git_commit` | Voller `HEAD`-Commit |
| `profile_hashes.topn_profile_catalog` | `core/profile_sync/__init__.py` | `apps/cli/commands/scan.py:1193-1200`; Profilregister bezeichnet sich selbst als zentrale Quelle | SHA-256 der Datei |
| `profile_hashes.phase1_template_rules` | `apps/cli/commands/scan.py` | `_phase1_template_values` und `_build_phase1_cli_option_args` ab Zeile 422 sowie Top-N-Übergabe ab Zeile 1178 | SHA-256 der Datei, bis die Regeln in ein separates Datendokument ausgegliedert werden |
| `data_hashes.procedural_group_catalog` | `core/subgroups/procedural_groups.py` | `services/subgroup_service.py:14-23` delegiert die Kandidatenerzeugung direkt dorthin | SHA-256 der Datei |
| `data_hashes.subgroup_dispatch` | `services/subgroup_service.py` | alleinige Fassade im Top-N-nahen Scanpfad | SHA-256 der Datei |

Die Quellenliste beschreibt Programm- und Kataloggrundlagen, nicht Klientendaten.
Sie ist absichtlich klein: Nur Dateien, deren Änderung die Profilwahl,
Profilparameter oder prozeduralen Kandidaten beeinflussen kann, gehören in den
Erst-Manifestumfang.

## 2. Ausdrücklich nicht aufnehmen

- `name`, `first_name`, `birth_date`, `birth_place`, `focus`, Bildpfade oder der
  aus diesen Werten gebildete Seed; dies wären PII oder rückführbare Ableitungen.
- Entropieproben, Hardwarewerte und volatile Laufzeitwerte; der Erstumfang führt
  nur `seed_mode`, nicht den Seed oder dessen Material.
- Export-, Report-, Archiv-, Runtime- und Web-Jobpfade; sie werden erst nach
  erfolgreicher Laufende als separat gehashte Artefakte behandelt.
- `tools/group_manager.py` und lokale `config/groups_config.json`: Der geprüfte
  `top3-scan`-Pfad verwendet für die Kandidaten `SubgroupService`, nicht diesen
  administrativen Gruppenmanager.
- Beschreibungs- und Remedy-SQLite-Datenbanken: Sie sind nicht Teil des
  nachgewiesenen Top-N-Scorings und müssen nicht vorsorglich gelesen werden.

## 3. Integrationsgrenze für Gate 3

Der spätere Writer darf ausschließlich nach vollständig erfolgreichem Top-N-Lauf
aufgerufen werden. Er erhält den Commit über `resolve_git_commit(...)` und die
oben genannte Quellenliste über `collect_source_hashes(...)`; anschließend baut
`build_run_manifest(...)` das pseudonyme Objekt.

Vor dem eigentlichen Schreiben sind noch separat zu testen:

1. Kein Manifest bei fehlgeschlagenem oder abgebrochenem Lauf.
2. Manifest enthält nur `stable_client_id`/Tenant-ID, niemals CLI-Klartext.
3. Gehashte Ausgabeartefakte werden erst nach ihrem erfolgreichen Abschluss
   angehängt.
4. Default-Score, Launcher-Argumente und vorhandene Exportdateien bleiben byte-
   bzw. verhaltensäquivalent.

Bis zu diesen RED/GREEN-Tests bleibt der Builder vollständig entkoppelt.
