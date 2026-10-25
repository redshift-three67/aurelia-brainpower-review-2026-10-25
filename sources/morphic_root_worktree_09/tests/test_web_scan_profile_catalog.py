from __future__ import annotations

import hashlib
import json

import pytest
from fastapi import HTTPException

from apps.web import workbench as workbench_module
from core import profile_sync as profile_sync_module
import core.source_registry as source_registry_module
from apps.web.workbench import build_scan_profile_catalog
from core.profile_sync import ProfileAuthorityError
from core.source_registry import SourceRegistryError


class _Source:
    def __init__(self, source_id: str, label: str, *, active: bool) -> None:
        self.id = source_id
        self.label = label
        self.active = active


class _IntSubclass(int):
    pass


_INVALID_PROFILE_LEVELS = [
    pytest.param(True, id="true"),
    pytest.param(False, id="false"),
    pytest.param(3.0, id="float"),
    pytest.param("3", id="string"),
    pytest.param(0, id="below-range"),
    pytest.param(6, id="above-range"),
    pytest.param(_IntSubclass(3), id="int-subclass"),
]


def _expected_pool_fingerprint(
    profile_level: int,
    profiles: list[tuple[str, str]],
) -> str:
    canonical = json.dumps(
        {
            "schema_version": 1,
            "profile_level": profile_level,
            "pool_source": "legacy",
            "profiles": [
                {"id": profile_id, "label": label}
                for profile_id, label in profiles
            ],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_scan_profile_pool_fingerprint_uses_stable_canonical_utf8_json() -> None:
    profiles = [("internal-a", "Intern A"), ("umlaut", "Äther")]
    original_profiles = list(profiles)
    canonical = (
        '{"pool_source":"legacy","profile_level":3,"profiles":['
        '{"id":"internal-a","label":"Intern A"},'
        '{"id":"umlaut","label":"Äther"}],"schema_version":1}'
    )
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    first = workbench_module.build_scan_profile_pool_fingerprint(3, profiles)
    second = workbench_module.build_scan_profile_pool_fingerprint(3, profiles)

    assert first == expected
    assert second == first
    assert len(first) == 64
    assert first == first.lower()
    assert all(character in "0123456789abcdef" for character in first)
    assert profiles == original_profiles


@pytest.mark.parametrize(
    "profiles",
    [
        pytest.param([], id="empty"),
        pytest.param([("", "Label")], id="blank-id"),
        pytest.param([("id", " \t")], id="blank-label"),
        pytest.param([("id", "A"), ("id", "B")], id="duplicate-id"),
        pytest.param([(None, "Label")], id="none-id"),
        pytest.param([("id", None)], id="none-label"),
        pytest.param([(7, "Label")], id="nonstr-id"),
        pytest.param([("id", 7)], id="nonstr-label"),
        pytest.param([("id",)], id="short-tuple"),
        pytest.param([("id", "Label", "extra")], id="long-tuple"),
        pytest.param([["id", "Label"]], id="non-tuple-entry"),
        pytest.param([("id", "\ud800")], id="non-utf8-label"),
    ],
)
def test_scan_profile_pool_fingerprint_rejects_invalid_authoritative_pool(
    profiles: object,
) -> None:
    error_type = getattr(profile_sync_module, "ProfileAuthorityError", None)
    assert error_type is not None

    with pytest.raises(error_type):
        workbench_module.build_scan_profile_pool_fingerprint(
            3,
            profiles,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "profiles",
    [
        pytest.param([], id="empty"),
        pytest.param([("", "Label")], id="blank-id"),
        pytest.param([("id", " ")], id="blank-label"),
        pytest.param([("id", "A"), ("id", "B")], id="duplicate-id"),
        pytest.param([(None, "Label")], id="none-id"),
        pytest.param([("id", None)], id="none-label"),
        pytest.param([("id", 7)], id="nonstr-label"),
        pytest.param([("id",)], id="malformed-tuple"),
        pytest.param([("id", "\ud800")], id="non-utf8-label"),
    ],
)
def test_scan_profile_catalog_builder_rejects_invalid_authoritative_pool(
    profiles: object,
) -> None:
    error_type = getattr(profile_sync_module, "ProfileAuthorityError", None)
    assert error_type is not None

    with pytest.raises(error_type):
        build_scan_profile_catalog(
            profile_level=3,
            internal_profiles=profiles,  # type: ignore[arg-type]
            registry_sources=[],
        )


@pytest.mark.parametrize("profile_level", _INVALID_PROFILE_LEVELS)
def test_scan_profile_pool_fingerprint_rejects_non_builtin_or_out_of_range_level(
    profile_level: object,
) -> None:
    with pytest.raises(ValueError, match="profile_level must be between 1 and 5"):
        workbench_module.build_scan_profile_pool_fingerprint(
            profile_level,  # type: ignore[arg-type]
            [("internal-a", "Intern A")],
        )


@pytest.mark.parametrize(
    ("profile_level", "profiles"),
    [
        (4, [("internal-a", "Intern A"), ("internal-b", "Intern B")]),
        (3, [("internal-x", "Intern A"), ("internal-b", "Intern B")]),
        (3, [("internal-a", "Geändert"), ("internal-b", "Intern B")]),
        (3, [("internal-b", "Intern B"), ("internal-a", "Intern A")]),
    ],
    ids=["level", "id", "label", "order"],
)
def test_scan_profile_pool_fingerprint_detects_authority_drift(
    profile_level: int,
    profiles: list[tuple[str, str]],
) -> None:
    baseline = workbench_module.build_scan_profile_pool_fingerprint(
        3,
        [("internal-a", "Intern A"), ("internal-b", "Intern B")],
    )

    assert (
        workbench_module.build_scan_profile_pool_fingerprint(profile_level, profiles)
        != baseline
    )


def test_current_scan_profile_pool_fingerprint_uses_only_profile_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profiles = [("authority-b", "Autorität B"), ("authority-a", "Autorität A")]
    requested_levels: list[int] = []

    def authoritative_profiles(profile_level: int) -> list[tuple[str, str]]:
        requested_levels.append(profile_level)
        return profiles

    def fail_if_registry_loaded():
        raise AssertionError("registry must not be loaded for the pool fingerprint")

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        authoritative_profiles,
    )
    monkeypatch.setattr(
        workbench_module.SourceRegistry,
        "load_default",
        fail_if_registry_loaded,
    )

    fingerprint = workbench_module.current_scan_profile_pool_fingerprint(3)

    assert requested_levels == [3]
    assert fingerprint == _expected_pool_fingerprint(3, profiles)


def test_current_scan_profile_pool_authority_uses_one_defensive_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profiles = [("authority-b", "Autorität B"), ("authority-a", "Autorität A")]
    provider_calls = 0

    def authoritative_profiles(profile_level: int) -> list[tuple[str, str]]:
        nonlocal provider_calls
        provider_calls += 1
        assert profile_level == 3
        return profiles

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        authoritative_profiles,
    )

    authority = workbench_module.current_scan_profile_pool_authority(3)
    profiles.append(("late-mutation", "Späte Mutation"))

    assert provider_calls == 1
    assert authority.profiles == (
        ("authority-b", "Autorität B"),
        ("authority-a", "Autorität A"),
    )
    assert authority.count == 2
    assert authority.fingerprint == _expected_pool_fingerprint(
        3,
        list(authority.profiles),
    )
    with pytest.raises(TypeError):
        authority.profiles[0] = ("mutated", "Mutation")  # type: ignore[index]


