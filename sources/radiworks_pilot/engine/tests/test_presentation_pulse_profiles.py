"""Pulse profile schema evolution preserves legacy bytes and frozen receipts."""
from __future__ import annotations

import copy
import json

import pytest

from radiworks.api.routes import STATE
from radiworks.core.presentation_profile import (
    PresentationProfileError,
    PresentationProfileStore,
    default_profile,
    make_presentation_receipt,
    validate_presentation_receipt,
    validate_profile_payload,
)
from radiworks.persistence import document_digest
from radiworks.scope import ScopeContext


V1_KEYS = {
    "schemaVersion", "caseId", "version", "audioProfile",
    "stageSeconds", "repeat", "images", "digest",
}
V2_KEYS = V1_KEYS | {"modulationDepthPercent"}
PULSE_LIMITS = {
    "pink-pulse-v1": 600,
    "pink-phi-v1": 87,
    "pink-fibonacci-v1": 46,
}


def signed_profile(body):
    value = copy.deepcopy(body)
    value["digest"] = document_digest(value)
    return value


def pulse_profile(audio_profile, stage_seconds, depth):
    return signed_profile({
        "schemaVersion": 2,
        "caseId": "a" * 32,
        "version": 1,
        "audioProfile": audio_profile,
        "stageSeconds": stage_seconds,
        "repeat": True,
        "images": [],
        "modulationDepthPercent": depth,
    })


def profile_payload(case, reference, version, **changes):
    body = {
        "expected_case_ref": reference,
        "expected_context_version": case["contextVersion"],
        "expected_profile_version": version,
        "audio_profile": "original",
        "stage_seconds": 60,
        "repeat": False,
        "images": [],
    }
    body.update(changes)
    return body


def new_case(home):
    response = home.post("/cases", json={"name": "Pulse profile", "focus": "Schema test"})
    assert response.status_code == 200, response.text
    return response.json(), response.headers["X-RadiWorks-Case-Ref"]


