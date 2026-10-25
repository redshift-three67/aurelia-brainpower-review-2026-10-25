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
KERNEL_VERSION = "0.1.0"

INPUT_SCHEMA = {
    "type": "object",
    "required": ["database"],
    "properties": {
        "database": {"type": "string", "description": "Raten-Datenbank oder Kategorie-Praefix"},
        "seed": {"type": ["integer", "null"], "description": "Reproduzierbarkeits-Seed"},
        "mode": {"type": "string", "enum": ["seeded", "stochastic"]},
        "max_hits": {"type": "integer", "enum": [100, 1000]},
        "tenant_id": {"type": ["string", "null"]},
        "client_id": {"type": ["string", "null"]},
    },
}

OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["passport", "result"],
    "properties": {
        "passport": {"type": "object"},
        "result": {
            "type": "object",
            "properties": {
                "general_vitality": {"type": ["integer", "null"]},
                "number_of_trials": {"type": ["integer", "null"]},
                "rate_objects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "energetic_value": {"type": "integer"},
                            "name_or_rate": {"type": "string"},
                            "url": {"type": ["string", "null"]},
                            "gv": {"type": "integer"},
                            "recurring": {"type": "integer"},
                            "level": {"type": "integer"},
                            "potency": {"type": ["string", "null"]},
                        },
                    },
                },
            },
        },
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
        "entry": "radiworks.core.analysis:analyse_rate_list",
        "copy": COPY,
        "isHardwareActivatable": False,
    }


def kernel_hash() -> str:
    return artifact_hash()


def kernel_json() -> str:
    return json.dumps(manifest(), sort_keys=True, ensure_ascii=False)
