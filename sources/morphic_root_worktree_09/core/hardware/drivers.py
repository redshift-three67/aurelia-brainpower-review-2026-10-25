from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Protocol


VALID_STATUSES = {"ok", "unavailable", "timeout", "error", "fallback"}


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    if not math.isfinite(number):
        number = 0.0
    return max(minimum, min(maximum, number))


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else 0.0
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(v) for v in value]
    return str(value)


@dataclass
class HardwareSignalSample:
    source_id: str
    source_type: str
    status: str
    value: float
    unit: str = "normalized_entropy"
    duration_ms: float = 0.0
    quality: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            self.status = "error"
        self.value = clamp(self.value)
        self.quality = clamp(self.quality)
        self.duration_ms = max(0.0, float(self.duration_ms))
        if not math.isfinite(self.duration_ms):
            self.duration_ms = 0.0
        self.metadata = json_safe(self.metadata)
        self.error = str(self.error or "")

    def to_dict(self) -> dict[str, Any]:
        return json_safe(asdict(self))


@dataclass
class HardwareProviderStatus:
    provider_id: str
    provider_type: str
    display_name: str
    available: bool
    default_timeout_ms: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HardwareSignalProvider(Protocol):
    provider_id: str
    provider_type: str
    display_name: str
    default_timeout_ms: int

    def is_available(self) -> bool: ...

    def sample(self, timeout_ms: int | None = None) -> HardwareSignalSample: ...


class MockSignalProvider:
    provider_type = "mock"
    display_name = "Mock Signal"
    default_timeout_ms = 1

    def __init__(self, value: float = 0.5, provider_id: str = "mock") -> None:
        self.provider_id = provider_id
        self._value = clamp(value)

    def is_available(self) -> bool:
        return True

    def sample(self, timeout_ms: int | None = None) -> HardwareSignalSample:
        return HardwareSignalSample(
            source_id=self.provider_id,
            source_type=self.provider_type,
            status="ok",
            value=self._value,
            quality=1.0,
            metadata={"provider": self.__class__.__name__},
        )


class CpuTimingSignalProvider:
    provider_id = "cpu_timing"
    provider_type = "system"
    display_name = "CPU Timing"
    default_timeout_ms = 50

    def __init__(self, iterations: int = 32) -> None:
        self.iterations = max(3, int(iterations))

    def is_available(self) -> bool:
        return True

    def sample(self, timeout_ms: int | None = None) -> HardwareSignalSample:
        started = time.perf_counter()
        timeout = max(1, int(timeout_ms or self.default_timeout_ms)) / 1000.0
        stamps: list[int] = []
        try:
            while len(stamps) < self.iterations:
                stamps.append(time.perf_counter_ns())
                if time.perf_counter() - started >= timeout:
                    break
            if len(stamps) < 3:
                return HardwareSignalSample(
                    source_id=self.provider_id,
                    source_type=self.provider_type,
                    status="timeout",
                    value=0.5,
                    quality=0.0,
                    duration_ms=(time.perf_counter() - started) * 1000.0,
                    metadata={
                        "provider": self.__class__.__name__,
                        "sample_count": len(stamps),
                    },
                )
            diffs = [
                float(stamps[i + 1] - stamps[i]) for i in range(len(stamps) - 1)
            ]
            mean = sum(diffs) / len(diffs)
            variance = sum((x - mean) ** 2 for x in diffs) / len(diffs)
            rel = math.sqrt(max(variance, 0.0)) / abs(mean or 1.0)
            value = clamp(rel / (rel + 1.0))
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="ok",
                value=value,
                quality=clamp(len(stamps) / float(self.iterations)),
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={
                    "provider": self.__class__.__name__,
                    "sample_count": len(stamps),
                },
            )
        except Exception as exc:
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="error",
                value=0.5,
                quality=0.0,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={"provider": self.__class__.__name__},
                error=str(exc),
            )


