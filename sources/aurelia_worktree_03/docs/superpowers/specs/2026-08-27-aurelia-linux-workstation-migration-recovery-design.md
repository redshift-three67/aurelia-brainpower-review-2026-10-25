# AURELIA Linux Workstation Migration and Recovery Design

**Status:** approved Strategy A design, documentation checkpoint only
**Date:** 2026-08-27
**Target workstation:** Ubuntu 24.04.4 LTS Desktop, amd64
**Repository:** private `redshift-three67/aurelia`
**Active branch:** `codex/aurelia-konsolidierung`

## 1. Goal

Preserve every locally relevant AURELIA state before the Windows development
workstation is reinstalled, prove that the preserved state can be restored in
an independent directory, and make the committed consolidation history
recoverable from the private GitHub repository without publishing dirty,
untracked, ignored, or sensitive local material.

This design covers the local development workstation only. It does not
authorize or perform an AURELIA server installation, SSH/IPMI access, server
mutation, `main` changes, force-push, history rewrite, production-code commit,
or Task-4 work.

## 2. Verified source state

The immutable pre-design source checkpoint is
`bf3bed79bd0357941676cd55f0e1a9962307a526`. A later documentation commit is
expected to be a descendant of this checkpoint; it must never claim its own
future commit ID inside its committed content.

| State | Verified value |
|---|---|
| Local consolidation branch | `bf3bed79bd0357941676cd55f0e1a9962307a526` |
| Remote consolidation branch | `029bdcef62ccff35c0e964588e32a9727ea42470` |
| Local/remote distance | `0 behind / 11 ahead` |
| Local branch | `codex/aurelia-konsolidierung` |
| Stashes | `0` |
| Tags | `0` |
| Submodules | none |
| Git LFS objects | none |
| Case-colliding tracked paths | none |
| Symlinks | none |
| Git object integrity | `git fsck --full --no-reflogs` completed without missing objects |

The consolidation worktree contains exactly two intentional, unstaged files:

| File | SHA-256 at design start |
|---|---|
| `scripts/check-push-graph.mjs` | `32c0b5b4ec3fdf5083bc399c5525e11281d7f6301e86e5670840cca9bca1abef` |
| `scripts/check-push-graph.test.mjs` | `ce9e3a6d88e01a5d935212d848141d29f82aa282848f0d749d1427bd9b4a44b9` |

These two files are evidence-bearing work in progress. They may be captured in
a binary patch but must not be staged, committed, or pushed by this migration
checkpoint.

The G0 worktree contains 15 untracked files under
`docs/superpowers/plans/`. They must be archived and hash-verified, but they
must remain untracked and unpublished. The preparation and canon worktrees are
clean.

There are also 52 ignored local analysis/source files. Their `.gitignore`
policy identifies them as potentially containing credentials or detailed
server evidence. They must not enter Git, GitHub, the ordinary recovery
capsule, logs, or chat output. They require a separately encrypted offline
copy.

## 3. Publication-gate evidence and exception boundary

The full reachable-graph scanner returns exit `1` for both the currently
published consolidation branch and the local candidate branch. Each produces
the same 15 records and the same aggregate categories:

| Category | Aggregate count |
|---|---:|
| `absolute_user_path` | 7 |
| `credential_like` | 5 |
| `env_or_key_material` | 1 |
| `operational_identity` | 2 |
| `unscannable` | 1 |

A record-key comparison over `category`, `blob`, and repository path produced
`added_records=0` and `removed_records=0`. This proves only that the 11 local
commits add no scanner records relative to the already published branch. It is
not a general safety clearance, and it does not turn the formal gate green.

The operator explicitly authorized one private fast-forward publication
exception for `codex/aurelia-konsolidierung`. The exception is valid only when
all of these conditions remain true immediately before the push:

1. the live remote ref still equals
   `029bdcef62ccff35c0e964588e32a9727ea42470`;
2. the local ref is a strict descendant of that remote ref;
3. the full-graph record-key comparison still reports no added record;
4. the index contains only the separately approved documentation checkpoint
   before its commit and is empty before the push;
5. the two scanner files remain unstaged and retain their captured hashes;
6. no G0 untracked file or ignored analysis source enters the commit;
7. the push uses an explicit fast-forward refspec for
   `codex/aurelia-konsolidierung` only;
8. `main`, force-push, tags, other branches, server actions, and history rewrite
   remain forbidden.

