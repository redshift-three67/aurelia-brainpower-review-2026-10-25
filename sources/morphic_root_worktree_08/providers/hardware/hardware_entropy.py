from __future__ import annotations

"""Hardware-nahe Entropiemessungen für Morphic_Engine_V1.

Port der Radialgo2-Funktionen `sample_timer_jitter`, `sample_cpu_mem`,
`sample_h_level`, HID-Leser sowie der adaptiven h-Level-API, angepasst auf den
neuen Provider-Namespace.
"""

import os
import time
from math import isfinite
from typing import Dict

import numpy as np

try:  # pragma: no cover - optional psutil
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None

try:  # pragma: no cover - optional hid
    import hid  # type: ignore
except Exception:  # pragma: no cover
    hid = None

from .entropy_sources import select_entropy_source


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def sample_timer_jitter(duration_s: float = 2.0, target_samples: int = 5000) -> Dict[str, float]:
    """Misst Jitter über hochauflösenden Timer (perf_counter_ns).

    Liefert normierte Kennwerte in [0,1].
    """

    t0 = time.perf_counter_ns()
    stamps = []
    while True:
        stamps.append(time.perf_counter_ns())
        if len(stamps) >= target_samples:
            break
        if (stamps[-1] - t0) / 1e9 >= duration_s:
            break
    if len(stamps) < 3:
        return {"rel_jitter": 0.0, "entropy": 0.0}

    diffs = np.diff(np.array(stamps, dtype=np.int64)).astype(np.float64)
    med = float(np.median(diffs)) or 1.0
    sd = float(np.std(diffs))
    rel = sd / abs(med)

    if sd > 0:
        bins = max(10, min(256, int(len(diffs) ** 0.5)))
        hist, _ = np.histogram(diffs, bins=bins, density=True)
        p = hist[hist > 0]
        ent = -float(np.sum(p * np.log2(p))) / np.log2(bins)
    else:
        ent = 0.0

    rel_norm = rel / (rel + 1.0)
    ent_norm = _clamp(ent)
    return {"rel_jitter": _clamp(rel_norm), "entropy": ent_norm}


def sample_cpu_mem(duration_s: float = 1.5, interval_s: float = 0.2) -> Dict[str, float]:
    """Misst CPU- und RAM-Schwankungen mit psutil.

    Falls psutil fehlt, werden konservative kleine Werte zurückgegeben.
    """

    if psutil is None:
        return {"cpu_var": 0.05, "mem_var": 0.02}

    samples = int(max(1, duration_s / max(0.05, interval_s)))
    cpu_vals = []
    mem_vals = []
    for _ in range(samples):
        cpu_vals.append(float(psutil.cpu_percent(interval=interval_s)))
        try:
            mem_vals.append(float(psutil.virtual_memory().percent))
        except Exception:  # pragma: no cover
            mem_vals.append(0.0)

    cpu_arr = np.array(cpu_vals, dtype=np.float64)
    mem_arr = np.array(mem_vals, dtype=np.float64)

    cpu_std = float(np.std(cpu_arr))
    mem_std = float(np.std(mem_arr))

    cpu_norm = _clamp(cpu_std / 50.0)
    mem_norm = _clamp(mem_std / 20.0)
    return {"cpu_var": cpu_norm, "mem_var": mem_norm}


def sample_time_coherence(duration_s: float = 1.0, interval_s: float = 0.01) -> Dict[str, float]:
    """Misst die Kohärenz zwischen Hochauflöser und Wall-Clock.

    Orientiert sich am Kozyrev-Zeitdichte-Gedanken, indem Drift zwischen
    ``time.perf_counter`` und ``time.time`` auf kurzen Skalen gemessen wird.
    Liefert einen normierten Kohärenzwert in [0,1], wobei 1 hohe Kohärenz
    (geringe Drift) bedeutet.
    """

    if duration_s <= 0.0:
        return {"avg_drift": 0.0, "coherence": 0.5}

    t0_perf = time.perf_counter()
    t0_wall = time.time()

    drifts = []
    deadline = t0_perf + duration_s
    min_interval = max(0.001, interval_s)

    while True:
        now_perf = time.perf_counter()
        if now_perf >= deadline:
            break

        # Relativzeiten modulo 1s, um Langzeit-Offset zu entfernen
        perf_rel = (now_perf - t0_perf) % 1.0
        wall_rel = (time.time() - t0_wall) % 1.0
        drift = abs(perf_rel - wall_rel)
        drifts.append(drift)

        # Kurze Pause, um CPU-Last gering zu halten
        time.sleep(min_interval)

    if not drifts:
        return {"avg_drift": 0.0, "coherence": 0.5}

    avg_drift = float(np.mean(drifts))

    # Typische Drift wird im Millisekunden-Bereich erwartet.
    # Wir normalisieren mit einem konservativen 50ms-Skalenfaktor.
    scale = 0.050
    coherence = 1.0 - (avg_drift / scale)
    coherence = _clamp(coherence)

    return {"avg_drift": avg_drift, "coherence": coherence}


