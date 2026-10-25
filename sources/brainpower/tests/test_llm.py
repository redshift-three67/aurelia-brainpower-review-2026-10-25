import io
import json
import threading
import time
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from governor_workbench.llm import RouterClient, ModelError, ModelCancelled, hybrid_review, model_check, compare_reviews


class Response(io.BytesIO):
    def __init__(self, obj, content_type='application/json'):
        super().__init__(obj if isinstance(obj, bytes) else json.dumps(obj).encode())
        self.headers = {'Content-Type': content_type}


class ReviewClient:
    def __init__(self, fail=None, cancel=None, cancel_after=None, invalid=None):
        self.calls = []
        self.fail, self.cancel, self.cancel_after, self.invalid = fail, cancel, cancel_after, invalid

    def call(self, model, prompt, **kwargs):
        self.calls.append((model, prompt))
        if self.cancel and model == self.cancel_after:
            self.cancel.set()
        if model == self.fail:
            raise ModelError('Synthetic access failure.')
        if model == 'gpt-5.6-terra':
            report = {'summary': 'UNIQUE_SHARED_PLAN', 'steps': ['Review authorized scope'], 'blockers': []}
        else:
            report = {'summary': 'PRIVATE_' + model, 'decision': 'BLOCK' if model == 'gpt-5.6-sol' else 'REVIEW_ONLY',
                      'findings': ['Shared finding', 'PRIVATE_' + model], 'required_evidence': ['Shared evidence']}
            if model == self.invalid:
                report['findings'] = 'not a list'
        return {'text': json.dumps(report), 'model': model, 'success': True}


