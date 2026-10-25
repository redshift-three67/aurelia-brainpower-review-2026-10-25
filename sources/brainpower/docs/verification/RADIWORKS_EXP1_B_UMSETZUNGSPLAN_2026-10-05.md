# RadiWorks EXP1-B Implementation Plan — 05.10.2026

> For agentic workers: subagent-driven-development for bounded pure formula input; root owns context/API/UI integration, Astra independent boundary review. Operator approved optional exclusive residence/birth choice and context-only image. No new approval gate or live rollout.

**Goal:** Unambiguous single active place type, backwards-compatible saved context and exact existing Radi144 name/birth preparation, without original numeric changes.
**Architecture:** Pinned114-file VF3 copy runtime/rw-exp1b-20261005; optional personalContext.placeKind residence|birth, omitted means legacy unknown. One place value; no hidden second place. UI change clears value pending save, meaningful label and help. Explicit type travels in immutable snapshot; old snapshot bytes/digests remain valid. Pure preparer validates snapshot then ports only existing scalar formulas, omits clock and numeric image per approved profile. It does not rank, consume entropy, create a session, issue broadcasts or select a mode.
**Tech Stack:** Existing Python>=3.12 stdlib/FastAPI and vanillaJS/CSS; no new Torch/NumPy or image decoder dependency for this package.

## Contract
normalize_personal recognizes placeKind only when explicitly present, accepts exactly residence or birth; nullable/nonstring/unknown invalid. Legacy omission keeps old shape, so old context snapshots continue to validate unchanged. Typing a formerly untyped place is explicit user input. One active place only, no stored inactive place fields. Server patch/type changes must include place in the same explicit patch, or reject409/422 without mutation; no reinterpreting a previous value. Full replacement may choose type/place together. API full-case existing saves likewise require explicit paired place on type transition.

UI select: new blank form defaults residence; existing untyped saved case shows disabled empty option 'Bisheriger Ort: Typ nicht festgelegt'. Selecting residence/birth clears place input, updates label and focus, announces that re-entry+save are required. Case switch/reload rehydrates typed or legacy values; save lock covers select; patch includes placeKind and place together for type transition. Untyped case simple other edits preserve legacy shape. Old jobs/snapshots remain unchanged.

experimental_context.prepare_experimental_context(snapshot) -> deterministic dict: formulaVersion,sourceHashes,contextDigest,contextVersion,caseId,signature {frequency,components,weights},placeUse,imageUse,focusUse,parameters. Uses ContextSnapshot.from_payload; rejects invalid snapshot and no available name/date scalar component. Name present if firstName or lastName has text, use existing calculate_name_frequency(firstName or '', [lastName] if present else []) with0.15. Birth present if birthDate has text: JDN modulo1000*.6 plus placeMD5[:4]/65.535*.3 ONLY when placeKind==birth and place nonempty, no birthtime (0);0.20. Weightedmean divide by present weights. Organuhr/planetary/EMF/HRV disabled, image metadata/context only. No focus number added here: existing conditional database substring requires catalog in next package; report focusUse='requires-catalog-match'. Store sourceSha256 of exact Radi144 file in helper, matching pinnedreference. No implicit time/random/hardware inputs. Frequency is heuristic, no physical/medical quality guarantee. Unknown/residence place remains context only. No source-rate mutation or new formula mixture.

## Tasks
- [x] Root verify/copy114parent product files, no global Git or original/source task mutation; read-only port baseline.
- [x] Root write test_place_kind.py: strict kinds, legacy snapshot preserved, typed snapshot/version transitions, API paired patch enforcement, original numeric equality and frozen old jobs. Run expected RED before production edit.
- [x] Root personal_context.py optionalkind support and pairing API validation; preserve all original contracts.
- [x] Luna owns ONLY core/experimental_context.py and tests/test_experimental_context.py. Fresh bounded context; test RED before helper, source reference parity and deterministic/error branches. No recursion or other files.
- [x] Root index.html and js/case-personal.js labelled select/help/value-clear, no stale response/save loophole. Actual bound Chrome missingcontrol RED before production UI; then all36parent sections+place transition/reload/legacy/browser focus and narrowviewport checks.
- [x] Root full engine, JavaScript syntax, parent/source/reference hashes, protectedport/PID comparison. Failures investigated without weakening checks.
- [x] Astra independent spec then quality review; confirmed issues fixed with regression tests.
- [x] Root report/TemplateDelta/current WIED/codecheckpoint withSHAreadback. No canonical source/template copy or F backup/live takeover.

## Commands and completion
PYTHONPATH=candidate/engine/src; existing RadiWorksvenv python -m pytest tests/test_place_kind.py -q --junitxml=../place-red-or-green.xml; full suite python -m pytest --basetemp=../test-temp/full --junitxml=../engine-final.xml. Bound Chrome helper copied/adapted from VF3, verifies loaded_main.__file__ equals candidate and uses owned synthetichome+ephemeralport. Syntax node --check every19JS file.

No globalstage/commit/worktree: user-home Git has unrelated WIP; approved pinnedruntime isolation and bounded checkpoints instead. Existing114parentmanifest proves baseline, no costly full baseline rerun without a change. EXP1-A sourceprobe23PASS remains valid sourceevidence, not new target/runtime or ranking acceptance. This EXP1-B package becomes100% only after stated input/UI tests and independentreview; full matrix/ranking mode, sessions/comparison, operatorprobe remain later EXP1-C.

## Abschlusskorrekturen
Astra-Zeitbefund behoben: SnapshotdatumUTC+1 konservative Zeitzonentoleranz ohne aktuellen Uhrzugriff, Intake unverändert;5 Regressionfälle. Kennzeichnung birth-scalar erfordert auch Geburtsdatum. Final585PASS/3Skip,41Browser/19JS/8Originalquellenproben;34neueTests. Vollständige EXP1-Matrix folgt separat.
