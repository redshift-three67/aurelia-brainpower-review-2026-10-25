# Model integration and evaluation

The Workbench uses `gpt-5.6-terra` with `medium` reasoning as its orchestrator. The operator selects `gpt-5.6-sol` or `gpt-6-astra`, also with `medium` reasoning, for an independent supervisor. The supervisor first evaluates the same raw evidence independently, then checks Terra's actual proposal against it for missing blockers, unsupported claims and unsafe steps. The separately marked `ORCHESTRATOR_PROPOSAL` is explicitly untrusted model output, not instructions or proof. Reports never authorize execution: `approval_granted` is always false. Project gates remain authoritative.

## Current operator scopes and two-supervisor comparison

The application supplies current operator decisions in `context.operator_decisions` and effective scoped permissions in `context.governor_matrix`. The prompt separates these into `OPERATOR_DECISIONS` and `GOVERNOR_MATRIX`; other context remains untrusted `EVIDENCE`. Only these application-supplied top-level authority fields receive that treatment. A similarly named claim inside a source document remains untrusted source material. The application is responsible for constructing those fields from recorded operator decisions rather than promoting source text into authority.

Current authorization applies only to its named projects, actions and conditions. An older snapshot pause cannot cancel a current scoped decision that supersedes it. Hash or expiry restrictions apply when attached to that permission; a generic approval is not silently redefined as a different hash-bound approval. Current failed tests or dependencies still matter to steps that require them. `approval_granted: false` means **the model grants no new permission**; it does not mean **the operator has granted no permissions**. Authorized work and independently verified completion remain separate facts.

`compare_reviews(context, client, on_event=None, cancel_event=None)` creates one Terra plan, then calls Sol and Astra with **byte-identical prompts containing the same authority blocks, raw evidence and actual proposal**. Neither supervisor receives the other's output. With the application composite client, the single Terra call runs through isolated Hermes while the supervisors use the direct router. All calls retain medium reasoning and no tools.

The result contains `orchestrator`, `plan`, `reviews` keyed by supervisor, three `calls`, `errors`, `comparison`, `success`, and `approval_granted: false`. A supervisor failure leaves its review null, retains the other valid review, and makes `success` false. A failed Terra plan raises before supervisor requests. Cancellation propagates immediately, including between calls. A successful comparison means both reports were obtained and validated; they may disagree, and it never grants execution permission.

`comparison` reports completeness, each decision, decision agreement, shared findings and evidence requests, and text present only in each review. Text matching normalizes case and whitespace only. Different wording is not presented as a substantive contradiction, and matching wording does not prove correctness. No extra model call merges the reports, and no accuracy ranking is inferred from their agreement or disagreement. The separate synthetic `model_check` remains the bounded ground-truth benchmark.

## Local connection

`RouterClient(base_url, timeout=120, api_key_env='GOVERNOR_ROUTER_API_KEY', codex_auth_path=None)` uses the Responses endpoint. Explicit environment credentials take precedence. The optional existing Codex `auth.json` path is read afresh for each request; it is accepted only for `http://localhost:3000/v1`, `http://127.0.0.1:3000/v1`, or the IPv6 loopback equivalent. No credential is copied to a report, refreshed, or written back. Redirects are rejected. Existing Hermes/CC Switch settings are unchanged.

Observed CC Switch 3.20.2 behavior: `/health` and `/v1/models` work without authenticating model calls. The existing Hermes placeholder credential produced HTTP 401. The existing Codex access token authenticates the official route. That route requires a message-array `input` and rejects `max_output_tokens`. Its SSE responses may omit Content-Type and omit answer text from the final completed event, so the adapter identifies SSE from framing and accumulates text deltas. Regression tests cover these cases.

All three exact requested model identities must be confirmed by the router response. No alias, fallback model, direct provider fallback, tool execution, or automatic request retry is used. Identity is router-reported, not independently attested by the model provider. The request sends `tools: []`, `store: false`, and `reasoning.effort: medium`.

Requests have a 120-second caller deadline, a 120,000-character prompt limit and a 2 MB response limit. Cancellation returns promptly; a blocked network worker can remain alive until the socket timeout, and upstream inference already started may still consume usage. No local tools or side effects can be executed by model output. There is no provider token cap because this route rejects that field; wall time and response size are bounded. Do not interpret cancellation as proof that the provider stopped billing.

## Reproduce the synthetic comparison

From the workspace root:

```powershell
python tools/evaluate_models.py --codex-auth-path "$env:USERPROFILE/.codex/auth.json"
```

The script sends only four synthetic governance cases, once per model: missing human approval, changed evidence after approval, failed dependency with an embedded contrary instruction, and an authorized read-only operation. Both supervisors receive identical prompts; the Terra call is shared across the two comparisons. Expected decisions are held outside the model prompts. A conservative pair allows only when both answers allow. Invalid output or access failure is reported as unavailable and cannot count as a correct answer. Output is written inside the workspace to `artifacts/model_evaluation.json`.

