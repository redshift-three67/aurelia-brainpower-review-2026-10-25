"""
Datenbank-Module für Morphic Engine V1.
"""

from .descriptions_db import (
    DescriptionsDB,
    get_descriptions_db,
)
from .health import (
    assert_core_databases_ready,
    collect_core_database_health,
    collect_runtime_health,
    table_count,
)

__all__ = [
    "DescriptionsDB",
    "assert_core_databases_ready",
    "collect_core_database_health",
    "collect_runtime_health",
    "get_descriptions_db",
    "table_count",
]
