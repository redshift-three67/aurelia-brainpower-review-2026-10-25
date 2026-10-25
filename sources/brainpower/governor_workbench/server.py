"""Loopback HTTP application and low-frequency persistent observation loop."""
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import threading
import time
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
from . import __version__
from .config import SUPERVISORS
from .evidence import Observer, MemoryConflict, now, fingerprint
from .jobs import JobRunner
from .store import Store, JobBusy
from .registry import Registry


def recent_scope_observations(cache, signature, tick=None):
    """Expose only fresh, signature-bound scope hashes; never return source content."""
    tick = time.monotonic() if tick is None else tick
    latest = {}
    for key, entry in cache.copy().items():
        if not isinstance(key, tuple) or len(key) != 3 or not isinstance(entry, tuple) or len(entry) != 3:
            continue
        kind, scope_id, _ = key
        bound_signature, observed_tick, context = entry
        if (kind not in ('project', 'group') or not isinstance(scope_id, str)
                or bound_signature != signature or not isinstance(observed_tick, (int, float))
                or not 0 <= tick - observed_tick < 15 or not isinstance(context, dict)):
            continue
        scope_hash = context.get('scope_hash')
        if not isinstance(scope_hash, str) or not 1 <= len(scope_hash) <= 128:
            continue
        if (kind, scope_id) not in latest or observed_tick > latest[(kind, scope_id)][0]:
            latest[(kind, scope_id)] = (observed_tick, dict(kind=kind, id=scope_id,
                scope_hash=scope_hash, observed_at=context.get('observed_at'), stale=False))
    return [entry[1] for entry in latest.values()]


