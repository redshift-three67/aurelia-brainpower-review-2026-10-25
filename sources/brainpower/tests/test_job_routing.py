import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from governor_workbench.store import Store
from governor_workbench.model_usage import TrackedClient
from governor_workbench.llm import ModelError


class JobRoutingTests(unittest.TestCase):
    def test_receipt_persists_selection_and_failed_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp)/'db')
            job = store.create_job('scope_patch', None)
            choice = dict(requested='auto', effective='low', role='orchestrator', reason='fixture', version='rh1-v1')
            class Client:
                def call(self, model, prompt, **kwargs):
                    if kwargs['reasoning'] != 'low': raise AssertionError('wrong payload')
                    raise ModelError('synthetic failure')
            with self.assertRaises(ModelError):
                TrackedClient(Client(), store, job['id'], routing=lambda model: choice).call('gpt-5.6-terra', 'x')
            usage = store.job(job['id'])['token_usage']
            self.assertEqual(usage['calls'][0]['routing'], choice)
            self.assertEqual(usage['calls'][0]['status'], 'failed')
            self.assertIsNone(usage['total_tokens'])

    def test_changed_routing_blocks_before_transport(self):
        from governor_workbench.job_routing import snapshot, JobRouting
        settings = dict(supervisor='gpt-5.6-sol', reasoning_mode='medium')
        app = SimpleNamespace(config={'orchestrator_transport':'hermes', 'router_url':'http://127.0.0.1:3000/v1'}, settings=lambda: dict(settings))
        job = dict(action='scope_plan', request={'_model_routing': snapshot(app, 'gpt-5.6-sol')})
        routing = JobRouting(app, job, 'gpt-5.6-sol')
        self.assertEqual(routing('gpt-5.6-terra')['effective'], 'medium')
        settings['reasoning_mode'] = 'high'
        with self.assertRaises(ModelError): routing('gpt-5.6-terra')

    def test_legacy_job_never_inherits_high_or_auto(self):
        from governor_workbench.job_routing import JobRouting
        app = SimpleNamespace(config={}, settings=lambda:dict(supervisor='gpt-5.6-sol',reasoning_mode='high'))
        choice = JobRouting(app, dict(action='scope_plan',request={}), 'gpt-5.6-sol')('gpt-5.6-terra')
        self.assertEqual(choice['effective'], 'medium')
        self.assertIn('Altauftrag', choice['reason'])

    def test_routine_low_is_lost_after_question_and_blocked_on_scope_drift(self):
        from governor_workbench.job_routing import snapshot, JobRouting
        answers=[]
        scope={'scope_hash':'a'*64}
        step={'action':'change','depends_on':[],'scope':['docs/help.md']}
        app=SimpleNamespace(config={},settings=lambda:dict(supervisor='gpt-5.6-sol',reasoning_mode='auto'),
            questions=SimpleNamespace(answers=lambda key:answers),scope_context=lambda *a,**k:scope,
            store=SimpleNamespace(job=lambda key:dict(action='scope_plan',status='completed',request={})))
        req=dict(scope_kind='project',scope_id='pilot',scope_hash='a'*64,routine_note='Unkritische Routine',_model_routing=snapshot(app,'gpt-5.6-sol'))
        job=dict(id='fixture',action='scope_patch',request=req)
        routing=JobRouting(app,job,'gpt-5.6-sol')
        routing.enable_routine(step)
        with patch('governor_workbench.change_execution.resolve',return_value=({'job_id':'plan'},step,{})):
            self.assertEqual('low',routing('gpt-5.6-terra')['effective'])
            self.assertEqual('medium',routing('gpt-5.6-sol')['effective'])
            answers.append({'answer':'complexity'})
            self.assertEqual('medium',routing('gpt-5.6-terra')['effective'])
            scope['scope_hash']='b'*64
            with self.assertRaises(ModelError):routing('gpt-5.6-terra')

    def test_repair_plan_origin_cannot_be_lowered_by_routine_confirmation(self):
        from governor_workbench.job_routing import snapshot, JobRouting
        step={'action':'change','depends_on':[],'scope':['docs/help.md']}
        app=SimpleNamespace(config={},settings=lambda:dict(supervisor='gpt-5.6-sol',reasoning_mode='auto'),
            questions=SimpleNamespace(answers=lambda key:[]),scope_context=lambda *a,**k:{'scope_hash':'a'*64},
            store=SimpleNamespace(job=lambda key:dict(action='scope_plan',status='completed',request={'repair_binding':{'diagnosis':'fixture'}})))
        req=dict(scope_kind='project',scope_id='pilot',scope_hash='a'*64,routine_note='Routine bestätigt',_model_routing=snapshot(app,'gpt-5.6-sol'))
        routing=JobRouting(app,dict(id='patch',action='scope_patch',request=req),'gpt-5.6-sol')
        routing.enable_routine(step)
        with patch('governor_workbench.change_execution.resolve',return_value=({'job_id':'repair-plan'},step,{})):
            self.assertEqual('medium',routing('gpt-5.6-terra')['effective'])

    def test_drift_creates_no_call_receipt_and_no_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=Store(Path(tmp)/'db');job=store.create_job('scope_plan',None)
            from unittest.mock import Mock
            transport=Mock()
            transport.prompt_limit.return_value=120000
            def blocked(model):raise ModelError('routing changed')
            with self.assertRaises(ModelError):TrackedClient(transport,store,job['id'],routing=blocked).call('gpt-5.6-terra','x')
            transport.call.assert_not_called()
            self.assertFalse(store.job(job['id'])['token_usage']['recorded'])

    def test_new_settings_survive_without_altering_auto_reviews(self):
        from governor_workbench.server import Application
        with tempfile.TemporaryDirectory() as tmp:
            app = Application.__new__(Application)
            app.store = Store(Path(tmp)/'db')
            app.config = dict(supervisor='gpt-5.6-sol')
            app.event = lambda *a: None
            app.update_settings({'reasoning_mode':'auto'})
            self.assertEqual(app.settings()['reasoning_mode'], 'auto')
            self.assertFalse(app.settings()['auto_review'])
            with self.assertRaises(ValueError): app.update_settings({'reasoning_mode':'ultra'})


if __name__ == '__main__': unittest.main()
