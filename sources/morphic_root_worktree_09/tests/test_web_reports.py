import json
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

import apps.web.reports as reports_module
from apps.web.reports import ReportCatalog


def test_report_catalog_groups_phase1_roots_by_client_and_session(
    tmp_path: Path,
) -> None:
    roots = [tmp_path / f"root_{index}" for index in range(5)]
    for root in roots:
        root.mkdir(parents=True)

    client_dir = roots[0] / "Mustermann_Klaus_09041966_Augsburg"
    client_dir.mkdir(parents=True)
    (client_dir / "20260115_101530_multiplex_scan.html").write_text(
        "<html><body><script>alert(1)</script><h1>HTML Bericht</h1></body></html>",
        encoding="utf-8",
    )
    (
        roots[1]
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260115_101530_multiplex_scan.json"
    ).parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    (
        roots[1]
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260115_101530_multiplex_scan.json"
    ).write_text('{"score": 7, "focus": "Bronchien"}', encoding="utf-8")
    (
        roots[2]
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260115_101530_multiplex_scan.txt"
    ).parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    (
        roots[2]
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260115_101530_multiplex_scan.txt"
    ).write_text("Text Bericht", encoding="utf-8")
    (
        roots[3]
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260116_091500_trend_report.pdf"
    ).parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    (
        roots[3]
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260116_091500_trend_report.pdf"
    ).write_bytes(b"%PDF-1.4\n% report\n")
    legacy_dir = roots[4] / "Beispiel_Anna_01011980_Berlin"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "legacy_notes.txt").write_text("Altbestand", encoding="utf-8")

    catalog = ReportCatalog(roots)

    payload = catalog.list(include_all_formats=True)

    assert payload["count"] == 5
    assert payload["client_count"] == 2
    assert payload["root_count"] == 5

    clients = {client["client_id"]: client for client in payload["clients"]}
    assert "Mustermann_Klaus_09041966_Augsburg" in clients

    sessions = {
        session["session_id"]: session
        for session in clients["Mustermann_Klaus_09041966_Augsburg"]["sessions"]
    }
    assert "20260115_101530" in sessions
    assert "20260116_091500" in sessions
    assert {item["kind"] for item in sessions["20260115_101530"]["files"]} == {
        "HTML",
        "JSON",
        "TXT",
    }
    assert sessions["20260116_091500"]["files"][0]["kind"] == "PDF"


