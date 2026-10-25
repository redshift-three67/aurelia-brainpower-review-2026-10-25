# AURELIA — Tiefenanalyse V5, NACHTRAG: Evidenzstufen, Evidenzlücken und Nachvollziehbarkeitsleitfaden

**Nachtragszeitstempel:** 2026-08-28, ~09:50 CEST (gleiche Nur-Lese-Session wie 00–07)
**Anlass:** Follow-up des Betreibers („Benötigst Du noch weitere Informationen oder einen lesenden Zugriff?") — die Antwort wird hier konsolidiert, damit ein Entwickler den **Grenzwert jeder V5-Aussage** exakt nachvollziehen kann.
**Status:** Non-normativ bis zur Übernahme in eine freigegebene AURELIA-Spezifikation.

---

## 1. Kernaussage des Nachtrags

Die V5-Beurteilung (00–07) ist auf ihrer gewählten Evidenzbasis **vollständig und selbstkonsistent**. Was ihr fehlt, ist nicht Information im Projekt, sondern **Evidenzhöhe**: Alle Laufzeitqualitäten (Tests, Typecheck, Lint, Canon-/Scanner-Gates) sind *dokumentiert*, aber in dieser Session *nicht ausgeführt*; der GitHub-Zustand ist nur über anonyme Ref-Heads beobachtbar; der Server M G1 wurde bewusst nicht berührt (Befundstand = V4, 25.08.).

## 2. Evidenzstufen-Modell (E0–E3)

| Stufe | Zugang | Was wird messbar, das V5 nur dokumentiert | Schließt Lücken-ID | Trade-off | Verfassungsbezug |
|---|---|---|---|---|---|
| **E0** (V5-Basis, erbracht) | Statisches Lesen des Repos + `git ls-remote` | Inventar, Topologie, Kanonquellen, Gate-/Plan-Dokumente, Branch-Divergenz, Git-Status | — | keine Laufzeit-/Fernbefunde | konform (rein lesend) |
| **E1** (größter Mehrwert) | Freigabe für `npm install` bzw. `npm ci` (nur Dependencies, kein Build, kein Dev-Server) | Ausführung der Qualitätskette: `npm test` (Erwartung: 175 Tests Haupt-Checkout / 185 Kanon-Branch; **empirischer Test der Windows-Glob-Lücke**), `npm run typecheck`, `npm run lint`, `npm run check:auth`; je Worktree: `check:canon` (kanon), `check:k1-control` + `check:push-graph` mit `--base --head --mode full` (Erwartung: Exit 2 ohne Argumente = fail-closed) | **L3.4** (Qualitätskette inaktiv) empirisch belegt oder widerlegt | schreibt `node_modules` (lokal, gitignored) | nur mit Betreiberfreigabe; ändert kein getracktes File |
| **E2** (zweitgrößter Mehrwert) | Read-only GitHub-Token (nur `repo:read`, kein Schreibrecht) | PRs, Issues, Branch-Protection, Actions/CI-Runs, Commit-Status auf `redshift-three67/aurelia` (privat → anonym 404, siehe 02 §5) | **L4.1** (GitHub-Zustand unbekannt); beantwortet die im Governance-Design selbst als „unknown/red" geführte Branchschutz-Evidenz | Token existiert außerhalb des Repos; Geheimnisdiziplin nötig | Regel 25/26-Geist: nur lesend, keine Publikation |
| **E3** (optional) | Read-only SSH auf M G1 (unprivilegierter Nutzer, wie V3/V4) | Neüberprüfung der Altbefunde: NVML-Mismatch, `radiquant4-web`-Crashloop, offene Ports, failed Units — Befundstand aktuell **25.08. (V4)**, nicht 28.08. | Aktualisierung von **L1.4** (Restrisikofenster) | Serverberührung; nur lesend | Regel 25 (unprivilegierter Entwicklungsnutzer), Regel 26 (keine öffentlichen Adminports); **ersetzt nie** den G0-SRV-0-Nachweis selbst |

**Priorität:** E1 > E2 > E3. E1 liefert echte Gate-Evidenz für die nächste Analyse; E2 klärt den Replikationsschutz; E3 ist optional, weil die Serverfrage ohnehin erst durch den G0-SRV-0-Nachweis entschieden wird.

## 3. Bewusst NICHT angeforderte Zugriffe (und warum)

| Nicht angefragt | Begründung |
|---|---|
| Lesen der 52 ignorierten Analysquelldateien / V3-`source/`-Ordner | Enthalten das Klartext-DB-Geheimnis; Sicherheitsgrenze `docs/project-control/README.md` verbietet Weitergabe an externe LLMs/Reviewer — die V5-Analyse liest sie bewusst nicht |
| Operatorseitige Nachweise (USV-Kapazität, separates Backupsystem, DDoS-Umfang, IPMI-Funktionstest) | 0/6 technische Abnahmen (L1.2) sind **nur vor Ort als Gate-Acceptance** erbringbar; kein Lesen/Remote-Zugriff kann sie substituieren |
| K1-Task-3-Spec-Review-Ergebnis | Betreiber-/Reviewer-Entscheidung, nicht im Repo vorhanden; blockiert Tasks 4–14 bis zur Erbringung (L2.2/L5.2) |
| Schreibzugriffe jeder Art (Push, PR, Issue, Gate-Eintrag) | Ausdrücklich ausgeschlossen; `publication_gate` bleibt `blocked` |

## 4. Nachvollziehbarkeitsleitfaden für Entwickler (Claim → Quelle → Evidenztyp)

**Evidenztyp-Legende:** `LESEN` = Dateivolllesung · `GIT-R` = lesender Git-Befehl (`status`, `log`, `branch -vv`, `rev-list`, `worktree list`) · `REMOTE-R` = `git ls-remote` / anonymer API-Versuch · `EXEC` = **in V5 nicht ausgeführt** (nur dokumentierte Erwartung).

| V5-Aussage | Kanonische Quelle | Evidenztyp | Lücken-ID |
|---|---|---|---|
| Phase 1 pausiert am `G0-SRV-GROUND-ZERO`; `G0-SRV-0` wartet auf Backup/Restore-Nachweis | `AGENTS.project.md`, `docs/STATUS.md`, `docs/project-control/ground-zero/GATE-STATUS.md` | LESEN | L1.1 |
| 0/13 G0-SRV-Gates bestanden; 6/6 Betreiberbestätigungen, 0/6 technische Abnahmen | `GATE-STATUS.md` (Voraussetzungs- + Gateübersichtstabelle), Serverdesign §11 | LESEN | L1.2 |
| `server_changes_started: false`; Stop-Regel intakt | `GATE-STATUS.md` (YAML + Stop-Regel) | LESEN | L1.4 (Kontext) |
| 4 Branchlinien; `g0-governance` hat G0-SRV-/Analysedocs gelöscht und Phase-1-Pause entfernt | Worktree-Diffs/Logs (`.worktrees/*`), Branch-Matrix T6 in `03` | GIT-R | L2.1 |
| 13 unpushed Commits (`konsolidierung`), 15 ungetrackte G0-Pläne, 2 dirty Scanner-Dateien, 1 ungetrackter Migrationsplan | `git branch -vv` („ahead 13"), `git status` je Worktree, `ls-remote` | GIT-R + REMOTE-R | L2.3 |
| K1: T1/T2 abgenommen, T3 Review ausstehend, T4–T14 blockiert | `docs/project-control/K1-STATUS.md` (im Konsolidierungs-Worktree) | LESEN | L2.2 |
| Testinventar 175 (Haupt) / 185 (Kanon-Branch); **Ausführung erfolgte nicht** | `package.json` (`test`-Skript) + Dateizählung der 11/12 Suites | LESEN (Zählung) + EXEC (nicht) | L3.4 |
| Windows-Glob-Lücke („`npm test` findet ggf. 0 Skripttests") | K1-Plan Task 6/9 (dokumentierte Behauptung) | LESEN — **empirische Prüfung erst mit E1** | L3.4 |
| `node_modules` fehlt → alle lokalen Gates aktuell inaktiv | `Test-Path node_modules` = False | GIT-R/Shell (lesend) | L3.4 |
| `data_class='synthetic'` nur DB-Default + Konvention, kein CHECK/kein Test | `migrations/0002_tenants.sql` (Zeile 5), `src/lib/praxis/memberships.ts` | LESEN | L3.1 |
| Keine RLS, keine negativen Isolationstests | Arbeitspaket C der Vorbereitungsspezifikation (geplant) | LESEN | L3.2 |
| GitHub privat → anonyme API 404; Branch-Heads synchron außer konsolidierung +13 | `git ls-remote`, `api.github.com`-Versuch (404) | REMOTE-R | L4.1 |
| Governance-Design eingefroren (3.968 Zeilen, Byte-Hash), aber 0 % Umsetzung; Operator-Freigabe nicht im Signaturformat | G0-Governance-Spec, Masterplan (ungetrackt), Spec §10/§13/§16 | LESEN | L2.5 |
| Altserver-Befunde auf Stand 25.08. (V4), in V5 nicht neu geprüft | V4-Dokumente, `GATE-STATUS.md` | LESEN (Sekundär) | L1.4 |
| Prozentrollup ≈ 30–35 % | Modellformel 30/50/20 in `04` — **modelliert, nicht gemessen** | LESEN (Modell) | — |

**Rekonstruktionsregel für Dritte:** Jede V5-Aussage ist durch die Quellen Spalte 2 und den Evidenztyp Spalte 3 reproduzierbar. Wo `EXEC` steht, ist die Aussage eine dokumentierte Erwartung des Projekts, kein Messergebnis dieser Session — das ist der einzige bewusste Evidenzsprung der V5.

## 5. Aktualisierungspflicht (wenn E1/E2/E3 freigegeben werden)

1. Freigabe durch den Betreiber als explicit scope (z. B. „E1 erlaubt", „E2 erlaubt", „E3 erlaubt").
2. Ausführung ausschließlich im freigegebenen Umfang; Ergebnisse landen als **V6-Delta** (neuer Zeitstempel, gleiche Ordnerkonvention), nicht als Überschreibung der V5.
3. In V6 zu aktualisieren: Lücken-IDs L3.4 (E1), L4.1 (E2), L1.4 (E3); das Prozentmodell ändert sich dadurch **nicht** (Evidenzqualität ≠ Fortschritt).
4. Unabhängig davon gilt weiter die Änderungspflicht des project-control-README: Nach jedem Gateereignis `docs/STATUS.md` + Nachweis + README aktualisieren.

---

*Ende des Nachtrags. Erstellt ausschließlich aus lesenden Zugriffen; keine Konfiguration, kein Code, kein Git-Zustand wurde verändert.*
