from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
STATE_JS = ROOT / "apps" / "web" / "static" / "workbench-state.js"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
NODE_HARNESS_TIMEOUT_SECONDS = 10


def _run_app_script(
    body: str,
    *,
    mutate_authority_assignment: bool = False,
    mutate_harmonization_eligibility: bool = False,
    media_query_mode: str = "modern",
) -> subprocess.CompletedProcess[str]:
    harness = r"""
const fs = require("fs");
const vm = require("vm");

const createdElementTags = [];
let innerHTMLWriteCount = 0;

function node(overrides = {}) {
  const attributes = new Map();
  const classes = new Set();
  const listeners = {};
  const element = {
    tagName: "",
    textContent: "",
    className: "",
    disabled: false,
    checked: false,
    hidden: false,
    value: "",
    href: "",
    src: "",
    srcdoc: "",
    style: {},
    dataset: {},
    children: [],
    options: [],
    selectedIndex: 0,
    tabIndex: -1,
    focusCalls: 0,
    listeners,
    classList: {
      add(name) { classes.add(name); },
      remove(name) { classes.delete(name); },
      toggle(name, force) {
        if (force === true) classes.add(name);
        else if (force === false) classes.delete(name);
        else if (classes.has(name)) classes.delete(name);
        else classes.add(name);
      },
      contains(name) { return classes.has(name); },
    },
    addEventListener(type, listener) { listeners[type] = listener; },
    appendChild(child) { this.children.push(child); return child; },
    replaceChildren(...children) { this.children = children; },
    querySelectorAll() { return []; },
    focus() { this.focusCalls += 1; },
    reset() {},
    dispatchEvent() {},
    setAttribute(name, value) { attributes.set(name, String(value)); },
    removeAttribute(name) {
      attributes.delete(name);
      if (name === "src") this.src = "";
    },
    getAttribute(name) { return attributes.has(name) ? attributes.get(name) : null; },
    ...overrides,
  };
  Object.defineProperty(element, "innerHTML", {
    get() { return ""; },
    set() {
      innerHTMLWriteCount += 1;
      throw new Error("innerHTML assignment is forbidden in the report DOM harness");
    },
  });
  return element;
}

const controls = {
  profile_level: node({value: "3"}),
  top_n: node({value: "5", options: ["3", "5", "7", "9"].map(value => node({value}))}),
  target_frequency: node({value: "432"}),
};
const scanForm = node({
  fields: controls,
  reset() { controls.profile_level.value = "3"; },
});
const nodes = {
  "#scan-form": scanForm,
  "#preview-state": node(),
  "#wizard-navigation-state": node(),
  "#new-case-button": node(),
  "#preview-button": node(),
  "#start-analysis-button": node(),
  "#scan-refresh-button": node(),
  "#scan-stop-button": node(),
  "#report-list": node({children: [node()]}),
  "#reports-state": node(),
  "#report-preview-panel": node({dataset: {state: "empty"}, hidden: false}),
  "#report-preview-frame": node({src: "/stale-report", srcdoc: "<p>stale</p>", hidden: false}),
  "#report-preview-text": node({textContent: "stale text", hidden: true}),
  "#report-preview-title": node({textContent: "stale title"}),
  "#report-preview-meta": node({textContent: "stale metadata"}),
  "#report-preview-state": node({textContent: "stale state", className: "inline-state ok"}),
  "#report-open-link": node({href: "/api/reports/stale/file", hidden: false}),
  "#harmonization-start-button": node({disabled: true}),
};

global.FormData = class FormDataDouble {
  constructor(form) { this.form = form; }
  get(name) { return this.form?.fields?.[name]?.value ?? null; }
};
global.Event = class EventDouble { constructor(type) { this.type = type; } };
global.document = {
  body: node({dataset: {}}),
  querySelector(selector) {
    if (nodes[selector]) return nodes[selector];
    const match = selector.match(/name="([^"]+)"/);
    return match ? controls[match[1]] || null : null;
  },
  querySelectorAll(selector) {
    if (selector === ".report-item") return nodes["#report-list"].children;
    return [];
  },
  createElement(tagName) {
    const normalized = String(tagName || "").toUpperCase();
    createdElementTags.push(normalized);
    return node({tagName: normalized});
  },
  createTextNode(value) { return node({textContent: String(value)}); },
};
const storage = new Map();
const mediaQueryMode = __MEDIA_QUERY_MODE__;
let matchMediaCalls = 0;
let modernMediaSubscriptions = 0;
let legacyMediaSubscriptions = 0;
const windowListeners = {};
const reportListMediaQuery = {
  media: "(max-width: 768px)",
  matches: false,
};
if (mediaQueryMode === "modern") {
  reportListMediaQuery.addEventListener = () => { modernMediaSubscriptions += 1; };
} else if (mediaQueryMode === "legacy") {
  reportListMediaQuery.addListener = () => { legacyMediaSubscriptions += 1; };
}
global.window = {
  innerWidth: 1024,
  addEventListener(type, listener) { windowListeners[type] = listener; },
  localStorage: {
    getItem(key) { return storage.has(key) ? storage.get(key) : null; },
    setItem(key, value) { storage.set(key, String(value)); },
    removeItem(key) { storage.delete(key); },
  },
  MorphicWorkbenchApi: {},
  MorphicWorkbenchRender: {
    renderResults() {},
    renderRunTrace() {},
    renderReviewCards() {},
    renderChoiceCards() {},
    resetSubstepTimeline() {},
    renderSubstepTimeline() {},
    showStep() {},
  },
};
if (mediaQueryMode !== "absent") {
  window.matchMedia = () => {
    matchMediaCalls += 1;
    return reportListMediaQuery;
  };
}
global.setTimeout = () => 1;
global.clearTimeout = () => {};

vm.runInThisContext(fs.readFileSync(__STATE_JS__, "utf8"));
let appSource = fs.readFileSync(__APP_JS__, "utf8");
if (__MUTATE_AUTHORITY__) {
  const assignmentStart = appSource.indexOf("  transitionReportAuthority({\n    type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,");
  const assignmentEnd = appSource.indexOf("  state.scanResults = results;", assignmentStart);
  if (assignmentStart < 0 || assignmentEnd < 0) {
    throw new Error("mutation target for report authority dispatch not found");
  }
  appSource = appSource.slice(0, assignmentStart)
    + "  state.activeReportSessionId = state.activeReportSessionId;\n"
    + appSource.slice(assignmentEnd);
}
if (__MUTATE_HARMONIZATION_ELIGIBILITY__) {
  const functionStart = appSource.indexOf("function reportAuthorityCanHarmonize(authority) {");
  const functionEnd = appSource.indexOf("\nfunction reportAuthorityEffect", functionStart);
  if (functionStart < 0 || functionEnd < 0) {
    throw new Error("mutation target for harmonization eligibility not found");
  }
  appSource = appSource.slice(0, functionStart)
    + "function reportAuthorityCanHarmonize(authority) {\n  return Boolean(authority.stable);\n}\n"
    + appSource.slice(functionEnd + 1);
}
vm.runInThisContext(appSource);

function acceptReportSessionForHarness(sessionId) {
  transitionReportAuthority({
    type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
    generation: caseGeneration,
    sessionId,
  });
}

function validCatalog(level = 3) {
  return {
    profile_level: Number(level),
    pool_authority: {fingerprint: "a".repeat(64)},
    internal: {count: 0, profiles: []},
    external: {},
  };
}
async function waitUntil(predicate) {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    if (predicate()) return;
    await Promise.resolve();
  }
  throw new Error("timed out waiting for controlled promise boundary");
}

(async function runGate4Harness() {
__BODY__
console.log("__MORPHIC_GATE4_NODE_SUCCESS__");
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    script = (
        harness.replace("__STATE_JS__", json.dumps(str(STATE_JS)))
        .replace("__APP_JS__", json.dumps(str(APP_JS)))
        .replace(
            "__MUTATE_AUTHORITY__",
            "true" if mutate_authority_assignment else "false",
        )
        .replace(
            "__MUTATE_HARMONIZATION_ELIGIBILITY__",
            "true" if mutate_harmonization_eligibility else "false",
        )
        .replace("__MEDIA_QUERY_MODE__", json.dumps(media_query_mode))
        .replace("__BODY__", body.strip())
    )
    return subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=NODE_HARNESS_TIMEOUT_SECONDS,
    )


def _assert_node_success(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, result.stderr
    assert "__MORPHIC_GATE4_NODE_SUCCESS__" in result.stdout.splitlines()


def test_report_helpers_flatten_context_and_rank_exact_session() -> None:
    body = r"""
const clients = [{
  client_id: "client-a",
  label: "Klient A",
  sessions: [{
    session_id: "session-active",
    label: "Session aktiv",
    files: [
      {id: "pdf-new", kind: "PDF", modified_at: "2026-07-31T12:04:00Z"},
      {id: "json-new", kind: "JSON", modified_at: "2026-07-31T12:03:00Z"},
      {id: "txt-old", kind: "TXT", modified_at: "2026-07-31T12:02:00Z"},
      {id: "html-old", kind: "HTML", modified_at: "2026-07-31T12:01:00Z"},
    ],
  }],
}, {
  client_id: "client-b",
  label: "Klient B",
  sessions: [{
    session_id: "session-other",
    label: "Session fremd",
    files: [
      {id: "html-foreign-new", kind: "HTML", modified_at: "2026-07-31T13:00:00Z"},
    ],
  }],
}];
const entries = flattenReportEntries(clients);
const chosen = automaticReportCandidate(entries, "session-active");
const withoutHtml = entries.filter(entry => entry.kind !== "HTML");
const textChosen = automaticReportCandidate(withoutHtml, "session-active");
const pdfOnly = entries.filter(entry => entry.kind === "PDF");
const pdfChosen = automaticReportCandidate(pdfOnly, "session-active");
const unknown = automaticReportCandidate(entries, "session-missing");
console.log(JSON.stringify({entries, chosen, textChosen, pdfChosen, unknown}));
"""

    result = _run_app_script(body)
    _assert_node_success(result)
    payload = json.loads(result.stdout.splitlines()[0])

    assert payload["entries"][0]["client_label"] == "Klient A"
    assert payload["entries"][0]["session_label"] == "Session aktiv"
    assert payload["chosen"]["id"] == "html-old"
    assert payload["textChosen"]["id"] == "json-new"
    assert payload["pdfChosen"]["id"] == "pdf-new"
    assert payload["unknown"] is None


def test_report_helpers_reject_malformed_entries_and_keep_ties_stable() -> None:
    body = r"""
const clients = [
  null,
  17,
  [],
  {},
  {
    client_id: "client-fallback",
    sessions: [null, 3, [], {}, {
      session_id: "session-fallback",
      files: [
        null,
        9,
        [],
        {},
        {id: ""},
        {id: "   ", kind: "HTML"},
        {id: 42, kind: "HTML"},
        {id: "fallback-report", kind: "TXT", modified_at: "not-a-date"},
      ],
    }],
  },
  {
    client_id: "   ",
    label: "   ",
    sessions: [{
      session_id: "   ",
      label: "   ",
      files: [{id: "unknown-context", kind: "PDF"}],
    }],
  },
  {
    label: "Klient Tie",
    sessions: [{
      session_id: "session-tie",
      label: "Session Tie",
      files: [
        {id: "tie-first", kind: "HTML", modified_at: "2026-07-31T12:00:00Z"},
        {id: "tie-second", kind: "HTML", modified_at: "2026-07-31T12:00:00Z"},
      ],
    }],
  },
];
const entries = flattenReportEntries(clients);
const fallback = entries.find(entry => entry.id === "fallback-report");
const unknownContext = entries.find(entry => entry.id === "unknown-context");
const tied = automaticReportCandidate([null, 5, ...entries], "session-tie");
window.MorphicWorkbenchState.activeReportSessionId = null;
window.MorphicWorkbenchApi = {
  async loadReports() { return {clients}; },
  async loadReportPreview() { throw new Error("malformed catalog must not auto-preview"); },
};
await loadReports(caseGeneration, true);
console.log(JSON.stringify({
  ids: entries.map(entry => entry.id),
  cardIds: nodes["#report-list"].children.map(card => card.dataset.reportId),
  fallback,
  unknownContext,
  tied,
  invalidTimes: [
    reportModifiedTime(null),
    reportModifiedTime({}),
    reportModifiedTime({modified_at: "invalid"}),
  ],
}));
"""

    result = _run_app_script(body)
    _assert_node_success(result)
    payload = json.loads(result.stdout.splitlines()[0])

    assert payload["ids"] == [
        "fallback-report",
        "unknown-context",
        "tie-first",
        "tie-second",
    ]
    assert payload["cardIds"] == payload["ids"]
    assert payload["fallback"]["client_label"] == "client-fallback"
    assert payload["fallback"]["session_label"] == "session-fallback"
    assert payload["unknownContext"]["client_label"] == "Unbekannt"
    assert payload["unknownContext"]["session_label"] == "Unbekannt"
    assert payload["tied"]["id"] == "tie-first"
    assert payload["invalidTimes"] == [0, 0, 0]


def test_report_authority_constructor_catalog_and_inputs_are_immutable() -> None:
    body = r"""
if (
  typeof createReportAuthorityState !== "function"
  || typeof reduceReportAuthority !== "function"
  || typeof reportAuthorityCanHarmonize !== "function"
  || typeof REPORT_AUTHORITY_EVENT !== "object"
) {
  throw new Error("report authority reducer globals are missing");
}
const eventNames = [
  "ACTIVE_SESSION_ACCEPTED", "CATALOG_REQUESTED", "CATALOG_ACCEPTED",
  "CATALOG_FAILED", "PREVIEW_REQUESTED", "PREVIEW_SUCCEEDED",
  "PREVIEW_FAILED", "PREVIEW_STALE", "RESET_STARTED", "RESET_ABORTED",
  "RESET_COMPLETED", "HARMONIZATION_STATE_CHANGED", "FOCUS_MOVED",
];
if (
  !Object.isFrozen(REPORT_AUTHORITY_EVENT)
  || eventNames.some(name => REPORT_AUTHORITY_EVENT[name] !== name)
) {
  throw new Error("authority event constants are not stable");
}

const initial = createReportAuthorityState(4);
const separate = createReportAuthorityState(4);
if (
  !Object.isFrozen(initial)
  || initial.generation !== 4
  || initial.nextCatalogRequestId !== 1
  || initial.acceptedCatalogRequestId !== 0
  || initial.nextPreviewRequestId !== 1
  || initial.activeSessionId !== null
  || !(initial.entriesById instanceof Map)
  || initial.entriesById.size !== 0
  || initial.entriesById === separate.entriesById
  || initial.stable !== null
  || initial.pending !== null
  || initial.deferredRefresh !== null
  || initial.autoAttemptKey !== null
  || initial.focusId !== null
  || initial.resetCheckpoint !== null
  || initial.harmonizationStartPending
  || initial.harmonizationRunActive
  || initial.canHarmonize
) {
  throw new Error("authority constructor defaults are not isolated and immutable");
}

