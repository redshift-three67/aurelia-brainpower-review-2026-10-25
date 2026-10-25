"""Presentation profiles are scoped case metadata; receipts pin them at acceptance."""
import base64
import hashlib
import json
import struct
import zlib

import pytest

from radiworks.api.routes import STATE
from radiworks.persistence import document_digest


def new_case(home, name="Synthetic A"):
    response = home.post("/cases", json={"name": name, "focus": "Presentation test"})
    assert response.status_code == 200, response.text
    return response.json(), response.headers["X-RadiWorks-Case-Ref"]


def profile_payload(case, ref, version, **changes):
    body = {
        "expected_case_ref": ref,
        "expected_context_version": case["contextVersion"],
        "expected_profile_version": version,
        "audio_profile": "original",
        "stage_seconds": 60,
        "repeat": False,
        "images": [],
    }
    body.update(changes)
    return body


def get_profile(home, case, ref):
    response = home.get(
        "/presentation-profile",
        params={"case_ref": ref, "context_version": case["contextVersion"]},
    )
    assert response.status_code == 200, response.text
    return response.json()["profile"]


def put_profile(home, case, ref, version, **changes):
    return home.put(
        "/presentation-profile",
        json=profile_payload(case, ref, version, **changes),
    )


def png(marker):
    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    pixels = b"\x00" + bytes((marker, marker ^ 0x55, marker ^ 0xAA, 255))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(pixels))
        + chunk(b"IEND", b"")
    )


def upload_presentation_image(home, data):
    return home.post(
        "/presentation-images",
        json={"pngBase64": base64.b64encode(data).decode("ascii")},
    )


def disable_broadcast_worker(monkeypatch):
    monkeypatch.setattr(STATE.state.broadcast, "_start_thread", lambda: None)


def assert_profile(profile, *, version, audio_profile, seconds, repeat, images):
    assert set(profile) == {
        "schemaVersion", "caseId", "version", "audioProfile",
        "stageSeconds", "repeat", "images", "digest",
    }
    assert profile["schemaVersion"] == 1
    assert profile["version"] == version
    assert profile["audioProfile"] == audio_profile
    assert profile["stageSeconds"] == seconds
    assert profile["repeat"] is repeat
    assert profile["images"] == images
    assert profile["digest"] == document_digest(
        {key: value for key, value in profile.items() if key != "digest"}
    )


def assert_frozen_presentation(row, *, case_id=None, audio_profile="original"):
    presentation = row["presentation"]
    assert set(presentation) == {
        "schemaVersion", "broadcastId", "targetDigest", "profile", "digest",
    }
    assert presentation["schemaVersion"] == 1
    assert presentation["broadcastId"] == row["broadcastId"]
    target = STATE.state.broadcast_targets.get(row["targetReference"]["jobId"])
    assert presentation["targetDigest"] == target["target"]["digest"]
    assert presentation["digest"] == document_digest(
        {key: value for key, value in presentation.items() if key != "digest"}
    )
    assert presentation["profile"]["audioProfile"] == audio_profile
    if case_id is not None:
        assert presentation["profile"]["caseId"] == case_id
    return presentation


