# Roadmap-Status - Erledigt Und Offen

## 1. Bereits klar im Haupt-Repository reflektiert

### Historische Kernphasen

1. CLI-Modularisierung
   - `apps/cli/main.py` ist duenn
   - Kommandos sind modularisiert
2. Web-App-Konsolidierung auf `apps/web/main.py`
3. Report-Katalog, Preview und File-Zugriff
4. Runtime-Privacy-Manifest
5. Source Registry und Health-Checks
6. Hardware Driver Layer / Snapshot / Realtime-EMF-Bausteine

## 2. Lokal bereits im Haupt-Checkout als WIP sichtbar

1. Erweiterung der Web-Shell auf 8 sichtbare Schritte
2. Berichte und Harmonisierung sind als explizite Workflow-Panels im aktuellen lokalen Diff enthalten

## 3. Freigegebene Zielrichtung

Aktuell freigegebene Hauptzielrichtung:

- `Morphic Operator Workbench`
- 10-Phasen-Modell
- Radi144-Patterns nur selektiv und professionell uebernommen

Quellen:

- `docs/superpowers/specs/2026-07-05-morphic-operator-workbench-design.md`
- `docs/superpowers/plans/2026-07-05-morphic-operator-workbench-phase1.md`

## 4. Aktuelle Umsetzungsplanung der Operator Workbench

Geplante Tasks:

1. Canonical Workbench Contracts And Registry
2. Hardware Truth Model And Expert-Mode Gate API
3. Runtime-Backed Drafts, Templates, And Run Trace Manifests
4. Rebuild The Frontend As A 10-Phase Operator Workbench
5. Review Gate, Result Workspace, And Finalization Wiring
6. Separate The Pipeline View And Finish Regression Coverage

## 5. Aktueller Task-Status im Worktree

### Abgeschlossen

1. Task 1
2. Task 2
3. Task 3

### Noch offen

4. Task 4
5. Task 5
6. Task 6

## 6. Grosse offene Produktachsen ausserhalb des aktuellen Workbench-Schnitts

Diese Themen bleiben auch nach dem Workbench-Plan offen:

### P0

1. kanonischer Workflow ueber alle Ebenen
2. Report-/Job-Ownership und echtes Auth-/Mandantenmodell
3. Privacy-Konflikt im Report-Katalog
4. Packaging-/Dependency-Wahrheit

### P1

1. Consent-/Actor-/Retention-Ausbau
2. Security Header und Netzwerkhaertung
3. tiefere UI-/A11y-/Reduced-Motion-Nacharbeit
4. Repo-Hygiene und Artefaktentkopplung

### P2

1. Browser-E2E
2. RUM/CWV
3. Legacy-Webpfade abbauen
4. Event-/Projection-basierte Ergebnislogik statt Dateisystemrekonstruktion

## 7. Wichtigste Drift in der Dokumentation

Veraltet oder widerspruechlich:

- `README.md`
- `CLAUDE.md`
- `PROJECT_MEMORY/00_CURRENT_STATE.md`

Technisch aktuellere Referenzen:

- `docs/deep-audit-2026-07-04/*`
- `docs/deep-audit-2026-07-05/*` (inkl. `RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`, `QISKIT_VERIFICATION_LOG.md`)
- `docs/superpowers/specs/2026-07-05-morphic-operator-workbench-design.md`
- `docs/superpowers/plans/2026-07-05-morphic-operator-workbench-phase1.md`
- `docs/superpowers/specs/2026-07-05-morphic-v1-radiquant4-alignment-design.md`
- `docs/superpowers/plans/2026-07-05-morphic-v1-radiquant4-alignment.md`

## 8. Update 2026-07-06: Alignment-Plan umgesetzt

Am 2026-07-06 wurde der `morphic-v1-radiquant4-alignment`-Plan
freigegeben und Tasks 1-7 sowie 9 umgesetzt (TDD, alle neuen Module
mit eigener Testsuite). Task 8 (Design-Token-Übernahme) wartet
bewusst auf Abschluss von Operator-Workbench-Task 4.

Neue Module (alle getestet, alle grün):

- `core/compliance/platform_export.py` - `StandardAnalysisBlock`-Adapter
- `core/compliance/operator_context.py` - Operator-/Workspace-Kontext
- `core/compliance/entitlement_stub.py` - austauschbare Entitlement-Naht
- `core/realtime/seed_generator.py` - deterministischer, workspace-gebundener Seed + ehrliche Entropie-Kaskade
- `apps/cli/workflow/substep_manifest.py` - Vokabular-Mapping morphic_v1↔radiquant4

Modifikationen (nicht-regierend, alle bestehenden Privacy-/Manifest-/Quantum-Tests weiterhin grün):

- `apps/cli/workflow/step11_export.py` - additiver `*_standard_block.json`-Export
- `apps/cli/workflow/step09_quantum.py` + `state.py` - `quantum_mode` ("real"|"classical") ehrlich sichtbar
- `core/compliance/runtime_manifest.py` - `append_audit(actor=...)`, `purge_expired(retention_days, dry_run)`
- `apps/cli/commands/privacy.py` - neue CLI `privacy purge-expired`

Quantum-Pfad erstmals real verifiziert: `qiskit 2.5.0`, 1 markiertes Item
von 8 wird mit 94.38% Top-Ergebnis (korrekte Amplitudenverstaerkung). Siehe
`docs/deep-audit-2026-07-05/QISKIT_VERIFICATION_LOG.md`.
