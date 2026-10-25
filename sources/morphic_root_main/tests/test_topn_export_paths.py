import re
from pathlib import Path

from apps.cli.commands.helpers.utility_helpers import _resolve_export_paths


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
    )

    expected_dir = (
        tmp_path.resolve()
        / "Resonanz"
        / "Mustermann_Klaus_09041966_Augsburg"
        / "20251222_210515_TOP9_SESSION"
        / "09_knochen_detailliert"
    )
    assert json_path == expected_dir / "20251222_210515_09_knochen_detailliert_top9_multiplex_scan.json"
    assert html_path == expected_dir / "20251222_210515_09_knochen_detailliert_top9_multiplex_scan.html"


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
        r'session_id\s*,?\s*'
        r'\)'
    )
    assert call_pattern.search(source), (
        "field.py muss _resolve_export_paths(export, client_info, "
        '"multiplex_scan", filename_suffix, scan_type, session_id) '
        "fuer den Top-N-Archivpfad aufrufen."
    )
