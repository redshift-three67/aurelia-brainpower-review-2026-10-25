# K1-Post-Sync-Evidenz vom 26. August 2026

Beobachtungszeit: `2026-08-26 08:33:37 +02:00`

Repository: privates Repository `redshift-three67/aurelia`

## Abgegrenzte Betreiberfreigabe

Der Betreiber gab eine einmalige, dokumentierte Ausnahme vom formal roten
Vollgraph-Publikationsgate frei. Sie galt ausschließlich für den Handoff-Sync
dieser drei Branches:

- `codex/aurelia-g0-governance`
- `codex/aurelia-kanon-implementation`
- `codex/aurelia-konsolidierung`

Die Ausnahme umfasste weder `main` noch einen erzwungenen Push, ein
History-Rewrite oder einen Serverzugriff. Ausgeführt wurde ein atomarer,
nicht erzwungener Push mit Upstream-Zuordnung für genau diese drei Branches.
Es wurde kein Connector verwendet.

## Live beobachtete Remote-Refs nach der ersten Übertragung

Unmittelbar nach der ersten Übertragungsrunde wurden mit einem live
ausgeführten `git ls-remote --heads` folgende Remote-Refs beobachtet:

| Remote-Ref | Beobachteter Commit |
|---|---|
| `refs/heads/codex/aurelia-g0-governance` | `a6a8e7dca456d14a6748b204b787b235fdedf9be` |
| `refs/heads/codex/aurelia-kanon-implementation` | `b20ee873347c5fd767e2089c993f1cf93a625def` |
| `refs/heads/codex/aurelia-konsolidierung` | `431695604f54a1fbea9e2d70d52ab27bc2ded16f` |
| `refs/heads/codex/aurelia-vorbereitung` | `8706186af01e10e4253e25abb31bf3577110dae4` |
| `refs/heads/main` | `b858ccdd258bb98d29cdf6622ce26f94a8524b3e` |

`main` und `codex/aurelia-vorbereitung` waren und blieben unverändert. Die drei
neu angelegten Remote-Branches entsprachen beim ersten Push exakt ihren
jeweiligen lokalen Heads.

Fünfzehn ungetrackte Governance-Artefakte, bestehend aus vierzehn
Planentwürfen und einer HTML-Statusdatei, wurden nicht übertragen. Ebenfalls
nicht übertragen wurden ignorierte Analyse-`source/`-Ordner sowie andere
ungetrackte oder ignorierte lokale Dateien. Keine dieser lokalen Dateien ist
eine ausführbare K1-Quelle.

Die dokumentierte Ausnahme umfasst exakt diese repo-relativen Pfade:

- `docs/superpowers/plans/2026-08-24-aurelia-g0-01-toolchain-directives-and-quality-gates.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-02-register-and-schema-core.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-03-transition-ledger.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-04-reviews-evidence-gates-no-waiver.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-05-cryptographic-bootstrap.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-06-transparency-and-witness.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-07-recovery-write-path.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-08-tcb-lifecycle.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-09-external-llm-and-egress.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-10-mg1-collector-contract.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-11-remote-governance.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-12-genesis-initial-manifest.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-13-g0-acceptance.md`
- `docs/superpowers/plans/2026-08-24-aurelia-g0-implementation-master.md`
- `docs/superpowers/plans/2026-08-25-aurelia-g0-status-live.html`

## Fortbestehendes Gate und Verbrauch der Ausnahme

Das Publikationsgate blieb formal `blocked`. Die Betreiberfreigabe legitimiert
nur den beschriebenen Handoff-Sync einschließlich des einmaligen
nachfolgenden Pushs dieses Evidenzcommits. Nach diesem Nachfolge-Sync ist die
Ausnahme verbraucht. Sie begründet keine fortdauernde Pushfreigabe;
`push_authorized: false` bleibt für jede künftige Änderung maßgeblich.

Dieses Dokument kann den Hash seines eigenen Commits nicht enthalten. Die oben
stehenden Commit-IDs belegen deshalb ausschließlich die erste
Übertragungsrunde. Die finale Abnahme des Nachfolge-Syncs darf erst nach der
Publikation dieses Evidenzcommits durch eine neue Live-Prüfung belegt werden:

