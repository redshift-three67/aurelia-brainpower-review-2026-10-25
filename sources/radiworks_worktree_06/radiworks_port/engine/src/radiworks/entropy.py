"""EntropyProvider — zentrale Entropie-Abstraktion des RadiWorks-Kernels.

Port der AetherOnePi-Hotbits-Kette (HotbitsHandler / HotbitsClient, siehe
Radiworks/docs/FUNKTIONSANALYSE.md §3) mit einer plattformgemäßen Korrektur:

Aurelia Hard Rule 7 ("MUST default to strict reproducibility. Stochastic/quantum
explicit.") => Standardmodus ist *seeded* (deterministisch, replaybar im
Computation Passport). Der stochastische Live-Modus (echte Entropie: QRNG,
random.org, OS) ist ein expliziter Opt-in pro Aufruf.

Seed-Semantik des Originals bleibt erhalten: ein gelieferter Entropiewert ist
SEED eines zweiten, deterministischen PRNG-Aufrufs — nicht die Zufallszahl
selbst (FUNKTIONSANALYSE §3.1, Random(hotbit).nextInt(...)).
"""

from __future__ import annotations

import hashlib
import random
import secrets
from dataclasses import dataclass, field
from typing import Callable, Protocol

# Gueltige Modi (Festlegung 2026-08-29: Settings-gesteuert, siehe
# Modul_Templates/modules/radiworks/FESTLEGUNGEN.md)
ENTROPY_MODES = ("seeded", "stochastic")


class RandomSource(Protocol):
    """Eine Quelle, die Roentropie-Werte (Seeds) liefert."""

    name: str

    def next_seed(self) -> int: ...


class SeededSource:
    """Deterministische Quelle: Fixed Seed -> wiederholbare Runs (Default)."""

    name = "seeded"

    def __init__(self, seed: int = 0) -> None:
        self._rng = random.Random(seed)

    def next_seed(self) -> int:
        return self._rng.randrange(0, 2**31)


class OSSource:
    """Betriebssystem-Entropie (CSPRNG) — Fallback-Kette, immer verfügbar."""

    name = "os"

    def next_seed(self) -> int:
        return secrets.randbelow(2**31)


class RandomOrgSource:
    """random.org-Quelle des Originals (HotbitsClient.getRandomOrgSeeded).

    Netzwerkeffekt bewusst als Fallback (nicht Default): keine versteckten
    Netzaufrufe (Kernel-ABI). Nur aktiv im stochastischen Modus.
    """

    name = "random.org"

    def __init__(self, http_get: Callable[[str], str] | None = None) -> None:
        self._http_get = http_get
        self._cache: list[int] = []
        self.url = (
            "https://www.random.org/integers/?num=1000&min=1&max=1000000"
            "&col=1&base=10&format=plain&rnd=new"
        )

    def next_seed(self) -> int:
        if not self._cache:
            self._refill()
        if self._cache:
            return self._cache.pop(0)
        return OSSource().next_seed()

    def _refill(self) -> None:
        if self._http_get is None:
            return
        try:  # pragma: no cover - nur mit aktivem Netz
            body = self._http_get(self.url)
            parts = [p for p in body.split() if p.strip()]
            if len(parts) >= 5:
                self._cache.extend(int(p) for p in parts)
        except Exception:
            return


@dataclass
class EntropyStatus:
    mode: str
    active_source: str
    chain: list[str] = field(default_factory=list)


class WebcamFeedSource:
    """Frisch eingespeiste Webcam-Entropie (Original-Format hotbits_*.json).

    Die Werte werden verbraucht (FIFO) und haben Vorrang vor random.org —
    genau wie im Original, wo hotbits/*.json zuerst geleert wird. Es werden
    NUR die abgeleiteten Ganzzahlen übertragen, niemals Bildframes.
    """

    name = "webcam"

    def __init__(self) -> None:
        self._buffer: list[int] = []

    def feed(self, values: list[int]) -> int:
        clean = [int(v) for v in values if int(v) >= 100]  # Original: seed < 100 wird verworfen
        self._buffer.extend(clean)
        if len(self._buffer) > 4_000_000:  # Original-Cachelimit HotbitsHandler
            del self._buffer[:-4_000_000]
        return len(clean)

    def next_seed(self) -> int:
        return self._buffer.pop(0)

    def __len__(self) -> int:
        return len(self._buffer)


class EntropyProvider:
    """Die einzige Ziehungsstelle des Kernels.

    Modus ``seeded`` (Default): deterministisch, aus ``seed`` abgeleitet.
    Modus ``stochastic``: Kette Webcam-Feed (falls vorhanden) -> random.org
    -> OS-CSPRNG.

    Interface entspricht dem Java-IHotbitsClient: get_boolean / get_integer.
    """

    def __init__(
        self,
        seed: int | None = None,
        mode: str = "seeded",
        feed: WebcamFeedSource | None = None,
    ) -> None:
        if mode not in ("seeded", "stochastic"):
            raise ValueError(f"unbekannter Entropie-Modus: {mode!r}")
        self._requested_mode = mode
        self._seed = seed
        self._seeded_source = SeededSource(seed if seed is not None else 0)
        # Geteilter Feed: Webcam-Pakete überdauern Einzelrequests (AppState).
        self._webcam_feed = feed if feed is not None else WebcamFeedSource()
        self._random_org = RandomOrgSource()
        self._os_source = OSSource()

    # -- Webcam-Zufuhr (Aether_8: GET HOTBITS) ---------------------------

    def feed_integers(self, values: list[int]) -> int:
        return self._webcam_feed.feed(values)

    def feed_size(self) -> int:
        return len(self._webcam_feed)

    # -- interne Helfer -------------------------------------------------

    @property
    def _source(self) -> RandomSource:
        if self._requested_mode == "stochastic":
            if len(self._webcam_feed) > 0:
                return self._webcam_feed
            if self._random_org._cache:
                return self._random_org
            return self._os_source
        return self._seeded_source

    def _draw(self, bound: int) -> int:
        """Ziehung wie im Original: Entropiewert = Seed eines PRNG-Schritts."""
        seed = self._source.next_seed()
        return random.Random(seed).randrange(bound)

    # -- oeffentliches Interface (IHotbitsClient-Port) -------------------

    def get_boolean(self) -> bool:
        return bool(self._draw(2))

    def get_integer(self, min_inclusive: int, max_inclusive: int) -> int:
        return min_inclusive + self._draw(max_inclusive - min_inclusive + 1)

    def get_integer_bound(self, bound: int) -> int:
        return self._draw(bound)

    # -- Status / Metadaten ----------------------------------------------

    @property
    def mode(self) -> str:
        return self._requested_mode

    @property
    def seed(self) -> int | None:
        return self._seed

    def status(self) -> EntropyStatus:
        if self._requested_mode == "stochastic":
            chain = (["webcam"] if len(self._webcam_feed) else []) + ["random.org", "os"]
        else:
            chain = ["seeded"]
        return EntropyStatus(
            mode=self._requested_mode,
            active_source=self._source.name,
            chain=chain,
        )

    def derived_seed(self) -> int:
        """Stabiler Run-Seed fuer den Computation Passport."""
        base = f"{self._requested_mode}:{self._seed if self._seed is not None else 'live'}"
        return int(hashlib.sha256(base.encode("utf-8")).hexdigest()[:12], 16)