def test_current_scan_profile_pool_authority_freezes_profiles_before_fingerprinting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profiles = [("authority-a", "Autorität A"), ("authority-b", "Autorität B")]

    def fingerprint_then_mutate(
        profile_level: int,
        fingerprint_profiles: list[tuple[str, str]],
    ) -> str:
        fingerprint = _expected_pool_fingerprint(
            profile_level,
            list(fingerprint_profiles),
        )
        fingerprint_profiles.append(("late-mutation", "Späte Mutation"))
        return fingerprint

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        lambda _profile_level: profiles,
    )
    monkeypatch.setattr(
        workbench_module,
        "build_scan_profile_pool_fingerprint",
        fingerprint_then_mutate,
    )

    authority = workbench_module.current_scan_profile_pool_authority(3)

    assert authority.profiles == tuple(profiles)
    assert authority.count == len(profiles) == 2
    assert authority.fingerprint == _expected_pool_fingerprint(3, profiles)


def test_current_scan_profile_pool_fingerprint_delegates_to_authority_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = "d" * 64
    calls: list[int] = []

    def authority(profile_level: int):
        calls.append(profile_level)
        return workbench_module.ScanProfilePoolAuthority(
            profiles=(("profile", "Profil"),),
            count=1,
            fingerprint=expected,
        )

    monkeypatch.setattr(
        workbench_module,
        "current_scan_profile_pool_authority",
        authority,
    )

    assert workbench_module.current_scan_profile_pool_fingerprint(4) == expected
    assert calls == [4]


