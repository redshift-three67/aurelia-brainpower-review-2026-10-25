import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from governor_workbench.evidence import Observer


class ObserverShutdownTests(unittest.TestCase):
    def test_shutdown_stops_followup_git_commands(self):
        stop=threading.Event()
        observer=Observer({'projects':[],'git_interval':60})
        observer.stop_event=stop
        stop.set()
        with patch('governor_workbench.evidence.subprocess.run') as run:
            result=observer.git(Path.cwd(),['status','--porcelain'])
        run.assert_not_called()
        self.assertNotEqual(0,result[0])


if __name__=='__main__':unittest.main()
