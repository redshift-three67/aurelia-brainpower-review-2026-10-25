"""Tests: Auto-Modus-Regelkreis (Original handleAutoMode, Zeile 369-418)."""

from __future__ import annotations

import threading
from types import SimpleNamespace

import pytest

from radiworks.core import automode as automode_module
from radiworks.core.analysis import AnalysisResult, Rate, RateObject
from radiworks.core.automode import AutoModeController, is_auto_broadcast_candidate


class SequenceEntropy:
    """Liefert pro GV-Prüfung dreimal denselben kontrollierten Wert."""

    def __init__(self, gv_values: list[int], *, seconds: int = 500):
        self._values = iter(gv_values)
        self._gv_draw = 0
        self._current_gv = 0
        self.seconds = seconds

    @property
    def gv_draws(self) -> int:
        return self._gv_draw

    def get_integer(self, min_inclusive: int, max_inclusive: int) -> int:
        bounds = (min_inclusive, max_inclusive)
        if bounds == (0, 999):
            if self._gv_draw % 3 == 0:
                self._current_gv = next(self._values)
            self._gv_draw += 1
            return self._current_gv
        if bounds == (0, 99):
            return 10
        if bounds == (10, 1000):
            return self.seconds
        raise AssertionError(f"Unerwartete Entropiegrenzen: {bounds}")


def _queue_state(*, queued: int = 0, active: int = 0) -> dict:
    return {
        "queued": [{"signature": f"Q{i}"} for i in range(queued)],
        "active": [{"signature": f"A{i}"} for i in range(active)],
        "resonanceTotals": {},
    }


def _controller(
    entropy: SequenceEntropy,
    *,
    enqueue=lambda _signature, _seconds, _multiplier: None,
    emit=lambda _event_type, _payload: None,
    find_rates=lambda _database: [Rate(name="R")],
    analyse=lambda _rates, _entropy: AnalysisResult(),
    queue_state=lambda: _queue_state(),
) -> AutoModeController:
    return AutoModeController(
        enqueue=enqueue,
        emit=emit,
        find_rates=find_rates,
        analyse=analyse,
        live_entropy=lambda: entropy,
        queue_state=queue_state,
    )


def _wait_until(predicate, message: str = "Worker wurde nicht rechtzeitig fertig") -> None:
    pause = threading.Event()
    for _ in range(100):
        if predicate():
            return
        pause.wait(0.01)
    raise AssertionError(message)


def test_disabled_tick_does_not_read_queue_or_entropy():
    queue_calls = []
    entropy = SequenceEntropy([])
    controller = _controller(
        entropy,
        queue_state=lambda: queue_calls.append(True) or _queue_state(),
    )

    controller.tick()

    assert queue_calls == []
    assert controller.snapshot()["runs"] == 0


def test_pending_queue_blocks_but_active_broadcasts_do_not():
    state = {"queued": 1, "active": 0}
    queue_calls = []
    entropy = SequenceEntropy([500])

    def queue_state():
        queue_calls.append((state["queued"], state["active"]))
        return _queue_state(**state)

    controller = _controller(entropy, queue_state=queue_state)
    controller.start("HOMEOPATHY_Test")
    controller.tick()
    assert controller.snapshot()["runs"] == 0

    state.update(queued=0, active=3)
    controller.tick()

    assert controller.snapshot()["runs"] == 1
    assert queue_calls == [(1, 0), (0, 3)]
    assert controller.state._next_analysis_at is not None


@pytest.mark.parametrize("case_gv", [100, 500])
def test_cooldown_is_one_deadline_for_low_and_high_gv(monkeypatch, case_gv):
    clock = [5.0]
    monkeypatch.setattr(
        automode_module,
        "time",
        SimpleNamespace(monotonic=lambda: clock[0]),
    )
    entropy = SequenceEntropy([case_gv, case_gv])
    controller = _controller(entropy, queue_state=lambda: _queue_state(active=2))
    controller.start("HOMEOPATHY_Test")

    controller.tick()
    _wait_until(lambda: not controller.state._analysing)
    assert controller.state._next_analysis_at == pytest.approx(5.444)
    assert controller.snapshot()["runs"] == 1

    clock[0] = 5.443
    controller.tick()
    assert controller.snapshot()["runs"] == 1

    clock[0] = 5.444
    controller.tick()
    _wait_until(lambda: not controller.state._analysing)
    assert controller.snapshot()["runs"] == 2
    assert controller.state._next_analysis_at == pytest.approx(5.888)


