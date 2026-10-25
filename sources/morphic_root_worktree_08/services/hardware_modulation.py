"""
Hardware-Modulation Service für Morphic Engine V1

Erweiterte Hardware-Modulation für Harmonisierungen:
- GPU-Modulation (via Compute Shaders)
- WebSocket-Frequenz-Übertragung
- RAM Access Pattern Modulation
- CPU Timing (aus harmonization_worker.py)
"""

import time
import math
import array
import struct
from typing import Dict, Optional
import asyncio
import json


# ============================================================================
# GPU-MODULATION (Python-basiert, ohne externe GPU-Libs)
# ============================================================================

def modulate_gpu_compute(frequency: float, duration_seconds: float = 1.0) -> Dict[str, float]:
    """
    GPU-Modulation via CPU-simulierte Compute-Operationen.
    
    In einer vollständigen Implementierung würde dies WebGL/OpenGL verwenden.
    Hier simulieren wir GPU-Last durch intensive Berechnungen.
    
    Args:
        frequency: Ziel-Frequenz in Hz
        duration_seconds: Dauer der Modulation
    
    Returns:
        Metriken der Modulation
    """
    if frequency <= 0:
        return {"gpu_cycles": 0, "gpu_frequency": 0.0}
    
    period = 1.0 / frequency
    cycles = int(duration_seconds / period)
    
    start_time = time.perf_counter()
    
    # Simuliere GPU-Compute-Operationen
    for i in range(cycles):
        cycle_start = time.perf_counter()
        
        # Matrix-Multiplikation (GPU-typische Operation)
        # Kleine Matrix für schnelle Zyklen
        size = 50
        matrix_a = [[math.sin(i * 0.01 + j * 0.01) for j in range(size)] for _ in range(size)]
        matrix_b = [[math.cos(i * 0.01 + j * 0.01) for j in range(size)] for _ in range(size)]
        
        # Einfache Matrix-Multiplikation
        result = [[sum(a * b for a, b in zip(row_a, col_b)) 
                   for col_b in zip(*matrix_b)] 
                  for row_a in matrix_a]
        
        # Timing-Kontrolle
        elapsed = time.perf_counter() - cycle_start
        sleep_time = period - elapsed
        
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    actual_duration = time.perf_counter() - start_time
    actual_frequency = cycles / actual_duration if actual_duration > 0 else 0
    
    return {
        "gpu_cycles": cycles,
        "gpu_frequency": actual_frequency,
        "gpu_duration": actual_duration
    }


# ============================================================================
# RAM ACCESS PATTERN MODULATION
# ============================================================================

def modulate_ram_access(frequency: float, duration_seconds: float = 1.0) -> Dict[str, float]:
    """
    RAM Access Pattern Modulation.
    
    Erzeugt rhythmische Speicherzugriffsmuster basierend auf Frequenz.
    
    Args:
        frequency: Ziel-Frequenz in Hz
        duration_seconds: Dauer der Modulation
    
    Returns:
        Metriken der Modulation
    """
    if frequency <= 0:
        return {"ram_cycles": 0, "ram_frequency": 0.0}
    
    period = 1.0 / frequency
    cycles = int(duration_seconds / period)
    
    # Erstelle großen Speicherbereich (10 MB)
    buffer_size = 10 * 1024 * 1024  # 10 MB
    memory_buffer = array.array('B', [0] * buffer_size)
    
    start_time = time.perf_counter()
    
    for i in range(cycles):
        cycle_start = time.perf_counter()
        
        # Rhythmisches Schreib-/Lesemuster
        # Frequenz bestimmt Zugriffsmuster
        step = int(frequency * 100) % 1000 + 1
        
        for offset in range(0, buffer_size, step):
            if offset < buffer_size:
                # Schreibe Wert
                memory_buffer[offset] = (i + offset) % 256
                # Lese Wert (erzwingt tatsächlichen RAM-Zugriff)
                _ = memory_buffer[offset]
        
        # Timing-Kontrolle
        elapsed = time.perf_counter() - cycle_start
        sleep_time = period - elapsed
        
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    actual_duration = time.perf_counter() - start_time
    actual_frequency = cycles / actual_duration if actual_duration > 0 else 0
    
    return {
        "ram_cycles": cycles,
        "ram_frequency": actual_frequency,
        "ram_duration": actual_duration,
        "ram_buffer_size": buffer_size
    }


