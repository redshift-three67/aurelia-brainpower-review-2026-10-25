from __future__ import annotations

"""Hardware-/Software-unabhängige Entropiequellen für Morphic_Engine_V1.

Port der Radialgo2-Logik mit angepasstem Modulpfad, so dass die neue
Architektur einen eigenen Provider-Layer erhält, ohne die alte Implementierung
zu verändern.
"""

import importlib
import os
import sys
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, List

import urllib.request
from urllib.parse import urlparse
import numpy as np


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


# Lazy-Loader für das passende hardware_entropy-Modul innerhalb des
# Morphic_Engine_V1-Provider-Pakets.


def _he():
    module_name = "providers.hardware.hardware_entropy"
    if module_name in sys.modules:
        return sys.modules[module_name]
    return importlib.import_module(module_name)


try:  # pragma: no cover - optionales HID-Modul
    import hid  # type: ignore
except Exception:  # pragma: no cover
    hid = None

# QRNG (Quantis) optional
try:  # pragma: no cover - optionales QRNG-Modul
    import pyqrng  # type: ignore
except Exception:  # pragma: no cover
    pyqrng = None

# TrueRNG (USB Serial) optional
try:  # pragma: no cover - optionales pyserial-Modul
    import serial  # type: ignore
except Exception:  # pragma: no cover
    serial = None

# GPU (CuPy/CUDA) optional – primär für Debian/NVIDIA-Serverprofile
try:  # pragma: no cover - optionales CuPy-Modul
    import cupy  # type: ignore
except Exception:  # pragma: no cover
    cupy = None


class EntropySource(ABC):
    """Abstrakte Basis für alle Entropiequellen."""

    @abstractmethod
    def sample_h_level(self, duration_s: float = 2.0) -> float:
        """Liefert h∈[0,1]."""

    @abstractmethod
    def name(self) -> str:
        """Short identifier for logging."""

    def healthy(self) -> bool:
        """Kann überladen werden, um Verfügbarkeit zu prüfen."""
        return True


class CpuTimerSource(EntropySource):
    def name(self) -> str:
        return "cpu_timer"

    def sample_h_level(self, duration_s: float = 2.0) -> float:
        he = _he()
        tj = he.sample_timer_jitter(duration_s=duration_s)
        cm = he.sample_cpu_mem(duration_s=max(1.0, duration_s - 0.5))
        try:
            tc = he.sample_time_coherence(duration_s=min(1.5, duration_s))
        except Exception:
            tc = {"coherence": 0.5}

        ent = tj.get("entropy", 0.0)
        rel_j = tj.get("rel_jitter", 0.0)
        cpu_v = cm.get("cpu_var", 0.0)
        mem_v = cm.get("mem_var", 0.0)
        coh = tc.get("coherence", 0.5)

        # Konservative Gewichtung: Time-Coherence ergänzt den bestehenden Mix,
        # ohne ihn zu dominieren. Alle Terme bleiben im Bereich [0,1].
        h = 0.45 * ent + 0.25 * rel_j + 0.15 * cpu_v + 0.05 * mem_v + 0.10 * coh
        return _clamp(float(h))


class HidSource(EntropySource):
    def __init__(self, vid: int = 0x0E50, pid: int = 0x0002):
        self.vid = vid
        self.pid = pid

    def name(self) -> str:
        return "hid_sensor"

    def healthy(self) -> bool:
        if hid is None:
            return False
        try:
            for dev in hid.enumerate():
                if dev.get("vendor_id") == self.vid and dev.get("product_id") == self.pid:
                    return True
        except Exception:  # pragma: no cover
            return False
        return False

    def sample_h_level(self, duration_s: float = 2.0) -> float:
        he = _he()
        res = he.sample_hid_level(vid=self.vid, pid=self.pid, duration_s=duration_s)
        if res.get("ok"):
            return float(res.get("h_level", 0.0))
        return 0.0

