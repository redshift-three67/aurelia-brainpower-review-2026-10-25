import unittest
from raid_health import sample_raid


class RaidHealthTests(unittest.TestCase):
    def run_samples(self, samples):
        values = iter(samples)
        clock = [0.0]
        def pause(seconds):
            clock[0] += seconds
        return sample_raid(lambda: next(values), pause=pause, clock=lambda: clock[0])

    def test_healthy_single_read(self):
        self.assertEqual(self.run_samples([(0, 'clean')])['state'], 'clean')

    def test_transition_must_resolve(self):
        data = self.run_samples([(0, 'write-pending'), (0, 'active')])
        self.assertEqual(data['state'], 'active')
        self.assertEqual(len(data['samples']), 2)

    def test_persistent_transition_fails(self):
        with self.assertRaisesRegex(ValueError, 'transition_not_resolved'):
            self.run_samples([(0, 'write-pending')] * 20)

    def test_degradation_never_retried_as_transition(self):
        for sample in [(1, 'write-pending'), (1, 'clean'), (-1, 'active')]:
            with self.subTest(sample=sample), self.assertRaises(ValueError):
                self.run_samples([sample])

    def test_other_bad_states_fail_immediately(self):
        for state in ('readonly', 'inactive', 'clear', 'broken', 'unknown'):
            with self.subTest(state=state), self.assertRaises(ValueError):
                self.run_samples([(0, state)])

    def test_failure_after_transition_not_hidden(self):
        with self.assertRaises(ValueError):
            self.run_samples([(0, 'write-pending'), (1, 'active')])

    def test_read_failure_propagates(self):
        def fail():
            raise OSError('unreadable')
        with self.assertRaises(OSError):
            sample_raid(fail)
