import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from governor_workbench.jobs import run_process, JobCancelled, evidence_stale, verified_runs


class ProcessTests(unittest.TestCase):
    def test_pre_cancel_does_not_launch_any_process(self):
        from unittest.mock import patch
        event = threading.Event(); event.set()
        with patch('governor_workbench.jobs.subprocess.Popen', side_effect=AssertionError('must not launch')) as launch:
            with self.assertRaises(JobCancelled):
                run_process([sys.executable], '.', {}, event, lambda line: None)
        launch.assert_not_called()

    def test_long_output_is_bounded_and_truncation_is_visible(self):
        with tempfile.TemporaryDirectory() as folder:
            lines = []
            code, output = run_process([sys.executable, '-c', 'print("x"*250000)'],
                folder, os.environ.copy(), threading.Event(), lines.append, 12)
        self.assertEqual(code, 0)
        self.assertLessEqual(len(output), 100000)
        self.assertIn('[Ausgabe gekürzt]', output)
        self.assertTrue(all(len(line) <= 12000 for line in lines))

    def test_invalid_timeout_never_launches(self):
        from unittest.mock import patch
        for timeout in (0, -1, float('inf'), float('nan'), True):
            with self.subTest(timeout=timeout), patch('governor_workbench.jobs.subprocess.Popen', side_effect=AssertionError('must not launch')) as launch:
                with self.assertRaises(ValueError):
                    run_process([sys.executable], '.', {}, threading.Event(), lambda line: None, timeout)
                launch.assert_not_called()

    def test_output_callback_failure_reaps_direct_child(self):
        from unittest.mock import patch
        import subprocess
        launched = []
        original = subprocess.Popen
        def capture(*args, **kwargs):
            process = original(*args, **kwargs)
            launched.append(process)
            return process
        def fail(line):
            failed.append(time.monotonic())
            raise RuntimeError('consumer failed')
        failed=[]
        with tempfile.TemporaryDirectory() as folder:
            with patch('governor_workbench.jobs.subprocess.Popen', side_effect=capture):
                with self.assertRaisesRegex(RuntimeError, 'consumer failed'):
                    run_process([sys.executable, '-u', '-c', 'import time; print("ready"); time.sleep(30)'],
                        folder, os.environ.copy(), threading.Event(), fail, 12)
        self.assertTrue(failed)
        self.assertLess(time.monotonic()-failed[0],2,'Callback failure did not promptly reap the child')
        self.assertIsNotNone(launched[0].poll())

    def test_rule_change_does_not_discard_unchanged_legacy_test_evidence(self):
        observation={'evidence_hash':'new-rules','source_hash':'same-sources','evidence_complete':True}
        jobs=[{'action':'radiworks_tests','status':'completed','result':{'evidence_hash':'same-sources','stale':False}}]
        self.assertEqual(1,len(verified_runs(jobs,observation)))
        observation['source_hash']='changed-sources'
        self.assertEqual([],verified_runs(jobs,observation))
    def test_incomplete_evidence_never_enters_verified_context(self):
        observation={'evidence_hash':'same','evidence_complete':False}
        jobs=[{'action':'radiworks_tests','status':'completed','result':{'evidence_hash':'same','stale':False}}]
        self.assertTrue(evidence_stale(observation,observation))
        self.assertEqual([],verified_runs(jobs,observation))

    def test_output_and_exit_code(self):
        with tempfile.TemporaryDirectory() as folder:
            lines=[]
            # Output/exit semantics allow cold startup; the dedicated timeout test below stays at .2s.
            code,out=run_process([sys.executable,'-c','print("proof"); raise SystemExit(3)'],folder,os.environ.copy(),threading.Event(),lines.append,12)
        self.assertEqual(3,code); self.assertIn('proof',out); self.assertIn('proof',lines)

    def test_timeout_terminates_owned_process(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(TimeoutError):
                run_process([sys.executable,'-c','import time; time.sleep(10)'],folder,os.environ.copy(),threading.Event(),lambda line:None,.2)

    def test_cancel_terminates_owned_process(self):
        event=threading.Event(); event.set()
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(JobCancelled):
                run_process([sys.executable,'-c','import time; time.sleep(10)'],folder,os.environ.copy(),event,lambda line:None,5)

    @unittest.skipUnless(os.name=='nt','Windows cleanup')
    def test_cancel_does_not_use_pid_based_taskkill(self):
        from unittest.mock import patch
        import subprocess
        event=threading.Event()
        cancelled=[]
        def cancel(line):
            cancelled.append(time.monotonic());event.set()
        with tempfile.TemporaryDirectory() as folder:
            with patch('governor_workbench.jobs.subprocess.run',return_value=subprocess.CompletedProcess([],1)) as cleanup:
                with self.assertRaises(JobCancelled):
                    run_process([sys.executable,'-u','-c','import time; print("ready"); time.sleep(30)'],folder,os.environ.copy(),event,cancel,12)
                cleanup.assert_not_called()
        self.assertTrue(cancelled)
        self.assertLess(time.monotonic()-cancelled[0],2,'Cancellation did not promptly stop the child')

if __name__=='__main__': unittest.main()