class HidSignalProvider:
    provider_id = "hid_sensor"
    provider_type = "hid"
    display_name = "HID Sensor"
    default_timeout_ms = 75

    def __init__(
        self,
        *,
        vid: int = 0x0E50,
        pid: int = 0x0002,
        hid_module: Any = "auto",
        allow_device_open: bool = False,
    ) -> None:
        self.vid = vid
        self.pid = pid
        self._hid_module = hid_module
        self.allow_device_open = allow_device_open

    def _hid(self) -> Any:
        if self._hid_module != "auto":
            return self._hid_module
        try:
            import hid

            return hid
        except Exception:
            return None

    def is_available(self) -> bool:
        hid = self._hid()
        if hid is None:
            return False
        try:
            return bool(hid.enumerate(self.vid, self.pid))
        except Exception:
            return False

    def sample(self, timeout_ms: int | None = None) -> HardwareSignalSample:
        started = time.perf_counter()
        hid = self._hid()
        if hid is None or not self.is_available():
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="unavailable",
                value=0.5,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={"provider": self.__class__.__name__},
            )
        if not self.allow_device_open:
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="fallback",
                value=0.5,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={"provider": self.__class__.__name__},
                error="device_open_disabled",
            )
        device = None
        timeout = max(1, int(timeout_ms or self.default_timeout_ms)) / 1000.0
        try:
            device = hid.device()
            device.open(self.vid, self.pid)
            device.set_nonblocking(True)
            buffer: list[int] = []
            while time.perf_counter() - started < timeout:
                data = device.read(64)
                if data:
                    buffer.extend(int(x) for x in data)
                time.sleep(0.002)
            if not buffer:
                return HardwareSignalSample(
                    source_id=self.provider_id,
                    source_type=self.provider_type,
                    status="fallback",
                    value=0.5,
                    duration_ms=(time.perf_counter() - started) * 1000.0,
                    metadata={"provider": self.__class__.__name__, "sample_count": 0},
                )
            mean = sum(buffer) / len(buffer)
            variance = sum((x - mean) ** 2 for x in buffer) / len(buffer)
            std = math.sqrt(max(variance, 0.0))
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="ok",
                value=clamp(std / 64.0),
                quality=clamp(len(buffer) / 128.0),
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={
                    "provider": self.__class__.__name__,
                    "sample_count": len(buffer),
                    "vid": self.vid,
                    "pid": self.pid,
                },
            )
        except Exception as exc:
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="error",
                value=0.5,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={"provider": self.__class__.__name__},
                error=str(exc),
            )
        finally:
            if device is not None:
                try:
                    device.close()
                except Exception:
                    pass


class TrueRngSignalProvider:
    provider_id = "truerng"
    provider_type = "serial"
    display_name = "TrueRNG Serial"
    default_timeout_ms = 75

    def __init__(
        self,
        *,
        list_ports_module: Any = "auto",
        serial_module: Any = "auto",
        allow_device_open: bool = False,
    ) -> None:
        self._list_ports_module = list_ports_module
        self._serial_module = serial_module
        self.allow_device_open = allow_device_open

    def _list_ports(self) -> Any:
        if self._list_ports_module != "auto":
            return self._list_ports_module
        try:
            from serial.tools import list_ports

            return list_ports
        except Exception:
            return None

    def _serial(self) -> Any:
        if self._serial_module != "auto":
            return self._serial_module
        try:
            import serial

            return serial
        except Exception:
            return None

    def _find_port(self) -> str | None:
        list_ports = self._list_ports()
        if list_ports is None:
            return None
        try:
            truerng_vids = {"04D8:F4FE", "16D0:0AA0"}
            for port in list_ports.comports():
                vid_pid = (
                    f"{port.vid:04X}:{port.pid:04X}"
                    if getattr(port, "vid", None) and getattr(port, "pid", None)
                    else ""
                )
                identity = " ".join(
                    str(part or "")
                    for part in (
                        getattr(port, "product", None),
                        getattr(port, "description", None),
                        getattr(port, "manufacturer", None),
                        getattr(port, "serial_number", None),
                    )
                )
                name_upper = identity.upper()
                has_truerng_identity = (
                    "TRUERNG" in name_upper or "TRUE RNG" in name_upper
                )
                if vid_pid in truerng_vids or has_truerng_identity:
                    return str(port.device)
        except Exception:
            return None
        return None

    def is_available(self) -> bool:
        return self._serial() is not None and self._find_port() is not None

    def sample(self, timeout_ms: int | None = None) -> HardwareSignalSample:
        started = time.perf_counter()
        serial = self._serial()
        port = self._find_port()
        if serial is None or port is None:
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="unavailable",
                value=0.5,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={"provider": self.__class__.__name__},
            )
        if not self.allow_device_open:
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="fallback",
                value=0.5,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={"provider": self.__class__.__name__, "port": port},
                error="device_open_disabled",
            )
        timeout = max(1, int(timeout_ms or self.default_timeout_ms)) / 1000.0
        handle = None
        try:
            handle = serial.Serial(port, baudrate=9600, timeout=timeout)
            data = handle.read(128)
            if len(data) < 16:
                return HardwareSignalSample(
                    source_id=self.provider_id,
                    source_type=self.provider_type,
                    status="fallback",
                    value=0.5,
                    duration_ms=(time.perf_counter() - started) * 1000.0,
                    metadata={
                        "provider": self.__class__.__name__,
                        "sample_count": len(data),
                    },
                )
            counts = [0] * 256
            for byte in data:
                counts[byte] += 1
            entropy = 0.0
            for count in counts:
                if count:
                    p = count / float(len(data))
                    entropy -= p * math.log2(p)
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="ok",
                value=clamp(entropy / 8.0),
                quality=clamp(len(data) / 128.0),
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={
                    "provider": self.__class__.__name__,
                    "sample_count": len(data),
                    "port": port,
                },
            )
        except Exception as exc:
            return HardwareSignalSample(
                source_id=self.provider_id,
                source_type=self.provider_type,
                status="error",
                value=0.5,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                metadata={"provider": self.__class__.__name__},
                error=str(exc),
            )
        finally:
            if handle is not None:
                try:
                    handle.close()
                except Exception:
                    pass


