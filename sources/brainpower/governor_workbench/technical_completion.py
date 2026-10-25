"""Operator-confirmed, source-bound closure of an isolated applied change.

No plan adoption, intake renewal, target tests or dependent execution permission.
"""
import json
import uuid
import hashlib
from pathlib import Path

from .evidence import fingerprint, now
from .plans import _id, _hash, _text


def adapter_hash():
    return fingerprint({name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                        for name in ('technical_completion.py','pilot_verification.py','pilot_actions.py')})


def binding(report):
    fields=('transaction_id','verified_test_job_id','stage_job_id','stage_id','manifest_hash',
            'candidate_id','step_id','step_hash','selection_id','plan_scope_hash',
            'observed_scope_hash','test_adapter_hash','completion_adapter_hash')
    if isinstance(report,dict) and 'successor_consent_id' in report:
        fields+=('successor_consent_id','successor_binding_hash','original_scope_hash',
                 'predecessor_event_id','predecessor_event_hash')
    if not isinstance(report,dict) or any(key not in report for key in fields):
        raise ValueError('Abschlussbindung unvollständig; erneut nachprüfen.')
    value={key:report[key] for key in fields}
    for key,item in value.items():
        (_hash if key.endswith('hash') else _id)(item)
    return value


def snapshot(store, transaction_id, report):
    """Derive freshness on explicit recheck; never trust old display status."""
    with store.db() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='technical_completions'").fetchone():
            return dict(status='not_recorded',receipt=None)
        row=db.execute('SELECT body FROM technical_completions WHERE transaction_id=? ORDER BY rowid DESC LIMIT 1',
                       (transaction_id,)).fetchone()
    if not row: return dict(status='not_recorded',receipt=None)
    receipt=json.loads(row['body'])
    current=False
    if report.get('evidence_usable') is True:
        try: current=fingerprint(receipt['binding'])==fingerprint(binding(report))
        except (KeyError,ValueError,TypeError): pass
    return dict(status='current' if current else 'stale',receipt=receipt)


def complete(app, verified_job_id, observed_scope_hash, note, cancel=None):
    _id(verified_job_id); _hash(observed_scope_hash); _text(note,2000)
    from .pilot_actions import _cancel
    from .pilot_verification import verify
    _cancel(cancel)
    with app.store.lock:
        job=app.store.job(verified_job_id)
        result=job.get('result') or {}
        previous=result.get('post_apply_verification') or {}
        tx_id=job['request'].get('transaction_id')
        if (job['action']!='pilot_verify' or job['status']!='completed'
                or result.get('success') is not True
                or previous.get('evidence_usable') is not True
                or not tx_id or previous.get('transaction_id')!=tx_id
                or previous.get('observed_scope_hash')!=observed_scope_hash):
            raise ValueError('Erfolgreicher angezeigter Nachprüfungsauftrag und passender Nachher-Hash erforderlich.')
        with app.store.db() as db:
            latest=db.execute("SELECT id FROM jobs WHERE action='pilot_verify' AND json_extract(request,'$.transaction_id')=? ORDER BY rowid DESC LIMIT 1",(tx_id,)).fetchone()
        if not latest or latest['id']!=verified_job_id:
            raise ValueError('Neuerer Nachprüfungsversuch vorhanden; aktuellen Bericht verwenden.')
        fresh=verify(app,tx_id,cancel)
        if fresh['evidence_usable'] is not True or fingerprint(binding(fresh))!=fingerprint(binding(previous)):
            raise ValueError('Nachweis seit Anzeige verändert oder gesperrt. Erneut nachprüfen.')
        if fresh['technical_completion']['status']=='current':
            raise ValueError('Dieser gebundene Übernahmeabschluss ist bereits bestätigt.')
        receipt=dict(id=uuid.uuid4().hex,transaction_id=tx_id,verified_job_id=verified_job_id,
                     binding=binding(fresh),created_at=now(),actor='operator',note=note,
                     kind='isolated_change_transfer_completion',status='recorded',
                     scope_observation_acknowledged=True,plan_rebased=False,
                     execution_enabled=False,product_gate_approved=False,target_tests_executed=False)
        _cancel(cancel)
        with app.store.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS technical_completions(
                    id TEXT PRIMARY KEY, transaction_id TEXT NOT NULL, body TEXT NOT NULL);
                CREATE TRIGGER IF NOT EXISTS technical_completions_no_update
                    BEFORE UPDATE ON technical_completions BEGIN SELECT RAISE(ABORT,'immutable completion'); END;
                CREATE TRIGGER IF NOT EXISTS technical_completions_no_delete
                    BEFORE DELETE ON technical_completions BEGIN SELECT RAISE(ABORT,'immutable completion'); END;
            ''')
            db.execute('INSERT INTO technical_completions VALUES(?,?,?)',
                       (receipt['id'],tx_id,json.dumps(receipt,ensure_ascii=False)))
        return receipt
