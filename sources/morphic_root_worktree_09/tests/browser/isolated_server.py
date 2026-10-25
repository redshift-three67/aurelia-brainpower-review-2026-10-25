from __future__ import annotations

import os
from pathlib import Path
import sys

import uvicorn


WORKTREE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE_ROOT))


def main() -> None:
    runtime_root = Path(os.environ["MORPHIC_BROWSER_RUNTIME_ROOT"]).resolve()
    runtime_root.mkdir(parents=True, exist_ok=True)
    os.environ["MORPHIC_RUNTIME_DIR"] = str(runtime_root / "runtime")
    os.environ["MORPHIC_HARMONIZATION_JOBS_DIR"] = str(
        runtime_root / "harmonization-jobs"
    )
    os.environ["MORPHIC_API_KEY"] = ""
    os.environ["MORPHIC_GROUP_ANALYSIS_ENABLED"] = "0"

    from apps.web.main import create_app

    app = create_app(
        runtime_dir=runtime_root / "runtime",
        report_roots=[runtime_root / "reports"],
    )
    health_token = os.environ["MORPHIC_BROWSER_HEALTH_TOKEN"]

    @app.get("/__browser-test-health", include_in_schema=False)
    async def browser_test_health() -> dict[str, str]:
        return {"token": health_token}

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=int(os.environ["MORPHIC_BROWSER_PORT"]),
        log_level="warning",
    )


if __name__ == "__main__":
    main()
