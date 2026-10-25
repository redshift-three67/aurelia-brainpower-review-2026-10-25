"""Internal S3b evidence ledger. No API, dispatch, file writes or execution grant.

S3c must supply freshly verified trusted snapshots and authenticated decisions,
hold the shared worker reservation, and enforce tip order before physical writes.
Hash chains detect inconsistency, not a hostile owner rewriting the whole DB.
"""
import copy
import json
import uuid

from . import change_journal_evidence as evidence_rules
from .evidence import fingerprint, now
from .execution_workspace import _root, _read, _sha, MAX_TOTAL_BYTES
from .plans import _hash, _id, _text


def _initialize(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS dependent_change_chains(
      id TEXT PRIMARY KEY,candidate_id TEXT NOT NULL UNIQUE,seal TEXT NOT NULL,body TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS dependent_change_events(
      id TEXT PRIMARY KEY,chain_id TEXT NOT NULL,ordinal INTEGER NOT NULL CHECK(ordinal BETWEEN 0 AND 3),
      request_hash TEXT NOT NULL UNIQUE,seal TEXT NOT NULL,body TEXT NOT NULL,UNIQUE(chain_id,ordinal));
    CREATE TRIGGER IF NOT EXISTS dependent_change_chains_no_update BEFORE UPDATE ON dependent_change_chains
      BEGIN SELECT RAISE(ABORT,'Immutable change baseline'); END;
    CREATE TRIGGER IF NOT EXISTS dependent_change_chains_no_delete BEFORE DELETE ON dependent_change_chains
      BEGIN SELECT RAISE(ABORT,'Immutable change baseline'); END;
    CREATE TRIGGER IF NOT EXISTS dependent_change_events_no_update BEFORE UPDATE ON dependent_change_events
      BEGIN SELECT RAISE(ABORT,'Immutable change event'); END;
    CREATE TRIGGER IF NOT EXISTS dependent_change_events_no_delete BEFORE DELETE ON dependent_change_events
      BEGIN SELECT RAISE(ABORT,'Immutable change event'); END;
    ''')


def _observe(binding,files):
    root,identity=_root(binding['root'])
    if identity!=binding['root_identity']:raise ValueError('Pilotwurzel hat sich geändert.')
    total=0
    for path,expected in files.items():
        raw=_read(root,path);total+=len(raw) if raw is not None else 0
        if total>MAX_TOTAL_BYTES or (_sha(raw) if raw is not None else None)!=expected:
            raise ValueError('Aktueller Dateistand weicht von Journalspitze ab.')
    if _root(binding['root'])[1]!=identity:raise ValueError('Wurzel während Beobachtung geändert.')


def _reconstruct(chain,events):
    binding=evidence_rules.baseline(chain['binding']);files=dict(binding['sources']);scope=binding['scope_hash']
    active=[];states=[dict(scope_hash=scope,files=dict(files))];head=None;previous=fingerprint(chain)
    rolled_back=False;transitions=0;seen_transactions=set();seen_receipts=set()
    for index,event in enumerate(events):
        if (index>=4 or event['ordinal']!=index or event['chain_id']!=chain['id']
                or event['previous_id']!=head or event['previous_hash']!=previous):
            raise ValueError('Journalvorgänger oder Reihenfolge stimmt nicht überein.')
        _id(event['id']);_text(event['note'],2000)
        if event['kind']=='transition':
            if rolled_back:raise ValueError('Rücknahme erfordert neue Planrevision.')
            proof=event['evidence'];tx=proof['transaction']['id'];receipt=proof['technical_receipt']['id']
            if tx in seen_transactions or receipt in seen_receipts:raise ValueError('Beleg wurde mehrfach verwendet.')
            before=dict(files);old_scope=scope
            files,scope=evidence_rules.transition(binding,files,scope,transitions,proof)
            seen_transactions.add(tx);seen_receipts.add(receipt);transitions+=1
            active.append(dict(event=event,files=before,scope=old_scope))
        elif event['kind']=='rollback':
            if not active or event['target_id']!=active[-1]['event']['id']:
                raise ValueError('Nur jüngster aktiver Übergang darf zurückgenommen werden.')
            tip=active.pop()
            evidence_rules.rollback_transaction(tip['event']['evidence']['transaction'],event['evidence'])
            files=dict(tip['files']);scope=tip['scope'];rolled_back=True
        else:raise ValueError('Unbekanntes Journalereignis.')
        states.append(dict(scope_hash=scope,files=dict(files)))
        head=event['id'];previous=fingerprint(event)
    return dict(files=files,scope_hash=scope,states=states,head_id=head,head_hash=previous,
        active_transition_ids=[a['event']['id'] for a in active],requires_new_plan=rolled_back,
        transition_count=transitions)


def _load(db,key):
    _id(key)
    row=db.execute('SELECT * FROM dependent_change_chains WHERE id=?',(key,)).fetchone()
    if not row:raise ValueError('Änderungsjournal nicht gefunden.')
    chain=json.loads(row['body'])
    if chain['id']!=row['id'] or chain['binding']['candidate_id']!=row['candidate_id'] or fingerprint(chain)!=row['seal']:
        raise ValueError('Journalbasis verändert.')
    events=[]
    for row in db.execute('SELECT * FROM dependent_change_events WHERE chain_id=? ORDER BY ordinal LIMIT 5',(key,)):
        event=json.loads(row['body'])
        if (event['id']!=row['id'] or event['chain_id']!=row['chain_id'] or event['ordinal']!=row['ordinal']
                or event['request_hash']!=row['request_hash'] or fingerprint(event)!=row['seal']):
            raise ValueError('Journalereignis verändert.')
        events.append(event)
    return chain,events,_reconstruct(chain,events)


class ChangeJournal:
    def __init__(self,store):
        self.store=store
        with store.db() as db:_initialize(db)

    def create(self,binding,note,*,controller_binding=None,before_commit=None):
        binding=evidence_rules.baseline(binding);_text(note,2000)
        with self.store.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT id FROM dependent_change_chains WHERE candidate_id=?',(binding['candidate_id'],)).fetchone()
            if row:
                chain,_,_=_load(db,row['id'])
                if chain['binding']==binding and chain['note']==note and chain.get('controller_binding')==controller_binding:
                    if before_commit:before_commit(db)
                    return chain
                raise ValueError('Diese Planrevision besitzt bereits eine andere Journalbindung.')
            from .change_rollback import require_no_physical_claim
            require_no_physical_claim(db)
            _observe(binding,binding['sources']);_observe(binding,binding['sources'])
            chain=dict(id=uuid.uuid4().hex,version=1,binding=binding,note=note,created_at=now(),execution_authorized=False)
            if controller_binding is not None:chain['controller_binding']=copy.deepcopy(controller_binding)
            if before_commit:before_commit(db)
            db.execute('INSERT INTO dependent_change_chains VALUES(?,?,?,?)',
                (chain['id'],binding['candidate_id'],fingerprint(chain),json.dumps(chain,ensure_ascii=False)))
            return chain

    def read(self,key):
        with self.store.db() as db:
            db.execute('BEGIN')
            chain,events,state=_load(db,key)
        return dict(chain=chain,events=events,**state)

    def transition(self,key,expected_head,evidence,note,*,before_commit=None):
        return self._append(key,expected_head,'transition',None,evidence,note,before_commit=before_commit)

    def rollback(self,key,expected_head,target_id,evidence,note):
        _id(target_id)
        return self._append(key,expected_head,'rollback',target_id,evidence,note)

    def _append(self,key,expected_head,kind,target_id,evidence,note,*,before_commit=None):
        _id(key);_text(note,2000)
        if expected_head is not None:_id(expected_head)
        request=dict(chain_id=key,previous_id=expected_head,kind=kind,target_id=target_id,evidence=copy.deepcopy(evidence),note=note)
        request_hash=fingerprint(request)
        with self.store.db() as db:
            db.execute('BEGIN IMMEDIATE')
            chain,events,state=_load(db,key)
            # Exact retries return historical evidence, never current authority or replay.
            for event in events:
                if event['request_hash']==request_hash:
                    if before_commit:before_commit(db)
                    return event
            from .change_rollback import require_no_physical_claim
            require_no_physical_claim(db)
            if state['head_id']!=expected_head:raise ValueError('Journalspitze seit Freigabe geändert.')
            event=dict(request,id=uuid.uuid4().hex,ordinal=len(events),previous_hash=state['head_hash'],
                request_hash=request_hash,created_at=now(),execution_authorized=False)
            try:
                updated=_reconstruct(chain,events+[event])
                _observe(chain['binding'],updated['files']);_observe(chain['binding'],updated['files'])
            except (KeyError,TypeError) as exc:
                raise ValueError('Unvollständiger Journalbeleg.') from exc
            if before_commit:before_commit(db)
            db.execute('INSERT INTO dependent_change_events VALUES(?,?,?,?,?,?)',
                (event['id'],key,event['ordinal'],request_hash,fingerprint(event),json.dumps(event,ensure_ascii=False)))
            return event

    def inspect(self,key,observed_scope_hash,current_adapter_hash):
        result=dict(history_valid=False,tip_current=False,execution_authorized=False,requires_new_plan=True)
        try:
            value=self.read(key);result.update({k:v for k,v in value.items() if k not in ('chain','events')},history_valid=True)
            _hash(observed_scope_hash);_hash(current_adapter_hash)
            binding=value['chain']['binding']
            if observed_scope_hash!=value['scope_hash'] or current_adapter_hash!=binding['adapter_hash']:
                raise ValueError('Aktueller Kontext oder Adapter stimmt nicht mit der Journalspitze überein.')
            _observe(binding,value['files']);_observe(binding,value['files'])
            latest=self.read(key)
            if latest['head_hash']!=value['head_hash'] or latest['chain']!=value['chain']:
                raise ValueError('Journalspitze während Beobachtung geändert.')
            result.update(tip_current=True,reason='Historie konsistent; expliziter Dateiumfang aktuell beobachtet. Keine Ausführungsfreigabe.')
        except (ValueError,KeyError,TypeError,OSError):
            result['reason']='Historie oder aktueller Stand nicht vollständig belegbar. Keine Ausführungsfreigabe.'
        return result