const sessionEvent = {
  type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
  generation: 4,
  sessionId: "  session-b  ",
};
const sessionEventBefore = JSON.stringify(sessionEvent);
const sessionAccepted = reduceReportAuthority(initial, sessionEvent);
if (
  sessionAccepted.state.activeSessionId !== "session-b"
  || initial.activeSessionId !== null
  || initial.entriesById.size !== 0
  || JSON.stringify(sessionEvent) !== sessionEventBefore
  || sessionAccepted.effects.length !== 0
) {
  throw new Error("active session normalization mutated reducer inputs");
}
const invalidSession = reduceReportAuthority(sessionAccepted.state, {
  type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
  generation: 4,
  sessionId: new String("foreign"),
});
if (invalidSession.state.activeSessionId !== null) {
  throw new Error("non-primitive active session was accepted");
}
const staleSession = reduceReportAuthority(sessionAccepted.state, {
  type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
  generation: 3,
  sessionId: "stale",
});
if (staleSession.state !== sessionAccepted.state || staleSession.effects.length !== 0) {
  throw new Error("stale active-session generation changed authority");
}

const requested = reduceReportAuthority(sessionAccepted.state, {
  type: REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED,
  generation: 4,
});
const requestEffect = requested.effects.find(effect => effect.type === "LOAD_CATALOG");
const request = requestEffect?.request;
if (
  !request
  || !Object.isFrozen(request)
  || request.generation !== 4
  || request.requestId !== 1
  || requested.state.nextCatalogRequestId !== 2
  || sessionAccepted.state.nextCatalogRequestId !== 1
) {
  throw new Error("catalog request allocation is not immutable");
}
const staleCatalog = reduceReportAuthority(requested.state, {
  type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
  generation: 4,
  request: {...request, requestId: 0},
  entries: [{id: "stale"}],
});
if (staleCatalog.state !== requested.state || staleCatalog.effects.length !== 0) {
  throw new Error("non-latest catalog acceptance changed authority");
}

const entries = [
  {id: "report-a", session_id: "session-a", kind: "TXT", modified_at: "v1", size: 1},
  {id: "report-a", session_id: "session-b", kind: "HTML", modified_at: "v2", size: 2},
  {id: "report-b", session_id: "session-b", kind: "JSON", modified_at: "v1", size: 3},
];
const entriesBefore = JSON.stringify(entries);
const accepted = reduceReportAuthority(requested.state, {
  type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
  generation: 4,
  request,
  entries,
});
if (
  accepted.state.acceptedCatalogRequestId !== request.requestId
  || accepted.state.entriesById === requested.state.entriesById
  || accepted.state.entriesById.size !== 2
  || accepted.state.entriesById.get("report-a")?.kind !== "TXT"
  || !Object.isFrozen(accepted.state.entriesById.get("report-a"))
  || requested.state.entriesById.size !== 0
  || JSON.stringify(entries) !== entriesBefore
  || !accepted.effects.some(effect => effect.type === "RENDER_CATALOG")
) {
  throw new Error("catalog acceptance did not deduplicate first-wins without mutation");
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_report_authority_manual_priority_and_stale_are_exact() -> None:
    body = r"""
if (
  typeof createReportAuthorityState !== "function"
  || typeof reduceReportAuthority !== "function"
) {
  throw new Error("report authority reducer globals are missing");
}
let authority = createReportAuthorityState(4);
let transition = reduceReportAuthority(authority, {
  type: REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED,
  generation: 4,
});
const catalogRequest = transition.effects.find(effect => effect.type === "LOAD_CATALOG").request;
authority = reduceReportAuthority(transition.state, {
  type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
  generation: 4,
  request: catalogRequest,
  entries: [
    {id: "report-a", session_id: "session-a", kind: "TXT", modified_at: "v1", size: 1},
    {id: "report-c", session_id: "session-b", kind: "HTML", modified_at: "v1", size: 2},
  ],
}).state;

const manualEvent = {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 4,
  reportId: "report-a",
  intent: "manual",
};
const manualEventBefore = JSON.stringify(manualEvent);
const manual = reduceReportAuthority(authority, manualEvent);
const manualRequest = manual.effects.find(effect => effect.type === "LOAD_PREVIEW")?.request;
if (
  !manualRequest
  || !Object.isFrozen(manualRequest)
  || manualRequest.generation !== 4
  || manualRequest.requestId !== 1
  || manualRequest.reportId !== "report-a"
  || manualRequest.intent !== "manual"
  || manualRequest.expectedFingerprint !== reportEntryFingerprint(
    authority.entriesById.get("report-a")
  )
  || manualRequest.expectedSessionId !== null
  || manualRequest.catalogRequestId !== catalogRequest.requestId
  || manual.state.pending !== manualRequest
  || manual.state.nextPreviewRequestId !== 2
  || authority.pending !== null
  || JSON.stringify(manualEvent) !== manualEventBefore
  || manual.effects.map(effect => effect.type).join(",") !== "RENDER_LOADING,LOAD_PREVIEW"
) {
  throw new Error("manual preview request context is not exact and immutable");
}

const withSession = reduceReportAuthority(manual.state, {
  type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
  generation: 4,
  sessionId: "session-b",
}).state;
const blockedAuto = reduceReportAuthority(withSession, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 4,
  reportId: "report-c",
  intent: "auto",
});
const blockedRefresh = reduceReportAuthority(withSession, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 4,
  reportId: "report-a",
  intent: "refresh",
});
if (
  blockedAuto.state !== withSession
  || blockedAuto.effects.length !== 0
  || blockedRefresh.state !== withSession
  || blockedRefresh.effects.length !== 0
) {
  throw new Error("auto or refresh superseded pending manual authority");
}

const newerManual = reduceReportAuthority(withSession, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 4,
  reportId: "report-c",
  intent: "manual",
});
const newerRequest = newerManual.effects.find(effect => effect.type === "LOAD_PREVIEW")?.request;
if (
  newerRequest?.requestId !== 2
  || newerManual.state.pending !== newerRequest
  || newerManual.state.pending.reportId !== "report-c"
) {
  throw new Error("new manual request did not supersede prior preview request");
}
const nonmatchingStale = reduceReportAuthority(newerManual.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_STALE,
  request: manualRequest,
});
if (nonmatchingStale.state !== newerManual.state || nonmatchingStale.effects.length !== 0) {
  throw new Error("nonmatching stale completion mutated authority");
}
const matchingStale = reduceReportAuthority(newerManual.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_STALE,
  request: newerRequest,
});
if (
  matchingStale.state.pending !== null
  || matchingStale.state.autoAttemptKey !== null
  || newerManual.state.pending !== newerRequest
) {
  throw new Error("matching stale did not clear only pending authority");
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_report_authority_auto_context_terminal_attempt_and_stable_failure() -> None:
    body = r"""
if (
  typeof createReportAuthorityState !== "function"
  || typeof reduceReportAuthority !== "function"
) {
  throw new Error("report authority reducer globals are missing");
}
function acceptCatalog(authority, entries) {
  const requested = reduceReportAuthority(authority, {
    type: REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED,
    generation: authority.generation,
  });
  const request = requested.effects.find(effect => effect.type === "LOAD_CATALOG").request;
  return reduceReportAuthority(requested.state, {
    type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
    generation: authority.generation,
    request,
    entries,
  });
}
const entries = [
  {id: "report-a", session_id: "session-a", kind: "TXT", modified_at: "v1", size: 1},
  {id: "report-c", session_id: "session-b", kind: "HTML", modified_at: "v1", size: 2},
];
let authority = createReportAuthorityState(4);
authority = reduceReportAuthority(authority, {
  type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
  generation: 4,
  sessionId: "session-b",
}).state;
let accepted = acceptCatalog(authority, entries);
let autoRequest = accepted.effects.find(effect => effect.type === "LOAD_PREVIEW")?.request;
if (
  !autoRequest
  || autoRequest.reportId !== "report-c"
  || autoRequest.intent !== "auto"
  || autoRequest.expectedSessionId !== "session-b"
  || autoRequest.expectedFingerprint !== reportEntryFingerprint(entries[1])
  || autoRequest.catalogRequestId !== accepted.state.acceptedCatalogRequestId
  || accepted.state.pending !== autoRequest
  || accepted.state.autoAttemptKey !== null
) {
  throw new Error("exact-session automatic request context was not derived");
}

const staleAuto = reduceReportAuthority(accepted.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_STALE,
  request: autoRequest,
});
if (staleAuto.state.pending !== null || staleAuto.state.autoAttemptKey !== null) {
  throw new Error("stale automatic completion consumed its attempt");
}
accepted = acceptCatalog(staleAuto.state, entries);
autoRequest = accepted.effects.find(effect => effect.type === "LOAD_PREVIEW")?.request;
if (!autoRequest || autoRequest.reportId !== "report-c") {
  throw new Error("stale automatic attempt was not retryable");
}

const view = {reportId: "report-c", mode: "text", title: "C", content: "stable-c", size: 2};
const viewBefore = JSON.stringify(view);
const succeeded = reduceReportAuthority(accepted.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_SUCCEEDED,
  request: autoRequest,
  view,
});
if (
  succeeded.state.pending !== null
  || !Object.isFrozen(succeeded.state.stable)
  || !Object.isFrozen(succeeded.state.stable?.view)
  || succeeded.state.stable?.view === view
  || succeeded.state.stable?.reportId !== "report-c"
  || succeeded.state.stable?.generation !== 4
  || succeeded.state.stable?.sessionId !== "session-b"
  || succeeded.state.stable?.entryFingerprint !== autoRequest.expectedFingerprint
  || succeeded.state.stable?.selectionSource !== "auto"
  || succeeded.state.focusId !== "report-c"
  || succeeded.state.autoAttemptKey !== "4:session-b"
  || !succeeded.state.canHarmonize
  || JSON.stringify(view) !== viewBefore
  || !succeeded.effects.some(effect => effect.type === "RENDER_STABLE")
  || !succeeded.effects.some(effect => effect.type === "RENDER_CATALOG_SELECTION")
  || !succeeded.effects.some(effect => effect.type === "SYNC_HARMONIZATION")
) {
  throw new Error("authoritative automatic success did not create stable immutable authority");
}

const replacement = reduceReportAuthority(succeeded.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 4,
  reportId: "report-a",
  intent: "manual",
});
const replacementRequest = replacement.effects.find(
  effect => effect.type === "LOAD_PREVIEW"
)?.request;
const failedReplacement = reduceReportAuthority(replacement.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_FAILED,
  request: replacementRequest,
  message: "controlled replacement failure",
});
if (
  failedReplacement.state.pending !== null
  || failedReplacement.state.stable !== succeeded.state.stable
  || failedReplacement.state.stable?.reportId !== "report-c"
  || !failedReplacement.state.canHarmonize
  || !failedReplacement.effects.some(effect => effect.type === "RENDER_STABLE")
  || failedReplacement.effects.some(effect => effect.type === "RENDER_ERROR")
) {
  throw new Error("failed replacement became active or discarded stable fallback");
}

let failureAuthority = createReportAuthorityState(8);
failureAuthority = reduceReportAuthority(failureAuthority, {
  type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
  generation: 8,
  sessionId: "session-b",
}).state;
const failureAccepted = acceptCatalog(failureAuthority, entries);
const failureRequest = failureAccepted.effects.find(
  effect => effect.type === "LOAD_PREVIEW"
)?.request;
const autoFailed = reduceReportAuthority(failureAccepted.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_FAILED,
  request: failureRequest,
  message: "controlled auto failure",
});
if (
  autoFailed.state.pending !== null
  || autoFailed.state.stable !== null
  || autoFailed.state.autoAttemptKey !== "8:session-b"
  || autoFailed.state.canHarmonize
  || !autoFailed.effects.some(effect => effect.type === "RENDER_ERROR")
) {
  throw new Error("authoritative automatic failure did not consume the exact attempt");
}
const noRetry = acceptCatalog(autoFailed.state, entries);
if (noRetry.effects.some(effect => effect.type === "LOAD_PREVIEW")) {
  throw new Error("consumed automatic attempt was retried");
}