def test_legacy_v1_bytes_digest_and_companion_receipt_remain_unchanged(tmp_path):
    scope = ScopeContext("tenant-a", "client-a", "job-a")
    store = PresentationProfileStore(tmp_path / "cases", scope)
    case_id = "a" * 32
    legacy = signed_profile({
        "schemaVersion": 1,
        "caseId": case_id,
        "version": 7,
        "audioProfile": "pink",
        "stageSeconds": 60,
        "repeat": True,
        "images": [],
    })
    path = store._path(case_id, create=True)
    original_bytes = json.dumps(
        {**legacy, "scopeHash": store.scope_hash},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    path.write_bytes(original_bytes)

    loaded = store.get(case_id)
    assert loaded == legacy
    assert set(loaded) == V1_KEYS
    assert loaded["digest"] == legacy["digest"]
    assert path.read_bytes() == original_bytes

    saved = store.update(
        case_id=case_id, expected_version=7, audio_profile="off",
        stage_seconds=600, repeat=False, images=[],
    )
    assert saved["schemaVersion"] == 1
    assert set(saved) == V1_KEYS
    assert saved["digest"] == document_digest(
        {key: value for key, value in saved.items() if key != "digest"}
    )
    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert set(persisted) == V1_KEYS | {"scopeHash"}
    assert persisted["digest"] == saved["digest"]

    default = default_profile(None)
    target = {"digest": "f" * 64, "binding": "unbound"}
    receipt = make_presentation_receipt(default, "b" * 32, target["digest"])
    assert receipt["schemaVersion"] == 1
    assert validate_presentation_receipt(
        receipt, broadcast_id="b" * 32, target=target,
    ) == receipt


def test_v2_validator_accepts_pulse_boundaries_and_rejects_corruption():
    for profile_id, upper_bound in PULSE_LIMITS.items():
        profile = pulse_profile(profile_id, upper_bound, 100)
        try:
            validated = validate_profile_payload(profile)
        except PresentationProfileError as exc:
            pytest.fail(f"valid V2 profile {profile_id} was rejected: {exc}")
        assert validated == profile
        assert set(validated) == V2_KEYS
        lower_profile = pulse_profile(profile_id, 1, 0)
        assert validate_profile_payload(lower_profile) == lower_profile

        for bad_depth in (True, 50.5, "50", None, -1, 101):
            corrupted = copy.deepcopy(profile)
            corrupted["modulationDepthPercent"] = bad_depth
            corrupted = signed_profile({key: value for key, value in corrupted.items() if key != "digest"})
            with pytest.raises(PresentationProfileError):
                validate_profile_payload(corrupted)

        too_long = copy.deepcopy(profile)
        too_long["stageSeconds"] = upper_bound + 1
        too_long = signed_profile({key: value for key, value in too_long.items() if key != "digest"})
        with pytest.raises(PresentationProfileError):
            validate_profile_payload(too_long)

        missing_depth = copy.deepcopy(profile)
        del missing_depth["modulationDepthPercent"]
        missing_depth = signed_profile({key: value for key, value in missing_depth.items() if key != "digest"})
        with pytest.raises(PresentationProfileError):
            validate_profile_payload(missing_depth)

    legacy_with_depth = signed_profile({
        "schemaVersion": 1,
        "caseId": "a" * 32,
        "version": 1,
        "audioProfile": "pink",
        "stageSeconds": 60,
        "repeat": False,
        "images": [],
        "modulationDepthPercent": 50,
    })
    with pytest.raises(PresentationProfileError):
        validate_profile_payload(legacy_with_depth)

    v2_legacy_id = pulse_profile("pink", 60, 50)
    with pytest.raises(PresentationProfileError):
        validate_profile_payload(v2_legacy_id)


def test_pulse_put_requires_strict_depth_and_keeps_scope_and_cas(home):
    case, reference = new_case(home)
    profile_version = 0
    for profile_id, upper_bound in PULSE_LIMITS.items():
        saved = home.put(
            "/presentation-profile",
            json=profile_payload(
                case, reference, profile_version,
                audio_profile=profile_id,
                stage_seconds=upper_bound,
                modulation_depth_percent=50,
            ),
        )
        assert saved.status_code == 200, saved.text
        profile = saved.json()["profile"]
        assert profile["schemaVersion"] == 2
        assert set(profile) == V2_KEYS
        assert profile["audioProfile"] == profile_id
        assert profile["stageSeconds"] == upper_bound
        assert profile["modulationDepthPercent"] == 50
        assert profile["digest"] == document_digest(
            {key: value for key, value in profile.items() if key != "digest"}
        )
        profile_version = profile["version"]

    for invalid in (
        {},
        {"modulation_depth_percent": None},
        {"modulation_depth_percent": True},
        {"modulation_depth_percent": 50.5},
        {"modulation_depth_percent": "50"},
        {"modulation_depth_percent": -1},
        {"modulation_depth_percent": 101},
    ):
        response = home.put(
            "/presentation-profile",
            json=profile_payload(
                case, reference, profile_version,
                audio_profile="pink-pulse-v1", stage_seconds=1, **invalid,
            ),
        )
        assert response.status_code == 422, response.text

    legacy_save = home.put(
        "/presentation-profile",
        json=profile_payload(
            case, reference, profile_version, audio_profile="pink",
        ),
    )
    assert legacy_save.status_code == 200, legacy_save.text
    legacy_profile = legacy_save.json()["profile"]
    assert legacy_profile["schemaVersion"] == 1
    assert set(legacy_profile) == V1_KEYS

    explicit_null = home.put(
        "/presentation-profile",
        json=profile_payload(
            case, reference, legacy_profile["version"],
            audio_profile="pink", modulation_depth_percent=None,
        ),
    )
    assert explicit_null.status_code == 422, explicit_null.text
    conflict = home.put(
        "/presentation-profile",
        json=profile_payload(
            case, reference, legacy_profile["version"] - 1,
            audio_profile="pink-pulse-v1", stage_seconds=1,
            modulation_depth_percent=25,
        ),
    )
    assert conflict.status_code == 409, conflict.text

    other_scope = PresentationProfileStore(
        STATE.state.case_store.cases_dir,
        ScopeContext("other-tenant", "client-a", "job-a"),
    )
    scoped_default = other_scope.get(case["caseId"])
    assert scoped_default["audioProfile"] == "original"
    assert scoped_default["schemaVersion"] == 1


def test_v2_broadcast_receipt_stays_frozen_after_profile_change(home, monkeypatch):
    case, reference = new_case(home)
    monkeypatch.setattr(STATE.state.broadcast, "_start_thread", lambda: None)
    first_profile = home.put(
        "/presentation-profile",
        json=profile_payload(
            case, reference, 0, audio_profile="pink-phi-v1",
            stage_seconds=30, repeat=True, modulation_depth_percent=43,
        ),
    )
    assert first_profile.status_code == 200, first_profile.text

    first = home.post(
        "/broadcast",
        json={
            "signature": "Synthetic Pulse", "seconds": 5,
            "expected_case_ref": reference,
            "expected_context_version": case["contextVersion"],
        },
    )
    assert first.status_code == 200, first.text
    first_receipt = first.json()["presentation"]
    assert first_receipt["schemaVersion"] == 1
    assert set(first_receipt) == {
        "schemaVersion", "broadcastId", "targetDigest", "profile", "digest",
    }
    assert first_receipt["profile"]["schemaVersion"] == 2
    assert first_receipt["profile"]["audioProfile"] == "pink-phi-v1"
    assert first_receipt["profile"]["modulationDepthPercent"] == 43

    changed_profile = home.put(
        "/presentation-profile",
        json=profile_payload(
            case, reference, 1, audio_profile="pink-fibonacci-v1",
            stage_seconds=46, repeat=False, modulation_depth_percent=72,
        ),
    )
    assert changed_profile.status_code == 200, changed_profile.text
    first_stored = STATE.state.broadcast_targets.get(
        first.json()["targetReference"]["jobId"],
    )
    assert first_stored["presentation"] == first_receipt

    second = home.post(
        "/broadcast",
        json={
            "signature": "Synthetic Pulse", "seconds": 5,
            "expected_case_ref": reference,
            "expected_context_version": case["contextVersion"],
        },
    )
    assert second.status_code == 200, second.text
    assert second.json()["presentation"]["profile"]["audioProfile"] == "pink-fibonacci-v1"
    assert first_stored["presentation"]["profile"]["audioProfile"] == "pink-phi-v1"


def test_persisted_v2_with_recomputed_but_invalid_depth_fails_closed(home):
    case, reference = new_case(home)
    saved = home.put(
        "/presentation-profile",
        json=profile_payload(
            case, reference, 0, audio_profile="pink-phi-v1",
            stage_seconds=87, modulation_depth_percent=50,
        ),
    )
    assert saved.status_code == 200, saved.text

    store = STATE.state.presentation_profiles
    path = store._path(case["caseId"])
    record = json.loads(path.read_text(encoding="utf-8"))
    record["modulationDepthPercent"] = 101
    body = {
        key: value for key, value in record.items()
        if key not in {"digest", "scopeHash"}
    }
    record["digest"] = document_digest(body)
    path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(PresentationProfileError) as caught:
        store.get(case["caseId"])
    assert caught.value.code == "profile_corrupt"

    response = home.get(
        "/presentation-profile",
        params={
            "case_ref": reference,
            "context_version": case["contextVersion"],
        },
    )
    assert response.status_code == 409, response.text



def test_nonpulse_put_rejects_an_explicit_modulation_value(home):
    case, reference = new_case(home)
    response = home.put(
        "/presentation-profile",
        json=profile_payload(
            case, reference, 0, audio_profile="pink",
            modulation_depth_percent=50,
        ),
    )
    assert response.status_code == 422, response.text

