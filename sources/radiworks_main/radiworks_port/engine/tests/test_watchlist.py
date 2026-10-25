import copy, threading, time
import pytest
from radiworks.core.watchlist import WatchlistController, WatchlistError
from radiworks.entropy import EntropyProvider
from radiworks.scope import ScopeContext
from radiworks.core.personal_context import prepare_identity, ContextSnapshot

@pytest.fixture
def basis():
 c={"name":"Synthetic","caseId":"a"*32,"contextVersion":1};prepare_identity(c)
 return {"caseId":c["caseId"],"sessionId":"b"*32,"contextSnapshot":ContextSnapshot.capture(c,ScopeContext("synthetic","test","watch")).payload(),"sessionDigest":"c"*64,"indices":[0,2],"rates":["Synthetic A","Synthetic C"],"referenceGv":700,"mode":"seeded","seed":0}

def controller(tmp_path):
 return WatchlistController(tmp_path,ScopeContext(tenant_id="synthetic",client_id="test",job_id="watch"))

def wait_done(c,j):
 for _ in range(200):
  r=c.get(j)
  if r["status"] not in ("queued","running"):return r
  time.sleep(.01)
 raise AssertionError("watchlist did not finish")

def test_separate_results_and_own_rng_do_not_mutate_input(tmp_path,basis):
 c=controller(tmp_path);before=copy.deepcopy(basis)
 try:
  j=c.submit(basis,EntropyProvider(seed=0,mode="seeded"));r=wait_done(c,j["id"])
  assert r["status"]=="completed" and len(r["rows"])==2
  assert basis==before and r["rows"][1]["checkpoint"]["drawCount"]>r["rows"][0]["checkpoint"]["drawCount"]
  assert c.history("d"*32)==[]
 finally:c.shutdown()

def test_restart_marks_unfinished_interrupted_without_replaying(tmp_path,basis,monkeypatch):
 c=controller(tmp_path);monkeypatch.setattr(c,"_launch",lambda *a:None)
 j=c.submit(basis,EntropyProvider(seed=0,mode="seeded"))
 reopened=controller(tmp_path);assert reopened.get(j["id"])["status"]=="interrupted"
 reopened.shutdown()

def test_cancel_wins_over_inflight_draw_and_blocks_second_job(tmp_path,basis,monkeypatch):
 entered=threading.Event();release=threading.Event()
 def draw(_):entered.set();assert release.wait(2);return 800
 monkeypatch.setattr("radiworks.core.watchlist.check_general_vitality",draw)
 c=controller(tmp_path)
 try:
  j=c.submit(basis,EntropyProvider(seed=0,mode="seeded"));assert entered.wait(1)
  with pytest.raises(WatchlistError):c.submit(basis,EntropyProvider(seed=1,mode="seeded"))
  assert c.cancel(j["id"])["status"]=="cancelled"
  release.set();c.shutdown();assert c.get(j["id"])["rows"]==[]
 finally:release.set();c.shutdown()

def test_tampered_record_and_too_large_list_fail_closed(tmp_path,basis):
 c=controller(tmp_path)
 try:
  with pytest.raises(WatchlistError):c.submit({**basis,"indices":list(range(101)),"rates":["A"]*101},EntropyProvider(seed=0,mode="seeded"))
  j=c.submit(basis,EntropyProvider(seed=0,mode="seeded"));wait_done(c,j["id"])
  p=tmp_path/(j["id"]+".json");p.write_text(p.read_text().replace('"completed"','"running"'))
  with pytest.raises(WatchlistError):c.get(j["id"])
 finally:c.shutdown()


def test_commit_failure_does_not_publish_gv(tmp_path,basis):
 class BrokenCommit(EntropyProvider):
  def commit_journal(self):raise OSError('synthetic fsync failure')
 c=controller(tmp_path)
 try:
  j=c.submit(basis,BrokenCommit(seed=0,mode='seeded'));r=wait_done(c,j['id'])
  assert r['status']=='failed' and r['rows']==[] and r['error']=='OSError'
 finally:c.shutdown()

def test_shutdown_joins_worker_even_when_status_write_fails(tmp_path,basis,monkeypatch):
 entered=threading.Event();release=threading.Event();ended=threading.Event();errors=[]
 def draw(_):entered.set();assert release.wait(3);return 500
 monkeypatch.setattr('radiworks.core.watchlist.check_general_vitality',draw)
 c=controller(tmp_path);j=c.submit(basis,EntropyProvider(seed=0,mode='seeded'));assert entered.wait(1)
 original=c._write
 def fail_shutdown(record):
  if record['status']=='interrupted':raise OSError('synthetic status failure')
  return original(record)
 monkeypatch.setattr(c,'_write',fail_shutdown)
 def close():
  try:c.shutdown()
  except OSError as e:errors.append(e)
  finally:ended.set()
 t=threading.Thread(target=close);t.start()
 try:
  assert not ended.wait(.1), 'shutdown released before worker ended'
 finally:release.set();t.join(3)
 assert ended.is_set() and errors and not c._thread.is_alive()
