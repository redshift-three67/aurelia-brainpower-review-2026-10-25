# AURELIA — Tiefenanalyse V4: Metadaten & Methodik

**Zeitstempel der Erstellung:** 2026-08-25, 19:39 CEST  
**Version:** 4.0 — **vollständige Neuanalyse von Null**, unter Einbezug einer erneuten, vertieften Serverinventur und einer fundamentalen Kanon-Wende, die zwischen V3 (17:33 CEST) und jetzt stattgefunden hat  
**Ablageort:** `aurelia-tiefenanalyse-v4-2026-08-25/`  
**Analysegegenstand:** Projekt AURELIA (Codebasis) **und** Server `185.242.115.210` (bisheriges M-G1-System) **und** der neu freigegebene Ground-Zero-Neuaufbauplan

---

## 1. Die entscheidende Neuigkeit seit V3

Zwischen der V3-Analyse (17:33 CEST) und dieser V4-Analyse (19:39 CEST) hat der Betreiber auf Basis der V3-Serverbefunde eine **strategische Kurskorrektur freigegeben**, dokumentiert im Commit `8706186` „Plan AURELIA server ground zero" (18:49 CEST) und der neuen Spezifikation `docs/superpowers/specs/2026-08-25-aurelia-ground-zero-server-design.md`:

- **Phase 1 ist am neuen Infrastruktur-Gate `G0-SRV-GROUND-ZERO` pausiert.** Produktarbeit (AUDIT-02) ruht, bis der Server-Neuaufbau abgenommen ist.
- **Zielbetriebssystem wechselt von Debian Bookworm zu Ubuntu Server 24.04.4 LTS** (plus minimalem GNOME für einen isolierten Codex-Entwicklungsnutzer).
- **Hardware-Korrektur:** tatsächlich 2× 2 TB WD_BLACK SN850X (nicht 2× 1 TB wie zuvor dokumentiert); ECC-Status des RAM ist unbewiesen.
- **Die komplette V3-Sicherheitsbefundliste wurde 1:1 als Abnahmekriterien-Tabelle in die neue Spezifikation übernommen** (Root-SSH, NOPASSWD:ALL, Klartext-Cron-Secret, Doppelorchestrierung, 23.292 Fehlversuche, fehlender Offsite-Nachweis, 200-GB-Docker-Müll, NVML-Mismatch, Strapi-Crashloop, öffentliches xRDP/Port 8000, fehlgeschlagene Units).
- **Es gilt ein strikter destruktiver Sperrmechanismus:** `destructive_actions_allowed: false` in `docs/project-control/ground-zero/GATE-STATUS.md`, aktuelles Gate `G0-SRV-0` (Backup/Restore-Nachweis), noch **keine** Serveränderung begonnen.

**Bedeutung für V4:** Diese Analyse bewertet nicht mehr nur „ist AURELIA umsetzbar", sondern zusätzlich **„ist der Ground-Zero-Serverneuaufbauplan selbst professionell, akkurat und umsetzbar"** — als eigenständige, vorgeschaltete Frage vor jeder Produktphase.

---

## 2. Verifikationsgrad dieser Session

| Quellblock | Methode | Verifikation |
|---|---|---|
| Vollständiger neuer Kanon (`AGENTS.project.md`, `docs/STATUS.md`, Ground-Zero-Design, Preflight-Plan, `docs/project-control/README.md`, `GATE-STATUS.md`, `26-wiedervorlage.md`, `14-hardware.md`, `11-llm-handoff.md`) | Volllesung, 19:00–19:35 CEST | ✅ 100 % |
| Codebasis (git log, `npm test`, `npm run typecheck`) | Live-Ausführung 19:36 CEST | ✅ |
| Server `185.242.115.210` — erneute Tiefeninventur (Delta zu V3: Paket-Updates, TLS-Zertifikate, PostgreSQL-Datenbanken/-Erweiterungen, Journal-Fehler in Echtzeit, systemd-Unit-Definitionen, Restart-Zähler, Webserver-Konfiguration, Datei-Limits) | SSH `klaus999`, ausschließlich lesende Kommandos, 19:35–19:39 CEST | ✅ |

**Wichtiger Befund zur Konsistenzprüfung:** Der Server zeigt in dieser Session **exakt dieselben** kritischen Symptome wie in V3 (NVML-Mismatch identisch, `radiquant4-web` weiterhin im Crashloop) — das bestätigt die Kanon-Aussage `server_changes_started: false` unabhängig und glaubwürdig.

## 3. Dokumentenstruktur

| Datei | Inhalt |
|---|---|
| `01_EXECUTIVE_SUMMARY_V4.md` | Gesamturteil unter Einbezug der Ground-Zero-Wende |
| `02_PROJEKTANALYSE_VON_NULL_V4.md` | Kanon, Codebestand, verifizierte Defekte |
| `03_SERVERANALYSE_ALTSYSTEM_V4.md` | Vollständige Neuinventur des (unverändert laufenden) Altsystems inkl. neuer Live-Befunde |
| `04_GROUND_ZERO_PLANBEWERTUNG_V4.md` | **Neu:** Eigenständige Professionalitäts-/Akkuranz-/Umsetzbarkeitsprüfung des Ground-Zero-Server-Designs und -Preflightplans |
| `05_LUECKEN_UND_RISIKEN_V4.md` | Kombinierte Lücken- & Risikomatrix (Projekt + Altserver + Ground-Zero-Plan) |
| `06_ERGAENZENDE_INNOVATIONEN_V4.md` | Verfassungsgeprüfte Innovationsvorschläge, ergänzt um Ground-Zero-Kontext |
| `07_PHASENPLAN_V4.md` | Gate-Sequenz `G0-SRV-0…12` **plus** Produktphasen 1–10 mit Subschritten, Abnahmekriterien, Aufwandsbändern |
| `08_VORGEHENSWEISE_UND_FAZIT_V4.md` | Architekten-Empfehlung, Prioritätenkette, Schlussurteil |
