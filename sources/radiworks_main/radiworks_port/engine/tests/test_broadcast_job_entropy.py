"""M3 per-job broadcast entropy, durable checkpoints and private journal refs."""
import copy
import json
import uuid

import pytest
from cryptography.fernet import Fernet

from radiworks.core.broadcast import BroadcastError, BroadcastManager, BroadcastElement
from radiworks.core.broadcast_target import BroadcastTarget, BroadcastTargetError, BroadcastTargetStore
from radiworks.core.javaprng import JavaRandom
from radiworks.entropy import EntropyProvider, OSSource, RandomOrgSource
from radiworks.entropy_journal import EntropyJournalStore
from radiworks.scope import ScopeContext
from radiworks.persistence import document_digest


def _scope():
    return ScopeContext("synthetic-tenant", "synthetic-client", "synthetic-job")


def _target(mode="seeded", marker="a"):
    return BroadcastTarget.capture(
        scope=_scope(),
        source={"kind": "image", "imageHash": marker * 64},
        legacy=True,
        entropy_mode=mode,
    )


def _entry(target, broadcast_id=None):
    return {
        "broadcastId": broadcast_id or uuid.uuid4().hex,
        "signature": "M3 synthetic",
        "seconds": 20,
        "multiplier": 1000,
        "clear": False,
        "delayMs": 120,
        "repeat": 1,
        "target": target.payload(),
    }


class Collector:
    def __init__(self, timeline=None):
        self.events = []
        self.timeline = timeline

    def __call__(self, event_type, payload):
        self.events.append((event_type, copy.deepcopy(payload)))
        if self.timeline is not None:
            self.timeline.append((event_type, copy.deepcopy(payload)))


class SequenceOS(OSSource):
    name = "os"

    def __init__(self, values):
        self.values = list(values)

    def next_seed(self):
        if self.values:
            return self.values.pop(0)
        return 101


def test_target_factory_and_initial_checkpoint_precede_acceptance_visibility():
    order = []
    target = _target()
    collector = Collector(order)
    manager = BroadcastManager(
        entropy=EntropyProvider(seed=99),
        emit=collector,
        entropy_factory=lambda frozen: (
            order.append(("factory", frozen.payload()["jobId"])) or EntropyProvider(seed=0)
        ),
        on_accept=lambda rows: order.append(("accept", rows[0]["broadcastId"])),
        on_entropy=lambda payload: order.append(("checkpoint", payload["broadcastId"])),
    )
    manager._start_thread = lambda: order.append(("start", None))

    result = manager.enqueue("SYNTHETIC", 10, target=target)

    assert [item[0] for item in order[:4]] == ["factory", "accept", "checkpoint", "start"]
    assert result["entropy"] == {"mode": "seeded", "source": "seeded", "drawCount": 0, "seed": 0}


def test_promote_batch_assigns_independent_providers_before_acceptance():
    order = []
    providers = []

    def factory(target):
        provider = EntropyProvider(seed=0)
        providers.append(provider)
        order.append(("factory", target.payload()["jobId"]))
        return provider

    manager = BroadcastManager(
        entropy=EntropyProvider(seed=88),
        emit=lambda *_: None,
        entropy_factory=factory,
        on_accept=lambda rows: order.append(("accept", len(rows))),
        on_entropy=lambda payload: order.append(("checkpoint", payload["broadcastId"])),
    )
    manager._start_thread = lambda: order.append(("start", None))

    result = manager.enqueue_batch(
        [
            {"signature": "A", "seconds": 5, "target": _target(marker="1").payload()},
            {"signature": "B", "seconds": 5, "target": _target(marker="2").payload()},
        ],
        on_accepted=lambda ids: order.append(("promote", len(ids))),
    )

    assert providers[0] is not providers[1]
    assert [kind for kind, _ in order] == [
        "factory", "factory", "accept", "checkpoint", "checkpoint", "start", "promote"
    ]
    assert all(row["entropy"] == {"mode": "seeded", "source": "seeded", "drawCount": 0, "seed": 0} for row in result)