def test_profile_defaults_and_updates_use_separate_case_and_context_cas(home):
    first, first_ref = new_case(home)
    default = get_profile(home, first, first_ref)
    assert_profile(default, version=0, audio_profile="original", seconds=60, repeat=False, images=[])

    stale_ref = "0" * 64
    assert put_profile(home, first, stale_ref, 0, audio_profile="off").status_code == 409
    assert put_profile(
        home, first, first_ref, 0,
        expected_context_version=first["contextVersion"] + 1,
        audio_profile="off",
    ).status_code == 409

    saved = put_profile(
        home, first, first_ref, 0,
        audio_profile="fixed-432", stage_seconds=37, repeat=True,
    )
    assert saved.status_code == 200, saved.text
    assert_profile(
        saved.json()["profile"], version=1, audio_profile="fixed-432",
        seconds=37, repeat=True, images=[],
    )
    assert put_profile(home, first, first_ref, 0, audio_profile="off").status_code == 409
    for invalid in (
        {"stage_seconds": 0}, {"stage_seconds": 601},
        {"audio_profile": "gv-to-hz"}, {"repeat": 0},
        {"gv_to_hz": True},
    ):
        assert put_profile(home, first, first_ref, 1, **invalid).status_code == 422

    second, second_ref = new_case(home, "Synthetic B")
    second_profile = get_profile(home, second, second_ref)
    assert_profile(second_profile, version=0, audio_profile="original", seconds=60, repeat=False, images=[])
    stale = home.get("/presentation-profile", params={"case_ref": first_ref, "context_version": first["contextVersion"]})
    assert stale.status_code == 409


def test_presentation_images_are_bounded_and_profile_refs_must_exist(home):
    case, ref = new_case(home)
    refs = []
    for marker in range(1, 7):
        data = png(marker)
        response = upload_presentation_image(home, data)
        assert response.status_code == 200, response.text
        image = response.json()["image"]
        assert image == {
            "sha256": hashlib.sha256(data).hexdigest(),
            "mediaType": "image/png",
            "byteLength": len(data),
        }
        refs.append(image["sha256"])
        fetched = home.get(f"/presentation-images/{image['sha256']}")
        assert fetched.status_code == 200
        assert fetched.content == data

    assert any(
        "presentation-images" in path.parts
        for path in STATE.state.case_store.cases_dir.rglob("*.png")
    )
    too_many = put_profile(
        home, case, ref, 0, images=refs[:6],
    )
    assert too_many.status_code == 422, too_many.text
    missing = put_profile(
        home, case, ref, 0, images=[refs[0], "f" * 64],
    )
    assert missing.status_code in (404, 409, 422), missing.text
    assert_profile(get_profile(home, case, ref), version=0, audio_profile="original", seconds=60, repeat=False, images=[])

    saved = put_profile(home, case, ref, 0, images=refs[:5])
    assert saved.status_code == 200, saved.text
    assert_profile(
        saved.json()["profile"], version=1, audio_profile="original",
        seconds=60, repeat=False, images=refs[:5],
    )


def test_acceptance_freezes_profile_against_target_and_new_profile_versions(home, monkeypatch):
    case, ref = new_case(home)
    disable_broadcast_worker(monkeypatch)
    first_profile = put_profile(
        home, case, ref, 0, audio_profile="fixed-432",
        stage_seconds=37, repeat=True,
    )
    assert first_profile.status_code == 200, first_profile.text

    first = home.post(
        "/broadcast",
        json={
            "signature": "Synthetic Rate", "seconds": 5,
            "expected_case_ref": ref,
            "expected_context_version": case["contextVersion"],
        },
    )
    assert first.status_code == 200, first.text
    first_receipt = assert_frozen_presentation(
        first.json(), case_id=case["caseId"], audio_profile="fixed-432",
    )
    assert_profile(
        first_receipt["profile"], version=1, audio_profile="fixed-432",
        seconds=37, repeat=True, images=[],
    )
    assert "contextSnapshot" not in first.json()

    changed = put_profile(
        home, case, ref, 1, audio_profile="fixed-528",
        stage_seconds=91, repeat=False,
    )
    assert changed.status_code == 200, changed.text
    second = home.post(
        "/broadcast",
        json={
            "signature": "Synthetic Rate", "seconds": 5,
            "expected_case_ref": ref,
            "expected_context_version": case["contextVersion"],
        },
    )
    assert second.status_code == 200, second.text
    assert_frozen_presentation(second.json(), case_id=case["caseId"], audio_profile="fixed-528")

    first_stored = STATE.state.broadcast_targets.get(first.json()["targetReference"]["jobId"])
    second_stored = STATE.state.broadcast_targets.get(second.json()["targetReference"]["jobId"])
    assert first_stored["presentation"] == first_receipt
    assert second_stored["presentation"]["profile"]["version"] == 2
    assert first_stored["target"]["contextSnapshot"]["context"] == second_stored["target"]["contextSnapshot"]["context"]
    assert first_stored["target"]["contextSnapshot"]["contextVersion"] == second_stored["target"]["contextSnapshot"]["contextVersion"]
    queued = home.get("/broadcast/queue").json()["queued"]
    assert next(row for row in queued if row["broadcastId"] == first.json()["broadcastId"])["presentation"] == first_receipt
    event = next(
        row for row in STATE.state.event_history
        if row["type"] == "emitter.sequence" and row["payload"]["broadcastId"] == first.json()["broadcastId"]
    )
    assert event["payload"]["presentation"] == first_receipt


