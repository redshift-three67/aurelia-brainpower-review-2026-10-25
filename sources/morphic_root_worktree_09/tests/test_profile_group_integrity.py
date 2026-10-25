from __future__ import annotations

from core.profile_sync import get_all_profiles
from core.remedy_auto_matcher import CATEGORY_REMEDY_MAPPING
from core.remedy_group_registry import list_all_remedy_groups
from core.subgroups.procedural_groups import list_groups


def test_all_profile_groups_are_registered() -> None:
    available_groups = set(list_groups())

    missing = {
        profile.name: [group for group in profile.groups if group not in available_groups]
        for profile in get_all_profiles()
    }
    missing = {name: groups for name, groups in missing.items() if groups}

    assert missing == {}


def test_explicit_remedy_groups_are_registered() -> None:
    available_groups = set(list_groups())
    remedy_groups = set(list_all_remedy_groups())

    missing = sorted(remedy_groups - available_groups)

    assert missing == []


def test_auto_matcher_only_suggests_registered_groups() -> None:
    available_groups = set(list_groups())
    suggested_groups = {
        group
        for groups in CATEGORY_REMEDY_MAPPING.values()
        for group in groups
    }

    missing = sorted(suggested_groups - available_groups)

    assert missing == []
