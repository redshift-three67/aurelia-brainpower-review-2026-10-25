from __future__ import annotations

import json

from core.realtime.event_log import RealtimeEventLog


def test_event_log_appends_jsonl_events_with_sequence(tmp_path) -> None:
    log = RealtimeEventLog(tmp_path)

    first = log.append("harm_test", "job_started", {"frequency": 432.0})
    second = log.append("harm_test", "cycle_metrics", {"cycle": 1})

    assert first["sequence"] == 1
    assert second["sequence"] == 2

    lines = (tmp_path / "harm_test.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["event_type"] == "job_started"
    assert json.loads(lines[1])["payload"] == {"cycle": 1}


def test_event_log_best_effort_helper_does_not_raise_for_nested_root(tmp_path) -> None:
    log = RealtimeEventLog(tmp_path / "missing-parent" / "events")

    event = log.append_best_effort("harm_test", "cycle_metrics", {"cycle": 1})

    assert event is not None


def test_event_log_best_effort_returns_none_when_root_is_file(tmp_path) -> None:
    root_file = tmp_path / "events"
    root_file.write_text("not a directory", encoding="utf-8")
    log = RealtimeEventLog(root_file)

    event = log.append_best_effort("harm_test", "cycle_metrics", {"cycle": 1})

    assert event is None
