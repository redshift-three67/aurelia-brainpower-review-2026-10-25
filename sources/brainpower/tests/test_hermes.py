import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import os
from governor_workbench.hermes import HermesAdapter


class HermesTests(unittest.TestCase):
    def test_isolation_blocks_external_writes_and_processes(self):
        from governor_workbench.hermes_runner import check_audit_event
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            check_audit_event('open', (str(home / 'output.txt'), 'w', os.O_WRONLY), home, False)
            with self.assertRaises(PermissionError):
                check_audit_event('open', (str(home.parent / 'outside.txt'), 'w', os.O_WRONLY), home, False)
            with self.assertRaises(PermissionError):
                check_audit_event('subprocess.Popen', ('cmd.exe',), home, False)

    def test_isolation_network_allowlist(self):
        from governor_workbench.hermes_runner import check_audit_event
        home = Path.cwd()
        check_audit_event('socket.connect', (None, ('127.0.0.1', 3000)), home, False)
        for address, probe in [(('127.0.0.1', 3000), True), (('127.0.0.1', 4000), False), (('8.8.8.8', 3000), False)]:
            with self.assertRaises(PermissionError):
                check_audit_event('socket.connect', (None, address), home, probe)

    def test_network_contract_rejects_tools_or_second_call(self):
        from governor_workbench.hermes_runner import validate_request
        agent = SimpleNamespace(tools=[], valid_tool_names=set())
        valid = {'model': 'gpt-5.6-terra', 'tools': [], 'reasoning': {'effort': 'medium'}, 'store': False}
        validate_request(valid, agent, 0, 'gpt-5.6-terra', 'http://127.0.0.1:3000/v1/')
        for body, calls in [(dict(valid, tools=[{'name': 'shell'}]), 0), (valid, 1), (dict(valid, model='other'), 0), (dict(valid, reasoning={'effort': 'high'}), 0)]:
            with self.assertRaises(RuntimeError):
                validate_request(body, agent, calls, 'gpt-5.6-terra', 'http://127.0.0.1:3000/v1/')

    def test_missing_is_unavailable(self):
        result = HermesAdapter('C:/not-present/hermes.cmd').check()
        self.assertFalse(result['available'])
        self.assertFalse(result['no_tools_review_supported'])

    def test_unverified_review_refused(self):
        with self.assertRaises(RuntimeError):
            HermesAdapter('C:/not-present/hermes.cmd').review('hello')

    def test_review_requires_explicit_workspace_and_auth(self):
        with self.assertRaises(RuntimeError):
            HermesAdapter('C:/not-present/hermes.cmd').review('hello', model='gpt-6-astra')

    def test_review_rejects_unknown_model(self):
        with self.assertRaises(ValueError):
            HermesAdapter('C:/not-present/hermes.cmd', workspace='.', codex_auth_path='auth.json').review('hello', model='other')

    def test_launcher_only_resolves_known_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            launcher = home / 'bin' / 'hermes.cmd'
            executable = home / 'hermes-agent' / 'venv' / 'Scripts' / 'hermes.exe'
            launcher.parent.mkdir()
            executable.parent.mkdir(parents=True)
            launcher.write_text('malicious command must not execute')
            executable.touch()
            with patch('subprocess.run', return_value=SimpleNamespace(returncode=0, stdout='Hermes 21.1\nsecret-output')) as run:
                result = HermesAdapter(launcher).check()
            self.assertEqual(run.call_args.args[0], [str(executable), '--version'])
            self.assertEqual(result['version'], '21.1')
            self.assertNotIn('secret-output', str(result))
