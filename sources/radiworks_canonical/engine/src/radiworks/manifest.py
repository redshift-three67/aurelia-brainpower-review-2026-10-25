"""Kernel-ABI v1 — Selbstbeschreibung des RadiWorks-Kernels (Aurelia docs/06-kernel-abi.md).

Das Manifest ist der Integrationsvertrag: Aurelias spaetere Kernel-Registry
(Phase 3) registriert genau dieses Objekt. Freigabe in Produktion ist ein
Admin-Akt; der Prototyp bleibt Labor-Mandant.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

KERNEL_ID = "radiworks.engine"
KERNEL_VERSION = "0.2.0"
REST_ABI_VERSION = "v1"

INPUT_SCHEMA = {
    "type": "object",
    "required": ["database"],
    "additionalProperties": False,
    "properties": {
        "database": {"type": "string", "description": "Raten-Datenbank oder Kategorie-Praefix"},
        "seed": {"type": ["integer", "null"], "description": "Reproduzierbarkeits-Seed"},
        "mode": {"type": ["string", "null"], "enum": ["seeded", "stochastic", None]},
        "max_hits": {"type": "integer", "enum": [100, 1000]},
    },
}

PASSPORT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "run_id",
        "tenant_id",
        "client_id",
        "modus",
        "kernel",
        "kernel_version",
        "kernel_hash",
        "input_hash",
        "input_hash_scheme",
        "passport_schema_version",
        "seed",
        "entropy_mode",
        "replayable",
        "seed_scheme",
        "copyguard_digest",
        "gpu_attest",
        "vram_mb",
        "dauer_ms",
        "sources",
        "signatur",
        "signatur_status",
    ],
    "properties": {
        "run_id": {"type": "string", "format": "uuid"},
        "tenant_id": {"type": ["string", "null"]},
        "client_id": {"type": ["string", "null"]},
        "modus": {"type": "string"},
        "kernel": {"type": "string"},
        "kernel_version": {"type": "string"},
        "kernel_hash": {"type": "string"},
        "input_hash": {"type": "string"},
        "input_hash_scheme": {"enum": ["analysis-request-v2", "analysis-request-catalog-v1"]},
        "passport_schema_version": {"const": 2},
        "seed": {"type": ["integer", "null"]},
        "entropy_mode": {"enum": ["seeded", "stochastic"]},
        "replayable": {"type": "boolean"},
        "seed_scheme": {"type": "string"},
        "copyguard_digest": {"type": ["string", "null"]},
        "gpu_attest": {"type": ["string", "null"]},
        "vram_mb": {"type": "integer"},
        "dauer_ms": {"type": "integer"},
        "sources": {"type": "object", "additionalProperties": {"type": "string"}},
        "signatur": {"type": "string"},
        "signatur_status": {"const": "unsigned"},
    },
}

RESULT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["generalVitality", "numberOfTrials", "rateObjects"],
    "properties": {
        "generalVitality": {"type": ["integer", "null"]},
        "numberOfTrials": {"type": ["integer", "null"]},
        "rateObjects": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "energeticValue",
                    "nameOrRate",
                    "url",
                    "gv",
                    "recurring",
                    "recurringGeneralVitality",
                    "level",
                    "potency",
                    "resonateCounter",
                ],
                "properties": {
                    "energeticValue": {"type": "integer"},
                    "nameOrRate": {"type": "string"},
                    "url": {"type": ["string", "null"]},
                    "gv": {"type": "integer"},
                    "recurring": {"type": "integer"},
                    "recurringGeneralVitality": {"type": "integer"},
                    "level": {"type": "integer"},
                    "potency": {"type": ["string", "null"]},
                    "resonateCounter": {"type": "integer"},
                },
            },
        },
    },
}

DRAFT_SUMMARY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "id", "tenant_id", "client_id", "practitioner_id", "source_kernel",
        "source_kernel_version", "source_run_id", "sessionId", "sessionRevision",
        "database", "focus", "copyguard_digest", "copyguard_verdict",
        "copyguard_findings", "client_editable_fields", "practitioner_note",
        "status", "created", "updated", "ttl_hint", "scope", "job_id",
    ],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "tenant_id": {"type": "string"},
        "client_id": {"type": "string"},
        "practitioner_id": {"type": ["string", "null"]},
        "source_kernel": {"type": "string"},
        "source_kernel_version": {"type": "string"},
        "source_run_id": {"type": "string", "format": "uuid"},
        "sessionId": {"type": ["string", "null"]},
        "sessionRevision": {"type": "integer"},
        "database": {"type": "string"},
        "focus": {"type": "object"},
        "copyguard_digest": {"type": "string"},
        "copyguard_verdict": {"enum": ["allow", "block"]},
        "copyguard_findings": {
            "type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}},
        },
        "client_editable_fields": {"type": "array", "items": {"type": "string"}},
        "practitioner_note": {"type": "string"},
        "status": {"type": "string"},
        "created": {"type": "string", "format": "date-time"},
        "updated": {"type": "string", "format": "date-time"},
        "ttl_hint": {"type": "string", "format": "date-time"},
        "scope": {
            "type": "object",
            "additionalProperties": False,
            "required": ["tenant_id", "client_id", "job_id"],
            "properties": {
                "tenant_id": {"type": "string"},
                "client_id": {"type": "string"},
                "job_id": {"type": "string"},
            },
        },
        "job_id": {"type": "string"},
    },
}

OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["passport", "result", "draft"],
    "properties": {
        "passport": PASSPORT_SCHEMA,
        "result": RESULT_SCHEMA,
        "draft": DRAFT_SUMMARY_SCHEMA,
    },
}

BUDGET = {"vram_mb": 0, "cpu_ms_est": 5000, "max_batch": 1}

COPY = [
    "Digitale Radionik als dokumentierte Wellbeing-Praxis.",
    "Kein Medizinprodukt, keine Diagnose, keine Therapie, kein Heilversprechen.",
    "Analysen sind modellbasierte Verlaufsdokumentation, keine Physikmessung.",
]


def artifact_hash() -> str:
    """SHA-256 ueber alle Python-Quellen des Kernels (Artefakt-Hash, ABI-Pflicht)."""
    src_root = Path(__file__).resolve().parent
    sha = hashlib.sha256()
    for file in sorted(src_root.rglob("*.py")):
        sha.update(str(file.relative_to(src_root)).encode("utf-8"))
        sha.update(file.read_bytes())
    return f"sha256:{sha.hexdigest()}"


def manifest() -> dict:
    return {
        "id": KERNEL_ID,
        "version": KERNEL_VERSION,
        "hash": artifact_hash(),
        "input_schema": INPUT_SCHEMA,
        "output_schema": OUTPUT_SCHEMA,
        "class": "cpu",
        "repro": "seeded",
        "budget": BUDGET,
        "abi_surface": "rest",
        "abi_version": REST_ABI_VERSION,
        "operations": [
            {
                "id": "analysis",
                "method": "POST",
                "path": "/analysis",
                "version": REST_ABI_VERSION,
                "input_schema": INPUT_SCHEMA,
                "output_schema": OUTPUT_SCHEMA,
            }
        ],
        "entry": "radiworks.core.analysis:analyse_rate_list",
        "entry_status": "deprecated-compatibility",
        "copy": COPY,
        "isHardwareActivatable": False,
    }


def kernel_hash() -> str:
    return artifact_hash()


def kernel_json() -> str:
    return json.dumps(manifest(), sort_keys=True, ensure_ascii=False)
