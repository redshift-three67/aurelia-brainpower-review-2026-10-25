"""Group-vector candidates and explicit in-memory opt-in application.

This module has no persistence, web, CLI, report, trace, job, or manifest
dependency. The analysis service may consume a supplied, consent-verified
candidate; external product paths remain separately gated.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

import numpy as np


_CLIENT_ID = re.compile(r"^cli-[A-Za-z0-9_-]{1,124}$")


@dataclass(frozen=True)
class GroupMemberRates:
    client_id: str
    rates: np.ndarray
    consent_recorded: bool


@dataclass(frozen=True)
class GroupAnalysisOptIn:
    """Explicit in-memory group-analysis request, disabled by default."""

    enabled: bool = False
    centroid_rates: np.ndarray | None = None
    strength: float = 0.0
    consent_verified: bool = False
    activation_generation: str = ""


def build_group_centroid(members: Iterable[GroupMemberRates]) -> np.ndarray:
    """Return a deterministic centroid from at least two consented member vectors."""

    resolved = list(members)
    if len(resolved) < 2:
        raise ValueError("at least two group members are required")

    normalized: list[tuple[str, np.ndarray]] = []
    seen_ids: set[str] = set()
    expected_size: int | None = None
    for member in resolved:
        client_id = str(member.client_id or "").strip()
        if not _CLIENT_ID.fullmatch(client_id):
            raise ValueError("group member client_id must be pseudonymous and canonical")
        if client_id in seen_ids:
            raise ValueError("group member client_id must be unique")
        if member.consent_recorded is not True:
            raise ValueError("every group member requires explicit consent")
        try:
            rates = np.asarray(member.rates, dtype=float)
        except (TypeError, ValueError) as exc:
            raise ValueError("group member rates must be numeric") from exc
        if rates.ndim != 1 or rates.size == 0 or not np.isfinite(rates).all():
            raise ValueError("group member rates must be a finite one-dimensional vector")
        if expected_size is None:
            expected_size = rates.size
        elif rates.size != expected_size:
            raise ValueError("group member rate vectors must have equal length")
        seen_ids.add(client_id)
        normalized.append((client_id, rates))

    ordered_rates = [rates for _, rates in sorted(normalized, key=lambda entry: entry[0])]
    return np.mean(np.stack(ordered_rates, axis=0), axis=0, dtype=float)


def blend_group_centroid(
    baseline_rates: np.ndarray,
    centroid_rates: np.ndarray,
    *,
    strength: float,
) -> np.ndarray:
    """Return a pure, explicit interpolation candidate for later analysis gates."""

    try:
        baseline = np.asarray(baseline_rates, dtype=float)
        centroid = np.asarray(centroid_rates, dtype=float)
        resolved_strength = float(strength)
    except (TypeError, ValueError) as exc:
        raise ValueError("group blend inputs must be numeric") from exc
    if (
        baseline.ndim != 1
        or centroid.ndim != 1
        or baseline.size == 0
        or baseline.shape != centroid.shape
        or not np.isfinite(baseline).all()
        or not np.isfinite(centroid).all()
    ):
        raise ValueError("group blend vectors must be finite, one-dimensional, and equally sized")
    if not np.isfinite(resolved_strength) or not 0.0 <= resolved_strength <= 1.0:
        raise ValueError("group blend strength must be finite and within [0.0, 1.0]")
    if resolved_strength == 0.0:
        return baseline.copy()
    return baseline + resolved_strength * (centroid - baseline)


def apply_group_opt_in(
    baseline_rates: np.ndarray,
    group_opt_in: GroupAnalysisOptIn | None,
) -> np.ndarray:
    """Apply a consent-verified group candidate, or copy the default baseline."""

    if group_opt_in is None or group_opt_in.enabled is not True:
        return np.asarray(baseline_rates, dtype=float).copy()
    if group_opt_in.consent_verified is not True:
        raise ValueError("group analysis requires verified member consent")
    if group_opt_in.centroid_rates is None:
        raise ValueError("group analysis requires a centroid candidate")
    return blend_group_centroid(
        baseline_rates,
        group_opt_in.centroid_rates,
        strength=group_opt_in.strength,
    )
