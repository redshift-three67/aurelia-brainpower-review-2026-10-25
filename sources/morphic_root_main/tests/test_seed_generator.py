"""Tests fuer core.realtime.seed_generator."""

from __future__ import annotations

from core.realtime.seed_generator import (
    generate_deterministic_seed,
    generate_seed_with_entropy,
)

CLIENT = dict(
    workspace_id="ws-1",
    last_name="Mustermann",
    first_name="Klaus",
    birth_date="09041966",
    birth_place="Augsburg",
)


def test_generate_deterministic_seed_is_reproducible() -> None:
    a = generate_deterministic_seed(**CLIENT)
    b = generate_deterministic_seed(**CLIENT)

    assert a == b
    assert isinstance(a, int)
    assert 0 <= a <= 0x7FFFFFFF


def test_generate_deterministic_seed_differs_per_workspace() -> None:
    a = generate_deterministic_seed(**CLIENT)
    b = generate_deterministic_seed(**{**CLIENT, "workspace_id": "ws-2"})

    assert a != b


def test_generate_deterministic_seed_is_case_and_whitespace_insensitive() -> None:
    a = generate_deterministic_seed(**CLIENT)
    b = generate_deterministic_seed(
        workspace_id=" ws-1 ",
        last_name=" mustermann ",
        first_name=" KLAUS ",
        birth_date="09041966",
        birth_place=" augsburg ",
    )

    assert a == b


def test_generate_seed_with_entropy_without_hardware_returns_none_extras() -> None:
    result = generate_seed_with_entropy(**CLIENT, use_hardware=False)

    assert result.hardware_seed is None
    assert result.entropy_samples is None
    assert result.source_label == "none"
    assert result.deterministic_seed == generate_deterministic_seed(**CLIENT)


def test_generate_seed_with_entropy_with_hardware_returns_seed_and_label() -> None:
    result = generate_seed_with_entropy(**CLIENT, use_hardware=True)

    assert result.hardware_seed is not None
    assert 0 <= result.hardware_seed <= 0x7FFFFFFF
    assert result.source_label != "none"
    assert result.deterministic_seed == generate_deterministic_seed(**CLIENT)


def test_generate_seed_with_entropy_hardware_seeds_are_not_constant() -> None:
    first = generate_seed_with_entropy(**CLIENT, use_hardware=True)
    second = generate_seed_with_entropy(**CLIENT, use_hardware=True)

    # deterministischer Teil bleibt gleich, der Hardware-Zusatz-Seed
    # kommt aus os.urandom und darf sich unterscheiden.
    assert first.deterministic_seed == second.deterministic_seed
    assert first.hardware_seed != second.hardware_seed
