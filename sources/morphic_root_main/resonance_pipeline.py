"""Legacy resonance pipeline adapter.

The maintained implementation lives in core.profiles and services.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

from core.profiles.profile import ClientProfile
from services.analysis_service import AnalysisService
from services.harmonization_service import HarmonizationService


class ResonancePipeline:
    def __init__(self, rate_db: Dict[str, Iterable[float]], h_level: float = 0.0):
        self.rate_db = rate_db
        self.h_level = h_level

    def analyze(self, profile: ClientProfile) -> Dict[str, Any]:
        return AnalysisService(self.rate_db, h_level=self.h_level).analyze(profile)

    def harmonize(
        self,
        profile: ClientProfile,
        analysis: Dict[str, Any],
        targets: Any = None,
    ) -> Dict[str, Any]:
        return HarmonizationService(self.rate_db, h_level=self.h_level).harmonize(
            profile,
            analysis,
            targets=targets,
        )