1. `refs/heads/codex/aurelia-konsolidierung` und
   `refs/remotes/origin/codex/aurelia-konsolidierung` sind gleich.
2. Ahead/Behind ist exakt `0 0`.
3. In allen Worktrees sind die getrackten Zustände sauber; ungetrackte
   Governance-Dateien entsprechen exakt der oben dokumentierten Ausnahme.

Diese finale Prüfung wird hier nicht als bereits vor dem Evidenzcommit erfolgt
behauptet. Der folgende PowerShell-Block ist die fail-closed Abnahme nach dem
autorisierten Nachfolge-Push:

```powershell
$ErrorActionPreference = "Stop"

git fetch --prune origin
if ($LASTEXITCODE -ne 0) { throw "K1_SYNC_FINAL_FETCH_FAILED" }

$localK1 = git rev-parse refs/heads/codex/aurelia-konsolidierung
if ($LASTEXITCODE -ne 0) { throw "K1_SYNC_FINAL_LOCAL_K1_REF_FAILED" }

$expectedLiveRefs = [ordered]@{
  "refs/heads/codex/aurelia-g0-governance" = "a6a8e7dca456d14a6748b204b787b235fdedf9be"
  "refs/heads/codex/aurelia-kanon-implementation" = "b20ee873347c5fd767e2089c993f1cf93a625def"
  "refs/heads/codex/aurelia-konsolidierung" = $localK1
  "refs/heads/codex/aurelia-vorbereitung" = "8706186af01e10e4253e25abb31bf3577110dae4"
  "refs/heads/main" = "b858ccdd258bb98d29cdf6622ce26f94a8524b3e"
}

$liveRows = @(git ls-remote --exit-code --heads origin `
  refs/heads/codex/aurelia-g0-governance `
  refs/heads/codex/aurelia-kanon-implementation `
  refs/heads/codex/aurelia-konsolidierung `
  refs/heads/codex/aurelia-vorbereitung `
  refs/heads/main)
if ($LASTEXITCODE -ne 0) { throw "K1_SYNC_FINAL_LS_REMOTE_FAILED" }
if ($liveRows.Count -ne 5) { throw "K1_SYNC_FINAL_LIVE_REF_COUNT_MISMATCH" }

$observedLiveRefs = @($liveRows | ForEach-Object {
  $fields = $_ -split "\s+", 2
  if ($fields.Count -ne 2) { throw "K1_SYNC_FINAL_LIVE_REF_FORMAT_INVALID" }
  [pscustomobject]@{ Hash = $fields[0]; Ref = $fields[1] }
})
foreach ($expectedRef in $expectedLiveRefs.Keys) {
  $matches = @($observedLiveRefs | Where-Object { $_.Ref -ceq $expectedRef })
  if ($matches.Count -ne 1) { throw "K1_SYNC_FINAL_LIVE_REF_NOT_UNIQUE" }
  if ($matches[0].Hash -cne $expectedLiveRefs[$expectedRef]) {
    throw "K1_SYNC_FINAL_LIVE_REF_HASH_MISMATCH"
  }
}

$transferredBranches = @(
  "codex/aurelia-g0-governance",
  "codex/aurelia-kanon-implementation",
  "codex/aurelia-konsolidierung"
)
foreach ($branchName in $transferredBranches) {
  $localBranchHead = git rev-parse "refs/heads/$branchName"
  if ($LASTEXITCODE -ne 0) { throw "K1_SYNC_FINAL_LOCAL_TRANSFER_REF_FAILED" }
  $liveRef = "refs/heads/$branchName"
  $liveBranch = @($observedLiveRefs | Where-Object { $_.Ref -ceq $liveRef })
  if ($liveBranch.Count -ne 1) { throw "K1_SYNC_FINAL_TRANSFER_REF_NOT_UNIQUE" }
  if ($localBranchHead -cne $liveBranch[0].Hash) {
    throw "K1_SYNC_FINAL_TRANSFER_REF_MISMATCH"
  }
}

$remoteK1 = git rev-parse refs/remotes/origin/codex/aurelia-konsolidierung
if ($LASTEXITCODE -ne 0) { throw "K1_SYNC_FINAL_REMOTE_K1_REF_FAILED" }
if ($localK1 -cne $remoteK1) { throw "K1_SYNC_FINAL_K1_TRACKING_MISMATCH" }