Any failed condition stops publication. A new remote commit, added scanner
record, changed dirty-file hash, unexpected staged path, authentication error,
or non-fast-forward result invalidates the exception until reviewed.

### 3.1 Non-self-referential Task-3 preflight repair

The existing overlap-correction plan incorrectly requires an exact historical
`HEAD` even though committing that requirement necessarily advances `HEAD`.
The documentation implementation must remove that equality check and instead:

1. require `f1082f9d5a04ca32eaa8f79b1b9188e740622904` to be an ancestor of
   the active `HEAD`;
2. require `73ea21ce8031714174d2b7cc922478a1dc0103af` to remain an ancestor;
3. retain the fixed branch, correction-design digest, empty-index, and exact
   two-file dirty-scope checks;
4. require the plan itself to have no worktree or index modification at
   implementation start.

This repair is documentation-only. It must not stage or modify either scanner
file, and it must not replace ancestry with a new exact-`HEAD` assertion.

## 4. Three-layer preservation architecture

### 4.1 Layer A: private GitHub committed state

GitHub preserves only committed, approved documentation and the existing
branch history. The final push must be a fast-forward update of
`refs/heads/codex/aurelia-konsolidierung` to the verified local documentation
checkpoint. GitHub is not the backup location for dirty scanner work, G0
untracked plans, ignored analyses, `.codex`, SSH material, or recovery codes.

### 4.2 Layer B: encrypted recovery capsule

The recovery capsule is created directly on an operator-provided encrypted
destination. No persistent plaintext capsule may be staged in the repository,
the Codex directory, or another internal workstation path. The destination's
encryption and unlocked state must be verified before generation begins.

The capsule remains confidential because its Git bundle contains the
scanner-flagged private history. The complete bundle is treated as sensitive;
the absence of real credentials must not be inferred from scanner category
names or from the unchanged record set. The capsule must not deliberately add
ignored analysis sources. Its required internal layout is:

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

The bundle captures all local branch refs. The binary patch captures only the
two dirty consolidation files against the documented base commit. The G0 TAR
preserves the 15 untracked relative paths. Inventories may contain repository
paths, hashes, counts, versions, and branch IDs, but never credential values,
remote credentials, file contents, raw server evidence, or private keys.

`SHA256SUMS.txt` covers every file in the capsule except itself. The README
records the final post-documentation commit as observed after the commit; this
post-commit manifest remains outside Git so it can truthfully name the commit
that already exists.

### 4.3 Layer C: encrypted offline cold backup

Before Windows is erased, the operator must place the verified recovery capsule
on two independent encrypted destinations, at least one of them offline. The
full repository directory, the 52 ignored analysis/source files, and the
following user state also require encrypted destinations:

- the closed-app copy of `%USERPROFILE%\.codex`;
- `%USERPROFILE%\.ssh` and any separately held recovery codes;
- user Git configuration and required editor settings;
- any project material intentionally kept outside Git.

The Codex directory is copied only after the Codex app and Codex CLI processes
are fully closed so its SQLite/WAL state is not captured mid-write. Existing
`auth.json`, tokens, browser sessions, and host credentials are rollback
material only; the Ubuntu installation must prefer fresh authentication and
token rotation rather than normal reuse. No password or recovery secret may be
placed in this repository or supplied in chat.

## 5. Capsule creation rules

Capsule generation is fail-closed:

1. verify that the selected destination is external to the repository and is
   encrypted before writing an artifact;
2. verify the expected branch, pre-design ancestry, exact dirty scope, empty
   index, and 15-file G0 untracked scope;
3. verify the two dirty-file hashes before capture;
4. create the Git bundle with all local refs directly on the encrypted
   destination;
5. create the binary consolidation patch without staging files;
6. create the G0 archive from an explicit, sorted file list;
7. classify the patch and each TAR member fail-closed while emitting only
   categories, repository-relative paths, and counts; never emit matched
   values;
8. treat the complete Git bundle as sensitive regardless of its record counts;
9. create sanitized inventories without reading secret values into output;
10. generate SHA-256 checksums;
11. reject any capsule file outside the declared layout;
12. scan filenames and text inventories for forbidden secret-bearing source
    paths or credential values;
13. confirm that no capsule artifact is tracked or staged in any worktree.

The capsule is a transport and recovery artifact, not a new source of truth.
The canonical committed state remains Git; dirty and untracked states remain
explicit overlays with documented bases.

