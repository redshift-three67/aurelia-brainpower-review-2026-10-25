"""Durable bounded clarification records; an answer never grants execution approval.

Answer queues the unchanged job for its owner to revalidate and review. It does
not enqueue a worker itself, execute model text, or create governance decisions.
"""
import json
import re
import uuid

from .config import SUPERVISORS
from .evidence import now
from .store import JobBusy


class OperatorQuestions:
    MAX_QUESTIONS = 3

    def __init__(self, store):
        self.store = store
        with store.db() as c:
            c.executescript('''
                CREATE TABLE IF NOT EXISTS operator_questions (
                    id TEXT PRIMARY KEY, job_id TEXT NOT NULL, revision INTEGER NOT NULL,
                    status TEXT NOT NULL, body TEXT NOT NULL,
                    UNIQUE(job_id, revision));
                CREATE UNIQUE INDEX IF NOT EXISTS operator_questions_pending
                    ON operator_questions(job_id) WHERE status='pending';
                CREATE TRIGGER IF NOT EXISTS operator_questions_immutable_update
                    BEFORE UPDATE ON operator_questions WHEN OLD.status IN ('answered','cancelled')
                    BEGIN SELECT RAISE(ABORT, 'Resolved question history is immutable'); END;
                CREATE TRIGGER IF NOT EXISTS operator_questions_immutable_delete
                    BEFORE DELETE ON operator_questions WHEN OLD.status IN ('answered','cancelled')
                    BEGIN SELECT RAISE(ABORT, 'Resolved question history is immutable'); END;
            ''')

    @staticmethod
    def _id(value):
        if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{32}', value) is None:
            raise ValueError('Ungültige Auftrag- oder Frage-ID.')

    @staticmethod
    def _hash(value):
        if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{64}', value) is None:
            raise ValueError('Ungültiger Quellenhash.')

    @staticmethod
    def _text(value, maximum, label):
        if not isinstance(value, str) or not value.strip() or len(value) > maximum:
            raise ValueError(f'{label}: 1 bis {maximum} Zeichen erforderlich.')
        return value

    @staticmethod
    def _job(c, job_id):
        OperatorQuestions._id(job_id)
        row = c.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        if row is None:
            raise ValueError('Auftrag nicht gefunden.')
        return row

    @staticmethod
    def _question(c, question_id):
        OperatorQuestions._id(question_id)
        row = c.execute('SELECT body FROM operator_questions WHERE id=?', (question_id,)).fetchone()
        if row is None:
            raise ValueError('Betreiberfrage nicht gefunden.')
        return json.loads(row['body'])

    @staticmethod
    def _result(job, question, extra=None):
        result = json.loads(job['result']) if job['result'] else {}
        if not isinstance(result, dict):
            raise ValueError('Auftragsergebnis muss ein Objekt sein.')
        if extra is not None:
            if not isinstance(extra, dict):
                raise ValueError('Auftragsergebnis muss ein Objekt sein.')
            result.update(extra)
        result['operator_question'] = question
        return json.dumps(result, ensure_ascii=False)

    def ask(self, job_id, question, scope_hash, scope_kind, scope_id, supervisor, result=None):
        """Atomically pause a running job and return its new pending record."""
        if not isinstance(question, dict) or set(question) != {'text', 'reason'}:
            raise ValueError('Betreiberfrage benötigt genau text und reason.')
        for key in ('text', 'reason'):
            self._text(question[key], 2000, key)
        self._id(job_id)
        self._hash(scope_hash)
        if not isinstance(scope_kind, str) or scope_kind not in {'project', 'group'}:
            raise ValueError('Ungültiger Bereichstyp.')
        self._text(scope_id, 256, 'Bereich')
        if supervisor not in SUPERVISORS:
            raise ValueError('Ungültiger Supervisor.')
        if result is not None and not isinstance(result, dict):
            raise ValueError('Auftragsergebnis muss ein Objekt sein.')
        evidence = {k: v for k, v in (result or {}).items() if k != 'operator_question'}
        try:
            encoded_evidence = json.dumps(evidence, ensure_ascii=False, allow_nan=False)
        except (TypeError, ValueError, RecursionError) as exc:
            raise ValueError('Ungültige Reviewnachweise.') from exc
        if len(encoded_evidence) > 160000:
            raise ValueError('Reviewnachweise überschreiten 160000 Zeichen.')
        evidence = json.loads(encoded_evidence)
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            job = self._job(c, job_id)
            if job['status'] != 'running':
                raise ValueError('Nur laufende Aufträge können auf eine Antwort warten.')
            count = c.execute('SELECT COUNT(*) FROM operator_questions WHERE job_id=?', (job_id,)).fetchone()[0]
            if count >= self.MAX_QUESTIONS:
                raise ValueError('Höchstens drei Betreiberfragen je Auftrag.')
            if c.execute("SELECT 1 FROM operator_questions WHERE job_id=? AND status='pending'", (job_id,)).fetchone():
                raise ValueError('Dieser Auftrag hat bereits eine offene Frage.')
            record = {'id': uuid.uuid4().hex, 'job_id': job_id, 'revision': count + 1,
                      'status': 'pending', 'question': dict(question), 'scope_hash': scope_hash,
                      'scope_kind': scope_kind, 'scope_id': scope_id, 'supervisor': supervisor,
                      'created_at': now(), 'answered_at': None, 'cancelled_at': None,
                      'answer': None, 'continuation_authorized': False, 'review_evidence': evidence}
            encoded_result = self._result(job, record, result)
            c.execute('INSERT INTO operator_questions VALUES(?,?,?,?,?)',
                      (record['id'], job_id, record['revision'], 'pending', json.dumps(record, ensure_ascii=False)))
            c.execute("UPDATE jobs SET status='waiting_for_operator',ended_at=NULL,error=NULL,result=? WHERE id=?",
                      (encoded_result, job_id))
            return record

    def get(self, question_id):
        with self.store.db() as c:
            return self._question(c, question_id)

    def list(self, status=None, job_id=None, limit=100):
        if status is not None and (not isinstance(status, str) or status not in {'pending', 'answered', 'cancelled'}):
            raise ValueError('Ungültiger Fragenstatus.')
        if job_id is not None:
            self._id(job_id)
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError('Fragenlimit: 1 bis 1000.')
        filters, values = [], []
        for column, value in (('status', status), ('job_id', job_id)):
            if value is not None:
                filters.append(column + '=?')
                values.append(value)
        where = ' WHERE ' + ' AND '.join(filters) if filters else ''
        with self.store.db() as c:
            return [json.loads(row['body']) for row in c.execute(
                'SELECT body FROM operator_questions' + where + ' ORDER BY rowid DESC LIMIT ?', (*values, limit))]

    def answers(self, job_id):
        self._id(job_id)
        records = sorted(self.list(status='answered', job_id=job_id, limit=self.MAX_QUESTIONS),
                         key=lambda item: item['revision'])
        return [{k: v for k, v in item.items() if k != 'review_evidence'} for item in records]

    def answer(self, question_id, answer, expected_scope_hash, current_scope_hash):
        """Return {'job': queued_job, 'answer': record}; caller must revalidate."""
        self._text(answer, 4000, 'Antwort')
        self._id(question_id)
        self._hash(expected_scope_hash)
        self._hash(current_scope_hash)
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            record = self._question(c, question_id)
            job = self._job(c, record['job_id'])
            if record['status'] != 'pending' or job['status'] != 'waiting_for_operator':
                raise ValueError('Diese Frage wartet nicht auf eine Antwort.')
            if expected_scope_hash != record['scope_hash'] or current_scope_hash != record['scope_hash']:
                raise ValueError('Quellenstand geändert; neuer Review erforderlich.')
            from .sequence_store import require_idle
            require_idle(c)
            record.update(status='answered', answer=answer, answered_at=now())
            encoded_result = self._result(job, record)
            c.execute("UPDATE operator_questions SET status='answered',body=? WHERE id=?",
                      (json.dumps(record, ensure_ascii=False), question_id))
            c.execute("UPDATE jobs SET status='queued',ended_at=NULL,error=NULL,result=? WHERE id=?",
                      (encoded_result, record['job_id']))
            return {'job': self.store.decode(self._job(c, record['job_id'])), 'answer': record}

    def cancel(self, job_id):
        """Cancel only a waiting job, retaining all question and answer history."""
        with self.store.db() as c:
            c.execute('BEGIN IMMEDIATE')
            job = self._job(c, job_id)
            if job['status'] != 'waiting_for_operator':
                raise ValueError('Dieser Auftrag wartet nicht auf eine Antwort.')
            row = c.execute("SELECT id FROM operator_questions WHERE job_id=? AND status='pending'", (job_id,)).fetchone()
            if row is None:
                raise ValueError('Offene Betreiberfrage fehlt.')
            record = self._question(c, row['id'])
            record.update(status='cancelled', cancelled_at=now())
            encoded_result = self._result(job, record)
            c.execute("UPDATE operator_questions SET status='cancelled',body=? WHERE id=?",
                      (json.dumps(record, ensure_ascii=False), record['id']))
            c.execute("UPDATE jobs SET status='cancelled',ended_at=?,result=? WHERE id=?",
                      (now(), encoded_result, job_id))
            return self.store.decode(self._job(c, job_id))
