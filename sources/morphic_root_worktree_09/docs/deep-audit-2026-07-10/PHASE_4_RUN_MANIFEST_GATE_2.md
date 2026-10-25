# Phase 4 – Gate 2: Explizite Run-Manifest-Hashquellen

**Status:** Read-only Hashquellen grün; weiterhin keine Laufverdrahtung.
**Ziel:** Commit-, Profil- und Datenhashes können für einen späteren Run-Manifest-
Writer explizit übergeben und deterministisch ermittelt werden.

## Implementierte Grenze

`core/compliance/run_manifest_sources.py` enthält zwei read-only Helfer:

- `resolve_git_commit(project_root)` liest ausschließlich den vollständigen
  `git rev-parse HEAD`-Commit eines expliziten Repositoryroots.
- `collect_source_hashes(profile_sources=..., data_sources=...)` hasht nur die
  explizit übergebenen regulären Dateien und liefert getrennte Profil-/Datenmaps.

Es werden keine Standard- oder Exportpfade geraten. Fehlende oder symbolische
Quellen sowie nichtkanonische Namen schlagen fail-closed fehl. Die Hashquelle
ist damit vor einer späteren Integration nachvollziehbar, ohne dass der aktuelle
Scan Daten lesen, Parameter ändern oder Artefakte erzeugen muss.

## TDD-Nachweis

`tests/test_run_manifest_sources.py` wurde vor dem Modul erstellt und erzeugt
nur temporäre, synthetische Dateien sowie ein temporäres Git-Repository. Er
belegt stabile Map-Sortierung, Inhaltsänderungsdetektion, Missing-Source-
Abweisung und einen echten 40-stelligen Commit.

## Nicht geändert

Kein Scanner, Launcher, Reportwriter, Runtime-Manifest, Workbench-Trace oder
Web-Jobstore ruft diese Helfer auf. Reale Profil-/Gruppen-/Datenbankquellen
wurden nicht geöffnet oder gehasht. Die spätere Zuordnung solcher Quellen ist
ein eigener Integrationsentscheid mit fachlichem Scope.

## Nächster Gate

Ein nachfolgender, separater Test muss eine kleine explizite Quellenliste für
einen konkreten erfolgreichen Scanpfad festlegen, den Builder damit versorgen
und nach Laufende ein neues Manifest schreiben. Erst dann dürfen reale
Artefakthashes, redigierte Commands und Recovery-Metadaten folgen.
