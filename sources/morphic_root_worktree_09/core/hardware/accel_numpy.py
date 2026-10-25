from __future__ import annotations

"""Backend-Selektor für NumPy oder CuPy.
Migriert nach core/hardware für bessere Kapselung.

Verwendung:
    from . import accel_numpy as anp
    xp = anp.xp          # np oder cp
    anp.use_gpu()        # versucht CuPy zu aktivieren
"""

import importlib
import os
import sys
import types
from typing import Any

import numpy as _np  # Fallback

_xp: Any = _np  # aktuelles Backend
xp: Any = _xp   # Public handle

def _try_import_cupy():  # noqa: D401
    try:
        return importlib.import_module("cupy")
    except Exception:
        return None


def use_gpu(force: bool = False) -> bool:  # noqa: D401
    """Versucht, CuPy zu aktivieren.  
    Gibt True zurück, wenn erfolgreich, sonst False.
    """
    global _xp, xp  # noqa: PLW0603
    cp = _try_import_cupy()
    if cp is None:
        if force:
            print("[accel_numpy] CuPy nicht verfügbar – bleibe auf NumPy.")
        return False
    try:
        _ = cp.zeros((1,))  # kleiner Smoke-Test
        _xp = cp
        xp = _xp
        # print("[accel_numpy] CuPy aktiviert (GPU-Backend).") 
        # Logging reduziert für sauberen CLI Output
        return True
    except Exception as exc:  # pragma: no cover
        if force:
            print(f"[accel_numpy] CuPy konnte nicht initialisiert werden: {exc}")
        _xp = _np
        xp = _xp
        return False


def set_backend(name: str) -> None:  # noqa: D401
    """Explizit 'numpy' oder 'cupy' wählen."""
    global _xp, xp  # noqa: PLW0603
    if name == "cupy":
        if not use_gpu(force=True):
            raise RuntimeError("CuPy konnte nicht aktiviert werden.")
    else:
        _xp = _np
    xp = _xp


# Alias für Kompatibilität
np = _np
cp = _try_import_cupy()
