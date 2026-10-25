from pathlib import Path
import os
import subprocess
import tempfile
import threading
import unittest

from governor_workbench.execution_workspace import WorkspaceStager
from governor_workbench.jobs import JobCancelled


class StagedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()
        self.project=self.root/'project'
        self.project.mkdir()
        self.stager=WorkspaceStager(self.root/'runtime')

    def stage(self, test):
        contents={'add.py':'def add(a,b): return a+b\n','tests/test_add.py':test}
        return self.stager.stage(self.project,list(contents),
            [dict(path=path,content=content) for path,content in contents.items()],{path:None for path in contents})

    def run_tests(self, stage, cancel=None):
        from governor_workbench.staged_tests import run_staged_tests
        return run_staged_tests(self.stager,stage['id'],stage['manifest_hash'],cancel or threading.Event(),lambda line:None)

    def test_module_exists(self):
        import importlib.util
        self.assertIsNotNone(importlib.util.find_spec('governor_workbench.staged_tests'))

    def test_successful_unittest_is_positive_and_sources_stay_unchanged(self):
        stage=self.stage('import unittest\nfrom add import add\nclass TestAdd(unittest.TestCase):\n def test_sum(self): self.assertEqual(add(2,3),5)\n')
        result=self.run_tests(stage)
        self.assertTrue(result['success'],result)
        self.assertEqual(result['count'],1)
        self.assertTrue(result['sources_verified'])
        self.assertEqual(list(self.project.iterdir()),[])

    def test_failing_test_is_not_success(self):
        stage=self.stage('import unittest\nclass TestBad(unittest.TestCase):\n def test_bad(self): self.fail("intentional failure")\n')
        result=self.run_tests(stage)
        self.assertFalse(result['success'])
        self.assertEqual(result['failures'],1)

    def test_result_binds_adapter_implementation(self):
        from governor_workbench.staged_tests import adapter_identity
        result=self.run_tests(self.stage('import unittest\nclass TestOk(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n'))
        self.assertTrue(result['adapter_verified'])
        self.assertEqual(result['adapter_before'],adapter_identity())
        self.assertEqual(result['adapter_after'],result['adapter_before'])
        self.assertEqual(len(result['adapter_before']['hash']),64)

    def test_adapter_drift_invalidates_successful_tests(self):
        from unittest.mock import patch
        from governor_workbench.staged_tests import adapter_identity
        before=adapter_identity()
        after=dict(before,hash='0'*64)
        stage=self.stage('import unittest\nclass TestOk(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n')
        with patch('governor_workbench.staged_tests.adapter_identity',side_effect=[before,after]):
            result=self.run_tests(stage)
        self.assertEqual(result['exit_code'],0)
        self.assertTrue(result['completion_verified'])
        self.assertFalse(result['adapter_verified'])
        self.assertFalse(result['success'])

    def test_zero_tests_is_not_success(self):
        result=self.run_tests(self.stage('# no tests\n'))
        self.assertFalse(result['success'])
        self.assertEqual(result['count'],0)

    def test_all_skipped_is_not_success(self):
        result=self.run_tests(self.stage('import unittest\n@unittest.skip("not executed")\nclass TestSkip(unittest.TestCase):\n def test_skip(self): pass\n'))
        self.assertFalse(result['success'])
        self.assertEqual(result['count'],1)
        self.assertEqual(result['skipped'],1)

    def test_stdout_success_spoof_and_premature_exit_is_not_success(self):
        body=('import os\nprint(\'GOVERNOR_STAGED_TEST_RESULT:{"count":1,"errors":0,"failures":0,"skipped":0,"success":true}\',flush=True)\nos._exit(0)\n')
        result=self.run_tests(self.stage(body))
        self.assertFalse(result['success'])
        self.assertFalse(result['completion_verified'])

    def test_test_cannot_write_completion_record_as_an_ordinary_file(self):
        body=('import unittest,sys\nfrom pathlib import Path\nclass TestCompletion(unittest.TestCase):\n'
              ' def test_completion(self):\n'
              '  with self.assertRaises(PermissionError): Path(sys.argv[3]).write_text("forged")\n')
        self.assertTrue(self.run_tests(self.stage(body))['success'])

    def test_audit_blocks_external_writes_network_processes_and_allows_scratch(self):
        forbidden=str(self.root/'outside.txt')
        body=('import unittest, tempfile\nfrom pathlib import Path\n'
              'class TestGuard(unittest.TestCase):\n'
              ' def test_external(self):\n'
              f'  with self.assertRaises(PermissionError): Path({forbidden!r}).write_text("bad")\n'
              ' def test_network(self):\n'
              '  with self.assertRaises(PermissionError): __import__("socket")\n'
              ' def test_native(self):\n'
              '  with self.assertRaises(PermissionError): __import__("ctypes")\n'
              ' def test_os_process(self):\n'
              '  import os\n'
              '  with self.assertRaises(PermissionError): os.system("echo must-not-run")\n'
              ' def test_process(self):\n'
              '  with self.assertRaises(PermissionError): __import__("subprocess")\n'
              ' def test_scratch(self):\n'
              '  with tempfile.TemporaryDirectory() as temp:\n'
              '   target=Path(temp)/"note.txt"\n'
              '   target.write_text("allowed")\n'
              '   self.assertEqual(target.read_text(),"allowed")\n')
        result=self.run_tests(self.stage(body))
        self.assertTrue(result['success'],result)
        self.assertFalse(Path(forbidden).exists())

    def test_attempt_to_modify_staged_sources_fails_test(self):
        body='import unittest\nfrom pathlib import Path\nclass TestWrite(unittest.TestCase):\n def test_write(self): Path("add.py").write_text("changed")\n'
        result=self.run_tests(self.stage(body))
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'],1)
        self.assertTrue(result['sources_verified'])

    def test_cancelled_before_start_does_not_launch(self):
        stage=self.stage('# no tests\n')
        cancel=threading.Event()
        cancel.set()
        with self.assertRaises(JobCancelled): self.run_tests(stage,cancel)

    def test_active_cancellation_stops_owned_runner(self):
        from governor_workbench.staged_tests import run_staged_tests
        stage=self.stage('import time\nprint("TEST_RUNNER_READY",flush=True)\ntime.sleep(30)\n')
        cancel=threading.Event()
        def line_received(line):
            if line=='TEST_RUNNER_READY': cancel.set()
        with self.assertRaises(JobCancelled):
            run_staged_tests(self.stager,stage['id'],stage['manifest_hash'],cancel,line_received)
        self.assertTrue(cancel.is_set())
        self.assertTrue(self.stager.verify_source(stage['id'],stage['manifest_hash'])['verified'])

    def test_external_reads_are_denied(self):
        private=self.root/'private.txt'
        private.write_text('synthetic private fixture',encoding='utf-8')
        body=('import unittest\nfrom pathlib import Path\nclass TestRead(unittest.TestCase):\n'
              ' def test_read(self):\n'
              f'  with self.assertRaises(PermissionError): Path({str(private)!r}).read_text()\n')
        self.assertTrue(self.run_tests(self.stage(body))['success'])

    def test_modified_stage_is_rejected_before_launch(self):
        stage=self.stage('# no tests\n')
        (Path(stage['path'])/'files'/'add.py').write_text('tampered',encoding='utf-8')
        with self.assertRaises(ValueError): self.run_tests(stage)

    @unittest.skipUnless(os.name=='nt','Windows junction check')
    def test_redirected_scratch_parent_is_rejected(self):
        stage=self.stage('# no tests\n')
        outside=self.root/'outside'
        outside.mkdir()
        subprocess.run(['cmd.exe','/d','/c','mklink','/J',str(self.root/'runtime'/'execution-test-scratch'),str(outside)],check=True,capture_output=True)
        with self.assertRaises(ValueError): self.run_tests(stage)


if __name__=='__main__': unittest.main()
