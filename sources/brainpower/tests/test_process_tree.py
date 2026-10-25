import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from governor_workbench.jobs import run_process, JobCancelled


@unittest.skipUnless(os.name == 'nt', 'Windows job ownership')
class WindowsProcessTreeTests(unittest.TestCase):
    def setUp(self):
        import ctypes
        from ctypes import wintypes
        self.ctypes = ctypes
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.kernel.OpenProcess.restype = wintypes.HANDLE
        self.kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.handles = []

    def tearDown(self):
        for handle in self.handles:
            if self.kernel.WaitForSingleObject(handle, 0) == 258:
                self.kernel.TerminateProcess(handle, 1)
                self.kernel.WaitForSingleObject(handle, 3000)
            self.kernel.CloseHandle(handle)

    def remember(self, line):
        if line.startswith('LEAF:'):
            handle = self.kernel.OpenProcess(0x100001, False, int(line[5:]))
            self.assertTrue(handle)
            self.handles.append(handle)

    def tree_command(self, exit_parent):
        leaf = 'import time; time.sleep(30)'
        command = ('import subprocess,sys,time; '
                   f'p=subprocess.Popen([sys.executable,"-c",{leaf!r}]); '
                   'print("LEAF:"+str(p.pid),flush=True); time.sleep(0.4); '
                   + ('print("EXITING",flush=True); sys.exit(0)' if exit_parent else 'time.sleep(30)'))
        return [sys.executable, '-u', '-c', command]

    def test_parent_exit_also_closes_descendants_and_output_pipe(self):
        exiting=[]
        def remember_exit(line):
            self.remember(line)
            if line=='EXITING':exiting.append(time.monotonic())
        with tempfile.TemporaryDirectory() as folder:
            code, _ = run_process(self.tree_command(True), folder, os.environ.copy(),
                                  threading.Event(), remember_exit, timeout=12)
        # Allow bounded cold startup, but independently require prompt tree/pipe cleanup.
        self.assertEqual(len(exiting),1)
        self.assertLess(time.monotonic()-exiting[0],2,'Tree cleanup stalled after payload exit')
        self.assertEqual(code, 0)
        self.assertEqual(len(self.handles), 1)
        self.assertEqual(self.kernel.WaitForSingleObject(self.handles[0], 2000), 0)

    def test_cancel_terminates_tree_without_taskkill(self):
        cancel = threading.Event()
        cancelled=[]
        def line(value):
            self.remember(value)
            if self.handles:
                cancelled.append(time.monotonic());cancel.set()
        with tempfile.TemporaryDirectory() as folder:
            with patch('governor_workbench.jobs.subprocess.run', side_effect=AssertionError('no PID-based taskkill')):
                with self.assertRaises(JobCancelled):
                    run_process(self.tree_command(False), folder, os.environ.copy(), cancel, line, 12)
        self.assertTrue(cancelled)
        self.assertLess(time.monotonic()-cancelled[0],2,'Tree cleanup stalled after cancellation')
        self.assertEqual(len(self.handles), 1)
        self.assertEqual(self.kernel.WaitForSingleObject(self.handles[0], 2000), 0)

    def test_assignment_failure_never_starts_payload(self):
        from governor_workbench.process_tree import WindowsJob
        with tempfile.TemporaryDirectory() as folder:
            marker = Path(folder) / 'must-not-exist'
            with patch.object(WindowsJob, 'assign', side_effect=OSError('assignment denied')):
                with self.assertRaises(OSError):
                    run_process([sys.executable, '-c', 'from pathlib import Path; Path("must-not-exist").touch()'],
                                folder, os.environ.copy(), threading.Event(), lambda line: None, 3)
            self.assertFalse(marker.exists())

    def test_owner_death_kills_payload_but_not_unrelated_process(self):
        root = str(Path(__file__).resolve().parents[1])
        source = ('import sys,os,time; sys.path.insert(0,' + repr(root) + '); '
                  'from governor_workbench.process_tree import start_owned_windows; '
                  'p,j=start_owned_windows([sys.executable,"-u","-c",'
                  '\'import os,time; print("LEAF:"+str(os.getpid()),flush=True); time.sleep(30)\'],'
                  'os.getcwd(),os.environ.copy()); '
                  'print(p.stdout.readline().strip(),flush=True); time.sleep(30)')
        unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'],
                                     creationflags=subprocess.CREATE_NO_WINDOW)
        owner = subprocess.Popen([sys.executable, '-u', '-c', source], stdout=subprocess.PIPE,
                                 text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        timer = threading.Timer(12, owner.kill)  # Startup watchdog; post-kill checks remain separate below.
        timer.start()
        try:
            self.remember(owner.stdout.readline().strip())
            self.assertEqual(len(self.handles), 1)
            owner.kill(); owner.wait(timeout=3)
            self.assertEqual(self.kernel.WaitForSingleObject(self.handles[0], 3000), 0)
            self.assertIsNone(unrelated.poll())
        finally:
            timer.cancel()
            if owner.poll() is None: owner.kill()
            owner.wait(timeout=3); owner.stdout.close()
            unrelated.kill(); unrelated.wait(timeout=3)
