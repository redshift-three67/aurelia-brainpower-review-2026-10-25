"""Pure, deterministic EXP1-B scalar preparation for an immutable context snapshot."""
from __future__ import annotations

import hashlib
from datetime import date
from typing import Any

from .personal_context import ContextError, ContextSnapshot


FORMULA_VERSION = "radi144-scalar-input-v1"
SOURCE_SHA256 = "3146960a23041cca959befd85882888fc3f896fe3b9a4eb83916b85aec859894"
_SOURCE_PATH = "Radi144/app/algorithms/client_signature.py"
_NAME_WEIGHT = 0.15
_BIRTH_WEIGHT = 0.20
_TEXT_MODULUS = 1000.0
_BIRTH_BASE_MULTIPLIER = 0.6
_BIRTH_PLACE_MULTIPLIER = 0.3
_BIRTH_PLACE_DIVISOR = 65.535


class ExperimentalContextError(ValueError):
    """Raised when an input snapshot or scalar basis is unavailable."""


def _validated_payload(snapshot: object) -> dict[str, Any]:
    try:
        raw = snapshot.payload() if isinstance(snapshot, ContextSnapshot) else snapshot
        return ContextSnapshot.from_payload(raw).payload()
    except (ContextError, TypeError, ValueError, AttributeError) as exc:
        raise ExperimentalContextError("Kontext-Snapshot ist ungültig.") from exc


def _text_to_frequency(text: str) -> float:
    lowered = text.lower()
    numerology = sum(ord(char) for char in lowered if char.isalpha())
    vowels = {"a": 440, "e": 330, "i": 550, "o": 220, "u": 165}
    phonetic = sum(
        vowels[char] if char in vowels else ord(char) * 2.0 if char.isalpha() else 0.0
        for char in lowered
    )
    return ((numerology + phonetic) / 2.0) % _TEXT_MODULUS


def _julian_day(date_text: str) -> float:
    parsed = date.fromisoformat(date_text)
    a = (14 - parsed.month) // 12
    year = parsed.year + 4800 - a
    month = parsed.month + 12 * a - 3
    jdn = (
        parsed.day
        + (153 * month + 2) // 5
        + 365 * year
        + year // 4
        - year // 100
        + year // 400
        - 32045
    )
    return float(jdn)


def _birth_frequency(birth_date: str, place: str | None, place_kind: str | None) -> float:
    base_frequency = _julian_day(birth_date) % _TEXT_MODULUS
    place_modulation = 0.0
    if place_kind == "birth" and place:
        place_hash = hashlib.md5(place.lower().strip().encode()).hexdigest()
        place_modulation = int(place_hash[:4], 16) / _BIRTH_PLACE_DIVISOR
    return (
        base_frequency * _BIRTH_BASE_MULTIPLIER
        + place_modulation * _BIRTH_PLACE_MULTIPLIER
    ) % _TEXT_MODULUS


def prepare_experimental_context(snapshot: object) -> dict[str, Any]:
    """Validate a snapshot and return only the approved deterministic scalar inputs."""
    payload = _validated_payload(snapshot)
    context = payload["context"]
    personal = context["personal"]

    components: dict[str, float] = {}
    weights: dict[str, float] = {}

    first_name = personal.get("firstName") or ""
    last_name = personal.get("lastName") or ""
    if first_name or last_name:
        components["name"] = _text_to_frequency(f"{first_name} {last_name}")
        weights["name"] = _NAME_WEIGHT

    birth_date = personal.get("birthDate")
    if birth_date:
        components["birth"] = _birth_frequency(
            birth_date,
            personal.get("place"),
            personal.get("placeKind"),
        )
        weights["birth"] = _BIRTH_WEIGHT

    total_weight = sum(weights.values())
    if not total_weight:
        raise ExperimentalContextError("Name oder Geburtsdatum fehlt als Skalarbasis.")

    frequency = sum(components[name] * weights[name] for name in components) / total_weight
    place_is_birth_scalar = (
        bool(birth_date) and personal.get("placeKind") == "birth" and bool(personal.get("place"))
    )
    image_use = "context-only" if personal.get("image") is not None else "not-provided"

    return {
        "formulaVersion": FORMULA_VERSION,
        "sourceHashes": {_SOURCE_PATH: SOURCE_SHA256},
        "contextDigest": payload["digest"],
        "contextVersion": payload["contextVersion"],
        "caseId": payload["caseId"],
        "signature": {
            "frequency": frequency,
            "components": components,
            "weights": weights,
        },
        "placeUse": "birth-scalar" if place_is_birth_scalar else "context-only",
        "imageUse": image_use,
        "focusUse": "requires-catalog-match",
        "parameters": {
            "nameWeight": _NAME_WEIGHT,
            "birthWeight": _BIRTH_WEIGHT,
            "textModulo": _TEXT_MODULUS,
            "birthJdnModulo": _TEXT_MODULUS,
            "birthBaseMultiplier": _BIRTH_BASE_MULTIPLIER,
            "birthPlaceMultiplier": _BIRTH_PLACE_MULTIPLIER,
            "birthPlaceDivisor": _BIRTH_PLACE_DIVISOR,
            "birthTimeMultiplier": 0.0,
            "availableWeightNormalization": "weighted-mean",
            "placeKindRequiredForBirthScalar": True,
            "organClockEnabled": False,
            "planetaryEnabled": False,
            "emfEnabled": False,
            "hrvEnabled": False,
            "imageSignatureEnabled": False,
            "focusVectorizationEnabled": False,
        },
    }
