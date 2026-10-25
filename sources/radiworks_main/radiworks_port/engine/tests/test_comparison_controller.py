import importlib.util,json,time,copy,os
from pathlib import Path
import pytest
from radiworks.persistence import document_digest
from test_comparison_basis import fixture,SCOPE,module as basis


def controller_module():
    assert importlib.util.find_spec('radiworks.core.comparison_controller') is not None,'C2 controller missing'
    from radiworks.core import comparison_controller
    return comparison_controller


def make_input(tmp_path):
    m=basis();repo,rates,cases,case,session=fixture(tmp_path,count=2)
    from radiworks.core.analysis import RateObject
    session['analysisBaseline']['rateObjects']=[RateObject(energetic_value=100-i,name_or_rate=r.name).to_dict() for i,r in enumerate(rates)]
    source=m.make_source(session,m.capture_catalog(repo,'SYNTHETIC',rates),SCOPE)
    session['comparisonBasis']=m.source_reference(source)
    return m.build_comparison_input(source,session,case,SCOPE,page_start=0,weight='Normal',implementation_hash=controller_module().implementation_hash())


def wait_terminal(controller,identifier,timeout=30):
    limit=time.monotonic()+timeout
    while time.monotonic()<limit:
        record=controller.store.get(identifier)
        if record['status'] not in ('queued','running'):return record
        time.sleep(.05)
    raise AssertionError('comparison job did not terminate')


def test_controller_without_optional_dependencies_does_not_load_torch_or_create_job(tmp_path):
    m=controller_module();c=m.ComparisonController(tmp_path/'comparisons',SCOPE)
    c.start()
    try:
        assert c.capability()['configured'] is False
        with pytest.raises(m.ComparisonControllerError):c.request(make_input(tmp_path),'1'*32)
        assert c.store.list_for_case('0'*32)==[]
    finally:c.shutdown()
    assert not c._thread.is_alive()


def test_worker_protocol_is_bounded_and_fixed_error_not_traceback(tmp_path):
    m=controller_module()
    from radiworks.core.comparison_worker import execute
    assert execute({'unexpected':'synthetic-private'},m.implementation_hash())=={'error':'worker_protocol'}
    assert execute({'input':{},'implementationHash':'0'*64},m.implementation_hash())=={'error':'implementation_changed'}


@pytest.fixture
def deps():
    value=os.environ.get('RADIOWORKS_EXP1_TEST_DEPS')
    if not value:pytest.skip('explicit isolated CPU subprocess profile not configured')
    return Path(value)


def test_actual_cpu_process_preserves_input_and_returns_bound_result(tmp_path,deps):
    m=controller_module();payload=make_input(tmp_path);saved=copy.deepcopy(payload)
    c=m.ComparisonController(tmp_path/'comparisons',SCOPE,deps_dir=deps)
    c.start()
    try:
        job=c.request(payload,'2'*32);record=wait_terminal(c,job['id'])
        assert record['status']=='completed',record['error']
        assert record['result']['parameters']['candidateCount']==80000
        assert record['result']['inputRates']==payload['rates'] and payload==saved
        assert c.request(payload,'2'*32)['id']==job['id']
    finally:c.shutdown()


def test_explicit_cancel_owned_cpu_process_never_publishes_late_result(tmp_path,deps,monkeypatch):
    import subprocess,sys
    m=controller_module();payload=make_input(tmp_path)
    c=m.ComparisonController(tmp_path/'comparisons',SCOPE,deps_dir=deps)
    def sleeping_spawn():
        return subprocess.Popen([sys.executable,'-c','import sys,time;sys.stdin.read();time.sleep(60)'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    monkeypatch.setattr(c,'_spawn',sleeping_spawn)
    c.start()
    try:
        job=c.request(payload,'3'*32)
        limit=time.monotonic()+10
        while c._process is None and time.monotonic()<limit:time.sleep(.02)
        process=c._process;assert process is not None
        assert c.cancel(job['id'])['status']=='cancelled'
        assert wait_terminal(c,job['id'])['result'] is None
        process.wait(timeout=10);assert process.poll() is not None
    finally:c.shutdown()
    assert c.store.get(job['id'])['status']=='cancelled'


def test_shutdown_interrupts_pending_and_restart_does_not_replay(tmp_path,deps,monkeypatch):
    import subprocess,sys
    m=controller_module();payload=make_input(tmp_path)
    root=tmp_path/'comparisons';c=m.ComparisonController(root,SCOPE,deps_dir=deps)
    monkeypatch.setattr(c,'_spawn',lambda:subprocess.Popen([sys.executable,'-c','import sys,time;sys.stdin.read();time.sleep(60)'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)))
    c.start();job=c.request(payload,'4'*32)
    limit=time.monotonic()+10
    while c._process is None and time.monotonic()<limit:time.sleep(.02)
    assert c._process is not None;c.shutdown()
    assert c.store.get(job['id'])['status']=='interrupted'
    fresh=m.ComparisonController(root,SCOPE,deps_dir=deps);fresh.start()
    try:
        assert fresh.store.get(job['id'])['status']=='interrupted' and fresh._process is None
        retry=fresh.retry(job['id'],'5'*32)
        done=wait_terminal(fresh,retry['id']);assert done['status']=='completed',done['error']
        assert done['parentJobId']==job['id'] and done['input']==payload
    finally:fresh.shutdown()


def test_timeout_and_worker_start_errors_are_durable(tmp_path,deps,monkeypatch):
    import subprocess,sys
    m=controller_module();payload=make_input(tmp_path)
    c=m.ComparisonController(tmp_path/'comparisons',SCOPE,deps_dir=deps,worker_timeout=.1)
    monkeypatch.setattr(c,'_spawn',lambda:subprocess.Popen([sys.executable,'-c','import sys,time;sys.stdin.read();time.sleep(60)'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)))
    c.start()
    try:
        job=c.request(payload,'6'*32);done=wait_terminal(c,job['id']);assert done['error']['code']=='worker_timeout'
        def fail():raise OSError('synthetic PRIVATE path must not leak')
        monkeypatch.setattr(c,'_spawn',fail)
        other=c.request(payload,'7'*32);done=wait_terminal(c,other['id']);assert done['error']=={'code':'worker_start_failed'}
    finally:c.shutdown()

def test_fatal_dispatcher_error_disables_new_requests(tmp_path,monkeypatch):
    m=controller_module();payload=make_input(tmp_path)
    fake=tmp_path/'deps';(fake/'torch').mkdir(parents=True);(fake/'numpy').mkdir()
    (fake/'torch'/'__init__.py').write_text('');(fake/'numpy'/'__init__.py').write_text('')
    c=m.ComparisonController(tmp_path/'comparisons',SCOPE,deps_dir=fake);c.start()
    from radiworks.core.comparison_store import ComparisonStoreError
    original_get=c.store.get
    def broken(_):raise ComparisonStoreError('store_error')
    monkeypatch.setattr(c.store,'get',broken)
    try:
        c.request(payload,'8'*32)
        limit=time.monotonic()+5
        while c._thread.is_alive() and time.monotonic()<limit:time.sleep(.02)
        monkeypatch.setattr(c.store,'get',original_get)
        assert not c.capability()['configured']
        with pytest.raises(m.ComparisonControllerError):c.request(payload,'9'*32)
        assert len(c.store.list_for_case(payload['caseId']))==1
    finally:c.shutdown()
