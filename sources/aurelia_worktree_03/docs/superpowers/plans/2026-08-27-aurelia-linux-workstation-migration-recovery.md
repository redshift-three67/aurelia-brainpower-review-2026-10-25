# AURELIA Linux Workstation Migration and Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create and prove a complete encrypted recovery checkpoint for the AURELIA Windows development state, then publish only the approved consolidation branch by one private fast-forward push.

**Architecture:** Preserve committed history in an all-local-branches Git bundle, preserve the two K1 scanner modifications as a binary patch, and preserve the 15 G0 files as an explicit TAR overlay. Build the capsule directly on encrypted external medium A, reproduce it on encrypted external medium B, restore from A into an isolated encrypted test root on B, and permit the single GitHub push only after every restore and publication-exception gate passes.

**Tech Stack:** Git 2.55 or later, PowerShell 7, Node.js 22.22.0, npm 11.18.0, SHA-256, `tar`, two independently encrypted external destinations, private Git remote `origin`.

---

## Execution boundary

This plan implements the approved design:
`docs/superpowers/specs/2026-08-27-aurelia-linux-workstation-migration-recovery-design.md`.

The design is committed in `85017ba`; its formatting-only successor is
`aec827f`. The plan document itself must be committed as documentation before
capsule execution. Therefore, execution requires `aec827f` to be an ancestor
of the active `HEAD`, not equal to it.

The following remain forbidden throughout:

- any commit containing production code, either scanner file, or a G0
  untracked file;
- any push of `main`, another branch, tags, or multiple refs;
- force-push, history rewrite, merge, rebase, reset, stash, or branch deletion;
- any AURELIA server, SSH, IPMI, database, CUDA, USB, or production action;
- any capsule, restored object, patch, TAR member, or cold backup on an
  unencrypted internal path;
- any Windows erase, repartition, or reinstall authorization.

The full-graph publication gate is expected to remain formally red. Only the
explicitly authorized unchanged-record exception described below can permit
the one private push.

Tasks 2 through 9 execute in one uninterrupted, orchestrator-owned PowerShell
7 session so verified path and identity variables cannot be silently
reconstructed by another process. Subagents may perform bounded read-only
reviews, but the primary orchestrator executes every state-changing command.
If that shell terminates, discard no artifacts and restart verification at
Task 2 before resuming.

## Shortened execution path (operator decision, 2026-08-28)

The operator declared on 2026-08-28 that complete local backups of the project
directory **including `.git`** already exist. Tasks 2–7 and Task 10 (encrypted
capsule, mirrors, independent restore proof, cold backup) are therefore
**waived as redundant** for this run. Task 1 is complete (`2f86d6b`). This run
executes **Task 8 and Task 9 only**, under the original push discipline, with
these documented adaptations:

1. Medium-derived variables are resolved without encrypted external media:
   the pre-push CAS hook and the push receipt are written to a local directory
   **outside every Git worktree**, and their SHA-256 hashes are recorded in
   the local evidence checkpoint (`aurelia-tiefenanalyse-v6-2026-08-28/`)
   instead of a capsule manifest.
2. Task 8 Step 3 dirty-scope expectations reflect the authorized state of
   2026-08-28: exactly **5** working-tree entries (the two scanner files plus
   the three amended K1 overlap documents), scanner test hash `81607e33…`,
   scanner hash unchanged `32c0b5b4…`.
3. Task 8 Step 3 ignored-scope: the frozen values (`52`, `afc5834d…`) predate
   the 2026-08-28 analysis folders. Count and digest are recomputed fresh,
   recorded in the evidence checkpoint, and must remain **unchanged between
   the Task 8 measurement and the post-push re-check**.
4. All other Task 8/9 assertions apply unchanged: private identity proof,
   single-ref fetch and fast-forward check, in-memory full-graph comparison
   with `added_records=0` and `removed_records=0`, the isolated pre-push CAS
   hook, the one-ref push without `--force`/`--all`, the independent remote
   readback, and the post-push overlay checks.
5. Infrastructure note (operator clarification, 2026-08-28): the local Windows
   workstation is the development environment only; the Debian server lives at
   a provider and is reachable exclusively via RDP and WinSCP. No server-side
   action is part of this plan.

## Required operator inputs

Execution cannot begin until the operator supplies and confirms all four
values below. They are session inputs, never committed values:

| Environment variable | Required meaning |
|---|---|
| `AURELIA_MEDIA_A_ROOT` | Existing root directory on encrypted external medium A |
| `AURELIA_MEDIA_B_ROOT` | Existing root directory on a physically independent encrypted external medium B |
| `AURELIA_MEDIA_A_LABEL` | Non-secret human label for medium A |
| `AURELIA_MEDIA_B_LABEL` | Non-secret human label for medium B |

Both filesystem roots must be absolute, distinct, outside every Git worktree,
writeable, and confirmed encrypted and unlocked. The executor must request the
encryption mechanism and verify it with a read-only platform command. For
BitLocker, `Get-BitLockerVolume` must report `ProtectionStatus On`. For another
mechanism, the operator must provide its native read-only status command; an
unverifiable verbal assumption is not sufficient.

## File and artifact map

### Repository documentation

- Create:
  `docs/superpowers/plans/2026-08-27-aurelia-linux-workstation-migration-recovery.md`
  — this executable plan; the only file in its documentation checkpoint.
- Read:
  `docs/superpowers/specs/2026-08-27-aurelia-linux-workstation-migration-recovery-design.md`
  — controlling design and stop conditions.
- Read only:
  `scripts/check-push-graph.mjs` and
  `scripts/check-push-graph.test.mjs` — evidence-bearing dirty overlay; never
  stage or commit during migration.

### Encrypted capsule on medium A and mirrored on medium B

```text
2026-08-27-aurelia-linux-workstation/
  README.md
  SHA256SUMS.txt
  git/
    aurelia-all-refs.bundle
  patches/
    k1-consolidation-unstaged.patch
  untracked/
    g0-untracked-plans.tar
  inventory/
    refs.txt
    worktrees.txt
    statuses.txt
    toolchain.txt
    git-config-sanitized.txt
    g0-untracked-files.txt
    sensitive-local-files-redacted.txt
```

The independent restore test root is a sibling of the capsule on medium B,
never a child of the capsule. A post-push receipt, if written, is also a sibling
on encrypted medium A; it is not added to the already verified capsule.

## Fixed identities and expected scopes

```text
approved_design_ancestor=aec827f829a2a716201cf21ac2574defb3e24c9a
authorized_remote_base=029bdcef62ccff35c0e964588e32a9727ea42470
active_branch=codex/aurelia-konsolidierung
scanner_sha256=32c0b5b4ec3fdf5083bc399c5525e11281d7f6301e86e5670840cca9bca1abef
scanner_test_sha256=81607e3362addb7ea160bf423934b1e043e42242a3917790ce23f361d76cbd63
g0_untracked_count=15
ignored_sensitive_count=52
ignored_sensitive_list_sha256=afc5834d0b84f3153e86dec429b55aae0aac55b944de26ab4324dd3b942d2f36
```

Amendment 2026-08-28: `scanner_test_sha256` wurde von
`ce9e3a6d88e01a5d935212d848141d29f82aa282848f0d749d1427bd9b4a44b9` auf den
aktuellen Stand `81607e33…` aktualisiert. Grund: Die durch die
Spec-Review-Korrekturschleife am 28.08. freigegebenen Testergänzungen
(gequotet-`=`-Abdeckung, escaped-Quote-/1-MiB-Fixtures; E3 §6) haben die
Testdatei geändert; der Scanner selbst ist unverändert. Die übrigen
Identitäten (`g0_untracked_count`, `ignored_sensitive_count`,
`ignored_sensitive_list_sha256`) sind Laufzeitverifikationen gemäß Task 2/3
und werden dort frisch geprüft; Weichen sie ab, gilt der Plan-Stop, keine
Anpassung der Werte im Lauf.

The final local `HEAD` is deliberately read at execution time after the plan
checkpoint commit. It must descend from the approved design ancestor and the
authorized remote base.

## Shared in-memory verification function

Every fresh PowerShell 7 execution session used for Tasks 5 through 7 or Task
10 must define these exact manifest functions before running the task. The
verifier creates no file, trusts no path from the manifest, and proves
one-to-one coverage:

```powershell
function Assert-AureliaCapsuleManifest {
  param([Parameter(Mandatory)][string]$Root)

  $resolvedRoot = (Get-Item -LiteralPath $Root).FullName
  $rootPrefix = $resolvedRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) +
    [IO.Path]::DirectorySeparatorChar
  $manifestPath = Join-Path $resolvedRoot "SHA256SUMS.txt"
  if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "MIGRATION_MANIFEST_MISSING"
  }

  $seen = [Collections.Generic.HashSet[string]]::new(
    [StringComparer]::Ordinal
  )
  foreach ($line in @(Get-Content -LiteralPath $manifestPath)) {
    if ($line -notmatch '^(?<Digest>[0-9a-f]{64})  (?<Relative>[^\r\n]+)$') {
      throw "MIGRATION_MANIFEST_LINE_INVALID"
    }
    $relative = $Matches.Relative.Replace("\", "/")
    $segments = @($relative -split '/')
    if ([IO.Path]::IsPathRooted($relative) -or
        $segments.Count -eq 0 -or
        @($segments | Where-Object { $_ -eq "" -or $_ -eq "." -or $_ -eq ".." }).Count -ne 0 -or
        $relative -eq "SHA256SUMS.txt" -or
        -not $seen.Add($relative)) {
      throw "MIGRATION_MANIFEST_PATH_INVALID"
    }
    $candidate = [IO.Path]::GetFullPath((Join-Path $resolvedRoot $relative))
    if (-not $candidate.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase) -or
        -not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
      throw "MIGRATION_MANIFEST_PATH_ESCAPE_OR_MISSING"
    }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $candidate).Hash.ToLowerInvariant()
    if ($actual -ne $Matches.Digest) { throw "MIGRATION_MANIFEST_HASH_MISMATCH" }
  }

  $actualFiles = @(Get-ChildItem -LiteralPath $resolvedRoot -File -Recurse |
    ForEach-Object {
      [IO.Path]::GetRelativePath($resolvedRoot, $_.FullName).Replace("\", "/")
    } | Where-Object { $_ -ne "SHA256SUMS.txt" } | Sort-Object)
  $manifestFiles = @($seen | Sort-Object)
  if (@(Compare-Object $manifestFiles $actualFiles).Count -ne 0) {
    throw "MIGRATION_MANIFEST_COVERAGE_MISMATCH"
  }
  "MANIFEST_PASS files=$($manifestFiles.Count)"
}

function New-AureliaSha256Manifest {
  param([Parameter(Mandatory)][string]$Root)

  $resolvedRoot = (Get-Item -LiteralPath $Root).FullName
  $manifest = Join-Path $resolvedRoot "SHA256SUMS.txt"
  if (Test-Path -LiteralPath $manifest) { throw "MIGRATION_MANIFEST_ALREADY_EXISTS" }
  $manifestLines = Get-ChildItem -LiteralPath $resolvedRoot -File -Recurse |
    ForEach-Object {
      $relative = [IO.Path]::GetRelativePath($resolvedRoot, $_.FullName).Replace("\", "/")
      $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
      [pscustomobject]@{ Relative = $relative; Line = "$hash  $relative" }
    } | Sort-Object Relative | Select-Object -ExpandProperty Line
  $manifestLines | Set-Content -Encoding utf8NoBOM -LiteralPath $manifest
}
```

### Task 1: Commit only the approved execution plan

**Files:**
- Create:
  `docs/superpowers/plans/2026-08-27-aurelia-linux-workstation-migration-recovery.md`
- Preserve unstaged: `scripts/check-push-graph.mjs`
- Preserve unstaged: `scripts/check-push-graph.test.mjs`

- [ ] **Step 1: Verify the pre-commit scope**

Run from the consolidation worktree:

```powershell
$ErrorActionPreference = "Stop"
$plan = "docs/superpowers/plans/2026-08-27-aurelia-linux-workstation-migration-recovery.md"
$expectedWorking = @(
  $plan,
  "scripts/check-push-graph.mjs",
  "scripts/check-push-graph.test.mjs",
  "docs/superpowers/plans/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction.md",
  "docs/superpowers/plans/2026-08-26-aurelia-k1-task3-string-type-bypass.md",
  "docs/superpowers/specs/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction-design.md"
) | Sort-Object
$actualWorking = @(git status --porcelain=v1 | ForEach-Object {
  $_.Substring(3).Replace("\", "/")
}) | Sort-Object
if (@(Compare-Object $expectedWorking $actualWorking).Count -ne 0) {
  throw "MIGRATION_PLAN_WORKTREE_SCOPE_MISMATCH"
}
if (git diff --cached --name-only) {
  throw "MIGRATION_PLAN_INDEX_NOT_EMPTY"
}
git merge-base --is-ancestor aec827f829a2a716201cf21ac2574defb3e24c9a HEAD
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_DESIGN_ANCESTRY_FAILED" }
```

Expected: exactly the plan plus the two scanner files are modified or
untracked; the index is empty; design ancestry passes.

- [ ] **Step 2: Validate the plan as text**

