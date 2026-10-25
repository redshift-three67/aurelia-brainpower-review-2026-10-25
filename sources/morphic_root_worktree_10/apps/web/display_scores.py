from __future__ import annotations

from collections.abc import Sequence
from typing import Any


DISPLAY_SCORE_DECIMALS = 3
ADAPTIVE_RESULT_CAP = 5


def round_display_score(value: float | int) -> float:
    return round(float(value), DISPLAY_SCORE_DECIMALS)


def format_display_score(value: float | int) -> str:
    return f"{round_display_score(value):.{DISPLAY_SCORE_DECIMALS}f}"


def adaptive_result_limit(top_n: int, adaptive_limits: bool) -> int:
    normalized = max(1, int(top_n))
    if not adaptive_limits:
        return normalized
    return min(normalized, ADAPTIVE_RESULT_CAP)


def adaptive_section_limit(
    base_limit: int,
    top_n: int,
    adaptive_limits: bool,
    *,
    minimum: int = 1,
) -> int:
    normalized_base = max(minimum, int(base_limit))
    normalized_top_n = max(1, int(top_n))
    effective_top_n = adaptive_result_limit(normalized_top_n, adaptive_limits)
    if effective_top_n >= normalized_top_n:
        return normalized_base
    scaled = round(normalized_base * (effective_top_n / normalized_top_n))
    return max(minimum, min(normalized_base, scaled))


def limit_display_items(
    items: Sequence[Any], *, top_n: int, adaptive_limits: bool
) -> list[Any]:
    return list(items[: adaptive_result_limit(top_n, adaptive_limits)])


def normalize_display_payload(payload: Any, *, _parent_key: str | None = None) -> Any:
    if isinstance(payload, dict):
        return {
            key: normalize_display_payload(value, _parent_key=str(key))
            for key, value in payload.items()
        }
    if isinstance(payload, list):
        return [
            normalize_display_payload(value, _parent_key=_parent_key)
            for value in payload
        ]
    if isinstance(payload, tuple):
        return tuple(
            normalize_display_payload(value, _parent_key=_parent_key)
            for value in payload
        )
    if (
        _is_score_key(_parent_key)
        and isinstance(payload, (int, float))
        and not isinstance(payload, bool)
    ):
        return format_display_score(payload)
    return payload


def _is_score_key(key: str | None) -> bool:
    if not key:
        return False
    return "score" in key.casefold()
