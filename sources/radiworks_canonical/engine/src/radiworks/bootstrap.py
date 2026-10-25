"""Opt-in Bootstrap eines ausschliesslich synthetischen Preview-Katalogs."""

from __future__ import annotations

from importlib import resources
from pathlib import Path


class SyntheticCatalogBootstrapError(RuntimeError):
    """Ein sicherer Bootstrap des Preview-Katalogs ist nicht moeglich."""


_FIXTURE_RESOURCE = "fixtures/synthetic_catalog/radionics/HOMEOPATHY_Synthetic.txt"


def bootstrap_synthetic_catalog(
    runtime_home: Path | str,
    *,
    external_data_dir: Path | str | None = None,
) -> Path:
    """Schreibt einmalig einen synthetischen Katalog in das Runtime-Home.

    Externe Betreiberkataloge sind ausschliesslich read-only und duerfen nie
    durch diesen Bootstrap veraendert werden.
    """
    if external_data_dir is not None:
        raise SyntheticCatalogBootstrapError(
            "Synthetischer Bootstrap ist mit RADIOWORKS_DATA_DIR nicht erlaubt"
        )

    target_root = Path(runtime_home).expanduser() / "data"
    existing_catalogs = [
        path
        for path in target_root.rglob("*")
        if path.is_file() and path.suffix in {".txt", ".rscript"}
    ] if target_root.exists() else []
    if existing_catalogs:
        raise SyntheticCatalogBootstrapError(
            "Rate-Katalog ist bereits vorhanden; Bootstrap ueberschreibt keine Daten"
        )

    target = target_root / "radionics" / "HOMEOPATHY_Synthetic.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    source = resources.files("radiworks").joinpath(_FIXTURE_RESOURCE)
    try:
        with source.open("rb") as source_file, target.open("xb") as target_file:
            target_file.write(source_file.read())
    except FileExistsError as exc:
        raise SyntheticCatalogBootstrapError(
            "Rate-Katalog ist bereits vorhanden; Bootstrap ueberschreibt keine Daten"
        ) from exc
    return target
