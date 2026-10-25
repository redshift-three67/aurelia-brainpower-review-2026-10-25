# V2 Realtime EMF Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first V2 realtime foundation by sharing EMF profiling between web and CLI workflow code and by tracing harmonization lifecycle/cycle events.

**Architecture:** Add `core/realtime/emf_profile.py` for low-load EMF snapshots and `core/realtime/event_log.py` for append-only JSONL traces. Web EMF endpoints delegate to the shared service, workflow step 05 consumes the same profile while keeping its compensation vector behavior, and the harmonization worker records lifecycle/cycle events without changing the JSON job store contract.

**Tech Stack:** Python dataclasses, FastAPI route integration, existing numpy workflow code, pytest focused tests, JSON Lines event files.

---

## File Structure

- Create `core/realtime/__init__.py`: package marker and optional exports.
- Create `core/realtime/emf_profile.py`: `EMFProfile`, `EMFProfileService`, entropy scoring helpers.
- Create `core/realtime/event_log.py`: JSONL event append/read helpers.
- Modify `apps/web/emf.py`: delegate `measure_emf()` to `EMFProfileService`.
- Modify `apps/cli/workflow/step05_emf.py`: reuse `EMFProfileService` for profile values.
- Modify `services/harmonization_worker.py`: append lifecycle/cycle events.
- Test `tests/test_realtime_emf_profile.py`: profile math, JSON-safe shape, web delegation, workflow integration.
- Test `tests/test_realtime_event_log.py`: event sequence and JSONL persistence.
- Modify `tests/test_harmonization_worker_stop.py`: event tracing during worker stop path.

---

### Task 1: Shared EMF Profile Service

**Files:**
- Create: `core/realtime/__init__.py`
- Create: `core/realtime/emf_profile.py`
- Test: `tests/test_realtime_emf_profile.py`

- [ ] **Step 1: Write the failing tests**

Add:

```python
from __future__ import annotations

from core.realtime.emf_profile import (
    EMFProfileService,
    histogram_entropy_score,
)


def test_histogram_entropy_score_rates_varied_bytes_above_flat_bytes() -> None:
    flat = bytes([7]) * 2048
    varied = bytes(range(256)) * 8

    assert histogram_entropy_score(varied) > 0.95
    assert histogram_entropy_score(flat) < 0.05


def test_profile_service_returns_bounded_json_safe_profile() -> None:
    service = EMFProfileService(
        rng_bytes=lambda size: bytes(range(256)) * (size // 256),
        timing_probe=lambda iterations: [0.01 for _ in range(iterations)],
        system_load_probe=lambda: 0.25,
        sensor_entropy_probe=lambda: (0.75, "ok"),
    )

    profile = service.measure()
    data = profile.to_dict()

    assert 0.0 <= data["emf_index"] <= 1.0
    assert 0.0 <= data["entropy_score"] <= 1.0
    assert data["timing_jitter_ms"] == 0.0
    assert data["system_load"] == 0.25
    assert data["sensor_entropy"] == 0.75
    assert data["source_health"]["sensor_entropy"] == "ok"
    assert data["replay"]["algorithm"] == "emf-profile-v2"
    assert data["counter_frequencies"] == [528.0]
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_realtime_emf_profile.py -q
```

Expected: import failure for `core.realtime.emf_profile`.

- [ ] **Step 3: Implement minimal service**

Create `core/realtime/__init__.py`:

```python
"""Realtime profiling and trace utilities."""
```

Create `core/realtime/emf_profile.py` with:

```python
from __future__ import annotations

import math
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Callable


RngBytes = Callable[[int], bytes]
TimingProbe = Callable[[int], list[float]]
SystemLoadProbe = Callable[[], float]
SensorEntropyProbe = Callable[[], tuple[float, str]]


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, float(value)))


def histogram_entropy_score(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    total = float(len(data))
    entropy = 0.0
    for count in counts:
        if count:
            p = count / total
            entropy -= p * math.log2(p)
    return clamp(entropy / 8.0)


def lag1_autocorrelation_score(data: bytes, sample_size: int = 512) -> float:
    values = [float(b) for b in data[:sample_size]]
    if len(values) < 2:
        return 0.5
    mean = sum(values) / len(values)
    den = sum((v - mean) ** 2 for v in values)
    if den <= 0:
        return 0.0
    num = sum((values[i] - mean) * (values[i + 1] - mean) for i in range(len(values) - 1))
    return clamp(1.0 - abs(num / den))


def default_timing_probe(iterations: int) -> list[float]:
    timings: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        _ = sum(i * i for i in range(50))
        t1 = time.perf_counter_ns()
        timings.append((t1 - t0) / 1e6)
    return timings


def default_system_load_probe() -> float:
    try:
        import psutil

        return clamp((psutil.cpu_percent(interval=0.05) + psutil.virtual_memory().percent) / 200.0)
    except Exception:
        return 0.3


def default_sensor_entropy_probe() -> tuple[float, str]:
    try:
        from core.hardware.sensors import SensorManager

        return clamp(SensorManager().get_combined_entropy()), "ok"
    except Exception:
        return 0.5, "fallback"


@dataclass
class EMFProfile:
    timestamp: str
    emf_index: float
    entropy_score: float
    timing_jitter_ms: float
    system_load: float
    sensor_entropy: float
    recommendation: str
    counter_frequencies: list[float]
    source_health: dict[str, str] = field(default_factory=dict)
    replay: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class EMFProfileService:
    def __init__(
        self,
        *,
        sample_size: int = 2048,
        timing_iterations: int = 20,
        rng_bytes: RngBytes = os.urandom,
        timing_probe: TimingProbe = default_timing_probe,
        system_load_probe: SystemLoadProbe = default_system_load_probe,
        sensor_entropy_probe: SensorEntropyProbe = default_sensor_entropy_probe,
    ) -> None:
        self.sample_size = sample_size
        self.timing_iterations = timing_iterations
        self._rng_bytes = rng_bytes
        self._timing_probe = timing_probe
        self._system_load_probe = system_load_probe
        self._sensor_entropy_probe = sensor_entropy_probe

    def measure(self) -> EMFProfile:
        source_health = {
            "rng": "ok",
            "cpu_timing": "ok",
            "system_load": "ok",
            "sensor_entropy": "ok",
        }
        try:
            data = self._rng_bytes(self.sample_size)
        except Exception:
            data = bytes([128]) * self.sample_size
            source_health["rng"] = "fallback"

        entropy_score = histogram_entropy_score(data)
        autocorr_score = lag1_autocorrelation_score(data)

        try:
            timings = self._timing_probe(self.timing_iterations)
            mean_t = sum(timings) / len(timings) if timings else 0.0
            jitter = math.sqrt(sum((t - mean_t) ** 2 for t in timings) / len(timings)) if timings else 0.0
        except Exception:
            jitter = 0.0
            source_health["cpu_timing"] = "fallback"

        try:
            system_load = clamp(self._system_load_probe())
        except Exception:
            system_load = 0.3
            source_health["system_load"] = "fallback"

        try:
            sensor_entropy, sensor_status = self._sensor_entropy_probe()
            sensor_entropy = clamp(sensor_entropy)
            source_health["sensor_entropy"] = sensor_status or "ok"
        except Exception:
            sensor_entropy = 0.5
            source_health["sensor_entropy"] = "fallback"

        emf_index = clamp(
            0.30 * (1.0 - entropy_score)
            + 0.25 * clamp(jitter)
            + 0.20 * system_load
            + 0.10 * (1.0 - autocorr_score)
            + 0.15 * abs(sensor_entropy - 0.5) * 2.0
        )
        recommendation = "hoch" if emf_index > 0.6 else "mittel" if emf_index > 0.3 else "niedrig"
        counters = [528.0]
        if emf_index > 0.3:
            counters.append(741.0)
        if emf_index > 0.6:
            counters.extend([963.0, 174.0])

        return EMFProfile(
            timestamp=datetime.now().isoformat(),
            emf_index=round(emf_index, 4),
            entropy_score=round(entropy_score, 4),
            timing_jitter_ms=round(jitter, 4),
            system_load=round(system_load, 4),
            sensor_entropy=round(sensor_entropy, 4),
            recommendation=recommendation,
            counter_frequencies=counters,
            source_health=source_health,
            replay={
                "algorithm": "emf-profile-v2",
                "sample_size": self.sample_size,
                "timing_iterations": self.timing_iterations,
                "sensor_manager": "core.hardware.sensors.SensorManager",
            },
        )
```

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_realtime_emf_profile.py -q
```

Expected: profile tests pass.

---

### Task 2: Web And Workflow Integration

**Files:**
- Modify: `apps/web/emf.py`
- Modify: `apps/cli/workflow/step05_emf.py`
- Test: `tests/test_realtime_emf_profile.py`

- [ ] **Step 1: Add failing integration tests**

Append:

```python
import numpy as np

from apps.cli.workflow.state import WorkflowState


