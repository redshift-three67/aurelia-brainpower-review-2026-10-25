"""Optional isolated CPU profile of the existing Radi144 matrix heuristic.

No original engine imports Torch. Callers supply frozen snapshot/catalog/rates;
C1 does not select datasets, persist sessions, assign medical meaning or broadcast.
"""
from __future__ import annotations
import copy
import hashlib
import math
import platform
import re
import sys
from dataclasses import dataclass
from .experimental_context import prepare_experimental_context,ExperimentalContextError,_text_to_frequency
from .personal_context import ContextSnapshot,ContextError
from ..persistence import document_digest

FORMULA_VERSION='radi144-matrix-cpu-v1'
ENGINE_SHA256='2aef926e2885adaee5a0724aaea827daf03d4363f07ed399d08d5e2c31333a09'
ROUTES_SHA256='a161551637e4149d3c8962cf870bca075d337f43cc798979a53b7c94ca538983'
WEIGHTS={'Deaktiviert':0.0,'Sanft':0.4,'Normal':1.0,'Stark':1.5}
MAX_CATALOG_BYTES=4*1024*1024
MAX_RATES=21

class MatrixError(ValueError):
    """Controlled unsupported/unavailable/failed EXP1 computation."""

@dataclass(frozen=True)
class MatrixProfile:
    candidate_count:int
    purpose:str

CPU_PROFILE=MatrixProfile(80000,'product-cpu')
PROBE_PROFILE=MatrixProfile(64,'test-only')


def _catalog_payload(catalog:object)->dict:
    if type(catalog) is not dict or set(catalog)!={'name','sha256','content'}:
        raise MatrixError('Katalogbindung ist unvollständig.')
    name,sha,content=(catalog[k] for k in ('name','sha256','content'))
    if (type(name) is not str or not name.endswith('.txt') or len(name)>240
        or any(c in name for c in '/\\:') or name in ('.txt','..txt')
        or any(ord(c)<32 for c in name)):
        raise MatrixError('Ein exakter Katalog-Dateiname ist erforderlich.')
    if type(content) is not str or type(sha) is not str or not re.fullmatch('[0-9a-f]{64}',sha):
        raise MatrixError('Kataloginhalt oder SHA-256 ist ungültig.')
    try: encoded=content.encode('utf-8')
    except UnicodeError as exc: raise MatrixError('Katalog ist kein gültiger UTF-8-Text.') from exc
    if len(encoded)>MAX_CATALOG_BYTES or hashlib.sha256(encoded).hexdigest()!=sha:
        raise MatrixError('Kataloggröße oder Prüfsumme stimmt nicht.')
    return {'name':name,'sha256':sha,'content':content}


def _snapshot_payload(snapshot:object)->dict:
    try:
        raw=snapshot.payload() if isinstance(snapshot,ContextSnapshot) else snapshot
        return ContextSnapshot.from_payload(raw).payload()
    except (ContextError,TypeError,ValueError,AttributeError) as exc:
        raise MatrixError('Kontext-Snapshot ist ungültig.') from exc


def prepare_catalog_context(snapshot:object,catalog:object)->dict:
    frozen=_snapshot_payload(snapshot);cat=_catalog_payload(catalog)
    try: result=prepare_experimental_context(frozen)
    except ExperimentalContextError as exc:raise MatrixError(str(exc)) from exc
    focus=frozen['context']['focus']
    if focus is None:focus=''
    if type(focus) is not str or len(focus)>2048:
        raise MatrixError('Gespeicherter Fokus ist ungültig.')
    matched=bool(focus) and focus.lower() in cat['content'].lower()
    frequency=_text_to_frequency(focus) if matched else 0.0
    if frequency>0:
        base=result['signature']['frequency']
        result['signature']['frequency']=(base+frequency)/2 if base else frequency
        result['signature']['components'].update(db_frequency_hz=frequency,db_source=cat['name'])
    result['catalog']={'name':cat['name'],'sha256':cat['sha256'],'byteLength':len(cat['content'].encode('utf-8'))}
    result['focusMatch']={'matched':matched,'applied':frequency>0,'method':'literal-substring-lower-v1'}
    result['focusUse']='catalog-match-applied' if frequency>0 else 'no-numeric-catalog-match'
    return result


def _load_cpu():
    try:
        import torch
        import numpy
    except (ImportError,OSError) as exc:
        raise MatrixError('Optionales CPU-Profil nicht verfügbar; Originalmodus bleibt eigenständig.') from exc
    if str(torch.__version__)!='2.12.0+cpu' or numpy.__version__!='2.4.6':
        raise MatrixError('CPU-Abhängigkeitsversion stimmt nicht mit dem geprüften Profil überein.')
    if sys.version_info[:2]!=(3,13) or platform.system()!='Windows':
        raise MatrixError('Dieses CPU-Profil ist bisher nur für Windows/Python3.13 geprüft.')
    if torch.get_num_threads()!=1:
        raise MatrixError('CPU-Profil verlangt einen vorher separat konfigurierten Thread.')
    return torch


