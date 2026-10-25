from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from .klienten import ClientBase


class ResonanceAnalysisRequest(BaseModel):
    client_id: Optional[str] = None
    client_data: Optional[ClientBase] = None
    focus: str = Field(..., json_schema_extra={"example": "Harmonische Regulation Lunge"})
    matrix_size: int = Field(default=12, description="Matrix-Groesse: 12 (Standard), 24 (Erweitert), 36 (Server/RTX)")
    iterations: int = Field(default=1000, ge=100)
    use_quantum: bool = True
    use_cuda: bool = True
    focus_weight: str = Field(default="Normal", description="Fokus-Gewichtung: Deaktiviert, Sanft, Normal, Stark")
    calculation_mode: str = Field(default="quantum", description="quantum (stochastisch) oder precision (deterministisch)")
    hrv_sim: bool = Field(default=False, description="HRV-Simulation aktivieren")
    emf_compensate: bool = Field(default=False, description="EMF-Umfeld-Kompensation aktivieren")
    use_planetary: bool = Field(default=False, description="Planetarischen Einfluss in der Signatur beruecksichtigen")
    palette: Optional[str] = Field(default=None, description="Farbpalette: None, 'generate_coherent', oder Dict")
    amplifier: Optional[str] = Field(default=None, description="Aktiver Amplifier (Name oder ID) fuer Analysebindung")
    # v1.5.0 Group/Geo Extensions
    group_members: Optional[List[Dict[str, Any]]] = Field(default=None, description="Gruppenmitglieder fuer Gruppen-Analyse")
    geo_coords: Optional[str] = Field(default=None, description="Geo-Koordinaten: 'lat,lon' oder 'lat,lon,radius'")
    image_path: Optional[str] = Field(default=None, description="Server-Pfad zu einem Bild fuer Bild-Resonanz")
    image_base64: Optional[str] = Field(default=None, description="Bilddaten als Base64-String (data URL oder raw base64)")
    db_path: Optional[str] = Field(default=None, description="Pfad zu einer DB-Textdatei fuer Vorab-Vektorisierung")
    symmetry: str = Field(default="none", description="Symmetrie-Modus: none, horizontal (Spiegel), quadrant (Mandala)")


class EMFCounterFrequency(BaseModel):
    frequency_hz: int
    amplitude: float
    duration_s: int
    description: str
    purpose: str


class EMFTimingRecommendation(BaseModel):
    recommendation: str
    message: str
    confidence: float
    emf_index: float


class EMFCompensationResult(BaseModel):
    active: bool
    emf_index: Optional[float] = None
    entropy_score: Optional[float] = None
    timing_recommendation: Optional[EMFTimingRecommendation] = None
    counter_frequencies: List[EMFCounterFrequency] = []


class ResonanceAnalysisResponse(BaseModel):
    analysis_id: UUID
    timestamp: datetime
    client_name: str
    focus: str
    resonance_score: float
    matrix_12x12: List[List[int]] = Field(description="Matrix-Daten (Abwaertskompatibilitaet)")
    matrix_data: Optional[List[List[int]]] = Field(default=None, description="Matrix-Daten (generisch fuer alle Groessen)")
    matrix_size: Optional[int] = Field(default=12, description="Tatsaechliche Matrix-Groesse (12, 24, 36)")
    matrix_colors: List[List[str]] = Field(description="Hex color codes corresponding to the matrix values")
    resonant_patterns: List[Dict[str, Any]]
    processing_time_ms: float
    hardware_acceleration: str
    emf_compensation: Optional[EMFCompensationResult] = None
    amplifier: Optional[Dict[str, Any]] = Field(default=None, description="Aktiver Amplifier in der Analyse")
    amplifier_recommendations: Optional[List[Dict[str, Any]]] = Field(default=None, description="Top Amplifier-Empfehlungen")
    symmetry: Optional[str] = Field(default=None, description="Angewendete Symmetrie: none, horizontal, quadrant")
    client_frequency_hz: Optional[float] = Field(default=None, description="Abgeleitete Klienten-Basisfrequenz in Hz")
    top_10: Optional[List[Dict[str, Any]]] = Field(default=None, description="Top-Varianten inkl. Matrix-Daten")
    # R-7: kanonische Safety-Posture (additiv, default None → byte-kompatibel).
    # Disclaimer + Marker (medical_claims=0, inference_only, non_medical) — siehe
    # app/services/safety_service.py. Kein Term-Block (Nutzer-Entscheidung 2026-06-27).
    safety: Optional[Dict[str, Any]] = Field(default=None, description="Nicht-Medizin-Safety-Posture (Disclaimer+Marker)")


class ResonanceSequenceResponse(BaseModel):
    count: int
    focuses: List[str]
    results: List[ResonanceAnalysisResponse]
    safety: Optional[Dict[str, Any]] = Field(default=None, description="Nicht-Medizin-Safety-Posture (Disclaimer+Marker)")


class EMFStatusResponse(BaseModel):
    active: bool
    continuous_monitoring: bool
    sdr_available: bool
    composite_emf_index: float
    entropy_score: float
    timing_jitter_ms: float
    low_noise_window: bool
    timing_recommendation: EMFTimingRecommendation
    counter_frequencies: List[EMFCounterFrequency]
    measurements_count: int
    calibration: Optional[Dict[str, Any]] = None
