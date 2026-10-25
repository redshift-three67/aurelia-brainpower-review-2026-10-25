from pathlib import Path

from apps.web.contracts import Phase1ScanRequest


ROOT = Path(__file__).resolve().parents[1]
PRODUCTIVE_PYTHON_PATHS = (
    ROOT / "apps" / "web" / "contracts.py",
    ROOT / "apps" / "web" / "launcher.py",
    ROOT / "apps" / "web" / "main.py",
    ROOT / "apps" / "web" / "workbench.py",
)
PRODUCTIVE_STATIC_PATHS = (
    ROOT / "apps" / "web" / "static" / "app.js",
    ROOT / "apps" / "web" / "static" / "workbench-api.js",
)


def test_local_vector_draft_modules_are_not_wired_to_productive_web_paths() -> None:
    for path in (*PRODUCTIVE_PYTHON_PATHS, *PRODUCTIVE_STATIC_PATHS):
        source = path.read_text(encoding="utf-8")
        assert "client_context_contracts" not in source
        assert "local_vector_draft_store" not in source
        assert "LocalVectorDraftStore" not in source


def test_group_geo_draft_fields_remain_outside_scan_contract_and_frontend_payloads() -> None:
    assert {
        "group",
        "geo",
        "group_members",
        "latitude",
        "longitude",
        "radius_meters",
    }.isdisjoint(Phase1ScanRequest.model_fields)

    for path in PRODUCTIVE_STATIC_PATHS:
        source = path.read_text(encoding="utf-8")
        for field_name in ("group_members", "latitude", "longitude", "radius_meters"):
            assert f"{field_name}:" not in source


def test_group_draft_router_cannot_reach_scan_or_analysis_paths() -> None:
    router_source = (ROOT / "apps" / "web" / "group_drafts.py").read_text(
        encoding="utf-8"
    )
    scan_sources = [
        (ROOT / "apps" / "web" / "contracts.py").read_text(encoding="utf-8"),
        (ROOT / "apps" / "web" / "launcher.py").read_text(encoding="utf-8"),
        (ROOT / "apps" / "web" / "scan_jobs.py").read_text(encoding="utf-8"),
        (ROOT / "apps" / "cli" / "commands" / "field.py").read_text(encoding="utf-8"),
    ]

    for forbidden in ("Phase1ScanRequest", "build_phase1_scan_launcher", "AnalysisService"):
        assert forbidden not in router_source
    for source in scan_sources:
        assert "group_drafts" not in source
        assert "build_group_draft_opt_in" not in source