let noMatchAuthority = createReportAuthorityState(9);
noMatchAuthority = reduceReportAuthority(noMatchAuthority, {
  type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
  generation: 9,
  sessionId: "session-missing",
}).state;
const noMatch = acceptCatalog(noMatchAuthority, entries);
if (
  noMatch.state.autoAttemptKey !== null
  || noMatch.state.pending !== null
  || noMatch.effects.some(effect => effect.type === "LOAD_PREVIEW")
) {
  throw new Error("catalog no-match consumed automatic attempt authority");
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_report_authority_catalog_reconciles_manual_refresh_before_session_auto() -> None:
    body = r"""
if (
  typeof createReportAuthorityState !== "function"
  || typeof reduceReportAuthority !== "function"
) {
  throw new Error("report authority reducer globals are missing");
}
function acceptCatalog(authority, entries) {
  const requested = reduceReportAuthority(authority, {
    type: REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED,
    generation: authority.generation,
  });
  const request = requested.effects.find(effect => effect.type === "LOAD_CATALOG").request;
  return reduceReportAuthority(requested.state, {
    type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
    generation: authority.generation,
    request,
    entries,
  });
}
const aV1 = {id: "report-a", session_id: "session-a", kind: "HTML", modified_at: "v1", size: 1};
const aV2 = {...aV1, modified_at: "v2", size: 2};
const aV3 = {...aV1, modified_at: "v3", size: 3};
const c = {id: "report-c", session_id: "session-b", kind: "HTML", modified_at: "v1", size: 4};

let oldAuto = createReportAuthorityState(4);
oldAuto = reduceReportAuthority(oldAuto, {
  type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
  generation: 4,
  sessionId: "session-a",
}).state;
let accepted = acceptCatalog(oldAuto, [aV1, c]);
let request = accepted.effects.find(effect => effect.type === "LOAD_PREVIEW").request;
oldAuto = reduceReportAuthority(accepted.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_SUCCEEDED,
  request,
  view: {reportId: "report-a", mode: "text", content: "a-v1"},
}).state;
oldAuto = reduceReportAuthority(oldAuto, {
  type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
  generation: 4,
  sessionId: "session-b",
}).state;
accepted = acceptCatalog(oldAuto, [aV2, c]);
request = accepted.effects.find(effect => effect.type === "LOAD_PREVIEW")?.request;
if (
  accepted.state.stable?.reportId !== "report-a"
  || request?.reportId !== "report-c"
  || request?.intent !== "auto"
  || request?.expectedSessionId !== "session-b"
  || accepted.state.deferredRefresh !== null
) {
  throw new Error("old automatic fingerprint drift blocked exact-session candidate");
}

let manual = createReportAuthorityState(5);
accepted = acceptCatalog(manual, [aV1, c]);
manual = accepted.state;
let manualRequested = reduceReportAuthority(manual, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 5,
  reportId: "report-a",
  intent: "manual",
});
request = manualRequested.effects.find(effect => effect.type === "LOAD_PREVIEW").request;
manual = reduceReportAuthority(manualRequested.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_SUCCEEDED,
  request,
  view: {reportId: "report-a", mode: "text", content: "manual-a-v1"},
}).state;
manual = reduceReportAuthority(manual, {
  type: REPORT_AUTHORITY_EVENT.ACTIVE_SESSION_ACCEPTED,
  generation: 5,
  sessionId: "session-b",
}).state;
accepted = acceptCatalog(manual, [aV2, c]);
request = accepted.effects.find(effect => effect.type === "LOAD_PREVIEW")?.request;
if (
  accepted.state.stable?.selectionSource !== "manual"
  || request?.reportId !== "report-a"
  || request?.intent !== "refresh"
  || request?.expectedFingerprint !== reportEntryFingerprint(aV2)
  || request?.expectedSessionId !== null
) {
  throw new Error("manual stable fingerprint refresh did not dominate session auto-selection");
}

manualRequested = reduceReportAuthority(accepted.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 5,
  reportId: "report-c",
  intent: "manual",
});
const pendingManual = manualRequested.state.pending;
accepted = acceptCatalog(manualRequested.state, [aV3, c]);
if (
  accepted.state.pending !== pendingManual
  || accepted.state.pending?.reportId !== "report-c"
  || accepted.state.deferredRefresh?.reportId !== "report-a"
  || accepted.state.deferredRefresh?.expectedFingerprint !== reportEntryFingerprint(aV3)
  || accepted.effects.some(effect => effect.type === "LOAD_PREVIEW")
) {
  throw new Error("manual pending intent did not defer latest stable fingerprint refresh");
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_report_authority_fingerprint_eligibility_harmonization_and_focus() -> None:
    body = r"""
if (
  typeof createReportAuthorityState !== "function"
  || typeof reduceReportAuthority !== "function"
  || typeof reportAuthorityCanHarmonize !== "function"
) {
  throw new Error("report authority reducer globals are missing");
}
function acceptCatalog(authority, entries) {
  const requested = reduceReportAuthority(authority, {
    type: REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED,
    generation: authority.generation,
  });
  const request = requested.effects.find(effect => effect.type === "LOAD_CATALOG").request;
  return reduceReportAuthority(requested.state, {
    type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
    generation: authority.generation,
    request,
    entries,
  });
}
const aV1 = {id: "report-a", session_id: "session-a", kind: "TXT", modified_at: "v1", size: 1};
const aV2 = {...aV1, modified_at: "v2", size: 2};
let accepted = acceptCatalog(createReportAuthorityState(4), [aV1]);
let requested = reduceReportAuthority(accepted.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 4,
  reportId: "report-a",
  intent: "manual",
});
let request = requested.effects.find(effect => effect.type === "LOAD_PREVIEW").request;
let authority = reduceReportAuthority(requested.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_SUCCEEDED,
  request,
  view: {reportId: "report-a", mode: "text", content: "a-v1"},
}).state;
if (!authority.canHarmonize || !reportAuthorityCanHarmonize(authority)) {
  throw new Error("current stable fingerprint was not harmonization eligible");
}

const staleFlags = reduceReportAuthority(authority, {
  type: REPORT_AUTHORITY_EVENT.HARMONIZATION_STATE_CHANGED,
  generation: 3,
  harmonizationStartPending: true,
  harmonizationRunActive: true,
});
if (staleFlags.state !== authority || staleFlags.effects.length !== 0) {
  throw new Error("stale harmonization generation changed authority");
}
const invalidFlags = reduceReportAuthority(authority, {
  type: REPORT_AUTHORITY_EVENT.HARMONIZATION_STATE_CHANGED,
  harmonizationStartPending: 1,
  harmonizationRunActive: "yes",
});
if (
  invalidFlags.state.harmonizationStartPending
  || invalidFlags.state.harmonizationRunActive
  || !invalidFlags.state.canHarmonize
) {
  throw new Error("harmonization flags were not normalized as strict booleans");
}
const startPending = reduceReportAuthority(invalidFlags.state, {
  type: REPORT_AUTHORITY_EVENT.HARMONIZATION_STATE_CHANGED,
  harmonizationStartPending: true,
  harmonizationRunActive: false,
});
if (!startPending.state.harmonizationStartPending || startPending.state.canHarmonize) {
  throw new Error("harmonization start pending did not disable eligibility");
}
authority = reduceReportAuthority(startPending.state, {
  type: REPORT_AUTHORITY_EVENT.HARMONIZATION_STATE_CHANGED,
  harmonizationStartPending: false,
  harmonizationRunActive: false,
}).state;

const missingFocus = reduceReportAuthority(authority, {
  type: REPORT_AUTHORITY_EVENT.FOCUS_MOVED,
  focusId: "missing",
});
if (missingFocus.state !== authority || missingFocus.effects.length !== 0) {
  throw new Error("focus moved outside the accepted catalog");
}
const acceptedFocus = reduceReportAuthority(authority, {
  type: REPORT_AUTHORITY_EVENT.FOCUS_MOVED,
  focusId: "report-a",
});
if (
  acceptedFocus.state.focusId !== "report-a"
  || !acceptedFocus.effects.some(effect => effect.type === "RENDER_CATALOG_SELECTION")
) {
  throw new Error("accepted catalog focus was not stored");
}

accepted = acceptCatalog(acceptedFocus.state, [aV2]);
request = accepted.effects.find(effect => effect.type === "LOAD_PREVIEW")?.request;
if (
  request?.intent !== "refresh"
  || accepted.state.canHarmonize
  || reportAuthorityCanHarmonize(accepted.state)
) {
  throw new Error("fingerprint drift remained harmonization eligible");
}
const refreshFailed = reduceReportAuthority(accepted.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_FAILED,
  request,
  message: "controlled refresh failure",
});
if (
  refreshFailed.state.stable?.view?.content !== "a-v1"
  || refreshFailed.state.pending !== null
  || refreshFailed.state.canHarmonize
  || reportAuthorityCanHarmonize(refreshFailed.state)
  || !refreshFailed.effects.some(effect => effect.type === "RENDER_STABLE")
) {
  throw new Error("failed refresh did not retain an ineligible stable fallback");
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_report_authority_reset_checkpoint_abort_and_completion() -> None:
    body = r"""
if (
  typeof createReportAuthorityState !== "function"
  || typeof reduceReportAuthority !== "function"
) {
  throw new Error("report authority reducer globals are missing");
}
function acceptCatalog(authority, entries) {
  const requested = reduceReportAuthority(authority, {
    type: REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED,
    generation: authority.generation,
  });
  const request = requested.effects.find(effect => effect.type === "LOAD_CATALOG").request;
  return reduceReportAuthority(requested.state, {
    type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
    generation: authority.generation,
    request,
    entries,
  });
}
const aV1 = {id: "report-a", session_id: "session-a", kind: "TXT", modified_at: "v1", size: 1};
const aV2 = {...aV1, modified_at: "v2", size: 2};
const b = {id: "report-b", session_id: "session-a", kind: "JSON", modified_at: "v1", size: 3};
let accepted = acceptCatalog(createReportAuthorityState(4), [aV1, b]);
let requested = reduceReportAuthority(accepted.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 4,
  reportId: "report-a",
  intent: "manual",
});
let request = requested.effects.find(effect => effect.type === "LOAD_PREVIEW").request;
let authority = reduceReportAuthority(requested.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_SUCCEEDED,
  request,
  view: {reportId: "report-a", mode: "text", content: "stable-a-v1"},
}).state;
requested = reduceReportAuthority(authority, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 4,
  reportId: "report-b",
  intent: "manual",
});
const pendingB = requested.state.pending;
accepted = acceptCatalog(requested.state, [aV2, b]);
if (
  accepted.state.pending !== pendingB
  || accepted.state.deferredRefresh?.reportId !== "report-a"
) {
  throw new Error("reset setup did not retain pending manual and deferred refresh");
}

const catalogCounter = accepted.state.nextCatalogRequestId;
const previewCounter = accepted.state.nextPreviewRequestId;
const reset = reduceReportAuthority(accepted.state, {
  type: REPORT_AUTHORITY_EVENT.RESET_STARTED,
  generation: 4,
});
if (
  !reset.state.resetCheckpoint
  || !Object.isFrozen(reset.state.resetCheckpoint)
  || reset.state.resetCheckpoint.stable !== accepted.state.stable
  || reset.state.resetCheckpoint.deferredRefresh !== accepted.state.deferredRefresh
  || reset.state.pending !== null
  || reset.state.nextCatalogRequestId !== catalogCounter + 1
  || reset.state.nextPreviewRequestId !== previewCounter + 1
  || reset.state.canHarmonize
  || accepted.state.pending !== pendingB
  || !reset.effects.some(effect => effect.type === "DISABLE_HARMONIZATION")
) {
  throw new Error("reset start did not atomically checkpoint and invalidate authority");
}
const lateB = reduceReportAuthority(reset.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_STALE,
  request: pendingB,
});
if (lateB.state !== reset.state || lateB.effects.length !== 0) {
  throw new Error("late preview mutated reset checkpoint authority");
}
const staleAbort = reduceReportAuthority(reset.state, {
  type: REPORT_AUTHORITY_EVENT.RESET_ABORTED,
  generation: 3,
});
if (staleAbort.state !== reset.state || staleAbort.effects.length !== 0) {
  throw new Error("stale reset abort changed authority");
}

const aborted = reduceReportAuthority(reset.state, {
  type: REPORT_AUTHORITY_EVENT.RESET_ABORTED,
  generation: 4,
});
if (
  aborted.state.resetCheckpoint !== null
  || aborted.state.pending !== null
  || aborted.state.stable !== accepted.state.stable
  || aborted.state.deferredRefresh !== accepted.state.deferredRefresh
  || aborted.state.stable?.view?.content !== "stable-a-v1"
  || aborted.state.canHarmonize
  || !aborted.effects.some(effect => effect.type === "RENDER_STABLE")
) {
  throw new Error("reset abort did not restore outdated checkpoint as ineligible fallback");
}

const resetAgain = reduceReportAuthority(aborted.state, {
  type: REPORT_AUTHORITY_EVENT.RESET_STARTED,
  generation: 4,
});
const wrongCompletion = reduceReportAuthority(resetAgain.state, {
  type: REPORT_AUTHORITY_EVENT.RESET_COMPLETED,
  generation: 6,
});
if (wrongCompletion.state !== resetAgain.state || wrongCompletion.effects.length !== 0) {
  throw new Error("non-next reset completion changed authority");
}
const completed = reduceReportAuthority(resetAgain.state, {
  type: REPORT_AUTHORITY_EVENT.RESET_COMPLETED,
  generation: 5,
});
if (
  completed.state === resetAgain.state
  || !Object.isFrozen(completed.state)
  || completed.state.generation !== 5
  || completed.state.nextCatalogRequestId !== 1
  || completed.state.acceptedCatalogRequestId !== 0
  || completed.state.nextPreviewRequestId !== 1
  || completed.state.entriesById.size !== 0
  || completed.state.stable !== null
  || completed.state.pending !== null
  || completed.state.deferredRefresh !== null
  || completed.state.autoAttemptKey !== null
  || completed.state.focusId !== null
  || completed.state.resetCheckpoint !== null
  || completed.state.canHarmonize
) {
  throw new Error("reset completion did not create fresh next-generation authority");
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_report_authority_removed_stable_clears_preview_effects() -> None:
    body = r"""
function acceptCatalog(authority, entries) {
  const requested = reduceReportAuthority(authority, {
    type: REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED,
    generation: authority.generation,
  });
  const request = requested.effects.find(effect => effect.type === "LOAD_CATALOG").request;
  return reduceReportAuthority(requested.state, {
    type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
    generation: authority.generation,
    request,
    entries,
  });
}

const reportA = {
  id: "report-a", session_id: "session-a", kind: "TXT", modified_at: "v1", size: 1,
};
const reportB = {
  id: "report-b", session_id: "session-b", kind: "JSON", modified_at: "v1", size: 2,
};
let accepted = acceptCatalog(createReportAuthorityState(4), [reportA, reportB]);
let requested = reduceReportAuthority(accepted.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
  generation: 4,
  reportId: "report-a",
  intent: "manual",
});
const request = requested.effects.find(effect => effect.type === "LOAD_PREVIEW").request;
let authority = reduceReportAuthority(requested.state, {
  type: REPORT_AUTHORITY_EVENT.PREVIEW_SUCCEEDED,
  request,
  view: {reportId: "report-a", mode: "text", content: "stable-a"},
}).state;
if (!authority.canHarmonize || authority.stable?.reportId !== "report-a") {
  throw new Error("stable setup did not become harmonization eligible");
}

