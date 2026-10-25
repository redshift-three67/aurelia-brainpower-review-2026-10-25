"""Local request receipts; never stores prompts, answers or credentials."""
import time
import uuid
import json

ROUTER_PROMPT_CHARS = 120_000
HERMES_PROMPT_CHARS = 95_000
FIELDS = ('input_tokens', 'output_tokens', 'total_tokens')
DETAILS = ('cached_tokens', 'reasoning_tokens')


def check_prompt(prompt, client=None, model=None, limit=None):
    from .llm import ModelError
    if limit is None:
        resolver = getattr(client, 'prompt_limit', None)
        limit = resolver(model) if callable(resolver) else ROUTER_PROMPT_CHARS
    if not isinstance(prompt, str) or len(prompt) > limit:
        raise ModelError(f'Kontext überschreitet die Transportgrenze von {limit} Zeichen. '
                         'Quellen gezielt eingrenzen; keine automatische Kürzung oder Ausweichroute.')


def normalized_usage(value):
    value = value if isinstance(value, dict) else {}
    valid = lambda number: number if type(number) is int and 0 <= number <= 2**53-1 else None
    result = {key: valid(value.get(key)) for key in FIELDS}
    incoming = value.get('input_tokens_details')
    outgoing = value.get('output_tokens_details')
    result['cached_tokens'] = valid(incoming.get('cached_tokens')) if isinstance(incoming, dict) else None
    result['reasoning_tokens'] = valid(outgoing.get('reasoning_tokens')) if isinstance(outgoing, dict) else None
    return result


def job_usage(connection, job_id):
    rows = []
    if connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='model_call_usage'").fetchone():
        rows = [dict(row) for row in connection.execute(
            'SELECT id,model,status,input_tokens,output_tokens,total_tokens,elapsed_seconds '
            'FROM model_call_usage WHERE job_id=? ORDER BY rowid', (job_id,))]
        routing = {}
        if connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='model_call_routing'").fetchone():
            routing = {r['call_id']: json.loads(r['body']) for r in connection.execute(
                'SELECT r.call_id,r.body FROM model_call_routing r JOIN model_call_usage u ON u.id=r.call_id WHERE u.job_id=?', (job_id,))}
        for row in rows: row['routing'] = routing.get(row['id'])
        details = {}
        if connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='model_call_usage_details'").fetchone():
            details = {r['call_id']: dict(r) for r in connection.execute(
                'SELECT call_id,cached_tokens,reasoning_tokens FROM model_call_usage_details '
                'WHERE call_id IN (SELECT id FROM model_call_usage WHERE job_id=?)', (job_id,))}
        for row in rows:
            for field in DETAILS:
                row[field] = details.get(row['id'], {}).get(field)
    result = dict(recorded=bool(rows), call_count=len(rows), calls=rows,
                  complete=bool(rows) and all(row[key] is not None for row in rows for key in FIELDS))
    for key in FIELDS + DETAILS:
        values = [row[key] for row in rows if row[key] is not None]
        result[key] = sum(values) if values else None
    return result


class TrackedClient:
    """Wrap one job's transport, persisting each attempt before dispatch."""
    def __init__(self, client, store, job_id, routing=None):
        self.client, self.store, self.job_id = client, store, job_id
        self.routing = routing

    def prompt_limit(self, model):
        resolver = getattr(self.client, 'prompt_limit', None)
        return resolver(model) if callable(resolver) else ROUTER_PROMPT_CHARS

    def call(self, model, prompt, **kwargs):
        from .llm import MODELS, ModelCancelled, ModelError
        from .routing_policy import ROUTE_B_EFFORTS
        if model not in MODELS and model not in ROUTE_B_EFFORTS:
            raise ModelError('Unsupported model.')
        check_prompt(prompt, self, model)
        cancel = kwargs.get('cancel_event')
        if cancel is not None and cancel.is_set():
            raise ModelCancelled('Model request cancelled before dispatch.')
        from .routing_policy import choose, validate_effort
        decision = self.routing(model) if self.routing else choose('medium', model)
        validate_effort(model, decision['effective'])
        if 'reasoning' in kwargs and kwargs['reasoning'] != decision['effective']:
            raise ModelError('Aufrufstufe widerspricht der gebundenen Auswahl.')
        kwargs['reasoning'] = decision['effective']
        key = uuid.uuid4().hex
        with self.store.db() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS model_call_usage(
                id TEXT PRIMARY KEY,job_id TEXT NOT NULL,model TEXT NOT NULL,status TEXT NOT NULL,
                input_tokens INTEGER,output_tokens INTEGER,total_tokens INTEGER,elapsed_seconds REAL)''')
            c.execute('CREATE INDEX IF NOT EXISTS model_call_usage_job ON model_call_usage(job_id)')
            c.execute('INSERT INTO model_call_usage(id,job_id,model,status) VALUES(?,?,?,?)',
                      (key,self.job_id,model,'started'))
            c.execute('CREATE TABLE IF NOT EXISTS model_call_routing(call_id TEXT PRIMARY KEY,body TEXT NOT NULL)')
            c.execute('INSERT INTO model_call_routing VALUES(?,?)', (key,json.dumps(decision,ensure_ascii=False)))
            c.execute('''CREATE TABLE IF NOT EXISTS model_call_usage_details(
                call_id TEXT PRIMARY KEY,cached_tokens INTEGER,reasoning_tokens INTEGER)''')
        started = time.monotonic()
        usage = normalized_usage(None)
        status = 'failed'
        try:
            result = self.client.call(model, prompt, **kwargs)
            usage = normalized_usage(result.get('usage'))
            status = 'failed' if result.get('success') is False else 'completed'
            return result
        except ModelCancelled:
            status = 'cancelled'
            raise
        finally:
            with self.store.db() as c:
                c.execute('UPDATE model_call_usage SET status=?,input_tokens=?,output_tokens=?,total_tokens=?,elapsed_seconds=? WHERE id=?',
                          (status,*(usage[k] for k in FIELDS),round(time.monotonic()-started,3),key))
                c.execute('INSERT INTO model_call_usage_details VALUES(?,?,?)',
                          (key,usage['cached_tokens'],usage['reasoning_tokens']))
