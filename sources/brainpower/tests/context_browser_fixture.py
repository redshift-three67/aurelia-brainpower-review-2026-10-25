"""Loopback-only synthetic UI fixture. No storage, model calls or real projects."""
import json
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

STATIC = Path(__file__).resolve().parents[1] / 'governor_workbench' / 'static'
PROJECTS = [dict(id=i, name=f'Fixture {i.upper()}', path=f'SYNTHETIC/{i}', archived=False,
                 group_id='g' if i in ('c','d') else None, role='member', model_egress=True,
                 memory_provisioning='ready', requirements=f'Only {i}') for i in ('a','b','c','d')]
JOBS = []

def state():
    return dict(projects=[], jobs=JOBS, events=[], planned_projects=[], csrf_token='fixture-only',
                settings=dict(supervisor='gpt-6-astra', reasoning_mode='medium', auto_review=False),
                monitor=dict(enabled=False), runtime=dict(models=dict(options=['gpt-6-astra'])),
                registry=dict(projects=PROJECTS, groups=[dict(id='g',name='Fixture Gruppe',archived=False)], observations=[]))

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(STATIC),**kwargs)

    def reply(self, value, status=200):
        body=json.dumps(value).encode()
        self.send_response(status);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)

    def do_GET(self):
        parsed=urlparse(self.path);q=parse_qs(parsed.query)
        if parsed.path=='/api/state':return self.reply(state())
        if parsed.path=='/api/events':
            body=('event: state\ndata: '+json.dumps(state())+'\n\n').encode()
            self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers();self.wfile.write(body);return
        if parsed.path=='/api/scope':
            kind=q.get('kind',[''])[0];scope=q.get('id',[''])[0]
            members=[p for p in PROJECTS if p['group_id']==scope] if kind=='group' else [p for p in PROJECTS if p['id']==scope]
            if not members:return self.reply({'error':'Unknown synthetic scope'},400)
            # Allows a real browser to demonstrate a late A response after selecting B.
            if scope=='a':time.sleep(1)
            return self.reply(dict(scope_hash=f'{kind}-{scope}',plan_ready=scope!='a',vault_sources=[],intake=[dict(project_id=p['id'],memories_present=True,evidence_complete=True,missing_proofs=[]) for p in members]))
        if parsed.path=='/api/plans':
            scope=q.get('id',[''])[0];kind=q.get('kind',[''])[0]
            plan=dict(id='fixture-plan',version=1,current=True,scope_kind=kind,scope_id=scope,scope_hash=f'{kind}-{scope}',
                      proposal=dict(summary='Synthetischer Prüfplan',steps=[dict(id='read',title='Anforderungen prüfen',project_id=scope,priority=1,depends_on=[],scope=['note.md'],tests=['Sichtprüfung'],rationale='Fixture',action='review')]),review={})
            return self.reply({'plans':[plan]})
        if parsed.path=='/api/strategies':return self.reply({'scope_hash':f"{q.get('kind',[''])[0]}-{q.get('id',[''])[0]}",'revisions':[]})
        if parsed.path.startswith('/api/'):return self.reply({'error':'Fixture route disabled'},404)
        return super().do_GET()

    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))))
        if self.path!='/api/actions' or body.get('action')!='scope_review' or body.get('scope_id') not in ('a','b','c','d','g'):
            return self.reply({'error':'Fixture mutation disabled'},403)
        job=dict(id=f'fixture-{len(JOBS)+1}',action='scope_review',request=body,status='running',created_at='2026-09-24T14:00:00+02:00',result=None)
        JOBS.append(job);return self.reply({'job':job},202)

    def log_message(self,*args):pass

if __name__=='__main__':
    ThreadingHTTPServer(('127.0.0.1',8794),Handler).serve_forever()