class Application:
    def __init__(self,config):
        self.config=config; self.stop_event=threading.Event(); self.lock=threading.RLock()
        self.revision=0; self.csrf=secrets.token_urlsafe(32); self.session=secrets.token_urlsafe(32)
        self.store=Store(Path(config['data_dir'])/'journal.db'); self.observer=Observer(config,self.stop_event)
        from .operator_questions import OperatorQuestions
        self.questions=OperatorQuestions(self.store)
        self.registry=Registry(self.store,config['projects'],legacy_egress_authorized=config.get('legacy_review_egress_authorized',False))
        self.scope_lock=threading.Lock(); self.scope_cache={}
        from .scopes import ScopeService
        self._scope_service=ScopeService(self.registry,self.config,self.stop_event)
        from .scope_monitor import ScopeMonitor
        self.scope_monitor=ScopeMonitor(self.registry,lambda kind,key:self.scope_context(kind,key,False,False))
        self.observation={'observed_at':None,'projects':[],'evidence_hash':''}
        self.source_evidence_hash=''
        self.last_error=None; self.health={'reachable':False,'url':config['router_url'],'error':'Noch nicht geprüft.'}
        self.last_health=0
        from .runtime_profiles import RuntimeProfiles
        self.runtime_profiles=RuntimeProfiles(self.store,config)
        self.runner=JobRunner(self)
        self.monitor_thread=threading.Thread(target=self.monitor,name='governor-observer',daemon=True)
        self.monitor_thread.start()
        self.event('info','governor','Governor gestartet. Beobachtung aktiv; Produktfreigaben bleiben gesondert.')

    def bump(self):
        with self.lock: self.revision+=1

    def event(self,level,source,message,job_id=None):
        self.store.event(level,source,message,job_id); self.bump()

    def settings(self):
        saved=self.store.settings()
        return dict(supervisor=saved.get('supervisor',self.config['supervisor']),
                    reasoning_mode=saved.get('reasoning_mode',self.config.get('reasoning_mode','medium')),
                    monitor_enabled=saved.get('monitor_enabled',True),auto_review=saved.get('auto_review',False))

    def update_settings(self,values):
        if not isinstance(values,dict) or not set(values)<={'supervisor','monitor_enabled','auto_review','reasoning_mode'}:
            raise ValueError('Unbekannte Einstellung.')
        if 'supervisor' in values and values['supervisor'] not in SUPERVISORS: raise ValueError('Supervisor nicht unterstützt.')
        if 'reasoning_mode' in values:
            from .routing_policy import validate_mode
            validate_mode(values['reasoning_mode'])
        for key in ('monitor_enabled','auto_review'):
            if key in values and type(values[key]) is not bool: raise ValueError('Einstellung muss boolesch sein.')
        if values.get('auto_review') is True and not self.settings()['auto_review']:
            with self.lock: source_hash=self.observation['evidence_hash']
            self.store.set_setting('_last_auto_evidence',fingerprint({'sources':source_hash,'decisions':self.store.decisions()}))
        for key,value in values.items(): self.store.set_setting(key,value)
        self.event('info','governor','Einstellungen aktualisiert: '+', '.join(values))

    def refresh(self,force_git=False):
        observation=self.observer.scan(force_git)
        with self.store.lock,self.lock:
            self.source_evidence_hash=observation['evidence_hash']
            self.bind_planning(observation)
            changed=observation['evidence_hash'] != self.observation['evidence_hash']
            self.observation=observation; self.last_error=None; self.revision+=1
        if changed: self.event('info','observer','Neue Beobachtung: Quellstand oder Git-Evidenz geändert.')
        return copy.deepcopy(observation)

    def bind_planning(self,observation):
        # Caller holds store.lock then self.lock, matching decision writes.
        from .governance import STEPS
        observation['source_hash']=fingerprint({'sources':self.source_evidence_hash,'planned_projects':self.store.planned()})
        observation['evidence_hash']=fingerprint({'sources':observation['source_hash'],'rules':STEPS})

    def refresh_planned(self):
        with self.store.lock,self.lock:
            observation=copy.deepcopy(self.observation)
            self.bind_planning(observation)
            self.observation=observation;self.revision+=1
        self.event('info','observer','Planungsstand aktualisiert; Quellenbeobachtung unverändert.')
        return copy.deepcopy(observation)

    def governance(self,observation=None,decisions=None,jobs=None):
        from .governance import build_matrix
        if observation is None:
            with self.lock: observation=copy.deepcopy(self.observation)
        decisions=self.store.decisions() if decisions is None else decisions
        observation['decision_hash']=fingerprint(decisions)
        return build_matrix(observation,decisions,self.store.jobs(200) if jobs is None else jobs,self.store.planned())

    def live_manager(self):
        from .live_view import LiveViews
        with self.lock:
            if not hasattr(self,'_live_manager'): self._live_manager=LiveViews(self.config)
            return self._live_manager

    def live_state(self):
        targets=[dict(project_id=key,name=next((p['name'] for p in self.config['projects'] if p['id']==key),key),url=value['url'])
                 for key,value in self.config.get('live_views',{}).items()]
        sessions=self._live_manager.state() if hasattr(self,'_live_manager') else []
        return {'targets':targets,'sessions':sessions}

    def add_decision(self,data):
        with self.store.lock:
            return self._add_decision(data)

    def _add_decision(self,data):
        from .governance import validate_decision
        observation=self.refresh(force_git=True)
        if data.get('kind')=='accept' and data.get('evidence_hash')!=observation['evidence_hash']:
            raise MemoryConflict('Quellen geändert. Aktuellen Stand prüfen und Abnahme erneut begründen.')
        item=validate_decision(data,observation)
        if item['kind']=='accept':
            step=next(s for s in self.governance(observation)['steps'] if s['id']==item['step_id'])
            if not step.get('acceptance_eligible'):
                raise ValueError('Abnahme benötigt aktuelle Quellen, Erlaubnis und erfüllte Voraussetzungen.')
        saved=self.store.add_decision(item)
        self.event('info','operator','Betreiberentscheidung: '+item['step_id']+' / '+item['kind'])
        return saved

    def review_context(self,observation,project_id=None):
        context=self.observer.context(observation,project_id)
        all_decisions=self.store.decisions()
        context['operator_decisions']=all_decisions[-100:]
        context['operator_decisions_truncated']=len(all_decisions)>100
        context['decision_hash']=fingerprint(all_decisions)
        matrix=self.governance(observation,all_decisions)
        context['governor_matrix']={k:matrix[k] for k in ('steps','projects','next_steps')}
        context['planned_projects']=self.store.planned()
        # The UI/API review request itself is explicit scoped authority, not product approval.
        context['current_request']={'authorized':True,'scope':'read_only_advisory',
                                    'product_implementation_authorized':False,
                                    'historical_pause_superseded_for_this_review':True}
        return context

    def scope_context(self,kind,key,require_egress=True,force=True,wait_for_lock=0):
        if kind not in ('group','project') or not isinstance(key,str) or not 1<=len(key)<=64:
            raise ValueError('Ungültiger Geltungsbereich.')
        cache_key=(kind,key,require_egress)
        signature=fingerprint({'registry':self.registry.list_projects(),'decisions':self.store.decisions(),'planned':self.store.planned()})
        if not self.scope_lock.acquire(timeout=wait_for_lock): raise JobBusy('Eine Kontextprüfung läuft bereits.')
        try:
            cached=self.scope_cache.get(cache_key)
            if not force and cached and cached[0]==signature and time.monotonic()-cached[1]<15:
                return copy.deepcopy(cached[2])
            result=self._scope_service.context(kind,key,require_egress,force_git=force)
            if len(self.scope_cache)>=100: self.scope_cache.clear()
            self.scope_cache[cache_key]=(signature,time.monotonic(),result)
            return copy.deepcopy(result)
        finally: self.scope_lock.release()

    def monitor(self):
        while not self.stop_event.is_set():
            try:
                if self.settings()['monitor_enabled']:
                    observation=self.refresh()
                    self.auto_review(observation)
                    self.scope_monitor.tick()
                if time.monotonic()-self.last_health>=60:
                    reachable=False; error=None
                    try:
                        url=self.config['router_url'].removesuffix('/v1').rstrip('/')+'/health'
                        with urlopen(url,timeout=3) as r: reachable=r.status==200
                    except Exception: error='Router nicht erreichbar; Inferenz separat prüfen.'
                    with self.lock:
                        self.health={'reachable':reachable,'url':self.config['router_url'],'error':error}
                        self.last_health=time.monotonic(); self.revision+=1
            except Exception as e:
                with self.lock: self.last_error=str(e)[:500]
                self.event('error','observer','Beobachtung fehlgeschlagen: '+str(e)[:500])
            self.stop_event.wait(self.config['monitor_interval'])

    def auto_review(self,observation):
        if not observation.get('evidence_complete'): return
        review_hash=fingerprint({'sources':observation['evidence_hash'],'decisions':self.store.decisions()})
        saved=self.store.settings(); last=saved.get('_last_auto_evidence')
        if not last:
            self.store.set_setting('_last_auto_evidence',review_hash); return
        if not self.settings()['auto_review'] or last==review_hash: return
        stamp=time.time(); day=now()[:10]
        count=saved.get('_auto_count',0) if saved.get('_auto_day')==day else 0
        if stamp-saved.get('_auto_time',0)<self.config['auto_review_cooldown'] or count>=self.config['auto_review_daily_limit']: return
        try: self.runner.submit('hybrid_review')
        except JobBusy: return
        # Failed calls count too: the limit prevents retry/cost storms.
        for k,v in {'_last_auto_evidence':review_hash,'_auto_time':stamp,'_auto_day':day,'_auto_count':count+1}.items():
            self.store.set_setting(k,v)

    def state(self):
        with self.lock:
            observation=copy.deepcopy(self.observation); health=dict(self.health); error=self.last_error
        settings=self.settings()
        from .sequence_store import SequenceJournal
        sequences=SequenceJournal(self.store).list()
        from .test_chain_store import TestChainJournal
        test_chains=TestChainJournal(self.store).list()
        from .pilot_actions import transaction_snapshot
        pilot_transactions=transaction_snapshot(self)
        from .registry import INITIAL_ROLES
        pilot_roots={os.path.normcase(os.path.abspath(p)) for p in self.config.get('staging_pilot_roots',[])}
        pilot_ids=[p['id'] for p in self.registry.list_projects() if not p['archived'] and not p['group_id']
                   and p['id'] not in INITIAL_ROLES and os.path.normcase(p['path']) in pilot_roots]
        jobs=self.store.jobs()
        decisions=self.store.decisions(); decision_hash=fingerprint(decisions)
        for job in jobs:
            result=job.get('result')
            if isinstance(result,dict) and result.get('scope_hash'):
                scope=result.get('review_scope',{})
                cached=[item for cache_key,item in self.scope_cache.copy().items()
                        if cache_key[:2]==(scope.get('kind'),scope.get('id')) and time.monotonic()-item[1]<15]
                latest=max(cached,key=lambda item:item[1])[2] if cached else None
                result['freshness']='recently_observed' if latest else 'unknown_requires_rescan'
                result['stale']=bool(result.get('stale') or latest is None or latest['scope_hash']!=result['scope_hash'])
                if 'verified' in result:
                    result['historical_verified']=result['verified']
                    result['verified']=bool(result['verified'] and not result['stale'])
            if isinstance(result,dict) and result.get('evidence_hash'):
                if job['action']=='radiworks_tests':
                    matches=result.get('source_hash',result['evidence_hash'])==observation.get('source_hash',observation['evidence_hash'])
                else: matches=result['evidence_hash']==observation['evidence_hash']
                result['stale']=result.get('stale',False) or not matches or not observation.get('evidence_complete')
                if result.get('decision_hash') and result['decision_hash']!=decision_hash: result['stale']=True
        # UI truncation must not give the main matrix a different history
        # window from scoped reviews and action eligibility checks.
        governor=self.governance(observation,decisions)
        derived={p['id']:p for p in governor['projects']}
        for p in observation['projects']:
            p['documented_status']=p['status']; p['documented_next_step']=p['next_step']
            if p['id'] in derived:
                p.update({k:derived[p['id']][k] for k in ('status','next_step','gate')})
                p['status_basis']='Berechnet aus Arbeitsschritten, Quellenstand und Betreiberentscheidungen.'
        registry_projects=self.registry.list_projects(); registry_groups=self.registry.list_groups()
        planned_projects=self.store.planned()
        scope_signature=fingerprint({'registry':registry_projects,'decisions':decisions,'planned':planned_projects})
        recent_scopes=recent_scope_observations(self.scope_cache,scope_signature)
        return dict(version=__version__,csrf_token=self.csrf,observed_at=observation['observed_at'],
                    execution_capabilities={'pilot_project_ids':pilot_ids,'isolated_pilot_apply':True,'product_apply_back':False,'dependent_steps':False},
                    monitor=dict(enabled=settings['monitor_enabled'],interval_seconds=self.config['monitor_interval'],
                                 git_interval_seconds=self.config['git_interval'],last_error=error),
                    runtime=dict(router=health,hermes=dict(available=Path(self.config['hermes_path']).is_file(),path=self.config['hermes_path']),
                                 models=dict(orchestrator=self.config['orchestrator'],supervisor=settings['supervisor'],reasoning=settings['reasoning_mode'],transport=self.config['orchestrator_transport'],options=list(SUPERVISORS))),
                    projects=observation['projects'],jobs=jobs,events=self.store.events(),settings=settings,sequences=sequences,test_chains=test_chains,
                    operator_questions=self.questions.list(status='pending'),
                    pilot_transactions=pilot_transactions,runtime_profiles=self.runtime_profiles.state(),
                    planned_projects=planned_projects,governor=governor,decisions=decisions,
                    evidence_hash=observation['evidence_hash'],decision_hash=decision_hash,live_views=self.live_state(),
                    registry={'projects':registry_projects,'groups':registry_groups,
                              'observations':self.scope_monitor.state(),
                              'recent_scope_observations':recent_scopes})

    def close(self):
        self.stop_event.set()
        with self.runner.lock:
            for event in self.runner.cancellations.values(): event.set()
        self.monitor_thread.join(timeout=5); self.runner.thread.join(timeout=12)
        self.runtime_profiles.close()
        if hasattr(self,'_live_manager'): self._live_manager.close()


