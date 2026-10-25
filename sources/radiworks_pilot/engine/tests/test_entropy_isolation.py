"""M3 webcam feed atomics and late-injected empty feeds."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock

from radiworks.core.javaprng import JavaRandom
from radiworks.entropy import EntropyProvider, OSSource, RandomOrgSource, WebcamFeedSource


class FixedOSSource(OSSource):
    name = "os"

    def __init__(self, seed=777):
        self.seed = seed

    def next_seed(self):
        return self.seed


def test_webcam_feed_atomic_take_is_fifo_and_returns_none_when_empty():
    feed = WebcamFeedSource()
    feed.feed(list(range(100, 300)))

    with ThreadPoolExecutor(max_workers=8) as pool:
        values = list(pool.map(lambda _: feed.try_next_seed(), range(200)))

    assert sorted(values) == list(range(100, 300))
    assert feed.try_next_seed() is None
    assert len(feed) == 0


def test_empty_supplied_feed_is_retained_for_later_camera_input():
    feed = WebcamFeedSource()
    provider = EntropyProvider(
        mode="stochastic",
        feed=feed,
        random_org=RandomOrgSource(http_get=None),
        os_source=FixedOSSource(999),
    )

    feed.feed([321])

    assert provider.get_integer(0, 99) == JavaRandom(321).next_int(100)
    assert provider.status().active_source == "webcam"


def test_two_providers_cannot_race_between_feed_length_and_pop():
    rendezvous = Barrier(2)

    class RacingFeed(WebcamFeedSource):
        race = False

        def __init__(self):
            super().__init__()
            self._race_reads = 0
            self._race_lock = Lock()

        def __len__(self):
            observed = super().__len__()
            should_wait = False
            if self.race:
                with self._race_lock:
                    self._race_reads += 1
                    should_wait = self._race_reads <= 2
            if should_wait:
                rendezvous.wait(timeout=2)
            return observed

    feed = RacingFeed()
    feed.feed([321])
    providers = [
        EntropyProvider(
            mode="stochastic",
            feed=feed,
            random_org=RandomOrgSource(http_get=None),
            os_source=FixedOSSource(500 + index),
        )
        for index in range(2)
    ]
    feed.race = True

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda provider: provider.get_integer(0, 99), providers))

    assert len(results) == 2
    feed.race = False
    assert len(feed) == 0
    assert sum(provider.status().active_source == "webcam" for provider in providers) == 1