"""R-10/R-11: Consumer-seitiger BusStore — liest/schreibt die geteilte BusDB.

Autark (stdlib-only, keine ME2-Imports). Oeffnet dieselbe BusDB-Datei die ME2
published (Schema ``me2.interchange_bus_store.v1``). Bootstrapped das Schema
idempotent (``CREATE TABLE IF NOT EXISTS``), sodass Radi144 auch eine frische
BusDB oeffnen kann (ME2 legt sie normalerweise an — aber idempotent ist sicher).

Consumer-Scope: ``register_module``/``poll``/``ack``/``subscription``/
``list_messages``/``append_audit``. KEIN publish (Radi144 ist Consumer im MVP).
Finale Verdrahtung auf Debian-Server, nicht vorab im Code.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .envelope import BusEnvelope, canonical_sha256, Action, SubjectKind

STORE_SCHEMA_VERSION = "me2.interchange_bus_store.v1"

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS interchange_bus_store_schema (
    schema_version TEXT PRIMARY KEY,
    applied_at_utc TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bus_messages (
    message_id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    producer_module_id TEXT NOT NULL,
    schema_ref TEXT NOT NULL,
    subject_kind TEXT NOT NULL DEFAULT 'none',
    subject_value TEXT NOT NULL DEFAULT '',
    content_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    acl_json TEXT NOT NULL DEFAULT '[]',
    safety_json TEXT NOT NULL,
    real_output_enabled INTEGER NOT NULL DEFAULT 0,
    medical_claims INTEGER NOT NULL DEFAULT 0,
    created_at_utc TEXT NOT NULL,
    CHECK (real_output_enabled = 0),
    CHECK (medical_claims = 0),
    CHECK (json_valid(payload_json)),
    CHECK (json_valid(safety_json)),
    CHECK (json_valid(acl_json))
);
CREATE INDEX IF NOT EXISTS idx_bus_messages_topic ON bus_messages(topic);
CREATE INDEX IF NOT EXISTS idx_bus_messages_subject ON bus_messages(subject_kind, subject_value);
CREATE TABLE IF NOT EXISTS bus_subscriptions (
    subscriber_module_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    last_seen_message_id TEXT,
    updated_at_utc TEXT NOT NULL,
    PRIMARY KEY (subscriber_module_id, topic)
);
CREATE TABLE IF NOT EXISTS bus_module_registry (
    module_id TEXT PRIMARY KEY,
    module_kind TEXT NOT NULL,
    capabilities_json TEXT NOT NULL DEFAULT '{}',
    registered_at_utc TEXT NOT NULL,
    CHECK (json_valid(capabilities_json))
);
CREATE TABLE IF NOT EXISTS bus_audit_log (
    event_id TEXT PRIMARY KEY,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    subject_kind TEXT NOT NULL DEFAULT 'none',
    subject_value TEXT NOT NULL DEFAULT '',
    outcome TEXT NOT NULL,
    detail_json TEXT NOT NULL DEFAULT '{}',
    created_at_utc TEXT NOT NULL,
    CHECK (json_valid(detail_json))
);
CREATE INDEX IF NOT EXISTS idx_bus_audit_subject ON bus_audit_log(subject_kind, subject_value);
"""


