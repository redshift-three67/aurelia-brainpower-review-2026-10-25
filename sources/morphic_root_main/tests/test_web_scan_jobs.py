from __future__ import annotations

from pathlib import Path

from apps.web.scan_jobs import LocalScanJobService, _LocalScanJob


class FakeProcess:
    def __init__(self, returncode: int | None = None) -> None:
        self.returncode = returncode

    def poll(self) -> int | None:
        return self.returncode


def _job(
    service: LocalScanJobService,
    tmp_path: Path,
    stdout: str,
    *,
    returncode: int | None = None,
) -> _LocalScanJob:
    stdout_path = tmp_path / "job.stdout.log"
    stderr_path = tmp_path / "job.stderr.log"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    return _LocalScanJob(
        job_id="job-1",
        command=["python", "-m", "apps.cli.main", "scan", "top3-scan"],
        process=FakeProcess(returncode),
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )


def test_scan_job_snapshot_exposes_progress_phase_and_substeps(tmp_path: Path) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(
        service,
        tmp_path,
        "\n".join(
            [
                "[1/2] PHASE 1: Screening aller Haupt-Profile...",
                "[OK] TOP-5 RELEVANTE PROFILE:",
                "[2/2] PHASE 2: Vollstaendige Analyse der Top-5 Profile...",
                "[1/5] [OK] Vollstaendige Analyse: regulation",
                "Export gespeichert: C:/exports/report.json",
                "Trendbericht erstellt",
            ]
        ),
    )

    snapshot = service._snapshot(job)

    assert snapshot["status"] == "running"
    assert snapshot["progress_percent"] is not None
    assert 0 < float(snapshot["progress_percent"]) < 100
    assert snapshot["current_phase"] == "Nachbereitung"
    assert snapshot["current_substep"] == "Trendbericht erstellt"
    assert snapshot["completed_substeps"] == [
        "PHASE 1: Screening aller Haupt-Profile",
        "TOP-5 RELEVANTE PROFILE",
        "PHASE 2: Vollstaendige Analyse der Top-5 Profile",
        "Vollstaendige Analyse: regulation",
        "Export gespeichert",
    ]


def test_scan_job_snapshot_bounds_completed_substeps_and_marks_completed(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path)
    job = _job(
        service,
        tmp_path,
        "\n".join(
            [
                "[1/5] Export vorbereiten",
                "[2/5] Harmonisierung vorbereiten",
                "[3/5] Trendbericht erstellt",
                "[4/5] Deutungsbericht erstellt",
                "[5/5] Remedy und Synergy abgeschlossen",
            ]
        ),
        returncode=0,
    )

    snapshot = service._snapshot(job)

    assert snapshot["status"] == "completed"
    assert snapshot["progress_percent"] == 100.0
    assert snapshot["current_phase"] == "Nachbereitung"
    assert snapshot["current_substep"] == "Remedy und Synergy abgeschlossen"
    assert snapshot["completed_substeps"] == [
        "Export vorbereiten",
        "Harmonisierung vorbereiten",
        "Trendbericht erstellt",
        "Deutungsbericht erstellt",
        "Remedy und Synergy abgeschlossen",
    ]


def test_scan_job_snapshot_buffers_partial_lines_between_polls(tmp_path: Path) -> None:
    service = LocalScanJobService(tmp_path)
    stdout_path = tmp_path / "job.stdout.log"
    stderr_path = tmp_path / "job.stderr.log"
    stdout_path.write_text("[1/2] PHASE 1: Screen", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    job = _LocalScanJob(
        job_id="job-2",
        command=["python", "-m", "apps.cli.main", "scan", "top3-scan"],
        process=FakeProcess(None),
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )

    first = service._snapshot(job)
    assert first["current_phase"] is None
    assert first["current_substep"] is None

    stdout_path.write_text(
        "[1/2] PHASE 1: Screening aller Haupt-Profile...\n[OK] TOP-5 RELEVANTE PROFILE:\n",
        encoding="utf-8",
    )
    second = service._snapshot(job)

    assert second["current_phase"] == "Phase 1"
    assert second["current_substep"] == "TOP-5 RELEVANTE PROFILE"
    assert "PHASE 1: Screening aller Haupt-Profile" in second["completed_substeps"]


def test_scan_job_snapshot_does_not_flush_recognizable_partial_marker(
    tmp_path: Path,
) -> None:
    service = LocalScanJobService(tmp_path)
    stdout_path = tmp_path / "job3.stdout.log"
    stderr_path = tmp_path / "job3.stderr.log"
    stdout_path.write_text("Trendbericht", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")
    job = _LocalScanJob(
        job_id="job-3",
        command=["python", "-m", "apps.cli.main", "scan", "top3-scan"],
        process=FakeProcess(None),
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )

    first = service._snapshot(job)
    assert first["current_substep"] is None

    stdout_path.write_text("Trendbericht erstellt\n", encoding="utf-8")
    second = service._snapshot(job)
    assert second["current_substep"] == "Trendbericht erstellt"
