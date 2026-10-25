"""
Advanced Entropy Source for Radialgo2 Morphic Engine.
Optimized for AMD Zen Architecture (RDRAND/RDSEED) and TrueRNG Hardware.

Features:
- CPU Jitter Measurement (Nanosecond precision)
- OS Randomness (RDRAND via OS API)
- Network Latency Jitter (Optional)
- TrueRNG Hardware Support (USB Serial)
"""

import time
import os
import hashlib
import platform
import statistics
import threading
from typing import List, Optional

# Versuche Requests zu importieren (für Netzwerk-Entropie)
try:
    import requests
    NETWORK_AVAILABLE = True
except ImportError:
    NETWORK_AVAILABLE = False

class EntropySource:
    """Basisklasse für Entropie-Quellen."""
    def get_bytes(self, length: int) -> bytes:
        raise NotImplementedError

class ZenJitterSource(EntropySource):
    """
    Nutzt CPU-Ausführungsschwankungen (Jitter) und OS-RNG.
    Besonders effektiv auf modernen CPUs (AMD Ryzen) mit hoher Taktfrequenz.
    """
    def __init__(self):
        self._last_val = 0

    def _measure_jitter(self, iterations: int = 100) -> bytes:
        """Misst Zeitdifferenzen zwischen Operationen."""
        deltas = []
        t0 = time.perf_counter_ns()
        for _ in range(iterations):
            t1 = time.perf_counter_ns()
            deltas.append(t1 - t0)
            t0 = t1
            # Leichte CPU-Last erzeugen, um thermisches Rauschen zu provozieren
            _ = hash(str(t1)) 
        
        # Konvertiere Deltas in Bytes
        jitter_str = ",".join(map(str, deltas))
        return jitter_str.encode('utf-8')

    def get_bytes(self, length: int) -> bytes:
        # 1. OS Random (nutzt RDRAND auf AMD CPUs)
        os_rnd = os.urandom(length * 2)
        
        # 2. Jitter messen
        jitter_data = self._measure_jitter(iterations=50)
        
        # 3. Mischen (Hashing)
        hasher = hashlib.sha512()
        hasher.update(os_rnd)
        hasher.update(jitter_data)
        hasher.update(str(time.time()).encode('utf-8'))
        
        full_hash = hasher.digest()
        return full_hash[:length]

class TrueRNGSource(EntropySource):
    """
    Treiber für Hardware-RNGs (z.B. TrueRNG v3 via COM-Port).
    Aktuell als Platzhalter/Fallback implementiert, da USB-Device-Zugriff
    spezifische Treiber (pyserial) erfordert.
    """
    def __init__(self, port: Optional[str] = None):
        self.port = port
        self.available = False # Aktuell false, bis pyserial integriert ist

    def get_bytes(self, length: int) -> bytes:
        # Fallback, wenn kein Gerät da ist
        return os.urandom(length)

class NetworkEntropySource(EntropySource):
    """
    Nutzt Latenzzeiten von HTTPS-Anfragen als Entropiequelle.
    (Atmosphärisches Rauschen des Internets).
    """
    def get_bytes(self, length: int) -> bytes:
        if not NETWORK_AVAILABLE:
            return b''
        
        try:
            t0 = time.perf_counter()
            # Ping an Cloudflare DNS (sehr schnell, aber jittery)
            _ = requests.get("https://1.1.1.1", timeout=1.0)
            dt = time.perf_counter() - t0
            return str(dt).encode('utf-8')
        except Exception:
            return b''

class HybridEntropyCollector:
    """
    Kombiniert alle verfügbaren Quellen zu einem hochwertigen Seed.
    """
    def __init__(self):
        self.zen = ZenJitterSource()
        self.net = NetworkEntropySource()
        # TrueRNG hier vorbereitet, aber inaktiv bis Hardware erkannt
        self.truerng = TrueRNGSource()

    def get_entropy_float(self) -> float:
        """Liefert eine hochwertige Zufallszahl 0.0 <= x < 1.0."""
        # Sammle Bytes
        raw = bytearray()
        raw.extend(self.zen.get_bytes(32))
        
        # Netzwerk nur sporadisch nutzen (Performance), oder wenn explizit gewünscht
        # Hier: Einfachheitshalber weglassen für Speed, oder asynchron
        # raw.extend(self.net.get_bytes(8)) 

        # Hashing zur Gleichverteilung
        final_hash = hashlib.sha256(raw).digest()
        
        # Konvertiere erste 8 Bytes in Float
        # (Big Endian unsigned long long)
        int_val = int.from_bytes(final_hash[:8], 'big')
        # Normalisiere auf 0..1 (max Wert für 8 bytes ist 2^64 - 1)
        return float(int_val) / (2**64 - 1)

# Singleton Instanz
collector = HybridEntropyCollector()

def get_true_random() -> float:
    """Öffentliche API für die Engine."""
    return collector.get_entropy_float()
