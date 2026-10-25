"""Opt-in GV observations; independent entropy, immutable broadcast identity."""
from __future__ import annotations

import copy
import json
import logging
import re
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from ..entropy import EntropyProvider, RandomOrgSource
from ..entropy_journal import EntropyJournalStore
from ..persistence import atomic_json_replace
from ..scope import ScopeContext
from .analysis import check_general_vitality
from .observation_binding import ObservationBinding

INTERVAL_SECONDS = 1260
MAX_RECORDS = 1000
MAX_FILES = 256
MAX_BYTES = 1024 * 1024
_HEX = re.compile(r'[0-9a-f]{32}\Z')


def trend(value: int, previous: int | None) -> dict:
    if previous is None:
        return {'direction': 'baseline', 'delta': None}
    delta = value - previous
    direction = 'flat' if delta == 0 else ('up' if delta > 0 else 'down')
    if abs(delta) >= 200:
        direction = 'strong_' + direction
    return {'direction': direction, 'delta': delta}


def validate_entropy(evidence: object) -> None:
    fields = {'mode', 'activeSource', 'drawCount', 'effectiveSeed', 'sourceSegment',
              'journalId', 'journalCursor', 'journalDigest', 'journalPrefixDigest'}
    if type(evidence) is not dict or set(evidence) != fields:
        raise ValueError('Entropiebeleg verletzt')
    if evidence['mode'] != 'stochastic' or evidence['activeSource'] != 'os' or evidence['effectiveSeed'] is not None:
        raise ValueError('Beobachtung braucht eigenen OS-Entropiestrom')
    if (type(evidence['sourceSegment']) is not int or evidence['sourceSegment'] != 0
            or type(evidence['drawCount']) is not int or not 6 <= evidence['drawCount'] <= 100000
            or type(evidence['journalCursor']) is not int or evidence['journalCursor'] != evidence['drawCount']):
        raise ValueError('Entropiecursor verletzt')
    if type(evidence['journalId']) is not str or not _HEX.fullmatch(evidence['journalId']):
        raise ValueError('Entropiejournal-ID verletzt')
    for field in ('journalDigest', 'journalPrefixDigest'):
        if type(evidence[field]) is not str or not re.fullmatch(r'[0-9a-f]{64}', evidence[field]):
            raise ValueError('Entropiejournal-Digest verletzt')
    if evidence['journalDigest'] != evidence['journalPrefixDigest']:
        raise ValueError('Entropiejournal-Praefix verletzt')


def journaled_os_draw(root: Path) -> dict:
    # No shared webcam/random.org pool and no seeded fallback for observations.
    journal = EntropyJournalStore(root).create()
    entropy = EntropyProvider(mode='stochastic', random_org=RandomOrgSource(http_get=None), journal=journal)
    with entropy.journal_write_scope():
        case_gv = check_general_vitality(entropy)
        rate_gv = check_general_vitality(entropy)
    entropy.commit_journal()
    checkpoint = entropy.checkpoint()
    checkpoint.pop('source', None)  # Preserve the accepted GV-history receipt schema.
    return {'caseGv': case_gv, 'rateGv': rate_gv,
            'entropy': {**checkpoint, 'activeSource': entropy.status().active_source}}


