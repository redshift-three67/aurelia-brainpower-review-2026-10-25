import os
import pathlib
import importlib
import sys
from pathlib import Path

# Ensure the project root is in sys.path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cli.utils.backup import log_command

def test_log_command_creates_backup(tmp_path: Path):
    # Create a temporary dummy source file
    src_file = tmp_path / "dummy.py"
    src_file.write_text("print('original')")

    # Dynamically create a function that points to the dummy file
    # We'll monkey‑patch inspect.getsourcefile to return our dummy path
    import inspect
    original_getsourcefile = inspect.getsourcefile
    inspect.getsourcefile = lambda f: str(src_file)

    @log_command
    def dummy_func():
        # Function body does nothing; we only care about the decorator side‑effects
        return True

    # Call the function – this should trigger a backup
    dummy_func()

    # Restore the original inspect function
    inspect.getsourcefile = original_getsourcefile

    # Verify that a backup file exists next to the dummy file
    backups = list(tmp_path.glob("dummy.py.bak_*"))
    assert len(backups) == 1, f"Expected one backup file, found: {backups}"
    # Ensure the backup content matches the original
    assert backups[0].read_text() == "print('original')"
