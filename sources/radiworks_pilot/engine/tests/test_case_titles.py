"""M2.1 case-title modes, stable files, and guarded metadata mutations."""
import copy
import json

import pytest

from radiworks.api.routes import STATE
from radiworks.core.cases import CaseNameError, CaseStore
from radiworks.scope import ScopeContext


def _context_case(home, *, personal=None, focus=None):
    response = home.post("/cases", json={
        "titleMode": "context",
        "personalContext": personal or {},
        "focus": focus,
    })
    assert response.status_code == 200, response.text
    return response


def test_context_title_uses_normalized_selected_person_place_and_focus_in_id_file(home):
    response = _context_case(
        home,
        personal={
            "firstName": "  Zoë  ",
            "lastName": "Müller",
            "birthDate": "1980-02-29",
            "place": " Hamburg/Innenstadt: Nord ",
            "placeKind": "residence",
        },
        focus="  Bereich / A: B  ",
    )

    case = response.json()
    state = STATE.state
    assert state is not None
    assert case["titleMode"] == "context"
    assert case["name"] == "Zoë Müller 29021980 Hamburg/Innenstadt: Nord - Bereich / A: B"
    path = state.case_store.cases_dir / f"case-{case['caseId']}.json"
    assert path.is_file()
    assert state.case_store.load(case["name"])["caseId"] == case["caseId"]
    assert response.headers["X-RadiWorks-Case-Ref"] == home.get("/cases/current/ref").json()["ref"]


def test_long_context_title_with_path_characters_never_becomes_a_path(home):
    personal = {
        "firstName": "A" * 160,
        "lastName": "B" * 160,
        "birthDate": "1980-01-02",
        "place": "P" * 238 + "/:",
        "placeKind": "birth",
    }
    focus = "F" * 238 + "/:"

    response = _context_case(home, personal=personal, focus=focus)

    case = response.json()
    state = STATE.state
    assert state is not None
    assert len(case["name"]) > 255
    assert case["name"].endswith(" - " + focus)
    assert (state.case_store.cases_dir / f"case-{case['caseId']}.json").is_file()
    assert state.case_store.load(case["name"])["caseId"] == case["caseId"]


def test_context_title_skips_missing_and_unselected_fields_and_has_neutral_fallback(home):
    partial = _context_case(
        home,
        personal={"firstName": "  Ada ", "place": "Unselected Place"},
    ).json()
    assert partial["name"] == "Ada"
    assert "Unselected Place" not in partial["name"]

    empty = _context_case(home).json()
    assert empty["name"] == f"Fall {empty['caseId'][:8]}"


def test_duplicate_context_titles_are_scoped_and_reference_activated(home):
    personal = {"firstName": "Alex", "birthDate": "1990-01-02"}
    first = _context_case(home, personal=personal, focus="Same focus").json()
    second = _context_case(home, personal=personal, focus="Same focus").json()
    state = STATE.state
    assert state is not None

    assert first["name"] == second["name"]
    assert first["caseId"] != second["caseId"]
    assert len(home.get("/cases").json()["entries"]) == 2
    with pytest.raises(CaseNameError, match="eindeutig"):
        state.case_store.load(first["name"])

    entries = home.get("/cases").json()["entries"]
    assert len({entry["ref"] for entry in entries}) == 2
    for case in (first, second):
        matching = next(entry for entry in entries if entry["ref"] == state.case_store.reference_for_case(case))
        activated = home.post(f"/cases/ref/{matching['ref']}/activate")
        assert activated.status_code == 200
        assert activated.json()["caseId"] == case["caseId"]


def test_unknown_title_mode_is_rejected_without_creating_a_case(home, tmp_path):
    response = home.post("/cases", json={"name": "Synthetic Invalid Mode", "titleMode": "automatic"})
    assert response.status_code == 422
    assert home.get("/cases").json()["entries"] == []

    store = CaseStore(tmp_path)
    with pytest.raises(CaseNameError, match="Titelmodus"):
        store.save({"name": "Synthetic Invalid Mode", "titleMode": "automatic"})


def test_legacy_name_stays_manual_until_explicit_context_mode_change(home):
    state = STATE.state
    assert state is not None
    original_name = "Mira Beispiel 04051980"
    path = state.case_store.cases_dir / "MiraBeispiel04051980.json"
    document = {
        "name": original_name,
        "scope": state.scope.to_dict(),
        "sessionList": [],
        "personalContext": {},
        "focus": None,
    }
    path.write_text(json.dumps(document), encoding="utf-8")
    before_read = path.read_bytes()

    activated = home.post("/cases/MiraBeispiel04051980/activate")
    assert activated.status_code == 200
    assert activated.json()["name"] == original_name
    assert activated.json().get("titleMode", "manual") == "manual"
    assert path.read_bytes() == before_read

    reference = home.get("/cases/current/ref").json()["ref"]
    edit = home.post("/cases/current/metadata", json={
        "focus": "Neuer Fokus", "expected_case_ref": reference,
    })
    assert edit.status_code == 200, edit.text
    assert edit.json().get("titleMode", "manual") == "manual"
    assert edit.json()["name"] == original_name
    assert path.is_file()
    assert len([item for item in state.case_store.cases_dir.glob("*.json") if item.name != "dashboardInformations.json"]) == 1


