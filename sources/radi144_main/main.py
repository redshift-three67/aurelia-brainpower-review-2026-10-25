import os
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

from app.bootstrap import API_PROFILE, enforce_profile

enforce_profile(API_PROFILE)

from app.api.resonance import router as resonance_router
from app.api.clients import router as clients_router

# Logging Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

APP_VERSION = "1.5.0"
PROJECT_ROOT = Path(__file__).resolve().parent

app = FastAPI(
    title="12x12 Resonance Matrix Standalone",
    description="High-Performance Resonance Matrix Engine with CUDA Support, Adaptive Hardware Scaling, Group Synergy, Multi-Layer Vectorization & EMF Compensation",
    version=APP_VERSION
)

# --- CORS Setup (R-5) -----------------------------------------------------------
# Explizite Origins aus CORS_ORIGINS-env (comma-separiert). Default ist loopback-only
# (konsistent mit deploy/server.env.example). Frueher stand hier allow_origins=["*"]
# kombiniert mit allow_credentials=True — das ist per CORS-Spec ungueltig (Browser lehnen
# Credentials bei Wildcard-Origin ab) und ueberpermissiv. Mit expliziten Origins ist
# allow_credentials=True gueltig; wird "*" konfiguriert, schalten wir Credentials ab.
_API_KEY_PLACEHOLDER = "<set-local-api-key>"


def _parse_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if not raw:
        return ["http://localhost:8090", "http://127.0.0.1:8090"]
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return origins or ["http://localhost:8090", "http://127.0.0.1:8090"]


_cors_origins = _parse_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials="*" not in _cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ui_file_response(filename: str) -> FileResponse:
    return FileResponse(PROJECT_ROOT / filename, headers={"Cache-Control": "no-store"})


@app.get("/user_workflow.html", include_in_schema=False)
async def user_workflow_html():
    return _ui_file_response("user_workflow.html")


@app.get("/user_workflow.css", include_in_schema=False)
async def user_workflow_css():
    return _ui_file_response("user_workflow.css")


@app.get("/user_workflow.js", include_in_schema=False)
async def user_workflow_js():
    return _ui_file_response("user_workflow.js")

# --- API-Key-Gate (R-4) ---------------------------------------------------------
# Default-OFF: aktiviert NUR wenn API_KEY env gesetzt UND nicht der Placeholder aus
# deploy/server.env.example ist. Env wird pro-Request gelesen (nicht import-time cached),
# damit Tests/TestClient ohne gesetztes API_KEY env unbeeinflusst bleiben (no-op).
# Geschuetzt werden /api/v1/*; /, /docs, /redoc, /openapi.json bleiben offen.
# OPTIONS-Preflight passiert ungeprueft (CORSMiddleware behandelt sie).
_OPEN_PATHS = {"/", "/docs", "/redoc", "/openapi.json"}


def _effective_api_key() -> str | None:
    key = os.getenv("API_KEY", "").strip()
    if not key or key == _API_KEY_PLACEHOLDER:
        return None
    return key


@app.middleware("http")
async def _api_key_guard(request: Request, call_next):
    key = _effective_api_key()
    if key is None:
        return await call_next(request)
    path = request.url.path
    if path in _OPEN_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
        return await call_next(request)
    if request.method == "OPTIONS":
        return await call_next(request)
    provided = request.headers.get("x-api-key", "")
    if provided != key:
        return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
    return await call_next(request)


# Router einbinden
app.include_router(resonance_router, prefix="/api/v1", tags=["Resonance"])
# R-7/R-8/R-9: Clients-Router (Safety-Posture, PII-Safe-View, Art.17-Kaskade) — additiv
app.include_router(clients_router, prefix="/api/v1", tags=["Clients"])

@app.get("/")
async def root():
    return {
        "message": "12x12 Resonance Matrix Engine is running",
        "docs": "/docs",
        "status": "active"
    }


def _server_kwargs() -> dict:
    """Host/Port aus APP_HOST/APP_PORT env (R-3), default loopback-safe.

    Konsistent mit deploy/resonance-engine.service, das ${APP_HOST}/${APP_PORT} an
    uvicorn uebergibt. Der direkte `python main.py`-Pfad liest dieselben Env-Variablen,
    statt 0.0.0.0:8000 zu hardcodieren (0.0.0.0 bindet alle Interfaces — nicht
    loopback-safe fuer autarke Lokalnutzung).
    """
    host = os.getenv("APP_HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = int(os.getenv("APP_PORT", "8090"))
    return {"host": host, "port": port}


if __name__ == "__main__":
    kwargs = _server_kwargs()
    logger.info(f"Starting 12x12 Standalone Server on {kwargs['host']}:{kwargs['port']} (APP_HOST/APP_PORT env)...")
    # __main__ ist der Dev-Pfad (reload=True); Produktion laeuft ueber die systemd-Unit
    # deploy/resonance-engine.service (uvicorn main:app --workers ${APP_WORKERS} ...).
    uvicorn.run("main:app", **kwargs, reload=True)
