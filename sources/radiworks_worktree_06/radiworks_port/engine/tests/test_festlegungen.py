"""Tests der drei Festlegungen vom 2026-08-29 (siehe Modul_Templates FESTLEGUNGEN)."""

import json
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient

from radiworks.core.emitter import emitter_sequence
from radiworks.main import create_app
from radiworks.api.routes import STATE


@contextmanager
def _client(tmp_path: Path, settings: dict | None = None):
    data = tmp_path / "data"
    data.mkdir(parents=True)
    (data / "HOMEOPATHY_Test.txt").write_text("Abrotanum\nAbsinthium\nArnica\n", encoding="utf-8")
    config = tmp_path / "config"
    config.mkdir()
    if settings:
        (config / "Settings.json").write_text(json.dumps(settings), encoding="utf-8")
    app = create_app(base_dir=tmp_path, data_dir=data)
    with TestClient(app) as client:
        yield client
    STATE.state = None


def test_festlegung_1_default_mode_seeded(tmp_path):
    with _client(tmp_path / "a") as c:
        status = c.get("/entropy/status").json()
        assert status["defaultMode"] == "seeded"
        assert status["factoryDefault"] == "seeded"


def test_festlegung_1_settings_switch_to_stochastic(tmp_path):
    settings = {"name": "Settings", "booleans": {}, "integers": {}, "strings": {"entropy.defaultMode": "stochastic"}}
    with _client(tmp_path / "b", settings) as c:
        assert c.get("/entropy/status").json()["defaultMode"] == "stochastic"
        # stochastischer Lauf laeuft und protokolliert seinen Modus im Passport
        run = c.post("/analysis", json={"database": "HOMEOPATHY_Test"}).json()
        assert run["passport"]["entropy_mode"] == "stochastic"


def test_festlegung_1_invalid_mode_rejected(tmp_path):
    with _client(tmp_path / "c") as c:
        assert (
            c.post("/analysis", json={"database": "HOMEOPATHY_Test", "mode": "quantum"}).status_code
            == 422
        )


def test_festlegung_2_mix_blocked_without_legacy(tmp_path):
    with _client(tmp_path / "d") as c:
        run = c.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 1}).json()
        draft_id = run["draft"]["id"]
        response = c.post("/broadcast/mix", json={"draft_id": draft_id})
        assert response.status_code == 409
        assert "legacyMixMode" in response.json()["detail"]


def test_festlegung_2_legacy_mix_one_click(tmp_path):
    settings = {
        "name": "Settings",
        "booleans": {"broadcast.legacyMixMode": True},
        "integers": {},
        "strings": {},
    }
    with _client(tmp_path / "e", settings) as c:
        run = c.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 1}).json()
        draft_id = run["draft"]["id"]
        response = c.post(
            "/broadcast/mix",
            json={"draft_id": draft_id, "max_rates": 2, "seconds_per_rate": 30},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "promoted"
        queue = c.get("/broadcast/queue").json()
        assert queue["queued"] or queue["active"]
        c.delete("/broadcast/all")


def test_festlegung_2_legacy_mix_still_copyguard_guarded(tmp_path):
    """Auch im Legacy-Einklick blockt CopyGuard fail-closed den Promote."""
    settings = {
        "name": "Settings",
        "booleans": {"broadcast.legacyMixMode": True},
        "integers": {},
        "strings": {},
    }
    with _client(tmp_path / "f", settings) as c:
        # Direkt manipulierten Draft erzeugen: Rate mit Heilbegriff
        run = c.post("/analysis", json={"database": "HOMEOPATHY_Test", "seed": 2}).json()
        draft_id = run["draft"]["id"]
        # Draft-Payload manipulieren (Storage-seitig, wie ein importierter Text)
        draft = c.get(f"/drafts/{draft_id}").json()
        assert draft["copyguard_verdict"] == "allow"
        from radiworks.api.routes import STATE

        store = STATE.state.draft_store
        stored = store.get(draft_id)
        stored["payload"]["rateObjects"][0]["nameOrRate"] = "Krebs heilt garantiert"
        store._write(stored)
        response = c.post("/broadcast/mix", json={"draft_id": draft_id})
        assert response.status_code == 409
        assert "CopyGuard" in response.json()["detail"]


def test_festlegung_3_emitter_sequence_matches_original():
    """Choreografie exakt nach BroadCastService.broadcastNow."""
    steps = emitter_sequence("AB 19-D")
    cleaned = "AB19D"
    assert [s.char for s in steps] == list(cleaned)
    # 'A' = 65 -> 65-48 = 17 -> Ziffern 1,7 -> infrared(1), green(7)
    a = steps[0]
    assert a.digit_sequence == [1, 7]
    assert a.lit_groups == [["infrared"], ["greens"]]
    # '1' -> Ziffer 1 -> infrared
    assert steps[2].lit_groups == [["infrared"]]
    # '9' -> Ziffer 9 -> whites
    assert steps[3].digit_sequence == [9]
    assert steps[3].lit_groups == [["whites"]]
    # Clear-Modus: ZAHLENLISTE infrared [1,6] treibt den ULTRAVIOLET-Pin
    # (Java: blinkLED(data, n, this.infrared, AetherOnePins.ULTRAVIOLET))
    clear_steps = emitter_sequence("19", clear=True)
    assert clear_steps[0].lit_groups == [["ultraviolet"]]
    assert clear_steps[1].lit_groups == [[]]
    # Defaults wie BroadCastData
    assert all(s.delay_ms == 25 and s.repeat == 1 for s in steps)


def test_festlegung_3_broadcast_emits_sequence_event(tmp_path):
    with _client(tmp_path / "g") as c:
        c.post("/broadcast", json={"signature": "TEST 12", "seconds": 1})
        state_events = [
            e for e in STATE.state.event_history if e["type"] == "emitter.sequence"
        ]
        assert state_events, "emitter.sequence muss im Fachkanal liegen"
        payload = state_events[-1]["payload"]
        assert payload["signature"] == "TEST 12"
        assert len(payload["steps"]) == len("TEST12")
        c.delete("/broadcast/all")
