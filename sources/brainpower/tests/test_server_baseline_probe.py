import importlib.util
from pathlib import Path
import unittest


class BaselineSanitizationTests(unittest.TestCase):
    def load(self):
        path = Path(__file__).resolve().parents[1]/'artifacts/server-baseline-probe-20260919.py'
        self.assertTrue(path.exists(), 'Baseline probe not implemented')
        spec = importlib.util.spec_from_file_location('baseline_probe', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_ssh_only_expected_fields_and_values(self):
        probe = self.load()
        result = probe.ssh_summary('permitrootlogin no\npasswordauthentication no\nsecret TOPSECRET\npubkeyauthentication unexpected-secret\n')
        self.assertEqual(result, {'permitrootlogin': 'no', 'passwordauthentication': 'no'})

    def test_firewall_does_not_export_addresses_comments(self):
        probe = self.load()
        rule = {'nftables': [{'rule': {'family': 'inet', 'table': 't', 'chain': 'input',
                'comment': 'TOPSECRET', 'expr': [{'match': {'left': {'payload': {'protocol': 'tcp', 'field': 'dport'}}, 'right': 22, 'op': '=='}},
                {'match': {'left': {'payload': {'protocol': 'ip', 'field': 'saddr'}}, 'right': 'PRIVATE-IP', 'op': '=='}}, {'accept': None}]}}]}
        result = probe.firewall_summary(rule)
        self.assertEqual(result['accept_rules'][0]['destination_ports'], [22])
        self.assertTrue(result['accept_rules'][0]['additional_conditions'])
        self.assertNotIn('TOPSECRET', str(result))
        self.assertNotIn('PRIVATE-IP', str(result))

    def test_malformed_firewall_rejected(self):
        probe = self.load()
        with self.assertRaises(ValueError):
            probe.firewall_summary({})
