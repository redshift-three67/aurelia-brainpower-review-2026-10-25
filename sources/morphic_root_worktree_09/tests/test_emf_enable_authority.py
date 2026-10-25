from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import threading
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from apps.web.emf_authority import (
    EmfTelemetryAuthority,
    build_emf_telemetry_authority,
)
from apps.web.emf import emf_status_payload


def test_async_publish_permit_waits_without_blocking_event_loop(
    tmp_path: Path,
) -> None:
    authority = build_emf_telemetry_authority(tmp_path)
    authority.set_enabled(True)
    lease = authority.begin_measurement()
    lock_held = threading.Event()
    release_lock = threading.Event()

    def hold_publish_permit() -> None:
        with authority.publish_permit(lease) as permitted:
            assert permitted is True
            lock_held.set()
            release_lock.wait(timeout=2)

    holder = threading.Thread(target=hold_publish_permit, daemon=True)
    holder.start()
    assert lock_held.wait(timeout=1)

    async def exercise() -> None:
        async def acquire() -> bool:
            async with authority.async_publish_permit(lease) as permitted:
                return permitted

        acquisition = asyncio.create_task(acquire())
        await asyncio.sleep(0)
        event_loop_remained_responsive = holder.is_alive() and not acquisition.done()
        release_lock.set()
        result = await asyncio.gather(acquisition, return_exceptions=True)
        assert event_loop_remained_responsive
        assert result == [True]

    asyncio.run(exercise())
    holder.join(timeout=1)
    assert holder.is_alive() is False


def test_emf_authority_factory_initializes_valid_disabled_authority(
    tmp_path: Path,
) -> None:
    authority = build_emf_telemetry_authority(tmp_path)

    generation_record = json.loads(
        authority.generation_path.read_text(encoding="utf-8")
    )
    main_record = json.loads(authority.path.read_text(encoding="utf-8"))

    assert authority.path == tmp_path / "emf-telemetry-authority.json"
    assert authority.is_enabled() is False
    assert generation_record["generation"] == 1
    assert len(generation_record["activation_id"]) == 32
    assert int(generation_record["activation_id"], 16) >= 0
    assert main_record == {"enabled": False, **generation_record}


def test_emf_authority_factory_preserves_enabled_state(tmp_path: Path) -> None:
    first = build_emf_telemetry_authority(tmp_path)
    first.set_enabled(True)
    main_record = first.path.read_bytes()
    generation_record = first.generation_path.read_bytes()

    second = build_emf_telemetry_authority(tmp_path)

    assert second.path == first.path
    assert second.is_enabled() is True
    assert second.path.read_bytes() == main_record
    assert second.generation_path.read_bytes() == generation_record


def test_emf_authority_factory_does_not_repair_partial_state(
    tmp_path: Path,
) -> None:
    authority_path = tmp_path / "emf-telemetry-authority.json"
    partial_record = '{"enabled":true,"generation":1}'
    authority_path.write_text(partial_record, encoding="utf-8")

    authority = build_emf_telemetry_authority(tmp_path)

    assert authority.is_enabled() is False
    assert authority_path.read_text(encoding="utf-8") == partial_record
    assert authority.generation_path.exists() is False


def test_emf_authority_factory_preserves_subprocess_activation(
    tmp_path: Path,
) -> None:
    authority = build_emf_telemetry_authority(tmp_path)
    command = [
        sys.executable,
        "-c",
        (
            "from pathlib import Path; "
            "from apps.web.emf_authority import build_emf_telemetry_authority; "
            f"authority = build_emf_telemetry_authority(Path({str(tmp_path)!r})); "
            "authority.set_enabled(True); "
            "print(authority.is_enabled())"
        ),
    ]

    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    recreated = build_emf_telemetry_authority(tmp_path)

    assert completed.stdout.strip() == "True"
    assert recreated.path == authority.path
    assert recreated.is_enabled() is True


def test_emf_authority_lock_uses_shared_durable_parent_helper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.web import emf_authority

    calls: list[Path] = []

    def parent(path: Path, *, mode: int = 0o777) -> None:
        calls.append(Path(path))
        Path(path).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(emf_authority, "durable_mkdir_parents", parent, raising=False)

    assert EmfTelemetryAuthority(tmp_path / "nested" / "emf.json").is_enabled() is False
    assert calls == [tmp_path / "nested"]


