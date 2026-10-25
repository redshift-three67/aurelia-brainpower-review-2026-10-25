"""
Quantum-Synergy Module
Quantum-Enhanced Synergy Detection für optimale Item-Kombinationen

Version: 1.0.0
Author: Morphic Engine Team
"""

from .hybrid_engine import QuantumSynergyEngine
from .database_manager import get_item_database, ItemDatabase
from .synergy_core import SynergyCalculator

__version__ = "1.0.0"
__all__ = [
    "QuantumSynergyEngine",
    "get_item_database",
    "ItemDatabase",
    "SynergyCalculator",
]
