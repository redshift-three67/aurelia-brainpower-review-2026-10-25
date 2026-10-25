# Workflows, Phasen Und Schritte

## 1. Aktuelle reale Workflow-Modelle

Das Projekt besitzt aktuell **drei** relevante Workflow-Realitaeten.

### A. Produktiver Top-N-Scan

Hauptpfad:

- `scan top3-scan`
- `field multiplex-scan`

Merkmale:

- produktionsnahe CLI-/Web-Kopplung
- Report- und Exportpfad historisch gewachsen
- Webstatus wird weitgehend aus Job-/CLI-Kontext rekonstruiert

### B. 12-Step-Orchestrator

Pfad:

- `apps/cli/workflow/*`
- `apps/web/analyze.py`

Merkmale:

- eigener fachlicher Schrittpfad
- nicht identisch mit dem Web-Hauptpfad
- aktuell eher paralleles Orchestrierungsmodell

### C. Aktuelle 8-Step-Web-Shell

Pfad:

- `apps/web/static/index.html`
- `apps/web/static/app.js`

Aktuelle 8 Schritte:

1. Preflight
2. Hinweise
3. Klientenaufnahme
4. Fokus
5. Scan-Profil
6. Analysefreigabe
7. Berichte
8. Harmonisierung

## 2. Geplantes Zielmodell

Freigegebenes Ziel laut aktueller Design-Spezifikation:

- `docs/superpowers/specs/2026-07-05-morphic-operator-workbench-design.md`

Ziel: `Operator Workbench` mit 10 Phasen.

Geplante 10 Phasen:

1. Runtime & Workspace
2. Klient / Kontext
3. Fokus & Zielsetzung
4. Analyseprofil
5. Hardware & Realtime
6. Review & Freigabe
7. Analyse-Lauf
8. Ergebnis-Uebersicht
9. Technische Details & Nachvollziehbarkeit
10. Harmonisierung & Export

## 3. Aktueller Implementierungsstand dieses Zielmodells

### Bereits im Worktree backend-seitig vorhanden

- Registry fuer 10 Phasen
- Hardware-Truth-API
- Runtime-backed Draft-/Template-/Run-Trace-Persistenz

### Noch nicht vorhanden

- echte 10-Phasen-Frontend-Shell
- Review-Gate im Frontend
- Result Workspace
- finale 10-Phasen-Navigation in `apps/web/static/*`

## 4. Bedeutende Differenz zwischen Ist und Ziel

Derzeit existiert das Zielmodell **noch nicht als aktive Benutzeroberflaeche**, sondern nur als:

- freigegebenes Design,
- detaillierter Implementierungsplan,
- und teilweise umgesetztes Backend-Grundgeruest im Worktree.

## 5. Wichtige Entwicklerfolgerung

Jeder Entwickler muss derzeit klar unterscheiden zwischen:

- `der heute sichtbaren 8-Step-Produktoberflaeche`
- `dem 12-Step-Erklaer-/Alternativpfad`
- `der im Worktree vorbereiteten 10-Phasen-Zielarchitektur`

Diese drei Ebenen duerfen nicht miteinander verwechselt werden.
