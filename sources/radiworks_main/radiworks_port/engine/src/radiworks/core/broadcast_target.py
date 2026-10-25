"""BC1: frozen target metadata and durable acceptance, never automatic replay."""
from __future__ import annotations
import copy
import json
import re
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from .personal_context import ContextSnapshot, ContextError
from ..scope import ScopeContext
from .broadcast_policy import ExecutionPolicy, PolicyError
from .presentation_profile import PresentationProfileError, validate_presentation_receipt
from ..persistence import atomic_json_replace, document_digest

HEX32=re.compile(r'[0-9a-f]{32}\Z')
HEX64=re.compile(r'[0-9a-f]{64}\Z')
PROCEDURES=('original-aetherone-v1','radi144-personal-v1')

class BroadcastTargetError(ValueError):
    pass

def _source(value):
    if type(value) is not dict or value.get('kind') not in ('direct','image','auto','promote'):
        raise BroadcastTargetError('Broadcastquelle ist ungültig.')
    kind=value['kind']
    allowed={'kind'} | ({'sessionId','draftId','personalJobId','personalInputIndex'} if kind=='direct' else {'sessionId','draftId'} if kind=='promote' else {'generationId'} if kind=='auto' else {'imageHash'})
    required={'kind'} | ({'draftId'} if kind=='promote' else {'generationId'} if kind=='auto' else {'imageHash'} if kind=='image' else set())
    if not required<=set(value):raise BroadcastTargetError('Broadcastquelle ist unvollständig.')
    if set(value)-allowed:raise BroadcastTargetError('Broadcastquelle enthält unbekannte Felder.')
    for key in ('sessionId','generationId','personalJobId'):
        if key in value and (type(value[key]) is not str or not HEX32.fullmatch(value[key])):
            raise BroadcastTargetError('Quell-ID ist ungültig.')
    if 'personalInputIndex' in value and ('personalJobId' not in value or type(value['personalInputIndex']) is not int or not 0 <= value['personalInputIndex'] < 4096):
        raise BroadcastTargetError('Persönlicher Ergebnisindex ist ungültig.')
    if 'personalJobId' in value and 'personalInputIndex' not in value:
        raise BroadcastTargetError('Persönlicher Ergebnisindex fehlt.')
    if 'draftId' in value:
        try:
            if str(uuid.UUID(value['draftId']))!=value['draftId']:raise ValueError()
        except (ValueError,TypeError,AttributeError) as exc:raise BroadcastTargetError('Draft-ID ist ungültig.') from exc
    if 'imageHash' in value and (type(value['imageHash']) is not str or not re.fullmatch(r'[0-9a-f]{32}|[0-9a-f]{64}',value['imageHash'])):
        raise BroadcastTargetError('Bildreferenz ist ungültig.')
    return copy.deepcopy(value)

