from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Callable, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class JsonStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self, default_factory: Callable[[], T]) -> T:
        if not self.path.exists():
            return default_factory()
        raw = self.path.read_text(encoding="utf-8")
        if not raw.strip():
            return default_factory()
        return default_factory().__class__.model_validate(json.loads(raw))

    def save(self, model: T) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_path = tempfile.mkstemp(prefix=self.path.stem + "_", suffix=".tmp", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(model.model_dump(mode="json"), handle, indent=2, ensure_ascii=False)
            os.replace(temp_path, self.path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