class HardwareDriverRegistry:
    def __init__(self, providers: list[HardwareSignalProvider]) -> None:
        self._providers = list(providers)

    @classmethod
    def default(cls, *, allow_device_open: bool = False) -> "HardwareDriverRegistry":
        return cls(
            [
                CpuTimingSignalProvider(),
                HidSignalProvider(allow_device_open=allow_device_open),
                TrueRngSignalProvider(allow_device_open=allow_device_open),
            ]
        )

    def list_statuses(self) -> list[HardwareProviderStatus]:
        statuses: list[HardwareProviderStatus] = []
        for provider in self._providers:
            try:
                available = bool(provider.is_available())
            except Exception:
                available = False
            statuses.append(
                HardwareProviderStatus(
                    provider_id=provider.provider_id,
                    provider_type=provider.provider_type,
                    display_name=provider.display_name,
                    available=available,
                    default_timeout_ms=provider.default_timeout_ms,
                )
            )
        return statuses

    def available_providers(self) -> list[HardwareSignalProvider]:
        return [
            provider
            for provider in self._providers
            if self._safe_available(provider)
        ]

    def get(self, provider_id: str) -> HardwareSignalProvider:
        for provider in self._providers:
            if provider.provider_id == provider_id:
                return provider
        raise KeyError(provider_id)

    def sample(
        self,
        provider_ids: list[str] | None = None,
        timeout_ms: int | None = None,
    ) -> list[HardwareSignalSample]:
        providers = (
            [self.get(provider_id) for provider_id in provider_ids]
            if provider_ids is not None
            else list(self._providers)
        )
        return [provider.sample(timeout_ms=timeout_ms) for provider in providers]

    def _safe_available(self, provider: HardwareSignalProvider) -> bool:
        try:
            return bool(provider.is_available())
        except Exception:
            return False


class CachedHardwareSampler:
    def __init__(
        self,
        registry: HardwareDriverRegistry,
        *,
        ttl_seconds: float = 2.0,
        timeout_ms: int = 75,
    ) -> None:
        self.registry = registry
        self.ttl_seconds = max(0.0, float(ttl_seconds))
        self.timeout_ms = max(1, int(timeout_ms))
        self._cache: dict[str, tuple[float, HardwareSignalSample]] = {}

    def sample(
        self, provider_ids: list[str] | None = None
    ) -> list[HardwareSignalSample]:
        ids = (
            [status.provider_id for status in self.registry.list_statuses()]
            if provider_ids is None
            else list(provider_ids)
        )
        return [self._sample_one(provider_id) for provider_id in ids]

    def _sample_one(self, provider_id: str) -> HardwareSignalSample:
        now = time.monotonic()
        cached = self._cache.get(provider_id)
        if cached is not None:
            cached_at, sample = cached
            if now - cached_at < self.ttl_seconds:
                return sample
        try:
            provider = self.registry.get(provider_id)
            sample = provider.sample(timeout_ms=self.timeout_ms)
        except Exception as exc:
            sample = HardwareSignalSample(
                source_id=provider_id,
                source_type="unknown",
                status="fallback",
                value=0.5,
                quality=0.0,
                metadata={"provider": "CachedHardwareSampler"},
                error=str(exc),
            )
        self._cache[provider_id] = (now, sample)
        return sample
