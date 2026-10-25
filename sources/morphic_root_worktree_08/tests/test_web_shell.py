import asyncio
import json
from pathlib import Path
from typing import Any

from apps.web.main import create_app
from apps.cli.commands.helpers.harmonization_helpers import _render_basic_html
from core.compliance.runtime_manifest import RuntimeManifestService
from tools.reporting_common import render_legacy_html


ROOT = Path(__file__).resolve().parents[1]


class AsgiResponse:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self.body = body
        self.text = body.decode("utf-8")

    def json(self) -> dict[str, Any]:
        return json.loads(self.text)


class FakeScanJobs:
    def __init__(self) -> None:
        self.started: list[list[str]] = []

    def start(self, command: list[str]) -> dict[str, Any]:
        self.started.append(command)
        return {
            "executes": True,
            "job_id": "job-test",
            "status": "running",
            "command": command,
            "progress_percent": 12.5,
            "current_phase": "Phase 1",
            "current_substep": "Screening aller Haupt-Profile",
            "completed_substeps": [],
        }

    def get(self, job_id: str) -> dict[str, Any]:
        return {
            "job_id": job_id,
            "status": "completed",
            "returncode": 0,
            "command": self.started[-1] if self.started else [],
            "stdout_tail": "Analyse abgeschlossen",
            "stderr_tail": "",
            "progress_percent": 100.0,
            "current_phase": "Nachbereitung",
            "current_substep": "Synergy abgeschlossen",
            "completed_substeps": [
                "Screening aller Haupt-Profile",
                "TOP-7 RELEVANTE PROFILE",
                "Vollstaendige Analyse: regulation",
                "Export gespeichert",
            ],
        }


class FakeHarmonizationJobs:
    def __init__(self) -> None:
        self.started: list[dict[str, Any]] = []
        self.stopped: list[str] = []

    def start(
        self,
        *,
        mode: str,
        target_frequency: float,
        duration_minutes: int,
        intention: str,
        hardware_config: dict[str, bool],
    ) -> dict[str, Any]:
        self.started.append(
            {
                "mode": mode,
                "target_frequency": target_frequency,
                "duration_minutes": duration_minutes,
                "intention": intention,
                "hardware_config": hardware_config,
            }
        )
        return {
            "job_id": "harm-web",
            "status": "running",
            "mode": mode,
            "phase": "harmonizing",
            "target_frequency": target_frequency,
            "duration_minutes": duration_minutes,
            "intention": intention,
            "hardware_config": hardware_config,
            "progress_percent": 12.5,
            "cycles_completed": 5,
            "total_cycles": 40,
            "error_message": None,
        }

    def get(self, job_id: str) -> dict[str, Any]:
        return {
            "job_id": job_id,
            "status": "completed",
            "mode": "clearing",
            "phase": "completed",
            "target_frequency": 432.0,
            "duration_minutes": 5,
            "intention": "clearing",
            "progress_percent": 100.0,
            "cycles_completed": 300,
            "total_cycles": 300,
            "error_message": None,
        }

    def stop(self, job_id: str) -> dict[str, Any]:
        self.stopped.append(job_id)
        return {
            "job_id": job_id,
            "status": "stopped",
            "mode": "clearing",
            "phase": "stopped",
            "progress_percent": 12.5,
            "cycles_completed": 5,
            "error_message": None,
        }


def request(
    app: Any, method: str, path: str, json_body: dict[str, Any] | None = None
) -> AsgiResponse:
    body = json.dumps(json_body or {}).encode("utf-8") if json_body is not None else b""
    headers = [(b"host", b"testserver")]
    if json_body is not None:
        headers.extend(
            [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ]
        )

    async def run() -> AsgiResponse:
        sent = False
        events: list[dict[str, Any]] = []

        async def receive() -> dict[str, Any]:
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message: dict[str, Any]) -> None:
            events.append(message)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "path": path,
            "raw_path": path.encode("ascii"),
            "query_string": b"",
            "headers": headers,
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "scheme": "http",
        }
        await app(scope, receive, send)
        status = next(
            event["status"]
            for event in events
            if event["type"] == "http.response.start"
        )
        response_body = b"".join(
            event.get("body", b"")
            for event in events
            if event["type"] == "http.response.body"
        )
        return AsgiResponse(status, response_body)

    return asyncio.run(run())


