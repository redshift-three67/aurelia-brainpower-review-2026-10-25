# Local AI Explicit Opt-in Design

**Date:** 2026-07-30
**Status:** User-approved design; implementation not started
**Roadmap position:** Gate-1 acceptance remediation with a deliberately limited
Gate-7 vertical slice

## Problem

The Workbench currently says that local AI is not selectable and that Gate 7
will add an explicit opt-in. The productive Top-N scan nevertheless always
passes `--llm` to `tools.interpretation_generator`. That tool attempts local
Ollama and falls back to rule-based text when Ollama is unavailable.

The current implementation has two truth defects:

1. Users cannot withhold the local Ollama attempt for a productive scan.
2. A rule-based fallback after `--llm` can be labelled as generated AI text and
   can retain an Ollama-only note.

The user chose to introduce explicit opt-in now rather than merely document the
automatic behavior until Gate 7.

## Goals

- Local AI is off by default for Web and direct CLI scans.
- Every productive local Ollama attempt requires an explicit per-case opt-in.
- Preview and start use the same opt-in value and start-operation identity.
- Ollama is limited to a fixed loopback production origin and a pinned model.
- Missing service, missing model, timeout, empty response, or client error falls
  back safely to rule-based interpretation.
- Reports state whether local Ollama was actually used.
- Fallback text is never labelled as model-generated output.
- Scores, source findings, profile selection, and Registry behavior remain
  unchanged.

## Non-goals

- Full Gate-7 report restructuring.
- Full post-LLM compliance pipeline and policy engine.
- PDF parity work.
- User-configurable model or origin.
- Cloud or non-loopback LLM providers.
- Persisting the opt-in in templates, browser storage, or client drafts.
- Changing EMF, Adaptive Limits, group activation, or scan-profile authority.

This slice does not constitute complete Gate-7 acceptance.

## Contract

### Web request

`Phase1ScanRequest` gains:

```python
local_ai_enabled: bool = Field(default=False, strict=True)
```

Requests from older clients remain valid and resolve to `false`. Non-boolean
values fail validation. The existing request serialization used by
start-operation reconciliation includes the field automatically, so changing
the opt-in changes payload identity and cannot reuse a conflicting operation
under the same idempotency key.

### Workbench control

Phase 5 gains one checkbox:

- ID: `local-ai-enabled`
- Name: `local_ai_enabled`
- Initial state: unchecked
- Accessible description: `local-ai-help`
- Reset behavior: a new case returns it to unchecked

The help text must state:

- Purpose: optionally request a local interpretation from Ollama.
- Default: off for every new case.
- Effect: when enabled, the interpretation report may use the pinned local
  model after the scan.
- No effect: no score, profile-pool, source, or Registry calculation changes.
- Boundary: loopback only; unavailable or rejected Ollama falls back to
  rule-based interpretation and is labelled as fallback.
- Persistence: the opt-in is not retained for the next case.

The review card displays `Lokale KI: aus` or `Lokale KI: aktiviert`. Preview and
start serialize the same boolean.

### Web launcher and direct CLI

`build_phase1_scan_launcher()` appends `--local-ai` only when
`request.local_ai_enabled` is true.

`scan top3-scan` gains:

```text
--local-ai / --no-local-ai
```

The default is `--no-local-ai`. The interpretation-generator subprocess gets
`--llm` only when the CLI option is true. The direct CLI therefore adopts the
same explicit-opt-in default as the Workbench.

### Ollama boundary

The productive interpretation path uses constants for:

- Origin: `http://127.0.0.1:11434`
- Model: `phi3:latest`

The reusable client may accept a loopback URL for isolated tests, but rejects
non-loopback hostnames, non-HTTP schemes, credentials, query strings, and
fragments. Production does not expose origin or model selection through Web or
CLI in this slice.

Availability succeeds only when the pinned model is present. The client must
not replace it with the first installed model.

## Interpretation Outcome

Interpretation generation uses one explicit outcome object with:

