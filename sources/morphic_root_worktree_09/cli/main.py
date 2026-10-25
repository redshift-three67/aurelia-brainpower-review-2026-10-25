"""Supported compatibility adapter for legacy ``cli.main`` helper imports."""

from __future__ import annotations

from apps.cli.commands import helpers as _helpers


COMPATIBILITY_STATUS = "supported"
ADAPTER_TARGET = "apps.cli.commands.helpers"

for _helper_name in _helpers.__all__:
    globals()[_helper_name] = getattr(_helpers, _helper_name)

__all__ = [
    "ADAPTER_TARGET",
    "COMPATIBILITY_STATUS",
    *_helpers.__all__,
]
