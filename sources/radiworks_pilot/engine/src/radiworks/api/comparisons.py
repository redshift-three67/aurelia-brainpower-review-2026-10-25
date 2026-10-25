"""Explicit comparisons: current-case guarded API, no Original/GV/Broadcast mutation."""
import copy
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from .. import copyguard
from ..persistence import RecoveryError
from ..core.comparison_basis import read_source, build_comparison_input, ComparisonBasisError
from ..core.comparison_controller import ComparisonControllerError, implementation_hash
from ..core.experimental_matrix import prepare_catalog_context, MatrixError
from ..core.comparison_store import ComparisonStoreError


class ComparisonRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_case_ref: str = Field(pattern=r'^[0-9a-f]{64}$')
    source_session_id: str = Field(pattern=r'^[0-9a-f]{32}$')
    page_start: StrictInt = Field(default=0, ge=0)
    weight: Literal['Deaktiviert','Sanft','Normal','Stark'] = 'Normal'
    request_id: str = Field(pattern=r'^[0-9a-f]{32}$')


class JobCommand(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_case_ref: str = Field(pattern=r'^[0-9a-f]{64}$')
    request_id: str = Field(pattern=r'^[0-9a-f]{32}$')


def public_job(record):
    payload = record['input']
    response = {k:copy.deepcopy(record[k]) for k in ('id','requestId','comparisonSessionId','status','error','parentJobId','createdAt','updatedAt','inputDigest')}
    response.update(caseId=payload['caseId'], sourceSessionId=payload['sourceSessionId'], pageStart=payload['pageStart'],
        weight=payload['weight'], catalog={k:payload['catalog'][k] for k in ('name','sha256')},
        contextDigest=payload['contextSnapshot']['digest'], formulaVersion=payload['formulaVersion'],
        implementationHash=payload['implementationHash'], originalSubset=copy.deepcopy(payload['originalSubset']))
    response['result'] = copy.deepcopy(record['result'])
    if response['result'] is not None: response['result'].pop('preparedContext', None)
    return copyguard.public_view(response)


def build_comparison_router(state):
    router = APIRouter()

    def bound_case(reference):
        current = state.case_store.current
        if not current or reference != state.case_store.reference_for_case(current):
            raise HTTPException(409, 'Fallbindung ist nicht mehr aktuell. Bitte Fall neu laden.')
        return current

    def controller():
        if state.comparisons is None or state.comparisons.store is None: raise HTTPException(503, 'Experimentalvergleich ist nicht verfügbar.')
        return state.comparisons

    def owned_job(identifier, case):
        try: record = controller().store.get(identifier)
        except ComparisonStoreError as exc: raise HTTPException(404, 'Vergleichsauftrag nicht vorhanden.') from exc
        if record['input']['caseId'] != case['caseId']: raise HTTPException(404, 'Vergleichsauftrag nicht vorhanden.')
        return record

    def require_cpu_slot():
        if state.personal and state.personal.store and state.personal.store.has_pending():
            raise HTTPException(409,'Persönlicher CPU-Auftrag läuft bereits; bitte Abschluss oder Abbruch abwarten.')

    def controlled_error(exc):
        code = getattr(exc, 'code', 'comparison_conflict')
        status = 503 if code in ('cpu_unavailable','shutdown') else 409
        return HTTPException(status, {'code':code, 'message':'Vergleich kann nicht ausgeführt werden; Original bleibt unverändert.'})

    @router.get('/comparisons/capability')
    def capability():
        return state.comparisons.capability()

    @router.get('/comparisons/sources')
    def sources(case_ref: str):
        with state.stick_pad.transaction_lock():
            case = bound_case(case_ref); available=[]
            for index, session in enumerate(case.get('sessionList', [])):
                if 'comparisonBasis' not in session: continue
                item={'sessionId':session['sessionId'],'index':index,'eligible':False,'reason':'source_not_supported'}
                try:
                    source=read_source(controller().root.parent/'comparison_sources',session['comparisonBasis'])
                    if source['scope'] != state.scope.to_dict() or source['caseId'] != case['caseId'] or source['contextSnapshot'] != session.get('contextSnapshot') or source['baseline'] != session.get('analysisBaseline') or source['passport'] != session.get('passport'):
                        raise ComparisonBasisError('Quellbindung stimmt nicht.')
                    prepare_catalog_context(source['contextSnapshot'],source['catalog'])
                    item.update(eligible=True,reason=None,catalog=source['catalog']['name'],
                        rateCount=len(source['baseline']['rateObjects']),contextDigest=source['contextSnapshot']['digest'])
                except (ComparisonBasisError,MatrixError): pass
                available.append(item)
            return copyguard.public_view({'caseId':case['caseId'],'sources':available})

    @router.get('/comparisons')
    def jobs(case_ref: str):
        with state.stick_pad.transaction_lock():
            case=bound_case(case_ref)
            return {'caseId':case['caseId'],'jobs':[public_job(r) for r in controller().store.list_for_case(case['caseId'])]}

    @router.get('/comparisons/{job_id}')
    def job(job_id: str, case_ref: str):
        with state.stick_pad.transaction_lock():
            return public_job(owned_job(job_id,bound_case(case_ref)))

    @router.post('/comparisons')
    def create(body: ComparisonRequest):
        with state.stick_pad.transaction_lock():
            case=bound_case(body.expected_case_ref)
            try:
                state.recovery.ensure_no_pending()
                matches=[s for s in case.get('sessionList',[]) if s.get('sessionId')==body.source_session_id]
                if len(matches)!=1: raise ComparisonBasisError('Belegte Originalquellsitzung fehlt; bitte neue Originalanalyse starten.')
                source=read_source(controller().root.parent/'comparison_sources',matches[0].get('comparisonBasis'))
                payload=build_comparison_input(source,matches[0],case,state.scope,page_start=body.page_start,weight=body.weight,implementation_hash=implementation_hash())
                require_cpu_slot()
                return public_job(controller().request(payload,body.request_id))
            except (ComparisonBasisError,RecoveryError) as exc: raise HTTPException(409,str(exc)) from exc
            except (ComparisonControllerError,ComparisonStoreError) as exc: raise controlled_error(exc) from exc

    @router.post('/comparisons/{job_id}/cancel')
    def cancel(job_id: str, body: JobCommand):
        with state.stick_pad.transaction_lock():
            owned_job(job_id,bound_case(body.expected_case_ref))
            try: return public_job(controller().cancel(job_id))
            except (ComparisonControllerError,ComparisonStoreError) as exc: raise controlled_error(exc) from exc

    @router.post('/comparisons/{job_id}/retry')
    def retry(job_id: str, body: JobCommand):
        with state.stick_pad.transaction_lock():
            owned_job(job_id,bound_case(body.expected_case_ref))
            try:
                require_cpu_slot()
                return public_job(controller().retry(job_id,body.request_id))
            except (ComparisonControllerError,ComparisonStoreError) as exc: raise controlled_error(exc) from exc

    return router
