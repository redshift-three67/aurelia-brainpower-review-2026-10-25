# K1-Projektstatus

Verifizierter Pre-Sync-Snapshot: 2026-08-25, Europe/Berlin. Die Aussagen zum
Remotezustand sind historische Snapshot-Evidenz, kein späterer Live-Status.

> **Historischer Nachweis:** Die Pre-Sync-Aussagebasis dieses Dokuments bleibt
> als historische Evidenz erhalten. Für den aktuellen lokalen K1-Arbeitsstand,
> einschließlich Task-, Dirty- und Prüflage, ist ausschließlich
> [`K1-CURRENT.json`](K1-CURRENT.json) maßgeblich. Ein lokaler Commit oder ein
> dortiger Testerfolg ist keine Publikations-, Server- oder Produktionsfreigabe.

```yaml
branch: codex/aurelia-konsolidierung
base: 8706186af01e10e4253e25abb31bf3577110dae4
implementation_checkpoint: 095e0a074eba55719c373207e980388c927f2240
plan: 54a5ab673b1adeb697e6d0b3da22f6583dfbd809
design: 7de43db7bdaf87132de6893daf6acdad46d9c9ba
historical_governance: a6a8e7dca456d14a6748b204b787b235fdedf9be
remote_k1_ref_at_verified_pre_sync: absent/unpublished
remote_mutation: false
server_mutation: false
history_rewrite: false
push_authorized: false
publication_gate: blocked
publication_gate_reason_categories: [credential_like, operational_identity]
sanitization_scope: V1/V2 branch-tip manifests only
server_gate_authority: docs/project-control/ground-zero/GATE-STATUS.md
```

Der Implementierungscheckpoint
`095e0a074eba55719c373207e980388c927f2240` bezeichnet den geprüften Stand der
Task-3-Implementierung **vor** diesem späteren Dokument-Handoff. Er ist deshalb
nicht als selbstreferenzieller aktueller Dokument-Commit zu lesen. Nach dem
Handoff darf `HEAD` auf einem Nachfolger liegen, muss diesen Checkpoint und die
Basis weiterhin enthalten.

K1 ist zum unten festgehaltenen Pre-Sync-Zeitpunkt eine ausschließlich lokale
Kanonkonsolidierung auf dem oben genannten Arbeitszweig. Der Remote-Tracking-Ref
`origin/codex/aurelia-konsolidierung` war nicht vorhanden; der Branch war damit
nicht aus einem frischen GitHub-Clone rekonstruierbar.
Alte Git-Objekte wurden nicht gelöscht. Die Sanitisierung schützt damit den
Branch-Tip von V1 und V2, entfernt aber keine bereits erreichbaren historischen
Fassungen.

Lokale Commits sind keine Publikationsfreigabe. Ein späterer Push oder eine
Änderung bereits veröffentlichter Historie braucht eine neue, ausdrücklich
abgegrenzte Freigabe.

Das Publikations-Gate ist ausschließlich lokal diagnostisch; ein Push ist
dadurch nicht autorisiert. K1 verändert oder rotiert weder V3 noch ein
Preview-Credential.

G0-SRV-Status bleibt unberührt. Seine alleinige Statusautorität bleibt
[`docs/project-control/ground-zero/GATE-STATUS.md`](ground-zero/GATE-STATUS.md);
K1 erlaubt keinen Serverzugriff und keine Servermutation.

## Task-Ledger am Implementierungscheckpoint

