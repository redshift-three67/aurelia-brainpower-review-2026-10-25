"""Scoped personal job ledger: whole-catalog completion, no automatic replay."""
from __future__ import annotations
import copy
import json
import math
import re
import sqlite3
import threading
import uuid
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from .personal_analysis import validate_personal_input, PersonalAnalysisError
from ..persistence import document_digest

STATES = {"queued", "running", "completed", "cancelled", "interrupted", "failed"}
ACTIVE = {"queued", "running"}

class PersonalJobError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _identifier(value):
    return type(value) is str and re.fullmatch(r"[0-9a-f]{32}", value) is not None


def _validate_rows(rows, data):
    if type(rows) is not list or len(rows)>len(data["rates"]):raise PersonalJobError("worker_protocol")
    seen=set()
    for row in rows:
        if type(row) is not dict or set(row)!={"inputIndex","rate","score","intensity","matrix"}:raise PersonalJobError("worker_protocol")
        i=row["inputIndex"]
        if type(i) is not int or not 0<=i<len(data["rates"]) or i in seen or row["rate"]!=data["rates"][i]:raise PersonalJobError("worker_protocol")
        seen.add(i)
        if any(type(row[k]) not in (int,float) or not math.isfinite(row[k]) for k in ("score","intensity")) or not -1.00001<=row["score"]<=1.00001 or row["intensity"]<0:raise PersonalJobError("worker_protocol")
        matrix=row["matrix"]
        if type(matrix) is not list or len(matrix)!=12 or any(type(r) is not list or len(r)!=12 or any(type(v) is not int or not 0<=v<=9 for v in r) for r in matrix):raise PersonalJobError("worker_protocol")


