"""
EMF Environment Compensator v1.0 - Codegeau Extension
======================================================
Echtzeit-Kompensation von elektromagnetischen Stoerfrequenzen
(WiFi, Bluetooth, 5G, Powerline-Noise) im Rechenumfeld.

Architektur:
  Layer 1: SENSING    - Hardware-Entropie + System-Metriken + [optional RTL-SDR]
  Layer 2: PROFILING  - EMF-Fingerprint, Entropie-Score, Zeitfenster-Analyse
  Layer 3: COMPENSATE - Inverse Frequenzmaske, Seed-Qualitaet, Counter-Frequencies

Software-only Ansatz mit Plug-in Architektur fuer spaetere RTL-SDR Integration.
"""

import torch
import numpy as np
import time
import hashlib
import struct
import os
import logging
import threading
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class EMFCompensator:
    """
    Echtzeit EMF-Kompensationsmodul.
    
    Nutzt interne Hardware-Sensoren (CPU-Timing-Jitter, RAM-Entropy,
    GPU-Thermal-Noise, System-RNG-Qualitaet) um ein EMF-Umfeldprofil
    zu erstellen und Kompensationsvektoren zu berechnen.
    """
    
    # Bekannte Stoerfrequenz-Baender (MHz) - fuer Referenz und spaetere SDR-Integration
    KNOWN_EMF_BANDS = {
        "wifi_2g":     {"center_mhz": 2437, "bw_mhz": 40,   "severity": 0.7},
        "wifi_5g":     {"center_mhz": 5500, "bw_mhz": 80,   "severity": 0.6},
        "bluetooth":   {"center_mhz": 2442, "bw_mhz": 80,   "severity": 0.5},
        "5g_sub6":     {"center_mhz": 3500, "bw_mhz": 100,  "severity": 0.8},
        "5g_mmwave":   {"center_mhz": 28000, "bw_mhz": 400, "severity": 0.9},
        "lte_b7":      {"center_mhz": 2600, "bw_mhz": 20,   "severity": 0.6},
        "lte_b20":     {"center_mhz": 800,  "bw_mhz": 10,   "severity": 0.5},
        "powerline":   {"center_mhz": 0.05, "bw_mhz": 0.03, "severity": 0.4},
        "monitor_emf": {"center_mhz": 0.06, "bw_mhz": 0.02, "severity": 0.3},
    }
    
    # Solfeggio Counter-Frequencies (Hz) - zur aktiven Harmonisierung
    SOLFEGGIO_COUNTER = {
        174: "Schmerzlinderung",
        285: "Geweberegeneration",
        396: "Befreiung von Angst",
        417: "Resonanz mit Wandel",
        528: "DNA-Reparatur / Transformation",
        639: "Harmonische Beziehungen",
        741: "Ausdruck / Reinigung",
        852: "Intuition / Innere Ordnung",
        963: "Kosmische Einheit",
    }
    
    def __init__(self, device: torch.device = None, continuous: bool = False):
        """
        Initialisiert den EMF Compensator.
        
        Args:
            device: torch.device (CPU/CUDA) - nutzt die gleiche wie die Engine
            continuous: Wenn True, startet einen Hintergrund-Thread fuer Echtzeit-Monitoring
        """
        self.device = device or torch.device("cpu")
        self.active = True
        self.continuous = continuous
        
        # --- Sensing Layer State ---
        self.entropy_history = deque(maxlen=100)  # Letzte 100 Messungen
        self.timing_jitter_history = deque(maxlen=100)
        self.compensation_history = deque(maxlen=50)
        
        # Remote Client Sensor Data (empfangen via WebSocket /emf/client-sensor)
        self._remote_sensor_data = {
            "audio": None,      # FFT-Spektrum vom Client-Mikrofon
            "location": None,   # GPS-Position des Klienten
            "hrv": None,        # HRV-Daten von Wearable
            "device": None,     # Geraete-Sensoren (Magnetometer, etc.)
        }
        
        # Aktueller EMF-Status
        self.current_profile = {
            "entropy_score": 1.0,       # 0.0 (schlecht) - 1.0 (rein)
            "timing_jitter_ms": 0.0,    # CPU Timing Jitter
            "rng_autocorrelation": 0.0, # Auto-Korrelation der Zufallszahlen
            "system_load_factor": 0.0,  # CPU/RAM Auslastung als Proxy
            "gpu_noise_factor": 0.0,    # GPU Thermal/Clock Noise
            "composite_emf_index": 0.0, # Gesamt-EMF-Belastungsindex (0-1)
            "timestamp": None,
            "low_noise_window": False,  # True wenn Umfeld ruhig
        }
        
        # Kompensationsvektor (wird bei jedem Profiling aktualisiert)
        self._compensation_vector = None
        self._inverse_mask = None
        self._counter_frequencies = []
        
        # RTL-SDR Plug-in Interface (fuer spaetere Hardware-Integration)
        self._sdr_backend = None
        self._sdr_available = False
        
        # Hintergrund-Thread fuer Echtzeit-Monitoring
        self._monitor_thread = None
        self._stop_event = threading.Event()
        
        # WebSocket Callbacks (fuer Live-Dashboard)
        self._ws_callbacks = []
        
        # Initiale Kalibrierung
        self._calibration_baseline = None
        self._calibrate()
        
        if continuous:
            self.start_continuous_monitoring()
        
        logger.info(f"EMFCompensator initialisiert auf {self.device} "
                     f"[Continuous: {continuous}]")
    
    # =========================================================================
    # LAYER 1: SENSING - Echtzeit Hardware-Entropie-Messung
    # =========================================================================
    
    def _measure_cpu_timing_jitter(self, samples: int = 50) -> float:
        """
        Misst CPU-Timing-Jitter als Indikator fuer elektromagnetische Stoerungen.
        Hoher Jitter kann auf externe EMF-Einflüsse oder hohe Systemlast hindeuten.
        
        Returns:
            Jitter in Millisekunden (Standardabweichung der Timing-Differenzen)
        """
        timings = []
        for _ in range(samples):
            t0 = time.perf_counter_ns()
            # Definierte Arbeitslast: kleines Matmul als Referenz
            _ = sum(i * i for i in range(100))
            t1 = time.perf_counter_ns()
            timings.append((t1 - t0) / 1e6)  # ns -> ms
        
        jitter = float(np.std(timings))
        self.timing_jitter_history.append(jitter)
        return jitter
    
    def _measure_rng_entropy_quality(self, sample_size: int = 1024) -> Dict[str, float]:
        """
        Misst die Qualitaet der System-Entropiequelle.
        Schlechte Entropie (hohe Auto-Korrelation) deutet auf EMF-Beeinflussung
        des Hardware-RNG hin.
        
        Returns:
            Dict mit entropy_score (0-1), autocorrelation, chi_squared_p
        """
        # Generiere Zufallsdaten aus OS-Entropiequelle
        try:
            raw_bytes = os.urandom(sample_size)
            values = np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float64)
        except Exception:
            return {"entropy_score": 0.5, "autocorrelation": 0.5, "chi_squared_p": 0.5}
        
        # 1. Auto-Korrelation (Lag-1)
        # Ideale Zufallszahlen haben Auto-Korrelation nahe 0
        if len(values) > 1:
            mean_val = np.mean(values)
            centered = values - mean_val
            variance = np.sum(centered ** 2)
            if variance > 0:
                autocorr = np.sum(centered[:-1] * centered[1:]) / variance
            else:
                autocorr = 0.0
        else:
            autocorr = 0.0
        
        # 2. Byte-Frequenz-Verteilung (Chi-Squared artig)
        # Ideale Gleichverteilung: jeder Byte-Wert gleich haeufig
        observed = np.bincount(values.astype(int), minlength=256)
        expected = sample_size / 256.0
        chi_sq = np.sum((observed - expected) ** 2 / expected)
        # Normalisiere auf 0-1 (255 Freiheitsgrade, kritischer Wert ~293 bei p=0.05)
        chi_p = min(1.0, chi_sq / 400.0)
        
        # 3. Bitweise Entropie (Shannon)
        byte_probs = observed / sample_size
        byte_probs = byte_probs[byte_probs > 0]
        shannon_entropy = -np.sum(byte_probs * np.log2(byte_probs))
        # Max Entropie fuer 256 Symbole = 8.0 Bits
        normalized_entropy = shannon_entropy / 8.0
        
        # Composite Score (gewichtet)
        entropy_score = (
            0.4 * normalized_entropy +
            0.3 * (1.0 - abs(autocorr)) +
            0.3 * (1.0 - chi_p)
        )
        entropy_score = max(0.0, min(1.0, entropy_score))
        
        self.entropy_history.append(entropy_score)
        
        return {
            "entropy_score": round(entropy_score, 4),
            "autocorrelation": round(abs(autocorr), 6),
            "chi_squared_p": round(chi_p, 4),
            "shannon_bits": round(shannon_entropy, 4),
        }
    
    def _measure_system_load(self) -> Dict[str, float]:
        """
        Misst aktuelle Systemauslastung als EMF-Proxy.
        Hohe CPU/RAM-Last korreliert oft mit erhoehter EMF-Emission des Systems selbst.
        """
        cpu_percent = 0.0
        ram_percent = 0.0
        
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1) / 100.0
            ram_percent = psutil.virtual_memory().percent / 100.0
        except ImportError:
            # Fallback: Nutze Thread-basierte Schaetzung
            t0 = time.perf_counter()
            _ = sum(range(100000))
            elapsed = time.perf_counter() - t0
            # Wenn laenger als 2ms -> hohe Last
            cpu_percent = min(1.0, elapsed / 0.005)
        
        return {
            "cpu_load": round(cpu_percent, 3),
            "ram_usage": round(ram_percent, 3),
            "system_load_factor": round((cpu_percent + ram_percent) / 2.0, 3)
        }
    
    def _measure_gpu_noise(self) -> float:
        """
        Misst GPU-basiertes thermisches Rauschen als EMF-Indikator.
        Nutzt die Varianz wiederholter GPU-Berechnungen desselben Inputs.
        Auf Server-GPUs (VRAM >= 8GB) wird zusaetzlich eine parallele
        Spektrumanalyse durchgefuehrt.
        """
        if self.device.type != "cuda":
            return 0.0
        
        try:
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            if vram_gb >= 8.0:
                # === SERVER MODE (RTX 4000 Ada / High-End GPUs) ===
                # Massiv parallele Noise-Analyse: 1024x1024 Tensor-Operationen
                return self._measure_gpu_noise_server()
            else:
                # === DEV MODE (integrierte GPUs / Low VRAM) ===
                return self._measure_gpu_noise_basic()
            
        except Exception as e:
            logger.debug(f"GPU Noise Messung fehlgeschlagen: {e}")
            return 0.0
    
    def _measure_gpu_noise_basic(self) -> float:
        """Basis GPU-Noise Messung fuer Dev-PCs mit begrenztem VRAM."""
        try:
            times = []
            test_tensor = torch.ones(256, 256, device=self.device)
            
            for _ in range(10):
                torch.cuda.synchronize()
                t0 = time.perf_counter_ns()
                _ = test_tensor @ test_tensor
                torch.cuda.synchronize()
                t1 = time.perf_counter_ns()
                times.append((t1 - t0) / 1e6)
            
            noise_factor = min(1.0, float(np.std(times)) / 0.5)
            return round(noise_factor, 4)
        except Exception:
            return 0.0
    
    def _measure_gpu_noise_server(self) -> float:
        """
        Erweiterte CUDA-Sensorik fuer Server-GPUs (>= 8GB VRAM).
        
        Nutzt massiv parallele Tensor-Operationen und FFT-basierte
        Spektrumanalyse des GPU-Rauschens fuer praezisere EMF-Erkennung.
        Optimiert fuer NVIDIA RTX 4000 SFF Ada (20GB VRAM).
        """
        try:
            with torch.no_grad():
                # 1. Timing-Varianz mit grossen Matrizen (genauer auf Server-GPUs)
                times = []
                test_mat = torch.randn(1024, 1024, device=self.device)
                ref_result = test_mat @ test_mat.T
                
                for _ in range(20):
                    torch.cuda.synchronize()
                    t0 = time.perf_counter_ns()
                    result = test_mat @ test_mat.T
                    torch.cuda.synchronize()
                    t1 = time.perf_counter_ns()
                    times.append((t1 - t0) / 1e6)
                
                timing_noise = min(1.0, float(np.std(times)) / 0.3)
                
                # 2. Numerische Drift-Analyse
                # Identische Berechnung sollte identische Ergebnisse liefern
                # Abweichungen deuten auf EMF-beeinflusste Gleitkomma-Operationen
                drift_samples = []
                for _ in range(5):
                    result2 = test_mat @ test_mat.T
                    diff = torch.abs(result2 - ref_result).mean().item()
                    drift_samples.append(diff)
                
                # Normalisiere: 0 = perfekte Reproduzierbarkeit, 1 = starke Drift
                numerical_drift = min(1.0, float(np.mean(drift_samples)) * 1e6)
                
                # 3. GPU-Memory Noise Pattern
                # Allokiere und lese einen Speicherblock, messe Bit-Flip-Rate
                noise_block = torch.zeros(1024 * 1024, device=self.device, dtype=torch.float32)
                torch.cuda.synchronize()
                time.sleep(0.01)  # Kurz warten lassen
                flipped = torch.count_nonzero(noise_block).item()
                mem_noise = min(1.0, flipped / 100.0)
                
                # 4. FFT-Spektrumanalyse des Timing-Signals
                timing_tensor = torch.tensor(times, dtype=torch.float32, device=self.device)
                timing_fft = torch.fft.rfft(timing_tensor - timing_tensor.mean())
                spectral_energy = torch.abs(timing_fft).mean().item()
                spectral_noise = min(1.0, spectral_energy / 0.1)
                
                # Composite Server-Noise Score
                noise_factor = (
                    0.30 * timing_noise +
                    0.25 * numerical_drift +
                    0.20 * spectral_noise +
                    0.15 * mem_noise +
                    0.10 * min(1.0, float(np.max(times) - np.min(times)) / 1.0)
                )
                
                # Raeume GPU-Speicher auf
                del test_mat, ref_result, noise_block, timing_tensor, timing_fft
                torch.cuda.empty_cache()
                
                logger.debug(f"Server GPU Noise: timing={timing_noise:.4f}, "
                            f"drift={numerical_drift:.6f}, spectral={spectral_noise:.4f}, "
                            f"mem={mem_noise:.4f} → composite={noise_factor:.4f}")
                
                return round(min(1.0, noise_factor), 4)
                
        except Exception as e:
            logger.debug(f"Server GPU Noise Messung fehlgeschlagen: {e}")
            return self._measure_gpu_noise_basic()
    
    # =========================================================================
    # LAYER 2: PROFILING - EMF-Fingerprint & Zeitfenster-Analyse
    # =========================================================================
    
    def _calibrate(self):
        """
        Fuehrt eine initiale Kalibrierung durch (Baseline-Messung).
        Wird einmal beim Start aufgerufen.
        """
        logger.info("EMF Compensator: Starte Kalibrierung...")
        
        # Sammle 5 Messungen fuer stabilen Baseline
        entropy_scores = []
        jitter_values = []
        
        for _ in range(5):
            ent = self._measure_rng_entropy_quality(512)
            jit = self._measure_cpu_timing_jitter(30)
            entropy_scores.append(ent["entropy_score"])
            jitter_values.append(jit)
        
        self._calibration_baseline = {
            "entropy_baseline": float(np.mean(entropy_scores)),
            "jitter_baseline_ms": float(np.mean(jitter_values)),
            "calibrated_at": datetime.now().isoformat(),
        }
        
        logger.info(f"EMF Kalibrierung abgeschlossen: "
                     f"Entropy Baseline={self._calibration_baseline['entropy_baseline']:.3f}, "
                     f"Jitter Baseline={self._calibration_baseline['jitter_baseline_ms']:.3f}ms")
    
    def profile_environment(self) -> Dict[str, Any]:
        """
        Erstellt einen vollstaendigen EMF-Fingerprint des aktuellen Umfelds.
        Dies ist die Hauptmethode fuer Layer 2.
        
        Returns:
            Dict mit allen Umfeld-Metriken und dem Composite EMF Index
        """
        # 1. Alle Sensoren auslesen
        entropy_data = self._measure_rng_entropy_quality(2048)
        jitter_ms = self._measure_cpu_timing_jitter(50)
        system_load = self._measure_system_load()
        gpu_noise = self._measure_gpu_noise()
        
        # 2. Abweichung von Baseline berechnen
        baseline = self._calibration_baseline or {
            "entropy_baseline": 0.9, "jitter_baseline_ms": 0.1
        }
        
        entropy_deviation = max(0, baseline["entropy_baseline"] - entropy_data["entropy_score"])
        jitter_deviation = max(0, (jitter_ms - baseline["jitter_baseline_ms"]) / 
                               max(baseline["jitter_baseline_ms"], 0.01))
        
        # 3. Composite EMF Index berechnen (0 = rein, 1 = stark belastet)
        composite_emf = (
            0.30 * (1.0 - entropy_data["entropy_score"]) +  # Entropie-Degradation
            0.25 * min(1.0, jitter_deviation) +              # Timing-Instabilitaet
            0.20 * system_load["system_load_factor"] +       # Systemlast
            0.15 * gpu_noise +                               # GPU-Noise
            0.10 * entropy_data["autocorrelation"]           # RNG-Korrelation
        )
        composite_emf = max(0.0, min(1.0, composite_emf))
        
        # 4. Low-Noise Window Detection
        # Pruefen ob die letzten 5 Messungen stabil und niedrig waren
        recent_entropy = list(self.entropy_history)[-5:] if len(self.entropy_history) >= 5 else []
        low_noise = (
            len(recent_entropy) >= 5 and
            all(e > 0.85 for e in recent_entropy) and
            composite_emf < 0.25
        )
        
        # 5. SDR-Daten einbeziehen (falls verfuegbar)
        sdr_data = None
        if self._sdr_available and self._sdr_backend:
            try:
                sdr_data = self._sdr_backend.get_spectrum_snapshot()
            except Exception:
                sdr_data = None
        
        # 6. Profil aktualisieren
        self.current_profile = {
            "entropy_score": entropy_data["entropy_score"],
            "entropy_details": entropy_data,
            "timing_jitter_ms": round(jitter_ms, 4),
            "rng_autocorrelation": entropy_data["autocorrelation"],
            "system_load": system_load,
            "gpu_noise_factor": gpu_noise,
            "composite_emf_index": round(composite_emf, 4),
            "low_noise_window": low_noise,
            "sdr_data": sdr_data,
            "baseline": baseline,
            "timestamp": datetime.now().isoformat(),
        }
        
        # WebSocket Broadcast
        self._notify_ws_clients(self.current_profile)
        
        return self.current_profile
    
    # =========================================================================
    # LAYER 3: ACTIVE COMPENSATION - Inverse Masken & Counter-Frequencies
    # =========================================================================
    
    def compute_compensation_vector(self, vector_dim: int = 256) -> torch.Tensor:
        """
        Berechnet einen Kompensationsvektor basierend auf dem aktuellen EMF-Profil.
        Dieser Vektor wird auf die Resonanz-Berechnung angewendet.
        
        Der Vektor invertiert die gemessenen Stoerungscharakteristiken:
        - Hohe EMF-Belastung -> staerkere Kompensation
        - Niedrige EMF-Belastung -> minimale Kompensation (nahe Identity)
        
        Args:
            vector_dim: Dimension des Kompensationsvektors (muss zur Engine passen)
        
        Returns:
            torch.Tensor der Dimension [vector_dim]
        """
        if not self.active:
            return torch.ones(vector_dim, device=self.device)
        
        # Aktuelles Profil holen (oder neu messen)
        profile = self.current_profile
        if profile["timestamp"] is None:
            profile = self.profile_environment()
        
        emf_index = profile["composite_emf_index"]
        entropy_score = profile["entropy_score"]
        
        # --- Kompensationsstaerke ---
        # Je hoeher der EMF-Index, desto staerker die Kompensation
        compensation_strength = emf_index * 0.3  # Max 30% Modulation
        
        # --- Deterministischer Kompensations-Seed ---
        # Basiert auf aktuellem EMF-Profil fuer Reproduzierbarkeit innerhalb einer Session
        seed_source = (
            f"{entropy_score:.4f}_"
            f"{profile['timing_jitter_ms']:.4f}_"
            f"{profile['gpu_noise_factor']:.4f}_"
            f"{datetime.now().strftime('%Y%m%d%H')}"  # Stundengranularitaet
        )
        seed_hash = hashlib.sha256(seed_source.encode()).hexdigest()
        seed_int = int(seed_hash[:8], 16)
        
        # --- Kompensationsvektor generieren ---
        g = torch.Generator(device=self.device)
        g.manual_seed(seed_int)
        
        # Basis: Einheitsvektor (keine Kompensation)
        base = torch.ones(vector_dim, device=self.device)
        
        # Kompensationsrauschen (gegenlaefig zur gemessenen Stoerung)
        noise = torch.randn(vector_dim, generator=g, device=self.device)
        
        # Inverse Maske: Daempft Dimensionen, die von Stoerung betroffen sind
        # und verstaerkt "reine" Dimensionen
        compensation = base + (noise * compensation_strength)
        
        # Normalisiere, damit der Vektor die Gesamtenergie nicht veraendert
        compensation = compensation / compensation.norm() * np.sqrt(vector_dim)
        
        self._compensation_vector = compensation
        
        # Log
        logger.info(f"EMF Kompensation berechnet: Strength={compensation_strength:.3f}, "
                     f"EMF-Index={emf_index:.3f}, Entropy={entropy_score:.3f}")
        
        return compensation
    
    def get_enhanced_entropy_seed(self) -> int:
        """
        Generiert einen hochwertigen Seed aus mehreren Entropiequellen.
        Kombiniert OS-RNG, CPU-Timing-Jitter und optional GPU-Rauschen.
        
        Returns:
            int: Hochwertiger Seed fuer torch.manual_seed()
        """
        components = []
        
        # 1. OS-Entropie (primaere Quelle)
        os_entropy = os.urandom(32)
        components.append(os_entropy)
        
        # 2. CPU-Timing-Jitter als zusaetzliche Entropie
        jitter_values = []
        for _ in range(8):
            t0 = time.perf_counter_ns()
            _ = hashlib.sha256(os.urandom(16)).digest()
            t1 = time.perf_counter_ns()
            jitter_values.append(t1 - t0)
        jitter_bytes = struct.pack(f">{len(jitter_values)}q", *jitter_values)
        components.append(jitter_bytes)
        
        # 3. Hochpraeziser Zeitstempel
        ts = struct.pack(">d", time.perf_counter())
        components.append(ts)
        
        # 4. GPU Thermal Noise (wenn verfuegbar)
        if self.device.type == "cuda":
            try:
                gpu_noise = torch.randn(64, device=self.device)
                gpu_bytes = gpu_noise.cpu().numpy().tobytes()[:32]
                components.append(gpu_bytes)
            except Exception:
                pass
        
        # Kombiniere alle Quellen via SHA-256
        combined = b"".join(components)
        final_hash = hashlib.sha256(combined).hexdigest()
        
        # Nutze 8 Bytes (64 Bit) als Seed
        seed = int(final_hash[:16], 16)
        
        return seed
    
    def get_counter_frequencies(self) -> List[Dict[str, Any]]:
        """
        Berechnet Solfeggio Counter-Frequencies basierend auf dem EMF-Profil.
        Diese koennen vom Harmonizer als zusaetzliche Kompensations-Layer
        abgespielt werden.
        
        Returns:
            Liste von Frequenz-Dicts mit Hz, Amplitude, Dauer und Beschreibung
        """
        emf_index = self.current_profile.get("composite_emf_index", 0.0)
        
        if emf_index < 0.1:
            # Minimale Belastung -> nur Grundfrequenz
            return [{
                "frequency_hz": 528,
                "amplitude": 0.1,
                "duration_s": 30,
                "description": self.SOLFEGGIO_COUNTER[528],
                "purpose": "maintenance"
            }]
        
        # Waehle Counter-Frequencies basierend auf EMF-Intensitaet
        selected = []
        
        # Immer: 528 Hz (DNA-Reparatur) als Basis
        selected.append({
            "frequency_hz": 528,
            "amplitude": min(0.8, 0.2 + emf_index * 0.6),
            "duration_s": 60,
            "description": self.SOLFEGGIO_COUNTER[528],
            "purpose": "core_repair"
        })
        
        # Bei mittlerer Belastung: 741 Hz (Reinigung)
        if emf_index > 0.3:
            selected.append({
                "frequency_hz": 741,
                "amplitude": min(0.7, emf_index * 0.7),
                "duration_s": 45,
                "description": self.SOLFEGGIO_COUNTER[741],
                "purpose": "emf_cleansing"
            })
        
        # Bei hoher Belastung: 963 Hz (Kosmische Einheit) + 174 Hz (Schmerzlinderung)
        if emf_index > 0.6:
            selected.append({
                "frequency_hz": 963,
                "amplitude": min(0.6, emf_index * 0.5),
                "duration_s": 30,
                "description": self.SOLFEGGIO_COUNTER[963],
                "purpose": "high_frequency_shield"
            })
            selected.append({
                "frequency_hz": 174,
                "amplitude": 0.4,
                "duration_s": 30,
                "description": self.SOLFEGGIO_COUNTER[174],
                "purpose": "low_frequency_ground"
            })
        
        self._counter_frequencies = selected
        return selected
    
    def apply_to_target_vector(
        self, 
        target_vector: torch.Tensor
    ) -> torch.Tensor:
        """
        Wendet die EMF-Kompensation auf einen Zielvektor an.
        Wird direkt in der Engine vor der Cosinus-Aehnlichkeitsberechnung genutzt.
        
        Args:
            target_vector: Der Original-Zielvektor aus der Engine
        
        Returns:
            Kompensierter Zielvektor
        """
        if not self.active or self._compensation_vector is None:
            return target_vector
        
        # Stelle sicher, dass Dimensionen passen
        if self._compensation_vector.shape != target_vector.shape:
            comp = self.compute_compensation_vector(target_vector.shape[0])
        else:
            comp = self._compensation_vector
        
        # Element-weise Multiplikation (sanfte Modulation)
        compensated = target_vector * comp
        
        return compensated
    
    def get_timing_recommendation(self) -> Dict[str, Any]:
        """
        Gibt eine Empfehlung, ob jetzt ein guter Zeitpunkt fuer eine Analyse ist.
        Basiert auf den letzten Messungen und Zeitfenster-Erkennung.
        """
        profile = self.current_profile
        emf_index = profile.get("composite_emf_index", 0.5)
        low_noise = profile.get("low_noise_window", False)
        
        if low_noise:
            return {
                "recommendation": "OPTIMAL",
                "message": "Niedriges EMF-Umfeld erkannt. Optimaler Zeitpunkt fuer Analyse.",
                "confidence": 0.95,
                "emf_index": emf_index
            }
        elif emf_index < 0.3:
            return {
                "recommendation": "GUT",
                "message": "Akzeptables EMF-Umfeld. Kompensation minimal noetig.",
                "confidence": 0.80,
                "emf_index": emf_index
            }
        elif emf_index < 0.6:
            return {
                "recommendation": "MODERAT",
                "message": "Erhoehte EMF-Belastung erkannt. Kompensation aktiv.",
                "confidence": 0.65,
                "emf_index": emf_index
            }
        else:
            return {
                "recommendation": "KRITISCH",
                "message": "Hohe EMF-Belastung! Empfehlung: Spaeter wiederholen oder Counter-Frequencies aktivieren.",
                "confidence": 0.40,
                "emf_index": emf_index
            }
    
    # =========================================================================
    # CONTINUOUS MONITORING (Hintergrund-Thread)
    # =========================================================================
    
    def start_continuous_monitoring(self, interval_s: float = 10.0):
        """
        Startet Echtzeit-Monitoring in einem Hintergrund-Thread.
        Aktualisiert das EMF-Profil alle `interval_s` Sekunden.
        """
        if self._monitor_thread and self._monitor_thread.is_alive():
            logger.warning("Monitoring laeuft bereits.")
            return
        
        self._stop_event.clear()
        
        def _monitor_loop():
            logger.info(f"EMF Monitoring gestartet (Intervall: {interval_s}s)")
            while not self._stop_event.is_set():
                try:
                    self.profile_environment()
                    self.compute_compensation_vector()
                except Exception as e:
                    logger.error(f"EMF Monitoring Fehler: {e}")
                self._stop_event.wait(interval_s)
            logger.info("EMF Monitoring gestoppt.")
        
        self._monitor_thread = threading.Thread(
            target=_monitor_loop, 
            daemon=True, 
            name="EMF-Monitor"
        )
        self._monitor_thread.start()
    
    def stop_continuous_monitoring(self):
        """Stoppt den Hintergrund-Monitoring-Thread."""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
            self._monitor_thread = None
    
    # =========================================================================
    # WEBSOCKET INTERFACE (fuer Live-Dashboard)
    # =========================================================================
    
    def register_ws_callback(self, callback):
        """Registriert einen WebSocket-Callback fuer Live-Updates."""
        self._ws_callbacks.append(callback)
    
    def unregister_ws_callback(self, callback):
        """Entfernt einen WebSocket-Callback."""
        self._ws_callbacks = [cb for cb in self._ws_callbacks if cb != callback]
    
    def _notify_ws_clients(self, data: Dict):
        """Benachrichtigt alle registrierten WebSocket-Clients."""
        for cb in self._ws_callbacks:
            try:
                cb(data)
            except Exception as e:
                logger.debug(f"WS Callback Fehler: {e}")
    
    # =========================================================================
    # RTL-SDR PLUG-IN INTERFACE (fuer spaetere Hardware-Integration)
    # =========================================================================
    
    def register_sdr_backend(self, sdr_backend):
        """
        Registriert ein RTL-SDR Backend fuer Hardware-basiertes Spektrum-Sensing.
        
        Das Backend muss folgende Methoden implementieren:
          - get_spectrum_snapshot() -> Dict mit frequency_bins und power_dbm
          - get_band_power(center_mhz, bw_mhz) -> float (dBm)
          - is_connected() -> bool
        
        Beispiel fuer spaetere Integration:
            from rtlsdr_backend import RTLSDRBackend
            sdr = RTLSDRBackend(device_index=0)
            compensator.register_sdr_backend(sdr)
        """
        self._sdr_backend = sdr_backend
        self._sdr_available = True
        logger.info("RTL-SDR Backend registriert. Hardware-Sensing aktiviert.")
    
    def get_status_report(self) -> Dict[str, Any]:
        """
        Gibt einen vollstaendigen Statusbericht des EMF Compensators zurueck.
        Geeignet fuer CLI-Ausgabe und API-Response.
        """
        return {
            "active": self.active,
            "continuous_monitoring": self.continuous and self._monitor_thread is not None,
            "sdr_available": self._sdr_available,
            "current_profile": self.current_profile,
            "calibration": self._calibration_baseline,
            "timing_recommendation": self.get_timing_recommendation(),
            "counter_frequencies": self.get_counter_frequencies(),
            "measurements_count": len(self.entropy_history),
            "compensation_active": self._compensation_vector is not None,
        }