## 6. Independent restoration proof

The proof must run from a capsule read back from one actual external encrypted
destination. Its dedicated test root must itself be on that encrypted medium or
on a separately verified encrypted temporary volume outside every current
worktree. No bundle, patch, extracted TAR member, restored Git object, or
worktree may be copied to an unencrypted internal path. The evidence records a
non-secret medium label, the capsule-manifest SHA-256, and the result. The proof
must not use an existing checkout, linked-worktree metadata, Git object
alternates, or the original repository as an object source after the capsule
has been read from the external destination.

The proof performs these checks in order:

1. verify `SHA256SUMS.txt` before using capsule artifacts;
2. initialize a new bare verification repository and run `git bundle verify`
   from that explicit repository context;
3. fetch `refs/heads/*` from the bundle into a separate new bare restore
   repository using an explicit refspec;
4. run `git fsck --full` in the bare restored repository;
5. compare all local branch heads with the inventory;
6. create four explicitly named worktrees for preparation, G0, canon, and
   consolidation from the bare restored repository using `git worktree add`;
7. run `git apply --check` and then apply the K1 binary patch in the restored
   consolidation worktree;
8. extract the G0 TAR into the restored G0 worktree;
9. compare the two scanner hashes and all 15 G0 file hashes with the inventory;
10. verify the expected restored status: preparation clean, canon clean, G0
    with exactly 15 untracked files, and consolidation with exactly the two
    modified scanner files;
11. confirm no case collision, symlink surprise, unexpected executable-mode
    change, or additional untracked file;
12. verify the second encrypted external copy against the same manifest;
13. delete the temporary proof directory only after its absolute location has
    been verified to lie inside the dedicated test root.

The proof does not execute `npm run build`, because that command includes a
database migration. Dependency installation and application gates belong to
the post-Ubuntu validation phase, where the environment can be explicitly
controlled.

## 7. Ubuntu restoration contract

The preferred workstation image is Ubuntu 24.04.4 LTS Desktop for amd64. The
restoration starts from GitHub after the private ref is verified, with the
bundle retained as the independent fallback.

The Ubuntu setup must:

1. install Git and recreate worktrees rather than copying Windows `.git`
   worktree pointers;
2. use `core.autocrlf=input` and verify LF for shell scripts;
3. preserve the tracked executable modes, including `startup.sh`;
4. initially reproduce Node.js `22.22.0` and npm `11.18.0` until the project
   explicitly pins a different toolchain;
5. install Codex CLI from the official Linux distribution and authenticate
   afresh;
6. restore only reviewed user configuration, skills, rules, and project
   instructions from the encrypted cold copy;
7. run `npm ci`, `npm run typecheck`, the focused scanner tests, the project
   test suite, and K1 controls;
8. run any build containing database migration only with a deliberately safe
   test database and explicit authorization.

Windows-to-Linux line-ending or file-mode changes must not be normalized inside
the evidence-bearing dirty scanner overlay. Any unexpected diff stops the
restore and is diagnosed before development resumes.

## 8. Acceptance and erase gate

The workstation may be considered migration-ready only when all of the
following are evidenced:

- the documentation checkpoint contains only approved documentation;
- the recovery capsule checksum manifest verifies;
- the independent restore proof passes completely from a capsule read back
  from an actual encrypted external destination, with its complete test root
  remaining on verified encrypted storage;
- the GitHub remote ref equals the verified local committed checkpoint after a
  successful fast-forward push;
- two encrypted external copies have been checksum-verified and at least one
  has supplied the complete successful restore proof;
- the encrypted cold copy was made after Codex and related processes were
  closed;
- SSH/recovery material is available independently of the Windows disk;
- the operator explicitly confirms that the external backups are readable.

Only the operator may authorize erasing or repartitioning the Windows disk.
This design and any successful automated checks do not constitute that final
destructive-action authorization.

## 9. Stop conditions

Stop without improvisation if any checksum differs, a ref changes
unexpectedly, the remote is no longer the documented ancestor, GitHub asks for
a force update, a credential value appears in generated output, the dirty or
untracked scope changes, the recovery proof depends on the original object
database, any capsule or restore artifact would be written to unencrypted
storage, or an external backup cannot be read back.

No workaround may weaken these conditions. The next action is diagnosis and a
new explicit decision, not publication or disk erasure.
