"""Startskript des RadiWorks-Kernels.

Verwendung (aus engine/):
    .venv/Scripts/python.exe run.py                 # Port 8090
    .venv/Scripts/python.exe run.py --port 8091
    .venv/Scripts/python.exe run.py --bootstrap-synthetic-catalog

Pathlogik: Der Heimatpfad kommt aus ``RADIOWORKS_HOME`` oder standardmaessig
``~/.radiworks``. Der read-only Rate-Katalog kommt optional aus
``RADIOWORKS_DATA_DIR``. Liegt das Skript im Radiworks-Baum, wird der originale
Clarke-Korpus direkt eingebunden; andernfalls wird der Laufzeitkorpus genutzt.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import uvicorn

ENGINE_DIR = Path(__file__).resolve().parent
RADIWORKS_ROOT = ENGINE_DIR.parent.parent
ORIGINAL_CLARKE = RADIWORKS_ROOT / "materiaMedica" / "Clarke"
WEBAPP_DIR = ENGINE_DIR.parent / "webapp"


def resolve_materia_dir(home_dir: Path) -> Path:
    if ORIGINAL_CLARKE.is_dir():
        return ORIGINAL_CLARKE
    return home_dir / "materiaMedica" / "Clarke"


def main() -> None:
    parser = argparse.ArgumentParser(description="RadiWorks Engine starten")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--bootstrap-synthetic-catalog",
        action="store_true",
        help="legt einmalig einen rein synthetischen Preview-Katalog im Runtime-Home an",
    )
    args = parser.parse_args()

    from radiworks.bootstrap import (
        SyntheticCatalogBootstrapError,
        bootstrap_synthetic_catalog,
    )
    from radiworks.main import create_app, default_rate_data_dir, default_runtime_home

    home_dir = default_runtime_home()
    if args.bootstrap_synthetic_catalog:
        try:
            catalog = bootstrap_synthetic_catalog(
                home_dir,
                external_data_dir=os.environ.get("RADIOWORKS_DATA_DIR") or None,
            )
        except SyntheticCatalogBootstrapError as exc:
            parser.error(str(exc))
        print(f"RadiWorks Engine — synthetischer Preview-Katalog: {catalog.resolve()}")
    data_dir = default_rate_data_dir(home_dir)
    materia_dir = resolve_materia_dir(home_dir)
    print(f"RadiWorks Engine — Heimat: {home_dir.resolve()}")
    print(f"RadiWorks Engine — Rate-Katalog: {data_dir.resolve()}")
    print(f"RadiWorks Engine — Clarke-Korpus: {materia_dir.resolve()}")
    if WEBAPP_DIR.is_dir():
        print(f"RadiWorks Engine — Webapp: {WEBAPP_DIR.resolve()}")

    app = create_app(
        base_dir=home_dir,
        materia_dir=materia_dir,
        webapp_dir=WEBAPP_DIR if WEBAPP_DIR.is_dir() else None,
    )
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
