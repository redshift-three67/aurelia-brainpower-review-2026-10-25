from __future__ import annotations

from pathlib import Path

from apps.cli.commands import scan


def _touch_json(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")


def test_collect_current_session_scan_files_excludes_historical_jsons(tmp_path: Path) -> None:
    current_session = "20260628_224628"
    client_dir = tmp_path / "Deisenhofer_Klaus_09041966_Augsburg"

    current_multiplex = (
        client_dir
        / f"{current_session}_TOP7_SESSION"
        / "01_pathogen"
        / f"{current_session}_01_pathogen_top7_multiplex_scan.json"
    )
    current_field = (
        client_dir
        / f"{current_session}_TOP7_SESSION"
        / "02_toxin"
        / f"{current_session}_02_toxin_top7_field_test.json"
    )
    historical_multiplex = (
        client_dir
        / "20251222_210515_TOP9_SESSION"
        / "01_zahn_detailliert"
        / "20251222_210515_01_zahn_detailliert_top9_multiplex_scan.json"
    )
    unrelated_current = (
        tmp_path
        / "Other_Client"
        / f"{current_session}_TOP7_SESSION"
        / "01_pathogen"
        / f"{current_session}_01_pathogen_top7_multiplex_scan.json"
    )

    for path in [current_multiplex, current_field, historical_multiplex, unrelated_current]:
        _touch_json(path)

    files = scan._collect_current_session_scan_files(client_dir, current_session)

    assert files == [current_multiplex, current_field]