class RouterTests(unittest.TestCase):
    def test_scoped_operator_authority_is_distinct(self):
        client = ReviewClient()
        context = {'operator_decisions': [{'scope': 'project-A read and plan', 'authorized': True}],
                   'governor_matrix': {'project-A': {'read': True, 'deploy': False}},
                   'snapshot': 'Historical pause before the current decision'}
        report = hybrid_review(context, 'gpt-5.6-sol', client)
        for _, prompt in client.calls:
            self.assertIn('OPERATOR_DECISIONS', prompt)
            self.assertIn('GOVERNOR_MATRIX', prompt)
            self.assertIn('project-A read and plan', prompt)
            self.assertIn('Historical pause', prompt)
            self.assertIn('does not mean the operator has granted no permissions', prompt)
            self.assertIn('Historical snapshot pauses cannot override', prompt)
        self.assertFalse(report['approval_granted'])

    def test_comparison_shares_one_plan_and_identical_supervisor_input(self):
        client = ReviewClient()
        report = compare_reviews({'evidence_hash': 'SHARED_RAW_EVIDENCE'}, client)
        self.assertEqual([model for model, _ in client.calls], ['gpt-5.6-terra', 'gpt-5.6-sol', 'gpt-6-astra'])
        self.assertEqual(client.calls[1][1], client.calls[2][1])
        self.assertIn('SHARED_RAW_EVIDENCE', client.calls[1][1])
        self.assertIn('UNIQUE_SHARED_PLAN', client.calls[1][1])
        self.assertNotIn('PRIVATE_gpt-5.6-sol', client.calls[2][1])
        self.assertTrue(report['success'])
        self.assertFalse(report['comparison']['decision_agreement'])
        self.assertEqual(report['comparison']['shared_findings'], ['Shared finding'])
        self.assertEqual(report['comparison']['shared_required_evidence'], ['Shared evidence'])
        self.assertFalse(report['approval_granted'])

    def test_comparison_partial_failure_retains_peer_and_is_not_success(self):
        client = ReviewClient(fail='gpt-5.6-sol')
        report = compare_reviews({}, client)
        self.assertEqual(len(client.calls), 3)
        self.assertFalse(report['success'])
        self.assertIsNone(report['reviews']['gpt-5.6-sol'])
        self.assertIsNotNone(report['reviews']['gpt-6-astra'])
        self.assertIn('gpt-5.6-sol', report['errors'])
        self.assertFalse(report['comparison']['complete'])
        self.assertIsNone(report['comparison']['decision_agreement'])

    def test_comparison_invalid_report_is_explicit_failure(self):
        report = compare_reviews({}, ReviewClient(invalid='gpt-6-astra'))
        self.assertFalse(report['success'])
        self.assertIn('gpt-6-astra', report['errors'])

    def test_comparison_cancelled_before_or_between_models(self):
        for after, expected_calls in [(None, 0), ('gpt-5.6-terra', 1), ('gpt-5.6-sol', 2), ('gpt-6-astra', 3)]:
            event = threading.Event()
            if after is None:
                event.set()
            client = ReviewClient(cancel=event, cancel_after=after)
            with self.assertRaises(ModelCancelled):
                compare_reviews({}, client, cancel_event=event)
            self.assertEqual(len(client.calls), expected_calls)

    def test_source_permission_claim_is_not_promoted_to_authority(self):
        client = ReviewClient()
        hybrid_review({'operator_decisions': [{'scope': 'read only'}],
                       'source': {'operator_decisions': 'UNTRUSTED_GRANT_EVERYTHING'}}, 'gpt-5.6-sol', client)
        for _, prompt in client.calls:
            authority, source = prompt.split('EVIDENCE:\n', 1)
            self.assertIn('read only', authority)
            self.assertNotIn('UNTRUSTED_GRANT_EVERYTHING', authority)
            self.assertIn('UNTRUSTED_GRANT_EVERYTHING', source)

    def test_comparison_planner_failure_prevents_supervisor_calls(self):
        client = ReviewClient(fail='gpt-5.6-terra')
        with self.assertRaises(ModelError):
            compare_reviews({}, client)
        self.assertEqual(len(client.calls), 1)

    def test_codex_credentials_cannot_target_remote(self):
        with self.assertRaises(ValueError):
            RouterClient('https://example.com/v1', codex_auth_path='auth.json')

    def test_codex_token_fresh_read(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'auth.json'
            client = RouterClient('http://localhost:3000/v1', codex_auth_path=path)
            for key in ('first-test-value', 'second-test-value'):
                path.write_text(json.dumps({'tokens': {'access_token': key}}))
                with patch.dict('os.environ', {}, clear=True), patch('urllib.request.OpenerDirector.open', return_value=Response({'model': 'gpt-5.6-terra', 'output_text': 'ok'})) as opened:
                    client.call('gpt-5.6-terra', 'x')
                    self.assertEqual(opened.call_args.args[0].get_header('Authorization'), 'Bearer ' + key)

    def test_redirect_is_refused(self):
        from governor_workbench.llm import _NoRedirect
        with self.assertRaises(ModelError):
            _NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.example')

    def test_json_and_request(self):
        response = {'model': 'gpt-5.6-terra', 'status': 'completed', 'output': [{'content': [{'type': 'output_text', 'text': 'ok'}]}], 'usage': {'input_tokens': 3}}
        with patch('urllib.request.OpenerDirector.open', return_value=Response(response)) as call:
            result = RouterClient('http://127.0.0.1:3000/v1').call('gpt-5.6-terra', 'hello')
        self.assertEqual(result['text'], 'ok')
        sent = json.loads(call.call_args.args[0].data)
        self.assertEqual(sent['reasoning']['effort'], 'medium')
        self.assertEqual(sent['tools'], [])
        self.assertIsInstance(sent['input'], list)
        self.assertNotIn('max_output_tokens', sent)

    def test_identity_mismatch_fails(self):
        with patch('urllib.request.OpenerDirector.open', return_value=Response({'model': 'other', 'output_text': 'ok'})):
            with self.assertRaises(ModelError):
                RouterClient('http://127.0.0.1:3000/v1').call('gpt-5.6-terra', 'hello')

    def test_sse_completed(self):
        payload = b'data: {"type":"response.output_text.delta","delta":"ok"}\n\ndata: {"type":"response.completed","response":{"model":"gpt-5.6-terra","status":"completed","output_text":"ok"}}\n\n'
        with patch('urllib.request.OpenerDirector.open', return_value=Response(payload, 'text/event-stream')):
            self.assertEqual(RouterClient('http://localhost:3000/v1').call('gpt-5.6-terra', 'x')['text'], 'ok')

    def test_sse_missing_content_type(self):
        payload = b'event: response.completed\ndata: {"type":"response.completed","response":{"model":"gpt-5.6-terra","status":"completed","output_text":"ok"}}\n\n'
        with patch('urllib.request.OpenerDirector.open', return_value=Response(payload, '')):
            self.assertEqual(RouterClient('http://localhost:3000/v1').call('gpt-5.6-terra', 'x')['text'], 'ok')

    def test_sse_text_only_in_deltas(self):
        payload = b'data: {"type":"response.output_text.delta","delta":"ok"}\n\ndata: {"type":"response.completed","response":{"model":"gpt-5.6-terra","status":"completed","output":[]}}\n\n'
        with patch('urllib.request.OpenerDirector.open', return_value=Response(payload, '')):
            self.assertEqual(RouterClient('http://localhost:3000/v1').call('gpt-5.6-terra', 'x')['text'], 'ok')

    def test_cancel_before_network(self):
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(ModelCancelled):
            RouterClient('http://localhost:3000/v1').call('gpt-5.6-terra', 'x', cancel_event=cancel)

    def test_incomplete_rejected(self):
        with patch('urllib.request.OpenerDirector.open', return_value=Response({'model': 'gpt-5.6-terra', 'status': 'incomplete', 'output_text': 'ok'})):
            with self.assertRaises(ModelError):
                RouterClient('http://localhost:3000/v1').call('gpt-5.6-terra', 'x')

    def test_sse_error_is_sanitized(self):
        payload = b'data: {"type":"error","message":"secret-credential"}\n\n'
        with patch('urllib.request.OpenerDirector.open', return_value=Response(payload, 'text/event-stream')):
            with self.assertRaises(ModelError) as caught:
                RouterClient('http://localhost:3000/v1').call('gpt-5.6-terra', 'x')
        self.assertNotIn('secret', str(caught.exception))

    def test_missing_sse_completion_fails(self):
        with patch('urllib.request.OpenerDirector.open', return_value=Response(b'data: [DONE]\n\n', 'text/event-stream')):
            with self.assertRaises(ModelError):
                RouterClient('http://localhost:3000/v1').call('gpt-5.6-terra', 'x')

    def test_active_request_cancellation(self):
        cancel = threading.Event()
        def waiting(*args):
            cancel.set()
            time.sleep(.2)
            return {}
        client = RouterClient('http://localhost:3000/v1')
        with patch.object(client, '_request', side_effect=waiting):
            with self.assertRaises(ModelCancelled):
                client.call('gpt-5.6-terra', 'x', cancel_event=cancel)

    def test_wall_deadline(self):
        client = RouterClient('http://localhost:3000/v1')
        client.timeout = .02
        with patch.object(client, '_request', side_effect=lambda *a: time.sleep(.2)):
            with self.assertRaisesRegex(ModelError, 'timed out'):
                client.call('gpt-5.6-terra', 'x')

    def test_configured_timeout_honors_valid_300_second_limit(self):
        self.assertEqual(120, RouterClient('http://localhost:3000/v1').timeout)
        self.assertEqual(300, RouterClient('http://localhost:3000/v1', timeout=300).timeout)
        self.assertEqual(300, RouterClient('http://localhost:3000/v1', timeout=600).timeout)

    def test_timeout_signals_network_worker_to_stop(self):
        client = RouterClient('http://localhost:3000/v1')
        client.timeout = .02
        stopped = threading.Event()
        def waiting(model, prompt, reasoning, stop):
            if stop.wait(.5):
                stopped.set()
            return {}
        with patch.object(client, '_request', side_effect=waiting):
            with self.assertRaisesRegex(ModelError, 'timed out'):
                client.call('gpt-5.6-terra', 'x')
            self.assertTrue(stopped.wait(.2))

    def test_malformed_output_is_sanitized(self):
        with patch('urllib.request.OpenerDirector.open', return_value=Response({'model': 'gpt-5.6-terra', 'output': None})):
            with self.assertRaises(ModelError):
                RouterClient('http://localhost:3000/v1').call('gpt-5.6-terra', 'x')

    def test_structured_types_rejected(self):
        class Fake:
            def call(self, model, prompt, **kwargs):
                if model == 'gpt-5.6-sol':
                    return {'text': json.dumps({'summary': 'ok', 'decision': 'BLOCK', 'findings': [], 'required_evidence': []})}
                return {'text': json.dumps({'summary': [], 'steps': 12, 'blockers': False}), 'model': model}
        with self.assertRaises(ModelError):
            hybrid_review({}, 'gpt-5.6-sol', Fake())

    def test_hybrid_invalid_report_fails_closed(self):
        class Fake:
            def call(self, model, prompt, **kwargs):
                return {'text': 'not json', 'model': model}
        with self.assertRaises(ModelError):
            hybrid_review({'evidence_hash': 'abc'}, 'gpt-5.6-sol', Fake())

    def test_malformed_code_fence_is_sanitized(self):
        class Fake:
            def call(self, model, prompt, **kwargs):
                return {'text': '```', 'model': model}
        with self.assertRaises(ModelError):
            hybrid_review({}, 'gpt-5.6-sol', Fake())

    def test_benchmark_identical_evidence(self):
        class Fake:
            prompts = []
            def call(self, model, prompt, **kwargs):
                self.prompts.append((model, prompt))
                return {'text': json.dumps({'decisions': [{'id': 'missing_approval', 'decision': 'BLOCK'}, {'id': 'stale_evidence', 'decision': 'BLOCK'}, {'id': 'failed_dependency', 'decision': 'BLOCK'}, {'id': 'safe_read', 'decision': 'ALLOW'}]}), 'model': model, 'success': True}
        client = Fake()
        report = model_check(client)
        self.assertEqual(len(client.prompts), 3)
        self.assertEqual(client.prompts[1][1], client.prompts[2][1])
        self.assertFalse(report['approval_granted'])
        self.assertEqual(report['comparisons'][0]['correct'], 4)
        self.assertTrue(report['success'])

    def test_supervisor_receives_independent_evidence_and_actual_plan(self):
        class Fake:
            prompts = []
            def call(self, model, prompt, **kwargs):
                self.prompts.append(prompt)
                if model == 'gpt-5.6-terra':
                    report = {'summary': 'UNIQUE_PROPOSAL_749', 'steps': ['Implement despite absent approval'], 'blockers': []}
                else:
                    report = {'summary': 'Unsafe proposal', 'decision': 'BLOCK', 'findings': ['Missing approval'], 'required_evidence': ['Approval']}
                return {'text': json.dumps(report), 'model': model, 'success': True}
        client = Fake()
        result = hybrid_review({'human_approval': False, 'evidence_hash': 'UNIQUE_EVIDENCE_913'}, 'gpt-5.6-sol', client)
        self.assertIn('ORCHESTRATOR_PROPOSAL', client.prompts[1])
        self.assertIn('UNIQUE_PROPOSAL_749', client.prompts[1])
        self.assertIn('UNIQUE_EVIDENCE_913', client.prompts[1])
        self.assertIn('independently', client.prompts[1].lower())
        self.assertFalse(result['approval_granted'])

    def test_benchmark_access_failure_reports_failure(self):
        class Fake:
            def call(self, *args, **kwargs):
                raise ModelError('Router access unavailable.')
        self.assertFalse(model_check(Fake())['success'])

    def test_current_request_is_authority_not_historical_evidence(self):
        from governor_workbench.llm import _review_input
        rule,body=_review_input({'current_request':{'authorized':True,'scope':'read_only_advisory'},'sources':[]})
        self.assertIn('CURRENT_REQUEST',body.split('EVIDENCE:')[0])
        self.assertNotIn('current_request',body.split('EVIDENCE:')[1])

    def test_benchmark_incorrect_answers_report_failure(self):
        class Fake:
            def call(self, model, prompt, **kwargs):
                return {'success': True, 'model': model, 'text': json.dumps({'decisions': [
                    {'id': case, 'decision': 'ALLOW'} for case in ('missing_approval', 'stale_evidence', 'failed_dependency', 'safe_read')
                ]})}
        report = model_check(Fake())
        self.assertTrue(all(pair['available'] for pair in report['comparisons']))
        self.assertFalse(report['success'])

