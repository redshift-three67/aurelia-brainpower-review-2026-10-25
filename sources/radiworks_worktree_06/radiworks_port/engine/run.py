"""Startskript des RadiWorks-Kernels.

Verwendung (aus engine/):
    .venv/Scripts/python.exe run.py                 # Port 8090
    .venv/Scripts/python.exe run.py --port 8091

Pfadlogik: liegt das Skript im Radiworks-Baum, wird der originale
Clarke-Korpus (Radiworks/materiaMedica/Clarke) direkt eingebunden —
keine Datenkopie. Andernfalls gilt radiworks_home/materiaMedica/Clarke.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

ENGINE_DIR = Path(__file__).resolve().parent
HOME_DIR = ENGINE_DIR / "radiworks_home"
RADIWORKS_ROOT = ENGINE_DIR.parent.parent
ORIGINAL_CLARKE = RADIWORKS_ROOT / "materiaMedica" / "Clarke"
WEBAPP_DIR = ENGINE_DIR.parent / "webapp"


def resolve_materia_dir() -> Path:
    if ORIGINAL_CLARKE.is_dir():
        return ORIGINAL_CLARKE
    return HOME_DIR / "materiaMedica" / "Clarke"


def main() -> None:
    parser = argparse.ArgumentParser(description="RadiWorks Engine starten")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    materia_dir = resolve_materia_dir()
    print(f"RadiWorks Engine — Heimat: {HOME_DIR.resolve()}")
    print(f"RadiWorks Engine — Clarke-Korpus: {materia_dir.resolve()}")
    if WEBAPP_DIR.is_dir():
        print(f"RadiWorks Engine — Webapp: {WEBAPP_DIR.resolve()}")

    from radiworks.main import create_app

    app = create_app(
        base_dir=HOME_DIR,
        materia_dir=materia_dir,
        webapp_dir=WEBAPP_DIR if WEBAPP_DIR.is_dir() else None,
    )
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
