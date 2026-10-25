"""Tests: Broadcast-Manager (Queue, Resonanzwahrscheinlichkeit, Stop)."""

import time

from radiworks.core.broadcast import (
    MAX_ACTIVE,
    RESONANCE_BASE,
    TICK_SECONDS,
    BroadcastElement,
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


def test_stop_all_clears_active():
    manager, collector = _manager()
    manager.enqueue("A", seconds=3600)
    manager.enqueue("B", seconds=3600)
    manager._promote_from_queue()
    manager.stop_all()
    manager._stop_all_elements()
    assert manager.queue_state()["active"] == []
    stopped = [e for _, e in collector.events if e.get("stopped")]
    assert len(stopped) == 2


def test_element_progress():
    element = BroadcastElement(signature="S", seconds=1)
    time.sleep(TICK_SECONDS * 2)
    assert 0.0 <= element.progress < 1.0
