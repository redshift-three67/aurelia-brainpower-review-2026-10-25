"""EntropyProvider — zentrale Entropie-Abstraktion des RadiWorks-Kernels.

Die Quelle liefert immer Roh-Seeds. Jeder Seed wird anschliessend wie im
AetherOnePi-Original durch ``java.util.Random(seed)`` in eine Ziehung umgesetzt.
Seeded ist reproduzierbar; stochastic nutzt Webcam/Hotbits, dann random.org und
zuletzt den OS-CSPRNG. Netzverkehr ist ausschliesslich im stochastic-Modus
moeglich.
"""

from __future__ import annotations

import secrets
from threading import Lock
from time import monotonic
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Callable, Iterator, Protocol
from urllib.request import urlopen

from .core.javaprng import JavaRandom
from .entropy_journal import EntropyJournal

ENTROPY_MODES = ("seeded", "stochastic")
RANDOM_ORG_TIMEOUT_S = 2.0
RANDOM_ORG_RETRY_COOLDOWN_S = 60.0


class RandomSource(Protocol):
    name: str

    def next_seed(self) -> int: ...


class SeededSource:
    """Java-kompatibler Master-Seed-Strom fuer reproduzierbare Laeufe."""

    name = "seeded"

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self._rng = JavaRandom(seed)

    def next_seed(self) -> int:
        return self._rng.next_int32()


class OSSource:
    """Betriebssystem-Entropie (CSPRNG) als stochastic Fallback."""

    name = "os"

    def next_seed(self) -> int:
        return secrets.randbelow(2**31)


def _random_org_http_get(url: str) -> str:
    with urlopen(url, timeout=RANDOM_ORG_TIMEOUT_S) as response:  # noqa: S310 - feste random.org-URL
        return response.read().decode("ascii", errors="strict")


class RandomOrgSource:
    """Explizit autorisierte stochastic random.org-Seed-Quelle mit Cache."""

    name = "random.org"

    def __init__(self, http_get: Callable[[str], str] | None = _random_org_http_get) -> None:
        self._http_get = http_get
        self._cache: list[int] = []
        self._retry_after: float | None = None
        self._lock = Lock()
        self.url = (
            "https://www.random.org/integers/?num=1000&min=1&max=1000000"
            "&col=1&base=10&format=plain&rnd=new"
        )

    def try_next_seed(self) -> int | None:
        with self._lock:
            if not self._cache:
                self._refill()
            return self._cache.pop(0) if self._cache else None

    def next_seed(self) -> int:
        seed = self.try_next_seed()
        if seed is None:
            raise RuntimeError("random.org hat keinen verwertbaren Seed geliefert")
        return seed

    def _in_cooldown(self) -> bool:
        return self._retry_after is not None and monotonic() < self._retry_after

    def _can_supply_seed(self) -> bool:
        return bool(self._cache) or (
            self._http_get is not None and not self._in_cooldown()
        )

    def _cool_down(self) -> None:
        self._retry_after = monotonic() + RANDOM_ORG_RETRY_COOLDOWN_S

    def _refill(self) -> None:
        if self._http_get is None or self._in_cooldown():
            return
        try:
            parts = [part for part in self._http_get(self.url).split() if part.strip()]
            values = [int(part) for part in parts]
        except (OSError, UnicodeError, ValueError):
            self._cool_down()
            return
        if len(values) < 5 or any(value < 1 or value > 1_000_000 for value in values):
            self._cool_down()
            return
        self._cache.extend(values)
        self._retry_after = None

@dataclass
class EntropyStatus:
    mode: str
    active_source: str
    chain: list[str] = field(default_factory=list)


class WebcamFeedSource:
    """Frisch eingespeiste Webcam-/Hotbits-Seeds; FIFO mit hoechster Prioritaet."""

    name = "webcam"

    def __init__(self) -> None:
        self._buffer: list[int] = []
        self._lock = Lock()

    def feed(self, values: list[int]) -> int:
        clean = [int(value) for value in values if int(value) >= 100]
        with self._lock:
            self._buffer.extend(clean)
            if len(self._buffer) > 4_000_000:
                del self._buffer[:-4_000_000]
        return len(clean)

    def try_next_seed(self) -> int | None:
        """Entnimmt genau einen Seed atomar; leere Feeds liefern ``None``."""
        with self._lock:
            return self._buffer.pop(0) if self._buffer else None

    def next_seed(self) -> int:
        seed = self.try_next_seed()
        if seed is None:
            raise IndexError("pop from empty list")
        return seed

    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)


