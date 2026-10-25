"""Internal sequence journal. No HTTP admission, queue dispatch or file/model execution.

The future controller must freshly validate preview and adapter evidence; this
layer guarantees transactional ownership and at-most-once child allocation only.
"""
import json
import re
import uuid

from .evidence import fingerprint, now
from .store import JobBusy

ACTIVE = ('testing', 'assessing')
TERMINAL = ('awaiting_transfer_decision', 'blocked', 'failed', 'cancelled', 'interrupted')


def initialize(c):
    c.executescript('''
        CREATE TABLE IF NOT EXISTS sequence_runs (
            id TEXT PRIMARY KEY, stage_job_id TEXT NOT NULL UNIQUE,
            binding_hash TEXT NOT NULL, binding TEXT NOT NULL, note TEXT NOT NULL,
            created_at TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN
                ('testing','assessing','awaiting_transfer_decision','blocked','failed','cancelled','interrupted')),
            current_job_id TEXT, cancel_requested INTEGER NOT NULL DEFAULT 0 CHECK(cancel_requested IN (0,1)));
        CREATE UNIQUE INDEX IF NOT EXISTS sequence_single_reservation
            ON sequence_runs((1)) WHERE status IN ('testing','assessing');
        CREATE TABLE IF NOT EXISTS sequence_children (
            sequence_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal IN (0,1)),
            job_id TEXT NOT NULL UNIQUE, PRIMARY KEY(sequence_id,ordinal));
        CREATE TABLE IF NOT EXISTS sequence_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sequence_id TEXT NOT NULL,
            time TEXT NOT NULL, kind TEXT NOT NULL, status TEXT NOT NULL, job_id TEXT);
        CREATE TRIGGER IF NOT EXISTS sequence_consent_immutable BEFORE UPDATE OF
            id,stage_job_id,binding_hash,binding,note,created_at ON sequence_runs
            BEGIN SELECT RAISE(ABORT,'Sequence consent is immutable'); END;
        CREATE TRIGGER IF NOT EXISTS sequence_terminal_immutable BEFORE UPDATE ON sequence_runs
            WHEN OLD.status NOT IN ('testing','assessing')
            BEGIN SELECT RAISE(ABORT,'Terminal sequence is immutable'); END;
        CREATE TRIGGER IF NOT EXISTS sequence_no_delete BEFORE DELETE ON sequence_runs
            BEGIN SELECT RAISE(ABORT,'Sequence history is immutable'); END;
        CREATE TRIGGER IF NOT EXISTS sequence_child_no_update BEFORE UPDATE ON sequence_children
            BEGIN SELECT RAISE(ABORT,'Sequence child is immutable'); END;
        CREATE TRIGGER IF NOT EXISTS sequence_child_no_delete BEFORE DELETE ON sequence_children
            BEGIN SELECT RAISE(ABORT,'Sequence child is immutable'); END;
        CREATE TRIGGER IF NOT EXISTS sequence_event_no_update BEFORE UPDATE ON sequence_events
            BEGIN SELECT RAISE(ABORT,'Sequence event is immutable'); END;
        CREATE TRIGGER IF NOT EXISTS sequence_event_no_delete BEFORE DELETE ON sequence_events
            BEGIN SELECT RAISE(ABORT,'Sequence event is immutable'); END;
    ''')


def _event(c, sequence_id, kind, status, job_id):
    c.execute('INSERT INTO sequence_events(sequence_id,time,kind,status,job_id) VALUES(?,?,?,?,?)',
              (sequence_id, now(), kind, status, job_id))


def recover(c):
    """Startup only, inside the same transaction as ordinary job interruption."""
    rows=c.execute("SELECT id,current_job_id FROM sequence_runs WHERE status IN ('testing','assessing')").fetchall()
    for row in rows:
        c.execute("UPDATE sequence_runs SET status='interrupted' WHERE id=?", (row['id'],))
        _event(c,row['id'],'restart','interrupted',row['current_job_id'])


def require_idle(c):
    if (c.execute("SELECT 1 FROM sequence_runs WHERE status IN ('testing','assessing')").fetchone()
            or c.execute("SELECT 1 FROM test_chain_runs WHERE status IN ('testing','checking')").fetchone()
            or c.execute("SELECT 1 FROM jobs WHERE status IN ('queued','running')").fetchone()):
        raise JobBusy('Ausführungsplatz durch Auftrag oder Prüffolge belegt.')