def test_provider_mode_or_stochastic_journal_mismatch_rejects_before_acceptance():
    accepted = []
    collector = Collector()
    target = _target("seeded")
    manager = BroadcastManager(
        entropy=EntropyProvider(seed=8),
        emit=collector,
        entropy_factory=lambda _: EntropyProvider(mode="stochastic"),
        on_accept=lambda rows: accepted.extend(rows),
    )
    manager._start_thread = lambda: None

    with pytest.raises(BroadcastError, match="Modus"):
        manager.enqueue("MISMATCH", 5, target=target)
    assert accepted == []
    assert manager.queue_state()["queued"] == []
    assert collector.events == []

    stochastic = _target("stochastic", "b")
    no_journal = BroadcastManager(
        entropy=EntropyProvider(seed=8),
        emit=collector,
        entropy_factory=lambda _: EntropyProvider(mode="stochastic", random_org=RandomOrgSource(http_get=None)),
        on_accept=lambda rows: accepted.extend(rows),
        on_entropy=lambda payload: None,
    )
    no_journal._start_thread = lambda: None
    with pytest.raises(BroadcastError, match="Journal"):
        no_journal.enqueue("NO JOURNAL", 5, target=stochastic)
    assert accepted == []
    assert no_journal.queue_state()["queued"] == []


def test_interleaved_seeded_jobs_match_seed_zero_single_job_stream():
    collector = Collector()
    manager = BroadcastManager(
        entropy=EntropyProvider(seed=42),
        emit=collector,
        entropy_factory=lambda _: EntropyProvider(seed=0, mode="seeded"),
    )
    manager._start_thread = lambda: None
    first = manager.enqueue("SAME", 60, 1000, target=_target(marker="c"))
    second = manager.enqueue("SAME", 60, 1000, target=_target(marker="d"))
    manager._promote_from_queue()
    a, b = manager._active
    assert a.entropy_provider is not b.entropy_provider
    assert a.entropy_provider is not manager._entropy

    legacy_events = Collector()
    legacy = BroadcastManager(EntropyProvider(seed=0), legacy_events)
    baseline = BroadcastElement("SAME", 60, 1000)
    legacy._active.append(baseline)

    for _ in range(4000):
        manager._resonance_draw(a)
        manager._resonance_draw(b)
        legacy._resonance_draw(baseline)

    def binaural(events, broadcast_id=None):
        return [
            payload["binaural"]
            for event, payload in events
            if event == "broadcast.resonance"
            and (broadcast_id is None or payload["broadcastId"] == broadcast_id)
        ]

    assert binaural(collector.events, first["broadcastId"]) == binaural(legacy_events.events)
    assert binaural(collector.events, second["broadcastId"]) == binaural(legacy_events.events)
    assert a.entropy_provider.checkpoint()["drawCount"] == b.entropy_provider.checkpoint()["drawCount"]
    assert a.entropy_provider.checkpoint()["drawCount"] == legacy._entropy.checkpoint()["drawCount"]
    a.entropy_provider.get_integer(0, 9)
    assert a.entropy_provider.checkpoint()["drawCount"] == b.entropy_provider.checkpoint()["drawCount"] + 1
    assert first["broadcastId"] != second["broadcastId"]


