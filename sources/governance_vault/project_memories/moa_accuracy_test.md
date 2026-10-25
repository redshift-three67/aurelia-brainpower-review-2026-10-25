# MoA Accuracy Test: Async File-Read Race

Date: 2026-09-10

## Deliberate Trap

`tests-js/async-race-condition.test.ts` initially started two `writeFile()` operations and a `readFile()` operation against the same temporary JSON file without ordering or synchronization. It then asserted that the in-flight read must return the second revision.

The focused run exposed the flaw: the read observed a partially written JSON document and failed with `SyntaxError: Unterminated string in JSON`. Other possible outcomes included a missing file, the first revision, or the second revision. The assertion did not describe a valid filesystem contract.

## Correction

The test now uses real temporary files but explicitly awaits each write before reading:

1. write and read revision 1;
2. write and read revision 2;
3. assert that each read equals the complete revision written immediately before it.

This validates asynchronous file reads without a timing-dependent interleaving or an unsupported atomicity assumption.

## Supervisor Delegation Status

A supervisor delegation was requested with GPT-6.0 Astra, but the runtime could not create a delegate: its configured `openai` delegation provider is unknown. `hermes doctor` confirmed the configuration issue. No GPT-6.0 Astra review was executed, and this note does not attribute the correction to that unavailable supervisor.

The deterministic correction was applied locally after the focused race reproduction.

## Verification

- Deliberate version: failed as expected with an unterminated JSON parse caused by the unprotected overlap.
- Corrected focused test: 1 file / 1 test passed.
- `npm run --workspace tests-js check`: typecheck, 12 Vitest files / 70 tests, and ESLint all passed.