def _id(value):
    if not isinstance(value,str) or not re.fullmatch('[a-f0-9]{32}',value):
        raise ValueError('Ungültige Sequenz- oder Auftragsreferenz.')


def _get(c,key):
    _id(key)
    row=c.execute('SELECT * FROM sequence_runs WHERE id=?',(key,)).fetchone()
    if row is None:raise ValueError('Prüffolge nicht gefunden.')
    return row


def _view(c,key):
    row=dict(_get(c,key));row['binding']=json.loads(row['binding'])
    row['cancel_requested']=bool(row['cancel_requested'])
    row['children']=[dict(r) for r in c.execute('SELECT ordinal,job_id FROM sequence_children WHERE sequence_id=? ORDER BY ordinal',(key,))]
    row['events']=[dict(r) for r in c.execute('SELECT time,kind,status,job_id FROM sequence_events WHERE sequence_id=? ORDER BY id',(key,))]
    return row


def _child(c,row,ordinal,previous=None):
    # Fixed actions and requests only; caller cannot supply a command or child action.
    key=uuid.uuid4().hex
    action='stage_test' if ordinal==0 else 'pilot_assess'
    request={'stage_job_id':row['stage_job_id']} if ordinal==0 else {'verified_test_job_id':previous}
    c.execute('INSERT INTO jobs(id,action,status,created_at,request) VALUES(?,?,?,?,?)',
              (key,action,'queued',now(),json.dumps(request)))
    c.execute('INSERT INTO sequence_children(sequence_id,ordinal,job_id) VALUES(?,?,?)',(row['id'],ordinal,key))
    c.execute('UPDATE sequence_runs SET current_job_id=? WHERE id=?',(key,row['id']))
    return key