def test_emf_authority_is_durable_cross_process_and_fails_closed(tmp_path) -> None:
    path = tmp_path / "emf-authority.json"
    authority = EmfTelemetryAuthority(path)
    assert authority.is_enabled() is False

    authority.set_enabled(True)
    first_generation = authority.begin_measurement()
    assert first_generation is not None and first_generation.startswith("1:")
    command = [
        sys.executable,
        "-c",
        (
            "from pathlib import Path; "
            "from apps.web.emf_authority import EmfTelemetryAuthority; "
            f"print(EmfTelemetryAuthority(Path({str(path)!r})).is_enabled())"
        ),
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    assert completed.stdout.strip() == "True"

    authority.set_enabled(False)
    assert EmfTelemetryAuthority(path).is_enabled() is False
    path.write_text("not-json", encoding="utf-8")
    assert EmfTelemetryAuthority(path).is_enabled() is False
    authority.set_enabled(True)
    assert authority.begin_measurement().startswith("3:")
    assert authority.measurement_is_current(first_generation) is False

    path.unlink()
    authority.set_enabled(True)
    assert authority.begin_measurement().startswith("4:")

    authority.generation_path.write_text("not-json", encoding="utf-8")
    assert authority.begin_measurement() is None
    authority.set_enabled(True)
    repaired_lease = authority.begin_measurement()
    assert repaired_lease is not None and repaired_lease.startswith("5:")

    path.unlink()
    authority.generation_path.unlink()
    authority.set_enabled(True)
    replacement_lease = authority.begin_measurement()
    assert replacement_lease is not None and replacement_lease != first_generation
    assert authority.measurement_is_current(first_generation) is False


def test_partial_emf_authority_commit_fails_closed(tmp_path, monkeypatch) -> None:
    path = tmp_path / "emf-authority.json"
    authority = EmfTelemetryAuthority(path)
    authority.set_enabled(True)
    old_lease = authority.begin_measurement()
    from apps.web import emf_authority

    real_write = emf_authority.durable_write_bytes
    writes = 0

    def fail_main_write(target, payload):
        nonlocal writes
        writes += 1
        if writes == 2:
            raise OSError("injected main write failure")
        return real_write(target, payload)

    monkeypatch.setattr(emf_authority, "durable_write_bytes", fail_main_write)
    with pytest.raises(OSError, match="main write failure"):
        authority.set_enabled(False)

    assert authority.begin_measurement() is None
    assert authority.measurement_is_current(old_lease) is False


def test_set_enabled_returns_private_immutable_exact_revision(tmp_path: Path) -> None:
    authority = EmfTelemetryAuthority(tmp_path / "emf-authority.json")

    revision = authority.set_enabled(True)
    main_record = json.loads(authority.path.read_text(encoding="utf-8"))

    assert type(revision).__name__.startswith("_")
    assert revision.generation == main_record["generation"]
    assert revision.activation_id == main_record["activation_id"]
    assert revision.enabled is True
    with pytest.raises(FrozenInstanceError):
        revision.enabled = False


def test_compensation_disables_current_enabled_revision_across_instances(
    tmp_path: Path,
) -> None:
    path = tmp_path / "emf-authority.json"
    writer = EmfTelemetryAuthority(path)
    compensator = EmfTelemetryAuthority(path)
    revision = writer.set_enabled(True)

    assert compensator.compensate_to_disabled_if_current(revision) is True
    assert writer.is_enabled() is False

    main_after = path.read_bytes()
    generation_after = writer.generation_path.read_bytes()
    assert compensator.compensate_to_disabled_if_current(revision) is False
    assert path.read_bytes() == main_after
    assert writer.generation_path.read_bytes() == generation_after


def test_stale_compensation_does_not_clobber_newer_enabled_revision_across_instances(
    tmp_path: Path,
) -> None:
    path = tmp_path / "emf-authority.json"
    first = EmfTelemetryAuthority(path)
    second = EmfTelemetryAuthority(path)
    stale_revision = first.set_enabled(True)
    newer_revision = second.set_enabled(True)
    main_before = path.read_bytes()
    generation_before = first.generation_path.read_bytes()

    assert first.compensate_to_disabled_if_current(stale_revision) is False
    assert first.is_enabled() is True
    assert first.begin_measurement() == (
        f"{newer_revision.generation}:{newer_revision.activation_id}"
    )
    assert path.read_bytes() == main_before
    assert first.generation_path.read_bytes() == generation_before


@pytest.mark.parametrize("newer_enabled", (False, True), ids=("still-disabled", "later-enable"))
def test_disabled_revision_compensation_is_always_a_noop(
    tmp_path: Path,
    newer_enabled: bool,
) -> None:
    authority = EmfTelemetryAuthority(tmp_path / "emf-authority.json")
    disabled_revision = authority.set_enabled(False)
    if newer_enabled:
        authority.set_enabled(True)
    main_before = authority.path.read_bytes()
    generation_before = authority.generation_path.read_bytes()

    assert authority.compensate_to_disabled_if_current(disabled_revision) is False
    assert authority.path.read_bytes() == main_before
    assert authority.generation_path.read_bytes() == generation_before
    assert authority.is_enabled() is newer_enabled


@pytest.mark.parametrize(
    "damage",
    (
        "missing-main",
        "missing-generation",
        "corrupt-main",
        "corrupt-generation",
        "mismatched-records",
        "boolean-generation",
        "unexpected-fields",
    ),
)
def test_compensation_preserves_partial_or_corrupt_fail_closed_records(
    tmp_path: Path,
    damage: str,
) -> None:
    authority = EmfTelemetryAuthority(tmp_path / "emf-authority.json")
    revision = authority.set_enabled(True)
    if damage == "missing-main":
        authority.path.unlink()
    elif damage == "missing-generation":
        authority.generation_path.unlink()
    elif damage == "corrupt-main":
        authority.path.write_text("not-json", encoding="utf-8")
    elif damage == "corrupt-generation":
        authority.generation_path.write_text("not-json", encoding="utf-8")
    elif damage == "mismatched-records":
        generation_record = json.loads(
            authority.generation_path.read_text(encoding="utf-8")
        )
        generation_record["activation_id"] = "0" * 32
        authority.generation_path.write_text(
            json.dumps(generation_record),
            encoding="utf-8",
        )
    elif damage == "boolean-generation":
        main_record = json.loads(authority.path.read_text(encoding="utf-8"))
        generation_record = json.loads(
            authority.generation_path.read_text(encoding="utf-8")
        )
        main_record["generation"] = True
        generation_record["generation"] = True
        authority.path.write_text(json.dumps(main_record), encoding="utf-8")
        authority.generation_path.write_text(
            json.dumps(generation_record),
            encoding="utf-8",
        )
    else:
        generation_record = json.loads(
            authority.generation_path.read_text(encoding="utf-8")
        )
        generation_record["unexpected"] = "corrupt"
        authority.generation_path.write_text(
            json.dumps(generation_record),
            encoding="utf-8",
        )
    main_before = authority.path.read_bytes() if authority.path.exists() else None
    generation_before = (
        authority.generation_path.read_bytes()
        if authority.generation_path.exists()
        else None
    )

    assert authority.compensate_to_disabled_if_current(revision) is False
    assert (
        authority.path.read_bytes() if authority.path.exists() else None
    ) == main_before
    assert (
        authority.generation_path.read_bytes()
        if authority.generation_path.exists()
        else None
    ) == generation_before
    assert authority.is_enabled() is False


@pytest.mark.parametrize(
    "invalid_activation_id",
    (
        "!" * 32,
        "A" * 32,
        " " * 32,
        "\x00" * 32,
        "z" * 32,
    ),
    ids=("punctuation", "uppercase-hex", "whitespace", "control", "nonhex"),
)
def test_matching_invalid_activation_ids_remain_disabled_and_unmodified(
    tmp_path: Path,
    invalid_activation_id: str,
) -> None:
    authority = EmfTelemetryAuthority(tmp_path / "emf-authority.json")
    revision = authority.set_enabled(True)
    main_record = json.loads(authority.path.read_text(encoding="utf-8"))
    generation_record = json.loads(
        authority.generation_path.read_text(encoding="utf-8")
    )
    main_record["activation_id"] = invalid_activation_id
    generation_record["activation_id"] = invalid_activation_id
    authority.path.write_text(json.dumps(main_record), encoding="utf-8")
    authority.generation_path.write_text(
        json.dumps(generation_record),
        encoding="utf-8",
    )
    main_before = authority.path.read_bytes()
    generation_before = authority.generation_path.read_bytes()

    assert authority.begin_measurement() is None
    assert emf_status_payload(authority)["active"] is False
    assert authority.compensate_to_disabled_if_current(revision) is False
    assert authority.path.read_bytes() == main_before
    assert authority.generation_path.read_bytes() == generation_before
