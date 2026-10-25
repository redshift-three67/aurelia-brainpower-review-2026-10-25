"""Console-free, allowlisted entry point for RadiWorks scheduled tasks."""
import ntpath
import os
import subprocess
import sys


CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
_HOST_PORTS = frozenset(str(port) for port in range(8103, 8110))
_POWERSHELL_RELATIVE = ("System32", "WindowsPowerShell", "v1.0", "powershell.exe")


def build_command(argv, *, system_root=None, tools_dir=None):
    """Return the fixed PowerShell command for one allowlisted task mode."""
    arguments = list(argv)
    if arguments == ["--watchdog"]:
        script_name = "radiworks_scheduled_watchdog.ps1"
        script_arguments = []
    elif len(arguments) == 1 and arguments[0] in _HOST_PORTS:
        script_name = "radiworks_scheduled_host.ps1"
        script_arguments = ["-Port", arguments[0]]
    else:
        raise ValueError("Unsupported scheduled launcher mode")

    if system_root is None:
        system_root = os.environ.get("SystemRoot")
    if not system_root:
        raise ValueError("SystemRoot is unavailable")
    if tools_dir is None:
        tools_dir = os.path.dirname(os.path.abspath(__file__))

    powershell = ntpath.join(system_root, *_POWERSHELL_RELATIVE)
    script = os.path.join(os.fspath(tools_dir), script_name)
    return [
        powershell,
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-WindowStyle",
        "Hidden",
        "-File",
        script,
        *script_arguments,
    ]


def run(argv, *, system_root=None, tools_dir=None, popen=None):
    try:
        command = build_command(argv, system_root=system_root, tools_dir=tools_dir)
    except (TypeError, ValueError):
        return 2

    if popen is None:
        popen = subprocess.Popen
    try:
        child = popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW,
        )
        return child.wait()
    except (OSError, subprocess.SubprocessError, ValueError):
        return 1


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
