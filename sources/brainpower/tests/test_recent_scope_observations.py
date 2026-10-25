import time
import unittest

from governor_workbench.server import recent_scope_observations


class RecentScopeObservationsTests(unittest.TestCase):
    def test_only_current_signature_and_recent_exact_scope_are_exposed(self):
        tick = time.monotonic()
        cache = {
            ('project', 'grouped', False): ('current', tick - 2, {
                'scope_hash': 'project-hash', 'observed_at': '2026-09-25T10:00:00Z'}),
            ('group', 'product', False): ('current', tick - 16, {
                'scope_hash': 'old-hash', 'observed_at': '2026-09-25T09:00:00Z'}),
            ('project', 'changed', True): ('old-signature', tick - 1, {
                'scope_hash': 'wrong-hash', 'observed_at': '2026-09-25T10:00:00Z'}),
        }
        self.assertEqual([dict(kind='project', id='grouped', scope_hash='project-hash',
                               observed_at='2026-09-25T10:00:00Z', stale=False)],
                         recent_scope_observations(cache, 'current', tick))

    def test_newest_entry_wins_for_same_scope(self):
        tick = time.monotonic()
        cache = {
            ('project', 'grouped', False): ('current', tick - 5, {'scope_hash': 'old', 'observed_at': 'old'}),
            ('project', 'grouped', True): ('current', tick - 1, {'scope_hash': 'new', 'observed_at': 'new'}),
        }
        self.assertEqual('new', recent_scope_observations(cache, 'current', tick)[0]['scope_hash'])


if __name__ == '__main__':
    unittest.main()
