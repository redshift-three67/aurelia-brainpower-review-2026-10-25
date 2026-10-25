"""Workflow State - zentrales Datenobjekt fuer alle 12 Steps.

Dieses Objekt wird durch alle 12 Workflow-Steps gereicht und sammelt
alle Zwischenergebnisse. Es beruehrt NICHT die Kernengine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class WorkflowState:
    """Zentraler Zustand des 12-Step Workflows."""

    # Step 1: Init
    hardware_report: Dict[str, Any] = field(default_factory=dict)
    h_level: float = 0.0
    entropy_source_name: str = ""

    # Step 2: Eingabe
    name: str = ""
    first_name: str = ""
    birth_date: str = ""
    birth_place: str = ""
    focus: str = ""
    intention: str = "harmonization"
    profile_level: int = 3
    top_n: int = 5
    matrix_size: int = 12
    image_path: str = ""
    planet_type: str = ""

    # Personalprofil
    p_emotion: float = 0.5
    p_physisch: float = 0.5
    p_mental: float = 0.5
    p_astral: float = 0.5

    # Step 3: Klienten-Signatur
    client_rates: Optional[np.ndarray] = None
    client_frequency: float = 0.0
    signature_components: Dict[str, float] = field(default_factory=dict)
    emf_corrected_frequency: float = 0.0

    # Step 4: Fokus-Vektor
    focus_vector: Optional[np.ndarray] = None
    focus_multiplier: float = 1.0

    # Step 5: EMF
    composite_emf_index: float = 0.0
    compensation_vector: Optional[np.ndarray] = None
    counter_frequencies: List[float] = field(default_factory=list)

    # Step 6: Amplifier
    amplifier_recommendations: List[Dict[str, Any]] = field(default_factory=list)

    # Step 7: Palette
    palette: List[str] = field(default_factory=list)
    palette_strategy: str = "unified_coherent"

    # Step 8: Matrix
    matrix_results: List[Dict[str, Any]] = field(default_factory=list)
    candidate_count: int = 0

    # Step 9: Quantum
    quantum_synergies: List[Dict[str, Any]] = field(default_factory=list)

    # Step 10: Post-Processing
    symmetrized: bool = False
    final_matrix: Optional[np.ndarray] = None
    level_info: Dict[str, Any] = field(default_factory=dict)

    # Step 11: Ausgabe
    export_paths: Dict[str, str] = field(default_factory=dict)

    # Step 12: Harmonisierung
    harmonization_active: bool = False
    harmonization_job_id: str = ""

    # Metadaten
    session_id: str = ""
    errors: List[str] = field(default_factory=list)
    step_completed: List[int] = field(default_factory=list)

    def mark_step(self, step: int) -> None:
        if step not in self.step_completed:
            self.step_completed.append(step)

    def add_error(self, step: int, msg: str) -> None:
        self.errors.append(f"Step {step}: {msg}")

    @property
    def is_complete(self) -> bool:
        return len(self.step_completed) >= 12
