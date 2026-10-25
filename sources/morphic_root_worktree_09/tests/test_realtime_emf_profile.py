from __future__ import annotations

import json
import math
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from apps.cli.workflow.state import WorkflowState
from core.hardware.drivers import (
    CachedHardwareSampler,
    HardwareDriverRegistry,
    MockSignalProvider,
)
from core.realtime.emf_profile import (
    EMFProfileService,
    default_sensor_entropy_probe,
    default_system_load_probe,
    hardware_sampler_entropy_probe,
    histogram_entropy_score,
    sensor_manager_entropy_probe,
)


PROFILE_NUMERIC_FIELDS = (
    "emf_index",
    "entropy_score",
    "timing_jitter_ms",
    "system_load",
    "sensor_entropy",
)
EXPECTED_DEFAULT_SAMPLE_SIZE = 2048
EXPECTED_DEFAULT_TIMING_ITERATIONS = 20
EXPECTED_MAX_SAMPLE_SIZE = 1024 * 1024
EXPECTED_MAX_TIMING_ITERATIONS = 100_000


def _raise_private_probe_error(*_args: object) -> object:
    raise RuntimeError("private probe exception must not leak")


def _assert_strict_json_profile(profile: dict[str, object]) -> None:
    for field_name in PROFILE_NUMERIC_FIELDS:
        value = profile[field_name]
        assert isinstance(value, (int, float)) and not isinstance(value, bool)
        assert math.isfinite(value)
    json.dumps(profile, allow_nan=False)