class FakeProfile:
    emf_index = 0.42
    entropy_score = 0.9
    timing_jitter_ms = 0.01
    system_load = 0.2
    sensor_entropy = 0.6
    recommendation = "mittel"
    counter_frequencies = [528.0, 741.0]
    source_health = {"rng": "ok"}
    replay = {"algorithm": "emf-profile-v2"}

    def to_dict(self) -> dict[str, object]:
        return {
            "timestamp": "2026-07-03T12:00:00",
            "emf_index": self.emf_index,
            "entropy_score": self.entropy_score,
            "timing_jitter_ms": self.timing_jitter_ms,
            "system_load": self.system_load,
            "sensor_entropy": self.sensor_entropy,
            "recommendation": self.recommendation,
            "counter_frequencies": self.counter_frequencies,
            "source_health": self.source_health,
            "replay": self.replay,
        }


class FakeProfileService:
    def measure(self) -> FakeProfile:
        return FakeProfile()


def test_web_measure_emf_uses_shared_profile_service(monkeypatch) -> None:
    from apps.web import emf

    monkeypatch.setattr(emf, "EMFProfileService", lambda: FakeProfileService())

    payload = emf.measure_emf()

    assert payload["emf_index"] == 0.42
    assert payload["source_health"] == {"rng": "ok"}
    assert payload["replay"]["algorithm"] == "emf-profile-v2"


def test_workflow_step05_uses_shared_profile_for_state(monkeypatch) -> None:
    from apps.cli.workflow import step05_emf

    monkeypatch.setattr(step05_emf, "EMFProfileService", lambda: FakeProfileService())
    state = WorkflowState(
        client_rates=np.array([1.0, 2.0, 3.0]),
        client_frequency=432.0,
    )

    result = step05_emf.step_05_emf(state, verbose=False)

    assert result.composite_emf_index == 0.42
    assert result.counter_frequencies == [528.0, 741.0]
    assert result.emf_corrected_frequency == 432.0 * (1.0 - 0.42 * 0.05)
    assert result.compensation_vector is not None
    assert 5 in result.step_completed
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_realtime_emf_profile.py -q
```

Expected: monkeypatch target or assertion failures because integration still uses old duplicated logic.

- [ ] **Step 3: Implement web delegation**

In `apps/web/emf.py`, import `EMFProfileService` and replace `measure_emf()` body with:

```python
def measure_emf() -> dict:
    """Measure operational EMF telemetry through the shared V2 profile service."""
    return EMFProfileService().measure().to_dict()
```

- [ ] **Step 4: Implement workflow delegation**

In `apps/cli/workflow/step05_emf.py`, import `EMFProfileService` and replace the sensing/profiling section of `step_05_emf()` with:

```python
    profile = EMFProfileService().measure()
    jitter = profile.timing_jitter_ms
    entropy_score = profile.entropy_score
    sys_load = profile.system_load
    gpu_noise = 0.0

    state.composite_emf_index = float(profile.emf_index)
```

Keep the compensation vector code, but use:

```python
    state.counter_frequencies = list(profile.counter_frequencies)
```

instead of rebuilding counters locally.

- [ ] **Step 5: Run tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_realtime_emf_profile.py -q
```

Expected: all realtime EMF tests pass.

---

### Task 3: Append-Only Realtime Event Log

**Files:**
- Create: `core/realtime/event_log.py`
- Test: `tests/test_realtime_event_log.py`

- [ ] **Step 1: Write failing event log tests**

Add:

```python
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


def test_event_log_best_effort_helper_does_not_raise_for_invalid_root(tmp_path) -> None:
    log = RealtimeEventLog(tmp_path / "missing-parent" / "events")

    event = log.append_best_effort("harm_test", "cycle_metrics", {"cycle": 1})

    assert event is not None
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_realtime_event_log.py -q
```

Expected: import failure for `core.realtime.event_log`.

- [ ] **Step 3: Implement event log**