def test_web_shell_serves_phase1_client_facing_first_screen(tmp_path: Path) -> None:
    app = create_app(runtime_dir=tmp_path)

    response = request(app, "GET", "/")

    assert response.status_code == 200
    assert "Morphic Engine V1" in response.text
    assert "Phase 1 Klienten-Workflow" in response.text
    assert "Klientenaufnahme" in response.text
    assert "Scan-Profil" in response.text
    assert "Analysefreigabe" in response.text
    assert "/static/app.css" in response.text
    assert "/static/app.js" in response.text


def test_web_shell_exposes_guided_workflow_stepping(tmp_path: Path) -> None:
    app = create_app(runtime_dir=tmp_path)

    response = request(app, "GET", "/")

    assert response.status_code == 200
    assert 'id="wizard-stepper"' in response.text
    assert 'id="wizard-progress-fill"' in response.text
    assert 'id="wizard-progress-label"' in response.text
    assert 'id="btn-prev"' in response.text
    assert 'id="btn-next"' in response.text
    assert 'data-step="5"' in response.text
    assert "Phase 2" not in response.text
    assert "Quellen &amp; Preflight" not in response.text
    assert "Berichte &amp; Datenschutz" not in response.text
    assert "Workflowabschluss &amp; Harmonisierung" in response.text
    assert "substep-list" in response.text
    assert 'id="start-analysis-button"' in response.text
    assert 'id="job-status-panel"' in response.text
    assert 'id="job-status-label"' in response.text
    assert 'id="job-phase-label"' in response.text
    assert 'id="job-substep-label"' in response.text
    assert 'id="job-substep-list"' in response.text
    assert 'name="profile_template"' in response.text
    assert 'name="entropy_mode"' in response.text
    assert 'name="image_path"' in response.text
    assert 'name="adaptive_limits"' in response.text
    assert 'id="harmonization-form"' in response.text
    assert 'name="intention"' in response.text
    assert 'id="harmonization-preview-state"' in response.text
    assert 'id="harmonization-start-button"' in response.text
    assert 'id="harmonization-status-panel"' in response.text
    assert 'id="harmonization-phase-label"' in response.text
    assert 'id="harmonization-cycles-label"' in response.text
    assert 'id="harmonization-error-label"' in response.text
    assert 'id="report-catalog-panel"' in response.text
    assert 'id="report-preview-panel"' in response.text


def test_web_shell_static_assets_define_wizard_behavior() -> None:
    js = (ROOT / "apps" / "web" / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "apps" / "web" / "static" / "app.css").read_text(encoding="utf-8")

    assert "const WORKFLOW_STEPS" in js
    assert "function goToStep" in js
    assert "function navigate" in js
    assert "function validateCurrentStep" in js
    assert "function updateProgress" in js
    assert "function startScanJob" in js
    assert "function pollScanJob" in js
    assert "function loadReports" in js
    assert "function renderReportPreview" in js
    assert "function formHarmonizationPayload" in js
    assert "function startHarmonizationJob" in js
    assert "function pollHarmonizationJob" in js
    assert "function renderProfileSelection" in js
    assert "function renderJobChecklist" in js
    assert "function renderJobProgressLabel" in js
    assert 'if (status === "stopped") return "gestoppt";' in js
    assert 'if (status === "error") return "fehler";' in js
    assert '"/api/scan/jobs"' in js
    assert '"/api/reports"' in js
    assert '"/api/harmonization/jobs"' in js
    assert '"#report-preview-frame"' in js
    assert '"#report-catalog-panel"' in js
    assert '"#report-preview-panel"' in js
    assert (
        'intention: String(data.get("intention") || "").trim() || "harmonization"' in js
    )
    assert (
        'profile_template: String(data.get("profile_template") || "").trim() || "phase1-default"'
        in js
    )
    assert (
        'entropy_mode: String(data.get("entropy_mode") || "").trim() || "legacy"' in js
    )
    assert 'image_path: String(data.get("image_path") || "").trim() || null' in js
    assert 'adaptive_limits: data.get("adaptive_limits") === "on"' in js
    assert "entry.relative_path" not in js
    assert ".wizard-panel" in css
    assert ".wizard-panel.active" in css
    assert ".wizard-step.completed" in css
    assert ".job-status-panel" in css
    assert ".job-substeps" in css
    assert ".job-checklist" in css
    assert ".reports-layout" in css
    assert ".report-catalog-panel" in css
    assert ".report-preview-panel" in css
    assert ".report-preview-frame" in css


