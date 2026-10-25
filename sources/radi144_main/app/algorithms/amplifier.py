"""
Amplifier Vector Generator & Client Matching Module
====================================================
Version: 1.5.0

Generiert Resonanz-Vektoren aus physischen Verstaerkern (Heilsteine, Orgonite,
Kristalle, Symbole) und berechnet die optimale Zuordnung zum Klienten-Vektor.

Features:
- Frequenz-basierte Vektor-Generierung (Basis + Harmonische)
- Bild-basierte Signatur (SHA-256 Hash + Farbanalyse)
- Cosinus-Aehnlichkeit fuer Klienten-Matching
- Top-N Empfehlungen mit Begruendung
- Amplifier-modulierte Palette und Audio-Frequenzen
- Umfeld-Sensor via Bild-Vergleich (Server-Phase)
"""

import json
import hashlib
import os
import math
import logging
import colorsys
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

import numpy as np

logger = logging.getLogger("amplifier")


class AmplifierVectorGenerator:
    """
    Erzeugt mathematische Vektoren aus Amplifier-Definitionen
    und matched sie gegen Klienten-Signaturen.
    """
    
    # 5-Elemente Frequenz-Mapping (Hz)
    ELEMENT_FREQUENCIES = {
        "Holz":   (294.0, 0.15),
        "Feuer":  (440.0, 0.20),
        "Erde":   (264.0, 0.18),
        "Metall": (352.0, 0.12),
        "Wasser": (308.0, 0.16),
    }
    
    # Chakra Basis-Frequenzen (Hz) - Index 1-7
    CHAKRA_FREQUENCIES = {
        1: 256.0,   # Wurzel (Muladhara)
        2: 288.0,   # Sakral (Svadhisthana)
        3: 320.0,   # Solarplexus (Manipura)
        4: 341.3,   # Herz (Anahata)
        5: 384.0,   # Kehlkopf (Vishuddha)
        6: 426.7,   # Drittes Auge (Ajna)
        7: 480.0,   # Krone (Sahasrara)
        0: 432.0,   # Alle / Universal
    }
    
    def __init__(self, registry_path: str = None):
        """
        Initialisiert den AmplifierVectorGenerator.
        
        Args:
            registry_path: Pfad zur amplifiers.json. 
                           Default: data/amplifiers.json relativ zum Projekt.
        """
        if registry_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            registry_path = os.path.join(base_dir, "data", "amplifiers.json")
        
        self.registry_path = registry_path
        self.amplifiers: Dict[str, Dict] = {}
        self.amplifier_vectors: Dict[str, np.ndarray] = {}
        self._image_signatures: Dict[str, Dict] = {}
        
        self._load_registry()
    
    def _load_registry(self):
        """Laedt die Amplifier-Registry aus der JSON-Datei."""
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.amplifiers = data.get("amplifiers", {})
            logger.info(f"Amplifier Registry geladen: {len(self.amplifiers)} Verstaerker")
            
            # Pre-compute Vektoren fuer alle registrierten Amplifier
            for amp_id, amp_data in self.amplifiers.items():
                self.amplifier_vectors[amp_id] = self._compute_vector(amp_data)
                
        except FileNotFoundError:
            logger.warning(f"Amplifier Registry nicht gefunden: {self.registry_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Amplifier Registry JSON Fehler: {e}")
    
    def _compute_vector(self, amp_data: Dict) -> np.ndarray:
        """
        Berechnet den Resonanz-Vektor eines Amplifiers.
        
        Der Vektor hat 12 Dimensionen (passend zur 12x12 Matrix):
        [0-3]   Frequenz-Komponenten (Basis + 3 Harmonische, normalisiert)
        [4]     Element-Affinitaet (0-1)
        [5]     Chakra-Resonanz (0-1)
        [6]     Verstaerkungsfaktor (0-1)
        [7]     Solfeggio-Affinitaet (normalisiert)
        [8-9]   Farb-Signatur (Hue, Saturation aus color_hex)
        [10]    Kristallsystem-Index (kategorisch, normalisiert)
        [11]    Bild-Signatur-Hash (normalisierter Hash-Wert)
        """
        vec = np.zeros(12, dtype=np.float64)
        
        # [0-3] Frequenz-Komponenten
        harmonics = amp_data.get("harmonics_hz", [440.0])
        for i, h in enumerate(harmonics[:4]):
            # Normalisiere auf 0-1 Bereich (20 Hz - 2000 Hz Mapping)
            vec[i] = min(1.0, max(0.0, (h - 20.0) / 1980.0))
        
        # [4] Element-Affinitaet
        element = amp_data.get("element", "Erde")
        elem_freq, elem_weight = self.ELEMENT_FREQUENCIES.get(element, (264.0, 0.15))
        vec[4] = elem_weight / 0.20  # Normalisiert auf max Element-Weight
        
        # [5] Chakra-Resonanz
        chakra_idx = amp_data.get("chakra_index", 0)
        chakra_freq = self.CHAKRA_FREQUENCIES.get(chakra_idx, 432.0)
        # Resonanz = Naehere Frequenzen zum Amplifier = hoehere Resonanz
        base_freq = amp_data.get("base_frequency_hz", 440.0)
        freq_distance = abs(base_freq - chakra_freq)
        vec[5] = max(0.0, 1.0 - (freq_distance / 500.0))
        
        # [6] Verstaerkungsfaktor
        vec[6] = amp_data.get("amplification_factor", 0.5)
        
        # [7] Solfeggio-Affinitaet (normalisiert auf 174-963 Bereich)
        solfeggio = amp_data.get("solfeggio_affinity", 528)
        vec[7] = (solfeggio - 174.0) / (963.0 - 174.0)
        
        # [8-9] Farb-Signatur
        color_hex = amp_data.get("color_hex", "#FFFFFF")
        h, s, v = self._hex_to_hsv(color_hex)
        vec[8] = h  # Hue (0-1)
        vec[9] = s  # Saturation (0-1)
        
        # [10] Kristallsystem-Index
        crystal_systems = {
            "trigonal": 0.14, "kubisch": 0.28, "hexagonal": 0.42,
            "orthorhombisch": 0.56, "monoklin": 0.70, "triklin": 0.84,
            "amorph": 0.92, "pyramidal": 1.0, None: 0.5
        }
        vec[10] = crystal_systems.get(amp_data.get("crystal_system"), 0.5)
        
        # [11] Bild-Signatur (Hash des Bildpfads als deterministischer Seed)
        image_path = amp_data.get("image_path", "")
        img_hash = int(hashlib.sha256(image_path.encode("utf-8")).hexdigest()[:8], 16)
        vec[11] = (img_hash % 10000) / 10000.0
        
        # Wenn ein echtes Bild existiert, berechne die Bild-Signatur
        self._try_compute_image_signature(amp_data.get("name", "unknown"), image_path)
        
        return vec
    
    def _hex_to_hsv(self, hex_color: str) -> Tuple[float, float, float]:
        """Konvertiert Hex-Farbe zu HSV (0-1 Bereich)."""
        hex_color = hex_color.lstrip("#")
        try:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return colorsys.rgb_to_hsv(r, g, b)
        except (ValueError, IndexError):
            return (0.0, 0.0, 1.0)
    
    def _try_compute_image_signature(self, name: str, image_path: str):
        """
        Versucht eine Bild-Signatur zu berechnen, wenn das Bild existiert.
        Nutzt SHA-256 und durchschnittliche Farbwerte.
        """
        if not image_path:
            return
        
        # Absoluten Pfad konstruieren
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        abs_path = os.path.join(base_dir, image_path)
        
        if not os.path.exists(abs_path):
            return
        
        try:
            with open(abs_path, "rb") as f:
                img_bytes = f.read()
            
            img_hash = hashlib.sha256(img_bytes).hexdigest()
            
            # Einfache Byte-basierte Farbanalyse (ohne PIL/Pillow Dependency)
            # Nutze die letzten N Bytes als Proxy fuer Farbverteilung
            sample = img_bytes[-4096:] if len(img_bytes) > 4096 else img_bytes
            byte_values = np.frombuffer(sample, dtype=np.uint8).astype(np.float64)
            
            self._image_signatures[name] = {
                "sha256": img_hash,
                "file_size": len(img_bytes),
                "byte_mean": float(np.mean(byte_values)),
                "byte_std": float(np.std(byte_values)),
                "byte_entropy": float(self._calculate_byte_entropy(byte_values)),
                "timestamp": datetime.now().isoformat(),
            }
            
            logger.debug(f"Bild-Signatur berechnet fuer {name}: {img_hash[:16]}...")
            
        except Exception as e:
            logger.debug(f"Bild-Signatur Fehler fuer {name}: {e}")
    
    def _calculate_byte_entropy(self, data: np.ndarray) -> float:
        """Berechnet Shannon-Entropie eines Byte-Arrays."""
        if len(data) == 0:
            return 0.0
        counts = np.bincount(data.astype(int), minlength=256)
        probs = counts / len(data)
        probs = probs[probs > 0]
        return float(-np.sum(probs * np.log2(probs)) / 8.0)
    
    # =========================================================================
    # CLIENT MATCHING
    # =========================================================================
    
    def match_client(
        self,
        client_signature: Dict,
        focus_list: Optional[List[str]] = None,
        bio_info: Optional[Dict] = None,
        top_n: int = 3
    ) -> List[Dict]:
        """
        Berechnet die besten Amplifier fuer einen gegebenen Klienten.
        
        Args:
            client_signature: Klienten-Signatur (aus ClientSignatureGenerator)
            focus_list: Liste der Fokus-Themen
            bio_info: Bio-energetische Information (Meridian, Chakra, etc.)
            top_n: Anzahl der Top-Empfehlungen
            
        Returns:
            Liste von Dicts mit: amplifier_id, name, score, reasons, vector
        """
        if not self.amplifiers:
            return []
        
        # 1. Klienten-Vektor in 12D Amplifier-Space projizieren
        client_vec = self._project_client_to_amplifier_space(
            client_signature, focus_list, bio_info
        )
        
        # 2. Cosinus-Aehnlichkeit mit allen Amplifiern
        scores = []
        for amp_id, amp_vec in self.amplifier_vectors.items():
            similarity = self._cosine_similarity(client_vec, amp_vec)
            
            # Bonus fuer Element-Synergie
            element_bonus = self._element_synergy_bonus(
                client_signature, self.amplifiers[amp_id]
            )
            
            # Bonus fuer Fokus-Property-Match
            property_bonus = self._property_match_bonus(
                focus_list, self.amplifiers[amp_id]
            )
            
            # Gewichteter Gesamt-Score
            total_score = (
                0.55 * similarity +
                0.20 * element_bonus +
                0.25 * property_bonus
            )
            
            # Gruende sammeln
            reasons = self._generate_match_reasons(
                self.amplifiers[amp_id], similarity, element_bonus, property_bonus
            )
            
            scores.append({
                "amplifier_id": amp_id,
                "name": self.amplifiers[amp_id]["name"],
                "category": self.amplifiers[amp_id]["category"],
                "score": round(total_score, 4),
                "cosine_similarity": round(similarity, 4),
                "element_synergy": round(element_bonus, 4),
                "property_match": round(property_bonus, 4),
                "reasons": reasons,
                "base_frequency_hz": self.amplifiers[amp_id]["base_frequency_hz"],
                "color_hex": self.amplifiers[amp_id]["color_hex"],
                "amplification_factor": self.amplifiers[amp_id]["amplification_factor"],
                "chakra": self.amplifiers[amp_id].get("chakra", ""),
                "element": self.amplifiers[amp_id].get("element", ""),
                "harmonics_hz": self.amplifiers[amp_id].get("harmonics_hz", []),
            })
        
        # 3. Nach Score sortieren und Top-N zurueckgeben
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_n]
    
    def _project_client_to_amplifier_space(
        self,
        client_sig: Dict,
        focus_list: Optional[List[str]] = None,
        bio_info: Optional[Dict] = None
    ) -> np.ndarray:
        """
        Projiziert die Klienten-Signatur in den 12D Amplifier-Raum.
        """
        vec = np.zeros(12, dtype=np.float64)
        
        client_freq = client_sig.get("frequency", 440.0)
        components = client_sig.get("components", {})
        
        # [0-3] Frequenz-Komponenten des Klienten
        vec[0] = min(1.0, max(0.0, (client_freq - 20.0) / 1980.0))
        vec[1] = min(1.0, max(0.0, (client_freq * 1.5 - 20.0) / 1980.0))  # Quinte
        vec[2] = min(1.0, max(0.0, (client_freq * 2.0 - 20.0) / 1980.0))  # Oktave
        vec[3] = min(1.0, max(0.0, (client_freq / 2.0 - 20.0) / 1980.0))  # Sub-Oktave
        
        # [4] Element-Affinitaet (aus Signatur-Komponenten)
        name_comp = components.get("name_frequency", 0)
        if name_comp > 0:
            vec[4] = min(1.0, (name_comp % 100) / 100.0)
        
        # [5] Chakra-Resonanz (aus bio_info wenn vorhanden)
        if bio_info and bio_info.get("data"):
            bio_freq = bio_info["data"].get("frequency_hz", 432.0)
            vec[5] = min(1.0, max(0.0, (bio_freq - 20.0) / 1980.0))
        else:
            vec[5] = 0.5
        
        # [6] Gesamt-Signatur-Staerke
        vec[6] = min(1.0, client_freq / 1000.0)
        
        # [7] Solfeggio-Naehe
        solfeggio_freqs = [174, 285, 396, 417, 528, 639, 741, 852, 963]
        closest_solf = min(solfeggio_freqs, key=lambda s: abs(s - client_freq))
        vec[7] = (closest_solf - 174.0) / (963.0 - 174.0)
        
        # [8-9] Fokus-basierte Hue/Saturation
        if focus_list:
            focus_combined = " ".join(focus_list).lower()
            h = int(hashlib.md5(focus_combined.encode("utf-8")).hexdigest()[:6], 16)
            vec[8] = (h % 360) / 360.0
            vec[9] = 0.5 + (len(focus_list) * 0.1)  # Mehr Fokus = mehr Saettigung
        else:
            vec[8] = 0.5
            vec[9] = 0.5
        
        # [10] Zeitbasierter Index (Tageszeit-Korrelation)
        hour = datetime.now().hour
        vec[10] = hour / 24.0
        
        # [11] EMF-Korrektur-Komponente (wenn vorhanden)
        emf_corr = components.get("emf_correction", 0)
        vec[11] = min(1.0, abs(emf_corr) / 100.0) if emf_corr else 0.5
        
        return vec
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Berechnet Cosinus-Aehnlichkeit zwischen zwei Vektoren."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def _element_synergy_bonus(self, client_sig: Dict, amp_data: Dict) -> float:
        """
        Berechnet Element-Synergie basierend auf dem 5-Elemente-Zyklus.
        Naehrungs-Zyklus: Holz→Feuer→Erde→Metall→Wasser→Holz
        """
        # Bestimme Klienten-Element aus Frequenz
        client_freq = client_sig.get("frequency", 440.0)
        elements_sorted = sorted(
            self.ELEMENT_FREQUENCIES.items(),
            key=lambda x: abs(x[1][0] - client_freq)
        )
        client_element = elements_sorted[0][0]
        amp_element = amp_data.get("element", "Erde")
        
        # Naehrungs-Zyklus (foerdernd)
        nurturing = {
            "Holz": "Feuer", "Feuer": "Erde", "Erde": "Metall",
            "Metall": "Wasser", "Wasser": "Holz"
        }
        
        if client_element == amp_element:
            return 0.8  # Gleiches Element = stark
        elif nurturing.get(client_element) == amp_element:
            return 1.0  # Naehrungs-Richtung = optimal
        elif nurturing.get(amp_element) == client_element:
            return 0.7  # Umgekehrte Naehrung = gut
        else:
            return 0.4  # Neutral
    
    def _property_match_bonus(
        self, focus_list: Optional[List[str]], amp_data: Dict
    ) -> float:
        """Berechnet Match zwischen Fokus-Themen und Amplifier-Properties."""
        if not focus_list:
            return 0.5
        
        amp_properties = amp_data.get("properties", [])
        amp_description = amp_data.get("description", "").lower()
        amp_name = amp_data.get("name", "").lower()
        
        # Keyword-Mapping: Fokus-Begriffe → Amplifier-Properties
        keyword_map = {
            "heilung": ["heilung", "reinigung", "liebe", "harmonie"],
            "schutz": ["schutz", "abschirmung", "emf_schutz", "erdung"],
            "liebe": ["liebe", "harmonie", "emotionale_balance"],
            "klarheit": ["klarheit", "intuition", "reinigung"],
            "energie": ["energie", "verstaerkung", "manifestation"],
            "erdung": ["erdung", "schutz", "emf_absorption"],
            "intuition": ["intuition", "klarheit", "licht"],
            "kommunikation": ["kommunikation", "ausdruck", "wahrheit"],
            "transformation": ["transformation", "wandel", "reinigung"],
            "balance": ["harmonie", "balance", "universell"],
            "ruhe": ["harmonie", "reinigung", "erdung"],
            "kraft": ["energie", "verstaerkung", "manifestation"],
            "emf": ["emf_schutz", "emf_absorption", "emf_transmutation", "abschirmung"],
        }
        
        total_match = 0.0
        match_count = 0
        
        for focus in focus_list:
            focus_lower = focus.strip().lower()
            
            # Direkter Property-Match
            for prop in amp_properties:
                if focus_lower in prop or prop in focus_lower:
                    total_match += 1.0
                    match_count += 1
            
            # Keyword-Map Match
            for keyword, targets in keyword_map.items():
                if keyword in focus_lower:
                    for target in targets:
                        if target in amp_properties:
                            total_match += 0.7
                            match_count += 1
            
            # Beschreibungs-Match
            if focus_lower in amp_description:
                total_match += 0.5
                match_count += 1
        
        if match_count == 0:
            return 0.3
        
        return min(1.0, total_match / max(1, len(focus_list) * 2))
    
    def _generate_match_reasons(
        self, amp_data: Dict, similarity: float, element_bonus: float, property_bonus: float
    ) -> List[str]:
        """Generiert menschenlesbare Begruendungen fuer die Empfehlung."""
        reasons = []
        
        if similarity > 0.8:
            reasons.append(f"Sehr hohe Frequenz-Resonanz ({similarity*100:.0f}%)")
        elif similarity > 0.6:
            reasons.append(f"Gute Frequenz-Resonanz ({similarity*100:.0f}%)")
        
        if element_bonus >= 1.0:
            reasons.append(f"Optimale Element-Synergie ({amp_data.get('element', '')})")
        elif element_bonus >= 0.8:
            reasons.append(f"Starke Element-Affinitaet ({amp_data.get('element', '')})")
        
        if property_bonus > 0.7:
            reasons.append("Fokus-Themen stark abgedeckt")
        
        chakra = amp_data.get("chakra", "")
        if chakra:
            reasons.append(f"Chakra-Zuordnung: {chakra}")
        
        amp_factor = amp_data.get("amplification_factor", 0.5)
        if amp_factor >= 0.9:
            reasons.append("Maximale Verstaerkungskraft")
        elif amp_factor >= 0.7:
            reasons.append("Hohe Verstaerkungskraft")
        
        if "emf_schutz" in amp_data.get("properties", []) or "emf_absorption" in amp_data.get("properties", []):
            reasons.append("EMF-Schutz Eigenschaften")
        
        return reasons
    
    # =========================================================================
    # AMPLIFIER MODULATION (fuer Harmonisierung)
    # =========================================================================
    
    def get_amplifier_by_id(self, amp_id: str) -> Optional[Dict]:
        """Gibt einen Amplifier anhand seiner ID zurueck."""
        return self.amplifiers.get(amp_id)
    
    def get_amplifier_by_name(self, name: str) -> Optional[Tuple[str, Dict]]:
        """Sucht einen Amplifier anhand seines Namens (case-insensitive)."""
        name_lower = name.strip().lower()
        for amp_id, amp_data in self.amplifiers.items():
            if amp_data["name"].lower() == name_lower or amp_id == name_lower:
                return amp_id, amp_data
        return None
    
    def get_audio_frequencies(self, amp_id: str) -> List[Dict]:
        """
        Gibt die Audio-Frequenzen eines Amplifiers zurueck,
        formatiert fuer die Integration in den Harmonizer.
        
        Returns:
            Liste von Dicts mit frequency_hz, amplitude, label
        """
        amp = self.amplifiers.get(amp_id)
        if not amp:
            return []
        
        result = []
        harmonics = amp.get("harmonics_hz", [])
        base_amp = amp.get("amplification_factor", 0.5)
        
        for i, freq in enumerate(harmonics):
            # Amplitude nimmt mit jeder Harmonischen ab
            amplitude = base_amp * (0.8 ** i)
            result.append({
                "frequency_hz": freq,
                "amplitude": round(amplitude, 4),
                "label": f"{amp['name']} H{i}" if i > 0 else f"{amp['name']} Basis",
            })
        
        return result
    
    def modulate_palette(
        self, base_palette: Dict[int, str], amp_id: str, strength: float = 0.15
    ) -> Dict[int, str]:
        """
        Moduliert eine bestehende Farbpalette mit der Farb-Signatur eines Amplifiers.
        
        Args:
            base_palette: Bestehende Palette {digit: "#RRGGBB"}
            amp_id: Amplifier ID
            strength: Modulationsstaerke (0.0 - 1.0)
            
        Returns:
            Modulierte Palette
        """
        amp = self.amplifiers.get(amp_id)
        if not amp or not base_palette:
            return base_palette
        
        amp_hex = amp.get("color_hex", "#FFFFFF")
        amp_h, amp_s, amp_v = self._hex_to_hsv(amp_hex)
        
        modulated = {}
        for digit, hex_color in base_palette.items():
            h, s, v = self._hex_to_hsv(hex_color)
            
            # Subtile Hue-Verschiebung Richtung Amplifier-Farbe
            new_h = h + (amp_h - h) * strength
            new_h = new_h % 1.0
            
            # Saettigungs-Anpassung
            new_s = s + (amp_s - s) * strength * 0.5
            new_s = max(0.0, min(1.0, new_s))
            
            # Helligkeit leicht anpassen
            new_v = v + (amp_v - v) * strength * 0.3
            new_v = max(0.0, min(1.0, new_v))
            
            r, g, b = colorsys.hsv_to_rgb(new_h, new_s, new_v)
            modulated[digit] = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        
        return modulated
    
    # =========================================================================
    # ENVIRONMENT SENSOR (Server-Phase: Bild-Vergleich)
    # =========================================================================
    
    def compare_environment_image(
        self, amp_id: str, current_image_path: str
    ) -> Optional[Dict]:
        """
        Vergleicht ein aktuelles Bild des Amplifiers mit der Referenz-Signatur.
        Aenderungen in Helligkeit/Farbtemperatur dienen als Umfeld-Proxy.
        
        Args:
            amp_id: Amplifier ID
            current_image_path: Pfad zum aktuellen Bild
            
        Returns:
            Dict mit delta_brightness, delta_entropy, environment_change_score
        """
        amp = self.amplifiers.get(amp_id)
        if not amp:
            return None
        
        ref_sig = self._image_signatures.get(amp["name"])
        if not ref_sig:
            return None
        
        if not os.path.exists(current_image_path):
            return None
        
        try:
            with open(current_image_path, "rb") as f:
                current_bytes = f.read()
            
            sample = current_bytes[-4096:] if len(current_bytes) > 4096 else current_bytes
            current_values = np.frombuffer(sample, dtype=np.uint8).astype(np.float64)
            
            current_mean = float(np.mean(current_values))
            current_std = float(np.std(current_values))
            current_entropy = self._calculate_byte_entropy(current_values)
            
            delta_brightness = abs(current_mean - ref_sig["byte_mean"]) / 255.0
            delta_variation = abs(current_std - ref_sig["byte_std"]) / 128.0
            delta_entropy = abs(current_entropy - ref_sig["byte_entropy"])
            
            # Composite Change Score (0 = keine Aenderung, 1 = starke Aenderung)
            change_score = min(1.0, (
                0.4 * delta_brightness +
                0.3 * delta_variation +
                0.3 * delta_entropy
            ) * 3.0)
            
            return {
                "amplifier": amp["name"],
                "delta_brightness": round(delta_brightness, 4),
                "delta_variation": round(delta_variation, 4),
                "delta_entropy": round(delta_entropy, 4),
                "environment_change_score": round(change_score, 4),
                "interpretation": self._interpret_change(change_score),
                "timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Umfeld-Vergleich Fehler: {e}")
            return None
    
    def _interpret_change(self, score: float) -> str:
        """Interpretiert den Umfeld-Aenderungs-Score."""
        if score < 0.1:
            return "Umfeld stabil - keine signifikante Aenderung"
        elif score < 0.3:
            return "Leichte Umfeld-Variation (Lichtaenderung)"
        elif score < 0.6:
            return "Moderate Umfeld-Aenderung (Lichtquelle/Tageszeit)"
        else:
            return "Starke Umfeld-Aenderung (Standortwechsel oder neue Lichtquelle)"
    
    # =========================================================================
    # REGISTRY MANAGEMENT
    # =========================================================================
    
    def list_amplifiers(self) -> List[Dict]:
        """Gibt eine kompakte Liste aller registrierten Amplifier zurueck."""
        result = []
        for amp_id, amp_data in self.amplifiers.items():
            result.append({
                "id": amp_id,
                "name": amp_data["name"],
                "category": amp_data["category"],
                "element": amp_data.get("element", ""),
                "chakra": amp_data.get("chakra", ""),
                "base_frequency_hz": amp_data["base_frequency_hz"],
                "amplification_factor": amp_data.get("amplification_factor", 0.5),
                "color_hex": amp_data.get("color_hex", "#FFFFFF"),
                "has_image": os.path.exists(
                    os.path.join(
                        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        amp_data.get("image_path", "")
                    )
                ) if amp_data.get("image_path") else False,
            })
        return result
    
    def add_amplifier(self, amp_id: str, amp_data: Dict) -> bool:
        """
        Fuegt einen neuen Amplifier zur Registry hinzu und speichert.
        
        Args:
            amp_id: Eindeutige ID (z.B. "mein_rosenquarz")
            amp_data: Vollstaendige Amplifier-Definition
            
        Returns:
            True bei Erfolg
        """
        required_keys = ["name", "category", "base_frequency_hz"]
        for key in required_keys:
            if key not in amp_data:
                logger.error(f"Amplifier fehlt Pflichtfeld: {key}")
                return False
        
        # Defaults setzen
        amp_data.setdefault("harmonics_hz", [amp_data["base_frequency_hz"]])
        amp_data.setdefault("element", "Erde")
        amp_data.setdefault("chakra", "Alle")
        amp_data.setdefault("chakra_index", 0)
        amp_data.setdefault("amplification_factor", 0.5)
        amp_data.setdefault("color_hex", "#FFFFFF")
        amp_data.setdefault("properties", [])
        amp_data.setdefault("solfeggio_affinity", 528)
        amp_data.setdefault("image_path", "")
        
        self.amplifiers[amp_id] = amp_data
        self.amplifier_vectors[amp_id] = self._compute_vector(amp_data)
        
        return self._save_registry()
    
    def _save_registry(self) -> bool:
        """Speichert die aktuelle Registry zurueck in die JSON-Datei."""
        try:
            data = {
                "_meta": {
                    "version": "1.5.0",
                    "description": "Amplifier Registry - Resonanz-Verstaerker fuer die Harmonisierung",
                    "categories": ["heilstein", "orgonit", "kristall", "metall", "symbol"],
                    "last_modified": datetime.now().isoformat(),
                },
                "amplifiers": self.amplifiers,
            }
            
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Amplifier Registry gespeichert: {len(self.amplifiers)} Eintraege")
            return True
            
        except Exception as e:
            logger.error(f"Amplifier Registry Speichern fehlgeschlagen: {e}")
            return False