def test_report_catalog_builds_inline_and_file_previews(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    client_dir = report_root / "Mustermann_Klaus_09041966_Augsburg"
    client_dir.mkdir(parents=True)
    html_file = client_dir / "20260115_101530_multiplex_scan.html"
    json_file = client_dir / "20260115_101530_multiplex_scan.json"
    txt_file = client_dir / "20260115_101530_multiplex_scan.txt"
    pdf_file = client_dir / "20260115_101530_multiplex_scan.pdf"

    html_file.write_text(
        "<html><body><script>alert(1)</script><h1>HTML Bericht</h1></body></html>",
        encoding="utf-8",
    )
    json_file.write_text('{"score": 7, "focus": "Bronchien"}', encoding="utf-8")
    txt_file.write_text("Zeile 1\nZeile 2", encoding="utf-8")
    pdf_file.write_bytes(b"%PDF-1.4\n% report\n")

    catalog = ReportCatalog([report_root])

    listing = catalog.list(include_all_formats=True)
    files = listing["clients"][0]["sessions"][0]["files"]
    by_kind = {entry["kind"]: entry for entry in files}

    html_preview = catalog.preview(by_kind["HTML"]["id"])
    json_preview = catalog.preview(by_kind["JSON"]["id"])
    txt_preview = catalog.preview(by_kind["TXT"]["id"])
    pdf_preview = catalog.preview(by_kind["PDF"]["id"])

    assert html_preview["mode"] == "html"
    assert "<h1>HTML Bericht</h1>" in html_preview["content"]
    assert "<script" not in html_preview["content"]

    assert json_preview["mode"] == "text"
    assert '  "focus": "Bronchien"' in json_preview["content"]
    assert json_preview["content_type"] == "application/json"

    assert txt_preview["mode"] == "text"
    assert "Zeile 1" in txt_preview["content"]
    assert txt_preview["content_type"] == "text/plain"

    assert pdf_preview["mode"] == "file"
    assert pdf_preview["content"] is None
    assert pdf_preview["file_name"] == pdf_file.name


def test_html_preview_strips_scripts_handlers_and_javascript_urls(
    tmp_path: Path,
) -> None:
    report_root = tmp_path / "reports"
    client_dir = report_root / "Mustermann_Klaus_09041966_Augsburg"
    client_dir.mkdir(parents=True)
    html_file = client_dir / "bericht.html"
    html_file.write_text(
        '<html><body><script>alert(1)</script><a href="javascript:alert(2)" onclick="evil()">Link</a><img src="x" onerror="boom()"><div>OK</div></body></html>',
        encoding="utf-8",
    )

    catalog = ReportCatalog([report_root])
    listing = catalog.list()
    report_id = listing["clients"][0]["sessions"][0]["files"][0]["id"]
    preview = catalog.preview(report_id)

    assert preview["mode"] == "html"
    assert "<script" not in preview["content"]
    assert "onclick" not in preview["content"]
    assert "onerror" not in preview["content"]
    assert "javascript:" not in preview["content"].lower()
    assert "@import" not in preview["content"].lower()
    assert "alert(1)" not in preview["content"]
    assert "alert(2)" not in preview["content"]
    assert "evil()" not in preview["content"]
    assert "boom()" not in preview["content"]
    assert "<div>OK</div>" in preview["content"]


def test_html_preview_shell_does_not_nest_document_wrappers(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    client_dir = report_root / "Synthetic_Client"
    client_dir.mkdir(parents=True)
    report = client_dir / "bericht.html"
    report.write_text(
        "<!doctype html><html lang='de'><head><title>Intern</title></head>"
        "<body><h1>Bericht</h1><p>Inhalt</p></body></html>",
        encoding="utf-8",
    )

    catalog = ReportCatalog([report_root])
    report_id = catalog.list()["clients"][0]["sessions"][0]["files"][0]["id"]
    content = catalog.preview(report_id)["content"]

    assert content.lower().count("<html") == 1
    assert content.lower().count("<head") == 1
    assert content.lower().count("<body") == 1
    assert "<h1>Bericht</h1>" in content
    assert "Intern" not in content


def test_report_catalog_filters_legacy_misplaced_client_suffix_folders(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "Benutzer_Archive_Start"
    good = (
        archive_root
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260630_200536_TOP3_SESSION"
    )
    legacy = (
        archive_root
        / "Mustermann_Klaus_09041966_Augsburg_Synergy"
        / "20260630_200536_synergy_report"
    )
    good.mkdir(parents=True)
    legacy.mkdir(parents=True)
    (good / "a.html").write_text("<html>ok</html>", encoding="utf-8")
    (legacy / "b.html").write_text("<html>legacy</html>", encoding="utf-8")

    catalog = ReportCatalog([archive_root])
    payload = catalog.list(include_all_formats=True)

    assert payload["count"] == 1
    assert payload["clients"][0]["client_id"] == "Mustermann_Klaus_09041966_Augsburg"


def test_report_catalog_refreshes_when_existing_file_changes(tmp_path: Path) -> None:
    root = (
        tmp_path
        / "Benutzer_Archive_Start"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20260630_210612_TOP3_SESSION"
    )
    root.mkdir(parents=True)
    report = root / "bericht.html"
    report.write_text("<html>v1</html>", encoding="utf-8")

    catalog = ReportCatalog([tmp_path / "Benutzer_Archive_Start"])
    first = catalog.list(include_all_formats=True)
    first_entry = first["clients"][0]["sessions"][0]["files"][0]
    first_modified = first_entry["modified_at"]

    import time

    time.sleep(0.01)
    report.write_text("<html>v2 with more content</html>", encoding="utf-8")

    second = catalog.list(include_all_formats=True)
    second_entry = second["clients"][0]["sessions"][0]["files"][0]

    assert second_entry["modified_at"] != first_modified
    assert second_entry["size"] > first_entry["size"]


def test_report_catalog_strips_trailing_session_stamps_from_display_titles(
    tmp_path: Path,
) -> None:
    report_root = tmp_path / "reports"
    client_dir = report_root / "Mustermann_Klaus_09041966_Augsburg"
    client_dir.mkdir(parents=True)
    report_file = client_dir / "trendanalyse_20260115_101530.html"
    report_file.write_text("<html>Trend</html>", encoding="utf-8")

    catalog = ReportCatalog([report_root])

    payload = catalog.list(client_view=True)

    assert payload["count"] == 1
    assert payload["reports"][0]["label"] == "Trendanalyse"


def test_equal_relative_report_paths_in_different_roots_have_distinct_ids_and_content(
    tmp_path: Path,
) -> None:
    roots = [tmp_path / "first" / "Reports", tmp_path / "second" / "reports"]
    relative = Path("Same_Client") / "Same_Session" / "report.txt"
    for root, content in zip(roots, ("first-root", "second-root"), strict=True):
        report = root / relative
        report.parent.mkdir(parents=True)
        report.write_text(content, encoding="utf-8")
    catalog = ReportCatalog(roots)

    listing = catalog.list(include_all_formats=True)
    entries = listing["reports"]

    assert len(entries) == 2
    assert entries[0]["id"] != entries[1]["id"]
    previews = {catalog.preview(str(entry["id"]))["content"] for entry in entries}
    assert previews == {"first-root", "second-root"}


def test_catalog_id_does_not_casefold_distinct_canonical_root_identities() -> None:
    components = ("client", "session", "report.txt")

    upper = reports_module._catalog_report_id(
        r"C:\Private\Reports",
        101,
        202,
        components,
    )
    lower = reports_module._catalog_report_id(
        r"c:\private\reports",
        101,
        202,
        components,
    )

    assert upper != lower


def test_report_catalog_payload_never_contains_absolute_root_paths(tmp_path: Path) -> None:
    private_root = tmp_path / "private-root-marker" / "reports"
    report = private_root / "Client" / "report.txt"
    report.parent.mkdir(parents=True)
    report.write_text("safe", encoding="utf-8")

    payload = ReportCatalog([private_root]).list(include_all_formats=True)
    serialized = json.dumps(payload, ensure_ascii=False)

    assert str(private_root) not in serialized
    assert str(tmp_path) not in serialized


def test_catalog_refresh_replaces_id_map_without_old_id_fallback(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    old_report = root / "Client" / "old.txt"
    old_report.parent.mkdir(parents=True)
    old_report.write_text("old", encoding="utf-8")
    catalog = ReportCatalog([root])
    old_id = str(catalog.list()["reports"][0]["id"])
    old_report.unlink()
    (old_report.parent / "new.txt").write_text("new", encoding="utf-8")

    refreshed = catalog.list(include_all_formats=True)

    assert refreshed["count"] == 1
    assert refreshed["reports"][0]["id"] != old_id
    with pytest.raises(KeyError):
        catalog.preview(old_id)


def test_preview_reads_one_verified_handle_once_with_fstat_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "reports"
    report = root / "Client" / "report.txt"
    report.parent.mkdir(parents=True)
    report.write_text("catalog bytes", encoding="utf-8")
    catalog = ReportCatalog([root])
    report_id = str(catalog.list()["reports"][0]["id"])
    content = "handle bytes".encode("utf-8")

    class FakeHandle:
        def __init__(self) -> None:
            self.stat = SimpleNamespace(
                st_mode=stat.S_IFREG | 0o600,
                st_size=len(content),
                st_mtime=1_700_000_000.0,
                st_mtime_ns=1_700_000_000_000_000_000,
            )
            self.read_calls: list[int] = []
            self.close_calls = 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback) -> None:
            self.close()

        def read(self, size: int = -1) -> bytes:
            self.read_calls.append(size)
            return content

        def close(self) -> None:
            self.close_calls += 1

    handle = FakeHandle()
    open_calls: list[tuple[object, ...]] = []

    def fake_open(*args, **kwargs):
        open_calls.append((*args, kwargs))
        return handle

    monkeypatch.setattr(reports_module, "open_report_handle", fake_open)

    preview = catalog.preview(report_id)

    assert len(open_calls) == 1
    assert handle.read_calls == [reports_module.MAX_PREVIEW_BYTES]
    assert handle.close_calls == 1
    assert preview["content"] == "handle bytes"
    assert preview["size"] == len(content)
    assert preview["modified_at"] == "2023-11-14T22:13:20+00:00"


def test_replaced_final_file_after_cataloging_uses_current_safe_open(tmp_path: Path) -> None:
    root = tmp_path / "reports"
    report = root / "Client" / "report.txt"
    report.parent.mkdir(parents=True)
    report.write_text("cataloged", encoding="utf-8")
    catalog = ReportCatalog([root])
    report_id = str(catalog.list()["reports"][0]["id"])
    replacement = report.with_name("replacement.txt")
    replacement.write_text("replacement", encoding="utf-8")
    report.unlink()
    replacement.replace(report)

    preview = catalog.preview(report_id)

    assert preview["content"] == "replacement"
    assert preview["size"] == len(b"replacement")


@pytest.mark.parametrize(
    "operation",
    ["open_report", "validate", "preview", "open_download"],
)
def test_catalog_closes_safe_handle_once_when_metadata_building_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    root = tmp_path / "reports"
    report = root / "Client" / "report.txt"
    report.parent.mkdir(parents=True)
    report.write_text("content", encoding="utf-8")
    catalog = ReportCatalog([root])
    report_id = str(catalog.list()["reports"][0]["id"])

    class MetadataFailureHandle:
        def __init__(self) -> None:
            self.stat = SimpleNamespace(
                st_mode=stat.S_IFREG | 0o600,
                st_size=7,
                st_mtime=float("inf"),
            )
            self.close_calls = 0

        def close(self) -> None:
            self.close_calls += 1

    handle = MetadataFailureHandle()
    open_calls: list[str] = []

    def fake_open(*args, **kwargs):
        open_calls.append("open")
        return handle

    monkeypatch.setattr(reports_module, "open_report_handle", fake_open)

    with pytest.raises((OSError, OverflowError, ValueError)):
        getattr(catalog, operation)(report_id)

    assert open_calls == ["open"]
    assert handle.close_calls == 1