class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'

    @property
    def app(self): return self.server.app

    def log_message(self,*args): pass

    def origin(self): return 'http://'+self.headers.get('Host','')

    def valid_host(self):
        port=self.server.server_port
        return self.headers.get('Host') in (f'127.0.0.1:{port}',f'localhost:{port}')

    def session_ok(self):
        from http.cookies import SimpleCookie
        cookies=SimpleCookie()
        try: cookies.load(self.headers.get('Cookie',''))
        except Exception: return False
        name='governor_session_'+str(self.server.server_port)
        return name in cookies and secrets.compare_digest(cookies[name].value,self.app.session)

    def headers_base(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")

    def reply(self,data,status=200,content_type='application/json; charset=utf-8',set_session=False):
        body=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode('utf-8')
        self.send_response(status); self.headers_base(); self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(body)))
        if set_session: self.send_header('Set-Cookie','governor_session_'+str(self.server.server_port)+'='+self.app.session+'; HttpOnly; SameSite=Strict; Path=/')
        try:
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError): pass

    def guard(self,write=False):
        if not self.valid_host() or self.headers.get('Sec-Fetch-Site')=='cross-site':
            if write:self.discard_rejected_body()
            self.reply({'error':'Lokaler Zugriff erforderlich.'},403); return False
        if write:
            if not self.session_ok() or self.headers.get('Origin')!=self.origin() or not secrets.compare_digest(self.headers.get('X-CSRF-Token',''),self.app.csrf):
                self.discard_rejected_body()
                self.reply({'error':'Sitzung oder Origin ungültig. Seite neu laden.'},403); return False
        return True

    def discard_rejected_body(self):
        # Unread request bytes can reset a closing TCP connection before its 403 is received.
        self.close_connection=True
        try:remaining=int(self.headers.get('Content-Length','0'))
        except ValueError:return
        if not 0<remaining<=1048576 or self.headers.get('Transfer-Encoding'):return
        previous=self.connection.gettimeout();deadline=time.monotonic()+.25
        try:
            while remaining and time.monotonic()<deadline:
                self.connection.settimeout(max(.001,deadline-time.monotonic()))
                chunk=self.rfile.read1(min(65536,remaining))
                if not chunk:break
                remaining-=len(chunk)
        except OSError:
            pass  # Partial rejected bodies are not parsed or executed; never wait indefinitely.
        finally:
            self.connection.settimeout(previous)

    def do_GET(self):
        if not self.guard(): return
        parsed=urlparse(self.path)
        try:
            if parsed.path in ('/','/index.html','/app.js','/theme.js','/style.css'):
                name='index.html' if parsed.path=='/' else parsed.path[1:]
                raw=(Path(__file__).parent/'static'/name).read_bytes()
                mime={'index.html':'text/html','app.js':'text/javascript','theme.js':'text/javascript','style.css':'text/css'}[name]
                return self.reply(raw,content_type=mime+'; charset=utf-8',set_session=name=='index.html')
            if parsed.path=='/health': return self.reply({'ok':True,'service':'governor-workbench','version':__version__})
            if parsed.path=='/api/state': return self.reply(self.app.state(),set_session=True)
            if not self.session_ok(): return self.reply({'error':'Sitzung erforderlich.'},403)
            if parsed.path=='/api/memory':
                q=parse_qs(parsed.query)
                return self.reply(self.app.observer.read_memory(q.get('project',[''])[0],q.get('name',[''])[0]))
            if parsed.path=='/api/scope':
                q=parse_qs(parsed.query)
                fresh=q.get('fresh',['0'])
                if fresh not in (['0'],['1']): raise ValueError('Ungültiger Umfangsabruf.')
                return self.reply(self.app.scope_context(q.get('kind',[''])[0],q.get('id',[''])[0],False,fresh==['1']))
            if parsed.path=='/api/plans':
                from .plans import PlanBook
                q=parse_qs(parsed.query)
                return self.reply({'plans':PlanBook(self.app.store).list(q.get('kind',[''])[0],q.get('id',[''])[0])})
            if parsed.path in ('/api/intake/drafts','/api/strategies'):
                q=parse_qs(parsed.query); kind=q.get('kind',[''])[0]; key=q.get('id',[''])[0]
                context=self.app.scope_context(kind,key,False)
                if parsed.path=='/api/intake/drafts':
                    from .intake_drafts import IntakeDrafts
                    return self.reply({'drafts':IntakeDrafts(self.app.store).list(context),'scope_hash':context['scope_hash']})
                from .strategies import StrategyBook
                revisions=StrategyBook(self.app.store).list(kind,key)
                for index,item in enumerate(revisions):
                    item['current']=index==0 and item['scope_hash']==context['scope_hash'] and context['plan_ready']
                return self.reply({'revisions':revisions,'scope_hash':context['scope_hash']})
            if parsed.path=='/api/events': return self.sse()
            if parsed.path=='/api/reports':
                key=parse_qs(parsed.query).get('id',[''])[0]
                if not __import__('re').fullmatch(r'[a-f0-9]{32}',key): raise ValueError('Ungültige Berichts-ID.')
                job=self.app.store.job(key)
                if job['action']!='governance_report' or job['status']!='completed': raise ValueError('Kein abgeschlossener Bericht.')
                target=(Path(self.app.config['data_dir'])/'runs'/key/'governance-report.json').resolve()
                if target.stat().st_size>2*1024*1024: raise ValueError('Bericht zu groß.')
                return self.reply(target.read_bytes())
            if parsed.path=='/api/live/screenshot':
                key=parse_qs(parsed.query).get('id',[''])[0]
                if not __import__('re').fullmatch(r'[a-f0-9]{32}',key): raise ValueError('Ungültige Live-ID.')
                job=self.app.store.job(key)
                if job['action']!='live_capture' or job['status']!='completed' or not job.get('result'): raise ValueError('Kein Screenshot vorhanden.')
                screenshot=Path(job['result']['screenshot']).resolve()
                if not screenshot.is_relative_to((Path(self.app.config['data_dir'])/'live'/job['result']['id']).resolve()): raise ValueError('Ungültiger Screenshotpfad.')
                if screenshot.stat().st_size>20*1024*1024: raise ValueError('Screenshot zu groß.')
                return self.reply(screenshot.read_bytes(),content_type='image/png')
            self.reply({'error':'Nicht gefunden.'},404)
        except JobBusy as e: self.reply({'error':str(e)},409)
        except (ValueError,UnicodeError) as e: self.reply({'error':str(e)},400)
        except OSError: self.reply({'error':'Lokale Datei nicht verfügbar.'},500)

    def do_POST(self):
        if not self.guard(write=True): self.close_connection=True; return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=1048576: raise ValueError('Ungültige Anfragegröße.')
            if self.headers.get('Content-Type','').split(';')[0]!='application/json': raise ValueError('JSON erforderlich.')
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise ValueError('JSON-Objekt erforderlich.')
            path=urlparse(self.path).path
            if path=='/api/change-chains/preview':
                from .change_chain_preview import preview
                if set(data)!={'candidate_id','step_ids'}:raise ValueError('Änderungsvorschau benötigt nur Kandidat und Schritte.')
                return self.reply(preview(self.app,data['candidate_id'],data['step_ids']))
            if path.startswith('/api/change-chains/'):
                from .change_api import dispatch
                value,status=dispatch(self.app,path.removeprefix('/api/change-chains/'),data)
                if status==202 or path.rsplit('/',1)[-1] in ('begin','acknowledge','confirm'):self.app.bump()
                return self.reply(value,status)
            if path=='/api/test-chains/preview':
                from .test_chains import preview
                if set(data)!={'candidate_id','step_ids'}:raise ValueError('Testkettenvorschau benötigt nur Kandidat und Testschritte.')
                return self.reply(preview(self.app,data['candidate_id'],data['step_ids']))
            if path=='/api/test-chains/start':
                return self.reply({'chain':self.app.runner.submit_test_chain(data)},202)
            if path=='/api/test-chains/cancel':
                if set(data)!={'chain_id'}:raise ValueError('Abbruch benötigt ausschließlich die Testketten-ID.')
                return self.reply({'chain':self.app.runner.cancel_test_chain(data['chain_id'])})
            if path=='/api/sequences/start':
                return self.reply({'sequence':self.app.runner.submit_sequence(data)},202)
            if path=='/api/sequences/cancel':
                if set(data)!={'sequence_id'}:raise ValueError('Abbruch benötigt ausschließlich die Prüffolgen-ID.')
                return self.reply({'sequence':self.app.runner.cancel_sequence(data['sequence_id'])})
            if path=='/api/sequences/preview':
                from .sequences import preview
                if set(data)!={'stage_job_id'}:
                    raise ValueError('Vorschau benötigt ausschließlich den Änderungsvorschlagsauftrag.')
                return self.reply(preview(self.app,data['stage_job_id']))
            if path=='/api/strategies/adopt':
                from .strategies import StrategyBook
                if set(data)!={'scope_kind','scope_id','candidate_id','scope_hash','expected_previous_id'}:
                    raise ValueError('Ungültige Strategieübernahmefelder.')
                with self.app.store.lock:
                    context=self.app.scope_context(data['scope_kind'],data['scope_id'],False)
                    item=StrategyBook(self.app.store).adopt(data['candidate_id'],data['scope_hash'],data['expected_previous_id'],context)
                self.app.event('info','strategy','Strategierevision übernommen; keine Produktfreigabe oder Ausführung.')
                return self.reply({'revision':item},201)
            if path=='/api/intake/drafts':
                from .intake_drafts import IntakeDrafts
                if set(data)!={'scope_kind','scope_id','scope_hash','project_id','fields','sources'}:
                    raise ValueError('Ungültige Aufnahmeentwurfsfelder.')
                context=self.app.scope_context(data['scope_kind'],data['scope_id'],False)
                item=IntakeDrafts(self.app.store).save(context,data['scope_hash'],data['project_id'],data['fields'],data['sources'])
                self.app.scope_cache.clear()
                self.app.event('info','intake','Lokaler Aufnahmeentwurf gespeichert; Betreiberbestätigung steht aus.')
                return self.reply({'draft':item},201)
            if path=='/api/questions/answer':
                if set(data)!={'question_id','answer','scope_hash'}: raise ValueError('Ungültige Antwortfelder.')
                return self.reply(self.app.runner.answer_question(data['question_id'],data['answer'],data['scope_hash']),202)
            if path=='/api/plans/approve':
                from .plans import PlanBook
                context=self.app.scope_context(data.get('scope_kind'),data.get('scope_id'),False)
                item=PlanBook(self.app.store).approve(data.get('candidate_id'),data.get('scope_hash'),context,
                    data.get('selected_step_ids'),data.get('mode','single'))
                self.app.event('info','plans','Planauswahl bestätigt; keine Produktausführung gestartet.')
                return self.reply({'approval':item},201)
            if path=='/api/plans/test':
                return self.reply({'job':self.app.runner.submit_plan_test(data)},202)
            if path=='/api/plans/test-failure':
                return self.reply({'job':self.app.runner.submit_test_failure(data)},202)
            if path=='/api/plans/repair':
                return self.reply({'job':self.app.runner.submit_repair_plan(data)},202)
            if path=='/api/plans/dependencies':
                if set(data)!={'scope_kind','scope_id','candidate_id'}:
                    raise ValueError('Ungültige Felder für die Vorgängerprüfung.')
                from .plans import PlanBook
                context=self.app.scope_context(data['scope_kind'],data['scope_id'],False,force=True)
                return self.reply({'report':PlanBook(self.app.store,self.app.config).dependency_report(data['candidate_id'],context)})
            if path=='/api/plans/complete-step':
                if set(data)!={'scope_kind','scope_id','candidate_id','step_id','scope_hash','selection_id','note'}:
                    raise ValueError('Ungültige Felder für die fachliche Abnahme.')
                from .plans import PlanBook
                context=self.app.scope_context(data['scope_kind'],data['scope_id'],False,force=True)
                receipt=PlanBook(self.app.store,self.app.config).complete_step(data['candidate_id'],data['step_id'],context,data['scope_hash'],data['selection_id'],data['note'])
                return self.reply({'receipt':receipt},201)
            if path=='/api/plans/withdraw-completion':
                if set(data)!={'candidate_id','step_id','expected_receipt_id','note'}:
                    raise ValueError('Ungültige Felder für die Abnahmerücknahme.')
                from .plans import PlanBook
                receipt=PlanBook(self.app.store).withdraw_completion(data['candidate_id'],data['step_id'],data['expected_receipt_id'],data['note'])
                return self.reply({'receipt':receipt},201)
            if path=='/api/intake':
                from .intake import Intake
                with self.app.store.lock:
                    context=self.app.scope_context(data.get('scope_kind'),data.get('scope_id'),False)
                    item=Intake(self.app.store).accept(context,data.get('scope_hash'),data.get('project_id'),data.get('fields'))
                    self.app.scope_cache.clear()
                self.app.event('info','intake','Projektaufnahme bestätigt; keine Produktfreigabe.')
                return self.reply({'intake':item},201)
            if path=='/api/vault/sources':
                from .vault import Vault
                item=Vault(self.app.registry,self.app.config['data_dir'],self.app.config.get('vault_root') or None).map_source(
                    data.get('scope_kind'),data.get('scope_id'),data.get('path'),data.get('model_egress',False))
                self.app.scope_cache.clear()
                self.app.event('info','vault','Explizite Vault-Quelle zugeordnet; Inhalt bleibt Referenzmaterial.')
                return self.reply({'source':item},201)
            if path.startswith('/api/registry/'):
                with self.app.store.lock:
                    if any(j['status'] in ('queued','running') for j in self.app.store.jobs()):
                        raise JobBusy('Registeränderung erst nach Abschluss des Auftrags.')
                    if path=='/api/registry/projects':
                        item=self.app.registry.register(data.get('name'),data.get('path'),requirements=data.get('requirements',''),model_egress=data.get('model_egress',False))
                        result={'project':item}
                    elif path=='/api/registry/groups':
                        result={'group':self.app.registry.create_group(data.get('name'))}
                    elif path=='/api/registry/memberships':
                        result={'project':self.app.registry.assign(data.get('project_id'),data.get('group_id'),data.get('role','member'))}
                        from .memory_registry import RegistryMemory
                        try:
                            result['memory']=RegistryMemory(self.app.registry,self.app.config['data_dir']).provision(data.get('project_id'))
                        except (ValueError,OSError) as exc:
                            result['memory_warning']='Zugehörigkeit gespeichert; Gedächtniszuordnung offen: '+str(exc)
                    elif path=='/api/registry/memory':
                        from .memory_registry import RegistryMemory
                        result={'memory':RegistryMemory(self.app.registry,self.app.config['data_dir']).provision(data.get('project_id'))}
                    elif path=='/api/registry/archive':
                        result={'project':self.app.registry.archive(data.get('project_id'))}
                    elif path=='/api/registry/policy':
                        if not set(data)<={'project_id','requirements','model_egress'}: raise ValueError('Unbekannte Projektoption.')
                        result={'project':self.app.registry.set_project_policy(data.get('project_id'),**{k:v for k,v in data.items() if k!='project_id'})}
                    else: raise ValueError('Unbekannte Registeraktion.')
                self.app.event('info','registry','Projektregister aktualisiert: '+path.rsplit('/',1)[-1])
                return self.reply(result,201)
            if path=='/api/actions':
                job=self.app.runner.submit(data.get('action'),data.get('project_id'),data.get('supervisor'),data.get('step_id'),data.get('live_id'),data.get('scope_kind'),data.get('scope_id'),data.get('candidate_id'),data.get('stage_job_id'),routine_note=data.get('routine_note'),critical_review=data.get('critical_review'))
                return self.reply({'job':job},202)
            if path in ('/api/pilot/prepare','/api/pilot/apply','/api/pilot/rollback','/api/pilot/assess','/api/pilot/verify','/api/pilot/complete','/api/pilot/transition'):
                job=self.app.runner.submit_pilot('pilot_'+path.rsplit('/',1)[-1],data)
                return self.reply({'job':job},202)
            if path in ('/api/runtime/start','/api/runtime/stop','/api/runtime/check'):
                job=self.app.runner.submit_runtime('runtime_'+path.rsplit('/',1)[-1],data)
                return self.reply({'job':job},202)
            if path=='/api/decisions':
                return self.reply({'decision':self.app.add_decision(data)},201)
            if path=='/api/jobs/cancel':
                self.app.runner.cancel(data.get('id')); return self.reply({'ok':True})
            if path=='/api/settings':
                self.app.update_settings(data); return self.reply(self.app.settings())
            if path=='/api/memory':
                result=self.app.observer.save_memory(data.get('project'),data.get('name'),data.get('content'),data.get('expected_sha256'))
                self.app.event('info','memory','Gedächtnis gespeichert und gesichert: '+data['project']+'/'+data['name'])
                self.app.refresh(); return self.reply(result)
            if path=='/api/projects':
                known=[p['id'] for p in self.app.config['projects']+self.app.store.planned()]
                if len(known)>=50: raise ValueError('Maximal 50 Projekte.')
                if any(p['name'].casefold()==str(data.get('name','')).strip().casefold() for p in self.app.config['projects']):
                    raise ValueError('Projektname existiert bereits.')
                item=self.app.store.add_project(data.get('name'),data.get('description',''),data.get('depends_on',[]),known)
                self.app.refresh_planned(); return self.reply({'project':item},201)
            if path=='/api/shutdown':
                self.reply({'ok':True}); threading.Thread(target=self.server.shutdown,daemon=True).start(); return
            self.reply({'error':'Aktion nicht gefunden.'},404)
        except (MemoryConflict,JobBusy) as e: self.reply({'error':str(e)},409)
        except (ValueError,TypeError,KeyError) as e: self.reply({'error':str(e)[:500]},400)
        except OSError: self.reply({'error':'Lokaler Schreibzugriff fehlgeschlagen; Ergebnis prüfen.'},500)

    def sse(self):
        # Bound connections so idle tabs cannot accumulate worker threads indefinitely.
        if not self.server.stream_slots.acquire(blocking=False): return self.reply({'error':'Zu viele Live-Verbindungen.'},429)
        try:
            self.send_response(200); self.headers_base(); self.send_header('Content-Type','text/event-stream')
            self.send_header('Connection','close'); self.end_headers(); self.close_connection=True
            revision=-1; started=time.monotonic()
            while not self.app.stop_event.is_set() and time.monotonic()-started<90:
                if revision!=self.app.revision:
                    revision=self.app.revision
                    content='event: state\ndata: '+json.dumps(self.app.state(),ensure_ascii=False)+'\n\n'
                else: content=': heartbeat\n\n'
                self.wfile.write(content.encode('utf-8')); self.wfile.flush()
                self.app.stop_event.wait(2)
        except (BrokenPipeError,ConnectionResetError,OSError): pass
        finally: self.server.stream_slots.release()


def make_server(config,port=None):
    server=ThreadingHTTPServer(('127.0.0.1',config['port'] if port is None else port),Handler)
    server.daemon_threads=True; server.stream_slots=threading.BoundedSemaphore(8)
    try: server.app=Application(config)
    except BaseException: server.server_close(); raise
    return server