class SequenceJournal:
    def __init__(self,store):self.store=store

    def find(self,*,stage_job_id=None,job_id=None):
        with self.store.db() as c:
            if stage_job_id is not None:
                _id(stage_job_id)
                row=c.execute('SELECT id FROM sequence_runs WHERE stage_job_id=?',(stage_job_id,)).fetchone()
            else:
                _id(job_id)
                row=c.execute('SELECT sequence_id AS id FROM sequence_children WHERE job_id=?',(job_id,)).fetchone()
            return _view(c,row['id']) if row else None

    def list(self):
        with self.store.db() as c:
            return [_view(c,r['id']) for r in c.execute('SELECT id FROM sequence_runs ORDER BY rowid DESC LIMIT 40').fetchall()]

    def get(self,key):
        with self.store.db() as c:return _view(c,key)

    def start(self,binding,binding_hash,note):
        """Internal only: caller owns fresh preview/consent checks before dispatch."""
        if (not isinstance(binding,dict) or binding.get('profile_id')!='pilot_test_assess_v1'
                or not isinstance(note,str) or not note.strip() or len(note)>2000
                or any(ord(ch)<32 and ch not in '\n\r\t' for ch in note)):
            raise ValueError('Ungültige Profilbindung oder Begründung.')
        try:encoded=json.dumps(binding,ensure_ascii=False,sort_keys=True,allow_nan=False)
        except (ValueError,TypeError,RecursionError) as exc:raise ValueError('Ungültige Bindung.') from exc
        if len(encoded.encode('utf-8'))>65536 or binding_hash!=fingerprint(binding):
            raise ValueError('Bindung stimmt nicht mit dem bestätigten Hash überein.')
        source_id=binding.get('stage_job_id');_id(source_id)
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            existing=c.execute('SELECT * FROM sequence_runs WHERE stage_job_id=?',(source_id,)).fetchone()
            if existing:
                if existing['binding_hash']!=binding_hash or existing['binding']!=encoded or existing['note']!=note:
                    raise ValueError('Vorschlag bereits mit anderer Bindung oder Zustimmung verwendet.')
                return _view(c,existing['id'])
            require_idle(c)
            source=c.execute('SELECT * FROM jobs WHERE id=?',(source_id,)).fetchone()
            if source is None or source['action']!='scope_patch' or source['status']!='completed':
                raise ValueError('Abgeschlossener Vorschlag erforderlich.')
            result=json.loads(source['result'] or '{}');stage=result.get('stage') or {}
            req=json.loads(source['request'] or '{}')
            if (stage.get('id')!=binding.get('stage_id') or stage.get('manifest_hash')!=binding.get('manifest_hash')
                    or any(req.get(k)!=binding.get(k) for k in ('candidate_id','step_id','scope_hash'))
                    or not all(binding.get(k) for k in ('stage_id','manifest_hash','candidate_id','step_id','scope_hash','selection_id'))):
                raise ValueError('Vorschlagsbindung passt nicht zum gespeicherten Auftrag.')
            latest=c.execute("SELECT id FROM jobs WHERE action='stage_test' AND json_extract(request,'$.stage_job_id')=? ORDER BY rowid DESC LIMIT 1",(source_id,)).fetchone()
            if (latest['id'] if latest else None)!=binding.get('latest_stage_test_id'):
                raise ValueError('Neuerer Staging-Test seit Vorschau.')
            key=uuid.uuid4().hex
            c.execute('INSERT INTO sequence_runs(id,stage_job_id,binding_hash,binding,note,created_at,status) VALUES(?,?,?,?,?,?,?)',
                      (key,source_id,binding_hash,encoded,note,now(),'testing'))
            child=_child(c,_get(c,key),0)
            _event(c,key,'consent','testing',child)
            return _view(c,key)

    def begin_child(self,key,job_id):
        _id(job_id)
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE');row=_get(c,key)
            if row['status'] not in ACTIVE or row['cancel_requested'] or row['current_job_id']!=job_id:
                raise ValueError('Kindauftrag nicht mehr freigegeben.')
            child=c.execute('SELECT ordinal FROM sequence_children WHERE sequence_id=? AND job_id=?',(key,job_id)).fetchone()
            if child is None or child['ordinal']!=(0 if row['status']=='testing' else 1):
                raise ValueError('Ungültige Kindposition.')
            if c.execute("UPDATE jobs SET status='running',started_at=? WHERE id=? AND status='queued'",(now(),job_id)).rowcount!=1:
                raise ValueError('Kindauftrag wurde bereits gestartet oder beendet.')
            _event(c,key,'started',row['status'],job_id)
            return self.store.decode(c.execute('SELECT * FROM jobs WHERE id=?',(job_id,)).fetchone())

    def finish_child(self,key,job_id,status,result,*,evidence_current=False):
        """Atomically save child outcome and reserve next; freshness is controller-owned."""
        if status not in ('completed','failed','cancelled') or not isinstance(result,dict) or type(evidence_current) is not bool:
            raise ValueError('Ungültiger Kindabschluss.')
        encoded=json.dumps(result,ensure_ascii=False,allow_nan=False)
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE');row=_get(c,key)
            job=c.execute('SELECT * FROM jobs WHERE id=?',(job_id,)).fetchone()
            if row['status'] not in ACTIVE or row['current_job_id']!=job_id or job is None or job['status']!='running':
                raise ValueError('Kein passender laufender Kindauftrag.')
            if row['cancel_requested']:status='cancelled'
            positive=result.get('success') is True
            if row['status']=='testing':positive=positive and result.get('verified') is True and not result.get('stale')
            else:positive=positive and isinstance(result.get('pilot_assessment'),dict) and result['pilot_assessment'].get('evidence_usable') is True
            if status!='completed':end=status
            elif not evidence_current or not positive:end='blocked'
            else:end='assessing' if row['status']=='testing' else 'awaiting_transfer_decision'
            c.execute('UPDATE jobs SET status=?,ended_at=?,result=? WHERE id=?',(status,now(),encoded,job_id))
            c.execute('UPDATE sequence_runs SET status=? WHERE id=?',(end,key))
            if end=='assessing':_child(c,_get(c,key),1,job_id)
            _event(c,key,'child_finished',end,job_id)
            return _view(c,key)

    def cancel(self,key):
        """Record intent. Running owners retain the reservation until acknowledged."""
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE');row=_get(c,key)
            if row['status'] in TERMINAL or row['cancel_requested']:return _view(c,key)
            job=c.execute('SELECT status FROM jobs WHERE id=?',(row['current_job_id'],)).fetchone()
            end=row['status'] if job and job['status']=='running' else 'cancelled'
            c.execute('UPDATE sequence_runs SET cancel_requested=1,status=? WHERE id=?',(end,key))
            c.execute("UPDATE jobs SET status='cancelled',ended_at=? WHERE id=? AND status='queued'",(now(),row['current_job_id']))
            _event(c,key,'cancel_requested',end,row['current_job_id'])
            return _view(c,key)