Create `core/realtime/event_log.py`:

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class RealtimeEventLog:
    root: Path

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, job_id: str) -> Path:
        safe_job_id = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in job_id)
        return self.root / f"{safe_job_id}.jsonl"

    def _next_sequence(self, path: Path) -> int:
        if not path.exists():
            return 1
        try:
            return len(path.read_text(encoding="utf-8").splitlines()) + 1
        except OSError:
            return 1

    def append(self, job_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        path = self._path(job_id)
        event = {
            "timestamp": datetime.now().isoformat(),
            "job_id": job_id,
            "event_type": event_type,
            "payload": payload,
            "sequence": self._next_sequence(path),
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        return event

    def append_best_effort(
        self, job_id: str, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        try:
            return self.append(job_id, event_type, payload)
        except Exception:
            return None
```

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_realtime_event_log.py -q
```

Expected: event log tests pass.

---

### Task 4: Harmonization Worker Trace Integration

**Files:**
- Modify: `services/harmonization_worker.py`
- Modify: `tests/test_harmonization_worker_stop.py`

- [ ] **Step 1: Add failing worker trace test**

Append to `tests/test_harmonization_worker_stop.py`:

```python
def test_worker_appends_realtime_trace_events(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(worker, "JOBS_DIR", tmp_path)
    monkeypatch.setattr(worker, "EVENTS_DIR", tmp_path / "events")
    now = [0.0]

    def fake_time() -> float:
        return now[0]

    def fake_sleep(seconds: float) -> None:
        now[0] += max(seconds, 1.0)

    job = HarmonizationJob(
        job_id="harm_trace_check",
        target_frequency=432.0,
        duration_minutes=1,
        intention="harmonization",
        hardware_config={"use_cpu": False},
    )
    job.save()

    calls = {"count": 0}

    def fake_modulate_hardware(*args, **kwargs) -> dict[str, float]:
        calls["count"] += 1
        now[0] += 0.01
        stopped = HarmonizationJob.load("harm_trace_check")
        assert stopped is not None
        stopped.status = "stopped"
        stopped.end_time = datetime.now().isoformat()
        stopped.save()
        return {"cpu_frequency": 431.9}

    monkeypatch.setattr(worker.time, "time", fake_time)
    monkeypatch.setattr(worker.time, "sleep", fake_sleep)
    monkeypatch.setattr(worker, "modulate_hardware", fake_modulate_hardware)
    monkeypatch.setattr(
        worker,
        "measure_realtime_emf_profile",
        lambda: {"emf_index": 0.2, "replay": {"algorithm": "emf-profile-v2"}},
    )

    worker.run_harmonization_worker("harm_trace_check")

    events = (tmp_path / "events" / "harm_trace_check.jsonl").read_text(encoding="utf-8")
    assert '"event_type": "job_started"' in events
    assert '"event_type": "cycle_metrics"' in events
    assert '"event_type": "stop_requested"' in events
    assert '"cpu_frequency": 431.9' in events
```

- [ ] **Step 2: Run worker tests to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_harmonization_worker_stop.py -q
```

Expected: failure because `EVENTS_DIR` and trace hooks do not exist.

- [ ] **Step 3: Implement worker trace hooks**

In `services/harmonization_worker.py`, add after `JOBS_DIR`:

```python
EVENTS_DIR = JOBS_DIR / "events"
```

Add helpers:

```python
def _event_log():
    from core.realtime.event_log import RealtimeEventLog

    return RealtimeEventLog(EVENTS_DIR)


def _append_event(job_id: str, event_type: str, payload: Dict[str, object]) -> None:
    _event_log().append_best_effort(job_id, event_type, payload)


def measure_realtime_emf_profile() -> dict[str, object]:
    from core.realtime.emf_profile import EMFProfileService

    return EMFProfileService().measure().to_dict()
```

In `run_harmonization_worker()`:

- after start status save, append `job_started`.
- after `metrics = modulate_hardware(...)`, append `cycle_metrics` with `cycle`, `metrics`, and `emf_profile` on cycle 1 and every 10 cycles.
- when a stopped job is detected, append `stop_requested`.
- on completion, append `completed`.
- on exception, append `error`.

- [ ] **Step 4: Run worker tests to verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_harmonization_worker_stop.py tests\test_realtime_event_log.py -q
```

Expected: worker stop and event log tests pass.

---

### Task 5: Focused Verification And Commit

**Files:**
- All changed files from tasks 1-4.

- [ ] **Step 1: Run focused tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_realtime_emf_profile.py tests\test_realtime_event_log.py tests\test_harmonization_worker_stop.py -q
```

Expected: all focused tests pass.

- [ ] **Step 2: Run small web-contract regression**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_web_contracts.py tests\test_web_shell.py -q
```

Expected: web contract/shell tests pass.

- [ ] **Step 3: Check Git status**

Run:

```powershell
git status --short
```

Expected: only intended V2 files modified/added.

- [ ] **Step 4: Commit implementation**

Run:

```powershell
git add .
git commit -m "feat: add v2 realtime emf profile trace"
```

Expected: one implementation commit after the design and plan commits.

## Deferred

The full pytest suite remains deferred per `docs/superpowers/plans/2026-07-03-deferred-full-pytest.md`.
