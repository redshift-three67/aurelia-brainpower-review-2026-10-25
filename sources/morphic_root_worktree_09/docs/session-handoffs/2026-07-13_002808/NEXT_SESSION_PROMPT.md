# COPY-PASTE-WORTLAUT FÜR DIE NÄCHSTE SESSION

> **ÜBERHOLT SEIT 2026-07-13 09:41 CEST – den untenstehenden E5.10F-Arbeitsauftrag nicht erneut ausführen.** E5.10F und E5.10 sind nach Post-Issue-Erasure-Härtung, realem Browserlauf, 51-Dateien-Artefaktaudit und abschließendem unabhängigen Re-Review (`APPROVE`) GO. Aktueller Gate-Record: `docs/status/2026-07-13-e510f-browser-privacy-audit-rollback-release-gate.md`. Nächster Arbeitsbereich ist Feedback f als read-only Ist-Analyse; Geo bleibt separat NO-GO.

Den folgenden Block vollständig als erste Nachricht in einer neuen Session verwenden:

```text
Arbeite bitte ausschließlich im bestehenden Worktree
C:\morphic_v1\.worktrees\operator-workbench-phase1
auf dem Branch operator-workbench-phase1 weiter.

Lies vor jeder Änderung zwingend und in dieser Reihenfolge:
1. CLAUDE.md
2. docs/session-handoffs/2026-07-13_002808/SESSION_HANDOFF.md
3. docs/session-handoffs/2026-07-13_002808/CURRENT_SESSION_CHRONICLE.md
4. docs/session-handoffs/2026-07-13_002808/VERIFICATION_EVIDENCE.md
5. docs/status/2026-07-13-e510e-local-productive-group-integration-gate.md
6. docs/status/2026-07-12-gesamtstruktur-fortschritt.md
7. .hermes/plans/2026-07-13-e510e-local-productive-group-integration.md
8. docs/status/2026-07-12-e510d-activation-handle-transport-gate.md

Verifiziere anschließend live:
- git branch --show-current
- git log -1 --oneline
- git status --short
- git diff --check

WICHTIG: Der Worktree ist absichtlich sehr umfangreich modified/untracked. Nichts bereinigen, löschen, resetten, stagen, committen oder pushen, sofern ich dies nicht ausdrücklich anfordere. Insbesondere die zahlreichen Benutzer_Archive__ws-* Verzeichnisse nicht anfassen. Keine vorhandenen Ports oder Prozesse verändern. Vor jedem Serverstart freie Ports prüfen; Port 8090 gehört Radi144 und bleibt unberührt.

Aktueller fachlicher Stand:
- Radiquant4-Alignment und Radi144-UI/UX-Konsolidierung sind abgeschlossen.
- Feedback b, c und d sind abgeschlossen.
- Feedback e liegt bei ca. 90 %.
- E4.1–E4.6, E5.1–E5.9.5 und E5.10A–E sind technisch abgeschlossen.
- E5.10E hat die streng lokale Backend-/Worker-Produktivintegration umgesetzt.
- E5.10 insgesamt bleibt ausdrücklich NO-GO, bis E5.10F vollständig abgenommen ist.
- Geo bleibt separat deaktiviert und darf nicht zusammen mit Gruppe freigegeben werden.

E5.10E-Datenfluss, der unverändert geschützt bleiben muss:
Phase1ScanRequest.group_draft_id
→ serverseitig abgeleitete stabile subject_id
→ DPAPI-Gruppendraft
→ DPAPI-Identity-Store und aktueller Einzelconsent
→ Resolver/Autorisierung plus explizite Policy-Stärke
→ DPAPI-Root-Handle
→ ausschließlich nicht persistiertes privates Job-Environment
→ Top-N konsumiert Root-Handle genau einmal
→ eigener kurzlebiger Child-Handle je Screening-/Detail-Multiplexprozess
→ Field-Worker konsumiert Child-Handle genau einmal
→ AnalysisService.encode_profile(group_opt_in=...) ausschließlich in-memory.

Unverhandelbare Verträge:
1. MORPHIC_GROUP_ANALYSIS_ENABLED fehlt/ist unbekannt → keine Wirkung.
2. Fehlende Stärke oder Stärke 0.0 → keine Wirkung und kein Draft-/Identity-Storezugriff.
3. Aktivierung ist nur über explizites group_draft_id zulässig; kein implizit letzter Draft.
4. Der Request darf keine group_member_rates, group_opt_in, group_centroid, group_subject_id oder activation_handle enthalten.
5. Handles dürfen niemals in CLI-Argumenten, Job-Snapshots, API-Responses, Workbench-Run-Traces, Reports oder Manifesten erscheinen.
6. Rohidentitäten, Mitgliedslisten, Raten und Zentroide dürfen keine Prozessgrenze überschreiten.
7. Ungültige, abgelaufene, fremde oder wiederverwendete Handles müssen fail-closed enden; kein stiller Baseline-Scan unter behaupteter Aktivierung.
8. OperatorContext ist weiterhin nur eine lokale Vorbereitungsschicht und keine echte Authentifizierung.
9. Geo bleibt vollständig unverdrahtet.

Reale letzte E5.10E-Verifikation:
- E5.10E-/Web-/Release-Fokus: 59 passed.
- Neuer Integrationsfokus: 13 passed.
- Rest-Suite ohne Top-5: 470 passed, 2 skipped; acht bekannte gemeinsame Rate-Limit-429-Ausreißer und ein alter Boundary-Test, der nach E5.10E korrekt evolviert wurde.
- Alle acht 429-Ausreißer separat/frisch: jeweils 1 passed.
- Evolvierter Boundary-Test: 1 passed.
- Top-5-Smoke: 1 passed in 152.25s.
- Python-Compile, node --check und git diff --check: bestanden.

Beginne jetzt konservativ und testgetrieben mit E5.10F – Browser-, Privacy-, Audit- und Rollback-Gesamtfreigabe. Führe zuerst eine fokussierte Discovery durch; ändere noch nichts, bevor die vorhandene UI-/State-/Payload-Kette exakt kartiert ist:
- Gruppen-Draft-Auswahl, Consent-UI und Policy-Stärke in index.html/app.js/workbench-api.js nachvollziehen;
- klären, wie die explizite group_draft_id ausschließlich bei bewusster Aktivierung in formScanPayload() gelangt;
- sicherstellen, dass keine Gruppen-ID oder Aktivierung in localStorage, Templates, allgemeinen Workbench-Drafts, Logs oder Run-Traces landet;
- reale positive Wirkung und alle Rollbacks als TDD-/Browser-Matrix formulieren;
- vor Serverstart Ports prüfen und für Abnahme einen freien Loopback-Port verwenden; 8090 nicht anfassen.

E5.10F-Mindestmatrix:
A. Default/Flag aus → exakt bestehender Baselinepfad, kein Storezugriff.
B. Stärke 0 → exakt Baseline, kein Handle.
C. Gültiger Draft + aktuelle Einzelconsents + Flag an + Stärke >0 → positive synthetische Wirkung.
D. Draft-Analyseconsent false → fail-closed vor Scanstart.
E. Subject nicht Mitglied → fail-closed.
F. Einzelconsent fehlt, widerrufen oder abgelaufen → fail-closed.
G. fremder Owner/Workspace/Tenant → fail-closed.
H. abgelaufener/manipulierter/wiederverwendeter Handle → fail-closed.
I. Kill-Switch nach Aktivierung aus → neue Scans baseline; keine neuen Handles.
J. Erasure einer Identity oder des Drafts → verbleibende Aktivierung inert.
K. API-Response, Job-Snapshot, Run-Trace, Logs, Reports und Manifeste bleiben redigiert.
L. Browserfluss zeigt explizite Wirkung/Keine-Wirkung korrekt, funktioniert bei 320 px ohne horizontalen Overflow und hinterlässt nach Test keine synthetischen Daten.

Qualitätsregeln:
- Python ausschließlich mit C:\morphic_v1\.venv\Scripts\python.exe ausführen.
- PYTHONUTF8=1 und OPENBLAS_NUM_THREADS=1 setzen.
- Striktes RED → minimale GREEN-Implementierung → Refactor nur bei grün.
- Fokustests, Rest-Suite ohne Top-5, Rate-Limiter-Ausreißer separat, Top-5-Smoke separat.
- Python-Compile, node --check und git diff --check.
- Reale Browserabnahme erst nach grünen Backend-/DOM-Verträgen.
- Synthetische Drafts/Identitäten/Handles nach Browserabnahme gezielt löschen; keine Archive pauschal bereinigen.
- Kein Commit/Push/Reset/Clean ohne ausdrückliche Nutzeranweisung.

Starte mit einer kurzen tabellarischen Revalidierung der Übergabe und arbeite danach autonom mit der E5.10F-Discovery und dem präzisen TDD-/Browser-Abnahmeplan weiter. Berichte E5.10 erst dann als GO, wenn sämtliche E5.10F-Verträge real und vollständig bestanden sind.
```
