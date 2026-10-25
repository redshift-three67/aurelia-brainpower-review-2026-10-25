from apps.web.workbench_registry import build_workbench_registry


def test_build_workbench_registry_exposes_canonical_operator_workbench() -> None:
    payload = build_workbench_registry()

    assert payload["version"] == 1
    assert [step["id"] for step in payload["steps"]] == [
        "runtime",
        "client",
        "focus",
        "profile",
        "hardware",
        "review",
        "run",
        "results",
        "details",
        "harmonize",
        "finalize",
    ]
    assert payload["steps"][5]["label"] == "Review & Freigabe"
    assert payload["steps"][9]["label"] == "Harmonisierung & Abschluss"
    assert payload["steps"][10]["label"] == "Berichtskatalog & Export"
    assert payload["pipeline_view"]["href"] == "/workflow-stepping"
    assert payload["pipeline_view"]["kind"] == "explanatory"
