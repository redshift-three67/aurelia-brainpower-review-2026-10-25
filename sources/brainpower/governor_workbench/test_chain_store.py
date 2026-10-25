"""Transactional test-chain ownership; freshness remains controller-owned."""
import json
import uuid
from .evidence import fingerprint, now
from .plans import _id, _text
from .plan_tests import attempt_policy, successful
from .sequence_store import require_idle

ACTIVE=('testing','checking')


def initialize(c):
    c.executescript('''
    CREATE TABLE IF NOT EXISTS test_chain_runs(
      id TEXT PRIMARY KEY, activation TEXT NOT NULL UNIQUE, binding_hash TEXT NOT NULL,
      binding TEXT NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN ('testing','checking','completed','blocked','failed','cancelled','interrupted')),
      current_job_id TEXT, cancel_requested INTEGER NOT NULL DEFAULT 0 CHECK(cancel_requested IN (0,1)));
    CREATE UNIQUE INDEX IF NOT EXISTS test_chain_single ON test_chain_runs((1)) WHERE status IN ('testing','checking');
    CREATE TABLE IF NOT EXISTS test_chain_children(chain_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal BETWEEN 0 AND 4),
      step_id TEXT NOT NULL, job_id TEXT NOT NULL UNIQUE, PRIMARY KEY(chain_id,ordinal));
    CREATE TABLE IF NOT EXISTS test_chain_events(id INTEGER PRIMARY KEY AUTOINCREMENT,chain_id TEXT NOT NULL,
      time TEXT NOT NULL,kind TEXT NOT NULL,status TEXT NOT NULL,job_id TEXT);
    CREATE TRIGGER IF NOT EXISTS test_chain_consent BEFORE UPDATE OF id,activation,binding_hash,binding,note,created_at ON test_chain_runs
      BEGIN SELECT RAISE(ABORT,'Immutable consent'); END;
    CREATE TRIGGER IF NOT EXISTS test_chain_terminal BEFORE UPDATE ON test_chain_runs WHEN OLD.status NOT IN ('testing','checking')
      BEGIN SELECT RAISE(ABORT,'Immutable terminal chain'); END;
    CREATE TRIGGER IF NOT EXISTS test_chain_no_delete BEFORE DELETE ON test_chain_runs BEGIN SELECT RAISE(ABORT,'Immutable chain'); END;
    CREATE TRIGGER IF NOT EXISTS test_chain_child_update BEFORE UPDATE ON test_chain_children BEGIN SELECT RAISE(ABORT,'Immutable child'); END;
    CREATE TRIGGER IF NOT EXISTS test_chain_child_delete BEFORE DELETE ON test_chain_children BEGIN SELECT RAISE(ABORT,'Immutable child'); END;
    CREATE TRIGGER IF NOT EXISTS test_chain_event_update BEFORE UPDATE ON test_chain_events BEGIN SELECT RAISE(ABORT,'Immutable event'); END;
    CREATE TRIGGER IF NOT EXISTS test_chain_event_delete BEFORE DELETE ON test_chain_events BEGIN SELECT RAISE(ABORT,'Immutable event'); END;
    ''')


def _event(c,key,kind,status,job):
    c.execute('INSERT INTO test_chain_events(chain_id,time,kind,status,job_id) VALUES(?,?,?,?,?)',(key,now(),kind,status,job))


def recover(c):
    for row in c.execute("SELECT id,current_job_id FROM test_chain_runs WHERE status IN ('testing','checking')").fetchall():
        c.execute("UPDATE test_chain_runs SET status='interrupted' WHERE id=?",(row['id'],))
        _event(c,row['id'],'restart','interrupted',row['current_job_id'])


def _view(c,key):
    _id(key)
    row=c.execute('SELECT * FROM test_chain_runs WHERE id=?',(key,)).fetchone()
    if not row:raise ValueError('Testkette nicht gefunden.')
    value=dict(row);value['binding']=json.loads(value['binding']);value['cancel_requested']=bool(value['cancel_requested'])
    value['children']=[dict(r) for r in c.execute('SELECT ordinal,step_id,job_id FROM test_chain_children WHERE chain_id=? ORDER BY ordinal',(key,))]
    value['events']=[dict(r) for r in c.execute('SELECT time,kind,status,job_id FROM test_chain_events WHERE chain_id=? ORDER BY id',(key,))]
    return value


def _attempt(c,binding,step):
    p=attempt_policy(c,binding['candidate_id'],step)
    h=p['history']
    return p,dict(used=p['used'],remaining=p['remaining'],limit=p['limit'],latest=dict(id=h[0]['id'],status=h[0]['status']) if h else None)


def _child(c,row):
    binding=row['binding'];ordinal=len(row['children']);step=binding['step_ids'][ordinal]
    policy,observed=_attempt(c,binding,step)
    if not policy['allowed'] or observed!=binding['attempts'][step]:raise ValueError('Versuchslage verändert.')
    key=uuid.uuid4().hex
    request=dict(candidate_id=binding['candidate_id'],step_id=step,scope_hash=binding['scope_hash'],selection_id=binding['selection_id'])
    c.execute('INSERT INTO jobs(id,action,status,created_at,request) VALUES(?,?,?,?,?)',(key,'plan_test','queued',now(),json.dumps(request)))
    c.execute('INSERT INTO test_chain_children VALUES(?,?,?,?)',(row['id'],ordinal,step,key))
    c.execute("UPDATE test_chain_runs SET current_job_id=?,status='testing' WHERE id=?",(key,row['id']))
    return key