accepted = acceptCatalog(authority, [reportB]);
if (
  accepted.state.stable !== null
  || accepted.state.canHarmonize
  || accepted.effects.filter(effect => effect.type === "RENDER_CATALOG").length !== 1
  || !accepted.effects.some(effect => effect.type === "RENDER_EMPTY")
  || !accepted.effects.some(
    effect => effect.type === "SYNC_HARMONIZATION" && effect.canHarmonize === false
  )
  || accepted.effects.some(effect => effect.type === "LOAD_PREVIEW")
) {
  throw new Error(
    `removed stable did not emit clear effects: ${accepted.state.stable}/`
    + `${accepted.state.canHarmonize}/${accepted.effects.map(effect => effect.type)}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_report_catalog_wires_one_delegated_orientation_aware_keyboard_handler() -> None:
    app_source = APP_JS.read_text(encoding="utf-8")

    assert 'window.matchMedia("(max-width: 768px)")' in app_source
    assert (
        app_source.count(
            'reportList.addEventListener("keydown", handleReportListKeydown)'
        )
        == 1
    )
    assert "function nextReportFocusIndex(" in app_source
    handler_start = app_source.find("function handleReportListKeydown(")
    handler_end = app_source.find("function renderReportPreviewLoading", handler_start)
    assert handler_start >= 0
    assert handler_end > handler_start
    handler_source = app_source[handler_start:handler_end]
    for key in (
        "ArrowLeft",
        "ArrowRight",
        "ArrowUp",
        "ArrowDown",
        "Home",
        "End",
    ):
        assert key in handler_source
    assert "renderReportPreview(" not in handler_source


@pytest.mark.parametrize(
    (
        "mode",
        "media_matches",
        "inner_width",
        "orientation",
        "modern_subscriptions",
        "legacy_subscriptions",
        "resize_subscribed",
    ),
    [
        ("modern", True, 1024, "vertical", 1, 0, False),
        ("legacy", True, 1024, "vertical", 0, 1, False),
        ("absent", False, 375, "vertical", 0, 0, True),
    ],
)
def test_report_list_orientation_supports_media_query_subscription_variants(
    mode: str,
    media_matches: bool,
    inner_width: int,
    orientation: str,
    modern_subscriptions: int,
    legacy_subscriptions: int,
    resize_subscribed: bool,
) -> None:
    body = f"""
reportListMediaQuery.matches = {str(media_matches).lower()};
window.innerWidth = {inner_width};
syncReportListOrientation();
subscribeReportListOrientation();
console.log(JSON.stringify({{
  orientation: nodes["#report-list"].getAttribute("aria-orientation"),
  matchMediaCalls,
  modernMediaSubscriptions,
  legacyMediaSubscriptions,
  resizeSubscribed: typeof windowListeners.resize === "function",
}}));
"""
    result = _run_app_script(body, media_query_mode=mode)
    _assert_node_success(result)
    payload = json.loads(result.stdout.splitlines()[0])

    assert payload == {
        "orientation": orientation,
        "matchMediaCalls": 0 if mode == "absent" else 1,
        "modernMediaSubscriptions": modern_subscriptions,
        "legacyMediaSubscriptions": legacy_subscriptions,
        "resizeSubscribed": resize_subscribed,
    }


def test_next_report_focus_index_clamps_and_respects_orientation() -> None:
    body = r"""
console.log(JSON.stringify({
  leftAtStart: nextReportFocusIndex(0, 4, "ArrowLeft", false),
  right: nextReportFocusIndex(1, 4, "ArrowRight", false),
  downMobile: nextReportFocusIndex(1, 4, "ArrowDown", true),
  wrongAxisMobile: nextReportFocusIndex(1, 4, "ArrowRight", true),
  home: nextReportFocusIndex(2, 4, "Home", false),
  end: nextReportFocusIndex(1, 4, "End", true),
}));
"""

    result = _run_app_script(body)
    _assert_node_success(result)
    payload = json.loads(result.stdout.splitlines()[0])

    assert payload == {
        "leftAtStart": 0,
        "right": 2,
        "downMobile": 2,
        "wrongAxisMobile": 1,
        "home": 0,
        "end": 3,
    }


def test_report_keyboard_navigation_persists_focus_and_scrolls_nearest() -> None:
    body = r"""
let previewCalls = 0;
window.MorphicWorkbenchApi.loadReportPreview = async () => {
  previewCalls += 1;
  return {};
};
function reportCard(reportId) {
  const scrollCalls = [];
  const card = node({dataset: {reportId}, scrollCalls});
  card.closest = selector => selector === ".report-item" ? card : null;
  card.scrollIntoView = options => scrollCalls.push(options);
  return card;
}
const cards = [reportCard("report-a"), reportCard("report-b"), reportCard("report-c")];
const list = nodes["#report-list"];
list.children = cards;
list.contains = candidate => cards.includes(candidate);
list.querySelectorAll = selector => selector === ".report-item" ? cards : [];
reportAuthority = reportAuthorityState(reportAuthority, {
  entriesById: new Map(cards.map(card => [card.dataset.reportId, {
    id: card.dataset.reportId,
    session_id: "session-a",
  }])),
});
projectReportAuthority(reportAuthority);

function resetCards(anchorIndex) {
  cards.forEach((card, index) => {
    card.tabIndex = index === anchorIndex ? 0 : -1;
    card.focusCalls = 0;
    card.scrollCalls.length = 0;
  });
}
function dispatch(target, key) {
  const event = {
    target,
    key,
    prevented: false,
    preventDefault() { this.prevented = true; },
  };
  handleReportListKeydown(event);
  return event;
}
function snapshot(event) {
  return {
    prevented: event.prevented,
    tabStops: cards.filter(card => card.tabIndex === 0).map(card => card.dataset.reportId),
    focusId: window.MorphicWorkbenchState.reportFocusId,
    focusCalls: cards.map(card => card.focusCalls),
    scrollCalls: cards.map(card => card.scrollCalls.map(options => ({...options}))),
  };
}

reportListMediaQuery.matches = false;
list.setAttribute("aria-orientation", "horizontal");
resetCards(0);
const endpoint = snapshot(dispatch(cards[0], "ArrowLeft"));

reportListMediaQuery.matches = true;
list.setAttribute("aria-orientation", "vertical");
resetCards(0);
const wrongAxis = snapshot(dispatch(cards[0], "ArrowRight"));
const moved = snapshot(dispatch(cards[0], "ArrowDown"));

console.log(JSON.stringify({endpoint, wrongAxis, moved, previewCalls}));
"""

    result = _run_app_script(body)
    _assert_node_success(result)
    payload = json.loads(result.stdout.splitlines()[0])

    assert payload["endpoint"] == {
        "prevented": True,
        "tabStops": ["report-a"],
        "focusId": "report-a",
        "focusCalls": [1, 0, 0],
        "scrollCalls": [[{"block": "nearest", "inline": "nearest"}], [], []],
    }
    assert payload["wrongAxis"] == {
        "prevented": False,
        "tabStops": ["report-a"],
        "focusId": "report-a",
        "focusCalls": [0, 0, 0],
        "scrollCalls": [[], [], []],
    }
    assert payload["moved"] == {
        "prevented": True,
        "tabStops": ["report-b"],
        "focusId": "report-b",
        "focusCalls": [0, 1, 0],
        "scrollCalls": [[], [{"block": "nearest", "inline": "nearest"}], []],
    }
    assert payload["previewCalls"] == 0


def test_load_reports_auto_selects_once_and_preserves_manual_authority() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let previewCalls = [];
let catalog = {clients: [{
  client_id: "client-a",
  label: "Klient A",
  sessions: [{
    session_id: "session-active",
    label: "Session aktiv",
    files: [
      {id: "active-json", kind: "JSON", file_name: "Neu.json", modified_at: "2026-07-31T12:03:00Z"},
      {id: "active-html", kind: "HTML", file_name: "Alt.html", modified_at: "2026-07-31T12:01:00Z"},
    ],
  }, {
    session_id: "session-other",
    label: "Session manuell",
    files: [
      {id: "manual-report", kind: "TXT", file_name: "Manuell.txt", modified_at: "2026-07-31T13:00:00Z"},
    ],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: "session-missing",
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
acceptReportSessionForHarness("session-missing");
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview(reportId) {
    previewCalls.push(reportId);
    return {mode: "text", kind: "TXT", title: reportId, content: `preview:${reportId}`, size: 10};
  },
};

await loadReports(caseGeneration, true);
let cards = nodes["#report-list"].children;
if (cards.length !== 3 || cards.some(card => card.className !== "report-item")) {
  throw new Error(`catalog is not flat: ${cards.length}/${cards.map(card => card.className)}`);
}
if (
  cards.some(card => card.tagName !== "BUTTON")
  || createdElementTags.includes("DETAILS")
  || createdElementTags.includes("SUMMARY")
  || innerHTMLWriteCount !== 0
) {
  throw new Error(
    `unsafe or nested report DOM: ${createdElementTags}/${innerHTMLWriteCount}`
  );
}
const activeHtml = cards.find(card => card.dataset.reportId === "active-html");
if (!activeHtml || activeHtml.dataset.sessionId !== "session-active") {
  throw new Error("flat report card is missing report/session data attributes");
}
const metadata = activeHtml.children.map(child => child.className);
if (!metadata.includes("report-item-client") || !metadata.includes("report-item-session")) {
  throw new Error(`context metadata missing: ${metadata}`);
}
if (cards.filter(card => card.tabIndex === 0).length !== 1) {
  throw new Error("catalog does not expose one roving tab stop");
}
if (previewCalls.length !== 0 || state.reportFocusId !== null) {
  throw new Error(`missing exact session bound preview authority: ${previewCalls}/${state.reportFocusId}`);
}
acceptReportSessionForHarness("session-active");
await loadReports(caseGeneration, true);
cards = nodes["#report-list"].children;
if (
  previewCalls.join(",") !== "active-html"
  || state.activeReportId !== "active-html"
  || state.reportSelectionSource !== "auto"
  || state.reportFocusId !== "active-html"
) {
  throw new Error(`exact auto-selection failed: ${previewCalls}/${state.activeReportId}/${state.reportSelectionSource}`);
}
if (cards.some(card => card.focusCalls !== 0)) {
  throw new Error("automatic selection moved DOM focus");
}

await loadReports(caseGeneration, true);
if (previewCalls.length !== 1 || state.activeReportId !== "active-html") {
  throw new Error(`automatic selection repeated: ${previewCalls}`);
}

cards = nodes["#report-list"].children;
const manualCard = cards.find(card => card.dataset.reportId === "manual-report");
await manualCard.listeners.click();
if (
  previewCalls.join(",") !== "active-html,manual-report"
  || state.activeReportId !== "manual-report"
  || state.reportSelectionSource !== "manual"
) {
  throw new Error(`manual authority was not bound: ${previewCalls}/${state.activeReportId}/${state.reportSelectionSource}`);
}
await loadReports(caseGeneration, true);
if (previewCalls.length !== 2 || state.activeReportId !== "manual-report") {
  throw new Error(`existing manual selection was replaced: ${previewCalls}/${state.activeReportId}`);
}

catalog = {clients: [catalog.clients[0]]};
catalog.clients[0] = {
  ...catalog.clients[0],
  sessions: [catalog.clients[0].sessions[0]],
};
await loadReports(caseGeneration, true);
if (
  previewCalls.join(",") !== "active-html,manual-report"
  || state.activeReportId !== null
  || state.reportSelectionSource !== null
  || state.reportAutoSelectionKey !== `${caseGeneration}:session-active`
) {
  throw new Error(
    `disappeared manual authority or once-key was retained: `
    + `${previewCalls}/${state.activeReportId}/${state.reportAutoSelectionKey}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_pending_manual_preview_blocks_parallel_catalog_auto_selection() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-active",
    files: [
      {id: "auto-html", kind: "HTML", modified_at: "2026-07-31T12:00:00Z"},
      {id: "manual-json", kind: "JSON", modified_at: "2026-07-31T12:01:00Z"},
    ],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let catalogCalls = 0;
let resolveManual;
let resolveAuto;
const previewCalls = [];
window.MorphicWorkbenchApi = {
  async loadReports() { catalogCalls += 1; return catalog; },
  async loadReportPreview(reportId) {
    previewCalls.push(reportId);
    return new Promise(resolve => {
      if (reportId === "manual-json") resolveManual = resolve;
      else resolveAuto = resolve;
    });
  },
};

await loadReports(caseGeneration, true);
const manualCard = nodes["#report-list"].children.find(
  card => card.dataset.reportId === "manual-json"
);
const pendingManual = manualCard.listeners.click();
await waitUntil(() => typeof resolveManual === "function");
acceptReportSessionForHarness("session-active");
const pendingReload = loadReports(caseGeneration, true);
await waitUntil(() => catalogCalls === 2);
await Promise.resolve();
await Promise.resolve();
const autoStarted = previewCalls.includes("auto-html");

resolveManual({mode: "text", kind: "JSON", title: "manual", content: "manual", size: 6});
await pendingManual;
if (resolveAuto) {
  resolveAuto({mode: "text", kind: "HTML", title: "auto", content: "auto", size: 4});
}
await pendingReload;
if (
  autoStarted
  || previewCalls.join(",") !== "manual-json"
  || state.activeReportId !== "manual-json"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "manual-json"
  || nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `pending manual lost authority: ${previewCalls}/${state.activeReportId}/`
    + `${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_removed_pending_manual_preview_cannot_bind_or_enable_harmonization() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-manual",
    files: [{id: "manual-report", kind: "TXT", modified_at: "2026-07-31T12:00:00Z"}],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let resolveManual;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview() {
    return new Promise(resolve => { resolveManual = resolve; });
  },
};

await loadReports(caseGeneration, true);
const manualCard = nodes["#report-list"].children[0];
const pendingManual = manualCard.listeners.click();
await waitUntil(() => typeof resolveManual === "function");
catalog = {clients: []};
await loadReports(caseGeneration, true);
resolveManual({mode: "text", kind: "TXT", title: "removed", content: "removed", size: 7});
const outcome = await pendingManual;
if (
  outcome !== "stale"
  || state.activeReportId !== null
  || state.reportSelectionSource !== null
  || state.reportFocusId !== null
  || nodes["#report-list"].children.length !== 0
  || !nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `removed pending manual rebound: ${outcome}/${state.activeReportId}/`
    + `${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-list"].children.length}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_stale_overlapping_auto_does_not_consume_successful_auto_key() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-active",
    files: [{id: "auto-html", kind: "HTML", modified_at: "2026-07-31T12:00:00Z"}],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: "session-active",
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
acceptReportSessionForHarness("session-active");
let catalogCalls = 0;
let resolveSecondCatalog;
let resolveFirstPreview;
let previewCalls = 0;
window.MorphicWorkbenchApi = {
  async loadReports() {
    catalogCalls += 1;
    if (catalogCalls === 2) {
      return new Promise(resolve => { resolveSecondCatalog = resolve; });
    }
    return catalog;
  },
  async loadReportPreview() {
    previewCalls += 1;
    if (previewCalls === 1) {
      return new Promise(resolve => { resolveFirstPreview = resolve; });
    }
    return {mode: "text", kind: "HTML", title: "fresh", content: "fresh", size: 5};
  },
};

const firstLoad = loadReports(caseGeneration, true);
await waitUntil(() => typeof resolveFirstPreview === "function");
const secondLoad = loadReports(caseGeneration, true);
await waitUntil(() => typeof resolveSecondCatalog === "function");
resolveSecondCatalog(catalog);
await secondLoad;
resolveFirstPreview({mode: "text", kind: "HTML", title: "stale", content: "stale", size: 5});
await firstLoad;
await loadReports(caseGeneration, true);
const expectedKey = `${caseGeneration}:session-active`;
if (
  previewCalls !== 2
  || state.activeReportId !== "auto-html"
  || state.reportSelectionSource !== "auto"
  || state.reportFocusId !== "auto-html"
  || state.reportAutoSelectionKey !== expectedKey
) {
  throw new Error(
    `stale auto consumed key: ${previewCalls}/${state.activeReportId}/`
    + `${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${state.reportAutoSelectionKey}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_new_case_invalidates_pending_report_before_blocked_stop_await() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-a",
    files: [{id: "manual-report", kind: "TXT"}],
  }],
}]};
Object.assign(state, {
  activeJobId: null,
  scanRunActive: false,
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
  pendingMutations: 0,
  scanStartPending: false,
  resetInProgress: false,
});
let resolveManual;
let resolveStop;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview() {
    return new Promise(resolve => { resolveManual = resolve; });
  },
  async stopScanJob() {
    return new Promise(resolve => { resolveStop = resolve; });
  },
  async loadScanProfileCatalog(level) { return validCatalog(level); },
};

await loadReports(caseGeneration, true);
const pendingManual = nodes["#report-list"].children[0].listeners.click();
await waitUntil(() => typeof resolveManual === "function");
state.activeJobId = "scan-reset-report-race";
state.scanRunActive = true;
const previewTokenBeforeReset = reportAuthority.nextPreviewRequestId;
const catalogTokenBeforeReset = reportAuthority.nextCatalogRequestId;
const pendingReset = resetWorkbenchForNewCase();
await waitUntil(() => typeof resolveStop === "function");
const invalidatedSynchronously = (
  state.resetInProgress
  && reportAuthority.nextPreviewRequestId > previewTokenBeforeReset
  && reportAuthority.nextCatalogRequestId > catalogTokenBeforeReset
  && reportAuthority.pending === null
);
resolveManual({mode: "text", kind: "TXT", title: "late", content: "late", size: 4});
const manualOutcome = await pendingManual;
const stateDuringReset = {
  activeReportId: state.activeReportId,
  source: state.reportSelectionSource,
  focus: state.reportFocusId,
  harmonizationDisabled: nodes["#harmonization-start-button"].disabled,
};
resolveStop({status: "stopped"});
await pendingReset;
if (
  !invalidatedSynchronously
  || manualOutcome !== "stale"
  || stateDuringReset.activeReportId !== null
  || stateDuringReset.source !== null
  || stateDuringReset.focus !== null
  || !stateDuringReset.harmonizationDisabled
) {
  throw new Error(
    `reset report race escaped: ${invalidatedSynchronously}/${manualOutcome}/`
    + `${JSON.stringify(stateDuringReset)}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_successive_pending_manual_requests_restore_last_stable_active_preview() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-a",
    files: [
      {id: "report-a", kind: "TXT"},
      {id: "report-b", kind: "JSON"},
      {id: "report-c", kind: "PDF"},
    ],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let resolveB;
let resolveC;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview(reportId) {
    if (reportId === "report-a") {
      return {mode: "text", kind: "TXT", title: "A", content: "stable-preview-a", size: 16};
    }
    return new Promise(resolve => {
      if (reportId === "report-b") resolveB = resolve;
      else resolveC = resolve;
    });
  },
};

await loadReports(caseGeneration, true);
let cards = nodes["#report-list"].children;
await cards.find(card => card.dataset.reportId === "report-a").listeners.click();
const pendingB = cards.find(card => card.dataset.reportId === "report-b").listeners.click();
await waitUntil(() => typeof resolveB === "function");
const pendingC = cards.find(card => card.dataset.reportId === "report-c").listeners.click();
await waitUntil(() => typeof resolveC === "function");
if (
  state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-a"
) {
  throw new Error("successive pending requests changed stable A authority before success");
}

catalog = {clients: [{
  ...catalog.clients[0],
  sessions: [{
    ...catalog.clients[0].sessions[0],
    files: catalog.clients[0].sessions[0].files.filter(file => file.id !== "report-c"),
  }],
}]};
await loadReports(caseGeneration, true);
resolveB({mode: "text", kind: "JSON", title: "B", content: "preview-b", size: 9});
resolveC({mode: "file", kind: "PDF", title: "C", size: 10});
const [outcomeB, outcomeC] = await Promise.all([pendingB, pendingC]);
cards = nodes["#report-list"].children;
if (
  outcomeB !== "stale"
  || outcomeC !== "stale"
  || reportAuthority.pending !== null
  || state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-a"
  || nodes["#report-preview-panel"].dataset.state !== "ready"
  || nodes["#report-preview-text"].textContent !== "stable-preview-a"
  || nodes["#harmonization-start-button"].disabled
  || cards.find(card => card.dataset.reportId === "report-a")?.getAttribute("aria-pressed") !== "true"
) {
  throw new Error(
    `successive snapshot chain lost A: ${outcomeB}/${outcomeC}/`
    + `${reportAuthority.pending}/${state.activeReportId}/`
    + `${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-preview-panel"].dataset.state}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_aborted_new_case_restores_stable_active_preview_after_sync_invalidation() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-a",
    files: [
      {id: "report-a", kind: "TXT"},
      {id: "report-b", kind: "JSON"},
    ],
  }],
}]};
Object.assign(state, {
  activeJobId: null,
  scanRunActive: false,
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
  pendingMutations: 0,
  scanStartPending: false,
  resetInProgress: false,
});
let resolveB;
let rejectStop;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview(reportId) {
    if (reportId === "report-a") {
      return {mode: "text", kind: "TXT", title: "A", content: "stable-reset-a", size: 14};
    }
    return new Promise(resolve => { resolveB = resolve; });
  },
  async stopScanJob() {
    return new Promise((resolve, reject) => { rejectStop = reject; });
  },
};

await loadReports(caseGeneration, true);
const cards = nodes["#report-list"].children;
await cards.find(card => card.dataset.reportId === "report-a").listeners.click();
const pendingB = cards.find(card => card.dataset.reportId === "report-b").listeners.click();
await waitUntil(() => typeof resolveB === "function");
state.activeJobId = "scan-reset-abort";
state.scanRunActive = true;
const previewTokenBeforeReset = reportAuthority.nextPreviewRequestId;
const catalogTokenBeforeReset = reportAuthority.nextCatalogRequestId;
const pendingReset = resetWorkbenchForNewCase();
await waitUntil(() => typeof rejectStop === "function");
const invalidatedSynchronously = (
  state.resetInProgress
  && reportAuthority.nextPreviewRequestId > previewTokenBeforeReset
  && reportAuthority.nextCatalogRequestId > catalogTokenBeforeReset
  && reportAuthority.pending === null
);
resolveB({mode: "text", kind: "JSON", title: "B", content: "preview-b", size: 9});
const outcomeB = await pendingB;
rejectStop(new Error("controlled stop rejection"));
const resetOutcome = await pendingReset;
const activeCard = nodes["#report-list"].children.find(
  card => card.dataset.reportId === "report-a"
);
if (
  !invalidatedSynchronously
  || outcomeB !== "stale"
  || resetOutcome !== false
  || state.resetInProgress
  || reportAuthority.pending !== null
  || state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-a"
  || nodes["#report-preview-panel"].dataset.state !== "ready"
  || nodes["#report-preview-text"].textContent !== "stable-reset-a"
  || nodes["#harmonization-start-button"].disabled
  || activeCard?.getAttribute("aria-pressed") !== "true"
  || activeCard?.tabIndex !== 0
) {
  throw new Error(
    `aborted reset lost A: ${invalidatedSynchronously}/${outcomeB}/${resetOutcome}/`
    + `${state.resetInProgress}/${reportAuthority.pending}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-preview-panel"].dataset.state}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#harmonization-start-button"].disabled}/`
    + `${activeCard?.getAttribute("aria-pressed")}/${activeCard?.tabIndex}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_removed_pending_report_restores_existing_active_preview() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-a",
    files: [
      {id: "report-a", kind: "TXT"},
      {id: "report-b", kind: "JSON"},
    ],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let resolveB;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview(reportId) {
    if (reportId === "report-a") {
      return {mode: "text", kind: "TXT", title: "A", content: "preview-a", size: 9};
    }
    return new Promise(resolve => { resolveB = resolve; });
  },
};

await loadReports(caseGeneration, true);
let cards = nodes["#report-list"].children;
await cards.find(card => card.dataset.reportId === "report-a").listeners.click();
const pendingB = cards.find(card => card.dataset.reportId === "report-b").listeners.click();
await waitUntil(() => typeof resolveB === "function");
if (
  state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-a"
) {
  throw new Error("pending B changed successful A authority before success");
}
catalog = {clients: [{
  ...catalog.clients[0],
  sessions: [{...catalog.clients[0].sessions[0], files: [catalog.clients[0].sessions[0].files[0]]}],
}]};
await loadReports(caseGeneration, true);
resolveB({mode: "text", kind: "JSON", title: "B", content: "preview-b", size: 9});
const outcomeB = await pendingB;
if (
  outcomeB !== "stale"
  || reportAuthority.pending !== null
  || state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-a"
  || nodes["#harmonization-start-button"].disabled
  || nodes["#report-preview-panel"].dataset.state === "loading"
  || nodes["#report-preview-text"].textContent !== "preview-a"
) {
  throw new Error(
    `removed B did not restore A: ${outcomeB}/${reportAuthority.pending}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#harmonization-start-button"].disabled}/`
    + `${nodes["#report-preview-panel"].dataset.state}/`
    + `${nodes["#report-preview-text"].textContent}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_authoritative_preview_failure_keeps_one_roving_tabstop() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-a",
    files: [
      {id: "report-first", kind: "TXT"},
      {id: "report-second", kind: "JSON"},
    ],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview() { throw new Error("authoritative preview failure"); },
};

await loadReports(caseGeneration, true);
const outcome = await nodes["#report-list"].children[0].listeners.click();
const cards = nodes["#report-list"].children;
if (
  outcome !== "failure"
  || reportAuthority.pending !== null
  || state.activeReportId !== null
  || state.reportSelectionSource !== null
  || state.reportFocusId !== null
  || cards.filter(card => card.tabIndex === 0).length !== 1
  || cards[0].tabIndex !== 0
  || cards.some(card => card.getAttribute("aria-pressed") !== "false")
) {
  throw new Error(
    `failure broke roving tabstop: ${outcome}/${reportAuthority.pending}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${cards.map(card => card.tabIndex)}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_authoritative_auto_failure_consumes_once_key_but_stale_does_not() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-active",
    files: [{id: "auto-html", kind: "HTML"}],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: "session-active",
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
acceptReportSessionForHarness("session-active");
let previewCalls = 0;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview() {
    previewCalls += 1;
    throw new Error("authoritative auto failure");
  },
};
await loadReports(caseGeneration, true);
await loadReports(caseGeneration, true);
const expectedKey = `${caseGeneration}:session-active`;
if (
  previewCalls !== 1
  || state.reportAutoSelectionKey !== expectedKey
  || state.activeReportId !== null
  || state.reportSelectionSource !== null
  || state.reportFocusId !== null
) {
  throw new Error(
    `authoritative auto failure retried: ${previewCalls}/${state.reportAutoSelectionKey}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}`
  );
}

Object.assign(state, {
  reportAutoSelectionKey: null,
  activeReportId: null,
  reportSelectionSource: null,
  reportFocusId: null,
});
reportAuthority = createReportAuthorityState(caseGeneration);
projectReportAuthority(reportAuthority);
state.activeReportSessionId = "session-active";
acceptReportSessionForHarness("session-active");
let resolveStale;
previewCalls = 0;
window.MorphicWorkbenchApi.loadReportPreview = async () => {
  previewCalls += 1;
  return new Promise(resolve => { resolveStale = resolve; });
};
const staleLoad = loadReports(caseGeneration, true);
await waitUntil(() => typeof resolveStale === "function");
caseGeneration += 1;
resolveStale({mode: "text", kind: "HTML", title: "stale", content: "stale", size: 5});
await staleLoad;
if (state.reportAutoSelectionKey !== null || state.activeReportId !== null) {
  throw new Error(`stale auto consumed key: ${state.reportAutoSelectionKey}/${state.activeReportId}`);
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_failed_or_catalog_stale_auto_restores_existing_stable_preview() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let catalog = {clients: [{
  client_id: "client-a",
  sessions: [
    {session_id: "session-a", files: [{id: "report-a", kind: "HTML"}]},
    {session_id: "session-b", files: [{id: "report-b", kind: "HTML"}]},
    {session_id: "session-c", files: [{id: "report-c", kind: "HTML"}]},
  ],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: "session-a",
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
acceptReportSessionForHarness("session-a");
let resolveC;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview(reportId) {
    if (reportId === "report-a") {
      return {mode: "text", kind: "HTML", title: "A", content: "stable-auto-a", size: 13};
    }
    if (reportId === "report-b") throw new Error("authoritative B failure");
    return new Promise(resolve => { resolveC = resolve; });
  },
};

await loadReports(caseGeneration, true);
acceptReportSessionForHarness("session-b");
await loadReports(caseGeneration, true);
if (
  state.activeReportId !== "report-a"
  || nodes["#report-preview-panel"].dataset.state !== "ready"
  || nodes["#report-preview-text"].textContent !== "stable-auto-a"
  || nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `authoritative auto failure lost A: ${state.activeReportId}/`
    + `${nodes["#report-preview-panel"].dataset.state}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}

acceptReportSessionForHarness("session-c");
const staleAuto = loadReports(caseGeneration, true);
await waitUntil(() => typeof resolveC === "function");
acceptReportSessionForHarness("session-missing");
await loadReports(caseGeneration, true);
resolveC({mode: "text", kind: "HTML", title: "C", content: "preview-c", size: 9});
await staleAuto;
if (
  state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "auto"
  || state.reportFocusId !== "report-a"
  || nodes["#report-preview-panel"].dataset.state !== "ready"
  || nodes["#report-preview-text"].textContent !== "stable-auto-a"
  || nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `catalog-stale auto lost A: ${state.activeReportId}/${state.reportSelectionSource}/`
    + `${state.reportFocusId}/${nodes["#report-preview-panel"].dataset.state}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_old_auto_fingerprint_drift_cannot_block_new_exact_session_candidate() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let reportA = {
  id: "report-a",
  kind: "HTML",
  modified_at: "2026-08-01T10:00:00Z",
  size: 10,
};
const reportC = {
  id: "report-c",
  kind: "HTML",
  modified_at: "2026-08-01T10:00:00Z",
  size: 30,
};
const catalogPayload = () => ({clients: [{
  client_id: "client-a",
  sessions: [
    {session_id: "session-a", files: [{...reportA}]},
    {session_id: "session-b", files: [{...reportC}]},
  ],
}]});
const previewCalls = [];
window.MorphicWorkbenchApi = {
  async loadScanResults(jobId) {
    return {report_session_id: jobId === "scan-a" ? "session-a" : "session-b"};
  },
  async loadRunTrace(jobId) { return {job_id: jobId, status: "completed"}; },
  async loadReports() { return catalogPayload(); },
  async loadReportPreview(reportId) {
    previewCalls.push(reportId);
    return {
      mode: "text",
      kind: "HTML",
      title: reportId,
      content: `preview-${reportId}`,
      size: reportId === "report-a" ? reportA.size : reportC.size,
    };
  },
};

state.activeJobId = "scan-a";
state.scanRunActive = true;
const acceptedA = await loadScanResults("scan-a", caseGeneration, true);
if (!acceptedA || state.activeReportSessionId !== "session-a") {
  throw new Error(`session A was not accepted: ${acceptedA}/${state.activeReportSessionId}`);
}
await loadReports(caseGeneration, true);
if (
  previewCalls.join(",") !== "report-a"
  || state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "auto"
) {
  throw new Error(
    `initial session A auto-preview failed: ${previewCalls}/${state.activeReportId}/`
    + `${state.reportSelectionSource}`
  );
}

state.activeJobId = "scan-b";
const acceptedB = await loadScanResults("scan-b", caseGeneration, true);
if (!acceptedB || state.activeReportSessionId !== "session-b") {
  throw new Error(`session B was not accepted: ${acceptedB}/${state.activeReportSessionId}`);
}
reportA = {
  ...reportA,
  modified_at: "2026-08-01T10:01:00Z",
  size: 20,
};
await loadReports(caseGeneration, true);

let cards = nodes["#report-list"].children;
let pressedCards = cards.filter(card => card.getAttribute("aria-pressed") === "true");
let tabStops = cards.filter(card => card.tabIndex === 0);
if (
  previewCalls.join(",") !== "report-a,report-c"
  || state.activeReportId !== "report-c"
  || state.reportSelectionSource !== "auto"
  || state.reportFocusId !== "report-c"
  || nodes["#report-preview-panel"].dataset.state !== "ready"
  || pressedCards.length !== 1
  || pressedCards[0]?.dataset.reportId !== "report-c"
  || tabStops.length !== 1
  || tabStops[0]?.dataset.reportId !== "report-c"
  || nodes["#report-preview-text"].textContent !== "preview-report-c"
  || !nodes["#report-preview-title"].textContent.includes("report-c")
  || nodes["#report-open-link"].hidden
  || !nodes["#report-open-link"].href.endsWith("/api/reports/report-c/file")
) {
  throw new Error(
    `old auto fingerprint drift blocked exact session candidate: ${previewCalls}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-preview-panel"].dataset.state}/`
    + `${pressedCards.map(card => card.dataset.reportId)}/`
    + `${tabStops.map(card => card.dataset.reportId)}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#report-preview-title"].textContent}/`
    + `${nodes["#report-open-link"].hidden}/${nodes["#report-open-link"].href}`
  );
}

await loadReports(caseGeneration, true);
cards = nodes["#report-list"].children;
pressedCards = cards.filter(card => card.getAttribute("aria-pressed") === "true");
tabStops = cards.filter(card => card.tabIndex === 0);
if (
  previewCalls.join(",") !== "report-a,report-c"
  || state.activeReportId !== "report-c"
  || state.reportSelectionSource !== "auto"
  || state.reportFocusId !== "report-c"
  || nodes["#report-preview-panel"].dataset.state !== "ready"
  || pressedCards.length !== 1
  || pressedCards[0]?.dataset.reportId !== "report-c"
  || tabStops.length !== 1
  || tabStops[0]?.dataset.reportId !== "report-c"
  || nodes["#report-preview-text"].textContent !== "preview-report-c"
  || !nodes["#report-preview-title"].textContent.includes("report-c")
  || nodes["#report-open-link"].hidden
  || !nodes["#report-open-link"].href.endsWith("/api/reports/report-c/file")
) {
  throw new Error(
    `unchanged catalog did not retain visible C authority: ${previewCalls}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-preview-panel"].dataset.state}/`
    + `${pressedCards.map(card => card.dataset.reportId)}/`
    + `${tabStops.map(card => card.dataset.reportId)}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#report-preview-title"].textContent}/`
    + `${nodes["#report-open-link"].hidden}/${nodes["#report-open-link"].href}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_auto_preview_is_stale_after_active_report_session_changes() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-a",
    files: [{id: "report-a", kind: "HTML", modified_at: "2026-08-01T10:00:00Z"}],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: "session-a",
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
acceptReportSessionForHarness("session-a");
let resolveAuto;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview() {
    return new Promise(resolve => { resolveAuto = resolve; });
  },
};

const pendingLoad = loadReports(caseGeneration, true);
await waitUntil(() => typeof resolveAuto === "function");
acceptReportSessionForHarness("session-b");
resolveAuto({mode: "text", kind: "HTML", title: "A", content: "stale-a", size: 7});
await pendingLoad;
if (
  state.activeReportId !== null
  || state.reportSelectionSource !== null
  || state.reportFocusId !== null
  || state.reportAutoSelectionKey !== null
  || !nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `session-stale auto bound: ${state.activeReportId}/${state.reportSelectionSource}/`
    + `${state.reportFocusId}/${state.reportAutoSelectionKey}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_catalog_drift_without_refresh_disables_harmonization_from_authority() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let reportA = {
  id: "report-a", kind: "HTML", modified_at: "2026-08-01T10:00:00Z", size: 10,
};
const catalogPayload = () => ({clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: [{...reportA}]}],
}]});
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
acceptReportSessionForHarness("session-a");
window.MorphicWorkbenchApi = {
  async loadReports() { return catalogPayload(); },
  async loadReportPreview() {
    return {mode: "text", kind: "HTML", title: "A", content: "stable-a", size: reportA.size};
  },
};

await loadReports(caseGeneration, true);
if (state.activeReportId !== "report-a" || nodes["#harmonization-start-button"].disabled) {
  throw new Error(
    `baseline auto stable not eligible: ${state.activeReportId}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
acceptReportSessionForHarness("session-missing");
reportA = {...reportA, modified_at: "2026-08-01T10:01:00Z", size: 20};
await loadReports(caseGeneration, true);
if (!nodes["#harmonization-start-button"].disabled || reportAuthority.canHarmonize) {
  throw new Error(
    `drifted stale stable left harmonization enabled: `
    + `${nodes["#harmonization-start-button"].disabled}/${reportAuthority.canHarmonize}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_aborted_reset_without_stable_preview_restores_neutral_catalog_state() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: [{id: "report-a", kind: "TXT"}]}],
}]};
Object.assign(state, {
  activeJobId: null,
  scanRunActive: false,
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
  pendingMutations: 0,
  scanStartPending: false,
  resetInProgress: false,
});
let resolveManual;
let rejectStop;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview() {
    return new Promise(resolve => { resolveManual = resolve; });
  },
  async stopScanJob() {
    return new Promise((resolve, reject) => { rejectStop = reject; });
  },
};

await loadReports(caseGeneration, true);
const pendingManual = nodes["#report-list"].children[0].listeners.click();
await waitUntil(() => typeof resolveManual === "function");
state.activeJobId = "scan-reset-no-stable";
state.scanRunActive = true;
const pendingReset = resetWorkbenchForNewCase();
await waitUntil(() => typeof rejectStop === "function");
resolveManual({mode: "text", kind: "TXT", title: "late", content: "late", size: 4});
const manualOutcome = await pendingManual;
rejectStop(new Error("controlled reset abort without stable preview"));
const resetOutcome = await pendingReset;
const cards = nodes["#report-list"].children;
if (
  manualOutcome !== "stale"
  || resetOutcome !== false
  || state.resetInProgress
  || reportAuthority.pending !== null
  || state.activeReportId !== null
  || state.reportSelectionSource !== null
  || state.reportFocusId !== null
  || nodes["#report-preview-panel"].dataset.state === "loading"
  || nodes["#report-preview-text"].textContent.includes("geladen")
  || !nodes["#harmonization-start-button"].disabled
  || cards.filter(card => card.tabIndex === 0).length !== 1
  || cards.some(card => card.getAttribute("aria-pressed") !== "false")
) {
  throw new Error(
    `aborted reset lacked neutral fallback: ${manualOutcome}/${resetOutcome}/`
    + `${state.resetInProgress}/${reportAuthority.pending}/${state.activeReportId}/`
    + `${nodes["#report-preview-panel"].dataset.state}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#harmonization-start-button"].disabled}/${cards.map(card => card.tabIndex)}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_reset_abort_with_deferred_refresh_never_enables_harmonization_without_current_stable_preview() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let reportA = {
  id: "report-a",
  kind: "TXT",
  modified_at: "2026-08-01T10:00:00Z",
  size: 10,
};
const reportB = {
  id: "report-b",
  kind: "JSON",
  modified_at: "2026-08-01T10:00:00Z",
  size: 8,
};
const catalogPayload = () => ({clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: [{...reportA}, {...reportB}]}],
}]});
let resolveB;
let rejectStop;
let callsA = 0;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalogPayload(); },
  async loadReportPreview(reportId) {
    if (reportId === "report-a") {
      callsA += 1;
      return {
        mode: "text",
        kind: "TXT",
        title: "A",
        content: `stable-a-v${callsA}`,
        size: reportA.size,
      };
    }
    return new Promise(resolve => { resolveB = resolve; });
  },
  async stopScanJob() {
    return new Promise((resolve, reject) => { rejectStop = reject; });
  },
};

await loadReports(caseGeneration, true);
let cards = nodes["#report-list"].children;
const outcomeA = await cards.find(
  card => card.dataset.reportId === "report-a"
).listeners.click();
if (
  outcomeA !== REPORT_PREVIEW_OUTCOME.SUCCESS
  || callsA !== 1
  || state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || nodes["#report-preview-text"].textContent !== "stable-a-v1"
) {
  throw new Error(
    `stable A preview was not established: ${outcomeA}/${callsA}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/`
    + `${nodes["#report-preview-text"].textContent}`
  );
}

cards = nodes["#report-list"].children;
const pendingB = cards.find(
  card => card.dataset.reportId === "report-b"
).listeners.click();
await waitUntil(() => typeof resolveB === "function");
reportA = {
  ...reportA,
  modified_at: "2026-08-01T10:01:00Z",
  size: 20,
};
await loadReports(caseGeneration, true);
if (callsA !== 1) {
  throw new Error(`A-v2 refresh was not deferred behind pending B: ${callsA}`);
}

Object.assign(state, {
  activeJobId: "scan-reset-deferred-refresh",
  scanRunActive: true,
  pendingMutations: 0,
  scanStartPending: false,
  resetInProgress: false,
});
const pendingReset = resetWorkbenchForNewCase();
await waitUntil(() => typeof rejectStop === "function");
resolveB({mode: "text", kind: "JSON", title: "B", content: "preview-b", size: 8});
const outcomeB = await pendingB;
rejectStop(new Error("controlled stop rejection"));
const resetOutcome = await pendingReset;

cards = nodes["#report-list"].children;
let pressedCards = cards.filter(card => card.getAttribute("aria-pressed") === "true");
let tabStops = cards.filter(card => card.tabIndex === 0);
if (
  resetOutcome !== false
  || outcomeB !== REPORT_PREVIEW_OUTCOME.STALE
  || callsA !== 1
  || nodes["#report-preview-panel"].dataset.state !== "ready"
  || state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-a"
  || nodes["#report-preview-text"].textContent !== "stable-a-v1"
  || pressedCards.length !== 1
  || pressedCards[0]?.dataset.reportId !== "report-a"
  || tabStops.length !== 1
  || tabStops[0]?.dataset.reportId !== "report-a"
  || nodes["#harmonization-start-button"].disabled !== true
) {
  throw new Error(
    `reset abort did not restore coherent outdated A-v1: ${resetOutcome}/${outcomeB}/`
    + `${callsA}/${nodes["#report-preview-panel"].dataset.state}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${pressedCards.map(card => card.dataset.reportId)}/`
    + `${tabStops.map(card => card.dataset.reportId)}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}

await loadReports(caseGeneration, true);
cards = nodes["#report-list"].children;
pressedCards = cards.filter(card => card.getAttribute("aria-pressed") === "true");
tabStops = cards.filter(card => card.tabIndex === 0);
if (
  callsA !== 2
  || nodes["#report-preview-panel"].dataset.state !== "ready"
  || state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-a"
  || nodes["#report-preview-text"].textContent !== "stable-a-v2"
  || pressedCards.length !== 1
  || pressedCards[0]?.dataset.reportId !== "report-a"
  || tabStops.length !== 1
  || tabStops[0]?.dataset.reportId !== "report-a"
  || nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `required A-v2 refresh did not restore current authority: ${callsA}/`
    + `${nodes["#report-preview-panel"].dataset.state}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${pressedCards.map(card => card.dataset.reportId)}/`
    + `${tabStops.map(card => card.dataset.reportId)}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}

await loadReports(caseGeneration, true);
cards = nodes["#report-list"].children;
pressedCards = cards.filter(card => card.getAttribute("aria-pressed") === "true");
tabStops = cards.filter(card => card.tabIndex === 0);
if (
  callsA !== 2
  || nodes["#report-preview-panel"].dataset.state !== "ready"
  || state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-a"
  || nodes["#report-preview-text"].textContent !== "stable-a-v2"
  || pressedCards.length !== 1
  || pressedCards[0]?.dataset.reportId !== "report-a"
  || tabStops.length !== 1
  || tabStops[0]?.dataset.reportId !== "report-a"
  || nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `unchanged catalog repeated A refresh or lost authority: ${callsA}/`
    + `${nodes["#report-preview-panel"].dataset.state}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${pressedCards.map(card => card.dataset.reportId)}/`
    + `${tabStops.map(card => card.dataset.reportId)}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)

    mutated = _run_app_script(body, mutate_harmonization_eligibility=True)
    assert mutated.returncode != 0
    assert "reset abort did not restore coherent outdated A-v1" in mutated.stderr


def test_same_report_id_reloads_only_when_catalog_version_changes() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let file = {
  id: "report-r",
  kind: "TXT",
  file_name: "report.txt",
  relative_path: "session/report.txt",
  modified_at: "2026-08-01T10:00:00Z",
  size: 10,
};
const catalogPayload = () => ({clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: [{...file}]}],
}]});
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let previewCalls = 0;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalogPayload(); },
  async loadReportPreview() {
    previewCalls += 1;
    return {
      mode: "text",
      kind: file.kind,
      title: file.file_name,
      content: `version-${previewCalls}`,
      modified_at: file.modified_at,
      size: file.size,
    };
  },
};

