"""Pre-write S3 rollback barrier; caller holds an immediate SQLite transaction.

No journal is created for legacy transactions. No authorization is inferred here;
the existing protected action and single-worker admission remain mandatory.
"""
import json
import uuid

from .change_journal import _load, _observe, _reconstruct
from .change_journal_evidence import rollback_transaction
from .evidence import fingerprint, now


def require_no_physical_claim(db):
    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='pilot_apply_transactions'").fetchone():
        if db.execute("SELECT 1 FROM pilot_apply_transactions WHERE status IN ('running','rolling_back','interrupted','recovery_needed')").fetchone():
            raise ValueError('Physische Übernahme/Rücknahme unvollständig; Journalfortschritt gesperrt.')


def prepare(db,tx):
    tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('dependent_change_chains','dependent_change_events')")}
    if not tables:return None
    if len(tables)!=2:raise ValueError('Änderungsjournal unvollständig; Rücknahme gesperrt.')
    matches=db.execute("SELECT DISTINCT chain_id FROM dependent_change_events WHERE json_extract(body,'$.kind')='transition' AND json_extract(body,'$.evidence.transaction.id')=?",(tx['id'],)).fetchall()
    if not matches:return None
    if len(matches)!=1:raise ValueError('Transaktion mehrdeutig an Änderungsketten gebunden.')
    key=matches[0]['chain_id'];chain,events,state=_load(db,key)
    target=next(e for e in events if e['kind']=='transition' and e['evidence']['transaction']['id']==tx['id'])
    rollback_transaction(target['evidence']['transaction'],dict(tx,status='rolled_back'))
    if target['id'] not in state['active_transition_ids']:
        if tx['status']=='rolled_back' and any(e['kind']=='rollback' and e['target_id']==target['id'] for e in events):
            return None  # Historical retry; never replay a physical write.
        raise ValueError('Transaktionsstatus widerspricht der Rücknahmehistorie.')
    if state['active_transition_ids'][-1]!=target['id']:
        raise ValueError('Zuerst das jüngste übernommene Änderungsglied zurücknehmen.')
    later=db.execute("""SELECT 1 FROM pilot_apply_transactions
        WHERE rowid>(SELECT rowid FROM pilot_apply_transactions WHERE id=?)
        AND json_extract(body,'$.original_root')=? AND status NOT IN ('rolled_back','conflict') LIMIT 1""",
        (tx['id'],tx['original_root'])).fetchone()
    if later:raise ValueError('Neuere Übernahme derselben Wurzel muss zuerst geklärt oder zurückgenommen werden.')
    try:
        _observe(chain['binding'],state['files'])
    except ValueError:
        if tx['status'] not in ('recovery_needed','rolled_back'):
            raise
        # Only a fully restored before-state permits explicit terminal-commit recovery.
        before=dict(state['files'])
        for f in tx['files']:before[f['path']]=f['before']
        _observe(chain['binding'],before)
    return dict(chain_id=key,head_id=state['head_id'],head_hash=state['head_hash'],target_id=target['id'])


def finish(db,guard,tx):
    """Append rollback in the same commit as terminal transaction status."""
    if guard is None:return
    chain,events,state=_load(db,guard['chain_id'])
    if state['head_id']!=guard['head_id'] or state['head_hash']!=guard['head_hash']:
        raise ValueError('Änderungshistorie seit Rücknahmefreigabe verändert.')
    request=dict(chain_id=chain['id'],previous_id=state['head_id'],kind='rollback',
        target_id=guard['target_id'],evidence=tx,note='Ausdrücklich angeforderte Pilot-Rücknahme abgeschlossen.')
    request_hash=fingerprint(request)
    event=dict(request,id=uuid.uuid4().hex,ordinal=len(events),previous_hash=state['head_hash'],
        request_hash=request_hash,created_at=now(),execution_authorized=False)
    updated=_reconstruct(chain,events+[event]);_observe(chain['binding'],updated['files'])
    db.execute('INSERT INTO dependent_change_events VALUES(?,?,?,?,?,?)',
        (event['id'],chain['id'],event['ordinal'],request_hash,fingerprint(event),json.dumps(event,ensure_ascii=False)))
