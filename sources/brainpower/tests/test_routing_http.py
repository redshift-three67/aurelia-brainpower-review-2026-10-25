"""Actual HTTP/settings/worker integration; synthetic model transport only."""
import unittest
from unittest.mock import patch
from tests import test_server


class RoutingHttpTests(unittest.TestCase):
    setUp=test_server.ServerTests.setUp
    cleanup=test_server.ServerTests.cleanup
    request=test_server.ServerTests.request
    auth=test_server.ServerTests.auth
    wait_terminal=test_server.ServerTests.wait_terminal

    def test_settings_dispatch_receipts_and_admission_drift(self):
        app=self.server.app
        self.assertEqual(403,self.request('POST','/api/settings',{'reasoning_mode':'high'})[0])
        self.assertEqual(400,self.request('POST','/api/settings',{'reasoning_mode':'low'},self.auth())[0])
        sent=[]
        def transport(client,model,prompt,**kwargs):
            sent.append((model,kwargs['reasoning']))
            return {'success':True,'text':'synthetic','usage':{'total_tokens':2}}
        def check(client,**kwargs):
            for model in ('gpt-5.6-terra','gpt-5.6-sol'):
                client.call(model,'synthetic',**kwargs)
            return {'success':True}
        with patch('governor_workbench.jobs.model_check',side_effect=check),patch('governor_workbench.jobs.RouterClient.call',new=transport):
            for mode,effort in (('high','high'),('auto','medium')):
                status,_,_=self.request('POST','/api/settings',{'reasoning_mode':mode},self.auth())
                self.assertEqual(200,status)
                status,response,_=self.request('POST','/api/actions',{'action':'model_check'},self.auth())
                self.assertEqual(202,status,response)
                job=self.wait_terminal(lambda:app.store.job(response['job']['id']),('queued','running'))
                self.assertEqual('completed',job['status'],job)
                self.assertEqual(mode,job['request']['_model_routing']['mode'])
                self.assertEqual([effort,effort],[r['routing']['effective'] for r in job['token_usage']['calls']])
                self.assertFalse(app.settings()['auto_review'])
            # Freeze admission at its real queue boundary, then change settings.
            with patch.object(app.runner.pending,'put'):
                admitted=app.runner.submit('model_check')
            app.update_settings({'reasoning_mode':'medium'})
            from governor_workbench.llm import ModelError
            import threading
            before=list(sent)
            with self.assertRaises(ModelError):app.runner.execute(admitted,app.settings()['supervisor'],threading.Event())
            self.assertEqual(before,sent)
            self.assertFalse(app.store.job(admitted['id'])['token_usage']['recorded'])
            app.store.update_job(admitted['id'],status='cancelled')


if __name__=='__main__':unittest.main()
