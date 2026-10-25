"""
Hardware-Profile für Morphic Engine V1

Adaptive Konfiguration für verschiedene Umgebungen:
- DEV: Entwicklungsumgebung (Windows, 16GB RAM, iGPU)
- PROD: Produktionsserver (Linux, 128GB RAM, RTX 4000)

Erstellt: 01.12.2025
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import platform
import os

# ============================================================================
# HARDWARE-PROFILE DEFINITIONEN
# ============================================================================

@dataclass
class HardwareProfile:
    """Definiert Hardware-Fähigkeiten und Limits"""
    name: str
    os: str
    ram_gb: int
    gpu_name: str
    gpu_vram_gb: float
    cpu_cores: int
    cpu_threads: int
    storage_type: str
    
    # LLM-Fähigkeiten
    max_llm_params_b: float  # Max LLM Parameter in Milliarden
    llm_quantization: str     # Empfohlene Quantisierung
    llm_batch_size: int       # Batch-Größe für Inferenz
    
    # Quantum-Synergy Limits
    max_prefilter_items: int
    max_combinations: int
    grover_iterations: int
    
    # Parallelisierung
    max_workers: int
    use_gpu_acceleration: bool


# ============================================================================
# ENTWICKLUNGSUMGEBUNG (Aktuell)
# ============================================================================

DEV_PROFILE = HardwareProfile(
    name="dev_windows",
    os="Windows",
    ram_gb=16,
    gpu_name="AMD Radeon 780M (iGPU)",
    gpu_vram_gb=0.37,  # Shared Memory
    cpu_cores=8,
    cpu_threads=16,
    storage_type="NVMe SSD",
    
    # LLM: Kleine, schnelle Modelle
    max_llm_params_b=3.0,      # Max 3B Parameter
    llm_quantization="Q4_K_M",  # 4-bit Quantisierung
    llm_batch_size=1,           # Einzelne Anfragen
    
    # Quantum-Synergy: Konservative Limits
    max_prefilter_items=200,
    max_combinations=5000,
    grover_iterations=3,
    
    # Parallelisierung: Begrenzt
    max_workers=4,
    use_gpu_acceleration=False  # iGPU nicht für ML geeignet
)


# ============================================================================
# PRODUKTIONSSERVER (Zukünftig)
# ============================================================================

PROD_PROFILE = HardwareProfile(
    name="prod_linux",
    os="Linux",
    ram_gb=128,
    gpu_name="NVIDIA RTX 4000 SFF Ada",
    gpu_vram_gb=20.0,
    cpu_cores=6,
    cpu_threads=12,
    storage_type="NVMe SSD RAID",
    
    # LLM: Größere Modelle möglich
    max_llm_params_b=14.0,     # Bis 14B Parameter (Qwen2.5 14B)
    llm_quantization="Q8_0",   # 8-bit für bessere Qualität
    llm_batch_size=8,          # Parallele Anfragen
    
    # Quantum-Synergy: Erweiterte Limits
    max_prefilter_items=500,
    max_combinations=50000,
    grover_iterations=5,
    
    # Parallelisierung: Voll
    max_workers=12,
    use_gpu_acceleration=True  # CUDA für ML
)


# ============================================================================
# LLM-EMPFEHLUNGEN PRO PROFIL
# ============================================================================

LLM_RECOMMENDATIONS = {
    "dev_windows": {
        "primary": {
            "name": "Phi-3 Mini 3.8B",
            "file": "phi-3-mini-4k-instruct.Q4_K_M.gguf",
            "params_b": 3.8,
            "ram_required_gb": 4,
            "speed": "sehr schnell",
            "quality": "gut",
            "strengths": ["Allgemeinwissen", "Schnelle Inferenz", "Deutsch"],
            "download": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf"
        },
        "alternative": {
            "name": "TinyLlama 1.1B",
            "file": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "params_b": 1.1,
            "ram_required_gb": 2,
            "speed": "extrem schnell",
            "quality": "akzeptabel",
            "strengths": ["Minimaler RAM", "Schnellste Option"],
            "download": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
        },
        "medical": {
            "name": "BioMistral 7B (Q4)",
            "file": "biomistral-7b.Q4_K_M.gguf",
            "params_b": 7.0,
            "ram_required_gb": 6,
            "speed": "mittel",
            "quality": "sehr gut (medizinisch)",
            "strengths": ["Medizinisches Wissen", "PubMed-Training"],
            "download": "https://huggingface.co/BioMistral/BioMistral-7B-GGUF",
            "note": "Grenzwertig für 16GB RAM, nur wenn keine anderen Prozesse laufen"
        }
    },
    "prod_linux": {
        "primary": {
            "name": "Qwen2.5 14B",
            "file": "qwen2.5-14b-instruct.Q8_0.gguf",
            "params_b": 14.0,
            "ram_required_gb": 16,
            "gpu_vram_required_gb": 18,
            "speed": "schnell (GPU)",
            "quality": "exzellent",
            "strengths": ["Multilinguale Stärke", "Reasoning", "Deutsch"],
            "download": "https://huggingface.co/Qwen/Qwen2.5-14B-Instruct-GGUF"
        },
        "alternative": {
            "name": "Llama 3.1 8B",
            "file": "llama-3.1-8b-instruct.Q8_0.gguf",
            "params_b": 8.0,
            "ram_required_gb": 10,
            "gpu_vram_required_gb": 10,
            "speed": "sehr schnell (GPU)",
            "quality": "sehr gut",
            "strengths": ["Allrounder", "Gutes Reasoning"],
            "download": "https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct-GGUF"
        },
        "medical": {
            "name": "BioMistral 7B (Q8)",
            "file": "biomistral-7b.Q8_0.gguf",
            "params_b": 7.0,
            "ram_required_gb": 8,
            "gpu_vram_required_gb": 8,
            "speed": "schnell (GPU)",
            "quality": "exzellent (medizinisch)",
            "strengths": ["Medizinisches Wissen", "Volle Präzision"],
            "download": "https://huggingface.co/BioMistral/BioMistral-7B-GGUF"
        }
    }
}


# ============================================================================
# AUTOMATISCHE PROFIL-ERKENNUNG
# ============================================================================

def _detect_system_specs() -> Dict[str, Any]:
    """
    Erkennt die tatsächlichen Hardware-Spezifikationen des Systems.
    Funktioniert auf jedem PC.
    """
    specs = {
        "os": platform.system(),
        "os_version": platform.version(),
        "cpu_name": platform.processor() or "Unknown",
        "cpu_cores": os.cpu_count() or 4,
        "cpu_threads": os.cpu_count() or 4,
        "ram_gb": 8,  # Fallback
        "gpu_name": "Unknown",
        "gpu_vram_gb": 0.0,
        "has_nvidia": False,
        "has_amd_gpu": False,
        "storage_type": "Unknown",
    }
    
    # RAM ermitteln
    try:
        import psutil
        specs["ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)
    except ImportError:
        # Fallback für Windows ohne psutil
        try:
            import subprocess
            result = subprocess.run(
                ["wmic", "computersystem", "get", "totalphysicalmemory"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    specs["ram_gb"] = round(int(lines[1].strip()) / (1024**3), 1)
        except:
            pass
    
    # NVIDIA GPU erkennen
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(',')
            specs["gpu_name"] = parts[0].strip()
            specs["gpu_vram_gb"] = round(float(parts[1].strip()) / 1024, 1) if len(parts) > 1 else 0
            specs["has_nvidia"] = True
    except:
        pass
    
    # AMD GPU erkennen (Windows)
    if not specs["has_nvidia"] and specs["os"] == "Windows":
        try:
            import subprocess
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name,adapterram"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                output = result.stdout.lower()
                if "radeon" in output or "amd" in output:
                    specs["has_amd_gpu"] = True
                    # Extrahiere GPU-Name
                    for line in result.stdout.strip().split('\n')[1:]:
                        if "radeon" in line.lower() or "amd" in line.lower():
                            specs["gpu_name"] = line.split()[0:3]
                            specs["gpu_name"] = " ".join(line.split()[:4]).strip()
                            break
        except:
            pass
    
    return specs


def create_dynamic_profile(specs: Dict[str, Any]) -> HardwareProfile:
    """
    Erstellt ein dynamisches Hardware-Profil basierend auf erkannten Specs.
    Passt sich automatisch an jeden PC an.
    """
    ram_gb = specs["ram_gb"]
    has_nvidia = specs["has_nvidia"]
    gpu_vram = specs["gpu_vram_gb"]
    cpu_threads = specs["cpu_threads"]
    
    # Bestimme LLM-Fähigkeiten basierend auf RAM
    if ram_gb >= 64:
        max_llm_params = 14.0
        llm_quant = "Q8_0"
        llm_batch = 8
    elif ram_gb >= 32:
        max_llm_params = 7.0
        llm_quant = "Q6_K"
        llm_batch = 4
    elif ram_gb >= 16:
        max_llm_params = 3.8
        llm_quant = "Q4_K_M"
        llm_batch = 2
    elif ram_gb >= 8:
        max_llm_params = 1.1
        llm_quant = "Q4_K_M"
        llm_batch = 1
    else:
        max_llm_params = 0.5
        llm_quant = "Q4_0"
        llm_batch = 1
    
    # Bestimme Quantum-Synergy Limits
    if ram_gb >= 64:
        prefilter = 500
        max_combos = 50000
        grover_iter = 5
    elif ram_gb >= 32:
        prefilter = 350
        max_combos = 25000
        grover_iter = 4
    elif ram_gb >= 16:
        prefilter = 200
        max_combos = 10000
        grover_iter = 3
    elif ram_gb >= 8:
        prefilter = 100
        max_combos = 5000
        grover_iter = 2
    else:
        prefilter = 50
        max_combos = 2000
        grover_iter = 2
    
    # Bestimme Parallelisierung
    max_workers = max(2, min(cpu_threads - 2, 12))  # Lasse 2 Threads für System
    use_gpu = has_nvidia and gpu_vram >= 4.0
    
    return HardwareProfile(
        name="auto_detected",
        os=specs["os"],
        ram_gb=int(ram_gb),
        gpu_name=specs["gpu_name"],
        gpu_vram_gb=gpu_vram,
        cpu_cores=specs["cpu_cores"],
        cpu_threads=cpu_threads,
        storage_type=specs["storage_type"],
        max_llm_params_b=max_llm_params,
        llm_quantization=llm_quant,
        llm_batch_size=llm_batch,
        max_prefilter_items=prefilter,
        max_combinations=max_combos,
        grover_iterations=grover_iter,
        max_workers=max_workers,
        use_gpu_acceleration=use_gpu
    )


def detect_hardware_profile() -> HardwareProfile:
    """
    Erkennt automatisch das passende Hardware-Profil.
    
    Prüft zuerst auf bekannte Profile (DEV, PROD),
    erstellt sonst ein dynamisches Profil basierend auf erkannter Hardware.
    """
    specs = _detect_system_specs()
    
    current_os = specs["os"]
    ram_gb = specs["ram_gb"]
    has_nvidia = specs["has_nvidia"]
    gpu_vram = specs["gpu_vram_gb"]
    
    # Prüfe auf bekannte Konfigurationen
    
    # PROD-Server: Linux + viel RAM + NVIDIA
    if current_os == "Linux" and ram_gb >= 64 and has_nvidia and gpu_vram >= 16:
        return PROD_PROFILE
    
    # DEV-Umgebung: Windows + 16GB + AMD iGPU
    if current_os == "Windows" and 14 <= ram_gb <= 18 and specs["has_amd_gpu"]:
        if "780m" in specs["gpu_name"].lower() or "radeon" in specs["gpu_name"].lower():
            return DEV_PROFILE
    
    # Unbekannter PC: Erstelle dynamisches Profil
    return create_dynamic_profile(specs)


def get_current_profile() -> HardwareProfile:
    """Gibt das aktuelle Hardware-Profil zurück."""
    # Umgebungsvariable hat Vorrang
    profile_name = os.environ.get("ME_HARDWARE_PROFILE", "").lower()
    
    if profile_name == "prod" or profile_name == "prod_linux":
        return PROD_PROFILE
    elif profile_name == "dev" or profile_name == "dev_windows":
        return DEV_PROFILE
    elif profile_name == "auto":
        specs = _detect_system_specs()
        return create_dynamic_profile(specs)
    else:
        return detect_hardware_profile()


def get_llm_recommendation(profile: Optional[HardwareProfile] = None) -> Dict[str, Any]:
    """Gibt LLM-Empfehlung für das aktuelle Profil zurück."""
    if profile is None:
        profile = get_current_profile()
    
    # Bekannte Profile
    if profile.name in LLM_RECOMMENDATIONS:
        return LLM_RECOMMENDATIONS[profile.name]
    
    # Dynamisches Profil: Empfehlung basierend auf RAM
    ram_gb = profile.ram_gb
    
    if ram_gb >= 64:
        return {
            "primary": {
                "name": "Qwen2.5 14B (Q8)",
                "params_b": 14.0,
                "ram_required_gb": 16,
                "speed": "schnell (GPU)",
                "quality": "exzellent",
                "note": f"Optimal für {ram_gb}GB RAM"
            },
            "alternative": {
                "name": "Llama 3.1 8B",
                "params_b": 8.0,
                "ram_required_gb": 10,
                "speed": "sehr schnell",
                "quality": "sehr gut"
            }
        }
    elif ram_gb >= 32:
        return {
            "primary": {
                "name": "BioMistral 7B (Q6)",
                "params_b": 7.0,
                "ram_required_gb": 8,
                "speed": "mittel",
                "quality": "sehr gut (medizinisch)",
                "note": f"Gut für {ram_gb}GB RAM"
            },
            "alternative": {
                "name": "Mistral 7B (Q4)",
                "params_b": 7.0,
                "ram_required_gb": 6,
                "speed": "schnell",
                "quality": "gut"
            }
        }
    elif ram_gb >= 16:
        return {
            "primary": {
                "name": "Phi-3 Mini 3.8B (Q4)",
                "params_b": 3.8,
                "ram_required_gb": 4,
                "speed": "sehr schnell",
                "quality": "gut",
                "note": f"Empfohlen für {ram_gb}GB RAM"
            },
            "alternative": {
                "name": "TinyLlama 1.1B",
                "params_b": 1.1,
                "ram_required_gb": 2,
                "speed": "extrem schnell",
                "quality": "akzeptabel"
            }
        }
    elif ram_gb >= 8:
        return {
            "primary": {
                "name": "TinyLlama 1.1B (Q4)",
                "params_b": 1.1,
                "ram_required_gb": 2,
                "speed": "extrem schnell",
                "quality": "akzeptabel",
                "note": f"Einzige Option für {ram_gb}GB RAM"
            },
            "alternative": {
                "name": "Keine",
                "note": "Mehr RAM empfohlen"
            }
        }
    else:
        return {
            "primary": {
                "name": "LLM nicht empfohlen",
                "note": f"Nur {ram_gb}GB RAM - zu wenig für LLM",
                "ram_required_gb": 0,
                "speed": "-",
                "quality": "-"
            }
        }


# ============================================================================
# ADAPTIVE PARAMETER
# ============================================================================

def get_adaptive_params(profile: Optional[HardwareProfile] = None) -> Dict[str, Any]:
    """
    Gibt adaptive Parameter basierend auf Hardware zurück.
    Diese können direkt in Funktionen verwendet werden.
    """
    if profile is None:
        profile = get_current_profile()
    
    return {
        # Quantum-Synergy
        "prefilter_size": profile.max_prefilter_items,
        "max_combinations": profile.max_combinations,
        "grover_iterations": profile.grover_iterations,
        
        # Parallelisierung
        "max_workers": profile.max_workers,
        "use_gpu": profile.use_gpu_acceleration,
        
        # LLM
        "llm_max_params": profile.max_llm_params_b,
        "llm_quantization": profile.llm_quantization,
        "llm_batch_size": profile.llm_batch_size,
        
        # Speicher-Limits
        "max_items_in_memory": profile.ram_gb * 10000,  # ~10k Items pro GB
        "chunk_size": min(1000, profile.ram_gb * 100),
    }


# ============================================================================
# HARDWARE-INFO AUSGABE
# ============================================================================

def print_hardware_info(verbose: bool = False):
    """Gibt aktuelle Hardware-Informationen aus."""
    profile = get_current_profile()
    llm_rec = get_llm_recommendation(profile)
    
    # Profil-Typ bestimmen
    if profile.name == "dev_windows":
        profile_type = "ENTWICKLUNG (bekannt)"
    elif profile.name == "prod_linux":
        profile_type = "PRODUKTION (bekannt)"
    else:
        profile_type = "AUTO-ERKANNT (dynamisch)"
    
    print("=" * 70)
    print("MORPHIC ENGINE - HARDWARE-PROFIL")
    print("=" * 70)
    print(f"Profil-Typ: {profile_type}")
    print(f"Profil-ID:  {profile.name}")
    print("-" * 70)
    print(f"OS:         {profile.os}")
    print(f"RAM:        {profile.ram_gb} GB")
    print(f"GPU:        {profile.gpu_name}")
    if profile.gpu_vram_gb > 0:
        print(f"GPU VRAM:   {profile.gpu_vram_gb} GB")
    print(f"CPU:        {profile.cpu_cores} Cores / {profile.cpu_threads} Threads")
    print("-" * 70)
    
    print("LLM-EMPFEHLUNG:")
    primary = llm_rec.get('primary', {})
    print(f"  Modell:   {primary.get('name', 'Nicht verfügbar')}")
    if primary.get('ram_required_gb'):
        print(f"  RAM:      {primary.get('ram_required_gb')} GB benötigt")
    if primary.get('speed'):
        print(f"  Speed:    {primary.get('speed')}")
    if primary.get('quality'):
        print(f"  Qualität: {primary.get('quality')}")
    if primary.get('note'):
        print(f"  Hinweis:  {primary.get('note')}")
    
    alt = llm_rec.get('alternative', {})
    if alt and alt.get('name') and alt.get('name') != 'Keine':
        print(f"  Alternativ: {alt.get('name')}")
    
    print("-" * 70)
    print("QUANTUM-SYNERGY LIMITS:")
    print(f"  Pre-Filter:    {profile.max_prefilter_items} Items")
    print(f"  Kombinationen: {profile.max_combinations:,}")
    print(f"  Grover-Iter.:  {profile.grover_iterations}")
    print(f"  Max Workers:   {profile.max_workers}")
    print(f"  GPU-Accel.:    {'Ja' if profile.use_gpu_acceleration else 'Nein'}")
    print("=" * 70)
    
    if verbose:
        print("\nDETAILLIERTE SPECS:")
        specs = _detect_system_specs()
        for key, value in specs.items():
            print(f"  {key}: {value}")


def get_hardware_summary() -> str:
    """Gibt eine einzeilige Hardware-Zusammenfassung zurück."""
    profile = get_current_profile()
    return f"{profile.name} | {profile.ram_gb}GB RAM | {profile.gpu_name} | {profile.cpu_threads} Threads"


if __name__ == "__main__":
    print_hardware_info(verbose=True)
