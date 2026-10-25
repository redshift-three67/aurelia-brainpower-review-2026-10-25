from __future__ import annotations

import json
import re
import secrets
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
API_JS = ROOT / "apps" / "web" / "static" / "workbench-api.js"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
APP_CSS = ROOT / "apps" / "web" / "static" / "app.css"
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"
STATE_JS = ROOT / "apps" / "web" / "static" / "workbench-state.js"
EMF_PY = ROOT / "apps" / "web" / "emf.py"
MONITOR_JS = ROOT / "apps" / "web" / "static" / "emf-monitor.js"
MONITOR_CSS = ROOT / "apps" / "web" / "static" / "emf-monitor.css"
NODE_HARNESS_TIMEOUT_SECONDS = 10
EMF_PROXY_LABEL = "System-/Entropie-basierter EMF-Proxy-Index"
EMF_PROXY_DERIVED_COPY = (
    "Abgeleiteter System-/Entropie-Proxy; keine physische Feldmessung."
)


def _isolated_css_declarations(css: str, selector: str) -> dict[str, str]:
    rules = re.findall(
        rf"(?ms)^\s*{re.escape(selector)}\s*\{{(?P<body>[^{{}}]*)\}}",
        css,
    )
    assert len(rules) == 1
    return {
        match.group("name").lower(): match.group("value").strip().lower()
        for match in re.finditer(
            r"(?P<name>[a-z-]+)\s*:\s*(?P<value>[^;]+);",
            rules[0],
        )
    }


