# New Kilo Session Prompt - Resume Gate 5 Exactly

Paste the following text as the first message in a new Kilo session:

```text
Setze die RadiMorphic-Single-Core-Baseline im bestehenden Worktree exakt am
Gate-5-Unterbrechungspunkt fort.

Arbeite ausschliesslich hier:
C:\morphic_v1\.worktrees\operator-workbench-phase1

Erwarteter Branch: report-ux-polish
Erwarteter HEAD: 2d38d3bfa3f204491fe066fbc986e07fffc2ff06
Kein Staging, Commit, Push, Reset oder Clean ohne meine separate ausdrueckliche
Anweisung. Historische untracked Dateien und akzeptierte Gate-4-Aenderungen
nicht anfassen oder zuruecksetzen.

Lies zwingend zuerst, in dieser Reihenfolge:
1. PROJECT_MEMORY/00_CURRENT_STATE.md
2. PROJECT_MEMORY/2026-08-06-gate5-session-checkpoint.md
3. docs/superpowers/specs/2026-08-06-gate5-emf-authority-source-truth-design.md
4. docs/superpowers/plans/2026-08-06-gate5-emf-authority-source-truth.md

Verifiziere vor jeder Fortsetzung das Recovery-WIP-Manifest:
PROJECT_MEMORY/2026-08-06-gate5-wip-source.sha256
Jeder Hash-Mismatch ist ein Stop-Gate und muss vor Tests erklaert werden. Das
WIP-Manifest ist kein Gate-5-Acceptance-Freeze.

Wichtiger Status:
- Gate 5 Tasks 1-7 sind implementiert.
- Tasks 1-5 und 7 haben finale unabhaengige APPROVE-Reviews ohne blockierende
  Befunde.
- Task 6 ist nach Marker-, Monitor-, Statusnormalisierungs- und WCAG-Fixes final
  Spec- und Quality/Accessibility-approved, ohne blockierende Befunde.
- Finaler Task-6-Quality/Renderer-Fokus: 78 passed; betroffene Browserchecks:
  2 passed.
- Whole-Gate-Reviews fanden danach Auth-Generationsraces. Diese sind mit
  Request-State-Snapshots, Response-Body-Revalidierung, atomarer Sessionausgabe,
  Mutation-Kompensation und finaler WebSocket-Authpruefung geschlossen.
- Hardened-Auth-Matrix: 368 passed; Spec-Fix- und Security-Re-Review APPROVE.
- Die vorher gruenen Python-3235-/Browser-50-Gesamtmatrizen liegen vor diesen
  Security-Sourceaenderungen und muessen deshalb erneut laufen.
- Der abschliessende Whole-Gate-Quality-Review fand danach vier valide Blocker:
  Same-Origin-CSRF, stale Kompensation, ambige Timeout-Reconciliation und
  malformed Probe-Truth. Alle vier sind TDD-gefixt und fokussiert approved.
- Aktuell: Whole-Gate Spec APPROVE und Quality-Re-Review APPROVE P0/P1/P2=0;
  die Gesamtmatrizen muessen auf den letzten Quality-Bytes erneut laufen.
- Finaler Gate-5-Fokus nach dem Fix: 408 passed.
- Fokussierter Playwright Gate-5-Test nach dem Fix: 1 passed, zero retries.
- Die erste Vollsuite vor dem Fix hatte exakt einen Fehler wegen dieses Markers:
  1 failed, 3221 passed, 17 skipped, 9 warnings in 481.46s.
- Die komplette Python-Suite und komplette Browsermatrix wurden nach dem Fix
  noch nicht erneut ausgefuehrt.
- Gate-5-Manifest, Freeze und Acceptance-Status existieren noch nicht.
- Gate 5 ist daher noch NICHT accepted.

Die letzte Kilo-Meldung `Tool execution aborted` war kein Codefehler. Ein
Review-Tool wurde versehentlich mit leerem Auftrag aufgerufen; kein Subagent
startete und keine Datei wurde dadurch geaendert.

Beginne exakt so:
1. Verifiziere Branch, HEAD, leeren Index, RAM >= 3.5 GiB, einen Kilo-Prozess,
   freie/erklaerte Ports und keine stale Prozesse.
2. Verifiziere das WIP-Manifest vollstaendig gegen die aktuellen Dateien.
3. Starte die volle Python-Suite auf den finalen Quality-Bytes seriell mit
   PYTHONUTF8=1, PYTHONIOENCODING=utf-8 und OPENBLAS_NUM_THREADS=1.
4. Danach `npm --prefix tests/browser test`.
5. Bei unveraenderten Quellen: finaler Whole-Gate-5-Spec-Review, danach separater
   Quality/Security-Review.
6. Erst bei komplett gruenen Matrizen und Reviews SHA-256-Manifest, zwei
   Review-Records, Freeze-Record und Acceptance-Status erzeugen, Hashes
   rueckverifizieren und Golden Record auf Gate-5-GO/naechstes Gate 6 setzen.

Verbindliche Scopegrenze:
- kein Linux-Server/Remote-WSS;
- keine physische Sensorintegration;
- keine Harmonisierung, Reports/PDF, Katalogaktivierung, Quantum/Grover oder
  Cloud-Integration;
- moderne und Legacy-EMF-Routen behalten eine gemeinsame durable Autoritaet,
  gleiche Authentifizierung und Lease-Sicherheit;
- Aktivierung bleibt bis manuell deaktiviert;
- Fallbackwerte bleiben sichtbar und quellengekennzeichnet;
- kein physischer oder medizinischer Claim.

Arbeite subagent-gesteuert, seriell, mit RED/GREEN fuer jeden validen Fund und
Evidence-before-Completion. Stoppe bei RAM-/Prozess-/Port- oder Review-Blockern,
statt zu raten.
```
