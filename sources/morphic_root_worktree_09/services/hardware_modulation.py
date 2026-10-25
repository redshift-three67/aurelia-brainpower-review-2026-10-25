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
import multiprocessing
import queue
import sys
from typing import Any, Callable, Dict, Optional
import asyncio
import json


class HardwareModulationOverrunError(RuntimeError):
    """Raised when a hardware path ignores the shared pulse deadline."""

    def __init__(self, message: str, *, terminated_pids: list[int] | None = None) -> None:
        super().__init__(message)
        self.terminated_pids = list(terminated_pids or [])


HARDWARE_FUTURE_GRACE_SECONDS = 0.2


# ============================================================================
# GPU-MODULATION (Python-basiert, ohne externe GPU-Libs)
# ============================================================================

def modulate_gpu_compute(
    frequency: float, duration_seconds: float = 1.0, should_continue=None
) -> Dict[str, float]:
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
    completed_cycles = 0
    for i in range(cycles):
        if should_continue is not None and not should_continue():
            break
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
        
        while sleep_time > 0:
            if should_continue is not None and not should_continue():
                break
            chunk = min(0.05, sleep_time)
            time.sleep(chunk)
            sleep_time -= chunk
        else:
            completed_cycles += 1

    actual_duration = time.perf_counter() - start_time
    actual_frequency = completed_cycles / actual_duration if actual_duration > 0 else 0

    return {
        "gpu_cycles": completed_cycles,
        "gpu_frequency": actual_frequency,
        "gpu_duration": actual_duration
    }


# ============================================================================
# RAM ACCESS PATTERN MODULATION
# ============================================================================

