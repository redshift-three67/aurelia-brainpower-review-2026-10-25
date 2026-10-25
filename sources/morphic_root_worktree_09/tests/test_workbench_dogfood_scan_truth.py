from __future__ import annotations

import subprocess
from pathlib import Path

from apps.web.main import create_app
from apps.web.scan_jobs import _update_progress_state
from apps.web.workbench import current_scan_profile_pool_fingerprint
from tests.test_web_shell import FakeScanJobs, request


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"
APP_JS = ROOT / "apps" / "web" / "static" / "app.js"
RENDER_JS = ROOT / "apps" / "web" / "static" / "workbench-render.js"


def _scan_payload() -> dict[str, object]:
    return {
        "last_name": "Synthetic",
        "first_name": "QA",
        "birth_date": "01011990",
        "birth_place": "Testort",
        "focus": "Stabilitaet",
        "scan_profile_pool_fingerprint": current_scan_profile_pool_fingerprint(3),
        "consent_local": True,
        "consent_safety": True,
    }


def test_top3_progress_exposes_actual_stage_ids_without_separate_harmonization() -> None:
    progress = _update_progress_state(
        [
            "Screening aller Haupt-Profile",
            "TOP-3 RELEVANTE PROFILE",
            "Harmonisierung vorbereitet",
            "Export gespeichert",
        ],
        status="completed",
        labels=[],
        seen_labels=set(),
        stage_ids=[],
        seen_stage_ids=set(),
        current_substep=None,
        current_phase=None,
        current_stage_id=None,
        progress_percent=None,
    )

    assert progress["completed_stage_ids"] == ["phase1", "top_profiles", "export"]
    assert progress["current_stage_id"] == "export"
    assert "harmonization" not in progress["completed_stage_ids"]


def test_scan_timeline_declares_only_actual_top3_scan_stages() -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    timeline = html.split('id="substep-timeline"', 1)[1].split("</ul>", 1)[0]
    assert timeline.count('data-stage-id="') == 8
    for stage_id in (
        "phase1",
        "top_profiles",
        "phase2",
        "export",
        "trend",
        "interpretation",
        "remedy",
        "synergy",
    ):
        assert f'data-stage-id="{stage_id}"' in timeline
    assert "Harmonisierung" not in timeline
    assert "Tatsaechlicher Web-Scan" in html


def test_scan_timeline_uses_stage_ids_and_never_completes_unobserved_stages() -> None:
    source = RENDER_JS.read_text(encoding="utf-8")
    block = source.split("renderSubstepTimeline(", 1)[1].split("resetSubstepTimeline", 1)[0]
    assert "completedStageIds" in block
    assert "item.dataset.stageId" in block
    assert "allComplete" not in block
    assert "alle 12 Substeps abgeschlossen" not in block


def test_scan_status_poll_updates_minimized_run_trace(tmp_path: Path) -> None:
    jobs = FakeScanJobs()
    app = create_app(scan_jobs=jobs, runtime_dir=tmp_path)
    started = request(app, "POST", "/api/scan/jobs", json_body=_scan_payload())
    assert started.status_code == 200
    job_id = started.json()["job_id"]

    status = request(app, "GET", f"/api/scan/jobs/{job_id}")
    synced = request(app, "POST", f"/api/scan/jobs/{job_id}/sync-trace")
    trace = request(app, "GET", f"/api/workbench/run-trace/{job_id}").json()

    assert status.status_code == 200
    assert synced.status_code == 200
    assert trace["status"] == "completed"
    assert trace["returncode"] == 0
    assert trace["progress_percent"] == 100.0
    assert trace["current_substep"] == "Synergy abgeschlossen"
    assert "stdout_tail" not in trace
    assert "command" not in trace


def test_completed_scan_refreshes_report_catalog() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    finalization = source.split("async function finalizeTerminalScan", 1)[1].split(
        "/* ── Health & Sources", 1
    )[0]
    assert 'terminalStatus === "completed"' in finalization
    assert "await loadReports(generation" in finalization


def test_results_renderer_displays_profile_names_scores_and_resonances() -> None:
    script = f"""
const fs=require('fs'); const vm=require('vm');
function cls(){{return{{add(){{}},remove(){{}},toggle(){{}}}};}}
function node(tag='div'){{return{{tagName:tag,textContent:'',className:'',children:[],classList:cls(),appendChild(x){{this.children.push(x);}},replaceChildren(){{this.children=[];}},setAttribute(){{}}}};}}
const nodes={{'#results-metric-grid':node(),'#results-profile-list':node()}};
global.window={{MorphicWorkbenchState:{{}},addEventListener(){{}}}};
global.document={{querySelector(s){{return nodes[s]||null;}},querySelectorAll(){{return[];}},createElement(t){{return node(t);}},createTextNode(t){{const n=node('#text');n.textContent=t;return n;}}}};
vm.runInThisContext(fs.readFileSync({str(RENDER_JS)!r},'utf8'));
window.MorphicWorkbenchRender.renderResults({{status:'completed',job_id:'job-1',top_profiles:[{{profile:'regulation',score:8.25,top_resonances:[{{label:'Bronchien',score:8.25,group:'respiratory'}}]}}]}});
function text(n){{return [n.textContent,...n.children.flatMap(c=>[text(c)])].join(' ');}}
const rendered=text(nodes['#results-profile-list']);
if(!rendered.includes('regulation')||!rendered.includes('8,25')||!rendered.includes('Bronchien'))throw new Error(rendered);
"""
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