class TrueRngSource(EntropySource):
    """Externe TrueRNG-Geräte via USB-Serial (optional).

    Nutzt pyserial, falls verfügbar. Port wird über die Umgebungsvariable
    ME_TRUERNG_PORT konfiguriert (z.B. "COM4" oder "/dev/ttyACM0").
    """

    def __init__(self, port: Optional[str] = None):
        self.port = (port or os.getenv("ME_TRUERNG_PORT") or "").strip()

    def name(self) -> str:
        return "truerng"

    def healthy(self) -> bool:
        if serial is None or not self.port:
            return False
        try:  # pragma: no cover - hardwareabhängig
            with serial.Serial(self.port, 115200, timeout=0.5) as ser:  # type: ignore[attr-defined]
                data = ser.read(8)
                return bool(data)
        except Exception:
            return False

    def sample_h_level(self, duration_s: float = 1.0) -> float:
        if serial is None or not self.port:
            return 0.0
        try:  # pragma: no cover - hardwareabhängig
            n = int(max(256, duration_s * 512))
            with serial.Serial(self.port, 115200, timeout=1.0) as ser:  # type: ignore[attr-defined]
                data = ser.read(n)
            if not data:
                return 0.0
            arr = np.frombuffer(data, dtype=np.uint8).astype(np.float64)
            if arr.size < 8:
                return 0.0
            ent = _spectral_entropy(arr)
            std_n = _clamp(float(np.std(arr)) / 64.0)
            h = 0.6 * ent + 0.4 * std_n
            return _clamp(float(h))
        except Exception:
            return 0.0


class QrngSource(EntropySource):
    """Quantis USB / QRNG-Geräte via pyqrng (falls vorhanden)."""

    def name(self) -> str:
        return "qrng"

    def healthy(self) -> bool:
        return pyqrng is not None

    def sample_h_level(self, duration_s: float = 1.0) -> float:
        if pyqrng is None:
            return 0.0
        try:
            n = int(max(128, duration_s * 256))
            data = pyqrng.get_random_data(n)  # returns bytes
            if not data:
                return 0.0
            arr = np.frombuffer(data, dtype=np.uint8).astype(np.float64)
            ent = _spectral_entropy(arr)
            std_n = _clamp(float(np.std(arr)) / 128.0)
            h = 0.6 * ent + 0.4 * std_n
            return _clamp(h)
        except Exception:  # pragma: no cover
            return 0.0


class GpuSource(EntropySource):
    """GPU-basierte Entropiequelle über CuPy/CUDA (falls vorhanden).

    Diese Implementierung ist bewusst konservativ und wird nur auf Systemen
    aktiv, auf denen CuPy installiert ist und mindestens ein CUDA-Device
    verfügbar ist. Andernfalls meldet ``healthy()`` False, so dass
    ``select_entropy_source`` automatisch auf CPU-Timer zurückfällt.
    """

    def name(self) -> str:
        return "gpu"

    def healthy(self) -> bool:
        if cupy is None:
            return False
        try:
            # Import innerhalb der Funktion, um harte Abhängigkeiten zu vermeiden.
            from cupy.cuda import runtime  # type: ignore

            return runtime.getDeviceCount() > 0
        except Exception:  # pragma: no cover
            return False

    def sample_h_level(self, duration_s: float = 1.5) -> float:
        if cupy is None:
            return 0.0
        try:
            from cupy.cuda import Stream  # type: ignore
        except Exception:  # pragma: no cover
            return 0.0

        try:
            # Ein sehr kleiner, wiederholter Matrix-Workload auf der GPU, um
            # Laufzeitjitter zu messen. Dimension und Wiederholungen sind
            # konservativ gewählt, um die Laufzeit zu begrenzen.
            n = 64
            reps = max(5, int(duration_s * 5))

            a = cupy.random.rand(n, n, dtype=cupy.float32)
            b = cupy.random.rand(n, n, dtype=cupy.float32)
            Stream.null.synchronize()

            times: List[float] = []
            for _ in range(reps):
                t0 = time.perf_counter()
                c = a @ b  # noqa: F841 - Ergebnis wird nur zur Last-Erzeugung genutzt
                Stream.null.synchronize()
                t1 = time.perf_counter()
                times.append(t1 - t0)

            if len(times) < 3:
                return 0.0

            arr = np.asarray(times, dtype=np.float64)
            mean = float(np.mean(arr)) or 1.0
            std = float(np.std(arr))

            # Relativer Jitter: höherer Jitter -> höherer h-Level
            rel = std / abs(mean)
            rel_norm = rel / (rel + 1.0)
            return _clamp(float(rel_norm))
        except Exception:  # pragma: no cover
            return 0.0