def test_web_shell_accessibility_and_report_readability_baseline(
    tmp_path: Path,
) -> None:
    app = create_app(runtime_dir=tmp_path)

    response = request(app, "GET", "/")
    css = (ROOT / "apps" / "web" / "static" / "app.css").read_text(encoding="utf-8")
    legacy_html = render_legacy_html(
        title="Testbericht",
        subtitle="Lesbarkeit",
        body_html="<div class='section'><h2>Abschnitt</h2><p>Inhalt</p></div>",
        focus="Bronchien",
        meta=(("Profil", "Phase 1"),),
    )
    harmonization_html = _render_basic_html(
        {
            "client": {
                "first_name": "Klaus",
                "name": "Mustermann",
                "birth_date": "09041966",
                "birth_place": "Augsburg",
            },
            "focus": "Bronchien",
            "analysis": {},
            "sub_results": {"top": []},
        }
    )

    assert response.status_code == 200
    assert 'role="navigation"' in response.text
    assert 'aria-label="Workflow-Navigation"' in response.text
    assert 'aria-current="step"' in response.text
    assert 'role="status"' in response.text
    assert 'aria-live="polite"' in response.text
    assert 'aria-label="Berichtskatalog"' in response.text
    assert 'aria-label="Berichtsvorschau"' in response.text
    assert 'tabindex="0"' in response.text
    assert ":focus-visible" in css
    assert ".scroll-region" in css
    assert "max-height:" in legacy_html
    assert 'main class="report-shell"' in legacy_html
    assert "section class='report-block'" in harmonization_html
    assert "scroll-section" in harmonization_html


def test_web_shell_health_and_sources_api() -> None:
    app = create_app()

    health = request(app, "GET", "/api/health").json()
    sources = request(app, "GET", "/api/sources").json()

    assert {"ok", "profiles", "databases"}.issubset(health)
    assert sources["count"] >= 1
    assert any(source["id"] == "nlm_mesh" for source in sources["sources"])
    assert {"active", "disabled", "quarantined"}.issubset(sources["status_counts"])


def test_web_shell_privacy_clients_are_safe(tmp_path: Path) -> None:
    service = RuntimeManifestService(tmp_path)
    service.get_or_create_client(
        {
            "first_name": "Klaus",
            "last_name": "Mustermann",
            "birth_date": "09041966",
            "birth_place": "Augsburg",
        }
    )
    app = create_app(runtime_dir=tmp_path)

    response = request(app, "GET", "/api/privacy/clients")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["clients"][0]["client_id"].startswith("cli-")
    assert "Klaus" not in str(payload)
    assert "Mustermann" not in str(payload)


