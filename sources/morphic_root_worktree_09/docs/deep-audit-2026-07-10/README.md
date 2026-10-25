# Morphic V1 – codebasierte Tiefenanalyse

**Prüfstand:** 2026-07-10 · Worktree `operator-workbench-phase1` · Commit `619a1f5` · keine Remote-Repository-Konfiguration (`git remote -v` leer).

## Zweck und Grenzen

Diese Analyse trennt überprüften Ist-Code, Laufzeitbelege und Empfehlungen strikt. Sie bewertet **nicht** medizinische/therapeutische Wirksamkeit, sondern ausschließlich Implementierung, Datenschutz, Sicherheitsarchitektur, Bedienbarkeit und Betriebsreife. Personendaten aus Runtime-/Exportdateien wurden nicht in die Dokumentation übernommen.

| Phase | Dokument | Inhalt |
|---|---|---|
| 0 | [PHASE_0_BASIS_UND_VERIFIKATION.md](PHASE_0_BASIS_UND_VERIFIKATION.md) | Scope, Befehle, reale Laufzeit und Reifegrad |
| 1 | [PHASE_1_ARCHITEKTUR_WORKFLOW_ALGORITHMEN.md](PHASE_1_ARCHITEKTUR_WORKFLOW_ALGORITHMEN.md) | Struktur, Ein-/Ausstiege, 11 UI-Phasen, 12 Substeps, Algorithmen |
| 2 | [PHASE_2_SECURITY_DSGVO_AUTH_MULTITENANT.md](PHASE_2_SECURITY_DSGVO_AUTH_MULTITENANT.md) | Datenschutz, API-Security, Ownership und Tenant-Isolation |
| 3 | [PHASE_3_FRONTEND_UIUX_GOOGLE_2026.md](PHASE_3_FRONTEND_UIUX_GOOGLE_2026.md) | UI/UX, Accessibility, Performance, Google-/web.dev-Abgleich |
| 4 | [PHASE_4_BEFUND_MATRIX_UND_INNOVATIONEN.md](PHASE_4_BEFUND_MATRIX_UND_INNOVATIONEN.md) | priorisierte Lücken, stabile Innovationen und Gate-Folgeplan |

## Kurzstatus

| Dimension | Status | Beleg |
|---|---|---|
| Testnetz | grün | `PYTHONUTF8=1 OPENBLAS_NUM_THREADS=1 /c/morphic_v1/.venv/Scripts/python.exe -m pytest tests -q` → **282 passed, 2 skipped** |
| CLI | bootfähig | `python -m apps.cli.main --help`, `scan --help`, `privacy --help` erfolgreich |
| Web-Shell | loopback-smoke grün | Uvicorn auf `127.0.0.1:8001`; `/`, `/api/status`, `/api/health`, `/static/app.js` jeweils HTTP 200 |
| Auth/Multitenancy | Vorbereitungs-/lokaler Modus | API-Key optional; dateibasierter Operator/Workspace/Tenant-Kontext, kein Identity Provider/keine RBAC |
| DSGVO | Teilimplementiert | lokale Manifeste, Safe View, Löschkaskade, Audit; keine Verschlüsselung/Retention-Policy-Automation |
| Produktivfreigabe Internet | nicht gegeben | offene Befunde S-01 bis S-07 in Phase 2 |

Alle Änderungen dieser Lieferung sind reine Dokumentation unter diesem Ordner; produktiver Code und Konfiguration bleiben unverändert.
