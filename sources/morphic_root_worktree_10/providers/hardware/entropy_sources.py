from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np


try:
    import cupy  # type: ignore
except Exception:  # pragma: no cover - optional GPU dependency
    cupy = None


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


class EntropySource(ABC):
    @abstractmethod
    def sample_h_level(self, duration_s: float = 2.0) -> float:
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    def healthy(self) -> bool:
        return True


class CpuTimerSource(EntropySource):
    def name(self) -> str:
        return "cpu_timer"

    def sample_h_level(self, duration_s: float = 2.0) -> float:
        from providers.hardware import hardware_entropy

        return hardware_entropy.sample_h_level(max_duration_s=duration_s)


class HidSource(EntropySource):
    """HID-Sensor Entropie-Quelle.

    Verbindet sich zu HID-Geraeten (VID:0x0E50, PID:0x0002)
    ueber die `hid` library und liest Sensor-Daten als Entropie.
    """

    def __init__(self, vid: int = 0x0E50, pid: int = 0x0002):
        self.vid = vid
        self.pid = pid

    def name(self) -> str:
        return "hid_sensor"

    def _find_device(self) -> dict | None:
        """Sucht nach verfuegbaren HID-Geraeten mit passender VID/PID."""
        try:
            import hid

            devices = hid.enumerate(self.vid, self.pid)
            if devices:
                return devices[0]
        except ImportError:
            pass
        except Exception:
            pass
        return None

    def healthy(self) -> bool:
        return self._find_device() is not None

    def sample_h_level(self, duration_s: float = 2.0) -> float:
        device = self._find_device()
        if not device:
            return 0.0
        try:
            import hid

            h = hid.device()
            h.open(self.vid, self.pid)
            h.set_nonblocking(True)
            # Lese Daten fuer duration_s Sekunden
            data_chunks: list[bytes] = []
            end_time = time.perf_counter() + duration_s
            while time.perf_counter() < end_time:
                data = h.read(64, timeout_ms=100)
                if data:
                    data_chunks.append(bytes(data))
            h.close()

            if not data_chunks:
                return 0.0

            all_data = b"".join(data_chunks)
            if len(all_data) < 32:
                return 0.0

            arr = np.frombuffer(all_data, dtype=np.uint8).astype(float)
            shannon = -np.sum((arr / 256.0) * np.log2(arr / 256.0 + 1e-12))
            return _clamp(float(shannon / 8.0))
        except Exception:
            return 0.0


class TrueRngSource(EntropySource):
    """USB TrueRNG Hardware-Entropie-Quelle.

    Erkennt TrueRNG/TrueRNGpro Geraete an Serial-Ports.
    Wenn kein Geraet gefunden wird, ist healthy()=False.
    """

    def name(self) -> str:
        return "truerng"

    def _find_truerng_port(self) -> str | None:
        """Sucht nach TrueRNG Serial-Ports."""
        try:
            from serial.tools import list_ports

            # TrueRNG USB Vendor/Product IDs
            # TrueRNG: 0x0403:0x6001 (FTDI), 0x04D8:0xF4FE (Microchip)
            truerng_vids = {"0403:6001", "04D8:F4FE", "16D0:0AA0"}
            for port in list_ports.comports():
                vid_pid = f"{port.vid:04X}:{port.pid:04X}" if port.vid and port.pid else ""
                if vid_pid in truerng_vids:
                    return port.device
                # Fallback: Name-basierte Erkennung
                name_upper = (port.product or port.description or "").upper()
                if "TRUERNG" in name_upper or "TRUE RNG" in name_upper:
                    return port.device
        except ImportError:
            pass
        except Exception:
            pass
        return None

    def healthy(self) -> bool:
        return self._find_truerng_port() is not None

    def sample_h_level(self, duration_s: float = 1.0) -> float:
        port = self._find_truerng_port()
        if not port:
            return 0.0
        try:
            import serial

            ser = serial.Serial(port, baudrate=9600, timeout=duration_s)
            data = ser.read(256)
            ser.close()
            if len(data) < 32:
                return 0.0
            arr = np.frombuffer(data, dtype=np.uint8).astype(float)
            shannon = -np.sum((arr / 256.0) * np.log2(arr / 256.0 + 1e-12))
            return _clamp(float(shannon / 8.0))
        except Exception:
            return 0.0