class GvObservationController:
    def __init__(self, root: Path, scope: ScopeContext, broadcast, *, draw: Callable[[], dict],
                 ready: Callable[[], None], clock: Callable[[], float] = time.monotonic) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.scope, self.broadcast = scope, broadcast
        self._draw, self._ready, self._clock = draw, ready, clock
        self._lock = threading.RLock()
        self._controls: dict[str, dict] = {}
        self._inflight: set[str] = set()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _path(self, broadcast_id: str) -> Path:
        if type(broadcast_id) is not str or not _HEX.fullmatch(broadcast_id):
            raise ValueError('Ungueltige Broadcast-ID')
        path = self.root / (broadcast_id + '.json')
        if path.is_symlink() or path.resolve().parent != self.root:
            raise ValueError('Beobachtungspfad ist nicht lokal')
        return path

    def _read(self, broadcast_id: str, binding: dict | None = None) -> dict | None:
        path = self._path(broadcast_id)
        if not path.exists():
            return None
        if path.stat().st_size > MAX_BYTES:
            raise ValueError('Beobachtungshistorie ist zu gross')
        try:
            doc = json.loads(path.read_text(encoding='utf8'))
            if set(doc) != {'schema', 'broadcastId', 'binding', 'records'} or doc['schema'] != 'radiworks.gv-observations.v1':
                raise ValueError('Historienvertrag verletzt')
            owned = ObservationBinding.from_payload(doc['binding'])
            if owned.scope != self.scope or doc['broadcastId'] != broadcast_id:
                raise ValueError('Historienzuordnung verletzt')
            if binding is not None and doc['binding'] != binding:
                raise ValueError('Historienbindung hat sich geaendert')
            rows = doc['records']
            if type(rows) is not list or len(rows) > MAX_RECORDS:
                raise ValueError('Historiengrenze verletzt')
            previous = None
            ids = set()
            for row in rows:
                if type(row) is not dict or set(row) != {'observationId', 'observedAt', 'caseGv', 'rateGv', 'caseTrend', 'rateTrend', 'entropy'}:
                    raise ValueError('Historieneintrag verletzt')
                if type(row['observationId']) is not str or not _HEX.fullmatch(row['observationId']) or row['observationId'] in ids:
                    raise ValueError('Doppelte/ungueltige Beobachtung')
                ids.add(row['observationId'])
                if type(row['observedAt']) is not str or datetime.fromisoformat(row['observedAt']).tzinfo is None:
                    raise ValueError('Beobachtungszeit fehlt')
                if any(type(row[k]) is not int or row[k] < 0 for k in ('caseGv', 'rateGv')) or type(row['entropy']) is not dict:
                    raise ValueError('Beobachtungswerte verletzt')
                validate_entropy(row['entropy'])
                for value, key in [('caseGv', 'caseTrend'), ('rateGv', 'rateTrend')]:
                    if row[key] != trend(row[value], previous[value] if previous else None):
                        raise ValueError('Historientendenz verletzt')
                previous = row
            return doc
        except (OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
            raise ValueError('Beobachtungshistorie kann nicht geprueft werden') from exc

    def _eligible(self) -> list[dict]:
        result = []
        for entry in self.broadcast.queue_state()['active']:
            if entry.get('progress', 0) >= 1:
                continue
            try:
                binding = ObservationBinding.from_payload(entry.get('observationBinding'))
            except (TypeError, ValueError):
                continue
            if binding.scope == self.scope:
                result.append(entry)
        return result

    def set_enabled(self, broadcast_id: str, enabled: bool) -> dict:
        self._path(broadcast_id)
        if type(enabled) is not bool:
            raise ValueError('enabled muss bool sein')
        with self._lock:
            if self._stop.is_set():
                raise ValueError('Beobachtungsworker ist beendet')
            if not enabled:
                item = self._controls.get(broadcast_id)
                if item:
                    item['enabled'] = False
                    item['generation'] = uuid.uuid4().hex
                return self.snapshot()
            entry = next((e for e in self._eligible() if e['broadcastId'] == broadcast_id), None)
            if entry is None:
                raise ValueError('Nur aktiv gebundene Promotionsraten sind beobachtbar')
            self._ready()
            self._read(broadcast_id, entry['observationBinding'])
            item = self._controls.get(broadcast_id)
            if item and item['enabled']:
                return self.snapshot()
            if broadcast_id not in self._controls and len(self._controls) >= MAX_FILES:
                raise ValueError('Beobachtungssteuerungsgrenze erreicht')
            self._controls[broadcast_id] = {
                'enabled': True, 'binding': entry['observationBinding'], 'generation': uuid.uuid4().hex,
                'nextDue': self._clock() + INTERVAL_SECONDS, 'error': None,
            }
            return self.snapshot()

    def snapshot(self) -> dict:
        with self._lock:
            eligible = self._eligible()
            active_ids = {e['broadcastId'] for e in eligible}
            now = self._clock()
            controls = []
            for bid, item in self._controls.items():
                if bid not in active_ids and item['enabled']:
                    item['enabled'] = False
                    item['error'] = 'Broadcast nicht mehr aktiv'
                controls.append({'broadcastId': bid, 'binding': copy.deepcopy(item['binding']),
                                 'enabled': item['enabled'], 'error': item['error'],
                                 'nextInSeconds': max(0, round(item['nextDue'] - now)) if item['enabled'] else None})
            all_active = self.broadcast.queue_state()['active']
            return {'intervalSeconds': INTERVAL_SECONDS, 'source': 'os', 'restartPolicy': 'off',
                    'eligible': copy.deepcopy(eligible), 'controls': controls,
                    'excludedCount': len(all_active) - len(eligible), 'strongDeltaThreshold': 200}

    def history(self, *, session_id: str | None = None, case_ref: str | None = None) -> dict:
        with self._lock:
            paths = list(self.root.glob('*.json'))
            if len(paths) > MAX_FILES:
                raise ValueError('Historien-Dateigrenze erreicht')
            records = []
            sessions = {}
            for path in paths:
                doc = self._read(path.stem)
                if doc is None:
                    continue
                binding = doc['binding']
                sid = binding['sessionId']
                if sid in sessions and sessions[sid]['caseRef'] != binding['caseRef']:
                    raise ValueError('Sitzung mehreren Faellen zugeordnet')
                session = sessions.setdefault(sid, {'sessionId': sid, 'caseRef': binding['caseRef'], 'records': 0})
                session['records'] += len(doc['records'])
                if session_id is not None and binding['sessionId'] != session_id:
                    continue
                if case_ref is not None and binding['caseRef'] != case_ref:
                    continue
                for row in doc['records']:
                    records.append({**copy.deepcopy(row), 'broadcastId': doc['broadcastId'], 'binding': copy.deepcopy(binding)})
            records.sort(key=lambda r: (r['observedAt'], r['observationId']))
            return {'records': records[-200:], 'total': len(records), 'truncated': len(records) > 200,
                    'limitPerBroadcast': MAX_RECORDS, 'sessionIndex': list(sessions.values())}

    def _persist(self, bid: str, binding: dict, sample: dict) -> None:
        doc = self._read(bid, binding) or {'schema': 'radiworks.gv-observations.v1',
                                         'broadcastId': bid, 'binding': binding, 'records': []}
        if len(doc['records']) >= MAX_RECORDS:
            raise ValueError('Beobachtungskapazitaet erreicht')
        if not self._path(bid).exists() and len(list(self.root.glob('*.json'))) >= MAX_FILES:
            raise ValueError('Historien-Dateigrenze erreicht')
        for key in ('caseGv', 'rateGv'):
            if type(sample.get(key)) is not int or sample[key] < 0:
                raise ValueError('Ungueltiger Beobachtungswert')
        validate_entropy(sample.get('entropy'))
        previous = doc['records'][-1] if doc['records'] else None
        row = {'observationId': uuid.uuid4().hex, 'observedAt': datetime.now(timezone.utc).isoformat(),
               'caseGv': sample['caseGv'], 'rateGv': sample['rateGv'], 'entropy': copy.deepcopy(sample['entropy']),
               'caseTrend': trend(sample['caseGv'], previous['caseGv'] if previous else None),
               'rateTrend': trend(sample['rateGv'], previous['rateGv'] if previous else None)}
        doc['records'].append(row)
        if len(json.dumps(doc, ensure_ascii=False, indent=2).encode('utf8')) > MAX_BYTES:
            raise ValueError('Historien-Bytegrenze erreicht')
        atomic_json_replace(self._path(bid), doc)

    def tick(self) -> None:
        with self._lock:
            if self._stop.is_set():
                return
            self.snapshot()
            due = [(bid, copy.deepcopy(item)) for bid, item in self._controls.items()
                   if item['enabled'] and item['nextDue'] <= self._clock() and bid not in self._inflight]
            self._inflight.update(bid for bid, _ in due)
        for bid, captured in due:
            try:
                with self._lock:
                    current = self._controls[bid]
                    if (self._stop.is_set() or not current['enabled']
                            or current['generation'] != captured['generation']):
                        continue
                sample = self._draw()
                with self._lock:
                    item = self._controls[bid]
                    if self._stop.is_set() or not item['enabled'] or item['generation'] != captured['generation']:
                        continue
                    committed = self.broadcast.commit_observation_if_active(
                        bid, captured['binding'], lambda: self._persist(bid, captured['binding'], sample))
                    if committed:
                        item['nextDue'] = self._clock() + INTERVAL_SECONDS
                    else:
                        item['enabled'] = False
                        item['error'] = 'Broadcast waehrend Beobachtung beendet'
            except Exception as exc:
                logging.getLogger(__name__).error('GV observation failed: %s', type(exc).__name__)
                with self._lock:
                    item = self._controls[bid]
                    if item['generation'] == captured['generation']:
                        item['enabled'] = False
                        item['error'] = 'Beobachtung fehlgeschlagen: ' + type(exc).__name__
            finally:
                with self._lock:
                    self._inflight.discard(bid)

    def start(self) -> None:
        if self._thread is not None:
            return
        def work():
            while not self._stop.wait(1.0):
                self.tick()
        self._thread = threading.Thread(target=work, name='gv-observations', daemon=True)
        self._thread.start()

    def request_stop(self) -> None:
        self._stop.set()

    def shutdown(self, timeout: float | None = 2.0) -> None:
        self.request_stop()
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join(timeout)
            if self._thread.is_alive():
                raise RuntimeError('GV-Beobachtungswriter ist noch nicht beendet')
