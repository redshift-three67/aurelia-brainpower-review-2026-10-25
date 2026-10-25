from __future__ import annotations

from pathlib import Path

import json
import subprocess
import pytest

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


def test_top3_consolidation_uses_only_validated_record_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = "authority-profile"
    exact_json = tmp_path / "exports" / "client-a" / "exact.json"
    exact_html = tmp_path / "exports" / "client-a" / "exact.html"
    foreign_json = tmp_path / "exports" / "client-b" / "foreign.json"
    for path, content in [
        (exact_json, "{}"),
        (exact_html, "<html></html>"),
        (foreign_json, "{}"),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    monkeypatch.setattr(
        scan,
        "get_top_n_analysis_profiles_by_level",
        lambda _level: [(profile, "Authority profile")],
    )
    monkeypatch.setattr(scan, "_run_topn_report_tool", lambda *_args: False)
    captured_json_files: list[Path] = []
    from tools import remedy_reporter, synergy_consolidator

    def capture_json_files(json_files, *_args, **_kwargs):
        captured_json_files.extend(json_files)
        return False

    monkeypatch.setattr(synergy_consolidator, "consolidate_synergies", capture_json_files)
    monkeypatch.setattr(
        remedy_reporter,
        "consolidate_remedy_synergies",
        lambda *_args, **_kwargs: False,
    )

    def fake_run(command, **_kwargs):
        selected_profile = command[command.index("--profile") + 1]
        if "--export" not in command:
            score_count = int(command[command.index("--top-k") + 1])
            payload = {
                "version": 1,
                "profile": selected_profile,
                "scores": [score_count - index for index in range(score_count)],
            }
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="MORPHIC_SCREENING_RESULT_V1 " + json.dumps(payload) + "\n",
                stderr="",
            )
        session_id = command[command.index("--session-id") + 1]
        payload = {
            "version": 1,
            "profile": selected_profile,
            "session_id": session_id,
            "json_path": str(exact_json.resolve()),
            "html_path": str(exact_html.resolve()),
        }
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="MORPHIC_MULTIPLEX_EXPORT_V1 " + json.dumps(payload) + "\n",
            stderr="",
        )

    monkeypatch.setattr(scan.subprocess, "run", fake_run)
    monkeypatch.setattr(
        scan,
        "_collect_current_session_scan_files",
        lambda *_args: (_ for _ in ()).throw(AssertionError("recursive collector used")),
    )

    scan.top3_scan.__wrapped__(
        name="ClientA",
        first_name="Test",
        birth_date="01011990",
        birth_place="Berlin",
        export_path=str(tmp_path / "exports"),
        focus="",
        k_total=16,
        top_k=5,
        hardware_profile="windows",
        quick_scan=True,
        synergy=False,
        synergy_combos=4,
        synergy_threshold=6.0,
        top_n=1,
        profile_level=3,
        profile_template="phase1-default",
        entropy_mode="legacy",
        image_path="",
        planet_type="",
        adaptive_limits=False,
    )

    assert captured_json_files == [exact_json.resolve()]
    assert foreign_json not in captured_json_files
