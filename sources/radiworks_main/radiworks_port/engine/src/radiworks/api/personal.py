"""Separate personal procedure; immutable catalog/context and explicit randomness."""
import copy
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from .. import copyguard
from ..core.personal_context import ContextSnapshot, ContextError
from ..core.personal_analysis import freeze_personal_input, PersonalAnalysisError, MAX_PERSONAL_RATES
from ..core.personal_controller import personal_implementation_hash
from ..core.personal_jobs import PersonalJobError
from ..core.comparison_basis import capture_catalog, ComparisonBasisError
from ..persistence import RecoveryError
from ..entropy_journal import JournalConfigurationError

class PersonalRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    expected_case_ref: str=Field(pattern=r'^[0-9a-f]{64}$')
    expected_context_version: StrictInt=Field(ge=1)
    request_id: str=Field(pattern=r'^[0-9a-f]{32}$')
    database: str=Field(min_length=1,max_length=240)
    mode: Literal['seeded','stochastic']
    seed: StrictInt | None=Field(default=0,ge=-(2**63),lt=2**63)
    weight: Literal['Deaktiviert','Sanft','Normal','Stark']='Normal'

class PersonalCommand(BaseModel):
    model_config=ConfigDict(extra='forbid')
    expected_case_ref: str=Field(pattern=r'^[0-9a-f]{64}$')


def public_personal_job(record):
    data=record['input']
    response={k:copy.deepcopy(record[k]) for k in ('id','requestId','status','createdAt','updatedAt','resultDigest','error')}
    response.update(procedure=data['procedure'],mode=data['mode'],seed=data['jobSeed'],weight=data['weight'],
        caseId=data['contextSnapshot']['caseId'],contextVersion=data['contextSnapshot']['contextVersion'],contextDigest=data['contextSnapshot']['digest'],
        catalog={k:data['catalog'][k] for k in ('name','sha256')},inputDigest=data['inputDigest'],implementationHash=data['implementationHash'],
        completedRates=len(record['rows']),totalRates=len(data['rates']),complete=record['status']=='completed',
        entropy={'mode':data['mode'],'sources':sorted(set(data['drawSources'])) or ['seeded'],'drawCount':data['entropy']['drawCount']})
    # Incomplete CPU blocks are progress only, never a partially ranked analysis.
    response['rows']=copy.deepcopy(record['rows']) if record['status']=='completed' else []
    return copyguard.public_view(response)


def build_personal_router(state):
    router=APIRouter()
    def controller():
        if state.personal is None or state.personal.store is None:raise HTTPException(503,'Persönliche Analyse ist nicht verfügbar.')
        return state.personal
    def bound_case(reference,version=None):
        case=state.case_store.current
        if not case or not case.get('caseId') or state.case_store.reference_for_case(case)!=reference or (version is not None and case.get('contextVersion')!=version):raise HTTPException(409,'Fall oder Kontext wurde geändert. Bitte Fall erneut laden.')
        return case
    def controlled(exc):
        code=getattr(exc,'code','personal_conflict')
        status=413 if code=='input_too_large' else 503 if code in ('cpu_unavailable','shutdown','store_unavailable') else 409
        return HTTPException(status,{'code':code,'message':'Persönlicher Auftrag nicht ausgeführt; Original bleibt unverändert.'})
    def owned(identifier,case):
        try:record=controller().store.get(identifier)
        except PersonalJobError as exc:
            if exc.code=='not_found':raise HTTPException(404,'Auftrag nicht vorhanden.') from exc
            raise controlled(exc) from exc
        if record['input']['contextSnapshot']['caseId']!=case['caseId']:raise HTTPException(404,'Auftrag nicht vorhanden.')
        return record

    @router.get('/personal-analyses/capability')
    def capability():return state.personal.capability()

    @router.get('/personal-analyses')
    def jobs(case_ref:str):
        with state.stick_pad.transaction_lock():
            case=bound_case(case_ref)
            try:return {'caseId':case['caseId'],'jobs':[public_personal_job(r) for r in controller().store.list(case['caseId'])]}
            except PersonalJobError as exc:raise controlled(exc) from exc

    @router.get('/personal-analyses/{identifier}')
    def job(identifier:str,case_ref:str):
        with state.stick_pad.transaction_lock():return public_personal_job(owned(identifier,bound_case(case_ref)))

    @router.post('/personal-analyses')
    def create(body:PersonalRequest):
        with state.stick_pad.transaction_lock():
            case=bound_case(body.expected_case_ref,body.expected_context_version)
            try:
                state.recovery.ensure_no_pending()
                ctrl=controller()
                if not ctrl.capability()['configured']:raise PersonalJobError('cpu_unavailable')
                if body.mode=='stochastic' and body.seed is not None:raise PersonalJobError('invalid_seed')
                if body.mode=='seeded' and body.seed is None:raise PersonalJobError('invalid_seed')
                rates=state.rate_repository.find_all_fresh_by_source_name(body.database)
                if not 1<=len(rates)<=MAX_PERSONAL_RATES:raise HTTPException(413,'Persönliche Analyse benötigt eine vollständige Liste mit höchstens 4096 Raten; es wird nichts gekürzt. Original bleibt nutzbar.')
                catalog=capture_catalog(state.rate_repository,body.database,rates)
                snapshot=ContextSnapshot.capture(case,state.scope).payload()
                digest=personal_implementation_hash()
                previous=ctrl.store.by_request(body.request_id)
                if previous is not None:
                    old=previous['input']
                    keys=('schemaVersion','caseId','contextVersion','scope','context','originalPersonal')
                    same_context=all(old['contextSnapshot'][k]==snapshot[k] for k in keys)
                    if not same_context or (old['catalog'],old['mode'],old['jobSeed'],old['weight'],old['implementationHash'])!=(catalog,body.mode,body.seed,body.weight,digest):raise PersonalJobError('request_conflict')
                    return public_personal_job(previous)
                ctrl.store.ensure_capacity()
                if state.comparisons and state.comparisons.store and state.comparisons.store.has_pending():raise PersonalJobError('busy')
                journal=state.create_entropy_journal() if body.mode=='stochastic' else None
                provider=state.new_provider(body.seed,body.mode,journal=journal)
                payload=freeze_personal_input(state.scope,snapshot,catalog,[r.name for r in rates],mode=body.mode,job_seed=body.seed,entropy=provider,implementation_hash=digest,weight=body.weight)
                return public_personal_job(ctrl.request(payload,body.request_id))
            except (PersonalJobError,) as exc:raise controlled(exc) from exc
            except (ContextError,PersonalAnalysisError,ComparisonBasisError,RecoveryError) as exc:raise HTTPException(409,str(exc)) from exc
            except (JournalConfigurationError,OSError) as exc:raise HTTPException(503,'Eigene Zufallsquelle oder Katalog derzeit nicht dauerhaft verfügbar.') from exc

    @router.post('/personal-analyses/{identifier}/cancel')
    def cancel(identifier:str,body:PersonalCommand):
        with state.stick_pad.transaction_lock():
            owned(identifier,bound_case(body.expected_case_ref))
            try:return public_personal_job(controller().cancel(identifier))
            except PersonalJobError as exc:raise controlled(exc) from exc

    return router
