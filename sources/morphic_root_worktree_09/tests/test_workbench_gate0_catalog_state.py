from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"
API_JS = ROOT / "apps" / "web" / "static" / "workbench-api.js"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


def _run_node(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_workbench_api_aborts_hanging_reads_after_bounded_timeout() -> None:
    script = f"""
const fs = require("fs");
const vm = require("vm");
global.window = {{MORPHIC_REQUEST_TIMEOUT_MS: 5}};
global.fetch = async (_url, options = {{}}) => new Promise((_resolve, reject) => {{
  if (options.signal) {{
    options.signal.addEventListener("abort", () => {{
      const error = new Error("aborted");
      error.name = "AbortError";
      reject(error);
    }}, {{once: true}});
  }}
}});
vm.runInThisContext(fs.readFileSync({str(API_JS)!r}, "utf8"));
(async () => {{
  const outcome = await Promise.race([
    window.MorphicWorkbenchApi.loadRegistry().then(
      () => "resolved",
      error => error?.code || error?.name || "rejected"
    ),
    new Promise(resolve => setTimeout(() => resolve("hung"), 40)),
  ]);
  if (outcome !== "request_timeout") {{
    throw new Error(`expected request_timeout, got ${{outcome}}`);
  }}
}})().catch((error) => {{ console.error(error); process.exit(1); }});
"""

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


def test_workbench_api_does_not_abort_dispatched_mutations_without_reconciliation() -> None:
    script = """
const fs = require("fs");
const vm = require("vm");
let observedSignal = "not-called";
global.window = {MorphicWorkbenchState: {pendingMutations: 0, resetInProgress: false}};
global.document = {querySelector() { return null; }};
global.fetch = async (_url, options = {}) => {
  observedSignal = options.signal;
  return {ok: true, status: 200, async json() { return {saved: true}; }};
};
vm.runInThisContext(fs.readFileSync(__API_JS__, "utf8"));
(async () => {
  await window.MorphicWorkbenchApi.saveDraft({draft: {}});
  if (observedSignal !== undefined) {
    throw new Error("Mutation erhielt ohne Reconciliation eine clientseitige Abort-Autorität");
  }
})().catch((error) => { console.error(error); process.exit(1); });
""".replace("__API_JS__", repr(str(API_JS)))

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


def test_harmonization_start_has_no_ambiguous_timeout_while_scan_paths_keep_fifteen_seconds() -> None:
    script = """
const fs = require("fs");
const vm = require("vm");
const requests = [];
const timeoutDelays = [];
global.window = {MorphicWorkbenchState: {pendingMutations: 0, resetInProgress: false}};
global.document = {querySelector() { return null; }};
global.AbortSignal = {
  timeout(delay) {
    timeoutDelays.push(delay);
    return {addEventListener() {}, removeEventListener() {}};
  },
};
global.fetch = async (url, options = {}) => {
  requests.push({url, options});
  return {ok: true, status: 200, async json() { return {ok: true}; }};
};
vm.runInThisContext(fs.readFileSync(__API_JS__, "utf8"));
(async () => {
  const operationKey = "valid-operation-key-12345678";
  await window.MorphicWorkbenchApi.startHarmonization({job: "harm"}, operationKey);
  await window.MorphicWorkbenchApi.startScanJob({job: "scan"}, operationKey);
  await window.MorphicWorkbenchApi.reconcileScanStartOperation(operationKey);
  if (requests.length !== 3) throw new Error(`unexpected request count ${requests.length}`);
  const [harmonization, scanStart, scanReconcile] = requests;
  if (harmonization.url !== "/api/harmonization/jobs" || harmonization.options.signal !== undefined) {
    throw new Error("harmonization start received ambiguous timeout/AbortSignal authority");
  }
  if (!scanStart.options.signal || !scanReconcile.options.signal) {
    throw new Error("scan start/reconcile lost their bounded AbortSignal");
  }
  if (timeoutDelays.length !== 2 || timeoutDelays.some(delay => delay !== 15000)) {
    throw new Error(`scan timeout contract changed: ${JSON.stringify(timeoutDelays)}`);
  }
  if (requests.some(({options}) => "ambiguousTimeoutMs" in options)) {
    throw new Error("internal ambiguous timeout option leaked to fetch");
  }
})().catch((error) => { console.error(error); process.exit(1); });
""".replace("__API_JS__", repr(str(API_JS)))

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


def test_scan_start_timeout_is_bounded_and_releases_mutation_state() -> None:
    script = """
const fs = require("fs");
const vm = require("vm");
const reset = {disabled: false};
let observedOptions = null;
global.window = {
  MORPHIC_SCAN_START_TIMEOUT_MS: 5,
  MorphicWorkbenchState: {pendingMutations: 0, resetInProgress: false},
};
global.document = {querySelector(selector) { return selector === "#new-case-button" ? reset : null; }};
global.fetch = async (_url, options = {}) => new Promise((_resolve, reject) => {
  observedOptions = options;
  options.signal.addEventListener("abort", () => {
    const error = new Error("aborted");
    error.name = "AbortError";
    reject(error);
  }, {once: true});
});
vm.runInThisContext(fs.readFileSync(__API_JS__, "utf8"));
(async () => {
  const outcome = await Promise.race([
    window.MorphicWorkbenchApi.startScanJob({}, "scan-timeout-authority-12345678").then(
      () => "resolved",
      error => error?.code || error?.name || "rejected",
    ),
    new Promise(resolve => setTimeout(() => resolve("hung"), 50)),
  ]);
  if (outcome !== "request_timeout") throw new Error(`unexpected outcome ${outcome}`);
  if (!observedOptions?.signal) throw new Error("scan start had no bounded abort signal");
  if ("ambiguousTimeoutMs" in observedOptions) throw new Error("internal timeout option leaked to fetch");
  if (window.MorphicWorkbenchState.pendingMutations !== 0 || reset.disabled) {
    throw new Error(`mutation state leaked: ${window.MorphicWorkbenchState.pendingMutations}/${reset.disabled}`);
  }
})().catch((error) => { console.error(error); process.exit(1); });
""".replace("__API_JS__", repr(str(API_JS)))

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


def test_scan_reconciliation_is_bounded_and_has_no_request_body() -> None:
    script = """
const fs = require("fs");
const vm = require("vm");
let observedUrl = null;
let observedOptions = null;
global.window = {
  MORPHIC_SCAN_START_TIMEOUT_MS: 5,
  MorphicWorkbenchState: {pendingMutations: 0, resetInProgress: false},
};
global.document = {querySelector() { return null; }};
global.fetch = async (url, options = {}) => new Promise((_resolve, reject) => {
  observedUrl = url;
  observedOptions = options;
  options.signal.addEventListener("abort", () => {
    const error = new Error("aborted");
    error.name = "AbortError";
    reject(error);
  }, {once: true});
});
vm.runInThisContext(fs.readFileSync(__API_JS__, "utf8"));
(async () => {
  const key = "scan-reconcile-timeout-12345678";
  const outcome = await Promise.race([
    window.MorphicWorkbenchApi.reconcileScanStartOperation(key).then(
      () => "resolved",
      error => error?.code || error?.name || "rejected",
    ),
    new Promise(resolve => setTimeout(() => resolve("hung"), 50)),
  ]);
  if (outcome !== "request_timeout") throw new Error(`unexpected outcome ${outcome}`);
  if (observedUrl !== "/api/scan/start-operation/reconcile") {
    throw new Error(`unexpected URL ${observedUrl}`);
  }
  if (observedOptions?.method !== "POST" || observedOptions?.body !== undefined) {
    throw new Error(`reconcile request contract leaked a body: ${JSON.stringify(observedOptions)}`);
  }
  if (observedOptions?.headers?.["idempotency-key"] !== key || !observedOptions?.signal) {
    throw new Error("reconcile request lacked operation authority or timeout signal");
  }
  if (window.MorphicWorkbenchState.pendingMutations !== 0) {
    throw new Error(`pending mutation leaked: ${window.MorphicWorkbenchState.pendingMutations}`);
  }
})().catch((error) => { console.error(error); process.exit(1); });
""".replace("__API_JS__", repr(str(API_JS)))

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


def test_scan_start_uses_fifteen_second_default_ambiguous_timeout() -> None:
    script = """
const fs = require("fs");
const vm = require("vm");
let timeoutDelay = null;
global.window = {MorphicWorkbenchState: {pendingMutations: 0, resetInProgress: false}};
global.document = {querySelector() { return null; }};
global.AbortSignal = undefined;
global.setTimeout = (callback, delay) => {
  timeoutDelay = delay;
  queueMicrotask(callback);
  return 1;
};
global.clearTimeout = () => {};
global.fetch = async (_url, options = {}) => new Promise((_resolve, reject) => {
  options.signal.addEventListener("abort", () => {
    const error = new Error("aborted");
    error.name = "AbortError";
    reject(error);
  }, {once: true});
});
vm.runInThisContext(fs.readFileSync(__API_JS__, "utf8"));
(async () => {
  const outcome = await window.MorphicWorkbenchApi.startScanJob(
    {}, "scan-default-timeout-12345678"
  ).then(() => "resolved", error => error?.code);
  if (outcome !== "request_timeout") throw new Error(`unexpected outcome ${outcome}`);
  if (timeoutDelay !== 15000) throw new Error(`unexpected default timeout ${timeoutDelay}`);
})().catch((error) => { console.error(error); process.exit(1); });
""".replace("__API_JS__", repr(str(API_JS)))

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


def test_workbench_api_refuses_start_mutations_without_operation_authority() -> None:
    script = """
const fs = require("fs");
const vm = require("vm");
let fetchCalls = 0;
global.window = {MorphicWorkbenchState: {pendingMutations: 0, resetInProgress: false}};
global.document = {querySelector() { return null; }};
global.fetch = async () => { fetchCalls += 1; throw new Error("must not dispatch"); };
vm.runInThisContext(fs.readFileSync(__API_JS__, "utf8"));
(async () => {
  for (const invoke of [
    () => window.MorphicWorkbenchApi.startScanJob({}, null),
    () => window.MorphicWorkbenchApi.reconcileScanStartOperation(null),
    () => window.MorphicWorkbenchApi.startHarmonization({}, ""),
  ]) {
    let rejected = false;
    try { await invoke(); } catch (error) {
      rejected = String(error?.message || error).includes("operation authority");
    }
    if (!rejected) throw new Error("missing operation authority was accepted");
  }
  if (fetchCalls !== 0) throw new Error(`unexpected fetch calls: ${fetchCalls}`);
})().catch((error) => { console.error(error); process.exit(1); });
""".replace("__API_JS__", repr(str(API_JS)))

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


def test_workbench_api_classifies_timeout_during_response_body_read() -> None:
    script = """
const fs = require("fs");
const vm = require("vm");
global.window = {MORPHIC_REQUEST_TIMEOUT_MS: 5};
global.fetch = async (_url, options = {}) => ({
  ok: true,
  status: 200,
  json: async () => new Promise((_resolve, reject) => {
    options.signal.addEventListener("abort", () => {
      const error = new Error("body aborted");
      error.name = "AbortError";
      reject(error);
    }, {once: true});
  }),
});
vm.runInThisContext(fs.readFileSync(__API_JS__, "utf8"));
(async () => {
  const outcome = await Promise.race([
    requestJson("/body-timeout").then(
      () => "resolved",
      error => error?.code || error?.name || "rejected",
    ),
    new Promise(resolve => setTimeout(() => resolve("hung"), 40)),
  ]);
  if (outcome !== "request_timeout") {
    throw new Error(`expected request_timeout, got ${outcome}`);
  }
})().catch((error) => { console.error(error); process.exit(1); });
""".replace("__API_JS__", repr(str(API_JS)))

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


def test_workbench_api_propagates_upstream_abort_during_response_body_read() -> None:
    script = """
const fs = require("fs");
const vm = require("vm");
global.window = {MORPHIC_REQUEST_TIMEOUT_MS: 1000};
global.fetch = async (_url, options = {}) => ({
  ok: true,
  status: 200,
  json: async () => new Promise((_resolve, reject) => {
    options.signal.addEventListener("abort", () => {
      const error = new Error("body aborted");
      error.name = "AbortError";
      reject(error);
    }, {once: true});
  }),
});
vm.runInThisContext(fs.readFileSync(__API_JS__, "utf8"));
(async () => {
  const upstream = new AbortController();
  const pending = requestJson("/body-abort", {signal: upstream.signal}).then(
    () => "resolved",
    error => error?.name || "rejected",
  );
  upstream.abort();
  const outcome = await pending;
  if (outcome !== "AbortError") {
    throw new Error(`expected AbortError, got ${outcome}`);
  }
})().catch((error) => { console.error(error); process.exit(1); });
""".replace("__API_JS__", repr(str(API_JS)))

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


def test_review_cards_render_terminal_scan_profile_catalog_error() -> None:
    script = f"""
const fs = require("fs");
const vm = require("vm");
function node(tagName) {{
  return {{
    tagName,
    children: [],
    _text: "",
    appendChild(child) {{ this.children.push(child); }},
    replaceChildren() {{ this.children = []; this._text = ""; }},
    addEventListener() {{}},
    get textContent() {{ return this._text + this.children.map((child) => child.textContent).join(""); }},
    set textContent(value) {{ this._text = String(value); this.children = []; }},
  }};
}}
const cards = {{
  "#review-client": node("article"),
  "#review-focus": node("article"),
  "#review-profile": node("article"),
  "#review-hardware": node("article"),
  "#review-scan-scope": node("article"),
}};
global.window = {{MorphicWorkbenchState: {{
  workbenchMode: "standard",
  scanProfileCatalogStatus: "error",
  scanProfileCatalogError: "Lokaler Quellenkatalog nicht verfügbar.",
}}}};
global.document = {{
  querySelector(selector) {{ return cards[selector] || null; }},
  createElement(tagName) {{ return node(tagName); }},
  createTextNode(value) {{ const text = node("#text"); text.textContent = value; return text; }},
}};
vm.runInThisContext(fs.readFileSync({str(RENDER_JS)!r}, "utf8"));
window.MorphicWorkbenchRender.renderReviewCards({{}}, null, null);
const text = cards["#review-scan-scope"].textContent;
if (!text.includes("Lokaler Quellenkatalog nicht verfügbar.")) {{
  throw new Error(`terminaler Katalogfehler fehlt: ${{text}}`);
}}
if (text.includes("wird geladen")) {{
  throw new Error(`Fehlerzustand bleibt fälschlich im Laden: ${{text}}`);
}}
"""

    result = _run_node(script)

    assert result.returncode == 0, result.stderr


def test_catalog_loader_uses_explicit_states_and_rerenders_terminal_error() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    loader = source.split(
        "async function loadScanProfileCatalog(profileLevel, generation = caseGeneration)",
        1,
    )[1].split("/* ── Hardware Truth", 1)[0]

    assert 'scanProfileCatalogStatus = "loading"' in loader
    assert 'scanProfileCatalogStatus = "ready"' in loader
    assert 'scanProfileCatalogStatus = "error"' in loader
    catch_body = loader.split("} catch (e) {", 1)[1]
    assert "renderReviewCards(" in catch_body
    assert "scanProfileCatalogError" in catch_body


def test_bootstrap_wires_catalog_listener_before_parallel_initial_reads() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    bootstrap = source.split("async function bootstrapWorkbench()", 1)[1].split(
        "bootstrapWorkbench();", 1
    )[0]

    listener_at = bootstrap.index('profileLevelControl.addEventListener("change"')
    parallel_at = bootstrap.index("Promise.allSettled(")
    assert listener_at < parallel_at
    assert "loadHealthAndSources(generation)" in bootstrap[parallel_at:]
    assert "loadScanProfileCatalog(initialProfileLevel, generation)" in bootstrap[parallel_at:]
    assert "loadHardwareTruth(generation)" in bootstrap[parallel_at:]
    assert "loadReports(generation)" in bootstrap[parallel_at:]
