# Feedback a - Einheitliches Workbench-Reportdesign

Stand: 2026-07-18
Branch: `operator-workbench-phase1`
Basis-Checkpoint: `730da8e feat: checkpoint operator workflow gates`

## Entscheidung

Feedback a ist technisch umgesetzt: HTML-Reports verwenden eine gemeinsame Report-Schale im Look der Operator Workbench. Die Aenderung ist bewusst auf Darstellung, HTML-/PDF-Theme und Regressionstests begrenzt; Analyseinhalte, Scoreberechnung, Exportpfade, Manifestregistrierung und Runtime-Gates bleiben unveraendert.

## Umgesetzter Scope

| Bereich | Umsetzung |
|---|---|
| Gemeinsames HTML-Theme | `tools.reporting_common.REPORT_THEME_ID`, `report_theme_css()`, `report_document_start()`, `report_document_end()` und `render_report_header()` |
| Legacy-/Toolberichte | `render_legacy_html()` rendert Deutung, Synergy, Remedy und Trend ueber dieselbe Workbench-Schale |
| Multiplex-Hauptbericht | `_render_basic_html()` nutzt denselben Dokumentrahmen statt eigener alter Blau-/Glas-Schale |
| Reportkoerper | Alte Inline-Farb-/Kartenreste in Synergy-, Remedy- und Multiplex-Abschnitten wurden auf gemeinsame Klassen zurueckgefuehrt |
| PDF-Layout | `tools/pdf_exporter.py` nutzt die Workbench-nahe Palette fuer Text, Akzente, Header, Tabellen und Statusfarben |

## Designvertrag

- Palette: `paper/surface/sage/teal/terracotta` analog Workbench.
- Report-Karten und Tabellen: 8px-Radius, kompakte Flaechen, klare Linien.
- Keine alte dominante Blau-/Glas-Schale in aktiven Report-Renderern.
- Keine negative Laufweite im Report-Theme.
- Dynamische Scrollhoehen bleiben inline, weil sie datenabhaengig berechnet werden.

## Verifikation

| Gate | Ergebnis |
|---|---|
| RED-Vertrag | Import-/Theme-Tests brachen vor Implementierung erwartungsgemaess an fehlendem `REPORT_THEME_ID` |
| Fokussierte Reporttests | `16 passed in 0.64s` und nach Quote-Korrektur `16 passed in 0.83s` |
| Erweiterte Report-/Web-Regression | `56 passed in 113.46s` |
| Syntax | `py_compile` fuer geaenderte Reportmodule erfolgreich |
| Diff-Hygiene | `git diff --check` erfolgreich; nur bekannte LF/CRLF-Warnungen |
| Theme-Scan | Aktive Report-Renderer frei von alten `#6BA5D0`/`#E8F1F8`/Purple-Inline-Markern; verbleibende Treffer nur in nicht betroffenen Workflow-/Workbench-CSS-Dateien |

## Nicht freigegeben

- Kein Merge.
- Kein Push.
- Keine Produktivfreigabe.
- Keine Aenderung an Admin-Catalog- oder Runtime-Wirkung.
