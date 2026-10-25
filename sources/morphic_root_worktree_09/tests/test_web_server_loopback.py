from __future__ import annotations

import pytest

from web_server import resolve_bind_host


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "::1"])
def test_local_operator_web_server_allows_loopback_hosts(host: str) -> None:
    assert resolve_bind_host(host) == host


@pytest.mark.parametrize("host", ["0.0.0.0", "192.168.1.20", "example.invalid", ""])
def test_local_operator_web_server_rejects_non_loopback_hosts(host: str) -> None:
    with pytest.raises(RuntimeError, match="Loopback"):
        resolve_bind_host(host)
