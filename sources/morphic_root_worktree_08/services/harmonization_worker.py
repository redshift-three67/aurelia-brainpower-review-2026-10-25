"""
Harmonisierungs-Worker Service für Morphic Engine V1

Ermöglicht persistente Harmonisierungen als Background-Jobs,
die auch nach Schließen der PowerShell weiterlaufen.

Features:
- Job-Management (JSON-basiert)
- Worker-Prozesse (multiprocessing)
- Hardware-Modulation (CPU, GPU, WebSocket)
- Status-Tracking
"""

import time
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import multiprocessing
import sys


# Pfade
JOBS_DIR = Path(__file__).parent.parent / "data" / "harmonization_jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class HarmonizationJob:
    """Repräsentiert einen Harmonisierungs-Job."""
    
    job_id: str
    target_frequency: float
    duration_minutes: int
    intention: str
    hardware_config: Dict[str, bool]
    
    # Status-Felder
    status: str = "pending"  # pending, running, completed, stopped, error
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    progress_percent: float = 0.0
    error_message: Optional[str] = None
    
    # Statistiken
    cycles_completed: int = 0
    total_cycles: int = 0
    
    def to_dict(self) -> Dict:
        """Konvertiert Job zu Dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HarmonizationJob':
        """Erstellt Job aus Dictionary."""
        return cls(**data)
    
    def save(self):
        """Speichert Job in JSON-Datei."""
        job_file = JOBS_DIR / f"{self.job_id}.json"
        
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, job_id: str) -> Optional['HarmonizationJob']:
        """Lädt Job aus JSON-Datei."""
        job_file = JOBS_DIR / f"{job_id}.json"
        
        if not job_file.exists():
            return None
        
        try:
            with open(job_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return cls.from_dict(data)
        except Exception as e:
            print(f"Fehler beim Laden von Job {job_id}: {e}")
            return None
    
    def delete(self):
        """Löscht Job-Datei."""
        job_file = JOBS_DIR / f"{self.job_id}.json"
        
        if job_file.exists():
            job_file.unlink()


def list_all_jobs() -> List[HarmonizationJob]:
    """
    Listet alle Jobs auf.
    
    Returns:
        Liste aller Jobs, sortiert nach Erstellungszeit
    """
    jobs = []
    
    for job_file in JOBS_DIR.glob("*.json"):
        job_id = job_file.stem
        job = HarmonizationJob.load(job_id)
        
        if job:
            jobs.append(job)
    
    # Sortiere nach Start-Zeit (neueste zuerst)
    jobs.sort(
        key=lambda j: j.start_time or "0000-00-00",
        reverse=True
    )
    
    return jobs


def get_active_jobs() -> List[HarmonizationJob]:
    """
    Gibt alle aktiven Jobs zurück.
    
    Returns:
        Liste der Jobs mit Status 'running'
    """
    all_jobs = list_all_jobs()
    return [j for j in all_jobs if j.status == "running"]


def cleanup_old_jobs(days: int = 7):
    """
    Löscht alte abgeschlossene Jobs.
    
    Args:
        days: Jobs älter als X Tage werden gelöscht
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for job in list_all_jobs():
        if job.status in ["completed", "stopped", "error"]:
            if job.end_time:
                try:
                    end_dt = datetime.fromisoformat(job.end_time)
                    if end_dt < cutoff_date:
                        job.delete()
                except:
                    pass


# ============================================================================
# HARDWARE-MODULATION
# ============================================================================

def modulate_cpu_timing(frequency: float, duration_seconds: float = 1.0):
    """
    Moduliert CPU-Timing basierend auf Ziel-Frequenz.
    
    Args:
        frequency: Ziel-Frequenz in Hz
        duration_seconds: Dauer der Modulation
    """
    if frequency <= 0:
        return
    
    # Berechne Periode (Zeit pro Zyklus)
    period = 1.0 / frequency
    
    # Anzahl der Zyklen in der Dauer
    cycles = int(duration_seconds / period)
    
    start_time = time.perf_counter()
    
    for _ in range(cycles):
        cycle_start = time.perf_counter()
        
        # Minimale CPU-Operation (um Timing-Jitter zu erzeugen)
        _ = sum(range(100))
        
        # Warte bis zum Ende der Periode
        elapsed = time.perf_counter() - cycle_start
        sleep_time = period - elapsed
        
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    actual_duration = time.perf_counter() - start_time
    actual_frequency = cycles / actual_duration if actual_duration > 0 else 0
    
    return actual_frequency


