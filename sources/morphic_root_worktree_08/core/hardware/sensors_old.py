"""
Unified Sensor API für Radialgo2 Morphic Engine.
Verwaltet externe Hardware-Sensoren (USB/HID, Serial, Network).
"""

import time
import abc
from typing import Dict, Any, List, Optional
import numpy as np

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
        """z.B. 'usb_hid', 'serial', 'network'"""
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


class SensorManager:
    """Verwaltet alle registrierten Sensoren."""
    
    def __init__(self):
        self.sensors: List[Sensor] = []
        self._register_defaults()
        
    def _register_defaults(self):
        # Standard Edelstein/Trigonal Sensor
        self.sensors.append(HIDSensor(vid=0x0E50, pid=0x0002, name="Trigonal Sensor"))
        # Hier könnten später Kozyrev-Sensoren registriert werden
        
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
        """Liest alle verfügbaren Sensoren und kombiniert die Werte."""
        vals = []
        for s in self.sensors:
            if s.is_available:
                res = s.read_entropy(duration_s=0.5)
                if res.get("ok"):
                    vals.append(res.get("val", 0.0))
        
        if not vals:
            return 0.0
        return float(np.mean(vals))
