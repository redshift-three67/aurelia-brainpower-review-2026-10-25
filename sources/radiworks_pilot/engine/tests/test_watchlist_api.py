import time
from radiworks.api.routes import STATE

def prepared(home):
 assert home.post('/cases',json={'name':'Synthetic Watch','focus':'calm'}).status_code==200
 assert home.post('/analysis',json={'database':'HOMEOPATHY_Test','seed':0,'mode':'seeded','max_hits':100}).status_code==200
 c=home.get('/cases/current').json();ref=home.get('/cases/current/ref').json()['ref']
 return {'source_session_id':c['sessionList'][-1]['sessionId'],'indices':[0,1],'seed':0,'mode':'seeded','expected_case_ref':ref,'expected_context_version':c['contextVersion']}

def test_watchlist_is_separate_and_stale_session_is_rejected(home):
 body=prepared(home);before=home.get('/cases/current').json()
 p=home.post('/watchlist/preview',json=body);assert p.status_code==200,p.text
 assert p.json()['count']==2
 start=home.post('/watchlist',json={**body,'expected_preview_digest':p.json()['previewDigest'],'request_id':'a'*32});assert start.status_code==200,start.text
 job=start.json()['id']
 for _ in range(200):
  r=home.get('/watchlist/'+job).json()
  if r['status'] not in ('queued','running'):break
  time.sleep(.01)
 assert r['status']=='completed' and len(r['rows'])==2
 assert home.get('/cases/current').json()==before
 assert STATE.state.broadcast.queue_state()['queued']==[]
 assert home.post('/watchlist',json={**body,'expected_preview_digest':p.json()['previewDigest'],'request_id':'a'*32}).json()['id']==job
 assert home.post('/cases',json={'name':'Another Synthetic'}).status_code==200
 assert home.get('/watchlist/'+job).status_code==409
 assert home.post('/watchlist',json={**body,'expected_preview_digest':p.json()['previewDigest'],'request_id':'b'*32}).status_code==409

def test_watchlist_rejects_duplicate_indices_and_unconfirmed_start(home):
 body=prepared(home)
 assert home.post('/watchlist/preview',json={**body,'indices':[0,0]}).status_code==422
 assert home.post('/watchlist',json={**body,'request_id':'a'*32}).status_code==409
 assert home.post('/watchlist/preview',json={**body,'indices':[999]}).status_code==422
