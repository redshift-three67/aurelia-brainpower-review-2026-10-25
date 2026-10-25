# Radi144 Restore-/Packaging-Sonderfall-Audit

Stand: 2026-06-06
Projektwurzel: `/home/klaus999/projects/Radi144`
Gepruefte Sonderfaelle:

- `create_restore_point.py`
- `create_restore.ps1`
- `finalize_project.py`

## 1. Zielbild Radi144

Radi144 ist die Weiterentwicklung des urspruenglichen Prototyps und soll zwei Rollen gleichzeitig erfuellen:

1. **Standalone-System:** lokal lauffaehig, voll funktional und stabil gemaess Nutzeranforderungen.
2. **Referenz-/Informationsmodul:** akkurate, praezise und nachvollziehbare Informationsquelle fuer das uebergeordnete Radionik-Wellbeing-/Radiquant-Projekt.

Konsequenz fuer die Baseline:

- Produktiver Standalone-Code und Referenzdaten sollen erhalten und kuratiert baselinefaehig gemacht werden.
- Historische, stale oder in-repo kopierende Restore-/Packaging-Skripte duerfen nicht als aktueller Betriebsstandard in die Initial-Baseline rutschen.
- Backup-/Recovery muss reproduzierbar, datenschutzbewusst und ausserhalb des Projektbaums stattfinden.

## 2. Sicherheitsgrenze

Nicht veraendert:

- Kernengine
- Resonanzscore
- Matrixlogik
- DB-Ranking
- EMF-/Audio-/Harmonizer-Funktion
- Runtime JSON-Daten
- `db_import/` Inhalte
- Secret-/Deploy-Werte

Die geprueften Skripte wurden nicht ausgefuehrt.

## 3. Befund: `create_restore_point.py`

Statischer Befund:

- Python-Skript fuer `Codegeau v1.4.9.1` / `Pre-Bugfix` RestorePoints.
- Schreibt in projektlokales `RestorePoints/`.
- Kopiert den Projektbaum mit manuell gepflegten Ignore-Patterns.
- Enthält veraltete Versions-/Feature-Texte:
  - `v1.4.9.1`
  - `Pre-Bugfix Snapshot`
  - bekannte alte Issues wie `PkADDING typo`, `$u_ae/$u_ue variables undefined`, `REST API not updated`.
- Ignoriert `Analysen`, aber nicht alle heute bekannten sensiblen lokalen Runtime-/Session-Dateien explizit.

Bewertung:

Nicht als aktueller Standalone-/Referenzmodul-Baselinebestand aufnehmen. Das Skript dokumentiert historische Restore-Logik, ist aber durch den aktuellen externen ShadowCopy-Prozess ersetzt.

## 4. Befund: `create_restore.ps1`

Statischer Befund:

- PowerShell-Variante des RestorePoint-Erzeugers.
- Schreibt ebenfalls in projektlokales `RestorePoints/`.
- Versioniert als `v1.4.9.1 Pre-Bugfix`.
- Verwendet `Copy-Item -Recurse -Exclude` mit statischen Exclude-Patterns.
- Enthält denselben veralteten Recovery-/Known-Issue-Block.

Bewertung:

Nicht als aktueller Windows-Betriebsstandard aufnehmen. Windows-Standalone-Faehigkeit bleibt wichtig, aber diese Datei ist historisch/stale und kein moderner, datenschutzbewusster Restore-Mechanismus.

## 5. Befund: `finalize_project.py`

Statischer Befund:

- Setzt `VERSION = "1.5.0"`, schreibt aber eine eingebettete `COMPLETE_SYSTEM_DESCRIPTION.md` mit `Version 1.4.9` und `Finalized & Validated`.
- Schreibt direkt in die Projektwurzel.
- Erstellt anschliessend projektlokale RestorePoints.
- Enthält historische Architektur-/Feature-Texte, die nicht als aktuelle SSOT-Dokumentation gelten duerfen.
- Kopiert Projektdateien mit statischen Excludes und kann dadurch lokale Daten unvollstaendig schuetzen.

Bewertung:

Nicht baselinefaehig. Das Skript vermischt Dokumentgenerierung, Release-/Finalisierung und Backup. Das widerspricht dem aktuellen vorsichtigen, phase-gated Standalone-/Referenzmodul-Zielbild.

## 6. Baseline-Entscheidung

Diese Dateien werden aus der initialen Git-Baseline ausgeschlossen und in `.gitignore` aufgenommen:

- `create_restore_point.py`
- `create_restore.ps1`
- `finalize_project.py`

Begruendung:

1. Stale Versions-/Pre-Bugfix-Kontext.
2. Projektinterne RestorePoints statt externer ShadowCopies.
3. Potenzielles Risiko, lokale Runtime-/Session-/Analyse-Daten unvollstaendig auszuschliessen.
4. Vermischung von Backup, Release, Dokumentation und Packaging.
5. Nicht erforderlich fuer die aktuelle Standalone-Lauffaehigkeit.
6. Nicht geeignet als Referenz fuer das uebergeordnete Wellbeing/Radiquant-Projekt.

## 7. Zukunftsempfehlung

Spaeter sinnvoll, aber nicht in dieser Phase:

- neues, bewusstes `scripts/maintenance/create_shadowcopy.py` oder aehnliches Wartungstool entwickeln,
- Ziel ausserhalb des Projektbaums erzwingen,
- sensible Runtime-/Session-/Analyse-/Secret-Pfade standardmaessig ausschliessen,
- Manifest mit SHA256-Dateiliste erzeugen,
- Restore-Anleitung aus aktuellen SSOT-Dokumenten ableiten,
- Tests fuer Ausschlussregeln und Manifest-Integritaet schreiben.

Das sollte erst nach initialer Baseline oder als eigene TDD-Phase erfolgen.

## 8. Automatisierter Guard

Erweitert wurde:

- `tests/test_repository_data_hygiene.py`

Neue Regel:

- `create_restore_point.py`, `create_restore.ps1` und `finalize_project.py` muessen ausserhalb der initialen Baseline bleiben.

TDD-Verlauf:

- RED: Der neue Test schlug zuerst fehl, weil `create_restore_point.py` noch nicht ignoriert war.
- GREEN: Nach `.gitignore`-Erweiterung muss der Test gruen sein.

## 9. Naechste Prioritaet

Nach Abschluss dieser Phase ist die Baseline-Kuratierung inhaltlich weit genug, um als naechsten Schritt keine weitere Blindklassifizierung, sondern eine explizite Initial-Baseline-Vorbereitung zu machen:

1. Gitstatus vollstaendig aufnehmen.
2. Baseline-Gruppen in Reihenfolge vorbereiten.
3. Noch keinen Commit ohne ausdrueckliche Freigabe.
4. Vor jedem Commit: fokussierte Tests + full pytest + Port-/Prozesshygiene.