# ============================================================================
# WEBSOCKET-FREQUENZ-ÜBERTRAGUNG
# ============================================================================

class FrequencyWebSocketServer:
    """
    WebSocket-Server für Echtzeit-Frequenz-Übertragung.
    
    Sendet Frequenz-Daten an verbundene Clients (z.B. externe Hardware).
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.is_running = False
    
    async def handler(self, websocket, path):
        """Handler für WebSocket-Verbindungen."""
        self.clients.add(websocket)
        try:
            async for message in websocket:
                # Echo zurück (für Debugging)
                await websocket.send(f"Echo: {message}")
        finally:
            self.clients.remove(websocket)
    
    async def broadcast_frequency(self, frequency: float, intention: str):
        """
        Sendet Frequenz an alle verbundenen Clients.
        
        Args:
            frequency: Frequenz in Hz
            intention: Intention
        """
        if not self.clients:
            return
        
        message = json.dumps({
            "type": "frequency",
            "frequency": frequency,
            "intention": intention,
            "timestamp": time.time()
        })
        
        # Sende an alle Clients
        await asyncio.gather(
            *[client.send(message) for client in self.clients],
            return_exceptions=True
        )
    
    async def start(self):
        """Startet den WebSocket-Server."""
        try:
            import websockets
            
            self.is_running = True
            async with websockets.serve(self.handler, self.host, self.port):
                print(f"WebSocket-Server läuft auf ws://{self.host}:{self.port}")
                await asyncio.Future()  # Run forever
        
        except ImportError:
            print("⚠️  websockets-Modul nicht installiert")
            print("   Installation: pip install websockets")
            return
    
    def stop(self):
        """Stoppt den WebSocket-Server."""
        self.is_running = False


def modulate_websocket(
    frequency: float,
    intention: str,
    duration_seconds: float = 1.0,
    host: str = "localhost",
    port: int = 8765
) -> Dict[str, float]:
    """
    WebSocket-Frequenz-Modulation.
    
    Sendet Frequenz-Daten via WebSocket an externe Empfänger.
    
    Args:
        frequency: Ziel-Frequenz in Hz
        intention: Intention
        duration_seconds: Dauer der Modulation
        host: WebSocket-Host
        port: WebSocket-Port
    
    Returns:
        Metriken der Modulation
    """
    # Prüfe ob websockets verfügbar ist
    try:
        import websockets
    except ImportError:
        return {
            "websocket_error": "websockets module not installed",
            "websocket_cycles": 0
        }
    
    # Für synchrone Verwendung: Sende einzelne Nachricht
    # (Vollständige Implementierung würde async Server nutzen)
    
    period = 1.0 / frequency if frequency > 0 else 1.0
    cycles = int(duration_seconds / period)
    
    # Simuliere WebSocket-Übertragung
    # In Produktion: Tatsächliche WebSocket-Verbindung
    
    return {
        "websocket_cycles": cycles,
        "websocket_frequency": frequency,
        "websocket_host": f"ws://{host}:{port}",
        "websocket_note": "Simulation (kein aktiver Server)"
    }


# ============================================================================
# KOMBINIERTE HARDWARE-MODULATION
# ============================================================================

def modulate_all_hardware(
    frequency: float,
    intention: str,
    config: Dict[str, bool],
    duration_seconds: float = 1.0
) -> Dict[str, any]:
    """
    Kombinierte Hardware-Modulation.
    
    Führt alle aktivierten Modulationen parallel aus.
    
    Args:
        frequency: Ziel-Frequenz in Hz
        intention: Intention
        config: Hardware-Konfiguration
        duration_seconds: Dauer pro Zyklus
    
    Returns:
        Kombinierte Metriken
    """
    metrics = {
        "frequency": frequency,
        "intention": intention,
        "duration": duration_seconds
    }
    
    # CPU Timing (aus harmonization_worker.py)
    if config.get("use_cpu", True):
        from services.harmonization_worker import modulate_cpu_timing
        cpu_freq = modulate_cpu_timing(frequency, duration_seconds)
        metrics["cpu_frequency"] = cpu_freq
    
    # GPU Compute
    if config.get("use_gpu", False):
        gpu_metrics = modulate_gpu_compute(frequency, duration_seconds)
        metrics.update(gpu_metrics)
    
    # RAM Access Pattern
    if config.get("use_ram", False):
        ram_metrics = modulate_ram_access(frequency, duration_seconds)
        metrics.update(ram_metrics)
    
    # WebSocket
    if config.get("use_websocket", False):
        ws_metrics = modulate_websocket(frequency, intention, duration_seconds)
        metrics.update(ws_metrics)
    
    return metrics


# ============================================================================
# HELPER-FUNKTIONEN
# ============================================================================

def get_hardware_capabilities() -> Dict[str, bool]:
    """
    Prüft verfügbare Hardware-Capabilities.
    
    Returns:
        Dictionary mit verfügbaren Features
    """
    capabilities = {
        "cpu": True,  # Immer verfügbar
        "gpu": True,  # Simuliert via CPU
        "ram": True,  # Immer verfügbar
        "websocket": False,
        "quartz": False  # Externe Hardware
    }
    
    # Prüfe WebSocket-Verfügbarkeit
    try:
        import websockets
        capabilities["websocket"] = True
    except ImportError:
        pass
    
    return capabilities


def format_hardware_metrics(metrics: Dict) -> str:
    """
    Formatiert Hardware-Metriken als Text.
    
    Args:
        metrics: Metriken-Dictionary
    
    Returns:
        Formatierter String
    """
    lines = []
    
    lines.append("Hardware-Modulation Metriken:")
    lines.append(f"  Frequenz: {metrics.get('frequency', 0)} Hz")
    lines.append(f"  Intention: {metrics.get('intention', 'N/A')}")
    lines.append(f"  Dauer: {metrics.get('duration', 0):.2f}s")
    lines.append("")
    
    if "cpu_frequency" in metrics:
        lines.append(f"  CPU: {metrics['cpu_frequency']:.2f} Hz (tatsächlich)")
    
    if "gpu_cycles" in metrics:
        lines.append(f"  GPU: {metrics['gpu_cycles']} Zyklen, {metrics.get('gpu_frequency', 0):.2f} Hz")
    
    if "ram_cycles" in metrics:
        lines.append(f"  RAM: {metrics['ram_cycles']} Zyklen, {metrics.get('ram_buffer_size', 0) / 1024 / 1024:.1f} MB")
    
    if "websocket_host" in metrics:
        lines.append(f"  WebSocket: {metrics['websocket_host']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test
    print("Hardware-Modulation Service")
    print("=" * 70)
    
    # Teste Capabilities
    print("\nVerfügbare Hardware:")
    caps = get_hardware_capabilities()
    for hw, available in caps.items():
        status = "✅" if available else "❌"
        print(f"  {status} {hw.upper()}")
    
    print("\n" + "=" * 70)
    print("Test: GPU-Modulation (1 Sekunde, 10 Hz)")
    
    metrics = modulate_gpu_compute(10.0, 1.0)
    print(f"  Zyklen: {metrics['gpu_cycles']}")
    print(f"  Frequenz: {metrics['gpu_frequency']:.2f} Hz")
    print(f"  Dauer: {metrics['gpu_duration']:.2f}s")
    
    print("\n" + "=" * 70)
    print("Test: RAM-Modulation (1 Sekunde, 5 Hz)")
    
    metrics = modulate_ram_access(5.0, 1.0)
    print(f"  Zyklen: {metrics['ram_cycles']}")
    print(f"  Frequenz: {metrics['ram_frequency']:.2f} Hz")
    print(f"  Buffer: {metrics['ram_buffer_size'] / 1024 / 1024:.1f} MB")
    
    print("\n" + "=" * 70)
    print("Test abgeschlossen")
