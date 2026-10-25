"""Explicit options-v1 execution policies; immutable per accepted broadcast."""
from __future__ import annotations
import json,re
from dataclasses import dataclass
from ..persistence import document_digest

VERSION='options-v1'
class PolicyError(ValueError):pass

def _integer(value,lo,hi):
    if type(value) is not int or not lo<=value<=hi:raise PolicyError('Broadcast-Grenze ist ungültig.')
    return value

@dataclass(frozen=True,slots=True)
class ExecutionPolicy:
    _serialized:str
    @classmethod
    def capture(cls,settings,target,seconds,reference_gv=None,*,allow_delta=True):
        _integer(seconds,1,86400)
        b=settings.get('booleans',{});n=settings.get('integers',{});active=settings.get('strings',{}).get('broadcast.optionsVersion')==VERSION
        limit=_integer(n.get('broadcast.adjustment.maxFollowups',1),0,3)
        minimum=_integer(n.get('broadcast.adjustment.minSeconds',10),1,86400)
        original=target is not None and target.payload()['procedure']=='original-aetherone-v1' and target.payload()['binding']=='bound'
        reference=reference_gv if original and type(reference_gv) is int and 0<reference_gv<=1000000 else None
        delta=active and b.get('broadcast.delta.time') is True and allow_delta and reference is not None
        effective=seconds-reference if delta and seconds>reference else seconds
        body={'version':VERSION,'requestedSeconds':seconds,'seconds':effective,'referenceGv':reference,
              'deltaApplied':effective!=seconds,'dynamicEnabled':active and b.get('dynamic.adjustments') is True and reference is not None and limit>0,
              'maxFollowups':limit,'minSeconds':minimum,'depth':0,'rootJobId':target.payload()['jobId'] if target else None,'parentJobId':None}
        body['digest']=document_digest(body);return cls.from_payload(body)
    @classmethod
    def from_payload(cls,body):
        fields={'version','requestedSeconds','seconds','referenceGv','deltaApplied','dynamicEnabled','maxFollowups','minSeconds','depth','rootJobId','parentJobId','digest'}
        if type(body) is not dict or set(body)!=fields or body['version']!=VERSION:raise PolicyError('Unbekanntes Ausführungsschema.')
        for field,lo,hi in [('requestedSeconds',1,86400),('seconds',1,86400),('maxFollowups',0,3),('minSeconds',1,86400),('depth',0,3)]:_integer(body[field],lo,hi)
        if body['referenceGv'] is not None:_integer(body['referenceGv'],1,1000000)
        if any(type(body[k]) is not bool for k in ('deltaApplied','dynamicEnabled')):raise PolicyError('Ungültige Ausführungsauswahl.')
        if body['depth']>body['maxFollowups'] or (body['dynamicEnabled'] and (body['referenceGv'] is None or body['rootJobId'] is None)):raise PolicyError('Ungültige Folgeauftragsgrenze.')
        for k in ('rootJobId','parentJobId'):
            if body[k] is not None and (type(body[k]) is not str or not re.fullmatch('[0-9a-f]{32}',body[k])):raise PolicyError('Ungültiger Auftragsbezug.')
        if body['digest']!=document_digest({k:v for k,v in body.items() if k!='digest'}):raise PolicyError('Ausführungsbeleg wurde verändert.')
        return cls(json.dumps(body,sort_keys=True,separators=(',',':')))
    def payload(self):return json.loads(self._serialized)
    @property
    def seconds(self):return self.payload()['seconds']
    @property
    def dynamic_enabled(self):
        p=self.payload();return p['dynamicEnabled'] and p['depth']<p['maxFollowups']
    def followup_seconds(self,new_gv):
        _integer(new_gv,0,1000000);p=self.payload()
        if not self.dynamic_enabled or new_gv>=p['referenceGv']:return None
        s=p['seconds'];reduction=200 if s>1000 else 100 if s>500 else 50 if s>200 else 25 if s>100 else 0
        return max(p['minSeconds'],s-reduction) if s>=p['minSeconds'] else None
    def child(self,parent_job_id,seconds):
        p=self.payload();p.update(requestedSeconds=seconds,seconds=seconds,deltaApplied=False,depth=p['depth']+1,parentJobId=parent_job_id)
        p['digest']=document_digest({k:v for k,v in p.items() if k!='digest'});return self.from_payload(p)
