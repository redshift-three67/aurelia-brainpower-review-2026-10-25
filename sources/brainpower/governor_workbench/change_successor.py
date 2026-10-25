"""Explicit H1 acknowledgement for B; no execution grant or inherited tests.

Internal C3 foundation. Protected routes and execution adapters are separate.
Preview performs reads only; no journal schema or jobs are created by preview.
"""
import json
import uuid

from .change_controller import _claim, _collect, _environment, identity
from .change_journal import ChangeJournal, _observe as observe_files
from .evidence import fingerprint, now
from .pilot_actions import _cancel
from .plans import _hash, _id, _text


def _journal(store):
    value=ChangeJournal.__new__(ChangeJournal);value.store=store
    return value


def _observe(app,chain_id,cancel=None):
    journal=_journal(app.store);state=journal.read(chain_id)
    base=state['chain']['binding']
    if (state['requires_new_plan'] or len(state['events'])!=1
            or state['transition_count']!=1 or state['active_transition_ids']!=[state['head_id']]):
        raise ValueError('Genau ein bestätigter aktiver A-Übergang erforderlich.')
    event=state['events'][0];technical=event['evidence']['technical_receipt']
    with app.store.db() as db:
        later=db.execute("SELECT 1 FROM pilot_apply_transactions WHERE rowid>(SELECT rowid FROM pilot_apply_transactions WHERE id=?) AND json_extract(body,'$.original_root')=? LIMIT 1",
                         (technical['transaction_id'],base['root'])).fetchone()
    if later:raise ValueError('H1-Zustimmung wurde durch weiteren Übernahmeversuch verbraucht; neuer Plan erforderlich.')
    fresh,evidence=_collect(app,journal,chain_id,technical['id'],state['scope_hash'],
                            base['selection_id'],cancel,historical_tip=True)
    if fresh!=state:raise ValueError('Journal während H1-Prüfung verändert.')
    return dict(profile_id='dependent_successor_h1_v1',chain_id=chain_id,
                candidate_id=base['candidate_id'],selection_id=base['selection_id'],
                original_scope_hash=base['scope_hash'],effective_scope_hash=state['scope_hash'],
                predecessor_event_id=event['id'],predecessor_event_hash=state['head_hash'],
                predecessor_receipt_id=technical['id'],predecessor_receipt_hash=fingerprint(technical),
                predecessor_transaction_id=evidence['transaction']['id'],
                step_id=base['step_ids'][1],step_hash=base['step_hashes'][base['step_ids'][1]],
                root=base['root'],root_identity=base['root_identity'],files=state['files'],
                adapter_hash=identity(),environment_hash=_environment(app))


def preview(app,chain_id,cancel=None):
    result=dict(eligible=False,binding=None,binding_hash=None,execution_authorized=False,
                inherited_test_approval=False,model_transmission_required=False)
    _cancel(cancel)
    try:
        _id(chain_id)
        with app.store.db() as watch:
            tables={r[0] for r in watch.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not {'dependent_change_chains','dependent_change_events'}<=tables:
                raise ValueError('Bestätigtes Änderungsjournal fehlt.')
            version=watch.execute('PRAGMA data_version').fetchone()[0]
            first=_observe(app,chain_id,cancel);second=_observe(app,chain_id,cancel)
            if first!=second or watch.execute('PRAGMA data_version').fetchone()[0]!=version:
                raise ValueError('H1-Belege während Beobachtung verändert.')
        result.update(eligible=True,binding=first,binding_hash=fingerprint(first),
                      reason='H1 aktuell beobachtet. B benötigt eigene Zustimmung und neue Prüfbelege; keine Ausführung.')
    except (ValueError,KeyError,TypeError,OSError):
        result['reason']='H1 oder Vorgängerbelege nicht aktuell und vollständig; Zustimmung gesperrt.'
    _cancel(cancel)
    return result


def _initialize(db):
    db.executescript('''
        CREATE TABLE IF NOT EXISTS dependent_change_successor_consents(
            id TEXT PRIMARY KEY,chain_id TEXT NOT NULL,head_id TEXT NOT NULL,
            seal TEXT NOT NULL,body TEXT NOT NULL,UNIQUE(chain_id,head_id));
        CREATE TRIGGER IF NOT EXISTS successor_consent_no_update BEFORE UPDATE ON dependent_change_successor_consents
            BEGIN SELECT RAISE(ABORT,'Immutable successor consent'); END;
        CREATE TRIGGER IF NOT EXISTS successor_consent_no_delete BEFORE DELETE ON dependent_change_successor_consents
            BEGIN SELECT RAISE(ABORT,'Immutable successor consent'); END;
    ''')


def _decode(row):
    if not row:raise ValueError('Gespeicherte H1-Zustimmung fehlt.')
    value=json.loads(row['body'])
    if (value['id']!=row['id'] or value['binding']['chain_id']!=row['chain_id']
            or value['binding']['predecessor_event_id']!=row['head_id']
            or fingerprint(value)!=row['seal'] or fingerprint(value['binding'])!=value['binding_hash']):
        raise ValueError('H1-Zustimmung verändert.')
    return value


def acknowledge(app,chain_id,binding_hash,note,cancel=None):
    _id(chain_id);_hash(binding_hash);_text(note,2000);_cancel(cancel)
    # Schema only on explicit acknowledgement, before the guarded read window.
    with app.store.db() as db:_initialize(db)
    with _claim(app,'successor_h1',cancel) as (_,commit):
        shown=preview(app,chain_id,cancel)
        if not shown['eligible'] or shown['binding_hash']!=binding_hash:
            raise ValueError('Aktuelle unveränderte H1-Vorschau erforderlich.')
        binding=shown['binding']
        value=dict(id=uuid.uuid4().hex,binding=binding,binding_hash=binding_hash,note=note,
                   actor='operator',created_at=now(),execution_authorized=False,
                   inherited_test_approval=False,kind='dependent_successor_h1_acknowledgement')
        with app.store.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM dependent_change_successor_consents WHERE chain_id=? AND head_id=?',
                           (chain_id,binding['predecessor_event_id'])).fetchone()
            if row:
                value=_decode(row)
                if value['binding_hash']!=binding_hash or value['note']!=note:
                    raise ValueError('H1-Zustimmung bereits anders gebunden.')
            observe_files(binding,binding['files'])
            commit(db)
            if row is None:
                db.execute('INSERT INTO dependent_change_successor_consents VALUES(?,?,?,?,?)',
                           (value['id'],chain_id,binding['predecessor_event_id'],fingerprint(value),json.dumps(value,ensure_ascii=False)))
        return value


def require_current(app,consent_id,cancel=None):
    """Fresh point-in-time proof only; later execution must hold its own claim."""
    _id(consent_id);_cancel(cancel)
    with app.store.db() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='dependent_change_successor_consents'").fetchone():
            raise ValueError('Gespeicherte H1-Zustimmung fehlt.')
        value=_decode(db.execute('SELECT * FROM dependent_change_successor_consents WHERE id=?',(consent_id,)).fetchone())
    shown=preview(app,value['binding']['chain_id'],cancel)
    if not shown['eligible'] or shown['binding_hash']!=value['binding_hash']:
        raise ValueError('H1-Zustimmung nicht mehr aktuell; B bleibt gesperrt.')
    return value