def _seed(text:str)->int:
    return int(hashlib.md5(text.encode('utf-8')).hexdigest()[:8],16)


def _embedding(torch,text:str):
    generator=torch.Generator(device='cpu').manual_seed(_seed(text))
    return torch.randn(256,generator=generator,device='cpu',dtype=torch.float32)


def _score(torch,signature:dict,personal:dict,rate:str,count:int,weight:float)->dict:
    components=''.join(sorted(f'{k}:{v}' for k,v in signature['components'].items()))
    client=_embedding(torch,f"{signature['frequency']}_{components}")
    focus=_embedding(torch,rate)
    master=f"{personal.get('firstName') or ''}{personal.get('birthDate') or ''}{rate}"
    generator=torch.Generator(device='cpu').manual_seed(_seed(master))
    with torch.no_grad():
        matrices=torch.randint(0,10,(count,144),generator=generator,device='cpu').float()
        target=client+focus*weight
        projection=matrices@torch.randn(144,256,generator=generator,device='cpu',dtype=torch.float32)
        similarities=torch.nn.functional.cosine_similarity(projection,target)
        scores,indices=torch.topk(similarities,10)
        pattern=matrices[indices[0]]
        score=float(scores[0]);intensity=float(torch.std(pattern))
        if not math.isfinite(score) or not math.isfinite(intensity):
            raise MatrixError('Matrixberechnung lieferte keine endlichen Werte.')
        return {'score':score,'intensity':intensity,'matrix':pattern.reshape(12,12).int().tolist()}


def rank_experimental_rates(snapshot:object,catalog:object,rates:object,*,weight:str='Normal',profile:MatrixProfile=CPU_PROFILE)->dict:
    frozen=_snapshot_payload(snapshot);cat=_catalog_payload(catalog)
    if type(weight) is not str or weight not in WEIGHTS:
        raise MatrixError('Fokusgewicht ist nicht unterstützt.')
    if (type(profile) is not MatrixProfile or type(profile.candidate_count) is not int
        or type(profile.purpose) is not str or profile not in (CPU_PROFILE,PROBE_PROFILE)):
        raise MatrixError('Matrixprofil ist nicht unterstützt.')
    if type(rates) is not list:
        raise MatrixError('Pro Aufruf ist eine explizite Ratenliste erforderlich.')
    rates=list(rates)  # Freeze the external list before validation and CPU work.
    if not 1<=len(rates)<=MAX_RATES:
        raise MatrixError('Pro Aufruf sind ausdrücklich 1–21 Raten erforderlich.')
    names={line.partition('\t')[0] for line in cat['content'].splitlines() if line.strip()}
    for rate in rates:
        if type(rate) is not str or not 1<=len(rate)<=2048 or not rate.strip() or rate not in names:
            raise MatrixError('Eine Rate fehlt im gebundenen Katalog oder ist ungültig.')
    prepared=prepare_catalog_context(frozen,cat)
    torch=_load_cpu()
    parameters={'backend':'cpu','dtype':'float32','matrixSize':12,'embedDimension':256,
        'candidateCount':profile.candidate_count,'purpose':profile.purpose,'threads':1,
        'focusWeight':weight,'focusWeightValue':WEIGHTS[weight],'rng':'local-torch-generators','topK':10,
        'torchVersion':str(torch.__version__),'numpyVersion':'2.4.6','pythonVersion':platform.python_version(),
        'platform':platform.system(),'bioEnabled':False,'hrvEnabled':False,'emfEnabled':False,
        'quantumEnabled':False,'symmetry':'none','clockEnabled':False,'numericImageEnabled':False,
        'rateScope':'explicit-bound-subset','maximumRates':MAX_RATES}
    rows=[]
    try:
        for index,rate in enumerate(rates):
            rows.append({'rate':rate,'originalIndex':index,**_score(torch,prepared['signature'],frozen['context']['personal'],rate,profile.candidate_count,WEIGHTS[weight])})
    except (RuntimeError,MemoryError) as exc:
        raise MatrixError('CPU-Berechnung fehlgeschlagen; kein vollständiges Ergebnis verfügbar.') from exc
    rows.sort(key=lambda row:(-row['score'],row['originalIndex']))
    result={'formulaVersion':FORMULA_VERSION,'sourceHashes':{**prepared['sourceHashes'],
        'Radi144/app/algorithms/resonance_engine.py':ENGINE_SHA256,'Radi144/app/api/resonance.py':ROUTES_SHA256},
        'caseId':prepared['caseId'],'contextVersion':prepared['contextVersion'],'contextDigest':prepared['contextDigest'],
        'catalog':prepared['catalog'],'preparedContext':copy.deepcopy(prepared),'parameters':parameters,
        'inputRates':list(rates),'results':rows}
    result['resultDigest']=document_digest(result)
    return result
