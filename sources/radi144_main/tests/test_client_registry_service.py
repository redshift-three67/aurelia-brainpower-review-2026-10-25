from pathlib import Path

from app.models.client_registry import ClientRegistryEntry
from app.services.client_registry_service import ClientRegistryService


def test_client_registry_reuses_stable_id_for_same_identity(tmp_path):
    service = ClientRegistryService(tmp_path / "clients.json")

    payload = {
        "first_name": "Max",
        "last_names": ["Mustermann"],
        "birth_date": "1990-01-01",
        "birth_place": "Berlin",
        "planet": "Mars",
    }

    first = service.get_or_create(payload)
    second = service.get_or_create(payload)

    assert isinstance(first, ClientRegistryEntry)
    assert first.client_id == second.client_id
    assert first.first_name == "Max"
    assert first.last_names == ["Mustermann"]
    assert first.birth_place == "Berlin"


def test_client_registry_persists_json_store_with_entries(tmp_path):
    store_path = tmp_path / "clients.json"
    service = ClientRegistryService(store_path)

    created = service.get_or_create(
        {
            "first_name": "Anna",
            "last_names": ["Muster"],
            "birth_date": "1988-03-14",
            "birth_place": "Wien",
        }
    )

    persisted = store_path.read_text(encoding="utf-8")

    assert created.client_id in persisted
    assert '"entries"' in persisted
