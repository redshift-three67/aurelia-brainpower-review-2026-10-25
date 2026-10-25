"""Computation Passport — Aurelia-Vertrag (docs/04-compute.md).

Felder lt. Aurelia: run_id, tenant_id, modus, kernel, kernel_hash, input_hash,
seed, gpu_attest, vram_mb, copyguard_digest, dauer_ms, signatur.
Quelle jeder Zahl: simulated / measured / derived / manual / ai-generated.

Der RadiWorks-Kernel ist CPU-only (class: cpu, vram_mb: 0); gpu_attest bleibt
None. Alle Zahlen stammen aus dem EntropyProvider (simulated/derived).
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


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
    seed: int
    entropy_mode: str
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
            seed=entropy.derived_seed(),
            entropy_mode=entropy.mode,
        )

    def finish(self, dauer_ms: int, sources: dict[str, str] | None = None) -> None:
        self.dauer_ms = dauer_ms
        if sources:
            self.sources = sources

    def signature(self) -> str:
        """Deterministische Prüfsumme (Prototyp; echte Signatur folgt im Gate)."""
        return _sha256(
            {
                "run_id": self.run_id,
                "kernel": self.kernel,
                "kernel_version": self.kernel_version,
                "input_hash": self.input_hash,
                "seed": self.seed,
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
            "gpu_attest": self.gpu_attest,
            "vram_mb": self.vram_mb,
            "copyguard_digest": self.copyguard_digest,
            "dauer_ms": self.dauer_ms,
            "sources": self.sources,
            "signatur": self.signature(),
        }


def now_ms() -> int:
    return int(time.monotonic() * 1000)