```powershell
git diff --check -- $plan
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_PLAN_DIFF_INVALID" }

$unfinishedPattern = @("T", "BD", "|T", "ODO", "|PLACE", "HOLDER") -join ""
$forbidden = @(rg -n $unfinishedPattern $plan)
if ($LASTEXITCODE -eq 0 -or $forbidden.Count -ne 0) {
  throw "MIGRATION_PLAN_UNFINISHED_MARKER_FOUND"
}
if ($LASTEXITCODE -ne 1) { throw "MIGRATION_PLAN_SEARCH_FAILED" }

node --input-type=module -e "import {readFile} from 'node:fs/promises'; import {classifyBlob} from './scripts/check-push-graph.mjs'; const p=process.argv[1]; const findings=classifyBlob(p,await readFile(p)); console.log(JSON.stringify(findings)); process.exitCode=findings.length===0?0:1" $plan
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_PLAN_CLASSIFICATION_FAILED" }
```

Expected: no formatting errors, no unfinished markers, and `[]` from the
correct `classifyBlob(repositoryPath, bytes)` call signature.

- [ ] **Step 3: Stage and commit only the plan after explicit content approval**

```powershell
git add -- $plan
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_PLAN_STAGE_FAILED" }
$staged = @(git diff --cached --name-only)
if ($staged.Count -ne 1 -or $staged[0] -ne $plan) {
  throw "MIGRATION_PLAN_STAGED_SCOPE_MISMATCH"
}
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_PLAN_INDEX_INVALID" }
$parentBeforePlanCommit = (git rev-parse HEAD).Trim()
git commit -m "docs: plan Linux migration recovery checkpoint"
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_PLAN_COMMIT_FAILED" }
```

- [ ] **Step 4: Prove post-commit cleanliness boundaries**

```powershell
if (git diff --cached --name-only) { throw "MIGRATION_POSTCOMMIT_INDEX_NOT_EMPTY" }
$committedParent = (git rev-parse HEAD^).Trim()
if ($committedParent -ne $parentBeforePlanCommit) {
  throw "MIGRATION_PLAN_PARENT_MISMATCH"
}
$committedPaths = @(git diff-tree --no-commit-id --name-only -r HEAD)
if ($committedPaths.Count -ne 1 -or $committedPaths[0] -ne $plan) {
  throw "MIGRATION_PLAN_COMMIT_SCOPE_MISMATCH"
}
$remaining = @(git status --porcelain=v1)
if ($remaining.Count -ne 5) { throw "MIGRATION_POSTCOMMIT_DIRTY_COUNT_MISMATCH" }
if (@($remaining | Where-Object { $_ -notmatch '^ M (scripts/check-push-graph(?:\.test)?\.mjs|docs/superpowers/plans/2026-08-26-aurelia-k1-task3-(?:overlap-enumeration-correction|string-type-bypass)\.md|docs/superpowers/specs/2026-08-26-aurelia-k1-task3-overlap-enumeration-correction-design\.md)$' }).Count -ne 0) {
  throw "MIGRATION_POSTCOMMIT_DIRTY_SCOPE_MISMATCH"
}
$postCommitHashes = @{
  "scripts/check-push-graph.mjs" = "32c0b5b4ec3fdf5083bc399c5525e11281d7f6301e86e5670840cca9bca1abef"
  "scripts/check-push-graph.test.mjs" = "81607e3362addb7ea160bf423934b1e043e42242a3917790ce23f361d76cbd63"
}
foreach ($entry in $postCommitHashes.GetEnumerator()) {
  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Key).Hash.ToLowerInvariant()
  if ($actual -ne $entry.Value) { throw "MIGRATION_PLAN_POSTCOMMIT_SCANNER_HASH_MISMATCH" }
}
```

Expected: the commit contains only the plan and exactly two scanner files
remain unstaged.

Amendment 2026-08-28: Steps 1 und 4 erwarten zusätzlich die drei durch die
Spec-Review-Korrekturschleife am 28.08. geänderten Overlap-Dokumente
(2 Pläne, 1 Design) im Arbeitsbaum, und der Post-Commit-Hash der
Testdatei wurde auf `81607e33…` aktualisiert (E3 §6). Der Commit-Scope
selbst bleibt unverändert: ausschließlich dieses Plandokument.

### Task 2: Lock source state and verify both encrypted destinations

**Files:**
- Read: all worktree metadata and Git refs
- Create only on encrypted media: capsule and restore roots

- [ ] **Step 1: Resolve and validate operator inputs without logging secrets**

```powershell
$ErrorActionPreference = "Stop"
$requiredNames = @(
  "AURELIA_MEDIA_A_ROOT",
  "AURELIA_MEDIA_B_ROOT",
  "AURELIA_MEDIA_A_LABEL",
  "AURELIA_MEDIA_B_LABEL"
)
foreach ($name in $requiredNames) {
  if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name))) {
    throw "MIGRATION_REQUIRED_INPUT_MISSING:$name"
  }
}
$mediaA = (Get-Item -LiteralPath $env:AURELIA_MEDIA_A_ROOT).FullName
$mediaB = (Get-Item -LiteralPath $env:AURELIA_MEDIA_B_ROOT).FullName
if (-not [IO.Path]::IsPathFullyQualified($mediaA) -or
    -not [IO.Path]::IsPathFullyQualified($mediaB) -or
    $mediaA -eq $mediaB) {
  throw "MIGRATION_MEDIA_ROOT_INVALID"
}
$gitShapeVariables = @(
  "GIT_ALTERNATE_OBJECT_DIRECTORIES",
  "GIT_OBJECT_DIRECTORY",
  "GIT_DIR",
  "GIT_COMMON_DIR",
  "GIT_WORK_TREE",
  "GIT_INDEX_FILE",
  "GIT_NAMESPACE",
  "GIT_CEILING_DIRECTORIES"
)
foreach ($name in $gitShapeVariables) {
  if (-not [string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable($name))) {
    throw "MIGRATION_GIT_SHAPING_ENVIRONMENT_PRESENT:$name"
  }
}
$gitConfigEnvironment = @(Get-ChildItem Env: | Where-Object {
  $_.Name -like "GIT_CONFIG_*"
})
$configCountValue = [Environment]::GetEnvironmentVariable("GIT_CONFIG_COUNT")
if ($configCountValue -notmatch '^\d+$') {
  throw "MIGRATION_GIT_CONFIG_ENVIRONMENT_SHAPE_INVALID"
}
$configCount = [int]$configCountValue
$expectedConfigEnvironmentNames = @("GIT_CONFIG_COUNT")
for ($index = 0; $index -lt $configCount; $index += 1) {
  $expectedConfigEnvironmentNames += @("GIT_CONFIG_KEY_$index", "GIT_CONFIG_VALUE_$index")
  if ([Environment]::GetEnvironmentVariable("GIT_CONFIG_KEY_$index") -ne "safe.directory") {
    throw "MIGRATION_GIT_CONFIG_ENVIRONMENT_KEY_FORBIDDEN"
  }
}
if (@(Compare-Object ($expectedConfigEnvironmentNames | Sort-Object) ($gitConfigEnvironment.Name | Sort-Object)).Count -ne 0) {
  throw "MIGRATION_GIT_CONFIG_ENVIRONMENT_SET_INVALID"
}
$worktreeRoots = @(git worktree list --porcelain | Where-Object {
  $_.StartsWith("worktree ")
} | ForEach-Object {
  [IO.Path]::GetFullPath($_.Substring(9)).TrimEnd([IO.Path]::DirectorySeparatorChar)
})
$commonGitRoot = [IO.Path]::GetFullPath((git rev-parse --path-format=absolute --git-common-dir).Trim()).TrimEnd([IO.Path]::DirectorySeparatorChar)
foreach ($media in @($mediaA, $mediaB)) {
  $mediaNormalized = [IO.Path]::GetFullPath($media).TrimEnd([IO.Path]::DirectorySeparatorChar)
  $mediaPrefix = $mediaNormalized + [IO.Path]::DirectorySeparatorChar
  foreach ($worktreeRoot in $worktreeRoots) {
    $worktreePrefix = $worktreeRoot + [IO.Path]::DirectorySeparatorChar
    if ($mediaNormalized -eq $worktreeRoot -or
        $mediaNormalized.StartsWith($worktreePrefix, [StringComparison]::OrdinalIgnoreCase) -or
        $worktreeRoot.StartsWith($mediaPrefix, [StringComparison]::OrdinalIgnoreCase)) {
      throw "MIGRATION_MEDIA_WORKTREE_OVERLAP"
    }
  }
  $commonPrefix = $commonGitRoot + [IO.Path]::DirectorySeparatorChar
  if ($mediaNormalized -eq $commonGitRoot -or
      $mediaNormalized.StartsWith($commonPrefix, [StringComparison]::OrdinalIgnoreCase) -or
      $commonGitRoot.StartsWith($mediaPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "MIGRATION_MEDIA_GITDIR_OVERLAP"
  }
}

function Assert-NoReparseAncestor {
  param([Parameter(Mandatory)][string]$Path)
  $item = Get-Item -LiteralPath $Path
  while ($null -ne $item) {
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
      throw "MIGRATION_MEDIA_REPARSE_POINT_FOUND"
    }
    $item = $item.Parent
  }
}
Assert-NoReparseAncestor -Path $mediaA
Assert-NoReparseAncestor -Path $mediaB
```

- [ ] **Step 2: Verify encryption and physical independence**

Strategy A execution requires two BitLocker-protected external Windows volumes.
Another encryption mechanism requires a separately reviewed documentation
addendum before execution; it is not substituted ad hoc.

```powershell
$volumeA = Get-BitLockerVolume -MountPoint ([IO.Path]::GetPathRoot($mediaA))
$volumeB = Get-BitLockerVolume -MountPoint ([IO.Path]::GetPathRoot($mediaB))
foreach ($volume in @($volumeA, $volumeB)) {
  if ($volume.ProtectionStatus -ne "On" -or
      $volume.LockStatus -ne "Unlocked" -or
      $volume.VolumeStatus -ne "FullyEncrypted") {
    throw "MIGRATION_MEDIA_ENCRYPTION_NOT_READY"
  }
}
$driveA = [IO.Path]::GetPathRoot($mediaA).Substring(0, 1)
$driveB = [IO.Path]::GetPathRoot($mediaB).Substring(0, 1)
$diskA = Get-Partition -DriveLetter $driveA | Get-Disk
$diskB = Get-Partition -DriveLetter $driveB | Get-Disk
foreach ($disk in @($diskA, $diskB)) {
  if ($disk.IsSystem -or $disk.IsBoot -or
      $disk.BusType -ne "USB" -or
      [string]::IsNullOrWhiteSpace($disk.UniqueId)) {
    throw "MIGRATION_MEDIA_NOT_VERIFIED_EXTERNAL_USB"
  }
}
if ($diskA.UniqueId -eq $diskB.UniqueId -or $diskA.Number -eq $diskB.Number) {
  throw "MIGRATION_MEDIA_NOT_PHYSICALLY_INDEPENDENT"
}
if ([IO.Path]::GetPathRoot($mediaA) -eq [IO.Path]::GetPathRoot($mediaB)) {
  throw "MIGRATION_MEDIA_VOLUME_ROOT_NOT_DISTINCT"
}
```

- [ ] **Step 3: Define isolated artifact locations and reject collisions**

```powershell
$capsuleName = "2026-08-27-aurelia-linux-workstation"
$capsuleA = Join-Path $mediaA $capsuleName
$capsuleB = Join-Path $mediaB $capsuleName
$restoreRoot = Join-Path $mediaB "2026-08-27-aurelia-restore-proof"
foreach ($path in @($capsuleA, $capsuleB, $restoreRoot)) {
  if (Test-Path -LiteralPath $path) { throw "MIGRATION_TARGET_ALREADY_EXISTS" }
}
```

Expected: three absent paths across two verified encrypted physical media.

### Task 3: Re-prove the exact local source state

**Files:**
- Read: consolidation, G0, preparation, and canon worktrees
- Write only sanitized inventory files under `$capsuleA`

- [ ] **Step 1: Verify branch, ancestry, index, and exact scanner hashes**

```powershell
$expectedBranch = "codex/aurelia-konsolidierung"
$remoteBase = "029bdcef62ccff35c0e964588e32a9727ea42470"
$designAncestor = "aec827f829a2a716201cf21ac2574defb3e24c9a"
if ((git branch --show-current).Trim() -ne $expectedBranch) {
  throw "MIGRATION_BRANCH_MISMATCH"
}
foreach ($ancestor in @($remoteBase, $designAncestor)) {
  git merge-base --is-ancestor $ancestor HEAD
  if ($LASTEXITCODE -ne 0) { throw "MIGRATION_REQUIRED_ANCESTOR_MISSING" }
}
if (git diff --cached --name-only) { throw "MIGRATION_INDEX_NOT_EMPTY" }
$expectedHashes = @{
  "scripts/check-push-graph.mjs" = "32c0b5b4ec3fdf5083bc399c5525e11281d7f6301e86e5670840cca9bca1abef"
  "scripts/check-push-graph.test.mjs" = "ce9e3a6d88e01a5d935212d848141d29f82aa282848f0d749d1427bd9b4a44b9"
}
foreach ($entry in $expectedHashes.GetEnumerator()) {
  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Key).Hash.ToLowerInvariant()
  if ($actual -ne $entry.Value) { throw "MIGRATION_SCANNER_HASH_MISMATCH" }
}
$dirty = @(git status --porcelain=v1)
if ($dirty.Count -ne 2 -or
    @($dirty | Where-Object { $_ -notmatch '^ M scripts/check-push-graph(?:\.test)?\.mjs$' }).Count -ne 0) {
  throw "MIGRATION_CONSOLIDATION_DIRTY_SCOPE_MISMATCH"
}
```

