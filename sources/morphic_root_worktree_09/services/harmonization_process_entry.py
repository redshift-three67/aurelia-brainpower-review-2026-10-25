from __future__ import annotations

import argparse

from apps.web.authority_ids import validate_harmonization_job_id_for_creation


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("job_id")
    args = parser.parse_args()
    job_id = validate_harmonization_job_id_for_creation(args.job_id)
    from services.harmonization_worker import HarmonizationJob, run_harmonization_worker

    outcome = run_harmonization_worker(job_id)
    persisted = HarmonizationJob.load(job_id)
    if persisted is None:
        return 1
    if outcome == "completed" and persisted.status == "completed":
        return 0
    if outcome == "stopped" and persisted.status in {
        "pending",
        "starting",
        "running",
        "stopped",
    }:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