def test_start_stop_and_restart_reset_session_state():
    events = []
    entropy = SequenceEntropy([500])
    controller = _controller(
        entropy,
        emit=lambda event_type, payload: events.append((event_type, payload)),
    )

    first = controller.start("HOMEOPATHY_Test", multiplier=3)
    assert first == {
        "enabled": True,
        "database": "HOMEOPATHY_Test",
        "multiplier": 3,
        "caseGv": 0,
        "runs": 0,
        "seriesLength": 0,
        "average": None,
    }
    controller.tick()
    deadline = controller.state._next_analysis_at
    stopped = controller.stop()
    assert stopped["enabled"] is False
    assert stopped["runs"] == 1
    assert stopped["caseGv"] == 500
    assert stopped["seriesLength"] == 0
    assert stopped["average"] == 500
    assert controller.state._next_analysis_at == deadline

    restarted = controller.start("HOMEOPATHY_Other", multiplier=7)
    assert restarted["enabled"] is True
    assert restarted["database"] == "HOMEOPATHY_Other"
    assert restarted["multiplier"] == 7
    assert restarted["caseGv"] == 0
    assert restarted["runs"] == 0
    assert restarted["average"] is None
    assert controller.state._next_analysis_at == deadline
    assert [event_type for event_type, _ in events].count("auto.mode") == 3


def test_only_one_analysis_worker_runs_while_gv_ticks_continue():
    started = threading.Event()
    release = threading.Event()
    analyse_calls = []

    def analyse(_rates, _entropy):
        analyse_calls.append(True)
        started.set()
        assert release.wait(1)
        return AnalysisResult()

    controller = _controller(SequenceEntropy([100, 100]), analyse=analyse)
    controller.start("HOMEOPATHY_Test")
    controller.tick()
    assert started.wait(1)

    controller.tick()
    assert controller.snapshot()["runs"] == 2
    assert len(analyse_calls) == 1

    release.set()
    _wait_until(lambda: not controller.state._analysing)


def test_worker_uses_latest_case_gv_like_original_bytecode():
    """GuiElements.java:401 liest den veränderlichen aktuellen Fall-GV."""
    started = threading.Event()
    release = threading.Event()
    enqueued = []

    def analyse(_rates, _entropy):
        started.set()
        assert release.wait(1)
        return AnalysisResult(rate_objects=[RateObject(name_or_rate="Current GV")])

    controller = _controller(
        SequenceEntropy([100, 300, 900]),
        analyse=analyse,
        enqueue=lambda signature, seconds, multiplier: enqueued.append(
            (signature, seconds, multiplier)
        ),
    )
    controller.start("HOMEOPATHY_Test")
    controller.tick()
    assert started.wait(1)

    controller.tick()
    assert controller.snapshot()["caseGv"] == 300
    release.set()
    _wait_until(lambda: not controller.state._analysing)

    assert enqueued == []


def test_stop_during_analysis_prevents_late_enqueue():
    started = threading.Event()
    release = threading.Event()
    enqueued = []

    def analyse(_rates, _entropy):
        started.set()
        assert release.wait(1)
        return AnalysisResult(rate_objects=[RateObject(name_or_rate="Late Rate")])

    controller_entropy = SequenceEntropy([100, 801])
    controller = _controller(
        controller_entropy,
        analyse=analyse,
        enqueue=lambda signature, seconds, multiplier: enqueued.append(
            (signature, seconds, multiplier)
        ),
    )
    controller.start("HOMEOPATHY_Test", multiplier=4)
    controller.tick()
    assert started.wait(1)

    controller.stop()
    release.set()
    _wait_until(lambda: not controller.state._analysing)

    assert enqueued == []
    assert controller.snapshot()["enabled"] is False
    assert controller._worker is None
    assert controller_entropy.gv_draws == 3


def test_stop_does_not_wait_for_a_blocked_worker_entropy_draw():
    entered = threading.Event()
    release = threading.Event()
    stopped = threading.Event()
    enqueued = []

    class BlockingWorkerEntropy:
        def __init__(self):
            self.calls = 0

        def get_integer(self, min_inclusive, max_inclusive):
            self.calls += 1
            if (min_inclusive, max_inclusive) == (0, 999) and self.calls == 4:
                entered.set()
                assert release.wait(1)
            if (min_inclusive, max_inclusive) == (10, 1000):
                return 500
            return 100 if self.calls <= 3 else 801

    controller = _controller(
        BlockingWorkerEntropy(),
        analyse=lambda _rates, _entropy: AnalysisResult(
            rate_objects=[RateObject(name_or_rate="Blocked Rate")]
        ),
        enqueue=lambda signature, seconds, multiplier: enqueued.append(
            (signature, seconds, multiplier)
        ),
    )
    controller.start("HOMEOPATHY_Test")
    controller.tick()
    assert entered.wait(1)

    stopper = threading.Thread(target=lambda: (controller.stop(), stopped.set()))
    stopper.start()
    stopped_without_waiting_for_entropy = stopped.wait(0.2)
    release.set()
    stopper.join(1)
    _wait_until(lambda: not controller.state._analysing)

    assert stopped_without_waiting_for_entropy
    assert enqueued == []
    assert controller.snapshot()["enabled"] is False


