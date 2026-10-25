# AURELIA — Tiefenanalyse V5: Phasen- und Prozentrollup

**Stand: 2026-08-28, 09:28 CEST · Nur-Lese-Analyse**

---

## 1. Methodik der Prozentwerte

Alle Prozentsätze sind **modellierte Fortschrittswerte**, transparent aus drei Dimensionen je Phase/Programm hergeleitet — keine gemessene Produktivität, keine Aufwandsprognose:

```
Fortschritt(Phase) = 0,30 × Planung + 0,50 × Umsetzung + 0,20 × Abnahme
```

- **Planung:** Verfassung/Design/Specs/Pläne vorhanden und freigegeben. Abzug, wenn Artefakte nur lokal existieren (uncommitted/ungetrackt = nicht repliziert, nicht reviewt, nicht versioniert).
- **Umsetzung:** Code, Migrationen, Nachweisartefakte tatsächlich vorhanden (nicht: geplant). Read-only Inventuren/Hashes zählen als minimale Ausführung.
- **Abnahme:** formale, dokumentierte Gate-/Review-Akzeptanz (Gate „bestanden", Review „PASS", Betreiberfreigabe im vorgeschriebenen Format). Ohne Protokoll = 0.

**Bewusste Verzerrung nach unten (konservative Auslegung):** fail-closed — fehlende Evidenz zählt als nicht erbracht (entspricht dem eigenen Projektgrundsatz „fehlender Nachweis ist kein PASS", `QUALITY-ROUTING.md` §1).

## 2. Detailherleitung je Phase

### Phase 0 — Konzept → **100 %**
Planung 1,0 (Verfassung, D/C/X/U gesetzt, abgenommen 2026-08-23/24) · Umsetzung 1,0 (Kanon in `src/lib/concept/*` + Portal) · Abnahme 1,0 (dokumentiert, `docs/09-roadmap.md`).

### G0-SRV-GROUND-ZERO → **≈ 20 %**
- Planung 0,90: Serverdesign + Preflight + Gatekette 0–12 vollständig; **Abzug** → effektiv 0,60, da 15 Governance-Plan-/Masterdateien ungetrackt und 13 Konsolidierungs-Commits unpushed sind (nicht repliziert).
- Umsetzung 0,05: nur read-only Teilinventur (2×2 TB SN850X identifiziert, RAID1 gesund, ISO-SHA-256 fixiert); `server_changes_started: false` — korrekt so.
- Abnahme 0,00: **0 von 13 Gates bestanden**; 6/6 Betreiberbestätigungen, 0/6 technische Abnahmen.
- Rechnung: 0,30×0,60 + 0,50×0,05 + 0,20×0 = **0,205 → ≈ 20 %**.

### Phase 1 — Gehäuse → **≈ 65 %**
- Planung 0,95: U09-Startbeschluss verriegelt, Verfassungsregeln 21–26, Portalrouten definiert.
- Umsetzung 0,75: Auth (Better Auth, Gate-Identity Ed25519/JWKS, SameSite-Isolation, Middleware-Chokepoint) ✅ · Mandanten/Mitgliedschaften inkl. Migration 0002 und 2-Mandanten-Isolationstest ✅ · Portal 23 Routen ✅ · Migrationsrunner ✅ · **Abzüge**: kein `data_class`-CHECK, keine RLS, Windows-Testrunner-Glob-Lücke, Portal-Altverweise (bewusst), Phase-1-Formalabnahme fehlt.
- Abnahme 0,00: Isolationstest-Zeremonie/AUDIT-02 pausiert bis G0-SRV-12.
- Rechnung: 0,30×0,95 + 0,50×0,75 + 0 = **0,66 → ≈ 65 %**.

### Phasen 2–8, 10 (Produktphasen) → **≈ 18–22 % je Phase**
- Planung 0,60–0,75: Kapiteldateien `docs/04–24` definieren Compute, Daten, Kernel-ABI, Live/Timer, Wellbeing, CUDA, Clipboard, Kozyrev, Standalone — tief, aber ohne freigegebene Umsetzungsspezifikationen je Phase.
- Umsetzung 0, Abnahme 0 (bewusst: keine Module, kein CUDA, kein USB, keine echten Klienten).
- Werte: P2 0,75→22 % · P3/P4/P5 0,70→21 % · P7 0,65→20 % · P6/P8/P10 0,60→18 %.

### Phase 9 — WebRTC/Medien → **N/A (gestrichen)**
D10/O08: keine Videos. Vom Plan entfernt; gilt als geschlossen, nicht als Rückstand.

### Querschnitt K1 — Kanonkonsolidierung → **≈ 16 %**
- Planung 1,0 (Design + Plan + Kanonmatrix-Zielbild).
- Umsetzung 0,18: T1/T2 vollständig, T3 ~80 % (4 Security-Fixes committet, Overlap-Korrektur uncommittet), T4–T14 0.
- Abnahme 0,14: 2 von 14 Tasks Doppel-PASS; T3 wartet auf erneutes Spec-Review.
- Rechnung: 0,30×1,0 + 0,50×0,18 + 0,20×0,14 = **0,418 — normiert auf den Konsolidierungszeitraum bis Merge: ≈ 16 % des Gesamtvorhabens** (K1 selbst abgeschlossen = Voraussetzung, nicht Produktfortschritt; deshalb bewusst niedrig gewichtet im Projektrollup).

### Querschnitt GATE-G0 (Governance) → **≈ 25 %**
- Planung 1,0 (Spec eingefroren mit Byte-Hash) — aber Pläne nur lokal → effektiv 0,85.
- Umsetzung 0,00 (kein Register, kein Validator-Code, keine Pins, kein Collector).
- Abnahme 0,00 (Operator-Freigabe nicht im vorgeschriebenen Signaturformat; §16-Abnahmekriterien offen).
- Rechnung: 0,30×0,85 + 0 + 0 = **≈ 25 %** (reiner Entwurfswert, bewusst ohne Umsetzungsanteil).

### Querschnitt Migration (Linux-Workstation) → **≈ 35 %**
- Planung 1,0 (Design approved, dokumentierter Checkpoint) — Plan ungetrackt → effektiv 0,85.
- Umsetzung 0,25: Ausgangslage vollständig inventarisiert (13/27 Commits, 2 Dirty-Dateien mit Hash, 15 untracked, 52 ignoriert, `git fsck` sauber) — Ausführung 0.
- Abnahme 0,00 (Restaurationsnachweis 13 Schritte nicht gefahren).
- Rechnung: 0,30×0,85 + 0,50×0,25 + 0 = **0,38 → ≈ 35 %**.

## 3. Gesamtrollup

| Block | Anteil am Modell | Wert | Gewichtet |
|---|---|---|---|
| Phase 0 | abgeschlossen | 100 % | — (Kredit) |
| G0-SRV | Voraussetzung aller Produktarbeit | 20 % | hoch |
| Phase 1 | aktuelle Produktphase | 65 % | hoch |
| Phasen 2–8, 10 | 9 Produktphasen | 18–22 % | mittel |
| K1 + Governance + Migration | Querschnitt | 16/25/35 % | mittel |
| **Gesamtprojekt (modelliert)** | | | **≈ 30–35 %** |

**Interpretation:** Der Wert drückt aus, dass Konzept und Verfassung (Phase 0) und ein großer Teil der Phase-1-Schale stehen, während die alles entscheidende Infrastrukturabnahme (G0-SRV) und die Kanonkonsolidierung (K1) noch vor der Tür stehen. **Kein einzelner Prozentpunkt der Produktphasen ≥ 2 ist durch Umsetzung gedeckt — gewollt und verfassungskonform.**

## 4. Prozentstand der 13 G0-SRV-Gates (Gates = Schritte)

| Schrittgruppe | Gates | Stand |
|---|---|---|
| bestanden | 0 | 0 % |
| in Vorbereitung/Teilinventur | 2 (G0-SRV-0 Design fertig, G0-SRV-1/2 teils) | ≈ 15–40 % je Gate |
| gesperrt (sequenziell) | 11 | 0 % |
| **Programmfortschritt Gates** | | **0/13 bestanden · ≈ 8 % Schrittdurchschnitt, 20 % programmweit inkl. Planung** |

## 5. Prozentstand K1-Schritte (14 Tasks)

| Gruppe | Tasks | Stand |
|---|---|---|
| abgenommen (Doppel-PASS) | T1, T2 | 14 % der Tasks |
| in Korrektur/Review | T3 | ~80 % Implementierung, 0 % Abnahme |
| blockiert | T4–T14 | 0 % |
| **Taskdurchschnitt** | | **≈ 18 % Umsetzung · ≈ 16 % Gesamtvorhaben** |
