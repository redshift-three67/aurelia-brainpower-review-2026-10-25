import threading,time,io,subprocess
import pytest
from test_personal_controller import data,SCOPE
from test_comparison_controller import make_input
from test_comparison_basis import SCOPE as COMPARISON_SCOPE
from radiworks.core.personal_controller import PersonalController
from radiworks.core.personal_jobs import PersonalJobError
from radiworks.core.comparison_controller import ComparisonController
from radiworks.api.routes import STATE
from test_personal_api import client_context,ready,command
from test_comparison_api import original


def test_cpu_children_share_one_slot_until_process_is_reaped(tmp_path,monkeypatch):
    pdir=tmp_path/'p';pdir.mkdir();cdir=tmp_path/'c';cdir.mkdir()
    personal=PersonalController(pdir/'runtime',SCOPE);comparison=ComparisonController(cdir/'runtime',COMPARISON_SCOPE)
    budget=threading.Lock();personal._cpu_budget=comparison._cpu_budget=budget
    release=threading.Event();entered=threading.Event();second=threading.Event()
    class DelayedOutput(io.BytesIO):
        def readline(self, size=-1):
            entered.set()
            assert release.wait(5)
            return super().readline(size)
    class Process:
        def __init__(self):
            self.stdin=io.BytesIO()
            self.stdout=DelayedOutput(b"{}\n")
            self.stderr=io.BytesIO()
        returncode=1
        def poll(self):return 1 if release.is_set() else None
        def communicate(self,raw,timeout):entered.set();assert release.wait(5);return '{}',''
        def kill(self):release.set()
        def terminate(self):release.set()
        def wait(self,timeout):
            if not release.wait(timeout):raise subprocess.TimeoutExpired('synthetic-worker',timeout)
            return 1
    monkeypatch.setattr(personal,'capability',lambda:{'configured':True})
    monkeypatch.setattr(comparison,'_ready',lambda:None)
    monkeypatch.setattr(personal,'_spawn',Process)
    def spawn():second.set();return Process()
    monkeypatch.setattr(comparison,'_spawn',spawn)
    personal.start();comparison.start()
    try:
        personal.request(data(pdir,2),'1'*32);assert entered.wait(5)
        comparison.request(make_input(cdir),'2'*32)
        assert not second.wait(.2), 'Second CPU child started before first process reaped'
        release.set();assert second.wait(5)
    finally:release.set();personal.shutdown();comparison.shutdown()


def test_personal_admission_checks_comparisons_across_cases(home,monkeypatch):
    case,ref=client_context(home);ready(monkeypatch)
    monkeypatch.setattr(STATE.state.comparisons.store,'has_pending',lambda:True,raising=False)
    reply=home.post('/personal-analyses',json=command(case,ref))
    assert reply.status_code==409,reply.text
    assert STATE.state.personal.store.list()==[]


def test_comparison_create_and_retry_check_personal_jobs_across_cases(home,monkeypatch):
    case,ref=original(home);state=STATE.state
    monkeypatch.setattr(state.personal.store,'has_pending',lambda:True,raising=False)
    def forbidden(*args):raise AssertionError('Comparison CPU work admitted despite active personal job')
    monkeypatch.setattr(state.comparisons,'request',forbidden)
    body={'expected_case_ref':ref,'source_session_id':case['sessionList'][-1]['sessionId'],'request_id':'a'*32}
    assert home.post('/comparisons',json=body).status_code==409
    monkeypatch.setattr(state.comparisons.store,'get',lambda _: {'input':{'caseId':case['caseId']}})
    monkeypatch.setattr(state.comparisons,'retry',forbidden)
    assert home.post('/comparisons/'+'b'*32+'/retry',json={'expected_case_ref':ref,'request_id':'c'*32}).status_code==409


