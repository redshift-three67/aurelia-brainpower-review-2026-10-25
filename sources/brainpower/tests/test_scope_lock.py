"""A model job may wait for the observer's scope scan before its final drift check."""
import threading
import time
import unittest
from types import SimpleNamespace

from governor_workbench.server import Application
from governor_workbench.store import JobBusy


class ScopeLockTests(unittest.TestCase):
    def test_bounded_worker_wait_avoids_false_busy_and_keeps_browser_nonblocking(self):
        app = Application.__new__(Application)
        app.scope_lock = threading.Lock()
        app.scope_cache = {}
        app.registry = SimpleNamespace(list_projects=lambda: [])
        app.store = SimpleNamespace(decisions=lambda: [], planned=lambda: [])
        app._scope_service = SimpleNamespace(context=lambda *args, **kwargs: {'scope_hash': 'stable'})

        app.scope_lock.acquire()
        release = threading.Thread(target=lambda: (time.sleep(.05), app.scope_lock.release()))
        release.start()
        try:
            with self.assertRaises(JobBusy):
                app.scope_context('project', 'test')
            self.assertEqual('stable', app.scope_context('project', 'test', wait_for_lock=1)['scope_hash'])
        finally:
            release.join(2)
            self.assertFalse(release.is_alive())


if __name__ == '__main__':
    unittest.main()
