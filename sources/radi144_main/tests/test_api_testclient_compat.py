from fastapi.testclient import TestClient

from main import app


def test_fastapi_testclient_can_boot_against_app():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "active"