@pytest.mark.parametrize('kind',['personal','comparison'])
def test_terminate_failure_keeps_owned_dispatcher_until_confirmed_exit(tmp_path,monkeypatch,kind):
    payload=data(tmp_path,2) if kind=='personal' else make_input(tmp_path)
    cls=PersonalController if kind=='personal' else ComparisonController
    scope=SCOPE if kind=='personal' else COMPARISON_SCOPE
    ctrl=cls(tmp_path/'runtime',scope);entered=threading.Event();release=threading.Event();done=threading.Event();errors=[]
    class DelayedOutput(io.BytesIO):
        def readline(self, size=-1):
            entered.set()
            assert release.wait(5)
            return super().readline(size)
    class Process:
        def __init__(self):
            self.stdin=io.BytesIO()
            self.stdout=DelayedOutput(b"{}\n")
            self.stderr=io.BytesIO()
        returncode=1
        def poll(self):return 1 if release.is_set() else None
        def communicate(self,raw,timeout):entered.set();assert release.wait(5);return '{}',''
        def terminate(self):raise OSError('synthetic terminate failed')
        def kill(self):release.set()
        def wait(self,timeout):
            if not release.wait(timeout):raise subprocess.TimeoutExpired('synthetic-worker',timeout)
            return 1
    monkeypatch.setattr(ctrl,'_spawn',Process)
    if kind=='personal':monkeypatch.setattr(ctrl,'capability',lambda:{'configured':True})
    else:monkeypatch.setattr(ctrl,'_ready',lambda:None)
    ctrl.start()
    def stop():
        try:ctrl.shutdown()
        except Exception as exc:errors.append(exc)
        finally:done.set()
    thread=threading.Thread(target=stop)
    try:
        ctrl.request(payload,'7'*32);assert entered.wait(5);thread.start()
        assert not done.wait(.2), 'Shutdown released ownership before delayed worker ended'
        release.set();thread.join(5);assert done.is_set()
        assert not ctrl._thread.is_alive()
        if kind=='personal':
            assert errors and isinstance(errors[0],PersonalJobError)
            assert ctrl._stream is not None and not ctrl._stream.cleanup_confirmed
            assert not ctrl._cpu_budget.acquire(blocking=False)
        else:
            assert errors and isinstance(errors[0].__cause__,OSError)
    finally:
        release.set()
        thread.join(5) if thread.ident else None
        if kind=='personal' and ctrl._stream is not None and not ctrl._stream.cleanup_confirmed:
            with pytest.raises(PersonalJobError,match='shutdown'):ctrl.shutdown()
        else:ctrl.shutdown()


def test_failed_kill_still_drains_and_waits_for_owned_cpu_child():
    from radiworks.core.owned_cpu import reap_owned_process
    entered=threading.Event();release=threading.Event();done=threading.Event();errors=[]
    class Process:
        def poll(self):return 0 if release.is_set() else None
        def kill(self):raise OSError('synthetic kill failed')
        def communicate(self):entered.set();assert release.wait(5);return '', ''
        def wait(self):assert release.is_set();return 0
    def reap():
        try:reap_owned_process(Process())
        except Exception as exc:errors.append(exc)
        finally:done.set()
    thread=threading.Thread(target=reap);thread.start()
    try:
        assert entered.wait(2)
        assert not done.wait(.2)
        release.set();thread.join(5);assert done.is_set()
        assert errors and isinstance(errors[0].__cause__,OSError)
    finally:release.set();thread.join(5)


def test_unknown_poll_state_does_not_release_cpu_budget_before_exit():
    from radiworks.core.owned_cpu import reap_owned_process
    entered=threading.Event();release=threading.Event();done=threading.Event();budget=threading.Lock();errors=[]
    class Process:
        def poll(self):raise OSError('synthetic poll failed')
        def kill(self):pass
        def communicate(self):entered.set();assert release.wait(5);return '', ''
        def wait(self):assert release.is_set();return 0
    def reap():
        with budget:
            try:reap_owned_process(Process())
            except Exception as exc:errors.append(exc)
            finally:done.set()
    thread=threading.Thread(target=reap);thread.start()
    try:
        assert entered.wait(2)
        assert not done.wait(.2) and not budget.acquire(blocking=False)
        release.set();thread.join(5);assert done.is_set()
        assert errors and isinstance(errors[0].__cause__,OSError)
        assert budget.acquire(blocking=False);budget.release()
    finally:release.set();thread.join(5)
