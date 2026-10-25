from fastapi.testclient import TestClient

from main import _server_kwargs, app


def test_direct_server_default_port_is_8090(monkeypatch):
    monkeypatch.delenv("APP_PORT", raising=False)

    assert _server_kwargs()["port"] == 8090


def test_user_workflow_is_served_by_standalone_api():
    client = TestClient(app)

    response = client.get("/user_workflow.html")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert response.headers["cache-control"] == "no-store"
    assert '<script src="user_workflow.js"></script>' in response.text
    assert "localhost:8000" not in response.text


def test_user_workflow_assets_are_served_by_standalone_api():
    client = TestClient(app)

    css_response = client.get("/user_workflow.css")
    js_response = client.get("/user_workflow.js")

    assert css_response.status_code == 200
    assert "text/css" in css_response.headers["content-type"]
    assert css_response.headers["cache-control"] == "no-store"
    assert js_response.status_code == 200
    assert "javascript" in js_response.headers["content-type"]
    assert js_response.headers["cache-control"] == "no-store"
    assert 'const API_BASE = "/api/v1";' in js_response.text
    assert "localhost:8000" not in js_response.text
