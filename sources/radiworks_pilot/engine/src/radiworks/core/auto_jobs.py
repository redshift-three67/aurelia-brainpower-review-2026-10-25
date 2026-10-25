"""Durable Auto generation binding and checkpoint; restart never enables Auto."""
import copy
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from .broadcast_target import BroadcastTarget, BroadcastTargetStore, BroadcastTargetError
from .rates import catalog_binding
from ..persistence import atomic_json_replace, document_digest

class AutoJobStore:
    def __init__(self,root,scope):
        self.root=Path(root);self.scope=scope.to_dict();self._lock=threading.RLock();self._records={}
        if self.root.is_symlink() or self.root.is_junction():raise BroadcastTargetError('Auto-Belegordner darf kein Link sein.')
        self.root.mkdir(parents=True,exist_ok=True)
        for path in self.root.glob('*.json'):
            if path.is_symlink() or path.is_junction():raise BroadcastTargetError('Auto-Beleg darf kein Link sein.')
            try:record=json.loads(path.read_text(encoding='utf-8'))
            except (OSError,ValueError) as exc:raise BroadcastTargetError('Auto-Beleg nicht lesbar.') from exc
            self._validate(record)
            identifier=record['target']['source']['generationId']
            if path.name!=identifier+'.json':raise BroadcastTargetError('Auto-Belegdatei stimmt nicht mit Generation überein.')
            self._records[identifier]=record
        for identifier,record in list(self._records.items()):
            if record['state']=='active':self._write({**record,'state':'interrupted'})

    def _validate(self,record):
        fields={'schemaVersion','target','database','multiplier','catalog','entropy','state','updatedAt','digest'}
        if type(record) is not dict or set(record)!=fields or type(record['schemaVersion']) is not int or record['schemaVersion']!=1:raise BroadcastTargetError('Auto-Belegschema ungültig.')
        target=BroadcastTarget.from_payload(record['target']).payload()
        if target['scope']!=self.scope or target['source']['kind']!='auto' or target['procedure']!='original-aetherone-v1':raise BroadcastTargetError('Auto-Beleg gehört zu anderem Auftrag.')
        if type(record['database']) is not str or not record['database'] or type(record['multiplier']) is not int or not 1<=record['multiplier']<=1000 or record['state'] not in ('active','stopped','failed','interrupted'):raise BroadcastTargetError('Auto-Parameter ungültig.')
        if type(record['catalog']) is not dict:raise BroadcastTargetError('Auto-Katalogbeleg fehlt.')
        BroadcastTargetStore._validate_entropy_checkpoint(record['entropy'],target['entropyMode'])
        if record['digest']!=document_digest({k:v for k,v in record.items() if k!='digest'}):raise BroadcastTargetError('Auto-Beleg wurde verändert.')

    def _write(self,record):
        record=copy.deepcopy(record);record['updatedAt']=datetime.now(timezone.utc).isoformat()
        record.pop('digest',None);record['digest']=document_digest(record);self._validate(record)
        identifier=record['target']['source']['generationId'];path=self.root/(identifier+'.json')
        if path.is_symlink() or path.is_junction():raise BroadcastTargetError('Auto-Beleg darf kein Link sein.')
        atomic_json_replace(path,record);self._records[identifier]=record

    def accept(self,target,database,multiplier,rates,checkpoint):
        with self._lock:
            value=target.payload();identifier=value['source']['generationId']
            if identifier in self._records:raise BroadcastTargetError('Auto-Generation wurde bereits angenommen.')
            self._write({'schemaVersion':1,'target':value,'database':database,'multiplier':multiplier,'catalog':catalog_binding(database,rates),'entropy':checkpoint,'state':'active'})

    def checkpoint(self,target,checkpoint):
        with self._lock:
            identifier=target.payload()['source']['generationId'];record=self._records.get(identifier)
            if record is None or record['target']!=target.payload() or record['state']!='active':raise BroadcastTargetError('Auto-Generation ist nicht aktiv.')
            if checkpoint.get('drawCount',-1)<record['entropy']['drawCount']:raise BroadcastTargetError('Auto-Checkpoint ist veraltet.')
            self._write({**record,'entropy':checkpoint})

    def end(self,target,state):
        if target is None:return
        with self._lock:
            identifier=target.payload()['source']['generationId'];record=self._records.get(identifier)
            if record is not None and record['state']=='active':self._write({**record,'state':state})

    def get(self,identifier):
        with self._lock:return copy.deepcopy(self._records.get(identifier))
