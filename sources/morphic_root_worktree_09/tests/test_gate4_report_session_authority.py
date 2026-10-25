from __future__ import annotations

import json

import pytest

from apps.web.scan_jobs import (
    _resolved_report_session_id,
    _update_report_session_authority,
)


def _record(session_id: str, *, profile: str = "P1") -> str:
    payload = {
        "version": 1,
        "profile": profile,
        "session_id": session_id,
        "json_path": f"C:/reports/{profile}.json",
        "html_path": f"C:/reports/{profile}.html",
    }
    return "MORPHIC_MULTIPLEX_EXPORT_V1 " + json.dumps(payload)


def test_report_session_authority_accepts_one_consistent_session() -> None:
    ids, invalid = _update_report_session_authority(
        [_record("session-a", profile="P1"), _record("session-a", profile="P2")],
        session_ids=set(),
        invalid=False,
    )

    assert invalid is False
    assert ids == {"session-a"}
    assert _resolved_report_session_id(ids, invalid) == "session-a"


def test_report_session_authority_rejects_conflicting_sessions() -> None:
    ids, invalid = _update_report_session_authority(
        [_record("session-a"), _record("session-b", profile="P2")],
        session_ids=set(),
        invalid=False,
    )

    assert ids == {"session-a", "session-b"}
    assert _resolved_report_session_id(ids, invalid) is None


def test_report_session_authority_retains_only_first_conflict_pair() -> None:
    ids, invalid = _update_report_session_authority(
        [
            _record("session-a"),
            _record("session-b", profile="P2"),
            _record("session-c", profile="P3"),
            _record("session-a", profile="P4"),
        ],
        session_ids=set(),
        invalid=False,
    )

    assert ids == {"session-a", "session-b"}
    assert invalid is False


def test_report_session_authority_still_marks_malformed_records_after_conflict() -> None:
    ids, invalid = _update_report_session_authority(
        [
            _record("session-c", profile="P3"),
            "MORPHIC_MULTIPLEX_EXPORT_V1 {not-json",
        ],
        session_ids={"session-a", "session-b"},
        invalid=False,
    )

    assert ids == {"session-a", "session-b"}
    assert invalid is True


def test_report_session_authority_rejects_any_malformed_prefixed_record() -> None:
    ids, invalid = _update_report_session_authority(
        [_record("session-a"), "MORPHIC_MULTIPLEX_EXPORT_V1 {not-json"],
        session_ids=set(),
        invalid=False,
    )

    assert ids == {"session-a"}
    assert invalid is True
    assert _resolved_report_session_id(ids, invalid) is None


@pytest.mark.parametrize(
    "field",
    ["profile", "session_id", "json_path", "html_path"],
)
def test_report_session_authority_rejects_non_utf8_marker_strings(field: str) -> None:
    payload = {
        "version": 1,
        "profile": "P1",
        "session_id": "session-a",
        "json_path": "C:/reports/P1.json",
        "html_path": "C:/reports/P1.html",
    }
    payload[field] = "\ud800"
    record = "MORPHIC_MULTIPLEX_EXPORT_V1 " + json.dumps(payload)

    ids, invalid = _update_report_session_authority(
        [record],
        session_ids=set(),
        invalid=False,
    )

    assert ids == set()
    assert invalid is True
    assert _resolved_report_session_id(ids, invalid) is None


def test_report_session_authority_ignores_unrelated_output() -> None:
    ids, invalid = _update_report_session_authority(
        ["Analyse gestartet", "Export gespeichert: C:/reports/P1.json"],
        session_ids=set(),
        invalid=False,
    )

    assert ids == set()
    assert invalid is False
    assert _resolved_report_session_id(ids, invalid) is None
