from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import pytest

from apps.web.contracts import Phase1ScanRequest
from apps.web.main import create_app
from apps.web.scan_jobs import ScanJobOwnershipError
from core.compliance.operator_context import operator_owner_scope
from tests.test_web_shell import request


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "apps" / "web" / "static" / "index.html"


class AdaptiveLimitsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.control: dict[str, str | None] | None = None
        self.help_parts: list[str] = []
        self._inside_help = False

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if tag == "input" and attributes.get("name") == "adaptive_limits":
            self.control = attributes
        if attributes.get("id") == "adaptive-limits-help":
            self._inside_help = True

    def handle_endtag(self, tag: str) -> None:
        if self._inside_help and tag == "p":
            self._inside_help = False

    def handle_data(self, data: str) -> None:
        if self._inside_help and data.strip():
            self.help_parts.append(" ".join(data.split()))


def test_adaptive_limits_default_and_help_match_product_contract() -> None:
    parser = AdaptiveLimitsParser()
    parser.feed(INDEX_HTML.read_text(encoding="utf-8"))

    assert Phase1ScanRequest.model_fields["adaptive_limits"].default is False
    assert parser.control is not None
    assert "checked" not in parser.control
    assert parser.control.get("aria-describedby") == "adaptive-limits-help"

    help_text = " ".join(parser.help_parts)
    for marker in (
        "Standard: aus",
        "Screening-Pool",
        "Top-N",
        "Phase-2-Detailumfang",
        "max(32, Top-N × 16)",
        "höchstens 5",
        "ReportDETAIL",
        "ownergebundene sichtbare Top-Profilliste",
    ):
        assert marker in help_text
    assert "Scoreformel und Reihenfolge werden nicht verändert" in help_text
    assert "Der globale Berichtskatalog bleibt unverändert" in help_text
    for forbidden in (
        "Scoreformel wird verändert",
        "Scoreformel wird begrenzt",
        "Reihenfolge wird verändert",
        "Reihenfolge wird begrenzt",
        "globale Berichtskatalog wird verändert",
        "globale Berichtskatalog wird begrenzt",
    ):
        assert forbidden not in help_text


class _AdaptiveResultJobs:
    def __init__(
        self,
        command: Any,
        artifact_paths: list[Path],
        report_session_id: object = None,
    ) -> None:
        self.command = command
        self.artifact_paths = artifact_paths
        self.report_session_id = report_session_id
        self.owner_id = ""

    def get_owned(
        self,
        job_id: str,
        *,
        expected_owner_id: str,
    ) -> dict[str, object]:
        if self.owner_id != expected_owner_id:
            raise ScanJobOwnershipError("scan job owner identity mismatch")
        return {
            "job_id": job_id,
            "status": "completed",
            "owner_id": self.owner_id,
            "command": self.command,
            "artifact_paths": [str(path) for path in self.artifact_paths],
            "report_session_id": self.report_session_id,
        }


def _ranked_result_artifacts(export_root: Path, count: int) -> list[Path]:
    artifacts = []
    for index in range(count):
        path = (
            export_root
            / "Resonanz"
            / "client"
            / "run"
            / f"profile-{index}"
            / f"{index:02d}_multiplex_scan.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "profile": f"P{index}",
                    "sub_results": {
                        "top": [
                            {
                                "label": f"R{index}",
                                "score": float(90 - index),
                            }
                        ]
                    },
                }
            ),
            encoding="utf-8",
        )
        artifacts.append(path)
    # The endpoint must sort by score rather than trust persisted artifact order.
    return list(reversed(artifacts[::2])) + artifacts[1::2]


@pytest.mark.parametrize("report_session_id", ["session-exact", None])
def test_owner_bound_results_expose_exact_optional_report_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    report_session_id: str | None,
) -> None:
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "gate-4-report-owner")
    export_root = tmp_path / "exports"
    artifacts = _ranked_result_artifacts(export_root, 3)
    jobs = _AdaptiveResultJobs(
        ["--top-n", "3"],
        artifacts,
        report_session_id=report_session_id,
    )
    app = create_app(scan_jobs=jobs, runtime_dir=tmp_path / "runtime")
    jobs.owner_id = operator_owner_scope(app.state.operator_context)

    response = request(app, "GET", "/api/scan/jobs/gate-2-results/results")

    assert response.status_code == 200
    assert response.json()["report_session_id"] == report_session_id


@pytest.mark.parametrize(
    ("limit_mode", "expected_count"),
    [("none", 9), ("adaptive", 5), ("fixed", 9)],
)
def test_owner_bound_results_apply_adaptive_limit_from_persisted_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    limit_mode: str,
    expected_count: int,
) -> None:
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "gate-2-owner")
    export_root = tmp_path / "exports"
    artifacts = _ranked_result_artifacts(export_root, 9)
    command = [
        "python",
        "-m",
        "apps.cli.main",
        "scan",
        "top3-scan",
        "--export",
        str(export_root),
        "--top-n",
        "9",
    ]
    if limit_mode == "adaptive":
        command.append("--adaptive-limits")
    elif limit_mode == "fixed":
        command.append("--fixed-limits")
    jobs = _AdaptiveResultJobs(command, artifacts)
    app = create_app(scan_jobs=jobs, runtime_dir=tmp_path / "runtime")
    jobs.owner_id = operator_owner_scope(app.state.operator_context)

    response = request(app, "GET", "/api/scan/jobs/gate-2-results/results")

    assert response.status_code == 200
    payload = response.json()
    top_profiles = payload["top_profiles"]
    assert [(item["profile"], item["score"]) for item in top_profiles] == [
        (f"P{index}", float(90 - index)) for index in range(expected_count)
    ]
    assert [(item["label"], item["score"]) for item in payload["top_resonances"]] == [
        (f"R{index}", float(90 - index)) for index in range(9)
    ]
    if limit_mode == "adaptive":
        assert {item["profile"] for item in top_profiles}.isdisjoint(
            {"P5", "P6", "P7", "P8"}
        )