await loadReports(caseGeneration, true);
await nodes["#report-list"].children[0].listeners.click();
await loadReports(caseGeneration, true);
if (previewCalls !== 1 || nodes["#report-preview-text"].textContent !== "version-1") {
  throw new Error(`unchanged report reloaded: ${previewCalls}`);
}
file = {
  ...file,
  relative_path: "session/report-v2.txt",
  modified_at: "2026-08-01T10:01:00Z",
  size: 20,
};
await loadReports(caseGeneration, true);
if (
  previewCalls !== 2
  || state.activeReportId !== "report-r"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-r"
  || nodes["#report-preview-text"].textContent !== "version-2"
  || nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `changed report version not rebound: ${previewCalls}/${state.activeReportId}/`
    + `${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-preview-text"].textContent}`
  );
}
await loadReports(caseGeneration, true);
if (previewCalls !== 2) {
  throw new Error(`current report version entered reload loop: ${previewCalls}`);
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_pending_manual_intent_defers_active_fingerprint_refresh_and_wins_on_success() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let reportA = {
  id: "report-a", kind: "TXT", modified_at: "2026-08-01T10:00:00Z", size: 10,
};
const reportB = {
  id: "report-b", kind: "JSON", modified_at: "2026-08-01T10:00:00Z", size: 8,
};
const catalogPayload = () => ({clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: [{...reportA}, {...reportB}]}],
}]});
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let resolveB;
let callsA = 0;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalogPayload(); },
  async loadReportPreview(reportId) {
    if (reportId === "report-a") {
      callsA += 1;
      return {mode: "text", kind: "TXT", title: "A", content: `a-${callsA}`, size: reportA.size};
    }
    return new Promise(resolve => { resolveB = resolve; });
  },
};