@pytest.mark.parametrize("profile_level", _INVALID_PROFILE_LEVELS)
def test_current_scan_profile_pool_fingerprint_rejects_level_before_authority_load(
    monkeypatch: pytest.MonkeyPatch,
    profile_level: object,
) -> None:
    authority_calls: list[object] = []

    def authoritative_profiles(level: int) -> list[tuple[str, str]]:
        authority_calls.append(level)
        return [("must-not-load", "Darf nicht geladen werden")]

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        authoritative_profiles,
    )

    with pytest.raises(ValueError, match="profile_level must be between 1 and 5"):
        workbench_module.current_scan_profile_pool_fingerprint(
            profile_level  # type: ignore[arg-type]
        )

    assert authority_calls == []


def test_registry_sources_do_not_change_scan_profile_pool_fingerprint() -> None:
    profiles = [("internal-a", "Intern A"), ("internal-b", "Intern B")]
    without_registry_sources = build_scan_profile_catalog(
        profile_level=3,
        internal_profiles=profiles,
        registry_sources=[],
    )
    with_registry_sources = build_scan_profile_catalog(
        profile_level=3,
        internal_profiles=profiles,
        registry_sources=[
            _Source("source-active", "Aktive Referenzquelle", active=True),
            _Source("source-disabled", "Deaktivierte Quelle", active=False),
        ],
    )

    assert (
        without_registry_sources["pool_authority"]["fingerprint"]
        == with_registry_sources["pool_authority"]["fingerprint"]
    )


def test_scan_profile_catalog_separates_internal_profiles_from_registry_sources() -> None:
    profiles = [("internal-a", "Intern A"), ("internal-b", "Intern B")]
    fingerprint = _expected_pool_fingerprint(3, profiles)
    catalog = build_scan_profile_catalog(
        profile_level=3,
        internal_profiles=profiles,
        registry_sources=[
            _Source("source-active", "Aktive Referenzquelle", active=True),
            _Source("source-disabled", "Deaktivierte Quelle", active=False),
        ],
    )

    assert catalog == {
        "schema_version": 1,
        "profile_level": 3,
        "pool_authority": {
            "source": "legacy",
            "label": "Legacy",
            "revision": None,
            "revision_short": None,
            "fingerprint": fingerprint,
            "fingerprint_short": fingerprint[:12],
        },
        "internal": {
            "count": 2,
            "profiles": [
                {"id": "internal-a", "label": "Intern A"},
                {"id": "internal-b", "label": "Intern B"},
            ],
        },
        "external": {
            "count": 0,
            "profiles": [],
            "integration_status": "registry_only",
            "scan_effect": False,
            "activation_available": False,
            "activation_gate": "gate_14",
            "active_source_count": 1,
            "active_sources": [
                {
                    "id": "source-active",
                    "label": "Aktive Referenzquelle",
                    "scan_effect": False,
                    "reason_code": "registry_metadata_only",
                }
            ],
        },
        "total_scan_profiles": 2,
    }


@pytest.mark.parametrize("profile_level", _INVALID_PROFILE_LEVELS)
def test_scan_profile_catalog_builder_rejects_non_builtin_or_out_of_range_level(
    profile_level: object,
) -> None:
    with pytest.raises(ValueError, match="profile_level must be between 1 and 5"):
        build_scan_profile_catalog(
            profile_level=profile_level,  # type: ignore[arg-type]
            internal_profiles=[],
            registry_sources=[],
        )


def test_scan_profile_catalog_route_uses_authoritative_pool_and_redacts_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profiles = [("authority-b", "Autorität B"), ("authority-a", "Autorität A")]
    active_source = _Source("source-active", "Aktive Referenzquelle", active=True)
    active_source.private_path = r"C:\private\source.json"
    disabled_source = _Source("source-disabled", "Deaktivierte Quelle", active=False)
    requested_levels: list[int] = []
    registry_loads = 0
    source_lists = 0

    def authoritative_profiles(profile_level: int) -> list[tuple[str, str]]:
        requested_levels.append(profile_level)
        return profiles

    class _Registry:
        def list_sources(self) -> list[_Source]:
            nonlocal source_lists
            source_lists += 1
            return [active_source, disabled_source]

    def load_registry() -> _Registry:
        nonlocal registry_loads
        registry_loads += 1
        return _Registry()

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        authoritative_profiles,
    )
    monkeypatch.setattr(
        workbench_module.SourceRegistry,
        "load_default",
        load_registry,
    )

    catalog = workbench_module.scan_profile_catalog(profile_level=4, _api_key=None)
    expected_fingerprint = workbench_module.build_scan_profile_pool_fingerprint(
        4,
        profiles,
    )

    assert requested_levels == [4]
    assert registry_loads == 1
    assert source_lists == 1
    assert catalog["profile_level"] == 4
    assert catalog["internal"] == {
        "count": 2,
        "profiles": [
            {"id": "authority-b", "label": "Autorität B"},
            {"id": "authority-a", "label": "Autorität A"},
        ],
    }
    assert catalog["total_scan_profiles"] == 2
    assert catalog["pool_authority"]["fingerprint"] == expected_fingerprint
    assert catalog["pool_authority"]["fingerprint_short"] == expected_fingerprint[:12]
    assert catalog["external"] == {
        "count": 0,
        "profiles": [],
        "integration_status": "registry_only",
        "scan_effect": False,
        "activation_available": False,
        "activation_gate": "gate_14",
        "active_source_count": 1,
        "active_sources": [
            {
                "id": "source-active",
                "label": "Aktive Referenzquelle",
                "scan_effect": False,
                "reason_code": "registry_metadata_only",
            }
        ],
    }


