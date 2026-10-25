import logging
import json
from logging.handlers import RotatingFileHandler

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "module": record.name,
            "msg": record.getMessage(),
            "extra": getattr(record, "extra", {})
        })

def get_logger(name: str = "radialgo") -> logging.Logger:
    # Ensure the logs directory exists before creating the handler
    from pathlib import Path
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler("logs/radialgo.log", maxBytes=5_000_000, backupCount=5)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger

log = get_logger()