def test_image_broadcast_uses_the_same_frozen_profile_contract(home, monkeypatch):
    case, ref = new_case(home)
    disable_broadcast_worker(monkeypatch)
    saved = put_profile(home, case, ref, 0, audio_profile="fixed-42962", stage_seconds=12)
    assert saved.status_code == 200, saved.text
    response = home.post(
        "/images/broadcast",
        json={
            "md5": "a" * 64, "seconds": 5,
            "expected_case_ref": ref,
            "expected_context_version": case["contextVersion"],
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["targetReference"]["source"]["kind"] == "image"
    assert_frozen_presentation(response.json(), case_id=case["caseId"], audio_profile="fixed-42962")


def test_no_case_broadcast_freezes_explicit_default_presentation(home, monkeypatch):
    disable_broadcast_worker(monkeypatch)
    response = home.post("/broadcast", json={"signature": "Synthetic", "seconds": 5})
    assert response.status_code == 200, response.text
    presentation = assert_frozen_presentation(response.json())
    assert presentation["profile"]["caseId"] is None
    assert_profile(
        presentation["profile"], version=0, audio_profile="original",
        seconds=60, repeat=False, images=[],
    )


def test_presentation_from_old_promoted_draft_uses_its_case_profile(home, monkeypatch):
    first_case, first_ref = new_case(home)
    disable_broadcast_worker(monkeypatch)
    saved = put_profile(home, first_case, first_ref, 0, audio_profile="fixed-432")
    assert saved.status_code == 200, saved.text

    analysis = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "seeded", "seed": 42},
    )
    assert analysis.status_code == 200, analysis.text
    draft_id = analysis.json()["draft"]["id"]
    assert home.post(f"/drafts/{draft_id}/transition", json={"status": "ready"}).status_code == 200

    second_case, second_ref = new_case(home, "Later case")
    second_profile = put_profile(home, second_case, second_ref, 0, audio_profile="off")
    assert second_profile.status_code == 200, second_profile.text
    promoted = home.post(f"/drafts/{draft_id}/promote", json={"max_rates": 2})
    assert promoted.status_code == 200, promoted.text
    rows = promoted.json()["broadcastEntries"]
    assert len(rows) == 2
    for row in rows:
        presentation = assert_frozen_presentation(
            row, case_id=first_case["caseId"], audio_profile="fixed-432",
        )
        stored = STATE.state.broadcast_targets.get(row["targetReference"]["jobId"])
        assert stored["target"]["contextSnapshot"]["caseId"] == first_case["caseId"]
        assert presentation["profile"]["version"] == 1


