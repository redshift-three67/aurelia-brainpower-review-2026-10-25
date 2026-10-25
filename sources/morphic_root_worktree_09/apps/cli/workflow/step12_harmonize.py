"""Step 12: Harmonisierung - Puls/Pause-Zyklus (21s/14s) nach Radi144.

Verwendet den existierenden HarmonizationWorker als Wrapper, erweitert um
den Puls/Pause-Rhythmus und optional Audio-Synthese.
"""

from __future__ import annotations

import time

from .state import WorkflowState

_PULSE_SECONDS = 21.0
_PAUSE_SECONDS = 14.0
_TOTAL_CYCLE = _PULSE_SECONDS + _PAUSE_SECONDS


def step_12_harmonize(
    state: WorkflowState, duration_minutes: int = 1, verbose: bool = True
) -> WorkflowState:
    if verbose:
        print("  [12/12] Harmonisierung (Puls/Pause-Zyklus)...")

    total_seconds = duration_minutes * 60
    cycles = int(total_seconds / _TOTAL_CYCLE)

    if verbose:
        print(f"        Puls: {_PULSE_SECONDS}s, Pause: {_PAUSE_SECONDS}s")
        print(f"        Zyklen: {cycles} (Dauer: {duration_minutes} Min)")
        print(f"        Klienten-Frequenz: {state.client_frequency:.2f} Hz")

    try:
        from services.harmonization_worker import start_harmonization_job, list_all_jobs

        hardware_config = {
            "use_cpu": True,
            "use_ram": True,
            "use_gpu": False,
            "use_websocket": False,
        }
        job = start_harmonization_job(
            target_frequency=state.client_frequency,
            duration_minutes=duration_minutes,
            intention=state.intention,
            hardware_config=hardware_config,
        )
        state.harmonization_job_id = getattr(job, "job_id", "unknown")
        state.harmonization_active = True

        if verbose:
            print(f"        Job-ID: {state.harmonization_job_id}")
            print(f"        Status: {getattr(job, 'status', 'started')}")

        for cycle in range(cycles):
            if verbose:
                print(f"        --- Zyklus {cycle + 1}/{cycles} ---")
                print(
                    f"        Puls ({_PULSE_SECONDS}s): {state.client_frequency:.2f} Hz"
                )
            time.sleep(min(_PULSE_SECONDS, total_seconds - cycle * _TOTAL_CYCLE))
            remaining = total_seconds - (cycle + 1) * _TOTAL_CYCLE + _PAUSE_SECONDS
            if remaining > 0 and cycle < cycles - 1:
                if verbose:
                    print(f"        Pause ({_PAUSE_SECONDS}s)")
                time.sleep(min(_PAUSE_SECONDS, remaining))

        if verbose:
            print("        Harmonisierung abgeschlossen.")
    except Exception as exc:
        state.add_error(12, str(exc))
        state.harmonization_active = False
        if verbose:
            print(f"        [WARN] Harmonisierung: {exc}")
            print(f"        (Simulation: {cycles} Zyklen Puls/Pause)")

    state.mark_step(12)
    return state
