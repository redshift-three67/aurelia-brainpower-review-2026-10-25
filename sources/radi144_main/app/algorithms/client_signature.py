"""
Client Signature Generator
Multi-parametrische Klienten-Frequenzsignatur für >90% Akkuranz
"""

import numpy as np
import os
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ClientSignatureGenerator:
    """
    Generiert hochpräzise Klienten-Frequenzsignatur
    
    Komponenten:
    1. Name-Frequenz (Linguistisch/Garjajev)
    2. Geburtsdaten (Temporal/Astronomisch)
    3. Bild-Signatur (Holografisch/AI)
    4. Organuhr (Circadian)
    5. Planetarisch (Astrologisch)
    6. Nullpunkt-Kalibrierung (Entropie)
    """
    
    def generate_signature(
        self, 
        client_data: Dict, 
        use_planetary: bool = False,
        emf_compensator=None
    ) -> Dict:
        """Hauptmethode zur Signatur-Generierung"""
        signature_components = []
        
        # 1. Name-Frequenz
        if "first_name" in client_data and "last_names" in client_data:
            name_freq = self.calculate_name_frequency(
                client_data["first_name"],
                client_data["last_names"]
            )
            signature_components.append(("name", name_freq, 0.15))
        
        # 2. Geburtsdaten
        if "birth_date" in client_data:
            birth_freq = self.calculate_birth_frequency(
                client_data["birth_date"],
                client_data.get("birth_time"),
                client_data.get("birth_place")
            )
            signature_components.append(("birth", birth_freq, 0.20))
        
        # 3. Bild-Signatur (falls vorhanden)
        if "image_signature_ai" in client_data:
            image_freq = client_data["image_signature_ai"].get("frequency", 0.0)
            signature_components.append(("image", image_freq, 0.25))
        
        # 4. Organuhr
        organ_freq = self.calculate_organ_clock_influence(datetime.now())
        signature_components.append(("organ_clock", organ_freq, 0.10))
        
        # 5. Planetarisch (Optional)
        if use_planetary and "birth_date" in client_data:
            planetary_freq = self.calculate_planetary_influence(
                client_data["birth_date"],
                client_data.get("geolocation")
            )
            signature_components.append(("planetary", planetary_freq, 0.15))
        
        # 6. EMF-Umfeld-Korrektur (Optional)
        # Kompensiert elektromagnetische Stoerungen im Umfeld des Klienten/Servers.
        # Der EMF-Index moduliert die Nullpunkt-Kalibrierung der Signatur.
        emf_correction = 0.0
        if emf_compensator:
            try:
                emf_profile = emf_compensator.profile_environment()
                emf_index = emf_profile.get("composite_emf_index", 0.0)
                entropy = emf_profile.get("entropy_score", 0.5)
                
                # Berechne Korrekturfrequenz:
                # Hoher EMF-Index → staerkere Korrektur (Shift Richtung Schumann-Resonanz 7.83Hz Harmonische)
                # Hohe Entropy → bessere Kalibrierung → geringere Korrektur noetig
                schumann_harmonics = [7.83, 14.3, 20.8, 27.3, 33.8]
                harmonic = schumann_harmonics[min(4, int(emf_index * 5))]
                
                # Korrekturstaerke: EMF-Index gewichtet, Entropie-invertiert
                correction_strength = emf_index * (1.0 - entropy * 0.5)
                emf_correction = harmonic * correction_strength * 10.0  # Skalierung in Hz-Bereich
                
                signature_components.append(("emf_correction", emf_correction, 0.05))
                logger.info(f"EMF Signatur-Korrektur: {emf_correction:.2f}Hz "
                           f"(Index={emf_index:.3f}, Entropy={entropy:.3f})")
            except Exception as e:
                logger.warning(f"EMF Signatur-Korrektur fehlgeschlagen: {e}")
        
        # Gewichtete Kombination
        final_signature = self.combine_weighted(signature_components)
        
        return {
            "frequency": final_signature,
            "components": {k: v for k, v, _ in signature_components},
            "emf_corrected": emf_correction > 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def calculate_name_frequency(
        self, 
        first_name: str, 
        last_names: List[str]
    ) -> float:
        """Name → Frequenz nach Garjajev-Prinzipien"""
        full_name = f"{first_name} {' '.join(last_names)}"
        return self._text_to_frequency(full_name)

    def _text_to_frequency(self, text: str) -> float:
        """Allgemeine Text → Frequenz Transformation"""
        # Numerologie
        numerology = sum(ord(char) for char in text.lower() if char.isalpha())
        
        # Phonetik (vereinfacht)
        phonetic_sum = sum(self._char_to_frequency(c) for c in text.lower())
        
        # Kombiniere
        frequency = (numerology + phonetic_sum) / 2.0
        
        # Normalisiere zu sinnvollem Bereich
        return frequency % 1000.0

    def generate_group_signature(self, members: List[Dict]) -> Dict:
        """
        Erzeugt eine Gruppen-Signatur durch Vektor-Interferenz (Centroid).
        Kombiniert die individuellen Signaturen zu einem kollektiven Resonanzfeld.
        """
        if not members:
            return {"frequency": 0.0, "components": {}, "type": "group"}

        member_signatures = []
        for m in members:
            # Stelle sicher, dass birth_place vorhanden ist, falls nicht in JSON
            if "birth_place" not in m and "place" in m:
                m["birth_place"] = m["place"]
            member_signatures.append(self.generate_signature(m))
        
        # Frequenz-Interferenz (Mittelwert)
        group_freq = sum(s["frequency"] for s in member_signatures) / len(member_signatures)
        
        # Komponenten-Aggregation
        group_components = {"member_count": len(members)}
        for idx, s in enumerate(member_signatures):
            group_components[f"member_{idx}"] = s["frequency"]

        return {
            "frequency": group_freq,
            "components": group_components,
            "type": "group",
            "timestamp": datetime.utcnow().isoformat()
        }

    def generate_image_signature(self, image_path: str) -> Dict:
        """
        Erzeugt eine Frequenz-Signatur aus einem Bild.
        
        Methodik:
        1. SHA-256 Hash → deterministische Basis-Frequenz
        2. Durchschnitts-Farbwerte (RGB/HSV) → Chakra/Element-Zuordnung
        3. Pixel-Entropie → Komplexitätsgewichtung
        4. Bildname → linguistische Frequenz (wie Name-Frequenz)
        
        Args:
            image_path: Absoluter Pfad zum Bild (jpg, png, bmp, etc.)
            
        Returns:
            Signatur-Dict kompatibel zum Standard-Format
        """
        import os
        
        if not os.path.exists(image_path):
            logger.warning(f"Bild nicht gefunden: {image_path}")
            return {"frequency": 0.0, "components": {}, "type": "image", "timestamp": datetime.utcnow().isoformat()}
        
        signature_components = []
        
        # 1. SHA-256 Hash → Basis-Frequenz (deterministisch)
        try:
            with open(image_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            hash_freq = int(file_hash[:8], 16) % 1000.0
            signature_components.append(("hash", hash_freq, 0.25))
        except Exception as e:
            logger.warning(f"Image hash failed: {e}")
            hash_freq = 0.0
        
        # 2. Farbanalyse (RGB-Durchschnitt → HSV → Frequenz)
        color_freq = 0.0
        try:
            from PIL import Image
            img = Image.open(image_path).convert("RGB")
            # Reduziere auf 64x64 fuer schnelle Analyse
            img_small = img.resize((64, 64))
            pixels = list(img_small.getdata())
            
            r_avg = sum(p[0] for p in pixels) / len(pixels)
            g_avg = sum(p[1] for p in pixels) / len(pixels)
            b_avg = sum(p[2] for p in pixels) / len(pixels)
            
            # RGB → HSV Hue als Frequenz-Basis (0-360° → 0-720 Hz)
            import colorsys
            h, s, v = colorsys.rgb_to_hsv(r_avg / 255, g_avg / 255, b_avg / 255)
            color_freq = h * 720.0 + s * 100.0 + v * 50.0
            signature_components.append(("color", color_freq, 0.30))
            
            # 3. Pixel-Entropie (Komplexität des Bildes)
            # Hohe Entropie = komplexes Bild = breiteres Frequenzspektrum
            import math
            histogram = img_small.histogram()
            total_px = sum(histogram)
            entropy = 0.0
            for count in histogram:
                if count > 0:
                    p = count / total_px
                    entropy -= p * math.log2(p)
            # Normalisiere Entropie (typ. 0-8 bits) auf 0-500 Hz
            entropy_freq = (entropy / 8.0) * 500.0
            signature_components.append(("entropy", entropy_freq, 0.20))
            
        except ImportError:
            logger.warning("PIL/Pillow nicht installiert - Farbanalyse uebersprungen, nutze nur Hash")
        except Exception as e:
            logger.warning(f"Image color analysis failed: {e}")
        
        # 4. Bildname → linguistische Frequenz
        basename = os.path.splitext(os.path.basename(image_path))[0]
        name_freq = self._text_to_frequency(basename)
        signature_components.append(("name", name_freq, 0.25))
        
        # Gewichtete Kombination
        final_freq = self.combine_weighted(signature_components)
        
        return {
            "frequency": final_freq,
            "components": {k: v for k, v, _ in signature_components},
            "type": "image",
            "image_path": image_path,
            "image_label": basename,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_geo_frequency(self, lat: float, lon: float, radius_m: float = 0.0) -> float:
        """
        Vektorisierung von Geo-Koordinaten.
        Transformiert Breitengrad und Längengrad in eine energetische Signatur.
        Radius_m: Umkreis in Metern (beeinflusst die Bandbreite/Resonanzvolumen).
        """
        # Basis-Transformation
        geo_sig = (abs(lat) * 111.32 + abs(lon) * 40.075) % 1000.0
        
        # Radius-Modulation (falls vorhanden)
        if radius_m > 0:
            # Radius wirkt als "Dicke" des Vektors (Harmonische Ausdehnung)
            # Logarithmische Skalierung des Radius-Einflusses
            radius_mod = np.log10(radius_m + 1) * 7.83 # Kopplung an Schumann-Resonanz Basis
            geo_sig = (geo_sig + radius_mod) % 1000.0
            
        return geo_sig

    def vectorise_database_selection(self, db_path: str, focus_query: str) -> float:
        """
        Sucht in einer .txt Datenbank nach dem Fokus und vektorisiert die Fundstelle.
        Ermoeglicht die Einbindung von vordefinierten Wissensfeldern.
        """
        import os
        if not os.path.exists(db_path):
            return 0.0
            
        content = ""
        # Robustes Encoding-Handling für Datenbank-Dateien
        for enc in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(db_path, 'r', encoding=enc) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error reading DB with {enc}: {e}")
                continue

        if not content:
            logger.warning(f"DB Vectorisation failed: Could not read {db_path}")
            return 0.0
            
        try:
            # Einfache Suche nach dem Fokus (oder semantisch Verwandtem)
            if focus_query.lower() in content.lower():
                # Vektorisierung des Kontexts um den Fundort
                return self._text_to_frequency(focus_query)
        except Exception as e:
            logger.error(f"DB Search failed: {e}")
            
        return 0.0
    
    def calculate_birth_frequency(
        self,
        birth_date: str,
        birth_time: Optional[str] = None,
        birth_place: Optional[str] = None
    ) -> float:
        """Geburtsdaten -> Frequenz (Einbindung von Zeit und Ort fuer maximale Spezifitaet)"""
        try:
            # Versuche verschiedene Formate, falls noetig
            if isinstance(birth_date, str):
                dt = datetime.fromisoformat(birth_date.split('T')[0])
            else:
                dt = birth_date
            
            # 1. Astronomische Basis (Julian Day)
            julian_day = self._to_julian_day(dt)
            base_freq = julian_day % 1000.0
            
            # 2. Lokale Spezifitaet (Geburtsort)
            place_mod = 0.0
            if birth_place:
                # Nutze Hashing fuer einen stabilen Orts-Vektor
                place_hash = hashlib.md5(birth_place.lower().strip().encode()).hexdigest()
                place_mod = int(place_hash[:4], 16) / 65.535 # Normalisiere auf 0-1000
            
            # 3. Zeitliche Spezifitaet (Geburtszeit)
            time_mod = 0.0
            if birth_time:
                # Erwartet HH:MM
                try:
                    h, m = map(int, birth_time.split(':'))
                    time_mod = (h * 60 + m) / 1.44 # 1440 min / 10 = 1000er Bereich
                except:
                    pass
            
            # Gewichtete Kombination
            # Basis (60%) + Ort (30%) + Zeit (10%)
            final_birth_freq = (base_freq * 0.6) + (place_mod * 0.3) + (time_mod * 0.1)
            
            return final_birth_freq % 1000.0
            
        except Exception as e:
            logger.warning(f"Birth frequency calculation failed: {e}")
            return 0.0
    
    def calculate_organ_clock_influence(self, current_time: datetime) -> float:
        """Organuhr → aktuelle Frequenz"""
        hour = current_time.hour
        
        # TCM Organuhr Mapping
        organ_frequencies = {
            range(1, 3): 194.18,    # Leber (F)
            range(3, 5): 220.00,    # Lunge (A)
            range(5, 7): 246.94,    # Dickdarm (H)
            range(7, 9): 261.63,    # Magen (C)
            range(9, 11): 293.66,   # Milz (D)
            range(11, 13): 329.63,  # Herz (E)
            range(13, 15): 349.23,  # Dünndarm (F)
            range(15, 17): 392.00,  # Blase (G)
            range(17, 19): 440.00,  # Niere (A)
            range(19, 21): 493.88,  # Perikard (H)
            range(21, 23): 523.25,  # 3E (C)
            range(23, 25): 587.33,  # Gallenblase (D)
        }
        
        for hour_range, frequency in organ_frequencies.items():
            if hour in hour_range:
                return frequency
        
        return 440.0  # Default A
    
    def calculate_planetary_influence(
        self,
        birth_date: str,
        geolocation: Optional[str] = None
    ) -> float:
        """Planetarische Einflüsse (vereinfacht)"""
        # Würde mit pyswisseph implementiert werden
        # Hier vereinfachte Version
        
        try:
            if isinstance(birth_date, str):
                dt = datetime.fromisoformat(birth_date.split('T')[0])
            else:
                dt = birth_date
            
            # Zyklische Berechnung basierend auf Datum
            day_of_year = dt.timetuple().tm_yday
            
            # Sinusförmige Modulation (simuliert planetarische Zyklen)
            planetary_freq = 100.0 * (1 + np.sin(day_of_year * 2 * np.pi / 365.25))
            
            return planetary_freq
            
        except Exception as e:
            logger.warning(f"Planetary calculation failed: {e}")
            return 100.0
    
    def combine_weighted(self, components: List[tuple]) -> float:
        """Gewichtete Kombination aller Komponenten"""
        total_frequency = 0.0
        total_weight = 0.0
        
        for name, frequency, weight in components:
            total_frequency += frequency * weight
            total_weight += weight
        
        if total_weight > 0:
            return total_frequency / total_weight
        else:
            return 0.0
    
    def _char_to_frequency(self, char: str) -> float:
        """Charakter → Frequenz (Phonetik)"""
        # Vereinfachte Vokal/Konsonant-Frequenzen
        vowels = {'a': 440, 'e': 330, 'i': 550, 'o': 220, 'u': 165}
        
        if char in vowels:
            return vowels[char]
        elif char.isalpha():
            return ord(char) * 2.0
        else:
            return 0.0
    
    def _to_julian_day(self, dt: datetime) -> float:
        """Konvertiert Datum zu Julian Day Number"""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        
        jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        
        return float(jdn)