class TestChainJournal:
    def __init__(self,store):self.store=store

    def get(self,key):
        with self.store.db() as c:return _view(c,key)

    def list(self):
        with self.store.db() as c:return [_view(c,r['id']) for r in c.execute('SELECT id FROM test_chain_runs ORDER BY rowid DESC LIMIT 40').fetchall()]

    def find(self,job_id):
        with self.store.db() as c:
            r=c.execute('SELECT chain_id FROM test_chain_children WHERE job_id=?',(job_id,)).fetchone()
            return _view(c,r['chain_id']) if r else None

    def start(self,binding,binding_hash,note):
        _text(note,2000)
        if binding.get('profile_id')!='plan_test_chain_v1' or fingerprint(binding)!=binding_hash:raise ValueError('Ungültige Bindung.')
        ids=binding.get('step_ids')
        if not isinstance(ids,list) or not 2<=len(ids)<=5 or len(set(ids))!=len(ids):raise ValueError('Ungültige Testliste.')
        for step in ids:_id(step)
        encoded=json.dumps(binding,ensure_ascii=False,sort_keys=True,allow_nan=False)
        if len(encoded.encode('utf-8'))>262144:raise ValueError('Bindung zu groß.')
        activation=fingerprint([binding['candidate_id'],binding['selection_id'],ids])
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            existing=c.execute('SELECT * FROM test_chain_runs WHERE activation=?',(activation,)).fetchone()
            if existing:
                if existing['binding']!=encoded or existing['binding_hash']!=binding_hash or existing['note']!=note:raise ValueError('Aktivierung bereits anders bestätigt.')
                return _view(c,existing['id'])
            require_idle(c)
            selection=c.execute('SELECT id FROM plan_approvals WHERE candidate_id=? ORDER BY rowid DESC LIMIT 1',(binding['candidate_id'],)).fetchone()
            if not selection or selection['id']!=binding['selection_id']:raise ValueError('Auswahl verändert.')
            for step in ids:
                policy,observed=_attempt(c,binding,step)
                if not policy['allowed'] or observed!=binding['attempts'][step]:raise ValueError('Versuchslage verändert.')
            key=uuid.uuid4().hex
            c.execute('INSERT INTO test_chain_runs(id,activation,binding_hash,binding,note,created_at,status) VALUES(?,?,?,?,?,?,?)',
                      (key,activation,binding_hash,encoded,note,now(),'testing'))
            child=_child(c,_view(c,key));_event(c,key,'consent','testing',child)
            return _view(c,key)

    def begin_child(self,key,job_id):
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE');row=_view(c,key)
            if row['status']!='testing' or row['cancel_requested'] or row['current_job_id']!=job_id:raise ValueError('Kind nicht freigegeben.')
            if c.execute("UPDATE jobs SET status='running',started_at=? WHERE id=? AND status='queued'",(now(),job_id)).rowcount!=1:raise ValueError('Kind bereits gestartet.')
            _event(c,key,'started','testing',job_id)

    def finish_child(self,key,job_id,status,result,*,evidence_current=False):
        if status not in ('completed','failed','cancelled') or not isinstance(result,dict):raise ValueError('Ungültiger Abschluss.')
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE');row=_view(c,key)
            job=c.execute('SELECT status FROM jobs WHERE id=?',(job_id,)).fetchone()
            if row['status']!='testing' or row['current_job_id']!=job_id or not job or job['status']!='running':raise ValueError('Kein laufendes Kind.')
            if row['cancel_requested']:status='cancelled'
            positive=result.get('success') is True and successful((result.get('test_evidence') or {}).get('test') or {}) and bool(result.get('completion_receipt'))
            end=status if status!='completed' else ('checking' if evidence_current and positive else 'blocked')
            c.execute('UPDATE jobs SET status=?,ended_at=?,result=? WHERE id=?',(status,now(),json.dumps(result,ensure_ascii=False),job_id))
            c.execute('UPDATE test_chain_runs SET status=? WHERE id=?',(end,key))
            _event(c,key,'child_finished',end,job_id)
            return _view(c,key)

    def advance(self,key,*,evidence_current=False):
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE');row=_view(c,key)
            if row['status'] not in ACTIVE:return row
            if row['status']!='checking':raise ValueError('Belegprüfung noch nicht möglich.')
            end='cancelled' if row['cancel_requested'] else 'blocked'
            if evidence_current and not row['cancel_requested']:
                if len(row['children'])==len(row['binding']['step_ids']):end='completed'
                else:
                    try:_child(c,row);end='testing'
                    except ValueError:end='blocked'
            c.execute('UPDATE test_chain_runs SET status=? WHERE id=?',(end,key))
            _event(c,key,'evidence_checked',end,row['current_job_id'])
            return _view(c,key)

    def cancel(self,key):
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE');row=_view(c,key)
            if row['status'] not in ACTIVE or row['cancel_requested']:return row
            job=c.execute('SELECT status FROM jobs WHERE id=?',(row['current_job_id'],)).fetchone()
            end=row['status'] if job and job['status']=='running' else 'cancelled'
            c.execute('UPDATE test_chain_runs SET cancel_requested=1,status=? WHERE id=?',(end,key))
            c.execute("UPDATE jobs SET status='cancelled',ended_at=? WHERE id=? AND status='queued'",(now(),row['current_job_id']))
            _event(c,key,'cancel_requested',end,row['current_job_id'])
            return _view(c,key)
