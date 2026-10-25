"""Small durable SQLite journal. No database access to governed projects."""
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
import threading
import uuid
from .evidence import now


class JobBusy(ValueError): pass


class Store:
    def __init__(self, path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        self.lock=threading.RLock()
        with self.db() as c:
            c.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, action TEXT, project_id TEXT, status TEXT,
                    created_at TEXT, started_at TEXT, ended_at TEXT, error TEXT, result TEXT);
                CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, level TEXT,
                    source TEXT, message TEXT, job_id TEXT);
                CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
                CREATE TABLE IF NOT EXISTS planned(id TEXT PRIMARY KEY,body TEXT);
                CREATE TABLE IF NOT EXISTS decisions(id TEXT PRIMARY KEY,body TEXT);
            ''')
            if 'request' not in [r['name'] for r in c.execute('PRAGMA table_info(jobs)')]:
                c.execute('ALTER TABLE jobs ADD COLUMN request TEXT')
            from .sequence_store import initialize,recover
            initialize(c)
            from .test_chain_store import initialize as chain_initialize, recover as chain_recover
            chain_initialize(c)
            c.execute('BEGIN IMMEDIATE')
            c.execute("UPDATE jobs SET status='interrupted',ended_at=?,error='Dienst beendet; Auftrag nicht automatisch erneut ausgeführt.' WHERE status IN ('queued','running')",(now(),))
            recover(c)
            chain_recover(c)

    @contextmanager
    def db(self):
        with self.lock:
            c=sqlite3.connect(self.path,timeout=10); c.row_factory=sqlite3.Row
            try:
                yield c
                c.commit()
            except BaseException:
                c.rollback(); raise
            finally: c.close()

    def event(self, level, source, message, job_id=None):
        with self.db() as c:
            c.execute('INSERT INTO events(time,level,source,message,job_id) VALUES(?,?,?,?,?)',
                      (now(),level,source,str(message)[:12000],job_id))
            c.execute('DELETE FROM events WHERE id < (SELECT MAX(id)-10000 FROM events)')

    def events(self, limit=150):
        with self.db() as c:
            rows=c.execute('SELECT * FROM events ORDER BY id DESC LIMIT ?',(limit,)).fetchall()
            return [dict(r) for r in reversed(rows)]

    def create_job(self, action, project_id, request=None):
        with self.db() as c:
            from .sequence_store import require_idle
            c.execute('BEGIN IMMEDIATE')
            require_idle(c)
            key=uuid.uuid4().hex
            c.execute('INSERT INTO jobs(id,action,project_id,status,created_at,request) VALUES(?,?,?,?,?,?)',
                      (key,action,project_id,'queued',now(),json.dumps(request or {})))
        return self.job(key)

    def update_job(self, key, **values):
        allowed={'status','started_at','ended_at','error','result'}
        if not values or not set(values)<=allowed: raise ValueError('Ungültiges Job-Update.')
        if 'result' in values: values['result']=json.dumps(values['result'],ensure_ascii=False)
        with self.db() as c:
            c.execute('UPDATE jobs SET '+','.join(k+'=?' for k in values)+' WHERE id=?',(*values.values(),key))

    @staticmethod
    def decode(row):
        result=dict(row)
        if result.get('result'): result['result']=json.loads(result['result'])
        result['request']=json.loads(result.get('request') or '{}')
        return result

    def job(self, key):
        with self.db() as c:
            row=c.execute('SELECT * FROM jobs WHERE id=?',(key,)).fetchone()
            if not row: raise ValueError('Auftrag nicht gefunden.')
            from .model_usage import job_usage
            return dict(self.decode(row), token_usage=job_usage(c, key))

    def jobs(self, limit=40):
        with self.db() as c:
            from .model_usage import job_usage
            return [dict(self.decode(r), token_usage=job_usage(c, r['id'])) for r in c.execute('SELECT * FROM jobs ORDER BY created_at DESC,rowid DESC LIMIT ?',(limit,)).fetchall()]

    def require_latest_stage_test(self, test_id, stage_job_id):
        """A later attempt supersedes success, even when cancelled or interrupted."""
        with self.db() as c:
            row=c.execute("SELECT id FROM jobs WHERE action='stage_test' "
                          "AND json_extract(request,'$.stage_job_id')=? ORDER BY rowid DESC LIMIT 1",
                          (stage_job_id,)).fetchone()
            if row is None or row['id'] != test_id:
                raise ValueError('Ein neuerer Staging-Test liegt vor oder der Nachweis fehlt. Aktuellsten Test prüfen.')

    def jobs_for_action(self,action,limit=100):
        with self.db() as c:
            return [self.decode(r) for r in c.execute('SELECT * FROM jobs WHERE action=? ORDER BY created_at DESC,rowid DESC LIMIT ?',
                                                     (action,limit))]

    def settings(self):
        with self.db() as c: return {r['key']:json.loads(r['value']) for r in c.execute('SELECT * FROM settings')}

    def set_setting(self, key, value):
        with self.db() as c:
            c.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(key,json.dumps(value,ensure_ascii=False)))

    def planned(self):
        with self.db() as c: return [json.loads(r['body']) for r in c.execute('SELECT * FROM planned ORDER BY rowid')]

    def decisions(self):
        with self.db() as c:
            return [json.loads(r['body']) for r in c.execute('SELECT body FROM decisions ORDER BY rowid')]

    def add_decision(self, value):
        item={**value,'id':uuid.uuid4().hex,'created_at':now()}
        with self.db() as c:
            c.execute('INSERT INTO decisions VALUES(?,?)',(item['id'],json.dumps(item,ensure_ascii=False)))
        return item

    def add_project(self,name,description,depends_on,known_ids):
        if not isinstance(name,str) or not 1<=len(name.strip())<=80: raise ValueError('Name: 1 bis 80 Zeichen.')
        if not isinstance(description,str) or len(description)>4000: raise ValueError('Beschreibung zu lang.')
        if not isinstance(depends_on,list) or any(not isinstance(d,str) or d not in known_ids for d in depends_on):
            raise ValueError('Unbekannte Projektabhängigkeit.')
        with self.db() as c:
            if any(p['name'].casefold()==name.strip().casefold() for p in self.planned()):
                raise ValueError('Geplantes Projekt existiert bereits.')
            p=dict(id='planned-'+uuid.uuid4().hex[:12],name=name.strip(),description=description,
                   depends_on=list(dict.fromkeys(depends_on)),kind='planned',status='Geplant',
                   gate='Konzept / keine Implementierungsfreigabe',path=None,created_at=now(),
                   next_step='Anforderungen und Abhängigkeiten präzisieren; Prototyp separat freigeben.')
            c.execute('INSERT INTO planned VALUES(?,?)',(p['id'],json.dumps(p,ensure_ascii=False)))
        self.event('info','governor','Geplantes Modul erfasst: '+p['name'])
        return p
