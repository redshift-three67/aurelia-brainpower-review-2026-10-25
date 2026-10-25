from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "apps" / "web" / "main.py"


def test_local_operator_app_denies_cross_origin_cors_and_sets_security_headers() -> None:
    source = MAIN.read_text(encoding="utf-8")

    assert "allow_origins=[]" in source
    assert "allow_credentials=False" in source
    assert 'response.headers["X-Content-Type-Options"] = "nosniff"' in source
    assert 'response.headers["X-Frame-Options"] = "SAMEORIGIN"' in source
    assert 'response.headers["Referrer-Policy"] = "no-referrer"' in source