@dataclass(frozen=True,slots=True)
class BroadcastTarget:
    _serialized:str

    @classmethod
    def capture(cls,*,scope:ScopeContext,source:dict,snapshot:dict|None=None,legacy=False,procedure='original-aetherone-v1',entropy_mode='seeded'):
        body={'schemaVersion':1,'jobId':uuid.uuid4().hex,'scope':scope.to_dict(),
              'source':_source(source),'binding':'bound' if snapshot is not None else 'legacy-unbound' if legacy else 'no-case',
              'contextSnapshot':copy.deepcopy(snapshot),'procedure':procedure,'entropyMode':entropy_mode}
        body['digest']=document_digest(body)
        return cls.from_payload(body)

    @classmethod
    def from_payload(cls,value):
        keys={'schemaVersion','jobId','scope','source','binding','contextSnapshot','procedure','entropyMode','digest'}
        if type(value) is not dict or set(value)!=keys or type(value['schemaVersion']) is not int or value['schemaVersion']!=1:
            raise BroadcastTargetError('Broadcastziel hat ein ungültiges Schema.')
        if type(value['jobId']) is not str or not HEX32.fullmatch(value['jobId']):raise BroadcastTargetError('Auftrags-ID ist ungültig.')
        try:
            scope=ScopeContext(**value['scope'])
        except (TypeError,ValueError) as exc:raise BroadcastTargetError('Auftrags-Scope ist ungültig.') from exc
        _source(value['source'])
        if value['binding'] not in ('bound','no-case','legacy-unbound'):raise BroadcastTargetError('Fallbindung ist ungültig.')
        if value['procedure'] not in PROCEDURES or value['entropyMode'] not in ('seeded','stochastic'):
            raise BroadcastTargetError('Verfahren oder Zufallsmodus ist ungültig.')
        if value['binding']=='bound':
            try:snapshot=ContextSnapshot.from_payload(value['contextSnapshot']).payload()
            except (ContextError,TypeError,ValueError) as exc:raise BroadcastTargetError('Fester Fallkontext ist ungültig.') from exc
            if snapshot['scope']!=scope.to_dict():raise BroadcastTargetError('Fallkontext gehört zu anderem Scope.')
        elif value['contextSnapshot'] is not None or value['procedure']!='original-aetherone-v1':
            raise BroadcastTargetError('Persönlicher Auftrag braucht einen nachgewiesenen Fallkontext.')
        clean={k:v for k,v in value.items() if k!='digest'}
        if type(value['digest']) is not str or value['digest']!=document_digest(clean):raise BroadcastTargetError('Auftragsprüfsumme stimmt nicht.')
        return cls(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')))

    def payload(self):return json.loads(self._serialized)
    def summary(self):
        value=self.payload();snapshot=value['contextSnapshot']
        result={k:value[k] for k in ('schemaVersion','jobId','binding','source','procedure','entropyMode','digest')}
        if snapshot is not None:result.update(caseId=snapshot['caseId'],contextVersion=snapshot['contextVersion'],contextDigest=snapshot['digest'])
        return result

class BroadcastTargetStore:
    """One atomic receipt per accepted batch; separate terminal state document."""
    def __init__(self,root:Path,scope:ScopeContext,*,presentation_resolver=None):
        self.root=Path(root);self.scope=scope.to_dict();self._lock=threading.RLock();self._jobs={};self._broadcasts={};self._entropy_checkpoints={};self._presentation_resolver=presentation_resolver
        if self.root.is_symlink() or self.root.is_junction():raise BroadcastTargetError('Auftragsordner darf kein Link sein.')
        self.root.mkdir(parents=True,exist_ok=True)
        for path in self.root.glob('*.receipt.json'):
            if path.is_symlink() or path.is_junction():raise BroadcastTargetError('Auftragsbeleg darf kein Link sein.')
            try:record=json.loads(path.read_text(encoding='utf-8'))
            except (OSError,ValueError) as exc:raise BroadcastTargetError('Auftragsbeleg nicht lesbar.') from exc
            required={'schemaVersion','acceptedAt','scope','entries','digest'}
            if type(record) is not dict or set(record)!=required or type(record['schemaVersion']) is not int or record['schemaVersion']!=1:
                raise BroadcastTargetError('Unbekanntes Auftragsbelegschema.')
            try:
                timestamp=datetime.fromisoformat(record['acceptedAt'])
                if timestamp.tzinfo is None:raise ValueError()
            except (ValueError,TypeError) as exc:raise BroadcastTargetError('Auftragszeitpunkt ist ungültig.') from exc
            if record.get('scope')!=self.scope:raise BroadcastTargetError('Auftragsbeleg gehört zu anderem Scope.')
            rows=self._validate(record.get('entries'))
            if record.get('digest')!=document_digest({k:v for k,v in record.items() if k!='digest'}):raise BroadcastTargetError('Auftragsbeleg wurde verändert.')
            self._index(rows)
        self._load_entropy_checkpoints()
        states={job:self._state(job) for job in self._jobs}
        for job_id,state in states.items():
            if state not in ('finished','failed','stopped','interrupted'):
                self._write_state(job_id,'interrupted')

    def _validate(self,entries):
        if type(entries) is not list or not entries:raise BroadcastTargetError('Leerer Annahmebeleg.')
        rows=copy.deepcopy(entries);seen_jobs=set();seen_broadcasts=set()
        for row in rows:
            required={'broadcastId','signature','seconds','multiplier','clear','delayMs','repeat','target'}
            if type(row) is not dict or not required<=set(row) or set(row)-required-{'executionPolicy','presentation'}:raise BroadcastTargetError('Annahmebeleg hat unbekannte Felder.')
            if 'executionPolicy' in row:
                try:policy=ExecutionPolicy.from_payload(row['executionPolicy'])
                except PolicyError as exc:raise BroadcastTargetError('Ungültiger Ausführungsbeleg.') from exc
                if policy.seconds!=row['seconds']:raise BroadcastTargetError('Laufzeit und Ausführungsbeleg widersprechen sich.')
            target=BroadcastTarget.from_payload(row['target']).payload()
            job=target['jobId'];bid=row['broadcastId']
            if 'presentation' in row:
                try:row['presentation']=validate_presentation_receipt(row['presentation'],broadcast_id=bid,target=target)
                except PresentationProfileError as exc:raise BroadcastTargetError(str(exc)) from exc
            if target['scope']!=self.scope or job in seen_jobs or job in self._jobs:raise BroadcastTargetError('Doppelte oder fremde Auftragsbindung.')
            if type(bid) is not str or not HEX32.fullmatch(bid) or bid in seen_broadcasts or bid in self._broadcasts:raise BroadcastTargetError('Broadcast-ID ist ungültig oder doppelt.')
            if type(row['signature']) is not str or not row['signature'].strip():raise BroadcastTargetError('Signatur fehlt.')
            if type(row['seconds']) is not int or not 1<=row['seconds']<=86400 or type(row['multiplier']) is not int or not 1<=row['multiplier']<=1000:
                raise BroadcastTargetError('Auftragslaufzeit ist ungültig.')
            if type(row['clear']) is not bool or type(row['delayMs']) is not int or not 1<=row['delayMs']<=10000 or type(row['repeat']) is not int or not 1<=row['repeat']<=1000:
                raise BroadcastTargetError('Emitterparameter sind ungültig.')
            seen_jobs.add(job);seen_broadcasts.add(bid)
        return rows

    def _index(self,rows):
        for row in rows:
            job=row['target']['jobId'];self._jobs[job]=copy.deepcopy(row);self._broadcasts[row['broadcastId']]=job

    @staticmethod
    def _validate_entropy_checkpoint(checkpoint, entropy_mode):
        base={'mode','drawCount','effectiveSeed','sourceSegment','source'}
        journal={'journalId','journalCursor','journalDigest','journalPrefixDigest'}
        if type(checkpoint) is not dict or not base<=set(checkpoint) or set(checkpoint)-base-journal:
            raise BroadcastTargetError('Entropiecheckpoint hat ein ungültiges Schema.')
        present=journal & set(checkpoint)
        if present and present!=journal:
            raise BroadcastTargetError('Entropiejournalreferenz ist unvollständig.')
        if checkpoint['mode']!=entropy_mode:
            raise BroadcastTargetError('Checkpoint-Modus stimmt nicht mit dem Zielmodus überein.')
        if type(checkpoint['drawCount']) is not int or checkpoint['drawCount']<0:
            raise BroadcastTargetError('Checkpoint-Ziehungszahl ist ungültig.')
        if type(checkpoint['sourceSegment']) is not int or checkpoint['sourceSegment']<0:
            raise BroadcastTargetError('Checkpoint-Quellsegment ist ungültig.')
        if checkpoint['source'] not in ('seeded','webcam','random.org','os'):
            raise BroadcastTargetError('Checkpoint-Entropiequelle ist ungültig.')
        if entropy_mode=='seeded':
            if checkpoint['source']!='seeded' or type(checkpoint['effectiveSeed']) is not int:
                raise BroadcastTargetError('Seeded-Checkpoint ist ungültig.')
        elif checkpoint['source']=='seeded' or checkpoint['effectiveSeed'] is not None:
            raise BroadcastTargetError('Stochastic-Checkpoint ist ungültig.')
        if entropy_mode=='stochastic' and present!=journal:
            raise BroadcastTargetError('Stochastic-Checkpoint braucht eine Journalreferenz.')
        if present:
            if (type(checkpoint['journalId']) is not str or not HEX32.fullmatch(checkpoint['journalId'])
                    or type(checkpoint['journalCursor']) is not int
                    or checkpoint['journalCursor']!=checkpoint['drawCount']
                    or type(checkpoint['journalDigest']) is not str or not HEX64.fullmatch(checkpoint['journalDigest'])
                    or type(checkpoint['journalPrefixDigest']) is not str or not HEX64.fullmatch(checkpoint['journalPrefixDigest'])
                    or checkpoint['journalDigest']!=checkpoint['journalPrefixDigest']):
                raise BroadcastTargetError('Checkpoint-Journalreferenz ist ungültig.')
        return copy.deepcopy(checkpoint)

    def _load_entropy_checkpoints(self):
        for path in self.root.glob('*.entropy.json'):
            if path.is_symlink() or path.is_junction():
                raise BroadcastTargetError('Entropiecheckpoint darf kein Link sein.')
            try:
                record=json.loads(path.read_text(encoding='utf-8'))
            except (OSError,ValueError) as exc:
                raise BroadcastTargetError('Entropiecheckpoint ist nicht lesbar.') from exc
            if type(record) is not dict or set(record)!={'jobId','broadcastId','checkpoint','digest'}:
                raise BroadcastTargetError('Entropiecheckpoint hat ein unbekanntes Schema.')
            job_id=record['jobId'];broadcast_id=record['broadcastId']
            if (type(job_id) is not str or not HEX32.fullmatch(job_id)
                    or type(broadcast_id) is not str or not HEX32.fullmatch(broadcast_id)):
                raise BroadcastTargetError('Entropiecheckpoint enthält ungültige Referenzen.')
            row=self._jobs.get(job_id)
            if (row is None or path.name!=job_id+'.entropy.json'
                    or broadcast_id!=row['broadcastId']
                    or record['digest']!=document_digest({k:v for k,v in record.items() if k!='digest'})):
                raise BroadcastTargetError('Entropiecheckpoint oder Prüfsumme ist ungültig.')
            self._validate_entropy_checkpoint(record['checkpoint'],row['target']['entropyMode'])
            self._entropy_checkpoints[job_id]=copy.deepcopy(record)

    def record_entropy(self,payload):
        if type(payload) is not dict or set(payload)!={'broadcastId','checkpoint'}:
            raise BroadcastTargetError('Entropiecheckpoint-Eingabe ist ungültig.')
        broadcast_id=payload['broadcastId']
        if type(broadcast_id) is not str or not HEX32.fullmatch(broadcast_id):
            raise BroadcastTargetError('Broadcast-ID für Entropiecheckpoint ist ungültig.')
        with self._lock:
            job_id=self._broadcasts.get(broadcast_id)
            row=self._jobs.get(job_id) if job_id is not None else None
            if row is None or row['broadcastId']!=broadcast_id:
                raise BroadcastTargetError('Entropiecheckpoint gehört zu keinem angenommenen Auftrag.')
            checkpoint=self._validate_entropy_checkpoint(payload['checkpoint'],row['target']['entropyMode'])
            previous=self._entropy_checkpoints.get(job_id)
            if previous is not None:
                prior=previous['checkpoint']
                if checkpoint['drawCount']<prior['drawCount'] or checkpoint['sourceSegment']<prior['sourceSegment']:
                    raise BroadcastTargetError('Veralteter Entropiecheckpoint.')
            record={'jobId':job_id,'broadcastId':broadcast_id,'checkpoint':checkpoint}
            record['digest']=document_digest(record)
            path=self.root/(job_id+'.entropy.json')
            if path.is_symlink() or path.is_junction():
                raise BroadcastTargetError('Entropiecheckpoint darf kein Link sein.')
            atomic_json_replace(path,record)
            self._entropy_checkpoints[job_id]=copy.deepcopy(record)

    def accept(self,entries):
        with self._lock:
            prepared=copy.deepcopy(entries)
            if self._presentation_resolver is not None:
                for row in prepared:
                    if 'presentation' in row:
                        raise BroadcastTargetError('Präsentationsbeleg wird ausschließlich bei der Annahme eingefroren.')
                    try:
                        row['presentation']=self._presentation_resolver(row['target'],row['broadcastId'])
                    except PresentationProfileError as exc:
                        raise BroadcastTargetError(str(exc)) from exc
            rows=self._validate(prepared);body={'scope':self.scope,'entries':rows}
            record={**body,'schemaVersion':1,'acceptedAt':datetime.now(timezone.utc).isoformat()}
            record['digest']=document_digest(record)
            path=self.root/(uuid.uuid4().hex+'.receipt.json')
            atomic_json_replace(path,record)
            self._index(rows)
            if self._presentation_resolver is not None:
                return {row['broadcastId']:copy.deepcopy(row['presentation']) for row in rows}

    def _state(self,job_id):
        path=self.root/(job_id+'.state.json')
        if not path.exists():return 'accepted'
        if path.is_symlink() or path.is_junction():raise BroadcastTargetError('Auftragsstatus darf kein Link sein.')
        try:data=json.loads(path.read_text(encoding='utf-8'))
        except (OSError,ValueError) as exc:raise BroadcastTargetError('Auftragsstatus ist nicht lesbar.') from exc
        if set(data)!={'jobId','state'} or data['jobId']!=job_id or data['state'] not in ('finished','failed','stopped','interrupted'):
            raise BroadcastTargetError('Auftragsstatus ist ungültig.')
        return data['state']
    def _write_state(self,job_id,state):atomic_json_replace(self.root/(job_id+'.state.json'),{'jobId':job_id,'state':state})
    def get(self,job_id):
        with self._lock:
            row=self._jobs.get(job_id)
            if row is None:return None
            result={**copy.deepcopy(row),'state':self._state(job_id)}
            checkpoint=self._entropy_checkpoints.get(job_id)
            if checkpoint is not None:result['entropyCheckpoint']=copy.deepcopy(checkpoint)
            return result
    def terminal(self,payload):
        state='finished' if payload.get('finished') else 'failed' if payload.get('failed') else 'stopped' if payload.get('stopped') else None
        if state is None:return
        with self._lock:
            job=self._broadcasts.get(payload.get('broadcastId'))
            if job is not None and self._state(job)=='accepted':self._write_state(job,state)

    def record_adjustment(self, payload):
        required={'parentBroadcastId','parentJobId','rootJobId','depth','referenceGv','measuredGv','seconds','reason','childJobId'}
        if type(payload) is not dict or set(payload)!=required:raise BroadcastTargetError('Ungültiger Anpassungsbeleg.')
        with self._lock:
            job=payload['parentJobId'];row=self._jobs.get(job)
            if row is None or row['broadcastId']!=payload['parentBroadcastId']:raise BroadcastTargetError('Anpassung gehört zu keinem angenommenen Auftrag.')
            policy=ExecutionPolicy.from_payload(row.get('executionPolicy'))
            p=policy.payload()
            if not policy.dynamic_enabled or payload['rootJobId']!=p['rootJobId'] or payload['depth']!=p['depth'] or payload['referenceGv']!=p['referenceGv']:
                raise BroadcastTargetError('Anpassung widerspricht dem eingefrorenen Auftrag.')
            expected=policy.followup_seconds(payload['measuredGv'])
            if payload['seconds']!=expected or payload['reason'] not in ('followup','comparison-complete','followup-not-accepted'):
                raise BroadcastTargetError('Anpassungsentscheidung ist ungültig.')
            child=payload['childJobId']
            if (expected is None and child is not None) or (expected is not None and (type(child) is not str or not HEX32.fullmatch(child))):
                raise BroadcastTargetError('Folgeauftrags-ID ist ungültig.')
            record={'schemaVersion':1,'scope':self.scope,**copy.deepcopy(payload)}
            record['digest']=document_digest(record)
            atomic_json_replace(self.root/(job+'.adjustment.json'),record)
    def adjustments(self):
        with self._lock:
            rows=[]
            for path in sorted(self.root.glob('*.adjustment.json')):
                if path.is_symlink() or path.is_junction():raise BroadcastTargetError('Anpassungsbeleg darf kein Link sein.')
                record=json.loads(path.read_text(encoding='utf8'))
                if record.get('scope')!=self.scope or record.get('digest')!=document_digest({k:v for k,v in record.items() if k!='digest'}):
                    raise BroadcastTargetError('Anpassungsbeleg wurde verändert.')
                job=record.get('parentJobId')
                if job not in self._jobs or path.name!=job+'.adjustment.json':raise BroadcastTargetError('Anpassungsherkunft fehlt.')
                # Decision intent and durable child admission are separate facts.
                child = record.get('childJobId')
                accepted = self._jobs.get(child) if child else None
                admission = 'accepted' if accepted else 'not-accepted' if record.get('reason') == 'followup-not-accepted' else 'interrupted-before-acceptance' if child else 'not-requested'
                rows.append({**{k:v for k,v in record.items() if k not in ('scope',)},
                    'childAdmission': admission, 'childState': self._state(child) if accepted else None})
            return rows[-100:]

