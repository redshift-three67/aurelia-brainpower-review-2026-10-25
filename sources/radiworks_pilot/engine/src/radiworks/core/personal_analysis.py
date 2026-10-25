"""Versioned personal procedure; original analysis and bounded EXP1 stay independent."""
from __future__ import annotations
import copy
import hashlib
import math
import re
from .experimental_matrix import _catalog_payload, _seed, prepare_catalog_context, MatrixError, WEIGHTS
from .personal_context import ContextSnapshot, ContextError
from ..persistence import document_digest

PROCEDURE = 'radi144-personal-v1'
SEED_SCHEME = 'radi144-personal-generator-sha256-v1'
MAX_PERSONAL_RATES = 4096  # Admission bound, not a measured duration guarantee.

class PersonalAnalysisError(ValueError):
    pass


def candidate_seed(basis_seed: int, mode: str, draw: int) -> int:
    encoded = f'{SEED_SCHEME}\0{basis_seed}\0{mode}\0{draw}'.encode('ascii')
    return int.from_bytes(hashlib.sha256(encoded).digest()[:4], 'big')


def freeze_personal_input(scope, snapshot, catalog, rates, *, mode, job_seed, entropy, implementation_hash, weight='Normal'):
    try:
        frozen = ContextSnapshot.from_payload(snapshot).payload()
        cat = _catalog_payload(catalog)
        prepared = prepare_catalog_context(frozen, cat)
    except (ContextError, MatrixError, TypeError, ValueError) as exc:
        raise PersonalAnalysisError('Persönlicher Kontext oder Katalog ist nicht gültig.') from exc
    if frozen['scope'] != scope.to_dict():
        raise PersonalAnalysisError('Persönlicher Auftrag liegt außerhalb des aktiven Bereichs.')
    names = [line.partition('\t')[0].strip() for line in cat['content'].splitlines() if line.strip()]
    if type(rates) is not list or not 1 <= len(rates) <= MAX_PERSONAL_RATES or rates != names:
        raise PersonalAnalysisError('Die vollständige gebundene Ratenliste muss 1–4096 Einträge enthalten; keine stille Kürzung.')
    if any(type(rate) is not str or not rate or len(rate) > 2048 for rate in rates):
        raise PersonalAnalysisError('Ratennamen sind nicht verarbeitbar.')
    if type(mode) is not str or type(weight) is not str or mode not in ('seeded', 'stochastic') or entropy.mode != mode or weight not in WEIGHTS:
        raise PersonalAnalysisError('Verfahren, Zufallsquelle oder Fokusgewicht stimmen nicht.')
    if (mode == 'seeded' and (type(job_seed) is not int or not -(2**63) <= job_seed < 2**63 or entropy.effective_seed != job_seed)) or (mode == 'stochastic' and job_seed is not None):
        raise PersonalAnalysisError('Auftragsseed stimmt nicht mit dem Zufallsmodus überein.')
    if type(implementation_hash) is not str or not re.fullmatch('[0-9a-f]{64}', implementation_hash):
        raise PersonalAnalysisError('Implementierungsbeleg fehlt.')
    if entropy.checkpoint().get('drawCount') != 0:
        raise PersonalAnalysisError('Persönlicher Auftrag benötigt eine frische eigene Zufallsfolge.')
    if mode == 'stochastic' and not entropy.checkpoint().get('journalId'):
        raise PersonalAnalysisError('Stochastik benötigt ein dauerhaftes eigenes Journal.')
    basis_seeds = [_seed(f"{frozen['context']['personal'].get('firstName') or ''}{frozen['context']['personal'].get('birthDate') or ''}{rate}") for rate in rates]
    seeds, draws, sources = [], [], []
    # Persist all entropy before a CPU child receives any candidate seed.
    with entropy.journal_write_scope():
        for base in basis_seeds:
            if mode == 'seeded' and job_seed == 0:
                seeds.append(base)
            else:
                draw = entropy.get_integer_bound(2**31 - 1)
                draws.append(draw)
                sources.append(entropy.status().active_source)
                seeds.append(candidate_seed(base, mode, draw))
    entropy.commit_journal()
    payload = {
        'schemaVersion':1, 'procedure':PROCEDURE, 'scope':scope.to_dict(),
        'contextSnapshot':frozen, 'catalog':cat, 'rates':list(rates),
        'mode':mode, 'jobSeed':job_seed, 'weight':weight,
        'candidateSeeds':seeds, 'drawValues':draws, 'drawSources':sources,
        'seedScheme':SEED_SCHEME, 'entropy':entropy.checkpoint(),
        'implementationHash':implementation_hash,
        'contextParameters':copy.deepcopy(prepared),
        'parameters':{'candidateCount':80000,'backend':'cpu','threads':1,'focusWeight':weight,'focusWeightValue':WEIGHTS[weight],'seedScheme':SEED_SCHEME,'projectionUse':'same-local-generator-after-candidates'},
    }
    payload['inputDigest'] = document_digest(payload)
    return payload


