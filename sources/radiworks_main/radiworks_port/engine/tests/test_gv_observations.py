import importlib.util
import copy
import uuid
from pathlib import Path

import pytest
from radiworks.core.broadcast import BroadcastManager
from radiworks.core.observation_binding import ObservationBinding
from radiworks.entropy import EntropyProvider
from radiworks.scope import ScopeContext

def fixture_entropy():
    # Deterministic injected values; this shape test is not an OS quality proof.
    return {'mode': 'stochastic', 'activeSource': 'os', 'drawCount': 6, 'effectiveSeed': None,
            'sourceSegment': 0, 'journalId': uuid.uuid4().hex, 'journalCursor': 6,
            'journalDigest': 'c'*64, 'journalPrefixDigest': 'c'*64}

SCOPE = ScopeContext(tenant_id='local', client_id='local', job_id='local')

def controller(tmp_path, *, values=None):
    assert importlib.util.find_spec('radiworks.core.gv_observations') is not None, 'GV-2 controller not implemented'
    from radiworks.core.gv_observations import GvObservationController
    now = [0.0]
    manager = BroadcastManager(EntropyProvider(seed=7), lambda *_: None)
    manager._start_thread = lambda: None
    binding = ObservationBinding(SCOPE, 'a'*64, uuid.uuid4().hex, str(uuid.uuid4()), 0, 0, 'b'*64)
    ids = []
    entry = manager.enqueue_batch([{'signature': 'Synthetic rate', 'seconds': 4000, 'observationBinding': binding.payload()}], on_accepted=ids.extend)[0]
    manager._promote_from_queue()
    observations = values or [(700, 800), (690, 500)]
    calls = []
    def draw():
        calls.append(True)
        c, r = observations[min(len(calls)-1, len(observations)-1)]
        return {'caseGv': c, 'rateGv': r, 'entropy': fixture_entropy()}
    ctl = GvObservationController(tmp_path / 'observations', SCOPE, manager, draw=draw, ready=lambda: None, clock=lambda: now[0])
    return ctl, manager, entry, now, calls

def test_default_off_and_exact_interval_then_history_without_original_mutation(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    before = copy.deepcopy(entry['observationBinding'])
    now[0] = 2000
    ctl.tick()
    assert not calls
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] += 1259.999
    ctl.tick()
    assert not calls
    now[0] += .001
    ctl.tick()
    rows = ctl.history()['records']
    assert len(rows) == 1 and rows[0]['rateGv'] == 800
    assert rows[0]['rateTrend']['direction'] == 'baseline'
    assert rows[0]['binding'] == before
    now[0] += 1260
    ctl.tick()
    rows = ctl.history()['records']
    assert len(rows) == 2
    assert rows[-1]['rateTrend'] == {'direction': 'strong_down', 'delta': -300}
    assert manager.queue_state()['active'][0]['observationBinding'] == before