$aheadBehind = git rev-list --left-right --count refs/remotes/origin/codex/aurelia-konsolidierung...refs/heads/codex/aurelia-konsolidierung
if ($LASTEXITCODE -ne 0) { throw "K1_SYNC_FINAL_COUNTS_FAILED" }
if (($aheadBehind -replace "\s+", " ").Trim() -ne "0 0") {
  throw "K1_SYNC_FINAL_AHEAD_BEHIND_MISMATCH"
}

$worktreeRows = @(git worktree list --porcelain)
if ($LASTEXITCODE -ne 0) { throw "K1_SYNC_FINAL_WORKTREE_LIST_FAILED" }
$worktreePaths = @($worktreeRows | ForEach-Object {
  if ($_.StartsWith("worktree ")) { $_.Substring(9) }
})
if ($worktreePaths.Count -eq 0) { throw "K1_SYNC_FINAL_NO_WORKTREES" }

$expectedGovernanceUntracked = @(
  "docs/superpowers/plans/2026-08-24-aurelia-g0-01-toolchain-directives-and-quality-gates.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-02-register-and-schema-core.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-03-transition-ledger.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-04-reviews-evidence-gates-no-waiver.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-05-cryptographic-bootstrap.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-06-transparency-and-witness.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-07-recovery-write-path.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-08-tcb-lifecycle.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-09-external-llm-and-egress.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-10-mg1-collector-contract.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-11-remote-governance.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-12-genesis-initial-manifest.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-13-g0-acceptance.md",
  "docs/superpowers/plans/2026-08-24-aurelia-g0-implementation-master.md",
  "docs/superpowers/plans/2026-08-25-aurelia-g0-status-live.html"
) | Sort-Object

$governanceWorktreeCount = 0
foreach ($worktreePath in $worktreePaths) {
  $trackedState = @(git -C $worktreePath status --porcelain=v1 --untracked-files=no)
  if ($LASTEXITCODE -ne 0) { throw "K1_SYNC_FINAL_TRACKED_STATUS_FAILED" }
  if ($trackedState.Count -ne 0) { throw "K1_SYNC_FINAL_TRACKED_STATE_DIRTY" }

  $worktreeBranch = git -C $worktreePath branch --show-current
  if ($LASTEXITCODE -ne 0) { throw "K1_SYNC_FINAL_WORKTREE_BRANCH_FAILED" }
  $untrackedState = @(git -C $worktreePath ls-files --others --exclude-standard)
  if ($LASTEXITCODE -ne 0) { throw "K1_SYNC_FINAL_UNTRACKED_STATUS_FAILED" }

  if ($worktreeBranch -ceq "codex/aurelia-g0-governance") {
    $governanceWorktreeCount++
    $actualGovernanceUntracked = @($untrackedState | Sort-Object)
    $difference = @(Compare-Object `
      -ReferenceObject $expectedGovernanceUntracked `
      -DifferenceObject $actualGovernanceUntracked)
    if ($difference.Count -ne 0) {
      throw "K1_SYNC_FINAL_GOVERNANCE_ALLOWLIST_MISMATCH"
    }
  } elseif ($untrackedState.Count -ne 0) {
    throw "K1_SYNC_FINAL_UNEXPECTED_UNTRACKED_FILES"
  }
}
if ($governanceWorktreeCount -ne 1) {
  throw "K1_SYNC_FINAL_GOVERNANCE_WORKTREE_COUNT_MISMATCH"
}
```

## Fachlicher Resume-Punkt

Der fachliche Stand ist durch den Sync unverändert: Task 3 bleibt mit den zwei
offenen Spec-P1-Findings `K1-T3-P1-01` und `K1-T3-P1-02` sowie dem offenen
Qualitätsfinding `K1-T3-Q-01` fortzusetzen. Task 4 bleibt bis zum erneuten
Spec-PASS und anschließenden Qualitäts-PASS für Task 3 blockiert.

Verbindliche Detailquellen:

- [K1-Projektstatus](K1-STATUS.md)
- [K1-Kanonkonsolidierungsdesign](../superpowers/specs/2026-08-25-aurelia-k1-canon-consolidation-design.md)
- [K1-Kanonkonsolidierungsplan](../superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md)

## Read-only CLI-Einstieg

Der folgende Einstieg ist für einen frischen Clone bestimmt. Er checkt `main`
nicht aus und stoppt bei jeder Abweichung fail-closed. Die `origin`-Pushroute
dieses Clones wird lokal technisch gesperrt; weitergehende Read-only-Garantien
werden daraus nicht abgeleitet.

```powershell
$ErrorActionPreference = "Stop"
$repoUrl = "https://github.com/redshift-three67/aurelia.git"
$cloneDir = "aurelia-k1-readonly"

