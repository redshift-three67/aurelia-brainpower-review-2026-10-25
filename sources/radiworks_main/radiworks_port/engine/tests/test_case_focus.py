"""Fallfokus bleibt eine Auswahlhilfe und verändert keine Analyseberechnung."""

from fastapi.testclient import TestClient

from radiworks.copyguard import PUBLIC_REDACTION


def test_case_focus_is_saved_without_session_and_snapshotted_in_new_drafts(home: TestClient):
    created = home.post("/cases", json={"name": "Synthetic Focus", "description": "Notiz", "focus": "Pflanzen"})
    assert created.status_code == 200
    assert home.get("/cases/current").json()["focus"] == "Pflanzen"
    reference = home.get("/cases/current/ref").json()["ref"]

    first = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 17, "mode": "seeded"})
    assert first.status_code == 200
    assert first.json()["draft"]["focus"]["case_focus"] == "Pflanzen"

    changed = home.post("/cases/current/metadata", json={
        "focus": "Mineralien", "expected_case_ref": reference,
    })
    assert changed.status_code == 200
    second = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 17, "mode": "seeded"})
    assert second.status_code == 200
    assert second.json()["draft"]["focus"]["case_focus"] == "Mineralien"
    assert home.get(f"/drafts/{first.json()['draft']['id']}").json()["focus"]["case_focus"] == "Pflanzen"
    assert first.json()["result"] == second.json()["result"]


def test_focus_edit_rejects_stale_case_and_redacted_roundtrip(home: TestClient):
    assert home.post("/cases", json={"name": "Synthetic A", "focus": "Erster Fokus"}).status_code == 200
    old_ref = home.get("/cases/current/ref").json()["ref"]
    assert home.post("/cases", json={"name": "Synthetic B", "focus": "Zweiter Fokus"}).status_code == 200
    stale = home.post("/cases/current/metadata", json={
        "focus": "Falsch zugeordnet", "expected_case_ref": old_ref,
    })
    assert stale.status_code == 409
    assert home.get("/cases/current").json()["focus"] == "Zweiter Fokus"

    assert home.post("/cases/current/metadata", json={"focus": "Heilt garantiert"}).status_code == 409
    assert home.post("/cases/current/metadata", json={"focus": PUBLIC_REDACTION}).status_code == 200
    assert home.get("/cases/current").json()["focus"] == "Zweiter Fokus"


def test_focus_length_and_type_are_bounded_on_create_and_edit(home: TestClient):
    assert home.post("/cases", json={"name": "Synthetic Long", "focus": "x" * 241}).status_code == 422
    assert home.post("/cases", json={"name": "Synthetic Wrong", "focus": ["text"]}).status_code == 422
    assert home.post("/cases", json={"name": "Synthetic Valid"}).status_code == 200
    assert home.post("/cases/current/metadata", json={"focus": "x" * 241}).status_code == 422
    assert home.get("/cases/current").json().get("focus") is None


def test_case_mutation_response_binds_saved_document_to_its_reference(home: TestClient):
    created = home.post("/cases", json={"name": "Synthetic Bound A", "focus": "A"})
    assert created.status_code == 200
    ref_a = created.headers["X-RadiWorks-Case-Ref"]
    assert ref_a == home.get("/cases/current").headers["X-RadiWorks-Case-Ref"]

    edited = home.post("/cases/current/metadata", json={
        "description": "A geändert", "expected_case_ref": ref_a,
    })
    assert edited.status_code == 200
    assert edited.headers["X-RadiWorks-Case-Ref"] == ref_a

    created_b = home.post("/cases", json={"name": "Synthetic Bound B", "focus": "B"})
    assert created_b.status_code == 200
    assert created_b.headers["X-RadiWorks-Case-Ref"] != ref_a
    assert edited.headers["X-RadiWorks-Case-Ref"] == ref_a


def test_case_reference_header_is_visible_to_allowed_local_ui_origin(home: TestClient):
    created = home.post("/cases", json={"name": "Synthetic CORS Bound"},
                        headers={"Origin": "http://localhost:8080"})
    assert created.status_code == 200
    assert created.headers["access-control-allow-origin"] == "http://localhost:8080"
    assert "x-radiworks-case-ref" in created.headers.get("access-control-expose-headers", "").lower()
