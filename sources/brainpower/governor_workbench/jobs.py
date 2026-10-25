"""One bounded worker, exact actions, durable outcomes and cancellation."""
import os
import math
from pathlib import Path
import queue
import subprocess
import threading
import time
import xml.etree.ElementTree as ET
from .evidence import now, fingerprint
from .llm import RouterClient, hybrid_review, model_check
from .hermes import HermesAdapter
from .model_usage import TrackedClient, HERMES_PROMPT_CHARS, ROUTER_PROMPT_CHARS


class JobCancelled(RuntimeError): pass


def verify_question_sources(binding, context, sources=None):
    """Check only the sealed selected paths, including files absent at review time."""
    from .execution_workspace import _root, _read, _sha
    if (not isinstance(binding, dict) or set(binding) != {'root', 'root_identity', 'hashes'}
            or not isinstance(binding['hashes'], dict) or not 1 <= len(binding['hashes']) <= 20):
        raise ValueError('Exakte Quellenbindung der Rückfrage fehlt; neuer Review erforderlich.')
    root, identity = _root(binding['root'])
    if identity != binding['root_identity'] or not any(
            os.path.normcase(str(root)) == os.path.normcase(str(p.get('path')))
            for p in context['registry_projects']):
        raise ValueError('Quellenwurzel der Rückfrage geändert; neuer Review erforderlich.')
    if sources is None:
        actual = {}
        for path in binding['hashes']:
            raw = _read(root, path)
            actual[path] = None if raw is None else _sha(raw)
    else:
        actual = {source['path']: source['sha256'] for source in sources}
    if actual != binding['hashes']:
        raise ValueError('Exakte Quellen der Rückfrage geändert; neuer Review erforderlich.')


def evidence_stale(before,after):
    return (not before.get('evidence_complete') or not after.get('evidence_complete')
            or before.get('evidence_hash')!=after.get('evidence_hash'))


def verified_runs(jobs,observation):
    if not observation.get('evidence_complete'): return []
    return [{'action':j['action'],'result':{k:j['result'].get(k) for k in ('summary','exit_code','evidence_hash','stale')}}
            for j in jobs if j['action']=='radiworks_tests' and j['status']=='completed' and j.get('result') and
            j['result'].get('source_hash',j['result'].get('evidence_hash'))==observation.get('source_hash',observation['evidence_hash']) and not j['result'].get('stale')]


