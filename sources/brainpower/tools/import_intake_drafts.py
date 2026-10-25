"""Import audited local drafts through the guarded API; never confirm intake."""
import argparse
import hashlib
from http.cookiejar import CookieJar
import json
from pathlib import Path
import urllib.request
from urllib.parse import urlparse


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--origin',default='http://127.0.0.1:8787')
    p.add_argument('--drafts',required=True); p.add_argument('--hashes',required=True)
    p.add_argument('--group',default='aurelia-integration'); p.add_argument('--output',required=True)
    args=p.parse_args(); parsed=urlparse(args.origin)
    if parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or parsed.path not in ('','/') or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Nur lokaler Governor auf 127.0.0.1 erlaubt.')
    origin=args.origin.rstrip('/')
    drafts=json.loads(Path(args.drafts).read_text(encoding='utf-8-sig'))['projects']
    referenced={name for draft in drafts for name in draft['source_names']}
    ledger=json.loads(Path(args.hashes).read_text(encoding='utf-8-sig'))['sources']
    for source in (s for s in ledger if s['source_name'] in referenced):
        path=Path(source['path'])
        if path.stat().st_size>2*1024*1024 or hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']:
            raise ValueError('Auditquelle geändert: '+str(path))
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    def request(path,data=None):
        headers={} if data is None else {'Content-Type':'application/json','Origin':origin,'X-CSRF-Token':state['csrf_token']}
        req=urllib.request.Request(origin+path,data=None if data is None else json.dumps(data,ensure_ascii=False).encode('utf-8'),headers=headers)
        with opener.open(req,timeout=90) as response: return json.load(response)
    state=request('/api/state')
    from urllib.parse import urlencode
    route='/api/scope?'+urlencode({'kind':'group','id':args.group})
    context=request(route)
    if {d['project_id'] for d in drafts}!={p['id'] for p in context['projects']}:
        raise ValueError('Entwürfe decken die gewählte Gruppe nicht exakt ab.')
    available={(s['name'],s['sha256']) for row in context['projects'] for s in row['memories']}
    available.update((s['name'],s['sha256']) for s in context.get('governance_sources',[]))
    payloads=[]
    for draft in drafts:
        sources=[]
        for name in draft['source_names']:
            matches=[s for s in ledger if s['source_name']==name and (name,s['sha256']) in available]
            local=next(p for p in context['projects'] if p['id']==draft['project_id'])
            local_hashes={(m['name'],m['sha256']) for m in local['memories']}
            local_matches=[s for s in matches if (name,s['sha256']) in local_hashes]
            if local_matches: matches=local_matches
            if len(matches)!=1: raise ValueError('Quelle nicht eindeutig im aktuellen Umfang: '+name)
            sources.append(dict(name=name,sha256=matches[0]['sha256']))
        payloads.append(dict(scope_kind='group',scope_id=args.group,scope_hash=context['scope_hash'],project_id=draft['project_id'],fields=draft['fields'],sources=sources))
    receipts=[]
    for payload in payloads:
        fresh=request(route)
        if fresh['intake_source_hash']!=context['intake_source_hash']:
            raise ValueError('Gruppenquellen während des Imports geändert; verbleibende Entwürfe nicht gespeichert.')
        payload['scope_hash']=fresh['scope_hash']
        receipts.append(request('/api/intake/drafts',payload)['draft'])
    output={'kind':'local_unaccepted_intake_drafts','scope_hash':context['scope_hash'],'receipts':receipts,'approval_granted':False}
    Path(args.output).write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'saved':len(receipts),'accepted':False,'output':args.output}))


if __name__=='__main__': main()
