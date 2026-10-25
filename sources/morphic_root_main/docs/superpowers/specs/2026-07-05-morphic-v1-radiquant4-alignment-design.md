# Morphic V1 → radiquant4/RadiMorphic Alignment Design

**Stand:** `2026-07-05`
**Workspace:** `C:/morphic_v1`
**Status:** Zieldesign zur Abstimmung, vor Umsetzung
**Baut auf:** `docs/superpowers/specs/2026-07-05-morphic-operator-workbench-design.md` (akzeptiert, Tasks 1-3 im Worktree `operator-workbench-phase1` bereits umgesetzt)
**Referenz:** `docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`

## Ziel

`morphic_v1` wird in seinem eigenen Repository **funktional fertiggestellt, visuell an `radiquant4` angeglichen und getestet**, so dass es später — als eigener Schritt, ausgeführt von einer Instanz direkt in `radiquant4` — entweder

1. **standalone** (als eigenständiges Produkt, ohne Plattformanbindung) oder
2. **synergetisch** (als plattform-kompatibler Baustein, der sich am `radimorphic`-Vertrag orientiert)

freigegeben und übernommen werden kann. Dieses Dokument beschreibt **nicht** die eigentliche Migration nach `radiquant4` — das bleibt explizit einer dortigen Instanz vorbehalten.

## Ausgangslage (zwei zusammengeführte Befundquellen)

1. `docs/deep-audit-2026-07-04/*` + `docs/deep-audit-2026-07-05/PHASE_8_QUANTUM_FRAMEWORK_TIEFENANALYSE.md`: `morphic_v1` ist funktionsreich, aber mit drei konkurrierenden Workflow-Modellen, ohne echtes Auth-/Mandantenmodell, mit Privacy-Widerspruch im Report-Katalog, und einem Quantum-Framework, das mangels installiertem `qiskit` faktisch immer im klassischen Fallback läuft.
2. `docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`: `radiquant4` betreibt bereits produktiv einen eigenen, konzeptionell verwandten `radimorphic`-Service mit striktem Vertrag (SSOT-Manifest, `StandardAnalysisBlock`, 12-Substep-Contract, Tenant-/Abo-Gating, TRNG-Kaskade, Qiskit→PennyLane→NumPy-Fallback, Astro/React/Tailwind/shadcn-Frontend mit oklch-Design-Tokens).

**Kernspannung:** Der Name/Platz "RadiMorphic" ist auf der Plattform bereits belegt. `morphic_v1` kann daher nicht einfach "werden", sondern muss so **vertragskompatibel** gemacht werden, dass eine spätere Instanz in `radiquant4` entscheiden kann, ob und wie `morphic_v1`s Fachlogik (Remedies-DB, `procedural_groups`, NLS-Scoring, Quantum-Synergy) den bestehenden Service ergänzt, ablöst oder als eigenständiges Zusatzmodul danebensteht.

## Designprinzipien (Priorität wie vom Auftraggeber vorgegeben)

1. **Intuitive Usability zuerst.** Jede Änderung muss den Operator-Workflow klarer machen, nicht nur "plattformkompatibler". Basis bleibt die bereits akzeptierte 10-Phasen-Operator-Workbench.
2. **Echtzeitfähigkeit für akkurate, effektive, nachvollziehbare Ergebnisse.** Entropie-/Seed-Erzeugung und Quantum-Pfad werden am `radiquant4`-Goldstandard (TRNG-Kaskade, deterministischer tenant-gebundener Seed, ehrliche Fallback-Kaskade) ausgerichtet — nicht als Kopie, sondern als gleichwertiges Muster im bestehenden Python/FastAPI/Typer-Stack von `morphic_v1`.
3. **Modularität vor Migration.** `morphic_v1` bekommt eine klar abgegrenzte Adapterschicht (Datenkontrakt, Modul-Registry-Eintrag, Entitlement-Stub), die *heute* keine Wirkung auf den Standalone-Betrieb hat, aber morgen die Übernahme erleichtert.
4. **Keine Vortäuschung.** Wo `morphic_v1` (noch) keine Postgres-/Redis-/Multi-Tenant-Infrastruktur hat, wird das ehrlich als "Kompatibilitätsschicht auf Dateibasis" gekennzeichnet, nicht als vollwertige Multitenancy verkauft.
5. **Nicht doppelt planen.** Die bereits laufende Operator-Workbench-Initiative (Worktree `operator-workbench-phase1`) bleibt der alleinige UI-Umsetzungsstrang; dieses Dokument erweitert sie um Design-Tokens, Datenkontrakt und Realtime-/Quantum-Härtung, ersetzt sie nicht.

## Zielarchitektur: Kontraktabgleich