@pytest.mark.parametrize(
    ("command_case", "tokens"),
    [
        pytest.param("none", None, id="none"),
        pytest.param("tuple", ["--top-n", "9", "--adaptive-limits"], id="tuple"),
        pytest.param(
            "invalid-list",
            ["--top-n", "9", "--adaptive-limits", None],
            id="non-string-token",
        ),
        pytest.param(
            "list",
            ["--top-n", "9", "--top-n", "9", "--adaptive-limits"],
            id="duplicate-top-n-equal",
        ),
        pytest.param(
            "list",
            ["--top-n", "9", "--top-n", "7", "--adaptive-limits"],
            id="duplicate-top-n-different",
        ),
        pytest.param("list", ["--top-n"], id="missing-top-n-value"),
        pytest.param(
            "list",
            ["--top-n", "9", "--adaptive-limits", "--fixed-limits"],
            id="adaptive-and-fixed",
        ),
        pytest.param(
            "list",
            ["--top-n", "9", "--adaptive-limits", "--adaptive-limits"],
            id="duplicate-adaptive",
        ),
        pytest.param(
            "list",
            ["--top-n", "9", "--adaptive-limits", "true"],
            id="adaptive-with-value",
        ),
        pytest.param(
            "list",
            ["--top-n", "9", "--adaptive-limits=true"],
            id="adaptive-with-attached-value",
        ),
        pytest.param(
            "list",
            ["--top-n", "9", "--fixed-limits", "--fixed-limits"],
            id="duplicate-fixed",
        ),
        pytest.param(
            "list",
            ["--top-n", "9", "--fixed-limits", "false"],
            id="fixed-with-value",
        ),
        pytest.param(
            "list",
            ["--top-n", "9", "--fixed-limits=false"],
            id="fixed-with-attached-value",
        ),
        pytest.param(
            "list",
            ["--top-n", "9", "--adaptive-limits", "--fixed-limits=false"],
            id="adaptive-with-attached-fixed-conflict",
        ),
        pytest.param(
            "list",
            ["--top-n", "9", "--fixed-limits", "--adaptive-limits=true"],
            id="fixed-with-attached-adaptive-conflict",
        ),
    ],
)
def test_owner_bound_results_reject_ambiguous_persisted_limit_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    command_case: str,
    tokens: list[object] | None,
) -> None:
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "gate-2-command-owner")
    export_root = tmp_path / "exports"
    artifacts = _ranked_result_artifacts(export_root, 11)
    if tokens is None:
        command: Any = None
    else:
        command = ["python", "--export", str(export_root), *tokens]
        if command_case == "tuple":
            command = tuple(command)
    jobs = _AdaptiveResultJobs(command, artifacts)
    app = create_app(scan_jobs=jobs, runtime_dir=tmp_path / "runtime")
    jobs.owner_id = operator_owner_scope(app.state.operator_context)

    response = request(app, "GET", "/api/scan/jobs/gate-2-command/results")

    assert response.status_code == 200
    expected_profiles = (
        []
        if command_case in {"none", "tuple", "invalid-list"}
        else [f"P{index}" for index in range(10)]
    )
    assert [item["profile"] for item in response.json()["top_profiles"]] == expected_profiles


@pytest.mark.parametrize(
    "tail",
    [
        ["--adaptive-limits", "--focus", "Schlaf"],
        ["--adaptive-limits", "--local-ai", "--focus", "Schlaf"],
    ],
    ids=["focus", "local-ai-and-focus"],
)
def test_owner_bound_results_accept_generated_adaptive_flag_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    tail: list[str],
) -> None:
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "gate-2-generated-owner")
    export_root = tmp_path / "exports"
    artifacts = _ranked_result_artifacts(export_root, 9)
    jobs = _AdaptiveResultJobs(
        [
            "python",
            "--export",
            str(export_root),
            "--top-n",
            "9",
            *tail,
        ],
        artifacts,
    )
    app = create_app(scan_jobs=jobs, runtime_dir=tmp_path / "runtime")
    jobs.owner_id = operator_owner_scope(app.state.operator_context)

    response = request(app, "GET", "/api/scan/jobs/gate-2-generated/results")

    assert response.status_code == 200
    assert [item["profile"] for item in response.json()["top_profiles"]] == [
        f"P{index}" for index in range(5)
    ]


@pytest.mark.parametrize("top_n_value", ["invalid", "100"])
def test_owner_bound_results_keep_legacy_limit_for_invalid_top_n(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    top_n_value: str,
) -> None:
    monkeypatch.setenv("MORPHIC_OPERATOR_ID", "gate-2-legacy-owner")
    export_root = tmp_path / "exports"
    artifacts = _ranked_result_artifacts(export_root, 11)
    jobs = _AdaptiveResultJobs(
        [
            "python",
            "--export",
            str(export_root),
            "--top-n",
            top_n_value,
            "--adaptive-limits",
        ],
        artifacts,
    )
    app = create_app(scan_jobs=jobs, runtime_dir=tmp_path / "runtime")
    jobs.owner_id = operator_owner_scope(app.state.operator_context)

    response = request(app, "GET", "/api/scan/jobs/gate-2-legacy/results")

    assert response.status_code == 200
    assert [item["profile"] for item in response.json()["top_profiles"]] == [
        f"P{index}" for index in range(10)
    ]
