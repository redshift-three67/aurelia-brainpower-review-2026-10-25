# Risiken, Drift Und Naechste Punkte

## 1. Dokumentationsdrift

Die staerkste nicht-funktionale Schwachstelle des Projekts ist derzeit die Drift zwischen:

- altem README-/PROJECT_MEMORY-Narrativ,
- realem Codezustand,
- lokalem Haupt-Checkout,
- aktivem Worktree,
- und den neuesten freigegebenen Designs/Plans.

## 2. Architekturdrift

Das Projekt hat weiterhin mehrere konkurrierende Ablaufmodelle:

1. produktiver Top-N-CLI-Pfad
2. 12-Step-Orchestrator
3. aktuelle 8-Step-Web-Shell
4. geplante 10-Phasen-Operator-Workbench

Bis die Workbench fertig und kanonisch ist, bleibt dies ein zentrales Verstaendigungs- und Wartungsrisiko.

## 3. Sicherheits- und Privacy-Risiken

Unveraendert offen:

- kein echtes Owner-/Mandantenmodell
- optionale API-Key-Authentifizierung
- weites CORS
- reportbasierte Klartext-Slugs im Dateisystem und Katalogkontext
- Runtime-Manifest mit Klartext-Personendaten

## 4. Packaging- und Betriebsrisiken

Offen:

- `pyproject.toml` und reale Imports passen nicht sauber zusammen
- Windows-zentrierte Pfade und Launchermodelle
- Tool-/Runtime-Artefakte im Source Tree

## 5. Test- und Reproduzierbarkeitsrisiko

Die Testbasis ist breit, aber nicht voll monoton stabil.

Beobachtete Punkte:

- Testsammlung und gezielte Web-Schnitte laufen lokal
- spaetere Full-Suite-Reruns koennen mit OpenBLAS-/Speicherfehlern brechen
- auch einzelne Worktree-Laeufe verhalten sich in dieser Sitzung teils nicht stabil reproduzierbar, je nach Zusammenstellung und Ausgabeform

## 6. Konkrete naechste technische Punkte

### Sofort naechster Umsetzungsfokus

1. Task 4 `Frontend als 10-Phasen-Operator-Workbench`
2. Task 5 `Review Gate, Result Workspace, Finalization Wiring`
3. Task 6 `Pipeline-Flaeche final trennen und Regressionen schliessen`

### Danach produktweit wichtig

1. Privacy-/Report-Katalog-Konflikt aufloesen
2. Packaging-/Dependency-Wahrheit herstellen
3. Security-Haertung
4. Full-Suite-/OpenBLAS-Stabilisierung

## 7. Empfohlene Entwickler-Lesereihenfolge

1. `Entwicklung/00_AKTUELLER_GESAMTSTAND.md`
2. `Entwicklung/01_SYSTEMARCHITEKTUR_UND_ENTRYPOINTS.md`
3. `Entwicklung/02_WORKFLOWS_PHASES_UND_SCHRITTE.md`
4. `Entwicklung/04_AKTIVE_UMSETZUNG_OPERATOR_WORKBENCH.md`
5. `docs/superpowers/specs/2026-07-05-morphic-operator-workbench-design.md`
6. `docs/superpowers/plans/2026-07-05-morphic-operator-workbench-phase1.md`
7. `docs/deep-audit-2026-07-04/*`

## 8. Schlussurteil

`Morphic V1` hat heute zwei gleich wichtige Wahrheiten:

- den funktionalen, aber noch driftenden Hauptstand auf `master`,
- und die bereits ernsthaft begonnene, aber noch nicht in die UI durchgezogene `Operator Workbench`-Transformation im Worktree.

Die naechste echte Professionalisierung liegt nicht mehr in der Analyse, sondern in der kontrollierten Konsolidierung dieser beiden Wahrheiten.