def test_auto_target_freezes_its_case_profile_not_the_current_case(home, monkeypatch):
    case, ref = new_case(home)
    disable_broadcast_worker(monkeypatch)
    assert put_profile(home, case, ref, 0, audio_profile="fixed-432").status_code == 200
    started = home.post(
        "/auto-mode/on",
        json={
            "database": "HOMEOPATHY_Test",
            "expected_case_ref": ref,
            "expected_context_version": case["contextVersion"],
            "mode": "seeded",
            "seed": 4,
        },
    )
    assert started.status_code == 200, started.text
    target = STATE.state.auto._target_template
    changed = put_profile(home, case, ref, 1, audio_profile="fixed-528")
    assert changed.status_code == 200, changed.text

    later, later_ref = new_case(home, "Unrelated current case")
    assert put_profile(home, later, later_ref, 0, audio_profile="off").status_code == 200
    queued = STATE.state.broadcast.enqueue("Synthetic Auto", 5, target=target)
    assert_frozen_presentation(queued, case_id=case["caseId"], audio_profile="fixed-528")
    assert home.post("/auto-mode/off").status_code == 200


def test_personal_source_broadcast_freezes_profile_at_acceptance(home, monkeypatch):
    from test_personal_api import client_context, command, finished, ready

    case, ref = client_context(home)
    ready(monkeypatch)
    disable_broadcast_worker(monkeypatch)
    saved = put_profile(home, case, ref, 0, audio_profile="pink", stage_seconds=49)
    assert saved.status_code == 200, saved.text
    started = home.post("/personal-analyses", json=command(case, ref))
    assert started.status_code == 200, started.text
    job = finished(home, started.json(), ref)
    row = job["rows"][0]
    response = home.post(
        "/broadcast",
        json={
            "signature": row["rate"], "seconds": 5,
            "source_personal_job_id": job["id"],
            "source_personal_input_index": row["inputIndex"],
        },
    )
    assert response.status_code == 200, response.text
    assert_frozen_presentation(response.json(), case_id=case["caseId"], audio_profile="pink")


def test_profile_changes_do_not_shift_analysis_or_broadcast_rng(home, monkeypatch):
    case, ref = new_case(home)
    disable_broadcast_worker(monkeypatch)
    before = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "seeded", "seed": 42},
    )
    assert before.status_code == 200, before.text
    assert put_profile(home, case, ref, 0, audio_profile="off").status_code == 200
    queued = home.post(
        "/broadcast",
        json={
            "signature": "Synthetic Rate", "seconds": 5,
            "expected_case_ref": ref,
            "expected_context_version": case["contextVersion"],
        },
    )
    assert queued.status_code == 200, queued.text
    after = home.post(
        "/analysis", json={"database": "HOMEOPATHY_Test", "mode": "seeded", "seed": 42},
    )
    assert after.status_code == 200, after.text
    assert before.json()["result"] == after.json()["result"]
    assert queued.json()["entropy"] == {
        "mode": "seeded", "source": "seeded", "drawCount": 0, "seed": 0,
    }
    assert queued.json()["presentation"]["profile"]["audioProfile"] == "off"


def test_existing_acceptance_receipts_without_presentation_remain_loadable(tmp_path):
    from radiworks.core.broadcast_target import BroadcastTarget, BroadcastTargetStore
    from radiworks.scope import ScopeContext

    scope = ScopeContext("tenant-a", "client-a", "job-a")
    target = BroadcastTarget.capture(scope=scope, source={"kind": "direct"})
    store = BroadcastTargetStore(tmp_path, scope)
    store.accept([{
        "broadcastId": "a" * 32, "signature": "Synthetic", "seconds": 5,
        "multiplier": 1, "clear": False, "delayMs": 1, "repeat": 1,
        "target": target.payload(),
    }])
    restarted = BroadcastTargetStore(tmp_path, scope)
    loaded = restarted.get(target.payload()["jobId"])
    assert loaded is not None
    assert "presentation" not in loaded






