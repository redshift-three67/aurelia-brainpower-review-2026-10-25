import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request


class LifecycleTests(unittest.TestCase):
    def test_real_cli_stop_releases_port_and_lock(self):
        with tempfile.TemporaryDirectory() as folder:
            with socket.socket() as candidate:
                candidate.bind(('127.0.0.1',0)); port=candidate.getsockname()[1]
            config=Path(folder)/'config.json'
            config.write_text(json.dumps({'version':1,'port':port,'projects':[]}))
            process=subprocess.Popen([sys.executable,'-m','governor_workbench','serve','--config',str(config)],
                                     stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                                     creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:
                ready=False
                for _ in range(50):
                    try:
                        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=.2): pass
                        ready=True; break
                    except OSError: time.sleep(.1)
                self.assertTrue(ready)
                result=subprocess.run([sys.executable,'-m','governor_workbench','stop','--config',str(config)],
                                      capture_output=True,text=True,timeout=35)
                self.assertEqual(0,result.returncode,result.stderr)
                self.assertEqual(0,process.wait(timeout=5))
                from governor_workbench.__main__ import instance_lock
                with instance_lock(Path(folder)/'runtime'): pass
            finally:
                if process.poll() is None: process.kill(); process.wait(timeout=5)

if __name__=='__main__': unittest.main()
