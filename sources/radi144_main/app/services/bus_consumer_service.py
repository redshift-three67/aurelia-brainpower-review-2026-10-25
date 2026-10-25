"""R-10..R-14: Bus-Consumer-Service fuer Radi144.

Spiegelt ME2s generischen Consumer-Helfer ``consume_bus_messages`` (M-2):
Auto-Cursor-Resume aus der subscription (since_message_id), pro-Envelope
``verify()`` + Safety-Assertion, auto_ack optional (at-least-once default),
Tamper-Reject ohne Abbruch (sammelt rejects, wirft nicht — Batch bleibt stabil).

Autark: nutzt nur ``app.interchange_bus`` (stdlib-only). KEIN publish, KEIN
Netzwerk (Loopback/offline-safe). Finale Verdrahtung auf Debian-Server.
"""
from __future__ import annotations

from typing import Any

from ..interchange_bus import (
    BusConsumerStore,
    BusEnvelope,
    Topic,
    is_allowed_schema_ref,
    topic_values,
)

# Safety-Invarianten (M-1 §8) — jede gelesene Nachricht MUSS sie erfuellen.
_SAFETY_REQUIRED = {
    "real_output_enabled": False,
    "medical_claims": 0,
}


def _assert_safety(envelope: BusEnvelope) -> dict[str, Any] | None:
    """Liefert ein Verletzungs-Dict falls Safety-Marker driften, sonst None."""
    s = envelope.safety or {}
    for key, expected in _SAFETY_REQUIRED.items():
        if s.get(key) != expected:
            return {
                "violation": "safety_marker_drift",
                "field": key,
                "expected": expected,
                "actual": s.get(key),
                "message_id": envelope.message_id,
            }
    return None


def consume_bus_messages(
    subscriber_module_id: str,
    topic: str | Topic,
    bus_db: str,
    *,
    limit: int = 100,
    since_message_id: str | None = None,
    auto_ack: bool = False,
) -> dict[str, Any]:
    """Konsumiere Bus-Nachrichten zu ``topic``. Generisch, plattformweit nutzbar.

    Ablauf (M-2):
      1. BusConsumerStore oeffnen (Schema-Bootstrap idempotent).
      2. Cursor-Resume: wenn ``since_message_id`` None, aus subscription holen.
      3. poll(limit) → Liste BusEnvelope.
      4. Pro Envelope: verify() (Tamper-Check) + schema_ref erlaubt + Safety-Assertion.
         Tamper/Verstoss → reject (NICHT werfen; Batch bleibt stabil).
      5. auto_ack: letzte gueltige message_id in subscription setzen.
      6. Return ``{subscriber, topic, consumed, verified, rejected, last_message_id, auto_acked}``.

    at-least-once default: ohne auto_ack bleibt der Cursor unveraendert →
    Neu-Poll liefert dieselben Nachrichten (idempotent durch verify/content_hash).
    """
    store = BusConsumerStore(bus_db)
    topic_str = Topic(topic).value if not isinstance(topic, Topic) else topic.value

    cursor = since_message_id
    if cursor is None:
        sub = store.subscription(subscriber_module_id, topic_str)
        if sub is not None and sub.get("last_seen_message_id"):
            cursor = sub["last_seen_message_id"]

    envelopes = store.poll(subscriber_module_id, topic_str, limit=limit, since_message_id=cursor)

    consumed = 0
    verified = 0
    rejects: list[dict[str, Any]] = []
    last_message_id: str | None = None

    for env in envelopes:
        consumed += 1
        if not env.verify():
            rejects.append({"violation": "tamper", "message_id": env.message_id})
            continue
        if not is_allowed_schema_ref(topic_str, env.schema_ref):
            rejects.append({
                "violation": "disallowed_schema_ref",
                "message_id": env.message_id,
                "schema_ref": env.schema_ref,
            })
            continue
        bad = _assert_safety(env)
        if bad is not None:
            rejects.append(bad)
            continue
        verified += 1
        last_message_id = env.message_id

    acked = False
    if auto_ack and last_message_id is not None:
        store.ack(subscriber_module_id, last_message_id)
        acked = True

    return {
        "subscriber": subscriber_module_id,
        "topic": topic_str,
        "consumed": consumed,
        "verified": verified,
        "rejected": len(rejects),
        "rejects": rejects,
        "cursor_before": cursor,
        "last_message_id": last_message_id,
        "auto_acked": acked,
        "store_schema": store.status()["store_schema"],
    }


class Radi144BusConsumer:
    """Duenn-Wrapper fuer die plattformweite ``consume_bus_messages`` mit
    festem subscriber ``"radi144"``. Erlaubt der Applikation, den Consumer
    an einer Stelle zu konfigurieren (z.B. Module-Registry bei Start)."""

    MODULE_ID = "radi144"
    MODULE_KIND = "consumer"

    def __init__(self, bus_db: str):
        self.bus_db = bus_db
        self._store = BusConsumerStore(bus_db)
        self._store.register_module(
            module_id=self.MODULE_ID,
            module_kind=self.MODULE_KIND,
            capabilities={"topics": list(topic_values()), "publish": False},
        )

    def consume(self, topic: str | Topic, *, limit: int = 100, auto_ack: bool = False) -> dict[str, Any]:
        return consume_bus_messages(
            self.MODULE_ID, topic, self.bus_db, limit=limit, auto_ack=auto_ack,
        )

    def status(self) -> dict[str, Any]:
        return self._store.status()