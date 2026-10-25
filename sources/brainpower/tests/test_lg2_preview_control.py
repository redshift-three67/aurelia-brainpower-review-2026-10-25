import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/server'))
from lg2_preview_control import PreviewController, TARGETS, PreviewError


SSH = b'PermitRootLogin prohibit-password\nPasswordAuthentication no\nKbdInteractiveAuthentication no\nAllowAgentForwarding no\nX11Forwarding no\nAllowTcpForwarding local\nGatewayPorts no\nPermitTunnel no\n'
UFW = b'*filter\n:ufw-before-input - [0:0]\n:ufw-before-output - [0:0]\n:ufw-before-forward - [0:0]\n-A ufw-before-output -o lo -j ACCEPT\nCOMMIT\n'


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.commands = []
        self.timer = True
        self.fail_reload = False
        self.c = PreviewController('/root/aurelia-preview-20261016T120000Z', root=self.root, runner=self.runner)
        self.c._check_identity = lambda: None
        self.c._protected = lambda: {'protected': 'unchanged'}
        self.c._copy_tools = lambda: {}
        keys = [b'restrict ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n', b'restrict ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB\n']
        for name, raw in zip(TARGETS, [SSH, UFW, *keys]):
            p = self.root / name.lstrip('/'); p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw); p.chmod(0o600)
        self.originals = {n: (self.root / n.lstrip('/')).read_bytes() for n in TARGETS}

    def tearDown(self):
        self.temp.cleanup()

    def runner(self, args, **kwargs):
        self.commands.append(args)
        rc = 0; out = ''
        if args == ['hostname']: out = 'vm2565\n'
        if args == ['lsb_release','-rs']: out = '24.04\n'
        if args[:3] == ['systemctl', 'is-active', '--quiet']:
            rc = 0 if self.timer else 4
        if args[:2] == ['systemctl', 'stop']:
            self.timer = False
        if args[:2] == ['/usr/sbin/sshd', '-T']:
            out = 'allowtcpforwarding local\nallowstreamlocalforwarding no\npermitlisten none\npermitopen 127.0.0.1:18112 127.0.0.1:18113\npasswordauthentication no\nkbdinteractiveauthentication no\n'
        if self.fail_reload and args == ['systemctl', 'reload', 'ssh.service']:
            rc = 1
        return subprocess.CompletedProcess(args, rc, out, '')

    def proof(self):
        from lg2_ipv4_control import _utc_now
        j=self.c._load()
        return {'workdir':self.c.workdir,'applied_at':j['applied_at'],'checked_at':_utc_now(),
                'after_sha256':{n:i['sha256'] for n,i in j['after'].items()},
                'checks':dict.fromkeys(['admin_login','ops_login','website_login','own_http','cross_denied','reverse_denied','socket_denied','ufw_reload'], True)}

    def test_real_identity_check_uses_compatible_runner_signature(self):
        del self.c._check_identity
        self.c.prepare()
        self.assertIn(['hostname'],self.commands)
        self.assertIn(['lsb_release','-rs'],self.commands)

    def test_apply_requires_live_timer_and_does_not_write(self):
        self.c.prepare(); self.timer = False
        with self.assertRaises(PreviewError): self.c.apply()
        for n in TARGETS: self.assertEqual((self.root / n.lstrip('/')).read_bytes(), self.originals[n])

    def test_apply_rollback_restores_exact_bytes_and_modes(self):
        self.c.prepare(); self.c.apply(); result = self.c.rollback()
        self.assertEqual(result['phase'], 'rolled_back')
        for n in TARGETS:
            p = self.root / n.lstrip('/'); self.assertEqual(p.read_bytes(), self.originals[n]); self.assertEqual(p.stat().st_mode & 0o777, 0o600)

    def test_foreign_edit_refuses_apply_before_any_write(self):
        self.c.prepare(); p = self.root / TARGETS[-1].lstrip('/'); p.write_bytes(b'foreign')
        with self.assertRaises(PreviewError): self.c.apply()
        self.assertEqual((self.root / TARGETS[0].lstrip('/')).read_bytes(), self.originals[TARGETS[0]])

    def test_foreign_edit_refuses_rollback_without_overwrite(self):
        self.c.prepare(); self.c.apply(); p = self.root / TARGETS[0].lstrip('/'); p.write_bytes(b'foreign')
        with self.assertRaises(PreviewError): self.c.rollback()
        self.assertEqual(p.read_bytes(), b'foreign')

    def test_foreign_project_key_does_not_block_root_config_restoration(self):
        self.c.prepare(); self.c.apply(); p=self.root / TARGETS[-1].lstrip('/');p.write_bytes(b'foreign')
        with self.assertRaises(PreviewError):self.c.rollback()
        for n in TARGETS[:2]:self.assertEqual((self.root / n.lstrip('/')).read_bytes(),self.originals[n])
        self.assertEqual(p.read_bytes(),b'foreign')
        self.assertEqual(self.c._load()['phase'],'rollback_conflict')
        with self.assertRaises(PreviewError):self.c.rollback()
        self.assertEqual(p.read_bytes(),b'foreign')

    def test_rollback_after_partial_write(self):
        self.c.prepare(); j = self.c._load(); j['phase'] = 'applying'; self.c._save(j)
        n = TARGETS[0]; self.c._replace(n, base64.b64decode(j['after'][n]['data']), j['after'][n])
        self.c.rollback()
        for n in TARGETS: self.assertEqual((self.root / n.lstrip('/')).read_bytes(), self.originals[n])

    def test_failed_reload_retains_recoverable_journal(self):
        self.c.prepare(); self.fail_reload = True
        with self.assertRaises(PreviewError): self.c.apply()
        self.assertEqual(self.c._load()['phase'], 'applying')
        self.fail_reload = False; self.c.rollback()

    def test_commit_requires_explicit_complete_proof(self):
        self.c.prepare(); self.c.apply()
        with self.assertRaises(PreviewError): self.c.commit({})
        self.assertTrue(self.timer)

    def test_commit_and_gc_timer_idempotence(self):
        self.c.prepare(); self.c.apply()
        proof = self.proof()
        self.assertEqual(self.c.commit(proof)['phase'], 'committed')
        self.assertFalse(self.timer)
        self.assertEqual(self.c.commit(proof)['phase'], 'committed')
        self.assertEqual(self.c.rollback()['phase'], 'committed')

    def test_proof_for_other_transaction_is_refused(self):
        self.c.prepare();self.c.apply();proof=self.proof();proof['workdir']+='-foreign'
        with self.assertRaises(PreviewError):self.c.commit(proof)
        self.assertTrue(self.timer)

    def test_symlink_parent_is_refused(self):
        self.c.prepare(); p = self.root / TARGETS[-1].lstrip('/'); parent = p.parent
        parent.rename(parent.with_name('saved')); parent.symlink_to(parent.with_name('saved'), target_is_directory=True)
        with self.assertRaises(PreviewError): self.c.apply()

    def test_protected_drift_refuses_apply(self):
        self.c.prepare(); self.c._protected = lambda: {'protected': 'changed'}
        with self.assertRaises(PreviewError): self.c.apply()

    def test_repeated_prepare_cannot_reset_transaction(self):
        self.c.prepare(); self.c.apply()
        with self.assertRaises(PreviewError): self.c.prepare()


if __name__ == '__main__': unittest.main()
