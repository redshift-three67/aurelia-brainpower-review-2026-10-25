from __future__ import annotations

import json
import os
import subprocess
import threading
from pathlib import Path

import pytest
from pydantic import ValidationError

from apps.web.contracts import HarmonizationRequest
from apps.web.harmonization import WorkerHarmonizationService
from apps.web.main import create_app
from apps.web.scan_jobs import (
    LocalScanJobService,
    ScanJobOwnershipError,
    _LocalScanJob,
    _update_progress_state,
)
from core.compliance.operator_context import operator_owner_scope
from tests.test_web_shell import FakeHarmonizationJobs, FakeScanJobs, app_with_harmonization_report, request
from tests.test_workbench_dogfood_scan_truth import _scan_payload
from services import harmonization_worker as worker
from tools.reporting_common import client_slug


class _FakeAuthority:
    def get_for_replay(self, job_id: str, **kwargs):
        raise KeyError(job_id)

    def start(self, command, **kwargs):
        return {"job_id": kwargs["job_id"], "status": "running"}

    def get(self, job_id: str):
        return {"job_id": job_id, "status": "running"}


def test_scan_stage_order_is_monotonic_and_current_stage_is_not_completed() -> None:
    state = _update_progress_state(
        lines=[
            "Screening: alle Haupt-Profile...",
            "Top Profile Auswahl...",
            "Phase 2: Vollanalyse...",
            "Export erstellt",
            "Synergy-Bericht erstellt",
            "Remedy-Bericht erstellt",
            "Interpretation Report erstellt",
            "Trend Report erstellt",
        ],
        status="running",
        labels=[],
        seen_labels=set(),
        current_substep=None,
        current_phase=None,
        progress_percent=0.0,
        stage_ids=[],
        seen_stage_ids=set(),
        current_stage_id=None,
    )
    assert state["current_stage_id"] == "trend"
    assert state["completed_stage_ids"] == [
        "phase1", "top_profiles", "phase2", "export", "synergy", "remedy", "interpretation"
    ]
    assert state["progress_percent"] == 87.5

    completed = _update_progress_state(
        lines=[],
        status="completed",
        labels=state["_all_labels"],
        seen_labels=state["_seen_labels"],
        current_substep=state["current_substep"],
        current_phase=state["current_phase"],
        progress_percent=state["progress_percent"],
        stage_ids=state["_all_stage_ids"],
        seen_stage_ids=state["_seen_stage_ids"],
        current_stage_id=state["current_stage_id"],
    )
    assert completed["completed_stage_ids"][-1] == "trend"
    assert completed["progress_percent"] == 100.0