- `text`
- `mode`: `disabled`, `ollama`, or `rule_fallback`
- `model`: pinned model only when actually used
- `reason`: safe reason code for fallback, not raw exception text

Expected states:

| Opt-in | Ollama result | Mode | Report truth |
|---|---|---|---|
| false | not contacted | `disabled` | Local AI disabled; rule-based interpretation |
| true | valid non-empty text | `ollama` | Local Ollama used with pinned model |
| true | unavailable/missing/timeout/error/empty | `rule_fallback` | Opt-in requested, Ollama not used; rule-based fallback |

Top findings are collected once. Rule-based interpretation remains substantive
in both `disabled` and `rule_fallback` modes.

Raw exception messages, prompts, and model responses are not copied into status
metadata or logs by this slice. Existing HTML escaping remains mandatory.

## Report Rendering

The report no longer uses an unconditional `KI-gestuetzte Tiefenanalyse`
heading or Ollama note. It renders a neutral `Deutung` section plus an explicit
source/provenance line derived from the outcome.

Only `mode=ollama` may render an Ollama-generated note and active model
metadata. `disabled` and `rule_fallback` must identify rule-based content.

The existing wellbeing block and diagnosis boundary remain. This slice does not
claim to implement the complete future post-LLM compliance gate.

## Error Handling

- No opt-in: no Ollama client construction and no request to port 11434.
- Unavailable service: rule-based fallback.
- Pinned model absent: rule-based fallback; no model substitution.
- Timeout or empty response: rule-based fallback.
- Unexpected client exception: rule-based fallback with a safe reason code.
- Invalid non-loopback origin in direct client construction: fail closed before
  network access.
- Scan and report creation continue unless the existing report-tool contract
  independently treats report generation as failed.

## File Responsibilities

| File | Responsibility |
|---|---|
| `apps/web/contracts.py` | Strict request field and default |
| `apps/web/static/index.html` | Checkbox and truthful accessible help |
| `apps/web/static/app.js` | Payload and new-case reset behavior |
| `apps/web/static/workbench-render.js` | Review-card truth |
| `apps/web/launcher.py` | Conditional CLI flag |
| `apps/cli/commands/scan.py` | CLI option and conditional `--llm` subprocess flag |
| `core/llm/ollama_client.py` | Loopback validation and pinned-model fail-closed behavior |
| `tools/interpretation_generator.py` | Outcome/provenance and truthful report rendering |
| focused Python/Node/Browser tests | RED/GREEN and acceptance contracts |

No new runtime service or persistence store is required.

## Test Strategy

### Contract and launcher

- Missing `local_ai_enabled` defaults to false.
- Literal true/false are accepted; coercive values are rejected.
- Launcher omits `--local-ai` by default.
- Launcher adds exactly one `--local-ai` for opt-in.
- Preview and start preserve the same boolean.

### CLI and interpretation

- Direct CLI default omits `--llm` from the report subprocess.
- Direct CLI opt-in adds `--llm` exactly once.
- Disabled mode never constructs or calls Ollama.
- Real mocked model output produces `mode=ollama` and model provenance.
- Unavailable, missing-model, timeout, exception, and empty-result cases produce
  rule-based fallback and never claim generated AI text.

### Client security

- Loopback HTTP origins are accepted for isolated tests.
- External hostname, HTTPS/non-HTTP scheme, credentials, query, and fragment are
  rejected before network access.
- Pinned model missing does not select another installed model.

### Frontend and browser

- Checkbox is unchecked and ARIA-linked on initial load.
- Payload and review card agree for off and on.
- Preview and start receive the selected value.
- New Case resets the checkbox to off.
- Desktop and mobile layouts have no horizontal overflow.

### Final acceptance

1. Focused Python, Node, and browser tests.
2. Full Python suite.
3. Full isolated browser matrix.
4. JavaScript syntax, Python compile, and diff checks.
5. Process, temporary-runtime, port, and Git-index cleanup checks.
6. Scope-bound SHA-256 freeze.
7. Independent specification and quality/security reviews.

No commit, staging, push, reset, or unrelated worktree cleanup occurs without
explicit user approval.
