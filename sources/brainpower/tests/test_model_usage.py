import tempfile
import unittest
from pathlib import Path
from governor_workbench.store import Store
from governor_workbench.llm import ModelError, ModelCancelled
from governor_workbench.model_usage import TrackedClient, job_usage, check_prompt


class UsageTests(unittest.TestCase):
    def test_cached_and_reasoning_subtotals_are_recorded_separately(self):
        class Client:
            def call(self,*args,**kwargs):
                return {'usage':dict(input_tokens=100,output_tokens=40,total_tokens=140,
                                      input_tokens_details={'cached_tokens':70},
                                      output_tokens_details={'reasoning_tokens':30})}
        with tempfile.TemporaryDirectory() as tmp:
            store=Store(Path(tmp)/'db');job=store.create_job('scope_plan',None)
            TrackedClient(Client(),store,job['id']).call('gpt-5.6-terra','x')
            usage=store.job(job['id'])['token_usage']
            self.assertEqual(70,usage['cached_tokens'])
            self.assertEqual(30,usage['reasoning_tokens'])
            self.assertEqual(70,usage['calls'][0]['cached_tokens'])
            self.assertEqual(30,usage['calls'][0]['reasoning_tokens'])

    def test_real_transport_limits_and_no_process_on_overflow(self):
        from governor_workbench.hermes import HermesAdapter
        from governor_workbench.llm import RouterClient
        from unittest.mock import patch
        hermes=HermesAdapter('missing.cmd',workspace='.',codex_auth_path='not-read.json')
        router=RouterClient('http://127.0.0.1:3000/v1')
        check_prompt('x'*120000,router,'gpt-5.6-sol')
        with patch('subprocess.Popen') as process, patch.object(router,'_request') as request:
            with self.assertRaises(ModelError): hermes.review('x'*95001)
            with self.assertRaises(ModelError): router.call('gpt-5.6-sol','x'*120001)
            process.assert_not_called(); request.assert_not_called()

    def test_complete_usage_survives_new_wrapper_without_double_count(self):
        class Client:
            def call(self,*a,**k): return {'usage':dict(input_tokens=0,output_tokens=5,total_tokens=5)}
        with tempfile.TemporaryDirectory() as tmp:
            store=Store(Path(tmp)/'db');job=store.create_job('scope_plan',None)
            for _ in range(2): TrackedClient(Client(),store,job['id']).call('gpt-5.6-terra','x')
            first=store.job(job['id'])['token_usage']
            self.assertEqual(first,store.jobs()[0]['token_usage'])
            self.assertTrue(first['complete']);self.assertEqual(first['total_tokens'],10)
            self.assertEqual(first['input_tokens'],0)

    def test_preflight_rejection_leaves_no_started_receipt(self):
        class Client:
            def prompt_limit(self,model): return 3
            def call(self,*a,**k): raise AssertionError('network forbidden')
        with tempfile.TemporaryDirectory() as tmp:
            store=Store(Path(tmp)/'db');job=store.create_job('scope_plan',None)
            with self.assertRaises(ModelError): TrackedClient(Client(),store,job['id']).call('gpt-5.6-terra','long')
            self.assertFalse(store.job(job['id'])['token_usage']['recorded'])

    def test_failed_and_hard_interrupted_calls_remain_unknown(self):
        class Client:
            def call(self,*a,**k): raise ModelError('synthetic failure')
        with tempfile.TemporaryDirectory() as tmp:
            store=Store(Path(tmp)/'db');job=store.create_job('scope_plan',None)
            with self.assertRaises(ModelError): TrackedClient(Client(),store,job['id']).call('gpt-5.6-terra','x')
            with store.db() as c:
                c.execute('INSERT INTO model_call_usage(id,job_id,model,status) VALUES(?,?,?,?)',('interrupted',job['id'],'gpt-5.6-sol','started'))
            value=store.job(job['id'])['token_usage']
            self.assertEqual(value['call_count'],2);self.assertIsNone(value['total_tokens'])
            self.assertEqual([r['status'] for r in value['calls']],['failed','started'])

    def test_transport_boundary_prevents_call(self):
        class Client:
            def prompt_limit(self, model): return 95000
            def call(self, *args, **kwargs): raise AssertionError('must not call')
        check_prompt('x'*95000, Client(), 'gpt-5.6-terra')
        with self.assertRaises(ModelError):
            check_prompt('x'*95001, Client(), 'gpt-5.6-terra')

    def test_partial_failure_persists_and_reads_do_not_duplicate(self):
        class Client:
            n = 0
            def call(self, *args, **kwargs):
                self.n += 1
                if self.n == 2: raise ModelCancelled('cancel')
                return {'usage': {'input_tokens': 12, 'output_tokens': True, 'total_tokens': -1}}
        with tempfile.TemporaryDirectory() as tmp:
            store=Store(Path(tmp)/'db')
            job=store.create_job('model_check', None)
            client=TrackedClient(Client(),store,job['id'])
            client.call('gpt-5.6-terra','test')
            with self.assertRaises(ModelCancelled): client.call('gpt-5.6-sol','test')
            with store.db() as c:
                result=job_usage(c,job['id'])
                self.assertEqual(result,job_usage(c,job['id']))
            self.assertEqual(result['call_count'],2)
            self.assertEqual(result['input_tokens'],12)
            self.assertIsNone(result['output_tokens'])
            self.assertIsNone(result['total_tokens'])
            self.assertFalse(result['complete'])
            self.assertEqual(result['calls'][1]['status'],'cancelled')
            self.assertEqual(store.job(job['id'])['token_usage'], result)

    def test_unknown_legacy_is_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=Store(Path(tmp)/'db')
            job=store.create_job('hybrid_review',None)
            with store.db() as c: value=job_usage(c,job['id'])
            self.assertFalse(value['recorded'])
            self.assertIsNone(value['total_tokens'])
