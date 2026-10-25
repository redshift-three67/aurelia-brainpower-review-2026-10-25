"""
Klienten-Profil System
Erweiterte Klienten-Details für verbesserte Akkuranz
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from pathlib import Path
import json


@dataclass
class ClientProfile:
    """Erweitertes Klienten-Profil"""
    
    # Basis-Daten (erforderlich)
    name: str
    first_name: str
    birth_date: str  # Format: DDMMYYYY
    birth_place: str
    
    # Erweiterte Daten (optional, verbessern Akkuranz)
    birth_time: Optional[str] = None  # Format: HH:MM
    gender: Optional[str] = None  # "m", "f", "d"
    blood_type: Optional[str] = None  # "A+", "B-", etc.
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    
    # Kontakt
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    # Medizinische Historie
    chronic_conditions: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    previous_diagnoses: List[str] = field(default_factory=list)
    
    # Lebensstil (für bessere Resonanz-Berechnung)
    occupation: Optional[str] = None
    stress_level: Optional[int] = None  # 1-10
    sleep_hours: Optional[float] = None
    exercise_frequency: Optional[str] = None  # "täglich", "wöchentlich", "selten", "nie"
    diet_type: Optional[str] = None  # "omnivor", "vegetarisch", "vegan", etc.
    
    # Umwelt-Faktoren
    living_environment: Optional[str] = None  # "Stadt", "Land", etc.
    water_quality: Optional[str] = None  # "Leitungswasser", "gefiltert", etc.
    emf_exposure: Optional[str] = None  # "hoch", "mittel", "niedrig"
    
    # Notizen
    notes: str = ""
    
    # Metadaten
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_age(self) -> int:
        """Berechnet aktuelles Alter"""
        try:
            birth = datetime.strptime(self.birth_date, "%d%m%Y")
            today = datetime.now()
            age = today.year - birth.year
            if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
                age -= 1
            return age
        except:
            return 0
    
    def get_bmi(self) -> Optional[float]:
        """Berechnet BMI"""
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100.0
            return round(self.weight_kg / (height_m ** 2), 1)
        return None
    
    def get_folder_name(self) -> str:
        """Generiert Ordnernamen"""
        return f"{self.name}_{self.first_name}_{self.birth_date}_{self.birth_place}".replace(" ", "_")
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ClientProfile':
        """Erstellt aus Dictionary"""
        return cls(**data)
    
    def save(self, base_path: Path):
        """Speichert Profil"""
        folder = base_path / self.get_folder_name()
        folder.mkdir(parents=True, exist_ok=True)
        
        profile_file = folder / "client_profile.json"
        self.updated_at = datetime.now().isoformat()
        
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, folder: Path) -> Optional['ClientProfile']:
        """Lädt Profil aus Ordner"""
        profile_file = folder / "client_profile.json"
        if not profile_file.exists():
            return None
        
        with open(profile_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)


def calculate_resonance_modifiers(profile: ClientProfile) -> Dict[str, float]:
    """
    Berechnet Resonanz-Modifikatoren basierend auf Klienten-Details
    
    Diese Modifikatoren verbessern die Akkuranz der Analyse durch:
    - Alter (verschiedene Resonanzen in verschiedenen Lebensphasen)
    - Geschlecht (hormonelle Unterschiede)
    - Blutgruppe (energetische Signatur)
    - BMI (Stoffwechsel-Einfluss)
    - Stress-Level (Cortisol-Einfluss)
    - Schlaf (Regenerations-Kapazität)
    - Umwelt-Faktoren (EMF, Wasser, etc.)
    
    Returns:
        Dictionary mit Modifikatoren für verschiedene Kategorien
    """
    modifiers = {
        'age_factor': 1.0,
        'gender_factor': 1.0,
        'blood_type_factor': 1.0,
        'bmi_factor': 1.0,
        'stress_factor': 1.0,
        'sleep_factor': 1.0,
        'emf_factor': 1.0,
    }
    
    # Alter-Faktor
    age = profile.get_age()
    if age < 18:
        modifiers['age_factor'] = 1.2  # Kinder: höhere Sensitivität
    elif age > 65:
        modifiers['age_factor'] = 1.1  # Senioren: veränderte Resonanz
    
    # Geschlecht-Faktor (hormonelle Unterschiede)
    if profile.gender == 'f':
        modifiers['gender_factor'] = 1.05  # Weiblich: andere hormonelle Signatur
    elif profile.gender == 'm':
        modifiers['gender_factor'] = 0.95
    
    # BMI-Faktor (Stoffwechsel)
    bmi = profile.get_bmi()
    if bmi:
        if bmi < 18.5:
            modifiers['bmi_factor'] = 1.1  # Untergewicht: höhere Sensitivität
        elif bmi > 30:
            modifiers['bmi_factor'] = 0.9  # Übergewicht: gedämpfte Resonanz
    
    # Stress-Faktor
    if profile.stress_level:
        if profile.stress_level >= 8:
            modifiers['stress_factor'] = 1.3  # Hoher Stress: verstärkte Reaktion
        elif profile.stress_level >= 5:
            modifiers['stress_factor'] = 1.1
    
    # Schlaf-Faktor
    if profile.sleep_hours:
        if profile.sleep_hours < 6:
            modifiers['sleep_factor'] = 1.2  # Schlafmangel: höhere Belastung
        elif profile.sleep_hours > 8:
            modifiers['sleep_factor'] = 0.9  # Guter Schlaf: bessere Regeneration
    
    # EMF-Faktor
    if profile.emf_exposure == "hoch":
        modifiers['emf_factor'] = 1.3
    elif profile.emf_exposure == "mittel":
        modifiers['emf_factor'] = 1.1
    
    return modifiers


def get_focus_recommendations(profile: ClientProfile) -> List[str]:
    """
    Gibt Fokus-Empfehlungen basierend auf Profil
    
    Returns:
        Liste empfohlener Fokus-Themen
    """
    recommendations = []
    
    age = profile.get_age()
    
    # Alters-basierte Empfehlungen
    if age < 18:
        recommendations.extend([
            "ADHS", "Wachstum", "Immunsystem", "Allergien"
        ])
    elif 18 <= age < 40:
        recommendations.extend([
            "Stress", "Hormone", "Verdauung", "Energie"
        ])
    elif 40 <= age < 65:
        recommendations.extend([
            "Hormone", "Gelenke", "Herz-Kreislauf", "Stoffwechsel"
        ])
    else:
        recommendations.extend([
            "Gelenke", "Herz-Kreislauf", "Gedächtnis", "Knochen"
        ])
    
    # Geschlechts-basierte Empfehlungen
    if profile.gender == 'f':
        if 40 <= age < 60:
            recommendations.append("Wechseljahre")
        recommendations.extend(["Hormone", "Eisenmangel"])
    
    # BMI-basierte Empfehlungen
    bmi = profile.get_bmi()
    if bmi:
        if bmi > 30:
            recommendations.extend(["Stoffwechsel", "Diabetes", "Herz-Kreislauf"])
        elif bmi < 18.5:
            recommendations.extend(["Nährstoffmängel", "Verdauung"])
    
    # Stress-basierte Empfehlungen
    if profile.stress_level and profile.stress_level >= 7:
        recommendations.extend(["Burnout", "Nebennieren", "Schlaf"])
    
    # Chronische Erkrankungen
    for condition in profile.chronic_conditions:
        if "diabetes" in condition.lower():
            recommendations.append("Blutzucker")
        if "bluthochdruck" in condition.lower():
            recommendations.append("Herz-Kreislauf")
    
    return list(set(recommendations))  # Duplikate entfernen