def test_context_mode_switch_keeps_old_file_identity_and_session_snapshot(home):
    created = home.post("/cases", json={
        "name": "Operator Supplied Legacy Label",
        "personalContext": {
            "firstName": "Ria", "lastName": "Muster", "birthDate": "1975-06-04",
            "place": "Bern", "placeKind": "birth",
        },
        "focus": "Before",
    })
    assert created.status_code == 200, created.text
    old_name = created.json()["name"]
    old_id = created.json()["caseId"]
    state = STATE.state
    assert state is not None
    old_path = state.case_store.cases_dir / f"{old_name.replace(' ', '')}.json"

    analysis = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 42})
    assert analysis.status_code == 200, analysis.text
    old_sessions = copy.deepcopy(home.get("/cases/current").json()["sessionList"])
    old_snapshot = copy.deepcopy(old_sessions[-1]["contextSnapshot"])
    old_snapshot_bytes = json.dumps(old_snapshot, sort_keys=True, separators=(",", ":"))
    reference = home.get("/cases/current/ref").json()["ref"]

    switched = home.post("/cases/current/metadata", json={
        "titleMode": "context",
        "expected_case_ref": reference,
        "expected_context_version": created.json()["contextVersion"],
    })
    assert switched.status_code == 200, switched.text
    current = switched.json()
    assert current["titleMode"] == "context"
    assert current["name"] == "Ria Muster 04061975 Bern - Before"
    assert current["caseId"] == old_id
    assert current["sessionList"] == old_sessions
    assert json.dumps(current["sessionList"][-1]["contextSnapshot"], sort_keys=True, separators=(",", ":")) == old_snapshot_bytes
    assert old_path.is_file()
    assert len([item for item in state.case_store.cases_dir.glob("*.json") if item.name != "dashboardInformations.json"]) == 1

    newer = home.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 43})
    assert newer.status_code == 200, newer.text
    assert newer.json()["draft"]["contextSnapshot"]["context"]["caseLabel"] == current["name"]


def test_context_metadata_is_guarded_and_full_case_post_cannot_bypass_it(home):
    created = _context_case(home, personal={"firstName": "Ria"}, focus="First").json()
    reference = home.get("/cases/current/ref").json()["ref"]
    fresh = home.post("/cases/current/metadata", json={
        "personalContextChanges": {"firstName": "Ria Fresh"}, "expected_case_ref": reference,
        "expected_context_version": created["contextVersion"],
    })
    assert fresh.status_code == 200, fresh.text
    current = home.get("/cases/current").json()

    stale = home.post("/cases/current/metadata", json={
        "personalContextChanges": {"firstName": "Ria Stale"}, "expected_case_ref": reference,
        "expected_context_version": created["contextVersion"],
    })
    assert stale.status_code == 409

    forged = copy.deepcopy(current)
    forged["focus"] = "Bypass"
    forged["name"] = "A Different Title"
    direct = home.post("/cases", json=forged)
    assert direct.status_code in (409, 422)
    after = home.get("/cases/current").json()
    assert after["caseId"] == created["caseId"]
    assert after["name"] == current["name"]
    assert after["focus"] == current["focus"]
    assert len(home.get("/cases").json()["entries"]) == 1


def test_context_label_lookup_respects_each_store_scope(tmp_path):
    first_scope = ScopeContext("tenant-a", "client", "job")
    second_scope = ScopeContext("tenant-b", "client", "job")
    first = CaseStore(tmp_path, scope=first_scope)
    second = CaseStore(tmp_path, scope=second_scope)

    first_case = first.save({"titleMode": "context", "focus": "Shared focus"})
    second_case = second.save({"titleMode": "context", "focus": "Shared focus"})

    assert first_case["name"] == second_case["name"]
    assert first_case["caseId"] != second_case["caseId"]
    assert first.load(first_case["name"])["scope"] == first_scope.to_dict()
    assert second.load(second_case["name"])["scope"] == second_scope.to_dict()
    assert len(first.list_entries()) == 1
    assert len(second.list_entries()) == 1
    assert first.find_identity(second_case["caseId"]) is None


def test_raw_legacy_metadata_never_uses_other_active_case_file(home):
    state = STATE.state
    path = state.case_store.cases_dir / "LegacyA.json"
    legacy = {"name": "Legacy A", "scope": state.scope.to_dict(), "sessionList": [], "description": "Before"}
    path.write_text(json.dumps(legacy), encoding="utf-8")
    other = home.post("/cases", json={"name": "Synthetic B"}).json()
    other_path = state.case_store.find_identity(other["caseId"])[0]
    untouched = other_path.read_bytes()
    response = home.post("/cases", json={"name": "Legacy A", "description": "After"})
    assert response.status_code == 200, response.text
    assert json.loads(path.read_text(encoding="utf-8"))["description"] == "After"
    assert other_path.read_bytes() == untouched
    assert response.json()["caseId"] != other["caseId"]


def test_context_title_editor_accepts_version_and_rejects_stale_edit(home):
    response = _context_case(home, personal={"firstName": "Synthetic"}, focus="Before")
    reference = response.headers["X-RadiWorks-Case-Ref"]
    guard = {"expected_case_ref": reference, "expected_context_version": response.json()["contextVersion"]}
    changed = home.post("/cases/current/metadata", json={"focus": "After", **guard})
    assert changed.status_code == 200, changed.text
    stale = home.post("/cases/current/metadata", json={"focus": "Wrong", **guard})
    assert stale.status_code == 409
    assert home.get("/cases/current").json()["focus"] == "After"
