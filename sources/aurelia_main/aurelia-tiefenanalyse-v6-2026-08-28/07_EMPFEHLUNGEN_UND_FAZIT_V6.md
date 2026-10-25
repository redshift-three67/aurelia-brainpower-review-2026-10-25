# AURELIA Tiefenanalyse V6 — Empfehlungen und Fazit

## 1. Kernaussage

> AURELIA hat sein Konzept-, Werkzeug- und Verfassungsproblem gelöst — und hat
> es noch **nicht**, seinen Konsolidierungs- und Nachweisstand dauerhaft
> unantastbar zu machen. Das größte Sachrisiko ist nicht Code oder Konzept,
> sondern **unreplizierte, un-reviewte, ungemergte Arbeit auf einer einzigen
> Workstation**, die nach eigenem Plan demnächst neu installiert wird.

## 2. Prioritätenkette (7 Stufen)

| Stufe | Maßnahme | Entblockt | Aufwand |
|---|---|---|---|
| 1 | Qualitätskette im Worktree ausführen (N1) — Test-/Typecheck-Evidenz ohne Installation | Evidenzbasis, L3.4 | Stunden |
| 2 | `gh` re-authentifizieren (N2) → GitHub-Evidenz (E2) | L4.2 | Minuten |
| 3 | K1-Task 3: fokussiertes Spec-Review terminieren (N5), danach Qualitätsreview; Eskalationsfenster in QUALITY-ROUTING ergänzen (N4) | Tasks 4–14 | 1 Review-Tag |
| 4 | K1-Tasks 4–14 ausführen (Kanonmatrix, Validator, Windows-Runner N9, Auth-Abnahme) | Einheitlicher Kanon-Zweig | Tage |
| 5 | Replikationskapsel Layer A→B→C inkl. Restaurationsnachweis (N3), dann abgegrenzter Fast-Forward-Push | SPOF beseitigt; Generalprobe WV01/G0-SRV-0 | 1 Tag |
| 6 | `G0-SRV-0`: externer Backup-/Restore-Nachweis erbringen und als `G0-SRV-0: bestanden` protokollieren | Gates 1–12, AUDIT-02, Phase-1-Abschluss | Betreiberaktion |
| 7 | Gatefolge 1–12 sequenziell (ECC-Runbook N13 in Gate 2); parallel N6/N7/N8 (Constraints, Header, RLS) und N10–N12 (CI, Kanon-Deckung, Gate-Spiegel) | Phase-1-Abnahme → Phasen ≥ 2 | Wochen |

**Bewusst nicht:** Serveränderungen vor Stufe 6 · K6–K8/H5–H8 · Video ·
Lovable-Publish · `/opt/radiquant4` · Passkeys produktiv · Governance-Genesis.

## 3. Stabilitäts- und Akkuranzselbsteinschätzung

| Dimension | Einschätzung |
|---|---|
| Stabilität | **hoch** — alle 15 Prozentwerte identisch zu V5 (gleiche Repo-Basis, keine Mutation dazwischen); Modellformel unverändert |
| Akkuranz | **hoch mit 3 Korrekturen gegenüber V5** — jede verifiziert (Git-Archäologie, Verzeichnisprüfungen, Remote-Reads), dokumentiert in `08` |
| Präzision | **hoch** — zwei bewusste Ausnahmen bleiben benannt: (1) Portal-Altverweise bis AUDIT-02, (2) ungetrackte Governance-/Migrationspläne; beide sind dokumentiert und adressierbar |
| Abdeckung | vollständige Inventare: 5 Branches, 4 Worktrees, Remote-Heads, `src/`/`scripts/`/`migrations/`/`server/`/`docs/`, 9 Analysedokumente von V5 |

## 4. Fazit

Der Projektzustand ist **konsistent, ehrlich und gut verfasst**. Die
Governance-Maschinerie (Gates, Kanon-Contract, Scanner, Qualitätsrouting,
Migrationsdesign) ist auf einem Niveau, das viele Professional-Teams nicht
haben. Genau deshalb ist der nächste Schritt kein neuer Entwurf, sondern
**Ausführung**: ein Review, ein Push, eine Kapsel, ein Restore-Nachweis.

Die Verfassung selbst sagt es vor: *„Qualität vor Menge. Nächste Phase nur bei
ehrlicher Abnahme der vorigen."* — Die Abnahme-Schritte 3–6 der Prioritätenkette
sind genau diese Ehrlichkeit in Werkzeugform.

## 5. Verhältnis zu V5 und früheren Analysen

- V1–V3 (25.08.): Erst- bis Drittanalyse inkl. read-only Serverinventur;
  V3-Befunde = Abnahmekriterien des Ground-Zero-Designs.
- V4 (25.08.): Neuanalyse nach der Ubuntu-Kanon-Wende, letzte mit Server-/Build-
  Ausführung.
- V5 (28.08. morgens): erste Analyse der Selbstorganisationsmaschinerie
  (Branchlinien, Konsolidierungsprogramme, zwei Gate-Systeme).
- **V6 (28.08., dieses Dokument):** Bestätigung der V5-Substanz, drei
  präzisierte/korrigierte Befunde, hart verifizierter GitHub-Fernzustand,
  neue Durchsetzungsvorschläge (N1–N2, N7, N12, N14). Das Prozentmodell ist
  stabil; Evidenzqualität ≠ Fortschritt.
