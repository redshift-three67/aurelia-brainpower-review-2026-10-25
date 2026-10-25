"""Durable EXP1 comparison job store tests using synthetic bound source data."""

from __future__ import annotations

import copy
import hashlib
import importlib
from pathlib import Path
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

from radiworks.core.experimental_matrix import (
    ENGINE_SHA256,
    FORMULA_VERSION,
    ROUTES_SHA256,
    prepare_catalog_context,
)
from radiworks.core.personal_context import ContextSnapshot, prepare_identity
from radiworks.persistence import document_digest
from radiworks.scope import ScopeContext


SCOPE = ScopeContext("tenant-a", "client-a", "job-a")
OTHER_SCOPE = ScopeContext("tenant-b", "client-a", "job-a")


def _api():
    try:
        module = importlib.import_module("radiworks.core.comparison_store")
    except ImportError as exc:
        raise AssertionError("comparison store API is missing") from exc
    assert hasattr(module, "ComparisonStore"), "ComparisonStore is missing"
    assert hasattr(module, "ComparisonStoreError"), "ComparisonStoreError is missing"
    return module.ComparisonStore, module.ComparisonStoreError


def _snapshot(scope: ScopeContext = SCOPE) -> dict:
    case = {
        "name": "Synthetic comparison",
        "focus": "Ruhe",
        "personalContext": {
            "firstName": "Ada",
            "lastName": "Example",
            "birthDate": "1980-02-29",
        },
    }
    prepare_identity(case)
    return ContextSnapshot.capture(case, scope).payload()


def _catalog(content: str = "Synthetic Rate A\nSynthetic Rate B\nRuhe\n") -> dict:
    return {
        "name": "TEST_STORE.txt",
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "content": content,
    }


def _rate(name: str) -> dict:
    return {
        "energeticValue": 0,
        "nameOrRate": name,
        "url": None,
        "gv": 0,
        "recurring": 0,
        "recurringGeneralVitality": 0,
        "level": 0,
        "potency": None,
        "resonateCounter": 0,
    }


def _input(scope: ScopeContext = SCOPE, *, rates=None) -> dict:
    snapshot = _snapshot(scope)
    catalog = _catalog()
    selected_rates = list(rates if rates is not None else ["Synthetic Rate A", "Synthetic Rate B"])
    return {
        "caseId": snapshot["caseId"],
        "sourceSessionId": "a" * 32,
        "contextSnapshot": snapshot,
        "catalog": catalog,
        "rates": selected_rates,
        "originalSubset": [_rate(name) for name in selected_rates],
        "originalProvenance": {"sessionId": "a" * 32, "revision": 2},
        "formulaVersion": FORMULA_VERSION,
        "implementationHash": "b" * 64,
        "weight": "Normal",
        "pageStart": 0,
        "sourceDigest": "c" * 64,
    }


def _valid_result(payload: dict) -> dict:
    snapshot = payload["contextSnapshot"]
    catalog = payload["catalog"]
    prepared = prepare_catalog_context(snapshot, catalog)
    result = {
        "formulaVersion": FORMULA_VERSION,
        "sourceHashes": {
            **prepared["sourceHashes"],
            "Radi144/app/algorithms/resonance_engine.py": ENGINE_SHA256,
            "Radi144/app/api/resonance.py": ROUTES_SHA256,
        },
        "caseId": payload["caseId"],
        "contextVersion": snapshot["contextVersion"],
        "contextDigest": snapshot["digest"],
        "catalog": prepared["catalog"],
        "preparedContext": prepared,
        "parameters": {
            "backend": "cpu",
            "dtype": "float32",
            "matrixSize": 12,
            "embedDimension": 256,
            "candidateCount": 80000,
            "purpose": "product-cpu",
            "threads": 1,
            "focusWeight": payload["weight"],
            "focusWeightValue": 1.0,
            "rng": "local-torch-generators",
            "topK": 10,
            "torchVersion": "2.12.0+cpu",
            "numpyVersion": "2.4.6",
            "pythonVersion": "3.13.7",
            "platform": "Windows",
            "bioEnabled": False,
            "hrvEnabled": False,
            "emfEnabled": False,
            "quantumEnabled": False,
            "symmetry": "none",
            "clockEnabled": False,
            "numericImageEnabled": False,
            "rateScope": "explicit-bound-subset",
            "maximumRates": 21,
        },
        "inputRates": list(payload["rates"]),
        "results": [
            {
                "rate": rate,
                "originalIndex": index,
                "score": 0.5 - index / 10,
                "intensity": 1.25,
                "matrix": [[index % 10 for _ in range(12)] for _ in range(12)],
            }
            for index, rate in enumerate(payload["rates"])
        ],
    }
    result["resultDigest"] = document_digest(result)
    return result


def _store(path, scope=SCOPE):
    ComparisonStore, _ = _api()
    return ComparisonStore(path, scope)


