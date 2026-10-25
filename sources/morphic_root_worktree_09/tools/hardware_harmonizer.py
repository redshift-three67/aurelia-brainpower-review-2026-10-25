"""Hardware-Harmonisierungs-Tool fuer die CLI- und PowerShell-Anbindung.

Kapselt die HarmonizationEngine und den HarmonizationWorker, um eine
Hardware-Modulation (CPU/GPU/RAM) mit einer Zielfrequenz und Dauer zu starten.

Verwendung:
    python -m tools.hardware_harmonizer --frequency 432 --duration 5 --mode balanced
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Startet eine Hardware-Harmonisierung (CPU/GPU/RAM-Modulation)."
    )
    parser.add_argument(
        "--frequency",
        type=float,
        default=432.0,
        help="Zielfrequenz in Hz (Standard: 432)",
    )
    parser.add_argument(
        "--duration", type=int, default=5, help="Dauer in Minuten (Standard: 5)"
    )
    parser.add_argument(
        "--mode",
        default="balanced",
        choices=["gentle", "balanced", "intense"],
        help="Modus: gentle (nur CPU), balanced (CPU+RAM), intense (CPU+GPU+RAM)",
    )
    parser.add_argument(
        "--intention",
        default="harmonization",
        help="Intention (Standard: harmonization)",
    )
    args = parser.parse_args()

    hardware_config = {
        "use_cpu": True,
        "use_ram": True,
        "use_gpu": False,
        "use_websocket": False,
    }
    if args.mode == "gentle":
        hardware_config = {
            "use_cpu": True,
            "use_ram": False,
            "use_gpu": False,
            "use_websocket": False,
        }
    elif args.mode == "intense":
        hardware_config = {
            "use_cpu": True,
            "use_ram": True,
            "use_gpu": True,
            "use_websocket": False,
        }

    try:
        from services.harmonization_worker import (
            start_harmonization_job,
            list_all_jobs,
            stop_harmonization_job,
        )
    except Exception as exc:
        print(f"Fehler: HarmonizationWorker nicht verfuegbar: {exc}", file=sys.stderr)
        return 1

    print(
        f"Starte Hardware-Harmonisierung ({args.mode}): {args.frequency} Hz, {args.duration} Min"
    )
    print(
        f"  Hardware: CPU={hardware_config['use_cpu']}, GPU={hardware_config['use_gpu']}, RAM={hardware_config['use_ram']}"
    )
    print(f"  Intention: {args.intention}")

    try:
        job = start_harmonization_job(
            target_frequency=args.frequency,
            duration_minutes=args.duration,
            intention=args.intention,
            hardware_config=hardware_config,
        )
    except Exception as exc:
        print(f"Fehler beim Starten des Harmonisierungs-Jobs: {exc}", file=sys.stderr)
        return 1

    job_id = getattr(job, "job_id", "unknown")
    print(f"  Job-ID: {job_id}")
    print(f"  Status: {getattr(job, 'status', 'started')}")

    # Auf Abschluss warten (max duration+2 Minuten)
    max_wait = (args.duration + 2) * 60
    waited = 0
    while waited < max_wait:
        time.sleep(10)
        waited += 10
        try:
            jobs = list_all_jobs()
            current = next(
                (j for j in jobs if getattr(j, "job_id", "") == job_id), None
            )
            if current is None:
                print("  Job nicht mehr aktiv (beendet).")
                break
            status = getattr(current, "status", "unknown")
            progress = getattr(current, "progress_percent", 0)
            cycles = getattr(current, "cycles_completed", 0)
            print(
                f"  [{waited // 60:02d}:{waited % 60:02d}] Status={status}, Progress={progress:.0f}%, Zyklen={cycles}"
            )
            if status in ("completed", "stopped", "error"):
                print(f"  Job beendet: {status}")
                break
        except Exception:
            pass

    print("Hardware-Harmonisierung abgeschlossen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
