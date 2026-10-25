import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
LAUNCHER = TOOLS / 'radiworks_scheduled_launcher.pyw'


def load_launcher():
    source = LAUNCHER.read_text(encoding='utf-8')
    module_name = 'radiworks_scheduled_launcher_under_test'
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(LAUNCHER)
    exec(compile(source, str(LAUNCHER), 'exec'), module.__dict__)
    return module


class LauncherAvailabilityTests(unittest.TestCase):
    def test_scheduled_launcher_source_exists(self):
        self.assertTrue(LAUNCHER.is_file(), 'scheduled launcher must be present')


class ScheduledLauncherTests(unittest.TestCase):
    def setUp(self):
        if not LAUNCHER.is_file():
            self.skipTest('launcher implementation is not present yet')
        self.launcher = load_launcher()

    def test_only_allowlisted_host_ports_are_mapped_to_the_fixed_host_script(self):
        for port in ('8103', '8104', '8105', '8106', '8107', '8108', '8109'):
            with self.subTest(port=port):
                command = self.launcher.build_command([port], system_root=r'C:\Windows', tools_dir=TOOLS)
                self.assertEqual(command[0], r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe')
                self.assertIn(str(TOOLS / 'radiworks_scheduled_host.ps1'), command)
                self.assertEqual(command[-2:], ['-Port', port])

    def test_watchdog_mode_uses_only_the_fixed_watchdog_script(self):
        command = self.launcher.build_command(['--watchdog'], system_root=r'C:\Windows', tools_dir=TOOLS)
        self.assertIn(str(TOOLS / 'radiworks_scheduled_watchdog.ps1'), command)
        self.assertNotIn('-Port', command)

    def test_arbitrary_scripts_extra_arguments_and_unapproved_ports_are_rejected(self):
        for arguments in (
            [], ['8102'], ['8110'], ['08103'], ['--watchdog', 'anything'],
            ['-File', 'other.ps1'], ['8103', '-File', 'other.ps1'],
        ):
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    self.launcher.build_command(arguments, system_root=r'C:\Windows', tools_dir=TOOLS)

    def test_launch_suppresses_windows_and_standard_streams_and_returns_child_exit_code(self):
        process = Mock()
        process.wait.return_value = 17
        popen = Mock(return_value=process)

        result = self.launcher.run(
            ['--watchdog'], system_root=r'C:\Windows', tools_dir=TOOLS, popen=popen
        )

        self.assertEqual(result, 17)
        command = popen.call_args.args[0]
        self.assertEqual(command[0], r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe')
        self.assertEqual(popen.call_args.kwargs['creationflags'], self.launcher.CREATE_NO_WINDOW)
        self.assertIs(popen.call_args.kwargs['stdin'], subprocess.DEVNULL)
        self.assertIs(popen.call_args.kwargs['stdout'], subprocess.DEVNULL)
        self.assertIs(popen.call_args.kwargs['stderr'], subprocess.DEVNULL)
        process.wait.assert_called_once_with()

    def test_invalid_mode_and_process_start_failure_return_nonzero_without_script_selection(self):
        popen = Mock(side_effect=OSError('process start failed'))
        invalid = self.launcher.run(['--watchdog', 'extra'], system_root=r'C:\Windows', tools_dir=TOOLS,
                                    popen=popen)
        failed = self.launcher.run(['8103'], system_root=r'C:\Windows', tools_dir=TOOLS, popen=popen)

        self.assertEqual(invalid, 2)
        self.assertEqual(failed, 1)
        self.assertEqual(popen.call_count, 1)


if __name__ == '__main__':
    unittest.main()