class EntropyProvider:
    """Die einzige Ziehungsstelle des Kernels mit Java-zweistufiger Semantik."""

    def __init__(
        self,
        seed: int | None = None,
        mode: str = "seeded",
        feed: WebcamFeedSource | None = None,
        random_org: RandomOrgSource | None = None,
        os_source: OSSource | None = None,
        journal: EntropyJournal | None = None,
        source_segment: int = 0,
    ) -> None:
        if mode not in ENTROPY_MODES:
            raise ValueError(f"unbekannter Entropie-Modus: {mode!r}")
        self._requested_mode = mode
        self._seed = seed
        self._seeded_source = SeededSource(seed if seed is not None else 0)
        self._webcam_feed = feed if feed is not None else WebcamFeedSource()
        self._random_org = random_org if random_org is not None else RandomOrgSource()
        self._os_source = os_source if os_source is not None else OSSource()
        self._journal = journal
        self._source_segment = source_segment
        self._draw_count = 0
        self._active_source = "seeded" if mode == "seeded" else self._preferred_stochastic_source()

    def feed_integers(self, values: list[int]) -> int:
        return self._webcam_feed.feed(values)

    def feed_size(self) -> int:
        return len(self._webcam_feed)

    def _preferred_stochastic_source(self) -> str:
        if len(self._webcam_feed):
            return self._webcam_feed.name
        if self._random_org._can_supply_seed():
            return self._random_org.name
        return self._os_source.name

    def _record_stochastic_seed(self, seed: int) -> int:
        if self._journal is not None:
            self._journal.append(seed, self._active_source, self._source_segment)
        return seed

    def _next_seed(self) -> int:
        if self._requested_mode == "seeded":
            self._active_source = self._seeded_source.name
            return self._seeded_source.next_seed()
        webcam_seed = self._webcam_feed.try_next_seed()
        if webcam_seed is not None:
            self._active_source = self._webcam_feed.name
            return self._record_stochastic_seed(webcam_seed)
        random_org_seed = self._random_org.try_next_seed()
        if random_org_seed is not None:
            self._active_source = self._random_org.name
            return self._record_stochastic_seed(random_org_seed)
        self._active_source = self._os_source.name
        return self._record_stochastic_seed(self._os_source.next_seed())

    def _draw(self, bound: int) -> int:
        value = JavaRandom(self._next_seed()).next_int(bound)
        self._draw_count += 1
        return value

    def get_boolean(self) -> bool:
        return bool(self._draw(2))

    def get_integer(self, min_inclusive: int, max_inclusive: int) -> int:
        return min_inclusive + self._draw(max_inclusive - min_inclusive + 1)

    def get_integer_bound(self, bound: int) -> int:
        return self._draw(bound)

    @property
    def mode(self) -> str:
        return self._requested_mode

    @property
    def seed(self) -> int | None:
        return self._seed

    @property
    def effective_seed(self) -> int | None:
        return self._seeded_source.seed if self._requested_mode == "seeded" else None

    @property
    def draw_count(self) -> int:
        return self._draw_count

    @property
    def has_journal(self) -> bool:
        return self._journal is not None

    @property
    def replayable(self) -> bool:
        return self._requested_mode == "seeded"

    @contextmanager
    def journal_write_scope(self) -> Iterator[None]:
        if self._journal is None:
            yield
            return
        with self._journal.write_scope():
            yield

    def commit_journal(self) -> None:
        if self._journal is not None:
            self._journal.commit()

    def checkpoint(self) -> dict:
        checkpoint = {
            "mode": self.mode,
            "drawCount": self._draw_count,
            "effectiveSeed": self.effective_seed,
            "sourceSegment": self._source_segment,
            "source": self._active_source,
        }
        if self._journal is not None:
            checkpoint["journalId"] = self._journal.journal_id
            checkpoint["journalCursor"] = self._journal.cursor
            checkpoint["journalDigest"] = self._journal.digest()
            checkpoint["journalPrefixDigest"] = self._journal.prefix_digest(
                self._journal.cursor
            )
        return checkpoint

    def restore_seeded_cursor(self, draw_count: int) -> None:
        if self.mode != "seeded":
            raise ValueError("Nur seeded Entropie kann per Cursor fortgesetzt werden")
        if draw_count < 0:
            raise ValueError("drawCount darf nicht negativ sein")
        for _ in range(draw_count):
            self._seeded_source.next_seed()
        self._draw_count = draw_count

    def next_stochastic_segment(self) -> None:
        if self.mode == "stochastic":
            self._source_segment += 1

    def status(self) -> EntropyStatus:
        chain = ["seeded"] if self._requested_mode == "seeded" else ["webcam", "random.org", "os"]
        return EntropyStatus(
            mode=self._requested_mode,
            active_source=self._active_source,
            chain=chain,
        )

    def derived_seed(self) -> int | None:
        """Kompatibilitaetsalias; neue Passports verwenden ``effective_seed``."""
        return self.effective_seed
