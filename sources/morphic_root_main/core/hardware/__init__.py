"""
Hardware Abstraction Layer (HAL)
Bündelt Systemerkennung, Entropiequellen und Hardware-Beschleunigung.
"""

from .system_info import get_full_system_report, detect_system_profile
from .accel_numpy import xp, use_gpu
