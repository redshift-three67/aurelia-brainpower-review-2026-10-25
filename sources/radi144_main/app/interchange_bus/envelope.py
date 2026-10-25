"""R-10/R-11: BusEnvelope + kanonisches Hashing — Consumer-seitige stdlib-
Reimplementierung der M-1 Consumer-Adapter-SPEC (docs/INTERCHANGE_BUS_CONSUMER_SPEC.md).

Autark: KEINE ME2-Imports. Die Primitive sind identisch zu ME2s
``src/morphic_engine_2/interchange_bus/envelope.py`` spezifiziert, sodass
``canonical_sha256``/``message_id``/``verify()`` moduluebergreifend greifen
(Radi144 liest dieselbe geteilte BusDB und verifiziert ME2-published Envelopes).
Finale Verdrahtung (welche BusDB, welche Topics fliessen) auf dem Debian-Server,
NICHT vorab im Code (konservative Vorbereitung, keine fixe Verdrahtung).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Any

from .topics import Topic, is_allowed_schema_ref

SCHEMA_VERSION = "me2.interchange_bus.v1"

# Identisch zu domain/catalog_import_template.py:41 (ME2) — DSGVO/Medical-Claim-Governance.
FORBIDDEN_MEDICAL_FIELDS: tuple[str, ...] = (
    "indication",
    "diagnosis",
    "therapeutic_use",
    "healing",
    "symptom",
)

# Safety-Marker (IMMER, nicht verhandelbar — M-1 §8). build_envelope hardcodiert sie.
DEFAULT_SAFETY: dict[str, Any] = {
    "real_output_enabled": False,
    "medical_claims": 0,
    "adapter": "dummy",
}


class SubjectKind(StrEnum):
    CLIENT_CODE = "client_code"        # 16-hex
    CLIENT_SIGNATURE = "client_signature"  # 64-hex
    NONE = "none"


class Action(StrEnum):
    PUBLISH = "publish"
    ACK = "ack"
    PURGE = "purge"
    REGISTER = "register"
    QUARANTINE = "quarantine"


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(payload: Any) -> str:
    """Deterministisch, sortiert, kompakt — identisch zu ME2 audit/receipt.py:16."""
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def quarantined_forbidden_fields(payload: Any, *, _path: str = "") -> list[str]:
    """Rekursive Erkennung verbotener Medical-Claim-Felder (case-insensitiv).

    Liefert dotted-Pfade (z.B. ``"items[0].indication"``). Leere Liste = clean.
    """
    hits: list[str] = []
    forbidden = {f.lower() for f in FORBIDDEN_MEDICAL_FIELDS}
    if isinstance(payload, dict):
        for key, value in payload.items():
            here = f"{_path}.{key}" if _path else str(key)
            if str(key).lower() in forbidden:
                hits.append(here)
            hits.extend(quarantined_forbidden_fields(value, _path=here))
    elif isinstance(payload, list):
        for idx, value in enumerate(payload):
            here = f"{_path}[{idx}]"
            hits.extend(quarantined_forbidden_fields(value, _path=here))
    return hits


@dataclass(frozen=True)
class BusEnvelope:
    schema_version: str
    message_id: str
    topic: str
    producer: dict[str, str] = field(default_factory=dict)
    schema_ref: str = ""
    subject_ref: dict[str, str] = field(default_factory=lambda: {"kind": "none", "value": ""})
    content_hash: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    safety: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_SAFETY))
    acl: tuple[str, ...] = field(default_factory=tuple)
    created_at_utc: str = ""

    def to_payload(self) -> dict[str, Any]:
        """Kanonische Serialisierung (``acl`` tuple → list)."""
        data = asdict(self)
        data["acl"] = list(self.acl)
        return data

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "BusEnvelope":
        """Deserialisierung (trusts message_id — verify() separat aufrufen)."""
        acl = payload.get("acl") or ()
        if isinstance(acl, list):
            acl = tuple(acl)
        return cls(
            schema_version=payload.get("schema_version", SCHEMA_VERSION),
            message_id=payload.get("message_id", ""),
            topic=payload.get("topic", ""),
            producer=dict(payload.get("producer") or {}),
            schema_ref=payload.get("schema_ref", ""),
            subject_ref=dict(payload.get("subject_ref") or {"kind": "none", "value": ""}),
            content_hash=payload.get("content_hash", ""),
            payload=dict(payload.get("payload") or {}),
            safety=dict(payload.get("safety") or DEFAULT_SAFETY),
            acl=tuple(acl),
            created_at_utc=payload.get("created_at_utc", ""),
        )

    def _unsigned_payload(self) -> dict[str, Any]:
        data = self.to_payload()
        data.pop("message_id", None)
        return data

    def verify(self) -> bool:
        """Self-certifying Tamper-Check: recompute message_id, vergleiche."""
        return canonical_sha256(self._unsigned_payload()) == self.message_id


def build_envelope(
    *,
    topic: Topic | str,
    producer_module_id: str,
    producer_module_kind: str,
    schema_ref: str,
    payload: dict[str, Any],
    subject_kind: SubjectKind | str = SubjectKind.NONE,
    subject_value: str = "",
    acl: tuple[str, ...] | list[str] = (),
    created_at_utc: str,
    adapter: str = "dummy",
) -> BusEnvelope:
    """Baut ein self-certifying Envelope. Erzeugt ValueError bei:

    unbekanntem Topic, disallowed schema_ref, verbotenen Medical-Feldern,
    ungueltigem Subjekt-Format, Safety-Marker-Drift. (Consumer-seitig hier
    nur fuer Test-Fixtures genutzt — Radi144 published im MVP nicht.)
    """
    topic_str = Topic(topic).value if not isinstance(topic, Topic) else topic.value
    if not is_allowed_schema_ref(topic_str, schema_ref):
        raise ValueError(f"schema_ref {schema_ref!r} fuer topic {topic_str!r} nicht erlaubt")
    forbidden = quarantined_forbidden_fields(payload)
    if forbidden:
        raise ValueError(f"verbotene Medical-Felder in payload: {forbidden}")
    sk = SubjectKind(subject_kind) if not isinstance(subject_kind, SubjectKind) else subject_kind
    subject_ref = {"kind": sk.value, "value": str(subject_value or "")}
    if sk == SubjectKind.NONE and subject_ref["value"]:
        raise ValueError("subject_kind=none darf keinen value tragen")
    safety = {"real_output_enabled": False, "medical_claims": 0, "adapter": adapter}
    acl_tuple = tuple(acl) if isinstance(acl, list) else tuple(acl)

    content_hash = canonical_sha256(payload)
    envelope = BusEnvelope(
        schema_version=SCHEMA_VERSION,
        message_id="",  # placeholder, unten self-certifying gesetzt
        topic=topic_str,
        producer={"module_id": producer_module_id, "module_kind": producer_module_kind},
        schema_ref=schema_ref,
        subject_ref=subject_ref,
        content_hash=content_hash,
        payload=payload,
        safety=safety,
        acl=acl_tuple,
        created_at_utc=created_at_utc,
    )
    message_id = canonical_sha256(envelope._unsigned_payload())
    object.__setattr__(envelope, "message_id", message_id)
    return envelope