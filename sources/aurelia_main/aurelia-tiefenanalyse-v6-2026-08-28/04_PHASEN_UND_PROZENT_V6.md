# AURELIA Tiefenanalyse V6 — Phasen, Schritte und Prozentwerte

## 1. Modellformel (unverändert zu V5, für Vergleichbarkeit)

```text
Fortschritt(Phase) = 0,30 × Planung + 0,50 × Umsetzung + 0,20 × Abnahme
```

Konservative, fail-closed-Auslegung: nicht ausführbare/unter Evidenzmangel
stehende Planung wird abgewertet; Prozentsätze sind **modelliert**, nicht
gemessen. „Umsetzung" zählt nur existierenden, verdrahteten Code bzw.
vollzogene Realitätsschritte — nicht Dokumentation.

## 2. Phasen- und Blockübersicht

| Block | Planung | Umsetzung | Abnahme | **Gesamt** | Δ zu V5 |
|---|---:|---:|---:|---:|---|
| Phase 0 Konzept | 100 % | 100 % | 100 % | **100 %** | = |
| G0-SRV Server Ground Zero | 60 % effektiv¹ | 5 % | 0 % (0/13 Gates) | **≈ 20 %** | = |
| Phase 1 Gehäuse | 95 % | 75 % | 0 % | **≈ 65 %** | = |
| Phase 2 Praxisorganisation | 75 % | 0 % | 0 % | **≈ 22 %** | = |
| Phase 3 Kernel-ABI + Raten | 70 % | 0 % | 0 % | **≈ 21 %** | = |
| Phase 4 Analyse strikt | 70 % | 0 % | 0 % | **≈ 21 %** | = |
| Phase 5 Harmonisierung | 70 % | 0 % | 0 % | **≈ 21 %** | = |
| Phase 6 Archiv/Trend/Report | 60 % | 0 % | 0 % | **≈ 18 %** | = |
| Phase 7 GPU-Härtung | 65 % | 0 % | 0 % | **≈ 20 %** | = |
| Phase 8 Quantum opt-in | 60 % | 0 % | 0 % | **≈ 18 %** | = |
| Phase 9 WebRTC + Medien | — | — | — | **N/A** ❌ gestrichen | = |
| Phase 10 Betrieb | 60 % | 0 % | 0 % | **≈ 18 %** | = |
| Querschnitt K1 Konsolidierung | 100 % (Design/Plan) | 18 % (T1–T3) | 14 % (2/14) | **≈ 16 %** | = |
| Querschnitt GATE-GOV-0 Governance | 85 % effektiv² | 0 % | 0 % | **≈ 25 %** | = |
| Querschnitt Linux-Migration | 85 % effektiv | 25 %³ | 0 % | **≈ 35 %** | = |

¹ 35 % der Planmasse (Ground-Zero-Doku 2.543 Z.) fehlt auf den Nebenlinien bzw.
ist dort historisch; im Hauptbaum vollständig → im Hauptbaum 90 %.
² Design eingefroren, aber ohne `REV-G0-DESIGN-APPROVAL` nicht ausführbar.
³ Inventur verifiziert + Evidenzdokumentation; noch kein Push/Kapsel/Restore.

## 3. Rechenwege (Nachvollziehung)

- G0-SRV: `0,30×0,60 + 0,50×0,05 + 0,20×0 = 0,205 → ≈ 20 %`
- Phase 1: `0,30×0,95 + 0,50×0,75 + 0,20×0 = 0,66 → ≈ 65 %`
- Phase 2–8/10: `0,30×Planung` allein (Umsetzung/Abnahme 0)
- K1: `0,30×1,0 + 0,50×0,18 + 0,20×0,14 = 0,418 → ≈ 16 %` (normiert auf
  14-Task-Gesamtvorhaben)
- GATE-GOV-0: `0,30×0,85 = 0,255 → ≈ 25 %`
- Migration: `0,30×0,85 + 0,50×0,25 = 0,38 → ≈ 35 %`

## 4. Gesamtprojekt (gewichtet)

