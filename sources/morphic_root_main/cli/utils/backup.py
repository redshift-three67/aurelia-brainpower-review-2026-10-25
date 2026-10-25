import datetime
import functools
import inspect
import shutil
from pathlib import Path

from .logging import log


def _create_backup(file_path: Path) -> None:
    if not file_path.is_file():
        log.warning(f"Backup requested for non-existent file: {file_path}")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_name(f"{file_path.name}.bak_{timestamp}")
    try:
        shutil.copy2(str(file_path), str(backup_path))
        log.info(f"Backup created: {backup_path}")
    except Exception:
        log.exception(f"Failed to create backup for {file_path}")


def log_command(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            source = inspect.getsourcefile(func)
            src_path = Path(source).resolve() if source else None
        except Exception:
            src_path = None

        if src_path:
            _create_backup(src_path)

        log.info(
            f"START command: {func.__name__}",
            extra={"command_args": args, "command_kwargs": kwargs},
        )
        try:
            result = func(*args, **kwargs)
            log.info(f"END command: {func.__name__} - SUCCESS")
            return result
        except Exception:
            log.exception(f"END command: {func.__name__} - FAILURE")
            raise

    return wrapper
