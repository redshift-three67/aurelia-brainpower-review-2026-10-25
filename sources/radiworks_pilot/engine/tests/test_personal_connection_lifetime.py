import sqlite3
import pytest
from radiworks.core import personal_jobs as module
from radiworks.core.personal_jobs import PersonalJobStore
from radiworks.scope import ScopeContext

@pytest.mark.parametrize('rollback',[False,True])
def test_personal_transaction_closes_and_preserves_commit_rollback(tmp_path,monkeypatch,rollback):
    held=[]; original=sqlite3.connect
    def tracked(*args,**kwargs):
        connection=original(*args,**kwargs);held.append(connection);return connection
    monkeypatch.setattr(module.sqlite3,'connect',tracked)
    path=tmp_path/'synthetic.sqlite3'
    store=PersonalJobStore(path,ScopeContext('synthetic','client','job'))
    if rollback:
        with pytest.raises(RuntimeError,match='synthetic rollback'):
            with store._transaction() as db:
                db.execute("INSERT INTO personal_meta VALUES ('probe','written')")
                raise RuntimeError('synthetic rollback')
    else:
        with store._transaction() as db:db.execute("INSERT INTO personal_meta VALUES ('probe','written')")
    try:
        for connection in held:
            with pytest.raises(sqlite3.ProgrammingError,match='closed'):
                connection.execute('SELECT 1')
        check=original(path)
        try:assert check.execute("SELECT value FROM personal_meta WHERE key='probe'").fetchone()==(None if rollback else ('written',))
        finally:check.close()
        path.unlink()
        assert not path.exists()
    finally:
        for connection in held:connection.close()
