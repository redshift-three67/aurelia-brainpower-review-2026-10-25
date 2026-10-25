"""Package and Linux launch-contract tests; never starts systemd on Windows."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from contract_lab.linux_probe import build_package, verify_package, start_command, stop_command, ProbeError
from contract_lab.linux_worker import validate_limits, result


RUN = 'a' * 32


class LinuxProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'package'
        self.anchor = build_package(self.root)

    def test_roundtrip_and_runtime_binding(self):
        manifest = verify_package(self.root, self.anchor)
        self.assertEqual(manifest['runtime'], {'python': '3.12.3', 'systemd_major': 255})
        self.assertEqual(manifest['files'].keys(), {'linux_worker.py'})

    def test_existing_package_is_not_overwritten(self):
        with self.assertRaises(ProbeError):
            build_package(self.root)
        verify_package(self.root, self.anchor)

    def test_changed_worker_rejected(self):
        with (self.root / 'linux_worker.py').open('ab') as stream:
            stream.write(b'\n# drift')
        with self.assertRaises(ProbeError):
            verify_package(self.root, self.anchor)

    def test_changed_manifest_rejected_even_with_updated_file_hash(self):
        path = self.root / 'manifest.json'
        data = json.loads(path.read_text())
        data['properties']['MemoryMax'] = '8G'
        path.write_text(json.dumps(data))
        with self.assertRaises(ProbeError):
            verify_package(self.root, self.anchor)
        # A new hash alone cannot authorize a policy outside the fixed contract.
        with self.assertRaises(ProbeError):
            verify_package(self.root, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_extra_or_missing_file_rejected(self):
        extra = self.root / 'extra'
        extra.write_text('x')
        with self.assertRaises(ProbeError):
            verify_package(self.root, self.anchor)
        extra.unlink()
        (self.root / 'linux_worker.py').unlink()
        with self.assertRaises(ProbeError):
            verify_package(self.root, self.anchor)

    def test_fixed_start_arguments(self):
        command = start_command(RUN, 'normal')
        self.assertEqual(command[0], '/usr/bin/systemd-run')
        self.assertIn('--unit=aurelia-t3-' + RUN + '.service', command)
        self.assertIn('--property=KillMode=control-group', command)
        self.assertIn('--property=MemoryMax=128M', command)
        self.assertIn('--property=PrivateNetwork=yes', command)
        self.assertEqual(command[-3:], [RUN, 'normal', '--guarded'])
        self.assertNotIn('--collect', command)
        self.assertIn('--property=BindReadOnlyPaths=/var/tmp/aurelia-t3/' + RUN
                      + '/linux_worker.py:/run/aurelia-t3-worker.py', command)
        self.assertIn('/run/aurelia-t3-worker.py', command)

    def test_bad_run_and_mode_rejected(self):
        for run in ('../x', '', True, 'A' * 32):
            with self.assertRaises(ProbeError):
                start_command(run, 'normal')
        for mode in ('shell', '--help', None):
            with self.assertRaises(ProbeError):
                start_command(RUN, mode)

    def test_stop_is_bound_to_matching_receipt(self):
        receipt = {'run_id': RUN, 'invocation_id': 'b' * 32,
                   'boot_id': 'c' * 32, 'control_group': '/system.slice/aurelia-t3-' + RUN + '.service'}
        self.assertEqual(stop_command(receipt, dict(receipt)),
                         ['/usr/bin/systemctl', 'stop', 'aurelia-t3-' + RUN + '.service'])
        with self.assertRaises(ProbeError):
            stop_command(receipt, dict(receipt, invocation_id='d' * 32))
        with self.assertRaises(ProbeError):
            stop_command({}, {})

    def test_guard_accepts_only_bounded_limits(self):
        valid = {'memory.max': '134217728', 'memory.swap.max': '0',
                 'pids.max': '16', 'cpu.max': '25000 100000'}
        validate_limits(valid)
        for key, value in (('memory.max', 'max'), ('memory.max', '268435456'),
                           ('memory.swap.max', '1'), ('pids.max', 'max'),
                           ('cpu.max', 'max 100000'), ('cpu.max', '50000 100000')):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_limits(dict(valid, **{key: value}))

    def test_guard_rejects_missing_and_zero_limits(self):
        with self.assertRaises(ValueError):
            validate_limits({})
        with self.assertRaises(ValueError):
            validate_limits({'memory.max': '0', 'memory.swap.max': '0',
                             'pids.max': '16', 'cpu.max': '0 100000'})

    def test_normal_result_is_synthetic(self):
        self.assertEqual(result(), {'data_class': 'synthetic', 'result': 14})

    def test_worker_rejects_uncontained_execution(self):
        worker = self.root / 'linux_worker.py'
        completed = subprocess.run([sys.executable, '-I', '-B', str(worker), RUN,
                                    'normal', '--guarded'], capture_output=True, timeout=5)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout.strip(), b'{"status":"probe_failed"}')
        self.assertEqual(completed.stderr, b'')

    def test_manifest_rejects_duplicate_keys(self):
        path = self.root / 'manifest.json'
        raw = path.read_bytes().replace(b'"schema": 1', b'"schema": 2, "schema": 1')
        path.write_bytes(raw)
        with self.assertRaises(ProbeError):
            verify_package(self.root, hashlib.sha256(raw).hexdigest())

    def test_manifest_rejects_numeric_type_substitution(self):
        path = self.root / 'manifest.json'
        raw = path.read_bytes().replace(b'"systemd_major": 255', b'"systemd_major": 255.0')
        path.write_bytes(raw)
        with self.assertRaises(ProbeError):
            verify_package(self.root, hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    unittest.main()
