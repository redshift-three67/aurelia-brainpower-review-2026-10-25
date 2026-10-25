"""Tests: Java-kompatible EntropyProvider-Semantik und Quellenprioritaet."""

from radiworks.core.javaprng import JavaRandom
from radiworks.entropy import EntropyProvider, OSSource, RandomOrgSource, WebcamFeedSource
from radiworks.entropy_journal import EntropyJournalStore


class FixedOSSource(OSSource):
    name = "os"

    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.calls = 0

    def next_seed(self) -> int:
        self.calls += 1
        return self.seed


def test_seeded_mode_is_deterministic():
    a = EntropyProvider(seed=42, mode="seeded")
    b = EntropyProvider(seed=42, mode="seeded")
    seq_a = [a.get_integer(0, 999) for _ in range(50)]
    seq_b = [b.get_integer(0, 999) for _ in range(50)]
    assert seq_a == seq_b


def test_seeded_mode_uses_java_master_and_second_stage():
    master = JavaRandom(42)
    raw_seed = master.next_int32()
    expected = JavaRandom(raw_seed).next_int(997)

    provider = EntropyProvider(seed=42, mode="seeded")

    assert provider.get_integer(3, 999) == 3 + expected


def test_different_seeds_diverge():
    a = EntropyProvider(seed=1, mode="seeded")
    b = EntropyProvider(seed=2, mode="seeded")
    seq_a = [a.get_integer(0, 999) for _ in range(20)]
    seq_b = [b.get_integer(0, 999) for _ in range(20)]
    assert seq_a != seq_b


def test_seeded_mode_never_touches_random_org():
    def unexpected_network(_: str) -> str:
        raise AssertionError("seeded mode must not call random.org")

    provider = EntropyProvider(
        seed=7,
        mode="seeded",
        random_org=RandomOrgSource(http_get=unexpected_network),
    )
    assert provider.get_integer(0, 10) in range(11)
    assert provider.status().active_source == "seeded"
    assert "random.org" not in provider.status().chain


def test_get_integer_bounds_inclusive():
    provider = EntropyProvider(seed=5)
    draws = {provider.get_integer(1, 6) for _ in range(500)}
    assert draws <= set(range(1, 7))
    assert draws


def test_get_boolean_exists():
    provider = EntropyProvider(seed=9)
    values = {provider.get_boolean() for _ in range(100)}
    assert values <= {True, False}


def test_webcam_seed_has_priority_and_is_consumed_once():
    feed = WebcamFeedSource()
    feed.feed([321])
    random_org = RandomOrgSource(http_get=lambda _: "123\n124\n125\n126\n127\n")
    provider = EntropyProvider(
        mode="stochastic",
        feed=feed,
        random_org=random_org,
        os_source=FixedOSSource(999),
    )

    assert provider.get_integer(0, 99) == JavaRandom(321).next_int(100)
    assert provider.status().active_source == "webcam"
    assert provider.feed_size() == 0
    assert provider.get_integer(0, 99) == JavaRandom(123).next_int(100)
    assert provider.status().active_source == "random.org"


def test_random_org_failure_falls_back_to_os_without_crash():
    os_source = FixedOSSource(777)
    provider = EntropyProvider(
        mode="stochastic",
        random_org=RandomOrgSource(http_get=lambda _: "malformed"),
        os_source=os_source,
    )

    assert provider.get_integer(0, 10) == JavaRandom(777).next_int(11)
    assert provider.status().active_source == "os"
    assert os_source.calls == 1


def test_effective_seed_and_replayability():
    assert EntropyProvider(seed=12, mode="seeded").effective_seed == 12
    assert EntropyProvider(mode="seeded").effective_seed == 0
    assert EntropyProvider(mode="seeded").replayable is True
    assert EntropyProvider(mode="stochastic", random_org=RandomOrgSource(http_get=None)).effective_seed is None
    assert EntropyProvider(mode="stochastic", random_org=RandomOrgSource(http_get=None)).replayable is False


def test_seeded_checkpoint_restores_next_draw():
    continuous = EntropyProvider(seed=44)
    for _ in range(12):
        continuous.get_integer(0, 999)
    checkpoint = continuous.checkpoint()
    expected = continuous.get_integer(0, 999)

    restored = EntropyProvider(seed=checkpoint["effectiveSeed"])
    restored.restore_seeded_cursor(checkpoint["drawCount"])

    assert restored.get_integer(0, 999) == expected


def test_stochastic_restart_creates_new_recorded_source_segment(tmp_path):
    from cryptography.fernet import Fernet

    journal = EntropyJournalStore(tmp_path, key=Fernet.generate_key()).create()
    first = EntropyProvider(
        mode="stochastic",
        random_org=RandomOrgSource(http_get=None),
        os_source=FixedOSSource(101),
        journal=journal,
    )
    first.get_integer(0, 9)
    first.commit_journal()
    checkpoint = first.checkpoint()

    resumed = EntropyProvider(
        mode="stochastic",
        random_org=RandomOrgSource(http_get=None),
        os_source=FixedOSSource(202),
        journal=journal,
        source_segment=checkpoint["sourceSegment"] + 1,
    )
    resumed.get_integer(0, 9)
    resumed.commit_journal()

    assert [record["segment"] for record in journal.records()] == [0, 1]


def test_invalid_mode_rejected():
    try:
        EntropyProvider(seed=1, mode="quantum")  # type: ignore[arg-type]
    except ValueError:
        return
    raise AssertionError("unbekannter Modus muss abgelehnt werden")