git clone --no-checkout $repoUrl $cloneDir
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_CLONE_FAILED" }

Set-Location -LiteralPath $cloneDir

git remote set-url --push origin disabled://aurelia-read-only
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_DISABLE_PUSH_FAILED" }
$pushUrl = git remote get-url --push origin
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_PUSH_URL_READ_FAILED" }
if ($pushUrl -cne "disabled://aurelia-read-only") {
  throw "K1_READONLY_PUSH_URL_MISMATCH"
}
$fetchUrl = git remote get-url origin
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_FETCH_URL_READ_FAILED" }
if ($fetchUrl -cne "https://github.com/redshift-three67/aurelia.git") {
  throw "K1_READONLY_FETCH_URL_MISMATCH"
}

git fetch --prune origin
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_FETCH_FAILED" }

$requiredRemoteRefs = @(
  "refs/remotes/origin/codex/aurelia-g0-governance",
  "refs/remotes/origin/codex/aurelia-kanon-implementation",
  "refs/remotes/origin/codex/aurelia-konsolidierung",
  "refs/remotes/origin/codex/aurelia-vorbereitung",
  "refs/remotes/origin/main"
)
foreach ($remoteRef in $requiredRemoteRefs) {
  git show-ref --verify $remoteRef
  if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_REQUIRED_REF_ABSENT" }
}

git switch --detach origin/codex/aurelia-konsolidierung
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_DETACH_FAILED" }

$branchName = git branch --show-current
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_BRANCH_READ_FAILED" }
if (-not [string]::IsNullOrEmpty($branchName)) {
  throw "K1_READONLY_EXPECTED_DETACHED_HEAD"
}

$head = git rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_HEAD_READ_FAILED" }
$remoteK1 = git rev-parse refs/remotes/origin/codex/aurelia-konsolidierung
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_REMOTE_HEAD_READ_FAILED" }
if ($head -ne $remoteK1) { throw "K1_READONLY_HEAD_MISMATCH" }

git merge-base --is-ancestor 8706186af01e10e4253e25abb31bf3577110dae4 HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_BASE_ANCESTRY_FAILED" }
git merge-base --is-ancestor 431695604f54a1fbea9e2d70d52ab27bc2ded16f HEAD
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_FIRST_SYNC_ANCESTRY_FAILED" }

$worktreeState = @(git status --porcelain=v1)
if ($LASTEXITCODE -ne 0) { throw "K1_READONLY_STATUS_FAILED" }
if ($worktreeState.Count -ne 0) { throw "K1_READONLY_WORKTREE_DIRTY" }
```

Die kanonische, um Ground Zero und weitere Produktquellen ergänzte
Lesereihenfolge steht im [Project-Control-Einstieg](README.md). Die folgende
Kernfolge spiegelt deren erste acht Einträge und definiert keine konkurrierende
Reihenfolge:

1. [`AGENTS.md`](../../AGENTS.md)
2. [`AGENTS.project.md`](../../AGENTS.project.md)
3. [Project-Control-Einstieg](README.md)
4. [diese Post-Sync-Evidenz](K1-SYNC-EVIDENCE-2026-08-26.md)
5. [K1-Projektstatus](K1-STATUS.md)
6. [`docs/STATUS.md`](../STATUS.md)
7. [K1-Kanonkonsolidierungsdesign](../superpowers/specs/2026-08-25-aurelia-k1-canon-consolidation-design.md)
8. [K1-Kanonkonsolidierungsplan](../superpowers/plans/2026-08-25-aurelia-k1-canon-consolidation.md)

Außer der ausdrücklich gesetzten lokalen `origin`-Pushroute verändert dieser
Einstieg keine versionierten Inhalte; er führt keine Installation, keine Tests
und keinen Push aus.
