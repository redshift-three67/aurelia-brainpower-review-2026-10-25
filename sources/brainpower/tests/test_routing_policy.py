import unittest
from types import SimpleNamespace
from unittest.mock import patch


class RoutingPolicyTests(unittest.TestCase):
    def policy(self):
        from governor_workbench import routing_policy
        return routing_policy

    def test_policy_exists(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('governor_workbench.routing_policy'))

    def test_default_and_unknown_work_are_medium(self):
        p = self.policy()
        for mode in ('medium', 'auto'):
            self.assertEqual(p.choose(mode, 'gpt-5.6-terra')['effective'], 'medium')

    def test_auto_only_lowers_confirmed_routine_orchestrator(self):
        p = self.policy()
        self.assertEqual(p.choose('auto', 'gpt-5.6-terra', routine=True)['effective'], 'low')
        for model in ('gpt-5.6-sol', 'gpt-6-astra'):
            self.assertEqual(p.choose('auto', model, routine=True)['effective'], 'medium')
        self.assertEqual(p.choose('medium', 'gpt-5.6-terra', routine=True)['effective'], 'medium')

    def test_high_is_only_explicit_and_unknowns_rejected(self):
        p = self.policy()
        for value in ('high', 'xhigh'):
            self.assertEqual(p.choose(value, 'gpt-6-astra')['effective'], value)
        for value in ('low', 'ultra', True, None, []):
            with self.assertRaises(ValueError): p.choose(value, 'gpt-5.6-terra')
        with self.assertRaises(ValueError): p.choose('auto', 'unknown')

    def test_routine_requires_bound_independent_documentation(self):
        p = self.policy()
        step = {'action': 'change', 'scope': ['docs/help.md'], 'depends_on': []}
        self.assertTrue(p.routine_step(step, 'Unkritische Dokumentationspflege'))
        for bad in (dict(step, scope=['app.py']), dict(step, depends_on=['a']),
                    dict(step, scope=[]), dict(step, scope=['../help.md']),
                    dict(step, scope=['docs/help.md', 'run.ps1'])):
            self.assertFalse(p.routine_step(bad, 'bestätigt'))
        self.assertFalse(p.routine_step(step, ''))

    def test_router_payload_uses_selected_effort(self):
        from governor_workbench.llm import RouterClient
        client = RouterClient('http://127.0.0.1:3000/v1')
        for effort in ('low', 'medium', 'high', 'xhigh'):
            with patch.object(client, '_request', return_value={'model': 'gpt-5.6-terra', 'output_text': 'ok'}) as request:
                result = client.call('gpt-5.6-terra', 'synthetic', reasoning=effort)
                self.assertEqual(request.call_args.args[2], effort)
                self.assertEqual(result['requested_reasoning'], effort)

    def test_hermes_guard_requires_exact_selected_effort(self):
        from governor_workbench.hermes_runner import validate_request
        agent = SimpleNamespace(tools=[], valid_tool_names=set())
        body = dict(model='gpt-5.6-terra', tools=[], reasoning={'effort': 'low'}, store=False)
        validate_request(body, agent, 0, body['model'], 'http://127.0.0.1:3000/v1', 'low')
        with self.assertRaises(RuntimeError):
            validate_request(body, agent, 0, body['model'], 'http://127.0.0.1:3000/v1', 'medium')
        for value in ('ultra', True):
            with self.assertRaises((ValueError, RuntimeError)):
                validate_request(dict(body, reasoning={'effort': value}), agent, 0, body['model'], 'http://127.0.0.1:3000/v1', value)


if __name__ == '__main__': unittest.main()
