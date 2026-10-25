"""Computation Passport — Aurelia-Vertrag (docs/04-compute.md)."""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


SEED_SCHEME_EFFECTIVE_V2 = "effective-v2"
PASSPORT_SCHEMA_VERSION = 2
INPUT_HASH_SCHEME_ANALYSIS_REQUEST_V2 = "analysis-request-v2"
SIGNATURE_STATUS_UNSIGNED = "unsigned"


def _sha256(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass
class Passport:
    run_id: str
    tenant_id: str | None
    client_id: str | None
    modus: str
    kernel: str
    kernel_version: str
    kernel_hash: str
    input_hash: str
    seed: int | None
    entropy_mode: str
    replayable: bool
    seed_scheme: str = SEED_SCHEME_EFFECTIVE_V2
    passport_schema_version: int = PASSPORT_SCHEMA_VERSION
    input_hash_scheme: str = INPUT_HASH_SCHEME_ANALYSIS_REQUEST_V2
    signatur_status: str = SIGNATURE_STATUS_UNSIGNED
    vram_mb: int = 0
    gpu_attest: str | None = None
    copyguard_digest: str | None = None
    dauer_ms: int = 0
    sources: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        kernel: str,
        kernel_version: str,
        kernel_hash: str,
        input_payload: Any,
        entropy: "object",
        modus: str = "analyse",
        tenant_id: str | None = None,
        client_id: str | None = None,
    ) -> "Passport":
        return cls(
            run_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            client_id=client_id,
            modus=modus,
            kernel=kernel,
            kernel_version=kernel_version,
            kernel_hash=kernel_hash,
            input_hash=_sha256(input_payload),
            seed=entropy.effective_seed,
            entropy_mode=entropy.mode,
            replayable=entropy.replayable,
        )

    def finish(self, dauer_ms: int, sources: dict[str, str] | None = None) -> None:
        self.dauer_ms = dauer_ms
        if sources:
            self.sources = sources

    def signature(self) -> str:
        """Deterministische Prüfsumme über die replay-relevante Provenienz."""
        return _sha256(
            {
                "run_id": self.run_id,
                "kernel": self.kernel,
                "kernel_version": self.kernel_version,
                "kernel_hash": self.kernel_hash,
                "input_hash": self.input_hash,
                "seed": self.seed,
                "entropy_mode": self.entropy_mode,
                "replayable": self.replayable,
                "seed_scheme": self.seed_scheme,
                "passport_schema_version": self.passport_schema_version,
                "input_hash_scheme": self.input_hash_scheme,
                "signatur_status": self.signatur_status,
                "copyguard_digest": self.copyguard_digest,
                "dauer_ms": self.dauer_ms,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "tenant_id": self.tenant_id,
            "client_id": self.client_id,
            "modus": self.modus,
            "kernel": self.kernel,
            "kernel_version": self.kernel_version,
            "kernel_hash": self.kernel_hash,
            "input_hash": self.input_hash,
            "seed": self.seed,
            "entropy_mode": self.entropy_mode,
            "replayable": self.replayable,
            "seed_scheme": self.seed_scheme,
            "passport_schema_version": self.passport_schema_version,
            "input_hash_scheme": self.input_hash_scheme,
            "gpu_attest": self.gpu_attest,
            "vram_mb": self.vram_mb,
            "copyguard_digest": self.copyguard_digest,
            "dauer_ms": self.dauer_ms,
            "sources": self.sources,
            "signatur": self.signature(),
            "signatur_status": self.signatur_status,
        }


def now_ms() -> int:
    return int(time.monotonic() * 1000)