- [ ] **Step 2: Resolve worktrees internally and verify their states**

Use `git worktree list --porcelain` only in memory. Map each required branch to
its absolute worktree path, but never write those absolute paths into an
inventory.

```powershell
$porcelain = @(git worktree list --porcelain)
$worktreeRecords = @($porcelain | Where-Object { $_.StartsWith("worktree ") })
if ($worktreeRecords.Count -ne 4 -or
    @($porcelain | Where-Object { $_ -eq "detached" -or $_ -eq "bare" -or $_.StartsWith("prunable ") }).Count -ne 0) {
  throw "MIGRATION_WORKTREE_RECORD_SET_INVALID"
}
$worktrees = @{}
$currentPath = $null
foreach ($line in $porcelain) {
  if ($line.StartsWith("worktree ")) { $currentPath = $line.Substring(9) }
  elseif ($line.StartsWith("branch refs/heads/")) {
    $worktrees[$line.Substring(18)] = $currentPath
  }
}
$requiredBranches = @(
  "codex/aurelia-vorbereitung",
  "codex/aurelia-g0-governance",
  "codex/aurelia-kanon-implementation",
  "codex/aurelia-konsolidierung"
)
$expectedLocalRefs = @(
  "refs/heads/codex/aurelia-g0-governance",
  "refs/heads/codex/aurelia-kanon-implementation",
  "refs/heads/codex/aurelia-konsolidierung",
  "refs/heads/codex/aurelia-vorbereitung",
  "refs/heads/main"
) | Sort-Object
$actualLocalRefs = @(git for-each-ref --sort=refname --format="%(refname)" refs/heads)
if (@(Compare-Object $expectedLocalRefs $actualLocalRefs -CaseSensitive).Count -ne 0) {
  throw "MIGRATION_LOCAL_BRANCH_SET_MISMATCH"
}
if ($worktrees.Count -ne 4) { throw "MIGRATION_WORKTREE_COUNT_MISMATCH" }
foreach ($branch in $requiredBranches) {
  if (-not $worktrees.ContainsKey($branch)) { throw "MIGRATION_WORKTREE_MISSING" }
}
$g0Root = $worktrees["codex/aurelia-g0-governance"]
$prepRoot = $worktrees["codex/aurelia-vorbereitung"]
$canonRoot = $worktrees["codex/aurelia-kanon-implementation"]
if (@(git -C $prepRoot status --porcelain=v1).Count -ne 0) {
  throw "MIGRATION_PREPARATION_NOT_CLEAN"
}
if (@(git -C $canonRoot status --porcelain=v1).Count -ne 0) {
  throw "MIGRATION_CANON_NOT_CLEAN"
}
$g0Status = @(git -C $g0Root status --porcelain=v1)
if ($g0Status.Count -ne 15 -or @($g0Status | Where-Object { $_ -notmatch '^\?\? docs/superpowers/plans/' }).Count -ne 0) {
  throw "MIGRATION_G0_SCOPE_MISMATCH"
}
$allNonHeadRefs = @(git for-each-ref --format="%(refname)" | Where-Object {
  $_ -notlike 'refs/heads/*'
})
$unexpectedLocalRefs = @($allNonHeadRefs | Where-Object {
  $_ -notlike 'refs/remotes/origin/*' -and
  $_ -notlike 'refs/codex/turn-diffs/*'
})
if ($unexpectedLocalRefs.Count -ne 0) { throw "MIGRATION_UNEXPECTED_LOCAL_REF" }
git rev-parse --verify --quiet refs/stash | Out-Null
if ($LASTEXITCODE -eq 0) { throw "MIGRATION_STASH_PRESENT" }
if ($LASTEXITCODE -ne 1) { throw "MIGRATION_STASH_CHECK_FAILED" }
$repositoryRoot = Split-Path -Parent $commonGitRoot
$ignoredSensitivePaths = @(git -C $repositoryRoot ls-files --others --ignored --exclude-standard |
  Where-Object { $_ -notlike '.worktrees/*' } | Sort-Object -Unique)
$ignoredPayload = [Text.Encoding]::UTF8.GetBytes(($ignoredSensitivePaths -join "`n") + "`n")
$ignoredSensitiveDigest = [Convert]::ToHexString(
  [Security.Cryptography.SHA256]::HashData($ignoredPayload)
).ToLowerInvariant()
if ($ignoredSensitivePaths.Count -ne 52 -or
    $ignoredSensitiveDigest -ne "afc5834d0b84f3153e86dec429b55aae0aac55b944de26ab4324dd3b942d2f36") {
  throw "MIGRATION_IGNORED_SENSITIVE_SCOPE_MISMATCH"
}
```

`refs/remotes/origin/*` are reproducible remote-tracking metadata.
`refs/codex/turn-diffs/*` are transient Codex UI evidence and remain excluded
from the canonical branch bundle; the full encrypted repository cold archive
preserves them for forensic rollback. Every other non-head ref and every stash
blocks capsule creation.

- [ ] **Step 3: Verify repository object integrity and unsupported-feature absence**

```powershell
git fsck --full --no-reflogs
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_GIT_FSCK_FAILED" }
if (Test-Path -LiteralPath ".gitmodules") { throw "MIGRATION_UNEXPECTED_SUBMODULE_CONFIG" }
if (Test-Path -LiteralPath ".gitattributes") {
  $trackedPaths = @(git ls-files)
  $lfsAttributes = @(git check-attr filter -- $trackedPaths | Where-Object {
    $_ -match ': filter: lfs$'
  })
  if ($lfsAttributes.Count -ne 0) { throw "MIGRATION_UNEXPECTED_LFS_OBJECT" }
}
if (@(git tag --list).Count -ne 0) { throw "MIGRATION_UNEXPECTED_TAG" }
```

Dangling objects may be reported by `git fsck`; missing or corrupt objects are
not acceptable.

### Task 4: Build the capsule directly on encrypted medium A

**Files:**
- Create only beneath `$capsuleA` using the exact declared layout

- [ ] **Step 1: Create the declared directories**

```powershell
$directories = @(
  $capsuleA,
  (Join-Path $capsuleA "git"),
  (Join-Path $capsuleA "patches"),
  (Join-Path $capsuleA "untracked"),
  (Join-Path $capsuleA "inventory")
)
foreach ($directory in $directories) {
  New-Item -ItemType Directory -Path $directory | Out-Null
}
```

- [ ] **Step 2: Create the all-local-branches Git bundle**

```powershell
$bundle = Join-Path $capsuleA "git/aurelia-all-refs.bundle"
git bundle create $bundle --branches
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $bundle)) {
  throw "MIGRATION_BUNDLE_CREATE_FAILED"
}
```

Expected: one bundle containing every `refs/heads/*` ref and no worktree
overlay.

- [ ] **Step 3: Create the exact two-file binary patch without staging**

```powershell
$patchPath = Join-Path $capsuleA "patches/k1-consolidation-unstaged.patch"
git diff --binary --output=$patchPath HEAD -- `
  scripts/check-push-graph.mjs `
  scripts/check-push-graph.test.mjs
if ($LASTEXITCODE -ne 0 -or (Get-Item -LiteralPath $patchPath).Length -eq 0) {
  throw "MIGRATION_PATCH_CREATE_FAILED"
}
if (git diff --cached --name-only) { throw "MIGRATION_PATCH_STAGED_FILES" }
```

- [ ] **Step 4: Create the sorted G0 file list, hash inventory, and TAR**

```powershell
$g0Paths = @(git -C $g0Root ls-files --others --exclude-standard -- docs/superpowers/plans) |
  Sort-Object -Unique
if ($g0Paths.Count -ne 15) { throw "MIGRATION_G0_FILE_COUNT_MISMATCH" }
$g0Inventory = Join-Path $capsuleA "inventory/g0-untracked-files.txt"
$g0Lines = foreach ($relative in $g0Paths) {
  $full = Join-Path $g0Root $relative
  $item = Get-Item -LiteralPath $full
  $g0Prefix = [IO.Path]::GetFullPath($g0Root).TrimEnd([IO.Path]::DirectorySeparatorChar) +
    [IO.Path]::DirectorySeparatorChar
  $resolvedFile = [IO.Path]::GetFullPath($item.FullName)
  if ($item.PSIsContainer -or
      ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      -not [string]::IsNullOrEmpty($item.LinkType) -or
      -not $resolvedFile.StartsWith($g0Prefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "MIGRATION_G0_NONREGULAR_OR_ESCAPING_FILE"
  }
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $full).Hash.ToLowerInvariant()
  "$hash  $($relative.Replace('\','/'))"
}
$g0Lines | Set-Content -Encoding utf8NoBOM -LiteralPath $g0Inventory
$tarList = Join-Path $capsuleA "inventory/.g0-tar-input.txt"
$g0Paths | ForEach-Object { $_.Replace('\','/') } |
  Set-Content -Encoding utf8NoBOM -LiteralPath $tarList
$g0Tar = Join-Path $capsuleA "untracked/g0-untracked-plans.tar"
tar -cf $g0Tar -C $g0Root -T $tarList
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $g0Tar)) {
  throw "MIGRATION_G0_TAR_CREATE_FAILED"
}
$tarDetails = @(tar -tvf $g0Tar)
if ($LASTEXITCODE -ne 0 -or $tarDetails.Count -ne 15 -or
    @($tarDetails | Where-Object { $_ -notmatch '^-[r-][w-]-[r-][w-]-[r-][w-]-\s' }).Count -ne 0) {
  throw "MIGRATION_G0_TAR_TYPE_OR_MODE_INVALID"
}
Remove-Item -LiteralPath $tarList
```

The temporary TAR input list exists only on encrypted medium A and is removed
before layout validation.

- [ ] **Step 5: Write only sanitized inventories**

`refs.txt` contains sorted local branch ref names and commit IDs.
`worktrees.txt` contains logical branch names, commit IDs, and state labels but
no physical paths. `statuses.txt` contains counts and repository-relative
paths only. `toolchain.txt` contains version strings. The Git configuration
inventory is restricted to this allow-list:

```text
core.autocrlf
core.filemode
core.symlinks
init.defaultbranch
pull.ff
fetch.prune
commit.gpgsign
```

Generate the ref and toolchain inventories:

```powershell
$inventory = Join-Path $capsuleA "inventory"
git for-each-ref --sort=refname --format="%(refname) %(objectname)" refs/heads |
  Set-Content -Encoding utf8NoBOM -LiteralPath (Join-Path $inventory "refs.txt")
@(
  "git=$((git --version).Trim())"
  "node=$((node --version).Trim())"
  "npm=$((npm --version).Trim())"
  "powershell=$($PSVersionTable.PSVersion)"
  "tar=$((tar --version | Select-Object -First 1).Trim())"
) | Set-Content -Encoding utf8NoBOM -LiteralPath (Join-Path $inventory "toolchain.txt")
$safeKeys = @(
  "core.autocrlf", "core.filemode", "core.symlinks",
  "init.defaultbranch", "pull.ff", "fetch.prune", "commit.gpgsign"
)
$safeConfig = foreach ($key in $safeKeys) {
  $value = git config --get $key
  if ($LASTEXITCODE -eq 0) { "$key=$value" }
}
$safeConfig | Set-Content -Encoding utf8NoBOM -LiteralPath (Join-Path $inventory "git-config-sanitized.txt")
$stateByBranch = @{
  "codex/aurelia-vorbereitung" = "clean"
  "codex/aurelia-g0-governance" = "15-untracked"
  "codex/aurelia-kanon-implementation" = "clean"
  "codex/aurelia-konsolidierung" = "2-modified"
}
$worktreeLines = foreach ($branch in ($requiredBranches | Sort-Object)) {
  $head = (git -C $worktrees[$branch] rev-parse HEAD).Trim()
  "branch=$branch;head=$head;state=$($stateByBranch[$branch])"
}
$worktreeLines | Set-Content -Encoding utf8NoBOM -LiteralPath (Join-Path $inventory "worktrees.txt")
@(
  $g0Status
  " M scripts/check-push-graph.mjs"
  " M scripts/check-push-graph.test.mjs"
) | Sort-Object | Set-Content -Encoding utf8NoBOM -LiteralPath (Join-Path $inventory "statuses.txt")
@(
  "ignored_sensitive_files_count=52"
  "ignored_sensitive_list_sha256=$ignoredSensitiveDigest"
  "storage_policy=separate-encrypted-offline-cold-copy"
  "included_in_git=false"
  "included_in_recovery_capsule=false"
  "paths_disclosed=false"
) | Set-Content -Encoding utf8NoBOM -LiteralPath (Join-Path $inventory "sensitive-local-files-redacted.txt")
```

- [ ] **Step 6: Write the truthful post-plan README**