| Ebene | radiquant4/radimorphic (Ist) | morphic_v1 (Ist) | Zielzustand morphic_v1 |
| --- | --- | --- | --- |
| Ergebnis-Schema | `StandardAnalysisBlock` + `RadiMorphicAnalysisBlock` (Pydantic, tenant/session/patient-gebunden) | Freie JSON-Exportform pro Tool (`tools/*.py`) | Ein `PlatformExportAdapter`, der aus dem bestehenden Export zusätzlich ein `StandardAnalysisBlock`-kompatibles JSON erzeugt (append-only, bricht nichts Bestehendes) |
| Reporting-Rohform | `results["radimorphic"] = {inputs, outputs{quality_score, morphic_field, holographic_entropy, remedy_matches:[(name,score)]}, meta}` | ähnliche, aber nicht standardisierte Felder über mehrere Tools verteilt | Einheitliches `build_standard_output_block()` je Scan-Lauf, exakt in dieser Feldbenennung |
| Substep-Contract | 12 fest benannte Substeps mit Event-Bus-Emission | 12-Step-Orchestrator mit anderen Namen/State-Objekt, nicht der Web-Hauptpfad | Substep-Namen an das `radiquant4`-Vokabular anlehnen (Mapping-Tabelle, kein 1:1-Zwang), Events statt nur Stdout |
| Entropie/Seed | TRNG-Kaskade (QRNG→WebCam→InfiniteNoise→ESP32→os.urandom) + deterministischer SHA256-Seed (tenant-gebunden) | `providers/hardware/entropy_sources.py`, `core/realtime/emf_profile.py` mit `default_sensor_entropy_probe() -> (0.5, "fallback")` | Deterministischer, tenant-/session-fähiger Seed nach demselben Hash-Muster + dokumentierte, ehrliche Fallback-Kaskade mit Audit-Samples |
| Quantum | Qiskit → PennyLane → NumPy, alle 3 Stufen aktiv gepflegt | `core/quantum_synergy`: Qiskit → klassisch, Qiskit nicht installiert, „echter" Pfad nie verifiziert | Qiskit installierbar + verifizierbar machen (optional-extra sauber testbar), Fallback-Kaskade ehrlich sichtbar machen (siehe `PHASE_9`) |
| Multitenancy | Postgres-Tenant + Stripe-Subscription + `EntitlementService` | keine Tenant-Entität, kein Auth | Leichte, dateibasierte `operator_id`/`workspace_id`-Kontextschicht (aus `PHASE_5`-Vorschlag 2) + Entitlement-Stub-Interface, das später gegen echte Plattform-Entitlements getauscht werden kann |
| Design/UI | Astro+React+Tailwind+shadcn, oklch-Tokens, Modul-Registry mit `standaloneRunSupported` | Vanilla HTML/CSS/JS, 8-Step-Wizard im Umbau zu 10-Phasen-Workbench | CSS-Custom-Properties nach `design-tokens.css`-Vorbild in `apps/web/static/app.css` übernehmen (siehe Abschnitt "Design-Alignment"); Astro/React-Umstieg bewusst **nicht** jetzt (siehe Nicht-Ziele) |
| DSGVO | `gdpr_service.py` (Art. 17/20/30/35), `audit_service.py`, `data_retention_service.py`, `llm_safety_orchestrator.py` (PII-Redaction) | Runtime-Manifest mit Safe-View, aber Klartext-PII im Manifest, kein Retention-Purge, Audit-Actor immer `system` | Retention-Purge-Job + echter Actor-Kontext im Audit-Log (kleine, in sich geschlossene Erweiterung von `core/compliance/runtime_manifest.py`) |

## Design-Alignment (konkret, ohne Frontend-Rewrite)

Aus `apps/web-astro/src/styles/design-tokens.css` (radiquant4) werden die **semantischen** Tokens 1:1 als CSS-Custom-Properties in `apps/web/static/app.css` übernommen (Farbwerte in oklch, wo vom aktuellen Browser-Support unkritisch, sonst hex-Fallback):

- Primär-/Neutral-/Phasenfarben (`--background`, `--foreground`, `--primary`, `--phase-diagnose/-analyse/-harmonize/-reflexion`)
- Typografie (`Fraunces` für Überschriften, `Inter` für Fließtext — beides selbst gehostet, **keine** externen Google-Fonts-Requests, siehe `PHASE_4`-Kritikpunkt zu `workflow_stepping.html`)
- Radius-Skala (`--radius` … `--radius-3xl`), Shadow-Tokens, Motion-Tokens (inkl. `prefers-reduced-motion`-Kopplung, behebt einen offenen `PHASE_4`-P1-Punkt)
- Modul-Farbzuordnung: `morphic_v1` bekommt probeweise die Farbmetaphorik der `analyse`-Phase (528 Hz / Violett-Cyan-Bereich), passend zur inhaltlichen Nähe zu `radimorphic`

