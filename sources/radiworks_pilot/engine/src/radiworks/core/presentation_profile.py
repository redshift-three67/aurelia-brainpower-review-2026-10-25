"""Versioned, case-scoped presentation metadata and content-addressed PNGs."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import threading
from pathlib import Path

from ..persistence import atomic_json_replace, document_digest
from ..scope import ScopeContext
from .context_images import ContextImageError, ContextImageStore

LEGACY_AUDIO_PROFILE_IDS = (
    "original",
    "off",
    "fixed-432",
    "fixed-528",
    "fixed-42962",
    "solfeggio-9",
    "pink",
)
PULSE_PROFILE_IDS = (
    "pink-pulse-v1",
    "pink-phi-v1",
    "pink-fibonacci-v1",
)
PULSE_STAGE_SECONDS_LIMITS = {
    "pink-pulse-v1": 600,
    "pink-phi-v1": 87,
    "pink-fibonacci-v1": 46,
}
AUDIO_PROFILE_IDS = LEGACY_AUDIO_PROFILE_IDS + PULSE_PROFILE_IDS
DEFAULT_AUDIO_PROFILE = "original"
DEFAULT_STAGE_SECONDS = 60
PROFILE_SCHEMA_VERSION = 1
PULSE_PROFILE_SCHEMA_VERSION = 2
PRESENTATION_SCHEMA_VERSION = 1
_CASE_ID = re.compile(r"[0-9a-f]{32}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_PROFILE_V1_KEYS = {
    "schemaVersion", "caseId", "version", "audioProfile",
    "stageSeconds", "repeat", "images", "digest",
}
_PROFILE_V2_KEYS = _PROFILE_V1_KEYS | {"modulationDepthPercent"}
_PROFILE_KEYS = _PROFILE_V1_KEYS
_PRESENTATION_KEYS = {
    "schemaVersion", "broadcastId", "targetDigest", "profile", "digest",
}


class PresentationProfileError(ValueError):
    def __init__(self, message: str, code: str = "invalid_profile"):
        super().__init__(message)
        self.code = code


def _is_junction(path: Path) -> bool:
    return bool(hasattr(path, "is_junction") and path.is_junction())


def _scope_hash(scope: ScopeContext) -> str:
    payload = json.dumps(
        scope.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def default_profile(case_id: str | None) -> dict:
    profile = {
        "schemaVersion": PROFILE_SCHEMA_VERSION,
        "caseId": case_id,
        "version": 0,
        "audioProfile": DEFAULT_AUDIO_PROFILE,
        "stageSeconds": DEFAULT_STAGE_SECONDS,
        "repeat": False,
        "images": [],
    }
    profile["digest"] = document_digest(profile)
    return profile


def validate_profile_payload(value: object) -> dict:
    if type(value) is not dict:
        raise PresentationProfileError("Präsentationsprofil hat ein ungültiges Schema.")
    schema_version = value.get("schemaVersion")
    if type(schema_version) is not int or schema_version not in (
        PROFILE_SCHEMA_VERSION, PULSE_PROFILE_SCHEMA_VERSION,
    ):
        raise PresentationProfileError("Präsentationsprofilversion ist ungültig.")
    profile_keys = _PROFILE_V1_KEYS if schema_version == PROFILE_SCHEMA_VERSION else _PROFILE_V2_KEYS
    if set(value) != profile_keys:
        raise PresentationProfileError("Präsentationsprofil hat ein ungültiges Schema.")
    case_id = value["caseId"]
    if case_id is not None and (type(case_id) is not str or not _CASE_ID.fullmatch(case_id)):
        raise PresentationProfileError("Präsentationsprofil-Fallbindung ist ungültig.")
    if type(value["version"]) is not int or value["version"] < 0:
        raise PresentationProfileError("Präsentationsprofilzähler ist ungültig.")
    audio_profile = value["audioProfile"]
    if type(audio_profile) is not str:
        raise PresentationProfileError("Audio-Profil ist nicht zulässig.")
    allowed_profiles = (
        LEGACY_AUDIO_PROFILE_IDS
        if schema_version == PROFILE_SCHEMA_VERSION
        else PULSE_PROFILE_IDS
    )
    if audio_profile not in allowed_profiles:
        raise PresentationProfileError("Audio-Profil passt nicht zur Präsentationsprofilversion.")
    stage_limit = PULSE_STAGE_SECONDS_LIMITS.get(audio_profile, 600)
    if (type(value["stageSeconds"]) is not int
            or not 1 <= value["stageSeconds"] <= stage_limit):
        raise PresentationProfileError("Stufendauer überschreitet die zulässige Profilgrenze.")
    if schema_version == PULSE_PROFILE_SCHEMA_VERSION:
        depth = value["modulationDepthPercent"]
        if type(depth) is not int or not 0 <= depth <= 100:
            raise PresentationProfileError("Modulationstiefe muss eine ganze Zahl zwischen 0 und 100 sein.")
    if type(value["repeat"]) is not bool:
        raise PresentationProfileError("Wiederholung muss boolesch sein.")
    images = value["images"]
    if type(images) is not list or len(images) > 5:
        raise PresentationProfileError("Es sind höchstens fünf Präsentationsbilder zulässig.")
    if any(type(image) is not str or not _SHA256.fullmatch(image) for image in images):
        raise PresentationProfileError("Präsentationsbild-Verweis ist ungültig.")
    body = {key: copy.deepcopy(value[key]) for key in profile_keys if key != "digest"}
    if type(value["digest"]) is not str or value["digest"] != document_digest(body):
        raise PresentationProfileError("Präsentationsprofil-Prüfsumme stimmt nicht.")
    return copy.deepcopy(value)


def make_presentation_receipt(profile: dict, broadcast_id: str, target_digest: str) -> dict:
    frozen_profile = validate_profile_payload(profile)
    receipt = {
        "schemaVersion": PRESENTATION_SCHEMA_VERSION,
        "broadcastId": broadcast_id,
        "targetDigest": target_digest,
        "profile": frozen_profile,
    }
    receipt["digest"] = document_digest(receipt)
    return receipt


def validate_presentation_receipt(value: object, *, broadcast_id: str, target: dict) -> dict:
    if type(value) is not dict or set(value) != _PRESENTATION_KEYS:
        raise PresentationProfileError("Präsentationsbeleg hat ein ungültiges Schema.")
    if type(value["schemaVersion"]) is not int or value["schemaVersion"] != PRESENTATION_SCHEMA_VERSION:
        raise PresentationProfileError("Präsentationsbelegversion ist ungültig.")
    if value["broadcastId"] != broadcast_id or value["targetDigest"] != target.get("digest"):
        raise PresentationProfileError("Präsentationsbeleg gehört zu einem anderen Broadcastziel.")
    profile = validate_profile_payload(value["profile"])
    snapshot = target.get("contextSnapshot")
    if profile["caseId"] is None:
        if target.get("binding") == "bound":
            raise PresentationProfileError("Fallgebundener Broadcast braucht ein fallgebundenes Präsentationsprofil.")
    elif (
        target.get("binding") != "bound"
        or type(snapshot) is not dict
        or profile["caseId"] != snapshot.get("caseId")
    ):
        raise PresentationProfileError("Präsentationsprofil gehört zu einem anderen Fall.")
    body = {key: copy.deepcopy(value[key]) for key in _PRESENTATION_KEYS if key != "digest"}
    if type(value["digest"]) is not str or value["digest"] != document_digest(body):
        raise PresentationProfileError("Präsentationsbeleg-Prüfsumme stimmt nicht.")
    return copy.deepcopy(value)


class PresentationImageStore(ContextImageStore):
    """The context-image validator and safe content store in a separate namespace."""

    def __init__(self, cases_dir: Path, scope: ScopeContext):
        super().__init__(cases_dir, scope, namespace="presentation-images")


class PresentationProfileStore:
    """CAS-versioned presentation profile, isolated by scope and stable case ID."""

    def __init__(self, cases_dir: Path, scope: ScopeContext):
        self.base = Path(cases_dir).resolve()
        self.scope = scope
        self.scope_hash = _scope_hash(scope)
        self.images = PresentationImageStore(self.base, scope)
        self._lock = threading.RLock()

    def _directory(self, create: bool) -> Path:
        root = self.base / "presentation-profiles"
        directory = root / self.scope_hash
        for path in (root, directory):
            if path.is_symlink() or _is_junction(path):
                raise PresentationProfileError("Die lokale Profilablage ist nicht sicher erreichbar.", "store_unavailable")
            if not path.resolve().is_relative_to(self.base):
                raise PresentationProfileError("Die lokale Profilablage ist nicht sicher erreichbar.", "store_unavailable")
        if create:
            directory.mkdir(parents=True, exist_ok=True)
        return directory

    def _path(self, case_id: str, create: bool = False) -> Path:
        if type(case_id) is not str or not _CASE_ID.fullmatch(case_id):
            raise PresentationProfileError("Stabile Fall-ID ist ungültig.")
        path = self._directory(create) / (case_id + ".json")
        if path.is_symlink() or _is_junction(path) or not path.resolve().is_relative_to(self.base):
            raise PresentationProfileError("Die lokale Profilablage ist nicht sicher erreichbar.", "store_unavailable")
        return path

    def _load(self, case_id: str) -> dict:
        path = self._path(case_id)
        if not path.exists():
            return default_profile(case_id)
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            raise PresentationProfileError("Präsentationsprofil ist nicht sicher lesbar.", "profile_corrupt") from exc
        if type(record) is not dict:
            raise PresentationProfileError("Gespeichertes Präsentationsprofil hat ein unbekanntes Schema.", "profile_corrupt")
        schema_version = record.get("schemaVersion")
        if type(schema_version) is not int or schema_version not in (
            PROFILE_SCHEMA_VERSION, PULSE_PROFILE_SCHEMA_VERSION,
        ):
            raise PresentationProfileError("Gespeichertes Präsentationsprofil hat ein unbekanntes Schema.", "profile_corrupt")
        profile_keys = _PROFILE_V1_KEYS if schema_version == PROFILE_SCHEMA_VERSION else _PROFILE_V2_KEYS
        if set(record) != profile_keys | {"scopeHash"}:
            raise PresentationProfileError("Gespeichertes Präsentationsprofil hat ein unbekanntes Schema.", "profile_corrupt")
        if record.get("scopeHash") != self.scope_hash:
            raise PresentationProfileError("Präsentationsprofil gehört zu einem anderen Scope.", "profile_corrupt")
        profile = {key: copy.deepcopy(record[key]) for key in profile_keys}
        try:
            profile = validate_profile_payload(profile)
        except PresentationProfileError as exc:
            raise PresentationProfileError("Gespeichertes Präsentationsprofil ist ungültig.", "profile_corrupt") from exc
        if profile["caseId"] != case_id:
            raise PresentationProfileError("Präsentationsprofil ist an eine andere Fall-ID gebunden.", "profile_corrupt")
        return profile

    def _check_images(self, profile: dict) -> None:
        for reference in profile["images"]:
            try:
                self.images.get(reference)
            except (OSError, ContextImageError) as exc:
                raise PresentationProfileError(
                    "Ein gespeichertes Präsentationsbild ist nicht verfügbar.",
                    "image_unavailable",
                ) from exc

    def get(self, case_id: str) -> dict:
        with self._lock:
            profile = self._load(case_id)
            self._check_images(profile)
            return copy.deepcopy(profile)

    def update(
        self,
        *,
        case_id: str,
        expected_version: int,
        audio_profile: str,
        stage_seconds: int,
        repeat: bool,
        images: list[str],
        modulation_depth_percent: int | None = None,
    ) -> dict:
        if type(audio_profile) is not str or audio_profile not in AUDIO_PROFILE_IDS:
            raise PresentationProfileError("Präsentationsprofil-Eingaben sind ungültig.")
        is_pulse = audio_profile in PULSE_PROFILE_IDS
        stage_limit = PULSE_STAGE_SECONDS_LIMITS.get(audio_profile, 600)
        if (type(expected_version) is not int or expected_version < 0
                or type(stage_seconds) is not int or not 1 <= stage_seconds <= stage_limit
                or type(repeat) is not bool or type(images) is not list or len(images) > 5
                or any(type(image) is not str or not _SHA256.fullmatch(image) for image in images)
                or (is_pulse and (type(modulation_depth_percent) is not int
                                  or not 0 <= modulation_depth_percent <= 100))
                or (not is_pulse and modulation_depth_percent is not None)):
            raise PresentationProfileError("Präsentationsprofil-Eingaben sind ungültig.")
        with self._lock:
            previous = self._load(case_id)
            if previous["version"] != expected_version:
                raise PresentationProfileError(
                    "Präsentationsprofil wurde geändert. Bitte neu laden.",
                    "profile_conflict",
                )
            profile = {
                "schemaVersion": PULSE_PROFILE_SCHEMA_VERSION if is_pulse else PROFILE_SCHEMA_VERSION,
                "caseId": case_id,
                "version": expected_version + 1,
                "audioProfile": audio_profile,
                "stageSeconds": stage_seconds,
                "repeat": repeat,
                "images": copy.deepcopy(images),
            }
            if is_pulse:
                profile["modulationDepthPercent"] = modulation_depth_percent
            profile["digest"] = document_digest(profile)
            profile = validate_profile_payload(profile)
            self._check_images(profile)
            path = self._path(case_id, create=True)
            record = {**profile, "scopeHash": self.scope_hash}
            atomic_json_replace(path, record)
            return copy.deepcopy(profile)

    def put_image(self, data: bytes) -> dict:
        return self.images.put(data)

    def get_image(self, reference: str) -> bytes:
        return self.images.get(reference)

    def freeze_for_target(self, target: dict, broadcast_id: str) -> dict:
        if type(target) is not dict or target.get("scope") != self.scope.to_dict():
            raise PresentationProfileError("Präsentationsprofil gehört zu einem anderen Scope.")
        if target.get("binding") == "bound":
            snapshot = target.get("contextSnapshot")
            if type(snapshot) is not dict or snapshot.get("scope") != self.scope.to_dict():
                raise PresentationProfileError("Präsentationsprofil hat keine gültige Fallbindung.")
            profile = self.get(snapshot.get("caseId"))
        else:
            profile = default_profile(None)
        try:
            return make_presentation_receipt(profile, broadcast_id, target["digest"])
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, PresentationProfileError):
                raise
            raise PresentationProfileError("Präsentationsbeleg konnte nicht erstellt werden.") from exc