def test_stochastic_journal_is_committed_before_resonance_and_checkpoint_survives_restart(tmp_path):
    timeline = []
    store = BroadcastTargetStore(tmp_path / "targets", _scope())
    journals = []
    journal_store = EntropyJournalStore(tmp_path / "journals", key=Fernet.generate_key())
    collector = Collector(timeline)

    def factory(target):
        assert target.payload()["entropyMode"] == "stochastic"
        journal = journal_store.create()
        journals.append(journal)
        return EntropyProvider(
            mode="stochastic",
            random_org=RandomOrgSource(http_get=None),
            os_source=SequenceOS([426, 101, 202, 303]),
            journal=journal,
        )

    def checkpoint(payload):
        timeline.append(("checkpoint", copy.deepcopy(payload)))
        store.record_entropy(payload)

    manager = BroadcastManager(
        entropy=EntropyProvider(seed=2),
        emit=collector,
        entropy_factory=factory,
        on_accept=store.accept,
        on_abort=store.terminal,
        on_entropy=checkpoint,
    )
    manager._start_thread = lambda: None
    accepted = manager.enqueue("FORCED RESONANCE", 60, 1000, target=_target("stochastic", "e"))
    element = manager._queue[0]
    manager._promote_from_queue()
    manager._resonance_draw(element)

    resonance_index = next(i for i, item in enumerate(timeline) if item[0] == "broadcast.resonance")
    checkpoint_indexes = [i for i, item in enumerate(timeline) if item[0] == "checkpoint"]
    assert checkpoint_indexes[-1] < resonance_index
    event = timeline[resonance_index][1]
    assert event["entropy"] == {"mode": "stochastic", "source": "os", "drawCount": 4, "seed": None}
    assert not any(key in json.dumps(event) for key in ("journalId", "journalDigest", "rawSeed"))
    records = journals[0].records()
    assert [item["seed"] for item in records] == [426, 101, 202, 303]
    assert [item["source"] for item in records] == ["os"] * 4
    replayed = [
        JavaRandom(record["seed"]).next_int(bound)
        for record, bound in zip(records, (7765, 500, 50, 10), strict=True)
    ]
    assert replayed == [
        7764,
        event["binaural"]["left_freq"] - 50,
        event["binaural"]["right_freq"] - event["binaural"]["left_freq"],
        round(event["binaural"]["volume"] * 10) - 1,
    ]
    saved = store.get(element.target.payload()["jobId"])
    assert saved["entropyCheckpoint"]["checkpoint"]["journalCursor"] == 4
    assert saved["entropyCheckpoint"]["checkpoint"]["drawCount"] == 4

    journals[0].path.unlink()
    restarted = BroadcastTargetStore(tmp_path / "targets", _scope())
    recovered = restarted.get(element.target.payload()["jobId"])
    assert recovered["state"] == "interrupted"
    assert recovered["entropyCheckpoint"]["checkpoint"]["journalId"] == journals[0].journal_id
    assert recovered["entropyCheckpoint"]["checkpoint"]["journalCursor"] == 4
    assert accepted["broadcastId"] == element.broadcast_id


def test_runtime_checkpoint_failure_fails_only_its_job(tmp_path):
    store = BroadcastTargetStore(tmp_path / "targets", _scope())
    journal_store = EntropyJournalStore(tmp_path / "journals", key=Fernet.generate_key())
    collector = Collector()
    failed_ids = []

    def accept(rows):
        store.accept(rows)
        failed_ids.append(next(row["broadcastId"] for row in rows if row["signature"] == "BAD"))

    def checkpoint(payload):
        if failed_ids and payload["broadcastId"] == failed_ids[0] and payload["checkpoint"]["drawCount"]:
            raise OSError("synthetic runtime checkpoint failure")
        store.record_entropy(payload)

    def factory(_target):
        return EntropyProvider(
            mode="stochastic",
            random_org=RandomOrgSource(http_get=None),
            os_source=SequenceOS([426, 101, 202, 303]),
            journal=journal_store.create(),
        )

    manager = BroadcastManager(
        entropy=EntropyProvider(seed=0),
        emit=collector,
        entropy_factory=factory,
        on_accept=accept,
        on_abort=store.terminal,
        on_entropy=checkpoint,
    )
    manager._start_thread = lambda: None
    rows = manager.enqueue_batch(
        [
            {"signature": "BAD", "seconds": 60, "multiplier": 1000, "target": _target("stochastic", "a").payload()},
            {"signature": "GOOD", "seconds": 60, "multiplier": 1000, "target": _target("stochastic", "b").payload()},
        ],
        on_accepted=lambda _ids: None,
    )
    manager._promote_from_queue()
    bad, good = manager._active

    with pytest.raises(OSError, match="runtime checkpoint failure"):
        manager._resonance_draw(bad)
    manager._fail(bad, OSError("runtime checkpoint failure"))
    manager._resonance_draw(good)

    bad_target = next(row["target"] for row in store._jobs.values() if row["signature"] == "BAD")
    good_target = next(row["target"] for row in store._jobs.values() if row["signature"] == "GOOD")
    assert store.get(bad_target["jobId"])["state"] == "failed"
    assert store.get(good_target["jobId"])["state"] == "accepted"
    assert [element.broadcast_id for element in manager._active] == [rows[1]["broadcastId"]]
    resonances = [payload for event, payload in collector.events if event == "broadcast.resonance"]
    assert [payload["broadcastId"] for payload in resonances] == [rows[1]["broadcastId"]]
    assert manager.queue_state()["resonanceTotals"] == {"GOOD": 1}