def _expect_code(error_type, code, call):
    with pytest.raises(error_type) as caught:
        call()
    assert caught.value.code == code


def test_create_freezes_input_and_returns_detached_idempotent_record(tmp_path):
    ComparisonStore, _ = _api()
    payload = _input()
    before = copy.deepcopy(payload)
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)

    record = store.create("1" * 32, payload)
    payload["catalog"]["content"] = "changed"
    record["input"]["rates"].append("changed")
    reloaded = store.get(record["id"])
    duplicate = store.create("1" * 32, before)

    assert reloaded["input"] == before
    assert reloaded["inputDigest"] == document_digest(before)
    assert duplicate["id"] == record["id"]
    assert duplicate["comparisonSessionId"] == record["comparisonSessionId"]
    assert duplicate["status"] == "queued"
    assert duplicate["scope"] == SCOPE.to_dict()
    assert duplicate["result"] is None and duplicate["error"] is None


def test_create_rejects_same_request_id_with_different_frozen_input(tmp_path):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)
    store.create("2" * 32, _input())
    changed = _input()
    changed["weight"] = "Stark"

    _expect_code(Error, "idempotency_conflict", lambda: store.create("2" * 32, changed))


def test_only_one_queued_or_running_comparison_can_be_admitted(tmp_path):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)
    first = store.create("3" * 32, _input())

    _expect_code(Error, "busy", lambda: store.create("4" * 32, _input()))
    claimed = store.claim(first["id"])
    assert claimed["status"] == "running"
    _expect_code(Error, "busy", lambda: store.create("4" * 32, _input()))


def test_concurrent_admission_has_one_winner(tmp_path):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)

    def submit(index):
        try:
            return store.create(f"{index:032x}", _input())
        except Error as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=4) as pool:
        outcomes = list(pool.map(submit, range(1, 5)))

    assert sum(isinstance(outcome, dict) for outcome in outcomes) == 1
    assert outcomes.count("busy") == 3


def test_result_must_match_bound_cpu_product_envelope_before_completion(tmp_path):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)
    created = store.create("5" * 32, _input())
    store.claim(created["id"])
    result = _valid_result(created["input"])

    completed = store.finish(created["id"], result)
    assert completed["status"] == "completed"
    assert completed["result"] == result
    assert completed["error"] is None
    assert store.get(created["id"]) == completed
    assert store.list_for_case(created["input"]["caseId"]) == [completed]
    _expect_code(Error, "terminal", lambda: store.finish(created["id"], result))
    _expect_code(Error, "terminal", lambda: store.fail(created["id"], "worker_failed"))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda result: result["parameters"].update(candidateCount=64, purpose="test-only"),
        lambda result: result["parameters"].update(threads=2),
        lambda result: result["parameters"].update(bioEnabled=True),
        lambda result: result.update(contextDigest="0" * 64),
        lambda result: result["inputRates"].reverse(),
        lambda result: result["results"][0].update(originalIndex=1),
        lambda result: result["results"][0].update(score=float("nan")),
        lambda result: result["results"][0].update(matrix=[[10] * 12 for _ in range(12)]),
        lambda result: result.update(resultDigest="0" * 64),
    ],
)
def test_invalid_result_envelopes_never_leave_job_running(tmp_path, mutation):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)
    created = store.create("6" * 32, _input())
    store.claim(created["id"])
    result = _valid_result(created["input"])
    mutation(result)
    if result.get("resultDigest") != "0" * 64:
        result["resultDigest"] = document_digest(
            {key: value for key, value in result.items() if key != "resultDigest"}
        )

    _expect_code(Error, "invalid_result", lambda: store.finish(created["id"], result))
    assert store.get(created["id"])["status"] == "running"
    assert store.get(created["id"])["result"] is None


def test_payload_validation_rejects_scope_catalog_and_oversize_before_create(tmp_path):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)
    wrong_scope = _input(OTHER_SCOPE)
    _expect_code(Error, "scope_mismatch", lambda: store.create("7" * 32, wrong_scope))

    bad_catalog = _input()
    bad_catalog["catalog"]["sha256"] = "0" * 64
    _expect_code(Error, "invalid_input", lambda: store.create("8" * 32, bad_catalog))

    oversized = _input()
    oversized["originalProvenance"]["padding"] = "x" * (5 * 1024 * 1024)
    _expect_code(Error, "input_too_large", lambda: store.create("9" * 32, oversized))
    assert store.list_for_case(_input()["caseId"]) == []


@pytest.mark.parametrize("bad_id", ["", "A" * 32, "f" * 31, "g" * 32, 123])
def test_request_and_job_ids_are_exact_lowercase_hex(tmp_path, bad_id):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)
    _expect_code(Error, "invalid_id", lambda: store.create(bad_id, _input()))


