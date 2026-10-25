from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"
API_JS = ROOT / "apps" / "web" / "static" / "workbench-api.js"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"


def test_review_cards_accept_hardware_components_dictionary() -> None:
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
    get textContent() {{ return this._text + this.children.map((child) => child.textContent).join(""); }},
    set textContent(value) {{ this._text = String(value); this.children = []; }},
  }};
}}
const cards = {{
  "#review-client": node("article"),
  "#review-focus": node("article"),
  "#review-profile": node("article"),
  "#review-hardware": node("article"),
}};
global.window = {{}};
global.document = {{
  querySelector(selector) {{ return cards[selector] || null; }},
  createElement(tagName) {{ return node(tagName); }},
  createTextNode(value) {{ const text = node("#text"); text.textContent = value; return text; }},
}};
vm.runInThisContext(fs.readFileSync({str(RENDER_JS)!r}, "utf8"));
window.MorphicWorkbenchRender.renderReviewCards(
  {{}},
  {{components: {{cpu: {{label: "CPU", status: "software_fallback"}}}}}}
);
if (!cards["#review-hardware"].textContent.includes("CPU")) {{
  throw new Error("Hardware-Review enthält die Dictionary-Komponente nicht");
}}
"""

    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_review_cards_explain_both_adaptive_limits_states() -> None:
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
    get textContent() {{ return this._text + this.children.map((child) => child.textContent).join(""); }},
    set textContent(value) {{ this._text = String(value); this.children = []; }},
  }};
}}
const cards = {{
  "#review-client": node("article"),
  "#review-focus": node("article"),
  "#review-profile": node("article"),
  "#review-hardware": node("article"),
}};
global.window = {{}};
global.document = {{
  querySelector(selector) {{ return cards[selector] || null; }},
  createElement(tagName) {{ return node(tagName); }},
  createTextNode(value) {{ const text = node("#text"); text.textContent = value; return text; }},
}};
vm.runInThisContext(fs.readFileSync({str(RENDER_JS)!r}, "utf8"));
window.MorphicWorkbenchRender.renderReviewCards(
  {{adaptive_limits: false, local_ai_enabled: false}},
  {{components: {{}}}}
);
if (!cards["#review-profile"].textContent.includes(
  "aus (voller angeforderter Detailumfang; ownergebundene Top-Profile bis Top-N)"
)) {{
  throw new Error("default-off effect is not visible in review");
}}
if (!cards["#review-profile"].textContent.includes("Lokale KIaus")) {{
  throw new Error("local AI default-off truth is not visible in review");
}}
window.MorphicWorkbenchRender.renderReviewCards(
  {{adaptive_limits: true, local_ai_enabled: true}},
  {{components: {{}}}}
);
if (!cards["#review-profile"].textContent.includes(
  "aktiv (Phase-2-Detail-Cap; höchstens 5 ownergebundene Top-Profile)"
)) {{
  throw new Error("opt-in effect is not visible in review");
}}
if (!cards["#review-profile"].textContent.includes("Lokale KIaktiviert")) {{
  throw new Error("local AI opt-in truth is not visible in review");
}}
"""

    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_scan_preview_rejects_non_success_http_response() -> None:
    script = f"""
const fs = require("fs");
const vm = require("vm");
global.window = {{}};
global.fetch = async () => ({{
  ok: false,
  status: 422,
  async json() {{ return {{detail: "focus must not be blank"}}; }},
}});
vm.runInThisContext(fs.readFileSync({str(API_JS)!r}, "utf8"));
(async () => {{
  try {{
    await window.MorphicWorkbenchApi.loadScanPreview({{}});
    throw new Error("loadScanPreview resolved despite HTTP 422");
  }} catch (error) {{
    if (error.status !== 422 || error.message !== "focus must not be blank") {{
      throw error;
    }}
  }}
}})().catch((error) => {{ console.error(error); process.exit(1); }});
"""

    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_review_cards_render_untrusted_values_as_text() -> None:
    source = RENDER_JS.read_text(encoding="utf-8")
    review_cards = source.split("renderReviewCards(formData, hardwarePayload,", 1)[1].split(
        "/* ── Results Workspace", 1
    )[0]

    assert ".innerHTML" not in review_cards
    assert "textContent" in review_cards


def test_all_workbench_api_helpers_reject_non_success_responses() -> None:
    script = f"""
const fs = require("fs");
const vm = require("vm");
global.window = {{}};
global.fetch = async () => ({{
  ok: false,
  status: 503,
  async json() {{ return {{detail: "service unavailable"}}; }},
}});
vm.runInThisContext(fs.readFileSync({str(API_JS)!r}, "utf8"));
(async () => {{
  const api = window.MorphicWorkbenchApi;
  const calls = [
    () => api.loadRegistry(), () => api.loadHardware("standard"),
    () => api.loadDraft(), () => api.saveDraft({{}}), () => api.saveTemplate("name", {{}}),
    () => api.loadRunTrace("run"), () => api.loadHealth(), () => api.loadSources(),
    () => api.loadScanPreview({{}}), () => api.startScanJob({{}}, "scan-test-authority"), () => api.pollScanJob("job"),
    () => api.loadScanResults("job"), () => api.loadReports(), () => api.loadReportPreview("report"),
    () => api.startHarmonization({{}}, "harm-test-authority"), () => api.pollHarmonization("job"), () => api.stopHarmonization("job"),
  ];
  for (const call of calls) {{
    try {{
      await call();
      throw new Error("API helper resolved despite HTTP 503");
    }} catch (error) {{
      if (error.status !== 503 || error.message !== "service unavailable") {{
        throw error;
      }}
    }}
  }}
}})().catch((error) => {{ console.error(error); process.exit(1); }});
"""

    result = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
