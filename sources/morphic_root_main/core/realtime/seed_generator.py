"""Deterministischer, workspace-gebundener Seed + ehrliche Entropie-Kaskade.

Spiegelt das Muster aus radiquant4s
`apps/api/app/services/hardware/seed_generator.py` (siehe
`docs/deep-audit-2026-07-05/RADIQUANT4_RADIMORPHIC_KONTRAKT_REFERENZ.md`,
Abschnitt 9), angepasst an die in `morphic_v1` tatsaechlich vorhandene
Hardware-Kaskade (`providers.hardware.entropy_sources.select_entropy_source`).

Kaskade (ehrlich, nur real vorhandene Stufen):
    1. `select_entropy_source()` liefert Kontext/Label (qrng > truerng >
       hid_sensor > network > cpu_timer, je nach Verfuegbarkeit).
    2. Die eigentlichen Zusatz-Seed-Bytes kommen immer aus `os.urandom`
       (echter, kryptographisch geeigneter OS-CSPRNG) - es wird KEINE
       Hardware-TRNG-Stufe (Kozyrev/ESP32/WebCam) behauptet, die es in
       `morphic_v1` nicht gibt. `source_label`/`entropy_samples` dokumentieren
       nur den Kontext, nicht die Herkunft der Seed-Bytes selbst.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass


def generate_deterministic_seed(
    workspace_id: str,
    last_name: str,
    first_name: str,
    birth_date: str,
    birth_place: str,
) -> int:
    """Reproduzierbarer, workspace-gebundener Seed.

    Gleiche Eingaben ergeben immer denselben Seed; eine andere
    `workspace_id` ergibt einen anderen Seed, selbst bei identischen
    Klientendaten (verhindert Seed-Kollisionen zwischen Arbeitsbereichen).
    """

    base = ":".join(
        part.strip().casefold()
        for part in (workspace_id, last_name, first_name, birth_date, birth_place)
    )
    digest = hashlib.sha256(base.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) & 0x7FFFFFFF


@dataclass(frozen=True)
class SeedResult:
    deterministic_seed: int
    hardware_seed: int | None
    entropy_samples: list[float] | None
    source_label: str


def generate_seed_with_entropy(
    workspace_id: str,
    last_name: str,
    first_name: str,
    birth_date: str,
    birth_place: str,
    use_hardware: bool = False,
) -> SeedResult:
    """Erzeugt den deterministischen Basis-Seed plus optional einen
    zusaetzlichen, entropie-gestuetzten Seed fuer den erweiterten Modus.
    """

    deterministic_seed = generate_deterministic_seed(
        workspace_id, last_name, first_name, birth_date, birth_place
    )

    if not use_hardware:
        return SeedResult(deterministic_seed, None, None, "none")

    try:
        from providers.hardware.entropy_sources import select_entropy_source

        source = select_entropy_source()
        h_level = source.sample_h_level(duration_s=0.2)
        source_label = source.name()
    except Exception:
        h_level = None
        source_label = "unavailable"

    hardware_seed = int.from_bytes(os.urandom(8), "big") & 0x7FFFFFFF
    samples = [h_level] if h_level is not None else None

    return SeedResult(deterministic_seed, hardware_seed, samples, source_label)
