# 02 — Projektanalyse von Null V4 (Codebasis & Kanon, 2026-08-25 19:39 CEST)

---

## 1. Produktkanon — Stand nach der Ground-Zero-Wende

### 1.1 Was sich am Produktkanon selbst NICHT geändert hat
Alle in V1–V3 geprüften Kernentscheidungen bleiben unverändert gültig und wurden in `AGENTS.project.md` erneut bestätigt: D01–D08, D10, D12–D24 gesetzt; C01–C12 gesetzt; X-Katalog akzeptiert; K1–K5 gesetzt/K6–K8 gesperrt; H1–H3 gesetzt; VRAM-Budget 2/16/2; kein Video/WebRTC (D10); CopyGuard in RAM/NVMe (nicht VRAM).

### 1.2 Was sich am Kanon geändert hat (neu, gegenüber V3)
| Aspekt | Vorher (bis V3) | Jetzt (V4) | Quelle |
|---|---|---|---|
| Produktphasen-Status | „Phase 1 läuft" | **„Phase 1 pausiert am Gate `G0-SRV-GROUND-ZERO`"** | `AGENTS.project.md` Z.10 |
| Ziel-OS | Debian Bookworm | **Ubuntu Server 24.04.4 LTS + minimales GNOME** | Ground-Zero-Design §3.1 |
| Storage-Hardware | 2× 1 TB NVMe | **2× 2 TB WD_BLACK SN850X (korrigiert)** | `docs/14-hardware.md` |
| ECC-Status RAM | nicht thematisiert | **explizit als unbewiesen markiert** (`Memory Error Correction Type: None` laut DMI) | Ground-Zero-Design §2.1 |
| Neue harte Regeln | 22 Regeln | **26 Regeln** (Nr. 23–26: Ubuntu-Zielsystem, Lösch-/Reinstall-Sperre vor `G0-SRV-0`, Codex-Nutzerisolation, kein öffentliches SSH/RDP/PG/Redis/Monitoring) | `AGENTS.project.md` |
| Neuer Ordner | — | **`docs/project-control/`** als lesender Einstieg mit Archivierung von V1–V3 und expliziter Sicherheitsgrenze für `source/`-Unterordner (`.gitignore`) | `docs/project-control/README.md` |
| Wiedervorlage WV01 | „Backup vor Art. 9" | **„Backup/Restore ab Ground Zero UND erneut vor Art. 9"** (verschärft, zweifache Prüfung) | `docs/26-wiedervorlage.md` |

### 1.3 Bewertung dieser Kanon-Wende
Das ist **beispielhaftes Reagieren auf eine Tiefenanalyse**: Statt die V3-Befunde punktuell zu patchen, wurde die gesamte Infrastruktur-Grundlage neu gedacht und formal gategesteuert. Die explizite Übernahme aller zwölf V3-Sicherheitsbefunde als tabellarische Abnahmekriterien (Ground-Zero-Design §10) ist handwerklich vorbildlich — sie verhindert, dass ein einzelner Befund beim Neuaufbau vergessen wird.

---

## 2. Codebasis — frisch verifiziert (19:36–19:39 CEST)

### 2.1 Unveränderte Befunde (Bestätigung, keine Regression, aber auch kein Fortschritt)
| ID | Befund | Ergebnis dieser Session |
|---|---|---|
| DEF-01 | `npm test` | 15 Tests, **14 grün / 1 rot** (identisch zu V2/V3) |
| DEF-02 | `npm run typecheck` | weiterhin rot: `TS5102 baseUrl removed`, `TS2688 vite/client` |
| DEF-04 | `scripts/canon-contract.mjs` | **existiert weiterhin nicht** — der freigegebene Bereinigungsplan vom 24.08. ist nach wie vor nicht ausgeführt |

### 2.2 Git-Historie (frisch geprüft)
```
8706186 Plan AURELIA server ground zero          (25.08., 18:49 CEST — NEU seit V3)
a726346 chore: ignore local worktrees
e55ed59 Plan Aurelia canon reconciliation
9a7be72 Document Aurelia pre-planning design
b858ccd Start Phase 1 shell: accept X catalogue, lock no-video, turn auth on.
```
Der neueste Commit ist ausschließlich Dokumentation/Governance (siehe `git show --stat 8706186`: 14 geänderte Dateien, alle in `docs/`, `AGENTS.project.md`, `SECURITY.md`, `.gitignore` — **kein Anwendungscode**). Das bestätigt exakt die Selbstauskunft der Spezifikation: „Ground Zero löst die Codeprobleme nicht."

### 2.3 Unverändertes Soll-/Ist-Substanzbild
Die in V1–V3 dokumentierte Differenz (WebSocket-Fachkanal, `aurelia-timerd`, `aurelia-gpud`, `aurelia-emitterd`, CopyGuard, Kernel-Registry, RLS/Envelope-Encryption, AnalysisDraft/HarmonizationLane, Computation Passport — alle **0 % implementiert**) besteht unverändert fort. Das ist erwartungskonform: Solange Ground Zero läuft, ist Produktarbeit (AUDIT-02) bewusst pausiert.

---

## 3. Zwischenfazit Projektebene
Der Produktkanon ist inhaltlich stabil und wurde durch die Ground-Zero-Wende **nicht verwässert, sondern konsequent verschärft**. Die Codebasis stagniert erwartungsgemäß. Die eigentliche Dynamik dieser Analysephase liegt auf der Infrastrukturebene (Dokument 03 und 04).