| Task | Commits | Zustand | Reviews |
|---|---|---|---|
| 1 | `12f6c55`, `09eeddf`, `273e8c5` | abgeschlossen | Spec- und Qualitätsreview PASS |
| 2 | `96f06d2`, `683c332` | abgeschlossen | Spec- und Qualitätsreview PASS |
| 3 | `e33c84b` plus lokale Korrekturcommits und Overlap-Enumeration-Umbau | abgeschlossen: Head-first-Enumeration implementiert, alle Review-Befunde geschlossen | Spec-Review PASS; Qualitäts-/Security-Review PASS (je nach Korrekturschleife) |
| 4 | `1257283` | abgeschlossen: K1_CANON, Active-Allowlist und initialer fail-closed Kanonvertrag; 8/8 Fixturetests grün | Primäre TDD-Verifikation; keine Spur-B-Eskalation in Task 4 |
| 5 | noch kein Commit | lokal abgeschlossen: Canon-Suite 31/31, `check:canon`, Typecheck und K1-Control grün; Commit nicht autorisiert | Spec-Review PASS (SPEC-01…05 geschlossen); scoped Quality-Schließungsreview PASS, keine offenen P0–P2-Befunde |

### Task-3-Abschluss (Overlap-Enumeration, 2026-08-28)

- Spec-Review und Qualitäts-/Security-Review des Overlap-Enumeration-Umbaus
  sind PASS (nach je einer Korrekturschleife; 53 Tests grün; Performance
  O(n+c+a) gemessen — adversariale Fälle ≤ 5 s, JWT-Rohmuster auf
  `{10,512}` je Segment begrenzt).
- Geschlossene Review-Befunde (Auswahl): K1-T3-Q-NEW-01/02/03 aus dem
  Qualitätsreview des Vorgängerstands, K1-T3-GRAMMAR-CONFLICT (Option Y,
  Betreiberentscheidung), K1-T3-QOV-01/02/03 aus dem Umbau-Review.
- `K1-T3-QOV-02` (Blobcache ohne Pfad bei pfadsensitiver Klassifikation,
  fail-open Unterzählung bei identischem Blob unter mehreren Pfaden) wurde
  per Betreiberentscheidung im Lauf gefixt: Cache-Schlüssel `blob\0pfad`,
  Regressionstest vorhanden; Scope-Erweiterung der eingefrorenen Region
  (Design B §14) dokumentiert im amendierten Overlap-Korrekturdesign.
- Task 4 ist als lokaler Commit `1257283` abgeschlossen. Task 5 ist lokal
  abgeschlossen: `check:canon`, 31/31 Canon-Vertragstests, Typecheck und
  K1-Control sind grün. Das Spec-Review ist PASS; SPEC-01…05 sind geschlossen.
  Die OS-Adversativbindung, exakten D01–D24-Locks, Trennung von Produktpause und
  sequenziellen Servergates sowie die aktuelle Chronologie sind korrigiert. Das
  scoped Quality-Schließungsreview ist PASS; es bestehen keine offenen
  P0–P2-Befunde. Task 6 wurde nicht begonnen und braucht eine separate Freigabe.
  Der Task-5-Commit und jeder Push bleiben unautorisiert. Das Publikations-Gate
  bleibt formal blocked.

## Verifiziertes Branchinventar vor dem Sync

| Ref | Verifizierter Commit | Rolle und Basis |
|---|---|---|
| `origin/main` | `b858ccdd258bb98d29cdf6622ce26f94a8524b3e` | veröffentlichte Main-Basis |
| `origin/codex/aurelia-vorbereitung` | `8706186af01e10e4253e25abb31bf3577110dae4` | veröffentlichte K1-Basis; gegenüber dem gleichnamigen lokalen Zweig `0/0` |
| lokal `codex/aurelia-g0-governance` | `a6a8e7dca456d14a6748b204b787b235fdedf9be` | historische Governance-Referenz auf Basis von `main` |
| lokal `codex/aurelia-kanon-implementation` | `b20ee873347c5fd767e2089c993f1cf93a625def` | historischer, nicht blind ausführbarer Entwurf auf Basis von `main` |
| lokal `codex/aurelia-konsolidierung` | `095e0a074eba55719c373207e980388c927f2240` | K1-Implementierungscheckpoint auf Basis von `8706186` |
| `origin/codex/aurelia-konsolidierung` | nicht vorhanden | zum verifizierten Pre-Sync-Zeitpunkt unveröffentlicht |

