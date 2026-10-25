"""R-10..R-14: Bus-Consumer-Tests fuer Radi144.

Simuliert einen ME2-Producer indem Envelopes direkt via BusConsumerStore in die
BusDB geschrieben werden (Consumer-Store hat keinen publish-Pfad, deshalb hier
rohes INSERT ueber eine Test-Hilfe). Prueft: register/poll/verify/safety-assert/
auto_ack-cursor/tamper-reject/schema_ref-reject — alles ohne Abbruch des Batches.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

import pytest

from app.interchange_bus import (
    BusConsumerStore,
    BusEnvelope,
    SubjectKind,
    Topic,
    build_envelope,
    canonical_sha256,
    is_allowed_schema_ref,
    topic_values,
)
from app.interchange_bus.consumer_store import STORE_SCHEMA_VERSION
from app.services.bus_consumer_service import (
    Radi144BusConsumer,
    consume_bus_messages,
)

FIXED_TS = "2026-06-27T10:00:00Z"


# ------------------------------------------------------------------ helpers
def _open_busdb(tmp_path: Path) -> Path:
    db = tmp_path / "bus.db"
    # bootstrap via store (idempotent schema)
    BusConsumerStore(db)
    return db


def _insert_envelope(db_path: Path, env: BusEnvelope) -> None:
    """Simuliert ME2-Publish: schreibt ein fertiges Envelope in bus_messages.
    Setzt real_output_enabled/medical_claims konsistent zur safety."""
    con = sqlite3.connect(str(db_path))
    payload_json = json.dumps(env.to_payload(), ensure_ascii=False, sort_keys=True)
    safety_json = json.dumps(env.safety, ensure_ascii=False, sort_keys=True)
    acl_json = json.dumps(list(env.acl), ensure_ascii=False, sort_keys=True)
    con.execute(
        "INSERT OR REPLACE INTO bus_messages(message_id, topic, producer_module_id, schema_ref, subject_kind, subject_value, content_hash, payload_json, acl_json, safety_json, real_output_enabled, medical_claims, created_at_utc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            env.message_id, env.topic, env.producer.get("module_id", "me2"),
            env.schema_ref, env.subject_ref["kind"], env.subject_ref["value"],
            env.content_hash, payload_json, acl_json, safety_json,
            int(env.safety.get("real_output_enabled", False)),
            int(env.safety.get("medical_claims", 0)),
            env.created_at_utc,
        ),
    )
    con.commit()
    con.close()


def _make_scan_result_env(*, payload=None, subject_kind=SubjectKind.NONE, subject_value="", tamper=False) -> BusEnvelope:
    env = build_envelope(
        topic=Topic.SCAN_RESULT,
        producer_module_id="me2",
        producer_module_kind="producer",
        schema_ref="me2.v2_autoscan.v1",
        payload=payload or {"combined_top_items": [], "analysis_mode": "hybrid_observed"},
        subject_kind=subject_kind,
        subject_value=subject_value,
        created_at_utc=FIXED_TS,
    )
    if tamper:
        # manipulate payload after build → verify() must fail (content_hash mismatch → message_id mismatch)
        object.__setattr__(env, "payload", {**env.payload, "injected": "evil"})
    return env


# ------------------------------------------------------------------ store basics
def test_store_bootstraps_schema_and_status(tmp_path):
    db = _open_busdb(tmp_path)
    store = BusConsumerStore(db)
    status = store.status()
    assert status["store_schema"] == STORE_SCHEMA_VERSION
    assert status["bus_messages"] == 0
    assert status["bus_module_registry"] == 0
    assert os.path.isabs(status["db_path"])


def test_register_module_writes_registry_and_audit(tmp_path):
    import os
    db = _open_busdb(tmp_path)
    store = BusConsumerStore(db)
    res = store.register_module(module_id="radi144", module_kind="consumer", capabilities={"publish": False})
    assert res["module_id"] == "radi144"
    regs = store.list_registry()
    assert len(regs) == 1 and regs[0]["module_id"] == "radi144"
    assert store.status()["bus_audit_log"] >= 1


# ------------------------------------------------------------------ poll + verify
def test_poll_returns_envelopes_and_verify_passes(tmp_path):
    import os
    db = _open_busdb(tmp_path)
    env = _make_scan_result_env()
    _insert_envelope(db, env)
    store = BusConsumerStore(db)
    out = store.poll("radi144", Topic.SCAN_RESULT.value, limit=10)
    assert len(out) == 1
    assert out[0].verify() is True
    assert out[0].message_id == env.message_id


def test_poll_since_cursor_advances(tmp_path):
    db = _open_busdb(tmp_path)
    env1 = _make_scan_result_env(payload={"combined_top_items": [], "analysis_mode": "a"})
    env2 = _make_scan_result_env(payload={"combined_top_items": [], "analysis_mode": "b"})
    _insert_envelope(db, env1)
    _insert_envelope(db, env2)
    store = BusConsumerStore(db)
    first = store.poll("radi144", Topic.SCAN_RESULT.value, limit=10)
    assert len(first) == 2
    second = store.poll("radi144", Topic.SCAN_RESULT.value, limit=10, since_message_id=env1.message_id)
    assert len(second) == 1
    assert second[0].message_id == env2.message_id


# ------------------------------------------------------------------ consume_bus_messages
def test_consume_verifies_and_counts(tmp_path):
    db = _open_busdb(tmp_path)
    env = _make_scan_result_env()
    _insert_envelope(db, env)
    result = consume_bus_messages("radi144", Topic.SCAN_RESULT, str(db), limit=10)
    assert result["consumed"] == 1
    assert result["verified"] == 1
    assert result["rejected"] == 0
    assert result["last_message_id"] == env.message_id
    assert result["auto_acked"] is False


def test_consume_auto_ack_advances_cursor(tmp_path):
    db = _open_busdb(tmp_path)
    env = _make_scan_result_env()
    _insert_envelope(db, env)
    result = consume_bus_messages("radi144", Topic.SCAN_RESULT, str(db), limit=10, auto_ack=True)
    assert result["auto_acked"] is True
    store = BusConsumerStore(db)
    sub = store.subscription("radi144", Topic.SCAN_RESULT.value)
    assert sub is not None
    assert sub["last_seen_message_id"] == env.message_id


def test_consume_auto_ack_cursor_resume_skips_seen(tmp_path):
    db = _open_busdb(tmp_path)
    env1 = _make_scan_result_env(payload={"combined_top_items": [], "analysis_mode": "a"})
    env2 = _make_scan_result_env(payload={"combined_top_items": [], "analysis_mode": "b"})
    _insert_envelope(db, env1)
    _insert_envelope(db, env2)
    # first consume (limit=1) + ack env1
    r1 = consume_bus_messages("radi144", Topic.SCAN_RESULT, str(db), limit=1, auto_ack=True)
    assert r1["verified"] == 1
    assert r1["last_message_id"] == env1.message_id
    # second consume resumes cursor from subscription → only env2
    r2 = consume_bus_messages("radi144", Topic.SCAN_RESULT, str(db), limit=10, auto_ack=True)
    assert r2["consumed"] == 1
    assert r2["last_message_id"] == env2.message_id


def test_consume_rejects_tampered_without_aborting_batch(tmp_path):
    db = _open_busdb(tmp_path)
    good = _make_scan_result_env(payload={"combined_top_items": [], "analysis_mode": "good"})
    bad = _make_scan_result_env(payload={"combined_top_items": [], "analysis_mode": "bad"}, tamper=True)
    _insert_envelope(db, good)
    _insert_envelope(db, bad)
    result = consume_bus_messages("radi144", Topic.SCAN_RESULT, str(db), limit=10)
    assert result["consumed"] == 2
    assert result["verified"] == 1
    assert result["rejected"] == 1
    rejects = result["rejects"]
    assert any(r.get("violation") == "tamper" for r in rejects)
    # batch stayed stable → good one verified, last_message_id is the good one
    assert result["last_message_id"] == good.message_id


def test_consume_rejects_safety_drift(tmp_path):
    """Safety-Drift: ein boesartiger Producer koennte die Spalte real_output_enabled=0
    halten (CHECK ok) aber im eingebetteten payload_json.safety real_output_enabled=True
    tragen. Der Consumer liest via from_payload → envelope.safety und weist das zurueck,
    selbst wenn verify() (Integritaet) True ist."""
    from app.interchange_bus.envelope import BusEnvelope, SCHEMA_VERSION
    db = _open_busdb(tmp_path)
    bad_safety = {"real_output_enabled": True, "medical_claims": 0, "adapter": "dummy"}
    payload = {"analysis_mode": "drift"}
    env = BusEnvelope(
        schema_version=SCHEMA_VERSION, message_id="", topic=Topic.SCAN_RESULT.value,
        producer={"module_id": "me2", "module_kind": "producer"},
        schema_ref="me2.v2_autoscan.v1",
        subject_ref={"kind": "none", "value": ""},
        content_hash=canonical_sha256(payload),
        payload=payload, safety=bad_safety, acl=(), created_at_utc=FIXED_TS,
    )
    mid = canonical_sha256(env._unsigned_payload())
    object.__setattr__(env, "message_id", mid)
    # insert mit SPALTE real_output_enabled=0 (CHECK ok) aber payload_json traegt bad_safety
    con = sqlite3.connect(str(db))
    payload_json = json.dumps(env.to_payload(), ensure_ascii=False, sort_keys=True)
    con.execute(
        "INSERT OR REPLACE INTO bus_messages(message_id, topic, producer_module_id, schema_ref, subject_kind, subject_value, content_hash, payload_json, acl_json, safety_json, real_output_enabled, medical_claims, created_at_utc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (env.message_id, env.topic, "me2", env.schema_ref,
         env.subject_ref["kind"], env.subject_ref["value"], env.content_hash,
         payload_json, "[]", json.dumps(bad_safety, sort_keys=True), 0, 0, FIXED_TS),
    )
    con.commit()
    con.close()
    result = consume_bus_messages("radi144", Topic.SCAN_RESULT, str(db), limit=10)
    assert result["consumed"] == 1
    assert result["verified"] == 0
    assert result["rejected"] == 1
    assert result["rejects"][0]["violation"] == "safety_marker_drift"
    assert result["rejects"][0]["field"] == "real_output_enabled"


def test_consume_rejects_disallowed_schema_ref(tmp_path):
    db = _open_busdb(tmp_path)
    env = build_envelope(
        topic=Topic.SCAN_RESULT, producer_module_id="me2", producer_module_kind="producer",
        schema_ref="me2.v2_autoscan.v1", payload={"ok": True}, created_at_utc=FIXED_TS,
    )
    # rewrite schema_ref in DB to a disallowed value (keep message_id consistent → verify still true,
    # but is_allowed_schema_ref fails)
    con = sqlite3.connect(str(db))
    payload = env.to_payload()
    payload["schema_ref"] = "me2.bogus.v9"
    con.execute(
        "INSERT OR REPLACE INTO bus_messages(message_id, topic, producer_module_id, schema_ref, subject_kind, subject_value, content_hash, payload_json, acl_json, safety_json, real_output_enabled, medical_claims, created_at_utc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (env.message_id, env.topic, "me2", "me2.bogus.v9",
         env.subject_ref["kind"], env.subject_ref["value"], env.content_hash,
         json.dumps(payload, sort_keys=True, ensure_ascii=False), "[]",
         json.dumps(env.safety, sort_keys=True), 0, 0, FIXED_TS),
    )
    con.commit()
    con.close()
    result = consume_bus_messages("radi144", Topic.SCAN_RESULT, str(db), limit=10)
    # verify passes (message_id recomputed from unsigned payload which now includes bogus schema_ref →
    # but message_id was computed with the ORIGINAL schema_ref, so verify FAILS too). Either way rejected.
    assert result["verified"] == 0
    assert result["rejected"] == 1


# ------------------------------------------------------------------ ack
def test_ack_unknown_message_raises(tmp_path):
    db = _open_busdb(tmp_path)
    store = BusConsumerStore(db)
    with pytest.raises(ValueError):
        store.ack("radi144", "nonexistent-id")


def test_ack_records_subscription_and_audit(tmp_path):
    db = _open_busdb(tmp_path)
    env = _make_scan_result_env()
    _insert_envelope(db, env)
    store = BusConsumerStore(db)
    res = store.ack("radi144", env.message_id, created_at_utc=FIXED_TS)
    assert res["last_seen_message_id"] == env.message_id
    sub = store.subscription("radi144", Topic.SCAN_RESULT.value)
    assert sub["last_seen_message_id"] == env.message_id
    assert store.status()["bus_audit_log"] >= 1


# ------------------------------------------------------------------ Radi144BusConsumer
def test_radi144_consumer_registers_and_consumes(tmp_path):
    db = _open_busdb(tmp_path)
    env = _make_scan_result_env()
    _insert_envelope(db, env)
    consumer = Radi144BusConsumer(str(db))
    status = consumer.status()
    assert status["bus_module_registry"] == 1
    result = consumer.consume(Topic.SCAN_RESULT, limit=10, auto_ack=True)
    assert result["verified"] == 1
    assert result["auto_acked"] is True


# ------------------------------------------------------------------ topic vocab + forbidden fields
def test_topic_values_complete():
    vals = topic_values()
    assert set(vals) == {"scan_result", "post_scan_report", "trend_snapshot", "catalog_snapshot"}


def test_is_allowed_schema_ref_known_and_unknown():
    assert is_allowed_schema_ref(Topic.SCAN_RESULT, "me2.v2_autoscan.v1") is True
    assert is_allowed_schema_ref("scan_result", "me2.interactive_scan_result.v1") is True
    assert is_allowed_schema_ref(Topic.SCAN_RESULT, "me2.bogus.v1") is False
    assert is_allowed_schema_ref("not_a_topic", "x") is False


def test_build_envelope_rejects_forbidden_medical_fields():
    with pytest.raises(ValueError, match="verbotene Medical-Felder"):
        build_envelope(
            topic=Topic.SCAN_RESULT, producer_module_id="me2", producer_module_kind="producer",
            schema_ref="me2.v2_autoscan.v1",
            payload={"items": [{"indication": "Schmerzen"}]},
            created_at_utc=FIXED_TS,
        )


def test_canonical_sha256_is_deterministic():
    a = canonical_sha256({"b": 1, "a": 2})
    b = canonical_sha256({"a": 2, "b": 1})
    assert a == b
    assert len(a) == 64