```powershell
$createdUtc = [DateTimeOffset]::UtcNow
$berlinZone = [TimeZoneInfo]::FindSystemTimeZoneById("W. Europe Standard Time")
$createdBerlin = [TimeZoneInfo]::ConvertTime($createdUtc, $berlinZone)
$capsuleHead = (git rev-parse HEAD).Trim()
@(
  "# AURELIA encrypted recovery capsule"
  ""
  "created_utc=$($createdUtc.ToString('o'))"
  "created_europe_berlin=$($createdBerlin.ToString('o'))"
  "source_medium_label=$env:AURELIA_MEDIA_A_LABEL"
  "committed_head=$capsuleHead"
  "approved_design_ancestor=aec827f829a2a716201cf21ac2574defb3e24c9a"
  "authorized_remote_base=029bdcef62ccff35c0e964588e32a9727ea42470"
  "scanner_sha256=32c0b5b4ec3fdf5083bc399c5525e11281d7f6301e86e5670840cca9bca1abef"
  "scanner_test_sha256=ce9e3a6d88e01a5d935212d848141d29f82aa282848f0d749d1427bd9b4a44b9"
  "g0_untracked_count=15"
  "ignored_sensitive_count=52"
  "ignored_sensitive_list_sha256=$ignoredSensitiveDigest"
  "restore_branches=codex/aurelia-vorbereitung,codex/aurelia-g0-governance,codex/aurelia-kanon-implementation,codex/aurelia-konsolidierung"
  "restore_order=checksum,bundle-verify,fetch,fsck,worktrees,patch-check,patch-apply,tar-extract,hash-status-compare"
  "excluded=ignored-analyses,codex-user-state,ssh-material,recovery-material"
  "excluded_storage=separate-encrypted-offline-cold-copy"
  "disk_erasure_authorized=false"
) | Set-Content -Encoding utf8NoBOM -LiteralPath (Join-Path $capsuleA "README.md")
```

The README contains no absolute path, credential-bearing remote URL, account
session data, encryption recovery material, or secret value.

### Task 5: Classify, constrain, and checksum the capsule

**Files:**
- Read every capsule artifact
- Create: `$capsuleA/SHA256SUMS.txt`

- [ ] **Step 1: Classify the patch and every TAR member fail-closed**

Use the scanner's correct `classifyBlob(repositoryPath, bytes)` signature.
The helper may run from memory but must emit only category, relative path, and
count. It must never emit matched content.

```powershell
node --input-type=module -e "import {readFile} from 'node:fs/promises'; import {classifyBlob} from './scripts/check-push-graph.mjs'; const p=process.argv[1]; const b=await readFile(p); const f=classifyBlob('patches/k1-consolidation-unstaged.patch',b); console.log(JSON.stringify(f.map(({category,path,count})=>({category,path,count})))); process.exitCode=f.length===0?0:1" $patchPath
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_PATCH_CLASSIFICATION_FAILED" }
```

Expected: `[]`. There is no category allow-list for this checkpoint.

For the TAR, enumerate exactly 15 safe members and inspect them only on medium
A:

```powershell
$tarMembers = @(tar -tf $g0Tar | ForEach-Object { $_.Replace("\", "/") })
if ($LASTEXITCODE -ne 0 -or $tarMembers.Count -ne 15) {
  throw "MIGRATION_TAR_MEMBER_COUNT_FAILED"
}
$expectedMembers = @($g0Lines | ForEach-Object { $_.Substring(66) }) | Sort-Object
foreach ($member in $tarMembers) {
  $parts = @($member -split '/')
  if ([IO.Path]::IsPathRooted($member) -or
      $member -match '^[A-Za-z]:' -or
      @($parts | Where-Object { $_ -eq "" -or $_ -eq "." -or $_ -eq ".." }).Count -ne 0) {
    throw "MIGRATION_TAR_MEMBER_PATH_INVALID"
  }
}
if (@(Compare-Object $expectedMembers ($tarMembers | Sort-Object)).Count -ne 0) {
  throw "MIGRATION_TAR_MEMBER_SET_MISMATCH"
}
$inspectionRoot = Join-Path $mediaA "2026-08-27-aurelia-capsule-inspection"
if (Test-Path -LiteralPath $inspectionRoot) { throw "MIGRATION_INSPECTION_ROOT_EXISTS" }
New-Item -ItemType Directory -Path $inspectionRoot | Out-Null
tar -xf $g0Tar -C $inspectionRoot
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_INSPECTION_EXTRACT_FAILED" }
$scanCode = @'
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { classifyBlob } from "./scripts/check-push-graph.mjs";
const [root, ...paths] = process.argv.slice(1);
let blocked = false;
for (const path of paths) {
  const findings = classifyBlob(path, await readFile(join(root, path)));
  const safe = findings.map(({ category, path, count }) => ({ category, path, count }));
  if (safe.length) console.log(JSON.stringify(safe));
  if (findings.length !== 0) blocked = true;
}
process.exitCode = blocked ? 2 : 0;
'@
& node --input-type=module -e $scanCode $inspectionRoot @tarMembers
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_TAR_CLASSIFICATION_FAILED" }
$inspectionResolved = (Resolve-Path -LiteralPath $inspectionRoot).Path
$mediaAPrefix = $mediaA.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
if (-not $inspectionResolved.StartsWith($mediaAPrefix, [StringComparison]::OrdinalIgnoreCase)) {
  throw "MIGRATION_INSPECTION_PATH_ESCAPE"
}
$inspectionFiles = @(Get-ChildItem -LiteralPath $inspectionResolved -File -Recurse)
$inspectionRelative = @($inspectionFiles | ForEach-Object {
  if (($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      -not [string]::IsNullOrEmpty($_.LinkType)) {
    throw "MIGRATION_INSPECTION_REPARSE_FILE"
  }
  $resolved = [IO.Path]::GetFullPath($_.FullName)
  $inspectionPrefix = $inspectionResolved.TrimEnd([IO.Path]::DirectorySeparatorChar) +
    [IO.Path]::DirectorySeparatorChar
  if (-not $resolved.StartsWith($inspectionPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "MIGRATION_INSPECTION_FILE_ESCAPE"
  }
  [IO.Path]::GetRelativePath($inspectionResolved, $resolved).Replace("\", "/")
} | Sort-Object)
if (@(Compare-Object $expectedMembers $inspectionRelative).Count -ne 0) {
  throw "MIGRATION_INSPECTION_FILE_SET_MISMATCH"
}
Remove-Item -LiteralPath $inspectionResolved -Recurse
```

The scan prints only category, repository-relative path, and count. Every
finding stops. There is no silent or review-time allow-list.

- [ ] **Step 2: Reject undeclared layout entries**

```powershell
$expectedFiles = @(
  "README.md",
  "git/aurelia-all-refs.bundle",
  "patches/k1-consolidation-unstaged.patch",
  "untracked/g0-untracked-plans.tar",
  "inventory/refs.txt",
  "inventory/worktrees.txt",
  "inventory/statuses.txt",
  "inventory/toolchain.txt",
  "inventory/git-config-sanitized.txt",
  "inventory/g0-untracked-files.txt",
  "inventory/sensitive-local-files-redacted.txt"
) | Sort-Object
$actualFiles = @(Get-ChildItem -LiteralPath $capsuleA -File -Recurse | ForEach-Object {
  [IO.Path]::GetRelativePath($capsuleA, $_.FullName).Replace("\", "/")
}) | Sort-Object
if (@(Compare-Object $expectedFiles $actualFiles).Count -ne 0) {
  throw "MIGRATION_CAPSULE_LAYOUT_MISMATCH"
}
```

- [ ] **Step 3: Scan text inventories for forbidden disclosures**

Reject absolute user paths, remote URLs, and credential-like assignments by
running the existing classifier correctly against every `.md` and `.txt` file
except the not-yet-created checksum manifest:

```powershell
$textArtifacts = @(Get-ChildItem -LiteralPath $capsuleA -File -Recurse |
  Where-Object { $_.Extension -in @(".md", ".txt") })
$textScanCode = @'
import { readFile } from "node:fs/promises";
import { classifyBlob } from "./scripts/check-push-graph.mjs";
const [capsuleRoot, ...files] = process.argv.slice(1);
let count = 0;
for (const file of files) {
  const relative = file.slice(capsuleRoot.length + 1).replaceAll("\\", "/");
  const findings = classifyBlob(relative, await readFile(file));
  for (const { category, path, count: findingCount } of findings) {
    console.log(JSON.stringify({ category, path, count: findingCount }));
    count += 1;
  }
}
process.exitCode = count === 0 ? 0 : 1;
'@
& node --input-type=module -e $textScanCode $capsuleA @($textArtifacts.FullName)
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_TEXT_INVENTORY_CLASSIFICATION_FAILED" }
```

Expected: no finding. The complete bundle is still treated as sensitive even
though its binary contents are not passed to the text classifier.

- [ ] **Step 4: Generate the deterministic SHA-256 manifest**

```powershell
New-AureliaSha256Manifest -Root $capsuleA
```

- [ ] **Step 5: Verify the manifest immediately**

```powershell
Assert-AureliaCapsuleManifest -Root $capsuleA
```

Expected: `MANIFEST_PASS files=11`.

- [ ] **Step 6: Prove the repository was not affected**

```powershell
if (git diff --cached --name-only) { throw "MIGRATION_CAPSULE_CHANGED_INDEX" }
$postCapsuleStatus = @(git status --porcelain=v1)
if ($postCapsuleStatus.Count -ne 2 -or
    @($postCapsuleStatus | Where-Object { $_ -notmatch '^ M scripts/check-push-graph(?:\.test)?\.mjs$' }).Count -ne 0) {
  throw "MIGRATION_CAPSULE_CHANGED_WORKTREE"
}
```

### Task 6: Create and verify the second encrypted copy

**Files:**
- Copy exact capsule A to `$capsuleB`

- [ ] **Step 1: Copy without deleting any existing external data**

```powershell
Copy-Item -LiteralPath $capsuleA -Destination $capsuleB -Recurse
if (-not (Test-Path -LiteralPath $capsuleB)) { throw "MIGRATION_SECOND_COPY_FAILED" }
```

The destination was proven absent in Task 2; no mirroring or destructive
delete option is permitted.

- [ ] **Step 2: Verify copy B against copy A's manifest**

```powershell
Assert-AureliaCapsuleManifest -Root $capsuleB
```

Then compare the SHA-256 of both `SHA256SUMS.txt` files.

```powershell
$manifestAHash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $capsuleA "SHA256SUMS.txt")).Hash
$manifestBHash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $capsuleB "SHA256SUMS.txt")).Hash
if ($manifestAHash -ne $manifestBHash) { throw "MIGRATION_MANIFEST_COPY_MISMATCH" }
```

Expected: both encrypted copies have the same complete manifest.

### Task 7: Restore independently from medium A into encrypted medium B

**Files:**
- Read capsule A only
- Create restore proof only under `$restoreRoot` on medium B

- [ ] **Step 1: Re-verify source A after read-back**

```powershell
if (Test-Path -LiteralPath $restoreRoot) { throw "MIGRATION_RESTORE_ROOT_EXISTS" }
New-Item -ItemType Directory -Path $restoreRoot | Out-Null
Assert-AureliaCapsuleManifest -Root $capsuleA
$manifestAPath = Join-Path $capsuleA "SHA256SUMS.txt"
$manifestAHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $manifestAPath).Hash.ToLowerInvariant()
$readbackProof = Join-Path $restoreRoot "SOURCE-READBACK.txt"
if (Test-Path -LiteralPath $readbackProof) { throw "MIGRATION_READBACK_PROOF_EXISTS" }
@(
  "source_media_label=$env:AURELIA_MEDIA_A_LABEL"
  "capsule_manifest_sha256=$manifestAHash"
  "readback_utc=$([DateTimeOffset]::UtcNow.ToString('o'))"
  "manifest_readback=PASS"
) | Set-Content -Encoding utf8NoBOM -LiteralPath $readbackProof
```

- [ ] **Step 2: Initialize independent bare verification and restore repositories**

```powershell
$verifyBare = Join-Path $restoreRoot "verify.git"
$restoreBare = Join-Path $restoreRoot "restore.git"
$emptyTemplate = Join-Path $restoreRoot "empty-template"
New-Item -ItemType Directory -Path $emptyTemplate | Out-Null
if (@(Get-ChildItem -LiteralPath $emptyTemplate -Force).Count -ne 0) {
  throw "MIGRATION_RESTORE_TEMPLATE_NOT_EMPTY"
}
$savedGitConfigEnvironment = @{}
foreach ($entry in @(Get-ChildItem Env: | Where-Object { $_.Name -like "GIT_CONFIG_*" })) {
  $savedGitConfigEnvironment[$entry.Name] = $entry.Value
  Remove-Item -LiteralPath "Env:$($entry.Name)"
}
if (@(Get-ChildItem Env: | Where-Object { $_.Name -like "GIT_CONFIG_*" }).Count -ne 0) {
  throw "MIGRATION_RESTORE_GIT_CONFIG_ENV_CLEAR_FAILED"
}
$env:GIT_CONFIG_NOSYSTEM = "1"
$env:GIT_CONFIG_GLOBAL = "NUL"
git init --bare --template=$emptyTemplate $verifyBare
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_VERIFY_REPO_INIT_FAILED" }
git -C $verifyBare bundle verify $bundle
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_BUNDLE_VERIFY_FAILED" }
git init --bare --template=$emptyTemplate $restoreBare
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_RESTORE_REPO_INIT_FAILED" }
git -C $restoreBare fetch $bundle "refs/heads/*:refs/heads/*"
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_BUNDLE_FETCH_FAILED" }
git -C $restoreBare fsck --full
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_RESTORED_FSCK_FAILED" }
```

