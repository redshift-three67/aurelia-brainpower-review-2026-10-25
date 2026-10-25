from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading
import time

import pytest

from apps.web.main import create_app
from apps.web.reports import ReportCatalog
from tests.test_web_shell import request


def test_report_catalog_client_view_shows_only_html_with_grouping(
    tmp_path: Path,
) -> None:
    report_root = tmp_path / "reports"
    session_dir = (
        report_root
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260115_101530_TOP3_SESSION"
    )
    session_dir.mkdir(parents=True)
    (session_dir / "20260115_101530_multiplex_scan.html").write_text(
        "<html><body>HTML Bericht</body></html>",
        encoding="utf-8",
    )
    (session_dir / "20260115_101530_multiplex_scan.json").write_text(
        '{"focus": "Bronchien"}',
        encoding="utf-8",
    )
    (session_dir / "20260115_101530_multiplex_scan.txt").write_text(
        "Text Bericht",
        encoding="utf-8",
    )
    (session_dir / "20260115_101530_multiplex_scan.pdf").write_bytes(b"%PDF-1.4\n")

    catalog = ReportCatalog([report_root])

    payload = catalog.list(client_view=True)

    assert payload["count"] == 1
    assert payload["client_count"] == 1
    assert payload["clients"][0]["client_id"] == "Mustermann_Klaus_09041966_Augsburg"
    assert payload["clients"][0]["label"] == "Mustermann Klaus 09041966 Augsburg"
    assert payload["clients"][0]["session_count"] == 1
    assert payload["clients"][0]["file_count"] == 1

    session = payload["clients"][0]["sessions"][0]
    assert session["session_id"] == "20260115_101530_TOP3_SESSION"
    assert session["label"] == "2026-01-15 10:15:30"

    report = session["files"][0]
    assert report["kind"] == "HTML"
    assert report["file_name"] == "20260115_101530_multiplex_scan.html"
    assert report["label"] == "Multiplex Scan"


def test_reports_api_returns_all_supported_formats(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    client_dir = report_root / "Mustermann_Klaus_09041966_Augsburg"
    client_dir.mkdir(parents=True)
    (client_dir / "20260115_101530_multiplex_scan.html").write_text(
        "<html><body>Bericht</body></html>",
        encoding="utf-8",
    )
    (client_dir / "20260115_101530_multiplex_scan.json").write_text(
        '{"focus": "Bronchien"}',
        encoding="utf-8",
    )

    app = create_app(runtime_dir=tmp_path / "runtime", report_roots=[report_root])

    response = request(app, "GET", "/api/reports")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    session = payload["clients"][0]["sessions"][0]
    assert {entry["kind"] for entry in session["files"]} == {"HTML", "JSON"}


def test_report_catalog_parallel_cache_miss_is_single_flight(tmp_path: Path, monkeypatch) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "report.html").write_text("<p>ok</p>", encoding="utf-8")
    catalog = ReportCatalog([report_root], cache_ttl_seconds=30)
    original = catalog._entries_locked
    calls = 0
    active = 0
    maximum_active = 0
    counter_lock = threading.Lock()

    def observed_entries():
        nonlocal calls, active, maximum_active
        with counter_lock:
            calls += 1
            active += 1
            maximum_active = max(maximum_active, active)
        time.sleep(0.05)
        try:
            return original()
        finally:
            with counter_lock:
                active -= 1

    monkeypatch.setattr(catalog, "_entries_locked", observed_entries)
    with ThreadPoolExecutor(max_workers=8) as pool:
        payloads = list(pool.map(lambda _: catalog.list(), range(8)))

    assert calls == 1
    assert maximum_active == 1
    assert {payload["count"] for payload in payloads} == {1}


def test_report_catalog_cache_error_releases_waiters(tmp_path: Path, monkeypatch) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "report.html").write_text("<p>ok</p>", encoding="utf-8")
    catalog = ReportCatalog([report_root], cache_ttl_seconds=30)
    original = catalog._entries_locked
    calls = 0

    def fail_once():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("simulated catalog failure")
        return original()

    monkeypatch.setattr(catalog, "_entries_locked", fail_once)

    with pytest.raises(OSError, match="catalog failure"):
        catalog.list()
    assert catalog.list()["count"] == 1
    assert calls == 2


def test_report_catalog_ttl_expiry_invalidates_cached_population(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "first.html").write_text("<p>one</p>", encoding="utf-8")
    catalog = ReportCatalog([report_root], cache_ttl_seconds=0.05)

    assert catalog.list()["count"] == 1
    (report_root / "second.html").write_text("<p>two</p>", encoding="utf-8")
    assert catalog.list()["count"] == 1
    time.sleep(0.07)
    assert catalog.list()["count"] == 2