class QrngSource(EntropySource):
    def name(self) -> str:
        return "qrng"

    def healthy(self) -> bool:
        return False

    def sample_h_level(self, duration_s: float = 1.0) -> float:
        return 0.0


class GpuSource(EntropySource):
    def name(self) -> str:
        return "gpu"

    def healthy(self) -> bool:
        if cupy is None:
            return False
        try:  # pragma: no cover - depends on CUDA host state
            from cupy.cuda import runtime  # type: ignore

            return runtime.getDeviceCount() > 0
        except Exception:
            return False

    def sample_h_level(self, duration_s: float = 1.5) -> float:
        if not self.healthy():
            return 0.0
        try:  # pragma: no cover - depends on CUDA host state
            from cupy.cuda import Stream  # type: ignore

            n = 64
            reps = max(5, int(duration_s * 5))
            a = cupy.random.rand(n, n, dtype=cupy.float32)
            b = cupy.random.rand(n, n, dtype=cupy.float32)
            Stream.null.synchronize()
            times: List[float] = []
            for _ in range(reps):
                start = time.perf_counter()
                _ = a @ b
                Stream.null.synchronize()
                times.append(time.perf_counter() - start)
            arr = np.asarray(times, dtype=np.float64)
            mean = float(np.mean(arr)) or 1.0
            rel = float(np.std(arr)) / abs(mean)
            return _clamp(rel / (rel + 1.0))
        except Exception:
            return 0.0


class NetworkSource(EntropySource):
    """Misst Network-Timing-Jitter als Entropie-Quelle.

    Verbindet sich zu einem NTP-Server (pool.ntp.org:123) oder
    DNS-Server (8.8.8.8:53) und misst die Round-Trip-Time-Variation.
    Die Variation der RTTs ist eine gute Zufallsquelle.
    """

    def name(self) -> str:
        return "network"

    def healthy(self) -> bool:
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.5)
            # Test: DNS-Server erreichbar?
            sock.connect(("8.8.8.8", 53))
            sock.close()
            return True
        except Exception:
            return False

    def sample_h_level(self, duration_s: float = 1.0) -> float:
        if not self.healthy():
            return 0.0
        try:
            import socket
            import time

            rtts: list[float] = []
            n_samples = max(5, int(duration_s * 5))
            for _ in range(n_samples):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1.0)
                try:
                    t0 = time.perf_counter_ns()
                    # Sende ein leeres UDP-Paket an DNS-Port
                    sock.sendto(b"\x00", ("8.8.8.8", 53))
                    # Warte nicht auf Antwort - nur Senden kostet Zeit
                    sock.close()
                    t1 = time.perf_counter_ns()
                    rtts.append((t1 - t0) / 1e6)  # ms
                except Exception:
                    sock.close()
                    continue
                time.sleep(0.01)

            if len(rtts) < 3:
                return 0.0

            arr = np.asarray(rtts, dtype=np.float64)
            mean = float(np.mean(arr)) or 1.0
            rel = float(np.std(arr)) / abs(mean)
            return _clamp(rel / (rel + 1.0))
        except Exception:
            return 0.0


class MockSource(EntropySource):
    def __init__(self, fixed_h: float = 0.3):
        self.fixed_h = _clamp(fixed_h)

    def name(self) -> str:
        return "mock"

    def sample_h_level(self, duration_s: float = 0.1) -> float:
        return self.fixed_h


def select_entropy_source(preferred: Optional[List[str]] = None) -> EntropySource:
    order = preferred or ["qrng", "truerng", "hid_sensor", "network", "cpu_timer"]
    for key in order:
        if key == "qrng":
            source = QrngSource()
        elif key == "truerng":
            source = TrueRngSource()
        elif key == "gpu":
            source = GpuSource()
        elif key == "network":
            source = NetworkSource()
        elif key == "hid_sensor":
            source = HidSource()
        elif key == "cpu_timer":
            return CpuTimerSource()
        else:
            continue

        if source.healthy():
            return source
    return CpuTimerSource()
