import pytest
from radiworks.api.routes import STATE

def test_invalid_settings_batch_does_not_partially_change_saved_values(home):
 before=home.get('/settings').json()
 r=home.put('/settings',json={'booleans':{'play.binaural.sound':True},'integers':{'broadcast.adjustment.maxFollowups':4}})
 assert r.status_code==422
 assert home.get('/settings').json()==before

def test_explicit_options_version_required_and_unsupported_version_rejected(home):
 assert home.put('/settings',json={'strings':{'broadcast.optionsVersion':'future'}}).status_code==422
 r=home.put('/settings',json={'strings':{'broadcast.optionsVersion':'options-v1'},'booleans':{'broadcast.single.rates.only':True}})
 assert r.status_code==200
 assert STATE.state.broadcast._capacity()==1

def test_preview_and_start_pin_duration_and_reject_changed_selection(home,monkeypatch):
 monkeypatch.setattr(STATE.state.broadcast,'_start_thread',lambda:None)
 r=home.post('/cases',json={'titleMode':'context','personalContext':{'firstName':'Synthetic'},'focus':'calm'});assert r.status_code==200
 a=home.post('/analysis',json={'database':'HOMEOPATHY_Test','seed':0,'mode':'seeded','max_hits':100});assert a.status_code==200
 state=STATE.state
 case=home.get('/cases/current').json();ref=home.get('/cases/current/ref').json()['ref'];session=case['sessionList'][-1];gv=session['analysisResult']['generalVitality']
 home.put('/settings',json={'strings':{'broadcast.optionsVersion':'options-v1'},'booleans':{'broadcast.delta.time':True}})
 body={'signature':'Synthetic Rate','seconds':gv+60,'multiplier':1,'expected_case_ref':ref,'expected_context_version':case['contextVersion'],'source_session_id':session['sessionId']}
 preview=home.post('/broadcast/preview',json=body);assert preview.status_code==200,preview.text
 assert preview.json()['executionPolicy']['seconds']==60
 home.put('/settings',json={'booleans':{'broadcast.delta.time':False}})
 denied=home.post('/broadcast',json={**body,'expected_preview_digest':preview.json()['previewDigest']});assert denied.status_code==409
 assert state.broadcast.queue_state()['queued']==[]
 fresh=home.post('/broadcast/preview',json=body).json();accepted=home.post('/broadcast',json={**body,'expected_preview_digest':fresh['previewDigest']});assert accepted.status_code==200
 assert accepted.json()['seconds']==gv+60


def test_preview_reads_settings_once_and_update_is_serialized(home,monkeypatch):
 import threading,time
 state=STATE.state;entered=threading.Event();release=threading.Event();updated=threading.Event()
 original=state.broadcast_policy
 def barrier(*args,**kwargs):
  assert kwargs["saved"]["strings"].get("broadcast.optionsVersion")=="options-v1"
  entered.set();assert release.wait(2);return original(*args,**kwargs)
 home.put('/settings',json={'strings':{'broadcast.optionsVersion':'options-v1'},'booleans':{'broadcast.single.rates.only':True}})
 monkeypatch.setattr(state,'broadcast_policy',barrier)
 replies=[]
 t=threading.Thread(target=lambda:replies.append(home.post('/broadcast/preview',json={'signature':'Synthetic','seconds':60})));t.start();assert entered.wait(1)
 def change():home.put('/settings',json={'booleans':{'broadcast.single.rates.only':False}});updated.set()
 u=threading.Thread(target=change);u.start();assert not updated.wait(.1)
 release.set();t.join(2);u.join(2)
 assert replies[0].status_code==200 and replies[0].json()['maxActive']==1 and updated.is_set()