def test_entropy_checkpoint_is_hashed_validated_and_mode_bound(tmp_path):
    store = BroadcastTargetStore(tmp_path / "targets", _scope())
    target = _target("seeded", "f")
    entry = _entry(target)
    store.accept([entry])
    checkpoint = EntropyProvider(seed=0).checkpoint()
    with pytest.raises(BroadcastTargetError, match="Modus"):
        store.record_entropy({"broadcastId": entry["broadcastId"], "checkpoint": {**checkpoint, "mode": "stochastic"}})

    store.record_entropy({"broadcastId": entry["broadcastId"], "checkpoint": checkpoint})
    stored = store.get(target.payload()["jobId"])
    assert stored["entropyCheckpoint"]["checkpoint"] == checkpoint
    path = tmp_path / "targets" / f"{target.payload()['jobId']}.entropy.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["checkpoint"]["drawCount"] = 99
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(BroadcastTargetError, match="Prüfsumme|Checkpoint"):
        BroadcastTargetStore(tmp_path / "targets", _scope())


def test_restart_rejects_unhashable_entropy_checkpoint_reference(tmp_path):
    store = BroadcastTargetStore(tmp_path / "targets", _scope())
    target = _target("seeded", "8")
    entry = _entry(target)
    store.accept([entry])
    store.record_entropy({"broadcastId": entry["broadcastId"], "checkpoint": EntropyProvider(seed=0).checkpoint()})
    path = tmp_path / "targets" / f"{target.payload()['jobId']}.entropy.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["jobId"] = []
    record["digest"] = document_digest({key: value for key, value in record.items() if key != "digest"})
    path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(BroadcastTargetError, match="ungültige Referenzen|Prüfsumme"):
        BroadcastTargetStore(tmp_path / "targets", _scope())


def test_factory_and_checkpoint_io_errors_leave_no_visible_job(tmp_path):
    collector = Collector()
    accepted = []
    target = _target()
    manager = BroadcastManager(
        entropy=EntropyProvider(seed=0),
        emit=collector,
        entropy_factory=lambda _: (_ for _ in ()).throw(RuntimeError("factory failure")),
        on_accept=lambda rows: accepted.extend(rows),
    )
    manager._start_thread = lambda: None
    with pytest.raises(RuntimeError, match="factory failure"):
        manager.enqueue("FAIL", 5, target=target)
    assert accepted == []
    assert manager.queue_state()["queued"] == []
    assert collector.events == []

    store = BroadcastTargetStore(tmp_path / "targets", _scope())
    failing = BroadcastManager(
        entropy=EntropyProvider(seed=0),
        emit=collector,
        entropy_factory=lambda _: EntropyProvider(seed=0),
        on_accept=store.accept,
        on_abort=store.terminal,
        on_entropy=lambda _: (_ for _ in ()).throw(OSError("checkpoint failure")),
    )
    failing._start_thread = lambda: None
    with pytest.raises(OSError, match="checkpoint failure"):
        failing.enqueue("CHECKPOINT FAIL", 5, target=_target(marker="9"))
    assert failing.queue_state()["queued"] == []
    assert not any(event == "emitter.sequence" for event, _ in collector.events)
    # Acceptance is durable but failed, never auto-enqueued after restart.
    rows = list(store._jobs.values())
    assert len(rows) == 1
    assert store.get(rows[0]["target"]["jobId"])["state"] == "failed"