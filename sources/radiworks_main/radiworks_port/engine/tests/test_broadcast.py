"""Tests: Broadcast-Manager (Queue, Resonanzwahrscheinlichkeit, Stop)."""

import threading
import time

import pytest

from radiworks.core import broadcast as broadcast_module
from radiworks.core.broadcast import (
    MAX_ACTIVE,
    RESONANCE_BASE,
    TICK_SECONDS,
    BroadcastElement,
    BroadcastError,
    BroadcastManager,
)
from radiworks.entropy import EntropyProvider


class Collector:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def __call__(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, payload))


def _manager(seed: int = 1):
    collector = Collector()
    manager = BroadcastManager(entropy=EntropyProvider(seed=seed), emit=collector)
    manager._start_thread = lambda: None
    return manager, collector


def test_resonance_probability_threshold():
    """Exakt 1/(6765+multiplier) je Draw (BroadcastElement Zeile 207).

    Aggregiert ueber vier unabhaengige Seeds; Fenster +/- 40 % entspricht
    grob 3 Sigma der Binomialverteilung.
    """
    multiplier = 5
    bound = RESONANCE_BASE + multiplier
    draws_total = 100_000
    hits = 0
    for seed in (101, 202, 303, 404):
        provider = EntropyProvider(seed=seed)
        hits += sum(
            1
            for _ in range(draws_total)
            if provider.get_integer(0, bound - 1) == bound - 1
        )
    expected = draws_total * len((101, 202, 303, 404)) / bound
    assert hits == pytest_approx(expected, 0.40)


def pytest_approx(expected: float, tolerance_relative: float) -> float:
    class _Approx:
        def __eq__(self, other: object) -> bool:
            assert isinstance(other, (int, float))
            return abs(other - expected) <= expected * tolerance_relative

        def __repr__(self) -> str:  # pragma: no cover
            return f"~{expected}"

    return _Approx()  # type: ignore[return-value]


def test_enqueue_and_state(tmp_path=None):
    manager, collector = _manager()
    result = manager.enqueue("TEST SIGNATUR", seconds=1, multiplier=1)
    assert result["queued"] >= 1
    manager._promote_from_queue()
    assert len(manager.queue_state()["active"]) == 1
    assert manager.queue_state()["queued"] == []


def test_enqueue_rejects_unsafe_multiplier_without_queueing():
    manager, _ = _manager()

    with pytest.raises(BroadcastError, match="multiplier"):
        manager.enqueue("SYNTHETIC", seconds=60, multiplier=-6765)

    assert manager.queue_state()["queued"] == []
    assert manager.queue_state()["active"] == []


def test_worker_drops_failed_element_and_continues_queue():
    collector = Collector()
    manager = BroadcastManager(
        entropy=EntropyProvider(seed=1),
        emit=collector,
        keep_alive=lambda: True,
    )
    original_draw = manager._resonance_draw

    def fail_only_bad(element):
        if element.signature == "BAD":
            raise RuntimeError("synthetic resonance failure")
        original_draw(element)

    manager._resonance_draw = fail_only_bad  # type: ignore[method-assign]
    manager.enqueue("BAD", seconds=60)
    manager.enqueue("GOOD", seconds=60)

    deadline = time.monotonic() + 1
    while time.monotonic() < deadline:
        active = manager.queue_state()["active"]
        failed = [
            payload
            for event_type, payload in collector.events
            if event_type == "broadcast.progress" and payload.get("failed")
        ]
        if any(item["signature"] == "GOOD" for item in active) and failed:
            break
        time.sleep(TICK_SECONDS)
    else:
        pytest.fail("valid broadcast was not processed after failed element")

    manager.shutdown(timeout=1)
    failed = [
        payload
        for event_type, payload in collector.events
        if event_type == "broadcast.progress" and payload.get("failed")
    ]
    assert [payload["signature"] for payload in failed] == ["BAD"]
    assert failed[0]["error"] == "RuntimeError"


def test_multi_enqueued_stays_within_limit():
    manager, _ = _manager()
    for i in range(20):
        manager.enqueue(f"RATE {i}", seconds=3600)
    manager._promote_from_queue()
    assert len(manager.queue_state()["active"]) == MAX_ACTIVE
    assert len(manager.queue_state()["queued"]) == 20 - MAX_ACTIVE


def test_resonance_events_emitted_and_counted():
    manager, collector = _manager(seed=1234)
    element = BroadcastElement(signature="SIG", seconds=3600, multiplier=1000)
    manager._active.append(element)
    # 20.000 Draws mit multiplier=1000: Erwartung ~2,6 Resonanzen (deterministisch per Seed)
    for _ in range(20_000):
        manager._resonance_draw(element)
    resonances = [e for t, e in collector.events if t == "broadcast.resonance"]
    assert element.resonance_count == len(resonances)
    totals = manager.queue_state()["resonanceTotals"].get("SIG", 0)
    assert totals == element.resonance_count
    for event in resonances:
        assert set(event["binaural"]) == {"left_freq", "right_freq", "volume"}
        assert event["binaural"]["left_freq"] >= 50
        assert event["binaural"]["right_freq"] > event["binaural"]["left_freq"]


