"""Legacy label conversion helpers."""


def convert_legacy_label(label: str) -> str:
    return str(label or "").strip()