def test_wrong_scope_store_cannot_read_an_existing_scope_database(tmp_path):
    ComparisonStore, Error = _api()
    path = tmp_path / "comparisons.sqlite3"
    store = ComparisonStore(path, SCOPE)
    payload = _input()
    created = store.create("a" * 32, payload)

    _expect_code(Error, "scope_mismatch", lambda: ComparisonStore(path, OTHER_SCOPE))
    _expect_code(Error, "invalid_id", lambda: store.get("z" * 32))
    assert store.get(created["id"])["input"] == payload


def test_restart_interrupts_active_work_and_explicit_retry_keeps_input(tmp_path):
    ComparisonStore, Error = _api()
    path = tmp_path / "comparisons.sqlite3"
    first_store = ComparisonStore(path, SCOPE)
    first = first_store.create("b" * 32, _input())
    first_store.claim(first["id"])

    restarted = ComparisonStore(path, SCOPE)
    assert restarted.interrupt_pending() == 1
    interrupted = restarted.get(first["id"])
    assert interrupted["status"] == "interrupted"
    assert interrupted["error"] == {"code": "interrupted"}
    assert restarted.interrupt_pending() == 0

    retry = restarted.retry(first["id"], "c" * 32)
    assert retry["status"] == "queued"
    assert retry["parentJobId"] == first["id"]
    assert retry["input"] == first["input"]
    assert retry["inputDigest"] == first["inputDigest"]
    assert retry["id"] != first["id"]
    _expect_code(Error, "busy", lambda: restarted.retry(first["id"], "d" * 32))


def test_retry_is_idempotent_for_same_request_and_rejects_nonretryable_parent(tmp_path):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)
    first = store.create("d" * 32, _input())
    store.claim(first["id"])
    store.fail(first["id"], "worker_failed")

    retry = store.retry(first["id"], "e" * 32)
    assert store.retry(first["id"], "e" * 32)["id"] == retry["id"]
    store.claim(retry["id"])
    store.finish(retry["id"], _valid_result(retry["input"]))
    _expect_code(Error, "not_retryable", lambda: store.retry(retry["id"], "f" * 32))


def test_cancel_wins_terminal_race_and_late_finish_cannot_store_partial_result(tmp_path):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)
    created = store.create("f" * 32, _input())
    store.claim(created["id"])
    late_result = _valid_result(created["input"])

    cancelled = store.cancel(created["id"])
    assert cancelled["status"] == "cancelled"
    assert cancelled["result"] is None
    assert cancelled["error"] == {"code": "cancelled"}
    _expect_code(Error, "terminal", lambda: store.finish(created["id"], late_result))
    assert store.get(created["id"])["result"] is None


def test_database_tampering_and_corrupt_json_fail_closed_on_read(tmp_path):
    ComparisonStore, Error = _api()
    path = tmp_path / "comparisons.sqlite3"
    store = ComparisonStore(path, SCOPE)
    created = store.create("0" * 32, _input())
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE comparison_jobs SET input_json = ? WHERE job_id = ?",
            ('{"broken":', created["id"]),
        )

    _expect_code(Error, "corrupt_record", lambda: store.get(created["id"]))


def test_database_corruption_is_not_overwritten_on_open(tmp_path):
    ComparisonStore, Error = _api()
    path = tmp_path / "corrupt.sqlite3"
    path.write_bytes(b"this is not a sqlite database")

    _expect_code(Error, "corrupt_store", lambda: ComparisonStore(path, SCOPE))
    assert path.read_bytes() == b"this is not a sqlite database"


def test_unhashable_weight_is_a_controlled_input_error(tmp_path):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)
    payload = _input()
    payload["weight"] = []

    _expect_code(Error, "invalid_input", lambda: store.create("1" * 32, payload))


def test_unrepresentable_result_score_is_a_controlled_result_error(tmp_path):
    ComparisonStore, Error = _api()
    store = ComparisonStore(tmp_path / "comparisons.sqlite3", SCOPE)
    created = store.create("2" * 32, _input())
    store.claim(created["id"])
    result = _valid_result(created["input"])
    result["results"][0]["score"] = 10**3000
    result["resultDigest"] = document_digest(
        {key: value for key, value in result.items() if key != "resultDigest"}
    )

    _expect_code(Error, "invalid_result", lambda: store.finish(created["id"], result))


def test_invalid_database_path_is_a_controlled_store_error():
    ComparisonStore, Error = _api()
    _expect_code(Error, "unsafe_path", lambda: ComparisonStore(None, SCOPE))

def test_database_symlink_path_is_rejected_without_following_target(tmp_path, monkeypatch):
    ComparisonStore, Error = _api()
    target = tmp_path / "target.sqlite3"
    target.write_bytes(b"protected target")
    link = tmp_path / "linked.sqlite3"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        original_is_symlink = Path.is_symlink
        monkeypatch.setattr(
            Path,
            "is_symlink",
            lambda candidate: candidate == link or original_is_symlink(candidate),
        )

    _expect_code(Error, "unsafe_path", lambda: ComparisonStore(link, SCOPE))
    assert target.read_bytes() == b"protected target"