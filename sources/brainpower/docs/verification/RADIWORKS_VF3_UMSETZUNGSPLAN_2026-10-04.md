# RadiWorks VF3 Implementation Plan

> For agentic workers: use subagent-driven-development for the bounded pure helper; root integration and independent Astra spec/quality review. Approved VF3 continuation, no live rollout.

**Goal:** Explainable focus/topic catalog suggestions with explicit user selection, preserving manual search and original analysis.
**Architecture:** Fresh109-file manifest copy of VF2-B at runtime/rw-vf3-20261004. Pure lexical helper ranks exact database documents. Root adds bounded double-read catalog snapshot and two read-only POST routes; separate browser controller obtains context/query and confirms a current suggestion before selecting an exact .txt database. Original request/algorithms unchanged.
**Tech Stack:** Existing stdlib Python/FastAPI/Pydantic and vanilla JS/CSS, existing Chrome/Playwright testing; no new model/decoder/runtime dependency.

## Approved design and alternatives
Existing name-only search remains stable. Recommended additive focus/topic suggestions include names, fixed existing groups and allowed rate names, showing matched words and matching line count. Identity/image excluded. Semantics/embeddings and automatic selection rejected per operator directive. No medical suitability score, effectiveness promise or automatic analysis. Deterministic ordering: coverage, name matches, group matches, content matches then stable name; repeated rates do not inflate term coverage. Unicode NFKD/casefold, words >=3 characters, no numeric tokens; at most12 distinct meaningful query words, otherwise controlled422. No silent truncation.

Source limits: <=2048 database files, <=2MiB per file, <=32MiB total, <=250000 lines. Out-of-bounds/unavailable/drift return controlled errors, no partial result. Exact indexed .txt source paths only, no user supplied filesystem path, no symlink/junction escape. Content is read-only, copied in bounded memory; verify original pinned release or legacy second read and same inventory. Full catalog digest is point-in-time provenance, not future execution lease.

POST /database-suggestions accepts strict topics<=240,use_focus boolean,expected_case_ref/version,limit1..8. Focus read from saved active case only; missing required binding or changed context =>409. No personal identity echoed. CopyGuard blocks unsafe query and excludes unsafe database/line text from visible evidence. Response ruleVersion,queryTerms,totalMatches,suggestions,catalogSnapshotDigest,caseRef/contextVersion.
POST /database-suggestions/confirm repeats same bounded source/query/context checks with expected catalog digest and exactselector .txt; drift =>409. Return selector/name only after valid match; no cases/entropy/sessions/queues/files modified.
Browser new optional topic field and explicit suggest button. Existing focus-name button/manual search retained. Each suggestion explains name/group/rate matches without raw rate excerpt. User must press 'Datenbank wählen'; confirmation changes only selector, preserving current result/session/broadcast. Async revision/abort prevents stale focus/case/query response or later confirmation overwriting newer selection. No query in localStorage/logs/URL. Zero model calls.

## Tasks and ownership
- [x] Root verify/copy109parent files; read-only protected listener baseline, no Git/global home mutation.
- [x] Luna bounded interface consultation; root took ownership of helper/tests after no code delivery. Root implemented pure helper with26 RED/GREEN cases; no filesystem/network/entropy/recursive delegation.
- [x] Root RED engine/tests/test_database_suggestions.py against absent API: exact names/contents, no-state effects, context/scope/drift/limits/blocked projection.
- [x] Root engine/src/radiworks/core/catalog_suggestion_sources.py: strict source quotas, double-read, digest, safe indexed path guards.
- [x] Root engine/src/radiworks/api/routes.py: strict requests, capture context under existing transaction lock, compute read-only, recheck binding before response and confirmation; retain all original routes.
- [x] Root webapp/js/views/catalog_suggestions.js plus api.js/index.html/additive CSS and narrow analyze.js hooks. Bound real Chrome control RED against parent HTML then GREEN real actions; first startup diagnostic is not counted as feature RED; selected exact filename remains visible after manual filtering/reload. No automatic analysis.
- [x] Root full engine and bound browser regression, syntax, desktop/320px keyboard, error/retry/staleresponse/confirmation/catalogdrift/casechange probes; parent109/VF2A105/GV2103/core/ref and8103–8110 checks.
- [x] Astra read-only spec and quality review of query/privacy/source binding/async guards. Fix concrete findings with RED/GREEN. No release authority.
- [x] Root product manifest/diff/report/template delta/current Wiedereinstieg, local timestamp checkpoint withSHA readback. No real homes/keys/assets/F backup/Windows package yet.

## Commands
Engine: explicit PYTHONPATH=candidate/engine/src; existing RadiWorks engine/.venv/Scripts/python.exe -m pytest -q --basetemp=../test-temp/vf3 --junitxml=../engine-final.xml.
Browser: NODE_PATH=.../.agents/skills/playwright/node_modules, RW_ENGINE_DIR=this candidate engine, RW_SMOKE_PYTHON=existingvenv, RW_SMOKE_TMP_ROOT=this candidate/test-temp; node vf3_browser.mjs asserts loaded engine __file__, owns ephemeral loopback/home/cleanup.
Missing POST route must return404 where newtests expect200 (RED). Helper boundary tests fail before helper addition; same failures pass only after minimal implementation.
No commits/worktree against user-home Git repository: approved pinned runtime isolation and bounded code checkpoint preserve unrelated WIP and external originals.

## Completion boundary
VF3 is a local candidate feature, not clinical validation or production readiness. Legacy focus revisions, personal data and current source matching checked; no guarantee against malicious filesystem ABA by full-control attacker. Original names/prefix path remains unchanged; newly confirmed suggestions are exact .txt choices. EXP1, longtrend/camera/recovery/Area/Peggotty, operator acceptance, canonical/templates, Win10 package/F fullbackup and S4.8 remain separate.

## Verified compatibility corrections during implementation
Astra P2 found nonselected release-script/FUNCTION byte changes were not checked. Release snapshots now hash/double-read all entries within the same per-file/total bounds; selectable rate lines retain their own line quota.
Real read-only catalog probe found non-UTF8 bytes in original AetherOne data. VF3 uses the existing RateRepository UTF8 errors=replace rule, hashes original bytes and exposes an explicit replacement file-count warning; no silent encoding guess or source rewrite. Strict UTF8 rejection would incorrectly disable suggestions on the current original catalog. Standalone synthetic RED/GREEN probes capture both corrections.