def test_duplicate_signatures_receive_distinct_broadcast_ids():
    manager, collector = _manager()
    first = manager.enqueue("SAME", seconds=3600)
    second = manager.enqueue("SAME", seconds=3600)

    assert first["broadcastId"] != second["broadcastId"]
    assert [item["broadcastId"] for item in manager.queue_state()["queued"]] == [
        first["broadcastId"],
        second["broadcastId"],
    ]

    manager._promote_from_queue()
    starts = [
        payload
        for event_type, payload in collector.events
        if event_type == "broadcast.progress" and payload.get("started")
    ]
    assert [payload["broadcastId"] for payload in starts] == [
        first["broadcastId"],
        second["broadcastId"],
    ]


def test_stop_all_clears_active_and_pending_queue():
    manager, collector = _manager()
    results = [manager.enqueue(f"RATE {index}", seconds=3600) for index in range(10)]
    manager._promote_from_queue()
    assert len(manager.queue_state()["active"]) == MAX_ACTIVE
    assert len(manager.queue_state()["queued"]) == 2

    manager.stop_all()

    assert manager.queue_state()["active"] == []
    assert manager.queue_state()["queued"] == []
    stopped = [
        payload
        for event_type, payload in collector.events
        if event_type == "broadcast.progress" and payload.get("stopped")
    ]
    assert {payload["broadcastId"] for payload in stopped} == {
        result["broadcastId"] for result in results
    }


def test_stop_current_removes_only_first_active_element():
    manager, collector = _manager()
    first = manager.enqueue("A", seconds=3600)
    second = manager.enqueue("B", seconds=3600)
    manager._promote_from_queue()

    manager.stop_current()

    state = manager.queue_state()
    assert [item["broadcastId"] for item in state["active"]] == [second["broadcastId"]]
    stopped = [
        payload
        for event_type, payload in collector.events
        if event_type == "broadcast.progress" and payload.get("stopped")
    ]
    assert [payload["broadcastId"] for payload in stopped] == [first["broadcastId"]]


def test_manager_shutdown_joins_thread():
    collector = Collector()
    manager = BroadcastManager(
        entropy=EntropyProvider(seed=1),
        emit=collector,
        keep_alive=lambda: True,
    )
    manager.ensure_running()
    thread = manager._thread
    assert thread is not None and thread.is_alive()

    manager.shutdown(timeout=1)

    assert not thread.is_alive()
    assert manager.queue_state()["active"] == []
    assert manager.queue_state()["queued"] == []


def test_enqueue_rolls_back_if_thread_cannot_start(monkeypatch):
    collector = Collector()
    manager = BroadcastManager(entropy=EntropyProvider(seed=1), emit=collector)

    def fail_start(_thread):
        raise RuntimeError("cannot start")

    monkeypatch.setattr(broadcast_module.threading.Thread, "start", fail_start)
    with pytest.raises(RuntimeError, match="cannot start"):
        manager.enqueue("GHOST", seconds=60)

    assert manager.queue_state()["queued"] == []
    assert manager.queue_state()["active"] == []
    assert manager._running is False
    assert collector.events == []


def test_stop_all_prevents_late_events_from_blocked_entropy():
    entered = threading.Event()
    release = threading.Event()

    class BlockingEntropy:
        def __init__(self):
            self.calls = 0

        def get_integer(self, min_inclusive, max_inclusive):
            self.calls += 1
            if self.calls == 1:
                entered.set()
                assert release.wait(1)
                return max_inclusive
            return min_inclusive

    collector = Collector()
    manager = BroadcastManager(
        entropy=BlockingEntropy(),  # type: ignore[arg-type]
        emit=collector,
        keep_alive=lambda: True,
    )
    manager.enqueue("BLOCKED", seconds=3600)
    assert entered.wait(1)

    manager.stop_all()
    stopped_index = next(
        index
        for index, (event_type, payload) in enumerate(collector.events)
        if event_type == "broadcast.progress" and payload.get("stopped")
    )
    release.set()
    time.sleep(TICK_SECONDS * 2)
    manager.shutdown(timeout=1)

    assert collector.events[stopped_index + 1:] == []


def test_element_progress():
    element = BroadcastElement(signature="S", seconds=1, start=time.monotonic())
    time.sleep(TICK_SECONDS * 2)
    assert 0.0 < element.progress < 1.0
