from __future__ import annotations

from pathlib import Path

from apps.web.main import create_app
from apps.web.workbench import current_scan_profile_pool_fingerprint
from tests.test_web_shell import FakeHarmonizationJobs, request


def _report_root(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "reports"
    report = root / "Synthetic_QA_01011990_Testort" / "20260719_010101_report.html"
    report.parent.mkdir(parents=True)
    report.write_text("<html><body>QA</body></html>", encoding="utf-8")
    app = create_app(runtime_dir=tmp_path / "lookup", report_roots=[root])
    report_id = app.state.report_catalog_factory().list(include_all_formats=True)["reports"][0]["id"]
    return root, str(report_id)


def test_scan_export_root_matches_current_report_catalog_root(tmp_path: Path) -> None:
    root = tmp_path / "tenant-reports"
    app = create_app(runtime_dir=tmp_path / "runtime", report_roots=[root])
    preview = request(
        app,
        "POST",
        "/api/scan/preview",
        json_body={
            "last_name": "Synthetic",
            "first_name": "QA",
            "birth_date": "01011990",
            "birth_place": "Testort",
            "focus": "Stabilitaet",
            "scan_profile_pool_fingerprint": current_scan_profile_pool_fingerprint(3),
            "consent_local": True,
            "consent_safety": True,
        },
    ).json()
    command = preview["command"]
    assert Path(command[command.index("--export") + 1]).resolve() == root.resolve()


def test_reports_api_lists_all_supported_formats(tmp_path: Path) -> None:
    root, _ = _report_root(tmp_path)
    base = next(root.rglob("*.html")).with_suffix("")
    base.with_suffix(".json").write_text("{}", encoding="utf-8")
    base.with_suffix(".txt").write_text("QA", encoding="utf-8")
    base.with_suffix(".pdf").write_bytes(b"%PDF-1.4\n")
    app = create_app(runtime_dir=tmp_path / "runtime", report_roots=[root])
    payload = request(app, "GET", "/api/reports").json()
    kinds = {entry["kind"] for entry in payload["clients"][0]["sessions"][0]["files"]}
    assert kinds == {"HTML", "JSON", "TXT", "PDF"}


def test_harmonization_requires_and_persists_valid_report_binding(tmp_path: Path) -> None:
    root, report_id = _report_root(tmp_path)
    jobs = FakeHarmonizationJobs()
    app = create_app(runtime_dir=tmp_path / "runtime", report_roots=[root], harmonization_jobs=jobs)

    missing = request(app, "POST", "/api/harmonization/jobs", json_body={"duration_factor": 1})
    invalid = request(
        app,
        "POST",
        "/api/harmonization/jobs",
        json_body={"report_id": "not-a-current-report", "duration_factor": 1},
    )
    started = request(
        app,
        "POST",
        "/api/harmonization/jobs",
        json_body={
            "report_id": report_id,
            "workbench_mode": "expert",
            "duration_factor": 1,
        },
    )
    polled = request(app, "GET", "/api/harmonization/jobs/harm-web")

    assert missing.status_code == 422
    assert invalid.status_code == 404
    assert started.status_code == 200
    assert started.json()["report_id"] == report_id
    assert started.json()["workbench_mode"] == "expert"
    assert started.json()["duration_minutes"] == 21
    assert polled.json()["report_id"] == report_id
    assert polled.json()["workbench_mode"] == "expert"


def test_harmonization_frontend_binds_report_and_uses_factor_duration() -> None:
    source = (Path(__file__).resolve().parents[1] / "apps/web/static/app.js").read_text(encoding="utf-8")
    payload = source.split("function formHarmonizationPayload()", 1)[1].split("function formScanPayload", 1)[0]
    assert "duration_minutes" not in payload
    assert "solfeggio_base" not in payload
    assert "pulseSeconds + pauseSeconds" not in payload
    assert "report_id:" in payload
    assert "workbench_mode:" in payload
    solfeggio = source.split("function wireSolfeggioChoiceCards", 1)[1].split("/* ── Bootstrap", 1)[0]
    assert 'target_frequency' in solfeggio
