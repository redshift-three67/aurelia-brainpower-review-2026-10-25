"""M4 durable full-catalog jobs, cancellation and restart are separate from EXP1."""
import copy
import json
import pytest
from test_personal_analysis import basis, freeze, SCOPE
from radiworks.core.personal_jobs import PersonalJobStore, PersonalJobError


def payload(tmp_path, count=24):
    return freeze(*basis(tmp_path,count))


def block(data, start, count):
    return [{"inputIndex":i,"rate":data["rates"][i],"score":i/100.,"intensity":1.,"matrix":[[i%10]*12 for _ in range(12)]} for i in range(start,start+count)]


def test_complete_job_sorts_all_rates_once_after_two_blocks(tmp_path):
    data=payload(tmp_path);store=PersonalJobStore(tmp_path/"jobs.sqlite3",SCOPE)
    job=store.create("a"*32,data)
    assert job["status"]=="queued" and job["rows"]==[]
    running=store.claim(job["id"])
    first=store.append_block(job["id"],running["generation"],block(data,0,21))
    assert first["status"]=="running" and len(first["rows"])==21
    assert first["resultDigest"] is None
    final=store.append_block(job["id"],running["generation"],block(data,21,3))
    assert final["status"]=="completed"
    assert [r["inputIndex"] for r in final["rows"]]==list(reversed(range(24)))
    assert final["resultDigest"]
    assert store.get(job["id"])==final


def test_cancelled_generation_cannot_publish_late_cpu_result(tmp_path):
    data=payload(tmp_path,2);store=PersonalJobStore(tmp_path/"jobs.sqlite3",SCOPE)
    job=store.claim(store.create("b"*32,data)["id"])
    cancelled=store.cancel(job["id"])
    assert cancelled["status"]=="cancelled"
    with pytest.raises(PersonalJobError):store.append_block(job["id"],job["generation"],block(data,0,2))
    assert store.get(job["id"])["rows"]==[]


def test_restart_interrupts_and_retains_partial_data_without_replay(tmp_path):
    data=payload(tmp_path);path=tmp_path/"jobs.sqlite3"
    store=PersonalJobStore(path,SCOPE)
    job=store.claim(store.create("c"*32,data)["id"])
    store.append_block(job["id"],job["generation"],block(data,0,21))
    restored=PersonalJobStore(path,SCOPE)
    restored.interrupt_pending()
    old=restored.get(job["id"])
    assert old["status"]=="interrupted" and len(old["rows"])==21
    assert old["generation"]!=job["generation"]
    with pytest.raises(PersonalJobError):restored.append_block(job["id"],job["generation"],block(data,21,3))
    new=restored.create("d"*32,data)
    assert new["id"]!=job["id"] and new["rows"]==[]


def test_idempotency_and_one_pending_job_bound(tmp_path):
    data=payload(tmp_path,2);store=PersonalJobStore(tmp_path/"jobs.sqlite3",SCOPE)
    job=store.create("e"*32,data)
    assert store.create("e"*32,data)==job
    with pytest.raises(PersonalJobError):store.create("f"*32,data)
    store.cancel(job["id"])
    changed=copy.deepcopy(data);changed["inputDigest"]="f"*64
    with pytest.raises(PersonalJobError):store.create("e"*32,changed)
    other=store.create("f"*32,data)
    assert other["id"]!=job["id"]


@pytest.mark.parametrize("bad",["duplicate","missing","wrong-rate","nan","wrong-matrix","late-order"])
def test_invalid_cpu_block_cannot_commit_any_partial_rows(tmp_path,bad):
    data=payload(tmp_path,3);store=PersonalJobStore(tmp_path/"jobs.sqlite3",SCOPE)
    job=store.claim(store.create("1"*32,data)["id"])
    rows=block(data,0,3)
    if bad=="duplicate":rows[1]["inputIndex"]=0
    elif bad=="missing":rows=rows[:2]
    elif bad=="wrong-rate":rows[1]["rate"]="Outside"
    elif bad=="nan":rows[1]["score"]=float("nan")
    elif bad=="wrong-matrix":rows[1]["matrix"]=[[0]*12]*11
    elif bad=="late-order":rows.reverse()
    with pytest.raises(PersonalJobError):store.append_block(job["id"],job["generation"],rows)
    assert store.get(job["id"])["rows"]==[]


def test_scope_and_receipt_drift_are_rejected(tmp_path):
    import sqlite3
    from radiworks.scope import ScopeContext
    data=payload(tmp_path,2);path=tmp_path/"jobs.sqlite3"
    store=PersonalJobStore(path,SCOPE);job=store.create("2"*32,data)
    with pytest.raises(PersonalJobError):PersonalJobStore(path,ScopeContext("foreign","client","job"))
    with sqlite3.connect(path) as db:db.execute("UPDATE personal_jobs SET input_json=? WHERE id=?",(json.dumps({**data,"jobSeed":3}),job["id"]))
    with pytest.raises(PersonalJobError):store.get(job["id"])
