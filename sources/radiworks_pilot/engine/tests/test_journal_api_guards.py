"""API persistence boundaries must remain closed after journal/algorithm faults."""
import copy
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from radiworks.api import routes
from radiworks.core.analysis import AnalysisResult,RateObject
from radiworks.entropy import RandomOrgSource
from radiworks.main import create_app
from radiworks import entropy_journal


class FaultingWriter:
    def __init__(self,handle,phase):self.handle,self.phase,self.close_calls=handle,phase,0
    def __getattr__(self,name):return getattr(self.handle,name)
    def __enter__(self):return self
    def __exit__(self,*args):return self.handle.__exit__(*args)
    def write(self,data):
        if self.phase=='write':raise OSError('synthetic write failure')
        return self.handle.write(data)
    def flush(self):
        if self.phase=='flush':raise OSError('synthetic flush failure')
        return self.handle.flush()
    def close(self):
        self.close_calls+=1
        if self.close_calls==1 and self.phase.endswith('close-before'):
            raise OSError('synthetic close failure before actual release')
        self.handle.close()
        if self.close_calls==1 and self.phase.endswith('close-after'):
            raise OSError('synthetic close failure after actual release')


@pytest.mark.parametrize('phase',['write','flush','fsync','algorithm','scope-close-before','scope-close-after','commit-close-before','commit-close-after'])
def test_fault_does_not_publish_successful_case_or_draft_and_releases_file(tmp_path,monkeypatch,phase):
    monkeypatch.setenv('RADIOWORKS_JOURNAL_KEY',Fernet.generate_key().decode())
    data=tmp_path/'data';data.mkdir();(data/'SAFE.txt').write_text('Synthetic safe rate\n')
    app=create_app(base_dir=tmp_path,data_dir=data,cases_dir=tmp_path/'cases',drafts_dir=tmp_path/'drafts')
    state=app.state.radiworks_state;state.random_org=RandomOrgSource(http_get=None)
    journals=[];create=state.create_entropy_journal
    def capture():
        journal=create();journals.append(journal);return journal
    monkeypatch.setattr(state,'create_entropy_journal',capture)
    def kernel(rates,entropy,**kwargs):
        entropy.get_integer(0,9)
        if phase=='algorithm':raise RuntimeError('synthetic algorithm interruption')
        return AnalysisResult(rate_objects=[RateObject(name_or_rate='Synthetic safe rate',energetic_value=10)])
    monkeypatch.setattr(routes,'analyse_rate_list',kernel)
    with TestClient(app,raise_server_exceptions=False) as client:
        created=client.post('/cases',json={'name':'Artificial Fault Test','description':'Synthetic only'})
        assert created.status_code==200
        before=copy.deepcopy(state.case_store.current)
        saved={p.name:p.read_bytes() for p in (tmp_path/'cases').glob('*.json')}
        original_open=Path.open
        def fault_open(path,mode='r',*args,**kwargs):
            handle=original_open(path,mode,*args,**kwargs)
            target='r+b' if phase.startswith('commit-') else 'ab'
            return FaultingWriter(handle,phase) if str(path).endswith('.journal') and mode==target else handle
        if phase in ('write','flush') or '-close-' in phase:monkeypatch.setattr(Path,'open',fault_open)
        if phase=='fsync':
            def fail(_):raise OSError('synthetic fsync failure')
            monkeypatch.setattr(entropy_journal.os,'fsync',fail)
        response=client.post('/analysis',json={'database':'SAFE','mode':'stochastic','max_hits':100})
        assert response.status_code==500
        assert state.case_store.current==before
        assert {p.name:p.read_bytes() for p in (tmp_path/'cases').glob('*.json')}==saved
        assert not list((tmp_path/'drafts').glob('*.json'))
        assert len(journals)==1
        # Windows rename/delete exercises actual handle release rather than internals.
        path=journals[0].path
        if path.exists():
            moved=path.with_suffix('.renamed');path.rename(moved);moved.unlink()
