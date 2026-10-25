"""Morphic Engine V1 - Interaktive Web-UI (FastAPI + Uvicorn).

Startet einen FastAPI-Server auf http://127.0.0.1:8000 mit:
  - API-Endpunkten unter /api/* (neu) und /api/v1/* (legacy web_app.py)
  - WebSocket /api/emf/ws (5s EMF-Monitor)
  - Statischem Frontend unter /ui/* (web_ui/) und /static/ (apps/web/static/)

Verwendet jetzt die modulare apps/web/main.py als Haupt-App.
Die alte web_app.py ist deprecated und wird in einer folgenden Version entfernt.

Start: python web_server.py  oder  .venv/Scripts/python.exe web_server.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Projekt-Root sicherstellen
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def main() -> None:
    import uvicorn

    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))

    print(f"Morphic Engine V1 - Web-UI")
    print(f"  Server: http://{host}:{port}")
    print(f"  Frontend: http://{host}:{port}/ui/")
    print(f"  API-Docs: http://{host}:{port}/docs")
    print()

    uvicorn.run(
        "apps.web.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
