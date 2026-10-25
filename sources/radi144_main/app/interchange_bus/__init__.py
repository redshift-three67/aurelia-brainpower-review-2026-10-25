"""R-10..R-14: Interchange-Bus Consumer-Paket (Radi144) — stdlib-only, autark.

Spiegelt ME2s ``src/morphic_engine_2/interchange_bus/`` Primitive byte-identisch
(canonical_sha256, message_id, verify), sodass Radi144 ME2-published Envelopes
aus der geteilten BusDB liest und verifizieren kann. KEINE ME2-Imports im Core
(Extrahierbarkeit fuer alle Module bewahrt). Radi144 ist im MVP **Consumer**
(liest/ackt/registriert — published nicht). Finale Verdrahtung auf Debian-Server.
"""
from .envelope import (
    BusEnvelope,
    SCHEMA_VERSION,
    FORBIDDEN_MEDICAL_FIELDS,
    DEFAULT_SAFETY,
    SubjectKind,
    Action,
    canonical_sha256,
    quarantined_forbidden_fields,
    build_envelope,
)
from .topics import Topic, ALLOWED_SCHEMA_REFS, is_allowed_schema_ref, topic_values
from .consumer_store import BusConsumerStore, STORE_SCHEMA_VERSION

__all__ = [
    "BusEnvelope",
    "BusConsumerStore",
    "SCHEMA_VERSION",
    "STORE_SCHEMA_VERSION",
    "FORBIDDEN_MEDICAL_FIELDS",
    "DEFAULT_SAFETY",
    "SubjectKind",
    "Action",
    "Topic",
    "ALLOWED_SCHEMA_REFS",
    "is_allowed_schema_ref",
    "topic_values",
    "canonical_sha256",
    "quarantined_forbidden_fields",
    "build_envelope",
]