from __future__ import annotations

import apps.web.main as web_main
import core.hardware.system_info as system_info


def test_hardware_status_includes_driver_layer_without_sampling(monkeypatch) -> None:
    sampled: list[str] = []
    registry_calls: list[str] = []

    class FakeRegistry:
        @classmethod
        def default(cls):
            registry_calls.append("default")
            return cls()

        def list_statuses(self):
            from core.hardware.drivers import HardwareProviderStatus

            return [
                HardwareProviderStatus(
                    provider_id="fake",
                    provider_type="mock",
                    display_name="Fake Provider",
                    available=True,
                    default_timeout_ms=7,
                )
            ]

        def sample(self, *args, **kwargs):
            sampled.append("sampled")
            raise AssertionError("status endpoint must not sample providers")

    monkeypatch.setattr(web_main, "HardwareDriverRegistry", FakeRegistry, raising=False)
    monkeypatch.setattr(
        system_info,
        "get_full_system_report",
        lambda: {
            "profile": "test",
            "os": {},
            "cpu": {},
            "gpu": {},
            "sensors": {"devices": []},
        },
    )
    web_main.driver_layer_status.cache_clear()
    app = web_main.create_app(runtime_dir=None)
    endpoint = next(
        route.endpoint
        for route in app.routes
        if getattr(route, "path", None) == "/api/hardware/status"
    )

    payload = endpoint()
    second_payload = endpoint()

    assert payload["driver_layer"]["providers"][0]["provider_id"] == "fake"
    assert payload["driver_layer"]["providers"][0]["available"] is True
    assert "status does not open devices" in payload["driver_layer"]["note"]
    assert "timeout-protected" not in payload["driver_layer"]["note"]
    assert second_payload["driver_layer"]["providers"][0]["provider_id"] == "fake"
    assert sampled == []
    assert registry_calls == ["default"]