def test_web_shell_topn_scan_preview_is_non_executing() -> None:
    app = create_app()

    response = request(
        app,
        "POST",
        "/api/scan/preview",
        json_body={
            "last_name": "Deisenhofer",
            "first_name": "Klaus",
            "birth_date": "09041966",
            "birth_place": "Augsburg",
            "focus": "Bronchien",
            "profile_level": 3,
            "top_n": 7,
            "profile_template": "personal-balanced",
            "entropy_mode": "enhanced",
            "image_path": "C:/images/client-reference.png",
            "adaptive_limits": True,
            "consent_local": True,
            "consent_safety": True,
        },
    )

    payload = response.json()
    command = payload["command"]
    launcher = payload["launcher"]

    assert response.status_code == 200
    assert payload["profile_level"] == 3
    assert payload["profile_template"] == "personal-balanced"
    assert payload["entropy_mode"] == "enhanced"
    assert payload["image_path"] == "C:/images/client-reference.png"
    assert payload["image_enabled"] is True
    assert payload["adaptive_limits_requested"] is True
    assert payload["effective_result_limit"] == 5
    assert payload["executes"] is False
    assert command[1:5] == ["-m", "apps.cli.main", "scan", "top3-scan"]
    assert command[command.index("--export") + 1] == "C:\\Benutzer_Archive_Start"
    assert command[command.index("--hardware-profile") + 1] == "windows"
    assert command[command.index("--k-total") + 1] == "4096"
    assert command[command.index("--top-k") + 1] == "384"
    assert "--synergy" in command
    assert command[command.index("--synergy-combos") + 1] == "4"
    assert command[command.index("--synergy-threshold") + 1] == "6.0"
    assert "--top-n" in command
    assert command[command.index("--top-n") + 1] == "7"
    assert "--focus" in command
    assert command[command.index("--focus") + 1] == "Bronchien"
    assert launcher["script_path"] == "Run-MultiplexScan.ps1"
    assert launcher["cli_entrypoint"].endswith(" -m apps.cli.main scan top3-scan")
    assert payload["notes"]
    assert any("Adaptive Limits" in note for note in payload["notes"])
    assert "--p-emotion" not in command
    assert "--entropy-mode" not in command
    assert "--image" not in command


def test_web_shell_can_start_and_poll_scan_job() -> None:
    jobs = FakeScanJobs()
    app = create_app(scan_jobs=jobs)

    response = request(
        app,
        "POST",
        "/api/scan/jobs",
        json_body={
            "last_name": "Deisenhofer",
            "first_name": "Klaus",
            "birth_date": "09041966",
            "birth_place": "Augsburg",
            "focus": "Bronchien",
            "top_n": 7,
            "profile_template": "personal-focused",
            "entropy_mode": "hybrid",
            "image_path": "C:/images/client-reference.png",
            "adaptive_limits": True,
            "consent_local": True,
            "consent_safety": True,
        },
    )

    payload = response.json()
    command = payload["command"]
    launcher = payload["launcher"]

    assert response.status_code == 200
    assert payload["executes"] is True
    assert payload["job_id"] == "job-test"
    assert payload["status"] == "running"
    assert payload["progress_percent"] == 12.5
    assert payload["current_phase"] == "Phase 1"
    assert payload["current_substep"] == "Screening aller Haupt-Profile"
    assert payload["completed_substeps"] == []
    assert payload["profile_template"] == "personal-focused"
    assert payload["entropy_mode"] == "hybrid"
    assert payload["image_enabled"] is True
    assert payload["adaptive_limits_requested"] is True
    assert payload["effective_result_limit"] == 5
    assert jobs.started == [command]
    assert command[1:4] == ["-m", "apps.cli.main", "scan"]
    assert command[command.index("--export") + 1] == "C:\\Benutzer_Archive_Start"
    assert command[command.index("--hardware-profile") + 1] == "windows"
    assert command[command.index("--k-total") + 1] == "4096"
    assert command[command.index("--top-k") + 1] == "384"
    assert "--synergy" in command
    assert command[command.index("--synergy-combos") + 1] == "4"
    assert command[command.index("--synergy-threshold") + 1] == "6.0"
    assert command[command.index("--top-n") + 1] == "7"
    assert command[command.index("--focus") + 1] == "Bronchien"
    assert launcher["script_path"] == "Run-MultiplexScan.ps1"

    status = request(app, "GET", "/api/scan/jobs/job-test")

    assert status.status_code == 200
    assert status.json()["status"] == "completed"
    assert status.json()["stdout_tail"] == "Analyse abgeschlossen"
    assert status.json()["progress_percent"] == 100.0
    assert status.json()["current_phase"] == "Nachbereitung"
    assert status.json()["current_substep"] == "Synergy abgeschlossen"


