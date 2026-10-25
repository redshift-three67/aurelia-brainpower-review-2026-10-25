from __future__ import annotations

import json
import re
import secrets
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
APP_CSS = ROOT / "apps" / "web" / "static" / "app.css"
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"
STATE_JS = ROOT / "apps" / "web" / "static" / "workbench-state.js"
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
NODE_HARNESS_TIMEOUT_SECONDS = 10


def _require_node_harness_success(
    result: subprocess.CompletedProcess[str], marker: str
) -> subprocess.CompletedProcess[str]:
    if result.returncode != 0 or marker not in result.stdout.splitlines():
        raise AssertionError(
            "Node harness exited without its completion marker"
            f" (returncode={result.returncode}):\n{result.stderr}"
        )
    return result


def _run_app_script(body: str) -> subprocess.CompletedProcess[str]:
    harness = r"""
const fs = require("fs");
const vm = require("vm");

function node(overrides = {}) {
  const listeners = new Map();
  return {
    textContent: "",
    className: "",
    disabled: false,
    checked: false,
    hidden: false,
    value: "",
    style: {},
    children: [],
    addEventListener(type, listener) {
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(listener);
    },
    appendChild(child) { this.children.push(child); },
    replaceChildren() { this.children = []; },
    querySelectorAll() { return []; },
    reset() {},
    dispatchEvent(event) {
      event.target = this;
      for (const listener of listeners.get(event.type) || []) listener.call(this, event);
    },
    setAttribute() {},
    removeAttribute() {},
    ...overrides,
  };
}

const controls = {
  last_name: node({value: "Gate"}),
  first_name: node({value: "Drei"}),
  birth_date: node({value: "09041966"}),
  birth_place: node({value: "Augsburg"}),
  focus: node({value: "synthetischer Fokus"}),
  main_symptom: node({value: ""}),
  profile_level: node({value: "3"}),
  top_n: node({
    value: "5",
    options: ["3", "5", "7", "9"].map(value => node({value})),
  }),
  profile_template: node({value: "phase1-default"}),
  entropy_mode: node({value: "legacy"}),
  image_path: node({value: ""}),
  adaptive_limits: node({type: "checkbox", checked: false}),
  planetary_vector_enabled: node({type: "checkbox", checked: false}),
  planet_type: node({value: ""}),
};
function internalPool(count = 9) {
  return {
    count,
    profiles: Array.from({length: count}, (_, index) => ({
      id: `profile-${index + 1}`,
      label: `Profil ${index + 1}`,
    })),
  };
}
const scanForm = node({
  fields: controls,
  reset() { controls.profile_level.value = "3"; },
});
const nodes = {
  "#scan-form": scanForm,
  "#consent-local": node({checked: true}),
  "#consent-safety": node({checked: true}),
  "#preview-button": node(),
  "#start-analysis-button": node(),
  "#scan-refresh-button": node(),
  "#scan-stop-button": node(),
  "#job-status-panel": node({hidden: true}),
  "#job-id-label": node(),
  "#job-status-label": node(),
  "#preview-state": node(),
  "#wizard-navigation-state": node(),
  "#command-preview": node(),
  "#new-case-button": node(),
  "#source-analysis-integration": node(),
  "#group-scan-activation-enabled": node({checked: false}),
  "#group-scan-draft-id": node({value: ""}),
};

global.FormData = class FormDataDouble {
  constructor(form) { this.form = form; }
  get(name) {
    const control = this.form?.fields?.[name];
    if (!control) return null;
    if (control.type === "checkbox") return control.checked ? "on" : null;
    return control.value;
  }
};
global.Event = class EventDouble {
  constructor(type) { this.type = type; }
};
global.document = {
  querySelector(selector) {
    if (nodes[selector]) return nodes[selector];
    const match = selector.match(/name="([^"]+)"/);
    return match ? controls[match[1]] || null : null;
  },
  querySelectorAll() { return []; },
  createElement() { return node(); },
};
const storage = new Map();
global.window = {
  addEventListener() {},
  localStorage: {
    getItem(key) { return storage.has(key) ? storage.get(key) : null; },
    setItem(key, value) { storage.set(key, String(value)); },
    removeItem(key) { storage.delete(key); },
  },
  MorphicWorkbenchApi: {},
  MorphicWorkbenchRender: {
    renderReviewCards() {},
    renderChoiceCards() {},
    resetSubstepTimeline() {},
    renderSubstepTimeline() {},
    showStep() {},
  },
};

vm.runInThisContext(fs.readFileSync(__STATE_JS__, "utf8"));
vm.runInThisContext(fs.readFileSync(__APP_JS__, "utf8"));

(async function runGate3Harness() {
global.__morphicGate3TestOperation = undefined;
__BODY__

const operation = global.__morphicGate3TestOperation;
if (operation !== undefined) {
  if (!operation || typeof operation.then !== "function") {
    throw new Error("Gate-3 test operation must be a Promise");
  }
  await operation;
}
console.log(__SUCCESS_MARKER__);
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    marker = f"__MORPHIC_GATE3_NODE_SUCCESS_{secrets.token_hex(16)}__"
    script = (
        harness.replace("__STATE_JS__", json.dumps(str(STATE_JS)))
        .replace("__APP_JS__", json.dumps(str(APP_JS)))
        .replace("__BODY__", body.strip())
        .replace("__SUCCESS_MARKER__", json.dumps(marker))
    )
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=NODE_HARNESS_TIMEOUT_SECONDS,
    )
    return _require_node_harness_success(result, marker)


def _run_render_script(body: str) -> subprocess.CompletedProcess[str]:
    harness = r"""
const fs = require("fs");
const vm = require("vm");

class EventDouble {
  constructor(type) {
    this.type = type;
    this.defaultPrevented = false;
    this.target = null;
    this.currentTarget = null;
  }
  preventDefault() { this.defaultPrevented = true; }
}

function matches(node, selector) {
  return selector.split(",").some((candidate) => {
    const value = candidate.trim();
    if (!value) return false;
    if (value.startsWith("#")) return node.id === value.slice(1);
    if (value.startsWith(".")) {
      return String(node.className || "").split(/\s+/).includes(value.slice(1));
    }
    return node.tagName === value.toUpperCase();
  });
}

function descendants(root, selector) {
  const found = [];
  for (const child of root.children || []) {
    if (matches(child, selector)) found.push(child);
    found.push(...descendants(child, selector));
  }
  return found;
}

function contains(root, candidate) {
  if (root === candidate) return true;
  return (root.children || []).some((child) => contains(child, candidate));
}

function element(tagName) {
  const listeners = new Map();
  return {
    tagName: String(tagName).toUpperCase(),
    id: "",
    className: "",
    type: "",
    value: "",
    hidden: false,
    children: [],
    parentNode: null,
    attributes: {},
    _text: "",
    appendChild(child) {
      child.parentNode = this;
      this.children.push(child);
      return child;
    },
    replaceChildren(...children) {
      if (global.document?.activeElement && contains(this, global.document.activeElement)) {
        global.document.activeElement = global.document.body;
      }
      this.children = [];
      this._text = "";
      children.forEach((child) => this.appendChild(child));
    },
    addEventListener(type, listener) {
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(listener);
    },
    dispatchEvent(event) {
      event.target = this;
      event.currentTarget = this;
      for (const listener of listeners.get(event.type) || []) listener.call(this, event);
      return !event.defaultPrevented;
    },
    click() { this.dispatchEvent(new EventDouble("click")); },
    focus() { global.document.activeElement = this; },
    setAttribute(name, value) {
      const text = String(value);
      this.attributes[name] = text;
      if (name === "id") this.id = text;
      if (name === "class") this.className = text;
      if (name === "type") this.type = text;
    },
    getAttribute(name) { return this.attributes[name] ?? null; },
    removeAttribute(name) { delete this.attributes[name]; },
    querySelector(selector) { return descendants(this, selector)[0] || null; },
    querySelectorAll(selector) { return descendants(this, selector); },
    get textContent() {
      return this._text + this.children.map((child) => child.textContent).join("");
    },
    set textContent(value) {
      if (global.document?.activeElement && contains(this, global.document.activeElement)) {
        global.document.activeElement = global.document.body;
      }
      this._text = String(value);
      this.children = [];
    },
    set innerHTML(_value) { throw new Error("innerHTML is forbidden in the DOM harness"); },
    insertAdjacentHTML() { throw new Error("insertAdjacentHTML is forbidden in the DOM harness"); },
  };
}

const cards = {
  "#review-client": element("article"),
  "#review-focus": element("article"),
  "#review-profile": element("article"),
  "#review-hardware": element("article"),
  "#review-scan-scope": element("article"),
};

function find(root, selector) { return root.querySelector(selector); }
function findAll(root, selector) { return root.querySelectorAll(selector); }

global.Event = EventDouble;
global.window = {
  MorphicWorkbenchState: {
    workbenchMode: "standard",
    scanProfileCatalogStatus: "loading",
    scanProfileCatalogError: "",
  },
  MorphicWorkbenchActions: {},
};
const documentBody = element("body");
global.document = {
  body: documentBody,
  activeElement: documentBody,
  querySelector(selector) { return cards[selector] || null; },
  createElement(tagName) { return element(tagName); },
  createTextNode(value) {
    const text = element("#text");
    text.textContent = value;
    return text;
  },
  getElementById(id) {
    for (const card of Object.values(cards)) {
      if (card.id === id) return card;
      const match = descendants(card, `#${id}`)[0];
      if (match) return match;
    }
    return null;
  },
};

