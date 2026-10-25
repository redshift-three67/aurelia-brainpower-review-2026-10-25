import re
from pathlib import Path

from apps.cli.commands.helpers.utility_helpers import _resolve_export_paths
from apps.web.reports import ReportCatalog


CLIENT = {
    "name": "Mustermann",
    "first_name": "Klaus",
    "birth_date": "09041966",
    "birth_place": "Augsburg",
}


def test_topn_session_export_path_matches_legacy_archive_shape(tmp_path: Path) -> None:
    json_path, html_path = _resolve_export_paths(
        tmp_path,
        CLIENT,
        "multiplex_scan",
        filename_suffix="20251222_210515_09_knochen_detailliert_top9",
        scan_type="top9_session",
        session_id="20251222_210515",
        tenant_id="ws-legacy",
    )

    expected_dir = (
        Path(f"{tmp_path.resolve()}__ws-legacy")
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP9_SESSION"
        / "09_knochen_detailliert"
    )
    assert json_path == expected_dir / "20251222_210515_09_knochen_detailliert_top9_multiplex_scan.json"
    assert html_path == expected_dir / "20251222_210515_09_knochen_detailliert_top9_multiplex_scan.html"


def test_topn_export_path_catalog_session_matches_parent_marker_contract(
    tmp_path: Path,
) -> None:
    raw_session_id = "20251222_210515"
    emitted_session_id = f"{raw_session_id}_TOP9_SESSION"
    export_root = tmp_path / "exports"
    json_path, html_path = _resolve_export_paths(
        export_root,
        CLIENT,
        "multiplex_scan",
        filename_suffix="20251222_210515_09_knochen_detailliert_top9",
        scan_type="top9_session",
        session_id=raw_session_id,
    )
    json_path.write_text("{}", encoding="utf-8")
    html_path.write_text("<html></html>", encoding="utf-8")

    catalog = ReportCatalog([export_root]).list(include_all_formats=True)
    exposed_session_ids = {
        session["session_id"]
        for client in catalog["clients"]
        for session in client["sessions"]
    }

    assert exposed_session_ids == {emitted_session_id}


def test_topn_session_folder_formatter_is_shared_by_export_and_parent_marker() -> None:
    helper_source = Path(
        "apps/cli/commands/helpers/utility_helpers.py"
    ).read_text(encoding="utf-8")
    scan_source = Path("apps/cli/commands/scan.py").read_text(encoding="utf-8")

    assert "def _topn_session_folder_id(" in helper_source
    assert "_topn_session_folder_id(session_id, top_n)" in helper_source
    assert "_topn_session_folder_id(session_timestamp, top_n)" in scan_source


def test_resolve_export_paths_isolates_by_tenant_id(tmp_path: Path) -> None:
    json_path_a, _ = _resolve_export_paths(
        tmp_path, CLIENT, "field_test", tenant_id="ws-tenant-a"
    )
    json_path_b, _ = _resolve_export_paths(
        tmp_path, CLIENT, "field_test", tenant_id="ws-tenant-b"
    )

    assert json_path_a != json_path_b
    assert "ws-tenant-a" in str(json_path_a)
    assert "ws-tenant-b" in str(json_path_b)


def test_resolve_export_paths_ignores_tenant_id_for_explicit_file_path(
    tmp_path: Path,
) -> None:
    explicit = tmp_path / "custom_export.json"

    json_path, _ = _resolve_export_paths(
        explicit, CLIENT, "field_test", tenant_id="ws-tenant-a"
    )

    assert json_path == explicit.resolve()
    assert "ws-tenant-a" not in str(json_path)


def test_field_multiplex_scan_passes_topn_archive_arguments() -> None:
    source = Path("apps/cli/commands/field.py").read_text(encoding="utf-8")

    # Der Aufruf darf ueber mehrere Zeilen formatiert sein (z.B. durch einen
    # Formatter), die Argument-Reihenfolge muss aber erhalten bleiben.
    call_pattern = re.compile(
        r'_resolve_export_paths\(\s*'
        r'export\s*,\s*'
        r'client_info\s*,\s*'
        r'"multiplex_scan"\s*,\s*'
        r'filename_suffix\s*,\s*'
        r'scan_type\s*,\s*'
        r'session_id\s*,\s*'
        r'tenant_id\s*=\s*export_tenant_id\s*,?\s*'
        r'\)'
    )
    assert call_pattern.search(source), (
        "field.py muss _resolve_export_paths(export, client_info, "
        '"multiplex_scan", filename_suffix, scan_type, session_id, '
        "tenant_id=export_tenant_id) fuer den Top-N-Archivpfad aufrufen."
    )