_INPUT_FIELDS = {'schemaVersion','procedure','scope','contextSnapshot','catalog','rates','mode','jobSeed','weight',
    'candidateSeeds','drawValues','drawSources','seedScheme','entropy','implementationHash','contextParameters','parameters','inputDigest'}


def validate_personal_input(payload):
    if type(payload) is not dict or set(payload) != _INPUT_FIELDS:
        raise PersonalAnalysisError('Persönlicher Eingabebeleg hat ein ungültiges Schema.')
    data = copy.deepcopy(payload)
    if type(data['schemaVersion']) is not int or data['schemaVersion'] != 1 or data['procedure'] != PROCEDURE or data['seedScheme'] != SEED_SCHEME:
        raise PersonalAnalysisError('Persönliches Verfahren ist nicht unterstützt.')
    if data['inputDigest'] != document_digest({k:v for k,v in data.items() if k != 'inputDigest'}):
        raise PersonalAnalysisError('Persönlicher Eingabebeleg wurde verändert.')
    try:
        snapshot=ContextSnapshot.from_payload(data['contextSnapshot']).payload()
        cat=_catalog_payload(data['catalog'])
        prepared=prepare_catalog_context(snapshot,cat)
    except (ContextError,MatrixError,TypeError,ValueError) as exc:
        raise PersonalAnalysisError('Kontext-/Katalogbeleg ist ungültig.') from exc
    names=[line.partition('\t')[0].strip() for line in cat['content'].splitlines() if line.strip()]
    if snapshot['scope'] != data['scope'] or type(data['rates']) is not list or data['rates'] != names or not 1 <= len(names) <= MAX_PERSONAL_RATES:
        raise PersonalAnalysisError('Ratenliste oder Bereich ist nicht vollständig gebunden.')
    mode, seed, weight=data['mode'],data['jobSeed'],data['weight']
    if type(mode) is not str or type(weight) is not str or mode not in ('seeded','stochastic') or weight not in WEIGHTS or (mode=='seeded' and (type(seed) is not int or not -(2**63)<=seed<2**63)) or (mode=='stochastic' and seed is not None):
        raise PersonalAnalysisError('Zufallsmodus oder Parameter sind ungültig.')
    params={'candidateCount':80000,'backend':'cpu','threads':1,'focusWeight':weight,'focusWeightValue':WEIGHTS[weight],'seedScheme':SEED_SCHEME,'projectionUse':'same-local-generator-after-candidates'}
    if data['parameters'] != params or data['contextParameters'] != prepared or not isinstance(data['implementationHash'],str) or not re.fullmatch('[0-9a-f]{64}',data['implementationHash']):
        raise PersonalAnalysisError('Formelparameter oder Implementierungsbeleg stimmen nicht.')
    draws, sources=data['drawValues'],data['drawSources']
    needed=0 if mode=='seeded' and seed==0 else len(names)
    if type(draws) is not list or len(draws)!=needed or any(type(v) is not int or not 0<=v<2**31-1 for v in draws) or type(sources) is not list or len(sources)!=needed or any(v not in (('seeded',) if mode=='seeded' else ('webcam','random.org','os')) for v in sources):
        raise PersonalAnalysisError('Rate-Ziehungen sind nicht vollständig belegt.')
    seeds=[]
    for i,rate in enumerate(names):
        base=_seed(f"{snapshot['context']['personal'].get('firstName') or ''}{snapshot['context']['personal'].get('birthDate') or ''}{rate}")
        seeds.append(base if needed==0 else candidate_seed(base,mode,draws[i]))
    if type(data['candidateSeeds']) is not list or any(type(v) is not int for v in data['candidateSeeds']) or data['candidateSeeds'] != seeds:
        raise PersonalAnalysisError('Kandidatenseeds stimmen nicht mit den Rate-Ziehungen überein.')
    entropy=data['entropy']
    if type(entropy) is not dict or entropy.get('mode')!=mode or type(entropy.get('drawCount')) is not int or entropy['drawCount']!=needed or (mode=='seeded' and entropy.get('effectiveSeed')!=seed):
        raise PersonalAnalysisError('Zufallscheckpoint stimmt nicht.')
    if mode=='stochastic' and (not isinstance(entropy.get('journalId'),str) or not re.fullmatch('[0-9a-f]{32}',entropy['journalId']) or entropy.get('journalCursor')!=needed or any(not isinstance(entropy.get(k),str) or not re.fullmatch('[0-9a-f]{64}',entropy[k]) for k in ('journalDigest','journalPrefixDigest'))):
        raise PersonalAnalysisError('Stochastischer Journalbeleg ist unvollständig.')
    return data


