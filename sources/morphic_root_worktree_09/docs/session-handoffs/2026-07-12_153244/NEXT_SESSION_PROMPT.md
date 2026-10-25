# COPY-PASTE PROMPT FÜR DIE NÄCHSTE SESSION

```text
Arbeite bitte im bestehenden Worktree
C:\morphic_v1\.worktrees\operator-workbench-phase1
auf dem Branch operator-workbench-phase1 weiter.

Lies vor jeder Änderung zwingend und in dieser Reihenfolge:
1. CLAUDE.md
2. docs/session-handoffs/2026-07-12_153244/SESSION_HANDOFF.md
3. docs/session-handoffs/2026-07-12_153244/CURRENT_SESSION_CHRONICLE.md
4. docs/session-handoffs/2026-07-12_153244/VERIFICATION_EVIDENCE.md
5. docs/status/2026-07-12-e59-release-decision-before-e510.md
6. docs/status/2026-07-12-gesamtstruktur-fortschritt.md
7. .hermes/plans/2026-07-12_123938-e59-group-member-rate-resolver.md

Verifiziere anschließend live:
- git branch --show-current
- git status --short
- git log -1 --oneline

WICHTIG: Der Worktree ist absichtlich sehr umfangreich modified/untracked. Nichts bereinigen, löschen, resetten, stagen, committen oder pushen, sofern ich dies nicht ausdrücklich anfordere. Insbesondere die zahlreichen Benutzer_Archive__ws-* Verzeichnisse nicht anfassen. Keine vorhandenen Ports oder Prozesse verändern. Vor jedem Serverstart freie Ports prüfen; Port 8090 gehört Radi144 und bleibt unberührt.

Aktueller fachlicher Stand:
- Radiquant4-Alignment und Radi144-UI/UX-Konsolidierung sind abgeschlossen.
- Feedback b, c und d sind abgeschlossen.
- Feedback e liegt bei ca. 65 %.
- E4.1–E4.6, E5.1–E5.8 und E5.9.0–E5.9.5 sind abgeschlossen.
- E5.9.5-Entscheidung: E5.9 GO; E5.10 NO-GO.
- Die normale Scan-, CLI-, Job-, Report-, Trace- und Manifestpipeline besitzt weiterhin keine produktive Gruppenwirkung.
- Geo bleibt separat deaktiviert.

E5.10 darf noch NICHT produktiv aktiviert werden. Offene Blocker:
1. keine reale UI/API für individuelle Gruppenanalyse-Einwilligung;
2. produktive Session-/Artefaktregistrierung erzeugt Legacy-Clients ohne Owner-/Tenant-Kontext;
3. Runtime-Clientidentitäten liegen im bestehenden clients.json im Klartext;
4. OperatorContext ist keine echte Authentifizierung;
5. kein default-false Kill-Switch;
6. keine explizite Gruppenstärke in der UI;
7. kein sicherer Worker-Transport ohne Rohvektoren in CLI/Jobpayload;
8. kein produktiver Rollback-/Disable-Akzeptanztest;
9. kein redigierter produktiver Aktivierungs-Audit.

Gehe konservativ und testgetrieben mit E5.10A weiter: gehärtete/verschlüsselte Client-Identity-Quelle. Beginne NICHT mit einer produktiven Gruppen-Scanroute.

Führe zuerst eine fokussierte Discovery durch:
- RuntimeManifestService, Windows-DPAPI-Helfer und alle Client-/Session-/Erasure-/Retentionpfade lesen;
- entscheiden, ob ein separater DPAPI-Identity-Store oder eine sichere Migration minimaler und stabiler ist;
- Legacy-Clients nie automatisch migrieren, owner-binden oder als eingewilligt markieren;
- keine Gruppenraten, Rohgruppenlisten oder Identitäten in Browser, CLI, Jobs, Reports, Traces oder Manifeste einführen;
- vor Mutation einen präzisen E5.10A-Red-Test formulieren.

Empfohlene Richtung:
- separater DPAPI-geschützter, tenant-/workspace-gebundener Identity-Store;
- pseudonyme client_id als Dateischlüssel;
- Identitätsinhalt ausschließlich verschlüsselt;
- Safe-List nur redigierte Metadaten;
- explizite Registrierung, keine automatische Legacy-Migration;
- Resolver-Source liest ausschließlich den gehärteten Store;
- Erasure/Retention umfassen beide Stores;
- E5.10A bleibt ohne produktive Route und ohne Scanwirkung.

Qualitätsregeln:
- C:\morphic_v1\.venv\Scripts\python.exe verwenden;
- PYTHONUTF8=1 und OPENBLAS_NUM_THREADS=1 setzen;
- RED → minimale GREEN-Implementierung → fokussierte Tests → Rest-Suite → separater Top-5-Smoke;
- Python-Compile, node --check und git diff --check;
- bekannter Rate-Limit-Test kann im Gesamtlauf 429 statt 422 liefern und muss dann separat grün nachgewiesen werden;
- kein Commit/Push/Reset/Clean ohne ausdrückliche Anweisung.

Starte mit einer kurzen tabellarischen Revalidierung der Übergabe und arbeite danach autonom mit dem E5.10A-Discovery-/TDD-Gate weiter. Berichte keine produktive Gruppenaktivierung, solange die NO-GO-Blocker nicht geschlossen sind.
```
