"""Synthetic audit of the current RadiWorks *local* scope guard, never a host proof."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

from fastapi import WebSocketDisconnect
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from starlette.routing import WebSocketRoute

from radiworks.main import create_app


def main() -> None:
    root = Path(__file__).resolve().parents[3] / "runtime"
    root.mkdir(parents=True, exist_ok=True)
    os.environ["RADIOWORKS_SCOPE_MODE"] = "local"
    os.environ["RADIOWORKS_LOCAL_TENANT_ID"] = "scope-probe"
    os.environ["RADIOWORKS_LOCAL_CLIENT_ID"] = "synthetic"
    os.environ["RADIOWORKS_LOCAL_JOB_ID"] = "route-audit"
    with tempfile.TemporaryDirectory(prefix="rw-local-scope-", dir=root) as home_name:
        home = Path(home_name)
        data = home / "data"
        data.mkdir()
        app = create_app(base_dir=home / "runtime", data_dir=data,
                         materia_dir=home / "materia")
        mounted_routes = []
        for route in app.routes:
            included = getattr(route, "original_router", None)
            mounted_routes.extend(included.routes if included is not None else [route])
        api_routes = [route for route in mounted_routes if isinstance(route, APIRoute)
                      and route.path not in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}]
        ws_routes = [route for route in mounted_routes if isinstance(route, WebSocketRoute)]
        assert len(api_routes) == 61, f"Unexpected HTTP inventory: {len(api_routes)}"
        assert len(ws_routes) == 1 and ws_routes[0].path == "/ws"
        checks = 0
        with TestClient(app) as client:
            for route in api_routes:
                path = re.sub(r"\{[^/]+\}", "synthetic", route.path)
                for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
                    response = client.request(
                        method, path,
                        headers={"X-Aurelia-Tenant-Id": "forged"},
                    )
                    assert response.status_code == 400, (method, route.path, response.status_code)
                    checks += 1
            for header in ("X-Aurelia-Client-Id", "X-Aurelia-Job-Id"):
                response = client.get("/ping", headers={header: "forged"})
                assert response.status_code == 400, (header, response.status_code)
                checks += 1
            for header in ("X-Aurelia-Tenant-Id", "X-Aurelia-Client-Id", "X-Aurelia-Job-Id"):
                try:
                    with client.websocket_connect("/ws", headers={header: "forged"}) as ws:
                        ws.receive_json()
                except WebSocketDisconnect as exc:
                    assert exc.code == 1008, (header, exc.code)
                else:
                    raise AssertionError(f"Forged WebSocket scope accepted: {header}")
                checks += 1
            queue = client.get("/broadcast/queue")
            assert queue.status_code == 200 and queue.json()["queued"] == []
        print(f"PASS local guard: {len(api_routes)} HTTP routes + 1 WebSocket, {checks} forged requests, queue empty")


if __name__ == "__main__":
    main()
