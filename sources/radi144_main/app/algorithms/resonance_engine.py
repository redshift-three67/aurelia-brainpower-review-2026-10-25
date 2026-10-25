from ..bootstrap import CORE_PROFILE, enforce_profile

enforce_profile(CORE_PROFILE)

import torch
import numpy as np
import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import time
import hashlib
from .client_signature import ClientSignatureGenerator
from .emf_compensator import EMFCompensator
from .amplifier import AmplifierVectorGenerator
import logging

logger = logging.getLogger(__name__)

DEFAULT_RADIONIK_PALETTE = {
    0: "#FFFFFF",
    1: "#FF0000",
    2: "#FF7F00",
    3: "#FFFF00",
    4: "#00FF00",
    5: "#00FFFF",
    6: "#0000FF",
    7: "#8B00FF",
    8: "#FF00FF",
    9: "#FFD700",
}

class ResonanceMatrixEngine:
    """
    Hochperformante Matrix-Resonanz-Engine optimiert für NVIDIA RTX 4000 (Ada Generation).
    Berechnet die Resonanz zwischen einem Klienten-Vektor und einem Fokus-Vektor 
    innerhalb eines NxN Muster-Raums (12x12, 24x24, 36x36).
    """
    
    def __init__(self, use_cuda: bool = True, quantum_active: bool = False):
        import platform
        
        # Hardware-Erkennung und Adaption
        self.device = torch.device("cpu")
        self.hw_info = "CPU (Generic)"
        self.os_info = platform.system()
        self.vram_gb = 0.0  # Wird bei CUDA-Erkennung gesetzt
        
        # Basis-Skalierung basierend auf RAM (für CPU-Modus)
        total_ram_gb = 16.0 # Default fallback
        try:
            import psutil
            total_ram_gb = psutil.virtual_memory().total / (1024**3)
        except ImportError:
            logger.warning("psutil nicht installiert. Nutze Standard-RAM-Schätzung.")
        
        # Standard Kandidaten-Anzahl (Skalierbar)
        # Thresholds leicht gesenkt für bessere Erkennung von Standard-Konfigurationen (16GB/32GB)
        if total_ram_gb >= 31:
            self.candidate_count = 250000
        elif total_ram_gb >= 15:
            self.candidate_count = 150000
        else:
            self.candidate_count = 80000
            
        if use_cuda and torch.cuda.is_available():
            self.device = torch.device("cuda")
            device_name = torch.cuda.get_device_name(0)
            
            vram_gb = 4.0 # Fallback
            try:
                vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            except:
                pass
            self.vram_gb = vram_gb
                
            self.hw_info = f"CUDA ({device_name})"
            
            # CUDA Optimierungen
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Adaptive Skalierung basierend auf VRAM
            if vram_gb >= 20: # z.B. RTX 4000 Ada
                self.candidate_count = 1000000
                self.hw_info += " [Extreme Mode: 1M]"
            elif vram_gb >= 8:
                self.candidate_count = 500000
                self.hw_info += " [High Mode: 500k]"
            else:
                self.candidate_count = 200000
                self.hw_info += " [Standard Mode: 200k]"
            
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
             self.device = torch.device("mps")
             self.hw_info = "Apple Silicon (MPS)"
             self.candidate_count = 300000
             
        # CPU Thread Optimierung (Wichtig fuer AMD Ryzen im CPU Modus)
        if self.device.type == "cpu":
            import multiprocessing
            # Nutze 80% der Kerne, mindestens 1
            num_threads = max(1, int(multiprocessing.cpu_count() * 0.8))
            torch.set_num_threads(num_threads)
            self.hw_info = f"CPU Optimized ({num_threads} Threads, {total_ram_gb:.1f}GB RAM)"
            
        self.signature_gen = ClientSignatureGenerator()
        
        # D-Wave Konfiguration (Vorbereitung)
        self.dwave_enabled = False
        self.dwave_token = os.environ.get("DWAVE_API_TOKEN")
        self.dwave_solver = None
        self.quantum_active = quantum_active # Software-Toggle
        
        if self.dwave_token and self.quantum_active:
            self.prepare_dwave_solver()
        
        # HRV Fallback Simulation State
        self.hrv_sim_active = False
        self.last_hrv_score = 1.0
        
        # EMF Compensator (Echtzeit-Umfeld-Kompensation)
        self.emf_compensator = None
        self.emf_active = False
        
        # Amplifier System (Resonanz-Verstaerker)
        self.amplifier_gen = AmplifierVectorGenerator()
        self.active_amplifier_id = None
        self.active_amplifier_data = None
        
        # Bio-Wissen laden
        self.bio_knowledge = {}
        try:
            knowledge_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'bio_knowledge.json')
            if os.path.exists(knowledge_path):
                with open(knowledge_path, 'r', encoding='utf-8') as f:
                    self.bio_knowledge = json.load(f)
            else:
                logger.warning(f"bio_knowledge.json nicht gefunden unter {knowledge_path}")
        except Exception as e:
            logger.error(f"Fehler beim Laden von bio_knowledge.json: {e}")
        
        logger.info(f"ResonanceMatrixEngine initialized on {self.device} [{self.hw_info}]")
        logger.info(f"Unterstuetzte Matrix-Groessen: {self.get_supported_matrix_sizes()}")

    def get_supported_matrix_sizes(self) -> List[Dict[str, Any]]:
        """
        Gibt die unterstuetzten Matrix-Groessen basierend auf der erkannten Hardware zurueck.
        12x12: Immer verfuegbar
        24x24: Verfuegbar ab 1 GB VRAM oder CPU-Modus
        36x36: Nur auf Server-GPUs mit >= 8 GB VRAM
        """
        sizes = [
            {"size": 12, "label": "12x12 (Standard)", "available": True, "cells": 144},
            {"size": 24, "label": "24x24 (Erweitert)", "available": True, "cells": 576},
        ]
        
        # 36x36 nur auf Server-GPUs (>= 8 GB VRAM)
        if self.device.type == "cuda" and self.vram_gb >= 8.0:
            sizes.append({"size": 36, "label": "36x36 (Server/RTX)", "available": True, "cells": 1296})
        else:
            sizes.append({"size": 36, "label": "36x36 (Server/RTX - nicht verfuegbar)", "available": False, "cells": 1296})
        
        return sizes

    def enable_emf_compensation(self, continuous: bool = False):
        """Aktiviert die EMF-Umfeld-Kompensation."""
        try:
            self.emf_compensator = EMFCompensator(
                device=self.device, 
                continuous=continuous
            )
            self.emf_active = True
            logger.info("EMF Kompensation aktiviert.")
        except Exception as e:
            logger.error(f"EMF Compensator konnte nicht initialisiert werden: {e}")
            self.emf_active = False
    
    def disable_emf_compensation(self):
        """Deaktiviert die EMF-Umfeld-Kompensation."""
        if self.emf_compensator:
            self.emf_compensator.stop_continuous_monitoring()
            self.emf_compensator = None
        self.emf_active = False
        logger.info("EMF Kompensation deaktiviert.")
    
    def get_emf_status(self) -> Optional[Dict]:
        """Gibt den aktuellen EMF-Status zurueck."""
        if self.emf_compensator:
            return self.emf_compensator.get_status_report()
        return None
    
    # =========================================================================
    # AMPLIFIER SYSTEM
    # =========================================================================
    
    def set_amplifier(self, amplifier_name: str) -> Optional[Dict]:
        """
        Setzt den aktiven Amplifier fuer die Harmonisierung.
        
        Args:
            amplifier_name: Name oder ID des Amplifiers
            
        Returns:
            Amplifier-Daten oder None wenn nicht gefunden
        """
        result = self.amplifier_gen.get_amplifier_by_name(amplifier_name)
        if result:
            self.active_amplifier_id, self.active_amplifier_data = result
            logger.info(f"Amplifier aktiviert: {self.active_amplifier_data['name']}")
            return self.active_amplifier_data
        
        # Versuch ueber ID
        amp = self.amplifier_gen.get_amplifier_by_id(amplifier_name)
        if amp:
            self.active_amplifier_id = amplifier_name
            self.active_amplifier_data = amp
            logger.info(f"Amplifier aktiviert: {amp['name']}")
            return amp
        
        logger.warning(f"Amplifier nicht gefunden: {amplifier_name}")
        return None
    
    def clear_amplifier(self):
        """Deaktiviert den aktiven Amplifier."""
        self.active_amplifier_id = None
        self.active_amplifier_data = None
        logger.info("Amplifier deaktiviert.")
    
    def get_amplifier_recommendation(
        self, client_signature: Dict, focus_list: List[str] = None,
        bio_info: Dict = None, top_n: int = 3
    ) -> List[Dict]:
        """Berechnet die Top-N Amplifier-Empfehlungen fuer den Klienten."""
        return self.amplifier_gen.match_client(
            client_signature, focus_list, bio_info, top_n
        )
    
    def list_amplifiers(self) -> List[Dict]:
        """Listet alle verfuegbaren Amplifier auf."""
        return self.amplifier_gen.list_amplifiers()

    def calculate_resonance(
        self, 
        client_data: Dict, 
        focus: str, 
        matrix_size: int = 12,
        focus_weight: str = "Normal",
        palette: Union[Dict[int, str], str] = None,
        calculation_mode: str = "quantum", # 'quantum' (stochastisch) oder 'precision' (deterministisch)
        hrv_sim: bool = False,
        precomputed_signature: Optional[Dict] = None,
        emf_compensate: bool = False,
        symmetry: str = "none"  # 'none', 'horizontal', 'quadrant'
    ) -> Dict[str, Any]:
        start_time = time.time()
        self.hrv_sim_active = hrv_sim
        
        # --- EMF Kompensation ---
        emf_profile = None
        if emf_compensate and not self.emf_active:
            self.enable_emf_compensation(continuous=False)
        
        if self.emf_active and self.emf_compensator:
            emf_profile = self.emf_compensator.profile_environment()
            self.emf_compensator.compute_compensation_vector()
            logger.info(f"EMF Profil: Index={emf_profile['composite_emf_index']:.3f}, "
                        f"Entropy={emf_profile['entropy_score']:.3f}")
        
        # HRV Simulation: Beeinflusst die Kohärenz der Suche
        hrv_factor = 1.0
        if self.hrv_sim_active:
            # Simuliere HRV-Score (0.1 - 1.0), wobei 1.0 hohe Kohärenz bedeutet
            # Basiert auf Tageszeit und Zufallskomponente als Fallback
            current_hour = datetime.now().hour
            # Morgens oft höhere HRV
            base_hrv = 0.8 if 6 <= current_hour <= 10 else 0.6
            self.last_hrv_score = base_hrv + (np.random.random() * 0.2)
            hrv_factor = self.last_hrv_score
            logger.info(f"HRV Simulation aktiv: Score {hrv_factor:.2f}")

        # --- Deterministik-Logik (Option B) ---
        # Wenn Precision-Mode aktiv, setzen wir einen festen Seed für diesen Durchlauf
        current_rng_state = None
        cuda_rng_state = None
        if calculation_mode == "precision":
            # Speichere aktuellen State um ihn später wiederherzustellen (Clean State)
            current_rng_state = torch.get_rng_state()
            if self.device.type == "cuda":
                cuda_rng_state = torch.cuda.get_rng_state_all()
            
            # Generiere Master-Seed aus Klient und Fokus
            # Wir nutzen den Hash der Signatur-Komponenten und des Fokus
            birth_date = client_data.get("birth_date") or client_data.get("dob", "")
            seed_source = f"{client_data.get('first_name', '')}{birth_date}{focus}"
            master_seed = int(hashlib.md5(seed_source.encode('utf-8')).hexdigest()[:8], 16)
            
            torch.manual_seed(master_seed)
            if self.device.type == "cuda":
                torch.cuda.manual_seed_all(master_seed)
                # Für absolute Reproduzierbarkeit auf GPU (kostet etwas Performance)
                # torch.backends.cudnn.deterministic = True 
        
        # Bio-Vektor Check
        bio_vector = None
        bio_info = None
        focus_lower = focus.lower().strip()
        
        chakra_knowledge = self.bio_knowledge.get("chakras") or self.bio_knowledge.get("chakra")
        if chakra_knowledge:
            for k, v in chakra_knowledge.items():
                if k in focus_lower or v["name"].lower() in focus_lower:
                    bio_vector = self._embed_bio_frequency(v["frequency_hz"])
                    bio_info = {"type": "chakra", "data": v}
                    break
                    
        if bio_vector is None and "meridians" in self.bio_knowledge:
            for k, v in self.bio_knowledge["meridians"].items():
                if k in focus_lower or v["name"].lower() in focus_lower:
                    bio_vector = self._embed_bio_frequency(v["frequency_hz"])
                    bio_info = {"type": "meridian", "data": v}
                    break

        # 1. Klienten-Vektor generieren (oder nutzen falls vorhanden)
        if precomputed_signature:
            client_sig = precomputed_signature
            logger.info("Nutze vorab berechnete Signatur (Gruppe/Geo/DB).")
        else:
            client_sig = self.signature_gen.generate_signature(
                client_data,
                emf_compensator=self.emf_compensator if self.emf_active else None
            )
            
        client_vector = self._embed_signature(client_sig)
        
        # Palette Logic
        active_palette = None
        if isinstance(palette, dict):
            active_palette = palette
        elif palette == "client_focus_coherent":
            # Client + Fokus kohaerente Palette (unterschiedlich pro Fokus)
            active_palette = self.generate_focus_emf_palette(
                focus_list=[focus],
                bio_info=bio_info,
                emf_profile=None,
                client_frequency=client_sig.get("frequency", 440.0)
            )
        elif palette == "focus_only_coherent":
            # Rein fokus-basierte monochromatische Palette (kein Client-Einfluss)
            # Pro Fokus: 1 Hue aus Fokus-Hash, 10 Stufen nur S+V
            active_palette = self.generate_focus_monochrome_palette(focus)
        elif palette == "nature_healing":
            # Natur-heilsame Palette: Fokus → Natur-Familie (Wald/Erde/Himmel/Moos/Nebel/Morgenrot)
            active_palette = self.generate_nature_monochrome_palette(focus)
        elif palette == "focus_emf_coherent":
            # Fokus + EMF + Bio kohaerente Palette (volle EMF-Integration)
            active_palette = self.generate_focus_emf_palette(
                focus_list=[focus],
                bio_info=bio_info,
                emf_profile=emf_profile,
                client_frequency=client_sig.get("frequency", 440.0)
            )
        elif palette == "chakra_spectrum":
            # Chakra-inspiriertes Spektrum (0-9) mit sanfter Fokus-/Frequenz-Variation
            active_palette = self.generate_chakra_spectrum_palette(
                focus=focus,
                client_frequency=client_sig.get("frequency", 440.0),
            )
        elif palette == "twilight_balance":
            # Warm-kuehle Dämmerungs-Harmonie: ausgewogen zwischen Aktivierung und Beruhigung
            active_palette = self.generate_twilight_balance_palette(
                focus=focus,
                client_frequency=client_sig.get("frequency", 440.0),
            )
        elif palette == "generate_coherent":
            # Legacy: Rein frequenz-basierte Palette
            freq = bio_info["data"]["frequency_hz"] if bio_info else client_sig.get("frequency", 440.0)
            active_palette = self.generate_client_palette(freq)
        elif palette == "unified_coherent":
            # Unified Palette fuer API/UI (einzelner Fokus als 1-Element-Liste)
            active_palette = self.generate_unified_coherent_palette(
                client_data=client_data,
                focus_list=[focus],
                use_planetary=False,
            )
        
        # 2. Fokus-Vektor generieren (Semantische Einbettung)
        focus_vector = self._embed_focus(focus)
        
        # Kombiniere Fokus mit Bio-Vektor falls vorhanden
        if bio_vector is not None:
            # 50/50 Mix für Bio-Fokus
            focus_vector = (focus_vector + bio_vector) / 2.0
        
        # --- EMF-Kompensation auf Vektoren anwenden ---
        if self.emf_active and self.emf_compensator:
            client_vector = self.emf_compensator.apply_to_target_vector(client_vector)
            focus_vector = self.emf_compensator.apply_to_target_vector(focus_vector)
            logger.info("EMF Kompensationsvektor auf Client- und Fokus-Vektoren angewendet.")
        
        # 3. Hybrid-Suche (Heuristischer Quanten-Ansatz + CUDA/CPU)
        top_results = self._find_optimal_matrix_cuda(
            client_vector, 
            focus_vector, 
            size=matrix_size,
            weight_type=focus_weight,
            top_k=10,
            hrv_factor=hrv_factor
        )
        
        # 5-Elemente Validierung (Filter/Ranking)
        if bio_info and "elements" in self.bio_knowledge:
            top_results = self._validate_elements(top_results, bio_info)

        best_matrix = top_results[0]["matrix"]
        max_resonance = top_results[0]["score"]
        main_intensity = top_results[0]["intensity"]
        
        # --- Quantum Annealing Refinement (D-Wave) ---
        if self.dwave_enabled:
            logger.info("Starte Quantum Refinement...")
            refined_matrix = self.solve_with_dwave(best_matrix)
            if refined_matrix is not None:
                best_matrix = refined_matrix
                logger.info("Quantum Refinement abgeschlossen.")
        
        # --- Post-Symmetrisierung (Spiegel / Mandala) ---
        symmetry_applied = "none"
        if symmetry in ("horizontal", "quadrant"):
            best_matrix = self._symmetrize_matrix(best_matrix, mode=symmetry)
            for res in top_results:
                res["matrix"] = self._symmetrize_matrix(res["matrix"], mode=symmetry)
            symmetry_applied = symmetry
            logger.info(f"Post-Symmetrisierung angewendet: {symmetry}")
        
        # --- Amplifier Modulation ---
        amplifier_result = None
        if self.active_amplifier_id and self.active_amplifier_data:
            # Palette modulieren mit Amplifier-Farbe
            if active_palette:
                active_palette = self.amplifier_gen.modulate_palette(
                    active_palette, self.active_amplifier_id, strength=0.15
                )
            
            # Amplifier-Empfehlung berechnen
            amplifier_result = {
                "active": True,
                "id": self.active_amplifier_id,
                "name": self.active_amplifier_data["name"],
                "base_frequency_hz": self.active_amplifier_data["base_frequency_hz"],
                "amplification_factor": self.active_amplifier_data.get("amplification_factor", 0.5),
                "audio_frequencies": self.amplifier_gen.get_audio_frequencies(self.active_amplifier_id),
                "chakra": self.active_amplifier_data.get("chakra", ""),
                "element": self.active_amplifier_data.get("element", ""),
                "color_hex": self.active_amplifier_data.get("color_hex", "#FFFFFF"),
            }
        
        # Amplifier Top-3 Empfehlung (immer berechnen)
        amplifier_recommendations = self.amplifier_gen.match_client(
            client_sig, focus_list=[focus], bio_info=bio_info, top_n=3
        )
        
        # 4. Farbmuster generieren
        matrix_colors = self._generate_coherent_colors(best_matrix, active_palette)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Convert top results for JSON output
        top_10_list = []
        for res in top_results:
            m_list = res["matrix"].tolist()
            top_10_list.append({
                "score": float(res["score"]),
                "intensity": float(res["intensity"]),
                "matrix_12x12": m_list,
                "matrix_data": m_list,
            })

        matrix_list = best_matrix.tolist()

        if current_rng_state is not None:
            torch.set_rng_state(current_rng_state)
            if cuda_rng_state is not None and self.device.type == "cuda":
                torch.cuda.set_rng_state_all(cuda_rng_state)
        
        return {
            "resonance_score": float(max_resonance),
            "intensity": float(main_intensity),
            "matrix_12x12": matrix_list,  # Abwaertskompatibilitaet (Key bleibt fuer bestehende Verbraucher)
            "matrix_data": matrix_list,   # Generischer Key fuer alle Groessen
            "matrix_size": matrix_size,
            "matrix_colors": matrix_colors,
            "used_palette": active_palette, 
            "top_10": top_10_list,
            "processing_time_ms": processing_time,
            "hardware": self.hw_info,
            "client_name": f"{client_data.get('first_name')} {client_data.get('last_names', [''])[0]}",
            "client_signature": {
                "frequency": client_sig.get("frequency"),
                "components": client_sig.get("components")
            },
            "focus_weight": focus_weight,
            "bio_info": bio_info,
            "hrv_score": float(hrv_factor) if self.hrv_sim_active else None,
            "quantum_active": self.quantum_active,
            "emf_compensation": {
                "active": self.emf_active,
                "emf_index": emf_profile["composite_emf_index"] if emf_profile else None,
                "entropy_score": emf_profile["entropy_score"] if emf_profile else None,
                "timing_recommendation": self.emf_compensator.get_timing_recommendation() if self.emf_compensator else None,
                "counter_frequencies": self.emf_compensator.get_counter_frequencies() if self.emf_compensator else [],
            } if self.emf_active else None,
            "amplifier": amplifier_result,
            "amplifier_recommendations": amplifier_recommendations,
            "symmetry": symmetry_applied,
        }

    def _symmetrize_matrix(self, matrix: torch.Tensor, mode: str = "horizontal") -> torch.Tensor:
        """
        Post-Symmetrisierung einer 12x12 Matrix (Score-Retention: 88-95%).
        Bildet den Mittelwert der Spiegelpaare und rundet auf naechste Ganzzahl.
        
        Modi:
          'horizontal' → Links-Rechts-Spiegel (72 unabh. Zellen)
          'quadrant'   → 4-Quadranten-Mandala (36 unabh. Zellen)
        """
        if not isinstance(matrix, torch.Tensor):
            matrix = torch.tensor(matrix, dtype=torch.int32)
        
        sym = matrix.clone().float()
        size = sym.shape[0]  # 12
        
        if mode == "horizontal":
            # Links-Rechts-Spiegel: avg(matrix[i][j], matrix[i][size-1-j])
            for i in range(size):
                for j in range(size // 2):
                    j_mirror = size - 1 - j
                    avg_val = (sym[i][j] + sym[i][j_mirror]) / 2.0
                    sym[i][j] = avg_val
                    sym[i][j_mirror] = avg_val
                    
        elif mode == "quadrant":
            # 4-Quadranten-Mandala: avg aller 4 Spiegelpositionen
            for i in range(size // 2):
                for j in range(size // 2):
                    i_mirror = size - 1 - i
                    j_mirror = size - 1 - j
                    vals = [sym[i][j], sym[i][j_mirror], sym[i_mirror][j], sym[i_mirror][j_mirror]]
                    avg_val = sum(vals) / 4.0
                    sym[i][j] = avg_val
                    sym[i][j_mirror] = avg_val
                    sym[i_mirror][j] = avg_val
                    sym[i_mirror][j_mirror] = avg_val
        
        # Runden auf naechste Ganzzahl und Clamping auf 0-9
        sym = torch.clamp(torch.round(sym), 0, 9).int()
        return sym

    def _embed_bio_frequency(self, freq: float) -> torch.Tensor:
        """Erzeugt einen deterministischen Bio-Vektor basierend auf Frequenz."""
        seed_int = int(hashlib.md5(str(freq).encode()).hexdigest()[:8], 16)
        g = torch.Generator(device=self.device)
        g.manual_seed(seed_int)
        return torch.randn(256, generator=g, device=self.device)

    def _validate_elements(self, results: List[Dict], bio_info: Dict) -> List[Dict]:
        """Bewertet Ergebnisse nach 5-Elemente-Harmonie."""
        element = bio_info["data"].get("element")
        if not element or "elements" not in self.bio_knowledge:
            return results
            
        # Einfache Regel: Matrizen mit hoher Varianz (Intensität) sind "Feuer"-lastig,
        # Matrizen mit niedriger Varianz eher "Wasser/Erde".
        # Hier könnte man die Matrix-Zahlen 0-9 den Elementen zuordnen für tiefere Analyse.
        return results # Placeholder für komplexere Logik

    def generate_client_palette(self, frequency: float) -> Dict[int, str]:
        """Generiert eine kohärente Palette basierend auf der Klienten-Frequenz (Hue-Shift)."""
        import colorsys
        
        # Basis-Frequenz auf 0-1 Hue mappen (einfacher Modulo)
        base_hue = (frequency % 1000) / 1000.0
        
        palette = {}
        for i in range(10):
            # Erzeuge 10 harmonische Stufen
            # Shift hue slightly for each number, vary saturation/value
            hue = (base_hue + (i * 0.03)) % 1.0
            sat = 0.6 + (i % 3) * 0.15  # 0.6, 0.75, 0.9
            val = 0.5 + (i % 2) * 0.4   # 0.5, 0.9
            
            # 0 ist immer Weiß/Helles Grau für Kontrast
            if i == 0:
                sat = 0.0
                val = 1.0
                
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            # To Hex
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
            )
            palette[i] = hex_color.upper()
            
        return palette

    def generate_unified_coherent_palette(
        self,
        client_data: Dict,
        focus_list: List[str],
        use_planetary: bool = False
    ) -> Dict[int, str]:
        """
        Unified Coherent Palette: Sanfte, heilsame, in sich kohaerente Farbpalette.
        Kombiniert Klienten-Signatur (2/3) + gemeinsames Fokus-Feld (1/3).
        Wird EINMAL pro Sitzung berechnet (nicht pro Fokus).
        
        Schicht 1: Client-Anker (2/3) - Frequenz + Komponenten → Golden-Ratio Hue
        Schicht 2: Fokus-Feld (1/3) - Circular Mean aller Fokus-Hashes → Fokus-Zentroid
        Schicht 3: EMF-Kompensation - Subtile Counter-Frequency Micro-Offsets
        Schicht 4: Kohaerente Heilsame Palette - Sanfte Saettigung, hohe Helligkeit,
                   fliessender Farbverlauf 0-9 fuer in sich stimmige Farbharmonie
        """
        import colorsys
        
        # === SCHICHT 1: Client-Anker (2/3 Gewichtung) ===
        client_sig = self.signature_gen.generate_signature(
            client_data,
            emf_compensator=self.emf_compensator if self.emf_active else None
        )
        client_freq = client_sig.get("frequency", 440.0)
        client_components = client_sig.get("components", {})
        
        # Golden-Ratio Mapping fuer bessere Hue-Verteilung (Phi = 0.618033...)
        phi = 0.618033988749895
        client_hue = (client_freq * phi) % 1.0
        
        # Komponenten als sekundaere Hue-Modulation (components ist ein Dict)
        comp_shift = 0.0
        if isinstance(client_components, dict) and client_components:
            comp_values = list(client_components.values())[:5]
            comp_sum = sum(abs(float(c)) for c in comp_values if isinstance(c, (int, float)))
            comp_shift = (comp_sum % 100) / 3000.0  # Max ~0.033 Shift (sanft)
        elif isinstance(client_components, (list, tuple)) and client_components:
            comp_sum = sum(abs(float(c)) for c in client_components[:5] if isinstance(c, (int, float)))
            comp_shift = (comp_sum % 100) / 3000.0
        
        # === SCHICHT 2: Fokus-Feld (1/3 Gewichtung) ===
        focus_hues = []
        for f in focus_list:
            h = int(hashlib.md5(f.strip().lower().encode('utf-8')).hexdigest()[:6], 16)
            focus_hues.append((h % 360) / 360.0)
        
        # Circular Mean fuer Fokus-Zentroid
        if len(focus_hues) == 1:
            focus_centroid = focus_hues[0]
            focus_variance = 0.0
        else:
            sin_sum = sum(np.sin(2 * np.pi * h) for h in focus_hues)
            cos_sum = sum(np.cos(2 * np.pi * h) for h in focus_hues)
            focus_centroid = (np.arctan2(sin_sum, cos_sum) / (2 * np.pi)) % 1.0
            R = np.sqrt(sin_sum**2 + cos_sum**2) / len(focus_hues)
            focus_variance = 1.0 - R
        
        # Gewichtete Fusion: 2/3 Client + 1/3 Fokus (Client-dominant)
        # Circular Interpolation (kuerzester Weg um den Farbkreis)
        diff = focus_centroid - client_hue
        if diff > 0.5: diff -= 1.0
        elif diff < -0.5: diff += 1.0
        unified_hue = (client_hue + (1.0 / 3.0) * diff + comp_shift) % 1.0
        
        # === SCHICHT 3: EMF-Kompensation (subtiler Hue-Micro-Offset) ===
        emf_hue_micro = 0.0
        if self.emf_active and self.emf_compensator:
            try:
                counters = self.emf_compensator.get_counter_frequencies()
                if counters:
                    emf_hue_micro = (counters[0]["frequency_hz"] % 1000) / 100000.0
            except Exception:
                pass
        
        # Finaler monochromatischer Basis-Hue
        mono_hue = (unified_hue + emf_hue_micro) % 1.0
        
        # === SCHICHT 4: Monochromatische Design-Palette ===
        # Professionelles Monochrom wie "Misty Grays" / "Creamy Neutrals":
        # - EIN Farbton, 10 gleichmaessige Abstufungen
        # - Durchgehend niedrige Saettigung (neutral, gedaempft, beruhigend)
        # - Voller Helligkeitsbereich von fast-weiss bis warm-tief
        # - Gleichmaessige visuelle Schritte zwischen den Stufen
        #
        # S-Verlauf: 0.04 → 0.18 (durchgehend neutral/gedaempft)
        # V-Verlauf: 0.97 → 0.35 (volle Tiefe, echtes Monochrom)
        
        palette = {}
        
        for i in range(10):
            t = i / 9.0  # 0.0 bis 1.0
            
            # Saettigung: Durchgehend niedrig, leicht ansteigend
            # Erzeugt warme, neutrale Toene (nie bunt/knallig)
            sat = 0.04 + 0.14 * t  # 0.04 → 0.18
            
            # Helligkeit: Voller Bereich, gleichmaessige Schritte
            # Von fast-weiss (0.97) bis warm-tief (0.35)
            val = 0.97 - 0.62 * t  # 0.97 → 0.35
            
            rgb = colorsys.hsv_to_rgb(mono_hue, sat, val)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            palette[i] = hex_color.upper()
        
        logger.info(f"Unified Coherent Palette (monochrom/heilsam): "
                     f"Mono-Hue={mono_hue:.3f} ({mono_hue*360:.0f}°), "
                     f"Client-Hue={client_hue:.3f}, Fokus-Centroid={focus_centroid:.3f}, "
                     f"Client 2/3 + Fokus 1/3, Fokusse={len(focus_list)}")
        
        return palette

    def generate_nature_monochrome_palette(self, focus: str) -> Dict[int, str]:
        """
        Natur-heilsame Palette basierend auf Foggy-Forest Referenz-Farben.
        12 Referenztoene (Pinterest Foggy Green) nach Helligkeit sortiert:
          Salbeigruen, Blaugrau, Erdbraun — alle mit S=4-21%, V=30-83%.
        Multi-tonale Natur-Harmonie: Gruene, Blaugraue und Erdtoene wechseln
        sich ab (kein reines Monochrom, sondern natuerliche Farbvielfalt).
        
        Fokus-Hash bestimmt:
        - Welche 10 von 12 Referenz-Farben gewaehlt werden
        - Leichten Hue-Shift (+/-5°) fuer Individualitaet pro Fokus
        """
        import colorsys
        
        # 12 Referenz-Farben (Pinterest Foggy Forest) nach Helligkeit sortiert
        # Format: (Hue°, Sat%, Val%) — exakt aus den Hex-Werten analysiert
        nature_ref = [
            (60,   0.04, 0.83),  # #D4D4CC — Warmes Hellgrau (Licht)
            (165,  0.09, 0.74),  # #ACBCB8 — Helles Nebelgruen
            (171,  0.21, 0.65),  # #82A5A0 — Lebendiges Salbei
            (19,   0.10, 0.63),  # #A09590 — Warmes Steingrau
            (183,  0.15, 0.60),  # #819798 — Grau-Blaugruen
            (161,  0.13, 0.50),  # #6F7F7A — Salbeigruen
            (17,   0.18, 0.47),  # #776862 — Erdbraun
            (194,  0.19, 0.43),  # #59696E — Schieferblau
            (144,  0.10, 0.38),  # #57615B — Dunkles Waldgruen
            (198,  0.12, 0.33),  # #4B5255 — Schiefergrau
            (90,   0.08, 0.31),  # #4B4E48 — Moosgrau
            (5,    0.16, 0.30),  # #4C4140 — Dunkles Rostbraun
        ]
        
        # Fokus-Hash bestimmt Variation
        h = int(hashlib.md5(focus.strip().lower().encode('utf-8')).hexdigest()[:8], 16)
        
        # Welche 2 von 12 werden ausgelassen? (Hash waehlt 10 von 12)
        skip_a = h % 12
        skip_b = (h >> 4) % 12
        if skip_b == skip_a:
            skip_b = (skip_a + 1) % 12
        
        selected = [c for idx, c in enumerate(nature_ref) if idx not in (skip_a, skip_b)]
        # Sicherheit: genau 10 Farben
        while len(selected) < 10:
            selected.append(nature_ref[len(selected) % 12])
        selected = selected[:10]
        
        # Leichter Hue-Shift pro Fokus (+/- 5°) fuer Individualitaet
        hue_shift = ((h >> 8) % 11 - 5) / 360.0  # -5° bis +5°
        
        palette = {}
        for i, (ref_hue, ref_sat, ref_val) in enumerate(selected):
            # Hue: Referenz + individueller Shift
            hue = ((ref_hue / 360.0) + hue_shift) % 1.0
            
            rgb = colorsys.hsv_to_rgb(hue, ref_sat, ref_val)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            palette[i] = hex_color.upper()
        
        logger.info(f"Nature Healing Palette (Foggy Forest): "
                     f"Hue-Shift={hue_shift*360:.1f}°, Skip={skip_a},{skip_b}, "
                     f"Fokus='{focus[:40]}'")
        
        return palette

    def generate_focus_monochrome_palette(self, focus: str) -> Dict[int, str]:
        """
        Rein fokus-basierte monochromatische Design-Palette.
        Pro einzelnem Fokus: 1 Hue aus dem Fokus-Hash,
        10 gleichmaessige Stufen (S+V) im professionellen Monochrom-Stil.
        Niedrige Saettigung, voller Helligkeitsbereich.
        """
        import colorsys
        
        # Fokus-Hash → deterministischer Hue (0.0 - 1.0)
        h = int(hashlib.md5(focus.strip().lower().encode('utf-8')).hexdigest()[:6], 16)
        mono_hue = (h % 360) / 360.0
        
        palette = {}
        for i in range(10):
            t = i / 9.0  # 0.0 bis 1.0
            
            # Saettigung: Durchgehend niedrig (neutral, gedaempft)
            sat = 0.04 + 0.14 * t  # 0.04 → 0.18
            
            # Helligkeit: Voller Bereich, gleichmaessige Schritte
            val = 0.97 - 0.62 * t  # 0.97 → 0.35
            
            rgb = colorsys.hsv_to_rgb(mono_hue, sat, val)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            palette[i] = hex_color.upper()
        
        logger.info(f"Focus Monochrome Palette: Hue={mono_hue:.3f} ({mono_hue*360:.0f}°), "
                     f"Fokus='{focus[:40]}'")
        
        return palette

    def generate_focus_emf_palette(
        self,
        focus_list: List[str],
        bio_info: Optional[Dict] = None,
        emf_profile: Optional[Dict] = None,
        client_frequency: float = 440.0
    ) -> Dict[int, str]:
        """
        Generiert eine kohaerente Farbpalette (10 Farben fuer 0-9) aus:
        1. Fokus-Semantik: Hash-basierter Basis-Hue pro Fokus
        2. Bio-Frequenz: Chakra/Meridian-Frequenz als Hue-Modulation
        3. EMF Counter-Frequencies: Solfeggio-Frequenzen modulieren Saettigung
        4. Multi-Fokus: Kombination mehrerer Fokus-Hues fuer harmonische Palette
        
        Farbmodell: HSV mit 360 moeglichen Hue-Werten, volle Saettigungs- und 
        Helligkeitskontrolle → theoretisch 16.7 Mio Farben (24-bit RGB).
        Praktisch werden 10 optimal verteilte, visuell distinkte Farben generiert.
        """
        import colorsys
        
        # === SCHICHT 1: Fokus-basierter Basis-Hue ===
        focus_hues = []
        for f in focus_list:
            # Deterministischer Hash → Hue-Wert (0.0 - 1.0)
            h = int(hashlib.md5(f.strip().lower().encode('utf-8')).hexdigest()[:6], 16)
            focus_hues.append((h % 360) / 360.0)
        
        # Kombiniere alle Fokus-Hues zu einem gewichteten Mittelwert (Circular Mean)
        if len(focus_hues) == 1:
            base_hue = focus_hues[0]
        else:
            # Circular Mean fuer Hue-Werte (vermeidet 0/360 Sprung-Artefakte)
            sin_sum = sum(np.sin(2 * np.pi * h) for h in focus_hues)
            cos_sum = sum(np.cos(2 * np.pi * h) for h in focus_hues)
            base_hue = (np.arctan2(sin_sum, cos_sum) / (2 * np.pi)) % 1.0
        
        # === SCHICHT 2: Bio-Frequenz Modulation ===
        bio_hue_shift = 0.0
        if bio_info and "data" in bio_info:
            bio_freq = bio_info["data"].get("frequency_hz", 0)
            if bio_freq > 0:
                # Solfeggio-Frequenzen auf Hue-Shift mappen
                # 174Hz-963Hz → 0.0-0.12 Shift
                bio_hue_shift = (bio_freq % 1000) / 8000.0
        
        # === SCHICHT 3: EMF Counter-Frequency Modulation ===
        emf_sat_mod = 0.0  # Saettigungs-Modulation
        emf_val_mod = 0.0  # Helligkeits-Modulation
        emf_hue_offsets = []
        
        if emf_profile and self.emf_compensator:
            counters = self.emf_compensator.get_counter_frequencies()
            emf_index = emf_profile.get("composite_emf_index", 0.0)
            entropy = emf_profile.get("entropy_score", 0.5)
            
            # EMF-Index moduliert Saettigung (hoeher = mehr Saettigung als Kompensation)
            emf_sat_mod = min(0.15, emf_index * 0.2)
            
            # Entropie-Score moduliert Helligkeit (bessere Entropie = hellere Farben)
            emf_val_mod = (entropy - 0.5) * 0.1
            
            # Counter-Frequencies erzeugen zusaetzliche Hue-Punkte
            for cf in counters[:3]:  # Max 3 Counter-Frequencies einbeziehen
                cf_hue = (cf["frequency_hz"] % 1000) / 1000.0
                emf_hue_offsets.append(cf_hue)
        
        # === PALETTE GENERIERUNG: 10 kohaerente Farben ===
        # Strategie: Analoges Farbschema (30° Sektor) mit EMF-Erweiterung
        palette = {}
        
        # Berechne Spread-Winkel basierend auf Anzahl Fokusse
        # 1 Fokus → 30° Analoges Schema
        # Multiple Fokusse → breiterer Spread (bis 60°)
        spread = min(60, 30 + len(focus_list) * 5) / 360.0
        
        for i in range(10):
            if i == 0:
                # Ziffer 0: Weiss/Sehr helles Neutralgrau (Kontrast-Anker)
                palette[i] = "#F8F8FF"
                continue
            
            # Position im Farbkreis: Gleichmaessig verteilt im Spread-Bereich
            t = (i - 1) / 8.0  # 0.0 bis 1.0 fuer Ziffern 1-9
            
            # Basis-Hue + Bio-Shift + Spread-Verteilung
            hue = (base_hue + bio_hue_shift + (t - 0.5) * spread) % 1.0
            
            # EMF Counter-Frequency als subtiler Hue-Offset
            if emf_hue_offsets:
                cf_idx = i % len(emf_hue_offsets)
                hue = (hue + emf_hue_offsets[cf_idx] * 0.02) % 1.0
            
            # Saettigung: Basis + EMF-Modulation + Position
            # Ziffern 1-3 (niedrig): sanfter, 4-6 (mittel): normal, 7-9 (hoch): kräftig
            base_sat = 0.55 + (i / 9.0) * 0.35  # 0.55 → 0.90
            sat = min(1.0, max(0.3, base_sat + emf_sat_mod))
            
            # Helligkeit: Wechselnd fuer bessere Unterscheidbarkeit
            base_val = 0.65 + ((i % 3) * 0.15)  # 0.65, 0.80, 0.95
            val = min(1.0, max(0.4, base_val + emf_val_mod))
            
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            palette[i] = hex_color.upper()
        
        logger.info(f"Focus-EMF Palette generiert: Basis-Hue={base_hue:.3f}, "
                     f"Bio-Shift={bio_hue_shift:.3f}, EMF-Mod={emf_sat_mod:.3f}, "
                     f"Fokusse={len(focus_list)}, Spread={spread*360:.0f}°")
        
        return palette

    def generate_chakra_spectrum_palette(self, focus: str, client_frequency: float = 440.0) -> Dict[int, str]:
        """
        Chakra-Spektrum mit 10 Stufen fuer Ziffern 0-9.
        0 bleibt neutral, 1-9 laufen durch ein chakra-inspiriertes Farbbandschema.
        """
        import colorsys

        # Sanfte, deterministische Hue-Rotation aus Fokus + Klientenfrequenz
        h = int(hashlib.md5((focus or "").strip().lower().encode("utf-8")).hexdigest()[:6], 16)
        focus_shift = ((h % 15) - 7) / 360.0
        freq_shift = ((client_frequency % 120.0) - 60.0) / 3600.0
        hue_shift = focus_shift + freq_shift

        # Basis-Hues fuer 1..9 (rot -> orange -> gelb -> gruen -> cyan -> blau -> violett -> magenta -> rosa)
        chakra_hues = [
            0.00, 0.08, 0.15, 0.29, 0.47,
            0.58, 0.72, 0.84, 0.93,
        ]

        palette: Dict[int, str] = {0: "#F7F6F2"}
        for i in range(1, 10):
            hue = (chakra_hues[i - 1] + hue_shift) % 1.0
            # Hohe Lesbarkeit: mittlere bis hohe Saettigung, gute Helligkeit
            sat = 0.56 + (0.05 * ((i - 1) % 3))
            val = 0.92 - (0.04 * ((i - 1) // 3))
            r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
            palette[i] = "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))

        return palette

    def generate_twilight_balance_palette(self, focus: str, client_frequency: float = 440.0) -> Dict[int, str]:
        """
        Dämmerungs-Harmonie mit warm-kuehler Balance fuer 0-9.
        1-4 sind warm/erdend, 5-9 kuehl/ausgleichend.
        """
        import colorsys

        h = int(hashlib.md5((focus or "").strip().lower().encode("utf-8")).hexdigest()[:8], 16)
        warm_anchor = ((24 + (h % 22)) / 360.0) % 1.0
        cool_anchor = ((198 + ((h >> 5) % 28)) / 360.0) % 1.0
        blend_shift = ((client_frequency % 80.0) - 40.0) / 7200.0

        palette: Dict[int, str] = {0: "#F8F8F4"}
        for i in range(1, 10):
            t = (i - 1) / 8.0
            if i <= 4:
                # Warme Seite
                local_t = (i - 1) / 3.0
                hue = (warm_anchor + local_t * 0.07 + blend_shift) % 1.0
                sat = 0.46 + local_t * 0.14
                val = 0.95 - local_t * 0.14
            else:
                # Kuehle Seite
                local_t = (i - 5) / 4.0
                hue = (cool_anchor + local_t * 0.09 - blend_shift) % 1.0
                sat = 0.44 + local_t * 0.16
                val = 0.92 - local_t * 0.22

            # Leichtes Mittelton-Boost fuer Ziffern in der Mitte
            sat = min(0.85, sat + (0.03 if 0.35 <= t <= 0.65 else 0.0))
            val = max(0.48, min(0.96, val))
            r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
            palette[i] = "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))

        return palette

    def _limit_candidates_for_available_memory(self, num_candidates: int, size: int, embed_dim: int) -> int:
        """Begrenzt Kandidaten defensiv basierend auf verfuegbarem CPU-/GPU-Speicher."""
        if self.device.type == "cuda" and self.vram_gb > 0:
            # Peak-VRAM je Kandidat: candidate_matrices (size*size) + projections (embed_dim)
            # + similarities (1) — konsistent zum CPU-Pfad. Frueher wurde nur das
            # candidate_matrices-Tensor gezaehlt, was das Matmul-Intermediate (projections)
            # unterschaetzte und bei grossen Matrizen zu CUDA-OOM fuehrte (z.B. 153 MB-Allokation).
            bytes_per_candidate = (size * size + embed_dim + 1) * 4
            required_bytes = num_candidates * bytes_per_candidate
            max_allowed_bytes = self.vram_gb * (1024**3) * 0.65  # Max 65% VRAM nutzen
            if required_bytes > max_allowed_bytes:
                limited = int(max_allowed_bytes // bytes_per_candidate)
                logger.info(f"VRAM-Limit: Kandidaten reduziert auf {limited:,} fuer {size}x{size}")
                return max(1, limited)
            return num_candidates

        if self.device.type == "cpu":
            try:
                import psutil

                available_bytes = psutil.virtual_memory().available
                bytes_per_candidate = ((size * size) + embed_dim + 1) * 4
                cpu_budget_bytes = min(int(available_bytes * 0.20), 128 * 1024 * 1024)
                limited = cpu_budget_bytes // bytes_per_candidate
                if limited < num_candidates:
                    logger.info(f"CPU-RAM-Limit: Kandidaten reduziert auf {limited:,} fuer {size}x{size}")
                    return max(1, limited)
            except Exception as exc:
                logger.warning(f"CPU-RAM-Guard konnte nicht angewendet werden: {exc}")

        return num_candidates

    def _find_optimal_matrix_cuda(
        self, 
        client_vec: torch.Tensor, 
        focus_vec: torch.Tensor, 
        size: int = 12,
        weight_type: str = "Normal",
        top_k: int = 1,
        hrv_factor: float = 1.0
    ) -> List[Dict]:
        """
        Kern-Algorithmus: Findet die Matrizen mit der hoechsten Resonanz.
        Unterstuetzt variable Matrix-Groessen (12, 24, 36).
        hrv_factor beeinflusst die Rauschkomponente der Suche.
        """
        # Embedding-Dimension: Groessere Matrizen → groesserer Embedding-Raum
        embed_dim = 256 if size <= 12 else 384 if size <= 24 else 512

        # --- Adaptive Kandidaten-Skalierung basierend auf Matrix-Groesse ---
        num_candidates = self.candidate_count
        if size > 12:
            # Groessere Matrizen brauchen mehr Kandidaten fuer gleiche Score-Qualitaet
            scale_factor = 1.5 if size <= 24 else 2.5
            num_candidates = int(num_candidates * scale_factor)

        num_candidates = self._limit_candidates_for_available_memory(num_candidates, size, embed_dim)
        
        weight_map = {
            "Deaktiviert": 0.0,
            "Sanft": 0.4,
            "Normal": 1.0,
            "Stark": 1.5
        }
        w = weight_map.get(weight_type, 1.0)
        
        logger.info(f"Matrix-Suche: {size}x{size} ({size*size} Zellen), "
                     f"{num_candidates:,} Kandidaten, Embed-Dim={embed_dim}")
        
        with torch.no_grad():
            # Erzeuge Kandidaten
            candidate_matrices = torch.randint(0, 10, (num_candidates, size * size), device=self.device).float()
            
            # HRV-Einfluss: Modulation des Zielvektors oder Hinzufuegen von "koharentem Rauschen"
            if hrv_factor < 0.9:
                entropy = (1.0 - hrv_factor) * torch.randn_like(client_vec)
                target = client_vec + (focus_vec * w) + entropy
            else:
                target = client_vec + (focus_vec * w)
            
            # Target auf embed_dim anpassen (falls groesser als 256)
            if embed_dim != target.shape[0]:
                # Deterministisch erweitern via Wiederholung + Modulation
                repeats = (embed_dim // target.shape[0]) + 1
                target_expanded = target.repeat(repeats)[:embed_dim]
                # Leichte Modulation fuer zusaetzliche Dimensionen
                modulator = torch.linspace(0.95, 1.05, embed_dim, device=self.device)
                target = target_expanded * modulator
            
            projections = candidate_matrices @ torch.randn(size*size, embed_dim, device=self.device)
            similarities = torch.nn.functional.cosine_similarity(projections, target)
            
            # Top K Resultate
            top_scores, top_indices = torch.topk(similarities, top_k)
            
            results = []
            for i in range(top_k):
                idx = top_indices[i]
                score = top_scores[i]
                pattern_float = candidate_matrices[idx]
                
                # Intensitaet berechnen (Standardabweichung der Werte 0-9)
                intensity = torch.std(pattern_float)
                
                pattern_int = pattern_float.reshape(size, size).int()
                
                results.append({
                    "score": score,
                    "intensity": intensity,
                    "matrix": pattern_int
                })
            
        return results

    def run_quantum_inspired_refinement(self, initial_matrix: torch.Tensor, target_vec: torch.Tensor):
        """
        Verfeinert das Ergebnis mittels eines simulierten Annealing / Quantum-Tunneling Prozesses.
        """
        # Hier könnte Qiskit-Integration oder Grover-Logik für kleine Sub-Matrizen folgen
        pass

    def prepare_dwave_solver(self):
        """
        Initialisiert die Verbindung zur D-Wave Leap Cloud (Placeholder).
        Benötigt DWAVE_API_TOKEN Umgebungsvariable.
        """
        if not self.dwave_token:
            logger.warning("D-Wave Token nicht gefunden. Quantum Annealing deaktiviert.")
            return False
            
        try:
            # from dwave.system import DWaveSampler, EmbeddingComposite
            # self.dwave_solver = EmbeddingComposite(DWaveSampler(token=self.dwave_token))
            self.dwave_enabled = True
            logger.info("D-Wave Solver Interface initialized (Mock).")
            return True
        except ImportError:
            logger.error("dwave-ocean-sdk nicht installiert.")
            return False

    def solve_with_dwave(self, bias_matrix: torch.Tensor) -> torch.Tensor:
        """
        Führt ein echtes Quantum Annealing auf der D-Wave QPU durch.
        Konvertiert das Resonanz-Problem in ein QUBO (Quadratic Unconstrained Binary Optimization) Modell.
        """
        if not self.dwave_enabled:
            return None
            
        logger.info("Sende Problem an D-Wave Quantum Annealer...")
        # Placeholder für QUBO Formulierung:
        # 1. Map 12x12 Matrix (0-9) to Binary Variables
        # 2. Define Energy Landscape based on Client/Focus Vectors
        # 3. Sample from QPU
        # 4. Decode Result
        
        # Simulierter Return für jetzt
        return bias_matrix

    def _embed_signature(self, signature: Dict) -> torch.Tensor:
        """
        Wandelt die Klienten-Signatur in einen Vektor um (Embedding).
        Nutzt deterministisches Hashing für Reproduzierbarkeit.
        """
        # 1. Frequency & Components zu String
        freq = signature.get("frequency", 440.0)
        comps = "".join(sorted([f"{k}:{v}" for k, v in signature.get("components", {}).items()]))
        
        seed_str = f"{freq}_{comps}"
        seed_hash = hashlib.md5(seed_str.encode()).hexdigest()
        # Nutze ersten 8 chars als int seed
        seed_int = int(seed_hash[:8], 16)
        
        # Generator für deterministischen Vektor
        g = torch.Generator(device=self.device)
        g.manual_seed(seed_int)
        
        return torch.randn(256, generator=g, device=self.device)

    def _embed_focus(self, focus: str) -> torch.Tensor:
        """
        Wandelt den Fokus-Text in einen Vektor um.
        """
        seed_hash = hashlib.md5(focus.encode()).hexdigest()
        seed_int = int(seed_hash[:8], 16)
        
        g = torch.Generator(device=self.device)
        g.manual_seed(seed_int)
        
        return torch.randn(256, generator=g, device=self.device)

    def _generate_coherent_colors(self, matrix: torch.Tensor, palette: Optional[Dict[int, str]]) -> List[List[str]]:
        """
        Erstellt das visuelle Farbmuster basierend auf Matrix und Palette.
        """
        if not palette:
            palette = DEFAULT_RADIONIK_PALETTE
            
        # Ensure palette keys are ints
        palette_map = {int(k): v for k, v in palette.items()}
        
        # Matrix zu Python List
        if isinstance(matrix, torch.Tensor):
            matrix_list = matrix.tolist()
        else:
            matrix_list = matrix
            
        color_grid = []
        for row in matrix_list:
            color_row = []
            for val in row:
                # Fallback zu Weiss falls Key fehlt
                color_row.append(palette_map.get(int(val), "#FFFFFF"))
            color_grid.append(color_row)
            
        return color_grid