def test_stop_during_draw_discards_observation(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    original = ctl._draw
    def stop():
        result = original()
        manager.stop_all()
        return result
    ctl._draw = stop
    now[0] = 1260
    ctl.tick()
    assert calls and ctl.history()['records'] == []
    assert not ctl.snapshot()['controls'][0]['enabled']

def test_disable_during_draw_discards_observation(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    original = ctl._draw
    def disable():
        result = original()
        ctl.set_enabled(entry['broadcastId'], False)
        return result
    ctl._draw = disable
    now[0] = 1260
    ctl.tick()
    assert calls and ctl.history()['records'] == []

def test_write_failure_disables_and_never_returns_success_history(tmp_path, monkeypatch):
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    from radiworks.core import gv_observations
    def fail(*_): raise OSError('synthetic disk fault')
    monkeypatch.setattr(gv_observations, 'atomic_json_replace', fail)
    now[0] = 1260
    ctl.tick()
    assert ctl.history()['records'] == []
    status = ctl.snapshot()['controls'][0]
    assert not status['enabled'] and status['error']

def test_restart_history_survives_but_activation_does_not(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] = 1260
    ctl.tick()
    from radiworks.core.gv_observations import GvObservationController
    restarted = GvObservationController(tmp_path / 'observations', SCOPE, manager, draw=ctl._draw, ready=lambda: None, clock=lambda: now[0])
    now[0] += 9000
    restarted.tick()
    assert len(restarted.history()['records']) == 1
    assert restarted.snapshot()['controls'] == []
    assert len(calls) == 1

def test_unbound_and_queued_are_ineligible(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    direct = manager.enqueue('Synthetic direct', 4000)
    with pytest.raises(ValueError): ctl.set_enabled(direct['broadcastId'], True)
    manager._promote_from_queue()
    with pytest.raises(ValueError): ctl.set_enabled(direct['broadcastId'], True)
    assert entry['broadcastId'] in [x['broadcastId'] for x in ctl.snapshot()['eligible']]

@pytest.mark.parametrize('bad_id', ['../outside', '1'*31, 'z'*32, True])
def test_invalid_id_rejected(tmp_path, bad_id):
    ctl, *_ = controller(tmp_path)
    with pytest.raises(ValueError): ctl.set_enabled(bad_id, True)

def test_corrupt_history_is_visible_not_silently_replaced(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    path = tmp_path / 'observations' / (entry['broadcastId'] + '.json')
    path.parent.mkdir(exist_ok=True)
    path.write_text('{broken', encoding='utf8')
    with pytest.raises(ValueError): ctl.history()
    with pytest.raises(ValueError): ctl.set_enabled(entry['broadcastId'], True)
    assert path.read_text(encoding='utf8') == '{broken'


def test_os_observation_has_private_replay_journal_and_no_shared_draws(tmp_path, monkeypatch):
    from cryptography.fernet import Fernet
    from radiworks.core.gv_observations import journaled_os_draw
    from radiworks.entropy_journal import EntropyJournalStore
    key = Fernet.generate_key().decode()
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY', key)
    def forbidden(*_): raise AssertionError('network entropy was used')
    monkeypatch.setattr('radiworks.entropy._random_org_http_get', forbidden)
    unrelated = EntropyProvider(seed=42)
    before = unrelated.checkpoint()
    sample = journaled_os_draw(tmp_path / 'journals')
    assert sample['entropy']['activeSource'] == 'os'
    assert sample['entropy']['mode'] == 'stochastic'
    assert unrelated.checkpoint() == before
    journal = EntropyJournalStore(tmp_path / 'journals').open(sample['entropy']['journalId'])
    assert journal.cursor == sample['entropy']['drawCount'] >= 6
    assert journal.digest() == sample['entropy']['journalDigest']


def test_end_during_draw_discards_even_before_manager_finish(tmp_path):
    import time
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    def end():
        manager._active[0].start = time.monotonic() - 5000
        return {'caseGv': 20, 'rateGv': 30, 'entropy': fixture_entropy()}
    ctl._draw = end
    now[0] = 1260
    ctl.tick()
    assert ctl.history()['records'] == []
    assert not ctl.snapshot()['controls'][0]['enabled']


def test_repeated_enable_does_not_reset_deadline_or_double_draw(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] = 1200
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] = 1260
    ctl.tick()
    ctl.tick()
    assert len(calls) == 1


def test_stop_and_reenable_during_draw_cannot_commit_stale_generation(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    original = ctl._draw
    def change():
        sample = original()
        ctl.set_enabled(entry['broadcastId'], False)
        ctl.set_enabled(entry['broadcastId'], True)
        return sample
    ctl._draw = change
    now[0] = 1260
    ctl.tick()
    assert ctl.history()['records'] == []
    assert ctl.snapshot()['controls'][0]['nextInSeconds'] == 1260


def test_many_timer_intervals_do_not_trigger_catchup_burst(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] = 100000
    ctl.tick()
    ctl.tick()
    assert len(calls) == 1
    assert ctl.snapshot()['controls'][0]['nextInSeconds'] == 1260


def test_separate_broadcasts_same_rate_have_separate_history(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    other = manager.enqueue_batch([{'signature': entry['signature'], 'seconds': 4000,
        'observationBinding': entry['observationBinding']}], on_accepted=lambda _: None)[0]
    manager._promote_from_queue()
    ctl.set_enabled(entry['broadcastId'], True)
    ctl.set_enabled(other['broadcastId'], True)
    now[0] = 1260
    ctl.tick()
    rows = ctl.history()['records']
    assert {r['broadcastId'] for r in rows} == {entry['broadcastId'], other['broadcastId']}
    assert all(r['rateTrend']['direction'] == 'baseline' for r in rows)


def test_foreign_scope_binding_is_ineligible(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    binding = dict(entry['observationBinding'])
    binding['scope'] = {'tenant_id': 'foreign', 'client_id': 'local', 'job_id': 'local'}
    other = manager.enqueue_batch([{'signature': 'Other rate', 'seconds': 4000,
        'observationBinding': binding}], on_accepted=lambda _: None)[0]
    manager._promote_from_queue()
    with pytest.raises(ValueError): ctl.set_enabled(other['broadcastId'], True)


def test_entropic_failure_disables_without_history(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    def fail(): raise RuntimeError('synthetic source failure')
    ctl._draw = fail
    now[0] = 1260
    ctl.tick()
    assert ctl.history()['records'] == []
    assert not ctl.snapshot()['controls'][0]['enabled']


@pytest.mark.parametrize('value,previous,expected', [(1,None,'baseline'),(10,10,'flat'),(11,10,'up'),(9,10,'down'),(210,10,'strong_up'),(0,200,'strong_down')])
def test_display_trend_thresholds(value, previous, expected):
    from radiworks.core.gv_observations import trend
    assert trend(value, previous)['direction'] == expected


def test_shutdown_during_first_of_multiple_due_draws_stops_further_draws(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    other = manager.enqueue_batch([{'signature': 'Second rate', 'seconds': 4000,
        'observationBinding': entry['observationBinding']}], on_accepted=lambda _: None)[0]
    manager._promote_from_queue()
    ctl.set_enabled(entry['broadcastId'], True)
    ctl.set_enabled(other['broadcastId'], True)
    original = ctl._draw
    def shutdown():
        result = original()
        ctl.shutdown()
        return result
    ctl._draw = shutdown
    now[0] = 1260
    ctl.tick()
    assert len(calls) == 1, 'No new entropy journal after shutdown request'
    assert not ctl._inflight
    assert ctl.history()['records'] == []


def test_shutdown_reports_unfinished_writer_instead_of_claiming_release(tmp_path):
    import threading
    ctl, manager, entry, now, calls = controller(tmp_path)
    entered, release = threading.Event(), threading.Event()
    original = ctl._draw
    def block():
        entered.set()
        assert release.wait(3)
        return original()
    ctl._draw = block
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] = 1260
    ctl._thread = threading.Thread(target=ctl.tick)
    ctl._thread.start()
    assert entered.wait(2)
    try:
        with pytest.raises(RuntimeError): ctl.shutdown(timeout=.01)
    finally:
        release.set()
        ctl.shutdown(timeout=2)
    assert not ctl._thread.is_alive()
    assert ctl.history()['records'] == []


@pytest.mark.parametrize('bad_entropy', [{}, {'mode':'seeded'}, {'mode':'stochastic','activeSource':'webcam'}])
def test_invalid_entropy_evidence_never_commits(tmp_path, bad_entropy):
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl._draw = lambda: {'caseGv': 2, 'rateGv': 3, 'entropy': bad_entropy}
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] = 1260
    ctl.tick()
    assert ctl.history()['records'] == []
    assert not ctl.snapshot()['controls'][0]['enabled']


def test_exact_persisted_byte_limit_preserves_previous_readable_history(tmp_path, monkeypatch):
    import json
    from radiworks.core import gv_observations
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] = 1260
    ctl.tick()
    path = tmp_path / 'observations' / (entry['broadcastId'] + '.json')
    first_bytes = path.read_bytes()
    monkeypatch.setattr(gv_observations, 'MAX_BYTES', len(first_bytes) + 10)
    now[0] += 1260
    ctl.tick()
    assert path.read_bytes() == first_bytes
    assert len(ctl.history()['records']) == 1
    assert not ctl.snapshot()['controls'][0]['enabled']


@pytest.mark.parametrize('action', ['stop', 'disable', 'reenable'])
def test_actual_thread_interleaving_during_observation(tmp_path, action):
    import threading
    ctl, manager, entry, now, calls = controller(tmp_path)
    entered, release = threading.Event(), threading.Event()
    original = ctl._draw
    def block():
        entered.set()
        assert release.wait(3)
        return original()
    ctl._draw = block
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] = 1260
    worker = threading.Thread(target=ctl.tick)
    worker.start()
    assert entered.wait(2)
    try:
        if action == 'stop': manager.stop_all()
        else:
            ctl.set_enabled(entry['broadcastId'], False)
            if action == 'reenable': ctl.set_enabled(entry['broadcastId'], True)
    finally:
        release.set()
        worker.join(2)
    assert not worker.is_alive()
    assert ctl.history()['records'] == []
    assert not ctl._inflight


@pytest.mark.parametrize('change', ['scope', 'binding', 'mode', 'extra', 'digest', 'source_segment'])
def test_history_tampering_fails_closed_without_replacing_file(tmp_path, change):
    import json
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] = 1260
    ctl.tick()
    path = tmp_path / 'observations' / (entry['broadcastId'] + '.json')
    doc = json.loads(path.read_text(encoding='utf8'))
    if change == 'scope': doc['binding']['scope']['tenant_id'] = 'foreign'
    elif change == 'binding': doc['binding']['sessionId'] = '0'*32
    elif change == 'mode': doc['records'][0]['entropy']['mode'] = 'seeded'
    elif change == 'extra': doc['records'][0]['entropy']['unexpected'] = 'extra'
    elif change == 'digest': doc['records'][0]['entropy']['journalPrefixDigest'] = '0'*64
    else: doc['records'][0]['entropy']['sourceSegment'] = True
    path.write_text(json.dumps(doc),encoding='utf8')
    data = path.read_bytes()
    if change == 'binding':
        ctl.set_enabled(entry['broadcastId'], False)
        with pytest.raises(ValueError): ctl.set_enabled(entry['broadcastId'], True)
    else:
        with pytest.raises(ValueError): ctl.history()
    assert path.read_bytes() == data


def test_capacity_does_not_evict_old_observations(tmp_path, monkeypatch):
    from radiworks.core import gv_observations
    ctl, manager, entry, now, calls = controller(tmp_path)
    ctl.set_enabled(entry['broadcastId'], True)
    now[0] = 1260
    ctl.tick()
    before = ctl.history()['records']
    monkeypatch.setattr(gv_observations,'MAX_RECORDS',1)
    now[0] += 1260
    ctl.tick()
    assert ctl.history()['records'] == before
    assert not ctl.snapshot()['controls'][0]['enabled']


def test_history_bound_file_count(tmp_path, monkeypatch):
    from radiworks.core import gv_observations
    ctl, manager, entry, now, calls = controller(tmp_path)
    monkeypatch.setattr(gv_observations,'MAX_FILES',0)
    with pytest.raises(ValueError): ctl.set_enabled(entry['broadcastId'], True)


def test_symlink_history_cannot_escape_root(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    outside = tmp_path / 'outside.json'
    outside.write_text('{}',encoding='utf8')
    path = tmp_path / 'observations' / (entry['broadcastId'] + '.json')
    try: path.symlink_to(outside)
    except OSError: pytest.skip('Windows symlink privilege unavailable')
    with pytest.raises(ValueError): ctl.set_enabled(entry['broadcastId'], True)
    assert outside.read_text(encoding='utf8') == '{}'


def test_byte_budget_between_compact_and_disk_serialization_rejects_before_write(tmp_path, monkeypatch):
    import json
    from datetime import datetime, timezone
    from types import SimpleNamespace
    from radiworks.core import gv_observations as gv
    ctl, manager, entry, now, calls = controller(tmp_path)
    sample = {'caseGv': 700, 'rateGv': 800, 'entropy': fixture_entropy()}
    identifier = 'f'*32
    instant = datetime(2026,10,4,12,0,0,tzinfo=timezone.utc)
    row = {'observationId':identifier, 'observedAt':instant.isoformat(),
           'caseGv':700, 'rateGv':800, 'entropy':sample['entropy'],
           'caseTrend':{'direction':'baseline','delta':None}, 'rateTrend':{'direction':'baseline','delta':None}}
    document = {'schema':'radiworks.gv-observations.v1','broadcastId':entry['broadcastId'],
                'binding':entry['observationBinding'],'records':[row]}
    compact = len(json.dumps(document).encode('utf8'))
    on_disk = len(json.dumps(document,ensure_ascii=False,indent=2).encode('utf8'))
    assert compact < on_disk
    monkeypatch.setattr(gv,'MAX_BYTES',(compact+on_disk)//2)
    monkeypatch.setattr(gv,'uuid',SimpleNamespace(uuid4=lambda:SimpleNamespace(hex=identifier)))
    monkeypatch.setattr(gv,'datetime',SimpleNamespace(now=lambda *_:instant))
    with pytest.raises(ValueError): ctl._persist(entry['broadcastId'], entry['observationBinding'], sample)
    assert not (tmp_path/'observations'/(entry['broadcastId']+'.json')).exists()


def test_history_session_index_keeps_older_sessions_outside_latest_200(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    first = entry['observationBinding']
    ctl._persist(entry['broadcastId'], first, {'caseGv':700,'rateGv':800,'entropy':fixture_entropy()})
    newer = copy.deepcopy(first)
    newer['sessionId'] = uuid.uuid4().hex
    second_bid = uuid.uuid4().hex
    for _ in range(201):
        ctl._persist(second_bid, newer, {'caseGv':700,'rateGv':800,'entropy':fixture_entropy()})
    history = ctl.history()
    assert history['truncated'] and len(history['records']) == 200
    assert all(r['binding']['sessionId'] == newer['sessionId'] for r in history['records'])
    index = {s['sessionId']:s for s in history['sessionIndex']}
    assert index[first['sessionId']]['records'] == 1
    assert index[newer['sessionId']]['records'] == 201
    older = ctl.history(session_id=first['sessionId'])
    assert older['total'] == 1 and len(older['records']) == 1
    assert len(older['sessionIndex']) == 2


def test_history_index_rejects_one_session_reassigned_to_another_case(tmp_path):
    ctl, manager, entry, now, calls = controller(tmp_path)
    first = entry['observationBinding']
    ctl._persist(entry['broadcastId'], first, {'caseGv':700,'rateGv':800,'entropy':fixture_entropy()})
    conflicting = copy.deepcopy(first)
    conflicting['caseRef'] = 'd'*64
    ctl._persist(uuid.uuid4().hex, conflicting, {'caseGv':700,'rateGv':800,'entropy':fixture_entropy()})
    with pytest.raises(ValueError): ctl.history()
