# Exakter Startprompt für die nächste Session

Kopiere den folgenden Text vollständig als erste Nachricht in die neue Session:

---

Arbeite im bestehenden Worktree `C:\morphic_v1\.worktrees\operator-workbench-phase1` auf Branch `operator-workbench-phase1`. Lies zuerst vollständig und in dieser Reihenfolge:

1. `CLAUDE.md`
2. `docs/session-handoffs/2026-07-13_133304/SESSION_HANDOFF.md`
3. `docs/session-handoffs/2026-07-13_133304/VERIFICATION.md`
4. `docs/status/2026-07-13-feedback-f-F2-1-offline-service.md`
5. `docs/status/2026-07-13-feedback-f-umsetzungsplan-kurz.md`
6. `.hermes/plans/2026-07-13-feedback-f-admin-catalog-repositories.md`, besonders F2 ab Zeile 119
7. `docs/status/2026-07-12-gesamtstruktur-fortschritt.md`
8. `PROJECT_MEMORY/00_CURRENT_STATE.md`; behandle darin ältere Statusaussagen zu Feedback f als historisch und den timestamped Handoff als neueren Statusbeleg.

Verifiziere danach live, bevor du irgendetwas änderst:

```bash
pwd
git branch --show-current
git rev-parse HEAD
git status --short
sha256sum data/remedies.db
/c/morphic_v1/.venv/Scripts/python.exe -c "import psutil; print([(c.laddr.ip,c.laddr.port,c.status,c.pid) for c in psutil.net_connections(kind='inet') if c.laddr and c.laddr.port in (8000,8090)])"
```

Erwarteter Ausgangspunkt aus dem Pause-Handoff:

- Branch: `operator-workbench-phase1`
- HEAD: `619a1f5485a151816e32732929a6a823839ccb57`
- Worktree: umfangreich dirty mit fremder und benutzereigener Arbeit; nichts pauschal bereinigen, verschieben, überschreiben, stagen oder committen.
- `data/remedies.db` SHA-256: `c67d4e899dab9547a2171ec0d5604d9628721b6757a87d33ef8d34f0c0dadfa0`
- Port 8000 und Port 8090 waren bei der Pause beide auf `127.0.0.1` belegt. Bestehende Prozesse niemals stoppen oder verändern.
- F0: GO.
- F1: GO.
- F2.1: GO.
- Maßgeblicher F2.1-Review: `deleg_fa94b8c3`, `APPROVE`, Konfidenz HOCH, keine offenen historischen oder neuen P0–P2.
- Aktueller fokussierter Nachweis: 82 Admin-Catalog-Tests PASS mit `-W error`; 16 Service-Tests PASS; `py_compile` PASS.
- Breite Regression ohne Top-5: 563 passed, 2 skipped, 13 failed. Das ist exakt die bekannte Baseline `481 passed, 2 skipped, 13 failed` plus 82 neue grüne Catalog-Tests; alle 13 Fehler sind dieselben prozessweiten HTTP-429-/Rate-Limiter-Ausreißer.
- Top-5-Smoke: 1 passed.
- F2 insgesamt: 25 %; Feedback f gewichtet: 25 %.
- Feedback f als Gesamtfeature: NO-GO.
- Produktiver Admin-Catalog: NO-GO.
- Online-Repositories: NO-GO.
- Geo: separater NO-GO-Zweig.
- Keine Runtime-, Web-, CLI-, Engine-, Legacy- oder Netzwerkverdrahtung des Admin-Catalog-Services.
- Kein Commit, Push, Reset, Clean oder Staging wurde durchgeführt.

Post-State-ShadowCopy von F2.1:

```text
E:\mprphic_v1_Backups\morphic_v1_shadowcopy_20260713_132404_feedback_f_F2_1_GO_post
13/13 Dateien hashverifiziert
SHA256_MANIFEST.json: d1ab265153fce472aa72b6e395d6989003012439803be97d603a0a5a76dd124e
```

Setze anschließend konservativ mit dem nächsten zulässigen Block **F2.2 – sichere externe Admin-Catalog-Pfadpolicy und Sandbox-Schutz** fort. Vor jeder produktiven Mutation:

1. Lies die bestehenden Pfadhelfer und benachbarten Windows-Sicherheitsmuster read-only; erfinde keine APIs.
2. Erstelle eine neue externe timestamped, hashverifizierte Pre-State-ShadowCopy der konkret zu berührenden Dateien außerhalb des Repositories.
3. Definiere F2.2 strikt RED→GREEN in `tests/test_admin_catalog_paths.py`.
4. Implementiere minimal in `core/admin_catalog/paths.py`.
5. Halte den Block vollständig offline und ohne produktive Verdrahtung.
6. Lasse vorhandene Dienste auf 8000/8090 unberührt.
7. Führe nach GREEN die fokussierte Matrix, `py_compile`, breite Regression, Top-5, `git diff --check`, Remedy-DB-Hash und einen unabhängigen Current-Snapshot-Review aus.
8. Setze F2.2 nur bei unabhängigem APPROVE ohne offene P0–P2 auf GO.

Die bindenden F2.2-RED-Verträge aus dem freigegebenen Plan sind:

- Root kommt aus `MORPHIC_ADMIN_CATALOG_DIR` oder einem dedizierten User-Data-Default unter `%LOCALAPPDATA%/MorphicEngine/admin_catalog`.
- `runtime_root()` darf wegen seines Worktree-Defaults ausdrücklich nicht der Admin-Catalog-Default sein.
- Kontextnamespace muss kanonisch und kollisionsfrei sein.
- Pfadtraversierung muss fail-closed abgewiesen werden.
- systemweiter Scope ist standardmäßig nicht schreibbar.
- kanonisch aufgelöste Pfade innerhalb des Projektroots, von Export-/Archivroots oder über Symlink-/Windows-Reparse-Ausbruch werden fail-closed abgewiesen.

Wichtige Gategrenze: F2.2 ist zunächst die im Plan definierte Pfadpolicy. Ziehe Schema-Migration, Backup/Recovery, HMAC, Service-Auth, API/UI oder Runtime-Konsumtion nicht still in diesen Block. F2.3 bleibt Backup/Recovery; F2.4 bleibt Audit-Integritätsstufen/HMAC. Falls eine Schema-Migration für bestehende Stores nötig erscheint, zuerst die Plan- und Gatezuordnung explizit prüfen und dokumentieren, nicht improvisieren.

Arbeite autonom, präzise, deutschsprachig und TDD-basiert. Kombiniere nur kompatible Schritte ohne Qualitätsverlust. Frage nur, wenn eine nicht auflösbare Entscheidung die Gategrenze verändert. Melde keine Freigabe ohne reale Tool-Evidenz. Ändere oder lösche niemals `Benutzer_Archive__ws-*` oder fremde Dirty-Worktree-Arbeit. Keine Secrets lesen oder dokumentieren.

---
