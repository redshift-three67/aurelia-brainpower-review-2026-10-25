"""Durable, scope-pinned EXP1 comparison job storage.

This module stores immutable comparison inputs and terminal result envelopes only.
It does not select source data or run the optional CPU profile.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from ..persistence import document_digest
from ..scope import ScopeContext
from .experimental_context import ExperimentalContextError
from .experimental_matrix import (
    ENGINE_SHA256,
    FORMULA_VERSION,
    ROUTES_SHA256,
    WEIGHTS,
    MatrixError,
    prepare_catalog_context,
)
from .personal_context import ContextError, ContextSnapshot


_SCHEMA_VERSION = 1
_MAX_JSON_BYTES = 5 * 1024 * 1024
_MAX_CATALOG_BYTES = 4 * 1024 * 1024
_MAX_RATES = 21
_ID_RE = re.compile(r"[0-9a-f]{32}\Z")
_SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
_CATALOG_NAME_RE = re.compile(r"[^/\\:\x00-\x1f\x7f]{1,240}\.txt\Z")
_RATE_FIELDS = frozenset(
    {
        "energeticValue",
        "nameOrRate",
        "url",
        "gv",
        "recurring",
        "recurringGeneralVitality",
        "level",
        "potency",
        "resonateCounter",
    }
)
_INPUT_FIELDS = frozenset(
    {
        "caseId",
        "sourceSessionId",
        "contextSnapshot",
        "catalog",
        "rates",
        "originalSubset",
        "originalProvenance",
        "formulaVersion",
        "implementationHash",
        "weight",
        "pageStart",
        "sourceDigest",
    }
)
_RESULT_FIELDS = frozenset(
    {
        "formulaVersion",
        "sourceHashes",
        "caseId",
        "contextVersion",
        "contextDigest",
        "catalog",
        "preparedContext",
        "parameters",
        "inputRates",
        "results",
        "resultDigest",
    }
)
_PARAMETER_FIELDS = frozenset(
    {
        "backend",
        "dtype",
        "matrixSize",
        "embedDimension",
        "candidateCount",
        "purpose",
        "threads",
        "focusWeight",
        "focusWeightValue",
        "rng",
        "topK",
        "torchVersion",
        "numpyVersion",
        "pythonVersion",
        "platform",
        "bioEnabled",
        "hrvEnabled",
        "emfEnabled",
        "quantumEnabled",
        "symmetry",
        "clockEnabled",
        "numericImageEnabled",
        "rateScope",
        "maximumRates",
    }
)
_STORED_ERROR_CODES = frozenset(
    {
        "cancelled",
        "cpu_unavailable",
        "implementation_changed",
        "interrupted",
        "shutdown",
        "worker_failed",
        "worker_protocol",
        "worker_start_failed",
        "worker_timeout",
    }
)
_VALID_STATUSES = frozenset(
    {"queued", "running", "completed", "failed", "cancelled", "interrupted"}
)
_RETRYABLE_STATUSES = frozenset({"failed", "interrupted"})
_ACTIVE_STATUSES = ("queued", "running")


class ComparisonStoreError(RuntimeError):
    """A controlled comparison-store error with a fixed public code."""

    _MESSAGES = {
        "busy": "A comparison is already queued or running.",
        "corrupt_record": "Stored comparison evidence failed integrity checks.",
        "corrupt_store": "Comparison storage is damaged or has an unknown schema.",
        "idempotency_conflict": "The request identifier is already bound to different input.",
        "input_too_large": "Comparison input exceeds the storage limit.",
        "invalid_error_code": "Comparison error code is not allowlisted.",
        "invalid_id": "Comparison identifier is invalid.",
        "invalid_input": "Comparison input does not match the required contract.",
        "invalid_result": "Comparison result does not match the bound CPU profile.",
        "invalid_scope": "Comparison scope is invalid.",
        "invalid_transition": "Comparison job is not in a state that permits this transition.",
        "not_found": "Comparison job was not found in the active scope.",
        "not_retryable": "Only failed or interrupted comparisons can be retried.",
        "scope_mismatch": "Comparison storage belongs to a different scope.",
        "store_busy": "Comparison storage is busy.",
        "store_error": "Comparison storage could not complete the operation.",
        "terminal": "Comparison job is already terminal.",
        "unsafe_path": "Comparison database path is not a safe regular-file path.",
    }

    def __init__(self, code: str) -> None:
        self.code = code if code in self._MESSAGES else "store_error"
        super().__init__(self._MESSAGES[self.code])


def _valid_hex(value: object, pattern: re.Pattern[str]) -> bool:
    return type(value) is str and pattern.fullmatch(value) is not None


def _validate_json_tree(value: object, seen: set[int], depth: int = 0) -> None:
    if depth > 80:
        raise ValueError("JSON nesting is too deep")
    if value is None or type(value) in (str, bool, int):
        if type(value) is str:
            value.encode("utf-8")
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("non-finite number")
        return
    if type(value) not in (dict, list):
        raise ValueError("unsupported JSON value")
    identity = id(value)
    if identity in seen:
        raise ValueError("cyclic JSON value")
    seen.add(identity)
    try:
        if type(value) is dict:
            for key, item in value.items():
                if type(key) is not str:
                    raise ValueError("JSON object key is not text")
                key.encode("utf-8")
                _validate_json_tree(item, seen, depth + 1)
        else:
            for item in value:
                _validate_json_tree(item, seen, depth + 1)
    finally:
        seen.remove(identity)


def _canonical_json(value: object, *, limit: int = _MAX_JSON_BYTES) -> tuple[Any, str]:
    _validate_json_tree(value, set())
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    if len(encoded) > limit:
        raise OverflowError("JSON value exceeds limit")
    canonical = encoded.decode("utf-8")
    return json.loads(canonical), canonical


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _safe_sqlite_error(exc: sqlite3.Error) -> ComparisonStoreError:
    message = str(exc).lower()
    if "locked" in message or "busy" in message:
        return ComparisonStoreError("store_busy")
    if "malformed" in message or "not a database" in message or "corrupt" in message:
        return ComparisonStoreError("corrupt_store")
    return ComparisonStoreError("store_error")


class ComparisonStore:
    """SQLite-backed store for one immutable ScopeContext owner."""

    def __init__(self, path: Path, scope: ScopeContext) -> None:
        if not isinstance(scope, ScopeContext):
            raise ComparisonStoreError("invalid_scope")
        try:
            self.path = Path(path).absolute()
        except (TypeError, ValueError, OSError):
            raise ComparisonStoreError("unsafe_path") from None
        self.scope = scope
        self._scope_json = json.dumps(
            scope.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        self._check_safe_path(create_parent=True)
        self._initialize()

    def _check_safe_path(self, *, create_parent: bool = False) -> None:
        try:
            if self.path.is_symlink():
                raise ComparisonStoreError("unsafe_path")
            if self.path.exists() and not self.path.is_file():
                raise ComparisonStoreError("unsafe_path")
            for suffix in ("-wal", "-shm", "-journal"):
                if Path(f"{self.path}{suffix}").is_symlink():
                    raise ComparisonStoreError("unsafe_path")
            if create_parent:
                self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists() and self.path.stat().st_size:
                with self.path.open("rb") as handle:
                    if handle.read(16) != b"SQLite format 3\x00":
                        raise ComparisonStoreError("corrupt_store")
        except ComparisonStoreError:
            raise
        except OSError:
            raise ComparisonStoreError("unsafe_path") from None

    def _connect(self) -> sqlite3.Connection:
        self._check_safe_path()
        try:
            connection = sqlite3.connect(
                str(self.path), timeout=8.0, isolation_level=None
            )
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA busy_timeout = 8000")
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA synchronous = FULL")
            return connection
        except sqlite3.Error as exc:
            raise _safe_sqlite_error(exc) from None
        except OSError:
            raise ComparisonStoreError("store_error") from None

    @contextmanager
    def _transaction(self, *, write: bool) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            self._verify_schema_and_owner(connection)
            yield connection
            connection.commit()
        except ComparisonStoreError:
            connection.rollback()
            raise
        except sqlite3.Error as exc:
            connection.rollback()
            raise _safe_sqlite_error(exc) from None
        except (OSError, ValueError):
            connection.rollback()
            raise ComparisonStoreError("store_error") from None
        finally:
            connection.close()

    def _initialize(self) -> None:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
                )
            }
            if version == 0 and not tables:
                self._create_schema(connection)
                connection.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
            self._verify_schema_and_owner(connection)
            check = connection.execute("PRAGMA quick_check(1)").fetchone()
            if check is None or check[0] != "ok":
                raise ComparisonStoreError("corrupt_store")
            connection.commit()
            connection.execute("PRAGMA journal_mode = WAL")
        except ComparisonStoreError:
            connection.rollback()
            raise
        except sqlite3.Error as exc:
            connection.rollback()
            raise _safe_sqlite_error(exc) from None
        except OSError:
            connection.rollback()
            raise ComparisonStoreError("store_error") from None
        finally:
            connection.close()

    def _create_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            "CREATE TABLE comparison_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        connection.execute(
            "CREATE TABLE comparison_jobs ("
            "job_id TEXT PRIMARY KEY,"
            "comparison_session_id TEXT NOT NULL UNIQUE,"
            "request_id TEXT NOT NULL UNIQUE,"
            "case_id TEXT NOT NULL,"
            "input_json TEXT NOT NULL,"
            "input_digest TEXT NOT NULL,"
            "status TEXT NOT NULL CHECK(status IN "
            "('queued','running','completed','failed','cancelled','interrupted')),"
            "result_json TEXT,"
            "error_code TEXT,"
            "parent_job_id TEXT REFERENCES comparison_jobs(job_id),"
            "created_at TEXT NOT NULL,"
            "updated_at TEXT NOT NULL,"
            "CHECK((status = 'completed' AND result_json IS NOT NULL AND error_code IS NULL) OR "
            "(status IN ('failed','cancelled','interrupted') AND result_json IS NULL AND error_code IS NOT NULL) OR "
            "(status IN ('queued','running') AND result_json IS NULL AND error_code IS NULL))"
            ")"
        )
        connection.execute(
            "CREATE UNIQUE INDEX comparison_jobs_one_active "
            "ON comparison_jobs((1)) WHERE status IN ('queued','running')"
        )
        connection.execute(
            "CREATE INDEX comparison_jobs_by_case "
            "ON comparison_jobs(case_id, created_at, job_id)"
        )
        connection.executemany(
            "INSERT INTO comparison_meta(key, value) VALUES(?, ?)",
            (("scope", self._scope_json), ("schema", str(_SCHEMA_VERSION))),
        )

    def _verify_schema_and_owner(self, connection: sqlite3.Connection) -> None:
        try:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            objects = {
                (row[0], row[1])
                for row in connection.execute(
                    "SELECT type, name FROM sqlite_master "
                    "WHERE name NOT LIKE 'sqlite_%' AND type IN ('table','index','trigger','view')"
                )
            }
            expected_objects = {
                ("table", "comparison_meta"),
                ("table", "comparison_jobs"),
                ("index", "comparison_jobs_one_active"),
                ("index", "comparison_jobs_by_case"),
            }
            if version != _SCHEMA_VERSION or objects != expected_objects:
                raise ComparisonStoreError("corrupt_store")
            meta_columns = [
                row[1] for row in connection.execute("PRAGMA table_info(comparison_meta)")
            ]
            job_columns = [
                row[1] for row in connection.execute("PRAGMA table_info(comparison_jobs)")
            ]
            if meta_columns != ["key", "value"] or job_columns != [
                "job_id",
                "comparison_session_id",
                "request_id",
                "case_id",
                "input_json",
                "input_digest",
                "status",
                "result_json",
                "error_code",
                "parent_job_id",
                "created_at",
                "updated_at",
            ]:
                raise ComparisonStoreError("corrupt_store")
            meta = {
                row["key"]: row["value"]
                for row in connection.execute("SELECT key, value FROM comparison_meta")
            }
            if set(meta) != {"scope", "schema"} or meta["schema"] != str(_SCHEMA_VERSION):
                raise ComparisonStoreError("corrupt_store")
            if meta["scope"] != self._scope_json:
                raise ComparisonStoreError("scope_mismatch")
        except ComparisonStoreError:
            raise
        except sqlite3.Error as exc:
            raise _safe_sqlite_error(exc) from None

    def _validate_input(self, payload: object) -> tuple[dict[str, Any], str, str]:
        if type(payload) is not dict or set(payload) != _INPUT_FIELDS:
            raise ComparisonStoreError("invalid_input")
        try:
            frozen, encoded = _canonical_json(payload)
        except OverflowError:
            raise ComparisonStoreError("input_too_large") from None
        except (TypeError, ValueError, RecursionError, UnicodeError):
            raise ComparisonStoreError("invalid_input") from None

        for name in ("caseId", "sourceSessionId"):
            if not _valid_hex(frozen[name], _ID_RE):
                raise ComparisonStoreError("invalid_input")
        for name in ("implementationHash", "sourceDigest"):
            if not _valid_hex(frozen[name], _SHA_RE):
                raise ComparisonStoreError("invalid_input")
        if frozen["formulaVersion"] != FORMULA_VERSION:
            raise ComparisonStoreError("invalid_input")
        if type(frozen["weight"]) is not str or frozen["weight"] not in WEIGHTS:
            raise ComparisonStoreError("invalid_input")
        if type(frozen["pageStart"]) is not int or frozen["pageStart"] < 0:
            raise ComparisonStoreError("invalid_input")

        try:
            snapshot = ContextSnapshot.from_payload(frozen["contextSnapshot"])
        except (ContextError, TypeError, ValueError, AttributeError, RecursionError):
            raise ComparisonStoreError("invalid_input") from None
        snapshot_payload = snapshot.payload()
        if snapshot_payload.get("scope") != self.scope.to_dict():
            raise ComparisonStoreError("scope_mismatch")
        if frozen["caseId"] != snapshot_payload["caseId"]:
            raise ComparisonStoreError("invalid_input")

        catalog = frozen["catalog"]
        if type(catalog) is not dict or set(catalog) != {"name", "sha256", "content"}:
            raise ComparisonStoreError("invalid_input")
        name, catalog_hash, content = (catalog[key] for key in ("name", "sha256", "content"))
        if (
            type(name) is not str
            or _CATALOG_NAME_RE.fullmatch(name) is None
            or name in (".txt", "..txt")
            or not _valid_hex(catalog_hash, _SHA_RE)
            or type(content) is not str
        ):
            raise ComparisonStoreError("invalid_input")
        try:
            content_bytes = content.encode("utf-8")
        except UnicodeError:
            raise ComparisonStoreError("invalid_input") from None
        if len(content_bytes) > _MAX_CATALOG_BYTES:
            raise ComparisonStoreError("invalid_input")
        if hashlib.sha256(content_bytes).hexdigest() != catalog_hash:
            raise ComparisonStoreError("invalid_input")

        rates = frozen["rates"]
        subset = frozen["originalSubset"]
        provenance = frozen["originalProvenance"]
        if (
            type(rates) is not list
            or not 1 <= len(rates) <= _MAX_RATES
            or type(subset) is not list
            or len(subset) != len(rates)
            or type(provenance) is not dict
        ):
            raise ComparisonStoreError("invalid_input")
        catalog_names = {
            line.partition("\t")[0]
            for line in content.splitlines()
            if line.strip()
        }
        for index, rate_name in enumerate(rates):
            if (
                type(rate_name) is not str
                or not 1 <= len(rate_name) <= 2048
                or not rate_name.strip()
                or rate_name not in catalog_names
            ):
                raise ComparisonStoreError("invalid_input")
            rate = subset[index]
            if type(rate) is not dict or set(rate) != _RATE_FIELDS:
                raise ComparisonStoreError("invalid_input")
            if (
                type(rate["nameOrRate"]) is not str
                or rate["nameOrRate"] != rate_name
                or any(
                    type(rate[field]) is not int
                    for field in (
                        "energeticValue",
                        "gv",
                        "recurring",
                        "recurringGeneralVitality",
                        "level",
                        "resonateCounter",
                    )
                )
                or (rate["url"] is not None and type(rate["url"]) is not str)
                or (rate["potency"] is not None and type(rate["potency"]) is not str)
            ):
                raise ComparisonStoreError("invalid_input")

        digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        return frozen, encoded, digest

    def _validate_result(
        self, payload: dict[str, Any], result: object
    ) -> tuple[dict[str, Any], str]:
        try:
            frozen, encoded = _canonical_json(result)
        except OverflowError:
            raise ComparisonStoreError("invalid_result") from None
        except (TypeError, ValueError, RecursionError, UnicodeError):
            raise ComparisonStoreError("invalid_result") from None
        if type(frozen) is not dict or set(frozen) != _RESULT_FIELDS:
            raise ComparisonStoreError("invalid_result")

        claimed_digest = frozen.get("resultDigest")
        if not _valid_hex(claimed_digest, _SHA_RE):
            raise ComparisonStoreError("invalid_result")
        unsigned = {key: value for key, value in frozen.items() if key != "resultDigest"}
        if document_digest(unsigned) != claimed_digest:
            raise ComparisonStoreError("invalid_result")

        snapshot = payload["contextSnapshot"]
        if (
            frozen["formulaVersion"] != FORMULA_VERSION
            or frozen["formulaVersion"] != payload["formulaVersion"]
            or frozen["caseId"] != payload["caseId"]
            or type(frozen["contextVersion"]) is not int
            or frozen["contextVersion"] != snapshot["contextVersion"]
            or frozen["contextDigest"] != snapshot["digest"]
            or frozen["inputRates"] != payload["rates"]
        ):
            raise ComparisonStoreError("invalid_result")

        try:
            expected_prepared = prepare_catalog_context(snapshot, payload["catalog"])
        except (MatrixError, ExperimentalContextError, TypeError, ValueError, AttributeError):
            raise ComparisonStoreError("invalid_result") from None
        if frozen["preparedContext"] != expected_prepared:
            raise ComparisonStoreError("invalid_result")
        if frozen["catalog"] != expected_prepared["catalog"]:
            raise ComparisonStoreError("invalid_result")
        expected_hashes = {
            **expected_prepared["sourceHashes"],
            "Radi144/app/algorithms/resonance_engine.py": ENGINE_SHA256,
            "Radi144/app/api/resonance.py": ROUTES_SHA256,
        }
        if frozen["sourceHashes"] != expected_hashes:
            raise ComparisonStoreError("invalid_result")

        parameters = frozen["parameters"]
        if type(parameters) is not dict or set(parameters) != _PARAMETER_FIELDS:
            raise ComparisonStoreError("invalid_result")
        expected_parameters = {
            "backend": "cpu",
            "dtype": "float32",
            "matrixSize": 12,
            "embedDimension": 256,
            "candidateCount": 80000,
            "purpose": "product-cpu",
            "threads": 1,
            "focusWeight": payload["weight"],
            "focusWeightValue": WEIGHTS[payload["weight"]],
            "rng": "local-torch-generators",
            "topK": 10,
            "torchVersion": "2.12.0+cpu",
            "numpyVersion": "2.4.6",
            "platform": "Windows",
            "bioEnabled": False,
            "hrvEnabled": False,
            "emfEnabled": False,
            "quantumEnabled": False,
            "symmetry": "none",
            "clockEnabled": False,
            "numericImageEnabled": False,
            "rateScope": "explicit-bound-subset",
            "maximumRates": _MAX_RATES,
        }
        if any(parameters.get(key) != value for key, value in expected_parameters.items()):
            raise ComparisonStoreError("invalid_result")
        if any(type(parameters[key]) is not type(value) for key, value in expected_parameters.items()):
            raise ComparisonStoreError("invalid_result")
        if (
            type(parameters["pythonVersion"]) is not str
            or re.fullmatch(r"3\.13\.\d+", parameters["pythonVersion"]) is None
        ):
            raise ComparisonStoreError("invalid_result")

        results = frozen["results"]
        if type(results) is not list or len(results) != len(payload["rates"]):
            raise ComparisonStoreError("invalid_result")
        seen_indices: set[int] = set()
        for row in results:
            if type(row) is not dict or set(row) != {
                "rate",
                "originalIndex",
                "score",
                "intensity",
                "matrix",
            }:
                raise ComparisonStoreError("invalid_result")
            index = row["originalIndex"]
            if (
                type(index) is not int
                or not 0 <= index < len(payload["rates"])
                or index in seen_indices
                or row["rate"] != payload["rates"][index]
                or type(row["rate"]) is not str
            ):
                raise ComparisonStoreError("invalid_result")
            seen_indices.add(index)
            score, intensity = row["score"], row["intensity"]
            if (
                type(score) is not float
                or not math.isfinite(score)
                or not -1.0 <= score <= 1.0
                or type(intensity) is not float
                or not math.isfinite(intensity)
                or intensity < 0
            ):
                raise ComparisonStoreError("invalid_result")
            matrix = row["matrix"]
            if (
                type(matrix) is not list
                or len(matrix) != 12
                or any(type(line) is not list or len(line) != 12 for line in matrix)
                or any(
                    type(cell) is not int or not 0 <= cell <= 9
                    for line in matrix
                    for cell in line
                )
            ):
                raise ComparisonStoreError("invalid_result")
        if seen_indices != set(range(len(payload["rates"]))):
            raise ComparisonStoreError("invalid_result")
        return frozen, encoded

    def _load_json(self, raw: object) -> dict[str, Any]:
        if type(raw) is not str:
            raise ComparisonStoreError("corrupt_record")
        try:
            value = json.loads(raw)
            _, canonical = _canonical_json(value)
        except (TypeError, ValueError, OverflowError, RecursionError, UnicodeError):
            raise ComparisonStoreError("corrupt_record") from None
        if canonical != raw or type(value) is not dict:
            raise ComparisonStoreError("corrupt_record")
        return value

    def _row_record(self, row: sqlite3.Row | None) -> dict[str, Any]:
        if row is None:
            raise ComparisonStoreError("not_found")
        try:
            for field in ("job_id", "comparison_session_id", "request_id"):
                if not _valid_hex(row[field], _ID_RE):
                    raise ComparisonStoreError("corrupt_record")
            if row["parent_job_id"] is not None and not _valid_hex(row["parent_job_id"], _ID_RE):
                raise ComparisonStoreError("corrupt_record")
            if row["status"] not in _VALID_STATUSES:
                raise ComparisonStoreError("corrupt_record")

            raw_input = row["input_json"]
            payload = self._load_json(raw_input)
            try:
                validated, canonical, digest = self._validate_input(payload)
            except ComparisonStoreError:
                raise ComparisonStoreError("corrupt_record") from None
            if canonical != raw_input or digest != row["input_digest"] or validated["caseId"] != row["case_id"]:
                raise ComparisonStoreError("corrupt_record")

            result = None
            if row["result_json"] is not None:
                raw_result = row["result_json"]
                stored_result = self._load_json(raw_result)
                try:
                    result, canonical_result = self._validate_result(payload, stored_result)
                except ComparisonStoreError:
                    raise ComparisonStoreError("corrupt_record") from None
                if canonical_result != raw_result:
                    raise ComparisonStoreError("corrupt_record")

            error_code = row["error_code"]
            if row["status"] == "completed":
                if result is None or error_code is not None:
                    raise ComparisonStoreError("corrupt_record")
            elif row["status"] in ("failed", "cancelled", "interrupted"):
                if result is not None or error_code not in _STORED_ERROR_CODES:
                    raise ComparisonStoreError("corrupt_record")
            elif result is not None or error_code is not None:
                raise ComparisonStoreError("corrupt_record")

            return {
                "id": row["job_id"],
                "comparisonSessionId": row["comparison_session_id"],
                "scope": self.scope.to_dict(),
                "requestId": row["request_id"],
                "input": copy.deepcopy(validated),
                "inputDigest": digest,
                "status": row["status"],
                "result": copy.deepcopy(result),
                "error": {"code": error_code} if error_code is not None else None,
                "parentJobId": row["parent_job_id"],
                "createdAt": row["created_at"],
                "updatedAt": row["updated_at"],
            }
        except ComparisonStoreError:
            raise
        except (KeyError, TypeError, ValueError, RecursionError):
            raise ComparisonStoreError("corrupt_record") from None

    def _select_job(self, connection: sqlite3.Connection, job_id: str) -> dict[str, Any]:
        row = connection.execute(
            "SELECT * FROM comparison_jobs WHERE job_id = ?", (job_id,)
        ).fetchone()
        return self._row_record(row)

    def _active_exists(self, connection: sqlite3.Connection) -> bool:
        return connection.execute(
            "SELECT 1 FROM comparison_jobs WHERE status IN ('queued','running') LIMIT 1"
        ).fetchone() is not None

    def _parent_available(self, connection: sqlite3.Connection, parent_job_id: str) -> None:
        parent = self._select_job(connection, parent_job_id)
        if parent["status"] not in _RETRYABLE_STATUSES:
            raise ComparisonStoreError("not_retryable")

    def _insert_job(
        self,
        connection: sqlite3.Connection,
        request_id: str,
        payload: dict[str, Any],
        encoded: str,
        digest: str,
        parent_job_id: str | None,
    ) -> dict[str, Any]:
        job_id = uuid.uuid4().hex
        session_id = uuid.uuid4().hex
        timestamp = _now()
        connection.execute(
            "INSERT INTO comparison_jobs("
            "job_id, comparison_session_id, request_id, case_id, input_json, input_digest, "
            "status, result_json, error_code, parent_job_id, created_at, updated_at"
            ") VALUES(?, ?, ?, ?, ?, ?, 'queued', NULL, NULL, ?, ?, ?)",
            (
                job_id,
                session_id,
                request_id,
                payload["caseId"],
                encoded,
                digest,
                parent_job_id,
                timestamp,
                timestamp,
            ),
        )
        return self._select_job(connection, job_id)

    def create(
        self,
        request_id: str,
        payload: dict[str, Any],
        parent_job_id: str | None = None,
    ) -> dict[str, Any]:
        if not _valid_hex(request_id, _ID_RE):
            raise ComparisonStoreError("invalid_id")
        if parent_job_id is not None and not _valid_hex(parent_job_id, _ID_RE):
            raise ComparisonStoreError("invalid_id")
        frozen, encoded, digest = self._validate_input(payload)
        with self._transaction(write=True) as connection:
            existing_row = connection.execute(
                "SELECT * FROM comparison_jobs WHERE request_id = ?", (request_id,)
            ).fetchone()
            if existing_row is not None:
                existing = self._row_record(existing_row)
                if existing["inputDigest"] != digest or existing["parentJobId"] != parent_job_id:
                    raise ComparisonStoreError("idempotency_conflict")
                return existing
            if parent_job_id is not None:
                self._parent_available(connection, parent_job_id)
            if self._active_exists(connection):
                raise ComparisonStoreError("busy")
            return self._insert_job(connection, request_id, frozen, encoded, digest, parent_job_id)

    def get(self, job_id: str) -> dict[str, Any]:
        if not _valid_hex(job_id, _ID_RE):
            raise ComparisonStoreError("invalid_id")
        with self._transaction(write=False) as connection:
            return self._select_job(connection, job_id)

    def has_pending(self) -> bool:
        with self._transaction(write=False) as connection:
            return self._active_exists(connection)

    def list_for_case(self, case_id: str) -> list[dict[str, Any]]:
        if not _valid_hex(case_id, _ID_RE):
            raise ComparisonStoreError("invalid_id")
        with self._transaction(write=False) as connection:
            rows = connection.execute(
                "SELECT * FROM comparison_jobs WHERE case_id = ? ORDER BY created_at, job_id",
                (case_id,),
            ).fetchall()
            return [self._row_record(row) for row in rows]

    def claim(self, job_id: str) -> dict[str, Any]:
        if not _valid_hex(job_id, _ID_RE):
            raise ComparisonStoreError("invalid_id")
        with self._transaction(write=True) as connection:
            current = self._select_job(connection, job_id)
            if current["status"] != "queued":
                code = (
                    "terminal"
                    if current["status"] in _RETRYABLE_STATUSES | {"completed", "cancelled"}
                    else "invalid_transition"
                )
                raise ComparisonStoreError(code)
            connection.execute(
                "UPDATE comparison_jobs SET status = 'running', updated_at = ? "
                "WHERE job_id = ? AND status = 'queued'",
                (_now(), job_id),
            )
            return self._select_job(connection, job_id)

    def finish(self, job_id: str, result: dict[str, Any]) -> dict[str, Any]:
        if not _valid_hex(job_id, _ID_RE):
            raise ComparisonStoreError("invalid_id")
        with self._transaction(write=True) as connection:
            current = self._select_job(connection, job_id)
            if current["status"] != "running":
                code = (
                    "terminal"
                    if current["status"] in _VALID_STATUSES - {"queued", "running"}
                    else "invalid_transition"
                )
                raise ComparisonStoreError(code)
            _, encoded = self._validate_result(current["input"], result)
            connection.execute(
                "UPDATE comparison_jobs SET status = 'completed', result_json = ?, "
                "error_code = NULL, updated_at = ? WHERE job_id = ? AND status = 'running'",
                (encoded, _now(), job_id),
            )
            return self._select_job(connection, job_id)

    def fail(self, job_id: str, code: str) -> dict[str, Any]:
        if not _valid_hex(job_id, _ID_RE):
            raise ComparisonStoreError("invalid_id")
        if type(code) is not str or code not in _STORED_ERROR_CODES - {"cancelled"}:
            raise ComparisonStoreError("invalid_error_code")
        with self._transaction(write=True) as connection:
            current = self._select_job(connection, job_id)
            if current["status"] != "running":
                state_code = (
                    "terminal"
                    if current["status"] in _VALID_STATUSES - {"queued", "running"}
                    else "invalid_transition"
                )
                raise ComparisonStoreError(state_code)
            connection.execute(
                "UPDATE comparison_jobs SET status = 'failed', result_json = NULL, "
                "error_code = ?, updated_at = ? WHERE job_id = ? AND status = 'running'",
                (code, _now(), job_id),
            )
            return self._select_job(connection, job_id)

    def cancel(self, job_id: str) -> dict[str, Any]:
        if not _valid_hex(job_id, _ID_RE):
            raise ComparisonStoreError("invalid_id")
        with self._transaction(write=True) as connection:
            current = self._select_job(connection, job_id)
            if current["status"] == "cancelled":
                return current
            if current["status"] not in _ACTIVE_STATUSES:
                code = (
                    "terminal"
                    if current["status"] in _VALID_STATUSES - set(_ACTIVE_STATUSES)
                    else "invalid_transition"
                )
                raise ComparisonStoreError(code)
            connection.execute(
                "UPDATE comparison_jobs SET status = 'cancelled', result_json = NULL, "
                "error_code = 'cancelled', updated_at = ? WHERE job_id = ? "
                "AND status IN ('queued','running')",
                (_now(), job_id),
            )
            return self._select_job(connection, job_id)

    def interrupt_pending(self) -> int:
        with self._transaction(write=True) as connection:
            cursor = connection.execute(
                "UPDATE comparison_jobs SET status = 'interrupted', result_json = NULL, "
                "error_code = 'interrupted', updated_at = ? "
                "WHERE status IN ('queued','running')",
                (_now(),),
            )
            return cursor.rowcount

    def retry(self, job_id: str, request_id: str) -> dict[str, Any]:
        if not _valid_hex(job_id, _ID_RE) or not _valid_hex(request_id, _ID_RE):
            raise ComparisonStoreError("invalid_id")
        with self._transaction(write=True) as connection:
            parent = self._select_job(connection, job_id)
            existing_row = connection.execute(
                "SELECT * FROM comparison_jobs WHERE request_id = ?", (request_id,)
            ).fetchone()
            if existing_row is not None:
                existing = self._row_record(existing_row)
                if (
                    existing["parentJobId"] != job_id
                    or existing["inputDigest"] != parent["inputDigest"]
                ):
                    raise ComparisonStoreError("idempotency_conflict")
                return existing
            if parent["status"] not in _RETRYABLE_STATUSES:
                raise ComparisonStoreError("not_retryable")
            if self._active_exists(connection):
                raise ComparisonStoreError("busy")
            encoded = json.dumps(
                parent["input"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
            return self._insert_job(
                connection, request_id, parent["input"], encoded, parent["inputDigest"], job_id
            )
