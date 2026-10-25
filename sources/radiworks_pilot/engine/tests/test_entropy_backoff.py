from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock

import radiworks.entropy as entropy_module
from radiworks.core.javaprng import JavaRandom
from radiworks.entropy import EntropyProvider, OSSource, RandomOrgSource, WebcamFeedSource


class FixedOSSource(OSSource):
    name = "os"

    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.calls = 0

    def next_seed(self) -> int:
        self.calls += 1
        return self.seed


class FakeMonotonic:
    def __init__(self, now: float = 100.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_random_org_failure_enters_cooldown_and_reports_os(monkeypatch):
    clock = FakeMonotonic()
    monkeypatch.setattr(entropy_module, "monotonic", clock, raising=False)
    requests = 0

    def fail(_: str) -> str:
        nonlocal requests
        requests += 1
        raise OSError("synthetic timeout")

    random_org = RandomOrgSource(http_get=fail)
    provider = EntropyProvider(
        mode="stochastic",
        random_org=random_org,
        os_source=FixedOSSource(777),
    )

    provider.get_integer(0, 10)
    provider.get_integer(0, 10)

    assert requests == 1
    assert provider.status().active_source == "os"
    resumed = EntropyProvider(
        mode="stochastic",
        random_org=random_org,
        os_source=FixedOSSource(888),
    )
    assert resumed.status().active_source == "os"


def test_random_org_retries_after_cooldown_and_recovers(monkeypatch):
    clock = FakeMonotonic()
    monkeypatch.setattr(entropy_module, "monotonic", clock, raising=False)
    requests = 0

    def fail_then_succeed(_: str) -> str:
        nonlocal requests
        requests += 1
        if requests == 1:
            raise OSError("synthetic timeout")
        return "123\n124\n125\n126\n127\n"

    provider = EntropyProvider(
        mode="stochastic",
        random_org=RandomOrgSource(http_get=fail_then_succeed),
        os_source=FixedOSSource(777),
    )

    provider.get_integer(0, 10)
    clock.advance(59.0)
    provider.get_integer(0, 10)
    assert requests == 1
    clock.advance(2.0)
    provider.get_integer(0, 10)

    assert requests == 2
    assert provider.status().active_source == "random.org"


def test_random_org_invalid_payload_enters_cooldown(monkeypatch):
    clock = FakeMonotonic()
    monkeypatch.setattr(entropy_module, "monotonic", clock, raising=False)
    requests = 0

    def invalid(_: str) -> str:
        nonlocal requests
        requests += 1
        return "malformed"

    os_source = FixedOSSource(777)
    provider = EntropyProvider(
        mode="stochastic",
        random_org=RandomOrgSource(http_get=invalid),
        os_source=os_source,
    )

    provider.get_integer(0, 10)
    provider.get_integer(0, 10)

    assert requests == 1
    assert os_source.calls == 2
    assert provider.status().active_source == "os"


def test_random_org_successful_cache_is_consumed_without_refetch():
    requests = 0

    def valid(_: str) -> str:
        nonlocal requests
        requests += 1
        return "123\n124\n125\n126\n127\n"

    provider = EntropyProvider(
        mode="stochastic",
        random_org=RandomOrgSource(http_get=valid),
        os_source=FixedOSSource(777),
    )

    for _ in range(5):
        provider.get_integer(0, 10)

    assert requests == 1
    assert provider.status().active_source == "random.org"


def test_disabled_random_org_uses_os_without_network():
    os_source = FixedOSSource(777)
    provider = EntropyProvider(
        mode="stochastic",
        random_org=RandomOrgSource(http_get=None),
        os_source=os_source,
    )

    provider.get_integer(0, 10)
    provider.get_integer(0, 10)

    assert provider.status().active_source == "os"
    assert os_source.calls == 2


def test_webcam_remains_first_priority_during_random_org_cooldown(monkeypatch):
    clock = FakeMonotonic()
    monkeypatch.setattr(entropy_module, "monotonic", clock, raising=False)
    requests = 0

    def fail(_: str) -> str:
        nonlocal requests
        requests += 1
        raise OSError("synthetic timeout")

    feed = WebcamFeedSource()
    os_source = FixedOSSource(777)
    provider = EntropyProvider(
        mode="stochastic",
        feed=feed,
        random_org=RandomOrgSource(http_get=fail),
        os_source=os_source,
    )

    provider.get_integer(0, 10)
    feed.feed([321])
    provider.get_integer(0, 10)

    assert requests == 1
    assert os_source.calls == 1
    assert provider.status().active_source == "webcam"


def test_seeded_stream_ignores_random_org_cooldown_source(monkeypatch):
    clock = FakeMonotonic()
    monkeypatch.setattr(entropy_module, "monotonic", clock, raising=False)
    requests = 0

    def fail(_: str) -> str:
        nonlocal requests
        requests += 1
        raise OSError("seeded mode must not request network entropy")

    random_org = RandomOrgSource(http_get=fail)
    first = EntropyProvider(seed=42, mode="seeded", random_org=random_org)
    second = EntropyProvider(seed=42, mode="seeded", random_org=random_org)

    assert [first.get_integer(0, 999) for _ in range(50)] == [
        second.get_integer(0, 999) for _ in range(50)
    ]
    assert requests == 0

def test_concurrent_random_org_failures_share_cooldown(monkeypatch):
    clock = FakeMonotonic()
    monkeypatch.setattr(entropy_module, "monotonic", clock, raising=False)
    requests = 0
    requests_lock = Lock()
    second_request_started = Event()
    source = None
    nested_future = None

    def fail(_: str) -> str:
        nonlocal requests, nested_future
        with requests_lock:
            requests += 1
            request_number = requests
        if request_number == 1:
            nested_future = pool.submit(source.try_next_seed)
            second_request_started.wait(timeout=1.0)
        else:
            second_request_started.set()
        raise OSError("synthetic timeout")

    with ThreadPoolExecutor(max_workers=2) as pool:
        source = RandomOrgSource(http_get=fail)
        first_future = pool.submit(source.try_next_seed)
        assert first_future.result(timeout=2.0) is None
        assert nested_future is not None
        assert nested_future.result(timeout=2.0) is None

    assert requests == 1


def test_concurrent_random_org_cache_draws_have_no_duplicates_or_loss():
    requests = 0

    def valid(_: str) -> str:
        nonlocal requests
        requests += 1
        return "\n".join(str(value) for value in range(100, 120))

    source = RandomOrgSource(http_get=valid)
    with ThreadPoolExecutor(max_workers=8) as pool:
        seeds = list(pool.map(lambda _: source.try_next_seed(), range(20)))

    assert sorted(seeds) == list(range(100, 120))
    assert len(set(seeds)) == 20
    assert requests == 1
