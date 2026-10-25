from __future__ import annotations

from typing import Protocol

from apps.web.authority_ids import (
    validate_authority_id,
    validate_harmonization_job_id_for_creation,
)


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


class HarmonizationReplayOwnershipError(RuntimeError):
    pass


class HarmonizationOwnershipError(RuntimeError):
    pass


class HarmonizationReplayIdentityError(RuntimeError):
    pass


class HarmonizationReplayAuthorityError(RuntimeError):
    pass


def normalize_harmonization_mode(value: str | None) -> str:
    from services.harmonization_worker import normalize_harmonization_intention

    return normalize_harmonization_intention(value)


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
        hardware_config: dict[str, object],
        pulse_seconds: float = 3.0,
        pause_seconds: float = 2.0,
        duration_factor: int = 1,
        solfeggio_base: float = 432.0,
        report_id: str = "",
        workbench_mode: str = "standard",
        tenant_id: str = "",
        operator_id: str = "",
        job_id: str | None = None,
    ) -> dict[str, object]: ...

    def get(self, job_id: str) -> dict[str, object]: ...

    def get_owned(
        self,
        job_id: str,
        *,
        tenant_id: str,
        operator_id: str,
    ) -> dict[str, object]: ...

    def get_for_replay(
        self,
        job_id: str,
        *,
        mode: str,
        target_frequency: float,
        duration_minutes: int,
        intention: str,
        hardware_config: dict[str, object],
        pulse_seconds: float,
        pause_seconds: float,
        duration_factor: int,
        solfeggio_base: float,
        report_id: str,
        workbench_mode: str,
        tenant_id: str,
        operator_id: str,
    ) -> dict[str, object]: ...

    def stop(self, job_id: str) -> dict[str, object]: ...

    def stop_owned(
        self,
        job_id: str,
        *,
        tenant_id: str,
        operator_id: str,
    ) -> dict[str, object]: ...