Neither repository may use alternates:

```powershell
foreach ($bare in @($verifyBare, $restoreBare)) {
  if (Test-Path -LiteralPath (Join-Path $bare "objects/info/alternates")) {
    throw "MIGRATION_RESTORE_USES_ALTERNATES"
  }
}
```

- [ ] **Step 3: Compare every restored local branch head**

```powershell
$expectedRefs = @(Get-Content -LiteralPath (Join-Path $capsuleA "inventory/refs.txt"))
$restoredRefs = @(git -C $restoreBare for-each-ref --sort=refname --format="%(refname) %(objectname)" refs/heads)
if ($LASTEXITCODE -ne 0 -or
    @(Compare-Object $expectedRefs $restoredRefs -CaseSensitive).Count -ne 0) {
  throw "MIGRATION_RESTORED_REFS_MISMATCH"
}
```

- [ ] **Step 4: Create four explicit restored worktrees**

```powershell
$restoredWorktrees = Join-Path $restoreRoot "worktrees"
New-Item -ItemType Directory -Path $restoredWorktrees | Out-Null
$restoredPrep = Join-Path $restoredWorktrees "preparation"
$restoredG0 = Join-Path $restoredWorktrees "g0"
$restoredCanon = Join-Path $restoredWorktrees "canon"
$restoredK1 = Join-Path $restoredWorktrees "consolidation"
git -C $restoreBare worktree add $restoredPrep codex/aurelia-vorbereitung
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_RESTORE_PREPARATION_FAILED" }
git -C $restoreBare worktree add $restoredG0 codex/aurelia-g0-governance
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_RESTORE_G0_FAILED" }
git -C $restoreBare worktree add $restoredCanon codex/aurelia-kanon-implementation
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_RESTORE_CANON_FAILED" }
git -C $restoreBare worktree add $restoredK1 codex/aurelia-konsolidierung
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_RESTORE_CONSOLIDATION_FAILED" }
```

- [ ] **Step 5: Check and apply the K1 patch**

```powershell
git -C $restoredK1 apply --check $patchPath
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_PATCH_CHECK_FAILED" }
git -C $restoredK1 apply $patchPath
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_PATCH_APPLY_FAILED" }
```

- [ ] **Step 6: Validate and extract the G0 TAR**

```powershell
$g0TarFromA = Join-Path $capsuleA "untracked/g0-untracked-plans.tar"
$restoreTarMembers = @(tar -tf $g0TarFromA | ForEach-Object { $_.Replace("\", "/") })
$restoreExpectedMembers = @(Get-Content -LiteralPath (Join-Path $capsuleA "inventory/g0-untracked-files.txt") |
  ForEach-Object {
    if ($_ -notmatch '^[0-9a-f]{64}  (?<Relative>[^\r\n]+)$') {
      throw "MIGRATION_G0_INVENTORY_LINE_INVALID"
    }
    $Matches.Relative
  } | Sort-Object)
if ($LASTEXITCODE -ne 0 -or $restoreTarMembers.Count -ne 15) {
  throw "MIGRATION_RESTORE_TAR_MEMBER_COUNT_FAILED"
}
foreach ($member in $restoreTarMembers) {
  $parts = @($member -split '/')
  if ([IO.Path]::IsPathRooted($member) -or
      $member -match '^[A-Za-z]:' -or
      @($parts | Where-Object { $_ -eq "" -or $_ -eq "." -or $_ -eq ".." }).Count -ne 0) {
    throw "MIGRATION_RESTORE_TAR_MEMBER_PATH_INVALID"
  }
}
if (@(Compare-Object $restoreExpectedMembers ($restoreTarMembers | Sort-Object)).Count -ne 0) {
  throw "MIGRATION_RESTORE_TAR_MEMBER_SET_MISMATCH"
}
tar -xf $g0TarFromA -C $restoredG0
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_G0_TAR_EXTRACT_FAILED" }
```

- [ ] **Step 7: Compare restored hashes and exact statuses**

```powershell
if (@(git -C $restoredPrep status --porcelain=v1).Count -ne 0) {
  throw "MIGRATION_RESTORED_PREPARATION_NOT_CLEAN"
}
if (@(git -C $restoredCanon status --porcelain=v1).Count -ne 0) {
  throw "MIGRATION_RESTORED_CANON_NOT_CLEAN"
}
$restoredG0Status = @(git -C $restoredG0 status --porcelain=v1)
if ($restoredG0Status.Count -ne 15 -or
    @($restoredG0Status | Where-Object { $_ -notmatch '^\?\? docs/superpowers/plans/' }).Count -ne 0) {
  throw "MIGRATION_RESTORED_G0_STATUS_MISMATCH"
}
$restoredG0Prefix = [IO.Path]::GetFullPath($restoredG0).TrimEnd([IO.Path]::DirectorySeparatorChar) +
  [IO.Path]::DirectorySeparatorChar
$restoredOverlayFiles = @(Get-ChildItem -LiteralPath (Join-Path $restoredG0 "docs/superpowers/plans") -File -Recurse)
$restoredOverlayRelative = @($restoredOverlayFiles | ForEach-Object {
  $resolved = [IO.Path]::GetFullPath($_.FullName)
  if (($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      -not [string]::IsNullOrEmpty($_.LinkType) -or
      -not $resolved.StartsWith($restoredG0Prefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "MIGRATION_RESTORED_G0_REPARSE_OR_ESCAPE"
  }
  [IO.Path]::GetRelativePath($restoredG0, $resolved).Replace("\", "/")
} | Sort-Object)
if (@(Compare-Object $restoreExpectedMembers $restoredOverlayRelative).Count -ne 0) {
  throw "MIGRATION_RESTORED_G0_FILE_SET_MISMATCH"
}
$restoredK1Status = @(git -C $restoredK1 status --porcelain=v1)
if ($restoredK1Status.Count -ne 2 -or
    @($restoredK1Status | Where-Object { $_ -notmatch '^ M scripts/check-push-graph(?:\.test)?\.mjs$' }).Count -ne 0) {
  throw "MIGRATION_RESTORED_K1_STATUS_MISMATCH"
}
$restoredScannerExpected = @{
  "scripts/check-push-graph.mjs" = "32c0b5b4ec3fdf5083bc399c5525e11281d7f6301e86e5670840cca9bca1abef"
  "scripts/check-push-graph.test.mjs" = "ce9e3a6d88e01a5d935212d848141d29f82aa282848f0d749d1427bd9b4a44b9"
}
foreach ($entry in $restoredScannerExpected.GetEnumerator()) {
  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $restoredK1 $entry.Key)).Hash.ToLowerInvariant()
  if ($actual -ne $entry.Value) { throw "MIGRATION_RESTORED_SCANNER_HASH_MISMATCH" }
}
foreach ($line in @(Get-Content -LiteralPath (Join-Path $capsuleA "inventory/g0-untracked-files.txt"))) {
  if ($line -notmatch '^(?<Digest>[0-9a-f]{64})  (?<Relative>[^\r\n]+)$') {
    throw "MIGRATION_RESTORED_G0_HASH_LINE_INVALID"
  }
  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $restoredG0 $Matches.Relative)).Hash.ToLowerInvariant()
  if ($actual -ne $Matches.Digest) { throw "MIGRATION_RESTORED_G0_HASH_MISMATCH" }
}
```

- [ ] **Step 8: Check Linux-sensitive repository properties**

```powershell
foreach ($restored in @($restoredPrep, $restoredG0, $restoredCanon, $restoredK1)) {
  $paths = @(git -C $restored ls-tree -r --name-only HEAD)
  $caseGroups = @($paths | Group-Object { $_.ToLowerInvariant() } | Where-Object { $_.Count -gt 1 })
  if ($caseGroups.Count -ne 0) { throw "MIGRATION_RESTORED_CASE_COLLISION" }
  $symlinks = @(git -C $restored ls-tree -r HEAD | Where-Object { $_ -match '^120000 ' })
  if ($symlinks.Count -ne 0) { throw "MIGRATION_RESTORED_SYMLINK_FOUND" }
}
foreach ($branch in $requiredBranches) {
  $sourceTree = @(git -C $worktrees[$branch] ls-tree -r $branch)
  $restoredTree = @(git -C $restoreBare ls-tree -r $branch)
  if (@(Compare-Object $sourceTree $restoredTree -CaseSensitive).Count -ne 0) {
    throw "MIGRATION_RESTORED_TREE_MISMATCH"
  }
}
$startupMode = (git -C $restoredK1 ls-files --stage -- startup.sh) -split '\s+' | Select-Object -First 1
if ($startupMode -ne "100755") { throw "MIGRATION_STARTUP_MODE_MISMATCH" }
if (git -C $restoredK1 diff --summary) { throw "MIGRATION_PATCH_MODE_CHANGE_FOUND" }
```

- [ ] **Step 9: Record the restore proof without sensitive paths**

```powershell
$restoreProof = Join-Path $restoreRoot "RESTORE-PROOF.txt"
@(
  "source_media_label=$env:AURELIA_MEDIA_A_LABEL"
  "test_media_label=$env:AURELIA_MEDIA_B_LABEL"
  "capsule_manifest_sha256=$manifestAHash"
  "bundle_verify=PASS"
  "restored_fsck=PASS"
  "refs_compare=PASS"
  "patch_restore=PASS"
  "g0_restore=PASS"
  "status_compare=PASS"
  "path_mode_checks=PASS"
  "overall=PASS"
) | Set-Content -Encoding utf8NoBOM -LiteralPath $restoreProof
$restoreProofHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $restoreProof).Hash.ToLowerInvariant()
"RESTORE_PROOF_SHA256=$restoreProofHash"
Remove-Item Env:GIT_CONFIG_NOSYSTEM
Remove-Item Env:GIT_CONFIG_GLOBAL
foreach ($entry in $savedGitConfigEnvironment.GetEnumerator()) {
  [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value)
}
if (@(Get-ChildItem Env: | Where-Object { $_.Name -like "GIT_CONFIG_*" }).Count -ne $savedGitConfigEnvironment.Count) {
  throw "MIGRATION_RESTORE_GIT_CONFIG_ENV_NOT_RESTORED"
}
```

Do not delete `$restoreRoot` until the push and final operator review are
complete. If it is later deleted, first resolve its absolute path and prove it
is a descendant of `$mediaB`; never use a wildcard or unresolved variable.

### Task 8: Re-evaluate the one-time full-graph publication exception

**Files:**
- Read Git refs and current scanner only
- Write no repository file

- [ ] **Step 1: Prove the exact remote identity and private visibility**

Do not print the configured URL. Accept one credential-free canonical GitHub
form and reject every explicit `pushurl`:

```powershell
$allowedOriginUrls = @(
  "https://github.com/redshift-three67/aurelia.git",
  ("git" + "@github.com:redshift-three67/aurelia.git"),
  ("ssh://git" + "@github.com/redshift-three67/aurelia.git")
)
$originUrls = @(git remote get-url --all origin)
if ($LASTEXITCODE -ne 0 -or $originUrls.Count -ne 1 -or
    $originUrls[0] -notin $allowedOriginUrls) {
  throw "MIGRATION_ORIGIN_IDENTITY_MISMATCH"
}
$effectivePushUrls = @(git remote get-url --push --all origin)
if ($LASTEXITCODE -ne 0 -or $effectivePushUrls.Count -ne 1 -or
    $effectivePushUrls[0] -notin $allowedOriginUrls) {
  throw "MIGRATION_EFFECTIVE_PUSH_URL_MISMATCH"
}
$configuredPushUrls = @(git config --get-all remote.origin.pushurl)
if ($configuredPushUrls.Count -ne 0) { throw "MIGRATION_ORIGIN_PUSHURL_FORBIDDEN" }
$urlRewriteRules = @(git config --show-origin --get-regexp '^url\..*\.(insteadOf|pushInsteadOf)$')
if ($urlRewriteRules.Count -ne 0) { throw "MIGRATION_URL_REWRITE_RULE_FORBIDDEN" }
$privateProof = @(gh repo view redshift-three67/aurelia --json nameWithOwner,isPrivate --jq '.nameWithOwner + "|" + (.isPrivate|tostring)')
if ($LASTEXITCODE -ne 0 -or $privateProof.Count -ne 1 -or
    $privateProof[0] -ne "redshift-three67/aurelia|true") {
  throw "MIGRATION_GITHUB_PRIVATE_IDENTITY_UNPROVEN"
}
```

An authentication failure stops. It is not bypassed by relying on the Git
remote URL alone.

- [ ] **Step 2: Fetch only the authorized remote branch**

