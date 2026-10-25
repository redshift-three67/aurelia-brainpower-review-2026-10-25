"""
Unified Sensor API für Radialgo2 Morphic Engine.
Verwaltet externe Hardware-Sensoren (USB/HID, Serial, Network) und Quanten-Entropie.
"""

import time
import abc
from typing import Dict, Any, List, Optional
import numpy as np

# Importiere das neue High-End Entropie Modul
try:
    from . import entropy
    ENTROPY_MODULE_AVAILABLE = True
except ImportError:
    ENTROPY_MODULE_AVAILABLE = False

# Versuche HID zu importieren
try:
    import hid
except ImportError:
    hid = None

class Sensor(abc.ABC):
    """Abstrakte Basisklasse für alle Sensoren."""
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def sensor_type(self) -> str:
        """z.B. 'usb_hid', 'serial', 'network', 'system'"""
        pass

    @property
    @abc.abstractmethod
    def is_available(self) -> bool:
        pass

    @abc.abstractmethod
    def read_entropy(self, duration_s: float = 1.0) -> Dict[str, float]:
        """Liest Entropie-Daten vom Sensor."""
        pass


class HIDSensor(Sensor):
    """Treiber für USB-HID Sensoren (z.B. Edelstein-Sensor)."""
    
    def __init__(self, vid: int = 0x0E50, pid: int = 0x0002, name: str = "Generic HID"):
        self._vid = vid
        self._pid = pid
        self._name = name
        
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def sensor_type(self) -> str:
        return "usb_hid"

    @property
    def is_available(self) -> bool:
        if hid is None:
            return False
        try:
            # Prüfe ob Gerät gelistet wird
            for d in hid.enumerate():
                if d['vendor_id'] == self._vid and d['product_id'] == self._pid:
                    return True
            return False
        except Exception:
            return False

    def read_entropy(self, duration_s: float = 1.0) -> Dict[str, float]:
        if not self.is_available:
            return {"ok": 0.0, "val": 0.0}
            
        try:
            dev = hid.device()
            dev.open(self._vid, self._pid)
            dev.set_nonblocking(True)
            
            buff = []
            t0 = time.perf_counter()
            while (time.perf_counter() - t0) < duration_s:
                data = dev.read(64)
                if data:
                    buff.extend(data)
                time.sleep(0.005)
            
            dev.close()
            
            if not buff:
                return {"ok": 1.0, "val": 0.0} # Verbunden aber keine Daten
                
            arr = np.array(buff, dtype=np.float64)
            std = float(np.std(arr))
            # Einfache Normalisierung
            val = min(1.0, std / 50.0) 
            return {"ok": 1.0, "val": val, "raw_std": std}
            
        except Exception as e:
            return {"ok": 0.0, "error": str(e)}


class TrueRandomSensor(Sensor):
    """Virtueller Sensor, der das entropy.py Modul (AMD Zen Jitter) kapselt."""
    
    def __init__(self):
        self._name = "AMD Zen Entropy Source"

    @property
    def name(self) -> str:
        return self._name

    @property
    def sensor_type(self) -> str:
        return "system_truerng"

    @property
    def is_available(self) -> bool:
        return ENTROPY_MODULE_AVAILABLE

    def read_entropy(self, duration_s: float = 1.0) -> Dict[str, float]:
        if not self.is_available:
            return {"ok": 0.0, "val": 0.5}
        
        # Wir rufen get_true_random auf. Da dies sehr schnell geht,
        # nutzen wir duration_s ggf. um zu warten, falls nötig.
        # Hier: Sofort-Wert.
        val = entropy.get_true_random()
        return {"ok": 1.0, "val": val}


class SensorManager:
    """Verwaltet alle registrierten Sensoren."""
    
    def __init__(self, use_legacy_only: bool = False):
        self.sensors: List[Sensor] = []
        self.use_legacy_only = use_legacy_only
        self._register_defaults()
        
    def _register_defaults(self):
        # 1. Hardware HID (Priorität, wenn Hand aufliegt)
        self.sensors.append(HIDSensor(vid=0x0E50, pid=0x0002, name="Trigonal Sensor"))
        
        # 2. TrueRNG / Zen Jitter (Basis-Feld)
        # Nur hinzufügen, wenn wir nicht im Legacy-Modus sind
        if not self.use_legacy_only and ENTROPY_MODULE_AVAILABLE:
            self.sensors.append(TrueRandomSensor())
        
    def list_available_sensors(self) -> List[Dict[str, str]]:
        found = []
        for s in self.sensors:
            if s.is_available:
                found.append({
                    "name": s.name,
                    "type": s.sensor_type
                })
        return found

    def get_combined_entropy(self) -> float:
        """
        Liest alle verfügbaren Sensoren und kombiniert die Werte.
        Strategie:
        - TrueRNG liefert das 'Trägerrauschen' (Basis).
        - HID liefert 'Modulation' (Klienten-Kontakt).
        """
        hid_val = 0.0
        truerng_val = 0.5 # Neutral
        
        has_hid = False
        has_truerng = False
        
        for s in self.sensors:
            if s.is_available:
                # Kurze Messung für HID, Sofort für TrueRNG
                duration = 0.5 if s.sensor_type == "usb_hid" else 0.0
                res = s.read_entropy(duration_s=duration)
                
                if res.get("ok"):
                    val = res.get("val", 0.0)
                    if s.sensor_type == "usb_hid":
                        hid_val = val
                        has_hid = True
                    elif s.sensor_type == "system_truerng":
                        truerng_val = val
                        has_truerng = True
        
        # FUSION LOGIK
        if has_hid and has_truerng:
            # Wenn Hand aufliegt, moduliert sie das Quantenfeld
            # Wir nutzen eine gewichtete Mischung
            return (truerng_val * 0.7) + (hid_val * 0.3)
        
        if has_truerng:
            return truerng_val
            
        if has_hid:
            return hid_val
            
        # Fallback
        return 0.5