Die beiden historischen lokalen Zweige sind Referenzen, keine K1-Mergeziele.
Sie dürfen insbesondere nicht durch Merge, Rebase, Reset oder Cherry-pick in
K1 übernommen werden.

## Aggregierter Scanner-Sicherheitsstatus vor dem Sync

Die folgende Evidenz enthält nur Kategorien und Record-Anzahlen, keine
Fundwerte und keine sensiblen internen Pfade.

| Stand | Records | Aggregierte Kategorien |
|---|---:|---|
| `origin/main` | 5 | `credential_like=1`, `env_or_key_material=1`, `pii_or_operational_identity=2`, `unscannable=1` |
| lokal `codex/aurelia-g0-governance` | 5 | `credential_like=1`, `env_or_key_material=1`, `pii_or_operational_identity=2`, `unscannable=1` |
| lokal `codex/aurelia-kanon-implementation` | 5 | `credential_like=1`, `env_or_key_material=1`, `pii_or_operational_identity=2`, `unscannable=1` |
| `origin/codex/aurelia-vorbereitung` | 7 | dieselben fünf Records plus `absolute_user_path=2` |
| lokaler K1-Implementierungscheckpoint | 12 | `credential_like=1`, `env_or_key_material=1`, `pii_or_operational_identity=2`, `unscannable=1`, `absolute_user_path=7` |

Der Vergleich zeigt ausschließlich, dass die aggregierten Counts der beiden
historischen lokalen Zweige für `credential_like` und für den Gate-Grund, dessen
historischer technischer Name `pii_or_operational_identity` war und dessen
heutige kanonische Kategorie `operational_identity` ist, nicht höher als bei
`origin/main` sind. Gleiche Counts beweisen keine Mengenidentität: Neue oder
ersetzte Records können vorliegen. Der Vergleich ist daher weder ein Unbedenklichkeitsnachweis
noch eine Ausnahme- oder Pushautorisierung; das Publikations-Gate bleibt formal
blockiert.

## Sichere Wiederaufnahme aus einem späteren frischen Clone

### Grenzen gelten vor dem ersten Arbeitsbefehl

- Nicht auf `main` wechseln oder dort arbeiten.
- Kein Merge, Rebase, Reset, Cherry-pick und kein History-Rewrite.
- Kein Push ohne eine neue, ausdrückliche Publikationsentscheidung. Das gilt
  trotz einer aktuellen Sync-Anfrage, solange `publication_gate: blocked`
  bleibt.
- Kein Serverzugriff, SSH oder IPMI und keine Servermutation.
- Keine V3-Änderung und keine Credentialrotation.
- Keine Veröffentlichung eines `source/`-Ordners.
- `docs/project-control/K1-VERIFICATION.md` wird erst in Task 14 angelegt.

Solange `origin/codex/aurelia-konsolidierung` fehlt, ist der lokale K1-Stand
nicht aus GitHub wiederherstellbar: an dieser Stelle stoppen und keine
Ersatzbasis raten. Sobald der Ref nach einer gesonderten Freigabe vorhanden
ist, lautet der sichere Einstieg in einem frischen Clone:

```powershell
$ErrorActionPreference = "Stop"

git clone --no-checkout https://github.com/redshift-three67/aurelia.git aurelia
if ($LASTEXITCODE -ne 0) { throw "K1_RESUME_CLONE_FAILED" }

Set-Location aurelia

git fetch --prune origin
if ($LASTEXITCODE -ne 0) { throw "K1_RESUME_FETCH_FAILED" }

$null = git show-ref --verify refs/remotes/origin/codex/aurelia-konsolidierung
if ($LASTEXITCODE -ne 0) { throw "K1_RESUME_REMOTE_REF_ABSENT" }

git switch --track -c codex/aurelia-konsolidierung origin/codex/aurelia-konsolidierung
if ($LASTEXITCODE -ne 0) { throw "K1_RESUME_SWITCH_FAILED" }

$branch = git branch --show-current
if ($LASTEXITCODE -ne 0) { throw "K1_RESUME_BRANCH_READ_FAILED" }
if ($branch -ne "codex/aurelia-konsolidierung") {
  throw "K1_RESUME_BRANCH_MISMATCH"
}

$head = git rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_RESUME_HEAD_READ_FAILED" }
Write-Output $head

git merge-base --is-ancestor 8706186af01e10e4253e25abb31bf3577110dae4 HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_RESUME_BASE_ANCESTRY_FAILED" }

git merge-base --is-ancestor 095e0a074eba55719c373207e980388c927f2240 HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_RESUME_CHECKPOINT_ANCESTRY_FAILED" }

$worktreeState = @(git status --porcelain=v1)
if ($LASTEXITCODE -ne 0) { throw "K1_RESUME_STATUS_READ_FAILED" }
if ($worktreeState.Count -ne 0) { throw "K1_RESUME_WORKTREE_DIRTY" }
```

Der Clone nimmt wegen `--no-checkout` keinen Default-Branch in den Worktree auf.
Erst der explizite, geprüfte `git switch` aktiviert den K1-Zweig. Danach wird
ausschließlich die im Task-Ledger niedrigste nicht abgeschlossene und separat
freigegebene Aufgabe fortgesetzt: Tasks 1–5 sind lokal abgeschlossen; Task 6
wurde nicht begonnen und besitzt keine Ausführungsfreigabe.
Auch die Abnahme bleibt fail-closed:

```powershell
node --test scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_ACCEPT_SCANNER_TESTS_FAILED" }

npm run check:k1-control
if ($LASTEXITCODE -ne 0) { throw "K1_ACCEPT_CONTROL_FAILED" }

node --experimental-strip-types --test scripts/canon-contract.test.mjs
if ($LASTEXITCODE -ne 0) { throw "K1_ACCEPT_CANON_TESTS_FAILED" }

npm run check:canon
if ($LASTEXITCODE -ne 0) { throw "K1_ACCEPT_CANON_FAILED" }

npm run typecheck
if ($LASTEXITCODE -ne 0) { throw "K1_ACCEPT_TYPECHECK_FAILED" }

git diff --check 095e0a074eba55719c373207e980388c927f2240..HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_ACCEPT_COMMITTED_DIFF_CHECK_FAILED" }

git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "K1_ACCEPT_INDEX_DIFF_CHECK_FAILED" }

git diff --check
if ($LASTEXITCODE -ne 0) { throw "K1_ACCEPT_WORKTREE_DIFF_CHECK_FAILED" }

node scripts/check-push-graph.mjs --base origin/codex/aurelia-vorbereitung --head HEAD --mode full
if ($LASTEXITCODE -ne 1) { throw "K1_ACCEPT_SCANNER_EXIT_MISMATCH" }
```

Der reale Scanner bleibt erwartungsgemäß bei Exit 1, solange die oben nur
aggregiert dokumentierten Records existieren. Seine Ausgabe darf Kategorien,
Blob-IDs, Repositorypfade und Anzahlen enthalten, aber niemals Fundwerte. Das
nackte `npm run check:push-graph` ist absichtlich Exit 2, weil `--base` und
`--head` fehlen; es ist kein Abnahmebefehl.

Tasks 1–5 sind lokal abgeschlossen. Task 5 besitzt Spec- und scoped
Quality-Schließungsreview PASS ohne offene P0–P2-Befunde; sein Commit ist nicht
autorisiert. Task 6 wurde nicht begonnen und benötigt eine separate, ausdrücklich
abgegrenzte Ausführungsfreigabe.

Ein später ausdrücklich autorisierter Publikationsschritt muss den dann
beobachteten Remotezustand in einem neuen, datierten Nachfolge-Evidenzpunkt
dokumentieren. Dieser Snapshot bleibt unverändert historisch; der
Nachfolge-Evidenzpunkt darf keinen selbstreferenziellen Hash seines eigenen
Dokument-Commits verlangen oder behaupten.
