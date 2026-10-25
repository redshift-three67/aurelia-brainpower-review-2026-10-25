# Worktree Inventory 2026-06-29

Dieses Inventar beschreibt den Stand nach der Wiederaufnahme der abgebrochenen
Windows-Session. Es ist bewusst nicht destruktiv: Es wurden keine bestehenden
Loeschungen, untracked Dateien oder fremden Aenderungen zurueckgesetzt.

## Aktuelle absichtliche Stabilisierungsaenderungen

| Bereich | Dateien | Zweck |
|---|---|---|
| Source-Datenpromotion | `core/source_data_promotion.py`, `apps/cli/commands/sources.py`, `tests/test_source_data_promotion.py`, `tests/test_source_registry_cli.py` | Validiertes Staging und append-only Promotion-Ledger fuer konkrete Source-Datenbatches; CLI `sources data-stage` und `sources data-promote`. |
| Offline-3D-Viewer | `apps/viewer/index.html`, `core/viewer_3d.py`, `tests/test_viewer_offline.py` | Entfernt CDN-Abhaengigkeiten; statischer Viewer und generierter HTML-Viewer laufen als selbstenthaltene Canvas-Viewer. |
| Report-/CLI-Textsauberkeit | `apps/cli/commands/field.py`, `tests/test_report_text_cleanliness.py` | Sichtbare Feldtest-/Multiplex-Ausgaben und HTML/TXT-Exports werden auf typische mojibake-Artefakte bereinigt. |
| Laufende Stabilisierung | `docs/STABILIZATION_TEST_MATRIX.md`, `docs/SESSION_HANDOFF_20260628.md`, dieses Inventar | Dokumentiert die neuen Gates und den nicht aufgeraeumten Worktree-Zustand. |

## Vorbestehender Dirty-Worktree-Zustand

`git status --short` zeigt weiterhin sehr viele Aenderungen ausserhalb der oben
genannten Arbeit. Auffaellig sind:

- zahlreiche `D`-Eintraege unter `imports/`, `venv/`, Legacy-Skripten und alten
  Analyse-/Hilfsdateien;
- viele untracked Test-, Doku-, Runtime- und Archivdateien;
- bestehende Aenderungen an CLI-, Core-, Provider-, Service- und Tool-Modulen,
  die aus der laufenden Stabilisierung vor dieser Wiederaufnahme stammen.

Diese Eintraege wurden nicht bereinigt, weil nicht sicher ist, welche davon vom
Nutzer absichtlich vorbereitet wurden. Eine spaetere Konsolidierung sollte in
separaten Schritten erfolgen.

## Erzeugter Preview-Report

Fuer den direkten Layoutvergleich wurde eine kleine Mustermann-Testanalyse im
Workspace-Tempbereich erzeugt:

```text
C:\Morphic_v1\codex_tmp\Morphic_Mustermann_Test_20260629\Mustermann_Klaus_09041966_Augsburg\20260629_103647_SINGLE\
```

Enthalten sind JSON, HTML, PDF, TXT, Hoch-/Mittel-Labels und `*_3d_scan.json`.
Ein `rg`-Check ueber HTML/TXT fand keine typischen mojibake-Marker.

Nach der Tabellenangleichung wurde zusaetzlich ein aktueller TOP9-Strukturlauf
erzeugt:

```text
C:\Morphic_v1\codex_tmp\Morphic_Mustermann_Top9_20260629\
```

Dieser Lauf enthaelt Resonanz-, Deutungs-, Remedy-, Synergy- und Trendbereiche.
Der Vergleich zur Originalstruktur ist in
`docs/MUSTERMANN_REPORT_COMPARISON_20260629.md` dokumentiert.

Nach der Deutungsfixierung wurde der aktuellste Deutungsbericht neu erzeugt:

```text
C:\Morphic_v1\codex_tmp\Morphic_Mustermann_Top9_20260629\Mustermann_Klaus_09041966_Augsburg_Deutung\20260629_105923_top9\
```

Nach der Detailangleichung der konsolidierten Berichte wurden zusaetzlich diese
aktuellen Artefakte erzeugt:

```text
C:\Morphic_v1\codex_tmp\Morphic_Mustermann_Top9_20260629\Mustermann_Klaus_09041966_Augsburg_Synergy\20260629_111057_synergy_report\
C:\Morphic_v1\codex_tmp\Morphic_Mustermann_Top9_20260629\Mustermann_Klaus_09041966_Augsburg_Remedies\20260629_111427_top9_remedies.html
```

## Empfohlene spaetere Commit-Gruppierung

1. Aktuelle Stabilisierung: Source-Datenpromotion, Offline-Viewer,
   Report-Textsauberkeit und zugehoerige Tests.
2. Dokumentation: aktualisierte Testmatrix, Handoff und dieses Inventar.
3. Separat entscheiden: grosse Loeschserien unter `imports/` und `venv/`,
   generierte Benutzerarchive und alte Legacy-Skripte.

## Verifikation fuer diesen Stand

Mindestens auszufuehren:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_viewer_offline.py tests\test_source_data_promotion.py tests\test_source_registry_cli.py tests\test_report_text_cleanliness.py -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m apps.cli.main health --strict
.\.venv\Scripts\python.exe -m apps.cli.main sources validate
```
