"""Lifecycle regressions: runtime lease outlives every owned writer."""

import threading
import time

import pytest
from fastapi.testclient import TestClient

from radiworks.api.routes import STATE
from radiworks.core.analysis import AnalysisResult, Rate, RateObject
from radiworks.core.automode import AutoModeController
from radiworks.core.broadcast import BroadcastManager
from radiworks.entropy import EntropyProvider
from radiworks.main import create_app


class BlockingSecondsEntropy:
    def __init__(self):
        self._gv_draws = 0
        self._current_gv = 0
        self._gvs = iter((100, 900))
        self.entered = threading.Event()
        self.release = threading.Event()

    def get_integer(self, minimum, maximum):
        if (minimum, maximum) == (0, 999):
            if self._gv_draws % 3 == 0:
                self._current_gv = next(self._gvs)
            self._gv_draws += 1
            return self._current_gv
        if (minimum, maximum) == (10, 1000):
            self.entered.set()
            if not self.release.wait(3):
                raise TimeoutError("synthetic draw was not released")
            return 500
        raise AssertionError((minimum, maximum))


def test_auto_shutdown_raises_if_analysis_worker_outlives_timeout():
    entropy = BlockingSecondsEntropy()
    queued = []
    controller = AutoModeController(
        enqueue=lambda signature, seconds, multiplier: queued.append(signature),
        emit=lambda *_: None,
        find_rates=lambda _database: [Rate(name="Synthetic rate")],
        analyse=lambda _rates, _entropy: AnalysisResult(
            rate_objects=[RateObject(name_or_rate="Synthetic rate")]
        ),
        live_entropy=lambda: entropy,
        queue_state=lambda: {"queued": [], "active": []},
    )
    controller.start("Synthetic")
    controller.tick()
    assert entropy.entered.wait(1)
    worker = controller._worker
    assert worker is not None and worker.is_alive()
    try:
        with pytest.raises(RuntimeError, match="worker"):
            controller.shutdown(timeout=0.01)
        assert worker.is_alive()
    finally:
        entropy.release.set()
        worker.join(1)
    assert not worker.is_alive()
    assert queued == []


def test_broadcast_shutdown_joins_after_stop_event_emit_failure():
    def emit(event_type, payload):
        if event_type == "broadcast.progress" and payload.get("stopped"):
            raise OSError("synthetic event sink failure")

    manager = BroadcastManager(
        entropy=EntropyProvider(seed=0), emit=emit, keep_alive=lambda: True
    )
    manager.enqueue("Synthetic rate", seconds=3600)
    worker = manager._thread
    assert worker is not None and worker.is_alive()
    with pytest.raises(RuntimeError, match="Shutdown"):
        manager.shutdown(timeout=None)
    assert not worker.is_alive()
    assert manager.queue_state()["active"] == []
    assert manager.queue_state()["queued"] == []


def test_lifespan_waits_and_continues_cleanup_after_end_receipt_failure(tmp_path):
    data = tmp_path / "rates"
    data.mkdir()
    (data / "synthetic.txt").write_text("Synthetic rate\n", encoding="utf-8")
    materia = tmp_path / "materia"
    materia.mkdir()
    client = TestClient(
        create_app(base_dir=tmp_path / "runtime", data_dir=data, materia_dir=materia)
    )
    client.__enter__()

    state = STATE.state
    assert state is not None and state.auto is not None
    auto = state.auto
    calls = []
    waiting = threading.Event()
    release = threading.Event()
    observed = {}

    def fail_receipt(*_args):
        raise OSError("synthetic receipt failure")

    auto._target_template = object()
    auto._on_generation_end = fail_receipt
    worker = threading.Thread(target=lambda: release.wait(3))
    auto._worker = worker
    worker.start()

    original_auto = auto.shutdown

    def auto_shutdown(*, timeout=2.0):
        calls.append("auto")
        observed["auto_timeout"] = timeout
        waiting.set()
        return original_auto(timeout=timeout)

    auto.shutdown = auto_shutdown

    original_personal = state.personal.shutdown
    state.personal.shutdown = lambda: (calls.append("personal"), original_personal())[1]
    original_comparison = state.comparisons.shutdown
    state.comparisons.shutdown = lambda: (calls.append("comparisons"), original_comparison())[1]
    original_broadcast = state.broadcast.shutdown

    def broadcast_shutdown(*, timeout=2.0):
        calls.append("broadcast")
        observed["broadcast_timeout"] = timeout
        return original_broadcast(timeout=timeout)

    state.broadcast.shutdown = broadcast_shutdown
    original_request_stop = state.observations.request_stop
    state.observations.request_stop = lambda: (calls.append("observation_stop"), original_request_stop())[1]
    original_observations = state.observations.shutdown

    def observations_shutdown(*, timeout=2.0):
        calls.append("observations")
        observed["observations_timeout"] = timeout
        return original_observations(timeout=timeout)

    state.observations.shutdown = observations_shutdown
    original_websockets = state.shutdown_websockets

    async def shutdown_websockets():
        calls.append("websockets")
        await original_websockets()

    state.shutdown_websockets = shutdown_websockets

    def release_after_auto_starts():
        if not waiting.wait(2):
            observed["entered"] = False
            release.set()
            return
        observed["entered"] = True
        observed["worker_alive"] = worker.is_alive()
        observed["calls_before_release"] = list(calls)
        time.sleep(0.03)
        release.set()

    releaser = threading.Thread(target=release_after_auto_starts)
    releaser.start()
    try:
        with pytest.raises(RuntimeError, match="cleanup failed"):
            client.__exit__(None, None, None)
    finally:
        release.set()
        worker.join(1)
        releaser.join(1)

    assert observed["entered"] is True
    assert observed["worker_alive"] is True
    assert observed["auto_timeout"] is None
    assert "broadcast" not in observed["calls_before_release"]
    assert "observations" not in observed["calls_before_release"]
    assert "websockets" not in observed["calls_before_release"]
    assert {"personal", "comparisons", "observation_stop", "auto", "broadcast",
            "observations", "websockets"}.issubset(calls)
    assert observed["broadcast_timeout"] is None
    assert observed["observations_timeout"] is None
    assert not worker.is_alive()
    assert state.loop is None
    assert STATE.state is None