vm.runInThisContext(fs.readFileSync(__RENDER_JS__, "utf8"));

(async function runGate3Harness() {
global.__morphicGate3TestOperation = undefined;
__BODY__

const operation = global.__morphicGate3TestOperation;
if (operation !== undefined) {
  if (!operation || typeof operation.then !== "function") {
    throw new Error("Gate-3 test operation must be a Promise");
  }
  await operation;
}
console.log(__SUCCESS_MARKER__);
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    marker = f"__MORPHIC_GATE3_NODE_SUCCESS_{secrets.token_hex(16)}__"
    script = harness.replace("__RENDER_JS__", json.dumps(str(RENDER_JS))).replace(
        "__BODY__", body.strip()
    ).replace("__SUCCESS_MARKER__", json.dumps(marker))
    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=NODE_HARNESS_TIMEOUT_SECONDS,
    )
    return _require_node_harness_success(result, marker)


def test_gate3_node_harnesses_propagate_a_fixed_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[int | float | None] = []

    def expire(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed.append(kwargs.get("timeout"))
        raise subprocess.TimeoutExpired(args[0], kwargs.get("timeout"))

    monkeypatch.setattr(subprocess, "run", expire)

    for harness in (_run_app_script, _run_render_script):
        with pytest.raises(subprocess.TimeoutExpired) as captured:
            harness("")
        assert captured.value.timeout == NODE_HARNESS_TIMEOUT_SECONDS

    assert observed == [NODE_HARNESS_TIMEOUT_SECONDS, NODE_HARNESS_TIMEOUT_SECONDS]


def test_gate3_node_harnesses_require_unique_awaited_completion_markers() -> None:
    results = [_run_app_script(""), _run_render_script("")]
    markers = [
        re.findall(r"__MORPHIC_GATE3_NODE_SUCCESS_[0-9a-f]{32}__", result.stdout)
        for result in results
    ]

    assert all(len(found) == 1 for found in markers)
    assert markers[0][0] != markers[1][0]

    unresolved = r"""
global.__morphicGate3TestOperation = (async () => {
  await new Promise(() => {});
})();
"""
    for harness in (_run_app_script, _run_render_script):
        with pytest.raises(AssertionError, match="completion marker"):
            harness(unresolved)


def test_gate3_node_harnesses_await_registered_operation_after_prelude() -> None:
    unresolved = r"""
const prelude = "registered-before-operation";
if (!prelude) throw new Error("prelude missing");
global.__morphicGate3TestOperation = (async () => {
  await new Promise(() => {});
})();
"""

    for harness in (_run_app_script, _run_render_script):
        with pytest.raises(AssertionError, match="completion marker"):
            harness(unresolved)


def test_gate3_node_harnesses_reject_registered_delayed_failure_without_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[subprocess.CompletedProcess[str]] = []
    run = subprocess.run

    def capture(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        result = run(*args, **kwargs)
        observed.append(result)
        return result

    monkeypatch.setattr(subprocess, "run", capture)
    rejected = r"""
const prelude = "registered-before-operation";
if (!prelude) throw new Error("prelude missing");
global.__morphicGate3TestOperation = (async () => {
  await new Promise(resolve => setTimeout(resolve, 20));
  throw new Error("registered delayed rejection");
})();
"""

    for harness in (_run_app_script, _run_render_script):
        with pytest.raises(AssertionError, match="completion marker"):
            harness(rejected)
        result = observed[-1]
        assert result.returncode != 0
        assert "registered delayed rejection" in result.stderr
        assert not re.search(
            r"__MORPHIC_GATE3_NODE_SUCCESS_[0-9a-f]{32}__",
            result.stdout,
        )


def test_scan_actions_are_initially_disabled_in_html() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")

    for button_id in ("preview-button", "start-analysis-button"):
        match = re.search(rf'<button\s+id="{button_id}"[^>]*>', html)
        assert match is not None
        assert re.search(r"\sdisabled(?:\s|>)", match.group(0)) is not None
        assert 'aria-describedby="preview-state"' in match.group(0)

    status = re.search(r'<span\s+id="preview-state"[^>]*>(.*?)</span>', html)
    assert status is not None
    assert 'role="status"' in status.group(0)
    assert 'aria-live="polite"' in status.group(0)
    assert 'aria-atomic="true"' in status.group(0)
    assert 'class="inline-state neutral"' in status.group(0)
    assert status.group(1) == (
        "Scanprofil-Pool wird geladen; Vorschau und Start bleiben gesperrt."
    )


def test_form_payload_uses_only_ready_fingerprint_for_current_loaded_level() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const fingerprint = "a".repeat(64);
function ready() {
  state.scanProfileCatalogStatus = "ready";
  state.scanProfileCatalogLevel = 3;
  state.scanProfileCatalog = {
    profile_level: 3,
    pool_authority: {fingerprint},
  };
  controls.profile_level.value = "3";
}
function expectEmpty(label) {
  const actual = formScanPayload().scan_profile_pool_fingerprint;
  if (actual !== "") throw new Error(`${label}: leaked ${actual}`);
}

ready();
if (formScanPayload().scan_profile_pool_fingerprint !== fingerprint) {
  throw new Error("current fingerprint missing from payload");
}

controls.profile_level.value = "4";
expectEmpty("selected level changed");
ready();
state.scanProfileCatalogLevel = 2;
expectEmpty("old request level");
ready();
state.scanProfileCatalog.profile_level = 2;
expectEmpty("old response level");
ready();
state.scanProfileCatalogStatus = "loading";
expectEmpty("loading");
ready();
state.scanProfileCatalogStatus = "error";
expectEmpty("error");
ready();
state.scanProfileCatalog.pool_authority.fingerprint = "A".repeat(64);
expectEmpty("uppercase fingerprint");
ready();
state.scanProfileCatalog.pool_authority.fingerprint = "g".repeat(64);
expectEmpty("non-hex fingerprint");
ready();
state.scanProfileCatalog.pool_authority.fingerprint = "a".repeat(63);
expectEmpty("short fingerprint");
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_action_gate_combines_pool_readiness_with_pending_and_reservation_flags() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const preview = nodes["#preview-button"];
const start = nodes["#start-analysis-button"];
const refresh = nodes["#scan-refresh-button"];
const stop = nodes["#scan-stop-button"];
function ready() {
  controls.profile_level.value = "3";
  state.scanProfileCatalogStatus = "ready";
  state.scanProfileCatalogLevel = 3;
    state.scanProfileCatalog = {
      profile_level: 3,
      pool_authority: {fingerprint: "b".repeat(64)},
      internal: internalPool(),
  };
  state.scanStartPending = false;
  state.scanRunActive = false;
}
function expectButtons(label, previewDisabled, startDisabled) {
  updateScanActionAvailability();
  if (preview.disabled !== previewDisabled || start.disabled !== startDisabled) {
    throw new Error(`${label}: preview=${preview.disabled}, start=${start.disabled}`);
  }
}

ready();
expectButtons("ready", false, false);
state.scanStartPending = true;
expectButtons("start pending", true, true);
state.scanStartPending = false;
state.scanRunActive = true;
expectButtons("scan active", true, true);

ready();
setScanReservationControls(true);
if (!preview.disabled || !start.disabled || refresh.disabled || stop.disabled) {
  throw new Error("reservation controls did not preserve the active-run gate");
}
setScanReservationControls(false);
if (preview.disabled || start.disabled || !refresh.disabled || !stop.disabled) {
  throw new Error("reservation release did not delegate to current pool readiness");
}

for (const [label, mutate] of [
  ["loading", () => { state.scanProfileCatalogStatus = "loading"; }],
  ["error", () => { state.scanProfileCatalogStatus = "error"; }],
  ["loaded level", () => { state.scanProfileCatalogLevel = 4; }],
  ["response level", () => { state.scanProfileCatalog.profile_level = 4; }],
  ["fingerprint", () => { state.scanProfileCatalog.pool_authority.fingerprint = "invalid"; }],
]) {
  ready();
  mutate();
  expectButtons(label, true, true);
}
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_top_n_pool_cardinality_gates_actions_options_and_programmatic_requests() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const topN = controls.top_n;
state.scanProfileCatalogStatus = "ready";
state.scanProfileCatalogLevel = 1;
state.scanProfileCatalog = {
  profile_level: 1,
  pool_authority: {fingerprint: "c".repeat(64)},
  internal: {
    count: 5,
    profiles: Array.from({length: 5}, (_, index) => ({
      id: `profile-${index + 1}`,
      label: `Profil ${index + 1}`,
    })),
  },
};
controls.profile_level.value = "1";
topN.value = "9";
let previewCalls = 0;
let startCalls = 0;
window.MorphicWorkbenchApi.loadScanPreview = async () => { previewCalls += 1; };
window.MorphicWorkbenchApi.startScanJob = async () => { startCalls += 1; };

global.__morphicGate3TestOperation = (async () => {
  updateScanProfileTopNOptions();
  const disabled = Object.fromEntries(topN.options.map(option => [option.value, option.disabled]));
  if (JSON.stringify(disabled) !== JSON.stringify({3: false, 5: false, 7: true, 9: true})) {
    throw new Error(`falsche Top-N-Optionen: ${JSON.stringify(disabled)}`);
  }
  if (topN.value !== "9") throw new Error(`Auswahl wurde still geändert: ${topN.value}`);
  if (scanProfilePoolSupportsCurrentTopN()) throw new Error("Top-9 wurde für Pool 5 akzeptiert");
  updateScanActionAvailability();
  if (!nodes["#preview-button"].disabled || !nodes["#start-analysis-button"].disabled) {
    throw new Error("ungültiges Top-N ließ Aktionen aktiv");
  }
  const message = validateScanPayload(formScanPayload());
  if (message !== "Top-N überschreitet den bestätigten Scanprofil-Pool. Bitte Auswahl anpassen.") {
    throw new Error(`falsche Top-N-Meldung: ${message}`);
  }
  await generatePreview();
  await startScanJob();
  if (previewCalls !== 0 || startCalls !== 0) {
    throw new Error(`ungültiges Top-N wurde versandt: ${previewCalls}/${startCalls}`);
  }

  topN.value = "5";
  if (!scanProfilePoolSupportsCurrentTopN()) throw new Error("Top-5 wurde für Pool 5 abgelehnt");
  updateScanActionAvailability();
  if (nodes["#preview-button"].disabled || nodes["#start-analysis-button"].disabled) {
    throw new Error("Top-5-Recovery entsperrte Aktionen nicht");
  }
  if (validateScanPayload(formScanPayload()) !== null) {
    throw new Error("Top-5-Recovery blieb ungültig");
  }

  for (const invalidCount of ["5", true, 5.5]) {
    state.scanProfileCatalog.internal.count = invalidCount;
    if (scanProfilePoolSupportsCurrentTopN()) {
      throw new Error(`coerciver Pool-Count wurde akzeptiert: ${JSON.stringify(invalidCount)}`);
    }
  }
  state.scanProfileCatalog.internal.count = 5;

  state.scanProfileCatalogStatus = "loading";
  updateScanProfileTopNOptions();
  updateScanActionAvailability();
  if (topN.options.some(option => option.disabled)) {
    throw new Error("Loading behielt veraltete deaktivierte Optionen");
  }
  if (!nodes["#preview-button"].disabled || !nodes["#start-analysis-button"].disabled) {
    throw new Error("Loading entsperrte Aktionen");
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_programmatic_preview_and_start_are_blocked_without_current_fingerprint() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
state.scanProfileCatalogStatus = "error";
state.scanProfileCatalogError = "Katalog nicht verfügbar";
state.scanProfileCatalogLevel = 3;
state.scanProfileCatalog = null;
let previewCalls = 0;
let startCalls = 0;
window.MorphicWorkbenchApi.loadScanPreview = async () => {
  previewCalls += 1;
  return {command: []};
};
window.MorphicWorkbenchApi.startScanJob = async () => {
  startCalls += 1;
  throw new Error("must not dispatch");
};

global.__morphicGate3TestOperation = (async () => {
  const payload = formScanPayload();
  const validationMessage = validateScanPayload(payload);
  if (
    !validationMessage
    || !validationMessage.includes("Scanprofil-Pool")
    || !validationMessage.includes("neu laden")
  ) throw new Error(`unclear pool validation: ${validationMessage}`);

  state.scanProfileCatalogStatus = "ready";
  state.scanProfileCatalog = {
    profile_level: 3,
    pool_authority: {fingerprint: "e".repeat(64)},
  };
  const wrongLevelPayload = formScanPayload();
  wrongLevelPayload.profile_level = 4;
  const wrongLevelMessage = validateScanPayload(wrongLevelPayload);
  if (!wrongLevelMessage?.includes("Scanprofil-Pool")) {
    throw new Error(`mutated payload level passed validation: ${wrongLevelMessage}`);
  }
  state.scanProfileCatalogStatus = "error";
  state.scanProfileCatalog = null;

  await generatePreview();
  await startScanJob();
  if (previewCalls !== 0 || startCalls !== 0) {
    throw new Error(`programmatic request escaped: ${previewCalls}/${startCalls}`);
  }
  if (state.scanStartOperationId !== null) {
    throw new Error("start operation was reserved before pool validation");
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("state_overrides", "existing_text", "existing_class"),
    [
        (
            {"scanStartPending": True},
            "Analyse wird gestartet...",
            "inline-state neutral",
        ),
        (
            {"scanRunActive": True},
            "Analyse gestartet",
            "inline-state ok",
        ),
    ],
)
def test_programmatic_preview_is_side_effect_free_while_scan_owns_status(
    state_overrides: dict[str, bool],
    existing_text: str,
    existing_class: str,
) -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
state.scanProfileCatalogStatus = "ready";
state.scanProfileCatalogLevel = 3;
state.scanProfileCatalog = {
  profile_level: 3,
  pool_authority: {fingerprint: "0".repeat(64)},
};
Object.assign(state, {scanStartPending: false, scanRunActive: false}, __STATE_OVERRIDES__);

let previewCalls = 0;
let formDataConstructions = 0;
window.MorphicWorkbenchApi.loadScanPreview = async () => {
  previewCalls += 1;
  return {command: ["must-not-dispatch"]};
};
global.FormData = class BlockedFormData {
  constructor() {
    formDataConstructions += 1;
    throw new Error("blocked preview reached formScanPayload");
  }
};

global.__morphicGate3TestOperation = (async () => {
  const previewState = nodes["#preview-state"];
  const navigationState = nodes["#wizard-navigation-state"];
  previewState.textContent = __EXISTING_TEXT__;
  previewState.className = __EXISTING_CLASS__;
  navigationState.textContent = "";
  navigationState.className = "inline-state neutral";
  nodes["#command-preview"].textContent = "bestehende Vorschau";
  updateScanActionAvailability();
  if (!nodes["#preview-button"].disabled) {
    throw new Error("preview button stayed enabled while scan owned the action");
  }

  const tokenBefore = scanPreviewRequestToken;
  const blocked = await generatePreview();
  if (blocked !== false) throw new Error(`blocked preview returned ${blocked}`);
  if (scanPreviewRequestToken !== tokenBefore) {
    throw new Error("blocked preview incremented the request token");
  }
  if (formDataConstructions !== 0 || previewCalls !== 0) {
    throw new Error(`blocked preview caused side effects: ${formDataConstructions}/${previewCalls}`);
  }
  if (
    previewState.textContent !== __EXISTING_TEXT__
    || previewState.className !== __EXISTING_CLASS__
    || nodes["#command-preview"].textContent !== "bestehende Vorschau"
  ) throw new Error("blocked preview overwrote the authoritative scan status or preview");
  if (
    navigationState.textContent !== "Eine Analyse wird bereits gestartet oder ausgefuehrt."
    || navigationState.className !== "inline-state bad"
  ) throw new Error(`clear blocked message missing: ${navigationState.textContent}`);
})();
"""
    body = (
        body.replace("__STATE_OVERRIDES__", json.dumps(state_overrides))
        .replace("__EXISTING_TEXT__", json.dumps(existing_text))
        .replace("__EXISTING_CLASS__", json.dumps(existing_class))
    )

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_catalog_level_change_locks_immediately_and_late_response_cannot_unlock() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const preview = nodes["#preview-button"];
const start = nodes["#start-analysis-button"];
const requests = new Map();
window.MorphicWorkbenchApi.loadScanProfileCatalog = (level) => new Promise(
  (resolve, reject) => requests.set(Number(level), {resolve, reject})
);

global.__morphicGate3TestOperation = (async () => {
  controls.profile_level.value = "3";
  preview.disabled = false;
  start.disabled = false;
  const oldRequest = loadScanProfileCatalog(3);
  if (!preview.disabled || !start.disabled || state.scanProfileCatalogStatus !== "loading") {
    throw new Error("loading did not lock actions synchronously");
  }

  controls.profile_level.value = "4";
  const currentRequest = loadScanProfileCatalog(4);
  requests.get(3).resolve({
    profile_level: 3,
    pool_authority: {fingerprint: "c".repeat(64)},
  });
  await oldRequest;
  if (
    state.scanProfileCatalog !== null
    || state.scanProfileCatalogLevel !== 4
    || state.scanProfileCatalogStatus !== "loading"
    || !preview.disabled
    || !start.disabled
  ) throw new Error("late old response changed current loading authority");

  requests.get(4).resolve({
    profile_level: 4,
    pool_authority: {fingerprint: "d".repeat(64)},
    internal: internalPool(),
    external: {},
  });
  await currentRequest;
  if (
    state.scanProfileCatalogStatus !== "ready"
    || preview.disabled
    || start.disabled
  ) throw new Error("matching catalog did not unlock actions");

  controls.profile_level.value = "2";
  const failedRequest = loadScanProfileCatalog(2);
  requests.get(2).reject(new Error("catalog unavailable"));
  await failedRequest;
  if (
    state.scanProfileCatalogStatus !== "error"
    || !preview.disabled
    || !start.disabled
  ) throw new Error("catalog error did not keep actions locked");
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_reset_locks_scan_actions_and_programmatic_requests_until_abort_or_completion() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const preview = nodes["#preview-button"];
const start = nodes["#start-analysis-button"];
function ready() {
  controls.profile_level.value = "3";
  state.scanProfileCatalogStatus = "ready";
  state.scanProfileCatalogLevel = 3;
  state.scanProfileCatalog = {
    profile_level: 3,
    pool_authority: {fingerprint: "f".repeat(64)},
    internal: internalPool(),
  };
  state.scanStartPending = false;
  state.scanRunActive = false;
  state.resetInProgress = false;
  updateScanActionAvailability();
}

let rejectStop;
let previewCalls = 0;
let startCalls = 0;
const observedOperationIds = [];
let catalogCalls = 0;
window.MorphicWorkbenchApi.stopHarmonization = async () => new Promise(
  (_resolve, reject) => { rejectStop = reject; }
);
window.MorphicWorkbenchApi.loadScanPreview = async () => {
  previewCalls += 1;
  return {command: ["must-not-render"]};
};
window.MorphicWorkbenchApi.startScanJob = async (_body, operationId) => {
  startCalls += 1;
  observedOperationIds.push(operationId);
  throw Object.assign(new Error("must not dispatch"), {
    status: 500,
    startOperationDisposition: "safe-to-replace",
  });
};
window.MorphicWorkbenchApi.loadScanProfileCatalog = async (level) => {
  catalogCalls += 1;
  return {
    profile_level: Number(level),
    pool_authority: {fingerprint: "1".repeat(64)},
    internal: internalPool(),
    external: {},
  };
};

global.__morphicGate3TestOperation = (async () => {
  ready();
  state.activeHarmonizationJobId = "harm-reset-race";
  const pendingReset = resetWorkbenchForNewCase();
  await Promise.resolve();
  const lockedAtStart = preview.disabled && start.disabled;

  await generatePreview();
  await startScanJob();
  rejectStop(new Error("stop failed"));
  const aborted = await pendingReset;

  if (!lockedAtStart) throw new Error("reset did not lock actions before stop await");
  if (previewCalls !== 0 || startCalls !== 0 || observedOperationIds.length !== 0) {
    throw new Error(`reset allowed request/operation: ${previewCalls}/${startCalls}/${observedOperationIds.length}`);
  }
  if (aborted !== false || state.resetInProgress) {
    throw new Error("failed reset did not leave reset state cleanly");
  }
  if (preview.disabled || start.disabled) {
    throw new Error("aborted reset did not restore valid pool availability");
  }

  state.activeHarmonizationJobId = null;
  const completed = await resetWorkbenchForNewCase();
  if (!completed || state.resetInProgress || catalogCalls !== 1) {
    throw new Error("successful reset did not finish with a fresh catalog");
  }
  if (preview.disabled || start.disabled) {
    throw new Error("successful reset did not refresh action availability after clearing reset flag");
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_stale_header_preview_409_invalidates_pool_and_starts_one_catalog_reload() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
controls.profile_level.value = "3";
state.scanProfileCatalogStatus = "ready";
state.scanProfileCatalogLevel = 3;
state.scanProfileCatalog = {
  profile_level: 3,
  pool_authority: {fingerprint: "2".repeat(64)},
  internal: internalPool(),
};
let previewCalls = 0;
let reloadCalls = 0;
let resolveReload;
window.MorphicWorkbenchApi.loadScanPreview = async () => {
  previewCalls += 1;
  throw Object.assign(new Error("server detail is irrelevant"), {
    status: 409,
    scanProfilePoolDisposition: "stale",
  });
};
window.MorphicWorkbenchApi.loadScanProfileCatalog = async () => {
  reloadCalls += 1;
  return new Promise(resolve => { resolveReload = resolve; });
};

global.__morphicGate3TestOperation = (async () => {
  await generatePreview();
  if (previewCalls !== 1 || reloadCalls !== 1) {
    throw new Error(`unexpected preview/reload count: ${previewCalls}/${reloadCalls}`);
  }
  if (
    state.scanProfileCatalog !== null
    || state.scanProfileCatalogStatus !== "loading"
    || !nodes["#preview-button"].disabled
    || !nodes["#start-analysis-button"].disabled
  ) throw new Error("preview 409 did not invalidate the pool synchronously");
  resolveReload({
    profile_level: 3,
    pool_authority: {fingerprint: "3".repeat(64)},
    internal: internalPool(),
    external: {},
  });
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_generic_preview_409_does_not_invalidate_or_reload_pool() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
controls.profile_level.value = "3";
state.scanProfileCatalogStatus = "ready";
state.scanProfileCatalogLevel = 3;
state.scanProfileCatalog = {
  profile_level: 3,
  pool_authority: {fingerprint: "2".repeat(64)},
  internal: internalPool(),
};
let reloadCalls = 0;
window.MorphicWorkbenchApi.loadScanPreview = async () => {
  throw Object.assign(new Error("identity conflict"), {status: 409});
};
window.MorphicWorkbenchApi.loadScanProfileCatalog = async () => {
  reloadCalls += 1;
  throw new Error("generic 409 must not reload");
};

global.__morphicGate3TestOperation = (async () => {
  const catalog = state.scanProfileCatalog;
  await generatePreview();
  if (reloadCalls !== 0) throw new Error(`generic 409 reloaded ${reloadCalls} times`);
  if (state.scanProfileCatalog !== catalog || state.scanProfileCatalogStatus !== "ready") {
    throw new Error("generic 409 invalidated catalog authority");
  }
  updateScanActionAvailability();
  if (nodes["#preview-button"].disabled || nodes["#start-analysis-button"].disabled) {
    throw new Error("generic 409 left valid actions locked");
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_stale_disposition_without_409_does_not_reload_pool() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
controls.profile_level.value = "3";
state.scanProfileCatalogStatus = "ready";
state.scanProfileCatalogLevel = 3;
state.scanProfileCatalog = {
  profile_level: 3,
  pool_authority: {fingerprint: "2".repeat(64)},
  internal: internalPool(),
};
let reloadCalls = 0;
window.MorphicWorkbenchApi.loadScanPreview = async () => {
  throw Object.assign(new Error("service unavailable"), {
    status: 503,
    scanProfilePoolDisposition: "stale",
  });
};
window.MorphicWorkbenchApi.loadScanProfileCatalog = async () => {
  reloadCalls += 1;
  throw new Error("non-409 must not reload");
};

global.__morphicGate3TestOperation = (async () => {
  const catalog = state.scanProfileCatalog;
  await generatePreview();
  if (reloadCalls !== 0) throw new Error(`non-409 reloaded ${reloadCalls} times`);
  if (state.scanProfileCatalog !== catalog || state.scanProfileCatalogStatus !== "ready") {
    throw new Error("non-409 invalidated catalog authority");
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_start_409_reconciles_without_generic_catalog_reload_and_tagged_adoption_wins() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
function ready(fingerprint) {
  controls.profile_level.value = "3";
  state.scanProfileCatalogStatus = "ready";
  state.scanProfileCatalogLevel = 3;
    state.scanProfileCatalog = {
      profile_level: 3,
      pool_authority: {fingerprint},
      internal: internalPool(),
  };
  state.scanStartPending = false;
  state.scanRunActive = false;
}
let startCalls = 0;
let reconcileCalls = 0;
let reloadCalls = 0;
const errors = [
  Object.assign(new Error("start identity"), {status: 409}),
  Object.assign(new Error("drift"), {
    status: 409,
    scanProfilePoolDisposition: "stale",
  }),
];
const reconciliations = [
  {disposition: "retry-same-key"},
  {disposition: "job", job_id: "scan-adopted-after-stale", status: "running"},
];
window.MorphicWorkbenchApi.startScanJob = async () => {
  startCalls += 1;
  throw errors.shift();
};
window.MorphicWorkbenchApi.reconcileScanStartOperation = async () => {
  reconcileCalls += 1;
  return reconciliations.shift();
};
window.MorphicWorkbenchApi.pollScanJob = async () => new Promise(() => {});
window.MorphicWorkbenchApi.loadScanProfileCatalog = async () => {
  reloadCalls += 1;
  return new Promise(() => {});
};

global.__morphicGate3TestOperation = (async () => {
  ready("4".repeat(64));
  const generic = await startScanJob();
  const retainedKey = state.scanStartOperationId;
  if (generic !== false || !retainedKey) {
    throw new Error("generic 409 did not retain unresolved operation authority");
  }
  if (startCalls !== 1 || reconcileCalls !== 1 || reloadCalls !== 0) {
    throw new Error(`generic 409 contract: ${startCalls}/${reconcileCalls}/${reloadCalls}`);
  }

  ready("5".repeat(64));
  const adopted = await startScanJob();
  if (!adopted || state.activeJobId !== "scan-adopted-after-stale") {
    throw new Error(`tagged stale did not adopt reconciled job: ${state.activeJobId}`);
  }
  if (state.scanStartOperationId !== retainedKey) {
    throw new Error("reconciled job discarded or replaced the durable key");
  }
  if (startCalls !== 2 || reconcileCalls !== 2 || reloadCalls !== 1) {
    throw new Error(`tagged 409 contract: ${startCalls}/${reconcileCalls}/${reloadCalls}`);
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_successful_scan_start_retains_key_until_terminal_poll_confirmation() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
controls.profile_level.value = "3";
state.scanProfileCatalogStatus = "ready";
state.scanProfileCatalogLevel = 3;
state.scanProfileCatalog = {
  profile_level: 3,
  pool_authority: {fingerprint: "9".repeat(64)},
  internal: internalPool(),
};
let resolvePoll;
window.MorphicWorkbenchApi.startScanJob = async () => ({
  job_id: "scan-durable-key",
  status: "running",
});
window.MorphicWorkbenchApi.pollScanJob = async () => new Promise(
  resolve => { resolvePoll = resolve; }
);
window.MorphicWorkbenchApi.syncScanRunTrace = async () => ({});
window.MorphicWorkbenchApi.loadScanResults = async () => ({top_profiles: []});
window.MorphicWorkbenchApi.loadRunTrace = async () => ({status: "completed"});
window.MorphicWorkbenchApi.loadReports = async () => ({clients: []});

global.__morphicGate3TestOperation = (async () => {
  const started = await startScanJob();
  const operationId = readExistingStartOperationId("scan");
  if (!started || !operationId) throw new Error("successful start discarded operation key");
  if (state.activeJobId !== "scan-durable-key" || state.currentStepIndex !== 6) {
    throw new Error(`successful start was not adopted in Phase 6: ${state.activeJobId}/${state.currentStepIndex}`);
  }
  if (window.localStorage.getItem("morphic_scan_start_operation_id") !== operationId) {
    throw new Error("successful start did not persist durable reload authority");
  }
  const terminalPoll = scanPollInFlight?.promise;
  resolvePoll({
    job_id: "scan-durable-key",
    status: "completed",
    progress_percent: 100,
    completed_substeps: [],
    completed_stage_ids: [],
  });
  await terminalPoll;
  if (readExistingStartOperationId("scan") !== null) {
    throw new Error("terminal poll confirmation retained stale operation key");
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_reconcile_dispositions_clear_only_explicit_safe_authority() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const results = [
  {disposition: "safe-to-replace"},
  {disposition: "retry-same-key"},
];
window.MorphicWorkbenchApi.reconcileScanStartOperation = async () => results.shift();

global.__morphicGate3TestOperation = (async () => {
  const safeKey = startOperationId("scan");
  const safe = await reconcileExistingScanStartOperation(safeKey);
  if (safe.disposition !== "safe-to-replace" || readExistingStartOperationId("scan") !== null) {
    throw new Error("safe-to-replace did not clear operation authority");
  }

  const retryKey = startOperationId("scan");
  const retry = await reconcileExistingScanStartOperation(retryKey);
  if (retry.disposition !== "retry-same-key" || readExistingStartOperationId("scan") !== retryKey) {
    throw new Error("retry-same-key did not retain operation authority");
  }

  window.MorphicWorkbenchApi.reconcileScanStartOperation = async () => {
    throw Object.assign(new Error("unavailable"), {status: 503});
  };
  const unresolved = await reconcileExistingScanStartOperation(retryKey);
  if (unresolved.disposition !== "unresolved" || readExistingStartOperationId("scan") !== retryKey) {
    throw new Error("reconcile error discarded unresolved operation authority");
  }
  if (!nodes["#preview-state"].textContent.includes("Schlüssel")) {
    throw new Error(`missing clear unresolved state: ${nodes["#preview-state"].textContent}`);
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_new_case_reconciles_unresolved_key_and_retains_it_when_unresolved() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const operationId = startOperationId("scan");
let reconcileCalls = 0;
let stopCalls = 0;
window.MorphicWorkbenchApi.reconcileScanStartOperation = async (key) => {
  reconcileCalls += 1;
  if (key !== operationId) throw new Error("wrong operation key");
  return {disposition: "retry-same-key"};
};
window.MorphicWorkbenchApi.stopScanJob = async () => {
  stopCalls += 1;
  return {status: "stopped"};
};

global.__morphicGate3TestOperation = (async () => {
  const generation = caseGeneration;
  const reset = await resetWorkbenchForNewCase();
  if (reset !== false || reconcileCalls !== 1 || stopCalls !== 0) {
    throw new Error(`unresolved reset escaped: ${reset}/${reconcileCalls}/${stopCalls}`);
  }
  if (caseGeneration !== generation || readExistingStartOperationId("scan") !== operationId) {
    throw new Error("unresolved reset changed generation or operation authority");
  }
  if (!nodes["#preview-state"].textContent.includes("Abgleich")) {
    throw new Error(`reset did not request reconciliation: ${nodes["#preview-state"].textContent}`);
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_new_case_active_job_retains_key_on_failed_stop_and_clears_after_terminal_stop() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const operationId = startOperationId("scan");
state.activeJobId = "scan-reset-authority";
state.scanRunActive = true;
let stopCalls = 0;
window.MorphicWorkbenchApi.stopScanJob = async () => {
  stopCalls += 1;
  if (stopCalls === 1) throw new Error("stop unavailable");
  return {job_id: "scan-reset-authority", status: "stopped"};
};
window.MorphicWorkbenchApi.loadScanProfileCatalog = async (level) => ({
  profile_level: Number(level),
  pool_authority: {fingerprint: "a".repeat(64)},
  internal: internalPool(),
  external: {},
});

global.__morphicGate3TestOperation = (async () => {
  const failed = await resetWorkbenchForNewCase();
  if (failed !== false || readExistingStartOperationId("scan") !== operationId) {
    throw new Error("failed stop released durable operation authority");
  }
  if (state.activeJobId !== "scan-reset-authority" || !state.scanRunActive) {
    throw new Error("failed stop released active job reservation");
  }

  const completed = await resetWorkbenchForNewCase();
  if (!completed || stopCalls !== 2 || readExistingStartOperationId("scan") !== null) {
    throw new Error(`terminal stop did not clear/reset: ${completed}/${stopCalls}`);
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_stale_preview_cannot_overwrite_new_level_or_newer_preview() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
controls.profile_level.value = "3";
state.scanProfileCatalogStatus = "ready";
state.scanProfileCatalogLevel = 3;
state.scanProfileCatalog = {
  profile_level: 3,
  pool_authority: {fingerprint: "6".repeat(64)},
  internal: internalPool(),
};
const previewRequests = [];
const renderedPayloads = [];
nodes["#command-preview"].textContent = "BEFORE-LEVEL-CHANGE";
window.MorphicWorkbenchApi.loadScanPreview = async (payload) => new Promise(
  resolve => previewRequests.push({payload, resolve})
);
window.MorphicWorkbenchApi.loadScanProfileCatalog = async (level) => ({
  profile_level: Number(level),
  pool_authority: {fingerprint: "7".repeat(64)},
  internal: internalPool(),
  external: {},
});
window.MorphicWorkbenchRender.renderReviewCards = payload => {
  renderedPayloads.push(payload);
};

global.__morphicGate3TestOperation = (async () => {
  const oldPreview = generatePreview();
  await Promise.resolve();
  controls.profile_level.value = "4";
  await loadScanProfileCatalog(4);
  previewRequests[0].resolve({command: ["STALE-LEVEL-3"]});
  await oldPreview;
  if (
    nodes["#command-preview"].textContent !== "BEFORE-LEVEL-CHANGE"
    || renderedPayloads.length !== 0
    || nodes["#preview-state"].textContent === "Vorschau bereit"
  ) throw new Error("level change did not invalidate old preview");

  const supersededPreview = generatePreview();
  const currentPreview = generatePreview();
  await Promise.resolve();
  previewRequests[2].resolve({command: ["CURRENT-LEVEL-4"]});
  await currentPreview;
  previewRequests[1].resolve({command: ["SUPERSEDED-LEVEL-4"]});
  await supersededPreview;

  if (nodes["#command-preview"].textContent !== "CURRENT-LEVEL-4") {
    throw new Error(`stale preview overwrote command: ${nodes["#command-preview"].textContent}`);
  }
  if (
    renderedPayloads.length !== 1
    || renderedPayloads[0].profile_level !== 4
    || nodes["#preview-state"].textContent !== "Vorschau bereit"
  ) throw new Error("stale preview overwrote review or status");
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_scan_start_invalidates_an_older_preview_response() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
controls.profile_level.value = "3";
state.scanProfileCatalogStatus = "ready";
state.scanProfileCatalogLevel = 3;
state.scanProfileCatalog = {
  profile_level: 3,
  pool_authority: {fingerprint: "8".repeat(64)},
  internal: internalPool(),
};
let resolvePreview;
let rejectStart;
let renderCalls = 0;
nodes["#command-preview"].textContent = "UNCHANGED";
window.MorphicWorkbenchApi.loadScanPreview = async () => new Promise(
  resolve => { resolvePreview = resolve; }
);
window.MorphicWorkbenchApi.startScanJob = async () => new Promise(
  (_resolve, reject) => { rejectStart = reject; }
);
window.MorphicWorkbenchRender.renderReviewCards = () => { renderCalls += 1; };

global.__morphicGate3TestOperation = (async () => {
  const previewRequest = generatePreview();
  await Promise.resolve();
  const startRequest = startScanJob();
  await Promise.resolve();
  resolvePreview({command: ["STALE-BEFORE-START"]});
  await previewRequest;

  if (nodes["#command-preview"].textContent !== "UNCHANGED" || renderCalls !== 0) {
    throw new Error("preview response rendered after scan start");
  }
  if (nodes["#preview-state"].textContent !== "Analyse wird gestartet...") {
    throw new Error(`preview response overwrote start status: ${nodes["#preview-state"].textContent}`);
  }

  rejectStart(Object.assign(new Error("stop test start"), {
    status: 500,
    startOperationDisposition: "safe-to-replace",
  }));
  await startRequest;
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_catalog_rejects_invalid_fingerprint_before_ready() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const invalidFingerprints = [null, "A".repeat(64), "a".repeat(63), "g".repeat(64)];
let responseIndex = 0;
window.MorphicWorkbenchApi.loadScanProfileCatalog = async () => {
  const fingerprint = invalidFingerprints[responseIndex++];
  return {
    profile_level: 3,
    pool_authority: fingerprint === null ? {} : {fingerprint},
    internal: {},
    external: {},
  };
};

global.__morphicGate3TestOperation = (async () => {
  for (const fingerprint of invalidFingerprints) {
    await loadScanProfileCatalog(3);
    if (
      state.scanProfileCatalogStatus !== "error"
      || state.scanProfileCatalog !== null
      || !nodes["#preview-button"].disabled
      || !nodes["#start-analysis-button"].disabled
    ) throw new Error(`invalid fingerprint reached ready: ${fingerprint}`);
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_ready_pool_renders_response_summary_badges_and_search_without_mutation() -> None:
    body = r"""
const scope = cards["#review-scan-scope"];
const catalog = {
  profile_level: 4,
  pool_authority: {
    source: "legacy",
    label: "Legacy",
    revision: null,
    revision_short: null,
    fingerprint: "abcdef123456" + "0".repeat(52),
    fingerprint_short: "abcdef123456",
  },
  internal: {
    count: 208,
    profiles: [
      {id: "zeta-id", label: "beta <img src=x onerror=alert(1)>"},
      {id: "b-id", label: "Alpha"},
      {id: "a-id", label: "alpha"},
      ...Array.from({length: 205}, (_, index) => ({
        id: `zz-${String(index).padStart(3, "0")}`,
        label: `ZZ Profil ${String(index).padStart(3, "0")}`,
      })),
    ],
  },
  external: {
    count: 0,
    active_source_count: 2,
    active_sources: [],
    integration_status: "registry_only",
    scan_effect: false,
  },
  total_scan_profiles: 999,
};
const before = JSON.stringify(catalog);
window.MorphicWorkbenchState.scanProfileCatalogStatus = "ready";
window.MorphicWorkbenchRender.renderReviewCards(
  {profile_level: 99, top_n: 5},
  {components: {}},
  catalog,
);

const summary = find(scope, ".scan-scope-summary");
if (summary?.textContent !== "Level 4 prüft 208 interne Screening-Profile; anschließend werden Top-5 vollständig analysiert.") {
  throw new Error(`falsche Ready-Zusammenfassung: ${summary?.textContent}`);
}
const badges = findAll(scope, ".scan-pool-badge").map((node) => node.textContent);
for (const expected of ["Poolquelle: Legacy", "Fingerprint: abcdef123456"]) {
  if (!badges.includes(expected)) throw new Error(`Badge fehlt: ${expected} in ${badges}`);
}
if (scope.textContent.includes("999")) throw new Error("total_scan_profiles leaked into summary");

const internal = find(scope, ".scan-pool-internal");
if (!internal || internal.tagName !== "DETAILS") throw new Error("interne Details fehlen");
const search = find(internal, ".scan-profile-search");
const searchLabel = find(internal, ".scan-profile-search-label");
if (
  !search
  || search.type !== "search"
  || !search.id
  || searchLabel?.getAttribute("for") !== search.id
  || search.getAttribute("aria-label") !== "Interne Profile durchsuchen"
) throw new Error("Suchfeld ist nicht korrekt beschriftet");

const items = findAll(internal, ".scan-profile-item");
const ids = items.map((item) => find(item, ".scan-profile-id")?.textContent);
if (JSON.stringify(ids.slice(0, 3)) !== JSON.stringify(["a-id", "b-id", "zeta-id"])) {
  throw new Error(`Profile nicht nach Label und ID sortiert: ${JSON.stringify(ids.slice(0, 3))}`);
}
const labels = items.map((item) => find(item, ".scan-profile-label")?.textContent);
if (labels[2] !== "beta <img src=x onerror=alert(1)>" || internal.querySelectorAll("img").length) {
  throw new Error("Profilwerte wurden nicht als sicherer Text gerendert");
}
if (items.some((item) => item.hidden)) throw new Error("Profile sind initial gefiltert");
const counter = find(internal, ".scan-profile-counter");
if (counter?.textContent !== "208 von 208 Profilen") {
  throw new Error(`falscher Initialzaehler: ${counter?.textContent}`);
}

search.value = "BETA";
search.dispatchEvent(new Event("input"));
if (items.filter((item) => !item.hidden).length !== 1) throw new Error("Labelsuche filtert nicht case-insensitive");
if (counter.textContent !== "1 von 208 Profilen") throw new Error(`falscher Suchzaehler: ${counter.textContent}`);

search.value = "B-ID";
search.dispatchEvent(new Event("input"));
if (items.filter((item) => !item.hidden).length !== 1) throw new Error("ID-Suche filtert nicht case-insensitive");

search.value = "kein-treffer";
search.dispatchEvent(new Event("input"));
const empty = find(internal, ".scan-profile-empty");
if (items.some((item) => !item.hidden) || empty?.hidden !== false) {
  throw new Error("Nulltrefferzustand fehlt");
}
if (counter.textContent !== "0 von 208 Profilen") throw new Error(`falscher Nullzaehler: ${counter.textContent}`);
if (JSON.stringify(catalog) !== before) throw new Error("Responsepayload wurde mutiert");
"""

    result = _run_render_script(body)

    assert result.returncode == 0, result.stderr


def test_invalid_top_n_review_warns_without_claiming_full_analysis() -> None:
    body = r"""
const scope = cards["#review-scan-scope"];
const catalog = {
  profile_level: 1,
  pool_authority: {label: "Legacy", fingerprint_short: "abcdef123456"},
  internal: {
    count: 5,
    profiles: Array.from({length: 5}, (_, index) => ({
      id: `profile-${index + 1}`,
      label: `Profil ${index + 1}`,
    })),
  },
  external: {count: 0, active_source_count: 0, active_sources: []},
};
window.MorphicWorkbenchState.scanProfileCatalogStatus = "ready";
window.MorphicWorkbenchRender.renderReviewCards(
  {profile_level: 1, top_n: 9},
  {components: {}},
  catalog,
);

const invalidSummary = find(scope, ".scan-scope-summary");
const warning = find(scope, ".scan-pool-topn-warning");
if (invalidSummary?.textContent.includes("vollständig analysiert")) {
  throw new Error(`ungültiges Review behauptet Vollanalyse: ${invalidSummary.textContent}`);
}
if (
  warning?.textContent !== "Top-N überschreitet den bestätigten Scanprofil-Pool. Bitte Auswahl anpassen."
  || warning.getAttribute("role") !== "status"
) throw new Error(`klare Top-N-Warnung fehlt: ${warning?.textContent}`);

window.MorphicWorkbenchRender.renderReviewCards(
  {profile_level: 1, top_n: 5},
  {components: {}},
  catalog,
);
const validSummary = find(scope, ".scan-scope-summary");
if (!validSummary?.textContent.includes("Top-5 vollständig analysiert")) {
  throw new Error(`gültiges Review erholt sich nicht: ${validSummary?.textContent}`);
}
if (find(scope, ".scan-pool-topn-warning")) throw new Error("Warnung blieb nach Recovery sichtbar");
"""

    result = _run_render_script(body)

    assert result.returncode == 0, result.stderr


def test_external_registry_sources_are_separate_redacted_and_non_interactive() -> None:
    body = r"""
const scope = cards["#review-scan-scope"];
const catalog = {
  profile_level: 4,
  pool_authority: {label: "Legacy", fingerprint_short: "abcdef123456"},
  internal: {count: 1, profiles: [{id: "intern", label: "Intern"}]},
  external: {
    count: 0,
    active_source_count: 2,
    integration_status: "registry_only",
    scan_effect: false,
    activation_available: false,
    activation_gate: "gate_14",
    active_sources: [
      {
        id: "z-source",
        label: "Zeta Registry",
        scan_effect: false,
        reason_code: "registry_metadata_only",
        path: "C:\\secret\\registry.json",
        loader: "internal-loader",
        notes: "private notes",
        url: "https://secret.invalid/catalog",
      },
      {id: "a-source", label: "Alpha Registry", scan_effect: false},
    ],
  },
};
window.MorphicWorkbenchState.scanProfileCatalogStatus = "ready";
window.MorphicWorkbenchRender.renderReviewCards(
  {top_n: 1},
  {components: {}},
  catalog,
);

const external = find(scope, ".scan-pool-external");
if (!external || external.tagName !== "DETAILS") throw new Error("separate externe Details fehlen");
for (const expected of [
  "2 Registry-Quellen sind betriebsbereit; 0 als Scanprofile freigegeben.",
  "Keine Wirkung auf diesen Scan, Profilpool oder Score.",
  "Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14.",
]) {
  if (!external.textContent.includes(expected)) throw new Error(`externe Wahrheit fehlt: ${expected}`);
}
const sources = findAll(external, ".registry-source-item");
if (sources.length !== 2 || sources.some((source) => !source.textContent.includes("keine Scanwirkung"))) {
  throw new Error("Source-Eintrag ohne Kennzeichnung der Scanwirkung");
}
const sourceIds = sources.map((source) => find(source, ".registry-source-id")?.textContent);
if (JSON.stringify(sourceIds) !== JSON.stringify(["a-source", "z-source"])) {
  throw new Error(`Registry-Quellen nicht alphabetisch: ${JSON.stringify(sourceIds)}`);
}
if (external.querySelectorAll("input").length || external.querySelectorAll("button").length) {
  throw new Error("externer Container enthaelt Controls");
}
for (const forbidden of ["C:\\secret", "internal-loader", "private notes", "https://secret.invalid"]) {
  if (external.textContent.includes(forbidden)) throw new Error(`nicht redigiertes Sourcefeld: ${forbidden}`);
}
"""

    result = _run_render_script(body)

    assert result.returncode == 0, result.stderr


def test_pool_loading_and_error_states_are_semantic_and_retry_by_dom_event() -> None:
    body = r"""
const scope = cards["#review-scan-scope"];
window.MorphicWorkbenchState.scanProfileCatalogStatus = "loading";
window.MorphicWorkbenchRender.renderReviewCards({}, {components: {}}, null);
const loading = find(scope, ".scan-pool-loading");
if (
  loading?.getAttribute("role") !== "status"
  || loading.getAttribute("aria-live") !== "polite"
  || loading.getAttribute("tabindex") !== "-1"
  || !loading.textContent.includes("Scanprofil-Pool wird geladen")
) throw new Error("semantischer Ladezustand fehlt");
const skeleton = find(scope, ".scan-pool-skeleton");
if (skeleton?.getAttribute("aria-hidden") !== "true") throw new Error("Ladeskeleton fehlt");
if (/0 Profile|0 Profilen/.test(scope.textContent)) throw new Error("Loading behauptet einen Nullpool");

let retries = 0;
window.MorphicWorkbenchActions.retryScanProfileCatalog = () => { retries += 1; };
window.MorphicWorkbenchState.scanProfileCatalogStatus = "error";
window.MorphicWorkbenchState.scanProfileCatalogError = "Scanprofil-Pool konnte nicht geladen werden (HTTP 503). Bitte erneut versuchen.";
window.MorphicWorkbenchRender.renderReviewCards({}, {components: {}}, null);
const error = find(scope, ".scan-pool-error");
if (
  error?.getAttribute("role") !== "status"
  || error.getAttribute("aria-live") !== "assertive"
  || error.textContent !== window.MorphicWorkbenchState.scanProfileCatalogError
) throw new Error(`redigierter Fehlerzustand fehlt: ${error?.textContent}`);
if (/0 Profile|0 Profilen/.test(scope.textContent)) throw new Error("Error behauptet einen Nullpool");
const retry = find(scope, ".scan-pool-retry");
if (!retry || retry.type !== "button") throw new Error("Retrybutton fehlt");
retry.click();
if (retries !== 1) throw new Error(`Retryevent nicht delegiert: ${retries}`);
"""

    result = _run_render_script(body)

    assert result.returncode == 0, result.stderr


def test_catalog_runtime_hint_and_error_handoff_stay_redacted_and_scan_neutral() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const integration = nodes["#source-analysis-integration"];
const previewState = nodes["#preview-state"];
const preview = nodes["#preview-button"];
const start = nodes["#start-analysis-button"];
const loadingText = "Registry-Prüfung läuft; Scanprofil-Pool wird geladen. Keine Wirkung auf diesen Scan, Profilpool oder Score. Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14.";
const loadingActionText = "Scanprofil-Pool wird geladen; Vorschau und Start bleiben gesperrt.";
const readyActionText = "Scanprofil-Pool ist für das gewählte Level bestätigt.";
const errorActionText = "Scanprofil-Pool konnte nicht bestätigt werden; Vorschau und Start bleiben gesperrt.";
const readyCatalog = {
  profile_level: 3,
  pool_authority: {fingerprint: "a".repeat(64)},
  internal: {count: 208, profiles: []},
  external: {
    count: 0,
    active_source_count: 2,
    active_sources: [{id: "one"}],
  },
};

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return {promise, resolve, reject};
}

global.__morphicGate3TestOperation = (async () => {
  integration.textContent = "9 Registry-Quellen; 7 Scanprofile";
  previewState.textContent = "Vorschau bereit";
  previewState.className = "inline-state ok";
  preview.disabled = false;
  start.disabled = false;
  const first = deferred();
  window.MorphicWorkbenchApi.loadScanProfileCatalog = () => first.promise;
  const firstLoad = loadScanProfileCatalog(3);
  if (integration.textContent !== loadingText || /\b(?:9|7|0)\b/.test(integration.textContent)) {
    throw new Error(`Loading behielt alte oder hardcodierte Counts: ${integration.textContent}`);
  }
  if (
    previewState.textContent !== loadingActionText
    || previewState.className !== "inline-state neutral"
    || !preview.disabled
    || !start.disabled
  ) throw new Error(`Loading-Aktionsstatus ist falsch: ${previewState.textContent}/${previewState.className}`);
  first.resolve(readyCatalog);
  await firstLoad;
  const expected = "2 Registry-Quellen sind betriebsbereit; 0 als Scanprofile freigegeben. Keine Wirkung auf diesen Scan, Profilpool oder Score. Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14.";
  if (integration.textContent !== expected) {
    throw new Error(`Runtime-Hinweis ist nicht Gate-3-neutral: ${integration.textContent}`);
  }
  if (/\baktiv\b/i.test(integration.textContent)) throw new Error("Registryquelle wird schlicht aktiv genannt");
  if (previewState.textContent !== readyActionText || previewState.className !== "inline-state ok") {
    throw new Error(`Ready-Aktionsstatus ist falsch: ${previewState.textContent}/${previewState.className}`);
  }

  const raw = "C:\\private\\registry.json <img src=x onerror=alert(1)>";
  const second = deferred();
  window.MorphicWorkbenchApi.loadScanProfileCatalog = () => second.promise;
  const secondLoad = loadScanProfileCatalog(3);
  if (integration.textContent !== loadingText || integration.textContent.includes("2 Registry")) {
    throw new Error(`Reload behielt Ready-Counts: ${integration.textContent}`);
  }
  second.reject(Object.assign(new Error(raw), {status: 503}));
  await secondLoad;
  const expectedError = "Scanprofil-Pool konnte nicht geladen werden (HTTP 503). Bitte erneut versuchen.";
  const expectedErrorIntegration = `${expectedError} Keine Wirkung auf diesen Scan, Profilpool oder Score. Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14.`;
  if (state.scanProfileCatalogStatus !== "error" || state.scanProfileCatalogError !== expectedError) {
    throw new Error(`Fehler wurde nicht redigiert: ${state.scanProfileCatalogError}`);
  }
  if (
    integration.textContent !== expectedErrorIntegration
    || integration.textContent.includes(raw)
    || integration.textContent.includes("2 Registry")
  ) {
    throw new Error("rohes Fehlerdetail gelangte in den Runtime-Hinweis");
  }
  if (previewState.textContent !== errorActionText || previewState.className !== "inline-state bad") {
    throw new Error(`Error-Aktionsstatus ist falsch: ${previewState.textContent}/${previewState.className}`);
  }
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_catalog_response_does_not_overwrite_a_newer_preview_or_start_status() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
let resolveCatalog;
window.MorphicWorkbenchApi.loadScanProfileCatalog = () => new Promise(
  resolve => { resolveCatalog = resolve; }
);

global.__morphicGate3TestOperation = (async () => {
  const loading = loadScanProfileCatalog(3);
  showInlineState("Analyse wird gestartet...", "neutral");
  resolveCatalog({
    profile_level: 3,
    pool_authority: {fingerprint: "b".repeat(64)},
    internal: {count: 55, profiles: []},
    external: {count: 0, active_source_count: 2, active_sources: []},
  });
  await loading;
  if (
    state.scanProfileCatalogStatus !== "ready"
    || nodes["#preview-state"].textContent !== "Analyse wird gestartet..."
    || nodes["#preview-state"].className !== "inline-state neutral"
  ) throw new Error("Katalogresponse überschrieb einen neueren Prozessstatus");
})();
"""

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("outcome", ["ready", "error"])
@pytest.mark.parametrize(
    ("state_overrides", "existing_text", "existing_class", "ready_preview_disabled"),
    [
        (
            {"scanRunActive": True},
            "Analyse läuft; Fortschritt wird aktualisiert.",
            "inline-state neutral",
            True,
        ),
        (
            {"scanStartPending": True},
            "Analyse wird gestartet...",
            "inline-state neutral",
            True,
        ),
        (
            {
                "resetInProgress": True,
                "scanStartPending": True,
                "scanRunActive": True,
            },
            "Fallwechsel wartet auf den Abschluss der laufenden Serveraktion.",
            "inline-state bad",
            True,
        ),
    ],
)
def test_catalog_status_never_overwrites_higher_priority_scan_or_reset_owner(
    outcome: str,
    state_overrides: dict[str, bool],
    existing_text: str,
    existing_class: str,
    ready_preview_disabled: bool,
) -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const previewState = nodes["#preview-state"];
const preview = nodes["#preview-button"];
const start = nodes["#start-analysis-button"];
const integration = nodes["#source-analysis-integration"];
const outcome = __OUTCOME__;
const existingText = __EXISTING_TEXT__;
const existingClass = __EXISTING_CLASS__;
const expectedReadyPreviewDisabled = __READY_PREVIEW_DISABLED__;
Object.assign(state, __STATE_OVERRIDES__);
state.currentStepIndex = 5;
state.scanProfileCatalogStatus = "ready";
state.scanProfileCatalogLevel = 3;
state.scanProfileCatalog = {
  profile_level: 3,
  pool_authority: {fingerprint: "9".repeat(64)},
};
previewState.textContent = existingText;
previewState.className = existingClass;
preview.disabled = false;
start.disabled = false;
integration.textContent = "alter Quellenstatus";

let resolveCatalog;
let rejectCatalog;
window.MorphicWorkbenchApi.loadScanProfileCatalog = () => new Promise((resolve, reject) => {
  resolveCatalog = resolve;
  rejectCatalog = reject;
});
const renders = [];
window.MorphicWorkbenchRender.renderReviewCards = (_formData, _hardware, catalog) => {
  renders.push({status: state.scanProfileCatalogStatus, catalog});
};

global.__morphicGate3TestOperation = (async () => {
  const request = loadScanProfileCatalog(3);
  if (previewState.textContent !== existingText || previewState.className !== existingClass) {
    throw new Error(`Loading übernahm höherrangigen Status: ${previewState.textContent}/${previewState.className}`);
  }
  if (!preview.disabled || !start.disabled) {
    throw new Error(`Loading entsperrte Aktionen: ${preview.disabled}/${start.disabled}`);
  }
  if (!integration.textContent.includes("Registry-Prüfung läuft")) {
    throw new Error(`Source-Loading wurde nicht aktualisiert: ${integration.textContent}`);
  }
  if (renders.length !== 1 || renders[0].status !== "loading" || renders[0].catalog !== null) {
    throw new Error("Reviewkarte erhielt den Loadingzustand nicht");
  }

  if (outcome === "ready") {
    resolveCatalog({
      profile_level: 3,
      pool_authority: {fingerprint: "a".repeat(64)},
      internal: {count: 55, profiles: []},
      external: {count: 0, active_source_count: 4, active_sources: []},
    });
  } else {
    rejectCatalog(Object.assign(new Error("C:\\private\\raw-error"), {status: 503}));
  }
  await request;

  if (previewState.textContent !== existingText || previewState.className !== existingClass) {
    throw new Error(`${outcome} übernahm höherrangigen Status: ${previewState.textContent}/${previewState.className}`);
  }
  if (outcome === "ready") {
    if (preview.disabled !== expectedReadyPreviewDisabled || !start.disabled) {
      throw new Error(`Ready verletzte Action-Gate: ${preview.disabled}/${start.disabled}`);
    }
    if (!integration.textContent.includes("4 Registry-Quellen sind betriebsbereit")) {
      throw new Error(`Source-Ready wurde nicht aktualisiert: ${integration.textContent}`);
    }
    if (renders.length !== 2 || renders[1].status !== "ready" || !renders[1].catalog) {
      throw new Error("Reviewkarte erhielt den Readyzustand nicht");
    }
  } else {
    if (!preview.disabled || !start.disabled) {
      throw new Error(`Error entsperrte Aktionen: ${preview.disabled}/${start.disabled}`);
    }
    if (
      !integration.textContent.includes("Keine Wirkung auf diesen Scan, Profilpool oder Score.")
      || !integration.textContent.includes("Gate 14")
      || integration.textContent.includes("C:\\private")
    ) throw new Error(`Source-Error ist nicht redigiert/invariant: ${integration.textContent}`);
    if (renders.length !== 2 || renders[1].status !== "error" || renders[1].catalog !== null) {
      throw new Error("Reviewkarte erhielt den Errorzustand nicht");
    }
  }
})();
"""
    body = (
        body.replace("__OUTCOME__", json.dumps(outcome))
        .replace("__EXISTING_TEXT__", json.dumps(existing_text))
        .replace("__EXISTING_CLASS__", json.dumps(existing_class))
        .replace("__READY_PREVIEW_DISABLED__", json.dumps(ready_preview_disabled))
        .replace("__STATE_OVERRIDES__", json.dumps(state_overrides))
    )

    result = _run_app_script(body)

    assert result.returncode == 0, result.stderr


def test_retry_focus_follows_loading_then_ready_or_error_only_after_explicit_retry() -> None:
    body = r"""
const scope = cards["#review-scan-scope"];
const state = window.MorphicWorkbenchState;
const readyCatalog = {
  profile_level: 3,
  pool_authority: {label: "Legacy", fingerprint_short: "abcdef123456"},
  internal: {count: 1, profiles: [{id: "internal", label: "Intern"}]},
  external: {count: 0, active_source_count: 0, active_sources: []},
};
let request;
let actionPromise;

function deferred() {
  let resolve;
  const promise = new Promise(resolvePromise => { resolve = resolvePromise; });
  return {promise, resolve};
}
function render(catalog = null) {
  window.MorphicWorkbenchRender.renderReviewCards(
    {top_n: 1},
    {components: {}},
    catalog,
  );
}
window.MorphicWorkbenchActions.retryScanProfileCatalog = () => {
  request = deferred();
  state.scanProfileCatalogStatus = "loading";
  render();
  actionPromise = request.promise.then((result) => {
    if (result === "ready") {
      state.scanProfileCatalogStatus = "ready";
      render(readyCatalog);
    } else {
      state.scanProfileCatalogStatus = "error";
      state.scanProfileCatalogError = "Scanprofil-Pool konnte nicht geladen werden (HTTP 503). Bitte erneut versuchen.";
      render();
    }
  });
  return actionPromise;
};

global.__morphicGate3TestOperation = (async () => {
  const outside = element("button");
  outside.focus();
  state.scanProfileCatalogStatus = "loading";
  render();
  if (document.activeElement !== outside) throw new Error("Bootstrap-/Level-Loading verschob den Fokus");
  state.scanProfileCatalogStatus = "ready";
  render(readyCatalog);
  if (document.activeElement !== outside) throw new Error("nicht explizites Ready verschob den Fokus");

  state.scanProfileCatalogStatus = "error";
  state.scanProfileCatalogError = "Scanprofil-Pool konnte nicht geladen werden (HTTP 503). Bitte erneut versuchen.";
  render();
  const firstRetry = find(scope, ".scan-pool-retry");
  firstRetry.focus();
  firstRetry.dispatchEvent(new Event("click"));
  const firstLoading = find(scope, ".scan-pool-loading");
  if (
    document.activeElement !== firstLoading
    || firstLoading?.getAttribute("tabindex") !== "-1"
  ) throw new Error("expliziter Retry fokussierte den Loadingstatus nicht");
  request.resolve("ready");
  await actionPromise;
  await Promise.resolve();
  const internalSummary = find(scope, ".scan-pool-internal-summary");
  if (document.activeElement !== internalSummary || internalSummary?.tagName !== "SUMMARY") {
    throw new Error("erfolgreicher Retry fokussierte die interne Pool-Zusammenfassung nicht");
  }

  state.scanProfileCatalogStatus = "error";
  render();
  const secondRetry = find(scope, ".scan-pool-retry");
  secondRetry.focus();
  secondRetry.dispatchEvent(new Event("click"));
  if (document.activeElement !== find(scope, ".scan-pool-loading")) {
    throw new Error("zweiter Retry fokussierte den Loadingstatus nicht");
  }
  request.resolve("error");
  await actionPromise;
  await Promise.resolve();
  const currentRetry = find(scope, ".scan-pool-retry");
  if (document.activeElement !== currentRetry || currentRetry === secondRetry) {
    throw new Error("fehlgeschlagener Retry fokussierte den neuen Retrybutton nicht");
  }
})();
"""

    result = _run_render_script(body)

    assert result.returncode == 0, result.stderr


def test_pool_copy_and_css_are_local_responsive_and_count_free() -> None:
    renderer = RENDER_JS.read_text(encoding="utf-8")
    styles = APP_CSS.read_text(encoding="utf-8")
    html = INDEX_HTML.read_text(encoding="utf-8")

    assert "208" not in renderer
    assert "internal.count || 0" not in renderer
    assert "external.count || 0" not in renderer
    assert "Keine Wirkung auf diesen Scan, Profilpool oder Score." in html
    assert "Gate 14" in html
    source_hint = re.search(
        r'<div id="source-analysis-integration"[^>]*>\s*(.*?)\s*</div>',
        html,
        re.DOTALL,
    )
    assert source_hint is not None
    assert source_hint.group(1) == (
        "Registry-Prüfung läuft; Scanprofil-Pool wird geladen. "
        "Keine Wirkung auf diesen Scan, Profilpool oder Score. "
        "Externe Scanprofile erst nach validierter Catalog-Freigabe in Gate 14."
    )
    assert re.findall(r"\b\d+\b", source_hint.group(1)) == ["14"]
    for selector in (
        ".review-scan-scope .scan-pool-details",
        ".review-scan-scope .scan-profile-search",
        ".review-scan-scope .scan-profile-list",
        ".review-scan-scope .registry-source-list",
        ".review-scan-scope .scan-pool-badges",
    ):
        assert selector in styles
    assert "max-width: 100%;" in styles
    assert "min-width: 0;" in styles
    assert "overflow-wrap: anywhere;" in styles
    body_rule = re.search(r"(?m)^body\s*\{([^}]*)\}", styles, re.DOTALL)
    assert body_rule is not None
    assert not re.search(r"min-width\s*:\s*320px", body_rule.group(1))