def test_web_shell_lists_opens_and_previews_reports(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_file = (
        report_root
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260115_101530_multiplex_scan.html"
    )
    report_file.parent.mkdir(parents=True)
    report_file.write_text(
        "<html><body><script>alert(1)</script>Bericht Mustermann</body></html>",
        encoding="utf-8",
    )
    json_file = report_file.with_suffix(".json")
    json_file.write_text('{"focus": "Bronchien", "score": 7}', encoding="utf-8")
    txt_file = report_file.with_suffix(".txt")
    txt_file.write_text("Bericht Mustermann\nZeile 2", encoding="utf-8")
    pdf_file = report_file.with_suffix(".pdf")
    pdf_file.write_bytes(b"%PDF-1.4\n% test\n")
    app = create_app(
        runtime_dir=tmp_path / "runtime",
        report_roots=[report_root],
    )

    response = request(app, "GET", "/api/reports")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["client_count"] == 1
    assert payload["clients"][0]["client_id"] == "Mustermann_Klaus_09041966_Augsburg"
    assert payload["clients"][0]["label"] == "Mustermann Klaus 09041966 Augsburg"
    session = payload["clients"][0]["sessions"][0]
    assert session["session_id"] == "20260115_101530"
    assert session["label"] == "2026-01-15 10:15:30"
    html_report = next(
        report for report in session["files"] if report["kind"] == "HTML"
    )
    assert html_report["label"] == "Multiplex Scan"
    assert html_report["relative_path"].endswith(
        "Mustermann_Klaus_09041966_Augsburg/20260115_101530_multiplex_scan.html"
    )

    full_listing = app.state.report_catalog.list(include_all_formats=True)
    full_session = full_listing["clients"][0]["sessions"][0]

    preview = request(app, "GET", f"/api/reports/{html_report['id']}/preview")

    assert preview.status_code == 200
    preview_payload = preview.json()
    assert preview_payload["mode"] == "html"
    assert "Bericht Mustermann" in preview_payload["content"]
    assert "<script" not in preview_payload["content"]

    json_report = next(
        report for report in full_session["files"] if report["kind"] == "JSON"
    )
    json_preview = request(app, "GET", f"/api/reports/{json_report['id']}/preview")

    assert json_preview.status_code == 200
    assert '"focus": "Bronchien"' in json_preview.json()["content"]

    pdf_report = next(
        report for report in full_session["files"] if report["kind"] == "PDF"
    )
    pdf_preview = request(app, "GET", f"/api/reports/{pdf_report['id']}/preview")

    assert pdf_preview.status_code == 200
    assert pdf_preview.json()["mode"] == "file"
    assert pdf_preview.json()["file_url"].endswith(
        f"/api/reports/{pdf_report['id']}/file"
    )

    opened = request(app, "GET", f"/api/reports/{html_report['id']}/file")

    assert opened.status_code == 200
    assert "Bericht Mustermann" in opened.text


def test_web_shell_can_start_poll_and_stop_harmonization_job() -> None:
    harmonization_jobs = FakeHarmonizationJobs()
    app = create_app(harmonization_jobs=harmonization_jobs)

    start = request(
        app,
        "POST",
        "/api/harmonization/jobs",
        json_body={
            "intention": "clearing",
            "target_frequency": 528.0,
            "duration_minutes": 4,
            "use_cpu": False,
            "use_gpu": True,
            "use_ram": True,
            "use_websocket": False,
        },
    )

    payload = start.json()

    assert start.status_code == 200
    assert payload["job_id"] == "harm-web"
    assert payload["status"] == "running"
    assert payload["intention"] == "clearing"
    assert payload["phase"] == "harmonizing"
    assert payload["progress_percent"] == 12.5
    assert payload["cycles_completed"] == 5
    assert payload["error_message"] is None
    assert harmonization_jobs.started == [
        {
            "mode": "clearing",
            "target_frequency": 528.0,
            "duration_minutes": 4,
            "intention": "clearing",
            "hardware_config": {
                "use_cpu": False,
                "use_gpu": True,
                "use_ram": True,
                "use_websocket": False,
                "use_quartz": False,
            },
        }
    ]

    status = request(app, "GET", "/api/harmonization/jobs/harm-web")
    stopped = request(app, "POST", "/api/harmonization/jobs/harm-web/stop")

    assert status.status_code == 200
    assert status.json()["status"] == "completed"
    assert status.json()["mode"] == "clearing"
    assert status.json()["phase"] == "completed"
    assert stopped.status_code == 200
    assert stopped.json()["status"] == "stopped"
    assert stopped.json()["phase"] == "stopped"
    assert harmonization_jobs.stopped == ["harm-web"]
