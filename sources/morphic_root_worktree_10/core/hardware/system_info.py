"""
Hardware Detection Layer für Radialgo2 Morphic Engine V1.
Analysiert die Umgebung (OS, CPU, GPU, Sensoren) und liefert ein Systemprofil.
"""

import platform
import psutil
import os
import sys
from typing import Dict, Any, Optional
from . import accel_numpy
from .sensors import SensorManager

# Konstanten für Systemprofile
PROFILE_WINDOWS_DEV = "windows_dev_pc"
PROFILE_LINUX_SERVER = "linux_root_server"
PROFILE_UNKNOWN = "generic"

def get_os_info() -> Dict[str, str]:
    """Liefert Informationen zum Betriebssystem."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

def get_cpu_info() -> Dict[str, Any]:
    """Liefert Informationen zur CPU (Kerne, Auslastung)."""
    try:
        freq = psutil.cpu_freq()
        freq_max = freq.max if freq else 0.0
    except Exception:
        freq_max = 0.0

    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "frequency_max": freq_max,
        "usage_percent": psutil.cpu_percent(interval=0.1),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
    }

def get_gpu_info() -> Dict[str, Any]:
    """Prüft GPU-Verfügbarkeit via accel_numpy (CuPy)."""
    has_gpu = accel_numpy.use_gpu()
    # Wir schalten danach wieder auf CPU zurück, um Seiteneffekte beim Start zu vermeiden,
    # es sei denn, die Engine fordert es explizit an.
    accel_numpy.set_backend("numpy") 
    
    return {
        "has_gpu": has_gpu,
        "backend": "cupy" if has_gpu else "numpy",
        "device_name": "NVIDIA/AMD GPU" if has_gpu else "CPU fallback"
    }

def get_sensor_info() -> Dict[str, Any]:
    """Prüft verfügbare externe Sensoren."""
    try:
        mgr = SensorManager()
        found = mgr.list_available_sensors()
        return {
            "count": len(found),
            "devices": found
        }
    except Exception:
        return {"count": 0, "devices": [], "error": "Sensor detection failed"}

def detect_system_profile() -> str:
    """
    Entscheidet basierend auf OS und Hardware, welches Profil geladen werden soll.
    """
    os_name = platform.system().lower()
    
    if "windows" in os_name:
        return PROFILE_WINDOWS_DEV
    elif "linux" in os_name:
        # Unterscheidung Desktop vs Server könnte man über GUI-Check machen,
        # aber für jetzt nehmen wir an: Linux = Server (gemäß Masterplan)
        return PROFILE_LINUX_SERVER
    
    return PROFILE_UNKNOWN

def get_full_system_report() -> Dict[str, Any]:
    """Sammelt alle Hardware-Infos für den Start-Log."""
    return {
        "profile": detect_system_profile(),
        "os": get_os_info(),
        "cpu": get_cpu_info(),
        "gpu": get_gpu_info(),
        "sensors": get_sensor_info(),
    }
