# AURELIA Tiefenanalyse V6 — Executive Summary

**Datum:** 2026-08-28, 10:44–10:55 CEST · **Basis:** Haupt-Checkout `codex/aurelia-vorbereitung` @ `8706186` + vollständige Branch-/Worktree-/Remote-Inventur · **Modus:** strikt lesend.

## 1. Gesamturteil

AURELIA ist konzeptionell ausgereift, verfassungsstark und diszipliniert geführt.
Die Codebasis ist sauber (React 19/TanStack Start, Better Auth, Kysely,
Postgres/PGlite, 9 Testdateien mit ~175 Testfällen), die Phase-1-Schale
(Auth, Mandanten, Rollen, Konzeptportal) ist **funktional vorhanden** —
Auth „funktionsfähig implementiert", Portal zu ~90 % statisches
Konzeptportal mit einem echten App-Kern (3 Server-Functions für
Mandanten-Memberships).

Das Projekt steht unverändert an **einer engen, zweifachen Flaschenhalsstelle**:

1. **Infrastruktur:** Gate `G0-SRV-0` (externer Backup-/Restore-Nachweis auf M G1)
   ist seit dem 25.08. offen. **0 von 13 Servergates bestanden**, 0/6 technische
   Abnahmen der Gate-Voraussetzungen (nur Betreiberbestätigungen),
   `server_changes_started: false`.
2. **Konsolidierung:** Vier parallele Branchlinien mit divergenten Kanänen.
   K1 steckt bei **Task 3 von 14** (TDD-Korrektur implementiert, erneutes
   Spec-Review ausstehend → Tasks 4–14 blockiert). **13 Commits unpushed**,
   15 G0-Governance-Pläne (**17.091 Zeilen**) und ein Migrationsplan
   (**1.949 Zeilen**) nur ungetrackt lokal, 2 Scanner-Dateien als bewusstes
   Dirty-Overlay. Die gesamte jüngste Denkarbeit existiert **genau einmal**,
   auf einer Windows-Workstation, die laut eigenem Migrationsdesign vom
   27.08. demnächst neu installiert werden soll.

**Neu in V6 (gegenüber V5):**

- **E1-Blocker entschärft:** Alle drei Worktrees besitzen vollständige
  `node_modules`-Installationen (~253 Pakete, 24.–25.08.). Die Qualitätskette
  ist dort **ohne jede Installation lauffähig** — V5s Befund „kein lokales Gate
  ausführbar" gilt nur für den Haupt-Checkout.
- **Korrektur eines V5-Befunds:** `g0-governance` hat die Ground-Zero-/Analyse-
  Dokumente **nicht gelöscht** — sie wurden erst in `8706186` hinzugefügt, dem
  einen Commit, der dem Zweig fehlt (verifiziert: kein Lösch-Commit in der
  Historie). Der Zweig trägt consequently noch den alten Debian-Kanon.
- **GitHub-Fernzustand präzisiert:** 5 Branches, 0 Tags, 0 PR-Refs, **kein CI
  definiert** (`.github/workflows` existierte nie), Repo privat, `gh`-Keyring-
  Token ungültig (HTTP 401) — git funktioniert via Windows Credential Manager.
- **Fortschritt seit V5-Timestamp: null** — das Repo hat sich seit `aec827f`
  (27.08., 09:24) nicht geändert. V6 bestätigt V5s Prozentmodell im Kern.

**Rollup (modelliert):** Gesamtfortschritt ≈ **30–35 %**
(produktlinien-gewichtet ≈ 35 %; Methodik in `04`).

## 2. Was steht gut (Top 5)

| # | Stärke | Beleg |
|---|---|---|
| 1 | Verfassungs- und Gate-Architektur: 111 vergebene Produkt-IDs, 13+1 G0-SRV-Gates mit Stop-Kriterien, Destruktionssperre fail-closed | `AGENTS.project.md`, `GATE-STATUS.md`, Ground-Zero-Spec §11–12 |
| 2 | Phase-1-Auth-Schale produktionsnah: `__Host-`-Cookies, Bearer-Fallback, Fetch-Metadata-Isolation, beweisbarer Sign-out, 326 Z. Gate-Tests | `src/lib/auth/`, `memberships.ts` |
| 3 | Maschinell prüfbarer Kanon (Branch `kanon-implementation`) + fail-closed Push-Graph-Scanner mit TS-AST-Adjudikation (K1) | `scripts/canon-contract.mjs`, `check-push-graph.mjs` |
| 4 | Zwei-Spuren-Qualitätsrouting (Spur A/B, fail-closed zu B) als Prozessinnovation | `QUALITY-ROUTING.md` (K1) |
| 5 | Konsistentes, zugängliches Konzeptportal (WCAG-Ansatz, typisierte ID-Systematik, responsive DataTables) | `src/lib/concept/`, `components/concept/` |

## 3. Was blockiert (Top 5)

| # | Blocker | Schwere |
|---|---|---|
| 1 | `G0-SRV-0` ohne Backup-/Restore-Nachweis → alle Produktphasen pausiert | 🔴 |
| 2 | K1-Task-3-Review-Stau → Tasks 4–14 blockiert (u. a. Kanonmatrix, Testrunner-Fix, Auth-Abnahme) | 🟠 |
| 3 | Single Point of Failure Windows-Workstation (13 unpushed Commits + 19.040 Zeilen ungetrackte Pläne + 2 Dirty-Dateien) — kurz vor geplanter Linux-Neuinstallation | 🟠 |
| 4 | Keine RLS/keine CHECK-Constraints; Isolation nur applikativ; kein CSP/Security-Header | 🟠 |
| 5 | Kein CI, keine Branch-Protection, `gh` ohne gültigen Token → Zweitaugenprinzip automatisiert nicht durchsetzbar | 🟡 |

## 4. Dringlichste Einzelschritte

1. **Qualitätskette im Worktree ausführen** (E1, ohne Installation) — schließt
   die L3.4-Evidenzlücke sofort.
2. **K1-Task-3-Spec-Review terminieren** → danach Qualitätsreview → Tasks 4–14.
3. **Replikationskapsel Layer A/B/C** nach dem eigenen Migrationsdesign —
   Generalprobe für `G0-SRV-0`/WV01 und Beseitigung des SPOF in einem Schritt.
4. **`G0-SRV-0`-Nachweis erbringen** → alleinige Tür zu Gates 1–12, AUDIT-02,
   Phase-1-Abschluss.
5. **`gh` re-authentifizieren** + CI/Branch-Protection beim nächsten abgegrenzten Push.

## 5. Verhältnis zu V5

V6 bestätigt die V5-Befunde in der Substanz (identische Prozentwerte, gleiche
Blocker-Hierarchie) und korrigiert präzise drei Punkte: Lösch-Behauptung
(`g0-governance`), node_modules-Reichweite (Worktrees), GitHub-CI-Feststellung
(neu, hart verifiziert). Details: `08_DIFFERENZEN_ZU_V5_V6.md`.
