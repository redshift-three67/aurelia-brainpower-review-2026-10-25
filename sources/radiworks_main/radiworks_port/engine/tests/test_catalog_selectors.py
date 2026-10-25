import json
import re

from radiworks import copyguard
from radiworks.api.routes import STATE
from radiworks.core.rates import RateRepository


def test_catalog_route_projects_names_but_keeps_stable_safe_ids(home):
    state = STATE.state
    data_dir = state.rate_repository.data_dir
    (data_dir / "Heilt.txt").write_text("Synthetic rate\n", encoding="utf-8")
    (data_dir / "HOMEOPATHY_Test_Variant.txt").write_text(
        "Synthetic variant\n", encoding="utf-8"
    )
    state.rate_repository.refresh()

    response = home.get("/catalogs")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["releaseId"] is None
    assert set(payload["catalogs"][0]) == {"id", "exactId", "selector", "name", "label"}
    protected = next(
        item for item in payload["catalogs"] if item["name"] == copyguard.PUBLIC_REDACTION
    )
    assert protected["label"] == copyguard.PUBLIC_REDACTION
    assert re.fullmatch(r"catalog-[0-9a-f]{64}", protected["id"])
    assert re.fullmatch(r"catalog-[0-9a-f]{64}", protected["exactId"])
    assert protected["selector"] == protected["id"]
    assert protected["id"] != protected["exactId"]
    assert [rate.name for rate in state.rate_repository.find_all_by_source_name(protected["id"])] == ["Synthetic rate"]
    assert [rate.name for rate in state.rate_repository.find_all_by_source_name(protected["exactId"])] == ["Synthetic rate"]
    assert "Heilt" not in json.dumps(payload, ensure_ascii=False)
    assert "Synthetic rate" not in json.dumps(payload, ensure_ascii=False)

    first_ids = {item["id"] for item in payload["catalogs"]}
    state.rate_repository.refresh()
    refreshed = home.get("/catalogs").json()
    assert {item["id"] for item in refreshed["catalogs"]} == first_ids

    legacy = home.get("/databases")
    assert legacy.status_code == 200
    assert copyguard.PUBLIC_REDACTION in legacy.json()["databases"]


def test_catalog_ids_preserve_prefix_exact_and_legacy_group_order(home):
    state = STATE.state
    data_dir = state.rate_repository.data_dir
    (data_dir / "HOMEOPATHY_Test_Variant.txt").write_text(
        "VariantRate\n", encoding="utf-8"
    )
    state.rate_repository.refresh()

    response = home.get("/catalogs")

    assert response.status_code == 200, response.text
    item = next(
        item for item in response.json()["catalogs"] if item["name"] == "HOMEOPATHY_Test"
    )
    repository = state.rate_repository
    legacy_prefix = repository.find_all_by_source_name("HOMEOPATHY_Test")
    id_prefix = repository.find_all_by_source_name(item["id"])
    legacy_exact = repository.find_all_by_source_name("HOMEOPATHY_Test.txt")
    id_exact = repository.find_all_by_source_name(item["exactId"])
    legacy_group = repository.find_all_by_source_name("HOMEOPATHY")

    assert [(rate.source_name, rate.analysis_key) for rate in id_prefix] == [
        (rate.source_name, rate.analysis_key) for rate in legacy_prefix
    ]
    assert [(rate.source_name, rate.analysis_key) for rate in id_exact] == [
        (rate.source_name, rate.analysis_key) for rate in legacy_exact
    ]
    assert {rate.source_name for rate in id_prefix} == {
        "HOMEOPATHY_Test.txt",
        "HOMEOPATHY_Test_Variant.txt",
    }
    assert {rate.source_name for rate in legacy_group} == {
        "HOMEOPATHY_Test.txt",
        "HOMEOPATHY_Test_Variant.txt",
    }


def test_unknown_opaque_id_is_not_used_as_a_legacy_prefix(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    unknown_id = "catalog-" + "0" * 64
    (data_dir / f"{unknown_id}-decoy.txt").write_text("Must not select\n", encoding="utf-8")
    repository = RateRepository(data_dir)
    repository.refresh()

    assert repository.find_all_by_source_name(unknown_id) == []


def test_suggestions_include_opaque_ids_and_legacy_confirm_still_works(home):
    state = STATE.state
    data_dir = state.rate_repository.data_dir
    (data_dir / "BIOLOGICAL_Focus.txt").write_text("Pflanzen Ruhe\n", encoding="utf-8")
    state.rate_repository.refresh()
    body = {"topics": "Pflanzen", "use_focus": False}

    response = home.post("/database-suggestions", json=body)

    assert response.status_code == 200, response.text
    proposal = response.json()
    selected = next(item for item in proposal["suggestions"] if item["name"] == "BIOLOGICAL_Focus")
    assert selected["selector"] == selected["exactId"]
    assert re.fullmatch(r"catalog-[0-9a-f]{64}", selected["catalogId"])
    assert re.fullmatch(r"catalog-[0-9a-f]{64}", selected["exactId"])

    confirmed = home.post(
        "/database-suggestions/confirm",
        json={
            **body,
            "catalogSnapshotDigest": proposal["catalogSnapshotDigest"],
            "selector": "BIOLOGICAL_Focus.txt",
        },
    )
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["selector"] == selected["exactId"]


def test_opaque_selector_keeps_original_seeded_analysis_values(home):
    state = STATE.state
    (state.rate_repository.data_dir / "HOMEOPATHY_Test_Variant.txt").write_text("Synthetic variant\n", encoding="utf-8")
    state.rate_repository.refresh()
    entry = next(item for item in home.get("/catalogs").json()["catalogs"] if item["name"] == "HOMEOPATHY_Test")
    for legacy, selector in [("HOMEOPATHY_Test", entry["id"]), ("HOMEOPATHY_Test.txt", entry["exactId"])]:
        body = {"mode": "seeded", "seed": 29, "max_hits": 100}
        before = home.post("/analysis", json={**body, "database": legacy})
        after = home.post("/analysis", json={**body, "database": selector})
        assert before.status_code == after.status_code == 200
        assert before.json()["result"] == after.json()["result"]