def _valid_service(**overrides: object) -> EMFProfileService:
    probes = {
        "rng_bytes": lambda size: bytes(range(256)) * (size // 256),
        "timing_probe": lambda iterations: [0.01 for _ in range(iterations)],
        "system_load_probe": lambda: 0.25,
        "sensor_entropy_probe": lambda: (0.75, "ok"),
    }
    probes.update(overrides)
    return EMFProfileService(**probes)


class HostileInt(int):
    operations = 0

    def _fail(self, *_args: object) -> object:
        type(self).operations += 1
        raise AssertionError("hostile int operation must not run")

    __le__ = _fail
    __gt__ = _fail
    __mul__ = _fail
    __rmul__ = _fail


def test_histogram_entropy_score_rates_varied_bytes_above_flat_bytes() -> None:
    flat = bytes([7]) * 2048
    varied = bytes(range(256)) * 8

    assert histogram_entropy_score(varied) > 0.95
    assert histogram_entropy_score(flat) < 0.05


def test_profile_service_returns_bounded_json_safe_profile() -> None:
    service = _valid_service()

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
    _assert_strict_json_profile(data)


@pytest.mark.parametrize(
    "probe_result",
    [
        b"",
        bytes(2047),
        bytes(2049),
        bytearray(2048),
        None,
        "0" * 2048,
        math.nan,
        math.inf,
        -math.inf,
    ],
    ids=(
        "empty",
        "too-short",
        "too-long",
        "bytearray",
        "none",
        "numeric-string",
        "nan",
        "positive-infinity",
        "negative-infinity",
    ),
)
def test_profile_service_marks_invalid_rng_probe_as_fallback(
    probe_result: object,
) -> None:
    profile = _valid_service(rng_bytes=lambda _size: probe_result).measure().to_dict()

    assert profile["entropy_score"] == 0.0
    assert profile["source_health"]["rng"] == "fallback"
    assert profile["replay"]["sample_size"] == EXPECTED_DEFAULT_SAMPLE_SIZE
    _assert_strict_json_profile(profile)


def test_profile_service_marks_rng_probe_exception_as_fallback() -> None:
    profile = _valid_service(rng_bytes=_raise_private_probe_error).measure().to_dict()

    assert profile["entropy_score"] == 0.0
    assert profile["source_health"]["rng"] == "fallback"
    assert "private probe exception" not in json.dumps(profile)
    _assert_strict_json_profile(profile)


def test_profile_service_requires_positive_rng_sample_size() -> None:
    profile = _valid_service(
        sample_size=0,
        rng_bytes=lambda _size: b"",
    ).measure().to_dict()

    assert profile["entropy_score"] == 0.0
    assert profile["source_health"]["rng"] == "fallback"
    _assert_strict_json_profile(profile)


@pytest.mark.parametrize(
    "invalid_sample_size",
    [EXPECTED_MAX_SAMPLE_SIZE + 1, 10**100, True, 2048.0, HostileInt(2048)],
    ids=("above-maximum", "huge-int", "boolean", "float", "hostile-int-subclass"),
)
def test_profile_service_sanitizes_invalid_sample_size_without_call_or_allocation(
    invalid_sample_size: object,
) -> None:
    HostileInt.operations = 0
    calls: list[object] = []

    def rng_probe(size: object) -> bytes:
        calls.append(size)
        return b""

    profile = _valid_service(
        sample_size=invalid_sample_size,
        rng_bytes=rng_probe,
    ).measure().to_dict()

    assert calls == []
    assert HostileInt.operations == 0
    assert profile["source_health"]["rng"] == "fallback"
    assert profile["replay"]["sample_size"] == EXPECTED_DEFAULT_SAMPLE_SIZE
    assert type(profile["replay"]["sample_size"]) is int
    _assert_strict_json_profile(profile)


@pytest.mark.parametrize(
    "timing_factory",
    [
        lambda count: [],
        lambda count: tuple(0.01 for _ in range(count)),
        lambda count: [0.01 for _ in range(count - 1)],
        lambda count: None,
        lambda count: [math.nan for _ in range(count)],
        lambda count: [math.inf for _ in range(count)],
        lambda count: [-math.inf for _ in range(count)],
        lambda count: [True for _ in range(count)],
        lambda count: ["0.01" for _ in range(count)],
        lambda count: [0.01 for _ in range(count - 1)] + [-0.01],
        lambda count: [0.01 for _ in range(count - 1)] + ["0.01"],
        lambda count: [1e308 for _ in range(count)],
    ],
    ids=(
        "empty",
        "tuple",
        "wrong-length",
        "none",
        "nan",
        "positive-infinity",
        "negative-infinity",
        "boolean",
        "numeric-string",
        "negative",
        "mixed",
        "overflow",
    ),
)
def test_profile_service_marks_invalid_timing_probe_as_fallback(
    timing_factory,
) -> None:
    profile = _valid_service(timing_probe=timing_factory).measure().to_dict()

    assert profile["timing_jitter_ms"] == 0.0
    assert profile["source_health"]["cpu_timing"] == "fallback"
    assert (
        profile["replay"]["timing_iterations"]
        == EXPECTED_DEFAULT_TIMING_ITERATIONS
    )
    _assert_strict_json_profile(profile)


def test_profile_service_marks_timing_probe_exception_as_fallback() -> None:
    profile = _valid_service(timing_probe=_raise_private_probe_error).measure().to_dict()

    assert profile["timing_jitter_ms"] == 0.0
    assert profile["source_health"]["cpu_timing"] == "fallback"
    assert "private probe exception" not in json.dumps(profile)
    _assert_strict_json_profile(profile)


def test_profile_service_requires_positive_timing_iteration_count() -> None:
    profile = _valid_service(
        timing_iterations=0,
        timing_probe=lambda _count: [],
    ).measure().to_dict()

    assert profile["timing_jitter_ms"] == 0.0
    assert profile["source_health"]["cpu_timing"] == "fallback"
    _assert_strict_json_profile(profile)


@pytest.mark.parametrize(
    "invalid_timing_iterations",
    [EXPECTED_MAX_TIMING_ITERATIONS + 1, 10**100, True, 20.0, HostileInt(20)],
    ids=("above-maximum", "huge-int", "boolean", "float", "hostile-int-subclass"),
)
def test_profile_service_sanitizes_invalid_timing_count_without_call(
    invalid_timing_iterations: object,
) -> None:
    HostileInt.operations = 0
    calls: list[object] = []

    def timing_probe(iterations: object) -> list[float]:
        calls.append(iterations)
        return []

    profile = _valid_service(
        timing_iterations=invalid_timing_iterations,
        timing_probe=timing_probe,
    ).measure().to_dict()

    assert calls == []
    assert HostileInt.operations == 0
    assert profile["source_health"]["cpu_timing"] == "fallback"
    assert (
        profile["replay"]["timing_iterations"]
        == EXPECTED_DEFAULT_TIMING_ITERATIONS
    )
    assert type(profile["replay"]["timing_iterations"]) is int
    _assert_strict_json_profile(profile)


def test_profile_service_non_finite_requested_lengths_remain_strict_json_safe() -> None:
    profile = _valid_service(
        sample_size=math.nan,
        timing_iterations=math.inf,
    ).measure().to_dict()

    assert profile["source_health"]["rng"] == "fallback"
    assert profile["source_health"]["cpu_timing"] == "fallback"
    assert math.isfinite(profile["replay"]["sample_size"])
    assert math.isfinite(profile["replay"]["timing_iterations"])
    _assert_strict_json_profile(profile)


def test_profile_service_preserves_valid_in_range_custom_lengths() -> None:
    rng_calls: list[int] = []
    timing_calls: list[int] = []

    def rng_probe(size: int) -> bytes:
        rng_calls.append(size)
        return bytes(range(256)) * (size // 256)

    def timing_probe(iterations: int) -> list[float]:
        timing_calls.append(iterations)
        return [0.01 for _ in range(iterations)]

    profile = _valid_service(
        sample_size=512,
        timing_iterations=4,
        rng_bytes=rng_probe,
        timing_probe=timing_probe,
    ).measure().to_dict()

    assert rng_calls == [512]
    assert timing_calls == [4]
    assert profile["source_health"]["rng"] == "ok"
    assert profile["source_health"]["cpu_timing"] == "ok"
    assert profile["replay"]["sample_size"] == 512
    assert profile["replay"]["timing_iterations"] == 4
    _assert_strict_json_profile(profile)


@pytest.mark.parametrize(
    "probe_result",
    [None, "", "0.2", True, math.nan, math.inf, -math.inf],
    ids=(
        "none",
        "empty-string",
        "numeric-string",
        "boolean",
        "nan",
        "positive-infinity",
        "negative-infinity",
    ),
)
def test_profile_service_marks_invalid_system_load_probe_as_fallback(
    probe_result: object,
) -> None:
    profile = _valid_service(
        system_load_probe=lambda: probe_result
    ).measure().to_dict()

    assert profile["system_load"] == 0.3
    assert profile["source_health"]["system_load"] == "fallback"
    _assert_strict_json_profile(profile)


def test_profile_service_marks_system_load_probe_exception_as_fallback() -> None:
    profile = _valid_service(
        system_load_probe=_raise_private_probe_error
    ).measure().to_dict()

    assert profile["system_load"] == 0.3
    assert profile["source_health"]["system_load"] == "fallback"
    assert "private probe exception" not in json.dumps(profile)
    _assert_strict_json_profile(profile)


@pytest.mark.parametrize(
    "probe_result",
    [
        None,
        (),
        (0.2,),
        (0.2, "ok", "extra"),
        [0.2, "ok"],
        ("0.2", "ok"),
        (True, "ok"),
        (math.nan, "ok"),
        (math.inf, "ok"),
        (-math.inf, "ok"),
        (0.2, ""),
        (0.2, "healthy"),
        (0.2, None),
    ],
    ids=(
        "none",
        "empty-tuple",
        "short-tuple",
        "long-tuple",
        "list-shape",
        "numeric-string",
        "boolean",
        "nan",
        "positive-infinity",
        "negative-infinity",
        "empty-status",
        "invalid-status",
        "none-status",
    ),
)
def test_profile_service_marks_invalid_sensor_probe_as_fallback(
    probe_result: object,
) -> None:
    profile = _valid_service(
        sensor_entropy_probe=lambda: probe_result
    ).measure().to_dict()

    assert profile["sensor_entropy"] == 0.5
    assert profile["source_health"]["sensor_entropy"] == "fallback"
    _assert_strict_json_profile(profile)


def test_profile_service_marks_sensor_probe_exception_as_fallback() -> None:
    profile = _valid_service(
        sensor_entropy_probe=_raise_private_probe_error
    ).measure().to_dict()

    assert profile["sensor_entropy"] == 0.5
    assert profile["source_health"]["sensor_entropy"] == "fallback"
    assert "private probe exception" not in json.dumps(profile)
    _assert_strict_json_profile(profile)


@pytest.mark.parametrize("status", ["ok", "partial", "fallback"])
@pytest.mark.parametrize(
    ("probe_value", "expected_value"),
    [(-0.25, 0.0), (0.75, 0.75), (1.25, 1.0)],
)
def test_profile_service_clamps_valid_sensor_value_and_preserves_status(
    status: str,
    probe_value: float,
    expected_value: float,
) -> None:
    profile = _valid_service(
        sensor_entropy_probe=lambda: (probe_value, status)
    ).measure().to_dict()

    assert profile["sensor_entropy"] == expected_value
    assert profile["source_health"]["sensor_entropy"] == status
    _assert_strict_json_profile(profile)


@pytest.mark.parametrize(
    ("probe_value", "expected_value"),
    [(-0.25, 0.0), (0.25, 0.25), (1.25, 1.0)],
)
def test_profile_service_clamps_valid_finite_system_load(
    probe_value: float,
    expected_value: float,
) -> None:
    profile = _valid_service(system_load_probe=lambda: probe_value).measure().to_dict()

    assert profile["system_load"] == expected_value
    assert profile["source_health"]["system_load"] == "ok"
    _assert_strict_json_profile(profile)


def test_profile_service_all_invalid_probes_are_safe_fallbacks() -> None:
    profile = EMFProfileService(
        rng_bytes=lambda _size: math.nan,
        timing_probe=lambda count: [0.01 for _ in range(count - 1)] + [math.inf],
        system_load_probe=lambda: "0.99",
        sensor_entropy_probe=lambda: (math.nan, "ok"),
        sensor_source="hardware_snapshot",
    ).measure().to_dict()

    assert profile["recommendation"] != "hoch"
    assert profile["source_health"] == {
        "rng": "fallback",
        "cpu_timing": "fallback",
        "system_load": "fallback",
        "sensor_entropy": "fallback",
    }
    assert profile["replay"]["sensor_source"] == "hardware_snapshot"
    _assert_strict_json_profile(profile)


def test_profile_service_records_sensor_source_in_replay() -> None:
    service = EMFProfileService(
        rng_bytes=lambda size: bytes(range(256)) * (size // 256),
        timing_probe=lambda iterations: [0.01 for _ in range(iterations)],
        system_load_probe=lambda: 0.25,
        sensor_entropy_probe=lambda: (0.75, "ok"),
        sensor_source="hardware_snapshot",
    )

    profile = service.measure().to_dict()

    assert profile["replay"]["sensor_source"] == "hardware_snapshot"


def test_default_sensor_entropy_probe_is_lightweight_fallback() -> None:
    assert default_sensor_entropy_probe() == (0.5, "fallback")


def test_default_system_load_probe_propagates_internal_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingPsutil:
        @staticmethod
        def cpu_percent(*_args: object, **_kwargs: object) -> float:
            raise RuntimeError("private psutil exception")

    monkeypatch.setitem(sys.modules, "psutil", FailingPsutil())

    with pytest.raises(RuntimeError, match="private psutil exception"):
        default_system_load_probe()


@pytest.mark.parametrize("invalid_value", [math.nan, math.inf, -math.inf])
def test_sensor_manager_entropy_probe_rejects_non_finite_as_fallback(
    monkeypatch: pytest.MonkeyPatch,
    invalid_value: float,
) -> None:
    from core.hardware import sensors

    class NonFiniteSensorManager:
        def get_combined_entropy(self) -> float:
            return invalid_value

    monkeypatch.setattr(sensors, "SensorManager", NonFiniteSensorManager)

    assert sensor_manager_entropy_probe() == (0.5, "fallback")


def test_hardware_sampler_entropy_probe_averages_ok_samples() -> None:
    sampler = CachedHardwareSampler(
        HardwareDriverRegistry(
            [
                MockSignalProvider(value=0.2, provider_id="a"),
                MockSignalProvider(value=0.8, provider_id="b"),
            ]
        ),
        ttl_seconds=2.0,
    )

    value, status = hardware_sampler_entropy_probe(sampler)

    assert value == 0.5
    assert status == "ok"


def test_hardware_sampler_entropy_probe_falls_back_without_ok_samples() -> None:
    sampler = CachedHardwareSampler(HardwareDriverRegistry([]))

    value, status = hardware_sampler_entropy_probe(sampler, provider_ids=["missing"])

    assert value == 0.5
    assert status == "fallback"


def test_hardware_sampler_entropy_probe_ignores_non_finite_values() -> None:
    class BadSample:
        status = "ok"
        value = math.nan

    class BadSampler:
        def sample(self, provider_ids=None):
            return [BadSample()]

    value, status = hardware_sampler_entropy_probe(BadSampler())

    assert value == 0.5
    assert status == "fallback"


@pytest.mark.parametrize(
    "samples",
    [
        None,
        (SimpleNamespace(status="ok", value=0.2),),
        (sample for sample in [SimpleNamespace(status="ok", value=0.2)]),
        "not-a-list",
        [],
    ],
    ids=("none", "tuple", "generator", "string", "empty"),
)
def test_hardware_sampler_entropy_probe_requires_nonempty_concrete_list(
    samples: object,
) -> None:
    sampler = SimpleNamespace(sample=lambda _provider_ids: samples)

    assert hardware_sampler_entropy_probe(sampler) == (0.5, "fallback")


@pytest.mark.parametrize(
    "invalid_value",
    ["0.2", True, math.nan, math.inf, -math.inf],
    ids=("numeric-string", "boolean", "nan", "positive-infinity", "negative-infinity"),
)
def test_hardware_sampler_entropy_probe_rejects_invalid_ok_value(
    invalid_value: object,
) -> None:
    sampler = SimpleNamespace(
        sample=lambda _provider_ids: [
            SimpleNamespace(status="ok", value=invalid_value)
        ]
    )

    assert hardware_sampler_entropy_probe(sampler) == (0.5, "fallback")


def test_hardware_sampler_entropy_probe_falls_back_on_overflowing_average() -> None:
    sampler = SimpleNamespace(
        sample=lambda _provider_ids: [
            SimpleNamespace(status="ok", value=1e308),
            SimpleNamespace(status="ok", value=1e308),
        ]
    )

    assert hardware_sampler_entropy_probe(sampler) == (0.5, "fallback")


@pytest.mark.parametrize("attribute", ["status", "value"])
def test_hardware_sampler_entropy_probe_contains_raising_sample_attributes(
    attribute: str,
) -> None:
    class RaisingSample:
        @property
        def status(self) -> str:
            if attribute == "status":
                raise RuntimeError("private status failure")
            return "ok"

        @property
        def value(self) -> float:
            if attribute == "value":
                raise RuntimeError("private value failure")
            return 0.2

    sampler = SimpleNamespace(sample=lambda _provider_ids: [RaisingSample()])

    assert hardware_sampler_entropy_probe(sampler) == (0.5, "fallback")


@pytest.mark.parametrize(
    "malformed_sample",
    [object(), SimpleNamespace(status=None, value=0.2), SimpleNamespace(status="", value=0.2)],
    ids=("missing-attributes", "none-status", "empty-status"),
)
def test_hardware_sampler_entropy_probe_rejects_malformed_samples(
    malformed_sample: object,
) -> None:
    sampler = SimpleNamespace(
        sample=lambda _provider_ids: [
            SimpleNamespace(status="ok", value=0.2),
            malformed_sample,
        ]
    )

    assert hardware_sampler_entropy_probe(sampler) == (0.5, "fallback")


class StatusSubclass(str):
    pass


@pytest.mark.parametrize("mixed_with_ok", [False, True], ids=("alone", "mixed"))
@pytest.mark.parametrize(
    "invalid_status",
    ["healthy", "", "OK", None, StatusSubclass("ok")],
    ids=("unknown", "empty", "uppercase", "none", "str-subclass"),
)
def test_hardware_sampler_entropy_probe_rejects_noncanonical_statuses(
    invalid_status: object,
    mixed_with_ok: bool,
) -> None:
    samples = [SimpleNamespace(status=invalid_status, value=0.8)]
    if mixed_with_ok:
        samples.insert(0, SimpleNamespace(status="ok", value=0.2))
    sampler = SimpleNamespace(sample=lambda _provider_ids: samples)

    assert hardware_sampler_entropy_probe(sampler) == (0.5, "fallback")


@pytest.mark.parametrize(
    "degraded_status",
    ["unavailable", "timeout", "error", "fallback"],
)
def test_hardware_sampler_entropy_probe_preserves_allowed_degraded_partial_mix(
    degraded_status: str,
) -> None:
    sampler = SimpleNamespace(
        sample=lambda _provider_ids: [
            SimpleNamespace(status="ok", value=0.2),
            SimpleNamespace(status=degraded_status, value="not-inspected"),
        ]
    )

    assert hardware_sampler_entropy_probe(sampler) == (0.2, "partial")


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


def test_workflow_step05_uses_shared_profile_for_state(monkeypatch, tmp_path) -> None:
    from apps.cli.workflow import step05_emf
    from apps.web.emf_authority import EmfTelemetryAuthority

    authority_path = tmp_path / "emf-authority.json"
    EmfTelemetryAuthority(authority_path).set_enabled(True)
    monkeypatch.setenv("MORPHIC_EMF_AUTHORITY_PATH", str(authority_path))
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


def test_workflow_step05_is_default_off_without_authority(monkeypatch) -> None:
    from apps.cli.workflow import step05_emf

    monkeypatch.delenv("MORPHIC_EMF_AUTHORITY_PATH", raising=False)
    monkeypatch.setattr(
        step05_emf,
        "EMFProfileService",
        lambda: (_ for _ in ()).throw(AssertionError("must not measure")),
    )
    state = WorkflowState(
        client_rates=np.array([1.0, 2.0, 3.0]),
        client_frequency=432.0,
    )

    result = step05_emf.step_05_emf(state, verbose=False)

    assert result.composite_emf_index == 0.0
