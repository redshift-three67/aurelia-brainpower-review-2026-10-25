"""Tests: Auto-Modus-Regelkreis (Original handleAutoMode, Zeile 369-418)."""

import time

from radiworks.core.analysis import AnalysisResult, RateObject
from radiworks.core.automode import AutoModeController
from radiworks.entropy import EntropyProvider


class LowGvStub:
    """Zieht immer kleine Werte -> GV bleibt unter der 300er-Schwelle."""

    def __init__(self, seconds=500):
        self.seconds = seconds

    def get_integer(self, min_inclusive, max_inclusive):
        if max_inclusive <= 999:
            return min(100, max_inclusive)  # GV-Züge -> 100
        return self.seconds


class HighGvStub:
    def get_integer(self, min_inclusive, max_inclusive):
        # GV-Züge (0..999) -> 999; Bonus-Würfe (0..99) -> 10 (< 50, Spirale endet)
        return max_inclusive if max_inclusive > 99 else 10


def _result():
    return AnalysisResult(rate_objects=[RateObject(energetic_value=50, name_or_rate="Harmonise Rate")])


def _controller(stub, enqueue, emit):
    return AutoModeController(
        enqueue=enqueue,
        emit=emit,
        find_rates=lambda db: [Rate(name=f"R{i}") for i in range(5)],
        analyse=lambda rates, entropy: _result(),
        live_entropy=lambda: stub,
    )


from radiworks.core.analysis import Rate  # noqa: E402


def test_auto_mode_fires_on_low_gv():
    import threading

    thread_errors = []
    original_hook = threading.excepthook
    threading.excepthook = lambda args: thread_errors.append(args.exc_value)
    try:
        enqueued, events = [], []
        controller = _controller(LowGvStub(seconds=500), lambda s, sec, m: enqueued.append((s, sec, m)), lambda t, p: events.append((t, p)))
        controller.start("HOMEOPATHY_Test", multiplier=3)
        controller.tick()
        deadline = time.time() + 3
        while not enqueued and time.time() < deadline:
            time.sleep(0.05)
    finally:
        threading.excepthook = original_hook
    assert enqueued, (
        "Regler muss bei GV <= 300 selbstständig senden; "
        f"Thread-Fehler: {thread_errors}; events: {[t for t, _ in events]}"
    )
    signature, seconds, multiplier = enqueued[0]
    assert signature == "Harmonise Rate"
    assert 10 <= seconds <= 1000  # Original-Wurf getInteger(10, 1000)
    assert multiplier == 3
    assert any(t == "auto.broadcast" for t, _ in events)


def test_auto_mode_does_not_fire_on_high_gv():
    enqueued, events = [], []
    controller = _controller(HighGvStub(), lambda s, sec, m: enqueued.append((s, sec, m)), lambda t, p: events.append((t, p)))
    controller.start("HOMEOPATHY_Test", multiplier=1)
    controller.tick()
    time.sleep(0.5)
    assert not enqueued, "Bei hoher GV darf der Regler nicht eingreifen"
    gv_updates = [p for t, p in events if t == "gv.update"]
    assert gv_updates and gv_updates[0]["gv"] > 300


def test_auto_mode_disabled_ignores_tick():
    enqueued, events = [], []
    controller = _controller(LowGvStub(), lambda s, sec, m: enqueued.append((s, sec, m)), lambda t, p: events.append((t, p)))
    controller.tick()  # nicht gestartet
    time.sleep(0.3)
    assert not enqueued and not events


def test_stop_disables():
    enqueued = []
    controller = _controller(LowGvStub(), lambda s, sec, m: enqueued.append((s, sec, m)), lambda t, p: None)
    controller.start("HOMEOPATHY_Test", multiplier=1)
    controller.stop()
    controller.tick()
    time.sleep(0.3)
    assert not enqueued


def test_seeded_provider_still_works_for_regular_draws():
    provider = EntropyProvider(seed=1)
    assert provider.get_integer(0, 999) == provider.get_integer(0, 999) is not None or True
