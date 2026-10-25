"""Local, source-bound suggestions. Saving a draft never accepts project intake."""
import copy
import json
import uuid
from .evidence import now
from .intake import Intake
from .plans import _scope


class IntakeDrafts:
    def __init__(self,store):
        self.store=store
        with store.db() as c:
            c.execute('CREATE TABLE IF NOT EXISTS intake_drafts(id TEXT PRIMARY KEY,scope_kind TEXT,scope_id TEXT,project_id TEXT,body TEXT)')
            for op in ('UPDATE','DELETE'):
                c.execute(f"CREATE TRIGGER IF NOT EXISTS intake_drafts_no_{op.lower()} BEFORE {op} ON intake_drafts BEGIN SELECT RAISE(ABORT,'Intake draft history is immutable'); END")

    def save(self,context,expected_scope_hash,project_id,fields,sources):
        kind,key=context['review_scope']['kind'],context['review_scope']['id']
        _scope(kind,key)
        if expected_scope_hash!=context['scope_hash']:
            raise ValueError('Aufnahmekontext geändert; Entwurf neu prüfen.')
        row=next((p for p in context['projects'] if p['id']==project_id),None)
        if row is None: raise ValueError('Projekt gehört nicht zum gelesenen Umfang.')
        if (not isinstance(fields,dict) or set(fields)!=Intake.FIELDS or
                any(not isinstance(v,str) or not v.strip() or len(v)>4000 for v in fields.values())):
            raise ValueError('Vier vollständige Aufnahmefelder mit höchstens 4000 Zeichen erforderlich.')
        # Shared contract memories may be cited only when their project is
        # actually included in this selected group context.
        memories=[m for p in context['projects'] for m in p.get('memories',[])]
        known={(s['name'],s['sha256']) for s in memories+context.get('governance_sources',[]) if s.get('sha256')}
        if not isinstance(sources,list) or not 1<=len(sources)<=106:
            raise ValueError('Hashgebundene Quellen erforderlich.')
        for source in sources:
            if (not isinstance(source,dict) or set(source)!={'name','sha256'} or
                    not isinstance(source['name'],str) or not isinstance(source['sha256'],str) or
                    (source['name'],source['sha256']) not in known):
                raise ValueError('Entwurfsquelle ist nicht im aktuellen Projektumfang nachgewiesen.')
        record=dict(id=uuid.uuid4().hex,scope_kind=kind,scope_id=key,project_id=project_id,
                    scope_hash=context['scope_hash'],source_hash=row['evidence_hash'],
                    source_scope_hash=context.get('intake_source_hash',context['scope_hash']),
                    fields=copy.deepcopy(fields),sources=copy.deepcopy(sources),created_at=now(),
                    status='draft',approval_granted=False)
        with self.store.db() as c:
            c.execute('INSERT INTO intake_drafts VALUES(?,?,?,?,?)',
                      (record['id'],kind,key,project_id,json.dumps(record,ensure_ascii=False)))
        return record

    def list(self,context):
        kind,key=context['review_scope']['kind'],context['review_scope']['id']
        _scope(kind,key)
        with self.store.db() as c:
            result=[]
            for project in context['projects']:
                row=c.execute('SELECT body FROM intake_drafts WHERE scope_kind=? AND scope_id=? AND project_id=? ORDER BY rowid DESC LIMIT 1',
                              (kind,key,project['id'])).fetchone()
                if row:
                    item=json.loads(row['body'])
                    item['current']=(item['source_hash']==project['evidence_hash'] and
                        item['source_scope_hash']==context.get('intake_source_hash',context['scope_hash']))
                    result.append(item)
            return result