class WorkerHarmonizationService:
    def recover_interrupted_jobs(self) -> list[str]:
        from services import harmonization_worker as worker

        return worker.recover_interrupted_harmonization_jobs()

    def start(
        self,
        *,
        mode: str,
        target_frequency: float,
        duration_minutes: int,
        intention: str,
        hardware_config: dict[str, object],
        pulse_seconds: float = 3.0,
        pause_seconds: float = 2.0,
        duration_factor: int = 1,
        solfeggio_base: float = 432.0,
        report_id: str = "",
        workbench_mode: str = "standard",
        tenant_id: str = "",
        operator_id: str = "",
        job_id: str | None = None,
    ) -> dict[str, object]:
        if job_id is not None:
            job_id = validate_harmonization_job_id_for_creation(job_id)
        from services import harmonization_worker as worker

        job_id = worker.start_harmonization_job(
            target_frequency=target_frequency,
            duration_minutes=duration_minutes,
            intention=intention,
            hardware_config=hardware_config,
            pulse_seconds=pulse_seconds,
            pause_seconds=pause_seconds,
            duration_factor=duration_factor,
            solfeggio_base=solfeggio_base,
            report_id=report_id,
            workbench_mode=workbench_mode,
            tenant_id=tenant_id,
            operator_id=operator_id,
            job_id=job_id,
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
                "pulse_seconds": pulse_seconds,
                "pause_seconds": pause_seconds,
                "duration_factor": duration_factor,
                "solfeggio_base": solfeggio_base,
                "report_id": report_id,
                "workbench_mode": workbench_mode,
                "tenant_id": tenant_id,
                "operator_id": operator_id,
                "progress_percent": 0.0,
                "cycles_completed": 0,
                "total_cycles": int(duration_factor * 21 * 60 / (pulse_seconds + pause_seconds)),
            }
        return self._snapshot(job)

    def get_for_replay(
        self,
        job_id: str,
        *,
        mode: str,
        target_frequency: float,
        duration_minutes: int,
        intention: str,
        hardware_config: dict[str, object],
        pulse_seconds: float,
        pause_seconds: float,
        duration_factor: int,
        solfeggio_base: float,
        report_id: str,
        workbench_mode: str,
        tenant_id: str,
        operator_id: str,
    ) -> dict[str, object]:
        job_id = validate_authority_id(job_id)
        from services import harmonization_worker as worker

        if normalize_harmonization_mode(mode) != normalize_harmonization_mode(
            intention
        ):
            raise HarmonizationReplayIdentityError(
                "harmonization replay identity mismatch"
            )
        try:
            current, _, validated_status_phase = worker.reconcile_harmonization_start(
                job_id,
                target_frequency=target_frequency,
                duration_minutes=duration_minutes,
                intention=intention,
                hardware_config=dict(hardware_config),
                pulse_seconds=pulse_seconds,
                pause_seconds=pause_seconds,
                duration_factor=duration_factor,
                solfeggio_base=solfeggio_base,
                report_id=report_id,
                workbench_mode=workbench_mode,
                tenant_id=tenant_id,
                operator_id=operator_id,
            )
        except worker.HarmonizationStartOwnershipError as exc:
            raise HarmonizationReplayOwnershipError(
                "harmonization replay owner identity mismatch"
            ) from exc
        except worker.HarmonizationStartIdentityError as exc:
            raise HarmonizationReplayIdentityError(
                "harmonization replay identity mismatch"
            ) from exc
        except RuntimeError as exc:
            if str(exc) == "harmonization job record is unreadable":
                raise HarmonizationReplayIdentityError(
                    "harmonization replay record is unreadable"
                ) from exc
            raise HarmonizationReplayAuthorityError(
                "harmonization process authority is invalid"
            ) from exc
        return self._snapshot(
            current,
            validated_status_phase=validated_status_phase,
        )

    def get(self, job_id: str) -> dict[str, object]:
        job_id = validate_authority_id(job_id)
        from services import harmonization_worker as worker

        job = worker.reconcile_expired_harmonization_job_on_get(job_id)
        return self._snapshot(job)

    def get_owned(
        self,
        job_id: str,
        *,
        tenant_id: str,
        operator_id: str,
    ) -> dict[str, object]:
        job_id = validate_authority_id(job_id)
        from services import harmonization_worker as worker

        try:
            job = worker.reconcile_expired_harmonization_job_on_get(
                job_id,
                expected_tenant_id=tenant_id,
                expected_operator_id=operator_id,
            )
        except worker.HarmonizationJobOwnershipError as exc:
            raise HarmonizationOwnershipError(
                "harmonization job ownership mismatch"
            ) from exc
        return self._snapshot(job)

    def stop(self, job_id: str) -> dict[str, object]:
        job_id = validate_authority_id(job_id)
        from services import harmonization_worker as worker

        stopped = worker.stop_harmonization_job(job_id)
        job = worker.HarmonizationJob.load(job_id)
        if job is None:
            raise KeyError(job_id)
        if not stopped and job.status == "running":
            return self._snapshot(job)
        return self._snapshot(job)

    def stop_owned(
        self,
        job_id: str,
        *,
        tenant_id: str,
        operator_id: str,
    ) -> dict[str, object]:
        job_id = validate_authority_id(job_id)
        from services import harmonization_worker as worker

        try:
            worker.stop_harmonization_job(
                job_id,
                expected_tenant_id=tenant_id,
                expected_operator_id=operator_id,
            )
        except worker.HarmonizationJobOwnershipError as exc:
            raise HarmonizationOwnershipError(
                "harmonization job ownership mismatch"
            ) from exc
        job = worker.HarmonizationJob.load(job_id)
        if job is None:
            raise KeyError(job_id)
        return self._snapshot(job)

    def _snapshot(
        self,
        job: object,
        *,
        validated_status_phase: tuple[str, str] | None = None,
    ) -> dict[str, object]:
        from services import harmonization_worker as worker

        intention = str(getattr(job, "intention", DEFAULT_HARMONIZATION_MODE))
        if validated_status_phase is not None:
            status, authoritative_phase = validated_status_phase
        elif isinstance(job, worker.HarmonizationJob):
            status = str(job.forced_status or job.status)
            authoritative_phase = job.current_phase
        else:
            status = str(
                getattr(job, "forced_status", None)
                or getattr(job, "status", "pending")
            )
            authoritative_phase = getattr(job, "current_phase", None)
        normalized_intention = normalize_harmonization_mode(intention)
        return {
            "job_id": getattr(job, "job_id"),
            "status": status,
            "mode": normalized_intention,
            "intention": normalized_intention,
            "phase": authoritative_phase or harmonization_phase(status),
            "lease": {
                "worker_pid": getattr(job, "worker_pid", None),
                "heartbeat_at": getattr(job, "heartbeat_at", None),
            },
            "manual_action_required": status in {"interrupted", "authority_ambiguous"},
            "target_frequency": getattr(job, "target_frequency"),
            "duration_minutes": getattr(job, "duration_minutes"),
            "hardware_config": {
                key: value
                for key, value in getattr(job, "hardware_config").items()
                if not str(key).startswith("_")
            },
            "pulse_seconds": getattr(job, "pulse_seconds", 3.0),
            "pause_seconds": getattr(job, "pause_seconds", 2.0),
            "duration_factor": getattr(job, "duration_factor", 1),
            "solfeggio_base": getattr(job, "solfeggio_base", 432.0),
            "report_id": getattr(job, "report_id", None),
            "workbench_mode": getattr(job, "workbench_mode", "standard"),
            "tenant_id": getattr(job, "tenant_id", None),
            "operator_id": getattr(job, "operator_id", None),
            "start_time": getattr(job, "start_time"),
            "end_time": getattr(job, "end_time"),
            "progress_percent": getattr(job, "progress_percent"),
            "cycles_completed": getattr(job, "cycles_completed"),
            "total_cycles": getattr(job, "total_cycles"),
            "error_message": getattr(job, "error_message"),
        }