await loadReports(caseGeneration, true);
let cards = nodes["#report-list"].children;
await cards.find(card => card.dataset.reportId === "report-a").listeners.click();
const pendingB = cards.find(card => card.dataset.reportId === "report-b").listeners.click();
await waitUntil(() => typeof resolveB === "function");
const previewTokenBeforeRefresh = reportAuthority.nextPreviewRequestId;
const pendingAuthorityBeforeRefresh = reportAuthority.pending;
reportA = {...reportA, modified_at: "2026-08-01T10:01:00Z", size: 20};
await loadReports(caseGeneration, true);
const preservedPending = (
  reportAuthority.nextPreviewRequestId === previewTokenBeforeRefresh
  && reportAuthority.pending === pendingAuthorityBeforeRefresh
  && reportAuthority.pending?.reportId === "report-b"
  && callsA === 1
  && nodes["#harmonization-start-button"].disabled
);
resolveB({mode: "text", kind: "JSON", title: "B", content: "b-success", size: 8});
const outcomeB = await pendingB;
if (
  !preservedPending
  || outcomeB !== "success"
  || state.activeReportId !== "report-b"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-b"
  || callsA !== 1
  || nodes["#report-preview-text"].textContent !== "b-success"
  || nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `pending B lost to background A refresh: ${preservedPending}/${outcomeB}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${callsA}/${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_failed_pending_manual_runs_deferred_latest_active_fingerprint_refresh() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let reportA = {
  id: "report-a", kind: "TXT", modified_at: "2026-08-01T10:00:00Z", size: 10,
};
const reportB = {
  id: "report-b", kind: "JSON", modified_at: "2026-08-01T10:00:00Z", size: 8,
};
const catalogPayload = () => ({clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: [{...reportA}, {...reportB}]}],
}]});
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let rejectB;
let callsA = 0;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalogPayload(); },
  async loadReportPreview(reportId) {
    if (reportId === "report-a") {
      callsA += 1;
      return {
        mode: "text", kind: "TXT", title: "A", content: `a-${callsA}`,
        modified_at: reportA.modified_at, size: reportA.size,
      };
    }
    return new Promise((resolve, reject) => { rejectB = reject; });
  },
};

await loadReports(caseGeneration, true);
let cards = nodes["#report-list"].children;
await cards.find(card => card.dataset.reportId === "report-a").listeners.click();
const pendingB = cards.find(card => card.dataset.reportId === "report-b").listeners.click();
await waitUntil(() => typeof rejectB === "function");
reportA = {...reportA, modified_at: "2026-08-01T10:02:00Z", size: 30};
await loadReports(caseGeneration, true);
if (callsA !== 1 || reportAuthority.pending?.reportId !== "report-b") {
  throw new Error(`A refresh was not deferred behind B: ${callsA}/${reportAuthority.pending?.reportId}`);
}
rejectB(new Error("controlled B failure"));
const outcomeB = await pendingB;
if (
  outcomeB !== "failure"
  || reportAuthority.pending !== null
  || callsA !== 2
  || state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-a"
  || nodes["#report-preview-text"].textContent !== "a-2"
  || nodes["#harmonization-start-button"].disabled
  || reportAuthority.stable?.entryFingerprint
    !== reportEntryFingerprint(reportAuthority.entriesById.get("report-a"))
) {
  throw new Error(
    `deferred A refresh did not recover after B failure: ${outcomeB}/`
    + `${reportAuthority.pending}/${callsA}/${state.activeReportId}/`
    + `${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_deferred_active_refresh_is_discarded_when_active_report_disappears() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let files = [
  {id: "report-a", kind: "TXT", modified_at: "2026-08-01T10:00:00Z", size: 10},
  {id: "report-b", kind: "JSON", modified_at: "2026-08-01T10:00:00Z", size: 8},
];
const catalogPayload = () => ({clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: files.map(file => ({...file}))}],
}]});
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let resolveB;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalogPayload(); },
  async loadReportPreview(reportId) {
    if (reportId === "report-a") {
      return {mode: "text", kind: "TXT", title: "A", content: "a", size: 10};
    }
    return new Promise(resolve => { resolveB = resolve; });
  },
};