Gewichtung der Produktlinie (Begründung: G0-SRV dominiert alle Produktphasen;
Phase 1 ist einzige teilweise umgesetzte Produktphase):

| Block | Gewicht | Fortschritt | Beitrag |
|---|---:|---:|---:|
| Phase 0 | 5 % | 100 % | 5,0 |
| G0-SRV | 30 % | 20 % | 6,0 |
| Phase 1 | 25 % | 65 % | 16,25 |
| Phase 2–8, 10 (je 5 %) | 40 % | Ø ≈ 19,9 % | 7,95 |
| **Summe** | **100 %** | | **≈ 35,2 %** |

**Gesamtfortschritt ≈ 30–35 %** (gewichtet ≈ 35 %; konservativ als Spanne
bericht). Querschnitte (K1 ≈ 16 %, Governance ≈ 25 %, Migration ≈ 35 %) werden
nicht in die Produktlinien-Summe gemischt, da sie Werkzeug-/Sicherheitsarbeit
für mehrere Phasen sind.

## 5. Schrittzahlen der aktiven Programme

### 5.1 G0-SRV-Gates

| Status | Gates | Schrittwert je Gate | Programmbeitrag |
|---|---|---|---|
| bestanden | 0/13 | 100 % | 0 % |
| in Vorbereitung | 2 (`G0-SRV-0`, `G0-SRV-1` teils, `G0-SRV-2` ≈ 40 %) | 15–40 % | ≈ 5 % |
| gesperrt | 10–11 | 0 % | 0 % |
| **Gesamt (Schrittdurchschnitt)** | | | **≈ 8 % rein, ≈ 20 % inkl. Planung** |

### 5.2 K1-Tasks

| Status | Tasks | Wert |
|---|---|---|
| abgenommen | 2/14 | 14 % |
| in Arbeit (T3, ~80 % implementiert, 0 % Abnahme) | 1 | ≈ 4 % |
| blockiert | 11/14 | 0 % |
| **Umsetzungs-/Gesamtwert** | | **≈ 18 % Umsetzung · ≈ 16 % gesamt** |

### 5.3 Qualitätskette (neu differenziert in V6)

| Umgebungs-/Werkzeugwert | Zustand |
|---|---|
| Test-Suiten vorhanden (9 Dateien, ~175 Fälle) | ✅ definiert |
| Ausführbar (Worktrees, node_modules vorhanden) | ✅ **jetzt möglich** (V5: nein) |
| Ausgeführt mit frischer Evidenz | ⬜ 0 % (Nur-Lese-Gebot; E1 steht offen) |
| CI-seitig erzwungen | ⬜ 0 % |

## 6. Stabilitätsaussage

Alle 15 Blockwerte sind **identisch zu V5** (erstellt 4 Stunden zuvor an
derselben Repo-Basis `8706186`/`aec827f`). Das ist das erwartete Ergebnis:
Zwischen den Analysen fand keine Repo-Mutation statt (letzter Commit 27.08.,
09:24). V6 ändert die **Evidenzqualität** (E1 ohne Installation möglich;
GitHub-CI-Feststellung hart verifiziert; zwei V5-Befunde korrigiert), nicht
die **Fortschrittswerte**.

## 7. Interpretation

- Der kritische Pfad läuft ausschließlich über **Nicht-Code-Arbeit**:
  Nachweis (G0-SRV-0), Review-Freigabe (K1-T3), Publikation/Replikation
  (Push + Kapsel), Betreiberentscheidungen.
- 100 % Phase 0 und ≈ 65 % Phase 1 sind **planungs-/schalengetragen**; die
  Produktlogik ab Phase 2 ist bewusst 0 % — verfassungskonform.
- Der größte relative Hebel liegt bei K1: +1 Review-Tag entsperrt 11 Tasks
  (≈ 79 % des Konsolidierungsvorhabens), die wiederum die Windows-Lücken
  (Testrunner, Vite-CLI, Browser-Smoke) schließen, die für die Migration
  gebraucht werden.