def _score_with_seed(torch, signature, rate, count, weight, seed):
    from .experimental_matrix import _embedding
    components=''.join(sorted(f'{k}:{v}' for k,v in signature['components'].items()))
    client=_embedding(torch,f"{signature['frequency']}_{components}")
    focus=_embedding(torch,rate)
    generator=torch.Generator(device='cpu').manual_seed(seed)
    with torch.no_grad():
        matrices=torch.randint(0,10,(count,144),generator=generator,device='cpu').float()
        projection=matrices@torch.randn(144,256,generator=generator,device='cpu',dtype=torch.float32)
        similarities=torch.nn.functional.cosine_similarity(projection,client+focus*weight)
        scores,indices=torch.topk(similarities,10)
        pattern=matrices[indices[0]]
        score=float(scores[0]);intensity=float(torch.std(pattern))
        if not math.isfinite(score) or not math.isfinite(intensity):
            raise PersonalAnalysisError('Persönliche Matrixberechnung lieferte keine endlichen Werte.')
        return {'score':score,'intensity':intensity,'matrix':pattern.reshape(12,12).int().tolist()}


def rank_personal_block(payload, indices, *, profile=None):
    from .experimental_matrix import CPU_PROFILE, PROBE_PROFILE, _load_cpu, _score
    data=validate_personal_input(payload)
    profile=CPU_PROFILE if profile is None else profile
    if profile not in (CPU_PROFILE,PROBE_PROFILE) or type(indices) is not list or not 1<=len(indices)<=21 or len(set(indices))!=len(indices) or any(type(i) is not int or not 0<=i<len(data['rates']) for i in indices):
        raise PersonalAnalysisError('Persönlicher Rechenblock oder Profil ist ungültig.')
    torch=_load_cpu();rows=[]
    for i in indices:
        rate=data['rates'][i]
        if data['mode']=='seeded' and data['jobSeed']==0:
            value=_score(torch,data['contextParameters']['signature'],data['contextSnapshot']['context']['personal'],rate,profile.candidate_count,WEIGHTS[data['weight']])
        else:
            value=_score_with_seed(torch,data['contextParameters']['signature'],rate,profile.candidate_count,WEIGHTS[data['weight']],data['candidateSeeds'][i])
        rows.append({'inputIndex':i,'rate':rate,**value})
    return rows
