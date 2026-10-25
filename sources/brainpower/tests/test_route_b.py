"""Optional Sol/Luna/Astra route with synthetic, bounded model responses."""
import json
import threading
import unittest
from types import SimpleNamespace

from governor_workbench.llm import ModelCancelled, ModelError
from governor_workbench.route_b import run


SAFE = dict(critical_decision=False, material_contradiction=False, reason='No current consequential decision or conflict.')
REVIEW = dict(summary='Independent evidence checked', decision='REVIEW_ONLY', findings=[], required_evidence=[])
PLAN = dict(summary='Read current contract', steps=[dict(
    id='read', title='Inspect contract', project_id='one', priority=1, depends_on=[],
    rationale='Establish source', scope=['README.md'], tests=['Verify cited content'], action='review')])
CONTEXT = dict(plan_ready=True, review_scope=dict(kind='project', id='one'),
               scope_hash='a'*64, registry_projects=[dict(id='one')],
               evidence_marker='synthetic source evidence')


class Client:
    def __init__(self, replies): self.replies, self.calls = replies, []

    def call(self, model, prompt, **kwargs):
        self.calls.append((model, prompt, kwargs))
        reply = self.replies[len(self.calls)-1]
        if isinstance(reply, Exception): raise reply
        return dict(text=json.dumps(reply), success=True, requested_model=model,
                    actual_model=model, model=model)