await loadReports(caseGeneration, true);
let cards = nodes["#report-list"].children;
await cards.find(card => card.dataset.reportId === "report-a").listeners.click();
const pendingB = cards.find(card => card.dataset.reportId === "report-b").listeners.click();
await waitUntil(() => typeof resolveB === "function");
files = [
  {...files[0], modified_at: "2026-08-01T10:01:00Z", size: 20},
  files[1],
];
await loadReports(caseGeneration, true);
if (reportAuthority.deferredRefresh?.reportId !== "report-a") {
  throw new Error("changed A was not deferred behind pending B");
}
files = [files[1]];
await loadReports(caseGeneration, true);
if (reportAuthority.deferredRefresh !== null) {
  throw new Error(`removed A retained deferred refresh: ${reportAuthority.deferredRefresh.reportId}`);
}
resolveB({mode: "text", kind: "JSON", title: "B", content: "b", size: 8});
await pendingB;
if (reportAuthority.deferredRefresh !== null) {
  throw new Error(`removed A retained deferred refresh: ${reportAuthority.deferredRefresh.reportId}`);
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_newer_active_fingerprint_refresh_supersedes_older_without_clearing_selection() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let reportA = {
  id: "report-a", kind: "TXT", modified_at: "2026-08-01T10:00:00Z", size: 10,
};
const catalogPayload = () => ({clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: [{...reportA}]}],
}]});
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let callsA = 0;
let resolveV2;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalogPayload(); },
  async loadReportPreview() {
    callsA += 1;
    if (callsA === 1) {
      return {mode: "text", kind: "TXT", title: "A", content: "a-v1", size: 10};
    }
    if (callsA === 2) {
      return new Promise(resolve => { resolveV2 = resolve; });
    }
    return {mode: "text", kind: "TXT", title: "A", content: "a-v3", size: 30};
  },
};