def modulate_hardware(
    frequency: float,
    intention: str,
    config: Dict[str, bool]
) -> Dict[str, float]:
    """
    Moduliert Hardware basierend auf Frequenz und Intention.
    
    Args:
        frequency: Ziel-Frequenz in Hz
        intention: Intention (healing, clearing, etc.)
        config: Hardware-Konfiguration
    
    Returns:
        Dictionary mit Modulations-Metriken
    """
    # Verwende erweiterte Hardware-Modulation
    try:
        from services.hardware_modulation import modulate_all_hardware
        
        metrics = modulate_all_hardware(
            frequency=frequency,
            intention=intention,
            config=config,
            duration_seconds=1.0
        )
        
        return metrics
    
    except ImportError:
        # Fallback: Nur CPU-Modulation
        metrics = {}
        
        if config.get("use_cpu", True):
            actual_freq = modulate_cpu_timing(frequency, duration_seconds=1.0)
            metrics["cpu_frequency"] = actual_freq
        
        return metrics


# ============================================================================
# WORKER-PROZESS
# ============================================================================

def run_harmonization_worker(job_id: str):
    """
    Worker-Prozess für Harmonisierung.
    Läuft im Hintergrund, auch nach PowerShell-Schließung.
    
    Args:
        job_id: ID des Jobs
    """
    # Lade Job
    job = HarmonizationJob.load(job_id)
    
    if not job:
        print(f"[{job_id}] Job nicht gefunden", file=sys.stderr)
        return
    
    # Setze Status auf 'running'
    job.status = "running"
    job.start_time = datetime.now().isoformat()
    job.save()
    
    print(f"[{job_id}] Harmonisierung gestartet")
    print(f"  Frequenz: {job.target_frequency} Hz")
    print(f"  Dauer: {job.duration_minutes} Minuten")
    print(f"  Intention: {job.intention}")
    
    # Berechne Gesamt-Zyklen (1 Zyklus = 1 Sekunde)
    total_seconds = job.duration_minutes * 60
    job.total_cycles = total_seconds
    job.save()
    
    end_time = time.time() + total_seconds
    
    try:
        while time.time() < end_time:
            cycle_start = time.time()
            
            # Hardware-Modulation durchführen
            metrics = modulate_hardware(
                frequency=job.target_frequency,
                intention=job.intention,
                config=job.hardware_config
            )
            
            # Aktualisiere Fortschritt
            job.cycles_completed += 1
            job.progress_percent = (job.cycles_completed / job.total_cycles) * 100
            
            # Speichere Status alle 10 Zyklen
            if job.cycles_completed % 10 == 0:
                job.save()
            
            # Warte bis zum Ende des Zyklus (1 Sekunde)
            elapsed = time.time() - cycle_start
            sleep_time = 1.0 - elapsed
            
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Job abgeschlossen
        job.status = "completed"
        job.end_time = datetime.now().isoformat()
        job.progress_percent = 100.0
        job.save()
        
        print(f"[{job_id}] Harmonisierung abgeschlossen")
        print(f"  Zyklen: {job.cycles_completed}/{job.total_cycles}")
    
    except Exception as e:
        # Fehler aufgetreten
        job.status = "error"
        job.end_time = datetime.now().isoformat()
        job.error_message = str(e)
        job.save()
        
        print(f"[{job_id}] Fehler: {e}", file=sys.stderr)


