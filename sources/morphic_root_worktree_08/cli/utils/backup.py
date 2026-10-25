import functools
import inspect
import shutil
import datetime
from pathlib import Path
from .logging import log

def _create_backup(file_path: Path) -> None:
    """Create a timestamped shadow copy of *file_path*.
    The backup is placed next to the original file with the suffix
    `.bak_YYYYMMDD_HHMMSS`.
    """
    if not file_path.is_file():
        log.warning(f"Backup requested for non‑existent file: {file_path}")
        return
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_name(f"{file_path.name}.bak_{timestamp}")
    try:
        shutil.copy2(str(file_path), str(backup_path))
        log.info(f"Backup created: {backup_path}")
    except Exception as exc:
        log.error(f"Failed to create backup for {file_path}: {exc}")

def log_command(func):
    """Decorator that creates a backup of the source file before executing *func*.
    It also logs start/end of the command via the global JSON logger.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Determine the source file of the wrapped function
        try:
            src_path = Path(inspect.getsourcefile(func)).resolve()
        except Exception:
            src_path = None
        if src_path:
            _create_backup(src_path)
        log.info(f"START command: {func.__name__}", extra={"command_args": args, "command_kwargs": kwargs})
        try:
            result = func(*args, **kwargs)
            log.info(f"END command: {func.__name__} – SUCCESS")
            return result
        except Exception as exc:
            log.exception(f"END command: {func.__name__} – FAILURE")
            raise
    return wrapper
