from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"


def test_interrupted_harmonization_poll_renders_phase_lease_and_manual_action() -> None:
    index_html = INDEX_HTML.read_text(encoding="utf-8")
    assert 'id="harmonization-phase-label"' in index_html
    assert 'id="harmonization-lease-label"' in index_html
    assert 'id="harmonization-error-label"' in index_html

    script = f"""
const fs = require("fs");
const vm = require("vm");
function node() {{
  return {{
    textContent: "",
    style: {{}},
    hidden: false,
  }};
}}
const nodes = {{
  "#harmonization-status-label": node(),
  "#harmonization-progress-fill": node(),
  "#harmonization-progress-label": node(),
  "#harmonization-phase-label": node(),
  "#harmonization-cycles-label": node(),
  "#harmonization-error-label": node(),
  "#harmonization-lease-label": node(),
}};
global.window = {{
  MorphicWorkbenchApi: {{
    async pollHarmonization() {{
      return {{
        status: "interrupted",
        progress_percent: 50,
        phase: "pause",
        cycles_completed: 2,
        total_cycles: 4,
        lease: {{ heartbeat_at: "2026-07-11T10:00:00" }},
        manual_action_required: true,
      }};
    }},
  }},
  MorphicWorkbenchState: {{ activeHarmonizationJobId: "interrupted-job" }},
  addEventListener() {{}},
}};
global.document = {{
  querySelector(selector) {{ return nodes[selector] || null; }},
}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r}, "utf8"));
(async () => {{
  await pollHarmonizationJob("interrupted-job");
  const expected = {{
    "#harmonization-phase-label": "pause",
    "#harmonization-lease-label": "2026-07-11T10:00:00",
    "#harmonization-error-label": "Manuelle Folgeaktion erforderlich",
  }};
  for (const [selector, value] of Object.entries(expected)) {{
    if (nodes[selector].textContent !== value) {{
      throw new Error(`${{selector}}: expected '${{value}}', got '${{nodes[selector].textContent}}'`);
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


def test_starting_harmonization_enables_refresh_and_stop_controls() -> None:
    script = f"""
const fs = require("fs");
const vm = require("vm");
function node() {{
  return {{
    textContent: "",
    style: {{}},
    hidden: true,
    disabled: true,
  }};
}}
const nodes = {{
  "#harmonization-form": null,
  "#harmonization-status-panel": node(),
  "#harmonization-job-id-label": node(),
  "#harmonization-mode-label": node(),
  "#harmonization-refresh-button": node(),
  "#harmonization-stop-button": node(),
  "#harmonization-start-button": node(),
}};
global.window = {{
  MorphicWorkbenchApi: {{
    async startHarmonization() {{ return {{job_id: "harm-controls"}}; }},
    async pollHarmonization() {{
      return {{
        status: "interrupted",
        progress_percent: 0,
        phase: "interrupted",
        cycles_completed: 0,
        total_cycles: 0,
        lease: {{}},
        manual_action_required: true,
      }};
    }},
  }},
  MorphicWorkbenchState: {{ activeHarmonizationJobId: null }},
  addEventListener() {{}},
}};
global.document = {{
  querySelector(selector) {{ return nodes[selector] || null; }},
}};
vm.runInThisContext(fs.readFileSync({str(APP_JS)!r}, "utf8"));
(async () => {{
  const entry = {{id: "report-ready", session_id: "session-a", kind: "TXT", size: 1}};
  const catalogEffects = transitionReportAuthority({{
    type: REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED,
    generation: caseGeneration,
  }});
  const catalogRequest = catalogEffects.find((effect) => effect.type === "LOAD_CATALOG").request;
  transitionReportAuthority({{
    type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
    generation: caseGeneration,
    request: catalogRequest,
    entries: [entry],
  }});
  const previewEffects = transitionReportAuthority({{
    type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
    generation: caseGeneration,
    reportId: "report-ready",
    intent: "manual",
  }});
  const previewRequest = previewEffects.find((effect) => effect.type === "LOAD_PREVIEW").request;
  transitionReportAuthority({{
    type: REPORT_AUTHORITY_EVENT.PREVIEW_SUCCEEDED,
    request: previewRequest,
    view: {{reportId: "report-ready", mode: "text", kind: "TXT", title: "ready", content: "ready", size: 1}},
  }});
  await startHarmonizationJob();
  if (nodes["#harmonization-refresh-button"].disabled) {{
    throw new Error("Refresh control remains disabled after a harmonization job starts");
  }}
  if (nodes["#harmonization-stop-button"].disabled) {{
    throw new Error("Stop control remains disabled after a harmonization job starts");
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
