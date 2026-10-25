"""Append-only operator assessment of project intake; never a product gate approval."""
import json
import uuid
from .evidence import now


class Intake:
    FIELDS={'requirements','test_strategy','dependencies','open_evidence'}

    def __init__(self,store):
        self.store=store
        with store.db() as c:
            c.execute('CREATE TABLE IF NOT EXISTS reg_intake(id TEXT PRIMARY KEY,project_id TEXT,source_hash TEXT,body TEXT,created_at TEXT)')

    def accepted(self,project_id,source_hash):
        with self.store.db() as c:
            row=c.execute('SELECT source_hash FROM reg_intake WHERE project_id=? ORDER BY rowid DESC LIMIT 1',(project_id,)).fetchone()
            return bool(row and row['source_hash']==source_hash)

    def records(self,project_ids):
        with self.store.db() as c:
            result=[]
            for key in project_ids:
                row=c.execute('SELECT * FROM reg_intake WHERE project_id=? ORDER BY rowid DESC LIMIT 1',(key,)).fetchone()
                if row: result.append({**dict(row),'body':json.loads(row['body'])})
            return result

    def accept(self,context,expected_scope_hash,project_id,fields):
        if context['scope_hash']!=expected_scope_hash: raise ValueError('Aufnahmekontext geändert; erneut prüfen.')
        if not isinstance(fields,dict) or set(fields)!=self.FIELDS:
            raise ValueError('Ziel/Anforderungen, Teststrategie, Abhängigkeiten und offene Nachweise sind erforderlich.')
        if any(not isinstance(v,str) or not v.strip() or len(v)>4000 for v in fields.values()):
            raise ValueError('Aufnahmefelder benötigen 1 bis 4000 Zeichen.')
        row=next((p for p in context['projects'] if p['id']==project_id),None)
        intake=next((p for p in context['intake'] if p['project_id']==project_id),None)
        if not row or not intake or not intake['evidence_complete'] or not intake['memories_present']:
            raise ValueError('Aktuelle vollständige Erfassung und Projektgedächtnis erforderlich.')
        item={'id':uuid.uuid4().hex,'project_id':project_id,'source_hash':row['evidence_hash'],
              'body':fields,'created_at':now()}
        with self.store.db() as c:
            c.execute('INSERT INTO reg_intake VALUES(?,?,?,?,?)',
                      (item['id'],project_id,item['source_hash'],json.dumps(fields,ensure_ascii=False),item['created_at']))
        return item