@pytest.mark.parametrize(
    "registry_error",
    [
        SourceRegistryError(r"C:\\private\\source_repositories.json is invalid"),
        OSError(r"C:\\private\\source_repositories.json cannot be read"),
        json.JSONDecodeError(
            "invalid registry",
            r'C:\\private\\source_repositories.json',
            0,
        ),
    ],
)
def test_scan_profile_catalog_maps_registry_failures_to_redacted_503(
    monkeypatch: pytest.MonkeyPatch,
    registry_error: Exception,
) -> None:
    def fail_registry_load():
        raise registry_error

    monkeypatch.setattr(
        workbench_module.SourceRegistry,
        "load_default",
        fail_registry_load,
    )

    with pytest.raises(HTTPException) as captured:
        workbench_module.scan_profile_catalog(profile_level=3, _api_key=None)

    assert captured.value.status_code == 503
    assert captured.value.detail == "Lokaler Quellenkatalog nicht verfügbar."
    assert "private" not in str(captured.value.detail).lower()


@pytest.mark.parametrize(
    "error_type",
    [RuntimeError, TypeError, ImportError, OSError, ValueError],
)
def test_scan_profile_catalog_maps_profile_provider_failures_before_registry_to_503(
    monkeypatch: pytest.MonkeyPatch,
    error_type: type[Exception],
) -> None:
    sensitive_detail = r"C:\private\profiles\authority.json"
    registry_touched = False

    def fail_profile_provider(_profile_level: int):
        raise error_type(sensitive_detail)

    def forbidden_registry_load():
        nonlocal registry_touched
        registry_touched = True
        raise AssertionError("registry must not load after a profile provider failure")

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        fail_profile_provider,
    )
    monkeypatch.setattr(
        workbench_module.SourceRegistry,
        "load_default",
        forbidden_registry_load,
    )

    with pytest.raises(HTTPException) as captured:
        workbench_module.scan_profile_catalog(profile_level=3, _api_key=None)

    assert captured.value.status_code == 503
    assert captured.value.detail == "Scanprofil-Pool nicht verfügbar."
    assert sensitive_detail not in str(captured.value.detail)
    assert registry_touched is False


def test_scan_profile_catalog_validates_provider_pool_before_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_touched = False

    def forbidden_registry_load():
        nonlocal registry_touched
        registry_touched = True
        raise AssertionError("registry must not load after an invalid profile pool")

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        lambda _profile_level: [],
    )
    monkeypatch.setattr(
        workbench_module.SourceRegistry,
        "load_default",
        forbidden_registry_load,
    )

    with pytest.raises(HTTPException) as captured:
        workbench_module.scan_profile_catalog(profile_level=3, _api_key=None)

    assert captured.value.status_code == 503
    assert captured.value.detail == "Scanprofil-Pool nicht verfügbar."
    assert registry_touched is False


@pytest.mark.parametrize(
    "fingerprint_error",
    [
        RuntimeError(r"C:\private\profiles\fingerprint.json"),
        UnicodeEncodeError("utf-8", "\ud800", 0, 1, "surrogate not allowed"),
    ],
    ids=["runtime", "unicode"],
)
def test_scan_profile_catalog_fingerprints_before_registry_and_redacts_failure(
    monkeypatch: pytest.MonkeyPatch,
    fingerprint_error: Exception,
) -> None:
    registry_touched = False

    def fail_fingerprint(*_args: object, **_kwargs: object) -> str:
        raise fingerprint_error

    def forbidden_registry_load():
        nonlocal registry_touched
        registry_touched = True
        raise AssertionError("registry must not load after a fingerprint failure")

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        lambda _profile_level: [("valid", "Valid")],
    )
    monkeypatch.setattr(
        workbench_module,
        "build_scan_profile_pool_fingerprint",
        fail_fingerprint,
    )
    monkeypatch.setattr(
        workbench_module.SourceRegistry,
        "load_default",
        forbidden_registry_load,
    )

    with pytest.raises(HTTPException) as captured:
        workbench_module.scan_profile_catalog(profile_level=3, _api_key=None)

    assert captured.value.status_code == 503
    assert captured.value.detail == "Scanprofil-Pool nicht verfügbar."
    assert registry_touched is False