```powershell
git fetch --no-tags origin `
  refs/heads/codex/aurelia-konsolidierung:refs/remotes/origin/codex/aurelia-konsolidierung
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_REMOTE_FETCH_FAILED" }
$remoteNow = (git rev-parse refs/remotes/origin/codex/aurelia-konsolidierung).Trim()
if ($remoteNow -ne "029bdcef62ccff35c0e964588e32a9727ea42470") {
  throw "MIGRATION_REMOTE_CHANGED_EXCEPTION_INVALID"
}
git merge-base --is-ancestor $remoteNow HEAD
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_PUSH_NOT_FAST_FORWARD" }
```

- [ ] **Step 3: Re-prove index, dirty scope, scanner hashes, G0, and ignored scope**

```powershell
if ((git branch --show-current).Trim() -ne "codex/aurelia-konsolidierung") {
  throw "MIGRATION_PUSH_BRANCH_MISMATCH"
}
if (git diff --cached --name-only) { throw "MIGRATION_PUSH_INDEX_NOT_EMPTY" }
$prePushDirty = @(git status --porcelain=v1)
if ($prePushDirty.Count -ne 2 -or
    @($prePushDirty | Where-Object { $_ -notmatch '^ M scripts/check-push-graph(?:\.test)?\.mjs$' }).Count -ne 0) {
  throw "MIGRATION_PUSH_DIRTY_SCOPE_MISMATCH"
}
$prePushHashes = @{
  "scripts/check-push-graph.mjs" = "32c0b5b4ec3fdf5083bc399c5525e11281d7f6301e86e5670840cca9bca1abef"
  "scripts/check-push-graph.test.mjs" = "ce9e3a6d88e01a5d935212d848141d29f82aa282848f0d749d1427bd9b4a44b9"
}
foreach ($entry in $prePushHashes.GetEnumerator()) {
  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Key).Hash.ToLowerInvariant()
  if ($actual -ne $entry.Value) { throw "MIGRATION_PUSH_SCANNER_HASH_MISMATCH" }
}
$prePushG0 = @(git -C $g0Root status --porcelain=v1)
if ($prePushG0.Count -ne 15 -or
    @($prePushG0 | Where-Object { $_ -notmatch '^\?\? docs/superpowers/plans/' }).Count -ne 0) {
  throw "MIGRATION_PUSH_G0_SCOPE_MISMATCH"
}
$prePushLocalRefs = @(git for-each-ref --sort=refname --format="%(refname)" refs/heads)
if (@(Compare-Object $expectedLocalRefs $prePushLocalRefs -CaseSensitive).Count -ne 0) {
  throw "MIGRATION_PUSH_LOCAL_BRANCH_SET_MISMATCH"
}
$prePushWorktreeLines = @(git worktree list --porcelain | Where-Object {
  $_.StartsWith("worktree ")
})
if ($prePushWorktreeLines.Count -ne 4) { throw "MIGRATION_PUSH_WORKTREE_COUNT_MISMATCH" }
if (@(git -C $prepRoot status --porcelain=v1).Count -ne 0 -or
    @(git -C $canonRoot status --porcelain=v1).Count -ne 0) {
  throw "MIGRATION_PUSH_CLEAN_WORKTREE_CHANGED"
}
git rev-parse --verify --quiet refs/stash | Out-Null
if ($LASTEXITCODE -eq 0) { throw "MIGRATION_PUSH_STASH_PRESENT" }
if ($LASTEXITCODE -ne 1) { throw "MIGRATION_PUSH_STASH_CHECK_FAILED" }
$prePushUnexpectedRefs = @(git for-each-ref --format="%(refname)" | Where-Object {
  $_ -notlike 'refs/heads/*' -and
  $_ -notlike 'refs/remotes/origin/*' -and
  $_ -notlike 'refs/codex/turn-diffs/*'
})
if ($prePushUnexpectedRefs.Count -ne 0) { throw "MIGRATION_PUSH_UNEXPECTED_LOCAL_REF" }
$prePushIgnored = @(git -C $repositoryRoot ls-files --others --ignored --exclude-standard |
  Where-Object { $_ -notlike '.worktrees/*' } | Sort-Object -Unique)
$prePushIgnoredPayload = [Text.Encoding]::UTF8.GetBytes(($prePushIgnored -join "`n") + "`n")
$prePushIgnoredDigest = [Convert]::ToHexString(
  [Security.Cryptography.SHA256]::HashData($prePushIgnoredPayload)
).ToLowerInvariant()
if ($prePushIgnored.Count -ne 52 -or
    $prePushIgnoredDigest -ne "afc5834d0b84f3153e86dec429b55aae0aac55b944de26ab4324dd3b942d2f36") {
  throw "MIGRATION_PUSH_IGNORED_SCOPE_MISMATCH"
}
```

- [ ] **Step 4: Compare remote and candidate full-graph record keys in memory**

Use the dirty scanner only after its exact hashes have been verified. Compare
the two complete graphs with base equal to the remote ref:

```powershell
node --input-type=module -e "import {scanGraph} from './scripts/check-push-graph.mjs'; const root=process.cwd(); const remote='refs/remotes/origin/codex/aurelia-konsolidierung'; const published=scanGraph({root,base:remote,head:remote,mode:'full'}); const candidate=scanGraph({root,base:remote,head:'HEAD',mode:'full'}); if(published.exitCode!==1||candidate.exitCode!==1||published.diagnostics.length||candidate.diagnostics.length){console.error('GRAPH_EXECUTION_MISMATCH');process.exit(2)} const key=x=>[x.category,x.blob,x.path].join('\u0000'); const a=new Set(published.findings.map(key)); const b=new Set(candidate.findings.map(key)); const added=[...b].filter(x=>!a.has(x)); const removed=[...a].filter(x=>!b.has(x)); const counts=x=>Object.fromEntries([...x.findings.reduce((m,f)=>m.set(f.category,(m.get(f.category)||0)+f.count),new Map())].sort()); console.log(JSON.stringify({published_records:a.size,candidate_records:b.size,added_records:added.length,removed_records:removed.length,published_categories:counts(published),candidate_categories:counts(candidate)})); process.exitCode=added.length===0&&removed.length===0?0:1"
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_GRAPH_EXCEPTION_CHANGED" }
```

Expected result:

```json
{"published_records":15,"candidate_records":15,"added_records":0,"removed_records":0,"published_categories":{"absolute_user_path":7,"credential_like":5,"env_or_key_material":1,"operational_identity":2,"unscannable":1},"candidate_categories":{"absolute_user_path":7,"credential_like":5,"env_or_key_material":1,"operational_identity":2,"unscannable":1}}
```

The exact record keys remain in memory and are not printed. Any added or
removed record, diagnostic, or unexpected exit code stops the push.

- [ ] **Step 5: Capture the final authorized local target**

```powershell
$pushTarget = (git rev-parse HEAD).Trim()
if ($pushTarget -notmatch '^[0-9a-f]{40}$') { throw "MIGRATION_PUSH_TARGET_INVALID" }
$branchTarget = (git rev-parse refs/heads/codex/aurelia-konsolidierung).Trim()
if ($pushTarget -ne $branchTarget) { throw "MIGRATION_HEAD_BRANCH_DIVERGENCE" }
if ($pushTarget -eq $remoteNow) { throw "MIGRATION_PUSH_TARGET_NOT_STRICT_DESCENDANT" }
```

Do not write `$pushTarget` into a tracked file.

### Task 9: Perform the single authorized private fast-forward push

**Files:**
- No file changes
- Remote mutation: only `refs/heads/codex/aurelia-konsolidierung`

- [ ] **Step 1: Execute the explicit one-ref push**

```powershell
$privateProofImmediatelyBeforePush = @(gh repo view redshift-three67/aurelia --json nameWithOwner,isPrivate --jq '.nameWithOwner + "|" + (.isPrivate|tostring)')
if ($LASTEXITCODE -ne 0 -or
    $privateProofImmediatelyBeforePush.Count -ne 1 -or
    $privateProofImmediatelyBeforePush[0] -ne "redshift-three67/aurelia|true") {
  throw "MIGRATION_PUSH_PRIVATE_IDENTITY_UNPROVEN"
}
$effectivePushImmediatelyBefore = @(git remote get-url --push --all origin)
if ($LASTEXITCODE -ne 0 -or $effectivePushImmediatelyBefore.Count -ne 1 -or
    $effectivePushImmediatelyBefore[0] -ne $effectivePushUrls[0]) {
  throw "MIGRATION_PUSH_EFFECTIVE_URL_CHANGED"
}
$urlRewriteImmediatelyBefore = @(git config --show-origin --get-regexp '^url\..*\.(insteadOf|pushInsteadOf)$')
if ($urlRewriteImmediatelyBefore.Count -ne 0) {
  throw "MIGRATION_PUSH_URL_REWRITE_RULE_FOUND"
}
$liveImmediatelyBeforePush = @(git ls-remote --exit-code origin refs/heads/codex/aurelia-konsolidierung)
if ($LASTEXITCODE -ne 0 -or $liveImmediatelyBeforePush.Count -ne 1 -or
    ($liveImmediatelyBeforePush[0] -split "\s+")[0] -ne $remoteNow) {
  throw "MIGRATION_PUSH_REMOTE_CHANGED"
}
$hookRoot = Join-Path $mediaA "2026-08-27-aurelia-push-cas-hook"
if (Test-Path -LiteralPath $hookRoot) { throw "MIGRATION_PUSH_HOOK_ROOT_EXISTS" }
New-Item -ItemType Directory -Path $hookRoot | Out-Null
$hookTemplate = @'
#!/bin/sh
set -eu
test "$1" = "origin" || exit 39
test "$2" = "__REMOTE_URL__" || exit 40
count=0
while IFS=' ' read -r local_ref local_oid remote_ref remote_oid
do
  count=$((count + 1))
  test "$local_ref" = "refs/heads/codex/aurelia-konsolidierung" || exit 41
  test "$local_oid" = "__LOCAL_OID__" || exit 42
  test "$remote_ref" = "refs/heads/codex/aurelia-konsolidierung" || exit 43
  test "$remote_oid" = "029bdcef62ccff35c0e964588e32a9727ea42470" || exit 44
done
test "$count" -eq 1 || exit 45
'@
$hookText = $hookTemplate.Replace("__LOCAL_OID__", $pushTarget).Replace(
  "__REMOTE_URL__",
  $effectivePushUrls[0]
)
$hookPath = Join-Path $hookRoot "pre-push"
[IO.File]::WriteAllText(
  $hookPath,
  $hookText.Replace("`r`n", "`n") + "`n",
  [Text.UTF8Encoding]::new($false)
)
$hookHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $hookPath).Hash.ToLowerInvariant()
git -c core.hooksPath=$hookRoot push --porcelain origin `
  refs/heads/codex/aurelia-konsolidierung:refs/heads/codex/aurelia-konsolidierung
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_AUTHORIZED_PUSH_FAILED" }
```

The command must contain neither `--force` nor `--all`; no other refspec is
permitted. The isolated pre-push hook validates the exact server-advertised old
OID, local OID, local ref, remote ref, and one-ref count before Git sends the
update. Git's receive-pack then performs the compare-and-swap against that
advertised old OID. A race, stale ref, or non-fast-forward response stops
without retrying through another strategy.

- [ ] **Step 2: Verify the live remote target independently**

```powershell
$remoteLine = @(git ls-remote --exit-code origin refs/heads/codex/aurelia-konsolidierung)
if ($LASTEXITCODE -ne 0 -or $remoteLine.Count -ne 1) {
  throw "MIGRATION_REMOTE_READBACK_FAILED"
}
$remoteAfter = ($remoteLine[0] -split "\s+")[0]
if ($remoteAfter -ne $pushTarget) { throw "MIGRATION_REMOTE_TARGET_MISMATCH" }
```

- [ ] **Step 3: Write an encrypted, non-capsule push receipt**

```powershell
$pushReceipt = Join-Path $mediaA "2026-08-27-aurelia-consolidation-push-receipt.txt"
if (Test-Path -LiteralPath $pushReceipt) { throw "MIGRATION_PUSH_RECEIPT_EXISTS" }
@(
  "branch=codex/aurelia-konsolidierung"
  "old_remote=029bdcef62ccff35c0e964588e32a9727ea42470"
  "new_remote=$pushTarget"
  "verified_utc=$([DateTimeOffset]::UtcNow.ToString('o'))"
  "fast_forward=PASS"
  "force_push=false"
  "other_refs_pushed=0"
  "pre_push_cas_hook_sha256=$hookHash"
) | Set-Content -Encoding utf8NoBOM -LiteralPath $pushReceipt
$pushReceiptHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $pushReceipt).Hash.ToLowerInvariant()
"PUSH_RECEIPT_SHA256=$pushReceiptHash"
```

The receipt remains a sibling under encrypted medium A. It does not modify the
capsule or its verified manifest.

- [ ] **Step 4: Prove the local overlays remain unchanged**

