from pathlib import Path

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
