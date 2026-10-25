"""Fake-clock regression for periodic progress events in the real worker loop."""

import pytest

from radiworks.core import broadcast as broadcast_module
from radiworks.core.broadcast import BroadcastElement, BroadcastManager, PROGRESS_EVENT_EVERY_S, TICK_SECONDS
from radiworks.entropy import EntropyProvider


@pytest.mark.parametrize("active_count", [1, 3])
def test_worker_emits_bounded_progress_for_each_active_entry(monkeypatch, active_count):
    class FakeClock:
        def __init__(self):
            self.now = 1_000.0
            self.sleeps = 0
            self.manager = None

        def monotonic(self):
            return self.now

        def sleep(self, seconds):
            assert seconds == TICK_SECONDS
            self.now += seconds
            self.sleeps += 1
            if self.sleeps == 14:
                self.manager._running = False

    clock = FakeClock()
    events = []
    manager = BroadcastManager(
        entropy=EntropyProvider(seed=1),
        emit=lambda event_type, payload: events.append(
            (event_type, payload, clock.now)
        ),
    )
    clock.manager = manager
    manager._resonance_draw = lambda _element: None
    monkeypatch.setattr(broadcast_module, "time", clock)
    manager._queue.extend(
        BroadcastElement(signature=f"SYNTHETIC {index}", seconds=60)
        for index in range(active_count)
    )
    manager._running = True

    manager._loop()

    progress_by_id = {
        element.broadcast_id: []
        for element in manager._active
    }
    for event_type, payload, emitted_at in events:
        if event_type == "broadcast.progress" and not payload.get("started"):
            progress_by_id.setdefault(payload["broadcastId"], []).append(emitted_at)

    assert len(progress_by_id) == active_count
    for emitted_times in progress_by_id.values():
        assert 3 <= len(emitted_times) <= 5
        assert all(
            later - earlier <= PROGRESS_EVENT_EVERY_S + TICK_SECONDS + 1e-9
            for earlier, later in zip(emitted_times, emitted_times[1:])
        )