def _hex_contrast_ratio(foreground: str, background: str) -> float:
    def luminance(value: str) -> float:
        digits = value.removeprefix("#")
        if len(digits) == 3:
            digits = "".join(character * 2 for character in digits)
        assert len(digits) == 6
        channels = [int(digits[index : index + 2], 16) / 255 for index in (0, 2, 4)]
        linear = [
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    foreground_luminance = luminance(foreground)
    background_luminance = luminance(background)
    lighter = max(foreground_luminance, background_luminance)
    darker = min(foreground_luminance, background_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def _run_app_script(body: str) -> subprocess.CompletedProcess[str]:
    harness = r"""
const fs = require("fs");
const vm = require("vm");

function node(overrides = {}) {
  const listeners = new Map();
  const attributes = new Map();
  return {
    textContent: "",
    className: "",
    disabled: false,
    checked: false,
    hidden: false,
    value: "",
    selectedIndex: 0,
    style: {},
    dataset: {},
    children: [],
    options: [],
    addEventListener(type, listener) {
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(listener);
    },
    dispatchEvent(event) {
      event.target = this;
      for (const listener of listeners.get(event.type) || []) listener.call(this, event);
    },
    appendChild(child) { this.children.push(child); return child; },
    replaceChildren(...children) { this.children = children; },
    querySelectorAll() { return []; },
    reset() {},
    focus() {},
    scrollIntoView() {},
    setAttribute(name, value) { attributes.set(name, String(value)); },
    getAttribute(name) { return attributes.get(name) || null; },
    removeAttribute(name) { attributes.delete(name); },
    ...overrides,
  };
}

const controls = {
  last_name: node({value: "Gate"}),
  first_name: node({value: "Five"}),
  birth_date: node({value: "01011980"}),
  birth_place: node({value: "Berlin"}),
  birth_time: node({value: ""}),
  email: node({value: ""}),
  notes: node({value: ""}),
  focus: node({value: "EMF authority"}),
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
  local_ai_enabled: node({type: "checkbox", checked: false}),
  planetary_vector_enabled: node({type: "checkbox", checked: false}),
  planet_type: node({value: ""}),
};
const scanForm = node({fields: controls});
const nodes = {
  "#scan-form": scanForm,
  "#consent-local": node({checked: true}),
  "#consent-safety": node({checked: true}),
  "#emf-telemetry-state": node(),
  "#emf-enable-button": node(),
  "#emf-disable-button": node(),
  "#new-case-button": node(),
  "#hardware-truth-grid": node(),
  "#realtime-calibration": node(),
  "#hardware-gate-warnings": node(),
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
  body: node({dataset: {}}),
  querySelector(selector) {
    if (nodes[selector]) return nodes[selector];
    const match = selector.match(/name="([^"]+)"/);
    return match ? controls[match[1]] || null : null;
  },
  querySelectorAll() { return []; },
  createElement() { return node(); },
  createTextNode(value) { return node({textContent: String(value)}); },
};

const storageWrites = [];
const sessionWrites = [];
const storage = new Map();
const windowListeners = {};
global.window = {
  innerWidth: 1024,
  addEventListener(type, listener) { windowListeners[type] = listener; },
  localStorage: {
    getItem(key) { return storage.has(key) ? storage.get(key) : null; },
    setItem(key, value) {
      storageWrites.push([key, String(value)]);
      storage.set(key, String(value));
    },
    removeItem(key) { storage.delete(key); },
  },
  sessionStorage: {
    getItem() { return null; },
    setItem(key, value) { sessionWrites.push([key, String(value)]); },
    removeItem() {},
  },
  MorphicWorkbenchState: {
    registry: null,
    currentStepId: "runtime",
    currentStepIndex: 0,
    workbenchMode: "standard",
    selectedSolfeggioBase: 432,
    activeJobId: null,
    scanStartOperationId: null,
    scanStartPending: false,
    scanRunActive: false,
    activeReportId: null,
    activeReportSessionId: null,
    reportFocusId: null,
    activeHarmonizationJobId: null,
    harmonizationStartPending: false,
    harmonizationRunActive: false,
    emfTelemetryActive: null,
    emfTelemetryStatus: "unknown",
    emfTelemetryMutationPending: false,
    emfTelemetryMutationUnresolved: false,
    hardwareTruth: null,
    scanProfileCatalog: null,
    scanProfileCatalogStatus: "loading",
    scanProfileCatalogError: "",
    scanProfileCatalogLevel: null,
    pendingMutations: 0,
    resetInProgress: false,
    hasFocusHistoryConsent() { return false; },
    setFocusHistoryConsent() {},
    loadFocusHistory() { return []; },
    clearFocusHistory() {},
    saveFocusToHistory() {},
  },
  MorphicWorkbenchRender: {
    renderStepper() {},
    showStep() {},
    renderHardwareTruth(payload) { global.__renderedHardware.push(payload); },
    renderReviewCards() {},
    renderChoiceCards() {},
    renderFocusHistoryChips() {},
    renderResults() {},
    renderRunTrace() {},
    renderSubstepTimeline() {},
    resetSubstepTimeline() {},
    setModePill() {},
  },
};

global.__renderedHardware = [];
let fetchImpl = async (url, options) => {
  throw new Error(`unexpected request: ${String(options?.method || "GET").toUpperCase()} ${url}`);
};
global.fetch = (url, options = {}) => fetchImpl(url, options);

function response(payload, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: {get() { return null; }},
    async json() { return payload; },
  };
}
function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((done, fail) => { resolve = done; reject = fail; });
  return {promise, resolve, reject};
}
async function waitUntil(predicate) {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    if (predicate()) return;
    await Promise.resolve();
  }
  throw new Error("timed out waiting for controlled promise boundary");
}
function resetEmfDom(active, status = "ready") {
  window.MorphicWorkbenchState.emfTelemetryActive = active;
  window.MorphicWorkbenchState.emfTelemetryStatus = status;
  window.MorphicWorkbenchState.emfTelemetryMutationPending = false;
  window.MorphicWorkbenchState.emfTelemetryMutationUnresolved = false;
  nodes["#emf-enable-button"].disabled = active === true;
  nodes["#emf-disable-button"].disabled = active !== true;
  nodes["#new-case-button"].disabled = false;
  nodes["#emf-telemetry-state"].textContent = "authoritative before mutation";
  nodes["#emf-telemetry-state"].className = "inline-state ok";
}

vm.runInThisContext(fs.readFileSync(__API_JS__, "utf8"));
vm.runInThisContext(fs.readFileSync(__APP_JS__, "utf8"));

(async function runGate5Harness() {
__BODY__
console.log(__SUCCESS_MARKER__);
})().catch(error => { console.error(error); process.exitCode = 1; });
"""
    marker = f"__MORPHIC_GATE5_NODE_SUCCESS_{secrets.token_hex(16)}__"
    script = (
        harness.replace("__API_JS__", json.dumps(str(API_JS)))
        .replace("__APP_JS__", json.dumps(str(APP_JS)))
        .replace("__BODY__", body.strip())
        .replace("__SUCCESS_MARKER__", json.dumps(marker))
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
    assert re.search(
        r"^__MORPHIC_GATE5_NODE_SUCCESS_[0-9a-f]{32}__$",
        result.stdout,
        re.MULTILINE,
    )


def _run_render_script(body: str) -> subprocess.CompletedProcess[str]:
    harness = r"""
const fs = require("fs");
const vm = require("vm");

function node(overrides = {}) {
  const attributes = new Map();
  return {
    textContent: "",
    className: "",
    hidden: false,
    style: {},
    dataset: {},
    children: [],
    appendChild(child) { this.children.push(child); return child; },
    replaceChildren(...children) { this.children = children; },
    setAttribute(name, value) { attributes.set(name, String(value)); },
    getAttribute(name) { return attributes.get(name) || null; },
    ...overrides,
  };
}

const nodes = {
  "#hardware-truth-grid": node(),
  "#realtime-calibration": node(),
  "#hardware-gate-warnings": node(),
  "#review-hardware": node(),
};
global.window = {MorphicWorkbenchState: {}};
global.document = {
  querySelector(selector) { return nodes[selector] || null; },
  createElement() { return node(); },
  createTextNode(value) { return node({textContent: String(value)}); },
};

function walk(root) {
  return [root, ...(root.children || []).flatMap(walk)];
}
function hasClass(item, className) {
  return String(item.className || "").split(/\s+/).includes(className);
}
function byClass(root, className) {
  return walk(root).filter(item => hasClass(item, className));
}
function nodeText(item) {
  return String(item.textContent || "") + (item.children || []).map(nodeText).join("");
}

vm.runInThisContext(fs.readFileSync(__RENDER_JS__, "utf8"));

(function runGate5RenderHarness() {
__BODY__
console.log(__SUCCESS_MARKER__);
})()
"""
    marker = f"__MORPHIC_GATE5_NODE_SUCCESS_{secrets.token_hex(16)}__"
    script = (
        harness.replace("__RENDER_JS__", json.dumps(str(RENDER_JS)))
        .replace("__BODY__", body.strip())
        .replace("__SUCCESS_MARKER__", json.dumps(marker))
    )
    return subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=NODE_HARNESS_TIMEOUT_SECONDS,
    )


def _run_monitor_script(body: str) -> subprocess.CompletedProcess[str]:
    harness = r"""
const fs = require("fs");
const vm = require("vm");

function node(overrides = {}) {
  const attributes = new Map();
  let reflectedValue = 0;
  const target = {
    textContent: "",
    className: "",
    hidden: false,
    setAttribute(name, value) { attributes.set(name, String(value)); },
    getAttribute(name) { return attributes.has(name) ? attributes.get(name) : null; },
    hasAttribute(name) { return attributes.has(name); },
    removeAttribute(name) {
      attributes.delete(name);
      if (name === "value") reflectedValue = 0;
    },
  };
  Object.defineProperty(target, "value", {
    get() { return reflectedValue; },
    set(value) {
      reflectedValue = Number(value);
      attributes.set("value", String(value));
    },
  });
  Object.assign(target, overrides);
  return target;
}

const nodes = Object.fromEntries([
  "connectionState", "emf", "emfBar", "ent", "jit", "load", "sensor",
  "entStatus", "jitStatus", "loadStatus", "sensorStatus", "rec", "freq",
].map(id => [id, node()]));
for (const id of ["entStatus", "jitStatus", "loadStatus", "sensorStatus"]) {
  nodes[id].textContent = "unknown";
  nodes[id].className = "monitor-source-status status-unknown";
}

global.window = global;
global.document = {getElementById(id) { return nodes[id] || null; }};
global.location = {protocol: "http:", host: "monitor.test"};
global.setTimeout = () => 0;
global.WebSocket = class SyntheticWebSocket {
  constructor(url) {
    this.url = url;
    global.__monitorSocket = this;
  }
  close() {}
};

const nativeJsonParse = JSON.parse;
let controlledPayload;
JSON.parse = value => value === "__CONTROLLED_PAYLOAD__"
  ? controlledPayload
  : nativeJsonParse(value);

vm.runInThisContext(fs.readFileSync(__MONITOR_JS__, "utf8"));
function emit(payload) {
  controlledPayload = payload;
  global.__monitorSocket.onmessage({data: "__CONTROLLED_PAYLOAD__"});
}

(function runGate5MonitorHarness() {
__BODY__
JSON.parse = nativeJsonParse;
console.log(__SUCCESS_MARKER__);
})()
"""
    marker = f"__MORPHIC_GATE5_NODE_SUCCESS_{secrets.token_hex(16)}__"
    script = (
        harness.replace("__MONITOR_JS__", json.dumps(str(MONITOR_JS)))
        .replace("__BODY__", body.strip())
        .replace("__SUCCESS_MARKER__", json.dumps(marker))
    )
    return subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=NODE_HARNESS_TIMEOUT_SECONDS,
    )


def test_emf_monitor_markup_exposes_four_literal_source_truth_rows() -> None:
    emf_source = EMF_PY.read_text(encoding="utf-8")
    monitor_html = emf_source.split('return HTMLResponse("""', 1)[1].split(
        '""")', 1
    )[0]

    mappings = (
        ("ent", "Entropie", "rng", "entStatus"),
        ("jit", "Jitter (ms)", "cpu_timing", "jitStatus"),
        ("load", "Systemlast", "system_load", "loadStatus"),
        ("sensor", "Sensorentropie", "sensor_entropy", "sensorStatus"),
    )
    assert monitor_html.count('class="card monitor-source-card"') == 4
    for value_id, label, source_key, status_id in mappings:
        card = monitor_html.split(f'id="{value_id}"', 1)[1].split(
            "</section>", 1
        )[0]
        assert f'<div class="label">{label}</div>' in card
        assert f'<code class="monitor-source-key">{source_key}</code>' in card
        assert f'id="{status_id}"' in card
        assert 'class="monitor-source-status status-unknown"' in card
        assert ">unknown</span>" in card
    progress = monitor_html.split('id="emfBar"', 1)[1].split(">", 1)[0]
    assert " hidden" in progress


def test_emf_monitor_update_renders_values_keys_and_normalized_health() -> None:
    body = r"""
emit({
  emf_index: 0.42,
  entropy_score: 0.73,
  timing_jitter_ms: 0.18,
  system_load: 0.61,
  sensor_entropy: 0.5,
  source_health: {
    rng: "ok",
    cpu_timing: "partial",
    system_load: "ok",
    sensor_entropy: "fallback",
  },
});
const actual = {
  aggregate: nodes.emf.textContent,
  progressHidden: nodes.emfBar.hidden,
  progressValue: nodes.emfBar.value,
  values: [nodes.ent.textContent, nodes.jit.textContent, nodes.load.textContent, nodes.sensor.textContent],
  statuses: [nodes.entStatus, nodes.jitStatus, nodes.loadStatus, nodes.sensorStatus].map(node => ({
    text: node.textContent,
    className: node.className,
  })),
};
const expected = {
  aggregate: "0.420",
  progressHidden: false,
  progressValue: 0.42,
  values: ["0.730", "0.18", "0.610", "0.500"],
  statuses: [
    {text: "ok", className: "monitor-source-status status-ok"},
    {text: "partial", className: "monitor-source-status status-partial"},
    {text: "ok", className: "monitor-source-status status-ok"},
    {text: "fallback", className: "monitor-source-status status-fallback"},
  ],
};
if (JSON.stringify(actual) !== JSON.stringify(expected)) {
  throw new Error(`monitor source truth mismatch: ${JSON.stringify(actual)}`);
}
"""

    _assert_node_success(_run_monitor_script(body))


def test_emf_monitor_valid_frame_clears_prior_malformed_response_error() -> None:
    body = r"""
global.__monitorSocket.onmessage({data: "{"});
if (nodes.connectionState.textContent !== "Ungültige Messantwort verworfen") {
  throw new Error(`malformed frame state mismatch: ${nodes.connectionState.textContent}`);
}
emit({
  emf_index: 0.42,
  entropy_score: 0.73,
  timing_jitter_ms: 0.18,
  system_load: 0.61,
  sensor_entropy: 0.5,
  source_health: {rng: "ok", cpu_timing: "partial", system_load: "ok", sensor_entropy: "fallback"},
});
if (nodes.connectionState.textContent !== "Verbunden" || nodes.emf.textContent !== "0.420") {
  throw new Error(`valid frame did not recover monitor state: ${nodes.connectionState.textContent}`);
}
"""

    _assert_node_success(_run_monitor_script(body))


@pytest.mark.parametrize(
    "invalid_expression",
    ("null", '""', '"ungueltig"', "NaN", "Infinity", "-Infinity"),
)
def test_emf_monitor_invalid_aggregate_hides_gauge_and_valid_update_restores_it(
    invalid_expression: str,
) -> None:
    body = r"""
const valid = {
  emf_index: 0.42,
  entropy_score: 0.73,
  timing_jitter_ms: 0.18,
  system_load: 0.61,
  sensor_entropy: 0.5,
  source_health: {rng: "ok", cpu_timing: "partial", system_load: "ok", sensor_entropy: "fallback"},
};
emit(valid);
emit({...valid, emf_index: __INVALID_VALUE__});
if (
  nodes.emf.textContent !== "--"
  || nodes.emfBar.hidden !== true
  || nodes.emfBar.hasAttribute("value")
) throw new Error(`invalid aggregate retained gauge: ${nodes.emf.textContent}/${nodes.emfBar.hidden}`);
emit(valid);
if (
  nodes.emf.textContent !== "0.420"
  || nodes.emfBar.hidden !== false
  || nodes.emfBar.value !== 0.42
) throw new Error("valid aggregate did not restore gauge and value");
""".replace("__INVALID_VALUE__", invalid_expression)

    _assert_node_success(_run_monitor_script(body))


def test_emf_monitor_invalid_component_keeps_source_status_and_unknown_defaults() -> None:
    body = r"""
emit({
  emf_index: 0.42,
  entropy_score: null,
  timing_jitter_ms: 0.18,
  system_load: 0.61,
  sensor_entropy: 0.5,
  source_health: {rng: "partial", cpu_timing: "healthy", sensor_entropy: null},
});
const statuses = [nodes.entStatus, nodes.jitStatus, nodes.loadStatus, nodes.sensorStatus].map(node => ({
  text: node.textContent,
  className: node.className,
}));
if (nodes.ent.textContent !== "--") throw new Error("invalid component did not render placeholder");
if (JSON.stringify(statuses) !== JSON.stringify([
  {text: "partial", className: "monitor-source-status status-partial"},
  {text: "unknown", className: "monitor-source-status status-unknown"},
  {text: "unknown", className: "monitor-source-status status-unknown"},
  {text: "unknown", className: "monitor-source-status status-unknown"},
])) throw new Error(`unsafe monitor status normalization: ${JSON.stringify(statuses)}`);
"""

    _assert_node_success(_run_monitor_script(body))


def test_emf_monitor_source_metadata_css_is_responsive_and_contrast_safe() -> None:
    css = MONITOR_CSS.read_text(encoding="utf-8")

    assert re.search(r"\.monitor-source-card\s*\{[^}]*min-width:\s*0", css, re.S)
    assert re.search(r"\.monitor-source-meta\s*\{[^}]*flex-wrap:\s*wrap", css, re.S)
    key = _isolated_css_declarations(css, ".monitor-source-key")
    assert key.get("color") == "#c9d1d9"
    assert key.get("background") == "#0d1117"
    assert _hex_contrast_ratio("#c9d1d9", "#0d1117") >= 4.5
    for status, background in {
        "ok": "#1f6f43",
        "partial": "#87451f",
        "fallback": "#7a4f00",
        "unknown": "#484f58",
    }.items():
        declarations = _isolated_css_declarations(
            css,
            f".monitor-source-status.status-{status}",
        )
        assert declarations.get("color") == "#fff"
        assert declarations.get("background") == background
        assert _hex_contrast_ratio("#fff", background) >= 4.5
    mobile = css.split("@media (max-width: 560px)", 1)[1]
    assert ".monitor-source-meta" in mobile
    assert "max-width: 100%" in mobile


def test_emf_proxy_renderer_shows_derived_aggregate_and_four_source_rows() -> None:
    body = r"""
const calibration = {
  emf_index: 0.42,
  entropy_score: 0.73,
  timing_jitter_ms: 0.18,
  system_load: 0.61,
  sensor_entropy: 0.5,
  source_health: {
    rng: "ok",
    cpu_timing: "partial",
    system_load: "ok",
    sensor_entropy: "fallback",
  },
  replay: {sensor_source: "fallback"},
};
window.MorphicWorkbenchRender.renderHardwareTruth({
  components: {},
  realtime_calibration: calibration,
  gate_warnings: [],
});

const root = nodes["#realtime-calibration"];
const labels = byClass(root, "emf-index-label");
const derived = byClass(root, "emf-index-derived");
const gauges = byClass(root, "emf-index-gauge");
const aggregateValues = byClass(root, "emf-index-value");
if (labels.length !== 1 || nodeText(labels[0]) !== __EMF_LABEL__) {
  throw new Error(`aggregate label mismatch: ${labels.map(nodeText)}`);
}
if (derived.length !== 1 || nodeText(derived[0]) !== __DERIVED_COPY__) {
  throw new Error(`derived copy mismatch: ${derived.map(nodeText)}`);
}
if (
  gauges.length !== 1
  || gauges[0].getAttribute("aria-label") !== __EMF_LABEL__
  || gauges[0].getAttribute("aria-valuenow") !== "0.42"
) throw new Error("aggregate gauge contract mismatch");
if (aggregateValues.length !== 1 || nodeText(aggregateValues[0]) !== "0,42") {
  throw new Error(`aggregate value mismatch: ${aggregateValues.map(nodeText)}`);
}

const rows = byClass(root, "emf-source-row").map(row => {
  const status = byClass(row, "emf-source-status")[0];
  return {
    label: nodeText(byClass(row, "emf-source-label")[0]),
    value: nodeText(byClass(row, "emf-source-value")[0]),
    source: nodeText(byClass(row, "emf-source-key")[0]),
    status: nodeText(status),
    statusClass: status.className,
  };
});
const expected = [
  {label: "Entropie", value: "0,73", source: "rng", status: "ok", statusClass: "emf-source-status status-ok"},
  {label: "Jitter (ms)", value: "0,18", source: "cpu_timing", status: "partial", statusClass: "emf-source-status status-partial"},
  {label: "Systemlast", value: "0,61", source: "system_load", status: "ok", statusClass: "emf-source-status status-ok"},
  {label: "Sensorentropie", value: "0,5", source: "sensor_entropy", status: "fallback", statusClass: "emf-source-status status-fallback"},
];
if (JSON.stringify(rows) !== JSON.stringify(expected)) {
  throw new Error(`source row mismatch: ${JSON.stringify(rows)}`);
}
"""
    body = body.replace("__EMF_LABEL__", json.dumps(EMF_PROXY_LABEL)).replace(
        "__DERIVED_COPY__", json.dumps(EMF_PROXY_DERIVED_COPY)
    )

    _assert_node_success(_run_render_script(body))


def test_hardware_renderer_preserves_dict_quartz_not_implemented_status() -> None:
    body = r"""
window.MorphicWorkbenchRender.renderHardwareTruth({
  components: {
    quartz: {
      id: "quartz",
      label: "Quartz",
      status: "not_implemented",
      note: "Noch nicht implementiert.",
    },
    future_component: {
      id: "future_component",
      label: "Future component",
      status: "future_backend_state",
      note: "Unrecognized test state.",
    },
  },
  gate_warnings: [],
});

const grid = nodes["#hardware-truth-grid"];
const cards = byClass(grid, "hardware-card");
const quartzCard = cards.find(card => nodeText(card).includes("Quartz"));
const quartzBadge = byClass(quartzCard, "hardware-status-badge")[0];
if (
  !quartzCard
  || quartzCard.dataset.status !== "not_implemented"
  || nodeText(quartzBadge) !== "not_implemented"
  || !hasClass(quartzBadge, "status-not_implemented")
  || nodeText(quartzCard).includes("unknown")
) throw new Error(`Quartz status lost: ${nodeText(quartzCard)}`);

const futureCard = cards.find(card => nodeText(card).includes("Future component"));
const futureBadge = byClass(futureCard, "hardware-status-badge")[0];
if (
  futureCard.dataset.status !== "unknown"
  || nodeText(futureBadge) !== "unknown"
  || !hasClass(futureBadge, "status-unknown")
) throw new Error("unrecognized hardware status did not fall back to unknown");
"""

    _assert_node_success(_run_render_script(body))


def test_hardware_and_review_share_known_and_unknown_status_normalization() -> None:
    body = r"""
const payload = {
  components: {
    available: {
      id: "available",
      label: "Available component",
      status: "real_available_not_used",
      note: "Known inactive hardware.",
    },
    future: {
      id: "future",
      label: "Future component",
      status: "future_backend_state",
      note: "Unsupported payload status.",
    },
  },
  gate_warnings: [],
};
window.MorphicWorkbenchRender.renderHardwareTruth(payload);
window.MorphicWorkbenchRender.renderReviewCards({}, payload);

const hardwareStatuses = byClass(
  nodes["#hardware-truth-grid"],
  "hardware-status-badge",
).map(nodeText);
if (JSON.stringify(hardwareStatuses) !== JSON.stringify(["real_available_not_used", "unknown"])) {
  throw new Error(`hardware normalization mismatch: ${JSON.stringify(hardwareStatuses)}`);
}
const reviewText = nodeText(nodes["#review-hardware"]);
if (
  !reviewText.includes("Available component: real_available_not_used")
  || !reviewText.includes("Future component: unknown")
  || reviewText.includes("future_backend_state")
) throw new Error(`review normalization mismatch: ${reviewText}`);
"""

    _assert_node_success(_run_render_script(body))


@pytest.mark.parametrize(
    ("case_name", "invalid_expression", "delete_value"),
    [
        ("null", "null", False),
        ("undefined", "undefined", False),
        ("missing", "undefined", True),
        ("empty", '""', False),
        ("nonnumeric", '"ungueltig"', False),
        ("nan", "NaN", False),
        ("positive-infinity", "Infinity", False),
        ("negative-infinity", "-Infinity", False),
    ],
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_invalid_emf_aggregate_and_component_keep_source_truth_without_gauge(
    case_name: str,
    invalid_expression: str,
    delete_value: bool,
) -> None:
    del case_name
    body = r"""
const calibration = {
  status: "active",
  emf_index: __INVALID_VALUE__,
  entropy_score: __INVALID_VALUE__,
  timing_jitter_ms: 0.18,
  system_load: 0.61,
  sensor_entropy: 0.5,
  source_health: {
    rng: "partial",
    cpu_timing: "ok",
    system_load: "ok",
    sensor_entropy: "fallback",
  },
  replay: {sensor_source: "fallback"},
};
if (__DELETE_VALUE__) {
  delete calibration.emf_index;
  delete calibration.entropy_score;
}
window.MorphicWorkbenchRender.renderHardwareTruth({
  components: {},
  realtime_calibration: calibration,
  gate_warnings: [],
});

const root = nodes["#realtime-calibration"];
if (byClass(root, "emf-index-gauge").length !== 0) {
  throw new Error("invalid aggregate rendered a gauge");
}
const aggregate = byClass(root, "emf-index-value");
if (aggregate.length !== 1 || nodeText(aggregate[0]) !== "--") {
  throw new Error(`invalid aggregate rendered as ${aggregate.map(nodeText)}`);
}
const rows = byClass(root, "emf-source-row");
if (rows.length !== 4) throw new Error(`missing source rows: ${rows.length}`);
const entropyRow = rows.find(row => nodeText(byClass(row, "emf-source-label")[0]) === "Entropie");
const entropyStatus = byClass(entropyRow, "emf-source-status")[0];
if (
  nodeText(byClass(entropyRow, "emf-source-value")[0]) !== "--"
  || nodeText(byClass(entropyRow, "emf-source-key")[0]) !== "rng"
  || nodeText(entropyStatus) !== "partial"
  || !hasClass(entropyStatus, "status-partial")
) throw new Error("invalid component lost its source or status");
const sensorRow = rows.find(row => nodeText(byClass(row, "emf-source-label")[0]) === "Sensorentropie");
if (
  nodeText(byClass(sensorRow, "emf-source-value")[0]) !== "0,5"
  || nodeText(byClass(sensorRow, "emf-source-status")[0]) !== "fallback"
) throw new Error("numeric fallback value was hidden");
"""
    body = body.replace("__INVALID_VALUE__", invalid_expression).replace(
        "__DELETE_VALUE__", json.dumps(delete_value)
    )

    _assert_node_success(_run_render_script(body))


def test_unrecognized_or_missing_emf_source_health_normalizes_to_unknown() -> None:
    body = r"""
window.MorphicWorkbenchRender.renderHardwareTruth({
  components: {},
  realtime_calibration: {
    status: "active",
    emf_index: 0.42,
    entropy_score: 0.73,
    timing_jitter_ms: 0.18,
    system_load: 0.61,
    sensor_entropy: 0.5,
    source_health: {rng: "healthy", system_load: "", sensor_entropy: null},
  },
  gate_warnings: [],
});
const root = nodes["#realtime-calibration"];
const statuses = byClass(root, "emf-source-status").map(status => ({
  text: nodeText(status),
  className: status.className,
}));
if (
  statuses.length !== 4
  || statuses.some(status => status.text !== "unknown")
  || statuses.some(status => status.className !== "emf-source-status status-unknown")
) throw new Error(`unsafe source health default: ${JSON.stringify(statuses)}`);
"""

    _assert_node_success(_run_render_script(body))


def test_gate5_product_copy_is_exact_and_avoids_physical_or_medical_claims() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    app_source = APP_JS.read_text(encoding="utf-8")
    render_source = RENDER_JS.read_text(encoding="utf-8")
    emf_source = EMF_PY.read_text(encoding="utf-8")

    hardware_phase = html.split('id="hardware-phase"', 1)[1].split(
        "<!-- Phase 6:", 1
    )[0]
    emf_help = hardware_phase.split('id="emf-help"', 1)[1].split("</p>", 1)[0]
    app_emf_controls = app_source.split(
        "function updateEmfTelemetryControls(", 1
    )[1].split("async function generatePreview(", 1)[0]
    render_emf = render_source.split("renderHardwareTruth(payload)", 1)[1].split(
        "/* ── Review Cards", 1
    )[0]
    monitor_html = emf_source.split('return HTMLResponse("""', 1)[1].split(
        '""")', 1
    )[0]

    assert EMF_PROXY_LABEL in emf_help
    assert EMF_PROXY_DERIVED_COPY in emf_help
    assert "<strong>Datenschutz-/Hardwaregrenze:</strong>" in emf_help
    assert EMF_PROXY_DERIVED_COPY in render_source
    assert app_emf_controls.count(
        '"EMF-Telemetrie aktiv bis manuell deaktiviert."'
    ) == 2
    assert f"<h1>{EMF_PROXY_LABEL}</h1>" in monitor_html
    assert f'<div class="label">{EMF_PROXY_LABEL}</div>' in monitor_html
    assert f'aria-label="{EMF_PROXY_LABEL}"' in monitor_html
    assert EMF_PROXY_DERIVED_COPY in monitor_html

    gate5_copy = "\n".join((emf_help, app_emf_controls, render_emf, monitor_html)).lower()
    for forbidden_claim in (
        "exposition",
        "belastung",
        "diagnose",
        "behandlung",
        "therapie",
        "wirksamkeit",
        "heilversprechen",
    ):
        assert forbidden_claim not in gate5_copy


def test_hardware_classification_copy_names_backend_states_and_unknown_fallback() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    hardware_phase = html.split('id="hardware-phase"', 1)[1].split(
        "<!-- Phase 6:", 1
    )[0]
    classification_copy = hardware_phase.split(
        "<strong>Hinweis zur Klassifikation.</strong>", 1
    )[1].split("</span>", 1)[0]

    for status in (
        "real_active",
        "real_available_not_used",
        "software_fallback",
        "not_implemented",
    ):
        assert f"<code>{status}</code>" in classification_copy
    assert (
        "Nicht erkannte Payload-Statuswerte werden als <code>unknown</code> angezeigt."
        in classification_copy
    )


def test_emf_index_label_css_preserves_exact_visible_casing() -> None:
    css = APP_CSS.read_text(encoding="utf-8")
    declarations = _isolated_css_declarations(css, ".emf-index-label")
    assert declarations.get("text-transform", "none") != "uppercase"


def test_emf_source_key_uses_contrast_safe_ink_foreground() -> None:
    css = APP_CSS.read_text(encoding="utf-8")
    declarations = _isolated_css_declarations(css, ".emf-source-key")

    assert declarations.get("color") == "var(--ink, #222a32)"
    assert declarations.get("background") == "var(--surface-muted, #eef2ea)"


def test_partial_source_status_fixed_colors_meet_wcag_normal_text_contrast() -> None:
    css = APP_CSS.read_text(encoding="utf-8")
    declarations = _isolated_css_declarations(
        css,
        ".emf-source-status.status-partial",
    )

    assert declarations.get("color") == "#fff"
    assert declarations.get("background") == "#87451f"
    assert _hex_contrast_ratio("#fff", "#87451f") >= 4.5


def test_gate5_source_rows_have_tokenized_status_and_375px_overflow_contract() -> None:
    css = APP_CSS.read_text(encoding="utf-8")

    assert re.search(r"\.emf-source-row\s*\{[^}]*min-width:\s*0", css, re.S)
    assert re.search(r"\.emf-source-key\s*\{[^}]*monospace", css, re.S)
    for status in ("ok", "fallback", "unknown"):
        assert re.search(
            rf"\.emf-source-status\.status-{status}\s*\{{[^}}]*var\(--",
            css,
            re.S,
        )
    mobile = css.split("@media (max-width: 375px)", 1)[1]
    assert re.search(
        r"\.emf-source-row\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)\s+auto",
        mobile,
        re.S,
    )
    assert "overflow-wrap: anywhere" in mobile


def test_hardware_known_inactive_and_unknown_badges_meet_wcag_contrast() -> None:
    css = APP_CSS.read_text(encoding="utf-8")
    pairs = {
        ".hardware-status-badge.status-real_available_not_used": "#536b92",
        ".hardware-status-badge.status-unknown": "#484f58",
    }

    for selector, background in pairs.items():
        declarations = _isolated_css_declarations(css, selector)
        assert declarations.get("color") == "#fff"
        assert declarations.get("background") == background
        assert _hex_contrast_ratio("#fff", background) >= 4.5


@pytest.mark.parametrize(
    ("enabled", "initial_active", "mutation_label", "confirmed_active"),
    [
        (True, False, "POST enable", True),
        (False, True, "POST disable", False),
    ],
)
def test_successful_mutation_uses_post_confirming_status_then_hardware(
    enabled: bool,
    initial_active: bool,
    mutation_label: str,
    confirmed_active: bool,
) -> None:
    body = r"""
const requested = __ENABLED__;
const confirmed = __CONFIRMED__;
const mutationUrl = requested ? "/api/emf/enable" : "/api/emf/disable";
const mutationLabel = __MUTATION_LABEL__;
const calls = [];
resetEmfDom(__INITIAL_ACTIVE__);
fetchImpl = async (url, options = {}) => {
  const method = String(options.method || "GET").toUpperCase();
  if (url === mutationUrl && method === "POST") {
    calls.push(mutationLabel);
    return response({active: !confirmed});
  }
  if (url === "/api/emf/status" && method === "GET") {
    calls.push("GET status");
    return response({active: confirmed});
  }
  if (String(url).startsWith("/api/workbench/hardware?") && method === "GET") {
    calls.push("GET hardware");
    return response({snapshot: "confirmed-hardware"});
  }
  throw new Error(`unexpected request: ${method} ${url}`);
};

await setEmfTelemetryEnabled(requested, caseGeneration);
const state = window.MorphicWorkbenchState;
const actual = {
  calls,
  active: state.emfTelemetryActive,
  status: state.emfTelemetryStatus,
  enableDisabled: nodes["#emf-enable-button"].disabled,
  disableDisabled: nodes["#emf-disable-button"].disabled,
};
const expected = {
  calls: [mutationLabel, "GET status", "GET hardware"],
  active: confirmed,
  status: confirmed ? "ok" : "neutral",
  enableDisabled: confirmed,
  disableDisabled: !confirmed,
};
if (JSON.stringify(actual) !== JSON.stringify(expected)) {
  throw new Error(`confirmed mutation mismatch: ${JSON.stringify(actual)}`);
}
"""
    body = (
        body.replace("__ENABLED__", json.dumps(enabled))
        .replace("__CONFIRMED__", json.dumps(confirmed_active))
        .replace("__MUTATION_LABEL__", json.dumps(mutation_label))
        .replace("__INITIAL_ACTIVE__", json.dumps(initial_active))
    )

    _assert_node_success(_run_app_script(body))


@pytest.mark.parametrize(
    ("enabled", "initial_active", "pending_copy"),
    [
        (True, False, "EMF-Telemetrie wird aktiviert..."),
        (False, True, "EMF-Telemetrie wird deaktiviert..."),
    ],
)
def test_pending_mutation_locks_buttons_without_changing_authority(
    enabled: bool,
    initial_active: bool,
    pending_copy: str,
) -> None:
    body = r"""
const requested = __ENABLED__;
const mutationUrl = requested ? "/api/emf/enable" : "/api/emf/disable";
const mutation = deferred();
resetEmfDom(__INITIAL_ACTIVE__);
fetchImpl = async (url, options = {}) => {
  const method = String(options.method || "GET").toUpperCase();
  if (url === mutationUrl && method === "POST") return mutation.promise;
  if (url === "/api/emf/status") return response({active: requested});
  if (String(url).startsWith("/api/workbench/hardware?")) return response({});
  throw new Error(`unexpected request: ${method} ${url}`);
};

const operation = setEmfTelemetryEnabled(requested, caseGeneration);
await Promise.resolve();
if (window.MorphicWorkbenchState.emfTelemetryActive !== __INITIAL_ACTIVE__) {
  throw new Error("pending copy changed authoritative activation state");
}
if (!nodes["#emf-enable-button"].disabled || !nodes["#emf-disable-button"].disabled) {
  throw new Error("pending mutation did not lock both controls");
}
if (nodes["#emf-telemetry-state"].textContent !== __PENDING_COPY__) {
  throw new Error(`wrong pending copy: ${nodes["#emf-telemetry-state"].textContent}`);
}
mutation.resolve(response({active: !requested}));
await operation;
"""
    body = (
        body.replace("__ENABLED__", json.dumps(enabled))
        .replace("__INITIAL_ACTIVE__", json.dumps(initial_active))
        .replace("__PENDING_COPY__", json.dumps(pending_copy))
    )

    _assert_node_success(_run_app_script(body))


def test_status_started_before_mutation_cannot_overwrite_pending_state() -> None:
    body = r"""
const initialStatus = deferred();
const mutation = deferred();
let statusCalls = 0;
resetEmfDom(false);
window.MorphicWorkbenchApi.loadEmfStatus = async () => {
  statusCalls += 1;
  if (statusCalls === 1) return initialStatus.promise;
  return {active: true};
};
window.MorphicWorkbenchApi.enableEmfTelemetry = () => mutation.promise;
window.MorphicWorkbenchApi.loadHardware = async () => ({snapshot: "confirmed"});

const bootstrapStatus = loadEmfTelemetryStatus(caseGeneration);
await Promise.resolve();
const operation = setEmfTelemetryEnabled(true, caseGeneration);
await Promise.resolve();
initialStatus.resolve({active: false});
const staleConfirmation = await bootstrapStatus;
if (staleConfirmation !== false) {
  throw new Error("status started before the mutation retained authority");
}
if (
  window.MorphicWorkbenchState.emfTelemetryActive !== false
  || !nodes["#emf-enable-button"].disabled
  || !nodes["#emf-disable-button"].disabled
  || nodes["#emf-telemetry-state"].textContent !== "EMF-Telemetrie wird aktiviert..."
) throw new Error("late bootstrap status overwrote pending mutation state");

mutation.resolve({active: false});
await operation;
if (window.MorphicWorkbenchState.emfTelemetryActive !== true || statusCalls !== 2) {
  throw new Error("mutation did not obtain its own confirming status");
}
"""

    _assert_node_success(_run_app_script(body))


def test_new_case_is_blocked_until_confirmed_emf_operation_finishes() -> None:
    body = r"""
const status = deferred();
const hardware = deferred();
let statusRequested = false;
let hardwareRequested = false;
fetchImpl = async (url, options = {}) => {
  const method = String(options.method || "GET").toUpperCase();
  if (url === "/api/emf/enable" && method === "POST") return response({active: false});
  if (url === "/api/emf/status" && method === "GET") {
    statusRequested = true;
    return status.promise;
  }
  if (String(url).startsWith("/api/workbench/hardware?") && method === "GET") {
    hardwareRequested = true;
    return hardware.promise;
  }
  if (String(url).startsWith("/api/workbench/scan-profile-catalog?") && method === "GET") {
    return response({
      profile_level: 3,
      pool_authority: {fingerprint: "a".repeat(64)},
      internal: {count: 9, profiles: []},
      external: {count: 0, active_source_count: 0},
    });
  }
  throw new Error(`unexpected request: ${method} ${url}`);
};

const generation = caseGeneration;
const operation = setEmfTelemetryEnabled(true, generation);
await waitUntil(() => statusRequested);
if (window.MorphicWorkbenchState.pendingMutations !== 0) {
  throw new Error("POST mutation counter did not settle before confirmation");
}
const blockedReset = await resetWorkbenchForNewCase();
const blockedSnapshot = {
  blockedReset,
  generation: caseGeneration,
  pending: window.MorphicWorkbenchState.emfTelemetryMutationPending,
  enableDisabled: nodes["#emf-enable-button"].disabled,
  disableDisabled: nodes["#emf-disable-button"].disabled,
  copy: nodes["#emf-telemetry-state"].textContent,
};

status.resolve(response({active: true}));
await waitUntil(() => hardwareRequested || caseGeneration !== generation);
if (hardwareRequested) hardware.resolve(response({snapshot: "confirmed"}));
const operationResult = await operation;
const confirmedSnapshot = {
  operationResult,
  pending: window.MorphicWorkbenchState.emfTelemetryMutationPending,
  active: window.MorphicWorkbenchState.emfTelemetryActive,
  enableDisabled: nodes["#emf-enable-button"].disabled,
  disableDisabled: nodes["#emf-disable-button"].disabled,
};
const completedReset = await resetWorkbenchForNewCase();

if (
  blockedSnapshot.blockedReset !== false
  || blockedSnapshot.generation !== generation
  || blockedSnapshot.pending !== true
  || !blockedSnapshot.enableDisabled
  || !blockedSnapshot.disableDisabled
  || blockedSnapshot.copy !== "EMF-Telemetrie wird aktiviert..."
) throw new Error(`New Case escaped EMF fence: ${JSON.stringify(blockedSnapshot)}`);
if (
  confirmedSnapshot.operationResult !== true
  || confirmedSnapshot.pending !== false
  || confirmedSnapshot.active !== true
  || !confirmedSnapshot.enableDisabled
  || confirmedSnapshot.disableDisabled
) throw new Error(`EMF fence did not release to confirmed authority: ${JSON.stringify(confirmedSnapshot)}`);
if (completedReset !== true) throw new Error("New Case remained blocked after EMF completion");
"""

    _assert_node_success(_run_app_script(body))


def test_new_case_button_stays_disabled_through_post_status_and_hardware() -> None:
    body = r"""
const mutation = deferred();
const status = deferred();
const hardware = deferred();
const calls = [];
fetchImpl = async (url, options = {}) => {
  const method = String(options.method || "GET").toUpperCase();
  if (url === "/api/emf/enable" && method === "POST") {
    calls.push("POST");
    return mutation.promise;
  }
  if (url === "/api/emf/status" && method === "GET") {
    calls.push("STATUS");
    return status.promise;
  }
  if (String(url).startsWith("/api/workbench/hardware?") && method === "GET") {
    calls.push("HARDWARE");
    return hardware.promise;
  }
  throw new Error(`unexpected request: ${method} ${url}`);
};

const operation = setEmfTelemetryEnabled(true, caseGeneration);
await waitUntil(() => calls.includes("POST"));
const disabledDuringPost = nodes["#new-case-button"].disabled;
mutation.resolve(response({active: false}));
await waitUntil(() => calls.includes("STATUS"));
const disabledDuringStatus = nodes["#new-case-button"].disabled;
status.resolve(response({active: true}));
await waitUntil(() => calls.includes("HARDWARE"));
const disabledDuringHardware = nodes["#new-case-button"].disabled;
const emfControlsLockedDuringHardware = nodes["#emf-enable-button"].disabled
  && nodes["#emf-disable-button"].disabled;
hardware.resolve(response({snapshot: "confirmed"}));
await operation;
if (!disabledDuringPost) throw new Error("New Case was enabled during EMF POST");
if (!disabledDuringStatus) {
  throw new Error("New Case was enabled during confirming status GET");
}
if (!disabledDuringHardware) {
  throw new Error("New Case was enabled during confirmed hardware GET");
}
if (!emfControlsLockedDuringHardware) {
  throw new Error("EMF controls allowed an overlapping mutation during hardware GET");
}
if (
  window.MorphicWorkbenchState.emfTelemetryMutationPending
  || nodes["#new-case-button"].disabled
) throw new Error("New Case fence did not release after the full EMF operation");
"""

    _assert_node_success(_run_app_script(body))


def test_emf_mutation_is_rejected_without_side_effects_during_new_case_reset() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const stop = deferred();
const statusResponse = deferred();
const emfApiCalls = [];
let stopCalls = 0;
const originalEnable = window.MorphicWorkbenchApi.enableEmfTelemetry;
const originalLoadStatus = window.MorphicWorkbenchApi.loadEmfStatus;
const originalLoadHardware = window.MorphicWorkbenchApi.loadHardware;
window.MorphicWorkbenchApi.enableEmfTelemetry = async (...args) => {
  emfApiCalls.push("POST enable");
  return originalEnable(...args);
};
window.MorphicWorkbenchApi.loadEmfStatus = async (...args) => {
  emfApiCalls.push("GET status");
  return originalLoadStatus(...args);
};
window.MorphicWorkbenchApi.loadHardware = async (...args) => {
  emfApiCalls.push("GET hardware");
  return originalLoadHardware(...args);
};
window.MorphicWorkbenchApi.stopScanJob = async () => {
  stopCalls += 1;
  return stop.promise;
};
fetchImpl = async (url, options = {}) => {
  const method = String(options.method || "GET").toUpperCase();
  if (url === "/api/emf/status" && method === "GET") return statusResponse.promise;
  if (String(url).startsWith("/api/workbench/hardware?") && method === "GET") {
    return response({snapshot: "must-not-load"});
  }
  if (String(url).startsWith("/api/workbench/scan-profile-catalog?") && method === "GET") {
    return response({
      profile_level: 3,
      pool_authority: {fingerprint: "b".repeat(64)},
      internal: {count: 9, profiles: []},
      external: {count: 0, active_source_count: 0},
    });
  }
  throw new Error(`unexpected request: ${method} ${url}`);
};

updateEmfTelemetryControls(false, "Existing confirmed EMF authority", "neutral");
const emfDomSnapshot = () => ({
  active: state.emfTelemetryActive,
  status: state.emfTelemetryStatus,
  copy: nodes["#emf-telemetry-state"].textContent,
  className: nodes["#emf-telemetry-state"].className,
  enableDisabled: nodes["#emf-enable-button"].disabled,
  disableDisabled: nodes["#emf-disable-button"].disabled,
});
const before = emfDomSnapshot();
const statusTokenBefore = emfTelemetryStatusRequestToken;
state.activeJobId = "scan-reset-reverse-order";
state.scanRunActive = true;
const resetGeneration = caseGeneration;
const resetOperation = resetWorkbenchForNewCase();
await waitUntil(() => state.resetInProgress && stopCalls === 1);

let rejectedSettled = false;
let rejectedResult;
const rejectedOperation = setEmfTelemetryEnabled(true, caseGeneration).then(result => {
  rejectedSettled = true;
  rejectedResult = result;
});
for (let turn = 0; turn < 20; turn += 1) await Promise.resolve();
const duringReset = {
  settled: rejectedSettled,
  result: rejectedResult,
  fence: state.emfTelemetryMutationPending,
  token: emfTelemetryStatusRequestToken,
  dom: emfDomSnapshot(),
};

stop.resolve({status: "stopped"});
const resetResult = await resetOperation;
const afterResetBeforeStatus = emfDomSnapshot();
statusResponse.resolve(response({active: true}));
await rejectedOperation;
const final = {
  fence: state.emfTelemetryMutationPending,
  dom: emfDomSnapshot(),
  newCaseDisabled: nodes["#new-case-button"].disabled,
};

if (
  !duringReset.settled || duringReset.result !== false
  || duringReset.fence !== false || duringReset.token !== statusTokenBefore
  || JSON.stringify(duringReset.dom) !== JSON.stringify(before)
) throw new Error(`reset-time EMF call was not side-effect free: ${JSON.stringify(duringReset)}`);
if (emfApiCalls.length !== 0) {
  throw new Error(`reset-time EMF call reached APIs: ${JSON.stringify(emfApiCalls)}`);
}
if (
  resetResult !== true || caseGeneration !== resetGeneration + 1
  || JSON.stringify(afterResetBeforeStatus) !== JSON.stringify(before)
  || final.fence !== false || JSON.stringify(final.dom) !== JSON.stringify(before)
  || final.newCaseDisabled
) throw new Error(`reset left EMF controls stranded: ${JSON.stringify({resetResult, afterResetBeforeStatus, final})}`);
"""

    _assert_node_success(_run_app_script(body))


def test_duplicate_emf_mutation_does_not_steal_existing_fence() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const apiCalls = [];
window.MorphicWorkbenchApi.disableEmfTelemetry = async () => {
  apiCalls.push("POST disable");
  return {active: false};
};
window.MorphicWorkbenchApi.loadEmfStatus = async () => {
  apiCalls.push("GET status");
  return {active: false};
};
window.MorphicWorkbenchApi.loadHardware = async () => {
  apiCalls.push("GET hardware");
  return {snapshot: "duplicate"};
};
updateEmfTelemetryControls(true, "Existing active authority", "ok");
state.emfTelemetryMutationPending = true;
nodes["#new-case-button"].disabled = true;
const before = {
  active: state.emfTelemetryActive,
  status: state.emfTelemetryStatus,
  copy: nodes["#emf-telemetry-state"].textContent,
  className: nodes["#emf-telemetry-state"].className,
  enableDisabled: nodes["#emf-enable-button"].disabled,
  disableDisabled: nodes["#emf-disable-button"].disabled,
  newCaseDisabled: nodes["#new-case-button"].disabled,
  token: emfTelemetryStatusRequestToken,
};

const result = await setEmfTelemetryEnabled(false, caseGeneration);
const after = {
  active: state.emfTelemetryActive,
  status: state.emfTelemetryStatus,
  copy: nodes["#emf-telemetry-state"].textContent,
  className: nodes["#emf-telemetry-state"].className,
  enableDisabled: nodes["#emf-enable-button"].disabled,
  disableDisabled: nodes["#emf-disable-button"].disabled,
  newCaseDisabled: nodes["#new-case-button"].disabled,
  token: emfTelemetryStatusRequestToken,
};
if (result !== false || apiCalls.length !== 0) {
  throw new Error(`duplicate EMF call reached authority: ${result}/${JSON.stringify(apiCalls)}`);
}
if (!state.emfTelemetryMutationPending || JSON.stringify(after) !== JSON.stringify(before)) {
  throw new Error(`duplicate EMF call stole fence or DOM: ${JSON.stringify({before, after, fence: state.emfTelemetryMutationPending})}`);
}
"""

    _assert_node_success(_run_app_script(body))


def test_unknown_emf_state_initializes_without_guessed_activation() -> None:
    source = STATE_JS.read_text(encoding="utf-8")

    assert re.search(
        r'emfTelemetryActive:\s*null,\s*emfTelemetryStatus:\s*"unknown",',
        source,
    )
    assert re.search(r"emfTelemetryMutationPending:\s*false,", source)
    assert re.search(r"emfTelemetryMutationUnresolved:\s*false,", source)


def test_only_emf_mutations_receive_configurable_ambiguous_timeout() -> None:
    body = r"""
const requests = [];
const originalRequestJson = requestJson;
requestJson = async (url, options = {}) => {
  requests.push({url, options: {...options}});
  return {};
};
window.MORPHIC_EMF_MUTATION_TIMEOUT_MS = "2468";
await window.MorphicWorkbenchApi.enableEmfTelemetry();
window.MORPHIC_EMF_MUTATION_TIMEOUT_MS = 0;
await window.MorphicWorkbenchApi.disableEmfTelemetry();
await window.MorphicWorkbenchApi.saveDraft({draft: {}});
requestJson = originalRequestJson;

const captured = requests.map(({url, options}) => ({
  url,
  method: options.method,
  ambiguousTimeoutMs: options.ambiguousTimeoutMs,
}));
const expected = [
  {url: "/api/emf/enable", method: "POST", ambiguousTimeoutMs: 2468},
  {url: "/api/emf/disable", method: "POST", ambiguousTimeoutMs: 10000},
  {url: "/api/workbench/draft", method: "PUT"},
];
if (JSON.stringify(captured) !== JSON.stringify(expected)) {
  throw new Error(`EMF timeout scope mismatch: ${JSON.stringify(captured)}`);
}
"""

    _assert_node_success(_run_app_script(body))


@pytest.mark.parametrize(
    ("enabled", "initial_active", "mutation_label"),
    [
        (True, False, "POST enable"),
        (False, True, "POST disable"),
    ],
)
def test_timeout_polls_until_requested_state_without_settling_opposite_observations(
    enabled: bool,
    initial_active: bool,
    mutation_label: str,
) -> None:
    body = r"""
const requested = __ENABLED__;
const initialActive = __INITIAL_ACTIVE__;
const state = window.MorphicWorkbenchState;
const calls = [];
const observations = [deferred(), deferred(), deferred()];
let statusCalls = 0;
let hardwareCalls = 0;
const nativeSetTimeout = global.setTimeout;
global.setTimeout = callback => {
  Promise.resolve().then(callback);
  return 0;
};
resetEmfDom(initialActive);
const timeoutError = new Error("mutation timed out");
timeoutError.code = "request_timeout";
window.MorphicWorkbenchApi.enableEmfTelemetry = async () => {
  calls.push("POST enable");
  throw timeoutError;
};
window.MorphicWorkbenchApi.disableEmfTelemetry = async () => {
  calls.push("POST disable");
  throw timeoutError;
};
window.MorphicWorkbenchApi.loadEmfStatus = () => {
  calls.push(`GET status ${statusCalls + 1}`);
  return observations[statusCalls++].promise;
};
window.MorphicWorkbenchApi.loadHardware = async () => {
  hardwareCalls += 1;
  calls.push("GET hardware");
  return {snapshot: "timeout-reconciled"};
};

const operation = setEmfTelemetryEnabled(requested, caseGeneration);
await waitUntil(() => statusCalls === 1);
observations[0].resolve({active: initialActive});
await waitUntil(() => statusCalls === 2);
const afterFirstOpposite = {
  active: state.emfTelemetryActive,
  pending: state.emfTelemetryMutationPending,
  unresolved: state.emfTelemetryMutationUnresolved,
  hardwareCalls,
  enableDisabled: nodes["#emf-enable-button"].disabled,
  disableDisabled: nodes["#emf-disable-button"].disabled,
  newCaseDisabled: nodes["#new-case-button"].disabled,
};
observations[1].resolve({active: initialActive});
await waitUntil(() => statusCalls === 3);
const afterSecondOpposite = {
  active: state.emfTelemetryActive,
  pending: state.emfTelemetryMutationPending,
  unresolved: state.emfTelemetryMutationUnresolved,
  hardwareCalls,
  enableDisabled: nodes["#emf-enable-button"].disabled,
  disableDisabled: nodes["#emf-disable-button"].disabled,
  newCaseDisabled: nodes["#new-case-button"].disabled,
};
observations[2].resolve({active: requested});
const result = await operation;
global.setTimeout = nativeSetTimeout;

for (const snapshot of [afterFirstOpposite, afterSecondOpposite]) {
  if (
    snapshot.active !== initialActive
    || snapshot.pending !== true
    || snapshot.unresolved !== true
    || snapshot.hardwareCalls !== 0
    || !snapshot.enableDisabled
    || !snapshot.disableDisabled
    || !snapshot.newCaseDisabled
  ) throw new Error(`opposite timeout observation settled: ${JSON.stringify(snapshot)}`);
}
if (result !== false) throw new Error(`lost POST response returned ${result}`);
if (
  state.emfTelemetryActive !== requested
  || state.emfTelemetryMutationPending
  || state.emfTelemetryMutationUnresolved
  || hardwareCalls !== 1
  || nodes["#emf-enable-button"].disabled !== requested
  || nodes["#emf-disable-button"].disabled === requested
  || nodes["#new-case-button"].disabled
) throw new Error(`requested state did not reconcile: ${JSON.stringify({state, hardwareCalls})}`);
const expectedCalls = [
  __MUTATION_LABEL__,
  "GET status 1",
  "GET status 2",
  "GET status 3",
  "GET hardware",
];
if (JSON.stringify(calls) !== JSON.stringify(expectedCalls)) {
  throw new Error(`timeout reconciliation ordering: ${JSON.stringify(calls)}`);
}
"""
    body = (
        body.replace("__ENABLED__", json.dumps(enabled))
        .replace("__INITIAL_ACTIVE__", json.dumps(initial_active))
        .replace("__MUTATION_LABEL__", json.dumps(mutation_label))
    )

    _assert_node_success(_run_app_script(body))


def test_timeout_exhaustion_is_unknown_and_keeps_controls_and_new_case_fenced() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const observations = [
  {active: false},
  {active: "true"},
  new Error("status unavailable"),
  {active: false},
];
const calls = [];
const nativeSetTimeout = global.setTimeout;
global.setTimeout = callback => {
  Promise.resolve().then(callback);
  return 0;
};
resetEmfDom(false);
const timeoutError = new Error("mutation timed out");
timeoutError.code = "request_timeout";
window.MorphicWorkbenchApi.enableEmfTelemetry = async () => {
  calls.push("POST enable");
  throw timeoutError;
};
window.MorphicWorkbenchApi.loadEmfStatus = async () => {
  calls.push("GET status");
  const observation = observations.shift();
  if (observation instanceof Error) throw observation;
  return observation;
};
window.MorphicWorkbenchApi.loadHardware = async () => {
  calls.push("GET hardware");
  return {snapshot: "must-not-load"};
};

const result = await setEmfTelemetryEnabled(true, caseGeneration);
global.setTimeout = nativeSetTimeout;
const resetResult = await resetWorkbenchForNewCase();
if (result !== false || resetResult !== false) {
  throw new Error(`unresolved mutation returned ${result}/${resetResult}`);
}
if (observations.length !== 0 || calls.filter(call => call === "GET status").length !== 4) {
  throw new Error(`poll bound mismatch: ${JSON.stringify({calls, remaining: observations.length})}`);
}
if (calls.includes("GET hardware")) throw new Error("unresolved timeout loaded hardware");
if (
  state.emfTelemetryActive !== null
  || state.emfTelemetryStatus !== "unknown"
  || state.emfTelemetryMutationPending
  || state.emfTelemetryMutationUnresolved !== true
  || !nodes["#emf-enable-button"].disabled
  || !nodes["#emf-disable-button"].disabled
  || !nodes["#new-case-button"].disabled
  || nodes["#emf-telemetry-state"].className !== "inline-state bad"
  || !/unbekannt|ungeklaert|nicht eindeutig/i.test(nodes["#emf-telemetry-state"].textContent)
) throw new Error(`timeout did not remain unknown and fenced: ${JSON.stringify(state)}`);
"""

    _assert_node_success(_run_app_script(body))


def test_timeout_reconciliation_stops_without_stale_generation_updates() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const firstStatus = deferred();
let statusCalls = 0;
let hardwareCalls = 0;
const nativeSetTimeout = global.setTimeout;
global.setTimeout = callback => {
  Promise.resolve().then(callback);
  return 0;
};
resetEmfDom(false);
const timeoutError = new Error("mutation timed out");
timeoutError.code = "request_timeout";
window.MorphicWorkbenchApi.enableEmfTelemetry = async () => { throw timeoutError; };
window.MorphicWorkbenchApi.loadEmfStatus = () => {
  statusCalls += 1;
  return firstStatus.promise;
};
window.MorphicWorkbenchApi.loadHardware = async () => {
  hardwareCalls += 1;
  return {snapshot: "stale"};
};

const generation = caseGeneration;
const operation = setEmfTelemetryEnabled(true, generation);
await waitUntil(() => statusCalls === 1);
caseGeneration += 1;
resetEmfDom(false, "new-generation");
state.emfTelemetryMutationPending = true;
nodes["#new-case-button"].disabled = true;
nodes["#emf-telemetry-state"].textContent = "new generation";
firstStatus.resolve({active: true});
const result = await operation;
global.setTimeout = nativeSetTimeout;
if (
  result !== false || statusCalls !== 1 || hardwareCalls !== 0
  || state.emfTelemetryActive !== false
  || state.emfTelemetryStatus !== "new-generation"
  || state.emfTelemetryMutationPending !== true
  || state.emfTelemetryMutationUnresolved
  || !nodes["#new-case-button"].disabled
  || nodes["#emf-telemetry-state"].textContent !== "new generation"
) throw new Error(`stale timeout poll updated new generation: ${JSON.stringify({state, statusCalls, hardwareCalls})}`);
"""

    _assert_node_success(_run_app_script(body))


def test_post_success_status_failure_is_unknown_and_skips_hardware() -> None:
    body = r"""
const calls = [];
resetEmfDom(false);
fetchImpl = async (url, options = {}) => {
  const method = String(options.method || "GET").toUpperCase();
  if (url === "/api/emf/enable" && method === "POST") {
    calls.push("POST enable");
    return response({active: true});
  }
  if (url === "/api/emf/status" && method === "GET") {
    calls.push("GET status");
    throw new Error("status unavailable");
  }
  if (String(url).startsWith("/api/workbench/hardware?")) {
    calls.push("GET hardware");
    return response({});
  }
  throw new Error(`unexpected request: ${method} ${url}`);
};

await setEmfTelemetryEnabled(true, caseGeneration);
const state = window.MorphicWorkbenchState;
if (JSON.stringify(calls) !== JSON.stringify(["POST enable", "GET status"])) {
  throw new Error(`status failure ordering: ${JSON.stringify(calls)}`);
}
if (state.emfTelemetryActive !== null || state.emfTelemetryStatus !== "unknown") {
  throw new Error(`POST response became authority: ${JSON.stringify(state)}`);
}
if (!nodes["#emf-enable-button"].disabled || !nodes["#emf-disable-button"].disabled) {
  throw new Error("unknown state did not fail closed");
}
if (
  nodes["#emf-telemetry-state"].className !== "inline-state bad"
  || !nodes["#emf-telemetry-state"].textContent.includes("nicht verfuegbar")
) throw new Error("explicit status error state was not rendered");
"""

    _assert_node_success(_run_app_script(body))


@pytest.mark.parametrize(
    ("enabled", "initial_active", "confirmed_active"),
    [
        (True, True, False),
        (False, False, True),
    ],
)
def test_definite_http_rejection_uses_one_status_read_and_refreshes_hardware(
    enabled: bool,
    initial_active: bool,
    confirmed_active: bool,
) -> None:
    body = r"""
const requested = __ENABLED__;
const confirmed = __CONFIRMED__;
const mutationUrl = requested ? "/api/emf/enable" : "/api/emf/disable";
const mutationLabel = requested ? "POST enable" : "POST disable";
const calls = [];
resetEmfDom(__INITIAL_ACTIVE__);
fetchImpl = async (url, options = {}) => {
  const method = String(options.method || "GET").toUpperCase();
  if (url === mutationUrl && method === "POST") {
    calls.push(mutationLabel);
    return response({detail: "mutation rejected"}, 409);
  }
  if (url === "/api/emf/status" && method === "GET") {
    calls.push("GET status");
    return response({active: confirmed});
  }
  if (String(url).startsWith("/api/workbench/hardware?") && method === "GET") {
    calls.push("GET hardware");
    return response({snapshot: "post-failure-confirmed"});
  }
  throw new Error(`unexpected request: ${method} ${url}`);
};

await setEmfTelemetryEnabled(requested, caseGeneration);
const state = window.MorphicWorkbenchState;
if (JSON.stringify(calls) !== JSON.stringify([mutationLabel, "GET status", "GET hardware"])) {
  throw new Error(`POST failure ordering: ${JSON.stringify(calls)}`);
}
if (state.emfTelemetryActive !== confirmed) {
  throw new Error(`requested or inverse state was inferred: ${state.emfTelemetryActive}`);
}
if (
  nodes["#emf-enable-button"].disabled !== confirmed
  || nodes["#emf-disable-button"].disabled !== !confirmed
) throw new Error("controls do not reflect confirmed post-failure status");
"""
    body = (
        body.replace("__ENABLED__", json.dumps(enabled))
        .replace("__CONFIRMED__", json.dumps(confirmed_active))
        .replace("__INITIAL_ACTIVE__", json.dumps(initial_active))
    )

    _assert_node_success(_run_app_script(body))


def test_only_confirmed_authoritative_status_clears_unresolved_fence() -> None:
    body = r"""
const state = window.MorphicWorkbenchState;
const payloads = [{active: "false"}, {active: false}];
resetEmfDom(null, "unknown");
state.emfTelemetryMutationUnresolved = true;
nodes["#new-case-button"].disabled = true;
window.MorphicWorkbenchApi.loadEmfStatus = async () => payloads.shift();

const invalidResult = await loadEmfTelemetryStatus(caseGeneration);
if (
  invalidResult !== false
  || state.emfTelemetryMutationUnresolved !== true
  || !nodes["#new-case-button"].disabled
) throw new Error("invalid bootstrap status cleared unresolved mutation");
const confirmedResult = await loadEmfTelemetryStatus(caseGeneration);
if (
  confirmedResult !== true
  || state.emfTelemetryMutationUnresolved
  || nodes["#new-case-button"].disabled
  || state.emfTelemetryActive !== false
) throw new Error("authoritative bootstrap status did not recover unresolved mutation");
"""

    _assert_node_success(_run_app_script(body))


def test_status_rejects_every_non_boolean_active_value() -> None:
    body = r"""
const malformed = [
  {},
  {active: null},
  {active: 0},
  {active: "false"},
  {active: new Boolean(false)},
];
for (const payload of malformed) {
  resetEmfDom(true);
  fetchImpl = async (url, options = {}) => {
    const method = String(options.method || "GET").toUpperCase();
    if (url === "/api/emf/status" && method === "GET") return response(payload);
    throw new Error(`unexpected request: ${method} ${url}`);
  };
  const confirmed = await loadEmfTelemetryStatus(caseGeneration);
  const state = window.MorphicWorkbenchState;
  if (confirmed !== false || state.emfTelemetryActive !== null || state.emfTelemetryStatus !== "unknown") {
    throw new Error(`malformed active accepted: ${JSON.stringify(payload)} / ${confirmed}`);
  }
  if (!nodes["#emf-enable-button"].disabled || !nodes["#emf-disable-button"].disabled) {
    throw new Error(`malformed active unlocked controls: ${JSON.stringify(payload)}`);
  }
  if (!nodes["#emf-telemetry-state"].textContent.includes("ungueltig")) {
    throw new Error(`malformed active lacks explicit error: ${JSON.stringify(payload)}`);
  }
}
"""

    _assert_node_success(_run_app_script(body))


def test_generation_drift_blocks_stale_mutation_status_and_hardware_updates() -> None:
    body = r"""
const mutation = deferred();
const mutationGeneration = caseGeneration;
let mutationStatusCalls = 0;
let mutationHardwareCalls = 0;
window.MorphicWorkbenchApi.enableEmfTelemetry = () => mutation.promise;
window.MorphicWorkbenchApi.loadEmfStatus = async () => {
  mutationStatusCalls += 1;
  return {active: true};
};
window.MorphicWorkbenchApi.loadHardware = async () => {
  mutationHardwareCalls += 1;
  return {snapshot: "stale-mutation"};
};
resetEmfDom(false);
const mutationOperation = setEmfTelemetryEnabled(true, mutationGeneration);
await Promise.resolve();
caseGeneration += 1;
resetEmfDom(false, "current-case");
nodes["#emf-telemetry-state"].textContent = "current case";
mutation.resolve({active: true});
const mutationResult = await mutationOperation;
if (
  mutationResult !== false || mutationStatusCalls !== 0 || mutationHardwareCalls !== 0
  || window.MorphicWorkbenchState.emfTelemetryActive !== false
  || window.MorphicWorkbenchState.emfTelemetryStatus !== "current-case"
  || nodes["#emf-telemetry-state"].textContent !== "current case"
) throw new Error("stale mutation updated the current case");

const status = deferred();
const statusGeneration = caseGeneration;
window.MorphicWorkbenchApi.loadEmfStatus = () => status.promise;
const statusOperation = loadEmfTelemetryStatus(statusGeneration);
await Promise.resolve();
caseGeneration += 1;
resetEmfDom(false, "newer-status");
nodes["#emf-telemetry-state"].textContent = "newer status";
status.resolve({active: true});
const statusResult = await statusOperation;
if (
  statusResult !== false || window.MorphicWorkbenchState.emfTelemetryActive !== false
  || window.MorphicWorkbenchState.emfTelemetryStatus !== "newer-status"
  || nodes["#emf-telemetry-state"].textContent !== "newer status"
) throw new Error("stale status updated the current case");

const hardware = deferred();
const hardwareGeneration = caseGeneration;
window.MorphicWorkbenchApi.loadHardware = () => hardware.promise;
window.MorphicWorkbenchState.hardwareTruth = {snapshot: "current-hardware"};
global.__renderedHardware.length = 0;
const hardwareOperation = loadHardwareTruth(hardwareGeneration);
await Promise.resolve();
caseGeneration += 1;
window.MorphicWorkbenchState.hardwareTruth = {snapshot: "newer-hardware"};
hardware.resolve({snapshot: "stale-hardware"});
await hardwareOperation;
if (
  window.MorphicWorkbenchState.hardwareTruth.snapshot !== "newer-hardware"
  || global.__renderedHardware.length !== 0
) throw new Error("stale hardware updated the current case");
"""

    _assert_node_success(_run_app_script(body))


def test_failed_hardware_refresh_invalidates_stale_emf_rendering() -> None:
    body = r"""
window.MorphicWorkbenchState.hardwareTruth = {snapshot: "stale-active"};
nodes["#realtime-calibration"].children = [node({className: "emf-index-gauge"})];
nodes["#hardware-gate-warnings"].children = [node({textContent: "stale warning"})];
window.MorphicWorkbenchApi.loadHardware = async () => {
  throw new Error("hardware unavailable");
};

await loadHardwareTruth(caseGeneration);

if (window.MorphicWorkbenchState.hardwareTruth !== null) {
  throw new Error("failed refresh retained stale hardware snapshot");
}
if (nodes["#realtime-calibration"].children.length !== 0) {
  throw new Error("failed refresh retained stale EMF gauge");
}
if (nodes["#hardware-gate-warnings"].children.length !== 0) {
  throw new Error("failed refresh retained stale hardware warnings");
}
if (!nodes["#hardware-truth-grid"].children[0]?.textContent.includes("nicht erreichbar")) {
  throw new Error("failed refresh did not retain the explicit endpoint error");
}
"""

    _assert_node_success(_run_app_script(body))


def test_page_bootstrap_reads_status_without_posting_activation() -> None:
    body = r"""
const calls = [];
fetchImpl = async (url, options = {}) => {
  const method = String(options.method || "GET").toUpperCase();
  calls.push({method, url: String(url)});
  if (url === "/api/workbench/registry") return response({steps: []});
  if (url === "/api/health") {
    return response({ok: true, python: {}, profiles: 0, databases: []});
  }
  if (url === "/api/sources") return response({count: 0, sources: [], status_counts: {}});
  if (String(url).startsWith("/api/workbench/scan-profile-catalog?")) {
    return response({
      profile_level: 3,
      pool_authority: {fingerprint: "a".repeat(64)},
      internal: {count: 9, profiles: []},
      external: {count: 0, active_source_count: 0},
    });
  }
  if (url === "/api/emf/status") return response({active: false});
  if (String(url).startsWith("/api/workbench/hardware?")) return response({components: {}});
  if (url === "/api/reports") return response({clients: []});
  throw new Error(`unexpected bootstrap request: ${method} ${url}`);
};

await bootstrapWorkbench();
await waitUntil(() => calls.some(call => call.url === "/api/emf/status"));
await Promise.resolve();
const emfCalls = calls.filter(call => call.url.startsWith("/api/emf/"));
if (JSON.stringify(emfCalls) !== JSON.stringify([{method: "GET", url: "/api/emf/status"}])) {
  throw new Error(`bootstrap activation calls: ${JSON.stringify(emfCalls)}`);
}
"""

    _assert_node_success(_run_app_script(body))


def test_emf_control_flow_does_not_persist_browser_draft_or_template_state() -> None:
    body = r"""
let draftCalls = 0;
let templateCalls = 0;
window.MorphicWorkbenchApi.saveDraft = async () => { draftCalls += 1; };
window.MorphicWorkbenchApi.saveTemplate = async () => { templateCalls += 1; };
fetchImpl = async (url, options = {}) => {
  const method = String(options.method || "GET").toUpperCase();
  if (url === "/api/emf/enable" && method === "POST") return response({active: false});
  if (url === "/api/emf/status" && method === "GET") return response({active: true});
  if (String(url).startsWith("/api/workbench/hardware?") && method === "GET") return response({});
  throw new Error(`unexpected request: ${method} ${url}`);
};

await setEmfTelemetryEnabled(true, caseGeneration);
const payloads = [formScanPayload(), clientContextDraftPayload()];
if (storageWrites.length || sessionWrites.length || draftCalls || templateCalls) {
  throw new Error(JSON.stringify({storageWrites, sessionWrites, draftCalls, templateCalls}));
}
const persistedKeys = payloads.flatMap(payload => Object.keys(payload));
if (persistedKeys.some(key => /emf/i.test(key))) {
  throw new Error(`EMF authority leaked into a persisted payload: ${JSON.stringify(payloads)}`);
}
"""

    _assert_node_success(_run_app_script(body))

    source = APP_JS.read_text(encoding="utf-8")
    for start, end in (
        ("function formScanPayload(", "function clientContextDraftPayload("),
        ("function clientContextDraftPayload(", "function showClientContextState("),
        ("function groupDraftPayload(", "function resetGroupDraftForm("),
    ):
        block = source.split(start, 1)[1].split(end, 1)[0]
        assert "emfTelemetry" not in block
        assert "emf_telemetry" not in block
    template_block = source.split(
        'const saveTemplate = $("#save-template-button")', 1
    )[1].split('const newCase = $("#new-case-button")', 1)[0]
    assert "emfTelemetry" not in template_block
    assert "emf_telemetry" not in template_block


def test_gate5_workbench_uses_only_modern_emf_urls() -> None:
    api_source = API_JS.read_text(encoding="utf-8")
    app_source = APP_JS.read_text(encoding="utf-8")
    control_path = app_source.split(
        "function updateEmfTelemetryControls(", 1
    )[1].split("async function generatePreview(", 1)[0]

    assert 'requestJson("/api/emf/status")' in api_source
    assert 'requestJson("/api/emf/enable", {' in api_source
    assert 'requestJson("/api/emf/disable", {' in api_source
    assert "/api/v1/emf" not in api_source
    assert "/api/v1/emf" not in control_path
    assert "localStorage" not in control_path
    assert "sessionStorage" not in control_path
    assert "saveDraft" not in control_path
    assert "saveTemplate" not in control_path