def test_worker_job_persists_report_and_owner_binding(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    monkeypatch.setattr(worker, "_process_authority_service", _FakeAuthority)
    service = WorkerHarmonizationService()

    started = service.start(
        mode="harmonization",
        target_frequency=528.0,
        duration_minutes=21,
        intention="harmonization",
        hardware_config={"use_cpu": False},
        report_id="report-1",
        workbench_mode="standard",
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    reloaded = service.get(str(started["job_id"]))
    assert reloaded["report_id"] == "report-1"
    assert reloaded["workbench_mode"] == "standard"
    assert reloaded["tenant_id"] == "tenant-a"
    assert reloaded["operator_id"] == "operator-a"


def test_harmonization_contract_rejects_contradictory_duration_and_solfeggio_fields() -> None:
    base = {"report_id": "report-1", "target_frequency": 528.0, "duration_factor": 1}
    with pytest.raises(ValidationError):
        HarmonizationRequest.model_validate({**base, "duration_minutes": 4})
    with pytest.raises(ValidationError):
        HarmonizationRequest.model_validate({**base, "solfeggio_base": 432.0})


@pytest.mark.parametrize("field", ["pulse_seconds", "pause_seconds"])
def test_harmonization_contract_bounds_stop_latency(field: str) -> None:
    with pytest.raises(ValidationError):
        HarmonizationRequest.model_validate(
            {"report_id": "report-1", "target_frequency": 528.0, field: 5.01}
        )


def test_harmonization_contract_bounds_productive_frequency() -> None:
    with pytest.raises(ValidationError):
        HarmonizationRequest(report_id="report-1", target_frequency=2000.01)


def test_frontend_has_case_generation_guards_and_complete_sensitive_reset() -> None:
    source = Path("apps/web/static/app.js").read_text(encoding="utf-8")
    assert "let caseGeneration = 0" in source
    assert "caseGeneration += 1" in source
    assert "if (generation !== caseGeneration) return" in source
    reset = source.split("function resetWorkbenchForNewCase()", 1)[1].split("/* ── Choice", 1)[0]
    for token in (
        '"#consent-local"',
        '"#consent-safety"',
        'document.querySelectorAll(\'[form="scan-form"]\')',
        "activeGroupConsentClientId = null",
        '"#group-consent-valid-until"',
        '"#group-identity-retention-days"',
    ):
        assert token in reset


def test_scan_poll_status_is_read_only_and_terminal_sync_is_explicit_post() -> None:
    main = Path("apps/web/main.py").read_text(encoding="utf-8")
    status = main.split('@app.get("/api/scan/jobs/{job_id}")', 1)[1].split("@app.", 1)[0]
    assert "ensure_run_trace" not in status
    assert '@app.post("/api/scan/jobs/{job_id}/sync-trace")' in main
    app_js = Path("apps/web/static/app.js").read_text(encoding="utf-8")
    assert "syncScanRunTrace(jobId)" in app_js


def test_frontend_run_trace_errors_are_optional_except_authentication() -> None:
    source = Path("apps/web/static/app.js").read_text(encoding="utf-8")
    assert "function isOptionalRunTraceError(error)" in source
    classifier = source.split(
        "function isOptionalRunTraceError(error)", 1
    )[1].split("\n}", 1)[0]
    assert "![401, 403].includes(Number(error?.status))" in classifier
    finalization = source.split("async function finalizeTerminalScan", 1)[1].split(
        "/* ── Health & Sources", 1
    )[0]
    load = source.split("async function loadScanResults", 1)[1].split(
        "/* ── Reports", 1
    )[0]
    assert "isOptionalRunTraceError(error)" in finalization
    assert "isOptionalRunTraceError(e)" in load
    assert "[401, 403].includes(e?.status)" in load


def test_completed_scan_ignores_non_auth_trace_failures_in_both_catches() -> None:
    app_js = Path("apps/web/static/app.js").resolve()
    script = f"""
const fs = require('fs');
const vm = require('vm');
function node() {{
  return {{
    textContent: '', className: '', disabled: false, style: {{}},
    setAttribute() {{}}, replaceChildren() {{}}, appendChild() {{}},
  }};
}}
const nodes = {{
  '#job-status-label': node(), '#scan-refresh-button': node(),
  '#start-analysis-button': node(), '#preview-state': node(),
}};
global.window = {{
  MorphicWorkbenchState: {{activeJobId: null, scanRunActive: false}},
  MorphicWorkbenchApi: {{}},
  MorphicWorkbenchRender: {{
    renderSubstepTimeline() {{}}, renderResults() {{}}, renderRunTrace() {{}},
  }},
  addEventListener() {{}},
}};
global.document = {{
  querySelector(selector) {{ return nodes[selector] || null; }},
  querySelectorAll() {{ return []; }},
  createElement() {{ return node(); }},
}};
global.setTimeout = () => 1;
vm.runInThisContext(fs.readFileSync({json.dumps(str(app_js))}, 'utf8'));

async function run(target, errorKind) {{
  const jobId = `scan-${{target}}-${{errorKind}}`;
  const failure = errorKind === 'http'
    ? Object.assign(new Error('rate limited'), {{status: 429}})
    : new TypeError('network failed');
  window.MorphicWorkbenchState.activeJobId = jobId;
  window.MorphicWorkbenchState.scanRunActive = true;
  scanPollDegradation = null;
  showInlineState('', 'neutral');
  window.MorphicWorkbenchApi = {{
    async pollScanJob() {{
      return {{
        status: 'completed', progress_percent: 100, completed_substeps: [],
        completed_stage_ids: [], current_stage_id: null,
      }};
    }},
    async syncScanRunTrace() {{ if (target === 'sync') throw failure; }},
    async loadScanResults() {{ return {{top_profiles: []}}; }},
    async loadRunTrace() {{ if (target === 'load') throw failure; return {{status: 'completed'}}; }},
    async loadReports() {{ return {{clients: []}}; }},
  }};
  await pollScanJob(jobId, caseGeneration, 0);
  const actual = {{
    status: nodes['#job-status-label'].textContent,
    inline: nodes['#preview-state'].textContent,
    active: window.MorphicWorkbenchState.scanRunActive,
  }};
  if (actual.status !== 'abgeschlossen' || actual.inline.includes('nicht erreichbar') || actual.active) {{
    throw new Error(`${{target}}/${{errorKind}}: ${{JSON.stringify(actual)}}`);
  }}
}}
(async () => {{
  for (const target of ['sync', 'load']) {{
    for (const errorKind of ['http', 'network']) await run(target, errorKind);
  }}
}})().catch(error => {{ console.error(error); process.exit(1); }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_stopped_scan_releases_authority_when_trace_sync_requires_authentication() -> None:
    app_js = Path("apps/web/static/app.js").resolve()
    script = f"""
const fs = require('fs');
const vm = require('vm');
function node() {{
  return {{
    textContent: '', className: '', disabled: false, style: {{}},
    setAttribute() {{}}, replaceChildren() {{}}, appendChild() {{}},
  }};
}}
const nodes = {{
  '#job-status-label': node(), '#scan-refresh-button': node(),
  '#scan-stop-button': node(), '#start-analysis-button': node(),
  '#preview-state': node(),
}};
const calls = {{results: 0, reports: 0}};
global.window = {{
  MorphicWorkbenchState: {{
    activeJobId: 'scan-stopped-auth', scanRunActive: true,
    scanProfileCatalogStatus: 'ready', scanProfileCatalogLevel: 3,
    scanProfileCatalog: {{profile_level: 3, pool_authority: {{fingerprint: 'a'.repeat(64)}}, internal: {{count: 9, profiles: Array.from({{length: 9}}, (_, i) => ({{id: `p-${{i}}`, label: `P ${{i}}`}}))}}}},
  }},
  MorphicWorkbenchApi: {{
    async pollScanJob() {{
      return {{status: 'stopped', completed_substeps: [], completed_stage_ids: []}};
    }},
    async syncScanRunTrace() {{
      throw Object.assign(new Error('authentication required'), {{status: 403}});
    }},
    async loadScanResults() {{ calls.results += 1; return {{}}; }},
    async loadReports() {{ calls.reports += 1; return {{}}; }},
  }},
  MorphicWorkbenchRender: {{renderSubstepTimeline() {{}}}},
  addEventListener() {{}},
}};
global.document = {{
  querySelector(selector) {{ if (selector.includes('name="top_n"')) return {{value: '5'}}; return nodes[selector] || null; }},
  querySelectorAll() {{ return []; }},
  createElement() {{ return node(); }},
}};
global.setTimeout = () => 1;
global.clearTimeout = () => {{}};
vm.runInThisContext(fs.readFileSync({json.dumps(str(app_js))}, 'utf8'));

(async () => {{
  await pollScanJob('scan-stopped-auth', caseGeneration, 0);
  const actual = {{
    activeJobId: window.MorphicWorkbenchState.activeJobId,
    scanRunActive: window.MorphicWorkbenchState.scanRunActive,
    startDisabled: nodes['#start-analysis-button'].disabled,
    refreshDisabled: nodes['#scan-refresh-button'].disabled,
    stopDisabled: nodes['#scan-stop-button'].disabled,
    status: nodes['#job-status-label'].textContent,
    inline: nodes['#preview-state'].textContent,
    calls,
  }};
  if (
    actual.activeJobId !== null || actual.scanRunActive
    || actual.startDisabled || !actual.refreshDisabled || !actual.stopDisabled
    || !actual.status.includes('Anmeldung erforderlich')
    || !actual.inline.includes('Anmeldung')
    || actual.calls.results !== 0 || actual.calls.reports !== 0
  ) throw new Error(JSON.stringify(actual));
}})().catch(error => {{ console.error(error); process.exit(1); }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_unresolved_scan_statuses_keep_reservation_until_stopped() -> None:
    app_js = Path("apps/web/static/app.js").resolve()
    script = f"""
const fs = require('fs');
const vm = require('vm');
function node() {{
  return {{
    textContent: '', className: '', disabled: false, hidden: false, style: {{}},
    setAttribute() {{}}, replaceChildren() {{}}, appendChild() {{}},
  }};
}}
const nodes = {{
  '#job-status-label': node(), '#scan-refresh-button': node(),
  '#scan-stop-button': node(), '#start-analysis-button': node(),
  '#preview-state': node(),
}};
global.window = {{
  MorphicWorkbenchState: {{
    activeJobId: null, scanRunActive: false,
    scanProfileCatalogStatus: 'ready', scanProfileCatalogLevel: 3,
    scanProfileCatalog: {{profile_level: 3, pool_authority: {{fingerprint: 'a'.repeat(64)}}, internal: {{count: 9, profiles: Array.from({{length: 9}}, (_, i) => ({{id: `p-${{i}}`, label: `P ${{i}}`}}))}}}},
  }},
  MorphicWorkbenchApi: {{}},
  MorphicWorkbenchRender: {{renderSubstepTimeline() {{}}}},
  addEventListener() {{}},
}};
global.document = {{
  querySelector(selector) {{ if (selector.includes('name="top_n"')) return {{value: '5'}}; return nodes[selector] || null; }},
  querySelectorAll() {{ return []; }},
  createElement() {{ return node(); }},
}};
global.setTimeout = () => 1;
global.clearTimeout = () => {{}};
vm.runInThisContext(fs.readFileSync({json.dumps(str(app_js))}, 'utf8'));

const cases = [
  ['authority_ambiguous', {{status: 'authority_ambiguous'}}],
  ['rollback_failed', {{status: 'rollback_failed'}}],
  ['missing', {{}}],
  ['non-string', {{status: 17}}],
  ['unknown', {{status: 'unknown'}}],
];
(async () => {{
  for (const [label, unresolved] of cases) {{
    const jobId = `scan-${{label}}`;
    let polls = 0;
    let syncCalls = 0;
    let resultCalls = 0;
    window.MorphicWorkbenchState.activeJobId = jobId;
    window.MorphicWorkbenchState.scanRunActive = true;
    window.MorphicWorkbenchApi = {{
      async pollScanJob() {{
        polls += 1;
        return polls === 1 ? unresolved : {{status: 'stopped'}};
      }},
      async syncScanRunTrace() {{ syncCalls += 1; return {{}}; }},
      async loadScanResults() {{ resultCalls += 1; return {{}}; }},
    }};

    await pollScanJob(jobId, caseGeneration, 0);
    const retained = {{
      activeJobId: window.MorphicWorkbenchState.activeJobId,
      scanRunActive: window.MorphicWorkbenchState.scanRunActive,
      startDisabled: nodes['#start-analysis-button'].disabled,
      refreshDisabled: nodes['#scan-refresh-button'].disabled,
      stopDisabled: nodes['#scan-stop-button'].disabled,
      message: nodes['#preview-state'].textContent,
      syncCalls,
      resultCalls,
    }};
    if (
      retained.activeJobId !== jobId || !retained.scanRunActive
      || !retained.startDisabled || retained.refreshDisabled || retained.stopDisabled
      || !retained.message.includes('Status erneut laden')
      || !retained.message.includes('manuell stoppen')
      || retained.syncCalls !== 0 || retained.resultCalls !== 0
    ) throw new Error(`${{label}} retained: ${{JSON.stringify(retained)}}`);

    await pollScanJob(jobId, caseGeneration, 0);
    const released = {{
      activeJobId: window.MorphicWorkbenchState.activeJobId,
      scanRunActive: window.MorphicWorkbenchState.scanRunActive,
      startDisabled: nodes['#start-analysis-button'].disabled,
      refreshDisabled: nodes['#scan-refresh-button'].disabled,
      stopDisabled: nodes['#scan-stop-button'].disabled,
      status: nodes['#job-status-label'].textContent,
      resultCalls,
    }};
    if (
      released.activeJobId !== null || released.scanRunActive
      || released.startDisabled || !released.refreshDisabled || !released.stopDisabled
      || released.status !== 'gestoppt' || released.resultCalls !== 0
    ) throw new Error(`${{label}} released: ${{JSON.stringify(released)}}`);
  }}
}})().catch(error => {{ console.error(error); process.exit(1); }});
"""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_harmonization_replay_identity_is_owned_by_atomic_store_boundary() -> None:
    main = Path("apps/web/main.py").read_text(encoding="utf-8")
    route = main.split('@app.post("/api/harmonization/jobs")', 1)[1].split(
        '@app.get("/api/harmonization/jobs/{job_id}")',
        1,
    )[0]
    worker = Path("services/harmonization_worker.py").read_text(encoding="utf-8")

    assert "def _assert_harmonization_replay_identity" not in main
    assert "_assert_harmonization_replay_identity(" not in route
    assert "get_for_replay(" in route
    assert "reconcile_harmonization_start(" in worker
    assert "assert_harmonization_start_identity(" in worker


def test_accessibility_contract_uses_single_radio_semantics_and_fallback_ids() -> None:
    render = Path("apps/web/static/workbench-render.js").read_text(encoding="utf-8")
    choices = render.split("renderChoiceCards(containerId", 1)[1].split("/* ── Reale", 1)[0]
    assert 'aria-pressed' not in choices
    assert 'setAttribute("aria-checked"' in choices
    assert 'setAttribute("tabindex"' in choices
    assert 'case "ArrowRight"' in choices
    assert 'btn.id = `wizard-step-${i}`' in render
    assert 'panel.setAttribute("aria-labelledby"' in render
    app = Path("apps/web/static/app.js").read_text(encoding="utf-8")
    assert "FALLBACK_STEPS[index].id" in app


def test_cross_owner_harmonization_stop_is_rejected_before_side_effect(tmp_path: Path) -> None:
    jobs = FakeHarmonizationJobs()
    app, report_id = app_with_harmonization_report(tmp_path, jobs)
    started = request(
        app,
        "POST",
        "/api/harmonization/jobs",
        json_body={"report_id": report_id, "target_frequency": 432.0},
    )
    assert started.status_code == 200
    jobs.binding["operator_id"] = "different-operator"

    stopped = request(app, "POST", "/api/harmonization/jobs/harm-web/stop")

    assert stopped.status_code == 403
    assert jobs.stopped == []


class _TerminalProcess:
    def poll(self) -> int:
        return 0


def test_terminal_scan_flushes_unterminated_final_marker(tmp_path: Path) -> None:
    stdout = tmp_path / "stdout.log"
    stderr = tmp_path / "stderr.log"
    stdout.write_text("Trendbericht erstellt", encoding="utf-8")
    stderr.write_text("", encoding="utf-8")
    job = _LocalScanJob(
        job_id="terminal", command=[], process=_TerminalProcess(),
        stdout_path=stdout, stderr_path=stderr,
        created_at="2026-07-19T00:00:00+00:00",
        updated_at="2026-07-19T00:00:00+00:00",
    )
    snapshot = LocalScanJobService(tmp_path)._snapshot(job)
    assert snapshot["current_stage_id"] == "trend"
    assert "trend" in snapshot["completed_stage_ids"]


def test_stale_worker_save_cannot_overwrite_stop_marker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "_converge_harmonization_worker", lambda job: None)
    job = worker.HarmonizationJob(
        job_id="race", status="running", target_frequency=432.0,
        duration_minutes=21, intention="analysis", hardware_config={},
    )
    job.save()
    stale = worker.HarmonizationJob.load("race")
    assert stale is not None
    assert worker.stop_harmonization_job("race") is True
    stale.status = "running"
    stale.save()
    persisted = worker.HarmonizationJob.load("race")
    assert persisted is not None
    assert persisted.status == "stopped"


def test_pending_harmonization_can_be_stopped_before_worker_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    job = worker.HarmonizationJob(
        job_id="pending-stop",
        target_frequency=432.0,
        duration_minutes=21,
        intention="test",
        hardware_config={"use_cpu": False},
    )
    job.save()

    assert worker.stop_harmonization_job(job.job_id) is True
    assert worker.HarmonizationJob.load(job.job_id).status == "stopped"


def test_stop_waits_for_stale_save_and_publishes_stopped_last(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "_converge_harmonization_worker", lambda job: None)
    job = worker.HarmonizationJob(
        job_id="concurrent-stop",
        target_frequency=432.0,
        duration_minutes=21,
        intention="test",
        hardware_config={"use_cpu": False},
        status="running",
    )
    job.save()
    entered = threading.Event()
    release = threading.Event()
    original_write = worker._atomic_write_text

    def delayed_write(path: Path, content: str) -> None:
        if path.suffix == ".json" and not entered.is_set():
            entered.set()
            assert release.wait(timeout=5)
        original_write(path, content)

    monkeypatch.setattr(worker, "_atomic_write_text", delayed_write)
    stale = worker.HarmonizationJob.load(job.job_id)
    assert stale is not None
    save_thread = threading.Thread(target=stale.save)
    save_thread.start()
    assert entered.wait(timeout=5)
    stop_result: list[bool] = []
    stop_thread = threading.Thread(
        target=lambda: stop_result.append(worker.stop_harmonization_job(job.job_id))
    )
    stop_thread.start()
    release.set()
    save_thread.join(timeout=5)
    stop_thread.join(timeout=5)

    assert stop_result == [True]
    assert worker.HarmonizationJob.load(job.job_id).status == "stopped"


def test_v3_review_lifecycle_and_dom_contracts_are_explicit() -> None:
    app = Path("apps/web/static/app.js").read_text(encoding="utf-8")
    for function_name in (
        "loadClientContextDraft", "loadHealthAndSources", "loadHardwareTruth",
        "generatePreview", "startScanJob", "loadScanResults", "loadReports",
        "startHarmonizationJob", "loadInitialGroupDraft",
        "loadInitialGroupConsent", "loadInitialGroupAnalysisPolicy",
    ):
        body = app.split(f"async function {function_name}", 1)[1].split("\n}", 1)[0]
        assert "generation = caseGeneration" in body
        assert "generation !== caseGeneration" in body
    preview_body = app.split("async function renderReportPreview", 1)[1].split("\n}", 1)[0]
    assert "generation = caseGeneration" in preview_body
    assert "ensureReportAuthorityGeneration(generation)" in preview_body
    assert "REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED" in preview_body
    preview_guard = app.split("function reportPreviewRequestStillCurrent", 1)[1].split("\n}", 1)[0]
    assert "request.generation !== caseGeneration" in preview_guard
    assert 'const imageFile = $("#image-file-input")' in app
    assert "resetChoiceCardControls()" in app

    html = Path("apps/web/static/index.html").read_text(encoding="utf-8")
    positions = [html.index(f'data-stage-id="{stage}"') for stage in (
        "export", "synergy", "remedy", "interpretation", "trend",
    )]
    assert positions == sorted(positions)
    assert 'aria-label="Profilvorlage"' in html
    assert 'aria-label="Entropie-Modus"' in html
    assert html.count('tabindex="-1"') >= 2


def test_results_never_fall_back_to_unrelated_historical_sessions() -> None:
    main = Path("apps/web/main.py").read_text(encoding="utf-8")
    assert "matching or session_dirs" not in main
    assert 'job.get("artifact_paths", [])' in main


def test_trace_sync_rejects_duplicate_terminal_mutation(tmp_path: Path) -> None:
    app = create_app(scan_jobs=FakeScanJobs(), runtime_dir=tmp_path)
    started = request(app, "POST", "/api/scan/jobs", json_body=_scan_payload())
    assert started.status_code == 200
    job_id = started.json()["job_id"]
    assert request(app, "POST", f"/api/scan/jobs/{job_id}/sync-trace").status_code == 200
    assert request(app, "POST", f"/api/scan/jobs/{job_id}/sync-trace").status_code == 409


def test_terminal_trace_sync_reconstructs_and_finalizes_a_missing_trace(
    tmp_path: Path,
) -> None:
    app = create_app(scan_jobs=FakeScanJobs(), runtime_dir=tmp_path)
    started = request(app, "POST", "/api/scan/jobs", json_body=_scan_payload())
    assert started.status_code == 200
    job_id = started.json()["job_id"]
    trace_path = app.state.workbench_store._path_for("run_traces")
    trace_path.unlink()

    synchronized = request(app, "POST", f"/api/scan/jobs/{job_id}/sync-trace")

    assert synchronized.status_code == 200
    trace = app.state.workbench_store.get_run_trace(job_id)
    assert trace["run_id"] == job_id
    assert trace["job_id"] == job_id
    assert trace["status"] == "completed"
    assert trace["returncode"] == 0


class _HistoricalResultJobs:
    def __init__(self, export_root: Path, artifact_paths: list[Path] | None = None) -> None:
        self.export_root = export_root
        self.artifact_paths = artifact_paths or []
        self.owner_id = ""

    def get(self, job_id: str) -> dict[str, object]:
        return {
            "job_id": job_id,
            "status": "completed",
            "owner_id": self.owner_id,
            "created_at": "2026-07-19T10:00:00+00:00",
            "command": [
                "python", "-m", "apps.cli.main", "scan", "top3-scan",
                "Alt", "Fall", "--birth-date", "01011990", "--birth-place", "Bern",
                "--export", str(self.export_root),
            ],
            "artifact_paths": [str(path) for path in self.artifact_paths],
        }

    def get_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, object]:
        snapshot = self.get(job_id)
        if snapshot.get("owner_id") != expected_owner_id:
            raise ScanJobOwnershipError("scan job owner identity mismatch")
        return snapshot


def test_completed_job_does_not_claim_old_session_results(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "review-owner")
    export_root = tmp_path / "exports"
    slug = client_slug("Alt", "Fall", "01011990", "Bern")
    session = export_root / "Resonanz" / slug / "20200101_000000_SESSION_TOP3"
    profile = session / "old-profile"
    profile.mkdir(parents=True)
    (profile / "old_multiplex_scan.json").write_text(
        json.dumps({"profile": "old", "sub_results": {"top": [{"label": "old", "score": 99}]}}),
        encoding="utf-8",
    )
    os.utime(session, (1, 1))
    jobs = _HistoricalResultJobs(export_root)
    app = create_app(scan_jobs=jobs, runtime_dir=tmp_path / "runtime")
    jobs.owner_id = operator_owner_scope(app.state.operator_context)

    response = request(app, "GET", "/api/scan/jobs/historical/results")

    assert response.status_code == 200
    assert response.json()["top_profiles"] == []
    assert response.json()["export_paths"] == {}


def test_results_use_only_artifacts_emitted_by_the_exact_job(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "review-owner")
    export_root = tmp_path / "exports"
    exact = export_root / "Resonanz" / "client" / "run-one" / "profile" / "exact_multiplex_scan.json"
    later = export_root / "Resonanz" / "client" / "run-two" / "profile" / "later_multiplex_scan.json"
    for path, profile in ((exact, "exact-profile"), (later, "later-profile")):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"profile": profile, "sub_results": {"top": [{"label": profile, "score": 1}]}}),
            encoding="utf-8",
        )
    jobs = _HistoricalResultJobs(export_root, [exact])
    app = create_app(
        scan_jobs=jobs,
        runtime_dir=tmp_path / "runtime",
    )
    jobs.owner_id = operator_owner_scope(app.state.operator_context)

    payload = request(app, "GET", "/api/scan/jobs/exact/results").json()

    assert [entry["profile"] for entry in payload["top_profiles"]] == ["exact-profile"]
    assert "run-one" in payload["export_paths"]["archive"]
    assert "run-two" not in json.dumps(payload)


def test_results_ignore_emitted_artifacts_outside_the_job_export_root(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "review-owner")
    export_root = tmp_path / "exports"
    outside = tmp_path / "foreign" / "Resonanz" / "run" / "profile" / "foreign_multiplex_scan.json"
    outside.parent.mkdir(parents=True)
    outside.write_text(
        json.dumps({"profile": "foreign", "sub_results": {"top": [{"label": "leak", "score": 1}]}}),
        encoding="utf-8",
    )
    jobs = _HistoricalResultJobs(export_root, [outside])
    app = create_app(
        scan_jobs=jobs,
        runtime_dir=tmp_path / "runtime",
    )
    jobs.owner_id = operator_owner_scope(app.state.operator_context)

    payload = request(app, "GET", "/api/scan/jobs/exact/results").json()

    assert payload["top_profiles"] == []
    assert payload["top_resonances"] == []
    assert payload["export_paths"] == {}