def run_process(argv,cwd,env,cancel,on_line,timeout=300):
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('Prozesszeitlimit muss endlich und positiv sein.')
    if cancel.is_set():
        raise JobCancelled('Auftrag vor Prozessstart abgebrochen.')
    owner=None
    if os.name=='nt':
        from .process_tree import start_owned_windows
        process,owner=start_owned_windows(argv,cwd,env)
    else:
        process=subprocess.Popen(argv,cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',
                             creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    lines=queue.Queue(maxsize=1000)
    dropped=threading.Event()
    def reader():
        # Bound the read itself, including output with no newline.
        for line in iter(lambda: process.stdout.readline(12000),''):
            try: lines.put_nowait(line)
            except queue.Full: dropped.set()
        process.stdout.close()
    thread=threading.Thread(target=reader,daemon=True); thread.start()
    started=time.monotonic(); output=[]; size=0
    try:
        while process.poll() is None or not lines.empty() or thread.is_alive():
            if owner is not None and process.poll() is not None:
                owner.close()  # Close descendants even when the direct child has exited.
            if cancel.is_set(): raise JobCancelled('Auftrag abgebrochen.')
            if time.monotonic()-started>timeout: raise TimeoutError('Auftrag überschreitet das Zeitlimit.')
            try:
                line=lines.get(timeout=.2)
                remaining=100000-size
                if remaining > 0:
                    part=line[:remaining]
                    on_line(part.rstrip())
                    output.append(part); size+=len(part)
                if len(line)>remaining: dropped.set()
            except queue.Empty: pass
        if dropped.is_set():
            marker='\n[Ausgabe gekürzt]\n'
            on_line(marker.strip())
            return process.returncode,''.join(output)[:100000-len(marker)]+marker
        return process.returncode,''.join(output)
    finally:
        if owner is not None:
            owner.close()
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        thread.join(timeout=2)


class JobRunner:
    ACTIONS={'refresh','hybrid_review','compare_reviews','scope_review','scope_compare','scope_plan','scope_patch','scope_route_b_review','scope_route_b_plan','stage_test','governance_report','live_start','live_capture','live_stop','model_check','radiworks_tests','hermes_check'}
    def __init__(self,app):
        self.app=app; self.pending=queue.Queue(); self.cancellations={}; self.lock=threading.Lock()
        self.thread=threading.Thread(target=self.worker,name='governor-worker',daemon=True)
        self.thread.start()

    def submit(self,action,project_id=None,supervisor=None,step_id=None,live_id=None,scope_kind=None,scope_id=None,candidate_id=None,stage_job_id=None,successor_consent_id=None,routine_note=None,critical_review=None):
        if routine_note is not None and (action != 'scope_patch' or not isinstance(routine_note,str) or not routine_note.strip() or len(routine_note)>1000):
            raise ValueError('Routinebestätigung nur für einen begrenzten Änderungsvorschlag zulässig.')
        if action not in self.ACTIONS: raise ValueError('Aktion nicht freigegeben.')
        route_b = action in ('scope_route_b_review','scope_route_b_plan')
        if critical_review is not None and (not route_b or type(critical_review) is not bool):
            raise ValueError('Kritischer Review nur als boolesche Route-B-Auswahl zulässig.')
        if successor_consent_id is not None and action!='scope_patch':raise ValueError('Nachfolgerzustimmung nur für eigenen Änderungsvorschlag.')
        if project_id and not action.startswith('live_'): self.app.observer.project(project_id)
        if action=='radiworks_tests' and project_id not in (None,'radiworks'): raise ValueError('Testaktion gilt ausschließlich für RadiWorks.')
        from .config import SUPERVISORS
        supervisor=supervisor or self.app.settings()['supervisor']
        if supervisor not in SUPERVISORS: raise ValueError('Ungültiger Supervisor.')
        if action=='radiworks_tests': self.app.observer.project('radiworks')
        request={}
        if action in ('scope_review','scope_compare','scope_plan','scope_patch','scope_route_b_review','scope_route_b_plan'):
            if project_id or (step_id and action!='scope_patch') or live_id: raise ValueError('Gruppenreview benötigt ausschließlich einen Geltungsbereich.')
            from .store import JobBusy
            if any(j['status'] in ('queued','running') for j in self.app.store.jobs()):
                raise JobBusy('Ein Auftrag läuft bereits.')
            context=self.app.scope_context(scope_kind,scope_id)
            if action in ('scope_plan','scope_route_b_plan') and not context['plan_ready']:
                raise ValueError('Vor der Matrixplanung muss jedes Mitglied vollständig aufgenommen sein.')
            request={'scope_kind':scope_kind,'scope_id':scope_id,'scope_hash':context['scope_hash']}
            if route_b: request['critical_review']=critical_review is True
            if action=='scope_patch':
                from .plans import PlanBook
                book=PlanBook(self.app.store); candidate=book.get(candidate_id)
                from .change_execution import resolve
                selected=dict(request,candidate_id=candidate_id,step_id=step_id)
                if successor_consent_id is not None:selected['successor_consent_id']=successor_consent_id
                resolve(self.app,selected,context)
                step=next((s for s in candidate['proposal']['steps'] if s['id']==step_id),None)
                if not step or step['action']!='change': raise ValueError('Änderungsvorschlag benötigt einen change-Schritt.')
                request.update(candidate_id=candidate_id,step_id=step_id)
                if routine_note is not None:
                    from .routing_policy import routine_step
                    from .job_routing import routine_origin
                    if (successor_consent_id is not None or self.app.settings().get('reasoning_mode','medium')!='auto'
                            or not routine_step(step,routine_note) or not routine_origin(self.app,candidate)):
                        raise ValueError('Routineauswahl benötigt Auto und einen bestätigten unabhängigen Dokumentationsschritt ohne Reparatur-/Rückfrageherkunft.')
                    request['routine_note']=routine_note.strip()
                if successor_consent_id is not None:request['successor_consent_id']=successor_consent_id
        elif scope_kind is not None or scope_id is not None:
            raise ValueError('Geltungsbereich nur für Gruppen-/Single-Review zulässig.')
        if action=='governance_report':
            observation=self.app.refresh(force_git=True)
            step=next((s for s in self.app.governance(observation)['steps'] if s['id']==step_id),None)
            if not step or not step.get('can_run'): raise ValueError('Dieser Berichtsschritt ist nicht ausführbar oder noch nicht erlaubt.')
            project_id=step['project_id']; request={'step_id':step_id,'evidence_hash':observation['evidence_hash']}
        elif step_id is not None and action!='scope_patch': raise ValueError('Arbeitsschritt nur für Governance-Berichte oder Änderungsvorschläge zulässig.')
        if candidate_id is not None and action!='scope_patch': raise ValueError('Plankandidat nur für Änderungsvorschläge zulässig.')
        if action=='stage_test':
            if not isinstance(stage_job_id,str) or not __import__('re').fullmatch(r'[a-f0-9]{32}',stage_job_id): raise ValueError('Staging-Auftrag fehlt.')
            source=self.app.store.job(stage_job_id)
            if source['action']!='scope_patch' or source['status']!='completed' or not source.get('result',{}).get('stage'):
                raise ValueError('Geprüfter Änderungsarbeitsbereich erforderlich.')
            request={'stage_job_id':stage_job_id}
        elif stage_job_id is not None: raise ValueError('Staging-Auftrag nur für begrenzte Tests zulässig.')
        if action=='live_start':
            if project_id not in self.app.config.get('live_views',{}): raise ValueError('Kein Live-Testziel für dieses Projekt konfiguriert.')
        if action in ('live_capture','live_stop'):
            if not isinstance(live_id,str) or not __import__('re').fullmatch(r'[a-f0-9]{32}',live_id): raise ValueError('Ungültige Live-ID.')
            request={'live_id':live_id}
        elif live_id is not None: raise ValueError('Live-ID nur für laufende Live-Tests.')
        with self.lock:
            if action in ('hybrid_review','compare_reviews','scope_review','scope_compare','scope_plan','scope_patch','scope_route_b_review','scope_route_b_plan','model_check','stage_test'):
                from .job_routing import snapshot, route_b_snapshot
                bound = route_b_snapshot(self.app,supervisor) if route_b else snapshot(self.app,supervisor)
                request={**(request or {}),'_model_routing':bound}
            job=self.app.store.create_job(action,project_id,request)
            self.cancellations[job['id']]=threading.Event()
            self.pending.put((job,supervisor))
        self.app.event('info','governor','Auftrag eingereiht: '+action,job['id'])
        return job

    def cancel(self,key):
        from .test_chain_store import TestChainJournal
        chain=TestChainJournal(self.app.store).find(key)
        if chain:return self.cancel_test_chain(chain['id'])
        from .sequence_store import SequenceJournal
        sequence=SequenceJournal(self.app.store).find(job_id=key)
        if sequence:return self.cancel_sequence(sequence['id'])
        with self.lock:
            event=self.cancellations.get(key)
            if self.app.store.job(key)['status']=='waiting_for_operator':
                self.app.questions.cancel(key)
            elif event: event.set()
            else: raise ValueError('Auftrag ist nicht aktiv.')
        self.app.event('warning','governor','Abbruch angefordert.',key)

    def submit_test_chain(self,values):
        from .test_chains import start
        with self.lock,self.app.store.lock:
            row,created=start(self.app,values)
            if created:
                job=self.app.store.job(row['current_job_id'])
                self.cancellations[job['id']]=threading.Event()
                self.pending.put((job,self.app.settings()['supervisor']))
        self.app.bump()
        return row

    def cancel_test_chain(self,key):
        from .test_chain_store import TestChainJournal
        with self.lock:
            row=TestChainJournal(self.app.store).cancel(key)
            event=self.cancellations.get(row['current_job_id'])
            if event:event.set()
        self.app.bump()
        return row

    def test_chain_child(self,job,supervisor,cancel):
        from .test_chain_store import TestChainJournal,ACTIVE
        from .test_chains import validate
        journal=TestChainJournal(self.app.store)
        with self.lock:
            row=journal.find(job['id'])
            if row['status'] not in ACTIVE:return
            journal.begin_child(row['id'],job['id'])
        self.app.bump();result={};current=False;status='completed'
        try:
            validate(self.app,journal.get(row['id']))
            if cancel.is_set():raise JobCancelled('Abbruch angefordert.')
            result=self.execute(job,supervisor,cancel)
            validate(self.app,journal.get(row['id']))
            current=True
            if result.get('success') is False:status='failed'
        except ValueError:
            result.update(success=False,stale=True,chain_blocked=True)
        except Exception:
            status='cancelled' if cancel.is_set() else 'failed'
            result.update(success=False,chain_error='Testkette nicht abgeschlossen.')
        with self.lock:
            if cancel.is_set():status='cancelled'
            row=journal.finish_child(row['id'],job['id'],status,result,evidence_current=current)
            if row['status']=='checking':
                try:
                    validate(self.app,row)
                    row=journal.advance(row['id'],evidence_current=True)
                except (ValueError,KeyError,TypeError,OSError):
                    row=journal.advance(row['id'],evidence_current=False)
            if row['status']=='testing':
                child=self.app.store.job(row['current_job_id'])
                self.cancellations[child['id']]=threading.Event()
                self.pending.put((child,supervisor))
        self.app.event('info','test-chain','Testkette: '+row['status'],job['id'])

    def submit_sequence(self,values):
        from .sequences import start
        with self.lock:
            row,created=start(self.app,values)
            if created:
                job=self.app.store.job(row['current_job_id'])
                self.cancellations[job['id']]=threading.Event()
                self.pending.put((job,row['binding']['routing']['supervisor']))
        self.app.bump()
        return row

    def cancel_sequence(self,key):
        from .sequence_store import SequenceJournal
        with self.lock:
            row=SequenceJournal(self.app.store).cancel(key)
            event=self.cancellations.get(row['current_job_id'])
            if event:event.set()
        self.app.bump()
        return row

    def sequence_child(self,job,supervisor,cancel):
        from .sequence_store import SequenceJournal,ACTIVE
        from .sequences import validate_child
        journal=SequenceJournal(self.app.store)
        with self.lock:
            row=journal.find(job_id=job['id'])
            if row['status'] not in ACTIVE:return
            journal.begin_child(row['id'],job['id'])
        self.app.bump();result={};current=False;status='completed'
        try:
            validate_child(self.app,job)
            if cancel.is_set():raise JobCancelled('Abbruch angefordert.')
            result=self.execute(job,supervisor,cancel)
            validate_child(self.app,job)
            current=True
            if result.get('success') is False:status='failed'
        except ValueError:
            result.update(sequence_blocked=True,sequence_reason='Gebundene Voraussetzungen nicht mehr gültig.')
            if job['action']=='stage_test':result.update(stale=True,verified=False)
        except Exception as exc:
            status='cancelled' if cancel.is_set() or isinstance(exc,JobCancelled) else 'failed'
            result.update(sequence_error='Prüfschritt nicht abgeschlossen; keine Folgeausführung.')
        with self.lock:
            if cancel.is_set():status='cancelled'
            row=journal.finish_child(row['id'],job['id'],status,result,evidence_current=current)
            if row['status']=='assessing':
                child=self.app.store.job(row['current_job_id'])
                self.cancellations[child['id']]=threading.Event()
                self.pending.put((child,row['binding']['routing']['supervisor']))
        self.app.event('info','sequence','Prüffolge: '+row['status'],job['id'])

    def submit_runtime(self, action, values):
        import re
        fields={'runtime_start': {'profile_id','profile_hash'}, 'runtime_stop': {'instance_id'}, 'runtime_check': {'instance_id'}}
        if action not in fields or not isinstance(values,dict) or set(values)!=fields[action]:
            raise ValueError('Ungültiger Laufzeitauftrag.')
        if action=='runtime_start':
            profile=self.app.runtime_profiles.profile()
            if values['profile_id']!=profile['id'] or values['profile_hash']!=profile['hash']:
                raise ValueError('Laufzeitprofil geändert oder unbekannt.')
        elif not isinstance(values['instance_id'],str) or not re.fullmatch('[a-f0-9]{32}',values['instance_id']):
            raise ValueError('Ungültige Laufzeitinstanz.')
        with self.lock:
            job=self.app.store.create_job(action,None,dict(values))
            self.cancellations[job['id']]=threading.Event()
            self.pending.put((job,self.app.settings()['supervisor']))
        self.app.event('info','operator','Expliziter lokaler Laufzeitauftrag: '+action,job['id'])
        return job

    def submit_repair_plan(self,values):
        from .repair_planning import submission,attempts
        if not isinstance(values,dict) or set(values)!={'diagnosis_job_id','note'}:
            raise ValueError('Reparaturplanung benötigt Fehlerdiagnose und ausdrückliche Begründung.')
        with self.lock:
            context,binding=submission(self.app,values['diagnosis_job_id'],values['note'])
            with self.app.store.db() as db:attempts(db,binding['candidate_id'],binding['step_id'])
            request=dict(scope_kind=context['review_scope']['kind'],scope_id=context['review_scope']['id'],scope_hash=context['scope_hash'],
                repair_diagnosis_job_id=values['diagnosis_job_id'],repair_note=values['note'],repair_binding=binding,
                repair_candidate_id=binding['candidate_id'],repair_step_id=binding['step_id'])
            from .job_routing import snapshot
            request['_model_routing']=snapshot(self.app,self.app.settings()['supervisor'])
            job=self.app.store.create_job('scope_plan',None,request)
            self.cancellations[job['id']]=threading.Event()
            self.pending.put((job,self.app.settings()['supervisor']))
        return job

    def submit_test_failure(self, values):
        from .test_failure import source_job
        if not isinstance(values,dict) or set(values)!={'job_id'}:
            raise ValueError('Fehlerprüfung benötigt ausschließlich den Testauftrag.')
        with self.lock:
            source_job(self.app,values['job_id'])
            job=self.app.store.create_job('plan_failure',None,dict(values))
            self.cancellations[job['id']]=threading.Event()
            self.pending.put((job,self.app.settings()['supervisor']))
        return job

    def submit_plan_test(self, values):
        from .plans import _id, _hash
        from .plan_tests import preflight, attempt_policy
        if not isinstance(values,dict) or set(values)!={'candidate_id','step_id','scope_hash','selection_id'}:
            raise ValueError('Testauftrag benötigt ausschließlich gebundene Planreferenzen.')
        for key,value in values.items(): (_hash if key=='scope_hash' else _id)(value)
        with self.lock:
            with self.app.store.db() as db:
                attempts=attempt_policy(db,values['candidate_id'],values['step_id'])
            if not attempts['allowed']: raise ValueError(attempts['reason'])
            preflight(self.app,values)
            job=self.app.store.create_job('plan_test',None,dict(values))
            self.cancellations[job['id']]=threading.Event()
            self.pending.put((job,self.app.settings()['supervisor']))
        return job

    def submit_pilot(self, action, values):
        import re
        fields = {'pilot_prepare': {'verified_test_job_id'},
                  'pilot_assess': {'verified_test_job_id'},
                  'pilot_verify': {'transaction_id'},
                  'pilot_complete': {'verified_job_id','observed_scope_hash','note'},
                  'pilot_transition': {'technical_receipt_id','observed_scope_hash','selection_id','note'},
                  'pilot_apply': {'proposal_id', 'proposal_hash'},
                  'pilot_rollback': {'transaction_id'}}
        if action not in fields or not isinstance(values,dict) or set(values)!=fields[action]:
            raise ValueError('Ungültige Pilotfreigabe.')
        for name,value in values.items():
            if name=='note':
                from .plans import _text
                _text(value,2000)
                continue
            length=64 if name in ('proposal_hash','observed_scope_hash') else 32
            if not isinstance(value,str) or re.fullmatch('[a-f0-9]{'+str(length)+'}',value) is None:
                raise ValueError('Ungültige gebundene Pilotreferenz.')
        with self.lock:
            job=self.app.store.create_job(action,None,dict(values))
            self.cancellations[job['id']]=threading.Event()
            self.pending.put((job,self.app.settings()['supervisor']))
        self.app.event('info','operator','Expliziter Pilotauftrag: '+action,job['id'])
        return job

    def answer_question(self,question_id,answer,expected_scope_hash):
        record=self.app.questions.get(question_id)
        context=self.app.scope_context(record['scope_kind'],record['scope_id'])
        with self.lock:
            if self.app.store.job(record['job_id'])['action']=='scope_patch':
                verify_question_sources(record.get('review_evidence',{}).get('question_source_binding'),context)
            value=self.app.questions.answer(question_id,answer,expected_scope_hash,context['scope_hash'])
            job=value['job']
            self.cancellations[job['id']]=threading.Event()
            self.pending.put((job,record['supervisor']))
        self.app.event('info','operator','Antwort gespeichert; Umfang wird vor Fortsetzung hybrid geprüft.',job['id'])
        return value

    def worker(self):
        while not self.app.stop_event.is_set():
            try: job,supervisor=self.pending.get(timeout=.5)
            except queue.Empty: continue
            key=job['id']; cancel=self.cancellations[key]
            try:
                from .test_chain_store import TestChainJournal
                if TestChainJournal(self.app.store).find(key):
                    self.test_chain_child(job,supervisor,cancel)
                    continue
                from .sequence_store import SequenceJournal
                if SequenceJournal(self.app.store).find(job_id=key):
                    self.sequence_child(job,supervisor,cancel)
                    continue
                if cancel.is_set(): raise JobCancelled('Vor Ausführung abgebrochen.')
                self.app.store.update_job(key,status='running',started_at=now()); self.app.bump()
                result=self.execute(job,supervisor,cancel)
                if cancel.is_set() and not ((job['action'] in ('pilot_apply','pilot_rollback') and
                        result.get('pilot_transaction',{}).get('status') in ('completed','rolled_back')) or
                        (job['action']=='pilot_complete' and result.get('technical_completion',{}).get('status')=='recorded') or
                        (job['action']=='pilot_transition' and result.get('change_chain',{}).get('completion',{}).get('status')=='accepted')):
                    if job['action']=='runtime_start' and result.get('runtime_instance'):
                        result['runtime_instance']=self.app.runtime_profiles.stop(result['runtime_instance']['id'])
                    self.app.store.update_job(key,result=result)
                    raise JobCancelled('Auftrag abgebrochen; vorhandene Prüfnachweise bleiben erhalten.')
                if result.get('operator_question') and not result.get('stale'):
                    with self.lock:
                        self.app.store.update_job(key,result=result)
                        if cancel.is_set(): raise JobCancelled('Vor der Rückfrage abgebrochen.')
                        if job['action']=='scope_patch':
                            fresh=self.app.scope_context(job['request']['scope_kind'],job['request']['scope_id'])
                            if fresh['scope_hash']!=result['scope_hash']:
                                raise ValueError('Quellen vor Rückfrage geändert; neuer Review erforderlich.')
                            verify_question_sources(result.get('question_source_binding'),fresh)
                        self.app.questions.ask(key,result['operator_question'],result['scope_hash'],
                            job['request']['scope_kind'],job['request']['scope_id'],supervisor,result=result)
                        self.app.event('info','operator','Wartet auf deine Antwort.',key)
                    continue
                status='completed'
                if isinstance(result,dict) and result.get('success') is False: status='failed'
                if result.get('requires_new_review'): status='review_required'
                self.app.store.update_job(key,status=status,ended_at=now(),result=result)
                self.app.event('info' if status=='completed' else 'error','governor','Auftrag '+status+'.',key)
            except Exception as e:
                status='cancelled' if cancel.is_set() or isinstance(e,JobCancelled) else 'failed'
                if job['action'] in ('pilot_apply','pilot_rollback'):
                    from .pilot_actions import recovery_receipt
                    try:
                        receipt=recovery_receipt(self.app,job)
                        if receipt: self.app.store.update_job(key,result=receipt)
                    except Exception:
                        pass  # Preserve the original failure; durable transaction snapshot remains available.
                # Adapter errors must be sanitized; never expose env or command arguments.
                message=str(e)[:1200]
                self.app.store.update_job(key,status=status,ended_at=now(),error=message)
                self.app.event('warning' if status=='cancelled' else 'error','governor',message,key)
            finally:
                with self.lock:
                    if self.cancellations.get(key) is cancel: self.cancellations.pop(key,None)
                self.app.bump(); self.pending.task_done()

    def execute(self,job,supervisor,cancel):
        key=job['id']; action=job['action']; app=self.app
        if action=='plan_failure':
            from .test_failure import diagnose
            return dict(success=True,test_failure=diagnose(app,job['request']['job_id'],cancel),
                        product_files_changed=False,approval_granted=False,
                        summary='Fehlernachweis geprüft; keine Reparatur oder Folgeausführung freigegeben.')
        if action=='plan_test':
            from .plan_tests import run
            return run(app,job,cancel,lambda line:app.event('info','plan-tests',line,key))
        if action in ('runtime_start','runtime_stop','runtime_check'):
            request=job['request']
            if action=='runtime_start':
                row=app.runtime_profiles.start(request['profile_id'],request['profile_hash'],cancel)
            elif action=='runtime_check':
                row=app.runtime_profiles.check(request['instance_id'],cancel)
            else:
                row=app.runtime_profiles.stop(request['instance_id'])
            return dict(success=row['last_check']['success'] if action=='runtime_check' else True,runtime_instance=row,approval_granted=False,
                        summary='Lokaler Laufzeittest: '+row['status'],product_execution=False)
        if action=='refresh': return app.refresh(force_git=True)
        if action in ('pilot_prepare','pilot_apply','pilot_rollback','pilot_assess','pilot_verify','pilot_complete','pilot_transition'):
            from . import pilot_actions
            req=job['request']
            if cancel.is_set(): raise JobCancelled('Pilotauftrag vor Beginn abgebrochen.')
            if action=='pilot_transition':
                from .change_chain import confirm
                receipt=confirm(app,req['technical_receipt_id'],req['observed_scope_hash'],req['selection_id'],req['note'],cancel)
                return dict(success=True,change_chain=receipt,approval_granted=False,product_files_changed=False,
                            summary='Quellenübergang und isolierter Änderungsabschluss bestätigt; keine automatische Ausführung.')
            if action=='pilot_complete':
                from .technical_completion import complete
                receipt=complete(app,req['verified_job_id'],req['observed_scope_hash'],req['note'],cancel)
                return dict(success=True,technical_completion=receipt,approval_granted=False,product_files_changed=False,
                            summary='Gebundener Übernahmeabschluss gespeichert; keine Plan- oder Folgefreigabe.')
            if action=='pilot_verify':
                from .pilot_verification import verify
                return dict(success=True,post_apply_verification=verify(app,req['transaction_id'],cancel),
                            approval_granted=False,product_files_changed=False,
                            summary='Nachprüfung der Übernahme abgeschlossen; kein neuer Funktionstest und keine Schrittfreigabe.')
            if action=='pilot_assess':
                return dict(success=True,pilot_assessment=pilot_actions.assess(app,req['verified_test_job_id']),
                            approval_granted=False,product_files_changed=False,
                            summary='Pilot-Nachweisprüfung abgeschlossen; Ergebnis ist keine Übernahmefreigabe.')
            if action=='pilot_prepare':
                proposal=pilot_actions.prepare(app,req['verified_test_job_id'])
                return dict(success=True,apply_proposal=proposal,approval_granted=False,
                            summary='Rückübernahme vorbereitet. Dateien und Diff vor gesonderter Freigabe prüfen.')
            if action=='pilot_apply':
                tx=pilot_actions.execute(app,req['proposal_id'],req['proposal_hash'],cancel)
                return dict(success=True,pilot_transaction=tx,product_files_changed=True,approval_granted=False,
                            summary='Pilotänderungen übernommen; neuer Review erforderlich.')
            tx=pilot_actions.rollback(app,req['transaction_id'],cancel)
            return dict(success=True,pilot_transaction=tx,product_files_changed=True,approval_granted=False,
                        summary='Pilotänderungen zurückgenommen; neuer Review erforderlich.')
        if action=='stage_test':
            from .job_routing import JobRouting
            from .sequence_store import SequenceJournal
            sequence=SequenceJournal(app.store).find(job_id=key)
            bound=sequence['binding']['routing'].get('model_policy') if sequence else None
            routing=JobRouting(app,job,supervisor,binding=bound)
            from .execution_workspace import WorkspaceStager
            from .staged_tests import run_staged_tests
            source=app.store.job(job['request']['stage_job_id'])
            stage=source['result']['stage']; req=source['request']
            context=app.scope_context(req['scope_kind'],req['scope_id'])
            if context['scope_hash']!=source['result']['scope_hash']:
                raise ValueError('Quellen oder Plangrundlage seit Änderungsvorschlag geändert.')
            from .plans import PlanBook
            from .execution_policy import require_staging_pilot,pilot_model_context
            book=PlanBook(app.store)
            candidate=book.get(req['candidate_id'])
            from .change_execution import resolve,require_latest_source,GuardedClient as SuccessorClient
            require_latest_source(app,req,source['id'])
            candidate,step,permission=resolve(app,req,context)
            stager=WorkspaceStager(app.config['data_dir'])
            result=run_staged_tests(stager,stage['id'],stage['manifest_hash'],cancel,
                lambda line:app.event('info','staged-tests',line,key))
            result.update(stage_job_id=source['id'],product_files_changed=False,apply_back_enabled=False,
                          scope_hash=context['scope_hash'],review_scope=context['review_scope'],verified=False,
                          plan_selection_id=permission['plan_selection_id'])
            if 'successor_binding' in permission:result['successor_binding']=permission['successor_binding']
            from .post_test_review import review_staged
            from .llm import ModelError
            client=RouterClient(app.config['router_url'],timeout=app.config['model_timeout'],api_key_env=app.config['router_api_key_env'],codex_auth_path=app.config.get('codex_auth_path') or None)
            try:
                from .execution_workspace import _read,_sha
                staged_sources=[]
                for item in stage['manifest']['files']:
                    raw=_read(stager.base/stage['id']/'files',item['path'])
                    if raw is None: raise ValueError('Gestagte Testquelle fehlt.')
                    staged_sources.append(dict(path=item['path'],content=raw.decode('utf-8'),sha256=_sha(raw)))
                stager.verify_source(stage['id'],stage['manifest_hash'])
                from .sequences import GuardedClient,validate_child
                validate_child(app,job)
                result['post_test_review']=review_staged(pilot_model_context(context,candidate,step,'post_test_review'),stage['manifest'],result,supervisor,SuccessorClient(GuardedClient(TrackedClient(client,app.store,key,routing=routing),app,job),app,req,source['id']),
                    cancel_event=cancel,staged_sources=staged_sources)
                stager.verify_source(stage['id'],stage['manifest_hash'])
                current=app.scope_context(req['scope_kind'],req['scope_id'])
                _,_,current_permission=resolve(app,req,current)
                require_latest_source(app,req,source['id'])
                result['stale']=(context['scope_hash']!=current['scope_hash']
                                 or current_permission.get('plan_selection_id') != result['plan_selection_id'])
                result['verified']=result['post_test_review']['verified'] and not result['stale']
            except (ModelError,ValueError,OSError):
                result.update(stale=True,post_test_review_error='Nachprüfung nicht abgeschlossen; tatsächlicher Testbericht bleibt erhalten.')
            result['success']=bool(result['success'] and result['verified'])
            return result
        if action.startswith('live_'):
            manager=app.live_manager()
            if action=='live_start':
                return manager.start(job['project_id'],app.config['live_views'][job['project_id']]['url'])
            if action=='live_stop': return manager.stop(job['request']['live_id'])
            result=manager.snapshot(job['request']['live_id'])
            import shutil
            original=Path(result['screenshot']); immutable=original.with_name('capture-'+key+'.png')
            shutil.copyfile(original,immutable)
            result['screenshot']=str(immutable)
            result['screenshot_url']='/api/live/screenshot?id='+key
            return result
        if action=='governance_report':
            import json
            observation=app.refresh(force_git=True)
            step_id=job['request']['step_id']
            matrix=app.governance(observation)
            step=next((s for s in matrix['steps'] if s['id']==step_id),None)
            if not step or not step.get('can_run') or observation['evidence_hash']!=job['request']['evidence_hash']:
                raise ValueError('Schritt oder Quellen seit Auftragserteilung geändert.')
            decisions=fingerprint(app.store.decisions())
            context=app.review_context(observation,job['project_id'])
            report={'step':step,'context':context,'matrix':matrix,
                    'source_ledger':[{k:p.get(k) for k in ('id','path','head','git_status','git_observed_at','memories','documented_statuses','warnings','evidence_hash')} for p in observation['projects']],
                    'scope':'Quellen- und Entscheidungsbericht; keine vollständige fachliche Gate-Abnahme.',
                    'approval_granted':False}
            folder=Path(app.config['data_dir'])/'runs'/key; folder.mkdir(parents=True)
            target=folder/'governance-report.json'
            target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            current=app.refresh(force_git=True)
            return {'success':True,'step_id':step_id,'report':str(target),'report_url':'/api/reports?id='+key,'report_sha256':__import__('hashlib').sha256(target.read_bytes()).hexdigest(),
                    'summary':'Quellengebundener Bericht erstellt; fachliche Prüfung und Abnahme bleiben getrennt.',
                    'evidence_hash':observation['evidence_hash'],'decision_hash':decisions,
                    'stale':evidence_stale(observation,current) or decisions!=fingerprint(app.store.decisions()),
                    'approval_granted':False}
        if action=='hermes_check':
            adapter=HermesAdapter(app.config['hermes_path'],workspace=app.config['data_dir'],
                                  codex_auth_path=app.config.get('codex_auth_path'),timeout=app.config['model_timeout'])
            result=adapter.check()
            if result['available']:
                result['isolation_probe']=adapter.review('Local zero-network capability check.',probe_only=True,cancel_event=cancel)
                result['no_tools_review_supported']=result['isolation_probe'].get('tool_count')==0
            result['success']=result['available'] and result['no_tools_review_supported']
            return result
        def event(value):
            if isinstance(value,dict): app.event('info',value.get('model') or 'models',value.get('message',str(value)),key)
            else: app.event('info','models',str(value),key)
        if action in ('hybrid_review','compare_reviews','scope_review','scope_compare','scope_plan','scope_patch','scope_route_b_review','scope_route_b_plan','model_check'):
            from .job_routing import JobRouting, RouteBRouting
            route_b = action in ('scope_route_b_review','scope_route_b_plan')
            routing=RouteBRouting(app,job,supervisor) if route_b else JobRouting(app,job,supervisor)
            client=RouterClient(app.config['router_url'],timeout=app.config['model_timeout'],api_key_env=app.config['router_api_key_env'],codex_auth_path=app.config.get('codex_auth_path') or None)
            if action=='model_check':
                return model_check(TrackedClient(client,app.store,key,routing=routing),on_event=event,cancel_event=cancel)
            if app.config['orchestrator_transport']=='hermes' and not route_b:
                router=client
                adapter=HermesAdapter(app.config['hermes_path'],workspace=app.config['data_dir'],
                                      codex_auth_path=app.config.get('codex_auth_path'),timeout=app.config['model_timeout'])
                class HybridTransport:
                    def prompt_limit(self,model):
                        return HERMES_PROMPT_CHARS if model=='gpt-5.6-terra' else ROUTER_PROMPT_CHARS
                    def call(self,model,prompt,**kwargs):
                        return adapter.review(prompt,model=model,**kwargs) if model=='gpt-5.6-terra' else router.call(model,prompt,**kwargs)
                client=HybridTransport()
            client=TrackedClient(client,app.store,key,routing=routing)
            if action=='scope_patch':
                from .change_execution import GuardedClient as SuccessorClient
                client=SuccessorClient(client,app,job['request'],job['id'])
            scoped=action in ('scope_review','scope_compare','scope_plan','scope_patch','scope_route_b_review','scope_route_b_plan')
            complete_memory=action in ('hybrid_review','compare_reviews','scope_review','scope_compare',
                                       'scope_plan','scope_route_b_review','scope_route_b_plan')
            if scoped:
                context=app.scope_context(job['request']['scope_kind'],job['request']['scope_id'])
                if context['scope_hash']!=job['request']['scope_hash']:
                    raise ValueError('Reviewkontext seit Auftragserteilung geändert.')
                if complete_memory:
                    from .model_memory import complete_memories
                    context=complete_memories(context,context['registry_projects'])
                if job['request'].get('repair_diagnosis_job_id'):
                    from .repair_planning import prepare,attempts
                    context,binding=prepare(app,job['request']['repair_diagnosis_job_id'],job['request']['repair_note'],cancel)
                    if binding!=job['request']['repair_binding']:raise ValueError('Reparaturgrundlage geändert.')
                    with app.store.db() as db:attempts(db,binding['candidate_id'],binding['step_id'],key)
                answers=app.questions.answers(key)
                answer_bindings=[]
                if answers and action=='scope_patch':
                    for answer in answers:
                        binding=app.questions.get(answer['id']).get('review_evidence',{}).get('question_source_binding')
                        verify_question_sources(binding,context)
                        answer_bindings.append(binding)
                if answers:
                    from .question_llm import assess_answer
                    answer_options={}
                    if action=='scope_patch':
                        from .plans import PlanBook
                        from .execution_policy import require_staging_pilot
                        from .execution_workspace import _root,_read,_sha
                        book=PlanBook(app.store); candidate=book.get(job['request']['candidate_id'])
                        from .change_execution import resolve
                        candidate,step,_=resolve(app,job['request'],context)
                        project=next(p for p in context['registry_projects'] if p['id']==step['project_id'])
                        source_root,_=_root(project['path']); exact=[]
                        for path in step['scope']:
                            raw=_read(source_root,path)
                            exact.append(dict(path=path,content=None if raw is None else raw.decode('utf-8'),sha256=None if raw is None else _sha(raw)))
                        for binding in answer_bindings: verify_question_sources(binding,context,exact)
                        answer_options=dict(step=step,sources=exact)
                    context['operator_answers']=answers
                    assessments=[]
                    for answer in answers:
                        assessment=assess_answer(context,answer,supervisor,client,on_event=event,cancel_event=cancel,**answer_options)
                        assessments.append(assessment)
                        if not assessment['within_scope']:
                            return dict(success=False,requires_new_review=True,answer_assessments=assessments,
                                operator_answers=answers,scope_hash=context['scope_hash'],review_scope=context['review_scope'],
                                approval_granted=False,summary='Antwort verändert den Umfang oder bleibt unklar; neue Prüfung erforderlich.')
                    context['operator_answers']=answers
                    context['answer_assessments']=assessments
            else:
                observation=app.refresh(force_git=True)
                context=app.review_context(observation,job['project_id'])
                context['verified_runs']=verified_runs(app.store.jobs_for_action('radiworks_tests'),observation)
                if complete_memory:
                    from .model_memory import complete_memories
                    context=complete_memories(context,app.config['projects'])
            if complete_memory:
                from .model_memory import stage_memories
                if route_b:
                    stage_models=('gpt-6-sol','gpt-6-luna')
                elif action in ('compare_reviews','scope_compare'):
                    stage_models=('gpt-5.6-terra','gpt-5.6-sol','gpt-6-astra')
                else:
                    stage_models=('gpt-5.6-terra',supervisor)
                context=stage_memories(
                    context,context['registry_projects'] if scoped else app.config['projects'],
                    client,stage_models,cache_dir=Path(app.config['data_dir'])/'artifacts'/'memory-index',
                    compact=action in ('scope_plan','scope_route_b_plan'),
                    on_event=event,cancel_event=cancel)
            if action=='scope_patch':
                from .plans import PlanBook
                from .execution_workspace import WorkspaceStager,_root,_read,_sha
                from .patch_llm import propose_patch
                book=PlanBook(app.store); candidate=book.get(job['request']['candidate_id'])
                from .execution_policy import require_staging_pilot,pilot_model_context
                from .change_execution import resolve
                candidate,step,permission=resolve(app,job['request'],context)
                step=next(s for s in candidate['proposal']['steps'] if s['id']==job['request']['step_id'])
                project=next(p for p in context['registry_projects'] if p['id']==step['project_id'])
                root,root_identity=_root(project['path']); sources=[]; hashes={}
                for path in step['scope']:
                    raw=_read(root,path); sha=None if raw is None else _sha(raw)
                    sources.append({'path':path,'content':None if raw is None else raw.decode('utf-8'),'sha256':sha}); hashes[path]=sha
                for binding in answer_bindings: verify_question_sources(binding,context,sources)
                routing.enable_routine(step)
                result=propose_patch(pilot_model_context(context,candidate,step,'patch_preflight'),step,sources,supervisor,client,on_event=event,cancel_event=cancel)
                resolve(app,job['request'],app.scope_context(job['request']['scope_kind'],job['request']['scope_id']))
                from .change_execution import require_latest_source
                require_latest_source(app,job['request'],job['id'])
                if result.get('operator_question'):
                    result['question_source_binding']=dict(root=str(root),root_identity=root_identity,hashes=hashes)
                review=result.get('review',{})
                if 'patch' in result and review['decision']=='REVIEW_ONLY' and not review['findings'] and not review['required_evidence']:
                    try:
                        result['stage']=WorkspaceStager(app.config['data_dir']).stage(root,step['scope'],result['patch']['files'],hashes)
                    except (ValueError,OSError):
                        result['stage_blocked']='Quellenkonflikt oder Staging nicht verfügbar; Modellbericht bleibt erhalten.'
                elif not result.get('operator_question'): result['stage_blocked']='Supervisor meldet offene Befunde oder Nachweise.'
                result.update(candidate_id=candidate['id'],step_id=step['id'],product_files_changed=False,apply_back_enabled=False)
            elif route_b:
                from .route_b import run
                result=run(context,client,plan=action=='scope_route_b_plan',
                           force_critical=job['request']['critical_review'],on_event=event,cancel_event=cancel)
            elif action=='scope_plan':
                from .planning_llm import propose_plan
                result=propose_plan(context,supervisor,client,on_event=event,cancel_event=cancel)
            elif action in ('compare_reviews','scope_compare'):
                from .llm import compare_reviews
                result=compare_reviews(context,client,on_event=event,cancel_event=cancel)
            else: result=hybrid_review(context,supervisor,client,on_event=event,cancel_event=cancel)
            if scoped:
                try:
                    current=app.scope_context(job['request']['scope_kind'],job['request']['scope_id'],wait_for_lock=120)
                    stale=context['scope_hash']!=current['scope_hash']
                    if action=='scope_patch' and 'successor_consent_id' in job['request']:
                        from .change_execution import resolve
                        resolve(app,job['request'],current)
                    if action=='scope_patch' and result.get('operator_question'):
                        verify_question_sources(result.get('question_source_binding'),current)
                except (ValueError,OSError):
                    stale=True
                result.update(scope_hash=context['scope_hash'],review_scope=context['review_scope'],
                              intake=context['intake'],plan_ready=context['plan_ready'],
                              intake_proposals=context.get('intake_proposals',[]),
                              stale=stale,freshness_requires_rescan=True)
            else:
                current=app.refresh(force_git=True)
                result['evidence_hash']=observation['evidence_hash']
                result['stale']=evidence_stale(observation,current) or context['decision_hash']!=fingerprint(app.store.decisions())
            result['decision_hash']=context['decision_hash']
            if complete_memory:
                result['memory_coverage']=context['memory_coverage']
                result['model_context_hash']=fingerprint(context)
            result['approval_granted']=False
            result['orchestrator_transport']='router' if route_b else app.config['orchestrator_transport']
            if scoped and context.get('operator_answers'):
                result['operator_answers']=context['operator_answers']
                result['answer_assessments']=context['answer_assessments']
            if result['stale']: result['warning']='Quellen inzwischen geändert. Review darf nicht zur Freigabe dienen.'
            if action in ('scope_plan','scope_route_b_plan') and 'proposal' in result and not result['stale']:
                from .plans import PlanBook
                try:
                    if job['request'].get('repair_diagnosis_job_id'):
                        from .repair_planning import prepare,validate
                        _,binding=prepare(app,job['request']['repair_diagnosis_job_id'],job['request']['repair_note'],cancel)
                        if binding!=job['request']['repair_binding']:raise ValueError('Reparaturgrundlage während Planung geändert.')
                        validate(result['proposal'],binding,job['request']['scope_id'])
                        result['repair_binding']=binding
                    result['candidate']=PlanBook(app.store).save_candidate(context,result['proposal'],result['review'],key)
                except ValueError as exc:
                    result['candidate_blocked']=str(exc)
            return result
        if action=='radiworks_tests':
            p=app.observer.project('radiworks'); engine=Path(p['path'])/'radiworks_port'/'engine'
            python=engine/'.venv'/'Scripts'/'python.exe'
            if not python.is_file(): raise ValueError('RadiWorks-Testumgebung fehlt: '+str(python))
            before=app.refresh(force_git=True)
            folder=Path(app.config['data_dir'])/'runs'/key; folder.mkdir(parents=True)
            env=os.environ.copy(); env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8',
                                             RADIOWORKS_HOME=str(folder/'home'),PYTHONPATH=str(engine/'src'))
            code,output=run_process([str(python),'-B','-m','pytest','-p','no:cacheprovider','-o','addopts=',
                                     '--basetemp',str(folder/'tmp'),'--junitxml',str(folder/'junit.xml'),'-q'],
                                    str(engine),env,cancel,lambda line: app.event('info','pytest',line,key),timeout=600)
            after=app.refresh(force_git=True)
            summary={}
            if (folder/'junit.xml').exists():
                tree=ET.parse(folder/'junit.xml').getroot()
                suites=[tree] if tree.tag=='testsuite' else list(tree.findall('testsuite'))
                summary={k:sum(int(s.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
            return dict(success=code==0,exit_code=code,output=output,summary=summary,
                        source_hash=before.get('source_hash',before['evidence_hash']),
                        evidence_hash=before['evidence_hash'],stale=evidence_stale(before,after),
                        approval_granted=False,junit=str(folder/'junit.xml'))
        raise ValueError('Unbekannte Aktion.')