await loadReports(caseGeneration, true);
await nodes["#report-list"].children[0].listeners.click();
reportA = {...reportA, modified_at: "2026-08-01T10:01:00Z", size: 20};
const refreshV2 = loadReports(caseGeneration, true);
await waitUntil(() => typeof resolveV2 === "function");
const stateDuringV2 = {
  active: state.activeReportId,
  source: state.reportSelectionSource,
  focus: state.reportFocusId,
  harmonizationDisabled: nodes["#harmonization-start-button"].disabled,
};
reportA = {...reportA, modified_at: "2026-08-01T10:02:00Z", size: 30};
const refreshV3 = loadReports(caseGeneration, true);
await refreshV3;
resolveV2({mode: "text", kind: "TXT", title: "A", content: "a-v2", size: 20});
await refreshV2;
if (
  stateDuringV2.active !== "report-a"
  || stateDuringV2.source !== "manual"
  || stateDuringV2.focus !== "report-a"
  || !stateDuringV2.harmonizationDisabled
  || callsA !== 3
  || state.activeReportId !== "report-a"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-a"
  || nodes["#report-preview-text"].textContent !== "a-v3"
  || nodes["#harmonization-start-button"].disabled
  || reportAuthority.stable?.entryFingerprint
    !== reportEntryFingerprint(reportAuthority.entriesById.get("report-a"))
) {
  throw new Error(
    `v3 did not supersede v2: ${JSON.stringify(stateDuringV2)}/${callsA}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_duplicate_report_ids_are_deduplicated_before_ranking_and_rendering() -> None:
    body = r"""
const clients = [{
  client_id: "client-first",
  sessions: [{
    session_id: "session-first",
    files: [{id: "duplicate-id", kind: "HTML", modified_at: "2026-08-01T10:00:00Z"}],
  }],
}, {
  client_id: "client-second",
  sessions: [{
    session_id: "session-second",
    files: [{id: "duplicate-id", kind: "HTML", modified_at: "2026-08-01T11:00:00Z"}],
  }],
}];
const entries = flattenReportEntries(clients);
const firstCandidate = automaticReportCandidate(entries, "session-first");
const secondCandidate = automaticReportCandidate(entries, "session-second");
const state = window.MorphicWorkbenchState;
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: "session-first",
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
window.MorphicWorkbenchApi = {
  async loadReports() { return {clients}; },
  async loadReportPreview() {
    return {mode: "text", kind: "HTML", title: "first", content: "first", size: 5};
  },
};
await loadReports(caseGeneration, true);
const cards = nodes["#report-list"].children;
if (
  entries.length !== 1
  || entries[0].client_id !== "client-first"
  || firstCandidate?.id !== "duplicate-id"
  || secondCandidate !== null
  || cards.length !== 1
  || cards.filter(card => card.tabIndex === 0).length !== 1
  || cards.filter(card => card.getAttribute("aria-pressed") === "true").length > 1
) {
  throw new Error(
    `duplicate IDs escaped fail-closed flattening: ${entries.length}/`
    + `${entries.map(entry => `${entry.client_id}:${entry.session_id}`)}/`
    + `${firstCandidate?.id}/${secondCandidate?.id}/${cards.length}/`
    + `${cards.map(card => card.tabIndex)}/`
    + `${cards.map(card => card.getAttribute("aria-pressed"))}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_successive_manual_previews_bind_only_latest_and_clear_pending_authority() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{
    session_id: "session-a",
    files: [
      {id: "report-first", kind: "TXT"},
      {id: "report-second", kind: "JSON"},
    ],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let resolveFirst;
let resolveSecond;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview(reportId) {
    return new Promise(resolve => {
      if (reportId === "report-first") resolveFirst = resolve;
      else resolveSecond = resolve;
    });
  },
};

await loadReports(caseGeneration, true);
const cards = nodes["#report-list"].children;
const first = cards[0].listeners.click();
await waitUntil(() => typeof resolveFirst === "function");
const second = cards[1].listeners.click();
await waitUntil(() => typeof resolveSecond === "function");
if (
  state.activeReportId !== null
  || state.reportSelectionSource !== null
  || state.reportFocusId !== null
  || reportAuthority.pending?.reportId !== "report-second"
) {
  throw new Error("manual state was bound before successful latest preview");
}
resolveFirst({mode: "text", kind: "TXT", title: "first", content: "first", size: 5});
const firstOutcome = await first;
if (
  firstOutcome !== "stale"
  || state.activeReportId !== null
  || reportAuthority.pending?.reportId !== "report-second"
) {
  throw new Error(`older manual rebound: ${firstOutcome}/${state.activeReportId}`);
}
resolveSecond({mode: "text", kind: "JSON", title: "second", content: "second", size: 6});
const secondOutcome = await second;
if (
  secondOutcome !== "success"
  || reportAuthority.pending !== null
  || state.activeReportId !== "report-second"
  || state.reportSelectionSource !== "manual"
  || state.reportFocusId !== "report-second"
) {
  throw new Error(
    `latest manual did not bind: ${secondOutcome}/${reportAuthority.pending}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_stale_generation_manual_preview_clears_pending_without_binding() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: [{id: "manual-report", kind: "TXT"}]}],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let resolveManual;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview() {
    return new Promise(resolve => { resolveManual = resolve; });
  },
};

await loadReports(caseGeneration, true);
const pending = nodes["#report-list"].children[0].listeners.click();
await waitUntil(() => typeof resolveManual === "function");
caseGeneration += 1;
resolveManual({mode: "text", kind: "TXT", title: "stale", content: "stale", size: 5});
const outcome = await pending;
if (
  outcome !== "stale"
  || reportAuthority.pending !== null
  || state.activeReportId !== null
  || state.reportSelectionSource !== null
  || state.reportFocusId !== null
  || !nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `stale generation bound manual: ${outcome}/${reportAuthority.pending}/`
    + `${state.activeReportId}/${state.reportSelectionSource}/${state.reportFocusId}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_report_preview_races_cannot_override_manual_or_newer_catalog() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  label: "Klient A",
  sessions: [{
    session_id: "session-active",
    label: "Session aktiv",
    files: [
      {id: "auto-html", kind: "HTML", file_name: "Auto.html", modified_at: "2026-07-31T12:01:00Z"},
      {id: "manual-json", kind: "JSON", file_name: "Manual.json", modified_at: "2026-07-31T12:02:00Z"},
    ],
  }],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: "session-active",
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
acceptReportSessionForHarness("session-active");
let resolveAuto;
let resolveManual;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview(reportId) {
    return new Promise(resolve => {
      if (reportId === "auto-html") resolveAuto = resolve;
      else resolveManual = resolve;
    });
  },
};

const pendingCatalog = loadReports(caseGeneration, true);
await waitUntil(() => typeof resolveAuto === "function");
const manualCard = nodes["#report-list"].children.find(
  card => card.dataset.reportId === "manual-json"
);
const pendingManual = manualCard.listeners.click();
await waitUntil(() => typeof resolveManual === "function");
resolveManual({mode: "text", kind: "JSON", title: "manual", content: "manual", size: 6});
await pendingManual;
resolveAuto({mode: "text", kind: "HTML", title: "auto", content: "auto", size: 4});
await pendingCatalog;
if (state.activeReportId !== "manual-json" || state.reportSelectionSource !== "manual") {
  throw new Error(`late auto preview replaced manual authority: ${state.activeReportId}/${state.reportSelectionSource}`);
}

Object.assign(state, {
  activeReportId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
reportAuthority = createReportAuthorityState(caseGeneration);
projectReportAuthority(reportAuthority);
state.activeReportSessionId = "session-active";
acceptReportSessionForHarness("session-active");
let resolveStalePreview;
let resolveNewCatalog;
let catalogCalls = 0;
window.MorphicWorkbenchApi = {
  async loadReports() {
    catalogCalls += 1;
    if (catalogCalls === 1) return catalog;
    return new Promise(resolve => { resolveNewCatalog = resolve; });
  },
  async loadReportPreview() {
    return new Promise(resolve => { resolveStalePreview = resolve; });
  },
};
const staleCatalog = loadReports(caseGeneration, true);
await waitUntil(() => typeof resolveStalePreview === "function");
const newerCatalog = loadReports(caseGeneration, true);
await waitUntil(() => typeof resolveNewCatalog === "function");
resolveStalePreview({mode: "text", kind: "HTML", title: "stale", content: "stale", size: 5});
await staleCatalog;
if (state.activeReportId !== null || state.reportSelectionSource !== null) {
  throw new Error(`stale catalog bound preview authority: ${state.activeReportId}/${state.reportSelectionSource}`);
}
resolveNewCatalog({clients: []});
await newerCatalog;
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_superseded_preview_request_dispatches_stale_without_loading_html() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const catalog = {clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: [
    {id: "report-old", kind: "HTML", modified_at: "2026-08-01T10:00:00Z"},
    {id: "report-new", kind: "HTML", modified_at: "2026-08-01T10:01:00Z"},
  ]}],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let resolveOld;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview(reportId) {
    if (reportId === "report-old") {
      return new Promise(resolve => { resolveOld = resolve; });
    }
    return {mode: "text", kind: "HTML", title: "new", content: "new-text", size: 8};
  },
};

await loadReports(caseGeneration, true);
const cards = nodes["#report-list"].children;
const oldPreview = cards.find(card => card.dataset.reportId === "report-old").listeners.click();
await waitUntil(() => typeof resolveOld === "function");
await cards.find(card => card.dataset.reportId === "report-new").listeners.click();
const frameBefore = nodes["#report-preview-frame"].srcdoc;
resolveOld({mode: "html", kind: "HTML", title: "old", content: "<h1>old-html</h1>", size: 9});
const oldOutcome = await oldPreview;
if (
  oldOutcome !== "stale"
  || nodes["#report-preview-frame"].srcdoc !== frameBefore
  || state.activeReportId !== "report-new"
  || nodes["#report-preview-text"].textContent !== "new-text"
) {
  throw new Error(
    `superseded request loaded or rebound: ${oldOutcome}/`
    + `${nodes["#report-preview-frame"].srcdoc}/${frameBefore}/`
    + `${state.activeReportId}/${nodes["#report-preview-text"].textContent}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_stale_pending_without_stable_renders_empty_preview() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let catalog = {clients: [{
  client_id: "client-a",
  sessions: [{session_id: "session-a", files: [{id: "report-a", kind: "TXT"}]}],
}]};
Object.assign(state, {
  activeReportId: null,
  activeReportSessionId: null,
  reportFocusId: null,
  reportAutoSelectionKey: null,
  reportSelectionSource: null,
});
let resolvePreview;
window.MorphicWorkbenchApi = {
  async loadReports() { return catalog; },
  async loadReportPreview() {
    return new Promise(resolve => { resolvePreview = resolve; });
  },
};

await loadReports(caseGeneration, true);
const pending = nodes["#report-list"].children[0].listeners.click();
await waitUntil(() => typeof resolvePreview === "function");
if (nodes["#report-preview-panel"].dataset.state !== "loading") {
  throw new Error(`preview did not enter loading: ${nodes["#report-preview-panel"].dataset.state}`);
}
catalog = {clients: []};
await loadReports(caseGeneration, true);
resolvePreview({mode: "text", kind: "TXT", title: "A", content: "late", size: 4});
const outcome = await pending;
if (
  outcome !== "stale"
  || nodes["#report-preview-panel"].dataset.state !== "empty"
  || nodes["#report-preview-text"].hidden
  || !nodes["#report-preview-text"].textContent.includes("Waehle oben")
  || !nodes["#harmonization-start-button"].disabled
) {
  throw new Error(
    `stale pending without stable left loading: ${outcome}/`
    + `${nodes["#report-preview-panel"].dataset.state}/`
    + `${nodes["#report-preview-text"].hidden}/`
    + `${nodes["#report-preview-text"].textContent}/`
    + `${nodes["#harmonization-start-button"].disabled}`
  );
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_gate4_report_state_is_memory_only_and_reset_per_case() -> None:
    state_source = STATE_JS.read_text(encoding="utf-8")
    app_source = APP_JS.read_text(encoding="utf-8")
    reset_block = app_source.split(
        "async function resetWorkbenchForNewCase", 1
    )[1].split("function wireWorkbench", 1)[0]
    compact_state = re.sub(r"\s+", "", state_source)
    compact_reset = re.sub(r"\s+", "", reset_block)

    failures = []
    for field in (
        "activeReportSessionId",
        "reportFocusId",
        "reportAutoSelectionKey",
        "reportSelectionSource",
    ):
        if f"{field}:null" not in compact_state:
            failures.append(f"missing state field {field}: null")
    if "type:REPORT_AUTHORITY_EVENT.RESET_COMPLETED" not in compact_reset:
        failures.append("missing reducer new-case report authority reset")
    for storage in ("localStorage", "sessionStorage"):
        if storage in state_source:
            failures.append(f"workbench-state.js contains {storage}")
    for source_name, source in (
        ("workbench-state.js", state_source),
        ("app.js", app_source),
    ):
        lines = source.splitlines()
        for field in (
            "activeReportSessionId",
            "reportFocusId",
            "reportAutoSelectionKey",
            "reportSelectionSource",
        ):
            for index, line in enumerate(lines):
                if field not in line:
                    continue
                context = "\n".join(lines[max(0, index - 2) : index + 3])
                if "localStorage" in context or "sessionStorage" in context:
                    failures.append(f"{source_name} persists {field} in browser storage")

    assert not failures, "; ".join(failures)


def test_load_scan_results_runtime_accepts_normalizes_and_precedes_reports() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
async function finalizePayload(label, payload, expected) {
  const jobId = `scan-${label}`;
  let observedAuthority = "not-called";
  let reportCalls = 0;
  state.activeJobId = jobId;
  state.scanRunActive = true;
  state.activeReportSessionId = "previous-authority";
  window.MorphicWorkbenchApi = {
    async syncScanRunTrace() {},
    async loadScanResults() { return payload; },
    async loadRunTrace() { return {status: "completed"}; },
    async loadReports() {
      reportCalls += 1;
      observedAuthority = state.activeReportSessionId;
      return {clients: []};
    },
  };
  scanPollInFlight = {key: `${caseGeneration}:${jobId}`};
  const outcome = await finalizeTerminalScanOnce(jobId, "completed", caseGeneration, "poll");
  if (outcome !== "finalized" || reportCalls !== 1) {
    throw new Error(`${label}: finalization/report count ${outcome}/${reportCalls}`);
  }
  if (state.activeReportSessionId !== expected || observedAuthority !== expected) {
    throw new Error(
      `${label}: valid report authority not visible before catalog load: `
      + `${JSON.stringify(state.activeReportSessionId)}/${JSON.stringify(observedAuthority)}`
    );
  }
}

await finalizePayload("exact", {report_session_id: "session-exact"}, "session-exact");
await finalizePayload("null", {report_session_id: null}, null);
await finalizePayload("empty", {report_session_id: ""}, null);
for (const [label, value] of [
  ["number", 17], ["boolean", true], ["object", {id: "foreign"}], ["array", ["foreign"]],
]) {
  await finalizePayload(label, {report_session_id: value}, null);
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)

    mutated = _run_app_script(body, mutate_authority_assignment=True)
    assert mutated.returncode != 0
    assert "valid report authority not visible before catalog load" in mutated.stderr


def test_load_scan_results_runtime_rejects_stale_and_failed_authority() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;

async function staleJobCase() {
  const jobId = "scan-stale-job";
  let resolveResults;
  let reportCalls = 0;
  state.activeJobId = jobId;
  state.activeReportSessionId = "stable-job-authority";
  window.MorphicWorkbenchApi = {
    async syncScanRunTrace() {},
    async loadScanResults() { return new Promise(resolve => { resolveResults = resolve; }); },
    async loadRunTrace() { return {}; },
    async loadReports() { reportCalls += 1; return {clients: []}; },
  };
  scanPollInFlight = {key: `${caseGeneration}:${jobId}`};
  const pending = finalizeTerminalScanOnce(jobId, "completed", caseGeneration, "poll");
  await waitUntil(() => typeof resolveResults === "function");
  state.activeJobId = "scan-new-owner";
  resolveResults({report_session_id: "foreign-job-authority"});
  const outcome = await pending;
  if (outcome !== "stale" || reportCalls !== 0 || state.activeReportSessionId !== "stable-job-authority") {
    throw new Error(`stale job escaped guards: ${outcome}/${reportCalls}/${state.activeReportSessionId}`);
  }
}

async function staleGenerationCase() {
  const jobId = "scan-stale-generation";
  const generation = caseGeneration;
  let resolveResults;
  let reportCalls = 0;
  state.activeJobId = jobId;
  state.activeReportSessionId = "stable-generation-authority";
  window.MorphicWorkbenchApi = {
    async syncScanRunTrace() {},
    async loadScanResults() { return new Promise(resolve => { resolveResults = resolve; }); },
    async loadRunTrace() { return {}; },
    async loadReports() { reportCalls += 1; return {clients: []}; },
  };
  scanPollInFlight = {key: `${generation}:${jobId}`};
  const pending = finalizeTerminalScanOnce(jobId, "completed", generation, "poll");
  await waitUntil(() => typeof resolveResults === "function");
  caseGeneration += 1;
  resolveResults({report_session_id: "foreign-generation-authority"});
  const outcome = await pending;
  if (outcome !== "stale" || reportCalls !== 0 || state.activeReportSessionId !== "stable-generation-authority") {
    throw new Error(`stale generation escaped guards: ${outcome}/${reportCalls}/${state.activeReportSessionId}`);
  }
}

async function staleRequestTokenCase() {
  const jobId = "scan-stale-request-token";
  const generation = caseGeneration;
  let resolveFirstResults;
  let resultCalls = 0;
  let reportCalls = 0;
  state.activeJobId = jobId;
  state.activeReportSessionId = "stable-request-authority";
  window.MorphicWorkbenchApi = {
    async syncScanRunTrace() {},
    async loadScanResults() {
      resultCalls += 1;
      if (resultCalls === 1) {
        return new Promise(resolve => { resolveFirstResults = resolve; });
      }
      return {report_session_id: "fresh-request-authority"};
    },
    async loadRunTrace() { return {}; },
    async loadReports() { reportCalls += 1; return {clients: []}; },
  };
  scanPollInFlight = {key: `${generation}:${jobId}`};
  const staleFinalization = finalizeTerminalScanOnce(jobId, "completed", generation, "poll");
  await waitUntil(() => typeof resolveFirstResults === "function");
  await loadScanResults(jobId, generation, true);
  if (state.activeReportSessionId !== "fresh-request-authority") {
    throw new Error(`fresh request was not accepted: ${state.activeReportSessionId}`);
  }
  resolveFirstResults({report_session_id: "stale-request-authority"});
  const outcome = await staleFinalization;
  if (outcome !== "stale" || reportCalls !== 0 || state.activeReportSessionId !== "fresh-request-authority") {
    throw new Error(`stale request token escaped guards: ${outcome}/${reportCalls}/${state.activeReportSessionId}`);
  }
}

async function failedResultCase(label, failure) {
  const jobId = `scan-${label}`;
  let reportCalls = 0;
  state.activeJobId = jobId;
  state.activeReportSessionId = `${label}-stable-authority`;
  window.MorphicWorkbenchApi = {
    async syncScanRunTrace() {},
    async loadScanResults() { throw failure; },
    async loadRunTrace() { throw new Error("must not load trace after result failure"); },
    async loadReports() { reportCalls += 1; return {clients: []}; },
  };
  scanPollInFlight = {key: `${caseGeneration}:${jobId}`};
  const outcome = await finalizeTerminalScanOnce(jobId, "completed", caseGeneration, "poll");
  if (
    outcome !== "followup-error"
    || reportCalls !== 0
    || state.activeReportSessionId !== `${label}-stable-authority`
  ) {
    throw new Error(`${label} replaced authority: ${outcome}/${reportCalls}/${state.activeReportSessionId}`);
  }
}

await staleJobCase();
await staleGenerationCase();
await staleRequestTokenCase();
await failedResultCase("error", new Error("result failed"));
const abort = new Error("result aborted");
abort.name = "AbortError";
await failedResultCase("abort", abort);
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_new_case_runtime_clears_report_authority_and_preview() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
Object.assign(state, {
  activeJobId: null,
  activeHarmonizationJobId: null,
  pendingMutations: 0,
  scanStartPending: false,
  resetInProgress: false,
  activeReportId: "report-stale",
  activeReportSessionId: "session-stale",
  reportFocusId: "focus-stale",
  reportAutoSelectionKey: "auto-stale",
  reportSelectionSource: "manual",
});
window.MorphicWorkbenchApi = {
  async loadScanProfileCatalog(level) { return validCatalog(level); },
};

const completed = await resetWorkbenchForNewCase();
if (!completed) throw new Error("new-case reset did not complete");
for (const field of [
  "activeReportId",
  "activeReportSessionId",
  "reportFocusId",
  "reportAutoSelectionKey",
  "reportSelectionSource",
]) {
  if (state[field] !== null) throw new Error(`new-case reset retained ${field}: ${state[field]}`);
}
const frame = nodes["#report-preview-frame"];
const text = nodes["#report-preview-text"];
const link = nodes["#report-open-link"];
if (frame.srcdoc !== "" || frame.src !== "" || !frame.hidden) {
  throw new Error(`preview frame retained stale content: ${frame.src}/${frame.srcdoc}/${frame.hidden}`);
}
if (text.hidden || !text.textContent.includes("Waehle oben einen Bericht")) {
  throw new Error(`preview text was not reset: ${text.hidden}/${text.textContent}`);
}
if (link.href !== "#" || !link.hidden) {
  throw new Error(`preview link retained stale authority: ${link.href}/${link.hidden}`);
}
if (
  nodes["#report-preview-title"].textContent !== "Noch kein Bericht gewaehlt"
  || !nodes["#report-preview-meta"].textContent.includes("Keine Vorschau")
  || nodes["#report-preview-state"].textContent !== "bereit"
  || nodes["#report-list"].children.length !== 0
) {
  throw new Error("new-case reset left stale report catalog or preview metadata");
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)


def test_new_case_invalidates_pending_results_before_waiting_for_stop() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const jobId = "scan-reset-pending-results";
let resolveResults;
let resolveStop;
let reportCalls = 0;
state.activeJobId = jobId;
state.scanRunActive = true;
acceptReportSessionForHarness("pre-reset-authority");
window.MorphicWorkbenchApi = {
  async syncScanRunTrace() {},
  async loadScanResults() {
    return new Promise(resolve => { resolveResults = resolve; });
  },
  async loadRunTrace() { return {}; },
  async loadReports() { reportCalls += 1; return {clients: []}; },
  async stopScanJob() {
    return new Promise(resolve => { resolveStop = resolve; });
  },
  async loadScanProfileCatalog(level) { return validCatalog(level); },
};
scanPollInFlight = {key: `${caseGeneration}:${jobId}`};

const pendingFinalization = finalizeTerminalScanOnce(
  jobId,
  "completed",
  caseGeneration,
  "poll"
);
await waitUntil(() => typeof resolveResults === "function");
const pendingReset = resetWorkbenchForNewCase();
await waitUntil(() => state.resetInProgress && typeof resolveStop === "function");

resolveResults({report_session_id: "result-during-reset"});
const finalizationOutcome = await pendingFinalization;
if (
  finalizationOutcome !== "stale"
  || state.activeReportSessionId !== "pre-reset-authority"
  || reportCalls !== 0
) {
  throw new Error(
    `pending result escaped reset gate: ${finalizationOutcome}/`
    + `${state.activeReportSessionId}/${reportCalls}`
  );
}
if (!state.resetInProgress) {
  throw new Error("reset stopped waiting before controlled stop response");
}

resolveStop({status: "stopped"});
const resetCompleted = await pendingReset;
if (!resetCompleted || state.activeReportSessionId !== null) {
  throw new Error(`reset did not finish cleanly: ${resetCompleted}/${state.activeReportSessionId}`);
}
"""

    result = _run_app_script(body)
    _assert_node_success(result)