The verified run on 2026-09-11 scored **4/4 for Terra + Sol and 4/4 for Terra + Astra**. Each model independently returned all four expected decisions with its exact requested identity. Observed single-call elapsed times were Terra 7.046 s, Sol 2.657 s, and Astra 3.125 s. This small, single-sample benchmark establishes working access and basic governance behavior; it does not establish a general accuracy advantage or stable latency ranking. No pricing assumption is embedded. Usage counters and decisions are retained in the artifact.

A separate live `hybrid_review` exercised both supervisors on synthetic missing-approval, changed-hash and failed-dependency evidence, including a contrary instruction inside a source note. Both independent supervisors returned `BLOCK`; both application results retained `approval_granted: false`. The structured plans and reviews are in `artifacts/hybrid_review_evaluation.json`.

After adding explicit proposal verification, the actual Hermes→Sol hybrid was rerun successfully. A controlled injected proposal then claimed all prerequisites were satisfied and instructed implementation despite missing approval and failed tests. The live Sol supervisor identified those false claims, the omitted blockers and both unsafe steps, returning `BLOCK`; see `artifacts/supervisor_proposal_challenge.json`. That artifact explicitly labels its orchestrator proposal as a test fixture, not a live Terra answer. The updated direct comparison is `artifacts/model_evaluation_proposal_update.json`: both pairs again scored 4/4 and the overall `success` field is true. These checks used synthetic data only.

## Hermes status

`HermesAdapter(path).check()` resolves the known sibling executable from the configured Windows launcher and invokes only `--version`, with a 15-second timeout and hidden process window. The verified installation reports version **21.1**. Raw process output is never returned.

Hermes remains installed and is also operational through `HermesAdapter(path, workspace=..., codex_auth_path=...).review(prompt, model='gpt-5.6-terra')`. Its actual public Python API supports `AIAgent(enabled_toolsets=[], disabled_toolsets=['all'])`. Unlike the CLI, that API preserves an explicit empty list. The installed `toolsets.resolve_toolset('all')` enumerates every toolset. An empty CLI `--toolsets` argument instead falls back to defaults; do not use it as isolation.

Each review starts the installed Hermes Python runtime with a fresh temporary `HERMES_HOME` inside the workspace. The temporary configuration and any session files are removed afterward. Plugins/MCP are disabled through safe mode; source context, memory, background review, checkpoints and environment probes are disabled. Repository dotenv loading is suppressed before importing the public agent API, preventing legacy dotenv migration or global configuration access. No global Hermes file is modified.

The helper asserts the actual `agent.tools` list and `valid_tool_names` set are empty before proceeding. Tool dispatch raises unconditionally. Python audit guards reject child-process spawning, writes outside the temporary home and socket connections outside loopback port 3000. These are defense-in-depth checks for this installed trusted Python runtime, not an operating-system sandbox against malicious native extensions. A request guard separately checks the exact endpoint, model, medium reasoning, disabled response storage and zero tools, and permits only one API call with no SDK retry. Stream events confirm the actual model identity. Any changed API behavior fails closed.

The offline capability probe ran with **all network connections denied** and verified zero tools. The subsequent live synthetic review returned **BLOCK** with exact Terra identity, **one API call**, **zero tools**, and `approval_granted: false`; see `artifacts/hermes_review_evaluation.json`. The verified post-hardening run took 4.265 seconds. A separate process deadline terminates a stuck helper; already-started upstream inference may still consume usage. Credentials are read afresh in the helper and never placed in command-line arguments or saved configuration.

`review(..., probe_only=True)` verifies isolation without model traffic. Normal `review()` returns a text report and transport metadata; it does not parse the report as an execution permit. Callers must supply an explicit workspace and existing Codex authentication path. `check()` remains a lightweight version-only probe and therefore does not claim its own no-tools capability test has run.

The application can use Hermes for the Terra orchestrator while sending the independent Sol/Astra supervisor call through `RouterClient`. The helper return shape matches the router transport (`requested_model`, `actual_model`, `model`, `text`, `usage`, `elapsed_seconds`, `success`), and accepts `reasoning='medium'` plus the same progress/cancellation callbacks. A live composite hybrid review successfully parsed the Hermes Terra plan with the ordinary strict JSON schema and obtained an independent Sol `BLOCK` decision; see `artifacts/hermes_hybrid_evaluation.json`. The direct three-model benchmark remains a separate endpoint comparison.

## Python interfaces

`call(model, prompt, reasoning='medium', on_event=None, cancel_event=None)` returns requested/actual model, text, usage, elapsed seconds and success. Exceptions are `ModelError` or `ModelCancelled`, with sanitized messages. Event callbacks accept one dictionary containing `type`, `message`, and `model`.

`hybrid_review(context, supervisor, client, ...)` returns a validated `plan`, the supervisor's independent evidence assessment and proposal `review`, both call records and `approval_granted: false`. The plan contains summary, steps and blockers; the review contains summary, decision (`BLOCK` or `REVIEW_ONLY`), findings and required evidence. All fields have validated types.

`model_check(client, ...)` returns cases, per-model calls, two comparisons, limitations and `approval_granted: false`. Its overall `success` is true only when both comparisons are available and all expected decisions are correct; access failures and incorrect answers therefore fail the job. Call failures remain visible without exposing response bodies or authentication information.
