from __future__ import annotations

from typing import Protocol


DEFAULT_HARMONIZATION_MODE = "harmonization"
HARMONIZATION_MODES: dict[str, dict[str, str]] = {
    "analysis": {
        "label": "Analysis",
        "description": "Analytische Resonanz-Beobachtung ohne starke Auslenkung.",
    },
    "regulation": {
        "label": "Regulation",
        "description": "Regulatorischer Ausgleich und Stabilisierung.",
    },
    "healing": {
        "label": "Healing",
        "description": "Heilung und Regeneration.",
    },
    "clearing": {
        "label": "Clearing",
        "description": "Klaerung und Reinigung.",
    },
    "protection": {
        "label": "Protection",
        "description": "Schutz und Abschirmung.",
    },
    "transformation": {
        "label": "Transformation",
        "description": "Wandel und Neuordnung.",
    },
    "harmonization": {
        "label": "Harmonization",
        "description": "Balance und Ausgleich.",
    },
    "activation": {
        "label": "Activation",
        "description": "Aktivierung und Energie.",
    },
}


def normalize_harmonization_mode(value: str | None) -> str:
    cleaned = str(value or "").strip().lower()
    if cleaned in HARMONIZATION_MODES:
        return cleaned
    return DEFAULT_HARMONIZATION_MODE


def resolve_harmonization_intention(*, mode: str | None, intention: str | None) -> str:
    cleaned = str(intention or "").strip().lower()
    if cleaned:
        return cleaned
    return normalize_harmonization_mode(mode)


def harmonization_phase(status: str | None) -> str:
    status_value = str(status or "pending").strip().lower()
    return {
        "pending": "preparing",
        "running": "harmonizing",
        "completed": "completed",
        "stopped": "stopped",
        "error": "error",
    }.get(status_value, status_value or "preparing")


class HarmonizationJobStore(Protocol):
    def start(
        self,
        *,
        mode: str,
        target_frequency: float,
        duration_minutes: int,
        intention: str,
        hardware_config: dict[str, bool],
    ) -> dict[str, object]: ...

    def get(self, job_id: str) -> dict[str, object]: ...

    def stop(self, job_id: str) -> dict[str, object]: ...


class WorkerHarmonizationService:
    def start(
        self,
        *,
        mode: str,
        target_frequency: float,
        duration_minutes: int,
        intention: str,
        hardware_config: dict[str, bool],
    ) -> dict[str, object]:
        from services import harmonization_worker as worker

        job_id = worker.start_harmonization_job(
            target_frequency=target_frequency,
            duration_minutes=duration_minutes,
            intention=intention,
            hardware_config=hardware_config,
        )
        job = worker.HarmonizationJob.load(job_id)
        if job is None:
            return {
                "job_id": job_id,
                "status": "pending",
                "mode": normalize_harmonization_mode(mode),
                "phase": harmonization_phase("pending"),
                "target_frequency": target_frequency,
                "duration_minutes": duration_minutes,
                "intention": intention,
                "hardware_config": hardware_config,
                "progress_percent": 0.0,
                "cycles_completed": 0,
                "total_cycles": duration_minutes * 60,
            }
        return self._snapshot(job)

    def get(self, job_id: str) -> dict[str, object]:
        from services import harmonization_worker as worker

        job = worker.HarmonizationJob.load(job_id)
        if job is None:
            raise KeyError(job_id)
        return self._snapshot(job)

    def stop(self, job_id: str) -> dict[str, object]:
        from services import harmonization_worker as worker

        stopped = worker.stop_harmonization_job(job_id)
        job = worker.HarmonizationJob.load(job_id)
        if job is None:
            raise KeyError(job_id)
        if not stopped and job.status == "running":
            return self._snapshot(job)
        return self._snapshot(job)

    def _snapshot(self, job: object) -> dict[str, object]:
        intention = str(getattr(job, "intention", DEFAULT_HARMONIZATION_MODE))
        status = str(getattr(job, "status", "pending"))
        normalized_intention = normalize_harmonization_mode(intention)
        return {
            "job_id": getattr(job, "job_id"),
            "status": status,
            "mode": normalized_intention,
            "intention": normalized_intention,
            "phase": harmonization_phase(status),
            "target_frequency": getattr(job, "target_frequency"),
            "duration_minutes": getattr(job, "duration_minutes"),
            "hardware_config": getattr(job, "hardware_config"),
            "start_time": getattr(job, "start_time"),
            "end_time": getattr(job, "end_time"),
            "progress_percent": getattr(job, "progress_percent"),
            "cycles_completed": getattr(job, "cycles_completed"),
            "total_cycles": getattr(job, "total_cycles"),
            "error_message": getattr(job, "error_message"),
        }