```powershell
if (git diff --cached --name-only) { throw "MIGRATION_POSTPUSH_INDEX_NOT_EMPTY" }
$postPushDirty = @(git status --porcelain=v1)
if ($postPushDirty.Count -ne 2 -or
    @($postPushDirty | Where-Object { $_ -notmatch '^ M scripts/check-push-graph(?:\.test)?\.mjs$' }).Count -ne 0) {
  throw "MIGRATION_POSTPUSH_DIRTY_SCOPE_MISMATCH"
}
foreach ($entry in $prePushHashes.GetEnumerator()) {
  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Key).Hash.ToLowerInvariant()
  if ($actual -ne $entry.Value) { throw "MIGRATION_POSTPUSH_SCANNER_HASH_MISMATCH" }
}
$postPushG0 = @(git -C $g0Root status --porcelain=v1)
if ($postPushG0.Count -ne 15 -or
    @($postPushG0 | Where-Object { $_ -notmatch '^\?\? docs/superpowers/plans/' }).Count -ne 0) {
  throw "MIGRATION_POSTPUSH_G0_SCOPE_MISMATCH"
}
$postPushIgnored = @(git -C $repositoryRoot ls-files --others --ignored --exclude-standard |
  Where-Object { $_ -notlike '.worktrees/*' } | Sort-Object -Unique)
$postPushIgnoredPayload = [Text.Encoding]::UTF8.GetBytes(($postPushIgnored -join "`n") + "`n")
$postPushIgnoredDigest = [Convert]::ToHexString(
  [Security.Cryptography.SHA256]::HashData($postPushIgnoredPayload)
).ToLowerInvariant()
if ($postPushIgnored.Count -ne 52 -or
    $postPushIgnoredDigest -ne "afc5834d0b84f3153e86dec429b55aae0aac55b944de26ab4324dd3b942d2f36") {
  throw "MIGRATION_POSTPUSH_IGNORED_SCOPE_MISMATCH"
}
$remotePostProof = @(git ls-remote --exit-code origin refs/heads/codex/aurelia-konsolidierung)
if ($LASTEXITCODE -ne 0 -or $remotePostProof.Count -ne 1 -or
    ($remotePostProof[0] -split "\s+")[0] -ne $pushTarget) {
  throw "MIGRATION_POSTPUSH_REMOTE_MISMATCH"
}
```

### Task 10: Prepare the separate encrypted cold backup and erase gate

**Files:**
- No repository files
- Create cold-copy artifacts only on encrypted external media

- [ ] **Step 1: Produce the operator handoff checklist before closing Codex**

Require all of these facts to be visible to the operator:

- capsule A manifest PASS;
- capsule B manifest PASS;
- independent restore proof overall PASS;
- private GitHub branch equals `$pushTarget`;
- scanner and G0 overlays remain local and are recoverable from the capsule;
- 52 ignored sensitive files are still excluded from Git and capsule;
- Windows disk erasure remains unauthorized.

After the operator confirms separately held recovery material is readable and
confirms either that no additional AURELIA source exists outside the repository
or supplies its encrypted source list, create one encrypted handoff file:

```powershell
if ($env:AURELIA_RECOVERY_MATERIAL_CONFIRMED -ne "YES") {
  throw "MIGRATION_RECOVERY_MATERIAL_UNCONFIRMED"
}
$externalNone = $env:AURELIA_EXTERNAL_SOURCES_CONFIRMED_NONE -eq "YES"
$externalListProvided = -not [string]::IsNullOrWhiteSpace($env:AURELIA_EXTERNAL_SOURCE_LIST)
if ($externalNone -eq $externalListProvided) {
  throw "MIGRATION_EXTERNAL_SOURCE_DECISION_MISSING"
}
$externalMode = if ($externalNone) { "none" } else { "list" }
$externalListPath = $null
$externalListSha256 = $null
if ($externalListProvided) {
  $externalListItem = Get-Item -LiteralPath $env:AURELIA_EXTERNAL_SOURCE_LIST
  $externalListPath = $externalListItem.FullName
  $mediaAPrefix = $mediaA.TrimEnd([IO.Path]::DirectorySeparatorChar) +
    [IO.Path]::DirectorySeparatorChar
  if (-not $externalListPath.StartsWith($mediaAPrefix, [StringComparison]::OrdinalIgnoreCase) -or
      $externalListItem.PSIsContainer -or
      ($externalListItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      -not [string]::IsNullOrEmpty($externalListItem.LinkType)) {
    throw "MIGRATION_EXTERNAL_SOURCE_LIST_NOT_SAFE_ON_MEDIA_A"
  }
  $cursor = $externalListItem.Directory
  $reachedMediaA = $false
  while ($null -ne $cursor) {
    if (($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
        -not [string]::IsNullOrEmpty($cursor.LinkType)) {
      throw "MIGRATION_EXTERNAL_SOURCE_LIST_REPARSE_ANCESTOR"
    }
    if ($cursor.FullName.TrimEnd([IO.Path]::DirectorySeparatorChar) -eq
        $mediaA.TrimEnd([IO.Path]::DirectorySeparatorChar)) {
      $reachedMediaA = $true
      break
    }
    $cursor = $cursor.Parent
  }
  if (-not $reachedMediaA) { throw "MIGRATION_EXTERNAL_SOURCE_LIST_MEDIA_A_NOT_REACHED" }
  $declaredExternalSources = @(Get-Content -LiteralPath $externalListPath |
    Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
  if ($declaredExternalSources.Count -eq 0) {
    throw "MIGRATION_EXTERNAL_SOURCE_LIST_EMPTY"
  }
  $externalListSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $externalListPath).Hash.ToLowerInvariant()
}
$coldInputPath = Join-Path $mediaA "2026-08-27-aurelia-cold-backup-inputs.json"
if (Test-Path -LiteralPath $coldInputPath) { throw "MIGRATION_COLD_INPUT_EXISTS" }
[pscustomobject]@{
  repositoryRoot = $repositoryRoot
  mediaARoot = $mediaA
  mediaBRoot = $mediaB
  mediaALabel = $env:AURELIA_MEDIA_A_LABEL
  mediaBLabel = $env:AURELIA_MEDIA_B_LABEL
  userProfile = $env:USERPROFILE
  ignoredCount = 52
  ignoredListSha256 = "afc5834d0b84f3153e86dec429b55aae0aac55b944de26ab4324dd3b942d2f36"
  recoveryMaterialConfirmed = $true
  externalSourcesMode = $externalMode
  externalSourceList = $externalListPath
  externalSourceListSha256 = $externalListSha256
} | ConvertTo-Json | Set-Content -Encoding utf8NoBOM -LiteralPath $coldInputPath
```

The JSON is stored only on encrypted medium A and may contain local source
paths. It is never added to the capsule, Git, logs, or chat.

- [ ] **Step 2: Stop Codex before copying user state**

The operator closes the Codex desktop app and every Codex CLI session. In a new
standalone PowerShell 7 session, set only `AURELIA_MEDIA_A_ROOT` to medium A and
run:

```powershell
$ErrorActionPreference = "Stop"
$coldInputPath = Join-Path $env:AURELIA_MEDIA_A_ROOT "2026-08-27-aurelia-cold-backup-inputs.json"
$cold = Get-Content -Raw -LiteralPath $coldInputPath | ConvertFrom-Json
$codexProcesses = @(Get-CimInstance Win32_Process | Where-Object {
  $_.Name -match '^codex(?:\.exe)?$' -or
  $_.ExecutablePath -like '*\.codex\*' -or
  $_.CommandLine -match '(^|\s)codex(?:\.exe)?(\s|$)'
})
if ($codexProcesses.Count -ne 0) { throw "MIGRATION_CODEX_PROCESS_STILL_RUNNING" }
```

The process records are counted only; names, command lines, and paths are not
printed.

- [ ] **Step 3: Create separate encrypted cold-copy artifacts**

Revalidate both BitLocker media in the new shell, then create two absent cold
roots:

```powershell
$mediaA = (Get-Item -LiteralPath $cold.mediaARoot).FullName
$mediaB = (Get-Item -LiteralPath $cold.mediaBRoot).FullName
foreach ($media in @($mediaA, $mediaB)) {
  $item = Get-Item -LiteralPath $media
  while ($null -ne $item) {
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
      throw "MIGRATION_COLD_MEDIA_REPARSE_POINT_FOUND"
    }
    $item = $item.Parent
  }
}
$volumeA = Get-BitLockerVolume -MountPoint ([IO.Path]::GetPathRoot($mediaA))
$volumeB = Get-BitLockerVolume -MountPoint ([IO.Path]::GetPathRoot($mediaB))
foreach ($volume in @($volumeA, $volumeB)) {
  if ($volume.ProtectionStatus -ne "On" -or
      $volume.LockStatus -ne "Unlocked" -or
      $volume.VolumeStatus -ne "FullyEncrypted") {
    throw "MIGRATION_COLD_MEDIA_ENCRYPTION_NOT_READY"
  }
}
$diskA = Get-Partition -DriveLetter ([IO.Path]::GetPathRoot($mediaA).Substring(0, 1)) | Get-Disk
$diskB = Get-Partition -DriveLetter ([IO.Path]::GetPathRoot($mediaB).Substring(0, 1)) | Get-Disk
if ($diskA.IsSystem -or $diskA.IsBoot -or $diskA.BusType -ne "USB" -or
    $diskB.IsSystem -or $diskB.IsBoot -or $diskB.BusType -ne "USB" -or
    [string]::IsNullOrWhiteSpace($diskA.UniqueId) -or
    [string]::IsNullOrWhiteSpace($diskB.UniqueId) -or
    $diskA.UniqueId -eq $diskB.UniqueId -or $diskA.Number -eq $diskB.Number) {
  throw "MIGRATION_COLD_MEDIA_INDEPENDENCE_FAILED"
}
$coldName = "2026-08-27-aurelia-cold-backup"
$coldA = Join-Path $mediaA $coldName
$coldB = Join-Path $mediaB $coldName
if ((Test-Path -LiteralPath $coldA) -or (Test-Path -LiteralPath $coldB)) {
  throw "MIGRATION_COLD_TARGET_EXISTS"
}
New-Item -ItemType Directory -Path $coldA | Out-Null
```

Create the artifacts directly on encrypted medium A without printing archive
members:

