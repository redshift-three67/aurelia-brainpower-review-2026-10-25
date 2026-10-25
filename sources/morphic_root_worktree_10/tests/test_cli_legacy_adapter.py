from __future__ import annotations

import cli.main as legacy_main
from apps.cli.commands import helpers


def test_cli_main_legacy_adapter_is_supported() -> None:
    assert legacy_main.COMPATIBILITY_STATUS == "supported"
    assert legacy_main.ADAPTER_TARGET == "apps.cli.commands.helpers"


def test_cli_main_legacy_adapter_exports_helper_delegates() -> None:
    assert set(legacy_main.__all__) == set(helpers.__all__) | {
        "ADAPTER_TARGET",
        "COMPATIBILITY_STATUS",
    }

    for name in helpers.__all__:
        assert getattr(legacy_main, name) is getattr(helpers, name), name