def test_scan_profile_catalog_rejects_surrogate_label_before_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_touched = False

    def forbidden_registry_load():
        nonlocal registry_touched
        registry_touched = True
        raise AssertionError("registry must not load after a non-UTF8 label")

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        lambda _profile_level: [("valid", "\ud800")],
    )
    monkeypatch.setattr(
        workbench_module.SourceRegistry,
        "load_default",
        forbidden_registry_load,
    )

    with pytest.raises(HTTPException) as captured:
        workbench_module.scan_profile_catalog(profile_level=3, _api_key=None)

    assert captured.value.status_code == 503
    assert captured.value.detail == "Scanprofil-Pool nicht verfügbar."
    assert registry_touched is False


def test_scan_profile_catalog_reuses_guarded_fingerprint_without_recalculation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fingerprint_calls = 0

    def fingerprint_once(*_args: object, **_kwargs: object) -> str:
        nonlocal fingerprint_calls
        fingerprint_calls += 1
        if fingerprint_calls > 1:
            raise AssertionError("fingerprint was recalculated after registry access")
        return "a" * 64

    class _Registry:
        def list_sources(self) -> list[object]:
            return []

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        lambda _profile_level: [("valid", "Valid")],
    )
    monkeypatch.setattr(
        workbench_module,
        "build_scan_profile_pool_fingerprint",
        fingerprint_once,
    )
    monkeypatch.setattr(
        workbench_module.SourceRegistry,
        "load_default",
        lambda: _Registry(),
    )

    catalog = workbench_module.scan_profile_catalog(profile_level=3, _api_key=None)

    assert fingerprint_calls == 1
    assert catalog["pool_authority"]["fingerprint"] == "a" * 64


@pytest.mark.parametrize("fingerprint", ["", "A" * 64, "g" * 64, "a" * 63])
def test_scan_profile_catalog_builder_rejects_invalid_prevalidated_fingerprint(
    fingerprint: str,
) -> None:
    with pytest.raises(ProfileAuthorityError):
        build_scan_profile_catalog(
            profile_level=3,
            internal_profiles=[("valid", "Valid")],
            registry_sources=[],
            _validated_fingerprint=fingerprint,
        )


@pytest.mark.parametrize("profile_level", _INVALID_PROFILE_LEVELS)
def test_scan_profile_catalog_rejects_level_before_loading_profiles_or_registry(
    monkeypatch: pytest.MonkeyPatch,
    profile_level: object,
) -> None:
    profiles_touched = False
    registry_touched = False

    def fail_if_profiles_loaded(level: int):
        nonlocal profiles_touched
        profiles_touched = True
        return []

    def fail_if_loaded():
        nonlocal registry_touched
        registry_touched = True
        raise AssertionError("registry must not be loaded for an invalid level")

    monkeypatch.setattr(
        workbench_module,
        "get_top_n_analysis_profiles_by_level",
        fail_if_profiles_loaded,
    )
    monkeypatch.setattr(
        workbench_module.SourceRegistry,
        "load_default",
        fail_if_loaded,
    )

    with pytest.raises(HTTPException) as captured:
        workbench_module.scan_profile_catalog(
            profile_level=profile_level,  # type: ignore[arg-type]
            _api_key=None,
        )

    assert captured.value.status_code == 422
    assert captured.value.detail == "profile_level must be between 1 and 5"
    assert profiles_touched is False
    assert registry_touched is False


def test_scan_profile_catalog_redacts_structurally_malformed_registry(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "source_repositories.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "revision": 0,
                "rollback_history": [],
                "sources": [1],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(source_registry_module, "DEFAULT_SOURCE_REGISTRY_PATH", path)

    with pytest.raises(HTTPException) as captured:
        workbench_module.scan_profile_catalog(profile_level=3, _api_key=None)

    assert captured.value.status_code == 503
    assert captured.value.detail == "Lokaler Quellenkatalog nicht verfügbar."