class PersonalJobStore:
    def __init__(self, path, scope):
        self.path=Path(path);self.scope=scope.to_dict();self._lock=threading.RLock()
        if self.path.is_symlink() or self.path.is_junction() or self.path.parent.is_symlink() or self.path.parent.is_junction():raise PersonalJobError("unsafe_store")
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS personal_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS personal_jobs (id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, status TEXT NOT NULL, input_json TEXT NOT NULL, record_json TEXT NOT NULL)")
            expected=json.dumps(self.scope,sort_keys=True)
            stored=db.execute("SELECT value FROM personal_meta WHERE key='scope'").fetchone()
            if stored and stored[0]!=expected:raise PersonalJobError("foreign_scope")
            db.execute("INSERT OR IGNORE INTO personal_meta VALUES ('scope',?)",(expected,))
            schema=db.execute("SELECT value FROM personal_meta WHERE key='schema'").fetchone()
            if schema and schema[0]!='1':raise PersonalJobError("unknown_schema")
            db.execute("INSERT OR IGNORE INTO personal_meta VALUES ('schema','1')")
            for (identifier,) in db.execute("SELECT id FROM personal_jobs").fetchall():self._get(db,identifier)

    @contextmanager
    def _transaction(self):
        with self._lock:
            try:
                with closing(sqlite3.connect(self.path,timeout=10)) as db, db:
                    db.execute("PRAGMA synchronous=FULL")
                    db.execute("BEGIN IMMEDIATE")
                    yield db
            except sqlite3.Error as exc:raise PersonalJobError("store_unavailable") from exc

    def _get(self,db,identifier):
        row=db.execute("SELECT id,request_id,status,input_json,record_json FROM personal_jobs WHERE id=?",(identifier,)).fetchone()
        if row is None:raise PersonalJobError("not_found")
        try:
            data=validate_personal_input(json.loads(row[3]));record=json.loads(row[4])
            fields={"id","requestId","status","generation","createdAt","updatedAt","rows","resultDigest","error","receiptDigest"}
            if type(record) is not dict or set(record)!=fields or record["id"]!=row[0] or record["requestId"]!=row[1] or record["status"]!=row[2] or not _identifier(record["id"]) or not _identifier(record["requestId"]) or not _identifier(record["generation"]) or record["status"] not in STATES:raise PersonalJobError("invalid_receipt")
            if data["scope"]!=self.scope:raise PersonalJobError("foreign_scope")
            body={k:v for k,v in record.items() if k!='receiptDigest'};body['input']=data
            if record["receiptDigest"]!=document_digest(body):raise PersonalJobError("receipt_changed")
            for key in ("createdAt","updatedAt"):
                if datetime.fromisoformat(record[key]).tzinfo is None:raise PersonalJobError("invalid_receipt")
            _validate_rows(record["rows"],data)
            indices=[r["inputIndex"] for r in record["rows"]]
            if record["status"]=="completed":
                if len(indices)!=len(data["rates"]) or record["rows"]!=sorted(record["rows"],key=lambda r:(-r["score"],r["inputIndex"])) or record["resultDigest"]!=document_digest(record["rows"]):raise PersonalJobError("invalid_result")
            elif indices!=list(range(len(indices))) or record["resultDigest"] is not None:raise PersonalJobError("invalid_partial")
            return {**record,'input':data}
        except (ValueError,TypeError,KeyError,AttributeError) as exc:
            if isinstance(exc,PersonalJobError):raise
            raise PersonalJobError("invalid_receipt") from exc

    def _write(self,db,record):
        body={k:v for k,v in record.items() if k!='receiptDigest'}
        record["receiptDigest"]=document_digest(body)
        metadata={k:v for k,v in record.items() if k!='input'}
        db.execute("INSERT INTO personal_jobs VALUES (?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET status=excluded.status,input_json=excluded.input_json,record_json=excluded.record_json",(record["id"],record["requestId"],record["status"],json.dumps(record['input'],ensure_ascii=False,allow_nan=False),json.dumps(metadata,ensure_ascii=False,allow_nan=False)))
        return copy.deepcopy(record)

    def get(self,identifier):
        with self._transaction() as db:return self._get(db,identifier)

    def list(self,case_id=None):
        with self._transaction() as db:
            records=[self._get(db,r[0]) for r in db.execute("SELECT id FROM personal_jobs ORDER BY rowid DESC").fetchall()]
            return [r for r in records if case_id is None or r['input']['contextSnapshot']['caseId']==case_id]

    def by_request(self,request_id):
        if not _identifier(request_id):raise PersonalJobError('invalid_request')
        with self._transaction() as db:
            found=db.execute('SELECT id FROM personal_jobs WHERE request_id=?',(request_id,)).fetchone()
            return self._get(db,found[0]) if found else None

    def has_pending(self):
        with self._transaction() as db:
            return db.execute("SELECT 1 FROM personal_jobs WHERE status IN ('queued','running') LIMIT 1").fetchone() is not None

    def ensure_capacity(self):
        with self._transaction() as db:
            if db.execute("SELECT 1 FROM personal_jobs WHERE status IN ('queued','running') LIMIT 1").fetchone():raise PersonalJobError('busy')

    def create(self,request_id,data):
        if not _identifier(request_id):raise PersonalJobError("invalid_request")
        try:data=validate_personal_input(data)
        except PersonalAnalysisError as exc:raise PersonalJobError("invalid_input") from exc
        if data['scope']!=self.scope:raise PersonalJobError("foreign_scope")
        with self._transaction() as db:
            previous=db.execute("SELECT id FROM personal_jobs WHERE request_id=?",(request_id,)).fetchone()
            if previous:
                record=self._get(db,previous[0])
                if record['input']['inputDigest']!=data['inputDigest']:raise PersonalJobError("request_conflict")
                return record
            if db.execute("SELECT 1 FROM personal_jobs WHERE status IN ('queued','running') LIMIT 1").fetchone():raise PersonalJobError("busy")
            timestamp=_now()
            return self._write(db,{"id":uuid.uuid4().hex,"requestId":request_id,"status":"queued","generation":uuid.uuid4().hex,"createdAt":timestamp,"updatedAt":timestamp,"input":data,"rows":[],"resultDigest":None,"error":None})

    def claim(self,identifier):
        with self._transaction() as db:
            record=self._get(db,identifier)
            if record['status']!='queued':raise PersonalJobError('stale_job')
            record.update(status='running',updatedAt=_now());return self._write(db,record)

    def append_block(self,identifier,generation,rows):
        with self._transaction() as db:
            record=self._get(db,identifier)
            if record['status']!='running' or record['generation']!=generation:raise PersonalJobError('stale_job')
            _validate_rows(rows,record['input'])
            start=len(record['rows']);end=min(start+21,len(record['input']['rates']))
            if [r['inputIndex'] for r in rows]!=list(range(start,end)):raise PersonalJobError('worker_protocol')
            record['rows'].extend(copy.deepcopy(rows));record['updatedAt']=_now()
            if end==len(record['input']['rates']):
                record['rows'].sort(key=lambda r:(-r['score'],r['inputIndex']))
                record.update(status='completed',resultDigest=document_digest(record['rows']))
            return self._write(db,record)

    def _end(self,identifier,state,error=None):
        with self._transaction() as db:
            record=self._get(db,identifier)
            if record['status'] in ACTIVE:
                record.update(status=state,generation=uuid.uuid4().hex,updatedAt=_now(),error=error)
                return self._write(db,record)
            return record

    def cancel(self,identifier):return self._end(identifier,'cancelled')
    def fail(self,identifier,code):
        allowed={'implementation_changed','worker_start_failed','worker_timeout','worker_failed','worker_protocol','cpu_unavailable','shutdown'}
        if code not in allowed:raise PersonalJobError('invalid_error')
        return self._end(identifier,'failed',code)

    def interrupt_pending(self):
        with self._transaction() as db:
            for (identifier,) in db.execute("SELECT id FROM personal_jobs WHERE status IN ('queued','running')").fetchall():
                record=self._get(db,identifier)
                record.update(status='interrupted',generation=uuid.uuid4().hex,updatedAt=_now())
                self._write(db,record)