def sample_h_level(max_duration_s: float = 3.5) -> float:
    """Aggregiert mehrere Messgrößen in einen Modulationswert h∈[0,1]."""

    tj = sample_timer_jitter(duration_s=min(2.0, max_duration_s))
    cm = sample_cpu_mem(
        duration_s=min(1.5, max_duration_s - 0.5) if max_duration_s > 0.5 else 1.0
    )
    tc = sample_time_coherence(duration_s=min(1.5, max_duration_s))

    rel_j = tj.get("rel_jitter", 0.0)
    ent = tj.get("entropy", 0.0)
    cpu_v = cm.get("cpu_var", 0.0)
    mem_v = cm.get("mem_var", 0.0)
    coh = tc.get("coherence", 0.5)

    # Bewusst konservative Gewichtung: bestehende Struktur bleibt dominant,
    # Kohärenz steuert nur sanft nach.
    h = 0.35 * rel_j + 0.25 * ent + 0.25 * cpu_v + 0.10 * mem_v + 0.05 * coh
    if not isfinite(h):
        h = 0.0
    return _clamp(float(h))


def _spectral_entropy(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64).flatten()
    if x.size < 8:
        return 0.0
    x = x - np.mean(x)
    p = np.abs(np.fft.rfft(x)) ** 2
    if p.size <= 1:
        return 0.0
    p = p[1:]
    s = float(np.sum(p))
    if s <= 0:
        return 0.0
    p = p / s
    p = p[p > 0]
    H = -float(np.sum(p * np.log2(p)))
    Hmax = np.log2(len(p)) if len(p) > 0 else 1.0
    return float(_clamp(H / (Hmax or 1.0)))


def sample_hid_raw(
    vid: int = 0x0E50,
    pid: int = 0x0002,
    duration_s: float = 2.0,
    report_size: int = 64,
) -> dict:
    if hid is None:  # pragma: no cover
        return {"ok": False, "reason": "hid module not available"}
    dev = None
    try:
        dev = hid.device()
        dev.open(vid, pid)
        dev.set_nonblocking(True)
        t0 = time.perf_counter()
        buff = []
        while (time.perf_counter() - t0) < duration_s:
            try:
                data = dev.read(report_size)
            except Exception:  # pragma: no cover
                data = []
            if data:
                buff.extend(int(b) for b in data)
            time.sleep(0.005)
        arr = np.array(buff, dtype=np.float64)
        if arr.size == 0:
            return {"ok": False, "reason": "no data", "count": 0}
        std = float(np.std(arr))
        var = float(np.var(arr))
        ent = _spectral_entropy(arr)
        p95 = float(np.percentile(arr, 95)) or 1.0
        std_n = _clamp(std / (p95 + 1e-9))
        var_n = _clamp(var / ((p95 ** 2) + 1e-9))
        return {
            "ok": True,
            "count": int(arr.size),
            "std": std,
            "var": var,
            "std_norm": std_n,
            "var_norm": var_n,
            "entropy": ent,
        }
    except Exception as e:  # pragma: no cover
        return {"ok": False, "reason": str(e)}
    finally:
        try:
            if dev is not None:
                dev.close()
        except Exception:  # pragma: no cover
            pass


def sample_hid_level(vid: int = 0x0E50, pid: int = 0x0002, duration_s: float = 2.0) -> dict:
    """Liest HID-Rohdaten und bildet einen h-Level in [0,1]."""

    res = sample_hid_raw(vid=vid, pid=pid, duration_s=duration_s)
    if not res.get("ok"):
        return {"ok": False, "h_level": 0.0, **res}
    std_n = float(res.get("std_norm", 0.0))
    var_n = float(res.get("var_norm", 0.0))
    ent = float(res.get("entropy", 0.0))
    h = 0.45 * std_n + 0.15 * var_n + 0.40 * ent
    return {"ok": True, "h_level": _clamp(h), **res}


def get_adaptive_h_level(
    *,
    duration_s: float = 2.0,
    prefer_qrng: bool = False,
    allow_hid: bool = True,
    vid: int = 0x0E50,
    pid: int = 0x0002,
) -> float:
    """Liefert einen h-Level in [0,1] basierend auf verfügbarer Hardware.

    Der Modus wird über die Umgebungsvariable ``ME_ENTROPY_MODE`` gesteuert:

    - ``legacy`` (Standard):
        1. QRNG (falls installiert & ``prefer_qrng``)
        2. HID-Sensor (falls ``allow_hid`` und Gerät vorhanden)
        3. CPU-Timer / Systemjitter (Fallback)

    - ``enhanced``:
        1. QRNG (falls installiert & ``prefer_qrng``)
        2. TrueRNG (falls konfiguriert & gesund)
        3. HID-Sensor (falls ``allow_hid`` und Gerät vorhanden)
        4. Network-Quelle (falls ``ME_NETWORK_ENTROPY_URL`` gesetzt)
        5. CPU-Timer / Systemjitter (Fallback)
    """

    mode = (os.getenv("ME_ENTROPY_MODE") or "legacy").strip().lower()

    pref: list[str] = []
    if prefer_qrng:
        pref.append("qrng")

    if mode == "enhanced":
        # Externe, hochwertige Quellen priorisieren, falls verfügbar.
        pref.append("truerng")
        if allow_hid:
            pref.append("hid_sensor")
        pref.append("network")
    else:
        # Bisheriges Standardverhalten: HID vor CPU, kein Netzwerk.
        if allow_hid:
            pref.append("hid_sensor")

    pref.append("cpu_timer")

    src = select_entropy_source(preferred=pref)

    try:
        return _clamp(src.sample_h_level(duration_s=duration_s))
    except Exception:  # pragma: no cover
        return _clamp(sample_h_level(max_duration_s=duration_s))
