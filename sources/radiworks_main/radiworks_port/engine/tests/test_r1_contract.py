"""R1: REST-ABI-v1 und Passport-v2-Vertrag."""

from fastapi.testclient import TestClient

from radiworks.api.routes import STATE
from radiworks.manifest import KERNEL_VERSION


def _analysis(client: TestClient, **body):
    return client.post(
        "/analysis",
        json={"database": "HOMEOPATHY_Test", "seed": 991, **body},
    )


def test_manifest_declares_the_rest_analysis_operation(home: TestClient):
    manifest = home.get("/manifest").json()

    assert manifest["version"] == KERNEL_VERSION == "0.2.0"
    assert manifest["abi_surface"] == "rest"
    assert manifest["abi_version"] == "v1"
    assert manifest["entry"] == "radiworks.core.analysis:analyse_rate_list"
    assert manifest["entry_status"] == "deprecated-compatibility"

    operation = manifest["operations"]
    assert operation == [
        {
            **operation[0],
            "id": "analysis",
            "method": "POST",
            "path": "/analysis",
            "version": "v1",
        }
    ]
    assert operation[0]["input_schema"] == manifest["input_schema"]
    assert operation[0]["output_schema"] == manifest["output_schema"]


def test_manifest_analysis_schema_matches_the_current_rest_wire_shape(home: TestClient):
    manifest = home.get("/manifest").json()
    response = _analysis(home)
    assert response.status_code == 200
    payload = response.json()
    schema = manifest["operations"][0]["output_schema"]

    assert set(schema["required"]).issubset(payload)
    assert set(schema["properties"]["result"]["required"]).issubset(payload["result"])
    assert set(schema["properties"]["draft"]["required"]).issubset(payload["draft"])
    assert set(schema["properties"]["passport"]["required"]).issubset(payload["passport"])
    assert "general_vitality" not in payload["result"]
    assert "rate_objects" not in payload["result"]
    assert payload["result"]["rateObjects"]
    assert set(
        schema["properties"]["result"]["properties"]["rateObjects"]["items"]["required"]
    ).issubset(payload["result"]["rateObjects"][0])


def test_passport_v2_hashes_the_resolved_mode_and_declares_unsigned(home: TestClient):
    implicit = _analysis(home)
    explicit = _analysis(home, mode="seeded")
    assert implicit.status_code == explicit.status_code == 200
    implicit_passport = implicit.json()["passport"]
    explicit_passport = explicit.json()["passport"]

    assert implicit_passport["input_hash"] == explicit_passport["input_hash"]
    assert implicit_passport["passport_schema_version"] == 2
    assert implicit_passport["input_hash_scheme"] == "analysis-request-v2"
    assert implicit_passport["seed_scheme"] == "effective-v2"
    assert implicit_passport["signatur_status"] == "unsigned"

    state = STATE.state
    assert state is not None
    state.random_org._http_get = None
    state.entropy_feed.feed([123456])
    stochastic = _analysis(home, mode="stochastic")
    assert stochastic.status_code == 200
    stochastic_passport = stochastic.json()["passport"]
    assert stochastic_passport["input_hash"] != implicit_passport["input_hash"]
    assert stochastic_passport["entropy_mode"] == "stochastic"
    assert stochastic_passport["replayable"] is False


def test_body_and_header_seed_share_the_effective_passport_input(home: TestClient):
    body = _analysis(home, seed=17)
    header = home.post(
        "/analysis",
        json={"database": "HOMEOPATHY_Test"},
        headers={"X-Client-Seed": "17"},
    )

    assert body.status_code == header.status_code == 200
    assert body.json()["passport"]["input_hash"] == header.json()["passport"]["input_hash"]