def test_profile_and_image_namespaces_are_isolated_by_scope(tmp_path):
    from radiworks.core.context_images import ContextImageError
    from radiworks.core.presentation_profile import PresentationProfileStore
    from radiworks.scope import ScopeContext

    cases_dir = tmp_path / "cases"
    scope_a = ScopeContext("tenant-a", "client-a", "job-a")
    scope_b = ScopeContext("tenant-b", "client-a", "job-a")
    first = PresentationProfileStore(cases_dir, scope_a)
    second = PresentationProfileStore(cases_dir, scope_b)
    case_id = "a" * 32
    data = png(22)
    image = first.put_image(data)
    saved = first.update(
        case_id=case_id, expected_version=0, audio_profile="pink",
        stage_seconds=24, repeat=True, images=[image["sha256"]],
    )
    assert saved["version"] == 1
    assert first.get(case_id)["audioProfile"] == "pink"
    assert second.get(case_id)["version"] == 0
    assert second.get(case_id)["audioProfile"] == "original"
    with pytest.raises((OSError, ContextImageError)):
        second.get_image(image["sha256"])

    second.put_image(data)
    assert len(list((cases_dir / "presentation-images").rglob("*.png"))) == 2


def test_broadcast_receipt_revalidates_presentation_target_binding(tmp_path):
    from radiworks.core.broadcast_target import BroadcastTarget, BroadcastTargetError, BroadcastTargetStore
    from radiworks.core.presentation_profile import PresentationProfileStore
    from radiworks.scope import ScopeContext

    scope = ScopeContext("tenant-a", "client-a", "job-a")
    profiles = PresentationProfileStore(tmp_path / "cases", scope)
    targets_dir = tmp_path / "targets"
    store = BroadcastTargetStore(
        targets_dir, scope, presentation_resolver=profiles.freeze_for_target,
    )
    target = BroadcastTarget.capture(scope=scope, source={"kind": "direct"})
    store.accept([{
        "broadcastId": "b" * 32, "signature": "Synthetic", "seconds": 5,
        "multiplier": 1, "clear": False, "delayMs": 1, "repeat": 1,
        "target": target.payload(),
    }])
    path = next(targets_dir.glob("*.receipt.json"))
    record = json.loads(path.read_text(encoding="utf-8"))
    record["entries"][0]["presentation"]["targetDigest"] = "0" * 64
    record["digest"] = document_digest({key: value for key, value in record.items() if key != "digest"})
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(BroadcastTargetError, match="Präsentationsbeleg"):
        BroadcastTargetStore(
            targets_dir, scope, presentation_resolver=profiles.freeze_for_target,
        )


def test_acceptance_batch_with_one_bad_presentation_writes_no_receipt(tmp_path):
    from radiworks.core.broadcast_target import BroadcastTarget, BroadcastTargetError, BroadcastTargetStore
    from radiworks.core.presentation_profile import PresentationProfileError, default_profile, make_presentation_receipt
    from radiworks.scope import ScopeContext

    scope = ScopeContext("tenant-a", "client-a", "job-a")
    target_a = BroadcastTarget.capture(scope=scope, source={"kind": "direct"})
    target_b = BroadcastTarget.capture(scope=scope, source={"kind": "direct"})

    def freeze(target, broadcast_id):
        if broadcast_id == "2" * 32:
            raise PresentationProfileError("synthetic missing image", "image_unavailable")
        return make_presentation_receipt(default_profile(None), broadcast_id, target["digest"])

    targets_dir = tmp_path / "targets"
    store = BroadcastTargetStore(targets_dir, scope, presentation_resolver=freeze)
    entries = [
        {
            "broadcastId": bid, "signature": "Synthetic", "seconds": 5,
            "multiplier": 1, "clear": False, "delayMs": 1, "repeat": 1,
            "target": target.payload(),
        }
        for bid, target in (("1" * 32, target_a), ("2" * 32, target_b))
    ]
    with pytest.raises(BroadcastTargetError, match="synthetic missing image"):
        store.accept(entries)
    assert list(targets_dir.glob("*.receipt.json")) == []
    assert store.get(target_a.payload()["jobId"]) is None