def modulate_ram_access(
    frequency: float, duration_seconds: float = 1.0, should_continue=None
) -> Dict[str, float]:
    """Run cancellable RAM access-pattern modulation."""
    if frequency <= 0:
        return {"ram_cycles": 0, "ram_frequency": 0.0}

    period = 1.0 / frequency
    cycles = int(duration_seconds / period)
    buffer_size = 10 * 1024 * 1024
    memory_buffer = array.array("B", [0] * buffer_size)
    start_time = time.perf_counter()
    completed_cycles = 0

    for i in range(cycles):
        if should_continue is not None and not should_continue():
            break
        cycle_start = time.perf_counter()
        step = int(frequency * 100) % 1000 + 1
        interrupted = False
        for item_index, offset in enumerate(range(0, buffer_size, step)):
            if (
                item_index % 1024 == 0
                and should_continue is not None
                and not should_continue()
            ):
                interrupted = True
                break
            memory_buffer[offset] = (i + offset) % 256
            _ = memory_buffer[offset]
        if interrupted:
            break

        sleep_time = period - (time.perf_counter() - cycle_start)
        while sleep_time > 0:
            if should_continue is not None and not should_continue():
                interrupted = True
                break
            chunk = min(0.05, sleep_time)
            time.sleep(chunk)
            sleep_time -= chunk
        if interrupted:
            break
        completed_cycles += 1

    actual_duration = time.perf_counter() - start_time
    actual_frequency = completed_cycles / actual_duration if actual_duration > 0 else 0
    return {
        "ram_cycles": completed_cycles,
        "ram_frequency": actual_frequency,
        "ram_duration": actual_duration,
        "ram_buffer_size": buffer_size,
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
    port: int = 8765,
    should_continue=None,
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
    if should_continue is not None and not should_continue():
        return {"websocket_cycles": 0, "websocket_frequency": frequency}

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


def _task_process_entry(
    name: str,
    function: Callable[..., Dict[str, Any]],
    args: tuple[Any, ...],
    stop_event,
    pulse_event,
    result_queue,
) -> None:
    result_queue.put(("started", name, None))
    pulse_event.wait()
    try:
        result_queue.put(("result", name, function(*args, stop_event)))
    except BaseException as exc:
        result_queue.put(("error", name, f"{type(exc).__name__}: {exc}"))


def _converge_started_processes(
    processes,
    stop_event,
    pulse_event,
    result_queue=None,
) -> None:
    primary_error = sys.exception()
    cleanup_errors: list[BaseException] = []

    def attempt(operation):
        try:
            return operation()
        except BaseException as exc:
            cleanup_errors.append(exc)
            return None

    attempt(stop_event.clear)
    attempt(pulse_event.set)
    grace_deadline = time.monotonic() + HARDWARE_FUTURE_GRACE_SECONDS
    for process in processes:
        attempt(lambda process=process: process.join(
            timeout=max(0.0, grace_deadline - time.monotonic())
        ))

    def alive(process) -> bool:
        try:
            return bool(process.is_alive())
        except BaseException as exc:
            cleanup_errors.append(exc)
            return True

    survivors = [process for process in processes if alive(process)]
    for process in survivors:
        attempt(process.terminate)
    for process in survivors:
        attempt(lambda process=process: process.join(timeout=1))
        if alive(process):
            attempt(process.kill)
            attempt(lambda process=process: process.join(timeout=1))
    remaining = [process for process in processes if alive(process)]
    if remaining:
        cleanup_errors.append(
            HardwareModulationOverrunError(
                "hardware modulation processes survived final convergence",
                terminated_pids=[
                    process.pid for process in remaining if getattr(process, "pid", None)
                ],
            )
        )
    for process in processes:
        close = getattr(process, "close", None)
        if close is not None:
            attempt(close)
    if result_queue is not None:
        close_queue = getattr(result_queue, "close", None)
        if close_queue is not None:
            attempt(close_queue)
        join_thread = getattr(result_queue, "join_thread", None)
        if join_thread is not None:
            attempt(join_thread)
    if cleanup_errors:
        errors = ([primary_error] if primary_error is not None else []) + cleanup_errors
        raise BaseExceptionGroup("hardware operation and cleanup failed", errors)


def _run_killable_tasks(
    tasks: dict[str, tuple[Callable[..., Dict[str, Any]], tuple[Any, ...]]],
    *,
    duration_seconds: float,
    should_continue=None,
) -> Dict[str, Any]:
    context = multiprocessing.get_context("spawn")
    stop_event = context.Event()
    pulse_event = context.Event()
    stop_event.set()
    result_queue = context.Queue()
    processes = {
        name: context.Process(
            target=_task_process_entry,
            args=(name, function, args, stop_event, pulse_event, result_queue),
            daemon=False,
        )
        for name, (function, args) in tasks.items()
    }
    started_processes = []
    try:
        for process in processes.values():
            process.start()
            started_processes.append(process)

        messages: list[tuple[str, str, Any]] = []
        started_names: set[str] = set()
        startup_deadline = time.monotonic() + 5.0
        while len(started_names) < len(processes) and time.monotonic() < startup_deadline:
            try:
                message = result_queue.get(timeout=0.05)
            except queue.Empty:
                if any(process.exitcode not in {None, 0} for process in started_processes):
                    break
                continue
            messages.append(message)
            if message[0] == "started":
                started_names.add(message[1])

        if len(started_names) != len(processes):
            raise HardwareModulationOverrunError(
                "hardware modulation processes did not reach the shared pulse boundary",
                terminated_pids=[process.pid for process in started_processes if process.pid],
            )

        pulse_event.set()
        pulse_deadline = time.monotonic() + max(0.0, duration_seconds)
        while time.monotonic() < pulse_deadline:
            if should_continue is not None and not should_continue():
                break
            if all(not process.is_alive() for process in started_processes):
                break
            time.sleep(0.005)
        stop_event.clear()

        grace_deadline = time.monotonic() + HARDWARE_FUTURE_GRACE_SECONDS
        for process in started_processes:
            process.join(timeout=max(0.0, grace_deadline - time.monotonic()))
        survivors = [process for process in started_processes if process.is_alive()]
        if survivors:
            raise HardwareModulationOverrunError(
                "hardware modulation processes did not converge after pulse deadline",
                terminated_pids=[process.pid for process in survivors if process.pid],
            )

        while True:
            try:
                messages.append(result_queue.get_nowait())
            except queue.Empty:
                break
        results: Dict[str, Any] = {}
        errors = []
        for kind, name, payload in messages:
            if kind == "result":
                results.update(payload)
            elif kind == "error":
                errors.append(f"{name}: {payload}")
        if errors:
            raise RuntimeError("; ".join(errors))
        return results
    finally:
        _converge_started_processes(
            started_processes,
            stop_event,
            pulse_event,
            result_queue,
        )


def _cpu_process_task(frequency: float, duration_seconds: float, stop_event) -> Dict[str, Any]:
    from services.harmonization_worker import modulate_cpu_timing

    return {
        "cpu_frequency": modulate_cpu_timing(
            frequency,
            duration_seconds,
            stop_event.is_set,
        )
    }


def _gpu_process_task(frequency: float, duration_seconds: float, stop_event) -> Dict[str, Any]:
    return modulate_gpu_compute(frequency, duration_seconds, stop_event.is_set)


def _ram_process_task(frequency: float, duration_seconds: float, stop_event) -> Dict[str, Any]:
    return modulate_ram_access(frequency, duration_seconds, stop_event.is_set)


def _websocket_process_task(
    frequency: float,
    intention: str,
    duration_seconds: float,
    stop_event,
) -> Dict[str, Any]:
    return modulate_websocket(
        frequency,
        intention,
        duration_seconds,
        should_continue=stop_event.is_set,
    )


def modulate_all_hardware(
    frequency: float,
    intention: str,
    config: Dict[str, bool],
    duration_seconds: float = 1.0,
    should_continue=None,
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
        "duration": duration_seconds,
    }
    tasks: dict[str, tuple[Callable[..., Dict[str, Any]], tuple[Any, ...]]] = {}
    if config.get("use_cpu", True):
        tasks["cpu"] = (_cpu_process_task, (frequency, duration_seconds))
    if config.get("use_gpu", False):
        tasks["gpu"] = (_gpu_process_task, (frequency, duration_seconds))
    if config.get("use_ram", False):
        tasks["ram"] = (_ram_process_task, (frequency, duration_seconds))
    if config.get("use_websocket", False):
        tasks["websocket"] = (
            _websocket_process_task,
            (frequency, intention, duration_seconds),
        )

    if not tasks:
        return metrics
    metrics.update(
        _run_killable_tasks(
            tasks,
            duration_seconds=duration_seconds,
            should_continue=should_continue,
        )
    )
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