class RouteBTests(unittest.TestCase):
    def test_plan_with_clean_luna_review_still_gets_independent_astra_and_retains_gates(self):
        client=Client([dict(proposal=PLAN,risk=SAFE),dict(review=REVIEW,risk=SAFE),
                       dict(review=REVIEW,risk=SAFE)])
        result=run(CONTEXT,client,plan=True)
        self.assertEqual(['gpt-6-sol','gpt-6-luna','gpt-6-astra'],[call[0] for call in client.calls])
        self.assertEqual(PLAN,result['proposal'])
        self.assertEqual('b_plus_v1',result['route_variant'])
        self.assertEqual('mandatory_plan',result['critical_review_reason'])
        self.assertEqual(REVIEW,result['review'])
        self.assertFalse(result['approval_granted'])
        self.assertTrue(result['critical_review_required'])
        self.assertIn('synthetic source evidence',client.calls[1][1])
        self.assertIn('PROPOSAL',client.calls[1][1])
        self.assertIn('synthetic source evidence',client.calls[2][1])
        self.assertNotIn('WORKER_REPORT',client.calls[2][1])

    def test_astra_plan_review_does_not_receive_luna_findings(self):
        marker='Luna-only private finding marker'
        blocker=dict(summary='Unresolved',decision='BLOCK',findings=[marker],required_evidence=[])
        client=Client([dict(proposal=PLAN,risk=SAFE),dict(review=blocker,risk=SAFE),
                       dict(review=REVIEW,risk=SAFE)])
        result=run(CONTEXT,client,plan=True)
        self.assertNotIn(marker,client.calls[2][1])
        self.assertEqual('BLOCK',result['review']['decision'])
        self.assertIn(marker,result['review']['findings'])

    def test_worker_detects_contradiction_and_astra_block_cannot_be_overridden(self):
        flagged=dict(SAFE,material_contradiction=True,reason='Equal-authority evidence conflicts.')
        blocker=dict(summary='Restore unresolved',decision='BLOCK',findings=['No independent restore proof'],required_evidence=[])
        client=Client([dict(proposal=PLAN,risk=SAFE),dict(review=REVIEW,risk=flagged),
                       dict(review=blocker,risk=flagged)])
        result=run(CONTEXT,client,plan=True)
        self.assertEqual(['gpt-6-sol','gpt-6-luna','gpt-6-astra'],[call[0] for call in client.calls])
        self.assertTrue(result['critical_review_required'])
        self.assertEqual('BLOCK',result['review']['decision'])
        self.assertIn('No independent restore proof',result['review']['findings'])
        self.assertFalse(result['approval_granted'])

    def test_operator_can_force_astra_without_model_risk_signal(self):
        client=Client([dict(plan=dict(summary='Inspect',steps=['Read'],blockers=[]),risk=SAFE),
                       dict(review=REVIEW,risk=SAFE),dict(review=REVIEW,risk=SAFE)])
        result=run(CONTEXT,client,force_critical=True)
        self.assertEqual(3,len(client.calls))
        self.assertEqual('gpt-6-astra',client.calls[-1][0])
        self.assertFalse(result['approval_granted'])

    def test_foreign_plan_and_malformed_risk_stop_before_worker(self):
        foreign=json.loads(json.dumps(PLAN));foreign['steps'][0]['project_id']='other'
        fenced=json.loads(json.dumps(PLAN));fenced['steps'][0]['tests']=['```sh\nrm -rf elsewhere\n```']
        for lead in (dict(proposal=foreign,risk=SAFE),dict(proposal=fenced,risk=SAFE),
                     dict(proposal=PLAN,risk=dict(SAFE,critical_decision='false'))):
            client=Client([lead])
            with self.subTest(lead=lead),self.assertRaises(ModelError): run(CONTEXT,client,plan=True)
            self.assertEqual(1,len(client.calls))

    def test_astra_failure_does_not_fallback_to_worker_approval(self):
        client=Client([dict(proposal=PLAN,risk=SAFE),dict(review=REVIEW,risk=SAFE),ModelError('upstream unavailable')])
        with self.assertRaises(ModelError): run(CONTEXT,client,plan=True,force_critical=True)
        self.assertEqual(3,len(client.calls))

    def test_cancel_stops_before_any_request(self):
        cancelled=threading.Event();cancelled.set()
        client=Client([])
        with self.assertRaises(ModelCancelled): run(CONTEXT,client,cancel_event=cancelled)
        self.assertEqual([],client.calls)

    def test_old_rh1_choices_remain_old(self):
        from governor_workbench.routing_policy import choose, validate_effort
        self.assertEqual('medium',choose('auto','gpt-6-astra')['effective'])
        self.assertEqual('low',choose('auto','gpt-5.6-terra',routine=True)['effective'])
        self.assertEqual('max',validate_effort('gpt-6-luna','max'))
        self.assertEqual('high',validate_effort('gpt-6-astra','high'))
        self.assertEqual('xhigh',validate_effort('gpt-6-astra','xhigh'))
        for model,effort in [('gpt-6-luna','medium'),('gpt-6-sol','medium'),('gpt-6-astra','max')]:
            with self.assertRaises(ValueError):validate_effort(model,effort)
        with self.assertRaises(ValueError):choose('auto','gpt-6-luna')

    def test_bound_route_rejects_drift_before_transport(self):
        from governor_workbench.job_routing import RouteBRouting,route_b_snapshot
        settings=dict(supervisor='gpt-5.6-sol',reasoning_mode='medium')
        app=SimpleNamespace(config={},settings=lambda:dict(settings))
        job=dict(request={'_model_routing':route_b_snapshot(app,settings['supervisor'])})
        routing=RouteBRouting(app,job,settings['supervisor'])
        self.assertEqual('high',routing('gpt-6-sol')['effective'])
        self.assertEqual('max',routing('gpt-6-luna')['effective'])
        self.assertEqual('medium',routing('gpt-6-astra')['effective'])
        stale=dict(request={'_model_routing':dict(job['request']['_model_routing'], variant='route-b-v1')})
        with self.assertRaises(ModelError): RouteBRouting(app,stale,settings['supervisor'])
        with self.assertRaises(ModelError):routing('gpt-5.6-terra')
        settings['reasoning_mode']='high'
        with self.assertRaises(ModelError):routing('gpt-6-astra')


if __name__=='__main__': unittest.main()
