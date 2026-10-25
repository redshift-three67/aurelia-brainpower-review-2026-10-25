from __future__ import annotations

import json
import math
from datetime import UTC, datetime
from pathlib import Path

import pytest

from apps.cli.commands import scan


SCREENING_PREFIX = "MORPHIC_SCREENING_RESULT_V1 "
EXPORT_PREFIX = "MORPHIC_MULTIPLEX_EXPORT_V1 "


def _screening_record(
    profile: str = "profile-a",
    scores: list[object] | None = None,
    **updates: object,
) -> str:
    payload: dict[str, object] = {
        "version": 1,
        "profile": profile,
        "scores": scores if scores is not None else [5.0, 4.0, 3.0, 2.0, 1.0],
    }
    payload.update(updates)
    return SCREENING_PREFIX + json.dumps(payload, separators=(",", ":"))


def _export_record(
    json_path: Path,
    html_path: Path,
    *,
    profile: str = "profile-a",
    session_id: str = "run-a",
    **updates: object,
) -> str:
    payload: dict[str, object] = {
        "version": 1,
        "profile": profile,
        "session_id": session_id,
        "json_path": str(json_path),
        "html_path": str(html_path),
    }
    payload.update(updates)
    return EXPORT_PREFIX + json.dumps(payload, separators=(",", ":"))


def test_screening_record_parser_accepts_exact_stdout_contract() -> None:
    stdout = "Client score=999\n" + _screening_record() + "\nFokus score=888\n"

    scores = scan._parse_screening_result_record(
        stdout,
        expected_profile="profile-a",
        expected_score_count=5,
    )

    assert scores == [5.0, 4.0, 3.0, 2.0, 1.0]
    assert all(math.isfinite(score) for score in scores)


@pytest.mark.parametrize(
    "stdout",
    [
        "Client score=9\nFokus score=8\n",
        "Client: " + _screening_record(),
        SCREENING_PREFIX + "not-json",
        _screening_record(profile="wrong"),
        _screening_record(scores=[1, 2, 3, 4]),
        _screening_record(scores=[1, 2, 3, 4, 5, 6]),
        _screening_record(scores=[1, 2, 3, 4, float("nan")]),
        _screening_record(scores=[1, 2, 3, 4, float("inf")]),
        _screening_record(scores=[1, 2, 3, 4, True]),
        _screening_record(version=2),
        _screening_record(extra="forbidden"),
        _screening_record() + "\n" + _screening_record(),
    ],
    ids=[
        "human-score-lines",
        "forged-user-line",
        "malformed-json",
        "wrong-profile",
        "too-few-scores",
        "too-many-scores",
        "nan",
        "infinity",
        "boolean",
        "wrong-version",
        "extra-field",
        "duplicate-record",
    ],
)
def test_screening_record_parser_rejects_forgery_and_malformed_contract(
    stdout: str,
) -> None:
    with pytest.raises(ValueError):
        scan._parse_screening_result_record(
            stdout,
            expected_profile="profile-a",
            expected_score_count=5,
        )


@pytest.mark.parametrize("expected_score_count", [True, False, 0, 6, 4.0, "4", None])
def test_screening_record_parser_rejects_invalid_expected_score_count(
    expected_score_count: object,
) -> None:
    with pytest.raises(ValueError):
        scan._parse_screening_result_record(
            _screening_record(),
            expected_profile="profile-a",
            expected_score_count=expected_score_count,  # type: ignore[arg-type]
        )


def test_screening_record_parser_normalizes_integer_float_overflow() -> None:
    with pytest.raises(ValueError) as captured:
        scan._parse_screening_result_record(
            _screening_record(scores=[10**400, 4, 3, 2, 1]),
            expected_profile="profile-a",
            expected_score_count=5,
        )

    assert "10" * 20 not in str(captured.value)


def test_export_record_parser_accepts_nonempty_unique_artifacts_under_root(
    tmp_path: Path,
) -> None:
    root = tmp_path / "exports"
    json_path = root / "client-a" / "result.json"
    html_path = root / "client-a" / "result.html"
    json_path.parent.mkdir(parents=True)
    json_path.write_text("{}", encoding="utf-8")
    html_path.write_text("<html></html>", encoding="utf-8")

    parsed = scan._parse_multiplex_export_record(
        _export_record(json_path, html_path),
        expected_profile="profile-a",
        expected_session_id="run-a",
        export_root=root,
        used_paths=set(),
    )

    assert parsed == (json_path.resolve(), html_path.resolve())