**Wichtig:** Das ist eine Werteübernahme (Tokens), keine Technologieübernahme. Der bestehende, dependency-freie Vanilla-Stack bleibt erhalten. Das entspricht der geäußerten Vorsicht ("Radiquant4 zuerst analysieren, um spätere Probleme zu vermeiden") — ein voller Astro/React-Umstieg jetzt würde die laufende Operator-Workbench-Umsetzung (Worktree, Tasks 1-3 bereits fertig) unnötig gefährden.

## Nicht-Ziele (bewusst ausgeschlossen)

1. Kein Wechsel von Vanilla-JS auf Astro/React/Tailwind in diesem Schritt — nur Design-Token-Übernahme.
2. Keine echte Postgres-/Redis-/Celery-Infrastruktur in `morphic_v1` — die Kompatibilitätsschicht bleibt dateibasiert.
3. Keine Migration von Code nach `radiquant4` — das bleibt einer dortigen Instanz vorbehalten.
4. Kein Zwang, `morphic_v1`s Substep-Namen 1:1 an `radimorphic` anzugleichen — nur eine dokumentierte Mapping-Tabelle.
5. Keine Änderungen am `radiquant4`-Server selbst.

## Abnahmekriterien ("platform-ready" Definition of Done)

1. Jeder produktive Scan-/Harmonisierungslauf erzeugt zusätzlich ein `StandardAnalysisBlock`-kompatibles JSON (Feldnamen exakt wie in Abschnitt "Zielarchitektur").
2. Es existiert ein dokumentiertes, getestetes Mapping zwischen `morphic_v1`s 12-Step-Workflow und dem `radimorphic`-12-Substep-Vokabular.
3. Der Quantum-Pfad ist mit installiertem `qiskit` mindestens einmal real (nicht nur klassisch) end-to-end verifiziert und das Ergebnis dokumentiert.
4. Die Entropie-/Seed-Erzeugung liefert einen deterministischen, tenant-/workspace-fähigen Seed nach demselben Hash-Prinzip wie `radiquant4`, mit dokumentierter Fallback-Kaskade.
5. Es existiert ein leichtgewichtiger `operator_id`/`workspace_id`-Kontext, der Ownership-Checks für Jobs/Reports ermöglicht (schließt einen P0-Punkt aus `PHASE_3`).
6. Das Web-Frontend nutzt die übernommenen Design-Tokens sichtbar (Screenshots/visueller Vergleich), ohne die Operator-Workbench-Funktionalität zu regressieren.
7. Alle bestehenden Tests bleiben grün; neue Funktionalität ist mit eigenen Tests abgedeckt (TDD-Vorgehen wie im bestehenden Operator-Workbench-Plan).
8. Ein einziges Referenzdokument (`RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`) bleibt Quelle der Wahrheit für zukünftige Abgleiche.

## Risiken

1. **Scope-Kollision** mit der laufenden Operator-Workbench-Umsetzung, falls beide gleichzeitig an `apps/web/static/*` arbeiten → Empfehlung: Design-Token-Übernahme als eigener, kleiner Task *innerhalb* des bestehenden Worktrees, nicht parallel dazu.
2. **Falsche Sicherheit durch Kompatibilitätsschicht**: eine dateibasierte "Tenant"-Schicht darf nicht als echte Mandantenfähigkeit missverstanden werden — muss in Doku und Code klar als Vorbereitungsschicht markiert sein.
3. **Qiskit-Installation** kann in der aktuellen Windows-/Ressourcen-Umgebung zusätzliche Instabilität erzeugen (vgl. bereits beobachtete OpenBLAS-Speicherfehler) → als optionale, isoliert getestete Extra-Dependency behandeln, nicht als Pflichtabhängigkeit.
4. **Domänen-Drift**: `morphic_v1`s Faktorentabellen (Bruce-Copen/Phi/Schumann) und `radiquant4`s (`_MORPHIC_GEOMETRY_FACTORS`/`_MORPHIC_INTENTION_FACTORS`) sind fachlich verwandt, aber nicht identisch — eine 1:1-Vereinheitlichung ist ausdrücklich nicht Teil dieses Schritts, nur die Kontrakt-/Formebene.

## Entscheidung (2026-07-06)

Design-Token-Übernahme (Task 8) erfolgt **strikt nach** Abschluss von Task 4 (10-Phasen-Frontend-Rebuild) des bestehenden Operator-Workbench-Plans, nicht parallel/während. Tasks 1-3, 5-7 und 9 sind davon unabhängig und wurden zur sofortigen Umsetzung freigegeben.