class NetworkSource(EntropySource):
    # Default-URLs für Network-Entropy (schnelle, zuverlässige Endpoints)
    DEFAULT_URLS = [
        "https://www.google.com",
        "https://cloudflare.com",
        "https://www.microsoft.com",
    ]
    
    def __init__(self, url: Optional[str] = None):
        self.url = (url or os.getenv("ME_NETWORK_ENTROPY_URL") or "").strip()
        if not self.url:
            # Verwende Default-URL wenn keine konfiguriert
            self.url = self.DEFAULT_URLS[0]

    def name(self) -> str:
        return "network"

    def healthy(self) -> bool:
        return bool(self.url)

    def sample_h_level(self, duration_s: float = 1.0) -> float:
        if not self.url:
            return 0.0

        parsed = urlparse(self.url)
        scheme = (parsed.scheme or "").lower()

        ws_mod = None
        if scheme in ("ws", "wss"):
            try:  # pragma: no cover - optionales WebSocket-Modul
                import websocket as _ws  # type: ignore
            except Exception:
                return 0.0
            ws_mod = _ws

        # Versuche requests-Modul falls verfügbar (robuster als urllib)
        requests_mod = None
        try:
            import requests as _requests  # type: ignore
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            requests_mod = _requests
        except Exception:
            pass

        max_probes = 16
        n = max(6, min(max_probes, int(duration_s * 5)))
        times: List[float] = []
        for i in range(n):
            t0 = time.perf_counter()
            try:
                if ws_mod is not None:
                    ws = ws_mod.create_connection(self.url, timeout=1.5)
                    try:
                        ws.send("ping")
                        ws.recv()
                    finally:
                        ws.close()
                elif requests_mod is not None:
                    # requests-Modul ist robuster für HTTPS
                    resp = requests_mod.head(self.url, timeout=1.5, verify=False)
                    _ = resp.status_code
                else:
                    sep = "&" if "?" in self.url else "?"
                    url = f"{self.url}{sep}ping={i}"
                    import ssl
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    with urllib.request.urlopen(url, timeout=1.5, context=ctx) as resp:
                        resp.read(1)
            except Exception:
                continue
            t1 = time.perf_counter()
            times.append(t1 - t0)
        if len(times) < 3:
            return 0.0
        arr = np.asarray(times, dtype=np.float64)
        mean = float(np.mean(arr)) or 1.0
        std = float(np.std(arr))
        rel = std / abs(mean)
        rel_norm = rel / (rel + 1.0)
        return _clamp(float(rel_norm))


class MockSource(EntropySource):
    def __init__(self, fixed_h: float = 0.3):
        self.fixed_h = _clamp(fixed_h)

    def name(self) -> str:
        return "mock"

    def sample_h_level(self, duration_s: float = 0.1) -> float:
        return self.fixed_h


def _spectral_entropy(arr: np.ndarray) -> float:
    x = arr.astype(np.float64)
    if x.size < 8:
        return 0.0
    x -= np.mean(x)
    p = np.abs(np.fft.rfft(x)) ** 2
    p = p[1:]
    if p.size == 0:
        return 0.0
    p_sum = float(np.sum(p))
    if p_sum <= 0:
        return 0.0
    p = p / p_sum
    p = p[p > 0]
    H = -float(np.sum(p * np.log2(p)))
    Hmax = np.log2(len(p)) if len(p) > 0 else 1.0
    return _clamp(H / (Hmax or 1.0))


def select_entropy_source(preferred: Optional[List[str]] = None) -> EntropySource:
    """Wählt die beste verfügbare Quelle nach Wunschliste oder Standardreihenfolge."""

    order = preferred or ["qrng", "truerng", "hid_sensor", "network", "cpu_timer"]
    for key in order:
        if key == "qrng":
            qs = QrngSource()
            if qs.healthy():
                return qs
        if key == "truerng":
            ts = TrueRngSource()
            if ts.healthy():
                return ts
        if key == "gpu":
            gs = GpuSource()
            if gs.healthy():
                return gs
        if key == "network":
            ns = NetworkSource()
            if ns.healthy():
                return ns
        if key == "hid_sensor":
            hs = HidSource()
            if hs.healthy():
                return hs
        if key == "cpu_timer":
            return CpuTimerSource()
    return CpuTimerSource()