@pytest.mark.parametrize(
    "case",
    [
        "marker-only",
        "forged-user-line",
        "malformed-json",
        "duplicate-record",
        "wrong-profile",
        "wrong-session",
        "outside-root",
        "missing-json",
        "empty-html",
        "wrong-extension",
        "duplicate-path",
        "wrong-version",
        "extra-field",
    ],
)
def test_export_record_parser_rejects_untrusted_or_invalid_artifacts(
    tmp_path: Path,
    case: str,
) -> None:
    root = tmp_path / "exports"
    root.mkdir()
    json_path = root / "profile-a" / "result.json"
    html_path = root / "profile-a" / "result.html"
    json_path.parent.mkdir()
    json_path.write_text("{}", encoding="utf-8")
    html_path.write_text("<html></html>", encoding="utf-8")
    used_paths: set[Path] = set()
    stdout = _export_record(json_path, html_path)

    if case == "marker-only":
        stdout = "Export gespeichert\nHTML-Report gespeichert\n"
    elif case == "forged-user-line":
        stdout = "Client: " + stdout
    elif case == "malformed-json":
        stdout = EXPORT_PREFIX + "not-json"
    elif case == "duplicate-record":
        stdout = stdout + "\n" + stdout
    elif case == "wrong-profile":
        stdout = _export_record(json_path, html_path, profile="wrong")
    elif case == "wrong-session":
        stdout = _export_record(json_path, html_path, session_id="wrong")
    elif case == "outside-root":
        outside = tmp_path / "foreign.json"
        outside.write_text("{}", encoding="utf-8")
        stdout = _export_record(outside, html_path)
    elif case == "missing-json":
        json_path.unlink()
    elif case == "empty-html":
        html_path.write_text("", encoding="utf-8")
    elif case == "wrong-extension":
        wrong = root / "profile-a" / "result.txt"
        wrong.write_text("{}", encoding="utf-8")
        stdout = _export_record(wrong, html_path)
    elif case == "duplicate-path":
        used_paths.add(json_path.resolve())
    elif case == "wrong-version":
        stdout = _export_record(json_path, html_path, version=2)
    elif case == "extra-field":
        stdout = _export_record(json_path, html_path, extra="forbidden")

    with pytest.raises(ValueError):
        scan._parse_multiplex_export_record(
            stdout,
            expected_profile="profile-a",
            expected_session_id="run-a",
            export_root=root,
            used_paths=used_paths,
        )


@pytest.mark.parametrize(
    "filesystem_error",
    [FileNotFoundError(r"C:\private\exports\vanished.json"), PermissionError(r"C:\private\exports\denied.json")],
    ids=["disappearing", "permission"],
)
def test_export_record_parser_normalizes_artifact_stat_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    filesystem_error: OSError,
) -> None:
    root = tmp_path / "exports"
    json_path = root / "profile-a" / "result.json"
    html_path = root / "profile-a" / "result.html"
    json_path.parent.mkdir(parents=True)
    json_path.write_text("{}", encoding="utf-8")
    html_path.write_text("<html></html>", encoding="utf-8")
    original_is_file = Path.is_file
    original_stat = Path.stat

    def forced_is_file(path: Path) -> bool:
        if path == json_path:
            return True
        return original_is_file(path)

    def failing_stat(path: Path, *args, **kwargs):
        if path == json_path:
            raise filesystem_error
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "is_file", forced_is_file)
    monkeypatch.setattr(Path, "stat", failing_stat)

    with pytest.raises(ValueError) as captured:
        scan._parse_multiplex_export_record(
            _export_record(json_path, html_path),
            expected_profile="profile-a",
            expected_session_id="run-a",
            export_root=root,
            used_paths=set(),
        )

    assert "private" not in str(captured.value).lower()


def test_top3_run_ids_are_collision_resistant_within_same_utc_microsecond(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixed = datetime(2026, 7, 27, 13, 15, 16, 123456, tzinfo=UTC)

    class FixedDatetime:
        @staticmethod
        def now(_timezone):
            return fixed

    monkeypatch.setattr(scan, "datetime", FixedDatetime)

    first = scan._new_top3_session_id()
    second = scan._new_top3_session_id()

    assert first != second
    assert first.startswith("20260727_131516_123456")
    assert second.startswith("20260727_131516_123456")
    assert "Mustermann" not in first + second