def _utc_now() -> str:
    """ISO-8601 UTC mit Z-Suffix. (Kein Date.now im Core-Vertrag; hier Hilfsfunktion
    fuer Audit-Zeitstempel — Consumer darf eigene Zeit setzen.)"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class BusConsumerStore:
    """Consumer-seitiger Zugriff auf die geteilte BusDB (kein publish)."""

    def __init__(self, db_path: str | Path):
        path = Path(db_path).resolve()
        if not path.is_absolute():
            raise ValueError("bus db_path must be absolute")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = path
        self._bootstrap()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self.db_path))
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def _bootstrap(self) -> None:
        with self._connect() as con:
            con.executescript(_SCHEMA_SQL)
            row = con.execute(
                "SELECT schema_version FROM interchange_bus_store_schema WHERE schema_version = ?",
                (STORE_SCHEMA_VERSION,),
            ).fetchone()
            if row is None:
                con.execute(
                    "INSERT OR IGNORE INTO interchange_bus_store_schema(schema_version, applied_at_utc) VALUES (?, ?)",
                    (STORE_SCHEMA_VERSION, _utc_now()),
                )
            con.commit()

    # ------------------------------------------------------------------ registry
    def register_module(
        self, *, module_id: str, module_kind: str, capabilities: dict[str, Any] | None = None,
        created_at_utc: str | None = None,
    ) -> dict[str, Any]:
        caps = capabilities or {}
        ts = created_at_utc or _utc_now()
        with self._connect() as con:
            con.execute(
                "INSERT OR REPLACE INTO bus_module_registry(module_id, module_kind, capabilities_json, registered_at_utc) VALUES (?, ?, ?, ?)",
                (module_id, module_kind, json.dumps(caps, sort_keys=True, ensure_ascii=False), ts),
            )
            con.commit()
        self.append_audit(
            actor=module_id, action=Action.REGISTER.value,
            entity_type="module", entity_id=module_id,
            outcome="ok", detail={"module_kind": module_kind, "capabilities": caps},
            created_at_utc=ts,
        )
        return {"module_id": module_id, "module_kind": module_kind, "capabilities": caps, "registered_at_utc": ts}

    def list_registry(self) -> list[dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute("SELECT * FROM bus_module_registry ORDER BY registered_at_utc ASC").fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ poll/ack
    def poll(
        self, subscriber_module_id: str, topic: str, *, limit: int = 100,
        since_message_id: str | None = None,
    ) -> list[BusEnvelope]:
        with self._connect() as con:
            if since_message_id is not None:
                ref = con.execute(
                    "SELECT rowid FROM bus_messages WHERE message_id = ?", (since_message_id,)
                ).fetchone()
                if ref is None:
                    raise ValueError(f"since_message_id {since_message_id!r} nicht in bus_messages")
                rows = con.execute(
                    "SELECT * FROM bus_messages WHERE topic = ? AND rowid > ? ORDER BY rowid ASC LIMIT ?",
                    (topic, int(ref["rowid"]), limit),
                ).fetchall()
            else:
                rows = con.execute(
                    "SELECT * FROM bus_messages WHERE topic = ? ORDER BY rowid ASC LIMIT ?",
                    (topic, limit),
                ).fetchall()
        return [BusEnvelope.from_payload(json.loads(r["payload_json"])) for r in rows]

    def subscription(self, subscriber_module_id: str, topic: str) -> dict[str, Any] | None:
        with self._connect() as con:
            row = con.execute(
                "SELECT * FROM bus_subscriptions WHERE subscriber_module_id = ? AND topic = ?",
                (subscriber_module_id, topic),
            ).fetchone()
        return dict(row) if row else None

    def ack(self, subscriber_module_id: str, message_id: str, *, created_at_utc: str | None = None) -> dict[str, Any]:
        ts = created_at_utc or _utc_now()
        with self._connect() as con:
            row = con.execute("SELECT topic FROM bus_messages WHERE message_id = ?", (message_id,)).fetchone()
            if row is None:
                raise ValueError(f"message_id {message_id!r} nicht in bus_messages (cannot ack)")
            topic = row["topic"]
            con.execute(
                "INSERT OR REPLACE INTO bus_subscriptions(subscriber_module_id, topic, last_seen_message_id, updated_at_utc) VALUES (?, ?, ?, ?)",
                (subscriber_module_id, topic, message_id, ts),
            )
            con.commit()
        self.append_audit(
            actor=subscriber_module_id, action=Action.ACK.value,
            entity_type="bus_message", entity_id=message_id,
            outcome="ok", detail={"topic": topic}, created_at_utc=ts,
        )
        return {"subscriber": subscriber_module_id, "topic": topic, "last_seen_message_id": message_id, "updated_at_utc": ts}

    def list_messages(self, topic: str | None = None, *, limit: int = 100) -> list[BusEnvelope]:
        with self._connect() as con:
            if topic:
                rows = con.execute(
                    "SELECT * FROM bus_messages WHERE topic = ? ORDER BY rowid ASC LIMIT ?", (topic, limit)
                ).fetchall()
            else:
                rows = con.execute(
                    "SELECT * FROM bus_messages ORDER BY rowid ASC LIMIT ?", (limit,)
                ).fetchall()
        return [BusEnvelope.from_payload(json.loads(r["payload_json"])) for r in rows]

    # ------------------------------------------------------------------ audit (append-only)
    def append_audit(
        self, *, actor: str, action: str, entity_type: str, entity_id: str,
        subject_kind: str = SubjectKind.NONE.value, subject_value: str = "",
        outcome: str = "ok", detail: dict[str, Any] | None = None,
        created_at_utc: str | None = None,
    ) -> dict[str, Any]:
        ts = created_at_utc or _utc_now()
        detail_json = json.dumps(detail or {}, sort_keys=True, ensure_ascii=False)
        event_payload = {
            "actor": actor, "action": action, "entity_type": entity_type, "entity_id": entity_id,
            "subject_kind": subject_kind, "subject_value": subject_value,
            "outcome": outcome, "detail_json": detail_json, "created_at_utc": ts,
        }
        event_id = canonical_sha256(event_payload)
        with self._connect() as con:
            con.execute(
                "INSERT OR IGNORE INTO bus_audit_log(event_id, actor, action, entity_type, entity_id, subject_kind, subject_value, outcome, detail_json, created_at_utc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (event_id, actor, action, entity_type, entity_id, subject_kind, subject_value, outcome, detail_json, ts),
            )
            con.commit()
        return {"event_id": event_id, **event_payload}

    def status(self) -> dict[str, Any]:
        with self._connect() as con:
            messages = con.execute("SELECT COUNT(*) AS c FROM bus_messages").fetchone()["c"]
            subs = con.execute("SELECT COUNT(*) AS c FROM bus_subscriptions").fetchone()["c"]
            modules = con.execute("SELECT COUNT(*) AS c FROM bus_module_registry").fetchone()["c"]
            audit = con.execute("SELECT COUNT(*) AS c FROM bus_audit_log").fetchone()["c"]
        return {
            "store_schema": STORE_SCHEMA_VERSION,
            "bus_messages": messages,
            "bus_subscriptions": subs,
            "bus_module_registry": modules,
            "bus_audit_log": audit,
            "db_path": str(self.db_path),
        }