def test_stop_does_not_wait_for_a_blocked_tick_entropy_draw():
    entered = threading.Event()
    release = threading.Event()
    stopped = threading.Event()

    class BlockingTickEntropy:
        def get_integer(self, min_inclusive, max_inclusive):
            assert (min_inclusive, max_inclusive) == (0, 999)
            entered.set()
            assert release.wait(1)
            return 500

    controller = _controller(BlockingTickEntropy())
    controller.start("HOMEOPATHY_Test")
    ticker = threading.Thread(target=controller.tick)
    ticker.start()
    assert entered.wait(1)

    stopper = threading.Thread(target=lambda: (controller.stop(), stopped.set()))
    stopper.start()
    stopped_without_waiting_for_entropy = stopped.wait(0.2)
    release.set()
    stopper.join(1)
    ticker.join(1)

    assert stopped_without_waiting_for_entropy
    assert controller.snapshot()["enabled"] is False


def test_shutdown_joins_analysis_worker():
    started = threading.Event()
    release = threading.Event()

    def analyse(_rates, _entropy):
        started.set()
        assert release.wait(1)
        return AnalysisResult()

    controller = _controller(SequenceEntropy([100]), analyse=analyse)
    controller.start("HOMEOPATHY_Test")
    controller.tick()
    assert started.wait(1)
    worker = controller._worker
    assert worker is not None and worker.is_alive()

    shutdown_thread = threading.Thread(
        target=lambda: controller.shutdown(timeout=1),
        name="test-auto-shutdown",
    )
    shutdown_thread.start()
    _wait_until(lambda: controller._shutdown)
    assert shutdown_thread.is_alive(), "Shutdown wartete nicht auf den aktiven Worker"

    release.set()
    shutdown_thread.join(1)

    assert not shutdown_thread.is_alive()
    assert not worker.is_alive()
    assert controller._worker is None
    assert controller.snapshot()["enabled"] is False


def test_empty_rates_release_worker_for_a_later_tick():
    calls = []

    def find_rates(_database):
        calls.append(True)
        return []

    controller = _controller(
        SequenceEntropy([100, 100]),
        find_rates=find_rates,
    )
    controller.start("EMPTY")

    controller.tick()
    _wait_until(lambda: not controller.state._analysing)
    controller.tick()
    _wait_until(lambda: not controller.state._analysing)

    assert len(calls) == 2


def test_analysis_error_emits_event_and_releases_worker():
    events = []

    def fail(_rates, _entropy):
        raise RuntimeError("kaputt")

    controller = _controller(
        SequenceEntropy([100]),
        analyse=fail,
        emit=lambda event_type, payload: events.append((event_type, payload)),
    )
    controller.start("HOMEOPATHY_Test")
    controller.tick()
    _wait_until(lambda: not controller.state._analysing)

    errors = [payload for event_type, payload in events if event_type == "auto.error"]
    assert errors == [{"phase": "analysis", "message": "kaputt"}]


def test_first_bytecode_candidate_is_broadcast_with_complete_payload():
    enqueued = []
    events = []
    done = threading.Event()
    result = AnalysisResult(
        rate_objects=[
            RateObject(name_or_rate="Skip Boundary"),
            RateObject(name_or_rate="First Candidate"),
            RateObject(name_or_rate="Never Reached"),
        ]
    )

    def enqueue(signature, seconds, multiplier):
        enqueued.append((signature, seconds, multiplier))
        done.set()
        return {"broadcastId": "broadcast-1"}

    controller = _controller(
        SequenceEntropy([100, 800, 801], seconds=500),
        enqueue=enqueue,
        emit=lambda event_type, payload: events.append((event_type, payload)),
        analyse=lambda _rates, _entropy: result,
    )
    controller.start("HOMEOPATHY_Test", multiplier=3)
    controller.tick()
    assert done.wait(1)
    _wait_until(lambda: not controller.state._analysing)

    assert enqueued == [("First Candidate", 500, 3)]
    auto_events = [payload for event_type, payload in events if event_type == "auto.broadcast"]
    assert auto_events == [
        {
            "rate": "First Candidate",
            "seconds": 500,
            "multiplier": 3,
            "gvOfRate": 801,
            "caseGv": 100,
            "broadcastId": "broadcast-1",
        }
    ]


@pytest.mark.parametrize(
    ("gv_of_rate", "case_gv", "expected"),
    [
        (1400, 1000, False),
        (1401, 1000, True),
        (800, 100, False),
        (801, 100, True),
        (1400, 100, True),
    ],
)
def test_bytecode_candidate_boundaries(gv_of_rate, case_gv, expected):
    assert is_auto_broadcast_candidate(gv_of_rate, case_gv) is expected