```powershell
$profileRoot = (Get-Item -LiteralPath $cold.userProfile).FullName
$repositoryRoot = (Get-Item -LiteralPath $cold.repositoryRoot).FullName
$codexRoot = Join-Path $profileRoot ".codex"
$sshRoot = Join-Path $profileRoot ".ssh"
if (-not (Test-Path -LiteralPath $codexRoot -PathType Container)) {
  throw "MIGRATION_CODEX_SOURCE_MISSING"
}
if (-not (Test-Path -LiteralPath $sshRoot -PathType Container)) {
  throw "MIGRATION_SSH_SOURCE_MISSING"
}
tar -cf (Join-Path $coldA "codex-user-state.tar") -C $profileRoot .codex
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_CODEX_ARCHIVE_FAILED" }
tar -cf (Join-Path $coldA "ssh-user-state.tar") -C $profileRoot .ssh
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_SSH_ARCHIVE_FAILED" }
$repositoryParent = Split-Path -Parent $repositoryRoot
$repositoryLeaf = Split-Path -Leaf $repositoryRoot
tar -cf (Join-Path $coldA "aurelia-full-repository.tar") -C $repositoryParent $repositoryLeaf
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_REPOSITORY_ARCHIVE_FAILED" }
$ignored = @(git -C $repositoryRoot ls-files --others --ignored --exclude-standard |
  Where-Object { $_ -notlike '.worktrees/*' } | Sort-Object -Unique)
$ignoredPayload = [Text.Encoding]::UTF8.GetBytes(($ignored -join "`n") + "`n")
$ignoredDigest = [Convert]::ToHexString(
  [Security.Cryptography.SHA256]::HashData($ignoredPayload)
).ToLowerInvariant()
if ($ignored.Count -ne [int]$cold.ignoredCount -or
    $ignoredDigest -ne [string]$cold.ignoredListSha256) {
  throw "MIGRATION_COLD_IGNORED_SCOPE_MISMATCH"
}
$ignoredListPath = Join-Path $coldA "ignored-sensitive-files.list"
$ignored | Set-Content -Encoding utf8NoBOM -LiteralPath $ignoredListPath
tar -cf (Join-Path $coldA "ignored-sensitive-files.tar") -C $repositoryRoot -T $ignoredListPath
if ($LASTEXITCODE -ne 0) { throw "MIGRATION_IGNORED_ARCHIVE_FAILED" }
$gitConfig = Join-Path $profileRoot ".gitconfig"
if (Test-Path -LiteralPath $gitConfig -PathType Leaf) {
  Copy-Item -LiteralPath $gitConfig -Destination (Join-Path $coldA "git-user-config")
}
$editorRoot = Join-Path $env:APPDATA "Code/User"
if (Test-Path -LiteralPath $editorRoot -PathType Container) {
  tar -cf (Join-Path $coldA "editor-user-settings.tar") -C (Split-Path -Parent $editorRoot) (Split-Path -Leaf $editorRoot)
  if ($LASTEXITCODE -ne 0) { throw "MIGRATION_EDITOR_ARCHIVE_FAILED" }
}
$externalMode = [string]$cold.externalSourcesMode
if ($externalMode -eq "list") {
  $externalListItem = Get-Item -LiteralPath ([string]$cold.externalSourceList)
  $externalList = $externalListItem.FullName
  $mediaAPrefix = $mediaA.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
  if (-not $externalList.StartsWith($mediaAPrefix, [StringComparison]::OrdinalIgnoreCase) -or
      $externalListItem.PSIsContainer -or
      ($externalListItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
      -not [string]::IsNullOrEmpty($externalListItem.LinkType)) {
    throw "MIGRATION_COLD_EXTERNAL_LIST_OUTSIDE_MEDIA_A"
  }
  $cursor = $externalListItem.Directory
  $reachedMediaA = $false
  while ($null -ne $cursor) {
    if (($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
        -not [string]::IsNullOrEmpty($cursor.LinkType)) {
      throw "MIGRATION_COLD_EXTERNAL_LIST_REPARSE_ANCESTOR"
    }
    if ($cursor.FullName.TrimEnd([IO.Path]::DirectorySeparatorChar) -eq
        $mediaA.TrimEnd([IO.Path]::DirectorySeparatorChar)) {
      $reachedMediaA = $true
      break
    }
    $cursor = $cursor.Parent
  }
  if (-not $reachedMediaA) { throw "MIGRATION_COLD_EXTERNAL_LIST_MEDIA_A_NOT_REACHED" }
  $externalListActualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $externalList).Hash.ToLowerInvariant()
  if ($externalListActualHash -ne [string]$cold.externalSourceListSha256) {
    throw "MIGRATION_COLD_EXTERNAL_LIST_CHANGED"
  }
  $externalSources = @(Get-Content -LiteralPath $externalList |
    Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
  if ($externalSources.Count -eq 0) { throw "MIGRATION_COLD_EXTERNAL_LIST_EMPTY" }
  $externalArchive = Join-Path $coldA "external-aurelia-sources.tar"
  $externalTarArguments = @("-cf", $externalArchive)
  $externalRecords = [Collections.Generic.List[string]]::new()
  $externalLeaves = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
  $repositoryPrefix = $repositoryRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
  $mediaBPrefix = $mediaB.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
  foreach ($declaredSource in $externalSources) {
    if (-not [IO.Path]::IsPathFullyQualified($declaredSource)) {
      throw "MIGRATION_COLD_EXTERNAL_SOURCE_NOT_ABSOLUTE"
    }
    $source = Get-Item -LiteralPath $declaredSource -Force
    if ($source.PSProvider.Name -ne "FileSystem" -or
        ($source.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
        -not [string]::IsNullOrEmpty($source.LinkType)) {
      throw "MIGRATION_COLD_EXTERNAL_SOURCE_NOT_REGULAR"
    }
    $sourceFull = [IO.Path]::GetFullPath($source.FullName)
    $sourcePrefix = $sourceFull.TrimEnd([IO.Path]::DirectorySeparatorChar) +
      [IO.Path]::DirectorySeparatorChar
    if ($sourceFull -eq $repositoryRoot -or
        $sourceFull -eq $mediaA -or
        $sourceFull -eq $mediaB -or
        $sourceFull.StartsWith($repositoryPrefix, [StringComparison]::OrdinalIgnoreCase) -or
        $sourceFull.StartsWith($mediaAPrefix, [StringComparison]::OrdinalIgnoreCase) -or
        $sourceFull.StartsWith($mediaBPrefix, [StringComparison]::OrdinalIgnoreCase) -or
        $repositoryRoot.StartsWith($sourcePrefix, [StringComparison]::OrdinalIgnoreCase) -or
        $mediaA.StartsWith($sourcePrefix, [StringComparison]::OrdinalIgnoreCase) -or
        $mediaB.StartsWith($sourcePrefix, [StringComparison]::OrdinalIgnoreCase) -or
        -not $externalLeaves.Add($source.Name)) {
      throw "MIGRATION_COLD_EXTERNAL_SOURCE_SCOPE_OR_NAME_INVALID"
    }
    $externalTarArguments += @("-C", (Split-Path -Parent $source.FullName), $source.Name)
    $nodes = if ($source.PSIsContainer) {
      @($source) + @(Get-ChildItem -LiteralPath $source.FullName -Force -Recurse)
    } else {
      @($source)
    }
    foreach ($node in $nodes) {
      if (($node.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
          -not [string]::IsNullOrEmpty($node.LinkType)) {
        throw "MIGRATION_COLD_EXTERNAL_DESCENDANT_REPARSE_FOUND"
      }
      $relative = if ($node.FullName -eq $source.FullName) {
        $source.Name
      } else {
        "$($source.Name)/$([IO.Path]::GetRelativePath($source.FullName, $node.FullName).Replace('\','/'))"
      }
      if ($node.PSIsContainer) {
        $externalRecords.Add("D  $relative")
      } else {
        $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $node.FullName).Hash.ToLowerInvariant()
        $externalRecords.Add("F  $hash  $relative")
      }
    }
  }
  & tar @externalTarArguments
  if ($LASTEXITCODE -ne 0) { throw "MIGRATION_COLD_EXTERNAL_ARCHIVE_FAILED" }
  $externalTarDetails = @(tar -tvf $externalArchive)
  if ($LASTEXITCODE -ne 0 -or
      @($externalTarDetails | Where-Object { $_ -notmatch '^[d-]' }).Count -ne 0) {
    throw "MIGRATION_COLD_EXTERNAL_TAR_TYPE_INVALID"
  }
  $externalRecords | Sort-Object -Unique |
    Set-Content -Encoding utf8NoBOM -LiteralPath (Join-Path $coldA "external-aurelia-sources.manifest")
} elseif ($externalMode -ne "none") {
  throw "MIGRATION_COLD_EXTERNAL_MODE_INVALID"
}
@(
  "recovery_material_confirmed=true"
  "external_sources_mode=$externalMode"
  "ignored_sensitive_files_count=52"
  "ignored_sensitive_list_sha256=$ignoredDigest"
  "authentication_reuse_policy=rollback-only-fresh-sign-in-preferred"
) | Set-Content -Encoding utf8NoBOM -LiteralPath (Join-Path $coldA "COLD-BACKUP-METADATA.txt")
```

```powershell
New-AureliaSha256Manifest -Root $coldA
Assert-AureliaCapsuleManifest -Root $coldA
```

Both shared functions must be defined in the new shell before this command.
The verifier is generic and verifies any manifest-root tree.

- [ ] **Step 4: Verify cold-copy readability from the second medium**

```powershell
Copy-Item -LiteralPath $coldA -Destination $coldB -Recurse
if (-not (Test-Path -LiteralPath $coldB -PathType Container)) {
  throw "MIGRATION_COLD_SECOND_COPY_FAILED"
}
Assert-AureliaCapsuleManifest -Root $coldB
$coldManifestA = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $coldA "SHA256SUMS.txt")).Hash
$coldManifestB = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $coldB "SHA256SUMS.txt")).Hash
if ($coldManifestA -ne $coldManifestB) { throw "MIGRATION_COLD_MANIFEST_MISMATCH" }
$ignoredMembersB = @(tar -tf (Join-Path $coldB "ignored-sensitive-files.tar") |
  ForEach-Object { $_.Replace("\", "/") } | Sort-Object -Unique)
$ignoredMembersPayload = [Text.Encoding]::UTF8.GetBytes(($ignoredMembersB -join "`n") + "`n")
$ignoredMembersDigest = [Convert]::ToHexString(
  [Security.Cryptography.SHA256]::HashData($ignoredMembersPayload)
).ToLowerInvariant()
if ($ignoredMembersB.Count -ne 52 -or
    $ignoredMembersDigest -ne "afc5834d0b84f3153e86dec429b55aae0aac55b944de26ab4324dd3b942d2f36") {
  throw "MIGRATION_COLD_IGNORED_READBACK_MISMATCH"
}
foreach ($archive in @(
  "codex-user-state.tar",
  "ssh-user-state.tar",
  "aurelia-full-repository.tar",
  "ignored-sensitive-files.tar"
)) {
  $memberCount = @(tar -tf (Join-Path $coldB $archive)).Count
  if ($LASTEXITCODE -ne 0 -or $memberCount -eq 0) {
    throw "MIGRATION_COLD_ARCHIVE_READBACK_FAILED"
  }
}
if ([string]$cold.externalSourcesMode -eq "list") {
  $externalArchiveB = Join-Path $coldB "external-aurelia-sources.tar"
  $externalManifestB = Join-Path $coldB "external-aurelia-sources.manifest"
  if (-not (Test-Path -LiteralPath $externalArchiveB -PathType Leaf) -or
      -not (Test-Path -LiteralPath $externalManifestB -PathType Leaf)) {
    throw "MIGRATION_COLD_EXTERNAL_COPY_MISSING"
  }
  $externalMembers = @(tar -tf $externalArchiveB | ForEach-Object { $_.Replace("\", "/") })
  $externalDetails = @(tar -tvf $externalArchiveB)
  if ($LASTEXITCODE -ne 0 -or $externalMembers.Count -eq 0 -or
      $externalMembers.Count -ne $externalDetails.Count -or
      @($externalDetails | Where-Object { $_ -notmatch '^[d-]' }).Count -ne 0) {
    throw "MIGRATION_COLD_EXTERNAL_TAR_READBACK_INVALID"
  }
  foreach ($member in $externalMembers) {
    $parts = @($member -split '/')
    if ([IO.Path]::IsPathRooted($member) -or
        $member -match '^[A-Za-z]:' -or
        @($parts | Where-Object { $_ -eq "" -or $_ -eq "." -or $_ -eq ".." }).Count -ne 0) {
      throw "MIGRATION_COLD_EXTERNAL_MEMBER_PATH_INVALID"
    }
  }
  $externalReadbackRoot = Join-Path $mediaB "2026-08-27-aurelia-external-source-readback"
  if (Test-Path -LiteralPath $externalReadbackRoot) {
    throw "MIGRATION_COLD_EXTERNAL_READBACK_ROOT_EXISTS"
  }
  New-Item -ItemType Directory -Path $externalReadbackRoot | Out-Null
  tar -xf $externalArchiveB -C $externalReadbackRoot
  if ($LASTEXITCODE -ne 0) { throw "MIGRATION_COLD_EXTERNAL_EXTRACT_FAILED" }
  $readbackRecords = [Collections.Generic.List[string]]::new()
  foreach ($top in @(Get-ChildItem -LiteralPath $externalReadbackRoot -Force)) {
    $nodes = if ($top.PSIsContainer) {
      @($top) + @(Get-ChildItem -LiteralPath $top.FullName -Force -Recurse)
    } else {
      @($top)
    }
    foreach ($node in $nodes) {
      if (($node.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
          -not [string]::IsNullOrEmpty($node.LinkType)) {
        throw "MIGRATION_COLD_EXTERNAL_READBACK_REPARSE_FOUND"
      }
      $relative = [IO.Path]::GetRelativePath($externalReadbackRoot, $node.FullName).Replace("\", "/")
      if ($node.PSIsContainer) {
        $readbackRecords.Add("D  $relative")
      } else {
        $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $node.FullName).Hash.ToLowerInvariant()
        $readbackRecords.Add("F  $hash  $relative")
      }
    }
  }
  $expectedExternalRecords = @(Get-Content -LiteralPath $externalManifestB | Sort-Object -Unique)
  if (@(Compare-Object $expectedExternalRecords ($readbackRecords | Sort-Object -Unique) -CaseSensitive).Count -ne 0) {
    throw "MIGRATION_COLD_EXTERNAL_CONTENT_MISMATCH"
  }
} elseif ((Test-Path -LiteralPath (Join-Path $coldB "external-aurelia-sources.tar")) -or
          (Test-Path -LiteralPath (Join-Path $coldB "external-aurelia-sources.manifest"))) {
  throw "MIGRATION_COLD_UNDECLARED_EXTERNAL_ARTIFACT"
}
```

Archive member names are counted only and never printed. Authentication state
remains rollback material; Ubuntu uses fresh sign-in and credential rotation.

- [ ] **Step 5: Require a separate operator erase authorization**

Successful completion changes the state only to `migration-ready-for-operator-review`.
It does not authorize reinstalling, erasing, or repartitioning Windows. The
operator must explicitly confirm that both encrypted external copies are
readable and separately authorize the destructive workstation operation.

## Final acceptance matrix

| Gate | Required evidence | Failure action |
|---|---|---|
| Documentation | plan-only commit; `aec827f` ancestor | stop |
| Source scope | empty index; exact two scanner hashes; exact 15 G0 files | stop |
| Capsule A | exact layout; safe classifications; manifest PASS | stop |
| Capsule B | identical manifest; physically independent encrypted medium | stop |
| Restore | bundle, refs, fsck, worktrees, patch, TAR, hashes, modes all PASS | stop |
| Publication exception | remote unchanged; strict ancestry; `15/15`; added `0`; removed `0` | stop |
| GitHub | exactly one explicit consolidation ref; fast-forward; read-back equals target | stop |
| Cold backup | app closed; encrypted artifacts readable from independent copy | stop |
| Disk operation | new explicit operator authorization | remain paused |

## Required review routing

1. Use `Sol high` for Task 1 through Task 7 orchestration and deterministic
   verification.
2. Before Task 8, use one bounded `Sol xHigh` security review of the fresh
   evidence packet: design, plan, exact preflight facts, sanitized capsule
   manifest, and restore proof. Do not send ignored analyses, credentials,
   private-key material, raw `.codex` state, or secret-bearing paths.
3. If and only if the review returns PASS with no open P0-P2 finding, return to
   `Sol high` for Task 8 and Task 9.
4. A second reviewer is required only if the first review identifies a P0-P2
   issue, evidence is ambiguous, or a precondition changed. Routine duplicate
   reviews are not part of this checkpoint.

## Terminal stop condition

Stop without improvisation if an environment input is missing, encryption or
physical independence is unproven, an artifact target already exists, a path
escapes its encrypted root, a checksum or ref differs, the dirty/untracked
scope changes, a scanner classification is unscannable or newly sensitive, the
bundle relies on the original object database, the restore differs, GitHub
requests a non-fast-forward update, or any command would broaden the authorized
branch/server/destructive scope.

The next action after a stop is a read-only diagnosis and a new explicit
decision. It is never force, cleanup, deletion, secret disclosure, or a weaker
gate.
