import json
import threading
import unittest
from unittest.mock import Mock,patch
from governor_workbench.runtime_profiles import RuntimeProfiles


class RuntimeReadinessTests(unittest.TestCase):
    def simulate(self,ready_after):
        manager=RuntimeProfiles.__new__(RuntimeProfiles)
        manager.lock=threading.RLock();manager.closing=threading.Event();manager.active=None
        manager.config={'data_dir':'.','port':8787}
        manager.profile=Mock(return_value={'id':'local_probe','hash':'fixture','port':8794,'supported':True})
        manager._save=Mock();manager._finish=Mock()
        clock=[0.0];cancel=Mock();cancel.is_set.return_value=False
        cancel.wait.side_effect=lambda delay:clock.__setitem__(0,clock[0]+delay)
        process=Mock();process.poll.return_value=None
        response=Mock()
        def read(limit):
            row=manager.active[0]
            return json.dumps({'service':'governor-runtime-probe','instance_id':row['id'] if clock[0]>=ready_after else 'wrong-instance'}).encode()
        response.read.side_effect=read
        opener=Mock();opener.open.return_value.__enter__=Mock(return_value=response)
        opener.open.return_value.__exit__=Mock(return_value=False)
        with patch('governor_workbench.runtime_profiles.time.monotonic',side_effect=lambda:clock[0]),patch('governor_workbench.runtime_profiles.socket.socket'),patch('governor_workbench.runtime_profiles.start_owned_windows',return_value=(process,Mock())),patch('governor_workbench.runtime_profiles.urllib.request.build_opener',return_value=opener):
            try:result=manager.start('local_probe','fixture',cancel)
            except ValueError as error:result=error
        return manager,clock[0],result

    def test_verified_cold_start_can_complete_after_six_seconds(self):
        manager,elapsed,result=self.simulate(7)
        self.assertIsInstance(result,dict,result)
        self.assertTrue(result['readiness_verified'])
        self.assertGreaterEqual(elapsed,7);self.assertLess(elapsed,12)
        manager._finish.assert_not_called()

    def test_wrong_instance_remains_bounded_and_closes_owned_process(self):
        manager,elapsed,result=self.simulate(float('inf'))
        self.assertIsInstance(result,ValueError)
        self.assertGreaterEqual(elapsed,12);self.assertLess(elapsed,12.1)
        manager._finish.assert_called_once_with('failed','Start ohne Bereitschaft oder abgebrochen.')