def start_harmonization_job(
    target_frequency: float,
    duration_minutes: int,
    intention: str = "harmonization",
    hardware_config: Optional[Dict[str, bool]] = None
) -> str:
    """
    Startet einen Harmonisierungs-Job im Hintergrund.
    
    Args:
        target_frequency: Ziel-Frequenz in Hz
        duration_minutes: Dauer in Minuten
        intention: Intention (healing, clearing, etc.)
        hardware_config: Hardware-Konfiguration
    
    Returns:
        Job-ID
    """
    # Generiere Job-ID
    job_id = f"harm_{uuid.uuid4().hex[:8]}"
    
    # Standard-Hardware-Config
    if hardware_config is None:
        hardware_config = {
            "use_cpu": True,
            "use_gpu": False,
            "use_ram": False,
            "use_websocket": False,
            "use_quartz": False
        }
    
    # Erstelle Job
    job = HarmonizationJob(
        job_id=job_id,
        target_frequency=target_frequency,
        duration_minutes=duration_minutes,
        intention=intention,
        hardware_config=hardware_config
    )
    
    job.save()
    
    # Starte Worker-Prozess im Hintergrund
    process = multiprocessing.Process(
        target=run_harmonization_worker,
        args=(job_id,),
        daemon=False  # Läuft weiter nach Parent-Prozess-Ende
    )
    process.start()
    
    return job_id


def stop_harmonization_job(job_id: str) -> bool:
    """
    Stoppt einen laufenden Harmonisierungs-Job.
    
    Args:
        job_id: ID des Jobs
    
    Returns:
        True wenn erfolgreich gestoppt, False sonst
    """
    job = HarmonizationJob.load(job_id)
    
    if not job:
        return False
    
    if job.status != "running":
        return False
    
    # Setze Status auf 'stopped'
    job.status = "stopped"
    job.end_time = datetime.now().isoformat()
    job.save()
    
    # TODO: Prozess tatsächlich beenden (erfordert PID-Tracking)
    # Aktuell: Worker prüft Status-Datei nicht, läuft bis Ende
    
    return True


# ============================================================================
# HELPER-FUNKTIONEN
# ============================================================================

def format_job_status(job: HarmonizationJob) -> str:
    """
    Formatiert Job-Status als Text.
    
    Args:
        job: Harmonisierungs-Job
    
    Returns:
        Formatierter Status-String
    """
    lines = []
    
    # Status-Symbol
    status_symbols = {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "stopped": "⏹️",
        "error": "❌"
    }
    
    symbol = status_symbols.get(job.status, "❓")
    
    lines.append(f"\n{symbol} Job: {job.job_id}")
    lines.append(f"   Status: {job.status}")
    lines.append(f"   Frequenz: {job.target_frequency} Hz")
    lines.append(f"   Dauer: {job.duration_minutes} Minuten")
    lines.append(f"   Intention: {job.intention}")
    
    if job.start_time:
        lines.append(f"   Gestartet: {job.start_time}")
    
    if job.status == "running":
        lines.append(f"   Fortschritt: {job.progress_percent:.1f}% ({job.cycles_completed}/{job.total_cycles} Zyklen)")
    
    if job.end_time:
        lines.append(f"   Beendet: {job.end_time}")
    
    if job.error_message:
        lines.append(f"   Fehler: {job.error_message}")
    
    # Hardware-Config
    active_hw = [k.replace("use_", "").upper() for k, v in job.hardware_config.items() if v]
    if active_hw:
        lines.append(f"   Hardware: {', '.join(active_hw)}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test
    print("Harmonisierungs-Worker Service")
    print("=" * 70)
    
    # Teste Job-Erstellung
    print("\nTest: Job erstellen...")
    job_id = start_harmonization_job(
        target_frequency=432.0,
        duration_minutes=1,  # 1 Minute für Test
        intention="healing"
    )
    
    print(f"✅ Job erstellt: {job_id}")
    
    # Warte kurz
    time.sleep(2)
    
    # Lade Job und zeige Status
    job = HarmonizationJob.load(job_id)
    if job:
        print(format_job_status(job))
    
    print("\n" + "=" * 70)
    print("Test abgeschlossen")
