from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class QuantumState:
    amplitude: float
    energy: float
    phase: float = 0.0


@dataclass
class MorphicFieldConfig:
    quantum_states: List[QuantumState]
    numerical_sequence: List[float]
    geometric_form: str
    intention: str
    use_hardware_modulation: bool = False
    hardware_profile: str = "auto"
    time: Optional[float] = None


@dataclass
class MorphicFieldResult:
    total_wave_function: float
    quantum_component: float
    numerical_factor: float
    geometric_factor: float
    intention_factor: float
    hardware_factor: Optional[float]
    coherence: float
    resonance_frequency: float
    field_strength: float
    timestamp: float
    extras: Dict[str, object] = field(default_factory=dict)
